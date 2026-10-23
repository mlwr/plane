# 27 – Bezahl-Features Cluster P08 „Sicherheit, Administration, Lizenz“ – IST-Analyse

> **Phase:** IST-Analyse (keine Implementierung). **Stand der Recherche:** 2026-10-21; **Verifikationslauf:** 2026-10-22 (Korrekturen im Text mit „Verifikation“ markiert, Protokoll am Dokumentende).
> **Basis-Repo:** `/home/user/plane` = Plane Community Edition v1.4.2 (AGPL-3.0). Alle Repo-Pfade sind relativ zum Repo-Root.
> **Bindend:** `migration/architecture/00-grundsatzentscheidungen.md` (ADR-000 … ADR-006). Für diesen Cluster besonders relevant: **ADR-001** (eine Edition, alle Features immer aktiv, kein Lizenzschlüssel, keine Seats, kein Billing, keine Upgrade-CTAs), **ADR-004** (Self-hosted inkl. Airgapped, keine Pflicht-SaaS), **ADR-005** (UI 1:1, Upsell-Elemente entfallen), **ADR-003** (Greenfield, Semantik bleibt).
> **Schwester-Dokumente (nicht duplizieren, nur verweisen):** `migration/features/20-paid-spuren-im-repo.md` (P01: Repo-Spuren, PF-54…PF-59, PF-93…PF-103), `migration/features/21-paid-api-referenz-developer-docs.md` (P02: IdP-Group-Sync-API §2.6/§4.8, Rollen-Slugs F26, Member-Remove F23), `migration/features/22-paid-architektur-selfhosting-dienste.md` (P03: Dienste, Monitor/Prime, SSO/LDAP-Architektur – in Arbeit), `migration/features/25-paid-workflows-automation-templates.md` (P06: Approval-Flows F03/F08, Workspace-Governance F07), `migration/features/26-paid-wissen-pages-wiki.md` (P07: Page-Berechtigungen), `migration/analysis/03-api-intern-workspace-projekt-user.md` (CE-Rollen/Permissions §2.4, Mitglieder-Endpunkte W-09…W-21), `migration/analysis/11-frontend-admin-space.md` (CE-God-Mode), `migration/analysis/01-gesamtarchitektur-infrastruktur.md` (Instanz-Registrierung, Telemetrie, `SKIP_ENV_VAR`).

---

## Inhaltsverzeichnis

1. Überblick & Quellenlage
2. Plan-Matrix-Auszug (zeilengenau) für diesen Cluster
3. Feature-Tabelle (P08-01 … P08-31)
4. Feature-Abschnitte
   - 4.1 Authentifizierung & Identität: P08-01 SAML, P08-02 OIDC, P08-03 Workspace-Identity/verifizierte Domains, P08-04 LDAP, P08-05 IdP Group Sync, P08-06 SCIM
   - 4.2 Kontoschutz: P08-07 Zwei-Faktor-Authentifizierung, P08-08 Passkeys, P08-09 Password Policy, P08-10 Domain Security
   - 4.3 Rollen & Zugriff: P08-11 System-Rollen/RBAC, P08-12 Custom Roles, P08-13 GAC (Permission Schemes, effektive Berechtigungen), P08-14 Guests, P08-15 Approvals
   - 4.4 Administration & Nachvollziehbarkeit: P08-16 Admin Interface, P08-17 Workspace Activity Logs, P08-18 API-enabled Audit Logs, P08-27 God-Mode User Management, P08-28 Session-Expiry, P08-29 Argus PII-Scanner
   - 4.5 Lizenz, Seats, Pläne: P08-19 Workspace-Lizenz & Billing-Seite, P08-20 Enterprise-Grid-Instanzlizenz, P08-21 Airgapped-Lizenzdatei, P08-22 Prime/Monitor, P08-23 Self-hosted-Pläne & Deployment-Varianten (One, Airgapped, Private/Managed, FIPS), P08-24 Member-Limits & Seat-Berechnung, P08-25 Storage-Limits, P08-26 Support/SLA
   - 4.6 Querbezüge: P08-30 IdP-Profil-Sync (CE), P08-31 Mitglieder-CSV-Import mit Seat-Limit
5. Offene Punkte / Unklarheiten
- Anhang A: Vollständiges i18n-Inventar der Cluster-Texte (EE-Texte im CE)
- Anhang B: Vollständiges Inventar der CE-Extension-Points und CE-Spuren dieses Clusters
- Anhang C: Inventar der Referenz-Screenshots (Commercial-UI) aus den Developer-Docs

---

## 1. Überblick & Quellenlage

### 1.1 Gegenstand

Spezifiziert werden **alle Funktionen des Clusters „Sicherheit, Administration, Lizenz“, die nicht in der Community Edition (CE) enthalten sind**, sondern in den Bezahl-Editionen (One, Pro, Business, Enterprise bzw. heute „Enterprise Grid“). Der Code der Commercial Edition (`makeplane/plane-ee`, vgl. `/home/user/makeplane/helm-charts/charts/plane-enterprise/Chart.yaml`) ist closed-source. Die Features werden **clean-room** aus öffentlichen Quellen, aus den im CE mitgelieferten EE-Texten (`packages/i18n/src/locales/en/*.json`) und aus Screenshots der offiziellen Developer-Docs beschrieben.

Für jedes Feature wird zusätzlich der CE-Ausgangszustand belegt (grep/Lesen des Repos), damit Implementierungs-Agenten wissen, welche Basis schon portiert wird (siehe `migration/analysis/*`) und was neu entsteht.

### 1.2 Plan- und Editionsmodell (nur Kontext – entfällt nach ADR-001)

| Begriff | Bedeutung | Quelle |
|---|---|---|
| Plan-Keys im CE | `free`, `one`, `pro`, `business`, `enterprise` (`TPlanePlans`), Enum `EProductSubscriptionEnum` = `FREE`, `ONE`, `PRO`, `BUSINESS`, `ENTERPRISE` | `apps/web/components/workspace/billing/comparison/plans.tsx` Z. 15, 70; `packages/types/src/payment.ts` |
| One | Legacy-Self-hosted-Plan, 799 einmalig „per workspace“, `isActive: false`; Highlights „Upto 50 users“, „OIDC and SAML“, „Active cycles“, „Limited time tracking“ | `plans.tsx` Z. 1266–1275, 1305 |
| Pro | 8 $ (monatlich) / 6 $ (jährlich) je User und Monat; Badge „Popular“ | `plans.tsx` Z. 1276–1285; `apps/web/components/workspace/billing/comparison/plan-detail.tsx` |
| Business | „Talk to Sales“ / „Quote on request“ | `plans.tsx` Z. 1286–1293 |
| Enterprise / Enterprise Grid | Top-Lizenz. Im CE-Code `ENTERPRISE`; in Developer-Docs als Badge **„Enterprise Grid“** (LDAP, Airgapped, FIPS) | `plans.tsx` Z. 1294–1301; `/home/user/makeplane/developer-docs/docs/self-hosting/govern/ldap.md` Z. 7; `…/methods/airgapped-edition.md` Z. 7; `…/methods/fips-deployment.md` Z. 11 |
| „Business Plus“ | Nur einmal genannt: Cloud-Spalte „Audit logs, SCIM, advanced auth → Business Plus“; Self-hosted „Available on plans (Commercial and Airgapped)“. Kein Enum, keine weitere Fundstelle. **UNVERIFIZIERT**, ob eigener Plan oder Add-on | `/home/user/makeplane/developer-docs/docs/self-hosting/self-hosting-101.md` Z. 42 |
| Community Edition | AGPL-3.0, „at par with the Free tier of the Cloud“, kein Lizenzschlüssel | `/home/user/makeplane/developer-docs/docs/self-hosting/editions-and-versions.md` Z. 19–29 |
| Commercial Edition | closed-source, „Full feature parity with our Cloud“, **12 freie User-Seats je Workspace**, Upgrade-Flow berechnet Seats aus „users with paid roles“ | `editions-and-versions.md` Z. 31–37; `self-hosting-101.md` Z. 60 |
| Airgapped Edition | Commercial ohne Internet, Offline-Lizenzdatei, „exclusively for Enterprise Grid customers with a minimum commitment of 100 seats“ | `/home/user/makeplane/developer-docs/docs/self-hosting/methods/airgapped-requirements.md` Z. 10 |
| Lizenzbindung | Pro/Business: an **einen Workspace und eine Maschine** gebunden (Workspace Settings → Billing and plans); Enterprise Grid: **Instanz**-Lizenz (God Mode → Billing), gilt für alle Workspaces | `…/manage/manage-licenses/activate-pro-and-business.md` Z. 9, 51; `…/activate-enterprise.md` Z. 9, 23 |
| Aktuelle Pläne (Verifikation) | „Plans are Free, Pro, Business, and Enterprise Grid.“ – One ist nicht mehr erhältlich (`isActive: false`, Kommentar „Plane one plan is not longer available“). **Tier-Regel dieses Dokuments (Verifikation, wie Dok. 20/21/22):** Wo `plans.tsx` nur One nennt, aktuellere/spezifischere Quellen (Docs-Badges, docs.plane.so-Labels) aber einen aktuellen Plan, gilt der aktuelle Plan; der Widerspruch wird dokumentiert. | `self-hosting-101.md` Z. 54; `plans.tsx` Z. 1274; `apps/web/components/workspace/billing/comparison/base.tsx` Z. 29 |

**Hinweis Aktualität:** Die Matrix `plans.tsx` ist ein älterer Stand als die heutige öffentliche Doku (Schwester-Dok. 25 §1.2 belegt Umgruppierungen, z. B. Approvals 2026 unter Enterprise Grid). Für die Portierung ist die Tier-Zuordnung wegen ADR-001 irrelevant; sie wird zur Nachvollziehbarkeit vollständig dokumentiert.

### 1.3 Quellenverzeichnis (Kürzel werden im Text verwendet)

**Repo (R)**

