# Revisione dell'articolo: punti di forza, debolezze, cosa migliorare

*Federico Bassi e Vincenzo Lio. Lettura critica dell'articolo (versione del 28 ottobre 2026) con gli occhi di un referee
di una rivista di economia. Proposte, non decisioni: le scelte da prendere sono in fondo, in formato D.*

## Giudizio sintetico

La domanda è attuale e originale, il meccanismo è chiaro, e la cura metodologica è sopra la media degli ABM pubblicati.
Il punto debole è economico più che tecnico: nessuno nel modello sceglie (né lavoratori né imprese, tranne l'esercizio
D15 fuori dal modello), la calibrazione è parziale e gli effetti sono modesti in livello. Oggi un referee di una buona
rivista direbbe probabilmente *major revision* nel migliore dei casi. Con tre o quattro interventi mirati (sotto) il
lavoro diventa competitivo per riviste come JEBO, SCED o JEDC.

## Punti di forza

1. **Domanda nuova e rilevante.** Il canale intergenerazionale dell'IA (meno junior oggi, senior meno formati domani) è
   discusso ma quasi mai quantificato. Il ritardo di una generazione professionale spiega perché i dati di oggi non
   possono ancora vederlo: è un messaggio forte per la politica.
2. **Risultati analitici dentro un ABM.** La Proposizione 1 (identità di campo medio per B) e la Proposizione 2 (ritardo
   esatto di $s_S - s_J + 1$ anni) sono rare in un ABM e fanno da ponte verso i modelli aggregati.
3. **Risultati concettuali puliti.**
   - La tabella 2×2 (compiti o posto, junior o senior).
   - L'equivalenza media di p e β, che si rompe con il mentore stabile.
   - Il fatto che perdere il posto *rinvia* la formazione invece di cancellarla.
   - L'eccesso di automazione che cresce con l'orizzonte e non si vede sui 10 anni.
4. **Riproducibilità esemplare.** Codice aperto e testato, numeri casuali comuni tra scenari, invarianza alla scala
   fino a 24 milioni di agenti, docking con Mesa e test di equivalenza (TOST), protocollo ODD, IC al 95% ovunque.
   Molte riviste ora chiedono pacchetti di replica: qui è già pronto.
5. **Sintesi verificabile.** Ogni numero del testo viene da un file `numeri_*.json` rigenerabile.

## Debolezze, come le vedrebbe un referee

Ordinate per gravità.

### Gravi

1. **"Dov'è l'economia?"** Nessuno sceglie nulla. I lavoratori non investono in formazione, le imprese non decidono
   chi assumere né quanto automatizzare (D15 è un calcolo esterno con π e c illustrativi), i salari non si formano su
   un mercato (w = h). Per una rivista di economia l'esternalità di Ide dovrebbe *emergere* dalle scelte delle imprese
   dentro il modello, non essere imposta con φ esogeno.
2. **Calibrazione debole.**
   - Solo β è calibrato su un dato esterno (Jarosch et al.); p e κ sono scelti a mano, θ e g sono arbitrari.
   - φ_max è ancorato a un calo di *occupazione* (Brynjolfsson et al.), ma nel modello è una quota di *compiti*: il
     passaggio dall'uno all'altra non è giustificato.
   - p e β non sono identificati separatamente, e la Proposizione 1 dice che in media conta solo il loro prodotto: i
     risultati principali dipendono quindi soprattutto da φ_max.
   - Il riferimento all'Italia è solo nel profilo salariale e nell'età di pensione.
3. **Il legame con Lucas è più retorico che dimostrato.** Il modello è stazionario: H non cresce, B è il tasso di
   apprendimento dei junior, non il tasso di crescita dell'economia. Il terzo contributo ("un'identità utilizzabile
   nei modelli di crescita") va mostrato in concreto: innestare la Proposizione 1 in un modello alla Lucas e mostrare
   cosa cambia nella crescita di lungo periodo, oppure caratterizzare la soglia oltre cui gli incontri diventano un
   motore di crescita endogena (la soglia R della nota sulla calibrazione).
