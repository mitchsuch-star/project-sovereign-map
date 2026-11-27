"""Row FUN, Session FUN-2b "peace terms priced" — its behaviour test, opened by
FUN-2 (November 26, 2026) for the brief's sixth point, which FUN-2's approved
plan moved to its own session (`docs/NEXT_SESSION_PROMPT.md`, FUN-2b's block;
`PRE_DEPLOY_PLAN.md` §2 row FUN; `STATUS.md`).

The brief: "taking a province at the table costs war score (the settlement's own
scorer); a total conquest by treaty takes more than one war." FUN-2 made land
taken BY ARMS cost fear; FUN-2b prices land taken AT THE TABLE, and gives the
table's land the same fear a capture gives (and land handed back the reverse).

Each strict xfail turns red the day FUN-2b lands its rule, and is then made a
plain test. The plain test documents what already holds: the bilateral peace
refuses a total cession of Austria at any war score.
"""
from __future__ import annotations

import os

import pytest

from backend.game_logic import fear as F
from backend.models.world_state import WorldState

SCENARIO = os.path.join("godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")
AUSTRIA = ["Tyrol", "Carniola", "Croatia", "Hungary", "Moravia", "Bohemia", "Vienna"]


@pytest.fixture(scope="module")
def _booted():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(_booted.to_dict())


class TestFUN2bPeaceTermsPriced:

    def test_a_bilateral_total_cession_is_refused_at_any_war_score(self, world):
        from backend.game_logic.diplomacy import calculate_acceptance
        from backend.game_logic.diplomacy import get_war_score_for
        key = world._make_diplo_key("France", "Austria")
        world.war_scores[key] = 100 if key.split("|")[0] == "France" else -100
        assert get_war_score_for(world, "France", "Austria") == 100     # France is winning
        result = calculate_acceptance({
            "type": "peace", "proposer_nation": "France", "target_nation": "Austria",
            "demands": [{"type": "territory", "regions": list(AUSTRIA),
                         "from": "Austria", "to": "France"}]}, world)
        assert result["outcome"] == "REJECT"

    @pytest.mark.xfail(strict=True, reason="FUN-2b — the settlement table's land price stops "
                                           "rising at five provinces (harshness capped at 1.5)")
    def test_the_tables_price_keeps_rising_past_five_provinces(self):
        from backend.game_logic.diplomatic_templates import calculate_raw_treaty_harshness
        from backend.game_logic.settlement_scoring import calculate_term_harshness_penalty

        def penalty(n):
            raw = calculate_raw_treaty_harshness({"clauses": [], "demands": [
                {"type": "territory_cede", "regions": AUSTRIA[:n]}]})
            return calculate_term_harshness_penalty(raw)["score"]

        assert penalty(7) < penalty(5)

    @pytest.mark.xfail(strict=True, reason="FUN-2b — land taken at the table frightens the "
                                           "courts as a capture does")
    def test_a_cession_at_the_table_frightens_like_a_capture(self, world):
        from backend.game_logic import game_end
        region = world.regions["Tyrol"]
        region.controller = "France"
        region.stability = 50
        world.invalidate_active_nations_cache()
        game_end.record_province_title(world, "Tyrol", game_end.TITLE_TREATY, "Austria", "France")
        assert F.fear_of(world, "Bavaria") > 0

    @pytest.mark.xfail(strict=True, reason="FUN-2b — land handed back calms the court's fear")
    def test_land_handed_back_calms_the_court(self, world):
        from backend.game_logic.diplomacy import hand_back_province
        world.capture_region("Tyrol", "France")
        before = F.fear_of(world, "Austria")
        hand_back_province(world, "Austria", "France", "Tyrol")
        assert F.fear_of(world, "Austria") < before