| Kürzel | Pfad | Inhalt |
|---|---|---|
| R1 | `apps/web/components/workspace/billing/comparison/plans.tsx` | Feature×Plan-Matrix (`PLANS_COMPARISON_LIST`), `PLANE_PLANS.planDetails`, `planHighlights` |
| R2 | `packages/constants/src/subscription.ts` | `ENTERPRISE_PLAN_FEATURES` (Z. 7–14), `BUSINESS_PLAN_FEATURES` (Z. 16–23), `PRO_PLAN_FEATURES` (Z. 25–32), `ONE_PLAN_FEATURES` (Z. 34–41), `FREE_PLAN_UPGRADE_FEATURES` (Z. 43–48) |
| R3 | `packages/i18n/src/locales/en/auth.json` | `sso.*` (Z. 2–207: Identity, Domain management, SAML/OIDC-Provider), `auth.common.username.*` (Z. 278–281), `auth.ldap.*` (Z. 361–366) |
| R4 | `packages/i18n/src/locales/en/workspace-settings.json` | `workspace_settings.settings.group_syncing.*` (Z. 192–252), `…identity.*` (Z. 253–257), `…billing_and_plans.*` (Z. 68–75), `…cancel_trial.*` (Z. 282–291), `…general.delete_modal.*` (Z. 21–30) |
| R5 | `packages/i18n/src/locales/en/empty-state.json` | `settings_empty_state.group_syncing.title` (Z. 252–254) |
| R6 | `packages/i18n/src/locales/en/home.json` | `home.business_trial_banner.*` (Z. 68–75) |
| R7 | `packages/i18n/src/locales/en/common.json` | `upgrade_request` (Z. 374), `common.add_seats` (Z. 664), `common.upgrade_cta.*` (Z. 690–693), `role_details.*` (Z. 791–804) |
| R8 | `packages/i18n/src/locales/en/workspace.json` | `workspace.members_import.*` (Z. 331 ff.) inkl. `summary.message.seat_limit` |
| R9 | `packages/i18n/src/locales/en/navigation.json`, `accessibility.json` | `sidebar.upgrade`, `sidebar.upgrade_plan`, `sidebar.plane_pro`; `aria_labels.projects_sidebar.edition_badge` |
| R10 | `apps/api/plane/license/models/instance.py` | `Instance` (inkl. `edition`, `whitelist_emails`, `is_support_required`), `InstanceAdmin`, `InstanceConfiguration`, `InstanceEdition` |
| R11 | `apps/api/plane/license/migrations/0001_initial.py`, `0002_…`, `0003_…`, `0005_rename_product_instance_edition_and_more.py` | historische Felder `license_key`, `user_count`, `product` (in 0005 entfernt/umbenannt) |
| R12 | `apps/api/plane/db/models/user.py` | `User.is_managed`, `is_password_expired`, `is_password_reset_required`, `last_login_medium`, `Account.PROVIDER_CHOICES` |
| R13 | `apps/api/plane/db/migrations/0116_workspacemember_explored_features_and_more.py` | Einführung `User.is_password_reset_required` |
| R14 | `apps/api/plane/authentication/**` (`adapter/base.py`, `adapter/error.py`, `utils/password.py`, `urls.py`) | CE-Auth-Pipeline, Fehlercodes, Passwortstärke |
| R15 | `packages/types/src/instance/auth-ee.ts`, `packages/types/src/instance/auth.ts`, `packages/types/src/instance/base.ts` | EE-Extension-Typen (`TExtendedLoginMediums = never`, `TExtendedInstanceAuthenticationModeKeys = never`), `IInstance.license_key`, `is_activated`, `user_count` |
| R16 | `packages/constants/src/auth/extended.ts`, `core.ts`, `index.ts` | `EXTENDED_LOGIN_MEDIUM_LABELS = {}`, `LOGIN_MEDIUM_LABELS`, `E_PASSWORD_STRENGTH`, `PASSWORD_MIN_LENGTH`, `EAuthErrorCodes` |
| R17 | `apps/web/hooks/oauth/extended.tsx`, `apps/web/hooks/oauth/index.ts`, `apps/web/hooks/oauth/core.tsx`, `apps/space/hooks/oauth/extended.tsx` | Extension-Point für zusätzliche Login-Buttons (SSO/LDAP) |
| R18 | `apps/admin/hooks/oauth/index.ts`, `apps/admin/hooks/oauth/core.tsx`, `apps/admin/hooks/use-sidebar-menu/core.ts`, `index.ts`, `apps/admin/app/routes.ts`, `apps/admin/components/authentication/*.tsx`, `apps/admin/components/common/copy-field.tsx`, `apps/admin/app/(all)/(dashboard)/authentication/page.tsx`, `…/authentication/gitlab/form.tsx` | CE-God-Mode (Muster für SSO-/LDAP-Konfigurationsseiten) |
| R19 | `packages/utils/src/auth.ts` | `getPasswordStrength`, `getPasswordCriteria` |
| R20 | `apps/web/components/settings/profile/content/pages/security.tsx`, `packages/constants/src/settings/profile.ts`, `apps/web/components/settings/profile/sidebar/item-categories.tsx` | Profil → Security (Ort für 2FA/Passkeys) |
| R21 | `packages/constants/src/workspace.ts` (`ROLE`, `ROLE_DETAILS`, `RESTRICTED_URLS`), `packages/constants/src/user.ts` (`EUserPermissions`, `USER_ALLOWED_PERMISSIONS`), `packages/types/src/workspace.ts`, `packages/types/src/project/projects.ts` | CE-Rollen |
| R22 | `apps/api/plane/db/models/workspace.py` (`ROLE_CHOICES` Z. 19, `WorkspaceMember` Z. 198–231), `apps/api/plane/db/models/project.py` (`ProjectMember`, `ProjectMemberInvite`, `guest_view_all_features`) | CE-Rollen/Gäste (Backend) |
| R23 | `apps/web/components/workspace/settings/useMemberColumns.tsx`, `member-columns.tsx` | CE-Mitgliedertabelle (Spalten „Account type“, „Authentication“) |
| R24 | `apps/web/store/workspace/index.ts` Z. 385–391 | No-op-Stub `mutateWorkspaceMembersActivity` |
| R25 | `apps/api/plane/app/views/workspace/user.py` Z. 409–435, `apps/api/plane/app/urls/workspace.py` Z. 137–146 | CE: Benutzer-Aktivität je User und Export |
| R26 | `apps/web/components/workspace/billing/root.tsx`, `…/comparison/{root,base,plan-detail,feature-detail,frequency-toggle}.tsx`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/page.tsx` | CE-Billing-Seite |
| R27 | `apps/web/components/license/modal/upgrade-modal.tsx`, `…/modal/card/*.tsx`, `apps/web/components/workspace/edition-badge.tsx`, `apps/web/components/sidebar/sidebar-wrapper.tsx` Z. 85 | Upgrade-Modal, Editions-Badge |
| R28 | `packages/constants/src/payment.ts`, `packages/types/src/payment.ts`, `packages/utils/src/subscription.ts` | Preis-/Abo-Konstanten |
| R29 | `packages/constants/src/settings/workspace.ts`, `packages/types/src/settings.ts`, `apps/web/components/settings/workspace/sidebar/item-icon.tsx` | Workspace-Settings-Navigation (`billing-and-plans`) |
| R30 | `apps/api/bin/docker-entrypoint-api.sh` Z. 10–24, `apps/api/plane/license/management/commands/register_instance.py` | `MACHINE_SIGNATURE` (SHA-256 aus Host-Merkmalen), Instanz-Registrierung |
| R31 | `apps/api/plane/settings/common.py` Z. 389, 403, 425, 432; `apps/api/plane/license/api/views/instance.py` Z. 142; `apps/web/hooks/use-file-size.ts` | `FILE_SIZE_LIMIT`, `SESSION_COOKIE_AGE`, `ADMIN_SESSION_COOKIE_AGE` |
| R32 | npm `@makeplane/propel@0.7.3` (entpackt, nur gelesen) `dist/icons/**` | Icons `Saml`, `Oidc` (`other-products/`), `AuditLogsOutline`, `AccessAndRolesOutline`, `ShieldOutline`, `ShieldMinusOutline`, `KeyOutline`, `BillingsOutline`, `ApproverOutline`, `UpgradeOutline`, `DeactivatedUserOutline`, `LockKeyholeCircleOutline`, `FileKeyOutline`, `LogsOutline`, `LogsAltOutline`, `LogConfigOutline`, `ActivityOutline`, `MessageSupportOutline`, `FolderLockOutline`, **`GroupSyncOutline`**, **`PiiScannerOutline`** (`miscellaneous/`), jeweils mit `*Filled`-Variante; **Ausnahmen (Verifikation):** `UserCogOutline` ohne Filled-Variante, `UpgradeAltFilled` ohne Outline-Variante (`dist/icons/index.d.ts` Z. 545–546, 623–624, 690, 695) |
| R33 | `packages/blocks/src/empty-state/assets/horizontal-stack/group-syncing.tsx`, `packages/blocks/src/empty-state/assets/asset-registry.tsx` Z. 75–77 | Illustration „group-syncing“ |
| R34 | `deployments/cli/community/restore-airgapped.sh` | CE-Skript zum Restore in eine Airgapped-Commercial-Instanz |

**Offline-Dokumentation (D)** – Basis `/home/user/makeplane/developer-docs/docs/`

| Kürzel | Pfad | Inhalt |
|---|---|---|
| D1 | `self-hosting/govern/saml-sso.md` | SAML SSO (Badges Pro, Business) |
| D2 | `self-hosting/govern/oidc-sso.md` | OIDC SSO (Badges Pro, Business) |
| D3 | `self-hosting/govern/ldap.md` | LDAP (Badge Enterprise Grid) |
| D4 | `self-hosting/govern/authentication.md` | Überblick Auth-Methoden |
| D5 | `self-hosting/govern/instance-admin.md` | God Mode (General, Email, Authentication, Workspaces, User management, Images) |
| D6 | `self-hosting/govern/god-mode/session-expiry.md` | Session-Einstellungen |
| D7 | `self-hosting/manage/manage-instance-users.md` | God-Mode User Management |
| D8 | `self-hosting/manage/manage-licenses/activate-pro-and-business.md` | Workspace-Lizenz, Sync plan, Delink |
| D9 | `self-hosting/manage/manage-licenses/activate-enterprise.md` | Enterprise-Grid-Instanzlizenz |
| D10 | `self-hosting/manage/manage-licenses/activate-airgapped.md`, `activate-airgapped-enterprise.md` | Lizenzdatei-Aktivierung |
| D11 | `self-hosting/troubleshoot/license-errors.md` | Lizenzfehler |
| D12 | `self-hosting/editions-and-versions.md`, `self-hosting/self-hosting-101.md`, `self-hosting/upgrade-from-community.md` | Editionen, Lizenzmodell, Upgrade CE → Commercial |
| D13 | `self-hosting/methods/airgapped-requirements.md`, `airgapped-edition.md`, `airgapped-edition-kubernetes.md`, `self-hosting/manage/community-to-airgapped.md` | Airgapped |
| D14 | `self-hosting/methods/fips-deployment.md` | FIPS (Badge Enterprise Grid) |
| D15 | `self-hosting/manage/prime-cli.md`, `self-hosting/manage/health-checks.md` Z. 365–386, `self-hosting/plane-architecture.md` Z. 46–47 | Prime CLI, Monitor-Dienst |
| D16 | `self-hosting/telemetry.md` | „Usage for billing“ |
| D17 | `api-reference/idp-group-sync/*.md` (13 Dateien) | IdP-Group-Sync-API |
| D18 | `api-reference/members/remove-workspace-member.md` | Mitglied entfernen inkl. Seat-Reduktion |
| D19 | `dev-tools/mcp-server-tools.md` Z. 409–421 | Rollen-Namespaces, `list_roles`, `role_slug` |
| D20 | `dev-tools/mcp-server.md` Z. 729–752 | „audit API token events in the workspace audit log“ |
| D21 | `dev-tools/agents/overview.md` Z. 38 | „Agents … do not count as billable users“ |
| D22 | `self-hosting/govern/environment-variables.md` Z. 111–121 | `MACHINE_SIGNATURE`, `SECRET_KEY`, `AES_SECRET_KEY` |
| D23 (Verifikation) | Branch `docs/api-reference-v2` der Developer-Docs (Commit `b89c72c`, 11.08.2026; lokaler Klon `/tmp/claude-0/-home-user-plane/fe89ae79-d9fa-54e4-b848-1dc9726b58d0/scratchpad/devdocs-v2/repo/docs/api-reference/v2/`, wie Dok. 21 Kap. 9 „`V2/`“): `audit-logs/{overview,list-audit-logs,get-audit-log}.md`, `roles/{overview,list-roles,get-role}.md`, `permission-schemes/{overview,list-permission-schemes,get-permission-scheme}.md`, `permissions/{overview,get-workspace-permissions,get-project-permissions}.md`, `members/overview.md`, `group-sync/overview.md`, `invitations/overview.md`, `authentication.md` Z. 280–287, `errors.md` Z. 200, 276–297 | Audit-Log-Objekt und -Filter, Rollen-/Permission-Scheme-/Effektiv-Berechtigungs-API, Rollen-Slugs, Scopes, Feature-Gating `402` |

**Screenshots der Commercial-UI (B)** – Basis `/home/user/makeplane/developer-docs/docs/public/images/` (gesichtet; maßgebliche 1:1-Referenz, soweit vorhanden; vollständiges Inventar in Anhang C)

| Kürzel | Datei | Zeigt |
|---|---|---|
| B1 | `custom-sso/oidc-oauth.png` | God Mode → Authentication → OIDC (Formular + Plane-provided details) |
| B2 | `custom-sso/saml-oauth.png` | God Mode → Authentication → SAML (Formular + Mapping) |
| B3 | `custom-sso/instance-login.png`, `custom-sso/plane-login.png` | Login-Seite mit Button „Sign up with Okta“ |
| B4 | `ldap/enable-ldap.webp`, `instance-admin/god-mode-authentication.webp` | God-Mode-Authentifizierungsliste inkl. OIDC/SAML/LDAP-Karten, Sidebar mit „Billing“/„User Management“ |
| B5 | `ldap/ldap-configuration.webp` | LDAP-Konfigurationsseite |
| B6 | `ldap/sign-in-ldap.webp` | Login-Seite mit „Sign in with LDAP“ |
| B7 | `activate-license/activate-enterprise-plan.webp`, `activate-license/upload-airgapped-enterprise.webp` | God Mode → Billing (Schlüssel bzw. Lizenzdatei) |
| B8 | `activate-license/enter-license-key-selfhosted.webp`, `activate-license/upload-airgapped-license-file.webp` | Workspace → Billing and plans → Aktivierungs-Modal (Schlüssel bzw. Datei) |
| B9 | `activate-license/pro-activated-cloud.webp`, `activate-license/billing-and-plans-cloud.webp` | Billing-and-plans-Seite (Pro aktiv / Free mit „Start free trial“) |
| B10 | `instance-admin/user-management.webp`, `invite-instance-admin.webp`, `user-actions.webp` | God-Mode User Management |
| B11 | `instance-admin/god-mode-general.webp` | God Mode → General mit „Chat + telemetry“ |

**Helm-Chart (H)** – Basis `/home/user/makeplane/helm-charts/charts/plane-enterprise/`

| Kürzel | Pfad | Inhalt |
|---|---|---|
| H1 | `values.yaml` Z. 1–21 (`planeVersion: v3.3.3`, `license.licenseServer`, `license.licenseDomain`, `airgapped.*`), Z. 393–405 (`services.monitor`), Z. 700–720 (`services.argus`), Z. 1137–1145 (`env.skip_env_var`) | Lizenz-/Airgapped-/Monitor-/Argus-Konfiguration |
| H2 | `templates/config-secrets/app-env.yaml` Z. 110–230 | `PRIME_HOST`, `MACHINE_SIGNATURE`, `APP_DOMAIN`, `APP_VERSION`, `PAYMENT_SERVER_BASE_URL`, `FEATURE_FLAG_SERVER_BASE_URL`, `SKIP_ENV_VAR`, `IS_AIRGAPPED` |
| H3 | `templates/config-secrets/monitor.yaml` | Monitor-Umgebung (`DEPLOY_PLATFORM`, `API_URL`, `IS_AIRGAPPED`) |
| H4 | `templates/config-secrets/argus-env.yaml`, `README.md` Z. 1090–1146 | Argus PII-Scanner |
| H5 | `README.md` Z. 1688–1700, `templates/NOTES.txt` Z. 127 | DB-residente Secrets (OIDC-Client-Secret, SAML-Zertifikat, `LDAP_BIND_PASSWORD`) |

**Web (W) – nur sekundär (W1–W14).** Eigene WebSearch-Abfragen waren im Autorenlauf **nicht möglich** (der Verifikationslauf hat eigene Abfragen ergänzt, W15–W23 unten): Das WebSearch-Budget des gesamten Workflow-Laufs (200 Abfragen je Turn, über alle Agenten geteilt) war beim Start dieser Analyse bereits erschöpft; `plane.so`/`docs.plane.so` sind per Netzwerk-Policy nicht abrufbar; ein GitHub-Quell-Repo der Nutzer-Doku war nicht erreichbar (`https://github.com/makeplane/docs` → HTTP 404). Die folgenden URLs stammen aus Schwester-Dokumenten, deren Agenten WebSearch-Zusammenfassungen gelesen haben. Aussagen daraus sind mit „(W, sekundär)“ markiert und gelten als **mittel** belastbar.

| Kürzel | URL | Über Schwester-Dokument |
|---|---|---|
| W1 | https://docs.plane.so/authentication/group-sync | 21 (§4.8), 22 (Q29) |
| W2 | https://plane.so/blog/introducing-granular-access-control-gac-ldap-idp-group-sync | 22 (Q29, P03-F45) |
| W3 | https://docs.plane.so/authentication/sso | 22 (Q29, P03-F06) |
| W4 | https://docs.plane.so/workspaces-and-users/audit-logs | 22 (Q29, P03-F44) |
| W5 | https://plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more | 25 (W30), 26 (W15) |
| W6 | https://plane.so/changelog/2026-07-31-skills-plane-ai-richer-pages-audit-logs | 25 (W31), 26 (W19) |
| W7 | https://docs.plane.so/roles-and-permissions/permissions-matrix, https://docs.plane.so/roles-and-permissions/member-roles | 25 (W48), 26 (W29) |
| W8 | https://plane.so/changelog/release-v2-5-0-project-labels-sso-for-god-mode-columns-in-pages | 26 (W44) |
| W9 | https://plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more | 26 (W32) |
| W10 | https://docs.plane.so/workspace-administration/workspace-governance, https://plane.so/blog/introducing-workspace-governance | 25 (W3, W4) |
| W11 | https://plane.so/pricing, https://plane.so/enterprise-grid, https://plane.so/business, https://plane.so/blog/introducing-enterprise-grid | 20, 25 (W27, W45), 26 (W12, W43) |
| W12 | https://plane.so/self-hosted/whitepaper | 20 (PF-61, PF-98) |
| W13 | https://www.idenhq.com/scim-tax/plane | 22 (Q29) |
| W14 | https://docs.plane.so/workspaces-and-users/billing-and-plans | 20 (Q10) |

**Web (W) – eigene WebSearch-Abfragen des Verifikationslaufs (2026-10-22, 13 Tool-Aufrufe bzw. 14 Abfragen, nur Suchmaschinen-Zusammenfassungen; Seiten selbst nicht abrufbar → Konfidenz höchstens „mittel“):**

| Kürzel | URL | Befund (Zusammenfassung) |
|---|---|---|
| W15 | https://docs.plane.so/workspaces-and-users/audit-logs | Seitentitel „Workspace Audit Logs **Enterprise Grid**“; Ort Settings → Audit logs; nur Admins und Owners sehen/exportieren; neueste Ereignisse zuerst, Filter und Export oben; Einträge unveränderlich (auch nicht durch Admins löschbar); erfasst laut Zusammenfassung Sign-ins, Mitgliedschafts-/Rollenänderungen, Einstellungsänderungen, Integrations- und Sicherheitsereignisse, Workspace-Feature an/aus, Planwechsel; Lesen und Exportieren des Logs werden selbst protokolliert |
| W16 | https://docs.plane.so/authentication/sso | Domain-Verifizierung vor SSO-Konfiguration; Workspace Settings → Identity; TXT-Record; Status „Pending“ möglich, später „Verify“; Prüftipp `dig TXT yourdomain.com`; **eine Domain kann nur in einem Workspace gleichzeitig verifiziert sein** (vorher dort entfernen); Plan im Snippet nicht genannt |
| W17 | https://plane.so/business | Business ($13/Seat/Monat jährlich, 14-Tage-Trial) nennt „SSO on Cloud“ |
| W18 | https://docs.plane.so/roles-and-permissions/overview, https://docs.plane.so/roles-and-permissions/member-roles, https://docs.plane.so/roles-and-permissions/permissions-matrix | Owner, Member, Guest auf allen Plänen; weitere System-Rollen (Admin, Contributor, Commenter) „exclusive to the Business plan and higher“; Umbenennungen „Workspace Admin“ → „Workspace Owner“, „Project Member“ → „Contributor“; Owner allein darf Workspace löschen und Ownership übertragen; Commenter = Lesen + Kommentieren + Intake; ältere Seite https://docs.plane.so/workspaces-and-users/roles kennt nur Admin/Member/Guest |
| W19 | https://docs.plane.so/roles-and-permissions/custom-roles, https://docs.plane.so/roles-and-permissions/permission-schemes | Workspace settings → „Roles and permissions schemes“, Tab „Roles“ (Projektrollen im Tab „Project“); Custom Roles aus Permission Schemes zusammengesetzt; effektive Rechte = Vereinigung aller Schemes; System-Schemes (z. B. „Workspace Member“, „Workspace Admin“) vorgefertigt, nicht editierbar; Custom Roles nur Enterprise Grid; dürfen weder Workspace-Löschung noch Ownership-Transfer enthalten |
| W20 | https://plane.so/changelog/2026-04-25-custom-roles-granular-access-permissions-redesign | RBAC bleibt Standard in jedem Workspace; **GAC = Enterprise-Add-on** (Custom Roles aus wiederverwendbaren Permission Schemes); drei System-Rollen umbenannt; neue Rolle **Workspace Admin** zwischen Owner und Member auf Business und Enterprise; bedingte Rechte (z. B. nur selbst erstellte Items löschen); bestehende Zuweisungen automatisch gemappt |
| W21 | https://forum.plane.so/t/plane-commercial-v3-0-0-is-live-desktop-app-workspace-governance-rbac-and-more/281 | Commercial v3.0.0 „… workspace governance, RBAC, and more“ (nur Titel) |
| W22 | https://plane.so/blog/introducing-granular-access-control-gac-ldap-idp-group-sync (10.06.2026), https://plane.so/blog/introducing-enterprise-grid | GAC und LDAP unter Enterprise Grid; LDAP für Active Directory, OpenLDAP, FreeIPA; Group Sync: IdP-Gruppe → Projekt mit Default-Rolle Admin/Member/Guest, Offline-Sync alle 6 h; Workspace-Mitgliedschaft bleibt beim Entfernen immer erhalten; alleinige Projekt-Admins und manuell hinzugefügte Mitglieder werden nie entfernt; mehrere Gruppen → höchste passende Rolle; manuell vergebene Rollen werden nie herabgestuft |
| W23 | https://docs.plane.com/…, https://help.plane.com/… | **Anderes Unternehmen** (Plane, Lohn-/Zahlungsplattform; Treffer erwähnen Bankkonto-Änderungen, „administrators and managers“). Die dortigen Aussagen zu 2FA, Passkeys, Geräte-Sessions gehören **nicht** zu makeplane/Plane und werden **nicht** verwendet (gleiche Feststellung Dok. 22, Verifikations-Protokoll) |

Ohne Plane-Treffer blieben die Suchen zu Password Policy/erlaubten Domains, Workspace Activity Logs, Audit-Log-Aufbewahrung und SCIM.

### 1.4 Methode

1. Plan-Matrix R1 für die Sektionen `workspace-user-management`, `storage`, `security`, `self-hosted`, `support` zeilengenau übertragen (Kap. 2).
2. Alle EE-Texte des Clusters per Skript aus `packages/i18n/src/locales/en/*.json` extrahiert (Anhang A, 251 Schlüssel) und gegen CE-Code geprüft (`grep` auf `apps/**`, `packages/**` außer `locales`): Die Schlüssel `sso.*`, `auth.ldap.*`, `auth.common.username.*`, `workspace_settings.settings.group_syncing.*`, `…identity.*`, `…cancel_trial.*`, `…general.delete_modal.{description,dismiss,cancel}`, `home.business_trial_banner.*`, `common.add_seats`, `common.upgrade_cta.higher_subscription`, `upgrade_request`, `workspace.members_import.*`, `project.members_import.*` werden im CE-Code **nicht** referenziert (= EE-Texte).
3. CE-Status jedes Features per `grep` geprüft (Anhang B).
4. Developer-Docs (D), Helm-Chart (H) und Screenshots (B) vollständig gelesen bzw. gesichtet.
5. Web-Aussagen nur sekundär (siehe oben).

### 1.5 Kernaussagen

1. **Instanzweites SSO (SAML, OIDC, LDAP)** ist in der Commercial Edition eine Erweiterung der God-Mode-Seite „Authentication“: drei zusätzliche Karten mit „Configure“/„Edit“ + Schalter und je einer Konfigurationsseite mit zweispaltigem Layout „IdP-provided details for Plane“ / „Plane-provided details for your IdP“ (B1, B2, B4, B5). Das CE hat dafür fertige Extension-Points (R15–R18).
2. **Workspace-Identity** (verifizierte Domains per DNS-TXT, Workspace-SSO mit genau einem aktiven Provider) ist ein **zweiter, workspace-bezogener SSO-Weg** (Cloud). Alle UI-Texte liegen vollständig im CE (`sso.*`, 115 Schlüssel, R3), Code fehlt.
3. **IdP Group Sync** (Gruppen-Claim → Workspace-/Projektrollen, Sync on login, Offline-Sync alle 6 h, Auto-remove) ist über API (D17) und UI-Texte (R4) gut spezifiziert.
4. **2FA, Passkeys, Password Policy, Domain Security, Approvals, Admin Interface, Activity Logs** sind im CE nur als Matrix-Zeilen belegt; öffentliche Detailspezifikationen waren nicht abrufbar. Die Abschnitte geben das Belegbare wieder und kennzeichnen Entwurfsvorschläge als **Vorschlag (UNVERIFIZIERT)**. **Audit Logs** sind seit dem Verifikationslauf über die v2-API-Doku (D23: Objekt, Filter, Kategorien, Scopes) und die Nutzer-Doku (W15: Ort, Rollen, Unveränderlichkeit) belegt; Tier laut Doku **Enterprise Grid**.
5. **Rollenmodell der Commercial Edition (Verifikation erweitert):** Zwei Schichten. **RBAC** mit System-Rollen ist Standard in jedem Workspace; Owner, Member, Guest gibt es auf allen Plänen, die Rollen Workspace Admin, Contributor und Commenter ab Business (W18, W20). **GAC** (Enterprise Grid) ergänzt Custom Roles aus wiederverwendbaren Permission Schemes (W19, W20). Rollen sind Objekte mit `namespace` (`instance`, `workspace`, `project`), `slug`, `level`, `is_system`, `status` (D19, D23). Das CE kennt nur Integer-Rollen 20/15/5 (R21, R22).
6. **Lizenz/Seats/Billing** (Workspace-Lizenzschlüssel, Instanzlizenz, Lizenzdatei, Sync/Delink, Seat-Berechnung, Trial, Monitor/Prime) ist vollständig dokumentiert, **entfällt aber nach ADR-001** komplett. Die neue Plattform zeigt keine Billing-Seite, kein Editions-Badge und kein Upgrade-Modal.
7. **Airgapped** ist im Original eine Enterprise-Grid-Edition; in der neuen Plattform ist Airgapped-Fähigkeit **Grundeigenschaft** (ADR-004). FIPS ist ein Betriebsprofil (Krypto-Policy), kein Feature-Gate.
8. **God-Mode-Erweiterungen** der Commercial Edition in diesem Cluster: „User Management“ (Instanz-Benutzer, Instanz-Admins einladen), „Billing“ (entfällt), Session-Expiry-Einstellungen, „Chat with us“-Schalter (entfällt, ADR-004). Die God-Mode-Seite „System checks“ (Health-Übersicht aller Dienste) ist in Dok. 22 (P03-F03, P03-F34) spezifiziert und wird hier nicht dupliziert (Verifikation).

---

## 2. Plan-Matrix-Auszug für diesen Cluster (R1, zeilengenau)

Darstellung: `✓` = `true`, `–` = `false`, Text = String-Wert, „CS“ = `comingSoon: true`. Spalte „Z.“ = Zeile in `apps/web/components/workspace/billing/comparison/plans.tsx`. Da `PlansComparison` fest `isSelfManaged` setzt, zeigt das CE `feature["self-hosted"]?.[plan] ?? feature.cloud[plan]` (`apps/web/components/workspace/billing/comparison/root.tsx`; vgl. Dok. 20 §1.2).

### 2.1 Sektion `workspace-user-management` – „Workspace and user management“ (Z. 671–763)

| Z. | Feature | Beschreibung (Original) | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 676 | Member limit | Cloud: „Number of seats that can use project and work management features“; `selfHostedDescription`: „Number of users that our standard infra supports / Increase infra to get more users“ | Cloud „12“; self-hosted „~50“ | Cloud „“ (leer); self-hosted „~50“ | Cloud „Unlimited“; self-hosted „~200“ | Cloud „Unlimited“; self-hosted „~200“ | „Unlimited“ / „Unlimited“ | |
| 695 | Roles | Choose from one of four pre-defined roles or create custom ones with RBAC. | Basic | Basic | Pre-defined roles | RBAC | GAC | |
| 706 | Guests | Let some users see everything or just their work items in a project. | – | 5 per paid member | 5 per paid member | 5 per paid member | 5 per paid member | |
| 717 | Approvals | Set workspace, project, and work item type approvals to designated admins. | – | – | – | ✓ | ✓ | CS |
| 729 | Admin Interface | Get an admin overview to manage workspace and project settings. | – | – | – | ✓ | ✓ | |
| 740 | Workspace Activity Logs | See filterable activity logs for your entire workspace. | – | – | – | ✓ | ✓ | |
| 751 | API-enabled Audit Logs | See a full-workspace audit log and use APIs to flag Plane activity in compliance systems. | – | – | – | ✓ | ✓ | CS |

### 2.2 Sektion `storage` – „Storage“ (Z. 1026–1054, `cloudOnly: true`)

| Z. | Feature | Beschreibung | Free | One | Pro | Business | Enterprise |
|---|---|---|---|---|---|---|---|
| 1032 | Space | Total storage allowed per workspace | 5GB | – | 1 TB | 5 TB | Custom |
| 1043 | Max file size | Limit for uploads to your workspace | 5 MB | – | 100 MB | 200 MB | Custom |

`cloudOnly` wird in `base.tsx` nicht ausgewertet (Dok. 20 §2.11).

### 2.3 Sektion `security` – „Security“ (Z. 1055–1129)

| Z. | Feature | Beschreibung | Free | One | Pro | Business | Enterprise | Besonderheit |
|---|---|---|---|---|---|---|---|---|
| 1060 | SAML | Get the officially supported SAML implementation and make Plane secure with any IdP. | – | ✓ | ✓ | ✓ | ✓ | |
| 1071 | OIDC | Get the officially supported OIDC implementation and make Plane secure with any IdP. | – | ✓ | ✓ | ✓ | ✓ | `selfHostedOnly: true` |
| 1083 | Domain Security | Choose other domains that can authenticate into your Plane workspace or restrict all but one domain. | – | – | ✓ | ✓ | ✓ | |
| 1095 | Two-factor authentication and passkeys | Secure your Plane workspace with device-dependent two-factor authentication and passkeys. | – | – | ✓ | ✓ | ✓ | |
| 1106 | Password Policy | Set custom password policies in line with your compliance requirements. | – | – | ✓ | ✓ | ✓ | |
| 1117 | LDAP | Get our official LDAP implementation and secure your Plane workspace with your LDAP server. | – | – | – | – | ✓ | `comingSoon: true` |

### 2.4 Sektion `self-hosted` – „Self-hosted“ (Z. 1130–1203, `selfHostedOnly: true`)

| Z. | Feature | Beschreibung | Free | One | Pro | Business | Enterprise | CS |
|---|---|---|---|---|---|---|---|---|
| 1136 | God Mode | Manage your self-hosted Plane instance better with an instance admin interface. | ✓ | ✓ | ✓ | ✓ | ✓ | |
| 1147 | One-click Deployment | Install and deploy your self-hosted Plane to any private cloud with a single-line command. | – | ✓ | ✓ | ✓ | ✓ | |
| 1158 | Digital Ocean Marketplace app | Get our Digital Ocean-compatible app on their marketplace. | – | ✓ | ✓ | ✓ | ✓ | |
| 1169 | Heroku Platform app | Get our Heroku Platform-compatible app and deploy to Heroku easily. | – | ✓ | ✓ | ✓ | ✓ | |
| 1180 | AWS AMI | Get our AMI-compatible app from the AWS marketplace. | – | ✓ | ✓ | ✓ | ✓ | |
| 1191 | Private deployments | Get our hosted Cloud app on a private Cloud managed by us. | – | – | – | – | ✓ | CS |

### 2.5 Sektion `support` – „Support“ (Z. 1204–1254)

| Z. | Feature | Beschreibung | Free | One | Pro | Business | Enterprise |
|---|---|---|---|---|---|---|---|
| 1209 | Channels | Get access to one or more Support channels by your plan. | Icon Forum (`ChatOutline`, `ForumIcon`) | Icons `MailOutline` + Forum | Icons `MailOutline` + Forum + `ChatOutline` | „Full-suite / professional services“ | „Full-suite / professional services“ |
| 1235 | SLA | „Get business-friendly SLAs with higher plans. SLAs are by priority of work item and tiers can be requested.“ (Link `https://plane.so/talk-to-sales`) | – | – | ✓ | ✓ | ✓ |

### 2.6 Plan-Highlights und Feature-Listen mit Cluster-Bezug

| Liste | Einträge mit Cluster-Bezug (vollständig) | Quelle |
|---|---|---|
| `planHighlights.free` | „Upto 12 users“ | R1 Z. 1304 |
| `planHighlights.one` | „Upto 50 users“, „OIDC and SAML“ | R1 Z. 1305 |
| `planHighlights.pro` | „Unlimited users“ | R1 Z. 1306 |
| `planHighlights.business` | „RBAC“ | R1 Z. 1307 |
| `planHighlights.enterprise` | „Private + managed deployments“, „GAC“, „LDAP support“ | R1 Z. 1308 |
| `ENTERPRISE_PLAN_FEATURES` | „Private + managed deployments“, „GAC“, „LDAP support“, „Full-suite professional services“ | R2 Z. 7–14 |
| `BUSINESS_PLAN_FEATURES` | „Workflows + Approvals“ | R2 Z. 16–23 |
| `ONE_PLAN_FEATURES` | „OIDC + SAML for SSO“, „Docker, Kubernetes and more“ | R2 Z. 34–41 |
| `FREE_PLAN_UPGRADE_FEATURES` | „OIDC + SAML for SSO“ | R2 Z. 43–48 |
| Pro-Kurzbeschreibung (Commercial-Billing-Seite) | „Unlimited members, 1:5 Guests, Issue Types, Active Cycles, and more“ | B9 (`pro-activated-cloud.webp`) |
| Free-Kurzbeschreibung (Cloud) | „12 members, unlimited projects, issues, cycles, modules, and pages“ | B9 (`billing-and-plans-cloud.webp`) |
| Free-Kurzbeschreibung (CE) | Box „Community – Unlimited projects, issues, cycles, modules, pages, and storage“ | `apps/web/components/workspace/billing/root.tsx` |

---
## 3. Feature-Tabelle

Legende **CE-Status** (per `grep`/Lesen geprüft, Belege in Anhang B):
- **fehlt** – keine funktionale Spur außer Matrix-Zeile, i18n-Texten, Icons oder Illustrationen.
- **Stub/UI-Hülle im CE** – Extension-Point, leerer Typ/Enum, No-op-Funktion, ungenutztes Modellfeld, leere Komponente, toter Service-Aufruf oder Upsell-Seite vorhanden, Funktion fehlt.
- **teilweise im CE** – im CE erreichbare Teilfunktion oder produktiv genutztes Datenmodell vorhanden, Bezahl-Abstufung fehlt.
- **im CE vorhanden (nur Cloud-Gating)** – Funktion im CE vollständig, nur Kontingent/Plan-Gate ist Cloud-/Commercial-seitig.
- **Verifikation:** Legende an die verifizierte Abgrenzungsregel aus Dok. 20 (Abschnitt 3, „Abgrenzungsregel“) angeglichen; vorher zählten „vollständige UI-Texte“ als Stub. Betroffen: P08-05 (Stub → fehlt), P08-22 und P08-26 (teilweise → Stub).

Legende **Portierung** (ADR-001/004): **portieren** = neue Plattform baut die Funktion, immer aktiv · **entfällt** = Billing/Limit/Vertrieb, wird nicht gebaut · **Instanz-Einstellung** = Limit wird frei konfigurierbar mit großzügigem Default.

| ID | Feature | ab Plan | Abstufung je Plan | CE-Status | Portierung | Quelle |
|---|---|---|---|---|---|---|
| P08-01 | SAML-SSO, instanzweit (God Mode → Authentication → SAML), inkl. Login in God Mode per SSO | **Pro** (Verifikation, vorher One): Docs-Badges „Pro“, „Business“ (aktuellere, self-hosting-spezifische Quelle; One nicht mehr erhältlich); Matrix: One | Matrix: Free –; One/Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (generische Extension-Points R15–R18, Icon `Saml` R32); **Widerspruch:** Dok. 22 P03-F04 wertet als „fehlt“ (Dok. 22 O33) | portieren | R1 Z. 1060; R2 Z. 35, 44; D1 Z. 7; B2; B4; W8 (W, sekundär); Dok. 22 P03-F04 |
| P08-02 | OIDC-SSO, instanzweit (God Mode → Authentication → OIDC) | **Pro** (Verifikation, vorher One): Docs-Badges „Pro“, „Business“; Matrix: One (`selfHostedOnly`) | Matrix: Free –; One/Pro/Business/Enterprise ✓ | Stub/UI-Hülle im CE (wie P08-01, Icon `Oidc`); Widerspruch Dok. 22 P03-F05 „fehlt“ | portieren | R1 Z. 1071–1073; D2 Z. 7; B1; B4; Dok. 22 P03-F05 |
| P08-03 | Workspace-Identity: verifizierte E-Mail-Domains (DNS-TXT) + Workspace-SSO (SAML **oder** OIDC, genau ein aktiver Provider, „Switch“-Dialog) | **Business** (Verifikation, vorher „unklar“; Cloud): plane.so/business nennt „SSO on Cloud“ (W17, nur Suchzusammenfassung, mittel) | – | Stub/UI-Hülle im CE (115 Texte `sso.*`, 3 Texte `workspace_settings.settings.identity.*`, Login-Extension-Points R15–R17; keine Route, kein Modell) | portieren (als Workspace-SSO zusätzlich zum Instanz-SSO; siehe offene Frage O1) | R3 Z. 2–207; R4 Z. 253–257; W3, W16, W17 (W) |
| P08-04 | LDAP-Authentifizierung (Bind-DN-Suche + User-Bind, Profilabgleich) | Enterprise (Matrix, Coming soon); Docs: Enterprise Grid | nur Enterprise / Enterprise Grid | Stub/UI-Hülle im CE (`auth.ldap.header.*`, `auth.common.username.*`) | portieren | R1 Z. 1117; R2 Z. 10; R3 Z. 278–281, 361–366; D3; D14; B4; B5; B6 |
| P08-05 | IdP Group Sync (IdP-Gruppen → Workspace-Rolle bzw. Projekt + Projektrolle; Sync on login, Offline-Sync alle 6 h, Auto remove, Group attribute key) | Enterprise Grid (Doku-Seite mit Tag „Enterprise Grid“, Dok. 21 V.2 S3; W2, W22; Whitepaper-Snippet in Dok. 20 PF-98); Docs: nur Commercial Self-hosted, nur OIDC (W1) | – | **fehlt** (Verifikation, vorher Stub): nur 33 Texte R4, 1 Empty-State-Text R5, registrierte, aber unbenutzte Illustration R33, Propel-Icon `GroupSyncOutline` (R32); kein Code-Verweis. Konsistent mit Dok. 20 PF-98 und Dok. 21 F12 (K09); Widerspruch Dok. 22 P03-F08 „Stub“ | portieren | D17; D23; R4 Z. 192–252; R5; R33; Dok. 21 §2.6/§4.8 |
| P08-06 | SCIM-Provisioning | „Business Plus“ (Cloud) / „Available on plans (Commercial and Airgapped)“ (D12); Enterprise Grid laut Whitepaper-Snippet (Dok. 20 PF-98, W12) | – | fehlt | portieren (UNVERIFIZIERT im Umfang, O7) | `self-hosting-101.md` Z. 42; W12, W13 (W, sekundär) |
| P08-07 | Zwei-Faktor-Authentifizierung (geräteabhängig) | Pro | Free/One –; Pro/Business/Enterprise ✓ | fehlt | portieren | R1 Z. 1095 |
| P08-08 | Passkeys | Pro | wie P08-07 (gleiche Matrix-Zeile) | fehlt | portieren | R1 Z. 1095 |
| P08-09 | Password Policy (eigene Passwortrichtlinien) | Pro | Free/One –; Pro/Business/Enterprise ✓ | teilweise im CE (erreichbare feste Regeln: zxcvbn-Score ≥ 3 im Backend, 8 Zeichen + Zeichenklassen im Frontend; ungenutzte Felder `is_password_expired`, `is_password_reset_required`); **Widerspruch:** Dok. 20 PF-96 „fehlt“, Dok. 22 P03-F10 „teilweise“ – beibehalten, weil die Durchsetzungspunkte im CE erreichbar sind | portieren | R1 Z. 1106; R12; R13; R14 (`utils/password.py`); R16; R19 |
| P08-10 | Domain Security (weitere zugelassene Domains / alle außer einer Domain sperren) | Pro | Free/One –; Pro/Business/Enterprise ✓ | fehlt (`Instance.whitelist_emails` ungenutztes Altfeld; verwandt: `GITHUB_ORGANIZATION_ID`) | portieren | R1 Z. 1083; R10 |
| P08-11 | Rollen (RBAC mit System-Rollen): Workspace Owner/Admin/Member/Guest, Projekt Admin/Contributor/Commenter/Guest; Owner allein darf Workspace löschen und Ownership übertragen | **Business** (Verifikation, vorher Pro): Workspace Admin, Contributor, Commenter laut Doku ab Business, Owner/Member/Guest auf allen Plänen (W18, W20) | Matrix: Free/One „Basic“, Pro „Pre-defined roles“, Business „RBAC“; **Widerspruch** Matrix (Pro) ↔ Doku 2026 (Business) – aktuellere Quelle gewinnt | teilweise im CE (Integer-Rollen 20/15/5 = Owner/Member/Guest-Äquivalent) | portieren | R1 Z. 695; D19; D23; R21; R22; W7, W18, W20 (W) |
| P08-12 | Custom Roles (benutzerdefinierte Rollen aus Permission Schemes) | **Enterprise Grid** (Verifikation, vorher Business): Doku „Custom roles … Enterprise“, Changelog „GAC = Enterprise add-on“ (W19, W20) | Matrix Business „RBAC“ mit Text „… or create custom ones with RBAC“; **Widerspruch** – aktuellere Doku gewinnt | fehlt | portieren | R1 Z. 695–703, 1307; D23; W19, W20 (W) |
| P08-13 | GAC – Granular Access Control: Permission Schemes (System- und Custom-Schemes), bedingte Rechte, effektive Berechtigungen | **Enterprise Grid** (Verifikation, vorher Enterprise; Synonym, Doku-Name) | Matrix Enterprise „GAC“ | fehlt | portieren | R1 Z. 695, 1308; R2 Z. 9; D23; W2, W19, W20, W22 (W) |
| P08-14 | Guests (Kontingent „5 per paid member“, Pro-Text „1:5 Guests“) | **Pro** für das Kontingent (Verifikation, vorher One; One nicht mehr erhältlich, B9 nennt „1:5 Guests“ bei Pro); die Gast-Rolle selbst gibt es laut Doku auf allen Plänen (W18) | Matrix: Free –; One–Enterprise „5 per paid member“ | im CE vorhanden (nur Cloud-Gating): Rolle Guest 5, `guest_view_all_features`, ohne Kontingent | Funktion portieren (über A03); Kontingent entfällt | R1 Z. 706; B9; R22; W18 |
| P08-15 | Approvals (Workspace-, Projekt-, Work-Item-Type-Approvals durch „designated admins“) | Business (Matrix, Coming soon); 2026 Workflow-Approvals Enterprise Grid (Dok. 25 F03) | Business/Enterprise ✓ | fehlt (Icon `ApproverOutline`, Upsell-Text) | portieren (Spezifikation fehlt, O4) | R1 Z. 717; R2 Z. 18; R27; Dok. 25 F03/F08 |
| P08-16 | Admin Interface (Admin-Übersicht über Workspace- und Projekteinstellungen) | Business | Business/Enterprise ✓ | fehlt (CE: Workspace-Settings nur für Admin/Member, keine projektübergreifende Admin-Übersicht) | portieren (Spezifikation fehlt, O5) | R1 Z. 729; W10 (W, sekundär) |
| P08-17 | Workspace Activity Logs (filterbar, ganzer Workspace) | Business | Business/Enterprise ✓ | teilweise im CE (Aktivität je User: `GET /api/workspaces/{slug}/user-activity/{user_id}/` + Export; No-op `mutateWorkspaceMembersActivity`) | portieren | R1 Z. 740; R24; R25 |
| P08-18 | API-enabled Audit Logs (Workspace-Audit-Log in Settings + v2-API `audit-logs`) | **Enterprise Grid** (Verifikation, vorher Business): Doku-Seitentitel „Workspace Audit Logs Enterprise Grid“ (W15); Matrix Business (Coming soon, älterer Stand); Cloud „Business Plus“ (D12); seit Commercial v3.1.0 ausgeliefert (W5) | Matrix Business/Enterprise ✓ (CS); **Widerspruch** zu Dok. 21 F34 und Dok. 22 P03-F44 (dort Matrix „Business“ beibehalten) – spezifischere Doku-Seite gewinnt | fehlt | portieren | R1 Z. 751; `self-hosting-101.md` Z. 42; D20; D23; W4–W6, W15 (W) |
| P08-19 | Workspace-Lizenz & Billing-Seite (Activate this workspace, Lizenzschlüssel, Sync plan, Delink, Billable seats, Manage subscription, Trial 14 Tage Business, Plan-Vergleich) | Commercial Edition (Mechanik aller Bezahlpläne) | Pro/Business workspace-gebunden | Stub/UI-Hülle im CE (Billing-Seite nur mit Plan-Vergleich; Upgrade-Modal; Editions-Badge) | entfällt (ADR-001) | D8; D11; D12; B8; B9; R4; R6; R26; R27; R28 |
| P08-20 | Enterprise-Grid-Instanzlizenz (God Mode → Billing „Activate Enterprise license“) | Enterprise Grid | gilt für alle Workspaces der Instanz | fehlt | entfällt (ADR-001) | D9; B7 |
| P08-21 | Offline-Lizenzdatei (Airgapped; `.json`-Upload in Workspace bzw. God Mode) | Airgapped Edition (Pro/Business: D10 `activate-airgapped.md`; Enterprise Grid: `activate-airgapped-enterprise.md`) | – | fehlt | entfällt (ADR-001) | D10; B7; B8 |
| P08-22 | Prime-Portal & Monitor-Dienst (Lizenzvalidierung, Feature-Flag-Resync alle 300 min, Health-Prober alle 5 min, `MACHINE_SIGNATURE`) | Commercial Edition | – | Stub/UI-Hülle im CE (Verifikation, vorher teilweise): Enum `InstanceEdition` nur `PLANE_COMMUNITY`, Typ-Altfelder `license_key`/`is_activated`/`user_count`; `MACHINE_SIGNATURE` wird im CE anders berechnet als im EE-Chart und nur auf Präsenz geprüft (keine Lizenzprüfung erreichbar) | entfällt (ADR-001); Health-Checks siehe Dok. 22 | D15; H1–H3; R10; R30; Dok. 22 Verifikations-Protokoll |
| P08-23 | Self-hosted-Pläne & Deployment-Varianten: One (Legacy), One-click/DO/Heroku/AWS AMI, Airgapped (≥ 100 Seats), Private/Managed Deployments, FIPS-140-3-Images | One (Deployment-Apps); Enterprise (Private deployments, Coming soon); Enterprise Grid (Airgapped, FIPS) | siehe Kap. 2.4 | teilweise im CE (Docker Compose, Kubernetes, Swarm, AIO unter `deployments/`; `restore-airgapped.sh`) | Airgapped = Grundeigenschaft (ADR-004); FIPS = Betriebsprofil; Private/Managed, Marktplatz-Apps entfallen. In `_data/P08.paid.json` in vier Einträge P08-23a (One/Installationskanäle, One), P08-23b (Airgapped, Enterprise Grid, teilweise), P08-23c (FIPS, Enterprise Grid, fehlt), P08-23d (Private/Managed, Enterprise, fehlt) aufgeteilt (Verifikation) | R1 Z. 1131–1202; R34; D13; D14 |
| P08-24 | Member-Limits & Seat-Berechnung (Cloud Free 12; Commercial Free 12 Seats/Workspace; Self-hosted-Richtwerte ~50/~200/Unlimited; Billable seats = User mit bezahlten Rollen; Agents nicht billable) | Pro (Aufhebung der Mitgliedergrenze; Free/One begrenzt; Verifikation präzisiert) | Cloud: Free 12, Pro+ Unlimited; Self-hosted: ~50/~50/~200/~200/Unlimited | im CE vorhanden (nur Cloud-Gating): CE hat kein Mitgliederlimit (entspricht „Unlimited“); Seat-Berechnung/-Abrechnung fehlt und entfällt (Verifikation: Wert an die Legende und an Dok. 20 PF-55 angeglichen, vorher „im CE ohne Limit“) | entfällt (ADR-001) | R1 Z. 676; D12; D18; D21; B8; B9 |
| P08-25 | Storage-Limits (Workspace-Speicher, Max file size je Plan) | Cloud-only | Free 5GB/5 MB; Pro 1 TB/100 MB; Business 5 TB/200 MB; Enterprise Custom | teilweise im CE (`FILE_SIZE_LIMIT` instanzweit, Default 5 242 880 Byte) | Instanz-Einstellung (Max file size); Speicherquote entfällt | R1 Z. 1032, 1043; R31 |
| P08-26 | Support-Kanäle, SLA, „Chat with us“ | Pro (SLA); Kanäle gestaffelt | Free Forum; One Mail+Forum; Pro Mail+Forum+Chat; Business/Enterprise „Full-suite professional services“ | Stub/UI-Hülle im CE (Verifikation, vorher teilweise): ungenutztes Modellfeld `Instance.is_support_required` und Typfeld `IInstance.is_support_required`, keine UI | entfällt (Vertrieb; ADR-004: kein externer Chat) | R1 Z. 1209, 1235; R10; B11; D5 |
| P08-27 | God Mode → User Management (alle Instanz-User, Instanz-Admins einladen, Admin-Rechte vergeben/entziehen, User entfernen) | Commercial Edition (kein Plan-Badge) | – | teilweise im CE (`InstanceAdmin`-Modell, `GET/POST /api/instances/admins/`; keine UI; `is_password_reset_required` ungenutzt) | portieren | D5; D7; B10; R10; R12; R13 |
| P08-28 | God Mode → Session-Einstellungen (Session expiry Tage, Admin session expiry Stunden) | Commercial Edition | – | teilweise im CE (nur ENV `SESSION_COOKIE_AGE`, `ADMIN_SESSION_COOKIE_AGE`) | portieren | D6; R31 |
| P08-29 | Argus – Sensitive-Data-/PII-Scanner | unklar (Feature-Flag `PII_SCANNER`); Changelog v3.2.0 „PII scanning“ (W9, sekundär) | – | fehlt (nur Propel-Icon `PiiScannerOutline`/`PiiScannerFilled`, R32; Verifikation ergänzt) | portieren (Umfang UNVERIFIZIERT, O9) | H1 Z. 700–720; H4; W9; Dok. 22 P03-F33 |
| P08-30 | IdP-Profil-Sync beim Login (`ENABLE_GOOGLE_SYNC`, `ENABLE_GITHUB_SYNC`, `ENABLE_GITLAB_SYNC`, `ENABLE_GITEA_SYNC`) – Basis für SSO-/LDAP-Profilabgleich | kein Bezahl-Feature | – | im CE vorhanden | portieren (Basis, A03/D05) | R14 (`adapter/base.py` `check_sync_enabled`, `sync_user_data`); R15 |
| P08-31 | Mitglieder-CSV-Import (Workspace, Projekt) mit Seat-Limit-Fehler | unklar (Dok. 20 PF-60) | – | fehlt (nur Texte R8, `project.members_import.*`) | portieren ohne Seat-Limit (Querbezug; gleiches Feature als P09-F32 in Dok. 28 – dort maßgeblich, hier nur Seat-Aspekt) | R8; `packages/i18n/src/locales/en/project.json` Z. 370 ff.; Dok. 28 P09-F32 |

---
## 4. Feature-Abschnitte

Konventionen: `{base}` = Instanz-Basis-URL (`WEB_URL`), API-Präfix der CE-Auth-Routen ist `/auth/` (`apps/api/plane/authentication/urls.py`, eingebunden in `apps/api/plane/urls.py`). „Vorschlag (UNVERIFIZIERT)“ kennzeichnet Entwurfsentscheidungen ohne öffentlichen Beleg; sie dürfen von den Architektur-Dokumenten (D05, D13c laut Workflow-Plan) überschrieben werden.

### 4.1 Authentifizierung & Identität

#### P08-01 – SAML-SSO (instanzweit)

**Funktionsbeschreibung (UI & Verhalten)**

- **Ort:** God Mode → „Authentication“ (`/god-mode/authentication/`). Die Liste „Available authentication modes“ der CE (Karten „Unique codes“, „Passwords“, „Google“, „GitHub“, „GitLab“, „Gitea“; R18 `apps/admin/hooks/oauth/core.tsx`) wird in der Commercial Edition um die Karten **„OIDC“**, **„SAML“**, **„LDAP“** (in dieser Reihenfolge, nach „Gitea“) erweitert (B4 `god-mode-authentication.webp`, `enable-ldap.webp`).
- **Karte SAML:** Icon SAML-Logo (Propel `Saml`, R32), Titel „SAML“, Beschreibung „Authenticate your users via the Security Assertion Markup Language protocol.“ (B4). Zustand **nicht konfiguriert**: Button „Configure“ (secondary, Einstellungs-Icon) wie CE-`GitlabConfiguration` (`apps/admin/components/authentication/gitlab-config.tsx`). Zustand **konfiguriert**: Link „Edit“ (unterstrichen, Akzentfarbe) + Switch (an/aus) (B4).
- **Konfigurationsseite** `/god-mode/authentication/saml` (Breadcrumb „Settings › Authentication › SAML“; B2):
  - Kopf: rundes Icon, Titel „SAML“, Untertitel „Authenticate your users via Security Assertion Markup Language protocol.“, rechts Switch (Aktivierung).
  - Linke Spalte „IdP-provided details for Plane“ (Formularfelder in dieser Reihenfolge, Platzhalter und Hilfetexte wörtlich aus B2):

    | Feld | Typ | Platzhalter | Hilfetext | Pflicht |
    |---|---|---|---|---|
    | Entity ID | Text | `70a44354520df8bd9bcd` | „A unique ID for this Plane app that you register on your IdP“ | ja (D1: „Copy the `ENTITY_ID` …“) |
    | SSO URL | Text (URL) | `https://example.com/sso` | „The URL that brings up your IdP's authentication screen when your users click the **Continue with** button“ | ja |
    | Logout URL | Text (URL) | `https://example.com/logout` | „Optional field that tells your IdP your users have logged out of this Plane app“ | nein |
    | IdP's name | Text | `Okta` | „Optional field for the name that your users see on the **Continue with** button“ | nein |
    | SAML certificate | Textarea | `---BEGIN CERTIFICATE---\n2yWn1gc7DhOFB9\nr0gbE+\n---END CERTIFICATE---` | „IdP-generated certificate for signing this Plane app as an authorized service provider for your IdP“ | ja (D1: „you have to copy the signing certificate from the IdP“) |

    Buttons: „Save changes“ (primary), „Go back“ (secondary) – identisch zum CE-Formular (`apps/admin/app/(all)/(dashboard)/authentication/gitlab/form.tsx` Z. 206, 214).
  - Rechte Spalte „Plane-provided details for your IdP“: graue Kästen **„WEB“** (Monitor-Icon) und **„MOBILE“** (Smartphone-Icon) mit Copy-Feldern (Muster CE `apps/admin/components/common/copy-field.tsx`: Button mit URL-Label + Copy-Icon, Toast „Copied to clipboard“):

    | Kasten | Label | Wert (B2) | Hilfetext (B2) |
    |---|---|---|---|
    | WEB | Entity ID \| Audience \| Metadata information | `{base}/auth/saml/metadata/` | „We will generate this bit of the metadata that identifies this Plane app as an authorized service on your IdP.“ |
    | WEB | Callback URI | `{base}/auth/saml/callback/` | „We will generate this **http-post request** URL that you should paste into your **ACS URL** or **Sign-in call back URL** field on your IdP.“ |
    | WEB | Logout URI | `{base}/auth/saml/logout/` | „We will generate this **http-redirect request** URL that you should paste into your **SLS URL** or **Logout URL** field on your IdP.“ |
    | MOBILE | Entity ID \| Audience \| Metadata information | `{base}/auth/mobile/saml/metadata/` | wie WEB |
    | MOBILE | Callback URI | `{base}/auth/mobile/saml/callback/` | wie WEB |
    | MOBILE | Logout URI | `{base}/auth/mobile/saml/logout/` | wie WEB |

    Dritter Kasten **„MAPPING“** (Icon Pfeile) mit Tabelle „IdP | Plane“: „Name ID format → emailAddress“, „first_name → user.firstName“, „last_name → user.lastName“, „email → user.email“ (B2; D1 Tabellen „Name ID format“ und „Set additional attribute values“).
  - i18n-Texte für dieselben Elemente (Workspace-Variante, P08-03) liegen in R3 `sso.providers.saml.*`: „Web details“, „Mobile details“, „Entity ID | Audience | Metadata information“, „SSO URL“, „SLO URL“, „Mapping details“ mit Spalten „IdP“/„Plane“.
- **Verhalten (D1):**
  - SP-initiiertes SSO; ACS mit **HTTP-POST-Binding**; Single Logout über SLS-URL (HTTP-Redirect laut B2).
  - „Plane does not need to provide a signing certificate like other service providers“ → AuthnRequests werden **nicht signiert**; die IdP-Antwort (Assertion/Response) wird mit dem hinterlegten IdP-Zertifikat geprüft.
  - Name-ID-Format `emailAddress`; Plane nutzt die E-Mail als Benutzernamen. Attribute `first_name`, `last_name` optional, `email` erforderlich; ohne Namen wird der Account nur mit E-Mail angelegt.
  - Der IdP-Name erscheint auf Login- und Sign-up-Screens (B3: Button „Sign up with Okta“ mit Schlüssel-Icon unter dem „or“-Trenner; B6 zeigt bei neuerem Stand SSO-Buttons **über** dem E-Mail-Feld).
  - Nach Konfiguration können sich auch **Instanz-Admins per SSO in God Mode anmelden** (D5 „Once SSO is configured, instance admins can also use SSO to log in to God Mode.“; Changelog v2.5.0 „SSO for God mode“, W8, sekundär).
  - Benutzeranlage beim ersten Login (Just-in-time) analog CE-OAuth (`Adapter.complete_login_or_signup`, R14): `ENABLE_SIGNUP == "0"` ohne Einladung → Fehler `SIGNUP_DISABLED` (5015); deaktivierte Konten (`last_logout_time` gesetzt) → `USER_ACCOUNT_DEACTIVATED` (5019); Bot-User → 5017. Passwort wird zufällig gesetzt, `is_password_autoset = true`, `is_email_verified = true` (CE-Logik für OAuth, `apps/api/plane/authentication/adapter/base.py` Z. 355–358).
  - FIPS-Profil: `SAML_REJECT_DEPRECATED_ALGORITHM` (FIPS-Default an, sonst aus) weist mit RSA-SHA1 signierte Assertions ab; IdP muss SHA-256 nutzen (D14 Tabelle „Configuration defaults specific to FIPS images“).

**Datenmodell-Hinweise**

- CE speichert Provider-Konfiguration als Schlüssel in `InstanceConfiguration(key, value, category, is_encrypted)` (R10). Helm-README bestätigt, dass in der Commercial Edition das **SAML-Zertifikat** und **OIDC-Client-Secrets** in dieser Tabelle liegen und nur beim ersten Start aus ENV geseedet werden (`SKIP_ENV_VAR=1`; H5).
- Konkrete Schlüsselnamen sind nicht öffentlich. Vorschlag (UNVERIFIZIERT), analog CE-Benennung `IS_GITLAB_ENABLED`/`GITLAB_CLIENT_ID` (R15 `auth.ts`): `IS_SAML_ENABLED`, `SAML_ENTITY_ID`, `SAML_SSO_URL`, `SAML_LOGOUT_URL`, `SAML_PROVIDER_NAME`, `SAML_CERTIFICATE` (verschlüsselt). Belegt ist nur die ENV `SAML_REJECT_DEPRECATED_ALGORITHM` (D14).
- `User.last_login_medium` (R12, `max_length=20`) erhält neuen Wert (Vorschlag `saml`); Typ `TExtendedLoginMediums = never` (R15) und `EXTENDED_LOGIN_MEDIUM_LABELS = {}` (R16) sind die vorgesehenen Erweiterungspunkte; Label erscheint in der CE-Mitgliederspalte „Authentication“ (R23 `useMemberColumns.tsx` Z. 113–119).
- `Account.PROVIDER_CHOICES` (R12: `google`, `github`, `gitlab`) enthält kein SAML; ein `Account`-Eintrag ist für SAML nicht nötig (keine Tokens), optional zur Verknüpfung `NameID` ↔ User (Vorschlag).

**API-Hinweise**

| Methode | Pfad | Zweck | Beleg |
|---|---|---|---|
| GET | `/auth/saml/` | Login initiieren (Redirect zum IdP); Query `next_path` wie CE-OAuth (`apps/web/hooks/oauth/core.tsx`) | D1 (Entity-ID-Basis), Analogie CE (UNVERIFIZIERT für Query) |
| POST | `/auth/saml/callback/` | ACS (HTTP-POST) | D1, B2 |
| GET/POST | `/auth/saml/logout/` | SLS | D1, B2 |
| GET | `/auth/saml/metadata/` | SP-Metadaten (Entity ID) | B2 |
| * | `/auth/mobile/saml/…` | Varianten für Mobile-App | B2 |
| * | `/auth/spaces/saml/…` | Variante für Space-App (öffentliche Boards) | Analogie CE `spaces/google/` (UNVERIFIZIERT) |

- Widerspruch: D1 nennt als Entity ID `http(s)://domain.tld/auth/saml/`, B2 zeigt `…/auth/saml/metadata/`. **Vorschlag:** Entity ID = Metadaten-URL `…/auth/saml/metadata/` (neuere UI), zusätzlich `/auth/saml/` als Initiierungs-Endpunkt.
- Konfiguration speichern über CE-Endpunkt `PATCH /api/instances/configurations/` (Instanz-Admin; `apps/api/plane/license/urls.py`).
- Fehlercodes: CE-Bereich 5104–5124 (OAuth) hat Lücken (5106–5109, 5113–5114, 5116–5119; R14 `adapter/error.py`). Vorschlag (UNVERIFIZIERT): `SAML_NOT_CONFIGURED`, `SAML_PROVIDER_ERROR`, `OIDC_NOT_CONFIGURED`, `OIDC_PROVIDER_ERROR`, `LDAP_NOT_CONFIGURED`, `LDAP_AUTHENTICATION_FAILED` in diese Lücken legen; Frontend-Mapping in `packages/utils/src/auth.ts` (`errorCodeMessages`).

**UI-Hinweise (Angular, 1:1)**

- God-Mode-Karte wiederverwendet das CE-Muster `AuthenticationMethodCard` (`apps/admin/components/authentication/authentication-method-card.tsx`) mit `name`, `description`, `icon`, `config`.
- Login-Buttons über den CE-Extension-Point `useExtendedOAuthConfig` (R17) → Eintrag `TOAuthOption { id: "saml", text: "{Sign in|Sign up} with {IdP's name}", icon: Schlüssel-Icon, onClick: location.assign("{API}/auth/saml/?next_path=…"), enabled }`. Aktionstext aus CE `auth-root.tsx` Z. 55 (`"Sign up"`/`"Sign in"`). Gleiches für Space (`apps/space/hooks/oauth/extended.tsx`).

**Migrationshinweis:** .NET: `Sustainsys.Saml2` oder `ITfoxtec.Identity.Saml2` (beide offline betreibbar, ADR-004). Immer aktiv (ADR-001).

**Quellen:** R1 Z. 1060; R2; R3 `sso.providers.saml.*`; R10; R12; R14–R18; D1; D5; D14; B2; B3; B4; H5; W8 (W, sekundär).
**Konfidenz:** hoch (UI/Felder/URLs aus Screenshots + Doku); mittel (Schlüsselnamen, Space-/Fehlercode-Details).

---

#### P08-02 – OIDC-SSO (instanzweit)

**Funktionsbeschreibung (UI & Verhalten)**

- **Karte OIDC** in God Mode → Authentication: Icon OIDC-Logo (Propel `Oidc`), Titel „OIDC“, Beschreibung „Authenticate your users via the OpenID Connect protocol.“; „Configure“ bzw. „Edit“ + Switch (B4).
- **Konfigurationsseite** `/god-mode/authentication/oidc` (Breadcrumb „Settings › Authentication › OIDC“; B1; D2 nennt `/god-mode/authentication/oidc`): Kopf „OIDC“ / „Authenticate your users via the OpenID connect protocol.“ + Switch.
  - Linke Spalte „IdP-provided details for Plane“:

    | Feld | Typ | Platzhalter (B1) | Hilfetext (B1) | Pflicht |
    |---|---|---|---|---|
    | Client ID | Text | `abc123xyz789` | „A unique ID for this Plane app that you register on your IdP“ | ja |
    | Client secret | Passwort mit Auge-Icon | `s3cr3tK3y123!` | „The secret key that authenticates this Plane app to your IdP“ | ja |
    | Authorize URL | Text (URL) | `https://example.com/` | „The URL that brings up your IdP's authentication screen when your users click the **Continue with**“ | ja |
    | Token URL | Text (URL) | `https://example.com/oauth/token` | „The URL that talks to the IdP and persists user authentication on Plane“ | ja |
    | Users' info URL | Text (URL) | `https://example.com/userinfo` | „The URL that fetches your users' info from your IdP“ | ja |
    | Logout URL | Text (URL) | `https://example.com/logout` | „Optional field that controls where your users go after they log out of Plane“ | nein |
    | IdP's name | Text | `Okta` | „Optional field for the name that your users see on the **Continue with** button“ | nein |

    Buttons „Save changes“, „Go back“.
  - Rechte Spalte „Plane-provided details for your IdP“, Kästen WEB und MOBILE:

    | Kasten | Label | Wert (B1) | Hilfetext (B1) |
    |---|---|---|---|
    | WEB | Origin URI | `{base}/auth/oidc/` | „We will generate this for this Plane app. Add this as a trusted origin on your IdP's corresponding field.“ |
    | WEB | Callback URI | `{base}/auth/oidc/callback/` | „We will generate this for you. Add this in the **Sign-in redirect URI** field of your IdP.“ |
    | WEB | Logout URI | `{base}/auth/oidc/logout/` | „We will generate this for you. Add this in the **Logout redirect URI** field of your IdP.“ |
    | MOBILE | Origin URI | `{base}/auth/mobile/oidc/` | wie WEB |
    | MOBILE | Callback URI | `{base}/auth/mobile/oidc/callback/` | wie WEB |
    | MOBILE | Logout URI | `{base}/auth/mobile/oidc/logout/` | wie WEB |

    D2 nennt dieselben drei Web-URLs (Tabelle „Origin URL / Callback URL / Logout URL“).
- **Verhalten (D2):** Authorization-Code-Flow mit den manuell eingetragenen Endpunkten (kein Discovery-Dokument-Feld; Werte stammen aus `.well-known/`). `email` ist Pflicht im Userinfo-Response; `first_name`/`last_name` optional. Login-Button „Login with {IdP name}“ bzw. „Sign up with {IdP name}“. Benutzeranlage/-sperren wie P08-01. Gruppen-Claim wird für P08-05 ausgewertet („group attribute key“; API-Beispielwert `groups`, UI-Platzhalter „Groups“ – ein Default-Wert ist nicht belegt; Verifikation korrigiert, vorher „Default `groups`“).

**Datenmodell-Hinweise:** wie P08-01; Vorschlag (UNVERIFIZIERT): `IS_OIDC_ENABLED`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` (verschlüsselt, laut H5 DB-resident), `OIDC_AUTHORIZE_URL`, `OIDC_TOKEN_URL`, `OIDC_USERINFO_URL`, `OIDC_LOGOUT_URL`, `OIDC_PROVIDER_NAME`. `Account`-Eintrag (`provider = "oidc"`, `access_token`, `refresh_token`, `id_token`) analog CE (R12) – Vorschlag.

**API-Hinweise:** `GET /auth/oidc/` (Initiierung, `next_path`), `GET /auth/oidc/callback/`, `GET /auth/oidc/logout/` (D2, B1); Mobile `/auth/mobile/oidc/…` (B1); Space-Variante `/auth/spaces/oidc/…` (UNVERIFIZIERT, Analogie). PKCE und `state`-Schutz wie CE (`apps/api/plane/authentication/utils/oauth_state.py`).

**UI-Hinweise:** wie P08-01 (Karte, Formular, Copy-Felder, Login-Button über `useExtendedOAuthConfig`).

**Migrationshinweis:** ASP.NET Core `AddOpenIdConnect` mit manuell konfigurierten Endpunkten (`Configuration` statt `Authority`/Discovery), offline-fähig.

**Quellen:** R1 Z. 1071; D2; D5; B1; B4; H5; R14; R17. **Konfidenz:** hoch.

---

#### P08-03 – Workspace-Identity: verifizierte Domains und Workspace-SSO

**Funktionsbeschreibung (aus den vollständigen EE-Texten R3 `sso.*`, R4 `identity.*`)**

- **Ort:** Workspace Settings → „Identity“ (`workspace_settings.settings.identity.title` = „Identity“, heading „Identity“, description „Configure your domain and enable Single sign-on“). Seitenkopf (R3): „Identity“ / „Configure your domain to access security features including single sign-on.“
- **Abschnitt „Domain management“ → „Verified domains“** („Verify the ownership of an email domain to enable single-sign on.“), Button „Add domain“. Liste mit Spalten „Domain name“, „Status“; Status-Werte „Verified“, „Failed“, „Pending“.
  - **Modal „Add domain“** („Add your domain to configure SSO and verify it.“): Feld „Domain“ (Platzhalter `plane.so`); Validierung „Domain is required“, „Enter a valid domain name (e.g., plane.so)“; Button „Add domain“ / Ladezustand „Adding“; Toasts „Success!“ + „Domain added successfully. Please verify it by adding the DNS TXT record.“ bzw. „Failed to add domain. Please try again.“
  - **Modal „Verify your domain“** („Follow these steps to verify your domain.“): Block „Instructions“ mit 4 Schritten: (1) „Go to the DNS settings for your domain host.“ (2) „Create a **TXT record** and paste the complete record value provided below.“ (3) „This update usually takes a few minutes but may take up to 72 hours to complete.“ (4) „Click "Verify domain" to confirm once your DNS record is updated.“; Felder „Domain“ und „TXT record value“ („Add this record to your DNS settings“, kopierbar); Buttons „Verify domain“ / „Verifying“ und „I'll do it later“; Toasts „Domain verified successfully.“ / „Failed to verify domain. Please try again.“
  - **Modal „Delete domain“**: „Are you sure you want to delete {domain}? This action cannot be undone.“; Buttons „Delete“/„Deleting“, „Cancel“; Toasts „Domain deleted successfully.“ / „Failed to delete domain. Please try again.“
- **Abschnitt „Single sign-on“**: Ohne verifizierte Domain deaktiviert mit Hinweis „Add a verified domain to configure SSO“. Zwei Provider-Zeilen:
  - „Enable SAML“ – „Configure your SAML identity provider to enable single sign-on.“
  - „Enable OIDC“ – „Configure your OIDC identity provider to enable single sign-on.“
  - Button je Zeile „Configure“ (neu) bzw. „Edit“ (vorhanden).
  - **Konfigurationsformular** (Modal/Seite „Enable SAML“ bzw. „Enable OIDC“, Beschreibung „Verify the ownership of an email domain to access security features including single-sign on.“): Abschnitt „IdP-provided details for {workspaceName}“; Abschnitt „{workspaceName} provided details for you IdP“ (Tippfehler „you“ im Original, 1:1 übernehmen) mit Button „Get setup details“; Setup-Details mit „Web details“/„Mobile details“ (SAML: „Entity ID | Audience | Metadata information“, „SSO URL“ – „Add this in the Sign-in redirect URL field of your IdP.“, „SLO URL“ – „Add this in the Single Logout redirect URL field“ bzw. mobil „Logout redirect URL field“; OIDC: „Origin URL“, „Redirect URL“, „Logout URL“) und bei SAML „Mapping details“ (Spalten „IdP“, „Plane“).
  - Aktionsbuttons: „Save“ (Default), „Save changes“, „Configure only“, „Configure and enable“, Ladezustand „Saving“.
  - Toasts SAML: „SAML provider created successfully.“ / „SAML provider updated successfully.“ / Fehler „Error!“ + „Failed to save SAML provider. Please try again.“; OIDC analog.
  - **Umschalt-Dialog** (genau ein aktiver Provider): Titel „Switch SSO Method to {newProviderShortName}?“, Text „You are about to enable {newProviderLongName} ({newProviderShortName}). This action will automatically disable {activeProviderLongName} ({activeProviderShortName}). Users attempting to sign in via {activeProviderShortName} will no longer be able to access the platform until they switch to the new method. Are you sure you want to proceed?“; Buttons „Switch“/„Switching“, „Cancel“.
- **Regeln (aus Texten ableitbar):** Domain-Status `pending → verified | failed`; SSO erst nach mindestens einer verifizierten Domain; je Workspace höchstens **ein** aktiver SSO-Provider; Aktivieren des anderen deaktiviert den bisherigen.
- **Ergänzung (Verifikation, W16, nur Suchzusammenfassung):** Die Domain-Verifizierung soll sicherstellen, dass nur berechtigte Admins SSO konfigurieren. **Eine Domain kann nur in einem Workspace gleichzeitig verifiziert sein**; ist sie anderswo verifiziert, muss sie dort zuerst entfernt werden → serverseitige Eindeutigkeit über alle Workspaces (nicht nur je Workspace). Eine Domain darf im Status „Pending“ bleiben; „Verify“ kann später erneut ausgelöst werden; DNS-Propagation kann Minuten dauern (Doku-Tipp `dig TXT yourdomain.com`).
- **Tier (Verifikation):** Business (Cloud) – plane.so/business listet „SSO on Cloud“ (W17). Schwach belegt (Suchzusammenfassung), Konfidenz mittel.
- **Nicht belegt (UNVERIFIZIERT):** Format des TXT-Werts, Recheck-Intervall, ob Login mit E-Mail einer verifizierten Domain automatisch an SSO weitergeleitet wird (Erzwingung), ob Workspace-SSO auch in Self-hosted angeboten wird (Dok. 22 P03-F06 markiert „unklar (Cloud)“).

**Datenmodell-Hinweise (Vorschlag, UNVERIFIZIERT):** `workspace_domains(id, workspace_id, domain citext, status enum pending|verified|failed, verification_token, last_checked_at, verified_at, created_by, created_at, updated_at)`, eindeutig `(workspace_id, domain)` und zusätzlich partiell eindeutig `(domain) WHERE status = 'verified'` (eine Domain nur in einem Workspace verifiziert, W16); `workspace_sso_providers(id, workspace_id, type saml|oidc, is_enabled, config jsonb verschlüsselt, created_at, …)`, Constraint „max. ein `is_enabled = true` je Workspace“.

**API-Hinweise (Vorschlag, UNVERIFIZIERT):** `GET/POST {W}/domains/`, `POST {W}/domains/{id}/verify/`, `DELETE {W}/domains/{id}/`, `GET/POST/PATCH {W}/sso-providers/…`, `POST {W}/sso-providers/{id}/enable/` (deaktiviert andere). Workspace-Admin-only.

**UI-Hinweise:** Workspace-Settings-Navigation (R29) um Eintrag „Identity“ in Kategorie `administration` ergänzen (Icon-Vorschlag `ShieldOutline` oder `LockKeyholeCircleOutline`, R32 – UNVERIFIZIERT).

**Migrationshinweis:** DNS-TXT-Prüfung per `DnsClient.NET`; in Airgapped-Umgebungen gegen internen DNS (ADR-004). Siehe offene Frage O1 (Verhältnis Instanz-SSO ↔ Workspace-SSO).

**Quellen:** R3 Z. 2–207; R4 Z. 253–257; W3 (W, sekundär); W16, W17 (W, Verifikation); Dok. 22 P03-F06. **Konfidenz:** hoch für UI-Texte; mittel für Domain-Eindeutigkeit und Tier; niedrig für übrige Backend-Semantik.

---

#### P08-04 – LDAP-Authentifizierung

**Funktionsbeschreibung (D3, B4, B5, B6)**

- **Ort:** God Mode → Authentication → Karte „LDAP“ (rotes LDAP-Logo, Beschreibung „Authenticate your users via LDAP directory services.“) ganz unten; „Configure“ → Seite; nach Konfiguration „Edit“ + Switch (B4).
- **Konfigurationsseite** `/god-mode/authentication/ldap` (Breadcrumb „Settings › Authentication › LDAP“; B5): Kopf „LDAP“ / „Authenticate your users via LDAP directory services.“ + Switch.
  - Linke Spalte „IdP-provided details for Plane“:

    | Feld | Platzhalter (B5) | Hilfetext (B5) | Pflicht / Default (D3) |
    |---|---|---|---|
    | Server URI | `ldap://ldap.example.com:389` | „The URI of your LDAP server (e.g., ldap://ldap.example.com:389)“ | Pflicht; Format `ldap://host:389` oder `ldaps://host:636` |
    | Bind DN | `cn=admin,dc=example,dc=com` | „The distinguished name to bind to the LDAP server“ | Pflicht |
    | Bind Password | „Enter bind password“ (Auge-Icon) | „The password for the bind DN“ | Pflicht; „Plane encrypts and stores this securely in its database.“ |
    | User Search Base | `ou=users,dc=example,dc=com` | „The base DN to search for users“ | Pflicht |
    | User Search Filter | `(uid={username})` | „The LDAP filter to find users (e.g., (uid={username}))“ | optional, Default `(uid={username})`; `{username}` = Eingabe im Login |
    | User Attributes | (unterhalb sichtbar abgeschnitten) | – | optional, Default `mail,cn,givenName,sn`; empfohlen `mail,cn,givenName,sn,userPrincipalName,displayName` |
    | Provider Name | – | – | optional, Default `LDAP`; Button-Text „Sign in with [Provider Name]“ |

  - Rechte Spalte „Plane-provided details for your IdP“, nur Kasten „WEB“: Copy-Feld „Authentication Endpoint“ (Wert im Screenshot unkenntlich) mit Hilfetext „The endpoint where users authenticate with their LDAP credentials. Ensure your LDAP server is accessible from Plane. Standard ports: **389** for LDAP, **636** for LDAPS (LDAP over SSL).“
  - „Save changes“: „Plane will validate the connection to your LDAP server.“ (D3 Schritt 5).
- **Login (B6):** Button mit Schlüssel-Icon „Sign in with LDAP“ (bzw. Provider Name) über dem „or“-Trenner und dem E-Mail-Feld. Nach Klick (EE-Texte R3): Kopf „Continue with {ldapProviderName}“, Unterzeile „Enter your {ldapProviderName} credentials“; Felder „Username“ (Platzhalter „Enter your username“, `auth.common.username.*`) und Passwort (`auth.common.password.*`).
- **Ablauf (D3 „How LDAP authentication works“):** (1) Verbindung zur Server URI, Bind mit Bind DN/Password – scheitert das, kann sich niemand anmelden; (2) Suche ab User Search Base mit Filter (`{username}` ersetzt); Ergebnis = DN des Users; (3) zweiter Bind mit User-DN + eingegebenem Passwort = Passwortprüfung; Plane speichert **keine** LDAP-Passwörter; (4) Attribute lesen: E-Mail aus `mail`, sonst `userPrincipalName` (Pflicht), Vorname aus `givenName`, sonst erster Teil von `cn`, Nachname aus `sn`, sonst letzter Teil von `cn`; erster Login legt Profil an, spätere Logins **aktualisieren** es; (5) Session wie jede andere Plane-Session.
- Filterbeispiele (D3): `(sAMAccountName={username})`, `(userPrincipalName={username})`, `(mail={username})`, `(|(uid={username})(mail={username}))`, Gruppenbeschränkung `(&(uid={username})(memberOf=cn=plane-users,ou=groups,dc=company,dc=com))`.
- TLS: `LDAP_TLS_REQUIRE_CERT` (Standard `never`, FIPS-Images `demand`; D14). Eigene CA über `customCA`-Mechanismus (H1 Z. 22–29).

**Datenmodell-Hinweise:** DB-resident (`LDAP_BIND_PASSWORD` in `InstanceConfiguration`, H5). Vorschlag (UNVERIFIZIERT): `IS_LDAP_ENABLED`, `LDAP_SERVER_URI`, `LDAP_BIND_DN`, `LDAP_BIND_PASSWORD` (belegt), `LDAP_USER_SEARCH_BASE`, `LDAP_USER_SEARCH_FILTER`, `LDAP_USER_ATTRIBUTES`, `LDAP_PROVIDER_NAME`, `LDAP_TLS_REQUIRE_CERT` (belegt). `last_login_medium = "ldap"` (Vorschlag).

**API-Hinweise:** Endpunkt „Authentication Endpoint“ (Pfad im Screenshot unkenntlich; Vorschlag `POST /auth/ldap/sign-in/` mit `username`, `password`, `next_path`; UNVERIFIZIERT). Fehler bei falschen Credentials analog `AUTHENTICATION_FAILED_SIGN_IN` (5065).

**UI-Hinweise:** Karte, Seite und Login-Button wie P08-01; zusätzlicher Login-Schritt „LDAP-Credentials“ im Auth-Root (CE `apps/web/components/account/auth-forms/auth-root.tsx` verwendet `EAuthSteps` EMAIL/PASSWORD/UNIQUE_CODE – neuer Schritt nötig).

**Migrationshinweis:** `System.DirectoryServices.Protocols` (plattformübergreifend, LDAPS); Rate-Limit wie CE-Login (`apps/api/plane/authentication/rate_limit.py`).

**Ergänzung (Verifikation, W22):** Laut GAC-/LDAP-Blog (10.06.2026) werden Active Directory, OpenLDAP, FreeIPA und jeder LDAP-kompatible Server unterstützt; Tier Enterprise Grid bestätigt.

**Quellen:** R1 Z. 1117; R2 Z. 10; R3 Z. 278–281, 361–366; D3; D14; B4; B5; B6; H1; H5; W22. **Konfidenz:** hoch.

---

#### P08-05 – IdP Group Sync

**Funktionsbeschreibung**

- **Ort:** Workspace Settings → „Group syncing“ (`workspace_settings.settings.group_syncing.title`). Seitenkopf „Group syncing“ – „Link identity provider groups to projects and roles. User access updates automatically when group membership changes in your IdP, simplifying onboarding and offboarding.“ (R4).
- **Schalter** „Enable group syncing“ – „Automatically add users to projects based on identity provider groups.“; Toasts „Updating group syncing feature“, „Group syncing feature updated successfully.“, „Failed to update group syncing feature!“
- **Block „Configure group sync“** – „Set up how identity provider groups are mapped to projects and roles.“:
  - „Sync on login“ – „Update group membership and project access when a user signs in.“ (API-Default `true`, D17)
  - „Offline sync“ – „Runs sync every six hours automatically, without waiting for users to log in.“ (Default `false`)
  - „Auto remove“ – „Automatically remove users from projects when they no longer match the group.“ (Default `false`)
  - „Group attribute key“ – „The identity provider attribute used to identify and sync user groups.“, Platzhalter „Groups“ (API-Beispiel `groups`)
- **Block „Group mapping“** – „Link identity provider groups to projects and roles.“, Button „Add new group sync“; Leerzustand „No group mappings yet“ (R5) mit Illustration `group-syncing` (R33).
- **Modal (Mapping anlegen/bearbeiten):** „User group“ (Platzhalter „Enter the IdP group names“, Fehler „User group is required“), „Project“ („Select a project“, „Project is required“), „Project role“ („Select a project role“, „Project role is required“).
- **Lösch-Modal:** „Delete group sync“ – „New users from this identity group will no longer be added to the project. Users already added will keep their current role.“
- **Semantik (D17 `overview.md`):** Config-Objekt `is_enabled`, `sync_on_login`, `auto_remove` („remove users from projects/workspace when they are removed from the IdP group“), `sync_offline`, `group_attribute_key`, `default_workspace_role` (Rollen-**Slug**, z. B. `member`). Projekt-Mapping `idp_group_name`, `project` **xor** `all_projects`, `role` (Projektrollen-Slug). Workspace-Mapping `idp_group_name`, `role` (Workspace-Rollen-Slug, z. B. `admin`). Alle Endpunkte workspace-scoped, nur Workspace-Admins. Laut Doku-Snippet nur Commercial Self-hosted und nur OIDC (Gruppen-Claim), SAML/LDAP „coming soon“ (W1, sekundär; Dok. 21 §4.8).
- **Abgeleitete Regeln:** Beim Login (OIDC) Gruppen aus Claim `group_attribute_key` lesen → Workspace-Mitgliedschaft mit Rolle aus Workspace-Mapping bzw. `default_workspace_role` sicherstellen → je Projekt-Mapping (oder alle Projekte) Projektmitgliedschaft mit Rolle anlegen. `auto_remove` entfernt Projektzugänge, wenn keine Gruppe mehr passt. Mapping löschen entzieht **keine** bestehenden Zugänge (Lösch-Text).
- **Regeln aus dem GAC-/Group-Sync-Blog (Verifikation, W22, nur Suchzusammenfassung, mittel):**
  - Mehrere passende Gruppen → der Nutzer erhält die **höchste** passende Rolle.
  - **Manuell vergebene Rollen werden nie herabgestuft.**
  - Beim Entfernen (Auto remove) bleibt die **Workspace-Mitgliedschaft immer erhalten**; **alleinige Projekt-Admins** und **manuell hinzugefügte Mitglieder** werden nie aus Projekten entfernt. (Präzisiert die Aussage der v1-Doku „remove users from projects/workspace“, D17, für die Projektebene; Widerspruch bzgl. Workspace dokumentiert – Blog ist spezifischer.)
  - Default-Rolle je Projekt-Mapping: Admin, Member oder Guest.
- **v2-Abweichung (Verifikation, D23 `group-sync/overview.md`):** Das Config-Feld heißt in v2 `default_workspace_role_slug` (v1: `default_workspace_role`); Pfade `/api/v2/workspaces/{slug}/group-sync/config/`, `…/project-mappings/`, `…/workspace-mappings/` (je List/Create/Get/Patch/Delete; Config nur Get/Patch); Scopes `workspaces.group_sync:read`, `workspaces.group_sync:write` (D23 `authentication.md` Z. 283–284).
- **Nicht belegt (UNVERIFIZIERT):** Verhalten von Offline-Sync ohne IdP-API (Dok. 21 O12).

**Datenmodell- und API-Hinweise:** vollständig in Dok. 21 §2.6 (G1–G12) und §4.8; Scopes `workspaces.group_sync:read/write`. G1 legt die Config bei erstem Zugriff mit Defaults an. Zusätzliche Spalten aus den Blog-Regeln: Projekt-/Workspace-Mitgliedschaften brauchen eine Herkunftsmarkierung (`source = manual | group_sync`, Vorschlag), damit „manuell vergebene Rollen nie herabstufen“ und „manuell hinzugefügte Mitglieder nie entfernen“ durchsetzbar sind.

**UI-Hinweise:** Settings-Eintrag im Bereich „Administration“; Icon: Propel bietet ein eigenes `GroupSyncOutline`/`GroupSyncFilled` (R32; Verifikation – ersetzt den früheren Vorschlag `UserCogOutline`; Zuordnung zum Settings-Eintrag weiterhin UNVERIFIZIERT). Rollen-Dropdowns verwenden die Rollen-Slugs aus P08-11.

**Migrationshinweis:** Hook im OIDC-Callback; Hintergrundjob alle 6 h nur mit konfiguriertem Provider-Adapter (z. B. Keycloak-Admin-API, Microsoft Graph) – sonst Schalter „Offline sync“ deaktiviert anzeigen (Vorschlag, O6).

**CE-Status (Verifikation):** **fehlt** – `grep` nach `group_sync`/`group_syncing` außerhalb von `locales/` ohne Treffer; vorhanden sind nur die Illustration `GroupSyncingHorizontalStackIllustration` (registriert in `packages/blocks/src/empty-state/assets/asset-registry.tsx` Z. 75–77 und `asset-types.ts` Z. 14, nirgends verwendet) und das Propel-Icon.

**Quellen:** R4 Z. 192–252; R5; R32; R33; D17; D23; Dok. 21; W1, W2 (W, sekundär); W22 (W, Verifikation). **Konfidenz:** hoch (UI/API); mittel (Ablaufregeln).

---

#### P08-06 – SCIM-Provisioning

**Funktionsbeschreibung:** Nur Nennungen: „Audit logs, SCIM, advanced auth – Cloud: Business Plus – Self-hosted: Available on plans (Commercial and Airgapped)“ (`/home/user/makeplane/developer-docs/docs/self-hosting/self-hosting-101.md` Z. 42); Whitepaper-Snippet „LDAP, SCIM, IdP group synchronization, custom roles … Enterprise Grid“ (Dok. 20 PF-98, W12, sekundär); Drittquelle W13 (sekundär). Keine UI-Texte im CE, keine API-Referenz in D.

**Datenmodell/API (Vorschlag, UNVERIFIZIERT):** SCIM 2.0 (RFC 7643/7644) `/scim/v2/Users`, `/scim/v2/Groups` je Workspace oder Instanz mit Bearer-Token; Users → `User` + `WorkspaceMember`, Groups → Eingabe für P08-05-Mappings. `User.is_managed` (R12, im CE ungenutzt außer im Serializer `apps/api/plane/app/serializers/user.py` Z. 55) ist ein möglicher Marker „vom IdP verwaltet“ (UNVERIFIZIERT).

**Quellen:** D12; W12, W13. **Konfidenz:** niedrig.

---
### 4.2 Kontoschutz

#### P08-07 – Zwei-Faktor-Authentifizierung (2FA)

**Funktionsbeschreibung (belegbar):** Einziger öffentlicher Beleg im Offline-Bestand ist die Matrix-Zeile „Two-factor authentication and passkeys – Secure your Plane workspace with device-dependent two-factor authentication and passkeys.“ (R1 Z. 1095–1104; Pro, Business, Enterprise). Im CE gibt es **keine** Texte, Typen, Felder oder Routen zu 2FA (grep nach `two_factor|2fa|totp|mfa|otp` in `apps/`, `packages/` ohne Treffer außer R1).

**Ableitungen aus dem Wortlaut:**
- „device-dependent“ → zweiter Faktor an ein Gerät gebunden (Authenticator-App/TOTP oder Plattform-Authenticator).
- „Secure your Plane **workspace**“ → Workspace-bezogene Komponente (z. B. Erzwingung für alle Mitglieder eines Workspaces) – **UNVERIFIZIERT**.

**Vorschlag (UNVERIFIZIERT) für die Portierung:**
- Benutzerseitige Einrichtung in Profil-Einstellungen → „Security“ (CE-Tab `security`, Icon `LockOutline`; R20 `packages/constants/src/settings/profile.ts`, `apps/web/components/settings/profile/sidebar/item-categories.tsx`), unterhalb „Change password“: Abschnitt „Two-factor authentication“ mit „Enable“ → QR-Code + manueller Schlüssel → 6-stelliger Code bestätigen → 10 Recovery-Codes anzeigen/herunterladen; „Disable“ (mit Passwort/Code-Bestätigung); „Regenerate recovery codes“.
- Login: nach erfolgreichem Passwort-/Magic-Code-Schritt zusätzlicher Schritt „Code eingeben“ (neuer `EAuthSteps`-Wert, CE `packages/constants/src/auth/index.ts` Z. 64–68). Für SSO/LDAP-Logins (P08-01…04) **keine** zusätzliche 2FA (IdP verantwortlich) – UNVERIFIZIERT.
- Workspace-Admin-Schalter „Require two-factor authentication for all members“ (Workspace Settings → Identity/Security); Mitglieder ohne 2FA werden beim Öffnen des Workspaces zur Einrichtung gezwungen – UNVERIFIZIERT.
- God-Mode-Admin-Login (`/api/instances/admins/sign-in/`) ebenfalls 2FA-fähig – UNVERIFIZIERT.

**Datenmodell-Hinweise (Vorschlag):** `user_two_factor(user_id PK, totp_secret verschlüsselt, enabled_at, last_used_step)`, `user_recovery_codes(id, user_id, code_hash, used_at)`, `workspaces.require_two_factor bool`. ASP.NET Core Identity bietet `AuthenticatorKey`/`RecoveryCodes` nativ (Greenfield, ADR-003).

**API-Hinweise (Vorschlag):** `POST /api/users/me/2fa/setup/` → `{secret, otpauth_uri}`; `POST /api/users/me/2fa/verify/` `{code}` → `{recovery_codes}`; `DELETE /api/users/me/2fa/`; `POST /auth/2fa/` `{code | recovery_code}` im Login-Flow; neue Fehlercodes im freien Bereich (z. B. 5026–5029) – UNVERIFIZIERT.

**Warnung (Verifikation):** Websuchen nach „Plane 2FA/Passkeys“ liefern Hilfeartikel und Changelogs von `help.plane.com` bzw. `docs.plane.com` (TOTP mit Recovery-Codes, „Verify code and activate“, Passkey-Anlage bei Registrierung, Geräte-Sessions). Diese gehören zu einem **anderen Unternehmen** (Plane, Lohn-/Zahlungsplattform; W23) und dürfen **nicht** als Spezifikation für makeplane/Plane verwendet werden. Für makeplane/Plane bleibt die Matrix-Zeile der einzige Beleg.

**Quellen:** R1 Z. 1095; R20; W23 (Ausschluss). **Konfidenz:** Tier mittel (nur Matrix, keine Doku-Seite gefunden); Funktionsdetails niedrig (O2).

---

#### P08-08 – Passkeys

**Funktionsbeschreibung (belegbar):** Gleiche Matrix-Zeile wie P08-07 (R1 Z. 1095; Pro+). Keine CE-Spuren.

**Vorschlag (UNVERIFIZIERT):** WebAuthn/FIDO2-Passkeys als (a) passwortloser Login-Weg („Sign in with passkey“ als `TOAuthOption`-ähnlicher Button über `useExtendedOAuthConfig`, R17) und (b) zweiter Faktor. Verwaltung in Profil → Security: Liste „Passkeys“ (Name, erstellt am, zuletzt genutzt), „Add passkey“, „Rename“, „Remove“.

**Datenmodell (Vorschlag):** `user_passkeys(id, user_id, credential_id bytea unique, public_key bytea, sign_count bigint, aaguid uuid, transports text[], name, created_at, last_used_at)`. ASP.NET Core 10 Identity enthält Passkey-Unterstützung (`IdentityPasskeyData`) – im Architektur-Dokument D05 zu prüfen.

**API (Vorschlag):** `POST /auth/passkeys/register/options/`, `POST /auth/passkeys/register/`, `POST /auth/passkeys/login/options/`, `POST /auth/passkeys/login/`, `GET/PATCH/DELETE /api/users/me/passkeys/{id}/`.

**Quellen:** R1 Z. 1095. **Konfidenz:** Tier hoch; Details niedrig (O2).

---

#### P08-09 – Password Policy

**Funktionsbeschreibung (belegbar):** „Set custom password policies in line with your compliance requirements.“ (R1 Z. 1106–1115; Pro+). Keine EE-Texte im CE.

**CE-Ausgangslage (vollständig, wird über A03/D05 portiert):**

| Stelle | Regel | Quelle |
|---|---|---|
| Backend Sign-up/Set/Reset/Change | `is_password_strong(password)`: zxcvbn-Score ≥ 3 auf den ersten **und/oder** letzten 128 Zeichen (Fenster-Menge; stark, wenn eines der Fenster stark ist); sonst `PASSWORD_TOO_WEAK` (5021) | `apps/api/plane/authentication/utils/password.py` Z. 10–15; `apps/api/plane/authentication/adapter/base.py` Z. 88–97, 363 |
| Weitere Aufrufstellen (Verifikation, vollständig per `grep is_password_strong`) | Passwort ändern/setzen (`apps/api/plane/authentication/views/common.py` Z. 86, 124), Passwort-Reset Web (`apps/api/plane/authentication/views/app/password_management.py` Z. 145) und Space (`apps/api/plane/authentication/views/space/password_management.py` Z. 139), **God-Mode-Admin-Sign-up** (`apps/api/plane/license/api/views/admin.py` Z. 197), Management-Command `reset_password` (`apps/api/plane/db/management/commands/reset_password.py` Z. 54) | dto. – alle Stellen müssen eine konfigurierbare Policy anwenden |
| Frontend Web/Admin | `getPasswordStrength`: leer → `EMPTY`; `< 8` → `LENGTH_NOT_VALID`; Groß- **und** Kleinbuchstabe **und** Ziffer **und** Sonderzeichen `[!@#$%^&*()\-_+=\[\]{}\|;:'",.<>?/]` → `STRENGTH_VALID`, sonst `STRENGTH_NOT_VALID` | `packages/utils/src/auth.ts` Z. 26–46 |
| Kriterienliste (Indikator) | „Min 8 characters“, „Min 1 upper-case letter“, „Min 1 lower-case letter“, „Min 1 number“, „Min 1 special character“ | `packages/utils/src/auth.ts` Z. 57–83; `packages/blocks/src/auth/password/indicator.tsx` |
| Space-App | nur „Min 8 characters“ (`SPACE_PASSWORD_CRITERIA`, weitere Kriterien auskommentiert) | `packages/constants/src/auth/index.ts` Z. 18–41 |
| Ungenutzte Modellfelder | `User.is_password_expired` (seit 0001), `User.is_password_reset_required` (seit Migration 0116) – im CE nirgends gelesen/geschrieben | R12; R13 |

**Vorschlag (UNVERIFIZIERT) Policy-Umfang:** Mindestlänge (≥ 8), geforderte Zeichenklassen (Groß, Klein, Ziffer, Sonderzeichen), Mindest-zxcvbn-Score, Ablauf nach N Tagen (setzt `is_password_expired` → Zwang zum Ändern beim Login), Wiederverwendungssperre der letzten N Passwörter, „Passwortwechsel beim ersten Login erzwingen“ (`is_password_reset_required`, belegt als Funktion in God-Mode-Einladung, P08-27). Geltungsbereich: Instanz (God Mode) **oder** Workspace – UNVERIFIZIERT (Matrix sagt „your Plane workspace“ nur bei 2FA/LDAP).

**Datenmodell (Vorschlag):** `password_policies(scope instance|workspace, scope_id, min_length, require_upper, require_lower, require_digit, require_special, min_zxcvbn_score, expiry_days, history_count)`, `user_password_history(user_id, password_hash, created_at)`.

**UI-Hinweise:** Die CE-Kriterienanzeige (`PasswordStrengthIndicator`, R19/`packages/blocks/src/auth/password/*`) muss die konfigurierten Kriterien dynamisch rendern (gleiche Optik).

**Quellen:** R1 Z. 1106; R12–R14; R16; R19. **Konfidenz:** CE-Basis hoch; EE-Umfang niedrig (O3).

---

#### P08-10 – Domain Security

**Funktionsbeschreibung (belegbar):** „Choose other domains that can authenticate into your Plane workspace or restrict all but one domain.“ (R1 Z. 1083–1092; Pro+). Zwei Modi lassen sich ablesen: (a) **zusätzliche** zugelassene Domains festlegen, (b) **auf genau eine** Domain beschränken.

**CE-Ausgangslage:** keine Domain-Beschränkung für Workspaces. Verwandt: `Instance.whitelist_emails` (TextField, im CE ungenutzt außer Typ `IInstance.whitelist_emails`, R10, R15); GitHub-OAuth-Organisationsbeschränkung `GITHUB_ORGANIZATION_ID` mit Fehler `GITHUB_USER_NOT_IN_ORG` (5122) (R14, R15 `auth.ts`).

**Vorschlag (UNVERIFIZIERT):** Workspace-Einstellung „Allowed email domains“ (Liste, Basis = verifizierte Domains aus P08-03) + Modus „Allow these domains“ / „Only primary domain“. Durchsetzung bei: Einladung (`POST {W}/invitations/` → 400), Annahme/Join (`POST {W}/invitations/{pk}/join/`, `POST /api/users/me/workspaces/invitations/`), CSV-Import (P08-31), Group-Sync-Provisionierung (P08-05); Bestandsmitglieder außerhalb der Domains: nicht automatisch entfernt (Vorschlag). Gäste ggf. ausgenommen (Gast-Definition „External members of organizations“, R7 `role_details.guest.description`) – UNVERIFIZIERT.

**Datenmodell (Vorschlag):** `workspace_domain_policies(workspace_id, mode allow_list|single_domain, domains text[])` oder Flag `is_allowed` an `workspace_domains` (P08-03).

**Quellen:** R1 Z. 1083; R10; R14; R15. **Konfidenz:** Tier hoch; Details niedrig (O3).

---

### 4.3 Rollen & Zugriff

#### P08-11 – Rollen: System-Rollen / RBAC (Business; Verifikation, vorher „Pre-defined Roles (Pro)“)

**Funktionsbeschreibung**
- Matrix: „Roles – Choose from one of four pre-defined roles or create custom ones with RBAC.“; Free/One „Basic“, Pro „Pre-defined roles“, Business „RBAC“ (R1 Z. 695–704).
- **Doku-Stand 2026 (Verifikation, W18, W20, nur Suchzusammenfassungen, mittel):**
  - Zwei Schichten: **RBAC ist Standard in jedem Workspace**; GAC (Custom Roles) ist ein Enterprise-Add-on (→ P08-12/P08-13).
  - **Owner, Member und Guest** gibt es auf **allen Plänen**; die übrigen System-Rollen (**Workspace Admin, Contributor, Commenter**) sind „exclusive to the Business plan and higher“. Die Rolle **Workspace Admin** ist neu und liegt **zwischen Owner und Member** (Business und Enterprise).
  - Umbenennungen (Changelog 2026-04-25): „Workspace Admin“ → **„Workspace Owner“**, „Project Member“ → **„Contributor“**; bestehende Zuweisungen wurden automatisch gemappt. Für das CE-Mapping heißt das: CE-Workspace-Rolle 20 entspricht **Owner**, CE-Projektrolle 15 entspricht **Contributor**.
  - **Owner** ist die höchste Workspace-Rolle mit Vollzugriff; nur der Owner darf den Workspace löschen und die Ownership übertragen.
  - **Commenter** = Lesen + Kommentieren + Intake einreichen; **Guest** (Projekt) = externe Mitarbeitende mit Interaktion über Intake (Wortlaut der Zusammenfassung; Abgleich mit der CE-Gastsemantik `guest_view_all_features` in P08-14 offen).
  - **Widerspruch:** „Contributor ab Business“ vs. „Project Member wurde zu Contributor umbenannt“ (dann wäre Contributor auch im Free-Plan vorhanden). UNVERIFIZIERT, siehe O8.
  - **Tier-Entscheidung:** Business (aktuellere Doku) statt Pro (Matrix „Pre-defined roles“).
- **v2-API (Verifikation, D23 `members/overview.md`):** `role` ist ein **Slug-String ohne Enum** („Roles are an open set“); als eingebaute Slugs genannt sind `owner`, `member`, `contributor` (eine vollständige Liste ist nicht dokumentiert); derselbe Nutzer kann im Workspace `member` und im Projekt `contributor` sein; `role = null` nur bei Altdaten vor Einführung der Slugs; v1 lieferte numerische Level (Vergleich `role >= 15`), v2 Slugs (Vergleich `role == "member"`).
- Rollenkatalog der Commercial Edition (D19 `mcp-server-tools.md` Z. 409–421): Rollen sind abfragbare Objekte (`list_roles` mit optionalem `namespace`, `retrieve_role` per `role_id`). Namespaces:
  - **`workspace`: Owner, Admin, Member, Guest**
  - **`project`: Admin, Contributor, Commenter, Guest**
  - „A role slug is stable but not globally unique -- key on (namespace, slug).“ Mitgliederlisten filtern per `role_slug`.
  - Rollen-Slugs in IdP-Group-Sync: Workspace `member`, `admin`; Projekt `member`, `admin`, `guest` (D17-Beispiele; Dok. 21 §4.8). **Widerspruch:** D17 nennt Projekt-Slug `member`, D19 den Anzeigenamen „Contributor“ → Slug der Contributor-Rolle vermutlich `member` (UNVERIFIZIERT, O8).
- „Four pre-defined roles“ = vier Rollen je Namespace.
- **Berechtigungsfragmente** aus der Permissions-Matrix (W7, sekundär, über Dok. 25/26 – vollständig wiedergegeben, was dort zitiert ist):

  | Bereich | Owner/Admin (Workspace) | Member (Workspace) | Projekt-Admin | Contributor | Commenter | Guest | Quelle |
  |---|---|---|---|---|---|---|---|
  | Workflows je Projekt | – | – | anlegen/bearbeiten/löschen | nur lesen | kein Zugriff | kein Zugriff | Dok. 25 Z. 234 |
  | Workspace-Automationen | sehen/anlegen/bearbeiten/(de)aktivieren/löschen | – | – | – | – | – | Dok. 25 Z. 586 |
  | Projekt-Templates | anlegen/veröffentlichen/bearbeiten/löschen | nur verwenden | – | – | – | – | Dok. 25 Z. 723 |
  | Work-Item-Templates | Workspace-Templates anlegen | – | Projekt-Templates anlegen/bearbeiten/löschen | sehen | – | – | Dok. 25 Z. 796 |
  | Private Projekte selbst beitreten | ja | nein | – | – | – | – | Dok. 25 Z. 449 |
  | Projektseiten | – | – | jede Seite | nur eigene | nicht (Export sichtbarer Seiten erlaubt) | nur eigene (Export eigener Seiten); kommentiert nur eigene Seiten; reagiert auf Kommentare, löst nicht auf | Dok. 26 Z. 409, 432, 520 |
  | Wiki-Seiten | jede Seite sperren/archivieren/wiederherstellen/löschen/verschieben/veröffentlichen | eigene; anlegen/duplizieren bei jeder | – | – | – | „Permission denied“ | Dok. 26 Z. 244 |
  | Seiten teilen | nur eigene | nur eigene | – | – | – | nein | Dok. 26 Z. 547 |

- **CE-Ausgangslage:** Integer-Rollen Admin 20 / Member 15 / Guest 5 auf Workspace- und Projektebene (`ROLE_CHOICES` R22; `EUserPermissions`, `EUserWorkspaceRoles`, `EUserProjectRoles` R21), numerische Vergleiche, Decorator `allow_permission`, Permission-Klassen – vollständig in `migration/analysis/03-api-intern-workspace-projekt-user.md` §2.4. Texte: Guest „External members of organizations can be invited as guests.“, Member „Ability to read, write, edit, and delete entities inside projects, cycles, and modules“, Admin „All permissions set to true within the workspace.“ (R7 `role_details.*`). `USER_ALLOWED_PERMISSIONS` enthält nur `workspace.dashboard.read` (R21 `packages/constants/src/user.ts`). CE kennt **keine** Owner-Rolle (nur Feld `Workspace.owner`) und **keine** Commenter-Rolle.

**Datenmodell-Hinweise (Vorschlag; Verifikation korrigiert):** `roles(id, workspace_id NULL für System-Rollen, namespace instance|workspace|project, slug, name, description, level, is_system, status, sort_order, created_at, updated_at)` – Felder `level`, `is_system`, `status`, `namespace` mit Wert `instance` laut v2-Rollen-Objekt (D23 `roles/overview.md`, `roles/list-roles.md`); eindeutig `(workspace_id, namespace, slug)`; `workspace_members.role_id`, `project_members.role_id`. Mapping der CE-Integer (korrigiert nach W18/W20): Workspace 20→`owner`, 15→`member`, 5→`guest`; Projekt 20→`admin`, 15→`contributor` (v2-Slug, D23; v1-Group-Sync-Beispiel nutzt `member`, siehe O8), 5→`guest`; neu: Workspace `admin` (zwischen Owner und Member), Projekt `commenter` (Slug-Vorschlag). Der CE-Wert `Workspace.owner` (Ersteller) ist nicht identisch mit der Owner-Rolle (mehrere Owner möglich? – UNVERIFIZIERT).

**API-Hinweise:** `GET {W}/roles/?namespace=`, `GET {W}/roles/{role_id}/` (D19); v2: `GET /api/v2/workspaces/{slug}/roles/` (Filter `is_system`, `namespace` ∈ `instance|workspace|project`, `slug`, `search`; Pagination `per_page` ≤ 200, `offset`, `paginate=cursor`, `count`; `fields` ∈ `description,id,is_system,level,name,namespace,slug,status`) und `GET …/roles/{pk}/`, Scope `workspaces.roles:read` („Read access to workspace roles (system + custom)“) (D23). Mitglieder-Filter `role_slug`, `is_active`, `is_bot` (D19 `list_workspace`). JSON-Feld `role` (Integer) der CE-Verträge bleibt für Contract-Kompatibilität parallel bestehen (Vorschlag; ADR-003). Workspace-Access-Tokens tragen ebenfalls eine Rolle („Use a workspace access token with the minimum role needed“, `DD/dev-tools/mcp-server.md` Z. 750) – Feature in Dok. 28 P09-F52.

**UI-Hinweise:** Rollen-Dropdowns in Mitgliederlisten (CE `apps/web/components/workspace/settings/member-columns.tsx` `ROLE_OPTIONS`) zeigen die Rollen-Namen des Namespaces; Settings-Header zeigt Rollentitel (CE `ROLE_DETAILS` in `apps/web/components/settings/workspace/sidebar/header.tsx` Z. 57).

**Quellen:** R1 Z. 695; R7; R21; R22; D17; D19; D23; W7 (W, sekundär); W18, W20, W21 (W, Verifikation); Dok. 03 §2.4. **Konfidenz:** Rollennamen hoch; Tier und Umbenennungen mittel; Rechte-Matrix mittel (nur Fragmente).

---

#### P08-12 – Custom Roles (Enterprise Grid; Verifikation, vorher „RBAC: benutzerdefinierte Rollen (Business)“)

**Funktionsbeschreibung (belegbar):**
- Matrix Business „RBAC“ zu „… or create custom ones with RBAC.“ (R1 Z. 695–704); `planHighlights.business` „RBAC“ (R1 Z. 1307). Keine EE-Texte im CE.
- **Doku-Stand 2026 (Verifikation, W19, W20, nur Suchzusammenfassungen, mittel):** Custom Roles gehören zu **GAC** („extends RBAC for Enterprise customers, unlocking custom roles composed of reusable permission schemes“) und sind **Enterprise Grid**. Ort: **Workspace settings → „Roles and permissions schemes“ → Tab „Roles“** (Workspace-Rollen); Projektrollen im selben Ablauf unter dem Tab **„Project“**. Eine Custom Role wird aus **einem oder mehreren Permission Schemes** zusammengesetzt (P08-13); die effektiven Rechte sind die **Vereinigung** aller Schemes. Workspace-Owner und -Admins dürfen Custom Roles anlegen. Custom Roles dürfen **weder Workspace-Löschung noch Ownership-Transfer** enthalten.
- **Tier-Entscheidung:** Enterprise Grid (aktuellere Doku) statt Business (Matrix-Text „create custom ones with RBAC“). RBAC im Sinne der Matrix = System-Rollen-Modell (P08-11).
- v2-API: Rollen nur lesbar (`GET …/roles/`, Scope `workspaces.roles:read` „system + custom“; D23). Ein Audit-Beispiel zeigt eine Custom Role mit Slug `release-manager` und Anzeigename „Release manager“ (D23 `audit-logs/list-audit-logs.md`, Ereignis `role.permissions_updated`).

**Vorschlag (UNVERIFIZIERT) für die Portierung:** CRUD für Custom Roles je Namespace (Name, Beschreibung, Slug, zugeordnete Schemes); System-Rollen nicht lösch-/editierbar; Löschen einer benutzten Rolle erfordert Ersatzrolle. Icon für den Settings-Eintrag: `AccessAndRolesOutline` (R32 – im CE nur im God-Mode-Dropdown verwendet, `apps/admin/app/(all)/(dashboard)/sidebar-dropdown.tsx` Z. 106; Zuordnung UNVERIFIZIERT).

**Datenmodell (Vorschlag):** `roles` (P08-11) mit `is_system = false`; `role_permission_schemes(role_id, scheme_id)`; Permission-Katalog als Code-Konstante (Single Source für ASP.NET-Policies und Angular-Guards).

**Quellen:** R1; D23; W19, W20 (W, Verifikation). **Konfidenz:** Tier mittel; Ort/Zusammensetzung mittel; Permission-Katalog niedrig (O4).

---

#### P08-13 – GAC: Granular Access Control – Permission Schemes und effektive Berechtigungen (Enterprise Grid)

**Funktionsbeschreibung (belegbar):**
- Matrix Enterprise „GAC“ (R1 Z. 702); `planHighlights.enterprise` und `ENTERPRISE_PLAN_FEATURES` „GAC“ (R1 Z. 1308; R2 Z. 9); Blog „Introducing Granular Access Control (GAC), LDAP, IdP group sync“ (10.06.2026) ordnet GAC und LDAP **Enterprise Grid** zu (W2, W22).
- **Permission Schemes (Verifikation, W19, W20):** benannte Bündel von Berechtigungen, die an eine oder mehrere Custom Roles (P08-12) gehängt werden. **System-Schemes** (genannt: „Workspace Member“, „Workspace Admin“) sind vorgefertigt und **nicht editierbar**; **Custom Schemes** können angelegt und geändert werden. Custom Schemes sind Enterprise-only. **Bedingte Rechte**: eine Rolle kann Regeln wie „nur selbst erstellte Items löschen“ ausdrücken (Changelog 2026-04-25).
- **v2-API (Verifikation, D23):**

  | Ressource | Methode/Pfad | Felder | Scope |
  |---|---|---|---|
  | Permission Scheme | `GET /api/v2/workspaces/{slug}/permission-schemes/`, `GET …/permission-schemes/{pk}/` (Filter `search`; Pagination wie Rollen) | `id`, `name`, `slug`, `description`, `namespace` (Beispiel `instance`), `permissions` (Array von Strings), `is_system`, `sort_order` (Default-Beispiel 65535, kleiner = weiter vorn) | `workspaces.roles:read` |
  | Effektive Berechtigungen | `GET /api/v2/workspaces/{slug}/permissions/me/`, `GET /api/v2/workspaces/{slug}/projects/{project_id}/permissions/me/` (`project_id` = UUID oder Identifier wie `ENG`) | `permission_grants` (Array von Strings), `relation` (String) | von feingranularen Scope-Prüfungen ausgenommen |

  Alle Endpunkte antworten mit `402 payment_required`, wenn das Feature im Plan nicht enthalten oder abgeschaltet ist (D23 `errors.md` Z. 276–297) – entfällt nach ADR-001. Format der Permission-Strings: nicht dokumentiert; ein Audit-Beispiel nennt `metadata.requested = "projects.states:write"` (Scope-artige Notation, D23) – UNVERIFIZIERT, ob identisch mit Permission-Keys.
- **Namespace `instance`:** Rollen und Schemes kennen neben `workspace` und `project` den Namespace `instance` (D23). Semantik (Instanz-Rollen im God Mode?) **UNVERIFIZIERT**.

**Vorschlag (UNVERIFIZIERT) für die Portierung:** Permission-Katalog aus den CE-Permission-Prüfungen (Dok. 03 §2.4) und den Fragmenten der Permissions-Matrix (P08-11) ableiten; Schemes als Tabelle `permission_schemes(id, workspace_id NULL für System, namespace, slug, name, description, is_system, sort_order)` + `permission_scheme_grants(scheme_id, permission_key, condition jsonb NULL)` für bedingte Rechte; effektive Rechte = Vereinigung über alle Schemes der Rolle; Endpunkt `permissions/me` liefert die Liste für Angular-Guards.

**Quellen:** R1; R2; D23; W2, W19, W20, W22 (W). **Konfidenz:** Objektmodell/API mittel (Doku-Schema mit Platzhalterbeispielen); Permission-Katalog niedrig (O4).

---

#### P08-14 – Guests

**Funktionsbeschreibung**
- Matrix: „Guests – Let some users see everything or just their work items in a project.“; Free –, One/Pro/Business/Enterprise „5 per paid member“ (R1 Z. 706–715). Billing-Karte Pro: „Unlimited members, **1:5 Guests**, Issue Types, Active Cycles, and more“ (B9).
- **CE-Funktion vollständig vorhanden:** Rolle Guest (5) auf Workspace- und Projektebene (R22); Projekt-Einstellung (Projekt → Members) mit Switch „Guest access“ – „This will allow guests to have view access to all the project work items.“ (Texte im CE fest kodiert, nur Projekt-Admin schaltbar; Feld `Project.guest_view_all_features`; `apps/web/components/project/project-settings-member-defaults.tsx` Z. 127, 197–210). Die i18n-Variante `project_settings.members.guest_super_permissions.*` („Grant view access to all work items for guest users:“ / „This will allow guests to have view access to all the project work items.“) ist im CE unreferenziert; Sichtbarkeitsfilter für Gäste in Suche, Export, Pages, Favoriten (`apps/api/plane/app/views/search/base.py` Z. 96–100, 177–182, 229–234, 266–270; `apps/api/plane/bgtasks/export_task.py` Z. 149–153; `apps/api/plane/app/permissions/page.py` Z. 62–63; `apps/api/plane/app/serializers/favorite.py` Z. 74–97); Herabstufung zum Gast setzt alle Projektrollen auf 5 (`apps/api/plane/app/views/workspace/member.py` Z. 116–130; Dok. 03 W-20).
- **Bezahl-Anteil = Kontingent:** max. 5 Gäste je bezahltem Mitglied; Free-Plan der Cloud ohne Gäste (Matrix). Widerspruch zur CE (Free-Parität, aber Gäste unbegrenzt) – im CE gibt es kein Gast-Kontingent. **Verifikation:** Die Doku 2026 nennt die Rolle Guest „auf allen Plänen“ (W18); damit ist die Matrix-Angabe „Free –“ überholt und das CE-Verhalten bestätigt (O16 erledigt). Tier des Kontingents: Pro (One nicht mehr erhältlich; B9 „1:5 Guests“ bei Pro).

**Portierung:** Funktion portieren (A03), Kontingent entfällt (ADR-001).

**Quellen:** R1 Z. 706; B9; R22; Dok. 03; W18 (W, Verifikation). **Konfidenz:** hoch.

---

#### P08-15 – Approvals

**Funktionsbeschreibung (belegbar):** „Set workspace, project, and work item type approvals to designated admins.“ (R1 Z. 717–727; Business/Enterprise, Coming soon); `BUSINESS_PLAN_FEATURES` „Workflows + Approvals“ (R2 Z. 18); Upgrade-Modal-Text „Dashboards, Workflows, Approvals, Time Management, and other superpowers …“ (R27 `upgrade-modal.tsx`); Icon `ApproverOutline` (R32). Weitere Approval-Kontexte im Repo: „Historical timesheets and approvals“ (Time Tracking, R1 Z. 189–190), „Private ones are visible but need approval to join“ (R1 Z. 333), Product-Tour „Your inbox keeps all mentions, approvals, and activity in one place“ (`packages/i18n/src/locales/en/tour.json`).

**Abgrenzung:** Die 2026 ausgelieferten **Workflow-Approval-Flows** (Approval-State, Approver, `required_approvals`, Rejection-State; Enterprise Grid) sind in Dok. 25 F03 vollständig spezifiziert. Die Matrix-Zeile „Approvals“ (Workspace/Projekt/WIT, „designated admins“) ist in Dok. 25 als F08 geführt und **ohne öffentlichen Detail-Spec**.

**Vorschlag (UNVERIFIZIERT):** generisches Freigabe-Objekt `approval_requests(id, workspace_id, scope workspace|project|work_item_type, scope_id, subject_type, subject_id, requested_by, status pending|approved|rejected|cancelled, decided_by, decided_at, comment)` mit konfigurierbaren Approvern je Scope; Benachrichtigung über Inbox. Für die Portierung genügt F03 aus Dok. 25 plus Join-Request privater Projekte (Querbezug Projekt-Cluster).

**Quellen:** R1; R2; R27; R32; Dok. 25. **Konfidenz:** niedrig (O4).

---
### 4.4 Administration & Nachvollziehbarkeit

#### P08-16 – Admin Interface

**Funktionsbeschreibung (belegbar):** „Admin Interface – Get an admin overview to manage workspace and project settings.“ (R1 Z. 729–738; Business/Enterprise). Keine EE-Texte, Routen oder Typen im CE, die eindeutig dazu gehören.

**Kandidaten aus angrenzenden Belegen:**
- Workspace-Einstellung „Projects“ – „Manage project states, and enable project labels, and other configuration.“ mit Tabs „Project states“, „Project labels“ (`workspace_settings.settings.projects.*`, R4) – gehört zum Feature „State of Projects“ (Dok. 20 PF-21).
- **Workspace Governance** (Enterprise Grid, Self-hosted ab v3.2.0, irreversibel): zentrale Verwaltung von States, Labels und Workflows auf Workspace-Ebene; Projekt-Admins sehen Labels „free/constrained/mandated/pinned“ (Dok. 25 F07; Dok. 23 WM-51; W10, sekundär). Commercial v3.0.0 wurde mit „workspace governance, RBAC“ angekündigt (W21).
- Permissions-Matrix: Owner/Admin dürfen privaten Projekten selbst beitreten (Dok. 25 Z. 449; W7, sekundär).

**Vorschlag (UNVERIFIZIERT):** Workspace Settings → Bereich „Administration“ um eine Projektübersicht ergänzen: Tabelle aller Projekte (auch nicht beigetretene, inkl. archivierter), Spalten Name, Identifier, Lead, Mitgliederzahl, Netzwerk (Public/Private/Secret), Erstellt am; Aktionen „Join“, „Settings öffnen“, „Archive“, „Delete“, „Manage members“ – nur Workspace-Admin. Zuordnung zu Governance klären (O5).

**Quellen:** R1 Z. 729; R4; Dok. 20; Dok. 25; W7, W10. **Konfidenz:** niedrig.

---

#### P08-17 – Workspace Activity Logs

**Funktionsbeschreibung (belegbar):** „See filterable activity logs for your entire workspace.“ (R1 Z. 740–749; Business/Enterprise; **nicht** Coming soon → ausgeliefert). **Abgrenzung (Verifikation):** Dok. 20 (`_data/P01.paid.json`, PF-59) zitiert einen Changelog v2.2.0 „audit logs for workspace and member activity“ (WebSearch, UNVERIFIZIERT); möglicherweise sind „Workspace Activity Logs“ und das Audit-Log (P08-18) im heutigen Produkt dieselbe Oberfläche. Die Audit-Log-Doku (W15) beschreibt nur Sicherheits-/Admin-Ereignisse, keine Work-Item-Änderungen; deshalb bleiben beide Features getrennt (O20). Plane-Doku zu „Activity Logs“ wurde per Websuche nicht gefunden.

**CE-Ausgangslage (wird portiert):**
- `IssueActivity`-Modell (Work-Item-Historie) mit Activity-Erzeugung im Celery-Task `issue_activities_task` (Details: `migration/analysis/04-api-intern-arbeitsobjekte.md`).
- Aktivität **je Benutzer**: `GET /api/workspaces/{slug}/user-activity/{user_id}/` (`WorkspaceUserActivityEndpoint`, Permission `WorkspaceEntityPermission`): alle `IssueActivity` des Actors im Workspace außer Feldern `comment`, `vote`, `reaction`, `draft`, nur sichtbare Work Items (`_visible_issues_q`), nur nicht archivierte Projekte, optional Query `project` (mehrfach), paginiert, `order_by` aus Allowlist (Default `-created_at`) (R25 `apps/api/plane/app/views/workspace/user.py` Z. 409–435); Export `GET …/user-activity/{user_id}/export/` (R25 `apps/api/plane/app/urls/workspace.py` Z. 142–146). UI: Profil → Activity (`apps/web/app/routes/core.ts` Z. 98–99), Account-Settings-Text „Track your recent actions and changes across all projects and work items.“ (`packages/i18n/src/locales/en/settings.json`, `account_settings.activity.description`).
- No-op im Workspace-Store: `mutateWorkspaceMembersActivity = async (_workspaceSlug) => { /* No-op in default/CE version */ }` (R24 Z. 385–391). Name deutet auf „Mitglieder-Aktivität“ hin; ob dies die Activity-Logs oder die Seat-/Aktivitätsdaten der Mitglieder (Billing) speist, ist **UNVERIFIZIERT**.

**Vorschlag (UNVERIFIZIERT) für die EE-Funktion:** Workspace Settings → „Activity“ (Admin): chronologische Liste aller Aktivitäten im Workspace (Work Items, Cycles, Modules, Pages, Views, Projekte, Mitglieder), Darstellung wie Work-Item-Activity (Avatar, Akteur, Verb, Feld, alt → neu, relative Zeit); Filter Akteur (Multi-Select), Projekt, Entitätstyp, Aktionstyp, Zeitraum (Optionen wie `EDurationFilters` `today/this_week/this_month/this_year/custom`, `packages/types/src/enums.ts`); Export CSV.

**Datenmodell (Vorschlag):** Aus bestehenden Activity-Tabellen per Union-View oder eigener `workspace_activities(id, workspace_id, project_id, actor_id, entity_type, entity_id, verb, field, old_value, new_value, created_at)` mit Index `(workspace_id, created_at desc)`.

**API (Vorschlag):** `GET {W}/activities/?actor=&project=&entity_type=&verb=&from=&to=&cursor=`.

**Quellen:** R1 Z. 740; R24; R25. **Konfidenz:** CE-Basis hoch; EE-UI niedrig.

---

#### P08-18 – API-enabled Audit Logs

**Funktionsbeschreibung (belegbar)**
- Matrix: „See a full-workspace audit log and use APIs to flag Plane activity in compliance systems.“ (R1 Z. 751–760; Business/Enterprise, Coming soon).
- „Audit logs, SCIM, advanced auth – Cloud: Business Plus; Self-hosted: Available on plans (Commercial and Airgapped)“ (`self-hosting-101.md` Z. 42).
- MCP-Doku: „Revoke tokens in Plane settings and audit API token events in the workspace audit log.“ (D20 Z. 751) → Audit-Log enthält **API-Token-Ereignisse** (Anlegen/Widerrufen/Nutzung – Umfang UNVERIFIZIERT).
- Ausgeliefert mit Commercial v3.1.0 bzw. Cloud-Release 2026-07-31 („audit logs“ im Changelog-Titel; W5, W6, sekundär); Nutzer-Doku `docs.plane.so/workspaces-and-users/audit-logs` existiert (W4, sekundär).
- Verwandt: Argus schreibt eigene „audit rows“ mit Client-IP (H4 README Z. 1145; P08-29).
- **Tier (Verifikation):** Der Seitentitel der Nutzer-Doku lautet „Workspace Audit Logs **Enterprise Grid**“ (W15) → Enterprise Grid; Matrix „Business“ (Coming soon) ist der ältere Stand. Widerspruch zu Dok. 21 F34 und Dok. 22 P03-F44 (dort Business beibehalten) dokumentiert.

**UI und Verhalten (Verifikation, W15, nur Suchzusammenfassung, mittel):**
- Ort: **Settings → „Audit logs“** (Workspace). Sichtbar und exportierbar **nur für Admins und Owners**, nicht für Members/Guests.
- Liste mit den **neuesten Ereignissen zuerst**; **Filter** und **Export** oben auf der Seite.
- Einträge werden einmal geschrieben und können **von niemandem** (auch nicht von Admins) bearbeitet oder gelöscht werden.
- Erfasste Ereignisse (laut Zusammenfassung): Sign-ins, Mitgliedschafts- und Rollenänderungen, Einstellungsänderungen, Integrationsaktivität, Sicherheitsereignisse, Aktivieren/Deaktivieren von Workspace-Features, Planwechsel; **das Lesen und Exportieren des Audit-Logs wird selbst protokolliert**. API-Token-Ereignisse sind enthalten (D20).
- Nicht belegt: Spalten der Tabelle, Filter-UI, Exportformat, Aufbewahrungsdauer (UNVERIFIZIERT, O9). Icon-Vorschlag `AuditLogsOutline` (R32 – im CE ungenutzt; Zuordnung UNVERIFIZIERT).

**API (Verifikation, D23 `audit-logs/*.md`, belegt):**

| Methode | Pfad | Zweck | Scope |
|---|---|---|---|
| GET | `/api/v2/workspaces/{slug}/audit-logs/` | Liste/Abfrage/Export | `workspaces.audit_logs:read` |
| GET | `/api/v2/workspaces/{slug}/audit-logs/{pk}/` | Einzeleintrag | `workspaces.audit_logs:read` |

Kein `POST`/`PATCH`/`DELETE` – Einträge schreibt nur Plane. Kein workspace-übergreifendes Abfragen.

**Audit-Log-Objekt (D23 `audit-logs/overview.md`):**

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | uuid | ID des Eintrags |
| `event_id` | uuid | ID des Ereignisses; Idempotenzschlüssel beim Import in Fremdsysteme |
| `sequence_number` | integer | fortlaufende Schreibreihenfolge; Tiebreaker bei gleichem `created_at` |
| `event_name` | string | konkretes Ereignis; belegte Beispiele: `member.role_updated`, `auth.sign_in`, `role.permissions_updated` (vollständiger Katalog nicht dokumentiert) |
| `category` | string | `auth`, `member`, `role`, `settings`, `integration`, `webhook`, `security`, `instance` |
| `outcome` | string | `success`, `failure` (Fehlversuche werden protokolliert) |
| `source` | string | `platform` (Plane-App), `api` (REST-Client), `graphql`, `auth`, `system` (Plane selbst) |
| `actor_type` | string | `user`, `api_token`, `system`, `anonymous` |
| `actor_id` | uuid, nullable | handelnder Nutzer (= `member_id` der Mitgliederlisten); `null` bei `system`/`anonymous` |
| `actor_display_name`, `actor_email` | string | Schnappschuss zum Ereigniszeitpunkt (spätere Umbenennung ändert alte Einträge nicht) |
| `target_type` | string | Art des Ziels, Beispiele `workspace_member`, `user`, `role` |
| `target_id` | string | ID des Ziels (bei Custom Roles der Slug, Beispiel `release-manager`) |
| `target_display_name` | string | Schnappschuss-Bezeichnung des Ziels |
| `old_value`, `new_value` | beliebig, nullable | Zustand vorher/nachher, freies Schema je `event_name` (Beispiel `{ "role": "member" }` → `{ "role": "owner" }`); bei Sign-in beide `null` |
| `reason` | string | Begründung, v. a. bei `failure` (Beispiele `invalid_credentials`, `insufficient_permissions`) |
| `metadata` | beliebig | Zusatzkontext je `event_name` (Beispiele `{ "workspace_slug": … }`, `{ "attempt": 3 }`, `{ "requested": "projects.states:write" }`) |
| `ip_address` | string, nullable | Client-IP; `null` bei `system` |
| `user_agent` | string | User-Agent |
| `workspace_id` | uuid | Workspace |
| `project_id` | uuid, nullable | Projekt, falls projektbezogen |
| `created_at` | date-time (UTC) | Zeitpunkt; Basis der Datumsfilter |

**Listen-Parameter (D23 `audit-logs/list-audit-logs.md`):** Filter (UND-verknüpft) `created_after`, `created_before` (ISO-8601, UTC), `actor_id` (schließt `system`/`anonymous` aus), `event_name`, `category`, `outcome`, `target_type`, `target_id`, `ip_address`, `search` (Freitext); Sortierung `order_by` ∈ `-created_at` (Default für Untersuchungen), `created_at`, `id`, `-id` (unbekannte Werte fallen still auf die Default-Sortierung zurück); Pagination `per_page` (Default 50, Max 200), `offset` (Max 10 000), `paginate=cursor` (Envelope mit `next_cursor`/`has_more` statt `next`/`total_count`, ohne `COUNT`, stabil bei neuen Einträgen), `count` (Default `true`; `false` lässt `total_count` weg); `fields` (Sparse Fields, `all` = alle; unbekannter Name → `400` mit Liste gültiger Felder; `id` immer enthalten). Offset-Envelope: `data`, `next`, `previous`, `total_count`, `pagination.style = "offset"`. Fehler: `401 unauthorized`, `402 payment_required` (Feature nicht im Plan/abgeschaltet – entfällt nach ADR-001), `403 forbidden` (Rolle oder Token-Scope), `404 not_found`, `406 not_acceptable`, `429 rate_limited` (mit `Retry-After`). Hinweis der Doku: der Scope legt E-Mails, IPs und User-Agents des ganzen Workspaces offen.

**Vorschlag (UNVERIFIZIERT) für die Portierung:**
- Append-only-Tabelle, beschrieben von allen sicherheitsrelevanten Pfaden (Auth inkl. Fehlversuche, Mitglieder, Rollen/Schemes P08-11…13, Einstellungen, Integrationen, Webhooks, Sicherheit inkl. SSO/Identity/Domains P08-03 und Group Sync P08-05, Instanz-Ereignisse, API-Token-Ereignisse, Lesen/Export des Logs selbst).
- Optional Webhook-Event für Compliance-Systeme („use APIs to flag Plane activity in compliance systems“) – nicht belegt.
- Aufbewahrung: Instanz-Einstellung (ADR-001: keine Plan-Limits).

**Datenmodell (Vorschlag, an das belegte Objekt angelehnt):** `audit_logs(id uuid, event_id uuid unique, sequence_number bigint identity, event_name, category, outcome, source, actor_type, actor_id null, actor_display_name, actor_email, target_type, target_id text, target_display_name, old_value jsonb null, new_value jsonb null, reason, metadata jsonb, ip_address inet null, user_agent, workspace_id, project_id null, created_at timestamptz)`; Indizes `(workspace_id, created_at desc)`, `(workspace_id, actor_id)`, `(workspace_id, category)`, `(workspace_id, target_type, target_id)`; Partitionierung nach Monat; kein Update/Delete außer Retention-Job.

**Quellen:** R1 Z. 751; D12; D20; D23; H4; W4–W6 (W, sekundär); W15 (W, Verifikation). **Konfidenz:** Existenz hoch; API-Objekt und Filter hoch (Doku-Branch, Stand 11.08.2026); UI mittel; Ereigniskatalog niedrig (O9).

---

#### P08-27 – God Mode: User Management (Instanz-Benutzer)

**Funktionsbeschreibung (D5, D7, B10)**
- **Navigation:** God-Mode-Sidebar der Commercial Edition (Reihenfolge laut B4/B10/B11): „General“ (Identify your instances and get key details.), „Email“ (Configure your SMTP controls.), „Authentication“ (Configure authentication modes.), „Workspaces“ (Manage all workspaces on this instance.), **„Billing“ (Active plans)**, **„User Management“ (Instance user management)**, „Artificial intelligence“ mit Zusatz „(deprecated)“ (Configure your OpenAI creds.), „Images in Plane“ (Allow third-party image libraries.); Fußzeile „Redirect to Plane“, Hilfe-Icon, Einklapp-Pfeil. CE-Sidebar: `apps/admin/hooks/use-sidebar-menu/core.ts`, `index.ts` (ohne Billing/User Management).
- **Seite „User Management“** (Breadcrumb „Settings › User Management“): Titel „User Management“, Untertitel „View and manage seats for all the members active in this instance“; rechts Suchfeld „Search…“ und Button „+ Invite members“ (primary). Tabelle mit Spalten **Full Name** (Avatar + Name + „…“-Menü), **Display Name**, **Email**, **Account Type** („User“ / „Instance Admin“), **Status** („Active“ / „Suspended“; Spalte mit Sortier-Icon), **Joining Date** (Format „Jan 29, 2026“); Spaltenköpfe mit Dropdown-Pfeil (Sortierung) (B10 `user-management.webp`; D7 Tabelle).
- **Zeilenmenü „…“** (B10 `user-actions.webp`; D7): „Grant admin access“ (User → Instance Admin) bzw. „Remove admin access“ (Schild-Icon), „Remove“ (Papierkorb, rot) – „remove the user from the instance entirely“.
- **Modal „Invite instance admin“** (B10 `invite-instance-admin.webp`): „Email ID *“ (Platzhalter „Enter Email ID“), „Password *“ (Platzhalter „Enter your password“, Auge-Icon, separater Copy-Button), Checkbox „Generate random password.“, Checkbox „Prompt user to change password after onboarding.“, Info-Box „Make sure to copy this password and share with the admin personally.“; Buttons „Cancel“, „Invite“. „No invitation email is sent.“ Instanz-Admins werden **keinem Workspace** hinzugefügt (D7).
- **Status:** Active = Zugriff; Suspended = Konto existiert, kein Zugriff (D7).

**CE-Ausgangslage:** Modell `InstanceAdmin(user, instance, role=20, is_verified)` (R10); Endpunkte `GET/POST /api/instances/admins/` (POST verlangt **existierenden** User per `email`, `role` Default 20) und `DELETE /api/instances/admins/{pk}/` (`apps/api/plane/license/api/views/admin.py` `InstanceAdminEndpoint`, Permission `InstanceAdminPermission`); keine UI. `User.is_password_reset_required` (R12/R13) ist im CE ungenutzt – plausibel das Feld hinter „Prompt user to change password after onboarding“ (UNVERIFIZIERT). Deaktivierte Konten werden im CE-Login abgewiesen (`USER_ACCOUNT_DEACTIVATED`, R14).

**Datenmodell-Hinweise:** Bestehende Modelle genügen: `User` (`is_active`, `is_password_reset_required`, `date_joined`), `InstanceAdmin`. „Remove“: Vorschlag Deaktivierung (`is_active=false`, `last_logout_time` setzen, Workspace-Mitgliedschaften deaktivieren) statt hartem Löschen (UNVERIFIZIERT, O10).

**API (Vorschlag):** `GET /api/instances/users/?search=&order_by=&cursor=`, `POST /api/instances/users/invite-admin/` `{email, password, generate_password, require_password_change}`, `POST /api/instances/users/{id}/grant-admin/`, `POST …/revoke-admin/`, `DELETE /api/instances/users/{id}/`.

**UI-Hinweise:** Untertitel enthält „seats“ – nach ADR-001 Wortlaut beibehalten oder neutralisieren (O11).

**Quellen:** D5; D7; B4; B10; B11; R10; R12–R14. **Konfidenz:** hoch (UI); mittel (Backend).

---

#### P08-28 – God Mode: Session-Einstellungen

**Funktionsbeschreibung (D6):** God Mode → „System Configurations“ → Abschnitt „Session settings“ mit zwei Feldern:

| Einstellung | Gilt für | Einheit | Default | Minimum |
|---|---|---|---|---|
| Session expiry | alle Sessions der Plane-App (alle Workspaces) | Tage | 7 | 1 |
| Admin session expiry | God-Mode-Session | Stunden | 1 | 1 |

- Ganzzahlen; Werte unter Minimum werden abgelehnt. App-Sessions sind **inaktivitätsbasiert**: Ablauf wird bei Aktivität im Hintergrund verlängert, höchstens einmal pro Tag. Admin-Sessions sind **absolut** (keine Verlängerung). Änderungen wirken bei Neuanlage/Refresh von Sessions, keine sofortige Abmeldung. ENV-Pendants in Sekunden `SESSION_COOKIE_AGE` (604800), `ADMIN_SESSION_COOKIE_AGE` (3600); UI-Wert hat Vorrang (gespeichert als Instanz-Konfiguration).
- **CE-Ausgangslage:** nur ENV (`apps/api/plane/settings/common.py` Z. 425, 432); Verwendung in `apps/api/plane/authentication/middleware/session.py` Z. 64 und `apps/api/plane/authentication/utils/login.py` Z. 19. Die Seite „System Configurations“ fehlt in der CE-Admin-App (`apps/admin/app/routes.ts`) und ist auf keinem Screenshot B4–B11 sichtbar (Sidebar-Eintrag UNVERIFIZIERT).

**Datenmodell:** `InstanceConfiguration`-Schlüssel (Vorschlag `SESSION_COOKIE_AGE`, `ADMIN_SESSION_COOKIE_AGE`, UNVERIFIZIERT).

**Quellen:** D6; R31. **Konfidenz:** hoch (Verhalten); mittel (Ort in der Navigation).

---

#### P08-29 – Argus: Sensitive-Data-/PII-Scanner

**Funktionsbeschreibung (H1, H4):** Optionaler Dienst „Argus – sensitive-data & PII scanner (gated in the product by the PII_SCANNER feature flag)“ (H1 Z. 703–704). Eigenschaften laut Helm-README (H4 Z. 1090–1146):
- Scannt Inhalte der Plane-Datenbank (optional über Read-Replica `ARGUS_CONTENT_DATABASE_URL`); eigenes Schema `argus` in der Plane-DB, schreibt nie in Plane-Tabellen.
- **Findings** mit HMAC-Fingerprints (`ARGUS_FINGERPRINT_SECRET` als HKDF-Master-Key, ≥ 32 Zeichen, stabil halten – sonst brechen „finding dedup, staling, `group_by=fingerprint` and existing triage decisions“) → Funktionen: Deduplizierung, Veralten („staling“), Gruppierung nach Fingerprint, **Triage-Entscheidungen**.
- Findings-Export als CSV mit Einmal-Download-Token (Gültigkeit 15 min), Scan-Runs mit Rate-Limit (`ARGUS_DEFAULT_RATE_RPS` 500, `ARGUS_MAX_RATE_RPS` 10000), Worker-Pool `min(8, NumCPU)`.
- „Audit rows“ protokollieren Client-IPs (`ARGUS_TRUSTED_PROXIES`).
- Browser-Routen unter `/argus/` (Web-Build `VITE_ARGUS_BASE_PATH`), d. h. eigene UI-Seiten in der Web-App.
- Changelog v3.2.0 „PII scanning“ (W9, sekundär). UI-Texte, Plan-Tier und Erkennungsregeln: **nicht belegt**.
- **Ergänzung (Verifikation):** Laut Dok. 22 P03-F33 (Suchzusammenfassung des v3.2.0-Changelogs, UNVERIFIZIERT) kam Argus mit Commercial v3.2.0 (10.09.2026); gescannt werden Work-Item-Beschreibungen, Kommentare, Pages und Anhänge; Kategorien E-Mail-Adressen, Telefonnummern, Kartennummern, Ausweis-/Regierungs-IDs, Adressen, Secrets, API-Keys; Funde nach Kategorie und Fundort; Schwärzung (Redaction) kann vor dem Teilen oder Exportieren erzwungen werden; Inhalte verlassen den Workspace nicht. Belegte Scan-Run-Status: `running`, `pausing`. Weitere Architekturdetails (Reaper, `/healthz`, `/admin-health`, Session-Prüfung über `GET <API_INTERNAL_URL>/api/users/session/`) stehen in Dok. 22 P03-F33. Propel liefert die Icons `PiiScannerOutline`/`PiiScannerFilled` (R32), im CE ungenutzt.

**Migrationshinweis:** Als .NET-Hintergrunddienst im Aspire-AppHost; Erkennungsregeln (E-Mail, Telefonnummern, IBAN, Kreditkarten mit Luhn, API-Keys) als Vorschlag (UNVERIFIZIERT, O9).

**Quellen:** H1; H4; R32; W9; Dok. 22 P03-F33. **Konfidenz:** Infrastruktur hoch; Produktfunktion niedrig.

---
### 4.5 Lizenz, Seats, Pläne (Dokumentation des Originals; **entfällt nach ADR-001**, außer wo „Portierung“ etwas anderes sagt)

#### P08-19 – Workspace-Lizenz und Seite „Billing and plans“

**Funktionsbeschreibung**
- **Ort:** Workspace Settings → „Billing and plans“ (CE-Key `billing-and-plans`, Route `/{workspaceSlug}/settings/billing`, nur Workspace-Admin, Icon `BillingsOutline`; R29; `apps/web/app/routes/core.ts` Z. 270–271).
- **CE-Inhalt (R26):** `SettingsHeading` „Billing & Plans“ – „Choose your plan, manage subscriptions, and easily upgrade as your needs grow.“; Box „Community“ – „Unlimited projects, issues, cycles, modules, pages, and storage“; Überschrift „All plans“; Planvergleich `PlansComparison` (Pro mit Badge „Popular“, Preis über `DiscountInfo`, Monat/Jahr-Umschalter `PlanFrequencyToggle`, Button „Upgrade to Pro“ → externe URL `https://app.plane.so/upgrade/pro/self-hosted?plan=month|year`; Business/Enterprise „Quote on request“ + „Talk to Sales“ → `https://plane.so/talk-to-sales`; R28 `SUBSCRIPTION_REDIRECTION_URLS`), aufklappbar „Compare all features“ mit Matrix R1.
- **Commercial-Inhalt (B8, B9, D8, D11, D12):**
  - **Plan-Karte oben** – Free (Self-hosted): „Free“ / „Your Plane license can only be used to unlock features for one workspace.“ / „Billable seats when you upgrade: {n}“ + Button **„Activate this workspace“** (B8). Free (Cloud): „12 members, unlimited projects, issues, cycles, modules, and pages“ / „Billable seats when you upgrade: 21“ + „Upgrade to Pro“ + „Start free trial“ (B9). Pro aktiv: „Pro“ / „Unlimited members, 1:5 Guests, Issue Types, Active Cycles, and more“ / „Your billing cycle renews on Oct 17, 2024 • Billable seats: 1“ + „Manage your subscription“ (externer Link) (B9).
  - **„All Plans“**: Spalten Free „$0“ („Current plan“), Pro „$6 a user per month billed yearly“ (Monthly/Yearly-Umschalter mit Badge „-25%“, Button „Upgrade“, Link „Start free trial“), Business/Enterprise „Quote on request / billed yearly“ + „Talk to sales“; Zeile „Highlights“ (Free: Upto 12 users, Pages, Unlimited projects, Unlimited cycles and modules; Pro: Unlimited users, Custom Issues + Properties, Issue templates, Full Time Tracking; Business: RBAC, Project Templates, Baselines And Deviations, Custom Reports; Enterprise: Private + managed deployments, GAC, LDAP support, Databases + Formulas); „Compare all features ↓“ (B9).
  - **Modal „Activate [Logo] {Workspace}“** (Schlüssel): „The Plane license key you enter below will activate the associated plan for this workspace on your instance. Any other workspaces without a license key will continue to be on the Free plan.“; Feld „Enter license key“ (Platzhalter `qwweq-wewqw-weqweq`); Buttons „Close“, „Activate“ (B8).
  - **„Sync plan“**: holt Plan-Typ, Seat-Anzahl, Ablaufdatum und Feature-Zugang vom Prime-Server; bei Abweichungen zwischen Prime-Portal und Workspace (D8 Z. 35–47; D12 Z. 74).
  - **„Delink license key“**: löst den Schlüssel vom Workspace/der Maschine (Schlüssel ist an **einen Workspace und eine Maschine** gebunden); danach `prime-cli restart` und Neuaktivierung (D8 Z. 49–64).
  - **Trial** (Cloud): Banner „Your 14-day Business plan trial is live!“ – „Explore all Business features. When you're ready, choose to subscribe. You'll not be billed automatically.“, „Trial ends today“ / „Trial ends in {days, plural, one {# day} other {# days}}“, Buttons „Start subscription“, „Explore Business features“ (R6). Workspace löschen während Trial gesperrt: „Cancel your trial first.“ / „You have an active trial to one of our paid plans. Please cancel it first to proceed.“, Buttons „Dismiss“, „Cancel trial“, Toasts „Trial cancelled.“ / „You can now delete the workspace.“ / „That didn't work.“ / „Try again, please.“ (R4 `cancel_trial.*`, `general.delete_modal.{description,dismiss,cancel}`).
  - **Upsell-Elemente** (EE-Texte): „Upgrade“, „Upgrade plan“, „Plane Pro“, „Add Seats“, „Upgrade to higher subscription“, „Talk to Sales“, „Ask your Workspace Admin to upgrade.“ (R7, R9); Editions-Badge in der Sidebar (CE: Button „Community“, Tooltip „Version: v{version}“, öffnet `PaidPlanUpgradeModal`; R27).
  - **Fehlertexte** (D11): „Your license is invalid or already in use.“; „Something went wrong please try again later“; „Payment server is not configured“ (fehlende ENV `payment_server_url`).
- **CE-Spuren:** Typ `IInstance.license_key`, `is_activated`, `user_count` (R15 `base.ts`) obwohl `license_key` und `user_count` per Migration 0005 aus `instances` entfernt wurden (R11); `Profile.billing_address_country` (Default „INDIA“), `billing_address`, `has_billing_address`, `company_name` (R12 Z. 238–241).

**Portierung:** **entfällt** (ADR-001). Konsequenzen für die 1:1-UI (ADR-005): Settings-Eintrag „Billing & Plans“, Editions-Badge, Upgrade-Modal, Trial-Banner und Upsell-Texte werden **nicht** gebaut; der Versions-Tooltip des Badges kann an anderer Stelle erscheinen (O11). `Profile.billing_*` nicht übernehmen.

**Quellen:** R4; R6; R7; R9; R11; R12; R15; R26–R29; D8; D11; D12; B8; B9. **Konfidenz:** hoch.

---

#### P08-20 – Enterprise-Grid-Instanzlizenz (God Mode → Billing)

**Funktionsbeschreibung (D9, B7):** God-Mode-Sidebar „Billing“ („Active plans“) → Seite „Billings and plans“ – „Manage your instance license, view billing details, and upgrade your plan.“; Karte „Activate Enterprise license“ – „If you possess an enterprise plan, please enter your license key to activate it here. This activation will apply to all workspaces within this instance.“; Eingabe „License key“ + Button „Activate“ (deaktiviert bis Eingabe). Enterprise-Grid-Lizenzen werden **auf Instanzebene** aktiviert, nicht je Workspace; danach gelten Enterprise-Features für alle Workspaces (D9 Z. 9, 23). Schlüssel aus Prime-Portal „Manage licenses“.

**Portierung:** entfällt (ADR-001). **Quellen:** D9; B7. **Konfidenz:** hoch.

---

#### P08-21 – Offline-Lizenzdatei (Airgapped)

**Funktionsbeschreibung (D10, B7, B8):**
- Prime-Portal → „Manage licenses“ → „Download license“ (Datei je Plane-Version).
- **Pro/Business (Workspace):** Workspace Settings → „Billing and plans“ → „Activate this workspace“ → Modal „Activate [Logo] {Workspace}“: „Upload a license file to activate the plan you subscribed to on this workspace. Any other workspaces without a license key on this instance will continue to be on the Free plan.“; Bereich „Upload a license file“ mit gestrichelter Dropzone „Drag & drop or click to browse. Supports .json files.“; Abschnitt „Plane provided details“ – „These details are auto-generated for your instance and workspace. You can copy and use them as needed.“ mit Copy-Feldern **Instance ID**, **Workspace ID**, **Workspace slug**, **Domain**, **Instance app version**; Buttons „Cancel“, „Activate“ (B8 `upload-airgapped-license-file.webp`).
- **Enterprise Grid (Instanz):** God Mode → Billing → Karte „Activate Enterprise license“ – „If you possess an enterprise plan, please upload your license file to activate it here. This activation will apply to all workspaces within this instance.“; Dropzone (.json); Abschnitt „Instance details“ – „These details are auto-generated for your instance. You can copy and use them as needed.“ mit **Instance ID** (Beispiel `742279ea7250377e29faf598`), **Domain** (Beispiel `https://airgapped.nikhil.plane.one`), **Instance app version** (Beispiel `v2.3.2`); Button „Activate“ (B7 `upload-airgapped-enterprise.webp`).
- Widerspruch: D13 „Airgapped deployments are available exclusively for Enterprise Grid customers“ vs. D10 „Activate Pro or Business on Airgapped Edition“.

**Portierung:** entfällt (ADR-001). Die angezeigten Instanzdaten (Instance ID, Domain, App-Version) bleiben in God Mode → General verfügbar (CE: Name, Email, Instance ID; B11). **Quellen:** D10; D13; B7; B8; B11. **Konfidenz:** hoch.

---

#### P08-22 – Prime-Portal und Monitor-Dienst

**Funktionsbeschreibung:**
- **Prime-Portal** `https://prime.plane.so/licenses`: Lizenzen verwalten, Schlüssel kopieren, Lizenzdatei herunterladen, „Get more licenses“ (D8, D10). Lizenzvalidierung der Commercial Edition gegen Prime; Airgapped ohne Verbindung (D12 `self-hosting-101.md` Z. 21; D13).
- **Monitor** (Go, StatefulSet, Image `makeplane/monitor-commercial`): „Used for license validation and activation. It checks the license status and ensures your instance is compliant.“ (D15 `plane-architecture.md` Z. 46–47). Zwei Cron-Jobs: Health-Probes alle 5 min gegen `SERVICE_<METHOD>_<NAME>`-Ziele (`maxRetries=5`, `confirmTries=3`, Timeout 5 s, Retry-Intervall 2 s, HTTP 200–399 gesund, Ergebnis an `HOST/api/service-status/`, unerreichbar = 500) und **„Flag/license resync“ alle 300 min** („refreshes feature flags and licenses from the monitoring server“) (D15 `health-checks.md` Z. 365–386).
- **Konfiguration** (H2, H3): `PRIME_HOST` (= `license.licenseServer`, Default `https://prime.plane.so`), `MACHINE_SIGNATURE` (Helm: Hash), `APP_DOMAIN` (= `license.licenseDomain`, an Ingress-Host gebunden), `APP_VERSION`, `DEPLOY_PLATFORM` (`KUBERNETES`), `IS_AIRGAPPED`, `API_URL`; API/Silo/PI/Argus fragen Monitor unter `PAYMENT_SERVER_BASE_URL` bzw. `FEATURE_FLAG_SERVER_BASE_URL` (`http://<release>-monitor:8080/`).
- **Telemetrie für Abrechnung** (D16): „Plane tracks the number of workspaces, members, and roles to bill you correctly and ensure accurate reporting in your workspace's Billing and plans screen and the Prime portal.“
- **CE-Spuren:** `MACHINE_SIGNATURE` = SHA-256 über Hostname, erste MAC-Adresse, `/proc/cpuinfo`, `free -h`, `df -h` (R30 `docker-entrypoint-api.sh` Z. 10–24); `register_instance` prüft nur, dass die Signatur nicht leer ist, legt `Instance` mit `instance_id = secrets.token_hex(12)`, `edition = PLANE_COMMUNITY` an und stößt Telemetrie an (R30). `Instance.edition` ist immer `PLANE_COMMUNITY` (R10).

**CE-Status (Verifikation):** Stub/UI-Hülle im CE statt „teilweise“ – im CE ist keine Lizenzvalidierung und kein Feature-Flag-Abruf erreichbar; vorhanden sind nur Enum/Typ-Spuren und die Präsenzprüfung der Signatur (Dok. 22 Verifikations-Protokoll: `MACHINE_SIGNATURE` im CE „anders berechnet als im EE-Chart“; Dok. 22 P03-F02 „fehlt“).

**Portierung:** entfällt (ADR-001, ADR-004: keine Pflicht-Verbindung nach außen). Health-Checks/System-Checks: siehe Dok. 22 (P03-F34). `MACHINE_SIGNATURE` nicht nötig. **Quellen:** D8; D10; D12; D13; D15; D16; H1–H3; R10; R30. **Konfidenz:** hoch.

---

#### P08-23 – Self-hosted-Pläne und Deployment-Varianten

| Variante | Inhalt | Tier | Quelle | Portierung |
|---|---|---|---|---|
| Plane One | Einmalpreis 799 „per workspace“; „Upto 50 users“, „OIDC and SAML“, „Active cycles“, „Limited time tracking“; `ONE_PLAN_FEATURES` inkl. „Docker, Kubernetes and more“; im Planvergleich nicht mehr gerendert („Plane one plan is not longer available“) | One | R1 Z. 1266–1275, 1305; R2 Z. 34–41; `apps/web/components/workspace/billing/comparison/base.tsx` Z. 27–33 | entfällt |
| One-click Deployment / Digital Ocean Marketplace / Heroku / AWS AMI | Installations-Kanäle | One+ | R1 Z. 1147–1189 | entfällt (Vertriebskanäle); Container-Images bleiben |
| God Mode | Instanz-Admin-Oberfläche | alle | R1 Z. 1136 | portieren (CE-Basis + P08-27/28) |
| Commercial-Installationsmethoden | Docker Compose (`prime-cli`), Kubernetes (`plane-enterprise`-Chart), AIO, Swarm, Podman Quadlets, Coolify, Portainer | Commercial | D15 `prime-cli.md`; Dok. 22 P03-F42 | entfällt als Produkt; Betrieb über Aspire-Manifest/Helm (Architektur) |
| Airgapped Edition | keine Telemetrie, Offline-Lizenz, keine externen Abhängigkeiten nach Image-Import, interne OAuth-Provider (GitHub Enterprise, GitLab), eigene Registry, interne CA (`customCA`), `IS_AIRGAPPED=1`; Mindestabnahme 100 Seats | Enterprise Grid | D13; H1 Z. 15–30; H2 | **Grundeigenschaft** (ADR-004), kein Schalter nötig |
| Private deployments | „Get our hosted Cloud app on a private Cloud managed by us.“ (Coming soon); Highlight „Private + managed deployments“ | Enterprise | R1 Z. 1191–1201, 1308; R2 Z. 8 | entfällt (Dienstleistung) |
| FIPS-Images | `-fips`-Varianten aller Images (UBI 10, OpenSSL-FIPS-Provider, Go-FIPS-140-3-Modul); Host muss im FIPS-Modus laufen (`/proc/sys/crypto/fips_enabled = 1`); `PLANE_REQUIRE_FIPS=1` → Start verweigert ohne FIPS-Host; Defaults: `LDAP_TLS_REQUIRE_CERT=demand`, `SAML_REJECT_DEPRECATED_ALGORITHM` an, `SECRET_ENCRYPTION_V2` an (AES-256-GCM für Secrets at rest, beide Formate lesbar), `USAGE_ID_DIGEST=sha256`; kein FIPS-AIO; Start-Log „plane: FIPS mode ACTIVE (host kernel reports fips_enabled=1)“ | Enterprise Grid | D14 | als **Betriebsprofil** portieren: Konfigurationsschalter `RequireFips` (Start-Check, nur FIPS-konforme Algorithmen, AES-GCM für Secrets, SHA-256 statt MD5/SHA-1) |

**CE-Spuren:** `deployments/cli/community/restore-airgapped.sh` (Restore von CE-Backups in Airgapped-Commercial, R34); Upgrade CE → Commercial durch Zurückspielen von Postgres-, Redis- und MinIO-Daten (D12 `upgrade-from-community.md`).

**Quellen:** R1; R2; R34; D12–D15; H1; H2. **Konfidenz:** hoch.

---

#### P08-24 – Member-Limits und Seat-Berechnung

| Regel | Wert | Quelle |
|---|---|---|
| Cloud Free | 12 Mitglieder („Upto 12 users“) | R1 Z. 680, 1304; B9 |
| Cloud One | leer (`""`); Highlight „Upto 50 users“ | R1 Z. 681, 1305 |
| Cloud Pro/Business/Enterprise | Unlimited | R1 Z. 682–684 |
| Self-hosted-Richtwerte („users that our standard infra supports“) | Free ~50, One ~50, Pro ~200, Business ~200, Enterprise Unlimited | R1 Z. 686–692 |
| Commercial Free | 12 freie Seats je Workspace | D12 `editions-and-versions.md` Z. 35; `self-hosting-101.md` Z. 60 |
| Billable Seats | Anzahl Nutzer mit **bezahlten Rollen** im Workspace (automatisch berechnet); Anzeige „Billable seats when you upgrade: n“ bzw. „Billable seats: n“ | D12 Z. 37; B8; B9 |
| Gäste | 5 je bezahltem Mitglied („1:5 Guests“) | R1 Z. 706; B9 |
| Agents/Bots | „Agents installed in your workspace do not count as billable users.“ | D21 |
| Mitglied entfernen (Public API) | `POST /api/v1/workspaces/{slug}/members/remove/` – entfernt, deaktiviert in allen Projekten, **reduziert Seat-Anzahl** | D18; Dok. 21 F23 |
| Seat-Überlauf | Fehlerklasse „seat overflow“; CSV-Import: „Unable to import members due to seat limit restrictions.“; CTA „Add Seats“ | `self-hosting-101.md` Z. 80; R8; R7 |
| Airgapped | Mindestabnahme 100 Seats | D13 |

**CE:** keine Limits. **Portierung:** entfällt (ADR-001); „bezahlte Rolle“-Begriff wird nicht benötigt. `members/remove`-Endpunkt ohne Seat-Logik portieren (Dok. 21 F23). **Konfidenz:** hoch.

---

#### P08-25 – Storage-Limits

- Matrix (Cloud-only): Speicher je Workspace Free 5GB, Pro 1 TB, Business 5 TB, Enterprise Custom; „Max file size“ Free 5 MB, Pro 100 MB, Business 200 MB, Enterprise Custom; One „–“ (R1 Z. 1026–1053).
- CE: instanzweites `FILE_SIZE_LIMIT` (Default 5 242 880 Byte, `apps/api/plane/settings/common.py` Z. 389; zugleich `DATA_UPLOAD_MAX_MEMORY_SIZE` Z. 403), ausgeliefert als `config.file_size_limit` (`apps/api/plane/license/api/views/instance.py` Z. 142), Frontend `useFileSize` mit Fallback `MAX_FILE_SIZE` (`apps/web/hooks/use-file-size.ts`); Commercial-Prime-CLI fragt „Max file-upload size“ (Default 5 MB) ab (D15 `prime-cli.md`). Keine Speicherquote.
- **Portierung:** Max file size = Instanz-Einstellung (God Mode, großzügiger Default); keine Workspace-Speicherquote (ADR-004 „Storage-Quoten pro Plan entfallen“). **Konfidenz:** hoch.

---

#### P08-26 – Support, SLA, „Chat with us“

- Matrix: Kanäle Free Forum-Icon; One Mail + Forum; Pro Mail + Forum + Chat; Business/Enterprise „Full-suite professional services“; SLA Pro+ („SLAs are by priority of work item and tiers can be requested“, Link Talk-to-Sales) (R1 Z. 1209–1252); `ENTERPRISE_PLAN_FEATURES` „Full-suite professional services“ (R2 Z. 13).
- God Mode → General (Commercial, B11; D5): Abschnitt „Chat + telemetry“ mit „Chat with us – Let your users chat with us. Toggling Telemetry off turns this off automatically.“ und „Let Plane collect anonymous usage data – No PII is collected. This anonymized data is used to understand how you use Plane and build new features in line with our Telemetry Policy.“; Button „Save changes“. CE: nur der Telemetrie-Schalter (`apps/admin/app/(all)/(dashboard)/general/form.tsx` Z. 119–140); Modellfeld `Instance.is_support_required` (Default `true`) ohne UI (R10). Hilfe-Texte „Support“, „Message support“ (`common.json`).
- **CE-Status (Verifikation):** Stub/UI-Hülle im CE statt „teilweise“ – `is_support_required` kommt nur in `apps/api/plane/license/models/instance.py` Z. 36 und `packages/types/src/instance/base.ts` Z. 36 vor (`grep`), ohne Lese- oder Schreibzugriff.
- **Portierung:** entfällt (Vertrag/Organisation; ADR-004: kein externer Chat-Dienst, Telemetrie nach außen abgeschaltet – siehe Architektur). **Konfidenz:** hoch.

---

### 4.6 Querbezüge

#### P08-30 – IdP-Profil-Sync beim Login (CE, kein Bezahl-Feature)

CE synchronisiert bei OAuth-Login bestehender Nutzer Vorname, Nachname, Anzeigename und Avatar, wenn `ENABLE_GOOGLE_SYNC`/`ENABLE_GITHUB_SYNC`/`ENABLE_GITLAB_SYNC`/`ENABLE_GITEA_SYNC` = `"1"` (`Adapter.check_sync_enabled`, `sync_user_data`; `apps/api/plane/authentication/adapter/base.py` Z. 122–135, 274–305; Konfig-Schlüssel in R15 `auth.ts`). LDAP aktualisiert das Profil bei jedem Login (D3). Für SAML/OIDC empfiehlt sich dieselbe Option (`ENABLE_SAML_SYNC`, `ENABLE_OIDC_SYNC` – Vorschlag, UNVERIFIZIERT). **Konfidenz:** hoch (CE).

#### P08-31 – Mitglieder-CSV-Import (Querbezug)

EE-Texte im CE (R8, `project.json` Z. 370 ff.): Workspace „Import Members from CSV“ – „Upload a CSV with columns: Email, Display Name, First Name, Last Name, Role (5, 15, or 20)“; Projekt „Upload a CSV with columns: Email and Role (5=Guest, 15=Member, 20=Admin). Users must already be workspace members.“; Ergebnis-Statistiken Workspace „Successful“/„Failed“, Projekt „Added“/„Reactivated“/„Already Members“/„Skipped“; Seat-Fehler „Unable to import members due to seat limit restrictions.“ Vollständige Texte in Anhang A. Tier unklar (Dok. 20 PF-60). **Portierung:** ohne Seat-Prüfung; Domain-Policy (P08-10) anwenden. **Konfidenz:** hoch (Texte).

---
## 5. Offene Punkte / Unklarheiten

| Nr. | Thema | Unklarheit | Auswirkung / Vorschlag |
|---|---|---|---|
| O1 | Instanz-SSO vs. Workspace-SSO | Self-hosted-Doku beschreibt SSO **instanzweit** im God Mode (D1, D2, D3); die EE-Texte `sso.*` beschreiben **workspace-bezogenes** SSO mit verifizierten Domains (P08-03), vermutlich Cloud. Ob beides in derselben Edition koexistiert, ist nicht belegt. | **Rückfrage an den Auftraggeber:** beide Varianten bauen (Instanz-SSO für Self-hosted-Betrieb, Workspace-Identity für Mandantentrennung) oder nur Instanz-SSO? Vorschlag: beide, Workspace-Identity optional. Verifikation: Workspace-SSO ist laut plane.so/business ein Cloud-Merkmal („SSO on Cloud“, W17); eine verifizierte Domain gilt instanzweit nur für einen Workspace (W16). |
| O2 | 2FA und Passkeys | Kein öffentlicher Detail-Spec erreichbar (Faktoren, Recovery-Codes, Erzwingung je Workspace, Geltung für SSO-Logins, God-Mode). | Entwurf in P08-07/08 als Vorschlag; Nachrecherche (siehe O12). |
| O3 | Password Policy, Domain Security | Konfigurierbare Parameter, Geltungsbereich (Instanz/Workspace) und Durchsetzungspunkte nicht belegt. | Entwurf in P08-09/10; Nachrecherche. |
| O4 | RBAC, GAC, Approvals | Verifikation: GAC-Struktur (Custom Roles aus Permission Schemes, System-Schemes nicht editierbar, bedingte Rechte, Lese-API) jetzt belegt (P08-12/13). Offen: konkreter Permission-Katalog (Strings in `permissions`/`permission_grants`), vollständige Permissions-Matrix, Matrix-Zeile „Approvals“ (Workspace/Projekt/WIT). Nur Fragmente der Permissions-Matrix (W7, sekundär). | Permission-Katalog aus CE-Code (Dok. 03 §2.4) + Fragmenten ableiten (Aufgabe D05); Approvals = Dok. 25 F03. |
| O5 | Admin Interface | Bedeutung von „admin overview to manage workspace and project settings“ unbelegt; mögliche Überschneidung mit Workspace Governance (Dok. 25 F07). | Vorschlag P08-16; mit D13c abstimmen. |
| O6 | Offline-Group-Sync | Wie Gruppen ohne Login abgefragt werden (reines OIDC liefert Gruppen nur im Token). | Provider-Adapter optional; ohne Adapter Schalter „Offline sync“ deaktiviert (Dok. 21 O12). |
| O7 | SCIM | Nur Nennungen (D12, W12, W13); Endpunkte, Token-Verwaltung, Scope (Instanz/Workspace) unbekannt. | SCIM 2.0 Standard als Vorschlag; Nachrecherche. |
| O8 | Rollen-Slugs | D17 (v1-Group-Sync) nutzt Projekt-Slug `member`, D19 nennt Rolle „Contributor“. **Verifikation:** v2-Doku nennt die eingebauten Slugs `owner`, `member`, `contributor` und zeigt denselben Nutzer als Workspace-`member` und Projekt-`contributor` (D23); Changelog: „Project Member“ → „Contributor“ (W20). Widerspruch: Doku-Zusammenfassung „Contributor ab Business“ vs. Umbenennung der Free-Rolle (W18). Slugs für Workspace-Admin und Commenter weiterhin nicht belegt. | Vorschlag (korrigiert): Workspace `owner`, `admin`, `member`, `guest`; Projekt `admin`, `contributor`, `commenter`, `guest`; v1-Wert `member` für Projektrollen als Alias von `contributor` akzeptieren. |
| O9 | Audit-Log-Inhalt, Argus-Regeln | Verifikation: Felder, Kategorien, Filter und API-Pfade des Audit-Logs sind jetzt über D23 belegt. Offen: vollständiger `event_name`-Katalog (belegt nur `member.role_updated`, `auth.sign_in`, `role.permissions_updated`), Tabellenspalten/Exportformat der UI, Aufbewahrung; Erkennungsregeln/UI von Argus. | Vorschläge in P08-18/29; Nachrecherche. |
| O10 | God-Mode „Remove“ | Löschen vs. Deaktivieren eines Instanz-Users nicht beschrieben (nur „remove the user from the instance entirely“, Status „Suspended“ existiert). | Vorschlag: Deaktivieren (Soft), Daten bleiben. |
| O11 | UI 1:1 vs. ADR-001 | Wegfall von „Billing & Plans“-Eintrag, Editions-Badge (inkl. Versions-Tooltip „Version: v…“), Upgrade-Modal, Trial-Banner; Wort „seats“ im God-Mode-Untertitel „View and manage seats for all the members active in this instance“. | **Rückfrage an den Auftraggeber:** Versionsanzeige an anderer Stelle (z. B. Hilfe-Menü)? Untertitel neutralisieren („… all the members …“)? |
| O12 | Recherche-Lücke (Verifikation: teilweise geschlossen durch W15–W22; offen bleiben 2FA/Passkeys, Password Policy, Domain Security, Activity Logs, SCIM, Audit-Log-Aufbewahrung) | WebSearch-Budget des Autorenlaufs war erschöpft (Limit 200/Turn, geteilt); `docs.plane.so`/`plane.so` nicht abrufbar; GitHub-Doku-Repo nicht verfügbar. | Nachrecherche in einem Folgelauf mit Budget: `docs.plane.so/authentication/sso`, `…/authentication/group-sync`, `…/authentication/two-factor-authentication` (Pfad UNVERIFIZIERT), `…/workspaces-and-users/audit-logs`, `…/roles-and-permissions/permissions-matrix`, `…/roles-and-permissions/member-roles`, `…/workspace-administration/workspace-governance`, `plane.so/blog/introducing-granular-access-control-gac-ldap-idp-group-sync`, `plane.so/changelog/release-v3-1-0-audit-logs-skills-in-plane-ai-dashboards-and-more`, `plane.so/changelog/release-v3-2-0-workspace-governance-ai-memory-pii-scanning-and-more`, `plane.so/pricing`, `plane.so/enterprise-grid`. |
| O13 | SAML Entity ID | D1: `…/auth/saml/`; B2: `…/auth/saml/metadata/`. | Vorschlag in P08-01 (Metadaten-URL als Entity ID). |
| O14 | Airgapped-Pläne | D13 „exclusively for Enterprise Grid“ vs. D10 „Activate Pro or Business on Airgapped Edition“. | Irrelevant nach ADR-001/004 (Airgapped ist Grundeigenschaft). |
| O15 | „Business Plus“ | Einzige Nennung in `self-hosting-101.md` Z. 42; kein Enum, keine Matrix-Spalte. | Nur dokumentarisch; nach ADR-001 irrelevant. |
| O16 | Gäste im Free-Plan (Verifikation: **erledigt**) | Matrix: Free ✗ Gäste; CE (= Free-Parität) hat die Gast-Rolle ohne Einschränkung. Doku 2026: Guest „auf allen Plänen“ (W18). | Funktion bleibt (CE-Verhalten), Kontingent entfällt. |
| O17 | Ort der Session-Einstellungen | D6 nennt „System Configurations → Session settings“; auf keinem Screenshot sichtbar. | God-Mode-Seite „System Configurations“ neu anlegen oder in „General“ integrieren (Entscheidung D13c). |
| O18 | Tier-Widersprüche (Verifikation) | SAML/OIDC: Matrix One vs. Badges Pro; Rollen: Matrix Pro „Pre-defined roles“ vs. Doku Business; Custom Roles: Matrix Business „RBAC“ vs. Doku Enterprise Grid; Audit Logs: Matrix Business vs. Doku-Titel Enterprise Grid. In allen Fällen wurde die aktuellere/spezifischere Quelle gewählt; Dok. 21 F34 und Dok. 22 P03-F44 führen Audit Logs noch als Business. | Nach ADR-001 ohne Auswirkung auf die Portierung; die Schwester-Dokumente sollten beim nächsten Lauf angeglichen werden. |
| O19 | Rolle „Workspace Admin“ vs. CE-„Admin“ | Changelog: CE-„Workspace Admin“ heißt jetzt „Owner“, die neue Rolle „Workspace Admin“ liegt darunter (W20). Rechteumfang der neuen Admin-Rolle gegenüber Owner (außer Löschen/Ownership-Transfer) und Anzahl möglicher Owner sind nicht belegt. | Rechte-Matrix in Architektur D05 festlegen; Default: Admin = Owner-Rechte ohne Workspace-Löschung, Ownership-Transfer und Billing (Billing entfällt). |
| O20 | Workspace Activity Logs vs. Audit Logs | Unklar, ob die Matrix-Zeile „Workspace Activity Logs“ (Business) im heutigen Produkt eine eigene Oberfläche ist oder im Audit-Log (Enterprise Grid) aufging (Changelog v2.2.0 „audit logs for workspace and member activity“, nur über Dok. 20). | Getrennt portieren (P08-17 Work-Item-/Entitätsaktivität, P08-18 Sicherheits-/Admin-Audit); Zusammenlegung in der Architektur prüfen. |
| O21 | Namespace `instance` bei Rollen/Schemes | Die v2-Doku erlaubt `namespace = instance` (D23); Bedeutung (Instanz-Rollen für God Mode, z. B. Instance Admin) nicht beschrieben. | Vorerst nicht portieren; God-Mode-Rechte bleiben über `InstanceAdmin` (P08-27). |

---

## Anhang A: Vollständiges i18n-Inventar der Cluster-Texte (Englisch, `packages/i18n/src/locales/en/`)

Automatisch extrahiert (Skript liest nur JSON, führt keinen Repo-Code aus). Spalte „im CE-Code referenziert“: `ja`, wenn der Schlüssel als String-Literal oder als Präfix eines Template-Literals in `apps/**` oder `packages/**` (ohne `locales`) vorkommt; sonst `nein` (= EE-Text bzw. ungenutzt). 17 von 251 Schlüsseln sind im CE referenziert. Übersetzungen in 21 weiteren Locales (`bg`, `cs`, `de`, `es`, `fr`, `id`, `it`, `ja`, `ka-ge`, `ko`, `nl`, `pl`, `pt-BR`, `ro`, `ru`, `sk`, `tr-TR`, `ua`, `vi-VN`, `zh-CN`, `zh-TW`) liegen unter denselben Schlüsseln in `packages/i18n/src/locales/<locale>/`.

#### `auth.json` → `sso` (115 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `sso.header` | Identity | nein |
| `sso.description` | Configure your domain to access security features including single sign-on. | nein |
| `sso.domain_management.header` | Domain management | nein |
| `sso.domain_management.verified_domains.header` | Verified domains | nein |
| `sso.domain_management.verified_domains.description` | Verify the ownership of an email domain to enable single-sign on. | nein |
| `sso.domain_management.verified_domains.button_text` | Add domain | nein |
| `sso.domain_management.verified_domains.list.domain_name` | Domain name | nein |
| `sso.domain_management.verified_domains.list.status` | Status | nein |
| `sso.domain_management.verified_domains.list.status_verified` | Verified | nein |
| `sso.domain_management.verified_domains.list.status_failed` | Failed | nein |
| `sso.domain_management.verified_domains.list.status_pending` | Pending | nein |
| `sso.domain_management.verified_domains.add_domain.title` | Add domain | nein |
| `sso.domain_management.verified_domains.add_domain.description` | Add your domain to configure SSO and verify it. | nein |
| `sso.domain_management.verified_domains.add_domain.form.domain_label` | Domain | nein |
| `sso.domain_management.verified_domains.add_domain.form.domain_placeholder` | plane.so | nein |
| `sso.domain_management.verified_domains.add_domain.form.domain_required` | Domain is required | nein |
| `sso.domain_management.verified_domains.add_domain.form.domain_invalid` | Enter a valid domain name (e.g., plane.so) | nein |
| `sso.domain_management.verified_domains.add_domain.primary_button_text` | Add domain | nein |
| `sso.domain_management.verified_domains.add_domain.primary_button_loading_text` | Adding | nein |
| `sso.domain_management.verified_domains.add_domain.toast.success_title` | Success! | nein |
| `sso.domain_management.verified_domains.add_domain.toast.success_message` | Domain added successfully. Please verify it by adding the DNS TXT record. | nein |
| `sso.domain_management.verified_domains.add_domain.toast.error_message` | Failed to add domain. Please try again. | nein |
| `sso.domain_management.verified_domains.verify_domain.title` | Verify your domain | nein |
| `sso.domain_management.verified_domains.verify_domain.description` | Follow these steps to verify your domain. | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.label` | Instructions | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_1` | Go to the DNS settings for your domain host. | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_2.part_1` | Create a | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_2.part_2` | TXT record | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_2.part_3` | and paste the complete record value provided below. | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_3` | This update usually takes a few minutes but may take up to 72 hours to complete. | nein |
| `sso.domain_management.verified_domains.verify_domain.instructions.step_4` | Click "Verify domain" to confirm once your DNS record is updated. | nein |
| `sso.domain_management.verified_domains.verify_domain.verification_code_label` | TXT record value | nein |
| `sso.domain_management.verified_domains.verify_domain.verification_code_description` | Add this record to your DNS settings | nein |
| `sso.domain_management.verified_domains.verify_domain.domain_label` | Domain | nein |
| `sso.domain_management.verified_domains.verify_domain.primary_button_text` | Verify domain | nein |
| `sso.domain_management.verified_domains.verify_domain.primary_button_loading_text` | Verifying | nein |
| `sso.domain_management.verified_domains.verify_domain.secondary_button_text` | I'll do it later | nein |
| `sso.domain_management.verified_domains.verify_domain.toast.success_title` | Success! | nein |
| `sso.domain_management.verified_domains.verify_domain.toast.success_message` | Domain verified successfully. | nein |
| `sso.domain_management.verified_domains.verify_domain.toast.error_message` | Failed to verify domain. Please try again. | nein |
| `sso.domain_management.verified_domains.delete_domain.title` | Delete domain | nein |
| `sso.domain_management.verified_domains.delete_domain.description.prefix` | Are you sure you want to delete | nein |
| `sso.domain_management.verified_domains.delete_domain.description.suffix` | ? This action cannot be undone. | nein |
| `sso.domain_management.verified_domains.delete_domain.primary_button_text` | Delete | nein |
| `sso.domain_management.verified_domains.delete_domain.primary_button_loading_text` | Deleting | nein |
| `sso.domain_management.verified_domains.delete_domain.secondary_button_text` | Cancel | nein |
| `sso.domain_management.verified_domains.delete_domain.toast.success_title` | Success! | nein |
| `sso.domain_management.verified_domains.delete_domain.toast.success_message` | Domain deleted successfully. | nein |
| `sso.domain_management.verified_domains.delete_domain.toast.error_message` | Failed to delete domain. Please try again. | nein |
| `sso.providers.header` | Single sign-on | nein |
| `sso.providers.disabled_message` | Add a verified domain to configure SSO | nein |
| `sso.providers.configure.create` | Configure | nein |
| `sso.providers.configure.update` | Edit | nein |
| `sso.providers.switch_alert_modal.title` | Switch SSO Method to {newProviderShortName}? | nein |
| `sso.providers.switch_alert_modal.content` | You are about to enable {newProviderLongName} ({newProviderShortName}). This action will automatically disable {activeProviderLongName} ({activeProviderShortName}). Users attempting to sign in via {activeProviderShortName} will no longer be able to access the platform until they switch to the new method. Are you sure you want to proceed? | nein |
| `sso.providers.switch_alert_modal.primary_button_text` | Switch | nein |
| `sso.providers.switch_alert_modal.primary_button_text_loading` | Switching | nein |
| `sso.providers.switch_alert_modal.secondary_button_text` | Cancel | nein |
| `sso.providers.form_section.title` | IdP-provided details for {workspaceName} | nein |
| `sso.providers.form_action_buttons.saving` | Saving | nein |
| `sso.providers.form_action_buttons.save_changes` | Save changes | nein |
| `sso.providers.form_action_buttons.configure_only` | Configure only | nein |
| `sso.providers.form_action_buttons.configure_and_enable` | Configure and enable | nein |
| `sso.providers.form_action_buttons.default` | Save | nein |
| `sso.providers.setup_details_section.title` | {workspaceName} provided details for you IdP | nein |
| `sso.providers.setup_details_section.button_text` | Get setup details | nein |
| `sso.providers.saml.header` | Enable SAML | nein |
| `sso.providers.saml.description` | Configure your SAML identity provider to enable single sign-on. | nein |
| `sso.providers.saml.configure.title` | Enable SAML | nein |
| `sso.providers.saml.configure.description` | Verify the ownership of an email domain to access security features including single-sign on. | nein |
| `sso.providers.saml.configure.toast.success_title` | Success! | nein |
| `sso.providers.saml.configure.toast.create_success_message` | SAML provider created successfully. | nein |
| `sso.providers.saml.configure.toast.update_success_message` | SAML provider updated successfully. | nein |
| `sso.providers.saml.configure.toast.error_title` | Error! | nein |
| `sso.providers.saml.configure.toast.error_message` | Failed to save SAML provider. Please try again. | nein |
| `sso.providers.saml.setup_modal.web_details.header` | Web details | nein |
| `sso.providers.saml.setup_modal.web_details.entity_id.label` | Entity ID \| Audience \| Metadata information | nein |
| `sso.providers.saml.setup_modal.web_details.entity_id.description` | We will generate this bit of the metadata that identifies this Plane app as an authorized service on your IdP. | nein |
| `sso.providers.saml.setup_modal.web_details.callback_url.label` | SSO URL | nein |
| `sso.providers.saml.setup_modal.web_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | nein |
| `sso.providers.saml.setup_modal.web_details.logout_url.label` | SLO URL | nein |
| `sso.providers.saml.setup_modal.web_details.logout_url.description` | We will generate this for you. Add this in the Single Logout redirect URL field of your IdP. | nein |
| `sso.providers.saml.setup_modal.mobile_details.header` | Mobile details | nein |
| `sso.providers.saml.setup_modal.mobile_details.entity_id.label` | Entity ID \| Audience \| Metadata information | nein |
| `sso.providers.saml.setup_modal.mobile_details.entity_id.description` | We will generate this bit of the metadata that identifies this Plane app as an authorized service on your IdP. | nein |
| `sso.providers.saml.setup_modal.mobile_details.callback_url.label` | SSO URL | nein |
| `sso.providers.saml.setup_modal.mobile_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | nein |
| `sso.providers.saml.setup_modal.mobile_details.logout_url.label` | SLO URL | nein |
| `sso.providers.saml.setup_modal.mobile_details.logout_url.description` | We will generate this for you. Add this in the Logout redirect URL field of your IdP. | nein |
| `sso.providers.saml.setup_modal.mapping_table.header` | Mapping details | nein |
| `sso.providers.saml.setup_modal.mapping_table.table.idp` | IdP | nein |
| `sso.providers.saml.setup_modal.mapping_table.table.plane` | Plane | nein |
| `sso.providers.oidc.header` | Enable OIDC | nein |
| `sso.providers.oidc.description` | Configure your OIDC identity provider to enable single sign-on. | nein |
| `sso.providers.oidc.configure.title` | Enable OIDC | nein |
| `sso.providers.oidc.configure.description` | Verify the ownership of an email domain to access security features including single-sign on. | nein |
| `sso.providers.oidc.configure.toast.success_title` | Success! | nein |
| `sso.providers.oidc.configure.toast.create_success_message` | OIDC provider created successfully. | nein |
| `sso.providers.oidc.configure.toast.update_success_message` | OIDC provider updated successfully. | nein |
| `sso.providers.oidc.configure.toast.error_title` | Error! | nein |
| `sso.providers.oidc.configure.toast.error_message` | Failed to save OIDC provider. Please try again. | nein |
| `sso.providers.oidc.setup_modal.web_details.header` | Web details | nein |
| `sso.providers.oidc.setup_modal.web_details.origin_url.label` | Origin URL | nein |
| `sso.providers.oidc.setup_modal.web_details.origin_url.description` | We will generate this for this Plane app. Add this as a trusted origin on your IdP's corresponding field. | nein |
| `sso.providers.oidc.setup_modal.web_details.callback_url.label` | Redirect URL | nein |
| `sso.providers.oidc.setup_modal.web_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | nein |
| `sso.providers.oidc.setup_modal.web_details.logout_url.label` | Logout URL | nein |
| `sso.providers.oidc.setup_modal.web_details.logout_url.description` | We will generate this for you. Add this in the Logout redirect URL field of your IdP. | nein |
| `sso.providers.oidc.setup_modal.mobile_details.header` | Mobile details | nein |
| `sso.providers.oidc.setup_modal.mobile_details.origin_url.label` | Origin URL | nein |
| `sso.providers.oidc.setup_modal.mobile_details.origin_url.description` | We will generate this for this Plane app. Add this as a trusted origin on your IdP's corresponding field. | nein |
| `sso.providers.oidc.setup_modal.mobile_details.callback_url.label` | Redirect URL | nein |
| `sso.providers.oidc.setup_modal.mobile_details.callback_url.description` | We will generate this for you. Add this in the Sign-in redirect URL field of your IdP. | nein |
| `sso.providers.oidc.setup_modal.mobile_details.logout_url.label` | Logout URL | nein |
| `sso.providers.oidc.setup_modal.mobile_details.logout_url.description` | We will generate this for you. Add this in the Logout redirect URL field of your IdP. | nein |

#### `auth.json` → `auth.ldap` (2 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `auth.ldap.header.label` | Continue with {ldapProviderName} | nein |
| `auth.ldap.header.sub_header` | Enter your {ldapProviderName} credentials | nein |

#### `auth.json` → `auth.common.username` (2 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `auth.common.username.label` | Username | nein |
| `auth.common.username.placeholder` | Enter your username | nein |

#### `workspace-settings.json` → `workspace_settings.settings.identity` (3 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace_settings.settings.identity.title` | Identity | nein |
| `workspace_settings.settings.identity.heading` | Identity | nein |
| `workspace_settings.settings.identity.description` | Configure your domain and enable Single sign-on | nein |

#### `workspace-settings.json` → `workspace_settings.settings.group_syncing` (33 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace_settings.settings.group_syncing.title` | Group syncing | nein |
| `workspace_settings.settings.group_syncing.heading` | Group syncing | nein |
| `workspace_settings.settings.group_syncing.description` | Link identity provider groups to projects and roles. User access updates automatically when group membership changes in your IdP, simplifying onboarding and offboarding. | nein |
| `workspace_settings.settings.group_syncing.enable.title` | Enable group syncing | nein |
| `workspace_settings.settings.group_syncing.enable.description` | Automatically add users to projects based on identity provider groups. | nein |
| `workspace_settings.settings.group_syncing.config.title` | Configure group sync | nein |
| `workspace_settings.settings.group_syncing.config.description` | Set up how identity provider groups are mapped to projects and roles. | nein |
| `workspace_settings.settings.group_syncing.config.sync_on_login.title` | Sync on login | nein |
| `workspace_settings.settings.group_syncing.config.sync_on_login.description` | Update group membership and project access when a user signs in. | nein |
| `workspace_settings.settings.group_syncing.config.sync_offline.title` | Offline sync | nein |
| `workspace_settings.settings.group_syncing.config.sync_offline.description` | Runs sync every six hours automatically, without waiting for users to log in. | nein |
| `workspace_settings.settings.group_syncing.config.auto_remove.title` | Auto remove | nein |
| `workspace_settings.settings.group_syncing.config.auto_remove.description` | Automatically remove users from projects when they no longer match the group. | nein |
| `workspace_settings.settings.group_syncing.config.group_attribute_key.title` | Group attribute key | nein |
| `workspace_settings.settings.group_syncing.config.group_attribute_key.description` | The identity provider attribute used to identify and sync user groups. | nein |
| `workspace_settings.settings.group_syncing.config.group_attribute_key.placeholder` | Groups | nein |
| `workspace_settings.settings.group_syncing.group_mapping.title` | Group mapping | nein |
| `workspace_settings.settings.group_syncing.group_mapping.description` | Link identity provider groups to projects and roles. | nein |
| `workspace_settings.settings.group_syncing.group_mapping.button_text` | Add new group sync | nein |
| `workspace_settings.settings.group_syncing.toast.updating` | Updating group syncing feature | nein |
| `workspace_settings.settings.group_syncing.toast.success` | Group syncing feature updated successfully. | nein |
| `workspace_settings.settings.group_syncing.toast.error` | Failed to update group syncing feature! | nein |
| `workspace_settings.settings.group_syncing.delete_modal.title` | Delete group sync | nein |
| `workspace_settings.settings.group_syncing.delete_modal.content` | New users from this identity group will no longer be added to the project. Users already added will keep their current role. | nein |
| `workspace_settings.settings.group_syncing.modal.idp_group_name.text` | User group | nein |
| `workspace_settings.settings.group_syncing.modal.idp_group_name.required` | User group is required | nein |
| `workspace_settings.settings.group_syncing.modal.idp_group_name.placeholder` | Enter the IdP group names | nein |
| `workspace_settings.settings.group_syncing.modal.project.text` | Project | nein |
| `workspace_settings.settings.group_syncing.modal.project.required` | Project is required | nein |
| `workspace_settings.settings.group_syncing.modal.project.placeholder` | Select a project | nein |
| `workspace_settings.settings.group_syncing.modal.default_role.text` | Project role | nein |
| `workspace_settings.settings.group_syncing.modal.default_role.required` | Project role is required | nein |
| `workspace_settings.settings.group_syncing.modal.default_role.placeholder` | Select a project role | nein |

#### `empty-state.json` → `settings_empty_state.group_syncing` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `settings_empty_state.group_syncing.title` | No group mappings yet | nein |

#### `workspace-settings.json` → `workspace_settings.settings.billing_and_plans` (6 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace_settings.settings.billing_and_plans.heading` | Billing & Plans | ja |
| `workspace_settings.settings.billing_and_plans.description` | Choose your plan, manage subscriptions, and easily upgrade as your needs grow. | ja |
| `workspace_settings.settings.billing_and_plans.title` | Billing & Plans | ja |
| `workspace_settings.settings.billing_and_plans.current_plan` | Current plan | nein |
| `workspace_settings.settings.billing_and_plans.free_plan` | You are currently using the free plan | nein |
| `workspace_settings.settings.billing_and_plans.view_plans` | View plans | nein |

#### `workspace-settings.json` → `workspace_settings.settings.cancel_trial` (8 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace_settings.settings.cancel_trial.title` | Cancel your trial first. | nein |
| `workspace_settings.settings.cancel_trial.description` | You have an active trial to one of our paid plans. Please cancel it first to proceed. | nein |
| `workspace_settings.settings.cancel_trial.dismiss` | Dismiss | nein |
| `workspace_settings.settings.cancel_trial.cancel` | Cancel trial | nein |
| `workspace_settings.settings.cancel_trial.cancel_success_title` | Trial cancelled. | nein |
| `workspace_settings.settings.cancel_trial.cancel_success_message` | You can now delete the workspace. | nein |
| `workspace_settings.settings.cancel_trial.cancel_error_title` | That didn't work. | nein |
| `workspace_settings.settings.cancel_trial.cancel_error_message` | Try again, please. | nein |

#### `workspace-settings.json` → `workspace_settings.settings.general.delete_modal` (8 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace_settings.settings.general.delete_modal.title` | Are you sure you want to delete this workspace? | ja |
| `workspace_settings.settings.general.delete_modal.description` | You have an active trial to one of our paid plans. Please cancel it first to proceed. | nein |
| `workspace_settings.settings.general.delete_modal.dismiss` | Dismiss | nein |
| `workspace_settings.settings.general.delete_modal.cancel` | Cancel trial | nein |
| `workspace_settings.settings.general.delete_modal.success_title` | Workspace deleted. | ja |
| `workspace_settings.settings.general.delete_modal.success_message` | You will soon go to your profile page. | ja |
| `workspace_settings.settings.general.delete_modal.error_title` | That didn't work. | ja |
| `workspace_settings.settings.general.delete_modal.error_message` | Try again, please. | ja |

#### `home.json` → `home.business_trial_banner` (6 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `home.business_trial_banner.title` | Your 14-day Business plan trial is live! | nein |
| `home.business_trial_banner.description` | Explore all Business features. When you're ready, choose to subscribe. You'll not be billed automatically. | nein |
| `home.business_trial_banner.trial_ends_today` | Trial ends today | nein |
| `home.business_trial_banner.trial_ends_in_days` | Trial ends in {days, plural, one {# day} other {# days}} | nein |
| `home.business_trial_banner.start_subscription` | Start subscription | nein |
| `home.business_trial_banner.explore_business_features` | Explore Business features | nein |

#### `common.json` → `common.upgrade` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `common.upgrade` | Upgrade | nein |

#### `common.json` → `common.add_seats` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `common.add_seats` | Add Seats | nein |

#### `common.json` → `common.upgrade_cta` (2 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `common.upgrade_cta.higher_subscription` | Upgrade to higher subscription | nein |
| `common.upgrade_cta.talk_to_sales` | Talk to Sales | ja |

#### `common.json` → `upgrade_request` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `upgrade_request` | Ask your Workspace Admin to upgrade. | nein |

#### `common.json` → `upgrade` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `upgrade` | Upgrade | ja |

#### `navigation.json` → `sidebar.upgrade` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `sidebar.upgrade` | Upgrade | nein |

#### `navigation.json` → `sidebar.upgrade_plan` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `sidebar.upgrade_plan` | Upgrade plan | nein |

#### `navigation.json` → `sidebar.plane_pro` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `sidebar.plane_pro` | Plane Pro | nein |

#### `accessibility.json` → `aria_labels.projects_sidebar.edition_badge` (1 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `aria_labels.projects_sidebar.edition_badge` | Open paid plans' modal | ja |

#### `workspace.json` → `workspace.members_import` (24 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `workspace.members_import.title` | Import Members from CSV | nein |
| `workspace.members_import.description` | Upload a CSV with columns: Email, Display Name, First Name, Last Name, Role (5, 15, or 20) | nein |
| `workspace.members_import.dropzone.active` | Drop CSV file here | nein |
| `workspace.members_import.dropzone.inactive` | Drag & drop or click to upload | nein |
| `workspace.members_import.dropzone.file_type` | Only .csv files supported | nein |
| `workspace.members_import.buttons.cancel` | Cancel | nein |
| `workspace.members_import.buttons.import` | Import | nein |
| `workspace.members_import.buttons.try_again` | Try Again | nein |
| `workspace.members_import.buttons.close` | Close | nein |
| `workspace.members_import.buttons.done` | Done | nein |
| `workspace.members_import.progress.uploading` | Uploading... | nein |
| `workspace.members_import.progress.importing` | Importing... | nein |
| `workspace.members_import.summary.title.failed` | Import Failed | nein |
| `workspace.members_import.summary.title.complete` | Import Complete | nein |
| `workspace.members_import.summary.message.seat_limit` | Unable to import members due to seat limit restrictions. | nein |
| `workspace.members_import.summary.message.success` | Successfully added {count} member{plural} to the workspace. | nein |
| `workspace.members_import.summary.message.no_imports` | No members were imported from the CSV file. | nein |
| `workspace.members_import.summary.stats.successful` | Successful | nein |
| `workspace.members_import.summary.stats.failed` | Failed | nein |
| `workspace.members_import.summary.download_errors` | Download errors | nein |
| `workspace.members_import.toast.invalid_file.title` | Invalid file | nein |
| `workspace.members_import.toast.invalid_file.message` | Only CSV files are supported. | nein |
| `workspace.members_import.toast.import_failed.title` | Import failed | nein |
| `workspace.members_import.toast.import_failed.message` | Something went wrong. | nein |

#### `project.json` → `project.members_import` (25 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `project.members_import.title` | Import Members from CSV | nein |
| `project.members_import.description` | Upload a CSV with columns: Email and Role (5=Guest, 15=Member, 20=Admin). Users must already be workspace members. | nein |
| `project.members_import.download_sample` | Download sample CSV | nein |
| `project.members_import.dropzone.active` | Drop CSV file here | nein |
| `project.members_import.dropzone.inactive` | Drag & drop or click to upload | nein |
| `project.members_import.dropzone.file_type` | Only .csv files supported | nein |
| `project.members_import.buttons.cancel` | Cancel | nein |
| `project.members_import.buttons.import` | Import | nein |
| `project.members_import.buttons.try_again` | Try Again | nein |
| `project.members_import.buttons.close` | Close | nein |
| `project.members_import.buttons.done` | Done | nein |
| `project.members_import.progress.uploading` | Uploading... | nein |
| `project.members_import.progress.importing` | Importing... | nein |
| `project.members_import.summary.title.complete` | Import Complete | nein |
| `project.members_import.summary.message.success` | Successfully imported {count} member{plural} to the project. | nein |
| `project.members_import.summary.message.no_imports` | No new members were imported from the CSV file. | nein |
| `project.members_import.summary.stats.added` | Added | nein |
| `project.members_import.summary.stats.reactivated` | Reactivated | nein |
| `project.members_import.summary.stats.already_members` | Already Members | nein |
| `project.members_import.summary.stats.skipped` | Skipped | nein |
| `project.members_import.summary.download_errors` | Download skipped details | nein |
| `project.members_import.toast.invalid_file.title` | Invalid file | nein |
| `project.members_import.toast.invalid_file.message` | Only CSV files are supported. | nein |
| `project.members_import.toast.import_failed.title` | Import failed | nein |
| `project.members_import.toast.import_failed.message` | Something went wrong. | nein |

#### `project-settings.json` → `project_settings.members.guest_super_permissions` (2 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `project_settings.members.guest_super_permissions.title` | Grant view access to all work items for guest users: | nein |
| `project_settings.members.guest_super_permissions.sub_heading` | This will allow guests to have view access to all the project work items. | nein |

#### `common.json` → `role_details` (6 Schlüssel)

| Schlüssel | Text (en) | im CE-Code referenziert |
|---|---|---|
| `role_details.guest.title` | Guest | ja |
| `role_details.guest.description` | External members of organizations can be invited as guests. | ja |
| `role_details.member.title` | Member | ja |
| `role_details.member.description` | Ability to read, write, edit, and delete entities inside projects, cycles, and modules | ja |
| `role_details.admin.title` | Admin | ja |
| `role_details.admin.description` | All permissions set to true within the workspace. | ja |

---

## Anhang B: Inventar der CE-Extension-Points und CE-Spuren dieses Clusters

| Nr. | Pfad | Inhalt im CE | Bedeutung für EE-Feature |
|---|---|---|---|
| B-01 | `packages/types/src/instance/auth-ee.ts` | `export type TExtendedLoginMediums = never;` `export type TExtendedInstanceAuthenticationModeKeys = never;` | Erweiterung um `oidc`, `saml`, `ldap` (P08-01/02/04) |
| B-02 | `packages/types/src/instance/auth.ts` | `TCoreInstanceAuthenticationModeKeys` (`unique-codes`, `passwords-login`, `google`, `github`, `gitlab`, `gitea`); `TInstanceAuthenticationModeKeys = TCoreInstanceAuthenticationModeKeys`; `TInstanceAuthenticationModes.unavailable?`; `TInstanceAuthenticationMethodKeys` (`ENABLE_SIGNUP`, `ENABLE_MAGIC_LINK_LOGIN`, `ENABLE_EMAIL_PASSWORD`, `IS_GOOGLE_ENABLED`, `IS_GITHUB_ENABLED`, `IS_GITLAB_ENABLED`, `IS_GITEA_ENABLED`); Sync-Schlüssel `ENABLE_*_SYNC`; `TOAuthOption`, `TOAuthConfigs` | Muster für SSO-Konfigurationsschlüssel |
| B-03 | `packages/types/src/instance/base.ts` | `TLoginMediums = TCoreLoginMediums \| TExtendedLoginMediums`; `IInstance.license_key`, `is_activated`, `user_count`, `whitelist_emails`, `is_support_required` | Lizenz-Altfelder (P08-19/22), Domain-Whitelist (P08-10), Support (P08-26) |
| B-04 | `packages/constants/src/auth/extended.ts` | `EXTENDED_LOGIN_MEDIUM_LABELS: Record<TExtendedLoginMediums, string> = {}` | Labels „OIDC“, „SAML“, „LDAP“ für Spalte „Authentication“ (R23) |
| B-05 | `packages/constants/src/auth/core.ts`, `index.ts` Z. 172–175 | `CORE_LOGIN_MEDIUM_LABELS` (Email, Magic code, GitHub, GitLab, Google, Gitea); `LOGIN_MEDIUM_LABELS = {...CORE, ...EXTENDED}` | dto. |
| B-06 | `apps/web/hooks/oauth/extended.tsx`, `apps/web/hooks/oauth/index.ts` | `useExtendedOAuthConfig` → `{ isOAuthEnabled: false, oAuthOptions: [] }`; `useOAuthConfig` vereinigt Core + Extended | Login-Buttons SSO/LDAP/Passkey (Web) |
| B-07 | `apps/space/hooks/oauth/extended.tsx` | identischer Stub | Login-Buttons in Space |
| B-08 | `apps/admin/hooks/oauth/index.ts`, `core.tsx` | `useAuthenticationModes` liefert nur die sechs Core-Modi | God-Mode-Karten OIDC/SAML/LDAP |
| B-09 | `apps/admin/components/authentication/authentication-method-card.tsx` Z. 17–31 | Prop `unavailable` → `opacity-50` (im CE nie gesetzt) | Darstellung nicht verfügbarer Modi (Upsell) – entfällt |
| B-10 | `apps/admin/components/common/header/extended.ts` | `EXTENDED_HEADER_SEGMENT_LABELS: Record<string, string> = {}` | Breadcrumb-Labels für EE-God-Mode-Routen (z. B. „OIDC“, „SAML“, „LDAP“, „Billing“, „User Management“) |
| B-11 | `apps/admin/hooks/use-sidebar-menu/core.ts`, `index.ts`, `types.ts` | sechs Menüeinträge (General, Email, Authentication, Workspaces, Artificial intelligence, Images in Plane) | Ergänzung „User Management“ (P08-27), ggf. „System Configurations“ (P08-28); „Billing“ entfällt |
| B-12 | `apps/admin/app/routes.ts` | Routen `general`, `workspace`, `workspace/create`, `email`, `authentication`, `authentication/{github,gitlab,google,gitea}`, `ai`, `image` | neue Routen `authentication/{oidc,saml,ldap}`, `user-management` |
| B-13 | `apps/web/app/routes/extended.ts` | `extendedRoutes: RouteConfigEntry[] = []` | Web-Routen für Identity, Group syncing, Roles, Activity, Audit logs |
| B-14 | `packages/types/src/settings.ts`, `packages/constants/src/settings/workspace.ts`, `apps/web/components/settings/workspace/sidebar/item-icon.tsx` | `TWorkspaceSettingsTabs` = `general`, `members`, `billing-and-plans`, `export`, `webhooks`; Kategorien `administration`, `features`, `developer` | neue Tabs (Identity, Group syncing, Roles, Activity, Audit logs); `billing-and-plans` entfällt |
| B-15 | `apps/web/store/workspace/index.ts` Z. 66, 385–391 | `mutateWorkspaceMembersActivity` No-op | Mitglieder-Aktivität (P08-17) bzw. Seat-Daten (UNVERIFIZIERT) |
| B-16 | `apps/api/plane/license/models/instance.py` | `InstanceEdition` nur `PLANE_COMMUNITY`; `Instance.whitelist_emails`, `is_support_required`, `is_verified`, `edition`; `InstanceAdmin`; `InstanceConfiguration` | Editions-/Lizenzmodell (entfällt), Konfig-Speicher für SSO/LDAP |
| B-17 | `apps/api/plane/license/migrations/0001_initial.py` (Felder `license_key` 256, `user_count`), `0002`/`0003` (`product` Default `plane-ce`), `0005_rename_product_instance_edition_and_more.py` | `product` → `edition`; `license_key`, `user_count` entfernt; `is_test` neu | historische Lizenzfelder |
| B-18 | `apps/api/plane/db/models/user.py` | `User.is_managed`, `is_password_expired`, `is_password_reset_required` (Migration 0116), `last_login_medium`; `Profile.billing_address_country` (Default „INDIA“), `billing_address`, `has_billing_address`, `company_name`; `Account.PROVIDER_CHOICES` | Password-Policy (P08-09), God-Mode-Invite (P08-27), SCIM (P08-06), Billing (entfällt) |
| B-19 | `apps/api/plane/authentication/adapter/error.py` | Codes 5000–5999; freie Bereiche in OAuth-Block (5106–5109, 5113–5114, 5116–5119) | Platz für SSO-/LDAP-/2FA-Codes (Vorschlag) |
| B-20 | `apps/api/plane/authentication/utils/password.py` | `is_password_strong` (zxcvbn ≥ 3, Fenster 128 Zeichen) | Password Policy (P08-09) |
| B-21 | `apps/api/bin/docker-entrypoint-api.sh` Z. 10–24, `apps/api/bin/docker-entrypoint-api-local.sh` Z. 21–24, `apps/api/plane/license/management/commands/register_instance.py` | `MACHINE_SIGNATURE` (SHA-256) → `register_instance` | Lizenzbindung an Maschine (entfällt) |
| B-22 | `packages/constants/src/workspace.ts` Z. 12 ff. (`RESTRICTED_URLS`), `apps/api/plane/utils/constants.py` (`RESTRICTED_WORKSPACE_SLUGS`) | Beide Listen sind identisch (je 65 Einträge inkl. Dubletten): `404`, `accounts`, `api`, `create-workspace`, `god-mode`, `installations`, `invitations`, `onboarding`, `profile`, `spaces`, `workspace-invitations`, `password`, `flags`, `monitor`, `monitoring`, `ingest`, `plane-pro`, `plane-ultimate`, `enterprise`, `plane-enterprise`, `disco`, `silo`, `chat`, `calendar`, `drive`, `channels`, `upgrade`, `billing`, `sign-in`, `sign-up`, `signin`, `signup`, `config`, `live`, `admin`, `m`, `import`, `importers`, `integrations`, `integration`, `configuration`, `initiatives`, `initiative`, `config` (doppelt), `workflow`, `workflows`, `epics`, `epic`, `story`, `mobile`, `dashboard`, `desktop`, `onload`, `real-time`, `one`, `pages`, `mobile` (doppelt), `business`, `pro`, `settings`, `monitor` (doppelt), `license`, `licenses`, `instances`, `instance`. Cluster-relevant: `billing`, `upgrade`, `license`, `licenses`, `monitor`, `monitoring`, `enterprise`, `plane-enterprise`, `plane-pro`, `plane-ultimate`, `one`, `pro`, `business`, `instance`, `instances`, `admin`, `god-mode` | Slug-Reservierung bleibt (CE-Verhalten) |
| B-23 | `apps/web/components/workspace/billing/root.tsx`, `comparison/*.tsx`; `apps/web/components/license/modal/upgrade-modal.tsx`, `modal/card/{base-paid-plan-card,checkout-button,discount-info,free-plan,plan-upgrade,talk-to-sales}.tsx`; `apps/web/components/workspace/edition-badge.tsx` | Billing-Seite, Upgrade-Modal („Upgrade to a paid plan and unlock missing features.“), Editions-Badge „Community“ | entfällt (ADR-001) |
| B-24 | `packages/constants/src/subscription.ts`, `packages/constants/src/payment.ts`, `packages/types/src/payment.ts`, `packages/utils/src/subscription.ts`, `packages/constants/src/endpoints.ts` Z. 31–33 | Plan-Listen, Preise, Redirect-URLs, Marketing-Links | entfällt |
| B-25 | `packages/blocks/src/empty-state/assets/horizontal-stack/group-syncing.tsx`; Registry `asset-registry.tsx` Z. 75–77 | Illustration `GroupSyncingHorizontalStackIllustration` | Leerzustand Group syncing (P08-05) |
| B-26 | `@makeplane/propel@0.7.3` `dist/icons/other-products/{oidc,saml}.d.ts`; `dist/icons/miscellaneous/{audit-logs,access-and-roles,shield,shield-minus,key,billings,approver,upgrade,deactivated-user,lock-keyhole-circle,file-key,logs,logs-alt,log-config,activity,message-support,folder-lock,group-sync,pii-scanner}-{outline,filled}.d.ts`, zusätzlich nur `user-cog-outline.d.ts` und nur `upgrade-alt-filled.d.ts` (Verifikation korrigiert; `group-sync`, `pii-scanner` ergänzt) | Icons `Oidc`, `Saml`, `AuditLogsOutline`, `AccessAndRolesOutline`, `ShieldOutline`, `ShieldMinusOutline`, `KeyOutline`, `BillingsOutline`, `ApproverOutline`, `UpgradeOutline`, `DeactivatedUserOutline`, `LockKeyholeCircleOutline`, `FileKeyOutline`, `LogsOutline`, `LogsAltOutline`, `LogConfigOutline`, `ActivityOutline`, `MessageSupportOutline`, `FolderLockOutline`, `GroupSyncOutline`, `PiiScannerOutline` (+ `*Filled`); `UserCogOutline` (ohne Filled), `UpgradeAltFilled` (ohne Outline). Im CE verwendet: `AccessAndRolesOutline` (God-Mode-Dropdown), `KeyOutline` (Admin-Auth „Passwords“, Profil „API tokens“), `BillingsOutline` (Settings „Billing & Plans“), `DeactivatedUserOutline` (Mitgliederliste), `ActivityOutline` (Power K); übrige ungenutzt | Icon-Quelle für 1:1-UI |
| B-27 | `deployments/cli/community/restore-airgapped.sh` | Restore-Skript für Airgapped-Commercial | Airgapped-Migration (entfällt) |
| B-28 | i18n (Anhang A) | 251 Schlüssel, davon EE-only siehe Methode §1.4 | UI-Texte 1:1 |

---

## Anhang C: Inventar der Referenz-Screenshots (Commercial-UI)

Alle Dateien unter `/home/user/makeplane/developer-docs/docs/public/images/` (nur gelesen). Für die visuelle Abnahme (ADR-005) sind sie die einzige verfügbare Bildreferenz der Commercial-UI dieses Clusters; Pixelwerte sind Screenshot-Größen.

| Datei | Größe | Inhalt (gesichtet) | Feature |
|---|---|---|---|
| `custom-sso/oidc-oauth.png` | 4594×1852 | God Mode (heller Modus, ältere Sidebar ohne Billing) → Authentication → OIDC: Kopf mit Switch, Formular 7 Felder, „Plane-provided details for your IdP“ WEB/MOBILE | P08-02 |
| `custom-sso/saml-oauth.png` | 4621×2350 | God Mode → Authentication → SAML: Formular 5 Felder, WEB/MOBILE, MAPPING | P08-01 |
| `custom-sso/instance-login.png` | 1920×1069 | Sign-up-Seite (dunkel) „Create your account“ mit „Continue“ und Button „Sign up with Okta“ | P08-01/02 |
| `custom-sso/plane-login.png` | 1920×1071 | wie oben, Button hervorgehoben | P08-01/02 |
| `custom-sso/okta-signin.webp` | – | Okta-Anmeldeseite (Drittanbieter) | – |
| `custom-sso/github-oauth.png`, `google-oauth.png` | 4599×1298, 4585×1347 | CE-OAuth-Konfiguration | CE |
| `ldap/enable-ldap.webp` | 2868×1494 | God Mode (dunkel) Authentication-Liste: Unique codes, Passwords, Google, GitHub, GitLab, Gitea, OIDC, SAML (je „Configure“), LDAP („Edit“ + Switch an); Sidebar mit „Billing – Active plans“ | P08-01/02/04 |
| `ldap/ldap-configuration.webp` | 2814×1470 | LDAP-Konfiguration (Server URI, Bind DN, Bind Password, User Search Base, User Search Filter, User Attributes …) + „Authentication Endpoint“ | P08-04 |
| `ldap/sign-in-ldap.webp` | 2978×1452 | Login „Work in all dimensions. Welcome back to Plane.“ mit „Sign in with LDAP“ über „or“ und E-Mail-Feld | P08-04 |
| `instance-admin/god-mode-authentication.webp` | – | God Mode (hell): „Manage authentication modes for your instance“, „Allow anyone to sign up even without an invite“, Karten inkl. OIDC/SAML/LDAP mit „Edit“ + Switch; Sidebar inkl. „Billing“, „User Management“, „Artificial intelligence (deprecated)“ | P08-01/02/04/27 |
| `instance-admin/god-mode-general.webp` | 3186×1712 | „General settings“, „Instance details“ (Name of instance, Email, Instance ID), „Chat + telemetry“ (Chat with us, Let Plane collect anonymous usage data), „Save changes“ | P08-26 |
| `instance-admin/user-management.webp` | 3822×912 | „User Management“-Tabelle | P08-27 |
| `instance-admin/invite-instance-admin.webp` | – | Modal „Invite instance admin“ | P08-27 |
| `instance-admin/user-actions.webp` | – | Zeilenmenü „Remove admin access“ / „Remove“ | P08-27 |
| `activate-license/activate-enterprise-plan.webp` | 3024×1655 | God Mode → Billing „Billings and plans“, Karte „Activate Enterprise license“ (Schlüssel) | P08-20 |
| `activate-license/upload-airgapped-enterprise.webp` | 1920×961 | God Mode → Billing, Lizenzdatei + „Instance details“ | P08-21 |
| `activate-license/enter-license-key-selfhosted.webp` | 2520×1478 | Workspace „Billing and plans“ mit Modal „Activate Plane Pro“ | P08-19 |
| `activate-license/upload-airgapped-license-file.webp` | 1436×970 | Modal „Activate plane-test“ mit Datei-Upload und „Plane provided details“ | P08-21 |
| `activate-license/pro-activated-cloud.webp` | 2500×1338 | „Billing and plans“ mit aktivem Pro | P08-19 |
| `activate-license/billing-and-plans-cloud.webp` | 2476×1544 | „Billing and plans“ Cloud Free mit Trial | P08-19 |
| `activate-license/activate-pro-license.webp`, `copy-license-key.webp`, `download-license.webp`, `workspace-settings.webp` | 2499×1704, 2708×1174, 2907×934, 3000×838 | Prime-Portal bzw. Navigation zu Workspace Settings (`workspace-settings.webp` gesichtet: Workspace-Dropdown mit „Workspace settings“) | P08-19/22 |

**Hinweis zur Optik:** Die Screenshots stammen aus unterschiedlichen Versionen (z. B. Sidebar-Reihenfolge „Workspaces“ vor/nach „Email“; SSO-Button unter bzw. über dem E-Mail-Feld). Maßgeblich für die 1:1-UI ist die **CE-Komponentenbasis v1.4.2** (Propel 0.7.3, `apps/admin`), in die die EE-Elemente im Stil der jeweils neuesten Screenshots (B4, B5, B6, B10) eingefügt werden.

---

## Verifikations-Protokoll

Verifikationslauf vom 22.10.2026 (Skeptiker/Verifizierer Cluster P08). Geprüft wurden (a) jede Tier-Zuordnung gegen `apps/web/components/workspace/billing/comparison/plans.tsx`, `packages/constants/src/subscription.ts`, die Schwester-Dokumente `migration/features/20-*.md` bis `28-*.md` (einschließlich der verifizierten Listen `_data/P01.paid.json`, `P02.paid.json`, `P03.paid.json`, `P05.paid.json`, `P06.paid.json`) und gezielte WebSearch-Abfragen, (b) jeder CE-Status per `grep`/Lesen im Repo `/home/user/plane`, (c) die Vollständigkeit des Clusters gegen Developer-Docs (Branch `master` offline und Branch `docs/api-reference-v2`, D23), Helm-Chart und Propel-Icons, (d) Beschreibungen auf erfundene oder übertriebene Aussagen. Korrekturen sind direkt im Text eingearbeitet und mit „Verifikation“ markiert. Außerhalb von `migration/` wurde nichts geändert; kein Commit.

### V.1 Bestätigte Aussagen (Stichproben mit Beleg)

| Aussage im Dokument | Prüfung | Ergebnis |
|---|---|---|
| Matrix-Zeilen Kap. 2 (Z. 676, 695, 706, 717/719, 729, 740, 751/753, 1032, 1043, 1060, 1071/1073, 1083, 1095, 1106, 1117/1119, 1136–1193, 1209, 1235) und Zellwerte | `grep -n 'title:\|comingSoon\|selfHostedOnly\|cloudOnly'` und Lesen `plans.tsx` Z. 660–1311 | bestätigt, alle Zellwerte stimmen |
| `planHighlights` Z. 1304–1308, `PLANE_PLANS` Z. 1266–1301, Pro 8/6 $, Business/Enterprise „Talk to Sales“, „Quote on request“, Badge „Popular“ | `plans.tsx`; `plan-detail.tsx` Z. 41, 63 | bestätigt |
| `ENTERPRISE_PLAN_FEATURES` Z. 7–14, `BUSINESS_PLAN_FEATURES` Z. 16–23, `ONE_PLAN_FEATURES` Z. 34–41, `FREE_PLAN_UPGRADE_FEATURES` Z. 43–48 inkl. Einzelzeilen 8, 9, 10, 13, 18, 35, 44 | `cat -n packages/constants/src/subscription.ts` | bestätigt |
| Extension-Points `TExtendedLoginMediums = never`, `TExtendedInstanceAuthenticationModeKeys = never`, `EXTENDED_LOGIN_MEDIUM_LABELS = {}`, `useExtendedOAuthConfig` (Web und Space funktional identisch), `EXTENDED_HEADER_SEGMENT_LABELS = {}`, Prop `unavailable` | Lesen der Dateien | bestätigt |
| Keine 2FA-/Passkey-Spur im CE | `grep -rniE "two_factor\|two-factor\|twofactor\|\b2fa\b\|totp\|\bmfa\b\|passkey\|webauthn"` über `apps`, `packages` | nur `plans.tsx` – bestätigt |
| `is_password_expired`, `is_password_reset_required` ungenutzt; `whitelist_emails` ungenutzt; `is_support_required` ungenutzt | `grep` ohne Migrationen | nur Modell (+ Typ) – bestätigt |
| `mutateWorkspaceMembersActivity` No-op | `apps/web/store/workspace/index.ts` Z. 66, 385–391 | bestätigt; ergänzend: **kein Aufrufer** im gesamten Repo |
| `user-activity`-Endpunkte | `apps/api/plane/app/urls/workspace.py` Z. 137–146 | bestätigt |
| `InstanceAdminEndpoint` (POST nur für existierende User, `role` Default 20; DELETE mit `pk`) | `apps/api/plane/license/api/views/admin.py` Z. 47–88; `apps/api/plane/license/urls.py` Z. 25, 37 | bestätigt |
| CE-God-Mode: 6 Sidebar-Einträge, Routen | `apps/admin/hooks/use-sidebar-menu/core.ts`; `apps/admin/app/routes.ts` Z. 11–26 | bestätigt |
| `FILE_SIZE_LIMIT` Z. 389, `DATA_UPLOAD_MAX_MEMORY_SIZE` Z. 403, `SESSION_COOKIE_AGE` Z. 425, `ADMIN_SESSION_COOKIE_AGE` Z. 432, `file_size_limit` Z. 142, Session-Middleware Z. 64, `login.py` Z. 19 | `grep -n` | bestätigt |
| Fehlercode-Lücken 5106–5109, 5113–5114, 5116–5119; 5015, 5019, 5021, 5065, 5122 | Skript über `apps/api/plane/authentication/adapter/error.py` | bestätigt |
| `RESTRICTED_URLS` = `RESTRICTED_WORKSPACE_SLUGS`, je 65 Einträge, Dubletten `monitor`, `config`, `mobile` | Python-Vergleich der Listen | bestätigt |
| i18n-Zeilenangaben (`auth.json` Z. 2/278/361, `workspace-settings.json` Z. 21/68/192/253/282, `workspace.json` Z. 331, `project.json` Z. 370, `home.json` Z. 68, `empty-state.json` Z. 252) und „EE-Texte im CE unreferenziert“ | `grep -n`; `grep` der Schlüssel außerhalb `locales/` (0 Treffer für `group_syncing`, `settings.identity`, `sso.`, `auth.ldap`, `members_import`, `business_trial_banner`, `cancel_trial`, `add_seats`, `upgrade_request`, `sidebar.upgrade`, `sidebar.plane_pro`, `higher_subscription`, `guest_super_permissions`) | bestätigt; 17 von 251 referenzierte Schlüssel nachgezählt |
| Gast-Logik im CE (`project-settings-member-defaults.tsx` Z. 127, 199–208; Suche Z. 96–100, 177–182, 229–234, 266; Export Z. 149–153; Page-Permission Z. 62–63; Favoriten-Serializer; Herabstufung `member.py` Z. 116–130) | Lesen | bestätigt |
| Passwortregeln (`password.py` Z. 10–15, `packages/utils/src/auth.ts`, `SPACE_PASSWORD_CRITERIA`), `EAuthSteps` Z. 64–68, Aktionstext `auth-root.tsx` Z. 55, Mitgliederspalte „Authentication“ `useMemberColumns.tsx` Z. 112–118 | Lesen | bestätigt |
| Screenshot B2 `saml-oauth.png` (Felder, Platzhalter, Hilfetexte, WEB/MOBILE-URLs, MAPPING, Buttons) und B10 `user-management.webp` (Spalten, Untertitel mit „seats“, Sidebar-Reihenfolge General, Email, Authentication, Workspaces, Billing, User Management, Artificial intelligence (deprecated), Images in Plane) | Bild gesichtet | bestätigt |
| Docs-Badges (SAML/OIDC Pro+Business, LDAP/Airgapped/FIPS Enterprise Grid) | `grep -rn '<Badge'` über Developer-Docs (33 Treffer) | bestätigt |
| Session-Expiry-Tabelle, User-Management-Tabelle/Modal/Status, LDAP-Defaults und Ablauf, FIPS-Defaults (`fips-deployment.md` Z. 46, 72, 163, 196–199), Lizenzfehlertexte, Monitor 5 min/300 min, `plane-architecture.md` Z. 46–47, `airgapped-requirements.md` Z. 10, `editions-and-versions.md` Z. 35/37, `self-hosting-101.md` Z. 42/54/60/80 | Lesen | bestätigt |
| Helm-README: OIDC-Client-Secret, SAML-Zertifikat, `LDAP_BIND_PASSWORD` DB-resident bei `SKIP_ENV_VAR=1`; Argus-Werte | `README.md` Abschnitt „Secrets that live in the database“; `values.yaml` Z. 700–722 | bestätigt |
| CE-Nutzung der Propel-Icons (`AccessAndRolesOutline`, `KeyOutline`, `BillingsOutline`, `DeactivatedUserOutline`, `ActivityOutline`) | `grep` | bestätigt |

Keine Funktionsbeschreibung wurde als erfunden erkannt. Übertreibungen bzw. unbelegte Präzisierungen wurden korrigiert (K15, K16).

### V.2 WebSearch-Abfragen (13 Tool-Aufrufe; S4 lief intern als Doppelabfrage, damit 14 von höchstens 15 verbraucht)

| # | Abfrage | Befund | Wirkung |
|---|---|---|---|
| S1 | docs.plane.so audit logs workspace settings plan Enterprise Grid | Seite „Workspace Audit Logs Enterprise Grid“ mit Ort, Rollen, Unveränderlichkeit, Ereignisarten | W15; P08-18 Tier → Enterprise Grid, UI ergänzt |
| S2 | Plane docs.plane.so two-factor authentication passkeys workspace | nur `docs.plane.com`-Changelog (anderes Unternehmen) | W23; P08-07/08 Warnung |
| S3 | plane.so "two-factor" OR "2FA" OR "passkeys" … | nur `help.plane.com` (anderes Unternehmen) | W23 |
| S4 | docs.plane.so single sign-on SSO workspace domain verification plan (intern 2 Abfragen) | docs.plane.so/authentication/sso: Domain nur in einem Workspace verifizierbar, Pending, `dig TXT` | W16; P08-03 ergänzt |
| S5 | docs.plane.so custom roles permission schemes workspace settings roles Plane | Custom Roles aus Permission Schemes, Ort „Roles and permissions schemes“, System-Schemes, GAC Enterprise | W19; P08-12/13 |
| S6 | "docs.plane.so/roles-and-permissions" member roles … | Owner/Member/Guest alle Pläne, Admin/Contributor/Commenter ab Business, Umbenennungen, Owner-Exklusivrechte, Custom Roles Enterprise Grid | W18; P08-11/12/14 |
| S7 | plane.so changelog 2026-04-25 custom roles granular access permissions redesign | RBAC Standard, GAC Enterprise-Add-on, neue Rolle Workspace Admin (Business+), bedingte Rechte; Forum v3.0.0 „workspace governance, RBAC“ | W20, W21 |
| S8 | docs.plane.so workspace security settings password policy allowed email domains restrict sign-ups | keine Plane-Treffer | O12 bleibt offen |
| S9 | plane.so Enterprise Grid SCIM provisioning LDAP IdP group sync audit logs | GAC-/LDAP-Blog (10.06.2026): LDAP-Server-Typen, Group-Sync-Regeln; kein SCIM | W22; P08-04/05 |
| S10 | "docs.plane.so/workspaces-and-users/audit-logs" export filters events tracked retention | keine Plane-Treffer | O9 bleibt offen |
| S11 | plane.so pricing Pro Business Enterprise Grid SSO SAML OIDC "domain" … | plane.so/business „SSO on Cloud“ | W17; P08-03 Tier → Business |
| S12 | plane.so changelog "two-factor" OR "passkey" OR "password policy" OR "session management" makeplane | nur `docs.plane.com`/`help.plane.com` (anderes Unternehmen) | W23 bestätigt |
| S13 | docs.plane.so workspace activity log filter members projects Business plan Plane | keine Plane-Treffer | O20 |

### V.3 Korrekturen (vorher → nachher)

| # | Stelle | vorher | nachher | Beleg |
|---|---|---|---|---|
| K01 | P08-01 SAML Tier | One | **Pro** (Matrix One als Widerspruch) | `saml-sso.md` Z. 7; `plans.tsx` Z. 1274; Dok. 22 P03-F04 (verifiziert) |
| K02 | P08-02 OIDC Tier | One | **Pro** | `oidc-sso.md` Z. 7; Dok. 22 P03-F05 |
| K03 | P08-03 Workspace-Identity Tier | unklar | **Business** (Cloud, mittel) | W17 |
| K04 | P08-05 Group Sync CE-Status | Stub/UI-Hülle | **fehlt** | `grep group_sync` nur `locales/`; Dok. 20 PF-98; Dok. 21 F12 (K09) |
| K05 | P08-05 Icon-Vorschlag | `UserCogOutline` | `GroupSyncOutline` (eigenes Propel-Icon) | `dist/icons/index.d.ts` Z. 545–546 |
| K06 | P08-11 Tier und Titel | Pro, „Pre-defined Roles“ | **Business**, „System-Rollen / RBAC“ | W18, W20 |
| K07 | P08-11 CE-Mapping | Workspace 20→`admin`, Projekt 15→`member` | Workspace 20→`owner`; Projekt 15→`contributor` (v1-Alias `member`); neue Rollen Workspace `admin`, Projekt `commenter` | W20 (Umbenennungen); D23 `members/overview.md` |
| K08 | P08-12 Tier und Inhalt | Business, „RBAC: benutzerdefinierte Rollen“ (nur Vorschlag) | **Enterprise Grid**, „Custom Roles“ mit belegtem Ort, Zusammensetzung aus Schemes, Ausschlussregeln | W19, W20 |
| K09 | P08-13 Tier und Inhalt | Enterprise, nur Nennungen | **Enterprise Grid**; Permission Schemes, bedingte Rechte, v2-API `permission-schemes`, `permissions/me` | W19, W20, W22; D23 |
| K10 | P08-14 Tier | One | **Pro** (Kontingent); Gast-Rolle laut Doku auf allen Plänen | B9; W18 |
| K11 | P08-18 Tier | Business | **Enterprise Grid** | W15 (Seitentitel) |
| K12 | P08-18 Inhalt | Ereignisse, Felder, API nur als Vorschlag (v1-Pfad `GET /api/v1/…/audit-logs/`) | belegtes v2-Objekt (23 Felder), Kategorien/Outcome/Source/Actor-Enums, Filter, Pagination, Fehler, Scope; UI-Verhalten aus W15 | D23 `audit-logs/*.md`; W15 |
| K13 | P08-22 CE-Status | teilweise | **Stub/UI-Hülle** | Legende; Dok. 22 Verifikation (`MACHINE_SIGNATURE` anders berechnet) |
| K14 | P08-22 Tier (JSON) | Cloud-only | **unklar** (Commercial-Edition-Mechanik, auch Self-hosted) | `plane-architecture.md` Z. 46–47 |
| K15 | P08-02 „Default `groups`“ | Default `groups` | Beispielwert `groups`, UI-Platzhalter „Groups“, kein belegter Default | D17; R4 |
| K16 | P08-07 Konfidenz Tier | hoch | mittel (nur Matrix) | keine Doku-Seite auffindbar |
| K17 | P08-24 CE-Status | „im CE ohne Limit“ (kein Legendenwert); JSON „fehlt“ | **im CE vorhanden (nur Cloud-Gating)** | Legende; Dok. 20 PF-55 |
| K18 | P08-24 Tier (JSON) | Cloud-only | **Pro** (Aufhebung der Grenze; Seats gelten auch Self-hosted) | `plans.tsx` Z. 676–693; `editions-and-versions.md` Z. 35 |
| K19 | P08-26 CE-Status | teilweise | **Stub/UI-Hülle** (nur ungenutztes Feld) | `grep is_support_required` |
| K20 | Legende CE-Status | „vollständige UI-Texte“ = Stub | Texte/Icons/Illustrationen = fehlt; ungenutzte Felder/Typen = Stub; teilweise nur bei erreichbarer Teilfunktion | Dok. 20 Abschnitt 3 (Abgrenzungsregel) |
| K21 | R32 / Anhang B-26 | alle Icons mit Filled-Variante; ohne GroupSync/PiiScanner | `UserCogOutline` ohne Filled, `UpgradeAltFilled` ohne Outline; `GroupSync*`, `PiiScanner*` ergänzt | `dist/icons/miscellaneous/` |
| K22 | §1.3 Web-Quellen | „Eigene WebSearch-Abfragen waren in diesem Lauf nicht möglich“ | auf den Autorenlauf präzisiert; W15–W23 ergänzt | V.2 |
| K23 | Kernaussagen 4, 5 | Audit Logs nur Matrix; Rollenmodell nur Namespaces workspace/project | Audit Logs belegt; RBAC/GAC-Schichten, Namespace `instance`, Felder `level`/`status` | D23; W18–W20 |
| K24 | Offene Punkte O4, O8, O9, O12, O16 | offen | präzisiert bzw. O16 erledigt | V.2 |

### V.4 Ergänzungen

| # | Ergänzung | Ort |
|---|---|---|
| E01 | Quelle D23 (Developer-Docs-Branch `docs/api-reference-v2`, Commit `b89c72c`) | §1.3 |
| E02 | Web-Quellen W15–W23 inkl. Ausschluss von `plane.com` (anderes Unternehmen) | §1.3 |
| E03 | Aktuelle Plan-Liste und Tier-Regel (One → aktueller Plan) | §1.2 |
| E04 | Domain nur in einem Workspace verifizierbar; Datenmodell mit partiellem Unique-Index | P08-03 |
| E05 | LDAP-Server-Typen (AD, OpenLDAP, FreeIPA) | P08-04 |
| E06 | Group-Sync-Regeln (höchste Rolle, keine Herabstufung manueller Rollen, Workspace-Mitgliedschaft bleibt, alleinige Projekt-Admins/manuelle Mitglieder bleiben), v2-Feld `default_workspace_role_slug`, v2-Pfade, Herkunftsmarkierung | P08-05 |
| E07 | Vollständige Liste der CE-Durchsetzungspunkte der Passwortprüfung | P08-09 |
| E08 | Rollen-Doku 2026 (Owner/Admin/Member/Guest, Contributor/Commenter, Umbenennungen, Owner-Exklusivrechte), v2-Rollen-API, Querverweis Workspace-Access-Tokens (Dok. 28 P09-F52) | P08-11 |
| E09 | Custom Roles (Ort, Zusammensetzung, Ausschlüsse) | P08-12 |
| E10 | Permission Schemes, bedingte Rechte, effektive Berechtigungen, Namespace `instance` | P08-13 |
| E11 | Abgrenzung Activity Logs ↔ Audit Logs | P08-17, O20 |
| E12 | Audit-Log-UI, -Objekt, -Filter, -API, -Fehler | P08-18 |
| E13 | Argus-Scanumfang (Dok. 22), Propel-Icons | P08-29 |
| E14 | Querverweis God-Mode „System checks“ (Dok. 22) | §1.5 Punkt 8 |
| E15 | Querverweis Mitglieder-CSV-Import = Dok. 28 P09-F32 | P08-31 |
| E16 | Offene Punkte O18–O21 | Kap. 5 |
| E17 | Finale Feature-Liste mit 33 Einträgen (30 Autoren-Einträge korrigiert; P08-23 in vier Einträge P08-23a–d aufgeteilt) | `migration/features/_data/P08.paid.json` |

### V.5 Dokumentierte Widersprüche zwischen Quellen bzw. Schwester-Dokumenten

| Thema | Quelle A | Quelle B | Entscheidung |
|---|---|---|---|
| SAML/OIDC Tier | `plans.tsx` Z. 1060/1071 One; Dok. 20 PF-93 One | Docs-Badges Pro/Business; Dok. 22 P03-F04/F05 Pro | Pro (aktueller, self-hosting-spezifisch) |
| SAML/OIDC CE-Status | Dok. 22 P03-F04/F05 „fehlt“ | Dok. 20 PF-93 (K25), Dok. 27 „Stub“ | Stub (generische Extension-Points sind nach Legende Stub); Dok. 22 O33 |
| Group Sync CE-Status | Dok. 22 P03-F08 „Stub“ | Dok. 20 PF-98, Dok. 21 F12 „fehlt“ | fehlt (nur Texte/Illustration/Icon) |
| Rollen Tier | `plans.tsx` Pro „Pre-defined roles“; Dok. 20 PF-54 Pro | Doku 2026 Business (W18, W20); Dok. 21 F26 Business | Business |
| Custom Roles Tier | `plans.tsx` Business „RBAC … custom ones“; Dok. 21 F26 Business | Doku/Changelog Enterprise Grid (W19, W20) | Enterprise Grid |
| Audit Logs Tier | `plans.tsx` Business (CS); Dok. 21 F34, Dok. 22 P03-F44 Business | Doku-Seitentitel Enterprise Grid (W15); Dok. 20 PF-59 WebSearch „Enterprise Grid API audit logs“ | Enterprise Grid |
| Password Policy CE-Status | Dok. 20 PF-96 „fehlt“ | Dok. 22 P03-F10, Dok. 27 „teilweise“ | teilweise (erreichbare feste Regeln) |
| Group Sync Auto remove | v1-Doku: „remove users from projects/workspace“ (D17) | Blog: Workspace-Mitgliedschaft bleibt immer erhalten (W22) | Blog (spezifischer); UNVERIFIZIERT |
| Contributor-Verfügbarkeit | Doku-Zusammenfassung „Contributor ab Business“ | Changelog „Project Member → Contributor“ (Free-Rolle) | offen (O8) |
| Gäste im Free-Plan | `plans.tsx` Free „–“ | Doku: Guest auf allen Plänen; CE ohne Einschränkung | Doku/CE |
| Projekt-Rollen-Slug | v1-Group-Sync-Beispiel `member` | v2 `contributor` | `contributor` mit Alias `member` |
| `docs.plane.com` | Dok. 21 V.2 S1 wertet `docs.plane.com` als „Hinweis auf neue Domain plane.com“ | Treffer beschreiben Bankkonto-Änderungen und „administrators and managers“ (anderes Unternehmen); Dok. 22 Verifikation verwirft `docs.plane.com` ebenfalls | `plane.com` gehört **nicht** zu makeplane/Plane; Hinweis an Dok. 21 |
| Airgapped-Pläne | `airgapped-requirements.md` „exclusively for Enterprise Grid“ | `activate-airgapped.md` Pro/Business | irrelevant (O14) |
| SAML Entity ID | `saml-sso.md` `…/auth/saml/` | Screenshot `…/auth/saml/metadata/` | O13 |

### V.6 Restunsicherheiten

- Alle Web-Befunde W15–W22 sind Suchmaschinen-Zusammenfassungen; die Seiten selbst waren nicht abrufbar (Konfidenz höchstens „mittel“).
- Der v2-Doku-Branch (D23) ist ein unveröffentlichter Stand (11.08.2026); ob er dem ausgelieferten Produkt entspricht, ist nicht belegt (Dok. 21 O18). Die Beispielwerte der Rollen-/Scheme-Objekte sind Platzhalter („Example name“, Slug „my-team“).
- Für 2FA, Passkeys, Password Policy, Domain Security, Admin Interface und Workspace Activity Logs existiert weiterhin kein öffentlicher Spec; die Abschnitte bleiben Entwürfe (UNVERIFIZIERT).
- SCIM: kein Beleg über die Nennungen hinaus.
- Vollständiger `event_name`-Katalog des Audit-Logs, Exportformat, Aufbewahrung: nicht belegt.
- Schwester-Dokumente 20, 21, 22 führen Audit Logs, Custom Roles bzw. Rollen noch mit abweichendem Tier (O18) – bei deren nächster Überarbeitung angleichen.
