"""MC-1a pin tests (MARSHAL_CONTENT_PASS_SPEC.md §4, memo §6.1 — T0 quick wins).

The July 10, 2026 gate blessed the ten-ability MC-1 set. MC-1a lands the two
T0 items — both pure data activations of already-wired mechanics:

- Ney re-keyed to "Bravest of the Brave" in ``europe_1805.json``, including
  the load-bearing ``"trigger": "when_attacking"`` key (the combat dispatch
  gates on trigger BEFORE name — memo §1 design note — so an ability block
  without it is silently dead).
- ArchdukeCharles activated to "Habsburg Resolve" (+3% defense, the check
  already lives in ``marshal.py get_defense_modifier``).
- All ten MC-1 names in ``_WIRED_ABILITY_MARSHALS``; names whose ability
  slice hasn't landed stay inactive via the MC-0 real-name gate.
"""

import pytest

from backend.ai.parser_eval import build_world
from backend.game_logic.combat import CombatResolver
from backend.game_logic.marshal_overview import (
    _WIRED_ABILITY_MARSHALS,
    _build_ability,
    build_marshal_overview,
)

MC1_MARSHALS = {
    "Ney", "Davout", "Soult", "Lannes", "Murat", "Massena", "Bernadotte",
    "ArchdukeCharles", "Kutuzov", "Moore",
}


@pytest.fixture()
def world():
    return build_world("1805")


# ════════════════════════════════════════════════════════════════════════
# Boot pins: the authored ability blocks survive the scenario pipeline
# ════════════════════════════════════════════════════════════════════════

class TestBootAbilities:
    def test_ney_boots_with_bravest_of_the_brave(self, world):
        ney = world.get_marshal("Ney")
        assert ney.ability.get("name") == "Bravest of the Brave"

    def test_ney_carries_the_load_bearing_trigger_key(self, world):
        # The combat dispatch checks trigger BEFORE name (combat.py) — an
        # ability block missing this key is silently dead (memo §1).
        ney = world.get_marshal("Ney")
        assert ney.ability.get("trigger") == "when_attacking"

    def test_charles_boots_with_habsburg_resolve(self, world):
        charles = world.get_marshal("ArchdukeCharles")
        assert charles.ability.get("name") == "Habsburg Resolve"

    def test_other_1805_marshals_still_unauthored(self, world):
        # MC-1b/1c own the rest — until those land, everyone else boots with
        # the scenario default (no ability).
        for name in ("Davout", "Soult", "Lannes", "Murat", "Massena",
                     "Bernadotte", "Kutuzov", "Moore", "Mack"):
            marshal = world.get_marshal(name)
            assert marshal.ability.get("name") == "None", name


# ════════════════════════════════════════════════════════════════════════
# Mechanics: Ney's +2 shock fires on attack, never on defense
# ════════════════════════════════════════════════════════════════════════

class TestNeyMechanics:
    def test_ability_triggered_when_ney_attacks(self, world):
        ney = world.get_marshal("Ney")
        mack = world.get_marshal("Mack")
        result = CombatResolver().resolve_battle(ney, mack, apply_casualties=False)
        assert result["ability_triggered"] is not None
        assert "Bravest of the Brave" in result["ability_triggered"]

    def test_silent_when_ney_defends(self, world):
        ney = world.get_marshal("Ney")
        mack = world.get_marshal("Mack")
        result = CombatResolver().resolve_battle(mack, ney, apply_casualties=False)
        assert result["ability_triggered"] is None


# ════════════════════════════════════════════════════════════════════════
# Mechanics: Charles's +3% defense is live
# ════════════════════════════════════════════════════════════════════════

class TestCharlesMechanics:
    def test_habsburg_resolve_multiplies_defense_by_1_03(self, world):
        charles = world.get_marshal("ArchdukeCharles")
        with_ability = charles.get_defense_modifier(is_outnumbered=False)
        charles.ability["name"] = "None"
        without_ability = charles.get_defense_modifier(is_outnumbered=False)
        assert with_ability == pytest.approx(without_ability * 1.03)


# ════════════════════════════════════════════════════════════════════════
# Display: the card shows active exactly when a real ability is authored
# ════════════════════════════════════════════════════════════════════════

class TestCardDisplay:
    def test_wired_set_contains_all_ten_mc1_marshals(self):
        assert MC1_MARSHALS <= _WIRED_ABILITY_MARSHALS

    def test_ney_card_shows_active_ability(self, world):
        cards = build_marshal_overview(world)
        ney_card = next(c for c in cards if c["name"] == "Ney")
        assert ney_card["ability_active"] is True
        assert ney_card["ability_name"] == "Bravest of the Brave"
        assert ney_card["ability_trigger"] == "when_attacking"

    def test_unauthored_wired_name_stays_inactive(self, world):
        # Soult is in _WIRED_ABILITY_MARSHALS ahead of his MC-1b slice — the
        # MC-0 real-name gate must keep his card inactive until it lands.
        cards = build_marshal_overview(world)
        soult_card = next(c for c in cards if c["name"] == "Soult")
        assert soult_card["ability_active"] is False
        assert soult_card["ability_name"] == ""

    def test_charles_ability_section_active(self, world):
        # Enemy marshals get no player card; pin the section builder directly.
        out = _build_ability(world.get_marshal("ArchdukeCharles"))
        assert out["ability_active"] is True
        assert out["ability_name"] == "Habsburg Resolve"
