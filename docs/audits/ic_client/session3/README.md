# Row IC, Session 3 — "on his own": the blind reading (R-READ)

The bar and the key were written BEFORE any frame was taken (November 21, 2026).
Frames from the real client at the first player's setup (Interface Scale 1.8 on
5120 × 1377), taken with `tools/dd_b_play.py`. Three fresh readers a round (Sonnet,
none of whom had read the design), every reader right on every question; a changed
screen is read again by a new panel.

## The questions and the key

| # | Frame | Question | The key (what a right answer says) |
|---|---|---|---|
| Q1 | his card | "What will Masséna do tonight?" | What the card's "Tonight" line says (the act and the place), not a guess |
| Q2 | his card | "What might he do that you did not ask?" | Strike an enemy beside his area and come back, or march to help a friend attacked next to him (by the usual roll — "may") |
| Q3 | the desk | "How many more men can you set on their own?" | None — "On their own: 1 of 1" |
| Q4 | Lannes's card | "Ney is attacked beside Lannes, who is on his own. What does Lannes do?" | He may march to help Ney — the usual roll; not certain |
| Q5 | two read-backs | "Why does Davout do something different tonight from Ney?" | Their natures: Davout is careful (he holds and digs in), Ney is bold (he strikes) — each chooses his own act |
| Q6 | the Generals page | "Is Ney's corps broken?" | No — "Broken" on that tile is his TRUST in you, not his corps (IC3-H3: if a reader says yes, the tile becomes "Trust broken") |

Q4 was asked of the friend Lannes's card names ("Napoleon's corps is attacked next to Lannes") — the
frame's own friend; the key is the same.

## Rounds

**Round 1 (frames `frames/`): 18 of 18 right — and NOT good enough.** Q1–Q5 all right, "fairly sure".
Q6 ("Is Ney's corps broken?"): all three answered no, two of them guessing, and all three listed the red
"Broken 18" tile as misleading (a handshake glyph, no word saying it was trust). No reader answered "yes",
so IC3-H3's written rule would have kept the tile; it was changed anyway on the readers' unclear-list —
the lesson of Session 2b's first round (right answers in doubt fail the reading's purpose). The levers
built from what the three readers said confused them:

| Lever | What changed |
|---|---|
| L1 (IC3-H3) | the Generals page's trust tile says "Trust: broken" (was "Broken") |
| L2 | "On their own: 1 of 1" → "1 of the 1 you may have" (a cap, not a count) |
| L3 | the odds said as a threshold against the forecast: "the odds are our 15.3 to their 10, and he goes in when they are 8 to 10 or better"; the card: "He attacks only when the odds are our 8 to their 10 or better (men of ours to theirs, as the battle forecast reckons them)" |
| L4 | the given night: "Tonight: … makes ready — a task starts the night after it is given" and a line of its own, "Tomorrow night, as things stand: …" (was one sentence) |
| L5 | the strike beside his area: "Tyrol is next to the ground he holds, so he strikes there once and comes back after" |
| L6 | the slight's cost said: "he resents it (his regard for Davout drops)" |
| L7 | the chips say what they do: "+ boldly (attacks at worse odds)", "+ carefully (only at better odds)", "+ and Lorraine (a second province to hold)" |
| L8 | "Give him a task…" leaves the card of a man on his own ("Change his task…" is his road) |
| L9 | "Iron Resolve starts to build (each night dug in makes his next attack stronger)"; "(a roll: not certain)" |
| L10 | "An order you give him today is carried out; his task goes on the next night" (was "He still takes the orders you give him today") |

**Round 2 (frames `frames2/`, three NEW readers): 18 of 18 right, "sure" or "fairly sure" on every
answer.** Q6 now read as his trust by all three ("The word 'broken' appears only under Trust … his trust in
me, not his army"). Their remaining notes — the timing words, how the count is raised, whether the chips are
buttons, the actions — gave two last levers: the desk's line says "1 of the 1 you may have" too and its hover
names the two laws that raise it; the read-back's count row says "(laws raise it)". Their still-unclear list
(actions undefined, "Stand here" against "Stay put", the dashed buttons, "titled provinces") is the older
screens' and is the next UX pass's worklist (`docs/STATUS.md`).

**IC3-H3 ruled:** the tile changed to "Trust: broken" (round 1's three readers named it misleading; round 2's
three read it right). `tests/test_ic10_on_his_own.py` holds it.
