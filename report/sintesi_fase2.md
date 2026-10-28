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

**Bersagli e margini (D16, D17).** Il bersaglio dice chi viene sostituito; il margine
(`ai.margin_junior`, `ai.margin_senior`) dice che cosa vuol dire "sostituire". Dettagli nella sez. 8.

| Bersaglio | Cosa cambia (margine "compiti", default) | Lettura |
|---|---|---|
| junior | $p \times (1-\varphi_t)$ in entrambi i gruppi | meno lavoro junior, meno affiancamento |
| senior | $\beta \times (1-\varphi_t)$ in entrambi i gruppi | ogni incontro trasmette meno |
| qualificati | $p$ e $\beta$ del gruppo H $\times (1-\varphi_t)$ | sostituzione del lavoro qualificato |
| non qualificati | $p$ e $\beta$ del gruppo L $\times (1-\varphi_t)$ | sostituzione del lavoro non qualificato |
| complementare | $\beta \times (1+\varphi_t)$ in entrambi i gruppi | l'IA rende più efficace l'insegnamento |

Con il margine "posto" i junior colpiti diventano non occupati (D13) e i senior colpiti escono:
$\kappa \times (1-\varphi_t)$, meno mentori.

**Output.** Con $H_t = \sum_i h_{i,t}$:

$$Y_t = H_t\,\big[1 + \theta\,(A_t - 1)\big].$$

θ non entra nella dinamica degli agenti: la "corsa" si calcola quindi per qualsiasi θ a partire da $H_t$ e $A_t$, senza nuove simulazioni.

**Junior che perdono il posto (D13, ora `ai.margin_junior: posto`).** La sostituzione dei junior non riduce p: ogni anno
una quota $\varphi_t$ dei junior del gruppo colpito è senza lavoro. Un junior non occupato non incontra senior e non
impara sul lavoro; resta solo l'obsolescenza, $\Delta h_{i,t} = -d\,h_{i,t}$. I suoi compiti li svolge l'IA, quindi
l'output corrente non cambia: la perdita passa solo per il capitale umano. Le estrazioni per la non occupazione
usano un flusso di numeri casuali dedicato, così gli altri flussi restano allineati con lo scenario senza IA.
Con D19 l'anno da non occupato non conta come esperienza (sez. 8).

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

| Scenario | H | h senior | B da incontri | Y (θ = 0,02) | Gini | Anni al primo effetto sui senior |
|---|---|---|---|---|---|---|
| junior, compiti (p ↓) | −5,2% | −4,5% | −45% | +0,9% | 0,163 | 12 |
| junior, posto (non occupati) | −5,7% | −1,9% | −44% | +0,4% | 0,168 | 12 |
| senior, compiti (β ↓) | −5,2% | −4,5% | −45% | +0,9% | 0,161 | 12 |
| senior, posto (κ ↓) | −0,1% | 0,0% | −2% | +6,4% | 0,155 | 44 |
| non qualificati (p e β del gruppo L ↓) | −5,5% | −5,0% | −49% | +0,7% | 0,180 | 12 |
| qualificati (p e β del gruppo H ↓) | −3,3% | −2,9% | −21% | +3,0% | 0,144 | 12 |
| complementare (β ↑) | +5,2% | +4,3% | +45% | +12,0% | 0,150 | 12 |

*Senza IA il Gini è 0,155. Per i junior che perdono il posto, B da incontri è la media su tutti i junior, compresi i non occupati.*

