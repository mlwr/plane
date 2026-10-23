# Katalog Teil 3: RT, ANA, HOME, NOTIF, SRCH, PROF, AUTH, INST, SPACE, API, WH, EXP, AI, I18N, UIX, OPS + Anhänge
from cat2 import C, F

# ---------------- RT ----------------
G = "Realtime"
F("RT", G, "Realtime-Kollaborationsserver", "",
  "WebSocket /live/collaboration (Hocuspocus) mit Authentifizierung über die Session, Redis-Skalierung, Admin-Kanal und Force-Close sowie HTTP-Endpunkte für Konvertierung und PDF-Export; nach ADR-002 in .NET (YDotNet) neu zu bauen.",
  "A01#23 A12#21")
F("RT", G, "Echtzeit-Kollaboration und Offline-Cache (Client)", "",
  "Gleichzeitiges Bearbeiten über Yjs, IndexedDB-Cache für die Sofortanzeige, automatische Wiederverbindung bei Sichtbarkeit/online und Sync-Status syncing/synced/error an den Konsumenten.",
  "A12#21")
F("RT", G, "REST-Fallback-Speicherung", "",
  "Bei Verbindungsverlust wird der Serverstand per REST geladen, gemergt und per PATCH description (description_binary, description_html, description_json) gespeichert (Autosave).",
  "A12#22 A02b#26")
F("RT", G, "Echtzeit-Seitenereignisse", "",
  "Lock/Unlock, Archive/Unarchive, Make public/private und Löschen werden per Stateless-Nachricht an alle Clients verteilt, lokal übernommen und mit Toasts angezeigt.",
  "A12#23 A10b#40")
F("RT", G, "Persistenz und Titel-Sync (Server)", "",
  "Laden und Speichern des Y-Binaries über die API (Octet-Stream; mit Sperr-/Archivprüfung, PageLog und Versionierung) inkl. HTML→Binary- und Titel-Migration; der Titel wird debounced als Page-Name gespeichert.",
  "A12#24 A04#42 A02b#26")
F("RT", G, "Fehler-Broadcast und Force-Close", "",
  "Lade- und Speicherfehler werden an die Clients gemeldet; zu große Dokumente werden instanzübergreifend getrennt (Close-Code 4001) und entladen.",
  "A12#25")
F("RT", G, "Horizontale Skalierung", "",
  "Redis-Pub/Sub je Dokument und Admin-Kanal hocuspocus:admin für mehrere Live-Instanzen.",
  "A12#26")
F("RT", G, "Dokument-Konvertierung", "",
  "POST /live/convert-document/ wandelt HTML in description_json und description_binary (Varianten rich/document); genutzt vom API-Hintergrundtask copy_s3_object beim Duplizieren einer Page.",
  "A12#27")
F("RT", G, "Health-Endpunkt des Live-Servers", "",
  "GET /live/health/ liefert status, timestamp und version.",
  "A12#29")

# ---------------- ANA ----------------
G = "Analytics"
F("ANA", G, "Workspace-Analytics mit Tabs", "",
  "Seite /:ws/analytics/:tabId mit Tabs Overview und Work items, Datumsfiltern, Projektauswahl und Leerzustand ohne Projekte; das Backend (advance.py, build_chart, date_utils) liefert Kennzahlen, Projekt-Statistiktabelle und Chart-Daten mit Datumsbereichen und Vergleichsperioden.",
  "A10b#52 A08#15 A03#47 A06#33")
F("ANA", G, "Analytics-Kennzahlen", "",
  "Kennzahlen-Kacheln je Tab (Nutzer, Rollen, Projekte, Work Items, Cycles, Intake bzw. Work-Item-Gruppen).",
  "A10b#53 A13b#31")
F("ANA", G, "Project Insights", "",
  "Radar-Chart und Liste der Projekte mit Work-Item-Anzahl.",
  "A10b#54")
F("ANA", G, "Active Projects", "",
  "Liste der Projekte mit Fertigstellungsgrad (grün über 50 %, sonst rot).",
  "A10b#55")
F("ANA", G, "Created vs Resolved", "",
  "Gestapeltes Flächendiagramm erstellter und erledigter Work Items über die Zeit.",
  "A10b#56")
F("ANA", G, "Customized Insights", "",
  "Frei konfigurierbares Balkendiagramm mit X-Achse, Metrik und Gruppierung samt Tabelle und clientseitigem CSV-Export.",
  "A10b#57 A13b#31")
F("ANA", G, "Insight-Tabelle mit CSV-Export", "",
  "Tabelle der State-Gruppen je Projekt bzw. Assignee mit Suche in der ersten Spalte und CSV-Export.",
  "A10b#58")
F("ANA", G, "Analytics-Panel für Projekt, Cycle und Modul", "",
  "Button 'Analytics' öffnet ein rechtes Panel (auch im Vollbild) mit dem Work-Items-Tab, gefiltert auf Projekt, Cycle oder Modul; das Backend liefert Kennzahlen, Assignee-Statistik und Charts (Tagesreihe für Cycle/Modul, Monatsreihe für Projekt).",
  "A10b#59 A09#3 A03#48")
F("ANA", G, "Legacy-Analytics, gespeicherte Analytics-Views und Export per E-Mail", "nur API",
  "x/y-Achsen-Plot mit Segment, Default-Analytics, AnalyticView (query_dict) und CSV-Export der Distribution als Mail-Anhang; kein CE-Frontend (die UI exportiert clientseitig).",
  "A03#49 A02a#26 A07#12")

# ---------------- HOME ----------------
G = "Home"
F("HOME", G, "Workspace-Home", "",
  "Startseite /:ws mit Begrüßung (Tageszeit, Datum, Uhrzeit), Button 'Manage widgets' und Widget-Bereich (Quick links, Recents, Your stickies, Quick Tutorial, New at Plane).",
  "A10a#20 A08#13")
F("HOME", G, "Home-Widgets verwalten", "",
  "Dialog 'Manage widgets' zum Ein-/Ausschalten und Sortieren (Drag&Drop) der Widgets quick_links, recents und my_stickies; die Präferenzen (WorkspaceHomePreference) werden beim ersten Abruf lazy angelegt.",
  "A10a#21 A03#12 A02a#23 A13b#41")
F("HOME", G, "Quickstart-Guide", "",
  "Leerzustand 'Your quickstart guide' mit Karten Create a project, Invite your team, Set up your workspace und Make Plane yours sowie Button 'Not right now'; Fortschritt nur lokal (localStorage quickstart-guide-{ws}).",
  "A10a#22")
F("HOME", G, "Quick links", "",
  "Widget mit persönlichen Links (Titel, URL, Kopieren, Bearbeiten, Öffnen, Löschen) und Dialog zum Anlegen/Bearbeiten; das Backend ergänzt http://, validiert und verhindert Duplikate je Owner.",
  "A10a#23 A03#13 A02a#22")
F("HOME", G, "Recents (zuletzt besucht)", "",
  "Widget mit zuletzt besuchten Work Items, Pages und Projekten, Filter All/Work items/Pages/Projects; Work Items öffnen im Peek. Das Backend erfasst Besuche von Projekten, Work Items, Cycles, Modulen, Views und Pages (max. 20 je Nutzer und Workspace) per recent_visited_task.",
  "A10a#24 A03#14 A02a#20 A04#46 A07#25")
F("HOME", G, "Produkt-Tour", "",
  "Willkommensdialog und fünf Tour-Schritte (Work items, Cycles, Modules, Views, Pages) mit Abschluss 'Create your first project' beim ersten Besuch; Abschluss per tour-completed.",
  "A10a#74 A03#30")
F("HOME", G, "Legacy-Dashboard und Aktivitätsgraphen (nur API)", "nur API (teilweise defekt)",
  "users/me/workspaces/{slug}/dashboard (Widgets, Dauerfilter, Tabs Upcoming/Overdue/Completed), activity-graph, issues-completed-graph, users/me/activities und last-visited-workspace (defekt); kein CE-Frontend.",
  "A03#53 A13b#41")

G = "Stickies"
F("HOME", G, "Stickies-Widget", "",
  "Widget 'Your stickies' mit gekürzter Sticky-Liste, 'Add sticky' und Link zur Stickies-Seite.",
  "A10a#25")
F("HOME", G, "Stickies-Seite", "",
  "Seite /:ws/stickies mit Suche (über description_stripped), 'Add sticky', Masonry-Layout (2–6 Spalten), Infinite Scroll (Frontend 30 je Seite, Backend-Default 20) und Drag&Drop-Sortierung; neue Notizen oben; nur der Owner hat Zugriff.",
  "A10a#26 A08#20 A03#15 A02a#21")
F("HOME", G, "Sticky bearbeiten", "",
  "Sticky-Karte mit Editor (Autosave 500 ms; Toolbar mit Hintergrundfarben, Bold, Italic, To-do-Liste und Löschen), Farbwahl und Löschen mit Bestätigung; das Backend sanitisiert HTML und prüft das Binary.",
  "A10a#27 A10b#105 A03#15")

# ---------------- NOTIF ----------------
G = "In-App-Benachrichtigungen"
F("NOTIF", G, "Erzeugung von In-App-Benachrichtigungen", "nur Backend",
  "Je Activity entstehen Notification-Einträge für Subscriber, Ersteller und Assignees (sender created/assigned/subscribed) mit Snapshot in data.issue und data.issue_activity; Indizes für Inbox-Abfragen.",
  "A07#1 A02b#31")
F("NOTIF", G, "Erwähnungs-Benachrichtigungen", "nur Backend",
  "Neue @-Erwähnungen in Beschreibung oder Kommentar (mention-component user_mention) erzeugen Notifications mit sender 'mentioned'.",
  "A07#2")
F("NOTIF", G, "Automatisches Abonnieren", "nur Backend",
  "Akteure, neue Assignees und Erwähnte werden automatisch IssueSubscriber.",
  "A07#3")
F("NOTIF", G, "Inbox-Seite und Benachrichtigungsliste", "",
  "Route /:ws/notifications mit Liste, Tabs All/Mentions mit Ungelesen-Zählern, Pagination und Leerzuständen; Ungelesen-Badge in der Top-Navigation.",
  "A10a#28 A08#18 A03#39 A13b#17")
F("NOTIF", G, "Inbox-Filter und -Optionen", "",
  "Kopfaktionen 'Mark all as read' und 'Refresh', Filtermenü 'Inbox Filters' (Assigned to me, Created by me, Subscribed by me), Optionen Show unread, Show archived und Show snoozed; angewandte Filter als Chips.",
  "A10a#29 A03#39")
F("NOTIF", G, "Benachrichtigung lesen, archivieren, snoozen", "",
  "Aktionen je Zeile: Mark as read/unread, Archive/Unarchive, Snooze (1 day, 3 days, 5 days, 1 week, 2 weeks, Custom mit Datum und Uhrzeit) und Un snooze.",
  "A10a#30 A03#39 A13b#17")
F("NOTIF", G, "Benachrichtigungs-Detail", "",
  "Rechte Spalte zeigt das betroffene Work Item im eingebetteten Peek bzw. den Intake-Inhalt; ein Klick markiert als gelesen.",
  "A10a#31")

G = "E-Mail-Benachrichtigungen"
F("NOTIF", G, "E-Mail-Benachrichtigungen (5-Minuten-Bündelung)", "nur Backend",
  "EmailNotificationLog wird alle 5 Minuten je Empfänger und Issue zu einer Mail 'issue-updates' mit Änderungsblöcken und Kommentaren gebündelt.",
  "A07#4 A02b#32")
