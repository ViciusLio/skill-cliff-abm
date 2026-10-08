# Sintesi — Fase 2: l'intelligenza artificiale

*Federico Bassi e Vincenzo Lio. Numeri generati da `python scripts/fase2.py`
(N = 50.000, 30 repliche per scenario, seed radice 20261008) e salvati in `report/numeri_fase2.json`.
Versione interattiva: [fase 2 sul sito](https://viciuslio.github.io/skill-cliff-abm/fase2.html).*

## 1. Cosa aggiunge la fase 2

Il modello della fase 1 resta identico. L'IA arriva all'anno 10 e agisce su due canali:
- **sugli incontri:** riduce o potenzia le occasioni di apprendimento, secondo chi sostituisce;
- **sull'output:** aggiunge produttività che cresce nel tempo.

Ogni scenario usa gli stessi numeri casuali dello scenario senza IA (common random numbers):
le differenze sono dovute solo all'IA, e prima dell'anno 10 i risultati sono identici al bit (verificato dai test).

## 2. Equazioni come implementate (`src/skillcliff/ai.py`)

**Produttività dell'IA e quota di compiti automatizzati.** Con $t_0 = 10$:

$$A_t = (1+g)^{\,t-t_0}\ \text{per}\ t\ge t_0,\quad A_t = 1\ \text{prima};\qquad \varphi_t = \varphi_{\max}\left(1 - \frac{1}{A_t}\right).$$

$\varphi$ parte da zero, cresce con A e si satura a $\varphi_{\max}$. Poiché $A_{t_0} = 1$, l'IA agisce dall'anno $t_0 + 1$.

**Bersagli.** L'IA moltiplica i parametri degli incontri di ciascun gruppo di qualifica:

| Bersaglio | Cosa cambia | Lettura |
|---|---|---|
| junior | $p \times (1-\varphi_t)$ in entrambi i gruppi | meno lavoro junior, meno affiancamento |
| senior | $\kappa \times (1-\varphi_t)$ in entrambi i gruppi | meno senior disponibili come mentori |
| qualificati | $p$ e $\kappa$ del gruppo H $\times (1-\varphi_t)$ | sostituzione del lavoro qualificato |
| non qualificati | $p$ e $\kappa$ del gruppo L $\times (1-\varphi_t)$ | sostituzione del lavoro non qualificato |
| complementare | $\beta \times (1+\varphi_t)$ in entrambi i gruppi | l'IA rende più efficace l'insegnamento |

**Output.** Con $H_t = \sum_i h_{i,t}$:

$$Y_t = H_t\,\big[1 + \theta\,(A_t - 1)\big].$$

θ non entra nella dinamica degli agenti: la "corsa" si calcola quindi per qualsiasi θ a partire da $H_t$ e $A_t$, senza nuove simulazioni.

## 3. Parametri

| Parametro | Valore | Criterio |
|---|---|---|
| $t_0$ | 10 | lascia 50 anni di orizzonte dopo l'introduzione |
| $g$ | 3% (griglia 1–6%) | crescita della produttività dell'IA; arbitraria, quindi esplorata |
| $\varphi_{\max}$ | 0,6 | dopo 10 anni $\varphi$ = 0,15, coerente con il −13/16% di occupati di 22–25 anni nelle occupazioni esposte (Brynjolfsson et al. 2025) |
| $\theta$ | 0,02 (griglia 0–0,2) | +0,7% di produttività in 10 anni, come la stima prudente di Acemoglu (2024) |
| N | 50.000 | il modello è invariante alla scala (sez. 6) |

## 4. Risultati

### 4.1 Chi viene sostituito conta

![H per bersaglio](fig/fig6_scenari_H.png)

![h dei senior per bersaglio](fig/fig7_scenari_senior.png)

Variazioni rispetto allo scenario senza IA, a fine orizzonte (50 anni dopo l'introduzione):

| Bersaglio | H | h senior | B da incontri | Y (θ = 0,02) | Gini | Anni al primo effetto sui senior |
|---|---|---|---|---|---|---|
| junior | −5,2% | −4,5% | −45% | +1,0% | 0,163 | 12 |
| non qualificati | −3,2% | −2,8% | −31% | +3,1% | 0,170 | 12 |
| qualificati | −2,0% | −1,7% | −13% | +4,4% | 0,148 | 12 |
| senior | −0,1% | 0,0% | −2% | +6,4% | 0,155 | 42 |
| complementare | +5,2% | +4,3% | +45% | +12,0% | 0,150 | 12 |

*Senza IA il Gini è 0,155.*

1. **Sostituire i junior è il caso peggiore.** H scende del 5,2% e l'apprendimento da incontri quasi si dimezza. Il primo effetto sui senior arriva **12 anni** dopo l'introduzione: un anno perché l'IA inizi ad agire, più gli 11 anni della Proposizione 2.
2. **Sostituire i senior quasi non conta, finché la capacità di mentoring è in eccesso.** Con S/J ≈ 5,7 ci sono più mentori potenziali di quanti ne servano; il vincolo si attiva solo quando $\varphi$ è alto, dopo circa 30 anni. Il risultato dipende da κ (vedi sez. 5).
3. **Bersagliare i non qualificati costa più che bersagliare i qualificati, e aumenta la disuguaglianza.** Il Gini sale a 0,170 se l'IA sostituisce i non qualificati e scende a 0,148 se sostituisce i qualificati. Il motivo principale è il peso: i non qualificati sono il 70% degli entranti.
4. **L'IA complementare è lo specchio della sostituzione dei junior.** Con la stessa intensità $\varphi$, H sale del 5,2% e l'output del 12%.

### 4.2 La corsa

![La corsa](fig/fig8_corsa.png)

Con θ = 0,02 (Acemoglu) e bersaglio junior, **la perdita di capitale umano si mangia circa l'85% del guadagno di produttività dell'IA**:
- senza perdita di H l'output sarebbe +6,5% a fine orizzonte;
- con la skill cliff è +1,0%, quasi fermo (+0,6% / +0,7%) tra 20 e 30 anni dopo l'introduzione.

![Mappa della corsa](fig/fig9_mappa_corsa.png)

| g | H a fine orizzonte | θ di pareggio |
|---|---|---|
| 1% | −2,3% | 0,037 |
| 2% | −4,0% | 0,025 |
| 3% | −5,2% | 0,017 |
| 4% | −6,1% | 0,011 |
| 5% | −6,9% | 0,007 |
| 6% | −7,4% | 0,005 |

- **IA più veloce, perdita più grande.** Una crescita più rapida di A automatizza prima e aumenta la perdita di capitale umano.
- **Ma anche guadagno più grande.** Con A esponenziale, il guadagno di output cresce più in fretta della perdita, che si satura con $\varphi_{\max}$; la soglia θ per andare in pari quindi scende.
- **Con θ = 0** (IA che sostituisce senza aggiungere output) l'output cade esattamente come H.

## 5. Verifiche

**Riprodotto e verificato**
- **Prima dell'introduzione** ogni scenario è identico al bit allo scenario senza IA (test per tutti e 5 i bersagli).
- **Ritardo:** con il bersaglio junior l'h dei senior resta identico per $s_S - s_J$ anni dopo l'inizio dell'effetto, come previsto dalla Proposizione 2 (test).
- **Isolamento dei gruppi:** il bersaglio "qualificati" lascia identici i non qualificati (test).
- **Formule:** A, φ e Y seguono le formule (test).

**Cosa non torna o va discusso**
1. **Il risultato sui senior dipende da κ.** Con κ = 0,2 la capacità di mentoring è abbondante. Con κ più basso (meno senior disposti a insegnare) sostituire i senior diventerebbe costoso: va mostrata la sensibilità.
2. **A cresce senza limiti.** Con A esponenziale e θ > 0 l'IA vince sempre nel lunghissimo periodo; la corsa è interessante sull'orizzonte di una o due generazioni, non all'infinito.
3. **La sostituzione agisce solo sugli incontri.** I junior sostituiti restano nella forza lavoro e continuano a imparare da soli. Un canale occupazionale (junior senza lavoro che non producono e non incontrano) renderebbe gli effetti più forti.
4. **L'IA è esogena.** Nessuna impresa sceglie se automatizzare. Il fallimento di mercato di Ide (automazione socialmente eccessiva) richiede una scelta d'impresa: è il passo successivo.
5. **Il caso complementare è simmetrico per costruzione** (β × (1+φ)). Non c'è il calo di sforzo dei co-pilot descritto da Ide, che lo renderebbe meno favorevole.
6. **θ e g sono incerti.** Per questo sono esplorati su griglia; la stima di Acemoglu è prudente, altre sono molto più alte.

**Scelte arbitrarie:** la forma $\varphi = \varphi_{\max}(1 - 1/A)$; la forma moltiplicativa di Y; $t_0$ = 10; la stessa φ per tutti i bersagli.

## 6. Scala: quanti agenti servono?

Il modello è **invariante alla scala**: gli agenti interagiscono attraverso estrazioni casuali dentro pool grandi, non attraverso reti locali. N riduce solo il rumore.

| N | Repliche | Tempo | B | B da incontri | h senior | Gini |
|---|---|---|---|---|---|---|
| 5.000 | 30 | 0,4 s | 0,06903 | 0,04263 | 2,1568 | 0,1549 |
| 50.000 | 30 | 2,6 s | 0,06898 | 0,04258 | 2,1566 | 0,1547 |
| 500.000 | 10 | 11,4 s | 0,06898 | 0,04258 | 2,1570 | 0,1548 |
| 5.000.000 | 3 | 75 s | 0,06899 | 0,04259 | 2,1569 | 0,1548 |
| **24.000.000** (occupati in Italia) | 1 | 589 s, 2,5 GB | 0,06899 | 0,04259 | 2,1569 | 0,1548 |

Tempi con 4 core: le repliche girano in parallelo, quindi la riga da 24 milioni (una sola replica) ha usato un solo core.
Conclusione: 5.000 agenti sono un campione sufficiente per le medie, 50.000 restringono gli intervalli
di confidenza per i confronti tra scenari; la scala reale è possibile ma non cambia i risultati.

## 7. Decisioni da confermare (formato D: opzione raccomandata e implementata per prima)

- **D11 – Come l'IA riduce gli incontri.**
  - **A (implementata):** moltiplicatore $(1-\varphi_t)$ con $\varphi = \varphi_{\max}(1-1/A)$.
  - B: logistica nel tempo.
- **D12 – Output.**
  - **A (implementata):** $Y = H(1+\theta(A-1))$, una sola forma per tutti i bersagli.
  - B: forme diverse per sostituzione e complementarità (task-based alla Acemoglu).
- **D13 – Junior sostituiti.**
  - **A (implementata per ora):** restano occupati ma incontrano meno.
  - B (raccomandata come estensione): una quota diventa non occupata, non produce e non incontra.
- **D14 – Sensibilità a κ per il bersaglio senior.**
  - **A (raccomandata):** la aggiungo (κ = 0,05; 0,1; 0,2).
- **D15 – Scelta d'impresa sull'automazione** (per misurare l'automazione socialmente eccessiva di Ide).
  - **A (raccomandata):** dopo la revisione di questa sintesi.
