#!/usr/bin/env bash
# Instal·la totes les eines necessàries (macOS + Homebrew)
set -euo pipefail
cd "$(dirname "$0")"

command -v brew >/dev/null || { echo "Cal Homebrew: https://brew.sh"; exit 1; }

echo "== Paquets de Homebrew =="
brew install python@3.12 osmium-tool tippecanoe pmtiles jq node openjdk@21 wget git zip gdal

# Java 21 visible per al sistema
sudo ln -sfn "$(brew --prefix openjdk@21)/libexec/openjdk.jdk" \
  /Library/Java/JavaVirtualMachines/openjdk-21.jdk 2>/dev/null || true
export JAVA_HOME="$(brew --prefix openjdk@21)"
export PATH="$JAVA_HOME/bin:$PATH"

echo "== mapshaper (npm) =="
npm list -g mapshaper >/dev/null 2>&1 || npm install -g mapshaper

echo "== planetiler =="
mkdir -p "$HOME/.local/bin"
if [ ! -f "$HOME/.local/bin/planetiler.jar" ]; then
  curl -L -o "$HOME/.local/bin/planetiler.jar" \
    https://github.com/onthegomap/planetiler/releases/latest/download/planetiler.jar
fi
chmod +x "$HOME/.local/bin/planetiler.jar"
export PATH="$HOME/.local/bin:$PATH"

echo "== Entorn Python =="
python3.12 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet geopandas shapely pandas numpy duckdb mapbox_vector_tile \
  requests osmnx scipy pyogrio \
  "httpx[http2]" tqdm unidecode inflect matplotlib mercantile networkx xarray \
  netcdf4 h5netcdf pydap scikit-learn

echo "== depot (eines de mapes de Subway Builder Modded) =="
[ -d depot ] || git clone --depth 1 https://github.com/Subway-Builder-Modded/depot.git
pip install --quiet ./depot

echo
echo "Fet! Ara executa ./run_all.sh"
