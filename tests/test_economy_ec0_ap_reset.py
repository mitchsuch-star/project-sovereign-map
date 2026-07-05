"""EC-0 regression tests (ECONOMY_REVISIT_SPEC.md §2 EC-0).

The advance_turn AP reset used the LEGACY 4-nation builder regardless of
sovereign_map, so on the Europe world it:
  1. squashed Austria's tuned 4 AP back to the legacy 3 after turn 1, and
  2. never reset the 15 Europe-only nations (Naples/Bavaria/Ottoman/...),
     so their ap_per_turn treaty penalties compounded forever.

The fix snapshots the world's OWN base AP at construction
(``base_nation_actions``) and resets from that. These pins cover both worlds
plus the snapshot's serialization + back-compat.
"""

import pytest

from backend.models.world_state import WorldState


@pytest.fixture()
def europe():
    return WorldState(sovereign_map="europe")


@pytest.fixture()
def legacy():
    return WorldState()


# ════════════════════════════════════════════════════════════════════════
# Bug 1 — Austria keeps its tuned 4 AP across turns (was squashed to 3)
# ════════════════════════════════════════════════════════════════════════

class TestAustriaHoldsBaseAP:
    def test_boot_value(self, europe):
        assert europe.nation_actions["Austria"] == 4
        assert europe.base_nation_actions["Austria"] == 4

    def test_holds_4_across_one_turn(self, europe):
        europe.advance_turn()
        assert europe.nation_actions["Austria"] == 4

    def test_holds_4_across_several_turns(self, europe):
        for _ in range(3):
            europe.advance_turn()
        assert europe.nation_actions["Austria"] == 4

    def test_legacy_austria_still_3(self, legacy):
        # No regression: the legacy world's Austria base IS 3.
        assert legacy.base_nation_actions["Austria"] == 3
        legacy.advance_turn()
        assert legacy.nation_actions["Austria"] == 3


# ════════════════════════════════════════════════════════════════════════
# Bug 2 — Europe-only nations are reset each turn (were never restored)
# ════════════════════════════════════════════════════════════════════════

class TestEuropeOnlyNationsReset:
    @pytest.mark.parametrize("nation", ["Naples", "Bavaria", "Ottoman", "Holland"])
    def test_depressed_ap_restores_to_base(self, europe, nation):
        base = europe.base_nation_actions[nation]
        assert nation not in {"France", "Austria", "Britain", "Prussia", "Russia"}
        europe.nation_actions[nation] = 0  # as if a penalty had driven it down
        europe.advance_turn()
        assert europe.nation_actions[nation] == base

    def test_ap_per_turn_penalty_applies_then_releases(self, europe):
        # A treaty ap_per_turn clause on a Europe-only nation must reduce from
        # base each turn (apply-then-release), never compound to zero.
        nation = "Naples"
        base = europe.base_nation_actions[nation]  # 2
        key = europe._make_diplo_key("France", nation)
        europe.diplomatic_states[key] = "PEACE"
        europe.active_treaties[key] = {
            "type": "peace",
            "clauses": [{"type": "ap_per_turn", "amount": 1,
                         "from": nation, "to": "France"}],
            "signed_turn": 1,
        }
        europe.advance_turn()
        assert europe.nation_actions[nation] == base - 1
        europe.advance_turn()
        # Still base-1, NOT compounding downward
        assert europe.nation_actions[nation] == base - 1
        # Remove the clause -> next reset restores full base
        europe.active_treaties.pop(key)
        europe.advance_turn()
        assert europe.nation_actions[nation] == base


# ════════════════════════════════════════════════════════════════════════
# Snapshot serialization + back-compat
# ════════════════════════════════════════════════════════════════════════

class TestBaseSnapshotSerialization:
    def test_round_trip_preserves_base(self, europe):
        data = europe.to_dict()
        assert data["base_nation_actions"]["Austria"] == 4
        restored = WorldState.from_dict(data)
        assert restored.base_nation_actions["Austria"] == 4
        restored.advance_turn()
        assert restored.nation_actions["Austria"] == 4

    def test_from_dict_backcompat_defaults_to_nation_actions(self, europe):
        # A pre-fix save (no base_nation_actions) defaults base to the loaded
        # nation_actions — correct at a turn boundary (nation_actions IS base).
        data = europe.to_dict()
        data.pop("base_nation_actions")
        restored = WorldState.from_dict(data)
        assert restored.base_nation_actions["Austria"] == \
            restored.nation_actions["Austria"]

    def test_custom_scenario_base_survives_round_trip(self):
        # A modded custom-AP value the legacy builder could never rebuild is
        # captured by the snapshot.
        europe = WorldState(sovereign_map="europe")
        europe.nation_actions["Naples"] = 5
        europe.base_nation_actions["Naples"] = 5
        restored = WorldState.from_dict(europe.to_dict())
        restored.nation_actions["Naples"] = 0
        restored.advance_turn()
        assert restored.nation_actions["Naples"] == 5
