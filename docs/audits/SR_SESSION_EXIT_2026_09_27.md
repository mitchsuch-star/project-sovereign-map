# Score Mandate — Session Exit, September 27, 2026

**Row SR, `docs/SCORE_MANDATE_PLAN.md` §5** (one exit per session, over every
slice no earlier exit covered; one residue slice after it; **no §1 re-score** —
the one full re-score happens at the end of the mandate).

## 1. What this exit covers

Three landed slices, none through an exit before (the previous exit,
`SR_SESSION_EXIT_2026_09_26.md`, ended at `23bd2e57`):

| Slice | Commit | What it changed |
|---|---|---|
| SR-4c "The drama's fuse" (the Jealousy gate re-opened, `JEALOUSY_SPEC.md` §0.7) | `0825172f` | the laurel floor at the glory chokepoint; the crown wants 3 glory; a man who asked waits 6 turns; a lost crown says where it went |
| PC15-10 B1 "The Antechamber" (`PETITION_POPUP_REVISIT_SPEC.md` §9 B1) | `42a6c5a8` | routine audiences wait on the rail / Generals card / top bar; the crisis tier keeps the modal and evicts an audience |
| The Chunk 4 reserve (AAR4-X1, AAR24-X1/X2/X3, AAR10-X1, AAR32-D1, SRX-7, SRX-8) | `bdc0fe22` | the captor raises his own garrison; guns do not storm works; the counter-punch rides the assault; the objection reads what the attack engages; Rule 12 is the guns'; the favorable line weighs the generals; the driver closes an unratifiable table; the lesson runs on its own draws |

**Not built this session:** B2–B5 (the rest of PC15-10). The user's order put
them "as the session allows" after B1; the session's budget went to the
reserve, Chunk 5's gate and this exit. They stay queued, owned by
`PETITION_POPUP_REVISIT_SPEC.md` §9 (B2 supersede + the other kinds'
retirement + F10; B3 W7; B4 the stash chokepoint + F8; B5 the acceptance
re-run), STATUS ▶ NEXT UP carrying them. **Chunk 4 therefore stays OPEN**:
every slice it landed has been through an exit (SR-4a on September 26, the
rest here); it closes when B2–B5 land or the user re-homes them.

## 2. Method

- **Three played arms**, each run on BOTH trees in-process through
  `tools/playtest_driver.py` (saves sandboxed, mock parser, no key, hash seed
  0): the two committed exit arms — `sr_exit_first_contact.json` (`--turns 2`,
  28 typed lines) and `sr_exit_aar_typed.json` (`--turns 18 --objection insist
  --diplomacy accept`, 145 sent) — and **Chunk 4's evidence arm**, committed
  with this memo: `tools/playtest_scripts/sr_exit_chunk4_field.json`
  (`--turns 10 --objection insist --diplomacy decline`, 68 sent). The evidence
  arm is the AAR player's own opening (turns 1–6, which storm Vienna's works on
  turns 5–6) played with the war left open, so that on turn 7 Mack and
  Archduke John stand STACKED at Carniola beside Ney and Murat — measured on
  the shipped board by a scratch position census before the arm was authored.
- **The before tree is `23bd2e57`**, checked out with `git worktree add
  --detach` in the scratchpad (its Godot import cache seeded from the main
  tree) and removed afterwards.
- A **drama census** wrapped the two campaign arms on both trees (counting
  wrappers on `record_battle_glory`, `apply_jealousy`, `_push_petition` and
  `recompute_crowns`): glory by battle size, envy fires, petitions pushed with
  their tier and status, the crown per turn. **Petitions per turn** are the
  digest's POPUP lines: `marshal_petition` = a modal, `marshal_audience` = the
  antechamber.
- Every typed line's reply paired across the two trees and classified.
- `BASELINE_SERIES` + M1–M7: byte-identical at all three commits (each
  commit's pre-commit hook ran the full suite; SR-4c and the reserve each
  carry a flip-arm attribution with the reach counted).

## 3. What the exit read

### 3.1 First contact — the ten-minute test (28 lines, 2 turns)

**27 of 28 replies identical; 1 reworded; refusals 0 → 0.** The one change
is the morning desk ("what happened last turn") now naming the waiting card:
"… Murat appears envious of Ney's laurels — he has grown restless for glory;
**Murat seeks an audience, Sire — his card waits on the Generals screen and on
the rail** …". **Petitions: 2 modals (turns 1 and 2) → 0 modals, 2
audiences.** The first ten minutes no longer open with a grievance modal.