F("NOTIF", G, "E-Mail-Benachrichtigungseinstellungen", "",
  "Profil-Schalter Property changes, State change, Work item completed, Comments und Mentions (UserNotificationPreference: property_change, state_change, issue_completed, comment, mention) steuern den E-Mail-Versand.",
  "A10a#64 A03#40 A07#5 A02b#32")

# ---------------- SRCH ----------------
G = "Suche"
F("SRCH", G, "Globale Suche", "",
  "Suche über Workspaces, Projekte, Work Items (inkl. Sequenznummer), Cycles, Modules, Views, Pages und Intake mit Sichtbarkeits- und Gastregeln, optional projektbeschränkt (GlobalSearchEndpoint).",
  "A03#43")
F("SRCH", G, "Entity-Suche für Mentions und Picker", "",
  "Suche nach user_mention, project, issue, cycle (mit Status), module und page mit count-Limit, workspace- oder projektbezogen (SearchEndpoint).",
  "A03#44")
F("SRCH", G, "Work-Item-Picker-Suche", "",
  "Suche für Parent-, Relation-, Sub-Issue-, Cycle-, Module- und Gantt-Picker mit Ausschlusslogik; Teilstring auf dem Namen und Erkennung von Projekt-Identifier und Sequenznummer.",
  "A03#45 A06#36")

G = "Power-K & Shortcuts"
F("SRCH", G, "Power-K Command Palette", "",
  "Modal (Ctrl/⌘ K) bzw. Suchfeld in der Top-Navigation mit Befehlsgruppen, Suche über Workspace/Projekt, Kontext-Chip und Unterseiten; eingebunden in Projects-, Settings- und Profil-Layouts; cmdk-Optik (Gruppen, Überschriften, Items mit Fokus-/Auswahl-/Disabled-Zustand).",
  "A10a#36 A08#42 A13a#22")
F("SRCH", G, "Power-K-Navigationsbefehle", "",
  "Befehle zum Öffnen von Projekten, Cycles, Modules, Views, Pages, Intake, Workspace-Seiten, Einstellungen und Profil (Sequenzen G+…).",
  "A10a#37")
F("SRCH", G, "Power-K-Erstellbefehle", "",
  "New work item, New project, New cycle, New module, New view, New page und New workspace mit Shortcuts.",
  "A10a#38")
F("SRCH", G, "Power-K-Kontextbefehle", "",
  "Kontextbezogene Aktionen für Work Item, Cycle, Module und Page (Status, Priorität, Zuweisung, Labels, Cycle/Module, Schätzung, Favorit, Link kopieren, Löschen).",
  "A10a#39")
F("SRCH", G, "Power-K-Account-, Preferences- und Hilfebefehle", "",
  "Befehle für Theme, Sprache, Zeitzone, Wochenstart, Profil-Einstellungen, Workspace-Einladungen, Sign out, Hilfe und Shortcut-Übersicht.",
  "A10a#40")
F("SRCH", G, "Tastatur-Shortcuts", "",
  "Globaler Shortcut-Handler mit Einzeltasten, Modifier-Kombinationen und Sequenzen (1 000 ms), Ausschluss von Eingabefeldern; Übersicht 'Keyboard shortcuts'.",
  "A10a#41")

# ---------------- PROF ----------------
G = "Profil-Einstellungen"
F("PROF", G, "Profil-Datenmodell und persönliche Einstellungen", "",
  "Profile mit Theme (system/light/dark/contrast/custom inkl. primary/background/darkPalette), Sprache, Wochenstart, Benutzer-Zeitzone, Avatar/Cover, Display-Name, App-Rail, Smooth Cursor, Notification-View-Mode, Onboarding-Schritten, Use-Case, Job-Rolle und Tour-Flags; Endpunkte ProfileEndpoint, onboard und tour-completed.",
  "A02a#12 A03#30")
F("PROF", G, "Profil-Einstellungen (Modal und Seite)", "",
  "Profil-Einstellungen als Dialog aus dem User-Menü oder als Seite /settings/profile/{general,preferences,notifications,security,api-tokens} mit Sidebar (Your profile, Developer, auf der Seite zusätzlich Workspaces).",
  "A10a#57 A08#35 A13b#20")
F("PROF", G, "Profil bearbeiten", "",
  "Cover, Avatar-Upload/-Entfernen (nur eigene Assets), Vorname, Nachname, Display name und E-Mail mit 'Change email'; Save changes (UserEndpoint.partial_update).",
  "A10a#58 A03#29")
F("PROF", G, "E-Mail-Adresse ändern", "",
  "Zweistufiger Dialog: Verifizierungscode an die neue Adresse (Throttles, Limits je User und Zieladresse, Versuchszähler), Bestätigung, Bestätigungsmails an alte und neue Adresse und anschließendes Abmelden.",
  "A10a#59 A03#31 A06#25 A07#32")
F("PROF", G, "Konto deaktivieren", "",
  "Bestätigungsdialog 'Deactivate your account': deaktiviert alle Mitgliedschaften, löscht Sessions, setzt das Profil zurück, randomisiert das Passwort, sendet eine Mail und meldet ab; gesperrt für Instanz-Admins.",
  "A10a#60 A03#32 A07#31")
F("PROF", G, "Sprache, Zeitzone und Wochenstart (Preferences)", "",
  "Auswahl der UI-Sprache, der Zeitzone und des ersten Wochentags in den Preferences; Speichern sofort.",
  "A10a#63 A13b#19")
F("PROF", G, "Verknüpfte OAuth-Konten (nur API)", "nur API",
  "Account je Provider (google, github, gitlab, gitea), eindeutig je (provider, provider_account_id); Liste, Detail und Entfernen über /api/users/me/accounts/ (liefert auch Tokens, Sicherheitsbefund E-21); kein CE-Frontend.",
  "A03#33 A06#26 A02a#13")

G = "Your work (Benutzerprofil im Workspace)"
F("PROF", G, "Your work – Summary", "",
  "Profilseite /:ws/profile/:userId mit Kennzahlen (Created/Assigned/Subscribed), Workload je Zustandsgruppe, Charts nach Priorität und Zustand und Recent activity; Statistiken nur über für den Betrachter sichtbare Work Items.",
  "A10a#32 A08#19 A03#7")
F("PROF", G, "Your work – Work-Item-Tabs", "",
  "Tabs Assigned, Created und Subscribed mit List/Kanban, Filtern und Display-Optionen (nur Admin/Member); Backend-Issue-Liste mit Filter und Gruppierung.",
  "A10a#33 A03#7")
F("PROF", G, "Your work – Activity", "",
  "Aktivitätsliste (paginiert) mit 'Load more' und 'Download today's activity' als CSV.",
  "A10a#34 A03#7")
F("PROF", G, "Profil-Sidebar", "",
  "Rechte Spalte mit Cover, Avatar, Name, Joined on, Zeitzone mit Uhrzeit und Projekt-Statistiken (Fertigstellungsgrad, Created/Assigned/Due/Completed).",
  "A10a#35")

# ---------------- AUTH ----------------
G = "Anmeldung & Registrierung"
F("AUTH", G, "Sign-in-Seite", "",
  "Startseite '/' mit E-Mail-Schritt, danach Passwort oder Unique code, OAuth-Buttons (Google, GitHub, GitLab, Gitea), Einladungs-Kopf und Fehlerbanner; eingeloggte Nutzer werden zum Workspace oder Onboarding geleitet.",
  "A08#0 A10a#67")
F("AUTH", G, "Sign-up-Seite", "",
  "/sign-up mit derselben AuthBase im SIGN_UP-Modus (Passwort mit Bestätigung oder Magic-Code).",
  "A08#1 A10a#67")
F("AUTH", G, "E-Mail-Existenzprüfung", "",
  "email-check liefert existing und status MAGIC_CODE/CREDENTIAL abhängig von is_password_autoset, SMTP und ENABLE_MAGIC_LINK_LOGIN und steuert den nächsten Login-Schritt (Web und Space).",
  "A06#0 A13b#23")
F("AUTH", G, "Anmeldung mit E-Mail und Passwort", "",
  "Formular-POST /auth/sign-in/ mit CSRF, Throttle, Instanz-Check, Passwortprüfung, Konto- und Bot-Sperren, Session-Login und Redirect auf den Web-Root mit next_path.",
  "A06#1")
F("AUTH", G, "Registrierung mit E-Mail und Passwort", "",
  "POST /auth/sign-up/ mit Signup-Sperre (ENABLE_SIGNUP, ausgenommen Eingeladene), zxcvbn-Stärkeprüfung und Anlage von User und Profile.",
  "A06#2")
F("AUTH", G, "Magic-Code anfordern", "",
  "6-stelliger Code, 10 Minuten gültig, max. 4 Codes je 10 Minuten; Versand per Celery-Mail 'Your unique Plane login code is <code>' (Web und Space).",
  "A06#3 A07#27")
F("AUTH", G, "Anmeldung/Registrierung mit Magic-Code", "",
  "Code-Prüfung mit 5 Versuchen, Fehlervarianten SIGN_IN/SIGN_UP, Neuanlage mit is_password_autoset und is_email_verified.",
  "A06#4")
F("AUTH", G, "Login mit Google", "",
  "OAuth-Code-Flow mit State in der Session, verified_email-Pflicht und offline access.",
  "A06#5")
F("AUTH", G, "Login mit GitHub inkl. Organisationspflicht", "",
  "OAuth-Flow; die primäre verifizierte E-Mail ist Pflicht, optional die Mitgliedschaft in GITHUB_ORGANIZATION_ID.",
  "A06#6")
F("AUTH", G, "Login mit GitLab (auch self-hosted)", "",
  "OAuth-Flow gegen GITLAB_HOST mit confirmed_at-Pflicht.",
  "A06#7")
F("AUTH", G, "Login mit Gitea", "",
  "OAuth-Flow gegen GITEA_HOST mit Schema-Prüfung, Pflicht einer verifizierten E-Mail und abweichender Redirect-Logik (eigene Space-Route).",
  "A06#8")
F("AUTH", G, "Profil- und Avatar-Übernahme vom Identity-Provider", "",
  "Avatar-Download SSRF-sicher in den Storage, optionaler Profilsync bei jedem Login (ENABLE_<PROVIDER>_SYNC).",
  "A06#9")
F("AUTH", G, "Steuerung der Auth-Methoden", "",
  "Instanzschalter ENABLE_SIGNUP, ENABLE_EMAIL_PASSWORD, ENABLE_MAGIC_LINK_LOGIN und IS_<PROVIDER>_ENABLED sowie Client-IDs/Secrets (verschlüsselt) aus InstanceConfiguration oder ENV; ausgeliefert über /api/instances/.",
  "A06#16")
F("AUTH", G, "Auth-Fehlercodes als Banner", "",
  "Fehlercodes 5000–5900 aus Auth-Redirects (vollständige Liste AUTHENTICATION_ERROR_CODES in 06 §2.3, Banner-Zuordnung in apps/web/helpers/authentication.helper.tsx) werden als Banner mit Titel und Text angezeigt.",
  "A08#3 A13b#23")
F("AUTH", G, "AGB-Hinweis und Auth-Fuß", "",
  "Hinweis auf Terms of Service/Privacy Policy und Marketing-Fuß mit Kundenlogos auf den Auth-Seiten (im Airgap-Betrieb konfigurierbar bzw. zu entfernen).",
  "A10a#71")
