# IQ-3 "The Coalition Is Rare" — measurement memo of record (September 14, 2026)

Row IQ-3 of the improvement queue (PR-D1). Landing record =
`docs/IMPROVEMENT_QUEUE_SPEC.md` §1.2; this memo carries the measurements
behind it.

## 1. The disease, measured

A read-only decision fleet (three measurers, a seam census, three designers
and a judge, against snapshot `32e87754`) drove the COMMANDED arm
(`tools/playtest_scripts/commanded_full40.json --diplomacy accept`) and the
ambient arm on the seeds `historical`, `austerlitz` and `ulm`.

- **Commanded: six to eight coalitions in forty turns.** On historical the
  ordinal reached **"The Tenth Austrian Coalition"**.
- **Every dissolution was `insufficient_members`**, reached through the
  `set_diplomatic_state` treaty-ejection arm when France ratified the
  coalition's own settlement offer. None came from the low-threat tick.
- **The alarm never fell.** A peace that breaks a league changed no threat.
  At the formation tick France's alarm sat at 90–94 on historical and
  austerlitz, and the per-turn contributors (`hegemony_passive +1`,
  `agenda_grudge +2`, created by the peace itself, and `decay −3`) summed to 0.
- **The ≥90 override cancelled the 5-turn cooldown**, so something formed on
  the next tick. The majors were exempt under the PR-1 fresh-peace floor, so
  the minor courts (Hanover, Naples, Ottoman, Sardinia, Sweden) formed the next
  league. Two turns later that war was old enough for a settlement offer, the
  player accepted, and the majors' floor lapsed on exactly that tick.
- **The result was a major/minor alternation every four turns.** Every member's
  war exhaustion was 0 at every formation (17 of 17): `cleanup_war_end` (R49)
  pops it at every peace.
- **Ambient: one coalition in forty turns.** The passive France signs no
  peace, so the boot league stands until France collapses and it dissolves
  on low threat.

## 2. The rule

**"The League Is Spent"**: a TREATY that dissolves the league spends Europe's
alarm against its target. The target's `threat_by_target` slot is divided by
`LEAGUE_SPENT_DIVISOR = 2` through `reduce_threat`, as source `league_spent`.
The treaty's own annexation, vassalization and forced-alliance alarm this turn
is kept whole. The next coalition must be earned by a new act of the target's
that carries the alarm back to the 60 gate.

- **It is not a cooldown.** There is no timer, and the window lasts exactly as
  long as the target's own conduct keeps the alarm below 60. The formation turns
  in §3 differ by seed and by conduct.
- **It is derived.** It reads and writes only the existing slot. There are zero
  new serialized fields.
- **Rejected designs.** A 20-turn league memory measured 2/2/2, but formed on
  **turn 27 on all three seeds**, whatever the alarm: it was a cooldown with a
  memory label. Gating the AI's settlement offer made coalitions longer, not
  rarer; it moves to its own companion row, `DESIGN_REFINEMENT.md` PR-D1b.

## 3. The completion board — measured on the build

Setup: the rule as committed at `0dce5cfb` (run in-process on a `git archive`
of that exact tree, so a review fleet could read it concurrently),
`PYTHONHASHSEED=0`. Coalitions counted from the live `log_event` stream (the
boot Third plus every `coalition_declared`), never from the 500-row-capped
`event_log`.

| arm | historical | austerlitz | ulm | expected |
|---|---|---|---|---|
| A — ambient (France never signs) | **1** | **1** | **1** | 1 |
| B — commanded, accepts every peace | **1** | **1** | **1** | 1 |
| **C — B + `--declare-war proceed` (the completion board)** | **2** | **1** | **2** | 1–3, centre 2 |
| D — C + declarations at loops 10 / 20 / 30 | **3** | **2** | **2** | ≤ 3 |
| E — C with both IQ-3 levers DOWN (attribution) | **8** | **4** | **5** | the disease |

**The spends.**
- On arm B every seed spent at turn 4: 90 → 45 on historical, 91 → 45 on
  austerlitz and 83 → 41 on ulm.
- On arms C and D every later spend halved again, for example
  96 → 48, 80 → 40 and 74 → 37.

**Every coalition formed after a spend traces to a French declaration** that
broke a Peace Treaty:
- C historical: declared t5 → brewed after the cooldown → formed t12.
- C ulm: declared t4, t7 and t11 → formed t12.
- D: the formations follow the scripted declarations.

