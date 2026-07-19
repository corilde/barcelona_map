# Barcelona (regió metropolitana) — mapa per a Subway Builder

Mapa personalitzat de la regió metropolitana de Barcelona per al joc [Subway Builder](https://www.subwaybuilder.com/), compatible amb la versió 1.4.x i amb [Railyard](https://subwaybuildermodded.com/).

**Cobertura**: de Coma-ruga (el Vendrell) a Maçanet de la Selva i Blanes per la costa, i fins a Igualada i Manresa per l'interior — uns 115 × 75 km amb més de 5 milions d'habitants.

*Custom map of the Barcelona metropolitan region for Subway Builder (game v1.4.x, Railyard-compatible). From Coma-ruga to Maçanet de la Selva along the coast, inland to Igualada and Manresa.*

## Característiques

- **Mapa base actualitzat** amb OpenStreetMap recent: edificis 3D, ponts i túnels de carreteres (novetat del joc 1.4.5), batimetria del fons marí per a costos de túnels realistes, i etiquetes de municipis i barris en català.
- **Demanda realista basada en dades censals**: població i ocupats de la graella censal Eurostat/INE 2021 (cel·les d'1 km refinades a 500 m amb edificis OSM), i desplaçaments casa-feina generats amb un model gravitatori doblement restringit. Resultat: ~2,3 M de desplaçaments diaris amb una mediana de trajecte de 7,6 km / 13 min.
- **Demanda especial**: aeroport de Barcelona (T1/T2), port de creuers, universitats (UB, UAB, UPC, UPF, UManresa), 12 hospitals, Camp Nou, RCDE Stadium, Anella Olímpica, Sagrada Família, Park Güell, Tibidabo, platges (Barceloneta, Castelldefels, Sitges, Coma-ruga, Blanes), fires i centres comercials.
- **Índex d'edificis en format binari** (requerit pel joc ≥1.4).

## Instal·lació (jugadors)

1. Descarrega `BCN.zip` de la pàgina de [Releases](../../releases).
2. Obre [Railyard](https://github.com/Subway-Builder-Modded/monorepo/releases/latest) → **Import** → selecciona el zip.
3. Comença una partida nova a "Barcelona (regió metropolitana)".

## Regenerar el mapa (avançat)

Aquest repositori conté el pipeline complet per regenerar el mapa des de zero (macOS + Homebrew):

```bash
./00_install.sh   # instal·la eines i dependències
./run_all.sh      # descarrega dades i genera BCN.zip (3-5 h)
```

L'àrea, el model de demanda i els punts especials es configuren a `config_bcn.py`. Vegeu els comentaris de cada fitxer per als detalls.

## Fonts de dades i eines

- [OpenStreetMap](https://www.openstreetmap.org/copyright) via Geofabrik (© contribuïdors d'OSM)
- [Graella censal Eurostat/GISCO 2021](https://ec.europa.eu/eurostat/web/gisco/geodata/grids) (Cens 2021, INE)
- Edificis: Overture Maps Foundation
- [depot](https://github.com/Subway-Builder-Modded/depot) (Subway Builder Modded), planetiler, tippecanoe, osmium, OSMnx

Tiles vectorials derivades d'OpenStreetMap (CC-BY, © OpenMapTiles © OpenStreetMap contributors).
