# Piano della versione estesa (ramo `esteso`)

*Federico Bassi e Vincenzo Lio. La versione più complessa del modello, verso un secondo articolo (D28). La versione
base resta su `main` ed è il punto di partenza: ogni meccanismo qui si spegne da configurazione e, spento, lascia
la base identica bit per bit.*

## Regole del ramo (D27)

- **`main` confluisce qui** con un merge periodico (almeno dopo ogni lavoro concluso su `main`), così testo, analisi
  e correzioni della base arrivano anche qui. Il contrario non avviene senza una decisione esplicita.
- **Un errore che tocca anche la base** si corregge prima su `main`, poi arriva qui con il merge.
- **Non si modifica `paper/main.tex`** (l'articolo base). I risultati vanno in `report/sintesi_esteso.md` e, quando
  saranno maturi, in un secondo articolo.
- **Ogni meccanismo** si decide prima in formato D (da D29 in poi), ha uno stream casuale suo o derivato da `ai`,
  test e confronto "base contro esteso" a numeri casuali comuni.
- **Mesa e NetLogo** restano gemelli della base; per ogni meccanismo nuovo si dice se entra nel docking.
- **Il sito** si pubblica solo da `main`: qui i risultati stanno nei file di `report/`.
- **NetLogo (D29).** Federico prova la versione estesa in `Netlogo/skill_cliff_esteso.nlogo` (solo su questo ramo;
  il file base `Netlogo/skill_cliff.nlogo` resta quello della prima versione). Un meccanismo è finito solo quando è
  anche lì, spento di default, e il confronto con il Python (`scripts/docking_netlogo.py`) copre i suoi scenari.

## Compiti

Ognuno parte con un piano in formato D da confermare.

- [ ] **E1 – L'IA come tutor** (era T7, D23)
  - Il junior impara anche dall'IA, con un'efficacia legata alla familiarità (D18).
  - Possibile calo dello sforzo nell'apprendimento autonomo (Ide).
  - Domanda: quando l'IA tutor compensa la perdita di incontri?
- [ ] **E2 – Imprese che scelgono quanto automatizzare** (era T8, D22)
  - Un'impresa rappresentativa, poi poche imprese, scelgono φ ogni anno confrontando il costo dei junior con quello
    dell'IA, senza vedere l'effetto futuro sul capitale umano.
  - L'eccesso di automazione emerge dalle scelte; D15 resta il caso statico.
- [ ] **E3 – Calibrazione su dati italiani** (era T10, D26)
  - Momenti simulati su 6–8 bersagli: profilo salariale (SES/INPS), apprendimento dai colleghi (PIAAC), rapporto
    junior/senior, assunzioni entry-level nei settori esposti.
  - Serve accesso ai dati (vedi `nota_calibrazione.md`).
- [ ] **E4 – Legame con la crescita** (era T11)
  - Proposizione 1 innestata in un modello alla Lucas; soglia oltre cui gli incontri generano crescita endogena.
- [ ] **E5 – Demografia italiana** (era T12)
  - Piramide per età reale: la scogliera demografica e quella dell'IA si sommano?
- [ ] **E6 – Ruoli sfumati** (era T13)
  - Soglie junior/senior per lavoratore: il ritardo della Proposizione 2 diventa una distribuzione.
- [ ] **E7 – Persistenza della non occupazione**
  - Chi è stato fuori rientra con più difficoltà (effetto cicatrice oltre agli anni persi).
- [ ] **E8 – Secondo articolo**
  - Cartella `paper_esteso/` quando almeno due compiti sono conclusi.

## Registro

- **29 ottobre 2026.** Ramo creato da `main` (commit `5608a24`). Nessun meccanismo nuovo ancora.
- **29 ottobre 2026.** D29 A: NetLogo esteso in `Netlogo/skill_cliff_esteso.nlogo`. Ordine: E2, poi E1.
