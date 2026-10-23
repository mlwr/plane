# Katalog Teil 2: LV, CYC, MOD, INT, PAGE
from cat1 import C, F

# ---------------- LV ----------------
G = "Seitenkopf & Layoutwahl"
F("LV", G, "Layout-Umschaltung", "",
  "Segment-Control im Seitenkopf (ab @4xl) bzw. Mobil-Menü mit List, Board (Kanban), Calendar, Table (Spreadsheet) und Timeline (Gantt); der Wechsel speichert display_filters.layout und leert den Cache; zusätzlich Layout-Dropdown als Pill-Select. Space kennt nur List und Kanban.",
  "A09#0 A09#85 A13b#5")
F("LV", G, "Projekt-Work-Items-Seite und Kopf", "",
  "Route /:ws/projects/:pid/issues mit Breadcrumb 'Work Items', Anzahl-Chip mit Tooltip, Badge 'Public' bei veröffentlichtem Projekt, Filter-Toggle, 'Display', 'Analytics' und 'Add work item'.",
  "A09#1 A08#24")
F("LV", G, "Layout-Kontextmenü im Kopf", "",
  "'…'-Menü mit 'Open in new tab' und 'Copy link' für die Work-Item-Liste.",
  "A09#2")
F("LV", G, "Layout-Kontexte Cycle, Modul, View, Archiv, Profil", "",
  "Dieselben Layouts in Cycle (inkl. Transfer bei abgeschlossenem Cycle), Modul, Projekt-View, Archiv und Profil.",
  "A09#42")

G = "Daten, Filter & Anzeige"
F("LV", G, "Work-Item-Liste mit Gruppierung und Paginierung (Backend)", "",
  "Zentrale Projekt-Issue-Liste mit Rich-Filtern (JSON) und Legacy-Filtern, order_by aus Allowlist, group_by/sub_group_by aus ISSUE_GROUP_BY_ALLOWLIST, Cursor-Paginierung pro Gruppe, Gast-Einschränkung und Recent-Visit des Projekts.",
  "A04#0 A06#32")
F("LV", G, "Rich-Filter-Ausdrücke (AND/OR/NOT)", "",
  "JSON-Filterbaum im Query-Parameter filters mit den Feldern state_id, state_group, priority, assignee_id, label_id, cycle_id, module_id, mention_id, subscriber_id, created_by_id, project_id, start/target_date und created_at/updated_at (exact/in/range) sowie is_archived und is_draft.",
  "A04#1 A13b#9")
F("LV", G, "Rich-Filter-Zeile", "",
  "Filterzeile mit Bedingungs-Chips (Eigenschaft, Operator is/is any of/between, Wert, Entfernen), 'Add filter', 'Clear all', 'Save view', 'Update view' und Ein-/Ausblenden.",
  "A09#33 A13b#9")
F("LV", G, "Filterwert-Eingaben", "",
  "Einfach- und Mehrfachauswahl mit Icons, Datum ('is') und Datumsbereich ('between', unvollständig rot markiert), Anzeige '+N more'.",
  "A09#34")
F("LV", G, "Ungültige Filterbedingung", "",
  "Chip 'Invalid filter' mit Erklärungs-Tooltip, entfernbar.",
  "A09#35")
F("LV", G, "Work-Item-Filterfelder", "",
  "15 Filterfelder (State, State Group, Priority, Label, Cycle, Module, Projects, Assignees, Mentions, Created by, Subscriber, Start/Target/Created/Updated date) mit Icons und Optionen aus Projekt- bzw. Workspace-Stammdaten; Cycle/Module nur bei aktivierten Features.",
  "A09#37 A13b#9")
F("LV", G, "View aus Filtern speichern oder aktualisieren", "",
  "'Save view' öffnet ein vorbefülltes View-Modal (Projekt/Workspace), 'Update view' schreibt Filter und Display in die eigene, nicht gesperrte View.",
  "A09#36")
F("LV", G, "Klassische Filter-Sektionen und Applied-Filter-Chips", "",
  "Filtersektionen Assignee, Created by, Mention, Label, Priority, State, State group, Cycle, Module, Project und Start/Due date mit Custom-Datumsdialog (before/after/range) sowie Chips angewendeter Filter; genutzt von Sub-Items und weiteren Bereichen.",
  "A09#32 A10a#80")
F("LV", G, "Display-Dropdown", "",
  "Display Properties (Chips), Group by, Sub-group by (nur Kanban), Order by, 'Show sub-work items' und 'Show empty groups' – erlaubte Optionen, Defaults und Query-Parameter je Seite und Layout; 13 sichtbare Property-Toggles.",
  "A09#31 A13b#6 A13b#7")
F("LV", G, "Anzeige-Einstellungen je Nutzer und Projekt", "",
  "Persistenz von filters, rich_filters, display_filters (Layout, Gruppierung, Sortierung), display_properties und preferences je Nutzer und Projekt (ProjectUserProperty).",
  "A04#10 A02a#11")
F("LV", G, "Workspace-weite Filter- und Anzeigeeinstellungen", "",
  "WorkspaceUserProperties (filters, display_filters, display_properties, rich_filters) je Nutzer und Workspace, lazy per get_or_create angelegt und per PATCH geändert.",
  "A03#8 A02a#25")
