# La bottega vuota

*Che cosa succede alle competenze di un paese quando l'intelligenza artificiale toglie ai giovani le occasioni di imparare dai più esperti. Un modello, dieci anni di silenzio e una scogliera.*

---

Questo articolo racconta i risultati di un modello costruito con Federico Bassi, in una versione base e in una estesa ancora in costruzione. È nato in dialogo con un'intelligenza artificiale, che mi ha aiutato a scrivere il codice, a controllare i numeri e a criticare le mie idee. Le tesi, le scelte e gli errori sono nostri.

---

Ogni giovedì, alle sette di sera, il professor Ruggiero restituisce a Marta il capitolo che lei gli ha mandato.

È pieno di correzioni a matita. Una virgola spostata, un aggettivo cancellato, e ogni tanto una frase a margine: *"Un revisore questo lo legge come un risultato non dimostrato. Riformula."* Marta è dottoranda da otto mesi. Ruggiero insegna da trentadue anni.

Nessun manuale le avrebbe insegnato che quella frase suonava come un risultato non dimostrato. Lo sa Ruggiero, perché l'ha visto succedere, a sé e ai suoi studenti, decine di volte. E adesso, una correzione alla volta, lo sa anche Marta.

L'università, a modo suo, è ancora una bottega: come negli studi dei pittori del Rinascimento, il mestiere si impara guardando lavorare chi lo sa fare, e facendosi correggere.

L'anno scorso il dipartimento ha attivato un assistente di intelligenza artificiale che scrive e corregge le bozze. Sono buone, a volte ottime. Ruggiero le rilegge in dieci minuti invece di correggere quelle di Marta in un'ora. Il dipartimento risparmia ore, e Ruggiero ha più tempo per i suoi progetti. E Marta scrive sempre meno da sola.

Nessuno, nel dipartimento, ha perso il posto. Ma il giovedì sera, sulla scrivania di Ruggiero, ci sono meno fogli da correggere.

La domanda di questo articolo è semplice: **fra quindici anni, quando Ruggiero sarà in pensione, chi correggerà le tesi degli studenti?**

Do subito un nome alle due figure, perché ci accompagneranno fino alla fine. Chiamo **junior** chi è all'inizio e impara: Marta. Chiamo **senior** chi ha esperienza e insegna: Ruggiero. E chiamo **incontro** ogni occasione in cui il primo impara dal secondo lavorando: un capitolo corretto, un pomeriggio in laboratorio, una discussione dopo il seminario.

Vale un patto, come sempre: quello che segue viene da un modello, non dai dati. I numeri indicano direzioni e ordini di grandezza, non previsioni. I risultati della versione estesa, che racconto in una sezione a parte, sono ancora più provvisori. E l'università è solo l'esempio: lo stesso vale per un'officina, uno studio professionale, un ospedale, un'azienda.

## Un numero che nessuno spiegava

Nel 1988 Robert Lucas, premio Nobel per l'economia, scrisse un'equazione per spiegare perché alcuni paesi crescono e altri no. Il motore era il capitale umano: quello che le persone sanno fare. Nell'equazione c'era un numero, che chiamò B: l'efficienza con cui si impara. Due persone che studiano per lo stesso tempo imparano di più se B è alto.

Lucas fissò B e andò avanti. Non spiegò da dove venisse.

Eppure chiunque abbia studiato lo sa: si impara a velocità molto diverse a seconda di chi si ha accanto. Marta impara più in fretta di una dottoranda che lavora da sola con un motore di ricerca. Il suo B è più alto, e non per merito suo. È più alto perché c'è Ruggiero.

Più tardi lo stesso Lucas scrisse che la conoscenza si acquisisce negli incontri tra chi sa di più e chi sa di meno. E chi ha misurato questo effetto sui dati trova che imparare dai colleghi vale tra il 4 e il 9 per cento dello stipendio, ogni anno.

Se B nasce dagli incontri, allora una tecnologia che toglie incontri toglie anche B. Non subito, e non in modo visibile.

## Il modello in una pagina

Con Federico abbiamo costruito un modello ad agenti. È un modo di fare economia al computer: invece di scrivere un'equazione per l'intera economia, si simulano tante persone, ciascuna con regole semplici, e si guarda che cosa succede tutte insieme.

Le nostre persone sono cinquemila lavoratori. Ogni anno:

- **invecchiano** di un anno e, se lavorano, guadagnano un anno di esperienza;
- **chi ha meno di cinque anni di esperienza è junior**, chi ne ha più di quindici è senior;
- **ogni junior incontra un senior** del suo campo con una certa probabilità, e impara una parte della differenza tra quello che sa il senior e quello che sa lui;
- **tutti imparano anche da soli**, sempre meno con gli anni, e dimenticano un po';
- **chi arriva a 65 anni va in pensione** e al suo posto entra un giovane.

