# Katalog Teil 1: WS, PRJ, WI
C = []
def F(d, g, n, s, t, src):
    C.append({"d": d, "g": g, "n": n, "s": s, "t": t, "src": src.split()})

# ---------------- WS ----------------
G = "Workspace-Lebenszyklus"
F("WS", G, "Workspace anlegen", "",
  "Formular /create-workspace bzw. Onboarding-Schritt mit Name (max. 80 Zeichen, keine URL, mind. ein alphanumerisches Zeichen), Slug (Regex ^[a-zA-Z0-9_-]+$, max. 48 Zeichen, nicht in RESTRICTED_URLS/reservierten Slugs, global eindeutig; Verfügbarkeitsprüfung, 409 bei Konflikt) und Organisationsgröße. Legt Workspace und Admin-Mitgliedschaft (Rolle 20) an und startet den Demo-Seed. Ist DISABLE_WORKSPACE_CREATION gesetzt, erscheint ein Hinweis mit mailto-Anfrage.",
  "A03#0 A02a#0 A08#5 A10a#73 A13b#22 A06#39")
F("WS", G, "Demo-Inhalte bei Workspace-Anlage (Seed)", "nur Backend",
  "Asynchroner Seed nach der Anlage: Bot-User 'Plane', Demo-Projekt (Name = Workspace-Name) mit States, Labels, Cycles, Modules, 7 Tutorial-Work-Items, einer View und 2 Pages aus seeds/data/*.json.",
  "A02a#4 A07#26")
F("WS", G, "Workspace-Einstellungen General", "",
  "Settings → General mit Logo (Upload/Entfernen), Name, Company size, URL (kopierbar) und Timezone; 'Update workspace' nur für Admins (PATCH von Name, Slug, Logo, Zeitzone, Organisationsgröße).",
  "A10a#43 A03#1 A08#32")
F("WS", G, "Workspace löschen", "",
  "Löschbereich mit Bestätigungsdialog (Workspace-Name und 'delete my workspace' eintippen), nur für Admins. Soft-Delete mit asynchroner Kaskade, Slug wird zu slug__<epoch>, Profile.last_workspace_id wird geleert; endgültige Löschung nach 60 Tagen durch den täglichen hard_delete-Job.",
  "A10a#44 A03#1 A02a#1")
F("WS", G, "Workspace-Switcher und Workspace-Liste", "",
  "Dropdown mit E-Mail des Nutzers, alphabetischer Workspace-Liste (aktiver zuerst) mit Rolle und Mitgliederzahl (GET /api/users/me/workspaces/, Suche nach Name), Buttons Settings/Invite members sowie Links Create workspace, Workspace invites und Sign out; ein Wechsel speichert last_workspace_id.",
  "A10a#1 A03#2")
F("WS", G, "Workspace-weite Stammdatenlisten", "",
  "Workspace-weite Listen von Labels, States (mit berechnetem order), aktiven Estimates mit Punkten sowie Cycles und Modules mit Fortschrittszählern über alle Mitgliedsprojekte (Grundlage für Workspace-Views und Filter).",
  "A03#9")
F("WS", G, "Workspace-Themes (nur API)", "nur API",
  "CRUD benutzerdefinierter Farbthemen (WorkspaceTheme: name, colors) je Workspace für Admin/Member; vom CE-Frontend nicht genutzt.",
  "A02a#31 A03#17")

G = "Mitglieder & Rollen"
F("WS", G, "Rollen- und Berechtigungsmodell (Admin/Member/Guest)", "",
  "Workspace- und Projektrollen 20 (Admin), 15 (Member), 5 (Guest); Permission-Klassen je HTTP-Methode, allow_permission mit Ersteller-Ausnahme und Workspace-Admin-Override; Rollenbezeichnungen und -beschreibungen für die UI.",
  "A06#27 A02a#2 A13b#39")
F("WS", G, "Workspace-Mitgliederverwaltung", "",
  "Tabelle unter Settings → Members mit Suche, Rollenfilter (inkl. Suspended), Sortierung, Rollenwechsel (nur Admin, nicht die eigene Rolle; Herabstufung zum Gast stuft alle Projektrollen auf Gast herab), Entfernen und Workspace verlassen (is_active=false, alle Projektmitgliedschaften werden deaktiviert; Schutz für letzten Admin und alleinigen Projekt-Admin). E-Mail-Adressen nur für Nicht-Gäste sichtbar.",
  "A10a#45 A03#5 A02a#2 A08#32 A13b#39")
F("WS", G, "Mitglieder einladen und Einladungen verwalten", "",
  "Dialog 'Invite people to collaborate' mit mehreren Zeilen E-Mail + Rolle (höchstens die eigene Rolle), Fehler bei bestehenden Mitgliedern und ungültigen E-Mails; Liste 'Pending invites' mit Rollenwechsel, Copy link und Remove. Einladungsmail mit Link /workspace-invitations/?invitation_id&slug&token per Celery; WorkspaceMemberInvite mit JWT-Token, E-Mail in Kleinbuchstaben, eindeutig je E-Mail und Workspace unter aktiven Einladungen.",
  "A10a#46 A03#3 A02a#3 A07#29 A13b#39")
