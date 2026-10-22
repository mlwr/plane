export const meta = {
  name: 'plane-analyse-abschluss',
  description: 'Abschluss der IST-Analyse: fehlende Frontend-Analysen 10a/10b, Vervollständigung Paid-Dokument 23, Verifikation der Paid-Dokumente, CE-Feature-Katalog und Paid-Matrix',
  phases: [
    { title: 'Code-Lücken', detail: 'Analysen 10a und 10b (ohne Critic-Stufe, sparsamer Plan)' },
    { title: 'Paid-Abschluss', detail: 'Dokument 23 vervollständigen, dann alle ungeprüften Paid-Dokumente verifizieren' },
    { title: 'Synthese', detail: 'CE-Feature-Katalog + exakte Paid-Feature-Matrix' },
  ],
}

// Aufruf (args.part): 'code' | 'paid' | 'synth'. 'code' und 'paid' dürfen parallel laufen, 'synth' erst danach.

const REPO = '/home/user/plane'
const MIG = REPO + '/migration'
const OUT_A = MIG + '/analysis'
const OUT_F = MIG + '/features'
const DATA_A = OUT_A + '/_data'
const DATA_F = OUT_F + '/_data'
const DEVDOCS = '/home/user/makeplane/developer-docs'
const HELM = '/home/user/makeplane/helm-charts'
const A = args || {}

const CONTEXT = `
KONTEXT: Das Repo ${REPO} ist Plane v1.4.2 Community Edition (AGPL-3.0): Django/DRF-API (apps/api), React-Router-SPA "web" (apps/web), God-Mode "admin" (apps/admin), öffentliche Boards "space" (apps/space), Hocuspocus/Yjs-Realtime-Server "live" (apps/live), pnpm/turbo-Monorepo mit packages/*. Primitive UI-Komponenten kommen aus dem npm-Paket @makeplane/propel 0.7.3.
ZIEL DES GESAMTPROJEKTS: Vollständige Überführung ALLER Features (Community + Bezahl-Editionen Pro/Business/Enterprise) in eine .NET-Architektur (.NET Aspire, Entity Framework Core, PostgreSQL inkl. pgvector) mit Angular-Frontend. Die UI muss 1:1 wie das Original aussehen. Implementierungs-Agenten arbeiten später AUSSCHLIESSLICH auf Basis dieser Dokumente + des Original-Repos — präzise und vollständig (Dateipfade, Feldnamen, Endpunkte, Verhalten, Edge-Cases, Berechtigungen, Seiteneffekte).
FESTE ENTSCHEIDUNGEN (${MIG}/architecture/00-grundsatzentscheidungen.md): keine Plan-Stufen (eine Edition, alle Features aktiv, Upsell/Billing entfällt); Realtime in reinem .NET (YDotNet); Greenfield; Self-hosted inkl. Airgapped.
DIESE PHASE: reine IST-Analyse. Ändere KEINE Dateien außerhalb von ${MIG}/. Kein git commit/push. Keine Installationen, keine Server starten.
SPRACHE: Deutsch für Fließtext; Code-Bezeichner, Pfade, Feldnamen, Endpunkte im Original. Markdown mit Tabellen. Jede Aussage mit Quellpfad belegen.
QUALITÄT: Vollständige Inventare statt Beispiele ("u. a.", "etc." verboten). Lies die Dateien wirklich. Schreibe große Dokumente in mehreren Schritten (Write, dann Edit/Append).
VORHANDENE ANALYSEN (Stil- und Strukturvorbild, Querverweise): ${OUT_A}/*.md, ${OUT_F}/*.md.`

const WEB_NOTE = `
RECHERCHE: docs.plane.so und plane.so sind per Netzwerk-Policy NICHT direkt abrufbar. WebSearch (via ToolSearch "select:WebSearch") liefert Seitenzusammenfassungen — das Kontingent ist für alle Agenten gemeinsam begrenzt: höchstens 15 Suchen in deinem Lauf, gezielt einsetzen. Offline: Developer-Docs ${DEVDOCS}/docs, Helm-Charts ${HELM}/charts/plane-enterprise, im Repo apps/web/components/workspace/billing/comparison/plans.tsx und packages/i18n/src/locales/en/*.json. Zitiere jede Quelle. Unsicheres als "UNVERIFIZIERT" markieren. Nichts erfinden.`

