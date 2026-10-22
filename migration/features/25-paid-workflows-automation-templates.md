# 25 – Bezahl-Features: Workflows, Approvals, Automationen, Templates, Recurring Work Items (Cluster P06)

> **Phase:** IST-Analyse (keine Implementierung). **Stand der Recherche:** 2026-10-21.
> **Basis-Repo:** `/home/user/plane` = Plane Community Edition v1.4.2 (`package.json`, Commit `38950eb4`), AGPL-3.0.
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere ADR-001 (keine Plan-Stufen, alle Features aktiv, Limits → Instanz-Einstellung), ADR-002 (kein Node.js zur Laufzeit), ADR-003 (Greenfield, Semantik bleibt), ADR-004 (Self-hosted/Airgapped, keine Pflicht-SaaS), ADR-005 (UI 1:1).

---

## 1. Überblick & Quellenlage

### 1.1 Gegenstand

Dieses Dokument spezifiziert **alle Funktionen des Clusters „Workflows, Automationen, Templates“, die NICHT in der Open-Source Community Edition (CE) enthalten sind**, sondern in den Bezahl-Editionen (Pro, Business, Enterprise bzw. heute „Enterprise Grid“). Zusätzlich werden die im CE vorhandenen Basisfunktionen (Auto-Archive/Auto-Close) vollständig beschrieben, weil die Bezahl-Editionen sie erweitern und die neue Plattform beide Ebenen in einem Modul vereint.

Der Code der Commercial Edition (`makeplane/plane-ee`, siehe `sources` in `/home/user/makeplane/helm-charts/charts/plane-enterprise/Chart.yaml`) ist **closed-source und nicht verfügbar**. Alle Bezahl-Features sind daher **clean-room aus öffentlichen Quellen** spezifiziert. Die neue Plattform muss sie nachbauen. Dabei gilt:

- **Verhalten und Texte** kommen aus öffentlichen Dokumenten (Docs, API-Referenz, Changelog, Blog) und aus den im CE **mitgelieferten EE-Texten** (`packages/i18n/src/locales/en/*.json`). Diese Texte sind die maßgebliche Quelle für die 1:1-UI (ADR-005).
- **Datenmodell und API** kommen aus der öffentlichen REST-API-Referenz v2 (`developers.plane.so/api-reference/v2/...`). Das ist der genaueste verfügbare Vertrag (Feldnamen in `snake_case`, Fehlercodes). ADR-003 fordert, dass die JSON-Verträge fachlich am Original orientiert sind.

### 1.2 Plan-Namen und Editionen

| Plan (Repo-Bezeichner) | Bedeutung | Quelle |
|---|---|---|
| `free` | Free / Community | `apps/web/components/workspace/billing/comparison/plans.tsx` (`PLANS_LIST`, `PLANE_PLANS.planDetails`) |
| `one` | „One“: Legacy-Self-hosted-Plan (Einmalpreis 799 „per workspace“) | `apps/web/components/workspace/billing/comparison/plans.tsx` |
| `pro` | Pro (8 $/Monat bzw. 6 $/Monat jährlich) | `apps/web/components/workspace/billing/comparison/plans.tsx` |
| `business` | Business („Talk to Sales“) | `apps/web/components/workspace/billing/comparison/plans.tsx` |
| `enterprise` | Enterprise. Heute vermarktet als **„Enterprise Grid“** (Top-Lizenz, nur auf Anfrage) | Repo: `plans.tsx`. Heute: https://plane.so/pricing, https://plane.so/blog/introducing-enterprise-grid |

**Wichtig:** Die Plan-Matrix im CE-Repo (`plans.tsx`) ist ein **älterer Stand** als die heutige öffentliche Doku. Seit 2026 ordnet Plane mehrere Funktionen anders zu: Custom Automations stehen in der Matrix unter „Pro“, in der Doku 2026 unter „Business“; Approvals stehen in der Matrix unter „Business (coming soon)“, in der Doku 2026 unter „Enterprise Grid“. Beide Zuordnungen sind in Tabelle 2 dokumentiert. **Für die Portierung ist die Zuordnung wegen ADR-001 nicht relevant**: alles ist immer aktiv. Sie dient nur der Nachvollziehbarkeit.

### 1.3 Quellenverzeichnis (Kürzel werden im Text verwendet)

**Repo (CE v1.4.2, Pfade relativ zum Repo-Root `/home/user/plane`)**

| Kürzel | Pfad | Inhalt |
|---|---|---|
| R1 | `apps/web/components/workspace/billing/comparison/plans.tsx` | Offizielle Feature×Plan-Matrix (`PLANS_COMPARISON_LIST`, `PLANE_PLANS.planHighlights`) |
| R2 | `packages/constants/src/subscription.ts` | Plan-Feature-Listen (`ENTERPRISE_PLAN_FEATURES`, `BUSINESS_PLAN_FEATURES`, `PRO_PLAN_FEATURES`, `ONE_PLAN_FEATURES`) |
| R3 | `packages/i18n/src/locales/en/workflow.json` | EE-Texte Workflows (1. Generation: Regeln pro State) |
| R4 | `packages/i18n/src/locales/en/automation.json` | EE-Texte Custom/Global Automations |
| R5 | `packages/i18n/src/locales/en/template.json` | EE-Texte Templates (Projekt/Work Item/Page, Marketplace-Publish) |
| R6 | `packages/i18n/src/locales/en/project-settings.json` | `project_settings.automations.*` (inkl. `auto-remind`), `project_settings.workflows.*` (2. Generation), `project_settings.templates.*`, `project_settings.cycles.auto_schedule.*` |
| R7 | `packages/i18n/src/locales/en/work-item.json` | `recurring_work_items.*`, `bulk_operations.error_details.invalid_state_transition` |
| R8 | `packages/i18n/src/locales/en/empty-state.json` | `settings_empty_state.templates|template_setting|recurring_work_items|workflows|work_item_types` |
| R9 | `packages/i18n/src/locales/en/workspace-settings.json` | `workspace_settings.settings.templates`, `workspace_settings.settings.runners` |
| R10 | `packages/i18n/src/locales/en/common.json` | `common.workflows`, `common.templates`, `common.recurring_work_items`, `common.automation`, `transition`, `activity_empty_state.no_transitions` |
| R11 | `packages/i18n/src/locales/en/power-k.json` | `power_k.creation_actions.create_project_automation` |
| R12 | `apps/web/components/workflow/use-workflow-drag-n-drop.ts`, `apps/web/components/workflow/index.ts` | CE-Stub des Workflow-Drag-and-Drop-Hooks |
| R13 | `apps/web/components/issues/issue-layouts/kanban/kanban-group.tsx`, `.../kanban/default.tsx`, `.../kanban/swimlanes.tsx`, `.../list/list-group.tsx`, `.../group-drag-overlay.tsx` | Aufrufstellen des Workflow-Hooks |
| R14 | `apps/web/components/dropdowns/state/state-select.tsx`, `packages/blocks/src/property-select/state-select.tsx` | Kommentar „CE change: EE reads a paginated state "lite" resource with workflow gating …“, Prop `allowedStateIds` |
| R15 | `apps/web/components/issues/issue-modal/context/issue-modal-context.tsx`, `.../issue-modal/provider.tsx`, `.../issue-modal/form.tsx`, `.../issue-modal/modal.tsx` | Work-Item-Template-Hooks (`workItemTemplateId`, `handleTemplateChange`, `isApplyingTemplate`) |
| R16 | `apps/web/components/project/create-project-modal.tsx`, `apps/web/components/projects/create/root.tsx`, `apps/web/components/project/create/header.tsx` | Projekt-Template-Hooks (`templateId`, `handleTemplateSelect`) |
| R17 | `apps/web/components/common/activity/helper.tsx` | Projekt-Activity für `is_workflow_enabled` („enabled/disabled custom workflow“) |
| R18 | `packages/constants/src/fetch-keys.ts` | `WORKSPACE_WORKFLOW_STATES`, `PROJECT_WORKFLOWS` |
| R19 | `packages/constants/src/state.ts` | `DISPLAY_WORKFLOW_PRO_CTA = false` |
| R20 | `apps/api/plane/bgtasks/issue_automation_task.py` | CE: `archive_and_close_old_issues`, `archive_old_issues`, `close_old_issues` |
| R21 | `apps/api/plane/celery.py` | Celery-Beat-Zeitplan |
| R22 | `apps/api/plane/db/models/project.py` | `Project.archive_in`, `close_in`, `default_state` |
| R23 | `apps/web/components/automation/auto-archive-automation.tsx`, `.../auto-close-automation.tsx`, `.../select-month-modal.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/automations/page.tsx` | CE-UI Automations-Seite |
| R24 | `packages/constants/src/project.ts` | `PROJECT_AUTOMATION_MONTHS` |
| R25 | `apps/api/plane/bgtasks/issue_activities_task.py` | Activity-Texte für Automation-Archivierung (`archived_at`) und `closed_to` |
| R26 | `apps/api/plane/db/models/issue_type.py` | `IssueType`, `ProjectIssueType` (im CE vorhanden, ohne Properties/Workflows) |
| R27 | `apps/api/plane/db/models/state.py` | `State`, `StateGroup`, `DEFAULT_STATES` |
| R28 | `packages/constants/src/settings/project.ts`, `packages/types/src/settings.ts`, `apps/web/app/routes/core.ts` | CE-Settings-Tabs und -Routen |
| R29 | npm `@makeplane/propel@0.7.3`, `dist/icons/...` (entpackt, nur gelesen) | Icons `WorkflowsOutline` (`project-features/workflows-outline.js`), `WorkflowsPropertyOutline` (`properties/workflows-outline.js`) [Verifikation: Pfadzuordnung korrigiert], `TimeInStateOutline` (`properties/time-in-state-outline.js`), `AutoArchiveOutline` (`actions/auto-archive-outline.js`, vom CE nicht genutzt – CE nimmt `RestoreOutline`), `AutoReminderOutline` (`actions/auto-reminder-outline.js`), `RulesOutline`, `VariableOutline`, `FunctionOutline`, `SandboxOutline` (`miscellaneous/*`; Verwendung im EE UNVERIFIZIERT), `ApproverOutline` (`miscellaneous/approver-outline.js`), `AutomationsOutline` (`miscellaneous/automations-outline.js`), `TriggerOutline` (`miscellaneous/trigger-outline.js`), `RecurringWorkItemsOutline` (`miscellaneous/recurring-work-items-outline.js`), `ScriptsOutline` (`project-features/scripts-outline.js`), `TemplatesOutline` (`workspace-features/templates-outline.js`), `LoopOutline` (`arrows/loop-outline.js`), `RepeatOutline` (`arrows/repeat-outline.js`), `GitBranchOutline` (`miscellaneous/git-branch-outline.js`), `AutoCloseOutline` (`actions/auto-close-outline.js`), `RestoreOutline` (`actions/restore-outline.js`), `WebhooksOutline` (`miscellaneous/webhooks-outline.js`), jeweils mit `*Filled`-Variante |
| R30 | `packages/blocks/src/empty-state/assets/asset-registry.tsx`, `.../asset-types.ts` | Empty-State-Illustrationen `template` (horizontal-stack), `workflow` (horizontal- und vertical-stack), `script`, `runner-scripts`, `runner-functions` (horizontal-stack; Plane Runner, F19) |
| R36 | `apps/web/components/issues/issue-layouts/utils.tsx` | CE-Quelle von `isDropDisabled`/`dropErrorMessage` je Gruppe (z. B. „Work item cannot be moved to completed cycles“) |
| R37 | `apps/web/components/automation/select-month-modal.tsx` | „Customize time range“-Dialog (Auto-Archive/-Close) |
| R31 | `apps/web/components/license/modal/upgrade-modal.tsx` | Upsell-Text „Dashboards, Workflows, Approvals, Time Management …“ |
| R32 | `apps/api/plane/bgtasks/webhook_task.py`, `apps/api/plane/db/models/webhook.py` | CE-Webhooks (HMAC-SHA256, Header `X-Plane-Signature`, `X-Plane-Delivery`, `X-Plane-Event`) |
| R33 | `apps/api/plane/db/models/issue.py` | `IssueManager` (`issue_objects`) |
| R34 | `apps/api/plane/db/models/intake.py` | `IntakeIssueStatus` |
| R35 | `apps/api/plane/db/models/user.py` | `User.is_bot`, `User.bot_type`, `BotTypeEnum` |

**Offline-Dokumentation**

| Kürzel | Pfad | Inhalt |
|---|---|---|
| D1 | `/home/user/makeplane/developer-docs/docs/dev-tools/plane-compose.md` | YAML-Schema für `workflows.yaml` (Transitions, Approvals), `states.yaml` (`allow_issue_creation`), `features.yaml` (`workflows`), `workitem_templates.yaml`, `page_templates.yaml` |
| D2 | `/home/user/makeplane/developer-docs/docs/self-hosting/govern/environment-variables.md` | `AUTOMATION_CONSUMER_REPLICAS`, `OUTBOX_POLLER_*`, `AUTOMATION_EVENT_STREAM_*`, RabbitMQ |
| D3 | `/home/user/makeplane/developer-docs/docs/self-hosting/manage/health-checks.md` | `node-runner` (Automation-Execution), `runnerctl/health` |
| D4 | `/home/user/makeplane/developer-docs/docs/self-hosting/methods/airgapped-edition.md` | Commercial-Images `automation-consumer`, `webhook-consumer`, `outbox-poller` |
| D5 | `/home/user/makeplane/developer-docs/docs/self-hosting/methods/kubernetes.md` | `services.automation_consumer.*`, `env.automation_consumer_envs.*` |
| D6 | `/home/user/makeplane/developer-docs/docs/api-reference/project/create-project-with-template.md` | `POST /api/v1/workspaces/{workspace_slug}/projects/templates/use/` |
| D7 | `/home/user/makeplane/developer-docs/docs/self-hosting/govern/high-availability.md` | Dienstliste inkl. `outbox_poller`, `automation_consumer`, `runner` |
| D8 | `/home/user/makeplane/developer-docs/docs/dev-tools/mcp-server-tools.md` | Project-Feature `workflows` (`update_features`) |
| D9 | `/home/user/makeplane/developer-docs/docs/api-reference/project/add-project.md` | `archive_in`, `close_in` |
| D10 | `/home/user/makeplane/developer-docs/docs/api-reference/project/overview.md` | Projekt-Objekt mit EE-Feld `template_id` („UUID of the project template used to create this project.“), `default_state` („used when the issues will be auto closed“) |
| D11 | `/home/user/makeplane/developer-docs/docs/public/images/webhooks/create-webhook.webp` | Screenshot Commercial-UI (Workspace mit Plan-Badge „Business“, Rolle Owner): Workspace-Settings-Sidebar Gruppe „Features“ = Projects, Integrations, **Plane Runner**, Connections, Teamspaces, Initiatives, Customers, Releases, **Templates**, Relations, Plane AI, **Automations**; Gruppe „Developer“ = Webhooks, Access Tokens |
| D12 | `/home/user/makeplane/developer-docs/docs/public/images/projects/project-automations.png` | Älterer Screenshot der Projekt-Automations-Seite (Texte noch „issues“, „Customize time range“ als Listeneintrag) |
| H1 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/templates/config-secrets/automations-consumer.yaml` | `AUTOMATION_EVENT_STREAM_QUEUE_NAME`, `…_PREFETCH`, `AUTOMATION_EXCHANGE_NAME`, `AUTOMATION_EVENT_TYPES` |
| H2 | `…/templates/config-secrets/outbox-poller.yaml` | `OUTBOX_POLLER_*` |
| H3 | `…/templates/config-secrets/runner-env.yaml` | `RUNNER_HMAC_SECRET_KEY`, `EXECUTION_TIMEOUT_MS`, `INIT_TIMEOUT_MS`, `ISOLATE_MEMORY_MB`, `API_BASE_URL`, `CONTROL_SERVICE_BASE_URL` |
| H4 | `…/templates/config-secrets/webhook-consumer.yaml` | `WEBHOOK_QUEUE_NAME`, `WEBHOOK_PREFETCH_COUNT` |
| H5 | `…/templates/workloads/automation-consumer.deployment.yaml`, `outbox-poller.deployment.yaml`, `runner.deployment.yaml`, `webhook-consumer.deployment.yaml` | Entrypoints `./bin/docker-entrypoint-automation-consumer.sh`, `…-outbox-poller.sh`, `…-webhook-consumer.sh`, Image `makeplane/node-runner-commercial` |
| H6 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/values.yaml`, `Chart.yaml` | Defaults, Chart 3.10.12, appVersion 3.3.3 |

**Web (Zugriff nur über WebSearch-Zusammenfassungen; docs.plane.so, plane.so und developers.plane.so sind per Netzwerk-Policy nicht direkt abrufbar, WebFetch scheitert mit `ENOTFOUND`)**

| Kürzel | URL |
|---|---|
| W1 | https://docs.plane.so/workflows-and-approvals/workflows |
| W2 | https://plane.so/blog/introducing-custom-workflows-and-approval-flows (11.06.2026) |
| W3 | https://docs.plane.so/workspace-administration/workspace-governance |
| W4 | https://plane.so/blog/introducing-workspace-governance (20.10.2026) |
| W5 | https://developers.plane.so/api-reference/v2/workflows/overview, …/workflows/create-workflow, …/workflows/update-workflow, …/workflows/preview-workflow-fallback |
| W6 | https://developers.plane.so/api-reference/v2/workflow-states/overview, …/create-workflow-state, …/update-workflow-state |
| W7 | https://developers.plane.so/api-reference/v2/workflow-transitions/overview, …/create-workflow-transition, …/list-workflow-transitions, …/update-workflow-transition |
| W8 | https://developers.plane.so/api-reference/v2/workspace-workflows/overview, …/create-workspace-workflow, …/update-workspace-workflow, …/get-workspace-workflow-usage |
| W9 | https://developers.plane.so/api-reference/v2/workspace-workflow-states/overview, …/update-workspace-workflow-state, …/add-workspace-workflow-states, …/mark-default-workspace-workflow-state, …/remove-workspace-workflow-state |
| W10 | https://developers.plane.so/api-reference/v2/workspace-workflow-transitions/overview, …/create-workspace-workflow-transition |
| W11 | https://developers.plane.so/api-reference/v2/workflow-hooks/overview, …/create-workflow-hook, …/list-workflow-hook-executions, …/regenerate-workflow-hook-secret |
| W12 | https://developers.plane.so/api-reference/v2/workspace-workflow-hooks/overview, …/create-workspace-workflow-hook |
| W13 | https://developers.plane.so/api-reference/v2/workflow-activities/overview, https://developers.plane.so/api-reference/v2/workspace-workflow-activities/overview |
| W14 | https://developers.plane.so/api-reference/v2/work-item-type-workflows/overview |
| W15 | https://developers.plane.so/api-reference/v2/work-item-type-governance/overview, …/create-work-item-type-workflow-pin |
| W16 | https://developers.plane.so/api-reference/v2/work-items/update-work-item |
| W17 | https://plane.so/workflows-and-approvals |
| W18 | https://plane.so/changelog/self-hosted-v1_9_0 |
| W19 | https://plane.so/changelog/release-v3-0-0-desktop-app-smarter-workflows-powerful-plane-ai-upgrades (14.07.2026) |
| W20 | https://plane.so/blog/new-work-item-detail-view-custom-relations-and-more |
| W21 | https://docs.plane.so/automations/custom-automations |
| W22 | https://docs.plane.so/automations/overview |
| W23 | https://plane.so/changelog/release-v-1-14-0-automations-recurring-work-and-integrations-for-self-running-projects (02.09.2025) |
| W24 | https://plane.so/blog/introducing-plane-runner-and-scheduled-automations |
| W25 | https://docs.plane.so/automations/plane-runner |
| W26 | https://plane.so/blog/designing-reliable-automation-when-to-use-rules-scripts-and-agents |
| W27 | https://plane.so/blog/introducing-enterprise-grid |
| W28 | https://developers.plane.so/api-reference/v2/project-automations/overview, …/create-project-automation, …/list-project-automations, …/set-project-automation-status, …/create-automation-node, …/create-automation-edge, …/list-automation-activities |
| W29 | https://developers.plane.so/api-reference/v2/workspace-automations/overview, …/list-workspace-automations, …/create-automation-node, …/update-automation-node, …/list-automation-nodes, …/set-workspace-automation-status, …/update-automation-edge |
| W30 | https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more |
| W31 | https://plane.so/changelog/2026-07-31-skills-plane-ai-richer-pages-audit-logs |
| W32 | https://plane.so/blog/building-zero-loss-event-streaming-with-postgresql-django-and-rabbitmq |
| W33 | https://docs.plane.so/templates/project-templates |
| W34 | https://docs.plane.so/templates/work-item-templates |
| W35 | https://docs.plane.so/templates/page-templates |
| W36 | https://developers.plane.so/api-reference/v2/project-templates/overview, …/create-project-template, …/update-project-template, …/use-project-template, …/copy-project-template, …/list-project-templates |
| W37 | https://developers.plane.so/api-reference/v2/project-work-item-templates/overview, …/create-project-work-item-template, …/use-work-item-template |
| W38 | https://developers.plane.so/api-reference/v2/workspace-work-item-templates/overview, …/create-workspace-work-item-template |
| W39 | https://developers.plane.so/api-reference/v2/workspace-page-templates/overview, https://developers.plane.so/api-reference/v2/project-page-templates/overview |
| W40 | https://plane.so/templates, https://plane.so/templates/39bcmn, https://plane.so/templates/website-updates-and-landing-pages |
| W41 | https://plane.so/changelog/2025-07-30-templates-initiatives |
| W42 | https://docs.plane.so/core-concepts/projects/recurring-work-items |
| W43 | https://developers.plane.so/api-reference/v2/recurring-work-items/overview, …/create-recurring-work-item, …/update-recurring-work-item |
| W44 | https://plane.so/changelog/2025-09-01-recurring-items-doc-imports-nested-pages |
| W45 | https://plane.so/pricing, https://plane.so/business, https://plane.so/enterprise-grid |
| W46 | https://docs.plane.so/communication-and-collaboration/notifications |
| W47 | https://plane.so/changelog/release-v2-6-0-pql-releases-wiki-collections-and-more |
| W48 | https://docs.plane.so/roles-and-permissions/permissions-matrix |
| W49 | https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles |
| W50 | https://plane.so/changelog/2026-03-31-vote-on-work-items-link-sub-work-items-across-projects |
| W51 | https://plane.so/changelog/2026-05-15-embed-media-in-the-editor-pql-in-dashboards-and-more |
| W52 | https://docs.plane.so/introduction/quickstart/enterprise-teams |

**Einschränkung der Quellenlage:** Alle W-Quellen wurden ausschließlich über Suchmaschinen-Zusammenfassungen gelesen, nicht im Volltext. Feldlisten und Fehlercodes aus der API-Referenz sind deshalb **mittel** belastbar. Wo die Zusammenfassungen sich widersprechen, ist das als **UNVERIFIZIERT** markiert. Die CE-i18n-Texte (R3 bis R11) sind wörtlich belastbar und decken die UI-Texte vollständig ab.

