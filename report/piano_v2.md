# Piano per la seconda versione dell'articolo (versione base)

*Federico Bassi e Vincenzo Lio. Task list costruita sulla [revisione dell'articolo](revisione_articolo.md).
Si spunta una casella quando il lavoro è fatto e verificato: test verdi, numeri rigenerati, testi coerenti.*

**La strategia (29 ottobre 2026).**
- **Questo ramo (`main`)** porta l'articolo base: un modello di capitale umano, senza scelte economiche degli agenti,
  con la teoria di fondo e risultati concreti e intuibili, utili a decisori pubblici e imprese. Qui non si aggiungono
  meccanismi: si lavora su testo, analisi e verifiche.
- **Il ramo `esteso`** porta la versione più complessa (imprese che scelgono, IA come tutor, dati italiani, crescita,
  demografia): piano in `report/piano_esteso.md` su quel ramo.

**Prima versione, conservata così com'è.**
- Il PDF è [sul sito](https://viciuslio.github.io/skill-cliff-abm/articolo_v1.pdf) e in `site/articolo_v1.pdf`.
- Codice, numeri e testi sono nel tag git `articolo-v1`: si guarda con `git checkout articolo-v1`, e
  `git diff articolo-v1` mostra cosa è cambiato da allora.

## Decisioni (29 ottobre 2026)

| | Decisione |
|---|---|
| D21 | Rivista: JASSS o SCED, che accolgono un modello di capitale umano senza scelte economiche. |
| D22 | Automazione scelta dalle imprese: nel ramo `esteso`. |
| D23 | IA come tutor: nel ramo `esteso`. |
| D24 | Validazione sulle coorti della recessione: sì, sulla base. |
| D25 | Struttura: quattro scenari nel testo, varianti in robustezza o appendice. |
| D26 | Calibrazione: sensibilità globale (Sobol) sulla base; calibrazione su dati italiani nel ramo `esteso`. |
| D27 | Gestione: ramo `esteso` di lunga durata. `main` confluisce in `esteso`, mai il contrario senza una decisione; i meccanismi nuovi si spengono da configurazione e, spenti, lasciano la base identica bit per bit. |
| D28 | La versione estesa diventa un secondo articolo. |

## 0. Preparazione

- [x] Revisione critica dell'articolo (`report/revisione_articolo.md`)
- [x] Prima versione congelata: tag `articolo-v1` e PDF sul sito
- [x] Modello in NetLogo per Federico, verificato contro il Python (`Netlogo/`)
- [x] Decisioni D21–D28
- [x] Ramo `esteso` creato con il suo piano

## 1. Testo

- [ ] **T1 – Un messaggio, una gerarchia** [D25]
  - Messaggio principale: il ritardo (Proposizione 2) e l'equivalenza p/β.
  - Conseguenze: l'eccesso di automazione e la corsa.
  - Tabella principale con 4 scenari: junior compiti, senior compiti, junior posto, complementare.
  - Posto dei senior, scenari per qualifica, familiarità (D18) e mentore stabile (D20) in una sezione di robustezza
    o in appendice.
  - La scelta di metodo detta nell'introduzione: prima il meccanismo del capitale umano, poi i comportamenti.
  - *Fatto quando:* sezioni 4–6 riorganizzate, abstract e introduzione allineati, README e sintesi aggiornati.
- [x] **T2 – Bibliografia e posizionamento** (29 ottobre: 48 voci, tutte verificate e citate; nuova sottosezione 2.4)
  - Da 18 a circa 50 voci, ognuna verificata sulla fonte (autori, anno, rivista):
    - ABM con competenze (Dawid et al., Eurace; Dosi et al., K+S);
    - diffusione della conoscenza (Perla e Tonetti; Buera e Oberfield; Akcigit et al.);
    - gerarchie della conoscenza (Garicano; Garicano e Rossi-Hansberg);
    - capitale umano d'annata (Chari e Hopenhayn; Violante);
    - apprendimento sul lavoro (Rosen 1972);
    - effetti cicatrice (Kahn; Oreopoulos et al.);
    - IA e lavoro (Brynjolfsson, Li e Raymond; Autor);
    - letteratura di JASSS sui modelli di apprendimento e diffusione;
    - restano da aggiungere con T6 e T10a: Saltelli et al. (2008) e Sobol (2001), già verificati.
  - Un paragrafo su cosa ci distingue dagli ABM con competenze.
  - *Fatto quando:* `references.bib` aggiornato, nessuna voce non verificata.
- [ ] **T3 – Effetti in punti di crescita annua**
  - Tradurre le perdite di H in tasso di crescita annuo equivalente e confrontarle con Ide (−0,05 punti).
  - *Fatto quando:* calcolo in `scripts/fase2.py`, numero in `numeri_fase2.json` e nel testo.
- [ ] **T4 – Stile**
  - Introduzione più asciutta con i contributi nel secondo paragrafo.
  - Titolo più corto.
  - "Proposition" diventa "Result" o "Lemma".
  - *Fatto quando:* testo rivisto e letto da entrambi.
- [ ] **T5 – Dati degli autori:** affiliazioni, ruoli CRediT, ringraziamenti, finanziamenti (servono da Vincenzo e
  Federico).

## 2. Analisi sulla base (senza meccanismi nuovi)

- [ ] **T6 – Validazione sulle coorti della recessione** [D24]
  - Shock di non occupazione su una coorte d'ingresso, usando D19.
  - Perdita salariale nel tempo confrontata con le stime degli effetti cicatrice: è un momento che non abbiamo usato
    per calibrare.
  - Script `scripts/validazione.py`, `numeri_validazione.json`, figura in italiano e in inglese, test.
  - *Fatto quando:* confronto con almeno due stime pubblicate, con le fonti verificate.
- [ ] **T9 – Politiche quantificate**
  - Sussidio al mentoring (κ), apprendistati (p), contributo sull'automazione dei compiti entry-level, IA che aiuta a
    insegnare (β).
  - Stessa metrica per tutte (effetto su B, H e output) e confronto a parità di intensità.
  - Lettura per i decisori pubblici e per le imprese che investono in capitale umano.
  - *Fatto quando:* tabella nella sezione 7 dell'articolo, nel README e nella sintesi.
- [ ] **T10a – Sensibilità globale** [D26]
  - Indici di Sobol sui risultati principali (perdita di H, ritardo, eccesso di automazione) rispetto ai parametri
    calibrati a mano.
  - *Fatto quando:* tabella e figura in appendice.

## 3. Chiusura della seconda versione

- [ ] Pipeline completa (`make all`), docking con Mesa e con NetLogo, test verdi in locale e su GitHub Actions.
- [ ] Coerenza dei testi: articolo, README, sintesi, sito, lezione.
- [ ] Tag `articolo-v2` e PDF `site/articolo_v2.pdf`.
- [ ] Requisiti della rivista: lunghezza, JEL, dichiarazione sui dati, pacchetto di replica (JASSS chiede il codice
  in un archivio pubblico, ad esempio CoMSES).
- [ ] Lettera di presentazione all'editor.

## Registro

- **28 ottobre 2026.** Prima versione congelata (`articolo-v1`). Revisione e piano scritti.
- **28 ottobre 2026.** Modello in NetLogo pubblicato in `Netlogo/` (docking: differenza massima 0,25%).
- **29 ottobre 2026.** Decisioni D21–D28: modello base su `main`, versione estesa nel ramo `esteso`. Si parte da T3 e T2.
