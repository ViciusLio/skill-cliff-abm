# Sintesi — Fase 1: modello base senza IA

*Federico Bassi e Vincenzo Lio. Numeri generati da `python scripts/make_report.py`
(30 repliche per scenario, seed radice 20261008) e salvati in `report/numeri_fase1.json`.*

## 1. Cosa fa il modello

N = 5.000 lavoratori, un periodo = un anno. Ogni lavoratore *i* ha età $a_i$, anni di
esperienza $s_i$, qualifica $q_i\in\{L,H\}$ e capitale umano $h_i$. L'efficienza
dell'apprendimento di Lucas (1988), $B$, **non è un parametro**: si misura come crescita media
di $h$ dei junior e dipende dagli incontri con i senior.

## 2. Equazioni come effettivamente implementate

Ordine degli eventi nell'anno *t* (`src/skillcliff/model.py`):

1. **Invecchiamento.** Ogni lavoratore presente invecchia di un anno:
   $a_{i,t} = a_{i,t-1} + 1$ e $s_{i,t} = s_{i,t-1} + 1$.
2. **Pensionamento.** Esce chi ha $a_{i,t} \ge 65$. L'ultima età lavorata è quindi 64 anni.
3. **Ingresso.** Entrano tanti lavoratori quanti sono usciti, quindi N resta costante. Per ciascun entrante:
   - è qualificato con probabilità $q=0{,}30$;
   - entra con $s=0$, a 20 anni se non qualificato e a 25 se qualificato (nell'anno d'ingresso non invecchia);
   - parte con capitale umano

$$h_{i,0} = \bar h_0(q_i)\, e^{\varepsilon_i},\qquad \varepsilon_i\sim\mathcal N(-\sigma^2/2,\ \sigma^2),\qquad \bar h_0(L)=1{,}0,\ \bar h_0(H)=1{,}5.$$

4. **Ruoli**, in base all'esperienza: junior se $s<5$, senior se $s\ge 15$.
5. **Incontri** (`learning.py`), per gruppo di qualifica $g\in\{L,H\}$ (decisione D1). Con $J_g$ junior e $S_g$ senior del gruppo:

$$p^{\text{eff}}_{g,t} = \min\!\left(p,\ \kappa\,\frac{S_{g,t}}{J_{g,t}}\right),$$

   cioè incontri = min(domanda $pJ_g$, capacità $\kappa S_g$). Ogni junior *j* incontra con probabilità $p^{\text{eff}}_{g,t}$ un senior *k* della **propria qualifica**, estratto uniformemente, e guadagna

$$\Delta h^{\text{inc}}_{j,t} = \beta\,\max(0,\ h_{k,t} - h_{j,t}).$$

   Il senior non perde nulla dall'incontro.

6. **Apprendimento autonomo e obsolescenza** (alla Ben-Porath), per tutti:

$$\Delta h^{\text{aut}}_{i,t} = \big[\delta(s_{i,t}) - d\big]\,h_{i,t},\qquad \delta(s) = \delta_0\,\max\!\left(0,\ 1-\frac{s}{S_h}\right).$$

7. **Aggiornamento simultaneo.** $h_{i,t+1} = h_{i,t} + \Delta h^{\text{inc}}_{i,t} + \Delta h^{\text{aut}}_{i,t}$, con entrambi i termini calcolati sull'$h$ di inizio anno. Vale $h\ge 0$ perché $d<1$.
8. **Output e salari.** $Y_t=\sum_i h_{i,t}$ e $w_i = h_i$ (prodotto marginale).
9. **B emergente.** Crescita relativa media dei junior, scomposta in due parti:

$$B_t = \underbrace{\tfrac{1}{J_t}\textstyle\sum_{j}\tfrac{\Delta h^{\text{inc}}_{j,t}}{h_{j,t}}}_{B^{\text{inc}}_t} + \underbrace{\tfrac{1}{J_t}\textstyle\sum_{j}\tfrac{\Delta h^{\text{aut}}_{j,t}}{h_{j,t}}}_{B^{\text{aut}}_t}.$$

   Nella notazione di Lucas, $\dot h = B(1-u)h$ con tutto il tempo di apprendimento normalizzato a uno.

**Riproducibilità.**
- La replica *r* usa `SeedSequence(seed).spawn(30)[r]`.
- Gli stream per demografia e incontri sono separati.
- Gli scenari con lo stesso seed condividono le estrazioni casuali.
- Burn-in di 300 anni, poi 60 anni registrati; intervalli di confidenza (IC) al 95% con t di Student tra repliche. (Con 120 anni, il valore iniziale, restava una deriva dello 0,4% nei livelli; i confronti tra scenari non cambiavano.)

## 3. Parametri

