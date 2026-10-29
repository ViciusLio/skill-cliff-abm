# La *skill cliff*: chi insegnerà ai senior di domani?

Modello ad agenti sulla trasmissione di capitale umano tra generazioni e sugli effetti
ritardati dell'intelligenza artificiale. Federico Bassi e Vincenzo Lio, lavoro in corso.

[![Apri in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ViciusLio/skill-cliff-abm?quickstart=1)

- **Per tutti**: [La bottega vuota](Medium/la_bottega_vuota.md), articolo divulgativo sulle conclusioni dei modelli
  (Medium, circa 13 minuti; versione base ed estesa)
- **Articolo** (bozza, in inglese): [articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf), sorgente [`paper/main.tex`](paper/main.tex);
  [traduzione italiana](https://viciuslio.github.io/skill-cliff-abm/articolo_it.pdf) della versione in lavorazione
- **Lezione**: [lezione](https://viciuslio.github.io/skill-cliff-abm/lezione.html)
- **Risultati**: [report](https://viciuslio.github.io/skill-cliff-abm/) e [dinamica degli agenti](https://viciuslio.github.io/skill-cliff-abm/dinamica.html)
- **Fase 2 (IA)**: [risultati interattivi](https://viciuslio.github.io/skill-cliff-abm/fase2.html) e [sintesi](report/sintesi_fase2.md)
- **Sintesi tecnica della fase 1**: [sintesi](report/sintesi.md)
- **Descrizione standard del modello (protocollo ODD)**: appendice A dell'[articolo](https://viciuslio.github.io/skill-cliff-abm/paper.pdf)
- **Nota sulla calibrazione** (traccia per la discussione): [nota](report/nota_calibrazione.md)
- **Resoconto dell'8 ottobre 2026**: [resoconto](report/resoconto_2026-10-08.md)
- **Revisione dei meccanismi** (osservazioni di Federico, decisioni D16–D20, tutte realizzate): [revisione](report/revisione_meccanismi.md)
- **Il modello in NetLogo**: [`Netlogo/skill_cliff.nlogo`](Netlogo/skill_cliff.nlogo) ([scarica](https://github.com/ViciusLio/skill-cliff-abm/raw/main/Netlogo/skill_cliff.nlogo)),
  guida in [`Netlogo/LEGGIMI.md`](Netlogo/LEGGIMI.md). È il modello della prima versione, verificato contro quello Python.
- **Verso la seconda versione dell'articolo**: [revisione critica](report/revisione_articolo.md) e [piano di lavoro](report/piano_v2.md).
  `main` resta la versione base del modello; la versione estesa (imprese, IA come tutor, dati italiani) cresce nel ramo
  [`esteso`](https://github.com/ViciusLio/skill-cliff-abm/tree/esteso), verso un secondo articolo.
  La prima versione resta disponibile: [PDF](https://viciuslio.github.io/skill-cliff-abm/articolo_v1.pdf),
  [traduzione italiana](https://viciuslio.github.io/skill-cliff-abm/articolo_v1_it.pdf) e tag git `articolo-v1`.

### Dove siamo (29 ottobre 2026)

- **Prima versione** dell'articolo congelata (tag `articolo-v1`), con traduzione italiana e modello NetLogo verificato
  contro il Python (differenza massima 0,25%).
- **Seconda versione** (ramo `main`): articolo riorganizzato attorno a due risultati (il ritardo di dieci anni e
  l'equivalenza tra perdere occasioni e perdere efficacia), bibliografia da 18 a 49 voci verificate, validazione sulle
  coorti della recessione, politiche quantificate, sensibilità globale; traduzione italiana aggiornata. Restano
  affiliazioni e ruoli CRediT, la rigenerazione completa e l'invio (JASSS o SCED).
- **Versione estesa** (ramo [`esteso`](https://github.com/ViciusLio/skill-cliff-abm/tree/esteso)): l'impresa che
  sceglie quanto automatizzare (E2) e l'IA come tutor (E1), in Python e in NetLogo; verso un secondo articolo.
- **Divulgazione**: [La bottega vuota](Medium/la_bottega_vuota.md).

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
4. **Un fatto non usato nella calibrazione.** Le coorti che entrano durante una recessione, e in parte restano
   senza lavoro, perdono salario in proporzione a chi resta fuori; dopo 15 anni ne resta il 30%, vicino alle stime
   per gli Stati Uniti (Kahn 2010, circa il 40%) e più persistente di quelle canadesi (Oreopoulos et al. 2012).
5. **Dal micro al macro.** Un'identità di campo medio (Proposizione 1) traduce le regole
   individuali in un'equazione aggregata per `B`, che dipende da opportunità d'incontro,
   capacità di mentoring e distribuzione della conoscenza. Si può innestare nei modelli di
   crescita a una equazione.

**Fase 2: l'IA.** Una produttività `A(t)` che cresce al tasso `g` sostituisce una quota crescente
del lavoro del bersaglio (junior, senior, qualificati, non qualificati) oppure, nel caso
complementare, rende più efficace l'insegnamento. "Sostituire" ha due significati (D16): restare al
lavoro con meno compiti, o perdere il posto. Junior: meno incontri (p) o non occupazione; senior:
meno trasmesso per incontro (β) o meno mentori (κ). Risultati, 50 anni dopo l'introduzione:
1. **Togliere compiti ai junior o ai senior costa lo stesso:** capitale umano −5,2% (come crescere 0,11
   punti l'anno più lentamente per 49 anni), apprendimento da incontri −45%; sui senior l'effetto arriva dopo 12 anni. Cambiano disuguaglianza e tempi: il
   guadagno dell'IA va a chi la usa (D18), cioè agli esperti se sostituisce i junior (Gini dei salari
   0,167) e ai meno esperti se sostituisce i senior (0,155, come senza IA). Dopo 10 anni l'output è
   +0,22% nel primo caso e +0,35% nel secondo, perché chi è entrato dopo l'IA la conosce meglio; a 50
   anni la differenza sparisce.
2. **I senior che perdono il posto contano solo se i mentori sono scarsi:** quasi nessun effetto con
   capacità di mentoring abbondante, −4,8% di capitale umano se è già al limite.
3. **Sostituire i non qualificati aumenta la disuguaglianza** (Gini dei salari da 0,155 a 0,169;
   0,153 se l'IA sostituisce i qualificati).
4. **La corsa:** con la stima prudente di Acemoglu (θ = 0,02) la perdita di capitale umano si mangia
   il 55% del guadagno di produttività dell'IA dopo 10 anni e l'86% dopo 50 (bersaglio junior).
5. **Se i junior perdono il posto** entrano più tardi: l'esperienza cresce solo da occupati (D19),
   quindi la formazione da junior è rinviata, non persa. Il capitale umano cala del 5,7%, poco più
   che con la perdita di compiti (−5,2%); i senior sono l'11% in meno e le carriere più brevi.
   (Prima di D19, quando l'esperienza cresceva anche da non occupati, la perdita era del 10,2%.)
6. **I segni non dipendono dai parametri scelti a mano.** Variando insieme nove parametri su intervalli ampi
   (704 combinazioni), la perdita di capitale umano dovuta all'IA non è mai positiva e l'eccesso di automazione è
   sempre positivo; i livelli dipendono soprattutto da p, β e δ₀ (sensibilità globale di Sobol, appendice
   dell'articolo).
7. **Le imprese automatizzano troppo.** Un'impresa che non vede la perdita futura di capitale umano
   automatizza il 30% dei compiti junior; su un orizzonte di 50 anni l'ottimo sociale è il 9%, e la
   scelta privata vale meno di non automatizzare affatto. Su 10 anni le due scelte quasi coincidono:
   il danno arriva dopo.
8. **Se il junior resta con lo stesso mentore** (variante D20, separazione annua del 15%, β
   ricalibrato sull'apprendimento della fase 1) profilo salariale, ritardo e disuguaglianza non
   cambiano, ma togliere incontri costa meno che togliere efficacia: −3,5% di capitale umano se l'IA
   toglie compiti ai junior, −5,3% se li toglie ai senior. Chi ha già un mentore lo tiene; chi perde il
   posto perde anche il mentore (−7,2%).

## Cosa significa: implicazioni

I numeri qui sotto vengono dal modello calibrato, non da dati: indicano direzioni e ordini di
grandezza, non previsioni.

**Lavoro.**
- **Il posto da junior è un posto di formazione.** Un junior non produce solo il suo output: è il canale
  con cui la conoscenza dei senior passa alla generazione successiva. Tagliare le assunzioni
  entry-level riduce l'apprendimento da incontri del 45%.
- **Il conto arriva ai senior di domani.** Chi oggi è già senior non perde nulla; chi entra oggi
  diventerà un senior con meno competenze. Nel modello l'effetto sui senior compare dopo 12 anni.
- **Restare fuori rinvia la formazione.** Se i junior sostituiti non trovano lavoro entrano più tardi
  e fanno carriere più brevi: la perdita di capitale umano è del 5,7% (5,2% se restano occupati con
  meno compiti).

**Politica.**
- **È un fallimento di mercato.** La formazione dei junior è un'esternalità tra generazioni:
  l'impresa paga il costo, il beneficio va all'economia futura. Nel modello un'impresa automatizza
  il 30% dei compiti junior; il pianificatore, su 50 anni, si ferma al 9%.
- **L'orizzonte decide.** Su 10 anni le due scelte quasi coincidono (25% contro 30%). Una politica
  valutata sul bilancio annuale o sul ciclo elettorale non vede il problema.
- **Le leve hanno un parametro preciso nel modello**, e lo stesso aumento del 10% recupera quote molto
  diverse della perdita di capitale umano (dopo 10, 25 e 50 anni):

  | Leva | IA sui compiti dei junior, mentori abbondanti | senior che perdono il posto, mentori scarsi |
  |---|---|---|
  | apprendistati su progetti reali (p) | 117% / 52% / 24% | 0% |
  | capacità di mentoring riservata nelle imprese (κ) | 0% | 96% / 47% / 24% |
  | IA che aiuta i senior a insegnare (β) | 118% / 52% / 24% | 124% / 53% / 24% |
  | contributo sull'automazione dei compiti d'ingresso (φ −10%) | 10% | 10% |

  La leva giusta dipende da quale vincolo è attivo: se mancano occasioni d'incontro servono gli apprendistati,
  se mancano mentori serve la loro capacità; rendere più efficace l'insegnamento funziona in entrambi i casi.
  Per un'impresa la prima domanda è quindi: ai junior mancano occasioni per imparare, o ai senior il tempo per
  insegnare? (Nel modello non ci sono prezzi: stessa intensità non vuol dire stesso costo.)
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
  Sostituire i non qualificati porta il Gini dei salari da 0,155 a 0,169: chi parte più indietro perde anche
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
  (la domanda, i due risultati principali e le due conseguenze), sezione 4 (risultati), sezione 5 (le due proposizioni),
  sezione 6 (l'IA: compiti o posto, corsa, impresa contro pianificatore), sezione 7 (fallimento di
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
make validazione # T6: coorti che entrano in una recessione (~3 min)
make politiche   # T9: leve di politica a parità di intensità (~4 min)
make sensibilita # T10a: sensibilità globale (Sobol), 704 punti (~8 min)
make mentore     # D20: mentore stabile, calibrazione, IA e docking della variante (~10 min con 2 core)
make docking     # NumPy contro Mesa: test di differenza e di equivalenza (~1 min)
make docking-netlogo  # NumPy contro NetLogo, 7 scenari (serve NETLOGO_HOME; ~15 min con 2 core)
make simmetria   # p dimezzato contro β dimezzato: stesso effetto medio (~10 s)
make paper       # compila paper/main.pdf
make site        # sito in locale sulla porta 8000 (si apre da solo)
```

**Claude nel Codespace.** Il Codespace installa Claude Code: scrivi `claude` nel terminale e, al
primo avvio, accedi con il tuo account Claude (si apre un link, si incolla il codice). Le regole di
lavoro del progetto sono in [`CLAUDE.md`](CLAUDE.md), che Claude legge da solo. In un Codespace
creato prima di questa modifica si installa a mano con `curl -fsSL https://claude.ai/install.sh | bash`.

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
                  ai.py          IA (fase 2): A(t), bersagli, margine compiti/posto (D16), output,
                                 automazione a quota fissa (D15), esperimento "p dimezzato"
                  mesa_twin.py   gemello Mesa (solo docking; modello base e variante D20)
configs/          parametri YAML
scripts/          run_scenario.py   repliche di uno scenario con parametri da riga di comando
                  make_report.py    fase 1: figure, numeri, dati del sito
                  fase2.py          fase 2: scenari IA, corsa, sensibilità a kappa
                  automazione.py    D15: automazione scelta dall'impresa contro ottimo sociale
                  scale_check.py    invarianza alla scala (fino a 24 milioni di agenti)
                  validazione.py    T6: coorti che entrano in una recessione (validazione non mirata)
                  politiche.py      T9: leve di politica (apprendistati, mentoring, IA che insegna, contributo)
                  sensibilita.py    T10a: indici di Sobol dei risultati principali su nove parametri
                  mentore_stabile.py  D20: mentore stabile (variante), calibrazione di beta, proposizioni, IA
                  docking.py        confronto NumPy vs Mesa (anche la variante D20, con --mentore)
                  docking_netlogo.py  confronto NumPy vs NetLogo, scenario per scenario
                  simmetria_p_beta.py  p dimezzato contro beta dimezzato
                  export_dynamics.py  dati della vista dinamica
                  verify_site.mjs   verifica del sito in un browser headless
Netlogo/          skill_cliff.nlogo, gemello NetLogo del modello (prima versione) e guida LEGGIMI.md
notebooks/        esplorazione interattiva
tests/            pytest
CLAUDE.md         regole di lavoro per Claude (anche nel Codespace)
paper/            articolo LaTeX (elsarticle) e figure in inglese
report/           sintesi delle fasi, resoconto, revisione dei meccanismi, numeri chiave (numeri_*.json), figure in italiano
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