---

## 2. Feature-Tabelle

Legende CE-Status: **fehlt** = weder Backend noch UI im CE · **Stub/UI-Hülle** = Erweiterungspunkte, No-op-Hooks oder Texte im CE, keine Funktion · **teilweise** = Teilfunktion im CE · **im CE vorhanden** = Funktion im CE vollständig.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status (Repo-geprüft) | Quelle |
|---|---|---|---|---|---|
| F01 | Workflows: Default-Workflow je Projekt (erlaubte State-Wechsel, „by“/Reviewer, „Allow new work items“ je State, Erzwingung in allen UIs und APIs) | Business | Business: ein Default-Workflow je Projekt. Enterprise Grid: zusätzlich F02 bis F04. Repo: „Workflows + Approvals“ unter Business. **Widerspruch (Verifikation):** Schwester-Dok. `20-paid-spuren-im-repo.md` (PF-68, OP-02) zitiert eine WebSearch-Zusammenfassung von plane.so/pricing mit „a single workflow per project“ bereits für **Pro** – UNVERIFIZIERT, siehe O21 | Stub/UI-Hülle: No-op-Hook `useWorkFlowFDragNDrop` (R12, R13), `allowedStateIds` (R14), Texte (R3, R6), `DISPLAY_WORKFLOW_PRO_CTA` (R19), Fetch-Keys (R18). Kein Modell, keine API, keine Route (R28) | R2, R3, R6, W1, W18, W45 |
| F02 | Mehrere Workflows je Projekt, typ-spezifisch (Work Item Type → Workflow, Fallback auf Default) | Enterprise Grid | Business: nur Default. Enterprise Grid: beliebig viele, je WIT | Stub/UI-Hülle (nur Texte `project_settings.workflows.*` in R6, `settings_empty_state.workflows` in R8) | W1, W2, W19, W45 |
| F03 | Approval Flows (Genehmigungs-Gate an einer Transition: Approver, `required_approvals`, Ziel- und Ablehnungs-State) | Enterprise Grid | Doku 2026: Enterprise Grid. Repo-Matrix: „Approvals“ Business (coming soon), Repo-Liste: „Workflows + Approvals“ Business | fehlt (nur Icon `ApproverOutline` in R29, Upsell-Text in R31) | R1, R2, W1, W2, W10, D1 |
| F04 | Transition Conditions / Workflow Hooks (pre/post; `run_script`, `send_webhook`; Ausführungshistorie) | Enterprise Grid | Enterprise Grid. `send_webhook` zusätzlich Plan-Feature „Webhook transition conditions“ | fehlt | W2, W11, W12, W25 |
| F05 | Workflow-Änderungshistorie („View change history“) und „Reset workflow“ | Business (mit F01) | wie F01 | fehlt (nur Texte `workflows.quick_actions.*` in R3) | R3, W13 |
| F06 | Transitions-Tab im Work Item mit Time-in-State-Badges, Transitions-Log inkl. Approval-Entscheidungen | Business | Business und höher | fehlt (nur Texte `activity_empty_state.no_transitions`, `transition` in R10) | W2, W19, W20 |
| F07 | Workspace Governance für Workflows (Modi any/constrained/required, Pins, effektiver Workflow, zentrale Verwaltung) | Enterprise Grid | nur Enterprise Grid, Self-hosted ab v3.2.0, irreversibel | fehlt | W3, W4, W14, W15 |
| F08 | Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene („designated admins“) | Business | Repo-Matrix: Business und Enterprise, „coming soon“. Kein öffentlicher Detail-Spec | fehlt | R1 |
| F09 | Custom Automations (Trigger → Bedingungen → Aktionen) je Projekt | Business (Doku 2026). Repo-Matrix: Pro | Repo: Pro „Trigger And Action“. Doku 2026: Business = projektbezogen mit „Change property“ und „Add comment“. Enterprise Grid = zusätzlich F13, F14, „Send webhook“, „Run script“ | fehlt (nur Texte R4, R11, Icon `TriggerOutline` R29) | R1, R2, R4, W21, W22, W23 |
| F10 | Trigger-Typen (Work item created/updated, State changed, Assignee changed, Comment added; Scheduled) | Business (Events), Enterprise Grid (Scheduled) | siehe F09/F14 | fehlt | R4, W21, W23, W24 |
| F11 | Bedingungen („Provided“: State, Priority, Assignees, Labels, Work item type, Created by; AND/OR) | Business | — | fehlt | R4, W21 |
| F12 | Aktionen: Change property, Add comment (Business); Send webhook, Run script (Enterprise Grid) | Business | Business: Change property, Add comment. Enterprise Grid: plus Send webhook, Run script | fehlt | R4, W21, W30, W31 |
| F13 | Global (Workspace-)Automations („All projects“ / „Select projects“) | Enterprise Grid | nur Enterprise Grid (W21/W22). Gegenindiz: Screenshot D11 zeigt den Sidebar-Eintrag „Automations“ in Workspace Settings eines **Business**-Workspace (ob mit Upsell-Sperre, nicht erkennbar) | fehlt (nur Texte `automations.global_automations.*` in R4) | R4, W21, W22, W29 |
| F14 | Scheduled Automations (Fixed: Daily/Weekly/Monthly; Cron) – nur Aktion „Run script“ | Enterprise Grid | nur Enterprise Grid | fehlt (nur Texte `automations.trigger.schedule.*` in R4) | R4, W21, W24, W27 |
| F15 | Decisions and Loops Automation (Aktionen als Trigger, Verzweigungen, Schleifen) | Business | Repo: Business und Enterprise, „coming soon“. Repo-Liste Enterprise: „Unlimited and full Automation Flows“ | fehlt | R1, R2, W28 |
| F16 | Anzahl Automationen je Workspace | Pro | Pro 5.000 · Business 10.000 · Enterprise unbegrenzt | fehlt | R1 |
| F17 | Automation-Ausführungslogs (Activity: Runs, Status, Fehler, Initiator, Filter) | Business (mit F09) | — | fehlt (nur Texte `automations.activity.*`, `automations.table.*` in R4) | R4, W21, W24, W28 |
| F18 | Automation-Consumer/Outbox-Architektur (DB-Trigger → Outbox → Poller → RabbitMQ → Consumer) | Commercial-Infrastruktur | alle Commercial-Pläne (Dienst in Commercial-Images) | fehlt (CE: Celery-Tasks, kein Outbox) | D2, D4, D5, D7, H1, H2, H5, W32 |
| F19 | Plane Runner (Skripte für Automationen, Workflow-Transitionen, Cron) – Schnittstelle zum Cluster | Enterprise Grid | nur Enterprise Grid (W24/W25). Gegenindiz: Screenshot D11 zeigt „Plane Runner“ in der Workspace-Settings-Sidebar eines **Business**-Workspace (Sperre nicht erkennbar) | fehlt (nur Texte `workspace_settings.settings.runners.*` in R9, Icon `ScriptsOutline` in R29) | R9, D3, H3, W24, W25 |
| F20 | Project Templates | Business | Business und Enterprise | Stub/UI-Hülle (`templateId`-Props ohne Wirkung in R16; Texte R5, R6, R8, R9) | R1, R2, R5, W18, W33, W36, W45 |
| F21 | Work Item Templates (Projekt- und Workspace-Ebene, inkl. Sub-Work-Items) | Pro | Pro, Business, Enterprise | Stub/UI-Hülle (Context-Felder und Formular-Logik vorhanden, Provider No-op; R15) | R1 (`planHighlights.pro`), R5, W18, W34, W37, W38, W41 |
| F22 | Page Templates (Projekt-Pages und Wiki) | Pro | Pro, Business, Enterprise | fehlt (nur Texte `templates.dropdown.label.page`, `templates.empty_state.page.*` in R5) | R1 („Templates“ unter Knowledge management), R5, W35, W39, W45 |
| F23 | Pre-defined Templates und Template-Marketplace (Publish, Kategorien, Verifizierung, Kopieren) | Pro (Pre-defined WI-Templates, coming soon) | Repo-Matrix: Pro, Business, Enterprise („coming soon“). Marketplace-Publish: ohne Plan-Angabe | fehlt (nur Texte `templates.settings.form.publish.*`, `templates.toasts.unpublish.*`, `templates.unpublish_confirmation.*` in R5) | R1, R5, W36, W40 |
| F24 | Recurring Work Items | Business | Business und Enterprise | fehlt (nur Texte `recurring_work_items.*` in R7, R8, R10, Icon `RecurringWorkItemsOutline` in R29) | R7 („Upgrade to Business“), W23, W42, W43, W44, W45 |
| F25 | Auto-Archive / Auto-Close (geschlossene bzw. inaktive Work Items) | Free | in allen Plänen | im CE vorhanden (R20 bis R25) | R20, R22, R23, W22 |
| F26 | Auto-Reminders (Fälligkeits-Erinnerung) | Business | Business und höher | fehlt (nur Texte `project_settings.automations.auto-remind.*` in R6) | R6, W22, W46, W47 |
| F27 | Auto-Schedule Cycles (Querverweis, Cycle-Cluster) | UNVERIFIZIERT | UNVERIFIZIERT | fehlt (nur Texte `project_settings.cycles.auto_schedule.*` in R6) | R6, W49 |
| F28 | Auto-transfer Cycle Work items (Querverweis Cycle-Cluster; Verifikation ergänzt) | Pro | Pro, Business, Enterprise (Matrix) | teilweise im CE: nur **manueller** Transfer (`POST …/cycles/<cycle_id>/transfer-issues/`, `apps/api/plane/app/urls/cycle.py`); automatischer Transfer fehlt | R1 (Zeile „Auto-transfer Cycle Work items“), R6 (`auto_rollover`) |
| F29 | Auto-assignment in Modules (Querverweis Modul-Cluster; Verifikation ergänzt) | Pro | Pro „Linear“; Business und Enterprise „Round-robin and Capacity“ | fehlt (keine Texte, keine Hooks) | R1 (Zeile „Auto-assignment In Modules“) |

---

## 3. Feature-Spezifikationen

### F01 – Workflows: Default-Workflow je Projekt

#### Funktionsbeschreibung (UI & Verhalten)

**Zweck:** Workflows legen fest, welche State-Wechsel erlaubt sind, wer sie ausführen darf und ob ein Wechsel eine Genehmigung braucht (W1). Sie verhindern laut Release v1.9.0 Rückschritte („stopping work items from moving backward unexpectedly“), definieren klare Pfade, beschränken Transitionen auf berechtigte Mitglieder und steuern, in welchen States neue Work Items angelegt werden dürfen (W18).

**Aktivierung:** Project Settings → **Workflows** → Toggle **„Enable workflows“** oben auf der Seite (W1). Text: `project_settings.workflows.toggle.title` = „Enable workflows“, `…toggle.description` = „Set workflows to control work item movement“ (R6). Der Toggle ist deaktiviert, mit Tooltip, wenn
- keine States im Workflow sind: `…toggle.no_states_tooltip` „No states are added to the workflow.“,
- keine Work Item Types zugeordnet sind: `…toggle.no_work_item_types_tooltip` „No work item types are added to the workflow.“,
- beides fehlt: `…toggle.no_states_or_work_item_types_tooltip` (R6).

Toasts beim Umschalten: Ladezustand `…toggle.toast.loading.enabling` „Enabling workflows“ bzw. `…disabling` „Disabling workflows“, Erfolg „Workflows enabled successfully.“, Fehler „Failed to enable workflows. Please try again.“ (R6). Ältere Generation (R3): `workflows.toasts.enable_disable.loading` „{action} workflow“, Erfolg „Workflow {action} successfully“, Fehler „Workflow could not be {action}. Please try again.“. In der Projekt-Activity erscheint „enabled custom workflow“ bzw. „disabled custom workflow“ mit Icon `GitBranchOutline` für das Feld `is_workflow_enabled` (R17). Das Feld existiert im CE-Modell `Project` nicht (R22). Es ist ein EE-Feld.

**Zwei UI-Generationen.** Das CE enthält Texte zweier UI-Versionen. Beide müssen bekannt sein. Die neue Plattform baut die aktuelle 2. Generation nach, mit den Regel-Elementen der 1. Generation als Transition-Editor (Annahme, UNVERIFIZIERT, siehe Offene Punkte):

*1. Generation (Release v1.9.0, Texte in R3 `workflows.*`): Regeln pro State*
- Liste aller Projekt-States, gruppiert nach State-Gruppe. Je State:
  - Toggle **„Allow new work items“** (`workflows.workflow_states.work_item_creation`). Bei deaktiviertem Toggle Tooltip „Work item creation is disabled for this state“ (`…work_item_creation_disable_tooltip`).
  - Für den **Default-State** ist der Toggle fixiert: „Default state lets all members create new work items. This can't be changed“ (`…default_state`).
  - Zähler: „{count} permitted state changes“ (`…state_change_count`, ICU-Plural) und „{count} listed reviewers“ (`…movers_count`).
  - Button **„Add permitted state change“** (`…state_changes.label.default`), Ladezustand „Adding permitted state change“ (`…label.loading`).
  - Je Regel: „**Change state to**“ [Ziel-State] (`…state_changes.move_to`) „**When reviewed by**“ [Mitglieder] (`…state_changes.movers.label`). Tooltip: „Reviewers are people who are permitted to move work items from one state to another.“ (`…movers.tooltip`). Button „Add reviewers“ (`…movers.add`).
- Baumdarstellung: „**For work items in**“ [Quell-State] „**can move it to**“ [Ziel-States] (`workflows.workflow_tree.label`, `…state_change_label`).
- Kontextmenü: „View change history“, „Reset workflow“ (`workflows.quick_actions.*`), siehe F05.
- Bestätigungsdialog Regel löschen: Titel „Are you sure you want to delete this state-change rule?“, Text „Once deleted, you can't undo this change and you will have to set the rule again if you want it running for this project.“ (`workflows.confirmation_modals.delete_state_change.*`).
- Fehler-Toasts: `workflows.toasts.add_state_change_rule.error`, `…modify_state_change_rule.error`, `…remove_state_change_rule.error`, `…modify_state_change_rule_movers.error` (Texte siehe Anhang A).
- Upsell-Empty-State (entfällt nach ADR-001): „Control the chaos of changes and reviews with Workflows.“ / „Set rules for where your work moves, by who, and when with Workflows in Plane.“ (`workflows.empty_state.upgrade.*`).

*2. Generation (ab v3.0.0 „Multiple workflows“, W19; Texte in R6 `project_settings.workflows.*`)*
- Seite „Workflows“ (`…heading`), Beschreibung „Automate work item transitions and set rules to control how tasks move through your project pipeline.“ (`…description`), Button „Add new workflow“ (`…add_button`), Suchfeld „Search workflows“ (`…search`).
- Leerzustand: „No workflows yet“ / „Create workflows to manage the progress of your work items.“ / CTA „Add new workflow“ (`settings_empty_state.workflows.*`, R8). Illustration `workflow` (R30).
- Default-Workflow mit Footer: „This workflow applies to any work item type that is not assigned to a workflow.“ (`…default_footer.fallback_message`).
- Detail: „Define workflow“ (`…detail.define`), „Add states“ (`…detail.add_states`). Leerzustand der State-Liste: „Add states“ / „Select the states through which the work item progresses.“ (`settings_empty_state.workflows.states.*`). State-Auswahl, wenn alle States schon verwendet werden: „All states are in use“ / „All defined states for this project are already present in your current workflow.“ (`…select_states.empty_state.*`). Toasts „States added successfully.“ bzw. „Failed to add states. Please try again.“ (`…add_states.*`).
- **Erkennung nicht abgebildeter States:** Banner „Unmapped states detected“ – „Some work items for the selected types are currently in states that do not exist in this workflow.“ – Hinweis: „If you enable this workflow, these items will automatically move to the initial state for this workflow.“ – Label „Missing states“. Tooltip in der Liste: „Some work items are in states that are not mapped to this workflow. Open the workflow to review.“ (`…detail.unmapped_states.*`, R6).
- Create-Modal: Titel „Create new workflow“. Name: Placeholder „Add a unique name“, Pflicht („Name is required“), max. 255 („Name must be less than 255 characters“), Zeichen-Regel „Name can only contain letters, numbers, spaces, hyphens, and apostrophes“. Beschreibung: Placeholder „Add a short description“, gleiche Zeichen-Regel. Feld „Work item type“ (`…create.*`). Toasts für create, update, delete („Deleting workflow“) siehe Anhang A.

**Transition-Semantik (aktuelle Doku):**
- Ohne definierte Transitionen ist jeder State-Wechsel zwischen den States des Workflows erlaubt (D1: „Without a `transitions` block, any state change is permitted.“; W8).
- Jede Transition hat einen Ziel-State und ein „**by**“-Feld. Default ist **All** = jedes Projektmitglied. Über das Members-Panel kann auf einzelne Personen eingeschränkt werden (W1, W2).
- Nicht erlaubte Wechsel zeigen eine Blocker-Meldung mit Begründung (W1).
- „Allow new work items“: Neue Work Items können nur in States angelegt werden, in denen das Flag aktiv ist. States wie „Done“ sind typischerweise nur durch Fortschreiten erreichbar (W1). Der Default-State hat das Flag immer aktiv (R3; W9: „Marking a state as default sets `allow_issue_creation` to true“).
- Nur Projekt-Owner/-Admins richten Workflows ein und bearbeiten sie. Jede Änderung wird protokolliert (W17). Permissions-Matrix: Projekt-Admin create/edit/delete; Contributor nur lesen; Commenter und Guest kein Zugriff (W48).

**Erzwingung („Enforcement“) – alle Schreibpfade:**
| Pfad | Verhalten | Quelle |
|---|---|---|
| Kanban/List Drag-and-Drop | Beim Ziehen werden Spalten bzw. Gruppen, die kein erlaubtes Ziel sind, mit Overlay `bg-danger-subtle` markiert, ohne Text (`workflowDisabledSource` gesetzt). Drop-Sperre mit Toast `type: "warning"`, Titel `common.warning`, Text = `dropErrorMessage`. **Präzisierung (Verifikation):** Kanban (`kanban-group.tsx`) ruft `handleWorkFlowState(sourceGroupId, groupId, sourceSubGroupId, sub_group_id)` in `onDragEnter` und `onDragStart` auf und sperrt den Drop **nur**, wenn zusätzlich `dropErrorMessage` gesetzt ist (`if ((isWorkflowDropDisabled \|\| isDropDisabled) && dropErrorMessage)`); ohne Meldung läuft `handleOnDrop` weiter. List (`list-group.tsx`) ruft `handleWorkFlowState(sourceGroupId, currentGroupId)` in `onDrag` auf (ohne Sub-Gruppen) und sperrt immer, Toast nur bei `group.dropErrorMessage`. Im CE stammt `dropErrorMessage` aus den Gruppen-Spalten (R36, z. B. „Work item cannot be moved to completed cycles“). Dass das EE dort „You can't move this work item here.“ (`workflows.workflow_disabled.title`) einsetzt, ist naheliegend, aber UNVERIFIZIERT. Für die Portierung: Sperre immer serverseitig nachprüfen (Kanban-Quirk nicht übernehmen) | R13 (`group-drag-overlay.tsx`, `kanban-group.tsx` `onDrop`, `list-group.tsx` `onDrag`/`onDrop`), R36, R3 |
| Quick-Add je Gruppe | Wenn im Ziel-State keine Neuanlage erlaubt ist, wird der Quick-Add-Bereich der Gruppe ausgeblendet (`getIsWorkflowWorkItemCreationDisabled(groupId, subGroupId)`) | R13 (`list-group.tsx`, `kanban-group.tsx`, `kanban/default.tsx`, `swimlanes.tsx`) |
| State-Dropdown | EE liest eine paginierte „State-lite“-Ressource mit Workflow-Gating (`typeId`, `isForWorkItemCreation`, `scopedProjectIds`) und übergibt `allowedStateIds`. Nur erlaubte States werden angezeigt: Der Block filtert per `filterOption={(state) => allowedStateIds.has(state.id)}` (Doc-Kommentar „When provided, only states whose id is in this set are shown. Pass `null` … to show all states — used when workflows are disabled or unavailable.“). Gesperrte States sind also **ausgeblendet, nicht ausgegraut** (Repo-belegt; zusätzlich W50, Changelog-Zuordnung UNVERIFIZIERT) | R14 (`packages/blocks/src/property-select/state-select.tsx`), W50 |
| Bulk Operations | Fehler „Unable to update work items“ / „State change is not allowed for some work items. Ensure the state change is allowed.“ (`bulk_operations.error_details.invalid_state_transition`) | R7 |
| REST-API | Nicht erlaubter State-Wechsel → **HTTP 403** mit Code `workflow_transition_denied`. Es wird nichts geschrieben. Nur State-Änderungen werden geprüft | W16 |
| Integrationen (GitHub/GitLab) | Ist der von einem MR ausgelöste Wechsel nicht erlaubt, bleibt das Work Item, wo es ist | W1 (Zusammenfassung) |
| Intake | Seit Mai 2026 blockieren Workflow-Regeln das Anlegen und Ändern von Intake-Work-Items nicht mehr | W51 (UNVERIFIZIERT, Zuordnung zum Eintrag) |
| Automationen | UNVERIFIZIERT, ob Automation-Aktionen „Change property → State“ Workflow-Regeln unterliegen. Siehe Offene Punkte | — |

**Löschen eines Workflows:** Work Items, die er regelte, fallen auf den Default-Workflow zurück (W1). Der Default-Workflow kann nicht gelöscht werden (W8). Ein verwendeter Workflow liefert beim Löschen 409 `workflow_in_use` in v2 (v1: 400) (W8).

#### Datenmodell-Hinweise

Öffentliche API v2 (W5, W6, W7) und Plane Compose (D1) ergeben folgendes Modell. Die Namen sind API-Feldnamen. EF-Core-Entitäten sind ein Vorschlag:

