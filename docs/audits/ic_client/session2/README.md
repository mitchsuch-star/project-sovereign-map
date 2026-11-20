# Row IC, Session 2 — buttons for orders, the line for tasks, exact orders: the blind reading (November 20, 2026)

**This page was written BEFORE any frame was shot.** The questions, the answer key and the bar stand as they
are below; the result is filled in under "The result" after the readers have answered, and nothing above that
heading is changed once a frame exists.

The frames are the real client at the first player's own setup (Interface Scale 1.8 on a 5120 x 1377 window:
a logical view of 2844 x 765), shot by the instrument (`tools/dd_b_play.py`,
`DD_B_UI_SCALE=1.8 DD_B_WINDOW=5120x1377`) on the opening board of the 1805 campaign.

## The bar

Three fresh readers (Sonnet) who have never seen the game are shown only the frames named for a question and
asked the question. The bar is met only if EVERY reader answers EVERY asked question correctly by the key.
"I cannot tell" on what the key asks is a miss. A miss is reported as a miss.

## The questions (`docs/INDEPENDENT_COMMAND_SPEC.md` §13, R-READ, "Version 6 — the buttons and the line")

| # | Frame | Question | Asked? |
|---|---|---|---|
| 1 | **F1** — Murat selected, the card that opens on a click on Mack | "How would you make Murat chase Mack without typing?" | yes |
| 2 | **F2** — the command window with "Ney, retreat if outnumbered" typed, before Enter | "You typed 'Ney, retreat if outnumbered' — what will happen?" | yes |
| 3 | — | "Why does Davout do something different tonight from Ney?" (Session 2's form in the plan: "Why does Davout propose a different task to prove himself from Ney?") | **NOT ASKED** — "Tonight" comes with Session 3, and the task to prove himself was handed to its own session at this session's checkpoint (the decided fork). There is no screen to show. Reported as not asked, not as met. |
| 4 | **F4** — Soult's exact order on the screen (his standing order's card, opened from the arrow on the map) | "What will Soult do if Mack attacks him?" | yes |

## The answer key (written before the frames)

1. **Without typing: select Murat, click Mack; on the card that opens, press "Chase him".** The card's own
   words name the button and its price ("Chase him · 2 actions"). Right if the reader names the "Chase him"
   button/chip on the card (and that it is pressed, not typed). Naming only "Attack"/"Send" is a miss; "type
   pursue" is a miss.
2. **The condition is not taken: if you press Enter, Ney falls back NOW, whatever the numbers — what is sent
   is "Ney, retreat".** The screen says so in three places: "Not taken: 'if outnumbered' — …", "Enter sends:
   Ney, retreat", and it offers the order that DOES mean it ("Ney, hold. If he is outnumbered, fall back to
   Lorraine.") as a chip that writes that sentence. Right if the reader says the "if outnumbered" part is not
   applied and that Enter sends the plain retreat (Ney falls back at once). Saying "Ney retreats only if he is
   outnumbered" is a miss.
3. *(not asked)*
4. **He digs in (fortifies) where he stands, at Lorraine — by himself, as the turn ends, once.** The card
   reads "Soult holds Lorraine — if he is attacked, dig in; if he is outnumbered, fall back to Champagne (2 of
   2 left)". Right if the reader says he digs in / fortifies. "He falls back to Champagne" is a miss (that is
   the line for being outnumbered); "nothing" is a miss.

## What each reader is also asked (not scored)

"Was anything on these screens confusing, or worded so that you had to guess?" — what they say is recorded
below with a ruling each.

## The result

**The bar is met: three readers, three asked questions, nine answers, nine right by the key.** Question 3 was not
asked (the table above says why) and is not counted as met.

| # | Reader 1 | Reader 2 | Reader 3 |
|---|---|---|---|
| 1 | right — "there is a button ‘Chase him · 2 actions’, so I would click it" | right — "Click the button ‘Chase him · 2 actions’" | right — "a button … labelled ‘Chase him · 2 actions’. Pressing it should send Murat after Mack" |
| 2 | right — "pressing Enter would make Ney retreat at once, with no outnumbered check" | right — "Ney would just retreat straight away and the condition would be dropped. The screen says ‘Enter sends: Ney, retreat’" | right — "If I press Enter it sends ‘Ney, retreat’ … Ney would fall back right away, whether or not he is outnumbered" |
| 4 | right — "If Mack attacks Soult, he will dig in" | right — "if Mack attacks him, he digs in" | right — "if Mack attacks him, Soult digs in at Lorraine" |