F("AUTH", G, "CSRF-Fehlerseite", "",
  "HTML-Seite 'CSRF Verification Failed' mit Link zur Startseite bei ungültigem Formular-Token.",
  "A06#30")

G = "Passwörter"
F("AUTH", G, "Passwort vergessen", "",
  "Formular 'Reset password' mit 'Send reset link' und 30-Sekunden-Timer (ohne SMTP ein Hinweis-Popover); Mail mit Reset-Link /accounts/reset-password/?uidb64&token&email, 1 h gültig (Web- und Space-Variante).",
  "A10a#68 A08#2 A06#12 A07#28")
F("AUTH", G, "Passwort zurücksetzen", "",
  "Formular mit neuem Passwort und Bestätigung; Formular-POST an /auth/reset-password/<uidb64>/<token>/ mit Token- und Stärkeprüfung, Redirect auf sign-in?success=True.",
  "A10a#69 A08#2 A06#13")
F("AUTH", G, "Passwort erstmalig setzen", "",
  "Seite /accounts/set-password (CSRF-geschützt) und JSON-POST /auth/set-password/ für Konten mit is_password_autoset (Magic-Code/OAuth).",
  "A08#2 A10a#69 A06#15")
F("AUTH", G, "Passwort ändern", "",
  "Security-Tab mit Current/New/Confirm password, Stärkeanzeige und Validierung; JSON-POST /auth/change-password/ (altes Passwort außer bei autoset), Neu-Login der aktuellen Session.",
  "A10a#65 A06#14")
F("AUTH", G, "Passwortstärke-Anzeige", "",
  "Fünf Passwortkriterien mit Stärkeermittlung und Fortschrittssegmenten (PasswordStrengthIndicator) in Sign-up, Reset, Set und Change.",
  "A13b#23")

G = "Sessions & Sicherheit"
F("AUTH", G, "Abmelden", "",
  "CSRF-geschützter Formular-POST an /auth/sign-out/ (Web), /auth/spaces/sign-out/ (Space) bzw. Admin-Sign-out; setzt last_logout_ip/time, löscht Session und Cookie, setzt alle Stores zurück und leitet um.",
  "A06#11 A10a#4 A08#44")
F("AUTH", G, "Session-Ablauf", "",
  "Bei HTTP 401 leitet das Frontend zum Login mit next_path um.",
  "A08#44")
F("AUTH", G, "Sessions und Cookies", "",
  "DB-Sessions mit 128-Zeichen-Key, device_info und user_id; getrennte Cookies session-id (7 Tage) und admin-session-id (1 h), Secure-Flag automatisch; Origin-basierter CSRF-Schutz für Schreibzugriffe (eigener oder konfigurierter Origin).",
  "A01#22 A02a#14")
F("AUTH", G, "Session-Status-Abfrage", "",
  "GET /api/users/session/ und /api/instances/admins/session/ liefern is_authenticated und den User.",
  "A06#22")
F("AUTH", G, "Rate-Limits gegen Brute-Force und Missbrauch", "",
  "Anonym 30/min, Auth 10/min (konfigurierbar), E-Mail-Verifizierung 3/h, Asset 5/min, API-Key 60/min; einheitlicher 429-Fehler RATE_LIMIT_EXCEEDED (5900).",
  "A06#23 A01#9")
F("AUTH", G, "Login-Sperre deaktivierter Konten", "",
  "Deaktivierte Konten werden in allen Login-Flows abgewiesen (Mail beim Login eines inaktiven Kontos), Sessions gelöscht; Reaktivierung nur per CLI activate_user.",
  "A06#24 A07#31")

G = "Post-Login & Onboarding"
F("AUTH", G, "Automatischer Beitritt aus angenommenen Einladungen", "",
  "Beim Login (nur App-Flows) werden Workspace- und Projektmitgliedschaften aus akzeptierten Einladungen angelegt und die Einladungen gelöscht.",
  "A06#17")
F("AUTH", G, "Weiterleitung nach dem Login", "",
  "Sichere next_path-Validierung und Zielermittlung onboarding/<slug>/invitations/create-workspace; users/me/settings liefert last/fallback Workspace und Einladungszähler, users/me/instance-admin den Admin-Status.",
  "A06#18 A03#35 A13b#27")
F("AUTH", G, "Onboarding", "",
  "Flow /onboarding: Profil (Name, Avatar, optional Passwort), Rolle und Use-Case (nur Cloud), Workspace anlegen oder offene Einladungen annehmen, Team einladen; Fortschrittsbalken, Zurück, Konto wechseln; Abschluss per onboard-Endpunkt.",
  "A10a#72 A08#4 A13b#22 A03#30")

# ---------------- INST ----------------
G = "Instanz-Backend"
F("INST", G, "Instanz-Registrierung und Versionsprüfung", "nur Backend",
  "Beim Containerstart legt register_instance die Instanz an bzw. aktualisiert sie (Name, ID, current_version, latest_version über die GitHub-API, edition) und seedet die Konfiguration.",
  "A01#13 A05#51")
F("INST", G, "Instanz-Konfiguration aus ENV und DB", "",
  "36 Schlüssel (Auth, Workspace, OAuth, SMTP, KI, Unsplash) werden beim ersten Start aus ENV in InstanceConfiguration übernommen; Secrets Fernet-verschlüsselt; Lesen und Speichern über die Admin-API.",
  "A01#14 A05#48 A02a#29")
F("INST", G, "Instanz-Info und öffentliche Konfiguration", "",
  "GET /api/instances/ liefert Instanzdaten und die abgeleitete config (Login-Methoden, Signup, SMTP, AI, Unsplash, URLs, Dateigröße) für Web, Space und Admin.",
  "A05#43 A13b#37")
F("INST", G, "Instanz-Admins verwalten (nur API)", "nur API",
  "Weitere Instanz-Admins per E-Mail mit Rolle hinzufügen, auflisten (gecacht 2 h) und entfernen; keine UI.",
  "A05#47 A06#21")
F("INST", G, "Instanz-Zustände in der Web-App", "",
  "Seiten 'Welcome to Plane' (Instanz nicht eingerichtet, Link zur Admin-App) und Wartungsmeldung (MaintenanceView).",
  "A10a#85 A08#37")

G = "God Mode – Zugang & Shell"
F("INST", G, "Erst-Einrichtung der Instanz", "",
  "God-Mode-Formular mit Vorname, Nachname, E-Mail, Firmenname, Passwort mit Stärkeanzeige und Bestätigung sowie Telemetrie-Checkbox; nativer POST an /api/instances/admins/sign-up/ legt User, Profil und InstanceAdmin an (Row-Lock gegen Doppel-Setup), setzt is_setup_done und Instanzname, meldet an und leitet auf /god-mode/general/ weiter.",
  "A11#0 A05#45 A06#19 A02a#29")
F("INST", G, "Admin-Anmeldung", "",
  "E-Mail/Passwort-Login per nativem POST an /api/instances/admins/sign-in/ mit CSRF, Fehlerbanner für Admin-Codes 5150–5190 und E-Mail-Vorbelegung aus der Query; eigenes Cookie admin-session-id (1 h), Session- und Me-Endpunkt.",
  "A11#1 A05#46 A06#20")
F("INST", G, "Admin-Abmeldung", "",
  "Menüeintrag 'Sign out' löst ein verstecktes Formular (POST /api/instances/admins/sign-out/) aus und setzt Stores und Theme auf system zurück.",
  "A11#2 A05#46")
F("INST", G, "Instanzfehler-Ansicht (God Mode)", "",
  "'Unable to fetch instance details.' mit themenabhängiger Illustration und Retry (Reload).",
  "A11#3")
F("INST", G, "Dashboard-Shell mit Sidebar", "",
  "Sidebar mit 6 Einträgen (General, Email, Authentication, Workspaces, Artificial intelligence, Images in Plane), ein-/ausklappbar (290/70 px), auf Mobile ein Overlay mit Auto-Collapse ab 768 px; Zustand in localStorage god_mode_sidebar_collapsed.",
  "A11#4")
F("INST", G, "Header mit Breadcrumb", "",
  "Breadcrumb 'Settings' plus Pfadsegmente mit festen Labels; Hamburger nur unter md.",
  "A11#5")
F("INST", G, "Konto-Menü mit Theme-Umschaltung", "",
  "Kopfzeile 'Instance admin' mit Avatar-Menü (E-Mail, 'Switch to dark/light mode', 'Sign out').",
  "A11#6")
F("INST", G, "Hilfe-Bereich der Admin-Sidebar", "",
  "'Redirect to Plane' (Web-App-Link), Hilfe-Popover (Documentation, Join our Forum, Report a bug, Version v{current_version}) und Sidebar-Toggle.",
  "A11#7")
F("INST", G, "Dialog für ungespeicherte Änderungen (God Mode)", "",
  "'You have unsaved changes' beim Zurückgehen aus einem Provider-Formular mit geänderten Werten.",
  "A11#16")
F("INST", G, "Kopierfelder für Plane-URLs", "",
  "Button mit URL-Text, kopiert in die Zwischenablage und zeigt einen Info-Toast.",
  "A11#17")
F("INST", G, "404-Seite und Fehlerbehandlung (God Mode)", "",
  "404 mit Button 'Go to general settings', Root-ErrorBoundary, HydrateFallback-Spinner und Navigations-Progressbar.",
  "A11#24")

G = "God Mode – Einstellungen"
F("INST", G, "Allgemeine Instanzeinstellungen", "",
  "Instanzname bearbeiten, Admin-E-Mail und Instance-ID read-only, Telemetrie-Switch; PATCH /api/instances/ (der Telemetrie-Export selbst entfällt nach ADR-004).",
  "A11#8 A05#44")
F("INST", G, "SMTP-Konfiguration", "",
  "SMTP-Switch im Header (Ausschalten leert die Konfiguration per DELETE disable-email-feature) und Formular Host/Port/Absender/Security (TLS/SSL/None)/Username/Passwort (verschlüsselt); Speichern setzt ENABLE_SMTP=1.",
  "A11#9 A05#49 A07#33")
F("INST", G, "Test-E-Mail senden", "",
  "Dialog in 3 Schritten (Eingabe, Erfolg, Fehler); sendet mit der gespeicherten SMTP-Konfiguration über POST /api/instances/email-credentials-check/ mit differenzierten Fehlermeldungen.",
  "A11#10 A05#49 A07#33")
F("INST", G, "Authentifizierungsmethoden-Übersicht", "",
  "Switch 'Allow anyone to sign up even without an invite' (ENABLE_SIGNUP) und Karten für Unique codes, Passwords, Google, GitHub, GitLab und Gitea mit Configure/Edit/Switch; mindestens eine Methode muss aktiv bleiben.",
  "A11#11")
F("INST", G, "Google-OAuth-Konfiguration", "",
  "Client ID/Secret, Sync-Switch, kopierbare Origin-URL und Callback-URI, Aktiv-Switch im Kopf.",
  "A11#12")
F("INST", G, "GitHub-OAuth-Konfiguration", "",
  "Client ID/Secret, Organization ID, Sync-Switch, kopierbare Origin-URL und Callback-URI, Aktiv-Switch.",
  "A11#13")
F("INST", G, "GitLab-OAuth-Konfiguration", "",
  "Host, Application ID, Secret, Sync-Switch, kopierbare Callback-URL, Aktiv-Switch.",
  "A11#14")
