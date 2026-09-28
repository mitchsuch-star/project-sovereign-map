# Score Mandate — Session Exit, September 28, 2026

**Row SR, `docs/SCORE_MANDATE_PLAN.md` §5.**
- One exit per session, covering every slice that no earlier exit covered.
- One residue slice after it.
- **No §1 re-score** — the one full re-score happens at the end of the
  mandate.

The session began on September 27 (its second session that day). The exit
ran past midnight.

## 1. What this exit covers

This exit covers thirteen landed commits, none of which had been through an
exit before.

The previous exit, `SR_SESSION_EXIT_2026_09_27.md`, landed with its residue
as `b858b806`. The three commits after it are docs only: the SR-D1 ruling,
the SR-D2 doctrine ruling and its review, and the UI/UX and fun review. They
end at `6ceadabe`.

| Slice | Commit | What it changed |
|---|---|---|
| PC15-10 B2 "The petition dies with its subject" (+ F10, §6 Q3) | `641958dd` | A petition whose subject can no longer be answered retires with a line, never silently. |
| B3 "The crisis survives a new flow" (F6 / W7) | `9f4f5f94` | A vassal rebellion or the sabotage reckoning no longer dies when the player types a new flow over it; its consumed modal comes back. |
| B4a "The order, justified" (F8, §6 Q5) | `bbc5bae4` | Nine popup slots, each justified in a table. The dead `coalition_popup` slot is retired, `proposal_result` is decided as the documented receipt, and the end-turn carry is declared. |
| B4b "The one tail" (F9) | `ba446bbc` | One stash, one raise chain and one control-return tail in `main.gd`. Four client defects were reproduced by driving the client and fixed. |
| B5 "The acceptance" | `e9d32403` | The August flagship arm was re-run and passed all five §8 items: 3 blocking petition modals in 24 turns (was 19) and 0 silent losses. PC15-10 is accepted and Chunk 4 is build-complete. |
| SR-5r RF-0 + RF-1 "The Laws" | `3d115784` | The substrate, `enact` / `repeal` on the player's road, the Laws Net line, the lapse before ESP-4, R8 "The Arrears", and the Staff's fifth action. |
| RF-2 "The catalogue" | `9dcd0b0d` | The other eight effect types; 25 laws in five decks. |
| RF-3 "The AI enacts" | `cc2ed1b7` | Every rival great power enacts from its own deck through the same verb. The series was re-recorded once. |
| RF-4a "The LAWS tab" | `f3b76e76` | The Strategic Ledger's eighth book, honest-availability chips, the enactment confirm and one authority line. |
| RF-4b "The laws everywhere else" | `67b86bfe` | One lapse forecast on three surfaces, the rival courts' beats, the nation cards' Laws line, and the desk answers a law by name. |
| DP-1 "The bank" | `2d155640` | Diplomatic points bank one turn for every court (cap 7). |
| RF-4c "The School card and the visual pass" | `a0eb2cf7` | Card XVIII "The Laws of State", the laws frames at both Interface Scales, and T7 and T8 met. |
| The AI drill fix (user-directed) | `65e0d9c9` | P4.9 drill to heal, one reach predicate for every AI drill, and the drilling penalty applied (GR4). |

## 2. Method

**Four played arms.** Each ran on both trees, in process, through
`tools/playtest_driver.py`: saves sandboxed, mock parser, no key, hash seed 0.
- **Three standing exit arms:**
  - `sr_exit_first_contact.json` (`--turns 2`);
  - `sr_exit_aar_typed.json` (`--turns 18 --objection insist --diplomacy accept`);
  - `sr_exit_chunk4_field.json` (`--turns 10 --objection insist --diplomacy decline`).
- **Chunk 5's laws evidence arm**, committed with this memo as
  `tools/playtest_scripts/sr_exit_chunk5_laws.json` (`--turns 10 --diplomacy accept`).
  Over ten turns it:
  - asks the desk about the laws;
  - enacts an authority law (the Anticipated Class) and a gold law (the Code
    Abroad) through the Council's quote;
  - tries the Staff every turn until the chest can buy it;
  - repeals a law (turn 7) and re-enacts it at full price (turn 8);
  - asks for the diplomatic points.

  Its military lines are RF-3's commanded arm, turns 1–10.

**The two trees.**
- **Before: `6ceadabe`**, checked out with `git worktree add --detach` in the
  scratchpad and removed afterwards.
- **After: the drill fix's tree.** The arms ran against it while its
  pre-commit hook ran, and it landed unchanged as `65e0d9c9`.

**The reads.**
- Every typed line's reply was paired across the two trees.
- Petitions were counted per turn from the digests' POPUP lines:
  `marshal_petition` = a modal, `marshal_audience` = the antechamber.
