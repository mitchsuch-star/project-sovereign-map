# DD-B — The fresh-eyes campaign (Pre-Deploy S13, October 14, 2026)

*Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 row S13 and §3 DD-B. The weak
spot it measures: hand-played campaigns had found 16.5 defect rows per 10 turns
while scripted runs found 0.4 — the driver answers every popup by policy and
never clicks, and the client is where the player lives.*

**Verdict.** Three players who had read nothing played 20 turns each in the
real client at the user's resolution. Their 96 rows de-duplicate to **69
causes: 11.5 rows per 10 turns, 3 of them P1.** DD-B's done-when (under 5 per
10 turns and 0 P1) is **not met**. As the plan's rule requires, every row is
filed and homed:

- the 62 client, copy and backend defects go to a new row, **S13b "DD-B
  fixes"** (`BUG_FIXES.md` §DD-B, DDB-1 … DDB-62), P1s first;
- the 9 design questions go to `DESIGN_REFINEMENT.md` §DD-B (DDB-D1 … D9),
  each with a recommendation, for the user at S15.

Nothing in the game was changed in S13.

---

## 1. The instrument

`tools/dd_b_client.gd` and `tools/dd_b_play.py` (rules: `SYSTEMS_REFERENCE.md`
§115; pins: `tests/test_dd_b_the_client_hands.py`):

- **The game as it launches.** The title screen, a first launch (nothing marked
  seen), a 5120×1440 window parked past the desktop, Interface Scale 1.4 as the
  menu derives it for that screen.
- **The backend.** A sandboxed backend on 8006: the mock parser, the historical
  seed, its own saves. The user's 8005 was never touched.
- **Real input.** The players act one action at a time through real input
  events: typing key by key, real clicks at a control's centre, keys and the
  mouse wheel.
- **Each action's record.** The full frame, a 2560-wide view, and a state
  record of everything visible.

Each player got the brief `docs/audits/dd_b/PLAYER_BRIEF.md` verbatim and
nothing else. The rules: run only the play tool, read only your own run
directory, play as a player would. The players were general-purpose agents,
one at a time; two engines never ran at once.

| Road | Goal given | Turn reached | Actions | Typed lines | Wall time | SCRIPT ERRORs |
|---|---|---|---|---|---|---|
| conquest | win the war in the field; take Vienna | Turn 21 (July 1806) | 368 | 125 | 54 min | 0 |
| diplomacy-first | end the war at the table; make the peace or the alliances you need | Turn 21 | 298 | 38 | 40 min | 0 |
| the sea | break the blockade, raise Ireland, or carry the war across the Channel | Turn 21 | 409 | 79 | 55 min | 0 |

Each action took about 3 s in the engine: settling took about 1 s, and writing
the frame and the record about 1.6 s. The 1,075 actions raised no SCRIPT ERROR.

## 2. The three campaigns, in the players' words

- **Conquest.**
  - *Turns 1–4:* Mack was destroyed on turn 1. Archduke Charles was broken
    and captured. Vienna was stormed on turn 4, and Austria signed a separate
    white peace that left Vienna, Bohemia and Tyrol French.
  - *Turns 9–15:* Britain signed a white peace on turn 9. A war on Prussia
    took four provinces, and the alarm it raised formed the Fourth Coalition
    on turn 15.
  - *Turns 15–20:* the second half went badly. Five marshals were captured
    and Vienna was lost.
  - *End:* 35 of the Congress's 45 titled provinces.
- **Diplomacy-first.**
  - *Turn 1:* every road to the table was shut.
  - *Turns 2–4:* the player fought "just enough to get a seat" (Mack captured
    on turn 2, Charles broken on turn 4), then ratified a separate peace with
    Austria on turn 4.
  - *Turns 5–10:* made Bavaria a vassal and Prussia a full ally, and accepted
    a British armistice. Britain's white peace covering Russia ended the
    Coalition's war at the table on turn 10.
  - *Turn 11 on:* the alliance carried France into Prussia's war on Hanover
    (a P1), and the Congress stalled at 38 of 45.
- **The sea.**
  - *The blockade:* it rotted the fleet's readiness 5 a turn, so the Descent
    was never risked.
  - *Ireland:* Oudinot (newly commissioned) landed in Munster and Dumonceau's
    Dutch corps in Ulster.
  - *The peace:* a British truce lifted the blockade, and the peace that
    followed titled both Irish provinces to France. The fleet grew from 46 to
    71 sail, and readiness rose from 50 to about 92.
  - *Turn 10:* the Dutch contingent left Ulster unordered when the war only
    paused (a P1).

Their notes are `docs/audits/dd_b/<road>/player_notes.md`.

## 3. The metric

