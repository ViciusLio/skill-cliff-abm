# skill-cliff-abm

Modello ad agenti sulla trasmissione di capitale umano tra lavoratori senior e junior
e sull'effetto dell'IA (ipotesi della *skill cliff*).

- **Fase 1** (completata, in revisione): modello base senza IA → [`report/sintesi.md`](report/sintesi.md)
- **Fase 2** (da fare): IA con produttività A(t) e target di sostituzione

## Installazione

Serve Python ≥ 3.11.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # modello e test
pip install -e ".[dev,mesa]"     # anche il gemello Mesa per il docking
```

### In alternativa: GitHub Codespaces

*Code → Codespaces → Create codespace on …*. Il devcontainer installa tutto e lancia i test.

## Esecuzione

```bash
pytest -q                                            # test
python scripts/run_scenario.py --name base           # 30 repliche dello scenario base
python scripts/run_scenario.py --name p03 --set meetings.p=0.3 --reps 10
python scripts/docking.py                            # confronto NumPy vs Mesa
python scripts/make_report.py                        # figure, numeri e dati del report (~20 s)
python -m http.server -d site 8000                   # report interattivo su http://localhost:8000
```

I parametri sono in [`configs/base.yaml`](configs/base.yaml). Si sovrascrivono da riga di comando
con `--set sezione.parametro=valore`.

## Struttura

```
src/skillcliff/   config.py      parametri (dataclass da YAML)
                  population.py  demografia (struttura di array)
                  learning.py    incontri junior-senior, apprendimento autonomo
                  model.py       dinamica annuale
                  metrics.py     metriche, Gini, IC tra repliche
                  experiment.py  repliche con seed derivati, salvataggio
                  ai.py          aggancio per la fase 2
                  mesa_twin.py   gemello Mesa (solo docking)
configs/          parametri YAML
scripts/          esecuzione scenari, docking, report
tests/            pytest
report/           sintesi.md e figure
site/             report interattivo (GitHub Pages)
outputs/          risultati delle simulazioni (non versionati, tranne outputs/examples)
```

## Scelte tecniche

- **NumPy vettorizzato.** Un run con N = 5.000 e 180 anni richiede circa 0,07 s.
- **Mesa solo come gemello.** Una seconda implementazione indipendente, con un oggetto per agente, serve a verificare il modello vettorizzato (docking, Axtell et al. 1996). È circa 10 volte più lenta, quindi non si usa per le analisi.
- **Riproducibilità.**
  - La replica *r* usa `SeedSequence(seed).spawn(n_reps)[r]`.
  - Gli stream per demografia e incontri sono separati.
  - A parità di seed gli scenari condividono le estrazioni casuali (common random numbers).

## Report interattivo (GitHub Pages)

Il workflow `.github/workflows/pages.yml` rigenera i risultati e pubblica `site/` a ogni push su `main`.
Va attivato una sola volta in *Settings → Pages → Build and deployment → Source: GitHub Actions*.