Tutto qui. Nessuno sceglie niente: le persone seguono le regole. È una scelta voluta: prima vogliamo capire bene il meccanismo, poi aggiungere i comportamenti.

Questa è la **versione base**, quella dell'articolo scientifico. Poi ce n'è una **versione estesa**, in cui aggiungiamo un pezzo alla volta quello che la base lascia fuori: un'impresa che sceglie, un'IA che insegna. La racconto più avanti, in una sezione a parte.

Con queste regole il modello riproduce due cose vere. Lo stipendio cresce lentamente e smette di salire dopo circa 34 anni di carriera, come nel settore privato italiano. E il 62% di quello che impara un junior viene dagli incontri con i senior.

## Dieci anni di silenzio

Il primo esperimento non riguarda ancora l'intelligenza artificiale. Dimezziamo le occasioni d'incontro, una volta per tutte, e guardiamo che cosa succede.

I junior se ne accorgono subito: dopo quattro anni sanno il 5,7% in meno.

I senior no. Per dieci anni il loro capitale umano resta **esattamente** uguale. Non quasi uguale: identico, fino all'ultima cifra. All'undicesimo anno comincia a scendere. Dopo 25 anni è più basso del 3,6%, alla fine del 6,7%.

Chiamiamo questa caduta ritardata *skill cliff*: la scogliera delle competenze. Si cammina in piano per dieci anni, e poi il terreno manca.

Un esempio dal dipartimento. Ruggiero ha imparato il mestiere negli anni Novanta, da un professore che gli correggeva la tesi come lui la corregge a Marta. Se oggi Marta riceve meno correzioni, Ruggiero non perde niente: quello che sa l'ha già imparato. Il problema arriva quando Marta diventerà professoressa, fra una decina d'anni, e avrà da insegnare meno di quanto Ruggiero insegnava a lei. E i suoi studenti impareranno ancora meno.

Il ritardo non è un caso. È la distanza tra la fine dell'apprendistato (5 anni) e l'inizio dell'esperienza piena (15 anni), più uno. Nell'articolo scientifico lo dimostriamo in poche righe: chi è senior nei prossimi dieci anni si è formato prima della riduzione degli incontri.

Dove l'esempio si rompe: nella realtà il confine tra junior e senior è sfumato, e il ritardo non sarebbe di dieci anni esatti. Ma l'ordine di grandezza resta quello di una generazione professionale.

Ed è questo il punto. I primi dati dicono che l'IA generativa sta riducendo le assunzioni dei giovani nei lavori più esposti. Sono dati sui junior di oggi. Sui senior di domani, per dieci anni, ogni indicatore dirà che non è successo niente.

## Togliere i compiti o togliere il posto

Che cosa vuol dire, in concreto, che l'IA "sostituisce" qualcuno? Federico me l'ha chiesto all'inizio, e la domanda ha cambiato il modello. Ci sono quattro risposte possibili.

| | Resta, ma perde dei compiti | Perde il posto |
|---|---|---|
| **Junior** | Marta scrive meno da sola: meno incontri | il dipartimento non finanzia la borsa di dottorato |
| **Senior** | Ruggiero corregge di meno: ogni incontro insegna meno | Ruggiero va in pensione e non viene sostituito: meno maestri |

Facciamo arrivare l'IA e guardiamo cinquant'anni dopo.

**Togliere compiti ai junior** riduce il capitale umano dell'economia del 5,2% e quasi dimezza quello che si impara dagli incontri. È come crescere 0,11 punti percentuali in meno ogni anno, per cinquant'anni.

**Togliere compiti ai senior** costa esattamente lo stesso: 5,2%. È il risultato che mi ha sorpreso di più, e che nel modello ha una spiegazione semplice: quello che un junior impara dipende dal prodotto di due cose, quante volte incontra un senior e quanto impara ogni volta. Dimezzare l'una o l'altra dà lo stesso risultato.

Un esempio dal dipartimento. Marta può avere metà dei capitoli corretti da Ruggiero, oppure tutti i capitoli con metà delle correzioni. Alla fine dell'anno ha imparato più o meno lo stesso.

Cambia però chi ci rimette. Nel primo caso alcuni studenti imparano e altri no; nel secondo imparano tutti un po' meno. E cambia chi guadagna dall'IA: se sostituisce i junior, il guadagno va ai più esperti, e la disuguaglianza degli stipendi cresce; se sostituisce i senior, va ai più giovani, che con l'IA sono cresciuti e la usano meglio.

