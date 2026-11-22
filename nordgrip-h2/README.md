# NORDGRIP H2 – AutoLevel

Självbalanserande ölhölster för bälte: passivt gravitationsstabiliserad tvåaxlig gimbal, utan elektronik.

- `cad/nordgrip_h2.py` – parametrisk CadQuery-modell. `pip install cadquery && python3 nordgrip_h2.py out`
- `cad/out/print/` – STL och STEP per del, orienterade för stödfri utskrift (Bambu Lab A1, PETG)
- `cad/out/nordgrip_h2_assembly.step` – hela sammanställningen
- `cad/out/analysis.json` – massa, tyngdpunkt och egenfrekvens per lastfall
- `presentation/` – produktpresentation med fyra vyer (hero, AutoLevel 45°, exploderad, snitt)

Status: konceptprototyp rev A. Geometrin är kontrollerad i CAD men inte utskriven eller provad.