4. **L'IA come fonte di apprendimento manca.** È l'obiezione più probabile. Brynjolfsson, Li e Raymond (2025) trovano
   che l'IA aiuta soprattutto i meno esperti: è un tutor. Nel modello l'IA toglie incontri o rende l'insegnamento più
   efficace, ma il junior non impara mai *dall'IA*, e il possibile calo di sforzo (Ide) non c'è. Senza questo canale il
   risultato sembra sbilanciato verso il pessimismo.

### Importanti

5. **Effetti piccoli in livello.** −5,2% di capitale umano in 50 anni sembra poco. Va tradotto in una metrica
   confrontabile: circa −0,1 punti di crescita annua, dello stesso ordine del −0,05 di Ide. Così diventa un risultato,
   non una debolezza.
6. **Troppi scenari, messaggio diluito.** Sette scenari, tre varianti (D13/D19, D18, D20), corsa, D15: sembra un
   catalogo. Serve una gerarchia: un risultato principale e il resto come robustezza in appendice.
7. **Nessuna validazione fuori campione.** Tutti i momenti sono bersagli o scelte a mano. Un test naturale: le coorti
   che entrano nel mercato del lavoro durante una recessione (Kahn 2010; Oreopoulos, von Wachter e Heisz 2012). Con
   D19 il modello dovrebbe produrre perdite salariali persistenti per quelle coorti; confrontarle con le stime è una
   validazione non mirata, e molto convincente.
8. **Forme funzionali ad hoc.** $\varphi = \varphi_{\max}(1 - 1/A)$, Y moltiplicativo, stessa φ per tutti i bersagli,
   IA complementare simmetrica per costruzione. Il quadro a compiti di Acemoglu e Restrepo è citato ma non usato.
9. **Ruoli a soglia netta.** Il ritardo esatto della Proposizione 2 dipende da soglie nette (junior sotto 5 anni,
   senior da 15). Con ruoli sfumati il ritardo diventa una distribuzione; va mostrato che il messaggio regge.
10. **Bibliografia sottile: 18 voci.** Mancano almeno:
    - **ABM con competenze:** Dawid et al. (Eurace@Unibi, competenze generali e specifiche), Dosi et al. (modelli
      K+S con competenze);
    - **diffusione della conoscenza:** Perla e Tonetti 2014; Buera e Oberfield 2020; Akcigit et al.;
    - **gerarchie della conoscenza:** Garicano 2000; Garicano e Rossi-Hansberg;
    - **capitale umano d'annata:** Chari e Hopenhayn 1991; Violante 2002;
    - **apprendimento sul lavoro:** Rosen 1972;
    - **effetti cicatrice:** Kahn, Oreopoulos et al.;
    - **la parte empirica sull'IA:** Brynjolfsson, Li e Raymond 2025; Autor.

### Minori

11. **Le "Proposizioni" possono sembrare enfatiche.** La 1 è un'identità contabile, la 2 un argomento di tempi. Meglio
    presentarle come *risultati* o *lemmi* e insistere sulla loro utilità: una metrica comune per le politiche e una
    previsione verificabile.
12. **Politiche solo qualitative.** Il modello permette di quantificarle a costo quasi nullo, ma la sezione 7 non lo fa:
    sussidio al mentoring (κ), contributo sull'automazione dei compiti entry-level, apprendistati (p).
13. **Stile.** L'introduzione narrativa ("In 1988 an economist from Chicago...") piace in una lezione, meno a un
    editor. Il titolo è lungo. Mancano affiliazioni e ruoli CRediT.

## Riviste possibili

| Rivista | Perché sì | Cosa serve in più |
|---|---|---|
| Structural Change and Economic Dynamics | ABM e cambiamento tecnico ben accolti; vicina al lavoro di Federico | validazione e bibliografia |
| Journal of Economic Behavior & Organization | ABM con domanda economica chiara | scelte d'impresa dentro il modello |
| Journal of Economic Dynamics and Control | risultati analitici più calibrazione | calibrazione seria (SMM, Sobol) e legame con la crescita |
| Journal of Evolutionary Economics | conoscenza, routine, dinamiche lente | posizionamento nella letteratura evolutiva |
| Labour Economics | tema del lavoro giovanile | servirebbe una parte empirica: oggi non adatta |

Raccomandazione: puntare a **SCED o JEBO** dopo gli interventi indispensabili; **JEDC** se si fa anche la calibrazione
SMM e il legame con la crescita.

