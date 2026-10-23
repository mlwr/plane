## Review-Protokoll

**Adversarialer Review vom 23.10.2026** über `plan/01`–`04` und `plan/_data/wp-ce.json`. Alle Korrekturen sind in den Spezifikationsdateien (`wp_spec*.py`), im Generator (`build.py`, `check_wp.py`) bzw. direkt in `plan/01`, `03`, `04` vorgenommen; dieses Dokument und `_data/*.json` sind danach neu erzeugt. Architektur-Dokumente wurden nicht geändert; ihr Nachpflegebedarf steht in plan/04 §6 (N-P13 … N-P16).

### Prüfmethode

| Nr. | Prüfung | Werkzeug / Quelle | Ergebnis vor Review | Ergebnis nach Review |
|---|---|---|---|---|
| P-1 | Jede CE-ID aus `features/_data/ce-features.json` genau einem Paket zugeordnet, keine unbekannten IDs | `check_wp.py` und unabhängiges Prüfskript gegen `ce-features.json` | 507/507, 0 doppelt, 0 unbekannt | unverändert 507/507 |
| P-2 | „entfällt“-IDs in Paketen mit Ersatznachweis; Status-Abgleich 00 ↔ 05 ↔ 15 | `15-ce-testmatrix.json`, 00 ADR-008, 05 Matrix CE-AUTH/PROF/INST/SPACE | 27 korrekt platziert; 2 Statuskonflikte zwischen den Architektur-Dokumenten | Konflikt dokumentiert (plan/04 N-P13), WP-I6-001 präzisiert |
| P-3 | Abhängigkeiten existent, nicht in spätere Inkremente, azyklisch | `check_wp.py`, DFS | grün | grün |
| P-4 | Jedes Paket unter der Abnahme seines Inkrements (außer Spikes) | neu in `check_wp.py` | grün | grün |
| P-5 | Meilenstein-Kette: jedes Paket in In (n ≥ 1) transitiv an `WP-I(n-1)-999`, außer Vorlauf | neu in `build.py`/`check_wp.py` | 12 Pakete ohne Kette, davon 3 fachlich falsch (WP-I4-005, WP-I4-007, Pages-Schema fehlte dem Vorlauf); Vorlauf nirgends markiert | 11 Vorlauf-Pakete, deklariert in `wp_spec.VORLAUF`, markiert in §3.3 und je Paket |
| P-6 | Spike-Gating nach 01 §9 Spalte „blockiert“ | Abgleich der direkten Nutzer je Spike | S11 (Paritäts-Harness) gatete keinen I0-Schnitt, Scope-FK-Spike gatete nicht die erste Tabelle mit Scope-FK (WP-I0-005) | ergänzt (R-01, R-02) |
| P-7 | Alle P-Andockstellen aus 16 §1.4, §3.3.0 (E-01 … E-26) und §4.6 in X-Paketen | Bezeichner-Abgleich (147 Contracts/Tokens/Tabellen) | 2 Bezeichner fehlten namentlich (`IProjectFeatureContributor`, `IWorkspaceFeatureContributor`), `FILTER_INPUT_MODES` (16 §5.5, AK-16-16) fehlte | ergänzt (WP-I1-202, WP-I2-201) |
| P-8 | Träger-Pakete (16 §4.6) hängen vom X-Paket ab (02 §2.1 Nr. 3) | Prüfskript über die Träger-CE-IDs je X-Paket | 4 fachliche Lücken (WP-I6-014, WP-I6-004, WP-I4-006, WP-I4-202) | ergänzt; verbleibende Treffer sind nominelle Träger aus dem Fundament (siehe „Bewusst nicht geändert“) |
| P-9 | Test-Inventar 16 §7.2 und AK-16-01 … AK-16-17 in den X-Paketen | Abgleich Testklassen/AK-IDs | 40 von 45 Testklassen aus 16 §7.2 und alle 17 AK-16-IDs in keinem Paket genannt | in die X-Pakete übernommen (Namen nach ADR-009C) |
| P-10 | Messbare Akzeptanzkriterien | Paketliste ohne paketspezifische AK; Suche nach vagen Begriffen („korrekt“, „funktioniert“, „performant“ …) | 62 Pakete nur mit Standardkriterien; 3 vage Kriterien in Spikes | jedes Paket ≥ 1 paketspezifisches, prüfbares Kriterium (Golden, Zählung, Schwellwert, Testname); vage Kriterien präzisiert |
| P-11 | Namen nach ADR-009C / Umbenennungstabelle 17 | Suche nach `Plane.`, `Plane:`, `X-Plane-`, `plane_*`, `@plane/` in generierten Texten | 4 × `Plane:OpenApi:Enabled` (Permission-Spalte aus `endpoints.json` nicht umbenannt) | `rename()` erweitert (`Plane:`, `Plane__`) und auf die Permission-Spalte angewandt |
| P-12 | Querverweise zwischen den Plan-Dokumenten | Abgleich `plan/0x §n` mit den Überschriften | 3 falsche Ziele (`plan/03 §9` statt §10 Eskalation, zweimal; `plan/03 §7` statt §8 DoD) | korrigiert |
| P-13 | Kennzahlen in plan/01 gegen 02 §3.2 | Neuberechnung kritischer Pfade inkl. „ab Meilenstein“ | „37 nach Vorlauf“ (I2, tatsächlich 42), „22 nach Vorlauf“ (I4, tatsächlich 29), I7 12 Tage | nach Korrekturen: I2 62/42, I4 44/37, I6 39, I7 22 Tage; Gantt angepasst |