**Austerlitz on C is 1, not 2.** France declared once, at t5, against a spent
alarm of 45, carrying it to 65. The dissolution at t4 had started the existing
5-turn cooldown. By the time the cooldown lapsed the alarm had decayed below
60, so no league gathered, and on that seed France declared no second war.
Inside the band, and the rule working as stated.

**France's provinces at turn 40.**

| arm | historical | austerlitz | ulm |
|---|---|---|---|
| B | 29 | 29 | 29 |
| C, levers up | 29 | 27 | 27 |
| E, levers down | 27 | 7 | 19 |

A commanded France under the rule never approaches the FA-D27 re-open line.

## 4. Two defects found on the way

- **`--declare-war` was dead in the driver.** FA-S17-D6 added the flag and the
  `declare_war` policy key, but not the policy override loop, so the flag was
  parsed and dropped. Every run that passed `--declare-war proceed` ran
  `cancel`, and its `meta.json` said so. Runs that left the flag alone measured
  what they claimed, because the default was cancel. Fixed: `resolve_policy`
  now carries every dial, pinned.
- **Talleyrand fell silent at the wrong moment.** His declare-war objection read
  only `threat > 50`. After a spend (alarm 41–48) he said nothing, exactly when
  one declaration would bring on the next league. He now reads the projection,
  the figure `declare_war` itself applies (`diplomacy.declaration_alarm`). The
  live run shows it firing at t5 on austerlitz: *"Europe's alarm stands at 45 …
  A declaration on Austria would carry it to 65, past the 60 at which a
  coalition gathers …"*.

## 5. What this does not do

- It does not touch win or defeat (`sandbox_mode` stands).
- It does not touch the 60 / 80 / 90 tiers or the ≥90 override.
- It does not touch war exhaustion or R49.
- It does not touch `COALITION_COOLDOWN_TURNS` or `FRESH_PEACE_FLOOR_TURNS`.
- It does not gate the AI settlement offer.
- The low-threat tick, the greater-danger pivot, elimination, a truce and a
  separate peace that leaves two members standing never spend.
- A peaceful France's thirty-six quiet turns on arm B are the stated
  expectation, not a defect. The balance consequence belongs to the FA-D27
  owner.

## 6. The review round

Four read-only lenses (does the spend fire exactly when it should · shown
equals applied · exploit and knock-on · do the pins bind) read a `git archive`
of the build, with one adversarial refuter per finding. There were 13
findings; the top ten went to refuters and the three P4s cut by the cap were
built anyway.

| # | finding | verdict | disposition |
|---|---|---|---|
| 1 | Breaking a truce (`break_treaty`: ARMISTICE → PEACE) dissolved a two-court league and halved the alarm, 85 → 42 | **P1, CONFIRMED** | fixed: `UNILATERAL_PEACE_REASONS` |
| 0 | A treaty that annexed one court of a two-court league whole dissolved it unspent; at 90+ the override re-formed a league next tick | P1 → P2 | fixed: `_eliminate_nation(by_treaty=)` from the three treaty sites |
| 4 | A vassalization clipped at 100 made the spend depend on pair order (62 against 70) | **CONFIRMED**, P2-grade beside an annex | fixed: `applied` stamp + pre-treaty formula |
| 2, 8 | Talleyrand counted courts before his master's own −15 (named 8; the league had 13) | P2 → P3 | fixed: `relation_shift`, single-sourced penalties |
| 5 | He objected while a league already brewed | P3 | fixed |
| 6 | "The last league was spent" claimed without measuring it (raw-tag half REFUTED — the client humanizes) | P3 | fixed |
| 7 | The spend arm hid a court genuinely still at war | P3 | fixed: `treaty_in_flight` |
| 9 + 3 capped | The confirmed-objection guard, the casus belli, sentence arms, `< 60` gates, arithmetic guards unpinned | **P4, CONFIRMED** | pinned |
| 3 | Declarations stacked on outside courts before signing are halved too | design gap | routed: `DESIGN_REFINEMENT.md` PR-D1c |

Every review fix is behind the two IQ-3 levers or is a pure correction of the
rule's own reach. The mechanics of arms A–E in §3 are unchanged by it: the
fixes touch eliminations by treaty, truce breaks, cap clips and copy, none of
which the arms exercised.
