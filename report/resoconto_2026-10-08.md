# Resoconto della giornata — 8 ottobre 2026

*Federico Bassi e Vincenzo Lio. Stato del lavoro alla chiusura della fase 1.*

## 1. In breve

In una giornata abbiamo costruito, verificato e documentato il modello base senza IA.

Il modello mostra che l'efficienza dell'apprendimento B **emerge** dagli incontri tra junior e
senior e ha memoria della loro storia. Una riduzione degli incontri resta **invisibile** nel
capitale umano dei senior per `s_S − s_J` anni (10 con le soglie 5/15) e poi lo erode in modo
cumulativo: −6,7% a regime se gli incontri si dimezzano.

Tutto questo è nel repository: codice testato, articolo in bozza, sintesi tecnica, sito
pubblicato e verificato automaticamente, ambiente Codespaces pronto per Federico.

## 2. Cronologia

| Ora | Commit | Cosa |
|---|---|---|
| 06:47 | `9bee574` | Scheletro del progetto, parametri in YAML |
| 06:49 | `46a4b8a` | Dinamica annuale: demografia, incontri junior-senior, apprendimento autonomo; test degli invarianti |
| 06:49 | `80a802a` | Repliche con seed derivati, salvataggio dei risultati |
| 06:51 | `5dd3969` | Gemello in Mesa per il docking; capacità di mentoring κ = 0,2 |
| 06:54 | `d7dd1cd` | Esperimento di meccanismo ("p dimezzato"), figure della fase 1 |
| 06:56 | `5498412` | Prima sintesi, README, devcontainer |
| 06:58 | `3423c6b` | Report interattivo su GitHub Pages, CI dei test |
| 06:58–06:59 | `53366af`, `9c7f4e0` | Correzioni di CI: deploy dal branch di default, Mesa compatibile con Python 3.11 |
| 07:12 | `f6d6152` | Plotly incluso nel sito (i grafici non comparivano), action su Node 24 |
| 07:15 | `e535105` | Vista dinamica: agenti nel tempo, incontri, correnti di conoscenza |
| 07:20 | `027244a` | Bozza dell'articolo in LaTeX; figure in inglese |
| 07:22 | `fbfb96f` | Codespaces con Makefile, notebook di esplorazione e LaTeX |
| 07:25 | `8daa828` | README come racconto del lavoro; lezione |
| 07:36 | `376eed7` | Decisioni D1–D5: incontri nella stessa qualifica, robustezza 10/20, verifiche calcolate dal codice |
| 07:39 | `e3ad994` | Articolo con autori, stile e numeri aggiornati |
| 07:41 | `89f2b41` | Lezione al posto di presentazione; verifica automatica del sito pubblicato |
| 07:44 | `9eb6c65` | Autori in ordine alfabetico |
| chiusura | — | Reindirizzamento del vecchio indirizzo della lezione, Pages a ogni push, questo resoconto |

**Incidenti e come li abbiamo risolti**
- **Grafici assenti su Pages.** Plotly era caricato da una CDN che non lo serviva. Ora la libreria è inclusa nel sito.
- **Commit firmati "Claude".** La sessione usava un'identità predefinita. Ora i commit sono a nome di Vincenzo e la storia è stata riscritta (D10).
- **Commit perso nel force push.** La riscrittura della storia è partita da una copia precedente all'ultimo commit (ordine degli autori). È stato riapplicato sopra la storia riscritta, con contenuto identico.
- **404 sulla lezione.** Il file era stato rinominato da `presentazione.html` a `lezione.html`. Ora il vecchio indirizzo reindirizza, e un job di Actions apre il sito pubblicato in un browser e ne verifica pagine e grafici a ogni deploy.

## 3. Cosa c'è oggi nel repository

