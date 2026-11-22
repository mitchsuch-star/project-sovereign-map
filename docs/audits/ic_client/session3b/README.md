# Row IC, Session 3b — an army's task: pressed in the real game, and the blind reading

Frames from the real client at the first player's setup (Interface Scale 1.8 on
5120 × 1377 — a logical screen of 2844 × 765), taken with `tools/dd_b_play.py`.

## The questions and the key

The three questions are the plan's own (`docs/NEXT_SESSION_PROMPT.md`, "Row IC, Session 3b —
the plan, decided", written November 21, 2026 before anything was built). The key below was
written before any reader was shown a frame.

**The bar:** three fresh readers (Sonnet, none of whom has read the design or the code), every
reader right on every question — 9 of 9 — and none of them guessing. A reader who is right but
unsure counts against the purpose: what he says confused him is built out and the changed
screen is read again by a NEW panel.

| # | Frames | Question | The key (what a right answer says) |
|---|---|---|---|
| Q1 | the typed line's reading; the list | "You type 'Army of Italy, take Swabia'. Who goes on his own, and what do the others do?" | **Ney** is set on his own with the task (he commands the army); **Davout and Soult follow him** — they move with him each night and may join his battles. The two followers are NOT on their own. |
| Q2 | the list | "What does it cost?" | **4 actions in all** — 2 for Ney and 1 each for Davout and Soult — of the 4 you have; nothing is spent until you press Give. |
| Q3 | the list of a changed war goal | "You change the war goal. What happens to Ney?" | If his row stays ticked he is **turned to the new goal** (Tyrol) for **1 action**; if you untick him he **keeps his old target** (Bohemia) and no longer serves the war goal. Naming the goal itself is free. |

## Pressed in the real client first — what it found

Every one fixed before any reader saw a frame:

| # | What the pressing showed | The fix |
|---|---|---|
| P1 | The list's commander row carried his whole read-back (seven notes): at the first player's screen height **both followers stood below the fold** — the list answered "who follows?" only if you scrolled | The commander's row says three things (who commands and why, with the place he takes; his first night; what warns); the list of a task takes a wider card (780 px where the screen has it); the help line is one sentence shorter. All three rows, the cost and the buttons now stand on one screen (`TestRowIC12AnArmysTask`) |
| P2 | The read-back said "Murat outranks **him** and has no order" before it had said who "him" was | "Murat outranks **Ney** and has no order — he will resent it" |
| P3 | The headline read "The Army of Italy: on its own: take Swabia" (two colons) | "The Army of Italy: take Swabia, on its own" |
| P4 | **The commander's card ran 11 px, then 27 px, past the screen's foot** — his last button was cut off — once the card said which army he commands | The army and the war goal share ONE line ("Commands the Army of Italy — 2 men follow him."), and the sentence that repeated his odds is left out where his night's own line already says them. His card stands whole (`_ic3b_card_fits`) |
| P5 | With the count full the commander's row said "the count is full — on their own: 1 of the 1 …" under a note that had just said the same | "would command — but no place is free for another man on his own" |
| P6 | Pressing the list's offer ("Stand down Massena (free) and list again") closed the card and opened it again **110 px to the right** — the first play's "windows that bob" | The card stays where it stands on a "reading" face while the stand-down is sent; the list drawn again opens in its place (the driven walk pins x and top) |
| P7 | The morning's status said "Supporting Ney" for a man who follows his army's commander | "Follows Ney — the Army of Italy's task (take Swabia)."; the commander's line adds "He commands the Army of Italy." |
| P8 | **Take back refused to undo an army's task** ("More than the order itself followed from it; it stands") whenever a senior marshal resented being passed over — which is nearly always at the start (Murat). The same hole stood for ONE man set on his own since Session 3 | The court's note of the slight is the order's own consequence and is un-written with it (ledger row IC3B-1) |
| P9 | A changed war goal's row carried the man's whole read-back too | The same three things as a commander's row |

## Rounds

Three rounds, nine readers, a new panel each round (Sonnet; none had read the design or the
code; each opened only the three crops named). **The bar was met in every round — 9 of 9 right,
nobody guessing an answer** — and the rounds went on because round 1's readers were right but
only "fairly sure" on two of the three questions, which the bar's own last sentence counts
against the purpose.

What each panel was told, said plainly because it differed: round 1 was told who the player is
and that a turn has a few "actions", and NOT who is in the army; rounds 2 and 3 were told the one
thing the player himself did before these screens (he formed the Army of Italy from Ney, Davout
and Soult, and has other marshals outside it) and nothing about actions.

| Round | Frames | Right | How sure (of 9 answers) | What they said was unclear → what was built |
|---|---|---|---|---|
| 1 | `A_…`, `B_…`, `F_…` | **9 of 9** | sure 3 · fairly sure 6 · guessing 0 (Q1 and Q3 "fairly sure" for all three) | See the levers below — six, all built |
| 2 | `A2_…`, `B2_…`, `F2_…` | **9 of 9** | sure 6 · fairly sure 3 · guessing 0 (one "fairly sure" each, on three different questions) | Two more: the odds sentence, and "keeps to Bohemia" |
| 3 | `A3_…`, `B3_…`, `F3_…` | **9 of 9** | **sure 9** · fairly sure 0 · guessing 0 | A fourth question was added on the odds sentence (below): 3 of 3 right, each "fairly sure" |