**How it is counted.** Each road counts each cause once, at its worst sighting
on that road. The total across the three counts each cause once, at its worst.
Severity is the players' own; `metric.json` holds the figures.

| | Player rows filed | Causes | P1 | P2 | P3 | Rows per 10 turns |
|---|---|---|---|---|---|---|
| conquest | 34 (1 struck) | 28 | 0 | 11 | 17 | **14.0** |
| diplomacy-first | 34 | 32 | 2 | 7 | 23 | **16.0** |
| the sea | 28 | 25 | 1 | 9 | 15 | **12.5** |
| **the three** | 96 | **69** | **3** | **21** | **45** | **11.5** (P1 0.5 · P2 3.5 · P3 7.5) |

**The done-when** is under 5 rows per 10 turns and 0 P1: NOT met. The players
hit the same weak spot the plan named. Hand-played turns in the client find
defects at the rate the plan measured: the raw rates of 16.5, 17.0 and 14.0
per road sit at the 16.5 it quoted.

## 4. The three P1s

1. **DDB-1 — Talleyrand's objection arrives after the proposal has already gone**
   (diplomacy #23/#24/#31/#32, sea #20/#26).
   - **What happened.** On a vassal proposal, "Use Talleyrand's suggestion"
     sent the proposal: the DP was charged, the proposal was put in transit,
     and the running mission paused. The TALLEYRAND OBJECTS popup, queued
     without its dialogue's id, rose only afterwards.
   - **Why "Modify Proposal" could not help.** By then the proposal was
     already on its way, so Modify changed nothing.
   - **The rest of the flow.** The suggestion is the very terms Talleyrand
     objects to. The objection strips the soften controls. The button's
     "Favorable" scores a vassalage with no terms at all.
2. **DDB-2 — A full alliance carries France into its ally's offensive war without
   a word** (diplomacy #29/#30). One turn after the general peace, France
   "joined Prussia's war against Hanover, honoring their alliance". The alliance
   proposal had listed only open borders and a payment, and as a non-leader France
   could not settle. The design question (should a full alliance join an
   OFFENSIVE war, may a non-leader leave) is DDB-D8.
3. **DDB-3 — A client's contingent garrisoning a conquest marches home, unordered,
   when France's war only pauses** (sea #19/#21).
   - **What happened.** `shared_enemies` counts only WAR. An armistice with
     Britain, with Austria at peace, left France and Holland no shared enemy,
     so Dumonceau left Ulster for Amsterdam, 11 turns away through Britain.
   - **The withdrawal message.** It then reported him "not moved".
   - **The design question.** Should a truce pause the shared war? That is
     DDB-D9.

## 5. What the players met most

**Seen on all three roads:**
- **DDB-D2, six sightings — the muster arrives with the battle's result.** Who
  will march, who will not and why, the band, the resentments: all of it
  prints in the same reply as the outcome. It pauses for a decision only for
  a cautious marshal at bad odds. Every player named it among their three
  biggest confusions.
- **DDB-7 — the Cabinet's recommended action sits below the fold.** The
  counsel names an action, the court's page lists it ninth, and nothing says
  more rows follow.

**Seen on two roads:**
- **DDB-1, six sightings — the objection arrives after the send.** The P1
  above.
- **DDB-48, six sightings — "how do I …?" dumps the whole manual.** It lands
  in a four-line window (DDB-57), and "help navy" is not understood.
- **DDB-10, five sightings — the Cabinet door.** The help, the Congress table,
  the Recall chip and the bid chip all teach typed diplomacy, which the client
  then refuses.
- **The peace table.** DDB-5: a white peace reads "no map redrawn" while it
  titles provinces. DDB-8: a separate peace is offered, then blocked two
  screens later. DDB-11 (the sea only): the table and the hand-off disagree by
  55 points. DDB-6: easing with France's gold lowers acceptance. DDB-23:
  per-turn streams carry no duration.
- **The war room.** DDB-13: the treasury goes negative at End Turn unwarned.
  DDB-46: the notice rail never retires a stale card. DDB-54: Escape twice
  after typing.

Across the roads the rows fall into four families:
1. **Learned only after acting.** The muster, the supply attrition, a battle's
   gold, an ally's petition, a captured marshal's fate.
2. **Controls that do something other than they say.** Counter, "Use
   Talleyrand's suggestion", Not Now, Recall, "Press <court>", "More generous".
3. **Two screens that disagree.** The settlement table against its hand-off;
   the treaties book against the Cabinet; an objection's odds against the
   muster's.
4. **Questions the game cannot answer.** Two-part questions, prisoners, "how
   do I …", the fleet's postures.

## 6. The judge

Every typed line was classified by the ONE judge (`tools/_score_probes.py`,
read through `unrehearsed_census.classify_order`). The players stated each
line's intent with `--meant`.

| Road | Lines | as_meant | asked | board_refusal | answered | honest_refusal | shrug | unjudged (other) | misread / executed-when-refusal-meant |
|---|---|---|---|---|---|---|---|---|---|
| conquest | 125 | 93 | 3 | 5 | 14 | 5 | 3 | 2 | **0** |
| diplomacy-first | 38 | 23 | 2 | 2 | 8 | 1 | 2 | 0 | **0** |
| the sea | 79 | 62 | 2 | 0 | 8 | 1 | 1 | 5 | **0** |

**Two reply shapes the judge did not know** were added to `ACTION_WORDS`,
"extend it there, never inline":
- **The assault on a province's works** ("ASSAULT — Ney storms the works",
  "assaults the garrison", "Captured:", "lays down its arms", "falls to
  France", "unopposed"). It accounted for 12 conquest lines first read as
  misreads; each had done exactly the attack meant.
- **A support halted at the approach** ("Soult reaches the approach to
  Swabia"). One diplomacy line.

Both extensions were checked before landing: neither moves a class in any of
the 4,350 orders of the committed census records, nor touches a HOLD command
line.

**Read by hand.** Three lines ran something other than the line said, and said
so in the reply: conquest #13 (an attack became a pursuit to Dresden), conquest
#32 (artillery became infantry), and sea #11 (the keel was laid at Bordelais,
not Normandy). By the census's own hand verdicts these are **disclosed**, not
the dangerous class. They keep the players' severities (P2, P3 and P3), and
the first two carry design questions (DDB-D1, DDB-D5).

The shrugs are questions the desk cannot answer (a prisoner, two questions in
one line); the honest refusals are mostly board refusals whose shape the judge
deliberately does not hold. Neither class is a P1.

## 7. Instrument notes

- **The struck row.** The conquest player's "Massena is missing from the
  opening roster" (row #2) was the instrument's doing. The summary cut a
  turn's new lines to the last 40, and the dispatch's first MARSHAL STATUS
  line (Massena) fell under the cut. The row is struck, and the summary was
  fixed during road 2: up to 80 lines, and any cut is said.
- **A harness keystroke.** `type` pressed End before typing, so the diplomacy
  player's Ctrl+A selection was appended to (action 43, "DavoutNapoleon, march
  to Rhineland"). The game asked which marshal; no row came of it. It was
  fixed before road 3.
- **Small rule breaks.** The players broke the "run only the play tool" rule
  in small ways, all inside their own run directories: a `python -c` and a
  grep over a state file (conquest), and an `echo` plus piping `act` through
  `grep`/`head` (the sea). None of it changed what they saw. Two lines of the
  brief were sharpened after road 1, before road 2 (recorded in the brief).
- **The keyboard focus.** The parked window never holds the OS focus, and
  Godot 4.4's LineEdit does not start editing on `grab_focus` without it. The
  harness gives the focused command line the editing state a player's window
  gives it (§115.1), and says so in each record.
- **Long replies.** The state record caps a text row at 4,000 characters. The
  full help reads only in the client's four-line window, which is itself a row
  (DDB-57).

## 8. Where the rows go

- **S13b "DD-B fixes"** — 62 rows. Every row names its decided fix, its test
  (`tests/test_ddb_s13b_<slice>.py::TestDDB<n>`), its STATUS line and the tag
  `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`. The slices:
  - S13b-1 the P1s (3);
  - S13b-2 the table (23);
  - S13b-3 the field (17);
  - S13b-4 the voice (9);
  - S13b-5 the client (4);
  - S13b-6 the sea (6).

  It is sized at **3.0 sessions**: part 1 covers S13b-1 and S13b-2, part 2
  S13b-3 and S13b-4, part 3 S13b-5, S13b-6 and the re-measure. In the
  re-measure, three fresh players play the same brief on the same roads in
  the client, and the metric is read again.
- **`DESIGN_REFINEMENT.md` §DD-B** — 9 rows, for the user at S15:
  - DDB-D1 the out-of-reach attack that becomes a pursuit;
  - DDB-D2 the muster as a preview;
  - DDB-D3 garrison losses scaled by odds;
  - DDB-D4 the turn that ends itself;
  - DDB-D5 the recruit arm override;
  - DDB-D6 falling back onto an ally's province;
  - DDB-D7 a gold sink on the peace road;
  - DDB-D8 an alliance that joins offensive wars;
  - DDB-D9 a truce that pauses a contingent's war.

  If the user rules BUILD, a row lands at S15's head, before the release
  build. **DDB-D2 is the weightiest:** seen on all three roads, the first
  confusion every player named.
