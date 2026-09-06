"""AI-4a steps 1-4 — the threat_by_target additive migration (Stage C).

docs/AI_INTENT_SPEC.md §4.4a: the migration is ADDITIVE, not a rewrite.

  1. `world.threat_by_target: dict[str, int]`; `add_threat`/`reduce_threat`
     gain an optional `target` defaulting to the player. Every existing
     call site keeps its exact behaviour.
  2. `threat_level` is a PROPERTY over the player's slot (the `gold`
     property idiom) — all 73 backend reads and 10 .gd reads unchanged.
  3. `threat_sources_this_turn` entries gain a `target` key; legacy
     entries without one default to the player on read. `from_dict`
     seeds the dict from a legacy scalar; `to_dict` writes both.
  4. THE PIN: a boot world + 40-turn run produce a byte-identical
     `threat_level` series before and after the migration, at fixed
     ambient RNG (per-turn `random.seed(10_000 + turn)`, the M7 idiom),
     `SOVEREIGN_SEED=historical` and `PYTHONHASHSEED=0` (set iteration
     order feeds AI decisions — without the hash pin the ambient sim is
     process-unstable, which is pin 14(c)'s "no campaign replay" clause
     observed in the wild).

Steps 5-6 (producer migration + decay re-key) are Stage D. Until they
land, NO production caller passes a non-player target, and every
non-player slot is structurally 0 — asserted here.

The recorded series below was measured on master @ d1be956 BEFORE the
migration was applied, then re-measured after: byte-identical. Any later
slice that legitimately changes AI-diplomacy behaviour (the Stage C rung
rework does) re-records the constant CONSCIOUSLY with a note beside it.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic.coalition import add_threat, reduce_threat
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")

# Measured on master @ d1be956 (pre-migration), re-measured identical
# post-migration (steps 1-4) — the §4.4a step-4 gate held: the
# migration alone changed NOTHING. Byte-identical baseline of record:
# [85, 86, 84, 82, 80, 77, 74, 71, 68, 65, 62, 59, 46, 43, 40, 45, 42,
#  39, 36, 41, 38, 35, 32, 40, 37, 34, 31, 37, 45, 42, 42, 42, 45, 45,
#  42, 42, 45, 45, 42, 42, 45]
# RE-RECORDED CONSCIOUSLY at the Stage C rung rework (the intent-driven
# rungs legitimately change what the courts do each turn):
# [85, 86, 84, 82, 80, 77, 74, 71, 68, 65, 62, 59, 46, 43, 40, 48, 53,
#  50, 47, 52, 49, 46, 43, 43, 40, 37, 34, 39, 36, 33, 33, 30, 27, 27,
#  27, 24, 24, 21, 21, 21, 18]
# Stage D verified that series BYTE-IDENTICAL twice (AI-4a steps 5-6 in
# isolation AND with the AI-4c tick live — spec §17). Then RE-RECORDED
# CONSCIOUSLY ONCE at the Stage D review round: the [r5 HIGH] exhausted-
# pair exit lets the boot minors' side-wars (Spain|Britain et al.) end by
# mutual exhaustion mid-run (~turn 17), which moves the minors' economies
# and the courts' behaviour downstream — identical through turn 17, +3
# offset after. The pin's job from here is to catch UNINTENDED drift.
#
# RE-RECORDED CONSCIOUSLY ONCE at IGR-X4 (July 31, 2026): the estate
# confiscation windfall was structurally 0 gold (it read effective income
# after stage 1 left stability <= 25); re-based on income_value it pays for
# real. The ambient run has FOUR live AI-vs-AI confiscations by turn 9
# (Britain reclaiming its own soil strips Castanos's estates for 184/245/
# 280g; Spain strips Moore's Flanders estate for 400g), so Britain's purse
# genuinely changes and the trajectory diverges from turn 15 on — identical
# through index 14. Attribution was BISECTED to the one-line windfall
# re-base (comment-only and function-only probes both left the series
# byte-identical; the live call swap alone flips it), and the confiscations
# were counted by a live spy because the 500-cap event log had EVICTED all
# four rows by turn 40 — the same trap IGR-B's landing record documents.
#
# RE-RECORDED CONSCIOUSLY ONCE at PT-F1 (August 1, 2026): the pursuit-
# capture guard (BUG_FIXES.md §Live-Playthrough) — a battle-advance may
# only transfer soil of a court the victor is AT WAR with. A live spy on
# the guard (the IGR-X4 idiom: the 500-cap log would have evicted the
# rows) found the OLD baseline world contained exactly two silent
# third-party annexations, both now blocked:
#   turn 5 — Austria's Mack pursued into BERLIN, Prussia's CAPITAL, a
#            court Austria was at PEACE with (the old run flipped it);
#   turn 6 — Britain's Moore pursued into Brunswick, HANOVER's soil (a
#            court in personal union with Britain, historically).
# Prussia keeping its capital is a structurally different (and finally
# sensible) Europe, so the series diverges from index 5 on — identical
# through index 4. The square-thrash latch (PT-F6) that landed the same
# session was measured in isolation FIRST: byte-identical, 72/72 — this
# re-record is attributed to the pursuit guard alone. The pin's job from
# here stays the same: catch UNINTENDED drift.
# Prior series (PT-F1, August 1, 2026):
#   [85, 86, 84, 82, 80, 78, 76, 74, 71, 68, 65, 70, 75, 72, 69, 59, 56,
#    53, 53, 50, 50, 47, 47, 44, 41, 38, 38, 35, 32, 29, 32, 35, 35, 32,
#    32, 32, 29, 26, 23, 20, 20]
#
# RE-RECORDED CONSCIOUSLY ONCE at DEF-5 NAVAL NV-0..NV-3 (August 2, 2026):
# the Wooden Wall goes live on the shipped scenario — Britain's boot
# blockade (France/Spain/Holland readiness rot + trade halved), the
# Admiralty upkeep, the CS closure squeeze on Britain's trade_dominance,
# and above all the §4.1 CROSSING GATE. Divergence index 5 IS the
# attribution: turn 5 was where the old ambient run walked an army over
# the London–Flanders link (the "Spain besieges London" believability
# defect this phase exists to kill — AI_V_SWEEP §10.5 rank 2); with the
# Royal Navy commanding the Channel that history is structurally
# impossible, and the whole tail re-derives lower (a Europe where the
# island is safe accrues less anti-France alarm). One re-record, one
# cause, spec-predicted (NAVAL_SPEC §7 boot deltas + §11 NV-0).
# Prior series (DEF-5 naval NV-0..NV-3, earlier the same day):
#   [85, 86, 84, 82, 80, 77, 74, 71, 68, 65, 70, 67, 64, 69, 66, 53, 50,
#    55, 52, 49, 46, 51, 48, 45, 42, 42, 39, 36, 33, 33, 30, 27, 24, 24,
#    21, 18, 18, 15, 12, 12, 9]
#
# RE-RECORDED CONSCIOUSLY ONCE at THE NORMAN BEACH (August 2, 2026,
# user-directed: "make it so British land in Normandy if they do land, not
# in the middle of the country"). The registry gained the short
# London↔Normandy sea link (111px — the historic descent coast) beside the
# long London↔Flanders hop (352px, one of the map's longest, whose
# Flanders↔Orleanais edge fed a landing straight into central France).
# Sea links are ALSO walkable adjacency (the DEF-7 contract), so continental
# pathfinding legitimately changed: measured, Britain now comes ashore at
# NORMANDY on turn 1 — fighting through its 12,000-man Channel depot in two
# garrison assaults (the DEF-6 rule, never a walk-in) instead of rolling
# through Flanders into Amsterdam. Divergence index 9 is that campaign
# re-shaping: a Britain contesting the Norman coast in front of Paris keeps
# French alarm HIGHER through the midgame (the tail runs ~8 above the
# previous record) rather than drifting off into the Low Countries. One
# re-record, one cause; M1–M7 stayed byte-identical throughout.
#
# RE-RECORDED CONSCIOUSLY ONCE at NV-4 THE HOST RULE (August 2, 2026,
# user-gated: "how do we abstract them entering on Portugal IRL?").
# An opposed landing stopped being an ordinary march: a sea link may no
# longer be walked INTO a province held by a court the mover is at war
# with while any hostile fleet still covers that water. Britain therefore
# no longer takes Normandy on turn 1 — DIVERGENCE INDEX 1 IS THAT TURN,
# and the attribution was verified by experiment, not by argument: with
# HOST_RULE_ACTIVE flipped to False and every other NV-4/NV-5 change left
# in place, this series reproduces the prior record BYTE-IDENTICALLY. So
# the AI expedition rung, the establishment build ceiling and the two
# repaired candidate filters are all threat-neutral, and this re-record
# has exactly one cause.
#
# The tail runs lower and reaches 0 because the ambient France (unplayed)
# now conquers nothing AND is invaded by nobody: Britain's army sails for
# Lisbon on turn 11 and fights its way up through Spain instead, so
# Europe's alarm at France decays undisturbed. That is the honest reading
# of a quiet France, and it is the shape the AI-3r probe already recorded
# for ambient runs (§8.2: the warlike 1805 designs all target the player).
# Prior series (THE NORMAN BEACH, earlier the same day):
#   [85, 86, 84, 82, 80, 77, 74, 71, 68, 73, 81, 78, 75, 80, 77, 74, 61,
#    66, 63, 60, 57, 62, 59, 56, 53, 53, 50, 47, 44, 44, 41, 38, 35, 35,
#    32, 29, 26, 26, 23, 20, 17]
#
# RE-RECORDED CONSCIOUSLY ONCE at NV-8c (August 2, 2026, user-directed:
# "looks like there is still a line connecting england to flanders").
# The long London↔Flanders sea link (352px) is CUT from the registry —
# sea_links 19 → 18 and both adjacency folds — leaving London↔Normandy
# as the ONE Channel crossing, which is what the Norman-beach re-stage
# had always meant. Divergence index 12 is pathfinding: continental
# distances that used to route through the Flanders hop lengthen by a
# turn or two, so the same events land a beat later and the tail
# stretches accordingly (the shape is the prior series time-shifted,
# which is exactly what a removed edge does). Deterministic across two
# processes; single registry-data cause, self-evident from the diff —
# the Norman-beach precedent.
# Prior series (the NV-4 host-rule record, earlier the same day):
#   [85, 83, 81, 79, 77, 75, 73, 71, 69, 66, 66, 63, 60, 57, 57, 44, 41,
#    38, 38, 35, 32, 29, 29, 26, 23, 20, 17, 14, 14, 11, 8, 5, 2, 2, 0,
#    0, 0, 0, 0, 0, 0]
#
# RE-RECORDED CONSCIOUSLY ONCE at CA8-20 (August 4, 2026, creative-audit
# sweep 4). The AI's estate grant rung stopped alienating provinces worth
# nothing. `list_eligible_estates` sorts on `get_effective_income()`, which
# is 0 at stability <= 25, and BOTH capture branches land inside that tier
# (`_apply_secure` sets 25, `apply_plunder_effects` sets 10) — so on fresh
# conquest every candidate is 0 and no ordering of [0,0,0,0] picks a payer.
# Because arm 1 returns unconditionally on a NON-EMPTY list, the rente arm
# below it was unreachable while any worthless province remained. Measured on
# this very run: 6 of 9 grants closed 0g of the marshal's gap, and Austria
# ended 1,761g/turn in household bills with ArchdukeJohn endowed to 1,137g
# against a 300 expectation cap. The rung now filters on
# `dotation.list_paying_estates` (income AND the EC-W1 disruption term, which
# `list_eligible_estates` never had).
#
# THIS IS A RESHAPED TAIL, NOT A TIME SHIFT. Divergence at index 12
# (63 -> 79); anti-France alarm now ends at 36 rather than 0. The cause is
# Austria's economy, not the threat machinery: unpatched she ends
# dotation_skim 1,761 / treasury 1,334, patched 1,037 / 10,485, so she levies
# on 12 turns rather than 13, and in 15 levies rather than 23. Britain
# commissions Wellesley instead of Shrapnel.
#
# CORRECTED Aug 4, 2026 by this slice's own review, and the correction is
# worth keeping visible. This paragraph first read "recruits on 13 turns
# instead of 22 and stays a live belligerent to the end of the window". BOTH
# halves were wrong. 13 and 22 are two different metrics of the SAME
# (unpatched) arm — executor dispatches vs Austria-attributed recruit rows in
# a 500-capped `event_log` — so the sentence compared an arm with itself; the
# patched figures are 12 and 15. And Austria is at WAR with France on all 40
# turns in BOTH arms, ending LARGER unpatched (21 provinces / 125,395 men vs
# 19 / 87,640), so "stays a live belligerent" named no difference the filter
# made and was inverted on the quantitative readings. The tail is reshaped by
# the fighting, not by Austria leaving the war.
#
# ATTRIBUTION VERIFIED BY EXPERIMENT, not by argument (the NV-4 idiom):
# with the filter clause alone disabled — `list_paying_estates` returning
# `list_eligible_estates` verbatim — the prior series below reproduces
# BYTE-FOR-BYTE. Single cause.
#
# Prior series (the CA8-20 record, i.e. everything above this block):
#   [85, 83, 81, 79, 77, 75, 73, 71, 69, 66, 66, 63, 63, 60, 60, 57, 44,
#    41, 41, 38, 35, 32, 32, 29, 26, 23, 20, 17, 17, 14, 11, 8, 5, 5, 2,
#    0, 0, 0, 0, 0, 0]
#
# RE-RECORDED CONSCIOUSLY ONCE at the ECON BALANCE gate (August 7, 2026 —
# docs/audits/ECON_BALANCE_GATE_2026_08_07.md, pre-authorized §6). THREE
# named causes, separated by a two-arm flip experiment (the NV-4 idiom):
#   (1) the authored boot threat 85 → 70 (EB-4.1, headroom) — index 0 by
#       definition, and the whole series re-levels under it;
#   (2) the DEFENSIVE-win battle_win exemption (EB-4.3) — Arm B (boot
#       restored to 85, all else live) still lost the prior record's
#       sporadic +3s from index 5 on: the old bar was re-pinned by France
#       WINNING DEFENSIVE battles, which no longer alarms Europe;
#   (3) the econ components (EB-1 charges / EB-2 overseas + subsidy tier
#       4 / EB-5a requisitions) — Arm C (boot AND defender credit both
#       restored, econ live) STILL diverges one point at index 5 and
#       butterflies thereafter: Britain's deepened purse (+307/turn)
#       crosses the subsidy tiers turns earlier and Austria requisitions
#       +37/turn from Swabia, so the courts genuinely fight and spend on
#       a different schedule. Causes (1)+(2)+(3) are jointly the record;
#       the pin's job from here stays catching UNINTENDED drift.
# The tail reaches 0 and STAYS there: with defensive wins no longer
# feeding the alarm, an unplayed France that conquers nothing decays to
# the honest floor — exactly the quiet-France reading EB-4 exists to
# make possible (the old bar could never fall while France defended
# itself competently).
# Prior series (the IGR-X4 record, i.e. everything above this block):
#   [85, 83, 81, 79, 77, 75, 73, 71, 69, 66, 66, 63, 79, 76, 84, 81, 86,
#    83, 70, 73, 78, 75, 72, 69, 69, 66, 63, 60, 60, 57, 54, 51, 54, 51,
#    48, 45, 45, 42, 39, 36, 36]
# RE-RECORDED CONSCIOUSLY ONCE for CA9-F9 (August 8, 2026), single cause,
# ATTRIBUTION VERIFIED BY A FOUR-ARM EXPERIMENT (the NV-4 idiom):
#
# The war score's contested-capital arm counted ANY marshal of the enemy
# nation standing in the capital province — and a CAPTURED marshal is held
# at his captor's capital at strength 0. So taking the enemy commander
# prisoner and holding him in Paris scored "Austria contests the French
# capital" and SUBTRACTED 10 from France's own war score. Both sibling
# readers of that pattern already carried the `strength > 0` guard.
#
# The experiment ran four arms of `_besieges`: control (neither clause),
# `captured_by` alone, `strength > 0` alone, and both as landed. All THREE
# fix arms produce the IDENTICAL series — which is itself the finding: on
# this board the two clauses catch exactly the same marshals, because a
# prisoner is precisely the strength-0 case. Single cause, no interaction.
#
# Divergence at index 11 (41 -> 46) and the tail runs four turns longer
# before reaching the floor: France's score is no longer docked for its own
# prisoners, so Europe stays alarmed about it for longer. The direction is
# what the fix predicts.
#
# RE-RECORDED CONSCIOUSLY A SECOND TIME the same day for CA9-N6, single
# cause, ATTRIBUTION VERIFIED BY A SIX-ARM EXPERIMENT (the NV-4 idiom):
#
# Both AI attack rungs summed the acting nation's WHOLE army and divided
# it by ONE enemy marshal — P4 by the named target, P0 by the WEAKEST
# corps present. Three enemy corps in a province therefore read as a
# walkover and the AI charged into the other two: twelve failed assaults
# over the played campaign for a 4.7:1 exchange against itself, which is
# why Europe read as busy rather than dangerous. It is the same
# defender-invisibility defect CA9-F1 fixed on the player's side.
#
# Arms: control (all three edits reverted) · N6-P0 alone · N6-P4 alone ·
# N7 alone · both N6 rungs · everything as landed. Result:
#   - N6-P0 alone   -> IDENTICAL to control. The P0 rung fires only when
#                      already engaged in the same province, a shape the
#                      ambient board does not produce differently.
#   - N7 alone      -> IDENTICAL to control. No marshal reaches three
#                      failed assaults on one target in 40 quiet turns.
#   - N6-P4 alone   -> the whole move, and `both N6 rungs` and `all` are
#                      BYTE-IDENTICAL to it. Single cause, no interaction.
#
# Divergence at index 4 (62 -> 72) and the tail no longer reaches the
# floor: an AI that refuses the assaults it would lose keeps its armies,
# and Europe's alarm decays far more slowly. Counter-check that the fix
# is not simply passivity: 13 battles still fought in the first 20
# ambient turns, 24 marshals still standing. M1-M7 byte-identical.
#
# Prior series (the CA9-F9 record, i.e. everything above this block):
#   [70, 68, 66, 64, 62, 59, 56, 53, 50, 47, 44, 46, 48, 45, 47, 44, 31,
#    28, 30, 27, 24, 21, 18, 15, 12, 14, 11, 8, 10, 7, 4, 1, 0, 0, 0, 0,
#    0, 0, 0, 0, 0]
#
# ── RE-RECORDED August 9, 2026 — CA9 row 3, A12 ────────────────────────
# "De-duplicate the briefing". A pair that cooled in step 1 of the
# jealousy pass could be handed straight back to the SAME marshal by
# step 3 of the same pass, because `clear_jealousy` writes no
# "cooled this turn" marker and rival memory returns the man he just
# stopped resenting. Measured on the ambient board: 26 same-pair
# cool-then-refire events across 20 of 40 turns, and one briefing page
# carrying "his resentment has cooled" above "he resents him, for the
# fourth time".
#
# ATTRIBUTION — 5-arm flip experiment, each arm a single reverted edit:
#   control (all three reverted)  -> reproduces the PRIOR series above,
#                                    byte-for-byte. (i)
#   (a) same-pass suppression     -> reproduces `all` byte-for-byte, and
#                                    diverges from control at INDEX 15.
#                                    SOLE CAUSE. (ii)
#   (b) the level-1 escalation
#       line no longer co-emits
#       with its own fire         -> BYTE-IDENTICAL to control. (iii)
#   (c) the rung-3.5 ranking      -> BYTE-IDENTICAL to control. (iii)
#       (consistent with the measurement that `build_morning_dispatch`
#        is called ZERO times in an ambient run — the dispatch is a
#        player surface and this runner never builds one.)
#
# WHY IT MOVES: `jealous_of` is read at the combat coordination
# chokepoint on BOTH boards, so suppressing the re-fires changes who
# holds a grievance and therefore how AI-vs-AI battles resolve. Measured
# on the same trace: player fires 41 -> 21, ENEMY fires 15 -> 2,
# escalations 39 -> 17. Downstream the run diverges visibly — Austria's
# and Russia's recruitment cadences shift later and lengthen, Russia
# commissions an extra marshal on turn 31, the Swiss vassal rebellion
# opens on turn 27 instead of 29, Holland ends at loyalty 100 instead of
# 80, and Russia promotes one more emergent design.
#
# THE TAIL REACHING 0 IS NOT A NEW MECHANIC. Both arms decay at the same
# -3/turn; the new curve simply starts its decay from a lower peak (index
# 24: 45 vs 71) and so reaches the floor inside the 40-turn window. The
# prior record ended at 13 mid-decay.
# ── RE-RECORDED AGAIN, same day — CA9 row 3, Q3(b) ─────────────────────
# "A first grievance gets a first act". `_check_escalation` qualified on
# `stored_rel <= -1 or fires >= 3`, and 14 of the 18 authored negative
# French edges sit at Rival, so the player's FIRST card on nearly every
# quarrel opened at escalation 1 — "this is no longer a passing mood" —
# about a resentment one turn old. A stored HOSTILE pair still escalates
# on sight; a stored RIVAL pair now needs the quarrel to RECUR.
#
# ATTRIBUTION — 3-arm flip experiment:
#   control (predicate reverted) -> reproduces the A12 series above,
#                                   byte-for-byte;
#   landed                       -> diverges from control at INDEX 12;
#   hostile_only (a sensitivity
#     arm: drop the Rival clause
#     entirely)                  -> a THIRD distinct series, also from
#                                   index 12 — measured so a cheaper
#                                   fallback exists if this proves too
#                                   large in play.
#
# Measured on the ambient board: escalations landing on a pair's FIRST
# fire 6 -> 1 (the remaining one is a stored-Hostile pair, which is the
# intended exemption). Player fires rise 21 -> 28 and enemy fires 2 -> 12,
# because delaying escalation ALSO delays the tier-2 `modify_relationship`
# that pushes a pair to Hostile, where the idle requirement damps it —
# so pairs linger at hair-trigger Rival instead. That is a real
# consequence of the ruling, not a side effect of the implementation.
#
# ⚠ CUMULATIVE, AND WORTH A PLAYED CHECK: across A12 and Q3(b) the tail
# now reaches 0 at index 34, where the pre-row-3 record ended at 13. This
# is a PASSIVE France doing nothing for 40 turns, so a decay to zero is
# defensible on its face — but "Europe's alarm flattens" is exactly the
# direction the Q5(c) refuter warned about, and the harness cannot see an
# ACTIVE France. The playtest owns that question.
# ── RE-RECORDED August 14, 2026 — HC-4 "The Lifeline and the Bill", the
# ONE re-record the health-check gate sanctions (gate record
# `docs/audits/HEALTH_CHECK_DESIGN_GATE_2026_08_14.md` §5). Prior series:
#   [70, 68, 66, 64, 72, 70, 68, 66, 64, 62, 60, 58, 59, 57, 55, 53, 51,
#    48, 49, 47, 45, 46, 44, 42, 29, 26, 23, 20, 17, 14, 11, 8, 5, 2, 0,
#    0, 0, 0, 0, 0, 0]
#
# ATTRIBUTION — 4-arm flip experiment (the two levers:
# `naval.SHORE_SUPPLY_ACTIVE`, `enemy_ai.AI_NAVAL_AP_PARITY`):
#   control (both False)    -> reproduces the prior series BYTE-FOR-BYTE
#                              (and thereby proves HC-0 calendar, HC-1
#                              blockade accrual, HC-2 narration and HC-3
#                              flavor move nothing — they were all in the
#                              tree for the control run);
#   lifeline only           -> BYTE-IDENTICAL to control (the ambient
#                              board's coastal armies never meet a
#                              one-sided shore inside 40 turns);
#   AP parity only          -> reproduces THIS series byte-for-byte,
#                              diverging at INDEX 12 (59 -> 56) —
#                              THE SOLE CAUSE;
#   both                    -> identical to parity-only.
#
# WHY it moves: Britain's descent now consumes her whole 2-AP admin
# phase (table price 2, was flat 1). MEASURED (30-turn cadence probe,
# both arms): the DESCENTS THEMSELVES are byte-identical — Britain
# lands at turn 12 (Corsica) and 16 (Flanders) under either billing —
# so the NV-5 shape SURVIVES exactly ("Britain still lands"; not even
# later). What changes is what Britain does BESIDE the descent: the
# second admin action (or the 25g unused-AP conversion) the flat bill
# used to leave room for is now foreclosed, and that treasury/army
# delta cascades — divergence index 12 IS the first descent turn. The
# mid-war shape loses its +1 sawtooth, the tail reaches 0 four turns
# earlier (index 30 vs 34), and the endgame threat_by_target flattens
# (control ends Austria 47 / Russia 6; parity ends all zeros).
# ── RE-RECORDED August 15, 2026 — the PC15-D gate rulings (D1 "The
# Closed Frontier" + D2 "The Ally's Table" + D4 "The Congress Holds"),
# the ONE re-record that gate sanctions (gate record
# `docs/DESIGN_REFINEMENT.md` §Comprehensive Playtest). Prior series:
#   [70, 68, 66, 64, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48,
#    45, 42, 39, 36, 33, 30, 27, 24, 26, 23, 20, 17, 14, 6, 3, 0, 0, 0,
#    0, 0, 0, 0, 0, 0]
#
# ATTRIBUTION — TWO-STAGE flip experiment.
# Stage 1 (D1/D2, 4 arms; the three levers:
# `WorldState.RETREAT_MOVEMENT_LAW_ACTIVE`, `ALLY_SUPPLY_STATES`
# emptied, the P6.5 effective-cap rider reverted to raw caps):
#   all three off           -> reproduces the prior series BYTE-FOR-BYTE
#                              (the lever census is COMPLETE; the
#                              player-only D1 riders are inert on the
#                              ambient board by construction);
#   retreat law off (rest on)  -> diverges at INDEX 8 (79 vs 64);
#   ally table off (rest on)   -> diverges at INDEX 8 (79 vs 64);
#   P6.5 rider off (rest on)   -> diverges at INDEX 26 (28 vs 23).
# So the INDEX-8 JUMP is the P6.5 shown≠applied unification — the AI
# stops fleeing provinces that actually feed it (home/ally 1.5×), keeps
# its concentrations, fights more and alarms Europe sooner — while the
# closed frontier (Mack capitulates instead of touring Berlin) and the
# ally table shape the later run. Stage-1 intermediate series:
#   [70, 68, 66, 64, 72, 70, 68, 66, 79, 77, 75, 73, 71, 72, 75, 73, 71,
#    69, 67, 65, 62, 59, 56, 53, 40, 37, 34, 31, 28, 25, 22, 19, 16, 13,
#    10, 7, 4, 1, 0, 0, 0]
# Stage 2 (D4, 2 arms; the three levers: the P3.7 war filter, the
# pair-exit homeland return, the truce floor):
#   all three off (D1/D2 on) -> reproduces the stage-1 intermediate
#                               BYTE-FOR-BYTE (the D4 delta is exactly
#                               these levers, nothing else);
#   final tree               -> THIS series, diverging from the
#                               intermediate at INDEX 20 (63 vs 62) —
#                               the turn the first exhaustion floors
#                               trip: pairs that used to churn
#                               peace-and-redeclare now hold their
#                               truce, homeland returns credit the
#                               receiver's threat slot, and the tail
#                               decays slower (ends 5, not 0). All
#                               RULED design; none is a leak.
# ── RE-RECORDED August 15, 2026 — row NP (Napoleon), the ONE re-record
# that row sanctions (NAPOLEON_SPEC §12.3; landing record §15). Prior
# series:
#   [70, 68, 66, 64, 72, 70, 68, 66, 79, 77, 75, 73, 71, 72, 75, 73, 71,
#    69, 67, 65, 63, 61, 59, 62, 60, 48, 46, 44, 41, 38, 35, 32, 29, 26,
#    23, 20, 17, 14, 11, 8, 5]
#
# ATTRIBUTION — 4-arm flip experiment (levers:
# `combat_executor.SOVEREIGN_PRESENCE_ACTIVE`,
# `enemy_ai.SOVEREIGN_FEAR_ACTIVE`, and the AUTHORING itself — the
# `Napoleon` entry in europe_1805.json + the Soult 40k->30k carve):
#   arm 0  authoring ABSENT, both levers on  -> reproduces the PRIOR
#                                               series BYTE-FOR-BYTE.
#          => every NP mechanism (NP-0..NP-5) is dormant by
#             construction on a sovereign-free board, which is the
#             row's central claim, measured rather than asserted.
#   arm 1  authoring, both levers OFF        -> THIS series.
#   arm 2  authoring + fear on               -> IDENTICAL to arm 1.
#   arm 3  full tree (both levers on)        -> IDENTICAL to arm 1.
#
# So the WHOLE divergence is the AUTHORING, and both behaviour levers are
# provably INERT on this board — reported, not buried: the ambient
# harness is an AI-vs-AI run in which the Emperor never leaves Paris and
# is never attacked, so the aura never stamps and the fear term never
# reaches a decision. The Presence and the Fear are measured by
# `test_napoleon_np2_presence.py` directly (band test, grip-fade table,
# both-sides arms), and their live behaviour belongs to a PLAYED
# campaign, not to this control series.
#
# The authoring's own mechanism: Soult 40,000 -> 30,000 changes the
# outcome of the battles his corps fights, and the 22nd marshal changes
# the per-turn marshal loops. Divergence from the prior series is INDEX
# 13 — the mid-war shape loses the +1 sawtooth at index 13-14 and the
# tail decays smoothly (both series end at 5). France's national total
# is unchanged at 189,000 and the E1/ES-3/EC-U3 economy pins are
# byte-identical by construction (§12.1).
# ── RE-RECORDED August 16, 2026 — "The Road Home" (WIN-D3 + WIN-D5), the
# ONE re-record that slice sanctions (WAR_WITHDRAWAL_SPEC §7a). Prior
# series:
#   [70, 68, 66, 64, 72, 70, 68, 66, 79, 77, 75, 73, 71, 69, 67, 65, 63,
#    61, 59, 57, 55, 53, 51, 49, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19,
#    17, 15, 13, 11, 9, 7, 5]
#
# ATTRIBUTION — 4-arm flip experiment, the two changes run as SEPARATE
# arms (levers: `withdrawal.WITHDRAWAL_ACTIVE`, and the `Napoleon`
# location in europe_1805.json):
#   arm 0  neither          -> reproduces the PRIOR series BYTE-FOR-BYTE.
#                              The control holds, so these two changes are
#                              the only causes of what follows.
#   arm A  corridor only    -> diverges at index 18.
#   arm B  Lorraine only    -> diverges at index 5.
#   arm AB both             -> diverges at index 5. THIS series.
#   (A != AB, so both arms are live; neither is masking the other.)
#
# WHAT EACH ARM DOES, mechanically:
#
# arm A — the evacuation corridor is genuinely EXERCISED on this board:
# measured over the 40 turns, ONE corridor opens (Britain's, after a war
# ends with Paget and Shrapnel ashore), THREE road-home orders stand at
# peak, and the corps walk home instead of loitering on foreign soil. Their
# absence from that soil is what moves the tail. Reported rather than
# buried: an EARLIER draft of this slice measured byte-identical here, and
# that was not a safety result — it was the corridor barely functioning
# (the grant was written after the distances were measured, so every
# corridor-dependent corps was misfiled as cut off). The series moved once
# the mechanism actually worked, which is the honest sequence.
#
# arm B — the Emperor boots at Lorraine, not Paris (WIN-D5). He stands one
# march from Mack at Swabia instead of five, beside Soult's corps his Guard
# was carved from. On an AI-vs-AI ambient board he issues no orders, but a
# 10,000-man French stack sitting on the German frontier from turn 1 is
# read by every enemy planner that scores proximity and strength, so the
# divergence starts early (index 5) and the whole mid-war shape shifts.
#
# France's national total is unchanged at 189,000 and the E1/ES-3/EC-U3
# economy pins are byte-identical by construction — nothing about the
# authoring changed except which province the Guard stands in.
#
# M1–M7 were run before and after and are byte-identical WITHOUT
# re-record; that is a fact about that harness (it has no war ending with
# an army abroad, and no sovereign in it), not independent proof of safety.
#
# WO-26 re-record (August 21, 2026, slice 15 "The Capture Question
# Holds") — ONE index moves: [40] 13 -> 23. Indices 0-39 are byte-identical.
#
# Cause, proved by experiment rather than asserted. The ambient board is
# AI-vs-AI with nobody at the keyboard, but France is still
# `world.player_nation`, so a French capture takes the PLAYER branch of
# `_attempt_region_capture` and mounts a plunder/secure question no one
# will ever answer. Instrumented over the 40 turns: the player branch
# fires THREE times — Ney takes Swabia and the question (600g on it)
# stands unanswered for the rest of the run, and then Moravia (turn 18)
# and Vienna (turn 21) arrive on top of it. Before this slice those two
# were bare writes: the question was overwritten, and the provinces kept
# `capture_region`'s control flip while never running secure — buildings
# undamaged, construction still running, no `region_captured` row. France
# stormed Vienna and the engine forgot to garrison it. They now secure and
# log, which changes those provinces' output and, forty turns later, the
# final reading.
#
# Attribution, four arms:
#   A. world_state + dotation + vassal only (WO-27 carve-out, the shared
#      producer defined but unused) ......................... 13, unchanged
#   B. + combat_executor (the producer conversion) ........... 23
#   C. + movement_executor ................................... 23
#   D. + executor/capture_executor/main ...................... 23
#   E. full tree with ONE line flipped — the occupancy arm of
#      `mount_or_auto_secure_capture` forced False .......... 13, verbatim
# So the sole lever is the occupancy rule itself; the `apply_secure_effects`
# extraction, the WO-22 auto-advance defer, the WO-27 prune carve-out and
# the move path's `auto_secure` are all inert here (E reproduces the prior
# series with every one of them in place).
#
# Note for the next reader: an event-log probe reports ZERO of these
# `region_captured` rows, because `event_log` is capped at 500 and they are
# evicted — the IGR-B trap. Spy on `log_event` at write time, not the log.
#
# M1-M7 were run before and after and are byte-identical WITHOUT
# re-record.
#
# WO-8 re-record (September 1, 2026, slice 9 "The Courting Cap") - THREE
# indices move: [28] 59 -> 69, [29] 56 -> 66, [30] 53 -> 63. Every other
# index, [31] onward included, is byte-identical: the two trajectories
# re-converge at 50 and stay together to the end.
#
# Cause, measured before a line was written. Every throttle on enemy
# vassal courting was keyed per-COURTIER, none per-TARGET, so on THIS
# board at turn 28 all nineteen enemy nations spent their first court on
# the same satellite in one tick: Switzerland 47 -> 42 -> ... -> 2 -> 0,
# NINE of the courts moving it from 0 to 0 while still charging 2 DP
# each, ending `Switzerland-France: VASSAL -> WAR (vassal_rebellion)`.
# France lost a satellite, and its threat reading fell with it. Capped,
# Switzerland is courted ONCE per turn - Britain 28, Russia 29, Austria
# 30, Britain again 31 as its cooldown expires - bleeding 47 * 34 * 21 * 8
# and rebelling ANYWAY, at turn 32. The cap does not save the satellite,
# it delays its fall by three turns, which is why the two trajectories
# re-converge at [31]: that index IS the delayed rebellion arriving.
# (Corrected September 1, 2026 by slice 10. This block previously said
# "the last ten courts" - off by one - and "bottoms at 8 and recovers
# instead of rebelling", which was read off a trace that stopped short.
# Both were already corrected in the slice-9 landing record; the copy
# here was missed. Pinned by
# `test_wo_slice9_the_courting_cap.py::TestWhatTheCapActuallyDoesToTheSatellite`.)
#
# Attribution, four arms:
#   0. both levers False .................. prior series, BYTE-FOR-BYTE
#   A. COURTING_TARGET_CAP_ACTIVE only .... diverges at [28][29][30]
#   B. OBJECTION_TRUST_DAMPER_ACTIVE only . prior series, BYTE-FOR-BYTE
#   AB. full tree ......................... identical to arm A
# So the courting cap is the SOLE lever, and WO-D9's trust damper is
# measured inert here rather than assumed to be: the objection channel is
# gated on `marshal.nation == world.player_nation` and France issues no
# orders on this board, so no objection is ever raised to damp.
#
# Note for the next reader: `attempt_vassal_courting` lives inside
# `_process_ai_diplomatic_phase`, which `end_turn` runs only `if
# game_state` (`turn_manager.py:258`). A probe calling `tm.end_turn()`
# bare - as a first pass of mine did - measures ZERO courting events on a
# board that in fact fires nineteen, and would retire the defect as
# unreachable. Pass the runner's own `game_state`.
#
# M1-M7 were run before and after and are byte-identical WITHOUT
# re-record - structurally, not by luck: M1-M6 drive `resolve_battle`
# directly with no turn loop, and M7 never calls `end_turn`, so the
# courting phase is unreachable from all seven.
#
# WO-13 re-record (September 1, 2026, slice 10 "The Enemy-Direction
# Gate") - indices [0]-[12] are byte-identical and everything from [13]
# on moves. The series no longer decays to 23; it rises and holds.
#
# Cause, measured before a line was written. Three name-resolution seams
# in `executor.py` auto-corrected a query onto a MARSHAL with no typo
# gate, so on this board twelve province names collapse onto marshals
# (`Bern` -> Bernadotte and `Leon` -> Napoleon at a full 100, seven more
# -> Ney at 80). The ambient AI hit it SEVENTEEN times in the 40 turns,
# every one of them from `enemy_ai._execute_action` -> `_execute_attack`,
# and the consequence was a STALL: Britain's Paget stood at Bearn from
# turn 17 to 28, adjacent to Gascony, and six times - turns 17, 19, 21,
# 23, 25, 27, every OTHER turn, because a failed action writes a 2-turn
# cooldown - his attack on that province was redirected to Ney, wherever
# Ney was, and refused as out of range. Shrapnel spent the alternate
# turns the same way. The seventeen span turns 6-27 in two phases: six
# `Leon -> Napoleon` from Lisbon, then eleven `Gascony -> Ney` from
# Bearn. Gated, Britain fights in Iberia and France is not stripped:
# final provinces move from France 18 / Britain 19 to France 26 /
# Britain 12. (An earlier draft said "twenty-two consecutive turns",
# which read the whole span as one marshal's ordeal. Corrected.)
#
# Attribution, SEVEN arms, each a real source edit + a hash-pinned
# `--emit-series` subprocess run:
#   0.  no lever ..................... prior series, BYTE-FOR-BYTE
#   A.  ENEMY_DIRECTION_GATE only .... diverges at [11] - and NOT toward
#       the fix: with the absorber still open, 15 of the collapses simply
#       re-route into `_broad_fuzzy_diplomatic_check` and the world ends
#       Britain 27 / France 8. Gating the first seam alone is a different
#       bug, not a partial fix. This is the eval's "gating :433 re-routes
#       to :370" claim, measured rather than asserted.
#   B.  BROAD_DIPLOMATIC_GATE only ... prior series, BYTE-FOR-BYTE
#   C.  MARSHAL_DIRECTION_GATE only .. prior series, BYTE-FOR-BYTE
#   AB. enemy + absorber ............. IDENTICAL to the full tree
#   AC. enemy + marshal .............. IDENTICAL to arm A
#   ABC full tree .................... the series below
# So: A is necessary (nothing moves without it); B is inert ALONE but
# load-bearing in combination (AB != A, AB == ABC); and C is measured
# completely inert on this board (C == 0, AC == A, AB == ABC) with a
# written reason - all 58 of the ambient run's touches of that seam are
# the EXACT string `Brunswick`, a Prussian marshal who is also a
# province, so the fuzzy arm is never reached there. C is kept because
# the hole is identical and IS reachable from the typed direction, and it
# is pinned by construction rather than by the ambient board.
#
# Note for the next reader: an instrumented count of this defect must
# treat an EXACT match as legitimate. A naive "query is also a region
# key" counter reports 75 hits, of which 58 are marshal Brunswick being
# looked up by his own name - the number that matters is the 17
# non-exact ones.
#
# M1-M7 were run before and after and are byte-identical WITHOUT
# re-record - structurally: none of the seven routes a target string
# through `_fuzzy_match_enemy`; M1-M6 call `resolve_battle` directly and
# M7 drives marshals by object, never by name.
#
# FA slice 2 re-record (September 4, 2026, "No Word Came" — FA-1 / FA-N72 /
# FA-35) — indices [0]-[18] are byte-identical and everything from [19] on
# moves. The series no longer climbs to 97; it holds in the 70s-80s and
# ends at 47.
#
# Cause, measured before a line was written, on THIS board. A French
# marshal cornered by an AI attack is asked the W6-7 question (fight to
# the last / attempt a breakout) — and the enemy phase does not wait for
# an answer. Every further attack in the same phase re-entered
# `_check_marshal_fate`, found no guard for the standing ask, re-asked it
# and shot him again: Austria's six actions were six attacks on Massena,
# 8,000 -> 259, still standing. Over the prior run FOUR French marshals
# (Lannes, Massena, Murat, Ney) were DESTROYED that way — a corps ground
# to nothing takes no prisoners and sends no men home. The enemy AI's
# engagement rung (P0) also read neither of the brakes P4 carries, so a
# co-located corps attacked the same defender twice in one turn and every
# corps of the nation queued on a sub-1,000 remnant.
#
# Attribution, EIGHT arms, each a subprocess with the module levers set in
# the child (never a source edit):
#   0.   all three False ............... prior series, BYTE-FOR-BYTE
#   A.   LAST_STAND_UNANSWERED_RESOLVES  diverges at [29]: three of the
#        four destroyed marshals end as PRISONERS instead (Lannes,
#        Massena, Ney), Murat alone falls; France 22 / Austria 14
#   B.   P0_ENGAGEMENT_BRAKES_ACTIVE ... diverges at [19]: France 29 /
#        Austria 6 — the AI stops grinding, but WITHOUT A the re-asked
#        remnant the stub latch now protects is immortal (Lannes, Massena
#        and Ney all survive the run). B is never shipped without A; the
#        contract pin in test_fa_slice2_no_word_came_2026_09_04.py says so.
#   C.   STANDALONE_DECISION_LIVENESS_ACTIVE  prior series, BYTE-FOR-BYTE —
#        measured inert here with a reason: France issues no orders on the
#        ambient board (its gate never fires) and with A an ask is
#        resolved by the next attack in the same phase, before any end
#        turn could retire it. Its behaviour is player-facing (the row,
#        the refusal, the retirement) and pinned by construction.
#   AB.  the series below (== ABC)
#   AC.  == A     BC. == B     ABC. == AB
# So: A and B are each necessary, C is inert on this board, and the full
# tree is AB. Ending state: France 25 / Austria 12 (was 26 / 10), fallen
# {Murat}, captured {Lannes, Massena, Ney, Bennigsen, Buxhowden, Davout,
# Mack, ArchdukeJohn, Paget} — Russians taken by France for the first time
# on this board, because a French corps that is not ground to dust is
# still an army the next turn.
#
# M1-M7 were run before and after and are byte-identical WITHOUT
# re-record — structurally: M1-M6 drive `resolve_battle` directly and M7
# never reaches the enemy AI or the forced-retreat seam's second call.
#
# FA slice 2 REVIEW ROUND re-record (September 4, 2026, "The Word Is
# Owed") — indices [0]-[21] are byte-identical and everything from [22]
# on moves. The series ends at 29, not 47.
#
# Cause, found by the review fleet on aa6faa01 and measured before a line
# was written (review R1, F1). Slice 2's P0 brakes let an ENGAGED corps
# whose blow was spent fall THROUGH the engagement rung, on the theory
# that P4.5 / P7 would give it a useful order. They cannot: the executor's
# engaged rule refuses every attack-elsewhere and every advance while ANY
# at-war corps shares the province, remnant included, and the refusal
# wrote a two-turn `attack` cooldown keyed on the ACTION — so the next
# turn he could not attack the man he was standing on either. Measured
# on this board: FOUR "Cannot attack elsewhere while engaged" refusals
# in 40 turns (Charles at Milan on Ney, t26-t29: attack, refused, no
# action, attack, refused, no action). The braked corps now HOLDS
# (`P0_BRAKED_CORPS_HOLDS`), and the phase's next choice differs from
# the first refused fall-through on.
#
# Attribution, EIGHT arms, each a subprocess with the three review-round
# levers set in the child — eight module globals plus the
# `CombatExecutor.GARRISON_ASSAULT_COUNTS` CLASS attribute, with
# PYTHONHASHSEED=0 in the child's ENVIRONMENT (set in-process it silently does
# nothing and yields a different series — the slice-4 claims audit measured
# it); slice 2's own three levers held True:
#   0.   all three False ............... slice-2 series, BYTE-FOR-BYTE
#   D.   P0_BRAKED_CORPS_HOLDS ......... diverges at [22] — the series below
#   E.   P0_PRICES_THE_WHOLE_FIELD ..... slice-2 series, BYTE-FOR-BYTE —
#        measured inert with a reason: the braked subset differed from
#        the field on TWO evaluations in 40 turns and the decision was
#        the same both times (`probe_arms_mechanism.py`, e_relevant=2);
#        the defect is real on a co-located two-corps field and is
#        pinned by construction (test_fa_slice2r).
#   F.   P0_READS_FUTILITY ............. slice-2 series, BYTE-FOR-BYTE —
#        measured inert with a reason: no co-located pair reached
#        ATTACK_FUTILITY_LIMIT in 40 turns (f_relevant=0) — P0's own
#        ratio check retreats, or the target dies, first.
#   DE. == D     DF. == D     EF. == 0     DEF. == D
# So: D is the sole mover; E and F are inert on this board and pinned by
# construction. Ending state: France 8 / Austria 19 (was 25 / 12),
# fallen {Murat}, captured {ArchdukeJohn, Hiller, Lannes, Liechtenstein,
# Mack, Massena, NAPOLEON, Ney, Paget}. That swing is ONE seed's path
# after a turn-22 fork on a board where France issues no orders — the
# pre-slice-2 board also ended with the Emperor captured (turn 37) — and
# is NOT a measured effectiveness shift: the AI's executed actions fell
# 1,101 -> 1,077 and the consecutive-skip early exit fired 0 times in
# BOTH arms (the mechanism hypothesis "the fall-through burned the
# nation's budget" was tested and is FALSE; the fork is the four refused
# engaged attacks and the cooldowns they wrote).
#
# M1-M7 byte-identical WITHOUT re-record, structurally, as above.
#
# FA slice 4 re-record (September 4, 2026, "The AI Reads the Board" —
# FA-8 / FA-27+N38 / FA-N6 / FA-N7 / FA-N80 / FA-N54 / FA-N59 / FA-R1 /
# FA-R2) — indices [0]-[3] are byte-identical and everything from [4] on
# moves. The series no longer holds in the 70s; it falls from turn 5,
# never recovers, and DECAYS TO ZERO from [30] — on this board, a France
# that issues no orders is now overrun (2 provinces at turn 40, the
# Emperor among the captured) by an AI that reads the board.
#
# Nine rows, nine levers, ELEVEN arms (each a subprocess with the levers
# set in the child, every earlier slice's lever held at its shipped value;
# an uncommitted instrumented copy of the runner counted the AI's refused
# actions and garrison-rung evaluations — the committed `_emit_series`
# counts nothing but the series).
# Divergence is measured against the slice-2 review-round series:
#   0.  all nine False ................ review-round series, BYTE-FOR-BYTE
#   A.  P425_SKIPS_A_HELD_FIELD ....... diverges at [5]: garrison orders
#       15 -> 4 (garrison-RUNG evaluations, arm A alone), refusals 23 -> 7
#       — the rung stopped ordering assaults
#       into provinces held by a field army (FA-8: measured, Charles read
#       Munich's 10,000 garrison as a 2.32 walkover under 101,000 Frenchmen
#       and the executor fought the field battle the order actually is)
#   B.  SQUARE_FORMS_AFTER_THE_STRIKES  diverges at [4]: France 6 /
#       Austria 16, refusals 23 -> 3 — the square is the LAST word of a
#       phase, so the strike that used to break it fires first, and P3's
#       postures yield to a wanted square (FA-27 / FA-N38)
#   C.  BROKEN_AI_CORPS_IS_LIMITED ..... BYTE-FOR-BYTE — inert with a
#       reason: no AI corps is broken on this board in 40 turns (the
#       guard never binds); pinned by construction (FA-N6)
#   D.  COUNTER_PUNCH_PRICES_THE_FIELD  diverges at [14]: France 20 /
#       Austria 7 — three suicidal free blows declined (FA-N7)
#   E.  STAGNATION_READS_THE_CROSSING . BYTE-FOR-BYTE — inert with a
#       reason: no stagnation candidate lies across barred water on this
#       board; pinned by construction on the Channel (FA-N80)
#   F.  CAVALRY_LIMITS_ALL_NATIONS .... diverges at [13]: Paget's horse is
#       forced out of its defensive line (FA-N54)
#   G.  GARRISON_ASSAULT_COUNTS ....... BYTE-FOR-BYTE — inert with a
#       reason: no corps assaults a garrison twice in one phase here, so
#       the counter the assault now writes is never read (FA-N59)
#   H.  ALLY_SUPPORT_FIGHTS_ONLY_ENEMIES  diverges at [24]: the two
#       ally-support strikes on coalition partners (Buxhowden ->
#       ArchdukeCharles, turn 23; Kutuzov -> Liechtenstein, turn 28) are
#       gone (FA-R1)
#   I.  DRILL_RUNG_READS_FORTIFIED .... diverges at [29]: refused drills
#       14 -> 0 (FA-R2)
#   ALL the series below, diverging at [4] with B: France 2 / Austria 23 /
#       Britain 28; refused actions 23 -> 7 (drill 14 -> 0); garrison-rung
#       EVALUATIONS 15 -> 27 (executed garrison assaults 7 -> 4 — the rung
#       now fires on garrisons that stand ALONE, which it used to spend on
#       held provinces); captured {Bernadotte,
#       Davout, Lannes, Massena, Murat, NAPOLEON, Ney, Soult}, fallen
#       {Deroy}.
# So: six levers each move the board alone, three are inert with measured
# reasons, and the full tree forks at [4] with B. The endgame is one
# seed's path on a board where France issues no orders — the AI-V
# ten-seed sweep and the next PLAYED campaign, not this pin, are where
# "does the AI now beat a defended France" is measured; it is recorded
# here as a delta and a WARNING for the next in-game review, not as a
# balance claim. (A first re-record of this block was taken BEFORE the
# P3-yield arm of lever B landed and was wrong from [18]; the arms were
# re-run on the final code — arm 0 still byte-identical.)
#
# M1-M7 byte-identical WITHOUT re-record — structurally: the harness
# calls `resolve_battle` directly and never reaches EnemyAI, advance_turn
# (the cavalry limits) or the garrison resolver.
#
# ── FA slice 4 REVIEW ROUND "The Board Reads Back" (September 4, 2026) ──
# Re-recorded ONCE more, TEN arms (`series_arm4.py`: eight module globals
# set in the CHILD — six in enemy_ai, COUNTER_PUNCH_CREDITS_THE_CAPTURE in
# combat_executor, FORTIFIED_CORPS_NEVER_MARCHES in movement_executor —
# with PYTHONHASHSEED=0 in the child's ENVIRONMENT; the reviewer's own
# recipe correction). Every earlier lever at its shipped value.
#   0.  all eight False ............... the slice-4 series, BYTE-FOR-BYTE
#   A.  FIELD_PRICES_THE_TARGET_TOO ... BYTE-FOR-BYTE — inert with a
#       reason: no counter-punch or range-arm target is a retreated corps
#       standing beside a friend in 40 turns; pinned on the reviewer's
#       geometry (R1-1)
#   B.  ALLY_SUPPORT_PRICES_THE_FIELD . BYTE-FOR-BYTE — inert with a
#       reason: the ally-support strikes this board makes all clear the
#       floor; pinned on the reviewer's geometry (R1-2)
#   C.  ADMIN_RECRUIT_SPARES_THE_SQUARE  diverges at [23]: France 1 /
#       Austria 21 / Britain 33 — Mack's square survives its own admin
#       phase (R1-3)
#   D.  STAGNATION_READS_THE_PHASE ..... diverges at [15]: France 5 /
#       Austria 23 / Britain 19; moves 167 -> 115, drills 18 -> 7,
#       refused 7 -> 3 — no corps is marched out of its own drill or
#       square within the phase (R1-4)
#   E.  DRILLING_CORPS_IS_LEFT_TO_DRILL  diverges at [18]: refused 7 -> 3
#       (six of the seven survivors were this class) (R1-5)
#   F.  CAVALRY_AI_READS_THE_LIMIT ..... diverges at [15]: France 0 /
#       Austria 26 / Britain 29 ALONE — the horse the limit forced
#       AGGRESSIVE is not bought back into DEFENSIVE (R1-7). Measured
#       three ways before shipping: an outright never-park ban with the
#       frontier-fortify guard moved the board to France 19 / Austria 10
#       (F alone, fork [9]) and the round to France 13 — a balance swing,
#       NOT taken; the shipped TELL rule (AGGRESSIVE horse = the limit
#       spoke; a fresh horse may park once) lands as recorded here.
#   G.  COUNTER_PUNCH_CREDITS_THE_CAPTURE  BYTE-FOR-BYTE — inert with a
#       reason: no banked blow is spent on an undefended capture in 40
#       turns; pinned on the reviewer's geometry (R1-6, GR5)
#   H.  FORTIFIED_CORPS_NEVER_MARCHES .. diverges at [10]: France 3 /
#       Austria 24 / Britain 20 — a fortified AI corps no longer walks
#       off with its works (R1-8, GR5)
#   ALL the series below, diverging at [10] with H: France 5 / Austria 26
#       / Britain 21 / Russia 10; refused actions 7 -> 4; squares 12 -> 10,
#       attacks 82 -> 68, moves 167 -> 150; captured {} (was eight, the
#       Emperor among them), fallen {Deroy}.
# So: five levers each move the board alone, three are inert with measured
# reasons, and the round forks at [10]. The passive board ends France 5
# where slice 4 left it at 2 with the whole roster captured — the AI's own
# defects, not France's play, had been worth three provinces and eight
# corps. The balance question the slice-4 record raised was MEASURED by
# the review's balance lens (docs/audits/fa_build_2026_09_04/
# REVIEW_slice4_R2_balance_measurement.md — an unattended France overrun on
# 8/8 seeds, a scripted one on 5/5 arms) and is put to the user as a gate
# in the round's landing record; nothing here retunes it.
# ── FA slice 14 part 2d re-record (September 6, 2026) ──────────────────────
# TWO levers move it and a third is measurably inert. Six arms, arm 0
# reproducing the prior series byte-for-byte, so the attribution is exact:
#
#   0   control ................ the prior series, byte-for-byte
#   A   CORRIDOR_MINIMUM_WINDOW_ACTIVE (FA-S12-1) ... diverges at [24] ALONE,
#       3 -> 13. Spain's Castanos is rescued from Guyenne at turn 17 instead
#       of standing there for twenty-five turns, so Switzerland's
#       `vassal_rebellion` -10 lands one loop later on a different board.
#   B   ELIMINATION_RELIEVES_THE_LORD (FA-S12-2) ... diverges at [10],
#       55 -> 45; indices 10-22 are a uniform -10 translation of the decay
#       ramp. The lever fires EXACTLY ONCE in 40 turns (KingdomOfItaly is
#       eliminated out of France's web at world turn 10).
#   C   FREED_SATELLITE_KEEPS_ITS_ARMY (FA-S12-2, the fifth exit) ...
#       BYTE-IDENTICAL, and inert BY CONSTRUCTION rather than by luck: every
#       lord that ever exists on this board is France, and France is the
#       player, whose elimination returns at the handler's first line.
#   AB  A + B ................. [10] as B, and A still adds [23] = 6.
#       AB != B, so neither lever is masked by the other.
#   ALL A + B + C ............. IDENTICAL to AB, which is C's inertness
#       measured a second time, in combination.
#
# The `provinces` map is IDENTICAL to control in all eighteen nations on
# every arm. Neither lever changes who holds what; they change when France's
# threat decays to nothing.
BASELINE_SERIES = [
    70, 68, 66, 64, 62, 68, 66, 63, 60, 58, 45, 42, 39, 36, 33, 30, 27,
    24, 21, 18, 15, 12, 9, 6, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0,
]


def _run_series_subprocess() -> dict:
    """Run the 40-turn ambient sim in a hash-pinned subprocess."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--emit-series"],
        env=env, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"series runner failed:\n{result.stdout[-2000:]}\n"
        f"{result.stderr[-2000:]}")
    payload_line = [ln for ln in result.stdout.splitlines()
                    if ln.startswith("PAYLOAD=")][-1]
    return json.loads(payload_line[len("PAYLOAD="):])