F("WS", G, "Einladungen annehmen oder ablehnen", "",
  "Seite /invitations zum gemeinsamen Annehmen mehrerer offener Einladungen (danach wird der Workspace der ersten Einladung last_workspace) und Seite /workspace-invitations?invitation_id&slug&token für den E-Mail-Link (annehmen/ignorieren, Zustände 'already member' und 'link not active'). Öffentliche Einladungsdetails ohne Token; Annahme nur durch den eingeloggten Empfänger gleicher E-Mail, nur einmal (responded_at); entfernte Mitglieder werden reaktiviert.",
  "A08#6 A08#7 A03#4 A02a#3 A13b#39")
F("WS", G, "Eigene Mitgliedschaft und Rollen-Maps", "intern (Frontend-Basis)",
  "GET workspace-members/me (Rolle, view_props, Draft-Zähler), POST workspace-views (view_props), Projektrollen-Map (project-roles) und Projekt-Mitglieder-Map je Projekt als Grundlage der clientseitigen Rechteprüfung.",
  "A03#6")

G = "Workspace-Navigation & Shell"
F("WS", G, "Workspace-Shell und Top-Navigation", "",
  "Leiste über allen Workspace-Seiten mit Workspace-Switcher, Power-K-Suchfeld, Inbox-Icon mit rotem Punkt (ungelesene Benachrichtigungen bzw. Mentions), Hilfe-Menü, GitHub-Link und Avatar-Menü.",
  "A10a#0 A08#8")
F("WS", G, "Hilfe-Menü", "",
  "Menü mit Documentation, Keyboard shortcuts, What's new?, Forum und Versionsnummer; der Eintrag 'Contact sales' entfällt nach ADR-001.",
  "A10a#2")
F("WS", G, "What's new? (Produkt-Changelog)", "",
  "Dialog mit der Seite aus INSTANCE_CHANGELOG_URL im iframe (15-s-Timeout, Fallback-Ansicht), Versionsanzeige und Links; für den Airgap-Betrieb konfigurierbar.",
  "A10a#81 A01#16")
F("WS", G, "User-Menü", "",
  "Avatar-Menü mit Cover-/Avatar-Kopfkarte, Settings und Preferences (öffnen das Profil-Einstellungs-Modal) sowie Sign out.",
  "A10a#3")
F("WS", G, "Star-us-on-GitHub-Link", "",
  "Link auf das GitHub-Repository mit themenabhängigem Logo in der Top-Navigation; im Airgap-Betrieb entfernbar bzw. konfigurierbar.",
  "A10a#5")
F("WS", G, "Resizable App-Sidebar mit Peek", "",
  "Projekt-App-Sidebar 236–350 px breit (Default 250, localStorage sidebarWidth), per Toggle einklappbar, Peek-Modus beim Hover im eingeklappten Zustand, Mobile-Verhalten unter 768 px; enthält Quick-Actions, Menüpunkte, Favoriten und Projektliste.",
  "A10a#7 A08#9")
F("WS", G, "Sidebar-Kopf und Quick-Action 'New work item'", "",
  "Titel Projects, Button Customize navigation, Sidebar-Toggle und Button New work item (deaktiviert ohne Projekt oder ohne Admin/Member-Rolle).",
  "A10a#8")
F("WS", G, "Sidebar-Menüeinträge", "",
  "Home sowie die persönlichen Einträge Stickies, Your work und Drafts und die Sektion Workspace (Projects, gepinnte Views/Analytics/Archives, More/Hide) mit Rollen- und Pin-Regeln; statische und dynamische Menüpunkte aus packages/constants.",
  "A10a#9 A13b#21")
F("WS", G, "Erweiterte Sidebar 'More' mit Pin und Sortierung", "",
  "Ausklapp-Panel (300 px) mit allen dynamischen Navigationseinträgen (views, active_cycles, analytics, drafts, your_work, archives, stickies) je nach Rolle, Pin/Unpin und Drag&Drop-Sortierung. Persistenz als WorkspaceUserPreference (is_pinned, sort_order, lazy geseedet) per Bulk-PATCH sidebar-preferences; der Einzel-PATCH {key} wird vom Frontend aufgerufen, fehlt aber im CE-Backend.",
  "A10a#10 A08#10 A03#16 A02a#24")
F("WS", G, "Customize navigation", "",
  "Dialog zum Ein-/Ausblenden und Sortieren der persönlichen und Workspace-Einträge, Wahl des Projekt-Navigationsmodus ACCORDION/TABBED und eines Projektlimits (navigation_control_preference, navigation_project_limit in WorkspaceUserProperties).",
  "A10a#11 A08#12 A02a#24 A03#8")
F("WS", G, "Favoriten mit Ordnern", "",
  "Sektion Favorites in der Sidebar für Projekte, Cycles, Modules, Views und Pages (Backend zusätzlich Issues) sowie Ordner: Ordner inline anlegen (Duplikatprüfung, Toasts), umbenennen, Einträge entfernen, Drag&Drop in/aus Ordnern und Sortierung (sequence). Backend mit Duplikaterkennung, Sichtbarkeitsprüfung der Entität und hartem Löschen mit Kaskade; nur Admin/Member.",
  "A10a#15 A10a#16 A08#43 A03#10 A02a#19 A13b#21")

