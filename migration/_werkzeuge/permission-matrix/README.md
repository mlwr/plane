# Permission-Matrix-Generator (D05)

Erzeugt aus dem Original-Code (`apps/api/plane/**`) die Endpunkt-×-Rollen-Matrix und den Permission-Katalog für
`migration/architecture/05-auth-sicherheit-berechtigungen.md` (Anhang A/B) und `migration/architecture/_data/05-permission-matrix.json`.

```bash
cd apps/api/plane
python3 -I ../../../migration/_werkzeuge/permission-matrix/extract.py . /tmp/pm/out.json     # URL-Routen + Views + Decorators (AST)
python3 -I ../../../migration/_werkzeuge/permission-matrix/stage2.py /tmp/pm/out.json /tmp/pm/rows.json   # Original-Prüfung je Methode
python3 -I ../../../migration/_werkzeuge/permission-matrix/stage3.py /tmp/pm/rows.json /tmp/pm/final.json # Ziel-Key + Ziel-Prüfung + Abweichungs-IDs
python3 -I ../../../migration/_werkzeuge/permission-matrix/gen_md.py /tmp/pm/final.json /tmp/pm/catalog.md /tmp/pm/endpoints.md /tmp/pm/matrix.json
```

Die Overrides (Sicherheitskorrekturen `SEC-xx`, Harmonisierungen `HARM-xx`, Wegfall `ADR-008`) stehen in `stage3.py` (Dict `T`) und sind in D05 §3.18 begründet.

Anhang A/B von D05 direkt aus der (ggf. manuell gepflegten) Datendatei erzeugen:

```bash
python3 -I migration/_werkzeuge/permission-matrix/gen_appendix.py migration/architecture/_data/05-permission-matrix.json /tmp/pm/appendix.md
# danach in 05-auth-sicherheit-berechtigungen.md den Block ab "## Anhang A" durch /tmp/pm/appendix.md ersetzen
```