- AI drills were read from the enemy phase's visible verbs.
- Every after-tree reply was scanned for a roster key where a printed name
  belongs.

**Balance.** `BASELINE_SERIES` was re-recorded twice this session, each time
by a flip-attributed slice: RF-3's AI enactments (two arms) and the drill fix
(seven arms). Every other slice held it byte-identical, and M1–M7 were
byte-identical at every commit.

## 3. What the exit read

### 3.1 First contact (28 lines, 2 turns)

- **27 of 28 replies identical; refusals 0 → 0.**
- **Petitions:** one audience per turn and no modal, on both trees.
- **The one change:** "who is winning" reads +15 where it read +16 on turn 2.
  **A flip attributes it to the drill fix.** Its five levers down restore +16;
  RF-3's lever down (`reforms.THE_AI_ENACTS=0`) still reads +15.

### 3.2 The AAR arm (18 turns)

**36 identical, 124 changed; refusals 47 → 45.** Most of the change is
drift, not defects:
- The boards part from turn 1: the rival courts' laws (Britain enacts the
  Orders in Council on turn 1, Russia the Opolchenie on turn 2) and the drill
  fix both move the AI.
- From turn 11 the pairing compares different world turns. On the after
  tree, turn 10's `recruit for Marmont` spent its last action and the turn
  ended there, so the script's `end turn` ended turn 11 with four actions
  unused. Past that point the pairing classifies lines; it does not attribute
  them.

**Petitions.** Two modals on both trees (turns 10 and 13, the crisis tier).
Audiences went from 9 to 11.

**Turns 3–10, where the boards still align:**
- **Raw keys.** Massena's fortify is now refused because two corps stand on
  his field, printed as "Enemy present: ArchdukeCharles, ArchdukeJohn". Turn
  8's attack is refused as "Cannot attack ArchdukeCharles — armistice with
  Austria". Both are **F6**.
- **Soult's pursuit of Kutuzov** is now mustered: the after board knows where
  Kutuzov stands.

**A defect on the after board (F7).** On turn 13, `guarantee Kingdom of
Italy` succeeded, one turn after `invest in Kingdom of Italy` was refused
because the kingdom had been eliminated.

**AI drills.** No AI drill was visible in either tree's enemy phase on any
arm; every drill was out of the arms' sight. The drill fix's own evidence
remains its measurements: on the ambient board, 9 AI drills (7 within reach)
became 1 (none within reach).

### 3.3 The Chunk 4 arm (10 turns)

**32 identical, 36 changed; refusals 13 → 15.** The new refusals:
- On turns 6 and 8, Vienna is already French — the after board took it on
  turn 5.
- Massena's fortify is refused as engaged (F6).

**Petitions:**
- Before: one modal (turn 10) and six audiences.
- After: two modals (a rivalry crisis on turn 7, and turn 10) and five
  audiences.

The garrison fights read as the previous exit recorded them.

### 3.4 The laws arm (10 turns, new)

**Before tree.** It has no laws. Its 23 refusals include every law order
("I cannot interpret that order"), and its questions about the laws were
shrugs ("I cannot answer that from the dispatches").

**After tree: 20 identical, 51 changed; refusals 23 → 17.** The laws road
read as follows.