F("LV", G, "Anzeige-Einstellungen je Cycle und Modul", "",
  "filters, rich_filters, display_filters und display_properties je Nutzer für Cycle- und Modul-Ansichten.",
  "A04#33 A02b#22")

G = "List"
F("LV", G, "List-Layout mit Gruppierung", "",
  "Gruppen mit sticky Kopf (Icon, Titel, Anzahl, Collapse), ausblendbare leere Gruppen, 'Load more' je Gruppe und virtualisierte Zeilen.",
  "A09#4")
F("LV", G, "List-Zeile mit Inline-Properties", "",
  "Identifier, Titel mit Tooltip, Aufklappen der Sub-Items, Properties-Leiste und Quick-Actions; Klick öffnet den Peek, Ctrl/Cmd- oder Mittelklick einen neuen Tab.",
  "A09#5")
F("LV", G, "Sub-Work-Items in der Liste aufklappen", "",
  "Chevron lädt die Kinder und zeigt sie eingerückt (nestingLevel) direkt in der Liste.",
  "A09#6")

G = "Kanban"
F("LV", G, "Kanban-Board", "",
  "Spalten je Gruppe (350 px), Spaltenkopf mit Collapse und '+', eingeklappte Spalten vertikal, leere Spalten standardmäßig sichtbar, Paginierung je Spalte.",
  "A09#7")
F("LV", G, "Kanban-Swimlanes", "",
  "Zweite Gruppierungsebene (Sub-group by) als Swimlanes mit eigenem Kopf und Collapse.",
  "A09#8")
F("LV", G, "Kanban-Karte", "",
  "Karte mit Identifier, Titel, Properties und Quick-Action-Button; Höhe für die Virtualisierung geschätzt.",
  "A09#9")
F("LV", G, "Kanban-Löschzone", "",
  "Beim Ziehen erscheinende Zone 'Drop here to delete the work item.', die den Delete-Dialog öffnet.",
  "A09#10")
F("LV", G, "Drag-and-Drop zwischen Gruppen und Reihenfolge", "",
  "Ändert den Gruppenwert (State, Priority, Assignees, Labels, Cycle, Module) und sort_order; Overlay mit Sortierhinweis; gesperrte Ziele mit Fehlermeldung.",
  "A09#11")

G = "Calendar"
F("LV", G, "Calendar-Layout Monat/Woche", "",
  "Navigation ‹ ›, Monatsauswahl, 'Today', Optionen (Monat/Woche, Wochenenden anzeigen), Monatsraster mit Nachbartagen und Wochenstart aus dem Profil; Einträge nach target_date.",
  "A09#12 A13b#19")
F("LV", G, "Calendar-Drag auf anderen Tag", "",
  "Verschieben eines Eintrags setzt target_date auf den Zieltag.",
  "A09#13")
F("LV", G, "Calendar-Eintrag", "",
  "Eintrag mit State-Farbe, Identifier, Titel und Quick-Actions; Hervorhebung bei Drag und Peek.",
  "A09#14")
F("LV", G, "Calendar-Quick-Add je Tag", "",
  "Hover-Trigger in der Tageszelle mit 'Add work item' bzw. 'Add existing work item' (in Cycle/Modul).",
  "A09#15")

G = "Gantt/Timeline"
F("LV", G, "Gantt/Timeline-Ansicht", "",
  "Sidebar mit Work Items und Dauer, Zeitleiste Week/Month/Quarter, 'Today', Vollbild, horizontales Endlos-Scrollen und Sprung-Button zu Balken außerhalb des Sichtbereichs; Timeline-Stores für Issues, Module, Projekt und gruppierte Ansichten.",
  "A09#16 A08#48")
F("LV", G, "Gantt verschieben und Dauer ändern", "",
  "Balken per Maus verschieben, linke/rechte Kante ziehen mit Datums-Badge; Sammel-Update über issue-dates (IssueBulkUpdateDateEndpoint, Validierung Start ≤ Ziel, Activity ohne Benachrichtigung).",
  "A09#17 A04#11")
F("LV", G, "Gantt-Datum für Items ohne Datum setzen", "",
  "Hover über eine Zeile ohne Daten zeigt ein Hinzufügen-Element, das Start und Ende setzt.",
  "A09#18")
F("LV", G, "Gantt-Sidebar-Reorder", "",
  "Reihenfolge in der Sidebar per Drag&Drop (nur bei order_by sort_order).",
  "A09#19")
F("LV", G, "Timeline-Daten mit Relationen (issues-detail)", "Endpunkt aktiv, Darstellung im CE deaktiviert",
  "Ungruppierte Liste mit expand issue_relation/issue_related für Timeline-Abhängigkeiten; die Abhängigkeitslinien sind im CE per ENABLE_ISSUE_DEPENDENCIES=false deaktiviert (Bezahl-Funktion PF-09, nach ADR-001 aktiv).",
  "A04#9")