**Se i junior perdono il posto** la formazione non si perde, si rinvia. Chi non ottiene la borsa resta "junior" più a lungo, e quando entra impara comunque dai senior. Il costo è nelle carriere più brevi: la perdita è del 5,7%, e cinquant'anni dopo i senior sono l'11% in meno.

**Se i senior perdono il posto**, quasi non succede niente. Ma solo perché nel modello i potenziali maestri sono più di quelli che servono. Se i maestri sono già pochi, come in un dipartimento dove ogni professore segue troppi studenti, la perdita sale al 4,8%. Quanti senior facciano davvero da maestri, in Italia, non lo sa nessuno. È uno dei numeri che più varrebbe la pena misurare.

## La corsa

L'IA non toglie soltanto: rende anche più produttivi. Il conto finale è una corsa tra due velocità: quanto in fretta l'IA aumenta la produzione, e quanto in fretta si erode la conoscenza su cui si appoggia.

Con una stima prudente del guadagno di produttività, quella dell'economista Daron Acemoglu, l'IA da sola farebbe crescere la produzione del 6,5% in cinquant'anni. Con la perdita di capitale umano il guadagno si ferma allo 0,9%.

La scogliera si mangia l'86% del guadagno. E già dopo dieci anni, quando nessun senior ha ancora perso niente, se ne è mangiato più della metà: la perdita dei junior pesa subito.

## Perché si automatizza troppo

Se il conto è così sfavorevole, perché il dipartimento attiva l'assistente?

Perché il conto non lo paga il dipartimento. Il dipartimento risparmia ore di correzione oggi. Quello che Marta avrebbe imparato, e insegnato fra quindici anni, andrà a vantaggio dell'università dove vincerà un concorso, degli studenti che formerà, dei lavori che scriverà. Nessuna voce di bilancio lo registra. Per un'impresa privata, che risparmia uno stipendio, è ancora più evidente.

È la stessa struttura dell'inquinamento: chi inquina ha un vantaggio subito, chi paga è lontano nel tempo e spesso non è ancora nato.

Nella versione base lo misuriamo così: un'impresa e un pianificatore che pensa al bene comune scelgono quanta parte del lavoro dei junior automatizzare. L'impresa sceglie il 30%. Il pianificatore che guarda a cinquant'anni sceglie il 9%. E la scelta dell'impresa, su cinquant'anni, vale meno di non automatizzare affatto.

Su dieci anni, invece, le due scelte quasi coincidono. Chi ragiona sul bilancio dell'anno, o sul prossimo ciclo elettorale, sceglie come l'impresa, perché il danno arriva dopo. È la scogliera vista da chi decide: per dieci anni il conto non arriva, e quando arriva è tardi.

## La versione estesa: quando il modello si complica

La versione base ha due semplificazioni che un economista nota subito. Nessuno sceglie niente: la quota di lavoro automatizzata cresce da sola, con la potenza dell'IA. E l'IA toglie e basta: non insegna niente a nessuno. Nella versione estesa abbiamo tolto queste due semplificazioni, una alla volta, controllando ogni volta che, spente le aggiunte, il modello tornasse identico alla base.

### Un'impresa che sceglie

La prima aggiunta è un'impresa che ogni anno decide quanto lavoro dei junior affidare all'IA. Il criterio è quello di qualunque bilancio: automatizza i compiti per cui l'IA costa meno di un junior. All'inizio l'IA costa cara e si automatizza poco; poi diventa più economica e si automatizza di più. Abbiamo regolato i costi in modo che, dopo dieci anni, l'impresa automatizzi la stessa quota della versione base.

Il primo risultato è quasi una conferma. Un'impresa miope, che guarda solo ai costi di oggi, si comporta quasi come la versione base: dopo cinquant'anni il capitale umano è più basso del 5,1% invece del 5,2%. La piccola differenza ha una spiegazione curiosa: i junior formati peggio valgono meno sul mercato, quindi costano meno, e l'impresa ha un po' meno convenienza a sostituirli.

Il secondo risultato è quello nuovo. Facciamo in modo che l'impresa tenga conto di una parte di quello che i suoi junior imparano lavorando, del loro valore formativo. Un'impresa miope ottiene circa metà del valore che potrebbe ottenere, sommando produzione e risparmi su cinquant'anni. Un'impresa che tiene conto di tre quarti del valore formativo ottiene il valore più alto tra quelli che abbiamo provato. Ma non smette di automatizzare. Aspetta: per circa trentacinque anni non tocca il lavoro dei junior, poi automatizza comunque un terzo dei loro compiti.

