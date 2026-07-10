"""MC-0 regression tests (MARSHAL_CONTENT_PASS_SPEC.md §2 MC-0).

marshal_overview._build_ability gated only on the marshal's NAME, so a
1805-scenario marshal (booted with ability {"name": "None"} by
create_marshal_from_data) whose name is in _WIRED_ABILITY_MARSHALS reported
``ability_active=True`` with the ability literally named "None". The fix also
requires a real ability name. Legacy marshals with genuine wired abilities
must still display them.
"""

import pytest

from backend.ai.parser_eval import build_world
from backend.game_logic.marshal_overview import (
    _build_ability,
    build_marshal_overview,
    _WIRED_ABILITY_MARSHALS,
)


def _find(marshal_cards, name):
    for card in marshal_cards:
        if card.get("identity", {}).get("name") == name or card.get("name") == name:
            return card
    return None


# ════════════════════════════════════════════════════════════════════════
# Unit: a wired-name marshal carrying no real ability is NOT active
# ════════════════════════════════════════════════════════════════════════

class TestBuildAbilityUnit:
    def test_none_ability_on_wired_name_not_active(self):
        # MC-1a authored real abilities onto roster marshals, so the MC-0
        # "wired name, no real ability" case is pinned on a bare-constructed
        # marshal (ability defaults to {"name": "None"}) — the gate itself,
        # independent of what the roster currently authors.
        from backend.models.marshal import Marshal
        ney = Marshal(name="Ney", location="Paris", strength=10000,
                      personality="aggressive", nation="France")
        assert ney.name in _WIRED_ABILITY_MARSHALS
        assert ney.ability.get("name") == "None"  # constructor default
        out = _build_ability(ney)
        assert out["ability_active"] is False
        assert out["ability_name"] == ""

    @pytest.mark.parametrize("name", ["Mack", "ArchdukeJohn", "Buxhowden",
                                      "Brunswick", "Hohenlohe"])
    def test_no_ability_1805_marshals_report_inactive(self, name):
        # The MC-1 gate blessed these as NO-ability by design (memo §2 —
        # Mack's nothing IS the Ulm story); they must stay inactive.
        w = build_world("1805")
        marshal = w.get_marshal(name)
        if marshal is None:
            pytest.skip(f"{name} not in 1805 roster")
        out = _build_ability(marshal)
        assert out["ability_active"] is False
        assert out["ability_name"] != "None"

    def test_legacy_real_ability_still_active(self):
        w = build_world("legacy")
        ney = _ability = _build_ability(w.get_marshal("Ney"))
        assert ney["ability_active"] is True
        assert ney["ability_name"] == "Bravest of the Brave"

    def test_legacy_marshal_without_ability_inactive(self):
        w = build_world("legacy")
        out = _build_ability(w.get_marshal("Grouchy"))
        assert out["ability_active"] is False


# ════════════════════════════════════════════════════════════════════════
# Integration: the full overview never shows a "None" active ability
# ════════════════════════════════════════════════════════════════════════

class TestOverviewIntegration:
    def test_no_1805_marshal_shows_none_ability(self):
        # Cards are flat dicts (_build_marshal_card spreads the section dicts).
        cards = build_marshal_overview(build_world("1805"))
        assert cards, "expected player marshal cards"
        for card in cards:
            if card.get("ability_active"):
                assert card.get("ability_name") not in ("", "None"), (
                    f"{card.get('name')} shows a bogus active ability")

    def test_legacy_wired_marshals_still_present(self):
        cards = build_marshal_overview(build_world("legacy"))
        actives = {
            card.get("ability_name")
            for card in cards
            if card.get("ability_active")
        }
        assert "Bravest of the Brave" in actives