- **Modello** (`src/skillcliff/`): NumPy vettorizzato, circa 0,07 s per run.
- **Test**: 13 test automatici, tra cui conservazione di N, h ≥ 0, p = 0 senza apprendimento, riproducibilità e docking con Mesa.
- **Gemello in Mesa**: implementazione indipendente con un oggetto per agente; nessuna differenza significativa dal modello NumPy.
- **Sintesi tecnica** (`report/sintesi.md`): equazioni come implementate, parametri, verifiche, decisioni.
- **Articolo** (`paper/main.tex`): 16 pagine, formato Elsevier, compilato a ogni push e pubblicato.
- **Sito**: report, dinamica degli agenti, lezione, articolo in PDF.
- **Codespaces**: `make help`, notebook `notebooks/esplora_modello.ipynb`.

## 4. Risultati principali (30 repliche, IC 95%)

| Grandezza | Valore |
|---|---|
| B emergente | 0,0690 [0,0689; 0,0691] |
| di cui da incontri | 0,0426 (62%) |
| Profilo salariale | picco a 34 anni di esperienza, ×1,83 sull'ingresso, calo finale −1%/−4% |
| p dimezzato: h dei junior dopo 4 anni | −5,7% |
| p dimezzato: h dei senior | invariato per 10 anni, primo effetto all'11°, −6,7% a regime |
| p dimezzato: output a regime | −7,2% |
| p dimezzato: Gini dei salari | da 0,155 a 0,165 |
| Proposizione 1 (identità per B) | 0,0427 contro 0,0426 simulato |
| Proposizione 2 (ritardo) | 11 anni previsti e osservati, con soglie 5/15 e 10/20 |

## 5. Riflessioni

- **B è una variabile di stato.** Dopo lo shock non torna a un nuovo valore fisso: crolla, risale (i junior hanno più distanza da colmare), poi scende di nuovo quando i senior formati con meno incontri diventano insegnanti. Un modello con B costante non può rappresentare questa sequenza.
- **Il ritardo è strutturale e misurabile.** Dipende dalla distanza tra le soglie di ruolo, non dal loro livello. Per questo i dati di oggi sull'occupazione dei giovani non possono, da soli, dire nulla sul capitale umano dei senior di domani.
- **Conta la distribuzione, non solo la media.** Usare il rapporto delle medie al posto della media degli inversi sottostima B del 10%: la dispersione dei junior è parte del meccanismo.
- **La demografia stazionaria nasconde la scogliera.** Con S/J costante il vincolo di capacità non si attiva mai. La scogliera vera richiede uno shock: l'IA o una piramide come quella italiana.
- **Gli incontri riducono la disuguaglianza.** Meno incontri significa più disuguaglianza salariale, un effetto che il dibattito sull'IA di solito non considera.

## 6. Critiche prevedibili e come rispondere

| Critica | Quanto è fondata | Mitigazione (fatta / da fare) |
|---|---|---|
| *p*, β e κ sono arbitrari | Fondata: si calibra solo il prodotto p·β | Fatto: β calibrato su Jarosch et al., sensibilità a p e κ. Da fare: stima su microdati italiani (reti di colleghi INPS) o inferenza indiretta sui profili salariali |
| Il ritardo è un artefatto delle soglie discrete | In parte: il valore esatto dipende dalle soglie | Fatto: robustezza 10/20 (il ritardo dipende dalla distanza). Da fare: versione con apprendimento continuo in funzione dell'esperienza, che lo renda graduale |
| Nessuna impresa, nessun mercato del lavoro, w = h | Fondata: è la causa del Gini basso | Da fare nella fase 2: stato di occupazione dei junior (un junior sostituito non lavora e non incontra), poi imprese come luogo degli incontri |
| Nessuna scelta: né il tempo di apprendimento né la decisione di automatizzare | Fondata, ed è centrale in Ide (contratti incompleti) | Fase 2 con IA esogena; poi decisione d'impresa per misurare l'automazione socialmente eccessiva |
| Economia stazionaria, non c'è crescita alla Lucas | Fondata | Da fare: opzione con ingresso proporzionale all'h medio, che rende la crescita endogena |
| Evidenza sull'IA recente, americana, in working paper | Fondata | Dichiarato nel testo; da fare: segnali italiani (assunzioni entry-level per settore esposto) |
| La mappatura con Jarosch et al. è approssimativa | Fondata | Dichiarato in nota; da fare: misura comparabile nel modello (apprendimento di tutti da tutti) |
| Il docking verifica il codice, non la validità del modello | Corretto | La validazione resta sui fatti stilizzati; la sezione Verifiche dichiara cosa non torna |
| Profili per qualifica con la stessa pendenza | Fondata (Lagakos et al.) | Scelta deliberata (D2) per tenere il modello essenziale; riapribile se cambia i risultati della fase 2 |
| Riferimenti da verificare | Da controllare | Da fare: controllo puntuale di pagine e versioni (Ide 2026, Herkenhoff et al. 2024, working paper del 2025) |

