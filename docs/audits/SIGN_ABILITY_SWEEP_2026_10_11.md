# The Sign-Ability Sweep — DD-1 S6, the first instrument (October 11, 2026)

*Pre-Deploy S6, `docs/PRE_DEPLOY_PLAN.md` §3.1 "The instrument" 1. Tool
`tools/sign_ability_sweep.py`; records `docs/audits/dd1/sign_ability_<ARM>.json`;
pin `tests/test_dd1_sign_ability_sweep.py`; rules `SYSTEMS_REFERENCE.md` §106.1;
rows `BUG_FIXES.md` §DD-1 S6 (DD1-1 … DD1-4). Nothing fixed — the slice measures.*

## What was measured

On every diplomacy arm the driver runs (`tools/score_run.py`'s own argv: FC, OP,
VOLTE, CONG, PRESS, REACH-AAR) and on three fresh seeds of the commanded
40-turn script (`dd1-one`, `dd1-two`, `dd1-three`; the four-turn `dd1-quick` is
the pin's live arm), every surface that shows an answerable letter, an enabled
chip, a priced Congress row, a counsel line or a settlement verdict was
dry-run through the REAL ratifier at the moment it was shown — the accept
road itself on a clone of the world (`WorldState.from_dict(world.to_dict())`,
the save road, 6 ms a clone), never a second implementation of its rules.

| surface | the moment | the promise | the oracle |
|---|---|---|---|
| letter | `DialogueManager.push` (arrived) and `_promote` / `activate_mailbox_item` (shown) | an accept-shaped option on the letter | `handle_diplomatic_dialogue_response(option)` on the clone, chased through the settlement confirm or the paradox alert it opens |
| chip | the top of `TurnManager.end_turn` (the board the player saw all turn) | a `propose_*` row with `available: True` | `_ratify_treaty` on the clone, France proposing |
| counsel | the same | a hint naming a treaty type | the same |
| congress | the same | a row with a `peace` lever | the same |
| settlement | the same | the preview's `carries`, and the confirm's own Ratify button | `propose_white_peace` + `confirm_settlement` on the clone |
| real | the live world | — | `_ratify_treaty` and `ratify_settlement_confirm` as the driver clicked |

Two counts: **A** "shown as signable, refused when signed" and **B** "refused
without naming the clause" — a refusal is *named* when its message matches
one of the ratifier's own shapes, the settlement display layer's words
(`SETTLEMENT_DISABLED_REASON_DISPLAY`), or the petition's own refusals; a raw
snake_case code in a player-facing message is *unnamed* by definition.

## The reading

```
arm              shown letters  real    A  A-dry  A-real    B  asked  err  A by surface
CONG                79      10     3    0      0       0    0      2    0  {}
FC                  39       9     2    0      0       0    0      0    0  {}
OP                 215      45    18    3      3       0    1      3    0  {'letter': 3}
PRESS               68      23     8    1      1       0    0      2    0  {'letter': 1}
REACH-AAR          500      65    21    3      3       0    1     17    0  {'letter': 3}
SEED-dd1-one       450      32    15    0      0       0    0      2    0  {}
SEED-dd1-three     520      30    11    0      0       0    0      2    0  {}
SEED-dd1-two       451      36    14    4      4       0    0      2    0  {'letter': 4}
SEED-quick          65      12     8    0      0       0    0      0    0  {}
VOLTE              443      28    14    0      0       0    0      2    0  {}
TOTAL                                  11                   2
```

- **2,830 promises read; 2,287 chips, 253 Congress rows and 0 counsel lines
  dry-signed — every chip, every Congress row and every counsel line the
  five polled surfaces showed, the ratifier would have signed.** The counsel
  (`_recommend_action`) never named a treaty type on these arms (its hints
  on a war arm are "Propose peace with X" only when the war score is past
  ±20, which the arms' wars never reached before the table settled them).
- **The settlement preview and its confirm agree** on all 148 rows: where the
  preview did not carry (`Settlement legitimacy`, `no_direct_war_score_for_
  covered_enemy`, the one-on-one war), the confirm offered no Ratify; where
  the arms' letters opened a confirm, it ratified (30 of 32 `asked` rows).
- **A = 11, every one a LETTER.** The table said yes and the treaty said no
  on exactly four shapes:
  1. **The ally petition cannot be granted from the letter** (OP t7, REACH-AAR
     t7 — Bavaria and Spain, `ally_settlement_petition`, option
     `grant_ally_petition_clause`): *"The settlement table for this war is not
     open in authoring, Sire. Open the settlement (Return to Terms if under
     review), then answer the petition. Opening the settlement for Austria now
     — the petition waits in the mailbox."* At the letter's second showing the
     grant opens the settlement editor in PROPOSE mode, whose own Ratify is
     withheld with the raw code `no_direct_war_score_for_covered_enemy`
     (`ratify_blocked_reason`, which `proposal_confirm_popup.gd:643` renders)
     — **the B count's two rows.** → DD1-1.
  2. **The client petition's Grant is enabled for a province already given**
     (PRESS t28, Holland, a `client_petition`): *"Brunswick was given elsewhere
     by our own hand — it cannot be ceded to Holland. The petition stands until
     the turn ends, and a lapse is a refusal."* The petition's `enabled` is
     re-derived on read (`mailbox_payloads.py`), yet the grant refuses. → DD1-2.
  3. **A settlement offer for a war France does not lead** (SEED-dd1-two t28,
     Austria, `incoming_settlement_offer`): *"Only the war leader can settle
     this side."* — SFR-B1 reproduced by the instrument, at arrival and when
     shown. → cross-referenced on SFR-B1.
  4. **A settlement offer for a one-on-one war** (SEED-dd1-two t33, Austria):
     *"Use bilateral peace or armistice for a one-on-one war."* — the emitter
     sent a whole-war letter the settlement road refuses by its own
     eligibility gate; SF-V5's dry run reads the per-court table, not the
     one-to-one gate. → DD1-3.
- **A-real = 0 and no real sign by the player was refused on any arm**: SF-V1 /
  SF-V5 withhold the bilateral letters the table refuses, so the driver's
  clicks never met the ratifier's no. The eleven are letters the SF-V1 guard
  does not govern (petitions, settlement offers).
- **One more found in passing** (not an A row — the surface promised nothing):
  a white peace proposed WITH a `war_id` on a war that has become one-on-one
  refuses with *"This war changed while the review was open"* on a fresh
  propose (`settlement_helpers.resolve_or_backfill_war_instance_for_settlement`
  :1978-1982 returns `war_state_changed_since_open` for a requested war whose
  pair sides no longer match) — the clause is the wrong one; the preview
  beside it says `one_to_one_war`. → DD1-4.

## The done-when

§3.1: *the sign-ability sweep reads 0 on every committed arm and three fresh
seeds.* **NOT met: A = 11, B = 2.** The pin asserts it NOT met so it is
re-seated on purpose when Step 2's `can_sign` verdict lands; the committed
counts are lower-only per arm.

## How to re-read

```
.venv/Scripts/python.exe tools/sign_ability_sweep.py                 # every arm + the seeds (about a minute, 5 in parallel)
.venv/Scripts/python.exe tools/sign_ability_sweep.py --summarize     # the table from the records
.venv/Scripts/python.exe tools/sign_ability_sweep.py --quick         # the pin's live set
```

## The re-read — DD-1 S7 Slice B, `can_sign` (October 11, 2026)

*The ONE verdict (`treaty.can_sign`, `SYSTEMS_REFERENCE.md` §108) read by
every surface and the ratifier; the instrument re-run as it stands — not a
regex, not a surface read, not a moment changed. Landing record
`PRE_DEPLOY_PLAN.md` §3.1 "DD-1 S7 landing record, Slice B".*

```
arm              shown letters  real    A  A-dry  A-real    B  asked  err  A by surface
CONG                79      10     3    0      0       0    0      2    0  {}
FC                  39       9     2    0      0       0    0      0    0  {}
OP                 215      45    18    0      0       0    0      2    0  {}
PRESS               67      22     8    0      0       0    0      2    0  {}
REACH-AAR          497      65    21    0      0       0    0     16    0  {}
SEED-dd1-one       450      32    15    0      0       0    0      2    0  {}
SEED-dd1-three     520      30    11    0      0       0    0      2    0  {}
SEED-dd1-two       447      32    14    0      0       0    0      2    0  {}
SEED-quick          65      12     8    0      0       0    0      0    0  {}
VOLTE              443      28    14    0      0       0    0      2    0  {}
TOTAL                                   0                   0
```

- **A 11 → 0, B 2 → 0; 2,822 promises** (2,830 at the first reading — the
  eight fewer are the promises the surfaces no longer make: the ally
  petition's Grant at arrival behind a mounted editor, the client petition
  that is no longer issued for a province a sibling already named).
- **How each of the four shapes went.** (1) The ally petition (OP / REACH-AAR
  t7): at ARRIVAL the editor is the current hard stop and the instrument's
  dry run displaces it into the queue — a state the player cannot reach (the
  identity binding and the letter-book both refuse a queued petition while
  a hard stop is mounted); the verdict reads a MOUNTED editor as "back out
  first — the draft is kept" and the Grant arrives disabled with that reason,
  re-stamped at every read seam once the draft is suspended. At the second
  showing the grant's editor withheld Ratify with a hard stop whose `reason`
  key the confirm builder never read — it reads it through the display map
  now (B 2 → 0), and the arrival stamp means the instrument no longer
  dry-signs that letter at its showing. (2) The client petition (PRESS t28):
  TWO petitions for Brunswick — Hesse's by the Congress's summons, Holland's
  by the end turn; `petition_subject` skips a province a sibling's standing
  petition names. (3) SFR-B1 and (4) DD1-3 (SEED-dd1-two t28 / t33): the
  emitter reads the settlement road's eligibility gate before the carry; the
  letters are no longer sent, no cooldown spent.
- **The done-when of §3.1 — MET.** `tests/test_dd1_sign_ability_sweep.py`
  re-seated: the caps zero per arm, `(0, 0)` asserted, the four S6 clauses
  asserted gone from the refused letters, the live quick set matched to its
  re-recorded record.
