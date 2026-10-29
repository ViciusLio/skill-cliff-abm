# Comandi principali del progetto. `make help` per l'elenco.
PY ?= python

.PHONY: help install test report fase2 automazione mentore validazione politiche sensibilita scala docking docking-netlogo simmetria dynamics paper paper-it site all clean

help:            ## mostra questo elenco
	@grep -E '^[a-z0-9-]+:.*## ' Makefile | awk -F':.*## ' '{printf "  make %-16s %s\n", $$1, $$2}'

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

validazione:     ## T6: coorti che entrano in una recessione, persistenza della perdita (~3 min)
	$(PY) scripts/validazione.py

politiche:       ## T9: quattro leve di politica a parità di intensità, due contesti (~4 min)
	$(PY) scripts/politiche.py

sensibilita:     ## T10a: indici di Sobol su nove parametri, 704 punti (~8 min con 2 core)
	$(PY) scripts/sensibilita.py

mentore:         ## D20: mentore stabile (calibrazione, proposizioni, IA) e suo docking con Mesa
	$(PY) scripts/mentore_stabile.py
	$(PY) scripts/docking.py --mentore

scala:           ## verifica dell'invarianza alla scala (fino a 5 milioni di agenti)
	$(PY) scripts/scale_check.py

docking:         ## confronto statistico NumPy vs Mesa (modello base; la variante D20 in make mentore)
	$(PY) scripts/docking.py

docking-netlogo: ## NetLogo vs NumPy, 7 scenari (serve NETLOGO_HOME, NetLogo 6.4 e Java; ~15 min)
	$(PY) scripts/docking_netlogo.py

simmetria:       ## p dimezzato contro beta dimezzato: stesso effetto medio? (~10 s)
	$(PY) scripts/simmetria_p_beta.py

dynamics:        ## dati della vista dinamica (site/dinamica.html)
	$(PY) scripts/export_dynamics.py

paper:           ## compila l'articolo in paper/main.pdf
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex

paper-it:        ## traduzioni italiane dell'articolo (paper/it), PDF copiati in site/
	cd paper/it && latexmk -pdf -interaction=nonstopmode articolo_v1_it.tex && latexmk -pdf -interaction=nonstopmode articolo_it.tex
	cp paper/it/articolo_v1_it.pdf site/articolo_v1_it.pdf
	cp paper/it/articolo_it.pdf site/articolo_it.pdf

site:            ## serve il sito in locale su http://localhost:8000
	$(PY) -m http.server -d site 8000

all: test docking report fase2 automazione mentore validazione politiche sensibilita dynamics paper  ## tutta la pipeline

clean:           ## rimuove i file intermedi di LaTeX
	cd paper && latexmk -c