const CODE_AREAS = [
  {
    key: 'A10a', file: '10a-frontend-workspace-projekt-navigation.md',
    scope: `Frontend Teil: apps/web/components/{workspace,project,projects,settings,profile,account,onboarding,navigation,sidebar,core,common,home,stickies,workspace-notifications,power-k,license,empty-state,ui,icons,appearance,user,instance,auth-screens,global,modals,breadcrumbs,browse,archives}/ (alles, was davon existiert). Dokumentiere JEDEN Screen/Dialog/Panel: Workspace-Sidebar (Struktur, Menüeinträge, Favoriten, Projekte-Liste, Erweiterung/Collapse, Workspace-Switcher), Header/Breadcrumbs, Home/Dashboard-Widgets (Recents, Quick Links, Stickies), Workspace-Einstellungen (alle Tabs), Projekt-Einstellungen (alle Tabs, Features-Toggles), Profil/Account-Einstellungen (alle Tabs: Profil, Security, Preferences, Notifications, API-Tokens, Appearance/Themes), Onboarding-Flow (alle Schritte), Auth-Screens (Sign-in/Sign-up/Magic-Code/Passwort/Reset), Power-K Command Palette (alle Befehle/Kontexte/Shortcuts), Notifications-Inbox, Upgrade-/Lizenz-Komponenten (Upgrade-Badges, Upgrade-Modal), Empty-States. Pfade + Interaktionsdetails für 1:1-Nachbau.`,
  },
  {
    key: 'A10b', file: '10b-frontend-cycles-modules-pages-views-weitere.md',
    scope: `Frontend Teil: apps/web/components/{cycles,modules,pages,views,analytics,inbox,estimates,labels,project-states,web-hooks,api-token,exporter,automation,integration,active-cycles,chart,editor,workflow}/ (alles, was existiert). Dokumentiere JEDEN Screen/Dialog: Cycles (Liste, aktive/kommende/abgeschlossene, Detail, Burndown/Progress-Charts, Transfer-Dialog, Archiv), Modules (Liste/Gallery, Detail, Status, Links, Leads/Members, Progress), Pages (Liste, Editor-Seite, Toolbar, Info-Panel/Outline, Versionen-Historie, Lock/Archive/Access, Export), Views (Projekt- und globale Workspace-Views, Speichern/Filter), Analytics (alle Tabs/Charts), Intake/Inbox (Liste, Detail, Accept/Decline/Snooze/Duplicate), Estimates (Systeme Points/Categories/Time, Erstellung), Labels (Hierarchie, Farben), States (Gruppen, Reihenfolge), Webhooks-/API-Token-Verwaltung, Exporter, Automation (Auto-Archive/Auto-Close), Integrationen (GitHub/Slack-Stubs), Charts (recharts-Wrapper), Editor-Wrapper. Pfade + Interaktionsdetails für 1:1-Nachbau.`,
  },
]

const P04_SCOPE = `Bezahl-Features Cluster "Work Management": Work Item Types, Custom Properties (alle Property-Typen inkl. Formula, Release-Picker, Relation, URL, Member, Dropdown, Boolean, Date, Number, Text; Pflichtfelder; Workspace-Level vs Projekt-Level; Roll-ups), Epics, Initiatives, Milestones, Releases, Customers, Recurring Work Items, Work Item Templates, Bulk Ops, Work Item Transfers/Conversions, Dependencies in Gantt, Auto-transfer Cycle Work Items, Module Overview, Auto-Assignment in Modules, Time Tracking + Worklogs + Timesheets + Approvals, Advanced Estimates, Public/Private/Secret Projects, State of Projects/Project Overview/Project Updates, Project Templates, Baselines & Deviations, Custom SLAs, Intake Forms, Intake Assignees, Emails for Intake, Duplicate Detection.`