F("INST", G, "Gitea-OAuth-Konfiguration", "",
  "Gitea-Host (Default https://gitea.com), Client ID/Secret, Sync-Switch, kopierbare Callback-URI, Aktiv-Switch.",
  "A11#15")
F("INST", G, "AI-Einstellungen", "",
  "Felder LLM Model und API key (OpenAI) mit Hinweis-CTA; nach ADR-004 muss zusätzlich ein lokal betreibbarer OpenAI-kompatibler Endpunkt unterstützt werden.",
  "A11#18")
F("INST", G, "Bildbibliotheken (Unsplash)", "",
  "Pflichtfeld Unsplash Access Key.",
  "A11#19")

G = "God Mode – Workspaces"
F("INST", G, "Workspace-Liste der Instanz", "",
  "Liste mit Logo, Name, Slug, Owner, Projekt- und Mitgliederzahl, öffnet den Workspace in der Web-App, 'Load more' mit 10 je Seite; das Backend paginiert mit Suche.",
  "A11#20 A05#50 A13b#37")
F("INST", G, "Workspace-Anlage sperren", "",
  "Switch 'Prevent anyone else from creating a workspace.' (DISABLE_WORKSPACE_CREATION).",
  "A11#21")
F("INST", G, "Workspace anlegen (God Mode)", "",
  "Name, automatisch erzeugter und prüfbarer Slug mit URL-Präfix und Organisationsgröße; Slug-Check plus Liste reservierter Slugs; Anlage durch Instanz-Admins.",
  "A11#22 A05#50")
F("INST", G, "Willkommens-Popup 'Create workspace'", "",
  "Karte unten rechts nach dem Setup, solange keine Workspaces existieren.",
  "A11#23")

# ---------------- SPACE ----------------
G = "Veröffentlichung & Board-API"
F("SPACE", G, "Projekt veröffentlichen (Publish)", "",
  "Publish-Dialog in der Web-App mit öffentlicher URL, Layout-Auswahl, Kommentaren, Reaktionen, Voting, Intake, 'Update' und 'Unpublish'; DeployBoard mit anchor und view_props; Public Members erfassen Interaktionen von Nicht-Mitgliedern.",
  "A10a#51 A03#26 A05#42 A02a#28")
F("SPACE", G, "Board-Einstellungen und Metadaten", "",
  "Abruf der Publish-Settings (Kommentare, Reaktionen, Votes, Intake, Layouts) und der Projekt-Metadaten per Anchor sowie Anchor-Ermittlung per Projekt-ID.",
  "A05#33 A13b#36")
F("SPACE", G, "Öffentliche Issue-Liste", "",
  "Anonyme, filterbare, sortierbare und gruppierte/subgruppierte Issue-Liste des veröffentlichten Projekts mit Votes und Reaktionen.",
  "A05#34")
F("SPACE", G, "Öffentliches Issue-Detail", "",
  "Issue-Details inkl. Beschreibung, Label-, Assignee- und Modul-IDs, Votes und Reaktionen.",
  "A05#35")
F("SPACE", G, "Board-Stammdaten", "",
  "States, Labels, Mitglieder, Cycles und Module des veröffentlichten Projekts.",
  "A05#39 A13b#36")
F("SPACE", G, "Öffentliche Intake-Einreichung (nur API)", "nur API",
  "Angemeldete Nutzer reichen über das Board Intake-Issues ein und sehen, ändern und löschen eigene Einreichungen; im CE ohne UI (Basis für Intake Forms PF-36).",
  "A05#40")
F("SPACE", G, "Kommentarbilder und Asset-Auslieferung", "",
  "Upload von Kommentarbildern mit MIME-Erkennung über die Datei-Signatur, Bindung an eigene Kommentare, Auslieferung von Beschreibungs- und Kommentarbildern per Redirect, Löschen/Wiederherstellen.",
  "A05#41 A13b#29")

G = "Space-Anmeldung"
F("SPACE", G, "Space-Login: E-Mail-Check", "",
  "E-Mail eingeben; POST /auth/spaces/email-check/ entscheidet SIGN_IN/SIGN_UP und Passwort- oder Unique-Code-Schritt.",
  "A11#28 A06#10")
F("SPACE", G, "Space-Login und -Sign-up mit Passwort", "",
  "Passwort-Schritt mit Stärkeanzeige und Bestätigung beim Sign-up, nativer POST an /auth/spaces/sign-in/ bzw. /auth/spaces/sign-up/, Wechsel zu 'Sign in with unique code'.",
  "A11#29 A06#10")
F("SPACE", G, "Space-Login mit Unique Code", "",
  "Code per E-Mail (POST /auth/spaces/magic-generate/), Resend-Timer 5 s, nativer POST an magic-sign-in bzw. magic-sign-up.",
  "A11#30 A06#10")
F("SPACE", G, "OAuth-Buttons im Space", "",
  "'Sign in/up with Google/GitHub/GitLab/Gitea' für aktivierte Provider, kompakt im Passwort-Schritt; OAuth nutzt die App-Routen.",
  "A11#31 A06#10")
F("SPACE", G, "Fehlerbanner aus Auth-Redirects (Space)", "",
  "Mapping der Fehlercodes 5000–5185 auf Banner, teilweise mit Wechsel von Modus und Schritt.",
  "A11#32")
F("SPACE", G, "Rechtshinweis Terms/Privacy (Space)", "",
  "Hinweis abhängig von Sign-up oder Sign-in mit Links zu den Rechtsseiten.",
  "A11#33")
F("SPACE", G, "Eingeloggt-Ansicht und next_path-Weiterleitung", "",
  "'Nice! Just one more step.' oder automatische Weiterleitung auf einen gültigen next_path.",
  "A11#34")

G = "Öffentliches Board"
F("SPACE", G, "Instanzfehler-Ansicht (Space)", "",
  "Vollbild mit Hintergrundmuster, Logo und Retry.",
  "A11#35")
F("SPACE", G, "Legacy-URL-Weiterleitung", "",
  "/:workspaceSlug/:projectId wird auf /issues/{anchor} umgeleitet (übernimmt board und peekId).",
  "A11#36")
F("SPACE", G, "Öffentliches Projekt-Board mit Social-Meta", "",
  "/issues/:anchor lädt Publish-Settings, States und Labels; SSR setzt Titel, Beschreibung und OG/Twitter-Tags inkl. Cover-Bild.",
  "A11#37")
F("SPACE", G, "Board-Navbar", "",
  "Projektlogo und -name, Layout-Umschalter List/Board, Filter, Theme-Toggle und User-Menü (Sign out) bzw. 'Sign in'; synchronisiert board und Filter mit der URL.",
  "A11#38")
F("SPACE", G, "List-Layout (read-only)", "",
  "Gruppen je State (auf-/zuklappbar, leere sichtbar), Zeilen mit Kennung, Titel und Eigenschaften, 'Load more' je Gruppe.",
  "A11#39")
F("SPACE", G, "Kanban-Layout (read-only)", "",
  "Spalten je State (350 px), Karten mit Eigenschaften und Reaktionsleiste, Infinite-Scroll je Spalte.",
  "A11#40")
F("SPACE", G, "Eigenschafts-Chips", "",
  "State, Priorität, Labels (bis 2 einzeln, sonst Anzahl) und Fälligkeitsdatum mit Überfällig-Hervorhebung, jeweils mit Tooltip.",
  "A11#41")
F("SPACE", G, "Filter-Popover", "",
  "Suche plus Filter nach Priorität und State (Mehrfachauswahl, 'View all'); der Label-Filter ist im Original auskommentiert.",
  "A11#42")
F("SPACE", G, "Leiste aktiver Filter", "",
  "Chips je Filterwert mit Entfernen, Gruppen-Entfernen und 'Clear all'.",
  "A11#43")
F("SPACE", G, "Peek-Ansicht eines Work Items", "",
  "Modi Side Peek, Modal und Full Screen; Kennung, Titel, Beschreibung read-only, Eigenschaften State/Priority/Due date, Link kopieren; Escape/Outside-Click schließt, Fokusfalle.",
  "A11#44")
F("SPACE", G, "Öffentliche Kommentare", "",
  "Liste der EXTERNAL-Kommentare (anonym lesbar), Lite-Editor mit Toolbar, Enter zum Senden und Bild-Upload; Bearbeiten und Löschen eigener Kommentare für angemeldete Nutzer, wenn am Board aktiviert; Sign-in-Hinweis für Anonyme.",
  "A11#45 A05#36 A13b#36")
F("SPACE", G, "Kommentar-Reaktionen", "",
  "Emoji-Reaktionen auf EXTERNAL-Kommentare mit Picker setzen und entfernen; Anonyme werden zum Login geleitet.",
  "A11#46 A05#37")
F("SPACE", G, "Emoji-Reaktionen auf Work Items", "",
  "Reaktionsgruppe mit Anzahl und Nutzernamen, Picker und Umschalten eigener Reaktionen (Peek und Kanban-Karte).",
  "A11#47 A05#37")
F("SPACE", G, "Up- und Downvotes", "",
  "Zwei Vote-Buttons mit Zählern und Namens-Tooltips; Umschalten bzw. Wechsel des eigenen Votes (IssueVote -1/1, eindeutig je Akteur).",
  "A11#48 A05#38 A02b#9")
F("SPACE", G, "iframe-Einbettung", "",
  "Im iframe sind Login, Composer, Kommentar-Menü und Peek-Reaktionen ausgeblendet; Votes und Kommentar-Reaktionen bleiben ohne Wirkung.",
  "A11#49")
F("SPACE", G, "Mention-Darstellung (Space)", "",
  "@Name bzw. '@deactivated user', eigene Mentions hervorgehoben.",
  "A11#50")
F("SPACE", G, "Fehler- und 404-Seiten (Space)", "",
  "Catch-all 'That didn't work', Anchor-404, 'The public board does not exist', globale Fehlerseite 'Yikes!' und Leerzustand 'No work items found'.",
  "A11#51")
F("SPACE", G, "'Powered by Plane Publish'-Badge", "",
  "Fester Link-Badge unten rechts auf Auth-, Eingeloggt- und Board-Seiten.",
  "A11#52")

# ---------------- API ----------------
G = "Querschnitt der Public API"
F("API", G, "API-Key-Authentifizierung", "",
  "Zugriff auf /api/v1/ ausschließlich per persönlichem API-Token im Header X-Api-Key; prüft Aktivität, Ablauf und aktiven User, aktualisiert last_used; das Token gilt workspaceübergreifend.",
  "A05#0")
F("API", G, "Rate-Limiting je API-Key", "",
  "Sliding-Window-Limit (Default 60/minute, konfigurierbar) je Token mit Headern X-RateLimit-Remaining/X-RateLimit-Reset und 429-Antwort mit Fehlercode 5900.",
  "A05#1 A06#41")
F("API", G, "API-Aktivitätsprotokoll", "nur Backend",
  "Asynchrone Protokollierung aller Requests mit X-Api-Key (Token als HMAC-ID, Pfad, Methode, Query, redigierte Header, Request-/Response-Body, Status, IP, User-Agent) in APIActivityLog; tägliche Bereinigung nach API_ACTIVITY_LOG_RETENTION_DAYS (14 Tage).",
  "A05#2 A01#10 A02a#16 A07#36")