1. **Sostituire i compiti dei junior o quelli dei senior costa lo stesso.** H scende del 5,2% in entrambi i casi e l'apprendimento da incontri quasi si dimezza: p e β entrano come prodotto nella Proposizione 1. Cambia solo la distribuzione: il Gini è 0,163 se l'IA toglie incontri ai junior, 0,161 se toglie efficacia ai senior (sez. 8). Il primo effetto sui senior arriva **12 anni** dopo l'introduzione: un anno perché l'IA inizi ad agire, più gli 11 anni della Proposizione 2.
2. **I senior che perdono il posto contano solo se i mentori sono scarsi.** Con κ = 0,2 e S/J ≈ 5,7 ci sono più mentori potenziali di quanti ne servano: il vincolo si attiva dopo circa 30 anni e l'effetto a fine orizzonte è quasi nullo. Con κ = 0,1, dove la capacità è già al limite, la stessa sostituzione costa −4,8% di capitale umano, quasi quanto sostituire i compiti (sez. 4.3).
3. **Bersagliare i non qualificati costa più che bersagliare i qualificati, e aumenta la disuguaglianza.** Il Gini sale a 0,180 se l'IA sostituisce i non qualificati e scende a 0,144 se sostituisce i qualificati. Il motivo principale è il peso: i non qualificati sono il 70% degli entranti. Questi due scenari tagliano insieme p e β del gruppo, quindi l'apprendimento da incontri del gruppo scala con $(1-\varphi)^2$: i non qualificati perdono più del bersaglio junior (−5,5% contro −5,2%).
4. **L'IA complementare è lo specchio della sostituzione dei compiti.** Con la stessa intensità $\varphi$, H sale del 5,2% e l'output del 12%.
5. **Se i junior perdono il posto, la formazione è rinviata, non persa.** Con D19 un anno da non occupato non conta come esperienza: il junior resta junior finché non ha lavorato 5 anni. H scende del 5,7%, poco più che con la perdita di compiti; a fine orizzonte i junior sono 10.200 invece di 5.800 e i senior 29.300 invece di 32.800 (N = 50.000). L'h medio dei senior cala solo dell'1,9% perché chi arriva a senior ha avuto la formazione completa, solo più tardi: il costo è nelle carriere più brevi. Con θ = 0,02 l'output resta sopra lo scenario senza IA (+0,4%); la soglia di pareggio è 0,019 (0,017 con la perdita di compiti). Prima di D19 lo stesso scenario dava −10,2%.

### 4.3 Sensibilità a κ per i senior che perdono il posto (D14)

| κ | p effettiva senza IA | H a fine orizzonte | h senior | Primo effetto su H |
|---|---|---|---|---|
| 0,05 | 0,29 (vincolo attivo) | −2,3% | −2,0% | subito |
| 0,1 | 0,57 (vincolo appena attivo) | −4,8% | −4,2% | subito |
| 0,2 | 0,60 (vincolo inattivo) | −0,1% | 0,0% | dopo 33 anni |

Con κ = 0,05 la perdita è minore che con 0,1 perché gli incontri sono già pochi senza IA: c'è meno da perdere.
Il dato empirico che servirebbe è quanti senior fanno davvero da mentori.

### 4.2 La corsa

![La corsa](fig/fig8_corsa.png)

Con θ = 0,02 (Acemoglu) e bersaglio junior, **la perdita di capitale umano si mangia circa l'86% del guadagno di produttività dell'IA**:
- senza perdita di H l'output sarebbe +6,5% a fine orizzonte;
- con la skill cliff è +0,9%, quasi fermo (+0,6%) tra 20 e 30 anni dopo l'introduzione.

![Mappa della corsa](fig/fig9_mappa_corsa.png)

| g | H a fine orizzonte | θ di pareggio |
|---|---|---|
| 1% | −2,3% | 0,037 |
| 2% | −4,0% | 0,025 |
| 3% | −5,2% | 0,017 |
| 4% | −6,2% | 0,011 |
| 5% | −6,9% | 0,007 |
| 6% | −7,5% | 0,005 |

- **IA più veloce, perdita più grande.** Una crescita più rapida di A automatizza prima e aumenta la perdita di capitale umano.
- **Ma anche guadagno più grande.** Con A esponenziale, il guadagno di output cresce più in fretta della perdita, che si satura con $\varphi_{\max}$; la soglia θ per andare in pari quindi scende.
- **Con θ = 0** (IA che sostituisce senza aggiungere output) l'output cade esattamente come H.

### 4.4 Automazione scelta dall'impresa contro ottimo sociale (D15)

Script `scripts/automazione.py`, numeri in `report/numeri_d15.json`, figura sotto.

**Impostazione.** Dall'anno 10 una quota costante φ dei compiti junior è automatizzata ($p\times(1-\varphi)$).
L'output netto relativo allo scenario senza automazione è

$$y_t(\varphi) = r_t(\varphi)\left(1 + \pi\varphi - \tfrac{c}{2}\varphi^2\right),\qquad r_t(\varphi) = \frac{H_t(\varphi)}{H_t(0)},$$

con guadagno pieno dell'automazione π = 0,10 e costo di adozione c = 1/3.
- **L'impresa** prende il capitale umano come dato: i contratti di trasmissione della conoscenza sono incompleti (Ide 2026) e chi forma un junior non ne cattura il valore futuro. Sceglie quindi $\varphi = \pi/c = 0{,}30$.
- **Il pianificatore** massimizza $\sum_k \rho^{k+1} y_{t_0+k}(\varphi)$ su un orizzonte dato, con $r_t(\varphi)$ misurato dal modello (griglia di φ, 10 repliche per punto, N = 50.000).

![Automazione: impresa contro pianificatore](fig/fig10_automazione.png)

