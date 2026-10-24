# DD-B — the re-measure (Pre-Deploy S14e, October 24, 2026)

*Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 row S14e. The first measure
(`docs/audits/DD_B_FRESH_EYES_2026_10_14.md`, October 14) found 69 causes in
60 turns — 11.5 rows per 10 turns, 3 P1 — and every row was fixed in S13b
(four parts, October 14–19). This measure reads the game Round 0 will meet:
the DD-B fixes, the nine rulings, VP-1 (S14b), the events (S14c), the table
lesson and the first-open lines (S14d).*

**Verdict.** Three fresh players, the same brief and the same roads, 20 turns
each in the real client at 5120×1440. Their 35 rows de-duplicate to **35
causes: 5.8 rows per 10 turns, 1 of them P1.** The done-when (under 5 per 10
turns and 0 P1) is **NOT met** — by one P1 and by five causes. Against the
first measure the rate halved (11.5 → 5.8) and the P1s fell from three to one;
**not one of the first measure's 69 causes was sighted again as filed**, and
every road reached Turn 21 without a script error. As the plan's rule
requires, every row is filed and homed:

- the 35 causes go to a new row, **S14f "the re-measure's rows"**
  (`BUG_FIXES.md` §S14E, S14E-1 … S14E-35), the P1 first;
- the four design halves go to `DESIGN_REFINEMENT.md` §S14E (S14E-D1 … D4),
  each with a recommendation, for the user at S14f's head.

Nothing in the game was changed in S14e. The instrument changed in four
small ways, each recorded (§7).

---

## 1. The instrument

`tools/dd_b_client.gd` and `tools/dd_b_play.py` as the first measure ran them
(`SYSTEMS_REFERENCE.md` §115): the game as it launches (the title screen, a
first launch, Interface Scale 1.4 derived for the screen), a sandboxed backend
on 8006 (the mock parser, the historical seed, its own saves; the user's 8005
never touched), real input events one action at a time, the full frame and
the state record after each. Each player got `docs/audits/dd_b/PLAYER_BRIEF.md`
verbatim and nothing else; the players were general-purpose agents on a
lower model, one at a time; two engines never ran at once.

| Road | Goal given | Turn reached | Actions | Typed lines sent | Wall time | SCRIPT ERRORs |
|---|---|---|---|---|---|---|
| conquest | win the war in the field; take Vienna | Turn 21 (July 1806) | 456 | 123 (12 typed under a modal, never sent) | 61 min | 0 |
| diplomacy-first | end the war at the table; make the peace or the alliances you need | Turn 21 | 403 | 19 | 49 min | 0 |
| the sea | break the blockade, raise Ireland, or carry the war across the Channel | Turn 21 | 290 | 72 | 40 min | 0 |

Settling took about 1 s an action and the record about 1.7–2.0 s. The
1,149 actions raised no SCRIPT ERROR. The records are
`docs/audits/dd_b/{conquest,diplomacy,sea}_2026_10_24/` (rows, the judge,
the actions, every action's summary, the players' notes, each cited frame).

## 2. The three campaigns, in the players' words

- **Conquest.** Two battles on turn 1; Mack's army destroyed and both
  Archdukes captured by turn 4; Vienna stormed on turn 3; the Treaty of
  Vienna on turn 5 kept four provinces. Russia and Britain each offered
  peace (turns 8 and 14) and both were taken. Then over-reach: the Staff
  law and the supply train, a war on Hanover despite Talleyrand's warning
  (alarm 45 → 73), the nine-court league the Balance of Europe page had
  forecast. On turns 16–20 the Fourth Coalition came: Kutuzov and Charles
  beaten, then Bagration's 46,000 beat the morale-0 corps one after another
  — Lannes, Bernadotte and Massena captured, Murat's corps destroyed,
  Napoleon out with 438 men. The player's own verdict: most of the disasters
  were over-reach, but several came from orders that did something other
  than expected.
