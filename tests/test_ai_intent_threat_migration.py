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
BASELINE_SERIES = [
    70, 68, 66, 64, 72, 70, 68, 66, 64, 62, 60, 58, 66, 64, 70, 68, 69,
    66, 63, 60, 57, 54, 51, 48, 45, 45, 32, 29, 26, 28, 30, 27, 24, 21,
    18, 15, 12, 9, 6, 3, 0,
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
        What must still hold: every slot is clamped 0-100, and on the
        historical 40-turn run no non-player slot reaches the brewing
        tier (D3's gravity — France remains the story of the age).

        DEF-5 naval flip (conscious, the AI-3r honest-zero discipline):
        the ambient run's non-player accrual came from CROSS-CHANNEL
        conquests — the very walks the §4.1 crossing gate now refuses —
        so the measured ambient value is an HONEST ZERO with a written
        predicate, and the liveness half of this pin moves to a direct
        producer probe (the machinery, not the ambient board, is what
        must stay alive)."""
        tbt = payload["threat_by_target"]
        for nation, value in tbt.items():
            assert 0 <= value <= 100, f"{nation} slot out of clamp: {value}"
            if nation != "France":
                assert value < 60, (
                    f"{nation} reached the brewing tier ({value}) on the "
                    f"historical ambient run — D3's gravity should hold")
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
    for turn in range(40):
        random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
        tm.end_turn(game_state)
        series.append(int(world.threat_level))
        if (world.threat_level
                != world.threat_by_target.get(world.player_nation, 0)):
            mirror_ok = False
    print("PAYLOAD=" + json.dumps({
        "series": series,
        "threat_by_target": {
            str(k): int(v) for k, v in world.threat_by_target.items()},
        "scalar_mirror_ok": bool(mirror_ok),
    }))


if __name__ == "__main__":
    if "--emit-series" in sys.argv:
        sys.path.insert(0, str(REPO_ROOT))
        _emit_series()