class TestStep4SeriesPin:
    """§4.4a step 4 — the byte-identical 40-turn series."""

    @pytest.fixture(scope="class")
    def payload(self):
        return _run_series_subprocess()

    def test_series_matches_recorded_baseline(self, payload):
        assert payload["series"] == BASELINE_SERIES

    def test_nonplayer_slots_live_and_bounded(self, payload):
        """Steps 5-6 LANDED (Stage D): producers now pass the actor as
        target, so non-player slots may accrue — the Stage-C-era
        no-accrual invariant is consciously INVERTED (AI_INTENT_SPEC §17).
        What must still hold: every slot is clamped 0-100, and D3's
        gravity — France remains the story of the age.

        DEF-5 naval flip (conscious, the AI-3r honest-zero discipline):
        the ambient run's non-player accrual came from CROSS-CHANNEL
        conquests — the very walks the §4.1 crossing gate now refuses —
        so the measured ambient value is an HONEST ZERO with a written
        predicate, and the liveness half of this pin moves to a direct
        producer probe (the machinery, not the ambient board, is what
        must stay alive).

        WIN-D5 amendment (August 16, 2026). The flat "no non-player slot
        reaches the brewing tier" clause was an OBSERVATION about the old
        ambient board, not a law, and the Emperor's forward start falsifies
        it. Attribution, three arms (final `threat_by_target`):

            arm 0  neither change      France 5
            arm A  corridor only       Austria 6
            arm B  Emperor at Lorraine France 35, Austria 54, Russia 32
            arm AB both                France 13, Austria 83, Russia 30

        Two hypotheses were tested and the first was WRONG, which is why
        this is spelled out rather than asserted. It is NOT D3's eclipse
        clause: Austria ends with **8 provinces against France's 21**, so
        she has plainly not eclipsed anyone. Tracing the producer instead
        gives the real answer — Austria's 83 is **36 × `battle_win`(+3),
        3 × `region_capture`, 2 × `capital_capture`**. With the Guard on
        the Rhine the German war becomes a grinding one, and a France that
        issues no orders for forty turns loses it battle after battle. A
        small power that has won thirty-six fights and stormed two
        capitals IS menacing, and the threat model is right to say so.

        So the clause is replaced by the anti-LEAK invariant it was really
        standing in for, which has teeth the old one did not: coalition-tier
        threat must be EARNED. A nation cannot arrive at the brewing tier
        without a war record that accounts for it. That catches a producer
        misattributing threat to a bystander — the actual failure mode —
        while allowing a belligerent to become genuinely dangerous.
        """
        tbt = payload["threat_by_target"]
        belligerents = set(payload["belligerents"])
        for nation, value in tbt.items():
            assert 0 <= value <= 100, f"{nation} slot out of clamp: {value}"
            if nation != "France" and value >= 60:
                assert nation in belligerents, (
                    f"{nation} reached the brewing tier ({value}) without "
                    f"ever being at war — threat is leaking onto a bystander")
        # Liveness (deterministic probe): the per-target producer accrues
        # a non-player slot when handed a non-player actor.
        probe = WorldState.from_scenario(str(SCENARIO_PATH))
        before = int(getattr(probe, "threat_by_target", {}).get("Austria", 0))
        add_threat(probe, 7, "test_probe", target="Austria")
        assert probe.threat_by_target["Austria"] == before + 7, (
            "steps 5-6 appear dead: the non-player slot did not accrue")

    def test_scalar_mirrors_player_slot_throughout(self, payload):
        assert payload["scalar_mirror_ok"] is True


