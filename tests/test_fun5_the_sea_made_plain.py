"""Row FUN, Session FUN-5 "the sea made plain" — its behaviour test, opened by
FUN-1 (November 25, 2026) for the one row FUN-1's plan moved here.

FUN1-11 (`docs/BUG_FIXES.md`, OPEN, owner row FUN, landing FUN-5): once France
holds Rumelia, Britain's blockade fleet counts as covering the Bosphorus
(`naval._fleet_covers_link`: a blockade covers every link touching a province
of a nation it is at war with), so the march is "shut" by 100 British sail in a
sea Britain has nothing to do with. FUN-5 rebuilds the straits (`docs/
GAMEPLAY_REVIEW_2026_11_25.md` §1.4, §5): a short strait is a land link closed
only while an ENEMY fleet commands that sea. The strict xfail turns red the day
FUN-5 lands, and is then made a plain test.
"""
from __future__ import annotations

import os

import pytest

from backend.game_logic import naval
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.world_state import WorldState

SCENARIO = os.path.join("godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")


@pytest.fixture(scope="module")
def _booted():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(_booted.to_dict())


class TestFUN5TheSeaMadePlain:

    @pytest.mark.xfail(strict=True, reason="FUN1-11 — owner row FUN, landing Session FUN-5 "
                                           "(a blockade covers only the straits of its own seas)")
    def test_a_blockade_does_not_shut_a_strait_in_another_sea(self, world):
        for name in ("Croatia", "Rumelia"):
            world.regions[name].controller = "France"
        set_diplomatic_state(world, "France", "Ottoman", "WAR", reason="FUN1-11")
        coverers = [c for c, _strength in naval.covering_fleets(world, "France", "Rumelia", "Constantinople")]
        assert "Britain" not in coverers, coverers