F("API", G, "OpenAPI-Dokumentation", "",
  "Optional per ENABLE_DRF_SPECTACULAR=1: OpenAPI-3-Schema nur der /api/v1/-Pfade (ohne PUT und server-Pfade) mit 14 Tags, operationIds, Beispielen und API-Key-Auth; Swagger-UI und ReDoc unter /api/schema/.",
  "A05#3 A01#17")
F("API", G, "Aktueller Benutzer", "",
  "GET /api/v1/users/me/ liefert das Kurzprofil des Token-Inhabers.",
  "A05#4")

G = "Projekte & Stammdaten"
F("API", G, "Projekte verwalten", "",
  "Projekt-CRUD inkl. Lite-Liste mit include_archived; bei Anlage Default-States und Admin-Mitgliedschaft, automatischer Default-Intake bei intake_view und Webhook-Ereignisse.",
  "A05#5")
F("API", G, "Projekt archivieren/dearchivieren", "",
  "POST/DELETE {P}/archive/ setzt bzw. entfernt archived_at und löscht die Favoriten.",
  "A05#6")
F("API", G, "Projekt-Summary", "",
  "Zählungen eines Projekts (members, states, labels, cycles, modules, issues, intakes, pages), wählbar per fields.",
  "A05#7")
F("API", G, "States verwalten", "",
  "CRUD der Workflow-States eines Projekts (ohne Triage), Default-Umschaltung, Löschschutz für Default- und belegte States, externe IDs.",
  "A05#8")
F("API", G, "Labels verwalten", "",
  "CRUD der Projekt-Labels (Schreiben nur Projekt-Admin), Namens- und External-ID-Konflikte als 409.",
  "A05#9")
F("API", G, "Workspace-Mitglieder lesen", "",
  "Liste der Workspace-Mitglieder mit Rolle und paginierte Lite-Liste.",
  "A05#26")
F("API", G, "Projekt-Mitglieder verwalten", "",
  "Projektmitglieder auflisten (voll/lite), hinzufügen, Rolle ändern und deaktivieren.",
  "A05#27")
F("API", G, "Workspace-Einladungen", "",
  "CRUD von Einladungsdatensätzen (ohne Token und ohne E-Mail-Versand), Sperren für Annahme/Antwort.",
  "A05#28")
F("API", G, "Stickies", "",
  "CRUD eigener Stickies im Workspace mit Volltextsuche über query.",
  "A05#29")
F("API", G, "User-Assets (Avatar/Cover)", "teilweise defekt im Original",
  "Upload-Tickets für Avatar- und Cover-Bilder, Upload-Bestätigung und Löschen (Server-Variante defekt).",
  "A05#30")
F("API", G, "Generic Workspace Assets", "defekt im Original (v1.4.2)",
  "Upload und Download generischer Workspace-Dateien mit externer ID (in v1.4.2 POST/GET defekt) und Upload-Bestätigung.",
  "A05#31")

G = "Work Items"
F("API", G, "Work Items verwalten", "",
  "Liste (Sortierung, External-ID-Lookup, fields/expand), Anlegen (Validierung, Default-Assignee, Default-Typ, Override von created_at/created_by), Ändern und Löschen mit Activity und Webhooks.",
  "A05#10")
F("API", G, "Work Item per Identifier", "",
  "GET {W}/work-items/{PROJ}-{seq}/ löst ein Work Item über Projekt-Identifier und Sequenznummer auf.",
  "A05#11")
F("API", G, "Work-Item-Suche", "",
  "Suche nach Name, Projekt-Identifier und Sequenznummern, workspaceweit oder projektbezogen, mit limit.",
  "A05#12")
F("API", G, "Work-Item-Links", "",
  "CRUD externer Links mit URL-Validierung, Duplikatprüfung und asynchronem Titel-Crawling.",
  "A05#13")
F("API", G, "Work-Item-Kommentare", "",
  "CRUD von Kommentaren (INTERNAL/EXTERNAL) inkl. externer IDs, Activity und Webhooks.",
  "A05#14")
F("API", G, "Work-Item-Aktivitäten", "",
  "Liste und Detail der Änderungshistorie ohne Kommentar-, Vote-, Reaction- und Draft-Einträge.",
  "A05#15")
F("API", G, "Work-Item-Anhänge", "",
  "Presigned-POST-Upload mit MIME-Allowlist und Größenlimit, Upload-Bestätigung, Liste, Download per 302-Redirect und Löschen.",
  "A05#16")
F("API", G, "Work-Item-Relationen", "",
  "Liste gruppiert nach 8 Relationstypen und Anlage (auch projektübergreifend) mit Mapping auf die gespeicherte Richtung.",
  "A05#17")
F("API", G, "Intake über die API", "",
  "Intake-Work-Items einreichen (Triage-State), auflisten, ansehen, triagieren (Status, Snooze, Duplikat, Annahme mit State-Wechsel) und löschen.",
  "A05#25")

G = "Cycles & Modules"
F("API", G, "Cycles verwalten", "",
  "CRUD, Lite-Liste und Filter cycle_view (all/current/upcoming/completed/draft/incomplete) mit Fortschrittszählungen und Konvertierung in die Projekt-Zeitzone.",
  "A05#18")
F("API", G, "Work Items in Cycles", "",
  "Work Items einem Cycle zuordnen (Verschieben aus anderen Cycles), auflisten und entfernen.",
  "A05#19")
F("API", G, "Cycle-Transfer", "",
  "Offene Work Items eines abgeschlossenen Cycles in einen anderen Cycle übertragen inkl. Progress-Snapshot.",
  "A05#20")
F("API", G, "Cycle-Archiv", "",
  "Abgeschlossene Cycles archivieren, archivierte auflisten (mit Schätzsummen) und dearchivieren.",
  "A05#21")
F("API", G, "Modules verwalten", "",
  "CRUD und Lite-Liste von Modulen inkl. Mitgliedern, Lead, Status und Fortschrittszählungen.",
  "A05#22")
F("API", G, "Work Items in Modulen", "",
  "Work Items Modulen zuordnen, auflisten und entfernen.",
  "A05#23")
F("API", G, "Modul-Archiv", "",
  "Abgeschlossene/abgebrochene Module archivieren, auflisten und dearchivieren.",
  "A05#24")

# ---------------- WH ----------------
G = "Webhooks"
F("WH", G, "Webhook-Datenmodell und Event-Typen", "",
  "Workspace-Webhooks (URL http/https, SSRF-Schutz) mit Event-Flags project, issue, module, cycle und issue_comment, Secret 'plane_wh_…', Version v1 und WebhookLog mit Retry-Count.",
  "A02a#17")
F("WH", G, "Webhook-Liste", "",
  "Workspace-Webhooks mit URL, Aktiv-Schalter und Leerzustand unter Settings → Webhooks (nur Admin).",
  "A10b#89 A08#32 A03#41")
F("WH", G, "Webhook anlegen", "",
  "Dialog mit Payload-URL und Ereignisauswahl (alle oder einzeln Projects, Cycles, Work items, Modules, Work item comments); serverseitige SSRF-Prüfung der URL.",
  "A10b#90 A03#41 A13b#38")
F("WH", G, "Webhook-Secret anzeigen, regenerieren und herunterladen", "",
  "Das Secret ist nur bei Anlage und Regenerierung sichtbar; Kopieren und CSV-Download mit Webhook-Daten und Secret; Regenerieren auf der Detailseite.",
  "A10b#91 A07#7 A03#41")
F("WH", G, "Webhook bearbeiten", "",
  "Detailseite mit URL, Aktiv-Schalter und Ereignissen.",
  "A10b#92 A03#41")
F("WH", G, "Webhook löschen", "",
  "Danger zone mit Bestätigungsdialog.",
  "A10b#93 A03#41")
F("WH", G, "Webhook-Zustellung", "nur Backend",
  "Signierte JSON-POSTs (HMAC-Header X-Plane-Signature) mit IP-Pinning, Retry (max. 5 Wiederholungen, Backoff 600 s mit Jitter) und automatischer Deaktivierung nach 6 fehlgeschlagenen Versuchen.",
  "A07#6 A06#37")
F("WH", G, "Webhook-Payload-Format", "",
  "Webhooks für project, issue, cycle, module, cycle_issue, module_issue, issue_comment, user und intake_issue werden mit den v1-Serializern der Public API serialisiert.",
  "A05#32")
F("WH", G, "Webhook-Deaktivierungs-Mail", "nur Backend",
  "Mail an den Ersteller, wenn ein Webhook wegen fehlgeschlagener Zustellungen deaktiviert wird.",
  "A07#8")
F("WH", G, "Webhook-Zustellprotokoll (nur API)", "nur API",
  "WebhookLog je Zustellversuch, abrufbar über den webhook-logs-Endpunkt (im CE-Frontend nicht genutzt), 14 Tage Aufbewahrung.",
  "A07#9 A03#41")
F("WH", G, "SSRF-Schutz und Ziel-Allowlists für Webhooks", "",
  "DNS-Auflösung mit IP-Blockliste, IP-Pinning, keine Redirects/Proxies; WEBHOOK_ALLOWED_IPS (CIDR), WEBHOOK_ALLOWED_HOSTS und WEBHOOK_DISALLOWED_DOMAINS steuern erlaubte Ziele trotz privater IP.",
  "A01#21 A07#10 A06#37")

G = "Persönliche API-Tokens"
F("WH", G, "API-Token-Liste", "",
  "Profil-Tab 'Personal Access Tokens' mit Liste (Status Active/Expired über berechnetes is_active, Beschreibung, Ablauf, letzter Gebrauch), 'Add access token' und Leerzustand.",
  "A10b#94 A10a#66 A02a#15 A03#34 A13b#38")
F("WH", G, "API-Token anlegen", "",
  "Dialog mit Titel, Beschreibung und Ablauf (1 week, 1 month, 3 months, 1 year, Custom, Never expires); das Token im Klartext wird nur einmal angezeigt und ist als CSV herunterladbar; Label/Beschreibung nachträglich änderbar.",
  "A10b#95 A02a#15 A03#34")
F("WH", G, "API-Token löschen", "",
  "Bestätigungsdialog zum Widerruf des Tokens.",
  "A10b#96 A03#34")

# ---------------- EXP ----------------
G = "Export"
F("EXP", G, "Work-Item-Export (CSV/XLSX/JSON)", "",
  "Settings → Exports: Export ausgewählter oder aller Projekte als CSV, Excel oder JSON (optional je Projekt eine Datei) als ZIP mit 28 Spalten; asynchron per Celery, serializer-basiert mit Schutz vor Formel-Injection.",
  "A10b#97 A07#11 A03#46 A02a#27 A06#35")
F("EXP", G, "Export-Historie und Download", "",
  "Tabelle früherer Exporte (ExporterHistory-Status queued/processing/completed/failed) mit Paginierung, Aktualisieren, 3-s-Polling und Download; der Presigned-Link gilt 7 Tage, der Ablauf-Job entfernt URLs nach 8 Tagen.",
  "A10b#98 A03#46 A02a#27")

# ---------------- AI ----------------
G = "Integrationen & AI"
F("AI", G, "KI-Assistent im Work-Item-Modal", "",
  "'I'm feeling lucky' (Beschreibung generieren) und GPT-Assistent-Popover mit Ladehinweis; LLM-Antwort auf task+prompt über den konfigurierten Provider (WorkspaceGPTIntegrationEndpoint, GPTIntegrationEndpoint); UI nur bei has_llm_configured.",
  "A09#68 A10a#78 A03#50 A13b#42")
