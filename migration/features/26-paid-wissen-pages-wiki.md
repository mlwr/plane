# 26 – Bezahl-Features Cluster „Wissensmanagement“ (Pages / Wiki) – IST-Analyse (Cluster P07)

> Phase: reine IST-Analyse. Ziel: Implementierungs-Agenten sollen jedes Bezahl-Feature des Wissensmanagements (Wiki, Collections, Nested Pages, Versionen, Realtime, Publish, Exports, Templates, Embeds, Kommentare, Sharing, Analytics, AI im Editor, erweiterte Editor-Blöcke) **clean-room** nachbauen können.
> Bindend: `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Insbesondere **ADR-001** (alle Features immer aktiv, keine Plan-Limits), **ADR-002** (Realtime in .NET/YDotNet), **ADR-003** (Greenfield, API-Verträge fachlich am Original), **ADR-004** (Self-hosted/Airgapped, keine Pflicht-Abhängigkeit zu externen Diensten), **ADR-005** (UI 1:1).
> Querverweise: `migration/features/21-paid-api-referenz-developer-docs.md` (§2.14 Pages-/Work-Item-Pages-API, §4.4 Teamspaces, §4.9 Work-Item↔Page-Links, §4.10 Pages-Public-API/Wiki, §4.11 Feature-Toggles).

---

## 1. Überblick & Quellenlage

### 1.1 Editionen und Plan-Namen

| Begriff | Bedeutung | Quelle |
|---|---|---|
| Community Edition (CE) | AGPL-3.0, dieses Repo (v1.4.2). „The Community Edition is at par with the Free tier of the Cloud edition in its feature availability.“ | `/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` |
| Commercial Edition / Airgapped Edition | closed-source, „Full feature parity with our Cloud“; Upgrade auf Pro/Business/Enterprise | ebd. |
| Plan-IDs im Repo | `free`, `one`, `pro`, `business`, `enterprise` (`TPlanePlans`) | `apps/web/components/workspace/billing/comparison/plans.tsx` (Typ `TPlanePlans`, `PLANS_LIST`) |
| „One“ | historischer Self-hosted-Plan (Highlights „Upto 50 users“, „OIDC and SAML“, „Active cycles“, „Limited time tracking“); **nicht mehr erhältlich**: `planDetails.one.isActive: false`, Kommentar „Plane one plan is not longer available“ in `shouldRenderPlanDetail` (Spalte wird in der Vergleichsansicht nicht gerendert); das Upgrade-Modal zeigt nur Pro/Business/Enterprise | `plans.tsx` (`planHighlights.one`, `planDetails.one`), `apps/web/components/workspace/billing/comparison/base.tsx` (`shouldRenderPlanDetail`), `apps/web/components/license/modal/upgrade-modal.tsx` |
| Aktuelle Cloud-Pläne | Free, Pro ($6/Seat/Monat jährlich), Business ($13), **Enterprise Grid** (Top-Lizenz, Preis auf Anfrage) | https://plane.so/pricing, https://plane.so/enterprise-grid (via WebSearch) |

**Top-Lizenz** im Sinne des Auftrags = „Enterprise“ (Repo-Matrix) bzw. „Enterprise Grid“ (aktuelle Preisseite). Im Cluster Wissensmanagement sind die **nur in der Top-Lizenz** enthaltenen Merkmale: unbegrenzte Page-Versionen (P07-05; Matrix „Unlimited“ nur Enterprise) und der Editor-Block „Link dashboard widgets“ (P07-42; nur Doku-Label aus Such-Zusammenfassung, UNVERIFIZIERT). **Strittig**: „Databases + Formulas“ (P07-20) – Upgrade-Modal (`ENTERPRISE_PLAN_FEATURES`) und `planHighlights.enterprise` nennen es als Enterprise-Merkmal, die feature-spezifische Matrix-Zeile markiert dagegen Business ✓ und Enterprise ✓ (`comingSoon: true`); nach der Regel „spezifischere Quelle gewinnt“ gilt Business+, der Widerspruch ist in OP-03 dokumentiert; das Feature ist ohnehin nicht ausgeliefert.

**Tier-Regel „One“**: Für Merkmale, die die Matrix ab „One“ führt (Real-time Collab, Work item Embeds, Link-to-work items, Publish, Wiki), ist der niedrigste **heute erhältliche** Plan **Pro**, da „One“ nicht mehr angeboten wird (`base.tsx`, s. o.). Das CE-Upsell-Modal (v1.4.2) bestätigt Pro: „Unlock public pages, version history, shared pages, real-time collaboration, and workspace pages … with Plane Pro.“ (`packages/i18n/src/locales/en/wiki.json` `wiki.upgrade_flow.description`).

### 1.2 Quellen-Inventar (alle in diesem Dokument verwendeten Quellen)

Repo-Quellen (relativ zu `/home/user/plane`):

| ID | Pfad | Inhalt / Relevanz |
|---|---|---|
| R1 | `apps/web/components/workspace/billing/comparison/plans.tsx` | Offizielle Feature×Plan-Matrix; Sektion `knowledge-management` (Pages, Real-time Collab, Work item Embeds, Link-to-work items, Publish, Wiki, Exports, Templates, Versions, Databases + Formulas, Nested Pages) und Sektion `analytics-reports` („Advanced Pages Analytics“); `planHighlights` |
| R2 | `packages/constants/src/subscription.ts` | `ENTERPRISE_PLAN_FEATURES` („Databases + Formulas“), `BUSINESS_PLAN_FEATURES` („Nested Pages“), `PRO_PLAN_FEATURES` („Teamspaces“, „Wikis“), `ONE_PLAN_FEATURES` („Real-time collab + public views and page“, „Link pages in issues and vice-versa“), `FREE_PLAN_UPGRADE_FEATURES` („Public Views and Pages“) |
| R3 | `packages/i18n/src/locales/en/wiki.json` | EE-Texte `wiki_collections.*` (Collections-UI vollständig), `wiki.upgrade_flow.*`, `wiki.nested_pages_download_banner.title` |
| R4 | `packages/i18n/src/locales/en/page.json` | `page_navigation_pane.tabs.comments.*`, `page_navigation_pane.tabs.info.version_history.highlight_changes`, `page_actions.move_page.*`, `page_actions.remove_from_collection.*`, `page_content_limit_banner.message` |
| R5 | `packages/i18n/src/locales/en/editor.json` | EE-Editor-Texte `attachmentComponent.*`, `externalEmbedComponent.*`, `ai_block.*` |
| R6 | `packages/i18n/src/locales/en/template.json` | `templates.settings.*` inkl. `new_page_template`, `form.page.*`, `empty_state.page.*`, `dropdown.label.page` („Choose from template“) |
| R7 | `packages/i18n/src/locales/en/work-item.json` | `issue.pages.*` („Link pages“, „Show Wiki pages“, „Link pages to“, „Linked pages“, Toasts) |
| R8 | `packages/i18n/src/locales/en/workspace.json` | `workspace_pages.empty_state.*` inkl. `shared` |
| R9 | `packages/i18n/src/locales/en/common.json` | `common.members_and_teamspaces` („Members & Teamspaces“), `powered_by_plane_pages` („Powered by Plane Pages“) |
| R10 | `apps/web/hooks/use-editor-flagging.ts` | CE deaktiviert `"ai"` und `"collaboration-cursor"` in allen Editoren |
| R11 | `apps/web/hooks/use-page-flag.ts` | CE: `isMovePageEnabled: false`, `isPageSharingEnabled: false` |
| R12 | `apps/api/plane/db/models/page.py` | `Page` (Felder vollständig in 3.0), `PageLog`, `PageLabel`, `ProjectPage`, `PageVersion` (inkl. `sub_pages_data`) |
| R13 | `apps/api/plane/bgtasks/page_version_task.py`, `apps/api/plane/bgtasks/cleanup_task.py` | Versionierung (10-min-Zusammenfassung, max. 20 Versionen) |
| R14 | `apps/live/src/types/index.ts`, `apps/live/src/services/page/handler.ts`, `apps/live/src/services/page/extended.service.ts`, `apps/live/src/services/page/core.service.ts` | CE-Realtime nur `TDocumentTypes = "project_page"`; Hinweis „Implementation for this is found in the enterprise repository.“ |
| R15 | `packages/types/src/page/core.ts` | `TWebhookConnectionQueryParams.documentType: "project_page" \| "team_page" \| "workspace_page"`, `teamId` |
| R16 | `packages/editor/src/types/editor.ts` | `TEditorCommands` enthält `"attachment"`, `"external-embed"`, `"issue-embed"` |
| R17 | `packages/editor/src/plugins/drag-handle.ts` | Drag-Selektoren `.editor-embed-component`, `.editor-drawio-component`, `.issue-embed` |
| R18 | `packages/editor/src/plugins/drop.ts`, `packages/editor/src/constants/config.ts` | Datei-Drop: Zweig `fileType === "attachment"` leer; `ACCEPTED_ATTACHMENT_MIME_TYPES` |
| R19 | `packages/editor/src/extensions/work-item-embed/*`, `packages/editor/src/extensions/core-without-props.ts` | Node `issue-embed-component` (Schema + NodeView), nicht registriert |
| R20 | `apps/web/hooks/pages/use-extended-editor-extensions.ts`, `apps/web/hooks/pages/use-pages-pane-extensions.ts`, `apps/web/components/pages/navigation-pane/types/extensions.ts` | leere Extension-Punkte (`useExtendedEditorProps` → `{}`, `navigationPaneExtensions = []`) |
| R21 | `apps/web/components/pages/modals/export-page-modal.tsx`, `apps/live/src/controllers/pdf-export.controller.ts`, `apps/live/src/schema/pdf-export.ts` | CE-Export (PDF/Markdown clientseitig; Live-PDF-Endpunkt) |
| R22 | `apps/api/plane/db/models/deploy_board.py`, `packages/types/src/publish.ts` | `DeployBoard.TYPE_CHOICES` enthält `("page", "Page")`; `TPublishEntityType = "project" \| "page"` |
| R23 | `apps/web/hooks/use-workspace-paths.ts`, `apps/web/components/power-k/ui/modal/search-results-map.tsx` | Route-Muster `/{workspaceSlug}/wiki/{pageId}`, `isWikiPath` |
| R24 | `apps/web/components/pages/editor/ai/menu.tsx`, `apps/web/components/pages/editor/ai/ask-pi-menu.tsx`, `packages/constants/src/ai.ts`, `packages/editor/src/plugins/ai-handle.ts`, `apps/web/services/ai.service.ts` | AI-Menü-Hülle („Ask Pi“), AI-Handle-Plugin |
| R25 | `apps/api/plane/app/views/page/base.py` | `parent`-Handling, rekursives Archivieren (`unarchive_archive_page_and_descendants`) |
| R26 | `packages/types/src/home.ts`, `apps/web/components/home/widgets/recents/index.tsx` | Recents-Entity `workspace_page` |
| R27 | `apps/api/plane/db/models/asset.py` | `FileAsset.EntityTypeContext.PAGE_DESCRIPTION`, FK `page` |
| R28 | `apps/web/components/stickies/*`, `apps/api/plane/db/models/sticky.py`, `apps/api/plane/api/urls/sticky.py` | Stickies vollständig im CE |
| R29 | `apps/api/plane/bgtasks/page_transaction_task.py` | `COMPONENT_MAP` nur `mention-component`, `image-component` (erweiterbar über `component_map`) |
| R30 | `apps/web/hooks/use-additional-editor-mention.tsx`, `packages/types/src/search.ts` | CE-Mentions nur `user_mention`; `TSearchEntities` kennt `issue`, `project`, `cycle`, `module`, `page` |
| R31 | `apps/web/components/pages/navigation-pane/tab-panels/index.ts`, `apps/web/components/pages/navigation-pane/index.ts` | CE-Tabs `outline`, `info`, `assets`; Query-Param `paneTab`, `version`; Breite 294 px |
| R32 | `apps/web/components/pages/dropdowns/actions.tsx`, `apps/web/components/pages/editor/toolbar/options-dropdown.tsx` | `TPageActions` inkl. `"move"`, `"export"`, `"version-history"` |
| R33 | `apps/web/components/pages/editor/page-root.tsx`, `apps/web/services/page/project-page-version.service.ts` | Restore clientseitig; Service ruft nicht existierendes `…/versions/{id}/restore/` |
| R34 | `apps/web/components/pages/editor/editor-body.tsx`, `packages/editor/src/components/editors/document/collaborative-editor.tsx`, `packages/editor/src/hooks/use-yjs-setup.ts`, `packages/editor/src/hooks/use-collaborative-editor.ts` | Realtime-Konfiguration, User-Objekt `{id, name, color}`, HocuspocusProvider |
| R35 | `apps/api/plane/app/urls/page.py`, `apps/api/plane/api/urls/` | CE-Page-Routen (nur App-API, Projektseiten); Public-API v1 ohne Page-Routen |
| R36 | `apps/web/components/workspace/billing/comparison/base.tsx`, `apps/web/components/license/modal/upgrade-modal.tsx` | „One“ nicht mehr erhältlich (`shouldRenderPlanDetail`); Upgrade-Modal mit `PRO_PLAN_FEATURES` / `BUSINESS_PLAN_FEATURES` / `ENTERPRISE_PLAN_FEATURES` (Verifikation) |
| R37 | `packages/editor/src/constants/document-collaborative-events.ts`, `apps/web/hooks/use-realtime-page-events.tsx`, `apps/live/src/lib/stateless.ts` | Realtime-Seitenereignisse inkl. `move` (`MovedPayload {new_project_id, new_page_id}`), `duplicate` (`{new_page_id}`), `restore` (`RestoredPayload {deleted_page_ids?}`); CE-Client hat für `moved`/`duplicated`/`restored` **keinen** Handler (nur über `customRealtimeEventHandlers` erweiterbar) (Verifikation) |
| R38 | `apps/web/hooks/editor/use-editor-mention.tsx`, `apps/web/components/pages/editor/editor-body.tsx`, `apps/web/components/editor/document/editor.tsx`, `apps/web/hooks/use-parse-editor-content.ts` | Parameter `enableAdvancedMentions: true` nur im Document-Editor (Pages); im CE wirkungslos, da `useAdditionalEditorMention` leere Sektionen liefert (Verifikation) |
| R39 | `apps/web/store/pages/base-page.ts` | `lock`/`unlock` mit Parameter `recursive?: boolean`, im CE ignoriert (Verifikation) |
| R40 | `packages/editor/src/types/asset.ts` | `TAdditionalEditorAsset = never`; Assets-Tab im CE nur Bilder (Verifikation) |
| R41 | `packages/i18n/src/locales/en/workspace-settings.json` | OAuth-Scope-Beschreibung `applications.scope_description.wiki` „Access to wiki, and all wiki related entities“ (Verifikation) |

Offline-Quellen:

| ID | Pfad | Inhalt |
|---|---|---|
| D1 | `/home/user/makeplane/developer-docs/docs/api-reference/page/*.md` | Public-API v1: list/add/get Projekt- und Workspace(Wiki)-Seiten, Filter `type` (`all`, `public`, `private`, `shared`, `archived`), `parent_id` in Listen |
| D2 | `/home/user/makeplane/developer-docs/docs/api-reference/work-item-pages/*.md` | Work-Item-Page-Links (Objekt mit `page{… is_global …}`) |
| D3 | `/home/user/makeplane/developer-docs/docs/api-reference/workspace-features/overview.md` | Workspace-Feature-Flags `wiki`, `pi`, `teams`, `project_grouping`, `initiatives`, `customers` |
| D4 | `/home/user/makeplane/developer-docs/docs/self-hosting/plane-architecture.md` | Live: „Handles cursor positions, live updates, and presence indicators“; Space publiziert „projects, views, pages“ |
| D5 | `/home/user/makeplane/developer-docs/docs/dev-tools/mcp-server-tools.md` (Abschnitt `page — Pages`) | MCP-Aktionen `list`, `retrieve`, `create`, `list_workitem_pages`, `attach_to_workitem`, `detach_from_workitem` |
| D6 | `/home/user/makeplane/developer-docs/docs/api-reference/sticky/*.md` | Sticky-API v1 (identisch zum CE) |
| H1 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/values.yaml` | `services.iframely`, `services.drawio`, `services.live_exporter`, `env.export_queue_name`, `env.export_download_base_url`, `env.external_iframely_url`, `env.drawio_remote_url`, `services.pi.*` |
| H2 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/templates/config-secrets/live-env.yaml` | Live-Env: `IFRAMELY_URL`, `EXPORT_DOWNLOAD_BASE_URL`, `EXPORT_QUEUE_NAME`, `PI_BASE_URL`, `PI_BASE_PATH`, `AMQP_URL`, `REDIS_URL` |
| H3 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/templates/config-secrets/app-env.yaml` | API-Env: `DRAWIO_EMBED_URL`, `IFRAMELY_URL`, `EXPORT_QUEUE_NAME` |
| H4 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/templates/workloads/{drawio,iframely,live-exporter}.deployment.yaml` | Images `makeplane/drawio:v2.5.0` (Port 8080), `makeplane/iframely:v2.5.4` (Port 8061, `node server.js`), Exporter `LIVE_MODE=exporter` |
| H5 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/README.md` (Zeilen 944–966) | „RabbitMQ queue name for background PDF/DOCX export jobs consumed by the `live-exporter` service“; Exporter „pure queue consumer, no HTTP port“, „PDF render footprint is 500MB–2GB per job“ |
| H6 | `/home/user/makeplane/helm-charts/charts/plane-enterprise/templates/ingress-nginx.yaml` | `/live/`, `/drawio/(.*)` |

Per WebFetch von GitHub geladene Dokumentationsquellen (Branches des Repos `makeplane/developer-docs`):

| ID | URL | Inhalt |
|---|---|---|
| G1 | https://raw.githubusercontent.com/makeplane/developer-docs/docs-page-update-api/docs/api-reference/page/page-content-html.md | HTML-Vertrag aller Editor-Komponenten (siehe 3.45) |
| G2 | https://raw.githubusercontent.com/makeplane/developer-docs/docs-page-update-api/docs/api-reference/page/overview.md | Page-Objekt inkl. `parent_id`, `collection_id`, `page_collection_id`; „Body mutations made through the API are applied to Plane's collaborative document“ |
| G3 | …/docs-page-update-api/docs/api-reference/page/update-workspace-page.md | `PUT …/pages/{id}/`, 502/503 bei Collaborative-Service-Fehler |
| G4 | …/docs-page-update-api/docs/api-reference/page/archive-workspace-page.md | Archiv inkl. Subpages, Archiv vor Löschen |
| G5 | …/docs-page-update-api/docs/api-reference/page/delete-workspace-page.md | 400 bei aktivem (nicht archiviertem) Page |
| G6 | …/docs-page-update-api/docs/api-reference/page/confirm-workspace-page-attachment-upload.md | `PATCH …/pages/{id}/attachments/{attachment_id}/` `{is_uploaded}` |
| G7 | …/docs-page-update-api/docs/api-reference/collection/overview.md | Collection-Objekt, Zugriffsregeln, Member-Rollen 0/1/2 |
| G8 | …/docs-page-update-api/docs/api-reference/collection/move-or-reorder-collection-page.md | `placement` (`append`/`before`/`after`), Regeln für private Collections |
| G9 | …/docs-page-update-api/docs/api-reference/collection/delete-collection.md | `archive_pages` (Default `true`) |
| G10 | …/docs-page-update-api/docs/api-reference/collection/add-collection-member.md | `member`, `access` 0/1/2 |
| G11 | https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/collections/{overview,create-collection,delete-collection,manage-collection-members,manage-collection-pages}.md | v2-Collections inkl. Fehlercodes (402 `payment_required`) |
| G12 | https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/workspace-pages/overview.md | v2-Workspace-Page-Objekt |
| G13 | https://github.com/makeplane/helm-charts/pull/245 | `DRAWIO_EMBED_URL`, Editor lädt `<DRAWIO_EMBED_URL>/?embed=1…`, Viewer `<DRAWIO_EMBED_URL>/js/viewer-static.min.js`, Fallback diagrams.net-Cloud |
| G14 | https://raw.githubusercontent.com/makeplane/developer-docs/docs-page-update-api/docs/api-reference/page/{add-workspace-page,restore-workspace-page,download-workspace-page-attachment,delete-workspace-page-attachment}.md | Unterseiten-Anlage (`parent_id`, Statuscodes 201/202/400/403/404/502), Restore (`DELETE …/archive/`, 400 bei archiviertem Parent), Attachment-Download/-Löschen (Verifikation, per Sparse-Clone gelesen) |
| G15 | https://raw.githubusercontent.com/makeplane/developer-docs/docs/api-reference-v2/docs/api-reference/v2/workspace-features/overview.md | v2-Flag `is_wiki_enabled` („behind the `wiki.pages:*` scopes“), „A flag being `true` is necessary, not sufficient. Features also have to be available on the workspace's plan.“ (Verifikation) |

Web-Quellen (docs.plane.so / plane.so / developers.plane.so sind nicht direkt abrufbar; Inhalte stammen aus WebSearch-Zusammenfassungen und sind daher **nicht wortgetreu**):

| ID | URL(s) |
|---|---|
| W1 | https://docs.plane.so/core-concepts/pages/wiki, https://docs.plane.so/pages/wiki |
| W2 | https://docs.plane.so/core-concepts/pages/nested-pages |
| W3 | https://docs.plane.so/pages/organize-pages |
| W4 | https://docs.plane.so/core-concepts/pages/editor-blocks, https://docs.plane.so/pages/editor-blocks |
| W5 | https://docs.plane.so/pages/overview, https://docs.plane.so/core-concepts/pages/overview |
| W6 | https://docs.plane.so/pages/page-analytics |
| W7 | https://docs.plane.so/core-concepts/pages/inline-comments |
| W8 | https://plane.so/changelog/2026-10-15-page-comments-dashboard-custom-properties |
| W9 | https://plane.so/changelog/2025-10-15-ai-work-creation-inline-comments-filters |
| W10 | https://plane.so/blog/introducing-collections-and-ai-native-documentation |
| W11 | https://plane.so/blog/plane-wiki-and-pages-a-guide-to-team-documentation |
| W12 | https://plane.so/pricing (sowie Vergleichsblogs https://plane.so/blog/plane-vs-openproject-which-should-you-choose-in-2026, https://plane.so/blog/plane-vs-clickup-which-should-you-choose-in-2026) |
| W13 | https://plane.so/changelog/release-v-1-15-0-embeds-pages-and-integrations-for-connected-cross-team-work |
| W14 | https://plane.so/changelog/release-v2-5-3-docx-export-for-pages |
| W15 | https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more |
| W16 | https://plane.so/blog/whats-new-in-plane-august-2026 |
| W17 | https://plane.so/changelog/2026-08-14-collapsible-toggle-blocks-dashboard-intake-widgets |
| W18 | https://plane.so/changelog/2026-08-31-shared-views-tabs-in-pages-and-more |
| W19 | https://plane.so/changelog/2026-07-31-skills-plane-ai-richer-pages-audit-logs |
| W20 | https://plane.so/changelog/2026-06-30-mermaid-js-diagrams-pql-dashboard-filters |
| W21 | https://plane.so/changelog/2026-06-15-ai-block-in-pages |
| W22 | https://docs.plane.so/ai/plane-ai |
| W23 | https://docs.plane.so/templates/page-templates |
| W24 | https://developers.plane.so/api-reference/v2/workspace-page-templates/overview, https://developers.plane.so/api-reference/v2/project-page-templates/overview |
| W25 | https://developers.plane.so/api-reference/v2/published-pages/overview, https://developers.plane.so/api-reference/v2/published-pages/get-published-page |
| W26 | https://docs.plane.so/pages/report-page |
| W27 | https://docs.plane.so/integrations/draw-io, https://plane.so/marketplace/drawio, https://www.drawio.com/blog/diagrams-in-plane |
| W28 | https://plane.so/changelog/release-v-1-16-0-introducing-milestones-and-recurring-cycles |
| W29 | https://docs.plane.so/roles-and-permissions/permissions-matrix, https://docs.plane.so/roles-and-permissions/member-roles |
| W30 | https://docs.plane.so/core-concepts/workspaces/teamspaces |
| W31 | https://docs.plane.so/pages/page-labels |
| W32 | https://plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more |
| W33 | https://plane.so/changelog/2026-05-15-embed-media-in-the-editor-pql-in-dashboards-and-more |
| W34 | https://developers.plane.so/self-hosting/govern/environment-variables |
| W35 | https://docs.plane.so/core-concepts/stickies, https://developers.plane.so/api-reference/v2/stickies/overview |
| W36 | https://plane.so/changelog/2026-09-15-ai-memory-workspace-labels-ms-office-edits |
| W37 | https://plane.so/changelog/release-v-2-1-0-text-to-work-items-video-attachments-and-block-links |
| W38 | https://plane.so/changelog/release-v-1-13-0-duplicate-work-items-and-epics-across-projects |
| W39 | https://developers.plane.so/api-reference/v2/work-item-pages/overview, https://developers.plane.so/api-reference/v2/work-item-pages/create-work-item-page |
| W40 | https://plane.so/changelog/2025-09-01-recurring-items-doc-imports-nested-pages |
| W41 | https://plane.so/changelog/release-v2-6-0-pql-releases-wiki-collections-and-more, https://plane.so/changelog/2026-04-15-wiki-collections-initiative-boards |
| W42 | https://plane.so/changelog/release-v-2-4-0-plane-ai-now-available |
| W43 | https://plane.so/pro, https://plane.so/business, https://plane.so/enterprise-grid |
| W44 | https://plane.so/changelog/release-v2-5-0-project-labels-sso-for-god-mode-columns-in-pages |
| W45 | https://plane.so/blog/introducing-plane-wiki-and-pages |
| W46 | https://docs.plane.so/support/keyboard-shortcuts |
| W47 | https://plane.so/changelog/release-v2-6-0-plane-ai-across-app-workspace-switcher-updates |

### 1.3 Bewertung der Quellenlage

- **Code der Commercial Edition ist nicht verfügbar.** Belegbar sind: (a) die offizielle Plan-Matrix im Repo (R1, Stand der Matrix mit „COMING SOON“-Markierungen, älter als die aktuelle Preisseite), (b) im CE zurückgebliebene EE-Spuren (i18n-Texte, Typ-Unions, CSS-Selektoren, leere Extension-Punkte, Datenmodellfelder), (c) die API-Dokumentation (offline v1, online-Branches v1/v2), (d) Helm-Charts der Commercial Edition, (e) docs.plane.so/Changelog/Blog (nur als Such-Zusammenfassungen).
- **Plan-Zuordnungen widersprechen sich mehrfach** zwischen R1, R2, Doku-Labels und Blog (Details in Spalte „Abstufung“ und in Kap. 4). Für die Migration ist das nach **ADR-001 irrelevant** (alle Features aktiv); die Tier-Angaben dienen nur der Vollständigkeit/Nachvollziehbarkeit.
- **UI-Referenz für EE-only-Oberflächen fehlt im Repo.** Für ADR-005 (1:1) existieren für EE-only-Features weder Komponenten noch Styles im CE. Siehe Offene Punkte (Kap. 4, OP-01).
- Kennzeichnung: **UNVERIFIZIERT** = aus Indizien abgeleitet oder nur aus einer Such-Zusammenfassung; **Vorschlag** = Entwurf für die Zielarchitektur (kein Originalverhalten).

---

## 2. Feature-Tabelle

Legende CE-Status: `fehlt` | `Stub/UI-Hülle im CE` | `teilweise im CE` | `im CE vorhanden (nur Cloud-Gating)`.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Quelle |
|---|---|---|---|---|---|
| P07-01 | Wiki (Workspace-Seiten ohne Projekt) inkl. Wiki-Home, Sidebar, Feature-Toggle | Pro | Matrix: Free ✗, One/Pro/Business/Enterprise ✓ („One“ nicht mehr erhältlich, R36); `PRO_PLAN_FEATURES` „Wikis“ (Upgrade-Modal); Upsell-Text „…with Plane Pro“; Doku „Wiki Pro“ | Stub/UI-Hülle im CE | R1, R2, R3, R36, W1 |
| P07-02 | Wiki-Collections (öffentlich, Default „General“) | Pro | Doku: „Wiki and Collections are available on Pro and above“; Blog: Collections Pro+ | fehlt | W1, W10, R3 |
| P07-03 | Private Collections (nur eingeladene Mitglieder) | Business | Doku/Blog: Business+; Anlage nur durch Workspace-Admins | fehlt | W1, W10, W11, G7 |
| P07-04 | Nested Pages (Unterseiten, Hierarchie, Drag-Umhängen) | Business | Matrix: Business/Enterprise (COMING SOON; Zellwert fehlerhaft „Word-compatible + other format downloads“); `BUSINESS_PLAN_FEATURES` „Nested Pages“; Doku/Blog Business+ | teilweise im CE | R1, R2, R12, R25, W1, W2, W11 |
| P07-05 | Page-Versionen: Aufbewahrung | Pro | Matrix: Pro „2 days“, Business „3 months“, Enterprise „Unlimited“; aktuelle Preisseite: Pro „20 versions / 30 days“, Business „60 versions / 90 days“, Enterprise Grid „Unlimited“ | teilweise im CE | R1, W12, R13 |
| P07-06 | Page-Versionen: „Highlight changes“, Vergleich zweier Versionen, Server-Restore | unklar (vermutlich wie P07-05, UNVERIFIZIERT) | keine Plan-Angabe gefunden | fehlt | R4, R33, W5, W19, W42 |
| P07-07 | Real-time Collaboration: Presence-Avatare + Live-Cursor (Abgrenzung: CRDT-Sync ist CE) | Pro | Matrix: Free ✗, One+ ✓ (historisch; „One“ nicht mehr erhältlich, R36); Upsell-Text v1.4.2 „real-time collaboration … with Plane Pro“; `ONE_PLAN_FEATURES` „Real-time collab + public views and page“ | teilweise im CE | R1, R2, R3, R10, R34, R36, D4, W5, W45 |
| P07-08 | Page-Publish (öffentlicher Link, Kommentare Externer, Report) | Pro | Matrix: Free ✗, One+ ✓ (historisch, R36); Doku: Publish erfordert Pro; Upsell-Text „public pages … with Plane Pro“; `FREE_PLAN_UPGRADE_FEATURES` „Public Views and Pages“ | Stub/UI-Hülle im CE | R1, R2, R3, R22, R36, W5, W25, W26 |
| P07-09 | Page-Exports PDF/Word/Markdown, Queue, ZIP inkl. Unterseiten | Pro | Matrix: Free ✗, One ✗, Pro „One download at a time“, Business/Enterprise „Queued downloads“ | teilweise im CE | R1, R21, H1, H2, H5, W5, W14, W15, W16, W17 |
| P07-10 | Page Templates (Workspace- und Projekt-Ebene) | Pro | Matrix: Pro/Business/Enterprise ✓; Blog Pro+ | fehlt | R1, R6, W11, W23, W24 |
| P07-11 | Work-Item-Embeds (Block) | Pro | Matrix: One+ ✓ (historisch, R36); Doku-Label „Work item Pro“ | Stub/UI-Hülle im CE | R1, R19, R36, W4 |
| P07-12 | Work-Item-Mentions in Pages, „Create work item from selection“ | Business | Doku-Labels „Business“ (nur Such-Zusammenfassung) | Stub/UI-Hülle im CE | R30, R38, W5, W37 |
| P07-13 | Link Pages ↔ Work Items (Pages-Sektion im Work Item) | Pro | Matrix: One+ ✓ (historisch, R36); `ONE_PLAN_FEATURES` „Link pages in issues and vice-versa“; Changelog Pro | fehlt | R1, R2, R7, R36, D2, W38, W39 |
| P07-14 | Inline-Kommentare (an markiertem Text, Threads, Resolve) | Business | Blog: „Inline Page comments are available on Business“ | fehlt | R4, W7, W9, W11 |
| P07-15 | Page-Level-Kommentare + Kommentar-Filter + Moderation (hide/unhide) | unklar | keine Plan-Angabe gefunden | fehlt | W8, W32 |
| P07-16 | Page-Sharing / Access-Control (Mitglieder, can view/comment/edit) | Business | Doku: „On the Business plan and above, you can selectively share private Wiki pages…“ | Stub/UI-Hülle im CE | R8, R9, R11, W1, W5, W29 |
| P07-17 | Teamspace-Pages | Pro (UNVERIFIZIERT) | `PRO_PLAN_FEATURES` „Teamspaces“ | fehlt | R2, R15, W5, W30 |
| P07-18 | Page Labels (eigene Workspace-Labels) | Business | Blog/Doku: Business+ | teilweise im CE | R12, W1, W11, W31 |
| P07-19 | Moving Pages (Projekt ↔ Projekt ↔ Teamspace ↔ Wiki/Collection) | Pro | Doku: „Moving is marked as a Pro feature“ | Stub/UI-Hülle im CE | R4, R11, R12, R32, W3 |
| P07-20 | Databases + Formulas in Pages | Business (Matrix-Zeile, spezifischer) – strittig | Matrix: Business/Enterprise ✓ (COMING SOON); Upgrade-Modal (`ENTERPRISE_PLAN_FEATURES`) und `planHighlights.enterprise` nennen es Enterprise; nicht ausgeliefert | fehlt | R1, R2, R36 |
| P07-21 | Draw.io-Diagramme und -Boards | Pro (Integrationsdoku) / Business (Blog) | widersprüchlich | fehlt | R17, H1, H3, H4, G13, W4, W11, W27, W28 |
| P07-22 | Externe Embeds / Rich Cards (Iframely), Medien per URL | Pro | Doku-Label „Embed Pro“ | Stub/UI-Hülle im CE | R5, R16, R17, H1, H2, H3, W4, W13, W33 |
| P07-23 | Attachments in Pages (inkl. Office-Bearbeitung) | Pro | Doku-Label „Attachment Pro“; max. Dateigröße planabhängig (Cloud) | Stub/UI-Hülle im CE | R5, R16, R18, R27, R1 (Storage), W4, W36, G1, G6 |
| P07-24 | Video-Block | Pro | Doku-Label „Video Pro“ | fehlt | W4, W37 |
| P07-25 | Advanced Pages Analytics (Page + Collection) | Business | Matrix: Business/Enterprise (COMING SOON); Doku: Business | fehlt | R1, W6, W18 |
| P07-26 | Stickies-Erweiterungen | kein Bezahl-Gate belegbar | Matrix enthält keine Stickies-Zeile | im CE vorhanden (nur Cloud-Gating) | R28, D6, W35, W36 |
| P07-27 | Plane AI im Editor: Selection-Aktionen (Paraphrase, Simplify, Elaborate, Summarize, Get title, Ton) | unklar (Plane AI, UNVERIFIZIERT) | – | Stub/UI-Hülle im CE | R10, R24, W22 |
| P07-28 | Plane AI: AI-Block (`/ai`) | Business (Doku, UNVERIFIZIERT) | widersprüchlich: Doku/Guide Business, Blog Pro+; Doku als spezifischere/aktuellere Quelle gewählt (Blog W10 datiert vor dem Launch des AI-Blocks am 2026-06-15, W21) | fehlt | R5, W4, W10, W21, W22 |
| P07-29 | Plane AI: Prompt/Agent in Pages mit Proposals (accept/reject) | Business (Doku, UNVERIFIZIERT) | widersprüchlich: Doku Business, Blog Pro+; Doku gewählt | fehlt | W10, W22 |
| P07-30 | Editor-Block Columns (2/3/4 Spalten) | Pro | Doku-Label „Columns Pro“ | fehlt | W4, W44 |
| P07-31 | Editor-Block Tabs (horizontal/vertikal) | Business | Doku-Label „Tabs Business“ | fehlt | W4, W18 |
| P07-32 | Editor-Block Toggle (aufklappbar) | Business | Doku-Label „Toggle Business“ | fehlt | W4, W17 |
| P07-33 | Editor-Inline Status (farbiges Label) | Pro | Doku-Label „Status Pro“ | fehlt | W4, W19 |
| P07-34 | Editor-Inline Date | Pro | Doku-Label „Date Pro“ | fehlt | W4, G1 |
| P07-35 | Block- und Inline-Gleichungen (LaTeX) | Business | Doku-Label „Business“ | fehlt | W4, W40, G1 |
| P07-36 | Mermaid-Diagramm-Block | unklar | – | fehlt | W4, W20, W15 |
| P07-37 | HTML-Artifact-Block (sandboxed) | Business | Doku-Label „Business“ | fehlt | W4, W19 |
| P07-38 | Table-of-contents-Block | unklar | – | fehlt (nur Outline im Navigation-Pane) | W4, R31 |
| P07-39 | „Link pages“-Block (Live-Liste von Wiki-Seiten) | Business | Doku-Label „Business“, nur Wiki-Seiten | fehlt | W4, W5, W18 |
| P07-40 | Page-Embed-Block (`/page` = neue Unterseite) und „Linked page embed“ | Business (mit Nested Pages, UNVERIFIZIERT) | – | fehlt | G1, W2, W4, W15 |
| P07-41 | Widget-Block (Chart aus Work-Item-Daten) | unklar | – | fehlt | W4 |
| P07-42 | „Link dashboard widgets“-Block | Enterprise (Grid) | Doku-Label „Enterprise“ | fehlt | W4, W19 |
| P07-43 | Block-Links (Link auf einen Block kopieren) | unklar | – | fehlt | W37 |
| P07-44 | Page-Benachrichtigungen (Freigabe-Mail, Page-Subscriber) | unklar | – | fehlt | W13, W32 |
| P07-45 | Pages-Public-API (v1/v2: Pages, Collections, Templates, Published Pages, Attachments, Work-Item-Pages) | je Ressource wie Feature | v2 liefert `402 payment_required`, wenn das Feature nicht im Plan **oder abgeschaltet** ist; die 402-Zeile steht als Standardtabelle in 388 von 454 v2-Dokumenten (auch States, Stickies) und ist **kein** Tier-Beleg | fehlt | D1, D2, D5, G1–G15, W24, W25, W39 |
| P07-46 | Upgrade-/Downgrade-Flows des Wissensmanagements | – (Billing) | entfällt nach ADR-001 | Stub/UI-Hülle im CE | R3, R5, R1 |
| P07-47 | Erweiterte Mentions im Document-Editor (Seiten/Projekte/Zyklen/Module) und Backlinks (Verifikations-Ergänzung) | unklar | keine Plan-Angabe gefunden | Stub/UI-Hülle im CE | R12, R29, R30, R38 |

---

## 3. Feature-Abschnitte

### 3.0 Gemeinsame IST-Basis im CE (Referenz für alle Abschnitte)

**Datenmodell `Page`** (`apps/api/plane/db/models/page.py`): `workspace` FK, `name` Text, `description_json` JSON, `description_binary` Binary (Yjs-State), `description_html` Text (Default `<p></p>`), `description_stripped` Text, `owned_by` FK User, `access` SmallInt (`0` Public, `1` Private; Konstanten `PUBLIC_ACCESS=0`, `PRIVATE_ACCESS=1`), `color`, `labels` M2M über `PageLabel` auf `db.Label`, `parent` FK self (`related_name="child_page"`, `on_delete=CASCADE`), `archived_at` **Date**, `is_locked`, `view_props` (Default `{"full_width": False}`), `logo_props`, `is_global` Bool, `projects` M2M über `ProjectPage`, `moved_to_page` UUID, `moved_to_project` UUID, `sort_order` Float (Default `65535`), `external_id`, `external_source`. `save()` füllt `description_stripped`. `PageVersion`: `workspace`, `page`, `last_saved_at`, `owned_by`, `description_binary`, `description_html`, `description_stripped`, `description_json`, `sub_pages_data` JSON. `PageLog.TYPE_CHOICES`: `to_do`, `issue`, `image`, `video`, `file`, `link`, `cycle`, `module`, `back_link`, `forward_link`, `page_mention`, `user_mention`.

**Felder ohne CE-Funktion** (= EE-Spuren): `is_global` (nur in Suche `apps/api/plane/app/views/search/base.py` mit `is_global=True` gefiltert und in `apps/api/plane/bgtasks/workspace_seed_task.py` `is_global=False` gesetzt), `moved_to_page`, `moved_to_project`, `PageVersion.sub_pages_data` (im CE immer `{}`, `page_version_task.py`), `PageLog`-Typen `video`, `file`, `back_link`, `forward_link`, `page_mention`.

**Realtime im CE**: Hocuspocus-Server `apps/live`, nur Dokumenttyp `project_page` (`apps/live/src/types/index.ts`, `apps/live/src/services/page/handler.ts` wirft `Invalid document type` für alles andere). Der Browser verbindet sich mit `wss://…{LIVE_BASE_PATH}/collaboration?documentType=…&projectId=…&workspaceSlug=…` (`apps/web/components/pages/editor/editor-body.tsx`, `buildRealtimeConfig`). Fehlercodes beim Speichern: `content_too_large`, `page_locked`, `page_archived` (`apps/live/src/extensions/database.ts`, `packages/editor/src/constants/document-collaborative-events.ts`).

**Navigation-Pane** (rechte Seitenleiste der Seite): Breite `PAGE_NAVIGATION_PANE_WIDTH = 294`, Query-Param `paneTab` (`outline` | `info` | `assets`), `version` (`apps/web/components/pages/navigation-pane/index.ts`, `tab-panels/index.ts`). Erweiterungen über `INavigationPaneExtension { id, triggerParam, component, data?, width? }` – aktiv, wenn `paneTab === triggerParam` und kein `version`-Param gesetzt ist; eigene Breite möglich (`apps/web/components/pages/navigation-pane/root.tsx`). EE nutzt diesen Punkt für zusätzliche Panels (Kommentare `page_navigation_pane.tabs.comments.*` in R4; Analytics-Panel UNVERIFIZIERT).

**Seitenaktionen** `TPageActions` (`apps/web/components/pages/dropdowns/actions.tsx`): `full-screen`, `sticky-toolbar`, `copy-markdown`, `toggle-lock`, `toggle-access`, `open-in-new-tab`, `copy-link`, `make-a-copy`, `archive-restore`, `delete`, `version-history`, `export`, `move`. Reihenfolge im Editor-Menü: `full-screen`, `sticky-toolbar`, `copy-markdown`, `version-history`, `make-a-copy`, `archive-restore`, `delete`, `toggle-access`, `export` (`options-dropdown.tsx`); in der Liste: `open-in-new-tab`, `copy-link`, `make-a-copy`, `toggle-lock`, `toggle-access`, `archive-restore`, `delete` (`apps/web/components/pages/list/block-item-action.tsx`).

**Editor-Extension-Punkte** (leer im CE, EE füllt sie): `IEditorPropsExtended`, `TExtendedEditorCommands`, `TExtendedEditorRefApi` = `unknown/never` (`packages/editor/src/types/editor-extended.ts`); `coreEditorAdditionalSlashCommandOptions` liefert `[]` (`packages/editor/src/extensions/additional-slash-command-options.tsx`); `DocumentEditorAdditionalExtensions` nur `SlashCommands` (`packages/editor/src/extensions/document-extensions.tsx`); `TExtensions = "ai" | "collaboration-cursor" | "issue-embed" | "slash-commands" | "enter-key" | "image"` (`packages/editor/src/types/extensions.ts`). CE-Slash-Befehle: `text`, `h1`–`h6`, `numbered-list`, `bulleted-list`, `to-do-list`, `table`, `quote`, `code`, `callout`, `divider`, `emoji`, Textfarben, Hintergrundfarben, `image` (`packages/editor/src/extensions/slash-commands/command-items-list.tsx`).

**Allgemeiner Migrationshinweis (alle Features)**: Nach ADR-001 werden alle Gates (`usePageFlag`, `useEditorFlagging`-Deaktivierungen, Upsell-Komponenten) entfernt; Feature-Toggles bleiben nur dort, wo das Original fachliche Schalter hat (Workspace-Feature `wiki`, `pi`; Projekt-Feature `pages`, D3; `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/features/pages`). Nach ADR-003 wird das Schema neu entworfen; die JSON-Verträge (snake_case, Enum-Werte, Fehlercodes) folgen den unten zitierten API-Dokumenten.

---

### 3.1 P07-01 – Wiki (Workspace-Seiten ohne Projekt)

**Funktionsbeschreibung (UI & Verhalten)**
- Wiki = workspaceweite Wissensbasis für projektübergreifende Inhalte (Richtlinien, Architekturentscheidungen); Wiki-Seiten gehören dem Workspace, nicht einem Projekt (W1; D1 `overview.md`: „Workspace pages are accessible across all projects“).
- Eigener App-Bereich unter Route `/{workspaceSlug}/wiki/{pageId}` (R23: Power-K-Suchergebnis navigiert für Seiten ohne `project_ids` nach `/${workspace__slug}/wiki/${id}`; `useWorkspacePaths().isWikiPath` prüft `/${workspaceSlug}/wiki`).
- **Wiki-Home**: persönliche Übersicht; „Recents“ zeigt zuletzt geöffnete/geänderte Seiten mit Zeitstempel und Owner (W1 via Suche). Recents-Entity `workspace_page` existiert bereits in CE-Typen und Home-Widget (R26).
- **Sidebar-Sektionen**: Home, Favorites (erscheint erst ab einem Favoriten), Collections, Shared, Private, Archived (W1). Vordefinierte Bezeichner (i18n `wiki_collections.predefined`): `general` „General“, `private` „Private“, `shared` „Shared“, `archived` „Archived“ (R3).
- **„New page“**-Button oben in der Wiki-Sidebar; neue Seite landet in der aktuell geöffneten Collection, sonst als öffentliche Seite in „General“ und wird geöffnet (W1; Doku widersprüchlich, siehe OP-07). Tastenkürzel **D** legt im Wiki eine neue Seite an; Favorit **Shift + F** (W46).
- **Zugriff**: Workspace-Owner, -Admins, -Member; **Gäste** sehen „Permission denied“ (W1). Berechtigungsmatrix Wiki: Owner/Admin dürfen jede Seite sperren, archivieren/wiederherstellen, löschen, verschieben, publizieren; Member nur eigene; Erstellen und Duplizieren dürfen Member bei jeder Seite; Public/Private und Teilen nur eigene Seite (W29).
- **Feature-Toggle**: standardmäßig an; Workspace-Admin schaltet unter *Workspace settings › Wiki* („Turn on wiki for this workspace“) (W1); API-Flag `wiki` in Workspace-Features (D3; MCP `update_features` D5).
- Leerzustände (R8 `workspace_pages.empty_state`): `general` („Write a note, a doc, or a full knowledge base. Get Galileo, Plane's AI assistant, to help you get started“), `private`, `public` („No workspace pages yet“), `archived`, `shared` („No shared pages yet“ / „Pages that others have shared with you will appear here.“). Zusätzlich `workspace_empty_state.wiki` in `packages/i18n/src/locales/en/empty-state.json`. Bild-Assets für Wiki-Leerzustände existieren im CE: `apps/web/app/assets/empty-state/wiki/{all,archived,private,public}-{dark,light}.webp`, `{all-filters,name-filter}-{dark,light}.svg`, `navigation-pane/{assets,outline}-{dark,light}.webp`.
- Wiki-Seiten unterstützen alle Seitenfunktionen der Projektseiten plus: Collections, Teilen mit Mitgliedern, „Link pages“-Block (nur Wiki) (W5 Vergleichstabelle).

**Datenmodell-Hinweise**
- CE-Feld `Page.is_global` (R12) = „Seite lebt auf Workspace-Ebene“ (v2: „`true` if the page is at workspace level rather than inside a project“, G12). Wiki-Seite = `is_global = true` und keine `ProjectPage`-Zeile (v2: `project_ids` ist für Wiki-Seiten leer, W25).
- Zusätzliche Felder im Public-Objekt: `collection_id`, `page_collection_id` (G2), `parent_id` (D1, G12).
- **Vorschlag**: Tabelle `pages` mit Diskriminator `scope` (`project` | `wiki` | `teamspace`) statt reinem `is_global`; API liefert weiterhin `is_global` (ADR-003, Vertragsnähe).

**API-Hinweise**
- Public v1: `GET/POST /api/v1/workspaces/{slug}/pages/`, `GET/PUT/DELETE /api/v1/workspaces/{slug}/pages/{page_id}/`, `POST …/archive/`, Restore-Endpunkt (`restore-workspace-page.md` im Branch `docs-page-update-api`), Scopes `wiki.pages:read|write` (D1, G3–G5). Liste: `type` (`all` Default, `public`, `private`, `shared`, `archived`), `search`, `per_page` (Default 20, Max 100), `cursor` (D1 `list-workspace-pages.md`).
- Public v2: `GET/POST /api/v2/workspaces/{slug}/pages/`, `GET/PATCH/DELETE /api/v2/workspaces/{slug}/pages/{pk}/`, `?fields=` (requestable: `access`, `archived_at`, `collection_id`, `color`, `created_at`, `created_by_id`, `description_html`, `description_stripped`, `external_id`, `external_source`, `id`, `is_global`, `is_locked`, `logo_props`, `name`, `owned_by_id`, `parent_id`, `sort_order`, `view_props`), `?expand=owned_by,parent` (G12; `workspace-pages/create-workspace-page.md` im Branch `docs/api-reference-v2`).
- Feature-Flag/Scopes: v1-Flag `wiki` = v2 `is_wiki_enabled` („Whether the workspace-level wiki is available, behind the `wiki.pages:*` scopes“); ein `true`-Flag ist „necessary, not sufficient“, das Feature muss zusätzlich im Plan sein (G15) → nach ADR-001 nur das Flag. OAuth-Scope-Beschreibung `wiki` „Access to wiki, and all wiki related entities“ ist bereits im CE-i18n vorhanden (R41).
- Interne App-API (Web-Client): im CE nur projektgebunden `/api/workspaces/{slug}/projects/{project_id}/pages/…` (R35). Das Live-Service-Muster `${basePath}/pages/${pageId}/description/` (`apps/live/src/services/page/core.service.ts`) nutzt im CE `basePath = /api/workspaces/{slug}/projects/{projectId}` (`apps/live/src/services/page/project-page.service.ts`). Für Wiki **Vorschlag** (analog ohne Projektsegment, `basePath = /api/workspaces/{slug}`): `/api/workspaces/{slug}/pages/…` mit denselben Unterrouten wie Projektseiten (`archive/`, `lock/`, `access/`, `description/`, `versions/`, `duplicate/`, Favoriten). UNVERIFIZIERT.
- Realtime: `documentType=workspace_page` (R15).

**UI-Hinweise**
- Kein CE-Code für Wiki-Layout/Sidebar. Wiederverwendbar: Projektseiten-Liste (`apps/web/components/pages/list/*`), Editor (`apps/web/components/pages/editor/*`), Header-Aktionen (`apps/web/components/pages/header/*`).
- Breadcrumb im CE: Projekt › „Pages“ › Seiten-Switcher (`apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/header.tsx`); für Wiki analog „Wiki“ › Collection › (Eltern-Seiten) › Seite (UNVERIFIZIERT; Breadcrumbs für Hierarchie belegt in W2).

**Migrationshinweis**: Wiki immer verfügbar (ADR-001), Toggle `wiki` bleibt als fachliche Workspace-Einstellung. Angular-Route `/:workspaceSlug/wiki`, `/:workspaceSlug/wiki/:pageId`.

**Konfidenz**: hoch (Existenz, Route, Zugriff, Sidebar-Sektionen), mittel (Home-Inhalte, Platzierung neuer Seiten).

---

### 3.2 P07-02 – Wiki-Collections

**Funktionsbeschreibung**
- Collections gruppieren Wiki-Seiten unter einem benannten „Zuhause“ (W10). Collections selbst sind **flach**; Seiten darin können Hierarchien bilden (Suche „Plane nested pages“, W1). Sidebar: Collection aufklappen zeigt Seiten, Seite aufklappen zeigt Unterseiten (W1). Drag-and-drop-Umsortierung von Collections und Seiten in der Sidebar (W1, Changelog-Hinweis).
- **Default-Collection „General“** wird automatisch angelegt und enthält alle nicht verschobenen Seiten; sie ist geschützt (nicht änderbar/löschbar) (W1, G7: „The default collection cannot be modified or deleted“).
- Private Seiten und mit mir geteilte Seiten liegen **außerhalb** von Collections; sie wandern nur per Drag in eine Collection, was die Sichtbarkeit ändern kann (W1).
- **UI-Texte** (R3, vollständig):
  - Formular: `name_required` „Collection title is required“, `name_max_length` „Collection name must be less than 255 characters“, Platzhalter „Give a title to the collection“ / „Collection name“; Fallback-Name „Collection“.
  - Modale: „Create a collection“ / „Create collection“; „Edit collection“.
  - Löschen-Modal: Titel „Delete collection“; „This collection has {pageCount} page(s). Choose what happens to them.“; Option 1 „Transfer pages and delete collection“ – „Move all pages to another collection before deleting. Pages and their permissions are preserved.“, Warnung „Moved pages will inherit the permissions of the selected collection.“, Ziel-Label „Move pages to“, Platzhalter „Select a collection“; Option 2 „Delete collection with pages“ – „Permanently delete the collection and all its pages. This action can't be undone.“; Button „Delete collection“.
  - Header: „Add page“. Menü: „Create new page“, „Add existing page“, „Edit collection“, „Collection options“.
  - „Add existing page“-Modal: Suche „Search for pages“, Erfolg „{count} page(s) added to collection.“, Fehler „Pages could not be moved. Please try again.“, „No pages found matching your search“, „No pages available to move“, Button „Move“.
  - Liste: „Invite only“, „Restricted Access“, „Untitled“, „Collapse page“, „Expand page“, „Page actions“, „Page link copied to clipboard.“, Leerzustände „No matching pages“ / „Remove the search criteria to see all pages“ / „Remove the filters to see all pages“ / „No pages yet“ / „This collection doesn't have any pages right now.“, Fehler „Failed to remove page from collection.“. **Spalten**: „Page name“, „Owner“, „Nested pages“, „Last activity“, „Actions“.
  - Toasts: created, create_error, renamed, rename_error, transferred_deleted „Pages transferred and collection deleted.“, deleted_with_pages „Collection and its pages deleted.“, delete_error, target_required „Please select a collection to move pages to.“, create_page_error, create_page_in_collection_error, collection_link_copied.
  - Seitenaktion „Remove from collection“ (R4 `page_actions.remove_from_collection`).
- Eingeführt im Changelog v2.6.0 / 2026-04-15 (W41).

**Datenmodell-Hinweise** (Public-API-Objekt, G7/G11)
- Collection: `id`, `name`, `owned_by_id`, `access` (`0` public, `1` private, **nach Anlage unveränderlich**), `current_user_access` (`null` bei public; bei private Rolle des Aufrufers `0`/`1`/`2`), `has_pages`, `is_default` (Setzen entfernt Flag der bisherigen Default-Collection), `is_global`, `logo_props` (v1 Objekt z. B. Emoji, v2 String „editor-owned“), `sort_order` (Default `65535`), `page_ids` (v2), `workspace`, `created_at`, `updated_at`, `created_by`, `updated_by`.
- Seitenzugehörigkeit als eigenes Membership-Objekt (`page_collection_id`): `id`, `collection`, `page`, `workspace`, `sort_order`, Audit-Felder (G8).
- „A page and its sub-pages move together when added, moved, or removed“ (G7) → Zugehörigkeit wird nur für Wurzelseiten gespeichert, Unterseiten erben (UNVERIFIZIERT).
- **Vorschlag** Tabellen: `page_collections`, `page_collection_pages` (unique `page_id` aktiv), `page_collection_members` (siehe P07-03).

**API-Hinweise**
- v1 (`docs-page-update-api`, Verzeichnis `collection/`): `create-collection`, `list-collections`, `retrieve-collection`, `update-collection`, `delete-collection` (`DELETE …/collections/{id}/?archive_pages=true|false`; Default `true` = Seiten archivieren; `false` erhält Seiten nur bei **öffentlichen** Collections; Seiten privater Collections werden immer archiviert, G9), `list-collection-pages`, `add-collection-pages`, `remove-collection-page`, `move-or-reorder-collection-page` (`PATCH …/collections/{collection_id}/pages/{page_collection_id}/` mit `collection` (Ziel), `sort_order`, `placement {type: append|before|after, parent_id?, target_page_id (Pflicht bei before/after)}`; `placement` überschreibt `sort_order`, G8), `search-collection-pages`, Member-Endpunkte. Fehler: 400 (ungültige Platzierung, Default-Collection ändern/löschen), 403, 404 (G7). Scopes `write` oder `wiki.pages:write`.
- v2: `GET/POST /api/v2/workspaces/{slug}/collections/`, `GET/PATCH/DELETE …/{pk}/`, `GET/POST …/{pk}/members/` (Body `add: [{member_id, access}]`, `remove: [uuid]`, Antwort `{added, removed}`), `GET …/{pk}/pages-search/`, `POST …/{pk}/pages/` (Body `add`, `remove`), `?fields=`, `?expand=owned_by`; Fehler 400/401/402/403/404/406/409/413/415/429 im problem+json-Format (G11). Abweichung v1 ↔ v2 (Verifikation): v2-Create typisiert `access` als **string** („Who can see this.“, Wertebereich nicht dokumentiert, UNVERIFIZIERT) und `logo_props` als string, v1 nutzt integer `0`/`1` bzw. Objekt (G7, G11). `is_default` v2: „Make this the default for its parent. Setting it clears the flag on the previous default.“ Die 402-Zeile ist Standardtabelle aller v2-Endpunkte und belegt kein Tier (siehe P07-45).
- **Widerspruch UI ↔ API**: UI bietet „Transfer pages and delete collection“ (R3), API v1 nur `archive_pages` (G9). → Ziel bietet beides (OP-05).

**UI-Hinweise**: Collection-Liste als Tabelle mit den o. g. Spalten (R3); Collection-Link kopierbar („Collection link copied to clipboard.“, R3) → eigene Route je Collection (UNVERIFIZIERT, z. B. `/{slug}/wiki/collections/{collectionId}`).

**Konfidenz**: hoch (Objekt, Texte, Regeln), mittel (Routen, Vererbung).

---

### 3.3 P07-03 – Private Collections

**Funktionsbeschreibung**
- Eine Collection kann privat sein; nur eingeladene Personen sehen sie; sie erscheint weder in Sidebar noch Suche für Außenstehende (W10).
- Nur Workspace-Admins dürfen private Collections anlegen; der Ersteller wird automatisch mit Edit-Zugriff Mitglied; `access` ist nach Anlage unveränderlich (G7).
- Mitgliederrollen: `0` View, `1` Comment, `2` Edit („Edit content and arrange pages. Does not grant ownership.“); nur Collection-Owner oder Workspace-Admin verwaltet Mitglieder (G7, G10).
- Verschieberegeln (G8): Unterseite in privater Collection nicht einzeln verschiebbar; private Seite in öffentliche Collection → Baum wird öffentlich (falls erlaubt); Wurzelseite aus privater Collection heraus nur durch Workspace-Admin oder Owner des Seitenbaums **und** Edit-Zugriff auf Quell-Collection; Ziel privat → Zugriff auf Ziel erforderlich.
- Listen-Hinweis „Invite only“ / „Restricted Access“ (R3).

**Datenmodell**: `page_collection_members(collection_id, member_id, access smallint 0|1|2, workspace_id)`; Antwort v1 `id`, `collection`, `member`, `access`, `workspace`, Audit-Felder (G10). Feature-Gate „private collections feature“ (G7) entfällt nach ADR-001.

**API**: v1 `add-collection-member` (`member`*, `access` Default `0`), `update-collection-member`, `remove-collection-member`, `list-collection-members`; v2 `…/members/` (G10, G11).

**Konfidenz**: hoch.

---

### 3.4 P07-04 – Nested Pages

**Funktionsbeschreibung**
- Eltern-Kind-Hierarchie wie Ordner/Dateien, in Wiki-, Projekt- und Teamspace-Seiten (W2; W13: „Nested pages are now in Wiki, Projects, and Teamspaces“; Projektseiten seit 2025-09-01, W40).
- **Anlegen**: `/page` im Editor erzeugt eine Unterseite der aktuellen Seite und fügt einen Link-Block (Page-Embed) ein; im Wiki zusätzlich „+“ neben dem Seitennamen in der Sidebar (W2, W4). Per API (G14 `add-workspace-page.md`, wörtlich geprüft): „To create a child page, pass `parent_id`; Plane creates the page and inserts a page embed into the parent document. The parent must be visible, editable, unlocked, and active.“; `parent_id` darf nicht mit `collection_id` kombiniert werden; Antworten `201` (Kind angelegt und im Eltern-Dokument verlinkt), `202` (Kind angelegt, Eltern-Link wird noch nachversucht; `parent_id` steht bereits in der Antwort), `400` (Parent gesperrt/archiviert oder `parent_id`+`collection_id`), `403` (kein Edit-Recht am Parent), `404` (Parent nicht verfügbar), `502` (Eltern-Link abgelehnt, das neue Kind wurde wieder entfernt). Embed-Vertrag: G1 `page-embed-component`.
- **Sperren**: Store-API `lock`/`unlock({ shouldSync, recursive })` hat einen Parameter `recursive`, den das CE ignoriert (R39) → Hinweis auf rekursives Sperren/Entsperren eines Seitenbaums in der EE (UNVERIFIZIERT).
- **Wiederherstellen aus Archiv**: EE-API v1: „If its parent is archived, restore the parent before restoring the child; otherwise the API returns `400`.“ (G14 `restore-workspace-page.md`, Restore = `DELETE …/pages/{id}/archive/`). **Abweichung zum CE**: CE-`unarchive` löst stattdessen die Eltern-Beziehung (`page.parent = None`), wenn der Parent archiviert ist (R25). Ziel folgt dem dokumentierten EE-Vertrag (400) für die Public-API; für die interne UI ist das Verhalten im Original nicht belegt (UNVERIFIZIERT).
- **Umhängen**: Drag in der Sidebar hoch/runter = befördern/zurückstufen (W2).
- **Navigation**: Einrückung, Auf-/Zuklappen, Breadcrumbs mit vollem Pfad (W2).
- **Sichtbarkeit**: Unterseiten erben die Sichtbarkeit **nicht**; private Unterseite unter öffentlicher Elternseite bleibt eingeschränkt; wer die Elternseite nicht sehen darf, sieht keine Unterseiten (W2).
- **Archivieren**: Elternseite archivieren archiviert Unterseiten (W2; G4 „Archive a workspace page and its subpages“). **Löschen**: Option, Kinder zu behalten, indem sie eine Ebene hochrücken (W2). CE-Vergleich: Löschen ist nur für archivierte Seiten erlaubt (400 „The page should be archived before deleting“), die Kinder werden per `update(parent=None)` zu **Wurzelseiten** (nicht eine Ebene höher) und bleiben archiviert, weil das Archivieren rekursiv war (R25). „Eine Ebene hoch“ (= Großeltern als neuer Parent) ist EE-Verhalten laut W2 (UNVERIFIZIERT, nur Such-Zusammenfassung).
- **Verschieben**: Unterseiten wandern mit (W3).
- Import: Notion/Confluence-Importer übernehmen Unterseiten als Nested Pages (Querverweis Importer-Cluster; W-Suche).
- Collections-Tabelle zeigt Spalte „Nested pages“ (R3); Analytics zählt „nested pages“ (W6).
- **Inhaltslimit**: CE-Banner „Content limit reached and live sync is off. Create a new page or use nested pages to continue syncing.“ (R4 `page_content_limit_banner`, ausgelöst durch Fehlercode `content_too_large`, `apps/web/components/pages/editor/page-root.tsx`).
- Downgrade-Banner „Nested pages require a paid plan. Upgrade to unlock.“ (R3) → entfällt (ADR-001).

**CE-Stand (teilweise)**: `Page.parent` (R12); Liste/Summary nur Wurzelseiten (`.filter(parent__isnull=True)`, R25); `partial_update` akzeptiert `parent` (validiert Existenz im selben Projekt, R25); Archivieren/Wiederherstellen rekursiv per CTE `unarchive_archive_page_and_descendants` (R25); Wiederherstellen löst Parent, wenn Parent archiviert ist (R25); Löschen setzt `parent=None` bei Kindern (R25); `PageVersion.sub_pages_data` (R12). **Keine** UI für Hierarchie, kein Endpunkt zum Laden von Unterseiten.

**Datenmodell-Hinweise**: `parent_id` (self FK), `sort_order` je Geschwisterebene; `sub_pages_data` in Versionen (Snapshot der Unterseiten-Embeds zum Versionszeitpunkt, UNVERIFIZIERT). **Vorschlag**: rekursive Abfragen per CTE oder `ltree`-Pfadspalte in PostgreSQL für Breadcrumbs/Teilbäume.

**API-Hinweise**: `parent_id` in Page-Objekt und Update (v2 PATCH nullable, W-Suche „project pages overview“); MCP keine Hierarchie-Aktion (D5). **Vorschlag** interne Endpunkte: `GET …/pages/{id}/sub-pages/`, `POST …/pages/{id}/move/` (Reparent + Platzierung analog `placement` aus G8).

**UI-Hinweise**: Seitenbaum in Wiki-Sidebar und in Projekt-/Teamspace-Seitenliste (Expand/Collapse, R3 „Collapse page“/„Expand page“).

**Konfidenz**: hoch (Verhalten), mittel (API-Interna).

---

### 3.5 P07-05 – Page-Versionen: Aufbewahrung

**Funktionsbeschreibung**
- Versionsliste im Info-Tab des Navigation-Pane (Zeitstempel, Bearbeiter); Version öffnen = Nur-Lese-Ansicht; Restore macht sie zur aktuellen Version und erzeugt einen neuen Historieneintrag (W5). Aufruf über „•••“ › „Version history“ (W5; CE-Menüpunkt `version-history` setzt `paneTab=info`, R32).
- Aufbewahrung je Plan: Repo-Matrix „2 days“ (Pro), „3 months“ (Business), „Unlimited“ (Enterprise) (R1); aktuelle Preisseite „20 versions / 30 days“, „60 versions / 90 days“, „Unlimited“ (Enterprise Grid) (W12).
- Draw.io-Diagrammänderungen sind **nicht** Teil der Versionshistorie (ältere Versionen zeigen das aktuelle Diagramm) (W27, drawio-Blog).

**CE-Stand (teilweise)**: Versionierung nach jedem `PATCH …/description/` per Celery `track_page_version` (R13): neue Version nur wenn `description_html` geändert; letzte Version desselben Users innerhalb `PAGE_VERSION_TASK_TIMEOUT = 600` s wird überschrieben (Zusammenfassung); >20 Versionen → älteste löschen; Cleanup-Task `delete_page_versions` hält max. 20 je Seite (Window `row_number` nach `created_at desc`) (R13). Keine zeitbasierte Aufbewahrung. Endpunkte `GET …/pages/{page_id}/versions/` und `…/versions/{pk}/` (R35, `apps/api/plane/app/views/page/version.py`). **Befund (statisch verifiziert, nicht ausgeführt)**: `track_page_version` liest `page.description` (Zeilen 45 und 63: `description_json=page.description`), `Page` definiert aber nur `description_json`; weder `BaseModel` (`apps/api/plane/db/models/base.py`) noch die Mixins `TimeAuditModel`/`UserAuditModel`/`SoftDeleteModel` (`apps/api/plane/db/mixins.py`) stellen ein Attribut `description` bereit → `AttributeError`, vom generischen `except Exception` per `log_exception` geschluckt; im CE entstehen damit über den Description-Endpunkt keine Versionen. Die Contract-Tests (`apps/api/plane/tests/contract/app/test_page_version_project_scope_app.py`) legen Versionen direkt per `PageVersion.objects.create` an und decken den Task nicht ab. Ziel muss das korrekt implementieren.
- Matrix markiert Versions für Free als ✗ (R1), obwohl die CE-UI Versionen anbietet → Plan-Abweichung CE/Cloud-Free.

**Datenmodell**: `page_versions` wie CE (R12) + **Vorschlag** Instanz-Einstellungen `page_version_max_count` (Default unbegrenzt), `page_version_retention_days` (Default unbegrenzt), `page_version_coalesce_seconds` (Default 600) (ADR-001: Limits → konfigurierbar).

**API**: CE-Verträge `TPageVersion` (`packages/types/src/page/core.ts`): `created_at`, `created_by`, `deleted_at`, `description_binary?`, `description_html?`, `description_json?`, `id`, `last_saved_at`, `owned_by`, `page`, `updated_at`, `updated_by`, `workspace`.

**Konfidenz**: hoch (Tiers belegt, zwei Stände), hoch (CE-Logik).

---

### 3.6 P07-06 – Versionen: „Highlight changes“, Vergleich, Server-Restore

**Funktionsbeschreibung**
- Toggle **„Highlight changes“** (Standard an) unten im Info-Panel markiert, was die gewählte Version hinzugefügt/geändert hat (W5; i18n-Key `page_navigation_pane.tabs.info.version_history.highlight_changes` existiert, wird im CE nicht verwendet, R4).
- v2.4.0: „highlighted diffs“ zwischen Bearbeitungen; Februar 2026: „version history with multi-user diffs“ (W42, Suchzusammenfassung).
- 2026-07-31 / v3.1.0: Vergleich **beliebiger zweier Versionen** („Compare page versions“) (W19, W15). Bedienablauf zur Auswahl zweier Versionen nicht dokumentiert (UNVERIFIZIERT).
- Server-Restore: CE-Web-Service **definiert** `restoreVersion` → `POST /api/workspaces/{slug}/projects/{project_id}/pages/{page_id}/versions/{version_id}/restore/` (R33) und verdrahtet es als Handler `restoreVersion` in `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/pages/(detail)/[pageId]/page.tsx`; **aufgerufen wird der Handler im CE nirgends** (Verifikation per grep). Die CE-API hat die Route nicht (R35); der CE stellt rein clientseitig wieder her (`handleRestoreVersion`: `clearEditor()` + `setEditorValue(descriptionHTML)`, an `PageVersionsOverlay.handleRestore` übergeben, R33). → EE hat vermutlich den Server-Endpunkt (UNVERIFIZIERT).
- Realtime-Ereignis `restore` (Client-Name `restored`) mit `RestoredPayload { deleted_page_ids?: string[] }` existiert in den CE-Konstanten, ohne CE-Handler (R37) → Indiz, dass ein Restore in der EE gelöschte Unterseiten wiederherstellt bzw. meldet (passt zu `PageVersion.sub_pages_data`; UNVERIFIZIERT).

**Datenmodell**: keine zusätzlichen Tabellen nötig; Diff wird aus `description_json`/`description_binary` zweier Versionen berechnet. **Vorschlag**: Diff auf ProseMirror-JSON-Ebene im Angular-Client (Mark-Dekorationen „added/removed“), Restore serverseitig über Yjs-Update auf dem Live-Dokument (damit verbundene Clients konsistent bleiben, analog G2 „Body mutations … are applied to Plane's collaborative document“).

**Konfidenz**: mittel.

---

### 3.7 P07-07 – Real-time Collaboration (Abgrenzung zum CE)

**Funktionsbeschreibung (Bezahl-Teil)**
- Mehrere Personen bearbeiten eine Seite gleichzeitig; **Profilbilder** der Anwesenden erscheinen oben im Dokument; **farbiger Cursor** pro Kollaborator mit Live-Bewegung (W5, Suchzusammenfassung „Plane pages real-time collaboration“; W45: „cursors show where your teammates are typing“, Yjs-CRDT über WebSocket).
- Live-Dienst „Handles cursor positions, live updates, and presence indicators“ (D4).
- Matrix-Text: „Edit a page together with members in your project, team, or workspace.“ (R1).
- **Tier (Verifikation)**: Pro. Die Matrix führt das Merkmal ab „One“, dieser Plan ist aber nicht mehr erhältlich (R36); das CE-Upsell nennt „real-time collaboration“ als Pro-Freischaltung (R3).

**Abgrenzung CE (teilweise)**
- CE hat **CRDT-Sync** (Tiptap `Collaboration` auf `provider.document`, Felder `default` und `title`, `use-collaborative-editor.ts`), Hocuspocus-Server, Offline-/Sync-Badges (`apps/web/components/pages/header/offline-badge.tsx`, `syncing-badge.tsx`), Statusmaschine `CollabStage` (`packages/editor/src/types/collaboration.ts`). Gleichzeitiges Bearbeiten funktioniert also im CE.
- CE **deaktiviert** `"collaboration-cursor"` in allen Editoren (R10); im Editor-Paket existiert keine Cursor-/Caret-Extension (kein `@tiptap/extension-collaboration-cursor`/`-caret` in `packages/editor/package.json`). Der Client sendet bereits ein User-Objekt `{ id, name: display_name, color: hslToHex(generateRandomColor(id)) }` als Hocuspocus-Token (`editor-body.tsx` `userConfig`; `collaborative-editor.tsx` `token = JSON.stringify(user)`), das für Awareness genutzt werden kann.
- Realtime nur für `project_page` (R14); Wiki- (`workspace_page`) und Teamspace-Seiten (`team_page`, `teamId`) sind EE (R15).

**Datenmodell**: keine Persistenz für Presence (flüchtig, Yjs-Awareness). Dokumentzustand: `description_binary` (Yjs-Update).

**API/Protokoll**: y-protocols Sync + **Awareness**-Nachrichten; Awareness-State je Client: `user {id, name, color}` (Vorschlag gemäß Tiptap-Collaboration-Caret-Konvention, UNVERIFIZIERT für EE). WebSocket-Pfad `{LIVE_BASE_PATH}/collaboration`, Query `documentType`, `projectId`, `teamId`, `workspaceSlug` (R15, `editor-body.tsx`).

**UI-Hinweise**: Avatar-Stapel im Seiten-Header (Position UNVERIFIZIERT: „at the top of the document“, W5); Cursor-Label mit Namen in Benutzerfarbe (UNVERIFIZIERT).

**Migrationshinweis (ADR-002)**: YDotNet-Server muss Awareness-Nachrichten empfangen, an alle Verbindungen desselben Dokuments verteilen, bei Disconnect entfernen und Timeouts (Standard y-protocols 30 s) beachten; Skalierung über mehrere Instanzen via Redis-Pub/Sub oder PostgreSQL `LISTEN/NOTIFY` (CE nutzt Redis-Extension `apps/live/src/extensions/redis.ts`). Angular: Tiptap-`CollaborationCaret` (MIT) bündeln.

**Konfidenz**: hoch (Abgrenzung durch Code belegt), mittel (exakte UI).

---

### 3.8 P07-08 – Page-Publish

**Funktionsbeschreibung**
- „Publish“-Button oben rechts; erzeugt eindeutigen Link; jeder mit Link öffnet die Seite ohne Login; Betrachter können **ohne Workspace-Konto** kommentieren (W5; Matrix: „Put your pages on the web for external users and let them comment without signing into your workspace.“, R1).
- Projekt- und Wiki-Seiten publizierbar, **Teamspace-Seiten nicht** (W5).
- **Tier (Verifikation)**: Pro (Doku, Upsell „public pages … with Plane Pro“, R3); Matrix „One+“ ist historisch (R36).
- Berechtigung: Projektseiten – Admin jede Seite, Contributor nur eigene, Commenter/Guest nicht; Wiki – Owner/Admin jede, Member eigene (W29).
- **Archivieren hebt die Veröffentlichung auf**, Wiederherstellen veröffentlicht **nicht** erneut (W5, W25).
- Published-Seite zeigt Tabs (umschaltbar, nicht editierbar) (W4 Tabs-Block); Fußzeile „Powered by Plane Pages“ (i18n-Key `powered_by_plane_pages`, im CE unbenutzt, R9).
- **„Report a published page“**: Dialog mit Gründen „Phishing or spam“, „Inappropriate content“, „Copyright / DMCA takedown“, „Other violation“ (Beschreibung Pflicht); kein Konto nötig; „Report this page“ öffnet E-Mail-Client mit vorbefüllter Nachricht an Support; Folgen: Seite deaktivieren, Workspace sperren, Konto beenden (W26). Cloud-spezifisch.

**CE-Stand (Stub)**: `DeployBoard.TYPE_CHOICES` enthält `page` (R22), `TPublishEntityType = "project" | "page"`, `TPublishSettings { anchor, entity_identifier, entity_name, is_comments_enabled, is_reactions_enabled, is_votes_enabled, … }` (R22); Space-App hat nur Routen `/:workspaceSlug/:projectId` und `/issues/:anchor` (`apps/space/app/routes.ts`).

**Datenmodell**: `deploy_boards` mit `entity_name='page'`, `entity_identifier=page_id`, `anchor` = 32-stelliges Hex (CE `get_anchor = uuid4().hex`, R22; W25 „32-character hex string“), `is_comments_enabled`, `is_reactions_enabled`, `is_disabled` (für Moderation). Kommentare Externer: Ziel-Tabelle siehe P07-15 mit `actor` = Space-Benutzer oder anonym (OP-09).

**API**: v2 `GET /api/v2/workspaces/{slug}/published-pages/{anchor}/` (read-only; es gibt **keine** Publish/Unpublish-Operation in der Public-API; Anchor gewährt Lesezugriff ohne Mitgliedschafts-/Access-Prüfung; 404 bei unbekanntem Anchor, fremdem Workspace, Nicht-Page-Entität, gelöschter/unveröffentlichter/archivierter Seite; `collection_id` immer `null`; `project_ids` leer für Wiki-Seiten; v1 war projektgebunden) (W25). Interne Publish-Endpunkte **Vorschlag** analog Projekt-Publish (`/api/workspaces/{slug}/projects/{pid}/pages/{id}/publish/` bzw. `/api/workspaces/{slug}/pages/{id}/publish/`).

**Migrationshinweis**: Angular-Space-App erhält Route für Seiten (Vorschlag `/pages/:anchor`); Report-Funktion für Self-hosted: konfigurierbare Melde-Adresse in God-Mode oder ausblenden (ADR-004, OP-10).

**Konfidenz**: hoch (Verhalten), mittel (Space-Route, Kommentar-Identität).

---

### 3.9 P07-09 – Page-Exports (PDF / Word / Markdown, Queue, ZIP)

**Funktionsbeschreibung**
- Formate PDF, Word (.docx), Markdown (W5); DOCX seit v2.5.3 (W14, zugleich bessere Tabellenspaltenbreiten im PDF).
- Matrix: Pro „One download at a time“, Business/Enterprise „Queued downloads“ (R1).
- v3.1.0 / August 2026: PDF- und DOCX-Exporte laufen **im Hintergrund**; Export einer Seite **mit allen Unterseiten als ein ZIP** (W15, W16, W17); Mitglieder öffnen die Export-Seite und laden **eigene** Exporte herunter (W15).
- Berechtigung „Export Pages“ für alle Rollen inkl. Guest (W11; Projekt-Matrix: Commenter darf sichtbare exportieren, Guest nur eigene, W29).
- Infrastruktur (H1, H2, H5): RabbitMQ-Queue `EXPORT_QUEUE_NAME` (Default `plane-exports`), Konsument `live-exporter` (gleiches Image wie live, `LIVE_MODE=exporter`, „pure queue consumer, no HTTP port“, 500 MB–2 GB RAM pro PDF-Job, horizontal skalieren), Job-Status in Redis, `EXPORT_DOWNLOAD_BASE_URL` (Basis-URL für Download-Redirects, Default `<scheme>://<licenseDomain>`).

**CE-Stand (teilweise)**
- Export-Modal (R21): Format `pdf` | `markdown`; Seitenformat `A4`, `A3`, `A2`, `LETTER` („Letter“), `LEGAL` („Legal“), `TABLOID` („Tabloid“); Inhalt `everything` („Everything“) | `no-assets` („No images“); Defaults `pdf`/`A4`/`everything`. Dateiname: Titel klein, `[^a-z0-9-_]`→`-`, Mehrfach-`-` zusammengefasst; PDF `{name}-{seitenformat klein}.pdf` (z. B. `meeting-notes-a4.pdf`, `${fileName}-${selectedPageFormat.toString().toLowerCase()}.pdf`), Markdown `{name}.md`. PDF clientseitig via `@react-pdf/renderer` mit `<h1 class="page-title">${pageTitle}</h1>` + Dokument-HTML; Custom-Komponenten werden vorher ersetzt (`useParseEditorContent`, `apps/web/hooks/use-parse-editor-content.ts`): HTML-Pfad ersetzt `mention-component` durch `<span data-node-type="mention-block">` mit Anzeigetext (User-Mentions; andere `entity_name` über `parseAdditionalEditorContent`, im CE `undefined`), ersetzt `image-component` durch `<img>` (bei „No images“ werden `image-component` und `img` entfernt), wandelt Bilder in Base64, ersetzt `input[type='checkbox']` durch `div` (Klasse für „checked“), entfernt `issue-embed-component`, entfernt `background-color: null`/`color: null`; Markdown-Pfad ersetzt Mentions durch `[display_name](redirect_url)` und `image-component` durch `<img src>` (bzw. entfernt bei „No images“) und entfernt `issue-embed-component`.
- Live-Server-Endpunkt `POST {live}/pdf-export` (synchron, Body `pageId`*, `workspaceSlug`*, `projectId?`, `title?`, `author?`, `subject?`, `pageSize?` (A4|A3|A2|LETTER|LEGAL|TABLOID), `pageOrientation?` (portrait|landscape), `fileName?`, `noAssets?`; Fehler 400/401/404/502/504/500; Antwort `application/pdf` mit `Content-Disposition` RFC 5987) (R21) – vom Web-Client im CE nicht genutzt.
- Kein DOCX, keine Queue, kein ZIP, keine Exporthistorie für Seiten (CE-`ExporterHistory` nur Work Items, `apps/api/plane/db/models/exporter.py`).

**Datenmodell (Vorschlag)**: `page_export_jobs(id, workspace_id, page_id, requested_by_id, format pdf|docx|markdown, page_size, orientation, no_assets, include_sub_pages, status queued|processing|completed|failed|expired, file_asset_id, error, created_at, started_at, completed_at, expires_at)`. Download-Ablaufzeit konfigurierbar (W15 erwähnt Ablauf für Work-Item-Exporte in God-Mode).

**Migrationshinweis (ADR-002)**: Kein Node: PDF- und DOCX-Rendering in .NET-Worker (Vorschlag: PDFsharp/MigraDoc für PDF, `DocumentFormat.OpenXml` für DOCX, beide MIT); Queue als PostgreSQL-Tabelle mit `FOR UPDATE SKIP LOCKED` oder Aspire-RabbitMQ-Ressource (Architekturentscheidung offen, OP-11); ADR-001: Parallelität nicht nach Plan beschränkt.

**Konfidenz**: hoch (Formate, Queue-Infrastruktur), mittel (UI des Export-Dialogs in EE, Exporthistorie für Seiten).

---

### 3.10 P07-10 – Page Templates

**Funktionsbeschreibung**
- Wiederverwendbare Seitenstrukturen; Verwaltung in *Workspace Settings › Templates* (Workspace-Ebene) und in *Project Settings* (Projekt-Ebene) (W23). „Create template“ › Seiten-Option → Formular Name, Beschreibung, Layout-Inhalt → „Create page template“ (W23; R6 `templates.settings.new_page_template`, `form.page.template.name.placeholder` „Name your page template.“, Validierung „Template name is required“ / „…less than 255 characters“, `form.page.name.placeholder` „Untitled page“, `form.page.button.create|update`).
- Verwenden: im Projekt- oder Wiki-Bereich „+“ → Template-Picker („Choose from template“, R6 `dropdown.label.page`) oder „Use template“ in den Template-Einstellungen („Use template“/„Applying“, R6) (W23). Leerzustände `empty_state.page.no_templates` („There are no templates you have access to.“ / „Please create a template“), `no_results` (R6).
- Template-Quelle-Info „Derived from workspace“ / „Derived from project“ (R6 `template_source`).
- Berechtigung: „Contact your project admin to create templates“ / „Contact your workspace admin to create templates“ (R6 `create_template.no_permission`).
- Beispiele: PRD, Engineering-RFC, Incident-Report, Retrospektive, Meeting-Notes (W11).
- Templates in Projekt-, Wiki- und Teamspace-Seiten verfügbar (W23 via Suche).
- Marketplace-Publish von Templates (R6 `form.publish.*`) ist Cloud-Marketplace (Cross-Cluster Templates).

**Datenmodell** (W24): Template-Objekt `id`, `name` (≤255), `description_html` (Beschreibung des Templates), `short_description` (nullable), `template_type` (immer `"page"`), `project_id` (`null` für Workspace-Templates), `template_data` (Seiten-Seed: Titel, HTML-Body, Anzeigeeinstellungen; `parent` – wenn nicht leer, Pflichtschlüssel `id`, `project_id`, `project_identifier`; nur Formprüfung), `created_at`, `updated_at`. Workspace- und Projekt-Templates sind getrennte Scopes.

**API** (W24): `GET/POST /api/v2/workspaces/{slug}/page-templates/`, `GET/PATCH/DELETE …/{id}/`; Projekt-Variante analog unter `…/projects/{project_id}/page-templates/` (UNVERIFIZIERT exakter Pfad).

**Konfidenz**: hoch (Objekt), mittel (UI-Fluss).

---

### 3.11 P07-11 – Work-Item-Embeds in Pages

**Funktionsbeschreibung**
- Block „Work item“ (nur Pages) platziert eine Karte eines Work Items mit dessen aktuellen Details; Alternative inline per `@` (W4). Matrix: „Embed work items from any project you are a member of.“ (R1).
- Archivierte eingebettete Work Items öffnen in Nur-Lese-Peek-View (W33).
- **Tier (Verifikation)**: Pro (Doku-Label „Work item Pro“); Matrix „One+“ historisch (R36).
- CE-Export entfernt `issue-embed-component` vollständig aus PDF und Markdown (`apps/web/hooks/use-parse-editor-content.ts`), der CE-Live-PDF-Renderer hat keinen Renderer dafür (`apps/live/src/lib/pdf/node-renderers.tsx`) → Ziel-Exporter (P07-09) muss eine Darstellung der Karte definieren (Vorschlag: Identifier + Titel als Link).

**CE-Stand (Stub)**: Node `issue-embed-component` (`CORE_EXTENSIONS.WORK_ITEM_EMBED`), `group: block`, `atom`, `draggable`; Attribute `entity_identifier`, `project_identifier`, `workspace_identifier`, `id`, `entity_name` (R19). NodeView `WorkItemEmbedExtension({ widgetCallback({issueId, projectId, workspaceSlug}) })` existiert, wird aber nirgends registriert; nur `WorkItemEmbedExtensionConfig` in `DocumentEditorExtensionsWithoutProps` (Parsing) (R19). Typ `TIssueEmbedConfig` (`packages/editor/src/types/issue-embed.ts`); `TEmbedItem {id, title, subTitle, icon, projectId, workspaceSlug}` (`packages/editor/src/types/embed.ts`). Drag-Selektor `.issue-embed` (R17). Kein Slash-Befehl.

**HTML-Vertrag** (G1): `<issue-embed-component id="…" entity_identifier="WORK_ITEM_UUID" project_identifier="PROJECT_UUID" workspace_identifier="WORKSPACE_SLUG" entity_name="issue"></issue-embed-component>`.

**Datenmodell**: Referenz nur im Dokument; **Vorschlag**: `page_logs`-Eintrag (`entity_name='issue'`) durch Erweiterung des `COMPONENT_MAP` (R29) für Backlinks.

**UI-Hinweise**: Kartenlayout nicht im CE → Referenz-Screenshot nötig (OP-01). Slash-Suche nach Work Items über CE-Suchendpunkt (`TSearchEntities` `issue`, R30).

**Konfidenz**: hoch (Vertrag), niedrig (Kartenlayout).

---

### 3.12 P07-12 – Work-Item-Mentions & „Create work item from selection“

**Funktionsbeschreibung**
- `@`-Mention eines Work Items erzeugt einen klickbaren interaktiven Link (Doku-Label Business) (W5).
- Text markieren → Kontextmenü „Create work item from selection“ → neues Work Item im Projekt mit markiertem Text als Titel; Text wird durch Mention ersetzt; Aktion endgültig (W5, W37).

**CE-Stand (Stub)**: Mention-UI nur `user_mention` (`useAdditionalEditorMention` → `editorMentionTypes = ["user_mention"]`, `updateAdditionalSections` → `{ sections: [] }`, `parseAdditionalEditorContent` → `undefined`; `EditorMentionsRoot` (`apps/web/components/editor/embeds/mentions/root.tsx`) rendert nur `user_mention`, alles andere `null`, R30); Suchendpunkt kennt `issue`, `project`, `cycle`, `module`, `page` (R30); `PageLog`-Typ `issue`, `page_mention` (R12). **Verifikations-Ergänzung**: Der Hook-Parameter `enableAdvancedMentions` wird nur im Document-Editor (Pages: `editor-body.tsx`; `components/editor/document/editor.tsx`) und im Export-Parser auf `true` gesetzt, Lite-/Rich-Text-Editoren (Kommentare, Beschreibungen) verwenden den Default `false` (R38) → erweiterte Mentions sind ein Pages-spezifisches EE-Merkmal (welche Entitätstypen außer Work Items, UNVERIFIZIERT; siehe P07-47).

**HTML-Vertrag**: `<mention-component id="…" entity_identifier="…" entity_name="user_mention">` (G1); für Work Items analoger `entity_name` (UNVERIFIZIERT, z. B. `issue_mention`).

**Konfidenz**: mittel.

---

### 3.13 P07-13 – Link Pages ↔ Work Items

**Funktionsbeschreibung**
- Abschnitt **„Pages“** in den Work-Item-Details; Button **„Link pages“** sucht in Projektseiten und Wiki, Mehrfachauswahl (W38). Matrix: „Link pages in work items in a separate section in work item details.“ (R1).
- i18n (R7): `issue.pages.link_pages` „Link pages“, `show_wiki_pages` „Show Wiki pages“ (Umschalter im Auswahl-Modal, UNVERIFIZIERT), `link_pages_to` „Link pages to“, `linked_pages` „Linked pages“, `no_description` („This is an empty page. Why don't you write something inside and see it show up here like this placeholder“ = Vorschau-Platzhalter für leere Seiten), Toasts `link.success` „Pages updated“, `remove.success` „Page removed“ und Fehlervarianten.
- Teamspace-Seiten nicht verlinkbar (W5 Tabelle „Link to a work item“: Projekt ✓, Wiki ✓, Teamspace –).
- **Tier (Verifikation)**: Pro (Changelog W38); Matrix „One+“ historisch (R36). v1-Request-Body: `page_id` (Pflicht) (D2 `add-work-item-page.md`).

**Datenmodell** (D2, W39): Link-Objekt `id`, `page {id, name, description_html, created_at, updated_at, created_by, is_global, logo_props}`, `issue`, `project`, `workspace`, `created_at`, `updated_at`, `created_by`. Jede Seite höchstens einmal je Work Item (sonst `409 conflict`); beliebige Seite des Workspace verlinkbar (eigenes Projekt, anderes Projekt, Wiki) (W39). **Vorschlag**: `work_item_pages(id, issue_id, page_id, project_id, workspace_id, …)`, partieller Unique-Index (`issue_id`, `page_id`) `WHERE deleted_at IS NULL`.

**API**: v1 `GET/POST …/projects/{pid}/work-items/{wid}/pages/`, `GET/DELETE …/pages/{page_id}/` (D2; Löschen per Link-ID laut MCP, D5); v2 `POST /api/v2/workspaces/{slug}/projects/{project_id}/work-items/{work_item_id}/pages/` (W39). Details siehe Dokument 21 §4.9.

**Konfidenz**: hoch.

---

### 3.14 P07-14 – Inline-Kommentare

**Funktionsbeschreibung**
- Text markieren → Kommentar-Thread am Text; in Projekt-, Wiki- und Teamspace-Seiten (W7). Seit 2025-10-15 (W9).
- Antworten im **Comments-Panel rechts** unter dem Kommentar (W7) = Navigation-Pane-Tab „Comments“ (R4 `page_navigation_pane.tabs.comments.label`, Leerzustand „No comments“ / „Add comments to see them here.“).
- Mentions in Kommentaren, Resolve per Häkchen › „Mark as resolved“; aufgelöste Threads verschwinden aus der Standardansicht; „Mark as unresolved“ öffnet erneut; Filter „Show active“ (Default), „Show resolved“, „Show all“ (W7, W8).
- Nur Autor darf eigenen Kommentar bearbeiten/löschen (W7); Teamspace-Lead darf jeden Kommentar löschen (W29, W30); Guests dürfen Projekt-Kommentare reagieren, nicht resolven (W29); Guest kommentiert nur eigene Seiten (W29).
- Reaktionen auf Seitenkommentare: nicht seitenspezifisch belegt (UNVERIFIZIERT; Work-Item-Kommentare haben Reaktionen).
- Teamspace-Kommentare bleiben im Teamspace sichtbar (W30).

**Datenmodell (Vorschlag)**: `page_comments(id, workspace_id, page_id, actor_id, parent_id (Thread), comment_type 'inline'|'page', anchor_id (ID der Kommentar-Markierung im Dokument), reference_text (Snapshot des markierten Texts), comment_html, comment_json, comment_stripped, is_resolved, resolved_by_id, resolved_at, edited_at, is_hidden, hidden_reason, hidden_by_id, hidden_at, created_at, updated_at, deleted_at)`; `page_comment_reactions(comment_id, actor_id, reaction)`. Anker als Tiptap-Mark mit Kommentar-ID im Yjs-Dokument (UNVERIFIZIERT – clean-room-Entwurf).

**Konfidenz**: hoch (Verhalten), niedrig (Persistenz-Interna).

---

### 3.15 P07-15 – Page-Level-Kommentare, Filter, Moderation

**Funktionsbeschreibung**
- 2026-10-15: Kommentare zur ganzen Seite ohne Textauswahl; Umschalter **„Page“ / „Inline“**; Filter nach Status (active/resolved/beide) **und Autor**; „Copy link“ eines Kommentars öffnet beim Empfänger den Thread (W8).
- v3.2.0: Admins können Kommentare auf Work Items, Pages und Teamspaces **verbergen/einblenden** mit Begründung (W32).
- Upsell-Tabs in `wiki.upgrade_flow.tabs`: „Nested Pages“, „Add embeds“, „Publish pages“, „Comments“ (R3) – bestätigt Kommentare als Bezahl-Merkmal.

**Datenmodell**: siehe P07-14 (`comment_type='page'`, `anchor_id=null`, `is_hidden`…).

**Konfidenz**: mittel.

---

### 3.16 P07-16 – Page-Sharing / Access-Control

**Funktionsbeschreibung**
- Private Wiki-Seiten sind standardmäßig nur für den Ersteller sichtbar; ab Business gezielt mit Workspace-Mitgliedern teilen über **„Share“** mit Stufen **„Can view“**, **„Can comment“**, **„Can edit“**; Stufen änderbar, Zugriff entziehbar; geteilte Seiten erscheinen beim Empfänger unter „Shared“ (W1, W5).
- Teilen nur für Wiki-Seiten (Projekt- und Teamspace-Seiten –) (W5); Teilen nur der eigenen Seite (Owner/Admin/Member jeweils „Own“), Gäste nicht (W29); Ersteller behält volle Kontrolle (W1).
- E-Mail-Benachrichtigung, wenn man zu einer geteilten Seite hinzugefügt wird (W13).
- i18n: „Members & Teamspaces“ (R9, vermutlich Abschnittsüberschrift im Share-/Move-Dialog, UNVERIFIZIERT); Move-Dialog-Regel „Private and shared pages cannot be moved to a teamspace.“ (R4).
- Listenfilter `type=shared` = „private pages explicitly shared with the user“; `private` = „pages owned by the user and not shared“ (D1).

**CE-Stand (Stub)**: `usePageFlag().isPageSharingEnabled = false` (R11); keine Share-UI, keine Tabelle.

**Datenmodell (Vorschlag)**: `page_members(id, page_id, member_id, access smallint 0 view|1 comment|2 edit, workspace_id, created_by, …)`, Werte analog Collection-Rollen (G7). Effektive Rechte = max(Workspace-Rolle-Regeln, Page-Owner, Page-Member-Access, Collection-Member-Access).

**API**: kein dokumentierter Share-Endpunkt (Suche ergebnislos); **Vorschlag** `GET/POST/PATCH/DELETE /api/workspaces/{slug}/pages/{id}/members/`.

**Konfidenz**: hoch (Verhalten), niedrig (API).

---

### 3.17 P07-17 – Teamspace-Pages

**Funktionsbeschreibung**
- Seiten im Tab „Pages“ eines Teamspace, nur für Teamspace-Mitglieder sichtbar, **immer öffentlich im Teamspace** (keine Private-Option); private/geteilte Seiten können nicht in einen Teamspace verschoben werden (W5, W30).
- Rechte: Member sehen, erstellen, bearbeiten, duplizieren, verschieben, exportieren, favorisieren; archivieren/löschen nur eigene; Lead archiviert/stellt wieder her/löscht jede Seite und jeden Kommentar (W30, W29).
- Nested Pages und Templates verfügbar; Publish und Work-Item-Links nicht (W5).

**CE-Stand**: Legacy-Modell `Team` (`apps/api/plane/db/models/workspace.py`, ohne Mitglieder/Seiten); Realtime-Typ `team_page` + `teamId` (R15). Teamspaces selbst: Dokument 21 §4.4.

**Datenmodell (Vorschlag)**: `pages.teamspace_id` (nullable FK) bzw. `scope='teamspace'`.

**Konfidenz**: mittel.

---

### 3.18 P07-18 – Page Labels

**Funktionsbeschreibung**
- Eigene Seiten-Labels, getrennt von Work-Item-Labels; Workspace-weit, für Projekt-, Wiki- und Teamspace-Seiten (W31; eingeführt 2026-07-31, W19).
- Label beim Taggen neu anlegen, sofern berechtigt (Default Owner/Admin); Verwaltung unter *Workspace settings › Wiki* (Abschnitt Page labels); Namen eindeutig je Workspace; Label löschen entfernt es von allen Seiten (W31).
- Filter in Seitenliste/Collection: mehrere Labels → Seiten mit **irgendeinem** gewählten Label (OR) (W31).
- Wer ändert Labels: Wiki – Owner der Seite und Workspace-Admins (Member nur eigene); Projekt/Teamspace – jeder mit Edit-Recht (W31, W29).

**CE-Stand (teilweise)**: `Page.labels` M2M über `PageLabel` auf **Work-Item-`Label`** (R12); Annotation `label_ids` (R25); Filter `labels` in `TPageFilterProps` (`packages/types/src/page/core.ts`).

**Datenmodell (Vorschlag)**: `page_label_definitions(id, workspace_id, name unique, color, sort_order)`, `page_label_assignments(page_id, label_id)`.

**Konfidenz**: hoch.

---

### 3.19 P07-19 – Moving Pages

**Funktionsbeschreibung**
- Icon **„Move page“** oben rechts → Ziel wählen (anderes Projekt, Teamspace, Wiki, konkrete Wiki-Collection) → Suche → bestätigen (W3).
- Voraussetzungen: Seite entsperrt und nicht archiviert; private/geteilte Seiten nicht in Teamspace (erst öffentlich machen); kann die Seite nicht in die gewählte Collection, landet sie im Wiki in „General“; Unterseiten wandern mit (W3).
- Rechte: Projekt-Admin jede Projektseite, Contributor nur eigene; Wiki-Member nur eigene; Teamspace-Member und -Lead dürfen umhängen (W3, W29).
- i18n (R4 `page_actions.move_page`): Buttons „Move“/„Moving“; Platzhalter je Richtung: `workspace_to_all` „Search for projects and teamspaces“, `workspace_to_project` „Search for projects“, `project_to_all` „Search for projects and teamspaces“, `project_to_project` „Search for projects“, `project_to_all_with_wiki` „Search for wiki collections, projects, and teamspaces“, `project_to_project_with_wiki` „Search for wiki collections and projects“; Toasts Erfolg „Page moved successfully.“, Fehler „Page could not be moved. Please try again later.“, `collection_error` „Moved to wiki“ / „Page was moved to wiki, but could not be added to the selected collection. It remains in General.“; Regel `cannot_move_to_teamspace`.

**CE-Stand (Stub)**: Menüpunkt `move` (Icon `ExportOutline`, Titel „Move“) nur wenn `canCurrentUserMovePage && isMovePageEnabled`; `isMovePageEnabled=false` (R11, R32); **zusätzlich** ist `"move"` in keinem `optionsOrder` des CE enthalten (`options-dropdown.tsx`, `block-item-action.tsx`) und würde selbst mit Flag nicht angezeigt (Verifikation); Zustand `movePageModal` wird gesetzt, aber keine Modal-Komponente gerendert (R32); Felder `moved_to_page`, `moved_to_project` (R12) und das Realtime-Ereignis `move`/`moved` mit `MovedPayload { new_project_id, new_page_id }` (R37, im CE ohne Client-Handler) → ein Move erzeugt vermutlich eine **neue Seiten-ID** im Ziel und hinterlässt einen Verweis, über den offene Clients umgeleitet werden (UNVERIFIZIERT).

**API (Vorschlag)**: `POST …/pages/{id}/move/` Body `{ target_type: project|teamspace|wiki, target_id, collection_id? }`.

**Konfidenz**: hoch (UI-Texte, Regeln), niedrig (technischer Ablauf).

---

### 3.20 P07-20 – Databases + Formulas

**Funktionsbeschreibung**: Matrix: „Put databases and formulas into a page without worrying about losing text, images, or other content types.“ (R1, `comingSoon: true`, Business/Enterprise ✓); `planHighlights.enterprise` und `ENTERPRISE_PLAN_FEATURES` führen „Databases + Formulas“ (R1, R2). In Changelog/Doku (Stand 10/2026) **kein Nachweis einer Auslieferung** (Suche ergebnislos; Formel-Property existiert nur bei Work-Item-Properties, `packages/i18n/src/locales/en/work-item-type.json` `formula.*`).

**Tier (Verifikation)**: widersprüchlich innerhalb des Repos – Matrix-Zeile Business ✓/Enterprise ✓ (R1) vs. Enterprise-Karte des aktiv genutzten Upgrade-Modals (`ENTERPRISE_PLAN_FEATURES`, `apps/web/components/license/modal/upgrade-modal.tsx`) und `planHighlights.enterprise`. Regel „spezifischere Quelle gewinnt“ → Business+; damit ist das Merkmal **nicht** eindeutig Top-Lizenz-only (Kap. 1.1 korrigiert).

**Migrationshinweis**: Kein Originalverhalten spezifizierbar → nicht portierbar ohne Produktentscheidung (OP-03).

**Konfidenz**: niedrig.

---

### 3.21 P07-21 – Draw.io-Diagramme

**Funktionsbeschreibung**
- Workspace-Integration zuerst verbinden: *Workspace settings › Integrations › Draw.io › Configure*, Zugriff bestätigen; nur Workspace-Admins (W27).
- Zwei Blöcke (nur Pages): **„Draw.io diagram“** (voller Editor: Flowcharts, Architektur, Org-Charts; Shape-Bibliotheken, Templates, Mermaid-Import) und **„Draw.io board“** (einfacher Whiteboard-/Freihand-Editor); Einfügen per `/draw` bzw. `/draw.io` (W4, W27).
- Diagrammänderungen nicht in der Seiten-Versionshistorie (W27).
- Fix 2026-10-15 für Vorschau im Dark-Mode und nach Speichern (W8 via Suche „Draw.io integration“).
- Eingeführt v1.16.0 (W28).

**Infrastruktur** (H1, H3, H4, G13): optionaler In-Chart-Dienst `makeplane/drawio:v2.5.0` (Tomcat, Port 8080, Ingress `/drawio/`, Prefix wird entfernt); `DRAWIO_EMBED_URL` in API-Env: lokal `<scheme>://<licenseDomain>/drawio`, sonst `env.drawio_remote_url`, sonst leer → Frontend fällt auf diagrams.net-Cloud zurück; Editor lädt `<DRAWIO_EMBED_URL>/?embed=1…`, Viewer `<DRAWIO_EMBED_URL>/js/viewer-static.min.js`.

**CE-Stand**: nur Drag-Selektor `.editor-drawio-component` (R17).

**Tier (Verifikation)**: Pro nach der Integrationsdoku (W27) als spezifischerer Quelle; Blog W11 nennt Business (UNVERIFIZIERT, Such-Zusammenfassungen). Helm-Defaults (H1): `services.drawio.local_setup: false`, `services.iframely.enabled: false`, `services.live_exporter.enabled: true` (Image `makeplane/live-commercial`). Helm beschreibt draw.io als „Self-hosted draw.io for the Wiki editor's diagram extension“ (H1, H5) – Geltungsbereich siehe OP-20.

**Datenmodell (Vorschlag, clean-room)**: Node `drawio-component` mit Attributen `id`, `data-mode` (`diagram`|`board`), `data-xml-asset-id` (Diagramm-XML als `FileAsset`), `data-image-asset-id` (SVG/PNG-Vorschau); Speicherung über `FileAsset` (`entity_type=PAGE_DESCRIPTION`, R27). HTML-Vertrag des Originals nicht dokumentiert (UNVERIFIZIERT).

**Migrationshinweis (ADR-004)**: draw.io-Webapp (jgraph/drawio, Apache-2.0) als statische Dateien bündeln und unter `/drawio/` ausliefern; Fallback auf diagrams.net nur per expliziter Konfiguration; Kommunikation über `postMessage`-Embed-Protokoll (`?embed=1&proto=json`).

**Konfidenz**: hoch (Infrastruktur, Bedienung), niedrig (Persistenzformat).

---

### 3.22 P07-22 – Externe Embeds / Rich Cards (Iframely), Medien per URL

**Funktionsbeschreibung**
- Block **„Embed“** (Pro): `/embed`, Link einfügen → Embed für YouTube, Figma, Google Docs, Loom; nicht in Kommentaren (W4, W13).
- Blockmenü-Umschaltung: „Convert to Embed“, „Convert to Link“, „Convert to Rich Card“ (R5 `externalEmbedComponent.block_menu`); Zoom in/out (W13).
- Platzhalter „Insert your preferred embed link here, such as YouTube video, Figma design, etc.“ (Originaltext) und „Enter or paste a link“; Eingabe-Modal „Embed“ / „Works with YouTube, Figma, Google Docs and more“; Fehler „Please enter a valid URL.“ (R5).
- Bilder und Videos per URL einfügen, schwebendes Upload-Modal (W33).

**HTML-Vertrag** (G1): `<external-embed-component id="…" src="https://…" data-entity-name="Plane" data-entity-type="link" data-is-rich-card="false" data-has-tried-embedding="true" data-has-embed-failed="false"></external-embed-component>`.

**Infrastruktur** (H1, H2, H3, H4, W34): Iframely-Dienst (`makeplane/iframely:v2.5.4`, `node server.js`, Port 8061, nur cluster-intern, kein Ingress) über `IFRAMELY_URL` für API und Live; `IFRAMELY_REPLICAS` „for link previews and embeds“.

**CE-Stand (Stub)**: Befehlstyp `"external-embed"` (R16), Drag-Selektor `.editor-embed-component` (R17), i18n (R5); keine Extension.

**Migrationshinweis (ADR-002/ADR-004)**: Iframely ist Node → .NET-Unfurl-Dienst (oEmbed-Provider-Liste, OpenGraph/Twitter-Card-Parser, SSRF-Schutz, Cache-Tabelle `link_previews(url_hash, url, payload jsonb, fetched_at)`); im Airgapped-Betrieb nur interne Ziele, Embed-Fehler → Fallback Link (`data-has-embed-failed`).

**Konfidenz**: hoch (Vertrag, Texte), mittel (Rich-Card-Layout).

---

### 3.23 P07-23 – Attachments in Pages

**Funktionsbeschreibung**
- Block **„Attachment“** (Pro): Datei hochladen → Karte auf der Seite; die meisten Typen erlaubt, ausführbare/Skriptdateien (`.exe`, `.bat`, `.sh`, `.php`) blockiert; max. Größe planabhängig, Self-hosted über Instanzeinstellungen (W4). Cloud-Matrix: Max file size Free 5 MB, Pro 100 MB, Business 200 MB, Enterprise Custom (R1, `cloudOnly` Storage).
- Uploader-Text „Drop files here or click to upload“; Fehler „File too large.“ / „Maximum size per file is {maxFileSize}MB“, „Unsupported file type.“ / „See supported formats“, „Upload failed.“ / „Something went wrong. Please try again.“; Aria „Click to upload attachment“; Downgrade-Text „Upgrade your plan to view this attachment.“ (entfällt) (R5).
- Video-Anhang: ⋮⋮-Menü „Show preview“ (Player) ↔ „Show as attachment“ (W4).
- Word/Excel/PowerPoint-Anhänge in Pages in Microsoft Office bearbeitbar (W36, 2026-09-15; Mechanismus UNVERIFIZIERT → OP-12).
- Helm: `env.allow_all_attachment_types` (H1).

**HTML-Vertrag** (G1): `<attachment-component id="ASSET_ID" src="ASSET_ID" data-name="requirements.pdf" data-file-size="12345" data-file-type="application/pdf" status="uploaded"></attachment-component>`. Upload: Assets-Endpunkt mit `entity_type=PAGE_DESCRIPTION` → Bytes an zurückgegebene URL → Bestätigung `PATCH …/pages/{page_id}/attachments/{attachment_id}/` `{is_uploaded: true}` (204; Seite muss editierbar, nicht gesperrt/archiviert sein; startet Metadaten-Extraktion) → Komponente in vollem Body senden; Metadaten/Downloads folgen der Seitensichtbarkeit (G1, G6). Weitere Endpunkte (G14, wörtlich geprüft): `GET …/pages/{page_id}/attachments/{attachment_id}/` (Metadaten und Links, Leserecht auf Seite), `GET …/pages/{page_id}/attachments/{attachment_id}/download/`, `DELETE …/pages/{page_id}/attachments/{attachment_id}/` (Soft-Delete, 204; danach liefern Metadaten/Download `404`; gesperrte/archivierte Seiten nicht änderbar) (Branch `docs-page-update-api`).
- **Assets-Tab** (Verifikation): Im CE listet der Navigation-Pane-Tab „Assets“ nur Bilder (`TEditorAsset = TEditorImageAsset | TAdditionalEditorAsset`, `TAdditionalEditorAsset = never`, R40; Leerzustand „Missing images“ / „Add images to see them here.“, `page_navigation_pane.tabs.assets.*`, R4); Erweiterungspunkt für Anhänge im Assets-Tab der EE (UNVERIFIZIERT).

**CE-Stand (Stub)**: Befehlstyp `"attachment"` (R16); Drop-Plugin erkennt `ACCEPTED_ATTACHMENT_MIME_TYPES` (Bilder, PDF, Office, Text/Markdown/RTF, Audio, Video, Archive, glTF, `application/octet-stream`, Fonts, CSS/JS/JSON/XML/CSV), Zweig `fileType === "attachment"` ist **leer** (R18); `FileAsset.page` und `PAGE_DESCRIPTION` vorhanden (R27).

**Konfidenz**: hoch.

---

### 3.24 P07-24 – Video-Block

**Funktionsbeschreibung**: Block „Video“ (Pro) `/video`, Upload und Wiedergabe in der Seite; Formate MP4, MPEG, OGG, WebM, QuickTime, AVI, WMV; Umschalten auf Datei-Link „Show as attachment“ (W4; v2.1.0 „video attachments“, W37). `PageLog`-Typ `video` im CE vorhanden (R12).

**Datenmodell**: `FileAsset` (`PAGE_DESCRIPTION`); Node-HTML nicht dokumentiert (UNVERIFIZIERT).

**Konfidenz**: mittel.

---

### 3.25 P07-25 – Advanced Pages Analytics

**Funktionsbeschreibung**
- Seiten-„•••“ › **„Analytics“** öffnet Seitenpanel; Zeitraum 7, 30, 90 Tage oder gesamt; Kennzahlen Total views, Unique views (verschiedene Personen), Nested pages, Attachments; Diagramm „Views“ mit Total/Unique pro Tag, Hover zeigt Tageswerte; Tab **„Viewers“** listet Personen mit letztem Ansichtszeitpunkt, mit Suche (W6).
- Zählregeln: wiederholte Ansicht derselben Person innerhalb **einer Stunde** zählt einmal; **eigene Ansichten des Owners** werden ausgeschlossen; Analytics wird beim Löschen der Seite gelöscht (W6).
- Sichtbar für alle, die die Seite öffnen dürfen (W6).
- **Collection-Analytics**: Summen über Seiten der Collection; eine Person, die fünf Seiten liest, zählt als ein Unique Viewer (W6; 2026-08-31, W18).
- Matrix-Text: „See who's viewing, sharing, and commenting on your pages along with other useful info.“ (R1).

**Datenmodell (Vorschlag)**: `page_views(id, workspace_id, page_id, user_id, viewed_at)` mit Dedup-Regel (kein Insert, wenn letzter View desselben Users < 1 h); Owner-Views nicht speichern; Aggregation per SQL (`date_trunc('day')`, `count(*)`, `count(distinct user_id)`); Cascade-Delete mit Seite. CE-`UserRecentVisit` (`apps/api/plane/db/models/recent_visit.py`) ist kein Ersatz (nur letzter Besuch).

**Konfidenz**: hoch.

---

### 3.26 P07-26 – Stickies-Erweiterungen

**Befund**: Stickies sind vollständig im CE (Modell `Sticky` mit `name`, `description`, `description_html`, `description_stripped`, `description_binary`, `logo_props`, `color`, `background_color`, `workspace`, `owner`, `sort_order` (+10000 je neuem Sticky); Public-API v1 `stickies`; UI-Komponenten Widget, Modal, Suche, Drag-and-Drop, Farbpalette, Action-Bar) (R28, D6). Die Plan-Matrix hat keine Stickies-Zeile (R1). Online-Quellen nennen kein Bezahl-Gate; Änderungen: Floater unten links (2026-09-15, W36), v2-API „private notes owned by the calling user“ (W35), OAuth-Scope `stickies` (`packages/i18n/src/locales/en/workspace-settings.json` `applications.scope_description.stickies`). `StickyActionBar` ist im CE definiert, aber nirgends eingebunden (`apps/web/components/stickies/action-bar.tsx`).

**Migrationshinweis**: Kein Bezahl-Feature nachweisbar; Stickies gehören in den CE-Feature-Cluster. Floater-Position laut aktuellem Original UNVERIFIZIERT.

**Konfidenz**: mittel (Abwesenheit eines Gates ist nur negativ belegt).

---

### 3.27 P07-27 – Plane AI im Editor: Selection-Aktionen

**Funktionsbeschreibung**: Für markierten Text feste Aktionen **Paraphrase, Simplify, Elaborate, Summarize, Get title**; „Replace selection“ ersetzt den Text; Ton-Einstellung vor Neugenerierung (W22). Übersetzen nicht im Selection-Menü belegt (W22).

**CE-Stand (Stub)**: `EditorAIMenu` (`apps/web/components/pages/editor/ai/menu.tsx`, eingebunden in `editor-body.tsx`) mit einziger Aufgabe `AI_EDITOR_TASKS.ASK_ANYTHING` „Ask Pi“; Töne (definiert in `menu.tsx`, nicht in den Konstanten) `default` (casual 5/formal 5), `professional` „💼 Professional“ (casual 0/formal 10), `casual` „😃 Casual“ (10/0); Antwort mit „Replace selection“, „Add to next line“, „Re-generate response“ (`menu.tsx`, `ask-pi-menu.tsx`); Ladetext „Pi is generating response“ (`packages/constants/src/ai.ts`). Service `POST /api/workspaces/{slug}/rephrase-grammar/` – Route existiert im CE-API nicht (nur `ai-assistant/`, `apps/api/plane/app/urls/external.py`). AI-Handle (Sparkles-Icon im Side-Menü, `packages/editor/src/plugins/ai-handle.ts`) nur aktiv, wenn `"ai"` nicht deaktiviert ist – CE deaktiviert es (R10).

**Migrationshinweis (ADR-004)**: OpenAI-kompatibler, lokal betreibbarer Provider; AI-Credits entfallen (ADR-001). Workspace-Feature `pi` (D3) als fachlicher Schalter.

**Konfidenz**: mittel.

---

### 3.28 P07-28 – Plane AI: AI-Block

**Funktionsbeschreibung**: Block, den Plane AI füllt; `/ai` (Doku) bzw. `/ai-block` (Changelog) einfügen; Typen **„Summarize Page“** und **„Custom Prompt“**; danach Regenerate, Refine, Rewrite, Keep („Use this“), Discard; nur Pages; verbraucht AI-Credits (W4, W21). Zusammenfassung mit Stale-Indikator, wenn sich die Seite nach Erzeugung ändert (W21). i18n (R5 `ai_block`): Platzhalter „Describe the content of this block“, „Your AI content will be generated here“, „Select block type“, Aktionen „Discard“, „Generate“, „Generating“, „Rewriting“, „Rewrite“, „Use this“, „Refine“.

**Datenmodell (Vorschlag)**: Node `ai-block-component` mit `block_type` (`summarize_page`|`custom_prompt`), `prompt`, `generated_html`, `generated_at`, `source_hash` (für Stale-Erkennung). Original-Vertrag UNVERIFIZIERT.

**Tier (Verifikation)**: Business nach Doku-Label (W4, W22) als spezifischerer/aktuellerer Quelle; der Blog W10 (Collections-Launch, April 2026) nennt Pro+, ist aber älter als der Launch des AI-Blocks (2026-06-15, W21). Beide Angaben stammen aus Such-Zusammenfassungen (UNVERIFIZIERT).

**Konfidenz**: mittel.

---

### 3.29 P07-29 – Plane AI: Prompt/Agent in Pages mit Proposals

**Funktionsbeschreibung**: KI schlägt Änderungen an mehreren Abschnitten gleichzeitig vor; Autor entscheidet blockweise über Annahme/Ablehnung; abgelehnte Vorschläge lassen Originaltext unverändert (W22, W10). Ältere Beschreibung: Agent im Seiten-Sidecar, wirkt auf einen gewählten Block (W10); aktuelle Doku: Prompt-Eingabe oben auf der Seite (W22).

**Migrationshinweis**: Vorschlag-Darstellung als Tiptap-Dekorationen/Suggestion-Marks; Ausführung über Plane-AI-Backend (anderer Cluster).

**Tier (Verifikation)**: Business (Doku W22) statt Pro (Blog W10); Regel „spezifischere/aktuellere Quelle gewinnt“, UNVERIFIZIERT.

**Konfidenz**: niedrig–mittel (Doku widersprüchlich).

---

### 3.30 P07-30 bis P07-43 – Erweiterte Editor-Blöcke

Gruppen des `/`-Menüs laut Doku: **Basics** (Text, Headings 1–6, Quote, Callout, Toggle), **Layout** (Table, Table of contents), **Media** (Image, Attachment, Video, Embed), **Advanced** (Mermaid, HTML artifact, Equations, Draw.io, AI block) (W4). Übersichtsseite nennt „16 different content blocks“ (W5; Tour-Text im CE `product_tour.page.step_two`: „Use / on a page to add content from 16 block types“, `packages/i18n/src/locales/en/tour.json`).

| ID | Block | Befehl(e) | Verhalten | Tier | HTML-Vertrag | Quelle |
|---|---|---|---|---|---|---|
| P07-30 | Columns | `/2 columns`, `/3 columns`, `/4 columns` (Bezeichnungen „2 Columns“, „3 Columns“, „4 Columns“) | nebeneinander, jede Spalte nimmt beliebige Blöcke | Pro | UNVERIFIZIERT | W4, W44 |
| P07-31 | Tabs | Horizontal tabs / Vertical tabs | Block mit mehreren Tabs, startet mit zwei Tabs; in Read-only/Published umschaltbar, nicht änderbar | Business | UNVERIFIZIERT | W4, W18 |
| P07-32 | Toggle | `/toggle` (+ Aliase) | aufklappbarer Block für Detailinhalte | Business | UNVERIFIZIERT | W4, W17 |
| P07-33 | Status | `/status`, `/label`, `/badge`, `/tag` | farbiges Label „STATUS“ (grau), Text änderbar, sechs Farben (vollständige Liste UNVERIFIZIERT), read-only nicht änderbar | Pro | UNVERIFIZIERT | W4 |
| P07-34 | Date (inline) | `/date`, `/calendar`, `/deadline`, `/due` | Pill, Klick öffnet Kalender, read-only als Text | Pro | `<inline-date-component id="…" date="2026-08-18"></inline-date-component>` | W4, G1 |
| P07-35 | Equation block / inline | `/`-Menü, `$$…$$` (Block), `$…$` (inline) | LaTeX, Block zentriert, Fehleranzeige bei nicht renderbarem LaTeX | Business | `<block-math-component id="…" latex="…">`, `<inline-math-component id="…" latex="…">` | W4, G1, W40 |
| P07-36 | Mermaid diagram | `/mermaid` | Flowcharts, Sequenz, Graphen; Umschalter Preview/Code; Mermaid-Code einfügen rendert | unklar | UNVERIFIZIERT | W4, W20, W15 |
| P07-37 | HTML artifact | `/`-Menü (Advanced) | hochgeladene `.html`/`.htm` live und interaktiv (Skripte laufen), isolierter Frame ohne Zugriff auf Session/Workspace/Seite; Block löschen löscht Datei, außer anderweitig auf derselben Seite verwendet | Business | UNVERIFIZIERT | W4, W19 |
| P07-38 | Table of contents | `/`-Menü (Layout) | Inhaltsverzeichnis aus Überschriften; nur Pages | unklar | UNVERIFIZIERT | W4 |
| P07-39 | Link pages | `/link pages` | Live-Liste von Wiki-Seiten; Quelle „Parent pages“ (Kinder einer gewählten Seite), Tiefe „All“ oder 1–6; aktualisiert bei Anlegen/Umbenennen/Archivieren/Löschen; archivierte nicht gelistet; nur Wiki-Seiten; 2026-08-31 auch Elternseite einfügbar | Business | UNVERIFIZIERT | W4, W5, W18 |
| P07-40 | Page embed / Linked page embed | `/page` (neue Unterseite + Link-Block); „Linked page embed“ referenziert bestehende Seite | Unterseiten-Link bzw. Referenz auf andere Seite | Business (UNVERIFIZIERT) | `<page-embed-component id="…" entity_identifier="PAGE_UUID" workspace_identifier="WORKSPACE_SLUG" entity_name="sub_page"></page-embed-component>` | G1, W2, W4, W15 |
| P07-41 | Widget | `/`-Menü | Chart direkt aus Work-Item-Daten (Projekt- und Wiki-Seiten) | unklar | UNVERIFIZIERT | W4 |
| P07-42 | Link dashboard widgets | `/`-Menü | bettet ein Widget (Chart, Tabelle, Zahl) eines bestehenden Dashboards ein, synchron mit Daten; mindestens ein Dashboard mit Widgets erforderlich | Enterprise (Grid) | UNVERIFIZIERT | W4, W19 |
| P07-43 | Block-Links | Kontextmenü eines Blocks | Link auf einen Block kopieren | unklar | UNVERIFIZIERT | W37 |

Weitere im CE bereits vorhandene Komponenten (Referenz, keine Bezahl-Features): Callout `<div data-block-type="callout-component" data-background="#eff6ff" data-logo-in-use="emoji" data-emoji-unicode="128161">…</div>`, Bild `<image-component id src width height alignment status>` (G1; CE-Extensions `packages/editor/src/extensions/callout`, `custom-image`).

**Migrationshinweis**: Alle Renderer (KaTeX, Mermaid, draw.io-Viewer) gebündelt ausliefern (ADR-004); HTML-Artifact in `<iframe sandbox="allow-scripts">` ohne `allow-same-origin`, ausgeliefert von separater Asset-Origin mit restriktiver CSP; PDF/DOCX-Exporter (P07-09) müssen jeden Node-Typ abbilden (CE-PDF-Renderer `nodeRenderers` kennt genau: `doc`, `text`, `paragraph`, `heading`, `blockquote`, `codeBlock`, `bulletList`, `orderedList`, `listItem`, `taskList`, `taskItem`, `table`, `tableRow`, `tableHeader`, `tableCell`, `horizontalRule`, `hardBreak`, `image`, `imageComponent`, `calloutComponent`, `mention` – `apps/live/src/lib/pdf/node-renderers.tsx`; Marks in `apps/live/src/lib/pdf/mark-renderers.ts`). Für Nodes ohne Originalvertrag definiert der Implementierungs-Agent einen eigenen, dokumentierten HTML-Vertrag im Stil von G1 (Custom-Element `<name>-component` + `data-*`-Attribute).

**Konfidenz**: hoch (Existenz, Tiers laut Doku-Labels), niedrig (HTML-Verträge der mit UNVERIFIZIERT markierten Blöcke).

---

### 3.31 P07-44 – Page-Benachrichtigungen

**Funktionsbeschreibung**: E-Mail, wenn man zu einer geteilten Seite hinzugefügt wird (W13); Page-Subscriber erhalten E-Mail bei Veröffentlichung einer neuen Version oder Erwähnung (v3.2.0, W32). Subscribe-Mechanik für Seiten nicht dokumentiert (Suche nur Work Items).

**Datenmodell (Vorschlag)**: `page_subscribers(page_id, subscriber_id)`; Benachrichtigungen über bestehendes Notification-Subsystem (anderer Cluster).

**Konfidenz**: niedrig.

---

### 3.32 P07-45 – Pages-Public-API

Vollständiges Inventar der dokumentierten Ressourcen (Details der v1-Basis in Dokument 21 §2.14):

| Ressource | Endpunkte | Quelle |
|---|---|---|
| Projektseiten v1 | `GET/POST …/projects/{pid}/pages/`, `GET/PUT/DELETE …/pages/{id}/`, `POST …/archive/`, Restore | D1, Branch `docs-page-update-api` (`archive-project-page.md`, `restore-project-page.md`, `update-project-page.md`, `delete-project-page.md`) |
| Workspace-/Wiki-Seiten v1 | `GET/POST /api/v1/workspaces/{slug}/pages/`, `GET/PUT/DELETE …/{id}/`, `POST …/{id}/archive/`, Restore, Attachments (`get`, `download`, `delete`, `confirm`) | D1, G3–G6 |
| Seiten v2 | `…/api/v2/workspaces/{slug}/pages/` (+ `{pk}`), Projektseiten v2 | G12, W-Suche |
| Collections v1/v2 | siehe 3.2/3.3 | G7–G11 |
| Page-Templates v2 | `/api/v2/workspaces/{slug}/page-templates/` | W24 |
| Published Pages v2 | `GET /api/v2/workspaces/{slug}/published-pages/{anchor}/` | W25 |
| Work-Item-Pages v1/v2 | siehe 3.13 | D2, W39 |
| MCP | `page` list/retrieve/create/list_workitem_pages/attach_to_workitem/detach_from_workitem | D5 |

Regeln: `402 payment_required` („The feature this endpoint belongs to isn't enabled on your plan or is switched off.“) steht als Standardzeile in 388 von 454 v2-Dokumenten (auch `states/*`, `stickies/*`) und ist daher **kein** Tier-Beleg; nach ADR-001 tritt 402 nur noch bei abgeschaltetem Feature-Flag auf (Vorschlag: stattdessen `403`/`404` gemäß Ziel-Fehlervertrag, Entscheidung bei Dokument 21). Body-Updates werden auf das kollaborative Dokument angewendet (G2); `PUT` ersetzt den gesamten Body (G3); 502 „collaborative document service could not complete the update“, 503 „not configured“ (G3); max. Payload 10 MB, HTML wird sanitisiert (G1); gesperrte/archivierte Seiten nicht aktualisierbar (G3); Löschen nur archivierter Seiten (G5). **Migrationshinweis (ADR-002)**: .NET-API muss HTML → ProseMirror-JSON → Yjs-Update serverseitig konvertieren und auf das Live-Dokument anwenden (CE besitzt dafür `POST {live}/convert-document/` in `apps/live/src/controllers/document.controller.ts` mit `TConvertDocumentRequestBody {description_html, variant: "rich" | "document"}`, `apps/live/src/types/index.ts`).

**Konfidenz**: hoch.

---

### 3.33 P07-46 – Upgrade-/Downgrade-Flows (entfällt)

Im CE vorhandene Upsell-/Downgrade-Texte, die nach ADR-001 **nicht** portiert werden: `wiki.upgrade_flow.*` („Upgrade to unlock Wiki“, Beschreibung „Unlock public pages, version history, shared pages, real-time collaboration, and workspace pages … with Plane Pro.“, Buttons „Upgrade“, „Learn more“, „Download data“/„Downloading“, Tabs „Nested Pages“, „Add embeds“, „Publish pages“, „Comments“), `wiki.nested_pages_download_banner.title`, `attachmentComponent.upgrade.description` (R3, R5); Matrix-/Plan-Komponenten (R1, R2). Die Upsell-Beschreibung bestätigt als Bezahl-Merkmale: öffentliche Seiten, Versionshistorie, geteilte Seiten, Realtime-Kollaboration, Workspace-Seiten (R3).

---

### 3.34 P07-47 – Erweiterte Mentions im Document-Editor und Backlinks (Verifikations-Ergänzung)

**Befund (nur CE-Spuren, keine Online-Quelle geprüft)**
- Der Document-Editor der Pages ruft `useEditorMention({ enableAdvancedMentions: true, … })` auf (`apps/web/components/pages/editor/editor-body.tsx`, `apps/web/components/editor/document/editor.tsx`), ebenso der Export-Parser (`apps/web/hooks/use-parse-editor-content.ts`); andere Editoren nutzen den Default `false` (`apps/web/hooks/editor/use-editor-mention.tsx`) (R38).
- Im CE ist der Schalter wirkungslos: `useAdditionalEditorMention` liefert `sections: []`, `parseAdditionalEditorContent` → `undefined`, `editorMentionTypes = ["user_mention"]` (`apps/web/hooks/use-additional-editor-mention.tsx`); `EditorMentionsRoot` rendert nur `user_mention` (R30).
- Der Suchendpunkt (`TSearchEntities`, `packages/types/src/search.ts`) kennt `issue`, `project`, `cycle`, `module`, `page`; `TSearchEntityRequestPayload` hat zusätzlich `team_id` und `issue_id` (R30).
- `PageLog.TYPE_CHOICES` enthält `page_mention`, `back_link`, `forward_link`, `cycle`, `module` (R12); `page_transaction_task.COMPONENT_MAP` verarbeitet nur `mention-component` und `image-component`, über `component_map` erweiterbar (R29) → Backlinks/Forward-Links zwischen Seiten sind im Datenmodell vorbereitet, im CE ohne Logik.

**Funktionsbeschreibung (abgeleitet, UNVERIFIZIERT)**: Im Pages-Editor können per `@` neben Benutzern weitere Entitäten (mindestens Work Items, siehe P07-12; vermutlich Seiten, Projekte, Zyklen, Module) erwähnt werden; erwähnte Seiten erhalten Backlinks (`back_link`/`forward_link`-Einträge in `page_logs`).

**HTML-Vertrag**: `mention-component` mit `entity_name` je Typ; nur `user_mention` belegt (G1), weitere Werte UNVERIFIZIERT.

**Tier**: unklar (keine Plan-Angabe gefunden; Web-Recherche in der Verifikation nicht möglich).

**Konfidenz**: niedrig.

---

## 4. Offene Punkte / Unklarheiten

| ID | Thema | Beschreibung | Vorschlag / Rückfrage |
|---|---|---|---|
| OP-01 | UI-Referenz für EE-only-Oberflächen | Für Wiki-Sidebar, Collections-Tabelle, Share-Dialog, Move-Dialog, Kommentar-Panel, Analytics-Panel, Export-Dialog (EE), Template-Picker und alle Blöcke aus 3.30 gibt es **keinen** CE-Code und keine Referenz-Screenshots im Repo; ADR-005 verlangt 1:1. | **Rückfrage an Auftraggeber**: Steht eine Commercial-/Cloud-Instanz (Trial) für Referenz-Screenshots und Verhaltensaufnahmen zur Verfügung? Sonst Design aus Doku-Screenshots + CE-Designsystem ableiten und als Abweichung dokumentieren. |
| OP-02 | Widersprüchliche Tiers | Wiki One (R1) vs. Pro (R2, W1); Real-time/Publish/Work-Item-Embeds/Link One (R1) vs. Pro (R3, W4, W5, W38); Draw.io Pro (W27) vs. Business (W11); AI-Block/Agent Pro (W10) vs. Business (W21, W22); Versionen 2 Tage/3 Monate (R1) vs. 20 Versionen/30 Tage, 60/90 (W12). **Aufgelöst in der Verifikation**: „One“ ist nicht mehr erhältlich (R36) → Pro für alle „One+“-Zeilen; Draw.io Pro (Integrationsdoku spezifischer als Blog); AI-Block/Agent Business (Doku spezifischer/aktueller als Blog). | Nach ADR-001 ohne Auswirkung; nur Dokumentation. |
| OP-03 | Databases + Formulas | Nur als „COMING SOON“ in R1, im Upgrade-Modal (R2, R36) als Enterprise-Merkmal; kein Auslieferungsnachweis; Tier Business (Matrix-Zeile) vs. Enterprise (Highlights/Upgrade-Modal). | **Rückfrage**: Soll ein eigenes Feature (Notion-artige Datenbanken in Pages) entworfen werden oder entfällt es mangels Original? |
| OP-04 | Matrix-Fehler | `Nested Pages` hat bei Business/Enterprise den Zellwert „Word-compatible + other format downloads“ (Copy-Paste aus Exports) (R1). | Ignorieren; Nested Pages = vollständiges Feature. |
| OP-05 | Collection löschen | UI: „Transfer pages and delete collection“ / „Delete collection with pages“ (R3) vs. API v1: `archive_pages` true/false (G9). | Ziel unterstützt alle drei Varianten (Transfer, Archivieren, endgültig Löschen); Abgleich gegen Original nötig. |
| OP-06 | Persistenzformat neuer Nodes | HTML-Verträge nur für Mention, Work-Item-Embed, Page-Embed, Image, Callout, External-Embed, Math, Date, Attachment belegt (G1). Draw.io, Mermaid, Toggle, Tabs, Columns, Status, HTML-Artifact, Widget, Dashboard-Widget, AI-Block, Video, TOC, Link-pages unbekannt. | Eigene Verträge definieren (clean-room), zentral in einem Editor-Schema-Dokument festhalten. |
| OP-07 | Platzierung neuer Wiki-Seiten | Doku widersprüchlich: aktuelle Collection vs. immer „General“ (W1). | In Original prüfen (OP-01). |
| OP-08 | CE-Bug Versionierung | `track_page_version` greift auf nicht existentes `page.description` zu (R13, R12) – statisch verifiziert (kein Attribut in `Page`, `BaseModel`, Mixins), nicht ausgeführt. | Ziel implementiert Versionierung korrekt; Test gegen CE-Verhalten nicht als Referenz verwenden. |
| OP-09 | Kommentare auf publizierten Seiten | „without signing into your workspace“ (R1) / „without a workspace account“ (W5): unklar, ob anonym oder mit Space-Login. | In Original prüfen; Vorschlag: Space-Login wie bei Projekt-Publish. |
| OP-10 | Report-Funktion | Cloud-spezifisch (Support-E-Mail, Sperrung durch Plane) (W26). | Für Self-hosted: Melde-Adresse in God-Mode konfigurierbar oder ausblenden – Entscheidung Auftraggeber. |
| OP-11 | Export-Queue-Technik | Original nutzt RabbitMQ + Redis (H1, H5). ADR-000 nennt nur PostgreSQL. | Architektur-Entscheidung: PostgreSQL-Job-Tabelle (`SKIP LOCKED`) vs. Aspire-RabbitMQ. |
| OP-12 | „MS Office edits“ | Bearbeitung von Office-Anhängen „in Microsoft Office“ (W36): Mechanismus (WOPI, Microsoft-365-Integration, lokales Öffnen) unbekannt; externe Abhängigkeit (ADR-004). | **Rückfrage**: Erforderlich? Falls ja, optionale Integration (z. B. WOPI-Host für eine selbst gehostete Office-Suite). |
| OP-13 | Server-Restore von Versionen | Web ruft `…/versions/{id}/restore/`, CE-API fehlt die Route (R33, R35). | Ziel bietet Server-Endpunkt mit Yjs-Anwendung. |
| OP-14 | Share-/Move-/Comment-/Analytics-Endpunkte der internen App-API | Nicht dokumentiert. | Endpunkte nach CE-Muster entwerfen (Vorschläge in 3.x), Contract-Tests nur für dokumentierte Public-API. |
| OP-15 | Teamspace-Pages-Tier | Nur indirekt über „Teamspaces“ Pro (R2) belegt. | Ohne Auswirkung (ADR-001). |
| OP-16 | Mermaid/TOC/Widget/Block-Links-Tiers | Nicht belegt. | Ohne Auswirkung (ADR-001). |
| OP-17 | Draw.io-Fallback | Original fällt bei leerem `DRAWIO_EMBED_URL` auf diagrams.net-Cloud zurück (G13) – widerspricht Airgapped-Ziel. | Ziel: gebündelte draw.io-Webapp als Default; Cloud-Fallback nur per Konfiguration. |
| OP-18 | Iframely-Ersatz | Iframely ist Node (H4) – ADR-002 verbietet Node zur Laufzeit; Provider-Abdeckung des Originals unbekannt. | .NET-Unfurl-Dienst (3.22); Abdeckung YouTube, Figma, Google Docs, Loom als Mindestumfang (W4, W13). |
| OP-19 | Restore bei archiviertem Parent | CE löst den Parent (`page.parent = None`, R25), EE-Public-API v1 antwortet `400` (G14). | Ziel: Public-API `400` gemäß Doku; UI-Verhalten im Original prüfen (OP-01). |
| OP-20 | Draw.io-Geltungsbereich | Helm-Chart beschreibt draw.io als „diagram extension“ des „Wiki editor“ (H1 `values.yaml`, H5 README, G13); Doku nennt Blöcke für Pages allgemein (W4, W27). | Ziel: in allen Seitentypen anbieten (ADR-001); Abgleich mit Original (OP-01). |