### 3.2 The AAR arm (145 lines, 18 turns)

**132 identical, 12 reworded, 1 now refused; refusals 46 → 47.** All twelve
rewordings are small numeric drift with one cause, SR-4c's crown floor (both
boards): the before tree crowned Ney (1 glory) and Bavaria's Deroy (2) on
turn 1 and Archduke Charles (1) on turn 2; the after tree crowns no one until
Ney on turn 3 with 4. The first battle to differ is turn 2's Charles against
Deroy — the crowned Deroy's +1 defense had cut his losses (4,469 before,
4,788 after) — and from there march losses move by a man or two, a war score
by a point, a substitute price by a few gold, a garrison count by 85. The one
new refusal is honest: "invest in Kingdom of Italy" finds the client's
loyalty already full ("the investment would buy nothing, so nothing is
charged") where the before tree bought one point.

- **Petitions: 13 modals (turns 1, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 17)
  → 2 modals (the Bernadotte–Ney breach on turn 10, Lannes's entrenched
  grievance on turn 13) + 9 audiences.** Envy fires are identical (21 = 21):
  SR-4c's clock suppresses the CARD, not the grievance — Murat, who asked on
  turn 1, does not ask again on turn 4, and Bernadotte's level-1 card takes
  the slot instead.
- **The laurel floor binds 0 of 15 glory calls** (every battle cost at least
  1,000 dead), as SR-4c measured.
- **SRX-7 in live play:** on turn 7 the white-peace table was dialled harsher
  **16 times to the answer-chain cap** on the before tree; the after tree
  dials once and closes it with the engine's own blocker — "closed — still
  unratifiable after one harsher dial: Will NOT carry as drafted — every court
  must reach 50. Holding out: Austria 5/50, Britain…".

### 3.3 Chunk 4's evidence arm (68 lines, 10 turns)

**56 identical, 12 reworded, refusals 13 → 13.** The evidence line's three
fights, and the petitions per turn:

- **A garrison, three times.** Ney storms Vienna's works on turn 5 (the
  assault's one-line muster: "Ney storms the works at Vienna alone: 19,164
  men, 22,809 in the assault's reckoning (+4% from the corps at his side),
  against a garrison of 25,000. Soult and Bernadotte do not join an assault
  on the works; the garrison breaks below 5,000."), Soult on turn 6, Soult and
  Bernadotte on turn 8 — Vienna falls on turn 8.
- **AAR24-X3 in live play.** Turn 8, "Bernadotte, attack Vienna": the
  before tree's cautious Bernadotte, 15,842 men against a garrison of 6,755,
  objected "The odds are not in our favor. Perhaps we should reconsider." —
  no figure, and the driver paid trust to insist past it; the after tree
  prices the assault by its own reckoning, raises no objection, and the
  assault takes Vienna.
- **A stacked defender — and a phantom in the band.** Turn 7, Mack and
  Archduke John at Carniola: "Ney, attack Archduke John" mustered
  "unfavorable" and cost Ney 3,209 for John's 1,073; "Murat, attack Mack"
  read, after the ruling, **"the balance of force looks even — a hard fight
  that may go against us"** ("even" on the before tree), with "Mack does not
  stand alone: at least 1 enemy corps within reach of Carniola would march to
  him" — and Murat broke Mack alone, 6,247 to 594. **A probe of the band at
  that moment (counting wrappers on `_defender_muster` and
  `_build_muster_preview`) named the corps it priced: Archduke John,
  co-located at Carniola with `retreat_recovery` 1** — and the resolver's
  casualty participants (`_get_casualty_participants`) drop a corps that is
  broken, retreated this turn or still recovering, while the muster's
  co-located arm returned "shares the field" before any of those checks. For
  Ney's strike the band had likewise priced Mack (recovery 2). The band, the
  "does not stand alone" row and, on our own side, the "stands on the field
  and will fight beside him" row and the shared-casualty note all counted a
  corps the resolver would not commit — **finding F3 (SRX-10), fixed by the
  residue.**
- **Rivals' battles.** Every French battle raises a rival's envy (the MC-3
  web): 13 French fires on the after tree (10 before — the boards drift
  after turn 6).
- **Petitions per turn:** before — modals on turns 1, 3, 4, 8, 9 (5); after —
  **audiences on turns 1, 3, 4, 7, 8, 9 (6) and one crisis modal on turn 10**
  (the Bernadotte–Ney breach). The crown: Ney on turn 1 for one point before;
  on turn 3 with 4 after.

### 3.4 What the arms could not reach

AAR4-X1 (the captor inherits nothing — every capture of Vienna in these arms
followed the garrison's collapse, which already cleared it), AAR24-X1 (no gun
corps stands before works in these arms), AAR24-X2 (no banked counter-punch
stormed works) and AAR10-X1 (no limbered battery was mustered) are read
through their own pins (`tests/test_sr4_quick_wins.py`) and, for AAR4-X1,
the reserve's four-arm series attribution (one 10,000-man garrison cleared on
the ambient board). The server consoles of all six runs are clean (0
tracebacks, 0 errors).