G = "Workspace-Einstellungen"
F("WS", G, "Workspace-Settings-Rahmen", "",
  "Einstellungsbereich mit eigener Sidebar (Kategorien Administration und Developer), Rechteprüfung je Tab und Mobile-Navigation; Einträge General, Members, Exports, Webhooks (der Eintrag Billing entfällt nach ADR-001).",
  "A10a#42 A08#32 A13b#20")

# ---------------- PRJ ----------------
G = "Projektliste & Lebenszyklus"
F("PRJ", G, "Projektliste", "",
  "Seite /:ws/projects mit Projektkarten, Suche, Sortierung, Filtern (My projects, Access, Lead, Members, Created date) und Leiste angewandter Filter. Das Backend liefert schlanke und detaillierte Listen mit Rolle, Favorit, Sortierung, Mitglieder-IDs, Anchor und nächster Sequenz; Sichtbarkeit nach Workspace-Rolle und Netzwerk (Private/Public).",
  "A10a#52 A08#22 A03#18 A13b#14")
F("PRJ", G, "Projektkarte", "",
  "Karte mit Cover, Logo, Name, Identifier, Beschreibung, Mitgliedern, Copy link, Favorit, Settings/Join/Joined und Kontextmenü.",
  "A10a#53")
F("PRJ", G, "Projekt-Statistiken", "",
  "Zähler total_issues, completed_issues (inkl. cancelled), total_members, total_cycles und total_modules je sichtbarem Projekt für die Projektkarten.",
  "A03#28")
F("PRJ", G, "Projekt anlegen", "",
  "Zweistufiger Dialog: Cover, Logo, Name, automatisch erzeugte Project ID (max. 12 Zeichen, Großbuchstaben), Beschreibung, Network und Lead; danach Feature-Schalter und 'Open project'. Das Backend validiert Name und Identifier (eindeutig im Workspace, keine verbotenen Sonderzeichen, Fehlercodes wie PROJECT_NAME_ALREADY_EXIST), reserviert den Identifier (ProjectIdentifier), legt Admin-Mitgliedschaft, Lead, 6 Default-States und ProjectUserProperty (neues Projekt oben) an und löst ein Webhook-Event aus.",
  "A10a#55 A03#19 A02a#5 A02a#10 A06#39")
F("PRJ", G, "Projekt-Identifier prüfen und freigeben", "",
  "Verfügbarkeitsprüfung gegen reservierte Identifier (GET workspaces/<slug>/project-identifiers/) und Freigabe reservierter Identifier gelöschter Projekte (DELETE).",
  "A03#22 A02a#9")
F("PRJ", G, "Projekt-Detail und Zugriffsschutz", "",
  "Projekt-Detail-Endpunkt mit 403/409 für Nicht-Mitglieder und Recent-Visit-Erfassung. Der Projekt-Wrapper zeigt ohne Projektrolle 'Join project' (bei 409 oder bei 403 als Workspace-Admin), sonst 'restricted' bzw. 'Project not found'.",
  "A08#23 A10a#70 A03#18")
F("PRJ", G, "Projekt beitreten und verlassen", "",
  "Join-Dialog für öffentliche Projekte (geheime nur für Workspace-Admins; die Workspace-Rolle wird zur Projektrolle), Annahme von Projekt-Einladungen per Token, Leave-Dialog mit Texteingabe sowie Verlassen über die Mitgliederliste (Schutz für den einzigen Admin).",
  "A10a#56 A03#23 A03#24")
F("PRJ", G, "Projekt archivieren und wiederherstellen", "",
  "Archivieren über die Projekt-Settings bzw. die Karte setzt archived_at und löscht alle Favoriten des Projekts; archivierte Projekte sind nicht änderbar. Seite /:ws/projects/archives listet archivierte Projekte mit Restore und Löschen.",
  "A10a#54 A10a#48 A03#21 A02a#8 A08#22")
F("PRJ", G, "Projekt löschen", "",
  "Löschdialog in den Projekt-Settings bzw. im Projektarchiv; Soft-Delete mit Webhook sowie Bereinigung von Deploy-Board und Favoriten.",
  "A10a#48 A03#21")
F("PRJ", G, "Projekt-Einladungen per E-Mail (defekt, nur API)", "defekt im Original, nur API",
  "Endpunkte für Liste, Anlage und Löschung von ProjectMemberInvite existieren; die Anlage liefert immer 500, Liste und Löschen erfolgen ohne Rechteprüfung; kein CE-Frontend.",
  "A03#25")

G = "Projekt-Navigation"
F("PRJ", G, "Projektliste in der Sidebar", "",
  "Beigetretene Projekte mit Logo, Aufklappen der Projekt-Features (Accordion) bzw. Direktnavigation (Tabbed), Projektlimit mit More/Hide, Drag&Drop-Sortierung (sort_order in ProjectUserProperty, Berechnung in packages/utils) und Add project.",
  "A10a#12 A02a#10 A13b#14")
