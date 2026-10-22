# A10a – Frontend `apps/web`: Workspace-Shell, Navigation, Home, Einstellungen, Profil, Auth, Onboarding, Power-K, Inbox (IST-Analyse)

> Bereich (A10a): `apps/web/components/{workspace, project, projects, settings, profile, account, onboarding, navigation, sidebar, core, common, home, stickies, workspace-notifications, power-k, license, empty-state, ui, icons, appearance, user, instance, auth-screens, global, modals, breadcrumbs, browse, archives}/` – 28 Verzeichnisse, 574 Dateien, 49.815 Zeilen – sowie die zugehörigen Routen-Dateien unter `apps/web/app/(all)/**`, soweit sie Screens dieses Bereichs zusammensetzen.
> Quelle: Plane v1.4.2 Community Edition, Repo-Root `/home/user/plane`. Alle Pfade relativ zum Repo-Root; in Tabellen mit Abschnitts-Präfix ist `apps/web/components/` gemeint. UI-Texte sind aus `packages/i18n/src/locales/en/*.json` aufgelöst (englisch, wörtlich).
> Bindend: `migration/architecture/00-grundsatzentscheidungen.md` (ADR-001 keine Planstufen/kein Upsell, ADR-002 Realtime, ADR-003 Greenfield, ADR-004 Self-hosted/Airgap, ADR-005 UI 1:1, ADR-006 Original als Referenz).
> Abgrenzung: Routen, Guards, Stores, Services und Browser-Storage-Architektur → A08 (`08-frontend-web-architektur.md`); Work-Item-Layouts, Peek, Filter, Dropdowns → A09; Cycles, Modules, Views, Pages, Intake, Analytics, Estimates, Labels/States, Webhooks, Exporter, API-Tokens → A10b; Admin-/Space-App → A11; Editor/Realtime → A12; Designsystem/Tokens → A13a; i18n/Shared-Packages → A13b; Bezahl-Spuren → `migration/features/20-paid-spuren-im-repo.md`.

## Inhaltsverzeichnis

1. Überblick & Verantwortlichkeiten (1.1 Verzeichnisse · 1.2 Shell-Struktur · 1.3 Bausteine · 1.4 CE-Stubs und Bezahlspuren · 1.5 Screen-Übersicht)
2. Vollständige Inventare (2.1 Dateien · 2.2 Shell/Top-Navigation · 2.3 Sidebar · 2.4 Header/Breadcrumbs/Projekt-Navigation · 2.5 Home · 2.6 Stickies · 2.7 Inbox · 2.8 „Your work“ · 2.9 Power-K · 2.10 Settings-Rahmen/Workspace-Settings · 2.11 Projekt-Settings · 2.12 Projektliste/Anlage · 2.13 Profil-Settings · 2.14 Auth · 2.15 Onboarding/Tour · 2.16 Querschnitt · 2.17 Workspace-Views/Archive/Browse · 2.18 Lizenz/Billing · 2.19 LocalStorage · 2.20 Endpunkte · 2.21 Toter Code)
3. Verhalten/Logik/Abläufe (3.1 Shell · 3.2–3.4 Sidebar · 3.5 Projekte · 3.6 Home · 3.7 Inbox · 3.8 Settings/Auth/Onboarding · 3.9 Power-K · 3.10 Edge-Cases)
4. Abhängigkeiten
5. Migrationshinweise für Angular
6. Offene Punkte

---

## 1. Überblick & Verantwortlichkeiten

### 1.1 Verzeichnisse im Bereich

| Verzeichnis (`apps/web/components/…`) | Dateien | Zeilen | Verantwortung | Abschnitt |
|---|---|---|---|---|
| `workspace/` | 69 | 8570 | Workspace-Switcher, User- und Hilfe-Menü, Sidebar (Menü-Items, Favoriten, Projektliste, Extended-Sidebar), Workspace-Details/-Löschung, Mitglieder- und Einladungstabellen, Einladungsdialog, Workspace anlegen, Workspace-Views, Billing/Plan-Vergleich, `UpgradeBadge`, `WorkspaceEditionBadge`, `WorkspaceLogo` | 2.2, 2.3, 2.10, 2.15.3, 2.17, 2.18 |
| `project/` | 46 | 5837 | Projektliste (Karten, Suche, Sortierung, Filter, angewandte Filter), Projekt anlegen/bearbeiten, Archivieren/Wiederherstellen/Löschen/Verlassen/Beitreten, Mitglieder und Mitglieder-Defaults, Publish-Dialog, Feature-Liste, Control-Section | 2.11, 2.12, 3.5 |
| `projects/` | 7 | 683 | Anlage-Root und -Attribute, Mobile-Header der Projektliste, Intake-Header, Spalten der Projektmitglieder-Tabelle | 2.11.3, 2.12 |
| `settings/` | 42 | 2488 | Settings-Rahmen (Content-Wrapper, Headings, Control-Items, Sidebar-Items, Mobile-Navigation), Workspace- und Projekt-Settings-Sidebars, Profil-Einstellungen (Modal und Seite, alle Tabs) | 2.10, 2.11, 2.13 |
| `profile/` | 14 | 1297 | „Your work“-Profilseiten (Summary, Issue-Tabs, Activity, Profil-Sidebar), Wochenstart-Auswahl | 2.8 |
| `account/` | 15 | 1814 | Auth-Formulare (E-Mail, Passwort, Magic-Code, Forgot/Reset/Set-Password), AGB-Hinweis, Konto-Deaktivierung | 2.13.2, 2.14 |
| `onboarding/` | 31 | 3869 | Onboarding-Schritte, Kopf mit Fortschritt und Account-Switch, Produkt-Tour, Altkomponenten | 2.15 |
| `navigation/` | 20 | 2306 | Top-Navigation, Power-K-Suchfeld, App-Rail (inaktiv), Tab-Navigation (TABBED), Projekt-Switcher/-Aktionen, „Customize navigation“ | 2.2, 2.3.4, 2.4.2 |
| `sidebar/` | 7 | 647 | `ResizableSidebar`, `SidebarWrapper`, Sidebar-Primitives, Toggle | 2.3, 3.2 |
| `core/` | 43 | 5164 | `AppHeader`, `ContentWrapper`, `PageHead`, Aktivitätstexte, Beschreibungs-Versionen, Datumsfilter, Image-Picker, Upload-/Change-Email-/Bulk-Delete-/Existing-Items-Dialoge, KI-Assistent, Theme-Editor, Mehrfachauswahl, Fortschritts-Statistiken | 2.4.3, 2.13, 2.16 |
| `common/` | 26 | 1712 | Breadcrumb-Link, Switcher-Label, Extended-Header, Count-Chip, Cover-Image, Logo-Spinner, Data-Table, Error-Boundary, Quick-Action-Fabrik, Filter-Bausteine, globale Modals | 2.4.3, 2.16 |
| `home/` | 33 | 2134 | Workspace-Home (Begrüßung, Widgets, Manage-Dialog, Quickstart, Quick links, Recents) | 2.5, 3.6 |
| `stickies/` | 17 | 1481 | Stickies-Seite, -Widget, Sticky-Karte mit Editor, Suche, DnD | 2.6, 3.6 |
| `workspace-notifications/` | 28 | 1878 | Inbox (Liste, Filter, Optionen, Snooze, Detail) | 2.7, 3.7 |
| `power-k/` | 79 | 5890 | Command Palette (Registry, Shortcuts, Kontext, alle Befehle, Modal, Shortcut-Übersicht) | 2.9, 3.9 |
| `license/` | 10 | 727 | Upgrade-Modal und Plan-Karten | 2.18 |
| `empty-state/` | 4 | 216 | Detailed/Simple/Section-Leerzustände | 2.16.2 |
| `ui/` | 25 | 1054 | Skeleton-Loader, `EmptySpace`, tote Markdown-/Profil-Leerzustände | 2.16.2, 2.16.3 |
| `icons/` | 26 | 501 | Dateityp-Icons, `SettingIcon`, `LockedComponent` | 2.16.6 |
| `appearance/` | 2 | 110 | Theme-Switcher | 2.13.3 |
| `user/` | 2 | 68 | Duplikat der Begrüßung (tot) | 2.21 |
| `instance/` | 4 | 152 | „Instance not ready“, Wartungsansicht | 2.16.8 |
| `auth-screens/` | 6 | 315 | Auth-Rahmen, „Not authorized“, Projektzugriff, „Not a member“ | 2.14 |
| `global/` | 9 | 437 | „What's new?“-Dialog, Zeitzonen-Auswahl, Versionsnummer | 2.16.9 |
| `modals/` | 3 | 210 | Modal-Hosts Workspace/Projekt/Work Item | 2.16.7 |
| `breadcrumbs/` | 3 | 150 | Projekt-Breadcrumb mit Switcher | 2.4.3 |
| `browse/` | 1 | 29 | Work-Item-Detail per Identifier | 2.17 |
| `archives/` | 2 | 76 | Archiv-Tabs | 2.17 |

### 1.2 Struktur der Workspace-Shell

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ TopNavigationRoot (bg-canvas, min-h-10, px-3.5, z-[27])                          2.2           │
│ [WorkspaceMenuRoot ▾]          [TopNavPowerK: Suchfeld 364px → 554px]   [Inbox•][?][★GitHub][👤]│
├──────────────────────┬───────────────────────────────────────────────────────────────────────┤
│ ProjectAppSidebar    │ <main class="bg-surface-1">                                            │
│ (ResizableSidebar    │   [Tab-Zeile bei navigationMode = TABBED]                      2.4.2   │
│  236–350px, Default  │   AppHeader (Breadcrumbs | Aktionen)                           2.4.3   │
│  250px)       2.3    │   ContentWrapper → Seite                                               │
│  „Projects“ ⚙ ⇤      │                                                                        │
│  [+ New work item]   │ ExtendedAppSidebar „More“ (absolute, 300px, left = Sidebar-Breite,     │
│  Home, Stickies,     │  z-[21]) bzw. ExtendedProjectSidebar                   2.3.3, 2.3.6   │
│  Your work, Drafts*  │                                                                        │
│  ▸ Workspace:        │                                                                        │
│    Projects, Views*, │                                                                        │
│    Analytics*,       │                                                                        │
│    Archives*, More   │                                                                        │
│  ▸ Favorites         │                                                                        │
│  ▸ Projects (+)      │                                                                        │
│  Fuß h-12: „Community“-Badge (entfällt, ADR-001)                                               │
└──────────────────────┴───────────────────────────────────────────────────────────────────────┘
 * = nur wenn in den Sidebar-Präferenzen gepinnt bzw. aktiviert (2.3.2)
```

Quellen: `apps/web/app/(all)/[workspaceSlug]/layout.tsx`, `apps/web/components/workspace/content-wrapper.tsx`, `apps/web/components/navigation/top-navigation-root.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/layout.tsx`, `.../(projects)/_sidebar.tsx`, `.../(projects)/sidebar.tsx`, `apps/web/components/sidebar/sidebar-wrapper.tsx`, `apps/web/components/workspace/sidebar/sidebar-menu-items.tsx`. Einstellungsseiten (`/:ws/settings/**`) verwenden einen eigenen Rahmen ohne App-Sidebar (2.10), Profil-Einstellungen (`/settings/profile/:tab`), Onboarding und Auth-Seiten liegen außerhalb der Workspace-Shell.

### 1.3 Bausteine

| Baustein | Herkunft | Verwendung |
|---|---|---|
| `Button`, `IconButton`, `Icon`, `Menu*`, `ContextMenu*`, `Dialog*` (`DialogContent size sm/md/lg/xl/full`), `Tabs/TabsList/Tab/TabsPanel`, `Tooltip`, `Collapsible`, `ScrollArea`, `Input/InputGroup`, `Field`, `Checkbox`, `Switch`, `Select`, `Combobox*`, `Popover*`, `Avatar`, `Table*`, Icons (`*Outline`) | npm `@makeplane/propel` 0.7.3 (`@makeplane/propel/components/*`, `/elements/*`, `/icons`) | alle Screens |
| `Breadcrumbs`, `Header` (`EHeaderVariant`), `Row`, `ContentWrapper`, `ControlLink`, `EmptyStateCompact`/`EmptyStateDetailed`, `Loader`, `ConfirmDialog`, `Logo`, `DragHandle`, `DropIndicator`, `Sortable`, `setToast`/`setPromiseToast`, `OAuthOptions`, `PasswordStrengthIndicator`, `BreadcrumbNavigationSelect` | `@plane/blocks` (`packages/blocks`, Subpfad-Importe) | alle Screens |
| Charts (`BarChart`, `PieChart`, `AreaChart`) | `@plane/blocks/charts/{bar-chart,pie-chart,area-chart}` | Profil-Summary (2.8.3), Fortschritt (2.16.4) |
| Command-Menü | `cmdk` | Power-K (2.9) |
| Drag&Drop | `@atlaskit/pragmatic-drag-and-drop` (+ `hitbox`, `auto-scroll`) | Sidebar-Projekte, Favoriten, Extended-Sidebar, Home-Widgets, Stickies (3.3, 3.4, 3.6) |
| Masonry | `react-masonry-component` | Stickies (2.6) |
| Formulare | `react-hook-form` | alle Formulare |
| Tokens/Klassen | Tailwind v4 (`@plane/tailwind-config`), Tokens wie `bg-canvas`, `bg-surface-1/2`, `bg-layer-1/2/3`, `text-primary/secondary/tertiary/placeholder`, `border-subtle` (A13a) | alle Komponenten |

### 1.4 CE-Stubs und Bezahlspuren in diesem Bereich

| Spur | Fundstelle | Behandlung |
|---|---|---|
| „Community“-Badge, Upgrade-Modal, Plan-Karten, Billing-Seite, „Pro“-Badges, „Contact sales“ | 2.18, 2.2 | entfällt (ADR-001) |
| Features-Kategorie der Workspace-Settings (leer), `ADDITIONAL_NOTIFICATION_CONTENT_MAP` (leer), `useIntakeHeaderMenuItems` (leer), App-Rail (`isEnabled = false`), „Enter god mode“ im User-Menü (`isUserInstanceAdmin` fest `false`) | 2.10.1, 2.7.3, 2.16.1, 2.2 | Erweiterungspunkte im Neubau neutral vorsehen, ohne Plan-Logik |
| Routen-Ziele, die nur in der Bezahl-Edition existieren (`/wiki/{id}`, `/{ws}/pages/{id}`, Projekt-Tabs `overview`/`epics`) | 2.4.1, 3.10 E25 | nicht verlinken, bis die Funktion gebaut ist |
| Übersetzte, ungenutzte EE-Texte `project_settings.features.time_tracking.*`, `project_settings.features.milestones.*`, `project_settings.features.intake.{intake_responsibility, intake_sources, notify_assignee, in_app, email, form, toasts.set}`, `home.business_trial_banner.*` | 2.11.1, `packages/i18n/src/locales/en/*.json` | nicht übernehmen |

### 1.5 Screen-Übersicht

| Screen / Dialog | Route bzw. Auslöser | Abschnitt |
|---|---|---|
| Workspace-Shell (Top-Navigation, Sidebar, Extended-Sidebars) | alle `/:ws/**` außer Settings | 2.2, 2.3 |
| Workspace-Home | `/:ws` | 2.5 |
| Stickies | `/:ws/stickies` | 2.6 |
| Inbox | `/:ws/notifications` | 2.7 |
| „Your work“ (Summary, Assigned, Created, Subscribed, Activity) | `/:ws/profile/:userId[/…]` | 2.8 |
| Power-K (Modal und Top-Nav-Variante), Shortcut-Übersicht | `Ctrl/⌘ K`, Top-Nav-Suchfeld, Hilfe-Menü | 2.9 |
| Workspace-Settings (General, Members, Billing, Exports, Webhooks) | `/:ws/settings/**` | 2.10 |
| Projekt-Settings (General, Members, 5 Features, States, Labels, Estimates, Automations) | `/:ws/settings/projects/:pid/**` | 2.11 |
| Projektliste, Projektarchiv, Projekt anlegen | `/:ws/projects`, `/:ws/projects/archives`, „Add Project“ | 2.12 |
| Profil-Einstellungen (Profile, Preferences, Notifications, Security, Personal Access Tokens) | `/settings/profile/:tab` bzw. Modal | 2.13 |
| Sign-in, Sign-up, Magic-Code, Forgot/Reset/Set-Password, Zugriffs-Screens | `/`, `/sign-up`, `/accounts/*` | 2.14 |
| Onboarding, Workspace anlegen, Produkt-Tour | `/onboarding`, `/create-workspace`, Home | 2.15 |
| Querschnittsdialoge (Versionen, Datumsfilter, Bulk-Delete, Existing Items, KI, Image-Picker, Uploads, What's new) | aus Fachscreens | 2.16 |
| Workspace-Views (Bausteine), Archiv-Tabs, Browse | `/:ws/workspace-views/**`, `/:ws/projects/:pid/archives/**`, `/:ws/browse/:id` | 2.17 |
| Instanz-Zustände | `InstanceWrapper` | 2.16.8 |

---

## 2. Vollständige Inventare

### 2.1 Datei-Inventar des Bereichs (`apps/web/components/…`)

Vollständige Liste aller 574 Dateien (49.815 Zeilen; Zeilenzahl per `wc -l`, Exporte per Quelltext-Scan). Spalte „Abschnitt“ verweist auf die Beschreibung in diesem Dokument; „Status“ = Erreichbarkeit im Importgraphen ab den Routen `apps/web/app/**` (2.21).

| Verzeichnis | Dateien | Zeilen | Abschnitte |
|---|---|---|---|
| `workspace/` | 69 | 8570 | 2.2, 2.3, 2.3.3, 2.3.5, 2.3.7, 2.4.1, 2.10.2, 2.10.3, 2.15.3, 2.17, 2.18, 2.21, 3.3, 3.4 |
| `sidebar/` | 7 | 647 | 2.3 |
| `navigation/` | 20 | 2306 | 2.2, 2.3.4, 2.4.2 |
| `breadcrumbs/` | 3 | 150 | 2.4.3 |
| `home/` | 33 | 2134 | 2.5, 2.5.1, 2.5.2, 2.5.3, 2.5.4, 2.5.5, 2.5.6, 2.5.7, 3.6 |
| `stickies/` | 17 | 1481 | 2.5.8, 2.6, 2.21 |
| `workspace-notifications/` | 28 | 1878 | 2.7, 2.7.1, 2.7.2, 2.7.3, 2.7.4, 2.21, 3.7 |
| `profile/` | 14 | 1297 | 2.8, 2.8.2, 2.8.3, 2.8.4, 2.8.5, 2.13.3, 2.21 |
| `power-k/` | 79 | 5890 | 2.9, 2.9.1, 2.9.2, 2.9.3, 3.9.1, 3.9.2 |
| `settings/` | 42 | 2488 | 2.10, 2.10.1, 2.11.1, 2.13 |
| `project/` | 46 | 5837 | 2.11, 2.11.2, 2.11.3, 2.11.4, 2.12, 2.12.1, 2.12.2, 2.12.3, 2.21 |
| `projects/` | 7 | 683 | 2.11.3, 2.12, 2.12.1, 2.12.3 |
| `account/` | 15 | 1814 | 2.13.2, 2.14.1, 2.14.2, 2.14.3, 2.21 |
| `auth-screens/` | 6 | 315 | 2.14.1, 2.14.4, 2.21 |
| `onboarding/` | 31 | 3869 | 2.15, 2.15.1, 2.15.2, 2.15.4, 2.21, 3.8.5 |
| `core/` | 43 | 5164 | 2.4.3, 2.13.2, 2.13.3, 2.16.1, 2.16.4, 2.16.5 |
| `common/` | 26 | 1712 | 2.4.3, 2.12.1, 2.13.1, 2.16.1, 2.16.2, 2.18, 2.21, 3.2 |
| `empty-state/` | 4 | 216 | 2.16.2 |
| `ui/` | 25 | 1054 | 2.16.2, 2.16.3 |
| `icons/` | 26 | 501 | 2.16.6 |
| `modals/` | 3 | 210 | 2.16.7 |
| `instance/` | 4 | 152 | 2.16.8 |
| `global/` | 9 | 437 | 2.16.9 |
| `appearance/` | 2 | 110 | 2.13.3 |
| `user/` | 2 | 68 | 2.5.2, 2.21 |
| `license/` | 10 | 727 | 2.18 |
| `archives/` | 2 | 76 | 2.17 |
| `browse/` | 1 | 29 | 2.17 |

#### `workspace/` (69 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `workspace/billing/comparison/base.tsx` | 144 | `shouldRenderPlanDetail`, `PlansComparisonBase` | 2.18 | erreichbar |
| `workspace/billing/comparison/feature-detail.tsx` | 32 | `PlanFeatureDetail` | 2.18 | erreichbar |
| `workspace/billing/comparison/frequency-toggle.tsx` | 60 | `PlanFrequencyToggle` | 2.18 | erreichbar |
| `workspace/billing/comparison/index.ts` | 8 | Barrel (Re-Exporte) | 2.18 | nicht erreichbar |
| `workspace/billing/comparison/plan-detail.tsx` | 113 | `PlanDetail` | 2.18 | erreichbar |
| `workspace/billing/comparison/plans.tsx` | 1311 | `TPlanFeatureData`, `TPlanePlans`, `TPlanDetail`, `ComingSoonBadge`, `PLANS_LIST`, `PLANS_COMPARISON_LIST`, `PLANE_PLANS` | 2.18 | erreichbar |
| `workspace/billing/comparison/root.tsx` | 54 | `PlansComparison` | 2.18 | erreichbar |
| `workspace/billing/index.ts` | 7 | Barrel (Re-Exporte) | 2.18 | erreichbar |
| `workspace/billing/root.tsx` | 71 | `BillingRoot` | 2.18 | erreichbar |
| `workspace/confirm-workspace-member-remove.tsx` | 76 | `Props`, `ConfirmWorkspaceMemberRemove` | 2.10.3 | erreichbar |
| `workspace/content-wrapper.tsx` | 42 | `WorkspaceContentWrapper` | 2.2 | erreichbar |
| `workspace/create-workspace-form.tsx` | 271 | `CreateWorkspaceForm` | 2.15.3 | erreichbar |
| `workspace/delete-workspace-form.tsx` | 186 | `DeleteWorkspaceForm` | 2.10.2 | erreichbar |
| `workspace/delete-workspace-modal.tsx` | 35 | `DeleteWorkspaceModal` | 2.10.2 | erreichbar |
| `workspace/delete-workspace-section.tsx` | 51 | `DeleteWorkspaceSection` | 2.10.2 | erreichbar |
| `workspace/edition-badge.tsx` | 46 | `WorkspaceEditionBadge` | 2.18 | erreichbar |
| `workspace/invite-modal/actions.tsx` | 83 | `InvitationModalActions` | 2.10.3 | erreichbar |
| `workspace/invite-modal/fields.tsx` | 139 | `InvitationFields` | 2.10.3 | erreichbar |
| `workspace/invite-modal/form.tsx` | 46 | `InvitationForm` | 2.10.3 | erreichbar |
| `workspace/logo.tsx` | 41 | `WorkspaceLogo` | 2.2 | erreichbar |
| `workspace/members/index.ts` | 7 | Barrel (Re-Exporte) | 2.10.3 | erreichbar |
| `workspace/members/invite-modal.tsx` | 78 | `TSendWorkspaceInvitationModalProps`, `SendWorkspaceInvitationModal` | 2.10.3 | erreichbar |
| `workspace/settings/invitations-list-item.tsx` | 218 | `WorkspaceInvitationsListItem` | 2.10.3 | erreichbar |
| `workspace/settings/member-columns.tsx` | 188 | `RowData`, `NameColumn`, `AccountTypeColumn` | 2.10.3 | erreichbar |
| `workspace/settings/members-list-item.tsx` | 117 | `WorkspaceMembersListItem` | 2.10.3 | erreichbar |
| `workspace/settings/members-list.tsx` | 101 | `WorkspaceMembersList` | 2.10.3 | erreichbar |
| `workspace/settings/useMemberColumns.tsx` | 137 | `useMemberColumns` | 2.10.3 | erreichbar |
| `workspace/settings/workspace-details.tsx` | 314 | `WorkspaceDetails` | 2.10.2 | erreichbar |
| `workspace/sidebar/dropdown-item.tsx` | 134 | `SidebarDropdownItem` (default) | 2.2 | erreichbar |
| `workspace/sidebar/extended-sidebar-item.tsx` | 225 | `ExtendedSidebarItem` | 2.3.3 | erreichbar |
| `workspace/sidebar/favorites/favorite-folder.tsx` | 296 | `FavoriteFolder` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/favorite-item-drag-handle.tsx` | 46 | `FavoriteItemDragHandle` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/favorite-item-icon.tsx` | 46 | `FavoriteItemIcon` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/favorite-item-quick-action.tsx` | 63 | `FavoriteItemQuickAction` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/favorite-item-title.tsx` | 38 | `FavoriteItemTitle` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/favorite-item-wrapper.tsx` | 34 | `FavoriteItemWrapper` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/helper.tsx` | 25 | `generateFavoriteItemLink` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/common/index.ts` | 12 | Barrel (Re-Exporte) | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/index.ts` | 8 | Barrel (Re-Exporte) | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorite-items/root.tsx` | 144 | `FavoriteRoot` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorites-menu.tsx` | 252 | `SidebarFavoritesMenu` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/favorites.helpers.ts` | 72 | `TargetData`, `getInstructionFromPayload`, `getCanDrop` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/favorites/new-fav-folder.tsx` | 163 | `NewFavoriteFolder` | 2.3.7 / 3.4 | erreichbar |
| `workspace/sidebar/help-section/index.ts` | 7 | Barrel (Re-Exporte) | 2.2 | nicht erreichbar |
| `workspace/sidebar/help-section/root.tsx` | 78 | `HelpMenuRoot` | 2.2 | erreichbar |
| `workspace/sidebar/helper.tsx` | 44 | `getSidebarNavigationItemIcon` | 2.3 | erreichbar |
| `workspace/sidebar/project-navigation.tsx` | 211 | `TNavigationItem`, `ProjectNavigation` | 2.4.1 | erreichbar |
| `workspace/sidebar/projects-list-item.tsx` | 458 | `SidebarProjectsListItem` | 2.3.5 / 3.3 | erreichbar |
| `workspace/sidebar/projects-list.tsx` | 255 | `SidebarProjectsList` | 2.3.5 / 3.3 | erreichbar |
| `workspace/sidebar/quick-actions.tsx` | 96 | `SidebarQuickActions` | 2.3 | erreichbar |
| `workspace/sidebar/sidebar-item.tsx` | 81 | `SidebarItemBase` | 2.3 | erreichbar |
| `workspace/sidebar/sidebar-menu-items.tsx` | 140 | `SidebarMenuItems` | 2.3 | erreichbar |
| `workspace/sidebar/user-menu-item.tsx` | 68 | `SidebarUserMenuItemProps`, `SidebarUserMenuItem` | 2.21 | nicht erreichbar |
| `workspace/sidebar/user-menu-root.tsx` | 147 | `UserMenuRoot` | 2.2 | erreichbar |
| `workspace/sidebar/user-menu.tsx` | 73 | `SidebarUserMenu` | 2.21 | nicht erreichbar |
| `workspace/sidebar/workspace-menu-header.tsx` | 76 | `SidebarWorkspaceMenuHeader` | 2.21 | nicht erreichbar |
| `workspace/sidebar/workspace-menu-item.tsx` | 75 | `SidebarWorkspaceMenuItemProps`, `SidebarWorkspaceMenuItem` | 2.21 | nicht erreichbar |
| `workspace/sidebar/workspace-menu-root.tsx` | 197 | `WorkspaceMenuRoot` | 2.2 | erreichbar |
| `workspace/sidebar/workspace-menu.tsx` | 79 | `SidebarWorkspaceMenu` | 2.21 | nicht erreichbar |
| `workspace/upgrade-badge.tsx` | 35 | `UpgradeBadge` | 2.18 | erreichbar |
| `workspace/views/default-view-list-item.tsx` | 37 | `GlobalDefaultViewListItem` | 2.17 | erreichbar |
| `workspace/views/default-view-quick-action.tsx` | 94 | `DefaultWorkspaceViewQuickActions` | 2.17 | erreichbar |
| `workspace/views/delete-view-modal.tsx` | 65 | `DeleteGlobalViewModal` | 2.17 | erreichbar |
| `workspace/views/form.tsx` | 218 | `WorkspaceViewForm` | 2.17 | erreichbar |
| `workspace/views/header.tsx` | 121 | `GlobalViewsHeader` | 2.17 | nicht erreichbar |
| `workspace/views/modal.tsx` | 128 | `CreateUpdateWorkspaceViewModal` | 2.17 | erreichbar |
| `workspace/views/quick-action.tsx` | 103 | `WorkspaceViewQuickActions` | 2.17 | erreichbar |
| `workspace/views/view-list-item.tsx` | 106 | `GlobalViewListItem` | 2.17 | erreichbar |
| `workspace/views/views-list.tsx` | 44 | `GlobalViewsList` | 2.17 | erreichbar |

#### `sidebar/` (7 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `sidebar/add-button.tsx` | 21 | `SidebarAddButton` | 2.3 | erreichbar |
| `sidebar/resizable-sidebar.tsx` | 269 | `ResizableSidebar` | 2.3 | erreichbar |
| `sidebar/search-button.tsx` | 32 | `SidebarSearchButton` | 2.3 | nicht erreichbar |
| `sidebar/sidebar-item.tsx` | 162 | `AppSidebarItemComponent`, `AppSidebarItem`, `AppSidebarItemData, AppSidebarItemProps` | 2.3 | erreichbar |
| `sidebar/sidebar-navigation.tsx` | 31 | `SidebarNavItem` | 2.3 | erreichbar |
| `sidebar/sidebar-toggle-button.tsx` | 37 | `AppSidebarToggleButton` | 2.3 | erreichbar |
| `sidebar/sidebar-wrapper.tsx` | 95 | `SidebarWrapper` | 2.3 | erreichbar |

#### `navigation/` (20 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `navigation/app-rail-hoc.tsx` | 38 | `withDockItems` | 2.2 | erreichbar |
| `navigation/app-rail-root.tsx` | 87 | `AppRailRoot` | 2.2 | erreichbar |
| `navigation/customize-navigation-dialog.tsx` | 385 | `CustomizeNavigationDialog` | 2.3.4 | erreichbar |
| `navigation/index.ts` | 11 | Barrel (Re-Exporte) | 2.2 | erreichbar |
| `navigation/items-root.tsx` | 31 | `AppSidebarItemsRoot` | 2.2 | erreichbar |
| `navigation/project-actions-menu.tsx` | 97 | `ProjectActionsMenu` | 2.4.2 | erreichbar |
| `navigation/project-header-button.tsx` | 31 | `ProjectHeaderButton` | 2.4.2 | erreichbar |
| `navigation/project-header.tsx` | 125 | `ProjectHeader` | 2.4.2 | erreichbar |
| `navigation/tab-navigation-overflow-menu.tsx` | 103 | `TabNavigationOverflowMenu` | 2.4.2 | erreichbar |
| `navigation/tab-navigation-root.tsx` | 261 | `TNavigationItem`, `TabNavigationRoot` | 2.4.2 | erreichbar |
| `navigation/tab-navigation-utils.ts` | 117 | `TTabPreferences`, `TAB_PREFS_KEY`, `DEFAULT_TAB_KEY`, `getTabPreferences`, `saveTabPreferences`, `getTabUrl`, `getDefaultTabUrl`, `getValidatedDefaultTab` | 2.4.2 | erreichbar |
| `navigation/tab-navigation-visible-item.tsx` | 74 | `TTabNavigationVisibleItemProps`, `TabNavigationVisibleItem` | 2.4.2 | erreichbar |
| `navigation/top-nav-power-k.tsx` | 294 | `TopNavPowerK` | 2.2 | erreichbar |
| `navigation/top-navigation-root.tsx` | 88 | `TopNavigationRoot` | 2.2 | erreichbar |
| `navigation/underline-tab-link.tsx` | 25 | `UnderlineTabLink` | 2.4.2 | erreichbar |
| `navigation/use-active-tab.ts` | 42 | `useActiveTab` | 2.4.2 | erreichbar |
| `navigation/use-navigation-items.ts` | 124 | `useNavigationItems` | 2.4.2 | erreichbar |
| `navigation/use-project-actions.ts` | 61 | `useProjectActions` | 2.4.2 | erreichbar |
| `navigation/use-responsive-tab-layout.ts` | 169 | `TResponsiveTabLayout`, `useResponsiveTabLayout` | 2.4.2 | erreichbar |
| `navigation/use-tab-preferences.ts` | 143 | `TTabPreferencesHook`, `useTabPreferences` | 2.4.2 | erreichbar |

#### `breadcrumbs/` (3 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `breadcrumbs/common.tsx` | 25 | `CommonProjectBreadcrumbs` | 2.4.3 | erreichbar |
| `breadcrumbs/project.tsx` | 84 | `ProjectBreadcrumb` | 2.4.3 | erreichbar |
| `breadcrumbs/use-project-crumb-props.ts` | 41 | `useProjectCrumbProps` | 2.4.3 | erreichbar |

#### `home/` (33 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `home/home-dashboard-widgets.tsx` | 115 | `HOME_WIDGETS_LIST`, `DashboardWidgets` | 2.5.3 | erreichbar |
| `home/index.ts` | 9 | Barrel (Re-Exporte) | 2.5 | erreichbar |
| `home/root.tsx` | 66 | `WorkspaceHomeView` | 2.5.1 | erreichbar |
| `home/user-greetings.tsx` | 61 | `IUserGreetingsView`, `UserGreetingsView` | 2.5.2 | erreichbar |
| `home/widgets/empty-states/index.ts` | 10 | Barrel (Re-Exporte) | 2.5.3 | erreichbar |
| `home/widgets/empty-states/links.tsx` | 21 | `LinksEmptyState` | 2.5.3 | erreichbar |
| `home/widgets/empty-states/no-projects.tsx` | 205 | `NoProjectsEmptyState` | 2.5.5 | erreichbar |
| `home/widgets/empty-states/recents.tsx` | 46 | `RecentsEmptyState` | 2.5.3 | erreichbar |
| `home/widgets/empty-states/stickies.tsx` | 17 | `StickiesEmptyState` | 2.5.3 | erreichbar |
| `home/widgets/index.ts` | 9 | Barrel (Re-Exporte) | 2.5 | erreichbar |
| `home/widgets/links/action.tsx` | 28 | `AddLink` | 2.5.6 / 3.6 | nicht erreichbar |
| `home/widgets/links/create-update-link-modal.tsx` | 174 | `TLinkOperationsModal`, `TLinkCreateFormFieldOptions`, `TLinkCreateEditModal`, `LinkCreateUpdateModal` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/index.ts` | 9 | Barrel (Re-Exporte) | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/link-detail.tsx` | 109 | `TProjectLinkDetail`, `ProjectLinkDetail` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/link-item-block.tsx` | 81 | `TLinkItemBlockProps`, `LinkItemBlock` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/links.tsx` | 53 | `TLinkOperationsModal`, `TProjectLinkList`, `ProjectLinkList` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/root.tsx` | 66 | `DashboardQuickLinks` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/links/use-links.tsx` | 105 | `TLinkOperations`, `TProjectLinkRoot`, `useLinks` | 2.5.6 / 3.6 | erreichbar |
| `home/widgets/loaders/home-loader.tsx` | 28 | `HomeLoader` | 2.5.3 | erreichbar |
| `home/widgets/loaders/index.ts` | 8 | Barrel (Re-Exporte) | 2.5.3 | erreichbar |
| `home/widgets/loaders/loader.tsx` | 31 | `EWidgetKeys`, `WidgetLoader` | 2.5.3 | erreichbar |
| `home/widgets/loaders/quick-links.tsx` | 19 | `QuickLinksWidgetLoader` | 2.5.3 | erreichbar |
| `home/widgets/loaders/recent-activity.tsx` | 26 | `RecentActivityWidgetLoader` | 2.5.3 | erreichbar |
| `home/widgets/manage/index.tsx` | 54 | `TProps`, `ManageWidgetsModal` | 2.5.4 | erreichbar |
| `home/widgets/manage/widget-item-drag-handle.tsx` | 31 | `WidgetItemDragHandle` | 2.5.4 | erreichbar |
| `home/widgets/manage/widget-item.tsx` | 150 | `WidgetItem` | 2.5.4 | erreichbar |
| `home/widgets/manage/widget-list.tsx` | 70 | `WidgetList` | 2.5.4 | erreichbar |
| `home/widgets/manage/widget.helpers.ts` | 68 | `TargetData`, `getInstructionFromPayload`, `getCanDrop` | 2.5.4 | erreichbar |
| `home/widgets/recents/filters.tsx` | 50 | `TFiltersDropdown`, `FiltersDropdown` | 2.5.7 / 3.6 | erreichbar |
| `home/widgets/recents/index.tsx` | 111 | `RecentActivityWidget` | 2.5.7 / 3.6 | erreichbar |
| `home/widgets/recents/issue.tsx` | 139 | `RecentIssue` | 2.5.7 / 3.6 | erreichbar |
| `home/widgets/recents/page.tsx` | 87 | `RecentPage` | 2.5.7 / 3.6 | erreichbar |
| `home/widgets/recents/project.tsx` | 78 | `RecentProject` | 2.5.7 / 3.6 | erreichbar |

#### `stickies/` (17 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `stickies/action-bar.tsx` | 150 | `StickyActionBar` | 2.6 / 2.21 | nicht erreichbar |
| `stickies/delete-modal.tsx` | 52 | `StickyDeleteModal` | 2.6 | erreichbar |
| `stickies/layout/stickies-infinite.tsx` | 69 | `StickiesInfinite` | 2.6 | erreichbar |
| `stickies/layout/stickies-list.tsx` | 213 | `StickiesList`, `StickiesLayout` | 2.6 | erreichbar |
| `stickies/layout/stickies-loader.tsx` | 53 | `StickiesLoader` | 2.6 | erreichbar |
| `stickies/layout/stickies-truncated.tsx` | 58 | `StickiesTruncated` | 2.6 | erreichbar |
| `stickies/layout/sticky-dnd-wrapper.tsx` | 140 | `StickyDNDWrapper` | 2.6 | erreichbar |
| `stickies/layout/sticky.helpers.ts` | 51 | `TargetData`, `getInstructionFromPayload` | 2.6 | erreichbar |
| `stickies/modal/index.tsx` | 34 | `AllStickiesModal` | 2.6 / 2.21 | nicht erreichbar |
| `stickies/modal/search.tsx` | 107 | `StickySearch` | 2.6 | erreichbar |
| `stickies/modal/stickies.tsx` | 80 | `Stickies` | 2.6 / 2.21 | nicht erreichbar |
| `stickies/sticky/index.ts` | 7 | Barrel (Re-Exporte) | 2.6 | erreichbar |
| `stickies/sticky/inputs.tsx` | 106 | `StickyInput` | 2.6 | erreichbar |
| `stickies/sticky/root.tsx` | 112 | `StickyNote` | 2.6 | erreichbar |
| `stickies/sticky/sticky-item-drag-handle.tsx` | 32 | `StickyItemDragHandle` | 2.6 | nicht erreichbar |
| `stickies/sticky/use-operations.tsx` | 154 | `TOperations`, `getRandomStickyColor`, `useStickyOperations` | 2.6 | erreichbar |
| `stickies/widget.tsx` | 63 | `StickiesWidget` | 2.5.8 | erreichbar |

#### `workspace-notifications/` (28 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `workspace-notifications/index.ts` | 7 | Barrel (Re-Exporte) | 2.7 | erreichbar |
| `workspace-notifications/notification-app-sidebar-option.tsx` | 45 | `NotificationAppSidebarOption` | 2.7 / 2.21 | nicht erreichbar |
| `workspace-notifications/notification-card/content.ts` | 31 | `ADDITIONAL_NOTIFICATION_CONTENT_MAP`, `renderAdditionalAction`, `renderAdditionalValue`, `shouldShowConnector`, `shouldRender` | 2.7.3 | erreichbar |
| `workspace-notifications/notification-card/root.tsx` | 62 | `NotificationCardListRoot` | 2.7.3 | erreichbar |
| `workspace-notifications/root.tsx` | 118 | `NotificationsRoot` | 2.7.4 | erreichbar |
| `workspace-notifications/sidebar/empty-state.tsx` | 37 | `NotificationEmptyState` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/filters/applied-filter.tsx` | 72 | `AppliedFilters` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/filters/menu/index.ts` | 7 | Barrel (Re-Exporte) | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/filters/menu/root.tsx` | 60 | `NotificationFilter` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/index.ts` | 7 | Barrel (Re-Exporte) | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/options/index.ts` | 7 | Barrel (Re-Exporte) | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/options/menu-option/index.ts` | 7 | Barrel (Re-Exporte) | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/options/menu-option/root.tsx` | 95 | `NotificationHeaderMenuOption` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/options/root.tsx` | 91 | `NotificationSidebarHeaderOptions` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/header/root.tsx` | 49 | `NotificationSidebarHeader` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/index.ts` | 7 | Barrel (Re-Exporte) | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/loader.tsx` | 26 | `NotificationsLoader` | 2.7.1 | erreichbar |
| `workspace-notifications/sidebar/notification-card/content.tsx` | 234 | `TNotificationFieldData`, `TNotificationContentDetails`, `TNotificationContentHandler`, `TNotificationContentMap`, `BASE_NOTIFICATION_CONTENT_MAP`, `NotificationContent` | 2.7.3 | erreichbar |
| `workspace-notifications/sidebar/notification-card/item.tsx` | 145 | `NotificationItem` | 2.7.2 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/archive.tsx` | 57 | `NotificationItemArchiveOption` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/button.tsx` | 44 | `NotificationItemOptionButton` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/index.ts` | 13 | Barrel (Re-Exporte) | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/read.tsx` | 51 | `NotificationItemReadOption` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/root.tsx` | 63 | `NotificationOption` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/snooze/index.ts` | 8 | Barrel (Re-Exporte) | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/snooze/modal.tsx` | 271 | `NotificationSnoozeModal` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/notification-card/options/snooze/root.tsx` | 142 | `NotificationItemSnoozeOption` | 2.7.2 / 3.7 | erreichbar |
| `workspace-notifications/sidebar/root.tsx` | 122 | `NotificationsSidebarRoot` | 2.7.1 | erreichbar |

#### `profile/` (14 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `profile/activity/activity-list.tsx` | 185 | `ActivityList` | 2.8.5 | erreichbar |
| `profile/activity/download-button.tsx` | 72 | `DownloadActivityButton` | 2.8.5 | erreichbar |
| `profile/activity/workspace-activity-list.tsx` | 55 | `WorkspaceActivityListPage` | 2.8.5 | erreichbar |
| `profile/overview/activity.tsx` | 91 | `ProfileActivity` | 2.8.3 | erreichbar |
| `profile/overview/priority-distribution.tsx` | 87 | `ProfilePriorityDistribution` | 2.8.3 | erreichbar |
| `profile/overview/state-distribution.tsx` | 90 | `ProfileStateDistribution` | 2.8.3 | erreichbar |
| `profile/overview/stats.tsx` | 77 | `ProfileStats` | 2.8.3 | erreichbar |
| `profile/overview/workload.tsx` | 53 | `ProfileWorkload` | 2.8.3 | erreichbar |
| `profile/profile-issues-filter.tsx` | 87 | `ProfileIssuesFilter` | 2.8.4 | erreichbar |
| `profile/profile-issues.tsx` | 82 | `ProfileIssuesPage` | 2.8.4 | erreichbar |
| `profile/profile-setting-content-wrapper.tsx` | 33 | `ProfileSettingContentWrapper` | 2.8 / 2.21 | nicht erreichbar |
| `profile/sidebar.tsx` | 284 | `ProfileSidebar` | 2.8.2 | erreichbar |
| `profile/start-of-week-preference.tsx` | 68 | `StartOfWeekPreference` | 2.13.3 | erreichbar |
| `profile/time.tsx` | 33 | `ProfileSidebarTime` | 2.8.2 | erreichbar |

#### `power-k/` (79 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `power-k/config/account-commands.ts` | 64 | `usePowerKAccountCommands` | 2.9.2 | erreichbar |
| `power-k/config/commands.ts` | 35 | `useProjectsAppPowerKCommands` | 2.9.2 | erreichbar |
| `power-k/config/creation/command.ts` | 163 | `TPowerKCreationCommandKeys`, `usePowerKCreationCommandsRecord` | 2.9.2 | erreichbar |
| `power-k/config/creation/root.ts` | 24 | `usePowerKCreationCommands` | 2.9.2 | erreichbar |
| `power-k/config/help-commands.ts` | 73 | `usePowerKHelpCommands` | 2.9.2 | erreichbar |
| `power-k/config/miscellaneous-commands.ts` | 90 | `usePowerKMiscellaneousCommands` | 2.9.2 | erreichbar |
| `power-k/config/navigation/commands.ts` | 538 | `TPowerKNavigationCommandKeys`, `usePowerKNavigationCommandsRecord` | 2.9.2 | erreichbar |
| `power-k/config/navigation/root.ts` | 51 | `usePowerKNavigationCommands` | 2.9.2 | erreichbar |
| `power-k/config/preferences-commands.ts` | 168 | `usePowerKPreferencesCommands` | 2.9.2 | erreichbar |
| `power-k/core/context-detector.ts` | 18 | `detectContextFromURL` | 2.9.1 | erreichbar |
| `power-k/core/registry.ts` | 166 | `IPowerKCommandRegistry`, `PowerKCommandRegistry implements IPowerKCommandRegistry` | 2.9.1 | erreichbar |
| `power-k/core/shortcut-handler.ts` | 379 | `TKeyboardLayoutMap`, `resolveShortcutKey`, `formatModifierShortcut`, `isTypingInInput`, `ShortcutHandler` | 2.9.1 / 3.9.1 | erreichbar |
| `power-k/core/types.ts` | 129 | `TPowerKContextType`, `TPowerKContext`, `TPowerKPageType`, `TPowerKCommandGroup`, `TPowerKCommandConfig`, `TCommandPaletteState`, `TSelectionPageProps`, `TPowerKSearchResultsKeys` | 2.9.1 | erreichbar |
| `power-k/global-shortcuts.tsx` | 84 | `GlobalShortcutsProvider` | 2.9 | erreichbar |
| `power-k/hooks/use-context-indicator.ts` | 57 | `useContextIndicator` | 2.9 | erreichbar |
| `power-k/menus/builder.tsx` | 55 | `PowerKMenuBuilder` | 2.9.2 | erreichbar |
| `power-k/menus/cycles.tsx` | 34 | `PowerKCyclesMenu` | 2.9.2 | erreichbar |
| `power-k/menus/empty-state.tsx` | 15 | `PowerKMenuEmptyState` | 2.9.2 | erreichbar |
| `power-k/menus/labels.tsx` | 37 | `PowerKLabelsMenu` | 2.9.2 | erreichbar |
| `power-k/menus/members.tsx` | 55 | `PowerKMembersMenu` | 2.9.2 | erreichbar |
| `power-k/menus/modules.tsx` | 34 | `PowerKModulesMenu` | 2.9.2 | erreichbar |
| `power-k/menus/projects.tsx` | 36 | `PowerKProjectsMenu` | 2.9.2 | erreichbar |
| `power-k/menus/settings.tsx` | 36 | `PowerKSettingsMenu` | 2.9.2 | erreichbar |
| `power-k/menus/views.tsx` | 32 | `PowerKViewsMenu` | 2.9.2 | erreichbar |
| `power-k/menus/workspaces.tsx` | 34 | `PowerKWorkspacesMenu` | 2.9.2 | erreichbar |
| `power-k/projects-app-provider.tsx` | 95 | `ProjectsAppPowerKProvider` | 2.9 | erreichbar |
| `power-k/ui/modal/command-item-shortcut-badge.tsx` | 112 | `formatShortcutForDisplay`, `ShortcutBadge`, `KeySequenceBadge` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/command-item.tsx` | 62 | `PowerKModalCommandItem` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/commands-list.tsx` | 58 | `TPowerKCommandsListProps`, `ProjectsAppPowerKCommandsList` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/constants.ts` | 75 | `TPowerKModalPageDetails`, `POWER_K_MODAL_PAGE_DETAILS` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/context-indicator.tsx` | 52 | `PowerKModalContextIndicator` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/footer.tsx` | 38 | `PowerKModalFooter` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/header.tsx` | 64 | `PowerKModalHeader` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/no-results-command.tsx` | 40 | `TPowerKModalNoSearchResultsCommandProps`, `PowerKModalNoSearchResultsCommand` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/search-menu.tsx` | 115 | `PowerKModalSearchMenu` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/search-results-map.tsx` | 120 | `TPowerKSearchResultGroupDetails`, `POWER_K_SEARCH_RESULTS_GROUPS_MAP` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/search-results.tsx` | 71 | `PowerKModalSearchResults` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/shortcuts-root.tsx` | 104 | `ShortcutsModal` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/modal/wrapper.tsx` | 174 | `ProjectsAppPowerKModalWrapper` | 2.9.3 / 3.9.2 | erreichbar |
| `power-k/ui/pages/context-based/cycle/commands.ts` | 101 | `usePowerKCycleContextBasedActions` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/index.ts` | 34 | Barrel (Re-Exporte) | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/module/commands.tsx` | 167 | `usePowerKModuleContextBasedActions` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/module/index.ts` | 7 | Barrel (Re-Exporte) | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/module/root.tsx` | 54 | `PowerKModuleContextBasedPages` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/module/status-menu.tsx` | 40 | `PowerKModuleStatusMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/page/commands.ts` | 189 | `usePowerKPageContextBasedActions` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/root.tsx` | 45 | `ContextBasedActionsProps`, `PowerKContextBasedPagesList`, `usePowerKContextBasedActions` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/commands.ts` | 459 | `usePowerKWorkItemContextBasedCommands` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/cycles-menu.tsx` | 33 | `PowerKWorkItemCyclesMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/estimates-menu.tsx` | 73 | `PowerKWorkItemEstimatesMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/index.ts` | 7 | Barrel (Re-Exporte) | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/labels-menu.tsx` | 33 | `PowerKWorkItemLabelsMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/modules-menu.tsx` | 35 | `PowerKWorkItemModulesMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/priorities-menu.tsx` | 37 | `PowerKWorkItemPrioritiesMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/root.tsx` | 84 | `PowerKWorkItemContextBasedPages` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/state-menu-item.tsx` | 39 | `TPowerKProjectStatesMenuItemsProps`, `PowerKProjectStatesMenuItems` | 2.9.2 | erreichbar |
| `power-k/ui/pages/context-based/work-item/states-menu.tsx` | 47 | `PowerKProjectStatesMenu` | 2.9.2 | erreichbar |
| `power-k/ui/pages/default.tsx` | 27 | `PowerKModalDefaultPage` | 2.9 | erreichbar |
| `power-k/ui/pages/index.ts` | 7 | Barrel (Re-Exporte) | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/project-cycles-menu.tsx` | 37 | `PowerKOpenProjectCyclesMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/project-modules-menu.tsx` | 37 | `PowerKOpenProjectModulesMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/project-settings-menu.tsx` | 48 | `PowerKOpenProjectSettingsMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/project-views-menu.tsx` | 34 | `PowerKOpenProjectViewsMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/projects-menu.tsx` | 32 | `PowerKOpenProjectMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/root.tsx` | 41 | `PowerKOpenEntityPages` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/shared.ts` | 14 | `TPowerKOpenEntityActionsProps` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/workspace-settings-menu.tsx` | 42 | `PowerKOpenWorkspaceSettingsMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/open-entity/workspaces-menu.tsx` | 30 | `PowerKOpenWorkspaceMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/index.ts` | 7 | Barrel (Re-Exporte) | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/languages-menu.tsx` | 29 | `PowerKPreferencesLanguagesMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/root.tsx` | 33 | `PowerKAccountPreferencesPages` | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/start-of-week-menu.tsx` | 29 | `PowerKPreferencesStartOfWeekMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/themes-menu.tsx` | 41 | `PowerKPreferencesThemesMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/preferences/timezone-menu.tsx` | 35 | `PowerKPreferencesTimezonesMenu` | 2.9 | erreichbar |
| `power-k/ui/pages/root.tsx` | 36 | `PowerKModalPagesList` | 2.9 | erreichbar |
| `power-k/ui/renderer/command.tsx` | 79 | `CommandRenderer` | 2.9.1 | erreichbar |
| `power-k/ui/renderer/shared.ts` | 31 | `POWER_K_GROUP_PRIORITY`, `POWER_K_GROUP_I18N_TITLES` | 2.9.1 | erreichbar |
| `power-k/ui/renderer/shortcut.tsx` | 124 | `ShortcutRenderer` | 2.9.1 | erreichbar |
| `power-k/utils/navigation.ts` | 26 | `handlePowerKNavigate` | 2.9 | erreichbar |

#### `settings/` (42 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `settings/boxed-control-item.tsx` | 34 | `SettingsBoxedControlItem` | 2.10 | erreichbar |
| `settings/content-wrapper.tsx` | 41 | `SettingsContentWrapper` | 2.10 | erreichbar |
| `settings/control-item.tsx` | 25 | `SettingsControlItem` | 2.10 | erreichbar |
| `settings/heading.tsx` | 38 | `SettingsHeading` | 2.10 | erreichbar |
| `settings/helper.ts` | 51 | `pathnameToAccessKey`, `getWorkspaceActivePath`, `getProjectActivePath` | 2.10 | erreichbar |
| `settings/layout.tsx` | 23 | `SettingsContentLayout` | 2.10 | nicht erreichbar |
| `settings/mobile/nav.tsx` | 58 | `SettingsMobileNav` | 2.10 | erreichbar |
| `settings/page-header.tsx` | 23 | `SettingsPageHeader` | 2.10 | erreichbar |
| `settings/profile/content/index.ts` | 7 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/content/pages/api-tokens.tsx` | 83 | `APITokensProfileSettings` | 2.13 | erreichbar |
| `settings/profile/content/pages/general/form.tsx` | 437 | `GeneralProfileSettingsForm` | 2.13 | erreichbar |
| `settings/profile/content/pages/general/index.ts` | 7 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/content/pages/general/root.tsx` | 29 | `GeneralProfileSettings` | 2.13 | erreichbar |
| `settings/profile/content/pages/index.ts` | 17 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/content/pages/notifications/email-notification-form.tsx` | 172 | `NotificationsProfileSettingsForm` | 2.13 | erreichbar |
| `settings/profile/content/pages/notifications/index.ts` | 7 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/content/pages/notifications/root.tsx` | 43 | `NotificationsProfileSettings` | 2.13 | erreichbar |
| `settings/profile/content/pages/preferences/default-list.tsx` | 23 | `ProfileSettingsDefaultPreferencesList` | 2.13 | erreichbar |
| `settings/profile/content/pages/preferences/index.ts` | 7 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/content/pages/preferences/language-and-timezone-list.tsx` | 119 | `ProfileSettingsLanguageAndTimezonePreferencesList` | 2.13 | erreichbar |
| `settings/profile/content/pages/preferences/root.tsx` | 42 | `PreferencesProfileSettings` | 2.13 | erreichbar |
| `settings/profile/content/pages/security.tsx` | 293 | `FormValues`, `SecurityProfileSettings` | 2.13 | erreichbar |
| `settings/profile/content/root.tsx` | 36 | `ProfileSettingsContent` | 2.13 | erreichbar |
| `settings/profile/heading.tsx` | 27 | `ProfileSettingsHeading` | 2.13 | erreichbar |
| `settings/profile/modal.tsx` | 75 | `ProfileSettingsModal` | 2.13 | erreichbar |
| `settings/profile/sidebar/header.tsx` | 36 | `ProfileSettingsSidebarHeader` | 2.13 | erreichbar |
| `settings/profile/sidebar/index.ts` | 7 | Barrel (Re-Exporte) | 2.13 | erreichbar |
| `settings/profile/sidebar/item-categories.tsx` | 77 | `ProfileSettingsSidebarItemCategories` | 2.13 | erreichbar |
| `settings/profile/sidebar/root.tsx` | 37 | `ProfileSettingsSidebarRoot` | 2.13 | erreichbar |
| `settings/profile/sidebar/workspace-options.tsx` | 56 | `ProfileSettingsSidebarWorkspaceOptions` | 2.13 | erreichbar |
| `settings/project/content/feature-control-item.tsx` | 74 | `ProjectSettingsFeatureControlItem` | 2.11.1 | erreichbar |
| `settings/project/sidebar/header.tsx` | 66 | `ProjectSettingsSidebarHeader` | 2.11.1 | erreichbar |
| `settings/project/sidebar/index.ts` | 7 | Barrel (Re-Exporte) | 2.11.1 | erreichbar |
| `settings/project/sidebar/item-categories.tsx` | 80 | `ProjectSettingsSidebarItemCategories` | 2.11.1 | erreichbar |
| `settings/project/sidebar/item-icon.tsx` | 38 | `PROJECT_SETTINGS_ICONS` | 2.11.1 | erreichbar |
| `settings/project/sidebar/root.tsx` | 30 | `ProjectSettingsSidebarRoot` | 2.11.1 | erreichbar |
| `settings/sidebar/item.tsx` | 60 | `SettingsSidebarItem` | 2.10 | erreichbar |
| `settings/workspace/sidebar/header.tsx` | 63 | `WorkspaceSettingsSidebarHeader` | 2.10.1 | erreichbar |
| `settings/workspace/sidebar/index.ts` | 7 | Barrel (Re-Exporte) | 2.10.1 | erreichbar |
| `settings/workspace/sidebar/item-categories.tsx` | 74 | `WorkspaceSettingsSidebarItemCategories` | 2.10.1 | erreichbar |
| `settings/workspace/sidebar/item-icon.tsx` | 25 | `WORKSPACE_SETTINGS_ICONS` | 2.10.1 | erreichbar |
| `settings/workspace/sidebar/root.tsx` | 34 | `WorkspaceSettingsSidebarRoot` | 2.10.1 | erreichbar |

#### `project/` (46 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `project/applied-filters/access.tsx` | 44 | `AppliedAccessFilters` | 2.12.1 | erreichbar |
| `project/applied-filters/date.tsx` | 60 | `AppliedDateFilters` | 2.12.1 | erreichbar |
| `project/applied-filters/index.ts` | 7 | Barrel (Re-Exporte) | 2.12.1 | erreichbar |
| `project/applied-filters/members.tsx` | 58 | `AppliedMembersFilters` | 2.12.1 | erreichbar |
| `project/applied-filters/project-display-filters.tsx` | 47 | `AppliedProjectDisplayFilters` | 2.12.1 | erreichbar |
| `project/applied-filters/root.tsx` | 130 | `ProjectAppliedFiltersList` | 2.12.1 | erreichbar |
| `project/archive-restore-modal.tsx` | 135 | `ArchiveRestoreProjectModal` | 2.11.4 | erreichbar |
| `project/card-list.tsx` | 114 | `ProjectCardList` | 2.12.2 | erreichbar |
| `project/card.tsx` | 394 | `ProjectCard` | 2.12.2 | erreichbar |
| `project/confirm-project-member-remove.tsx` | 117 | `ConfirmProjectMemberRemove` | 2.11.3 | erreichbar |
| `project/create-project-modal.tsx` | 92 | `CreateProjectModal` | 2.12.3 | erreichbar |
| `project/create/common-attributes.tsx` | 168 | `ProjectCommonAttributes` (default) | 2.12.3 | erreichbar |
| `project/create/header.tsx` | 119 | `ProjectCreateHeader` (default) | 2.12.3 | erreichbar |
| `project/create/project-create-buttons.tsx` | 54 | `ProjectCreateButtons` (default) | 2.12.3 | erreichbar |
| `project/delete-project-modal.tsx` | 188 | `DeleteProjectModal` | 2.11.4 | erreichbar |
| `project/dropdowns/filters/access.tsx` | 58 | `FilterAccess` | 2.12.1 | erreichbar |
| `project/dropdowns/filters/created-at.tsx` | 88 | `FilterCreatedDate` | 2.12.1 | erreichbar |
| `project/dropdowns/filters/index.ts` | 7 | Barrel (Re-Exporte) | 2.12.1 | erreichbar |
| `project/dropdowns/filters/lead.tsx` | 116 | `FilterLead` | 2.12.1 | erreichbar |
| `project/dropdowns/filters/member-list.tsx` | 89 | `MemberListFiltersDropdown` | 2.12.1 | erreichbar |
| `project/dropdowns/filters/members.tsx` | 116 | `FilterMembers` | 2.12.1 | erreichbar |
| `project/dropdowns/filters/root.tsx` | 110 | `ProjectFiltersSelection` | 2.12.1 | erreichbar |
| `project/dropdowns/order-by.tsx` | 78 | `ProjectOrderByDropdown` | 2.12.1 | erreichbar |
| `project/empty-state.tsx` | 51 | `EmptyState` | 2.12 / 2.21 | nicht erreichbar |
| `project/filters.tsx` | 109 | `HeaderFilters` (default) | 2.12.1 | erreichbar |
| `project/form-loader.tsx` | 67 | `ProjectDetailsFormLoader` | 2.11.2 | erreichbar |
| `project/form.tsx` | 473 | `IProjectDetailsForm`, `ProjectDetailsForm` | 2.11.2 | erreichbar |
| `project/header.tsx` | 93 | `ProjectsBaseHeader` | 2.12.1 | erreichbar |
| `project/integration-card.tsx` | 125 | `IntegrationCard` | 2.12 / 2.21 | nicht erreichbar |
| `project/join-project-modal.tsx` | 96 | `JoinProjectModal` | 2.11.4 | erreichbar |
| `project/leave-project-modal.tsx` | 207 | `ILeaveProjectModal`, `LeaveProjectModal` | 2.11.4 | erreichbar |
| `project/member-header-column.tsx` | 105 | `MemberHeaderColumn` | 2.11.3 | erreichbar |
| `project/member-list-item.tsx` | 95 | `ProjectMemberListItem` | 2.11.3 | erreichbar |
| `project/member-list.tsx` | 133 | `ProjectMemberList` | 2.11.3 | erreichbar |
| `project/multi-select-modal.tsx` | 197 | `ProjectMultiSelectModal` | 2.12 / 2.21 | nicht erreichbar |
| `project/project-feature-update.tsx` | 63 | `ProjectFeatureUpdate` | 2.12.3 | erreichbar |
| `project/project-network-icon.tsx` | 36 | `ProjectNetworkIcon` | 2.11.2 | erreichbar |
| `project/project-settings-member-defaults.tsx` | 215 | `ProjectSettingsMemberDefaults` | 2.11.3 | erreichbar |
| `project/publish-project/modal.tsx` | 390 | `PublishProjectModal` | 2.11.4 | erreichbar |
| `project/root.tsx` | 101 | `ProjectRoot` | 2.12.1 | erreichbar |
| `project/search-projects.tsx` | 89 | `ProjectSearch` | 2.12.1 | erreichbar |
| `project/send-project-invitation-modal.tsx` | 307 | `SendProjectInvitationModal` | 2.11.3 | erreichbar |
| `project/settings/control-section.tsx` | 91 | `GeneralProjectSettingsControlSection` | 2.11 | erreichbar |
| `project/settings/features-list.tsx` | 147 | `ProjectFeaturesList` | 2.11 | erreichbar |
| `project/settings/helper.tsx` | 40 | `ProjectFeatureToggle` | 2.11 | erreichbar |
| `project/settings/member-columns.tsx` | 218 | `RowData extends Pick`, `NameColumn`, `AccountTypeColumn` | 2.11 | erreichbar |

#### `projects/` (7 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `projects/create/attributes.tsx` | 92 | `ProjectAttributes` | 2.12.3 | erreichbar |
| `projects/create/root.tsx` | 193 | `TCreateProjectFormProps`, `CreateProjectForm` | 2.12.3 | erreichbar |
| `projects/create/utils.ts` | 24 | `getProjectFormValues` | 2.12.3 | erreichbar |
| `projects/mobile-header.tsx` | 99 | `ProjectsListMobileHeader` | 2.12.1 | erreichbar |
| `projects/page.tsx` | 30 | `ProjectPageRoot` | 2.12.1 | erreichbar |
| `projects/settings/intake/header.tsx` | 101 | `ProjectInboxHeader` | 2.12 | erreichbar |
| `projects/settings/useProjectColumns.tsx` | 144 | `RowData extends Pick`, `useProjectColumns` | 2.11.3 | erreichbar |

#### `account/` (15 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `account/auth-forms/auth-header.tsx` | 124 | `AuthHeader`, `AuthHeaderBase` | 2.14.2 | erreichbar |
| `account/auth-forms/auth-root.tsx` | 168 | `AuthRoot` | 2.14.2 | erreichbar |
| `account/auth-forms/common/container.tsx` | 13 | `FormContainer` | 2.14.2 | erreichbar |
| `account/auth-forms/common/header.tsx` | 14 | `AuthFormHeader` | 2.14.2 | erreichbar |
| `account/auth-forms/email.tsx` | 114 | `AuthEmailForm` | 2.14.2 | erreichbar |
| `account/auth-forms/forgot-password-popover.tsx` | 50 | `ForgotPasswordPopover` | 2.14.2 / 2.14.3 | erreichbar |
| `account/auth-forms/forgot-password.tsx` | 149 | `ForgotPasswordForm` | 2.14.2 / 2.14.3 | erreichbar |
| `account/auth-forms/form-root.tsx` | 138 | `AuthFormRoot` | 2.14.2 | erreichbar |
| `account/auth-forms/index.ts` | 7 | Barrel (Re-Exporte) | 2.14.2 | nicht erreichbar |
| `account/auth-forms/password.tsx` | 310 | `AuthPasswordForm` | 2.14.2 | erreichbar |
| `account/auth-forms/reset-password.tsx` | 217 | `ResetPasswordForm` | 2.14.3 | erreichbar |
| `account/auth-forms/set-password.tsx` | 213 | `SetPasswordForm` | 2.14.3 / 2.21 | nicht erreichbar |
| `account/auth-forms/unique-code.tsx` | 179 | `AuthUniqueCodeForm` | 2.14.2 | erreichbar |
| `account/deactivate-account-modal.tsx` | 73 | `DeactivateAccountModal` | 2.13.2 | erreichbar |
| `account/terms-and-conditions.tsx` | 45 | `TermsAndConditions` | 2.14.1 | erreichbar |

#### `auth-screens/` (6 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `auth-screens/auth-base.tsx` | 25 | `AuthBase` | 2.14.1 | erreichbar |
| `auth-screens/footer.tsx` | 45 | `AuthFooter` | 2.14.1 | erreichbar |
| `auth-screens/header.tsx` | 80 | `AuthHeader`, `AuthHeaderBase` | 2.14.1 | erreichbar |
| `auth-screens/not-authorized-view.tsx` | 42 | `NotAuthorizedView` | 2.14.4 | erreichbar |
| `auth-screens/project/project-access-restriction.tsx` | 76 | `ProjectAccessRestriction` | 2.14.4 | erreichbar |
| `auth-screens/workspace/not-a-member.tsx` | 47 | `NotAWorkspaceMember` | 2.14.4 / 2.21 | nicht erreichbar |

#### `onboarding/` (31 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `onboarding/create-or-join-workspaces.tsx` | 98 | `ECreateOrJoinWorkspaceViews`, `CreateOrJoinWorkspaces` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/create-workspace.tsx` | 280 | `CreateWorkspace` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/header.tsx` | 93 | `OnboardingHeader` | 2.15.1 | erreichbar |
| `onboarding/index.ts` | 7 | Barrel (Re-Exporte) | 2.15 | erreichbar |
| `onboarding/invitations.tsx` | 130 | `Invitations` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/invite-members.tsx` | 367 | `InviteMembers` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/profile-setup.tsx` | 563 | `ProfileSetup` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/root.tsx` | 144 | `OnboardingRoot` | 2.15.1 / 3.8.5 | erreichbar |
| `onboarding/step-indicator.tsx` | 51 | `OnboardingStepIndicator` | 2.15 / 2.21 | nicht erreichbar |
| `onboarding/steps/common/header.tsx` | 19 | `CommonOnboardingHeader` | 2.15.2 | erreichbar |
| `onboarding/steps/common/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/profile/consent.tsx` | 29 | `MarketingConsent` | 2.15.2 | erreichbar |
| `onboarding/steps/profile/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/profile/root.tsx` | 263 | `TProfileSetupFormValues`, `ProfileSetupStep` | 2.15.2 | erreichbar |
| `onboarding/steps/profile/set-password.tsx` | 133 | `SetPasswordRoot` | 2.15.2 | erreichbar |
| `onboarding/steps/role/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/role/root.tsx` | 164 | `RoleSetupStep` | 2.15.2 | erreichbar |
| `onboarding/steps/root.tsx` | 65 | `OnboardingStepRoot` | 2.15.2 | erreichbar |
| `onboarding/steps/team/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/team/root.tsx` | 358 | `InviteTeamStep` | 2.15.2 | erreichbar |
| `onboarding/steps/usecase/index.ts` | 7 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/usecase/root.tsx` | 155 | `UseCaseSetupStep` | 2.15.2 | erreichbar |
| `onboarding/steps/workspace/create.tsx` | 309 | `WorkspaceCreateStep` | 2.15.2 | erreichbar |
| `onboarding/steps/workspace/index.ts` | 9 | Barrel (Re-Exporte) | 2.15.2 | erreichbar |
| `onboarding/steps/workspace/join-invites.tsx` | 126 | `WorkspaceJoinInvitesStep` | 2.15.2 | erreichbar |
| `onboarding/steps/workspace/root.tsx` | 56 | `WorkspaceSetupStep` | 2.15.2 | erreichbar |
| `onboarding/switch-account-dropdown.tsx` | 60 | `SwitchAccountDropdown` | 2.15.1 | erreichbar |
| `onboarding/switch-account-modal.tsx` | 76 | `SwitchAccountModal` | 2.15.1 | erreichbar |
| `onboarding/tour/root.tsx` | 195 | `TOnboardingTourProps`, `TTourSteps`, `TourRoot` | 2.15.4 | erreichbar |
| `onboarding/tour/sidebar.tsx` | 77 | `TourSidebar` | 2.15.4 | erreichbar |

#### `core/` (43 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `core/activity.tsx` | 771 | `IssueLink`, `ActivityIcon`, `ActivityMessage` | 2.16.4 | erreichbar |
| `core/app-header.tsx` | 34 | `AppHeaderProps`, `AppHeader` | 2.4.3 | erreichbar |
| `core/content-overflow-HOC.tsx` | 164 | `ContentOverflowWrapper` | 2.16.1 | erreichbar |
| `core/content-wrapper.tsx` | 22 | `ContentWrapperProps`, `ContentWrapper` | 2.4.3 | erreichbar |
| `core/description-versions/dropdown-item.tsx` | 46 | `DescriptionVersionsDropdownItem` | 2.16.4 | erreichbar |
| `core/description-versions/dropdown.tsx` | 76 | `DescriptionVersionsDropdown` | 2.16.4 | erreichbar |
| `core/description-versions/index.ts` | 7 | Barrel (Re-Exporte) | 2.16.4 | erreichbar |
| `core/description-versions/modal.tsx` | 227 | `DescriptionVersionsModal` | 2.16.4 | erreichbar |
| `core/description-versions/root.tsx` | 106 | `TDescriptionVersionEntityInformation`, `DescriptionVersionsRoot` | 2.16.4 | erreichbar |
| `core/filters/date-filter-modal.tsx` | 171 | `DateFilterModal` | 2.16.4 | erreichbar |
| `core/filters/date-filter-select.tsx` | 68 | `DateFilterSelect` | 2.16.4 | erreichbar |
| `core/image-picker-popover.tsx` | 398 | `ImagePickerPopover` | 2.16.5 | erreichbar |
| `core/list/index.ts` | 8 | Barrel (Re-Exporte) | 2.16.1 | erreichbar |
| `core/list/list-item.tsx` | 116 | `ListItem` | 2.16.1 | erreichbar |
| `core/list/list-root.tsx` | 24 | `ListLayout` | 2.16.1 | erreichbar |
| `core/modals/bulk-delete-issues-modal-item.tsx` | 49 | `BulkDeleteIssuesModalItem` | 2.16.4 | erreichbar |
| `core/modals/bulk-delete-issues-modal.tsx` | 224 | `BulkDeleteIssuesModal` | 2.16.4 | erreichbar |
| `core/modals/change-email-modal.tsx` | 260 | `ChangeEmailModal` | 2.13.2 | erreichbar |
| `core/modals/existing-issues-list-modal.tsx` | 356 | `ExistingIssuesListModal` | 2.16.4 | erreichbar |
| `core/modals/gpt-assistant-popover.tsx` | 306 | `GptAssistantPopover` | 2.16.4 | erreichbar |
| `core/modals/issue-search-modal-empty-state.tsx` | 54 | `IssueSearchModalEmptyState` | 2.16.4 | erreichbar |
| `core/modals/user-image-upload-modal.tsx` | 195 | `UserImageUploadModal` | 2.16.5 | erreichbar |
| `core/modals/workspace-image-upload-modal.tsx` | 209 | `WorkspaceImageUploadModal` | 2.16.5 | erreichbar |
| `core/multiple-select/entity-select-action.tsx` | 41 | `MultipleSelectEntityAction` | 2.16.4 | erreichbar |
| `core/multiple-select/group-select-action.tsx` | 37 | `MultipleSelectGroupAction` | 2.16.4 | erreichbar |
| `core/multiple-select/index.ts` | 9 | Barrel (Re-Exporte) | 2.16.4 | erreichbar |
| `core/multiple-select/select-group.tsx` | 29 | `MultipleSelectGroup` | 2.16.4 | erreichbar |
| `core/page-title.tsx` | 24 | `PageHead` | 2.4.3 | erreichbar |
| `core/render-if-visible-HOC.tsx` | 103 | `RenderIfVisible` (default) | 2.16.1 | erreichbar |
| `core/sidebar/progress-chart.tsx` | 76 | `ProgressChart` (default) | 2.16.4 | erreichbar |
| `core/sidebar/progress-stats/assignee.tsx` | 90 | `TAssigneeData`, `AssigneeStatComponent` | 2.16.4 | erreichbar |
| `core/sidebar/progress-stats/label.tsx` | 91 | `TLabelData`, `LabelStatComponent` | 2.16.4 | erreichbar |
| `core/sidebar/progress-stats/shared.ts` | 51 | `PROGRESS_STATS`, `TSelectedFilterProgressStats`, `createFilterUpdateHandler` | 2.16.4 | erreichbar |
| `core/sidebar/progress-stats/state_group.tsx` | 52 | `TStateGroupData`, `StateGroupStatComponent` | 2.16.4 | erreichbar |
| `core/sidebar/sidebar-menu-hamburger-toggle.tsx` | 30 | `SidebarHamburgerToggle` | 2.16.4 | nicht erreichbar |
| `core/sidebar/single-progress-stats.tsx` | 36 | `SingleProgressStats` | 2.16.4 | erreichbar |
| `core/theme/color-inputs.tsx` | 98 | `CustomThemeColorInputs` | 2.13.3 | erreichbar |
| `core/theme/custom-theme-selector.tsx` | 132 | `CustomThemeSelector` | 2.13.3 | erreichbar |
| `core/theme/download-config-button.tsx` | 70 | `CustomThemeDownloadConfigButton` | 2.13.3 | erreichbar |
| `core/theme/import-config-button.tsx` | 106 | `CustomThemeImportConfigButton` | 2.13.3 | erreichbar |
| `core/theme/input-color-picker.tsx` | 63 | `InputColorPickerProps`, `InputColorPicker` | 2.13.3 | erreichbar |
| `core/theme/theme-mode-selector.tsx` | 57 | `CustomThemeModeSelector` | 2.13.3 | erreichbar |
| `core/theme/theme-switch.tsx` | 78 | `ThemeSwitch` | 2.13.3 | erreichbar |

#### `common/` (26 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `common/access-field.tsx` | 56 | `AccessField` | 2.16.1 | erreichbar |
| `common/activity/activity-block.tsx` | 60 | `ActivityBlockComponent` | 2.21 | nicht erreichbar |
| `common/activity/activity-item.tsx` | 35 | `ActivityItem` | 2.21 | nicht erreichbar |
| `common/activity/helper.tsx` | 291 | `iconsMap`, `messages` | 2.21 | nicht erreichbar |
| `common/activity/user.tsx` | 43 | `User` | 2.21 | nicht erreichbar |
| `common/applied-filters/date.tsx` | 60 | `AppliedDateFilters` | 2.12.1 / 2.16.1 | erreichbar |
| `common/applied-filters/members.tsx` | 59 | `AppliedMembersFilters` | 2.12.1 / 2.16.1 | erreichbar |
| `common/breadcrumb-link.tsx` | 89 | `BreadcrumbLink` | 2.4.3 | erreichbar |
| `common/count-chip.tsx` | 28 | `CountChip` | 2.16.1 | erreichbar |
| `common/cover-image.tsx` | 50 | `CoverImage` | 2.16.1 | erreichbar |
| `common/data-table.tsx` | 108 | `DataTableColumn`, `DataTableRowProps`, `DataTableProps`, `DataTable` | 2.16.1 | erreichbar |
| `common/empty-state.tsx` | 50 | `EmptyState` | 2.16.2 | erreichbar |
| `common/extended-app-header.tsx` | 33 | `ExtendedAppHeader` | 2.4.3 / 3.2 | erreichbar |
| `common/filters/created-at.tsx` | 82 | `FilterCreatedDate` | 2.12.1 / 2.16.1 | erreichbar |
| `common/filters/created-by.tsx` | 116 | `FilterCreatedBy` | 2.12.1 / 2.16.1 | erreichbar |
| `common/latest-feature-block.tsx` | 43 | `LatestFeatureBlock` | 2.21 | nicht erreichbar |
| `common/layout-error-boundary.tsx` | 58 | `LayoutErrorBoundary extends Component` | 2.16.1 | erreichbar |
| `common/layout/sidebar/property-list-item.tsx` | 31 | `SidebarPropertyListItem` | 2.16.1 | erreichbar |
| `common/logo-spinner.tsx` | 22 | `LogoSpinner` | 2.16.1 | erreichbar |
| `common/modal/global.tsx` | 32 | `GlobalModals` | 2.13.1 | erreichbar |
| `common/page-access-icon.tsx` | 23 | `PageAccessIcon` | 2.16.1 | erreichbar |
| `common/pro-icon.tsx` | 19 | `ProIcon` | 2.18 | erreichbar |
| `common/quick-actions-factory.tsx` | 92 | `useQuickActionsFactory` | 2.16.1 | erreichbar |
| `common/quick-actions-helper.tsx` | 153 | `useCycleMenuItems`, `useModuleMenuItems`, `useViewMenuItems`, `useLayoutMenuItems`, `useIntakeHeaderMenuItems` | 2.16.1 | erreichbar |
| `common/switcher-label.tsx` | 55 | `SwitcherIcon`, `SwitcherLabel` | 2.4.3 | erreichbar |
| `common/trigger-guard.ts` | 24 | `handleTriggerClick`, `handleTriggerKeyDown` | 2.16.1 | erreichbar |

#### `empty-state/` (4 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `empty-state/detailed-empty-state-root.tsx` | 121 | `DetailedEmptyState` | 2.16.2 | erreichbar |
| `empty-state/helper.tsx` | 8 | `getEmptyStateImagePath` | 2.16.2 | nicht erreichbar |
| `empty-state/section-empty-state-root.tsx` | 34 | `SectionEmptyState` | 2.16.2 | erreichbar |
| `empty-state/simple-empty-state-root.tsx` | 53 | `SimpleEmptyState` | 2.16.2 | erreichbar |

#### `ui/` (25 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `ui/empty-space.tsx` | 89 | `EmptySpace, EmptySpaceItem` | 2.16.2 | erreichbar |
| `ui/loader/cycle-module-board-loader.tsx` | 51 | `CycleModuleBoardLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/cycle-module-list-loader.tsx` | 41 | `CycleModuleListLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/calendar-layout-loader.tsx` | 47 | `CalendarLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/gantt-layout-loader.tsx` | 70 | `GanttLayoutListItemLoader`, `GanttLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/kanban-layout-loader.tsx` | 65 | `KanbanIssueBlockLoader`, `KanbanColumnLoader`, `KanbanLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/list-layout-loader.tsx` | 102 | `ListLoaderItemRow`, `ListLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/members-layout-loader.tsx` | 23 | `MembersLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/project-inbox/inbox-layout-loader.tsx` | 31 | `InboxLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/project-inbox/inbox-sidebar-loader.tsx` | 29 | `InboxSidebarLoader` | 2.16.3 | erreichbar |
| `ui/loader/layouts/spreadsheet-layout-loader.tsx` | 51 | `SpreadsheetIssueRowLoader`, `SpreadsheetLayoutLoader` | 2.16.3 | erreichbar |
| `ui/loader/notification-loader.tsx` | 26 | `NotificationsLoader` | 2.16.3 | nicht erreichbar |
| `ui/loader/pages-loader.tsx` | 38 | `PagesLoader` | 2.16.3 | nicht erreichbar |
| `ui/loader/projects-loader.tsx` | 44 | `ProjectsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/activity.tsx` | 21 | `ActivitySettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/api-token.tsx` | 30 | `APITokenSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/email.tsx` | 37 | `EmailSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/import-and-export.tsx` | 28 | `ImportExportSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/integration.tsx` | 26 | `IntegrationsSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/members.tsx` | 25 | `MembersSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/settings/web-hook.tsx` | 28 | `WebhookSettingsLoader` | 2.16.3 | erreichbar |
| `ui/loader/utils.tsx` | 12 | `getRandomInt`, `getRandomLength` | 2.16.3 | erreichbar |
| `ui/loader/view-list-loader.tsx` | 28 | `ViewListLoader` | 2.16.3 | erreichbar |
| `ui/markdown-to-component.tsx` | 85 | `MarkdownRenderer` | 2.16.2 | nicht erreichbar |
| `ui/profile-empty-state.tsx` | 27 | `ProfileEmptyState` | 2.16.2 | nicht erreichbar |

#### `icons/` (26 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `icons/attachment/attachment-icon.tsx` | 71 | `getFileIcon` | 2.16.6 | erreichbar |
| `icons/attachment/audio-file-icon.tsx` | 18 | `AudioIconProps`, `AudioIcon` | 2.16.6 | erreichbar |
| `icons/attachment/css-file-icon.tsx` | 15 | `CssIcon` | 2.16.6 | erreichbar |
| `icons/attachment/csv-file-icon.tsx` | 15 | `CsvIcon` | 2.16.6 | erreichbar |
| `icons/attachment/default-file-icon.tsx` | 15 | `DefaultIcon` | 2.16.6 | erreichbar |
| `icons/attachment/doc-file-icon.tsx` | 15 | `DocIcon` | 2.16.6 | erreichbar |
| `icons/attachment/document-icon.tsx` | 27 | `DocumentIcon` | 2.16.6 | erreichbar |
| `icons/attachment/figma-file-icon.tsx` | 15 | `FigmaIcon` | 2.16.6 | erreichbar |
| `icons/attachment/html-file-icon.tsx` | 15 | `HtmlIcon` | 2.16.6 | erreichbar |
| `icons/attachment/img-file-icon.tsx` | 15 | `ImgIcon` | 2.16.6 | erreichbar |
| `icons/attachment/index.ts` | 28 | Barrel (Re-Exporte) | 2.16.6 | erreichbar |
| `icons/attachment/jpg-file-icon.tsx` | 15 | `JpgIcon` | 2.16.6 | erreichbar |
| `icons/attachment/js-file-icon.tsx` | 15 | `JavaScriptIcon` | 2.16.6 | erreichbar |
| `icons/attachment/pdf-file-icon.tsx` | 15 | `PdfIcon` | 2.16.6 | erreichbar |
| `icons/attachment/png-file-icon.tsx` | 15 | `PngIcon` | 2.16.6 | erreichbar |
| `icons/attachment/rar-file-icon.tsx` | 15 | `RarIcon` | 2.16.6 | erreichbar |
| `icons/attachment/setting-icon.tsx` | 27 | `SettingIcon` | 2.16.6 | erreichbar |
| `icons/attachment/sheet-file-icon.tsx` | 15 | `SheetIcon` | 2.16.6 | erreichbar |
| `icons/attachment/svg-file-icon.tsx` | 15 | `SvgIcon` | 2.16.6 | erreichbar |
| `icons/attachment/tune-icon.tsx` | 27 | `TuneIcon` | 2.16.6 | erreichbar |
| `icons/attachment/txt-file-icon.tsx` | 15 | `TxtIcon` | 2.16.6 | erreichbar |
| `icons/attachment/video-file-icon.tsx` | 15 | `VideoIcon` | 2.16.6 | erreichbar |
| `icons/attachment/zip-file-icon.tsx` | 15 | `ZipIcon` | 2.16.6 | erreichbar |
| `icons/index.ts` | 7 | Barrel (Re-Exporte) | 2.16.6 | erreichbar |
| `icons/locked-component.tsx` | 30 | `LockedComponent` | 2.16.6 | nicht erreichbar |
| `icons/types.d.ts` | 11 | Typen `Props`, `ImageIconPros` | 2.16.6 | Typdatei |

#### `modals/` (3 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `modals/project-level.tsx` | 68 | `TProjectLevelModalsProps`, `ProjectLevelModals` | 2.16.7 | erreichbar |
| `modals/work-item-level.tsx` | 111 | `TWorkItemLevelModalsProps`, `WorkItemLevelModals` | 2.16.7 | erreichbar |
| `modals/workspace-level.tsx` | 31 | `TWorkspaceLevelModalsProps`, `WorkspaceLevelModals` | 2.16.7 | erreichbar |

#### `instance/` (4 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `instance/index.ts` | 8 | Barrel (Re-Exporte) | 2.16.8 | erreichbar |
| `instance/maintenance-message.tsx` | 43 | `MaintenanceMessage` | 2.16.8 | erreichbar |
| `instance/maintenance-view.tsx` | 39 | `MaintenanceView` | 2.16.8 | erreichbar |
| `instance/not-ready-view.tsx` | 62 | `InstanceNotReady` | 2.16.8 | erreichbar |

#### `global/` (9 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `global/index.ts` | 9 | Barrel (Re-Exporte) | 2.16.9 | erreichbar |
| `global/product-updates/changelog.tsx` | 95 | `ProductUpdatesChangelog` | 2.16.9 | erreichbar |
| `global/product-updates/fallback.tsx` | 38 | `ProductUpdatesFallback` | 2.16.9 | erreichbar |
| `global/product-updates/footer.tsx` | 75 | `ProductUpdatesFooter` | 2.16.9 | erreichbar |
| `global/product-updates/header.tsx` | 29 | `ProductUpdatesHeader` | 2.16.9 | erreichbar |
| `global/product-updates/index.ts` | 8 | Barrel (Re-Exporte) | 2.16.9 | erreichbar |
| `global/product-updates/modal.tsx` | 45 | `ProductUpdatesModalProps`, `ProductUpdatesModal` | 2.16.9 | erreichbar |
| `global/timezone-select.tsx` | 120 | `TimezoneSelect` | 2.16.9 | erreichbar |
| `global/version-number.tsx` | 18 | `PlaneVersionNumber` | 2.16.9 | erreichbar |

#### `appearance/` (2 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `appearance/index.ts` | 7 | Barrel (Re-Exporte) | 2.13.3 | erreichbar |
| `appearance/theme-switcher.tsx` | 103 | `ThemeSwitcher` | 2.13.3 | erreichbar |

#### `user/` (2 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `user/index.ts` | 7 | Barrel (Re-Exporte) | 2.5.2 / 2.21 | nicht erreichbar |
| `user/user-greetings.tsx` | 61 | `IUserGreetingsView`, `UserGreetingsView` | 2.5.2 / 2.21 | nicht erreichbar |

#### `license/` (10 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `license/index.ts` | 7 | Barrel (Re-Exporte) | 2.18 | erreichbar |
| `license/modal/card/base-paid-plan-card.tsx` | 100 | `TBasePaidPlanCardProps`, `BasePaidPlanCard` | 2.18 | erreichbar |
| `license/modal/card/checkout-button.tsx` | 109 | `TCheckoutParams`, `PlanCheckoutButton` | 2.18 | erreichbar |
| `license/modal/card/discount-info.tsx` | 66 | `DiscountInfo` | 2.18 | erreichbar |
| `license/modal/card/free-plan.tsx` | 47 | `FreePlanCard` | 2.18 | erreichbar |
| `license/modal/card/index.ts` | 10 | Barrel (Re-Exporte) | 2.18 | erreichbar |
| `license/modal/card/plan-upgrade.tsx` | 115 | `PlanUpgradeCardProps`, `PlanUpgradeCard` | 2.18 | erreichbar |
| `license/modal/card/talk-to-sales.tsx` | 114 | `TalkToSalesCardProps`, `TalkToSalesCard` | 2.18 | erreichbar |
| `license/modal/index.ts` | 7 | Barrel (Re-Exporte) | 2.18 | erreichbar |
| `license/modal/upgrade-modal.tsx` | 152 | `PaidPlanUpgradeModalProps`, `PaidPlanUpgradeModal` | 2.18 | erreichbar |

#### `archives/` (2 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `archives/archive-tabs-list.tsx` | 69 | `ArchiveTabsList` | 2.17 | erreichbar |
| `archives/index.ts` | 7 | Barrel (Re-Exporte) | 2.17 | erreichbar |

#### `browse/` (1 Dateien)

| Datei | Zeilen | Exporte | Abschnitt | Status |
|---|---|---|---|---|
| `browse/workItem-detail.tsx` | 29 | `TWorkItemDetailRoot`, `WorkItemDetailRoot` | 2.17 | erreichbar |

### 2.2 Workspace-Shell: Rahmenlayout, Top-Navigation, App-Rail

Komponentenbaum einer Workspace-Seite (Quelle: `apps/web/app/(all)/[workspaceSlug]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/layout.tsx`, `apps/web/components/workspace/content-wrapper.tsx`):

```
WorkspaceLayout (app/(all)/[workspaceSlug]/layout.tsx)
└─ AuthenticationWrapper → WorkspaceAuthWrapper → AppRailVisibilityProvider (isEnabled=false)
   └─ WorkspaceContentWrapper                      (components/workspace/content-wrapper.tsx)
      ├─ TopNavigationRoot                         (components/navigation/top-navigation-root.tsx)
      ├─ [AppRailRoot nur wenn shouldRenderAppRail] (components/navigation/app-rail-root.tsx) – in CE nie
      └─ div.pr-2.pb-2.pl-2  → GlobalModals + <Outlet/>
         └─ (projects)/layout.tsx
            ├─ ProjectsAppPowerKProvider           (components/power-k/projects-app-provider.tsx)
            └─ div.rounded-lg.border.border-subtle (Hauptkarte)
               ├─ #full-screen-portal
               ├─ ProjectAppSidebar (_sidebar.tsx) → ResizableSidebar → AppSidebar (sidebar.tsx) + ExtendedAppSidebar
               ├─ ExtendedProjectSidebar (extended-project-sidebar.tsx)
               └─ main.bg-surface-1 → <Outlet/> (Seite: AppHeader + ContentWrapper)
```

| Element | Datei | Klassen / Maße (1:1) | Inhalt & Verhalten |
|---|---|---|---|
| `WorkspaceContentWrapper` | `apps/web/components/workspace/content-wrapper.tsx` | Außen `relative flex size-full flex-col overflow-hidden bg-canvas transition-all duration-300 ease-in-out`; Innen `relative size-full flex-grow overflow-hidden pr-2 pb-2 pl-2` (bei App-Rail `pl-0!`) | Top-Navigation oben, darunter App-Rail (optional) und Seiteninhalt |
| `TopNavigationRoot` | `apps/web/components/navigation/top-navigation-root.tsx` | `z-[27] flex min-h-10 w-full items-center bg-canvas px-3.5` (bei `displayMode="icon_only"` `px-2`) | Drei Spalten: links `WorkspaceMenuRoot variant="top-navigation"` (`flex-1`), Mitte `TopNavPowerK` (`shrink-0`), rechts (`flex-1 justify-end gap-1`): Inbox-Link (Tooltip „Inbox“, `side="bottom"`), `HelpMenuRoot`, `StarUsOnGitHubLink`, `UserMenuRoot` (in `size-8 rounded-md hover:bg-layer-1-hover`) |
| Inbox-Icon | `top-navigation-root.tsx` | `AppSidebarItem variant="link"`, Icon `InboxOutline size-5`; roter Punkt `absolute top-0 right-0 size-2 rounded-full bg-danger-primary` | `href=/${ws}/notifications/`; aktiv bei `pathname.includes("/notifications/")`; Punkt sichtbar, wenn Zähler > 0. Zähler: wenn `mention_unread_notifications_count > 0` → dieser Wert, sonst `total_unread_notifications_count`. SWR-Key `"WORKSPACE_UNREAD_NOTIFICATION_COUNT"` → `getUnreadNotificationsCount(ws)` |
| `StarUsOnGitHubLink` | `apps/web/app/(all)/[workspaceSlug]/(projects)/star-us-link.tsx` | `flex flex-shrink-0 items-center gap-1.5 rounded-sm bg-layer-2 px-3 py-1.5`; Bild `h-4 w-4`; Label `hidden text-11 font-medium sm:hidden md:block` | Link `https://github.com/makeplane/plane` (`_blank`, `noopener noreferrer`); Logo `github-white.png` bei `resolvedTheme==="dark"`, sonst `github-black.png`; Text `home.star_us_on_github` = „Star us on GitHub“ |
| `AppRailRoot` | `apps/web/components/navigation/app-rail-root.tsx` | Breite `3.75rem` (mit Label) bzw. `3rem` (nur Icon); `z-[26] h-full bg-canvas` | Dock-Items aus `withDockItems` (nur „Projects“ → `/${ws}/`), Trenner, „Settings“ → `/${ws}/settings` (aktiv bei `/settings` ohne `projectId`). Kontextmenü (Rechtsklick): „Icon only“, „Icon with name“, Separator, „Dock App Rail“/„Undock App Rail“. **In CE nie gerendert**, da `AppRailVisibilityProvider isEnabled=false` (`apps/web/lib/app-rail/provider.tsx`) |
| `AppSidebarItemsRoot` / `withDockItems` | `apps/web/components/navigation/items-root.tsx`, `app-rail-hoc.tsx` | – | Dock-Item „Projects“ (Icon `Projects size-5`, aktiv bei `isProjectsPath && !isNotificationsPath` aus `useWorkspacePaths`) |
| `AppSidebarItem` (+ `.Icon`, `.Label`, `.Link`, `.Button`) | `apps/web/components/sidebar/sidebar-item.tsx` | base `group flex flex-col gap-0.5 items-center justify-center text-tertiary`; Icon `flex items-center justify-center gap-2 size-8 rounded-md`; aktiv `bg-layer-transparent-selected text-secondary !text-icon-primary`; inaktiv `group-hover:text-icon-secondary group-hover:bg-layer-transparent-hover !text-icon-tertiary`; Label `text-11 font-medium` | Generisches Rail-/Top-Nav-Item (Variante `link` oder `button`) |

**Workspace-Switcher (`WorkspaceMenuRoot`, `apps/web/components/workspace/sidebar/workspace-menu-root.tsx`)**

| Teil | Detail |
|---|---|
| Trigger `variant="top-navigation"` | Button `group/menu-button flex flex-grow items-center justify-between gap-1 truncate rounded-sm p-1 text-13 font-medium text-secondary hover:bg-layer-1` (offen: `bg-layer-1`); `WorkspaceLogo` `size-7 border border-subtle rounded-md`; Name `h4 truncate text-14 font-medium text-primary` (Fallback `loading` = „Loading“); `ChevronDownOutline size-4 text-placeholder duration-300`, offen `rotate-180`. Container `max-w-48` |
| Trigger `variant="sidebar"` | quadratischer Button `size-8` mit `WorkspaceLogo size-8 rounded-md border` (nur für App-Rail-Layout) |
| Popup | `MenuContent side="bottom" align="start"`, Breite `w-[19rem]`; Kopf (sticky) E-Mail des Nutzers `bg-layer-2 px-4 pt-3 pb-1 text-13 font-medium text-placeholder` |
| Workspace-Liste | `orderWorkspacesList` = alphabetisch nach `name` (`localeCompare`, `packages/utils/src/workspace.ts`); aktiver Workspace wird **an erste Stelle** gezogen; Lade-Skeleton 2× `30px`, solange `workspaces` fehlt |
| Zeile (`SidebarDropdownItem`, `dropdown-item.tsx`) | Wrapper `w-full px-4 py-2` (aktiv `bg-layer-transparent-active`); Logo-Kachel `h-8 w-8` – ohne Logo `rounded-md bg-[#026292] text-on-color` mit Anfangsbuchstabe (uppercase), mit Logo `<img src=getFileURL(logo_url)>`; Name `text-13 font-medium` (nicht aktueller Slug: `text-secondary`); Unterzeile `text-13 text-tertiary capitalize`: Rolle (`getUserRole(role).toLowerCase()`, Fallback „guest“) · Punkt `h-1 w-1 rounded-full` · `t("member",{count: total_members})` („# member/# members“); aktive Zeile: Haken `TickOutline h-5 w-5`. Klick → Link `/${slug}` + `updateUserProfile({last_workspace_id})`; < 768 px zusätzlich Sidebar einklappen |
| Aktionsknöpfe in aktiver Zeile | „Settings“ (`SettingsOutline`) → `/${slug}/settings` nur für Rolle Admin/Member; „Invite members“ (`UserPlusOutline`, `project_settings.members.invite_members.title`) → `/${slug}/settings/members` nur Admin; beide `Button variant="secondary" size="lg"` |
| Fußbereich | `MenuSeparator`; „Create workspace“ (`PlusCircleOutline`, Link `/create-workspace`) nur wenn `!config.is_workspace_creation_disabled`; „Workspace invites“ (`MailOutline`, Link `/invitations`); „Sign out“ (`variant="danger"`, `LogOutOutline`) → `signOut()`, Fehler-Toast `auth.sign_out.toast.error.title/message` |
| Seiteneffekt | Öffnen/Schließen setzt `toggleAnySidebarDropdown(isOpen)` (verhindert Peek-Schließen) |

**Hilfe-Menü (`HelpMenuRoot`, `apps/web/components/workspace/sidebar/help-section/root.tsx`)**

| Eintrag | Aktion |
|---|---|
| Trigger | `HelpOutline size-5` in `AppSidebarItem.Icon` (hervorgehoben solange offen), `aria-label = power_k.group_titles.help` |
| „Documentation“ (`PagesOutline`) | `window.open("https://go.plane.so/p-docs","_blank")` |
| „Contact sales“ (`UserOutline`) | `window.open("mailto:sales@plane.so","_blank")` → **entfällt (ADR-001)** |
| Separator | – |
| „Keyboard shortcuts“ | `toggleShortcutsListModal(true)` (Power-K-Shortcut-Modal, s. 2.9) |
| „What's new?“ | öffnet `ProductUpdatesModal` (s. 2.16.9) |
| „Forum“ | `window.open("https://forum.plane.so","_blank","noopener,noreferrer")` |
| Footer | `PlaneVersionNumber` (`text-11 text-secondary`) |

**User-Menü (`UserMenuRoot`, `apps/web/components/workspace/sidebar/user-menu-root.tsx`)**

| Teil | Detail |
|---|---|
| Trigger | `Avatar size="xs"` (`src=getFileURL(avatar_url)`, Fallback erster Buchstabe `display_name` groß) |
| Popup (`align="end"`, `w-72 p-2 gap-y-3`) | Kopfkarte `h-29 rounded-lg`: `CoverImage` (`showDefaultWhenEmpty`) + Overlay `bg-layer-1/50` + zentriert `Avatar size="xl"`, Name (`first_name last_name`, `text-body-sm-medium`), E-Mail (`text-caption-md-regular`) |
| „Settings“ | `toggleProfileSettingsModal({activeTab:"general", isOpen:true})` → **Profil-Einstellungen als Modal** (s. 2.13) |
| „Preferences“ | `toggleProfileSettingsModal({activeTab:"preferences", isOpen:true})` (Icon ebenfalls `SettingsOutline`) |
| „Sign out“ | `signOut()`, Fehler-Toast wie oben |
| „Enter god mode“ | nur wenn `isUserInstanceAdmin` – in CE fest `false` → nie sichtbar (`GOD_MODE_URL`) |

**Power-K-Suchfeld in der Top-Navigation (`TopNavPowerK`, `apps/web/components/navigation/top-nav-power-k.tsx`)** – Details der Befehle in 2.9.

| Zustand | Maße/Klassen |
|---|---|
| geschlossen | Feld-Wrapper `w-[364px]`, Feld `h-7 rounded-lg border border-subtle-1 bg-layer-2 p-2`; `SearchOutline size-3.5 text-placeholder`; Placeholder „Search commands...“ (hart codiert); Clear-`CloseOutline size-3.5` nur bei Suchtext |
| offen | Wrapper `w-[554px]`, Feld `bg-layer-1`; Panel `absolute -top-[6px] left-1/2 -translate-x-1/2 w-[574px] max-h-[80vh] pt-10 rounded-md border border-subtle bg-surface-1 shadow-lg z-20` (Feld liegt mit `z-30` über dem Panel); Liste `max-h-[60vh] overflow-y-auto px-2 pb-4`; Footer `PowerKModalFooter` |
| Animation | `transition-all duration-300 ease-in-out` (Breite/Opacity) |

### 2.3 Workspace-Sidebar („Projects“-App-Sidebar)

#### 2.3.1 Aufbau von oben nach unten

| # | Bereich | Komponente / Datei | Inhalt | Sichtbarkeit / Rechte |
|---|---|---|---|---|
| 1 | Kopfzeile | `SidebarWrapper` (`apps/web/components/sidebar/sidebar-wrapper.tsx`) | Titel „Projects“ (Prop `title`, `pt-1 text-16 font-medium text-primary`), rechts `IconButton` „Customize navigation“ (`PreferencesOutline`, nur wenn `title === "Projects"`) und `AppSidebarToggleButton` (`LeftSidePaneOutline`) | immer |
| 2 | Quick-Action | `SidebarQuickActions` (`apps/web/components/workspace/sidebar/quick-actions.tsx`) | Button „New work item“ (`sidebar.new_work_item`, `AddWorkItemOutline size-4`, Label `max-w-[145px] truncate text-13 font-medium`), `SidebarAddButton` = `Button variant="secondary" size="lg" stretch="full"` (`apps/web/components/sidebar/add-button.tsx`) → `toggleCreateIssueModal(true)` | **disabled**, wenn `joinedProjectIds.length === 0` oder WS-Rolle nicht Admin/Member |
| 3 | Statische Items | `SidebarMenuItems` (`apps/web/components/workspace/sidebar/sidebar-menu-items.tsx`) | „Home“ (`home.title`, `/`), danach persönliche Items in `sort_order`-Reihenfolge, **nur wenn `enabled`**: „Stickies“ (`/stickies/`), „Your work“ (`/profile/{userId}`), „Drafts“ (`/drafts/`) | Rolle je Item, s. 2.3.2 |
| 4 | Sektion „Workspace“ | `Collapsible placement="sidebar"` in `sidebar-menu-items.tsx`; Zustand `localStorage["is_workspace_menu_open"]` (Default `true`) | „Projects“ (`/projects/`, immer), danach dynamische Items (Views, Analytics, Archives) **nur wenn gepinnt**, sortiert nach `sort_order`; abschließend Button „More“/„Hide“ (`#extended-sidebar-toggle`, `MoreHorizontalOutline`) → `toggleExtendedSidebar()` | s. 2.3.2 |
| 5 | Sektion „Favorites“ | `SidebarFavoritesMenu` (`apps/web/components/workspace/sidebar/favorites/favorites-menu.tsx`) | Ordner + Favoriten (Projekt, Cycle, Module, View, Page), Drag&Drop, Ordner anlegen; Zustand `localStorage["is_favorite_menu_open"]` (Konstante `IS_FAVORITE_MENU_OPEN`, Default `false`) | nur WS-Admin/Member **und** `groupedFavorites` nicht leer (`apps/web/app/(all)/[workspaceSlug]/(projects)/sidebar.tsx`) |
| 6 | Sektion „Projects“ | `SidebarProjectsList` (`apps/web/components/workspace/sidebar/projects-list.tsx`) | Liste der beigetretenen Projekte (`joinedProjectIds`), „+“ (Create project) beim Hover, Lade-Skeleton 4× `28px` bei `loader==="init-loader"`, „More“/„Hide“ bei Projektlimit, „Add project“ bei 0 Projekten | „+“ und „Add project“ nur WS-Admin/Member |
| 7 | Fußzeile | `SidebarWrapper` | `h-12 border-t border-subtle bg-surface-1 p-3`, enthält `WorkspaceEditionBadge` („Community“-Button → Upgrade-Modal) | immer → **entfällt (ADR-001)**; Fußzeile leer lassen oder Versionsanzeige |

Container-Klassen: Wrapper `flex h-full w-full animate-fade-in flex-col`; Kopfbereich `flex flex-col gap-3 px-3`; Scrollbereich `ScrollArea orientation="vertical"` → `flex flex-col gap-3 overflow-x-hidden px-3 pt-3 pb-0.5`.

#### 2.3.2 Navigations-Items (Konstanten `packages/constants/src/workspace.ts`)

| key | Label-Key → EN | href (relativ zu `/${ws}`) | Rollen (WS) | Highlight-Regel | Gruppe | Icon (`getSidebarNavigationItemIcon`, `apps/web/components/workspace/sidebar/helper.tsx`) |
|---|---|---|---|---|---|---|
| `home` | `home.title` → „Home“ | `/` | Admin, Member, Guest | `pathname === url` | statisch (`WORKSPACE_SIDEBAR_STATIC_NAVIGATION_ITEMS_LINKS`) | `HomeOutline` |
| `inbox` | `notification.label` → „Inbox“ | `/notifications/` | Admin, Member, Guest | `includes` | definiert, aber **nicht in der Sidebar gerendert** (Inbox sitzt in der Top-Navigation) | `InboxOutline` |
| `your_work` | `your_work` → „Your work“ | `/profile/` + `{userId}` | Admin, Member | `includes` | persönlich | `YourWorkOutline` |
| `stickies` | `sidebar.stickies` → „Stickies“ | `/stickies/` | Admin, Member, Guest | `includes` | persönlich | `MultipleStickyOutline` |
| `drafts` | `drafts` → „Drafts“ | `/drafts/` | Admin, Member | `includes` | persönlich | `DraftsOutline` |
| `projects` | `projects` → „Projects“ | `/projects/` | Admin, Member, Guest | `pathname === url` | statisch gepinnt (`WORKSPACE_SIDEBAR_STATIC_PINNED_NAVIGATION_ITEMS_LINKS`) | `ProjectsOutline` |
| `views` | `views` → „Views“ | `/workspace-views/all-issues/` | Admin, Member, Guest | `includes` | dynamisch (`WORKSPACE_SIDEBAR_DYNAMIC_NAVIGATION_ITEMS_LINKS`) | `ViewsOutline` |
| `analytics` | `analytics` → „Analytics“ | `/analytics/` | Admin, Member | `includes` | dynamisch | `AnalyticsOutline` |
| `archives` | `archives` → „Archives“ | `/projects/archives/` | Admin, Member | `includes` | dynamisch | `ArchiveOutline` |
| `active_cycles` | – (nur Icon-Mapping + `UpgradeBadge` in `extended-sidebar-item.tsx`) | – | – | – | nicht in den Konstanten der CE; Backend-Key existiert (`WorkspaceUserPreference.UserPreferenceKeys.ACTIVE_CYCLES`, `apps/api/plane/db/models/workspace.py`) | `CyclesOutline` |

Render-Regel `SidebarItemBase` (`apps/web/components/workspace/sidebar/sidebar-item.tsx`): Item wird **nicht** gerendert, wenn die WS-Rolle nicht in `access` ist, oder wenn es nicht gepinnt ist und nicht in der Liste `["home","pi_chat","projects","your_work","stickies","drafts", …additionalStaticItems]` steht. Zeilenlayout: `SidebarNavItem` (`apps/web/components/sidebar/sidebar-navigation.tsx`: `group relative flex w-full cursor-pointer items-center justify-between gap-1.5 rounded-md px-2 py-1 outline-none`; aktiv `!bg-layer-transparent-active text-primary`; inaktiv `text-secondary hover:bg-layer-transparent-hover active:bg-layer-transparent-active`) mit Icon `size-4` + Label `text-13 leading-5 font-medium`, innen `py-[1px]`.

Server-Defaults der Präferenzen (`GET /api/workspaces/{slug}/sidebar-preferences/`, `apps/api/plane/app/views/workspace/user_preference.py`): fehlende Keys werden beim ersten GET angelegt mit `sort_order = 65535 + i*10000` und `is_pinned = true` nur für `drafts`, `your_work`, `stickies`; `views`, `active_cycles`, `analytics`, `archives` starten **ungepinnt**. Antwortformat `{ "<key>": { "is_pinned": bool, "sort_order": float } }`. Client-Fallback ohne Serverdaten: `DEFAULT_PERSONAL_PREFERENCES` = stickies `enabled:false/0`, your_work `true/1`, drafts `true/2`; `DEFAULT_WORKSPACE_PREFERENCES.items = {}` (`packages/types/src/navigation-preferences.ts`).

#### 2.3.3 Extended-Sidebar „More“ (`ExtendedAppSidebar`, `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-sidebar.tsx`)

| Aspekt | Detail | Quelle |
|---|---|---|
| Wrapper | `ExtendedSidebarWrapper`: `shadow-sm absolute z-[21] flex h-full flex-col border-r border-subtle bg-surface-1 p-4 py-2 transition-all duration-300 ease-in-out`, offen `opacity-100`, zu `hidden opacity-0`; `left = localStorage.sidebarWidth ?? 250`, `width = EXTENDED_SIDEBAR_WIDTH` (300) | `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-sidebar-wrapper.tsx` |
| Items | alle dynamischen Items mit Rollenrecht; Sortierung: gepinnte zuerst, dann `sort_order` aufsteigend | `extended-sidebar.tsx` |
| Zeile | `ExtendedSidebarItem`: Drag-Handle links (`absolute -left-3`, nur bei Hover sichtbar, Tooltip „Drag to rearrange“), Link mit Icon+Label, rechts Pin-/Unpin-Icon (`PinOutline`/`UnpinOutline size-3.5`, Tooltip „Pin“/„Unpin“); bei `active_cycles` zusätzlich `UpgradeBadge` | `apps/web/components/workspace/sidebar/extended-sidebar-item.tsx` |
| Aktiv-Regel | exakter Vergleich `itemHref === pathname` (anders als in der Haupt-Sidebar) | `extended-sidebar-item.tsx` |
| Pin | `toggleWorkspaceItem(key, true/false)` → `PATCH /api/workspaces/{ws}/sidebar-preferences/` Body `[{key, is_pinned, sort_order}]` | `apps/web/hooks/use-navigation-preferences.ts` |
| Drag&Drop | `dragInstanceId: "NAVIGATION"`; Drop-Indikator oben (`DRAG_OVER`) bzw. unter letztem Element (`DRAG_BELOW`); neue `sort_order`: Ziel 0 → `sort_order(ziel) − 10000`; Ende → `sort_order(letztes) + 10000`; Mitte → Mittelwert der Nachbarn; → `updateWorkspaceItemSortOrder(key, order)` | `extended-sidebar.tsx` |
| Schließen | Außenklick (ausgenommen Element `#extended-sidebar-toggle`), Einklappen der Haupt-Sidebar, Klick auf Link in der Haupt-Sidebar (`SidebarItemBase.handleLinkClick`) | `extended-sidebar-wrapper.tsx`, `apps/web/hooks/use-extended-sidebar-overview-outside-click.tsx`, `sidebar-item.tsx` |

#### 2.3.4 Dialog „Customize navigation“ (`CustomizeNavigationDialog`, `apps/web/components/navigation/customize-navigation-dialog.tsx`)

| Abschnitt | Elemente | Persistenz |
|---|---|---|
| Kopf | Titel `customize_navigation` = „Customize navigation“; Beschreibung (hart codiert): „Selected items will always stay visible in your sidebar. You can still find the others anytime from the More menu. These changes are personal to you and won't affect anyone else on your workspace.“; Schließen-`IconButton` (`CloseOutline`); `DialogContent size="md"`; Esc/Außenklick schließt | – |
| „Personal“ (`personal`) | `Sortable` (id `personal-enabled-items`) mit Zeilen: Drag-Icon `DragDropOutline size-4 cursor-grab`, `Checkbox` (enabled), Icon, Label: Stickies (`sidebar.stickies`), Your work (`sidebar.your_work`), Drafts (`drafts`); sortiert nach `sort_order` | Checkbox → `togglePersonalItem(key, checked)`; Umsortieren → `updatePersonalItemOrder([{key, sortOrder: index}])` → Bulk-PATCH `sidebar-preferences` (sort_order = **Index 0..n**) |
| „Workspace“ (`common.workspace`) | `Sortable` (id `workspace-pinned-items`): Views, Analytics, Archives (nur mit Rollenrecht), Checkbox = gepinnt | Checkbox → `toggleWorkspaceItem`; Umsortieren → `updateWorkspaceItemOrder` (sort_order = Index) |
| „Projects“ (`projects`) | Radio `navigation-mode`: „Accordion sidebar navigation“ (`accordion_navigation_control`, Hilfstext „Feature tabs will appear as nested items under project and acts as accordion.“) / „Tabbed Navigation“ (`horizontal_navigation_bar`, Hilfstext „Feature tabs will appear as horizontal tabs inside a project.“); Checkbox „Show limited projects on sidebar“; bei aktiv: Zahlenfeld „Enter number of projects“ (`type=number min=1 step=1`), Fehlertext „Minimum value is 1“ | `updateNavigationMode(mode)` → `navigation_control_preference`; Checkbox → `navigation_project_limit = show ? (count‖10) : 0`; Zahl → `navigation_project_limit = max(1, n)` – alles über `updateProjectNavigationPreferences(ws, …)` (Workspace-User-Properties, `GET/PATCH /api/workspaces/{ws}/user-properties/`, s. A08 §3.3) |
| Eingabevalidierung Zahl | Tasten `e`, `E`, `+`, `-`, `.` werden blockiert; Nicht-Ziffern entfernt; leerer Wert speichert nichts; Rahmen `border-danger-strong` wenn `< 1` | – |

Abgeleitete Projektpräferenz (`useProjectNavigationPreferences`): `navigationMode = navigation_control_preference ‖ "ACCORDION"`, `limitedProjectsCount = limit > 0 ? limit : 10`, `showLimitedProjects = limit > 0`; ohne Serverwerte `DEFAULT_PROJECT_PREFERENCES` (`ACCORDION`, `false`, `10`).

#### 2.3.5 Projektliste in der Sidebar

| Element | Detail | Quelle |
|---|---|---|
| Sektionskopf | `Collapsible` mit Trigger „Projects“ (`text-13 font-semibold text-placeholder`), rechts „+“ (`AddOutline`, Tooltip „Create project“) nur bei Hover/Fokus (`group-hover/projects-section`) → lokales `CreateProjectModal` (`setToFavorite=false`) | `projects-list.tsx` |
| Offen-Zustand | lokal `useState(true)`; schreibt `localStorage["isAllProjectsListOpen"]`, wird aber **nicht** zurückgelesen; bei Pfad mit „projects“ automatisch geöffnet | `projects-list.tsx` |
| Scroll-Schatten | `border-t border-strong` wenn `scrollTop > 0` des Containers | `projects-list.tsx` |
| Auto-Scroll beim Ziehen | `autoScrollForElements` (nur `dragInstanceId==="PROJECTS"`, vertikal) | `projects-list.tsx` |
| Limit | `showLimitedProjects` → erste `limitedProjectsCount` Projekte; darunter „More“/„Hide“ (`#extended-project-sidebar-toggle`) → `toggleExtendedProjectSidebar()` | `projects-list.tsx` |
| Leer | WS-Admin/Member und 0 Projekte → Button „Add project“ (`text-13 font-medium text-secondary hover:bg-surface-2 px-2 py-1.5`) → `toggleCreateProjectModal(true)` (globales Modal) | `projects-list.tsx` |
| Projektzeile | `SidebarProjectsListItem`: Wrapper `group/project-item relative flex w-full items-center rounded-md px-2 py-1.5 hover:bg-layer-transparent-hover` (Menü offen `bg-surface-2`; im TABBED-Modus aktuelles Projekt `bg-layer-transparent-active`); Drag-Handle `absolute -left-3` (Tooltip „Drag to rearrange“ bzw. „Join the project to rearrange“ bei `sort_order === null`, dann `cursor-not-allowed opacity-60`); Logo (`Logo size=16`) + Name (`truncate text-13 font-medium text-secondary`); „…“-Menü (Hover); im ACCORDION-Modus Chevron (`ChevronRightOutline size-3.5`, offen `rotate-90`) | `apps/web/components/workspace/sidebar/projects-list-item.tsx` |
| „…“-Menü (Projekt) | „Publish project“ (`ShareAltOutline`, nur PRJ-Admin) → `PublishProjectModal`; „Copy link“ (`LinkOutline`) → kopiert `${ws}/projects/${id}/issues`, Toast success „Link copied“/„Project link copied to clipboard“; „Archives“ (`ArchiveOutline`, nur PRJ-Admin/Member) → `/${ws}/projects/${id}/archives/issues`; „Settings“ (`SettingsOutline`, immer) → `/${ws}/settings/projects/${id}`; „Leave project“ (`LogOutOutline`, nur wenn **nicht** PRJ-Admin/Member, d. h. Guest) → `LeaveProjectModal` | `projects-list-item.tsx` |
| Unterpunkte (ACCORDION) | `ProjectNavigation` eingerückt `pl-6`, vertikale Linie `absolute top-0 bottom-1 left-[15px] w-[1px] bg-layer-3`; Items s. 2.4.1; Label hier `text-11 font-medium`; Intake mit Zähler `project.intake_count` (nur > 0) | `apps/web/components/workspace/sidebar/project-navigation.tsx` |
| Offen-Zustand je Projekt | `commandPalette.getIsProjectListOpen(projectId)` / `toggleProjectListOpen(projectId, value)` (Store, nicht persistiert); aktuelles Projekt (`URLProjectId`) wird automatisch geöffnet und nach 200 ms `scrollIntoView({behavior:"smooth", block:"center", scrollMode:"if-needed"})` | `projects-list-item.tsx` |
| Drag-Vorschau | eigenes Native-Preview: `flex items-center rounded-sm bg-surface-1 p-1 pr-2 text-13` mit Logo + Name | `projects-list-item.tsx` |
| Nach Drop | Highlight der Zeile `highlightIssueOnDrop("sidebar-${sourceId}-${projectListType}")` (CSS-Klasse `HIGHLIGHT_CLASS`, entfernt bei Außenklick) | `apps/web/components/issues/issue-layouts/utils.tsx` |

#### 2.3.6 Extended-Projekt-Sidebar (`ExtendedProjectSidebar`, `apps/web/app/(all)/[workspaceSlug]/(projects)/extended-project-sidebar.tsx`)

| Element | Detail |
|---|---|
| Wrapper | gleicher `ExtendedSidebarWrapper` (`className="px-0"`, ausgenommenes Element `#extended-project-sidebar-toggle`) |
| Kopf (sticky `top-4 px-4`) | „Projects“ (`py-1.5 text-13 font-semibold text-tertiary`, hart codiert), „+“ (`AddOutline size-3`, Tooltip „Create project“, nur WS-Admin/Member) → `CreateProjectModal`; Suchfeld `InputGroup size="lg"` mit `SearchOutline`, Placeholder `search`, `autoFocus` |
| Filter | Name enthält Suchbegriff (case-insensitive) **oder** Identifier enthält Suchbegriff (case-sensitive) |
| Leer | `EmptyStateCompact` `assetKey="search"` (`common_empty_state.search.title/description`), `mt-4 p-10` |
| Liste | `vertical-scrollbar mt-4 scrollbar-sm flex flex-grow flex-col gap-0.5 overflow-y-auto pr-2 pl-9`; `SidebarProjectsListItem renderInExtendedSidebar` (Drag-Handle immer sichtbar) |
| Drag&Drop | wie Haupt-Sidebar (`orderJoinedProjects`) |

#### 2.3.7 Favoriten

| Element | Detail | Quelle |
|---|---|---|
| Sektionskopf | Trigger „Favorites“ (dient zugleich als Drop-Ziel, beim Darüberziehen `bg-layer-1 opacity-60`), rechts beim Hover „Create folder“ (`CreateFolderOutline`) → Inline-Formular, öffnet Sektion falls zu | `favorites-menu.tsx` |
| Leer (bei geöffneter Sektion) | „No favorites yet“ (`px-8 py-1.5 text-11 font-medium text-placeholder`) – praktisch unerreichbar, da Sektion bei leerer Liste ausgeblendet ist | `favorites-menu.tsx`, `(projects)/sidebar.tsx` |
| Sortierung | Wurzelebene: `orderBy(groupedFavorites, "sequence", "desc")`, nur Einträge ohne `parent`; Kinder eines Ordners ebenfalls `sequence desc` | `favorites-menu.tsx`, `favorite-folder.tsx` |
| Ordnerzeile | `FavoriteFolder`: `FavoriteFolderIcon` (`size-5`), Name `text-13 font-medium text-secondary`, Tooltip mit Name (`side="right" sideOffset=40`), „…“-Menü: „Remove from favorites“ (`StarFilled text-yellow-500`), „Rename Folder“ (hart codiert, Icon `DraftsOutline`); Chevron (`size-3`, offen `rotate-90`); Kinder werden beim ersten Rendern nachgeladen, wenn `children === undefined` → `GET /api/workspaces/{ws}/user-favorites/{id}/group/`; Aufklappen nur lokal (`useState(false)`), Animation `animate-fade-in` | `favorite-folder.tsx` |
| Favoritenzeile | `FavoriteRoot` → `FavoriteItemWrapper` (`group/project-item … px-2 py-1.5 hover:bg-layer-transparent-hover`), `FavoriteItemDragHandle` (Tooltip „Drag to rearrange“/„Join the project to rearrange“ hart codiert), `FavoriteItemTitle` (Link, Tooltip, Icon `size-5`, Titel `text-13 leading-5 font-medium`; mobil → Sidebar einklappen), `FavoriteItemQuickAction` („Remove from favorites“) | `favorite-items/root.tsx`, `favorite-items/common/*` |
| Icons | `project` `ProjectsOutline`, `page` `PagesOutline`, `view` `ViewsOutline`, `module` `ModuleOutline`, `cycle` `CyclesOutline`, `folder` `FavoriteFolderIcon`, Fallback `PagesOutline`; bei Hover Typ-Icon, sonst Logo (`logo_props.in_use`: Projekt `material`, sonst `lucide`) | `favorite-items/common/favorite-item-icon.tsx` |
| Titel/Links | `apps/web/hooks/use-favorite-item-details.tsx` + `FAVORITE_ITEM_LINKS` (`packages/constants/src/sidebar-favorites.ts`): project → `/${ws}/projects/{project_id}/issues`; cycle → `…/cycles/{entity_identifier}`; module → `…/modules/{id}`; view → `…/views/{id}`; page → `…/pages/{id}`; unbekannter Typ → `/${ws}` + `console.error`; Titel aus Store (Projekt/Page via `getPageName`/View/Cycle/Module) sonst `entity_data.name ‖ name` | `favorite-items/common/helper.tsx` |
| Neuer/umbenannter Ordner | `NewFavoriteFolder`: `FavoriteFolderIcon size-4` + `Input size="2xl"` (Placeholder „New folder“, Autofokus); Enter speichert; Außenklick bricht ab | `new-fav-folder.tsx` |

### 2.4 Seiten-Header, Breadcrumbs und Projekt-Navigation

#### 2.4.1 Projekt-Feature-Navigation (gemeinsame Item-Definition)

Identische Definition in `apps/web/components/navigation/use-navigation-items.ts` (Tab-Navigation, Header-Switcher, Sidebar-Default-Tab) und `apps/web/components/workspace/sidebar/project-navigation.tsx` (Accordion-Unterpunkte; zusätzlich Erweiterungspunkt `additionalNavigationItems`).

| sortOrder | key | i18n-Key → EN | href | Icon | Rollen (Projekt) | `shouldRender` |
|---|---|---|---|---|---|---|
| 1 | `work_items` | `sidebar.work_items` → „Work items“ | `/${ws}/projects/${pid}/issues` | `WorkItemsOutline` | Admin, Member, Guest | immer |
| 2 | `cycles` | `sidebar.cycles` → „Cycles“ | `…/cycles` | `CyclesOutline` | Admin, Member | `project.cycle_view` |
| 3 | `modules` | `sidebar.modules` → „Modules“ | `…/modules` | `ModuleOutline` | Admin, Member | `project.module_view` |
| 4 | `views` | `sidebar.views` → „Views“ | `…/views` | `ViewsOutline` | Admin, Member, Guest | `project.issue_views_view` |
| 5 | `pages` | `sidebar.pages` → „Pages“ | `…/pages` | `PagesOutline` | Admin, Member, Guest | `project.page_view` |
| 6 | `intake` | `sidebar.intake` → „Intake“ | `…/intake` | `IntakeOutline` (Strich `stroke-1`, andere `stroke-[1.5]`) | Admin, Member, Guest | `project.inbox_view` |

`getTabUrl` kennt zusätzlich `overview` (`…/overview`) und `epics` (`…/epics`) – Routen existieren in der CE nicht (EE-Features „Project Overview“, „Epics“, s. A08 §2.16); unbekannter Key → `…/issues` (`apps/web/components/navigation/tab-navigation-utils.ts`).

#### 2.4.2 Tab-Navigation (Navigation-Modus `TABBED`)

| Element | Detail | Quelle |
|---|---|---|
| Einbindung | Nur bei `navigationMode === "TABBED"`: eigene Zeile über dem Seiten-Header jeder Projektseite (`Row h-header border-b border-subtle bg-surface-1 z-20`; links `AppSidebarToggleButton`, wenn Sidebar eingeklappt; `Header` mit `pl-1.5` bei offener Sidebar) – ebenso auf `/${ws}/browse/:workItem` mit `projectId = issue.project_id` | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/layout.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/browse/[workItem]/header.tsx` |
| Aufbau | `ProjectHeader` (Projekt-Switcher) + `ProjectActionsMenu` („…“), senkrechter Trenner `h-5 w-1 border-l border-subtle`, dann `Tabs variant="underline"` mit `TabsList` (`-mb-3`) | `apps/web/components/navigation/tab-navigation-root.tsx` |
| Projekt-Switcher | `Select` (propel) mit Optionen = alle beigetretenen Projekte (`value=id`, Label = Name, Icon `SwitcherIcon` mit `logo_props`, Fallback `ProjectsOutline`, Typ `material`); Trigger `variant="select-ghost-md"` mit `ProjectHeaderButton` (Logo in `size-7 rounded-md bg-layer-1`, Name `truncate px-2 text-14 font-medium text-secondary`, `max-w-48`, Tooltip mit vollem Namen); Placeholder `common.projects`; Wechsel → `router.push(getTabUrl(ws, neueId, validierterDefaultTab))` | `apps/web/components/navigation/project-header.tsx`, `project-header-button.tsx` |
| „…“-Menü | wie Sidebar-Projektmenü (Publish nur PRJ-Admin; Copy link; Archives nur Admin/Member; Settings; Leave project nur Guest). **Unterschied:** „Copy link“ kopiert `activeItem.href` (aktueller Tab) bzw. `…/issues`, Toast `type:"info"` „Link copied!“/„Project link copied to clipboard.“, Fehler „Copy failed“/„We couldn't copy the link. Please try again.“ (hart codiert) | `apps/web/components/navigation/project-actions-menu.tsx`, `use-project-actions.ts` |
| Tab | `UnderlineTabLink` (propel `Tab` mit `render=<Link>`), Label `t(i18n_key)`; aktiver Tab = `Tabs value=activeItem.key` (Underline-Indikator von propel) | `underline-tab-link.tsx`, `tab-navigation-visible-item.tsx` |
| Kontextmenü eines Tabs (Rechtsklick) | „Set as default“/„Clear default“ (`DefaultTabOutline`); „Hide in more menu“ (`UnpinOutline`) | `tab-navigation-visible-item.tsx` |
| Overflow-Menü | „…“-Button (`MoreHorizontalOutline h-4 w-4`, `aria_labels.common.more_actions`); Einträge = per Platz verdrängte Tabs + vom Nutzer versteckte Tabs; je Eintrag beim Hover: Pin-Icon „Show“ (nur bei versteckten) und Default-Icon (Tooltip „Set as default“/„Clear default“; beim Default-Tab dauerhaft sichtbar) | `tab-navigation-overflow-menu.tsx` |
| Aktiv-Regel | `pathname === href` oder `pathname.startsWith(href + "/")`, plus Work-Item-/Epic-Regel wie in 3.3 | `use-active-tab.ts` |
| Persistenz | Projekt-User-Properties: `preferences.navigation.default_tab` (Default `work_items`), `preferences.navigation.hide_in_more_menu` (Array); Update via `updateProjectUserProperties(ws, pid, {preferences:{pages: bisher‖{block_display:false}, navigation:{default_tab, hide_in_more_menu}}})` (Endpunkt `…/projects/{pid}/user-properties/`, A08 §2.7.2). Die `localStorage`-Funktionen `getTabPreferences`/`saveTabPreferences` (`plane_tab_prefs`) sind **ungenutzt** | `use-tab-preferences.ts`, `tab-navigation-utils.ts` |
| Toasts | Default gesetzt: success „Success!“/„Default tab updated successfully.“; Fehler „Error!“/„Failed to update default tab. Please try again later.“; Hide-/Show-Fehler „Failed to hide tab…“ bzw. „Something went wrong…“ (werden wegen fehlendem `await` nie ausgelöst) | `use-tab-preferences.ts` |

#### 2.4.3 Seiten-Header-Bausteine

| Baustein | Detail | Quelle |
|---|---|---|
| `AppHeader` | Wrapper `z-[18]`; `Row` (`@plane/blocks/layout`) `flex h-11 w-full items-center gap-2 border-b border-subtle bg-surface-1`; Inhalt `ExtendedAppHeader`; optional `mobileHeader` darunter | `apps/web/components/core/app-header.tsx` |
| `ExtendedAppHeader` | Sidebar-Toggle (s. 3.2) + `div.w-full` mit Header | `apps/web/components/common/extended-app-header.tsx` |
| `ContentWrapper` | `h-full w-full overflow-hidden` → innen `relative h-full w-full overflow-x-hidden overflow-y-scroll` | `apps/web/components/core/content-wrapper.tsx` |
| `PageHead` | setzt `document.title` nur wenn `title` gesetzt (kein Zurücksetzen beim Unmount) | `apps/web/components/core/page-title.tsx` |
| `SidebarHamburgerToggle` | `size-7 rounded-sm bg-surface-2 hover:bg-layer-1`, Icon `RightSidePaneOutline size-3.5` → `toggleSidebar()` (verwendet in Mobile-Headern) | `apps/web/components/core/sidebar/sidebar-menu-hamburger-toggle.tsx` |
| `BreadcrumbLink` | Breadcrumb-Element (`@plane/blocks/breadcrumb`): Icon in `Breadcrumbs.Icon`, Label `line-clamp-1 max-w-[150px] truncate`, Typ `link` bei `href`, sonst `text`; Tooltip mit Label (auf Mobile aus); Link mit Fokus-Outline `focus-visible:outline-2 -outline-offset-2 outline-accent-strong` | `apps/web/components/common/breadcrumb-link.tsx` |
| `ProjectBreadcrumb` | `Breadcrumbs.Item showSeparator={false}` mit `BreadcrumbNavigationSelect`: Auswahl aller beigetretenen Projekte (`SwitcherLabel`), Auswahl → `/${ws}/projects/{id}/issues`; Klick auf aktuelles Projekt → `handleOnClick` oder `/${ws}/projects/{id}/issues/`; Icon `Logo size=14`; Texte `common.project`, `common.search.label`, `common.search.no_matches_found` | `apps/web/components/breadcrumbs/project.tsx` |
| `CommonProjectBreadcrumbs` | rendert `ProjectBreadcrumb` **nur** im ACCORDION-Modus (im TABBED-Modus übernimmt die Tab-Zeile den Projektnamen) | `apps/web/components/breadcrumbs/common.tsx` |
| `useProjectCrumbProps` | `{crumbLabel: project.name, crumbHref: /${ws}/projects/${pid}/issues/}` für das Zusammenklappen langer Breadcrumbs | `apps/web/components/breadcrumbs/use-project-crumb-props.ts` |
| Verwender | Header der Projekt-Unterseiten Cycles (Liste/Detail), Modules (Liste/Detail), Views (Liste/Detail), Pages (Liste/Detail), Archives (`CommonProjectBreadcrumbs`); archiviertes Work Item (`ProjectBreadcrumb` direkt) | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(detail)/[projectId]/**/header.tsx` |
| `WorkspaceDashboardHeader` | Breadcrumb „Home“ (`HomeOutline h-4 w-4 text-tertiary`); rechts „Manage widgets“ (`WidgetOutline`; < md als `IconButton`, ≥ md als `Button variant="secondary" size="md"`) → `toggleWidgetSettings(true)` | `apps/web/app/(all)/[workspaceSlug]/(projects)/header.tsx` |

### 2.5 Workspace-Home (Dashboard) und Widgets

Route `/:workspaceSlug` (`apps/web/app/(all)/[workspaceSlug]/(projects)/page.tsx`): `AppHeader` mit `WorkspaceDashboardHeader` (2.4.3), `ContentWrapper`, `PageHead` „`{Workspace} - Home`“, `WorkspaceHomeView`.

#### 2.5.1 Seitenaufbau (`WorkspaceHomeView`, `apps/web/components/home/root.tsx`)

| Teil | Detail |
|---|---|
| Produkt-Tour | Wenn `currentUserProfile.is_tour_completed === false`: Vollbild-Overlay `fixed top-0 left-0 z-20 grid h-full w-full place-items-center overflow-y-auto bg-backdrop` mit `TourRoot` (2.15.4); Abschluss → `updateTourCompleted()` |
| Peek | `HomePeekOverviewsRoot` (`apps/web/components/issues/peek-overview/peek-overviews.tsx`, A09) für Work-Item-/Epic-Peek aus Recents |
| Inhalt | `ContentWrapper className="mx-auto scrollbar-hide gap-6 bg-surface-1 px-page-x"` → `div.mx-auto.w-full.max-w-[800px]` mit `UserGreetingsView` und `DashboardWidgets` |
| Daten | SWR `HOME_DASHBOARD_WIDGETS_${ws}` → `fetchWidgets` = `GET /api/workspaces/{ws}/home-preferences/` (`revalidateIfStale:true, revalidateOnFocus:false, revalidateOnReconnect:true`) |

#### 2.5.2 Begrüßung (`UserGreetingsView`, `apps/web/components/home/user-greetings.tsx`; identische Kopie `apps/web/components/user/user-greetings.tsx`)

| Element | Detail |
|---|---|
| Überschrift | `h2.text-center.text-20.font-semibold`: `t("good")` + `t(greeting)` + „, “ + `first_name last_name` → z. B. „Good morning, Max Mustermann“ |
| Tageszeit | Stunde (Browser-Zeitzone, `Intl.DateTimeFormat("en-US",{hour12:false,hour:"numeric"})`): < 12 `morning`, < 18 `afternoon`, sonst `evening` |
| Unterzeile | `h5.flex.items-center.gap-2.font-medium.text-placeholder`: Emoji (🌤️ morning, 🌥️ afternoon, 🌙️ evening) + „`{Wochentag}, {Mon} {Tag} {HH:MM}`“; Wochentag/Datum in Browser-Zeit, Uhrzeit in `user.user_timezone` (24 h); Aktualisierung über `useCurrentTime` |
| Wrapper | `my-6 flex flex-col items-center` |

#### 2.5.3 Widget-Container (`DashboardWidgets`, `apps/web/components/home/home-dashboard-widgets.tsx`)

| Widget-Key (`THomeWidgetKeys`) | Komponente | Titel-Key → EN | in CE aktiv |
|---|---|---|---|
| `quick_links` | `DashboardQuickLinks` | `home.quick_links.title_plural` → „Quicklinks“ | ja |
| `recents` | `RecentActivityWidget` | `home.recents.title` → „Recents“ | ja |
| `my_stickies` | `StickiesWidget` | `stickies.title` → „Your stickies“ | ja |
| `new_at_plane` | `null` | `home.new_at_plane.title` → „New at Plane“ | nein (Server liefert den Key nicht) |
| `quick_tutorial` | `null` | `home.quick_tutorial.title` → „Quick tutorial“ | nein |

| Zustand | Darstellung |
|---|---|
| Laden (`home.loading` oder `project.loader !== "loaded"`) | `HomeLoader`: 3 Blöcke je Titel-Skeleton `20px×100px` + Fläche `h-[110px]` (`apps/web/components/home/widgets/loaders/home-loader.tsx`) |
| Normal | `flex flex-col gap-7`; zuerst `NoProjectsEmptyState` (Quickstart-Guide, außer im Pfad `/${ws}/pages`), dann je aktiviertes Widget in `orderedWidgets` (sortiert `sort_order` **absteigend**) ein `div.py-4` |
| Alle Widgets aus | `SimpleEmptyState` „It's Quiet Without Widgets, Turn Them On“ / „It looks like all your widgets are turned off. Enable them now to enhance your experience!“, Bild `@/app/assets/empty-state/dashboard/widgets-light\|dark.webp` je `resolvedTheme` |
| Server-Defaults | `GET home-preferences` legt fehlende Keys `quick_links`, `recents`, `my_stickies` an (`is_enabled=true`, `sort_order = 1000 − i` → 999/998/997); Antwort `[{key, is_enabled, config, sort_order}]` (`apps/api/plane/app/views/workspace/home.py`) |

#### 2.5.4 Dialog „Manage widgets“ (`ManageWidgetsModal`, `apps/web/components/home/widgets/manage/*`)

| Element | Detail |
|---|---|
| Dialog | `DialogContent size="xs"`, Titel „Manage widgets“, Esc/Außenklick schließt (`toggleWidgetSettings(false)`) |
| Liste (`WidgetList`, `my-4`) | je Widget in `orderedWidgets`: Zeile `group/widget-item relative flex items-center justify-between rounded-sm px-2 py-2 text-13 font-medium hover:bg-layer-1` mit `DragHandle` (`mr-2 cursor-grab`), Titel `t(title,{count:1})` (→ „Quicklink“ für Quick Links, „Recents“, „Your stickies“), `Switch size="sm"` |
| Umschalten | `toggleWidget(ws, key, enabled)` → `PATCH /api/workspaces/{ws}/home-preferences/{key}/ {is_enabled}`; Store erst **nach** Erfolg aktualisiert, Fehler nur `console.error` + throw (kein Toast) |
| Umsortieren | Drag&Drop (pragmatic-dnd, `make-child` blockiert, `reorder-below` nur beim letzten); Sequenz: Basis 10000, `reorder-above` → Mittelwert mit Vorgänger bzw. `Ziel + 10000`, sonst `Ziel − 10000`; **optimistisch**, Revert bei Fehler; `PATCH {sort_order}`; Toast success „Widget reordered successfully.“ / error „Error occurred while reordering widget.“ |
| Drag-Vorschau | `rounded-sm bg-surface-1 p-1 pr-2 text-13` mit dem **Key** (nicht dem Titel) |

#### 2.5.5 Quickstart-Guide (`NoProjectsEmptyState`, `apps/web/components/home/widgets/empty-states/no-projects.tsx`)

Sichtbar, solange `localStorage["quickstart-guide-${ws}"].hide !== true` **und nicht** (≥ 1 beigetretenes Projekt **und** `total_members ≥ 2`). Kopf: „Your quickstart guide“ (`text-14 font-semibold text-tertiary`) + Button „Not right now“ (`CloseOutline`) → `hide: true`. Raster `grid grid-cols-1 gap-4 md:grid-cols-2`; Karte `flex flex-col rounded-xl border border-subtle bg-layer-2 p-4`; Icon-Kreis `size-9 rounded-full` (offen `bg-accent-primary/10 text-accent-primary`, erledigt `bg-surface-2 text-placeholder`); erledigt → grüner Haken-Kreis `bg-[#17a34a] p-1` mit `TickOutline size-3`.

| id | Titel / Beschreibung (EN) | CTA | erledigt wenn | CTA sichtbar wenn |
|---|---|---|---|---|
| `create-project` | „Create a project“ / „Most things start with a project in Plane.“ | Button „Get started“ → `toggleCreateProjectModal(true)` | `joinedProjectIds.length > 0` | WS-Admin/Member |
| `invite-team` | „Invite your team“ / „Build, ship, and manage with coworkers.“ | Link „Get them in“ → `/${ws}/settings/members`, setzt `visited_members: true` | `total_members ≥ 2` | WS-Admin |
| `configure-workspace` | „Set up your workspace.“ / „Turn features on or off or go beyond that.“ | Link „Configure this workspace“ → relativer Link `settings` (ergibt `/${ws}/settings`), setzt `visited_workspace: true` | `visited_workspace` | WS-Admin |
| `personalize-account` | „Make Plane yours.“ / „Choose your picture, colors, and more.“ | Link „Personalize now“ → `/settings/profile/general`, setzt `visited_profile: true` | `visited_profile` | immer |

Icon der 4. Karte: Avatar-Bild (Link auf `/${ws}/profile/{userId}`) bzw. Initiale auf `bg-[#028375]`.

#### 2.5.6 Quick Links (`DashboardQuickLinks`, `apps/web/components/home/widgets/links/*`)

| Element | Detail |
|---|---|
| Kopf | „Quicklinks“ + Button „Add quick Link“ (`AddOutline size-4`, `text-13 font-medium text-accent-primary`) → `toggleLinkModal(true)`, `setLinkData(undefined)` |
| Daten | SWR `HOME_LINKS_${ws}` → `GET /api/workspaces/{ws}/quick-links/` (keine Revalidierung) |
| Liste | `ContentOverflowWrapper maxHeight=150` (Show all/Show less); `flex flex-wrap gap-2`; laden → `QuickLinksWidgetLoader` (4× `56×230px`); leer → `LinksEmptyState` (`EmptyStateCompact assetKey="link"`, Titel `workspace_empty_state.home_widget_quick_links.title`, Box `rounded-lg bg-layer-1 py-10`) |
| Kachel (`LinkItemBlock`) | `group flex h-[56px] w-[230px] items-center gap-4 rounded-md border-[0.5px] border-subtle bg-surface-1 pr-4`; Icon nach URL (`getIconForLink`) in `size-8 rounded-sm bg-surface-2 p-2`; Titel (`title ‖ url`, `text-13 font-medium truncate`); „vor X“ (`calculateTimeAgo(created_at)`, `text-11 text-placeholder`); Klick → `window.open(url,"_blank","noopener,noreferrer")`; „⋮“-Menü (`MoreVerticalOutline`, nur bei Hover/Fokus/offenem Popup) |
| Menü | „Edit“ (`EditOutline`) → Modal mit Daten; „Open in new tab“ (`NewTabOutline`); „Copy link“ (`LinkOutline`) → Toast „Link copied“/„View link copied to clipboard.“; „Delete“ (`DeleteOutline`) → **sofortiges Löschen ohne Rückfrage** |
| Modal (`LinkCreateUpdateModal`, `DialogContent size="md"`) | Titel „Add Quicklink“/„Update Quicklink“; Feld „URL“ (Pflicht, Hinweis „required“, Placeholder „Type or paste a URL“, Fehler „URL is invalid“ nur bei leer); Feld „Display title“ (optional, Placeholder „What you'd like to see this link as“); Buttons „Cancel“ (Key `Cancel`) und „Add Quicklink“/„Adding Quicklink“/„Update Quicklink“/„Updating Quicklink“; URL ohne `http`-Präfix → `http://` vorangestellt |
| Operationen | `POST/PATCH/DELETE /api/workspaces/{ws}/quick-links/[{id}/]`; Toasts „Link created/updated/removed“ bzw. Fehlertext aus `error.data.error` oder „Link not created/updated/removed“; beim Entfernen ist der Toast-Titel versehentlich die Message („The link has been successfully removed“) |

#### 2.5.7 Recents (`RecentActivityWidget`, `apps/web/components/home/widgets/recents/*`)

| Element | Detail |
|---|---|
| Filter | Pill-Dropdown (`Pill size="md" variant="outline"`, `ChevronDownOutline`): „All“ (`all item`), „Work items“ (`issue`), „Pages“ (`page`), „Projects“ (`project`) |
| Daten | SWR `WORKSPACE_RECENT_ACTIVITY_${ws}_${filter}` → `GET /api/workspaces/{ws}/recent-visits/?entity_name=<filter>` (bei „All“ ohne Parameter), keine Revalidierung |
| Container | `ContentOverflowWrapper maxHeight=415`, `min-h-[250px]`; laden → 5 Skeleton-Zeilen (`32×32` + `70%`-Balken); Einträge ohne `entity_data` werden übersprungen |
| Leer | `RecentsEmptyState` je Filter: project → `assetKey="project"` „Your recent projects will appear here once you visit one.“; page → `note` „Your recent pages …“; issue → `work-item` „Your recent work items …“; sonst „You don't have any recents yet.“ |
| Zeile (`ListItem`, `apps/web/components/core/list/list-item.tsx`) | `className="my-auto border-none !px-2 py-3"`; rechts „vor X“ (`calculateTimeAgo(visited_at)`, `text-11 font-medium text-placeholder`) |
| Work Item (`RecentIssue`) | Präfix: mit `type` → `IssueIdentifier size="lg" variant="tertiary"`, sonst Kachel `size-8 rounded-sm bg-layer-2` mit `WorkItemsOutline` + „`PROJ-123`“; Quick-Elemente: State-Icon (Tooltip „State: {name}“), Priority-Icon (Tooltip „Priority: {priority}“), Assignee-Avatare (`MemberSelect variant="avatar-group-sm" disabled`); Klick → **Peek** (`setPeekIssue` bzw. Epic-Peek), Link-Ziel `generateWorkItemLink` |
| Page (`RecentPage`) | Kachel mit Page-Logo (`lucide`) oder `PagesOutline`, Projekt-Identifier; rechts Avatar des Owners; Klick → `/${ws}/projects/{pid}/pages/{id}` bzw. `/${ws}/pages/{id}` (Workspace-Page, Route in CE nicht vorhanden) |
| Projekt (`RecentProject`) | Kachel mit Projekt-Logo, Identifier; rechts Mitglieder-Avatare; Klick → `/${ws}/projects/{id}/issues` |

#### 2.5.8 Stickies-Widget (`StickiesWidget`, `apps/web/components/stickies/widget.tsx`)

Kopf „Your stickies“ + `StickySearch` + Button „Add sticky“ (`text-accent-primary`, Spinner `size-4 animate-spin border-2 border-accent-strong border-t-transparent` während `creatingSticky`, dann disabled); Inhalt `StickiesTruncated` (2.6) in `-mx-2`.

### 2.6 Stickies (Seite `/:ws/stickies`, Widget, Modal)

| Komponente | Datei | Zweck / Darstellung |
|---|---|---|
| `WorkspaceStickyHeader` | `apps/web/app/(all)/[workspaceSlug]/(projects)/stickies/header.tsx` | Breadcrumb „Stickies“ (hart codiert, `MultipleStickyOutline size-5 rotate-90`), rechts `StickySearch` + `Button variant="primary" size="md"` „Add sticky“ (`loading={creatingSticky}`) |
| Seite | `.../stickies/page.tsx`, `layout.tsx` | `PageHead` „Your stickies“, `StickiesInfinite` |
| `StickiesInfinite` | `apps/web/components/stickies/layout/stickies-infinite.tsx` | SWR `WORKSPACE_STICKIES_${ws}` → erste Seite; Endlos-Scroll via `useIntersectionObserver`: Platzhalter-Element (`min-h-[300px]` Skeleton) nur wenn `next_page_results` und ≥ `STICKIES_PER_PAGE` (30) geladen |
| `StickiesTruncated` | `layout/stickies-truncated.tsx` | Für Widget und Modal: `ContentOverflowWrapper maxHeight=620` mit eigenem Button-Link „Show all“ → `/${ws}/stickies` (schließt Modal) |
| `StickiesLayout` | `layout/stickies-list.tsx` | misst Containerbreite (ResizeObserver) → Spalten: < 640 → 2, < 850 → 3, < 1024 → 4, < 1280 → 5, sonst 6 (ohne Messung 4) |
| `StickiesList` | `layout/stickies-list.tsx` | `react-masonry-component` (`Masonry elementType="div"`), Element-Breite `100/Spalten %`; Ladezustand `StickiesLoader` (4 Skeleton-Karten im 4er-Grid); leer: auf Stickies-Seite ohne Suche `DetailedEmptyState` (Titel „Stickies are quick notes and to-dos you take down on the fly.“, Beschreibung „Capture your thoughts…“, Button „Add sticky“ mit `AddOutline`, disabled ohne WS-Rolle), mit Suche `SimpleEmptyState` „That doesn't match any of your stickies.“; außerhalb der Seite `StickiesEmptyState` (`assetKey="note"`, „Jot down an idea, capture an aha, or record a brainwave. Add a sticky to get started.“). Bilder `@/app/assets/empty-state/stickies/stickies-light\|dark.webp`, `stickies-search-light\|dark.webp` |
| `StickyDNDWrapper` | `layout/sticky-dnd-wrapper.tsx` | Zelle `box-border flex flex-col p-[8px]`; Drag&Drop **nur auf der Stickies-Seite** (`pathname.includes("stickies")`); Vorschau = verkleinertes Sticky (`scale-50`, `w-[290px]`, Offset `x:-200px`); Drop-Indikatoren auskommentiert |
| `StickyNote` | `sticky/root.tsx` | Karte `group/sticky flex h-fit w-full flex-col overflow-y-scroll rounded-sm`, Hintergrund = Farbe aus `STICKY_COLORS_LIST`; optional Schließen-Button (`ArrowCollapseOutline size-4`, `p-2.5`) wenn `onClose`; Inhalt `StickyInput` |
| `StickyInput` | `sticky/inputs.tsx` | `StickyEditor` (`apps/web/components/editor/sticky-editor/editor.tsx`, A12): Placeholder „Click to type here“ (nur bei leerem Inhalt), Container `vertical-scrollbar scrollbar-sm max-h-[540px] min-h-[256px] w-full overflow-y-scroll p-4 text-14` (auf Stickies-Seite `max-h-[588px]`), kein Datei-Upload (`uploadFile → ""`), Toolbar mit Farbwahl (`ColorPalette` „Background colors“) und Löschen |
| `StickyDeleteModal` | `delete-modal.tsx` | `ConfirmDialog` „Delete sticky“ / „Are you sure you want to delete this sticky?“; Fehler-Toast „Sticky not removed“ |
| `StickySearch` | `modal/search.tsx` | Lupe (`IconButton ghost md`) klappt Feld auf (`w-30 md:w-64 border-subtle px-2.5 py-1.5`, Animation `transition-[width] ease-linear`), Placeholder „Search by title“; Eingabe → `updateSearchQuery` + Debounce 500 ms → `fetchWorkspaceStickies` (Query-Param `query`); Esc: Text vorhanden → leeren + neu laden, sonst zuklappen; „×“ leert, klappt zu und lädt neu; Außenklick klappt nur bei leerem Text zu |
| `AllStickiesModal` / `Stickies` | `modal/index.tsx`, `modal/stickies.tsx` | `DialogContent size="xl"` (aria-label „Your stickies“), Inhalt `min-h-[620px] p-6 pb-0`: Kopf mit `MultipleStickyOutline size-5 rotate-90` + „Your stickies“ (hart codiert, `text-18 font-medium`), Suche, „Add sticky“ (hart codiert), Schließen-`CloseOutline`; Liste `max-h-[625px] overflow-scroll` mit `StickiesTruncated`. Geöffnet über `commandPalette.allStickiesModal` (`toggleAllStickiesModal`) – **einziger Aufrufer ist die tote `StickyActionBar`**, im CE also nicht erreichbar (`apps/web/components/stickies/action-bar.tsx`) |
| `StickyActionBar` | `action-bar.tsx` | Schwebende Aktionsleiste (Expand-Button, „All stickies“, Vorschau des letzten Stickys als `PreviewCard`, „Add sticky“) – **nirgends eingebunden (toter Code)** |
| `StickyItemDragHandle` | `sticky/sticky-item-drag-handle.tsx` | Drag-Handle `absolute top-3 left-1/2 rotate-90` – nur in auskommentiertem Code referenziert |

Farben (`STICKY_COLORS_LIST`, `apps/web/components/editor/sticky-editor/color-palette.tsx`): `gray`, `peach`, `pink`, `orange`, `green`, `light-blue`, `dark-blue`, `purple` → `var(--editor-colors-<key>-background)` (A13a §2.19). Neues Sticky erhält eine **zufällige** Farbe (`getRandomStickyColor`).

Endpunkte (`apps/web/services/sticky.service.ts`): `GET /api/workspaces/{ws}/stickies/?cursor=&per_page=30&query=`, `GET …/stickies/{id}` (ohne Slash, Interceptor ergänzt), `POST …/stickies/`, `PATCH …/stickies/{id}/`, `DELETE …/stickies/{id}/`. Store `apps/web/store/sticky/sticky.store.ts`.

### 2.7 Benachrichtigungs-Inbox (`/:ws/notifications`)

Layout `apps/web/app/(all)/[workspaceSlug]/(projects)/notifications/layout.tsx`: `relative flex h-full w-full items-center overflow-hidden` → links `NotificationsSidebarRoot`, rechts Detailbereich (`NotificationsRoot`). Seitentitel `notification.page_label` = „`{workspace} - Inbox`“. Die App-Sidebar ist auf diesem Pfad ausgeblendet (3.2).

#### 2.7.1 Linke Spalte (`NotificationsSidebarRoot`, `apps/web/components/workspace-notifications/sidebar/root.tsx`)

| Teil | Detail |
|---|---|
| Breite | `md:w-3/12`; mobil `w-full` bzw. `w-0`, sobald eine Benachrichtigung gewählt ist (Liste ↔ Detail); `md:border-r border-subtle bg-surface-1 z-[10]` |
| Kopf (`Row h-header border-b`) | `NotificationSidebarHeader`: Breadcrumb „Inbox“ (`InboxOutline h-4 w-4 text-primary`, ohne Tooltip); rechts `NotificationSidebarHeaderOptions` |
| Kopf-Aktionen | „Mark all as read“ (`CheckDoneOutline`, `IconButton ghost sm`, Loading bei `MARK_ALL_AS_READY`); „Refresh“ (`RefreshOutline`, Loading bei `MUTATION_LOADER`); Filter-Menü „Inbox Filters“ (`FilterOutline`) mit Checkbox-Einträgen „Assigned to me“, „Created by me“, „Subscribed by me“ (Menü bleibt offen); „⋮“-Menü (`MoreVerticalOutline`, aria „Notification options“) mit Checkbox-Einträgen „Show unread“ (`TickCircleOutline`, Filter `read`), „Show archived“ (`ArchiveOutline`, setzt `snoozed:false`), „Show snoozed“ (`ClockOutline`, setzt `archived:false`); Tooltips `side="bottom"`, mobil aus |
| Tabs (`Header variant=SECONDARY`) | „All“ (Zähler `total_unread_notifications_count`), „Mentions“ (Zähler `mention_unread_notifications_count`); aktiver Tab `text-accent-primary` mit Unterstrich `absolute bottom-0 rounded-t-md border border-accent-strong`; Zähler als `CountChip` (`getNumberCount`) nur > 0; Schrift `text-body-xs-medium` |
| Angewandte Filter | `AppliedFilters` (`Header variant=TERNARY`), nur wenn ein `type`-Filter aktiv: je Filter `Pill size="md" variant="outline"` mit `CloseOutline` (entfernt Filter) + Pill „Clear all“ (`common.clear_all`) |
| Liste | Loader (`init-loader`) → `NotificationsLoader` (8 Zeilen, Kreis `min-h-12 min-w-12`, Balken `h-5 w-36`, `w-28`, `w-16`, `animate-pulse divide-y`); sonst `ContentWrapper variant=HUGGING` mit `NotificationCardListRoot`; leer → `NotificationEmptyState` (`EmptyStateCompact assetKey="inbox" size-24 max-w-56`, „Updates for your subscribed work items will appear here“ bzw. „Mentions for your work items will appear here“) |
| Pagination | unter der Liste „Load more“ (`text-accent-secondary hover:text-accent-primary`) bzw. „Loading...“, nur wenn `paginationInfo.next_page_results`; Seitengröße `paginatedCount = 300` |

#### 2.7.2 Benachrichtigungszeile (`NotificationItem`, `.../sidebar/notification-card/item.tsx`)

| Teil | Detail |
|---|---|
| Zeile | `Row group relative flex cursor-pointer items-center gap-2 border-b border-subtle py-4`; ausgewählt `bg-layer-1/30`; ungelesen `bg-accent-primary/5` + Punkt `absolute top-[50%] left-2 h-1.5 w-1.5 rounded-full bg-accent-primary` |
| Avatar | Kreis `h-12 w-12 rounded-full bg-layer-1` mit `Avatar size="xl"` des Auslösers (`triggered_by_details`) |
| Text Zeile 1 | `NotificationContent` (s. 2.7.3), `line-clamp-1 text-body-xs-medium text-primary`; rechts Optionen (nur bei Hover bzw. offenem Snooze-Menü sichtbar) |
| Text Zeile 2 | `text-caption-sm-regular text-secondary`: „`{identifier}-{sequence_id} {name}`“; rechts entweder „Till {Datum}, {Uhrzeit 12-h}“ mit `ClockOutline` (gesnoozed) oder `calculateTimeAgo(created_at)` |
| Ausgeblendet | wenn `data.issue_activity.field`, `project` oder Workspace fehlen → leeres Fragment |
| Optionen (`NotificationOption`) | 3 Buttons `h-5 w-5 rounded-xs bg-layer-1 hover:bg-surface-2` mit Tooltip: Lesen/Ungelesen (`ChatOutline`, „Mark as read“/„Mark as unread“, Toast „Notification marked as read/unread“); Archivieren (`ArchiveOutline` / `RestoreOutline`, „Archive“/„Un archive“, Toast „Notification marked as archived/un archived“); Snooze (`ClockOutline`, „Snooze“/„Un snooze“) |
| Snooze-Menü | optional „Un snooze“ (wenn gesnoozed), dann „1 day“, „3 days“, „5 days“, „1 week“, „2 weeks“ (jetzt + n × 24 h), „Custom“ → `NotificationSnoozeModal`; Toast „Success!“ + „Notification snoozed“/„Notification un snoozed“ |
| Custom-Snooze-Dialog | `DialogContent size="md"`, Titel „Customize Snooze Time“ (hart codiert); links „Pick a date“ (`DateSelect`, `minDate=heute`, `weekStartsOn = profile.start_of_the_week`, Placeholder „Select date“; Datumswechsel leert Zeit); rechts „Pick a time“ (`Select` mit 24 Slots im 30-Min-Raster `12:00 … 11:30` aus `allTimeIn30MinutesInterval12HoursFormat`, Kopf-Umschalter AM/PM `bg-accent-primary/90 text-on-color` aktiv, Anzeige „`{hh:mm} am\|pm`“, heute nur zukünftige Zeiten, leer „No available time for this date.“); Buttons „Cancel“ / „Submit“ („Submitting...“); Pflichtfelder (Validierungstexte „Please select a date“/„Please select a time“ werden nicht angezeigt) |

#### 2.7.3 Benachrichtigungstext (`NotificationContent`, `.../sidebar/notification-card/content.tsx`, Fallbacks `.../notification-card/content.ts`)

Aufbau: **Auslöser** (`is_bot` → `first_name`, sonst `display_name`, `font-medium text-primary`) + Aktion (`text-tertiary`) + optional „to “ + **Wert** (`font-medium text-primary`) + „.“; bei `verb === "deleted"` nur Auslöser + Aktion.

| `issue_activity.field` | Aktion | Wert | „to“ |
|---|---|---|---|
| `duplicate` | „marked that this work item is a duplicate of“ (verb `created`) / „marked that this work item is not a duplicate“ | – | nein |
| `assignees` | „added assignee“ / „removed assignee“ (je nach `new_value` leer) | neuer bzw. alter Wert | nein |
| `start_date` | „set start date“ / „removed the start date“ | `renderFormattedDate(new)` | nein |
| `target_date` | „set due date“ / „removed the due date“ | formatiertes Datum | nein |
| `labels` | „added label“ / „removed label“ | Wert | nein |
| `parent` | „added parent“ / „removed parent“ | Wert | nein |
| `relates_to` | „marked that this work item is related to“ | – | ja |
| `comment` | „commented“ | bereinigter Kommentar (`sanitizeCommentForNotification`) oder – mit `renderCommentBox` – read-only `LiteTextEditor` (`scale-75`) | nein |
| `archived_at` | „restored the work item“ (new_value `restore`) / „archived the work item“ | – | nein |
| `None` | – | „the work item and assigned it to you.“ | nein |
| `attachment` | – (kein Aktionstext) | „the work item“ | ja |
| `description` | Fallback: `{verb} description` | `stripAndTruncateHTML(new, 55)` | ja |
| `estimate_time` | Fallback: `{verb} estimate time` | `convertMinutesToHoursMinutesString(new‖old)` | ja |
| alle anderen | `{verb} {feld mit Leerzeichen statt _}` (`renderAdditionalAction`) | `new_value` | ja (außer `comment`, `archived_at`, `None`, `assignees`, `labels`, `start_date`, `target_date`, `parent`) |

`ADDITIONAL_NOTIFICATION_CONTENT_MAP` ist in der CE leer (Erweiterungspunkt der Bezahl-Edition).

#### 2.7.4 Rechte Spalte (`NotificationsRoot`, `apps/web/components/workspace-notifications/root.tsx`)

| Zustand | Darstellung |
|---|---|
| keine Auswahl | zentriert `EmptyStateCompact assetKey="unknown" size-20` (ohne Text) |
| Intake-Work-Item (`is_inbox_issue`) | lädt Projekt-Mitgliedsinfo (SWR `PROJECT_MEMBER_PERMISSION_INFO_${ws}_${pid}` → `fetchUserProjectInfo`), solange `LogoSpinner`; dann `InboxContentRoot isNotificationEmbed` (A09/Intake) |
| normales Work Item | `IssuePeekOverview embedIssue` (eingebettete Peek-Ansicht, A09 §2.12); `embedRemoveCurrentNotification` hebt die Auswahl auf |

Sidebar-Zähler (`NotificationAppSidebarOption`, `apps/web/components/workspace-notifications/notification-app-sidebar-option.tsx`): `CountChip` mit „@ “-Präfix, wenn Mentions > 0 – wird nur in der ungenutzten `SidebarUserMenuItem` referenziert (Key `notifications`) und ist daher in der CE nicht sichtbar; sichtbar ist nur der rote Punkt der Top-Navigation (2.2).

### 2.8 Profil-Seiten „Your work“ (`/:ws/profile/:userId[/assigned|created|subscribed|activity]`)

Die Seiten zeigen die Arbeit eines Workspace-Mitglieds (eigenes Profil über Sidebar-Eintrag `your_work`, fremde Profile über Avatar-/Mitgliederlinks). Die Arbeitselement-Listen selbst (Layouts, Filter, Peek) sind in A09 beschrieben.

#### 2.8.1 Layout, Kopf und Tabs

| Element | Detail | Quelle |
|---|---|---|
| Layout | SWR `USER_PROFILE_PROJECT_SEGREGATION(ws,userId)` → `GET /api/workspaces/{ws}/user-profile/{userId}/` (Projekt-Aufschlüsselung für die rechte Sidebar); `AppHeader header=<UserProfileHeader/> mobileHeader=<ProfileIssuesMobileHeader/>`; darunter `ProfileNavbar`, Inhalt, rechts `ProfileSidebar` | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/layout.tsx`, `apps/web/services/user.service.ts` |
| Tabs | Viewer: „Summary“ (`summary`, Route `""`); zusätzlich nur bei WS-Rolle Admin/Member: „Assigned“ (`assigned`), „Created“ (`created`), „Subscribed“ (`subscribed`), „Activity“ (`activity`) | `packages/constants/src/profile.ts` (`PROFILE_VIEWER_TAB`, `PROFILE_ADMINS_TAB`), `layout.tsx` |
| Fehlendes Recht | Issue-Tabs bzw. Activity ohne Admin/Member-Rolle → Text „You do not have the permission to access this page.“ (`you_do_not_have_the_permission_to_access_this_page`) statt Inhalt | `layout.tsx` |
| `ProfileNavbar` | `Header variant=SECONDARY`; Tab-Links `border-b-2 p-4 text-13 font-medium whitespace-nowrap`, aktiv `border-accent-strong text-accent-primary`, sonst `border-transparent` | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/navbar.tsx` |
| `UserProfileHeader` | Breadcrumb mit Icon `YourWorkOutline`: eigenes Profil „Your work“ (`profile.page_label`), fremdes Profil „{first_name} {last_name} Work“ (`profile.work`); ab `md` rechts `ProfileIssuesFilter` (nur auf den Issue-Tabs); mobil Tab-`Menu` (Trigger = aktueller Tab) und `IconButton` `RightSidePaneOutline` → `toggleProfileSidebar` | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/header.tsx` |
| `ProfileIssuesMobileHeader` | nur Issue-Tabs, `md:hidden`: Menü „Layout“ (List/Kanban mit `IssueLayoutIcon`) und `FiltersDropdown` „Display“ mit `DisplayFiltersSelection` gemäß `ISSUE_DISPLAY_FILTERS_BY_PAGE.profile_issues.layoutOptions[layout]` | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/mobile-header.tsx` |
| `ProfileIssuesFilter` (Desktop) | `LayoutSelection` (nur LIST, KANBAN), `WorkItemFiltersToggle` (Filterzeile ein/aus), `FiltersDropdown` „Display“ (Display-Filter/-Properties, A09) | `apps/web/components/profile/profile-issues-filter.tsx` |

#### 2.8.2 Rechte Profil-Sidebar (`ProfileSidebar`, `apps/web/components/profile/sidebar.tsx`)

| Teil | Detail |
|---|---|
| Rahmen | ab `md` `w-[300px] border-l border-subtle shadow-raised-200`, mobil `fixed` und bei eingeklappt `marginLeft: 100vw`; automatisches Einklappen bei Fensterbreite < 768 (Resize) und bei Klick außerhalb (`useOutsideClickDetector`) |
| Cover | `h-[110px]`, `CoverImage` mit Default-Cover bei leerem `cover_image_url`; beim eigenen Profil `IconButton` (Stift) oben rechts → `toggleProfileSettingsModal({activeTab: "general"})` (2.13) |
| Identität | Avatar 52×52 (`rounded-sm`, Bild oder Initiale auf `bg-accent-primary text-on-color`), Name `first_name last_name`, darunter `({display_name})` |
| Details | „Joined on“ → `renderFormattedDate(date_joined)`; „Timezone“ → `ProfileSidebarTime`: aktuelle Uhrzeit des Nutzers `HH:MM` (24 h, `Intl.DateTimeFormat("en-US", {timeZone})`, minütlich via `useCurrentTime`) + Zeitzonen-Name (`apps/web/components/profile/time.tsx`) |
| Projekte | je Projekt aus `project_data` ein `Collapsible` (erstes offen): Kopf `Logo` + Name + Badge Fertigstellungsgrad `completed_issues / assigned_issues` in % (≤ 35 `bg-danger-subtle text-danger-primary`, ≤ 70 `bg-yellow-500/10 text-yellow-500`, sonst `bg-success-subtle text-success-primary`; Tooltip „Completion percentage“); Inhalt: segmentierter Balken (Created `#203b80`, Assigned `#3f76ff`, Due `#f59e0b` = `pending_issues`, Completed `#16a34a`) und vier Zeilen „Created/Assigned/Due/Completed … {n} Work items“ |
| Laden | `Loader` mit Platzhaltern, solange `userProjectsData` fehlt |

#### 2.8.3 Tab „Summary“ (`/:ws/profile/:userId`)

| Block | Detail | Quelle |
|---|---|---|
| Daten | SWR `USER_PROFILE_DATA` → `GET /api/workspaces/{ws}/user-stats/{userId}/`; `state_distribution` wird auf alle `GROUP_CHOICES` normalisiert (fehlende Gruppen = 0); Seitentitel „Your work“ | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/page.tsx` |
| „Overview“ (`ProfileStats`) | drei `Card`s (Raster 1/2/3 Spalten), je Link auf Tab: „Work items created“ (`AddOutline`, `created_issues`), „Work items assigned“ (`UserOutline`, `assigned_issues`), „Work items subscribed“ (`LayerStackIcon`, `subscribed_issues`); Wert „...“ bis geladen; Loader 3 × 80 px | `apps/web/components/profile/overview/stats.tsx` |
| „Workload“ (`ProfileWorkload`) | eine Karte je Zustandsgruppe (Raster bis 5 Spalten) mit Farbpunkt `STATE_GROUPS[group].color` (`#d9d9d9`, `#3f76ff`, `#f59e0b`, `#16a34a`, `#dc2626`) und Anzahl; Beschriftung „Backlog“, „Not started“ (unstarted), „Working on“ (started), „Completed“, „Canceled“ (hartkodiert bzw. `STATE_GROUPS.label`) | `apps/web/components/profile/overview/workload.tsx`, `packages/constants/src/state.ts` |
| „Work items by Priority“ (`ProfilePriorityDistribution`) | `BarChart` (`@plane/blocks/charts/bar-chart`) `h-[300px]`, Balkenbreite 20, X-Achse „Priority“, Farben urgent `#991b1b`, high `#ef4444`, medium `#f59e0b`, low `#16a34a`, none `#e5e5e5`; leer → `EmptyStateCompact assetKey="priority"` „No work item assigned yet“; Loader 5 Balken | `apps/web/components/profile/overview/priority-distribution.tsx` |
| „Work items by state“ (`ProfileStateDistribution`) | `PieChart` (`@plane/blocks/charts/pie-chart`, Donut `innerRadius 50%`, `paddingAngle 5`, `cornerRadius 4`, Tooltip „Count“) + Legende je Gruppe mit Anzahl; leer → derselbe Leerzustand „No work item assigned yet“ (Prioritäts-Text, s. 3.10) | `apps/web/components/profile/overview/state-distribution.tsx` |
| „Recent activity“ (`ProfileActivity`) | SWR `USER_PROFILE_ACTIVITY` → `GET /api/workspaces/{ws}/user-activity/{userId}/?per_page=10`; je Eintrag Avatar (sm), Akteur („You“ bzw. `display_name`), `ActivityMessage showIssue` bzw. „created {IssueLink}“, relative Zeit (`calculateTimeAgo`); leer „No Data yet“ (`EmptyStateCompact assetKey="unknown"`); Loader 5 × 40 px | `apps/web/components/profile/overview/activity.tsx` |

#### 2.8.4 Tabs „Assigned“, „Created“, „Subscribed“ (`/:ws/profile/:userId/:profileViewId`)

| Aspekt | Detail | Quelle |
|---|---|---|
| Store | `EIssuesStoreType.PROFILE`; `setViewId(profileViewId)` (`assigned`/`created`/`subscribed`); SWR `CURRENT_WORKSPACE_PROFILE_ISSUES_${ws}_${userId}` lädt Filter (`fetchFilters`) | `apps/web/components/profile/profile-issues.tsx` |
| Abruf | `GET /api/workspaces/{ws}/user-issues/{userId}/` mit Parametern des Profil-Issue-Stores (Filter, Gruppierung, Paginierung, A09) | `apps/web/services/user.service.ts` (`getUserProfileIssues`) |
| Filter | `WorkspaceLevelWorkItemFiltersHOC` + `WorkItemFiltersRow`; erlaubte Filter `priority`, `state_group`, `label_id`, `start_date`, `target_date` | `packages/constants/src/issue/filter.ts` (`ISSUE_DISPLAY_FILTERS_BY_PAGE.profile_issues`) |
| Layouts | nur List (Gruppierung `state_detail.group`, `priority`, `project`, `labels`, keine; Extra „show_empty_groups“, „sub_issue“) und Kanban (ohne „keine“ Gruppierung; Extra „show_empty_groups“); Sortierung `sort_order`, `-created_at`, `-updated_at`, `start_date`, `-priority`; Typ `active`/`backlog` | ebd. |
| Peek | `IssuePeekOverview` (A09) | `profile-issues.tsx` |

#### 2.8.5 Tab „Activity“ (`/:ws/profile/:userId/activity`)

| Aspekt | Detail | Quelle |
|---|---|---|
| Seite | Titel „Profile - Activity“; Seiten à 100 Einträge (`PER_PAGE = 100`), Cursor `100:{i}:0`; je Seite `WorkspaceActivityListPage` (SWR `USER_PROFILE_ACTIVITY` mit Cursor); Button „Load more“ (`common.load_more`), solange `next_page_results`; Kopf rechts `DownloadActivityButton` | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/activity/page.tsx`, `apps/web/components/profile/activity/workspace-activity-list.tsx` |
| Download | nur WS-Admin/Member; „Download today's activity“/„Downloading“; `POST /api/workspaces/{ws}/user-activity/{userId}/export/ {date: heute}` → CSV-Blob, Datei `profile-activity-{Date.now()}.csv` | `apps/web/components/profile/activity/download-button.tsx` |
| Liste (`ActivityList`) | Kommentar-Einträge: Avatar (oder Initiale), Name, „Commented {timeAgo}“, Kommentar als schreibgeschützter `RichTextEditor`; sonstige Einträge: `ActivityIcon`, Akteur „Plane“ (bei `field === "archived_at"` und nicht „restore“), Bots „{first_name} Bot“, eigener Nutzer „You“, `ActivityMessage` + relative Zeit | `apps/web/components/profile/activity/activity-list.tsx` |
| Nicht eingebunden | `ProfileSettingContentWrapper` (`apps/web/components/profile/profile-setting-content-wrapper.tsx`) | – |

### 2.9 Power-K Command Palette (`apps/web/components/power-k/**`)

#### 2.9.1 Architektur-Bausteine

| Baustein | Datei | Aufgabe |
|---|---|---|
| `ProjectsAppPowerKProvider` | `apps/web/components/power-k/projects-app-provider.tsx` | Eingebunden in `(projects)/layout.tsx`; baut den `TPowerKContext` (`currentUserId`, `activeCommand`, `activeContext`, `shouldShowContextBasedActions`, `params` + abgeleitete `projectId` (Route oder Projekt des Work Items aus `/browse/:workItem`), `router`, `closePalette`, `setActiveCommand`, `setActivePage`); rendert `GlobalShortcutsProvider`, `WorkspaceLevelModals`, `ProjectLevelModals` (nur mit `projectId`), `WorkItemLevelModals`, `ProjectsAppPowerKModalWrapper` |
| `GlobalShortcutsProvider` | `global-shortcuts.tsx` | setzt `activeContext` aus der URL (`detectContextFromURL`), registriert alle Befehle neu (`registry.clear()` + `registerMultiple`), hängt **einen** `keydown`-Listener an `document` (`ShortcutHandler`), rendert `ShortcutsModal` |
| Kontext-Erkennung | `core/context-detector.ts` | Priorität: `params.workItem` → `work-item`, `cycleId` → `cycle`, `moduleId` → `module`, `pageId` → `page`, sonst `null` |
| Registry | `core/registry.ts` (`PowerKCommandRegistry`, MobX) | `Map<id, command>`; `getVisibleCommands(ctx)` filtert `isVisible(ctx)` und – für `contextual` – `activeContext === contextType` **und** `shouldShowContextBasedActions`; Lookup-Maps für `shortcut`, `keySequence`, `modifierShortcut` (lowercase) |
| Store | `apps/web/store/base-power-k.store.ts` | `isPowerKModalOpen`, `isShortcutsListModalOpen`, `commandRegistry`, `activeContext`, `activePage`, `topNavInputRef`; Aktionen `togglePowerKModal`, `toggleShortcutsListModal`, `setActiveContext`, `setActivePage`, `setTopNavInputRef` |
| Befehlsliste | `config/commands.ts` | Reihenfolge: Navigation, Creation, Contextual, Account, Miscellaneous, Preferences, Help |
| Modal | `ui/modal/wrapper.tsx` (`ProjectsAppPowerKModalWrapper`) | `Dialog` + `DialogContent size="md"` (≈ 672 px), `cmdk`-`Command` mit eigenem Filter, Header, `Command.List` (`max-h-96 overflow-scroll`), Footer |
| Top-Nav-Variante | `apps/web/components/navigation/top-nav-power-k.tsx` | gleiche Befehlsliste als aufklappendes Panel unter dem Suchfeld (2.2) |
| Styles | `apps/web/styles/power-k.css` | `[cmdk-group]` `mt-2 px-[0.45rem]`; `[cmdk-group-heading]` `text-tertiary text-12 font-medium mb-2 px-[0.45rem]`; `[cmdk-item]` `flex items-center justify-between cursor-pointer bg-layer-transparent text-body-xs-regular p-2 rounded-md`, Fokus/`aria-selected` `bg-layer-transparent-active`, disabled `opacity-50 cursor-not-allowed` (Fokus `bg-layer-1/70`) |

Befehlstyp (`core/types.ts`): `{id, i18n_title, i18n_description?, icon?|iconNode?, shortcut?|keySequence?|modifierShortcut?, closeOnSelect, isVisible(ctx), isEnabled(ctx), keywords?, group, contextType? (nur group "contextual"), type: "action" (action(ctx)) | "change-page" (page, onSelect(data, ctx))}`. Gruppen-Priorität und -Titel (`ui/renderer/shared.ts`): contextual 1 (Titel je Kontext, s. u.), create 2 „Create“, navigation 3 „Navigate“, general 7 „General“, settings 8 „Settings“, account 9 „Account“, miscellaneous 10 „Miscellaneous“, preferences 11 „Preferences“, help 12 „Help“.

#### 2.9.2 Vollständiges Befehlsinventar

Legende Sichtbarkeit: **WS** = Route hat `workspaceSlug`; **PRJ** = zusätzlich `projectId` (Route oder Work-Item); **WS-M** = WS-Rolle Admin/Member; **PRJ-M** = Projektrolle Admin/Member; Feature-Flags des Projekts (`cycle_view`, `module_view`, `issue_views_view`, `page_view`, `inbox_view`). Für `change-page`-Befehle zeigt die Spalte „Ergebnis“ die Auswahlseite. Quelle je Gruppe in der letzten Spalte.

| id | Titel (EN) | Typ | Taste | sichtbar/aktiv wenn | Ergebnis | Quelle |
|---|---|---|---|---|---|---|
| `open_project_cycle` | Open a cycle | change-page `open-project-cycle` | `O` dann `C` | PRJ, PRJ-M, `cycle_view` | Liste der Projekt-Cycles (Spinner bis `fetchedMap[pid]`) → `/${ws}/projects/${pid}/cycles/${id}` | `config/navigation/commands.ts` |
| `open_project_module` | Open a module | change-page `open-project-module` | `O` `M` | PRJ, PRJ-M, `module_view` | Module (Icon = Modulstatus) → `…/modules/${id}` | ebd. |
| `open_project_view` | Open a project view | change-page `open-project-view` | `O` `V` | PRJ, `issue_views_view` | Projekt-Views → `…/views/${id}` | ebd. |
| `open_project_setting` | Open a project setting | change-page `open-project-setting` | `O` `S` | PRJ | `PROJECT_SETTINGS` mit Rollenrecht (Icons `PROJECT_SETTINGS_ICONS`) → `/${ws}/settings/projects/${pid}/{href}` | ebd., `ui/pages/open-entity/project-settings-menu.tsx` |
| `open_project` | Open a project | change-page `open-project` | `O` `P` | WS | beigetretene Projekte (Logo 14) → `/${ws}/projects/${id}/issues` | ebd. |
| `open_workspace_setting` | Open a workspace setting | change-page `open-workspace-setting` | `O` `S` | WS und **nicht** PRJ | `WORKSPACE_SETTINGS` mit Rollenrecht → `/${ws}/{href}` | ebd., `ui/pages/open-entity/workspace-settings-menu.tsx` |
| `open_workspace` | Open a workspace | change-page `open-workspace` | `O` `W` | WS | alle Workspaces (Spinner bei `loader`) → `/${slug}` | ebd. |
| `nav_home` | Go to home | action | `G` `H` | WS | `/${ws}` | ebd. |
| `nav_inbox` | Go to inbox | action | `G` `X` | WS | `/${ws}/notifications` | ebd. |
| `nav_your_work` | Go to your work | action | `G` `Y` | WS, WS-M | `/${ws}/profile/${userId}` | ebd. |
| `nav_project_work_items` | Go to work items | action | `G` `I` | PRJ | `/${ws}/projects/${pid}/issues` | ebd. |
| `nav_project_pages` | Go to pages | action | `G` `D` | PRJ, `page_view` | `…/pages` | ebd. |
| `nav_project_cycles` | Go to cycles | action | `G` `C` | PRJ, PRJ-M, `cycle_view` | `…/cycles` | ebd. |
| `nav_project_modules` | Go to modules | action | `G` `M` | PRJ, PRJ-M, `module_view` | `…/modules` | ebd. |
| `nav_project_views` | Go to project views | action | `G` `V` | PRJ, `issue_views_view` | `…/views` | ebd. |
| `nav_project_intake` | Go to intake | action | `G` `K` | PRJ, `inbox_view` | `…/intake` | ebd. |
| `nav_project_settings` | Go to project settings | action | `G` `S` | PRJ | `/${ws}/settings/projects/${pid}` | ebd. |
| `nav_project_archives` | Go to project archives | action | `G` `R` | PRJ, PRJ-M | `…/archives/issues` | ebd. |
| `nav_all_workspace_work_items` | Go to all work items | action | – | WS | `/${ws}/workspace-views/all-issues` | ebd. |
| `nav_assigned_workspace_work_items` | Go to assigned work items | action | – | WS | `…/workspace-views/assigned` | ebd. |
| `nav_created_workspace_work_items` | Go to created work items | action | – | WS | `…/workspace-views/created` | ebd. |
| `nav_subscribed_workspace_work_items` | Go to subscribed work items | action | – | WS | `…/workspace-views/subscribed` | ebd. |
| `nav_workspace_analytics` | Go to workspace analytics | action | `G` `A` | WS, WS-M | `/${ws}/analytics/overview` | ebd. |
| `nav_workspace_settings` | Go to workspace settings | action | `G` `S` | WS, nicht PRJ | `/${ws}/settings` | ebd. |
| `nav_workspace_drafts` | Go to workspace drafts | action | `G` `J` | WS, WS-M | `/${ws}/drafts` | ebd. |
| `nav_workspace_archives` | Go to workspace archives | action | `G` `R` | WS, nicht PRJ, WS-M | `/${ws}/projects/archives` | ebd. |
| `nav_projects_list` | Go to projects list | action | `G` `P` | WS | `/${ws}/projects` | ebd. |
| `nav_account_settings` | Go to account settings | action | – | WS | `/${ws}/settings/account` (→ Redirect `/settings/profile/general`, A08 §2.2.8) | ebd. |
| `create_work_item` | New work item | action | `N` `I` | `canPerformAnyCreateAction` und ≥ 1 Workspace-Projekt | `toggleCreateIssueModal(true)` (Vorbelegung `cycle_id`/`module_ids` auf Cycle-/Modul-Seiten, `apps/web/components/modals/work-item-level.tsx`) | `config/creation/command.ts` |
| `create_page` | New page | action | `N` `D` | PRJ, `page_view`, PRJ-M | `toggleCreatePageModal({isOpen:true})` → `CreatePageModal` (Redirect nach Anlage) | ebd. |
| `create_view` | New view | action | `N` `V` | PRJ, `issue_views_view`, PRJ-M | `CreateUpdateProjectViewModal` | ebd. |
| `create_cycle` | New cycle | action | `N` `C` | PRJ, `cycle_view`, PRJ-M | `CycleCreateUpdateModal` | ebd. |
| `create_module` | New module | action | `N` `M` | PRJ, `module_view`, PRJ-M | `CreateUpdateModuleModal` | ebd. |
| `create_project` | New project | action | `N` `P` | WS-M | `CreateProjectModal` | ebd. |
| `create_workspace` | New workspace | action | – | `!config.is_workspace_creation_disabled` | `router.push("/create-workspace")` | ebd. |
| `change_work_item_state` | Change state | change-page `update-work-item-state` | `S` | Kontext work-item, PRJ-M, nicht archiviert | Projekt-States (`StateGroupIcon`, Haken beim aktuellen) → `updateIssue({state_id})` (gleicher Wert → no-op) | `ui/pages/context-based/work-item/commands.ts` |
| `change_work_item_priority` | Change priority | change-page `update-work-item-priority` | `P` | wie oben | `ISSUE_PRIORITIES` mit `PriorityIcon` → `{priority}` | ebd. |
| `change_work_item_assignees` | Assign to | change-page `update-work-item-assignee` | `A` | wie oben | Projektmitglieder (Avatar xs, Haken bei Zugewiesenen) → Toggle in `assignee_ids`; **bleibt offen** (`closeOnSelect:false`) | ebd. |
| `assign_work_item_to_me` | Assign to me / Un-assign from me | action | `I` | wie oben | Toggle eigener User in `assignee_ids`; Icon `UserPlusOutline`/`UserMinusOutline` | ebd. |
| `change_work_item_estimate` | Change estimate | change-page `update-work-item-estimate` | `⇧E` | wie oben + Estimates aktiv | „No estimate“ + Punkte des aktiven Estimates (Zeit-Typ als „Xh Ym“), „No estimate found“ bei leer → `{estimate_point}` | ebd., `estimates-menu.tsx` |
| `add_work_item_to_cycle` | Add to cycle | change-page `update-work-item-cycle` | `⇧C` | wie oben + `cycle_view` | Projekt-Cycles (Haken beim aktuellen) → `addCycleToIssue`; leere Auswahl → `removeIssueFromCycle` | ebd. |
| `add_work_item_to_modules` | Add to modules | change-page `update-work-item-module` | `⇧M` | wie oben + `module_view` | Module (Mehrfach, Haken) → `changeModulesInIssue(add\|remove)`; bleibt offen | ebd. |
| `add_work_item_labels` | Add labels | change-page `update-work-item-labels` | `L` | wie oben | Labels (Farbpunkt `size-2.5`) → Toggle `label_ids`; bleibt offen | ebd. |
| `subscribe_work_item` | Subscribe to notifications / Unsubscribe from notifications | action | `⇧S` | wie oben | Abo an/aus; Toast `issue.subscription.actions.subscribed/unsubscribed` | ebd. |
| `delete_work_item` | Delete | action | `Ctrl/⌘ ⌫` | wie oben | `toggleDeleteIssueModal(true)` → `DeleteIssueModal`; nach Löschen Redirect `/${ws}/projects/${pid}/issues` (Epic: `/epics`) | ebd., `apps/web/components/modals/work-item-level.tsx` |
| `copy_work_item_id` | Copy ID | action | `Ctrl/⌘ .` | Kontext work-item | kopiert `PROJ-123`, Toast „Work item ID copied to clipboard.“ | ebd. |
| `copy_work_item_title` | Copy title | action | `Ctrl/⌘ ⇧ '` | Kontext work-item | kopiert Titel | ebd. |
| `copy_work_item_url` | Copy URL | action | `Ctrl/⌘ ⇧ ,` | Kontext work-item | kopiert `window.location.href` | ebd. |
| `toggle_cycle_favorite` | Add to favorites / Remove from favorites | action | `⇧F` | Kontext cycle, PRJ-Rolle Admin/Member (ohne Projekt-ID-Prüfung), nicht archiviert | `addCycleToFavorites`/`removeCycleFromFavorites` | `ui/pages/context-based/cycle/commands.ts` |
| `copy_cycle_url` | Copy URL | action | `Ctrl/⌘ ⇧ ,` | Kontext cycle | URL kopieren | ebd. |
| `add_remove_module_members` | Add/remove members | change-page `update-module-member` | `M` | Kontext module, Admin/Member, nicht archiviert | Projektmitglieder → Toggle `member_ids`; bleibt offen | `ui/pages/context-based/module/commands.tsx` |
| `change_module_status` | Change status | change-page `update-module-status` | `S` | wie oben | `MODULE_STATUS` mit `ModuleStatusIcon` → `{status}` | ebd., `module/status-menu.tsx` |
| `toggle_module_favorite` | Add/Remove from favorites | action | `⇧F` | wie oben | Favorit umschalten | ebd. |
| `copy_module_url` | Copy URL | action | `Ctrl/⌘ ⇧ ,` | Kontext module | URL kopieren | ebd. |
| `toggle_page_lock` | Lock / Unlock | action | `⇧L` | Kontext page, `canCurrentUserLockPage` | `lock/unlock({shouldSync:true, recursive:true})` | `ui/pages/context-based/page/commands.ts` |
| `toggle_page_access` | Make private / Make public | action | `⇧A` | `canCurrentUserChangeAccess` | `makePrivate/makePublic({shouldSync:true})` | ebd. |
| `toggle_page_archive` | Archive / Restore | action | `⇧R` | `canCurrentUserArchivePage` | `archive/restore({shouldSync:true})` | ebd. |
| `toggle_page_favorite` | Add/Remove from favorites | action | `⇧F` | `canCurrentUserFavoritePage` | Favorit umschalten | ebd. |
| `copy_page_url` | Copy URL | action | `Ctrl/⌘ ⇧ ,` | Kontext page | URL kopieren | ebd. |
| `workspace_invites` | Workspace invites | action | – | immer | `/invitations` | `config/account-commands.ts` |
| `sign_out` | Sign out | action | – | immer | `signOut()`, Fehler-Toast | ebd. |
| `toggle_app_sidebar` | Toggle app sidebar | action | `Ctrl/⌘ B` | immer | `toggleSidebar()` | `config/miscellaneous-commands.ts` |
| `copy_current_page_url` | Copy current page URL | action | `Ctrl/⌘ ⇧ C` | immer | URL kopieren, Toast „Current page URL copied to clipboard.“ | ebd. |
| `focus_top_nav_search` | Focus search input | action | `Ctrl/⌘ F` | nur wenn Top-Nav-Input gemountet (sonst Browser-Suche) | `topNavInputRef.focus()` (öffnet Panel, da Tastatur-Trigger) | ebd. |
| `update_interface_theme` | Change interface theme | change-page `update-theme` | – | immer | `THEME_OPTIONS` (`packages/constants/src/themes.ts`) → `setTheme` + `PATCH` Profil-Theme `{theme}`; Toast „Theme updated“ / „Reloading to apply changes...“ und **`window.location.reload()`** | `config/preferences-commands.ts` |
| `update_timezone` | Change timezone | change-page `update-timezone` | – | immer | `useTimezone().timezones` → `updateCurrentUser({user_timezone})` | ebd. |
| `update_start_of_week` | Change first day of week | change-page `update-start-of-week` | – | immer | `START_OF_THE_WEEK_OPTIONS` → `updateUserProfile({start_of_the_week})` | ebd. |
| `update_interface_language` | Change interface language | change-page `update-language` | – | immer | `SUPPORTED_LANGUAGES` (Label = Sprachname) → `updateUserProfile({language})` | ebd. |
| `open_keyboard_shortcuts` | Open keyboard shortcuts | action | `Ctrl/⌘ /` | immer | `ShortcutsModal` | `config/help-commands.ts` |
| `open_plane_documentation` | Open Plane documentation | action | – | immer | `https://docs.plane.so/` (neuer Tab) | ebd. |
| `join_forum` | Join our Forum | action | – | immer | `https://forum.plane.so` | ebd. |
| `report_bug` | Report a bug | action | – | immer | `https://github.com/makeplane/plane/issues/new/choose` | ebd. |

Nicht registrierte, aber übersetzte Keys (Hinweis auf EE-Befehle): `power_k.actions_commands.bulk_delete_work_items`, `power_k.creation_actions.create_project_automation`, `power_k.navigation_actions.nav_workspace_active_cycle`, `power_k.navigation_actions.nav_project_overview`, `power_k.help_actions.chat_with_us`, `power_k.search_menu.go_to_advanced_search` (`packages/i18n/src/locales/en/power-k.json`).

#### 2.9.3 Modal-UI

| Teil | Detail | Quelle |
|---|---|---|
| Kopf | `border-b border-subtle`; Kontext-Chip (nur ohne aktive Seite und wenn Kontextaktionen eingeblendet): `inline-flex rounded-sm bg-layer-1 py-0.5 pr-1 pl-2 text-11 font-medium` mit Indikator-Label („Work item“/„Cycle“/„Module“/„Page“) · Punkt · Name (Work-Item-Identifier aus URL, Cycle-/Modulname, Page-Name), „×“ (`CloseOutline size-2.5`, Title „Clear context (Backspace)“) blendet Kontextaktionen aus; Suchzeile `px-4 py-3` mit `SearchOutline size-4`, `Command.Input` (`text-13`, Autofokus), Placeholder je Seite (`POWER_K_MODAL_PAGE_DETAILS`, Default „Type a command or search“), Clear-Button | `ui/modal/header.tsx`, `ui/modal/context-indicator.tsx`, `ui/modal/constants.ts`, `apps/web/components/power-k/hooks/use-context-indicator.ts` |
| Zeile | `PowerKModalCommandItem`: links Icon `size-3.5` bzw. `iconNode` + Label (`text-secondary`, disabled `opacity-70`), rechts Haken (`TickOutline size-3`) bei Auswahl, `KeySequenceBadge` („G then M“: `kbd h-5 rounded-sm border border-strong bg-surface-1 px-1.5 font-code text-10 text-tertiary` + Trenner „then“ `text-10 text-placeholder`), `ShortcutBadge` (Mac: ⌘ ⌃ ⌥ ⇧, sonst Ctrl/Alt/Shift; ⌫, ↵, Space, Esc, Tab, Pfeile; sonst Großbuchstabe) | `ui/modal/command-item.tsx`, `ui/modal/command-item-shortcut-badge.tsx` |
| Default-Seite | alle sichtbaren Befehle gruppiert nach Gruppe (Priorität s. o.); Titel der Gruppe `contextual` = „Work item actions“/„Cycle actions“/„Module actions“/„Page actions“ | `ui/pages/default.tsx`, `ui/renderer/command.tsx` |
| Suche | `Command`-Filter: Item-`value` enthält Suchtext (case-insensitive), `no-results` immer sichtbar; Filter nur aktiv bei nicht leerem Suchtext. Zusätzlich serverseitige Suche (Debounce 500 ms): `GET /api/workspaces/{ws}/search/?search=…&workspace_search=<bool>[&project_id=…]` (`WorkspaceService.searchWorkspace`); Überschrift „Search results for "…" in workspace/project:“ (`text-11`, pulsierend während Suche); Ergebnisgruppen „Workspaces“, „Projects“, „Work items“, „Cycles“, „Modules“, „Views“, „Pages“; keine Treffer → Eintrag „No results found  Clear search“ (leert Suche) | `ui/modal/search-menu.tsx`, `search-results.tsx`, `search-results-map.tsx`, `no-results-command.tsx` |
| Ergebnisziele | workspace → `/${slug}/`; project → `/${ws}/projects/${id}/issues/`; issue → `generateWorkItemLink` (Browse-URL `PROJ-123`); cycle/module/issue_view → `/${ws}/projects/${pid}/{cycles\|modules\|views}/${id}`; page → erstes Projekt (bzw. aktuelles, wenn enthalten) `…/pages/${id}`, ohne Projekt `/${ws}/wiki/${id}` (Route existiert in CE nicht) | `search-results-map.tsx` |
| Footer | `rounded-b-lg border-t border-subtle bg-surface-2/80 px-4 py-2`; rechts „Workspace level“ (`text-11 text-tertiary`) + `Switch size="sm"` (disabled ohne Projekt; ohne Projekt wird immer workspaceweit gesucht) | `ui/modal/footer.tsx`, `ui/modal/commands-list.tsx` |
| Auswahlseiten-Leerzustände | „No cycles found“, „No modules found“, „No labels found“, „No projects found“, „No settings found“, „No views found“, „No workspaces found“, Default „No results found“ (`px-3 py-8 text-center text-13 text-tertiary`) | `apps/web/components/power-k/menus/*.tsx` |
| Shortcut-Übersicht (`ShortcutsModal`) | `DialogContent size="xs"`, Höhe `h-[61vh]`, Titel „Keyboard shortcuts“, Suchfeld „Search for shortcuts“ (Autofokus, Teilstring auf übersetzten Titel), Gruppen wie oben (Kontextbefehle je Kontexttyp eigene Gruppe), Zeile Titel `text-11 text-secondary` + Badges; leer „No shortcuts found for "…"“ (Query fett-kursiv); zeigt **alle** registrierten Befehle mit Taste (unabhängig von Sichtbarkeit) | `ui/modal/shortcuts-root.tsx`, `ui/renderer/shortcut.tsx` |

### 2.10 Einstellungs-Rahmen (`apps/web/components/settings/**`)

| Baustein | Datei | Klassen / Verhalten |
|---|---|---|
| Settings-Layout (Route) | `apps/web/app/(all)/[workspaceSlug]/(settings)/layout.tsx` | eigener `ProjectsAppPowerKProvider` (Power-K funktioniert auch in Einstellungen), Karte `relative flex size-full overflow-hidden rounded-lg border border-subtle` **ohne App-Sidebar**; Inhalt `ContentWrapper className="w-full bg-surface-1 md:flex"` |
| `SettingsContentWrapper` | `apps/web/components/settings/content-wrapper.tsx` | `@container flex size-full grow flex-col overflow-hidden`; optional `AppHeader` mit Seiten-Header; `ScrollArea`; Inhalt `py-9`; Modus „hugging“ (Tabellen-Seiten: Members, Exports, Billing, Projekt-Members, Automations) `w-full px-page-x lg:px-12`, sonst zentriert `mx-auto w-full max-w-225 px-page-x @min-[58.95rem]:px-0` (56,25 rem + 2×1,35 rem) |
| `SettingsPageHeader` | `page-header.tsx` | `Header` mit Left/Right-Item (Breadcrumb mit Icon + Label des Tabs) |
| `SettingsHeading` | `heading.tsx` | Titel `text-h3-medium` (Varianten `h4`/`h6`), Beschreibung `text-body-xs-regular text-tertiary`, optional Control rechts (`md:flex-row`) |
| `SettingsBoxedControlItem` | `boxed-control-item.tsx` | Karte `rounded-lg border border-subtle bg-layer-2 px-4 py-3`, Titel `text-body-sm-medium`, Beschreibung `text-caption-md-regular text-tertiary`, Control rechts |
| `SettingsControlItem` | `control-item.tsx` | ungerahmte Zeile `py-3`, Beschreibung `text-secondary` (Profil-Präferenzen, E-Mail-Benachrichtigungen) |
| `SettingsSidebarItem` | `sidebar/item.tsx` | Link/Button `flex items-center gap-2 rounded-lg px-2 py-1.5 text-body-sm-medium text-secondary`, aktiv `bg-layer-transparent-selected text-primary`, sonst `hover:bg-layer-transparent-hover`; Icon in `size-4` (Icon `size-3.5`) |
| `SettingsMobileNav` | `mobile/nav.tsx` | nur `< md`: Leiste `border-b px-page-x py-3` mit Hamburger (`IconButton secondary sm`, Icon `Menu`, aria „Toggle settings menu“) → Sidebar-Inhalt als Overlay (`absolute top-10.5 left-0 z-50`, `max-h-100 rounded-lg border`), Pfad-Anzeige `ChevronRightOutline` + aktueller Tab; Zustand `useUserSettings().sidebarCollapsed`, Außenklick schließt |
| Pfad-Helfer | `helper.ts` | `pathnameToAccessKey(pathname)` → Segmente 2–3 nach dem Slug (z. B. `/settings/members`); `getWorkspaceActivePath`/`getProjectActivePath` → i18n-Label des aktiven Tabs für die Mobile-Navigation |
| `SettingsContentLayout` | `layout.tsx` | ungenutzt |

#### 2.10.1 Workspace-Einstellungen – Sidebar und Rechte

Sidebar `WorkspaceSettingsSidebarRoot` (`apps/web/components/settings/workspace/sidebar/root.tsx`): `w-[250px] border-r bg-surface-1 animate-fade-in`. Kopf (`header.tsx`): Zurück-Pfeil (`ArrowNarrowLeftOutline`, aria `back_to_workspace` „Back to workspace“) → `/${ws}/` + Text „Workspace settings“ (hart codiert, `text-body-md-medium`), darunter `WorkspaceLogo size-8` + Name + Rollenname (`ROLE_DETAILS[role].i18n_title`). Kategorien (`item-categories.tsx`) mit Überschrift `p-2 text-caption-md-medium text-tertiary capitalize`, getrennt durch `divide-y`; leere Kategorien werden ausgeblendet. Aktiv-Regel: General exakt `/${ws}/settings/`, sonst Regex `^/${ws}{href}/`.

| Kategorie (`WORKSPACE_SETTINGS_CATEGORY`) | Tab-Key | Label (EN) | href | Icon (`WORKSPACE_SETTINGS_ICONS`) | Rollen | Inhalt |
|---|---|---|---|---|---|---|
| Administration | `general` | General | `/settings` | `BuildingOutline` | Admin, Member | 2.10.2 |
| Administration | `members` | Members | `/settings/members` | `MembersOutline` | Admin, Member | 2.10.3 |
| Administration | `billing-and-plans` | Billing and plans | `/settings/billing` | `BillingsOutline` | Admin | 2.18 (**entfällt, ADR-001**) |
| Administration | `export` | Exports | `/settings/exports` | `ExportOutline` | Admin, Member | `SettingsHeading` „Exports“ / „Export your project data in various formats and access your export history with download links.“ + `ExportGuide` (`apps/web/components/exporter/*`, nicht A10a) |
| Features | – | – | – | – | – | Kategorie in CE leer → ausgeblendet (EE-Erweiterungspunkt) |
| Developer | `webhooks` | Webhooks | `/settings/webhooks` | `WebhooksOutline` | Admin | Liste + „Add webhook“, Leerzustand `assetKey="webhook"`; Detail `/settings/webhooks/:id` mit `WebhookForm` und Löschbereich (`apps/web/components/web-hooks/*`, nicht A10a) |

Zugriffsprüfung im Layout `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/layout.tsx`: `WORKSPACE_SETTINGS_ACCESS[accessKey]` enthält Rolle? sonst `NotAuthorizedView section="settings"` (2.14.4). Seitentitel: General „`{ws} - General settings`“, Members „`{ws} - Members`“, Exports „`{ws} - Exports`“, Webhooks „`{ws} - Webhooks`“, Webhook-Detail „`{ws} - Webhook`“, Billing „`{ws} - Billing & Plans`“. Die Datei `.../(workspace)/integrations/page.tsx` ist nicht geroutet.

#### 2.10.2 Workspace „General“ (`WorkspaceDetails`, `apps/web/components/workspace/settings/workspace-details.tsx`)

| Element | Detail |
|---|---|
| Logo | Button (nur Admin): Bild `size-14 rounded-md` oder Initiale `size-14 rounded-md bg-accent-primary text-24 text-on-color uppercase` (Fallback „N“) → `WorkspaceImageUploadModal` (2.16.5) |
| Kopfzeile | Name (`text-h5-semibold`, live aus Formular), URL-Button „`host/slug`“ (`text-body-xs-regular`) → kopiert `${slug}` als URL, Toast „Workspace URL copied to the clipboard.“; Admin: Link „Upload logo“ bzw. `EditOutline` + „Edit logo“ (`text-caption-sm-medium text-accent-primary`) |
| Felder (Raster `grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-10`) | „Workspace name“ (`Input 2xl`, Validierung `validateWorkspaceName(value, true)`: Pflicht „Name is required“, max 80 „Workspace name should not exceed 80 characters“, Zeichenregeln aus `@plane/utils`); „Company size“ (`Select` mit `ORGANIZATION_SIZE` = „Just myself“, „2-10“, „11-50“, „51-200“, „201-500“, „500+“; Placeholder „Select organization size“); „Workspace URL“ (disabled, `host/slug`); „Workspace Timezone“ (`TimezoneSelect`, 2.16.9) |
| Speichern | Admin: `Button primary md` „Update workspace“/„Updating“ → `PATCH` Workspace `{name, organization_size, timezone}`; Toast „Success!“/„Workspace updated successfully“; Fehler nur Konsole; Loading endet 300 ms verzögert |
| Logo entfernen | `updateWorkspace({logo_url: ""})`; Toast „Workspace picture removed successfully.“ bzw. Fehler „There was some error in deleting your profile picture. Please try again.“ |
| Nicht-Admin | gesamter Bereich `opacity-60`, alle Felder disabled, kein Speichern-/Löschbereich |
| Löschbereich (Admin) | `mt-10` `SettingsBoxedControlItem` „Delete this workspace“ / „When deleting a workspace, all of the data and resources within that workspace will be permanently removed and cannot be recovered.“ + `Button danger-outline sm` „Delete“ |
| Lösch-Dialog (`DeleteWorkspaceModal` + `DeleteWorkspaceForm`, `DialogContent size="sm"`) | Warn-Icon (`WarningTriangleOutline` in `size-12 sm:size-10 rounded-full bg-danger-subtle`), Titel „Are you sure you want to delete this workspace?“, Text „You are about to delete the workspace **{name}**. If you confirm, you will lose access to all your work data in this workspace without any way to restore it. Tread very carefully.“; Feld 1 „Type in this workspace's name to continue.“ (Placeholder = Name); Feld 2 „For final confirmation, type **delete my workspace** below.“; „Confirm“/„Deleting“ (`danger`) nur aktiv, wenn beide exakt passen; Erfolg: `deleteWorkspace(slug)` → `fetchCurrentUserSettings()` → Redirect `getWorkspaceRedirectionUrl()` → Toast „Workspace deleted.“/„You will soon go to your profile page.“; Fehler „That didn't work.“/„Try again, please.“ |

#### 2.10.3 Workspace „Members“ (`apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx`)

| Element | Detail |
|---|---|
| Kopf | „Members“ (`text-h3-medium`) + `CountChip` (Anzahl `workspaceMemberIds`); rechts Suchfeld (`SearchOutline`, Placeholder „Search...“, Autofokus, `max-w-[234px]`), `MemberListFiltersDropdown memberType="workspace"` (Button „Filters“ mit Chevron, Punkt `bg-accent-primary` bei aktiven Filtern; Gruppe „Roles“ mit Zähler; Checkboxen Admin(20), Member(15), Guest(5), „Suspended“), „Add member“ (`Button primary md`, nur Admin) |
| Daten | SWR `WORKSPACE_MEMBERS_AND_MEMBER_INVITATIONS_${ws}` → erst Einladungen, dann Mitglieder (`GET /api/workspaces/{ws}/invitations/`, `GET /api/workspaces/{ws}/members/`); Loader `MembersSettingsLoader` |
| Tabelle (`DataTable`, `apps/web/components/common/data-table.tsx`) | Spalten (`useMemberColumns`): „Full name“ (Avatar `size-6` bzw. Initiale auf `bg-layer-3`, Link aufs Profil; Suspendierte mit `DeactivatedUserOutline`, Text `text-placeholder`; Hover-Menü „…“ mit „Remove“ bzw. „Leave“ für sich selbst – nur Admin oder eigene Zeile), „Display name“ (`w-32`), „Email address“ (`w-48 truncate`), „Account type“ (Admin: `Select select-ghost-md` mit Admin/Member/Guest → `PATCH …/members/{id}/ {role}`, Fehler-Toast mit Servertext; eigene Zeile/Nicht-Admin: Text; Suspendiert: `Badge neutral sm` „Suspended“), „Authentication“ (`LOGIN_MEDIUM_LABELS`: email „Email“, magic-code „Magic code“, github „GitHub“, gitlab „GitLab“, google „Google“, gitea „Gitea“), „Joining date“ (`renderFormattedDate`). Kopfzellen mit Sortiermenü `MemberHeaderColumn` (2.11.3); aktive Mitglieder vor suspendierten |
| Leer | „No matching members“ (`mt-16 text-center text-placeholder`), wenn weder Mitglieder noch Einladungen passen |
| Ausstehende Einladungen (nur Admin) | `Collapsible` (Default offen) „Pending invites“ (`text-h5-medium`) + `CountChip`; Zeile `WorkspaceInvitationsListItem`: Initial-Kachel `h-10 w-10 rounded-sm bg-layer-3`, E-Mail, Badge „Pending“ (`bg-label-yellow-bg-strong/20 text-label-yellow-text`), Rollen-`Select` (`pill-sm`, Nicht-Admins nur Rollen ≤ eigener), „…“-Menü (Admin): „Copy link“ (nur mit `invite_link`, Toast „Link copied!“/„Invite link copied to clipboard“) und „Remove“ (danger) → Bestätigung |
| Entfernen-Dialog (`ConfirmWorkspaceMemberRemove`) | `ConfirmDialog`: selbst → „Leave workspace?“ / `workspace_settings.settings.members.leave_confirmation`, Buttons „Leave“/„Leaving“; andere → „Remove {name}?“ / „Are you sure you want to remove member- **{name}**? They will no longer have access to this workspace. This action cannot be undone.“, „Remove“/„Removing“; bei Fehler bleibt der Dialog offen |
| Leave-Ablauf | `leaveWorkspace(ws)` → `fetchCurrentUserSettings()` → Redirect `getWorkspaceRedirectionUrl()`; Fehler-Toast „Error!“ + Servertext bzw. „Something went wrong. Please try again.“ |
| Einladungs-Dialog (`SendWorkspaceInvitationModal`) | `DialogContent size="md"`, **nicht** per Esc/Außenklick schließbar; Titel „Invite people to collaborate“, Beschreibung „Invite people to collaborate on your workspace.“; je Zeile E-Mail (`Input 2xl`, Placeholder „name@company.com“, Pflicht „We need an email address to invite them.“, Regex `/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i` „Email is invalid“) + Rolle (`Select select-2xl` `w-24`, nur Rollen ≤ eigener, Default Member) + „×“ (ab 2 Zeilen); Fußzeile „+ Add more“ (`text-caption-md-medium text-accent-primary`), „Cancel“, „Send invitations“/„Sending invitations“; Submit → `POST /api/workspaces/{ws}/invitations/ {emails:[{email, role}]}`; Toast „Invitations sent successfully“ bzw. Fehler; Reset 350 ms nach Schließen (`apps/web/hooks/use-workspace-invitation.tsx`, `apps/web/components/workspace/invite-modal/*`) |
| Nicht berechtigt | Guest → `NotAuthorizedView`; Seite `opacity-60` ohne Member-Recht (praktisch unerreichbar) |

### 2.11 Projekt-Einstellungen (`/:ws/settings/projects/:projectId/**`)

#### 2.11.1 Rahmen, Sidebar, Rechte

| Element | Detail | Quelle |
|---|---|---|
| Ohne Projekt-ID | `/:ws/settings/projects`: Layout leitet auf das erste beigetretene Projekt um; ohne Projekte Leerseite (`max-w-[480px]`): Bild `@/app/assets/empty-state/project-settings/no-projects-dark\|light.png`, „No projects yet“ (`text-16 font-semibold text-tertiary`), Text „Projects act as the foundation for goal-driven work. They let you manage your teams, tasks, and everything you need to get things done.“, Buttons „Learn more about projects“ (Link `https://plane.so/`, secondary) und „Start your first project“ (primary → `toggleCreateProjectModal(true)`) | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/layout.tsx`, `.../projects/page.tsx` |
| Mit Projekt-ID | `SettingsMobileNav` + Sidebar `ProjectSettingsSidebarRoot` (`w-[250px]`, `pb-5`) + Inhalt im `ProjectAuthWrapper` (A08 §2.3.5) | `.../projects/[projectId]/layout.tsx` |
| Sidebar-Kopf | Zurück-Pfeil (aria „Back to project“) → `/${ws}/projects/${pid}/issues/`, Text „Project settings“; Logo-Kachel `size-8 rounded bg-layer-2` (`Logo size=20`), Projektname, Rollenname; nur sichtbar mit Projektrolle | `apps/web/components/settings/project/sidebar/header.tsx` |
| Kategorien | Aktiv-Regel: General exakt `…/${pid}/`, sonst Regex `^…/${pid}{href}/`; Links immer mit abschließendem `/` | `apps/web/components/settings/project/sidebar/item-categories.tsx` |

| Kategorie | Tab-Key | Label (EN) | href | Icon (`PROJECT_SETTINGS_ICONS`) | Sidebar-Rolle | Seiten-Prüfung | Inhalt |
|---|---|---|---|---|---|---|---|
| General | `general` | General | `` | `SettingIcon` (web-eigenes Icon) | Admin, Member, Guest | Nicht-Admin: `opacity-60` | 2.11.2 |
| General | `members` | Members | `/members` | `MembersOutline` | Admin, Member, Guest | PRJ Admin/Member **oder** WS-Admin, sonst `NotAuthorizedView isProjectView` | 2.11.3 |
| Features | `features_cycles` | Cycles | `/features/cycles` | `CyclesOutline` | Admin | PRJ-Admin | Toggle `cycle_view` |
| Features | `features_modules` | Modules | `/features/modules` | `ModuleOutline` | Admin | PRJ-Admin | Toggle `module_view` |
| Features | `features_views` | Views | `/features/views` | `ViewsOutline` | Admin | PRJ-Admin | Toggle `issue_views_view` |
| Features | `features_pages` | Pages | `/features/pages` | `PagesOutline` | Admin | PRJ-Admin | Toggle `page_view` |
| Features | `features_intake` | Intake | `/features/intake` | `IntakeOutline` | Admin | PRJ-Admin | Toggle `inbox_view` |
| Work structure | `states` | States | `/states` | `StateOutline` | Admin, Member | PRJ Admin/Member | `SettingsHeading` „States“ / „Define and customize workflow states to track the progress of your work items.“ + `ProjectStateRoot` (`apps/web/components/project-states/*`, nicht A10a) |
| Work structure | `labels` | Labels | `/labels` | `LabelsOutline` | Admin, Member | PRJ Admin/Member | `ProjectSettingsLabelList` (`apps/web/components/labels/*`) mit Auto-Scroll beim Ziehen |
| Work structure | `estimates` | Estimates | `/estimates` | `EstimateOutline` | Admin | PRJ-Admin (sonst `pointer-events-none opacity-60`) | `EstimateRoot` (`apps/web/components/estimates/*`) |
| Execution | `automations` | Automations | `/automations` | `TriggerOutline` | Admin | PRJ-Admin | `SettingsHeading` „Automations“ / „Configure automated actions to streamline your project management workflow and reduce manual tasks.“ + `AutoArchiveAutomation`, `AutoCloseAutomation` (`apps/web/components/automation/*`) → `updateProject` |

Feature-Seiten (`.../features/{cycles|modules|views|pages|intake}/page.tsx`): `SettingsHeading` (Titel/Beschreibung) + `mt-7` `ProjectSettingsFeatureControlItem` (`apps/web/components/settings/project/content/feature-control-item.tsx`): `SettingsBoxedControlItem` mit `Switch size="sm"` → `PATCH` Projekt `{<feature>: !aktuell}` mit `setPromiseToast` (Loading „Updating project feature...“, Erfolg „Success!“/„Project feature updated successfully.“, Fehler „Error!“/„Something went wrong while updating project feature. Please try again.“). Seitentitel „`{Projekt} settings - {Feature}`“.

| Feature | Überschrift / Beschreibung (EN) | Toggle-Titel / -Beschreibung (EN) |
|---|---|---|
| Cycles | „Cycles“ / „Schedule work in flexible periods that adapt to this project's unique rhythm and pace.“ | „Enable cycles“ / „Plan work in focused timeframes.“ |
| Modules | „Modules“ / „Organize work into sub-projects with dedicated leads and assignees.“ | „Enable modules“ / „Project members will be able to create and edit modules.“ |
| Views | „Views“ / „Save custom sorts, filters, and display options or share them with your team.“ | „Enable views“ / „Project members will be able to create and edit views.“ |
| Pages | „Pages“ / „Create and edit free-form content; notes, docs, anything.“ | „Enable pages“ / „Project members will be able to create and edit pages.“ |
| Intake | „Intake“ / „Let non-members share bugs, feedback, and suggestions; without disrupting your workflow.“ | „Enable intake“ / „Let project members create in app intake requests.“ |

Weitere übersetzte, in der CE nicht genutzte Feature-Texte (EE): `project_settings.features.time_tracking.*`, `project_settings.features.milestones.*`, `project_settings.features.intake.{intake_responsibility, intake_sources, notify_assignee, in_app, email, form, toasts.set}` (`packages/i18n/src/locales/en/project-settings.json`).

#### 2.11.2 Projekt „General“ (`ProjectDetailsForm`, `apps/web/components/project/form.tsx`)

| Element | Detail |
|---|---|
| Cover-Bereich | `relative h-44 w-full`, Verlauf `bg-gradient-to-t from-black/50`, `CoverImage` (`h-44 rounded-md`); unten links Logo-Picker (`EmojiPicker iconType="material"`, Button `h-[52px] w-[52px] rounded-lg bg-white/10`, `Logo size=28`; Ergebnis `{in_use: "emoji"\|"icon", emoji:{value} \| icon:{name,color}}`), Name (`text-16 font-semibold`), Zeile „`{IDENTIFIER} .` + Schloss (bei `network===0`) + Netzwerkname“; unten rechts `ImagePickerPopover` „Change cover“ (2.16.5) |
| Felder | „Project name“ (Pflicht „Name is required“, max 255 „Project name should be less than 255 characters“); „Description“ (`TextArea` autoResize, max 8 Zeilen, Placeholder „Enter project description“); „Project ID“ (Eingabe wird auf `A–Z0–9` gefiltert und groß geschrieben; Regeln: Pflicht „Project ID is required“, Regex `/^[ÇŞĞIİÖÜA-Z0-9]+$/` „Only Alphanumeric & Non-latin characters are allowed.“, min 1, max 10 „Project ID must at most be of {max} characters“; Info-Tooltip „Helps you identify work items in the project uniquely. Max 50 characters.“); „Network“ (`Select select-lg` mit `NETWORK_CHOICES`: 0 Private `LockOutline` „Accessible only by invite“, 2 Public `GlobeOutline` „Anyone in the workspace except Guests can join“); „Project Timezone“ (`TimezoneSelect`, Pflicht „Please select a timezone“) |
| Speichern | „Update project“/„Updating“ (disabled für Nicht-Admin) → Cover-Änderung über `handleCoverImageChange(alt, neu, {entityType: PROJECT_COVER, entityIdentifier: projectId})`; bei geändertem Identifier zuerst `GET /api/workspaces/{ws}/project-identifiers?name=` (`checkProjectIdentifierAvailability`, Antwort `{exists}`), belegt → Feldfehler „Identifier already exists“; dann `PATCH` `{name, network, identifier, description, logo_props, timezone[, cover_image*]}`; Toast „Success“/„Project updated successfully“; Fehlercodes `PROJECT_NAME_ALREADY_EXIST` → „The project name is already taken.“, `PROJECT_IDENTIFIER_ALREADY_EXIST` → „The project identifier is already taken.“, `PROJECT_NAME_CANNOT_CONTAIN_SPECIAL_CHARACTERS` → „The project name cannot contain special characters.“, sonst „Something went wrong“ |
| Fußzeile | rechts „Created on {Datum}“ (`text-13 text-placeholder italic`) |
| Loader | `ProjectDetailsFormLoader` (`apps/web/components/project/form-loader.tsx`) solange keine Projektdetails |
| Archivieren/Löschen (nur Admin) | `GeneralProjectSettingsControlSection` (`apps/web/components/project/settings/control-section.tsx`): Doppelkarte `rounded-lg border border-subtle bg-layer-2`; „Archive“ + Text „Archiving a project will unlist your project from your side navigation although you will still be able to access it from your projects page. You can restore the project or delete it whenever you want.“ + `Button secondary sm` „Archive“ → `ArchiveRestoreProjectModal archive`; „Delete“ + „When deleting a project, all of the data and resources within that project will be permanently removed and cannot be recovered.“ + `Button danger-outline sm` „Delete“ → `DeleteProjectModal` |

#### 2.11.3 Projekt „Members“

| Element | Detail | Quelle |
|---|---|---|
| Kopf | `SettingsHeading` „Members“ | `.../members/page.tsx` |
| Defaults (`ProjectSettingsMemberDefaults`) | Zeilen (Titel `text-13 font-medium`, Beschreibung `text-11 text-tertiary`, Control `max-w-48 sm:max-w-64`): „Project Lead“ / „Select the project lead for the project.“ (`MemberSelect select-md clearable`, Clear „None“); „Default Assignee“ / „Select the default assignee for the project.“; „Guest access“ / „This will allow guests to have view access to all the project work items.“ (`Switch` → `{guest_view_all_features}`); nur Admin bearbeitbar; jede Änderung sofort `PATCH {project_lead, default_assignee}` (`"none"` → `null`), Toast „Success!“/„Project updated successfully“; lädt Projektdetails per SWR `PROJECT_DETAILS(ws,pid)` | `apps/web/components/project/project-settings-member-defaults.tsx` |
| Liste (`ProjectMemberList`) | Kopfzeile `border-b py-2`: „Members“ (`text-14 font-semibold`), Suche (Placeholder „Search“, Autofokus; Filter auf `display_name` oder „Vorname Nachname“, case-insensitive), `MemberListFiltersDropdown memberType="project"` (Admin/Member/Guest), „Add member“ (`Button primary sm`, nur PRJ-Admin); Loader `MembersSettingsLoader`; leer „No matching members“ | `apps/web/components/project/member-list.tsx` |
| Tabelle (`ProjectMemberListItem` + `useProjectColumns`) | Spalten „Full name“ (Avatar/Initiale, Link aufs Profil, Hover-„…“ mit `CircleMinus` „Remove“/„Leave“ (danger) für Admin oder eigene Zeile), „Display name“, „Email“ (`text-secondary`), „Account type“, „Joining date“; Kopfzellen sortierbar (`MemberHeaderColumn`) | `apps/web/components/project/member-list-item.tsx`, `apps/web/components/projects/settings/useProjectColumns.tsx`, `apps/web/components/project/settings/member-columns.tsx` |
| Rollenwechsel | editierbar, wenn (aktueller User ist WS-Admin **und** eigene Zeile) oder (aktueller User ist PRJ-Admin, Zielperson kein WS-Admin, nicht eigene Zeile); WS-Gäste dürfen nur „Guest“ werden; `PATCH …/projects/{pid}/members/{id}/ {role}`; Fehler-Toast „You can’t change this role yet.“ + Servertext | `apps/web/components/project/settings/member-columns.tsx` |
| Entfernen/Verlassen | `ConfirmProjectMemberRemove` (`DialogContent size="md"`): selbst → „Leave project?“ / „Are you sure you want to leave the **{Projekt}** project? You will be able to join the project if invited again or if it's public.“ („Leave“/„Leaving...“) → `leaveProject` → Redirect `/${ws}/projects`; Fehler „You can’t leave this project yet.“; andere → „Remove {name}?“ / „Are you sure you want to remove member- **{name}**? They will no longer have access to this project. This action cannot be undone.“ („Remove“/„Removing...“) → `removeMemberFromProject`; Fehler „You can't remove the member from this project yet.“ | `apps/web/components/project/confirm-project-member-remove.tsx`, `member-list-item.tsx` |
| Hinzufügen-Dialog (`SendProjectInvitationModal`) | `DialogContent size="md"`; Titel „Invite members“, Beschreibung „Invite members to work on your project.“; je Zeile `MemberSelect select-lg` (nur WS-Mitglieder, die noch nicht im Projekt sind; Placeholder „Select co-worker“; Pflicht „Please select a member“) + Rollen-`Select pill-md` (`w-32`, Placeholder „Select role“; Auswahl eines Mitglieds setzt Rolle auf dessen WS-Rolle; WS-Admins und -Gäste nur mit ihrer WS-Rolle wählbar; nur Rollen ≤ eigener Projektrolle) + „×“ ab 2 Zeilen; Fuß „+ Add more“, „Cancel“, „Add member“/„Add members“ (+„...“ während Submit); `POST …/projects/{pid}/members/ {members:[{member_id, role}]}` (`bulkAddMembersToProject`), Toast „Success!“/„Members added successfully.“ | `apps/web/components/project/send-project-invitation-modal.tsx` |
| Sortierkopf (`MemberHeaderColumn`) | Menü-Trigger `py-2 text-13 text-secondary hover:text-primary` mit Label, aktivem Sortier-Icon und Chevron; Einträge „A → Z“, „Z → A“ (Datum: „Old → New“, „New → Old“; Rolle: „Guest → Admin“, „Admin → Guest“) mit `SortDescendingOutline`/`SortAscendingOutline`, „Clear sorting“ (`EraserOutline`) bei aktiver Sortierung; setzt `order_by` (`full_name`, `-full_name`, `display_name`, `email`, `joining_date`, `role` jeweils ±) | `apps/web/components/project/member-header-column.tsx`, `packages/constants/src/members.ts` (`MEMBER_PROPERTY_DETAILS`) |

#### 2.11.4 Projekt-Dialoge (auch außerhalb der Einstellungen genutzt)

| Dialog | Größe | Inhalt / Texte | Aktion | Quelle |
|---|---|---|---|---|
| `ArchiveRestoreProjectModal` | `sm` | Titel „Archive {Name}“ / „Restore {Name}“; Text Archiv: „This project and its work items, cycles, modules, and pages will be archived. Its work items won't appear in search. Only project admins can restore the project.“; Restore: „Restoring a project will activate it and make it visible to all members of the project. Are you sure you want to continue?“; „Cancel“, „Archive“/„Archiving“ bzw. „Restore“/„Restoring“ | `archiveProject`/`restoreProject` → Toast „Archive success“/„{Name} has been archived successfully“ bzw. „Restore success“/„You can find {Name} in your projects.“ → Redirect `/${ws}/projects/`; Fehler „Project could not be archived/restored. Please try again.“ | `apps/web/components/project/archive-restore-modal.tsx` |
| `DeleteProjectModal` | `md` | Warn-Icon `p-4 rounded-full bg-danger-subtle`; Titel „Delete project“; Text „Are you sure you want to delete project **{Name}**? All of the data related to the project will be permanently removed. This action cannot be undone“; Feld „Enter the project name **{Name}** to continue:“ (Placeholder „Project name“); Feld „To confirm, type **delete my project** below:“ (Placeholder „Enter 'delete my project'“); „Cancel“, „Delete project“/„Deleting“ (nur bei exakter Eingabe) | `deleteProject`; war man im gelöschten Projekt → `/${ws}/projects`; Toast „Project deleted successfully.“ / „Something went wrong. Please try again later.“ | `apps/web/components/project/delete-project-modal.tsx` |
| `LeaveProjectModal` | `md` | Titel „Leave Project“; Text „Are you sure you want to leave the project - **"{Name}"** ? All of the work items associated with you will become inaccessible.“; Feld Projektname (Placeholder „Enter project name“); Feld „To confirm, type **Leave Project** below:“ (Placeholder „Enter 'leave project'“); „Cancel“, „Leave Project“/„Leaving...“ | Prüfung clientseitig: Name exakt, Bestätigung exakt „Leave Project“, sonst Fehler-Toasts „Please enter the project name as shown in the description.“ / „Please confirm leaving the project by typing the 'Leave Project'.“; **Redirect `/${ws}/projects` vor dem Request**, dann `leaveProject`; Fehler „Something went wrong please try again later.“ | `apps/web/components/project/leave-project-modal.tsx` |
| `JoinProjectModal` | `sm` | Titel „Join Project?“; Text „Are you sure you want to join the project **{Name}**? Please click the 'Join Project' button below to continue.“; „Cancel“, „Join Project“/„Joining...“ | `joinProject` (`POST /api/users/me/workspaces/{ws}/projects/invitations/ {project_ids:[id]}`, `apps/web/services/user.service.ts`) → `/${ws}/projects/${id}/issues`; Fehler nur Konsole | `apps/web/components/project/join-project-modal.tsx` |
| `PublishProjectModal` | `md` | Titel „Publish project“, rechts „Unpublish“/„Unpublishing“ (danger, nur wenn veröffentlicht); Loader 4×30 px; veröffentlicht: Linkbox `rounded-md border-strong` mit `{SPACE_BASE_URL‖origin}{SPACE_BASE_PATH}/issues/{anchor}`, Buttons „Open in new tab“ (`NewTabOutline`) und „Copy link“ (Toast „Published page link copied successfully.“), Status „This project is now live on web“ mit pulsierendem Punkt; Einstellungen: „Views“ (Mehrfach-`Select` List/Kanban, mindestens eines), „Allow comments“, „Allow reactions“, „Allow voting“ (Switches); Fuß-Info `GlobeOutline` „Anyone with the link can access“; „Cancel“ + „Publish“/„Publishing“ bzw. (nur wenn Formular geändert) „Update settings“/„Updating“ | ohne Layout → Fehler-Toast „Please select at least one view layout to publish the project.“; Publish `POST …/projects/{pid}/project-deploy-boards/`; Update `PATCH …/project-deploy-boards/{id}/` (Toast „Publish settings updated successfully!“, schließt); Unpublish `DELETE …/{id}/` (Fehler „Something went wrong while unpublishing the project.“); Defaults `is_comments_enabled/reactions/votes=false`, `view_props {list:true, kanban:true}` (Endpunkte s. A08 §2.7.2) | `apps/web/components/project/publish-project/modal.tsx` |

### 2.12 Projektliste, Projektkarten, Projekt anlegen (`/:ws/projects`, `/:ws/projects/archives`)

#### 2.12.1 Seitenaufbau

| Element | Detail | Quelle |
|---|---|---|
| Layout | `AppHeader header=<ProjectsBaseHeader/> mobileHeader=<ProjectsListMobileHeader/>` (Liste und Archiv identisch) | `apps/web/app/(all)/[workspaceSlug]/(projects)/projects/(list)/layout.tsx`, `.../(detail)/archives/layout.tsx` |
| Daten | `ProjectPageRoot`: SWR `WORKSPACE_PROJECTS_${ws}` → `fetchProjects(ws)` (keine Revalidierung bei Fokus/stale) | `apps/web/components/projects/page.tsx` |
| Header (`ProjectsBaseHeader`) | Breadcrumb „Projects“ (`ProjectsOutline`), im Archiv zusätzlich „Archived“; rechts `ProjectSearch`, ab `md` `HeaderFilters` (Sortierung + Filter), Button „Add Project“ (≥ sm) bzw. „Project“ (< sm) → `toggleCreateProjectModal(true)` – nur WS-Admin/Member und nicht im Archiv | `apps/web/components/project/header.tsx` |
| Mobile-Header | `md:hidden`, `border-b bg-surface-1 py-2`: Sortier-Dropdown (zentriert) + Filter-Dropdown („Filters“ mit Chevron) | `apps/web/components/projects/mobile-header.tsx` |
| Suche (`ProjectSearch`) | wie Sticky-Suche (Lupe → Feld `w-30 md:w-64`, Placeholder „Search“); Filter clientseitig auf Name **oder** Identifier (case-insensitive); Esc leert bzw. klappt zu | `apps/web/components/project/search-projects.tsx`, `apps/web/store/project/project.store.ts` (`filteredProjectIds`) |
| Sortierung (`ProjectOrderByDropdown`) | Trigger `ButtonElement secondary md` mit `SortDescendingOutline` + aktuellem Label; Optionen „Manual“ (`sort_order`), „Name“, „Created date“ (Default), „Number of members“; Separator; „Ascending“/„Descending“ (bei „Manual“ deaktiviert); Wechsel der Option behält die Richtung | `apps/web/components/project/dropdowns/order-by.tsx`, `packages/constants/src/project.ts` (`PROJECT_ORDER_BY_OPTIONS`) |
| Filter-Popover (`ProjectFiltersSelection` in `FiltersDropdown`, `placement="bottom-end"`, Icon `FilterOutline`, Indikator bei aktiven Filtern) | Suchfeld „Search“ (Autofokus außer Mobile); Abschnitte mit einklappbarem Kopf (`FilterHeader`, Titel mit Zähler „(n)“): „My projects“ (Display-Filter `my_projects`); „Access“ (Private/Public mit Netzwerk-Icon); „Lead“ und „Members“ (WS-Mitglieder mit Avatar, eigener Eintrag „You“, Sortierung: gewählte zuerst, dann man selbst, dann alphabetisch; 5 sichtbar, „View all“/„View less“); „Created date“ (Einzelauswahl „Today“, „Yesterday“, „Last 7 days“, „Last 30 days“, „Custom“ → `DateFilterModal` „Created date“); leer „No matches found“ | `apps/web/components/project/dropdowns/filters/*.tsx`, `packages/constants/src/filter.ts` (`PROJECT_CREATED_AT_FILTER_OPTIONS`) |
| Angewandte Filter (`ProjectAppliedFiltersList`) | `Header variant=TERNARY`; je Filter Gruppe `min-h-9 rounded-md border border-subtle p-1.5 text-11 capitalize` mit Feldname (Unterstriche → Leerzeichen) und Chips (`rounded-sm bg-layer-1 px-1.5 py-1 text-11`, „×“ je Wert, „×“ für Gruppe); Display-Filter-Gruppe „Projects“ („My projects“; „Archived“ wird ausgeblendet); „Clear all ×“; rechts Zähler `rounded-full bg-layer-1 px-2.5 py-1` „gefiltert/gesamt“ mit Tooltip „{n} of {m} projects match the applied filters.“ | `apps/web/components/project/applied-filters/*.tsx`, `apps/web/components/project/root.tsx` |
| Liste (`ProjectCardList`) | Loader `ProjectsLoader` (2.16.3) bis `fetchStatus === "complete"`; keine Projekte (und nicht Archiv) → `EmptyStateDetailed assetKey="project"` „No active projects“ / „Think of each project as the parent for goal-oriented work. …“, Button „Start your first project“ (disabled für Guest); gefiltert leer → im Archiv ohne Filter „No projects archived“ / „Looks like all your projects are still active—great job!“ (`assetKey="archived-work-item"`), sonst „No matching results.“ / „No results found. Try adjusting your search terms.“ (`assetKey="search"`); Raster `grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3` | `apps/web/components/project/card-list.tsx` |
| Seitentitel | „`{ws} - Projects`“ | `apps/web/components/project/root.tsx` |

#### 2.12.2 Projektkarte (`ProjectCard`, `apps/web/components/project/card.tsx`)

| Teil | Detail |
|---|---|
| Rahmen | `Link` auf `/${ws}/projects/${id}/issues`, `group/project-card flex flex-col overflow-hidden rounded-lg border border-subtle bg-layer-2 transition-all duration-300 hover:border-strong hover:shadow-raised-200`; Klick als Nicht-Mitglied → `JoinProjectModal` statt Navigation; Klick im Archiv → keine Aktion |
| Kopf | `h-[118px]`, Cover + Verlauf `from-black/60`; unten Logo-Kachel `h-9 w-9 rounded-sm bg-white/10` (`Logo size=18`), Name (`font-semibold text-on-color`), Identifier (`text-11`) + Schloss bei privat; rechts (nicht archiviert) „Copy link“ (`h-6 w-6 bg-white/10`, Toast `info` „Link Copied!“/„Project link copied to clipboard.“) und `FavoriteStar` (nur WS-Admin/Member) |
| Fuß | `h-[104px] p-4`: Beschreibung (`line-clamp-2 text-13 text-tertiary`) oder „Created on {Datum}“; links `AvatarGroup size="xs" max=2` (Tooltip „Members: n“ bzw. „No members“) oder „No Member Yet“ (kursiv), im Archiv zusätzlich „Archived“; rechts: Archiv+Admin → „Restore“ (ghost xs, `RestoreOutline`) + Löschen-Icon; Mitglied Admin/Member → Zahnrad-Link zu den Projekteinstellungen; Mitglied Guest → „✓ Joined“; Nicht-Mitglied → „Join“ (ghost sm) |
| Kontextmenü (Rechtsklick, `ContextMenu` aus `@plane/blocks`) | „Settings“ (nicht archiviert, Admin/Member), „Join“ (Nicht-Mitglied), „Open in new tab“ (Nicht-Mitglied), „Copy link“ (nicht archiviert), „Restore“ (archiviert, Admin), „Delete“ (archiviert, Admin) |
| Favorit | `addProjectToFavorites`/`removeProjectFromFavorites` mit Promise-Toast („Adding project to favorites...“ → „Project added to favorites.“ / „Couldn't add the project to favorites. Please try again.“; „Removing project from favorites...“ → „Project removed from favorites.“ / „Couldn't remove the project from favorites. Please try again.“); nach Hinzufügen wird die Favoriten-Sektion der Sidebar geöffnet (`localStorage.is_favorite_menu_open = true`) |

#### 2.12.3 Dialog „Projekt anlegen“ (`CreateProjectModal`, `apps/web/components/project/create-project-modal.tsx`)

| Schritt | Inhalt | Quelle |
|---|---|---|
| Dialog | `DialogContent size="lg"`, Außenklick schließt **nicht** (`disablePointerDismissal`), Esc schließt; beim Öffnen immer Schritt 1 | `create-project-modal.tsx` |
| Schritt 1 Kopf | Cover `h-44 rounded-lg` (zufälliges Default-Cover `getRandomCoverImage()`), „×“ oben rechts (`CloseOutline h-5 w-5 text-on-color`), „Change cover“ (`ImagePickerPopover`, 2.16.5) unten rechts, Logo-Picker unten links überlappend (`-bottom-[22px] left-3`, Kachel `h-11 w-11 rounded-md border bg-layer-2`, Default zufälliges Emoji aus `RANDOM_EMOJI_CODES`) | `apps/web/components/project/create/header.tsx`, `apps/web/components/projects/create/utils.ts` |
| Schritt 1 Felder | Raster `md:grid-cols-4`: Name (`col-span-3`, Placeholder „Project name“, Pflicht, max 255 „Title should be less than 255 characters“); Project ID (Placeholder „Project ID“, Info-Tooltip; **automatisch** aus dem Namen erzeugt: `projectIdentifierSanitizer(name).substring(0,10)` bis der Nutzer die ID selbst editiert; erlaubte Zeichen `ÇŞĞIİÖÜA-Za-z0-9`, max 10, Großschreibung beim Speichern); Beschreibung (`col-span-4`, Textarea); darunter Pills: Netzwerk (`Select pill-md`, Default Public=2) und Lead (`MemberSelect pill-md`, erneute Wahl desselben entfernt) | `apps/web/components/project/create/common-attributes.tsx`, `apps/web/components/projects/create/attributes.tsx` |
| Schritt 1 Fuß | `border-t py-4`: „Cancel“, „Create project“/„Creating“; Tab-Reihenfolge aus `ETabIndices.PROJECT_CREATE` (`packages/constants/src/tab-indices.ts`) | `apps/web/components/project/create/project-create-buttons.tsx` |
| Speichern | Cover-Typ `local_static` → vorab Upload (`uploadCoverImage`, Asset-Typ `PROJECT_COVER`); sonst `cover_image = url`, `cover_image_asset = null`; `POST /api/workspaces/{ws}/projects/`; danach ggf. Asset-Status-Update (`updateBulkProjectAssetsUploadStatus`) und `PATCH {cover_image_url}`; Toast „Success“/„Project created successfully“; optional Favorit (`setToFavorite`); Fehlercodes wie in 2.11.2 | `apps/web/components/projects/create/root.tsx` |
| Schritt 2 „Features“ | `ProjectFeatureUpdate`: Liste `ProjectFeaturesList` mit `SettingsHeading` `projects_and_issues`/`projects_and_issues_description` und fünf `SettingsBoxedControlItem` (Titel `t(key)`, Beschreibung `t("{key}_description")`, `Switch` → Promise-Toast „Updating project feature...“) für cycles, modules, views, pages, intake; Fußzeile „Congrats! {Logo} {Name} created.“ (`congrats`, `created`), „Close“, „Open project“ (Link `/${ws}/projects/${id}/issues`) | `apps/web/components/project/project-feature-update.tsx`, `apps/web/components/project/settings/features-list.tsx`, `apps/web/components/project/settings/helper.tsx` |

Weitere Komponenten dieses Ordners: `ProjectMultiSelectModal` (`apps/web/components/project/multi-select-modal.tsx`, Dialog `sm` mit Combobox-Suche „Search for projects“, Leerzustand `workspace_projects.empty_state.filter.title`, „Cancel“/„Confirm“) – **nicht eingebunden**; `IntegrationCard` (`apps/web/components/project/integration-card.tsx`) – **nicht eingebunden**; `EmptyState` (`apps/web/components/project/empty-state.tsx`, Duplikat von `common/empty-state.tsx` mit absoluter Positionierung) – **nicht eingebunden**; `ProjectInboxHeader` (`apps/web/components/projects/settings/intake/header.tsx`, Header der Intake-Seite: Breadcrumb Projekt → „Intake“, „Syncing...“-Indikator bei `pagination-loading`, „Add work item“ → `InboxIssueCreateModalRoot`, A09).

### 2.13 Profil-/Account-Einstellungen (Route `/settings/profile/:tab` **und** Modal)

#### 2.13.1 Zwei Darstellungsformen

| Form | Aufruf | Aufbau | Quelle |
|---|---|---|---|
| Seite | `/settings/profile/{general\|preferences\|notifications\|security\|api-tokens}` (Redirects von `/profile/*` und `/:ws/settings/account/*`, A08 §2.2.8) | Layout: `ProjectsAppPowerKProvider`, `AuthenticationWrapper`, `bg-canvas p-2`, Karte `rounded-lg border border-subtle bg-surface-1`; Sidebar `w-[250px]` + Inhalt `mx-auto w-fit max-w-225 grow px-page-x py-20`; Tab-Wechsel per `router.push`; ungültiger Tab oder fehlender User → Dauer-`LogoSpinner`; Titel „Profile - General settings“ | `apps/web/app/(all)/settings/profile/layout.tsx`, `.../[profileTabId]/page.tsx` |
| Modal | User-Menü „Settings“/„Preferences“ (2.2); `commandPalette.profileSettingsModal {isOpen, activeTab}` | `ProfileSettingsModal` (lazy über `GlobalModals` im Workspace-Layout): `DialogContent size="xl" height="fixed"`, Schließen-Button (`IconButton tertiary sm`), unsichtbarer Titel „Profile settings“, Sidebar `w-[250px] rounded-l-xl` + Inhalt `flex-1 rounded-r-xl`; Tab-Wechsel nur im Store; Schließen setzt `activeTab` nach 300 ms auf `null` | `apps/web/components/settings/profile/modal.tsx`, `apps/web/components/common/modal/global.tsx` |

Sidebar (`ProfileSettingsSidebarRoot`, `apps/web/components/settings/profile/sidebar/*`): `border-r bg-surface-2 px-3 py-4`; Kopf mit `Avatar size="lg"`, Name (`text-body-sm-medium`), E-Mail (`text-caption-md-regular`); Kategorien „Your profile“: Profile (`UserOutline`, Key `general`), Preferences (`SettingsOutline`), Notifications (`SubscribeOutline`), Security (`LockOutline`); „Developer“: Personal Access Tokens (`KeyOutline`, Key `api-tokens`). **Nur auf der Seite** (Param `profileTabId` vorhanden) zusätzlich Kategorie „Workspace“ mit allen Workspaces (Link `/${slug}/`, `WorkspaceLogo`), „Create workspace“ (`/create-workspace/`) und „Workspace invites“ (`/invitations/`). Inhalt (`ProfileSettingsContent`): `ScrollArea`, `px-8 py-9`, Tab-Komponenten lazy (`PROFILE_SETTINGS_PAGES_MAP`, `apps/web/components/settings/profile/content/pages/index.ts`). Überschriften `ProfileSettingsHeading` (`text-h6-medium`, Beschreibung `text-body-xs-regular text-tertiary`).

#### 2.13.2 Tab „Profile“ (`GeneralProfileSettingsForm`, `.../content/pages/general/form.tsx`)

| Element | Detail |
|---|---|
| Cover | `h-44 rounded-lg` `CoverImage`; rechts unten `ImagePickerPopover` „Change cover“ (`isProfileCover`, 2.16.5) |
| Avatar | überlappend `absolute -bottom-6 left-6`, Kachel `h-16 w-16 rounded-lg bg-surface-2`: Bild oder `UserOutline` → `UserImageUploadModal` (2.16.5); Upload-Erfolg setzt `avatar_url` und **speichert das Formular sofort**; Entfernen → `PATCH /api/users/me/ {avatar_url:""}`, Toast „Profile picture deleted successfully.“ / „There was some error in deleting your profile picture. Please try again.“ |
| Kopfzeile | „Vorname Nachname“ (`text-16 font-medium text-secondary`), E-Mail (`text-13 text-tertiary`) |
| Felder (Raster `sm:grid-cols-2 xl:grid-cols-3`) | „First name *“ (Pflicht „Please enter first name“, `validatePersonName`, max 50, Placeholder „Enter your first name“); „Last name“ (`validatePersonName`, max 50); „Display name *“ (Pflicht „Display name is required.“, `validateDisplayName`, max 50); „Email *“ (disabled) + bei `config.is_smtp_configured` Link „Change email“ (`text-11 underline`) |
| Speichern | „Save changes“/„Saving“ (`Button primary sm`) → `PATCH /api/users/me/ {first_name, last_name, avatar_url, display_name[, cover_image…]}` (Cover über `handleCoverImageChange`, Asset-Typ `USER_COVER`, `isUserAsset`) und – nur wenn geändert – `PATCH` Profil `{role}` (Default-Rolle „Product / Project Manager“); Promise-Toast „Updating...“ → „Profile updated successfully.“ / „There was some error in updating your profile. Please try again.“ |
| Deaktivieren | `mt-10` Boxed-Item „Deactivate account“ / „When deactivating an account, all of the data and resources within that account will be permanently removed and cannot be recovered.“ + `danger-outline` Button → `DeactivateAccountModal` (`ConfirmDialog` „Deactivate your account“ / „Once deactivated, you can't be assigned work items and be billed for your workspace. To reactivate your account, you will need an invite to a workspace at this email address.“, „Confirm“/„Deactivating“) → `deactivateAccount()` (`DELETE /api/users/me/`) → Toast „Account deactivated successfully.“ → `signOut()` → `/`; Fehler-Toast mit `err.error` (`apps/web/components/account/deactivate-account-modal.tsx`) |
| E-Mail ändern (`ChangeEmailModal`, `apps/web/components/core/modals/change-email-modal.tsx`) | `DialogContent size="md"`, Titel „Change email“, Beschreibung „Enter a new email address to receive a verification link.“; Schritt 1: E-Mail (Placeholder „Enter your email“, Pflicht „Email is required“, Regex „Email is invalid“) → CSRF holen → `checkEmail` (`existing` → „Email already exists. Please use a different one.“) → `generateEmailCode` → Schritt 2; Schritt 2: Label „New email“ (disabled) + „Unique code“ (Placeholder „123456“, Autofokus, Hilfe grün „Verification code sent to your new email.“, Pflicht „Unique code is required“) → `verifyEmailCode` → Toast „Success!“/„Email updated successfully. Please sign in again.“ → **Sign-out**; Fehler „Invalid verification code. Please try again.“; Auth-Fehlercodes über `authErrorHandler`, Fallback „Email validation failed. Please try again.“; Buttons „Cancel“, „Continue“/„Confirm“/„Sending“ |

#### 2.13.3 Tab „Preferences“ (`PreferencesProfileSettings`, `.../content/pages/preferences/*`)

| Zeile (`SettingsControlItem`) | Control | Speichern / Verhalten |
|---|---|---|
| Überschrift | „Preferences“ / „Customize your app experience the way you work“ | – |
| „Theme“ / „Select or customize your interface color scheme.“ | `ThemeSwitch` (`apps/web/components/core/theme/theme-switch.tsx`): `Select select-md w-42` mit `THEME_OPTIONS` (`packages/constants/src/themes.ts`: „System Preference“ `system`, „Light“ `light`, „Dark“ `dark`, „Light high contrast“ `light-contrast`, „Dark high contrast“ `dark-contrast`, „Custom theme“ `custom`; Icon = halbierter Kreis `h-4 w-4 rotate-45` mit `color1`/`color2`/`border`), Placeholder „Select your theme“ | `ThemeSwitcher` (`apps/web/components/appearance/theme-switcher.tsx`): `setTheme(value)`; bei „custom“ mit gespeicherten Farben sofort `applyCustomTheme(primary, background, dark\|light)`; Promise-Toast „Updating theme...“ → „Theme updated“/„Reloading to apply changes...“ → **`window.location.reload()`**; Fehler „Failed to update theme. Please try again.“ |
| Custom-Theme-Formular (nur wenn gespeichertes Theme `custom`) | `CustomThemeSelector` (`apps/web/components/core/theme/custom-theme-selector.tsx`): Karte `rounded-lg border bg-layer-1 px-4 py-3`; Kopf „Customize your theme“ + „Import config“ (verstecktes `input type=file accept=.json`); „Choose color mode *“ Radio „Light mode“/„Dark mode“ (`darkPalette`); „Neutral color *“ (Default `#1a1a1a`) und „Brand color *“ (Default `#3f76ff`) als `InputColorPicker` (Hex-Feld mit Swatch-Button = nativer Farbdialog; Regex `^#([A-Fa-f0-9]{6}\|[A-Fa-f0-9]{3})$` „Enter a valid hex code“; fehlendes `#` wird ergänzt); Fuß „Set theme“ („Saving“/„Generating“) + „Download config“ | Speichern → `applyCustomTheme` → `PATCH` Profil-Theme `{theme:"custom", primary, background, darkPalette}` → Toast „Reloading to apply changes...“ → Reload nach 1500 ms; Download → Datei `plane-theme-{timestamp}.json` `{version:"1.0", themeName:"Custom Theme", primary, background, darkPalette}`; Import validiert Pflichtfelder, Hex-Format, Boolean-Modus, wendet direkt an; Fehlertexte „Missing required fields: primary and background“, „Invalid brand color hex format“, „Invalid neutral color hex format“, „Invalid theme mode. Must be a boolean“ (Algorithmus A13a §3.3) |
| Abschnitt „Language & Time“ | – | – |
| „Timezone“ / „Current timezone setting.“ | `TimezoneSelect` (2.16.9), Fallback `Asia/Kolkata` | `PATCH /api/users/me/ {user_timezone}`, Toast „Timezone updated successfully“ / „Failed to update timezone“ |
| „Language“ / „Choose the language used in the user interface.“ | `Select select-md w-42` mit `SUPPORTED_LANGUAGES` (22 Sprachen, A13b §2.1.3), Placeholder „Select a language“ | `PATCH` Profil `{language}` → `setLanguage()`; Toast „Language updated successfully“ / „Failed to update language“ |
| „First day of the week“ / „This will change how all calendars in your app look.“ | `StartOfWeekPreference` (`apps/web/components/profile/start-of-week-preference.tsx`): `Select select-md w-42` mit `START_OF_THE_WEEK_OPTIONS` (Sunday…Saturday, `EStartOfTheWeek` 0–6), Popup bündig rechts | `PATCH` Profil `{start_of_the_week}`; Toast „First day of the week updated successfully“ / „Update failed“ „Please try again later.“ |

#### 2.13.4 Tab „Notifications“ (`NotificationsProfileSettings`)

Überschrift „Email notifications“ / „Stay in the loop on Work items you are subscribed to. Enable this to get notified.“; Daten SWR `CURRENT_USER_EMAIL_NOTIFICATION_SETTINGS` → `GET /api/users/me/notification-preferences/` (Loader `EmailSettingsLoader`); jede Switch-Änderung sofort `PATCH {<key>: bool}`, Toast „Success“/„Email notification setting updated successfully“ bzw. „Failed to update email notification setting“.

| Key | Titel | Beschreibung |
|---|---|---|
| `property_change` | Property changes | Notify me when work items' properties like assignees, priority, estimates or anything else changes. |
| `state_change` | State change | Notify me when the work items moves to a different state |
| `issue_completed` (eingerückt `border-l-3 border-subtle-1 pl-3`) | Work item completed | Notify me only when a work item is completed |
| `comment` | Comments | Notify me when someone leaves a comment on the work item |
| `mention` | Mentions | Notify me only when someone mentions me in the comments or description |

Quelle: `apps/web/components/settings/profile/content/pages/notifications/*`, Endpunkt in `apps/web/services/user.service.ts` (A08 §2.7.2).

#### 2.13.5 Tab „Security“ (`SecurityProfileSettings`, `.../content/pages/security.tsx`)

| Element | Detail |
|---|---|
| Überschrift | „Change password“ |
| Felder | „Current password“ (nur wenn **nicht** `is_password_autoset`; Pflicht; Placeholder „Old password“), „New password“ (Placeholder „Enter new password“; darunter `PasswordStrengthIndicator`, solange nicht stark), „Confirm password“; je Feld Auge-Toggle (`ShowOutline`/`HideOutline`); Fehler „Passwords don't match“ (erst wenn Bestätigung mindestens so lang wie Passwort oder Feld verlassen), „New password must be different from old password“ |
| Button | `Button primary lg` „Change password“/„Changing password“; disabled bis Stärke gültig, Pflichtfelder gefüllt, Passwörter gleich und neu ≠ alt |
| Ablauf | CSRF-Token (`GET /auth/get-csrf-token/`) → `changePassword(csrf, {old_password?, new_password})` (`POST /auth/change-password/`, A06) → Formular-Reset, Toast `auth.common.password.toast.change_password.success.*`; Fehlercode → `authErrorHandler` Titel/Text, bei Passwort-Codes zusätzlich Feldfehler |

#### 2.13.6 Tab „Personal Access Tokens“ (`APITokensProfileSettings`, `.../content/pages/api-tokens.tsx`)

Überschrift „Personal Access Tokens“ / „Generate secure API tokens to integrate your data with external systems and applications.“, Button „Add access token“ → `CreateApiTokenModal`; Liste `ApiTokenListItem` (beide `apps/web/components/api-token/*`, nicht A10a); Leerzustand `EmptyStateCompact assetKey="token"` „No Personal token yet“ / „Generate secure API tokens to connect your workspace with external systems and applications.“ + Aktion „Add access token“; Daten SWR `API_TOKENS_LIST` → `GET /api/users/api-tokens/` (`APITokenService.list`); Loader `APITokenSettingsLoader`.

### 2.14 Auth-Screens (Sign-in, Sign-up, Magic-Code, Passwort, Reset, Fehler-/Zugriffs-Screens)

Routen und Guards: A08 §2.2.1; serverseitige Auth-Flows (Formular-POST, Redirect mit `error_code`): A06.

#### 2.14.1 Rahmen (`AuthBase`, `apps/web/components/auth-screens/auth-base.tsx`)

| Teil | Detail | Quelle |
|---|---|---|
| Container | `relative z-10 flex h-screen w-screen flex-col items-center overflow-hidden overflow-y-auto px-8 pt-6 pb-10` | `auth-base.tsx` |
| Kopf (`AuthHeader`/`AuthHeaderBase`) | sticky; links `PlaneLockup` (`height=20 width=95`, Link `/`), rechts – nur bei `config.enable_signup` – „New to Plane? **Sign up**“ (Sign-in-Seite, Link `/sign-up`) bzw. „Already have an account? **Sign in**“ (Sign-up-Seite, Link `/sign-in` → Redirect `/`); Seitentitel **vertauscht**: Sign-in-Seite „Sign up - Plane“, Sign-up-Seite „Sign in - Plane“ (`authContentMap.pageTitle`) | `apps/web/components/auth-screens/header.tsx` |
| Fuß (`AuthFooter`) | „Join 10,000+ teams building with Plane“ (`text-13 text-tertiary`) + Logos Zerodha (`text-[#387ED1]`), Sony, Dolby, Accenture (`h-7`, Dark: `text-on-color`) → **Marketing; für die eigene Plattform entfernen/konfigurierbar (ADR-004/005 abwägen)** | `apps/web/components/auth-screens/footer.tsx` |
| Formularbereich (`AuthRoot` → `AuthContainer`) | `mt-10 flex w-full flex-grow flex-col items-center justify-center py-6`, innen `max-w-[22.5rem] flex-col gap-6`; Reihenfolge: Fehler-Banner (`Banner variant="accent" placement="inline"`, schließbar), Überschrift, OAuth-Buttons, E-Mail-Formular, `TermsAndConditions` | `apps/web/components/account/auth-forms/auth-root.tsx` |
| Überschrift | `text-h4-semibold`: „Work in all dimensions.“ + `text-placeholder` „Welcome back to Plane.“ (Sign-in) bzw. „Create your Plane account.“ (Sign-up); mit Einladung (`?invitation_id&slug`, E-Mail stimmt überein) „Join {WorkspaceLogo size-9} {Name}“ + „Log in to start managing work with your team.“/„Create an account to start managing work with your team.“ (Einladung per `GET /api/workspaces/{slug}/invitations/{id}/join/`, Spinner während Laden) | `apps/web/components/account/auth-forms/auth-header.tsx` |
| Keine Methode aktiv | „No authentication methods available“ / „Please contact your administrator to enable authentication for your instance.“ | `auth-root.tsx` |
| OAuth (`OAuthOptions` aus `@plane/blocks/auth`) | Buttons „Sign in with Google/GitHub/GitLab/Gitea“ bzw. „Sign up with …“ je `config.is_<provider>_enabled`; Klick → `window.location.assign(API_BASE_URL + /auth/<provider>/[?next_path=…])`; GitHub-Logo je Theme; kompakt im Passwort-Schritt; Trenner nur, wenn E-Mail-Login aktiv | `apps/web/hooks/oauth/core.tsx`, `auth-root.tsx` |
| AGB-Hinweis | „By signing in\|By creating an account, you understand and agree to \n our **Terms of Service** and **Privacy Policy**.“ (Links `https://plane.so/legals/terms-and-conditions`, `https://plane.so/legals/privacy-policy`, neuer Tab) → **Links konfigurierbar machen (Airgap)** | `apps/web/components/account/terms-and-conditions.tsx` |

#### 2.14.2 Schritte (`AuthFormRoot`, `apps/web/components/account/auth-forms/form-root.tsx`)

| Schritt | UI | Ablauf |
|---|---|---|
| EMAIL (`AuthEmailForm`, `email.tsx`) | Label „Email“, `Input 2xl` (Placeholder „name@company.com“, Autofokus), Clear-Button `CloseCircleOutline` (aria `aria_labels.auth_forms.clear_email`); Fehler „Email is invalid“ (`WarningCircleOutline`, erst nach Blur); Button „Continue“ (`primary lg full`, disabled bei leer/ungültig/sendend) | `POST /auth/email-check/ {email}` (A06) → Antwort `{existing, status: "MAGIC_CODE"\|"CREDENTIAL"}`: `existing` und Modus Sign-up → Modus Sign-in (und umgekehrt); `MAGIC_CODE` → Schritt UNIQUE_CODE + Code anfordern; `CREDENTIAL` → Schritt PASSWORD; Fehlercode → Banner/Toast via `authErrorHandler` |
| PASSWORD (`AuthPasswordForm`, `password.tsx`) | E-Mail (disabled) mit Clear (zurück zu EMAIL, Route `/` bzw. `/sign-up`); „Password“ bzw. „Set a password“ (Sign-up), Placeholder „Enter password“, Auge-Toggle; Sign-in: Link „Forgot your password?“ → `/accounts/forgot-password?email=…` (SMTP aktiv) bzw. `ForgotPasswordPopover` (🤥 „We see that your god hasn't enabled SMTP, we will not be able to send a password reset link“); Sign-up: Stärke-Anzeige (`PasswordStrengthIndicator`) + „Confirm password“ mit „Passwords don't match“; Buttons Sign-in „Continue“ (SMTP) bzw. „Go to workspace“ + optional „Sign in with unique code“ (secondary); Sign-up „Create account“ | echtes HTML-Formular `POST {API_BASE_URL}/auth/sign-in/` bzw. `/auth/sign-up/` mit Hidden-Feldern `csrfmiddlewaretoken` (vorab `GET /auth/get-csrf-token/`), `email`, `next_path`; Sign-up mit schwachem Passwort → Banner danger „Try setting-up a strong password to proceed“ statt Submit; „Sign in with unique code“ → Code anfordern + Schritt UNIQUE_CODE |
| UNIQUE_CODE (`AuthUniqueCodeForm`, `unique-code.tsx`) | E-Mail (disabled) mit Clear; „Unique code“ (Placeholder „123456“, Autofokus); Zeile darunter grün „Paste the code sent to your email“ (`TickCircleOutline`) und rechts „Resend“ / „Resend in {n} seconds“ (Timer 5 s nach Anforderung) / „Requesting new code“; Button „Continue“ bzw. „Sending code“ | Code anfordern `POST /auth/magic-generate/ {email}` **nur wenn SMTP konfiguriert**; Submit als HTML-Formular `POST /auth/magic-sign-in/` bzw. `/auth/magic-sign-up/` (Felder `csrfmiddlewaretoken`, `email`, `code`, `next_path`) |
| Fehler-Rückkehr | Query `error_code`: `AUTHENTICATION_FAILED_SIGN_UP\|SIGN_IN` → Modus + PASSWORD; `INVALID_MAGIC_CODE_*`, `INVALID_EMAIL_MAGIC_*`, `EXPIRED_MAGIC_CODE_*`, `EMAIL_CODE_ATTEMPT_EXHAUSTED_*` → Modus + UNIQUE_CODE; Banner-Text aus `authErrorHandler` (Codes A08/A06); E-Mail aus Query `email` vorbelegt | `auth-root.tsx`, `apps/web/helpers/authentication.helper.tsx` |

#### 2.14.3 Passwort vergessen / zurücksetzen / setzen

| Formular | Seite | UI | Ablauf | Quelle |
|---|---|---|---|---|
| `ForgotPasswordForm` | `/accounts/forgot-password` | Kopf `AuthFormHeader` „Reset password“ / „Regain access to your account.“ (`text-20 font-semibold`, zweite Zeile `text-placeholder`); „Email“ (Pflicht „Email is required“, Gültigkeit „Email is invalid“, vorbelegt aus `?email`); nach Versand grüner Hinweis „We sent the reset link to your email address“; Button „Send reset link“ / „Resend in {n} seconds“ (30 s, Feld gesperrt); Link-Button „Back to sign in“ → `/` | `POST /auth/forgot-password/ {email}` (`sendResetPasswordLink`); Toast „Email sent“ / „Check your inbox for a link to reset your password. If it doesn't appear within a few minutes, check your spam folder.“; Fehler „Error!“ + Servertext | `apps/web/components/account/auth-forms/forgot-password.tsx` |
| `ResetPasswordForm` | `/accounts/reset-password?uidb64&token&email[&error_code]` **und** `/accounts/set-password` | „Reset password“ / „Create a new password.“; optional Fehler-Banner; „Email“ (disabled), „Password“ (`minLength 8`, Stärke-Anzeige immer), „Confirm password“; Button „Set password“ (disabled bis stark und gleich) | HTML-Formular `POST /auth/reset-password/{uidb64}/{token}/` mit CSRF; auf `/accounts/set-password` fehlen `uidb64`/`token` → Ziel `/auth/reset-password/null/null/` (Edge-Case, s. 3.10) | `apps/web/components/account/auth-forms/reset-password.tsx`, `apps/web/app/(all)/accounts/set-password/page.tsx` |
| `SetPasswordForm` | **nicht eingebunden** | „Set password“ / „Create a new password.“; E-Mail des Users; Submit `handleSetPassword(csrf, {password})` → `/` | – | `apps/web/components/account/auth-forms/set-password.tsx` |
| `FormContainer`, `AuthFormHeader` | – | Container wie `AuthContainer`; Überschrift zweizeilig `text-20` | – | `apps/web/components/account/auth-forms/common/*` |

#### 2.14.4 Fehler- und Zugriffs-Screens

| Komponente | Inhalt | Verwendung | Quelle |
|---|---|---|---|
| `NotAuthorizedView` | `DefaultLayout`, Bild `h-[176px] w-[288px]` (Settings: `@/app/assets/auth/project-not-authorized.svg` bzw. `workspace-not-authorized.svg`; sonst `unauthorized.svg`), „Oops! You are not authorized to view this page“ (`text-18 font-medium`), optional Action-Button | Settings-Seiten ohne Recht (`section="settings"`, `isProjectView`), Workspace-Wrapper | `apps/web/components/auth-screens/not-authorized-view.tsx` |
| `ProjectAccessRestriction` | Status 409 oder (403 und WS-Admin) → `EmptyStateDetailed assetKey="no-access"` „Seems like you don’t have access to this Project“ / „Click the button below to join it.“ + „Join project“/„Joining project“; 403 sonst → gleicher Titel / „Contact admin to request for access and you can continue here.“; sonst „Project not found“ / „The project you are looking for does not exist.“ (`assetKey="project"`) | `ProjectAuthWrapper` (A08 §2.3.5) | `apps/web/components/auth-screens/project/project-access-restriction.tsx` |
| `NotAWorkspaceMember` | „Not Authorized!“ / „You're not a member of this workspace. Please contact the workspace admin to get an invitation or check your pending invitations.“ + „Check pending invites“ (`/invitations`) und „Create new workspace“ (`/create-workspace`) | **nicht eingebunden** | `apps/web/components/auth-screens/workspace/not-a-member.tsx` |
| Instanz-Screens | s. 2.16.8 (`InstanceNotReady`, `MaintenanceView`, `MaintenanceMessage`) | `InstanceWrapper` | `apps/web/components/instance/*` |

### 2.15 Onboarding (`/onboarding`), Workspace anlegen (`/create-workspace`), Produkt-Tour

#### 2.15.1 Rahmen (`apps/web/app/(all)/onboarding/page.tsx`, `apps/web/components/onboarding/root.tsx`)

| Teil | Detail |
|---|---|
| Seite | `AuthenticationWrapper pageType=ONBOARDING`; `bg-canvas p-2`, Karte `shadow-md rounded-lg border border-subtle bg-surface-1`; lädt Workspaces (SWR `USER_WORKSPACES_LIST`) und Einladungen (SWR `USER_WORKSPACE_INVITATIONS_LIST_${userId}` → `GET /api/users/me/workspaces/invitations/`); bis beides da ist `LogoSpinner` |
| Kopf (`OnboardingHeader`, `header.tsx`) | sticky; Fortschrittsbalken `h-1.5 rounded-t-lg bg-surface-1` mit Füllung `bg-accent-primary transition-all duration-700 ease-out` (Breite = Schritt/Anzahl, Tooltip „n/m“ unten rechts); darunter links Zurück-Chevron (`ChevronLeftOutline size-6`, nicht bei Profil und Einladen) + `PlaneLockup 95×20`, rechts `SwitchAccountDropdown` |
| Inhalt (`OnboardingStepRoot`, `steps/root.tsx`) | scrollt bei Schrittwechsel smooth nach oben; zentriert `p-8`, Breite `max-w-[24rem]`; Überschriften `CommonOnboardingHeader` (`text-h4-semibold` + `text-body-md-regular text-tertiary`) |
| Konto wechseln | Dropdown-Trigger `rounded-lg bg-layer-1 px-2 py-1.5` mit `Avatar sm` + Name (Vorname Nachname, sonst Anzeigename, sonst E-Mail); Eintrag (danger) „Wrong e-mail address?“ → `SwitchAccountModal` (`ConfirmDialog variant="primary"` „Switch account“, Text „If you have signed up via **{email}** un-intentionally, you can switch your account to a different one from here.“, Button „Switch account“/„Switching...“) → `signOut()`, `setTheme("system")`, `/`; Fehler „Failed to sign out. Please try again.“ (`switch-account-dropdown.tsx`, `switch-account-modal.tsx`) |

#### 2.15.2 Schritte (`EOnboardingSteps`)

| # | Schritt | Komponente / Datei | UI (EN) | Speichern / Weiter |
|---|---|---|---|---|
| 1 | `PROFILE_SETUP` | `ProfileSetupStep`, `steps/profile/root.tsx` | „Create your profile.“ / „This is how you will appear in Plane.“; Avatar-Kreis `size-12 rounded-full bg-accent-primary` (Initiale, Fallback „R“) + „Upload image“/„Change image“ (`ImageOutline`) → `UserImageUploadModal` (2.16.5); Feld „Name *“ (natives `input`, `focus:ring-2 focus:ring-accent-strong`, Placeholder „Enter your full name“, Pflicht „Name is required“, max 50 „Name must be within 50 characters.“, `validatePersonName`, Autofokus; schreibt **nur** `first_name`); bei `is_password_autoset` aufklappbarer Block „🔒 Set a password (Optional)“ (`SetPasswordRoot`, `bg-surface-2 rounded-lg`, Felder „Password“/„Confirm password“, Stärke-Anzeige, „Passwords do not match“ rot bzw. „✓ Passwords match“ grün); Button „Continue“; nur Cloud (`!is_self_managed`): Checkbox „I agree to Plane marketing communications“ (Default an) | `PATCH` Profil `{has_marketing_email_consent}` (fire-and-forget) + `PATCH /api/users/me/ {first_name, last_name, avatar_url}` + optional `POST /auth/set-password/ {password}` (mit CSRF); Fehler-Toast „User details update failed. Please try again!“; danach Schrittwechsel. Button disabled bis Formular gültig und – falls Passwort eingegeben – stark und bestätigt |
| 2 | `ROLE_SETUP` (nur Cloud) | `RoleSetupStep`, `steps/role/root.tsx` | „What's your role?“ / „Let's set up Plane for how you work.“; „Select one“; Kacheln `rounded-lg border px-3 py-2` (gewählt `border-accent-strong bg-accent-subtle text-accent-primary` + Haken-Box): Product Manager (`CubeOutline`), Engineering Manager (`ViewsOutline`), Designer (`PenTool`), Developer (`MonitorOutline`), Founder/Executive (`RocketOutline`), Operations Manager (`RefreshOutline`), Others (`CubeOutline`); „Continue“, „Skip“ | `PATCH` Profil `{role: id}` (z. B. `product-manager`), Toast „Profile setup completed!“ / „Profile setup failed. Please try again!“ |
| 3 | `USE_CASE_SETUP` (nur Cloud) | `UseCaseSetupStep`, `steps/usecase/root.tsx` | „What brings you to Plane?“ / „Tell us your goals and team size.“; „Select one or more“; Mehrfachauswahl `USE_CASES`: „Plan and track product roadmaps“, „Manage engineering sprints“, „Coordinate cross-functional projects“, „Replace our current tool“, „Just exploring“ (Pflicht „Please select at least one option“); „Continue“, „Skip“ | `PATCH` Profil `{use_case: auswahl.join(". ")}`; danach `onboarding_step.profile_complete = true`; existiert schon ein Workspace → Onboarding beenden, sonst Schritt 4 |
| 4a | `WORKSPACE_CREATE_OR_JOIN` – Einladungen vorhanden | `WorkspaceJoinInvitesStep`, `steps/workspace/join-invites.tsx` | „Join invites or create a workspace“ / „All your work — unified.“; je Einladung Zeile `rounded-lg border px-3 py-2 hover:bg-surface-2` mit `WorkspaceLogo size-8`, Name (max 30 Zeichen), Rolle, Checkbox; „Continue“ (Spinner) und „Create new workspace“ (ghost) | `POST /api/users/me/workspaces/invitations/ {invitations:[ids]}` → `fetchWorkspaces` → `fetchCurrentUserSettings` → Onboarding beenden (Einladen wird übersprungen) |
| 4b | `WORKSPACE_CREATE_OR_JOIN` – anlegen | `WorkspaceCreateStep`, `steps/workspace/create.tsx` | „Create your workspace“ / „All your work — unified.“; „Name your workspace *“ (Placeholder „Enter workspace name“, Pflicht, `validateWorkspaceName`, max 80 „Limit your name to 80 characters.“; befüllt Slug automatisch: lowercase, trim, Leerzeichen → „-“); „Set your workspace's URL *“ (Präfix `{host}/`, max 48 „Limit your URL to 48 characters.“, `validateSlug` → „URLs can contain only ('-') and alphanumeric characters.“; Hinweis „You can only edit the slug of the URL“); „How many people will use this workspace? *“ als Chip-Gruppe `ORGANIZATION_SIZE` (`TickCircleOutline`); „Create workspace“ (Spinner); bei vorhandenen Einladungen „Join existing workspace“; Instanz verbietet Anlage → Text „You don't seem to have any invites to a workspace and your instance admin has restricted creation of new workspaces. …“ | `GET /api/workspace-slug-check/?slug=` → `status===true` und nicht in `RESTRICTED_URLS` (2.3/`packages/constants/src/workspace.ts`) → `POST /api/workspaces/`; sonst „Workspace URL is already taken!“; Toast „Success“/„Workspace created successfully“ bzw. „Error“/„Workspace could not be created. Please try again.“; `PATCH` Profil `{last_workspace_id}` + Settings neu laden; `organization_size === "Just myself"` → Einladen überspringen und beenden, sonst `workspace_create = true` und Schritt 5 |
| 5 | `INVITE_MEMBERS` | `InviteTeamStep`, `steps/team/root.tsx` | „Invite your teammates“ / „Work in plane happens best with your team. Invite them now to use Plane to its potential.“; Spaltenköpfe „Email“/„Role“; 3 Startzeilen (Raster 10 Spalten: E-Mail 6, Rolle 4), Placeholder reihum `charlie.taylor@frstflt.com`, `octave.chanute@…` (10 Namen); Rolle `Select select-2xl` mit Beschreibungen aus `ROLE_DETAILS` (Default Member, grau bis Interaktion); „×“ (`CloseCircleOutline`) bei Hover ab 2 Zeilen; ungültige E-Mail: „🤥 That doesn't look like an email address.“; „+ Add another“; „Continue“ (disabled bis mind. eine gültige E-Mail) und „I’ll do it later“; Enter im Formular wird unterdrückt | `POST /api/workspaces/{ersterWorkspace}/invitations/ {emails:[{email, role}]}` (leere Zeilen entfernt); Toast „Invitations sent successfully.“; `workspace_invite = true`, Onboarding beenden |
| Ende | – | `finishUserOnboarding` (`apps/web/store/user/profile.store.ts`) | – | `PATCH` Profil `{onboarding_step:{profile_complete, workspace_join, workspace_create, workspace_invite: true}, last_workspace_id: ersterWorkspace}` → `PATCH /api/users/me/onboard/ {is_onboarded:true}` → Profil + Settings (Cache-Busting) neu laden → `is_onboarded = true` (Weiterleitung übernimmt `AuthenticationWrapper`, A08 §2.3.1); Fehler-Toast „Failed“/„Failed to finish onboarding, Please try again later.“ |

Selbst gehostet (`config.is_self_managed`): Schritte 2 und 3 entfallen; Profil → (Workspace vorhanden ? Ende : Schritt 4); Zurück von Schritt 4 führt zu Schritt 1; Fortschritt zählt 1/3 bzw. 1/2 (ohne Einladen-Schritt, wenn Einladungen vorhanden sind).

Wiederaufnahme beim Laden: `profile_complete` ohne `workspace_create`/`workspace_join` → Schritt 4; `profile_complete` und `workspace_create` ohne `workspace_invite` → Schritt 5.

Ungenutzte Altkomponenten (nicht eingebunden): `create-or-join-workspaces.tsx`, `create-workspace.tsx`, `invitations.tsx`, `invite-members.tsx`, `profile-setup.tsx`, `step-indicator.tsx` (alle `apps/web/components/onboarding/`).

#### 2.15.3 Seite „Create workspace“ (`CreateWorkspaceForm`, `apps/web/components/workspace/create-workspace-form.tsx`)

Verwendet von `/create-workspace` (A08 §2.2.1 Nr. 6). Felder wie 4b, jedoch: Name-Placeholder „Something familiar and recognizable is always best.“, URL in `InputGroup 2xl` mit Präfix `{host}/` (`text-12`), Organisationsgröße als `Select select-2xl` (Placeholder „Select a range“); Buttons optional `secondaryButton`, „Create workspace“/„Creating workspace“ (disabled bis gültig) und – ohne `secondaryButton` – „Go back“ (`router.back()`). Beim Unmount werden die eingegebenen Werte über `setDefaultValues` an die Seite zurückgegeben.

#### 2.15.4 Produkt-Tour (`TourRoot`, `apps/web/components/onboarding/tour/*`)

| Teil | Detail |
|---|---|
| Willkommen | Karte `w-4/5 md:w-1/2 lg:w-2/5 rounded-[10px] bg-surface-1`; Kopf `h-64 bg-accent-primary` mit `PlaneLockup h-10 text-on-color`; „Welcome to Plane, {Vorname} {Nachname}“, Text „We're glad that you decided to try out Plane. You can now manage your projects with ease. Get started by creating a project.“; „Take a Product Tour“ (primary sm) und Link-Button „No thanks, I will explore it myself“ (→ Abschluss) |
| Tour-Schritte | Karte `grid h-3/5 sm:h-3/4 w-4/5 md:w-1/2 lg:w-3/5 grid-cols-10`; links (`lg`) `TourSidebar` „Let's get started! Get more out of Plane.“ mit Einträgen Work items/Cycles/Modules/Views/Pages (aktiv `border-l-[3px] border-accent-strong text-accent-primary`, klickbar); rechts Bild (`bg-accent-primary`, abwechselnd links/rechts ausgerichtet) + Titel + Text + „Back“/„Next“; letzter Schritt „Create your first project“ (Abschluss + `toggleCreateProjectModal(true)`); Schließen-Kreis oben rechts (fixe Prozent-Position) |
| Inhalte | `work-items` „Plan with work items“ – „The work item is the building block of the Plane. Most concepts in Plane are either associated with work items and their properties.“; `cycles` „Move with cycles“ – „Cycles help you and your team to progress faster, similar to the sprints commonly used in agile development.“; `modules` „Break into modules“ – „Modules break your big thing into Projects or Features, to help you organize better.“; `views` „Views“ – „Create custom filters to display only the work items that matter to you. Save and share your filters in just a few clicks.“; `pages` „Document with pages“ – „Use Pages to quickly jot down work items when you're in a meeting or starting a day.“; Bilder `@/app/assets/onboarding/{issues,cycles,modules,views,pages}.webp` |
| Abschluss | `updateTourCompleted()` → optimistisch `is_tour_completed = true`, `PATCH /api/users/me/tour-completed/ {is_tour_completed:true}` (Revert + Fehlerstatus bei Fehler) |

### 2.16 Querschnittsbausteine (`core/*`, `common/*`, `empty-state/*`, `ui/*`, `icons/*`, `modals/*`, `instance/*`, `global/*`)

Die Theme-Bausteine `core/theme/*` und `ChangeEmailModal` (`core/modals/change-email-modal.tsx`) sind in 2.13 beschrieben, `AppHeader`/`ContentWrapper`/`PageHead` (`core/app-header.tsx`, `core/content-wrapper.tsx`, `core/page-title.tsx`) sowie `BreadcrumbLink`, `SwitcherLabel` und `ExtendedAppHeader` (`common/*`) in 2.4 und 3.2.

#### 2.16.1 Layout- und Hilfsbausteine

| Baustein | Pfad | Verhalten / Darstellung | Verwendet in |
|---|---|---|---|
| `ContentOverflowWrapper` | `apps/web/components/core/content-overflow-HOC.tsx` | Begrenzt Inhalt auf `maxHeight` (Default 625 px), misst Höhe per `ResizeObserver` + `MutationObserver`, Höhenanimation `transition-[height] duration-300`; bei Überlauf Verlauf `bg-gradient-to-t from-surface-1 to-transparent` (eingeklappt `h-[100px] opacity-100`, ausgeklappt `h-[30px] opacity-70`) und Button „Show all“/„Show less“ (`show_all`/`show_less`, Default-Klasse `text-13 font-medium text-accent-primary`, optional `customButton`); ohne Kinder → `fallback` | Quick links (`maxHeight 150`), Recents (`415`), Stickies-Widget (`620`) – 2.5, 2.6 |
| `RenderIfVisible` (Default-Export) | `apps/web/components/core/render-if-visible-HOC.tsx` | Virtualisierung per `IntersectionObserver` (`rootMargin` `{verticalOffset}% {horizontalOffset}%`, Defaults 50/0), Platzhalterhöhe Default `300px`, gemessene Höhe wird per `runIdleTask` gemerkt (`useIdleTime`) | List/Kanban/Spreadsheet/Gantt (A09 §2.1) |
| `ListItem` / `ListLayout` | `apps/web/components/core/list/list-item.tsx`, `list-root.tsx` | Zeile `Row` `min-h-[52px] border-b border-subtle bg-layer-transparent py-4 text-13 hover:bg-layer-transparent-hover`, ab `lg` (bei offener Sidebar `xl`) einzeilig; `ControlLink` (Klick → `onItemClick` oder `router.push(itemLink)`), Titel `truncate` mit Tooltip, Slots `prependTitleElement`, `appendTitleElement`, `quickActionElement`, `actionableItems` | Recents (2.5), Cycles/Module/Views/Pages-Listen (A10b) |
| `LayoutErrorBoundary` | `apps/web/components/common/layout-error-boundary.tsx` | React-Fehlergrenze: `WarningTriangleOutline size-8`, „Something went wrong“ (`something_went_wrong`), Button „Retry“ (`common.retry`) remountet die Kinder (`retryKey`) | `IssueLayoutHOC` (A09) |
| `DataTable` | `apps/web/components/common/data-table.tsx` | Generische Tabelle (`columns` mit `content`/`thRender`/`tdRender`/`padding cell\|trigger`, `data`, `keyExtractor`, `renderRow`, `getRowProps`) auf `Table` (`variant table\|spreadsheet`); `isLoading` → 3 Skeleton-Zeilen à 28 px | Mitgliederlisten Workspace/Projekt (2.10.3, 2.11), Exporte, Analytics (A10b) |
| `SidebarPropertyListItem` | `apps/web/components/common/layout/sidebar/property-list-item.tsx` | Eigenschaftszeile: links Icon + Label (`h-7.5 w-30 text-body-xs-regular text-tertiary`), rechts Inhalt | Peek/Detail-Sidebar (A09) |
| `CountChip` | `apps/web/components/common/count-chip.tsx` | Pille `rounded-xl bg-accent-primary/20 px-2.5 py-0.5 text-caption-sm-semibold text-accent-primary` | Inbox-Kopf (2.7), Mitglieder-Seite (2.10.3), Work-Item-Header (A09) |
| `CoverImage` | `apps/web/components/common/cover-image.tsx` | ohne `src` und ohne `showDefaultWhenEmpty` → Skeleton `animate-pulse bg-layer-2`; sonst `getCoverImageDisplayURL(src, fallbackUrl)` (`apps/web/helpers/cover-image.helper.ts`, Fallback `DEFAULT_COVER_IMAGE_URL`), `object-cover` | Profil-Sidebar (2.8), User-Menü (2.2), Profil-Formular (2.13), Projektformular/-karte/-anlage (2.11, 2.12) |
| `LogoSpinner` | `apps/web/components/common/logo-spinner.tsx` | GIF `apps/web/app/assets/images/logo-spinner-{light\|dark}.gif` je Theme, `h-6`, ab `sm` `h-11` | Ladezustände (Root, Auth-Header, Workspace-Wrapper, Inbox, Profil-Einstellungen) |
| `AccessField` | `apps/web/components/common/access-field.tsx` | Segment-Schalter aus Icon-Buttons (`h-5 w-5`, aktiv `bg-layer-1`, Tooltip mit `t(i18n_label)`, `tabIndex 2+i`) | Seitenformular `apps/web/components/pages/modals/page-form.tsx` (A10b) |
| `PageAccessIcon` | `apps/web/components/common/page-access-icon.tsx` | 10-px-Icon: archiviert `ArchiveOutline`, öffentlich `GlobeOutline`, sonst `LockOutline` | Seiten-Detail-Header (A10b) |
| `handleTriggerClick` / `handleTriggerKeyDown` | `apps/web/components/common/trigger-guard.ts` | `preventDefault`+`stopPropagation` bzw. `stopPropagation` bei Enter/Leertaste, damit Menü-Trigger in klickbaren Karten nicht navigieren | Modul-Karte, Relations-/Sub-Item-Buttons |
| `useQuickActionsFactory` | `apps/web/components/common/quick-actions-factory.tsx` | Fabrik für Kontextmenü-Einträge: `edit` („Edit“), `open-new-tab` („Open in new tab“), `copy-link` („Copy link“), `archive` („Archive“, optional `disabled`+`description`), `restore` („Restore“), `delete` („Delete“), Layout-Varianten „Open in new tab“/„Copy link“ (hart codiert) | `quick-actions-helper.tsx` |
| `useCycleMenuItems`, `useModuleMenuItems`, `useViewMenuItems`, `useLayoutMenuItems`, `useIntakeHeaderMenuItems` | `apps/web/components/common/quick-actions-helper.tsx` | Cycle: Edit (editierbar, nicht abgeschlossen, nicht archiviert), Open in new tab, Copy link, Archive (nur abgeschlossene: sonst disabled mit „Only completed cycles can be archived“), Restore (archiviert), Delete (wie Edit); Modul: Edit, Open, Copy, Archive (disabled mit „Only completed or cancelled modules can be archived“), Restore, Delete; View: Edit (Owner), Open, Copy, Delete (Owner oder Admin); Layout: Open in new tab, Copy link; Intake: leere Liste (CE-Stub, ungenutzt) | Cycles/Module/Views (A10b), Work-Item-Layout-Header (A09), Workspace-Views (2.17) |

#### 2.16.2 Leerzustände

| Komponente | Pfad | Darstellung |
|---|---|---|
| `DetailedEmptyState` | `apps/web/components/empty-state/detailed-empty-state-root.tsx` | Container `flex min-h-full min-w-full items-center justify-center overflow-y-auto px-5 py-10 md:px-20`; Größen `sm` (`md:min-w-[24rem] max-w-[45rem]`, Buttons `xs`), `base` (`28rem`/`50rem`, `sm`), `lg` (Default, `30rem`/`60rem`, `md`); Titel `text-18 font-semibold` (ohne Beschreibung `font-medium`), Beschreibung `text-13`, Bild `h-auto w-full loading="lazy"`, Primär-/Sekundär-Button (Icon vor/nach) oder Custom-Buttons |
| `SimpleEmptyState` | `apps/web/components/empty-state/simple-empty-state-root.tsx` | Bild `size-24` (`sm`) bzw. `size-28` (`lg`); Titel ohne Beschreibung `text-13 text-placeholder`, mit Beschreibung `text-16 text-tertiary`; Beschreibung `text-14 font-medium text-placeholder`, `whitespace-pre-line` |
| `SectionEmptyState` | `apps/web/components/empty-state/section-empty-state-root.tsx` | Rahmenbox `rounded-md border border-subtle p-10`, Icon-Kachel `size-8 bg-layer-1`, Titel `text-13 font-medium`, Beschreibung `text-11 text-tertiary`, optionale Aktion |
| `EmptyState` (alt) | `apps/web/components/common/empty-state.tsx` | Bild `w-52 sm:w-60`, Titel `text-18 font-semibold`, Beschreibung, Primär-Button `sm` + Sekundär-Element |
| `EmptySpace` / `EmptySpaceItem` | `apps/web/components/ui/empty-space.tsx` | Titel/Beschreibung + Liste von Einträgen (Icon-Kachel `h-10 w-10 rounded-lg bg-accent-primary`, Chevron rechts), optionaler Pfeil-Link; nur `apps/web/app/(all)/workspace-invitations/page.tsx` (A08 §2.2) |
| `EmptyStateCompact` / `EmptyStateDetailed` | `@plane/blocks/empty-state` | Primärer Leerzustand der neueren Screens (`assetKey`); im Bereich verwendet: `project`, `archived-work-item`, `search`, `no-access`, `priority`, `unknown`, `changelog` sowie die Keys aus 2.5–2.7 und 2.13 (A13a) |

#### 2.16.3 Skeleton-Loader (`apps/web/components/ui/loader/*`)

| Datei | Exporte | Verwendet in |
|---|---|---|
| `cycle-module-board-loader.tsx` | `CycleModuleBoardLayoutLoader` | Modul-Board (A10b) |
| `cycle-module-list-loader.tsx` | `CycleModuleListLayoutLoader` | Cycle-/Modul-Listen und -Archive (A10b) |
| `layouts/calendar-layout-loader.tsx` | `CalendarLayoutLoader` | `IssueLayoutHOC` (A09 §2.22) |
| `layouts/gantt-layout-loader.tsx` | `GanttLayoutLoader`, `GanttLayoutListItemLoader` | Gantt (A09 §2.22) |
| `layouts/kanban-layout-loader.tsx` | `KanbanLayoutLoader`, `KanbanColumnLoader`, `KanbanIssueBlockLoader` | Kanban (A09 §2.22) |
| `layouts/list-layout-loader.tsx` | `ListLayoutLoader`, `ListLoaderItemRow` | Liste, Entwürfe (A09 §2.22) |
| `layouts/members-layout-loader.tsx` | `MembersLayoutLoader` | `workspace/settings/members-list-item.tsx` (2.10.3) |
| `layouts/project-inbox/inbox-layout-loader.tsx`, `inbox-sidebar-loader.tsx` | `InboxLayoutLoader`, `InboxSidebarLoader` | Projekt-Intake (A10b) |
| `layouts/spreadsheet-layout-loader.tsx` | `SpreadsheetLayoutLoader`, `SpreadsheetIssueRowLoader` | Spreadsheet (A09 §2.22) |
| `projects-loader.tsx` | `ProjectsLoader` | Projektkarten (2.12.1) |
| `view-list-loader.tsx` | `ViewListLoader` | Projekt-Views und Workspace-Views (2.17, A10b) |
| `settings/activity.tsx` | `ActivitySettingsLoader` | Profil-Aktivität (2.8.5) |
| `settings/api-token.tsx` | `APITokenSettingsLoader` | Personal Access Tokens (2.13) |
| `settings/email.tsx` | `EmailSettingsLoader` | Benachrichtigungs-Einstellungen (2.13) |
| `settings/import-and-export.tsx` | `ImportExportSettingsLoader` | Exporte (A10b) |
| `settings/integration.tsx` | `IntegrationsSettingsLoader` | Workspace-Einstellungen „Integrations“ (2.10) |
| `settings/members.tsx` | `MembersSettingsLoader` | Mitgliederlisten Workspace/Projekt (2.10.3, 2.11) |
| `settings/web-hook.tsx` | `WebhookSettingsLoader` | Webhooks (A10b) |
| `utils.tsx` | `getRandomInt`, `getRandomLength` | Zufallsbreiten der Loader |
| `notification-loader.tsx`, `pages-loader.tsx` | `NotificationsLoader`, `PagesLoader` | **nicht eingebunden** (Inbox nutzt eigenen `workspace-notifications/sidebar/loader.tsx`) |

#### 2.16.4 Fachliche Querschnittsdialoge und -anzeigen in `core/`

| Baustein | Pfad | Inhalt / Verhalten | API |
|---|---|---|---|
| Beschreibungs-Versionen (`DescriptionVersionsRoot`, `…Dropdown`, `…DropdownItem`, `…Modal`) | `apps/web/components/core/description-versions/*` | Trigger (`HistoryOutline`, `text-11`): „Last edited by **{Name}** {vor x}“ (neueste Version bzw. ohne Versionen Ersteller/`createdAt`; gelöschter Nutzer „Deactivated user“), Chevron nur wenn Versionen vorhanden, sonst `disabled`; Menü „Previously edited by“ mit Einträgen Avatar 2xs + Name + relative Zeit (`last_saved_at`); Dialog `lg` (`data-prevent-outside-click`, sr-only-Titel „Version history“): Toolbar „Edited by“ + Avatar + Zeit, Pfeile vor/zurück (am Rand `opacity-50 disabled`), Inhalt read-only `RichTextEditor` (Skeleton während Laden); Footer: Icon „Copy markdown“ (Toast „Success!“/„Markdown copied to clipboard.“), „Cancel“, „Restore“ (nur wenn `!isRestoreDisabled`; übergibt `description_html` bzw. `<p></p>` und schließt) | über `fetchHandlers` des Aufrufers (Work Item, Epic, Intake; A08 §2.7, A09 §2.13); SWR `DESCRIPTION_VERSIONS_LIST_{id}`, `DESCRIPTION_VERSION_DETAILS_{versionId}` |
| Datumsfilter „Custom“ (`DateFilterModal`, `DateFilterSelect`) | `apps/web/components/core/filters/date-filter-modal.tsx`, `date-filter-select.tsx` | Dialog mit Auswahl „{title} before\|after\|range“ (Default `range`, Datum 1 = heute, Datum 2 = +1 Monat), Inline-Kalender (gegenseitig begrenzt: Datum 1 nicht nach Datum 2, Datum 2 nicht vor Datum 1), bei `range` Vorschauzeile beider Daten, Buttons „Cancel“/„Apply“ (disabled bei `isInvalid`); Ergebnis `["YYYY-MM-DD;after","YYYY-MM-DD;before"]` bzw. `["YYYY-MM-DD;before\|after"]`; `isInvalid` vergleicht wegen `const date2 = getDate(watch("date1"))` Datum 1 mit sich selbst (s. 3.10) | – |
| Bulk-Delete (`BulkDeleteIssuesModal`, `BulkDeleteIssuesModalItem`) | `apps/web/components/core/modals/bulk-delete-issues-modal.tsx`, `bulk-delete-issues-modal-item.tsx` | Dialog `md` mit Inline-Combobox (sr-only-Titel `power_k.actions_commands.bulk_delete_work_items`), Suche „Type to search“ (Debounce 500 ms), Überschrift „Select work items to delete“ (bei leerer Suche), Mehrfachauswahl; leer „No work items found“ bzw. „No matching work items found“ (Bilder `@/app/assets/empty-state/search/{issues,search}-{light\|dark}.webp`); Buttons (nur bei Treffern) „Cancel“, „Delete selected work items“/„Deleting...“ (danger); Toasts „Error!“/„Please select at least one work item.“, „Success!“/„Work items deleted successfully!“, „Error!“/„Something went wrong. Please try again.“; geöffnet über Power-K (2.9) via `WorkItemLevelModals` | `GET /api/workspaces/{ws}/projects/{pid}/search-issues/?search=…&workspace_search=false`; `DELETE /api/workspaces/{ws}/projects/{pid}/bulk-delete-issues/` (`apps/web/services/issue/issue.service.ts`) |
| Bestehende Work Items hinzufügen (`ExistingIssuesListModal`, `IssueSearchModalEmptyState`) | `apps/web/components/core/modals/existing-issues-list-modal.tsx`, `issue-search-modal-empty-state.tsx` | Dialog `md`, sr-only-Titel „Add existing work item“; Suche „Type to search“ (500 ms); Chips der Auswahl (`IssueIdentifier` + „×“) oder „No work items selected“; optional Switch „Workspace level“ (Tooltip „Toggle workspace level search“); Überschrift „Search results for "{q}" in project:“ (hart codiert); Liste mit Zustandsfarbpunkt, Identifier, Name, Checkbox und (Hover) Link „Open in new tab“ (`RocketOutline`); Footer „Select all“/„Deselect all“, „Cancel“, „Add selected work items“/„Adding“; leere Auswahl → Toast „Please select at least one work item“; Vorauswahl `selectedWorkItemIds`, Ausblenden per `shouldHideIssue` | `GET /api/workspaces/{ws}/projects/{pid}/search-issues/?search&workspace_search&…searchParams` oder `workItemSearchServiceCallback` (A09) |
| KI-Assistent (`GptAssistantPopover`) | `apps/web/components/core/modals/gpt-assistant-popover.tsx` | Popover `rich`: Abschnitt „Content:“ (read-only Editor mit Prompt), „Response:“ (read-only Editor), Hinweis „No response could be generated. This may be due to insufficient content or task information. Please try again.“; Eingabe (Autofokus, Enter sendet) „Tell AI what action to perform on this content...“ bzw. „Ask AI anything...“; Fuß: „By using this feature, you consent to sharing the message with a 3rd party service.“, „Close“, „Generate response“/„Generating response...“/„Generate again“; nach Antwort „Use this response“; Fehler 429 „You have reached the maximum number of requests of 50 requests per month per user.“, sonst „Some error occurred. Please try again.“, leere Aufgabe „Please enter some task to get AI assistance.“; sichtbar nur bei `config.has_llm_configured` im Work-Item-Modal (`apps/web/components/issues/issue-modal/components/description-editor.tsx`) | `POST /api/workspaces/{ws}/ai-assistant/ {prompt, task}` (`apps/web/services/ai.service.ts`) |
| Mehrfachauswahl (`MultipleSelectGroup`, `MultipleSelectEntityAction`, `MultipleSelectGroupAction`) | `apps/web/components/core/multiple-select/*` | Kontext und Checkboxen für Bulk-Auswahl (A09 §4.3) | – |
| Fortschritt (`ProgressChart`, `SingleProgressStats`, `StateGroupStatComponent`, `AssigneeStatComponent`, `LabelStatComponent`, `PROGRESS_STATS`, `createFilterUpdateHandler`) | `apps/web/components/core/sidebar/progress-chart.tsx`, `single-progress-stats.tsx`, `progress-stats/*` | Burn-up-Chart „Current {work items}“ vs. „Ideal {work items}“ (Achsen „Date“/„Completion“, `h-[370px]`); Tabs „States“, „Assignees“, „Labels“; Zeile `SingleProgressStats`: Titel (4/6), „{n}%“ + „of {total}“, klickbar setzt Filter, ausgewählt `bg-layer-1`; Assignee ohne Zuweisung „No assignee“ | Cycle-/Modul-Analytics (A10b) |
| Aktivitätstexte (`ActivityIcon`, `ActivityMessage`, `IssueLink`) | `apps/web/components/core/activity.tsx` | Feld → Icon + Satz (s. Tabelle 2.16.4a); `IssueLink`: Tooltip mit Work-Item-Name bzw. „This work item has been deleted“, Link `generateWorkItemLink` | Profil (2.8), Work-Item-Aktivität (A09 §2.15) |
| `SidebarHamburgerToggle` | `apps/web/components/core/sidebar/sidebar-menu-hamburger-toggle.tsx` | Kachel `size-7 rounded-sm bg-surface-2` mit `RightSidePaneOutline`; nur im toten `ProfileSettingContentWrapper` | **nicht erreichbar** |

**Tabelle 2.16.4a – Aktivitätssätze (`activityDetails` in `apps/web/components/core/activity.tsx`)** (Suffixe in Klammern nur bei `showIssue`):

| `field` | Icon | Satz |
|---|---|---|
| `assignees` | `MembersOutline` | „added a new assignee {User} (to {Issue})“ / „removed the assignee {User} (from {Issue})“ |
| `archived_at` | `ArchiveOutline` | „restored {Issue}“ (`new_value === "restore"`) / „archived {Issue}“ |
| `attachment` | `AttachOutline` | „uploaded a new attachment (to …)“ / „removed an attachment (from …)“ |
| `description` | `ChatOutline` | „updated the description (of …)“ |
| `estimate_point` | `TriangleIcon` | „removed the estimate point (from …)“ / „set the estimate point to {v} (for …)“ |
| `issue` | `WorkItemsOutline` | „created {Issue}“ / „converted {Issue} to an epic“ / „deleted {Issue}“ |
| `epic` | `EpicOutline` | „created {Issue}“ / „converted {Issue} to a work item“ / „deleted {Issue}“ |
| `labels` | `LabelsOutline` | „added a new label {Label-Pille} (to …)“ / „removed the label {Label-Pille} (from …)“ |
| `link` | `LinkOutline` | „added this link (to …)“ / „updated the link (from …)“ / „removed this link (from …)“ (Link öffnet `new_value`/`old_value` in neuem Tab) |
| `cycles` | `CyclesOutline` | „added {Issue\|this work item} to the cycle {Cycle-Link}“ / „set the cycle to {Cycle-Link}“ / „removed {Issue} from the cycle {Cycle-Link}“ (Links `/{ws}/projects/{pid}/cycles/{id}`) |
| `modules` | `ModuleOutline` | „added {Issue\|this work item} to the module {Modul-Link}“ / „set the module to {Modul-Link}“ / „removed {Issue} from the module {Modul-Link}“ |
| `name` | `ChatOutline` | „set the title to {v} (of …)“ |
| `parent` | `MembersOutline` | „removed the parent {old} (from …)“ / „set the parent to {new} (for …)“ |
| `priority` | `SignalMediumIcon` | „set the priority to {Urgent\|High\|Medium\|Low\|None} (for …)“ |
| `relates_to` | `RelatesToOutline` | „marked that {Issue\|this work item} relates to {v}.“ / „removed the relation from {v}.“ |
| `blocking` | `BlockerIcon` | „marked {Issue\|this work item} is blocking work item {v}.“ / „removed the blocking work item {v}.“ |
| `blocked_by` | `BlockedIcon` | „marked {Issue\|this work item} is being blocked by {v}.“ / „removed {Issue\|this work item} being blocked by work item {v}.“ |
| `duplicate` | `DuplicateOfOutline` | „marked {Issue\|this work item} as duplicate of {v}.“ / „removed {Issue\|this work item} as a duplicate of {v}.“ |
| `state` | `GridOutline` | „set the state to {v} (for …)“ |
| `start_date` | `CalendarOutline` | „removed the start date (from …)“ / „set the start date to {Datum} (for …)“ |
| `target_date` | `CalendarOutline` | „removed the due date (from …)“ / „set the due date to {Datum} (…)“ |
| `inbox` | `IntakeOutline` | Verb `-1` „declined work item“/„declined this work item from intake.“, `0` „snoozed work item“/„snoozed this work item.“, `1` „accepted work item“/„accepted this work item from intake.“, `2` „declined work item … from intake by marking a duplicate work item.“, sonst „updated intake work item status.“ |
| unbekanntes Feld | – | nichts (kein Icon, keine Nachricht); fehlendes `field` → wie `issue` |

#### 2.16.5 Bild-Picker und Upload-Dialoge

| Baustein | Pfad | UI | Ablauf / API |
|---|---|---|---|
| `ImagePickerPopover` | `apps/web/components/core/image-picker-popover.tsx` | Trigger `ButtonElement secondary xs` mit `label` (z. B. „Change cover“); Popover `rich` `h-96 w-80`, ab `md` `h-[36rem] w-[36rem]`; `Tabs variant="contained"`: „Unsplash“ (nur bei `config.has_unsplash_configured`), „Images“, „Upload“ (Default = erster aktiver Tab). Unsplash: Feld „Search for images“ (Enter oder Button „Search“), Raster der Treffer (aria „Select image: {alt}“), leer „No images found.“, Loader 8 Kacheln; Images: 29 statische Cover (`STATIC_COVER_IMAGES`, `@/app/assets/cover-images/image_1…29.jpg`), aria „Select cover image {n}“; Upload: Dropzone (gestrichelt), „Drag & drop image here“/„Drop image here to upload“, Vorschau mit „Edit“, Fehler „The image size cannot exceed 5 MB.“ bzw. „Please upload a file in a valid format.“, Buttons „Cancel“, „Upload & Save“/„Uploading“ | Unsplash `GET /api/unsplash/?query=` (SWR `UNSPLASH_IMAGES_{q}`); statisches Bild → `onChange(url)`; Upload `isProfileCover` → `uploadUserAsset({entity_type: USER_COVER})`, sonst `uploadWorkspaceAsset(ws, {entity_identifier: projectId, entity_type: PROJECT_COVER})` (Signed-URL-Upload, A07/A08 §2.7) → `onChange(asset_url)`; Fehler-Toast „Image not uploaded“/„The image could not be uploaded“; erlaubt `image/jpeg\|jpg\|png\|webp`, max. 5 MB (`packages/constants/src/file.ts`) |
| `UserImageUploadModal` | `apps/web/components/core/modals/user-image-upload-modal.tsx` | Dialog `sm` „Upload Image“; Dropzone wie oben, Hinweis „File formats supported- .jpeg, .jpg, .png, .webp“; Footer „Remove“/„Removing“ (danger, nur mit vorhandenem Bild), „Cancel“, „Upload & Save“/„Uploading“ | Upload `POST /api/assets/v2/user-assets/` (`USER_AVATAR`); Entfernen: alte absolute URL → `DELETE /api/users/file-assets/{key}/`, sonst `DELETE /api/assets/v2/user-assets/{assetId}/`, danach `handleRemove()`; Fehler-Toast „Error!“/Fehlertext bzw. „Something went wrong. Please try again.“ |
| `WorkspaceImageUploadModal` | `apps/web/components/core/modals/workspace-image-upload-modal.tsx` | wie oben, Titel „Upload image“ | `uploadWorkspaceAsset` (`WORKSPACE_LOGO`); Entfernen `DELETE /api/workspaces/file-assets/{workspaceId}/{key}/` bzw. `DELETE /api/assets/v2/workspaces/{ws}/{assetId}/`; Fehler-Toast „Error“/„Something went wrong“ |

#### 2.16.6 Icons (`icons/*`)

`getFileIcon(fileType, size = 28)` (`apps/web/components/icons/attachment/attachment-icon.tsx`) bildet Dateiendungen auf PNG-Icons aus `apps/web/app/assets/attachment/*` ab: `pdf`, `csv`, `xlsx` (Sheet), `css`, `doc`, `fig` (Figma), `html`, `png`, `jpg`, `js`, `txt`, `svg`, `mp3`/`wav` (Audio), `mp4`/`wmv`/`mkv` (Video), `zip`, `rar`, sonst Default-Icon (genutzt in den Attachment-Komponenten, A09 §2.14). `SettingIcon` nur in `apps/web/components/settings/project/sidebar/item-icon.tsx`. Ungenutzt: `DocumentIcon`, `TuneIcon`, `ImgIcon` (nur über `icons/attachment/index.ts` re-exportiert) und `LockedComponent` (`icons/locked-component.tsx`, Pille „Locked“).

#### 2.16.7 Globale Modal-Hosts (`modals/*`, eingehängt in `apps/web/components/power-k/projects-app-provider.tsx`)

| Host | Pfad | Dialoge (gesteuert über `useCommandPalette()`-Flags) |
|---|---|---|
| `WorkspaceLevelModals` | `apps/web/components/modals/workspace-level.tsx` | `CreateProjectModal` (`isCreateProjectModalOpen`, 2.12.3) |
| `ProjectLevelModals` (nur mit `projectId`) | `apps/web/components/modals/project-level.tsx` | `CycleCreateUpdateModal`, `CreateUpdateModuleModal`, `CreateUpdateProjectViewModal`, `CreatePageModal` (`redirectionEnabled`, `pageAccess` aus Flag) (A10b) |
| `WorkItemLevelModals` | `apps/web/components/modals/work-item-level.tsx` | `CreateUpdateIssueModal` (Vorbelegung `cycle_id` bzw. `module_ids` aus der Route; nach Anlage eines Sub-Work-Items Neuladen der Sub-Liste), `DeleteIssueModal` (für das per Identifier gewählte Work Item; danach Redirect `/{ws}/projects/{pid}/issues` bzw. `/epics`), `BulkDeleteIssuesModal` (2.16.4) |

#### 2.16.8 Instanz-Zustände (`instance/*`, eingebunden in `apps/web/lib/wrappers/instance-wrapper.tsx`, A08 §2.3)

| Ansicht | Pfad | Inhalt |
|---|---|---|
| `InstanceNotReady` | `apps/web/components/instance/not-ready-view.tsx` | `DefaultLayout`; zwei Hintergrund-Logos (`@/app/assets/auth/gradient-bg-logo.webp`), oben `PlaneLockup` (20×95), Mitte Logo `@/app/assets/auth/gradient-logo.webp` `h-24 w-40`, „Welcome to Plane“ (`text-h2-semibold`), „Set up your instance and create your first workspace to begin managing projects and work.“, Button „Get started“ (`primary lg`, `w-72`) → Link `GOD_MODE_URL` (`ADMIN_BASE_URL + ADMIN_BASE_PATH`, `packages/constants/src/endpoints.ts`) |
| `MaintenanceView` + `MaintenanceMessage` | `apps/web/components/instance/maintenance-view.tsx`, `maintenance-message.tsx` | Bild `@/app/assets/instance/maintenance-mode-{light\|dark}.svg` (288×176), „🚧 Looks like Plane didn't start up correctly!“, „Some services might have failed to start. Please check your container logs to identify and resolve the issue. If you're stuck, reach out to our support team for more help.“, Link „Contact Support“ (`mailto:support@plane.so`) → **Airgap: Kontakt konfigurierbar machen** |

#### 2.16.9 „What's new?“, Version, Zeitzonen-Auswahl (`global/*`)

| Baustein | Pfad | Inhalt |
|---|---|---|
| `ProductUpdatesModal` | `apps/web/components/global/product-updates/modal.tsx` | `DialogContent size="lg"` (aria „What's new?“): Header, Changelog, Footer; geöffnet aus dem Hilfe-Menü (2.2) |
| `ProductUpdatesHeader` | `.../product-updates/header.tsx` | „What's new?“ (`text-18 font-medium`) + Pille „Version: v{package.json version}“ (`bg-accent-primary/20 text-11 text-accent-primary`) |
| `ProductUpdatesChangelog` | `.../product-updates/changelog.tsx` | `iframe` auf `config.instance_changelog_url` (`h-[550px]`, Skeleton bis `onLoad` + 1 s, Timeout 15 s → Fehler); ohne URL oder bei Fehler `ProductUpdatesFallback` |
| `ProductUpdatesFallback` | `.../product-updates/fallback.tsx` | `EmptyStateDetailed assetKey="changelog"` „We're having trouble fetching the updates. Please visit our changelog to view the latest updates.“, Button „Go to changelog“ → `https://plane.so/changelog?category=cloud` bzw. `…=self-hosted` (je `config.is_self_managed`) |
| `ProductUpdatesFooter` | `.../product-updates/footer.tsx` | Links „Docs“ (`https://go.plane.so/p-docs`), „Full changelog“ (`https://go.plane.so/p-changelog`), „Support“ (`mailto:support@plane.so`), „Forum“ (`https://forum.plane.so`); Button „Powered by Plane Pages“ (`https://plane.so/pages`) → **Airgap: alle externen Links konfigurierbar/abschaltbar (ADR-004)** |
| `PlaneVersionNumber` | `apps/web/components/global/version-number.tsx` | „Version: v{package.json version}“ (Hilfe-Menü-Fuß, 2.2) |
| `TimezoneSelect` | `apps/web/components/global/timezone-select.tsx`, `apps/web/hooks/use-timezone.tsx` | `Combobox` (Default-Placeholder „Select a timezone“, Größe `lg`), Suche „Search“ (`common.search.label`), leer „No matches found“; Optionen aus `GET /api/timezones/` (SWR `TIMEZONES_LIST`), gruppiert nach `value` (Labels mit „, “ verbunden), Anzeige „{utc_offset} {label}“, Suche über `"{value} {label}, {gmt_offset}, {utc_offset}"`; zusätzlicher Eintrag „UTC“; deaktiviert während Laden/Fehler; genutzt in Workspace-Details (2.10.2), Projekt-Formular (2.11) und Profil-Präferenzen (2.13) |

### 2.17 Workspace-Views, Archiv-Tabs, Work-Item per Identifier

Die Workspace-Views (`/:ws/workspace-views[/:globalViewId]`) werden fachlich in A10b §2.5 und §3.4 beschrieben, die Spreadsheet-Darstellung `AllIssueLayoutRoot` in A09 §2.1. Hier nur die Bausteine aus `apps/web/components/workspace/views/`, `archives/` und `browse/`.

| Komponente | Pfad | Inhalt / Verhalten |
|---|---|---|
| Übersichtsseite | `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/page.tsx` | Titel „`{ws} - All Views`“; Kopfzeile `h-11 border-b` mit `InputGroup 2xl` (Lupe, Placeholder „Search“); darunter Default-Views gefiltert nach übersetztem Label, dann eigene Views (`GlobalViewsList`) |
| `GlobalDefaultViewListItem` | `apps/web/components/workspace/views/default-view-list-item.tsx` | Zeile mit Link `/{ws}/workspace-views/{key}` für `DEFAULT_GLOBAL_VIEWS_LIST` (`packages/constants/src/workspace.ts`): „All work items“ (`all-issues`), „Assigned“ (`assigned`), „Created“ (`created`), „Subscribed“ (`subscribed`); Name `truncateText(…, 75)` |
| `GlobalViewsList` | `apps/web/components/workspace/views/views-list.tsx` | SWR lädt `fetchAllGlobalViews` (`GET /api/workspaces/{ws}/views/`); bis geladen `ViewListLoader`; Filter `getSearchedViews(searchQuery)` |
| `GlobalViewListItem` | `apps/web/components/workspace/views/view-list-item.tsx` | Link `/{ws}/workspace-views/{id}`, Name (max. 75 Zeichen) und Beschreibung; „…“-Menü mit „Edit View“ (→ `CreateUpdateWorkspaceViewModal`) und „Delete View“ (→ `DeleteGlobalViewModal`) – **ohne Rechteprüfung** (hart codierte englische Labels) |
| `GlobalIssuesHeader` (Route-Header) | `apps/web/app/(all)/[workspaceSlug]/(projects)/workspace-views/header.tsx` | Breadcrumb „Views“ + Switcher (`SwitcherLabel` mit `ViewsOutline`; Default- und eigene Views, Suche „Search“, leer „No matches found“); `WorkItemFiltersToggle`; „Display“-Dropdown (nicht bei `is_locked`, Optionen `ISSUE_DISPLAY_FILTERS_BY_PAGE.my_issues.layoutOptions[layout]`, Default Spreadsheet); Button „Add view“; Quick-Actions der aktuellen View |
| `WorkspaceViewQuickActions` | `apps/web/components/workspace/views/quick-action.tsx` | Menü aus `useViewMenuItems` (2.16.1): „Edit“ (Owner), „Open in new tab“, „Copy link“ (Toast „Link Copied!“/„View link copied to clipboard.“), „Delete“ (Owner oder WS-Admin) |
| `DefaultWorkspaceViewQuickActions` | `apps/web/components/workspace/views/default-view-quick-action.tsx` | „Open in new tab“, „Copy link“ (gleicher Toast) |
| `CreateUpdateWorkspaceViewModal` + `WorkspaceViewForm` | `apps/web/components/workspace/views/modal.tsx`, `form.tsx` | `DialogContent size="md"` „Create View“/„Update View“; Anlegen → `POST /api/workspaces/{ws}/views/`, Toast „Success!“/„View created successfully.“ und Navigation zu `/{ws}/workspace-views/{id}`; Fehler „View could not be created. Please try again.“; Bearbeiten → `PATCH /api/workspaces/{ws}/views/{id}/`, „View updated successfully.“ / „View could not be updated. Please try again.“ (Formularfelder: A10b) |
| `DeleteGlobalViewModal` | `apps/web/components/workspace/views/delete-view-modal.tsx` | Bestätigung „Are you sure you want to delete this view?“ / „If you confirm, all the sort, filter, and display options + the layout you have chosen for this view will be permanently deleted without any way to restore them.“; `DELETE /api/workspaces/{ws}/views/{id}/`; danach `localStorage.removeItem("global_view_filters/{id}")`; Fehler „Failed to delete the view. Please try again.“ |
| `GlobalViewsHeader` | `apps/web/components/workspace/views/header.tsx` | **nicht eingebunden** (älterer Header) |
| `ArchiveTabsList` | `apps/web/components/archives/archive-tabs-list.tsx` | Tabs für `/{ws}/projects/{pid}/archives/{issues\|cycles\|modules}`: „Work items“ (immer), „Cycles“ (bei `cycle_view`), „Modules“ (bei `module_view`); aktiv, wenn `pathname.includes(key)`: `border-b-2 border-accent-strong text-accent-primary`, sonst `border-transparent text-tertiary hover:border-subtle`; Klassen `px-4 py-4 text-13 font-medium`; genutzt in den Archiv-Headern (A09 §2.18, A10b) |
| `WorkItemDetailRoot` | `apps/web/components/browse/workItem-detail.tsx` | Wrapper für `/{ws}/browse/{PROJ-123}`: rendert `IssueDetailRoot` mit `is_archived = !!issue.archived_at` (A08 §2.2, A09 §2.13) |

### 2.18 Lizenz-, Upgrade- und Billing-Komponenten (entfallen gemäß ADR-001)

Vollständige Inhalte (Texte, Preise, Plan-Matrix) stehen in `migration/features/20-paid-spuren-im-repo.md` §2 und §5 (U1–U11); hier nur die Fundstellen in diesem Bereich und das Zielbild.

| Komponente | Pfad | Erscheint in | Original | Zielbild (ADR-001) |
|---|---|---|---|---|
| `WorkspaceEditionBadge` | `apps/web/components/workspace/edition-badge.tsx` | Sidebar-Fuß (`apps/web/components/sidebar/sidebar-wrapper.tsx`, 2.3) | Button `tertiary md` „Community“, Tooltip „Version: v{package.json version}“, aria `aria_labels.projects_sidebar.edition_badge`, öffnet `PaidPlanUpgradeModal` | entfällt (ggf. neutrale Versionsanzeige) |
| `PaidPlanUpgradeModal` + Karten | `apps/web/components/license/modal/upgrade-modal.tsx`, `license/modal/card/{base-paid-plan-card,checkout-button,discount-info,free-plan,plan-upgrade,talk-to-sales}.tsx` | nur über `WorkspaceEditionBadge` | Vollbild-Dialog mit Plan-Karten, Checkout-Redirect, „Talk to Sales“ (features/20 U4–U10) | entfällt |
| `UpgradeBadge` | `apps/web/components/workspace/upgrade-badge.tsx` | „More“-Sidebar-Eintrag `active_cycles` (`workspace/sidebar/extended-sidebar-item.tsx`), Header der Seite „Active cycles“ (`app/(all)/[workspaceSlug]/(projects)/active-cycles/header.tsx`, `size="md"`), Schätzsysteme ohne Freischaltung (`components/estimates/create/stage-one.tsx`), Projekt-Features mit `isPro` (in CE alle `false`, `components/project/settings/features-list.tsx`), toter `SidebarWorkspaceMenuItem` | Pille „Pro“ (`sidebar.pro`) | entfällt; Funktionen ohne Plan-Grenze anbieten oder ausblenden |
| `ProIcon` | `apps/web/components/common/pro-icon.tsx` | `components/active-cycles/workspace-active-cycles-upgrade.tsx` (Upsell-Seite „Active cycles“) | `Crown` `text-amber-400 h-3.5 w-3.5` | entfällt |
| Billing-Seite (`BillingRoot`, `PlansComparison*`, `PlanDetail`, `PlanFrequencyToggle`, `PlanFeatureDetail`, `PLANS_LIST`, `PLANS_COMPARISON_LIST`, `PLANE_PLANS`, `ComingSoonBadge`) | `apps/web/components/workspace/billing/root.tsx`, `workspace/billing/comparison/{base,feature-detail,frequency-toggle,plan-detail,plans,root}.tsx` | Workspace-Einstellungen „Billing and plans“ (`/settings/billing`, 2.10.1) | Box „Community“ + Planvergleich (Matrix 14 Sektionen, features/20 §2) | Route, Menüeintrag und Komponenten entfallen; Matrix dient nur als Feature-Quelle |

### 2.19 Browser-Persistenz (LocalStorage) dieses Bereichs

| Schlüssel | Inhalt / Default | Quelle |
|---|---|---|
| `app_sidebar_collapsed` | Hauptsidebar eingeklappt (`"true"`/`"false"`) | `apps/web/store/theme.store.ts` |
| `extended_sidebar_collapsed` | „More“-Sidebar | `apps/web/store/theme.store.ts` |
| `extended_project_sidebar_collapsed` | erweiterte Projekt-Sidebar | `apps/web/store/theme.store.ts` |
| `profile_sidebar_collapsed` | Profil-Sidebar (2.8.2) | `apps/web/store/theme.store.ts` |
| `sidebarWidth` | Breite der Hauptsidebar (Default 250, 236–350) | `apps/web/app/(all)/[workspaceSlug]/(projects)/_sidebar.tsx`, `extended-sidebar-wrapper.tsx` |
| `is_workspace_menu_open` | Workspace-Menügruppe offen (Default `true`) | `apps/web/components/workspace/sidebar/sidebar-menu-items.tsx`, `workspace-menu.tsx` |
| `is_favorite_menu_open` (`IS_FAVORITE_MENU_OPEN`) | Favoriten-Sektion offen (Default `false`); wird beim Favorisieren auf `true` gesetzt | `apps/web/components/workspace/sidebar/favorites/favorites-menu.tsx`, `project/card.tsx`, `packages/constants/src/workspace.ts` |
| `isAllProjectsListOpen` | Projektliste offen – wird geschrieben, nie gelesen | `apps/web/components/workspace/sidebar/projects-list.tsx` |
| `draftedIssue` | Entwurf aus der Sidebar-Schnellaktion (`{[ws]: Partial<TIssue>}`) | `apps/web/components/workspace/sidebar/quick-actions.tsx` |
| `quickstart-guide-{ws}` | `{hide, visited_members, visited_workspace, visited_profile}` | `apps/web/components/home/widgets/empty-states/no-projects.tsx` |
| `global_view_filters/{viewId}` | wird beim Löschen einer Workspace-View entfernt | `apps/web/components/workspace/views/delete-view-modal.tsx` |
| `APP_RAIL_{ws}`, `app_rail_preferences` | App-Rail (in CE deaktiviert, 2.2) | `apps/web/lib/app-rail/provider.tsx`, `apps/web/hooks/use-navigation-preferences.ts` |
| `plane_tab_prefs` | Tab-Präferenzen – Hilfsfunktionen ungenutzt (Persistenz serverseitig, 2.4) | `apps/web/components/navigation/tab-navigation-utils.ts` |
| `theme` (next-themes) | Theme-Modus (`light`, `dark`, `light-contrast`, `dark-contrast`, `custom`, Default `system`) | `apps/web/app/root.tsx` (`ThemeProvider`), 2.13 |
| `userLanguage` | UI-Sprache | `packages/i18n/src/constants/language.ts` (`LANGUAGE_STORAGE_KEY`), A13b |

### 2.20 API-Endpunkte dieses Bereichs (Konsolidierung)

Vollständige Service-Tabelle: A08 §2.7; Backend: A03 (Workspace/Projekt/User), A06 (Auth).

| Bereich | Methode + Pfad | Service | Abschnitt |
|---|---|---|---|
| Auth | `GET /auth/get-csrf-token/`; `POST /auth/email-check/`; `POST /auth/magic-generate/`; Formular-POST `/auth/sign-in/`, `/auth/sign-up/`, `/auth/magic-sign-in/`, `/auth/magic-sign-up/`, `/auth/reset-password/{uidb64}/{token}/`; `POST /auth/forgot-password/`; `POST /auth/set-password/`; `POST /auth/change-password/`; Redirect `/auth/{google\|github\|gitlab\|gitea}/` | `apps/web/services/auth.service.ts`, `user.service.ts` | 2.13, 2.14, 2.15 |
| Benutzer | `GET`/`PATCH /api/users/me/`; `DELETE /api/users/me/`; `GET`/`PATCH /api/users/me/profile/`; `GET /api/users/me/settings/`; `PATCH /api/users/me/onboard/`; `PATCH /api/users/me/tour-completed/`; `POST /api/users/me/email/generate-code/`; `PATCH /api/users/me/email/`; `GET`/`PATCH /api/users/me/notification-preferences/`; `GET /api/users/me/workspaces/`; `GET /api/users/last-visited-workspace/` | `apps/web/services/user.service.ts`, `workspace.service.ts` | 2.2, 2.13, 2.15 |
| API-Tokens | `GET`/`POST /api/users/api-tokens/`; `GET`/`DELETE /api/users/api-tokens/{id}` | `packages/services/src/developer/api-token.service.ts` | 2.13 |
| Einladungen | `GET`/`POST /api/users/me/workspaces/invitations/`; `GET`/`POST /api/workspaces/{ws}/invitations/{id}/join/`; `GET`/`POST /api/workspaces/{ws}/invitations/`; `PATCH`/`DELETE /api/workspaces/{ws}/invitations/{id}/`; `POST /api/users/me/workspaces/{ws}/projects/invitations/` | `workspace.service.ts`, `user.service.ts` | 2.10.3, 2.11, 2.15 |
| Workspace | `POST /api/workspaces/`; `GET /api/workspace-slug-check/?slug=`; `GET`/`PATCH`/`DELETE /api/workspaces/{ws}/`; `GET /api/workspaces/{ws}/members/`; `PATCH`/`DELETE /api/workspaces/{ws}/members/{id}/`; `POST /api/workspaces/{ws}/members/leave/`; `GET /api/workspaces/{ws}/workspace-members/me/`; `GET /api/users/me/workspaces/{ws}/project-roles/`; `GET`/`PATCH /api/workspaces/{ws}/sidebar-preferences/`, `PATCH …/sidebar-preferences/{key}/`; `GET`/`PATCH /api/workspaces/{ws}/user-properties/` | `workspace.service.ts`, `user.service.ts` | 2.2, 2.3, 2.10 |
| Projekte | `GET /api/workspaces/{ws}/projects/`, `GET …/projects/details/`, `POST …/projects/`; `GET`/`PATCH`/`DELETE …/projects/{pid}/`; `POST`/`DELETE …/projects/{pid}/archive/`; `POST …/projects/{pid}/members/leave/`; `GET`/`POST …/projects/{pid}/members/`; `PATCH`/`DELETE …/projects/{pid}/members/{id}/`; `GET …/projects/{pid}/project-members/me/`; `GET`/`PATCH …/projects/{pid}/user-properties/`; `GET /api/workspaces/{ws}/project-identifiers?name=`; `GET`/`POST …/projects/{pid}/project-deploy-boards/`, `PATCH`/`DELETE …/project-deploy-boards/{id}/`; `POST`/`DELETE /api/workspaces/{ws}/user-favorite-projects/[{pid}/]` | `apps/web/services/project/*.ts` | 2.3.6, 2.11, 2.12 |
| Favoriten | `GET`/`POST /api/workspaces/{ws}/user-favorites/`; `PATCH`/`DELETE …/user-favorites/{id}/`; `GET …/user-favorites/{id}/group/` | `apps/web/services/favorite/favorite.service.ts` | 2.3.7, 3.4 |
| Home | `GET /api/workspaces/{ws}/home-preferences/`, `PATCH …/home-preferences/{key}/`; `GET`/`POST …/quick-links/`, `PATCH`/`DELETE …/quick-links/{id}/`; `GET …/recent-visits/?entity_name=` | `workspace.service.ts` | 2.5, 3.6 |
| Stickies | `GET`/`POST /api/workspaces/{ws}/stickies/`; `GET …/stickies/{id}`; `PATCH …/stickies/{id}/`; `DELETE …/stickies/{id}` | `apps/web/services/sticky.service.ts` | 2.6 |
| Inbox | `GET /api/workspaces/{ws}/users/notifications/`; `GET …/notifications/unread/`; `PATCH …/notifications/{id}/`; `POST`/`DELETE …/notifications/{id}/read/`; `POST`/`DELETE …/notifications/{id}/archive/`; `POST …/notifications/mark-all-read/` | `apps/web/services/workspace-notification.service.ts` | 2.7, 3.7 |
| Suche | `GET /api/workspaces/{ws}/search/` (Power-K), `GET /api/workspaces/{ws}/entity-search/` (Mentions), `GET …/projects/{pid}/search-issues/` (2.16.4) | `workspace.service.ts`, `project.service.ts` | 2.9, 2.16.4 |
| Profil-Seiten | `GET /api/workspaces/{ws}/user-profile/{userId}/`; `GET …/user-stats/{userId}/`; `GET …/user-activity/{userId}/`; `POST …/user-activity/{userId}/export/`; `GET …/user-issues/{userId}/` | `user.service.ts` | 2.8 |
| Workspace-Views | `GET`/`POST /api/workspaces/{ws}/views/`; `GET`/`PATCH`/`DELETE …/views/{id}/` | `workspace.service.ts` | 2.17 |
| Querschnitt | `DELETE /api/workspaces/{ws}/projects/{pid}/bulk-delete-issues/`; `POST /api/workspaces/{ws}/ai-assistant/`; `GET /api/unsplash/?query=`; `GET /api/timezones/`; Assets `POST /api/assets/v2/user-assets/`, `DELETE /api/assets/v2/user-assets/{id}/`, `DELETE /api/assets/v2/workspaces/{ws}/{id}/`, `DELETE /api/users/file-assets/{key}/`, `DELETE /api/workspaces/file-assets/{wsId}/{key}/` | `issue.service.ts`, `ai.service.ts`, `file.service.ts`, `timezone.service.ts` | 2.16 |

### 2.21 Nicht erreichbarer Code (Importgraph ab `apps/web/app/**`, per Skript über alle `import`/`from`-Angaben ermittelt)

| Pfad (`apps/web/components/…`) | Exporte | Befund |
|---|---|---|
| `workspace/sidebar/workspace-menu.tsx`, `workspace-menu-header.tsx`, `workspace-menu-item.tsx`, `user-menu.tsx`, `user-menu-item.tsx` | `SidebarWorkspaceMenu`, `SidebarWorkspaceMenuHeader`, `SidebarWorkspaceMenuItem`, `SidebarUserMenu`, `SidebarUserMenuItem` | alte Sidebar-Menüs; nur untereinander importiert |
| `workspace-notifications/notification-app-sidebar-option.tsx` | `NotificationAppSidebarOption` | nur aus den toten Sidebar-Menüs |
| `sidebar/search-button.tsx` | `SidebarSearchButton` | kein Importeur |
| `workspace/views/header.tsx` | `GlobalViewsHeader` | kein Importeur (Route nutzt eigenen Header) |
| `project/empty-state.tsx`, `project/integration-card.tsx`, `project/multi-select-modal.tsx` | `EmptyState`, `IntegrationCard`, `ProjectMultiSelectModal` | kein Importeur |
| `settings/layout.tsx` | `SettingsContentLayout` | kein Importeur |
| `profile/profile-setting-content-wrapper.tsx`, `core/sidebar/sidebar-menu-hamburger-toggle.tsx` | `ProfileSettingContentWrapper`, `SidebarHamburgerToggle` | Toggle nur im toten Wrapper |
| `account/auth-forms/set-password.tsx`, `account/auth-forms/index.ts` | `SetPasswordForm`, Barrel | kein Importeur |
| `onboarding/create-or-join-workspaces.tsx`, `create-workspace.tsx`, `invitations.tsx`, `invite-members.tsx`, `profile-setup.tsx`, `step-indicator.tsx` | `CreateOrJoinWorkspaces`, `CreateWorkspace`, `Invitations`, `InviteMembers`, `ProfileSetup`, `OnboardingStepIndicator` | altes Onboarding; nur gegenseitig importiert |
| `auth-screens/workspace/not-a-member.tsx` | `NotAWorkspaceMember` | kein Importeur |
| `common/activity/activity-item.tsx`, `activity-block.tsx`, `helper.tsx`, `user.tsx` | `ActivityItem`, `ActivityBlockComponent`, `iconsMap`, `messages`, `User` | Kette ohne Einstieg |
| `common/latest-feature-block.tsx` | `LatestFeatureBlock` | kein Importeur |
| `home/widgets/links/action.tsx` | `AddLink` | kein Importeur |
| `stickies/action-bar.tsx`, `stickies/modal/index.tsx`, `stickies/modal/stickies.tsx`, `stickies/sticky/sticky-item-drag-handle.tsx` | `StickyActionBar`, `AllStickiesModal`, `Stickies`, `StickyItemDragHandle` | Modal nur über die tote Action-Bar (`stickies/modal/search.tsx` ist dagegen live) |
| `empty-state/helper.tsx` | `getEmptyStateImagePath` | kein Importeur |
| `ui/loader/notification-loader.tsx`, `ui/loader/pages-loader.tsx`, `ui/markdown-to-component.tsx`, `ui/profile-empty-state.tsx` | `NotificationsLoader`, `PagesLoader`, `MarkdownRenderer`, `ProfileEmptyState` | kein Importeur |
| `icons/locked-component.tsx` | `LockedComponent` | kein Importeur |
| `user/index.ts`, `user/user-greetings.tsx` | `UserGreetingsView` | Duplikat von `home/user-greetings.tsx` |
| `workspace/billing/comparison/index.ts`, `workspace/sidebar/help-section/index.ts` | Barrels | ungenutzte Barrel-Dateien (Inhalte werden direkt importiert) |

Zusätzlich erreichbar, aber funktional ohne Wirkung: `AppRailRoot` (`navigation/app-rail-root.tsx`, `isEnabled = false`, 2.2), exportierte, aber nie verwendete Exporte `DocumentIcon`, `TuneIcon`, `ImgIcon` (`icons/attachment/*`), `useIntakeHeaderMenuItems` (`common/quick-actions-helper.tsx`), `getTabPreferences`, `saveTabPreferences`, `getDefaultTabUrl`, `getValidatedDefaultTab` (`navigation/tab-navigation-utils.ts`; nur `getTabUrl`, `DEFAULT_TAB_KEY`, `TTabPreferences` werden importiert), `toggleSidebarPeek(true)` (kein Aufrufer, 3.2).

---

## 3. Verhalten, Logik, Abläufe (inkl. Edge-Cases)

Routing, Guards (`AuthenticationWrapper`, `WorkspaceAuthWrapper`, `ProjectAuthWrapper`), Store-Initialisierung und Trailing-Slash-Regeln sind in A08 §2.2, §2.3 und §3 beschrieben und werden hier vorausgesetzt.

### 3.1 Workspace-Shell: Wechsel, Abmelden, Zähler, Menüs

| Ablauf | Verhalten | Quelle |
|---|---|---|
| Workspace wechseln | Klick auf eine Zeile im Workspace-Menü: Navigation `/{slug}` und parallel `updateUserProfile({last_workspace_id})`; bei Fensterbreite < 768 px wird zusätzlich die Sidebar eingeklappt; Reihenfolge der Liste alphabetisch, aktiver Workspace zuerst | `apps/web/components/workspace/sidebar/workspace-menu-root.tsx`, `dropdown-item.tsx`, `packages/utils/src/workspace.ts` |
| Workspace-Kontextwechsel | Der Projekt-Filter-Store reagiert per MobX-`reaction` auf `router.workspaceSlug`: Display-Filter werden auf `{order_by: bisher‖"created_at"}` zurückgesetzt (übrige Display-Filter wie „My projects“ entfallen), Filter bleiben je Workspace im Speicher, Suchtext wird geleert | `apps/web/store/project/project_filter.store.ts` |
| Abmelden | `signOut()`: `GET /auth/get-csrf-token/`, dann per dynamisch erzeugtem HTML-Formular `POST {API_BASE_URL}/auth/sign-out/` mit `csrfmiddlewaretoken`; danach `resetOnSignOut()` aller Stores; Fehler → Toast `auth.sign_out.toast.error.*` | `apps/web/store/user/index.ts`, `apps/web/services/auth.service.ts` |
| Unread-Zähler (Top-Navigation) | SWR-Key `"WORKSPACE_UNREAD_NOTIFICATION_COUNT"` (ohne Workspace-Slug) → `GET /api/workspaces/{ws}/users/notifications/unread/`; roter Punkt, wenn Mentions > 0, sonst wenn Gesamtzahl > 0; der Zähler wird beim Öffnen der Inbox und bei Lese-Aktionen im Store aktualisiert (3.7) | `apps/web/components/navigation/top-navigation-root.tsx`, `apps/web/store/notifications/workspace-notifications.store.ts` |
| Profil-Einstellungen aus dem User-Menü | „Settings“/„Preferences“ öffnen das Profil-Einstellungs-**Modal** (`toggleProfileSettingsModal`, eingebunden über `GlobalModals` mit `lazy`-Import), nicht die Route `/settings/profile/:tab` (2.13.1) | `apps/web/components/workspace/sidebar/user-menu-root.tsx`, `apps/web/components/common/modal/global.tsx` |
| Hilfe-Menü | externe Ziele per `window.open` (Docs, Forum, `mailto:sales@plane.so`); „Keyboard shortcuts“ öffnet das Power-K-Shortcut-Modal; „What's new?“ öffnet `ProductUpdatesModal` mit `iframe` auf `instance_changelog_url` (2.16.9) | `apps/web/components/workspace/sidebar/help-section/root.tsx` |
| Dropdown-Sperre | Öffnen eines Sidebar-Dropdowns (Workspace-Menü, Projekt-Menüs) setzt `toggleAnySidebarDropdown(true)`; der Theme-Store nutzt das, um Peek/Extended-Sidebars nicht durch Außenklick zu schließen (3.2) | `workspace-menu-root.tsx`, `apps/web/store/theme.store.ts` |
| Power-K in der Top-Navigation | Suchfeld wächst beim Fokus von 364 auf 554 px und öffnet das Panel (574 px); Tastatur und Zustandsmaschine wie das Modal (3.9) | `apps/web/components/navigation/top-nav-power-k.tsx` |

### 3.2 Sidebar: Größe, Collapse, Peek, Mobile

| Ablauf | Verhalten im Detail | Quelle |
|---|---|---|
| Breite | `ResizableSidebar` mit `minWidth=236`, `maxWidth=350`; Startbreite `localStorage["sidebarWidth"] ?? 250` (`SIDEBAR_WIDTH`); Ziehen am Griff (rechter Rand, `w-1 cursor-ew-resize`, aktiv `w-1.5 bg-layer-1`) setzt `document.body.style.cursor="col-resize"` und `userSelect="none"`; jede Breitenänderung wird sofort persistiert (`onWidthChange → setValue`) | `apps/web/components/sidebar/resizable-sidebar.tsx`, `apps/web/app/(all)/[workspaceSlug]/(projects)/_sidebar.tsx` |
| Einklappen | Toggle-Button im Sidebar-Kopf (`AppSidebarToggleButton`: schließt zuerst Peek, dann `toggleSidebar()`), Doppelklick auf den Resize-Griff, Power-K-Befehl/Shortcut (s. 2.9); Zustand im Theme-Store `sidebarCollapsed` + `localStorage["app_sidebar_collapsed"]` (A08 §2.10). Eingeklappt: `w-0 translate-x-[-100%] opacity-0`, Animation `transition-all duration-300 ease-in-out` (nicht während Resize) | `sidebar-toggle-button.tsx`, `resizable-sidebar.tsx` |
| Peek | Im eingeklappten Zustand rendert `ResizableSidebar` eine zweite Kopie der Sidebar als Overlay (`absolute left-0 z-20 shadow-sm`, `translate-x-0 opacity-100` bei `sidebarPeek`, `pointer-events-auto`). Beim Verlassen des Overlays schließt es nach `peekDuration=1500` ms – **nicht**, solange eine Extended-Sidebar oder ein Sidebar-Dropdown (`isAnySidebarDropdownOpen`) offen ist; schließt sich das Dropdown/Extended später und `isHoveringTrigger` ist gesetzt, startet der Timer erneut; Wiederbetreten bricht den Timer ab. **Edge-Case:** In der CE ruft kein Code `toggleSidebarPeek(true)` auf (einzige Aufrufer setzen `false`: `sidebar-toggle-button.tsx`, `resizable-sidebar.tsx`), `isHoveringTrigger` wird nie `true` → Peek ist faktisch unerreichbar. Für 1:1 nicht nachbauen oder als Option dokumentieren | `resizable-sidebar.tsx`, `_sidebar.tsx`, `apps/web/components/sidebar/sidebar-toggle-button.tsx` |
| Toggle-Button im Seiten-Header | `ExtendedAppHeader` zeigt `AppSidebarToggleButton` links vor dem Seiten-Header, **nur** wenn die Sidebar eingeklappt ist und (Navigation-Modus `ACCORDION` oder Seite ohne `projectId`/`workItem`) | `apps/web/components/common/extended-app-header.tsx` |
| Mobile (< 768 px) | Fenster < 768 px → Sidebar wird automatisch eingeklappt (`useSize`-Effekt); Klick außerhalb der Sidebar klappt sie ein; jeder Navigationsklick (Item, Projektunterpunkt, Workspace-Wechsel, Favorit) klappt ein. Auf Mobilgeräten (`usePlatformOS().isMobile`) ist die Sidebar `absolute` und trägt `data-prevent-outside-click` | `apps/web/components/sidebar/sidebar-wrapper.tsx`, `sidebar-item.tsx`, `project-navigation.tsx`, `favorite-item-title.tsx` |
| Notifications-Route | `ProjectAppSidebar` liefert `null`, wenn `pathname` `/${ws}/notifications` enthält (Inbox hat eigene linke Spalte) | `_sidebar.tsx` |
| Extended-Sidebars | „More“ (Workspace-Items) und „More“ (Projekte) sind getrennte Theme-Store-Flags (`isExtendedSidebarOpened`, `isExtendedProjectSidebarOpened`, persistiert als `extended_sidebar_collapsed`/`extended_project_sidebar_collapsed`); beide schließen bei Außenklick (Ausnahme: ihr Toggle-Element) und beim Einklappen der Haupt-Sidebar | `extended-sidebar-wrapper.tsx`, `apps/web/store/theme.store.ts` |

### 3.3 Sidebar: Projektliste, Navigation-Modus, Drag&Drop

| Ablauf | Verhalten | Quelle |
|---|---|---|
| Klick auf Projektzeile (ACCORDION) | Toggle der Unterpunkte (`toggleProjectListOpen`); der umschließende `ControlLink` hat `href=defaultTabUrl` – Strg/Cmd-Klick öffnet die Default-Tab-URL in neuem Tab, normaler Klick navigiert **nicht** | `projects-list-item.tsx`, `@plane/blocks/layout` (`ControlLink`) |
| Klick auf Projektzeile (TABBED) | `router.push(defaultTabUrl)`; schließt die Extended-Projekt-Sidebar. `defaultTabUrl` = `getTabUrl(ws, pid, defaultTab)` mit `defaultTab` aus den Projekt-User-Properties (`preferences.navigation.default_tab`), validiert gegen die verfügbaren Tabs, sonst `work_items` | `projects-list-item.tsx`, `apps/web/components/navigation/tab-navigation-utils.ts`, `use-tab-preferences.ts` |
| Aktiver Unterpunkt | `ProjectNavigation.isActive`: `pathname.includes(item.href)` **oder** (Item `work_items` und die Route `/browse/:workItem` zeigt ein Nicht-Epic dieses Projekts) **oder** (Item `epics` und Epic) | `project-navigation.tsx` |
| Projekte umsortieren | `orderJoinedProjects(sourceIndex, destinationIndex, …)` (`packages/utils/src/project.ts`): oben → `sort_order(erstes) − 10000`, unten → `sort_order(letztes) + 10000`, Mitte → Mittelwert; `updateProjectView(ws, pid, {sort_order})` → `PATCH /api/workspaces/{ws}/projects/{pid}/user-properties/` (optimistisch, A08 §3.3); Fehler → Toast „Error“/„Something went wrong“. Projekte mit `sort_order === null` (nicht beigetreten) zeigen „Join the project to rearrange“, sind aber technisch ziehbar (`canDrag` prüft das nicht) | `projects-list.tsx`, `extended-project-sidebar.tsx` |
| Projektlimit | Sidebar zeigt die ersten N (`navigation_project_limit`); Rest über „More“ → Extended-Projekt-Sidebar mit Suche | `projects-list.tsx`, `use-navigation-preferences.ts` |
| Navigation-Modus wechseln | Radio im Customize-Dialog → sofortiger PATCH, kein Speichern-Button; ACCORDION zeigt Unterpunkte in der Sidebar, TABBED zeigt Tab-Leiste im Header jeder Projektseite (s. 2.4) | `customize-navigation-dialog.tsx` |

### 3.4 Sidebar: Favoriten-Drag&Drop (vollständige Regeln)

Datenmodell: `IFavorite` mit `id`, `name`, `entity_type` (`project|cycle|module|view|page|folder`), `entity_identifier`, `entity_data {name, logo_props}`, `project_id`, `is_folder`, `parent`, `sequence`, `sort_order`, `children` (Store `apps/web/store/favorite.store.ts`; Endpunkte `GET/POST /api/workspaces/{ws}/user-favorites/`, `PATCH/DELETE …/user-favorites/{id}/`, `GET …/user-favorites/{id}/group/`, `apps/web/services/favorite/favorite.service.ts`).

| Regel | Detail | Quelle |
|---|---|---|
| Drag-Daten | Ordner `{id, isGroup:true, isChild:false}`; Favorit `{id, isGroup:false, isChild:!!parentId, parentId}` | `favorite-folder.tsx`, `favorite-items/root.tsx` |
| `canDrop` | nicht auf sich selbst; ein Ordner darf nicht auf ein Kind-Element (Favorit in Ordner) gezogen werden | `favorites.helpers.ts` (`getCanDrop`) |
| Instruktion | Mehrere Drop-Ziele und Ziel ist Ordner → `make-child`; `instruction-blocked` → bei Kind `reorder-above`, sonst `make-child`; Quelle ist Ordner und Instruktion `make-child` → `reorder-above`. Ordner blockieren `reorder-below` (außer letztes Element); Favoriten blockieren `make-child` und `reorder-below` (außer letztes) | `favorites.helpers.ts` (`getInstructionFromPayload`), `favorite-folder.tsx`, `favorite-items/root.tsx` |
| Visualisierung | `DropIndicator` oben (`reorder-above`) bzw. unten beim letzten Element (`reorder-below`); Ordner mit `make-child` erhält `border-[2px] border-accent-strong`; gezogenes Element `bg-layer-1 opacity-60` | `favorite-folder.tsx`, `favorite-items/root.tsx` |
| Drop auf Ordner | `parentId` (bei `make-child` = Ziel-ID, sonst `parentId` des Ziels) ≠ bisheriger Parent → `moveFavoriteToFolder` = `PATCH {parent: parentId}`; zusätzlich bei Nicht-`make-child` → `reOrderFavorite` | `favorites-menu.tsx` (`handleDrop`) |
| Drop auf Favorit | `reOrderFavorite(id, zielId, edge)` | `favorites-menu.tsx` |
| Aus Ordner herausziehen | Ziel ohne Parent und Quelle ist Kind → `removeFromFavoriteFolder` = `PATCH {parent: null}` | `favorites-menu.tsx` |
| Sequenzberechnung | Basis 10000; Liste aller Favoriten `sequence desc`; `reorder-above`: Vorgänger vorhanden → Mittelwert(Ziel, Vorgänger), sonst `Ziel + 10000`; `reorder-below` → `Ziel − 10000`; ohne `edge` → 10000; `PATCH {sequence}` | `apps/web/store/favorite.store.ts` (`reOrderFavorite`) |
| Ordner anlegen | Name schon vorhanden (`existingFolders` = Namen **aller** Favoriten, nicht nur Ordner) → Toast „Folder already exists“; leer nach `trim` → „Folder name cannot be empty“; sonst `POST {entity_type:"folder", is_folder:true, name, parent:null, project_id:null}` (optimistisch mit temporärer ID), Toast „Favorite created successfully“; Formular schließt sofort | `new-fav-folder.tsx`, `favorite.store.ts` |
| Ordner umbenennen | gleiche Validierung, `PATCH {name}`, Toast „Favorite updated successfully“ | `new-fav-folder.tsx` |
| Entfernen | `DELETE` → Toast „Favorite removed successfully“; Fehler „Something went wrong“ | `favorites-menu.tsx` |
| Fehler-Toasts | Verschieben „Failed to move favorite“, Umsortieren „Failed to reorder favorite“ | `favorites-menu.tsx` |
| Edge-Case | Drop auf den Sektionskopf „Favorites“ ruft nur `console.log({sourceId})` auf, keine Aktion | `favorites-menu.tsx` |

### 3.5 Projektliste und Projekt-Lebenszyklus

| Ablauf | Verhalten | Quelle |
|---|---|---|
| Filterung der Projektliste | `filteredProjectIds` = Projekte des aktuellen Workspace, deren `name` **oder** `identifier` den Suchtext enthält (case-insensitive) und `shouldFilterProject` erfüllen: `access` ⊇ `network`, `lead` ∋ `project_lead`, `members` ∩ `project.members` ≠ ∅, alle `created_at`-Filter erfüllt (`satisfiesDateFilter`: `today`, `yesterday`, `last_7_days`, `last_30_days` oder `YYYY-MM-DD;after\|before`); Display-Filter `my_projects` → nur mit `member_role`; archivierte Projekte nur, wenn `archived_projects` gesetzt (Archiv-Seite), und dann nur archivierte | `apps/web/store/project/project.store.ts`, `packages/utils/src/project.ts`, `packages/utils/src/filter.ts` |
| Sortierung | `orderProjects`: `sort_order` (Manual), `name`/`-name` (lowercase), `created_at` (Default, aufsteigend), `-created_at` sortiert nach `!created_at` → **behält die Server-Reihenfolge**, `members_length`/`-members_length`; jeder andere Schlüssel liefert eine **leere Liste** | `packages/utils/src/project.ts` |
| Filterzustand | nur im Speicher (`project_filter.store.ts`), je Workspace; Archiv-Seite setzt bei jedem Pfadwechsel `archived_projects = isArchived`; „Clear all“ löscht Filter und Display-Filter (Archiv-Flag wird danach wieder gesetzt); Zähler „gefiltert/gesamt“ im Kopf der Filterleiste | `apps/web/components/project/root.tsx`, `apps/web/store/project/project_filter.store.ts` |
| Projekt anlegen | Schritt 1 validiert Name (Pflicht, ≤ 255) und Identifier (Pflicht, Regex `/^[ÇŞĞIİÖÜA-Z0-9]+$/`, 1–10 Zeichen); Identifier wird aus dem Namen erzeugt, bis der Nutzer ihn ändert; Speichern: ggf. Cover-Upload (statisches Cover → Upload als Asset), `POST /api/workspaces/{ws}/projects/`, danach Asset-Status/`cover_image_url`-PATCH; Erfolg → Schritt 2 (Feature-Schalter) statt Schließen; Fehlercodes `PROJECT_NAME_ALREADY_EXIST`, `PROJECT_IDENTIFIER_ALREADY_EXIST`, `PROJECT_NAME_CANNOT_CONTAIN_SPECIAL_CHARACTERS` als Toast (2.11.2) | `apps/web/components/projects/create/root.tsx`, `apps/web/components/project/create/common-attributes.tsx` |
| Nach Anlage | `processProjectAfterCreation` legt das Projekt in `projectMap` ab und setzt die Projektrolle aus `member_role` der Antwort in `workspaceProjectsPermissions`; Projekt erscheint sofort in Sidebar und Liste | `apps/web/store/project/project.store.ts` |
| Favorisieren | Projektkarte/Sidebar: `POST /api/workspaces/{ws}/user-favorite-projects/` bzw. `DELETE …/{pid}/` mit Promise-Toast; nach Hinzufügen `localStorage.is_favorite_menu_open = true` (Favoriten-Sektion geht auf) | `apps/web/components/project/card.tsx`, `apps/web/services/project/project.service.ts` |
| Beitreten | Nicht-Mitglied klickt Karte/„Join“ → `JoinProjectModal` → `POST /api/users/me/workspaces/{ws}/projects/invitations/ {project_ids}` → Navigation `/…/projects/{id}/issues`; Fehler nur in der Konsole; Zugriffsschutz bei Direktaufruf: `ProjectAccessRestriction` (2.14.4) | `apps/web/components/project/join-project-modal.tsx` |
| Verlassen | Sidebar-/Tab-Menü „Leave project“ (nur Gast) → `LeaveProjectModal` (Name + „Leave Project“ eintippen; Redirect **vor** dem Request); Mitgliederliste „Leave“ → `ConfirmProjectMemberRemove` (Request, dann Redirect) | `apps/web/components/project/leave-project-modal.tsx`, `confirm-project-member-remove.tsx` |
| Archivieren / Wiederherstellen | `POST`/`DELETE /api/workspaces/{ws}/projects/{pid}/archive/` → Redirect `/{ws}/projects/`; archivierte Projekte verschwinden aus Sidebar und Liste und sind nur unter `/projects/archives` sichtbar (Karte ohne Navigation, Admin: „Restore“/Löschen) | `apps/web/components/project/archive-restore-modal.tsx`, `apps/web/services/project/project-archive.service.ts` |
| Löschen | doppelte Texteingabe (Projektname + „delete my project“) → `DELETE /api/workspaces/{ws}/projects/{pid}/`; war die aktuelle Route im Projekt → `/{ws}/projects` | `apps/web/components/project/delete-project-modal.tsx` |
| Veröffentlichen | `PublishProjectModal` (2.11.4): Publish/Update/Unpublish über `project-deploy-boards`; mindestens ein Layout Pflicht; öffentliche URL `{SPACE_BASE_URL‖origin}{SPACE_BASE_PATH}/issues/{anchor}` (Space-App, A11) | `apps/web/components/project/publish-project/modal.tsx` |
| Feature-Schalter | `PATCH` Projekt `{cycle_view\|module_view\|issue_views_view\|page_view\|inbox_view}`; ausgeschaltete Features verschwinden sofort aus Sidebar-/Tab-Navigation (`shouldRender: project.<flag>` in `ProjectNavigation`, 2.4.1); Verhalten der Feature-Routen bei deaktiviertem Feature: A10b | `apps/web/components/settings/project/content/feature-control-item.tsx`, `apps/web/components/workspace/sidebar/project-navigation.tsx` |
| Tab-Navigation | Projekt-Switcher übernimmt den **validierten Default-Tab des aktuell geöffneten Projekts** für das Zielprojekt; „Set as default“/„Hide in more menu“ schreiben Projekt-User-Properties (2.4.2) | `apps/web/components/navigation/project-header.tsx`, `use-tab-preferences.ts` |

### 3.6 Home, Quick Links, Recents, Stickies – Abläufe und Edge-Cases

| Ablauf / Edge-Case | Verhalten | Quelle |
|---|---|---|
| Erster Besuch | Server legt Home-Präferenzen an (3 Widgets aktiv); Client zeigt Loader, bis sowohl `home.loading === false` als auch `project.loader === "loaded"` | `apps/web/components/home/home-dashboard-widgets.tsx`, `apps/api/plane/app/views/workspace/home.py` |
| Produkt-Tour | Tour-Overlay liegt **über** dem Home-Inhalt, solange `is_tour_completed` false ist; erscheint nur auf der Home-Seite | `apps/web/components/home/root.tsx` |
| Widget-Reihenfolge | `sort_order` absteigend; neue Positionen werden halbiert bzw. ±10000 – keine Normalisierung (Gleitkomma-Erosion möglich) | `apps/web/store/workspace/home.ts` |
| Widget-Toggle-Fehler | kein Toast, nur Konsole | `apps/web/store/workspace/home.ts`, `widget-item.tsx` |
| Quick-Link-URL | Prüfung nur „nicht leer“; `startsWith("http")` entscheidet über Präfix `http://` (auch für `https`-lose Eingaben wie `www.x.de`, aber `httpfoo` bleibt unverändert) | `apps/web/components/home/widgets/links/create-update-link-modal.tsx` |
| Quick-Link löschen | ohne Bestätigungsdialog; Toast-Titel = Message | `link-detail.tsx`, `use-links.tsx` |
| Recents-Filter | Wechsel erzeugt neuen SWR-Key → neuer Request; Ergebnis pro Filter gecacht, keine Revalidierung bei Fokus | `apps/web/components/home/widgets/recents/index.tsx` |
| Recents-Klick Work Item | `ControlLink` mit `onItemClick` → `preventDefault` + Peek; Strg/Cmd-Klick öffnet Link `generateWorkItemLink` (Browse-URL) in neuem Tab | `recents/issue.tsx`, `apps/web/components/core/list/list-item.tsx` |
| Quickstart „Configure this workspace“ | relativer Link `settings`; korrekt nur, weil die Home-URL mit `/` endet (Trailing-Slash-Erzwingung, A08 §2.1) | `no-projects.tsx` |
| Quickstart-Status | rein lokal pro Browser (`localStorage["quickstart-guide-${ws}"]`), nicht serverseitig | `no-projects.tsx` |
| Sticky anlegen | Nur wenn `showAddNewSticky` gesetzt ist (Aufrufer setzen vorher `toggleShowNewSticky(true)`), sonst no-op; Warn-Toast „There already exists a sticky with no description“, wenn das oberste Sticky (höchste `sort_order`) leer ist (`isCommentEmpty`); Name > 100 Zeichen → Fehler-Toast; Erfolg-Toast „Sticky created“; neues Sticky wird vorne eingefügt und `activeStickyId`/`recentStickyId` | `apps/web/components/stickies/sticky/use-operations.tsx`, `apps/web/store/sticky/sticky.store.ts` |
| Sticky bearbeiten | jede Editor-Änderung → `handleSubmit` → Debounce 500 ms → `PATCH {description_html}` (leer → `"<p></p>"`); Farbwahl sofort `PATCH {background_color}`; optimistisch, Revert bei Fehler + Toast „Sticky not updated“; nach Änderung Masonry-Relayout | `sticky/root.tsx`, `sticky/inputs.tsx` |
| Sticky löschen | Bestätigungsdialog → optimistisch entfernen, `recentStickyId` = erstes verbleibendes; Toast „Sticky removed“ | `sticky/root.tsx`, `sticky.store.ts` |
| Sticky umsortieren | nur auf `/stickies`; Instruktion aus Hitbox (`reorder-above`/`reorder-below`); Sequenz wie Widgets (Basis 10000), optimistisch mit Revert | `layout/stickies-list.tsx`, `sticky.store.ts` |
| Suche + Pagination | Folgeseiten verwenden die aktuelle `searchQuery`; Suche lädt die erste Seite neu (`STICKIES_PER_PAGE:0:0`) | `sticky.store.ts` |

### 3.7 Inbox – Abläufe und Edge-Cases

| Ablauf | Verhalten | Quelle |
|---|---|---|
| Laden | SWR `WORKSPACE_NOTIFICATION_${ws}` → `getNotifications(ws, loader, cursorType)`: erster Aufruf `INIT_LOADER`/`INIT`, danach `MUTATION_LOADER`/`CURRENT`; vor jedem Listenabruf wird `GET …/users/notifications/unread/` geholt | `apps/web/components/workspace-notifications/root.tsx`, `apps/web/store/notifications/workspace-notifications.store.ts` |
| Query-Parameter | `GET /api/workspaces/{ws}/users/notifications/?type=<assigned,created,subscribed als CSV>&snoozed=<bool>&archived=<bool>&read=<false wenn "Show unread", sonst weggelassen>&per_page=300&cursor=300:0:0[&mentioned=true]` | `workspace-notifications.store.ts` (`generateNotificationQueryParams`) |
| Client-Filter | Liste = Store-Benachrichtigungen des Workspace, sortiert `created_at` absteigend; Tab Mentions → nur `is_mentioned_notification`, Tab All → **nur nicht**-erwähnte; ohne Archiv-/Snooze-Filter werden archivierte und gesnoozte ausgeblendet; mit Snooze-Filter nur gesnoozte; mit Archiv-Filter nur archivierte; Lesestatus-Filter clientseitig auskommentiert | `workspace-notifications.store.ts` (`notificationIdsByWorkspaceId`) |
| Tab-/Filterwechsel | `setCurrentNotificationTab`, `updateFilters`, `updateBulkFilters` setzen den Wert, **leeren `notifications` komplett** und laden mit `INIT_LOADER`/`INIT` neu (Skeleton erscheint erneut) | `apps/web/store/notifications/workspace-notifications.store.ts`, `apps/web/components/workspace-notifications/sidebar/root.tsx` |
| Klick auf Zeile | Peek schließen, Auswahl setzen, wenn ungelesen → `POST …/notifications/{id}/read/` (optimistisch, Unread-Zähler −1, Revert bei Fehler); kein Intake → `setPeekIssue({ws, projectId, issueId})`. Klick wird ignoriert, solange Snooze-Menü oder Custom-Dialog offen sind | `.../notification-card/item.tsx`, `apps/web/store/notifications/notification.ts` |
| Lesen/Ungelesen | `POST` bzw. `DELETE …/notifications/{id}/read/` | `apps/web/services/workspace-notification.service.ts` |
| Archivieren | `POST` bzw. `DELETE …/notifications/{id}/archive/` (optimistisch) | ebd. |
| Snooze | `PATCH …/notifications/{id}/ {snoozed_till: ISO}`; Un-Snooze `PATCH {snoozed_till: undefined}` (Feld fehlt im JSON – Backend muss das als „löschen“ interpretieren; zu prüfen in A03) | `notification.ts`, `workspace-notification.service.ts` |
| Custom-Snooze Zeitberechnung | AM: Stunde wie gewählt (12 AM bleibt **12**, nicht 0 → Fehler im Original); PM: +12, 12 PM → `00` (ebenfalls vertauscht) | `.../options/snooze/modal.tsx` (`onSubmit`) |
| Mark all as read | `POST …/notifications/mark-all-read/ {type, snoozed, archived, read}`; danach Unread-Zähler des **aktuellen Tabs** auf 0 und `read_at` aller geladenen Benachrichtigungen gesetzt; Doppelklick-Schutz über `loader` | `workspace-notifications.store.ts` |
| Mobile | Auswahl blendet Liste aus (`w-0`), Detail füllt Bildschirm; zurück nur über `embedRemoveCurrentNotification` (Schließen im Peek) | `sidebar/root.tsx`, `root.tsx` |
| Seitenwechsel | beim Unmount wird `setPeekWorkItem(undefined)` aufgerufen; die Auswahl bleibt im Store erhalten | `root.tsx` |

### 3.8 Einstellungen, Profil, Auth und Onboarding – Abläufe

#### 3.8.1 Rechte-Matrix der Oberflächen dieses Bereichs

Rollenwerte: Admin = 20, Member = 15, Guest = 5 (`EUserPermissions`, A08 §2.5). „WS“ = Workspace-Rolle, „PRJ“ = Projektrolle.

| Oberfläche | Sichtbar / bedienbar für | Quelle |
|---|---|---|
| Workspace-Einstellungen General, Members, Exports | WS Admin, Member (Member: General nur lesend, `opacity-60`) | `packages/constants/src/settings/workspace.ts` (`WORKSPACE_SETTINGS`, `WORKSPACE_SETTINGS_ACCESS`), `apps/web/components/workspace/settings/workspace-details.tsx` |
| Billing, Webhooks | WS Admin | ebd. |
| Mitglieder einladen, Rollen ändern, Einladungen verwalten | WS Admin; Rollenauswahl nur ≤ eigener Rolle | `apps/web/components/workspace/settings/member-columns.tsx`, `invitations-list-item.tsx` |
| Workspace löschen, Logo ändern | WS Admin | `workspace-details.tsx`, `delete-workspace-section.tsx` |
| Projekt-Einstellungen General | alle Projektrollen sichtbar, bearbeitbar nur PRJ Admin | `apps/web/components/project/form.tsx` |
| Projekt-Members | PRJ Admin/Member oder WS Admin; „Add member“ und Defaults nur PRJ Admin | `.../projects/[projectId]/members/page.tsx`, `apps/web/components/project/member-list.tsx` |
| Projekt-Features, Estimates, Automations | PRJ Admin | `packages/constants/src/settings/project.ts`, 2.11.1 |
| States, Labels | PRJ Admin, Member | ebd. |
| Projekt anlegen | WS Admin, Member („Add Project“, Power-K `create_project`) | `apps/web/components/project/header.tsx` |
| Projekt archivieren/löschen | PRJ Admin (Einstellungen) bzw. WS/PRJ Admin im Archiv | `apps/web/components/project/settings/control-section.tsx`, `apps/web/components/project/card.tsx` |
| „Leave project“ im Projektmenü | nur PRJ Guest (Admin/Member verlassen über die Mitgliederliste) | `apps/web/components/workspace/sidebar/projects-list-item.tsx`, `apps/web/components/navigation/project-actions-menu.tsx` |
| Profil-Seiten „Your work“ (Issue-Tabs, Activity, Download) | WS Admin, Member; Guest nur „Summary“ | `apps/web/app/(all)/[workspaceSlug]/(projects)/profile/[userId]/layout.tsx` |
| Home-Widgets verwalten, Quick links, Stickies | jeder angemeldete Nutzer (Daten nutzerbezogen) | 2.5, 2.6 |

#### 3.8.2 Speichermuster

| Muster | Verwendet in | Verhalten |
|---|---|---|
| Formular + Button „Save/Update“ | Workspace-General, Projekt-General, Profil-General, Custom-Theme | `react-hook-form`; Button während Submit „…ing“; Erfolg-Toast; Fehler-Toast (Workspace-General: nur Konsole) |
| Sofort-Speichern pro Control | Projekt-Members-Defaults, Feature-Schalter, E-Mail-Benachrichtigungen, Sprache, Zeitzone, Wochenstart, Rollenwechsel, Home-Widget-Schalter, Navigation-Präferenzen | `PATCH` je Änderung, Toast pro Aktion (Home-Widgets ohne Fehler-Toast) |
| Optimistisch mit Revert | Favoriten, Sidebar-Reihenfolgen, Stickies, Inbox-Lesen/Archivieren, Tour abgeschlossen | Store-Update vor Request, Rücksetzen bei Fehler (3.4, 3.6, 3.7) |
| Promise-Toast (`setPromiseToast`) | Projekt-Favorit, Feature-Schalter, Theme, Profil speichern | Loading-, Erfolgs- und Fehlertext in einem Toast |
| Reload | Theme-Wechsel (Profil und Power-K), Custom-Theme | `window.location.reload()` nach erfolgreichem PATCH (Custom: nach 1500 ms) |
| Doppelte Texteingabe vor Löschen | Workspace löschen („delete my workspace“), Projekt löschen („delete my project“), Projekt verlassen („Leave Project“) | Button erst aktiv bzw. Prüfung clientseitig bei exakter Eingabe |

#### 3.8.3 Weiterleitungen nach destruktiven Aktionen

| Aktion | Ziel | Quelle |
|---|---|---|
| Workspace löschen | `getWorkspaceRedirectionUrl()` nach Neuladen der User-Settings (nächster Workspace bzw. `/create-workspace`) | `apps/web/components/workspace/delete-workspace-form.tsx` |
| Workspace verlassen | `fetchCurrentUserSettings()` → `getWorkspaceRedirectionUrl()` | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx` |
| Projekt archivieren/wiederherstellen | `/{ws}/projects/` | `apps/web/components/project/archive-restore-modal.tsx` |
| Projekt löschen | `/{ws}/projects` (nur wenn man sich im Projekt befand) | `apps/web/components/project/delete-project-modal.tsx` |
| Projekt verlassen | `/{ws}/projects` | `leave-project-modal.tsx`, `confirm-project-member-remove.tsx` |
| Konto deaktivieren | `signOut()` → `/` | `apps/web/components/account/deactivate-account-modal.tsx` |
| E-Mail geändert | Toast „Email updated successfully. Please sign in again.“ → Abmelden | `apps/web/components/core/modals/change-email-modal.tsx` |
| Work Item löschen (Power-K) | `/{ws}/projects/{pid}/issues` bzw. `/epics` | `apps/web/components/modals/work-item-level.tsx` |
| Workspace-View anlegen | `/{ws}/workspace-views/{id}` | `apps/web/components/workspace/views/modal.tsx` |

#### 3.8.4 Auth-Ablauf (Zustandsautomat `AuthRoot`)

| Zustand | Eingang | Übergang |
|---|---|---|
| Start | Route `/` (Sign-in) bzw. `/sign-up`; Query `email`, `error_code`, `next_path`, `invitation_id`, `slug` | Mit `error_code` → Banner + Schritt gemäß Code (2.14.2); Einladung mit passender E-Mail → Einladungs-Überschrift |
| EMAIL | „Continue“ | `POST /auth/email-check/` → `existing`/Modus-Korrektur; `status MAGIC_CODE` → UNIQUE_CODE (+ `magic-generate`, nur mit SMTP); `CREDENTIAL` → PASSWORD |
| PASSWORD | Submit | HTML-Formular-POST (Server setzt Session-Cookie und leitet weiter, A06); „Sign in with unique code“ → UNIQUE_CODE; Clear-Button → EMAIL |
| UNIQUE_CODE | Submit / „Resend“ | HTML-Formular-POST `magic-sign-in\|up`; Resend nach Timer erneut `magic-generate` |
| OAuth | Klick Provider-Button | `window.location.assign(API_BASE_URL/auth/<provider>/[?next_path])` |
| Nach Login | Server-Redirect | `AuthenticationWrapper` entscheidet: nicht onboarded → `/onboarding`; sonst `next_path` oder letzter Workspace (A08 §2.3.1) |

#### 3.8.5 Onboarding-Steuerung

| Regel | Verhalten | Quelle |
|---|---|---|
| Schrittfolge Cloud | PROFILE_SETUP → ROLE_SETUP → USE_CASE_SETUP → (Workspace vorhanden ? Ende : WORKSPACE_CREATE_OR_JOIN) → (Einladungen angenommen oder „Just myself“ ? Ende : INVITE_MEMBERS) → Ende | `apps/web/components/onboarding/root.tsx` |
| Schrittfolge Self-managed | PROFILE_SETUP → (Workspace vorhanden ? Ende : WORKSPACE_CREATE_OR_JOIN) → … (ohne ROLE/USE_CASE) | ebd. |
| Wiederaufnahme | aus `profile.onboarding_step`: `profile_complete` ohne `workspace_create`/`workspace_join` → Schritt 4; mit `workspace_create` ohne `workspace_invite` → Schritt 5 | ebd. |
| Abschluss | `finishUserOnboarding`: Profil `onboarding_step` alle `true` + `last_workspace_id` → `PATCH /api/users/me/onboard/` → Neuladen von Profil und Settings; Weiterleitung durch `AuthenticationWrapper` | `apps/web/store/user/profile.store.ts` |
| Produkt-Tour | nach dem Onboarding auf der Home-Seite, solange `is_tour_completed === false`; Abschluss oder „No thanks“ → `PATCH /api/users/me/tour-completed/` | `apps/web/components/home/root.tsx`, `apps/web/components/onboarding/tour/root.tsx` |
| Konto wechseln | „Wrong e-mail address?“ → Abmelden, Theme `system`, `/` | `apps/web/components/onboarding/switch-account-modal.tsx` |

### 3.9 Power-K – Tastatur-Algorithmus, Modal-Zustandsmaschine, Edge-Cases

#### 3.9.1 Globaler Shortcut-Handler (`apps/web/components/power-k/core/shortcut-handler.ts`)

Reihenfolge der Prüfungen bei jedem `keydown` auf `document`:

1. Handler deaktiviert (`destroy()`) → ignorieren. `e.repeat` (Auto-Repeat) → ignorieren.
2. **Ctrl/⌘ + K** (Taste über Layout-Map aufgelöst) → `preventDefault`, Sequenz zurücksetzen, Palette **umschalten** (`togglePowerKModal()`) – funktioniert auch in Eingabefeldern.
3. `e.defaultPrevented` (z. B. Editor-Keymaps, cmdk) → Sequenz zurücksetzen, Ende.
4. Ziel ist Eingabe (`input`, `textarea`, `select`, `contentEditable`, ARIA-Rollen `textbox|searchbox|combobox|spinbutton|listbox|option|menu|menuitem|menuitemcheckbox|menuitemradio` oder Vorfahre `[role=dialog]`, `[role=alertdialog]`, `[role=menu]`, `[role=listbox]`, `.ProseMirror`) → Sequenz zurücksetzen, Ende.
5. Irgendein Modifier (Ctrl/⌘, Alt, Shift) → Sequenz zurücksetzen; Zeichenkette `cmd`(für Ctrl **oder** ⌘)`+alt+shift+<taste>` bilden und in der Modifier-Map suchen; Treffer und `canExecute` → `preventDefault` + ausführen.
6. Sonst Einzeltaste/Sequenz: nicht druckbare Taste (Länge ≠ 1) → Sequenz zurücksetzen. Druckbare Taste an Puffer anhängen; exakter Sequenztreffer → ausführen + zurücksetzen; Puffer ist Präfix einer Sequenz → 1000-ms-Timer neu starten und warten; Puffer hat Länge 1 und ist kein Präfix → Einzeltasten-Map; Puffer länger und kein Präfix → zurücksetzen und prüfen, ob die neue Taste selbst eine Sequenz beginnt (keine Umdeutung als Einzeltaste).
7. `canExecute`: `isVisible`, `isEnabled` und (bei Kontextbefehlen) passender `activeContext`. Ausführen: `action` → direkt (Palette bleibt zu); `change-page` → Palette öffnen, `activeCommand` und `activePage` setzen.

Tastenauflösung (`resolveShortcutKey`): Leertaste → `space`; benannte Tasten → lowercase `e.key`; druckbare Zeichen bevorzugt über `navigator.keyboard.getLayoutMap()` nach `e.code`; nicht-ASCII-Zeichen → US-Taste aus `KeyX`/`DigitN`; mit Shift werden US-Shift-Glyphen (`! @ # … ? < > "`) auf ihre Basistaste zurückgeführt (z. B. `⇧'` → `'`). Dadurch funktionieren `⇧E`, `⌘⇧'`, `⌘⇧,` layoutunabhängig.

Kollisionen sind durch Sichtbarkeitsbedingungen entschärft: `G S`/`O S` gehören in Projekten zu Projekt-, sonst zu Workspace-Einstellungen; `G R` analog (Projekt-/Workspace-Archive); `S` ist im Work-Item-Kontext „Change state“, im Modul-Kontext „Change status“; `⌘⇧,` kopiert je Kontext die URL.

#### 3.9.2 Modal-Zustandsmaschine (`ui/modal/wrapper.tsx`)

| Ereignis | Wirkung |
|---|---|
| Auswahl `action` | `action(ctx)`; bei `closeOnSelect` Palette schließen |
| Auswahl `change-page` | `activeCommand` setzen, `activePage = command.page`, Suchtext leeren |
| Auswahl auf Seite | `activeCommand.onSelect(data, ctx)`; bei `closeOnSelect` schließen, sonst bleibt die Seite offen (Mehrfachauswahl Assignees/Module/Labels/Modulmitglieder; Haken aktualisiert sich live) |
| Esc | Suchtext vorhanden → leeren; sonst schließen (Base-UI-Esc wird unterdrückt, damit die Zwei-Stufen-Logik greift) |
| Backspace bei leerem Suchtext | aktive Seite → zurück zur Hauptliste (`activePage=null`, `activeCommand=null`); sonst Kontextaktionen ausblenden |
| Ctrl/⌘ K im Modal | nur `preventDefault` (Umschalten erledigt der globale Handler) |
| Außenklick | schließt |
| Schließen | nach 200 ms (Animationsende) Reset: Suchtext, `activePage`, `activeCommand`, `shouldShowContextBasedActions = true`; erneutes Öffnen innerhalb 200 ms bricht den Reset ab |

Top-Nav-Variante (`apps/web/components/navigation/top-nav-power-k.tsx`): Öffnet nur bei echtem Klick (`mousedown`) oder Tastatur-Trigger (Ctrl/⌘ F) oder beim Tippen, nicht bei programmatischem Fokus (`apps/web/hooks/use-expandable-search.ts`); Ctrl/⌘ K im Feld schließt nur das Panel; Esc leert und schließt; Backspace wie oben; ↑/↓ werden als synthetische Events an `[cmdk-list]` weitergereicht (bei ↓ zusätzlich Fokus auf erstes aktives Item), Enter klickt das `aria-selected` Item; **jede** Aktionsauswahl schließt das Panel (unabhängig von `closeOnSelect`), Auswahl auf Seiten ebenfalls; Außenklick schließt und setzt Suchtext/Seite/Befehl zurück.

#### 3.9.3 Edge-Cases

| Fall | Verhalten im Original | Quelle |
|---|---|---|
| Befehle im Shortcut-Modal | listet alle registrierten Befehle mit Taste, auch solche, die im aktuellen Kontext nicht sichtbar sind | `ui/modal/shortcuts-root.tsx` (`getAllCommandsWithShortcuts`) |
| Theme-Wechsel per Power-K | erzwingt `window.location.reload()` nach erfolgreichem PATCH (Profil-Einstellungen machen das nicht) | `config/preferences-commands.ts` |
| Sprache per Power-K | nur `updateUserProfile({language})`; der Profil-Store ruft bei gesetztem `language` `setLanguage()` aus `@plane/i18n` auf (sofortige Umschaltung ohne Reload, A13b §3.1) | `config/preferences-commands.ts`, `apps/web/store/user/profile.store.ts` |
| Modul-Mitglieder | `handleUpdateMember` mutiert das Array `member_ids` des Store-Objekts direkt (`splice/push`) vor dem PATCH | `ui/pages/context-based/module/commands.tsx` |
| Cycle-/Modul-Favorit | Rechteprüfung ohne Workspace-/Projekt-Argumente (`allowPermissions([...], PROJECT)` nutzt Router-Kontext) | `cycle/commands.ts`, `module/commands.tsx` |
| Fehler beim Cycle-Zuordnen | `try/catch` um nicht abgewartete Promises → Fehler-Toast erscheint nie | `work-item/commands.ts` |
| Suche ohne Projekt | `workspace_search=true` erzwungen; Footer-Schalter disabled | `ui/modal/search-menu.tsx`, `commands-list.tsx` |
| Page-Treffer ohne Projekt | Link auf `/${ws}/wiki/${id}` (nur EE) | `search-results-map.tsx` |
| Registrierung | jede Änderung der Befehlsliste (neue Hook-Ausgabe) leert und befüllt die Registry neu | `global-shortcuts.tsx` |

### 3.10 Gesammelte Edge-Cases und Abweichungen im Original

Empfehlung: „Korrigieren“ = offensichtlicher Fehler, im Neubau beheben und als bewusste Abweichung dokumentieren; „1:1“ = sichtbares Verhalten beibehalten (ADR-005); „Entfällt“ = durch ADR-001/ADR-004 gegenstandslos.

| # | Fall | Verhalten im Original | Quelle | Empfehlung |
|---|---|---|---|---|
| E1 | Sidebar-Peek | Kein Aufrufer von `toggleSidebarPeek(true)` – Peek-Modus der eingeklappten Sidebar ist in der CE unerreichbar | `apps/web/store/theme.store.ts`, `apps/web/components/sidebar/sidebar-toggle-button.tsx` | 1:1 (nicht bauen) |
| E2 | Extended-Sidebar-Flag | `toggleExtendedSidebar(collapsed?)` setzt `isExtendedSidebarOpened = collapsed`; Link-Klick in der „More“-Sidebar ruft `toggleExtendedSidebar(true)` → Sidebar bleibt **offen**; Key `extended_sidebar_collapsed` speichert den Offen-Zustand | `apps/web/store/theme.store.ts`, `apps/web/components/workspace/sidebar/extended-sidebar-item.tsx` | 1:1 Verhalten, sauber benennen |
| E3 | Projektliste-Zustand | `localStorage.isAllProjectsListOpen` wird geschrieben, nie gelesen | `apps/web/components/workspace/sidebar/projects-list.tsx` | weglassen |
| E4 | Favoriten-Kopf als Drop-Ziel | Drop auf den Kopf „Favorites“ führt nur `console.log` aus | `apps/web/components/workspace/sidebar/favorites/favorites-menu.tsx` | 1:1 (No-op) |
| E5 | Favoriten-Ordner anlegen | Duplikatprüfung gegen die Namen **aller** Favoriten (auch Projekte/Views) | `apps/web/components/workspace/sidebar/favorites/new-fav-folder.tsx` (3.4) | Korrigieren (nur Ordner) |
| E6 | Inbox Custom-Snooze | 12 AM bleibt Stunde 12, 12 PM wird 00 (vertauscht) | `apps/web/components/workspace-notifications/sidebar/notification-card/options/snooze/modal.tsx` | Korrigieren |
| E7 | Un-Snooze | `PATCH {snoozed_till: undefined}` → Feld fehlt im JSON | `apps/web/store/notifications/notification.ts` | Backend-Vertrag klären (A03), explizit `null` senden |
| E8 | Inbox-Zähler beim Workspace-Wechsel | SWR-Key `WORKSPACE_UNREAD_NOTIFICATION_COUNT` ohne Slug – kein automatischer Neuabruf allein durch den Slug-Wechsel | `apps/web/components/navigation/top-navigation-root.tsx` | Korrigieren (Key mit Slug) |
| E9 | Quick link löschen | ohne Bestätigungsdialog, Toast-Titel = Nachricht | `apps/web/components/home/widgets/links/link-detail.tsx`, `use-links.tsx` | 1:1 |
| E10 | Home-Widget-Schalter | Fehler nur in der Konsole, kein Toast | `apps/web/store/workspace/home.ts` | Korrigieren (Fehler-Toast) |
| E11 | Begrüßung | Tageszeit („morning/afternoon/evening“) nach **Browser**-Zeitzone, angezeigte Uhrzeit nach `user_timezone` | `apps/web/components/home/user-greetings.tsx` | Korrigieren (einheitlich `user_timezone`) |
| E12 | Quickstart-Link | relativer Link `settings` funktioniert nur wegen Trailing-Slash der Home-URL | `apps/web/components/home/widgets/empty-states/no-projects.tsx` | absoluten Link verwenden |
| E13 | Auth-Seitentitel | Sign-in-Seite heißt „Sign up - Plane“, Sign-up-Seite „Sign in - Plane“ | `apps/web/components/auth-screens/header.tsx` | Korrigieren |
| E14 | Link „Sign in“ auf Sign-up | Ziel `/sign-in` (Redirect auf `/`) statt direkt `/` | `apps/web/components/auth-screens/header.tsx` | direkt `/` |
| E15 | `/accounts/set-password` | nutzt `ResetPasswordForm` ohne `uidb64`/`token` → POST auf `/auth/reset-password/null/null/` | `apps/web/app/(all)/accounts/set-password/page.tsx`, `apps/web/components/account/auth-forms/reset-password.tsx` | Korrigieren (Set-Password-Endpunkt) |
| E16 | Project-ID-Tooltip | Text „Max 50 characters.“, Validierung erlaubt max. 10 | `apps/web/components/project/create/common-attributes.tsx`, `apps/web/components/project/form.tsx`, `packages/i18n/src/locales/en/*.json` (`project_id_tooltip_content`) | Text korrigieren |
| E17 | Projektfilter „Access“ | Suche vergleicht mit dem i18n-**Schlüssel** (`i18n_label.includes(query)`), nicht mit dem Text | `apps/web/components/project/dropdowns/filters/access.tsx` | Korrigieren |
| E18 | Projektsortierung absteigend nach Datum | `-created_at` sortiert nach `!created_at` → Server-Reihenfolge; unbekannter Schlüssel → leere Liste | `packages/utils/src/project.ts` (`orderProjects`) | Korrigieren |
| E19 | Projekt verlassen (Dialog) | Navigation auf `/{ws}/projects` **vor** dem Request; Fehler danach nur als Toast | `apps/web/components/project/leave-project-modal.tsx` | Reihenfolge korrigieren |
| E20 | Projekt-Switcher (TABBED) | verwendet den Default-Tab des **aktuellen** Projekts für das Zielprojekt | `apps/web/components/navigation/project-header.tsx` | Korrigieren (Ziel-Präferenz) |
| E21 | Tab ausblenden/einblenden | Fehler-Toasts unerreichbar (fehlendes `await`) | `apps/web/components/navigation/use-tab-preferences.ts` | Korrigieren |
| E22 | Power-K Cycle-Zuordnung | Fehler-Toast unerreichbar (Promise nicht abgewartet) | `apps/web/components/power-k/ui/pages/context-based/work-item/commands.ts` | Korrigieren |
| E23 | Shortcut-Übersicht | listet alle Befehle, auch im Kontext unsichtbare | `apps/web/components/power-k/ui/modal/shortcuts-root.tsx` | 1:1 |
| E24 | Theme per Power-K/Profil | `window.location.reload()` nach Theme-Wechsel | `apps/web/components/power-k/config/preferences-commands.ts`, `apps/web/components/appearance/theme-switcher.tsx` | Neubau ohne Reload möglich (Theme-Service), Toast-Text anpassen |
| E25 | Links auf nicht vorhandene Routen | Power-K-Seiten-Treffer ohne Projekt → `/{ws}/wiki/{id}`; Recents-Seite ohne Projekt → `/{ws}/pages/{id}` (beide Routen existieren in der CE nicht) | `apps/web/components/power-k/ui/modal/search-results-map.tsx`, `apps/web/components/home/widgets/recents/page.tsx` | Workspace-Seiten erst mit Wiki-Feature (ADR-001) verlinken |
| E26 | Inbox-Erweiterungen | `ADDITIONAL_NOTIFICATION_CONTENT_MAP` leer | `apps/web/components/workspace-notifications/notification-card/content.ts`, `.../sidebar/notification-card/content.tsx` | Erweiterungspunkt vorsehen |
| E27 | Profil „Work items by state“ | Leerzustand zeigt den Prioritäts-Text „No work item assigned yet“ (`your_work_by_priority`) | `apps/web/components/profile/overview/state-distribution.tsx` | 1:1 oder eigener Text |
| E28 | `DateFilterModal` | `isInvalid` vergleicht Datum 1 mit sich selbst (`const date2 = getDate(watch("date1"))`) – „Apply“ nie gesperrt (Kalender verhindern ungültige Bereiche ohnehin) | `apps/web/components/core/filters/date-filter-modal.tsx` | Korrigieren |
| E29 | Workspace-View-Zeile | „Edit View“/„Delete View“ ohne Rechteprüfung (im Header dagegen Owner/Admin) | `apps/web/components/workspace/views/view-list-item.tsx` | Korrigieren (Rechte wie `useViewMenuItems`) |
| E30 | „Add existing work item“ | Beschriftung „Select all/Deselect all“ vergleicht mit allen Treffern, die Aktion mit den gefilterten (`shouldHideIssue`); Überschrift „… in project:“ auch bei Workspace-Suche | `apps/web/components/core/modals/existing-issues-list-modal.tsx` | Korrigieren |
| E31 | Hart codierte englische Texte (ohne i18n) | Bulk-Delete-Dialog (Buttons, Toasts, Überschrift), `ImagePickerPopover` (Tabs, Suche, Upload-Texte), `UserImageUploadModal`/`WorkspaceImageUploadModal`, `GptAssistantPopover`, `DateFilterModal`-Buttons, „Search results for … in project:“, Workspace-View-Zeile („Edit View“/„Delete View“) und View-Toasts, Power-K-Placeholder „Search commands...“, Kopf „Workspace settings“, Workload-Labels „Not started“/„Working on“, Profil-Aktivität („You“, „Plane“, „Bot“, „Commented“), Aktivitätssätze in `core/activity.tsx`, Instanz-Screens, What's-new-Fallback | 2.2, 2.8, 2.10.1, 2.16, 2.17 | i18n-Schlüssel ergänzen |
| E32 | Profil-Einstellungen Zeitzone | Fallback-Anzeige `Asia/Kolkata`, wenn keine Zeitzone gesetzt | `apps/web/components/settings/profile/content/pages/preferences/language-and-timezone-list.tsx`, `.../pages/general/form.tsx` | Fallback `UTC` (Instanz-Default) |
| E33 | Externe Ziele | GitHub-Stern-Link, Docs/Forum/Changelog/Support-Links, `mailto:sales@plane.so`/`support@plane.so`, Marketing-Logos im Auth-Fuß, AGB/Datenschutz-Links, Unsplash, „Learn more about projects“ (`https://plane.so/`) | 2.2, 2.11.1, 2.14.1, 2.16.5, 2.16.8, 2.16.9 | Entfällt bzw. konfigurierbar (ADR-001/ADR-004) |
| E34 | Upsell-Elemente | „Community“-Badge, „Pro“-Badges, Billing-Seite, „Contact sales“ | 2.18 | Entfällt (ADR-001) |
| E35 | Totes UI | Komponenten aus 2.21 sind nicht erreichbar | 2.21 | nicht portieren |

---

## 4. Abhängigkeiten

### 4.1 Stores und Hooks (Details: A08 §2.5 Store-Baum, §2.8 Hooks)

| Hook / Store (`apps/web/hooks/…`, `apps/web/store/…`) | Importe im Bereich | Verwendung in diesem Bereich |
|---|---|---|
| `store/user` (`useUser`, `useUserProfile`, `useUserSettings`, `useUserPermissions`) | 94 | Sitzung, Profil (Theme, Sprache, Onboarding-Schritte, Tour), Rollenprüfungen `allowPermissions`, `leaveProject`/`joinProject`, Sign-out |
| `store/use-project` (`project.store.ts`) | 34 | Projektliste, `filteredProjectIds`, `joinedProjectIds`, Favoriten, Archiv, Anlage, Sidebar-Reihenfolge |
| `store/use-member` | 27 | Workspace-/Projektmitglieder, Einladungen, Avatare in Listen und Filtern |
| `store/use-workspace` | 26 | aktueller Workspace, Workspace-Liste, Sidebar-/Navigations-Präferenzen, `getWorkspaceRedirectionUrl` |
| `use-app-router`, `use-platform-os`, `use-local-storage`, `use-debounce`, `use-current-time`, `use-timer`, `use-window-size`, `use-intersection-observer`, `use-expandable-search` | 24 / 19 / 4 / 3 / 3 / 2 / 1 / 1 / 1 | Navigation, Mobile-Erkennung, lokale Präferenzen (2.19), Suchen, Uhr in Begrüßung/Profil, Resend-Timer |
| `store/use-app-theme` (`theme.store.ts`) | 17 | Sidebar-Collapse/-Peek, Extended-Sidebars, Profil-Sidebar (3.2) |
| `store/use-command-palette` (`base-command-palette.store.ts`) | 16 | Flags der Modal-Hosts (2.16.7), Profil-Einstellungs-Modal, Shortcut-Modal |
| `store/use-instance` | 13 | `config` (Signup, SMTP, OAuth-Provider, Unsplash, LLM, Changelog-URL, `is_self_managed`, Workspace-Anlage gesperrt) |
| `use-navigation-preferences` | 10 | Sidebar-Präferenzen, Navigationsmodus, Projektlimit, App-Rail (2.3, 3.3) |
| `store/use-power-k` (`base-power-k.store.ts`) | 10 | Power-K-Zustand (2.9, 3.9) |
| `store/notifications` (+ `use-notification`, `use-notification-preview`) | 13 | Inbox (2.7, 3.7) |
| `use-stickies` (`store/sticky/sticky.store.ts`) | 9 | Stickies (2.6) |
| `store/use-home` (`store/workspace/home.ts`, `link.store.ts`) | 8 | Home-Widgets, Quick links, Recents (2.5) |
| `store/use-issue-detail`, `use-issues`, `use-issue-layout-store`, `use-issues-actions`, `use-workspace-issue-properties`, `work-item-filters` | 9 / 3 / 1 / 1 / 1 / 1 | Peek aus Inbox/Recents/Profil, Profil-Issue-Listen, Power-K-Kontextbefehle (A09) |
| `store/use-project-filter` | 5 | Projektliste (3.5) |
| `store/use-global-view` | 5 | Workspace-Views (2.17) |
| `store/use-module`, `use-cycle`, `use-label`, `use-project-state`, `estimates`, `use-project-view`, `use-project-publish`, `use-project-inbox` | 5 / 4 / 2 / 2 / 2 / 1 / 1 / 1 | Power-K-Kontextbefehle und Menüs, Publish-Dialog, Intake-Header (A10b) |
| `store/use-favorite`, `use-favorite-item-details` | 3 / 1 | Favoriten-Sektion (2.3.7) |
| `use-multiple-select` | 4 | Mehrfachauswahl (2.16.4) |
| `use-workspace-invitation`, `use-timezone`, `use-workspace-paths`, `oauth` | 2 / 2 / 1 / 1 | Einladungen, Zeitzonen, Top-Nav-Aktivzustand, OAuth-Buttons |

### 4.2 Services und Backend

| Service (`apps/web/services/…`, `packages/services/…`) | Endpunkte | Backend-Analyse |
|---|---|---|
| `auth.service.ts`, `user.service.ts` | 2.20 Zeilen „Auth“, „Benutzer“, „Profil-Seiten“ | A06 (Auth), A03 (User) |
| `workspace.service.ts` | Workspace, Einladungen, Mitglieder, Views, Quick links, Recents, Home-Präferenzen, Sidebar-Präferenzen, User-Properties, Suche | A03 |
| `project/*.service.ts` | Projekte, Mitglieder, Archiv, Publish, User-Properties, Favoriten-Projekte, Identifier-Prüfung, Issue-Suche | A03, A05 (Space/Publish) |
| `favorite/favorite.service.ts` | Favoriten | A03 |
| `sticky.service.ts` | Stickies | A03 |
| `workspace-notification.service.ts` | Inbox | A03, A07 (Benachrichtigungs-Jobs) |
| `file.service.ts` | Asset-Uploads (Signed URL), Unsplash | A07 (Storage) |
| `ai.service.ts`, `timezone.service.ts`, `issue/issue.service.ts` (Bulk-Delete) | KI-Assistent, Zeitzonen, Bulk-Delete | A03, A04 |
| `packages/services/src/developer/api-token.service.ts` | API-Tokens | A03 |

Vollständige Service-/Endpunkt-Tabelle: A08 §2.7; Datenmodelle (Workspace, Project, ProjectMember, UserFavorite, Sticky, Notification, WorkspaceUserPreference, WorkspaceHomePreference, WorkspaceUserLink, UserRecentVisit, ProjectUserProperty, WorkspaceUserProperties, Profile): A02a.

### 4.3 Andere UI-Bereiche

| Bereich | Kopplung | Analyse |
|---|---|---|
| Work-Item-Layouts, Peek, Detail, Create-Modal, Filter-HOCs, Display-Filter, Dropdowns | Profil-Issue-Tabs (2.8.4), Inbox-Detail (2.7.4), Recents-Peek, Power-K-Kontext Work Item, `WorkItemLevelModals`, `ExistingIssuesListModal`/`BulkDeleteIssuesModal` als Zulieferer | A09 |
| Cycles, Modules, Views, Pages, Intake, Analytics, Estimates, Labels, States, Automations, Webhooks, Exporter, API-Tokens (A10b §2.1–§2.15) | Seiten hinter Sidebar-/Tab-Navigation und Settings-Kategorien; `ProjectLevelModals`; Fortschritts-Statistiken; `ListItem`; Workspace-Views-Formular | A10b |
| Space-App (öffentliche Boards) | Ziel des Publish-Dialogs (`SPACE_BASE_URL/SPACE_BASE_PATH`) | A11 |
| Admin-App („God mode“) | `GOD_MODE_URL` in `InstanceNotReady` und (unsichtbar) im User-Menü | A11 |
| Editor | Sticky-Editor, Profil-Aktivität (Kommentare), Beschreibungs-Versionen, KI-Assistent, Inbox-Intake-Embed | A12 |
| Designsystem | Propel-/Blocks-Komponenten, Tokens, Themes, Custom-Theme-Algorithmus, Illustrationen (`assetKey`) | A13a (§2.17–2.18, §2.22–2.31, §3.3) |
| i18n, Konstanten, Utils | `packages/i18n` (Texte, Sprachen, `setLanguage`), `packages/constants` (Navigation, Settings, Profil-Tabs, Filter, Themes, Datei-Limits), `packages/utils` (Sortierung, Filter, Validierung, Datum) | A13b |
| Routing/Guards | Seiten dieses Bereichs hängen an den Routen und Wrappern aus A08 §2.2–2.3; Redirect-Regeln, Trailing-Slash | A08 |
| Bezahlfunktionen | Upsell-Stellen, Plan-Matrix, Erweiterungspunkte | `migration/features/20-paid-spuren-im-repo.md` §2, §5 |

---

## 5. Migrationshinweise für Angular

### 5.1 1:1 übertragbar (Daten, Texte, Regeln)

| Inhalt | Quelle | Hinweis |
|---|---|---|
| Navigations-Items, Rollen, Highlight-Regeln, Server-Defaults der Sidebar-Präferenzen | `packages/constants/src/workspace.ts`, 2.3.2 | als Konstanten-Modul übernehmen |
| Settings-Kategorien, Tabs, Icons, Rechte (Workspace, Projekt, Profil) | `packages/constants/src/settings/*.ts`, 2.10.1, 2.11.1, 2.13 | Route-Guards in Angular aus derselben Tabelle ableiten |
| Profil-Tabs, Default-Workspace-Views, Projekt-Sortieroptionen, Datumsfilter-Optionen, `ORGANIZATION_SIZE`, `USE_CASES`, Rollen-Kacheln, `THEME_OPTIONS`, `START_OF_THE_WEEK_OPTIONS`, `STICKY_COLORS_LIST`, `STATIC_COVER_IMAGES`, Datei-Limits | `packages/constants/src/*`, `apps/web/helpers/cover-image.helper.ts` | Werte unverändert; Bilder/Assets mitliefern (Airgap) |
| Power-K-Befehlsliste (IDs, Gruppen, Prioritäten, Tasten, Sichtbarkeitsregeln) | 2.9.2 | als deklarative Registry nachbauen; Shortcut-Algorithmus 3.9.1 exakt übernehmen |
| Sortier-Algorithmen (±10000 an den Rändern, Mittelwert zwischen Nachbarn; Favoriten/Widgets/Stickies absteigend mit Basis 10000) | 3.3, 3.4, 3.6 | identisch, damit bestehende `sort_order`-Werte kompatibel bleiben |
| Filter-/Sortierlogik der Projektliste, `satisfiesDateFilter` | 3.5, `packages/utils/src/project.ts`, `filter.ts` | 1:1 mit Korrekturen E17/E18 |
| Aktivitätssätze, Inbox-Texte, Toasts, Leerzustände | 2.7.3, 2.16.4a, alle 2.x | i18n-Schlüssel aus `packages/i18n` übernehmen; hart codierte Texte (E31) als neue Schlüssel |
| Klassenstrings/Maße der Screens | alle Tabellen in 2.x | ADR-005: Tailwind-Klassen wörtlich (A13a §5.1) |
| Onboarding-Schrittmaschine und Wiederaufnahme | 2.15.2, 3.8.5 | als Angular-Stepper mit identischen Bedingungen |

### 5.2 Neu zu bauen (Angular)

| Baustein | Original | Angular-Ansatz |
|---|---|---|
| App-Shell mit Top-Navigation, resizable Sidebar, Extended-Sidebars, Mobile-Verhalten | `ResizableSidebar`, `theme.store.ts`, Außenklick-Hooks | Shell-Komponente + `LayoutStateService` (Signals) mit LocalStorage-Persistenz (2.19); Resize per Pointer-Events (236–350 px), Außenklick-Direktive mit Ausnahmen (`#extended-sidebar-toggle`, offene Dropdowns) |
| Drag&Drop (Sidebar-Projekte, Favoriten inkl. Ordner, Extended-Items, Home-Widgets, Stickies) | `@atlaskit/pragmatic-drag-and-drop` mit Tree-Item-Hitbox | Angular CDK Drag&Drop reicht für Listen; Favoriten-Baum (Ordner, „make child“, „reorder above/below“) braucht eigene Hitbox-Logik oder Portierung von `pragmatic-drag-and-drop` (framework-agnostisch nutzbar) |
| Command Palette (Power-K) | `cmdk` + Registry + `ShortcutHandler` | eigene Komponente (Listbox mit Filter/Gruppen) oder framework-neutrale Bibliothek; Shortcut-Service global (`HostListener` auf `document`), Sequenzen mit 1000 ms Timeout, Eingabefeld-Ausschlüsse |
| Masonry-Layout Stickies | `react-masonry-component` | CSS-Columns oder `masonry-layout` (framework-neutral), Spalten 2–6 nach Breite (2.6) |
| Charts Profil/Fortschritt | `@plane/blocks/charts/*` (Recharts) | Chart-Bibliothek mit gleicher Optik (A13a), Farben aus 2.8.3/2.16.4 |
| Formulare | `react-hook-form` | Reactive Forms mit denselben Validatoren (`validatePersonName`, `validateWorkspaceName`, `validateSlug`, Identifier-Regex) |
| Auth-Formulare | echte HTML-Formular-POSTs mit CSRF und Server-Redirect | beibehalten (Server-Redirect-Flow), .NET liefert gleichwertige Endpunkte (A06) |
| Modal-Hosts | `modals/*` + Command-Palette-Store | zentraler `DialogService` mit denselben Flags |
| Data-Table, Combobox, Select, Menu, Tabs, Tooltip, Dialog | `@makeplane/propel` | Angular-Komponentenbibliothek mit identischem DOM/CSS (A13a §5.3) |
| Lazy Profil-Einstellungs-Modal und -Seite mit gemeinsamer Tab-Map | `PROFILE_SETTINGS_PAGES_MAP` | eine Tab-Registry, zwei Container (Route und Dialog) |
| `iframe`-Changelog | `ProductUpdatesChangelog` | nur wenn `instance_changelog_url` gesetzt; sonst Fallback ohne externe Links (ADR-004) |

### 5.3 Entfällt bzw. wird ersetzt (ADR-001, ADR-004)

| Element | Abschnitt | Ersatz |
|---|---|---|
| `WorkspaceEditionBadge`, `PaidPlanUpgradeModal`, Plan-Karten, Billing-Seite und -Menüeintrag, `UpgradeBadge`, `ProIcon`, „Contact sales“, Upsell-Seite „Active cycles“ | 2.18, 2.2 | keiner (Funktionen ohne Plan-Grenze oder nicht anbieten) |
| GitHub-Stern-Link, Marketing-Logos, Links auf plane.so/go.plane.so/forum, `mailto:` an Plane, Unsplash, Changelog-Fallback-Links | 2.2, 2.11.1, 2.14.1, 2.16.5, 2.16.8, 2.16.9 | konfigurierbare Instanz-Links (Admin-Einstellung) oder ausblenden |
| Marketing-Opt-in im Onboarding (nur Cloud) | 2.15.2 | Self-managed-Pfad ist maßgeblich (`is_self_managed`) |
| Toter Code | 2.21 | nicht portieren |

### 5.4 Fallstricke

| Fallstrick | Detail | Abschnitt |
|---|---|---|
| Zwei Darstellungsformen der Profil-Einstellungen | Modal (aus dem User-Menü) und Seite (`/settings/profile/:tab`) teilen Inhalte; nur die Seite zeigt die Workspace-Kategorie | 2.13.1 |
| Navigationsmodus ACCORDION vs. TABBED | beeinflusst Sidebar-Klickverhalten **und** fügt auf allen Projektseiten eine Tab-Zeile ein; Präferenz serverseitig in Workspace-User-Properties | 2.4.2, 3.3 |
| Präferenzen an drei Orten | Server (Sidebar-, Home-, Tab-, Navigations-Präferenzen, Theme, Sprache, Zeitzone), LocalStorage (2.19), nur im Speicher (Projektfilter) – Verhalten beim Gerätewechsel muss identisch bleiben | 2.19, 3.5 |
| Theme-Wechsel mit Reload | Original lädt neu; ein Neubau ohne Reload ändert sichtbares Verhalten (Toast „Reloading to apply changes...“) | 2.13.3, E24 |
| Trailing-Slash-abhängige relative Links | Quickstart-Link `settings`, Settings-Links mit abschließendem `/` | E12, A08 §2.1 |
| Optimistische Updates mit Revert | Favoriten, Reihenfolgen, Stickies, Inbox – Fehlerpfade müssen den Zustand exakt zurücksetzen | 3.4, 3.6, 3.7 |
| Rollenwerte | Rechteprüfungen vergleichen Workspace- **und** Projektrolle; Nicht-Admins sehen Workspace- und Projekt-„General“ deaktiviert (`opacity-60`) statt ausgeblendet | 3.8.1 |
| SWR-Cache-Schlüssel | einige Schlüssel ohne Workspace-Slug (E8) – im Neubau Cache je Workspace trennen | 3.1 |
| Lokalisierung | viele Texte hart codiert (E31); Aktivitätssätze werden aus Fragmenten zusammengesetzt (Satzbau englisch) | 2.16.4a |
| Sticky-/Inbox-Pagination | Cursor-Format `per_page:page:offset` (`300:0:0`, `100:{i}:0`, `STICKIES_PER_PAGE:0:0`) | 2.6, 2.7, 2.8.5 |
| Zeitzonen | Begrüßung nach Browser-, Uhrzeiten nach Nutzer-Zeitzone; Fallback `Asia/Kolkata` | E11, E32 |

### 5.5 Teststrategie (Hinweise)

| Ebene | Inhalt |
|---|---|
| Unit | Sortier-Algorithmen (3.3, 3.4, 3.6), Projektfilter/-sortierung (3.5), `satisfiesDateFilter`, Shortcut-Auflösung inkl. Sequenzen und Layout-Map (3.9.1), Onboarding-Schrittwahl (3.8.5), Custom-Snooze-Zeitberechnung (korrigiert, E6) |
| Komponente | Sidebar (Collapse, Resize, Extended, Mobile), Favoriten-DnD, Power-K (Seiten, Kontext, Suche), Inbox-Filter/Tabs, Profil-Einstellungen (Modal und Seite), Auth-Schritte inkl. Fehler-Codes |
| Visuelle Regression | alle Screens aus 1.5 in Light/Dark und High-Contrast gegen das Original (ADR-005, A13a §5.7) |
| E2E | Onboarding (Self-managed), Workspace anlegen/wechseln/löschen, Projekt anlegen → Features → Archivieren → Wiederherstellen → Löschen, Mitglied einladen/Rolle ändern/entfernen, Inbox lesen/archivieren/snoozen |

## 6. Offene Punkte

| # | Frage | Kontext |
|---|---|---|
| O1 | Soll der unerreichbare Peek-Modus der eingeklappten Sidebar (E1) gebaut werden oder entfällt er? | 3.2 |
| O2 | Welche Original-Fehler (3.10, Empfehlung „Korrigieren“) werden korrigiert, welche bewusst 1:1 nachgebaut? Entscheidung nötig je Eintrag (insbesondere E6, E13, E15, E18, E19, E20) | 3.10 |
| O3 | Wie wird „Un-Snooze“ im .NET-Backend signalisiert (`snoozed_till: null` vs. fehlendes Feld)? | E7, A03 |
| O4 | Ersatz für die externen Links (Docs, Forum, Changelog, Support, AGB/Datenschutz, „Learn more about projects“): konfigurierbare Instanz-URLs oder ersatzlos? | E33, ADR-004 |
| O5 | „What's new?“: ohne `instance_changelog_url` zeigt das Original Links auf plane.so – eigener Changelog-Inhalt oder Menüpunkt entfernen? | 2.16.9 |
| O6 | Unsplash-Tab des Image-Pickers: in Airgap-Installationen abschalten (Konfiguration `has_unsplash_configured`) oder entfernen? | 2.16.5 |
| O7 | KI-Assistent (`ai-assistant`, Hinweis „3rd party service“): soll eine lokale LLM-Anbindung vorgesehen werden? | 2.16.4 |
| O8 | Sidebar-Fuß ohne „Community“-Badge: leer lassen oder neutrale Versionsanzeige? | 2.18 |
| O9 | „Active cycles“ (Workspace-Ebene) ist in der CE nur Upsell; wird die Funktion gebaut (dann ohne Badge) oder der Sidebar-Key `active_cycles` ausgeblendet? | 2.3.2, 2.18, features/20 PF-04 |
| O10 | Theme-Wechsel: Reload beibehalten (1:1) oder Live-Umschaltung? | E24 |
| O11 | Sollen Projektfilter künftig persistiert werden (heute nur im Speicher, Reset bei Workspace-Wechsel)? | 3.5 |
| O12 | Hart codierte englische Texte (E31): Übersetzung im Zuge des Neubaus ergänzen? | E31, A13b |
| O13 | Routen-Ziele der Bezahl-Edition (Workspace-Pages/Wiki, Projekt-Overview, Epics-Tab) – Links bis zur Umsetzung ausblenden? | E25, 2.4.1 |
| O14 | Workspace-View-Zeile ohne Rechteprüfung (E29): Rechte wie im Header übernehmen? | 2.17 |
