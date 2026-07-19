#!/usr/bin/env bash
# Empaqueta el mapa en un zip importable per Railyard
set -euo pipefail
cd "$(dirname "$0")"

CODE="BCN"
cd "$CODE"

# comprovacions (índex d'edificis en format binari, requerit pel joc >=1.4)
for f in config.json "$CODE.pmtiles" buildings_index.bin demand_data.json \
         roads.geojson runways_taxiways.geojson; do
  [ -e "$f" ] || { echo "FALTA: $f — executa els passos anteriors"; exit 1; }
done

# opcionals: batimetria, esquemes de demanda especial, descripció
EXTRAS=""
for x in buildings_index.bin.gz ocean_depth_index.json ocean_depth_index.json.gz \
         description.md; do
  [ -e "$x" ] && EXTRAS="$EXTRAS $x"
done
[ -d .railyard_map ] && EXTRAS="$EXTRAS .railyard_map"

rm -f "../$CODE.zip"
zip -r -q "../$CODE.zip" config.json "$CODE.pmtiles" buildings_index.bin \
  demand_data.json roads.geojson runways_taxiways.geojson $EXTRAS

cd ..
echo "Creat $(pwd)/$CODE.zip ($(du -h $CODE.zip | cut -f1))"
echo "Obre Railyard -> Import -> selecciona $CODE.zip"