| ρ | Orizzonte | φ ottimo | Eccesso di automazione | Valore della scelta dell'impresa | Valore dell'ottimo |
|---|---|---|---|---|---|
| 0,97 | 10 anni | 0,251 | 0,049 | +1,02% | +1,06% |
| 0,97 | 25 anni | 0,185 | 0,115 | +0,36% | +0,58% |
| 0,97 | 50 anni | 0,088 | 0,212 | **−0,62%** | +0,14% |
| 0,99 | 50 anni | 0,045 | 0,255 | **−1,11%** | +0,04% |

*Valori: output netto scontato rispetto a nessuna automazione.*

1. **L'impresa automatizza troppo, e l'eccesso cresce con l'orizzonte.** Su 10 anni l'eccesso è piccolo (0,05), perché il danno sui senior arriva solo dopo 11 anni (Proposizione 2): chi guarda a dieci anni, come un bilancio o un ciclo politico, sceglie quasi come l'impresa.
2. **Su 50 anni la scelta privata è peggiore di non automatizzare affatto** (−0,6% con ρ = 0,97). Il guadagno immediato è più che compensato dalla perdita di capitale umano.
3. **I valori di π e c sono illustrativi**: determinano il livello di φ scelto dall'impresa, non il segno dell'eccesso, che deriva solo dal fatto che l'impresa non vede $r_t(\varphi)$.

## 5. Verifiche

**Riprodotto e verificato**
- **Prima dell'introduzione** ogni scenario è identico al bit allo scenario senza IA (test per tutti e 5 i bersagli).
- **Tabella 2×2:** ogni combinazione di bersaglio e margine produce i moltiplicatori attesi e la non occupazione solo con il margine "posto" (test). Le verifiche specifiche di D16, D17 e D19 sono nella sez. 8.
- **Ritardo:** con il bersaglio junior l'h dei senior resta identico per $s_S - s_J$ anni dopo l'inizio dell'effetto, come previsto dalla Proposizione 2 (test).
- **Isolamento dei gruppi:** il bersaglio "qualificati" lascia identici i non qualificati (test).
- **Formule:** A, φ e Y seguono le formule (test).

**Cosa non torna o va discusso**
1. **Il risultato sui senior che perdono il posto dipende da κ** (sez. 4.3). Senza una misura empirica della capacità di mentoring va presentato come un intervallo: da quasi nullo a −4,8%. Sui senior che perdono compiti κ non conta.
2. **A cresce senza limiti.** Con A esponenziale e θ > 0 l'IA vince sempre nel lunghissimo periodo; la corsa è interessante sull'orizzonte di una o due generazioni, non all'infinito.
3. **Due modi di sostituire i junior.** Nella versione "compiti" restano occupati e incontrano meno; nella versione "posto" restano senza lavoro e la formazione è rinviata (sez. 8). La realtà sta probabilmente in mezzo: chi non entra in un'impresa esposta trova spesso lavoro altrove, con meno apprendimento.
4. **L'IA è esogena.** Nessuna impresa sceglie se automatizzare. Il fallimento di mercato di Ide (automazione socialmente eccessiva) richiede una scelta d'impresa: è il passo successivo.
5. **Il caso complementare è simmetrico per costruzione** (β × (1+φ)). Non c'è il calo di sforzo dei co-pilot descritto da Ide, che lo renderebbe meno favorevole.
6. **θ e g sono incerti.** Per questo sono esplorati su griglia; la stima di Acemoglu è prudente, altre sono molto più alte.

**Stabilità numerica (controlli dell'8 ottobre)**
- **Burn-in (risolto).** Con 120 anni la convergenza non era completa, perché ogni generazione impara dalla precedente: restava una deriva relativa di +1,0·10⁻⁴ l'anno e i livelli erano più bassi dello 0,4%. Il burn-in è ora di 300 anni (deriva −0,9·10⁻⁵ l'anno) e tutti i numeri sono stati rigenerati. I confronti tra scenari erano già robusti (H con bersaglio junior: −5,20% con 120 anni, −5,24% con 300, −5,23% con 480).
- **Esistenza dello stato stazionario.** Con parametri estremi (p = 1, κ = 1, β = 0,5) il capitale umano cresce senza limite: gli incontri diventano un motore di crescita endogena alla Lucas. Con la calibrazione di base l'economia è stazionaria. La soglia tra i due regimi va caratterizzata (analiticamente con la Proposizione 1, o numericamente su una griglia di p e β).
- **Robustezza dei risultati.** Invarianza alla scala (5 mila – 24 milioni), docking con Mesa, seed diversi (IC al 95% molto stretti), soglie 10/20: le conclusioni qualitative non cambiano.

