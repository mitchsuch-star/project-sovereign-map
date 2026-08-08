"""CA8-D3 — the rival is a PERSON (gate held Aug 8, 2026, user-delegated).

Gate record: docs/JEALOUSY_SPEC.md §0.5. Two rulings, both YES:

Q1 RIVAL MEMORY — `find_jealousy_target` prefers, among peers STRICTLY
ABOVE on the glory ladder, the man this marshal's envy has already fired on
(most lifetime fires, ties by worse relationship then alphabetical); with
no history above, the one-rung-up rule is byte-identical. The audit had
measured Murat's rival changing FOUR times in twelve turns because
targeting recomputed from the rolling window alone.

Q2 PETITION PER ESCALATION LEVEL — the §6 confrontation latch widens from
once-per-pair-per-campaign to once per (pair, escalation level): the same
feud gets an audience each time it deepens, bounded at four confrontations
per pair (levels 0..3). A legacy bare pair key reads as "level 0 seen".

Zero new serialized fields: memory reads `jealousy_history` (already
serialized); the latch reuses `jealousy_confrontations_seen` (strings).
"""

from pathlib import Path

import pytest

from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    w = WorldState.from_dict(world1805.to_dict())
    w.authority_tracker.authority = 50
    return w


def _glory(world, name, points, turn=None):
    J._append_glory(world.marshals[name], turn or world.current_turn, points)


def _fire_history(marshal, target_name, turns):
    """Record prior fires the way apply_jealousy does — history only."""
    marshal.jealousy_history.setdefault(target_name, []).extend(turns)


# ═══════════════════════ Q1 — RIVAL MEMORY ═════════════════════════════════


class TestRivalMemory:
    def test_no_history_keeps_one_rung_rule_byte_identical(self, world):
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Lannes", 2)
        assert J.JEALOUSY_RIVAL_MEMORY is True
        target = J.find_jealousy_target(world.marshals["Lannes"], world)
        assert target.name == "Ney"  # one rung up, never the top

    def test_memory_refixes_on_historic_rival_above(self, world):
        """The Murat case: his envy has fired on Davout before; when the
        window reshuffles Ney between them, the feud does NOT re-cast."""
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Davout", [3])
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Davout"

    def test_memory_ignores_rival_no_longer_above(self, world):
        """Envy requires the object to outshine him — a passed rival falls
        back to the rung rule (and passing resolves with surge)."""
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Davout", [3])  # Davout at glory 0, below
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Ney"

    def test_memory_prefers_most_fires(self, world):
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Ney", [3])
        _fire_history(murat, "Davout", [4, 6])
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Davout"  # 2 fires beat 1

    def test_memory_tie_breaks_by_worse_relationship(self, world):
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Ney", [3])
        _fire_history(murat, "Davout", [4])
        murat.relationships["Ney"] = -2
        murat.relationships["Davout"] = 0
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Ney"

    def test_devoted_remembered_rival_never_shadows_fresh_envy(self, world):
        """A remembered rival repaired to Devoted (+2) is immune — memory
        must not return him, or old friendship would suppress ALL new envy
        (the rung rule would have fired on the fresh man)."""
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Davout", [3, 5])
        murat.relationships["Davout"] = 2
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Ney"

    def test_flip_experiment_flag_restores_rung_rule(self, world, monkeypatch):
        """The attribution instrument: memory OFF reproduces the pre-gate
        selection exactly."""
        _glory(world, "Davout", 7)
        _glory(world, "Ney", 4)
        _glory(world, "Murat", 2)
        murat = world.marshals["Murat"]
        _fire_history(murat, "Davout", [3])
        monkeypatch.setattr(J, "JEALOUSY_RIVAL_MEMORY", False)
        target = J.find_jealousy_target(murat, world)
        assert target.name == "Ney"

    def test_memory_is_gr5_symmetric(self, world):
        """An enemy-nation marshal's envy remembers too (Building Blocks)."""
        austrians = [m.name for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength > 0]
        assert len(austrians) >= 3, austrians
        low, mid, top = austrians[0], austrians[1], austrians[2]
        _glory(world, top, 7)
        _glory(world, mid, 4)
        _glory(world, low, 2)
        marshal = world.marshals[low]
        _fire_history(marshal, top, [3])
        target = J.find_jealousy_target(marshal, world)
        assert target.name == top

    def test_ladder_shift_still_resolves_with_surge(self, world):
        """Passing the remembered rival keeps the satisfying release arc."""
        murat = world.marshals["Murat"]
        _fire_history(murat, "Davout", [3])
        murat.jealous_of = "Davout"
        murat.jealousy_turns_remaining = 3
        _glory(world, "Murat", 5)  # now above Davout (0)
        world._jealousy_processed_turn = None
        events = J.process_turn(world)
        assert murat.jealous_of is None
        assert murat.jealousy_surge_turns == 1
        assert any(e.get("type") == "jealousy_ladder_shift" for e in events)