### Korrekturen

| Nr. | Fundstelle | Befund | Korrektur |
|---|---|---|---|
| R-01 | WP-I0-001, WP-I0-006, WP-I0-109 | Erste V/F-Pakete ohne Abhängigkeit auf CI/Gates (WP-I0-106) bzw. Paritäts-Harness (WP-I0-911), obwohl ihre DoD „G2 grün“ und Contract-Replay/Visual gegen das Original verlangt (01 §9 S11: „Definition of Done aller WPs“). | `WP-I0-106` (alle drei) und `WP-I0-911` (WP-I0-001, WP-I0-109) als Abhängigkeit; kritischer Pfad I0 unverändert 49 Tage. |
| R-02 | WP-I0-005 | Projektanlage legt `states`/`project_members` an, die nach 03 D03-ADR-05 bereits in I0 den zusammengesetzten Scope-FK tragen; der Scope-FK-Spike (WP-I0-913) gatete nur I1-Pakete. | Abhängigkeit `WP-I0-913`, AK zum Scope-FK. |
| R-03 | WP-I4-201, WP-I4-202, WP-I4-006 | Der Vorlauf-Kollaborationsserver (ab M2) speichert in `pages` und prüft Page-Zugriff je Verbindung (17 ABG-107), Schema und Zugriffsregel entstanden aber erst nach M3 (WP-I4-201 bzw. WP-I4-002). | WP-I4-201 wird Vorlauf-Paket (Abhängigkeit M2) und baut die zentrale Prüfstelle `IPageAccessPolicy` (05 §3.13.5); WP-I4-202 und WP-I4-006 hängen von WP-I4-201 ab (plan/04 OP-PLAN-13). |
| R-04 | WP-I4-007 | Lief als Vorlauf, nutzt aber den REST-Fallback `…/pages/{id}/description/` aus WP-I4-002. | Abhängigkeit `WP-I4-002`, Hinweis „kein Vorlauf-Paket“; kritischer Pfad I4 ab M3 37 Tage (plan/04 R-P31). |
| R-05 | WP-I4-005, WP-I4-004 | Versionshistorie (Typ V mit App-Endpunkten) hing nur am Vorlauf-Server und nicht an der Page-Verwaltung; das Info-Panel (WP-I4-004) zeigt die Versionsliste ohne Abhängigkeit. | WP-I4-005 → WP-I4-002; WP-I4-004 → WP-I4-005. |
| R-06 | WP-I4-002 | Duplizieren erzeugt JSON/Binary (CE-PAGE-009) ohne Abhängigkeit auf Funk.Documents Teil B. | Abhängigkeit `WP-I4-101`; AK „in-process, kein Live-Server-Aufruf“. |
| R-07 | WP-I2-004 | Sidebar-Properties der Detailseite ohne Abhängigkeit auf die Detailseite. | Abhängigkeit `WP-I2-002`. |
| R-08 | WP-I6-014, WP-I6-004 | Träger-CE-IDs (CE-WH-002/-003 Ereignisauswahl; CE-SPACE-001) ohne Abhängigkeit auf ihr X-Paket (WP-I6-202 bzw. WP-I6-203), entgegen 02 §2.1 Nr. 3. | Abhängigkeiten ergänzt; I6 kritischer Pfad 39 Tage. |
| R-09 | WP-I6-018 | KI-Assistent ohne Abhängigkeit auf die AI-Einstellungen (`has_llm_configured`, WP-I6-002). | Abhängigkeit `WP-I6-002`. |
| R-10 | WP-I7-107, WP-I7-201 | Airgap-Bundle enthält Compose, AIO-Compose, Helm-Chart, `funk-cli` und ACME-Profil (14 §3.14.1), hing aber nur an M6; der Airgap-Lauf mit Forgejo (WP-I7-201) hing nicht am Bundle. | WP-I7-107 → WP-I7-101, -102, -103, -105, -106; WP-I7-201 → WP-I7-107; I7 kritischer Pfad 22 Tage. |
| R-11 | 62 Pakete (u. a. alle I3-Schnitte, Public API v1, God Mode, Space, WP-I7-103/-104/-105/-109/-110) | Nur Standardkriterien des Typs; keine paketspezifischen Prüfpunkte (z. B. Lastziele LT-08/-13/-21 in WP-I7-109, Start-Abbruchregeln in WP-I7-103). | Paketspezifische AK mit Golden-, Zähl-, Zeit- oder Testnachweis ergänzt; Quelle je Kriterium aus CE-Katalog, 05, 07, 14, 15, 16. |
| R-12 | X-Pakete | Testinventar 16 §7.2 und AK-16-01 … -17 nicht zugeordnet; `assert-no-package-code`, `ReservedContractFieldsTests`, `e2e/web/extensions.spec.ts` ohne Paket. | Je X-Paket Testklassen und AK-16-Nachweise ergänzt; Querschnitt in WP-I0-208, AK-16-02 als Zwischenstand in WP-I2-999/WP-I4-999 und final in WP-I7-201. |
| R-13 | WP-I1-202, WP-I2-201 | E-26-Contributors nicht namentlich; Token `FILTER_INPUT_MODES` fehlte. | Titel/AK WP-I1-202 (AK-16-10), Lib und AK in WP-I2-201. |
| R-14 | WP-I1-205 | E-12 (`IInstanceConfigKeyProvider`) entsteht in I1, die 14 Instanz-Schlüssel aber schon in I0 (WP-I0-003) – Umbau der I0-Lösung war nicht beschrieben. | AK: Überführung in `CoreInstanceConfigKeyProvider`, Golden unverändert (plan/04 N-P14). |
| R-15 | WP-I6-001 | Paket nannte „Unsaved-Dialog“, aber nicht die Ersatzseite „Authentication“ (Keycloak-Karte, `ENABLE_SIGNUP`, Kopierfelder CE-INST-015; 05 §4.4, 08 §4.2 R6); 05 und 00/08/15 widersprechen sich im Status von CE-INST-014/-020. | Titel und AK präzisiert; Konflikt in plan/04 N-P13. |
| R-16 | `build.py` | `Plane:OpenApi:Enabled` in vier Endpunktzeilen (Permission-Spalte). | `rename()` deckt `Plane.`, `Plane:`, `Plane__` ab und wirkt auch auf die Permission-Spalte. |
| R-17 | `build.py`, `check_wp.py`, 02 §1.2/§3 | Vorlauf-Pakete nirgends gekennzeichnet (plan/03 §3 verlangte „gekennzeichnet“); keine Prüfung, dass nur gewollte Pakete den Meilenstein überspringen. | `wp_spec.VORLAUF`, Abbruch bei Abweichung oder Typ V/F/A, Merkmal „Vorlauf“ je Paket, Liste §3.3, Spalte „ab Meilenstein“ in §3.2, Abnahme-Vollständigkeit in `check_wp.py`. |
| R-18 | 02 §1.2, §2.4; plan/01 §7.3 | Verweise `plan/03 §9` (Eskalation steht in §10) und `plan/03 … §7` (DoD steht in §8). | korrigiert. |
| R-19 | WP-I0-901, WP-I0-902, WP-I0-903 | „funktioniert“, „korrekt gelesen“, „korrekt“. | messbar umformuliert (Wiederholungen ohne Fehlschlag, JSON ohne Diff, Glyphen + identischer Text). |