F("AI", G, "Unsplash-Bildsuche", "",
  "Proxy zur Unsplash-API für Cover-Bilder im Image-Picker; ohne Access-Key leer.",
  "A03#52")

# ---------------- I18N ----------------
G = "Lokalisierung"
F("I18N", G, "Sprachauswahl und Persistenz", "",
  "Dropdown in den Profil-Preferences und im Power-K-Menü mit 22 Sprachen (feste Labels und Reihenfolge); Sprache in localStorage 'userLanguage' und im Benutzerprofil, vor der Hydration initialisiert, setzt <html lang>; nach dem Sign-out gilt Englisch.",
  "A13b#0 A08#41 A10a#63")
F("I18N", G, "Übersetzte UI-Texte mit Fallback und ICU-Pluralisierung", "",
  "Alle UI-Texte über t(key, params); Suche in allen 28 Namespaces, Fallback Englisch, dann der Key; ICU plural/select inkl. # und verschachtelter Variablen.",
  "A13b#1")
F("I18N", G, "Datums- und Zeitdarstellung", "",
  "Datumsformate (englisch), relative und kurze relative Zeit, Datumsbereiche, Dauer und Grammatik der Datumsfilter.",
  "A13b#24")
F("I18N", G, "Zeitzonen-Auswahl und -Umrechnung", "",
  "Statische Liste von 120 Zeitzonen mit aktuellem UTC/GMT-Offset (/api/timezones/, gruppiert, inkl. UTC) als durchsuchbare Auswahl für Workspace, Projekt und Profil; Hinweis, wenn die Projekt-Zeitzone von der eigenen abweicht. Das Backend rechnet Datumsfelder in die User-Zeitzone und Cycle-Start/-Ende sowie Snooze in die Projekt-Zeitzone um.",
  "A03#38 A10a#82 A08#49 A06#40")

G = "Theming"
F("I18N", G, "Theme-System und Theme-Varianten", "",
  "next-themes setzt vor dem ersten Paint <html data-theme> aus localStorage['theme'] (Default system, per prefers-color-scheme aufgelöst, OS-Wechsel live); Web kennt light, dark, light-contrast, dark-contrast und custom, Admin und Space nur light/dark (+ system); Theme-Auflösung light/dark/system.",
  "A13a#0 A13b#3 A08#40")
F("I18N", G, "Theme-Auswahl und Server-Persistenz", "",
  "Auswahl System preference, Light, Dark, Light high contrast, Dark high contrast und Custom theme (Zwei-Farben-Icon) im Profil und per Power-K; speichert Profile.theme mit Promise-Toast und lädt danach neu; das Profil-Theme wird einmal je Sitzung übernommen.",
  "A13a#1 A10a#61 A02a#12")
F("I18N", G, "Custom Theme", "",
  "Formular mit Light/Dark-Modus, Neutral- und Brand-Farbe (Hex-Validierung), Import/Download der Konfiguration als JSON; Generator berechnet 14-stufige OKLCH-Paletten (im Dark-Modus invertiert), Alpha-Stufen, Kontrastfarben per WCAG-Luminanz und Editor-Hintergründe als CSS-Variablen auf <html>; Reload nach 1 500 ms.",
  "A13a#2 A10a#62 A13b#4")
F("I18N", G, "High-Contrast-Themes", "",
  "light-contrast und dark-contrast ergänzen die Light- bzw. Dark-Basis um je 33 Token-Overrides (18 Rahmen-, 15 Label-/Text-Tokens).",
  "A13a#3")
F("I18N", G, "Farb-Token-System", "",
  "Rohpaletten, semantische Laufzeit-Tokens (--bg-*, --border-*, --txt-*, --label-*, --illustration-*) und daraus erzeugte Utilities; Flächenhierarchie Canvas → Surface → Layer; 10 Label-Farben, kontrastgerechte Icon-Farben und deterministische Pastellfarben.",
  "A13a#4 A13b#26")
F("I18N", G, "Editor-Farbpalette", "",
  "8 Text- und 8 Hintergrundfarben für Editor-Inhalte (Hintergründe je Light/Dark), Inhaltsbreiten 720/1152 px, Schriftgrößen-Skalen, Schriftstile und Zeilenabstände.",
  "A13a#21")

G = "Designsystem"
F("I18N", G, "Typografie", "",
  "Inter Variable für Body/Heading, IBM Plex Mono für Code, 19 Pixelgrößen text-8 … text-40, 6 Gewichte (350–800), 4 Laufweiten und 57 zusammengesetzte Presets.",
  "A13a#5")
F("I18N", G, "Gebündelte Schriften (Airgap)", "",
  "Inter Variable (mit Preload), IBM Plex Mono und Material Symbols Rounded werden lokal gebündelt ausgeliefert; Ladeerkennung zeigt bis dahin Skelette.",
  "A13a#6")
F("I18N", G, "Icon-System", "",
  "919 Propel-Icons in 18 Kategorien (16×16, 1em, currentColor, Outline/Filled).",
  "A13a#7")
F("I18N", G, "Status-, Zyklus-, Modul- und Prioritäts-Icons", "",
  "StateGroupIcon mit Fortschrittsbogen, IntakeStateGroupIcon, CycleGroupIcon, ModuleStatusIcon und PriorityIcon mit festen Farben und Größen.",
  "A13a#8")
F("I18N", G, "Datei-Typ-Icons und Locked-Pill", "",
  "PNG-Icons je Dateiendung für Anhänge und die Pill 'Locked'.",
  "A13a#9")
F("I18N", G, "Logo-Picker (Emoji, Lucide, Material)", "",
  "EmojiPicker-Popover mit Tabs Emoji und Icon (157 Lucide-Icons, 200 Material-Symbols, Farbwahl, Suche) für Projekte, Pages und Views; logo_props mit persistierten Icon-Namen.",
  "A13a#10")
F("I18N", G, "Emoji-Reaktions-Komponenten", "",
  "Reaktions-Chips mit Zähler und Hervorhebung, Gruppe mit Add-Button, Tooltip mit max. 5 Namen und animiertem Zähler.",
  "A13a#11")
F("I18N", G, "Empty-State-Illustrationen und theme-abhängige Assets", "",
  "59 theme-fähige Inline-SVG-Illustrationen (compact/detailed) und Light/Dark-Rasterbildpaare (Umschaltung per resolvedTheme).",
  "A13a#12")
F("I18N", G, "Propel-Komponentenbibliothek und Varianten", "",
  "68 fertige Komponenten und 57 gestylte Elemente auf Base UI 1.6.0 (vollständige Namenslisten in A13a#13 bzw. 13a §2.22/§2.23); Button/IconButton mit 6 Varianten (primary, secondary, tertiary, ghost, danger, danger-outline) × 4 Größen (xs–lg); Zustände über data-*-Attribute, Klassen über cva ohne tailwind-merge.",
  "A13a#13")
F("I18N", G, "Blocks-Composites", "",
  "Subpath-Module auth, breadcrumb, card, charts, common, context-menu, dialog, emoji-icon-picker, emoji-reaction, empty-state, icons, layout, pill-button, portal, property-select, select, skeleton, spinner, toast, types, utils, virtual-list; Select-Engine mit 7 Trigger-Varianten und 11 Property-Selects.",
  "A13a#14")
F("I18N", G, "Toast-Benachrichtigungen", "",
  "setToast/updateToast/setPromiseToast/dismissToast mit Status-Glyphen, Aktionen und Stapelung.",
  "A13a#15")
F("I18N", G, "Diagramm-Bausteine und Farbpaletten", "",
  "Bar-, Area-, Line-, Pie-, Radar- und TreeMap-Charts (recharts) mit einheitlichem Grid, Legende und Tooltip; Paletten Modern, Horizon, Earthen.",
  "A13a#16 A13b#31")
F("I18N", G, "Animationen", "",
  "18 Propel-Animations-Utilities (Slide, Fade, Spinner, Tour-Carousel, Tour-Popover, Progress-Indeterminate, Notification-Bell-Ring; vollständige Liste in A13a#17), Tailwind-Defaults spin/pulse/ping/bounce und Web-eigene Lock-/Unlock-/Text-Slide-Animationen; Web überschreibt animate-fade-out (500 ms, 100 ms Verzögerung).",
  "A13a#17")
F("I18N", G, "Maßsystem, Elevation und Scrollbars", "",
  "Control-Leiter (Höhe, Padding, Gap, Glyphe, Radius je Stufe xs–2xl), Header-Höhe 52 px, 7 Shadows, eigene Border-Breiten, standardmäßig ausgeblendete Scrollbars mit eigenen Scrollbar-Utilities und globale Basisregeln.",
  "A13a#18")
F("I18N", G, "Avatare und Farbwähler", "",
  "Avatar mit Bild oder Initialen (6 Farbvarianten), AvatarGroup mit '+N', Workspace-Avatar, ColorPicker und ColorSwatchPicker (10 Default-Farben), Drag-Handle, Drop-Indikator und Favoriten-Stern.",
  "A13a#19 A13b#26")
F("I18N", G, "Lade-Indikatoren und Navigations-Progressbar", "",
  "Animiertes Plane-Logo als Splash, Kreis- und Balken-Spinner, Skeletons sowie Fortschrittsbalken oben bei Routenwechsel (bprogress, 2,5 px, Akzentfarbe).",
  "A13a#20 A08#39")

# ---------------- UIX ----------------
G = "UI-Querschnitt"
F("UIX", G, "Seiten-Header und Breadcrumbs", "",
  "AppHeader, Breadcrumb-Links, Projekt-Breadcrumb mit Projekt-Switcher, Seitentitel (PageHead) und ContentWrapper.",
  "A10a#19")
F("UIX", G, "Leerzustände und Skeletons", "",
  "Detailed-, Simple- und Section-Leerzustände sowie Skeleton-Loader für Listen, Layouts und Einstellungen.",
  "A10a#83")
F("UIX", G, "Globale Modal-Hosts", "",
  "Globale Dialoge für Projekt-, Cycle-, Modul-, View-, Page- und Work-Item-Anlage sowie Work-Item-Löschen auf Workspace-, Projekt- und Work-Item-Ebene.",
  "A10a#84")
F("UIX", G, "Dialog- und Dropdown-Verhalten", "",
  "Escape schließt nur den obersten Dialog; Outside-Click mit Ausnahmen für Portale und data-prevent-outside-click.",
  "A13b#33")
F("UIX", G, "Tab-Reihenfolge in Formularen", "",
  "Feste Tab-Indizes für Work-Item-, Intake-, Label-, Projekt-, Cycle-, Modul-, View- und Page-Formulare; mobil deaktiviert.",
  "A13b#32")
F("UIX", G, "Synchronisierte LocalStorage-Präferenzen und Plattformerkennung", "",
  "JSON-Werte im LocalStorage, über alle Komponenten per Event synchron; Erkennung von Mobilgerät und Betriebssystem.",
  "A13b#35")
F("UIX", G, "Zwischenablage und CSV-Download", "",
  "Kopieren von Links und Text mit Fallback sowie Herunterladen von CSV-Dateien (Webhook-Secret, API-Token, Analytics, Aktivität).",
  "A13b#28")
F("UIX", G, "Warnung bei ungespeicherten Änderungen", "",
  "Warnung bei beforeunload und beim Klick auf Links, solange Änderungen ungespeichert sind.",
  "A08#46")