Questa è la cosa che mi sembra più utile da dire a chi decide. **L'ottimo non è automatizzare meno. È automatizzare più tardi**, quando chi deve imparare ha già imparato. È il passo in più rispetto alla versione base, dove impresa e pianificatore sceglievano una quota fissa: anche la migliore quota fissa fa peggio dell'impresa che aspetta. Conta il *quando*, più del *quanto*.

Un esempio dal dipartimento. Un dipartimento lungimirante non rinuncia all'assistente IA. Lo usa per le pratiche, le bibliografie, le traduzioni, e lascia a Marta i capitoli da scrivere e a Ruggiero quelli da correggere, finché Marta non sa scriverli da sola.

Quanto dovrebbe costare l'automazione, con un contributo pubblico, perché anche l'impresa miope scelga così? Nel modello, quasi il triplo del costo dell'IA. È un numero da prendere con le pinze, perché dipende da come si misura il valore formativo di un anno da junior. Ma dice una cosa vera: quel valore è grande, circa due terzi di uno stipendio da junior, e nessun bilancio lo vede.

### Un'IA che insegna

La seconda aggiunta risponde a un'obiezione seria, che vale la pena prendere sul serio. Gli esperimenti dicono che l'IA aiuta soprattutto chi ha meno esperienza. Se Marta può chiedere all'IA perché quella frase sembra un risultato non dimostrato, non le serve Ruggiero.

Attenzione a non confonderla con la leva che vedremo tra poco, l'IA che aiuta Ruggiero a insegnare meglio: qui l'IA insegna direttamente a Marta. Nella versione estesa il junior impara anche dall'IA, che però sa solo quello che ha imparato dai senior di oggi, e solo la parte che si può scrivere. E chi usa l'IA, forse, si sforza un po' meno di imparare da solo.

La risposta dipende quasi solo da una cosa: **quanta parte della conoscenza di Ruggiero l'IA riesce a catturare**.

- Se ne cattura metà, aiuta poco: recupera tra il 7 e il 14% della perdita. Sa meno di quello che Marta sa già, e serve solo agli studenti più indietro.
- Se ne cattura tre quarti o più, compensa tutta la perdita, e anche di più.
- Ma basta che chi usa l'IA si sforzi un quarto in meno di imparare da solo, e la perdita quasi raddoppia.

Un esempio dal dipartimento. L'IA può spiegare a Marta un teorema meglio di molti libri. Può anche dirle, in astratto, che certe frasi promettono più di quello che dimostrano. Più difficile che sappia come leggerà quel capitolo il revisore di quella rivista, o quale domanda le farà la commissione. Ruggiero lo sa perché c'era.

Dove l'esempio si rompe: nessuno sa davvero quanta parte di quella conoscenza le prossime IA riusciranno a catturare. Il modello non risponde a questa domanda. Dice che è la domanda giusta.

### Provarlo con le proprie mani

Anche la versione estesa esiste in NetLogo, il programma con cui molti scienziati sociali costruiscono questi modelli. Si accende l'impresa che sceglie, si sposta il cursore del valore formativo, e si vede l'automazione slittare di decenni.

## Che cosa può fare chi decide

Il modello permette di confrontare quattro leve con la stessa misura: quanta parte della perdita recuperano, se applicate con la stessa intensità.

1. **Apprendistati veri**, come dottorati e tirocini in cui i giovani lavorano su problemi reali accanto ai senior: più occasioni d'incontro.
2. **Tempo riservato a insegnare**, come ore di supervisione protette dal resto del lavoro: più maestri disponibili.
3. **IA che aiuta i senior a insegnare**, invece di sostituire chi impara: incontri più efficaci.
4. **Un contributo sull'automazione dei compiti d'ingresso**.

Il risultato è che **la leva giusta dipende da che cosa manca**.

Se agli studenti mancano le occasioni, come quando l'IA scrive al posto di Marta, gli apprendistati funzionano e il tempo per la supervisione non serve a nulla: Ruggiero il tempo ce l'ha, è Marta che non ha capitoli da fargli leggere. Se invece mancano i maestri, come quando i professori vanno in pensione e non vengono sostituiti, vale il contrario: si possono moltiplicare le occasioni quanto si vuole, ma non c'è nessuno a cui portare i capitoli.

Una leva funziona in entrambi i casi: rendere più efficace ogni incontro. Un senior che insegna meglio, magari con l'aiuto dell'IA, serve sempre.

Per un'università o un'impresa che investe nelle persone, quindi, la prima domanda non è quanto spendere. È: **ai nostri junior mancano le occasioni per imparare, o ai nostri senior il tempo per insegnare?**