G = "Spreadsheet"
F("LV", G, "Spreadsheet-Tabelle", "",
  "Sticky erste Spalte mit Schatten beim Scrollen und 14 Spalten in fester Reihenfolge je Display-Property; editierbare Zellen (State, Priority, Assignees, Labels, Modules, Cycle, Start, Due, Estimate) und Read-only-Spalten (Created on, Updated on, Links, Attachments, Sub-work items).",
  "A09#21 A13b#8")
F("LV", G, "Spreadsheet-Sortierung über den Spaltenkopf", "",
  "Spaltenmenü mit auf-/absteigender Sortierung (Bezeichnungen je Typ: A/Z, New/Old, Low/High, Most/Least, None/Urgent, mit Icons) und Zurücksetzen; setzt order_by.",
  "A09#22 A13b#8")
F("LV", G, "Spreadsheet-Tastaturnavigation und Mehrfachauswahl", "",
  "Pfeiltasten zwischen Zellen, Enter öffnet das Zellen-Dropdown; Auswahl mit Shift/Ctrl und aktive Zeile über den Mehrfachauswahl-Store.",
  "A09#23 A08#47")
F("LV", G, "Sprung zu Sub-Work-Items aus dem Spreadsheet", "",
  "Klick auf 'N sub-work items' öffnet die Detailseite am Anker #sub-issues.",
  "A09#24")

G = "Gemeinsame Layout-Bausteine"
F("LV", G, "Inline-Property-Leiste", "",
  "State, Priority, Datumsbereich bzw. Start/Due, Assignees, Labels, Modules, Cycle, Estimate sowie Sub-Item-, Attachment- und Link-Zähler; Sichtbarkeit über Display-Properties (16 Properties standardmäßig sichtbar).",
  "A09#26 A13b#7")
F("LV", G, "Quick-Add je Layout", "",
  "Inline-Erfassung per Titel und Enter in List, Kanban, Calendar, Gantt und Spreadsheet (Formular bleibt offen), Vorbelegung aus der Gruppe, optimistische Anlage mit Promise-Toast.",
  "A09#27")
F("LV", G, "Gruppen-'+' mit 'Create work item' / 'Add an existing work item'", "",
  "Button im Gruppenkopf öffnet das Modal mit Gruppenvorbelegung; in Cycle/Modul zusätzlich bestehende Work Items hinzufügen.",
  "A09#29")
F("LV", G, "Quick-Action-Menü und Rechtsklick-Kontextmenü", "",
  "Edit, Make a copy, Open in new tab, Copy link, Remove from cycle/module, Archive (nur completed/cancelled), Restore und Delete – je Kontext (Projekt, Cycle, Modul, All work items, Archiv, Detail).",
  "A09#30")
F("LV", G, "Empty-States der Layouts", "",
  "Kontextabhängige Leerzustände (Projekt, View, Archiv, Cycle inkl. abgeschlossen, Modul, Global View, Profil) mit Aktionen bzw. 'Clear all filters'.",
  "A09#38")
F("LV", G, "Skeleton-Loader je Layout", "",
  "List-, Kanban-, Spreadsheet-, Calendar- und Gantt-Skeletons, Mutations-Spinner oben rechts und Paginations-Platzhalter.",
  "A09#39")
F("LV", G, "Virtualisierung und Endlos-Laden", "",
  "RenderIfVisible für Zeilen, Karten und Gantt-Blöcke; IntersectionObserver-Sentinels laden Folgeseiten.",
  "A09#40")
F("LV", G, "Layout-Fehlergrenze", "",
  "Fehler eines Layouts werden abgefangen und mit Fallback angezeigt.",
  "A09#41")

G = "Archive"
F("LV", G, "Projekt-Archive (Kopf und Tabs)", "",
  "Archivbereich eines Projekts mit Tabs Work items/Cycles/Modules, Filter-Toggle und Display (List-Optionen); Unterseiten archives/issues (Liste und read-only-Detail), archives/cycles und archives/modules.",
  "A09#43 A10a#88 A08#31")

G = "Projekt-Views"
F("LV", G, "Projekt-View-Liste", "",
  "Liste der Projekt-Views mit Suche, Sortierung, Filtern (Favorites, Created date, Created by), Zugriffssymbol, Live-Badge und Owner-Avatar.",
  "A10b#43 A08#27 A13b#15")
F("LV", G, "Projekt-View anlegen und bearbeiten", "",
  "Dialog mit Name, Beschreibung, Zugriff (privat/öffentlich), Logo, Rich-Filtern, Layout und Display-Optionen, auch aus der Filterzeile ('Save view'); Bearbeiten nur durch den Owner mit Lock-Prüfung. IssueView speichert Legacy- und Rich-Filter, Layout/Properties, Sperre, Archiv, Logo und Sortierung.",
  "A10b#44 A04#37 A02b#24")
F("LV", G, "Projekt-View löschen", "",
  "Bestätigungsdialog für Owner oder Projekt-Admin.",
  "A10b#45 A04#37")
F("LV", G, "View-Kontextmenü und Favoriten", "",
  "Menü mit Edit, Open in new tab, Copy link und Delete sowie Favoriten-Stern; Recent-Visit beim Öffnen.",
  "A10b#46 A04#37")