## 4. Findings

| # | Kind | Finding | Disposition |
|---|---|---|---|
| F1 | legibility | **A crisis card borrowed the routine tier's word.** AAR arm, turn 13: Lannes's grievance with Murat grown entrenched (escalation level 2 — the CRISIS tier) arrived as a modal titled "Marshal Lannes seeks an audience" — B1 made "an audience" the routine tier's word (the rail's "Hear him", the Generals chip, the badge), so the one modal the antechamber keeps for graver matters wore the routine title. | **Fixed by the residue (SRX-9)** |
| F2 | comment | The reserve's own comment at the muster band line still quoted the first cut's "most likely a fight that decides nothing" (the ruling measured "may well decide nothing"). | **Fixed by the residue** (comment only) |
| F3 | shown ≠ applied (P2) | **The muster counted a spent corps as sharing the field.** `_muster_reason`'s co-located arm returned "shares the field" for a corps the resolver's casualty participants exclude (broken, retreated this turn, recovering): the evidence arm's turn 7 priced a recovering Archduke John into "even — a hard fight that may go against us" before Murat broke Mack alone. It feeds the band on both sides of the muster, the "does not stand alone" and shared-casualty lines, and `muster_odds` — the glory gate on both boards. | **Fixed by the residue (SRX-10)** |

## 5. The residue slice

**One slice, two fixes and a comment, each behind its own lever** (rules
`SYSTEMS_REFERENCE.md` §73.7; pins `tests/test_sr_exit_residue_2026_09_27.py`
17; sweep `tools/_sweep_sr_exit_residue_2026_09_27.json` 6/6 killed, 0 INERT;
attribution `tools/_sr_exit_residue_2026_09_27_series_arms.py` + `.json`;
zero `.gd`):

- **SRX-9** — the §6 confrontation's title follows its tier through the tier
  table's own rule (`petition_tier_for`): an audience "seeks an audience", a
  crisis "demands to be heard". Display only; lever
  `jealousy.THE_CRISIS_IS_NOT_AN_AUDIENCE`.
- **SRX-10** — the muster's co-located arm reads the resolver's own
  exclusions: a corps broken, retreated this turn or recovering reads "is in
  no condition to fight" (`broken_recovering`), on both sides of the muster;
  a drift pin holds the arm's verdict equal to `_get_casualty_participants`
  flag by flag. Lever `combat_executor.A_SPENT_CORPS_DOES_NOT_SHARE_THE_FIELD`.
  **Balance, measured:** a two-arm flip — the lever changed 6 of 849 muster
  verdicts on the ambient board (the AI's field pricing reads the defender's
  muster) and the one glory-gate reading, neither moved a decision:
  `BASELINE_SERIES` byte-identical on both arms, the end-state provinces too;
  M1–M7 + the AI-V assurance byte-identical (81 passed).
- The stale comment at the band line.

The 125-file jealousy, petition and audience family green (6,100 passed) and
the 86-file muster, band and glory-gate family green (4,519 passed, the
standing xfail).

## 6. The gate this session stopped at

**Chunk 5's gate — SR-D1 "Reforms, not research" — is the user's ruling.**
Its questions (plan §4 SR-D1 Q1–Q4 and Q6; Q5 answered by SR-D3's ruling)
and SR-D3's two carried questions (Q3 DP, Q5 the admin pool) were put to the
user at this session's end with recommended defaults; nothing under §4 is
built until the ruling returns.
