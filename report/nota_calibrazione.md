# Nota sulla calibrazione — traccia per la discussione

*Federico Bassi e Vincenzo Lio. Proposta, non lavoro fatto: le fonti vanno verificate (accesso, anni, variabili).*

## Il problema

Oggi solo β è calibrato su un dato esterno, cioè la quota di apprendimento dai colleghi di Jarosch et al. (2021); gli altri parametri sono scelti a mano. I nodi sono tre:

1. **p e β non sono identificati separatamente.** I dati sui salari vedono solo il loro prodotto. Serve una fonte diretta per p, la frequenza con cui un junior impara da un senior.
2. **κ decide il risultato sul bersaglio senior.** Da quasi nullo a −4,8% di capitale umano (sintesi della fase 2, sez. 4.3). Serve una misura di quanti senior fanno davvero da mentori.
3. **δ₀, S_h, d e h₀** danno forma al profilo salariale e vanno stimati sui profili italiani per età e istruzione.

## Parametri, bersagli e fonti candidate

| Parametro | Cosa misura | Bersaglio | Fonte candidata |
|---|---|---|---|
| p | frequenza dell'apprendimento da colleghi | quota di junior che impara regolarmente da colleghi o superiori | OCSE PIAAC (domande sull'apprendimento sul lavoro da colleghi e superiori), Italia |
| κ | capacità di mentoring | quota di lavoratori esperti che affianca o forma colleghi | Eurofound EWCS (formazione sul lavoro da colleghi); indagine INAPP-PLUS |
| β | efficacia dell'incontro | crescita salariale dovuta ai colleghi: 4–9% della retribuzione | Jarosch et al. (2021); in prospettiva reti di colleghi su dati INPS |
| δ₀, S_h, d | apprendimento autonomo e obsolescenza | profilo salariale per età: picco, rapporto picco/ingresso, calo finale | Eurostat SES (retribuzioni per età e istruzione); INPS; Banca d'Italia SHIW |
| h̄₀(H)/h̄₀(L), σ | premio d'ingresso e dispersione | salario d'ingresso dei laureati rispetto ai diplomati; dispersione a inizio carriera | Eurostat SES; AlmaLaurea (retribuzioni a un anno dalla laurea) |
| φ (fase 2) | intensità della sostituzione | assunzioni entry-level nei settori esposti all'IA | INPS (assunzioni per età e settore); Unioncamere Excelsior |

## Metodo proposto

1. **Momenti simulati.** Scegliamo 6–8 momenti, cioè le grandezze in tabella, e minimizziamo la distanza ponderata tra momenti del modello e momenti dei dati. Un run con 5.000 agenti richiede circa 0,07 s, quindi 10.000 valutazioni costano circa 5 minuti su 4 core.
2. **Esplorazione globale prima dell'ottimizzazione.** Campionamento a ipercubo latino dello spazio dei parametri, poi raffinamento locale (Nelder–Mead).
3. **Sensibilità globale.** Indici di Sobol, per mostrare quali parametri contano per i risultati principali (H a fine orizzonte, ritardo, eccesso di automazione). È l'analisi che un referee chiede per prima.
4. **Incertezza.** Bootstrap sui momenti dei dati, per gli intervalli dei parametri stimati.

## Una proposta collegata: la soglia di crescita

Con parametri estremi il modello cresce senza limite, come in Lucas. Si può caratterizzare con un **numero di riproduzione della conoscenza R**: di quanto cresce l'h della prossima generazione di senior se quello dei senior di oggi aumenta dell'1%. Se R < 1 l'economia è stazionaria, se R > 1 cresce.

R si misura nel modello con una piccola perturbazione e si approssima analiticamente con la Proposizione 1. La mappa di R su (p, β) dice quanto la calibrazione è lontana dalla soglia e lega il lavoro a Lucas: l'IA che riduce p allontana l'economia dal regime di crescita.

## Da decidere insieme

- Quali momenti usare, e se fermarsi all'Italia o confrontare più paesi europei (SES e PIAAC lo permettono).
- Se c'è accesso a microdati (INPS, SES) o se si lavora su tabelle pubblicate.
- Se la mappa di R entra in questo articolo o nel successivo.