- **Diplomacy-first.** Straight to the Cabinet; every offer "Hopeless" on
  turn 1; one limited campaign on turn 2 ("Ney, attack Mack" drew five corps
  and the Emperor) bought an Austrian armistice for 115 gold a turn, carried
  into peace by Improve Relations (turn 8); the same pattern with Russia
  (turn 14); Britain's own white peace on turn 10 dissolved the Third
  Coalition (threat 78 → 37). The idle gold went to buying off the designs of
  Sweden, Austria, Britain and Russia, licences, Code Abroad, the satellites.
  Bavaria was lost to Austria while the truce held; the Spanish alliance
  decayed to a defensive one with no lever found; 35 of the Congress's 45.
- **The sea.** The Admiralty book taught the camp: 40,000 men two turns on
  the Channel shore broke the blockade on turns 5 and 8. Dumonceau's Dutch
  corps took Munster on turn 6 and later lost Wales to Moore. The Grand
  Diversion at 50 in 100 failed and the fleet action gutted the navy (49 →
  25 sail) on turn 12. Austria beaten and at peace; Britain's white peace on
  turn 15 titled Munster — and, the player learned only afterwards from the
  Formable Nations page, paused the Free Ireland road, which wanted Ulster
  too and a table while the war ran.

Their notes are `docs/audits/dd_b/<road>_2026_10_24/player_notes.md`.

## 3. The metric