F("PRJ", G, "Projekt-Kontextmenü in der Sidebar", "",
  "Menü je Projekt mit Publish, Copy link, Archives, Settings und Leave project (nur Gast).",
  "A10a#13")
F("PRJ", G, "Erweiterte Projekt-Sidebar", "",
  "Ausklapp-Panel mit allen beigetretenen Projekten, Suchfeld (Name oder Identifier), Create project, Link kopieren und Drag&Drop-Sortierung; genutzt bei überschrittenem Projektlimit der Sidebar.",
  "A10a#14 A08#11")
F("PRJ", G, "Projekt-Feature-Navigation", "",
  "Einträge Work items, Cycles, Modules, Views, Pages und Intake je nach Feature-Flags und Rolle; Aktiv-Regeln für die Work-Item-Detailseite.",
  "A10a#17")
F("PRJ", G, "Tab-Navigation (TABBED)", "",
  "Tab-Zeile mit Projekt-Switcher, Projekt-Aktionsmenü, Tabs, Overflow-Menü, 'Set/Clear default' und 'Hide in more menu'; Persistenz in preferences.navigation (default_tab, hide_in_more_menu) der Projekt-User-Properties.",
  "A10a#18 A08#12 A02a#11")
F("PRJ", G, "Projekt-Benutzerpräferenzen", "intern",
  "view_props, default_props, preferences (inkl. pages.block_display) und sort_order der eigenen Projektmitgliedschaft (ProjectUserViewsEndpoint) sowie Preferences-Merge je Mitglied (ohne Self-Check).",
  "A03#27 A02a#11")

G = "Projekt-Einstellungen"
F("PRJ", G, "Projekt-Settings-Rahmen", "",
  "Sidebar mit General, Members, Features (Cycles, Modules, Views, Pages, Intake), States, Labels, Estimates und Automations; Weiterleitung auf das erste Projekt bzw. Leerseite ohne Projekte.",
  "A10a#47 A08#34 A13b#20")
F("PRJ", G, "Projekt-Einstellungen General", "",
  "Cover, Logo, Name, Beschreibung, Project ID (mit Verfügbarkeitsprüfung), Network und Timezone (vom Workspace geerbt); 'Update project' durch Workspace- oder Projekt-Admin (PATCH mit Webhook-Diffs); Bereich zum Archivieren und Löschen.",
  "A10a#48 A03#20 A02a#5 A08#34")
F("PRJ", G, "Projekt-Feature-Toggles", "",
  "Je Feature eine Settings-Seite mit Schalter für cycle_view, module_view, issue_views_view, page_view und intake_view (Aktivieren legt den Default-Intake an); Änderung sofort per PATCH. Das Datenmodell enthält zusätzlich is_time_tracking_enabled, is_issue_type_enabled und guest_view_all_features.",
  "A10a#50 A02a#6 A03#20 A08#34")
F("PRJ", G, "Disabled-Feature-Zustände", "",
  "Ist Cycles, Modules, Views, Pages oder Intake im Projekt deaktiviert, zeigt die jeweilige Seite einen Leerzustand mit Link zu den Feature-Settings (nur Admin).",
  "A08#30")

G = "Projektmitglieder & Zugriff"
F("PRJ", G, "Projektmitglieder verwalten", "",
  "Bereich Defaults (Project Lead, Default Assignee, Guest access) und Mitgliederliste mit Suche, Filter, Sortierung, Rollenwechsel (Hierarchieprüfung gegen die Workspace-Rolle), Entfernen/Verlassen und Add member; neu hinzugefügte Mitglieder erhalten die Mail 'You have been invited to a Plane project'.",
  "A10a#49 A03#24 A02a#10 A07#30 A08#34")
F("PRJ", G, "Gastzugriff auf Projektinhalte (guest_view_all_features)", "",
  "Gäste sehen ohne Freigabe nur eigene Work Items, Intake-Einträge, Pages und Views; die Freigabe ist die Projekt-Einstellung 'Guest access'.",
  "A06#28")

G = "States"
F("PRJ", G, "State-Gruppen und Default-States", "",
  "Gruppen backlog, unstarted, started, completed und cancelled (aufklappbar, mit Farben und Default-Namen) plus unsichtbarer triage-State je Projekt für Intake; 6 Default-States bei Projektanlage, Slug automatisch.",
  "A10b#83 A02b#17 A02b#18 A13b#11")
F("PRJ", G, "State anlegen und bearbeiten", "",
  "Inline-Formular je Gruppe mit Farbe, Name (max. 100 Zeichen) und Beschreibung; gruppierte Liste mit berechnetem order.",
  "A10b#84 A03#36")
F("PRJ", G, "State-Reihenfolge per Drag&Drop", "",
  "Verschieben innerhalb und zwischen Gruppen mit Neuberechnung von sequence.",
  "A10b#85 A13b#11")