### Bewusst nicht geändert

| Punkt | Begründung |
|---|---|
| Nominelle Träger aus dem Fundament: CE-OPS-021/-022 (WP-I0-102, WP-I0-106) für WP-I0-201/-205/-208, CE-OPS-023 (WP-I0-106) für WP-I7-201, CE-INST-002/-003 (WP-I0-003) für WP-I1-205/WP-I6-203 | Die Andockstellen bauen auf diesen Fundament-Paketen auf (umgekehrte Richtung wäre ein Zyklus bzw. eine Abhängigkeit auf ein späteres Inkrement); 16 §4.6 nennt sie als „Walking-Skeleton-Gerüst“. Die Nutzung ist über WP-I1-205 (R-14) bzw. die Abnahmen abgesichert. |
| Spikes WP-I0-901 … -906, -908, -909, -912, -913 nicht unter WP-I0-999 | 01 §9: sie gaten erst das Inkrement in Spalte „blockiert“; `check_wp.py` nimmt Spikes von der Abnahme-Prüfung aus, die Folgepakete hängen direkt am Spike. |
| Plan-eigene Messgrößen ohne Vorgabe in den Architektur-Dokumenten | z. B. „< 200 Zeilen-Elemente bei 1 000 Items“ (WP-I2-014), „Zertifikatswechsel < 10 s“ (WP-I7-105), Korpusgrößen (20 Farbpaare, 5 Referenzdokumente, 10 Referenz-Seiten). Sie machen die Kriterien prüfbar; Änderungen nur über Planfrage (plan/03 §10). |
| Statuskonflikt CE-INST-014/-020 | Rangfolge 00 > 05: CE-INST-020 bleibt „entfällt“ (00 ADR-008), CE-INST-014 bleibt umgesetzt (08, 15). Die Zuordnung in diesem Plan ändert sich nicht; 05 ist nachzupflegen (plan/04 N-P13). |