### Round 1's levers (what three readers hesitated on, and what the screen says now)

| # | What the readers said | Built |
|---|---|---|
| R1 | "I could not tell what Lannes and Murat do" — the commander's first night names the men **beside his battle**, and two of them are not of the army; the warning named Murat too ("is Murat in the army?") | The list and the read-back say so where it is so: "…with Davout, Lannes and Murat beside him (they may join, **of this army or not**)", and "Murat **(not of this army)** outranks Ney and has no order" (`army_task._beside_for_the_list`, `_slight_for_the_list`) |
| R2 | "Not counted among those on their own — counted against what?" | "He takes none of your places for men on their own." — the same thing the commander's row says he takes (list, read-back, the follower's card) |
| R3 | "the commander's row stays" was read as "Ney cannot be unticked" (he can — and then nobody goes) | The help says what happens: "Untick a follower to leave him out; untick Ney and nobody goes." |
| R4 | "Soult outranks him but follows orders to the letter — why can't Soult command?" | "(Soult outranks him but takes only exact orders.)" |
| R5 | "…May become a great battle — **he** bars the road to Tyrol": who? and does Ney go to Tyrol or attack at Swabia? | The line names him: "— **Mack** bars the road to Tyrol" (`own_order`, a sentence of Session 3's) |
| R6 | "naming it is free" against "turning a man costs 1 action" had to be read twice | Two sentences: "…naming it is free. What costs is turning the 1 man who serves it: 1 action." |

**Pressed again before round 2** (the levers had added two lines): the list stood 8 px from the
foot of the first player's screen. The words were cut back until it stood shorter than it had
before the levers — 620 px, where round 1's stood 645: the warning on one line ("…he will resent
Ney for it"), "He takes your one place for a man on his own.", and a help line of two lines.

### Round 2's two

| # | What the readers said | Built |
|---|---|---|
| R7 | "he goes in when they are 5 to 10 or better" — one reader took it for the ENEMY at half his strength (the reverse); all six readers of rounds 1 and 2 called it hard | Both figures are said the same way round: "the odds are our 19.2 to their 10, and he goes in when they are **our 5 to their 10** or better" (`own_order.attack_line` — Session 3's sentence; its sibling `needed_words` already said "our 5 to their 10") |
| R8 | "he keeps to Bohemia" — keeps attacking it, or his order stands? | The reply's own words: "Untick him and he keeps to his task (take Bohemia) — he then serves the war goal no longer." |

### Round 3

Every answer right and every answer "sure". The added question — "at what odds does Ney attack,
and when does he hold back?" — was answered right by all three ("at least 5 of ours to 10 of
theirs; below that he holds back; 19.2 to 10 is well above it"), each "fairly sure": what they
still guessed at is what the figures COUNT (strength), which the sentence does not say and the
battle's own screens do.

### What every panel still called unclear, and where it stands

Said by most readers in every round, none of it in the way of the three answers, and none of it
changed here — each is another surface's own words, read and kept by its own session:

- the bracketed offers in the typed line's reading ("[+ boldly …] [Davout commands instead]") —
  buttons in the client; a still picture cannot show that they press (Session 2's read-back);
- "May become a great battle" (row BA's term; the Help has it);
- "about 95 times in 100" for a follower — read by all as his chance to reach the battle, which
  is what it is; why it is not 100 is the arrival roll's own rule (§9.1);
- how many places for men on their own there are (the desk's ON THEIR OWN line says "1 of the 1
  you may have"; the readers did not see the desk).

## The compact view

Interface Scale 2.0 on 1600 × 900 (a logical screen of 800 × 450), the same walk
(`frames/H_compact_list.jpg`): the card stands whole on the screen — its title, the headline,
the cost line, the help and both buttons in view — and its rows scroll inside it (the commander
first), which is the list card's standing rule at that size. Nothing is cut; nothing is off the
screen.

## The review, and the measure

The one review before the commit (three readers by lane on a frozen copy outside the repository) and what the suite's own instruments found are in `BUG_FIXES.md` §"Row IC, Session 3b" (IC3B-V1 … V10, IC3B-X1, and the seven read and not upheld). One of them was caught only here, in the real client: the review's own fix for Esc-while-the-offer-is-sent asked "is a window open?" — and the list card is itself a window, so the list never came back; the driven walk failed, and the question now leaves the card out (`dialog_manager.is_any_modal_open_but`).

The measure (`tools/_ic3b_measure.py`, rules written before any data, taken again after the review's fixes): **All four rules met.** R-TRUE: "Tonight" equalled every act — 0 differences in 1,390 nights read (30 seeds × 20 turns, the commander's and each follower's). R-TOGETHER: no follower opened a battle of his own; on all 1,064 nights the army shared, a follower's line named his commander (the bar: half). R-INERT: with no army's task the France band reads 26 / 27 / 28, the standing reading. R-BAND: with an army's task 28 / 25 / 28 (the bar 23–28). Reported: 533 nights with a task; the commander struck, attacked or took on 63, looked on 302; followers stayed with him on 618 nights, joined his battle on 107, marched after him on 49, stood by on 14, halted on 0.
