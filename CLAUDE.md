# Istruzioni per Claude

> **Sei sul ramo `esteso`** (versione complessa, secondo articolo). Piano: `report/piano_esteso.md`.
> Qui si aggiungono meccanismi, sempre spegnibili da configurazione; non si modifica `paper/main.tex`.

Progetto: ABM sulla trasmissione del capitale umano tra senior e junior e sull'effetto dell'IA
(la *skill cliff*). Autori: Federico Bassi e Vincenzo Lio (in quest'ordine, alfabetico; Lio è
l'autore di riferimento). Il README racconta il lavoro; `report/` contiene sintesi, numeri e decisioni.

## Rami

- **`main` è la versione base**: articolo 1, sito, lezione, NetLogo. Qui non si aggiungono meccanismi al
  modello: testo, analisi e verifiche (piano in `report/piano_v2.md`).
- **`esteso` è la versione complessa** (secondo articolo, piano in `report/piano_esteso.md` su quel ramo).
  `main` confluisce in `esteso` (merge), mai il contrario senza una decisione. Un errore che tocca anche la base
  si corregge prima su `main`. Su `esteso` non si modifica `paper/main.tex`.
- Prima di lavorare controlla il ramo con `git branch --show-current`.

## Come lavoriamo

- **Prima il piano, poi il codice.** Le scelte di modellazione ambigue si decidono insieme in formato
  D: numera le decisioni (D16, D17, ...), proponi le opzioni A/B con la raccomandazione, aspetta la
  conferma (es. "D16 A, D17 B"). Le decisioni prese sono elencate nelle sintesi in `report/`.
- **Modello essenziale.** Ogni meccanismo nuovo deve servire a una domanda dell'articolo.
- **Verifica prima di dire "finito".** Test verdi, numeri rigenerati, testi coerenti con i numeri
  (README, `report/sintesi*.md`, `paper/main.tex`, `site/`). Dì cosa non torna, se qualcosa non torna.
- **Aggiorna sempre il README** quando cambia un risultato, un comando o la struttura.
- **Niente frasi vuote.** Testi brevi, concreti, con i numeri.
- **Lingue.** Articolo in inglese; README, sintesi, note e lezione in italiano.
  Le figure si generano in italiano (`report/fig`) e in inglese (`paper/fig`).
- **Commit piccoli**, messaggi in italiano, autore l'utente del Codespace, push su `main`.
  Ogni push su `main` lancia i test e ripubblica il sito (GitHub Actions): controlla che passino.

## Regole tecniche

- NumPy vettorizzato, popolazione come struttura di array (`population.py`).
- Numeri casuali comuni: quattro stream da `SeedSequence.spawn(4)` (init, demo, meet, ai).
  Un nuovo meccanismo casuale usa uno stream suo o deriva da `ai`, senza spostare gli altri:
  la base deve restare identica bit per bit.
- Nessuna metrica durante il burn-in (300 anni). Repliche: 30, con IC al 95%.
- I moduli IA passati a `run_replications` devono essere serializzabili (`functools.partial`).
- Test obbligatori che devono continuare a valere: conservazione degli agenti, h ≥ 0,
  p = 0 ⇒ nessun apprendimento da incontri, stesso seed ⇒ risultati identici.
- Se cambia la versione base del modello, va aggiornato il gemello Mesa (`mesa_twin.py`) e
  rifatto il docking (`make docking`); una variante attivabile da configurazione può restare
  fuori dal docking, ma va detto.
- Il gemello NetLogo (`Netlogo/skill_cliff.nlogo`) riproduce il modello della prima versione (tag
  `articolo-v1`), che Federico usa in NetLogo. Se cambiano le regole, aggiornalo o di' che resta
  alla prima versione; verifica con `make docking-netlogo`. In NetLogo i nomi non distinguono le
  maiuscole (H e h sono lo stesso nome).

## Comandi

```bash
make test         # test
make report       # fase 1: figure, numeri (report/numeri_fase1.json), dati del sito
make fase2        # fase 2: scenari IA (report/numeri_fase2.json)
make automazione  # D15 (report/numeri_d15.json)
make mentore      # D20, mentore stabile, e suo docking (report/numeri_d20.json)
make docking      # NumPy contro Mesa
make docking-netlogo  # NumPy contro NetLogo (serve NETLOGO_HOME)
make paper        # paper/main.pdf
make site         # sito in locale, porta 8000
```

## Lavori aperti

- `report/piano_v2.md`: task list della seconda versione dell'articolo base (decisioni D21–D28 prese).
  La prima versione è congelata nel tag `articolo-v1` e in `site/articolo_v1.pdf`: non modificarli.
- `report/nota_calibrazione.md`: calibrazione e soglia di crescita R.
- Affiliazioni e ruoli CRediT nell'articolo: segnaposto, da completare.