F("LV", G, "Projekt-View-Detail", "",
  "Work-Item-Layouts der View mit Switcher-Kopf, Lock-/Private-Anzeige und 'Add work item'; Layout und Display sind bei gesperrten Views ausgeblendet.",
  "A10b#47 A08#27")

G = "Workspace-Views"
F("LV", G, "Workspace-Views-Übersicht", "",
  "Seite /:ws/workspace-views mit Suche, Default-Views (All work items, Assigned, Created, Subscribed) und eigenen Views mit Edit/Delete.",
  "A10a#86 A10b#49 A08#21")
F("LV", G, "Workspace-View anlegen, bearbeiten, löschen", "",
  "Dialog Create/Update View mit Name, Beschreibung, Zugriff, Filtern und Display, Löschbestätigung sowie Quick-Actions 'Open in new tab'/'Copy link' im Kopf.",
  "A10a#87 A10b#50 A04#38")
F("LV", G, "Workspace-View-Detail (All work items)", "",
  "Spreadsheet aller Work Items der View mit View-Switcher, Filtern, Display und Quick-Actions; projektübergreifende Liste mit Rechten und Gastfilter je Projekt.",
  "A10b#51 A09#25 A08#21 A04#38")

# ---------------- CYC ----------------
G = "Cycle-Liste & Dashboard"
F("CYC", G, "Cycle-Liste mit Gruppen", "",
  "Projekt-Cycle-Liste mit aktivem Cycle oben, aufklappbaren Gruppen 'Upcoming cycle' (offen) und 'Completed cycle' (zu), Status-Badges, Leerzuständen für Filter/Suche und Lader; Backend-Liste aller bzw. des aktuellen Cycles.",
  "A10b#0 A08#25 A04#27 A13b#12")
F("CYC", G, "Cycle-Suche und Filter", "",
  "Ausklappbare Namenssuche und Filter nach Status sowie Start- und Enddatum (inkl. Custom-Datumsbereich) mit Applied-Filter-Leiste; nicht persistent.",
  "A10b#1")
F("CYC", G, "Inline-Dashboard des aktiven Cycles", "",
  "Karten 'Progress' (Gruppenanteile, Klick filtert), 'Work item burndown' (nach Work Items oder Estimate-Punkten) und Statistik-Tabs 'Priority work items' (urgent/high), 'Assignees' und 'Labels'.",
  "A10b#2 A04#29")
F("CYC", G, "Workspace-weite Active Cycles", "Upsell im CE → PF-04",
  "Route /:ws/active-cycles und Sidebar-Eintrag active_cycles; das CE zeigt nur einen Upgrade-Screen mit Pro-Badge – nach ADR-001 als echte Übersicht aller aktiven Cycles umzusetzen (Spezifikation PF-04).",
  "A10b#12 A08#14")

G = "Cycle-Verwaltung"
F("CYC", G, "Cycle anlegen und bearbeiten", "",
  "Dialog mit Projekt, Name, Beschreibung und Datumsbereich; Daten werden in der Projekt-Zeitzone als timestamptz gespeichert, Draft-Cycles ohne Daten sind erlaubt, abgeschlossene Cycles sind gesperrt; Owner, Logo, Sortierung und version (1/2).",
  "A10b#3 A04#27 A02b#21")
F("CYC", G, "Datumsüberschneidung prüfen", "",
  "cycles/date-check/ prüft vor dem Speichern, ob sich der Zeitraum mit anderen Cycles des Projekts überschneidet.",
  "A04#28 A10b#3")
F("CYC", G, "Cycle-Peek und Detail-Sidebar", "",
  "Rechte Leiste (Query peekCycle oder Detailseite, Zustand persistiert) mit Kopf, Details (Datum, Lead, Members, Work items, Points), Fortschritt und Statistik-Tabs States/Assignees/Labels mit Filterwirkung.",
  "A10b#4 A08#25")
F("CYC", G, "Fortschritt, Verteilungen und Burndown", "",
  "Ideal- und Ist-Linie über die Laufzeit, umschaltbar zwischen Work-Item-Anzahl und Estimate-Punkten; das Backend liefert Fortschrittszahlen je State-Gruppe (Issues/Punkte), Assignee- und Label-Verteilungen sowie den Burndown je Tag; optimistische Aktualisierung der Distribution im Client.",
  "A10b#5 A04#31 A06#33 A13b#12")
F("CYC", G, "Cycle-Detailseite", "",
  "Work-Item-Layouts des Cycles mit Breadcrumb-Switcher, Zähler, Layoutwahl, Filtern, Display, Analytics, 'Add work item' (nicht bei abgeschlossenem Cycle), Sidebar-Umschalter und Quick-Actions; mobile Variante.",
  "A10b#6 A08#25")
F("CYC", G, "Work Items einem Cycle zuordnen", "",
  "Zuordnung über CycleIssue (fachlich höchstens ein Cycle je Work Item, Umhängen aus anderen Cycles), Entfernen und Liste der Cycle-Work-Items.",
  "A04#29 A02b#21")
F("CYC", G, "Unvollständige Work Items übertragen", "",
  "Transfer offener Work Items eines abgeschlossenen Cycles in einen nicht abgeschlossenen Cycle per Dialog mit Suche; Fortschritt, Verteilungen und Burndown werden im progress_snapshot eingefroren und Activities erzeugt; Hinweisleiste 'Completed cycles are not editable.' über den Layouts.",
  "A10b#7 A04#30 A06#34 A02b#21")
