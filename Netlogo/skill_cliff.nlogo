;; Skill cliff: gemello NetLogo del modello della prima versione dell'articolo (tag git articolo-v1).
;; Federico Bassi e Vincenzo Lio. Implementazione di riferimento: src/skillcliff (Python/NumPy).
;; Stesse regole, in ordine; i numeri casuali non sono gli stessi, quindi il confronto è statistico
;; (vedi Netlogo/LEGGIMI.md e scripts/docking_netlogo.py).
;;
;; Un tick = un anno. L'anno del modello t parte da -burn-in: le metriche si calcolano solo per
;; t >= 0 (anni registrati, da 0 a years - 1). L'IA arriva all'anno ai-start.
;;
;; Ordine degli eventi nell'anno t:
;;   1. invecchiamento: età +1; esperienza +1 e aggiornamento della familiarità con l'IA solo per
;;      chi era occupato l'anno prima (D19, D18)
;;   2. pensionamento (età >= retirement-age) e ingresso di altrettanti junior
;;   3. ruoli: junior se esperienza < junior-max-exp, senior se >= senior-min-exp
;;   4. IA: moltiplicatori di p, kappa, beta per gruppo; junior non occupati (margine "posto")
;;   5. coppie stabili con il mentore (D20, se attivo)
;;   6. incontri junior-senior dentro ogni gruppo di qualifica, con il vincolo di capacità
;;   7. apprendimento autonomo e obsolescenza; tutti i guadagni calcolati sullo stesso h
;;   8. metriche (solo negli anni registrati)

