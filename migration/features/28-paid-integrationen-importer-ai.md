# 28 – Bezahl-Features Cluster P09: Integrationen, Importer, Plane AI, Plattform – IST-Analyse

> **Status:** IST-Analyse (keine Implementierung). Bindend: `migration/architecture/00-grundsatzentscheidungen.md` – insbesondere **ADR-001** (eine Edition, alle Features aktiv, kein Billing/Upsell/Credits), **ADR-002** (kein Node.js zur Laufzeit), **ADR-003** (Greenfield-Schema, fachliche Semantik bleibt), **ADR-004** (Self-hosted inkl. Airgapped; externe Dienste optional/abschaltbar; lokal betreibbarer LLM-Provider Pflicht; Vektor-DB = PostgreSQL/pgvector), **ADR-005** (UI 1:1), **ADR-006** (Original-Repo ist Referenz).
>
> **Schwesterdokumente (nicht duplizieren, sondern dort nachlesen):**
> `20-paid-spuren-im-repo.md` (P01, Repo-Spuren, Plan-Matrix zeilengenau), `21-paid-api-referenz-developer-docs.md` (P02, REST-Verträge der Bezahl-Ressourcen, Scope-Inventar), `22-paid-architektur-selfhosting-dienste.md` (P03, Dienst-Landkarte Silo/PI/Runner/MCP, Config-/Secret-Inventar, Messaging), `25-paid-workflows-automation-templates.md` (P06, Automationen, **Plane Runner** im Detail), `26-paid-wissen-pages-wiki.md` (P07, **AI-Block / AI im Editor** im Detail).
>
> **Abkürzungen für Quellen**
>
> | Kürzel | Bedeutung |
> |---|---|
> | ohne Präfix | Pfad relativ zum Repo-Root `/home/user/plane` (Plane Community Edition v1.4.2) |
> | `DD/` | `/home/user/makeplane/developer-docs/docs/` (offizielle Developer-Docs, offline gelesen) |
> | `IMG/` | `/home/user/makeplane/developer-docs/docs/public/images/` (Screenshots, offline gesichtet) |
> | `HC/` | `/home/user/makeplane/helm-charts/charts/plane-enterprise/` (offizieller Helm-Chart der Commercial Edition, offline gelesen) |
> | `PROPEL/` | `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/propel-pkg/package/dist/icons/` (`@makeplane/propel` 0.7.3, nur gelesen) |
> | `GH:` | am 21.10.2026 direkt von github.com / raw.githubusercontent.com gelesene **Erstquelle** des Herstellers (Repos `makeplane/developer-docs`, Branch `docs/api-reference-v2`; `makeplane/plane-node-sdk`) |
> | `WEB(Pxx):` | öffentliche URL, die ein Schwester-Agent per WebSearch gefunden hat (nur Such-Snippet; hier **nicht** erneut geprüft) – Konfidenz entsprechend reduziert |
> | `WEB(V09):` | öffentliche URL aus der WebSearch des Verifikationslaufs dieses Dokuments am 22.10.2026 (nur Suchzusammenfassung, Seite selbst nicht abrufbar) – Liste der Suchen im Verifikations-Protokoll |
>
> **Status-Legende CE-Abgleich:** **fehlt** = weder Modell noch Route noch UI im CE · **Stub/UI-Hülle im CE** = nur i18n-Texte, Icons, Illustrationen, ungenutzte Altmodelle/-komponenten, keine lauffähige Funktion · **teilweise im CE** = fachlicher Kern vorhanden, Commercial-Funktion geht deutlich darüber hinaus · **im CE vorhanden (nur Cloud-Gating)** = vollständig im CE.

---

## Inhaltsverzeichnis

1. Überblick & Quellenlage
2. Feature-Tabelle (Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle)
3. Feature-Abschnitte
   - 3.A Integrationen (P09-F01 … P09-F20, P09-F59)
   - 3.B Importer (P09-F21 … P09-F32, P09-F60)
   - 3.C Plane AI (P09-F33 … P09-F46, P09-F61)
   - 3.D Plattform (P09-F47 … P09-F58)
   - 3.E Querschnittliche Zielarchitektur (.NET Aspire / EF Core / PostgreSQL+pgvector / Angular)
4. Offene Punkte / Unklarheiten
- Anhang A: Vollständiges i18n-Inventar `packages/i18n/src/locales/en/integration.json` (291 Schlüssel)
- Anhang B: Vollständiges i18n-Inventar `workspace_settings.settings.{integrations,imports,applications,runners,plane-intelligence,api_tokens,webhooks}` und weitere Cluster-Schlüssel
- Anhang C: Externe Callback-/Webhook-Endpunkte der Integrationen (Silo) – vollständige Liste
- Anhang D: MCP-Server-Tool-Inventar (28 Tools)
- Anhang E: OAuth-Scope-Inventar (v1-App-Scopes und v2-Scopes)
- Verifikations-Protokoll (Skeptiker-Lauf: Korrekturen, Tier-/CE-Abgleich, Ergänzungen F59–F61)

---

## 1. Überblick & Quellenlage

### 1.1 Zweck und Abgrenzung

Dieses Dokument spezifiziert die **Bezahl-Features** des Clusters „Integrationen, Importer, AI, Plattform“ – also Funktionen, die **nicht** in der Open-Source Community Edition (CE) enthalten sind, sondern nur in der closed-source Commercial Edition bzw. Plane Cloud (Pläne Free/One/Pro/Business/Enterprise bzw. „Enterprise Grid“). Der Code der Commercial Edition ist nicht verfügbar; die Spezifikation stützt sich ausschließlich auf öffentliche Quellen (Developer-Docs, Helm-Chart, offizielle SDKs/Docs-Repos auf GitHub, CE-Repo-Spuren: Plan-Matrix, i18n-Texte, Icons, Illustrationen, ungenutzte Altmodelle). Ziel: Implementierungs-Agenten können die Features clean-room nachbauen.

Nicht Gegenstand (Querverweis): Advanced Search/OpenSearch als Volltextsuche (P03 §3, `22-…`), Automationen/Workflows/Runner-Details (P06, `25-…`), AI-Block-Editor-Details (P07, `26-…`), SSO/LDAP/Group-Sync (P03), Audit-Logs, Customers, Releases (P02).

### 1.2 Quellen

| # | Quelle | Pfad / URL | gelesen |
|---|---|---|---|
| Q1 | Plan-Matrix (Hersteller-gepflegt) | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 935–1024 (Sektionen `importers`, `integrations`), Z. 1303–1309 (`planHighlights`) | vollständig |
| Q2 | Plan-Feature-Listen | `packages/constants/src/subscription.ts` (`PRO_PLAN_FEATURES` „Popular integrations“, `FREE_PLAN_UPGRADE_FEATURES` „Integrations“) | vollständig |
| Q3 | EE-UI-Texte | `packages/i18n/src/locales/en/integration.json` (291 Schlüssel, vollständig in Anhang A), `workspace-settings.json` (`settings.integrations/imports/applications/runners/plane-intelligence/api_tokens/webhooks`), `settings.json` (`account_settings.connections`), `editor.json` (`ai_block`), `tour.json` (`mcp_connectors`, `get_started`), `common.json`/`navigation.json` (`pi_chat`), `empty-state.json`, `project-settings.json` (`empty_state.integrations`), `workspace.json`/`project.json` (`members_import`) | vollständig (Skript-Dump aller 3 859 en-Schlüssel, danach gezielt) |
| Q4 | CE-Altmodelle Integrationen/Importer | `apps/api/plane/db/models/integration/{base,github,slack}.py`, `apps/api/plane/db/models/importer.py`, `apps/api/plane/app/serializers/importer.py` | vollständig |
| Q5 | CE-Alt-UI Integrationen/Importer | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/integrations/page.tsx`, `apps/web/components/integration/{single-integration-card,github/select-repository,slack/select-channel}.tsx`, `apps/web/components/project/integration-card.tsx`, `apps/web/hooks/use-integration-popup.tsx`, `apps/web/services/integrations/{integration,github,jira}.service.ts`, `apps/web/services/app_installation.service.ts`, `apps/web/services/project/project.service.ts` Z. 121–160, `packages/types/src/{integration.ts,importer/*.ts}`, `packages/constants/src/workspace.ts` (`IMPORTERS_LIST`), `packages/constants/src/fetch-keys.ts` Z. 114–126 | vollständig |
| Q6 | CE-AI-Basis | `apps/api/plane/app/views/external/base.py`, `apps/api/plane/app/urls/external.py`, `apps/web/services/ai.service.ts`, `apps/web/components/pages/editor/ai/menu.tsx`, `apps/web/components/core/modals/gpt-assistant-popover.tsx`, `apps/web/hooks/use-editor-flagging.ts`, `packages/editor/src/types/{ai,extensions}.ts`, `packages/constants/src/ai.ts`, `packages/types/src/instance/{ai,base}.ts`, `apps/admin/app/(all)/(dashboard)/ai/{page,form}.tsx`, `apps/api/plane/license/api/views/instance.py` Z. 55–139 | vollständig |
| Q7 | CE-Plattform-Basis | `apps/api/plane/db/models/{webhook,api,device,user}.py`, `apps/api/plane/bgtasks/webhook_task.py` Z. 230–392, `apps/api/plane/app/urls/{webhook,api}.py`, `apps/web/components/web-hooks/**`, `packages/constants/src/settings/workspace.ts`, `packages/types/src/settings.ts`, `apps/web/components/workspace/sidebar/{user-menu,sidebar-item}.tsx`, `apps/web/hooks/use-workspace-paths.ts`, `packages/constants/src/workspace.ts` (`RESTRICTED_URLS`) | vollständig |
| Q8 | Icons / Illustrationen (UI 1:1) | `PROPEL/index.d.ts` (Kategorien `other-products`, `sub-brands`, `miscellaneous`, `actions`, `workspace-features`, `project-features`, `properties`), `packages/blocks/src/icons/sub-brand/pi-chat.tsx`, `packages/blocks/src/empty-state/assets/asset-types.ts` Z. 25–40, `packages/blocks/src/empty-state/assets/horizontal-stack/{ai-agents,ai-skills,memory,runner-functions,runner-scripts,script,token,webhook}.tsx`, `apps/web/app/assets/services/{github.png,slack.png,jira.svg,csv.svg,excel.svg,json.svg}` | vollständig |
| Q9 | Self-Hosting-Integrationen | `DD/self-hosting/govern/integrations/{github,gitlab,bitbucket,slack,sentry}.md` | vollständig |
| Q10 | Plane AI | `DD/self-hosting/govern/plane-ai/{configure-plane-ai,configure-embedding-model,aws-opensearch-embedding}.md`, `DD/self-hosting/govern/environment-variables.md` Z. 34–330, `DD/self-hosting/govern/advanced-search.md` | vollständig |
| Q11 | Architektur/Betrieb | `DD/self-hosting/plane-architecture.md`, `DD/self-hosting/manage/health-checks.md` (Silo/PI/Runner/Live) | vollständig |
| Q12 | OAuth-App-Plattform | `DD/dev-tools/build-plane-app/{overview,create-oauth-application,choose-token-flow,oauth-scopes,webhooks,sdks,examples}.md` | vollständig |
| Q13 | Agents | `DD/dev-tools/agents/{overview,building-an-agent,signals-content-payload,best-practices}.md` | vollständig |
| Q14 | Webhooks v2 | `DD/dev-tools/intro-webhooks.md`, Screenshot `IMG/webhooks/create-webhook.webp` | vollständig |
| Q15 | MCP-Server | `DD/dev-tools/{mcp-server,mcp-server-self-host,mcp-server-tools}.md` | vollständig |
| Q16 | Plane Compose | `DD/dev-tools/plane-compose.md` | vollständig |
| Q17 | Helm Commercial | `HC/values.yaml` Z. 514–940, 1284–1442; `HC/templates/config-secrets/{silo,runner-env,agent-consumer,pi-api-env,app-env,mcp-server-env}.yaml`; `HC/templates/ingress-nginx.yaml`; `HC/README.md` Z. 1032–1090, 1148–1200, 1247–1262, 1352–1386, 1433–1435 | relevante Teile vollständig |
| Q18 | Legacy-Importer-Screenshots (CE ≤ 0.x, 2023) | `IMG/importers/jira/{jira-workspace-setting,jira-importer-second-step,jira-importer-step-three}.png`, `IMG/importers/github/{integration,configure,import,sync,map}.png` | gesichtet |
| Q19 | `GH:` API v2 (Erstquelle) | https://github.com/makeplane/developer-docs/tree/docs/api-reference-v2/docs/api-reference/v2 (Verzeichnis), https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/{webhooks/overview.md,webhooks/create-webhook.md,webhook-logs/overview.md,artifacts/overview.md,authentication.md} | gelesen (Zusammenfassung durch Abruf-Werkzeug) |
| Q20 | `GH:` Node-SDK (Erstquelle) | https://github.com/makeplane/plane-node-sdk , https://raw.githubusercontent.com/makeplane/plane-node-sdk/main/src/api/{AgentRuns/index.ts,AgentRuns/Activities.ts,BaseResource.ts}, https://raw.githubusercontent.com/makeplane/plane-node-sdk/main/src/models/AgentRun.ts ; npm `@makeplane/plane-node-sdk` latest 0.3.1 (https://registry.npmjs.org/@makeplane%2fplane-node-sdk) | gelesen |
| Q21 | `WEB(Pxx):` aus Schwesterdokumenten | P01 (`20-…` PF-82): https://plane.so/pro („1,000 AI credits per seat per month“); P03 (`22-…` Q29): https://docs.plane.so/ai/plane-ai-credits , https://docs.plane.so/ai/ai-usage , https://forum.plane.so/t/plane-v2-4-0-plane-ai-now-available-for-self-hosted/53 , https://docs.plane.so/importers/github ; P06 (`25-…` W19/W24/W25/W30/W31): https://plane.so/changelog/release-v3-0-0-desktop-app-smarter-workflows-powerful-plane-ai-upgrades , https://plane.so/blog/introducing-plane-runner-and-scheduled-automations , https://docs.plane.so/automations/plane-runner , https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more , https://plane.so/changelog/2026-07-31-skills-plane-ai-richer-pages-audit-logs ; P07 (`26-…` W4/W9/W10/W21/W22/W32/W36/W37/W40/W42): https://docs.plane.so/core-concepts/pages/editor-blocks , https://plane.so/changelog/2025-10-15-ai-work-creation-inline-comments-filters , https://plane.so/blog/introducing-collections-and-ai-native-documentation , https://plane.so/changelog/2026-06-15-ai-block-in-pages , https://docs.plane.so/ai/plane-ai , https://plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more , https://plane.so/changelog/2026-09-15-ai-memory-workspace-labels-ms-office-edits , https://plane.so/changelog/release-v-2-1-0-text-to-work-items-video-attachments-and-block-links , https://plane.so/changelog/2025-09-01-recurring-items-doc-imports-nested-pages , https://plane.so/changelog/release-v-2-4-0-plane-ai-now-available | nur übernommen |
| Q22 | `WEB(V09):` Verifikationslauf | https://docs.plane.so/importers/{github,clickup,csv,flatfile,confluence,linear,asana} , https://docs.plane.so/ai/{mcp-connectors,ai-skills,plane-ai-credits} , https://docs.plane.so/integrations , https://docs.plane.so/devices/{desktop,mobile} , https://plane.so/download , https://plane.so/changelog/mobile , https://plane.so/changelog/release-v2-4-0-ai-autopilot-skills-catch-up-widget , https://plane.so/changelog/release-v2-5-0-new-widgets-mcp-connectors-plane-ai-for-self-hosted , https://plane.so/changelog/release-v3-3-0-work-item-csv-imports-wiki-reordering , https://plane.so/blog/agents-are-now-live-in-plane , https://plane.so/blog/introducing-the-plane-marketplace , https://plane.so/marketplace/integrations , https://plane.so/marketplace/linear , https://plane.so/issues , https://apps.apple.com/in/app/plane-projects-wiki-ai/id6657986465 ; zusätzlich `GH:` `artifacts/overview.md` per direktem Abruf erneut bestätigt | Suchzusammenfassungen (14 Suchen) |

**Wichtige Einschränkung der Quellenlage (bitte beachten):** Das WebSearch-Kontingent dieses Workflow-Laufs war beim Start dieses Teilauftrags bereits erschöpft („this turn's web search budget is used up (limit: 200 WebSearch calls per turn, shared by every agent in it)“). Es konnten daher **keine eigenen** Suchen zu docs.plane.so/plane.so (Changelog, Blog, Nutzer-Doku der Integrationen/Importer/Plane AI) durchgeführt werden; `docs.plane.so`/`plane.so` sind zudem per Netzwerk nicht direkt abrufbar. Kompensation: (a) vollständige Auswertung aller Offline-Quellen (Q1–Q18), (b) direkte Abrufe von Hersteller-Erstquellen auf GitHub (Q19, Q20), (c) Übernahme der von Schwester-Agenten gefundenen URLs (Q21, als `WEB(Pxx)` gekennzeichnet). Alles, was darüber hinaus nur plausibel, aber nicht belegt ist, ist mit **UNVERIFIZIERT** markiert. Ein Nachrecherche-Lauf mit neuem Suchkontingent ist in Abschnitt 4 als offener Punkt OP-01 geführt. **Nachtrag Verifikation:** Der Skeptiker-Lauf hat 14 gezielte Suchen durchgeführt (Q22, `WEB(V09)`); die Ergebnisse sind in die Abschnitte eingearbeitet und mit „[Verifikation]“ markiert (Details im Verifikations-Protokoll am Dokumentende).

### 1.3 Kernaussagen

1. **Alle Integrationen und Importer** der Commercial Edition laufen über den separaten Node-Dienst **„Silo“** (Image `makeplane/silo-commercial`, Prefix `/silo`, Port 3000; „integrations engine (ETL, OAuth, webhooks, and sync for GitHub, Jira, Linear, Asana, Slack, etc.)“) (`DD/self-hosting/manage/health-checks.md` Z. 202–204; `HC/values.yaml` Z. 555–612; `DD/self-hosting/plane-architecture.md` „Silo“). Er speichert verschlüsselte Fremd-Tokens (`AES_SECRET_KEY`, „encrypts stored connector tokens: NEVER ROTATE“), spricht die Plane-API intern HMAC-signiert an (`SILO_HMAC_SECRET_KEY`) und arbeitet über RabbitMQ-Batches (`BATCH_SIZE`, `DEDUP_INTERVAL`, `MQ_PREFETCH_COUNT`) (`HC/values.yaml` Z. 1284–1305; `DD/self-hosting/govern/environment-variables.md` Z. 257–266).
2. **Konnektoren laut Helm-Chart (vollständig):** `slack`, `github`, `gitlab`, `sentry`, `bitbucket`, `hubspot` (`HC/values.yaml` Z. 576–612) sowie in-App konfigurierbare Enterprise-Varianten (GitHub Enterprise, GitLab Enterprise/Self-managed, Bitbucket Data Center) und eine **Cursor-Agent-Integration** (`CURSOR_WEBHOOK_SECRET`, `HC/README.md` Z. 1088). Plan-Matrix zusätzlich: **Zapier, Zendesk, Freshdesk** (`plans.tsx` Z. 992–1023); das Badge „Coming soon“ hängt an der **gesamten** Matrix-Sektion „Integrations“, also auch an GitHub und Slack (`comingSoon: true` auf Sektionsebene, `plans.tsx` Z. 966; Darstellung `apps/web/components/workspace/billing/comparison/base.tsx` Z. 86). **[Verifikation]** Native Integrationen laut Nutzer-Doku: GitHub, GitHub Enterprise, draw.io, GitLab, Slack, Sentry (`WEB(V09)` https://docs.plane.so/integrations; draw.io → F59). **Microsoft Teams und Discord sind in keiner Quelle als Integration belegt** (Discord nur als Icon `PROPEL/other-products/discord`).
3. **Importer (belegt):** Jira (Cloud) und GitHub (Plan-Matrix), Jira Server (`JIRA_SERVER_ISSUES_PAGE_SIZE`), Linear, Asana (Health-Check-Doku), Confluence (`entities.xml`-Parsing, Helm-Kommentar), Notion (`WEB(P07)`, Marketplace). **[Verifikation, Korrektur]** ClickUp, CSV-Work-Item-Import und Flatfile (nur Cloud, Beta) sind durch eigene Doku-Seiten belegt (`WEB(V09)` https://docs.plane.so/importers/clickup , …/csv , …/flatfile → F26, F29, F60); Linear und Asana haben eigene Doku-Seiten („all plans of the Commercial Edition“). Nur **Monday** ist **nicht belegt** (nur Icon). Mitglieder-Import per CSV ist belegt (i18n).
4. **Plane AI („Pi“, „Plane Intelligence“)** ist ein eigener Python/FastAPI-Dienst mit eigener DB (`plane_pi`), Lesezugriff auf die Haupt-DB, OpenSearch (BM25 + optional k-NN-Vektoren), LLM-Providern (OpenAI, Anthropic, Groq-STT, Cohere/Bedrock-Embeddings, „Custom LLM“ OpenAI-kompatibel) – Funktionen laut Doku: „natural language chat, duplicate detection, and search across work items, pages, and projects“, Health-Doku: „chat, embeddings, transcription, LLM proxy“ (`DD/self-hosting/govern/plane-ai/configure-plane-ai.md` Z. 9; `DD/self-hosting/manage/health-checks.md` „Plane AI (pi)“). Zusätzlich belegt: AI-generierte Dashboards als versionierte HTML-**Artifacts** („Applets“-Feature, `GH:` Q19). **[Verifikation]** Ebenfalls belegt (Suchzusammenfassungen): **Skills** (Slash-Command-Prompts, Scopes personal/workspace/system), **Connectors** (MCP, Authentifizierung je Nutzer, Ort Integrations → Connectors), eingebaute **Agents** (Beta), **Autopilot-Modus** und **Catch Up** (Mobile); Memory nur über Changelog-Titel.
5. **Plattform:** OAuth-App-Plattform (Beta; „available on Plane Cloud and Plane Commercial Edition; Plane Community Edition does not include it“, `DD/dev-tools/mcp-server-self-host.md` Voraussetzungen), darauf aufbauend **Agents** (Agent Runs/Activities/Signals, Beta), **MCP-Server** (OAuth-Transport nur Commercial; CE nur stdio + PAT), **Webhooks v2**, **Plane Runner** (Enterprise Grid, Details P06), **Plane Compose** (CLI), **Desktop-App** (macOS/Linux, Self-managed ab Commercial v3.0.0) und **Mobile-Apps** (iOS/Android, Self-hosted ab Commercial v1.5.0, Push nur Cloud) – **[Verifikation]** beide per Nutzer-Doku belegt (`WEB(V09)` https://docs.plane.so/devices/desktop , https://docs.plane.so/devices/mobile).
6. **CE-Spuren:** Das CE enthält ungenutzte Altmodelle der früheren Open-Source-Integrationen (GitHub/Slack/Importer, Abschnitt 3.A/3.B) **ohne** Backend-Routen; eine nicht geroutete Integrations-Seite; eine Basis-AI (GPT-Assistent + God-Mode-AI-Seite); Webhooks v1; persönliche API-Tokens; **[Verifikation]** No-op-Stubs der Duplikaterkennung (F42).
7. **ADR-Konsequenzen:** Credits/Plan-Gates entfallen (ADR-001); Silo, PI, Runner, MCP werden **.NET-Module** im Aspire-Verbund (ADR-002); Embeddings in **pgvector** statt OpenSearch (ADR-004); airgapped relevant sind nur selbst gehostete Gegenstellen (GitHub Enterprise Server, GitLab Self-managed, Bitbucket DC, Jira Server/DC, selbst gehostetes Sentry, lokales LLM via OpenAI-kompatiblem Endpunkt).

---

## 2. Feature-Tabelle

> „Cloud-Matrix“ = `plans.tsx` (Hersteller-Vergleichstabelle im CE-Repo). „Badge“ = Plan-Badge `<Badge type="info" text="…" />` in den Developer-Docs. Bei Widerspruch sind beide genannt. „Commercial Edition“ = in jeder Commercial-Installation enthalten, Plan nicht dokumentiert. Nach ADR-001 sind **alle** Zeilen in der Zielplattform immer aktiv.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| P09-F01 | Integrations-Framework „Silo“, Integrations-Übersicht, Workspace-/persönliche Connections | Pro | Cloud-Matrix: Integrationen Pro/Business/Enterprise ✓ (Sektion „Coming soon“); Pro-Plan-Liste „Popular integrations“ | Stub/UI-Hülle im CE | `plans.tsx` Z. 963–1024; `packages/constants/src/subscription.ts`; `HC/values.yaml` Z. 555–612; `integration.json` (`integrations.*`, `silo_errors.*`) |
| P09-F02 | GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping | Pro | Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE | `plans.tsx` Z. 969–979; `DD/self-hosting/govern/integrations/github.md` Badge „Pro“; `integration.json` (`github_integration.*`) |
| P09-F03 | GitHub: Pull-Request-Automation (PR-State → Plane-State) | Pro | wie F02 | Stub/UI-Hülle im CE (nur i18n) | `integration.json` (`github_integration.pr_state_mapping*`, `MR_*`, `integrations.skip_backward_state_movement`) |
| P09-F04 | GitHub: Project Issue Sync (bi-/unidirektional inkl. Kommentare, Sub-Issues) | Pro | wie F02; Cloud-Matrix-Text „Sync Plane work items and states to GitHub … and vice-versa“ | Stub/UI-Hülle im CE (Altmodelle `GithubIssueSync`, `GithubCommentSync`) | `plans.tsx` Z. 969–972; `apps/api/plane/db/models/integration/github.py`; `integration.json` |
| P09-F05 | GitHub Enterprise (Server; Enterprise Cloud ghe.com) | Pro (Badge gilt für die gesamte Seite) | – | Stub/UI-Hülle im CE (nur i18n) | `DD/self-hosting/govern/integrations/github.md`; `integration.json` (`github_enterprise_integration.*`) |
| P09-F06 | GitLab (gitlab.com): MR-State-Mapping, Issue Sync | Pro (Badge) | – | Stub/UI-Hülle im CE (nur i18n) | `DD/self-hosting/govern/integrations/gitlab.md`; `integration.json` (`gitlab_integration.*`) |
| P09-F07 | GitLab Self-managed („Gitlab Enterprise“) | Pro (Badge gilt für die gesamte Seite) | – | Stub/UI-Hülle im CE (nur i18n) | `DD/self-hosting/govern/integrations/gitlab.md`; `integration.json` (`gitlab_enterprise_integration.*`) |
| P09-F08 | Bitbucket Cloud und Bitbucket Data Center | Pro (Badge) | – | Stub/UI-Hülle im CE (nur i18n) | `DD/self-hosting/govern/integrations/bitbucket.md`; `integration.json` (`bitbucket_dc_integration.*`); `HC/values.yaml` (`connectors.bitbucket`) |
| P09-F09 | Slack: Workspace verbinden, persönliches Konto, DM-Alerts | Pro | Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (Altmodell `SlackProjectSync`) | `plans.tsx` Z. 980–990; `DD/self-hosting/govern/integrations/slack.md` Badge „Pro“; `integration.json` (`slack_integration.*`) |
| P09-F10 | Slack: Projekt-Benachrichtigungen (Projekt ↔ Channel) | Pro | wie F09 | Stub/UI-Hülle im CE | `integration.json` (`slack_integration.project_updates.*`) |
| P09-F11 | Slack: `/plane`-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl | Pro | wie F09; Cloud-Matrix „use / commands in Slack to make changes in Plane“ | fehlt | `DD/self-hosting/govern/integrations/slack.md` (Manifest); `plans.tsx` Z. 982 |
| P09-F12 | Sentry: Issue verknüpfen/erstellen, Alert-Rule-Action, State-Mapping | Pro (Badge) | – | Stub/UI-Hülle im CE (nur i18n) | `DD/self-hosting/govern/integrations/sentry.md`; `integration.json` (`sentry_integration.*`) |
| P09-F13 | HubSpot-Connector | unklar | – | fehlt | `HC/values.yaml` Z. 609–612; `HC/README.md` Z. 1074–1076 |
| P09-F14 | Cursor-Agent-Integration | unklar | – | fehlt | `HC/values.yaml` (`env.silo_envs.cursor_webhook_secret`); `HC/README.md` Z. 1088; Icon `PROPEL/other-products/cursor` |
| P09-F15 | Zapier | Pro | Pro/Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 991–1001 |
| P09-F16 | Zendesk | Pro | Pro/Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 1002–1012 |
| P09-F17 | Freshdesk | Pro | Pro/Business/Enterprise ✓ (Coming soon) | fehlt | `plans.tsx` Z. 1013–1023 |
| P09-F18 | Microsoft Teams | unklar – **nicht belegt** | – | fehlt | keine Quelle (Negativbefund: grep über Q3, Q8, Q9, Q17) |
| P09-F19 | Discord | unklar – **nicht belegt** | – | fehlt | nur Icon `PROPEL/other-products/discord` |
| P09-F20 | OAuth Bridge (externe IdP-JWTs als API-Credentials) | unklar | – | Stub/UI-Hülle im CE | `integration.json` (`oauth_bridge_integration.*`) |
| P09-F21 | Importer-Framework (Imports-Seite, Job-Status-Kette, Historie, Importer-Worker) | Free (Cloud/Commercial; nicht CE) – JSON-Tier „Pro“ (Konvention, Verifikations-Protokoll V-K01) | Free/One „Without custom props“, Pro/Business/Enterprise „With custom props“ (für Jira/GitHub); Linear, Asana und CSV laut Nutzer-Doku auf „all plans of the Commercial Edition“; Flatfile nur Cloud (F60) | Stub/UI-Hülle im CE (Altmodell `Importer`, Typen, `IMPORTERS_LIST`) | `plans.tsx` Z. 935–962; `workspace-settings.json` (`settings.imports`, `empty_state.imports`); `integration.json` (`import_status.*`); `HC/README.md` Z. 1247–1262; `WEB(V09)` https://docs.plane.so/importers/github |
| P09-F22 | Jira-Cloud-Importer (inkl. Custom Properties) | Free (ohne Custom Props) | Free/One ohne, Pro+ mit Custom Props | Stub/UI-Hülle im CE (Typen `IJira*`, Service `jira.service.ts`) | `plans.tsx` Z. 940–949; `packages/types/src/importer/jira-importer.ts` |
| P09-F23 | Jira-Server/Data-Center-Importer | unklar | – | fehlt | `HC/values.yaml` (`jira_server_issues_page_size`, `jira_server_issues_parallel_pages`); `HC/README.md` Z. 1086–1087 |
| P09-F24 | Linear-Importer | Free (Cloud/Commercial; nicht CE): „all plans of the Commercial Edition“ [Verifikation] | – | fehlt | `DD/self-hosting/manage/health-checks.md` Z. 204; Icon `PROPEL/other-products/linear`; `WEB(V09)` https://docs.plane.so/importers/linear , https://plane.so/marketplace/linear |
| P09-F25 | Asana-Importer | Free (Cloud/Commercial; nicht CE): „all plans of the Commercial Edition“ [Verifikation] | – | fehlt | `DD/self-hosting/manage/health-checks.md` Z. 204; Icon `PROPEL/other-products/asana`; `WEB(V09)` https://docs.plane.so/importers/asana |
| P09-F26 | ClickUp-Importer | Cloud/Commercial (Plan nicht genannt) – **[Verifikation] belegt** (vorher „nicht belegt“) | – | fehlt | `WEB(V09)` https://docs.plane.so/importers/clickup ; Dok. 22 P03-F22; Dok. 26 S3 (Changelog 2025-09-01); Icon `PROPEL/other-products/clickup` |
| P09-F27 | Notion-Importer | Cloud/Commercial (Plan nicht genannt) | – | fehlt | `WEB(P07)`-Zusammenfassung in `26-paid-wissen-pages-wiki.md` Z. 331; Changelog-Titel „doc imports“ (`WEB(P07)` https://plane.so/changelog/2025-09-01-recurring-items-doc-imports-nested-pages); Dok. 26 S3; `WEB(V09)` Marketplace-Zusammenfassung (https://plane.so/marketplace/integrations) |
| P09-F28 | Confluence-Importer | Cloud/Commercial (Plan nicht genannt) | – | fehlt | `HC/values.yaml` Z. 558–559 (Kommentar „Parsing an import (e.g. a Confluence entities.xml)“); `26-…` Z. 331; `WEB(V09)` https://docs.plane.so/importers/confluence („Only HTML exports“ – Widerspruch zu `entities.xml`, s. Abschnitt F28) |
| P09-F29 | CSV-Importer für Work Items | Free (Cloud/Commercial; nicht CE): „Cloud and all plans of the Commercial Edition“ – **[Verifikation] belegt** (vorher „nicht belegt“) | – | fehlt (CE nur CSV-Export) | `WEB(V09)` https://docs.plane.so/importers/csv , https://plane.so/changelog/release-v3-3-0-work-item-csv-imports-wiki-reordering ; Dok. 22 P03-F22, O17 |
| P09-F30 | GitHub-Importer (Issues → Work Items) | Free (ohne Custom Props) | Free/One ohne, Pro+ mit Custom Props | Stub/UI-Hülle im CE (Typen `IGithub*`, Service `github.service.ts`) | `plans.tsx` Z. 950–960; `packages/types/src/importer/github-importer.ts`; `WEB(P03)` https://docs.plane.so/importers/github |
| P09-F31 | Monday.com-Importer | unklar – **nicht belegt** (nur Icon) | – | fehlt | Icon `PROPEL/other-products/monday` |
| P09-F32 | Mitglieder-Import per CSV (Workspace und Projekt) | unklar | Workspace-Text erwähnt „seat limit restrictions“ (Seat-Limit entfällt, ADR-001) | Stub/UI-Hülle im CE [Verifikation, vorher „fehlt“] (nur i18n, im CE-Code ohne Referenz) | `packages/i18n/src/locales/en/workspace.json` (`workspace.members_import.*`), `project.json` (`project.members_import.*`) |
| P09-F33 | Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“ | Pro (Cloud, Credits je Seat); Self-hosted: Badge „Commercial Edition“ | Cloud: Pro „1,000 AI credits per seat per month“ (`WEB(P01)`), höhere Pläne mehr; Drittquellen: Free 500 / Pro 1,000 / Business 2,000 Credits je Seat – Widerspruch zur Doku „per paid seat“ (UNVERIFIZIERT, `WEB(V09)` https://docs.plane.so/ai/plane-ai-credits) | Stub/UI-Hülle im CE [Verifikation, vorher „teilweise“] (Sidebar-Key `pi_chat`, i18n `plane-intelligence`; der lauffähige Basis-GPT-Assistent ist in F40/F45 erfasst) | `DD/self-hosting/govern/plane-ai/configure-plane-ai.md`; `DD/api-reference/workspace-features/overview.md` (`pi`); `workspace-settings.json` (`settings.plane-intelligence`); `20-…` PF-82 |
| P09-F34 | Pi-Chat („Plane AI“-Chat): Navigation, Modellwahl, Anhänge, Spracheingabe | wie F33 | wie F33 | Stub/UI-Hülle im CE | `apps/web/components/workspace/sidebar/{user-menu.tsx Z. 55–61, sidebar-item.tsx Z. 52}`; `apps/web/hooks/use-workspace-paths.ts` Z. 19; `navigation.json` (`sidebar.pi_chat`); `configure-plane-ai.md` (Modelle, Voice, File uploads) |
| P09-F35 | Plane AI: Connectors (MCP; Authentifizierung je Nutzer; Beispiele GitHub, Sentry, Granola) | wie F33 | – | Stub/UI-Hülle im CE (nur i18n `tour.json`) | `tour.json` (`product_tour.mcp_connectors.step_zero`); `WEB(V09)` https://docs.plane.so/ai/mcp-connectors |
| P09-F36 | Plane AI: Skills (Slash-Command-Prompts; Scopes personal/workspace/system) | wie F33 („available when Plane AI is enabled“) | – | Stub/UI-Hülle im CE | Illustration `ai-skills` (`packages/blocks/src/empty-state/assets/horizontal-stack/ai-skills.tsx`); Changelog-Titel `WEB(P06)` W30/W31; `WEB(V09)` https://docs.plane.so/ai/ai-skills |
| P09-F37 | Plane AI: Memory | wie F33 (UNVERIFIZIERT) | – | Stub/UI-Hülle im CE | Illustration `memory`; Icons `MemoryOutline/Filled`; Changelog-Titel `WEB(P07)` W32/W36 |
| P09-F38 | Plane AI: eingebaute Agents (Playbook, Skills, MCP-Tools, Scope, Trigger, Memory) | wie F33 (Beta; Plan nicht genannt) | – | Stub/UI-Hülle im CE | Illustration `ai-agents`; Icons `AgentOutline/Filled`, `AgentAltOutline/Filled`; `WEB(V09)` https://plane.so/blog/agents-are-now-live-in-plane |
| P09-F39 | AI-Assistent im Editor (Ask Pi, Selection-Aktionen, AI-Block, Page-Proposals) | Pro (Selection-Aktionen, Seitenzusammenfassung – Dok. 26 P07-27) | AI-Block `/ai` und Prompt/Proposals: Business (Dok. 26 P07-28/P07-29, verifiziert; Blog „Pro+“ älter) | Stub/UI-Hülle im CE [Verifikation, vorher „teilweise“] (Ask-Pi-Menü eingebunden, Extension `ai` deaktiviert, Backend-Route `rephrase-grammar` fehlt) | `26-paid-wissen-pages-wiki.md` §3.27–3.29; `editor.json` (`ai_block.*`); `apps/web/components/pages/editor/ai/menu.tsx` |
| P09-F40 | AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung | unklar | – | teilweise im CE (GPT-Assistent im Work-Item-Modal) | `apps/web/components/issues/issue-modal/components/description-editor.tsx` Z. 247–267; Changelog-Titel `WEB(P07)` W9/W37 |
| P09-F41 | AI-Suche / Semantic Search (Embeddings, Vektorsuche) | Commercial Edition (optional; ohne Embedding-Modell BM25) | – | fehlt | `DD/self-hosting/govern/plane-ai/configure-embedding-model.md` |
| P09-F42 | Duplicate Detection (semantisch ähnliche Work Items) | Commercial Edition (benötigt Embedding-Modell) | – | Stub/UI-Hülle im CE [Verifikation, vorher „fehlt“] (Typen `de-dupe.ts`, No-op-Hook, Modal-State, i18n `duplicate_issue(s)_found`) | `configure-plane-ai.md` Z. 9; `configure-embedding-model.md` Z. 9; `packages/types/src/de-dupe.ts`; `apps/web/hooks/use-debounced-duplicate-issues.tsx`; `apps/web/components/issues/issue-modal/base.tsx` Z. 68, 382, 405; `apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–46; `common.json` Z. 284–285; Dok. 20 PF-104 |
| P09-F43 | AI-Aktionen Summary/Catch-up/Copy-as-prompt/AI-Filter | unklar | Catch Up (Mobile) belegt; übrige UNVERIFIZIERT | fehlt (nur Propel-Icons, kein CE-Code) [Verifikation, vorher Stub] | `PROPEL/index.d.ts` (`AiSummary*`, `Catchup*`, `CopyAsPrompt*`, `AiFilter*`, `Ask*`, `NewChat*`, `Voice*`, `Mic*`); `WEB(V09)` https://plane.so/changelog/release-v2-4-0-ai-autopilot-skills-catch-up-widget , https://plane.so/issues ; AI-Filter vgl. Dok. 24 P05-35 „Text to PQL“ (Enterprise Grid) |
| P09-F44 | Applets / Artifacts (AI-generierte HTML-Dashboards, versioniert, publizierbar) | Plan-Feature „Applets“ (Plan unklar) | – | fehlt | `GH:` Q19 `artifacts/overview.md` |
| P09-F45 | LLM-Provider- und Embedding-Konfiguration (inkl. Custom LLM, Bedrock, Voice) | Commercial Edition | – | teilweise im CE (God-Mode „Artificial intelligence“: `LLM_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`) | `configure-plane-ai.md`; `environment-variables.md` Z. 173–240, 294–330; `HC/values.yaml` Z. 729–798; `apps/admin/app/(all)/(dashboard)/ai/*` |
| P09-F46 | AI-Usage, Credits, Token-Budget | Cloud: je Plan (entfällt ADR-001); Budget-Schalter Commercial | – | fehlt | `HC/values.yaml` (`ai_usage_agent_max_tokens_budget`, `ai_usage_enforcement_enabled`); `WEB(P03)` https://docs.plane.so/ai/ai-usage , https://docs.plane.so/ai/plane-ai-credits |
| P09-F47 | OAuth-App-Plattform (Build your own app, Consent, Bot-/User-Token, Scopes, Installationen) | Commercial Edition (Beta) | „Plane Cloud and Plane Commercial Edition; Community Edition does not include it“ | Stub/UI-Hülle im CE (nur i18n `applications.*`) | `DD/dev-tools/build-plane-app/*.md`; `DD/dev-tools/mcp-server-self-host.md`; `workspace-settings.json` (`settings.applications.*`) |
| P09-F48 | App-Marketplace (Listing, Kategorien, Review-Status, Medien) | Commercial Edition (UNVERIFIZIERT) | „Supported Plans“-Filter je App (entfällt) | Stub/UI-Hülle im CE (nur i18n) | `workspace-settings.json` (`applications.categories*`, `supported_plans*`, `app_consent_unapproved_*`); `HC/templates/ingress-nginx.yaml` (`/marketplace/`) |
| P09-F49 | App-Mentions / Bot-User je Installation | Commercial Edition (Beta) | „Agents … do not count as billable users“ | teilweise im CE (`User.is_bot`, `bot_type`) | `applications.enable_app_mentions*`; `DD/dev-tools/agents/overview.md`; `apps/api/plane/db/models/user.py` Z. 52–53, 115–116 |
| P09-F50 | Agents-Plattform (Agent Runs, Activities, Signals, Agent-Webhooks) | Commercial Edition (Beta) | – | Stub/UI-Hülle im CE (nur Scope-Text `agents`, Icons) | `DD/dev-tools/agents/*.md`; `GH:` Q20; `HC/values.yaml` (`agent_consumer`) |
| P09-F51 | Webhooks v2 (Titel, Dot-Events, PQL-Filter, `previous_attributes`, Delivery-Statistik) | unklar (Screenshot aus Business-Workspace) | – | teilweise im CE (Webhooks v1) | `DD/dev-tools/intro-webhooks.md`; `IMG/webhooks/create-webhook.webp`; `GH:` Q19 |
| P09-F52 | Workspace-Access-Tokens (workspace-gebunden, mit Rolle) | unklar | – | teilweise im CE [Verifikation, vorher Stub]: Token-Kern vorhanden (persönliche Tokens mit CRUD `users/api-tokens/`, `X-Api-Key`-Authentifizierung, wiederverwendete UI-Texte `workspace_settings.settings.api_tokens.*`, `APIToken.workspace`-FK und `user_type` Bot); Workspace-Bindung, Rolle und Workspace-Settings-Seite fehlen | `workspace-settings.json` (`settings.api_tokens.*`); `empty-state.json` (`workspace_tokens`); `DD/dev-tools/mcp-server.md`; `apps/api/plane/db/models/api.py`; `apps/api/plane/app/urls/api.py`; `apps/web/components/api-token/delete-token-modal.tsx` |
| P09-F53 | MCP-Server (28 Tools, OAuth-/PAT-/stdio-Transport) | OAuth-Transport: Commercial Edition | CE nur stdio + PAT | teilweise im CE (nutzbar via stdio gegen CE-API v1) | `DD/dev-tools/mcp-server*.md`; `HC/values.yaml` Z. 844–870 |
| P09-F54 | Plane Runner (Skripte in Sandbox) | Enterprise Grid | nur Enterprise Grid | Stub/UI-Hülle im CE | `25-…` F19; `workspace-settings.json` (`settings.runners.*`); `HC/templates/config-secrets/runner-env.yaml` |
| P09-F55 | Plane Compose („project as code“-CLI) | kein eigener Plan; nutzt Commercial-API (Workspace-WIT „(Enterprise)“) | – | fehlt | `DD/dev-tools/plane-compose.md` |
| P09-F56 | Offizielle SDKs (Node, Python) | kein Plan | – | fehlt (externe Pakete) | `DD/dev-tools/build-plane-app/sdks.md`; `GH:` Q20 |
| P09-F57 | Desktop-App (macOS, Linux) | unklar (Self-managed ab Commercial v3.0.0; Plan nicht genannt) | – | Stub/UI-Hülle im CE (`Device.DeviceType.DESKTOP`, reservierter Slug `desktop`) | `WEB(P06)` https://plane.so/changelog/release-v3-0-0-desktop-app-smarter-workflows-powerful-plane-ai-upgrades ; `WEB(V09)` https://docs.plane.so/devices/desktop , https://plane.so/download ; `apps/api/plane/db/models/device.py` |
| P09-F58 | Mobile-Apps (iOS/Android) | unklar (Cloud inkl. Free-Workspace; Self-hosted „all plans of the Commercial Edition“ ab v1.5.0) | Push-Benachrichtigungen nur Plane Cloud | Stub/UI-Hülle im CE [Verifikation, vorher „teilweise“]: ungenutzte Modelle `Device`/`DeviceSession`, Profilfelder, i18n `mobile_details` ohne Referenz | `apps/api/plane/db/models/device.py`; `apps/api/plane/db/models/user.py` Z. 246–249; `auth.json` (`sso.providers.*.setup_modal.mobile_details`); `WEB(V09)` https://docs.plane.so/devices/mobile , https://plane.so/changelog/mobile |
| P09-F59 | draw.io-Integration (Diagramme/Boards in Pages; Aktivierung über Integrations) – Querverweis | Business (Dok. 26 P07-21, verifiziert) – Widerspruch: Pro (Dok. 22 P03-F31) | – | fehlt (nur CSS-Selektor `.editor-drawio-component`) | Dok. 26 §3.21 P07-21; Dok. 22 P03-F31; `WEB(V09)` https://docs.plane.so/integrations ; `packages/editor/src/plugins/drag-handle.ts` Z. 32 |
| P09-F60 | Flatfile-Importer (CSV über Flatfile, Beta) | Cloud-only | „only available on Plane Cloud“; Self-hosted → CSV-Importer F29 | fehlt | `WEB(V09)` https://docs.plane.so/importers/flatfile ; Dok. 22 P03-F22, O17 |
| P09-F61 | Plane AI: Autopilot-Modus (Ausführung ohne Einzelbestätigung) | wie F33 | belegt für Mobile (Changelog Mobile v2.4.0) | fehlt (nur Propel-Icons `AutopilotGoOutline/Filled`) | `WEB(V09)` https://plane.so/changelog/release-v2-4-0-ai-autopilot-skills-catch-up-widget ; `PROPEL/index.d.ts` |

---

## 3. Feature-Abschnitte

Aufbau je Feature: **Funktionsbeschreibung (UI & Verhalten)** · **UI-Hinweise (1:1)** · **Datenmodell-Hinweise** · **API-Hinweise** · **Migrationshinweise (.NET/Angular)** · **Quellen** · **Konfidenz**. Wörtliche UI-Texte stammen aus `packages/i18n/src/locales/en/*.json` (vollständig in Anhang A/B) und sind 1:1 in die Ziel-i18n zu übernehmen (ADR-005/006). Upsell-Elemente entfallen (ADR-001).

### 3.A Integrationen

#### P09-F01 – Integrations-Framework „Silo“, Integrations-Übersicht, Connections

**Funktionsbeschreibung (UI & Verhalten)**

- **Einstieg:** Workspace Settings → Gruppe „Features“ → **Integrations** (EE-Sidebar laut Screenshot `IMG/webhooks/create-webhook.webp`: Features = Projects, Integrations, Plane Runner, Connections, Teamspaces, Initiatives, Customers, Releases, Templates, Relations, Plane AI, Automations; Developer = Webhooks, Access Tokens …). Seitentexte: Titel/Heading „Integrations“, Beschreibung „Connect with popular tools and services to sync your work across your entire workflow ecosystem.“, Seitenkopf „Work with your Plane data in available apps or your own.“ / „View all the integrations in use by this workspace or you.“ (`workspace_settings.settings.integrations.{title,heading,description,page_title,page_description}`). Auf derselben Seite der Button **„Build your own“** zum Anlegen eigener OAuth-Apps (`DD/dev-tools/build-plane-app/create-oauth-application.md` Schritt 1–2) → P09-F47.
- **Integrationskarten** je Anbieter mit Logo, Name und Beschreibung (`github_integration.name/description`, `gitlab_integration.*`, `slack_integration.*`, `sentry_integration.*`, `bitbucket_dc_integration.*`, `github_enterprise_integration.*`, `gitlab_enterprise_integration.*`, `oauth_bridge_integration.*`) und Aktion „Configure“ (`integrations.configure`). Zustände:
  - nicht konfiguriert (Instanz hat keine App-Credentials): Badge „Not configured“ + Meldung „{name} integration is not configured. Please contact your instance admin to configure it.“ (`integrations.not_configured`, `integrations.not_configured_message_admin`; die Cloud-Variante `not_configured_message_support` „… Please contact support …“ entfällt im Self-hosted-Ziel);
  - nicht freigeschaltet: „{name} is not enabled for this workspace.“ (`integrations.not_enabled`) – im Original Feature-Flag/Plan; im Ziel: Instanz-Schalter des Admins (ADR-001: kein Plan-Gate);
  - Fehler: „Not able to fetch supported integrations. Please try again later.“ (`integrations.error_fetching_supported_integrations`), „Not able to access the external API. Please try again later.“ (`integrations.external_api_unreachable`); Laden: „Loading“ (`integrations.loading`); fehlende Rechte: „You are not authorized to view this page.“ (`integrations.unauthorized`).
- **Detailseite je Integration** mit Rücklink „Back to integrations“ (`integrations.back_to_integrations`); typische Bausteine: Organisation/Workspace verbinden, persönliches Konto verbinden („Disconnect personal {providerName} account“, `integrations.disconnect_personal_account`), Projekt-Zuordnungen, State-Mappings (Dropdowns „Select State“ / „Set State“ / „Choose Project...“, `integrations.select_state/set_state/choose_project`).
- **Persönliche Verbindungen** im Profil: Profil-Einstellungen → „Connections – Manage your workspace connections settings.“ (`account_settings.connections.{title,heading,description}`, Menüpunkt `profile.actions.connections` „Connections“). Dort verbindet/trennt ein Nutzer seine persönlichen Konten (GitHub, GitLab, Slack) je Workspace (Zuordnung abgeleitet aus `github_integration.connect_personal_account*`, `slack_integration.connect_personal_account`, `integrations.disconnect_personal_account`; konkrete Listendarstellung UNVERIFIZIERT).
- **Projekt-Einstellungen → Integrations:** Leerzustand „No integrations configured – Configure GitHub and other integrations to sync your project work items.“ (`project_settings.empty_state.integrations.{title,description}`; im CE ohne Referenz) – projektbezogene Ansicht der Mappings (Inhalt UNVERIFIZIERT).
- **Onboarding:** Checkliste „Link Integrations“, Abschnitt „Power up your workspace“, Link „Browse more integrations“ (`tour.json` `get_started.checklist_section.checklist_items.item_6.title`, `get_started.integrations_section.*`).
- **Eindeutigkeit:** Ein externes Konto (GitHub-Organisation, Slack-Team usw.) darf nur mit **einem** Plane-Workspace verbunden sein: „You have already connected your organization with a workspace. Please disconnect the existing connection before connecting a new one.“ (`silo_errors.cannot_create_multiple_connections`). Weitere Fehlercodes (vollständig): `invalid_query_params`, `invalid_installation_account`, `generic_error`, `connection_not_found`, `multiple_connections_found`, `cannot_create_multiple_connections`, `installation_not_found`, `user_not_found`, `error_fetching_token`, `invalid_app_credentials`, `invalid_app_installation_id` (Texte Anhang A).
- **Berechtigung:** Konfiguration der Integrationen nur Workspace-Admins (CE-Altseite: `allowPermissions([EUserPermissions.ADMIN], WORKSPACE)`, sonst `NotAuthorizedView`; `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/integrations/page.tsx` Z. 33–40). Persönliche Verbindungen: jeder Nutzer für sich (abgeleitet).
- **Instanz-Konfiguration (Self-hosted):** App-Credentials je Anbieter kommen aus Umgebungsvariablen (GitHub, GitLab-Cloud, Bitbucket-Cloud, Slack, Sentry, HubSpot – Anhang C); Enterprise-/Self-managed-Varianten (GitHub Enterprise, GitLab Self-managed) werden **in der App** pro Workspace über Formulare eingetragen (F05, F07). Helm: `services.silo.connectors.<slack|github|gitlab|sentry|bitbucket|hubspot>.enabled` (`HC/values.yaml` Z. 576–612).
- **Selbstregistrierung als Plane-App:** Silo-Integrationen sind intern als „Marketplace-Apps“ registriert; Fehlerbehebung „Application secret value not found for key: x-github-id“: Redis-Schlüssel `plane_app_details_github` löschen, `SILO_BASE_URL` setzen, `python manage.py reset_marketplace_app_secrets` ausführen (`DD/self-hosting/govern/integrations/github.md` Troubleshooting). ⇒ Jede Integration handelt in Plane über eine OAuth-App-Installation mit Bot-User (vgl. F47/F49; CE-Altmodell `WorkspaceIntegration.actor` = „Bot user“, `api_token`).
- **Betrieb:** Health `GET /silo/health/` → 201 `{"message":"Welcome to Silo health check"}`, `GET /silo/health/check-hmac` → 201 `{"message":"Welcome to Silo API health check"}` (prüft API-Erreichbarkeit), `GET /silo/health/check-db` → 200 `{"message":"Silo DB is up and running"}`, Fehler 500 (`DD/self-hosting/manage/health-checks.md` Z. 202–245). Event-Verarbeitung batchweise (`BATCH_SIZE` 60/100, `DEDUP_INTERVAL` 3 s, `MQ_PREFETCH_COUNT` 10/1, `REQUEST_INTERVAL` 400 ms, `IMPORTERS_QUEUE_NAME` `celery`) (`DD/self-hosting/govern/environment-variables.md` Z. 257–266; `HC/templates/config-secrets/silo.yaml`).

**UI-Hinweise (1:1)**

- Anbieter-Logos – **[Verifikation] vollständiges Inventar** `PROPEL/other-products/` (41 Logos): `asana`, `bitbucket`, `chatgpt`, `chrome`, `claude`, `clickup`, `codex`, `copilot`, `cursor`, `deepseek`, `discord`, `docker`, `dribbble`, `evermuse`, `facebook`, `figma`, `github`, `gitlab`, `glm-z-ai`, `gmail`, `granola`, `instagram`, `intercom`, `jira`, `kimi`, `kubernetes`, `linear`, `linkedin`, `monday`, `ms-excel`, `ms-powerpoint`, `ms-word`, `oidc`, `posthog`, `postman`, `raycast`, `saml`, `sentry`, `slack`, `x`, `youtube`. Mit belegtem Integrations-/Importer-/Connector-Bezug: `github`, `gitlab`, `bitbucket`, `slack`, `sentry`, `jira`, `linear`, `asana`, `clickup`, `cursor` (F14), `granola` (Connector, F35); `claude` und `raycast` erscheinen laut Suchzusammenfassung als Marketplace-Einträge (`WEB(V09)` https://plane.so/marketplace/integrations); Verwendungszweck der übrigen Logos UNVERIFIZIERT; CE-Raster-Assets `apps/web/app/assets/services/{github.png,slack.png,jira.svg}`; Navigations-Icons `IntegrationsOutline/Filled`, `ConnectionsOutline/Filled`, `SyncOutline/Filled`, `UnsyncOutline/Filled` (`PROPEL/miscellaneous`).
- CE-Altkarte (Referenz für Abstände/Typo, nicht für Inhalt): Zeile `flex items-center justify-between gap-2 border-b border-subtle bg-surface-1 px-4 py-6`, Logo `h-10 w-10`, Titel `text-body-xs-medium` + `TickCircleOutline` (`h-3.5 w-3.5 text-success-primary`) wenn installiert, Beschreibung `text-body-xs-regular text-secondary`, Buttons `variant="primary" size="sm"` „Install“/„Installing...“ bzw. `variant="danger"` „Uninstall“/„Uninstalling...“, Tooltip „You don't have permission to perform this“ (`apps/web/components/integration/single-integration-card.tsx` Z. 117–188).
- Pixelgenaue Referenz-Screenshots der **aktuellen** EE-Integrationsseiten liegen nicht vor (nur Legacy-Screenshot `IMG/importers/github/integration.png` von 2023: Karte „GitHub • Installed – Activate GitHub integrations on individual projects to sync with specific repositories.“ + roter Button „Remove installation“) → OP-02.

**Datenmodell-Hinweise**

- CE-Altmodelle (nur fachliche Orientierung, ADR-003): `Integration` (`title`, `provider` unique, `network` 1=Private/2=Public, `description` JSON, `author`, `webhook_url`, `webhook_secret`, `redirect_url`, `metadata`, `verified`, `avatar_url`; Tabelle `integrations`) und `WorkspaceIntegration` (`workspace`, `actor` = Bot-User, `integration`, `api_token` → `APIToken`, `metadata`, `config`; unique `workspace`+`integration`) (`apps/api/plane/db/models/integration/base.py`).
- Ziel (Vorschlag): `IntegrationProvider` (statischer Katalog: `github`, `github_enterprise`, `gitlab`, `gitlab_enterprise`, `bitbucket`, `bitbucket_dc`, `slack`, `sentry`, `hubspot`, `cursor`, `oauth_bridge`); `WorkspaceConnection` (`workspace_id`, `provider`, `external_account_id` + `external_account_name` (Org/Team/Instanz), `base_url` (Enterprise), `app_config` (verschlüsselt: App-ID, Client-ID/-Secret, Webhook-Secret, Private Key), `credentials` (verschlüsselt: Installations-/Bot-Token, Refresh-Token, Ablauf), `connected_by`, `connected_at`, `bot_user_id`; **unique (`provider`, `external_account_id`)** gemäß `cannot_create_multiple_connections`); `UserConnection` (`user_id`, `workspace_id`, `provider`, `external_user_id`, `external_login`, verschlüsselte Tokens); `EntityConnection` (`workspace_connection_id`, `project_id`, `entity_type` ∈ {`repository`, `gitlab_project`, `slack_channel`, `sentry_project`, …}, `external_entity_id`, `external_entity_name`, `config` jsonb – State-Mappings, Sync-Richtung, `skip_backward_state_movement`); `ExternalLink` (`provider`, `external_id`, `external_url`, `entity_type` ∈ {`work_item`, `comment`, `pull_request`}, `plane_entity_id`, `last_synced_at`, `sync_hash`) – verallgemeinert die CE-Altmodelle `GithubIssueSync`/`GithubCommentSync`; `InboundWebhookEvent` (`provider`, `delivery_id`, `received_at`, `payload`, `status`, `attempts`, `error`) für Idempotenz/Retry.
- Geheimnisse: ASP.NET Core Data Protection (Schlüsselring in PostgreSQL) statt `AES_SECRET_KEY`/`AES_SALT` (Helm-Hinweis „NEVER ROTATE“ zeigt: Schlüsselrotation muss Re-Encryption unterstützen).

**API-Hinweise**

- **Externe Callback-/Webhook-Pfade** (vom Fremdsystem aufgerufen, vollständige Liste in Anhang C). Empfehlung: Pfade **identisch** übernehmen (`/silo/api/...`), damit die Einrichtungsanleitungen der Hersteller-Doku 1:1 gelten.
- **Interne App-API (Web-Client → Backend):** in der Commercial Edition nicht dokumentiert. CE-Altservices (Backend-Routen fehlen im CE): `GET /api/integrations/`, `GET /api/workspaces/{slug}/workspace-integrations/`, `POST /api/workspaces/{slug}/workspace-integrations/{provider}/`, `DELETE /api/workspaces/{slug}/workspace-integrations/{id}/provider/`, `GET /api/workspaces/{slug}/workspace-integrations/{integrationSlug}/github-repositories`, `GET|POST /api/workspaces/{slug}/projects/{projectId}/workspace-integrations/{integrationId}/github-repository-sync/`, `GET|POST /api/workspaces/{slug}/projects/{projectId}/workspace-integrations/{integrationId}/project-slack-sync/`, `DELETE …/project-slack-sync/{slackSyncId}` (`apps/web/services/integrations/integration.service.ts`, `github.service.ts`, `apps/web/services/app_installation.service.ts`, `apps/web/services/project/project.service.ts` Z. 121–160). Vorschlag Ziel: `/api/workspaces/{slug}/integrations/` (Liste inkl. Status), `/api/workspaces/{slug}/integrations/{provider}/connections/…`, `/api/users/me/connections/…` – UNVERIFIZIERT (Neuentwurf).
- Instanz-Konfig an Frontend: CE liefert `github_app_name`, `slack_client_id` in `GET /api/instances/` (`apps/api/plane/license/api/views/instance.py` Z. 83–133); Ziel: zusätzlich `integrations: [{provider, configured: bool}]`.

**Migrationshinweise (.NET)**

- Silo (Node) entfällt (ADR-002) → .NET-Modul `Plane.Integrations` (eigenes Aspire-Projekt `integrations`, gleiche DB, eigene Schemas), Hintergrundverarbeitung über `BackgroundService` + Transactional Outbox/RabbitMQ (wie P03/P06). Bibliotheken: Octokit (GitHub/GHE), GitLab-REST via `HttpClient` (oder NGitLab), SlackNet, Bitbucket/Sentry/HubSpot via `HttpClient` + Polly.
- Airgapped (ADR-004): SaaS-Gegenstellen (github.com, gitlab.com, slack.com, sentry.io, bitbucket.org) sind optional/abschaltbar; selbst gehostete Varianten (GHE Server, GitLab Self-managed, Bitbucket DC, Sentry self-hosted via `SENTRY_BASE_URL`) müssen ohne Internet funktionieren; CA-Bundle-Unterstützung (Helm `prepare-ca-bundle`-Init-Container) übernehmen.

**Quellen:** `workspace-settings.json`; `integration.json`; `settings.json`; `project-settings.json`; `tour.json`; `apps/api/plane/db/models/integration/base.py`; `apps/web/components/integration/single-integration-card.tsx`; `apps/web/hooks/use-integration-popup.tsx`; `DD/self-hosting/govern/integrations/*.md`; `DD/self-hosting/manage/health-checks.md`; `DD/self-hosting/plane-architecture.md`; `HC/values.yaml`; `HC/templates/config-secrets/silo.yaml`; `IMG/webhooks/create-webhook.webp`.
**Konfidenz:** hoch (Texte, Konfiguration, Fehlercodes) / mittel (Seitenstruktur) / niedrig (interne API).

---

#### P09-F02 – GitHub: Organisation verbinden, persönliches Konto, Repository-Mapping

**Funktionsbeschreibung**

- Karte „GitHub – Connect and sync your GitHub work items with Plane“ (`github_integration.name/description`).
- **Connect Organization** – „Connect your GitHub organization with Plane“: Installation der GitHub-App in einer GitHub-Organisation (Redirect zu `https://github.com/apps/{GITHUB_APP_NAME}/installations/new?state={workspaceSlug}` – CE-Altfluss `apps/web/hooks/use-integration-popup.tsx` Z. 26; aktueller Setup-/Callback-Pfad `https://<domain>/silo/api/github/auth/callback`, „Redirect on update“ an). Während der Verbindung „Processing“; danach Zeile „GitHub org added by and time“ (`github_integration.connect_org*`, `processing`, `org_added_desc`); Fehler „Error fetching connection details from server“ (`connection_fetch_error`). Trennen über Disconnect (Text siehe F01).
- **Connect Personal Account** – „Connect your personal GitHub account with Plane.“ → OAuth-User-Flow (`/silo/api/github/auth/user/callback`), Erfolg „Personal account connected – Your GitHub account is now connected to Plane“ (`github_integration.connect_personal_account*`, `personal_account_connected*`). Zweck (abgeleitet, UNVERIFIZIERT): Aktionen/Kommentare aus Plane erscheinen in GitHub unter der Identität des Nutzers statt des Bots; Zuordnung GitHub-Nutzer ↔ Plane-Nutzer für Assignees/Autoren.
- **Repository Mapping** – „Map your GitHub repositories with Plane projects.“; Dialog „Link GitHub Repository to a Plane Project“ mit Dropdowns „Choose Repository...“ und „Choose Project...“, Speichern „Save“ (`github_integration.repo_mapping*`, `link`, `choose_repository`, `integrations.choose_project`, `save`).
- **Voraussetzungen GitHub-App** (vom Admin anzulegen): Repository-Berechtigungen Issues (read/write), Metadata (read), Pull requests (read/write); Account-Berechtigungen Email addresses (read), Profile (read/write); Events: Installation target, Meta, Issue comment, Issues, Pull request, Pull request review, Pull request review comment, Pull request review thread, Push, Repository sub issues; „Expire user authorization tokens“ **aus**; App muss **public** sein (sonst „Invalid request callback URL.“) (`DD/self-hosting/govern/integrations/github.md`).
- **Instanz-Variablen:** `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_APP_NAME`, `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY` (Base64, `cat private_key.pem | base64 -w 0`; Fehler „Failed to create GitHub connection: Invalid keyData“), Helm zusätzlich `GITHUB_WEBHOOK_SECRET` (`DD/…/github.md`; `HC/values.yaml` Z. 584–591).

**UI-Hinweise:** Logo Propel `Github`; Abschnitte als Karten mit Titel + Beschreibung (Texte oben); Personal-Account-Zeile mit Status. Struktur der aktuellen EE-Seite: UNVERIFIZIERT (OP-02).
**Datenmodell:** `WorkspaceConnection(provider=github, external_account_id=installation_id/org_id)`, `UserConnection(provider=github)`, `EntityConnection(entity_type=repository, external_entity_id=repo_id, project_id)`. CE-Alt: `GithubRepository` (`name`, `url`, `config`, `repository_id` BigInt, `owner`; Projektbezug) und `GithubRepositorySync` (`repository` 1:1, `credentials`, `actor` Bot-User, `workspace_integration`, `label` → automatisch gesetztes Label; unique `project`+`repository`) (`apps/api/plane/db/models/integration/github.py`).
**API:** extern Anhang C; intern UNVERIFIZIERT.
**Migration:** Octokit `GitHubAppsClient` (JWT aus Private Key, Installation-Token), Webhook-Signaturprüfung `X-Hub-Signature-256`.
**Quellen:** `integration.json`; `DD/self-hosting/govern/integrations/github.md`; `HC/values.yaml`; `apps/api/plane/db/models/integration/github.py`; `apps/web/hooks/use-integration-popup.tsx`.
**Konfidenz:** hoch (Texte/Setup) / mittel (Verhalten persönliches Konto).

---

#### P09-F03 – GitHub: Pull-Request-Automation (PR-State-Mapping)

**Funktionsbeschreibung**

- Abschnitt „Pull Request Automation – Configure pull request state mapping from GitHub to your Plane project“ bzw. „Pull Request State Mapping – Map GitHub pull request states to your Plane project“; Leerzustand „Mapped PR states will appear here“; Dialoge „Add Pull Request State Mapping for Plane project“ / „Edit Pull Request State Mapping for Plane project“; Entfernen „Remove this Pull Request State Mapping“ mit Bestätigung „Are you sure you want to remove this pull request state mapping?“ (`github_integration.pull_request_automation*`, `pr_state_mapping*`, `add_pr_state_mapping`, `edit_pr_state_mapping`, `remove_pr_state_mapping*`).
- Je Plane-Projekt wird pro PR-Ereignis ein Ziel-State gewählt („Select State“ / „Set State“). **PR-Ereignisse (vollständig):** `DRAFT_MR_OPENED` „Draft Open“, `MR_OPENED` „Open“, `MR_REVIEW_REQUESTED` „Review Requested“, `MR_READY_FOR_MERGE` „Ready for Merge“, `MR_MERGED` „Merged“, `MR_CLOSED` „Closed“ (`github_integration.*`).
- Option **„Prevent issues from moving to an earlier state due to PR updates“** (`integrations.skip_backward_state_movement`): wenn aktiv, verschiebt ein PR-Ereignis ein Work Item nicht in einen State, der in der Projekt-State-Reihenfolge (State-Gruppe/Sequence) vor dem aktuellen liegt (Vergleichsregel UNVERIFIZIERT; Vorschlag: Vergleich über State-Gruppen-Rang backlog<unstarted<started<completed<cancelled, bei gleicher Gruppe über `sequence`).
- **Verknüpfung PR ↔ Work Item:** Mechanismus nicht dokumentiert (UNVERIFIZIERT). Vorschlag (branchenüblich, mit Rückfrage OP-04): Work-Item-Kennung `PROJ-123` im PR-Titel, -Beschreibung oder Branch-Namen; der PR wird als Link am Work Item hinterlegt; ein PR-Ereignis setzt den gemappten State aller referenzierten Work Items.
- Push-/Review-Events werden abonniert (F02) – Nutzung (z. B. Commit-Links, Review-Status im Activity-Feed) UNVERIFIZIERT.

**UI-Hinweise:** Tabelle/Liste „PR-Ereignis → State-Dropdown“ (State-Dropdown wie CE-State-Picker mit State-Icons `PROPEL/work-item-states/*`).
**Datenmodell:** `EntityConnection.config.pr_state_map = { "DRAFT_MR_OPENED": state_id|null, "MR_OPENED": …, "MR_REVIEW_REQUESTED": …, "MR_READY_FOR_MERGE": …, "MR_MERGED": …, "MR_CLOSED": … }`, `skip_backward_state_movement: bool`; `ExternalLink(entity_type=pull_request)`.
**API:** Webhook-Eingang `POST /silo/api/github/github-webhook` (Events `pull_request`, `pull_request_review`, …).
**Migration:** State-Wechsel über den regulären Work-Item-Update-Pfad (damit Workflows/Automationen/Activity/Webhooks greifen; Actor = Integrations-Bot bzw. verknüpfter Nutzer).
**Quellen:** `integration.json`; `DD/self-hosting/govern/integrations/github.md`.
**Konfidenz:** hoch (Texte/Ereignisliste) / niedrig (Verknüpfungsregel).

---

#### P09-F04 – GitHub: Project Issue Sync

**Funktionsbeschreibung**

- Abschnitt „Project Issue Sync – Sync issues from GitHub to your Plane project“, Leerzustand „Mapped project issue sync will appear here“, Konfiguration „Configure Issue Sync State“ (Zuordnung `ISSUE_OPEN` „Issue Open“ und `ISSUE_CLOSED` „Issue Closed“ → Plane-State), Richtung „Select issue sync direction“:
  - **„Bidirectional - Sync issues and comments both ways between GitHub and Plane“**,
  - **„Unidirectional - Sync issues and comments from GitHub to Plane only“** mit Warnhinweis „Data from GitHub Issue will replace data in Linked Plane Work Item (GitHub → Plane only)“;
  - Start „Start Sync“; Hinweis nach Einrichtung „Work items are synced to {project}“; Entfernen „Remove this Project Issue Sync“ / „Are you sure you want to remove this project issue sync?“ (`github_integration.project_issue_sync*`, `configure_project_issue_sync_state`, `select_issue_sync_direction`, `allow_bidirectional_sync`, `allow_unidirectional_sync*`, `remove_project_issue_sync*`, `issue_sync_message`, `start_sync`).
- Cloud-Matrix-Beschreibung: „Sync Plane work items and states to GitHub work items and states. Update GitHub automatically with activity from Plane and vice-versa.“ (`plans.tsx` Z. 971–972).
- Abonnierte Events „Issues“ (created/updated/closed/reopened/assigned/labeled/transferred), „Issue comment“ (added/edited/deleted), „Repository sub issues“ (Eltern-/Kind-Beziehungen) (`DD/…/github.md` Events-Tabelle) ⇒ Sync umfasst Titel, Beschreibung, Status (über `ISSUE_OPEN/CLOSED`-Mapping), Kommentare, Sub-Issues (Parent), sehr wahrscheinlich Labels und Assignees (Feldumfang im Detail UNVERIFIZIERT).
- Konfliktregel unidirektional: GitHub überschreibt verknüpfte Plane-Daten (Warntext). Bidirektional: Konfliktauflösung UNVERIFIZIERT (Vorschlag: last-writer-wins je Feld mit Echo-Unterdrückung über `ExternalLink.sync_hash`).
- CE-Altlogik: Sync erzeugte je Repo ein Label (`GithubRepositorySync.label`) und je Issue/Kommentar Mapping-Zeilen (`GithubIssueSync`: `repo_issue_id`, `github_issue_id`, `issue_url`, `issue`, `repository_sync`; `GithubCommentSync`: `repo_comment_id`, `comment`, `issue_sync`) (`apps/api/plane/db/models/integration/github.py`).

**UI-Hinweise:** Radio-Auswahl der Richtung mit Warn-Callout bei unidirektional; State-Dropdowns für „Issue Open“/„Issue Closed“.
**Datenmodell:** `EntityConnection(entity_type=repository, config.issue_sync = { direction: "bidirectional"|"unidirectional", state_map: { ISSUE_OPEN, ISSUE_CLOSED }, enabled })`; `ExternalLink` für Work Items und Kommentare (ersetzt `GithubIssueSync`/`GithubCommentSync`); Work Items aus GitHub mit `external_source="github"`, `external_id=<issue id>` (Felder existieren im CE-Modell `Issue`, `apps/api/plane/db/models/issue.py` Z. 162–163).
**API:** eingehend Webhook (Anhang C); ausgehend GitHub REST/GraphQL; Plane-seitige Änderungen über Event-Stream (Outbox, P06) → Integrations-Consumer.
**Migration:** Echo-Schleifen verhindern (Aktor = Integrations-Bot ignorieren, Hash-Vergleich); Markdown ↔ Plane-HTML-Konvertierung (Markdig / HtmlAgilityPack) – exakte Konvertierregeln UNVERIFIZIERT.
**Quellen:** `integration.json`; `plans.tsx`; `DD/…/github.md`; `apps/api/plane/db/models/integration/github.py`.
**Konfidenz:** hoch (UI-Optionen) / mittel (Feldumfang).

---

#### P09-F05 – GitHub Enterprise (Server und Enterprise Cloud)

**Funktionsbeschreibung**

- Karte „GitHub Enterprise – Connect and sync your GitHub Enterprise organization with Plane.“ (`github_enterprise_integration.name/description`). Funktional wie F02–F04, aber App-Konfiguration **im UI pro Workspace**: Formular „GitHub Enterprise Configuration – Configure GitHub Enterprise to connect with Plane.“ mit Feldern (alle Pflicht): **App ID** („The ID of the app you created in your GitHub Enterprise organization.“, Platzhalter `e.g., "1234567890"`, Fehler „App ID is required“), **App Slug** („The slug of the app …“, `e.g., "plane-github-enterprise"`, „App slug is required“), **Base URL** („The base URL of your GitHub Enterprise organization.“, `e.g., "https://gh.plane.town"`, „Base URL is required“ / „Invalid base URL“), **Client ID**, **Client Secret**, **Webhook Secret**, **Private Key (Base64 encoded)** („Base64 encoded private key …“, Platzhalter `e.g., "MIIEpAIBAAKCAQEA...`, „Private key is required“); Button „Connect App“ (`github_enterprise_integration.*`, vollständig Anhang A).
- GitHub-seitige Callback-/Setup-/Webhook-URLs: `https://<domain>/silo/api/oauth/github-enterprise/auth/callback`, `…/auth/user/callback`, Webhook `https://<domain>/silo/api/github-enterprise/github-webhook`; für GHE.com wird die App unter `https://<github-domain>.ghe.com/enterprises/<enterprise-slug>/settings/apps` angelegt (`DD/…/github.md` Tab „GitHub Enterprise Server“).

**UI-Hinweise:** Formular mit Label/Beschreibung/Platzhalter je Feld; Base-URL-Validierung (gültige `http(s)`-URL).
**Datenmodell:** `WorkspaceConnection(provider=github_enterprise, base_url, app_config{app_id, app_slug, client_id, client_secret, webhook_secret, private_key})` verschlüsselt.
**Migration:** Octokit mit `GitHubClient(..., new Uri(baseUrl + "/api/v3/"))`; airgapped-relevant (ADR-004).
**Quellen:** `integration.json`; `DD/self-hosting/govern/integrations/github.md`.
**Konfidenz:** hoch.

---

#### P09-F06 – GitLab (gitlab.com)

**Funktionsbeschreibung**

- Karte „Gitlab – Connect and sync your Gitlab Merge Requests with Plane.“; „Connect Organization – Connect your Gitlab organization with Plane.“; Fehler „Error fetching connection details from server“ (`gitlab_integration.*`).
- **Projektverbindungen:** „Gitlab Project Connections – Sync merge requests from Gitlab to Plane projects.“, „Plane Project Connection – Configure pull requests state mapping from Gitlab to Plane projects“, Dialog „Link Gitlab repository to Plane project“ mit „Choose Entity“ (GitLab-Projekt/Gruppe), „Choose Project“, „Link Plane project“; Entfernen „Remove Connection“ / „Are you sure you want to remove this connection?“.
- **MR-Automation:** „Pull Request Automation – Configure pull request state mapping from Gitlab to Plane“, Hinweis „With Gitlab integration Enabled, you can automate work item workflows“; je Ereignis ein State: „On draft MR open, set the state to“ (`DRAFT_MR_OPENED`), „On MR open, set the state to“ (`MR_OPENED`), „On MR review requested, set the state to“ (`MR_REVIEW_REQUESTED`), „On MR ready for merge, set the state to“ (`MR_READY_FOR_MERGE`), „On MR merged, set the state to“ (`MR_MERGED`), „On MR closed, set the state to“ (`MR_CLOSED`).
- **Issue Sync** analog GitHub (F04): „Project Issue Sync – Sync issues from Gitlab to your Plane project“, Leerzustand, „Configure Issue Sync State“ (`ISSUE_OPEN`/`ISSUE_CLOSED`), Richtung bidirektional/unidirektional mit Warnung „Data from Gitlab Issue will replace data in Linked Plane Work Item (Gitlab → Plane only)“, „Remove this Project Issue Sync“, „Save“, „Start Sync“, „Choose Repository...“ (vollständig Anhang A).
- **OAuth-App (Admin):** Redirect URI `https://[YOUR_DOMAIN]/silo/api/gitlab/auth/callback`, „Confidential“ an, Scopes `api`, `read_api`, `read_user`, `read_repository`, `profile`, `email`; Instanz-Variablen `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET` (`DD/self-hosting/govern/integrations/gitlab.md`).

**Datenmodell/API/Migration:** wie F02–F04 mit `provider=gitlab`, `entity_type=gitlab_project`; Webhooks registriert die Integration selbst pro GitLab-Projekt (Scope `api`) – Webhook-Pfad für gitlab.com in der Doku nicht genannt (UNVERIFIZIERT; Vorschlag `/silo/api/gitlab/gitlab-webhook`).
**Quellen:** `integration.json`; `DD/…/gitlab.md`.
**Konfidenz:** hoch (Texte) / mittel (Verhalten).

---

#### P09-F07 – GitLab Self-managed („Gitlab Enterprise“)

- Karte „Gitlab Enterprise – Connect and sync your Gitlab Enterprise instance with Plane.“; Formular „Gitlab Enterprise Configuration – Configure Gitlab Enterprise to connect with Plane.“ mit **Base URL** („The base URL of your Gitlab Enterprise instance.“, `e.g., "https://glab.plane.town"`, Pflicht/gültig), **App ID** („The app ID of the app you created in your Gitlab Enterprise instance.“, `e.g., "7cd732xxxxxxxxxxxxxx"`), **Client Secret** (`e.g., "gloas-xxxx…"`), **Webhook Secret** („A random webhook secret that will be used to verify the webhook from Gitlab Enterprise instance.“, `e.g., "webhook1234567890"`), Button „Connect App“ (`gitlab_enterprise_integration.*`).
- GitLab-seitig: Redirect URI `https://<your-domain>/silo/api/oauth/gitlab-enterprise/auth/callback`, gleiche Scopes wie F06 (`DD/…/gitlab.md` Tab „GitLab Self-managed“). Funktionsumfang danach wie F06.
- **Datenmodell:** `WorkspaceConnection(provider=gitlab_enterprise, base_url, app_config{app_id, client_secret, webhook_secret})`. **Airgapped-relevant.**
- **Quellen/Konfidenz:** `integration.json`; `DD/…/gitlab.md` – hoch.

---

#### P09-F08 – Bitbucket Cloud und Bitbucket Data Center

- Belegter UI-Text nur: „Bitbucket Data Center – Connect and sync your Bitbucket Data Center repositories with Plane.“ (`bitbucket_dc_integration.name/description`). Doku: „Sync pull requests and commits with Plane work items for development workflow tracking“ (Front-Matter `DD/self-hosting/govern/integrations/bitbucket.md`).
- **Bitbucket Cloud (OAuth-Consumer):** Callback `https://[YOUR_DOMAIN]/silo/api/oauth/bitbucket/auth/callback`; Scopes: Account `email`, `read`; Repositories `read`, `write`; Pull requests `read`, `write`; Projects `read`; Issues `read`, `write`; Webhooks `read`, `write`; Variablen `BITBUCKET_CLIENT_ID`, `BITBUCKET_CLIENT_SECRET`, `BITBUCKET_WEBHOOK_SECRET`.
- **Bitbucket Data Center (Application Link):** Redirect `https://[YOUR_DOMAIN]/silo/api/oauth/bitbucket-dc/auth/callback`; Rechte Projects `Admin`, Repositories `Read`/`Write`/`Admin` (Webhooks verwalten). Konfiguration der DC-Credentials in der App (Doku-Abschnitt „Configure Plane instance“ enthält nur den Cloud-Tab; DC-Formularfelder UNVERIFIZIERT, vermutlich analog F07: Base URL, Client ID/Secret).
- Verhalten (PR-State-Automation analog F03/F06, Issue-Sync?) **UNVERIFIZIERT**; Issue-Scopes deuten auf Issue-Sync hin.
- **Datenmodell:** `provider=bitbucket|bitbucket_dc`, `entity_type=repository`. **Airgapped-relevant (DC).**
- **Quellen:** `integration.json`; `DD/…/bitbucket.md`; `HC/values.yaml` Z. 603–607. **Konfidenz:** mittel (Setup) / niedrig (Verhalten).

---

#### P09-F09 – Slack: Workspace verbinden, persönliches Konto, DM-Alerts

**Funktionsbeschreibung**

- Karte „Slack – Connect your Slack workspace with Plane.“ Liste „Connected Slack workspaces“ mit Zeilen „Connected on {date}“ und Aktion „Disconnect {name} workspace“ (`slack_integration.connected_slack_workspaces`, `connected_on`, `disconnect_workspace`). Installation per Slack-OAuth (Bot), Callback `https://[YOUR_DOMAIN]/silo/api/slack/team/auth/callback/`.
- **Persönliches Konto:** „Connect your personal Slack account with Plane.“ / „Link your personal {providerName} account to Plane.“ / „Your personal {providerName} account is now connected to Plane.“ (`slack_integration.connect_personal_account`, `link_personal_account`, `personal_account_connected`); Callback `…/silo/api/slack/user/auth/callback/`; User-Scopes `chat:write`, `identify`, `im:read`, `im:write`, `links:write`, `links:read`.
- **DM-Alerts:** „Get notified in Slack DMs for important updates, reminders, and alerts just for you.“ (`slack_integration.alerts.dm_alerts.title`) – persönliche Benachrichtigungen (Inbox-Ereignisse) per Slack-DM; Umfang der Ereignistypen UNVERIFIZIERT (Vorschlag: dieselben Kategorien wie die E-Mail-Benachrichtigungseinstellungen des CE: Property changes, State change, Issue completed, Comments, Mentions – `common.json` `property_changes_description` usw.).
- **Slack-App (Admin):** aus Manifest (Anhang C): Bot-Scopes `channels:join`, `channels:read`, `users:read`, `users:read.email`, `chat:write`, `chat:write.customize`, `channels:history`, `groups:history`, `mpim:history`, `im:history`, `links:read`, `links:write`, `groups:read`, `im:read`, `mpim:read`, `reactions:read`, `reactions:write`, `files:read`, `files:write`, `im:write`, `commands`; `token_rotation_enabled: true`, `socket_mode_enabled: false`, `org_deploy_enabled: false`; Variablen `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, Helm zusätzlich `SLACK_SIGNING_SECRET`, `SLACK_BASE_URL` (`DD/self-hosting/govern/integrations/slack.md`; `HC/values.yaml` Z. 577–583).

**Datenmodell:** `WorkspaceConnection(provider=slack, external_account_id=team_id, external_account_name=team_name, credentials{bot_token, refresh_token, expires_at})`, `UserConnection(provider=slack, external_user_id, user_token)`, Benutzerpräferenz `slack_dm_alerts_enabled` (UNVERIFIZIERT). CE-Alt `SlackProjectSync` (`access_token`, `scopes`, `bot_user_id`, `webhook_url`, `data`, `team_id`, `team_name`, `workspace_integration`; unique `team_id`+`project`) und Typ `ISlackIntegrationData` (`incoming_webhook.{url,channel,channel_id,configuration_url}`) – Altkonzept „Incoming Webhook je Projekt“ (`apps/api/plane/db/models/integration/slack.py`; `packages/types/src/integration.ts`). CE-Altfluss im Browser-Popup (600×600, Schließen-Polling alle 1 000 ms): Workspace-Installation `https://slack.com/oauth/v2/authorize?scope=chat:write,im:history,im:write,links:read,links:write,users:read,users:read.email&client_id={SLACK_CLIENT_ID}&state={workspaceSlug}`, Projekt-Channel `…?scope=incoming-webhook&client_id=…&state={workspaceSlug},{projectId}[,{workspaceIntegrationId}]` (`apps/web/hooks/use-integration-popup.tsx` Z. 25–31, 57–79; `apps/web/components/integration/slack/select-channel.tsx`).
**Migration:** SlackNet (Events API, Interactivity, OAuth v2 mit Token-Rotation), Signaturprüfung `X-Slack-Signature` mit Signing Secret.
**Quellen:** `integration.json`; `DD/…/slack.md`; `HC/values.yaml`; CE-Altmodelle.
**Konfidenz:** hoch (Texte/Setup) / niedrig (DM-Ereignisumfang).

---

#### P09-F10 – Slack: Projekt-Benachrichtigungen

- Abschnitt „Project Notifications – Configure Slack channels for project notifications“, Button „Add new project notifications“, Leerzustand „Projects connected with Slack Channels will appear here.“ (`slack_integration.project_updates.*`).
- Formular „Configure Slack Channel – Receive project notifications in selected Slack channel when work item is created“: Dropdown **„Plane Project“** (Platzhalter „Select a project“, leer „No projects available“) und **„Slack Channel“** („Select a channel“, „No channels available“); Ladefehler „Failed to load channels from Slack“; Begrenzungen „All projects are already connected to Slack channels.“ und „All Slack channels are already connected to projects.“ ⇒ **1:1-Zuordnung** (ein Projekt höchstens ein Channel, ein Channel höchstens ein Projekt).
- Toasts: „Project connection created successfully“, „Project connection updated successfully“, „Project connection deleted successfully“, Fehler „Failed to delete project connection“, „Failed to create project connection“, „Failed to upsert project connection“, Ladefehler „We couldn't load your project connections. This could be due to a network issue or a problem with the integration.“
- Ereignis: Nachricht beim **Anlegen eines Work Items** im Projekt (Formularbeschreibung); weitere Ereignisse UNVERIFIZIERT. Bot tritt dem Channel bei (`channels:join`).
- **Datenmodell:** `EntityConnection(provider=slack, entity_type=slack_channel, external_entity_id=channel_id, project_id)`; Unique-Constraints auf (`workspace_connection_id`, `project_id`) und (`workspace_connection_id`, `external_entity_id`).
- **UI:** Liste der Paare „Projekt (Logo/Name) → #channel“ mit Bearbeiten/Löschen (Darstellung UNVERIFIZIERT).
- **Quellen/Konfidenz:** `integration.json` – hoch (Texte/Regeln).

---

#### P09-F11 – Slack: `/plane`-Command, Message-Shortcuts, Thread-Sync, Link-Unfurl

Belegt ausschließlich über das offizielle Slack-App-Manifest (`DD/self-hosting/govern/integrations/slack.md`) und die Cloud-Matrix („Get Plane activity in Slack and use / commands in Slack to make changes in Plane.“, `plans.tsx` Z. 982):

| Baustein | Konfiguration | Verhalten laut Doku | Endpunkt |
|---|---|---|---|
| Slash-Command | `"command": "/plane"`, `"description": "Create issue in Plane"`, `should_escape: false` | „allows users to create issues directly from Slack using a slash command“ | `POST /silo/api/slack/command/` |
| Message-Shortcut 1 | `"name": "Create new issue"`, `type: message`, `callback_id: issue_shortcut`, „Create a new issue in plane“ | „users can create issues from messages inside Slack“ | Interactivity `POST /silo/api/slack/action/` |
| Message-Shortcut 2 | `"name": "Link Work Item"`, `callback_id: link_work_item`, „Links thread with an existing work item“ | Thread ↔ bestehendes Work Item verknüpfen | `POST /silo/api/slack/action/` |
| Dynamische Auswahllisten | `message_menu_options_url` | Optionen (Projekte, States, Nutzer …) für Modals | `POST /silo/api/slack/options/` |
| Thread-Sync | Bot-Events `message.channels`, `message.im` | „When a message is posted in a channel/DM, an event is triggered in Plane to support thread sync“; Bot sendet „thread messages while syncing issues“ | `POST /silo/api/slack/events` |
| Link-Unfurl | `unfurl_domains: [YOUR_DOMAIN]`, Event `link_shared` | „When an issue, cycle, or module link is pasted in Slack, it generates a preview of the entity.“ | `POST /silo/api/slack/events` |

- Unterargumente des Slash-Commands (z. B. `/plane create`, `/plane link`), Modal-Felder und Darstellung der Unfurl-Karten: **UNVERIFIZIERT** (OP-05). Vorschlag für Modal „Create work item“: Projekt, Titel, Beschreibung (vorbefüllt mit Nachrichtentext), State, Priorität, Assignees, Labels; nach Anlage Bot-Antwort im Thread mit Link; danach Thread-Antworten ↔ Work-Item-Kommentare synchronisieren.
- **Datenmodell:** `ExternalLink(provider=slack, entity_type=thread, external_id=channel_id:thread_ts, plane_entity_id=work_item_id)`; Kommentar-Mapping `ExternalLink(entity_type=comment, external_id=message_ts)`.
- **Migration:** Slack verlangt Antwort < 3 s → sofort 200 und asynchron verarbeiten (`response_url`).
- **Quellen:** `DD/…/slack.md`; `plans.tsx`. **Konfidenz:** hoch (Bausteine) / niedrig (Detailverhalten).

---

#### P09-F12 – Sentry

**Funktionsbeschreibung**

- Karte „Sentry – Connect your Sentry workspace with Plane.“, Liste „Connected Sentry workspaces“ („Connected on {date}“, „Disconnect {name} workspace“) (`sentry_integration.*`).
- **State Mapping:** „Map Sentry issue states to your project states. Configure which states to use when a Sentry issue is resolved or unresolved.“, Button „Add new state mapping“, Leerzustand „No state mappings configured. Create your first mapping to sync Sentry issue states with your project states.“, Lade-/Fehlertexte „Loading project states...“, „Error loading states“, „No states available“, „You don't have permission to access states for this project“, „Project states not found“, „Server error while loading states“, „We couldn't load your state mappings. This could be due to a network issue or a problem with the integration.“ ⇒ je Plane-Projekt: State für „resolved“ und State für „unresolved“.
- **In Sentry (Issue-Link-Komponente, Schema):** „Create“ eines Plane-Work-Items aus einem Sentry-Issue mit Pflichtfeldern **Title** (Default `issue.title`), **Description** (Default `issue.description`), **Project** (Select) und optional **Assignees** (Multi), **Priorities**, **Labels** (Multi), **State**, **Module**, **Cycle** (jeweils abhängig von `project_id`); „Link“ eines bestehenden Work Items über Select **Issue** (`identifier`, `skip_load_on_open`).
- **Alert-Rule-Action** „Create Plane Work Item or Intake Issue“ („Create a Plane Work Item or Intake Issue when an alert is triggered“): Pflicht **Type** (`intake` „Intake“ | `work_item` „Work Item“), **Project**; optional Assignees, State, Labels.
- **Sync:** Sentry-Webhook „issue“ mit `created`, `resolved`, `assigned`, `archived`, `unresolved` → verknüpfte Work Items folgen (resolved/unresolved über State-Mapping; assigned → Assignee-Sync; archived → Verhalten UNVERIFIZIERT).
- **Sentry-Integration (Admin):** Public Integration; Webhook URL `https://[YOUR_DOMAIN]/silo/api/sentry/sentry-webhook/`; Redirect `https://[YOUR_DOMAIN]/silo/api/oauth/sentry/auth/callback`; „Verify Installation“ aus, „Alert Rule Action“ an; Rechte Project Read, Team Read, Release/Distribution No Access, Issue & Event Read & Write, Organization Read, Member Read, Alerts Read; Variablen `SENTRY_BASE_URL` (Default `https://sentry.io`, self-hosted möglich), `SENTRY_CLIENT_ID`, `SENTRY_CLIENT_SECRET`, `SENTRY_INTEGRATION_SLUG` (`DD/self-hosting/govern/integrations/sentry.md`).

**API-Hinweise (Sentry-UI-Komponenten-Endpunkte, vollständig laut Schema):** `/api/sentry/issues/link`, `/api/sentry/issues` (Select „Issue“), `/api/sentry/issues/create`, `/api/sentry/users`, `/api/sentry/priorities`, `/api/sentry/labels`, `/api/sentry/states`, `/api/sentry/modules`, `/api/sentry/cycles`, `/api/sentry/projects`, `/api/sentry/alert-rule`. Sentry löst diese relativ zur Integrations-Basis auf; ob tatsächlich unter `/silo/api/sentry/...` bedient wird, ist UNVERIFIZIERT (OP-06). Antworten im Sentry-Select-Format `[{label, value}]` und Issue-Link-Antwort `{webUrl, project, identifier}` gemäß Sentry-Integration-Platform-Spezifikation (Fremdspezifikation).
**Datenmodell:** `WorkspaceConnection(provider=sentry, external_account_id=org_slug, credentials{access/refresh token})`; `EntityConnection(entity_type=sentry_state_mapping, project_id, config{resolved_state_id, unresolved_state_id})`; `ExternalLink(provider=sentry, entity_type=work_item, external_id=sentry_issue_id)`; Intake-Erzeugung nutzt CE-Intake (`apps/api/plane/db/models/intake.py`).
**Quellen:** `integration.json`; `DD/…/sentry.md`; `HC/values.yaml` Z. 596–601. **Konfidenz:** hoch (Schema/Setup) / mittel (Sync-Verhalten).

---

#### P09-F13 – HubSpot-Connector

- Belegt nur als Silo-Connector mit `HUBSPOT_CLIENT_ID`/`HUBSPOT_CLIENT_SECRET` („HubSpot Integration“) (`HC/values.yaml` Z. 609–612; `HC/README.md` Z. 1074–1076; `HC/templates/config-secrets/silo.yaml`). Keine UI-Texte, keine Doku. Fachlicher Zweck **UNVERIFIZIERT** (naheliegend: Abgleich mit dem Bezahl-Feature „Customers“/Customer Requests, P02 §2.2). → OP-07 (Rückfrage, ob nachzubauen).
- **Konfidenz:** niedrig.

#### P09-F14 – Cursor-Agent-Integration

- Belegt nur über `CURSOR_WEBHOOK_SECRET` („Webhook secret for the Cursor agent integration (`CURSOR_WEBHOOK_SECRET`), stored in the silo Secret“) (`HC/README.md` Z. 1088; `HC/values.yaml` `env.silo_envs.cursor_webhook_secret`) und Icon `Cursor` (`PROPEL/other-products/cursor`). Verhalten **UNVERIFIZIERT** (naheliegend: Work Items an einen Cursor-Cloud-Agenten delegieren; Cursor meldet Status per Webhook zurück; vgl. Agents-Plattform F50). → OP-07.
- **Konfidenz:** niedrig.

#### P09-F15 – Zapier · P09-F16 – Zendesk · P09-F17 – Freshdesk

| Feature | Matrix-Beschreibung (wörtlich) | Plan | Status | Quelle |
|---|---|---|---|---|
| Zapier | „Run if-then-else automations using Zapier.“ | Pro/Business/Enterprise (Sektion `comingSoon: true`) | keine weiteren Spuren | `plans.tsx` Z. 991–1001 |
| Zendesk | „Create Plane work items from Zendesk tickets.“ | Pro/Business/Enterprise (Coming soon) | keine weiteren Spuren | `plans.tsx` Z. 1002–1012 |
| Freshdesk | „Create Plane work items from Freshdesk tickets.“ | Pro/Business/Enterprise (Coming soon) | keine weiteren Spuren | `plans.tsx` Z. 1013–1023 |

- Ob diese Integrationen ausgeliefert wurden, ist nicht belegt (Sektion als „COMING SOON“ markiert). **[Verifikation]** Gezielte Suche ohne Beleg für eine Plane-Zapier-, -Zendesk- oder -Freshdesk-Integration; die Nutzer-Doku der nativen Integrationen nennt sie nicht (`WEB(V09)` https://docs.plane.so/integrations). Das „Coming soon“-Badge hängt an der gesamten Sektion „Integrations“ (auch an GitHub/Slack), nicht an den drei Einträgen einzeln (`plans.tsx` Z. 966; `base.tsx` Z. 86). **Migrationsvorschlag:** Zapier über die vorhandenen Bausteine (OAuth-App F47 + Webhooks v2 F51 + REST-API) abbildbar; Zendesk/Freshdesk als eingehende Webhooks (Ticket → Work Item oder Intake) im Integrationsmodul. → OP-07.
- **Konfidenz:** hoch (Matrix) / niedrig (Funktion).

#### P09-F18 – Microsoft Teams · P09-F19 – Discord

- **Negativbefund:** Weder i18n (alle 3 859 en-Schlüssel), Helm-Connectoren, Self-Hosting-Doku noch Plan-Matrix enthalten Microsoft Teams. Discord existiert nur als Logo-Icon `Discord` in `PROPEL/other-products` (und als Community-Support-Link in `DD/self-hosting/govern/instance-admin.md`). Beide sind **nicht als Plane-Integration belegt** → nicht als Bezahl-Feature spezifizierbar; OP-07. **[Verifikation]** Eine Suche nach einer Plane-Microsoft-Teams-Integration ergab keinen Treffer (`WEB(V09)`).

---

#### P09-F20 – OAuth Bridge (externe IdP-Tokens für API-Zugriff)

**Funktionsbeschreibung**

- Integrationskarte „OAuth Bridge – Validate external IdP tokens for API access.“, Kopftext „Validate externally-issued OIDC/JWT tokens from your IdP (Azure AD, Okta, etc.) for Plane API access.“; Status „Connected“, Buttons „Connect“, „Uninstall“ / „Uninstalling...“; Toasts „OAuth Bridge installed successfully.“, „Failed to install OAuth Bridge.“, „OAuth Bridge uninstalled.“, „Failed to uninstall OAuth Bridge.“
- Liste **„Token Providers – Configure external IdPs whose JWTs are accepted as API credentials.“**, Button „Add provider“, Dialog „Edit Provider“, Status „Enabled“/„Disabled“, Aktion „Test“ mit Ergebnis „JWKS Reachable“ / „JWKS Unreachable“ („Could not fetch JWKS from the configured URL.“); Leerzustand „No providers configured. – Add an IdP to enable external token authentication.“; Toasts „Provider updated.“, „Provider added.“, „Failed to save provider.“, „Provider deleted.“, „Failed to delete provider.“, „Failed to update provider.“
- **Provider-Formular (Feld · Validierung):** Name (Pflicht; Platzhalter „e.g. Azure AD Production“; „Human-readable label for this identity provider“) · Issuer (Pflicht; erwarteter `iss`; Platzhalter `https://login.microsoftonline.com/tenant-id/v2.0`) · JWKS URL (Pflicht, **muss HTTPS** sein; „HTTPS endpoint serving the provider's JSON Web Key Set“) · Audience (erwartete `aud`, kommagetrennt; `api://my-app-id`) · User claims (Pflicht, ≥1, kommagetrennt, „Comma-separated JWT claims to match against the Plane email (first match wins)“; `email, preferred_username, upn`) · Allowed signing algorithms (≥1, Mehrfachauswahl „Select algorithms“, „Asymmetric algorithms accepted for JWT signature verification“) · JWKS cache TTL (Sekunden, **min. 60**, Default **24 h**) · Rate limit („count/period (e.g. 120/minute). Leave blank for the default rate limit.“) · Checkbox „Enable this provider“; Buttons „Saving...“/„Update“ (`oauth_bridge_integration.*`, vollständig Anhang A).
- **Verhalten (abgeleitet):** Ein API-Request mit `Authorization: Bearer <externes JWT>` wird akzeptiert, wenn Signatur (JWKS, erlaubter asymmetrischer Algorithmus), `iss`, `aud` passen; der Nutzer wird über den ersten vorhandenen Claim aus „User claims“ per **E-Mail** einem Plane-Nutzer zugeordnet; Rate-Limit je Provider. Rechte = Rechte des zugeordneten Nutzers (UNVERIFIZIERT). Ebene (Workspace vs. Instanz): Karte liegt in den Workspace-Integrationen → Workspace (UNVERIFIZIERT).
- **Datenmodell:** `OAuthBridgeProvider` (`workspace_id`, `name`, `issuer`, `jwks_url`, `audiences[]`, `user_claims[]`, `allowed_algorithms[]` ∈ {RS256, RS384, RS512, PS256, PS384, PS512, ES256, ES384, ES512 – Liste UNVERIFIZIERT}, `jwks_cache_ttl_seconds` (≥60, Default 86400), `rate_limit` (`^\d+/(second|minute|hour|day)$`), `is_enabled`).
- **Migration:** ASP.NET Core `JwtBearer` mit dynamischen Issuer-/Key-Resolvern (`IssuerSigningKeyResolver` + gecachter JWKS via `ConfigurationManager<OpenIdConnectConfiguration>`), eigenes Authentifizierungsschema neben API-Key/OAuth; `System.Threading.RateLimiting` je Provider.
- **Quellen:** `integration.json`. **Konfidenz:** hoch (UI/Validierung) / mittel (Laufzeitverhalten).

---

#### P09-F59 – draw.io-Integration (Querverweis) [Verifikation ergänzt]

- **Einordnung:** Laut Nutzer-Doku ist draw.io eine der **nativen Integrationen** („Embed Draw.io diagrams directly in Plane pages to visualize workflows, architectures, and processes.“, `WEB(V09)` https://docs.plane.so/integrations). Aktivierung durch einen Workspace-Admin unter Workspace Settings → Integrations → draw.io → „Configure“ (Dok. 26 P07-21; Dok. 22 P03-F31). Die Editor-Funktion (Blöcke „Draw.io diagram“/„Draw.io board“, `/draw`) ist in **Dok. 26 §3.21 (P07-21)**, die Infrastruktur (`makeplane/drawio:v2.5.0`, Ingress `/drawio/`, `DRAWIO_EMBED_URL`) in **Dok. 22 P03-F31** spezifiziert – hier nicht dupliziert.
- **Tier:** **Business** (Dok. 26 P07-21, dort in Verifikation 2 korrigiert: Doku „Advanced Page blocks“ = Business). **Widerspruch:** Dok. 22 P03-F31 führt „Pro“ (auf der älteren, in P07 nicht reproduzierbaren Angabe „Integrationsdoku Pro“ beruhend) → die spezifischere und aktuellere Quelle P07 gilt.
- **CE-Status:** fehlt (nur CSS-Selektor `.editor-drawio-component` in `packages/editor/src/plugins/drag-handle.ts` Z. 32).
- **Ziel:** Integrationskarte „draw.io“ im Integrations-Katalog (F01) als Aktivierungsschalter; airgapped nur mit gebündelter draw.io-Webapp (ADR-004).
- **Konfidenz:** mittel.

---

### 3.B Importer

#### P09-F21 – Importer-Framework (Imports-Seite, Job-Status, Historie, Importer-Worker)

**Funktionsbeschreibung (UI & Verhalten)**

- **Einstieg:** Workspace Settings → **Imports** – Titel/Heading „Imports“, Beschreibung „Connect and import data from your existing project management tools to streamline your workflow integration.“; Leerzustand der Historie „No imports yet – Find all your previous imports here and download them.“ (`workspace_settings.settings.imports.{title,heading,description}`, `workspace_settings.empty_state.imports.{title,description}`; beide ohne CE-Referenz). Illustrationen `apps/web/app/assets/empty-state/workspace-settings/imports-{light,dark}{,-resp}.webp` liegen im CE.
- **Import-Quellen (Kacheln):** belegt: Jira, Jira Server/DC, Linear, Asana, ClickUp, Confluence, Notion, CSV, Flatfile (nur Cloud, Badge „Beta“), GitHub (F22–F30, F60); Monday nicht belegt (F31). **[Verifikation]** Laut Nutzer-Doku sind die Importer „available on Plane Cloud and the Commercial Edition“; für Linear, Asana und CSV ausdrücklich „all plans of the Commercial Edition“; Einstieg „Workspace settings → Imports“ → „Import“ bei der jeweiligen Quelle; Rolle Workspace-Admin (Linear-Doku) (`WEB(V09)` https://docs.plane.so/importers/github , …/linear , …/asana , …/csv , …/flatfile , …/clickup , …/confluence). Logos Propel `Jira`, `Linear`, `Asana`, `Github`, `Clickup`, `Monday`.
- **Job-Status (vollständige Enum aus `import_status.*`):** `queued` „Queued“, `created` „Created“, `initiated` „Initiated“, `pulling` „Pulling“, `timed_out` „Timed Out“, `pulled` „Pulled“, `progressing` „Progressing“, `transforming` „Transforming“, `transformed` „Transformed“, `pushing` „Pushing“, `finished` „Finished“, `error` „Error“, `cancelled` „Cancelled“. Abgeleitete ETL-Phasen: **Pull** (Quelle lesen) → **Transform** (auf Plane-Modell abbilden) → **Push** (in Plane schreiben). Exakte Übergangsreihenfolge UNVERIFIZIERT; Vorschlag: `created → queued → initiated → pulling → pulled → transforming → transformed → pushing → progressing → finished`, Endzustände `finished|error|timed_out|cancelled`.
- **Historie:** Liste früherer Imports mit Quelle → Zielprojekt, Status-Badge, Datum, Initiator, Zählern; „Refresh status“; Download (Legacy-Screenshot `IMG/importers/jira/jira-workspace-setting.png`: „Previous Imports“, „Refresh status“, Einträge „Import from Github to <Projekt> · Completed · 124 issues imported | 20 March 2023 · Download“; `IMG/importers/github/import.png`: „Import from GitHub to Plane Private · Completed · Apr 21, 2023 | Imported by Team Docs · ⋯-Menü“). Der Leerzustandstext „Find all your previous imports here and download them.“ ist identisch mit der aktuellen i18n → Download eines Import-Berichts ist weiterhin Teil der Funktion (Inhalt UNVERIFIZIERT; Vorschlag: CSV/JSON-Bericht mit importierten/übersprungenen Datensätzen und Fehlern). Abbrechen eines laufenden Imports → Status `cancelled`. Wiederholen nach `error`/`timed_out`: UNVERIFIZIERT.
- **Assistent (belegtes Legacy-Muster, CE ≤ 0.x, 2023):** Schrittleiste mit runden Icons (Zahnrad → Wolke/Upload → Liste → Personen → Haken), Link „Cancel import & go back“, Buttons „Back“/„Next“. Schritte: (1) **Configure** – Zugangsdaten/Verbindung („Set up your GitHub import.“, Status „Successfully Connected“); (2) **Quelle/Ziel** – „Select Repository – Select the repository that you want the issues to be imported from.“, „Select Project – Select the project to import the issues to.“, Schalter „Sync Issues – Set whether you want to sync the issues or not.“; (3) **Import Data** – „Import Completed. We have found:“ mit Zählern Issues/States/Modules/Labels/Users (Jira zusätzlich Schalter „Import Epics – Import epics as modules“); (4) **Users** – Schalter „Users – Update, invite or choose not to invite assignee“, Tabelle „Name | Import as…“ mit Optionen **„Invite by email“**, **„Map to existing“** (+ Dropdown „Select user from project“), **„Do not import“** („Ignore“), Kopf „{n} users selected“; (5) **Confirm**. (`IMG/importers/github/{configure,sync,map}.png`, `IMG/importers/jira/{jira-importer-second-step,jira-importer-step-three}.png`). Die aktuelle EE-Assistentenstruktur je Quelle ist nicht belegt (UNVERIFIZIERT, OP-08); die obigen Schritte sind die belegte fachliche Basis.
- **Plan-Abstufung:** Jira- und GitHub-Import ab Free „Without custom props“, ab Pro „With custom props“ (`plans.tsx` Z. 940–960) – d. h. Mapping von Fremd-Custom-Fields auf Plane-Custom-Properties (Work-Item-Types/Properties, P02 §2.12) ist Bezahl-Abstufung; nach ADR-001 immer aktiv. **[Verifikation]** Für Linear, Asana und CSV nennt die Nutzer-Doku „all plans of the Commercial Edition“ (F24, F25, F29); Flatfile nur Cloud (F60).
- **Betrieb:** dedizierter Celery-Worker „for the `celery.importer` queue, so imports run on their own worker“ (`HC/README.md` Z. 1251); `IMPORTERS_QUEUE_NAME` (`HC/templates/config-secrets/silo.yaml`); CPU-intensives Parsing (Confluence `entities.xml`) (`HC/values.yaml` Z. 558–559).

**UI-Hinweise (1:1):** Icons `ImportsOutline/Filled` (Navigation), Status-Badges analog CE-Export-Liste (`apps/web/components/exporter/*` als Stilreferenz für Listenzeilen „Previous exports“), Schrittleiste wie Legacy (Kreise 48 px, aktive Schritte gefüllt `bg-accent-primary`, Linien dazwischen – Maße aus Screenshot geschätzt, UNVERIFIZIERT).

**Datenmodell-Hinweise**

- CE-Altmodell `Importer` (Tabelle `importers`; `service` ∈ {`github`, `jira`}; `status` ∈ {`queued`, `processing`, `completed`, `failed`}; `initiated_by`; `metadata`, `config`, `data`, `imported_data` JSON; `token` → `APIToken`; Projektbezug) und Serializer mit `initiated_by_detail`, `project_detail`, `workspace_detail` (`apps/api/plane/db/models/importer.py`; `apps/api/plane/app/serializers/importer.py`); Typ `IImporterService` (`packages/types/src/importer/index.ts`).
- Ziel: `ImportJob` (`id`, `workspace_id`, `project_id` (Ziel; bei Wiki-Importen null), `source` ∈ {`jira`, `jira_server`, `linear`, `asana`, `clickup`, `notion`, `confluence`, `csv`, `github`}, `status` (13 Werte oben), `config` jsonb (Quelle: Projekt/Space/Repo; Mappings: States, Prioritäten, Typen, Custom Fields → Properties, Nutzer, Epics→Module/Epics), `credentials` (verschlüsselt, nach Abschluss löschen), `stats` jsonb (gefunden/importiert/übersprungen je Entität), `report_asset_id`, `error`, `initiated_by`, `started_at`, `finished_at`, `cancelled_at`); `ImportJobItem`/`ImportLog` (Quelle-ID, Ziel-ID, Ergebnis, Meldung).
- Idempotenz: alle Zielentitäten mit `external_source` + `external_id` (Felder existieren im CE bereits in `issue.py`, `issue_type.py`, `state.py`, `label.py`, `cycle.py`, `module.py`, `page.py`, `project.py`, `intake.py`, `asset.py`, `draft.py`); die CE-Public-API lehnt Duplikate mit gleicher Kombination ab (z. B. `apps/api/plane/api/views/cycle.py` Z. 314–327, `apps/api/plane/api/views/asset.py` Z. 517–571).

**API-Hinweise:** CE-Altrouten (Backend fehlt): `GET /api/workspaces/{slug}/importers/`, `GET /api/workspaces/{slug}/importers/{service}/` (Vorschau, z. B. GitHub `?owner&repo` → `IGithubRepoInfo {issue_count, labels, collaborators[]}`), `POST /api/workspaces/{slug}/projects/importers/{service}/`, `DELETE /api/workspaces/{slug}/importers/{service}/{importerId}/` (`apps/web/services/integrations/{integration,github,jira}.service.ts`); Fetch-Keys `IMPORTER_SERVICES_LIST_{SLUG}`, `JIRA_IMPORTER_DETAIL_…` (`packages/constants/src/fetch-keys.ts` Z. 118–126). Ziel-Vorschlag: `GET|POST /api/workspaces/{slug}/imports/`, `GET /api/workspaces/{slug}/imports/{id}/`, `POST …/{id}/cancel/`, `GET …/{id}/report/`, `POST /api/workspaces/{slug}/imports/{source}/preview/` (UNVERIFIZIERT – Neuentwurf).

**Migrationshinweise (.NET):** Import-Pipeline als `BackgroundService` mit eigener Queue (Aspire-Projekt `worker-importers` oder Teil von `integrations`), Fortschritt per SignalR/Polling; Pull-Clients je Quelle (Jira REST v3/v2, Linear GraphQL, Asana REST, Notion REST, Confluence-Export-ZIP/XML, GitHub REST); Transformation in Domänenmodelle; Push über interne Domänen-Services (nicht über HTTP); Rich-Text-Konvertierung (Jira ADF/Wiki-Markup, Notion-Blocks, Confluence-Storage-Format, Markdown) nach Plane-HTML/Tiptap-JSON. Airgapped: Jira Server/DC und Confluence-Datei-Upload funktionieren ohne Internet; SaaS-Quellen optional.

**Quellen:** `workspace-settings.json`; `integration.json` (`import_status`); `plans.tsx`; `apps/api/plane/db/models/importer.py`; `packages/types/src/importer/*`; `apps/web/services/integrations/*`; `HC/README.md`; `HC/values.yaml`; `IMG/importers/**`.
**Konfidenz:** hoch (Status-Enum, Texte, Plan-Abstufung) / mittel (Assistent, Legacy-basiert) / niedrig (aktuelle EE-UI).

---

#### P09-F22 – Jira-Cloud-Importer (inkl. Custom Properties)

- Matrix: „Import your work items and members from Jira.“ – Free/One „Without custom props“, Pro/Business/Enterprise „With custom props“ (`plans.tsx` Z. 940–949).
- **Belegte Eingaben (CE-Typen, Legacy-Formular):** `IJiraMetadata { cloud_hostname, api_token, project_key, email }` – UI „Jira Personal Access Token“ („Get to know your access token by navigating to Atlassian Settings“), „Jira Project Key“ („If XXX-123 is your issue, then enter XXX“, Platzhalter „LIN“), „Jira Email Address“ („Enter the Email account that you use in Jira account“, `name@company.com`), „Jira Installation or Cloud Host Name“ (`mycompany.atlassian.net`) (`packages/types/src/importer/jira-importer.ts`; `IMG/importers/jira/jira-workspace-setting.png`).
- **Vorschau:** `IJiraResponse { issues, modules, labels, states, users: IJiraResponseUser[] }` mit Jira-Nutzerfeldern `self`, `accountId`, `accountType`, `emailAddress`, `avatarUrls{48x48,24x24,16x16,32x32}`, `displayName`, `active`, `locale`.
- **Optionen:** `IJiraConfig { epics_to_modules: boolean }` („Import Epics – Import epics as modules“); `IJiraData { users: [{username, import: "invite"|"map"|false, email}], invite_users, total_issues, total_labels, total_states, total_modules }`; Formular `IJiraImporterForm { metadata, config, data, project_id }`.
- **Mapping (Ziel, abgeleitet):** Jira-Issues → Work Items (Titel, Beschreibung, Status → State (Status-Kategorien To Do/In Progress/Done → State-Gruppen unstarted/started/completed), Priorität (Highest/High/Medium/Low/Lowest → urgent/high/medium/low/none – Mapping UNVERIFIZIERT), Labels, Assignee/Reporter → Nutzer-Mapping, Kommentare, Anhänge, Sub-Tasks → Sub-Work-Items, Issue-Links → Relationen, Sprints → Cycles (UNVERIFIZIERT), Epics → Module (Legacy-Option) bzw. Epic-Work-Item-Type (aktuelles Plane-Modell, P02 §4.1), Issue-Types → Work Item Types, Custom Fields → Custom Properties (Pro-Abstufung).
- **Konfidenz:** hoch (Eingaben/Typen, Legacy) / niedrig (aktuelles Feld-Mapping).

#### P09-F23 – Jira-Server/Data-Center-Importer

- Belegt durch Silo-Variablen `JIRA_SERVER_ISSUES_PAGE_SIZE` (Default 50, „Page size used when fetching issues from Jira Server during imports“) und `JIRA_SERVER_ISSUES_PARALLEL_PAGES` (Default 1, „Number of Jira Server issue pages fetched in parallel during imports“) (`HC/README.md` Z. 1086–1087; `HC/templates/config-secrets/silo.yaml`). Authentifizierung (Basic/PAT), Base-URL-Feld: UNVERIFIZIERT (Jira-DC-API v2 nutzt PAT als Bearer). **[Verifikation]** Die Importer-Übersicht der Nutzer-Doku führt Jira Cloud und Jira Server als getrennte Importer; Schrittanleitung nicht gefunden (`WEB(V09)` https://docs.plane.so/importers/github).
- **Migration:** Paginierung `startAt`/`maxResults` mit konfigurierbarer Seitengröße und Parallelität übernehmen. Airgapped-relevant.
- **Konfidenz:** mittel (Existenz/Parameter) / niedrig (UI).

#### P09-F24 – Linear-Importer · P09-F25 – Asana-Importer

- Belegt durch „The `silo` service is the integrations engine (ETL, OAuth, webhooks, and sync for GitHub, Jira, Linear, Asana, Slack, etc.)“ (`DD/self-hosting/manage/health-checks.md` Z. 204), Logos `Linear`, `Asana` (`PROPEL/other-products`) und **[Verifikation]** je eine eigene Nutzer-Doku-Seite (`WEB(V09)` https://docs.plane.so/importers/linear , https://docs.plane.so/importers/asana – Suchzusammenfassungen):
  - **Verfügbarkeit (beide):** „available on Plane Cloud and on all plans of the Commercial Edition for self-hosted instances“.
  - **Linear:** Workspace settings → Imports → „Import“ im Abschnitt Linear → **Personal Access Token** eingeben → „Connect Linear“; Rolle: Workspace-Admins. Marketplace-Text: Migration von „projects, issues, and docs“ (`WEB(V09)` https://plane.so/marketplace/linear). Dok. 22 P03-F22 nennt zusätzlich Issues, States, Labels, Prioritäten, Nutzer und ein geführtes State-Mapping (WEB, UNVERIFIZIERT).
  - **Asana:** Personal Access Token → Plane-Zielprojekt sowie Asana-Workspace und -Projekt wählen → **Asana-Sections auf Plane-States** und **Asana-Prioritäten auf Plane-Prioritäten** mappen → Zusammenfassung prüfen → „Confirm“; nach dem Import lassen sich neue oder geänderte Asana-Einträge nachträglich synchronisieren (Mechanismus UNVERIFIZIERT, Zusammenfassung abgeschnitten). Marketplace: „projects, tasks, users, and workflows“.
- Weiterhin **UNVERIFIZIERT:** genaue Feldabbildung und Nutzer-Mapping-Dialog. Vorschlag: Linear (GraphQL): Teams → Projekt, Cycles → Cycles, Projects → Module, Kommentare, Sub-Issues; Asana: Subtasks → Sub-Work-Items, Tags → Labels, Custom Fields → Properties.
- **Konfidenz:** hoch (Existenz, Verfügbarkeit) / mittel (Ablauf) / niedrig (Feld-Mapping).

#### P09-F26 – ClickUp-Importer · P09-F31 – Monday.com-Importer

- **ClickUp – [Verifikation, Korrektur] belegt:** eigene Doku-Seite (`WEB(V09)` https://docs.plane.so/importers/clickup , Suchzusammenfassung): importiert **Projekte, Tasks, Team-Mitglieder, Custom Fields, Anhänge und Kommentare**; Authentifizierung per **ClickUp Personal Access Token**; Auswahl von **Workspace, Space und Folders**; **Prioritäten-Mapping** über Dropdowns; wird der Nutzer-Import übersprungen, bleibt das Feld Assignees leer. Weitere Belege: Dok. 22 P03-F22 („ClickUp (Projekte, Tasks, Teams)“), Changelog 2025-09-01 (Dok. 26 S3), Logo `Clickup`. Plan: „available on Plane Cloud and the Commercial Edition“ (konkreter Plan nicht genannt). Ziel-Mapping Custom Fields → Custom Properties und Folders/Lists → Projekt bzw. Module: UNVERIFIZIERT.
- **Monday.com – weiterhin nicht belegt:** nur Logo `Monday` in `PROPEL/other-products` (das Verzeichnis enthält 41 Logos, darunter Marken ohne Integrationsbezug wie `Dribbble`, `Instagram`, `Facebook`, `Linkedin`, `X`; vollständige Liste F01). Existenz eines Importers ist **UNVERIFIZIERT** → OP-07/OP-08.
- **Konfidenz:** ClickUp mittel (nur Suchzusammenfassung) / Monday niedrig.

#### P09-F27 – Notion-Importer · P09-F28 – Confluence-Importer

- Confluence: Helm-Kommentar „Parsing an import (e.g. a Confluence entities.xml) is CPU-bound; at 500m the batch writes stall long enough for storage to drop the read.“ (`HC/values.yaml` Z. 558–559) ⇒ Import eines **Confluence-Space-Exports (XML, `entities.xml`)** per Datei-Upload, verarbeitet von Silo, Ziel: Pages/Wiki. Schwesterdokument P07: „Notion/Confluence-Importer übernehmen Unterseiten als Nested Pages“ (`26-paid-wissen-pages-wiki.md` Z. 331, `WEB(P07)`); Changelog-Titel „doc imports“ (`WEB(P07)` https://plane.so/changelog/2025-09-01-recurring-items-doc-imports-nested-pages).
- **[Verifikation] Widerspruch zum Confluence-Exportformat:** Die Nutzer-Doku (`WEB(V09)` https://docs.plane.so/importers/confluence) sagt laut Suchzusammenfassung „Only HTML exports from Confluence are supported“: Space als **ZIP (HTML-Export)** exportieren, unter Workspace settings → Imports hochladen; Seiten werden zu **Wiki-Pages** mit erhaltener Unterseiten-Hierarchie. Der Helm-Kommentar nennt dagegen `entities.xml` (Bestandteil des XML-Exports). Für den Nachbau gilt die spezifischere, nutzerseitige Doku (HTML-ZIP); XML-Unterstützung UNVERIFIZIERT.
- Notion: Marketplace-Text „Notion pages and wikis into Plane's Pages“ (`WEB(V09)` Suchzusammenfassung zu https://plane.so/marketplace/integrations); Import-Format (ZIP-Export Markdown/HTML vs. Notion-API) weiterhin UNVERIFIZIERT; eine Schritt-Doku wurde nicht gefunden.
- **Ziel-Mapping (Vorschlag):** Seitenhierarchie → Nested Pages (Wiki/Collections, P07), Anhänge → Assets, Inline-Bilder → Editor-Bilder, interne Links → Page-Links, Datenbanken (Notion) → ggf. Work Items (UNVERIFIZIERT).
- **Konfidenz:** mittel (Confluence-Existenz) / niedrig (Notion, Details).

#### P09-F29 – CSV-Importer für Work Items

- **[Verifikation, Korrektur] belegt** (vorher „nicht belegt“). Nutzer-Doku (`WEB(V09)` https://docs.plane.so/importers/csv , Suchzusammenfassung): „available on Plane Cloud and on all plans of the Commercial Edition for self-hosted instances“. **Importierbare Felder (laut Zusammenfassung):** Title (**Pflicht**), Description, Work Item Type, State, Assignee, Priority, Created by, Start date, Due date, Modules, Cycle, Labels, Created At. **Regeln:** Assignee und Created by müssen **E-Mail-Adressen** sein (keine Usernamen); Description wird als **reiner Text** übernommen (Formatierung, Bilder und Tags landen als Rohtext). Changelog-Titel „Release v3.3.0 – work item CSV imports, wiki reordering“ (`WEB(V09)` https://plane.so/changelog/release-v3-3-0-work-item-csv-imports-wiki-reordering). Spaltenzuordnungs-Dialog und Fehlerbericht: UNVERIFIZIERT.
- **Abgrenzung:** Der separate **Flatfile-Importer** (CSV mit interaktivem Feld-Mapping über den SaaS-Dienst Flatfile) ist nur in Plane Cloud verfügbar (F60). Das CE besitzt nur den **Export** CSV/XLSX/JSON (`packages/constants/src/workspace.ts` `EXPORTERS_LIST`) und die i18n-Texte des **Mitglieder**-CSV-Imports (F32).
- **Ziel:** CSV-Upload mit eigener Spaltenzuordnung in Angular (airgapped, ADR-004; ersetzt Flatfile, vgl. Dok. 22 O17); Validierung je Zeile, Ergebnisbericht; Pflichtfeld Title; Nutzerauflösung per E-Mail.
- **Konfidenz:** mittel (nur Suchzusammenfassung).

#### P09-F30 – GitHub-Importer

- Matrix: „Import your work items and members from GitHub.“ – Free/One „Without custom props“, Pro+ „With custom props“ (`plans.tsx` Z. 950–960); Nutzer-Doku existiert (`WEB(P03)` https://docs.plane.so/importers/github, Inhalt nicht gelesen).
- **Belegte Datenstrukturen (CE-Typen):** `IGithubServiceImportFormData { metadata: {owner, name, repository_id, url}, data: { users: [{username, import: boolean|"invite"|"map", email}] }, config: { sync: boolean }, project_id }`; Vorschau `IGithubRepoInfo { issue_count, labels, collaborators: [{avatar_url, html_url, id, login, url}] }` (`packages/types/src/importer/github-importer.ts`).
- **Legacy-Assistent:** Configure („Set up your GitHub import.“, „Successfully Connected“) → Select Repository / Select Project / „Sync Issues“ → Datenübersicht → Users (Map to existing / Invite by email / Do not import; „Select user from project“) → Confirm; Historie „Import from GitHub to {Projekt} · Completed · {Datum} | Imported by {Name}“ (`IMG/importers/github/*.png`). Kachel-Text Legacy: „GitHub – Import issues from GitHub repositories and sync them.“; Legacy-Hinweis „Relocation Guide – You can now transfer all the issues that you've created in other tracking services. This tool will guide you to relocate the issue to Plane.“ + „Read More“.
- „Sync Issues“ verbindet Import mit dauerhaftem Sync → im aktuellen Produkt über die GitHub-Integration (F04) abgedeckt.
- **Konfidenz:** hoch (Typen, Legacy-UI) / niedrig (aktuelle UI).

#### P09-F32 – Mitglieder-Import per CSV (Workspace und Projekt)

- **Workspace:** Modal „Import Members from CSV“ – „Upload a CSV with columns: Email, Display Name, First Name, Last Name, Role (5, 15, or 20)“; Dropzone „Drop CSV file here“ (aktiv) / „Drag & drop or click to upload“ (inaktiv) / „Only .csv files supported“; Buttons „Cancel“, „Import“, „Try Again“, „Close“, „Done“; Fortschritt „Uploading...“, „Importing...“; Ergebnis „Import Failed“ / „Import Complete“, „Unable to import members due to seat limit restrictions.“ (entfällt, ADR-001), „Successfully added {count} member{plural} to the workspace.“, „No members were imported from the CSV file.“; Statistik „Successful“, „Failed“; „Download errors“; Toasts „Invalid file – Only CSV files are supported.“, „Import failed – Something went wrong.“ (`workspace.members_import.*`).
- **Projekt:** „Upload a CSV with columns: Email and Role (5=Guest, 15=Member, 20=Admin). Users must already be workspace members.“, „Download sample CSV“; Ergebnis „Successfully imported {count} member{plural} to the project.“ / „No new members were imported from the CSV file.“; Statistik „Added“, „Reactivated“, „Already Members“, „Skipped“; „Download skipped details“ (`project.members_import.*`).
- **Regeln (abgeleitet aus Texten):** Rollenwerte 5/15/20 (CE-Rollen-Enum); Projektimport nur für bestehende Workspace-Mitglieder; deaktivierte Projektmitglieder werden reaktiviert; vorhandene zählen als „Already Members“; Fehlerzeilen als CSV herunterladbar.
- **CE-Status [Verifikation, Korrektur]:** Stub/UI-Hülle im CE (vorher „fehlt“) – die Schlüssel `workspace.members_import.*` (24) und `project.members_import.*` (25) liegen im CE-Repo, haben aber keine Referenz im Code (grep `members_import` außerhalb `packages/i18n/src/locales` ohne Treffer); keine Backend-Route.
- **Datenmodell:** kein eigenes Modell nötig (synchroner oder Hintergrund-Job; Ergebnis-CSV als temporäres Asset).
- **API (Vorschlag, UNVERIFIZIERT):** `POST /api/workspaces/{slug}/members/import/` (multipart), `POST /api/workspaces/{slug}/projects/{id}/members/import/`; Antwort `{added, reactivated, already_members, skipped, failed, errors_csv_url}`.
- **Migration:** CsvHelper; Validierung E-Mail/Rolle; Einladungsversand über bestehende Invitation-Logik (CE `workspace_invitation_task.py`).
- **Quellen:** `packages/i18n/src/locales/en/workspace.json`, `project.json`. **Konfidenz:** hoch (UI/Format).

---

#### P09-F60 – Flatfile-Importer (CSV über Flatfile, nur Cloud) [Verifikation ergänzt]

- **Belegt:** eigene Doku-Seite (`WEB(V09)` https://docs.plane.so/importers/flatfile , Suchzusammenfassung): Import von Work Items aus CSV-Dateien über den SaaS-Dienst Flatfile (interaktives Feld-Mapping, Dok. 22 P03-F22); „The Flatfile importer is only available on Plane Cloud“ – Self-hosted-Nutzer sollen den CSV-Importer (F29) verwenden; Kachel in den Imports-Einstellungen mit Badge **„Beta“**. Spaltensatz: UNVERIFIZIERT.
- **Tier:** Cloud-only. **CE-Status:** fehlt.
- **Ziel:** entfällt als eigener Importer (SaaS, nicht airgapped-fähig, ADR-004); die Funktion deckt der CSV-Importer mit eigenem Spalten-Mapping-Dialog ab (F29; Abweichung von ADR-005 dokumentieren, vgl. Dok. 22 O17).
- **Konfidenz:** mittel.

---

### 3.C Plane AI

#### P09-F33 – Plane AI: Dienst „PI“, Workspace-Feature `pi`, Settings-Seite „Plane AI“

**Funktionsbeschreibung**

- **Funktionsumfang laut Hersteller:** „Plane AI brings AI-powered features to your workspace, including natural language chat, duplicate detection, and search across work items, pages, and projects.“ (`DD/self-hosting/govern/plane-ai/configure-plane-ai.md` Z. 9); Dienst-Rollen „chat, embeddings, transcription, LLM proxy“ (`DD/self-hosting/manage/health-checks.md` Abschnitt „Plane AI (pi)“). Bezeichnungen im Produkt: „Plane AI“ (UI), „Pi“ (Feature-Flag, Code), „Plane Intelligence“ (Env-Doku, i18n-Schlüssel `plane-intelligence`).
- **Workspace-Schalter:** Workspace-Feature `pi` (boolean, „Pi.“) neben `project_grouping`, `initiatives`, `teams`, `customers`, `wiki` (`DD/api-reference/workspace-features/overview.md`); Lesen/Ändern über die Workspace-Features-API (P02 §2.17). Fachlicher Toggle → bleibt nach ADR-001 erhalten.
- **Settings-Seite:** Workspace Settings → Features → **„Plane AI“** (Screenshot `IMG/webhooks/create-webhook.webp`, Icon = Plane-AI-Sub-Brand), Texte „Plane AI“ / „See your work get smarter and faster with AI that is natively connected to your work and knowledge base. “ (mit abschließendem Leerzeichen im Original; `workspace_settings.settings.plane-intelligence.{title,heading,description}`). Unterbereiche: belegt sind nur die Leerzustands-Illustrationen `ai-agents`, `ai-skills`, `memory` (`packages/blocks/src/empty-state/assets/asset-types.ts` Z. 38–40, `asset-registry.tsx` Z. 91–92) ⇒ Abschnitte **Agents**, **Skills**, **Memory** (F36–F38; Aufbau UNVERIFIZIERT).
- **Architektur des Originals (Self-hosted):** FastAPI-Dienst `pi-api` (Port 8000, Prefix `/pi`), `pi-worker` und `pi-beat` (Celery), `pi-migrator`; **eigene DB** `PLANE_PI_DATABASE_URL` („must not be shared with the main Plane application database“) plus **Lesezugriff** auf die Haupt-DB `FOLLOWER_POSTGRES_URI` (Read-Replica erlaubt; beide beim Start geprüft); OpenSearch ≥ 2.19 als Such-/Vektorindex; mindestens ein LLM-Key; Verbindung zur API über `PI_BASE_URL` + `PI_BASE_PATH` (`/pi`), internes Geheimnis `PI_INTERNAL_SECRET`; **PI ist OAuth-Client von Plane**: `PLANE_OAUTH_REDIRECT_URI=https://<domain>/pi/api/v1/oauth/callback/`, `PLANE_OAUTH_STATE_EXPIRY_SECONDS` 82800 ⇒ PI handelt mit den Rechten des Nutzers; Zugriff auf den Live-Server (`LIVE_BASE_URL`, `LIVE_SERVER_SECRET_KEY` in `HC/templates/config-secrets/pi-api-env.yaml`; Live-Metrik `serverAgent` in `DD/self-hosting/manage/health-checks.md`) ⇒ KI kann Pages kollaborativ bearbeiten (UNVERIFIZIERT, vgl. P07 §3.29); Health `GET /pi/live/` → `{"alive": true}`, `/pi/ready/`, `/pi/health/` (5-s-Cache), veraltet `/pi/api/v1/health/`, `/pi/api/v2/health/` (`configure-plane-ai.md`; `DD/self-hosting/govern/environment-variables.md` Z. 173–240, 294–330; `HC/values.yaml` Z. 729–825, 1390–1406).
- **CE-Status [Verifikation, Korrektur]:** Stub/UI-Hülle im CE (vorher „teilweise“): vom PI-Dienst, der Settings-Seite und dem Workspace-Feature `pi` existieren im CE nur der Sidebar-Key `pi_chat` (`sidebar-item.tsx` Z. 52), das ungenutzte Menü-Item (`user-menu.tsx` Z. 55–61) und i18n-Texte (grep `is_pi_enabled`, `plane-intelligence` außerhalb `locales` ohne Treffer). Die lauffähige CE-Basis-AI ist eigenständig in F40 (GPT-Assistent) und F45 (LLM-Konfiguration) erfasst. Abweichung zu Dok. 20 PF-82 („teilweise im CE“) dokumentiert; Dok. 22 P03-F12 führt ebenfalls „Stub“.
- **Verfügbarkeit:** Self-hosted seit Commercial v2.4.0 (`WEB(P03)` https://forum.plane.so/t/plane-v2-4-0-plane-ai-now-available-for-self-hosted/53 ; `WEB(P07)` https://plane.so/changelog/release-v-2-4-0-plane-ai-now-available). **[Verifikation] Cloud-Credits:** „included credits are assigned per paid seat“, standardmäßig nicht gepoolt, Overage per Workspace-Admin aktivierbar, gilt nur für Plane Cloud (`WEB(V09)` https://docs.plane.so/ai/plane-ai-credits); Drittquellen nennen 500 (Free) / 1,000 (Pro) / 2,000 (Business) Credits je Seat – die Free-Angabe widerspricht „paid seat“ (UNVERIFIZIERT). Tier bleibt „Pro“.
- **CE-Basis (nicht Gegenstand, aber Ausgangspunkt):** God-Mode-Seite „Artificial Intelligence Settings“ – „AI features for all your workspaces – Configure your AI API credentials so Plane AI features are turned on for all your workspaces.“ mit Feldern „LLM Model“ (Platzhalter `gpt-4o-mini`) und „API key“ (`apps/admin/app/(all)/(dashboard)/ai/{page,form}.tsx`); Instanz-Keys `LLM_API_KEY`, `LLM_PROVIDER` (Default `openai`), `LLM_MODEL`; Provider-Kataloge OpenAI/Anthropic/Gemini (`apps/api/plane/app/views/external/base.py` Z. 25–75; Aufruf erfolgt im CE stets über den OpenAI-Client); Endpunkte `POST /api/workspaces/{slug}/ai-assistant/` und `POST /api/workspaces/{slug}/projects/{project_id}/ai-assistant/` (Body `task`, `prompt`; Antwort `response`, `response_html`; Rollen Admin/Member) (`apps/api/plane/app/urls/external.py`); Flag `has_llm_configured` in `GET /api/instances/` (`apps/api/plane/license/api/views/instance.py` Z. 139). In der Commercial-God-Mode-Navigation ist dieser Bereich als „Artificial intelligence (deprecated) – Configure your OpenAI creds.“ markiert (`22-paid-architektur-selfhosting-dienste.md` §3.12, Screenshot-Auswertung).

**Datenmodell-Hinweise (Ziel):** `WorkspaceFeature.pi` (bool); Instanz-Konfiguration AI (F45); eigenes Schema `ai` in der Haupt-DB statt separater DB (ADR-003 erlaubt Neuentwurf; Lesereplikat optional über Npgsql-Multi-Host/Read-Replica-Connection).
**API-Hinweise:** PI-eigene API unter `/pi/api/v1/…` und `/pi/api/v2/…`. **[Verifikation]** Belegt sind außer Health/OAuth-Callback die Ingress-Sonderregeln `/pi/api/v1/attachments/` (Datei-Uploads, mit Body-Size-Limit) und `/pi/api/v1/chat/stream-answer/` (Chat-Antwort als **SSE**, ohne Buffering) (`HC/templates/ingress-traefik.yaml` Z. 113–133; ebenso Dok. 22 P03-F12); weitere Pfade UNVERIFIZIERT. Ziel: `/api/workspaces/{slug}/ai/...` im Haupt-API-Host oder eigener Aspire-Dienst `ai` hinter YARP mit Prefix `/pi` (Kompatibilität).
**Migrationshinweise:** Python/FastAPI entfällt → .NET-Modul `Plane.AI` mit `Microsoft.Extensions.AI` (`IChatClient`, `IEmbeddingGenerator`), Hintergrundjobs als `BackgroundService`/Quartz.NET; ADR-004: OpenAI-kompatibler lokaler Endpunkt (Ollama/vLLM) muss vollwertig funktionieren.
**Quellen:** wie oben. **Konfidenz:** hoch (Architektur/Konfiguration) / mittel (Settings-Aufbau).

---

#### P09-F34 – Pi-Chat („Plane AI“-Chat)

**Funktionsbeschreibung (UI & Verhalten)**

- **Navigation:** statischer Sidebar-Eintrag mit Key `pi_chat` (immer sichtbar wie Home/Projects/Your work/Stickies/Drafts; `apps/web/components/workspace/sidebar/sidebar-item.tsx` Z. 50–58), Label „Plane AI“ (`navigation.json` `sidebar.pi_chat`, `common.json` `pi_chat`), Route **`/{workspaceSlug}/pi-chat/`**, Zugriff **Admin, Member und Guest**, Icon `PiChatLogo` (`apps/web/components/workspace/sidebar/user-menu.tsx` Z. 55–61 – **[Verifikation]** dort lautet der Key `pi-chat` mit Bindestrich, im Static-Array von `sidebar-item.tsx` Z. 52 dagegen `pi_chat` mit Unterstrich; welche Schreibweise die EE verwendet, ist UNVERIFIZIERT; `packages/blocks/src/icons/sub-brand/pi-chat.tsx`) – im CE ist `SidebarUserMenu` nirgends eingebunden und es gibt keine Route `pi-chat` (`apps/web/app/routes/core.ts`, `apps/web/app/routes/extended.ts`; grep ohne Treffer), der Key `pi_chat` ist in `SidebarItemBase` als „statisch“ (immer sichtbar, nicht anpinnbar) vorgesehen (`sidebar-item.tsx` Z. 50–58), fehlt aber im CE in `WORKSPACE_SIDEBAR_STATIC_NAVIGATION_ITEMS` (nur `home`, `inbox`, `your-work`, `stickies`, `drafts`, `projects`; `packages/constants/src/workspace.ts` Z. 231–273) ⇒ die EE ergänzt dort einen Eintrag `pi_chat` (Label `sidebar.pi_chat`, Pfad `/pi-chat/`; Zugriffsrollen im Ziel wie im ungenutzten `user-menu.tsx`: Admin/Member/Guest). Der AI-Bereich ist ein eigener App-Bereich neben Projekten, Wiki und Settings (`useWorkspacePaths().isAiPath = pathname.includes("/{slug}/pi-chat")`, `apps/web/hooks/use-workspace-paths.ts` Z. 19–21) – d. h. eigene Seitenleiste/Shell (Inhalt UNVERIFIZIERT).
- **Chat:** Natürlichsprachige Fragen über Workspace-Daten (Work Items, Pages, Projekte, Cycles; Suche über Index) (`configure-plane-ai.md` Z. 9, Prerequisites Punkt 2).
- **Modellwahl:** Nutzer wählen aus den Modellen aller konfigurierten Provider: OpenAI **GPT-5.4**, **GPT-5.2**; Anthropic **Claude Sonnet 4.5**, **Claude Sonnet 4.6**; plus ein **Custom LLM** mit Anzeigename `CUSTOM_LLM_NAME` (Default „Custom LLM“ bzw. Helm „GPT-OSS-120B“) und Beschreibung `CUSTOM_LLM_DESCRIPTION` („A self-hosted OpenAI-compatible model“) – „You can provide API keys for both OpenAI and Anthropic, making all models available to users. If you provide only one key, users will only have access to that provider's models.“ (`configure-plane-ai.md` „Supported LLM providers“; `environment-variables.md` Z. 306–312) ⇒ Modell-Auswahlmenü im Chat-Eingabefeld.
- **Spracheingabe:** „Enables speech-to-text in Plane AI chat“ (Groq, `GROQ_API_KEY`) ⇒ Mikrofon-Button (Icons `MicOutline/Filled`, `VoiceOutline/Filled`).
- **Dateianhänge:** „Enables file attachments in Plane AI“ (S3/MinIO) ⇒ Anhang-Button.
- **Weitere belegte UI-Bausteine:** Icons `NewChatOutline/Filled` (neuer Chat, Kategorie `workspace-features`), `AskOutline/Filled`; Onboarding-Checkliste „Try Plane AI chat“ (`tour.json` `item_5`); CE-Ladetext „Pi is generating response“ (`packages/constants/src/ai.ts`). Chat-Verlauf/Threads, Teilen, Feedback, Streaming-Darstellung: UNVERIFIZIERT (OP-09).
- **Rechte:** Chat läuft im Kontext des Nutzers (PI als OAuth-Client, F33) ⇒ nur Daten, die der Nutzer sehen darf; Gäste haben laut Menüdefinition Zugriff.
- **Schreibende Aktionen** (Work Items anlegen/ändern aus dem Chat, „AI work creation“): Changelog-Titel `WEB(P07)` https://plane.so/changelog/2025-10-15-ai-work-creation-inline-comments-filters , https://plane.so/changelog/release-v-2-1-0-text-to-work-items-video-attachments-and-block-links – Umfang UNVERIFIZIERT (F40).

**UI-Hinweise (1:1):** Sub-Brand-Icons `PlaneAi`, `PlaneAiAlt`, `PlaneAiTwo` (`PROPEL/sub-brands`), `PiChatLogo`; AI-Sterne `AiStar1…4Outline/Filled`, `AiStarOne…FourOutline/Filled` (`PROPEL/miscellaneous`). Mention-Farben im Chat-Editor laut Kommentar in `apps/live/src/lib/pdf/colors.ts` Z. 209: „pi-chat-editor mention styles: bg-accent-primary/20 text-accent-primary“ ⇒ eigener Chat-Editor (Tiptap) mit @-Mentions.

**Datenmodell-Hinweise (Ziel):** `AiChat` (`id`, `workspace_id`, `user_id`, `title`, `model_key`, `is_archived`, `created_at`, `updated_at`); `AiMessage` (`chat_id`, `role` ∈ {`user`, `assistant`, `tool`}, `content` (Markdown/HTML), `mentions` jsonb, `attachments` (Asset-IDs), `tool_calls` jsonb, `citations` jsonb (referenzierte Work Items/Pages), `model_key`, `input_tokens`, `output_tokens`, `created_at`); `AiAttachment` → bestehendes `FileAsset`-Modell.
**API-Hinweise (Original, belegt):** `/pi/api/v1/chat/stream-answer/` (SSE), `/pi/api/v1/attachments/` (F33). **API-Hinweise (Ziel, Vorschlag):** `GET|POST /api/workspaces/{slug}/ai/chats/`, `GET|PATCH|DELETE …/chats/{id}/`, `POST …/chats/{id}/messages/` (Antwort als **Server-Sent Events**-Stream), `GET /api/workspaces/{slug}/ai/models/`, `POST /api/workspaces/{slug}/ai/transcriptions/` (Audio → Text).
**Migrationshinweise:** Tool-Calling über `Microsoft.Extensions.AI` (`AIFunction`) auf Domänen-Services (Suche, Work-Item-CRUD mit Nutzerrechten); STT airgapped: lokales Whisper (`Whisper.net`) oder OpenAI-kompatibler `/audio/transcriptions`-Endpunkt; Angular: Chat-Feature-Modul mit `fetch`-Streaming.
**Quellen:** s. o. **Konfidenz:** hoch (Navigation, Provider/Modelle, Voice/Anhänge) / niedrig (Chat-Detail-UI).

---

#### P09-F35 – Plane AI: Connectors (MCP)

- Produkt-Tour „mcp_connectors“: **„Stop tab-switching. Connect your world.“ – „Link GitHub, Slack to track PRs and summarize chats directly in Plane AI.“** (`tour.json` `product_tour.mcp_connectors.step_zero.{title,description}`) ⇒ In Plane AI lassen sich externe Werkzeuge (mind. GitHub, Slack) als **MCP-Connectoren** verbinden; die KI liest dann PRs bzw. Slack-Verläufe und fasst sie zusammen. **[Verifikation]** Nutzer-Doku (`WEB(V09)` https://docs.plane.so/ai/mcp-connectors , Suchzusammenfassung): Connectoren werden unter **Workspace Settings → Integrations → Connectors** eingerichtet und im Plane-AI-Chat genutzt; **Authentifizierung je Nutzer** (jedes Mitglied verbindet sein eigenes Konto); genannte Beispiele **GitHub, Sentry, Granola** (Propel-Logo `granola` vorhanden). Changelog-Titel „Release v2.5.0 – new widgets, MCP connectors, Plane AI for self-hosted“ (`WEB(V09)` https://plane.so/changelog/release-v2-5-0-new-widgets-mcp-connectors-plane-ai-for-self-hosted). Ob der separate Settings-Eintrag „Connections“ (Screenshot) dieselbe Verwaltung ist, bleibt UNVERIFIZIERT (OP-16).
- **Datenmodell (Vorschlag):** `AiConnector` (`workspace_id`, `user_id` (Authentifizierung je Nutzer laut Doku), `provider`, `transport` (`http`|`sse`), `server_url`, verschlüsselte OAuth-/Token-Daten, `enabled_tools[]`, `created_by`).
- **Migration:** MCP-**Client** über das offizielle C#-SDK `ModelContextProtocol`; Airgapped: nur interne MCP-Server; Wiederverwendung der Integrations-Verbindungen (F02, F09), wo vorhanden.
- **Konfidenz:** hoch (Existenz) / mittel (Ort, Authentifizierung je Nutzer) / niedrig (Details).

#### P09-F36 – Plane AI: Skills · P09-F37 – Memory · P09-F38 – eingebaute Agents

| Feature | Belege | Funktion (belegt bzw. UNVERIFIZIERT) |
|---|---|---|
| Skills | Illustration `ai-skills`; Changelog-Titel „Skills in Plane AI“ (`WEB(P06)` https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more , https://plane.so/changelog/2026-07-31-skills-plane-ai-richer-pages-audit-logs) | **[Verifikation] belegt** (`WEB(V09)` https://docs.plane.so/ai/ai-skills , Suchzusammenfassung): gespeicherte, wiederverwendbare Anweisungen („reusable instructions“), im Plane-AI-Chat per **Slash-Command** ausgeführt; drei Geltungsbereiche **personal**, **workspace** (von Workspace-Admins angelegt, für alle Mitglieder) und **system** (eingebaut, weder editier- noch löschbar); verfügbar, sobald Plane AI im Workspace aktiv ist; auf Mobile als Auswahl statt freiem Prompt (Mobile-Changelog v2.4.0). Verwaltungsort (Settings → Plane AI → Skills) UNVERIFIZIERT |
| Memory | Illustration `memory`; Icons `MemoryOutline/Filled`; Changelog-Titel „AI memory“ (`WEB(P07)` https://plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more , https://plane.so/changelog/2026-09-15-ai-memory-workspace-labels-ms-office-edits) | UNVERIFIZIERT (Suche ohne Doku-Treffer): dauerhaft gespeicherte Fakten/Präferenzen (je Nutzer und/oder Workspace), die in Chats einfließen; Liste mit Ansehen/Löschen. Der Agents-Blog nennt „memory that carries context between runs“ für Agents (F38) |
| Agents (eingebaut) | Illustration `ai-agents`; Icons `AgentOutline/Filled`, `AgentAltOutline/Filled`; OAuth-Scope-Beschreibung „Access to agents, and all agent related entities“ (`workspace_settings.settings.applications.scope_description.agents`) | **[Verifikation] belegt laut Blog** (`WEB(V09)` https://plane.so/blog/agents-are-now-live-in-plane , Suchzusammenfassung): Agents (Beta) mit **Playbook**, **Skills**, über **MCP** angebundenen Tools, **Scope** (Projekte, in denen der Agent handeln darf), **Triggern** (Zuweisung, Erwähnung, Änderung eines Work Items, Zeitplan) und **Memory** zwischen Runs; Lebenszyklus „from created to completed or failed“ (vgl. F50); Admins legen Agents an und konfigurieren sie, Mitglieder erwähnen bzw. weisen zu. Konfigurations-UI UNVERIFIZIERT |

- **Datenmodell (Vorschlag):** `AiSkill` (`workspace_id`, `name`, `description`, `instructions`, `is_enabled`, `created_by`); `AiMemory` (`workspace_id`, `user_id` nullable, `content`, `source_chat_id`, `created_at`); `AiAgent` → als OAuth-App/Agent-Installation (F47/F50) mit internem Handler.
- **Konfidenz:** Skills mittel, eingebaute Agents mittel (Suchzusammenfassungen), Memory niedrig. → OP-09.

---

#### P09-F39 – AI-Assistent im Editor (Ask Pi, Selection-Aktionen, AI-Block, Page-Proposals)

- Vollständig spezifiziert im Schwesterdokument **P07** (`26-paid-wissen-pages-wiki.md` §3.27 Selection-Aktionen „Paraphrase, Simplify, Elaborate, Summarize, Get title“ + Ton; §3.28 **AI-Block** `/ai` mit Typen „Summarize Page“, „Custom Prompt“ und Aktionen „Discard“, „Generate“/„Generating“, „Rewrite“/„Rewriting“, „Use this“, „Refine“, Stale-Indikator; §3.29 Prompt/Agent mit blockweisen Vorschlägen accept/reject). **Tier [Verifikation, Abgleich Dok. 26 / P07.paid.json]:** Selection-Aktionen und Seitenzusammenfassung **Pro** (P07-27); AI-Block `/ai` und Prompt/Agent-Proposals **Business** (P07-28/P07-29; die Doku-/Guide-Angabe „AI Blocks … available on Business“ ist neuer als der Blog „Pro+“ und gilt). Abgrenzung: Der Page-Block „HTML artifact“ (Dok. 26 P07-37, Upload von `.html`-Dateien) ist nicht identisch mit den AI-Artifacts (F44).
- **CE-Spuren:** Editor-Extension-Schalter `"ai"` in `TExtensions` (`packages/editor/src/types/extensions.ts` Z. 7), im CE überall deaktiviert (`apps/web/hooks/use-editor-flagging.ts`: `disabled: ["ai", "collaboration-cursor"]` für `document`, `liteText`, `richText`); `TAIHandler` (`packages/editor/src/types/ai.ts`); Menü `EditorAIMenu` mit einziger Aufgabe `ASK_ANYTHING` „Ask Pi“ (Icon `AiStar1Outline`), Tönen `default` (casual 5/formal 5), `professional` „💼 Professional“ (0/10), `casual` „😃 Casual“ (10/0), Breite 210 px → 700 px bei aktiver Aufgabe (`apps/web/components/pages/editor/ai/menu.tsx`); Service `POST /api/workspaces/{slug}/rephrase-grammar/` mit `TTaskPayload {casual_score?, formal_score?, task, text_input}` → Antwort `{response}` – **Route fehlt im CE-Backend** (`apps/web/services/ai.service.ts`). ⇒ **CE-Status [Verifikation, Korrektur]:** Stub/UI-Hülle im CE (vorher „teilweise“), da ohne Backend-Route und mit deaktivierter Extension nicht lauffähig; konsistent mit Dok. 26 P07-27.
- **Ziel:** Endpunkt `rephrase-grammar` (bzw. neutral `ai/editor-tasks`) mit Aufgaben `ASK_ANYTHING`, `PARAPHRASE`, `SIMPLIFY`, `ELABORATE`, `SUMMARIZE`, `GET_TITLE` (Enum-Werte außer `ASK_ANYTHING` UNVERIFIZIERT) und Ton-Scores.
- **Konfidenz:** siehe P07.

#### P09-F40 – AI-Work-Creation (Text → Work Items) und Beschreibungs-Generierung

- **CE-Basis (bereits vorhanden):** Im Work-Item-Modal bei konfiguriertem LLM Button **„I'm feeling lucky“** (generiert eine Beschreibung aus dem Titel; während der Generierung „Generating response“) und Button **„AI“** öffnet `GptAssistantPopover` („Use this response“, Hinweis „By using this feature, you consent to sharing the message with a 3rd party service.“, „Close“) (`apps/web/components/issues/issue-modal/components/description-editor.tsx` Z. 247–290; `apps/web/components/core/modals/gpt-assistant-popover.tsx` Z. 177–295).
- **EE-Erweiterung (nur Titel belegt):** „AI work creation“ (Okt. 2025) und „Text to work items“ (v2.1.0) (`WEB(P07)` W9, W37) ⇒ aus Freitext (z. B. Meeting-Notizen, Page-Abschnitt, Chat) mehrere Work Items mit Properties erzeugen. Ablauf/UI **UNVERIFIZIERT** (Vorschlag: KI schlägt eine Liste vor → Nutzer prüft/editiert → Massenanlage). → OP-09.
- **Konfidenz:** hoch (CE-Basis) / niedrig (EE-Erweiterung).

#### P09-F41 – AI-Suche / Semantic Search (Embeddings, Vektorsuche)

**Funktionsbeschreibung**

- „Configuring the embedding model is optional. Without it, Plane AI uses **BM25 keyword search**. With it, you get **vector similarity search, duplicate issue detection, and semantic retrieval over work items and pages**.“ (`DD/self-hosting/govern/plane-ai/configure-embedding-model.md` Z. 9).
- **Unterstützte Embedding-Modelle (vollständig):**

| Provider | Modell | Dimension |
|---|---|---|
| Cohere | `cohere/embed-v4.0` | 1536 |
| Cohere | `cohere/embed-english-v3.0` | 1024 |
| Cohere | `cohere/embed-english-v2.0` | 4096 |
| OpenAI | `openai/text-embedding-ada-002` | 1536 |
| OpenAI | `openai/text-embedding-3-small` | 1536 |
| OpenAI | `openai/text-embedding-3-large` | 3072 |
| AWS Bedrock | `bedrock/amazon.titan-embed-text-v1` | 1536 |
| AWS Bedrock | `bedrock/amazon.titan-embed-text-v2` | 1024 |
| AWS Bedrock | `bedrock/cohere.embed-english-v3` | 1024 |
| AWS Bedrock | `bedrock/cohere.embed-multilingual-v3` | 1024 |

- Dimension (`OPENSEARCH_EMBEDDING_DIMENSION`, Default 1536) muss zum Modell passen; Modellwechsel mit anderer Dimension erfordert Index-Neuaufbau und Re-Vektorisierung (`manage_search_index index rebuild --force`, `manage_search_index --background --vectorize document index --force`); neue Inhalte werden automatisch indiziert; periodische Synchronisation `CELERY_VECTOR_SYNC_ENABLED`/`_INTERVAL` (3 s), `CELERY_DOCS_SYNC_ENABLED`/`_INTERVAL` (86 400 s) (`configure-embedding-model.md`; `environment-variables.md` Z. 313–330).
- **Nutzung in der UI:** Retrieval für den Chat (F34) und Duplikaterkennung (F42) belegt; ob die globale Suche (Cmd/Ctrl+K, Power-K) semantische Treffer zeigt, ist UNVERIFIZIERT (Icon `AiFilterOutline` deutet auf KI-gestützte Filter hin, F43).

**Datenmodell-Hinweise (Ziel, ADR-004 pgvector):** Tabelle `ai.embeddings` (`id`, `workspace_id`, `project_id` nullable, `entity_type` ∈ {`work_item`, `page`, `comment`, `cycle`, `module`, `project`}, `entity_id`, `chunk_index`, `content` (normalisierter Text), `content_hash`, `embedding vector(<dim>)`, `model_key`, `updated_at`); HNSW-Index (`vector_cosine_ops`); Volltext-Spalte `tsvector` (oder Wiederverwendung des Such-Indexes aus P03) für hybride Suche (BM25-ähnliches `ts_rank_cd` + Vektor, Fusion per Reciprocal Rank Fusion); Rechtefilter über Projektmitgliedschaft im SQL.
**Migrationshinweise:** `Pgvector.EntityFrameworkCore` (`UseVector()`, `HasPostgresExtension("vector")`); Embedding-Erzeugung über `IEmbeddingGenerator<string, Embedding<float>>` (OpenAI-kompatibel; lokal z. B. Ollama) – Dimension als Instanz-Einstellung, Änderung → Hintergrund-Reindex; Change-Tracking über Outbox-Events (P06) statt 3-s-Polling.
**Quellen:** `configure-embedding-model.md`; `configure-plane-ai.md`; `environment-variables.md`; `HC/values.yaml` (`embedding_model`, `celery.vector_sync_*`). **Konfidenz:** hoch (Konfiguration) / mittel (UI-Nutzung).

#### P09-F42 – Duplicate Detection

- Belegt als Plane-AI-Funktion („duplicate detection“, „duplicate issue detection“), benötigt das Embedding-Modell (F41) (`configure-plane-ai.md` Z. 9; `configure-embedding-model.md` Z. 9).
- **CE-Stubs [Verifikation, Korrektur; vgl. Dok. 20 PF-104]:** Typen `TDuplicateIssuePayload {title, workspace_id, issue_id?, project_id?, description_stripped?}`, `TDeDupeIssue {id, type_id, project_id, sequence_id, name, priority, state_id, created_by}`, `TDuplicateIssueResponse {dupes: TDeDupeIssue[]}` (`packages/types/src/de-dupe.ts`); No-op-Hook `useDebouncedDuplicateIssues(workspaceSlug, workspaceId, projectId, {name, description_html, issueId})` → `{duplicateIssues: []}` (`apps/web/hooks/use-debounced-duplicate-issues.tsx`); Modal-State `isDuplicateModalOpen`/`handleDuplicateIssueModal` im Work-Item-Modal (`apps/web/components/issues/issue-modal/base.tsx` Z. 68, 382, 405) und im Intake-Create-Modal (`apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–46); Texte „Duplicate work item found“ / „Duplicate work items found“ (`common.json` `duplicate_issue_found`, `duplicate_issues_found`, im CE ohne Referenz). ⇒ **UI-Ort belegt:** entprellte Duplikatsuche beim Erstellen von Work Items und Intake-Requests (Titel/Beschreibung); ein Fundhinweis öffnet ein Duplikat-Modal; der Endpunkt ist im CE nicht benannt. **CE-Status:** Stub/UI-Hülle im CE (vorher „fehlt“). Schwellwert und Aktionen im Modal: UNVERIFIZIERT (OP-09). Ergänzender Vorschlag: Beim Anlegen eines Work Items bzw. in der Intake-Triage werden (debounced, ab Titel-Eingabe) semantisch ähnliche Work Items desselben Projekts angezeigt; Aktion „Mark as duplicate“ setzt die vorhandene Relation „Duplicate of“ (`work-item.json` `issue.relation.duplicate`; Intake `inbox_issue.actions.mark_as_duplicate`, Status `inbox_issue.status.duplicate`; Icon `DuplicateOfOutline`). Schwellwert konfigurierbar.
- **Datenmodell:** keine neue Entität (nutzt `ai.embeddings` + `IssueRelation(relation_type="duplicate")`).
- **Konfidenz:** hoch (Existenz, Schnittstellen, UI-Ort) / niedrig (Ranking, Modal-Aktionen).

#### P09-F43 – AI-Aktionen aus dem Icon-Inventar (Summary, Catch-up, Copy as prompt, AI-Filter)

| Icon (Propel) | Kategorie | Wahrscheinliche Funktion (UNVERIFIZIERT) |
|---|---|---|
| `AiSummaryOutline/Filled` | `actions` | KI-Zusammenfassung (Work Item, Kommentarverlauf, Page – Page-Summary über AI-Block belegt, P07); **[Verifikation]** die Produktseite Work Items nennt eine Sofort-Zusammenfassung („comments, activity, and linked items condensed into a single status update“, `WEB(V09)` https://plane.so/issues , Suchzusammenfassung) |
| `CatchupOutline/Filled` | `actions` | **[Verifikation] belegt für Mobile:** „Catch Up“-Widget (iOS/Android) zeigt Elemente, die Aufmerksamkeit erfordern; in der App markiert Wischen nach rechts ein Update als gelesen, nach links bleibt es ungelesen (Mobile-Changelog v2.4.0, `WEB(V09)` https://plane.so/changelog/release-v2-4-0-ai-autopilot-skills-catch-up-widget). Web-Variante UNVERIFIZIERT |
| `CopyAsPromptOutline/Filled` | `actions` | Work Item/Page als LLM-Prompt (Markdown mit Kontext) in die Zwischenablage kopieren |
| `AiFilterOutline/Filled` | `actions` | Filter in natürlicher Sprache → PQL/Filterobjekt; vgl. „Text to PQL“ (Dok. 24 P05-35, Enterprise Grid, dort spezifiziert) |
| `AskOutline/Filled` | `actions` | „Ask Plane AI“ aus Kontext (z. B. Work Item) |
| `NewChatOutline/Filled` | `workspace-features` | Neuer Chat (F34) |
| `MicOutline/Filled`, `VoiceOutline/Filled` | `miscellaneous` | Spracheingabe (F34, belegt) |
| `AutopilotGoOutline/Filled` | (Index) | Autopilot-Modus von Plane AI (F61, belegt für Mobile) |

- Quelle: `PROPEL/index.d.ts`. **CE-Status [Verifikation, Korrektur]:** fehlt (vorher „Stub“) – die Icons liegen nur im externen npm-Paket `@makeplane/propel`, nicht im CE-Code; Behandlung wie die übrigen Nur-Icon-Funde (F19, F26 vorher, F31; Dok. 20 PF-105). **Konfidenz:** hoch (Icons existieren) / mittel (Catch Up, Summary) / niedrig (Copy as prompt, AI-Filter, Ask). → OP-09.

#### P09-F44 – Applets / Artifacts (AI-generierte HTML-Dashboards)

- **Definition (Erstquelle `GH:` Q19 `artifacts/overview.md`):** „a versioned HTML document stored against a workspace“ – Speicher- und Hosting-Schicht für **von Plane Intelligence erzeugte Dashboards**; Name, optionaler Projektbezug, Daten-Modus und eine nur wachsende Kette von HTML-Versionen. Ausdrücklich „POC surface“ (kein List/Delete/ältere Version lesen/Unpublish).
- **Zugriff:** Plan-Feature **„Applets“** (sonst `402`) und **Workspace-Admin/Owner** (sonst `403`), auch für Lesezugriffe; Scopes `workspaces.artifacts:read|write` (`GH:` `authentication.md`).
- **Endpunkte (API v2):** `POST /api/v2/workspaces/{slug}/artifacts/` (anlegen inkl. erster HTML-Version) · `GET /api/v2/workspaces/{slug}/artifacts/{artifact_id}/` · `PATCH /api/v2/workspaces/{slug}/artifacts/{artifact_id}/update/` (neue Version anhängen) · `POST /api/v2/workspaces/{slug}/artifacts/{artifact_id}/publish/` (öffentlichen Anker erzeugen; Anker folgt immer der aktuellen Version).
- **Felder:** `id` (uuid), `name` (≤255, Default „Untitled dashboard“), `description` (≤2000, nur Detail), `html` (aktuelle Version, nur Detail), `current_version` (int, ab 1, +1 je Anhang), `data_mode` ∈ {`snapshot` (Daten zum Erzeugungszeitpunkt eingefroren, Default), `live` (Daten beim Ansehen neu gelesen)}, `is_published` (bool), `anchor` (string|null). Fehler nach problem+json, außer fehlendem `html`/ungültigem `data_mode` → nacktes `{"detail": "…"}`.
- **UI:** nicht belegt (vermutlich Erzeugung im Pi-Chat, Anzeige als Dashboard-Seite/öffentlicher Link) – UNVERIFIZIERT (OP-09).
- **Datenmodell (Ziel):** `Artifact` (`id`, `workspace_id`, `project_id`, `name`, `description`, `data_mode`, `current_version`, `is_published`, `anchor` unique, `created_by`), `ArtifactVersion` (`artifact_id`, `version`, `html`, `created_at`). Sicherheit: HTML nur in sandboxed `iframe` (eigene Origin/`sandbox`-Attribut, CSP) ausliefern; `live`-Modus braucht eine Datenschnittstelle für das Artefakt (UNVERIFIZIERT).
- **[Verifikation]** Definition, Plan-Feature „Applets“ (`402 payment_required`), Rolle Admin/Owner (`403`, auch für Lesezugriffe), die vier Endpunkte, Felder, `data_mode` und der Hinweis „POC surface … no list endpoint, no delete“ (kein Unpublish) wurden per direktem Abruf von https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/artifacts/overview.md am 22.10.2026 bestätigt.
- **Konfidenz:** hoch (API) / niedrig (UI).

#### P09-F45 – LLM-Provider- und Embedding-Konfiguration

- **Original (Commercial, Env/Helm):** `OPENAI_API_KEY`/`OPENAI_BASE_URL`, `CLAUDE_API_KEY`/`CLAUDE_BASE_URL`, `GROQ_API_KEY`/`GROQ_BASE_URL` (Speech-to-Text), `COHERE_API_KEY`/`COHERE_BASE_URL`; **Custom LLM** (genau eines zusätzlich): `CUSTOM_LLM_ENABLED`, `CUSTOM_LLM_PROVIDER` ∈ {`openai` (Default, OpenAI-kompatibel: Ollama, Groq, Cerebras, LiteLLM …), `bedrock`}, `CUSTOM_LLM_MODEL_KEY`, `CUSTOM_LLM_BASE_URL`, `CUSTOM_LLM_API_KEY` („use any non-empty string if no key is required“), `CUSTOM_LLM_NAME`, `CUSTOM_LLM_DESCRIPTION`, `CUSTOM_LLM_MAX_TOKENS` (Doku 64 000 bzw. Env-Default 128 000), `CUSTOM_LLM_AWS_REGION`; Bedrock-Varianten: statische Keys, `AWS_BEARER_TOKEN_BEDROCK` (Helm `api_key`), Inference Profile (`BEDROCK_INFERENCE_PROFILE_ARN`/`_ID`, IRSA/Pod Identity); Hinweis „The custom model should have at least 1 trillion parameters for all Plane AI features to work reliably.“; Embeddings: `EMBEDDING_MODEL`, `OPENSEARCH_ML_MODEL_ID`, `OPENSEARCH_EMBEDDING_DIMENSION`, `BR_AWS_ACCESS_KEY_ID`, `BR_AWS_SECRET_ACCESS_KEY`, `BR_AWS_REGION`, `BR_AWS_SESSION_TOKEN`; Betrieb: `FASTAPI_APP_WORKERS`, `PI_*_REPLICAS` (`configure-plane-ai.md`; `environment-variables.md` Z. 197–240, 294–330; `HC/values.yaml` Z. 747–798).
- **Ziel (ADR-004, ADR-001):** God-Mode-Seite „Plane AI“ (ersetzt CE-Seite „Artificial intelligence“, gleicher Navigationsplatz) mit: Provider-Liste (Typ `openai_compatible` | `anthropic` | `azure_openai` | `bedrock`; Base-URL; API-Key; Modelle mit Anzeigename/Beschreibung/Max-Tokens; Standardmodell), Embedding-Provider + Modell + Dimension, STT-Provider (optional), Token-Budget (F46). Werte verschlüsselt in der DB (Data Protection), Env-Variablen als Initialwerte. **Mindestanforderung:** voll funktionsfähig mit einem lokalen OpenAI-kompatiblen Endpunkt (Ollama/vLLM) inkl. lokalem Embedding-Modell.
- **Konfidenz:** hoch.

#### P09-F46 – AI-Usage, Credits, Token-Budget

- **Cloud:** AI-Credits je Plan („1,000 AI credits per seat per month“ ab Pro, `WEB(P01)` https://plane.so/pro ; Credit- und Usage-Doku `WEB(P03)` https://docs.plane.so/ai/plane-ai-credits , https://docs.plane.so/ai/ai-usage). → **entfällt** (ADR-001).
- **Commercial-Schalter:** `AI_USAGE_ENFORCEMENT_ENABLED` (Helm-Default `true`), `AI_USAGE_AGENT_MAX_TOKENS_BUDGET` (Default leer) – gesetzt in API und PI (`HC/values.yaml` Z. 1401–1402 [Verifikation: Zeilen korrigiert]; `HC/templates/config-secrets/{app-env,pi-api-env}.yaml`). Bedeutung (abgeleitet): maximales Token-Budget je Agent-Lauf; Durchsetzung an/aus.
- **Ziel:** optionale Instanz-Limits (Tokens je Nutzer/Monat, je Agent-Lauf), Nutzungsübersicht im God Mode (Tokens je Workspace/Nutzer/Modell) – keine Credits, keine Upsell-UI. **Konfidenz:** mittel.

#### P09-F61 – Plane AI: Autopilot-Modus [Verifikation ergänzt]

- **Belegt:** Mobile-Changelog v2.4.0 (31.07.2026): „Plane AI on mobile can run trusted workflows without asking for confirmation after each step“, Rückschalten auf manuelle Prüfung möglich (`WEB(V09)` https://plane.so/changelog/release-v2-4-0-ai-autopilot-skills-catch-up-widget , Suchzusammenfassung); Icons `AutopilotGoOutline/Filled` (`PROPEL/index.d.ts`). Ob der Modus auch im Web-Chat existiert: UNVERIFIZIERT.
- **Verhalten (abgeleitet, UNVERIFIZIERT):** Schreibende Tool-Aufrufe von Plane AI (Work Items anlegen/ändern, F40) werden standardmäßig je Schritt bestätigt; im Autopilot-Modus ohne Einzelbestätigung ausgeführt. Ebene des Schalters (je Chat oder je Nutzer) offen.
- **Ziel:** Bestätigungspflicht als Standard für schreibende `AIFunction`-Aufrufe; Autopilot als nutzerseitig umschaltbare Option; Nachvollziehbarkeit über das Activity-Log (Aktor = Nutzer, Quelle = Plane AI).
- **Tier:** wie F33. **CE-Status:** fehlt (nur Propel-Icons). **Konfidenz:** mittel (Existenz) / niedrig (Verhalten).

---

### 3.D Plattform

#### P09-F47 – OAuth-App-Plattform („Build your own app“, Consent, Tokens, Scopes, Installationen)

**Funktionsbeschreibung (UI & Verhalten)**

- **Status/Tier:** „Plane apps are currently in **Beta**“ (`DD/dev-tools/build-plane-app/overview.md`); „OAuth application registration is available on Plane Cloud and Plane Commercial Edition; Plane Community Edition does not include it“ (`DD/dev-tools/mcp-server-self-host.md` Voraussetzungen; ebenso `DD/dev-tools/mcp-server.md` Schluss-Tipp).
- **Einstieg:** Workspace Settings → Integrations → **„Build your own“** (`https://app.plane.so/<workspace>/settings/integrations/`) (`create-oauth-application.md`); i18n-Bereich „Applications“ mit Reitern/Listen **„Installed apps“**, **„All apps“**, **„Internal apps“**, **„Your apps“**, **„Third-party apps“**, Badge „Internal“, Aktionen „Connect“/„Connected“/„Disconnect“, „Install“/„Installed“, „Configure“, „Go to app“, „Build your own app“, „Edit app details“ (`workspace_settings.settings.applications.*`, vollständig Anhang B). Zuständig: Workspace-Admins (Installation; „This app can only be installed after a workspace admin installs it. Contact your workspace admin to proceed.“ / „Request to install“).
- **App anlegen/bearbeiten („Create app“ / „Update app“) – Felder und Validierungen (vollständig):**

| Feld (Label) | Beschreibung/Platzhalter (wörtlich) | Validierung (wörtlich) |
|---|---|---|
| App Name | – | „App name is required“ |
| App slug | eindeutig | „App slug is required“; „Slug already exists“ |
| Short Description | – | „App short description is required“ |
| Long Description | „Write a long description for marketplace. Press ‘/’ for commands.“ (Rich-Text-Editor) | „App description is required“ |
| Logo | „Upload Logo“ | – |
| Website | „Link to your app's website.“ / `https://example.com` | „Invalid website“ |
| App Maker | „The person or organization creating the app.“ | „Maker name is required“ |
| Setup URL | „Users will be redirected to this URL when they install the app.“ / `https://example.com/setup` | „Setup URL is required“; „Invalid setup URL“ |
| Configuration URL | – | „Configuration URL is required“; „Invalid configuration URL“ |
| Webhook URL | „This is where we will send webhook events and updates from the workspaces where your app is installed.“ / `https://example.com/webhook` | „Webhook URL is required“; „Invalid webhook URL“ |
| Webhook Secret | „Secret used to verify incoming webhook requests.“ / „Enter a random secret key“ | – |
| Redirect URIs (space separated) | „Users will be redirected to this path after they have authenticated with Plane.“ bzw. „Enter space seperated URIs where the app will redirect to after the user e.g https://example.com https://example.com/“ | „Redirect URIs are required“; „Invalid redirect URIs“ |
| Authorized Javascript Origins | „Enter space seperated origins where the app will be allowed to make requests e.g app.com example.com“ | „Authorized Javascript Origins are required“; „Invalid authorized Javascript Origins“ |
| Connection Type | „Choose if your app should be installed once for the workspace or let every user connect their own account“ | – (Werte UNVERIFIZIERT: Workspace-Installation vs. Nutzer-Verbindung) |
| Categories | „Select the categories that best describe the app“ / „Select app categories“ | „Categories are required“; „Invalid categories“ |
| Supported Plans | „Select the workspace plans that can install this application. Leave empty to allow all plans.“ | **entfällt (ADR-001)** |
| Privacy Policy URL | – | „Privacy Policy URL is required“; „Invalid privacy policy URL“ |
| Terms of Service URL | – | „Terms of Service URL is required“; „Invalid terms of service URL“ |
| Support URL | – | „Support URL is required“; „Invalid support URL“ |
| Video URL | – | „Video URL is required“; „Invalid video URL“ |
| Contact Email | – | „Contact Email is required“; „Invalid contact email“ |
| Attachments (Screenshots) | „Upload Attachments“, „Drop images here“, „Click to upload images“, „Uploading {count} Image…“, „Uploading...“, „Upload & Save“ | „Invalid file or exceeds size limit ({size} MB)“ |
| Enable App Mentions | „When this is enabled, Users can mention or assign Work Items to this application.“ | – (F49) |
| Scopes & Permissions | „Scopes“, „Select Scopes“, „{count} selected“, Spalten „Read“/„Write“, „Read-only access to“/„Write access to“; Beschreibungen `projects` „Access to projects, and all project related entities“, `wiki`, `workspaces`, `stickies`, `profile` „Access to user profile information“, `agents`, `assets`; Warnung „Global scopes are expiring soon. Use granular scopes instead. For example, use project:read instead of a global read.“ | – |

- **Nach dem Anlegen:** „App created successfully – Use the credentials to install the app in a Plane workspace“; Anzeige „Application ID“, „Client ID“, „Client Secret“ mit Kopier-Toasts („Application ID copied to clipboard“, „Client ID copied to clipboard“, „Client Secret copied to clipboard“); Abschnitt „Client ID and Secret – Copy and save this secret key in Pages. You can't see this key again after you hit Close.“ + „You can download a CSV with the key from here.“ + Button „Export as CSV“; Fehler „Failed to create application“. **Secret rotieren:** „Regenerate client secret – Regenerate the client secret. If you regenerate the secret, you can copy the key or download it to a CSV file right after.“ → Bestätigung „Sure you want to regenerate the client secret? – App using this secret will stop working. You will need to update the secret in the app.“ („Cancel“/„Regenerate“) → „App credentials successfully re-generated – Replace the client secret everywhere it's used. The previous secret is no longer valid.“; Hinweis „You have made this app available to use with a Plane workspace – Connect a Plane workspace to start using it“.
- **Consent-Screen:** „{app} is requesting access to your Plane workspace and profile.“; „Choose a workspace to connect the app with“; „Connect {app} to your workspace {workspace}“ „with the permissions“; Abschnitt „Workspace permissions – Workspace permissions are used to grant access to the workspace.“ mit „{app} would like“ + Liste („Read-only access to your workspace“, „Write access to your workspace“ bzw. granulare Scopes); Abschnitt „User permissions – User permissions are used to grant access to the user's profile.“ mit „{app} can also request a user's permission to the following resources. These permissions will be requested and authorized of and by a user only.“ („Read-only access to your user profile“, „Write access to your user profile“); „By accepting, you“ – „Grant the app access to your Plane data wherever you can use the app in or outside Plane“ – „Agree to {app}'s Privacy Policy and Terms Of Use“; Warnung für ungeprüfte Apps „This app hasn't been reviewed or approved by Plane yet. – Make sure you trust this app before connecting it to your workspace.“; Buttons „Accept“/„Accepting...“.
- **Token-Flows (`DD/dev-tools/build-plane-app/choose-token-flow.md`):**
  - **Bot-Token (Client Credentials, empfohlen für Agents/Automationen):** `GET /auth/o/authorize-app/?client_id&response_type=code&redirect_uri&scope=<space-separated>` → Consent → Redirect mit `app_installation_id` (+ `code`, ungenutzt) → `POST /auth/o/token/` (`application/x-www-form-urlencoded`, `Authorization: Basic base64(client_id:client_secret)`, `grant_type=client_credentials&app_installation_id=…&scope=…`) → `{"access_token":"pln_bot_…","token_type":"Bearer","expires_in":86400,"scope":"…"}`; Erneuerung durch denselben Aufruf; Installationsdetails `GET /auth/o/app-installation/?id=<id>` (Bearer Bot-Token) → `[{"id","workspace","workspace_detail":{"name","slug"},"app_bot":"<bot-user-uuid>","status":"installed"}]`.
  - **User-Token (Authorization Code):** wie oben plus `state` (CSRF) → `POST /auth/o/token/` mit `grant_type=authorization_code&code&client_id&client_secret&redirect_uri` → `{"access_token":"pln_…","refresh_token":"pln_refresh_…","token_type":"Bearer","expires_in":86400,"scope":"…"}`; Refresh `grant_type=refresh_token&refresh_token&client_id&client_secret`.
  - API-Aufruf: `Authorization: Bearer <token>` gegen `/api/v1/…` (bzw. `/api/v2/…`). API v2 dokumentiert zusätzlich `/auth/o/authorize/` als Authorization-URL und `X-Api-Key` für persönliche Tokens (`GH:` `authentication.md`).
- **App-Webhooks:** Ereignisse der Workspaces, in denen die App installiert ist, gehen an die Webhook-URL der App; Header `X-Plane-Delivery`, `X-Plane-Event`, `X-Plane-Signature` (HMAC-SHA256 über Rohbody mit Webhook-Secret der App); Beispiel-Payload `{event, action, webhook_id, workspace_id, data, activity:{actor:{id, display_name}}}` (`DD/dev-tools/build-plane-app/webhooks.md`). Event-Katalog = Webhooks v2 (F51) plus Agent-Ereignisse (F50).
- **Scopes:** vollständige Liste Anhang E.

**Datenmodell-Hinweise (Ziel):** `OAuthApplication` (`id`, `owner_workspace_id`, `name`, `slug` unique, `short_description`, `description_html`, `logo_asset_id`, `website`, `company_name` („App Maker“), `contact_email`, `privacy_policy_url`, `terms_of_service_url`, `support_url`, `video_url`, `setup_url`, `configuration_url`, `webhook_url`, `webhook_secret` (verschlüsselt), `redirect_uris[]`, `allowed_origins[]`, `connection_type`, `categories[]`, `attachment_asset_ids[]`, `scopes[]`, `is_mentionable`, `is_internal`, `is_published`, `is_verified`, `client_id` unique, `client_secret_hash`, `created_by`); `AppInstallation` (`id`, `application_id`, `workspace_id`, `installed_by`, `status` ∈ {`installed`, `uninstalled`, …}, `bot_user_id`, `granted_scopes[]`, `created_at`); Grants/Tokens (OpenIddict-Tabellen) mit Präfixen `pln_bot_`, `pln_`, `pln_refresh_`.
**API-Hinweise (intern, Vorschlag):** `GET|POST /api/workspaces/{slug}/applications/`, `GET|PATCH|DELETE …/{id}/`, `POST …/{id}/regenerate-secret/`, `GET /api/workspaces/{slug}/app-installations/`, `DELETE …/{id}/` (UNVERIFIZIERT – Neuentwurf; öffentliche OAuth-Endpunkte oben sind belegt und **identisch** zu übernehmen).
**Migrationshinweise:** OpenIddict (Authorization-Code + PKCE, Refresh, Client-Credentials mit Custom-Parameter `app_installation_id` → Bot-Identität der Installation); Scope-Prüfung als ASP.NET-Policies je Endpunkt („global `read`/`write` oder passender Fein-Scope“, `GH:` `authentication.md`); Consent-Seite als Angular-Route außerhalb der Workspace-Shell.
**Quellen:** `DD/dev-tools/build-plane-app/*.md`; `workspace-settings.json`; `GH:` Q19. **Konfidenz:** hoch (Flows, Felder, Texte) / mittel (Seitenstruktur).

---

#### P09-F48 – App-Marketplace

- Belegt: Marketplace-Felder der App (Kategorien, Langbeschreibung „for marketplace“, Screenshots, Video, Privacy/Terms/Support-URL, Kontakt), Review-Status („This app hasn't been reviewed or approved by Plane yet.“), Plan-Filter „Supported Plans“ (`workspace_settings.settings.applications.*`); API-Ingress-Route **`/marketplace/`** → API-Dienst (`HC/templates/ingress-nginx.yaml` Z. 92–94); öffentliche Marketplace-Seite z. B. `WEB(P07)` https://plane.so/marketplace/drawio ; Management-Command `reset_marketplace_app_secrets` (F01).
- **[Verifikation]** Der Marketplace startete im Oktober 2025 (`WEB(V09)` https://plane.so/blog/introducing-the-plane-marketplace); laut Suchzusammenfassungen gelistete Einträge: GitHub, GitHub Enterprise Server, GitLab, GitLab Enterprise, Slack, Sentry, draw.io, VS Code MCP, Claude, Raycast sowie Importer Linear, ClickUp, Notion, Jira, Asana (`WEB(V09)` https://plane.so/marketplace/integrations; Liste nicht als vollständig belegt).
- **Ziel:** instanzlokaler App-Katalog („All apps“) ohne Hersteller-Review; „verified/approved“-Kennzeichen setzt der Instanz-Admin (Vorschlag); Plan-Filter entfällt; vorinstallierte „Internal apps“ = eingebaute Integrationen (GitHub, Slack, …) und Plane AI.
- **Konfidenz:** mittel.

#### P09-F49 – App-Mentions / Bot-User

- „Enable App Mentions – When this is enabled, Users can mention or assign Work Items to this application.“ (`applications.enable_app_mentions*`); bei Installation erstellt Plane „a **bot user** for your agent in that workspace“, Bot-ID in den Installationsdetails (`app_bot`); Agents „appear in the mention picker alongside regular workspace members“, können „assigned or delegated work items“ werden; „Agents installed in your workspace do not count as billable users.“ (`DD/dev-tools/agents/{overview,building-an-agent}.md`).
- **CE-Basis:** `User.is_bot`, `User.bot_type` (einziger Wert `WORKSPACE_SEED`) (`apps/api/plane/db/models/user.py` Z. 52–53, 115–116); UI zeigt Bots als „{first_name} Bot“ (`apps/web/components/modules/links/list-item.tsx` Z. 104, `apps/web/components/issues/issue-detail/links/link-detail.tsx` Z. 118) bzw. mit `first_name` (`workspace-notifications/sidebar/notification-card/content.tsx` Z. 177, `comments/card/display.tsx` Z. 67); Mitgliederlisten filtern Bots aus (`apps/web/store/member/workspace/workspace-member.store.ts` Z. 136, 147; viele API-Abfragen `member__is_bot=False`).
- **Ziel:** neuer `bot_type` (z. B. `APP_BOT` – Wert UNVERIFIZIERT); Mention-Picker und Assignee-Dropdown schließen Bots erwähnbarer Apps **ein** (Sonderfall zur CE-Regel „Bots ausfiltern“); Seat-Zählung entfällt ohnehin (ADR-001).
- **Konfidenz:** hoch.

#### P09-F50 – Agents-Plattform (Agent Runs, Activities, Signals)

**Funktionsbeschreibung**

- **Status:** Beta (`DD/dev-tools/agents/*.md`). Agent = OAuth-App mit „Enable App Mentions“ **und** Agent-Run-Scopes (`agents.runs:read|write`, `agents.run_activities:read|write`).
- **Ablauf:** Nutzer @-erwähnt den Agenten in einem **Work-Item-Kommentar** → Plane legt **Agent Run** (`status=created`) und eine **Activity** (`type=prompt`) an → Webhook an die App → App sendet Activities zurück (`thought`, `action` = ephemer; `response`, `elicitation` = erzeugen Kommentar-Antworten) → Plane aktualisiert den Run-Status. Antwortet der Nutzer im Thread und es gibt einen aktiven Run, wird die Antwort als neue `prompt`-Activity angehängt und erneut ein Webhook gesendet (Mehrrunden-Dialog).
- **Run-Status (vollständig):** `created`, `in_progress`, `awaiting` (wartet auf Nutzer; durch `elicitation`), `completed`, `stopping` (Stop angefordert), `stopped`, `failed` (durch `error`), `stale` („not been updated in 5 minutes“). Run-Typ: `comment_thread`.
- **Activity-Typen:** `prompt` (nur Nutzer/Plane), `thought`, `action` (`{action, parameters: Record<string,string>}`, optional Ergebnis in `parameters.result`, Details in `content_metadata`), `response`, `elicitation`, `error` (alle Text-Inhalte `{type, body}` Markdown). Ephemer automatisch: `thought`, `action`, `error` („displayed temporarily in the UI and replaced when the next activity arrives“). **Widerspruch in der Doku:** `error` ist als ephemer gelistet, soll aber „a comment“ erzeugen und den Run auf `failed` setzen → OP-10.
- **Signals:** `continue` (Default), `stop` (Nutzer stoppt; Webhook mit Prompt „Stop“ und `signal=stop`; Agent bestätigt mit `response` → `stopped`), `auth_request` (`signal_metadata.url` **muss `https://`** sein; optional `provider`, `scopes`), `select` (`signal_metadata.options: [{id, label, description?}]`, `allow_multiple`). Fehler-Metadaten z. B. `{error_code, retryable, retry_after}`.
- **Webhooks an die App:** `agent_run_create` – `{"action":"created","agent_run":{id, agent_user, issue, project, workspace, status:"created", type:"comment_thread", started_at},"agent_user_id","app_client_id","issue_id","project_id","workspace_id","comment_id","type":"agent_run"}`; `agent_run_user_prompt` – `{"action":"prompted","agent_run_activity":{id, agent_run, type:"prompt", content:{type:"prompt", body}, ephemeral:false, signal, actor, workspace},"agent_run":{…,status:"in_progress"},"agent_user_id","app_client_id","comment_id","issue_id","project_id","workspace_id","type":"agent_run_activity"}`.
- **Empfehlungen an Agent-Bauer (Plattform muss sie unterstützen):** sofortiger `thought` (gegen `stale`), Heartbeat-Thoughts bei langen Aufgaben (z. B. jede Minute), Webhook binnen Sekunden mit 200 beantworten (`DD/dev-tools/agents/best-practices.md`).
- **UI (aus Doku abgeleitet):** Agent erscheint im Mention-Picker; Run-Verlauf im Kommentar-Thread; ephemere Activities als vorübergehende Statuszeile („Analyzing your request…“ → Tool-Aufruf → Antwort); Stop-Möglichkeit; Auswahl-Optionen bei `select`; Link-Button bei `auth_request`; optional `external_link` zum Dashboard des Agenten. Genaue Gestaltung UNVERIFIZIERT (OP-02).

**API-Hinweise (Erstquelle SDK `GH:` Q20, Basis `/api/v1`, Header `X-Api-Key` oder `Authorization: Bearer`):**

| Methode | Pfad | Zweck | Body/Antwort |
|---|---|---|---|
| POST | `/api/v1/workspaces/{slug}/runs/` | Agent Run anlegen | `CreateAgentRunRequest {agent_slug (Pflicht), issue?, project?, comment?, source_comment?, external_link?, type?}` → `AgentRun` |
| GET | `/api/v1/workspaces/{slug}/runs/{run_id}/` | Run lesen | `AgentRun` |
| GET | `/api/v1/workspaces/{slug}/runs/{run_id}/activities/` | Activities (paginiert `per_page`, `cursor`) | `PaginatedResponse<AgentRunActivity>` |
| GET | `/api/v1/workspaces/{slug}/runs/{run_id}/activities/{activity_id}/` | Activity lesen | `AgentRunActivity` |
| POST | `/api/v1/workspaces/{slug}/runs/{run_id}/activities/` | Activity anlegen | `CreateAgentRunActivityRequest {type ∈ {action, elicitation, error, response, thought}, content, content_metadata?, signal?, signal_metadata?, project?}` |

`AgentRun`: `id`, `agent_user`, `comment?`, `source_comment?`, `creator`, `stopped_at?`, `stopped_by?`, `started_at`, `ended_at?`, `external_link?`, `issue?`, `workspace`, `project?`, `status`, `error_metadata?`, `type` (+ BaseModel-Felder). `AgentRunActivity`: `agent_run`, `content`, `content_metadata?`, `ephemeral`, `signal`, `signal_metadata?`, `comment?`, `actor?`, `type`, `project?`, `workspace` (`GH:` `src/models/AgentRun.ts`).

**Datenmodell (Ziel):** `AgentRun` und `AgentRunActivity` wie oben (Enums als Strings); `AgentRun.comment_id` = Thread-Wurzel, `source_comment_id` = auslösender Kommentar; Stale-Job (5 min ohne Aktivität).
**Betrieb im Original:** eigener Consumer `agent-consumer` an Queue `plane.agent` (Prefetch 10) (`HC/values.yaml` Z. 687–709, 1379–1381; `HC/templates/config-secrets/agent-consumer.yaml`).
**Migration:** Kommentar-Mention-Erkennung (bestehender Mention-Parser) → Run-Erzeugung im selben Transaktionsrahmen (Outbox) → Webhook-Zustellung über die Webhook-Infrastruktur (F51) mit App-Secret; Live-Updates der ephemeren Activities per SignalR/WebSocket an den Work-Item-Detail-Client.
**Quellen:** `DD/dev-tools/agents/*.md`; `GH:` Q20; `HC/`. **Konfidenz:** hoch (Modelle, Endpunkte, Status) / mittel (UI).

---

#### P09-F51 – Webhooks v2 (Erweiterungen gegenüber CE v1)

**CE-Basis (v1, vorhanden):** Modell `Webhook` (`url` ≤1024, nur http/https, nicht localhost/127.0.0.1; `is_active`; `secret_key` `plane_wh_<uuid hex>`; Bool-Scopes `project`, `issue`, `module`, `cycle`, `issue_comment`; `is_internal`; `version` „v1“), `WebhookLog`, `ProjectWebhook` (`apps/api/plane/db/models/webhook.py`); Formular „Send me everything“/„Select individual events“ mit Projects/Cycles/Work items/Modules/Work item comments (`apps/web/components/web-hooks/form/individual-event-options.tsx`); Secret-CSV-Download (`create-webhook-modal.tsx` Z. 79–80); Endpunkte `workspaces/<slug>/webhooks/`, `…/<pk>/`, `…/<pk>/regenerate/`, `workspaces/<slug>/webhook-logs/<webhook_id>/` (`apps/api/plane/app/urls/webhook.py`); Versand mit Headern `Content-Type`, `User-Agent: Autopilot`, `X-Plane-Delivery`, `X-Plane-Event`, `X-Plane-Signature`, Payload `{event, action, webhook_id, workspace_id, workspace_slug, data, activity}`, 30 s Timeout, SSRF-Schutz, Retry `retry_backoff=600`, `max_retries=5`, Jitter, danach Deaktivierung + E-Mail an Ersteller; abgelehnte URL → Log 400 ohne Retry (`apps/api/plane/bgtasks/webhook_task.py` Z. 233–388).

**Erweiterungen der Commercial Edition (belegt):**

| Bereich | v2-Verhalten | Quelle |
|---|---|---|
| Formular | Pflichtfeld **„Webhook title“** („Give title for the webhook“), „Payload URL“ (`https://example.com/post`), Frage „Which events would do you like to trigger this webhook for?“, Block **„V1 scopes (deprecated)“** (die fünf CE-Scopes) und Block **„V2 scopes“** mit Gruppen-Checkbox je Entität und Unter-Checkboxen je Aktion („Created“, „Updated“, …); Abschnitt **„Advanced configurations“** mit „Work item v2 filters“; Buttons „Create webhook“ / „Update webhook“ | `IMG/webhooks/create-webhook.webp`; `DD/dev-tools/intro-webhooks.md` |
| Events (vollständig, 39) | `project.{created,updated,archived,deleted}`, `cycle.{created,updated,archived,deleted}`, `module.{created,updated,archived,deleted}`, `milestone.{created,updated,deleted}`, `page.{created,updated,archived,deleted}`, `page.comment.{created,updated,deleted}`, `workitem.{created,updated,archived,deleted}`, `workitem.comment.{created,updated,deleted}`, `workitem.link.{created,updated,deleted}`, `workitem.vote.{created,deleted}`, `workitem.attachment.{created,updated,deleted}`, `workitem.relation.{created,deleted}`, `workitem.dependency.{created,deleted}`, `workitem.page_link.{created,deleted}` | `intro-webhooks.md` „Event reference“ |
| Filter (nur Work-Item-Events) | Modi **Basic** (visuelle Auswahl) und **PQL** (Text), verlustfrei umschaltbar; Felder `type_id`, `state_group` (`backlog`·`unstarted`·`started`·`completed`·`cancelled`), `assignee_id`, `label_id`, `project_id`, `priority` (`none`·`low`·`medium`·`high`·`urgent`), `start_date`, `target_date`; Syntax `priority = "urgent"`, `priority in ["urgent","high"]`; Auswertung zum Zustellzeitpunkt, **bei Auswertungsfehler wird nicht zugestellt** | `intro-webhooks.md` „Filtering work item events“ |
| Payload v2 | `{version:"v2", delivery_id (neu je Versuch, = X-Plane-Delivery), event_id (stabil über Retries → Dedup), entity_id, entity_type (z. B. issue, cycle, issue_comment, issue_link), event, webhook_id, workspace_id, data (bei delete {}), previous_attributes (update: alte Werte geänderter Felder; delete: voller Datensatz; sonst {})}` | `intro-webhooks.md` „Payload structure“ |
| Header | wie v1; reservierte, nicht überschreibbare Header: `host`, `content-length`, `content-type`, `user-agent`, `x-plane-delivery`, `x-plane-event`, `x-plane-signature` ⇒ **benutzerdefinierte Header** sind konfigurierbar (UI UNVERIFIZIERT) | `intro-webhooks.md` „Request headers“ |
| Content-Type | `application/json` oder `application/x-www-form-urlencoded` (API v2 `content_type`) | `GH:` `webhooks/create-webhook.md` |
| Verwaltung | ⋯-Menü je Zeile: „Edit“, „Disable webhook“/„Enable webhook“ (Ereignisse während Deaktivierung werden **nicht** nachgeliefert), „Delete webhook“; Secret im Edit-Formular per Auge-Icon anzeigen, kopieren, „Re-generate key“ (alter Schlüssel sofort ungültig; neuer als CSV-Download); v1-Webhooks in der Liste mit Tag **„(deprecated)“**, keine In-Place-Migration | `intro-webhooks.md` „Managing webhooks“ |
| Zustellung | 2xx = Erfolg; Retry exponentiell (~10 min Basis, Jitter), nach **5** Fehlversuchen automatische Deaktivierung + E-Mail an Ersteller; **4xx werden nicht wiederholt**; kein manueller Retry | `intro-webhooks.md` „Delivery and monitoring“ |
| Delivery-Ansicht | Klick auf Webhook → Kennzahlen „Total deliveries“, „Successful“, „Failed“, „Success rate“; Log-Spalten „Events“, „Status“ (Successful/Failed), „Response time“ (ms), „Event time“ | `intro-webhooks.md` „How to read delivery logs“ |
| API v2 | `GET`/`POST /api/v2/workspaces/{slug}/webhooks/`, `GET`/`PATCH`/`DELETE …/{pk}/`, `POST …/{pk}/regenerate/`; Felder `content_type`, `created_at`, `created_by_id`, `id`, `is_active`, `name` (≤255), `scopes` (string[]), `url`, `version` (≤10, z. B. `1.4.0`); Scope `webhooks:read`/`webhooks:write`; Logs `GET /api/v2/workspaces/{slug}/webhook-logs/{webhook_id}/` und `…/{pk}/` mit `created_at`, `duration_ms`, `error_message`, `event_type`, `id`, `request_body`, `request_headers`, `request_method`, `response_body`, `response_headers`, `response_status`, `retry_count`, `status_text`, `webhook_id`; Fehlercodes 400 `invalid_request`, 401 `unauthorized`, 402 `payment_required`, 403 `forbidden`, 404 `not_found`, 406 `not_acceptable`, 409 `conflict`, 413 `payload_too_large`, 415 `unsupported_media_type`, 429 `rate_limited` | `GH:` Q19 |
| Rechte | nur Workspace-Owner/-Admins; Webhooks wirken workspaceweit („There is no per-project webhook configuration.“) | `intro-webhooks.md` |

- **Doku-Fehler:** Beispiel-Payloads `workitem.updated`/`workitem.link.updated` zeigen `"event": "WebhookScope.ScopeChoices.WORK_ITEM_UPDATED"` und Werte `"None"` als String – offensichtlicher Bug der Doku; Ziel sendet `workitem.updated` und JSON-`null` (OP-11).
- **Datenmodell (Ziel):** `Webhook` erweitert um `name`, `version` (`v1`|`v2`), `scopes text[]` (Dot-Events), `filter_pql`, `filter_basic` jsonb (Rückübersetzung Basic↔PQL), `content_type`, `custom_headers` jsonb; `WebhookDelivery` (`event_id`, `delivery_id`, `duration_ms`, `status_text`, `error_message` zusätzlich zu CE-Log-Feldern); Ereignisquelle Outbox (P06) → Queue `plane.webhook` (`HC/values.yaml` `webhook_consumer`).
- **Konfidenz:** hoch.

#### P09-F52 – Workspace-Access-Tokens

- Workspace Settings → Developer → **„Access Tokens“** – „Generate secure API tokens to integrate your data with external systems and applications.“; Buttons „Add access token“, „Create token“, „Generate token“/„Generating“; Ablauf „Never expires“; Löschen „Delete access token – Any application using this token will no longer have the access to Plane data. This action cannot be undone.“ („Success! – The token has been successfully deleted“ / „Error! – The token could not be deleted“); Leerzustände „No Access tokens yet – Generate secure API tokens to connect your workspace with external systems and applications.“ (CTA „Add access token“) und „No access tokens created – Plane APIs can be used to integrate your data in Plane with any external system. Create a token to get started.“ (`workspace_settings.settings.api_tokens.*`, `settings_empty_state.workspace_tokens.*`, `workspace_settings.empty_state.api_tokens.*`); Hinweis beim Erstellen (CE-Text, wiederverwendet) „Copy and save this secret key in Plane Pages. You can't see this key after you hit Close. A CSV file containing the key has been downloaded.“ (`workspace_settings.copy_key`).
- **Rolle:** „Use a workspace access token with the **minimum role** needed for automations.“ (`DD/dev-tools/mcp-server.md` Security) ⇒ Token trägt eine Workspace-Rolle; Plane Compose unterscheidet Auth-Typ `pat` und `workspace` („a workspace-scoped token“) (`DD/dev-tools/plane-compose.md` „Authenticate“).
- **CE-Basis:** persönliche Tokens unter `/settings/profile/api-tokens/` („Personal Access Tokens“), Modell `APIToken` mit bereits vorhandenem `workspace`-FK und `user_type` (0 Human/1 Bot), Token-Präfix `plane_api_` (`apps/api/plane/db/models/api.py`; `apps/api/plane/app/urls/api.py`).
- **CE-Status [Verifikation, Korrektur]:** teilweise im CE (vorher „Stub“): der Token-Kern ist lauffähig vorhanden (CRUD `users/api-tokens/` in `apps/api/plane/app/urls/api.py`, Authentifizierung per `X-Api-Key` in `apps/api/plane/api/middleware/api_authentication.py`, Lösch-Dialog mit den Texten `workspace_settings.settings.api_tokens.delete.*` in `apps/web/components/api-token/delete-token-modal.tsx`); die Route `:workspaceSlug/settings/api-tokens` leitet im CE auf die Profil-Tokens um (`apps/web/app/routes/core.ts` Z. 381–383). Es fehlen Workspace-Bindung, Rolle, Workspace-Settings-Seite. Abweichung zu Dok. 20 PF-62 („fehlt“) dokumentiert. API v2 führt Workspace-Tokens als eigene Rate-Limit-Klasse neben API-Keys, OAuth-, Service- und External-Tokens (Dok. 21, `V2/errors.md`).
- **Ziel:** `APIToken` mit `workspace_id` + eigenem Bot-User + `role` (5/15/20) + optional `expires_at`; Header `X-Api-Key`.
- **Konfidenz:** hoch (Texte) / mittel (Rollenmodell).

#### P09-F53 – MCP-Server

- **Belegter Funktionsumfang:** Server „sits between your client and Plane's REST API, then acts as the signed-in user“; **28 Tools, 183 Aktionen** (eine Tool je Ressource, Parameter `action`; `get_pql_reference` ohne Aktion), MCP-Annotationen `readOnlyHint`/`destructiveHint`; Plan-Gates für `work_log`, `workitem_type`, `workitem_property` und einige `project`-Features (Fehler nennt das Feature) (`DD/dev-tools/mcp-server.md`, `mcp-server-tools.md`; Inventar Anhang D). Open Source (MIT, `github.com/makeplane/plane-mcp-server`).
- **Transporte/Endpunkte:** Streamable HTTP mit OAuth `…/http/mcp`; PAT `…/http/api-key/mcp` mit Headern `Authorization: Bearer <PAT>` und `x-workspace-slug`; lokal `uvx plane-mcp-server stdio` mit `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_BASE_URL`; SSE (deprecated) `…/sse`. OAuth bindet die Verbindung an den beim Consent gewählten Workspace und fordert `read`+`write`; Token-Validierung via `/api/v1/users/me/`; Token-Ablage Redis/Valkey (sonst In-Memory).
- **Tier:** OAuth-Transport benötigt OAuth-App-Registrierung → nur Cloud/Commercial; **CE nur stdio + PAT** (`DD/dev-tools/mcp-server-self-host.md`).
- **Self-hosted-Betrieb (Commercial-Helm):** `services.mcp_server` (Image `makeplane/plane-mcp-server:v0.3.2`, `path_prefix` `/mcp`, OAuth-App-Pflicht; Redirect-URIs `https://<domain>/mcp/http/auth/callback` und `https://<domain>/mcp/auth/callback`), Ingress `/mcp/`, `/.well-known/oauth-protected-resource/mcp`, `/.well-known/oauth-authorization-server/mcp` (`HC/values.yaml` Z. 844–870; `HC/README.md` Z. 1433–1435; `HC/templates/ingress-nginx.yaml` Z. 125–150). Env (vollständig): `APP_RELEASE_VERSION`, `PLANE_BASE_URL`, `PLANE_INTERNAL_BASE_URL`, `PLANE_OAUTH_PROVIDER_CLIENT_ID`, `PLANE_OAUTH_PROVIDER_CLIENT_SECRET`, `PLANE_OAUTH_PROVIDER_BASE_URL`, `PLANE_OAUTH_PROVIDER_ENABLE_CIMD`, `PLANE_OAUTH_ALLOWED_REDIRECT_URIS`, `MCP_PATH_PREFIX`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_SSL`, `ELASTICACHE_SECRET_ARN`, `AWS_REGION`, `REDIS_AUTH_TOKEN_KEY`, `LOG_USER_INFO`; eingebaute Redirect-Allowlist: `http://localhost:*`, `http://localhost:*/*`, `http://127.0.0.1:*`, `http://127.0.0.1:*/*`, `cursor://anysphere.cursor-mcp/oauth/*`, `https://www.cursor.com/*`, `https://vscode.dev/redirect`, `https://insiders.vscode.dev/redirect`, `https://antigravity.google/oauth-callback`, `https://claude.ai/*`, `https://chatgpt.com/connector/oauth/*`, `https://chatgpt.com/connector_platform_oauth_redirect` (`DD/dev-tools/mcp-server-self-host.md`). Logs: JSON mit Toolname, Dauer, Status, opaker User-ID, Workspace-Slug; Anzeigename nur bei `LOG_USER_INFO=true`.
- **Ziel (.NET):** MCP-Server mit dem offiziellen C#-SDK (`ModelContextProtocol.AspNetCore`) als Aspire-Dienst `mcp` unter `/mcp`, gleiche Tool-/Aktionsnamen und Parameter (Kompatibilität zu Client-Konfigurationen), OAuth gegen den eigenen OpenIddict-Server (F47), PAT-Transport, kein SSE nötig (deprecated; optional). Ein stdio-Pendant kann als `dotnet tool` angeboten werden (optional).
- **Konfidenz:** hoch.

#### P09-F54 – Plane Runner

- **Detailspezifikation in P06** (`25-paid-workflows-automation-templates.md` F19, §„F19 – Plane Runner“): Skripte (JS/TS) in isolierter Sandbox, Typen Automation / Workflow Transition / Cron Trigger, `async function main(...)`, Variablen, Functions (`getSiblings`, `addComment`, `addLabel`, `postToSlack`, `httpRequest`), Plane-SDK im Skript, Domain-Allowlist für HTTP, Limits 10 s / Init 5 s / 128 MB, Test ohne Speichern; Health `GET /api/workspaces/{slug}/runnerctl/health/` → `{"is_available": bool}`; Plan **Enterprise Grid**.
- **Belege hier:** i18n „Plane Runner“ / „Scripts“ / „New Script“ / „Automate your workflows with custom scripts and automation rules.“ (`workspace_settings.settings.runners.*`), Automationsaktion „Run Script“/„Run script“ (`automation.json` `automations.action.handler_name.run_script`, `run_script_block.title`); Illustrationen `runner-functions`, `runner-scripts`, `script` (`packages/blocks/src/empty-state/assets/asset-types.ts` Z. 25, 35–36); Icons `ScriptsOutline/Filled` (`project-features`), `FunctionOutline/Filled`, `VariableOutline/Filled`, `SandboxOutline/Filled` (`miscellaneous`); Helm `services.runner` (Image `makeplane/node-runner-commercial`, Port 3000, `EXECUTION_TIMEOUT_MS` 10000, `INIT_TIMEOUT_MS` 5000, `ISOLATE_MEMORY_MB` 128, `API_BASE_URL`, `CONTROL_SERVICE_BASE_URL`, `RUNNER_HMAC_SECRET_KEY`) (`HC/values.yaml` Z. 826–842, 1383–1388; `HC/templates/config-secrets/runner-env.yaml`); Health `node-runner` `/health` intern (`DD/self-hosting/manage/health-checks.md` Z. 145).
- **ADR-002:** Node-Isolates entfallen → eingebettete JS-Engine in .NET (Jint mit Zeit-/Speicher-/Rekursionslimit oder ClearScript V8); TypeScript-Transpilation ohne Node offen (P06 O9).

#### P09-F55 – Plane Compose

- **Was:** CLI „project as code“ (`pipx install plane-compose`, PyPI `plane-compose`), definiert Projekte, Schema und Work Items in YAML, synchronisiert bidirektional über die API; Konfigurationsablage `~/.config/plane-compose/` (`config.json`, `plane.log`) (`DD/dev-tools/plane-compose.md`).
- **Befehle (vollständig):** `plane init`, `plane auth login|logout|list-connections|connect-workspace|disconnect-workspace`, `plane schema validate|push|import|diff`, `plane push` (`--dry-run`, `--schema-only`, `--work-only`, `--all`, `--filter`, `--workspace`, `--resume`, `--force`, `--no-conflict-check`, `--exit-code`), `plane pull` (`--merge`, `--force`, `--all`), `plane clone`, `plane diff`, `plane validate`, `plane status` (`--all`), `plane upgrade` (`--template`, `--dry-run`), `plane state show|reset|clear-items|remove`, `plane ws clone|pull|push|diff|upgrade`, `plane ws state show|reset|clear|remove`, `plane rate stats|reset`; globale Optionen `--version/-V`, `--verbose/-v`, `--debug`; Exit-Codes `0` keine Änderung, `1` Fehler, `2` Änderungen angewendet.
- **Dateien:** `plane.yaml` (`type`, `workspace`, `connection`, `project.{key ≤10 Großbuchstaben, name, uuid, description, network public|private, timezone}`, `defaults.{type, workflow}`, `template`), `workspace.yaml` (`workspace`, `connection`, `workspace_features`, `members[]`), `schema/{types,states,workflows,labels,features,members,workitem_templates,page_templates}.yaml`, Workspace `schema/workitem_types.yaml` („workspace-level WIT definitions **(Enterprise)**“), `work/{workitems,cycles,modules,milestones}.yaml`, `.plane/state.json`, `.plane/.state.lock`. Property-Typen: `text`/`string`, `number`, `decimal`, `date`, `datetime`, `option`/`enum` (`is_multi`), `boolean`, `url`, `email`, `member_picker`, `relation` (`relation_type: user|issue`), `release_picker` (nur Pull), `file`, `formula` (Push nicht unterstützt). Feature-Flags `cycles`, `modules`, `pages`, `views`, `intakes`, `epics`, `work_item_types`, `workflows`, `parallel_cycles`, `project_updates`. Workflow-Transitionen `type: transition|approval`, `required_approvals`, `approvers` (E-Mails). Fehlerfälle 401/403/404/429.
- **Migrationsbedeutung:** Compose ist ein **externer Client**; die Zielplattform muss die von Compose genutzten öffentlichen API-Endpunkte (v1/v2 inkl. Work-Item-Types, Properties, Workflows, Features, Milestones, Templates) kompatibel bereitstellen (genaue Endpunktliste von Compose UNVERIFIZIERT; Abgleich mit P02/P06). Ein .NET-Port der CLI ist optional (OP-12).
- **Konfidenz:** hoch (CLI-Oberfläche) / niedrig (genutzte Endpunkte).

#### P09-F56 – Offizielle SDKs

- Node `@makeplane/plane-node-sdk` (npm latest 0.3.1) und Python `plane-sdk`; OAuth-Helfer (`getAuthorizationUrl`, `getBotToken`, `exchangeCodeForToken`, `getRefreshToken` bzw. `get_authorization_url`, `get_client_credentials_token`, `exchange_code`, `refresh_token`) (`DD/dev-tools/build-plane-app/sdks.md`). Basis-Pfad `/api/v1`, Header `X-Api-Key` (API-Key) oder `Authorization: Bearer` (Access-Token) (`GH:` `src/api/BaseResource.ts`). Ressourcen-Module im Node-SDK (Verzeichnis `src/api`): Ordner `AgentRuns`, `Collections`, `Customers`, `Initiatives`, `ProjectTemplates`, `Releases`, `Teamspaces`, `WorkItemProperties`, `WorkItemTypeGovernance`, `WorkItems`, `Workflows`, `WorkspaceTemplates`, `WorkspaceWorkItemProperties`, `WorkspaceWorkItemTypes`, `WorkspaceWorkflows`, `v2`; Dateien `BaseResource.ts`, `Cycles.ts`, `Epics.ts`, `Estimates.ts`, `Intake.ts`, `Labels.ts`, `Links.ts`, `Milestones.ts`, `Modules.ts`, `Pages.ts`, `Projects.ts`, `Roles.ts`, `States.ts`, `Stickies.ts`, `Users.ts`, `WorkItemRelationDefinitions.ts`, `WorkItemTypes.ts`, `Workspace.ts`, `WorkspaceProjectLabels.ts`, `WorkspaceProjectStates.ts`, `WorkspaceStates.ts` (`GH:` https://github.com/makeplane/plane-node-sdk/tree/main/src/api – Listing ggf. gekürzt).
- **Migrationsbedeutung:** API-Kompatibilität ist die Anforderung (Agents/Apps nutzen die SDKs); ein eigenes .NET-SDK ist nicht erforderlich. **Konfidenz:** hoch.

#### P09-F57 – Desktop-App

- Belegt: Changelog-Titel „Release v3.0.0 – Desktop app, smarter workflows, powerful Plane AI upgrades“ (14.07.2026) (`WEB(P06)` https://plane.so/changelog/release-v3-0-0-desktop-app-smarter-workflows-powerful-plane-ai-upgrades); CE-Spuren `Device.DeviceType.DESKTOP` (`apps/api/plane/db/models/device.py` Z. 16), reservierter Workspace-Slug `desktop` (`packages/constants/src/workspace.ts` `RESTRICTED_URLS`). **[Verifikation] Nutzer-Doku** (`WEB(V09)` https://docs.plane.so/devices/desktop , Suchzusammenfassung): eigene App für **macOS (ab 12) und 64-bit-Linux**; Windows laut Download-Seite „Coming soon“ (`WEB(V09)` https://plane.so/download, nennt noch Version v2.0.0 – Inkonsistenz der Herstellerseiten); lädt die vollständige Plane-Web-App in eigenem Fenster mit **Browser-artigen Tabs**, **mehreren Fenstern**, **Dock-/Taskleisten-Badge für ungelesene Benachrichtigungen**, **Deep Links** und **automatischen Updates**; beim ersten Start Wahl **Cloud** oder **Self-managed** (Instanz wird gemerkt); Self-managed erfordert **Plane Commercial ab v3.0.0**. Offline-Fähigkeit und Tier: UNVERIFIZIERT → OP-13.
- **Ziel (Vorschlag):** Wrapper um die Angular-SPA (Tauri oder Electron; ADR-002 betrifft nur die Serverseite) mit Tabs, Mehrfenstern, Badge für ungelesene Benachrichtigungen, Deep Links und Auto-Update (airgapped: Update-Quelle konfigurierbar); Geräte-Registrierung über `Device`/`DeviceSession`. **Konfidenz:** mittel (Funktionsumfang laut Doku) / niedrig (Tier).

#### P09-F58 – Mobile-Apps (iOS/Android)

- **CE-Spuren:** `Device` (`device_type` ∈ {`ANDROID`, `IOS`, `WEB`, `DESKTOP`}, `device_id`, `push_token`, `is_active`) und `DeviceSession` (`device`, `session`, `is_active`, `user_agent`, `ip_address`, `start_time`, `end_time`) (`apps/api/plane/db/models/device.py`); Profilfelder `is_mobile_onboarded`, `mobile_onboarding_step` (`profile_complete`, `workspace_create`, `workspace_join`), `mobile_timezone_auto_set` (`apps/api/plane/db/models/user.py` Z. 34–39, 246–249); SSO-Setup-Dialoge mit Abschnitt **„Mobile details“** (SAML: „Entity ID | Audience | Metadata information“, „SSO URL“, „SLO URL“; OIDC: „Origin URL“, „Redirect URL“, „Logout URL“) (`auth.json` `sso.providers.{saml,oidc}.setup_modal.mobile_details.*`); reservierte Slugs `m`, `mobile`. Keine Zeile in der Plan-Matrix. **CE-Status [Verifikation, Korrektur]:** Stub/UI-Hülle im CE (vorher „teilweise“) – `Device`/`DeviceSession` werden außer in `db/models` nirgends verwendet, die Mobile-Profilfelder haben keine Logik (nur über `ProfileSerializer` `fields = "__all__"` sichtbar), die i18n-Schlüssel `mobile_details` sind im CE-Code ohne Referenz.
- **[Verifikation] Nutzer-Doku** (`WEB(V09)` https://docs.plane.so/devices/mobile , Suchzusammenfassung): Android 10+ (SDK 29+) und iOS 13+; keine Registrierung in der App, Mitgliedschaft in mindestens einem Workspace nötig; verfügbar für Plane Cloud und Self-hosted „on all plans of the Commercial Edition starting from version v1.5.0“ (Login-404 gegen ältere Instanzen); **Push-Benachrichtigungen nur für Plane Cloud**. App-Store-Eintrag „Plane: Projects, Wiki, AI“ (Plane Software, Inc.): Benachrichtigungen zu Zuweisungen, Erwähnungen, Kommentaren; Projekte ansehen; Cycles und Modules verfolgen; Page-Bearbeitung „coming soon“ (`WEB(V09)` https://apps.apple.com/in/app/plane-projects-wiki-ai/id6657986465). Mobile-Changelog (`WEB(V09)` https://plane.so/changelog/mobile): v2.4.0 (31.07.2026) Plane AI mit Skills und Autopilot-Modus (F61), Catch-Up-Widget (F43), Work-Item-Relationen und -Abhängigkeiten; v2.5.0 (19.08.2026) Homescreen-Widgets für Work Items fällig heute/morgen/diese Woche, MCP-Connectoren, Plane AI für Self-hosted. Welche API die Apps nutzen (Kandidat: Commercial-Route `/graphql/`, Dok. 22 P03-F40), ist UNVERIFIZIERT.
- **Bewertung:** Native Apps sind eigenständige Clients (nicht Teil dieses Repos); Funktionsumfang im Detail, Push-Infrastruktur (FCM/APNs – nicht airgapped-fähig; laut Doku ohnehin nur Cloud) und Tier sind **UNVERIFIZIERT** → OP-13 (Rückfrage, ob Mobile im Migrationsumfang ist; Alternative: responsive Angular-PWA).
- **Ziel (falls im Umfang):** API-Endpunkte für Geräte-Registrierung/Push-Token, Mobile-Onboarding-Felder, SSO-Mobile-Callbacks beibehalten. **Konfidenz:** niedrig.

---

### 3.E Querschnittliche Zielarchitektur (.NET Aspire / EF Core / PostgreSQL+pgvector / Angular) – Empfehlung, nicht bindend

| Original-Dienst (Commercial) | Rolle im Cluster | Ziel in .NET (Aspire-Ressource) | Begründung/ADR |
|---|---|---|---|
| `silo` (Node, `makeplane/silo-commercial`, `/silo`) | Integrationen (F01–F20, F59), Importer (F21–F31, F60) | Projekt `Plane.Integrations` (eigener Dienst `integrations` hinter YARP-Route `/silo/…`, gleiche externe Pfade wie Anhang C) + Hintergrund-Worker `integrations-worker` | ADR-002 (kein Node); Pfadkompatibilität für Hersteller-Setup-Anleitungen |
| `worker-importers` (Celery-Queue `celery.importer`) | Import-Jobs | `BackgroundService` im `integrations-worker` mit eigener Queue | Isolation langer CPU-Jobs (Helm-Kommentar Confluence) |
| `pi-api`, `pi-worker`, `pi-beat`, `pi-migrator` (Python/FastAPI, eigene DB `plane_pi`) | Plane AI (F33–F46, F61) | Projekt `Plane.AI` (Dienst `ai`, YARP-Route `/pi/…`), Schema `ai` in der Haupt-DB mit pgvector; Jobs via Quartz.NET/`BackgroundService` | ADR-002, ADR-004 (pgvector statt OpenSearch-k-NN) |
| OpenSearch (k-NN, ML-Commons-Embeddings, BM25) | Retrieval/Semantik | PostgreSQL: `tsvector` + `pg_trgm` (Volltext, siehe P03) und `vector` (HNSW) | ADR-004 |
| `agent-consumer` (Queue `plane.agent`) | Agent-Run-Webhooks (F50) | Consumer im API-Host oder `webhooks-worker` | Messaging wie P03/P06 |
| `webhook-consumer` (Queue `plane.webhook`) | Webhooks v2 (F51) | `webhooks-worker` (Outbox → RabbitMQ oder PostgreSQL-Queue) | P06-Outbox |
| `runner` (Node-Isolates) | Plane Runner (F54) | `Plane.Runner` mit Jint/ClearScript (Details P06) | ADR-002 |
| `mcp-server` (Python, `/mcp`) | MCP (F53) | Dienst `mcp` mit `ModelContextProtocol.AspNetCore` | ADR-002 |
| API (Django) OAuth-Server `/auth/o/…` | OAuth-Apps (F47–F49) | OpenIddict im API-Host | – |

**Gemeinsame Bausteine:**

1. **Geheimnisse:** ASP.NET Core Data Protection (Key-Ring in PostgreSQL) für alle Fremd-Tokens, App-Secrets, Webhook-Secrets, LLM-Keys; Rotation mit Re-Encryption (Original-Warnung „NEVER ROTATE“ für `AES_SECRET_KEY` nicht übernehmen).
2. **Eingehende Webhooks** (GitHub, GitLab, Bitbucket, Slack, Sentry, Cursor): Signaturprüfung je Anbieter (`X-Hub-Signature-256`, `X-Gitlab-Token`, Bitbucket-HMAC, `X-Slack-Signature` + Timestamp, Sentry `Sentry-Hook-Signature`), sofortige 2xx-Antwort, Persistenz in `InboundWebhookEvent`, Deduplizierung (Original `DEDUP_INTERVAL` 3 s), Batch-Verarbeitung (Original `BATCH_SIZE`).
3. **Ausgehende Änderungen** (Plane → Fremdsystem, Webhooks v2, Agents): Transactional Outbox (P06), Consumer mit Retry/Backoff, Echo-Unterdrückung über Aktor-ID der Integrations-Bots.
4. **Aktor-Modell:** Jede Integration/App handelt in Plane über eine App-Installation mit Bot-User (`User.is_bot=true`, neuer `bot_type`), damit Activity-Feed, Benachrichtigungen und Rechte konsistent bleiben (CE-Altmodell `WorkspaceIntegration.actor`).
5. **LLM-Abstraktion:** `Microsoft.Extensions.AI` (`IChatClient`, `IEmbeddingGenerator`) mit Providern OpenAI-kompatibel (Pflicht, lokal), Anthropic, Azure OpenAI, Bedrock (optional); Streaming via SSE; Tool-Calling auf Domänen-Services mit Nutzerrechten.
6. **Angular:** Feature-Bereiche (lazy routes) `settings/integrations` (+ `:provider`), `settings/imports`, `settings/applications`, `settings/access-tokens`, `settings/webhooks` (v1/v2), `settings/plane-ai`, `settings/runner`, `settings/connections`, `profile/connections`, `pi-chat`, OAuth-Consent-Seite; Komponenten aus der Propel-Nachbildung (Icons/Brand-Logos siehe Q8); Store-Logik analog MobX-Stores des Originals (ADR-003-Konsequenz: JSON-Verträge snake_case).
7. **Airgapped (ADR-004):** Alle SaaS-Konnektoren hinter Instanz-Schaltern; selbst gehostete Gegenstellen (GHE Server, GitLab Self-managed, Bitbucket DC, Jira Server/DC, Sentry self-hosted, Confluence-Datei-Import) und lokales LLM/Embedding/STT sind vollständig ohne Internet nutzbar; eigene CA-Zertifikate konfigurierbar.

---

## 4. Offene Punkte / Unklarheiten

| ID | Thema | Problem | Vorschlag / Rückfrage |
|---|---|---|---|
| OP-01 | Recherchelücke | WebSearch-Kontingent war in diesem Lauf erschöpft; Nutzer-Doku `docs.plane.so/integrations/*`, `/importers/*`, `/ai/*` und Changelogs konnten nicht gelesen werden | Nachrecherche-Lauf mit neuem Suchkontingent für: GitHub/GitLab/Slack/Sentry-Nutzerdoku, Importer-Doku (Jira, Jira Server, Linear, Asana, ClickUp, Notion, Confluence, CSV), Plane-AI-Doku (Pi-Chat, Skills, Memory, Agents, Connectors, Credits/Usage), Desktop-/Mobile-Apps. **Stand Verifikation:** teilweise erledigt (14 Suchen, Verifikations-Protokoll V-W01 bis V-W14): Importer ClickUp, CSV, Flatfile, Linear, Asana, Confluence, Skills, Connectors, eingebaute Agents, Credits, Desktop, Mobile nachrecherchiert; offen: Memory, Schritt-Doku Notion und Jira, Slack-/GitHub-Nutzerdoku im Detail |
| OP-02 | Pixelgenaue Referenzen (ADR-005) | Für alle EE-Seiten dieses Clusters liegen außer dem Webhook-Formular (`IMG/webhooks/create-webhook.webp`) keine aktuellen Screenshots vor; Legacy-Screenshots (2023) zeigen veraltete Layouts | **Rückfrage:** Zugang zu einer lizenzierten Commercial-Instanz (oder Plane Cloud Trial) zur Erstellung von Referenz-Screenshots? Ohne diese ist „1:1“ für diese Seiten nur stilistisch (Propel-Design-System) erreichbar |
| OP-03 | Interne App-API der Integrationen/Importer | Endpunkte des Web-Clients zu Silo/PI sind nicht dokumentiert | Neuentwurf nach CE-Konventionen (Vorschläge in F01, F21, F34, F47); Contract-Tests nur für öffentliche Endpunkte möglich |
| OP-04 | Verknüpfung PR/MR ↔ Work Item | Regel (Identifier im Titel/Branch/Beschreibung, Schlüsselwörter) nicht belegt | **Rückfrage**; Vorschlag: Identifier `PROJ-123` in Titel, Beschreibung oder Branch-Name; Schlüsselwörter optional |
| OP-05 | Slack-Detailverhalten | Unterbefehle von `/plane`, Modal-Felder, Unfurl-Layout, Thread-Sync-Richtung | Nach OP-01 klären; bis dahin Vorschlag F11 |
| OP-06 | Sentry-Komponenten-URIs | Ob Sentry `/api/sentry/...` relativ zu `/silo` auflöst | Beim Nachbau Sentry-Integration-Platform-Doku prüfen; beide Pfade bedienen |
| OP-07 | Nur schwach/nicht belegte Integrationen | HubSpot, Cursor, Zapier, Zendesk, Freshdesk (Coming soon), Microsoft Teams, Discord, Monday (ClickUp-Importer in der Verifikation belegt, F26; Zapier/Teams-Suche ohne Treffer) | **Rückfrage**, welche gebaut werden sollen; ohne Originalfunktion nur nach eigenem Entwurf möglich |
| OP-08 | Importer-UI und -Mappings | Aktueller EE-Assistent je Quelle, Feld-Mappings, Bericht-Download; CSV-Work-Item-Import in der Verifikation **belegt** (F29), Flatfile nur Cloud (F60) | Legacy-Assistent (F21) und belegte Abläufe Linear/Asana/ClickUp/CSV als Basis; Rückfrage zu CSV entfällt; offen: Spalten-Mapping-Dialog für Airgapped (ersetzt Flatfile) |
| OP-09 | Plane-AI-Detailfunktionen | Chat-UI (Verlauf, Teilen, Feedback), Skills, Memory, eingebaute Agents, Connectors, Duplikat-UI, AI-Filter/Summary/Catch-up/Copy-as-prompt, Text→Work Items, Artifacts-UI | Nach OP-01 klären; bis dahin Vorschläge in F34–F44 (als UNVERIFIZIERT markiert). **Stand Verifikation:** Skills, eingebaute Agents, Connectors, Duplikat-UI-Ort (CE-Stubs), Catch Up (Mobile), Autopilot (F61) belegt; offen: Chat-UI im Detail, Memory, AI-Filter, Copy as prompt, Text → Work Items, Artifacts-UI |
| OP-10 | Agents: `error`-Activity | Doku widersprüchlich (ephemer vs. erzeugt Kommentar) | Vorschlag: `error` erzeugt einen sichtbaren Kommentar und setzt `failed`; nicht in der ephemeren Statuszeile verschwinden lassen |
| OP-11 | Webhook-Doku-Fehler | Beispiel-`event`-Wert `WebhookScope.ScopeChoices.WORK_ITEM_UPDATED`, `"None"`-Strings | Ziel sendet Dot-Notation und JSON-`null` |
| OP-12 | Plane Compose | Welche API-Endpunkte Compose exakt nutzt; ob ein .NET-Port gewünscht ist | Compose-Quellcode (PyPI-Paket) im Nachgang auswerten; Kompatibilitätstests mit Original-CLI |
| OP-13 | Desktop- und Mobile-Apps | Umfang, Plattformen, Tier, Push-Infrastruktur (nicht airgapped-fähig) | **Rückfrage:** Sind native Desktop-/Mobile-Clients Teil des Migrationsumfangs oder genügt die responsive Angular-Web-App (ggf. als PWA/Tauri-Wrapper)? **Stand Verifikation:** Plattformen und Voraussetzungen belegt (F57: macOS/Linux, Commercial ≥ v3.0.0; F58: iOS 13+/Android 10+, Commercial ≥ v1.5.0, Push nur Cloud); die Rückfrage zum Umfang bleibt |
| OP-14 | LLM-Qualität lokal | Hersteller: Custom LLM „should have at least 1 trillion parameters for all Plane AI features to work reliably“ | Für airgapped Betrieb realistische lokale Modelle definieren; Funktionen mit hohem Qualitätsanspruch (Agents, Text→Work Items) ggf. als „experimentell“ kennzeichnen |
| OP-15 | Tier-Widersprüche | AI-Block: in Dok. 26 (Verifikation) zugunsten **Business** aufgelöst (F39); draw.io Business (Dok. 26) vs. Pro (Dok. 22) (F59); Plane-AI-Credits für Free laut Drittquellen vs. „paid seat“ laut Doku (F33); gesamte Matrix-Sektion „Integrations“ „Coming soon“ trotz dokumentierter Auslieferung (Badge Pro) | Nach ADR-001 ohne Auswirkung; nur dokumentarisch |
| OP-16 | Workspace-„Connections“ | Eintrag in der EE-Workspace-Sidebar (Screenshot) ohne Beschreibung; Bedeutung (MCP-Connectoren für Plane AI vs. Integrationsverbindungen) unklar | Nach OP-01 klären. **Stand Verifikation:** Connectoren werden laut Doku unter Integrations → Connectors verwaltet (F35); die Bedeutung des separaten Eintrags „Connections“ bleibt offen |

---

## Anhang A: Vollständiges i18n-Inventar `packages/i18n/src/locales/en/integration.json`

Automatisch extrahiert (read-only Skript), 291 Schlüssel. Alle Schlüssel haben im CE keine Referenz außer `integrations.*`-Präfixen (P01 Anhang A: 290/291 ohne CE-Referenz). Spalte „Feature“ ordnet dem Abschnitt in Kapitel 3 zu.

| # | Schlüssel | Text (en, wörtlich) | Feature |
|---|---|---|---|
| 1 | `integrations.integrations` | Integrations | F01 |
| 2 | `integrations.loading` | Loading | F01 |
| 3 | `integrations.unauthorized` | You are not authorized to view this page. | F01 |
| 4 | `integrations.configure` | Configure | F01 |
| 5 | `integrations.not_enabled` | {name} is not enabled for this workspace. | F01 |
| 6 | `integrations.not_configured` | Not configured | F01 |
| 7 | `integrations.disconnect_personal_account` | Disconnect personal {providerName} account | F01 |
| 8 | `integrations.not_configured_message_admin` | {name} integration is not configured. Please contact your instance admin to configure it. | F01 |
| 9 | `integrations.not_configured_message_support` | {name} integration is not configured. Please contact support to configure it. | F01 |
| 10 | `integrations.external_api_unreachable` | Not able to access the external API. Please try again later. | F01 |
| 11 | `integrations.error_fetching_supported_integrations` | Not able to fetch supported integrations. Please try again later. | F01 |
| 12 | `integrations.back_to_integrations` | Back to integrations | F01 |
| 13 | `integrations.select_state` | Select State | F01 |
| 14 | `integrations.set_state` | Set State | F01 |
| 15 | `integrations.choose_project` | Choose Project... | F01 |
| 16 | `integrations.skip_backward_state_movement` | Prevent issues from moving to an earlier state due to PR updates | F01 |
| 17 | `github_integration.name` | GitHub | F02–F04 |
| 18 | `github_integration.description` | Connect and sync your GitHub work items with Plane | F02–F04 |
| 19 | `github_integration.connect_org` | Connect Organization | F02–F04 |
| 20 | `github_integration.connect_org_description` | Connect your GitHub organization with Plane | F02–F04 |
| 21 | `github_integration.processing` | Processing | F02–F04 |
| 22 | `github_integration.org_added_desc` | GitHub org added by and time | F02–F04 |
| 23 | `github_integration.connection_fetch_error` | Error fetching connection details from server | F02–F04 |
| 24 | `github_integration.personal_account_connected` | Personal account connected | F02–F04 |
| 25 | `github_integration.personal_account_connected_description` | Your GitHub account is now connected to Plane | F02–F04 |
| 26 | `github_integration.connect_personal_account` | Connect Personal Account | F02–F04 |
| 27 | `github_integration.connect_personal_account_description` | Connect your personal GitHub account with Plane. | F02–F04 |
| 28 | `github_integration.repo_mapping` | Repository Mapping | F02–F04 |
| 29 | `github_integration.repo_mapping_description` | Map your GitHub repositories with Plane projects. | F02–F04 |
| 30 | `github_integration.project_issue_sync` | Project Issue Sync | F02–F04 |
| 31 | `github_integration.project_issue_sync_description` | Sync issues from GitHub to your Plane project | F02–F04 |
| 32 | `github_integration.project_issue_sync_empty_state` | Mapped project issue sync will appear here | F02–F04 |
| 33 | `github_integration.configure_project_issue_sync_state` | Configure Issue Sync State | F02–F04 |
| 34 | `github_integration.select_issue_sync_direction` | Select issue sync direction | F02–F04 |
| 35 | `github_integration.allow_bidirectional_sync` | Bidirectional - Sync issues and comments both ways between GitHub and Plane | F02–F04 |
| 36 | `github_integration.allow_unidirectional_sync` | Unidirectional - Sync issues and comments from GitHub to Plane only | F02–F04 |
| 37 | `github_integration.allow_unidirectional_sync_warning` | Data from GitHub Issue will replace data in Linked Plane Work Item (GitHub → Plane only) | F02–F04 |
| 38 | `github_integration.remove_project_issue_sync` | Remove this Project Issue Sync | F02–F04 |
| 39 | `github_integration.remove_project_issue_sync_confirmation` | Are you sure you want to remove this project issue sync? | F02–F04 |
| 40 | `github_integration.add_pr_state_mapping` | Add Pull Request State Mapping for Plane project | F02–F04 |
| 41 | `github_integration.edit_pr_state_mapping` | Edit Pull Request State Mapping for Plane project | F02–F04 |
| 42 | `github_integration.pr_state_mapping` | Pull Request State Mapping | F02–F04 |
| 43 | `github_integration.pr_state_mapping_description` | Map GitHub pull request states to your Plane project | F02–F04 |
| 44 | `github_integration.pr_state_mapping_empty_state` | Mapped PR states will appear here | F02–F04 |
| 45 | `github_integration.remove_pr_state_mapping` | Remove this Pull Request State Mapping | F02–F04 |
| 46 | `github_integration.remove_pr_state_mapping_confirmation` | Are you sure you want to remove this pull request state mapping? | F02–F04 |
| 47 | `github_integration.issue_sync_message` | Work items are synced to {project} | F02–F04 |
| 48 | `github_integration.link` | Link GitHub Repository to a Plane Project | F02–F04 |
| 49 | `github_integration.pull_request_automation` | Pull Request Automation | F02–F04 |
| 50 | `github_integration.pull_request_automation_description` | Configure pull request state mapping from GitHub to your Plane project | F02–F04 |
| 51 | `github_integration.DRAFT_MR_OPENED` | Draft Open | F02–F04 |
| 52 | `github_integration.MR_OPENED` | Open | F02–F04 |
| 53 | `github_integration.MR_READY_FOR_MERGE` | Ready for Merge | F02–F04 |
| 54 | `github_integration.MR_REVIEW_REQUESTED` | Review Requested | F02–F04 |
| 55 | `github_integration.MR_MERGED` | Merged | F02–F04 |
| 56 | `github_integration.MR_CLOSED` | Closed | F02–F04 |
| 57 | `github_integration.ISSUE_OPEN` | Issue Open | F02–F04 |
| 58 | `github_integration.ISSUE_CLOSED` | Issue Closed | F02–F04 |
| 59 | `github_integration.save` | Save | F02–F04 |
| 60 | `github_integration.start_sync` | Start Sync | F02–F04 |
| 61 | `github_integration.choose_repository` | Choose Repository... | F02–F04 |
| 62 | `gitlab_integration.name` | Gitlab | F06 |
| 63 | `gitlab_integration.description` | Connect and sync your Gitlab Merge Requests with Plane. | F06 |
| 64 | `gitlab_integration.connection_fetch_error` | Error fetching connection details from server | F06 |
| 65 | `gitlab_integration.connect_org` | Connect Organization | F06 |
| 66 | `gitlab_integration.connect_org_description` | Connect your Gitlab organization with Plane. | F06 |
| 67 | `gitlab_integration.project_connections` | Gitlab Project Connections | F06 |
| 68 | `gitlab_integration.project_connections_description` | Sync merge requests from Gitlab to Plane projects. | F06 |
| 69 | `gitlab_integration.plane_project_connection` | Plane Project Connection | F06 |
| 70 | `gitlab_integration.plane_project_connection_description` | Configure pull requests state mapping from Gitlab to Plane projects | F06 |
| 71 | `gitlab_integration.remove_connection` | Remove Connection | F06 |
| 72 | `gitlab_integration.remove_connection_confirmation` | Are you sure you want to remove this connection? | F06 |
| 73 | `gitlab_integration.link` | Link Gitlab repository to Plane project | F06 |
| 74 | `gitlab_integration.pull_request_automation` | Pull Request Automation | F06 |
| 75 | `gitlab_integration.pull_request_automation_description` | Configure pull request state mapping from Gitlab to Plane | F06 |
| 76 | `gitlab_integration.DRAFT_MR_OPENED` | On draft MR open, set the state to | F06 |
| 77 | `gitlab_integration.MR_OPENED` | On MR open, set the state to | F06 |
| 78 | `gitlab_integration.MR_REVIEW_REQUESTED` | On MR review requested, set the state to | F06 |
| 79 | `gitlab_integration.MR_READY_FOR_MERGE` | On MR ready for merge, set the state to | F06 |
| 80 | `gitlab_integration.MR_MERGED` | On MR merged, set the state to | F06 |
| 81 | `gitlab_integration.MR_CLOSED` | On MR closed, set the state to | F06 |
| 82 | `gitlab_integration.integration_enabled_text` | With Gitlab integration Enabled, you can automate work item workflows | F06 |
| 83 | `gitlab_integration.choose_entity` | Choose Entity | F06 |
| 84 | `gitlab_integration.choose_project` | Choose Project | F06 |
| 85 | `gitlab_integration.link_plane_project` | Link Plane project | F06 |
| 86 | `gitlab_integration.project_issue_sync` | Project Issue Sync | F06 |
| 87 | `gitlab_integration.project_issue_sync_description` | Sync issues from Gitlab to your Plane project | F06 |
| 88 | `gitlab_integration.project_issue_sync_empty_state` | Mapped project issue sync will appear here | F06 |
| 89 | `gitlab_integration.configure_project_issue_sync_state` | Configure Issue Sync State | F06 |
| 90 | `gitlab_integration.select_issue_sync_direction` | Select issue sync direction | F06 |
| 91 | `gitlab_integration.allow_bidirectional_sync` | Bidirectional - Sync issues and comments both ways between Gitlab and Plane | F06 |
| 92 | `gitlab_integration.allow_unidirectional_sync` | Unidirectional - Sync issues and comments from Gitlab to Plane only | F06 |
| 93 | `gitlab_integration.allow_unidirectional_sync_warning` | Data from Gitlab Issue will replace data in Linked Plane Work Item (Gitlab → Plane only) | F06 |
| 94 | `gitlab_integration.remove_project_issue_sync` | Remove this Project Issue Sync | F06 |
| 95 | `gitlab_integration.remove_project_issue_sync_confirmation` | Are you sure you want to remove this project issue sync? | F06 |
| 96 | `gitlab_integration.ISSUE_OPEN` | Issue Open | F06 |
| 97 | `gitlab_integration.ISSUE_CLOSED` | Issue Closed | F06 |
| 98 | `gitlab_integration.save` | Save | F06 |
| 99 | `gitlab_integration.start_sync` | Start Sync | F06 |
| 100 | `gitlab_integration.choose_repository` | Choose Repository... | F06 |
| 101 | `gitlab_enterprise_integration.name` | Gitlab Enterprise | F07 |
| 102 | `gitlab_enterprise_integration.description` | Connect and sync your Gitlab Enterprise instance with Plane. | F07 |
| 103 | `gitlab_enterprise_integration.app_form_title` | Gitlab Enterprise Configuration | F07 |
| 104 | `gitlab_enterprise_integration.app_form_description` | Configure Gitlab Enterprise to connect with Plane. | F07 |
| 105 | `gitlab_enterprise_integration.base_url_title` | Base URL | F07 |
| 106 | `gitlab_enterprise_integration.base_url_description` | The base URL of your Gitlab Enterprise instance. | F07 |
| 107 | `gitlab_enterprise_integration.base_url_placeholder` | e.g., "https://glab.plane.town" | F07 |
| 108 | `gitlab_enterprise_integration.base_url_error` | Base URL is required | F07 |
| 109 | `gitlab_enterprise_integration.invalid_base_url_error` | Invalid base URL | F07 |
| 110 | `gitlab_enterprise_integration.client_id_title` | App ID | F07 |
| 111 | `gitlab_enterprise_integration.client_id_description` | The app ID of the app you created in your Gitlab Enterprise instance. | F07 |
| 112 | `gitlab_enterprise_integration.client_id_placeholder` | e.g., "7cd732xxxxxxxxxxxxxx" | F07 |
| 113 | `gitlab_enterprise_integration.client_id_error` | App ID is required | F07 |
| 114 | `gitlab_enterprise_integration.client_secret_title` | Client Secret | F07 |
| 115 | `gitlab_enterprise_integration.client_secret_description` | The client secret of the app you created in your Gitlab Enterprise instance. | F07 |
| 116 | `gitlab_enterprise_integration.client_secret_placeholder` | e.g., "gloas-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | F07 |
| 117 | `gitlab_enterprise_integration.client_secret_error` | Client secret is required | F07 |
| 118 | `gitlab_enterprise_integration.webhook_secret_title` | Webhook Secret | F07 |
| 119 | `gitlab_enterprise_integration.webhook_secret_description` | A random webhook secret that will be used to verify the webhook from Gitlab Enterprise instance. | F07 |
| 120 | `gitlab_enterprise_integration.webhook_secret_placeholder` | e.g., "webhook1234567890" | F07 |
| 121 | `gitlab_enterprise_integration.webhook_secret_error` | Webhook secret is required | F07 |
| 122 | `gitlab_enterprise_integration.connect_app` | Connect App | F07 |
| 123 | `slack_integration.name` | Slack | F09 |
| 124 | `slack_integration.description` | Connect your Slack workspace with Plane. | F09 |
| 125 | `slack_integration.connect_personal_account` | Connect your personal Slack account with Plane. | F09 |
| 126 | `slack_integration.personal_account_connected` | Your personal {providerName} account is now connected to Plane. | F09 |
| 127 | `slack_integration.link_personal_account` | Link your personal {providerName} account to Plane. | F09 |
| 128 | `slack_integration.connected_slack_workspaces` | Connected Slack workspaces | F09 |
| 129 | `slack_integration.connected_on` | Connected on {date} | F09 |
| 130 | `slack_integration.disconnect_workspace` | Disconnect {name} workspace | F09 |
| 131 | `slack_integration.alerts.dm_alerts.title` | Get notified in Slack DMs for important updates, reminders, and alerts just for you. | F09 |
| 132 | `slack_integration.project_updates.title` | Project Notifications | F10 |
| 133 | `slack_integration.project_updates.description` | Configure Slack channels for project notifications | F10 |
| 134 | `slack_integration.project_updates.add_new_project_update` | Add new project notifications | F10 |
| 135 | `slack_integration.project_updates.project_updates_empty_state` | Projects connected with Slack Channels will appear here. | F10 |
| 136 | `slack_integration.project_updates.project_updates_form.title` | Configure Slack Channel | F10 |
| 137 | `slack_integration.project_updates.project_updates_form.description` | Receive project notifications in selected Slack channel when work item is created | F10 |
| 138 | `slack_integration.project_updates.project_updates_form.failed_to_load_channels` | Failed to load channels from Slack | F10 |
| 139 | `slack_integration.project_updates.project_updates_form.project_dropdown.placeholder` | Select a project | F10 |
| 140 | `slack_integration.project_updates.project_updates_form.project_dropdown.label` | Plane Project | F10 |
| 141 | `slack_integration.project_updates.project_updates_form.project_dropdown.no_projects` | No projects available | F10 |
| 142 | `slack_integration.project_updates.project_updates_form.channel_dropdown.label` | Slack Channel | F10 |
| 143 | `slack_integration.project_updates.project_updates_form.channel_dropdown.placeholder` | Select a channel | F10 |
| 144 | `slack_integration.project_updates.project_updates_form.channel_dropdown.no_channels` | No channels available | F10 |
| 145 | `slack_integration.project_updates.project_updates_form.all_projects_connected` | All projects are already connected to Slack channels. | F10 |
| 146 | `slack_integration.project_updates.project_updates_form.all_channels_connected` | All Slack channels are already connected to projects. | F10 |
| 147 | `slack_integration.project_updates.project_updates_form.project_connection_success` | Project connection created successfully | F10 |
| 148 | `slack_integration.project_updates.project_updates_form.project_connection_updated` | Project connection updated successfully | F10 |
| 149 | `slack_integration.project_updates.project_updates_form.project_connection_deleted` | Project connection deleted successfully | F10 |
| 150 | `slack_integration.project_updates.project_updates_form.failed_delete_project_connection` | Failed to delete project connection | F10 |
| 151 | `slack_integration.project_updates.project_updates_form.failed_create_project_connection` | Failed to create project connection | F10 |
| 152 | `slack_integration.project_updates.project_updates_form.failed_upserting_project_connection` | Failed to upsert project connection | F10 |
| 153 | `slack_integration.project_updates.project_updates_form.failed_loading_project_connections` | We couldn't load your project connections. This could be due to a network issue or a problem with the integration. | F10 |
| 154 | `sentry_integration.name` | Sentry | F12 |
| 155 | `sentry_integration.description` | Connect your Sentry workspace with Plane. | F12 |
| 156 | `sentry_integration.connected_sentry_workspaces` | Connected Sentry workspaces | F12 |
| 157 | `sentry_integration.connected_on` | Connected on {date} | F12 |
| 158 | `sentry_integration.disconnect_workspace` | Disconnect {name} workspace | F12 |
| 159 | `sentry_integration.state_mapping.title` | State Mapping | F12 |
| 160 | `sentry_integration.state_mapping.description` | Map Sentry issue states to your project states. Configure which states to use when a Sentry issue is resolved or unresolved. | F12 |
| 161 | `sentry_integration.state_mapping.add_new_state_mapping` | Add new state mapping | F12 |
| 162 | `sentry_integration.state_mapping.empty_state` | No state mappings configured. Create your first mapping to sync Sentry issue states with your project states. | F12 |
| 163 | `sentry_integration.state_mapping.failed_loading_state_mappings` | We couldn't load your state mappings. This could be due to a network issue or a problem with the integration. | F12 |
| 164 | `sentry_integration.state_mapping.loading_project_states` | Loading project states... | F12 |
| 165 | `sentry_integration.state_mapping.error_loading_states` | Error loading states | F12 |
| 166 | `sentry_integration.state_mapping.no_states_available` | No states available | F12 |
| 167 | `sentry_integration.state_mapping.no_permission_states` | You don't have permission to access states for this project | F12 |
| 168 | `sentry_integration.state_mapping.states_not_found` | Project states not found | F12 |
| 169 | `sentry_integration.state_mapping.server_error_states` | Server error while loading states | F12 |
| 170 | `bitbucket_dc_integration.name` | Bitbucket Data Center | F08 |
| 171 | `bitbucket_dc_integration.description` | Connect and sync your Bitbucket Data Center repositories with Plane. | F08 |
| 172 | `oauth_bridge_integration.name` | OAuth Bridge | F20 |
| 173 | `oauth_bridge_integration.description` | Validate external IdP tokens for API access. | F20 |
| 174 | `oauth_bridge_integration.header_description` | Validate externally-issued OIDC/JWT tokens from your IdP (Azure AD, Okta, etc.) for Plane API access. | F20 |
| 175 | `oauth_bridge_integration.connected` | Connected | F20 |
| 176 | `oauth_bridge_integration.connect` | Connect | F20 |
| 177 | `oauth_bridge_integration.uninstall` | Uninstall | F20 |
| 178 | `oauth_bridge_integration.uninstalling` | Uninstalling... | F20 |
| 179 | `oauth_bridge_integration.install_success` | OAuth Bridge installed successfully. | F20 |
| 180 | `oauth_bridge_integration.install_error` | Failed to install OAuth Bridge. | F20 |
| 181 | `oauth_bridge_integration.uninstall_success` | OAuth Bridge uninstalled. | F20 |
| 182 | `oauth_bridge_integration.uninstall_error` | Failed to uninstall OAuth Bridge. | F20 |
| 183 | `oauth_bridge_integration.token_providers` | Token Providers | F20 |
| 184 | `oauth_bridge_integration.token_providers_description` | Configure external IdPs whose JWTs are accepted as API credentials. | F20 |
| 185 | `oauth_bridge_integration.add_provider` | Add provider | F20 |
| 186 | `oauth_bridge_integration.edit_provider` | Edit Provider | F20 |
| 187 | `oauth_bridge_integration.enabled` | Enabled | F20 |
| 188 | `oauth_bridge_integration.disabled` | Disabled | F20 |
| 189 | `oauth_bridge_integration.test` | Test | F20 |
| 190 | `oauth_bridge_integration.no_providers_title` | No providers configured. | F20 |
| 191 | `oauth_bridge_integration.no_providers_description` | Add an IdP to enable external token authentication. | F20 |
| 192 | `oauth_bridge_integration.provider_updated` | Provider updated. | F20 |
| 193 | `oauth_bridge_integration.provider_added` | Provider added. | F20 |
| 194 | `oauth_bridge_integration.provider_save_error` | Failed to save provider. | F20 |
| 195 | `oauth_bridge_integration.provider_deleted` | Provider deleted. | F20 |
| 196 | `oauth_bridge_integration.provider_delete_error` | Failed to delete provider. | F20 |
| 197 | `oauth_bridge_integration.provider_update_error` | Failed to update provider. | F20 |
| 198 | `oauth_bridge_integration.jwks_reachable` | JWKS Reachable | F20 |
| 199 | `oauth_bridge_integration.jwks_unreachable` | JWKS Unreachable | F20 |
| 200 | `oauth_bridge_integration.jwks_test_error` | Could not fetch JWKS from the configured URL. | F20 |
| 201 | `oauth_bridge_integration.provider_form.name_label` | Name | F20 |
| 202 | `oauth_bridge_integration.provider_form.name_placeholder` | e.g. Azure AD Production | F20 |
| 203 | `oauth_bridge_integration.provider_form.name_description` | Human-readable label for this identity provider | F20 |
| 204 | `oauth_bridge_integration.provider_form.name_required` | Name is required. | F20 |
| 205 | `oauth_bridge_integration.provider_form.issuer_label` | Issuer | F20 |
| 206 | `oauth_bridge_integration.provider_form.issuer_placeholder` | https://login.microsoftonline.com/tenant-id/v2.0 | F20 |
| 207 | `oauth_bridge_integration.provider_form.issuer_description` | Expected iss claim value in the JWT | F20 |
| 208 | `oauth_bridge_integration.provider_form.issuer_required` | Issuer is required. | F20 |
| 209 | `oauth_bridge_integration.provider_form.jwks_url_label` | JWKS URL | F20 |
| 210 | `oauth_bridge_integration.provider_form.jwks_url_placeholder` | https://login.microsoftonline.com/tenant-id/discovery/v2.0/keys | F20 |
| 211 | `oauth_bridge_integration.provider_form.jwks_url_description` | HTTPS endpoint serving the provider's JSON Web Key Set | F20 |
| 212 | `oauth_bridge_integration.provider_form.jwks_url_required` | JWKS URL is required. | F20 |
| 213 | `oauth_bridge_integration.provider_form.jwks_url_https` | JWKS URL must use HTTPS. | F20 |
| 214 | `oauth_bridge_integration.provider_form.audience_label` | Audience | F20 |
| 215 | `oauth_bridge_integration.provider_form.audience_placeholder` | api://my-app-id | F20 |
| 216 | `oauth_bridge_integration.provider_form.audience_description` | Expected aud claim(s) in the JWT, comma-separated. | F20 |
| 217 | `oauth_bridge_integration.provider_form.user_claims_label` | User claims | F20 |
| 218 | `oauth_bridge_integration.provider_form.user_claims_placeholder` | email, preferred_username, upn | F20 |
| 219 | `oauth_bridge_integration.provider_form.user_claims_description` | Comma-separated JWT claims to match against the Plane email (first match wins) | F20 |
| 220 | `oauth_bridge_integration.provider_form.user_claims_required` | At least one user claim is required. | F20 |
| 221 | `oauth_bridge_integration.provider_form.allowed_algorithms_label` | Allowed signing algorithms | F20 |
| 222 | `oauth_bridge_integration.provider_form.allowed_algorithms_description` | Asymmetric algorithms accepted for JWT signature verification | F20 |
| 223 | `oauth_bridge_integration.provider_form.allowed_algorithms_required` | At least one algorithm is required. | F20 |
| 224 | `oauth_bridge_integration.provider_form.select_algorithms` | Select algorithms | F20 |
| 225 | `oauth_bridge_integration.provider_form.jwks_cache_ttl_label` | JWKS cache TTL (seconds) | F20 |
| 226 | `oauth_bridge_integration.provider_form.jwks_cache_ttl_description` | How long to cache the provider's JWKS keys (minimum 60s, default 24 hours) | F20 |
| 227 | `oauth_bridge_integration.provider_form.jwks_cache_ttl_min` | Cache TTL must be at least 60 seconds. | F20 |
| 228 | `oauth_bridge_integration.provider_form.rate_limit_label` | Rate limit | F20 |
| 229 | `oauth_bridge_integration.provider_form.rate_limit_placeholder` | 120/minute | F20 |
| 230 | `oauth_bridge_integration.provider_form.rate_limit_description` | Request throttle as count/period (e.g. 120/minute). Leave blank for the default rate limit. | F20 |
| 231 | `oauth_bridge_integration.provider_form.enable_provider` | Enable this provider | F20 |
| 232 | `oauth_bridge_integration.provider_form.saving` | Saving... | F20 |
| 233 | `oauth_bridge_integration.provider_form.update` | Update | F20 |
| 234 | `github_enterprise_integration.name` | GitHub Enterprise | F05 |
| 235 | `github_enterprise_integration.description` | Connect and sync your GitHub Enterprise organization with Plane. | F05 |
| 236 | `github_enterprise_integration.app_form_title` | GitHub Enterprise Configuration | F05 |
| 237 | `github_enterprise_integration.app_form_description` | Configure GitHub Enterprise to connect with Plane. | F05 |
| 238 | `github_enterprise_integration.app_id_title` | App ID | F05 |
| 239 | `github_enterprise_integration.app_id_description` | The ID of the app you created in your GitHub Enterprise organization. | F05 |
| 240 | `github_enterprise_integration.app_id_placeholder` | e.g., "1234567890" | F05 |
| 241 | `github_enterprise_integration.app_id_error` | App ID is required | F05 |
| 242 | `github_enterprise_integration.app_name_title` | App Slug | F05 |
| 243 | `github_enterprise_integration.app_name_description` | The slug of the app you created in your GitHub Enterprise organization. | F05 |
| 244 | `github_enterprise_integration.app_name_error` | App slug is required | F05 |
| 245 | `github_enterprise_integration.app_name_placeholder` | e.g., "plane-github-enterprise" | F05 |
| 246 | `github_enterprise_integration.base_url_title` | Base URL | F05 |
| 247 | `github_enterprise_integration.base_url_description` | The base URL of your GitHub Enterprise organization. | F05 |
| 248 | `github_enterprise_integration.base_url_placeholder` | e.g., "https://gh.plane.town" | F05 |
| 249 | `github_enterprise_integration.base_url_error` | Base URL is required | F05 |
| 250 | `github_enterprise_integration.invalid_base_url_error` | Invalid base URL | F05 |
| 251 | `github_enterprise_integration.client_id_title` | Client ID | F05 |
| 252 | `github_enterprise_integration.client_id_description` | The client ID of the app you created in your GitHub Enterprise organization. | F05 |
| 253 | `github_enterprise_integration.client_id_placeholder` | e.g., "1234567890" | F05 |
| 254 | `github_enterprise_integration.client_id_error` | Client ID is required | F05 |
| 255 | `github_enterprise_integration.client_secret_title` | Client Secret | F05 |
| 256 | `github_enterprise_integration.client_secret_description` | The client secret of the app you created in your GitHub Enterprise organization. | F05 |
| 257 | `github_enterprise_integration.client_secret_placeholder` | e.g., "1234567890" | F05 |
| 258 | `github_enterprise_integration.client_secret_error` | Client secret is required | F05 |
| 259 | `github_enterprise_integration.webhook_secret_title` | Webhook Secret | F05 |
| 260 | `github_enterprise_integration.webhook_secret_description` | The webhook secret of the app you created in your GitHub Enterprise organization. | F05 |
| 261 | `github_enterprise_integration.webhook_secret_placeholder` | e.g., "1234567890" | F05 |
| 262 | `github_enterprise_integration.webhook_secret_error` | Webhook secret is required | F05 |
| 263 | `github_enterprise_integration.private_key_title` | Private Key (Base64 encoded) | F05 |
| 264 | `github_enterprise_integration.private_key_description` | Base64 encoded private key of the app you created in your GitHub Enterprise organization. | F05 |
| 265 | `github_enterprise_integration.private_key_placeholder` | e.g., "MIIEpAIBAAKCAQEA... | F05 |
| 266 | `github_enterprise_integration.private_key_error` | Private key is required | F05 |
| 267 | `github_enterprise_integration.connect_app` | Connect App | F05 |
| 268 | `silo_errors.invalid_query_params` | The provided query parameters are invalid or missing required fields | F01 |
| 269 | `silo_errors.invalid_installation_account` | The installation account provided is not valid | F01 |
| 270 | `silo_errors.generic_error` | An unexpected error occurred while processing your request | F01 |
| 271 | `silo_errors.connection_not_found` | The requested connection could not be found | F01 |
| 272 | `silo_errors.multiple_connections_found` | Multiple connections were found when only one was expected | F01 |
| 273 | `silo_errors.cannot_create_multiple_connections` | You have already connected your organization with a workspace. Please disconnect the existing connection before connecting a new one. | F01 |
| 274 | `silo_errors.installation_not_found` | The requested installation could not be found | F01 |
| 275 | `silo_errors.user_not_found` | The requested user could not be found | F01 |
| 276 | `silo_errors.error_fetching_token` | Failed to fetch authentication token | F01 |
| 277 | `silo_errors.invalid_app_credentials` | The provided app credentials are invalid | F01 |
| 278 | `silo_errors.invalid_app_installation_id` | Failed to install the app | F01 |
| 279 | `import_status.queued` | Queued | F21 |
| 280 | `import_status.created` | Created | F21 |
| 281 | `import_status.initiated` | Initiated | F21 |
| 282 | `import_status.pulling` | Pulling | F21 |
| 283 | `import_status.timed_out` | Timed Out | F21 |
| 284 | `import_status.pulled` | Pulled | F21 |
| 285 | `import_status.progressing` | Progressing | F21 |
| 286 | `import_status.transforming` | Transforming | F21 |
| 287 | `import_status.transformed` | Transformed | F21 |
| 288 | `import_status.pushing` | Pushing | F21 |
| 289 | `import_status.finished` | Finished | F21 |
| 290 | `import_status.error` | Error | F21 |
| 291 | `import_status.cancelled` | Cancelled | F21 |

---

## Anhang B: Weitere i18n-Schlüssel dieses Clusters (vollständig je Präfix)

Automatisch extrahiert. Präfix-Filter je Datei; „Feature“ = Abschnitt in Kapitel 3.

| # | Datei | Schlüssel | Text (en, wörtlich) | Feature |
|---|---|---|---|---|
| 1 | `workspace-settings.json` | `workspace_settings.settings.integrations.title` | Integrations | F01 |
| 2 | `workspace-settings.json` | `workspace_settings.settings.integrations.heading` | Integrations | F01 |
| 3 | `workspace-settings.json` | `workspace_settings.settings.integrations.description` | Connect with popular tools and services to sync your work across your entire workflow ecosystem. | F01 |
| 4 | `workspace-settings.json` | `workspace_settings.settings.integrations.page_title` | Work with your Plane data in available apps or your own. | F01 |
| 5 | `workspace-settings.json` | `workspace_settings.settings.integrations.page_description` | View all the integrations in use by this workspace or you. | F01 |
| 6 | `workspace-settings.json` | `workspace_settings.settings.imports.title` | Imports | F21 |
| 7 | `workspace-settings.json` | `workspace_settings.settings.imports.heading` | Imports | F21 |
| 8 | `workspace-settings.json` | `workspace_settings.settings.imports.description` | Connect and import data from your existing project management tools to streamline your workflow integration. | F21 |
| 9 | `workspace-settings.json` | `workspace_settings.empty_state.imports.title` | No imports yet | F21 |
| 10 | `workspace-settings.json` | `workspace_settings.empty_state.imports.description` | Find all your previous imports here and download them. | F21 |
| 11 | `workspace-settings.json` | `workspace_settings.settings.applications.internal` | Internal | F47–F49 |
| 12 | `workspace-settings.json` | `workspace_settings.settings.applications.title` | Applications | F47–F49 |
| 13 | `workspace-settings.json` | `workspace_settings.settings.applications.applicationId_copied` | Application ID copied to clipboard | F47–F49 |
| 14 | `workspace-settings.json` | `workspace_settings.settings.applications.clientId_copied` | Client ID copied to clipboard | F47–F49 |
| 15 | `workspace-settings.json` | `workspace_settings.settings.applications.clientSecret_copied` | Client Secret copied to clipboard | F47–F49 |
| 16 | `workspace-settings.json` | `workspace_settings.settings.applications.third_party_apps` | Third-party apps | F47–F49 |
| 17 | `workspace-settings.json` | `workspace_settings.settings.applications.your_apps` | Your apps | F47–F49 |
| 18 | `workspace-settings.json` | `workspace_settings.settings.applications.connect` | Connect | F47–F49 |
| 19 | `workspace-settings.json` | `workspace_settings.settings.applications.connected` | Connected | F47–F49 |
| 20 | `workspace-settings.json` | `workspace_settings.settings.applications.disconnect` | Disconnect | F47–F49 |
| 21 | `workspace-settings.json` | `workspace_settings.settings.applications.install` | Install | F47–F49 |
| 22 | `workspace-settings.json` | `workspace_settings.settings.applications.installed` | Installed | F47–F49 |
| 23 | `workspace-settings.json` | `workspace_settings.settings.applications.configure` | Configure | F47–F49 |
| 24 | `workspace-settings.json` | `workspace_settings.settings.applications.app_available` | You have made this app available to use with a Plane workspace | F47–F49 |
| 25 | `workspace-settings.json` | `workspace_settings.settings.applications.app_credentials_regenrated.title` | App credentials successfully re-generated | F47–F49 |
| 26 | `workspace-settings.json` | `workspace_settings.settings.applications.app_credentials_regenrated.description` | Replace the client secret everywhere it's used. The previous secret is no longer valid. | F47–F49 |
| 27 | `workspace-settings.json` | `workspace_settings.settings.applications.app_created.title` | App created successfully | F47–F49 |
| 28 | `workspace-settings.json` | `workspace_settings.settings.applications.app_created.description` | Use the credentials to install the app in a Plane workspace | F47–F49 |
| 29 | `workspace-settings.json` | `workspace_settings.settings.applications.installed_apps` | Installed apps | F47–F49 |
| 30 | `workspace-settings.json` | `workspace_settings.settings.applications.all_apps` | All apps | F47–F49 |
| 31 | `workspace-settings.json` | `workspace_settings.settings.applications.internal_apps` | Internal apps | F47–F49 |
| 32 | `workspace-settings.json` | `workspace_settings.settings.applications.app_name_title` | App Name | F47–F49 |
| 33 | `workspace-settings.json` | `workspace_settings.settings.applications.app_description_title.label` | Long Description | F47–F49 |
| 34 | `workspace-settings.json` | `workspace_settings.settings.applications.app_description_title.placeholder` | Write a long description for marketplace. Press ‘/’ for commands. | F47–F49 |
| 35 | `workspace-settings.json` | `workspace_settings.settings.applications.authorization_grant_type.title` | Connection Type | F47–F49 |
| 36 | `workspace-settings.json` | `workspace_settings.settings.applications.authorization_grant_type.description` | Choose if your app should be installed once for the workspace or let every user connect their own account | F47–F49 |
| 37 | `workspace-settings.json` | `workspace_settings.settings.applications.website.title` | Website | F47–F49 |
| 38 | `workspace-settings.json` | `workspace_settings.settings.applications.website.description` | Link to your app's website. | F47–F49 |
| 39 | `workspace-settings.json` | `workspace_settings.settings.applications.website.placeholder` | https://example.com | F47–F49 |
| 40 | `workspace-settings.json` | `workspace_settings.settings.applications.app_maker.title` | App Maker | F47–F49 |
| 41 | `workspace-settings.json` | `workspace_settings.settings.applications.app_maker.description` | The person or organization creating the app. | F47–F49 |
| 42 | `workspace-settings.json` | `workspace_settings.settings.applications.app_maker_error` | Maker name is required | F47–F49 |
| 43 | `workspace-settings.json` | `workspace_settings.settings.applications.setup_url.label` | Setup URL | F47–F49 |
| 44 | `workspace-settings.json` | `workspace_settings.settings.applications.setup_url.description` | Users will be redirected to this URL when they install the app. | F47–F49 |
| 45 | `workspace-settings.json` | `workspace_settings.settings.applications.setup_url.placeholder` | https://example.com/setup | F47–F49 |
| 46 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_url.label` | Webhook URL | F47–F49 |
| 47 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_url.description` | This is where we will send webhook events and updates from the workspaces where your app is installed. | F47–F49 |
| 48 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_url.placeholder` | https://example.com/webhook | F47–F49 |
| 49 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_secret.label` | Webhook Secret | F47–F49 |
| 50 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_secret.description` | Secret used to verify incoming webhook requests. | F47–F49 |
| 51 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_secret.placeholder` | Enter a random secret key | F47–F49 |
| 52 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris.label` | Redirect URIs (space separated) | F47–F49 |
| 53 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris.description` | Users will be redirected to this path after they have authenticated with Plane. | F47–F49 |
| 54 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris.placeholder` | https://example.com https://example.com/ | F47–F49 |
| 55 | `workspace-settings.json` | `workspace_settings.settings.applications.app_available_description` | Connect a Plane workspace to start using it | F47–F49 |
| 56 | `workspace-settings.json` | `workspace_settings.settings.applications.client_id_and_secret` | Client ID and Secret | F47–F49 |
| 57 | `workspace-settings.json` | `workspace_settings.settings.applications.client_id_and_secret_description` | Copy and save this secret key in Pages. You can't see this key again after you hit Close. | F47–F49 |
| 58 | `workspace-settings.json` | `workspace_settings.settings.applications.client_id_and_secret_download` | You can download a CSV with the key from here. | F47–F49 |
| 59 | `workspace-settings.json` | `workspace_settings.settings.applications.application_id` | Application ID | F47–F49 |
| 60 | `workspace-settings.json` | `workspace_settings.settings.applications.client_id` | Client ID | F47–F49 |
| 61 | `workspace-settings.json` | `workspace_settings.settings.applications.client_secret` | Client Secret | F47–F49 |
| 62 | `workspace-settings.json` | `workspace_settings.settings.applications.export_as_csv` | Export as CSV | F47–F49 |
| 63 | `workspace-settings.json` | `workspace_settings.settings.applications.slug_already_exists` | Slug already exists | F47–F49 |
| 64 | `workspace-settings.json` | `workspace_settings.settings.applications.failed_to_create_application` | Failed to create application | F47–F49 |
| 65 | `workspace-settings.json` | `workspace_settings.settings.applications.upload_logo` | Upload Logo | F47–F49 |
| 66 | `workspace-settings.json` | `workspace_settings.settings.applications.app_name_error` | App name is required | F47–F49 |
| 67 | `workspace-settings.json` | `workspace_settings.settings.applications.app_short_description_title` | Short Description | F47–F49 |
| 68 | `workspace-settings.json` | `workspace_settings.settings.applications.app_short_description_error` | App short description is required | F47–F49 |
| 69 | `workspace-settings.json` | `workspace_settings.settings.applications.app_description_error` | App description is required | F47–F49 |
| 70 | `workspace-settings.json` | `workspace_settings.settings.applications.app_slug_title` | App slug | F47–F49 |
| 71 | `workspace-settings.json` | `workspace_settings.settings.applications.app_slug_error` | App slug is required | F47–F49 |
| 72 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_website_error` | Invalid website | F47–F49 |
| 73 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_url_title` | Webhook URL | F47–F49 |
| 74 | `workspace-settings.json` | `workspace_settings.settings.applications.webhook_url_error` | Webhook URL is required | F47–F49 |
| 75 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_webhook_url_error` | Invalid webhook URL | F47–F49 |
| 76 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris_title` | Redirect URIs | F47–F49 |
| 77 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris_error` | Redirect URIs are required | F47–F49 |
| 78 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_redirect_uris_error` | Invalid redirect URIs | F47–F49 |
| 79 | `workspace-settings.json` | `workspace_settings.settings.applications.redirect_uris_description` | Enter space seperated URIs where the app will redirect to after the user e.g https://example.com https://example.com/ | F47–F49 |
| 80 | `workspace-settings.json` | `workspace_settings.settings.applications.authorized_javascript_origins_title` | Authorized Javascript Origins | F47–F49 |
| 81 | `workspace-settings.json` | `workspace_settings.settings.applications.authorized_javascript_origins_error` | Authorized Javascript Origins are required | F47–F49 |
| 82 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_authorized_javascript_origins_error` | Invalid authorized Javascript Origins | F47–F49 |
| 83 | `workspace-settings.json` | `workspace_settings.settings.applications.authorized_javascript_origins_description` | Enter space seperated origins where the app will be allowed to make requests e.g app.com example.com | F47–F49 |
| 84 | `workspace-settings.json` | `workspace_settings.settings.applications.create_app` | Create app | F47–F49 |
| 85 | `workspace-settings.json` | `workspace_settings.settings.applications.update_app` | Update app | F47–F49 |
| 86 | `workspace-settings.json` | `workspace_settings.settings.applications.build_your_own_app` | Build your own app | F47–F49 |
| 87 | `workspace-settings.json` | `workspace_settings.settings.applications.edit_app_details` | Edit app details | F47–F49 |
| 88 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret_description` | Regenerate the client secret. If you regenerate the secret, you can copy the key or download it to a CSV file right after. | F47–F49 |
| 89 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret` | Regenerate client secret | F47–F49 |
| 90 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret_confirm_title` | Sure you want to regenerate the client secret? | F47–F49 |
| 91 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret_confirm_description` | App using this secret will stop working. You will need to update the secret in the app. | F47–F49 |
| 92 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret_confirm_cancel` | Cancel | F47–F49 |
| 93 | `workspace-settings.json` | `workspace_settings.settings.applications.regenerate_client_secret_confirm_regenerate` | Regenerate | F47–F49 |
| 94 | `workspace-settings.json` | `workspace_settings.settings.applications.read_only_access_to_workspace` | Read-only access to your workspace | F47–F49 |
| 95 | `workspace-settings.json` | `workspace_settings.settings.applications.write_access_to_workspace` | Write access to your workspace | F47–F49 |
| 96 | `workspace-settings.json` | `workspace_settings.settings.applications.read_only_access_to_user_profile` | Read-only access to your user profile | F47–F49 |
| 97 | `workspace-settings.json` | `workspace_settings.settings.applications.write_access_to_user_profile` | Write access to your user profile | F47–F49 |
| 98 | `workspace-settings.json` | `workspace_settings.settings.applications.connect_app_to_workspace` | Connect {app} to your workspace {workspace} | F47–F49 |
| 99 | `workspace-settings.json` | `workspace_settings.settings.applications.user_permissions` | User permissions | F47–F49 |
| 100 | `workspace-settings.json` | `workspace_settings.settings.applications.user_permissions_description` | User permissions are used to grant access to the user's profile. | F47–F49 |
| 101 | `workspace-settings.json` | `workspace_settings.settings.applications.workspace_permissions` | Workspace permissions | F47–F49 |
| 102 | `workspace-settings.json` | `workspace_settings.settings.applications.workspace_permissions_description` | Workspace permissions are used to grant access to the workspace. | F47–F49 |
| 103 | `workspace-settings.json` | `workspace_settings.settings.applications.with_the_permissions` | with the permissions | F47–F49 |
| 104 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_title` | {app} is requesting access to your Plane workspace and profile. | F47–F49 |
| 105 | `workspace-settings.json` | `workspace_settings.settings.applications.choose_workspace_to_connect_app_with` | Choose a workspace to connect the app with | F47–F49 |
| 106 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_workspace_permissions_title` | {app} would like | F47–F49 |
| 107 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_user_permissions_title` | {app} can also request a user's permission to the following resources. These permissions will be requested and authorized of and by a user only. | F47–F49 |
| 108 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_accept_title` | By accepting, you | F47–F49 |
| 109 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_accept_1` | Grant the app access to your Plane data wherever you can use the app in or outside Plane | F47–F49 |
| 110 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_accept_2` | Agree to {app}'s Privacy Policy and Terms Of Use | F47–F49 |
| 111 | `workspace-settings.json` | `workspace_settings.settings.applications.accepting` | Accepting... | F47–F49 |
| 112 | `workspace-settings.json` | `workspace_settings.settings.applications.accept` | Accept | F47–F49 |
| 113 | `workspace-settings.json` | `workspace_settings.settings.applications.categories` | Categories | F47–F49 |
| 114 | `workspace-settings.json` | `workspace_settings.settings.applications.select_app_categories` | Select app categories | F47–F49 |
| 115 | `workspace-settings.json` | `workspace_settings.settings.applications.categories_title` | Categories | F47–F49 |
| 116 | `workspace-settings.json` | `workspace_settings.settings.applications.categories_error` | Categories are required | F47–F49 |
| 117 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_categories_error` | Invalid categories | F47–F49 |
| 118 | `workspace-settings.json` | `workspace_settings.settings.applications.categories_description` | Select the categories that best describe the app | F47–F49 |
| 119 | `workspace-settings.json` | `workspace_settings.settings.applications.supported_plans` | Supported Plans | F47–F49 |
| 120 | `workspace-settings.json` | `workspace_settings.settings.applications.supported_plans_description` | Select the workspace plans that can install this application. Leave empty to allow all plans. | F47–F49 |
| 121 | `workspace-settings.json` | `workspace_settings.settings.applications.select_plans` | Select Plans | F47–F49 |
| 122 | `workspace-settings.json` | `workspace_settings.settings.applications.privacy_policy_url_title` | Privacy Policy URL | F47–F49 |
| 123 | `workspace-settings.json` | `workspace_settings.settings.applications.privacy_policy_url_error` | Privacy Policy URL is required | F47–F49 |
| 124 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_privacy_policy_url_error` | Invalid privacy policy URL | F47–F49 |
| 125 | `workspace-settings.json` | `workspace_settings.settings.applications.terms_of_service_url_title` | Terms of Service URL | F47–F49 |
| 126 | `workspace-settings.json` | `workspace_settings.settings.applications.terms_of_service_url_error` | Terms of Service URL is required | F47–F49 |
| 127 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_terms_of_service_url_error` | Invalid terms of service URL | F47–F49 |
| 128 | `workspace-settings.json` | `workspace_settings.settings.applications.support_url_title` | Support URL | F47–F49 |
| 129 | `workspace-settings.json` | `workspace_settings.settings.applications.support_url_error` | Support URL is required | F47–F49 |
| 130 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_support_url_error` | Invalid support URL | F47–F49 |
| 131 | `workspace-settings.json` | `workspace_settings.settings.applications.video_url_title` | Video URL | F47–F49 |
| 132 | `workspace-settings.json` | `workspace_settings.settings.applications.video_url_error` | Video URL is required | F47–F49 |
| 133 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_video_url_error` | Invalid video URL | F47–F49 |
| 134 | `workspace-settings.json` | `workspace_settings.settings.applications.setup_url_error` | Setup URL is required | F47–F49 |
| 135 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_setup_url_error` | Invalid setup URL | F47–F49 |
| 136 | `workspace-settings.json` | `workspace_settings.settings.applications.configuration_url_title` | Configuration URL | F47–F49 |
| 137 | `workspace-settings.json` | `workspace_settings.settings.applications.configuration_url_error` | Configuration URL is required | F47–F49 |
| 138 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_configuration_url_error` | Invalid configuration URL | F47–F49 |
| 139 | `workspace-settings.json` | `workspace_settings.settings.applications.contact_email_title` | Contact Email | F47–F49 |
| 140 | `workspace-settings.json` | `workspace_settings.settings.applications.contact_email_error` | Contact Email is required | F47–F49 |
| 141 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_contact_email_error` | Invalid contact email | F47–F49 |
| 142 | `workspace-settings.json` | `workspace_settings.settings.applications.upload_attachments` | Upload Attachments | F47–F49 |
| 143 | `workspace-settings.json` | `workspace_settings.settings.applications.uploading_images` | Uploading {count} Image{count, plural, one {s} other {s}} | F47–F49 |
| 144 | `workspace-settings.json` | `workspace_settings.settings.applications.drop_images_here` | Drop images here | F47–F49 |
| 145 | `workspace-settings.json` | `workspace_settings.settings.applications.click_to_upload_images` | Click to upload images | F47–F49 |
| 146 | `workspace-settings.json` | `workspace_settings.settings.applications.invalid_file_or_exceeds_size_limit` | Invalid file or exceeds size limit ({size} MB) | F47–F49 |
| 147 | `workspace-settings.json` | `workspace_settings.settings.applications.uploading` | Uploading... | F47–F49 |
| 148 | `workspace-settings.json` | `workspace_settings.settings.applications.upload_and_save` | Upload & Save | F47–F49 |
| 149 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_no_access_title` | Request to install | F47–F49 |
| 150 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_no_access_description` | This app can only be installed after a workspace admin installs it. Contact your workspace admin to proceed. | F47–F49 |
| 151 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_unapproved_title` | This app hasn't been reviewed or approved by Plane yet. | F47–F49 |
| 152 | `workspace-settings.json` | `workspace_settings.settings.applications.app_consent_unapproved_description` | Make sure you trust this app before connecting it to your workspace. | F47–F49 |
| 153 | `workspace-settings.json` | `workspace_settings.settings.applications.go_to_app` | Go to app | F47–F49 |
| 154 | `workspace-settings.json` | `workspace_settings.settings.applications.enable_app_mentions` | Enable App Mentions | F47–F49 |
| 155 | `workspace-settings.json` | `workspace_settings.settings.applications.enable_app_mentions_tooltip` | When this is enabled, Users can mention or assign Work Items to this application. | F47–F49 |
| 156 | `workspace-settings.json` | `workspace_settings.settings.applications.scopes` | Scopes | F47–F49 |
| 157 | `workspace-settings.json` | `workspace_settings.settings.applications.select_scopes` | Select Scopes | F47–F49 |
| 158 | `workspace-settings.json` | `workspace_settings.settings.applications.read_access_to` | Read-only access to | F47–F49 |
| 159 | `workspace-settings.json` | `workspace_settings.settings.applications.write_access_to` | Write access to | F47–F49 |
| 160 | `workspace-settings.json` | `workspace_settings.settings.applications.global_permission_expiration` | Global scopes are expiring soon. Use granular scopes instead. For example, use project:read instead of a global read. | F47–F49 |
| 161 | `workspace-settings.json` | `workspace_settings.settings.applications.selected_scopes` | {count} selected | F47–F49 |
| 162 | `workspace-settings.json` | `workspace_settings.settings.applications.scopes_and_permissions` | Scopes & Permissions | F47–F49 |
| 163 | `workspace-settings.json` | `workspace_settings.settings.applications.read` | Read | F47–F49 |
| 164 | `workspace-settings.json` | `workspace_settings.settings.applications.write` | Write | F47–F49 |
| 165 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.projects` | Access to projects, and all project related entities | F47–F49 |
| 166 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.wiki` | Access to wiki, and all wiki related entities | F47–F49 |
| 167 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.workspaces` | Access to workspaces, and all workspace related entities | F47–F49 |
| 168 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.stickies` | Access to stickies, and all sticky related entities | F47–F49 |
| 169 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.profile` | Access to user profile information | F47–F49 |
| 170 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.agents` | Access to agents, and all agent related entities | F47–F49 |
| 171 | `workspace-settings.json` | `workspace_settings.settings.applications.scope_description.assets` | Access to assets, and all asset related entities | F47–F49 |
| 172 | `workspace-settings.json` | `workspace_settings.settings.runners.title` | Plane Runner | F54 |
| 173 | `workspace-settings.json` | `workspace_settings.settings.runners.heading` | Scripts | F54 |
| 174 | `workspace-settings.json` | `workspace_settings.settings.runners.new_script` | New Script | F54 |
| 175 | `workspace-settings.json` | `workspace_settings.settings.runners.description` | Automate your workflows with custom scripts and automation rules. | F54 |
| 176 | `workspace-settings.json` | `workspace_settings.settings.plane-intelligence.title` | Plane AI | F33 |
| 177 | `workspace-settings.json` | `workspace_settings.settings.plane-intelligence.heading` | Plane AI | F33 |
| 178 | `workspace-settings.json` | `workspace_settings.settings.plane-intelligence.description` | See your work get smarter and faster with AI that is natively connected to your work and knowledge base.  | F33 |
| 179 | `workspace-settings.json` | `workspace_settings.copy_key` | Copy and save this secret key in Plane Pages. You can't see this key after you hit Close. A CSV file containing the key has been downloaded. | F52 |
| 180 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.heading` | Access Tokens | F52 |
| 181 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.description` | Generate secure API tokens to integrate your data with external systems and applications. | F52 |
| 182 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.title` | Access Tokens | F52 |
| 183 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.add_token` | Add access token | F52 |
| 184 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.create_token` | Create token | F52 |
| 185 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.never_expires` | Never expires | F52 |
| 186 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.generate_token` | Generate token | F52 |
| 187 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.generating` | Generating | F52 |
| 188 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.title` | Delete access token | F52 |
| 189 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.description` | Any application using this token will no longer have the access to Plane data. This action cannot be undone. | F52 |
| 190 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.success.title` | Success! | F52 |
| 191 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.success.message` | The token has been successfully deleted | F52 |
| 192 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.error.title` | Error! | F52 |
| 193 | `workspace-settings.json` | `workspace_settings.settings.api_tokens.delete.error.message` | The token could not be deleted | F52 |
| 194 | `workspace-settings.json` | `workspace_settings.empty_state.api_tokens.title` | No access tokens created | F52 |
| 195 | `workspace-settings.json` | `workspace_settings.empty_state.api_tokens.description` | Plane APIs can be used to integrate your data in Plane with any external system. Create a token to get started. | F52 |
| 196 | `workspace-settings.json` | `workspace_settings.settings.webhooks.heading` | Webhooks | F51 (CE-Basis) |
| 197 | `workspace-settings.json` | `workspace_settings.settings.webhooks.description` | Automate notifications to external services when project events occur. | F51 (CE-Basis) |
| 198 | `workspace-settings.json` | `workspace_settings.settings.webhooks.title` | Webhooks | F51 (CE-Basis) |
| 199 | `workspace-settings.json` | `workspace_settings.settings.webhooks.add_webhook` | Add webhook | F51 (CE-Basis) |
| 200 | `workspace-settings.json` | `workspace_settings.settings.webhooks.modal.title` | Create webhook | F51 (CE-Basis) |
| 201 | `workspace-settings.json` | `workspace_settings.settings.webhooks.modal.details` | Webhook details | F51 (CE-Basis) |
| 202 | `workspace-settings.json` | `workspace_settings.settings.webhooks.modal.payload` | Payload URL | F51 (CE-Basis) |
| 203 | `workspace-settings.json` | `workspace_settings.settings.webhooks.modal.question` | Which events would you like to trigger this webhook? | F51 (CE-Basis) |
| 204 | `workspace-settings.json` | `workspace_settings.settings.webhooks.modal.error` | URL is required | F51 (CE-Basis) |
| 205 | `workspace-settings.json` | `workspace_settings.settings.webhooks.secret_key.title` | Secret key | F51 (CE-Basis) |
| 206 | `workspace-settings.json` | `workspace_settings.settings.webhooks.secret_key.message` | Generate a token to sign-in to the webhook payload | F51 (CE-Basis) |
| 207 | `workspace-settings.json` | `workspace_settings.settings.webhooks.options.all` | Send me everything | F51 (CE-Basis) |
| 208 | `workspace-settings.json` | `workspace_settings.settings.webhooks.options.individual` | Select individual events | F51 (CE-Basis) |
| 209 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.created.title` | Webhook created | F51 (CE-Basis) |
| 210 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.created.message` | The webhook has been successfully created | F51 (CE-Basis) |
| 211 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_created.title` | Webhook not created | F51 (CE-Basis) |
| 212 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_created.message` | The webhook could not be created | F51 (CE-Basis) |
| 213 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.updated.title` | Webhook updated | F51 (CE-Basis) |
| 214 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.updated.message` | The webhook has been successfully updated | F51 (CE-Basis) |
| 215 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_updated.title` | Webhook not updated | F51 (CE-Basis) |
| 216 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_updated.message` | The webhook could not be updated | F51 (CE-Basis) |
| 217 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.removed.title` | Webhook removed | F51 (CE-Basis) |
| 218 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.removed.message` | The webhook has been successfully removed | F51 (CE-Basis) |
| 219 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_removed.title` | Webhook not removed | F51 (CE-Basis) |
| 220 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.not_removed.message` | The webhook could not be removed | F51 (CE-Basis) |
| 221 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.secret_key_copied.message` | Secret key copied to clipboard. | F51 (CE-Basis) |
| 222 | `workspace-settings.json` | `workspace_settings.settings.webhooks.toasts.secret_key_not_copied.message` | Error occurred while copying secret key. | F51 (CE-Basis) |
| 223 | `workspace-settings.json` | `workspace_settings.empty_state.webhooks.title` | No webhooks added | F51 (CE-Basis) |
| 224 | `workspace-settings.json` | `workspace_settings.empty_state.webhooks.description` | Create webhooks to receive real-time updates and automate actions. | F51 (CE-Basis) |
| 225 | `empty-state.json` | `settings_empty_state.workspace_tokens.title` | No Access tokens yet | F52 |
| 226 | `empty-state.json` | `settings_empty_state.workspace_tokens.description` | Generate secure API tokens to connect your workspace with external systems and applications. | F52 |
| 227 | `empty-state.json` | `settings_empty_state.workspace_tokens.cta_primary` | Add access token | F52 |
| 228 | `empty-state.json` | `settings_empty_state.tokens.title` | No Personal token yet | CE-Basis |
| 229 | `empty-state.json` | `settings_empty_state.tokens.description` | Generate secure API tokens to connect your workspace with external systems and applications. | CE-Basis |
| 230 | `empty-state.json` | `settings_empty_state.tokens.cta_primary` | Add access token | CE-Basis |
| 231 | `empty-state.json` | `settings_empty_state.webhooks.title` | No Webhook added yet | CE-Basis |
| 232 | `empty-state.json` | `settings_empty_state.webhooks.description` | Automate notifications to external services when project events occur. | CE-Basis |
| 233 | `empty-state.json` | `settings_empty_state.webhooks.cta_primary` | Add webhook | CE-Basis |
| 234 | `settings.json` | `account_settings.connections.title` | Connections | F01 |
| 235 | `settings.json` | `account_settings.connections.heading` | Connections | F01 |
| 236 | `settings.json` | `account_settings.connections.description` | Manage your workspace connections settings. | F01 |
| 237 | `settings.json` | `profile.actions.connections` | Connections | F01 |
| 238 | `settings.json` | `account_settings.api_tokens.title` | Personal Access Tokens | F52 (CE-Basis) |
| 239 | `settings.json` | `account_settings.api_tokens.description` | Generate secure API tokens to integrate your data with external systems and applications. | F52 (CE-Basis) |
| 240 | `project-settings.json` | `project_settings.empty_state.integrations.title` | No integrations configured | F01 |
| 241 | `project-settings.json` | `project_settings.empty_state.integrations.description` | Configure GitHub and other integrations to sync your project work items. | F01 |
| 242 | `navigation.json` | `sidebar.pi_chat` | Plane AI | F34 |
| 243 | `common.json` | `pi_chat` | Plane AI | F34 |
| 244 | `editor.json` | `ai_block.content.placeholder` | Describe the content of this block | F39 |
| 245 | `editor.json` | `ai_block.content.generated_here` | Your AI content will be generated here | F39 |
| 246 | `editor.json` | `ai_block.block_types.placeholder` | Select block type | F39 |
| 247 | `editor.json` | `ai_block.block_types.summarize_page` | Summarize Page | F39 |
| 248 | `editor.json` | `ai_block.block_types.custom_prompt` | Custom Prompt | F39 |
| 249 | `editor.json` | `ai_block.actions.discard` | Discard | F39 |
| 250 | `editor.json` | `ai_block.actions.generate` | Generate | F39 |
| 251 | `editor.json` | `ai_block.actions.generating` | Generating | F39 |
| 252 | `editor.json` | `ai_block.actions.rewriting` | Rewriting | F39 |
| 253 | `editor.json` | `ai_block.actions.rewrite` | Rewrite | F39 |
| 254 | `editor.json` | `ai_block.actions.use_this` | Use this | F39 |
| 255 | `editor.json` | `ai_block.actions.refine` | Refine | F39 |
| 256 | `tour.json` | `product_tour.mcp_connectors.step_zero.title` | Stop tab-switching. Connect your world. | F35 |
| 257 | `tour.json` | `product_tour.mcp_connectors.step_zero.description` | Link GitHub, Slack to track PRs and summarize chats directly in Plane AI. | F35 |
| 258 | `tour.json` | `get_started.checklist_section.checklist_items.item_5.title` | Try Plane AI chat | F01/F34 |
| 259 | `tour.json` | `get_started.checklist_section.checklist_items.item_6.title` | Link Integrations | F01/F34 |
| 260 | `tour.json` | `get_started.integrations_section.title` | Power up your workspace | F01/F34 |
| 261 | `tour.json` | `get_started.integrations_section.more_integrations` | Browse more integrations | F01/F34 |
| 262 | `automation.json` | `automations.action.handler_name.run_script` | Run Script | F54 |
| 263 | `automation.json` | `automations.action.run_script_block.title` | Run script | F54 |
| 264 | `workspace.json` | `workspace.members_import.title` | Import Members from CSV | F32 |
| 265 | `workspace.json` | `workspace.members_import.description` | Upload a CSV with columns: Email, Display Name, First Name, Last Name, Role (5, 15, or 20) | F32 |
| 266 | `workspace.json` | `workspace.members_import.dropzone.active` | Drop CSV file here | F32 |
| 267 | `workspace.json` | `workspace.members_import.dropzone.inactive` | Drag & drop or click to upload | F32 |
| 268 | `workspace.json` | `workspace.members_import.dropzone.file_type` | Only .csv files supported | F32 |
| 269 | `workspace.json` | `workspace.members_import.buttons.cancel` | Cancel | F32 |
| 270 | `workspace.json` | `workspace.members_import.buttons.import` | Import | F32 |
| 271 | `workspace.json` | `workspace.members_import.buttons.try_again` | Try Again | F32 |
| 272 | `workspace.json` | `workspace.members_import.buttons.close` | Close | F32 |
| 273 | `workspace.json` | `workspace.members_import.buttons.done` | Done | F32 |
| 274 | `workspace.json` | `workspace.members_import.progress.uploading` | Uploading... | F32 |
| 275 | `workspace.json` | `workspace.members_import.progress.importing` | Importing... | F32 |
| 276 | `workspace.json` | `workspace.members_import.summary.title.failed` | Import Failed | F32 |
| 277 | `workspace.json` | `workspace.members_import.summary.title.complete` | Import Complete | F32 |
| 278 | `workspace.json` | `workspace.members_import.summary.message.seat_limit` | Unable to import members due to seat limit restrictions. | F32 |
| 279 | `workspace.json` | `workspace.members_import.summary.message.success` | Successfully added {count} member{plural} to the workspace. | F32 |
| 280 | `workspace.json` | `workspace.members_import.summary.message.no_imports` | No members were imported from the CSV file. | F32 |
| 281 | `workspace.json` | `workspace.members_import.summary.stats.successful` | Successful | F32 |
| 282 | `workspace.json` | `workspace.members_import.summary.stats.failed` | Failed | F32 |
| 283 | `workspace.json` | `workspace.members_import.summary.download_errors` | Download errors | F32 |
| 284 | `workspace.json` | `workspace.members_import.toast.invalid_file.title` | Invalid file | F32 |
| 285 | `workspace.json` | `workspace.members_import.toast.invalid_file.message` | Only CSV files are supported. | F32 |
| 286 | `workspace.json` | `workspace.members_import.toast.import_failed.title` | Import failed | F32 |
| 287 | `workspace.json` | `workspace.members_import.toast.import_failed.message` | Something went wrong. | F32 |
| 288 | `project.json` | `project.members_import.title` | Import Members from CSV | F32 |
| 289 | `project.json` | `project.members_import.description` | Upload a CSV with columns: Email and Role (5=Guest, 15=Member, 20=Admin). Users must already be workspace members. | F32 |
| 290 | `project.json` | `project.members_import.download_sample` | Download sample CSV | F32 |
| 291 | `project.json` | `project.members_import.dropzone.active` | Drop CSV file here | F32 |
| 292 | `project.json` | `project.members_import.dropzone.inactive` | Drag & drop or click to upload | F32 |
| 293 | `project.json` | `project.members_import.dropzone.file_type` | Only .csv files supported | F32 |
| 294 | `project.json` | `project.members_import.buttons.cancel` | Cancel | F32 |
| 295 | `project.json` | `project.members_import.buttons.import` | Import | F32 |
| 296 | `project.json` | `project.members_import.buttons.try_again` | Try Again | F32 |
| 297 | `project.json` | `project.members_import.buttons.close` | Close | F32 |
| 298 | `project.json` | `project.members_import.buttons.done` | Done | F32 |
| 299 | `project.json` | `project.members_import.progress.uploading` | Uploading... | F32 |
| 300 | `project.json` | `project.members_import.progress.importing` | Importing... | F32 |
| 301 | `project.json` | `project.members_import.summary.title.complete` | Import Complete | F32 |
| 302 | `project.json` | `project.members_import.summary.message.success` | Successfully imported {count} member{plural} to the project. | F32 |
| 303 | `project.json` | `project.members_import.summary.message.no_imports` | No new members were imported from the CSV file. | F32 |
| 304 | `project.json` | `project.members_import.summary.stats.added` | Added | F32 |
| 305 | `project.json` | `project.members_import.summary.stats.reactivated` | Reactivated | F32 |
| 306 | `project.json` | `project.members_import.summary.stats.already_members` | Already Members | F32 |
| 307 | `project.json` | `project.members_import.summary.stats.skipped` | Skipped | F32 |
| 308 | `project.json` | `project.members_import.summary.download_errors` | Download skipped details | F32 |
| 309 | `project.json` | `project.members_import.toast.invalid_file.title` | Invalid file | F32 |
| 310 | `project.json` | `project.members_import.toast.invalid_file.message` | Only CSV files are supported. | F32 |
| 311 | `project.json` | `project.members_import.toast.import_failed.title` | Import failed | F32 |
| 312 | `project.json` | `project.members_import.toast.import_failed.message` | Something went wrong. | F32 |
| 313 | `work-item.json` | `issue.relation.duplicate` | Duplicate of | F42 |
| 314 | `inbox.json` | `inbox_issue.status.duplicate.title` | Duplicate | F42 |
| 315 | `inbox.json` | `inbox_issue.status.duplicate.description` | Duplicate | F42 |
| 316 | `inbox.json` | `inbox_issue.actions.mark_as_duplicate` | Mark as duplicate | F42 |
| 317 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.header` | Mobile details | F58 |
| 318 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.entity_id.label` | Entity ID \| Audience \| Metadata information | F58 |
| 319 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.entity_id.description` | We will generate this bit of the metadata that identifies this Plane app as an authorized service on your IdP. | F58 |
| 320 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.callback_url.label` | SSO URL | F58 |
| 321 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | F58 |
| 322 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.logout_url.label` | SLO URL | F58 |
| 323 | `auth.json` | `sso.providers.saml.setup_modal.mobile_details.logout_url.description` | We will generate this for you. Add this in the Logout redirect URL field of your IdP. | F58 |
| 324 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.header` | Mobile details | F58 |
| 325 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.origin_url.label` | Origin URL | F58 |
| 326 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.origin_url.description` | We will generate this for this Plane app. Add this as a trusted origin on your IdP's corresponding field. | F58 |
| 327 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.callback_url.label` | Redirect URL | F58 |
| 328 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | F58 |
| 329 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.logout_url.label` | Logout URL | F58 |
| 330 | `auth.json` | `sso.providers.oidc.setup_modal.mobile_details.logout_url.description` | We will generate this for you. Add this in the Logout redirect URL field of your IdP. | F58 |

Summe Anhang B: 330 Schlüssel.

---

## Anhang C: Externe Callback-/Webhook-Endpunkte der Integrationen (vollständig laut Doku)

Alle Pfade relativ zur Plane-Domain; im Original vom Dienst Silo unter Prefix `SILO_BASE_PATH` = `/silo` bedient. Empfehlung: in der Zielplattform **identisch** bereitstellen (Hersteller-Setup-Anleitungen bleiben gültig).

| # | Anbieter | Zweck | Methode/Pfad | Konfiguriert in | Quelle |
|---|---|---|---|---|---|
| 1 | GitHub (Cloud) | OAuth-Callback (Workspace/Org) und Setup-URL nach App-Installation | `GET /silo/api/github/auth/callback` | GitHub-App „Callback URL“ + „Setup URL“ | `DD/self-hosting/govern/integrations/github.md` |
| 2 | GitHub (Cloud) | OAuth-Callback persönliches Konto | `GET /silo/api/github/auth/user/callback` | GitHub-App „Callback URL“ | dto. |
| 3 | GitHub (Cloud) | Webhook-Empfang | `POST /silo/api/github/github-webhook` | GitHub-App „Webhook URL“ | dto. |
| 4 | GitHub Enterprise | OAuth-Callback + Setup-URL | `GET /silo/api/oauth/github-enterprise/auth/callback` | GHE-App | dto. |
| 5 | GitHub Enterprise | OAuth-Callback persönliches Konto | `GET /silo/api/oauth/github-enterprise/auth/user/callback` | GHE-App | dto. |
| 6 | GitHub Enterprise | Webhook-Empfang | `POST /silo/api/github-enterprise/github-webhook` | GHE-App | dto. |
| 7 | GitLab (Cloud) | OAuth-Redirect | `GET /silo/api/gitlab/auth/callback` | GitLab-Application „Redirect URI“ | `DD/self-hosting/govern/integrations/gitlab.md` |
| 8 | GitLab Self-managed | OAuth-Redirect | `GET /silo/api/oauth/gitlab-enterprise/auth/callback` | GitLab-Application | dto. |
| 9 | Bitbucket Cloud | OAuth-Callback | `GET /silo/api/oauth/bitbucket/auth/callback` | OAuth-Consumer | `DD/self-hosting/govern/integrations/bitbucket.md` |
| 10 | Bitbucket Data Center | OAuth-Redirect | `GET /silo/api/oauth/bitbucket-dc/auth/callback` | Application Link | dto. |
| 11 | Slack | Slash-Command `/plane` | `POST /silo/api/slack/command/` | Manifest `slash_commands[].url` | `DD/self-hosting/govern/integrations/slack.md` |
| 12 | Slack | OAuth Team (Bot-Installation) | `GET /silo/api/slack/team/auth/callback/` | Manifest `oauth_config.redirect_urls` | dto. |
| 13 | Slack | OAuth User (persönliches Konto) | `GET /silo/api/slack/user/auth/callback/` | Manifest `oauth_config.redirect_urls` | dto. |
| 14 | Slack | Events API (`link_shared`, `message.channels`, `message.im`) | `POST /silo/api/slack/events` | Manifest `settings.event_subscriptions.request_url` | dto. |
| 15 | Slack | Interactivity (Shortcuts, Modals, Buttons) | `POST /silo/api/slack/action/` | Manifest `settings.interactivity.request_url` | dto. |
| 16 | Slack | Dynamische Menü-Optionen | `POST /silo/api/slack/options/` | Manifest `settings.interactivity.message_menu_options_url` | dto. |
| 17 | Sentry | Webhook-Empfang (Issue-Events, Installation) | `POST /silo/api/sentry/sentry-webhook/` | Sentry-Integration „Webhook URL“ | `DD/self-hosting/govern/integrations/sentry.md` |
| 18 | Sentry | OAuth-Redirect | `GET /silo/api/oauth/sentry/auth/callback` | Sentry-Integration „Redirect URL“ | dto. |
| 19 | Sentry | UI-Komponente „Issue link“ | `POST /api/sentry/issues/link` (Auflösung relativ zur Integrations-Basis, OP-06) | Schema `elements[0].link.uri` | dto. |
| 20 | Sentry | Select „Issue“ | `GET /api/sentry/issues` | Schema `link.required_fields[0].uri` | dto. |
| 21 | Sentry | UI-Komponente „Issue create“ | `POST /api/sentry/issues/create` | Schema `create.uri` | dto. |
| 22 | Sentry | Select „Assignees“ | `GET /api/sentry/users` | Schema | dto. |
| 23 | Sentry | Select „Priorities“ | `GET /api/sentry/priorities` | Schema | dto. |
| 24 | Sentry | Select „Labels“ | `GET /api/sentry/labels` | Schema | dto. |
| 25 | Sentry | Select „State“ | `GET /api/sentry/states` | Schema | dto. |
| 26 | Sentry | Select „Module“ | `GET /api/sentry/modules` | Schema | dto. |
| 27 | Sentry | Select „Cycle“ | `GET /api/sentry/cycles` | Schema | dto. |
| 28 | Sentry | Select „Project“ | `GET /api/sentry/projects` | Schema | dto. |
| 29 | Sentry | Alert-Rule-Settings | `POST /api/sentry/alert-rule` | Schema `elements[1].settings.uri` | dto. |
| 30 | Silo | Liveness | `GET /silo/health/` (201) | Monitoring | `DD/self-hosting/manage/health-checks.md` |
| 31 | Silo | API-Konnektivität | `GET /silo/health/check-hmac` (201) | Monitoring | dto. |
| 32 | Silo | Readiness DB | `GET /silo/health/check-db` (200) | Monitoring | dto. |
| 33 | Plane AI | OAuth-Callback (PI als Plane-OAuth-Client) | `GET /pi/api/v1/oauth/callback/` | `PLANE_OAUTH_REDIRECT_URI` | `DD/self-hosting/govern/plane-ai/configure-plane-ai.md` |
| 34 | Plane AI | Liveness/Readiness/Health | `GET /pi/live/`, `GET /pi/ready/`, `GET /pi/health/`; veraltet `GET /pi/api/v1/health/`, `GET /pi/api/v2/health/` | Monitoring | `DD/self-hosting/manage/health-checks.md` |
| 35 | MCP-Server | Streamable HTTP (OAuth) | `/mcp/http/mcp` (Helm-Prefix `/mcp`) | MCP-Clients | `DD/dev-tools/mcp-server.md`; `HC/values.yaml` |
| 36 | MCP-Server | Streamable HTTP (PAT) | `/mcp/http/api-key/mcp` | MCP-Clients | dto. |
| 37 | MCP-Server | SSE (deprecated) | `/mcp/sse` | MCP-Clients | dto. |
| 38 | MCP-Server | OAuth-Callbacks | `/mcp/http/auth/callback`, `/mcp/auth/callback` | Plane-OAuth-App des MCP-Servers | `HC/README.md` Z. 1435 |
| 39 | MCP-Server | OAuth-Discovery | `/.well-known/oauth-protected-resource/mcp`, `/.well-known/oauth-authorization-server/mcp` | Ingress | `HC/templates/ingress-nginx.yaml` |
| 40 | Plane (OAuth-Server) | App-Autorisierung / Consent | `GET /auth/o/authorize-app/` (Build-a-Plane-App-Doku); `/auth/o/authorize/` (API-v2-Doku) | OAuth-Apps | `DD/dev-tools/build-plane-app/choose-token-flow.md`; `GH:` `authentication.md` |
| 41 | Plane (OAuth-Server) | Token (client_credentials, authorization_code, refresh_token) | `POST /auth/o/token/` | OAuth-Apps | dto. |
| 42 | Plane (OAuth-Server) | Installationsdetails | `GET /auth/o/app-installation/?id=<app_installation_id>` | OAuth-Apps | `choose-token-flow.md` |

**Umgebungsvariablen der Konnektoren (vollständig, Original):** GitHub `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_APP_NAME`, `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`; GitLab `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`; Bitbucket `BITBUCKET_CLIENT_ID`, `BITBUCKET_CLIENT_SECRET`, `BITBUCKET_WEBHOOK_SECRET`; Slack `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_BASE_URL`, `SLACK_SIGNING_SECRET`; Sentry `SENTRY_BASE_URL`, `SENTRY_CLIENT_ID`, `SENTRY_CLIENT_SECRET`, `SENTRY_INTEGRATION_SLUG`; HubSpot `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`; Cursor `CURSOR_WEBHOOK_SECRET`; Silo allgemein `SILO_BASE_PATH`, `SILO_BASE_URL`, `SILO_API_BASE_URL`, `SILO_HMAC_SECRET_KEY`, `AES_SECRET_KEY`, `AES_SALT`, `WEBHOOK_SECRET`, `BATCH_SIZE`, `DEDUP_INTERVAL`, `MQ_PREFETCH_COUNT`, `REQUEST_INTERVAL`, `IMPORTERS_QUEUE_NAME`, `INTEGRATION_CALLBACK_BASE_URL`, `JIRA_SERVER_ISSUES_PAGE_SIZE`, `JIRA_SERVER_ISSUES_PARALLEL_PAGES`, `AI_SERVICE_BASE_URL`, `APP_BASE_URL`, `API_BASE_URL`, `API_INTERNAL_BASE_URL`, `CORS_ALLOWED_ORIGINS` (`DD/self-hosting/govern/integrations/*.md`; `DD/self-hosting/govern/environment-variables.md` Z. 139–161, 257–266; `HC/templates/config-secrets/silo.yaml`). Im Ziel: App-Credentials zusätzlich im God Mode pflegbar (verschlüsselt in DB), Env-Variablen als Initialwerte.


---

## Anhang D: MCP-Server-Tool-Inventar

Quelle: `DD/dev-tools/mcp-server-tools.md` (automatisch extrahiert). Hersteller-Angabe: „28 tools, 183 actions, and 169 retired-name aliases“; die Tabellen der Doku enthalten 182 Aktionszeilen (Differenz von 1 nicht aufklärbar, OP-12-Umfeld). Spalten Required/Optional/Notes wörtlich.

| Gruppe | Tool | Bezeichnung | Anzahl | Aktionen |
|---|---|---|---|---|
| Work items | `workitem` | Work items | 12 | `list`, `list_archived`, `retrieve`, `retrieve_by_identifier`, `search`, `count`, `create`, `update`, `delete`, `archive`, `manage_assignee`, `manage_label` |
| Work items | `workitem_comment` | Work item comments | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Work items | `workitem_activity` | Work item activity | 2 | `list`, `retrieve` |
| Work items | `workitem_attachment` | Work item attachments | 5 | `list`, `read`, `download_url`, `upload_from_url`, `delete` |
| Work items | `workitem_link` | Work item links | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Work items | `workitem_relation` | Work item relations | 7 | `list`, `create`, `delete`, `list_definitions`, `create_definition`, `update_definition`, `delete_definition` |
| Work items | `work_log` | Work logs | 4 | `list`, `create`, `update`, `delete` |
| Types, properties and estimates | `workitem_type` | Work item types | 7 | `list`, `retrieve`, `resolve`, `create`, `update`, `delete`, `import_to_project` |
| Types, properties and estimates | `workitem_property` | Work item properties | 14 | `list`, `retrieve`, `create`, `update`, `delete`, `manage_type_properties`, `list_options`, `retrieve_option`, `create_option`, `update_option`, `delete_option`, `get_value`, `set_value`, `delete_value` |
| Types, properties and estimates | `project_estimate` | Project estimates | 9 | `retrieve`, `create`, `update`, `delete`, `link`, `list_points`, `create_points`, `update_point`, `delete_point` |
| Planning | `cycle` | Cycles | 11 | `list`, `retrieve`, `create`, `update`, `delete`, `list_workitems`, `manage_workitems`, `transfer_workitems`, `complete`, `archive`, `unarchive` |
| Planning | `module` | Modules | 9 | `list`, `retrieve`, `create`, `update`, `delete`, `list_workitems`, `manage_workitems`, `archive`, `unarchive` |
| Planning | `milestone` | Milestones | 7 | `list`, `retrieve`, `create`, `update`, `delete`, `list_workitems`, `manage_workitems` |
| Planning | `initiative` | Initiatives | 8 | `list`, `retrieve`, `create`, `update`, `delete`, `list_projects`, `add_projects`, `remove_projects` |
| Releases | `release` | Releases | 9 | `list`, `retrieve`, `create`, `update`, `delete`, `get_changelog`, `update_changelog`, `list_workitems`, `manage_workitems` |
| Releases | `release_tag` | Release tags | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Releases | `release_label` | Release labels | 6 | `list`, `create`, `update`, `delete`, `attach`, `detach` |
| Projects and workspace | `project` | Projects | 10 | `list`, `retrieve`, `create`, `update`, `delete`, `archive`, `unarchive`, `worklog_summary`, `get_features`, `update_features` |
| Projects and workspace | `state` | Workflow states | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Projects and workspace | `label` | Labels | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Projects and workspace | `member` | Members and roles | 5 | `me`, `list_workspace`, `list_project`, `list_roles`, `retrieve_role` |
| Projects and workspace | `workspace` | Workspace settings | 2 | `get_features`, `update_features` |
| Projects and workspace | `intake` | Intake queue | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Projects and workspace | `page` | Pages | 6 | `list`, `retrieve`, `create`, `list_workitem_pages`, `attach_to_workitem`, `detach_from_workitem` |
| Customers | `customer` | Customers | 7 | `list`, `retrieve`, `create`, `update`, `delete`, `list_workitems`, `manage_workitems` |
| Customers | `customer_request` | Customer requests | 5 | `list`, `retrieve`, `create`, `update`, `delete` |
| Customers | `customer_property` | Customer properties | 7 | `list`, `retrieve`, `create`, `update`, `delete`, `get_values`, `set_values` |
| Query | `get_pql_reference` | PQL reference | 0 |  |

Summe: 28 Tools, 182 Aktionszeilen.

### D.1 Aktionen mit Parametern (vollständig)

| Tool | Aktion | Required | Optional | Notes |
|---|---|---|---|---|
| `workitem` | `list` | — | `project_id`, `pql`, `order_by`, `per_page`, `cursor`, `expand`, `fields`, `external_id`, `external_source` | omit project_id to search the whole workspace; Read-only |
| `workitem` | `list_archived` | `project_id` | `pql`, `order_by`, `per_page`, `cursor`, `expand`, `fields`, `external_id`, `external_source` | Read-only |
| `workitem` | `retrieve` | `project_id`, `workitem_id` | `expand`, `fields`, `external_id`, `external_source`, `order_by` | Read-only |
| `workitem` | `retrieve_by_identifier` | `workitem_identifier` | `expand`, `fields`, `external_id`, `external_source`, `order_by` | identifier is PROJECT-N, e.g. ENG-42; Read-only |
| `workitem` | `search` | `query` | `expand`, `fields`, `external_id`, `external_source`, `order_by` | Read-only |
| `workitem` | `count` | — | `project_id`, `pql`, `group_by`, `sub_group_by` | counts the whole workspace unless project_id narrows it; Read-only |
| `workitem` | `create` | `project_id`, `name` | `assignees`, `labels`, `type_id`, `point`, `description_html`, `description_stripped`, `priority`, `start_date`, `target_date`, `sort_order`, `is_draft`, `parent`, `state`, `estimate_point`, `external_source`, `external_id` | — |
| `workitem` | `update` | `project_id`, `workitem_id` | `name`, `assignees`, `labels`, `type_id`, `point`, `description_html`, `description_stripped`, `priority`, `start_date`, `target_date`, `sort_order`, `is_draft`, `parent`, `state`, `estimate_point`, `external_source`, `external_id` | only the fields you pass are changed |
| `workitem` | `delete` | `project_id`, `workitem_id` | — | Destructive |
| `workitem` | `archive` | `project_id`, `workitem_id` | `archive` | archive defaults to true; pass archive=false to unarchive. Only completed or cancelled items can be archived |
| `workitem` | `manage_assignee` | `project_id`, `workitem_id` | `add_user_id`, `remove_user_id` | each takes one id or several; the list is merged, not replaced, and removals apply first |
| `workitem` | `manage_label` | `project_id`, `workitem_id` | `add_label_id`, `remove_label_id` | each takes one id or several; the list is merged, not replaced, and removals apply first |
| `workitem_comment` | `list` | `project_id`, `workitem_id` | `cursor`, `per_page` | Read-only |
| `workitem_comment` | `retrieve` | `project_id`, `workitem_id`, `comment_id` | — | Read-only |
| `workitem_comment` | `create` | `project_id`, `workitem_id`, `comment_html` | `access`, `external_source`, `external_id` | — |
| `workitem_comment` | `update` | `project_id`, `workitem_id`, `comment_id` | `comment_html`, `access`, `external_source`, `external_id` | — |
| `workitem_comment` | `delete` | `project_id`, `workitem_id`, `comment_id` | — | Destructive |
| `workitem_activity` | `list` | `project_id`, `workitem_id` | `cursor`, `per_page` | Read-only |
| `workitem_activity` | `retrieve` | `project_id`, `workitem_id`, `activity_id` | — | Read-only |
| `workitem_attachment` | `list` | `project_id`, `workitem_id` | — | Read-only |
| `workitem_attachment` | `read` | `project_id`, `workitem_id`, `attachment_id` | — | returns images and text inline; use download_url for anything else; Read-only |
| `workitem_attachment` | `download_url` | `project_id`, `workitem_id`, `attachment_id` | — | Read-only |
| `workitem_attachment` | `upload_from_url` | `project_id`, `workitem_id`, `url` | `name` | — |
| `workitem_attachment` | `delete` | `project_id`, `workitem_id`, `attachment_id` | — | Destructive |
| `workitem_link` | `list` | `project_id`, `workitem_id` | `cursor`, `per_page` | Read-only |
| `workitem_link` | `retrieve` | `project_id`, `workitem_id`, `link_id` | — | Read-only |
| `workitem_link` | `create` | `project_id`, `workitem_id`, `url` | — | — |
| `workitem_link` | `update` | `project_id`, `workitem_id`, `link_id`, `url` | — | — |
| `workitem_link` | `delete` | `project_id`, `workitem_id`, `link_id` | — | Destructive |
| `workitem_relation` | `list` | `project_id`, `workitem_id` | — | Read-only |
| `workitem_relation` | `create` | `project_id`, `workitem_id`, `workitem_ids` | `relation_type`, `relation_definition_id`, `relation_definition_label` | pass relation_type for a dependency, or definition id + label for a custom relation |
| `workitem_relation` | `delete` | `project_id`, `workitem_id`, `related_workitem_id` | `is_dependency` | removes one relation; dependencies and custom relations are independent, so is_dependency must match the kind that was created (default false); Destructive |
| `workitem_relation` | `list_definitions` | — | `is_default`, `is_active` | Read-only |
| `workitem_relation` | `create_definition` | `name` | `outward`, `inward`, `is_active`, `color` | — |
| `workitem_relation` | `update_definition` | `definition_id` | `name`, `outward`, `inward`, `is_active`, `color` | — |
| `workitem_relation` | `delete_definition` | `definition_id` | — | Destructive |
| `work_log` | `list` | `project_id`, `workitem_id` | `cursor`, `per_page` | Read-only |
| `work_log` | `create` | `project_id`, `workitem_id`, `duration` | `description` | — |
| `work_log` | `update` | `project_id`, `workitem_id`, `work_log_id` | `duration`, `description` | — |
| `work_log` | `delete` | `project_id`, `workitem_id`, `work_log_id` | — | Destructive |
| `workitem_type` | `list` | — | `project_id`, `cursor`, `per_page` | workspace scope when project_id is omitted; Read-only |
| `workitem_type` | `retrieve` | `workitem_type_id` | `project_id` | Read-only |
| `workitem_type` | `resolve` | `project_id`, `name` | — | finds or creates a named type usable in the project; never duplicates |
| `workitem_type` | `create` | `name` | `project_id`, `description`, `project_ids`, `is_active`, `external_source`, `external_id` | — |
| `workitem_type` | `update` | `workitem_type_id` | `project_id`, `name`, `description`, `project_ids`, `is_active`, `external_source`, `external_id` | only the fields you pass are changed |
| `workitem_type` | `delete` | `workitem_type_id` | `project_id` | Destructive |
| `workitem_type` | `import_to_project` | `project_id`, `workitem_type_ids` | — | links workspace types to a project |
| `workitem_property` | `list` | — | `project_id`, `workitem_type_id`, `cursor`, `per_page` | no ids lists every workspace property in one call -- the fast path for PQL; Read-only |
| `workitem_property` | `retrieve` | `workitem_property_id` | `project_id`, `workitem_type_id` | Read-only |
| `workitem_property` | `create` | `display_name`, `property_type` | `project_id`, `workitem_type_id`, `description`, `relation_type`, `is_required`, `is_multi`, `is_active`, `default_value`, `options`, `display_format`, `external_source`, `external_id` | — |
| `workitem_property` | `update` | `workitem_property_id` | `project_id`, `workitem_type_id`, `display_name`, `property_type`, `description`, `relation_type`, `is_required`, `is_multi`, `is_active`, `default_value`, `display_format`, `external_source`, `external_id` | only the fields you pass are changed |
| `workitem_property` | `delete` | `workitem_property_id` | `project_id`, `workitem_type_id` | Destructive |
| `workitem_property` | `manage_type_properties` | `workitem_type_id` | `project_id`, `attach_ids`, `detach_ids` | omit project_id where the workspace owns types; detach removes the association only, it does not delete the property |
| `workitem_property` | `list_options` | `property_id` | `project_id` | Read-only |
| `workitem_property` | `retrieve_option` | `property_id`, `option_id` | `project_id` | Read-only |
| `workitem_property` | `create_option` | `property_id`, `name` | `project_id`, `description`, `color`, `is_default`, `external_source`, `external_id` | — |
| `workitem_property` | `update_option` | `property_id`, `option_id` | `project_id`, `name`, `description`, `color`, `is_default`, `external_source`, `external_id` | — |
| `workitem_property` | `delete_option` | `property_id`, `option_id` | `project_id` | Destructive |
| `workitem_property` | `get_value` | `project_id`, `workitem_id`, `property_id` | — | Read-only |
| `workitem_property` | `set_value` | `project_id`, `workitem_id`, `property_id`, `value` | `external_source`, `external_id` | upsert; for a multi-value property this replaces every existing value |
| `workitem_property` | `delete_value` | `project_id`, `workitem_id`, `property_id` | — | Destructive |
| `project_estimate` | `retrieve` | `project_id` | — | a project has at most one estimate; Read-only |
| `project_estimate` | `create` | `project_id`, `name` | `type`, `description`, `last_used`, `external_source`, `external_id` | — |
| `project_estimate` | `update` | `project_id` | `name`, `description`, `external_source`, `external_id` | — |
| `project_estimate` | `delete` | `project_id` | — | Destructive |
| `project_estimate` | `link` | `project_id`, `estimate_id` | — | makes that estimate the project's active one |
| `project_estimate` | `list_points` | `project_id`, `estimate_id` | — | Read-only |
| `project_estimate` | `create_points` | `project_id`, `estimate_id`, `points` | — | — |
| `project_estimate` | `update_point` | `project_id`, `estimate_id`, `estimate_point_id` | `value`, `key`, `description`, `external_source`, `external_id` | — |
| `project_estimate` | `delete_point` | `project_id`, `estimate_id`, `estimate_point_id` | — | Destructive |
| `cycle` | `list` | `project_id` | `archived`, `status`, `cursor`, `per_page`, `order_by` | Read-only |
| `cycle` | `retrieve` | `project_id`, `cycle_id` | — | Read-only |
| `cycle` | `create` | `project_id`, `name`, `owned_by` | `description`, `start_date`, `end_date`, `timezone`, `external_source`, `external_id` | — |
| `cycle` | `update` | `project_id`, `cycle_id` | `name`, `description`, `start_date`, `end_date`, `owned_by`, `timezone`, `external_source`, `external_id` | only the fields you pass are changed |
| `cycle` | `delete` | `project_id`, `cycle_id` | — | Destructive |
| `cycle` | `list_workitems` | `project_id`, `cycle_id` | `pql`, `order_by`, `cursor`, `per_page`, `expand`, `fields` | Read-only |
| `cycle` | `manage_workitems` | `project_id`, `cycle_id` | `add_ids`, `remove_ids` | pass at least one of add_ids or remove_ids; returns nothing, read back with list_workitems |
| `cycle` | `transfer_workitems` | `project_id`, `cycle_id`, `new_cycle_id` | — | moves everything to new_cycle_id |
| `cycle` | `complete` | `project_id`, `cycle_id` | — | sets end_date to today |
| `cycle` | `archive` | `project_id`, `cycle_id` | — | ends the cycle first if it is still running |
| `cycle` | `unarchive` | `project_id`, `cycle_id` | — | — |
| `module` | `list` | `project_id` | `archived`, `cursor`, `per_page`, `order_by` | Read-only |
| `module` | `retrieve` | `project_id`, `module_id` | — | Read-only |
| `module` | `create` | `project_id`, `name` | `description`, `start_date`, `target_date`, `status`, `lead`, `members`, `external_source`, `external_id` | — |
| `module` | `update` | `project_id`, `module_id` | `name`, `description`, `start_date`, `target_date`, `status`, `lead`, `members`, `external_source`, `external_id` | only the fields you pass are changed |
| `module` | `delete` | `project_id`, `module_id` | — | Destructive |
| `module` | `list_workitems` | `project_id`, `module_id` | `pql`, `order_by`, `cursor`, `per_page`, `expand`, `fields` | Read-only |
| `module` | `manage_workitems` | `project_id`, `module_id` | `add_ids`, `remove_ids` | pass at least one of add_ids or remove_ids; returns nothing, read back with list_workitems |
| `module` | `archive` | `project_id`, `module_id` | — | — |
| `module` | `unarchive` | `project_id`, `module_id` | — | — |
| `milestone` | `list` | `project_id` | `cursor`, `per_page` | Read-only |
| `milestone` | `retrieve` | `project_id`, `milestone_id` | — | Read-only |
| `milestone` | `create` | `project_id`, `title` | `target_date`, `external_source`, `external_id` | — |
| `milestone` | `update` | `project_id`, `milestone_id` | `title`, `target_date`, `external_source`, `external_id` | only the fields you pass are changed |
| `milestone` | `delete` | `project_id`, `milestone_id` | — | Destructive |
| `milestone` | `list_workitems` | `project_id`, `milestone_id` | `cursor`, `per_page` | Read-only |
| `milestone` | `manage_workitems` | `project_id`, `milestone_id` | `add_ids`, `remove_ids` | pass at least one of add_ids or remove_ids; returns nothing, read back with list_workitems |
| `initiative` | `list` | — | — | returns every initiative; this endpoint does not paginate; Read-only |
| `initiative` | `retrieve` | `initiative_id` | — | Read-only |
| `initiative` | `create` | `name` | `description_html`, `start_date`, `end_date`, `state`, `lead` | — |
| `initiative` | `update` | `initiative_id` | `name`, `description_html`, `start_date`, `end_date`, `state`, `lead` | only the fields you pass are changed |
| `initiative` | `delete` | `initiative_id` | — | Destructive |
| `initiative` | `list_projects` | `initiative_id` | `cursor`, `per_page` | Read-only |
| `initiative` | `add_projects` | `initiative_id`, `project_ids` | — | returns nothing, read back with list_projects |
| `initiative` | `remove_projects` | `initiative_id`, `project_ids` | — | returns nothing, read back with list_projects; Destructive |
| `release` | `list` | — | `cursor`, `per_page` | Read-only |
| `release` | `retrieve` | `release_id` | — | Read-only |
| `release` | `create` | `name` | `description_html`, `status`, `release_date`, `target_date`, `tag_id`, `lead_id`, `is_prerelease`, `external_source`, `external_id` | — |
| `release` | `update` | `release_id` | `name`, `description_html`, `status`, `release_date`, `target_date`, `tag_id`, `lead_id`, `is_prerelease` | only the fields you pass are changed |
| `release` | `delete` | `release_id` | — | Destructive |
| `release` | `get_changelog` | `release_id` | — | Read-only |
| `release` | `update_changelog` | `release_id` | `description_html`, `description_stripped` | — |
| `release` | `list_workitems` | `release_id` | `cursor`, `per_page` | Read-only |
| `release` | `manage_workitems` | `release_id` | `add_ids`, `remove_ids` | pass at least one of add_ids or remove_ids; returns nothing, read back with list_workitems |
| `release_tag` | `list` | — | `cursor`, `per_page` | Read-only |
| `release_tag` | `retrieve` | `tag_id` | — | Read-only |
| `release_tag` | `create` | `version` | `description`, `commit_hash`, `git_tag` | — |
| `release_tag` | `update` | `tag_id` | `version`, `description`, `commit_hash`, `git_tag` | only the fields you pass are changed |
| `release_tag` | `delete` | `tag_id` | — | Destructive |
| `release_label` | `list` | — | `release_id`, `cursor`, `per_page` | the workspace palette unless release_id is given; Read-only |
| `release_label` | `create` | `name` | `color`, `sort_order` | adds to the workspace palette |
| `release_label` | `update` | `label_id` | `name`, `color`, `sort_order` | — |
| `release_label` | `delete` | `label_id` | — | removes it from the palette entirely; Destructive |
| `release_label` | `attach` | `release_id`, `label_ids` | — | returns nothing, read back with list |
| `release_label` | `detach` | `release_id`, `label_ids` | — | returns nothing, read back with list; Destructive |
| `project` | `list` | — | `cursor`, `per_page`, `order_by` | trimmed fields; use retrieve for full detail; Read-only |
| `project` | `retrieve` | `project_id` | — | Read-only |
| `project` | `create` | `name`, `identifier` | `description`, `project_lead`, `default_assignee`, `emoji`, `cover_image`, `timezone`, `archive_in`, `close_in`, `external_source`, `external_id` | — |
| `project` | `update` | `project_id` | `name`, `description`, `identifier`, `project_lead`, `default_assignee`, `emoji`, `cover_image`, `network`, `timezone`, `archive_in`, `close_in`, `default_state`, `estimate`, `is_time_tracking_enabled`, `external_source`, `external_id` | only the fields you pass are changed |
| `project` | `delete` | `project_id` | — | Destructive |
| `project` | `archive` | `project_id` | — | — |
| `project` | `unarchive` | `project_id` | — | — |
| `project` | `worklog_summary` | `project_id` | — | Read-only |
| `project` | `get_features` | `project_id` | — | Read-only |
| `project` | `update_features` | `project_id` | `modules`, `cycles`, `views`, `pages`, `intakes`, `workitem_types`, `epics`, `parallel_cycles`, `project_updates`, `workflows` | toggles project features on or off |
| `state` | `list` | `project_id` | `cursor`, `per_page` | Read-only |
| `state` | `retrieve` | `project_id`, `state_id` | — | Read-only |
| `state` | `create` | `project_id`, `name`, `color` | `description`, `sequence`, `group`, `is_triage`, `default`, `external_source`, `external_id` | — |
| `state` | `update` | `project_id`, `state_id` | `name`, `color`, `description`, `sequence`, `group`, `is_triage`, `default` | only the fields you pass are changed |
| `state` | `delete` | `project_id`, `state_id` | — | Destructive |
| `label` | `list` | `project_id` | `cursor`, `per_page` | Read-only |
| `label` | `retrieve` | `project_id`, `label_id` | — | Read-only |
| `label` | `create` | `project_id`, `name` | `color`, `description`, `parent`, `sort_order`, `external_source`, `external_id` | — |
| `label` | `update` | `project_id`, `label_id` | `name`, `color`, `description`, `parent`, `sort_order`, `external_source`, `external_id` | only the fields you pass are changed |
| `label` | `delete` | `project_id`, `label_id` | — | Destructive |
| `member` | `me` | — | — | the authenticated user; Read-only |
| `member` | `list_workspace` | — | `first_name`, `last_name`, `email`, `display_name`, `role_slug`, `is_active`, `is_bot`, `cursor`, `per_page`, `order_by` | name filters match case-insensitively and combine with AND; Read-only |
| `member` | `list_project` | `project_id` | — | Read-only |
| `member` | `list_roles` | — | `namespace`, `cursor`, `per_page` | Read-only |
| `member` | `retrieve_role` | `role_id` | — | Read-only |
| `workspace` | `get_features` | — | — | feature flags for the current workspace; Read-only |
| `workspace` | `update_features` | — | `project_grouping`, `initiatives`, `teams`, `customers`, `wiki`, `pi` | only the flags you pass are changed |
| `intake` | `list` | `project_id` | `cursor`, `per_page` | Read-only |
| `intake` | `retrieve` | `project_id`, `workitem_id` | — | Read-only |
| `intake` | `create` | `project_id`, `name` | `description_html`, `priority` | — |
| `intake` | `update` | `project_id`, `workitem_id` | `status`, `snoozed_till`, `duplicate_to`, `source`, `source_email` | pass status to make a triage decision |
| `intake` | `delete` | `project_id`, `workitem_id` | — | Destructive |
| `page` | `list` | — | `project_id`, `cursor`, `per_page` | workspace pages unless project_id is given; Read-only |
| `page` | `retrieve` | `page_id` | `project_id` | Read-only |
| `page` | `create` | `name`, `description_html` | `project_id`, `access`, `color`, `is_locked`, `external_source`, `external_id` | — |
| `page` | `list_workitem_pages` | `project_id`, `workitem_id` | — | Read-only |
| `page` | `attach_to_workitem` | `project_id`, `workitem_id`, `page_id` | — | — |
| `page` | `detach_from_workitem` | `project_id`, `workitem_id`, `workitem_page_id` | — | workitem_page_id is the link id from list_workitem_pages, not the page id; Destructive |
| `customer` | `list` | — | `query`, `cursor`, `per_page` | Read-only |
| `customer` | `retrieve` | `customer_id` | — | Read-only |
| `customer` | `create` | `name` | `description_html`, `email`, `website_url`, `domain`, `employees`, `stage`, `contract_status`, `revenue`, `external_source`, `external_id` | upsert: matches on external_source + external_id, else on name, so it never duplicates |
| `customer` | `update` | `customer_id` | `name`, `description_html`, `email`, `website_url`, `domain`, `employees`, `stage`, `contract_status`, `revenue`, `external_source`, `external_id` | only the fields you pass are changed |
| `customer` | `delete` | — | `customer_id`, `external_source`, `external_id` | address by customer_id, or by external_source plus external_id; Destructive |
| `customer` | `list_workitems` | `customer_id` | `customer_request_id`, `search` | Read-only |
| `customer` | `manage_workitems` | `customer_id` | `link_ids`, `unlink_ids`, `customer_request_id` | pass at least one of link_ids or unlink_ids; returns nothing, read back with list_workitems |
| `customer_request` | `list` | `customer_id` | `query`, `cursor`, `per_page` | Read-only |
| `customer_request` | `retrieve` | `customer_id`, `request_id` | — | Read-only |
| `customer_request` | `create` | `customer_id`, `name` | `description_html`, `link`, `workitem_ids` | workitem_ids can only be set here; change links afterwards with customer manage_workitems |
| `customer_request` | `update` | `customer_id`, `request_id` | `name`, `description_html`, `link` | only the fields you pass are changed |
| `customer_request` | `delete` | `customer_id`, `request_id` | — | Destructive |
| `customer_property` | `list` | — | `cursor`, `per_page` | Read-only |
| `customer_property` | `retrieve` | `property_id` | — | Read-only |
| `customer_property` | `create` | `display_name`, `property_type` | `relation_type`, `description`, `is_required`, `is_multi`, `is_active`, `default_value`, `options`, `display_format`, `external_source`, `external_id` | — |
| `customer_property` | `update` | `property_id` | `display_name`, `relation_type`, `description`, `is_required`, `is_multi`, `is_active`, `default_value`, `options`, `external_source`, `external_id` | only the fields you pass are changed |
| `customer_property` | `delete` | `property_id` | — | Destructive |
| `customer_property` | `get_values` | `customer_id` | `property_id` | omit property_id to read them all; Read-only |
| `customer_property` | `set_values` | `customer_id`, `values` | — | replaces the values of the properties named; others keep theirs |

### D.2 `get_pql_reference`

„Plane Query Language (PQL) syntax reference. Call this before composing a `pql` filter for the workitem list, list_archived or count actions.“ Parameter `detail`: `full` (Default; „operators, functions, common mistakes and worked examples“) oder `brief` („compact field and operator quick reference“); kein `action`-Parameter.

### D.3 Abgelöste Tool-Namen (Kompatibilität für bestehende Client-Konfigurationen)

„Plane MCP server 0.3.0 consolidated 177 per-operation tools into 28 resource tools. Of those 177 names, the 169 aliases below still resolve, stay hidden from tool listings, and accept their original parameter names; `get_pql_reference` is unchanged; and seven cannot be mapped to one action and instead return a message naming the replacement.“

| # | Alter Name | Ersatz | Art |
|---|---|---|---|
| 1 | `manage_customer_work_items` | `customer manage_workitems` with `link_ids` or `unlink_ids` | kein Alias (Hinweismeldung) |
| 2 | `manage_cycle_archive` | `cycle archive` or `cycle unarchive` | kein Alias (Hinweismeldung) |
| 3 | `manage_initiative_projects` | `initiative add_projects` or `initiative remove_projects` | kein Alias (Hinweismeldung) |
| 4 | `manage_module_archive` | `module archive` or `module unarchive` | kein Alias (Hinweismeldung) |
| 5 | `manage_project_archive` | `project archive` or `project unarchive` | kein Alias (Hinweismeldung) |
| 6 | `manage_release_labels` | `release_label attach` or `release_label detach` | kein Alias (Hinweismeldung) |
| 7 | `manage_release_work_items` | `release manage_workitems` with `add_ids` or `remove_ids` | kein Alias (Hinweismeldung) |
| 8 | `list_customers` | `customer list` | Alias |
| 9 | `retrieve_customer` | `customer retrieve` | Alias |
| 10 | `create_customer` | `customer create` | Alias |
| 11 | `update_customer` | `customer update` | Alias |
| 12 | `delete_customer` | `customer delete` | Alias |
| 13 | `list_customer_work_items` | `customer list_workitems` | Alias |
| 14 | `list_customer_properties` | `customer_property list` | Alias |
| 15 | `retrieve_customer_property` | `customer_property retrieve` | Alias |
| 16 | `create_customer_property` | `customer_property create` | Alias |
| 17 | `update_customer_property` | `customer_property update` | Alias |
| 18 | `delete_customer_property` | `customer_property delete` | Alias |
| 19 | `get_customer_property_values` | `customer_property get_values` | Alias |
| 20 | `set_customer_property_values` | `customer_property set_values` | Alias |
| 21 | `list_customer_requests` | `customer_request list` | Alias |
| 22 | `retrieve_customer_request` | `customer_request retrieve` | Alias |
| 23 | `create_customer_request` | `customer_request create` | Alias |
| 24 | `update_customer_request` | `customer_request update` | Alias |
| 25 | `delete_customer_request` | `customer_request delete` | Alias |
| 26 | `list_cycles` | `cycle list` | Alias |
| 27 | `retrieve_cycle` | `cycle retrieve` | Alias |
| 28 | `create_cycle` | `cycle create` | Alias |
| 29 | `update_cycle` | `cycle update` | Alias |
| 30 | `delete_cycle` | `cycle delete` | Alias |
| 31 | `list_cycle_work_items` | `cycle list_workitems` | Alias |
| 32 | `manage_cycle_work_items` | `cycle manage_workitems` | Alias |
| 33 | `transfer_cycle_work_items` | `cycle transfer_workitems` | Alias |
| 34 | `complete_cycle` | `cycle complete` | Alias |
| 35 | `list_initiatives` | `initiative list` | Alias |
| 36 | `retrieve_initiative` | `initiative retrieve` | Alias |
| 37 | `create_initiative` | `initiative create` | Alias |
| 38 | `update_initiative` | `initiative update` | Alias |
| 39 | `delete_initiative` | `initiative delete` | Alias |
| 40 | `list_initiative_projects` | `initiative list_projects` | Alias |
| 41 | `list_intake_work_items` | `intake list` | Alias |
| 42 | `retrieve_intake_work_item` | `intake retrieve` | Alias |
| 43 | `create_intake_work_item` | `intake create` | Alias |
| 44 | `update_intake_work_item` | `intake update` | Alias |
| 45 | `delete_intake_work_item` | `intake delete` | Alias |
| 46 | `list_labels` | `label list` | Alias |
| 47 | `retrieve_label` | `label retrieve` | Alias |
| 48 | `create_label` | `label create` | Alias |
| 49 | `update_label` | `label update` | Alias |
| 50 | `delete_label` | `label delete` | Alias |
| 51 | `get_me` | `member me` | Alias |
| 52 | `get_workspace_members` | `member list_workspace` | Alias |
| 53 | `get_project_members` | `member list_project` | Alias |
| 54 | `list_roles` | `member list_roles` | Alias |
| 55 | `retrieve_role` | `member retrieve_role` | Alias |
| 56 | `list_milestones` | `milestone list` | Alias |
| 57 | `retrieve_milestone` | `milestone retrieve` | Alias |
| 58 | `create_milestone` | `milestone create` | Alias |
| 59 | `update_milestone` | `milestone update` | Alias |
| 60 | `delete_milestone` | `milestone delete` | Alias |
| 61 | `list_milestone_work_items` | `milestone list_workitems` | Alias |
| 62 | `manage_milestone_work_items` | `milestone manage_workitems` | Alias |
| 63 | `list_modules` | `module list` | Alias |
| 64 | `retrieve_module` | `module retrieve` | Alias |
| 65 | `create_module` | `module create` | Alias |
| 66 | `update_module` | `module update` | Alias |
| 67 | `delete_module` | `module delete` | Alias |
| 68 | `list_module_work_items` | `module list_workitems` | Alias |
| 69 | `manage_module_work_items` | `module manage_workitems` | Alias |
| 70 | `list_pages` | `page list` | Alias |
| 71 | `retrieve_page` | `page retrieve` | Alias |
| 72 | `create_page` | `page create` | Alias |
| 73 | `list_work_item_pages` | `page list_workitem_pages` | Alias |
| 74 | `attach_page_to_work_item` | `page attach_to_workitem` | Alias |
| 75 | `detach_page_from_work_item` | `page detach_from_workitem` | Alias |
| 76 | `list_projects` | `project list` | Alias |
| 77 | `retrieve_project` | `project retrieve` | Alias |
| 78 | `create_project` | `project create` | Alias |
| 79 | `update_project` | `project update` | Alias |
| 80 | `delete_project` | `project delete` | Alias |
| 81 | `get_project_worklog_summary` | `project worklog_summary` | Alias |
| 82 | `update_project_features` | `project update_features` | Alias |
| 83 | `get_project_estimate` | `project_estimate retrieve` | Alias |
| 84 | `create_project_estimate` | `project_estimate create` | Alias |
| 85 | `update_project_estimate` | `project_estimate update` | Alias |
| 86 | `delete_project_estimate` | `project_estimate delete` | Alias |
| 87 | `link_estimate_to_project` | `project_estimate link` | Alias |
| 88 | `list_project_estimate_points` | `project_estimate list_points` | Alias |
| 89 | `create_project_estimate_points` | `project_estimate create_points` | Alias |
| 90 | `update_project_estimate_point` | `project_estimate update_point` | Alias |
| 91 | `delete_project_estimate_point` | `project_estimate delete_point` | Alias |
| 92 | `list_releases` | `release list` | Alias |
| 93 | `retrieve_release` | `release retrieve` | Alias |
| 94 | `create_release` | `release create` | Alias |
| 95 | `update_release` | `release update` | Alias |
| 96 | `delete_release` | `release delete` | Alias |
| 97 | `get_release_changelog` | `release get_changelog` | Alias |
| 98 | `update_release_changelog` | `release update_changelog` | Alias |
| 99 | `list_release_work_items` | `release list_workitems` | Alias |
| 100 | `list_release_labels` | `release_label list` | Alias |
| 101 | `create_release_label` | `release_label create` | Alias |
| 102 | `update_release_label` | `release_label update` | Alias |
| 103 | `delete_release_label` | `release_label delete` | Alias |
| 104 | `list_release_tags` | `release_tag list` | Alias |
| 105 | `retrieve_release_tag` | `release_tag retrieve` | Alias |
| 106 | `create_release_tag` | `release_tag create` | Alias |
| 107 | `update_release_tag` | `release_tag update` | Alias |
| 108 | `delete_release_tag` | `release_tag delete` | Alias |
| 109 | `list_states` | `state list` | Alias |
| 110 | `retrieve_state` | `state retrieve` | Alias |
| 111 | `create_state` | `state create` | Alias |
| 112 | `update_state` | `state update` | Alias |
| 113 | `delete_state` | `state delete` | Alias |
| 114 | `list_work_logs` | `work_log list` | Alias |
| 115 | `create_work_log` | `work_log create` | Alias |
| 116 | `update_work_log` | `work_log update` | Alias |
| 117 | `delete_work_log` | `work_log delete` | Alias |
| 118 | `list_work_items` | `workitem list` | Alias |
| 119 | `list_archived_work_items` | `workitem list_archived` | Alias |
| 120 | `retrieve_work_item` | `workitem retrieve` | Alias |
| 121 | `retrieve_work_item_by_identifier` | `workitem retrieve_by_identifier` | Alias |
| 122 | `search_work_items` | `workitem search` | Alias |
| 123 | `count_work_items` | `workitem count` | Alias |
| 124 | `create_work_item` | `workitem create` | Alias |
| 125 | `update_work_item` | `workitem update` | Alias |
| 126 | `delete_work_item` | `workitem delete` | Alias |
| 127 | `manage_work_item_archive` | `workitem archive` | Alias |
| 128 | `manage_work_item_assignee` | `workitem manage_assignee` | Alias |
| 129 | `manage_work_item_label` | `workitem manage_label` | Alias |
| 130 | `list_work_item_activities` | `workitem_activity list` | Alias |
| 131 | `retrieve_work_item_activity` | `workitem_activity retrieve` | Alias |
| 132 | `list_work_item_attachments` | `workitem_attachment list` | Alias |
| 133 | `read_work_item_attachment` | `workitem_attachment read` | Alias |
| 134 | `get_work_item_attachment_download_url` | `workitem_attachment download_url` | Alias |
| 135 | `upload_work_item_attachment_from_url` | `workitem_attachment upload_from_url` | Alias |
| 136 | `delete_work_item_attachment` | `workitem_attachment delete` | Alias |
| 137 | `list_work_item_comments` | `workitem_comment list` | Alias |
| 138 | `retrieve_work_item_comment` | `workitem_comment retrieve` | Alias |
| 139 | `create_work_item_comment` | `workitem_comment create` | Alias |
| 140 | `update_work_item_comment` | `workitem_comment update` | Alias |
| 141 | `delete_work_item_comment` | `workitem_comment delete` | Alias |
| 142 | `list_work_item_links` | `workitem_link list` | Alias |
| 143 | `retrieve_work_item_link` | `workitem_link retrieve` | Alias |
| 144 | `create_work_item_link` | `workitem_link create` | Alias |
| 145 | `update_work_item_link` | `workitem_link update` | Alias |
| 146 | `delete_work_item_link` | `workitem_link delete` | Alias |
| 147 | `list_work_item_properties` | `workitem_property list` | Alias |
| 148 | `retrieve_work_item_property` | `workitem_property retrieve` | Alias |
| 149 | `create_work_item_property` | `workitem_property create` | Alias |
| 150 | `update_work_item_property` | `workitem_property update` | Alias |
| 151 | `delete_work_item_property` | `workitem_property delete` | Alias |
| 152 | `manage_work_item_type_properties` | `workitem_property manage_type_properties` | Alias |
| 153 | `list_work_item_property_options` | `workitem_property list_options` | Alias |
| 154 | `retrieve_work_item_property_option` | `workitem_property retrieve_option` | Alias |
| 155 | `create_work_item_property_option` | `workitem_property create_option` | Alias |
| 156 | `update_work_item_property_option` | `workitem_property update_option` | Alias |
| 157 | `delete_work_item_property_option` | `workitem_property delete_option` | Alias |
| 158 | `get_work_item_property_value` | `workitem_property get_value` | Alias |
| 159 | `set_work_item_property_value` | `workitem_property set_value` | Alias |
| 160 | `delete_work_item_property_value` | `workitem_property delete_value` | Alias |
| 161 | `list_work_item_relations` | `workitem_relation list` | Alias |
| 162 | `create_work_item_relation` | `workitem_relation create` | Alias |
| 163 | `remove_work_item_relation` | `workitem_relation delete` | Alias |
| 164 | `list_work_item_relation_definitions` | `workitem_relation list_definitions` | Alias |
| 165 | `create_work_item_relation_definition` | `workitem_relation create_definition` | Alias |
| 166 | `update_work_item_relation_definition` | `workitem_relation update_definition` | Alias |
| 167 | `delete_work_item_relation_definition` | `workitem_relation delete_definition` | Alias |
| 168 | `list_work_item_types` | `workitem_type list` | Alias |
| 169 | `retrieve_work_item_type` | `workitem_type retrieve` | Alias |
| 170 | `resolve_work_item_type` | `workitem_type resolve` | Alias |
| 171 | `create_work_item_type` | `workitem_type create` | Alias |
| 172 | `update_work_item_type` | `workitem_type update` | Alias |
| 173 | `delete_work_item_type` | `workitem_type delete` | Alias |
| 174 | `import_work_item_types_to_project` | `workitem_type import_to_project` | Alias |
| 175 | `get_features` | `workspace get_features` | Alias |
| 176 | `update_workspace_features` | `workspace update_features` | Alias |

Summe D.3: 176 Einträge.

---

## Anhang E: OAuth-Scope-Inventar

### E.1 App-Scopes laut `DD/dev-tools/build-plane-app/oauth-scopes.md` (vollständig, automatisch extrahiert)

| Gruppe | Scope | Beschreibung (wörtlich) |
|---|---|---|
| Project scopes | `projects:read` | Read projects |
| Project scopes | `projects:write` | Create and update projects |
| Project scopes | `projects.features:read` | Read project features |
| Project scopes | `projects.features:write` | Create and update project features |
| Project scopes | `projects.members:read` | Read project members |
| Project scopes | `projects.members:write` | Manage project members |
| Project scopes | `projects.states:read` | Read project states |
| Project scopes | `projects.states:write` | Create and update project states |
| Project scopes | `projects.labels:read` | Read project labels |
| Project scopes | `projects.labels:write` | Create and update project labels |
| Project scopes | `projects.intakes:read` | Read project intakes |
| Project scopes | `projects.intakes:write` | Create and update project intakes |
| Project scopes | `projects.epics:read` | Read project epics |
| Project scopes | `projects.epics:write` | Create and update project epics |
| Project scopes | `projects.cycles:read` | Read project cycles |
| Project scopes | `projects.cycles:write` | Create and update project cycles |
| Project scopes | `projects.pages:read` | Read project pages |
| Project scopes | `projects.pages:write` | Create and update project pages |
| Project scopes | `projects.modules:read` | Read project modules |
| Project scopes | `projects.modules:write` | Create and update project modules |
| Project scopes | `projects.work_items:read` | Read project work items |
| Project scopes | `projects.work_items:write` | Create and update project work items |
| Project scopes | `projects.work_items.comments:read` | Read work item comments |
| Project scopes | `projects.work_items.comments:write` | Create and update work item comments |
| Project scopes | `projects.work_items.attachments:read` | Read work item attachments |
| Project scopes | `projects.work_items.attachments:write` | Create and update work item attachments |
| Project scopes | `projects.work_items.links:read` | Read work item links |
| Project scopes | `projects.work_items.links:write` | Create and update work item links |
| Project scopes | `projects.work_items.relations:read` | Read work item relations |
| Project scopes | `projects.work_items.relations:write` | Create and update work item relations |
| Project scopes | `projects.work_items.activities:read` | Read work item activities |
| Project scopes | `projects.work_items.activities:write` | Create and update work item activities |
| Project scopes | `projects.work_items.worklogs:read` | Read work item worklogs |
| Project scopes | `projects.work_items.worklogs:write` | Create and update work item worklogs |
| Project scopes | `projects.work_item_types:read` | Read work item types |
| Project scopes | `projects.work_item_types:write` | Create and update work item types |
| Project scopes | `projects.work_item_properties:read` | Read work item properties |
| Project scopes | `projects.work_item_properties:write` | Create and update work item properties |
| Project scopes | `projects.work_item_property_options:read` | Read work item property options |
| Project scopes | `projects.work_item_property_options:write` | Create and update work item property options |
| Project scopes | `projects.work_item_property_values:read` | Read work item property values |
| Project scopes | `projects.work_item_property_values:write` | Create and update work item property values |
| Project scopes | `projects.milestones:read` | Read project milestones |
| Project scopes | `projects.milestones:write` | Create and update project milestones |
| Wiki scopes | `wiki.pages:read` | Read wiki pages |
| Wiki scopes | `wiki.pages:write` | Create and update wiki pages |
| Customer scopes | `customers:read` | Read customers |
| Customer scopes | `customers:write` | Create and update customers |
| Customer scopes | `customers.requests:read` | Read customer requests |
| Customer scopes | `customers.requests:write` | Create and update customer requests |
| Customer scopes | `customers.properties:read` | Read customer properties |
| Customer scopes | `customers.properties:write` | Create and update customer properties |
| Customer scopes | `customers.property_values:read` | Read customer property values |
| Customer scopes | `customers.property_values:write` | Create and update customer property values |
| Customer scopes | `customers.work_items:read` | Read customer work items |
| Customer scopes | `customers.work_items:write` | Create and update customer work items |
| Initiatives scopes | `initiatives:read` | Read initiatives |
| Initiatives scopes | `initiatives:write` | Create and update initiatives |
| Initiatives scopes | `initiatives.projects:read` | Read initiative projects |
| Initiatives scopes | `initiatives.projects:write` | Create and update initiative projects |
| Initiatives scopes | `initiatives.epics:read` | Read initiative epics |
| Initiatives scopes | `initiatives.epics:write` | Create and update initiative epics |
| Initiatives scopes | `initiatives.labels:read` | Read initiative labels |
| Initiatives scopes | `initiatives.labels:write` | Create and update initiative labels |
| Workspace scopes | `workspaces.members:read` | Read workspace members |
| Workspace scopes | `workspaces.members:write` | Manage workspace members |
| Workspace scopes | `workspaces.features:read` | Read workspace features |
| Workspace scopes | `workspaces.features:write` | Create and update workspace features |
| Stickies scopes | `stickies:read` | Read stickies |
| Stickies scopes | `stickies:write` | Create and update stickies |
| Teamspaces scopes | `teamspaces:read` | Read teamspaces |
| Teamspaces scopes | `teamspaces:write` | Create and update teamspaces |
| Teamspaces scopes | `teamspaces.projects:read` | Read teamspace projects |
| Teamspaces scopes | `teamspaces.projects:write` | Create and update teamspace projects |
| Teamspaces scopes | `teamspaces.members:read` | Read teamspace members |
| Teamspaces scopes | `teamspaces.members:write` | Create and update teamspace members |
| Profile scopes | `profile:read` | Read user profile |
| Assets scopes | `assets:read` | Read assets |
| Assets scopes | `assets:write` | Create and update assets |
| Agent Run scopes | `agents.runs:read` | Read agent runs |
| Agent Run scopes | `agents.runs:write` | Create and update agent runs |
| Agent Run scopes | `agents.run_activities:read` | Read agent run activities |
| Agent Run scopes | `agents.run_activities:write` | Create and update agent run activities |

Summe E.1: 83 Scopes.

### E.2 Scopes der API v2 (Erstquelle `GH:` https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/authentication.md)

Regel: Eine Operation ist erlaubt, wenn der Token den **globalen** Scope (`read` bzw. `write`) **oder** den passenden Fein-Scope hat. Die Doku nennt die Liste ausdrücklich unvollständig („full OAuth scope catalog … served under `components.securitySchemes.oauth2` in `GET /api/v2/schema/`“). Persönliche API-Keys (`X-Api-Key`) sind nicht scope-begrenzt.

| # | Scope(s) |
|---|---|
| 1 | `assets:read`, `assets:write` |
| 2 | `automations:read`, `automations:write` |
| 3 | `customers:read`, `customers:write` |
| 4 | `customers.properties:read`, `customers.properties:write` |
| 5 | `customers.property_values:read`, `customers.property_values:write` |
| 6 | `customers.requests:read`, `customers.requests:write` |
| 7 | `initiatives:read`, `initiatives:write` |
| 8 | `initiatives.labels:read`, `initiatives.labels:write` |
| 9 | `projects:read`, `projects:write` |
| 10 | `projects.cycles:read`, `projects.cycles:write` |
| 11 | `projects.estimates:read`, `projects.estimates:write` |
| 12 | `projects.features:read`, `projects.features:write` |
| 13 | `projects.intakes:read`, `projects.intakes:write` |
| 14 | `projects.labels:read`, `projects.labels:write` |
| 15 | `projects.members:read`, `projects.members:write` |
| 16 | `projects.milestones:read`, `projects.milestones:write` |
| 17 | `projects.modules:read`, `projects.modules:write` |
| 18 | `projects.pages:read`, `projects.pages:write` |
| 19 | `projects.states:read`, `projects.states:write` |
| 20 | `projects.views:read`, `projects.views:write` |
| 21 | `projects.work_item_properties:read`, `projects.work_item_properties:write` |
| 22 | `projects.work_item_types:read`, `projects.work_item_types:write` |
| 23 | `projects.work_items:read`, `projects.work_items:write` |
| 24 | `projects.work_items.activities:read` |
| 25 | `projects.work_items.attachments:read`, `projects.work_items.attachments:write` |
| 26 | `projects.work_items.comments:read`, `projects.work_items.comments:write` |
| 27 | `projects.work_items.links:read`, `projects.work_items.links:write` |
| 28 | `projects.work_items.relations:read`, `projects.work_items.relations:write` |
| 29 | `projects.work_items.worklogs:read`, `projects.work_items.worklogs:write` |
| 30 | `projects.workflows:read`, `projects.workflows:write` |
| 31 | `releases:read`, `releases:write` |
| 32 | `releases.comments:read`, `releases.comments:write` |
| 33 | `releases.labels:read`, `releases.labels:write` |
| 34 | `releases.links:read`, `releases.links:write` |
| 35 | `releases.tags:read`, `releases.tags:write` |
| 36 | `stickies:read`, `stickies:write` |
| 37 | `teamspaces:read`, `teamspaces:write` |
| 38 | `templates.work_items:read`, `templates.work_items:write` |
| 39 | `webhooks:read`, `webhooks:write` |
| 40 | `wiki.pages:read`, `wiki.pages:write` |
| 41 | `workspaces.artifacts:read`, `workspaces.artifacts:write` |
| 42 | `workspaces.audit_logs:read` |
| 43 | `workspaces.features:read`, `workspaces.features:write` |
| 44 | `workspaces.group_sync:read`, `workspaces.group_sync:write` |
| 45 | `workspaces.members:read`, `workspaces.members:write` |
| 46 | `workspaces.roles:read` |
| 47 | `workspaces.views:read`, `workspaces.views:write` |
| 48 | `workspaces.work_item_properties:read`, `workspaces.work_item_properties:write` |
| 49 | `workspaces.work_item_relation_definitions:read`, `workspaces.work_item_relation_definitions:write` |
| 50 | `workspaces.work_item_types:read`, `workspaces.work_item_types:write` |
| 51 | `read`, `write` (globale Stufen; laut UI „Global scopes are expiring soon. Use granular scopes instead.“) |

**Abgleich E.1 ↔ E.2:** E.1 (App-Doku) enthält zusätzlich `agents.runs:read|write`, `agents.run_activities:read|write`, `profile:read`, `projects.epics:read|write`, `projects.work_items.activities:write`, `projects.work_item_property_options:read|write`, `projects.work_item_property_values:read|write`, `customers.work_items:read|write`, `initiatives.projects:read|write`, `initiatives.epics:read|write`, `teamspaces.projects:read|write`, `teamspaces.members:read|write`; E.2 enthält zusätzlich u. a. `automations:*`, `projects.estimates:*`, `projects.views:*`, `projects.workflows:*`, `releases*`, `templates.work_items:*`, `webhooks:*`, `workspaces.artifacts:*`, `workspaces.audit_logs:read`, `workspaces.group_sync:*`, `workspaces.roles:read`, `workspaces.views:*`, `workspaces.work_item_*`. Ziel: Vereinigungsmenge als Scope-Katalog (OpenIddict-Scopes) – Abgleich mit P02 §6.


---

## Verifikations-Protokoll

**Lauf:** Skeptiker/Verifizierer für Cluster P09, 22./23.10.2026. **Auftrag:** (a) Tier-Belege gegen `apps/web/components/workspace/billing/comparison/plans.tsx` und die Schwesterdokumente `20-…` bis `27-…` (inkl. `_data/P01…P07.paid.json`) prüfen, (b) CE-Status per grep im Repo prüfen, (c) fehlende Features ergänzen, (d) erfundene/übertriebene Beschreibungen korrigieren. Alle Korrekturen sind im Dokument mit „[Verifikation]“ markiert; die finale Feature-Liste steht in `migration/features/_data/P09.paid.json`.

### V.1 Methode

| Schritt | Vorgehen | Ergebnis |
|---|---|---|
| Plan-Matrix | `plans.tsx` vollständig gelesen (Sektionen `importers` Z. 936–962, `integrations` Z. 964–1024, `planHighlights` Z. 1303–1309); Rendering in `base.tsx` Z. 86/97 | Matrix-Angaben des Dokuments bestätigt; **Präzisierung:** `comingSoon: true` steht auf **Sektionsebene** „Integrations“ (Z. 966) und betrifft damit alle fünf Einträge (GitHub, Slack, Zapier, Zendesk, Freshdesk), nicht nur die letzten drei |
| Plan-Listen | `packages/constants/src/subscription.ts` Z. 25–32 (`PRO_PLAN_FEATURES` „Popular integrations“), Z. 43–48 (`FREE_PLAN_UPGRADE_FEATURES` „Integrations“) | bestätigt |
| Doku-Badges | `grep '<Badge'` über `DD/` | `integrations/{github,gitlab,bitbucket,slack,sentry}.md` = „Pro“; `plane-ai/configure-plane-ai.md`, `manage/health-checks.md`, `environment-variables.md` = „Commercial Edition“; `dev-tools/*` ohne Badge – bestätigt |
| Schwester-Abgleich | `20-…` bis `27-…` sowie `_data/P01/P02/P03/P05/P06/P07.paid.json` nach Cluster-Begriffen durchsucht | Abweichungen in V.4 dokumentiert |
| CE-grep | Routen (`apps/web/app/routes/{core,extended}.ts`, `apps/api/plane/app/urls/*.py`), Modelle, i18n-Referenzen außerhalb `packages/i18n/src/locales`, Stubs | Statuskorrekturen V-K06 bis V-K12 |
| i18n | `integration.json` per Skript gezählt (291 Schlüssel; Präfixe `integrations` 16, `github_integration` 45, `gitlab_integration` 39, `gitlab_enterprise_integration` 22, `slack_integration` 31, `sentry_integration` 16, `bitbucket_dc_integration` 2, `oauth_bridge_integration` 62, `github_enterprise_integration` 34, `silo_errors` 11, `import_status` 13); alle übrigen en-Dateien nach Cluster-Begriffen durchsucht | Anhang A vollständig (291 Zeilen); neu gefunden: `common.duplicate_issue_found`/`duplicate_issues_found` (F42) |
| Anhänge | Zeilenzählung per Skript | Anhang A 291, D.1 182 Aktionszeilen, D.3 176 Zeilen (169 Aliase + 7 Hinweisnamen), E.1 83 Scopes – bestätigt |
| Web | 14 WebSearch-Aufrufe (V.7), 1 direkter Abruf `raw.githubusercontent.com` (Artifacts) | Ergebnisse als `WEB(V09)` eingearbeitet |
| Screenshot | `IMG/webhooks/create-webhook.webp` selbst gesichtet | Sidebar „Features“/„Developer“ und Webhook-v2-Formular wie beschrieben bestätigt (Workspace mit Plan-Badge „Business“, Rolle Owner) |

### V.2 Korrekturen

| ID | Feature | vorher | nachher | Beleg |
|---|---|---|---|---|
| V-K01 | Tier-Konvention | – | Das JSON-Tier-Enum kennt keinen Wert „Free“. Konvention dieses Laufs: Importer mit Plan-Abstufung (F21, F22, F30) bleiben „Pro“ (konsistent mit Dok. 20 PF-83 und Dok. 22 P03-F22); Funktionen, die laut Doku auf **allen** Commercial-Plänen inkl. Free laufen (F24, F25, F29) oder ohne Plan nur „Cloud and Commercial Edition“ genannt sind (F23, F26, F27, F28), erhalten „unklar“ mit `tier_details` „ab Free …“ bzw. „Plan nicht genannt“ | `plans.tsx` Z. 940–960; `WEB(V09)` Importer-Doku |
| V-K02 | F26 ClickUp-Importer | „nicht belegt (nur Icon)“ | belegt: PAT, Workspace/Space/Folders, Prioritäten-Mapping, Projekte/Tasks/Mitglieder/Custom Fields/Anhänge/Kommentare | `WEB(V09)` https://docs.plane.so/importers/clickup ; Dok. 22 P03-F22; Dok. 26 S3 |
| V-K03 | F29 CSV-Importer | „nicht belegt“ | belegt inkl. Feldliste und Regeln; Flatfile als eigenes Feature F60 | `WEB(V09)` https://docs.plane.so/importers/csv , …/flatfile ; Dok. 22 O17 |
| V-K04 | F24/F25 Linear/Asana | Tier „unklar“, Details UNVERIFIZIERT | „all plans of the Commercial Edition“; Ablauf (PAT, Mappings, Confirm) | `WEB(V09)` https://docs.plane.so/importers/linear , …/asana |
| V-K05 | F28 Confluence | nur `entities.xml` | Widerspruch dokumentiert: Nutzer-Doku „Only HTML exports“ (ZIP) gilt für den Nachbau | `WEB(V09)` https://docs.plane.so/importers/confluence ; `HC/values.yaml` Z. 558–559 |
| V-K06 | F32 Mitglieder-CSV-Import | CE „fehlt“ | „Stub/UI-Hülle im CE“ (24 + 25 i18n-Schlüssel im CE ohne Code-Referenz) – gemäß Status-Legende dieses Dokuments | grep `members_import` |
| V-K07 | F33 Plane AI | CE „teilweise“ | „Stub/UI-Hülle im CE“; Basis-GPT separat in F40/F45 | grep `is_pi_enabled`, `plane-intelligence`, `pi_chat` |
| V-K08 | F39 AI im Editor | Tier „Pro/Business widersprüchlich“, CE „teilweise“ | Tier Pro (Selection-Aktionen, P07-27), AI-Block/Proposals Business (P07-28/29); CE „Stub“ (Extension `ai` deaktiviert, `rephrase-grammar` ohne Backend-Route) | `apps/web/hooks/use-editor-flagging.ts` Z. 37–45; `apps/web/services/ai.service.ts` Z. 43; Dok. 26 Z. 209–210 |
| V-K09 | F42 Duplicate Detection | CE „fehlt“, UI-Ort UNVERIFIZIERT | CE „Stub“; UI-Ort (Work-Item- und Intake-Create-Modal) aus CE-Stubs belegt | `packages/types/src/de-dupe.ts`; `apps/web/hooks/use-debounced-duplicate-issues.tsx`; `apps/web/components/issues/issue-modal/base.tsx` Z. 68, 382, 405; `apps/web/components/inbox/modals/create-modal/modal.tsx` Z. 23–46; `common.json` Z. 284–285; Dok. 20 PF-104 |
| V-K10 | F43 AI-Aktionen | CE „Stub (nur Icons)“; Funktionen sämtlich UNVERIFIZIERT | CE „fehlt“ (Icons nur im externen npm-Paket, gleiche Behandlung wie F19/F31 und Dok. 20 PF-105); Catch Up (Mobile) und Work-Item-Sofortzusammenfassung belegt; AI-Filter → Querverweis „Text to PQL“ (Dok. 24 P05-35) | `WEB(V09)` Mobile-Changelog v2.4.0, https://plane.so/issues |
| V-K11 | F52 Workspace-Access-Tokens | CE „Stub“ | „teilweise im CE“ (lauffähiger Token-Kern; Workspace-Bindung/Rolle fehlen) | `apps/api/plane/app/urls/api.py`; `apps/api/plane/app/views/api.py`; `apps/api/plane/db/models/api.py` Z. 35–36; `apps/web/components/api-token/delete-token-modal.tsx`; `apps/web/app/routes/core.ts` Z. 381–383 |
| V-K12 | F58 Mobile-Apps | CE „teilweise“; Umfang UNVERIFIZIERT | CE „Stub“ (Modelle/Felder ungenutzt); Plattformen, Voraussetzungen, Push nur Cloud, Changelog-Funktionen belegt | grep `Device`, `mobile_onboarding`, `mobile_details`; `WEB(V09)` https://docs.plane.so/devices/mobile |
| V-K13 | F57 Desktop-App | Plattformen/Umfang UNVERIFIZIERT | macOS/Linux, Tabs, Mehrfenster, Badge, Deep Links, Auto-Update, Commercial ≥ v3.0.0 | `WEB(V09)` https://docs.plane.so/devices/desktop , https://plane.so/download |
| V-K14 | F35 Connectors | Ort vermutet „Connections“ | Ort Integrations → Connectors, Authentifizierung je Nutzer, Beispiele GitHub/Sentry/Granola | `WEB(V09)` https://docs.plane.so/ai/mcp-connectors |
| V-K15 | F36 Skills | nur Existenz | Slash-Command-Prompts, Scopes personal/workspace/system | `WEB(V09)` https://docs.plane.so/ai/ai-skills |
| V-K16 | F38 eingebaute Agents | nur Existenz | Playbook, Skills, MCP-Tools, Scope, Trigger, Memory; Admin konfiguriert | `WEB(V09)` https://plane.so/blog/agents-are-now-live-in-plane |
| V-K17 | 1.3 Nr. 2, F15–F17 | „Coming soon“ nur bei Zapier/Zendesk/Freshdesk | gesamte Sektion „Integrations“ | `plans.tsx` Z. 966; `base.tsx` Z. 86 |
| V-K18 | F01 UI-Hinweise | Logo-Liste mit 14 Einträgen (unvollständig) | vollständiges Inventar 41 Logos `PROPEL/other-products/` | Verzeichnislisting Propel 0.7.3 |
| V-K19 | F34 Navigation | Key `pi_chat` | `user-menu.tsx` verwendet `pi-chat`, `sidebar-item.tsx` `pi_chat` – Abweichung vermerkt | `apps/web/components/workspace/sidebar/user-menu.tsx` Z. 56; `sidebar-item.tsx` Z. 52 |
| V-K20 | F33/F34 PI-API | Pfade außer Health/OAuth UNVERIFIZIERT | `/pi/api/v1/attachments/`, `/pi/api/v1/chat/stream-answer/` (SSE) belegt | `HC/templates/ingress-traefik.yaml` Z. 113–133 |
| V-K21 | F46 | `HC/values.yaml` Z. 1398–1399 | Z. 1401–1402 | `HC/values.yaml` |
| V-K22 | F33/F46 Credits | „höhere Pläne mehr (UNVERIFIZIERT)“ | Doku „per paid seat“, nicht gepoolt, Overage optional, nur Cloud; Drittquellen 500/1,000/2,000 (Free/Pro/Business) mit Widerspruch | `WEB(V09)` https://docs.plane.so/ai/plane-ai-credits |
| V-K23 | F44 Artifacts | `GH:` per Abruf-Werkzeug | erneut per direktem Abruf bestätigt; Abgrenzung zum Page-Block „HTML artifact“ (P07-37) | https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/artifacts/overview.md |

### V.3 Ergänzte Features

| ID | Feature | Grund |
|---|---|---|
| P09-F59 | draw.io-Integration (Querverweis) | in der Nutzer-Doku als native Integration gelistet; Aktivierung über Integrations; Detailspezifikation in Dok. 26 P07-21 / Dok. 22 P03-F31 |
| P09-F60 | Flatfile-Importer (Cloud-only, Beta) | eigene Doku-Seite; im Autoren-Inventar fehlend |
| P09-F61 | Plane AI: Autopilot-Modus | Mobile-Changelog v2.4.0 + Propel-Icons `AutopilotGo*`; im Autoren-Inventar fehlend |

Bewusst **nicht** als eigenes P09-Feature aufgenommen (Querverweis genügt): „Text to PQL“ (Dok. 24 P05-35), Public API v2 als Plattform (Dok. 21 / P02), PII-Scanner „Argus“ (Dok. 22 / Dok. 27), GraphQL- und Marketplace-Routen (Dok. 22 P03-F40), Page-Block „HTML artifact“ (Dok. 26 P07-37).

### V.4 Tier- und CE-Status-Abgleich je Feature (final)

| ID | Tier (JSON) | Tier-Beleg | CE-Status (final) | CE-Beleg / grep | Abgleich Schwesterdokumente |
|---|---|---|---|---|---|
| F01 | Pro | `plans.tsx` Z. 964–1024; `subscription.ts` Z. 31 | Stub | ungeroutete Seite `…/settings/(workspace)/integrations/page.tsx`; keine Route in `core.ts`/`extended.ts` | P03-F14 Pro/Stub ✓ |
| F02 | Pro | `plans.tsx` Z. 969–979; Badge `github.md` | Stub | Altmodelle `integration/github.py`, `use-integration-popup.tsx`, keine Backend-Route (`app/urls/*` ohne `github`) | P01 PF-84 Pro/Stub ✓; P03-F15 ✓ |
| F03 | Pro | wie F02 | Stub | nur i18n | ✓ |
| F04 | Pro | `plans.tsx` Z. 969–972 | Stub | Altmodelle `GithubIssueSync`, `GithubCommentSync` | ✓ |
| F05 | Pro | Badge gilt für ganze Seite `github.md` | Stub | nur i18n | P01 PF-84 „inkl. Enterprise“ Pro ✓ |
| F06 | Pro | Badge `gitlab.md` | Stub | nur i18n | P01 PF-85 Pro/„fehlt“ (Status-Konvention P01: i18n-only = fehlt; hier Legende „Stub“) |
| F07 | Pro | Badge `gitlab.md` | Stub | nur i18n | wie F06 |
| F08 | Pro | Badge `bitbucket.md` | Stub | i18n `bitbucket_dc_integration` | P01 PF-88 „fehlt“ (Konvention), P03-F17 Stub ✓ |
| F09 | Pro | `plans.tsx` Z. 980–990; Badge `slack.md` | Stub | Altmodell `SlackProjectSync`, Alt-UI | P01 PF-86 ✓; P03-F18 ✓ |
| F10 | Pro | wie F09 | Stub | nur i18n | ✓ |
| F11 | Pro | `plans.tsx` Z. 982 („use / commands in Slack“) | fehlt | keine Spur | ✓ |
| F12 | Pro | Badge `sentry.md`; `WEB(V09)` Sentry-Seite „Pro“ | Stub | nur i18n | P01 PF-87 „fehlt“ (Konvention); P03-F19 Stub ✓ |
| F13 | unklar | nur Helm | fehlt | – | P03-F20 ✓ |
| F14 | unklar | nur Helm-Secret | fehlt | – | P03-F21 ✓ |
| F15–F17 | Pro | `plans.tsx` Z. 991–1023 (Sektion Coming soon) | fehlt | – | P01 PF-89/90 ✓ |
| F18 | unklar | Negativbefund (Suche V-W05 ohne Treffer) | fehlt | – | – |
| F19 | unklar | nur Icon | fehlt | – | – |
| F20 | unklar | keine Plan-Angabe | Stub | nur i18n `oauth_bridge_integration` | P03-F09 Stub ✓; P01 PF-91 „fehlt“ (Konvention) |
| F21 | Pro (V-K01) | `plans.tsx` Z. 940–960 | Stub | Altmodell `Importer`, `IMPORTERS_LIST`, Services ohne Route | P03-F22 Pro/Stub ✓; P01 PF-83 Pro ✓ |
| F22 | Pro | `plans.tsx` Z. 940–949 | Stub | Typen `jira-importer.ts`, `jira.service.ts` | ✓ |
| F23 | unklar | Helm; Importer-Übersicht | fehlt | – | P03-F22 ✓ |
| F24/F25 | unklar (ab Free) | `WEB(V09)` „all plans of the Commercial Edition“ | fehlt | – | P03-F22 ✓ |
| F26 | unklar (Plan nicht genannt) | `WEB(V09)` | fehlt | – | P03-F22 ✓ (Korrektur V-K02) |
| F27/F28 | unklar | `WEB(P07)`, `WEB(V09)` | fehlt | – | ✓ |
| F29 | unklar (ab Free) | `WEB(V09)` | fehlt | nur Export | P03-F22 ✓ (Korrektur V-K03) |
| F30 | Pro | `plans.tsx` Z. 950–960 | Stub | Typen `github-importer.ts`, `github.service.ts` | ✓ |
| F31 | unklar | nur Icon | fehlt | – | – |
| F32 | unklar | keine Plan-Angabe | Stub | i18n ohne Referenz | P01 PF-60 „fehlt“ (Konvention) |
| F33 | Pro | `WEB(P01)` plane.so/pro; Credits „per paid seat“ | Stub | V-K07 | P01 PF-82 Pro/„teilweise“ ✗ (dokumentiert); P02 Pro/„fehlt“; P03-F12 Pro/Stub ✓ |
| F34 | Pro | wie F33 | Stub | `user-menu.tsx` ungenutzt, keine Route `pi-chat` | ✓ |
| F35–F38 | Pro | wie F33 (Skills-Doku: „available when Plane AI is enabled“) | Stub | i18n `tour.json`; Illustrationen `ai-skills`, `memory`, `ai-agents` (`asset-registry.tsx` Z. 91–93) | – |
| F39 | Pro | Dok. 26 P07-27 (Pro), P07-28/29 (Business) | Stub | V-K08 | P07-27 Stub ✓ |
| F40 | unklar | nur Changelog-Titel | teilweise | `description-editor.tsx` Z. 247–267 (lauffähig mit `has_llm_configured`); Route `ai-assistant/` (`app/urls/external.py`) | – |
| F41 | unklar | „Commercial Edition“-Badge | fehlt | – | P03-F13 ✓ |
| F42 | unklar | „Commercial Edition“ | Stub | V-K09 | P01 PF-104 Stub ✓; P03-F13 „fehlt“ ✗ (dokumentiert) |
| F43 | unklar | – | fehlt | V-K10 | P01 PF-105-Konvention ✓ |
| F44 | unklar | Plan-Feature „Applets“ (402) | fehlt | – | P02 unklar ✓ |
| F45 | unklar | „Commercial Edition“-Badge | teilweise | God-Mode `apps/admin/app/(all)/(dashboard)/ai/*`; `external/base.py` | – |
| F46 | Pro | Credits ab Pro (Cloud) | fehlt | – | – |
| F47 | unklar | „Cloud and Commercial Edition; Community Edition does not include it“ | Stub | nur i18n `applications.*` | P03-F25 Stub ✓; P01 PF-92/P02 „fehlt“ (Konvention) |
| F48 | unklar | – | Stub | nur i18n | P03-F40 ✓ |
| F49 | unklar | – | teilweise | `User.is_bot`/`bot_type`, Bot-Filter | – |
| F50 | unklar | Beta | Stub | i18n `scope_description.agents` | P03-F26 ✓; P02 „fehlt“ (Konvention) |
| F51 | unklar | Screenshot Business ist kein Mindest-Plan-Beleg | teilweise | Webhooks v1 (`db/models/webhook.py`, `bgtasks/webhook_task.py`) | P02/P03-F24 ✓ |
| F52 | unklar | – | teilweise | V-K11 | P01 PF-62 „fehlt“ ✗ (dokumentiert) |
| F53 | unklar | OAuth-Transport Commercial | teilweise | stdio + PAT gegen CE-API | P03-F27 ✓ |
| F54 | Enterprise Grid | Dok. 25 F19 (W24/W25) | Stub | i18n `runners.*`, Illustrationen | P06/P01 „fehlt“ (Konvention); P03-F28 Stub ✓ |
| F55 | unklar | – | fehlt | externer Client | P03-F43 ✓ |
| F56 | unklar | – | fehlt | externe Pakete | – |
| F57 | unklar | `WEB(V09)` Commercial ≥ v3.0.0 | Stub | `Device.DeviceType.DESKTOP`, Slug `desktop` | – |
| F58 | unklar (ab Free) | `WEB(V09)` | Stub | V-K12 | – |
| F59 | Business | Dok. 26 P07-21 | fehlt | CSS-Selektor | P03-F31 Pro ✗ → P07 gewählt |
| F60 | Cloud-only | `WEB(V09)` | fehlt | – | P03-F22/O17 ✓ |
| F61 | Pro | wie F33 | fehlt | nur Propel-Icons | – |

**Status-Konvention:** Dieses Dokument wendet seine eigene Legende an („Stub/UI-Hülle im CE = nur i18n-Texte, Icons, Illustrationen, ungenutzte Altmodelle/-komponenten“). Dok. 20 (P01) und Dok. 25 (P06) führen i18n-only-Funde häufig als „fehlt“; diese Abweichung ist rein klassifikatorisch. Icons, die **nur** im externen Paket `@makeplane/propel` liegen, werden – wie in Dok. 20 PF-105 – als „fehlt“ gewertet.

### V.5 Stichproben bestätigter Aussagen

Bestätigt durch eigene Lektüre: Silo-Konnektoren-Liste (`HC/values.yaml` Z. 555–612; `hubspot` Z. 609–612); `CURSOR_WEBHOOK_SECRET` (`HC/README.md` Z. 1088); Jira-Server-Variablen (`HC/values.yaml` Z. 1303–1304); MCP-Image `makeplane/plane-mcp-server:v0.3.2`, `path_prefix` `/mcp` (`HC/values.yaml` Z. 844–870); Agent-Queue `plane.agent` (Z. 1380); Runner-Image `makeplane/node-runner-commercial` (Z. 833); MCP „28 tools, 183 actions, 169 retired-name aliases“ (`DD/dev-tools/mcp-server-tools.md` Z. 13) und Plan-Gates (Z. 60–62); „Community Edition does not include it“ (`DD/dev-tools/mcp-server-self-host.md` Z. 18–21); Beta-Hinweise Apps/Agents; `pln_bot_`, `expires_in` 86400, `/auth/o/authorize-app/`, `/auth/o/app-installation/` (`choose-token-flow.md`); Agent-Status inkl. `stale` (5 min) (`building-an-agent.md` Z. 83, `best-practices.md` Z. 24, 347); Slack-Manifest (`/plane`, `link_shared`, `message.channels`, `message.im`, `message_menu_options_url`; `slack.md` Z. 66–119, 218–233); Sentry-Schema (Alert-Rule-Action „Create Plane Work Item or Intake Issue“, Typ `intake`/`work_item`; `sentry.md` Z. 165–204); Bitbucket-Scopes/Callbacks (`bitbucket.md` Z. 48–99); CE-AI (`external/base.py` Z. 26–75: Provider OpenAI/Anthropic/Gemini, Aufruf stets über `OpenAI`-Client Z. 131); `has_llm_configured` (`instance.py` Z. 139); `github_app_name`/`slack_client_id` (Z. 130/133); `EditorAIMenu` (Töne, 210/700 px; eingebunden in `editor-body.tsx` Z. 189); Importer-Altmodell (`importer.py` Z. 14–21); Webhook-v1-Retry (`webhook_task.py` Z. 238–239, `User-Agent: Autopilot` Z. 269, Timeout 30 s Z. 324); `APIToken` (`plane_api_`, `user_type`, `workspace`-FK; `api.py` Z. 20, 35–36); `Device`/`DeviceSession` (`device.py`); Bot-Anzeige „{first_name} Bot“ (`modules/links/list-item.tsx` Z. 104, `issue-detail/links/link-detail.tsx` Z. 118) und Bot-Filter (`workspace-member.store.ts` Z. 136, 147); `RESTRICTED_URLS` inkl. `silo`, `desktop`, `m`, `mobile`, `importers`, `integrations` (`packages/constants/src/workspace.ts` Z. 12–78).

### V.6 Verbleibende Widersprüche (dokumentiert, nach ADR-001 ohne Implementierungswirkung)

1. Confluence-Import: Nutzer-Doku „Only HTML exports“ vs. Helm-Kommentar `entities.xml` (F28).
2. draw.io: Business (Dok. 26 P07-21) vs. Pro (Dok. 22 P03-F31) – Business gewählt (F59).
3. Plane-AI-Credits: Doku „per paid seat“ vs. Drittquellen mit 500 Credits im Free-Plan (F33).
4. Desktop-App: Doku nennt Commercial ≥ v3.0.0, Download-Seite noch App-Version v2.0.0 und Windows „Coming soon“ (F57).
5. CE-Status-Konvention (i18n-only) zwischen Dok. 20/25 und diesem Dokument (V.4).
6. F33 CE-Status: Dok. 20 PF-82 „teilweise“ vs. hier „Stub“ (Basis-AI separat in F40/F45).

### V.7 WebSearch-Log (14 Suchen, Ergebnisse nur als Suchzusammenfassung)

| # | Suchanfrage (gekürzt) | Kernergebnis | eingearbeitet in |
|---|---|---|---|
| V-W01 | docs.plane.so importers ClickUp Linear Asana Notion Confluence CSV | Importer-Übersicht „Cloud and Commercial Edition“; ClickUp-, Confluence- (HTML-ZIP) und CSV-Seiten existieren | F21, F26, F28, F29 |
| V-W02 | Plane CSV importer Flatfile columns | CSV-Feldliste und Regeln; Flatfile nur Cloud, Beta; Changelog v3.3.0 | F29, F60 |
| V-W03 | Plane AI skills memory connectors MCP | Connectors unter Integrations → Connectors, je Nutzer, Beispiele GitHub/Sentry/Granola | F35 |
| V-W04 | Plane AI credits per seat | „per paid seat“, nicht gepoolt, Overage, nur Cloud; Drittquellen 500/1,000/2,000 | F33, F46 |
| V-W05 | plane.so marketplace integrations Zapier Teams Draw.io Figma Granola | draw.io native Integration; kein Beleg für Zapier, Teams, Figma, Granola-Integration | F15–F18, F59 |
| V-W06 | docs.plane.so/integrations/about plans | native Integrationen GitHub, GitHub Enterprise, draw.io, GitLab, Slack, Sentry; Sentry „Pro“ | 1.3, F12 |
| V-W07 | Plane AI skills memory changelog | Skills-Doku (Slash-Command, Scopes); Mobile-Changelog v2.4.0 | F36, F58 |
| V-W08 | docs.plane.so ai memory | kein Treffer | F37 (bleibt UNVERIFIZIERT) |
| V-W09 | Plane mobile app iOS Android | `docs.plane.so/devices/mobile`; App-Store-Eintrag | F58 |
| V-W10 | Plane desktop app | `docs.plane.so/devices/desktop`; Download-Seite | F57 |
| V-W11 | docs.plane.so importers linear jira-server notion asana | Linear-/Asana-Doku, „all plans of the Commercial Edition“, Abläufe | F23–F25, F27 |
| V-W12 | Plane AI built-in agents catch up summary | Agents-Blog (Playbook, Skills, MCP-Tools, Scope, Trigger, Memory); Work-Item-Sofortzusammenfassung | F38, F43 |
| V-W13 | Plane apps build your own access tokens plan | keine Plan-Angabe zu OAuth-Apps oder Tokens | F47, F52 (unverändert „unklar“) |
| V-W14 | Mobile-Changelog v2.4.0 autopilot catch up | Autopilot-Modus, Skills auf Mobile, Catch-Up-Widget; v2.5.0 Widgets, MCP-Connectoren, Plane AI für Self-hosted | F43, F58, F61 |