F("UIX", G, "Image-Picker und Uploads mit Fortschritt", "",
  "Cover-Auswahl aus Unsplash, statischen Bildern oder Upload; Avatar- und Workspace-Logo-Upload mit Entfernen; Presigned-Uploads mit Fortschrittsanzeige im Editor, für Attachments, Logos und Cover.",
  "A10a#79 A08#45")
F("UIX", G, "404-, Fehler- und Zugriffsseiten (Web)", "",
  "404-Catch-All, Fehlerseite in DEV (Stack) und PROD (freundlich mit Links), 'Workspace not found'/'Not authorized' und NotAuthorizedView.",
  "A08#37 A10a#70")
F("UIX", G, "Stale-Chunk-Auto-Reload", "",
  "Nach einem Deploy führen fehlende Chunks zu einem einmaligen Reload (höchstens einmal je 30 s), danach greift die Fehlerseite.",
  "A08#38")
F("UIX", G, "Legacy-Redirects", "",
  "Weiterleitungen alter URLs: projects/:pid/settings/*, analytics, settings/api-tokens, projects/:pid/inbox, accounts/sign-up, sign-in, signin, login, register, profile/*, settings/account/*.",
  "A08#36")
F("UIX", G, "Link-Icons und URL-Erkennung", "",
  "Icon je Domain bzw. Dateiendung sowie URL-, E-Mail- und IP-Erkennung (inkl. TLD-Liste).",
  "A13b#27")

# ---------------- OPS ----------------
G = "Deployment & Infrastruktur"
F("OPS", G, "Self-Hosting-CLI", "",
  "Interaktives Skript mit Menü 1–8 (Install/Start/Stop/Restart/Upgrade/Logs/Backup): lädt Compose/Env aus dem GitHub-Release, prüft die Architektur, kann lokal bauen, synchronisiert plane.env, erzeugt MinIO-Credentials, wartet auf Migrator und API-Health und sichert Volumes als tar.gz.",
  "A01#0")
F("OPS", G, "Daten-Restore", "",
  "Spielt Backup-Tarballs in Docker-Volumes (plane-app_*) zurück bzw. in die Datenordner der Air-Gapped-Edition (db, redis, minio/uploads, mq) mit Rollback.",
  "A01#1")
F("OPS", G, "Docker-Swarm-Deployment", "",
  "Menü Deploy/Remove/Status/Redeploy/Upgrade/Logs für einen Swarm-Stack auf Basis der CLI-Compose-Datei.",
  "A01#2")
F("OPS", G, "All-in-One-Container", "",
  "Ein Image mit supervisord (migrator, api, worker, beat, space, live, proxy), web/admin statisch; prüft Pflicht-ENV, Secrets und DOMAIN_NAME.",
  "A01#3")
F("OPS", G, "Reverse-Proxy mit automatischem HTTPS", "",
  "Caddy mit ACME (Let's Encrypt, DNS-Challenge Cloudflare/DigitalOcean), Trusted Proxies, Client-IP-Header, max_header_size 25 MB, Body-Limit FILE_SIZE_LIMIT und pfadbasiertem Routing inkl. Redirects /spaces und /god-mode.",
  "A01#4")
F("OPS", G, "Statische Frontend-Auslieferung", "",
  "Caddy :3000 für web/admin mit SPA-Fallback (try_files auf index.html bzw. /god-mode/index.html), Headern X-Frame-Options DENY, nosniff und X-XSS-Protection sowie 300 Requests/min pro IP.",
  "A01#5")
F("OPS", G, "Konfigurierbare Base-URLs und -Paths", "",
  "VITE_*_BASE_URL/_PATH (Build-Zeit) und API-seitige *_BASE_URL/_PATH für Redirects und Links zwischen web, admin, space und live.",
  "A01#6")
F("OPS", G, "Health-Checks und robots.txt", "",
  "GET / der API liefert {\"status\": \"OK\"} (nicht geloggt), GET /robots.txt sperrt Crawler (Disallow: /); Docker-HEALTHCHECKs für web, admin und space.",
  "A01#7 A05#53")
F("OPS", G, "Upload-Größenlimit mit 413-Fehler", "",
  "FILE_SIZE_LIMIT gilt für Proxy, DATA_UPLOAD_MAX_MEMORY_SIZE und Presigned-Policy und wird per /api/instances/ an die Frontends gemeldet; JSON-Fehler REQUEST_BODY_TOO_LARGE.",
  "A01#8")
F("OPS", G, "Read-Replica-Unterstützung", "",
  "Optionale zweite Datenbank; GET/HEAD/OPTIONS von Views mit use_read_replica=True gehen an die Replica, Schreibzugriffe und Migrationen an die Primary.",
  "A01#18")
F("OPS", G, "Redis mit TLS", "",
  "rediss:// mit standardmäßig aktiver Zertifikats- und Hostname-Prüfung, eigenem CA-Bundle oder Abschaltung per ENV bzw. URL-Option.",
  "A01#19")
F("OPS", G, "Objektspeicher mit Presigned Upload/Download", "",
  "S3/MinIO; Presigned POST mit Größen- und Typ-Policy, Presigned GET mit sicherer Content-Disposition (Standard 3 600 s, SIGNED_URL_EXPIRATION), Bucket-Anlage beim Start und Proxy-Route /uploads.",
  "A01#20")

G = "Dateien & Datenpflege"
F("OPS", G, "Datei-Assets (FileAsset)", "",
  "Avatar, Cover, Workspace-Logo, Projekt-Cover, Editor-Bilder und Beschreibungs-Assets per Presigned POST mit Bestätigung (is_uploaded), Entity-Zuordnung, Metadaten-Ermittlung, Soft-Delete/Restore (Undo), Existenzprüfung, serverseitigem Duplizieren (Throttle 5/min je Asset), Bulk-Zuordnung, Downloads und öffentlichen Static-Redirects (/api/assets/v2/static/<id>/, inline nur sichere Bildtypen); Legacy-v1-Endpunkte; nie bestätigte Uploads werden nach 7 Tagen entfernt.",
  "A03#42 A02a#18 A07#16 A07#18 A07#19 A13b#29")
F("OPS", G, "Soft-Delete und endgültige Löschung", "nur Backend",
  "Gelöschte Objekte werden samt abhängigen Daten soft markiert (deleted_at) und nach 60 Tagen vom täglichen hard_delete-Job physisch gelöscht.",
  "A07#34 A02a#32")
F("OPS", G, "Aufbewahrung und Bereinigung", "nur Backend",
  "Tägliche Bereinigung von API-Logs (14 Tage), Webhook-Logs (14 Tage), E-Mail-Logs (7 Tage), Page- und Description-Versionen (über 20), Export-Links (8 Tage) und nie hochgeladenen Assets (7 Tage).",
  "A07#35 A02a#32")
F("OPS", G, "Zeitgesteuerte Jobs (Beat-Plan)", "nur Backend",
  "13 Beat-Jobs: E-Mail-Benachrichtigungen und Intake-Unsnooze alle 5 min, Hard-Delete, Auto-Archive/-Close, Export-Link-Ablauf, nicht hochgeladene Assets, Log- und Versions-Cleanup, Telemetrie.",
  "A01#12")

G = "Sicherheit (Querschnitt)"
F("OPS", G, "Rich-Text-Sanitizing und Binary-Prüfung", "",
  "nh3-Sanitizing aller description_html/comment_html und Prüfung von description_binary vor dem Speichern.",
  "A06#31")
F("OPS", G, "SSRF-sichere ausgehende Requests", "",
  "Gemeinsame URL-Sicherheit für Webhooks, Link-Vorschau und Avatar-Download: DNS-Auflösung mit IP-Blockliste, IP-Pinning, keine Redirects/Proxies, Allow- und Blocklisten per ENV.",
  "A07#10")

G = "Betrieb & Entwicklung"
F("OPS", G, "Strukturiertes Request-Logging", "",
  "JSON-Logs pro Request (Methode, Pfad, Status, Dauer, IP, User-Agent, User) ohne Health-Check, rotierende Fehler-Logdatei und winston-JSON im Live-Server.",
  "A01#11")
F("OPS", G, "Betriebs-CLI (Management-Commands)", "",
  "activate_user, reset_password, create_instance_admin, reactivate_workspace_member, create_project_member, test_email, clear_cache, create_bucket, update_bucket, create_dummy_data, fix_duplicate_sequences, update_deleted_workspace_slug, wait_for_db, wait_for_migrations sowie Datenmigrations-Hilfen.",
  "A02a#30")
F("OPS", G, "Lokale Entwicklungsumgebung", "",
  "setup.sh (Env-Dateien, SECRET_KEY, MinIO-Keys, pnpm install), docker-compose-local.yml (Infrastruktur + API/Worker/Beat) und pnpm dev (web 3000, admin 3001, space 3002, live 3100).",
  "A01#24")
F("OPS", G, "Isolierter Test-Stack und Testsuites", "",
  "docker-compose-test.yml mit Postgres/Valkey/RabbitMQ/MinIO auf tmpfs; pytest-Marker unit/contract/smoke/slow; Vitest für live, blocks, services und codemods.",
  "A01#25")
F("OPS", G, "CI/CD-Pipelines", "",
  "Multi-Arch-Images (frontend, space, admin, live, backend, proxy, aio) mit GitHub-Release-Assets; Prüfungen für Version, CodeQL, Lizenz-Header, Migrationen, ruff, Format/Lint/Types, i18n-Sync und react-doctor.",
  "A01#26")
F("OPS", G, "Dummy-Daten-Generator", "",
  "Management-Command create_dummy_data erzeugt Testprojekte mit Faker-Daten.",
  "A07#38")

# ---------------- Anhänge: nicht katalogisierte Quell-Einträge ----------------
# Kategorie B: im CE-Code vorhanden, aber unerreichbar/ungenutzt
EXCL = []
def X(cat, src, grund, verweis):
    EXCL.append({"cat": cat, "src": src, "grund": grund, "verweis": verweis})

X("B", "A10a#6", "App-Rail (Dock-Leiste mit Projects/Settings, Kontextmenü Icon only/Icon with name/Dock/Undock) ist per isEnabled=false im CE nie sichtbar.", "10a-frontend-workspace-projekt-navigation.md")
X("B", "A09#86", "Read-only-Wertanzeigen (State, Priority, Member, Labels, Cycle, Module, Date, Estimate) werden im CE nicht verwendet.", "09-frontend-arbeitsobjekte-layouts.md")
X("B", "A09#87", "Generisches Layout-Framework (base-layouts: List/Kanban/Gantt, Layout-Switcher, Gruppen-Drop-Ziel, Loader) wird im CE nicht verwendet.", "09-frontend-arbeitsobjekte-layouts.md")

# Kategorie C: entfällt nach ADR-001 (Upsell/Billing) bzw. ADR-004 (Telemetrie)
X("C", "A10a#90", "Edition-Badge 'Community' und Upgrade-Modal mit Plan-Karten und Checkout.", "ADR-001; migration/features/20-paid-spuren-im-repo.md (PF-103)")
X("C", "A10a#91", "Workspace-Einstellung 'Billing and plans' mit Planvergleich.", "ADR-001; PF-103")
X("C", "A10a#92", "Pro-Badges an Active cycles, Schätzsystemen und weiteren Pro-Features.", "ADR-001; PF-103")
X("C", "A08#33", "Seite /:ws/settings/billing (nur Admin).", "ADR-001; PF-103")
X("C", "A13b#43", "Plan-Features, Preise, Upgrade-URLs und Rabattberechnung in packages/constants und packages/utils.", "ADR-001; PF-103")
X("C", "A01#15", "Telemetrie-Metriken (OTLP-Gauges alle 6 h an telemetry.plane.so) – keine Telemetrie nach außen.", "ADR-004; Schalter bleibt in CE-INST (Allgemeine Instanzeinstellungen)")
X("C", "A05#52", "Periodischer OTLP-Telemetrie-Push.", "ADR-004")
X("C", "A07#37", "Instanz-Telemetrie (OTLP-Gauges alle 6 h).", "ADR-004")

