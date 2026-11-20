# Row IC, the second commit — DIRECTIVES — the blind reading (November 19, 2026)

**Written before any frame was shot.** The questions, the frames they are asked of, the answer key and
the bar below were fixed first; the frames were shot afterwards from the real client at the first player's
own setup (Interface Scale 1.8 on a 5120 x 1377 window: a logical view of 2844 x 765), by the instrument
(`tools/dd_b_play.py`, `DD_B_UI_SCALE=1.8 DD_B_WINDOW=5120x1377`), on the shipped 1805 boot. The board
facts the key leans on were read from the backend first (`/command` with `list_first` — a read that
changes nothing), never from a frame.

## The frames (planned)

| Frame | What is on the screen |
|---|---|
| **L** | The first morning. The player has typed "Ney, Davout, Soult and Lannes, march to Lorraine" and pressed Enter: the LIST card stands — a row a corps with a tick, "Will not go:", the total against the actions in hand, the help line, "Give the order (Enter)". |
| **A** | An army named "the Army of Italy" (Lannes and Murat) and its chip pressed: the chip lit on the marshal row, its corps selected on the map, the selection card's group face ("Hold…", "Fortify…", "Drill…", "Disband the Army of Italy"). |
| **G** | "the war goal is Vienna" given: the desk card's THE WAR line, and the map with Vienna's gold ring. |

## The board the key leans on (read from the backend, November 19, 2026)

The list for "Ney, Davout, Soult and Lannes, march to Lorraine" on the 1805 boot (4 actions in hand):
Ney — march to Lorraine, 2 actions, ticked · Davout — march to Lorraine, 2 actions, ticked · Lannes — march
to Lorraine, 2 actions, NOT ticked (the actions run out with Ney and Davout) · Soult — will not go:
"already stands at Lorraine" · total 4 of the 4 in hand.

## The questions

| # | Frame | Question |
|---|---|---|
| 1 | L | If you press "Give the order", what happens — which corps receive an order, and what is it? |
| 2 | L | What will this cost, and can you afford it? |
| 3 | L | Who will not go, and why? |
| 4 | L | How would you leave Davout out of this order? |
| 5 | L | Once it is given, how would you undo the whole order — and what would that undo? |
| 6 | A | How would you order every corps of the Army of Italy to hold? |
| 7 | G | What is this war's goal, and where is it on the map? |
| 8 | all | What, if anything, confused you? (Asked of every reader; not scored.) |

## The answer key

