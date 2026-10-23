# 02 – Arbeitspakete der CE-Portierung (WP-<Inkrement>-<NNN>)

> **Stand:** 23.10.2026. **Verbindlichkeit:** bindend für alle Implementierungs-Agenten der CE-Phase (I0–I7). Rangfolge bei Widersprüchen: `architecture/00-grundsatzentscheidungen.md` > `architecture/17-abgleich-dokumentuebergreifend.md` (Entscheidungen des Auftraggebers, Umbenennungstabelle) > `architecture/01-zielarchitektur-und-tech-stack.md` > Themen-Dokumente 02–16 > dieses Dokument. Wo dieses Dokument eine Zuordnung bewusst anders trifft als ein Architektur-Dokument, steht die Begründung in `plan/04-risiken-offene-punkte.md` (Abschnitt „Planungsentscheidungen OP-PLAN-*“).
>
> **Erzeugt:** Abschnitte 3 und 4, die Anhänge und das angehängte Review-Protokoll (`02-review.md`) erzeugt `migration/_werkzeuge/plan/build.py` aus den Spezifikationsdateien `wp_spec.py`, `wp_spec_i1_i3.py`, `wp_spec_i4_i7.py`; die Vollständigkeit prüft `migration/_werkzeuge/plan/check_wp.py`. **Änderungen nur in den Spezifikationsdateien**, danach `python3 -I migration/_werkzeuge/plan/build.py && python3 -I migration/_werkzeuge/plan/check_wp.py`. Maschinenlesbar: `plan/_data/wp-ce.json` (Array `{wp, title, phase, ce_ids[], depends_on[], size}`) und `plan/_data/wp-endpoints.json` (registrierter Endpunkt → Arbeitspaket).
>
> **Namen:** Alle Zielbezeichner folgen ADR-009C (`Funk.*`, `FunkDbContext`, `Funk:`-Konfiguration, `X-Funk-*`, Realm `funk`, Clients `funk-*`, `@funk/*`). Wo die Architektur-Dokumente noch `Plane.*` schreiben, gilt die Umbenennungstabelle in 17. Pfade für Zielcode sind relativ zur Wurzel des Repositorys `funk.`; Original-Pfade beziehen sich auf `mlwr/plane@funk-referenz-1.4.2` (Commit `053b2c0`).

> **Prüfergebnis (`check_wp.py`, 23.10.2026, nach Review):** 180 Arbeitspakete (I0 38, I1 31, I2 35, I3 16, I4 13, I5 13, I6 22, I7 12); 507 von 507 CE-IDs genau einem Paket zugeordnet (27 davon „entfällt“ mit Ersatznachweis); alle Abhängigkeiten existieren, zeigen nicht in spätere Inkremente und bilden einen azyklischen Graphen; jedes Paket außer den Spikes liegt unter der Abnahme seines Inkrements; 11 Vorlauf-Pakete (§3.3) deckungsgleich mit `wp_spec.VORLAUF`; 564 registrierte Endpunkte genau einem Paket zugeordnet; jedes Paket hat mindestens ein paketspezifisches Akzeptanzkriterium. Review-Protokoll am Ende dieses Dokuments (Quelle `migration/_werkzeuge/plan/02-review.md`).

## 1. Lesehilfe

### 1.1 Nummernkreise

| Nummernkreis | Bedeutung | Typ (DoD 15 §3.15.3) | CE-IDs |
|---|---|---|---|
| `WP-In-001` … `WP-In-099` | fachliche Schnitte (vertikal: Endpunkte + Screens + Tests eines Feature-Clusters; Schnittregel 01 §1.3) | V, B, F, D | ja |
| `WP-In-101` … `WP-In-199` | Bausteine und Infrastruktur, die ein Inkrement braucht (Hosts, Plattform, Dokumente, Designsystem-Grundlagen, Betrieb) | I, B, D, F | teilweise (CE-OPS, CE-I18N) |
| `WP-In-201` … `WP-In-299` | **Erweiterungspunkte** für Bezahl-Pakete (P-Andockstellen aus 16 §1.4/§3.3.0) | X | nie |
| `WP-I0-900` … `WP-I0-913` | Spikes des Spike-Tracks (`WP-I0-9nn` = Spike S*nn*, `WP-I0-913` = Scope-FK-Spike) | S | nie |
| `WP-In-999` | Inkrement-Abnahme (Gate G5; für I7 zusätzlich G6) | A | nie |