| Parametro | Valore | Fonte / criterio | Arbitrario? |
|---|---|---|---|
| N | 5.000 | specifica | — |
| Età d'ingresso | 20 / 25 | i laureati italiani entrano tardi | approssimato |
| Pensionamento | 65 | uscita effettiva media 64,8 anni (Italia, 2024) | approssimato |
| Quota qualificati $q$ | 0,30 | ~30% di laureati tra i 25–34enni | approssimato |
| $\bar h_0$ | 1,0 / 1,5 | premio salariale d'ingresso dei laureati ~50% | **sì** (normalizzazione) |
| $\sigma$ | 0,20 | — | **sì** |
| Junior / senior | $s<5$ / $s\ge 15$ | evidenza sull'IA e il lavoro entry-level; 10/20 come robustezza | scelta condivisa |
| Incontri | stessa qualifica | si impara da chi fa il proprio mestiere (D1) | scelta condivisa |
| $p$ | 0,6 | — | **sì**; conta soprattutto il prodotto con β |
| $\kappa$ | 0,2 | un senior su cinque fa da mentore ogni anno (D4) | **sì** |
| $\beta$ | 0,10 | $B^{inc}\approx 4$–9% (Jarosch et al. 2021) | calibrato |
| $\delta_0,\ S_h,\ d$ | 0,040 / 50 / 0,012 | profilo concavo con picco tardo e calo lieve | calibrati |

## 4. Risultati

### 4.1 h medio per classe d'età nel tempo