**Scelte arbitrarie:** la forma $\varphi = \varphi_{\max}(1 - 1/A)$; la forma moltiplicativa di Y; $t_0$ = 10; la stessa φ per tutti i bersagli.

## 6. Scala: quanti agenti servono?

Il modello è **invariante alla scala**: gli agenti interagiscono attraverso estrazioni casuali dentro pool grandi, non attraverso reti locali. N riduce solo il rumore.

| N | Repliche | Tempo | B | B da incontri | h senior | Gini |
|---|---|---|---|---|---|---|
| 5.000 | 30 | 0,6 s | 0,06933 | 0,04293 | 2,1667 | 0,1550 |
| 50.000 | 30 | 4,2 s | 0,06934 | 0,04294 | 2,1653 | 0,1548 |
| 500.000 | 10 | 19 s | 0,06935 | 0,04295 | 2,1659 | 0,1549 |
| 5.000.000 | 3 | 137 s | 0,06933 | 0,04293 | 2,1654 | 0,1548 |
| **24.000.000** (occupati in Italia) | 1 | 18 min, 2,4 GB | 0,06933 | 0,04293 | 2,1656 | 0,1549 |

Tempi con 4 core: le repliche girano in parallelo, quindi la riga da 24 milioni (una sola replica) ha usato un solo core.
Conclusione: 5.000 agenti sono un campione sufficiente per le medie, 50.000 restringono gli intervalli
di confidenza per i confronti tra scenari; la scala reale è possibile ma non cambia i risultati.

## 7. Decisioni (formato D: opzione raccomandata per prima)

- **D11 – Come l'IA riduce gli incontri.**
  - **A (implementata):** moltiplicatore $(1-\varphi_t)$ con $\varphi = \varphi_{\max}(1-1/A)$.
  - B: logistica nel tempo.
- **D12 – Output.**
  - **A (implementata):** $Y = H(1+\theta(A-1))$, una sola forma per tutti i bersagli.
  - B: forme diverse per sostituzione e complementarità (task-based alla Acemoglu).
- **D13 – Junior sostituiti.** Fatto: la versione base (restano occupati, incontrano meno) resta il riferimento; la variante "non occupati" è implementata, testata e riportata accanto (sez. 4.1). Con D16 è diventata il margine "posto" dei junior.
- **D14 – Sensibilità a κ per il bersaglio senior.** Fatta (sez. 4.3).
- **D15 – Scelta d'impresa sull'automazione.** Fatto (sez. 4.4): l'eccesso di automazione va da 0,05 (orizzonte di 10 anni) a 0,21 (50 anni).
- **D16 – Che cosa vuol dire "sostituire".** **A (implementata):** tabella 2×2 esplicita, margine "compiti" o "posto" per junior e senior (sez. 8).
- **D17 – Compiti dei senior.** **A (implementata):** β ↓; κ resta solo nel margine "posto". L'equivalenza media con p è un risultato (sez. 8).
- **D18 – Produttività e familiarità con l'IA.** Da decidere.
- **D19 – Esperienza solo da occupati.** **A (implementata)** (sez. 8).
- **D20 – Mentore stabile.** Da decidere.

## 8. Revisione dei meccanismi: D16, D17, D19

Origine: le osservazioni di Federico in [`revisione_meccanismi.md`](revisione_meccanismi.md).

### 8.1 Equazioni come implementate

**Esperienza (D19, `src/skillcliff/model.py`).** Con $u_{i,t} = 1$ se il lavoratore $i$ è non occupato nell'anno $t$:

$$s_{i,t+1} = s_{i,t} + (1 - u_{i,t}),\qquad a_{i,t+1} = a_{i,t} + 1 .$$

Il ruolo (junior se $s<5$, senior se $s\ge 15$) e l'apprendimento autonomo $\delta(s)$ dipendono da $s$, il pensionamento
dall'età. Un anno fuori quindi rinvia la formazione da junior e accorcia la carriera. Senza non occupazione $u = 0$ e
$s = a - a^{\text{ingresso}}$ come prima.

**Sostituzione (D16, D17, `src/skillcliff/ai.py`).** Per il gruppo di qualifica $g$ colpito dal bersaglio:

| | compiti (resta al lavoro) | posto (lo perde) |
|---|---|---|
| **junior** | $p_g \times (1-\varphi_t)$ | $u_{i,t} = 1$ con probabilità $\varphi_t$ |
| **senior** | $\beta_g \times (1-\varphi_t)$ | $\kappa_g \times (1-\varphi_t)$ |