**Said plainly: on question 4 every reader was right on what was asked, and every reader then raised the same
doubt** — the card did not say which of Soult's two lines wins when he is attacked AND outnumbered at once. Two of
them found the rule in the log beside the card ("he carries out the first that has come true"); none found it on
the card. It is the one thing the reading found on this session's own screens that a player needs, and it is
built (below).

### The frames the readers saw

`F1_whole_screen.jpg` and `F1_the_card.jpg`; `F2_whole_screen.jpg` and `F2_the_line.jpg`; `F4_whole_screen.jpg`
and `F4_the_card.jpg` — for each question the whole screen and a larger crop of the same screenshot, so the
small text could be read. Each reader was told only where he stood ("you had selected your marshal Murat and
then clicked on the enemy general Mack"; "you typed … and have NOT pressed Enter yet"; "you clicked the small
mark that this order left on the map") and to answer from the screens alone, quoting the words relied on.

### What was changed BEFORE the reading (pressed in the real client first — the session's rule)

None of it changes a question, or the key's test of a right answer. Five things:

1. The "Posture" menu pushed every button of the general's card up as it opened ("Posture" itself moved 84 px
   under the cursor). It now opens where the hint text stood; nothing moves.
2. The ready tasks slid under the cursor that had asked for them. They now stand above his orders; only his
   name's row is lifted.
3. The order a dropped condition meant stood in brackets at the end of the reading's first line. It has its own
   line under "Enter sends".
4. The map's mark for an exact order said "if the enemy comes" whatever its first line was. It says the line's
   own words ("holds Lorraine · if he is attacked · +1 more").
5. **This one touches the key's wording.** The key quotes Soult's card as one sentence ("Soult holds Lorraine —
   if he is attacked, dig in; if he is outnumbered, fall back to Champagne (2 of 2 left)"). The first frame shot
   showed that sentence CUT at the card's edge ("… if he is outnumbered, fall …"). The card now says "Soult
   holds Lorraine" and lists "His exact orders — 2 of 2 left:" with a line each. The key's test — "right if the
   reader says he digs in" — is unchanged, and the key above is left as it was written.

### What the readers said was confusing (not scored), each with its ruling

| What a reader said | Readers | Ruling |
|---|---|---|
| The card does not say which line wins when both are true | 3 of 3 | **BUILT** — the lines are numbered, and the card says "As a turn ends he carries out the first of them that is true — by himself, at no cost, each once." (row IC2-C6) |
| "[Ney, hold. If he is outnumbered …]" — odd brackets; "not clear whether I can click it or must retype it" | 3 of 3 | **BUILT** — the line reads "Or press to write: […]" (row IC2-C3; the brackets are the reading's own mark of a chip, older than this session) |
| "Charge him" is locked — "one victory as the attacker arms the charge" is cryptic | 3 of 3 | **BUILT** — "he needs one victory as the attacker first" (row IC2-C7) |
| The typed text is cut off in the box: "Ney," has scrolled out | 3 of 3 | **FILED** — row IC2-N1, Session H's head, with a strict-xfail driven pin: at this setup the command line shows about twenty characters. Not moved here: the left column is full at this setup, so the line's own row needs its own press |
| The map's mark "holds Lorraine · if he is attacked · +1 more" reads as cut off | 3 of 3 | **KEPT** — the mark is a summary by design; the card it opens lists every line. (Before this session it said "if the enemy comes" of every first line.) |
| "Not taken" might mean "nothing happens"; no sign whether the line was sent or only read | 2 of 3 | **KEPT** — every reader answered right from the line under it, "Enter sends: Ney, retreat" |
| The same condition is taken for Soult and refused for Ney, unexplained | 1 of 3 | **KEPT** — the refusal's own words say why ("this order takes no condition; it would go out now") and the next line offers the order that takes it |
| "Chase him" does not say what chasing does, or when it stops | 2 of 3 | **KEPT** — its hover says it ("A standing order: he follows him wherever he goes and attacks on contact"); a still picture cannot show a hover |
| Words of screens this session did not touch — "free · he may object", "retreat" shown as "fall back", "Put in line", "Bring up", "95% under a written order", "the muster committed", "2 points", "Europe's alarm", the rivals' paragraph, "Cancelling costs 1 action — no trust lost: it was given this turn", "Change selects him", the top bar's counters | each by 1 to 3 | **NOTES for Session H's reading** — the deploy session reads every screen; none of these was introduced here |

The three things built after the reading were pressed in the real client by the driven class
(`tests/test_dd_b_the_client_hands.py::TestRowIC7TheButtons`); `F2_after.jpg` and `F4_after.jpg` are that run's
frames. They were not put to a second reading: each answers a remark a reader made, and none changes an answer
the key tests.