![h per classe d'età](fig/fig1_h_per_classe_eta.png)

(a) Stato stazionario. (b) **Esperimento di meccanismo, non uno scenario IA**: dall'anno 10 la probabilità d'incontro *p* viene dimezzata, per isolare il canale su cui agirà l'IA.

- **Junior:** −5,7% di h dopo 4 anni.
- **Senior:** variazione **esattamente nulla per 10 anni**; primo effetto all'**11° anno**, come previsto dalla Proposizione 2 (sez. 5); −3,6% dopo 25 anni; −6,7% a regime.
- **Output:** −7,2% a regime.
- **Classi d'età:** il calo supera lo 0,5% subito per i 20–29enni e dopo circa 4, 14, 24 e 33 anni per le classi successive (30–39, 40–49, 50–59, 60–64).

### 4.2 B emergente

![B emergente](fig/fig2_B_emergente.png)

**A regime:** $B$ = 0,0693 (IC [0,0692; 0,0694]). Di questo, $B^{inc}$ = 0,0429 (62%) e $B^{aut}$ = 0,0264.

**Dopo lo shock**, $B^{inc}$ si dimezza (da 0,043 a 0,021) e poi segue due fasi:
- **sale** fino a 0,025 nei 5–20 anni successivi, perché i junior partono più in basso e il divario da colmare è più grande;
- **scende** a 0,020 cinquant'anni dopo, quando i senior formati con meno incontri diventano gli insegnanti.

B ha quindi memoria della storia degli incontri: è una variabile di stato, non una costante.

### 4.3 Profilo salariale per età

![Profilo salariale](fig/fig3_profilo_salariale.png)

| | Picco (età / esperienza) | Picco / ingresso | Calo finale dal picco |
|---|---|---|---|
| Non qualificati | 54 / 34 anni | 1,84 | −3,6% |
| Qualificati | 60 / 35 anni | 1,84 | −0,8% |

### 4.4 Disuguaglianza

![Gini](fig/fig4_gini.png)

Il Gini dei salari a regime è 0,155 (IC [0,1547; 0,1553]) e sale a 0,165 dopo il dimezzamento degli incontri: gli incontri comprimono la disuguaglianza.

### 4.5 Sensibilità a p e κ

![Sensibilità](fig/fig5_sensibilita_p_kappa.png)

- $B^{inc}$ cresce in modo più che lineare con *p* finché il vincolo $p > \kappa S/J$ non diventa attivo.
- A regime $S/J = 5{,}71$: con $\kappa=0{,}2$ il vincolo non è attivo e lo diventerebbe solo se $S/J$ scendesse sotto 3.

### 4.6 Robustezza: soglie 10/20 (decisione D5)

| | Base 5/15 | Robustezza 10/20 |
|---|---|---|
| $B$ | 0,0693 | 0,0574 |
| $B^{inc}$ | 0,0429 | 0,0330 |
| Picco / ingresso (non qual. / qual.) | 1,84 / 1,84 | 2,08 / 1,95 |
| Esperienza al picco | 34–35 anni | 34 anni |
| Ritardo previsto / osservato | 11 / 11 | 11 / 11 |
| h senior a regime, p dimezzato | −6,7% | −6,6% |
| Output a regime, p dimezzato | −7,2% | −7,2% |

- Il ritardo dipende dalla **distanza** tra le soglie ($s_S - s_J + 1$), non dal loro livello: con 5/15 e con 10/20 è sempre 11 anni.
- Gli effetti a regime cambiano poco.
- $B$ è più basso con 10/20 perché tra i junior ci sono più lavoratori già lontani dall'ingresso, con meno da imparare.

### 4.7 Docking NumPy ↔ Mesa

Gemello in Mesa 3.5 (`src/skillcliff/mesa_twin.py`), scritto indipendentemente con un oggetto per agente; N = 1.000, 20 repliche ciascuno:

| Metrica | NumPy | Mesa | Diff. | p (Welch) |
|---|---|---|---|---|
| h medio | 1,9907 | 1,9897 | −0,05% | 0,82 |
| h junior | 1,4166 | 1,4150 | −0,11% | 0,66 |
| h senior | 2,1641 | 2,1630 | −0,05% | 0,82 |
| $B^{inc}$ | 0,0428 | 0,0429 | +0,27% | 0,59 |
| $B^{aut}$ | 0,0264 | 0,0264 | 0,00% | 0,86 |

Nessuna differenza è significativa.

## 5. Dal micro al macro: due proposizioni

**Proposizione 1 (B emergente).** Con incontri casuali dentro ciascun gruppo di qualifica *g*, e con tutte le grandezze misurate a inizio anno,

$$\mathbb E[B^{inc}_t] = \sum_g \frac{J_g}{J}\,\beta\,p^{\text{eff}}_{g,t}\left[\bar h^S_{g,t}\;\overline{h^{-1}}^{\,J}_{g,t} - 1 + \Omega_{g,t}\right],\qquad \Omega_{g,t} = \frac{1}{J_g S_g}\sum_{j,k\in g}\frac{\max(0,h_j-h_k)}{h_j}\ge 0.$$

- La dimostrazione usa $\max(0,x) = x + \max(0,-x)$.
- Verifica numerica: l'identità dà **0,0437** contro **0,0434** simulato.
- Usare il rapporto delle medie ($\bar h^S/\bar h^J$) al posto della media degli inversi sottostima B di circa il 9% (0,0395): la dispersione dei junior conta.

**Proposizione 2 (ritardo di trasmissione).** Se le opportunità d'incontro cambiano in modo permanente all'anno $t_0$ e i senior non imparano dagli incontri, l'h medio dei senior resta invariato fino a $t_0 + s_S - s_J$ e cambia da $t_0 + s_S - s_J + 1$.

- Motivo: chi è junior a $t_0$ ha al massimo $s_J - 1$ anni di esperienza, quindi diventa senior dopo almeno $s_S - s_J + 1$ anni.
- Osservato: 11 anni, sia con 5/15 sia con 10/20.

## 6. Verifiche

**Riprodotto**
- **Profilo salariale.** Concavo, che sale lentamente e si appiattisce (picco a 34–35 anni di esperienza, calo finale tra −1% e −4%): coerente con il settore privato italiano.
- **Apprendimento dai colleghi.** $B^{inc}$ = 4,3% del salario dei junior l'anno, dentro l'intervallo 4–9% di Jarosch et al. (2021); la mappatura è solo indicativa (vedi sotto).
- **B emergente con memoria.** Dipende da *p*, κ, β e dalla distribuzione di *h*.
- **Ritardo esatto.** Previsto e osservato coincidono (11 anni), e la Proposizione 1 è verificata numericamente.
- **Invarianti** (test automatici):
  - N conservato e $h\ge0$;
  - *p*=0 ⇒ nessun apprendimento da incontri;
  - stesso seed ⇒ risultati identici;
  - demografia identica tra scenari;
  - identificativi unici;
  - ogni incontro avviene tra un junior e un senior della stessa qualifica.

**Non torna**
1. **Profili per qualifica uguali (1,84 e 1,84).** Lagakos et al. (2018) trovano profili più ripidi per chi ha istruzione alta. Con D1 la pendenza invertita è sparita ma non si è rovesciata. Per riprodurla servirebbe un apprendimento autonomo diverso per qualifica (D2), che per ora escludiamo per tenere il modello essenziale.
2. **Gini basso (0,155).** Nei dati è circa 0,3 (ordine di grandezza da verificare su INPS): nel modello il salario dipende solo da *h*. Non è un obiettivo di calibrazione (D3).
3. **Nessuna crescita di lungo periodo.** Con $h_0$ fisso l'economia è stazionaria: c'è B, non c'è crescita endogena alla Lucas.
4. **Nessuna scogliera spontanea nel caso base.** Con demografia stazionaria S/J è costante e κ non è mai attivo: la skill cliff richiede uno shock (l'IA, oppure la piramide demografica italiana).
5. **Mappatura con Jarosch et al. indicativa.** Loro misurano l'apprendimento da tutti i colleghi sulla retribuzione di tutti; qui solo quello dei junior dai senior.

**Scelte arbitrarie**
- La forma lineare di δ(s).
- *p* e β presi separatamente.
- κ = 0,2.
- La normalizzazione di $\bar h_0$ e σ.
- Il senior estratto uniformemente nel gruppo; al massimo un incontro l'anno.
- Il pensionamento deterministico a 65 anni.
- w = h.

## 7. Decisioni prese

| | Decisione |
|---|---|
| D1 | incontri dentro la stessa qualifica |
| D2 | nessun apprendimento autonomo diverso per qualifica |
| D3 | Gini non calibrato |
| D4 | κ = 0,2 |
| D5 | robustezza 10/20 inclusa (sez. 4.6) |
| D9 | articolo in inglese; README, sintesi e lezione in italiano |