E per chi governa, il consiglio è misurare prima che sia tardi. Quando il calo si vede nei senior, sono passati dieci anni. I numeri da guardare adesso sono altri: quanti giovani si assumono, quanti junior ci sono per ogni senior, quanto tempo si dedica a insegnare.

## Che cosa il modello non dice

Un modello è una mappa, non il territorio. Ecco i suoi limiti principali.

- **Nella versione base nessuno sceglie**: né i lavoratori, né le imprese. Non ci sono prezzi, né mercati. La versione estesa aggiunge un'impresa, ma una sola: nessuno si contende i junior formati, e chi forma un giovane non lo perde. È il prossimo passo.
- **L'economia non cresce**: la perdita è di livello, non di velocità di crescita. Alla lunga si ferma.
- **Diversi numeri sono scelti a mano.** Per questo, nella versione base, li abbiamo fatti variare tutti insieme su intervalli ampi, in 704 combinazioni: i livelli cambiano, ma il segno no. La perdita di competenze dovuta all'IA non diventa mai un guadagno, e l'impresa automatizza sempre troppo.
- **Nella versione estesa due numeri decidono quasi tutto** e nessuno li conosce: quanto vale, davvero, un anno da junior, e quanta conoscenza dei senior l'IA riesce a catturare. Sono le prime cose da misurare.

C'è anche un controllo che il modello ha superato senza che lo avessimo preparato. Chi si laurea durante una recessione guadagna meno per molti anni: dopo quindici anni, negli Stati Uniti, resta circa il 40% della perdita iniziale. Il modello, senza essere stato costruito per questo, ne lascia il 30%. Non è una prova. È un buon segno.

## Il giovedì, alle sette

Torniamo al dipartimento.

Fra quindici anni Ruggiero sarà in pensione, e Marta sarà professoressa. Saprà scrivere bene, perché l'IA l'avrà aiutata. Saprà anche, forse, molte cose che Ruggiero non sapeva.

Ma ci sarà una cosa che non avrà imparato: perché quella frase, davanti a quel revisore, sembrava un risultato non dimostrato. Nessuno gliel'ha corretta, perché quel capitolo l'aveva scritto l'IA.

E il giovedì sera, quando una sua studentessa le porterà i fogli, avrà meno da scrivere a margine.

La versione estesa indica due vie d'uscita, nessuna gratuita: automatizzare più tardi, quando Marta avrà imparato; oppure costruire un'IA che sappia davvero quello che sa Ruggiero, e usarla senza smettere di sforzarsi.

Non è una profezia. Il modello non dice che le competenze debbano crollare. Dice che cosa succede se lo permettiamo senza accorgercene, e quanto tempo abbiamo prima che sia troppo tardi per accorgersene: una decina d'anni.

Il tempo, cioè, che serve a una dottoranda per diventare la professoressa che correggerà le tesi della prossima.

---

*Il modello, il codice e l'articolo scientifico (in inglese, con la traduzione italiana) sono pubblici: [github.com/ViciusLio/skill-cliff-abm](https://github.com/ViciusLio/skill-cliff-abm). C'è anche una versione del modello per NetLogo, per chi vuole provarlo con le proprie mani; la versione estesa è nel ramo `esteso` del repository. I personaggi del dipartimento sono inventati. L'articolo si collega a "La Zecca Cognitiva: l'inflazione del capitale umano nell'era dell'intelligenza artificiale".*

**Riferimenti**

Lucas, R. E. (1988), "On the mechanics of economic development", *Journal of Monetary Economics*, 22(1), 3–42.

Lucas, R. E. e Moll, B. (2014), "Knowledge growth and the allocation of time", *Journal of Political Economy*, 122(1), 1–51.

Jarosch, G., Oberfield, E. e Rossi-Hansberg, E. (2021), "Learning from coworkers", *Econometrica*, 89(2), 647–676.

Ide, E. (2026), "Automation, AI, and the intergenerational transmission of knowledge", IESE Business School, working paper.

Acemoglu, D. (2024), "The simple macroeconomics of AI", NBER Working Paper 32487.

Brynjolfsson, E., Li, D. e Raymond, L. (2025), "Generative AI at work", *Quarterly Journal of Economics*, 140(2), 889–942.

Kahn, L. B. (2010), "The long-term labor market consequences of graduating from college in a bad economy", *Labour Economics*, 17(2), 303–316.

Oreopoulos, P., von Wachter, T. e Heisz, A. (2012), "The short- and long-term career effects of graduating in a recession", *American Economic Journal: Applied Economics*, 4(1), 1–29.
