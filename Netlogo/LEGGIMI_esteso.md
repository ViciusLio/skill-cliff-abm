# La *skill cliff* in NetLogo — versione estesa

*Federico Bassi e Vincenzo Lio. Solo sul ramo `esteso`.* `skill_cliff_esteso.nlogo` parte dal modello della prima
versione (vedi [LEGGIMI.md](LEGGIMI.md), che resta valido per tutto il resto) e aggiunge i meccanismi della versione
estesa. **Con gli interruttori nuovi spenti coincide con il modello base.** Numeri e verifiche in
[report/sintesi_esteso.md](../report/sintesi_esteso.md).

## Scaricarlo

[skill_cliff_esteso.nlogo](https://github.com/ViciusLio/skill-cliff-abm/raw/esteso/Netlogo/skill_cliff_esteso.nlogo)
(dal ramo `esteso`; serve NetLogo 6.4).

## Cosa c'è in più

I controlli nuovi sono sotto i monitor, a sinistra.

| Interruttore / cursore | Meccanismo | Valore iniziale |
|---|---|---|
| `endogenous?` | **E2**: un'impresa sceglie ogni anno la quota φ di compiti junior da automatizzare (solo con `ai-target` = junior e `margin-junior` = compiti) | spento |
| `c0` | costo dell'IA all'arrivo, c = c0 / A | 1,33 (φ = 0,15 dopo 10 anni) |
| `chi` | quota del valore formativo dei junior che l'impresa internalizza (0 = miope) | 0 |
| `rho`, `career-years` | sconto e anni su cui si calcola il valore formativo | 0,97; 40 |
| `tutor?` | **E1**: il junior occupato impara anche dall'IA, dall'arrivo dell'IA | spento |
| `beta-ai` | efficacia del tutor (un incontro con un senior vale `beta` = 0,10) | 0,05 |
| `codifiable` | quota della conoscenza dei senior che l'IA codifica | 0,5 |
| `effort` | calo dello sforzo nell'apprendimento autonomo dei junior che usano l'IA | 0 |

Regole:
- **E2:** φ = phi-max · max(0, 1 − c / (w_J − chi · v)), con w_J il salario medio dei junior e v il valore formativo di
  un anno da junior (guadagno medio dagli incontri dell'anno prima, scontato su `career-years` anni). Il grafico
  "Quota automatizzata φ" e il monitor φ mostrano la scelta.
- **E1:** guadagno dal tutor = beta-ai · f · max(0, codifiable · h medio dei senior della qualifica − h); con `effort`
  l'apprendimento autonomo del junior si moltiplica per (1 − effort · f). Il monitor "B tutor" mostra quanto si impara
  dall'IA.

## Esperimenti già pronti (BehaviorSpace)

Oltre a quelli della versione base: `e2_impresa_miope`, `e2_impresa_chi_0.5`, `e1_tutor` (beta-ai = 0,1),
`e1_tutor_sforzo` (beta-ai = 0,1, effort = 0,25). Metriche in più: `phi`, `savings`, `w-firm`, `v-firm`, `B-tutor`.

## Quanto coincide con il Python

Base: differenza massima 0,08%. E2: entro lo 0,34% (φ equivalente con 60 repliche; i risparmi sono rumorosi).
E1: capitale umano, output e Gini entro lo 0,3%; l'apprendimento dal tutor è più basso dell'1,1–1,4% in NetLogo, una
differenza piccola non ancora spiegata (dettagli nella sintesi).

## Cose da provare

- Con `endogenous?` acceso, sposta `chi` da 0 a 1: l'impresa rimanda l'automazione di decenni.
- Con `tutor?` acceso, porta `codifiable` da 0,5 a 0,75: il tutor passa dal compensare poco al compensare tutto.
  Poi alza `effort`: il calo dello sforzo si mangia il guadagno.