# ═══════════════════ Q2 — PETITION PER ESCALATION LEVEL ════════════════════


def _fire(world, marshal, target):
    events = []
    J.apply_jealousy(world, marshal, target, delta=2, threshold=1,
                     events=events)
    return events


class TestPetitionPerLevel:
    def test_first_confrontation_latches_level_zero_key(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        _fire(world, ney, davout)
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["kind"] == "jealousy_confrontation"
        assert petition["context"]["escalation_level"] == 0
        assert "Davout|Ney@L0" in world.jealousy_confrontations_seen

    def test_same_level_never_reserves(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        _fire(world, ney, davout)
        world.pending_marshal_petition = None  # the player answered
        J.clear_jealousy(world, ney, resolved_by_action=False)
        _fire(world, ney, davout)  # still level 0 (no qualifying escalation)
        assert world.pending_marshal_petition is None

    def test_refires_when_the_level_rises(self, world):
        """The audit's channel-goes-silent defect: the feud deepens ON
        CAMERA now — each escalation level speaks exactly once."""
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        _fire(world, ney, davout)
        world.pending_marshal_petition = None
        J.clear_jealousy(world, ney, resolved_by_action=False)
        # Stored Rival relationship makes the next fire QUALIFY (spec §10),
        # advancing the pair to level 1 before the petition block reads it.
        ney.relationships["Davout"] = -1
        _fire(world, ney, davout)
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["context"]["escalation_level"] == 1
        assert "no longer a passing mood" in petition["body"]
        assert "Davout|Ney@L1" in world.jealousy_confrontations_seen

    def test_level_bodies_carry_the_escalation_register(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        J.queue_confrontation_petition(world, ney, davout, 2)
        assert "entrenched" in world.pending_marshal_petition["body"]
        J.queue_confrontation_petition(world, ney, davout, 3)
        body = world.pending_marshal_petition["body"]
        assert "mutual" in body and "Davout" in body

    def test_level_zero_body_is_unchanged(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        J.queue_confrontation_petition(world, ney, davout)
        body = world.pending_marshal_petition["body"]
        for fragment in ("passing mood", "entrenched", "mutual"):
            assert fragment not in body

    def test_legacy_bare_key_reads_as_level_zero_seen(self, world):
        """Pre-CA8-D3 saves hold bare pair keys — no duplicate level-0
        petition, but the level-1 re-fire is NEW behaviour they receive."""
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        world.jealousy_confrontations_seen = ["Davout|Ney"]
        _fire(world, ney, davout)
        assert world.pending_marshal_petition is None
        J.clear_jealousy(world, ney, resolved_by_action=False)
        ney.relationships["Davout"] = -1
        _fire(world, ney, davout)
        assert world.pending_marshal_petition is not None
        assert world.pending_marshal_petition["context"][
            "escalation_level"] == 1

    def test_bounded_at_four_levels_per_pair(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        world.jealousy_confrontations_seen = [
            f"Davout|Ney@L{n}" for n in range(4)]
        ney.relationships["Davout"] = -1
        J._set_escalation_level(ney, "Davout", 3)
        _fire(world, ney, davout)
        assert world.pending_marshal_petition is None

    def test_forced_mutual_spiral_fire_never_petitions(self, world):
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        events = []
        J.apply_jealousy(world, davout, ney, delta=1, threshold=1,
                         events=events, forced=True)
        assert world.pending_marshal_petition is None

    def test_enemy_pairs_never_petition(self, world):
        austrians = [m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength > 0]
        _fire(world, austrians[0], austrians[1])
        assert world.pending_marshal_petition is None

    def test_mixed_format_latch_round_trips(self, world):
        world.jealousy_confrontations_seen = ["Davout|Ney", "Lannes|Ney@L1"]
        restored = WorldState.from_dict(world.to_dict())
        assert restored.jealousy_confrontations_seen == [
            "Davout|Ney", "Lannes|Ney@L1"]
