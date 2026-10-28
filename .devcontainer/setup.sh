#!/usr/bin/env bash
# Preparazione del Codespace: pacchetto Python, LaTeX minimo per l'articolo, test, Claude Code.
set -euo pipefail
pip install -e ".[dev,mesa]" jupyter ipykernel
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-publishers \
  texlive-fonts-recommended lmodern latexmk >/dev/null
pytest -q
# Claude Code (si avvia con `claude`; al primo avvio chiede l'accesso con l'account Claude)
curl -fsSL https://claude.ai/install.sh | bash || echo "Installazione di Claude Code non riuscita: riprova a mano."
echo "Pronto. Prova: make help"
