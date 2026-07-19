#!/usr/bin/env bash
# Executa tot el pipeline de principi a fi
set -euo pipefail
cd "$(dirname "$0")"

export PATH="$HOME/.local/bin:$(brew --prefix openjdk@21)/bin:$PATH"
export JAVA_HOME="$(brew --prefix openjdk@21)"
source .venv/bin/activate

echo "==== 1/4 Descàrrega de dades ===="
./01_download.sh

echo "==== 2/4 Mapa base (30-90 min) ===="
python 02_basemap.py

echo "==== 3/4 Demanda (1-4 h, sobretot les rutes) ===="
python 03_demand.py

echo "==== 4/4 Paquet final ===="
./04_package.sh

echo
echo "LLEST! Importa BCN.zip amb Railyard i comença una partida a 'Barcelona (AMB ampliada)'."