**How it is counted** (the first measure's rule): each road counts each
cause once, at its worst sighting on that road; the total across the three
counts each cause once, at its worst. Severity is the players' own. The
figures are read off the records by ONE tool, `tools/dd_b_metric.py`, which
reproduces the first measure's `metric.json` byte for byte from its records
(`TestTheMetricTool`); `metric_2026_10_24.json` holds them.

| | Player rows filed | Causes | P1 | P2 | P3 | Rows per 10 turns | First measure |
|---|---|---|---|---|---|---|---|
| conquest | 13 | 13 | 0 | 6 | 7 | **6.5** | 14.0 |
| diplomacy-first | 9 | 9 | 0 | 4 | 5 | **4.5** | 16.0 |
| the sea | 13 | 14 | 1 | 4 | 9 | **7.0** | 12.5 |
| **the three** | 35 | **35** | **1** | **14** | **20** | **5.8** (P1 0.2 · P2 2.3 · P3 3.3) | 11.5 (3 P1) |

One cause was sighted on two roads (the campaign pay a corps on allied soil
draws, unpriced by the muster — conquest #1, the sea #1); one sea row names
two defects (the cancel verb and the dropped keel count), so the sea's 13
rows are 14 causes. No row was struck.

**The done-when** is under 5 rows per 10 turns and 0 P1: NOT met. The
distance is small — the diplomacy road alone meets it — and the shape of the
rows changed: the first measure's were mostly controls that did something
other than they said (Counter, "Use Talleyrand's suggestion", Not Now,
Recall) and screens that contradicted each other; this measure's are mostly
**prices and consequences not stated at the point of choice** (§5).

## 4. The one P1

**S14E-1 — a typed march whose first step meets an enemy fights the battle
unasked when the marshal is aggressive** (the sea #6, turn 4, action 72).
"Massena, march to Milan" — a plain move home, with an armistice proposal to
Austria in transit — ran through Austrian-held Tyrol; Archduke John barred
the road and Massena attacked ("Archduke John bars the way! Engaging!"): the
corps system drew Ney, Davout, Lannes, Murat and Teulie to Tyrol, Europe's
alarm rose +8 (threat 89 → 97), 1,691 men were lost on the march, the
materiel paid. The cause is `_handle_first_step_blocked`
(`strategic_executor.py:2837`): on a MOVE_TO's blocked first step an
AGGRESSIVE marshal auto-attacks at a raw strength ratio of 0.7 or better —
the attack run with `_strategic_execution`, so no objection, no muster gate,
no quote — while below 0.7, and for every other personality, the same step
asks (the contact interrupt; the dispatch's "HALTED … bars the way. Awaiting
your word."). Reproduced on the code; the reply printed the road only after
the step (`:2179-2183`), the same seam as the conquest road's march-detour
row. It is the mirror of the first measure's DDB-D1 (an attack out of reach
that marched as a pursuit, ruled ASK FIRST), on the sibling verb; its design
half is **S14E-D1** (recommendation: ask first on the first step, every
personality alike — the aggressive marshal's temperament in his line, never
in acting unordered).

By the judge, every sent line of the three roads read as meant, asked,
answered or refused honestly: **0 P1 proxies** (§6). The P1 is the player's,
by the brief's rule — the game did something the player did not order.

## 5. What the players met most

Across the roads the 35 causes fall into four families, and the first is
two-thirds of them:

1. **A price or a consequence not stated at the point of choice** (22). The
   campaign pay seven corps on Bavarian soil will draw (−1,776g a turn,
   explained only in the Economy book — both the conquest and the sea player
   filed it first); the peace with Austria that shelters the Russian armies
   on Austrian soil; End Turn with spent corps beside a known 55,000-man
   army; a war declared on a court whose capital a third court already
   holds; the Grand Diversion's card that prices the window and the wait but
   not the half-fleet a failure loses; a march between two camp provinces
   that steps out of the camp and resets two turns of staging; a white peace
   at the table that costs an ally −18 and a grievance no screen priced; the
   Free Ireland road's next step on the Formable Nations page alone; "Not
   Now" shutting the Cabinet for the turn; "Buy Off Their Design" spending
   more than half the treasury on one click; an Open Borders letter that
   never says what open borders does.
2. **Two readings of one figure** (6). The Cabinet's 44 of 50 for Britain's
   armistice beside the preview's 24 (typed by the pair score on one road
   and the side sum on the other); the armistice preview's "war score reads
   0" under its own "War score: 38"; "unfavorable" beside 2.5:1 on the
   printed numbers (the band weighs an unseen corps and says nothing); the
   muster's "expect about 118,448" against 52,597 who came; Improve Relations
   "+0 over 2 turns" beside "Net +7 a turn"; Europe's quiet-turns clock that
   jumped 6 → 16 when the marshal it was stamped on stood down.
3. **A control that does something other than it says, or nothing** (5).
   "Adjust terms" on a peace France dictates opening France's own
   concessions wizard — with no Back, no Close and a dead Escape; "Let
   Talleyrand haggle" live on offers it can never counter; "Open ▸" in the
   Envoys panel that is not a button; "More generous" filling the accord
   with gold that cannot touch the legitimacy blocker.
4. **A line the game cannot read, or prints too late** (2). "Murat, cancel"
   not understood though the game itself prints "'Ney, cancel' recalls him";
   "how do I get to Vienna" dumping the whole manual into the four-line
   window — DDB-48's class on a verb its table never got.

**The first measure's fixes held.** None of DDB-1 … 62 was sighted again as
filed. Twelve of the 35 are siblings a fix's sweep missed (named in each
row: DDB-13's gate for the army, DDB-14's sanctuary for the preview and the
what-if, DDB-4's button, DDB-48's verbs, DDB-59's camp, DDB-61's price,
DDB-6's sentence, DDB-27's stored score, DDB-54's ladder, DDB-7's counsel,
DDB-41's exit, IQ10-6's printed sentence); the rest are new to this
measure, five of them on surfaces that did not exist on October 14 (the
designs' instruments, ruling J's war title, the table-ratified peace's
proposer-side pass, the first-open lines' neighbours).

## 6. The judge

Every sent typed line was classified by the ONE judge (`tools/_score_probes.py`
through `unrehearsed_census.classify_order` / `classify_question`); the
players stated each line's intent with `--meant`.

| Road | Lines sent | as_meant | answered | board_refusal | honest_refusal | shrug | unjudged (other) | misread / executed-when-refusal-meant |
|---|---|---|---|---|---|---|---|---|
| conquest | 123 | 57 | 52 | 1 | 4 | 4 | 5 | **0** |
| diplomacy-first | 19 | 14 | 4 | 0 | 0 | 0 | 1 | **0** |
| the sea | 72 | 59 | 8 | 2 | 1 | 0 | 2 | **0** |

**Two reply shapes the judge did not know** were corrected in `_score_probes`
("extend it there, never inline"), each checked first against the 4,350
orders of the committed census records, the first measure's lines and every
committed HOLD arm — none moves:

- **The muster's standing line.** "Standing modifiers, already in the band:"
  rides every executed attack since the muster rework and matched the board
  gate's `already in`: nine fought battles of the conquest road read as
  board refusals. Narrowed to `in(?! the band)`; a true "already in"
  refusal still reads.
- **A halt meant as a hold.** "Murat, halt" — meant as the nearest family,
  hold — answers "Murat halts his march and awaits new orders": the march
  cancelled, as the player wanted. The judge read it as the sea road's one
  P1 proxy; `hold` now reads it. The player's own row on that line (the
  cancel verb the game prints but cannot read) is S14E-32.

**Lines never sent.** Twelve conquest lines were typed while a modal held
the command line (an interrupt, the battle replay, a client's petition);
`_act_type` refuses before any key and the state says so (`ok: false`). The
judge had read them as shrugs and honest refusals; it now judges sent lines
only and lists the rest (`unsent`). The client's own silence there — no sign
on the line that it is not taking orders — is noted with the Escape-ladder
row (S14E-21) rather than filed alone.

**Read by hand.** Conquest #424 ("Soult, march to Vienna", filed as other)
did exactly as typed and printed its six-province road afterwards (S14E-22);
the sea #126 ("Murat, cancel") was refused honestly and #221 ("recall
Talleyrand") pointed at the Cabinet by the never-typed ruling. No line ran
something other than it said.

## 7. Instrument notes

- **The reader raced the rename.** One `act` in 456 raised a PermissionError
  reading a state file an instant before the engine's rename released it
  (the order itself went through). `_read` retries for 2.5 s.
- **A control's text was cut at 120 characters** in the record, so the
  Cabinet's instrument chips (lengthened by DDB-31) read as clipped while
  the real chip wraps — half of the diplomacy road's row 4 was the
  instrument's (`MAX_CONTROL_TEXT` is now 600). The row's other half, the
  unconfirmed spend, stands (S14E-26).
- **The judge's `ok` blindness** and the two shapes above (§6).
- **Small rule breaks**, all inside the players' own run directories: each
  player ran a few `python -c` / `sed` / `grep` one-liners over state files
  instead of the file-reading tool; none changed what they saw.
- **Two notes from the players' tool messages, unverified:** a `click
  <nation>` on a re-scrolled Cabinet list that returned ok without opening
  the page (the record holds no `click_taken_by` for it); `click Envoys`
  sometimes opening a letter directly. The summary's "new lines" reprints
  the Morning Dispatch after every action of its turn (the terminal's diff
  reads the whole window), which the sea player found noisy.
- **The metric by tool.** `tools/dd_b_metric.py` (§3); `--check` holds the
  records to each other as the first measure's pins do.

## 8. Where the rows go

- **S14f "the re-measure's rows"** — 35 rows, P1 first, each with its decided
  fix, its test (`tests/test_s14f_the_remeasure_rows.py::TestS14E<n>`), its
  STATUS line and the tag `⟨SF step=pre-deploy S14e · DD-B re-measure ·
  pillar=…⟩`. Sized at **2.0 sessions**: part 1 the P1 with its ruling's
  build, the four rulings' halves as ruled, and the fourteen P2s (S14E-1 …
  15); part 2 the twenty P3s (S14E-16 … 35) and the closing re-play of every
  sighting on the DD-B instrument. The sibling sweep in force (Rule 10).
- **`DESIGN_REFINEMENT.md` §S14E** — 4 rows, for the user at S14f's head:
  - S14E-D1 the march that fights unasked (ask first, every personality);
  - S14E-D2 the legitimacy tier reading the whole package (read the court's
    own slice);
  - S14E-D3 the table's shut-out price on a white peace (keep it, state it);
  - S14E-D4 the war title's ground rung with no weight floor (a floor).
  Each lands its defect half as written whatever the ruling.
- **A third measure** is not in the plan's rule (S14e's miss homes its rows
  to S14f; the deploy gate is 0 open defect rows). It is the user's call at
  S14f's close: the diplomacy road already meets the done-when and the rate
  halved once; a 1.0-session measure on the three roads after S14f would
  read the build the testers get.