class TestStep2Property:
    """threat_level is a view over the player's slot."""

    def test_read_is_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["France"] = 37
        assert world.threat_level == 37

    def test_write_is_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 44
        assert world.threat_by_target["France"] == 44

    def test_missing_slot_reads_zero(self):
        world = WorldState(player_nation="France")
        world.threat_by_target = {}
        assert world.threat_level == 0

    def test_augmented_assignment_works(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        world.threat_level += 5
        assert world.threat_level == 15
        assert world.threat_by_target["France"] == 15


class TestStep1TargetParameter:
    """add_threat/reduce_threat optional target, default player."""

    def test_default_target_is_byte_identical_player_arm(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        new = add_threat(world, 5, "battle_win")
        assert new == 15
        assert world.threat_level == 15
        entry = world.threat_sources_this_turn[-1]
        assert entry["source"] == "battle_win"
        assert entry["amount"] == 5
        assert entry["target"] == "France"
        assert world.positive_threat_delta_this_turn is True

    def test_explicit_nonplayer_target_writes_its_own_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 10
        new = add_threat(world, 7, "battle_win", target="Austria")
        assert new == 7
        assert world.threat_by_target["Austria"] == 7
        assert world.threat_level == 10  # player slot untouched
        entry = world.threat_sources_this_turn[-1]
        assert entry["target"] == "Austria"

    def test_nonplayer_target_does_not_set_player_pressure_flag(self):
        """positive_threat_delta_this_turn backs a FRANCE-threat anti-spam
        gate — a foreign slot rising must not trip it."""
        world = WorldState(player_nation="France")
        world.positive_threat_delta_this_turn = False
        add_threat(world, 7, "battle_win", target="Austria")
        assert world.positive_threat_delta_this_turn is False
        add_threat(world, 3, "battle_win")
        assert world.positive_threat_delta_this_turn is True

    def test_reduce_threat_target_arm(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["Austria"] = 20
        new = reduce_threat(world, 6, "generous_peace", target="Austria")
        assert new == 14
        assert world.threat_by_target["Austria"] == 14
        entry = world.threat_sources_this_turn[-1]
        assert entry["amount"] == -6
        assert entry["target"] == "Austria"

    def test_per_slot_clamp(self):
        world = WorldState(player_nation="France")
        add_threat(world, 250, "capital_capture", target="Austria")
        assert world.threat_by_target["Austria"] == 100
        reduce_threat(world, 250, "generous_peace", target="Austria")
        assert world.threat_by_target["Austria"] == 0

    def test_zero_amount_noop_returns_target_slot(self):
        world = WorldState(player_nation="France")
        world.threat_by_target["Austria"] = 9
        assert add_threat(world, 0, "x", target="Austria") == 9
        assert reduce_threat(world, -3, "x", target="Austria") == 9
        assert world.threat_sources_this_turn == []


class TestStep3Serialization:
    """to_dict writes both; from_dict migrates a legacy scalar."""

    def test_round_trip_preserves_nonplayer_slots(self):
        world = WorldState(player_nation="France")
        world.threat_level = 42
        world.threat_by_target["Austria"] = 17
        restored = WorldState.from_dict(world.to_dict())
        assert restored.threat_level == 42
        assert restored.threat_by_target["Austria"] == 17

    def test_to_dict_writes_both_forms(self):
        world = WorldState(player_nation="France")
        world.threat_level = 33
        data = world.to_dict()
        assert data["threat_level"] == 33
        assert data["threat_by_target"]["France"] == 33

    def test_legacy_scalar_only_save_seeds_player_slot(self):
        world = WorldState(player_nation="France")
        world.threat_level = 55
        data = world.to_dict()
        data.pop("threat_by_target")
        restored = WorldState.from_dict(data)
        assert restored.threat_level == 55
        assert restored.threat_by_target["France"] == 55

    def test_missing_both_reads_zero(self):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        data.pop("threat_by_target")
        data.pop("threat_level")
        restored = WorldState.from_dict(data)
        assert restored.threat_level == 0

    def test_legacy_entry_without_target_survives_round_trip(self):
        """A legacy save's source entries have no target key — they load
        unchanged (readers default to the player at read time)."""
        world = WorldState(player_nation="France")
        world.threat_sources_this_turn = [
            {"source": "battle_win", "amount": 3}]
        restored = WorldState.from_dict(world.to_dict())
        assert restored.threat_sources_this_turn == [
            {"source": "battle_win", "amount": 3}]


def _emit_series() -> None:
    """The subprocess runner (invoked with --emit-series)."""
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager

    world = WorldState.from_scenario(str(SCENARIO_PATH))
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}

    series = [int(world.threat_level)]
    mirror_ok = (world.threat_level
                 == world.threat_by_target.get(world.player_nation, 0))
    # WIN-D5: which nations were ever belligerent during the run. Sampled
    # each turn from the live state rather than counted off `event_log`
    # (capped at 500 — the IGR-B eviction trap) or `battles_this_turn`
    # (cleared inside every advance, so it always reads empty from here).
    belligerents: set = set()
    for turn in range(40):
        random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
        tm.end_turn(game_state)
        for _key, _state in world.diplomatic_states.items():
            if _state == "WAR":
                belligerents.update(_key.split("|"))
        series.append(int(world.threat_level))
        if (world.threat_level
                != world.threat_by_target.get(world.player_nation, 0)):
            mirror_ok = False
    provinces: dict = {}
    for region in world.regions.values():
        if region.controller:
            provinces[region.controller] = provinces.get(region.controller, 0) + 1
    print("PAYLOAD=" + json.dumps({
        "series": series,
        "threat_by_target": {
            str(k): int(v) for k, v in world.threat_by_target.items()},
        "scalar_mirror_ok": bool(mirror_ok),
        # WIN-D5: the war record behind each slot, so the pin can tell a
        # nation that EARNED coalition-tier threat from a leak.
        "provinces": {str(k): int(v) for k, v in provinces.items()},
        "belligerents": sorted(belligerents),
    }))


if __name__ == "__main__":
    if "--emit-series" in sys.argv:
        sys.path.insert(0, str(REPO_ROOT))
        _emit_series()