# Kategorie D: Bezahl-Spuren (nicht Teil der CE, Spezifikation in features/20–28)
X("D", "A02a#33", "Schema-Indizien für Bezahl-/Mobile-Funktionen (Teamspaces, ProjectWebhook, Device/DeviceSession, SocialLoginConnection, Integration/GitHub/Slack-Sync, Importer, ChangeLog, Zeiterfassung, Issue-Typen, Onboarding-Checkliste/AI-Chat-Flags, EE-Asset-Typen).", "PF-03, PF-05, PF-30, PF-83, PF-84, PF-86")
X("D", "A02b#33", "Work-Item-Typen und Epics (IssueType, ProjectIssueType, Issue.type).", "PF-05, PF-14")
X("D", "A03#51", "Editor-KI 'Pi'/Rephrase (POST /workspaces/{slug}/rephrase-grammar/, Backend fehlt im CE).", "PF-82")
X("D", "A04#47", "Bezahl-Andockpunkte der Arbeitsobjekte-API (Page verschieben, Page-Version wiederherstellen, archived-/favorite-pages, Page-Mentions, Bulk-Operationen, Bulk-Abonnieren, Relation per ID löschen, View-Issues, Cycle-Progress/Active-Cycles, Epics, View-Lock/Access/Publish, geteilte private Pages, Custom-Property-Filter, Intake-Kanäle).", "PF-02, PF-04, PF-06, PF-14, PF-36, PF-37, PF-44, PF-46, PF-76, PF-80")
X("D", "A09#88", "Bulk Operations (Mehrfachauswahl mit Massenänderung; im CE nur Upsell-Banner).", "PF-02")
X("D", "A09#89", "Workflows beim Drag&Drop (Sperren nicht erlaubter State-Übergänge).", "PF-68")
X("D", "A09#90", "Duplizieren in ein anderes Projekt (Erweiterung von 'Make a copy').", "PF-38")
X("D", "A09#91", "Epics (Epic-Modal, Epic-Empty-State, Epic-Layouts).", "PF-14")
X("D", "A09#92", "Work-Item-Typen, Custom Properties, Vorlagen und Konvertierung (Erweiterungspunkte im Modal-Provider und Typ-Switcher).", "PF-05, PF-06, PF-25")
X("D", "A09#93", "Timeline-Abhängigkeiten (Dependency-Linien und -Typen im Gantt).", "PF-09")
X("D", "A09#94", "Erweiterte Filteroperatoren (zusätzliche/negierte Operatoren).", "PF-52")
X("D", "A09#95", "Kommentar-Antworten (Reply-Threads, Prop enableReplies).", "PF-39")
X("D", "A09#96", "Teamspace-Gruppierung (team_project, Teamspace-Stores).", "PF-30")
X("D", "A10b#13", "Cycle-Fortschritt Pro (Burnup, Fortschrittsreihe Version 2, cycle-progress-Endpunkt).", "PF-46")
X("D", "A10b#41", "Plane AI im Page-Editor ('Ask Pi', Ton-Varianten).", "PF-82")
X("D", "A10b#42", "Page verschieben (Menüeintrag 'Move', isMovePageEnabled = false).", "PF-80")
X("D", "A10b#48", "Views veröffentlichen und teilen (useViewPublish-Stub).", "PF-43, PF-44")
X("D", "A10b#60", "Erweiterte Analytics (Zeitraumfilter, weitere Achsen/Metriken, Epic-Modus, zusätzliche Tabs).", "PF-50")
X("D", "A10b#72", "Erweiterte Intake-Funktionen (Start date, Cycle, Modules, Estimate, Parent, Intake Forms, Zuständigkeit, E-Mail-Eingang, Duplikaterkennung).", "PF-34, PF-36, PF-37, PF-104")
X("D", "A10b#77", "Advanced Estimates (Zeit-Schätzungen, Bearbeiten, Umsortieren, Wechsel bestehender Systeme).", "PF-01")
X("D", "A10b#88", "Workflows (Übergangsregeln, Sperren beim Ziehen und Anlegen).", "PF-68")
X("D", "A10b#101", "Auto-Reminders und Custom Automations (nur Texte im CE).", "PF-63, PF-67")
X("D", "A10b#102", "GitHub- und Slack-Integration (CE-Bausteine unerreichbar).", "PF-84, PF-86")
X("D", "A11#25", "OIDC-SSO (instanzweit).", "PF-93")
X("D", "A11#26", "SAML-SSO (instanzweit).", "PF-93")
X("D", "A11#27", "LDAP-Login.", "PF-97")
X("D", "A11#53", "Publish Views (öffentliche Ansichten).", "PF-44")
X("D", "A11#54", "Publish Pages (öffentliche Seiten mit Kommentaren).", "PF-73")
X("D", "A11#55", "Intake Forms (öffentliches Formular; UI fehlt, Backend-Endpunkt existiert → CE-SPACE 'Öffentliche Intake-Einreichung').", "PF-36")
X("D", "A11#56", "Weitere Board-Layouts Calendar/Spreadsheet/Gantt im Space (per view_props schaltbar, im CE nicht gerendert).", "vgl. PF-44; 11-frontend-admin-space.md")
X("D", "A12#30", "AI-Menü im Editor (AI-Handle, 'Ask Pi', Tonalität; per disabledExtensions 'ai' deaktiviert).", "PF-82")
X("D", "A12#31", "Work-Item-Embeds, Editor-Attachments, External Embeds, Draw.io, Kollaborations-Cursor und erweiterte Mentions (nur Hooks).", "PF-70, PF-71, PF-81")
X("D", "A13b#2", "i18n-Texte der Bezahl-Features (Wiki-Collections, Workflows, Work-Item-Types inkl. Custom Properties/Formeln/Hierarchie, Templates inkl. Marketplace, Automations, Integrationen, Project Updates, Produkt-Tour, Editor-Blöcke Attachment/Embed/AI).", "PF-05, PF-06, PF-08, PF-23, PF-25, PF-28, PF-63, PF-68, PF-74, PF-81, PF-82, PF-84, PF-102")

# ---------------- Ergänzende Querverweise (Gegenstück Backend/Frontend) ----------------
def ADD(d, name, srcs):
    hits = [f for f in C if f["d"] == d and f["n"] == name]
    assert len(hits) == 1, (d, name, len(hits))
    for s in srcs.split():
        if s not in hits[0]["src"]: hits[0]["src"].append(s)

ADD("WI", "Label-Dropdown mit Anlage", "A04#14")
ADD("WI", "Work Item bearbeiten", "A09#53")
ADD("WI", "Work-Item-Detaildaten", "A09#49")
ADD("WI", "Work Items abonnieren", "A09#50")
ADD("WI", "Erwähnungen (@Mentions) in Beschreibung und Kommentaren", "A12#14")
ADD("PRJ", "Projekt-Identifier prüfen und freigeben", "A10a#48")
ADD("PRJ", "Gastzugriff auf Projektinhalte (guest_view_all_features)", "A10a#49")
ADD("LV", "Work-Item-Liste mit Gruppierung und Paginierung (Backend)", "A08#24")
ADD("LV", "Anzeige-Einstellungen je Cycle und Modul", "A08#25")
ADD("LV", "Projekt-View-Liste", "A04#37")
ADD("LV", "Workspace-Views-Übersicht", "A04#38")
ADD("LV", "Projekt-Archive (Kopf und Tabs)", "A04#13")
ADD("CYC", "Cycle-Peek und Detail-Sidebar", "A04#31")
ADD("CYC", "Cycle-Detailseite", "A04#29")
ADD("MOD", "Modul-Übersicht in drei Layouts", "A04#34")
ADD("MOD", "Modul-Detailseite", "A04#35")
ADD("MOD", "Work Items Modulen zuordnen", "A09#80")
ADD("INT", "Intake-Detail", "A04#26")
ADD("PAGE", "Kollaborativer Page-Editor (Seite)", "A04#42")
ADD("PAGE", "Info-Panel", "A04#43")
ADD("PAGE", "Page-Daten und Detail", "A08#28")
ADD("PAGE", "Nutzer-Mentions im Editor", "A03#44")
ADD("PAGE", "Bilder im Editor", "A03#42")
for n in ["Analytics-Kennzahlen", "Project Insights", "Active Projects", "Created vs Resolved", "Customized Insights", "Insight-Tabelle mit CSV-Export"]:
    ADD("ANA", n, "A03#47")
ADD("HOME", "Workspace-Home", "A03#12")
ADD("NOTIF", "Benachrichtigungs-Detail", "A03#39")
ADD("SRCH", "Power-K Command Palette", "A03#43")
ADD("PROF", "Sprache, Zeitzone und Wochenstart (Preferences)", "A03#30")
ADD("PROF", "Profil-Sidebar", "A03#7")
ADD("AUTH", "Sign-in-Seite", "A06#0 A06#1")
ADD("AUTH", "Sign-up-Seite", "A06#2")
ADD("AUTH", "Passwortstärke-Anzeige", "A06#2")
ADD("AUTH", "Registrierung mit E-Mail und Passwort", "A08#1")
ADD("AUTH", "Magic-Code anfordern", "A10a#67")
for n in ["Login mit Google", "Login mit GitHub inkl. Organisationspflicht", "Login mit GitLab (auch self-hosted)", "Login mit Gitea"]:
    ADD("AUTH", n, "A08#0")
ADD("AUTH", "Steuerung der Auth-Methoden", "A11#11")
ADD("AUTH", "Session-Status-Abfrage", "A08#44")
ADD("INST", "Instanz-Konfiguration aus ENV und DB", "A13b#37")
ADD("INST", "Instanz-Zustände in der Web-App", "A05#43")
for n in ["Authentifizierungsmethoden-Übersicht", "Google-OAuth-Konfiguration", "GitHub-OAuth-Konfiguration", "GitLab-OAuth-Konfiguration", "Gitea-OAuth-Konfiguration", "AI-Einstellungen", "Bildbibliotheken (Unsplash)", "Workspace-Anlage sperren"]:
    ADD("INST", n, "A05#48")
ADD("INST", "Willkommens-Popup 'Create workspace'", "A05#50")
ADD("SPACE", "Öffentliche Issue-Liste", "A11#39 A11#40")
ADD("SPACE", "Öffentliches Issue-Detail", "A11#44")
ADD("SPACE", "Öffentliches Projekt-Board mit Social-Meta", "A05#33")
ADD("SPACE", "List-Layout (read-only)", "A05#34")
ADD("SPACE", "Kanban-Layout (read-only)", "A05#34")
ADD("SPACE", "Filter-Popover", "A05#34")
ADD("SPACE", "Peek-Ansicht eines Work Items", "A05#35")
ADD("WH", "Webhook-Datenmodell und Event-Typen", "A10b#90")
ADD("UIX", "Image-Picker und Uploads mit Fortschritt", "A03#52 A03#42")
ADD("I18N", "Sprachauswahl und Persistenz", "A02a#12")