const PAID_DOCS = {
  P01: { file: '20-paid-spuren-im-repo.md', topic: 'Spuren der Bezahl-Features im CE-Repo (Plan-Matrix plans.tsx, Upsell-Stellen, CE-Stubs, EE-i18n, EE-Typen, Backend-Spuren)' },
  P02: { file: '21-paid-api-referenz-developer-docs.md', topic: 'Öffentliche API-Referenz der Commercial Edition (developer-docs/api-reference) vs. CE-Public-API' },
  P03: { file: '22-paid-architektur-selfhosting-dienste.md', topic: 'Dienst-Architektur der Commercial Edition (Helm-Chart plane-enterprise, Self-Hosting-Doku, Dev-Tools)' },
  P04: { file: '23-paid-work-management.md', topic: P04_SCOPE },
  P05: { file: '24-paid-planung-insights-teams.md', topic: 'Planung, Insights, Teams (Teamspaces, Dashboards, Reports, Active Cycles, Views, PQL, Advanced Search, Scheduled Comms, Activity Logs)' },
  P07: { file: '26-paid-wissen-pages-wiki.md', topic: 'Wissensmanagement (Wiki, Nested Pages, Versionen, Collab, Publish, Exporte, Templates, Embeds, Kommentare, Sharing, Databases, Draw.io, Iframely)' },
  P08: { file: '27-paid-sicherheit-admin-lizenz.md', topic: 'Sicherheit, Administration, Lizenz (SSO SAML/OIDC/LDAP, IdP Group Sync, 2FA/Passkeys, Password Policy, Domains, RBAC/GAC, Guests, Approvals, Admin Interface, Audit/Activity Logs, Seats/Lizenz)' },
  P09: { file: '28-paid-integrationen-importer-ai.md', topic: 'Integrationen, Importer, AI, Plattform (GitHub, GitLab, Slack, Sentry, Zapier, Zendesk, Freshdesk, Importer, Plane AI/Pi, MCP, Agents, Runner, OAuth-Apps)' },
}