| # | A right answer must say |
|---|---|
| 1 | Ney and Davout — the two ticked rows — each march to Lorraine, sent together as one order. Lannes (not ticked) and Soult (who will not go) are not ordered. |
| 2 | 4 actions; 4 are in hand — yes (it takes all of them). |
| 3 | Soult — he already stands at Lorraine. |
| 4 | Untick his row: click it (or move to it with Up/Down and press Space). |
| 5 | Take back (Ctrl+Z); it undoes the whole order — every corps it went to — at once. |
| 6 | Either: the army's chip has selected its corps, so press "Hold…" on the card (it shows the list first, then Give) — or type "Army of Italy, hold". One of the two is enough. |
| 7 | Vienna; it is the province ringed in gold on the map (the card's THE WAR line names it). |

## The bar

Three fresh readers (Sonnet) who have never seen the game are shown only the frames and asked the
questions. **The bar is met only if EVERY reader answers EVERY scored question (1–7) right by the key.** A
reader's "I cannot tell" on what the key asks is a miss. A miss is reported as a miss; a lever built from it
gets another reading with fresh readers. What the readers say confused them is ruled row by row: built, or
said why not.

## Reading 1 — `reading1/` — MET (21 of 21), one answer hedged

The frames as shot (`reading1/`, the build after the real client was pressed by hand — see "Pressed in the
real client" below). The readers were Explore agents, which carry no project instructions, told to open the
seven frames and nothing else. Their answers, as returned: `reading1/answers.json`.

Every reader named Ney and Davout, each marching to Lorraine, with Lannes unticked and Soult out (1); 4
actions of the 4 in hand (2); Soult, who already stands at Lorraine (3); untick his row — a click, or
Up/Down and Space (4); Take back, which undoes the whole order (5); the "Hold…" on the Army of Italy's card,
and the typed "Army of Italy, hold" from the log (6); Vienna, ringed in gold on the map (7).

**Recorded with its hedge, as given:** reader 3, question 6 — "Its panel has a 'Hold...' button, and the log
text says to say 'Army of Italy, hold'. Either would order that army to hold. … I cannot tell from the
screenshots whether this reaches every corps. The panel names only Lannes and Murat … So I cannot tell how to
hold every corps in the army, or whether the army has more than those two." The answer holds the key's
musts (both roads); the hedge is about how many corps the army has — the chip's "· 2" read as no word at
all (lever D7 below). It is counted right, and the lever goes to reading 2.

**What the readers said confused them, and what was done** (each built after this reading; reading 2's
fresh readers read the build with them):

| Said by | What | Ruling |
|---|---|---|
| all three | Lannes can go but stands unticked, and is not under "Will not go" — why? | **Lever D1, built:** a man who could go and is not ticked because the actions would run out says so under the cost — "Lannes is not ticked — not enough actions are left for him. Untick another corps to send him instead." |
| all three | "march together · up to 4 of 4 actions in hand" (the group's card) could not be read. | **Lever D2, built:** "sending them costs up to 4 actions · you have 4". |
| all three | "Hold…", "Fortify…", "Drill…" — what does the "…" ask next? Does Hold go to the whole army? | **Lever D3, built:** the card's line says it before the press — "Hold…, Fortify… or Drill… shows each corps' order and price first — nothing is spent until you Give". |
| all three | Does Take back give the actions back? | **Lever D4, built:** "Take back (Ctrl+Z) undoes them all and gives their actions back." |
| readers 1, 3 | "4 actions … 2 corps go" — is that two times two? | **Lever D5, built:** the cost says how it adds up — "Cost: 4 actions (2 + 2) of the 4 in hand". |
| readers 1, 2, 3 | "8 corps with no orders can march on Vienna" over "7 corps of yours have no orders and Mack…" — which is it? | **Lever D6, built:** where every corps with no orders can go, the goal's row counts nobody — "Your corps with no orders can march on Vienna, your war goal — see the list." (the list counts them; the hover names them). Where only some can, it counts them ("7 of your corps …"). |
| reader 3 | "I did not see a chip beside the marshals"; "Army of Italy · 2" read as a heading. | **Lever D7, built:** "Army of Italy · 2 corps". |
| readers 2, 3 | "He will drop this order for any battle within two provinces in a war of ours" — what happens, and why only for some? | Kept: the order's own rider (`strategic.py`, an aggressive marshal's), printed on the single order card the same way since S14h and pinned there; the list prints each order's own notes. Its words are carried to the deploy session's reading as a note, as the desk's reading carried the words of surfaces it did not make. |
| all three | The map's "?" boxes and numbers, "45 sail · BLOCKADED", "Threat", the war card's slider, the white dots on the portraits. | Not this row's surfaces; each has its hover and the map's key. Notes for the deploy session's reading. |
| readers 1, 3 | How THE PEACE's 45 provinces relate to the war goal. | Help's "War goal" says what a goal is and is not; a province taken counts toward the 45 only once kept 12 turns (THE PEACE's own line). Kept. |
| reader 1 | "Take back" greyed in L, lit in A and G. | An artefact of the frames (orders were given between them). |

## Reading 2 — the questions and the key (written before its frames were shot)

The same frames, shot again from the build with levers D1–D7 (`reading2/`), the same seven questions and
their key, and three more, one each for the levers readers could check from a frame:

| # | Frame | Question | A right answer must say |
|---|---|---|---|
| 8 | L | Why is Lannes not ticked, and how could you send him? | Not enough actions are left for him (Ney and Davout take the 4); untick another corps to send him instead. |
| 9 | A | What happens when you press "Hold…"? | It shows a list of each corps' order and its price first; nothing is spent until you press Give. |
| 10 | G | Which of your corps can march on Vienna, and how would you see them listed? | Your corps with no orders — all of them; press that row on the card ("see the list"). |

The bar is the same: every reader, every scored question (1–10), right by the key.

## Reading 2 — `reading2/` — NOT MET (28 of 30)

Answers as returned: `reading2/answers.json`. Questions 1–9: every reader right by the key. Lever D1 (why
Lannes is not ticked), D4 (Take back gives the actions back), D5 (2 + 2) and D3 (what "Hold…" opens) were
each read by all three.

**The misses — question 10 ("how would you see them listed?"), readers 2 and 3:** both took "see the list"
on the goal's row for the marshal roster on the left — "I think that means the roster of marshals on the
left" (reader 2); "The list is the corps roster at the top left" (reader 3). Reader 1 answered it ("pressing
that item would open it"). The row did not say what pressing it does. **Lever E1** (below).

**Recorded with its fault, as given:** reader 1, question 6 — "Press the button, then click a province to
send them there" (the hint's first clause, "Click a province to send them there", read as Hold's second
step). The answer holds the key's musts (both roads); the fault is the hint's — **lever E5**.

**What the readers said confused them, and what was done** (built after this reading; reading 3's fresh
readers read the build with them):

| Said by | What | Ruling |
|---|---|---|
| readers 2, 3 (the misses) | "see the list" — which list? | **Lever E1, built:** the row says what pressing it does — "Your corps with no orders can march on Vienna, your war goal — press to list them." (the row's 90-character cap took the longer "press for the list of their orders" first written here) |
| all three | "ORDERS FOR 4 CORPS" while two go. | **Lever E2, built:** the title counts the ticked — "ORDERS FOR 2 OF 4 CORPS" (all ticked: "ORDERS FOR 4 CORPS"), following every tick. |
| readers 1, 2 | The typed line stands in the log after the list was let go — "whether the earlier order was given or only drafted was unclear". | **Lever E3, built:** a list let go says so in the log — "Not given: <the line> — nothing was spent." |
| reader 2 (and readers 1, 3 of reading 1) | "to hold the homeland — goal: Vienna" mixes a defensive aim with a target. | **Lever E4, built:** the war's purpose and the player's own aim are told apart — "… to hold the homeland — your war goal: Vienna." (the war's window: "Your war goal: Vienna — the map rings it in gold."). |
| reader 1 | "Press Hold…, then click a province" — the hint's two clauses read as one. | **Lever E5, built:** the hint gives each its own sentence — "Click a province to send them there. Hold…, Fortify… or Drill… first shows each corps' order and price — nothing is spent until you Give. Ctrl-click a marshal to add or drop him; Esc unselects them." |
| reader 2 | Which rows of the roster belong to the army? | Kept: the map rings each of its corps and the card names them ("The Army of Italy — Lannes, Murat"); the roster marks one man, the selection, as it always has. |
| all three | "He will drop this order…" under Ney and Lannes; the white dots; "?" boxes; "BLOCKADED". | As in reading 1: the order's own rider and other surfaces' words — notes for the deploy session's reading. |
| reader 3 | The gold ring stands in Austria, not on a city's name. | Kept: the ring marks the province of Vienna, and its plate names it. |

## Reading 3 — the questions and the key (written before its frames were shot)

The frames shot again from the build with levers E1–E5 (`reading3/`), with one more: **C** — the list of
frame L let go with Esc. Three fresh readers; the question reading 2 missed, the one E5 touches, and one for
each other lever:

| # | Frame | Question | A right answer must say |
|---|---|---|---|
| 6 | A | How would you order every corps of the Army of Italy to hold? | As before: press "Hold…" on its card (it shows the list first, then Give) — or type "Army of Italy, hold". One is enough. |
| 10 | G | Which of your corps can march on Vienna, and how would you see them listed? | Your corps with no orders — all of them; press that row on the card. |
| 11 | L | How many corps get an order if you press "Give the order"? | Two — Ney and Davout (of the four named). |
| 12 | C | The player pressed Esc on the list. Was any order given? | No — "Not given … nothing was spent"; the typed line is back on the command line. |
| 13 | G | What is this war being fought for, and what is your own goal in it? | The war is fought to hold the homeland; your own goal in it is Vienna. |

The bar: every reader, every question, right by the key.

## Reading 3 — `reading3/` — MET (15 of 15), one answer with a fault

Answers as returned: `reading3/answers.json`. Question 10 (reading 2's miss) — all three: "I would press that
line to see them listed." Question 11 — all three: two, from the title "Orders for 2 of 4 corps". Question 12
— all three: no, from "Not given … nothing was spent" and "Actions 4/4". Question 13 — all three: to hold
the homeland, and Vienna their own goal. Question 6 — all three named "Hold…" (two also the typed line).

**Recorded with its fault, as given:** reader 2, question 6 — "Press it, then click a province. It first
shows each corps' order and price, and nothing is spent until I press Give." The same fault as reading 2's
reader 1: the hint's first sentence ("Click a province to send them there.") read as Hold's second step.
Twice is a pattern, so **lever F1** and a fourth reading.

**What the readers said confused them, and what was done:**

| Said by | What | Ruling |
|---|---|---|
| reader 2 (and reading 2's reader 1) | "Press Hold…, then click a province." | **Lever F1, built:** the hint leads with what the buttons do and says the click is the march — "Hold…, Fortify… or Drill… first shows each corps' order and price — nothing is spent until you Give. To march them instead, click a province. …" |
| readers 1, 2, 3 | After Esc the typed line stands in the box — "whether that text will be sent again". | **Lever F2, built:** "Not given: … — nothing was spent. Your line is back below: change it, or press Enter to see the list again." |
| reader 2 | "not enough actions are left" beside "4 of the 4 in hand" — "why the actions run out when the 4 are still there". | **Lever F3, built:** who takes them — "Lannes is not ticked: he needs 2 actions, and the ticked corps leave none. Untick one of them to send him instead." |
| reader 1 | The reply named "the war with Austria"; the war panel says "War with the Third Coalition". | **Lever F4, built:** the reply names the war as the panel does — "The goal of the war with the Third Coalition is now Vienna." |
| readers 1, 2, 3 | Whether Hold costs actions before the list; "sending them costs up to 4 actions" for a hold. | Kept: the list prices every order before anything is spent — the line under the buttons says so. |
| readers 1, 3 | Whether "Army of Italy · 2 corps" is a button or a label; whether its corps can still be ordered one by one. | Kept: it is a chip among the roster's chips (its hover: "Press to select its corps …"), and a marshal in an army takes his own orders as before — Help's "Named army" says so. |
| all three | "He will drop this order…", the war card's slider, "BLOCKADED", "Threat", the map's numbers; "7 corps of yours have no orders" (the desk's own row). | As in readings 1 and 2: other surfaces' words — notes for the deploy session's reading. |

## Reading 4 — the questions and the key (written before its frames were shot)

The frames shot again from the build with levers F1–F4 (`reading4/`: L, C, A, and G with the reply in the
log). Three fresh readers:

| # | Frame | Question | A right answer must say |
|---|---|---|---|
| 6′ | A | How would you order the Army of Italy (Lannes and Murat) to hold? | Press "Hold…" on its card — it shows the list first, then Give (or type "Army of Italy, hold"). It must NOT add a province click to the hold. |
| 8′ | L | Why is Lannes not ticked, and how could you send him? | He needs 2 actions and the ticked corps (Ney and Davout) leave none; untick one of them to send him. |
| 12′ | C | The player pressed Esc on the box of Frame L. Was any order given — and what is the text left in the box at the bottom left? | No order was given; the text is the player's own line put back — it can be changed, or Enter shows the list again (it is not sent by itself). |
| 14 | G | Which war did the player set a goal for, and what is the goal? | The war with the Third Coalition; Vienna. |

The bar: every reader, every question, right by the key.

## Reading 4 — `reading4/` — MET (12 of 12), no fault

Answers as returned: `reading4/answers.json`. Question 6′ — all three: press "Hold…" (two also the typed
line), and none added a province click. Question 8′ — all three: he needs 2 actions and Ney and Davout take
all 4; untick one of them. Question 12′ — all three: no order was given, and the line in the box is the
player's own, put back to change or to see the list again. Question 14 — all three: the war with the Third
Coalition, and Vienna.

**What the readers said confused them** — ruled, nothing built after this reading:

| Said by | What | Ruling |
|---|---|---|
| all three | "Orders for 2 of 4 corps" beside a line that names four — "it took me a moment". | Kept: the title counts the ticked of the corps named, and the two others each say why they are out — every reader then answered question 11 (reading 3) and 8′ right. |
| all three | The command line shows only the tail of the line put back ("…nes, march to Lorraine"). | Kept: the caret stands at the line's end, where typing goes on; the whole line is in the log twice ("►" and "Not given"). |
| readers 1, 2 | What Hold costs before the list. | Kept: the list prices every order before anything is spent. |
| reader 2 | Is "hold the homeland" one aim with "your war goal"? | Kept: "your war goal" (lever E4) answered question 13 for all three in reading 3; Help's "War goal" says what a goal is and is not. |
| all three | "He will drop this order…", the war card, the portraits' dots, "BLOCKADED". | As before: other surfaces' words — notes for the deploy session's reading. |

## The result, in one line

Four readings, twelve fresh readers, **76 of 78 answers right by the key** (21 + 28 + 15 + 12) — the two
misses (reading 2, question 10: "see the list" read as the marshal roster) were built out (E1) and the question
was answered by all three of reading 3. Two answers carried one fault between them ("press Hold…, then click a province"),
built out by F1 and absent from reading 4. Every lever (D1–D7, E1–E5, F1–F4) is in the shipped build and was
pressed in the real client at the first player's setup; `tests/test_dd_b_the_client_hands.py::TestRowICDirectives`
drives the same presses.

## Pressed in the real client

Three runs at the first player's setup before the readings (`tools/dd_b_play.py`, Interface Scale 1.8 on 5120 x
1377) found and fixed, besides the levers above: the list card for a group sent by a click GREW under the eye
as its rows arrived (a "reading" card first) — it now opens once, fully formed, and only a list slower than
0.35 s stands on "reading" first; an eight-corps list ran 26 px past the bottom of the screen — its room is now
reckoned from under the top bar; its head line cut "go to Vienna" off behind eight names — the order now leads
a line too long to fit; "AUSTRIA" vanished under Vienna's gold plate — a name the plate displaces steps below
it; a click group's head said "march to" over rows of one-action moves — it says "go to"; the army's own Hold
list was headed by the men's names — it is headed by the army's; the instrument's reader of the list card read
nothing (the card is a CanvasLayer) — fixed; and a list stopped by a marshal's question lost, in the client, the
lines of the men who went and of those who wait — the server now says them (`group.said`) and the client prints
them before his window.