**The desk and the prices.**
- "what laws are in force" answers from the ledger's own rows.
- The authority price and the marshals' calm are quoted before each
  enactment:
  - the Anticipated Class on turn 1 ("Authority 100 → 85 — the marshals' calm
    holds above 70");
  - the Code Abroad on turn 2 ("90 → 75");
  - the Code Abroad re-enacted on turn 8 at its full price ("85 → 70 — the
    marshals' calm above 70 is lost"). A repealed law is never in arrears
    (R3).

**The Staff.**
- It was refused on turns 3, 4 and 5 with its price and the purse (4,073,
  5,546 and 7,850 gold).
- It was enacted on turn 6 at 9,615 (9,000 spent).
- The fifth action is on the wire: turn 10 ends "5 actions unused".

**The repeal (turn 7):** "its 100 gold a turn ends, and nothing is refunded.
Enacting it again costs its full price (15 authority)."

**The Laws Net line:** 550 a turn on turns 6 and 9 — the Staff 300, the
Anticipated Class 150 and the Code Abroad 100, the ledger's own sum.

**The rival courts enact, and the dispatch says so:** seven THE LAWS beats in
ten turns (Britain three, Russia two, Austria one, Prussia one).

**No lapse.** The chest never fell below the bills.

**Findings on this arm:**
- **F1:** the bare word `laws` got Berthier's shrug on both trees.
- **F2:** "what does the Code Abroad do" answered with the Code Abroad's
  price, not what it does.
- **F3:** every refused gold law said its price twice: "The Artillery
  Reserve: 3,000 gold, then 150 gold a turn — the Artillery Reserve costs
  3,000 gold; the treasury holds 800".
- **F4:** "how many diplomatic points do I have" (turn 6) opened Talleyrand's
  assessment on both trees ("An astute question, Sire. Let me assess our
  position."). The driver's first-option policy then walked it into a peace
  proposal to Britain, refused as a paradox. The count the question asked for
  was never given.
- **F5:** turn 9's morning lead read "Sire — Rhineland has fallen. Enemy
  colours fly over French homeland soil. ArchdukeCharles's corps of 19,418
  stands there." The before tree printed the same clause on its own turn 9
  ("ArchdukeCharles's corps of 13,718").
- **F6:** the drill refusal (turn 8) read "ArchdukeCharles is at Rhineland,
  just one region away".

### 3.5 What the arms could not reach

- **A lapse** — no arm's chest fell below its bills. It is read through
  RF-4c's T7 pin: the staged lapse and the one Arrears price, 4,500 + 900.
- **The Staff's SITUATION line and the header's "Actions: 5/5"** — the digest
  does not record them. RF-4c's T8 census and the header pin read them.
- **DP-1's carry** — the digest records no pool. The residue's desk answer
  now states it ("5 came with this morning's refill and 2 were carried from
  last turn"), and that answer is pinned.
- **B3 (a crisis surviving a new flow) and B4b (the client's one tail)** — no
  arm raised a vassal rebellion or a sabotage reckoning, and the driver is not
  the client. B4b's four defects were reproduced by driving the client in
  their own slice.
- **Server consoles:** 0 tracebacks on all eight runs.

## 4. Findings

| # | Kind | Finding | Disposition |
|---|---|---|---|
| F1 (SRX-11) | desk | **The bare word "laws" got Berthier's shrug** ("this order eludes me"), where "economy" and "status" are answered. | **Fixed by the residue** |
| F2 (SRX-12) | desk | **A question that names a law was answered with its price alone** — "what does the Code Abroad do?" never said what the Code does. | **Fixed by the residue** |
| F3 (SRX-13) | copy | **A refused law said its price twice**, the head's price and the refusal's own price sentence. | **Fixed by the residue** |
| F4 (SRX-14) | routing (P2) | **"How many diplomatic points do I have?" opened Talleyrand's assessment.** "diplomatic" contains "diplomat", one of the diplomat's address names, and the count had no desk kind. Answered with its first options, the question becomes a proposal. | **Fixed by the residue** |
| F5 (SRX-15) | legibility | **The morning lead printed the occupier's roster key.** It was the one name in the dispatch not passed through the humaniser, and the client translates nation keys only, so "ArchdukeCharles's corps" reached the screen. | **Fixed by the residue** |
| F6 (SRX-16) | legibility | **Four refusals printed roster keys:** fortify ("Enemy present: ArchdukeCharles, ArchdukeJohn"), drill (both forms), the attack's truce refusal, and its pursue-road sibling. **Found in passing:** the pursue road's truce refusal still read the war-entry floor in `armistice_cooldowns` for its "turns remaining". SR-3a (ii)'s CRT-7 rider had moved only the attack road onto the truce's own clock. | **Fixed by the residue** |
| F7 (SRX-17) | correctness (P2) | **An eliminated court could be guaranteed.** The three instruments (guarantee, sponsor, buy off) share one gate, and it let an eliminated court through. "guarantee Kingdom of Italy", a turn after the kingdom fell, charged 1 DP and pledged to defend soil it no longer had, while "invest in" the same court was refused. | **Fixed by the residue** |

**Read and kept (not defects):**
- **The AAR arm's turn-11 misalignment.** The game ends a turn on the order
  that spends its last action. The script is not a player; a player reads
  "Turn 10 ended".
- **"yes" after the expedition quote got a shrug.** The driver's
  clarification policy had already answered the confirm (the landing took
  Munster), so there was nothing left to confirm.
- **"Berthier, remind me what the Russians demanded at the table" shrugs on
  both trees.** This is SRX-5, filed by the September 26 exit and owned by
  Chunk 6 (SR-6).
- **The enemy phase's own messages carry roster keys** ("ArchdukeCharles's
  forces press forward"). The enemy-phase dialog rebuilds its lines from the
  action type and does not render the `message` field (the CA8 method
  caveat). The wider census of name interpolations stays NPC-12's.

## 5. The residue slice

One slice, seven fixes (rules `SYSTEMS_REFERENCE.md` §74.9; pins
`tests/test_sr_exit_residue_2026_09_28.py` 41; sweep
`tools/_sweep_sr_exit_residue_2026_09_28.json` 23/23 killed, 0 INERT; zero
`.gd`):

- **SRX-11:** the whole line "laws" / "the laws" / "our laws of state" — with
  or without an address ("Berthier, laws") — is the laws answer. Lever
  `llm_client.THE_BARE_WORD_ASKS_FOR_THE_LAWS`.
- **SRX-12:** a question that names a law is answered with the law's authored
  `says`, whether or not the law is in force. Lever
  `first_contact.THE_LAW_NAMED_SAYS_WHAT_IT_DOES`.
- **SRX-13:** a refused law's line keeps only what the court holds ("…, then
  300 gold a turn — the treasury holds 800"; an authority law "the court
  holds 5 authority"). Every other refusal stays whole. Lever
  `first_contact.A_REFUSED_LAW_STATES_ITS_PRICE_ONCE`.
- **SRX-14: the desk counts the points.**
  - A new desk kind, `points`, is asked **before** the diplomat's address
    (`question_desk.classify_points_question`). It covers "how many
    (diplomatic) points / DP / (military | admin) actions | orders do I / we
    / you / Talleyrand have (left)" and "what actions / orders / points do I
    have (left)".
  - The answer reads the sources the top bar and the command header print:
    the pool and its ceiling (`diplomacy.displayed_dp_ceiling`), the
    refill's split (DP-1's `world._dp_refill`), and the day's orders and
    administrative actions (`world.get_action_summary`).
  - The minister may be its addressee (`parser.py`'s addressee exemption).
    Before this, "Talleyrand, how many points do we have?" was refused as a
    marshal typo.
  - Lever `question_desk.THE_DESK_COUNTS_THE_POINTS`.
- **SRX-15 and SRX-16:** the humaniser at the five producers — the soil
  alarm's clause, the fortify refusal, the drill refusal (both forms), and
  the two truce refusals, which also print the court by its display name.
  The pursue road's truce refusal now reads `ARMISTICE_DURATION −
  armistice_turns`, the attack road's clock. No levers: no decision reads
  these strings, and the clock is a number in a refusal.
- **SRX-17:** the instruments' shared gate
  (`DiplomaticExecutor._instrument_preflight`) asks the invest verb's own
  predicate and sentence (`VassalExecutor._eliminated_court_refusal`, one
  source, each verb with its own tail). An eliminated court is refused and
  nothing is charged. The guarantee's success line now names the court as
  printed ("France guarantees Papal States."). No lever: only the parser
  emits the three instrument actions, and the AI never takes the typed road.

**Two pins re-seated consciously:**
- `test_rf1_the_players_road.py::TestTheWords::test_the_answer_puts_a_refusal_in_its_place`
  pinned the double price (F3).
- The corpus row `srx0928-points-dp` is stated positively (`action: status`).
  To the Cabinet-door census (`test_wo_slice7_cabinet_door.py`), a
  `not_action: diplomatic*` row means a negated diplomatic order, which this
  row is not.

**Corpus:** five rows added (the bare word ×2, the points ×3).

## 6. Where the program stands

- **Chunk 4 is CLOSED.** Its last slices, B2–B5, have been through this exit
  (§5: a chunk is closed when its last slice has been through a session
  exit). Every slice of it has now been through one.
- **Chunk 5.** SR-5r (RF-0 → RF-4c + DP-1) is built and has been through this
  exit; RF-4 closes on the user's visual sign-off. Still to build: SR-5a "The
  chest", SR-5b "The second road at sea", SR-5c "The Descent's second throw"
  and the reserve. The session-exit evidence §2 names for Chunk 5 is owed by
  the exits that cover them: the IQ-1 exit's three arms, a played Descent or
  strangulation arc, and the Continental System shut-out arc played.
- **Open with the user:**
  - the RF-4 visual sign-off (the laws frames, card XVIII, the header's
    "Actions: 5/5");
  - **AIDR-D1: may an enemy literal drill to heal?** Measured, Mack's 40
    debased turns fall to 19 if he may. The recommendation is to allow it.
- **NEXT = the ECONOMY BALANCE pass**, by the user's September 27 direction:
  Britain should be richer than France.
  - At boot, Britain's Net (1,901) barely edges France's (1,842), while
    France's gross income is twice Britain's.
  - A commanded France banks about 2,300 gold a turn, and the Staff on turn 5
    is the symptom.
  - It opens SR-5a "The chest", whose question-(c) gate — the victor's Net
    ratchet — it meets.