F("CYC", G, "Cycle archivieren und wiederherstellen", "",
  "Archivieren nur abgeschlossener Cycles mit Bestätigung, Archivliste unter archives/cycles mit Verteilungen, Wiederherstellen per Menü.",
  "A10b#8 A04#32")
F("CYC", G, "Cycle löschen", "",
  "Bestätigungsdialog; Löschen inkl. Entfernen aus den Favoriten.",
  "A10b#9 A04#27")
F("CYC", G, "Cycle-Kontextmenü", "",
  "Menü und Rechtsklick-Menü mit Edit, Open in new tab, Copy link, Archive, Restore und Delete unter Rechte- und Statusbedingungen.",
  "A10b#10")
F("CYC", G, "Cycle-Favoriten", "",
  "Stern in der Listenzeile setzt bzw. entfernt den Favoriten (CycleFavoriteViewSet).",
  "A10b#11 A04#27")

# ---------------- MOD ----------------
G = "Module"
F("MOD", G, "Modul-Übersicht in drei Layouts", "",
  "Liste, Galerie (Board) und Timeline (Gantt mit Timeline-Typ MODULE) der Projektmodule mit Fortschritt, Daten, Lead, Mitgliedern und Status.",
  "A10b#14 A08#26 A09#20 A13b#13")
F("MOD", G, "Modul-Suche, Filter und Sortierung", "",
  "Suche, Filter nach Status, Lead, Mitgliedern, Start- und Zieldatum sowie Favoriten und Sortierung; Persistenz in localStorage.",
  "A10b#15 A13b#13")
F("MOD", G, "Modul anlegen und bearbeiten", "",
  "Dialog mit Projekt, Titel (eindeutig im Projekt), Beschreibung, Datumsbereich, Status, Lead und Mitgliedern (ModuleMember).",
  "A10b#16 A04#34 A02b#23")
F("MOD", G, "Modul-Status", "",
  "Statusauswahl Backlog, Planned, In Progress, Paused, Completed und Cancelled mit Farben in Liste, Formular und Sidebar.",
  "A10b#17 A13b#13")
F("MOD", G, "Modul-Links", "",
  "Links in der Modul-Sidebar anlegen, bearbeiten, kopieren, öffnen und löschen (ModuleLink, URL max. 200 Zeichen).",
  "A10b#18 A04#36 A02b#23")
F("MOD", G, "Modul-Sidebar mit Lead, Mitgliedern und Fortschritt", "",
  "Peek bzw. Detailleiste mit Status, Daten, Lead, Mitgliedern, Fortschritt (Burndown) und Statistik-Tabs; das Backend-Detail liefert Fortschritt, Schätzpunkte, Verteilungen und Burndown.",
  "A10b#19 A04#34")
F("MOD", G, "Modul-Detailseite", "",
  "Work-Item-Layouts des Moduls mit Kopf (Switcher, Layout, Filter, Display, Analytics, Add work item) und einklappbarer Sidebar; mobile Variante.",
  "A10b#20 A08#26")
F("MOD", G, "Work Items Modulen zuordnen", "",
  "n:m-Zuordnung vom Modul aus (mehrere Work Items) und vom Work Item aus (Module hinzufügen/entfernen); Liste der Modul-Work-Items.",
  "A04#35 A02b#23")
F("MOD", G, "Modul archivieren und wiederherstellen", "",
  "Archivieren nur bei Status completed/cancelled, Archivliste und -detail, Wiederherstellen.",
  "A10b#21 A04#36")
F("MOD", G, "Modul löschen", "",
  "Löschen mit Bestätigungsdialog.",
  "A10b#21 A04#34")
F("MOD", G, "Modul-Kontextmenü und Favoriten", "",
  "Menü mit Edit, Open in new tab, Copy link, Archive, Restore und Delete sowie Favoriten-Stern (ModuleFavoriteViewSet); Recent-Visit beim Öffnen.",
  "A10b#22 A04#34")

# ---------------- INT ----------------
G = "Intake"
F("INT", G, "Intake je Projekt und Triage-State", "",
  "Automatischer Default-Intake bei Aktivierung von intake_view; neue Intake-Einträge landen im unsichtbaren triage-State. IntakeIssue mit Status -2 Pending, -1 Rejected (Declined), 0 Snoozed, 1 Accepted, 2 Duplicate, duplicate_to, Quelle (IN_APP; FORMS/EMAIL nur Bezahl-Edition), source_email und extra; Übersicht mit Anzahl offener Einträge.",
  "A02b#29 A02b#18 A04#24")
F("INT", G, "Intake-Seite mit Tabs Open/Closed", "",
  "Route /:ws/projects/:pid/intake mit Liste Open/Closed, Zähler, Endlos-Laden (10 je Seite), automatischer Auswahl des ersten Eintrags, Deep-Link über inboxIssueId und mobiler Ebene; Gäste sehen nur eigene Einträge.",
  "A10b#61 A08#29 A04#25")
