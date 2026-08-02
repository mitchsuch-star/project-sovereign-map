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
BASELINE_SERIES = [
    85, 83, 81, 79, 77, 75, 73, 71, 69, 66, 66, 63, 60, 57, 57, 44, 41,
    38, 38, 35, 32, 29, 29, 26, 23, 20, 17, 14, 14, 11, 8, 5, 2, 2, 0,
    0, 0, 0, 0, 0, 0,
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