globals [
  t                          ; anno del modello (negativo durante il burn-in)
  A phi                      ; produttività dell'IA e quota di compiti automatizzati
  p-mult-L p-mult-H k-mult-L k-mult-H b-mult-L b-mult-H   ; moltiplicatori per gruppo (L, H)
  ; metriche dell'ultimo anno registrato
  H-agg Y F-users rent gini-w   ; H-agg = H (NetLogo non distingue H da h)
  B-meet B-aut B-total p-eff
  mean-h mean-h-junior mean-h-mid mean-h-senior
  n-junior n-mid n-senior n-meetings n-out
  n-pairs                    ; coppie stabili in corso (prima dei nuovi abbinamenti dell'anno)
]

turtles-own [
  age          ; anni compiuti
  experience   ; anni di esperienza da occupato (D19)
  high?        ; qualificato
  h            ; capitale umano
  out?         ; non occupato in quest'anno (junior che perdono il posto, D13)
  f            ; familiarità con l'IA, in [0, 1] (D18)
  mentor       ; mentore stabile (D20); nobody se non abbinato o se è andato in pensione
  h-prev       ; h a inizio anno
  gain         ; guadagno dagli incontri nell'anno
  dh           ; guadagno totale nell'anno
  met?         ; ha imparato da un senior nell'anno
]

;; ---------------------------------------------------------------------------------------------
;; Inizializzazione

to setup
  clear-all
  set t (- burn-in)
  create-turtles n-workers [
    init-worker
    ; età uniformi sulla carriera della propria qualifica; h viene portato a regime dal burn-in
    let career retirement-age - entry-age
    set experience floor (random-float 1 * career)
    set age entry-age + experience
  ]
  update-ai
  reset-ticks
end

to init-worker  ; turtle procedure: un nuovo entrante
  set high? random-float 1 < share-high
  set age entry-age
  set experience 0
  ; h0 = h0[qualifica] * exp(eps), eps ~ N(-sigma^2/2, sigma^2): rumore a media 1
  set h (ifelse-value high? [h0-high] [h0-low]) * exp (random-normal (-0.5 * h0-sigma * h0-sigma) h0-sigma)
  set out? false
  set f 0
  set mentor nobody
  set shape "circle"
  set size 0.8
  set hidden? not show-agents?
end

to-report entry-age  ; turtle reporter
  report ifelse-value high? [entry-age-high] [entry-age-low]
end

;; ---------------------------------------------------------------------------------------------
;; Un anno

to go
  if t >= years [ stop ]
  step
  tick
end

to step
  update-ai

  ; 1. invecchiamento (D19: l'esperienza cresce solo lavorando; D18: la familiarità pure)
  ask turtles [
    set age age + 1
    if not out? [
      set experience experience + 1
      if familiarity-on? and t - 1 >= ai-start [ set f f + gamma * (1 - f) ]
    ]
  ]

  ; 2. pensionamento e ingresso (popolazione stazionaria: un entrante per ogni pensionato)
  let retiring turtles with [age >= retirement-age]
  let n-new count retiring
  ask retiring [ die ]                          ; i loro junior restano senza mentore (nobody)
  create-turtles n-new [
    init-worker
    set f ifelse-value (familiarity-on? and t >= ai-start) [1] [0]
  ]

  ; 3. ruoli
  ask turtles [ set h-prev h  set gain 0  set met? false ]
  let juniors turtles with [experience < junior-max-exp]
  let seniors turtles with [experience >= senior-min-exp]

  ; 4. IA: moltiplicatori degli incontri e junior non occupati
  update-modifiers
  ask turtles [ set out? false ]
  if ai-on? and hits-junior? and margin-junior = "posto" [
    ask juniors with [in-hit-group?] [ if random-float 1 < phi [ set out? true ] ]
  ]

  ; 5. coppie stabili (D20): restano se il junior è ancora junior e occupato, il mentore è in
  ;    servizio e non c'è separazione (probabilità separation)
  ifelse stable-mentor? [
    ask turtles with [experience >= junior-max-exp] [ set mentor nobody ]
    ask juniors with [mentor != nobody] [
      if out? or random-float 1 < separation [ set mentor nobody ]
    ]
  ] [
    ask turtles [ set mentor nobody ]
  ]

  ; 6. incontri, dentro ogni gruppo di qualifica (decisione D1)
  let p-weighted 0
  let n-seekers 0
  set n-pairs 0
  foreach [false true] [ grp ->
    let js juniors with [high? = grp]
    let ss seniors with [high? = grp]
    let b-mult ifelse-value grp [b-mult-H] [b-mult-L]
    ; coppie in corso: imparano dal proprio mentore e occupano capacità
    let paired js with [mentor != nobody]
    ask paired [
      set gain beta * b-mult * max list 0 ([h-prev] of mentor - h-prev)
      set met? true
    ]
    let occupied count paired
    set n-pairs n-pairs + occupied
    ; chi cerca: p_eff = min(p, (kappa S - coppie in corso) / J)
    let seekers js with [not out? and mentor = nobody]
    let pg 0
    if any? seekers and any? ss [
      let cap kappa * (ifelse-value grp [k-mult-H] [k-mult-L]) * count ss
      set pg min list (p * (ifelse-value grp [p-mult-H] [p-mult-L])) (max list 0 (cap - occupied) / count seekers)
    ]
    set p-weighted p-weighted + pg * count seekers
    set n-seekers n-seekers + count seekers
    let ss-list [self] of ss
    let n-s length ss-list
    ask seekers [
      if random-float 1 < pg [
        let partner item (random n-s) ss-list
        set gain beta * b-mult * max list 0 ([h-prev] of partner - h-prev)
        set met? true
        if stable-mentor? [ set mentor partner ]
      ]
    ]
  ]
  set p-eff ifelse-value (n-seekers > 0) [p-weighted / n-seekers] [0]

  ; 7. apprendimento autonomo (alla Ben-Porath) e obsolescenza; i non occupati perdono solo d h
  ask turtles [
    ifelse out?
      [ set dh (- depreciation * h-prev) ]
      [ set dh gain + (delta0 * max list 0 (1 - experience / horizon) - depreciation) * h-prev ]
    set h h-prev + dh
  ]

  ; 8. metriche
  if t >= 0 [ record juniors seniors ]
  if show-agents? and t >= 0 [ draw ]
  set t t + 1
end

;; ---------------------------------------------------------------------------------------------
;; IA (fase 2)

to-report ai-on?
  report ai-target != "nessuna IA"
end

to-report familiarity-on?
  report ai-on? and familiarity?
end

to update-ai
  ; A_t = (1 + g)^(t - t0) per t >= t0;  phi_t = phi_max (1 - 1/A_t)
  set A ifelse-value (ai-on? and t >= ai-start) [(1 + g) ^ (t - ai-start)] [1]
  set phi ifelse-value ai-on? [phi-max * (1 - 1 / A)] [0]
end

to-report hits-junior?
  report member? ai-target ["junior" "qualificati" "non_qualificati"]
end

to-report hits-senior?
  report member? ai-target ["senior" "qualificati" "non_qualificati"]
end

to-report in-hit-group?  ; turtle reporter: il gruppo di qualifica è colpito dal bersaglio
  if ai-target = "qualificati" [ report high? ]
  if ai-target = "non_qualificati" [ report not high? ]
  report true
end

;; Tabella 2x2 (D16, D17): compiti -> junior p giù, senior beta giù;
;; posto -> junior non occupati, senior kappa giù. Complementare: beta * (1 + phi).
to update-modifiers
  set p-mult-L 1  set p-mult-H 1  set k-mult-L 1  set k-mult-H 1  set b-mult-L 1  set b-mult-H 1
  if not ai-on? [ stop ]
  if ai-target = "complementare" [
    set b-mult-L 1 + phi  set b-mult-H 1 + phi
    stop
  ]
  let cut-L ifelse-value (ai-target != "qualificati") [1 - phi] [1]
  let cut-H ifelse-value (ai-target != "non_qualificati") [1 - phi] [1]
  if hits-junior? and margin-junior = "compiti" [ set p-mult-L cut-L  set p-mult-H cut-H ]
  if hits-senior? [
    ifelse margin-senior = "compiti"
      [ set b-mult-L cut-L  set b-mult-H cut-H ]
      [ set k-mult-L cut-L  set k-mult-H cut-H ]
  ]
end

to-report user?  ; turtle reporter: lavora con l'IA al posto del bersaglio (D18)
  if out? [ report false ]
  if ai-target = "junior" [ report experience >= junior-max-exp ]
  if ai-target = "senior" [ report experience < senior-min-exp ]
  if ai-target = "qualificati" [ report high? ]
  if ai-target = "non_qualificati" [ report not high? ]
  report true                                   ; complementare: tutti
end

;; ---------------------------------------------------------------------------------------------
;; Metriche

to record [juniors seniors]
  let mids turtles with [experience >= junior-max-exp and experience < senior-min-exp]
  set n-junior count juniors
  set n-mid count mids
  set n-senior count seniors
  set n-out count turtles with [out?]
  set n-meetings count turtles with [met?]
  set H-agg sum [h] of turtles
  set mean-h mean [h] of turtles
  set mean-h-junior ifelse-value any? juniors [mean [h] of juniors] [0]
  set mean-h-mid ifelse-value any? mids [mean [h] of mids] [0]
  set mean-h-senior ifelse-value any? seniors [mean [h] of seniors] [0]
  ; B: crescita media del capitale umano dei junior (da incontri e autonoma)
  set B-meet ifelse-value any? juniors [mean [gain / h-prev] of juniors] [0]
  set B-aut ifelse-value any? juniors [mean [(dh - gain) / h-prev] of juniors] [0]
  set B-total B-meet + B-aut
  ; output, salari e rendita dell'IA (D18)
  let wages [h] of turtles
  ifelse familiarity-on? [
    let users turtles with [user?]
    let h-users sum [h] of users
    set F-users ifelse-value (h-users > 0) [sum [h * f] of users / h-users] [0]
    set wages [ifelse-value user? [h * (1 + theta * (A - 1) * f)] [h]] of turtles
  ] [
    set F-users 1
  ]
  set Y ifelse-value ai-on? [H-agg * (1 + theta * (A - 1) * F-users)] [H-agg]
  set rent Y - sum wages
  set gini-w gini wages
end

to-report gini [xs]
  let s sort xs
  let n-x length s
  let tot sum s
  if n-x = 0 or tot <= 0 [ report 0 ]
  let i 0
  let acc 0
  foreach s [ x ->
    set i i + 1
    set acc acc + i * x
  ]
  report 2 * acc / (n-x * tot) - (n-x + 1) / n-x
end

;; ---------------------------------------------------------------------------------------------
;; Vista: ogni lavoratore è un punto; x = età, y = capitale umano.
;; Verde = junior, grigio = intermedio, blu = senior, rosso = junior non occupato.

to draw
  ask turtles [
    set hidden? false
    setxy (min list max-pxcor age) (min list max-pycor (h * 12))
    set color ifelse-value out? [red]
      [ifelse-value (experience < junior-max-exp) [green]
        [ifelse-value (experience >= senior-min-exp) [blue] [gray]]]
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
625
10
939
325
-1
-1
6.0
1
10
1
1
1
0
0
0
1
15
65
0
50
1
1
1
anni
30.0

BUTTON
5
10
100
43
setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
105
10
200
43
go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
205
10
300
43
un anno
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
5
55
200
73
Popolazione e ruoli
12
0.0
1

SLIDER
5
75
200
108
n-workers
n-workers
500
50000
5000
500
1
NIL
HORIZONTAL

SLIDER
5
111
200
144
share-high
share-high
0
1
0.3
0.01
1
NIL
HORIZONTAL

SLIDER
5
147
200
180
entry-age-low
entry-age-low
15
30
20
1
1
NIL
HORIZONTAL

SLIDER
5
183
200
216
entry-age-high
entry-age-high
18
35
25
1
1
NIL
HORIZONTAL

SLIDER
5
219
200
252
retirement-age
retirement-age
50
75
65
1
1
NIL
HORIZONTAL

SLIDER
5
255
200
288
h0-low
h0-low
0.1
3
1.0
0.05
1
NIL
HORIZONTAL

SLIDER
5
291
200
324
h0-high
h0-high
0.1
3
1.5
0.05
1
NIL
HORIZONTAL

SLIDER
5
327
200
360
h0-sigma
h0-sigma
0
1
0.2
0.01
1
NIL
HORIZONTAL

SLIDER
5
363
200
396
junior-max-exp
junior-max-exp
1
15
5
1
1
NIL
HORIZONTAL

SLIDER
5
399
200
432
senior-min-exp
senior-min-exp
5
30
15
1
1
NIL
HORIZONTAL

SLIDER
5
435
200
468
burn-in
burn-in
0
500
300
10
1
NIL
HORIZONTAL

SLIDER
5
471
200
504
years
years
1
200
60
1
1
NIL
HORIZONTAL

TEXTBOX
210
55
405
73
Incontri e apprendimento
12
0.0
1

SLIDER
210
75
405
108
p
p
0
1
0.6
0.01
1
NIL
HORIZONTAL

SLIDER
210
111
405
144
kappa
kappa
0
2
0.2
0.01
1
NIL
HORIZONTAL

SLIDER
210
147
405
180
beta
beta
0
0.5
0.1
0.0001
1
NIL
HORIZONTAL

SLIDER
210
183
405
216
delta0
delta0
0
0.1
0.04
0.001
1
NIL
HORIZONTAL

SLIDER
210
219
405
252
horizon
horizon
10
100
50
1
1
NIL
HORIZONTAL

SLIDER
210
255
405
288
depreciation
depreciation
0
0.1
0.012
0.001
1
NIL
HORIZONTAL

TEXTBOX
210
299
405
317
Mentore stabile (D20)
12
0.0
1

SWITCH
210
319
405
352
stable-mentor?
stable-mentor?
1
1
-1000

SLIDER
210
355
405
388
separation
separation
0
1
1.0
0.01
1
NIL
HORIZONTAL

TEXTBOX
210
399
405
417
Vista
12
0.0
1

SWITCH
210
419
405
452
show-agents?
show-agents?
0
1
-1000

TEXTBOX
415
55
610
73
Intelligenza artificiale (fase 2)
12
0.0
1

CHOOSER
415
75
610
120
ai-target
ai-target
"nessuna IA" "junior" "senior" "qualificati" "non_qualificati" "complementare"
0

CHOOSER
415
123
610
168
margin-junior
margin-junior
"compiti" "posto"
0

CHOOSER
415
171
610
216
margin-senior
margin-senior
"compiti" "posto"
0

SLIDER
415
219
610
252
ai-start
ai-start
0
59
10
1
1
NIL
HORIZONTAL

SLIDER
415
255
610
288
g
g
0
0.1
0.03
0.005
1
NIL
HORIZONTAL

SLIDER
415
291
610
324
phi-max
phi-max
0
1
0.6
0.05
1
NIL
HORIZONTAL

SLIDER
415
327
610
360
theta
theta
0
0.5
0.02
0.005
1
NIL
HORIZONTAL

TEXTBOX
415
371
610
389
Familiarità con l'IA (D18)
12
0.0
1

SWITCH
415
391
610
424
familiarity?
familiarity?
0
1
-1000

SLIDER
415
427
610
460
gamma
gamma
0
1
0.1
0.01
1
NIL
HORIZONTAL

MONITOR
5
525
100
570
anno t
t
0
1
11

MONITOR
105
525
200
570
H
H-agg
0
1
11

MONITOR
205
525
300
570
B da incontri
B-meet
4
1
11

MONITOR
5
575
100
620
Gini dei salari
gini-w
3
1
11

MONITOR
105
575
200
620
non occupati
n-out
0
1
11

MONITOR
205
575
300
620
coppie stabili
n-pairs
0
1
11

PLOT
625
336
925
506
Capitale umano aggregato H
anno
H
0.0
60.0
0.0
0.1
true
true
"" ""
PENS
"H" 1.0 0 -16777216 true "" "if t > 0 [ plotxy (t - 1) H-agg ]"
"Y" 1.0 0 -13345367 true "" "if t > 0 [ plotxy (t - 1) Y ]"

PLOT
930
336
1230
506
Apprendimento junior (B)
anno
tasso
0.0
60.0
0.0
0.1
true
true
"" ""
PENS
"da incontri" 1.0 0 -13345367 true "" "if t > 0 [ plotxy (t - 1) B-meet ]"
"autonomo" 1.0 0 -2674135 true "" "if t > 0 [ plotxy (t - 1) B-aut ]"

PLOT
625
511
925
681
h medio per ruolo
anno
h
0.0
60.0
0.0
0.1
true
true
"" ""
PENS
"junior" 1.0 0 -10899396 true "" "if t > 0 [ plotxy (t - 1) mean-h-junior ]"
"intermedi" 1.0 0 -7500403 true "" "if t > 0 [ plotxy (t - 1) mean-h-mid ]"
"senior" 1.0 0 -13345367 true "" "if t > 0 [ plotxy (t - 1) mean-h-senior ]"

PLOT
930
511
1230
681
Gini dei salari
anno
Gini
0.0
60.0
0.0
0.1
true
true
"" ""
PENS
"Gini" 1.0 0 -2674135 true "" "if t > 0 [ plotxy (t - 1) gini-w ]"
@#$#@#$#@
## COS'È

La *skill cliff*: un modello ad agenti sulla trasmissione del capitale umano tra senior e junior e sugli effetti ritardati dell'intelligenza artificiale. Federico Bassi e Vincenzo Lio.

Questo è il gemello NetLogo del modello della **prima versione dell'articolo** (tag git `articolo-v1` del repository `ViciusLio/skill-cliff-abm`), cioè la fase 2 con le revisioni D16–D20. L'implementazione di riferimento è in Python (`src/skillcliff`): le regole sono le stesse, nello stesso ordine. I numeri casuali sono diversi, quindi i due modelli coincidono in distribuzione, non run per run. Il confronto statistico è in `scripts/docking_netlogo.py`.

## COME FUNZIONA

Un tick è un anno. Ogni lavoratore ha età, esperienza, qualifica (L o H) e capitale umano h.

- **Ruoli.** Junior se l'esperienza è sotto `junior-max-exp` (5), senior da `senior-min-exp` (15).
- **Incontri.** Ogni anno un junior incontra con probabilità p_eff un senior della propria qualifica, estratto a caso, e impara beta · max(0, h_senior − h_junior). Capacità: p_eff = min(p, kappa · S / J) per gruppo.
- **Apprendimento autonomo e obsolescenza.** dh = (delta0 · max(0, 1 − s/horizon) − depreciation) · h, con s l'esperienza.
- **Demografia.** Si va in pensione a `retirement-age`; per ogni pensionato entra un junior con h0 lognormale.
- **Esperienza (D19).** Cresce solo negli anni da occupato.
- **IA (fase 2).** Dall'anno `ai-start` la produttività A = (1+g)^(t−ai-start) automatizza una quota phi = phi-max · (1 − 1/A) del lavoro del bersaglio. Output Y = H · (1 + theta · (A − 1) · F).
- **Che cosa vuol dire "sostituire" (D16, D17):**

| | compiti (resta al lavoro) | posto (lo perde) |
|---|---|---|
| junior | p · (1 − phi) | non occupato con probabilità phi: niente incontri, niente esperienza, solo obsolescenza |
| senior | beta · (1 − phi) | kappa · (1 − phi): meno mentori |

  "qualificati" e "non_qualificati" applicano le due righe solo a quel gruppo; "complementare" moltiplica beta per (1 + phi).
- **Familiarità con l'IA (D18).** Chi entra dopo l'arrivo dell'IA ha f = 1; chi c'era parte da 0 e, per ogni anno da occupato, f ← f + gamma · (1 − f). F è la media di f, pesata con h, tra chi usa l'IA (i lavoratori non sostituiti). I salari di chi usa l'IA sono h · (1 + theta · (A − 1) · f); il resto dell'output è la rendita dell'IA.
- **Mentore stabile (D20, variante).** Con `stable-mentor?` acceso il junior tiene lo stesso senior finché è junior e occupato, il mentore è in servizio e la coppia non si scioglie (probabilità annua `separation`). Le coppie occupano capacità. Con `separation` = 1 si ritrova il modello base.

## COME SI USA

1. Premi **setup**, poi **go**. I primi `burn-in` anni (300) portano il modello a regime e non vengono registrati: la vista e i grafici partono dall'anno 0. Per andare più veloci spegni `show-agents?` o sposta il cursore della velocità.
2. **Vista:** ogni punto è un lavoratore; x = età, y = capitale umano. Verde = junior, grigio = intermedio, blu = senior, rosso = junior non occupato.
3. **Scenari dell'articolo** (impostazioni di `ai-target` e dei margini):
   - senza IA: `nessuna IA`;
   - IA che toglie compiti ai junior: `junior`, `margin-junior` = compiti;
   - junior che perdono il posto: `junior`, `margin-junior` = posto;
   - IA che toglie compiti ai senior: `senior`, `margin-senior` = compiti;
   - senior che perdono il posto: `senior`, `margin-senior` = posto;
   - mentore stabile della sezione 10 della sintesi: `stable-mentor?` acceso, `separation` = 0,15, `beta` = 0,0754.
4. **BehaviorSpace** (menu Tools) contiene già un esperimento per ciascuno di questi scenari: 10 repliche, metriche registrate negli anni 1–60 (`t > 0`, cioè gli anni 0–59 del modello).

I valori iniziali dei cursori sono quelli di `configs/base.yaml`.

## COSE DA NOTARE

- Nella base, il capitale umano dei senior non cambia per 10 anni dopo una riduzione degli incontri (Proposizione 2): si vede impostando l'IA sui junior e guardando "h medio per ruolo".
- Con N = 5.000 (come nella fase 1) i risultati sono rumorosi run per run: l'articolo usa medie su 30 repliche e, per la fase 2, N = 50.000.

## DIFFERENZE DAL MODELLO PYTHON

- **Numeri casuali.** Nessun accoppiamento tra scenari (in Python ogni scenario usa gli stessi numeri casuali dello scenario senza IA). In NetLogo si confrontano medie tra repliche.
- **Qualifica.** Gli incontri avvengono sempre dentro la stessa qualifica (`same_qual: true` in Python, l'unico caso usato nell'articolo).
- **Esperimenti di calcolo.** La corsa, le griglie su g e theta, l'automazione scelta dall'impresa (D15) e la calibrazione di beta per il mentore stabile restano negli script Python.

## CREDITI

Federico Bassi e Vincenzo Lio, 2026. Codice e documentazione: https://github.com/ViciusLio/skill-cliff-abm
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
set model-version "sheep-wolves-grass"
set show-energy? false
setup
repeat 75 [ go ]
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="base" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;nessuna IA&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="junior_compiti" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;junior&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="margin-junior">
      <value value="&quot;compiti&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="junior_posto" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;junior&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="margin-junior">
      <value value="&quot;posto&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="senior_compiti" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;senior&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="margin-senior">
      <value value="&quot;compiti&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="senior_posto" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;senior&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="margin-senior">
      <value value="&quot;posto&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="complementare" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;complementare&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="mentore_stabile" repetitions="10" runMetricsEveryStep="true">
    <setup>random-seed (20261008 + behaviorspace-run-number)
setup</setup>
    <go>go</go>
    <timeLimit steps="360"/>
    <metric>t</metric>
    <metric>H-agg</metric>
    <metric>Y</metric>
    <metric>B-meet</metric>
    <metric>B-aut</metric>
    <metric>mean-h</metric>
    <metric>mean-h-junior</metric>
    <metric>mean-h-senior</metric>
    <metric>gini-w</metric>
    <metric>F-users</metric>
    <metric>rent</metric>
    <metric>p-eff</metric>
    <metric>n-junior</metric>
    <metric>n-senior</metric>
    <metric>n-out</metric>
    <metric>n-pairs</metric>
    <metric>n-meetings</metric>
    <runMetricsCondition>t &gt; 0</runMetricsCondition>
    <enumeratedValueSet variable="show-agents?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ai-target">
      <value value="&quot;nessuna IA&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="stable-mentor?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="separation">
      <value value="0.15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="beta">
      <value value="0.0754"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
1
@#$#@#$#@