## Piano di miglioramento

### Indispensabile (prima di inviare)

1. **Un messaggio, una gerarchia.**
   - Il risultato principale è il ritardo (Proposizione 2) più l'equivalenza p/β.
   - L'eccesso di automazione e la corsa sono le conseguenze.
   - Varianti (posto, familiarità, mentore stabile) in una sezione di robustezza o in appendice.
   - Tabella principale con 4 scenari.
2. **Automazione scelta dentro il modello.** Un'impresa rappresentativa, o poche imprese, sceglie ogni anno φ
   confrontando il costo dei junior con quello dell'IA, senza vedere l'effetto futuro sul capitale umano. È la versione
   dinamica di D15 e fa emergere l'esternalità dalle scelte.
3. **Calibrazione e sensibilità globale.** Momenti simulati su 6–8 bersagli: profilo salariale italiano (SES/INPS),
   quota di apprendimento dai colleghi, rapporto junior/senior, assunzioni entry-level nei settori esposti. Poi indici
   di Sobol sui risultati principali: perdita di H, ritardo, eccesso di automazione. Il metodo è già nella nota sulla
   calibrazione.
4. **Validazione non mirata: coorti della recessione.** Shock di non occupazione su una coorte d'ingresso, con perdita
   salariale nel tempo confrontata con le stime degli effetti cicatrice. Costo basso: D19 c'è già.
5. **L'IA come tutor.** Il junior impara anche dall'IA, con un'efficacia legata alla familiarità (D18) e un possibile calo
   dello sforzo nell'apprendimento autonomo (Ide). Basta un parametro per canale. Il risultato va mostrato su una
   griglia: quando l'IA tutor compensa la perdita di incontri?
6. **Bibliografia e posizionamento.** Da 18 a circa 50 voci (elenco al punto 10 delle debolezze), con un paragrafo che
   dica in cosa ci distinguiamo da Eurace e dai modelli K+S.

### Utile (rafforza molto)

7. **Legame con la crescita.** Proposizione 1 in un modello alla Lucas e soglia di crescita endogena caratterizzata.
   Effetti tradotti in punti di crescita annua.
8. **Demografia italiana.** Le grandi coorti degli anni '60 vanno in pensione proprio ora: le due scogliere, demografica
   e da IA, si sommano? È anche ciò che giustifica il riferimento all'Italia.
9. **Politiche quantificate.** Tre leve (κ, p, imposta sull'automazione) confrontate con la stessa metrica (effetto su B
   e su H), e il loro costo.
10. **Ruoli sfumati.** Soglie per lavoratore estratte da una distribuzione: il ritardo diventa una distribuzione, il
    messaggio resta.

### Opzionale

11. **Persistenza della non occupazione** (chi è stato fuori rientra con più difficoltà).
12. **Mappa tra φ e occupazione.** Rendere esplicito come una quota di compiti automatizzati si traduce in calo
    dell'occupazione junior.
13. **Stile.** Introduzione più asciutta con i contributi nel secondo paragrafo; titolo più corto; "Proposition" →
    "Result" o "Lemma"; CRediT e affiliazioni.

## Decisioni da prendere (formato D)

| | Domanda | Raccomandazione |
|---|---|---|
| D21 | Rivista bersaglio | **A** SCED o JEBO (interventi 1–6). B JEDC (anche 7 e calibrazione SMM completa). |
| D22 | Automazione endogena | **A** impresa rappresentativa che sceglie φ ogni anno dentro il modello. B lasciare D15 come esercizio esterno. |
| D23 | IA come tutor | **A** due parametri (apprendimento dall'IA, calo dello sforzo), griglia nel testo. B rimandare a un altro articolo. |
| D24 | Validazione | **A** coorti della recessione con D19. B nessuna validazione esterna. |
| D25 | Struttura | **A** quattro scenari nel testo, varianti in robustezza o appendice. B tenere tutto nel testo. |
| D26 | Calibrazione | **A** SMM su 6–8 momenti più Sobol. B solo Sobol sulla calibrazione attuale. |

Ordine proposto: D25 e bibliografia (subito, sono solo testo), D24 e D23 (bassi costi, alto guadagno), D22, D26, poi
demografia e crescita se si punta a JEDC.