| Entität (Vorschlag) | Felder (API-Namen) | Regeln | Quelle |
|---|---|---|---|
| `Workflow` | `id`, `name` (≤255), `description`, `is_active`, `is_default`, `work_item_type_ids` (UUID[]; ersetzt beim Schreiben das Set), `created_at`, `created_by_id`, Projektbezug über Route | `is_default` setzen löscht das Flag am vorherigen Default. Genau ein Default je Projekt | W5 |
| `WorkflowState` (Chain-Eintrag) | `id` (Chain-Entry-ID), `workflow_id`, `state_id` (Katalog-/Projekt-State), `sequence` (Default: Position × 10000; über „Add states“ angehängt: 65535), `type` = `transition` \| `approval`, `is_default`, `allow_issue_creation` (Default `true`) | Jeder `state_id` nur einmal je Chain. `default_state_id` muss in der Chain liegen. Ein Typwechsel löscht alle von diesem State ausgehenden Transitionen samt Approvern. Ein Typwechsel-Request ändert nur `type`, `allow_issue_creation` muss separat gesendet werden. Eine vollständige Chain-Ersetzung setzt `allow_issue_creation` auf `true`, wo es fehlt | W6, W9 |
| `WorkflowTransition` | `id`, `workflow_state_id` (Quelle, in Requests als `state_id`), `transition_state_id` (Ziel), `rejection_state_id` (nur bei `approval`), `member_ids` (erlaubte Mover bzw. Approver), `required_approvals` (int; `null` = alle) | Quelle nicht in der Chain → 404. Ziel bzw. Rejection außerhalb der Chain → 400. Approver keine aktiven Workspace-Mitglieder → 400 | W7, W10 |
| Feature-Flag | `Project.is_workflow_enabled` (bzw. Project-Feature `workflows`) | MCP/Compose-Feature `workflows` | R17, D1, D8 |

Plane-Compose-YAML (D1): `workflows.<Name>.{description, is_active, work_item_types[], states[], transitions.<State>[].{to, type: transition|approval, required_approvals, approvers[emails]}}`. Dort heißt es: „When `false`, the workflow is defined but not enforced by Plane.“ (`is_active`). `states.yaml`: `allow_issue_creation` (Default `true`), `is_default`. Weitere Compose-Felder: `types.yaml` `<Type>.workflow` (Workflow je WIT), `plane.yaml` `defaults.workflow` („Default workflow applied when a work item type does not specify one“), `features.yaml` `workflows` („Enables custom workflow enforcement. When `false`, state transitions are unrestricted.“).

**Korrektur (Verifikation): D1 ist keine Bestätigung des State-Typs, sondern weicht ab.** In D1 sitzt `type` (`transition` | `approval`) **an jeder einzelnen Transition**, nicht am State. Das Doku-Beispiel hat aus demselben Quell-State „In Progress“ eine `approval`-Transition (→ Done, `required_approvals: 1`, ein Approver) **und** eine direkte `transition` (→ Todo). Ein Rejection-Ziel kennt D1 nicht. Die API-Zusammenfassungen (W6, W9) legen `type` dagegen an den Chain-Eintrag (State). Welche Ebene das Original speichert, ist UNVERIFIZIERT (O20). **Empfehlung:** `type` an der Transition modellieren (Obermenge: State-Typ = „alle ausgehenden Transitionen sind approval“), `rejection_state_id` optional.

CE-Bezug: `State` (R27) hat `group`, `default`, `is_triage`, `sequence`. Ein Workflow referenziert diese States, er ersetzt sie nicht. CE hat `IssueType`/`ProjectIssueType` ohne Workflow-Bezug (R26).

#### API-Hinweise

| Methode | Pfad | Zweck | Quelle |
|---|---|---|---|
| GET/POST | `/api/v2/workspaces/{slug}/projects/{project_id}/workflows/` | Liste, Anlage (`name`, `description`, `is_active`, `work_item_type_ids`) | W5 |
| GET/PATCH/DELETE | `/api/v2/workspaces/{slug}/projects/{project_id}/workflows/{pk}/` | Detail, Update, Löschen (Fallback auf Default) | W5 |
| POST | `…/workflows/{pk}/preview-fallback/` (Pfad UNVERIFIZIERT) | „Preview a workflow fallback“: welche Items wohin fallen | W5 |
| — | `…/workflows/{workflow_id}/states/…` | Chain-Einträge anlegen, ändern, als Default markieren, entfernen (mit `state_mapping`) | W6 |
| — | `…/workflows/{workflow_id}/transitions/…` | Transitionen CRUD | W7 |
| PATCH | Work Item (`state_id`) | 403 `workflow_transition_denied` | W16 |
| v1 intern (EE-Web) | „State-lite“-Ressource mit Parametern `typeId`, `isForWorkItemCreation`, `scopedProjectIds` | Dropdown-Gating | R14 |

Fetch-Keys aus dem CE zeigen die Client-Cache-Schlüssel des EE-Web: `WORKSPACE_WORKFLOW_STATES(workspaceSlug)` → `WORKSPACE_WORKFLOW_STATES_<SLUG>`, `PROJECT_WORKFLOWS(projectId, projectRole)` → `PROJECT_WORKFLOWS_<PROJECTID>_<role>` (R18). Schluss aus dem Cache-Key (nicht direkt belegt, UNVERIFIZIERT): Die gelieferten Workflow-Daten hängen von der Projektrolle des Nutzers ab und werden je Rolle gecacht.

#### UI-Hinweise

- Settings-Navigation: Der CE-Tab-Typ `TProjectSettingsTabs` (R28) kennt nur `general, members, features_*, states, labels, estimates, automations`. Ergänzt werden müssen `workflows`, `templates`, `recurring_work_items`, `work_item_types`. Die Labels liegen vor: `common.workflows`, `common.templates`, `common.recurring_work_items` (R10). Die Kategorien `common.work_structure` und `common.execution` gibt es bereits (R28). Die exakte Einordnung des Workflows-Tabs ist UNVERIFIZIERT.
- Icons: `WorkflowsOutline`/`WorkflowsPropertyOutline` (Properties), `GitBranchOutline` (Activity), `ApproverOutline` (Approver) (R29).
- Drag-Overlay: Klassen siehe `group-drag-overlay.tsx` (`bg-layer-1/85`, `border-strong`, `bg-danger-subtle`, `text-danger-secondary`) (R13).

#### Migrationshinweise (.NET/Angular)

- `WorkflowEnforcementService` als Domänendienst. Er wird bei **jedem** State-Wechsel aufgerufen: Work-Item-Update, Bulk-Update, Drag-and-Drop, Import, Integration, Automation-Aktion, Template-Anwendung. Ausnahme Intake (W51). Er liefert `workflow_transition_denied` (403) mit Begründung.
- Endpunkt für das Frontend: „erlaubte Ziel-States für (Work Item | Quell-State, WIT, Nutzer)“ und „States mit erlaubter Neuanlage“. Das bildet `allowedStateIds` (R14) und `getIsWorkflowWorkItemCreationDisabled` (R13) ab.
- Angular: Der CE-Hook `useWorkFlowFDragNDrop(groupBy, subGroupBy)` (R12) mit Rückgabe `{ workflowDisabledSource, isWorkflowDropDisabled, getIsWorkflowWorkItemCreationDisabled, handleWorkFlowState }` wird als Service mit echter Logik portiert. Er greift nur bei `group_by`/`sub_group_by` = `state` (Annahme, UNVERIFIZIERT).

#### Quellen
R2, R3, R6, R7, R12, R13, R14, R17, R18, R19, R22, R26, R27, R28, R29, D1, D8, W1, W2, W5, W6, W7, W8, W9, W10, W16, W17, W18, W19, W48, W50, W51.

#### Konfidenz
**Hoch** für UI-Texte und Erzwingungspunkte im Web (R3, R6, R13). **Mittel** für Feldnamen und Fehlercodes (API-Zusammenfassungen). **Niedrig** für das exakte Layout der 2. Generation.

---

### F02 – Mehrere, typ-spezifische Workflows

#### Funktionsbeschreibung
- Neben dem Default-Workflow lassen sich weitere Workflows anlegen. Jeder gilt für bestimmte **Work Item Types** (Feld „Work item type“ im Create-Modal, R6). Ein typ-spezifischer Workflow hat Vorrang vor dem Default. Passt der Typ eines Work Items, gelten dessen Regeln (W1, W2).
- Release v3.0.0 (14.07.2026): verschiedene Workflows für verschiedene Work Item Types und Teams im selben Projekt (W19).
- Der Workflow-Toggle verlangt zugeordnete WITs. Sonst greift der Tooltip `no_work_item_types_tooltip` (R6).
- Beim Zuordnen von Typen bzw. Aktivieren mit Items in nicht abgebildeten States erscheint der Banner „Unmapped states detected“. Beim Aktivieren werden diese Items **automatisch in den Initial-State** des Workflows verschoben (R6 `…unmapped_states.note`). Die API-Variante verlangt beim Entfernen von States ein `state_mapping` je betroffenem Item, sonst 409 `workflow_state_orphans`. Über 500 Items je Projekt und Typ läuft die Verschiebung im Hintergrund (W9). „Initial state“ = Default-State des Workflows (Annahme aus W15: Items außerhalb eines gepinnten Workflows gehen auf dessen Default-State).

#### Plan-Tier
Enterprise Grid (W1: „On the Enterprise Grid, you can create additional workflows, each scoped to specific work item types“; W2 Plan-Tabelle; W45 „Multiple Workflows + Approvals“). Business: ein Default-Workflow (W1).

#### CE-Status
Stub/UI-Hülle: nur Texte (R6, R8). Das CE-`IssueType` existiert (R26), hat aber keine Workflow-Zuordnung.

#### Datenmodell / API
`Workflow.work_item_type_ids` (W5). Die effektive Workflow-Auflösung je (Projekt, WIT) ist ohne Governance: typ-spezifischer Workflow, sonst Default des Projekts (W1). Mit Governance siehe F07.

#### Quellen
R6, R8, R26, W1, W2, W5, W9, W15, W19, W45.

#### Konfidenz
Mittel.

---

### F03 – Approval Flows (Workflow-Genehmigungen)

#### Funktionsbeschreibung (UI & Verhalten)
- Ein State im Workflow kann vom Typ **`approval`** sein (statt `transition`) (W9). **Korrektur (Verifikation):** D1 modelliert `type: approval` dagegen **je Transition** und erlaubt aus demselben Quell-State gemischte Typen (siehe F01 Datenmodell, O20). Für eine Transition aus einem Approval-State legt man fest:
  - **„on approve, move to“** → `transition_state_id`,
  - **„on reject, move to“** → `rejection_state_id` (Fallback-State),
  - **„by“** → Approver: Default **All**, einschränkbar auf bestimmte Mitglieder (`member_ids`). Mit Governance sind es Workspace-Mitglieder, sonst Projektmitglieder (W1, W2, W10).
  - **`required_approvals`** → Anzahl nötiger Zustimmungen. `null` = alle gelisteten Approver müssen zustimmen (W10, D1).
- Erreicht ein Work Item einen State mit Approval-Flow, ist es **pending**. Der Wechsel wird erst nach finaler Entscheidung wirksam (W2). Approver sehen **„Approve“** und **„Reject“** oben in der Work-Item-Detailansicht. Je nach Entscheidung geht das Item in den passenden Ziel-State (W1).
- Jedes Enforcement-Ereignis, jede gesperrte Transition, jedes Approval-Gate und jede Reviewer-Entscheidung landet im **Transitions-Log** des Items (W1, W20).
- Beispiel in der API-Doku: Approval-State mit `allow_issue_creation: false`, Rejection-State zurück auf „In Progress“, `required_approvals: 1` mit einem gelisteten Mitglied (W9).
- Benachrichtigung der Approver (Inbox/E-Mail): **nicht dokumentiert** (UNVERIFIZIERT). `tour.json` erwähnt allgemein „Your inbox keeps all mentions, approvals, and activity in one place“ (`packages/i18n/src/locales/en/tour.json`).
- Endpunkt für die Entscheidung (approve/reject) ist in der öffentlichen API **nicht dokumentiert** (UNVERIFIZIERT).

#### Plan-Tier
Doku/Blog 2026: **Enterprise Grid** (W1, W2, W27). API: „Creating a transition from an approval state needs the Workflow approvals plan feature, or the request returns 402“ (W10). Repo: `BUSINESS_PLAN_FEATURES` enthält „Workflows + Approvals“ (R2). Matrix-Zeile „Approvals“ Business, coming soon (R1) betrifft eher F08.

#### CE-Status
fehlt. Nur Icon `ApproverOutline` (R29) und Upsell-Text „Dashboards, Workflows, Approvals …“ (R31).

