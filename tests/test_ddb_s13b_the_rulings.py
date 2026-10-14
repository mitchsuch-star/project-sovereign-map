"""Pre-Deploy S13b part 1 — the rulings and the siblings the sweeps found
(October 14, 2026; `docs/BUG_FIXES.md` §DD-B; rules `SYSTEMS_REFERENCE.md`
§116).

  DDB-X5   DW-2, the bilateral weight: the bilateral acceptance reads the
           war score at the table's own credit (`BASE_SIDE_PRESSURE_SCALE`,
           0.65 — was 0.3), so the two scorers agree on one package.
  DDB-X7   (found by DDB-3) the peace's corridor hands a released contingent
           ITS court's road, never the treaty's road to the lord's home zone.
  DDB-X8   (found by DDB-10) the keep-out counsel, the question desk and the
           Congress name the Cabinet control, never a typed line the door
           refuses.
  DDB-X10  (found by DDB-X5) the armistice handoff carries concessions only —
           the drafted truce's own border demand is dropped and voiced.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import contingent as CG
from backend.game_logic import diplomacy as D
from backend.game_logic import settlement_scoring as SC
from backend.game_logic import settlement_staging as SS
from backend.game_logic import withdrawal as WD
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X5 — DW-2: one war score, one credit
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX5:
    _TERMS = [{"type": "peace"},
              {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 400}]

    def _both(self, w, war_score: int):
        key = w._make_diplo_key("France", "Britain")
        w.war_scores[key] = war_score if key.split("|")[0] == "France" else -war_score
        war_id = next(iter(w.get_war_instances_by_participant("Britain")))
        inst = w.war_instances[war_id]
        side = inst["side_by_nation"]["France"]
        acc = "defenders" if side == "attackers" else "attackers"
        table = SC.calculate_common_peace_acceptance(
            w, war_id=war_id, war_instance=inst, proposer_side=side, accepting_side=acc,
            accepting_leader="Britain", covered_enemy_participants=["Britain"],
            settlement_terms=self._TERMS)
        return table, SS.bilateral_estimate(w, "Britain", staged_terms=self._TERMS, actor="France")

    def test_the_weight_is_the_tables_own(self):
        assert D.bilateral_war_score_weight() == SC.BASE_SIDE_PRESSURE_SCALE == 0.65

    def test_the_two_scorers_agree_on_one_package(self, w):
        table, bilateral = self._both(w, 50)
        assert (table["score"], table["verdict"]) == (56, "accept")
        assert (bilateral["score"], bilateral["outcome"]) == (54, "ACCEPT")

    def test_at_the_old_weight_they_disagreed(self, w, monkeypatch):
        monkeypatch.setattr(D, "bilateral_war_score_weight", lambda: 0.3)
        table, bilateral = self._both(w, 50)
        assert table["verdict"] == "accept"
        assert (bilateral["score"], bilateral["outcome"]) == (37, "COUNTER_OFFER")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X7 — the contingent's own road at the peace
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX7:
    @pytest.fixture
    def posted(self, w):
        with contextlib.redirect_stdout(io.StringIO()):
            CG.raise_contingent(w, "Holland")
        record = CG.contingent_record(w, "Holland")
        marshal = w.marshals[record["marshal"]]
        w.regions["Ulster"].controller = "France"
        w.invalidate_active_nations_cache()
        marshal.location = "Ulster"
        marshal.strategic_order = None
        return w, marshal

    def test_a_peace_without_a_truce_walks_it_home_under_its_colours(self, posted):
        w, marshal = posted
        assert CG.takes_its_own_road(w, marshal)
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "France", "Britain", "PEACE", "peace_ratified")
            D.set_diplomatic_state(w, "Holland", "Britain", "PEACE", "peace_ratified")
        assert CG.contingent_record(w, "Holland")["state"] == "homeward"
        assert CG.is_contingent_home_order(marshal.strategic_order)
        messages = [e["message"] for e in w.event_log if e.get("type") == "evacuation_granted"]
        assert messages and "marching home under Holland's colours" in messages[-1]
        assert "Normandy" not in messages[-1]

    def test_a_french_corps_keeps_the_treatys_road(self, posted):
        w, _marshal = posted
        ney = w.marshals["Ney"]
        assert not CG.takes_its_own_road(w, ney)
        assert CG.release_home(w, ney) is None


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X8 — the keep-out names its Cabinet control
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX8:
    @pytest.fixture
    def quiet(self):
        from tests.test_sf_page_the_front_page_of_the_peace import _quiet_france
        with contextlib.redirect_stdout(io.StringIO()):
            return _quiet_france()

    def test_the_cheapest_keep_out_names_the_control(self, quiet):
        from backend.game_logic import coalition as CO
        quiet.nation_relations[quiet._make_diplo_key("France", "Prussia")] = -13
        quiet.nation_gold["France"] = 99999
        cheapest = CO.league_cheapest_keep_out(quiet)
        assert cheapest["control"] == "F1 → Prussia → Buy Off Their Design"
        assert cheapest["order_text"].endswith("— F1 → Prussia → Buy Off Their Design.")
        assert "'buy off" not in cheapest["order_text"]

    def test_the_desk_answers_with_the_cabinet_rows(self, quiet):
        from backend.ai.question_desk import _answer_keep_out
        text = _answer_keep_out(quiet, "France", "Austria")
        assert "In the Cabinet: F1 → Austria → Improve Relations" in text, text
        assert "'improve relations with" not in text and "The order" not in text


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X10 — a truce extracts no tribute, whatever the seed
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX10:
    """The leg-1 synthetic world (France +60 over Britain and Prussia in one
    war): at the shipped weight the drafted truce authors a border demand
    (Waterloo) that the estimator no longer eases away, and nothing is
    seeded from the joint draft."""

    def test_the_drafted_border_demand_is_dropped_and_voiced(self):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        from backend.game_logic.settlement_actions import handle_settlement_dialogue_action
        from tests.test_settlement_gate4_leg1_fixes import (
            _stage_propose, _winning_two_court_world,
        )
        world, _war = _winning_two_court_world()
        assert generate_suggested_terms("Britain", "armistice", world, deterministic=True)["demands"] == [
            {"type": "territory_cede", "value": 1, "regions": ["Waterloo"]}]
        with contextlib.redirect_stdout(io.StringIO()):
            review = handle_settlement_dialogue_action(
                world, action="submit_settlement_for_review", dialogue=_stage_propose(world),
                action_params={"action": "submit_settlement_for_review"})["diplomatic_dialogue"]
            chooser = handle_settlement_dialogue_action(
                world, action="seek_armistice_instead", dialogue=review,
                action_params={"action": "seek_armistice_instead"})
            confirmed = handle_settlement_dialogue_action(
                world, action="confirm_pair_substitute", dialogue=chooser["diplomatic_dialogue"],
                action_params={"action": "confirm_pair_substitute"})
        bilateral = confirmed["diplomatic_dialogue"]
        sends = [o for o in bilateral["options"] if o.get("action") == "execute_proposal"]
        assert sends and all(not (o.get("terms") or {}).get("demands") for o in sends)
        assert bilateral.get("armistice_demands_dropped") is True
        assert "Waterloo" not in str(bilateral.get("proposal_terms_summary"))
        assert "concessions travel" in str(bilateral.get("talleyrand_text") or "").lower()