F("INT", G, "Intake-Filter und Sortierung", "",
  "Filter nach Status (pending/declined/snoozed/accepted/duplicate), Priorität, Assignees, Erstellern, Labels sowie Erstell- und Aktualisierungsdatum (Heute, Gestern, 7 Tage, 30 Tage, Custom) und Sortierung (created/updated/sequence); das Backend nutzt Legacy-Filter mit Präfix issue__.",
  "A10b#62 A04#25 A13b#16")
F("INT", G, "Intake-Detail", "",
  "Titel, Beschreibung, Eigenschaften (Assignees, Priorität, Due date, Labels), Status-Banner, Duplikat-Hinweis, Anhänge (Kachelansicht), Aktivitäten und Kommentare.",
  "A10b#63")
F("INT", G, "Intake-Eintrag anlegen", "",
  "Dialog mit Titel, Beschreibung, Intake-State, Priorität, Assignees, Labels, Due date und 'Create more'; Einreichen durch alle Rollen inkl. Gäste.",
  "A10b#64 A04#24 A09#83")
F("INT", G, "Intake annehmen", "",
  "'Accept' öffnet das Work-Item-Modal, setzt den Status Accepted und übernimmt das Work Item mit dem Default-State ins Projekt (Statuswechsel nur durch Admins).",
  "A10b#65 A04#26")
F("INT", G, "Intake ablehnen", "",
  "'Decline' mit Bestätigung setzt den Status Declined.",
  "A10b#66 A04#26")
F("INT", G, "Intake zurückstellen (Snooze)", "",
  "Snooze bis zu einem Datum (frühestens morgen), gespeichert als 00:00 in der Projekt-Zeitzone, und 'Un snooze'; ein Beat-Job setzt abgelaufene Snoozes alle 5 Minuten auf Pending zurück; bei einem Wechsel der Projekt-Zeitzone werden snoozed_till-Werte umgerechnet.",
  "A10b#67 A04#26 A02b#30 A07#15 A06#40")
F("INT", G, "Als Duplikat markieren", "",
  "Auswahl eines Projekt-Work-Items als Original (duplicate_to), setzt den Status Duplicate.",
  "A10b#68 A04#26")
F("INT", G, "Intake bearbeiten und löschen", "",
  "Bearbeiten der Einträge (Gäste nur Name und Beschreibung); Löschen mit Bestätigung für Admin oder Ersteller, bei nicht angenommenen Einträgen inkl. des zugehörigen Issues.",
  "A10b#69 A04#26")
F("INT", G, "Intake-Navigation", "",
  "Vor-/Zurück-Buttons und Pfeiltasten wechseln zwischen Einträgen; mobile Kopfzeile.",
  "A10b#70")
F("INT", G, "Intake-Detail in Benachrichtigungen", "",
  "Eingebettete Intake-Detailansicht in der Workspace-Inbox.",
  "A10b#71")

# ---------------- PAGE ----------------
G = "Page-Liste & Verwaltung"
F("PAGE", G, "Page-Liste mit Tabs", "",
  "Tabs Public, Private und Archived (Query type) mit Seitenblöcken, Zugriffssymbol, Favorit und Menü; das Backend liefert die Root-Pages des Projekts (eigene und öffentliche, Gast-Filter), Favoriten zuerst, und Zähler public/private/archived (summary).",
  "A10b#23 A04#39 A08#28 A13b#15")
F("PAGE", G, "Page-Suche, Filter und Sortierung", "",
  "Suchfeld (Name), Filter (Favorites, Created date, Created by) und Sortierung mit Applied-Filter-Leiste.",
  "A10b#24 A04#39")
F("PAGE", G, "Page anlegen", "",
  "'Add page' legt sofort eine leere Page an und öffnet sie; über die Command-Palette ein Anlage-Dialog mit Name, Logo und Zugriff.",
  "A10b#25 A04#40")
F("PAGE", G, "Page-Daten und Detail", "",
  "Page mit Name, access 0/1, Farbe, Labels (PageLabel), Projektzuordnung (ProjectPage), Logo, view_props.full_width, is_locked und archived_at; das Detail liefert die IDs verlinkter Work Items; parent, is_global und moved_to_* sind EE-Gerüst.",
  "A04#40 A02b#25")
F("PAGE", G, "Page sperren und entsperren", "",
  "Lock/Unlock für Owner oder Admin über REST und Stateless-Realtime-Event; Lock-Animation im Kopf.",
  "A10b#33 A04#41")
F("PAGE", G, "Page-Zugriff öffentlich/privat", "",
  "'Make private'/'Make public' (nur Owner) verschiebt die Page in den jeweiligen Tab; ProjectPagePermission: Projekt-Scope über ProjectPage, private Pages nur für den Eigentümer, Gastregel, DELETE nur Admin.",
  "A10b#34 A04#41 A06#29")
F("PAGE", G, "Page archivieren und wiederherstellen", "",
  "Archive/Restore (rekursiv inkl. Nachkommen) über REST und Realtime-Event; archivierte Pages sind read-only mit Badge.",
  "A10b#35 A04#41")
F("PAGE", G, "Page löschen", "",
  "Löschen nur archivierter Pages mit Bestätigung; Kinder werden abgehängt.",
  "A10b#38 A04#41")