const CODE_SCHEMA = {
  type: 'object',
  properties: {
    doc_path: { type: 'string' },
    summary: { type: 'string', description: 'max. 15 Zeilen, deutsch' },
    key_facts: { type: 'array', items: { type: 'string' } },
    features: {
      type: 'array',
      items: {
        type: 'object',
        properties: { name: { type: 'string' }, area: { type: 'string' }, description: { type: 'string' }, code_refs: { type: 'array', items: { type: 'string' } } },
        required: ['name', 'area', 'description', 'code_refs'],
      },
    },
    migration_risks: { type: 'array', items: { type: 'string' } },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['doc_path', 'summary', 'key_facts', 'features', 'migration_risks', 'open_questions'],
}

const SMALL_SCHEMA = {
  type: 'object',
  properties: {
    doc_path: { type: 'string' },
    summary: { type: 'string' },
    changes: { type: 'array', items: { type: 'string' } },
    unverified_claims: { type: 'array', items: { type: 'string' } },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['doc_path', 'summary', 'changes', 'unverified_claims', 'open_questions'],
}

const PAID_JSON_SHAPE = `JSON-Array von Objekten {name, cluster, tier, tier_details, ce_status, description, data_model_hints, api_hints, ui_hints, sources[], confidence ("hoch"|"mittel"|"niedrig")}; tier = niedrigster Plan, ab dem verfügbar (Pro | Business | Enterprise | Enterprise Grid | One | Cloud-only | unklar); ce_status = fehlt | Stub/UI-Hülle im CE | teilweise im CE | im CE vorhanden (nur Cloud-Gating)`

// ---------------------------------------------------------------- part: code
if (A.part === 'code') {
  phase('Code-Lücken')
  const res = await parallel(CODE_AREAS.map((a) => () => agent(`${CONTEXT}
DEIN BEREICH (${a.key}): ${a.scope}

AUFGABE: Analysiere diesen Bereich erschöpfend und schreibe das Ergebnis nach ${OUT_A}/${a.file}. Struktur: 1. Überblick & Verantwortlichkeiten, 2. Vollständige Inventare (Tabellen), 3. Verhalten/Logik/Abläufe im Detail (inkl. Edge-Cases), 4. Abhängigkeiten zu anderen Bereichen (verweise auf die vorhandenen Analysen 08, 09, 11, 12, 13a, 13b statt sie zu wiederholen), 5. Migrationshinweise für Angular (1:1-Übertragbares, Neubau, Fallstricke), 6. Offene Punkte.
ZUSÄTZLICH: Schreibe die vollständige Feature-Liste (alle nutzersichtbaren Funktionen) als JSON-Array von Objekten {name, area, description, code_refs[]} nach ${DATA_A}/${a.key}.features.json.
RÜCKGABE: strukturierte Zusammenfassung gemäß Schema.`, { label: `analyse:${a.key}`, phase: 'Code-Lücken', schema: CODE_SCHEMA })))
  return { code: res.filter(Boolean).map((r) => ({ doc: r.doc_path, summary: r.summary, n_features: r.features.length, risks: r.migration_risks, open: r.open_questions })) }
}

// ---------------------------------------------------------------- part: paid
if (A.part === 'paid') {
  const keys = A.keys || ['P04', 'P01', 'P02', 'P03', 'P05', 'P07', 'P08', 'P09']
  const verify = (k) => agent(`${CONTEXT}
Du bist Skeptiker/Verifizierer für ${OUT_F}/${PAID_DOCS[k].file} (Cluster ${k}: ${PAID_DOCS[k].topic}).
${WEB_NOTE}
Die Autoren-Ergebnisse (Zusammenfassung + Feature-Liste) stehen in ${DATA_F}/${k}.author.json.
Prüfe adversarial: (a) Ist jede Tier-Zuordnung durch eine Quelle belegt? Gleiche gegen ${REPO}/apps/web/components/workspace/billing/comparison/plans.tsx und die Schwester-Dokumente ${OUT_F}/20-*.md bis 28-*.md ab; bei Widerspruch gewinnt die aktuellere/spezifischere Quelle, Widerspruch dokumentieren. (b) Stimmt der CE-Status (grep im Repo ${REPO})? (c) Fehlen Features des Clusters? (d) Sind Beschreibungen erfunden/übertrieben? Korrigiere das Dokument DIREKT (Edit) und hänge "## Verifikations-Protokoll" an.
ZUSÄTZLICH: Schreibe die FINALE, verifizierte Feature-Liste (Autoren-Liste mit Korrekturen + Ergänzungen, dedupliziert) nach ${DATA_F}/${k}.paid.json als ${PAID_JSON_SHAPE}.
RÜCKGABE gemäß Schema (changes = Korrekturen).`, { label: `verify:${k}`, phase: 'Paid-Abschluss', schema: SMALL_SCHEMA })

  phase('Paid-Abschluss')
  const out = await pipeline(
    keys,
    (k) => k !== 'P04' ? Promise.resolve({ skipped: true }) : agent(`${CONTEXT}
Das Dokument ${OUT_F}/23-paid-work-management.md (Cluster P04: ${P04_SCOPE}) wurde durch einen Abbruch UNVOLLSTÄNDIG geschrieben: Abschnitt 3 (Feature-Abschnitte) endet vorzeitig, Abschnitt 4 (Offene Punkte) fehlt.
${WEB_NOTE}
AUFGABE: Lies das Dokument vollständig. Ermittle, welche Features aus der Feature-Tabelle (Abschnitt 2) bzw. aus dem Cluster-Scope noch keinen eigenen Abschnitt in Abschnitt 3 haben, und ergänze diese im selben Format (Funktionsbeschreibung, Plan-Tier mit Quelle, CE-Status per grep geprüft, Datenmodell-, API-, UI-Hinweise, Quellen, Konfidenz). Ergänze Abschnitt "## 4. Offene Punkte / Unklarheiten". Nutze die Schwester-Dokumente ${OUT_F}/20-*.md, 21-*.md (API-Referenz: Customers, Epics, Initiatives, Milestones, Worklogs, Work-Item-Types) und 25-*.md, um Doppelungen zu vermeiden und konsistent zu bleiben.
ZUSÄTZLICH: Schreibe die vollständige Feature-Liste des Clusters nach ${DATA_F}/P04.author.json als Objekt {doc_path, summary, paid_features: ${PAID_JSON_SHAPE}, open_questions[]}.
RÜCKGABE gemäß Schema (changes = ergänzte Abschnitte).`, { label: 'vervollstaendigen:P04', phase: 'Paid-Abschluss', schema: SMALL_SCHEMA }),
    (prev, k) => verify(k).then((v) => ({ key: k, completion: prev && !prev.skipped ? prev : null, verify: v })),
  )
  return { paid: out.filter(Boolean).map((r) => ({ key: r.key, completion: r.completion ? r.completion.changes : null, changes: r.verify ? r.verify.changes : null, unverified: r.verify ? r.verify.unverified_claims : null, open: r.verify ? r.verify.open_questions : null })) }
}

// ---------------------------------------------------------------- part: synth
if (A.part === 'synth') {
  phase('Synthese')
  const SYN_SCHEMA = {
    type: 'object',
    properties: { doc_path: { type: 'string' }, summary: { type: 'string' }, counts: { type: 'string' }, notes: { type: 'array', items: { type: 'string' } } },
    required: ['doc_path', 'summary', 'counts', 'notes'],
  }
  const [ceCat, paidMatrix] = await parallel([
    () => agent(`${CONTEXT}
Erstelle den VOLLSTÄNDIGEN Feature-Katalog der Community Edition als ${OUT_F}/10-ce-feature-katalog.md.
Eingabe: Feature-Listen der Bereichsanalysen ${DATA_A}/*.features.json (alle lesen; Dubletten möglich). Für den Bereich 13a (Designsystem) existiert KEINE JSON-Datei: lies dafür ${OUT_A}/13a-designsystem-ui-tokens.md (Abschnitte 1–2 genügen) und leite die nutzersichtbaren Funktionen (Theming, Themes, Fonts, Icons, Komponenten-Varianten) selbst ab; schreibe sie zusätzlich nach ${DATA_A}/A13a.features.json. Detail-Dokumente ${OUT_A}/*.md nur gezielt nachlesen (sie sind sehr groß).
Anforderungen: Dedupliziere, gruppiere nach fachlicher Domäne (Workspace & Mitglieder, Projekte, Work Items, Layouts & Views, Cycles, Modules, Intake, Pages & Editor, Realtime, Analytics, Home/Stickies, Notifications, Suche/Power-K, Einstellungen/Profil, Auth, Instanz/God-Mode, Public Space, Public API v1, Webhooks/API-Tokens, Export, Integrationen/AI, i18n/Theming). Vergib jedem Feature eine stabile ID (CE-<DOMÄNE>-<NNN>), Kurzbeschreibung, Backend-Refs, Frontend-Refs, Verweis aufs Analyse-Dokument. Schreibe zusätzlich ${DATA_F}/ce-features.json (Array {id, domain, name, description, backend_refs[], frontend_refs[], doc}). Am Ende Statistik je Domäne.`, { label: 'synthese:ce-katalog', phase: 'Synthese', schema: SYN_SCHEMA }),
    () => agent(`${CONTEXT}
Erstelle die EXAKTE Bezahl-Feature-Matrix als ${OUT_F}/29-paid-feature-matrix.md — die zentrale Antwort auf die Frage des Auftraggebers: "Welche Features sind NICHT in der Open-Source Community Edition, sondern in den Bezahl-Editionen bis zur Top-Lizenz?"
Eingabe: verifizierte Feature-Listen ${DATA_F}/*.paid.json (alle lesen; Dubletten/Widersprüche möglich; falls für einen Cluster nur ${DATA_F}/<key>.author.json existiert, diese verwenden und als unverifiziert markieren). Detail-Dokumente: ${OUT_F}/20-*.md bis 28-*.md (gezielt nachlesen). Offizielle In-Repo-Matrix: ${REPO}/apps/web/components/workspace/billing/comparison/plans.tsx.
Anforderungen: (1) Editionsmodell (Community Edition vs. Commercial Edition mit Plänen Free/Pro/Business/Enterprise (+ ggf. Enterprise Grid, Airgapped), Cloud vs. Self-hosted, Plan "One" als Legacy) mit Quellen. (2) Dedupliziere und löse Widersprüche (dokumentieren). (3) Haupttabelle: ID (EE-<CLUSTER>-<NNN>) | Feature | ab Plan | Pro | Business | Enterprise | CE-Status | Konfidenz | Detail-Dok. (4) Separate Listen "Nur in Enterprise (Top-Lizenz), nicht in Business", "ab Business, nicht in Pro", "ab Pro". (5) Liste "Im CE-Code vorhanden, aber in Cloud-Free eingeschränkt" (z. B. Realtime-Collab, Publish — gegen Code prüfen). (6) Liste "coming soon / nicht verifizierbar". (7) Gesamtzahlen. Schreibe zusätzlich ${DATA_F}/paid-features.json (Array {id, cluster, name, min_plan, pro, business, enterprise, ce_status, confidence, doc}). Hinweis: Laut Auftraggeber werden in der Zielplattform ALLE Features ohne Plan-Stufen umgesetzt — die Matrix dient der exakten Bestandsaufnahme.`, { label: 'synthese:paid-matrix', phase: 'Synthese', schema: SYN_SCHEMA }),
  ])
  return { ceCat, paidMatrix }
}

return { error: 'unknown part', args: A }