## 7. Risvolti

**Politica**
- **Il costo arriva dopo che la decisione è stata presa.** Nella nostra calibrazione un'impresa che automatizza il lavoro junior non vede alcun costo nel capitale umano dei senior per dieci anni. È un'esternalità intergenerazionale, simile all'inquinamento: senza intervento, il mercato automatizza troppo.
- **Le leve corrispondono ai parametri del modello.**
  - Riserva di capacità per il mentoring nelle imprese: κ.
  - Apprendistati su progetti reali: p.
  - Contributo sull'automazione dei compiti entry-level: tassa sulle riduzioni di p.
  - IA che potenzia l'insegnamento invece di sostituire il junior: β.
  - L'identità della Proposizione 1 permette di confrontarle con una metrica comune.
- **Misurare prima.** Servono indicatori che anticipino la scogliera: assunzioni entry-level, quota di junior per senior, tempo dedicato al mentoring. Quando il calo si vedrà nei senior sarà tardi per correggerlo a basso costo.

**Tecnologia**
- La direzione conta più del livello. Un'IA che riduce *p* (sostituisce il junior) e un'IA che aumenta β (aiuta il senior a insegnare) hanno effetti opposti sullo stesso B.
- I co-pilot possono compensare in parte, ma riducono lo sforzo di chi impara (Ide): nel modello sarebbero un aumento di β accompagnato da un calo dell'apprendimento autonomo.

**Società**
- **Equità tra generazioni.** Chi paga sono i lavoratori che entreranno nei prossimi anni, che oggi non hanno voce.
- **Disuguaglianza.** Gli incontri la comprimono; ridurli la aumenta. Questo si collega all'ipotesi di "doppia segregazione" (ricchezza e competenze) su cui lavora Vincenzo.
- **Italia.** Le grandi coorti degli anni '60 vanno in pensione proprio ora: la scogliera demografica e quella dell'IA potrebbero sovrapporsi.

## 8. Prossimi passi

1. **Revisione di Federico** della sintesi e dell'articolo; affiliazioni e ruoli CRediT.
2. **Fase 2 (IA)**, dopo l'ok sulla sintesi. Decisioni da prendere all'inizio, in formato D (prima l'opzione raccomandata):
   - **D11 – Come l'IA riduce gli incontri.** **A:** p si riduce in proporzione alla quota di compiti junior automatizzata, che cresce con A(t) secondo una logistica. B: riduzione lineare in A(t).
   - **D12 – Output.** **A:** Y = (Σh)·(1 + θ·A) per il caso complementare e Y = Σh_non sostituiti + A per il caso sostitutivo. B: una CES unica con elasticità come parametro.
   - **D13 – Junior sostituiti.** **A:** restano nel modello come non occupati, che non incontrano nessuno e imparano solo da soli. B: escono dal modello.
3. **Caso Italia**: piramide degli occupati ISTAT e flussi d'ingresso dalle coorti di nascita.
4. **Calibrazione su dati**: profili salariali INPS per qualifica, quota di apprendimento dai colleghi.
5. **Articolo**: controllo dei riferimenti, sezione sulla fase 2, appendice ODD (descrizione standard dei modelli ad agenti).