F("PAGE", G, "Page duplizieren", "",
  "'Make a copy' erzeugt über duplicate/ eine Kopie mit Suffix '(Copy)', kopiert eingebettete Bilder in neue Assets, schreibt das HTML um und erzeugt JSON/Binary über den Live-Server.",
  "A10b#37 A04#44 A07#20")
F("PAGE", G, "Page favorisieren", "",
  "Favorit setzen/entfernen in Liste und Kopf (PageFavoriteViewSet).",
  "A04#44 A10b#23")
F("PAGE", G, "Page exportieren (PDF/Markdown)", "",
  "Export als PDF (Formate A4, A3, A2, Letter, Legal, Tabloid; Hoch/Quer; mit oder ohne Bilder) oder Markdown; PDF-Rendering im Browser bzw. serverseitig per POST /live/pdf-export/ (Mentions, verkleinerte Bilder).",
  "A10b#36 A12#28")
F("PAGE", G, "Referenzprotokoll der Inhalte (PageLog)", "nur Backend",
  "PageLog indiziert mention-component- und image-component-Knoten per page_transaction; Grundlage für die Liste erwähnter Work Items einer Page.",
  "A02b#28 A07#23")

G = "Page-Editor-Seite"
F("PAGE", G, "Kollaborativer Page-Editor (Seite)", "",
  "Editor-Seite /pages/:pageId mit Echtzeit-Kollaboration, separatem Titel-Editor (Platzhalter 'Untitled', Tastaturnavigation Titel↔Inhalt), Logo, Mentions, Asset-Upload, REST-Fallback, Lade-Skeleton, Sync-Status und Inhaltslimit-Banner.",
  "A10b#26 A08#28 A12#3")
F("PAGE", G, "Page-Toolbar", "",
  "Formatierungsleiste (Typografie, Marks, Ausrichtung, Listen, Zitat, Code, Tabelle, Bild, Farben), optional sticky.",
  "A10b#27")
F("PAGE", G, "Page-Kopf", "",
  "Breadcrumb mit Page-Switcher, Lock-Anzeige, Favorit, Link kopieren, Archiv-, Offline- und Syncing-Badges sowie Menü.",
  "A10b#28")
F("PAGE", G, "Outline", "",
  "Tab im Navigationsbereich mit Überschriften-Gliederung (Heading-Liste) und schwebendem Mini-Outline; Klick scrollt zur Überschrift.",
  "A10b#29 A12#19")
F("PAGE", G, "Info-Panel", "",
  "Dokumentinfo (Words, Characters, Paragraphs, Read time), Ersteller/Bearbeiter und Versionsliste.",
  "A10b#30 A12#19")
F("PAGE", G, "Assets-Panel", "",
  "Liste der in der Page eingebetteten Bilder mit Vorschau, Name und Download.",
  "A10b#31")
F("PAGE", G, "Versionshistorie", "Erzeugung im Original defekt",
  "Read-only-Ansicht früherer Versionen (Query version) mit Wiederherstellen durch Ersetzen des Editorinhalts; das Backend sieht PageVersion in 600-s-Merge-Fenstern je Besitzer mit max. 20 Versionen vor, die Versionen werden im Original durch einen Bug nie erzeugt.",
  "A10b#32 A04#43 A02b#27 A07#21")
F("PAGE", G, "Page-Anzeigeoptionen", "",
  "Full width, Sticky toolbar, Copy markdown und Version history im Page-Menü; Einstellungen in pages_config.",
  "A10b#39")

G = "Editor (packages/editor)"
F("PAGE", G, "Rich-Text-Editor", "",
  "Vollständiger Editor für Work-Item-Beschreibung, Intake und Space mit Bubble-Menü, Slash-Commands, Side-Menu/Drag-Handle, Block-Menü und History; externer value-Sync (SWR), onChange mit isMigrationUpdate.",
  "A12#0")
F("PAGE", G, "Lite-Text-Editor", "",
  "Schlanker Editor ohne Menüs für Kommentare und Stickies; Enter sendet ab (onEnterKeyPress), Shift-Enter erzeugt Zeilenumbruch bzw. Listen-Split; Toolbars der Konsumenten über executeMenuItemCommand.",
  "A12#1")
F("PAGE", G, "Dokument-Editor (read-only, Versionen)", "",
  "Nicht-kollaborativer Document-Editor mit PageRenderer, Outline und Slash-Commands; genutzt für Page- und Beschreibungs-Versionen.",
  "A12#2 A10b#107")
F("PAGE", G, "Slash-Command-Menü", "",
  "'/'-Menü mit Text, H1–H6, Listen, To-do, Tabelle, Quote, Code, Image, Callout, Divider, Emoji sowie 9 Text- und 9 Hintergrundfarben; Suche über Titel, Beschreibung und Suchbegriffe mit Treffer-Hervorhebung.",
  "A12#4")
F("PAGE", G, "Bubble-Menü", "",
  "Bei Textselektion: Node-Typ-Auswahl, Link setzen/entfernen mit Validierung, Text-/Hintergrundfarbe, Bold/Italic/Underline/Strike (bei Code nur Code) und Ausrichtung links/zentriert/rechts.",
  "A12#5")