F("PRJ", G, "Default-State festlegen", "",
  "'Mark as default' setzt atomar genau einen Default-State je Projekt; neue Work Items ohne State erhalten ihn.",
  "A10b#86 A03#36")
F("PRJ", G, "State löschen", "",
  "Löschen mit Bestätigung; gesperrt für den Default-State, den einzigen State einer Gruppe und States mit zugeordneten Work Items.",
  "A10b#87 A03#36 A02b#17")

G = "Labels"
F("PRJ", G, "Label-Liste mit Hierarchie", "",
  "Projekt-Labels als Baum mit aufklappbaren Gruppen (parent) und Einzel-Labels, Leerzustand und Lader.",
  "A10b#78 A02b#19")
F("PRJ", G, "Label anlegen und bearbeiten", "",
  "Inline-Formular mit Farbwahl aus 10 Label-Farben (Zufallsauswahl als Vorbelegung) und Name (Pflicht, max. 255 Zeichen, eindeutig im Projekt); Cache-Invalidierung im Backend.",
  "A10b#79 A04#14 A13b#26")
F("PRJ", G, "Labels per Drag&Drop ordnen und gruppieren", "",
  "Reihenfolge (sort_order) ändern, Label in eine Gruppe ziehen (make-child) oder auf die Wurzelebene verschieben; Auto-Scroll.",
  "A10b#80")
F("PRJ", G, "Label aus Gruppe entfernen", "",
  "Menüeintrag 'Remove from group' setzt parent auf null.",
  "A10b#81")
F("PRJ", G, "Label löschen", "",
  "Bestätigungsdialog; entfernt das Label von allen Work Items und aus View-Filtern.",
  "A10b#82 A04#14")
F("PRJ", G, "Labels per Bulk-Import (nur API)", "nur API",
  "Bulk-Anlage mehrerer Labels mit Zufallsfarbe (BulkCreateIssueLabelsEndpoint).",
  "A04#14 A02b#19")

G = "Estimates"
F("PRJ", G, "Estimates-Einstellungen", "",
  "Seite mit Schalter 'Enable estimates for my project', aktivem Schätzsystem und archivierten Systemen; Aktivierung über Project.estimate per Projekt-PATCH, last_used kennzeichnet das aktive System.",
  "A10b#73 A03#37 A02b#20")
F("PRJ", G, "Schätzsystem anlegen", "",
  "Zweistufiger Assistent: System (Points oder Categories) und Template (Fibonacci, Linear, Squares, T-Shirt Sizes, Easy to hard, Custom), dann Werte bearbeiten, ergänzen, entfernen und umsortieren (2–6 Werte).",
  "A10b#74 A03#37 A13b#18")
F("PRJ", G, "Schätzwert-Validierung", "",
  "Prüfung auf leer, Duplikat, Zahl > 0 (Points) bzw. Text (Categories) und maximal 20 Zeichen, mit Inline-Fehlern.",
  "A10b#75 A13b#18")
F("PRJ", G, "Schätzpunkte ändern und löschen (Backend)", "Backend vollständig, UI eingeschränkt",
  "API zum Hinzufügen und Ändern von Punkten sowie zum Löschen eines Punkts mit Umhängen betroffener Work Items und Umnummerierung; das CE-Frontend erlaubt nur das Anlegen und Löschen ganzer Systeme (Bearbeiten ist Bezahl-Funktion PF-01).",
  "A03#37")
F("PRJ", G, "Schätzsystem löschen", "",
  "Löschen des Systems mit Bestätigung und Abschalten der Estimates im Projekt.",
  "A10b#76 A03#37")

G = "Automationen"
F("PRJ", G, "Auto-Archive", "",
  "Projekt-Einstellung archive_in (1–12 Monate, 0 = aus): ein täglicher Job archiviert abgeschlossene/abgebrochene Work Items ohne laufenden Cycle/Modul, die so lange unverändert sind (Activity 'Plane has archived the issue').",
  "A10b#99 A02a#7 A02b#14 A07#13 A08#34")
F("PRJ", G, "Auto-Close", "",
  "Projekt-Einstellung close_in (1–12 Monate) mit wählbarem Cancelled-State: ein täglicher Job verschiebt offene Work Items, die so lange unverändert sind, in den Close-State.",
  "A10b#100 A02a#7 A07#14")

# ---------------- WI ----------------
G = "Anlegen & Bearbeiten"
F("WI", G, "Work Item anlegen (Modal)", "",
  "Create/Edit-Modal mit Projektwahl, Titel, Rich-Text-Beschreibung (Mentions, Uploads), Default-Properties-Pills, Parent, 'Create more', Discard, Save/Update und fester Tab-Reihenfolge. Das Backend sanitisiert die Beschreibung (HTML/JSON/Binary), setzt ohne State den Default-State und ohne Assignees den Default-Assignee des Projekts, verlangt einen Parent im selben Projekt und erzeugt Activity, Webhook und Description-Version.",
  "A09#66 A04#2 A02b#0 A13b#32")
