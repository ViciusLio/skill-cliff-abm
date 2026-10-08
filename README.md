# La *skill cliff*: chi insegnerà ai senior di domani?

Modello ad agenti sulla trasmissione di capitale umano tra generazioni e sugli effetti
ritardati dell'intelligenza artificiale. Federico Bassi e Vincenzo Lio, lavoro in corso.

[![Apri in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ViciusLio/skill-cliff-abm?quickstart=1)

- **Articolo** (bozza, in inglese): [articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf), sorgente [`paper/main.tex`](paper/main.tex)
- **Lezione**: [lezione](https://viciuslio.github.io/skill-cliff-abm/lezione.html)
- **Risultati**: [report](https://viciuslio.github.io/skill-cliff-abm/) e [dinamica degli agenti](https://viciuslio.github.io/skill-cliff-abm/dinamica.html)
- **Fase 2 (IA)**: [risultati interattivi](https://viciuslio.github.io/skill-cliff-abm/fase2.html) e [sintesi](report/sintesi_fase2.md)
- **Sintesi tecnica della fase 1**: [sintesi](report/sintesi.md)
- **Resoconto del 8 ottobre 2026**: [resoconto](report/resoconto_2026-10-08.md)

---

## La domanda

Quando un'impresa affida all'IA il lavoro che prima faceva un junior, risparmia un salario oggi.
Ma quel junior, lavorando accanto a un senior, avrebbe imparato qualcosa, e fra quindici anni
sarebbe diventato a sua volta il senior che insegna. **Che cosa succede al capitale umano di
un'economia quando si riducono le occasioni in cui chi sa incontra chi impara?**

## Tesi, antitesi e risultati

**L'antitesi, cioè la visione standard.** Nel modello di crescita di Lucas (1988) il capitale umano cresce come
`ḣ = B(1−u)h`, dove `1−u` è il tempo dedicato a imparare e `B`, l'efficienza dell'apprendimento, è un
**parametro**: Lucas lo fissa, non lo spiega.
Se `B` è fisso, una tecnologia che riorganizza il lavoro non tocca la capacità di imparare.
L'IA può sostituire alcuni lavoratori o completarli (Acemoglu 2024), ma l'effetto si misura
oggi, sull'occupazione.

**La tesi.** `B` non è un parametro: **emerge dagli incontri**. Lucas e Moll (2014) mostrano che
la conoscenza si trasmette incontrando chi ne sa di più, con un guadagno proporzionale alla
distanza di conoscenza. Jarosch, Oberfield e Rossi-Hansberg (2021) stimano che imparare dai
colleghi valga il 4–9% della retribuzione. Se l'IA toglie lavoro proprio ai junior, e i primi
dati dicono che lo fa (Brynjolfsson et al. 2025; Hosseini e Lichtinger 2025), toglie anche gli
incontri con cui i junior imparano (Ide 2026). Il danno però non si vede subito: arriva **una
generazione professionale dopo**, quando i junior formati con meno incontri diventano i senior.
È questa la *skill cliff*.

**I risultati finora (fase 1: modello senza IA).**
1. **Il modello è realistico dove deve esserlo.** Riproduce un profilo salariale che cresce
   lentamente e si appiattisce dopo circa 34 anni di esperienza, come nel settore privato italiano.
   L'apprendimento dei junior dovuto agli incontri (4,3% del salario l'anno) rientra nelle stime empiriche.
2. **`B` emerge e dipende dalla storia.** Il 62% dell'apprendimento dei junior viene dagli
   incontri con i senior. Se gli incontri calano, `B` crolla subito, risale per un po' e poi
   scende di nuovo quando i senior "impoveriti" diventano insegnanti.
3. **Il ritardo è esatto.** Dimezzando gli incontri, il capitale umano dei senior resta
   *identico* per 10 anni e inizia a scendere all'11°, cioè dopo `s_S − s_J + 1` anni, come
   previsto dalla Proposizione 2 dell'articolo (anche con soglie 10/20). A regime cala del 6,7%
   e l'output del 7,2%.
4. **Dal micro al macro.** Un'identità di campo medio (Proposizione 1) traduce le regole
   individuali in un'equazione aggregata per `B`, che dipende da opportunità d'incontro,
   capacità di mentoring e distribuzione della conoscenza. Si può innestare nei modelli di
   crescita a una equazione.

**Fase 2: l'IA.** Una produttività `A(t)` che cresce al tasso `g` automatizza una quota crescente
dei compiti del bersaglio (junior, senior, qualificati, non qualificati) oppure, nel caso
complementare, rende più efficace l'insegnamento. Risultati, 50 anni dopo l'introduzione:
1. **Sostituire i junior è il caso peggiore:** capitale umano −5,2%, apprendimento da incontri −45%;
   sui senior l'effetto arriva dopo 12 anni.
2. **Sostituire i senior quasi non conta** finché c'è capacità di mentoring in eccesso.
3. **Sostituire i non qualificati aumenta la disuguaglianza** (Gini da 0,155 a 0,170).
4. **La corsa:** con la stima prudente di Acemoglu (θ = 0,02) la perdita di capitale umano si mangia
   circa l'85% del guadagno di produttività dell'IA.

## Come leggere questo lavoro

- **In 10 minuti.** La [lezione](https://viciuslio.github.io/skill-cliff-abm/lezione.html),
  poi la [dinamica degli agenti](https://viciuslio.github.io/skill-cliff-abm/dinamica.html)
  con lo scenario "p dimezzato".
- **In un'ora.** L'[articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf): introduzione
  (tre lacune e tre contributi), sezione 4 (risultati), sezione 5 (le due proposizioni),
  sezione 6 (fallimento di mercato e politiche).
- **Per verificare tutto.** La [sintesi tecnica](report/sintesi.md) con equazioni, parametri e una
  sezione *Verifiche* che dice cosa torna e cosa no. Poi apri il Codespace ed esegui
  [`notebooks/esplora_modello.ipynb`](notebooks/esplora_modello.ipynb), che ricalcola le
  proposizioni a partire dal codice.

---

## Per chi lavora sul codice

### Avvio rapido in Codespaces (consigliato)

Pulsante qui sopra, oppure *Code → Codespaces → Create codespace on main*. Al primo avvio
(circa 3–4 minuti) il devcontainer installa Python, il pacchetto, Jupyter e LaTeX, poi lancia
i test. Quindi:

```bash
make help        # elenco dei comandi
make test        # test: invarianti, riproducibilità, docking con Mesa
make report      # rigenera figure, numeri e dati del sito (~20 s)
make fase2       # esperimenti della fase 2 (~30 s con 4 core)
make paper       # compila paper/main.pdf
make site        # sito in locale sulla porta 8000 (si apre da solo)
```

Il Codespace usa la quota gratuita dell'account GitHub di chi lo apre (circa 120 ore-core al mese).

### Installazione locale

Serve Python ≥ 3.11 (LaTeX solo per l'articolo).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mesa]"
make test
```

### Parametri e scenari

I parametri sono in [`configs/base.yaml`](configs/base.yaml). Da riga di comando si sovrascrivono con:

```bash
python scripts/run_scenario.py --name p03 --set meetings.p=0.3 --reps 10
```

### Struttura

```
src/skillcliff/   config.py      parametri (dataclass da YAML)
                  population.py  demografia (struttura di array)
                  learning.py    incontri junior-senior, apprendimento autonomo
                  model.py       dinamica annuale
                  metrics.py     metriche, Gini, IC tra repliche
                  experiment.py  repliche con seed derivati, salvataggio
                  ai.py          aggancio per la fase 2 (e l'esperimento di meccanismo)
                  mesa_twin.py   gemello Mesa (solo docking)
configs/          parametri YAML
scripts/          scenari, docking, report, vista dinamica
notebooks/        esplorazione interattiva
tests/            pytest
paper/            articolo LaTeX (elsarticle) e figure in inglese
report/           sintesi tecnica e figure in italiano
site/             sito pubblicato su GitHub Pages
outputs/          risultati delle simulazioni (non versionati, tranne outputs/examples)
```

### Scelte tecniche

- **NumPy vettorizzato.** Un run con N = 5.000 e 180 anni richiede circa 0,07 s.
- **Mesa solo come gemello.** Una seconda implementazione indipendente, con un oggetto per agente, verifica il modello (*docking*, Axtell et al. 1996).
- **Riproducibilità.** Seed derivati per replica, stream separati per demografia e incontri, numeri casuali comuni tra scenari.
- **Pubblicazione.** A ogni push su `main` che tocca `site/` o `paper/`, GitHub Actions compila l'articolo, pubblica il sito e poi lo verifica in un browser headless (`scripts/verify_site.mjs`): pagine raggiungibili, grafici con dati, animazione disegnata.