F("PAGE", G, "Drag-Handle, Block-Menü und Block-Drag&Drop", "",
  "Side-Menu mit Drag-Handle neben jedem Block; Klick öffnet das Block-Menü (Delete, Duplicate, Fit to width bei Tabellen); Drag&Drop von Blöcken inkl. Listen-Umbau und Autoscroll.",
  "A12#6")
F("PAGE", G, "Textstruktur", "",
  "Heading 1–6, Paragraph, Textausrichtung (left/center/right), Blockquote (Enter verlässt das Zitat) und horizontale Linie (---, ___, ***).",
  "A12#7")
F("PAGE", G, "Listen (Aufzählung, Nummerierung, To-do)", "",
  "Bullet-, Ordered- und Task-Listen mit Verschachtelung, Tab/Shift-Tab, eigener Backspace/Delete-Logik, automatischem Zusammenführen benachbarter Listen und Checkbox-Styling (erledigte Items ausgegraut).",
  "A12#8")
F("PAGE", G, "Text-Formatierung und Farben", "",
  "Bold, Italic, Underline, Strike, Inline-Code (Mod-e, Backticks), 8 Text- und 8 Hintergrundfarben (Light/Dark-Varianten) und Typografie-Ersetzungen (—, …, →, ©, ½, ×).",
  "A12#9")
F("PAGE", G, "Code-Block mit Syntax-Highlighting", "",
  "Code-Block per ``` bzw. ~~~ (mit Sprache), lowlight-Highlighting (common + ts, GitHub-Dark-Theme), Copy-Button 'Copy code', Tab-Einrückung, VS-Code-Paste übernimmt die Sprache, Rückumwandlung in Absätze.",
  "A12#10")
F("PAGE", G, "Tabellen", "",
  "3×3-Tabellen, Spaltenbreiten-Resize, Header-Zeile/-Spalte, Zeilen-/Spalten-Handles mit Dropdown (Insert, Duplicate, Clear, Delete, Hintergrundfarbe), Drag&Drop von Zeilen/Spalten, '+'-Buttons mit Drag zum Hinzufügen/Entfernen, Zellselektions-Rahmen, Tab-Navigation und Fit to width.",
  "A12#11")
F("PAGE", G, "Bilder im Editor", "",
  "Bild per Slash/Toolbar, Drop oder Paste; Upload mit Fortschritt; Resize mit Seitenverhältnis; Ausrichtung; Download; Vollbild mit Zoom (0,5–2×) und Pan; Restore bei Ladefehler; Asset-Duplizierung beim Einfügen aus Plane mit Retry; Lösch-Tracking.",
  "A12#12")
F("PAGE", G, "Callouts", "",
  "Callout-Block mit Emoji- oder Icon-Logo und wählbarer Hintergrundfarbe; die letzte Wahl wird in localStorage gemerkt; Pfeiltasten/Backspace an den Blockgrenzen.",
  "A12#13")
F("PAGE", G, "Nutzer-Mentions im Editor", "",
  "'@'-Suche (debounced 300 ms, Sektionen) nach Nutzern; Darstellung als @Name-Chip mit Hover-Profilkarte (Avatar, Name, Rolle) und Link zum Profil; der eigene Nutzer wird hervorgehoben, unbekannte Nutzer erscheinen als '@suspended user'.",
  "A12#14 A10b#106")
F("PAGE", G, "Emojis", "",
  "':'-Suggestion (max. 5, Default-Liste beim Slash-Befehl 'Emoji'), :shortcode:-Ersetzung, Emoticons und automatische Umwandlung von Unicode-Emojis in Emoji-Nodes.",
  "A12#15")
F("PAGE", G, "Links im Editor", "",
  "Autolink beim Tippen, Link-Paste über eine Selektion, Hover-Vorschau (Copy/Edit/Unlink), Bearbeiten von URL und Text, Öffnen per Klick und Filter für gefährliche Protokolle.",
  "A12#16")
F("PAGE", G, "Markdown-Funktionen", "",
  "Markdown-Paste wird geparst; Kopieren liefert Markdown (text/plain) und HTML; 'Copy as Markdown' und Markdown-Export wandeln HTML in GitHub-Markdown um (inkl. Bildern, Mentions, Checklisten und Kursivschrift).",
  "A12#17 A13b#30")
F("PAGE", G, "Platzhalter", "",
  "Kontextabhängige Platzhalter: 'Heading N', Default \"Press '/' for commands...\", eigene Texte/Funktionen, nur bei leerem Dokument; Titel-Platzhalter 'Untitled'.",
  "A12#18")
F("PAGE", G, "Deep-Links zu Blöcken", "",
  "Scroll zu einem Block per URL-Hash (#nodeId); der Hash-Scroll-Hook scrollt nach 200 ms weich, auch bei mehreren IDs im Hash.",
  "A12#19 A13b#34")
F("PAGE", G, "Anzeige-Konfiguration des Editors", "",
  "Schriftart (Sans serif/Serif/Mono), Schriftgröße (small/large/mobile), Zeilenabstand und Wide Layout (720/1152 px) mit Container-Queries.",
  "A12#20")