F("WI", G, "Fortlaufende Work-Item-ID (PROJ-123)", "",
  "Projektbezogene, nie wiederverwendete Sequenznummer, vergeben unter einem Advisory-Lock; das Projekt führt die nächste Nummer; Reparatur doppelter Sequenzen per fix_duplicate_sequences.",
  "A02b#1")
F("WI", G, "Work Item bearbeiten", "",
  "PATCH aller Felder inkl. Ersetzen von Assignees und Labels; completed_at wird beim Wechsel in einen completed-State gesetzt und sonst geleert; skip_activity für Beschreibungs-Migrationen; Activity, Benachrichtigung, Webhook pro Feld und Description-Versionierung.",
  "A04#3 A02b#15")
F("WI", G, "Titel-Bearbeitung mit Autosave", "",
  "Textarea mit 1,5 s Debounce, Zeichenzähler n/255, Pflichtprüfung und Speicherstatus-Anzeige.",
  "A09#51")
F("WI", G, "Beschreibungsfeld mit Autosave", "",
  "Rich-Text-Beschreibung für Work Items und Intake mit Debounce-Speicherung (1 500 ms), Datei-Uploads und Mentions.",
  "A10b#103")
F("WI", G, "Toast-Aktionen nach dem Erstellen", "",
  "Toast mit 'Copy link', Identifier kopieren und 'View' (öffnet neuen Tab).",
  "A09#28")
F("WI", G, "Draft-Rückfrage beim Schließen", "",
  "'Save this draft?' mit Discard/Cancel/Save to Drafts bei ungespeicherten neuen Work Items.",
  "A09#67")
F("WI", G, "Bestehende Work Items hinzufügen (Dialog)", "",
  "Mehrfachauswahl-Dialog mit Suche, optionaler Workspace-Suche, Select all und 'Add selected work items' (für Cycles, Module und Relationen).",
  "A10a#76")

G = "Detailansicht & Peek"
F("WI", G, "Work-Item-Detailseite per Identifier", "",
  "Kanonische Route /:ws/browse/IDENT-seq mit Hauptinhalt und einklappbarer Sidebar (mobil Properties inline) und Fehlerzustand 'View other work items'. Intake-Items werden ins Intake umgeleitet, die Legacy-URL /projects/:pid/issues/:id leitet über den meta-Endpunkt weiter. Das Backend löst den Projekt-Identifier case-insensitiv auf (inkl. is_intake) mit Mitgliedschafts- und Gastprüfung und Recent-Visit.",
  "A09#49 A08#16 A10a#89 A04#5")
F("WI", G, "Work-Item-Detaildaten", "",
  "Detail-Endpunkt mit cycle_id, module_ids, label_ids, assignee_ids, Zählern, is_subscribed und expand=issue_reactions,issue_attachments,issue_link,parent; Gastprüfung und Recent-Visit.",
  "A04#4")
F("WI", G, "Work-Item-Meta und Mehrfachabruf", "intern",
  "Sequenz-ID/Projekt-Identifier eines Issues (meta) und Laden mehrerer Issues per CSV-Liste (issues/list).",
  "A04#7")
F("WI", G, "Delta-Sync für den Client-Cache", "intern",
  "v2-Paginierung nach updated_at mit optionaler Beschreibung sowie Liste archivierter/gelöschter IDs seit updated_at__gt.",
  "A04#8")
F("WI", G, "Identifier mit Klick-zum-Kopieren", "",
  "Anzeige 'IDENT-seq' in Größen und Varianten mit Tooltip 'Click to copy'.",
  "A09#52")
F("WI", G, "Detail-Kopfaktionen", "",
  "Subscribe/Unsubscribe, Copy link (absolute URL), Make a copy, Open in new tab, Archive/Restore und Delete mit Weiterleitungen.",
  "A09#50")
F("WI", G, "Peek-Overview mit drei Modi", "",
  "Side Peek, Modal und Full Screen mit Schließen, Wechsel zur Vollbildseite, Moduswechsel, Speicherstatus, Subscribe, Copy link und Menü; auch auf der Home-Seite verfügbar.",
  "A09#44 A09#48")
F("WI", G, "Peek-Inhalt", "",
  "Parent-Chip, Identifier (Klick kopiert), Titel, Beschreibung mit Autosave, Reaktionen, Versionsverlauf, Widgets, Properties und Activity.",
  "A09#45")
F("WI", G, "Peek schließen per Outside-Click/Escape", "",
  "Regelbasiertes Schließen mit Ausnahmen für Portale, Modals und Eingabefelder; der Fokus kehrt zum Listenelement zurück.",
  "A09#46")
F("WI", G, "Peek-Fehler- und Ladezustand", "",
  "'Work item does not exist' mit Illustration bzw. Skeleton während des Ladens.",
  "A09#47")
F("WI", G, "Hover-Vorschaukarte", "",
  "Karte mit Identifier, State, Name, Priority und Datum beim Überfahren eines Work-Item-Verweises.",
  "A09#73")

G = "Eigenschaften & Dropdowns"
F("WI", G, "Sidebar-Properties", "",
  "State, Assignees, Priority, Created by, Start/Due date, Estimate, Modules, Cycle, Parent und Labels mit sofortigem Speichern.",
  "A09#53")
