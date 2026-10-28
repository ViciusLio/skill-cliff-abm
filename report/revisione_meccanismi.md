# Revisione dei meccanismi — osservazioni di Federico

*Federico Bassi e Vincenzo Lio. Analisi e proposte di decisione (D16–D20).*

**Stato (28 ottobre 2026).** Tutte implementate: D19 A, D16 A e D17 A (sintesi della fase 2, sez. 8),
D18 A (sez. 9), D20 A come variante (sez. 10). Equazioni, numeri e verifiche nella
[sintesi della fase 2](sintesi_fase2.md). Rispetto alle proposte qui sotto: in D20 β è ricalibrato con λ
empirico (calibrare λ da solo non funziona); in D18 la forma dell'output è da confermare (sez. 9.1).

## Le osservazioni

1. **La probabilità di incontro non dovrebbe dipendere da chi viene sostituito.** L'effetto specifico
   della sostituzione dei senior va cercato altrove, per esempio nella produttività: chi sostituisce i
   senior resta con junior poco esperti ma formati all'IA, quindi produttivi; chi sostituisce i junior
   resta con esperti meno abituati alle nuove tecnologie.
2. **Distinguere incontro e trasferimento.** Sostituire compiti junior riduce la probabilità che un
   junior incontri un senior; sostituire compiti senior riduce la capacità del senior di trasferire
   conoscenza a ogni incontro.
3. **Esperienza e dipendenza dal sentiero.** L'esperienza dovrebbe crescere solo da occupati. Un junior
   che trova un senior dovrebbe imparare da lui finché resta in azienda; chi entra tardi accumula meno
   esperienza e meno capitale umano.
4. **Cosa vuol dire "sostituire"?** Perdere il posto, o restare al lavoro perdendo alcune facoltà
   (insegnare, imparare)?

## Una verifica: p e β hanno lo stesso effetto medio

Nel modello l'apprendimento da incontri è, in media, p_eff · β · E[max(0, h_s − h_j)]
(Proposizione 1): p e β entrano come prodotto. `python scripts/simmetria_p_beta.py` (10 repliche,
shock dall'anno 10, configurazione base) dà, a fine orizzonte:

| | p dimezzato | β dimezzato |
|---|---|---|
| H totale | −8,73% | −8,77% |
| h dei senior | −8,66% | −8,69% |
| apprendimento da incontri | −54,5% | −54,6% |
| Gini (base 0,156) | 0,165 | 0,162 |

- **In media i due canali sono indistinguibili.** Cambia solo la dispersione: con meno incontri alcuni
  junior imparano e altri no; con meno efficacia imparano tutti un po' meno.
- **Nella base la capacità dei senior non vincola:** p_eff = 0,6 = p. Per questo lo scenario attuale
  "IA sostituisce i senior", che agisce su κ, non fa quasi nulla (−0,07% di H) se κ non è al limite.

## Punto 4 prima di tutto: quattro interpretazioni

| | **perde il posto** | **resta, ma perde compiti** |
|---|---|---|
| **junior** | non viene assunto o entra tardi: niente incontri né esperienza (D13 + punto 3) | meno lavoro accanto al senior: p ↓ (fase 2 attuale) |
| **senior** | esce prima: meno mentori, κ·S/J ↓ (scenario "senior" attuale) | trasmette meno per incontro: β ↓ (punto 2) |

Le prime evidenze sui junior (Brynjolfsson et al. 2025; Hosseini e Lichtinger 2025) indicano meno
assunzioni più che licenziamenti, cioè ingresso ritardato. *Da ricontrollare sugli articoli.*

## Punti 1 e 2: il bersaglio senior

- **Senso.** Lo scenario "senior" attuale descrive senior che perdono il posto, non compiti. Il canale
  produttività richiama il capitale umano d'annata (Chari e Hopenhayn 1991; Violante 2002) e
  l'evidenza che l'IA aiuta soprattutto i meno esperti (Brynjolfsson, Li e Raymond 2025).
- **Impatto.** Con il punto 2 junior e senior hanno lo stesso effetto medio su H; con il punto 1
  hanno effetti opposti sull'output. Sostituire i senior: più output oggi, meno trasmissione domani.
  Sostituire i junior: meno output oggi e la *skill cliff* domani. Il risultato "sostituire i senior
  conta solo se i mentori sono scarsi" (sintesi della fase 2, sez. 4.3) sarebbe sostituito da questo
  compromesso tra produttività oggi e capitale umano domani.
- **Costo.** Una variabile per lavoratore (familiarità con l'IA, anche solo l'anno d'ingresso) e una
  nuova equazione per l'output. La Proposizione 1 resta valida.

## Punto 3: esperienza e mentore stabile

- **Esperienza solo da occupati: corregge un'incoerenza attuale.** Oggi `pop.exp += 1` vale per tutti
  (`src/skillcliff/model.py`), anche per i junior non occupati dello scenario D13, che diventano
  "senior" dopo 15 anni senza aver lavorato.
  Impatto: effetto cicatrice per chi entra tardi (Kahn 2010; Oreopoulos, von Wachter e Heisz 2012).
  Con l'IA che frena le assunzioni ne escono coorti segnate in modo permanente.
- **Mentore stabile: cambia di più il modello.** Il junior abbinato resta con il suo senior fino al
  pensionamento di quest'ultimo, fino a quando smette di essere junior, o con una probabilità annua
  di separazione λ. Impatti:
  - la fortuna del primo abbinamento diventa persistente: più disuguaglianza;
  - con lo stesso mentore la distanza di conoscenza si chiude e si impara sempre meno; per restare
    confrontabili con la fase 1, λ va calibrato in modo da conservare l'apprendimento medio;
  - la Proposizione 1 diventa approssimata (i junior abbinati non sono un campione casuale);
  - la Proposizione 2 va riletta: il ritardo resta di 11 anni di esperienza, in anni di calendario
    può allungarsi;
  - il gemello in Mesa va esteso, altrimenti il docking vale solo per la versione attuale.

## Decisioni proposte

| | Domanda | Raccomandazione |
|---|---|---|
| D16 | Interpretazione della sostituzione | **A** tabella 2×2 esplicita (posto / compiti per ogni bersaglio). B solo "compiti". |
| D17 | Compiti senior | **A** β ↓; κ resta solo nella variante "posto"; l'equivalenza media con p diventa un risultato. B lasciare κ. |
| D18 | Produttività | **A** familiarità con l'IA legata all'anno d'ingresso, un parametro di aggiornamento per gli occupati; nell'output l'IA pesa per familiarità. B introdurre le imprese (articolo successivo). |
| D19 | Esperienza solo da occupati | **A** sì, subito. |
| D20 | Mentore stabile | **A** variante da configurazione, λ calibrato sull'apprendimento medio della fase 1, confronto con la versione attuale. B sostituire la versione attuale. |

Ordine proposto: D19, D16–D17, D18, D20. D18 e D20 da discutere insieme prima di scrivere codice.
