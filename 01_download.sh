#!/usr/bin/env bash
# Descarrega les dades font: OSM Catalunya + graella censal Eurostat 2021
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data

echo "== OSM Catalunya (Geofabrik, ~600 MB) =="
if [ ! -f data/cataluna-latest.osm.pbf ]; then
  wget -c -O data/cataluna-latest.osm.pbf \
    https://download.geofabrik.de/europe/spain/cataluna-latest.osm.pbf
fi

echo "== Graella censal Eurostat/GISCO 2021 (1 km, ~232 MB) =="
if ! ls data/grid2021/**/*.gpkg data/grid2021/*.gpkg >/dev/null 2>&1; then
  mkdir -p data/grid2021
  # Llistat de versions: https://gisco-services.ec.europa.eu/census/releases/
  wget -c -O data/grid2021.zip \
    "https://gisco-services.ec.europa.eu/census/releases/20250123/output/ESTAT_Census_2021_V2.gpkg.zip" \
    || { echo "AVÍS: descàrrega automàtica fallida; baixa-la manualment (vegeu README)"; exit 1; }
  unzip -o data/grid2021.zip -d data/grid2021
fi

echo "Fet."
