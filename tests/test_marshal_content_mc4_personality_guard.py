"""MC-4 pin tests (MARSHAL_CONTENT_PASS_SPEC.md §4/§9, memo §5 — the boot guard).

The July 10, 2026 gate closed the balanced/loyal question as a CONTRACT
(Golden Rule 9), not an open placeholder: the roster ships on THREE
implemented personalities (aggressive/cautious/literal), and the retired
reserved values may no longer be AUTHORED anywhere. Re-open owners: the
Jealousy v3.1 gate (v3.2 roster addendum) or the MC exit review, on
evidence three types are expressively insufficient. A revived fourth type
must not be named "loyal" (diplomat `loyalist` namespace collision).

The boot guard has three arms, pinned here:
  1. Validator hard-error — `VALID_PERSONALITIES` == the implemented three;
     because `from_scenario` raises on validator errors, an explicit
     retired/typo'd personality can never boot a scenario (assert arm).
  2. `create_marshal_from_data` ValueError — the data-driven roster path
     (legacy fixture lists, future code-authored rosters) refuses
     non-implemented types at construction.
  3. `from_scenario` log warning — a marshal dict that OMITS personality
     boots on from_dict's save-compat "balanced" default; that residual
     hole is logged, never silent (log arm).

Save-LOAD stays deliberately unguarded: from_dict must keep restoring
whatever a save carries (and defaulting an absent key to "balanced") so no
existing save is ever refused. The guard is authoring-time only.
"""

import json
import logging

import pytest

from backend.ai.parser_eval import SCENARIO_1805_PATH, build_world
from backend.models.marshal import (
    Marshal,
    create_enemy_marshals,
    create_marshal_from_data,
    create_starting_marshals,
)
from backend.models.personality import IMPLEMENTED_PERSONALITIES
from backend.models.world_state import WorldState
from backend.modding.validator import VALID_PERSONALITIES, validate_marshal


def _minimal_marshal(personality=None):
    data = {"name": "Test", "location": "Paris", "strength": 10000}
    if personality is not None:
        data["personality"] = personality
    return data


# ════════════════════════════════════════════════════════════════════════
# The single source of truth
# ════════════════════════════════════════════════════════════════════════

class TestSingleSource:
    def test_implemented_set_is_exactly_the_three(self):
        assert IMPLEMENTED_PERSONALITIES == {"aggressive", "cautious", "literal"}

    def test_validator_consumes_the_single_source(self):
        # The validator set IS the boot guard (from_scenario hard-fails on
        # its errors) — it must never drift from the implemented set.
        assert VALID_PERSONALITIES == set(IMPLEMENTED_PERSONALITIES)


# ════════════════════════════════════════════════════════════════════════
# Arm 1: validator hard-error (the scenario-boot assert arm)
# ════════════════════════════════════════════════════════════════════════

class TestValidatorArm:
    @pytest.mark.parametrize("personality", ["balanced", "loyal", "agressive"])
    def test_retired_or_typo_personality_is_an_error(self, personality):
        result = validate_marshal(_minimal_marshal(personality))
        assert not result.is_valid
        assert any("personality" in e.path for e in result.errors)

    @pytest.mark.parametrize("personality", sorted(IMPLEMENTED_PERSONALITIES))
    def test_implemented_personalities_validate_clean(self, personality):
        result = validate_marshal(_minimal_marshal(personality))
        assert not any("personality" in e.path for e in result.errors)

    def test_error_message_names_the_implemented_three(self):
        result = validate_marshal(_minimal_marshal("balanced"))
        msg = next(e.message for e in result.errors if "personality" in e.path)
        for p in IMPLEMENTED_PERSONALITIES:
            assert p in msg

    def test_scenario_authoring_balanced_cannot_boot(self, tmp_path):
        # End-to-end assert arm: flip one shipped marshal to a retired type
        # and the whole scenario refuses to boot.
        scenario = json.loads(SCENARIO_1805_PATH.read_text(encoding="utf-8"))
        scenario["marshals"]["Soult"]["personality"] = "balanced"
        path = tmp_path / "chimera_scenario.json"
        path.write_text(json.dumps(scenario), encoding="utf-8")
        with pytest.raises(ValueError, match="personality"):
            WorldState.from_scenario(str(path))


