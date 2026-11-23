# Row IC, Session 4b — the new screens' blind reading, November 23, 2026

The plan approved in Plan Mode (Part 5) asks for a blind reading of the new screens: three
fresh readers, the key written first, three questions. This file was written — questions, key
and bar — BEFORE any frame was taken or any reader was shown anything.

## The questions and the key

The questions are the plan's own, with one change said plainly: the plan wrote "What does 'Act
on his own' do?", but no screen carries those words — the card's button says **"Set him on his
own · 2 actions"** (the typed words are "act on your own"). A reader asked about words he cannot
find would be testing my question, not the screen, so Q2 uses the button's own words.

| # | Frames | Question | The key (what a right answer says) |
|---|---|---|---|
| Q1 | the reply when he is set on his own; the morning report; his card | "When does a marshal on his own move, and what did Ney do this turn?" | (a) **At the start of each turn** — the turn opens with his move, after the enemy has moved and before you give your orders; the morning report says what he did. Wrong: "when I end my turn, before the enemy", "at night", or "whenever I order him". (b) **What Ney did**: what his line in the morning report and his card's "This turn" say — copied into the table below from the run's own state as soon as the frame is taken, before any reader sees it. |
| Q2 | his card with the button and its hover tip; the reply | "What does pressing 'Set him on his own' do?" | (i) He is set to act **on his own judgement with no task** — each turn he makes war as he sees fit (strikes an enemy he can beat, takes ground the enemy holds, heads for your war goal); AND (ii) it **costs 2 actions**. Reported, not required: it takes one of your places for men on their own; a task given later guides him; his first move is at the start of next turn. |
| Q3 | the Generals page, Davout's card, its nature with its hover line | "What does Careful tell you about Davout?" | He **attacks only when the odds are good** (not at worse odds) — reported besides: he holds good ground. |

**A second change, made while taking the frames and before any reader saw anything:** the plan's
Q3 named Masséna, but the game makes Masséna **Bold** (`europe_1805.json`: "aggressive"; his
Generals card says so). The plan's question rested on my wrong premise. Davout is the careful
marshal on the board, so Q3 asks about him; the key is unchanged.

**Ney's line, copied from the run before any reader saw a frame** (the run's state 0010, turn 2,
"--- Your marshals on their own, as this turn opened ---"): *"Ney struck Mack at Swabia, with
Davout, Lannes and Napoleon beside him — the odds were our 16.5 to their 10; a threat to
Napoleon."* Q1 (b) is right when it says **Ney attacked Mack at Swabia** (the friends beside him
and the odds are reported, not required).

## The bar

Three fresh readers (Sonnet; none has read the design or the code), every reader right on every
question — 9 of 9 — and none guessing. A reader who is right but only "fairly sure" counts
against the purpose: what he says confused him is built out and the changed screen is read again
by a NEW panel. At most three rounds; a miss after the third is reported with the lines that
drew it.

What each reader is told: the player is Napoleon, playing France; marshals are his generals; a
turn has a few "actions"; the crops are from the game's screens. Nothing about the design, the
code, or what the answers should be.

## Pressed in the real client first — what it found

At the first player's setup (Interface Scale 1.8 on 5120 × 1377), with `tools/dd_b_play.py`,
before any reader saw a frame. Each was fixed and the frames taken again:

| # | What the pressing showed | The fix |
|---|---|---|
| P1 | Ney's card said "(makes his first move at the start of next turn)" and, on the next line, "He makes his first move at the start of next turn." | The state's words are left out when the line below says them (`selection_card.gd`); pinned in `TestRowIC4bHisOwnJudgement` |
| P2 | A man set on his own with NO task read "Your task guides him" | "No task: each turn he weighs the chances around him and makes war as he sees fit; a task you give later guides him." |
| P3 | Ney's answer as the order was given — "I'm moving now" — stood under "He makes his first move at the start of next turn"; four more lines said when an order is given promised "now" or "right away" | The six lines reworded (`own_voice.py`); a rule and a pin: a line said when an order is given never promises he acts at once (`test_a_line_said_when_an_order_is_given_never_promises_he_acts_at_once`) |
| P4 | The battle's lines still said "(Aggressive: +15% attack)" and "Personality (aggressive)" — the natures' sibling the session's sweep missed | Fixed in the same slice (`BUG_FIXES.md` §"Row IC, Session 4b") |

## Round 1

Three fresh readers — Sonnet, as **Explore** agents (that agent type loads no CLAUDE.md, whose
file table still carried a stale line about when a man on his own moves); each opened only the
six frames A–F (`frames/`). Their answers are kept verbatim (`_round1_reader1.txt` …
`_round1_reader3.txt`).

| Reader | Q1 (when · what Ney did) | Q2 (what the button does · its price) | Q3 (Careful) |
|---|---|---|---|
| 1 | right · right — SURE | right · right — SURE | right — SURE |
| 2 | right · right — SURE | right · right — SURE | right — SURE |
| 3 | right · right — SURE | right · right — SURE | right — SURE |

**The bar is met in round 1: 9 of 9 right, every answer SURE, nobody guessing.** Two notes, both
from answers marked SURE, recorded and not built: reader 1 saw the friend Ney may march to help
change from Napoleon (frame B) to Bernadotte (frame E) — true, it is the friend beside him that
turn, and the board had changed; reader 2 found the price "slightly muddied" by the 2 actions, the
place for men on their own and the free stand-down, and was sure of all three.
