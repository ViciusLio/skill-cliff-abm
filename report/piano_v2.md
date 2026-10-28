# Piano per la seconda versione dell'articolo

*Federico Bassi e Vincenzo Lio. Task list costruita sulla [revisione dell'articolo](revisione_articolo.md).
Si spunta una casella quando il lavoro è fatto e verificato: test verdi, numeri rigenerati, testi coerenti.*

**Prima versione, conservata così com'è.**
- Il PDF è [sul sito](https://viciuslio.github.io/skill-cliff-abm/articolo_v1.pdf) e in `site/articolo_v1.pdf`.
- Codice, numeri e testi sono nel tag git `articolo-v1`: si guarda con `git checkout articolo-v1`, e
  `git diff articolo-v1` mostra cosa è cambiato da allora.

## 0. Preparazione

- [x] Revisione critica dell'articolo (`report/revisione_articolo.md`)
- [x] Prima versione congelata: tag `articolo-v1` e PDF sul sito
- [ ] Decisioni D21–D26 prese con Federico (tabella in fondo alla revisione)

## 1. Testo (senza nuove simulazioni)

- [ ] **T1 – Un messaggio, una gerarchia** [D25]
  - Messaggio principale: il ritardo (Proposizione 2) e l'equivalenza p/β.
  - Conseguenze: l'eccesso di automazione e la corsa.
  - Tabella principale con 4 scenari: junior compiti, senior compiti, junior posto, complementare.
  - Posto dei senior, scenari per qualifica, familiarità (D18) e mentore stabile (D20) in una sezione di robustezza
    o in appendice.
  - *Fatto quando:* sezioni 4–6 riorganizzate, abstract e introduzione allineati, README e sintesi aggiornati.
- [ ] **T2 – Bibliografia e posizionamento**
  - Da 18 a circa 50 voci, ognuna verificata sulla fonte (autori, anno, rivista):
    - ABM con competenze (Dawid et al., Eurace; Dosi et al., K+S);
    - diffusione della conoscenza (Perla e Tonetti; Buera e Oberfield; Akcigit et al.);
    - gerarchie della conoscenza (Garicano; Garicano e Rossi-Hansberg);
    - capitale umano d'annata (Chari e Hopenhayn; Violante);
    - apprendimento sul lavoro (Rosen 1972);
    - effetti cicatrice (Kahn; Oreopoulos et al.);
    - IA e lavoro (Brynjolfsson, Li e Raymond; Autor).
  - Un paragrafo su cosa ci distingue dagli ABM con competenze.
  - *Fatto quando:* `references.bib` aggiornato, nessuna voce non verificata.
- [ ] **T3 – Effetti in punti di crescita annua**
  - Tradurre le perdite di H in tasso di crescita annuo equivalente (−5,2% in 50 anni ≈ −0,1 punti l'anno) e
    confrontarle con Ide (−0,05).
  - *Fatto quando:* calcolo in `scripts/fase2.py`, numero in `numeri_fase2.json` e nel testo.
- [ ] **T4 – Stile**
  - Introduzione più asciutta con i contributi nel secondo paragrafo.
  - Titolo più corto.
  - "Proposition" diventa "Result" o "Lemma".
  - *Fatto quando:* testo rivisto e letto da entrambi.
- [ ] **T5 – Dati degli autori:** affiliazioni, ruoli CRediT, ringraziamenti, finanziamenti (servono da Vincenzo e
  Federico).

## 2. Modello: interventi a basso costo

- [ ] **T6 – Validazione sulle coorti della recessione** [D24]
  - Shock di non occupazione su una coorte d'ingresso, usando D19.
  - Perdita salariale nel tempo confrontata con le stime degli effetti cicatrice: è un momento che non abbiamo usato
    per calibrare.
  - Script `scripts/validazione.py`, `numeri_validazione.json`, figura in italiano e in inglese, test sul
    meccanismo.
  - *Fatto quando:* confronto con almeno due stime pubblicate, con le fonti verificate.
- [ ] **T7 – L'IA come tutor** [D23]
  - Il junior impara anche dall'IA, con efficacia legata alla familiarità (D18).
  - Possibile calo dello sforzo nell'apprendimento autonomo.
  - Due parametri, stream casuale invariato, base identica bit per bit, test.
  - Griglia: quando l'IA tutor compensa la perdita di incontri?
  - *Fatto quando:* numeri, figura e un paragrafo nella sezione sull'IA.

## 3. Modello: interventi a costo medio

- [ ] **T8 – Automazione scelta dentro il modello** [D22]
  - Un'impresa rappresentativa sceglie φ ogni anno confrontando il costo dei junior con quello dell'IA, senza vedere
    l'effetto futuro sul capitale umano.
  - Confronto con il pianificatore e con D15.
  - *Fatto quando:* l'eccesso di automazione emerge dalle scelte; D15 resta come caso statico.
- [ ] **T9 – Politiche quantificate**
  - Sussidio al mentoring (κ), apprendistati (p), contributo sull'automazione dei compiti entry-level.
  - Confronto con la stessa metrica (effetto su B e H) e con il loro costo.
  - *Fatto quando:* tabella nella sezione 7 dell'articolo.
- [ ] **T10 – Calibrazione e sensibilità globale** [D26]
  - Momenti simulati su 6–8 bersagli (profilo salariale italiano, apprendimento dai colleghi, rapporto
    junior/senior, assunzioni entry-level), poi indici di Sobol sui risultati principali.
  - Serve accesso ai dati: SES, INPS, PIAAC (vedi `nota_calibrazione.md`).
  - *Fatto quando:* parametri stimati con intervalli, risultati principali rigenerati, sensibilità in appendice.

## 4. Se si punta a JEDC [D21 B]

- [ ] **T11 – Legame con la crescita.** Proposizione 1 innestata in un modello alla Lucas; soglia oltre cui gli
  incontri generano crescita endogena.
- [ ] **T12 – Demografia italiana.** Piramide per età reale: la scogliera demografica e quella dell'IA si sommano?
- [ ] **T13 – Ruoli sfumati.** Soglie per lavoratore: il ritardo della Proposizione 2 diventa una distribuzione.

## 5. Chiusura della seconda versione

- [ ] Pipeline completa (`make all`), docking, test verdi in locale e su GitHub Actions.
- [ ] Coerenza dei testi: articolo, README, sintesi, sito, lezione.
- [ ] Tag `articolo-v2` e PDF `site/articolo_v2.pdf`.
- [ ] Requisiti della rivista scelta: lunghezza, highlights (Elsevier), JEL, dichiarazione sui dati, pacchetto di
  replica.
- [ ] Lettera di presentazione all'editor.

## Registro

- **28 ottobre 2026.** Prima versione congelata (`articolo-v1`). Revisione e piano scritti; in attesa di D21–D26.