# ════════════════════════════════════════════════════════════════════════
# Arm 2: create_marshal_from_data (the data-driven roster path)
# ════════════════════════════════════════════════════════════════════════

class TestFactoryArm:
    @pytest.mark.parametrize("personality", ["balanced", "loyal", "agressive", None])
    def test_non_implemented_personality_raises(self, personality):
        with pytest.raises(ValueError, match="MC-4 boot guard"):
            create_marshal_from_data(_minimal_marshal(personality))

    @pytest.mark.parametrize("personality", sorted(IMPLEMENTED_PERSONALITIES))
    def test_implemented_personalities_construct(self, personality):
        marshal = create_marshal_from_data(_minimal_marshal(personality))
        assert marshal.personality == personality

    def test_error_names_the_marshal_and_the_three(self):
        with pytest.raises(ValueError) as exc:
            create_marshal_from_data(_minimal_marshal("loyal"))
        msg = str(exc.value)
        assert "'Test'" in msg
        for p in IMPLEMENTED_PERSONALITIES:
            assert p in msg

    def test_legacy_fixture_rosters_pass_the_guard(self):
        # The Waterloo fixture lists flow through the guarded factory —
        # every legacy marshal must already author an implemented type.
        marshals = {**create_starting_marshals(), **create_enemy_marshals()}
        assert marshals  # non-empty sanity
        for m in marshals.values():
            assert m.personality in IMPLEMENTED_PERSONALITIES, m.name


# ════════════════════════════════════════════════════════════════════════
# Arm 3: the omitted-key log warning (the residual hole, never silent)
# ════════════════════════════════════════════════════════════════════════

class TestLogArm:
    def test_omitted_personality_boots_balanced_but_logs(self, tmp_path, caplog):
        # A marshal dict WITHOUT the key passes validation (optional field,
        # minimal-scenario contract) and boots on the save-compat default —
        # the boot guard's log arm names it.
        scenario = {"marshals": {"Ghost": {
            "name": "Ghost", "location": "Paris", "strength": 10000,
        }}}
        path = tmp_path / "omitted_personality.json"
        path.write_text(json.dumps(scenario), encoding="utf-8")
        with caplog.at_level(logging.WARNING, logger="backend.models.world_state"):
            world = WorldState.from_scenario(str(path))
        assert world.get_marshal("Ghost").personality == "balanced"
        assert any(
            "Ghost" in rec.message and "balanced" in rec.message
            for rec in caplog.records
        )

    def test_shipped_scenario_boots_silently(self, caplog):
        # All 21 shipped marshals author an implemented type — no log line.
        with caplog.at_level(logging.WARNING, logger="backend.models.world_state"):
            world = build_world("1805")
        for m in world.marshals.values():
            assert m.personality in IMPLEMENTED_PERSONALITIES, m.name
        assert not any(
            "unimplemented personality" in rec.message for rec in caplog.records
        )


# ════════════════════════════════════════════════════════════════════════
# Save-LOAD is deliberately unguarded (pinned so a future "cleanup" can't
# quietly break old saves)
# ════════════════════════════════════════════════════════════════════════

class TestSaveLoadUnaffected:
    def test_from_dict_still_defaults_absent_key_to_balanced(self):
        marshal = Marshal.from_dict(
            {"name": "Old", "location": "Paris", "strength": 5000}
        )
        assert marshal.personality == "balanced"

    def test_from_dict_restores_a_retired_value_without_raising(self):
        marshal = Marshal.from_dict(
            {"name": "Old", "location": "Paris", "strength": 5000,
             "personality": "loyal"}
        )
        assert marshal.personality == "loyal"