### 1.2 Felder je Arbeitspaket

| Feld | Bedeutung |
|---|---|
| Inkrement | `I0` … `I7` (01 §1.3). Ein Paket darf nur von Paketen desselben oder eines früheren Inkrements abhängen (geprüft). |
| Typ | DoD-Typ aus 15 §3.15.3: **V** vertikaler Schnitt, **B** Backend-only, **F** Frontend-only, **I** Infrastruktur/Baustein, **D** Editor/Dokumente, **S** Spike, **X** Erweiterungspunkt 🧱; zusätzlich **A** Inkrement-Abnahme. |
| Größe | **S** ≤ 3 Agenten-Arbeitstage, **M** 3–7, **L** 7–12. Größer wird nicht geplant – ein Paket über 12 Tage wird geteilt (Änderungsverfahren §2.4). Für Schätzungen gilt S = 2, M = 5, L = 10 Tage (§3.2). |
| parallelisierbar | **ja**: kann gleichzeitig mit anderen Paketen desselben Inkrements laufen, sobald die Abhängigkeiten erfüllt sind. **nein**: legt gemeinsame Grundlagen (Basis-Store, gemeinsame Registry, zentrale Migration) oder liegt auf dem kritischen Pfad; es soll von genau einem Agenten ohne parallele Arbeit am selben Modul bearbeitet werden. |
| Abhängigkeiten | Pakete, die abgenommen (gemergt, G2 grün) sein müssen, bevor das Paket beginnt. Jedes Paket eines Inkrements `In` (n ≥ 1) hängt direkt oder transitiv an `WP-I(n-1)-999`, außer den ausdrücklich als **Vorlauf** markierten Paketen (Editor-Track ab I1, Dokument-/Realtime-Track ab I3; plan/01 L-8, Liste in §3.3, Merkmal „Vorlauf“ je Paket). |
| CE-IDs | Features aus `features/10-ce-feature-katalog.md`. **Jede der 507 CE-IDs gehört zu genau einem Arbeitspaket** (Anhang A, `check_wp.py`). CE-IDs mit Status „entfällt“ (27, ADR-008) liegen in dem Paket, das den Ersatznachweis führt (Titelzusatz „Nachweis entfallener …“). |
| Andockstelle | nur Typ X: Quelle in 01 §1.4 bzw. 16 §3.3.0 (E-Nummer) und die Träger-CE-IDs aus 16 §4.6. |
| Endpunkte | registrierte Endpunkte aus dem Katalog 04 (`architecture/_data/endpoints.json`). Jeder registrierte Endpunkt gehört zu genau einem Paket: dem Paket, das eine seiner CE-IDs enthält und im Inkrement des Katalogs liegt, sonst dem frühesten Paket mit einer seiner CE-IDs; „(vorab)“ = Endpunkt wird vor dem Paket seiner CE-ID gebraucht und in einem früheren Paket gebaut; das Paket der CE-ID erweitert ihn dann nur. „(verschoben)“ = Endpunkt kann erst später entstehen, weil seine Daten erst dann existieren (z. B. workspace-weite Cycle-/Modul-Listen in I3). Beide Fälle stehen in der Liste `EP_OVERRIDE` in `wp_spec.py`. |
| Referenzdokumente | „Architektur“ = von Hand gesetzte Abschnitte der Dokumente 00–17; „Analyse/Feature“ = automatisch aus dem Feld `doc` der enthaltenen CE-IDs übernommen. |
| Original-Pfade | automatisch aus `backend_refs`/`frontend_refs` der CE-IDs übernommen, ergänzt um von Hand gesetzte Pfade. |
| Akzeptanzkriterien | paketspezifische Kriterien, danach die Standardkriterien des Typs (15 §3.15.3) und der Abdeckungsnachweis `ce-coverage-check`. Der gemeinsame DoD-Kern aus 15 §3.15.3 und `plan/03-agenten-leitfaden.md` §8 gilt immer zusätzlich. |
| Testumfang | Pflicht-Ebenen, Testprojekte und E2E-Specs aus 15 Anhang B (automatisch) plus paketspezifische Tests. |