F("WI", G, "State-Dropdown", "",
  "States mit Gruppen-Icon und Fortschritt, Suche und Workflow-Reihenfolge.",
  "A09#75")
F("WI", G, "Prioritäten und Priority-Dropdown", "",
  "Prioritäten urgent, high, medium, low und none mit Farben und PriorityIcon.",
  "A09#76 A13b#10 A02b#0")
F("WI", G, "Member-Dropdown (Assignees)", "",
  "Einzel- und Mehrfachauswahl, aktueller Nutzer zuerst '(You)', Suspended deaktiviert, 'No assignee', Avatar-Gruppe mit max. 2 Avataren + '+N'.",
  "A09#77")
F("WI", G, "Label-Dropdown mit Anlage", "",
  "Mehrfachauswahl mit Suche; Projekt-Admins legen ein Label direkt aus dem Suchbegriff an.",
  "A09#78")
F("WI", G, "Cycle-Dropdown", "",
  "Nur current/upcoming/draft Cycles wählbar, 'No cycle' zum Leeren.",
  "A09#79")
F("WI", G, "Module-Dropdown", "",
  "Einzel- und Mehrfachauswahl mit Suche.",
  "A09#80")
F("WI", G, "Estimate-Dropdown", "",
  "Schätzpunkte des aktiven Systems (Zeitwerte als h/m), 'No estimate', lazy geladen.",
  "A09#81")
F("WI", G, "Projekt-Dropdown", "",
  "Beigetretene bzw. alle Projekte, Suche über Name und Identifier, ohne archivierte Projekte.",
  "A09#82")
F("WI", G, "Datums- und Datumsbereichsauswahl", "",
  "Kalender-Popover mit min/max, Wochenstart aus dem Profil und Clear; Bereichsauswahl mit Zwei-Klick-Auswahl und zusammengeführtem Label.",
  "A09#84")
F("WI", G, "Read-only-Label-Anzeige", "",
  "Label-Chips bzw. Sammelchip 'N Labels' mit Tooltip.",
  "A09#74")

G = "Hierarchie & Relationen"
F("WI", G, "Parent setzen, ändern, entfernen", "",
  "Parent-Auswahl per Suchmodal, Parent-Chip über dem Titel mit Geschwister-Liste und 'Remove parent work item'.",
  "A09#54 A02b#2")
F("WI", G, "Sub-Work-Items", "",
  "Widget mit Fortschritt 'x/y Done', Create new / Add existing, eigenen Display-Filtern, Filtern und Gruppierung sowie verschachtelter Liste mit Properties und Menü (Edit, Copy link, Remove parent, Delete). Das Backend liefert Kinder mit State-Verteilung, Sortierung und Gruppierung und ordnet bestehende Issues als Sub-Issues zu; Hierarchie über parent_id, das Löschen des Elternteils löscht Kinder soft mit.",
  "A09#58 A04#21 A02b#2")
F("WI", G, "Relationen zwischen Work Items", "",
  "Widget mit relates_to, duplicate, blocked_by und blocking (Liste je Typ mit Properties und Menü Edit, Copy link, Remove relation, Delete). Das Backend kennt zusätzlich start_before/after, finish_before/after und implemented_by/implements, speichert eine Zeile je gerichtetem Paar und berechnet die Gegenrichtung (auch projektübergreifend im Workspace).",
  "A09#59 A04#20 A02b#3")

G = "Links & Anhänge"
F("WI", G, "Widget-Aktionsleiste", "",
  "'Add sub-work item', 'Add relation', 'Add link' und 'Attach'; Sektionen erscheinen, sobald Inhalt vorhanden ist, und öffnen sich nach einer Aktion.",
  "A09#57")
F("WI", G, "Links an Work Items", "",
  "Link-Kacheln mit Favicon/Titel, Kopieren, Bearbeiten und Löschen; Modal 'Add link'/'Update link' mit URL-Validierung. Das Backend normalisiert URLs, prüft Duplikate und crawlt Titel und Favicon (Data-URI) asynchron und SSRF-geschützt (Redirect-Revalidierung) in IssueLink.metadata; Link-Icons je Domain bzw. Dateiendung.",
  "A09#60 A04#18 A02b#4 A07#24 A06#38 A13b#27")
F("WI", G, "Anhänge an Work Items", "",
  "Upload per Button oder Dropzone mit Größenlimit und Fortschritt, Liste mit Uploader-Avatar, Öffnen und Löschen mit Bestätigung; im Intake als Kachelansicht mit Upload-Kachel. Backend: Presigned POST (MIME-Allowlist ATTACHMENT_MIME_TYPES, FILE_SIZE_LIMIT), Bestätigung erzeugt Activity, Download per Presigned-Redirect, Soft-Delete; FileAsset(entity_type=ISSUE_ATTACHMENT), Legacy-Multipart-Upload v1.",
  "A09#61 A09#62 A04#19 A02b#5 A07#17")

