#!/usr/bin/env bash
# Preparazione del Codespace: pacchetto Python, LaTeX minimo per l'articolo, test.
set -euo pipefail
pip install -e ".[dev,mesa]" jupyter ipykernel
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-publishers \
  texlive-fonts-recommended lmodern latexmk >/dev/null
pytest -q
echo "Pronto. Prova: make help"