### 1.3 Ebenen und Gates (Kurzreferenz, Quelle 15 §3.1/§3.15)

L0 Statik · L1 Unit · L2 Frontend-Komponenten/Stores · L3 Modul-Integration (inkl. portierter Original-Tests) · L4 Golden-Files · L5 Contract-Parität (Parity-Harness) · L6 System (Aspire) · L7 E2E Dual-Target · L8 Visual/DOM/a11y (nur Chromium als Gate, 17 Z-10) · L9 Last/Soak. Gates: G0 lokal, G1 PR, G2 Merge-Queue (vor Merge in `develop`), G3 Golden-Änderung, G4 Nightly, G5 Inkrement-Abnahme, G6 Release.

## 2. Regeln für die Arbeit mit den Paketen

### 2.1 Zuordnungsregeln

1. **CE-ID → genau ein Paket.** Ein Paket kann mehrere CE-IDs enthalten; eine CE-ID wird nie geteilt. Wenn ein früheres Paket einen Teil einer CE-ID braucht (z. B. einen Endpunkt), baut es diesen Teil als „vorab“; die CE-ID wird erst im zugeordneten Paket abgenommen.
2. **Inkrement-Zuordnung.** Grundlage ist 01 §1.3 und die Inkrement-Spalte in 15 Anhang B; Abweichungen (Anhang B dieses Dokuments) sind in plan/04 OP-PLAN-03 begründet.
3. **Erweiterungspunkte bekommen eigene Pakete (Nummernkreis 2xx).** Abweichend von 16 §4.6 („im Arbeitspaket der Träger-CE-ID“) verlangt der Planungsauftrag eigene Pakete; das Träger-Paket hängt vom Erweiterungspunkt-Paket ab und nutzt die Andockstelle (plan/04 OP-PLAN-01). Die DoD Typ X wird im Erweiterungspunkt-Paket erfüllt; das Träger-Paket weist nach, dass es die Andockstelle verwendet (Review-Checkliste) – z. B. liest WP-I1-011 States ausschließlich über `IStateCatalog` aus WP-I1-201.
4. **Spikes** liefern dauerhafte Tests (DoD Typ S) und gaten nur die in 01 §9 Spalte „blockiert“ genannten Folgepakete; S0, S7, S10 (Shell-Teil) und S11 gaten die Abnahme von I0.
5. **Keine Platzhalter-Seiten** (01 §7.19): Ein Paket registriert seine Routen und Sidebar-Einträge erst, wenn sein Screen abgenommen ist.

### 2.2 Reihenfolge innerhalb eines Inkrements

Erweiterungspunkt-Pakete (2xx) und Bausteine (1xx) zuerst, weil fachliche Schnitte auf ihnen aufbauen; danach die Schnitte in der Reihenfolge des Abhängigkeitsgraphen (plan/01 §3). Pakete mit „parallelisierbar = ja“ werden auf mehrere Agenten verteilt. Der kritische Pfad je Inkrement steht in §3.2.

### 2.3 Wellen W1–W9 (Bezahl-Pakete)

Für die Wellen gibt es in dieser Phase **keine** Arbeitspakete. Sie stehen als grobe Blöcke in plan/01 §5 und werden erst kurz vor ihrer Umsetzung nach 16 §6 detailliert geplant (`migration/plan/waves/W<n>-<paket>.md`). Ihre Voraussetzungen im CE-Fundament sind die X-Pakete dieses Dokuments.

### 2.4 Änderungsverfahren

Ein Agent, der feststellt, dass ein Paket zu groß ist, eine Abhängigkeit fehlt oder eine CE-ID falsch zugeordnet ist, ändert **nicht** eigenmächtig den Plan im Repository `funk.`, sondern eröffnet eine Planfrage (plan/03 §10). Nach Freigabe werden die Spezifikationsdateien geändert, `build.py` und `check_wp.py` laufen, und `docs/plan/` in `funk.` wird aktualisiert.