L'apprendimento medio da incontri dei junior è $p^{\text{eff}}\,\beta\,\mathbb{E}[\max(0, h_s - h_j)]$
(Proposizione 1), con $p^{\text{eff}} = \min(p, \kappa S/J)$. Il margine "compiti" tocca $p$ o $\beta$, che entrano come
prodotto: stesso effetto medio. Il margine "posto" dei senior tocca $\kappa$, che conta solo se il vincolo è attivo.

**Riproducibilità.** I risultati precedenti si riottengono con: senior di prima = senior con `margin_senior: posto`;
qualificati e non qualificati di prima = `margin_junior: compiti`, `margin_senior: posto`; `ai.displacement` di prima =
`margin_junior: posto`. Verificato bit per bit su tutti e sette gli scenari di prima (N = 3.000).

### 8.2 Numeri (N = 50.000, 30 repliche, fine orizzonte)

**Compiti junior contro compiti senior (D17).** Differenze accoppiate per replica (`simmetria_compiti` in `numeri_fase2.json`):

| | junior, compiti (p ↓) | senior, compiti (β ↓) | differenza (IC 95%) |
|---|---|---|---|
| H | −5,24% | −5,24% | 0,002 punti [−0,007; +0,011] |
| Gini | 0,1635 | 0,1610 | 0,0024 [0,0024; 0,0025] |

Lo stesso risultato con uno shock secco (`make simmetria`, 10 repliche, N = 5.000): p dimezzato H −8,73%, Gini 0,165;
β dimezzato H −8,77%, Gini 0,162. Meno incontri: alcuni junior imparano e altri no. Meno efficacia: imparano tutti un po' meno.

**Junior che perdono il posto, prima e dopo D19:**

| | prima di D19 | con D19 |
|---|---|---|
| H | −10,2% | −5,7% |
| h senior | −8,8% | −1,9% |
| B da incontri | −46% | −44% |
| Y (θ = 0,02) | −4,3% | +0,4% |
| Gini | 0,170 | 0,168 |
| θ di pareggio | 0,035 circa | 0,019 |

Prima di D19 un junior rimasto fuori per 5 anni diventava "intermedio" senza aver mai incontrato un senior, e
15 anni dopo l'ingresso era senior: la formazione era persa. Con D19 è rinviata: ogni junior lavora 5 anni da junior
prima di passare oltre, ma lo fa più tardi e con meno anni di carriera davanti.

### 8.3 Verifiche

**Riprodotto e verificato**
- **Base identica bit per bit dopo D19:** senza non occupazione nessun output cambia (confronto prima/dopo su base e
  5 bersagli; test: senza IA $s = a - a^{\text{ingresso}}$ in ogni anno).
- **D19:** chi è stato non occupato in un anno non accumula esperienza in quell'anno, gli altri sì (test che segue
  ogni agente per identificativo).
- **Tabella 2×2:** moltiplicatori e non occupazione per ogni combinazione di bersaglio e margine (test).
- **Equivalenza media:** compiti junior e compiti senior danno lo stesso H (IC della differenza include lo zero) e Gini
  diversi (IC esclude lo zero); test a N piccolo con tolleranza del 15%.
- **Docking con Mesa:** la base non cambia, quindi il docking resta valido. Il gemello Mesa non ha l'IA: D16, D17 e D19
  restano fuori dal docking.

**Cosa non torna o va discusso**
1. **Con D19 il "posto" dei junior costa molto meno di prima** (−5,7% invece di −10,2%). Il numero vecchio era gonfiato
   dall'incoerenza che D19 corregge. Resta però un'ipotesi forte: ogni anno la non occupazione è estratta di nuovo,
   indipendentemente dagli anni precedenti; chi è stato fuori non ha meno probabilità di essere assunto (nessuna
   cicatrice oltre agli anni persi). Una persistenza della non occupazione aumenterebbe il danno.
2. **L'h medio dei senior è una misura di composizione.** Con D19 i senior sono meno (29.300 contro 32.800) ma hanno
   avuto la formazione completa: l'h medio dei senior sottostima il danno. Conta H.
3. **Gli scenari per qualifica sono cambiati** (qualificati −2,0% → −3,3%, non qualificati −3,3% → −5,5%; Gini 0,148 →
   0,144 e 0,170 → 0,180), perché con il margine "compiti" tagliano p e β del gruppo, non più p e κ. Il taglio doppio
   pesa $(1-\varphi)^2$ sull'apprendimento del gruppo: confrontarli con il bersaglio junior richiede attenzione.
4. **L'output del margine "compiti" è lo stesso per junior e senior.** La differenza di produttività che Federico
   suggerisce (junior formati all'IA, senior meno abituati) è D18, non ancora implementata.