G = "Kommentare, Reaktionen & Aktivität"
F("WI", G, "Kommentare", "",
  "Kommentar erstellen (Enter sendet), bearbeiten (nur Autor, edited_at), löschen, Link kopieren mit Hervorhebung, Umschalten intern/öffentlich (INTERNAL/EXTERNAL) bei veröffentlichtem Projekt und Reaktionen; Lite-Editor mit voller oder kompakter Toolbar. Das Backend sanitisiert HTML, beschränkt Gäste und erzeugt Activity und Webhooks.",
  "A09#65 A10b#104 A04#15 A02b#10")
F("WI", G, "Emoji-Reaktionen auf Work Items und Kommentare", "",
  "Emoji-Picker und Reaktionsgruppe mit Zählern und Nutzer-Tooltip; Reaktionen sind eindeutig je (Objekt, Akteur, Emoji), werden als Dezimal-Codepoint gespeichert (8 Standard-Emojis), eigene sind entfernbar, jeweils mit Activity.",
  "A09#55 A04#16 A02b#8 A13b#25")
F("WI", G, "Aktivitätsverlauf", "",
  "Zeitleiste aller Änderungen (Name, Beschreibung, State, Assignees, Priority, Estimate, Parent, Relationen, Daten, Cycle, Modul, Labels, Links, Attachments, Archiv, Intake, Reaktionen, Votes) mit Akteur und relativer Zeit, zusammengeführt mit Kommentaren. IssueActivity (verb, field, old/new, identifier, epoch) bleibt nach dem Löschen des Issues erhalten; der Endpunkt ist nach activity_type und created_at__gt filterbar und liefert Intake-Quelldaten.",
  "A09#63 A04#17 A07#0 A02b#11")
F("WI", G, "Activity-Filter und -Sortierung", "",
  "Filter Updates/Comments/State/Assignee und Sortierung asc/desc, gespeichert in localStorage.",
  "A09#64 A13b#40")

G = "Versionen"
F("WI", G, "Beschreibungs-Versionshistorie", "",
  "'Last edited by' mit Versionsliste, Versionsdialog mit Navigation, Copy markdown und Restore. Das Backend speichert IssueDescriptionVersion in 600-s-Merge-Fenstern je Nutzer (auch für Intake-Items), der Cleanup behält 20 Versionen je Issue; Liste und Detail per Endpunkt.",
  "A10a#75 A09#56 A04#23 A02b#12 A07#22")
F("WI", G, "Eigenschafts-Historie (IssueVersion)", "nur API (Backfill)",
  "Snapshots von State, Assignees, Labels, Cycle und Modules mit Endpunkt; im CE nur per Backfill befüllt, der Live-Task wird nicht aufgerufen.",
  "A02b#13 A04#23")

G = "Abonnements & Mentions"
F("WI", G, "Work Items abonnieren", "",
  "Abo-Status abfragen, abonnieren, abbestellen; Subscriber durch Mitglieder hinzufügen und entfernen; Grundlage der In-App- und E-Mail-Benachrichtigungen.",
  "A04#22 A02b#7")
F("WI", G, "Erwähnungen (@Mentions) in Beschreibung und Kommentaren", "",
  "IssueMention wird aus mention-component-Knoten gepflegt; Erwähnte werden automatisch Abonnenten und erhalten Mention-Benachrichtigungen.",
  "A02b#6")

G = "Archiv, Löschen & Drafts"
F("WI", G, "Work Items archivieren und wiederherstellen", "",
  "Dialog 'Archive Work item' nur für completed/cancelled (Toast mit Hinweis auf das Projekt-Archiv), Restore im Archiv-Menü und auf der Detailseite; Archivliste mit Filter, Gruppierung und show_sub_issues, Archiv-Detail read-only mit Banner.",
  "A09#70 A09#71 A04#13 A02b#14 A08#31")
F("WI", G, "Bulk-Archivieren (Backend)", "nur API",
  "Archivieren mehrerer Work Items, nur completed/cancelled (sonst Fehlercode 4091).",
  "A04#12")
F("WI", G, "Work Item löschen", "",
  "Dialog 'Delete Work item' mit Berechtigungsprüfung (Ersteller/Admin); Soft-Delete mit Kaskade inkl. Sub-Issues, Entfernen der Recent-Visits und Activity mit Benachrichtigung.",
  "A09#72 A04#6")
F("WI", G, "Mehrere Work Items löschen", "",
  "Power-K-Dialog zum Suchen, Auswählen und Löschen mehrerer Work Items eines Projekts; Backend BulkDeleteIssuesEndpoint nur für Admins.",
  "A10a#77 A04#12")
F("WI", G, "Workspace-Drafts", "",
  "Seite /:ws/drafts mit Zähler, Liste, Load More, Inline-Properties, Doppelklick zum Bearbeiten, Make a copy, Move to project, Delete und Empty-State 'Create draft work item' (Admin/Member). DraftIssue auf Workspace-Ebene (Projekt optional) mit Assignees, Labels, Modulen und Cycle; Konvertierung in ein echtes Issue inkl. Cycle-/Modul-Zuordnung, Activities und Asset-Übernahme.",
  "A09#69 A08#17 A03#11 A04#45 A02b#16")
