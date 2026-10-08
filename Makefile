# Comandi principali del progetto. `make help` per l'elenco.
PY ?= python

.PHONY: help install test report fase2 automazione scala docking dynamics paper site all clean

help:            ## mostra questo elenco
	@grep -E '^[a-z0-9]+:.*## ' Makefile | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

install:         ## installa il pacchetto con test e Mesa
	$(PY) -m pip install -e ".[dev,mesa]"

test:            ## esegue i test (invarianti, riproducibilità, docking)
	$(PY) -m pytest -q

report:          ## rigenera figure, numeri chiave e dati del sito (~20 s)
	$(PY) scripts/make_report.py

fase2:           ## esperimenti della fase 2 (IA): bersagli e corsa
	$(PY) scripts/fase2.py

automazione:     ## D15: automazione scelta dall'impresa contro ottimo sociale
	$(PY) scripts/automazione.py

scala:           ## verifica dell'invarianza alla scala (fino a 5 milioni di agenti)
	$(PY) scripts/scale_check.py

docking:         ## confronto statistico NumPy vs Mesa
	$(PY) scripts/docking.py

dynamics:        ## dati della vista dinamica (site/dinamica.html)
	$(PY) scripts/export_dynamics.py

paper:           ## compila l'articolo in paper/main.pdf
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

site:            ## serve il sito in locale su http://localhost:8000
	$(PY) -m http.server -d site 8000

all: test docking report fase2 automazione dynamics paper  ## tutta la pipeline

clean:           ## rimuove i file intermedi di LaTeX
	cd paper && latexmk -c
