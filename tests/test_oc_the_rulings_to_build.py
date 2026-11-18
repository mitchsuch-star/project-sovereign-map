"""Row OC — "the rulings built" (ruled November 17, 2026, row BA's session BA-6
and row MC, under the user's "leave no open calls or anything make decisions
yourself soundly with research"; the record `docs/audits/
OPEN_CALLS_RULED_2026_11_17.md` §5). Each ruling that lands in a slice of its
own before Session H — and the two that join Session H's head — carries a
STRICT xfail here: it turns red the day the behaviour lands, so the row is
closed with it (CLAUDE.md rule 9: owner row, landing slice, done-when, STATUS
line, behaviour test). Each pin reads the seam the ruling names — the slice
builds the rule behind it and turns the pin into its behaviour test.
"""
from __future__ import annotations

import importlib
import inspect

import pytest

_OC = ("RULED November 17, 2026 (BA-6) — HOMED in row OC before Session H "
       "(docs/audits/OPEN_CALLS_RULED_2026_11_17.md §5); this pin turns red the day it lands")
_H = ("RULED November 17, 2026 (BA-6) — HOMED at Session H's head "
      "(docs/audits/OPEN_CALLS_RULED_2026_11_17.md §3); this pin turns red the day it lands")


def _seam_up(module: str, name: str) -> bool:
    fn = getattr(importlib.import_module(module), name, None)
    return callable(fn) and not inspect.signature(fn).parameters and fn() is True


class TestOC1TheCourtsPurse:

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd15_a_law_buys_what_is_used(self):
        """Prussia paid ~3,100 gold of upkeep by turn 40 for drill laws it
        never drilled under: the law rung reads demand first."""
        assert _seam_up("backend.game_logic.reforms", "a_law_buys_what_is_used")

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd37_the_staff_is_saved_for_without_the_upkeep_reserve(self):
        """At war, a court saves for its Staff (the doctrine's cure) without
        the five-turns-of-upkeep reserve that made it unreachable after S14j."""
        assert _seam_up("backend.game_logic.reforms", "the_staff_is_saved_for_without_the_upkeep_reserve")

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd21_a_cheap_rung_keeps_a_turn_of_upkeep(self):
        assert _seam_up("backend.ai.enemy_ai", "a_cheap_rung_keeps_a_turn_of_upkeep")

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd29_a_cure_is_never_stranded_by_an_edict(self):
        assert _seam_up("backend.game_logic.affairs", "a_cure_is_never_stranded_by_an_edict")


class TestOC2TheEmperorsPurse:

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd20_a_deficit_every_third_turn_is_remembered(self):
        assert _seam_up("backend.models.world_state", "a_deficit_every_third_turn_is_remembered")

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd19_restlessness_is_priced_by_the_province(self):
        assert _seam_up("backend.models.world_state", "restlessness_is_priced_by_the_province")


class TestOC3TheStrangulationsLetter:

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_brit1_a_strangled_britain_writes_without_contact(self):
        assert _seam_up("backend.game_logic.ai_diplomacy", "a_strangled_britain_writes_without_contact")


class TestOC4GoldenRuleOne:

    @pytest.mark.xfail(strict=True, reason=_OC)
    def test_grd34_terrain_scaled_recklessness_is_read_in_the_marshal(self):
        from backend.models.marshal import Marshal
        assert "terrain" in inspect.signature(Marshal.get_attack_modifier).parameters


class TestSessionHsHead:

    @pytest.mark.xfail(strict=True, reason=_H)
    def test_grd16_a_marshal_typo_is_offered_the_nearest_own_name(self):
        assert _seam_up("backend.commands.executor", "a_marshal_typo_is_offered_the_nearest_own_name")

    @pytest.mark.xfail(strict=True, reason=_H)
    def test_grd33_the_literal_buff_expires_with_the_turn(self):
        assert _seam_up("backend.commands.meta_executor", "the_literal_buff_expires_with_the_turn")
