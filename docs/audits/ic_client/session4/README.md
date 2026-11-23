# Row IC, Session 4 — the voice: the reading, the pressing, the review (November 22, 2026)

## The blind reading — the bar MISSED on "none guessing"

**The plan's question 1** — "Here are two lines with no names: which marshal said which, and what told you?" — and, besides, a harder test: six unnamed lines of ONE kind, one from each of the six men who judge for themselves, each to be matched to its speaker. The reader is told only who each man is, in one line. **The bar** (written first): every reader right on every question, none guessing. **The key** was written before any reader saw a line, by a fixed seeded procedure (pairs: two of the six men and one kind every one of them has a set for, one line from each man's own set; each man in four pairs) — `_blind_key.json`, `_blind_key_round2.json` … `_blind_key_round7.json`; one draw was set aside UNREAD (`_blind_key_round4_draw1_discarded_unread.json`) when a systematic pass over the lines came first. Three fresh readers (Sonnet) a test a round, a new panel and a new draw after every change; the readers saw no file.

| Round | Test | Right | Marked "partly guessed" | What was done after it |
|---|---|---|---|---|
| 1 | six-way: waited · stayed · idle | 45 of 54 | many | nine "stayed" and three "idle" lines rewritten with the man's mark |
| 2 | six-way (two sets rewritten, one new) | 52 of 54 | few | five lines sharpened |
| 3 | six-way: three "stayed" sets | 42 of 54 | many | seven lines rewritten; then a SYSTEMATIC pass over every line of the six (148 rewrites, each checked by an adversarial reader and by hand) |
| 4 | the plan's question, 12 pairs · six-way, 5 kinds | 36 of 36 · 90 of 90 | 3–4 pairs a reader | nine lines sharpened |
| 5 | (new draw) | 35 of 36 · 90 of 90 | 1–2 pairs a reader | eight lines sharpened |
| 6 | (new draw) | 36 of 36 · 86 of 90 | 3 pairs a reader | a second, STRICTER systematic pass (71 rewrites; eight corrected by hand for their moment's truth) |
| 7 | (new draw) — the last | 36 of 36 · 90 of 90 | 2–3 pairs a reader | none: the reading stops here |

**What the rounds say.** The six voices are told apart: in rounds 4–7 the readers were right on 143 of 144 pairs and 356 of 360 six-way lines. What none of the rounds met is "none guessing": each reader still marks two to four pairs as partly guessed, and almost always the same two pairings — the two bold men (Ney and Lannes: "both are bold, so this is less clear") or the two who hold (Masséna and Davout). **Open: `BUG_FIXES.md` IC4-R1** — Session 4b reads again on a fresh draw (and the hold-proposal lines added after round 7, not read), or the user rules the clause.

The enemy's three questions of the plan (what you know of the enemy's plan; what "to the letter" tells you; what Mack will do) were NOT asked: they read the war plans, which ship off.

## Pressed in the real client first

At Interface Scale 1.8 on 5120 × 1377 (a logical 2844 × 765) and at 2.0 on 1600 × 900 (800 × 450), by `tools/dd_b_play.py` — "Ney, take Swabia on your own" typed and sent; exact orders typed for Soult and sent; Soult asked to act on his own.

| # | Seen | Done |
|---|---|---|
| P1 | His line stood TWICE in the reply — inside the staff's sentence and again beside his portrait | The staff's sentence no longer carries it (`own_order.give`); IC4-C1 |
| P2 | A refused order was answered by the staff alone | The refused road prints `voices`; the refusal carries his line; IC4-C2 |
| P3 | The read-back named him ("Ney: …") with no portrait | The small inline portrait stands there too |
| P4 | A new campaign started the set at another line than the test expected | Not a defect: a seed starts each set at its own place; the driven pin reads the whole pool |
| P5 | The audience window, at your setup and at the compact view: his line now heads his proposal by name; given, he says that same line once | Built after the census (IC4-V7) |
| P6 | An army's task given: the commander's answer, the passed-over senior's and a follower's, each with portrait and name | Built after the census (IC4-V8) |
| P7 | A battle (Lannes on Mack): Berthier's report carries "Lannes: “…”" in the helper's form | The terminal had scrolled past the line in the frame; the text record shows it, and the same helper drew portraits in P6 |

Pinned: `tests/test_dd_b_the_client_hands.py::TestRowIC13TheVoice`, `::TestRowIC13TheVoiceAtTheCompactView`, `::TestRowIC13TheAudienceSpeaksAtTheCompactView`, `::TestRowIC13AnArmysTaskSpeaks` (green). **Not pressed:** a desk row's hover; the enemy phase's report (its pin reads the source).

## The review — one, on a frozen copy, three readers by lane

| Lane | Upheld and fixed | Read and accepted |
|---|---|---|
| The enemy's night and the saves | the written plan sets rode every save (IC4-V6 — fixed; fixing it found that a board rebuilt before any court drew its plan lost the plans) | captured orders reach no screen (IC-15's, IC4-D2) |
| The voice | the read-back's line for exact orders was not the line said (IC4-V1); the trial's line on two channels (IC4-V4); a docstring claimed a petition is recorded (corrected) | the `proposal` line is his offer, the give answers with his `ack` |
| **The census** (after the review: four readers, every line said against the screens it reaches) | lines recorded and never shown — the task to prove himself, every line given through an order list, the answer after an objection, the completion on arrival; a task done drawn twice; no speaker on the battle lines; a take with no battle said "struck"; a refused reply on one renderer (IC4-V7 … V15) | the army's list leaves the commander's answer off (Session 3b's pressing) |
| **The independent check** (everything changed after the review; four lanes, three skeptics per finding) | his proposal line ignored the task proposed; "stayed" lines claimed a cause; "struck" lines on nights with no fight; a mod keeping the 1805 name lost its plan sets (IC4-V17 … V19, V6) | four findings held by fewer than two skeptics, read and left (`BUG_FIXES.md`) |
| The client | the lesson's two cards held an idle player off the last card (IC4-V2); a quote lost at a line's end (IC4-V3) | — |

The reviewers found the shipped tree unchanged in play with the plans' seam down (every plan path returns early or empty; the mood draw, the hunt's credit and the favour's set are inert).

## The measure

`tools/_ic4_measure.py`; the tables are `SYSTEMS_REFERENCE.md` §235.6 and `tools/_ic4_{band,gate,hill,chain_d}_2026_11_22.json`, `_ic4_series_arms_final.json`.