#### Datenmodell-Hinweise
- Konfiguration: `WorkflowState.type = approval`, `WorkflowTransition.{transition_state_id, rejection_state_id, member_ids, required_approvals}` (W10).
- Laufzeit (Vorschlag, nicht öffentlich belegt): `WorkflowApprovalRequest { id, work_item_id, workflow_transition_id, requested_by_id, from_state_id, status: pending|approved|rejected|cancelled, created_at, decided_at }` und `WorkflowApprovalDecision { request_id, approver_id, decision: approve|reject, comment?, created_at }`. Wird `required_approvals` erreicht → Wechsel auf `transition_state_id`. Wann ein einzelnes Reject zu `rejection_state_id` führt, ist UNVERIFIZIERT (Vorschlag: sofort).
- Wo das Item während „pending“ steht, ist UNVERIFIZIERT: im Approval-State selbst (Lesart W9: „A move out of an approval state waits for approvers“) oder davor (Lesart W2: „the work item won't move forward until …“). Die API-Formulierung (Quelle ist der Approval-State) spricht dafür, dass das Item **im Approval-State steht** und der **Wechsel aus ihm heraus** genehmigt wird.

#### API-Hinweise
Workspace-Katalog: `/api/v2/workspaces/{slug}/workflows/{workflow_id}/transitions/` (W10). Projekt: `/api/v2/workspaces/{slug}/projects/{project_id}/workflows/{workflow_id}/transitions/` (W7). Requests verwenden `state_id` (Quelle), `transition_state_id`, `rejection_state_id`. Responses melden die Quelle als `workflow_state_id` (W10).

#### UI-Hinweise
Approve/Reject-Buttons oben in der Detailansicht (W1). Approver-Auswahl als Member-Picker mit Option „All“ (W1). Das Changelog erwähnt einen Bugfix an der Checkbox „ALL“ im Workflow-Member-Picker (W19).

#### Quellen
R1, R2, R29, R31, D1, W1, W2, W7, W9, W10, W19, W20, W27.

#### Konfidenz
Mittel (Konfiguration), niedrig (Laufzeit-Entität, Benachrichtigung, Entscheidungs-Endpunkt).

---

### F04 – Transition Conditions / Workflow Hooks

#### Funktionsbeschreibung
- An eine Transition lassen sich **Plane-Runner-Skripte** hängen: **Pre-Validation** (vor dem Wechsel, kann ihn blockieren) und **Post-Action** (nach dem Wechsel, blockiert nicht) (W2, W25).
- Pre-Skripte laufen in der angezeigten Reihenfolge, alle müssen bestehen. `return { success: true }` erlaubt. Eine Rückgabe mit `success: false` oder ein `throw` blockiert. Der Nutzer sieht die Fehlermeldung aus dem geworfenen Error. Doku-Beispiel „To Do → In Progress“ wirft „Transition blocked“, wenn Assignee oder Estimate fehlt (W1, W25).
- Post-Skripte schlagen fehl, ohne den Wechsel zurückzunehmen. Der Fehler steht in der Ausführungshistorie des Skripts (W25).
- API-Modell „Hooks“: `phase` = `pre` | `post`. `handler_name` = `send_webhook` | `run_script` (bei Anlage gesetzt, unveränderlich). Die Reihenfolge wird bei Anlage vergeben: höchster vorhandener Wert der Phase + 1. Ein fehlgeschlagener Pre-Hook (auch Webhook-Fehler) blockiert den Wechsel (W11, W12).
- `send_webhook`: Plane erzeugt das Signing-Secret und liefert es **nur einmal** in der Create-Response als `config.secret_plaintext`. Endpunkt „regenerate secret“. Event-Typ `workflow.transition` mit Work-Item-Daten. Timeout 30 s, keine Redirects. Jeder Status außer 2xx ist ein Fehler (W11, W12).
- `run_script`: Script-ID und Ausführungs-Variablen (W11; Feldliste UNVERIFIZIERT).
- Ausführungen: Liste mit `status` = `pending` | `running` | `success` | `failed`, Input, Output. Sie bleiben nach Löschen des Hooks lesbar (W11).
- Hook-Änderungen erzeugen Workflow-Activity mit `field = transition_rule` (W13).

#### Plan-Tier
Enterprise Grid (W2). Zusätzlich je Handler: Plane Runner für `run_script`, „Webhook transition conditions“ für `send_webhook`. Fehlt eines → 402 (W12).

#### CE-Status
fehlt.

#### Datenmodell-Hinweise
`WorkflowHook { id, workflow_transition_id, project_id?, phase, handler_name, config (jsonb: url, headers, secret_encrypted | script_id, variables), order, is_enabled? }`, `WorkflowHookExecution { id, hook_id, status, input (jsonb), output (jsonb), error, started_at, finished_at }` (Vorschlag auf Basis von W11).

#### API-Hinweise
Projekt: `/api/v2/workspaces/{slug}/projects/{project_id}/workflows/…/hooks/` (list, get, create, update, delete, executions, regenerate-secret) (W11). Katalog: `/api/v2/workspaces/{slug}/workflows/…/hooks/` (W12). Pfadsegmente unterhalb von `workflows/` sind UNVERIFIZIERT.

#### Migrationshinweise
Pre-Hooks laufen **synchron** im Request des State-Wechsels (Timeout 10 s Skript bzw. 30 s Webhook), Post-Hooks asynchron über die Outbox (F18). Signatur wie CE-Webhooks: HMAC-SHA256, Header `X-Plane-Signature` (R32). **Ergänzung (Verifikation):** Für ausgehende Hook- und Automation-Webhooks die SSRF-Schutzlogik des CE übernehmen: `pinned_fetch(...)` mit `allowed_ips=settings.WEBHOOK_ALLOWED_IPS`, `allowed_hosts=settings.WEBHOOK_ALLOWED_HOSTS`, IP-Pinning gegen DNS-Rebinding, keine Redirects, `timeout=30` (`apps/api/plane/bgtasks/webhook_task.py`). Achtung Abweichung: Das CE signiert `json.dumps(payload)` und sendet `json=payload` (Re-Serialisierung), W21 verlangt für „Send webhook“ eine Signatur über die **rohen Body-Bytes** – in .NET Body einmal serialisieren und dieselben Bytes signieren und senden. CE-`User-Agent` ist `Autopilot`.

#### Quellen
R32, W1, W2, W11, W12, W13, W25.

#### Konfidenz
Mittel.

---

### F05 – Workflow-Änderungshistorie und „Reset workflow“

#### Funktionsbeschreibung
- Quick Actions „View change history“ und „Reset workflow“ (`workflows.quick_actions.*`, R3).
- Reset-Dialog: „Are you sure you want to reset this workflow?“ – „If you reset this workflow, all your state-change rules will be deleted and you will have to create them again to run them for this project.“ (`workflows.confirmation_modals.reset_workflow.*`). Toasts „Workflow reset successfully“ bzw. „Error resetting workflow“ / „Workflow could not be reset. Please try again.“ (R3). Wirkung: Alle Transition-Regeln werden gelöscht, das heißt nach D1/W8 sind danach alle Wechsel erlaubt.
- Änderungshistorie (API „workflow activities“): Felder `actor_id` (nullable), `verb` ∈ {`created`, `added`, `updated`, `removed`, `deleted`, `enabled`, `disabled`}, `field` (zum Beispiel `workflow_state`, `state_approvers`, `transition_rule`, `workflow_description`; bei `workflow_description` keine Werte), `old_value`, `new_value`, `old_identifier`, `new_identifier`, `created_at`. Nur lesbar, älteste zuerst. Inkrementelles Polling über `created_at__gt`. Filter `verb`, `field`, `actor_id`. Asynchron geschrieben (Eintrag kann kurz nach der Änderung erscheinen). Unbekannte `field`-Werte anzeigen, nicht als Fehler werten (W13).

#### Plan-Tier
Wie F01 (Business).

#### CE-Status
fehlt.

#### Quellen
R3, D1, W8, W13.

#### Konfidenz
Mittel.

---

### F06 – Transitions-Tab und Time-in-State (Querverweis Work-Item-Detail)

- Tab „Transitions“ im Activity-Bereich des Work Items (Tabs: All, Comments, History, Transitions, Worklogs). Listet jeden State-Wechsel: wer, wann, von → nach (farbige State-Icons). Zwischen den Einträgen zeigen **Badges die Verweildauer** im vorherigen State. „All“ kombiniert alles. „History“ ist das volle Property-Audit inklusive Bot-Aktionen (W20).
- Duration-Badges auch in Sidebar und Peek-Overview (W19). Passendes Icon im Propel-Paket: `TimeInStateOutline`/`TimeInStateFilled` (`properties/time-in-state-outline.js`, R29; Verwendung im EE UNVERIFIZIERT).
- CE-Leerzustände der Activity-Tabs (`activity_empty_state.*`, R10): `no_activity` „No activity yet“, `no_comments` „No comments yet“, `no_history` „No history yet“, `no_transitions` „No transitions yet“, `no_worklogs` „No worklogs yet“ – bestätigt die Tab-Liste All/Comments/History/Transitions/Worklogs.
- Plan: „Time in state + transitions“ ab Business (W20).
- CE: Leerzustand „No transitions yet“ (`activity_empty_state.no_transitions`), Label `transition` (R10). Kein Tab.
- Approval-Entscheidungen und Workflow-Enforcement-Ereignisse erscheinen hier (W1).
- **Konfidenz:** mittel. Volle Spezifikation gehört in das Work-Item-Detail-Dokument. Hier nur der Workflow-Bezug.

---

### F07 – Workspace Governance für Workflows (nur Workflow-Teil; Querverweis Governance-Cluster)

- Mit **Workspace Governance** haben alle Projekte dieselben States, Labels und Workflows. Workflows werden zentral vom Workspace-Admin definiert. Projekt-Admins bearbeiten sie nicht mehr im Projekt (W3, W4).
- Je Work Item Type gilt ein Modus. API: `any` (Default; Projekt wählt aus allen aktiven Workspace-Workflows), `constrained` (Allowlist), `required` (ein Workflow vorgeschrieben). UI-Labels für Projekt-Admins: **free**, **constrained**, **mandated**, **pinned** (W3, W15).
- **Pins** fixieren ein bestimmtes Projekt auf einen Workflow (unter `any` und `constrained`, nicht unter `required`). Ein Pin schreibt auch die Projektwahl („pick“). Items außerhalb des gepinnten Workflows gehen in dessen Default-State. Löschen eines Pins entfernt nur die Markierung (W15).
- **Effektiver Workflow** je (Projekt, WIT): `required` → Pin → Projektwahl → Workspace-Default (Katalog-Workflow mit `is_default`). Der Endpunkt „work item type workflows“ liefert `source` ∈ {`required`, `pin`, `pick`, `workspace_default`}. Der Name ist `null`. Ohne Governance kommt 409 `states_managed_at_project` (W14).
- Projekt-Admins sehen je Typ das Label, den effektiven Workflow und eine Vorschau der Umverteilung bestehender Items (W3).
- Katalog-Workflows: Ein neuer ist immer inaktiver Entwurf (`is_active=false`, `is_default=false`; `is_active` wird bei Create ignoriert). Setup: States anhängen, Default wählen, Transitionen, aktivieren (W8, W9). Usage-Endpunkt listet die Projekt/WIT-Paare, die auf den Workflow zeigen (W8).
- Governance ist **irreversibel** (W3, W4). Self-hosted ab v3.2.0 (W4). Plan: Enterprise Grid. Ohne Feature → 402 (W15).
- Governance sperrt im Projekt zusätzlich das Anlegen und Bearbeiten von Templates, Automationen und Recurring Work Items (W33). Bestehende Projekt-Automationen werden auf Workspace-Ebene migriert und laufen in ihrem ursprünglichen Scope weiter (W22, W27).
- **CE-Status:** fehlt. **Konfidenz:** mittel.
- **Migrationshinweis:** Das Datenmodell aus F01 bis F04 wird **von Anfang an zweistufig** angelegt: Workspace-Katalog (`workspace_id`, `project_id = null`) und Projektebene. So passen Governance und Nicht-Governance in ein Schema. ADR-001 hebt die Plan-Bindung auf. Die Irreversibilität ist eine fachliche Regel und bleibt erhalten (Empfehlung, siehe Offene Punkte).

---

### F08 – Approvals auf Workspace-, Projekt- und Work-Item-Type-Ebene

- **Einzige Quelle:** Matrix-Zeile „Approvals“: „Set workspace, project, and work item type approvals to designated admins.“, `comingSoon: true`, Business und Enterprise (R1).
- Öffentliche Doku 2026 beschreibt Approvals **nur** als Workflow-Approval-Flows (F03). Das Pricing nennt „workflows by work item type with designated approvers per transition“ (W45). Ein eigenständiges Approval-Modul für Workspace- oder Projekt-Änderungen ist **nicht dokumentiert** (UNVERIFIZIERT).
- Angrenzend, in anderen Clustern: Timesheet-Approvals („Historical timesheets and approvals“, Business, R1 Zeile „Time Tracking + Worklogs“); Beitrittsfreigabe privater Projekte („Private ones are visible but need approval to join“, Pro, R1 Zeile „Public, Private, and Secret projects“). Laut Permissions-Matrix dürfen nur Owner/Admin privaten Projekten selbst beitreten. Ein Request-to-Join-Flow ist nicht dokumentiert (W48).
- **CE-Status:** fehlt. **Konfidenz:** niedrig.
- **Empfehlung:** Die WIT-Ebene mit F03 abdecken (Approval-Flows je typ-spezifischem Workflow). Workspace- und Projekt-Approvals als offene Frage an den Auftraggeber (Abschnitt 4).

---

### F09 – Custom Automations (Trigger → Bedingungen → Aktionen), Projektebene

#### Funktionsbeschreibung (UI & Verhalten)

**Ort:** Project Settings → **Automations** → Abschnitt „Custom automations“ (`automations.settings.title`). Button „Create automation“ (`automations.settings.create_automation`) (R4, W21). Auf derselben Seite stehen oben die Standard-Automationen Auto-Archive, Auto-Close (F25) und Auto-Reminders (F26) (R6, R23, W22). Power K kennt die Aktion „New automation“ (`power_k.creation_actions.create_project_automation`, R11).

**Listen-Tabelle** (`automations.table.*`, R4): Spalten „Automation title“, „Scope“, „Projects“, „Last run on“, „Created on“, „Last updated on“, „Last run status“, „Average duration“, „Owner“, „Executions“. Scope-Labels bei globalen Automationen: „Global“, „Project“, „Multiple“, „All“ (`automations.global_automations.table.scope.*`).

**Leerzustand:** „There’re no automations to show yet.“ / „Automations help you eliminate repetitive tasks by setting triggers, conditions, and actions. Create one to save time and keep work moving effortlessly.“ (`automations.empty_state.no_automations.*`). Upsell-Variante entfällt (ADR-001).

**Create/Update-Modal** (`automations.create_modal.*`): Überschrift „Create automation“ bzw. „Update automation“. Titel-Feld mit Placeholder „Name your automation.“ (Pflicht: „Title is required“). Beschreibung mit Placeholder „Describe your automation.“. Submit „Create automation“ bzw. „Update automation“. Laut API: `name` ≤ 255 Pflicht, `scope` ≤ 50 Pflicht, `description` optional (W28).

**Automation-Editor** (Haupt-Canvas plus rechte Sidebar), Satzstruktur „**If** [Trigger] **Provided** [Bedingungen] **Then** [Aktionen]“ (`automations.conjunctions.if|then`, `automations.condition.label` = „Provided“):

1. **Scope** („Scope“ / „Run on“, `automations.scope.*`). Projekt-Automation: Projekt fix. Global: siehe F13. API-`scope` zum Beispiel `WorkItem`, `Cycle`, `Module` (W28).
2. **Trigger** (`automations.trigger.*`): Block „Trigger“, Button „Add trigger“. Sidebar-Header „Trigger configuration“, Frage „What’s the trigger for this automation?“, Auswahl-Placeholder „Select an option“. Gruppen **„Plane events“** und **„Time based“** (Option „Fixed schedule“). Navigation „Back“ / „Add action“. Nach Anlage gesperrt: „You can't change the trigger type once created“ (`automations.trigger.warning.disabled_trigger_switching`). Details zu den Typen in F10 und F14.
3. **Bedingungen** (`automations.condition.*`): „Provided“, Button „Add condition“, Ladezustand „Adding condition“. Verknüpfung „And“ / „Or“. Details F11.
4. **Aktionen** (`automations.action.*`): „Action“, Button „Add action“. Sidebar-Header „Actions“, Frage „What does the automation do?“, Placeholder „Select an option“. Handler-Namen: `add_comment` „Add comment“, `change_property` „Change property“, `run_script` „Run Script“. Abschnitt „Configuration“. Blocktitel „Add comment“, „Run script“, „Change property“. Mehrere Aktionen laufen **nacheinander** (W21). Details F12.
   - Regel: Die **einzige** Aktion lässt sich nur bei deaktivierter Automation löschen: „Disable the automation before deleting its only action.“ (`automations.action.validation.delete_only_action`).
   - Fehler-Toasts: „Failed to create action. Please try again!“, „Failed to update action. Please try again!“ (`automations.toasts.action.*`).

**Lebenszyklus:**
- Neu angelegt = **Entwurf** (API `status: "draft"`). Läuft nicht, bis aktiviert (W21, W28).
- Hinweis-Banner: „Hit 'Enable' whenever your automation is complete. Once enabled, the automation will be ready to run.“ (`automations.enable.alert`).
- **Enable** nur mit Trigger und mindestens einer Aktion: „Automation must have a trigger and at least one action to be enabled.“ (`automations.enable.validation.required`; W21).
- **Disable** über Button oder Status-Toggle (W21).
- **Delete** nur deaktiviert: „Automation must be disabled before deleting it.“ (`automations.delete.validation.enabled`; W21). Dialog „Delete automation“. Toast „Automation deleted“ / „{name}, the automation, has now been deleted from your project.“ (R4).
- Toasts für create, update, enable, disable, delete (Erfolg und Fehler) siehe Anhang A.

**Laufzeitverhalten:**
- Eine Automation wertet **nur das auslösende Work Item** aus und handelt nur auf ihm. Logik über andere Items (Geschwister, Parent schließen, wenn alle Kinder fertig) gehört in Runner-Skripte (W26).
- **Loop-Schutz:** Plane erkennt Änderungen aus einer Automation und speist sie nicht als neues Event zurück. Beispiel: eine State-Change-Regel feuert nicht erneut auf ihr eigenes Ergebnis (W21).
- **Idempotenz:** Jedes Event wird je Automation nur einmal verarbeitet (W21).
- Änderungen schreibt ein eigener Bot-Account **„Automation Bot“**. Daran unterscheidet die Activity Bot-Änderungen von denen der Mitglieder (W21). API-Feld `bot_user_id` an der Automation (W28). CE-Grundlage: `User.is_bot`, `User.bot_type`, `BotTypeEnum` mit bisher nur `WORKSPACE_SEED` (R35).
- **Fehler:** Scheitert eine Aktion, bricht der Run dort ab und wird als **failed** markiert. Details im Activity-Tab (W21).
- Berechtigung: Projekt-Automationen nur Projekt-Admin. Der CE-Tab `automations` hat `access: [EUserProjectRoles.ADMIN]` (R28, `packages/constants/src/settings/project.ts`). Die CE-Seite zeigt `NotAuthorizedView` für Nicht-Admins (R23). Governance sperrt Projekt-Admins (W22).

#### Plan-Tier
- Repo-Matrix: „Trigger And Action“ ab **Pro** (R1). `PRO_PLAN_FEATURES` enthält „Trigger And Action“ (R2).
- Doku 2026: „Business“ = Projekt-Automationen mit „Change property“ und „Add comment“. „Enterprise Grid“ = plus Workspace-Automationen, „Send webhook“, „Run script“, Scheduled (W21, W22).
- Release v1.14.0 (02.09.2025) führte Automations ein (W23).

#### CE-Status
fehlt. Nur Texte R4/R11. Die CE-Seite `…/automations/page.tsx` rendert nur `AutoArchiveAutomation` und `AutoCloseAutomation` (R23).

#### Datenmodell-Hinweise (API v2, W28/W29)

| Entität (Vorschlag) | Felder | Quelle |
|---|---|---|
| `Automation` | `id`, `name`, `description`, `scope` (z. B. `WorkItem`, `Cycle`, `Module`), `status` (mindestens `draft`; weitere Werte UNVERIFIZIERT), `is_enabled`, `is_global`, `project_ids` (UUID[], ersetzt beim Schreiben), `bot_user_id`, `current_version_id`, `run_count`, `last_run_at`, `created_at`, `created_by_id`, `updated_at` | W28, W29 |
| `AutomationNode` | `id`, `automation_id`, `version_id`, `node_type` ∈ {`trigger`, `condition`, `action`} (Feldname zwischen `node_type` und `name` widersprüchlich dokumentiert, UNVERIFIZIERT), `handler_name` (≤100; Beispiele `record_created`, `send_email`; aus R4: `add_comment`, `change_property`, `run_script`), `config` (jsonb), `is_enabled`, `last_triggered_at`, Anzeigename `name` | W28, W29, R4 |
| `AutomationEdge` | `id`, `source_node_id`, `target_node_id`, `execution_order` (Auswertungsreihenfolge bei mehreren ausgehenden Kanten), `version_id` | W28, W29 |
| `AutomationVersion` | `id`, `automation_id`, Nummer, Zeitstempel (Existenz belegt durch `current_version_id`/`automation_version_id`; Semantik UNVERIFIZIERT) | W28 |
| `AutomationRun` | `id`, `automation_id`, `version_id`, Initiator (`automations.activity.run_history.initiator`), `status` (success/failed), Start, Dauer (Basis für „Average duration“), Auslöse-Entity | R4, W28 (Felder UNVERIFIZIERT) |
| `AutomationNodeExecution` | `id`, `run_id`, `node_id`, Status, Input/Output, Fehler | W28 (`node_execution_id`; Felder UNVERIFIZIERT) |
| `AutomationActivity` | `id`, `actor_id`, `automation_id`, `automation_node_id`, `automation_edge_id`, `automation_run_id`, `automation_version_id`, `node_execution_id`, `automation_scope`, `field`, `verb`, `old_value`, `new_value`, `old_identifier`, `new_identifier`, `epoch`, `created_at` | W28 |

Das Modell ist ein **Regel-Graph** („rule graphs“, W28): Trigger-, Bedingungs- und Aktionsknoten, über Kanten verbunden. Der heutige Editor bildet eine lineare Kette ab (Trigger → Bedingungen → Aktionen in Reihenfolge). Der Graph erlaubt später F15 (Decisions/Loops).

#### API-Hinweise

| Methode | Pfad | Hinweis | Quelle |
|---|---|---|---|
| GET/POST | `/api/v2/workspaces/{slug}/projects/{project_id}/automations/` | Liste (Sparse-Fields über `fields`; unbekannter Name → 400), Create | W28 |
| GET/PATCH/DELETE | `…/automations/{pk}/` | — | W28 |
| POST | `…/automations/{pk}/status/` | Body `{ "is_enabled": bool }` → 204 ohne Body | W28 |
| CRUD | `…/automations/{automation_id}/nodes/` | Filter `handler_name` | W28 |
| CRUD | `…/automations/{automation_id}/edges/` | Filter `source_node_id`, `target_node_id` | W28 |
| GET | `…/automations/{automation_id}/activities/`, `…/activities/{id}/` | Filter `created_at__gt`, `field` | W28 |

#### UI-Hinweise
Icons `AutomationsOutline`, `TriggerOutline` (CE nutzt `TriggerOutline` bereits für den Settings-Tab „automations“, `apps/web/components/settings/project/sidebar/item-icon.tsx`), `LoopOutline`, `WebhooksOutline`, `ScriptsOutline` (R29).

#### Quellen
R1, R2, R4, R11, R23, R28, R29, R35, W21, W22, W23, W26, W28, W29.

#### Konfidenz
Hoch (UI-Texte und Regeln), mittel (API-Felder), niedrig (Run/NodeExecution-Felder).

---

### F10 – Trigger-Typen

| Trigger (UI) | Gruppe | Handler-Name | Plan | Quelle |
|---|---|---|---|---|
| Work item created | Plane events | `record_created` (API-Beispiel) | Business | W21, W23, W29 |
| Work item updated | Plane events | UNVERIFIZIERT | Business | W21, W23 |
| State changed | Plane events | UNVERIFIZIERT | Business | W21, W23 |
| Assignee changed | Plane events | UNVERIFIZIERT | Business | W21, W23 |
| Comment added | Plane events | UNVERIFIZIERT | Business | W21, W23 |
| Scheduled (Fixed schedule / Cron) | Time based | UNVERIFIZIERT | Enterprise Grid | R4, W21, W24 |
| Due-Date-basierte Erinnerung über Automationen | UNVERIFIZIERT | UNVERIFIZIERT | UNVERIFIZIERT | W47 („auto reminders … configured through automations based on due date“) |

- Ein Event-Trigger liefert Event-Daten im Runner-Format: `event_type` (zum Beispiel `work_item.updated`), `entity_type`, `entity_id`, `project`, `workspace`, `initiator_id`, `timestamp`, `payload.data` (aktueller Zustand), `payload.previous_attributes` (nur geänderte Felder mit alten Werten) (W25, W32).
- Der Automation-Consumer verarbeitet im Default nur Events vom Typ `issue` (`AUTOMATION_EVENT_TYPES: "issue"`, H1; `env.automation_consumer_envs.event_types`, D5). Mit `scope` `Cycle`/`Module` (W28) sind weitere Entity-Typen vorgesehen (UNVERIFIZIERT).
- Trigger-Typ nach Anlage unveränderlich (R4).
- **Konfidenz:** hoch (UI-Namen), niedrig (Handler-Namen außer `record_created`).

---

### F11 – Bedingungen („Provided“)

- Felder: **State, Priority, Assignees, Labels, Work item type, Created by** (W21).
- Operatoren: **Is, Is not, In, Contains** und Vergleichsoperatoren (Greater than, Less than) (W21). Die vollständige Operator-Liste je Feld ist UNVERIFIZIERT. Empfehlung: das CE-Rich-Filter-Modell wiederverwenden (`packages/types/src/rich-filters/*`, `packages/shared-state/src/store/rich-filters/*`, `packages/utils/src/work-item-filters/configs/filters/*`). Es kennt bereits State, Priority, Labels, User-Felder und Datumsfelder. **Repo-Indiz (Verifikation):** Der Adapter-Typ nennt Automationen ausdrücklich als zweites Filterformat: „@template E - External filter format type (e.g., work item filters, automation filters)“ (`packages/types/src/rich-filters/adapter.ts` Z. 18). Das EE nutzt für Automation-Bedingungen also sehr wahrscheinlich die Rich-Filter-Infrastruktur mit eigenem Adapter (UNVERIFIZIERT im Detail).
- Logik: Mehrere Bedingungen sind standardmäßig per **AND** verknüpft. **OR-Gruppen**, in denen eine Bedingung genügt, sind möglich (W21). UI-Konjunktionen „And“/„Or“ (`automations.conjunctions.*`, R4).
- Bedingungen sind optional (W21).
- **Konfidenz:** mittel.

---

### F12 – Aktionen

| Aktion | Handler | Konfiguration und Verhalten | Plan | Quelle |
|---|---|---|---|---|
| **Change property** | `change_property` | UI: Property wählen (Placeholder „Select a property“), Änderungsart („Select“), Wert(e) („Select value“ bzw. „Select values“, ICU-Plural; Datum: „Select date“). Validierung: „Property name is required“, „Change type is required“, „Property value is required“ (R4). Properties und Änderungsarten: Priority (set/add/remove), State, Assignees (add/remove), Labels (add, remove, replace all), Start und Due Date (set/update/remove) (W21, W23). Seit v3.1.0 bzw. Juli 2026 auch Cycle (inklusive Cycle-Auswahl für Multi-Projekt-Automationen), Module, Milestone, Release. Ein Work Item hat nur einen Milestone, Zuweisen verschiebt es aus dem bisherigen (W30, W31). Custom Properties UNVERIFIZIERT | Business | R4, W21, W23, W30, W31 |
| **Add comment** | `add_comment` | Kommentar ist **immer intern**. Autor im Activity-Log ist „Automation Bot“. Template-Variablen für dynamische Werte (Beispiele: aktuelle Priority, State-Name; vollständige Variablenliste UNVERIFIZIERT). Mitglieder lassen sich taggen („post comments and tag teammates“) | Business | R4, W21, W23 |
| **Send webhook** | UNVERIFIZIERT (vermutlich `send_webhook`, wie bei Workflow-Hooks) | **Ein** Versuch, 30 s Timeout, **kein Retry**. Bis zu 20 Custom-Header, Header als „secret“ markierbar (verschlüsselt gespeichert). Reservierte, nicht überschreibbare Header: `User-Agent`, `X-Plane-Signature`, `X-Plane-Delivery`, `X-Plane-Event`, `Content-Type`. Signatur HMAC-SHA256 über die **rohen Body-Bytes**. Secret regenerierbar, der alte Schlüssel ist sofort ungültig. Ergebnis und Response im Activity-Log. Im Unterschied dazu werden Workspace-Webhooks mit Exponential Backoff wiederholt und nach 5 Fehlschlägen deaktiviert (4xx kein Retry) (W21). **Präzisierung CE (Verifikation, R32):** Das CE wiederholt nur bei `requests.RequestException` (Verbindungsfehler, Timeout; `autoretry_for`, `retry_backoff=600`, `max_retries=5`, `retry_jitter=True`); **jede** HTTP-Antwort, auch 5xx, wird geloggt und nicht wiederholt. Nach dem 5. Fehlversuch `is_active=False` plus Mail `send_webhook_deactivation_email` | Enterprise Grid | W21, R32 |
| **Run script** | `run_script` | Führt ein Plane-Runner-Skript mit dem Event als Input und den an der Automation gesetzten Variablen aus (F19) | Enterprise Grid | R4, W21, W25 |

- Reihenfolge: sequenziell, Abbruch beim ersten Fehler (W21).
- Widerspruch: Die Setup-Schritte der Doku nennen „Run Script“ auch im Projekt-Flow, die Plan-Tabelle nur für Enterprise Grid (W21). Wegen ADR-001 unerheblich.
- **Konfidenz:** mittel.

---

### F13 – Global (Workspace-)Automations

- Workspace Settings → **Automations** (Sidebar-Label „Automations“). Titel „Automations“, Beschreibung „Standardize processes across your workspace with global automations.“ (`automations.global_automations.settings.*`, R4). Position in der Sidebar laut Screenshot D11: Gruppe „Features“, letzter Eintrag nach „Plane AI“, Icon ein Blitz (vermutlich `TriggerOutline` wie der CE-Projekt-Tab, UNVERIFIZIERT).
- Projektwahl: „Select projects to run this automation on“. Optionen **„All projects“** („Automation will run for all projects in the workspace.“) und **„Select projects“** („Automation will run for selected projects in the workspace.“, Placeholder „Select projects“) (`automations.global_automations.project_select.*`).
- Tabellen-Scope: „Global“ oder „Project“ mit „Multiple“ bzw. „All“ (R4).
- API: `/api/v2/workspaces/{slug}/automations/` (List-Filter `is_global`), `…/{pk}/status/`, Knoten, Kanten und Activities ohne Projektsegment. `project_ids` ersetzt das Set (W29). Welche Kombination aus `is_global` und `project_ids` „All projects“ bedeutet, ist UNVERIFIZIERT. Vorschlag: `is_global=true` ⇒ alle, auch künftige Projekte. `is_global=false` + `project_ids` ⇒ Auswahl.
- Berechtigung: Owner und Admin dürfen Workspace-Automationen sehen, anlegen, bearbeiten, aktivieren/deaktivieren und löschen (W48).
- Plan: Enterprise Grid (W21, W22). **CE:** fehlt. **Konfidenz:** mittel.

---

### F14 – Scheduled Automations

- Trigger-Gruppe „Time based“ → „Fixed schedule“ (R4). **Einzige erlaubte Aktion: „Run script“**, weil kein auslösendes Work Item existiert. Das Skript holt und ändert Items selbst (W21, W26).
- **Schedule mode** „Fixed“ | „Cron“ (`automations.trigger.schedule.schedule_mode*`):
  - Fixed: **Frequency** „Daily“ | „Weekly“ | „Monthly“.
    - Weekly: „On“ + „Select day“ (Wochentage; Mehrfachauswahl laut Validierung „Select at least one day of the week.“).
    - Monthly: „Every“ + „Day of month“ (ARIA „Day {day}“; Validierung „Select a day of the month.“).
    - „Time“ mit „Hour“ (Suffix „hr“), „Minute“ (Suffix „min“), „AM“/„PM“.
    - „Timezone“ (Placeholder „Select a timezone“).
    - Zusammenfassung im Canvas: „Every day at {time} ({timezone}).“ / „Every week on {days} at {time} ({timezone}).“ / „Every month on day {day} at {time} ({timezone}).“
  - Cron: „Enter Cron expression“ (Placeholder `0 9 * * 1-5`, 5 Felder). Ungültig: „Invalid cron expression.“. Vorschau: „This Cron expression runs "{description}".“. Canvas: „{description} ({timezone}).“ (R4; W21: 5-Feld-Cron).
- Auswertung „roughly every five minutes“ (W24). Jeder Run wird im Activity-Tab protokolliert: Zeit, Rückgabewert des Skripts, Fehlerdetails (W24).
- ~~Changelog März 2026: Bugfixes an Scheduled Automations und Runner (W23-Kontext).~~ **Korrektur (Verifikation):** W23 ist das Release v1.14.0 vom 02.09.2025 und kann keinen Eintrag aus März 2026 belegen; die Aussage hat keine Quelle und entfällt.
- Plan: Enterprise Grid (W24, W27). **CE:** fehlt. **Konfidenz:** hoch (UI), mittel (Laufzeit).
- **Migration:** Scheduler als Aspire-Worker (Cron-Parser, zum Beispiel Cronos, MIT-Lizenz). Zeitzonen über IANA-IDs (`TimeZoneInfo` mit ICU unter Linux). Monatstag > Monatslänge: Verhalten UNVERIFIZIERT.

---

### F15 – Decisions and Loops Automation

- Matrix: „Decisions And Loops Automation“ – „Use actions as triggers indefinitely in an automation flow.“, `comingSoon: true`, Business und Enterprise (R1). `BUSINESS_PLAN_FEATURES`: „Decision + Loops Automation“. `ENTERPRISE_PLAN_FEATURES`: „Unlimited and full Automation Flows“ (R2).
- Öffentliche UI-Doku: **keine** (Suche ohne Treffer). Das API-Modell ist aber bereits ein Graph: `node_type` `condition`, Kanten mit `execution_order` bei mehreren ausgehenden Kanten (W28, W29). Daraus folgen Verzweigungen. Schleifen und „actions as triggers“ sind UNVERIFIZIERT.
- **CE:** fehlt. **Konfidenz:** niedrig.
- **Empfehlung:** Datenmodell als Graph anlegen (F09). Die UI zuerst linear wie heute. Decisions/Loops als offene Frage (Abschnitt 4) mit Schutz gegen Endlosschleifen: maximale Tiefe und Knotenzahl je Run.

---

### F16 – Anzahl Automationen

- „Number of automations“ – „Total number of automation flows in your workspace“: Pro **5,000**, Business **10,000**, Enterprise **Unlimited** (R1).
- Keine Bestätigung in der Doku 2026 (Suche ohne Treffer).
- **ADR-001:** entfällt als Plan-Limit. Wird zur Instanz-Einstellung `Automations:MaxPerWorkspace` (Default: unbegrenzt bzw. `null`). **CE:** fehlt. **Konfidenz:** hoch (Repo-Wert), Relevanz gering.

---

### F17 – Ausführungslogs (Automation Activity)

- Öffnen: in der Automation Button **„Activity“** oben rechts. Zeigt jeden Run, die betroffenen Work Items, Erfolg oder Fehler und das volle Ausführungslog (W21).
- Filter (`automations.activity.filters.*`): „Show fails“ (Toggle), „All“, „Only activity“ (Konfigurationsänderungen), „Only run history“ (Runs). Run-History-Spalte bzw. -Feld „Initiator“ (`automations.activity.run_history.initiator`) (R4).
- Tabellen-Metriken: „Last run on“, „Last run status“, „Average duration“, „Executions“ (R4). API: `run_count`, `last_run_at` (W28).
- Activity-Datensatz siehe F09 (W28).
- **CE:** fehlt. **Konfidenz:** mittel.

---

### F18 – Automation-Consumer / Outbox-Architektur (Commercial-Infrastruktur)

#### Ist-Architektur der Commercial Edition (öffentlich belegt)

```
Django/API-Transaktion ──(PostgreSQL-Trigger via pgtrigger, gleiche Tx)──► Outbox-Tabelle
                                                                             │
                     outbox-poller (eigener async-Python-Prozess) ◄──────────┘  claim batch=250
                                │ publish
                                ▼
                RabbitMQ Exchange "plane.event_stream" (fanout)
                 ├─► Queue "plane.event_stream.automations" ─► automation-consumer (prefetch 10, event_types "issue")
                 ├─► Webhook-Queue "plane.webhook"           ─► webhook-consumer (prefetch 10)
                 └─► weitere Consumer (Live-Sockets, Integrations-Relays)
automation-consumer ──(run_script)──► node-runner :3000 (intern, HMAC RUNNER_HMAC_SECRET_KEY)
```

| Baustein | Fakten | Quelle |
|---|---|---|
| Outbox-Erzeugung | PostgreSQL-Trigger, als Django-Proxy-Modelle mit `pgtrigger` definiert und als Migration ausgeliefert. Gleiche Transaktion wie die Datenänderung: Rollback nimmt die Outbox-Zeile mit. Update-Trigger schreiben nur bei relevanten Spaltenänderungen. Fehler beim Outbox-Insert werden geloggt und blockieren den Write nicht. Begründung: Django-Signals verpassen `QuerySet.update()`, `bulk_create()`, `bulk_update()` und Raw-SQL | W32 |
| Outbox-Zeile | `event_id` (Idempotenz-Schlüssel), `event_type`, `entity_id`, `payload` (JSON: aktueller Zustand plus `previous_attributes` nur mit geänderten Feldern; große Felder wie `description` ausgeschlossen), `workspace_id`, `initiator_type`, `created_at`, `claimed_at`, `processed_at`. Partielle Indizes nur auf den unbearbeiteten Backlog | W32 |
| Initiator | Werte laut Modellkommentar `USER`, `SYSTEM`, `AUTOMATION`, laut Prosa `USER`, `SYSTEM.IMPORT`, `SYSTEM.AUTOMATION` (widersprüchlich, UNVERIFIZIERT). Die App setzt den Wert per Session-Variable vor dem Write. Consumer filtern danach. Das ist die Grundlage des Loop-Schutzes (F09) | W32, W21 |
| outbox-poller | Separater async-Python-Prozess. Claim über `UPDATE … WHERE id IN (SELECT … ORDER BY id LIMIT 250 …)`; `FOR UPDATE SKIP LOCKED` UNVERIFIZIERT. At-least-once, Consumer deduplizieren über `event_id`. Env: `OUTBOX_POLLER_INTERVAL_MIN` 0.25 s, `…_INTERVAL_MAX` 2 s, `…_BATCH_SIZE` 250, `…_MEMORY_LIMIT_MB` 512 (Doku) bzw. 400 (Helm), `…_MEMORY_CHECK_INTERVAL` 30, Pool `…_POOL_SIZE` 4, `…_POOL_MIN_SIZE` 2, `…_POOL_MAX_SIZE` 10, `…_POOL_TIMEOUT` 30.0, `…_POOL_MAX_IDLE` 300.0, `…_POOL_MAX_LIFETIME` 3600, `…_POOL_RECONNECT_TIMEOUT` 5.0, `…_POOL_HEALTH_CHECK_INTERVAL` 30 (Doku) bzw. 60 (Helm). Entrypoint `./bin/docker-entrypoint-outbox-poller.sh`, Image `makeplane/backend-commercial` | W32, D2, H2, H5 |
| automation-consumer | Env `AUTOMATION_EVENT_STREAM_QUEUE_NAME` = `plane.event_stream.automations`, `AUTOMATION_EVENT_STREAM_PREFETCH` = 10, `AUTOMATION_EXCHANGE_NAME` = `plane.event_stream`, `AUTOMATION_EVENT_TYPES` = `issue` (nur Helm H1; in D2 nicht dokumentiert). `AUTOMATION_CONSUMER_REPLICAS` Default 1, `OUTBOX_POLLER_REPLICAS` Default 1 (D2). Helm-Defaults `services.outbox_poller.enabled`, `services.automation_consumer.enabled`, `services.webhook_consumer.enabled`, `services.runner.enabled` jeweils `false` (H6) – die Dienste sind also optional zuschaltbar. Entrypoint `./bin/docker-entrypoint-automation-consumer.sh`. Helm `services.automation_consumer.enabled` Default `false`, Ressourcen 1000Mi/500m Limit | D2, D5, H1, H5, H6 |
| webhook-consumer | `WEBHOOK_QUEUE_NAME` = `plane.webhook`, `WEBHOOK_PREFETCH_COUNT` = 10. Liveness `pgrep -f "python"` | H4, H5 |
| RabbitMQ | `RABBITMQ_HOST` plane-mq, Port 5672, User/Pass/VHost `plane`, `AMQP_URL` | D2 |
| Runner | siehe F19 | D3, H3 |
| HA | `outbox_poller`, `automation_consumer`, `runner` sind Tier-1-Dienste und eignen sich für Spot-Pools (Batch-Worker) | D7 |

#### CE-Vergleich
Im CE gibt es keine Outbox und kein RabbitMQ für Events. Seiteneffekte laufen über Celery-Tasks: `issue_activity.delay(...)` (R20, R25) und `webhook_task` (R32). Der Zeitplan läuft über Celery Beat (R21).

#### Migrationshinweise (.NET, ADR-000/004)
- **Outbox in PostgreSQL** beibehalten. Erzeugung entweder als DB-Trigger (wie das Original, fängt auch Bulk-SQL ab) oder als EF-Core-`SaveChanges`-Interceptor plus Pflicht für Bulk-Updates (`ExecuteUpdate`), eigene Outbox-Writes zu erzeugen. **Empfehlung:** DB-Trigger als Migration, weil EF Core `ExecuteUpdate`/`ExecuteDelete` am Change-Tracker vorbeilaufen.
- **Broker optional** (ADR-004, airgapped): Standardbetrieb ohne RabbitMQ. Poller und Consumer als Aspire-Worker-Projekte, die die Outbox direkt mit `FOR UPDATE SKIP LOCKED` lesen und je Consumer-Gruppe einen Offset bzw. eine Zustellungstabelle führen. RabbitMQ bleibt als optionale Aspire-Ressource für Skalierung. Endgültige Wahl gehört ins Architektur-Dokument (Offene Punkte).
- `initiator_type` als PostgreSQL-Session-Variable (`SET LOCAL plane.initiator_type = 'AUTOMATION'`) setzen, damit Trigger ihn lesen. Das ist der Loop-Schutz.
- Konfigurations-Keys 1:1 als `Outbox:*`/`Automation:*`-Optionen übernehmen (Defaults siehe Tabelle).

#### Konfidenz
Hoch für Dienste und Env-Variablen (D2, H1 bis H6), mittel für das interne Outbox-Schema (W32, Blog).

---

### F19 – Plane Runner (Schnittstelle zum Cluster; Detail ggf. eigenes Dokument)

- Workspace Settings → **Plane Runner** → **Scripts** („Plane Runner“, „Scripts“, „New Script“, Beschreibung „Automate your workflows with custom scripts and automation rules.“; `workspace_settings.settings.runners.*`, R9). **Script Type**: Automation, Workflow Transition, Cron Trigger (W1/W25-Zusammenfassung). Sidebar-Position laut Screenshot D11: Gruppe „Features“, dritter Eintrag nach „Projects“, „Integrations“.
- **Ergänzung (Verifikation):** Neben Scripts gibt es einen Bereich **Functions** (wiederverwendbare Logik, die Scripts aufrufen; als eingebaut belegt sind `getSiblings`, `getChildren`, `addComment`, `addLabel`, `postToSlack`, `httpRequest({ url, method?, headers?, body? })` → `{ status, headers, data }` (wirft bei Nicht-2xx); `getChildren` fehlt in der obigen Aufzählung dieses Dokuments; Quelle Schwester-Dok. `22-paid-architektur-selfhosting-dienste.md` P03-F28, dort aus docs.plane.so/automations/plane-runner). Repo-Beleg: eigene Empty-State-Illustrationen `runner-scripts`, `runner-functions` und `script` (R30). Die vollständige Spezifikation des Runners liegt in Dok. 22 (P03-F28); hier nur die Schnittstelle.
- JavaScript oder TypeScript in einer isolierten Sandbox. Skripte exportieren `async function main(...)`, event-getriggert mit Event-Input und einem `variables`-Record (W25).
- **Variables**: Key-Value-Strings, am Skript definiert, Werte werden beim Anhängen an Automation, Schedule oder Workflow gesetzt (W25).
- **Functions**-Global, Aufruf per Name mit einem Parameterobjekt. Beispiele `getSiblings`, `addComment`, `addLabel`, `postToSlack`, `httpRequest`. Runner erkennt benutzte Functions beim Build (W24, W25). **Plane SDK**: Work Items lesen und ändern, States und Labels listen, Kommentare, Relationen, Advanced Search (W24).
- Ausgehendes HTTP nur zu je Skript erlaubten Domains (W24). Module-Imports und Node-APIs wie `fs` gesperrt, `while(true)`/`for(;;)` gesperrt (W25, W26).
- **Limits:** Ausführung 10 s, Init 5 s, 128 MB (W24). Helm: `EXECUTION_TIMEOUT_MS` 10000, `INIT_TIMEOUT_MS` 5000, `ISOLATE_MEMORY_MB` 128 (H3).
- **Test** ohne Speichern: Security-Validierung, Build (Function-Erkennung), Ausführung mit Input, Ergebnis oder Fehler (W25).
- Betrieb: Dienst `node-runner`, intern Port 3000, `GET /health` → `{"status":"ok"}`. Django `GET /api/workspaces/{slug}/runnerctl/health/` (Session-Auth, Workspace-Admin) → `{"is_available": bool}` (D3). HMAC zwischen API und Runner (`RUNNER_HMAC_SECRET_KEY`), `API_BASE_URL` = interne API `:8000` (H3).
- Plan: Enterprise Grid (W24, W25). **CE:** fehlt.
- **ADR-002-Konflikt:** Kein Node.js zur Laufzeit. Der Runner braucht eine **.NET-eingebettete JS-Engine** (zum Beispiel Jint mit Timeout-, Memory- und Statement-Limits, oder ClearScript V8). TypeScript-Transpilation ohne Node ist offen (Abschnitt 4).
- **Konfidenz:** mittel.

---

### F20 – Project Templates

#### Funktionsbeschreibung (UI & Verhalten)

**Verwaltung:** Workspace Settings → **Templates** (Tab-Titel, Heading und Beschreibung „Save 80% time spent on creating projects, work items, and pages when you use templates.“; `workspace_settings.settings.templates.*`, R9; gleicher Text `templates.settings.*`, R5). Button **„Create template“** mit Dropdown „Project templates“ / „Work item templates“ / „Page templates“ (`templates.settings.options.*`). Buttons „New project template“, „New work item template“, „New page template“ (R5). Ohne Berechtigung: „Contact your workspace admin to create templates“ (`templates.settings.create_template.no_permission.workspace`). Leerzustand: „No templates yet“ / „Reduce setup time by creating templates for projects, work items, and pages — and start new work in seconds.“ / „Create template“ (`settings_empty_state.template_setting.*`, R8). Button „Create your first template“ (`templates.empty_state.no_templates.button`). Illustration `template` (R30).

**Formular** (`templates.settings.form.project.*`, R5; W33):
| Bereich | Feld | Text/Regel |
|---|---|---|
| Template | Name | Placeholder „Name your project template.“; Pflicht „Template name is required“; „< 255“ |
| Template | Beschreibung | „Describe when and how to use this template.“ |
| Projekt | Name | „Name your project.“; Pflicht „Project title is required“; „< 255“ |
| Projekt | Beschreibung | „Describe the purpose and goals of this project.“ |
| Projekt | Cover Image, Logo/Emoji | W33; CE-Komponenten `ProjectCreateHeader` (Cover, Emoji/Icon-Picker) (R16) |
| Projekt | Properties: Visibility (`network`), Lead, Datumsfelder | W33 |
| Optional | States, Labels, Work Item Types | W33. Leerzustände: „No labels yet. Create labels to help organize and filter work items in you project.“ (Tippfehler „you“ im Original übernehmen), „No modules yet. Organize work into sub-projects with dedicated leads and assignees.“ (`templates.empty_state.no_labels|no_modules`) |
| Optional | Initiale Work Items (seit 30.07.2025) inklusive Sub-Work-Items | W41. Leerzustände „No work items yet. Add one to structure your work better.“, „No sub-work items yet. Add one to structure your work better.“ (`templates.empty_state.no_work_items|no_sub_work_items`) |
| Buttons | — | „Create project template“ / „Update project template“ |

Laut Matrix speichern Project Templates „states, workflows, automation, and other project settings“ (R1). Laut v1.9.0: Projekt-Properties, eigene States und Labels, aktivierte Features (W18). Sidebar-Position der Workspace-Seite „Templates“ laut Screenshot D11: Gruppe „Features“ zwischen „Releases“ und „Relations“.

**Ergänzung (Verifikation) – Herkunftsverweis am Projekt:** Das öffentliche Projekt-Objekt der API v1 hat das EE-Feld `template_id` („UUID of the project template used to create this project.“, D10). Im CE-Modell `Project` fehlt es (`apps/api/plane/db/models/project.py`, grep ohne Treffer). Für die neue Plattform: `Project.TemplateId` (nullable FK, `ON DELETE SET NULL`) beim „Use template“ setzen.

**Anwendung:**
1. Im **Projekt-Create-Modal** oben links ein Template-Picker „Pick a project template“ (`templates.dropdown.label.project`), Eintrag „Add new template“ (`templates.dropdown.add.project`), Leer „No templates found.“ (`templates.dropdown.no_results.project`). Das Projekt wird vorkonfiguriert (W33). CE-Hooks: `CreateProjectModal.templateId`, `CreateProjectForm.templateId` (Prop vorhanden, nicht ausgewertet), `ProjectCreateHeader.handleTemplateSelect` (Prop vorhanden, nicht ausgewertet) (R16).
2. Auf der Templates-Seite **„Use template“** (Ladezustand „Applying“, `templates.settings.use_template.button.*`). Öffnet das Projekt-Create-Formular mit allen Template-Werten vorbelegt (W33).
- Herkunftshinweis „Derived from workspace“ / „Derived from project“ (`templates.settings.template_source.*`).
- Toasts mit `{templateName}` und `{templateType}`: „Template created“ / „{templateName}, the {templateType} template, is now available for your workspace.“. Update „Template changed“. Delete „Template deleted“. Fehlertexte siehe Anhang A. Hinweis: Tippfehler im Original („We couldn't delete that template this.“) für 1:1 übernehmen.
- Löschdialog: „Delete template“ – „Are you sure you want to delete template-“ {Name} „? All of the data related to the template will be permanently removed. This action cannot be undone.“ (`templates.delete_confirmation.*`).

**Berechtigungen:** Nur Owner und Admin erstellen, veröffentlichen, bearbeiten und löschen Project Templates. Members nutzen sie nur zum Anlegen von Projekten (W48).

#### Plan-Tier
Business (R1 „Project Templates“ Business und Enterprise; R1 `planHighlights.business` „Project Templates“; R2; W18; W45).

#### CE-Status
Stub/UI-Hülle (R16; Texte R5, R6 `project_settings.templates.*`, R8, R9). Kein Modell, keine API, keine Route (`TWorkspaceSettingsTabs` ohne `templates`, R28).

#### Datenmodell-Hinweise (API v2, W36)

`ProjectTemplate`:
| Feld | Bedeutung |
|---|---|
| `id`, `workspace_id` | — |
| `name`, `short_description` (nullable, einzeilig), `description_html` | Template-Metadaten |
| `is_published` (Default `false`), `is_verified` (nur von Plane gesetzt, filterbar, nicht schreibbar), `category_ids` (UUID[], in Responses read-only, Filter `category_id`) | Marketplace (F23) |
| `template_data` (jsonb, in der Ablage frei, bei Create/Update shape-validiert) | Projekt-Blueprint, siehe unten |

`template_data`-Schlüssel (W36):
| Schlüssel | Inhalt |
|---|---|
| Projektfelder | `name`, `description`, `network`, `logo_props`, `cover_asset` (externe URL oder Plane-Asset-Pfad; `""` = kein Cover), `start_date`, `target_date`, Lead/Members (UNVERIFIZIERT im Detail) |
| Feature-Toggles | `module_view`, `cycle_view`, `issue_views_view`, `page_view`, `intake_view`, `is_time_tracking_enabled`, `is_issue_type_enabled`, `is_project_updates_enabled`, `is_epic_enabled`, `is_milestone_enabled` |
| `states[]` | `{ id (vom Client gewählte UUID), name, color, sequence (Zahl), group ∈ backlog|unstarted|started|completed|cancelled|triage, description?, default? }` |
| `project_state` | `{ id, name, group }` – Lebenszyklus-State des Projekts (Default `{}`) |
| `labels[]` | `{ id, name, color (≤7 Zeichen) }` |
| `estimates` | Schätzsystem (Schema UNVERIFIZIERT) |
| `workitem_types[]` | `{ id, name, logo_props, is_epic, properties, description?, is_default?, is_active? }` |
| `epics` | `{ id, name, properties }` (Epic-Typ) |
| `members` | Mitglieder und Rollen (Schema UNVERIFIZIERT) |
| `intake_settings` | `{ is_in_app_enabled, is_email_enabled, is_form_enabled }` |
| `workflows`, `milestones`, `modules`, `recurring_work_items`, `automations` | „stored as sent“, ohne dokumentiertes Schema (in Beispielen `{}`) |
| `workitems[]` | Starter-Work-Items in Anlagereihenfolge: `{ name (Pflicht, ≤255), description_html, priority, state {id,name,group}, assignees, labels, type, modules, properties }` |

#### API-Hinweise
| Methode | Pfad | Verhalten | Quelle |
|---|---|---|---|
| GET/POST | `/api/v2/workspaces/{slug}/project-templates/` | Liste (Filter `category_id`), Create | W36 |
| GET/PATCH/DELETE | `…/project-templates/{pk}/` | PATCH: Top-Level partiell. `template_data`: Merge **oder** vollständige Ersetzung, widersprüchlich dokumentiert (UNVERIFIZIERT). Gebündelte `workitems` werden immer vollständig ersetzt | W36 |
| POST | `…/project-templates/{pk}/use/` | Synchron: Projekt, Members, States. Hintergrundjob: Labels, Estimates, WITs, Epics, Modules, Starter-Work-Items. Verknüpft den Workspace-Default-WIT bei Workspace-Typen. `network`, `timezone`, `priority` und Daten kommen aus dem Request-Body, nicht aus dem Template | W36 |
| POST | `…/project-templates/copy/` | Body `{ template_id }`. Quelle muss `is_published` sein, darf in einem anderen Workspace liegen. Kopie: `is_published=false`, `is_verified=false`, `category_ids=[]`, **ohne** `workitems`. Name „… (copy)“-Regel. Scope `templates.projects:write`. 404 unbekannt oder unveröffentlicht | W36 |
| POST | `/api/v1/workspaces/{workspace_slug}/projects/templates/use/` | Body `template_id` (Pflicht, gleicher Workspace), `name`, `identifier`, `description`, `network` (0 secret, 2 public), `project_lead` (wird Projekt-Admin). Kopiert States, Labels, Estimates, Modules, Work Items. Body-Felder überschreiben Template-Defaults. Scope `write` oder `projects:write`. Response 201 mit reduziertem Projekt-Objekt (`id`, `name`, `description`, `identifier`, `network`, `project_lead`, `created_at`, `updated_at`) | D6 |

#### Edge-Cases
- Die Hintergrundphase führt dazu, dass Labels, Work Items usw. erst verzögert sichtbar sind (W36). Das Angular-Frontend sollte nach „use“ einen Lade- bzw. Refresh-Zustand haben (Empfehlung).
- Identifier- und Namens-Kollisionen beim Anlegen: wie CE-Projekt-Create (`PROJECT_NAME_ALREADY_EXIST`, R16 `root.tsx`).
- State-IDs im Template sind Client-UUIDs. Beim Anwenden werden neue IDs vergeben und Referenzen (`workitems[].state.id`, Workflows) umgemappt (Annahme, UNVERIFIZIERT).

#### Quellen
R1, R2, R5, R6, R8, R9, R16, R28, R30, D6, W18, W33, W36, W41, W45, W48.

#### Konfidenz
Mittel.

---

### F21 – Work Item Templates

#### Funktionsbeschreibung
- **Ebenen:** Workspace (Workspace Settings → Templates; befüllt neue Work Items projektübergreifend) und Projekt (Project Settings → Templates; „Templates“ / „Save 80% time …“, `project_settings.templates.*`, R6) (W34, W38). **Ergänzung (Verifikation):** Es gibt zwei Leerzustände: `settings_empty_state.template_setting` (Workspace: „No templates yet“ / „Reduce setup time by creating templates for projects, work items, and pages — and start new work in seconds.“ / CTA „Create template“) und `settings_empty_state.templates` („No templates yet“ / „Reduce setup time by creating templates for work items, and pages — and start new work in seconds.“ / CTA „Create your first template“). Der zweite nennt keine Projekt-Templates; Schluss: Er ist der Leerzustand der **Projekt**-Templates-Seite, und auf Projektebene gibt es nur Work-Item- und Page-Templates (R8; Zuordnung UNVERIFIZIERT).
- **Anlage (Projekt):** Project Settings → Templates → „Create template“ → „Work item template“ (W34). Formular (`templates.settings.form.work_item.*`, R5):
  - Template-Name „Name your work-item template.“ (Pflicht, < 255), Beschreibung „Describe when and how to use this template.“.
  - Work-Item-Titel „Give this work item a title.“ (Pflicht „Work item title is required“, < 255), Beschreibung „Describe this work item so its clear what you will accomplish when you complete this.“ (Tippfehler „its“ im Original).
  - Properties: Labels, Assignees, Modules (W34), dazu Priority, State, Type und Custom-Properties laut API-Seed (W37). Cycle, Estimate und Datumsfelder sind nicht belegt (UNVERIFIZIERT).
  - **Sub-Work-Items**, die mit dem Haupt-Item entstehen (seit 30.07.2025, W41).
  - Buttons „Create work-item template“ / „Update work-item template“. Ohne Berechtigung „Contact your project admin to create templates“ (`templates.settings.create_template.no_permission.project`).
- **Anwendung:** Work Items → „+“ → Work Item Type wählen → **Templates-Icon** (Tooltip „Pick a work item template“, `templates.dropdown.tooltip.work_item`) → Template aus dem Dropdown (Eintrag „Add new template“, leer „No templates found.“). Das Formular wird vorbelegt und bleibt vor dem Speichern editierbar (W34, R5).
- **Formular-Verhalten** (im CE schon implementiert, nur der Provider ist No-op; R15 `form.tsx`):
  - Ändert sich `workItemTemplateId` und ist der Editor bereit, ruft das Formular `handleTemplateChange({ workspaceSlug, reset, editorRef })` auf. Das setzt Formular und Editor-Inhalt.
  - Während `isApplyingTemplate` ist das Formular gesperrt (`isDisabled = isSubmitting || isApplyingTemplate`).
  - Wechsel des **Projekts** bei gesetztem Template: Template-ID zurücksetzen (`setWorkItemTemplateId(null)`), Formular auf `DEFAULT_WORK_ITEM_FORM_VALUES` mit neuem `project_id`, Editor leeren (`editorRef.current?.clearEditor()`). **Präzisierung (Verifikation):** Das geschieht nur, wenn das Formular `isDirty` ist; sonst passiert beim Projektwechsel nichts am Template. Ohne Template wird bei `isDirty` `getUpdateFormDataForReset(projectId, getValues())` angewendet (`form.tsx` Z. 162–176). Das Anwenden des Templates (`handleTemplateChange`) startet nur, wenn `editorRef.current` existiert (Z. 201–210).
  - Mit „Create more“ und Template wird das Template nach dem Speichern erneut angewendet. Ohne Template wird normal zurückgesetzt.
  - `IssueModal` akzeptiert `templateId` (Vorbelegung von außen, zum Beispiel aus „Use template“) (R15 `modal.tsx`, `provider.tsx`).
- Berechtigungen: Projekt-Templates anlegen, bearbeiten und löschen nur Projekt-Admin, Contributor sieht sie. Workspace-Templates anlegen nur Owner/Admin. Anwenden darf jeder, der Work Items anlegen darf (W48).

#### Plan-Tier
Pro (R1 `planHighlights.pro` „Work item templates“; W18 „Pro and Business“; W34 mit „Pro“ gelabelt).

#### CE-Status
Stub/UI-Hülle: `TIssueModalContext` mit `workItemTemplateId`, `setWorkItemTemplateId`, `isApplyingTemplate`, `setIsApplyingTemplate`, `handleTemplateChange`. Typ `THandleTemplateChangeProps { workspaceSlug, reset, editorRef }`. Provider liefert `null`/No-op (R15).

#### Datenmodell / API (W37, W38)
- `WorkItemTemplate { id, workspace_id, project_id? (null = Workspace-Ebene), name, short_description, description_html, is_published, template_data }`.
- `template_data`: `{ name, description_html, priority, state, labels, assignees, modules, type, properties }` plus Sub-Work-Items (Schlüssel UNVERIFIZIERT).
- Projekt: `/api/v2/workspaces/{slug}/projects/{project_id}/work-item-templates/` (`project_id` als UUID oder Identifier wie `ENG`), `…/{pk}/use/` (Body optional `name`, `project_id`) → erzeugt ein Work Item. Workspace: `/api/v2/workspaces/{slug}/work-item-templates/`. Bei Create sind `name` und `template_data` Pflicht.
- Plane Compose: `schema/workitem_templates.yaml` („populated on pull“) (D1).

#### Quellen
R1, R5, R6, R15, D1, W18, W34, W37, W38, W41, W48.

#### Konfidenz
Mittel (hoch für das Formularverhalten aus R15).

---

### F22 – Page Templates

- **Anlage:** Workspace Settings → Templates → „Create template“ → „Page template“: Name, Beschreibung, Seiteninhalt (W35). Formular (`templates.settings.form.page.*`, R5): Template-Name „Name your page template.“ (Pflicht, < 255), Beschreibung, Seitenname Placeholder „Untitled page“ (nur „Page name should be less than 255 characters“, kein Pflichtfeld), Buttons „Create page template“ / „Update page template“.
- Verwaltung auch in Project Settings → Templates (W35).
- **Anwendung:** In Projekt-Pages oder Wiki „+“ → Template-Picker **„Choose from template“** (`templates.dropdown.label.page`) → die neue Page enthält Inhalt und Formatierung des Templates (W35). Leer: „There are no templates you have access to.“ / „Please create a template“. Suche ohne Treffer: „That didn't match a template.“ / „Try searching by other terms.“ (`templates.empty_state.page.*`).
- **Plan:** Pro (R1 Knowledge-Management-Zeile „Templates“: „Use pages as templates for your project, team, or workspace.“ Pro und höher; W45 „Page Templates are available on Pro and above“).
- **CE:** fehlt. Keine Template-Hooks in `apps/web/components/pages` oder `packages/editor` (grep ohne Treffer).
- **API (W39):** Workspace `/api/v2/workspaces/{slug}/page-templates/` (v1: `/pages/templates/`, nicht paginiert), Projekt `/api/v2/workspaces/{slug}/projects/{project_id}/page-templates/`. Unter Governance liefert die Projekt-Route 409 `templates_managed_at_workspace`. Felder `name`, `short_description`, `description_html` (beschreibt das **Template**), `is_published`, `template_data` = Page-Seed `{ description_html (Seiteninhalt), logo_props, view_props, color, parent {id, project_id, project_identifier} }`. PATCH auf `template_data` ersetzt den Seed vollständig, ausgelassene Keys gehen auf Default (`{}`). Ein nicht leeres `parent` braucht alle drei IDs. Ein Endpunkt „Page aus Template erzeugen“ ist nicht dokumentiert. Die Anwendung läuft clientseitig (Inhalt in die neue Page kopieren). UNVERIFIZIERT.
- Plane Compose: `schema/page_templates.yaml` (D1).
- **Migration:** `template_data.description_html` muss beim Anwenden in den Yjs-Dokumentzustand der neuen Page (ADR-002) überführt werden. Der Server erzeugt daraus das initiale Y-Doc (Empfehlung; Details im Editor-Dokument).
- **Konfidenz:** mittel.

---

### F23 – Pre-defined Templates und Template-Marketplace

- Matrix: „Pre-defined work item Templates“ – „Choose from our available work item templates that customize work item types and properties for several use cases.“, `comingSoon: true`, Pro, Business, Enterprise (R1).
- Öffentliche Galerie `plane.so/templates` mit „By Plane“-Projekt-Templates (zum Beispiel „Web application development“, „Website updates and landing pages“). Wünsche für neue Templates nimmt Plane über die Seite an (W40). Inhalte (States, Labels) dort nicht im Detail belegt.
- **Publish-to-Marketplace-Formular** (R5 `templates.settings.form.publish.*`): Aktion „Publish to Marketplace“ bzw. „Publish settings“ (ICU `select` auf `isPublished`), „Unpublish from Marketplace“. Titel „Make your template discoverable and recognizable.“. Felder:
  | Feld | Label | Validierung |
  |---|---|---|
  | `name` | „Name of template“ | Pflicht, < 255 |
  | `short_description` | „Short description“ | Pflicht |
  | `description` | „Description“ | Pflicht |
  | `category` | „Category“ (Mehrfachauswahl: „You can choose more than one.“) | mindestens eine |
  | `keywords` | „Keywords“ (kommagetrennt) | mindestens eines |
  | `website` | „Website URL“ | gültige URL, < 800 |
  | `company_name` | „Company name“ | Pflicht, < 255 |
  | `contact_email` | „Contact email“ | gültige E-Mail, < 255 |
  | `privacy_policy_url` | „Link to your privacy policy“ | gültige URL, < 800 |
  | `terms_of_service_url` | „Link to your terms of use“ | gültige URL, < 800 |
  | `cover_image` | „Add a cover image that will be displayed in the marketplace“ (Upload mit Drag-and-Drop, „Upload and save“, „Remove“) | Pflicht; Fehler „Invalid file or exceeds size limit. Please try again.“ |
  | `attach_screenshots` | „Include pictures you think will make viewers of this template.“ | mindestens ein Screenshot |
- Unpublish-Dialog: „Unpublish template“ – „Are you sure you want to unpublish template-“ {Name} „? This template will no longer be available to users on the marketplace.“. Toasts „Template unpublished“ (R5).
- API: `is_published`, `is_verified`, `category_ids`, Copy-Endpunkt (F20, W36).
- **CE:** fehlt. **Konfidenz:** mittel (Formular), niedrig (Galerie-Inhalte).
- **ADR-004 (airgapped):** keine externe Galerie. **Empfehlung:** Pre-defined Templates als mitgelieferte Seed-Daten (Instanz-Katalog). „Marketplace“ = instanzweiter Katalog veröffentlichter Templates über Workspaces hinweg, mit Instanz-Admin als „Verifizierer“. Offene Frage an den Auftraggeber.

---

### F24 – Recurring Work Items

#### Funktionsbeschreibung (UI & Verhalten)
- **Ort:** Project Settings → **Recurring work items** (linke Navigation) → „Create recurring work item“ (W42). Heading „Recurring work items“, Beschreibung „Set your repeatable work once, and we’ll take care of the repeats. You’ll see everything right here when it’s time.“ (`recurring_work_items.settings.*`, R7). Nav-Label `common.recurring_work_items` (R10). Icon `RecurringWorkItemsOutline` (R29).
- Leerzustand: „No recurring work item yet“ / „Set up recurring work items to automate repeat tasks and stay on schedule effortlessly.“ / CTA „Create recurring work item“ (`settings_empty_state.recurring_work_items.*`, R8). Button „Create your first recurring work item“ (`recurring_work_items.empty_state.no_templates.button`).
- **Formular:** wie ein normales Work Item, das ist der „Blueprint“, der bei jedem Lauf kopiert wird (W42). Dazu Abschnitt **„Schedule“** (`…form.interval.title`): Startdatum (Pflicht „Start date is required“), Intervalltyp (Pflicht „Interval type is required“), optionales Enddatum (W42, R7). Buttons „Create recurring work item“ / „Update recurring work item“, Modal-Titel „New recurring work item“ / „Update recurring work item“.
- **Frequenzen:** daily, weekly, monthly, yearly (API `interval_type`, Default `monthly`) mit `interval_count` (Default 1; 2 + weekly = alle zwei Wochen). Laut Changelog zusätzlich „quarterly“ (W44). In der API wäre das `monthly` × 3. UI-Option „quarterly“ UNVERIFIZIERT (W43, W44).
- **Verankerung:** weekly am Wochentag von `start_at`, monthly am Monatstag von `start_at`. Keine separate Wochentags- oder Monatstag-Auswahl (W43).
- **Zeitpunkt:** Jeder Lauf ist um **00:05 Projekt-Zeitzone** fällig. `start_at` wird auf 00:05, `end_at` auf 23:59:59 der jeweiligen Tage gesetzt und in UTC gespeichert. `start_at` heute ⇒ erstes Item sofort. `start_at` in der Vergangenheit ⇒ erster Lauf am nächsten planmäßigen Datum nach jetzt. Änderung von `start_at`, `interval_type` oder `interval_count` berechnet `next_scheduled_at` neu (W43).
- **Ende:** Ohne Enddatum unbegrenzt (W42). `end_at` = letzter möglicher Lauftag (W43).
- **Bearbeiten** wirkt nur auf künftige Instanzen. Erzeugte Items bleiben unverändert (W42).
- **Kein Pause/Resume** in UI und API. `enabled` ist nur lesbar. Stoppen per `end_at` oder Löschen (W42, W43). Plane setzt `enabled=false` selbst, wenn der Plan das Feature nicht mehr enthält. Nach ADR-001 entfällt das.
- **Historie:** sichtbar, wann geändert wurde, welche Läufe es gab und ob etwas fehlschlug (W23).
- Kann von einem **Work Item Template** ausgehen (W23).
- Toasts mit `{name}`: „Recurring work item created“ / „{name}, the recurring work item, is now available for your workspace.“. Changed, Deleted und Fehlertexte siehe Anhang A. Löschdialog „Delete recurring work item“ – „Are you sure you want to delete recurring work item-“ {Name} „? All of the data related to the recurring work item will be permanently removed. This action cannot be undone.“ (R7).
- **Berechtigung:** Anlegen nur Projekt-Admin („Contact your project admin to create recurring work items“, `recurring_work_items.settings.create_button.no_permission`, R7). Commenter und Guests können nicht lesen oder schreiben (W43). Governance sperrt Projekt-Admins (W33).

#### Plan-Tier
Business (R7 „Upgrade to Business to make recurring work feel effortless.“; W42; W45). Eingeführt in v1.14.0 (02.09.2025, W23) bzw. Changelog 01.09.2025 (W44).

#### CE-Status
fehlt.

#### Datenmodell-Hinweise (API v2, W43)
`RecurringWorkItem` (flaches API-Objekt aus Blueprint plus Schedule):
| Feld | Typ/Regel |
|---|---|
| `id`, `project_id`, `workspace_id` | — |
| `work_item_blueprint_id` | Referenz auf den Blueprint (Vorschlag: eigene Tabelle `WorkItemBlueprint` mit Work-Item-Feldern) |
| Blueprint-Felder | `name`, `priority`, `state_id`, `assignee_ids` und weitere Work-Item-Felder (vollständige Liste UNVERIFIZIERT; Annahme: wie Work-Item-Create plus `type_id`, `label_ids`, `module_ids`, `description_html`, Custom-Property-Werte) |
| `start_at`, `end_at` | timestamptz (00:05 bzw. 23:59:59 Projekt-TZ) |
| `interval_type` | `daily`\|`weekly`\|`monthly`\|`yearly` (Default `monthly`) |
| `interval_count` | int ≥ 1 (Default 1) |
| `next_scheduled_at`, `last_run_at`, `enabled`, `schedule_description` | read-only |
| Läufe (Vorschlag) | `RecurringWorkItemRun { id, recurring_work_item_id, scheduled_for, status, created_work_item_id, error, created_at }` (Basis für „track runs, check if anything failed“, W23) |

#### API-Hinweise
`/api/v2/workspaces/{slug}/projects/{project_id}/recurring-work-items/` (list, get, create, update, delete). Ohne Plan-Feature → 402 (entfällt) (W43).

#### Migrationshinweise
Scheduler-Worker (Aspire) prüft minütlich `next_scheduled_at <= now()` mit `FOR UPDATE SKIP LOCKED`. Erzeugt das Work Item über denselben Domain-Service wie die UI (Workflow-Enforcement, Activity, Notifications, Outbox). Monatsende-Regel (Start am 31.) ist UNVERIFIZIERT. Vorschlag: letzter Tag des Monats.

#### Quellen
R7, R8, R10, R29, W23, W33, W42, W43, W44, W45.

#### Konfidenz
Mittel bis hoch.

---

### F25 – Auto-Archive / Auto-Close (im CE vorhanden; Basis der Erweiterungen)

#### Funktionsbeschreibung (CE, vollständig)
- **Seite:** Project Settings → Automations (`/:workspaceSlug/settings/projects/:projectId/automations`, R28). Heading „Automations“, Beschreibung „Configure automated actions to streamline your project management workflow and reduce manual tasks.“ (`project_settings.automations.*`, R6). Nur Projekt-Admins, sonst `NotAuthorizedView section="settings" isProjectView` (R23). Seitentitel `${project.name} - Automations` (R23).
- **Auto-archive** (`AutoArchiveAutomation`, R23): Icon `RestoreOutline` in `size-10`-Kachel (`bg-layer-2`). Titel „Auto-archive closed work items“, Beschreibung „Plane will auto archive work items that have been completed or canceled.“. Switch (`size="sm"`). Einschalten setzt `archive_in: 1`, Ausschalten `archive_in: 0`. Aktiv: Zeile „Auto-archive work items that are closed for“ mit Select der Monate `PROJECT_AUTOMATION_MONTHS` = 1, 3, 6, 9, 12 (Label `workspace_projects.common.months_count`, R24). Ein Wert außerhalb der Presets wird in die Liste aufgenommen und sortiert. Footer-Button „Customize time range“ (`common.customize_time_range`) öffnet `SelectMonthModal`.
- **Auto-close** (`AutoCloseAutomation`, R23): Icon `AutoCloseOutline` (`text-danger-primary`). Titel „Auto-close work items“, Beschreibung „Plane will automatically close work items that haven't been completed or canceled.“. Einschalten setzt `{ close_in: 1, default_state: <erster State der Gruppe cancelled> }`, Ausschalten `{ close_in: 0, default_state: null }`. Aktiv: „Auto-close work items that are inactive for“ (Monate wie oben) und „Auto-close status“ (Select nur über States der Gruppe `cancelled`, mit `StateGroupIcon`; deaktiviert, wenn es nur einen solchen State gibt; Trigger zeigt den gespeicherten `default_state` oder den ersten cancelled-State).
- **SelectMonthModal** (R23): Dialog „Customize time range“, Zahlenfeld (Placeholder „Enter Months“, Suffix „Months“, min 1, max 12, Fehler „Select a month between 1 and 12.“), Buttons „Cancel“ / „Submit“ („Submitting...“).
  - **Edge-Cases (Verifikation, R37):** Der Dialog startet immer mit dem Wert **1**, nicht mit dem aktuellen Projektwert (`initialValues` Archiv `{ archive_in: 1 }`, Close `{ close_in: 1, default_state: <erster cancelled-State des Projekts> }`). Beim Submit schickt der Auto-Close-Dialog `default_state` aus `initialValues` mit (react-hook-form übergibt alle `defaultValues`). Folge: **Ein zuvor gewählter „Auto-close status“ wird beim „Customize time range“ auf den ersten cancelled-State zurückgesetzt.** Für 1:1 dokumentieren; bei der Portierung als Bug beheben (nur `close_in` senden). `handleChange` im Dialog wird nicht abgewartet, der Dialog schließt sofort. Fehler beim Speichern zeigt die Seite als Toast „Error!“ / „Something went wrong. Please try again.“ (fester englischer Text, nicht i18n; `…/automations/page.tsx`).
  - Toggle-Logik: Einschalten nur, wenn der Wert genau `0` ist (`archive_in === 0` bzw. `close_in === 0`), sonst wird ausgeschaltet. Der Switch ist für Nicht-Admins `disabled`.
- **Backend-Modell:** `Project.archive_in`, `Project.close_in`: `IntegerField(default=0)`, Validatoren 0 bis 12. `Project.default_state`: FK `State` (`SET_NULL`) (R22). Public API dokumentiert beide Felder (D9).
- **Job:** Celery Beat `check-every-day-to-archive-and-close` täglich **01:00 UTC** → `archive_and_close_old_issues()` = `archive_old_issues()`, dann `close_old_issues()` (R21, R20).
- **Archiv-Kriterien** (`archive_old_issues`, R20): alle Projekte mit `archive_in > 0`. Je Projekt Issues aus `Issue.issue_objects` (ohne Triage-State-Gruppe, ohne bereits archivierte, ohne archivierte Projekte, ohne Drafts, R33) mit `archived_at IS NULL`, `updated_at <= now - archive_in*30 Tage`, State-Gruppe ∈ {completed, cancelled}. **Und** (kein Cycle **oder** Cycle-`end_date < now`). **Und** (kein Modul **oder** Modul-`target_date < now`). **Und** Intake-Status ∈ {1 accepted, -1 rejected, 2 duplicate} oder kein Intake-Eintrag. Pending (-2) und Snoozed (0) sind ausgeschlossen (R34). Setzt `archived_at = heute (Datum)`, `bulk_update` in Batches zu 100. Danach je Issue `issue_activity.delay(type="issue.activity.updated", requested_data={"archived_at": "<datum>", "automation": true}, actor_id=project.created_by_id, current_instance={"archived_at": null}, notification=True)`.
- **Activity-Text Archiv:** mit `automation: true` → Kommentar „Plane has archived the issue“, `new_value = "archive"`. Manuell → „Actor has archived the issue“, `new_value = "manual_archive"` (R25).
- **Close-Kriterien** (`close_old_issues`, R20): Projekte mit `close_in > 0`. Gleiche Filter, aber State-Gruppe ∈ {backlog, unstarted, started} und `updated_at <= now - close_in*30 Tage`. Ziel-State = `project.default_state`. Falls `null`: `State.objects.filter(group="cancelled").first()`. **Edge-Case/Bug:** Dieser Fallback filtert **nicht nach Projekt**, er kann also einen State eines fremden Projekts wählen. `track_closed_to` liest den State danach mit `project_id` und würfe `DoesNotExist` (R20, R25). Bei der Portierung **projektbezogen korrigieren** (erster cancelled-State des Projekts, analog UI). Activity: `requested_data={"closed_to": "<state_id>"}` → Feld `state`, Kommentar „Plane updated the state to “, `new_value = State-Name`, `new_identifier = State-ID` (R25).
- „Monat“ = 30 Tage. Referenz ist `updated_at`, nicht `completed_at` (R20).
- UI-Verweise „Set automation“ in Archiv-Leerzuständen (`project_views.empty_state.no_archived_issues.*`, `project_issues.empty_state.no_archived_issues.*`, `workspace_empty_state.archive_work_items.*`; `packages/i18n/src/locales/en/project.json`, `empty-state.json`).

#### Bezahl-Erweiterungen (öffentlich belegt)
- Laut Doku bleiben archivierte Items durchsuchbar. Items in **aktiven** Cycles oder Modulen werden nicht archiviert, auch wenn sie die Schwelle überschreiten (W22). Das entspricht der CE-Logik.
- Auto-Close-Zielstatus „such as Cancelled“ (W22). Das CE beschränkt die UI auf die Gruppe `cancelled` (R23).
- Unter Governance (Enterprise Grid) sind Projekt-Automationen für Projekt-Admins gesperrt (W22).
- Weitere EE-Felder oder -Optionen (Tage statt Monate, andere Zielgruppen) sind **nicht belegt**.

#### Plan-Tier
Free (in allen Plänen), CE vorhanden.

#### Konfidenz
Hoch (CE-Code).

---

### F26 – Auto-Reminders

- Icon im Propel-Paket: `AutoReminderOutline`/`AutoReminderFilled` (`actions/auto-reminder-outline.js`, R29; Verwendung im EE UNVERIFIZIERT, Kachel analog F25).
- Project Settings → Automations → Toggle **„Auto-reminders“** (`project_settings.automations.auto-remind.title`). Beschreibung „Plane will automatically send reminders via email and in-app notifications to keep your team on track with deadlines.“. Zeile „Send reminder before“ (`…duration`) mit Vorlauf, zum Beispiel 3 Tage vor Fälligkeit (R6, W22). Auswahlwerte UNVERIFIZIERT. Vorschlag in Anlehnung an F25: Select plus „Customize time range“.
- Nur Work Items **mit Due Date** und mindestens **einem Assignee oder Subscriber**. **Eine** Erinnerung je Fenster, keine tägliche Flut. Completed und Cancelled werden übersprungen. Kanäle In-App **und** E-Mail an Assignees und Subscriber (W22, W46).
- Changelog: v2.6.0 „auto reminders … configured through automations based on due date“ (W47). v3.0.0 „due date reminders“ als Enhancement (W19).
- **Plan:** Business (W22, W46). Im Repo ohne Plan-Angabe (keine Matrix-Zeile in R1, kein Eintrag in R2); die Tier-Zuordnung stützt sich nur auf W-Quellen. **CE:** fehlt (nur Texte, die CE-Seite rendert den Block nicht, R23).
- **Datenmodell (Vorschlag):** `Project.reminder_before_days` (int, 0 = aus) oder Automation-Setting-Tabelle. `WorkItemReminderLog { work_item_id, due_date, sent_at }` als Dedup („one reminder per window“). Bei Änderung des Due Date wird erneut gesendet (Annahme, UNVERIFIZIERT).
- **Konfidenz:** mittel.

---

### F27 – Auto-Schedule Cycles (Querverweis Cycle-Cluster)

- Texte vorhanden (`project_settings.cycles.auto_schedule.*`, R6): „Auto-schedule cycles“ / „Keep cycles moving without manual setup.“, Tooltip „Automatically create new cycles based on your chosen schedule.“. Formular: Cycle Title (Tooltip „The title will be appended with numbers for subsequent cycles. For eg: Design - 1/2/3“, Pflicht, ≤255), Cycle Duration (Wochen, 1 bis 30), Cooldown Period (Tage, ≥0), Cycle starts day (nicht in der Vergangenheit), Number of future cycles (1 bis 3), Auto-rollover work items („On the day a cycle completes, move all unfinished work items into the next cycle.“).
- Changelog „Introducing Milestones and Recurring cycles“ v1.16.0 (W49). Plan UNVERIFIZIERT (die Matrix nennt nur „Auto-transfer Cycle Work items“ ab Pro, R1).
- **CE:** fehlt. Vollständige Spezifikation gehört in das Cycle-Dokument. **Konfidenz:** mittel (Texte), niedrig (Plan).

---

### F28 – Auto-transfer Cycle Work items (Querverweis Cycle-Cluster; in der Verifikation ergänzt)

- **Quelle:** Matrix-Zeile „Auto-transfer Cycle Work items“ – „Transfer incomplete work items from a completed cycle to the next cycle or to the default project state.“; Pro, Business, Enterprise `true`, nicht „coming soon“ (R1, `plans.tsx` Z. 249–259). Gleichlautend Schwester-Dok. 20 PF-12.
- **Verhältnis zu F27:** Der Auto-Schedule-Schalter „Auto-rollover work items“ („On the day a cycle completes, move all unfinished work items into the next cycle.“, `project_settings.cycles.auto_schedule.form.auto_rollover.*`, R6) ist die einzige UI-Spur einer automatischen Übertragung. Ob die Matrix-Zeile genau diesen Schalter meint oder eine eigene Einstellung (Ziel „default project state“ ist im Auto-Rollover-Text nicht enthalten), ist UNVERIFIZIERT.
- **CE-Status:** teilweise. Der **manuelle** Transfer existiert: `POST /api/workspaces/<slug>/projects/<project_id>/cycles/<cycle_id>/transfer-issues/` (`TransferCycleIssueEndpoint`, `apps/api/plane/app/urls/cycle.py` Z. 72–74). Ein zeitgesteuerter automatischer Transfer fehlt.
- **Migrationshinweis:** Täglicher Scheduler-Job (wie F25) beim Abschluss eines Cycles; Ziel: nächster Cycle (laut Auto-Schedule) oder `Project.default_state`-Logik. Wiederverwendung der Transfer-Domänenlogik des CE-Endpunkts.
- **Konfidenz:** niedrig (nur Matrix-Text).

---

### F29 – Auto-assignment in Modules (Querverweis Modul-Cluster; in der Verifikation ergänzt)

- **Quelle:** Matrix-Zeile „Auto-assignment In Modules“ – „Choose assignment rules for work items in a module including Linear, Round Robin, or Capacity.“; Pro „Linear“, Business und Enterprise „Round-robin and Capacity“ (R1, `plans.tsx` Z. 308–317). Gleichlautend Schwester-Dok. 20 PF-19.
- **Funktion:** regelbasierte Zuweisung von Work Items innerhalb eines Moduls. Die Semantik von „Linear“, „Round-robin“ und „Capacity“ ist nirgends beschrieben (UNVERIFIZIERT). Keine i18n-Texte, keine Hooks im CE.
- **CE-Status:** fehlt.
- **Migrationshinweis:** Fachliche Klärung nötig (O22). Vorschlag: Regel je Modul `{ mode: linear|round_robin|capacity, member_ids[] }`, ausgeführt beim Hinzufügen eines Work Items zum Modul, über denselben Automation-Bot (F09) und dieselbe Activity-Protokollierung.
- **Konfidenz:** niedrig.

**Abgrenzung (nicht in P06 aufgenommen):** Matrix-Zeile „Scheduled Comms“ („Schedule reports, notifications, and messages to third-party tools.“, Business, R1 Z. 413–422) und „Zapier“ („Run if-then-else automations using Zapier.“, Pro, R1 Z. 991–1000) gehören zu den Clustern Benachrichtigungen bzw. Integrationen (Schwester-Dok. 20 PF-33; Dok. 28). GitHub/GitLab „Pull Request Automation“ (`integration.json` `github_integration.pull_request_automation*`, `gitlab_integration.pull_request_automation*`) gehört zum Integrations-Cluster (Dok. 28).

---

## 4. Offene Punkte / Unklarheiten

| # | Thema | Frage / Unklarheit | Vorschlag |
|---|---|---|---|
| O1 | Plan-Zuordnung | Repo-Matrix (R1/R2) und Doku 2026 (W1/W21) widersprechen sich (Automations Pro vs. Business; Approvals Business vs. Enterprise Grid; „Workflows + Approvals“ Business) | Wegen ADR-001 ohne Wirkung, nur dokumentarisch |
| O2 | Workflow-UI-Generation | Das CE enthält Texte zweier Generationen (R3 regelbasiert, R6 Multi-Workflow). Welche ist für ADR-005 die Referenz? | 2. Generation (aktueller Stand) mit Transition-Editor aus R3-Texten. Referenz-Screenshots einer aktuellen Commercial-Instanz nötig |
| O3 | Approval-Laufzeit | Kein öffentlicher Endpunkt für Approve/Reject. Pending-Position (im Approval-State oder davor), Verhalten bei einem Reject vor Erreichen von `required_approvals`, Benachrichtigung der Approver | Annahmen in F03. Entscheidung durch den Auftraggeber |
| O4 | Approvals Workspace/Projekt (F08) | Nur ein Matrix-Satz („coming soon“). Fachlicher Inhalt unbekannt | Rückfrage: weglassen, auf WIT-Workflow-Approvals reduzieren oder neu spezifizieren? |
| O5 | Decisions & Loops (F15) | Nicht öffentlich spezifiziert (coming soon). API-Graph vorhanden | Datenmodell als Graph. UI linear. Rückfrage, ob Verzweigungen/Schleifen gebaut werden sollen |
| O6 | Automation-Handler-Namen | Nur `record_created` (Trigger) sowie `add_comment`, `change_property`, `run_script` (Aktionen) belegt. Andere Trigger- und Aktions-Handler, Template-Variablen von „Add comment“, Operatorliste je Feld fehlen | Namen frei festlegen, an `snake_case`-Konvention orientieren (zum Beispiel `record_updated`, `state_changed`, `assignee_changed`, `comment_created`, `scheduled`, `send_webhook`) und in einer eigenen Konstantenliste dokumentieren |
| O7 | Automation-Status | Werte außer `draft` unbekannt | Vorschlag `draft`, `enabled`, `disabled` plus `is_enabled` |
| O8 | Workflow vs. Automation | Unterliegen Automation-Aktionen (State-Änderung) den Workflow-Regeln, oder darf der Automation Bot alles? | Rückfrage. Vorschlag: Bot unterliegt den Regeln, außer der Workflow erlaubt „All“ |
| O9 | Plane Runner ohne Node (ADR-002) | Sandbox für JS/TS in .NET (Jint vs. ClearScript V8). TypeScript-Transpilation ohne Node. Kompatibilität mit Original-Skripten (`Functions`, SDK) | Spike im Architektur-Dokument. Ggf. nur JavaScript (ES2020) in Phase 1 |
| O10 | Broker | RabbitMQ (Original) vs. reiner PostgreSQL-Outbox-Konsum (airgapped-freundlich, ADR-004) | Architektur-Entscheidung (ADR) nötig |
| O11 | Project-Template-PATCH | `template_data`: Merge oder Ersetzung widersprüchlich (W36) | Vollständige Ersetzung (einfacher, eindeutiger), Frontend sendet immer das ganze Objekt |
| O12 | Template-Schemata | `workflows`, `milestones`, `modules`, `recurring_work_items`, `automations`, `estimates`, `members` in `template_data` ohne Schema | Eigene, versionierte JSON-Schemata aus den Entitäten der neuen Plattform ableiten (`schema_version`-Feld) |
| O13 | Pre-defined Templates / Marketplace | Offline-Betrieb (ADR-004). Welche Templates mitliefern? Instanzweiter Marketplace gewünscht? | Rückfrage. Vorschlag: Seed-Katalog plus instanzweite Veröffentlichung |
| O14 | Recurring „quarterly“ | Changelog nennt quarterly, API nicht | UI-Option „Quarterly“ = `monthly` × 3. Prüfen gegen Referenz-Screenshot |
| O15 | Recurring Monatsende | Verhalten bei Start am 29./30./31. | Letzter Tag des Monats |
| O16 | Auto-Reminders | Auswahlwerte „Send reminder before“, Verhalten bei geändertem Due Date | Select mit Tagen (1, 2, 3, 5, 7) plus Custom. Annahme, gegen Screenshot prüfen |
| O17 | Governance-Irreversibilität (F07) | Fachliche Regel beibehalten, obwohl ADR-001 alle Features aktiviert? | Beibehalten (fachliche Semantik, ADR-003) |
| O18 | CE-Bug Auto-Close-Fallback | `State.objects.filter(group="cancelled").first()` ohne Projektfilter (R20) | Projektbezogen korrigieren und als bewusste Abweichung dokumentieren |
| O20 | Approval-Typ: State oder Transition (Verifikation) | W6/W9 (API-Zusammenfassung) legen `type` an den Chain-Eintrag (State), D1 an jede Transition und zeigt gemischte Typen aus einem Quell-State | `type` je Transition modellieren (Obermenge), `rejection_state_id` optional; gegen Volltext der API-v2-Referenz prüfen |
| O21 | Workflows-Tier Pro vs. Business (Verifikation) | Dok. 20 zitiert plane.so/pricing (WebSearch) „a single workflow per project“ für Pro; W1 und R2 sagen Business | Wegen ADR-001 ohne Wirkung; in der Feature-Liste Business mit Hinweis auf den Widerspruch |
| O22 | Auto-assignment in Modules (F29) | Semantik „Linear“, „Round-robin“, „Capacity“ unbekannt | Rückfrage an den Auftraggeber oder weglassen |
| O19 | Quellenzugriff | docs.plane.so, plane.so und developers.plane.so nur über Suchzusammenfassungen; GitHub-Repo `makeplane/developer-docs` (Master mit API v2) in dieser Session nicht freigegeben (Zugriff verweigert, nur `mlwr/plane` erlaubt) | Für die Implementierungsphase den Volltext der API-v2-Referenz offline bereitstellen (aktueller Clone von `makeplane/developer-docs`), um die als UNVERIFIZIERT markierten Feldlisten zu schließen |

---

## Anhang A – Vollständiges i18n-Inventar der Cluster-Texte (en)

Alle Schlüssel liegen in `packages/i18n/src/locales/en/`. Die Werte stehen in den Dateien. Bei der Portierung werden **alle** Locale-Verzeichnisse (`packages/i18n/src/locales/*/`) übernommen. Spalte 2 listet die Blätter des jeweiligen Pfads vollständig auf.

### A.1 `automation.json`
| Pfad | Blätter |
|---|---|
| `automations.settings` | `title`, `create_automation` |
| `automations.scope` | `label`, `run_on` |
| `automations.trigger` | `label`, `add_trigger`, `sidebar_header`, `input_label`, `input_placeholder`, `section_plane_events`, `section_time_based`, `fixed_schedule` |
| `automations.trigger.schedule` | `frequency`, `select_day`, `day_of_month`, `monthly_every`, `monthly_day_aria`, `time`, `hour`, `minute`, `hour_suffix`, `minute_suffix`, `am`, `pm`, `timezone`, `timezone_placeholder`, `frequency_daily`, `frequency_weekly`, `frequency_monthly`, `on`, `validation_weekly_day_required`, `validation_monthly_date_required`, `main_content_schedule_summary_daily`, `main_content_schedule_summary_weekly`, `main_content_schedule_summary_monthly`, `schedule_mode`, `schedule_mode_fixed`, `schedule_mode_cron`, `cron_expression_label`, `cron_expression_placeholder`, `cron_invalid`, `cron_preview`, `main_content_cron_summary` |
| `automations.trigger.button` | `previous`, `next` |
| `automations.trigger.warning` | `disabled_trigger_switching` |
| `automations.condition` | `label`, `add_condition`, `adding_condition` |
| `automations.action` | `label`, `add_action`, `sidebar_header`, `input_label`, `input_placeholder` |
| `automations.action.handler_name` | `add_comment`, `change_property`, `run_script` |
| `automations.action.configuration` | `label` |
| `automations.action.configuration.change_property.placeholders` | `property_name`, `change_type`, `property_value_select`, `property_value_select_date` |
| `automations.action.configuration.change_property.validation` | `property_name_required`, `change_type_required`, `property_value_required` |
| `automations.action.comment_block` | `title` |
| `automations.action.run_script_block` | `title` |
| `automations.action.change_property_block` | `title` |
| `automations.action.validation` | `delete_only_action` |
| `automations.conjunctions` | `and`, `or`, `if`, `then` |
| `automations.enable` | `alert` |
| `automations.enable.validation` | `required` |
| `automations.delete.validation` | `enabled` |
| `automations.table` | `title`, `scope`, `projects`, `last_run_on`, `created_on`, `last_updated_on`, `last_run_status`, `average_duration`, `owner`, `executions` |
| `automations.create_modal.heading` | `create`, `update` |
| `automations.create_modal.title` | `placeholder`, `required_error` |
| `automations.create_modal.description` | `placeholder` |
| `automations.create_modal.submit_button` | `create`, `update` |
| `automations.delete_modal` | `heading` |
| `automations.activity.filters` | `show_fails`, `all`, `only_activity`, `only_run_history` |
| `automations.activity.run_history` | `initiator` |
| `automations.toasts.{create,update,enable,disable,delete}.{success,error}` | je `title`, `message` |
| `automations.toasts.action.{create,update}.error` | je `title`, `message` |
| `automations.empty_state.no_automations` | `title`, `description` |
| `automations.empty_state.upgrade` | `title`, `description`, `sub_description` (entfällt, ADR-001) |
| `automations.global_automations.project_select` | `label` |
| `automations.global_automations.project_select.all_projects` | `label`, `description` |
| `automations.global_automations.project_select.select_projects` | `label`, `description`, `placeholder` |
| `automations.global_automations.settings` | `sidebar_label`, `title`, `description` |
| `automations.global_automations.table.scope` | `global` |
| `automations.global_automations.table.scope.project` | `label`, `multiple`, `all` |

### A.2 `workflow.json`
| Pfad | Blätter |
|---|---|
| `workflows.workflow_states` | `work_item_creation`, `work_item_creation_disable_tooltip`, `default_state`, `state_change_count`, `movers_count` |
| `workflows.workflow_states.state_changes.label` | `default`, `loading` |
| `workflows.workflow_states.state_changes` | `move_to` |
| `workflows.workflow_states.state_changes.movers` | `label`, `tooltip`, `add` |
| `workflows.workflow_disabled` | `title` |
| `workflows.workflow_enabled` | `label` |
| `workflows.workflow_tree` | `label`, `state_change_label` |
| `workflows.empty_state.upgrade` | `title`, `description` (entfällt, ADR-001) |
| `workflows.quick_actions` | `view_change_history`, `reset_workflow` |
| `workflows.confirmation_modals.reset_workflow` | `title`, `description` |
| `workflows.confirmation_modals.delete_state_change` | `title`, `description` |
| `workflows.toasts.enable_disable` | `loading` |
| `workflows.toasts.enable_disable.{success,error}` | je `title`, `message` |
| `workflows.toasts.reset.{success,error}` | je `title`, `message` |
| `workflows.toasts.{add_state_change_rule,modify_state_change_rule,remove_state_change_rule,modify_state_change_rule_movers}.error` | je `title`, `message` |

### A.3 `template.json`
| Pfad | Blätter |
|---|---|
| `templates.settings` | `title`, `description`, `new_project_template`, `new_work_item_template`, `new_page_template` |
| `templates.settings.options.{project,work_item,page}` | je `label` |
| `templates.settings.create_template` | `label` |
| `templates.settings.create_template.no_permission` | `project`, `workspace` |
| `templates.settings.use_template.button` | `default`, `loading` |
| `templates.settings.template_source.{workspace,project}` | je `info` |
| `templates.settings.form.project.template.name` | `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.project.template.description` | `placeholder` |
| `templates.settings.form.project.name` | `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.project.description` | `placeholder` |
| `templates.settings.form.project.button` | `create`, `update` |
| `templates.settings.form.work_item.template.name` | `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.work_item.template.description` | `placeholder` |
| `templates.settings.form.work_item.name` | `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.work_item.description` | `placeholder` |
| `templates.settings.form.work_item.button` | `create`, `update` |
| `templates.settings.form.page.template.name` | `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.page.template.description` | `placeholder` |
| `templates.settings.form.page.name` | `placeholder`; `.validation`: `maxLength` |
| `templates.settings.form.page.button` | `create`, `update` |
| `templates.settings.form.publish` | `action`, `unpublish_action`, `title` |
| `templates.settings.form.publish.name` | `label`, `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.publish.short_description` | `label`, `placeholder`; `.validation`: `required` |
| `templates.settings.form.publish.description` | `label`, `placeholder`; `.validation`: `required` |
| `templates.settings.form.publish.category` | `label`, `placeholder`; `.validation`: `required` |
| `templates.settings.form.publish.keywords` | `label`, `placeholder`, `helperText`; `.validation`: `required` |
| `templates.settings.form.publish.website` | `label`, `placeholder`; `.validation`: `invalid`, `maxLength` |
| `templates.settings.form.publish.company_name` | `label`, `placeholder`; `.validation`: `required`, `maxLength` |
| `templates.settings.form.publish.contact_email` | `label`, `placeholder`; `.validation`: `invalid`, `maxLength` |
| `templates.settings.form.publish.privacy_policy_url` | `label`, `placeholder`; `.validation`: `invalid`, `maxLength` |
| `templates.settings.form.publish.terms_of_service_url` | `label`, `placeholder`; `.validation`: `invalid`, `maxLength` |
| `templates.settings.form.publish.cover_image` | `label`, `upload_title`, `upload_placeholder`, `drop_here`, `click_to_upload`, `invalid_file_or_exceeds_size_limit`, `upload_and_save`, `uploading`, `remove`, `removing`; `.validation`: `required` |
| `templates.settings.form.publish.attach_screenshots` | `label`; `.validation`: `required` |
| `templates.empty_state.upgrade` | `title`, `description`, `sub_description` (entfällt, ADR-001) |
| `templates.empty_state.no_templates` | `button` |
| `templates.empty_state.{no_labels,no_modules,no_work_items,no_sub_work_items}` | je `description` |
| `templates.empty_state.page.{no_templates,no_results}` | je `title`, `description` |
| `templates.toasts.{create,update,delete,unpublish}.{success,error}` | je `title`, `message` |
| `templates.delete_confirmation` | `title`; `.description`: `prefix`, `suffix` |
| `templates.unpublish_confirmation` | `title`; `.description`: `prefix`, `suffix` |
| `templates.dropdown.add` | `work_item`, `project` |
| `templates.dropdown.label` | `project`, `page` |
| `templates.dropdown.tooltip` | `work_item` |
| `templates.dropdown.no_results` | `work_item`, `project` |

### A.4 `project-settings.json` (Cluster-Ausschnitte)
| Pfad | Blätter |
|---|---|
| `project_settings.automations` | `label`, `heading`, `description` |
| `project_settings.automations.auto-archive` | `title`, `description`, `duration` |
| `project_settings.automations.auto-close` | `title`, `description`, `duration`, `auto_close_status` |
| `project_settings.automations.auto-remind` | `title`, `description`, `duration` |
| `project_settings.workflows.toggle` | `title`, `description`, `no_states_tooltip`, `no_work_item_types_tooltip`, `no_states_or_work_item_types_tooltip` |
| `project_settings.workflows.toggle.toast.loading` | `enabling`, `disabling` |
| `project_settings.workflows.toggle.toast.{success,error}` | je `title`, `message` |
| `project_settings.workflows` | `heading`, `description`, `add_button`, `search` |
| `project_settings.workflows.detail` | `define`, `add_states` |
| `project_settings.workflows.detail.unmapped_states` | `title`, `description`, `note`, `label`, `tooltip` |
| `project_settings.workflows.select_states.empty_state` | `title`, `description` |
| `project_settings.workflows.default_footer` | `fallback_message` |
| `project_settings.workflows.create` | `heading` |
| `project_settings.workflows.create.name` | `placeholder`; `.validation`: `max_length`, `required`, `invalid` |
| `project_settings.workflows.create.description` | `placeholder`; `.validation`: `invalid` |
| `project_settings.workflows.create.work_item_type` | `label` |
| `project_settings.workflows.{create,update}.{success,error}` | je `title`, `message` |
| `project_settings.workflows.delete` | `loading`; `.{success,error}`: je `title`, `message` |
| `project_settings.workflows.add_states.{success,error}` | je `title`, `message` |
| `project_settings.templates` | `heading`, `description` |
| `project_settings.cycles.auto_schedule` | `heading`, `description`, `tooltip`, `edit_button` |
| `project_settings.cycles.auto_schedule.form.cycle_title` | `label`, `placeholder`, `tooltip`; `.validation`: `required`, `max_length` |
| `project_settings.cycles.auto_schedule.form.cycle_duration` | `label`, `unit`; `.validation`: `required`, `min`, `max`, `positive` |
| `project_settings.cycles.auto_schedule.form.cooldown_period` | `label`, `unit`, `tooltip`; `.validation`: `required`, `negative` |
| `project_settings.cycles.auto_schedule.form.start_date` | `label`; `.validation`: `required`, `past` |
| `project_settings.cycles.auto_schedule.form.number_of_cycles` | `label`; `.validation`: `required`, `min`, `max` |
| `project_settings.cycles.auto_schedule.form.auto_rollover` | `label`, `tooltip` |
| `project_settings.cycles.auto_schedule.toast.toggle` | `loading_enable`, `loading_disable`; `.{success,error}`: je `title`, `message` |
| `project_settings.cycles.auto_schedule.toast.save` | `loading`; `.success`: `title`, `message_create`, `message_update`; `.error`: `title`, `message_create`, `message_update` |

### A.5 `work-item.json` (Cluster-Ausschnitte)
| Pfad | Blätter |
|---|---|
| `recurring_work_items.settings` | `heading`, `description`, `new_recurring_work_item`, `update_recurring_work_item` |
| `recurring_work_items.settings.form.interval` | `title` |
| `recurring_work_items.settings.form.interval.start_date.validation` | `required` |
| `recurring_work_items.settings.form.interval.interval_type.validation` | `required` |
| `recurring_work_items.settings.form.button` | `create`, `update` |
| `recurring_work_items.settings.create_button` | `label`, `no_permission` |
| `recurring_work_items.empty_state.upgrade` | `title`, `description` (entfällt, ADR-001) |
| `recurring_work_items.empty_state.no_templates` | `button` |
| `recurring_work_items.toasts.{create,update,delete}.{success,error}` | je `title`, `message` |
| `recurring_work_items.delete_confirmation` | `title`; `.description`: `prefix`, `suffix` |
| `bulk_operations.error_details.invalid_state_transition` | `title`, `message` |

### A.6 Weitere Dateien
| Datei | Schlüssel |
|---|---|
| `empty-state.json` | `settings_empty_state.templates.{title,description,cta_primary}`, `settings_empty_state.template_setting.{title,description,cta_primary}`, `settings_empty_state.recurring_work_items.{title,description,cta_primary}`, `settings_empty_state.workflows.{title,description,cta_primary}`, `settings_empty_state.workflows.states.{title,description}`, `settings_empty_state.work_item_types.{title,description,cta_primary}` (WIT-Cluster), `workspace_empty_state.archive_work_items.{description,cta_primary}` |
| `workspace-settings.json` | `workspace_settings.settings.templates.{title,heading,description}`, `workspace_settings.settings.runners.{title,heading,new_script,description}` |
| `common.json` | `common.automation`, `common.workflows`, `common.templates`, `common.recurring_work_items`, `transition`, `activity_empty_state.no_transitions` |
| `power-k.json` | `power_k.creation_actions.create_project_automation` |
| `project.json` | `project_views.empty_state.no_archived_issues.{description,primary_button.text}`, `project_issues.empty_state.no_archived_issues.{description,primary_button.text}` |
| `tour.json` | Erwähnung „approvals“ im Inbox-Tourtext (siehe F03) |

---

## Anhang B – CE-Erweiterungspunkte (vollständige Liste, Repo-geprüft)

| Datei | Erweiterungspunkt | CE-Verhalten | Ziel in der neuen Plattform |
|---|---|---|---|
| `apps/web/components/workflow/use-workflow-drag-n-drop.ts` | `useWorkFlowFDragNDrop(groupBy, subGroupBy)` → `{ workflowDisabledSource, isWorkflowDropDisabled, getIsWorkflowWorkItemCreationDisabled, handleWorkFlowState }` | `undefined` / `false` / `() => false` / No-op | Echte Workflow-Prüfung (F01) |
| `apps/web/components/issues/issue-layouts/kanban/kanban-group.tsx` | `handleWorkFlowState` in `onDragEnter`/`onDragStart`; Drop-Sperre mit Warn-Toast **nur bei gesetztem `dropErrorMessage`** [Verifikation]; Quick-Add ausgeblendet bei `getIsWorkflowWorkItemCreationDisabled(groupId, sub_group_id)` | inaktiv | F01 |
| `apps/web/components/issues/issue-layouts/list/list-group.tsx` | `handleWorkFlowState(sourceGroupId, currentGroupId)` in `onDrag` (nicht `onDragEnter`/`onDragStart`, ohne Sub-Gruppen) [Verifikation: korrigiert]; Drop-Sperre immer, Warn-Toast nur bei `group.dropErrorMessage`; `isWorkflowIssueCreationDisabled` → `disableIssueCreation` (Quick-Add aus) | inaktiv | F01 |
| `apps/web/components/issues/issue-layouts/kanban/default.tsx`, `.../kanban/swimlanes.tsx` | `getIsWorkflowWorkItemCreationDisabled` → `disableIssueCreation` | inaktiv | F01 |
| `apps/web/components/issues/issue-layouts/group-drag-overlay.tsx` | Prop `workflowDisabledSource` → `bg-danger-subtle`, keine Nachricht | nie gesetzt | F01 |
| `apps/web/components/dropdowns/state/state-select.tsx` | Kommentar zum EE-„State-lite“-Gating | ganze Liste, `allowedStateIds` ungesetzt | F01/F02 |
| `packages/blocks/src/property-select/state-select.tsx` | Prop `allowedStateIds?: Set<string> \| null` | `null` = alle | F01/F02 |
| `apps/web/components/issues/issue-modal/context/issue-modal-context.tsx` | `workItemTemplateId`, `setWorkItemTemplateId`, `isApplyingTemplate`, `setIsApplyingTemplate`, `handleTemplateChange`, `THandleTemplateChangeProps` | Typen | F21 |
| `apps/web/components/issues/issue-modal/provider.tsx` | Prop `templateId`; Context-Werte | `null` / No-op | F21 |
| `apps/web/components/issues/issue-modal/form.tsx` | Anwenden, Zurücksetzen, Wiederanwenden des Templates | implementiert, wirkt durch No-op-Provider nicht | F21 |
| `apps/web/components/issues/issue-modal/modal.tsx` | Prop `templateId` → Provider | durchgereicht | F21 |
| `apps/web/components/project/create-project-modal.tsx` | Prop `templateId` → `CreateProjectForm` | durchgereicht | F20 |
| `apps/web/components/projects/create/root.tsx` | `TCreateProjectFormProps.templateId` | nicht ausgewertet | F20 |
| `apps/web/components/project/create/header.tsx` | Prop `handleTemplateSelect` | nicht ausgewertet | F20 (Template-Picker oben links) |
| `apps/web/components/common/activity/helper.tsx` | `is_workflow_enabled` (Icon `GitBranchOutline`, Text „custom workflow“) | Feld im CE nicht vorhanden | F01 |
| `packages/constants/src/fetch-keys.ts` | `WORKSPACE_WORKFLOW_STATES`, `PROJECT_WORKFLOWS` | ungenutzt | F01/F07 |
| `packages/constants/src/state.ts` | `DISPLAY_WORKFLOW_PRO_CTA = false` | Upsell aus | entfällt (ADR-001) |
| `packages/constants/src/subscription.ts` | Plan-Feature-Listen | Upsell | entfällt (ADR-001) |
| `apps/web/components/workspace/billing/comparison/plans.tsx` | Plan-Matrix | Billing-Seite | entfällt (ADR-001) |
| `apps/web/components/license/modal/upgrade-modal.tsx` | Upsell-Text | Upsell | entfällt (ADR-001) |
| `packages/i18n/src/constants/namespaces.ts` | Namespaces `automation`, `template`, `workflow` | geladen | übernehmen |
| `packages/blocks/src/empty-state/assets/asset-registry.tsx` | Illustrationen `template`, `workflow` | vorhanden | übernehmen (UI 1:1) |
| `apps/web/components/settings/project/sidebar/item-icon.tsx` | `automations: TriggerOutline` | vorhanden | erweitern (workflows, templates, recurring) |
| `packages/types/src/settings.ts`, `packages/constants/src/settings/project.ts` | `TProjectSettingsTabs`, `TWorkspaceSettingsTabs`, `GROUPED_PROJECT_SETTINGS` | ohne EE-Tabs | um `workflows`, `templates`, `recurring_work_items` (Projekt) sowie `templates`, `automations`, `runners` (Workspace) erweitern |
| `apps/web/app/routes/core.ts` | Settings-Routen | nur CE-Routen | EE-Routen ergänzen (Pfadnamen UNVERIFIZIERT, Vorschlag `/settings/projects/:projectId/workflows`, `/templates`, `/recurring-work-items`; `/settings/templates`, `/settings/automations`, `/settings/runners`) |
| `apps/api/plane/db/models/user.py` | `is_bot`, `bot_type`, `BotTypeEnum` (`WORKSPACE_SEED`) | vorhanden | Bot-Typ für „Automation Bot“ ergänzen |
| `apps/api/plane/bgtasks/issue_automation_task.py`, `apps/api/plane/celery.py` | Auto-Archive/-Close-Job | vorhanden | portieren (F25), Bug O18 beheben |
| `packages/types/src/rich-filters/adapter.ts` | Typ-Parameter `E` „External filter format type (e.g., work item filters, automation filters)“ [Verifikation ergänzt] | generisch | Automation-Bedingungen (F11) als Rich-Filter-Adapter |
| `apps/web/components/settings/workspace/sidebar/item-icon.tsx` | Icon-Map Workspace-Settings (`general`, `members`, `export`, `billing-and-plans`, `webhooks`) [Verifikation ergänzt] | ohne EE-Einträge | um `templates`, `automations`, `runners` erweitern (Reihenfolge laut D11) |

---

## Verifikations-Protokoll

**Prüfer:** Skeptiker/Verifizierer P06, Lauf vom 2026-10-21. **Prüfgegenstand:** dieses Dokument in der Fassung des Autors (1186 Zeilen) plus Autor-Feature-Liste (26 Einträge).

### V.1 Methode und Grenzen

| Prüfschritt | Umfang | Ergebnis |
|---|---|---|
| Plan-Matrix und Plan-Listen | `apps/web/components/workspace/billing/comparison/plans.tsx` (alle Zeilen mit workflow/approval/automat/trigger/template/recurring/loop/schedule/auto-), `packages/constants/src/subscription.ts` vollständig | Alle Repo-Tier-Zitate des Autors stimmen wörtlich (Zeilen 249, 308, 368, 392, 414, 717, 769, 780, 792, 887, 993, 1306–1307; `subscription.ts` Z. 12, 17–19, 29). Keine Matrix-Zeile „Workflows“ (nur „Approvals“ und die Erwähnung in „Project Templates“) |
| i18n-Inventar (Anhang A) | Alle Blätter von `automation.json` (141), `workflow.json` (40), `template.json` (137) maschinell flachgelegt und gegen A.1–A.3 abgeglichen; Cluster-Schlüssel in `project-settings.json`, `work-item.json`, `empty-state.json`, `workspace-settings.json`, `common.json`, `power-k.json`, `project.json`, `tour.json` | A.1–A.6 vollständig und korrekt; alle wörtlich zitierten UI-Texte stimmen, auch die Original-Tippfehler („in you project“, „so its clear“, „that template this.“) |
| CE-Stubs (Anhang B) | Jede Datei gelesen | Alle Erweiterungspunkte existieren wie beschrieben; zwei Präzisierungen (List-`onDrag`, Kanban-`dropErrorMessage`-Bedingung), zwei Ergänzungen (Rich-Filter-Adapter, Workspace-Sidebar-Icons) |
| CE-Auto-Archive/-Close (F25) | `issue_automation_task.py`, `issue_activities_task.py` (`track_archive_at`, `track_closed_to`), `celery.py`, `project.py`, `state.py`, drei Automation-Komponenten, `select-month-modal.tsx`, Seite `…/automations/page.tsx` | Beschreibung korrekt; **Bug O18 bestätigt** (`State.objects.filter(group="cancelled").first()` ohne Projektfilter; `track_closed_to` liest mit `project_id` → `State.DoesNotExist` bei fremdem State). Neu gefunden: Reset von `default_state` durch den „Customize time range“-Dialog |
| Offline-Doku/Helm | `plane-compose.md` (workflows/states/features/types), `create-project-with-template.md`, `project/overview.md`, `health-checks.md`, `environment-variables.md`, `high-availability.md`, `airgapped-edition.md`; Helm `automations-consumer.yaml`, `outbox-poller.yaml`, `runner-env.yaml`, `webhook-consumer.yaml`, `values.yaml`, `Chart.yaml` | Alle Env-Keys, Defaults und Dienstnamen stimmen. D1 widerspricht dem Approval-Datenmodell (O20). D10 (`template_id`) war nicht erfasst |
| Screenshots | `docs/public/images/webhooks/create-webhook.webp`, `docs/public/images/projects/project-automations.png` | Neue UI-Belege für Sidebar-Reihenfolge; Gegenindiz zur Tier-Angabe von F13/F19 |
| Propel-Icons | `dist/icons/index.js` und Unterordner | Alle genannten Icons vorhanden; Pfad von `WorkflowsOutline` korrigiert; vier relevante Icons ergänzt |
| Web-Quellen W1–W52 | — | **Nicht erneut prüfbar.** Das WebSearch-Kontingent dieses Laufs (200 Suchen, von allen Agenten geteilt) war bei Prüfbeginn erschöpft; es wurde keine einzige Suche ausgeführt. `WebFetch https://github.com/makeplane/docs` → 404. Alle Aussagen, die nur auf W-Quellen beruhen, haben deshalb weiter nur den Belegstand der Autor-Recherche (Suchzusammenfassungen) und sind in der Feature-Liste mit höchstens Konfidenz „mittel“ geführt |

### V.2 (a) Tier-Zuordnungen

| ID | Tier (Autor) | Repo-Beleg | Nur Web-Beleg | Urteil |
|---|---|---|---|---|
| F01 | Business | `subscription.ts` „Workflows + Approvals“ (Business) | W1, W18, W45 | Belegt. Widerspruch zu Dok. 20 („single workflow per project“ in Pro) dokumentiert (O21) |
| F02 | Enterprise Grid | — | W1, W2, W19, W45 | Nur Web; nicht gegengeprüft |
| F03 | Enterprise Grid | Repo sagt Business (`subscription.ts`, Matrix „Approvals“ coming soon) | W1, W2, W10, W27 | Aktuellere Quelle (Doku 2026) gewinnt; Widerspruch korrekt dokumentiert |
| F04 | Enterprise Grid | — | W2, W12 | Nur Web |
| F05 | Business | — | — | Abgeleitet aus F01 (kein eigener Beleg); korrekt so gekennzeichnet |
| F06 | Business | — | W20 | Nur Web |
| F07 | Enterprise Grid | — | W3, W4, W15 | Nur Web |
| F08 | Business | Matrix Z. 717 (Business, coming soon) | — | Belegt |
| F09 | Business | Matrix/`PRO_PLAN_FEATURES`: **Pro** | W21, W22 | Aktuellere Quelle (Doku 2026) gewinnt; Widerspruch dokumentiert. Wäre die Doku-Zusammenfassung falsch, gälte Pro |
| F10–F12 | Business / Enterprise Grid | — | W21, W23, W24, W30, W31 | Nur Web |
| F13 | Enterprise Grid | — | W21, W22 | Gegenindiz D11 (Sidebar-Eintrag im Business-Workspace) ergänzt |
| F14 | Enterprise Grid | — | W24, W27 | Nur Web |
| F15 | Business | Matrix Z. 780 (Business, coming soon), `BUSINESS_PLAN_FEATURES` | — | Belegt |
| F16 | Pro | Matrix Z. 792 | — | Belegt. Hinweis: Wenn Automationen laut Doku 2026 erst ab Business existieren, ist das Pro-Limit veraltet |
| F17 | Business | — | W21 | Abgeleitet aus F09 |
| F18 | unklar | Helm (Dienste optional, `enabled: false`) | W32 | Korrekt „kein Plan-Feature“ |
| F19 | Enterprise Grid | — | W24, W25 | Gegenindiz D11 ergänzt |
| F20 | Business | Matrix Z. 392, `planHighlights.business`, `BUSINESS_PLAN_FEATURES` | W18, W45 | Belegt |
| F21 | Pro | `planHighlights.pro` „Work item templates“ | W18, W34 | Belegt |
| F22 | Pro | Matrix Z. 887 („Templates“, Knowledge management) | W45 | Belegt |
| F23 | Pro | Matrix Z. 368 (coming soon) | — | Belegt (nur für Pre-defined WI-Templates; Marketplace ohne Tier) |
| F24 | Business | `recurring_work_items.empty_state.upgrade.description` „Upgrade to Business …“ | W42, W45 | Belegt |
| F25 | Free | CE-Code | — | Belegt |
| F26 | Business | **kein** Repo-Beleg | W22, W46 | Nur Web; im Dokument präzisiert |
| F27 | unklar | — | W49 | Korrekt als UNVERIFIZIERT geführt |
| F28 (neu) | Pro | Matrix Z. 249 | — | Belegt |
| F29 (neu) | Pro | Matrix Z. 308 | — | Belegt |

### V.3 (b) CE-Status

Per grep geprüft (`apps/`, `packages/`, ohne `node_modules` und Locales): Es gibt im CE keine Modelle, Views, URLs, Stores oder Komponenten für Workflows, Approvals, Custom Automations, Templates, Recurring Work Items, Auto-Reminders, Runner oder Outbox. Treffer nur in den in Anhang B genannten Stub-Dateien. Alle CE-Status-Angaben des Autors bestätigt. Präzisiert: F28 „teilweise“ (manueller Cycle-Transfer vorhanden).

### V.4 (c) Fehlende Features

- **Ergänzt:** F28 Auto-transfer Cycle Work items, F29 Auto-assignment in Modules (beide Automations-Regeln mit Matrix-Beleg, im Dokument bisher nur am Rand bzw. gar nicht erwähnt).
- **Ergänzt als Teilaspekt:** Runner-„Functions“ (F19), Projekt-Feld `template_id` (F20), Projekt-Leerzustand der Templates (F21), Activity-Tab-Leerzustände (F06), Workspace-Settings-Sidebar-Reihenfolge (F13, F19, F20).
- **Bewusst nicht aufgenommen (Abgrenzung):** „Scheduled Comms“, „Zapier“, „Pull Request Automation“ (GitHub/GitLab), „Intake Assignees“, „Custom SLAs“ – andere Cluster.

### V.5 (d) Korrekturen an Aussagen

1. R29: `WorkflowsOutline` liegt in `project-features/workflows-outline.js`, nicht in `properties/` (dort `WorkflowsPropertyOutline`).
2. F01/F03: D1 (Plane Compose) ist keine „zweite Bestätigung“ des State-Typs `approval`; D1 führt `type` je Transition und zeigt gemischte Typen aus einem Quell-State, ohne Rejection-State (O20).
3. F01 Enforcement Kanban/List: Event (`onDrag` in List), Kanban-Sperre nur mit `dropErrorMessage`, Zuordnung des Texts `workflows.workflow_disabled.title` als UNVERIFIZIERT markiert.
4. F01 State-Dropdown: „ausgeblendet statt ausgegraut“ ist durch `filterOption` im Repo belegt (vorher nur über unsicheren Changelog).
5. F01 Fetch-Keys: Rollenabhängigkeit als Schluss (UNVERIFIZIERT) gekennzeichnet.
6. F14: Die Aussage „Changelog März 2026: Bugfixes … (W23-Kontext)“ hatte keine passende Quelle (W23 = 09/2025) und wurde gestrichen.
7. F19: Anzahl eingebauter Functions ergänzt (`getChildren`).
8. F21: Template-Reset beim Projektwechsel nur bei `isDirty`.
9. F25: Edge-Case „Customize time range setzt Auto-close status zurück“ und Startwert 1 ergänzt.
10. F12: CE-Retry-Verhalten präzisiert (nur Netzwerkfehler, kein Retry auf HTTP-Status).
11. F04: Hinweis auf CE-SSRF-Schutz (`pinned_fetch`) und Raw-Body-Signatur ergänzt.
12. Keine Beschreibung wurde als erfunden erkannt. Alle wörtlichen UI-Texte stimmen mit den i18n-Dateien überein. Übertreibung: keine gefunden; die Formulierung „Erzwingung in allen UIs und APIs“ (Tabelle 2, F01) ist durch die Intake-Ausnahme (W51) eingeschränkt und dort bereits vermerkt.

### V.6 Verbleibende UNVERIFIZIERT-Punkte (Auswahl der tragenden)

Alle Aussagen aus W1–W52 (siehe V.1); Approval-Laufzeit und Entscheidungs-Endpunkt (O3); Handler-Namen außer `record_created`, `add_comment`, `change_property`, `run_script` (O6); Automation-`status`-Werte (O7); Workflow-Ebene des Approval-Typs (O20); Workflows-Tier Pro vs. Business (O21); Semantik von F28/F29 (O22); Settings-Routenpfade der EE-Seiten (Anhang B).
