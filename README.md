# La *skill cliff*: chi insegnerà ai senior di domani?

Modello ad agenti sulla trasmissione di capitale umano tra generazioni e sugli effetti
ritardati dell'intelligenza artificiale. Federico Bassi e Vincenzo Lio, lavoro in corso.

[![Apri in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ViciusLio/skill-cliff-abm?quickstart=1)

- **Articolo** (bozza, in inglese): [articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf), sorgente [`paper/main.tex`](paper/main.tex)
- **Lezione**: [lezione](https://viciuslio.github.io/skill-cliff-abm/lezione.html)
- **Risultati**: [report](https://viciuslio.github.io/skill-cliff-abm/) e [dinamica degli agenti](https://viciuslio.github.io/skill-cliff-abm/dinamica.html)
- **Fase 2 (IA)**: [risultati interattivi](https://viciuslio.github.io/skill-cliff-abm/fase2.html) e [sintesi](report/sintesi_fase2.md)
- **Sintesi tecnica della fase 1**: [sintesi](report/sintesi.md)
- **Descrizione standard del modello (protocollo ODD)**: appendice A dell'[articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf)
- **Nota sulla calibrazione** (traccia per la discussione): [nota](report/nota_calibrazione.md)
- **Resoconto dell'8 ottobre 2026**: [resoconto](report/resoconto_2026-10-08.md)

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
2. **Sostituire i senior conta solo se i mentori sono scarsi:** quasi nessun effetto con capacità di
   mentoring abbondante, −4,8% di capitale umano se è già al limite.
3. **Sostituire i non qualificati aumenta la disuguaglianza** (Gini da 0,155 a 0,170).
4. **La corsa:** con la stima prudente di Acemoglu (θ = 0,02) la perdita di capitale umano si mangia
   circa l'86% del guadagno di produttività dell'IA.
5. **Se i junior sostituiti restano senza lavoro** il danno raddoppia (capitale umano −10,2%) e
   l'output finisce sotto lo scenario senza IA.
6. **Le imprese automatizzano troppo.** Un'impresa che non vede la perdita futura di capitale umano
   automatizza il 30% dei compiti junior; su un orizzonte di 50 anni l'ottimo sociale è il 9%, e la
   scelta privata vale meno di non automatizzare affatto. Su 10 anni le due scelte quasi coincidono:
   il danno arriva dopo.

## Cosa significa: implicazioni

I numeri qui sotto vengono dal modello calibrato, non da dati: indicano direzioni e ordini di
grandezza, non previsioni.

**Lavoro.**
- **Il posto da junior è un posto di formazione.** Un junior non produce solo il suo output: è il canale
  con cui la conoscenza dei senior passa alla generazione successiva. Tagliare le assunzioni
  entry-level riduce l'apprendimento da incontri del 45%.
- **Il conto arriva ai senior di domani.** Chi oggi è già senior non perde nulla; chi entra oggi
  diventerà un senior con meno competenze. Nel modello l'effetto sui senior compare dopo 12 anni.
- **Restare fuori costa il doppio.** Se i junior sostituiti non trovano un altro lavoro, la perdita
  di capitale umano passa dal 5,2% al 10,2% e l'output scende sotto lo scenario senza IA.

**Politica.**
- **È un fallimento di mercato.** La formazione dei junior è un'esternalità tra generazioni:
  l'impresa paga il costo, il beneficio va all'economia futura. Nel modello un'impresa automatizza
  il 30% dei compiti junior; il pianificatore, su 50 anni, si ferma al 9%.
- **L'orizzonte decide.** Su 10 anni le due scelte quasi coincidono (25% contro 30%). Una politica
  valutata sul bilancio annuale o sul ciclo elettorale non vede il problema.
- **Le leve hanno un parametro preciso nel modello:**
  - capacità di mentoring riservata nelle imprese (κ);
  - apprendistati su progetti reali (p);
  - contributo sull'automazione dei compiti entry-level (tassa sulle riduzioni di p);
  - incentivi all'IA che aiuta a insegnare invece di sostituire chi impara (β).

  La Proposizione 1 permette di confrontarle con la stessa metrica, l'effetto su `B`.
- **Misurare prima.** Quando il calo si vede nei senior è tardi. Gli indicatori da seguire sono le
  assunzioni entry-level, il rapporto junior/senior e il tempo dedicato al mentoring.

**Tecnologia.**
- **Conta la direzione, non il livello.** La stessa IA che sostituisce i junior toglie il 5,2% di
  capitale umano; usata per rendere più efficace l'insegnamento lo aumenta del 5,2% e l'output
  cresce del 12%.
- **I co-pilot sono una via di mezzo.** Aiutano chi impara, ma possono ridurne lo sforzo (Ide 2026):
  nel modello sarebbero un β più alto con meno apprendimento autonomo. Il saldo non è scontato e non
  l'abbiamo ancora simulato.
- **Il guadagno di produttività può sparire.** Con la stima prudente di Acemoglu (θ = 0,02), la
  perdita di capitale umano si mangia circa l'86% del guadagno dell'IA.

**Società.**
- **Equità tra generazioni.** Chi paga sono i lavoratori che entreranno nei prossimi anni, che oggi
  non votano e non negoziano.
- **Disuguaglianza.** Gli incontri comprimono le differenze di competenze; toglierli le allarga.
  Sostituire i non qualificati porta il Gini da 0,155 a 0,170: chi parte più indietro perde anche
  le occasioni per recuperare. Il risultato si collega all'ipotesi di "doppia segregazione"
  (ricchezza e competenze).
- **Il caso italiano.** Le grandi coorti degli anni '60 vanno in pensione proprio ora: la scogliera
  demografica e quella dell'IA rischiano di sovrapporsi. Il modello per ora ha una demografia
  stazionaria, quindi questo resta da verificare.

Approfondimenti: sezione 7 dell'[articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf) e
sezione 7 del [resoconto](report/resoconto_2026-10-08.md).

## Come leggere questo lavoro

- **In 10 minuti.** La [lezione](https://viciuslio.github.io/skill-cliff-abm/lezione.html),
  poi la [dinamica degli agenti](https://viciuslio.github.io/skill-cliff-abm/dinamica.html)
  con lo scenario "p dimezzato".
- **In un'ora.** L'[articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf): introduzione
  (tre lacune e quattro contributi), sezione 4 (risultati), sezione 5 (le due proposizioni),
  sezione 6 (l'IA: bersagli, corsa, impresa contro pianificatore), sezione 7 (fallimento di
  mercato e politiche). L'appendice A descrive il modello con il protocollo ODD.
- **Per verificare tutto.** La [sintesi tecnica](report/sintesi.md) con equazioni, parametri e una
  sezione *Verifiche* che dice cosa torna e cosa no. Poi apri il Codespace ed esegui
  [`notebooks/esplora_modello.ipynb`](notebooks/esplora_modello.ipynb), che ricalcola le
  proposizioni a partire dal codice.

---

## Per chi lavora sul codice

### Avvio rapido in Codespaces (consigliato)

Pulsante qui sopra, oppure *Code → Codespaces → Create codespace on main*. Al primo avvio
(qualche minuto) il devcontainer installa Python, il pacchetto, Jupyter e LaTeX, poi lancia
i test. Quindi:

```bash
make help        # elenco dei comandi
make test        # test: invarianti, riproducibilità, IA, docking con Mesa
make report      # fase 1: figure, numeri e dati del sito (~15 s con 4 core)
make fase2       # fase 2: scenari IA, corsa, sensibilità (~2 min con 4 core)
make automazione # D15: automazione dell'impresa contro ottimo sociale (~30 s)
make scala       # invarianza alla scala, fino a 5 milioni di agenti (~3 min)
make docking     # NumPy contro Mesa: test di differenza e di equivalenza (~1 min)
make paper       # compila paper/main.pdf
make site        # sito in locale sulla porta 8000 (si apre da solo)
```

Il Codespace usa la quota gratuita dell'account GitHub di chi lo apre (circa 120 ore-core al mese).
Alla creazione si possono scegliere più core: le repliche girano in parallelo su tutti quelli disponibili
(o su `SKILLCLIFF_WORKERS`), quindi i tempi scendono quasi in proporzione.

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
                  ai.py          IA (fase 2): A(t), bersagli, non occupazione, output,
                                 automazione a quota fissa (D15), esperimento "p dimezzato"
                  mesa_twin.py   gemello Mesa (solo docking)
configs/          parametri YAML
scripts/          run_scenario.py   repliche di uno scenario con parametri da riga di comando
                  make_report.py    fase 1: figure, numeri, dati del sito
                  fase2.py          fase 2: scenari IA, corsa, sensibilità a kappa
                  automazione.py    D15: automazione scelta dall'impresa contro ottimo sociale
                  scale_check.py    invarianza alla scala (fino a 24 milioni di agenti)
                  docking.py        confronto NumPy vs Mesa
                  export_dynamics.py  dati della vista dinamica
                  verify_site.mjs   verifica del sito in un browser headless
notebooks/        esplorazione interattiva
tests/            pytest
paper/            articolo LaTeX (elsarticle) e figure in inglese
report/           sintesi delle fasi, resoconto, numeri chiave (numeri_*.json), figure in italiano
site/             sito pubblicato su GitHub Pages: index (fase 1), dinamica, fase2, lezione
outputs/          risultati delle simulazioni (non versionati, tranne outputs/examples)
```

### Scelte tecniche

- **NumPy vettorizzato.** Un run (300 anni di burn-in e 60 registrati) richiede circa 0,07 s con N = 5.000 e 0,5 s con N = 50.000; durante il burn-in le metriche non vengono calcolate.
- **Burn-in di 300 anni.** Ogni generazione impara dalla precedente, quindi la convergenza è lenta: con 120 anni restava una deriva dello 0,4% nei livelli (i confronti tra scenari non cambiavano). Con 300 la deriva residua è sotto 10⁻⁵ l'anno.
- **Repliche in parallelo.** Le repliche girano su tutti i core (`SKILLCLIFF_WORKERS` per limitarli); ogni replica ha il proprio seed, quindi il risultato non dipende dal numero di processi. 30 repliche con N = 50.000 su 4 core: circa 5 s.
- **Invarianza alla scala.** Gli agenti si incontrano per estrazione casuale dentro gruppi grandi, non lungo reti locali: da 5 mila a 24 milioni di agenti (gli occupati italiani) i risultati coincidono alla quarta cifra. N riduce solo il rumore; la fase 1 usa 5.000 agenti, la fase 2 50.000.
- **Mesa solo come gemello.** Una seconda implementazione indipendente, con un oggetto per agente, verifica il modello (*docking*, Axtell et al. 1996): con 5.000 agenti e 30 repliche un test di equivalenza dimostra che le due versioni coincidono entro ±1% (in pratica entro ±0,4%). A parità di core Mesa è circa 15–20 volte più lenta, quindi non si usa per le analisi.
- **Riproducibilità.** Seed derivati per replica; stream separati per demografia, incontri e IA; numeri casuali comuni tra scenari, quindi prima dell'arrivo dell'IA ogni scenario è identico al bit allo scenario senza IA.
- **Integrazione continua.** A ogni push i test girano su Python 3.11 e 3.13. A ogni push su `main` (o a mano da *Actions → Pages → Run workflow*) GitHub Actions compila l'articolo, pubblica il sito e poi lo verifica in un browser headless (`scripts/verify_site.mjs`): pagine raggiungibili, grafici con dati, animazione disegnata, reindirizzamento dei vecchi indirizzi.
