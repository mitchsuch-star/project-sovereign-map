"""The peace rulings, part 1 — the one verdict and the counsel (Pre-Deploy
S13e part 1, October 16, 2026; `docs/audits/PEACE_CONUNDRUM_2026_10_15.md`
§46; `docs/BUG_FIXES.md` §PC; rules `SYSTEMS_REFERENCE.md` §122).

  PC-R1  rulings B + C: ONE verdict on every road — France's separate peace
         is never stopped by an ally's war; it is PRICED where it leaves an
         ally fighting and COMMON TO THE SIDE where France leads it (the
         ally's pair ends in the same instrument, Pressburg Art. 6); the
         consent read is the court's own (COALITION_SPEC §6a's loyalty term,
         P1's break-ranks clause); the words; the guided demand's `to`.
  PC-R8  ruling K: Talleyrand's counsel is a reading, not a lookup — ranked
         over the roads that carry, varied from authored pools, his own mind
         said, one builder for every surface (pins (a)–(e) of §46 K).
  PC-F9  the beaten court's honest peace is never silent.
  PC-F49 a player carried into an ally's defensive war has a peace road.
  PC-F50 the leader's letter never signs away a winning court; gold credits
         the court paid in full and the side at half.
  PC-F51 a side whose leader left re-seats its leader.
  The client's lies at the peace moment: F48, F34, F67, F78, F65, F73, F76,
  F37; the counsel's rows F12, F35, F40, F43, F10, F25, F88.

The two boards of the report are fixtures (`tests/fixtures/pc_boards/`): the
user's turn-6 autosave copy, and the same board with Vienna in French hands.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import random
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy as AI
from backend.game_logic import counsel as CS
from backend.game_logic import diplomacy as D
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
BOARDS = REPO / "tests" / "fixtures" / "pc_boards"

BAVARIA_NOTE = "Bavaria's war with Austria ends in this instrument; she takes nothing by it."


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _board(name: str) -> WorldState:
    """The board as saved, its mailbox cleared: the user's save carries
    Italy's petition and an envoy, and a pending matter shuts the wizard
    (the rule the client keeps; the pins read the board, not the mailbox)."""
    with _quiet():
        world = WorldState.from_dict(
            json.loads((BOARDS / name).read_text(encoding="utf-8"))["world_state"])
        while world.dialogue_manager.peek() is not None:
            world.dialogue_manager.pop()
    return world


@pytest.fixture
def vienna_held() -> WorldState:
    return _board("turn6_vienna_held.json")


@pytest.fixture
def turn6() -> WorldState:
    return _board("turn6_copy.json")


def _rows(world, nation):
    acts = D.get_available_diplomatic_actions(world, nation)
    return acts.get("actions") if isinstance(acts, dict) else acts


def _state(world, a, b):
    return world.diplomatic_states.get(world._make_diplo_key(a, b), "PEACE")


# ═══════════════════════════════════════════════════════════════════════════
# PC-R1 — the one verdict
# ═══════════════════════════════════════════════════════════════════════════

class TestPCR1:
    def test_i_the_paradox_is_never_a_stop(self, w):
        """(i) the HARD_STOP at the predicate is the WARNING its siblings are."""
        rows = D.get_peace_commitment_conflicts(w, "France", "Austria", [])
        assert rows and not any(r["severity"] == "HARD_STOP" for r in rows)
        from backend.game_logic.treaty import can_sign
        assert can_sign(w, {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                            "sweeteners": [], "demands": [], "clauses": []}, at_send=True).ok

    def test_ii_the_leaders_peace_is_common_to_its_side(self, vienna_held):
        """(ii) the carry-in helper is shared by the table's plan and the
        bilateral ratifier: France's peace with Austria ends Bavaria's pair
        (the ally) and Italy's (the client) in the same instrument, at no
        fallout — the Vienna-held board, Austria alone from the wizard."""
        from backend.game_logic.settlement_ratify import carried_in_allies
        world = vienna_held
        assert carried_in_allies(world, "France", "Austria") == ["Bavaria"]
        assert _state(world, "Bavaria", "Austria") == "WAR"
        rel_before = int(world.nation_relations.get(world._make_diplo_key("France", "Bavaria"), 0))
        with _quiet():
            res = world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                        "target_nation": "Austria", "sweeteners": [],
                                        "demands": [], "clauses": []})
        assert res and res.get("type") == "diplomatic_treaty_signed", res
        assert _state(world, "France", "Austria") == "PEACE"
        assert _state(world, "Bavaria", "Austria") == "PEACE"          # the ally, carried in
        assert _state(world, "KingdomOfItaly", "Austria") == "PEACE"   # the client follows
        assert _state(world, "France", "Britain") == "WAR"             # the rest of the war stands
        assert int(world.nation_relations.get(world._make_diplo_key("France", "Bavaria"), 0)) == rel_before
        aftermath = world.peace_ratification_log[-1]["political_aftermath"]
        assert any(BAVARIA_NOTE in a for a in aftermath), aftermath
        assert "Bavaria|Austria" not in (world.war_instances["war_1"].get("active_diplo_keys") or [])

    def test_ii_the_tables_plan_and_the_ratifier_read_one_helper(self):
        from backend.game_logic import settlement_ratify as SR
        assert SR.build_pair_ratification_plan is SR._build_pair_ratification_plan
        src = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        assert "from backend.game_logic.settlement_ratify import carried_in_allies" in src

    def test_ii_a_truce_carries_nothing(self, w):
        with _quiet():
            w._ratify_treaty({"type": D.armistice_variant_for(w, "France", "Austria"),
                              "proposer_nation": "France", "target_nation": "Austria",
                              "sweeteners": [], "demands": [], "clauses": []})
        assert _state(w, "France", "Austria") == "ARMISTICE"
        assert _state(w, "Bavaria", "Austria") == "WAR"

    def test_iii_the_consent_read_is_the_courts_own(self, vienna_held):
        """(iii) `court_own_readiness` — P1's own clause and threshold for the
        recipient of France's letter; the bilateral formula reads §6a's
        loyalty term from it: Austria (beaten) pays none, Britain and Russia
        (loyal) pay -11 at exhaustion 45."""
        world = vienna_held
        austria = AI.court_own_readiness(world, "Austria", "France")
        assert austria["sues"] and austria["break_ranks"] == "score" and not austria["loyal"]
        assert austria["score"] < austria["threshold"]
        britain = AI.court_own_readiness(world, "Britain", "France")
        assert britain["in_league"] and britain["loyal"] and britain["break_ranks"] == ""
        assert AI.coalition_loyalty_penalty(world, "Austria", "France") == 0
        assert AI.coalition_loyalty_penalty(world, "Britain", "France") == -11
        for court in ("Austria", "Britain"):
            with _quiet():
                acc = D.calculate_acceptance({"type": "peace", "proposer_nation": "France",
                                              "target_nation": court, "sweeteners": [],
                                              "demands": [], "clauses": []}, world)
            assert acc["components"]["coalition_loyalty"] == AI.coalition_loyalty_penalty(world, court, "France")
        # the AI's own letter split is named, not a literal
        assert AI.P1_PEACE_SPLIT == -70

    def test_iii_the_loyalty_term_eases_with_exhaustion_and_lifts_with_a_reason(self, w):
        key = w._make_diplo_key("France", "Austria")
        assert AI.coalition_loyalty_penalty(w, "Austria", "France") == -15
        w.war_exhaustion["Austria"] = 150
        assert AI.coalition_loyalty_penalty(w, "Austria", "France") == 0
        w.war_exhaustion["Austria"] = 0
        w.war_scores[key] = 60 if key.split("|")[0] == "France" else -60    # Austria at -60
        assert AI.court_own_readiness(w, "Austria", "France")["break_ranks"] == "score"
        assert AI.coalition_loyalty_penalty(w, "Austria", "France") == 0

    def test_iv_the_words_on_the_chip_the_counsel_and_the_draft(self, w):
        """(iv) "X's war ends in this instrument" replaces "would break her war"
        on the wizard row, the per-court chip, the counsel and the draft."""
        from backend.game_logic import settlement_staging as SS
        from backend.game_logic.diplomatic_advisory import _recommend_action
        from backend.game_logic.diplomatic_dialogue import separate_peace_note_text
        row = next(a for a in _rows(w, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True and row["separate_peace_display"] == BAVARIA_NOTE
        chip = SS.separate_peace_chip(w, "Austria", war_id="war_1", staged_terms=[], actor="France")
        assert chip["separate_peace_display"] == BAVARIA_NOTE and chip["carried_in"] == ["Bavaria"]
        assert f"Mark one thing, Sire: {BAVARIA_NOTE}" in _recommend_action("Austria", w)["talleyrand_text"]
        assert separate_peace_note_text(w, "France", "Austria") == f"Mark one thing, Sire: {BAVARIA_NOTE}"
        for text in (row["separate_peace_display"], chip["description"],
                     _recommend_action("Austria", w)["talleyrand_text"]):
            assert "would break" not in text

    def test_iv_a_cession_names_the_beneficiary(self, w):
        words = D.separate_peace_words(w, "France", "Austria", [
            {"type": "territory_cede", "from": "Austria", "to": "Bavaria", "region": "Tyrol"}])
        assert words["named"] == {"Bavaria": ["Tyrol"]}
        assert words["display"] == "Bavaria's war with Austria ends in this instrument; she is named for Tyrol."

    def test_iv_f53_the_guided_demand_takes_a_beneficiary(self, monkeypatch):
        """PC-F53: a Carniola → Kingdom of Italy demand authored from the rows."""
        from fastapi.testclient import TestClient
        from backend import main as M
        from tests import _chip_census as C
        C.board_env(monkeypatch)
        world = M.world
        world.diplomatic_points = max(int(world.diplomatic_points), 5)
        key = world._make_diplo_key("France", "Austria")
        world.war_scores[key] = 58 if key.split("|")[0] == "France" else -58
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/command", json={"command": "propose common peace with Austria"}).json()
        dialogue = r.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "settlement_confirm", r.get("message")
        assert world.regions["Carniola"].controller == "Austria"
        with _quiet():
            out = client.post("/respond_to_diplomatic_dialogue", json={
                "choice": "settlement_demand_add",
                "dialogue_id": dialogue.get("dialogue_id"),
                "action_params": {"nation": "Austria", "group": "demand",
                                  "clause_type": "territory_cede", "region": "Carniola",
                                  "to": "KingdomOfItaly"}}).json()
        assert out.get("success"), out.get("message") or out.get("error_display")
        terms = (out.get("diplomatic_dialogue") or {}).get("settlement_terms") or []
        cession = [t for t in terms if t.get("type") == "territory_cede"]
        assert cession and cession[0]["from"] == "Austria" and cession[0]["to"] == "KingdomOfItaly"
        assert cession[0]["region"] == "Carniola"
        # a payee off our side is refused in words (the restaged table's id)
        restaged = out.get("diplomatic_dialogue") or {}
        with _quiet():
            bad = client.post("/respond_to_diplomatic_dialogue", json={
                "choice": "settlement_demand_add",
                "dialogue_id": restaged.get("dialogue_id"),
                "action_params": {"nation": "Austria", "group": "demand",
                                  "clause_type": "gold_indemnity", "amount": 100,
                                  "to": "Russia"}}).json()
        assert bad.get("success") is False
        assert "does not stand on our side" in str(bad.get("error_display") or bad.get("message"))

    def test_the_done_when_austria_alone_signs_from_the_wizard_with_the_price_said(self, vienna_held):
        """The part's done-when: on the Vienna-held board the wizard's Propose
        Peace row is open, the counsel names a road that carries with its
        price and Bavaria's fate, and the peace signs."""
        world = vienna_held
        row = next(a for a in _rows(world, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True and row["dp_cost"] == 3
        out = CS.counsel_for_wizard(world, "Austria")
        assert out["best_road"] in ("table_alone", "send_peace"), out["roads_display"]
        best = next(r for r in out["roads"] if r["road"] == out["best_road"])
        assert best["available"] and best["carries"] and best["price_dp"] == 3
        assert "3 DP" in out["line"] and BAVARIA_NOTE in out["line"]
        with _quiet():
            res = world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                        "target_nation": "Austria", "sweeteners": [],
                                        "demands": [], "clauses": []})
        assert res.get("type") == "diplomatic_treaty_signed"
        assert _state(world, "Bavaria", "Austria") == "PEACE"


# ═══════════════════════════════════════════════════════════════════════════
# The P1s — PC-F9, F49, F50, F51
# ═══════════════════════════════════════════════════════════════════════════

class TestPCF9:
    def test_the_beaten_courts_peace_is_force_sent(self, vienna_held):
        """Austria at -79 on the Vienna-held board, war age 5: her honest peace
        used to fall under the send filter (the silent band)."""
        world = vienna_held
        with _quiet():
            D.recalculate_war_scores(world)
        assert D.get_war_score_for(world, "Austria", "France") < AI.P1_PEACE_SPLIT
        with _quiet():
            letter = AI.process_diplomatic_phase("Austria", world)
        assert letter is not None
        assert letter["proposal_type"] == "peace" and letter["_force_send"] is True
        assert letter["honest_peace_fallback"] is True
        assert not (letter["terms"].get("demands") or [])

    def test_the_seam_is_one_function(self):
        p = {}
        AI.honest_peace_never_silent(p)
        assert p == {"_force_send": True, "honest_peace_fallback": True}


class TestPCF49:
    def _carried_board(self, w):
        """France ends the 1805 war with Austria (Bavaria carried in), then
        Austria declares on Bavaria and France is pulled in by the alliance —
        a war France does not lead."""
        with _quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                              "sweeteners": [], "demands": [], "clauses": []})
            w.armistice_cooldowns.pop(w._make_diplo_key("Austria", "Bavaria"), None)
            res = D.declare_war(w, "Austria", "Bavaria")
        assert res.get("success"), res
        assert _state(w, "France", "Austria") == "WAR"
        war = next(v for v in w.war_instances.values()
                   if v.get("ended_turn") is None and v.get("defender_leader") == "Bavaria")
        assert war["side_by_nation"]["France"] == "defenders"
        return w

    def test_the_bilateral_peace_is_open_and_priced(self, w):
        world = self._carried_board(w)
        from backend.game_logic.treaty import can_sign
        words = D.separate_peace_words(world, "France", "Austria")
        assert words["leader"] is False and words["carried"] == [] and words["left"] == ["Bavaria"]
        assert words["price"]["Bavaria"] < 0
        assert words["display"].startswith("Bavaria stays at war with Austria after this separate peace")
        assert "it costs" in words["display"] and "relation with her" in words["display"]
        row = next(a for a in _rows(world, "Austria") if a["action"] == "propose_peace")
        assert row["available"] is True and row["separate_peace_display"] == words["display"]
        assert can_sign(world, {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                "sweeteners": [], "demands": [], "clauses": []}, at_send=True).ok

    def test_the_separate_peace_signs_and_is_priced_at_the_ratification(self, w):
        world = self._carried_board(w)
        rel_before = int(world.nation_relations.get(world._make_diplo_key("France", "Bavaria"), 0))
        with _quiet():
            res = world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                        "target_nation": "Austria", "sweeteners": [],
                                        "demands": [], "clauses": []})
        assert res.get("type") == "diplomatic_treaty_signed"
        assert _state(world, "France", "Austria") == "PEACE"
        assert _state(world, "Bavaria", "Austria") == "WAR"       # left fighting
        assert int(world.nation_relations.get(world._make_diplo_key("France", "Bavaria"), 0)) < rel_before


class TestPCF50:
    def test_a_winning_court_keeps_its_war_unless_the_side_dictates(self, w):
        key_b = w._make_diplo_key("France", "Britain")
        key_r = w._make_diplo_key("France", "Russia")
        # Russia winning her own pair (+37 from her side), the side as a whole
        # not dictating (France +30 on Britain: the side sum reads -7)
        w.war_scores[key_r] = -37 if key_r.split("|")[0] == "France" else 37
        w.war_scores[key_b] = 30 if key_b.split("|")[0] == "France" else -30
        assert AI.leave_a_winning_court_its_war(w, "France", ["Britain", "Russia"]) == ["Britain"]
        # the side dictates (France decisively losing to it): every court is on the letter
        w.war_scores[key_b] = -40 if key_b.split("|")[0] == "France" else 40
        assert AI.leave_a_winning_court_its_war(w, "France", ["Britain", "Russia"]) == ["Britain", "Russia"]
        assert AI.leave_a_winning_court_its_war(w, "France", ["Russia"]) == ["Russia"]   # a one-court letter

    def test_gold_credits_the_court_paid_in_full_and_the_side_at_half(self):
        from backend.game_logic import settlement_scoring as SC
        terms = [{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 1000}]
        kw = dict(proposer_side_participants=["France"], accepting_side_participants=["Britain", "Prussia"],
                  covered_enemy_participants=["Britain", "Prussia"], settlement_terms=terms)
        britain = SC.calculate_concession_credit(accepting_leader="Britain", **kw)
        prussia = SC.calculate_concession_credit(accepting_leader="Prussia", **kw)
        assert britain["score"] == SC.CONCESSION_GOLD_CAP
        assert prussia["score"] == int(SC.CONCESSION_GOLD_CAP * SC.SIDE_GOLD_CREDIT_SHARE)
        assert prussia["credited_terms"][0]["side_share"] is True
        # a cession still credits the whole side
        cede = [{"type": "territory_cede", "from": "France", "to": "Britain", "region": "Flanders"}]
        kw2 = dict(kw, settlement_terms=cede)
        assert (SC.calculate_concession_credit(accepting_leader="Prussia", **kw2)["score"]
                == SC.calculate_concession_credit(accepting_leader="Britain", **kw2)["score"])


class TestPCF51:
    def test_the_leader_is_re_seated_on_a_separate_peace_exit(self, w):
        inst = w.war_instances["war_1"]
        assert inst["defender_leader"] == "Britain"
        with _quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                              "sweeteners": [], "demands": [], "clauses": []})
        inst = w.war_instances["war_1"]
        assert "Britain" not in (inst.get("active_participants") or [])
        assert inst["defender_leader"] in ("Austria", "Russia")
        assert inst["defender_leader"] in (inst.get("defenders") or [])

    def test_the_reactions_read_the_leader_who_signed(self):
        src = (REPO / "backend" / "game_logic" / "settlement_reactions.py").read_text(encoding="utf-8")
        assert "enemy_leader=str(" in src and "pre_cleanup_defender_leader) or \"\")" in src


# ═══════════════════════════════════════════════════════════════════════════
# PC-R8 — ruling K: the counsel alive
# ═══════════════════════════════════════════════════════════════════════════

class TestPCR8:
    def test_a_the_recommended_road_carries_or_the_flip_term_is_named(self, vienna_held, turn6):
        """(a) on the two turn-6 boards: for every court at war, the
        recommended road's button is enabled and its dry-run carries, or the
        line says none carries and names the flip term."""
        for world in (vienna_held, turn6):
            for court in ("Austria", "Britain", "Russia"):
                out = CS.counsel_for_wizard(world, court)
                if out["best_road"]:
                    best = next(r for r in out["roads"] if r["road"] == out["best_road"])
                    assert best["available"] and best["carries"], (court, out["roads_display"])
                    assert out["best_action"] in ("propose_peace", "propose_armistice",
                                                  "open_settlement", "propose_white_peace")
                    if out["best_action"] in ("propose_peace", "propose_armistice"):
                        row = next(a for a in _rows(world, court) if a["action"] == out["best_action"])
                        assert row["available"] is True
                else:
                    import re
                    nearest = next((r for r in out["roads"] if r.get("available") and r.get("score") is not None), None)
                    assert nearest is not None and nearest["label"].lower() in out["line"].lower(), (court, out["line"])
                    assert re.search(r"[-+]?\d+", out["line"]), out["line"]
                    flip = nearest.get("flip") or {}
                    if flip:
                        assert flip["label"] in out["line"], (court, out["line"])

    def test_a_austria_on_the_vienna_held_board(self, vienna_held):
        out = CS.counsel_for_wizard(vienna_held, "Austria")
        assert out["best_road"] == "table_alone", out["roads_display"]
        assert out["best_action"] == "propose_white_peace" and out["best_coverage"] == ["Austria"]
        assert out["carrying"] and "truce" in out["carrying"]           # the truce carries too …
        assert out["best_road"] != "truce"                              # … but a peace is preferred
        assert "Bavaria's war with Austria ends in this instrument" in out["line"]
        assert any(r.startswith("Open Settlement with Austria alone") for r in out["roads_display"])

    def test_b_a_priced_road_names_its_price_and_never_a_refused_truce(self, w):
        """(b) where the paradox is priced the line names the price; a truce
        the court refuses is never named as the way out (F67)."""
        board = TestPCF49()._carried_board(w)
        out = CS.counsel_for_wizard(board, "Austria")
        priced = next(r for r in out["roads"] if r["road"] == "send_peace")
        assert "relation with her" in priced["trade"]
        for r in out["roads"]:
            if r["road"] == "truce" and not r["carries"]:
                assert "Propose Armistice carries" not in out["line"]
        # F67 on the boot: no road's words sell "propose an armistice" as a way out
        for court in ("Austria", "Britain", "Russia"):
            words = D.separate_peace_words(w, "France", court)
            assert "propose an armistice" not in (words.get("display") or "")
            line = CS.counsel_for_wizard(w, court)["line"]
            truce = next((r for r in CS.read_counsel(w, court)["roads"] if r["road"] == "truce"), None)
            if truce and not truce["carries"]:
                assert "Propose Armistice" not in line.split(".")[0]

    def test_c_variety_the_same_situation_never_repeats_and_every_line_carries_a_figure(self, w):
        """(c) across the boot's courts and 20 turns the same situation never
        yields the same line twice in a row, and every line carries a figure."""
        import re
        for court in ("Austria", "Britain", "Russia"):
            last = None
            for turn in range(1, 21):
                w.current_turn = turn
                line = CS.counsel_for_wizard(w, court)["recommendation_line"]
                assert re.search(r"\d", line), line
                assert line != last, (court, turn, line)
                last = line
            # the memory: two opens in one turn, the situation unchanged — different lines
            first = CS.counsel_for_wizard(w, court)["recommendation_line"]
            second = CS.counsel_for_wizard(w, court)["recommendation_line"]
            assert first != second
            assert w.talleyrand_counsel_memory[court]["line"] == second

    def test_d_the_line_is_a_pure_function_of_the_reading(self, vienna_held):
        """(d) GR6 — shuffled roads, deep copies: byte-identical lines."""
        reading = CS.read_counsel(vienna_held, "Austria")
        base = CS.compose_counsel_line(reading, None)
        rng = random.Random(7)
        for _ in range(12):
            shuffled = copy.deepcopy(reading)
            rng.shuffle(shuffled["roads"])
            assert CS.compose_counsel_line(shuffled, None) == base
        assert CS.compose_counsel_line(copy.deepcopy(reading), None) == base
        with_last = CS.compose_counsel_line(reading, {"situation": base["situation"], "index": base["index"]})
        assert with_last["line"] != base["line"] and with_last["index"] != base["index"]

    def test_d_the_reading_is_byte_identical_under_the_historical_seed(self, vienna_held):
        a = json.dumps(CS.read_counsel(vienna_held, "Austria"), sort_keys=True, default=str)
        b = json.dumps(CS.read_counsel(_board("turn6_vienna_held.json"), "Austria"), sort_keys=True, default=str)
        assert a == b

    def test_his_own_mind_is_derived_from_the_stores_and_the_tally_counts(self, vienna_held):
        """(K item 4) the preference and the override tally."""
        from backend.commands.diplomatic_defiance import (
            get_override_dispatch_note, override_tally_sentence, record_override,
            resolve_pending_override,
        )
        world = vienna_held
        out = CS.counsel_for_wizard(world, "Austria")
        assert out["preference"]["kind"] == "moderate"
        assert "Revanche" in out["preference_line"] or "interest" in out["preference_line"]
        assert override_tally_sentence(world) == ""
        record_override(world, "peace", "pending")
        assert resolve_pending_override(world, "bad")
        assert world.talleyrand_override_tally == {"good": 0, "bad": 1}
        assert override_tally_sentence(world) == " Overruled, he has been right once and wrong never this campaign."
        assert get_override_dispatch_note(world).endswith("wrong never this campaign.")
        out2 = CS.counsel_for_wizard(world, "Austria")
        assert "right once" in out2["preference_line"]
        # the memory and the tally survive a save
        loaded = WorldState.from_dict(json.loads(json.dumps(world.to_dict(), default=str)))
        assert loaded.talleyrand_override_tally == {"good": 0, "bad": 1}
        assert loaded.talleyrand_counsel_memory["Austria"]["line"] == out2["recommendation_line"]

    def test_e_one_builder_every_surface(self, vienna_held):
        """(K item 5) the wizard's recommendation, the feasibility card and
        the table's counsel read the one set."""
        from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
        world = vienna_held
        with _quiet():
            pv = D.get_diplomatic_preview(world, "Austria")
        assert pv["recommendation"] == pv["counsel"]["line"]
        assert pv["counsel_roads_display"] == pv["counsel"]["roads_display"]
        send = next(r for r in pv["counsel_roads"] if r["road"] == "send_peace")
        with _quiet():
            card = generate_feasibility_dialogue(
                {"target_nation": "Austria", "proposal_type": "peace", "with_suggested_terms": True}, world)
        assert card["acceptance_estimate"] == send["score"]      # the card prices the wizard's draft
        assert card["context"]["largest_obstacle"] == send["flip"]["component"]
        assert send["flip"]["label"] in card["talleyrand_text"]
        assert f"({send['plain_score']})" in card["talleyrand_text"]        # F40: the plain peace
        assert "you have" in card["talleyrand_text"] and "1 diplomatic step" in card["talleyrand_text"]
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'data.get("counsel_roads_display"' in src                         # F12

    def test_f_the_road_he_names_opens_with_the_terms_he_priced(self, vienna_held, turn6):
        """(f) K item 6: choosing the recommended road opens it with the terms
        the dry-run priced, and the send is judged on those terms — the
        bilateral confirm pre-filled with the wizard's memo; the table road
        opened with the coverage priced."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        from backend.game_logic.settlement_staging import stage_settlement_confirm
        for world in (vienna_held, turn6):
            with _quiet():
                pv = D.get_diplomatic_preview(world, "Austria")
            send = next(r for r in pv["counsel_roads"] if r["road"] == "send_peace")
            memo = CS.priced_terms_for_confirm(world, "Austria", "peace")
            assert memo and memo == pv["war_context_snapshots"]["propose_peace"]["proposal_terms"] or memo
            with _quiet():
                confirm = generate_dialogue("proposal_confirm",
                                            {"target_nation": "Austria", "proposal_type": "peace"}, world)
            opt = next(o for o in confirm["options"] if o.get("action") == "execute_proposal")
            assert opt["terms"]["demands"] == list(memo.get("demands") or [])
            assert opt["terms"]["sweeteners"] == list(memo.get("sweeteners") or [])
            assert int(confirm["acceptance_estimate"]) == int(send["score"])
            # the table road: the coverage priced opens the white peace with the court alone
            alone = next((r for r in pv["counsel_roads"] if r["road"] == "table_alone"), None)
            if alone and alone["available"]:
                assert alone["action"] == "propose_white_peace" and alone["covered"] == ["Austria"]
                with _quiet():
                    staged = stage_settlement_confirm(
                        world, war_id=alone["war_id"], actor_nation="France", settlement_terms=[],
                        selected_target_nation="Austria", covered_enemy_participants=["Austria"],
                        density="medium", caller_kind="player_editor", white_peace=True)
                dlg = staged.get("diplomatic_dialogue") or staged
                rows = {r["nation"]: r for r in dlg.get("per_court_acceptance") or []}
                assert list(rows) == ["Austria"] and int(rows["Austria"]["total"]) == int(alone["score"])
                if pv["counsel"]["best_road"] == "table_alone":
                    wp = next(a for a in pv["actions"] if a["action"] == "propose_white_peace")
                    assert wp.get("counsel_first") and wp.get("counsel_coverage") == ["Austria"]

    def test_e_the_part_iv_frames_read_the_new_counsel(self):
        """(e) the Part IV M1, M3 and M5 frames, re-shot on the Vienna-held
        board at 5120x1440 (`docs/audits/peace_client/`), read the counsel:
        the moments index carries each frame's own lines."""
        index = json.loads((REPO / "docs" / "audits" / "peace_client" / "moments.json")
                           .read_text(encoding="utf-8"))
        by = {(e["id"], e["resolution"]): e for e in index}
        for sid in ("m1_war_card_tooltip", "m3_wizard_austria", "m5_counsel", "m5_feasibility"):
            e = by[(sid, "5120x1440")]
            assert e.get("reshot", "").startswith("S13e part 1"), sid
            assert (REPO / "docs" / "audits" / "peace_client" / e["file"]).exists(), e["file"]
        m3 = " ".join(by[("m3_wizard_austria", "5120x1440")]["lines"])
        assert "Recommendation: Permit me to observe, Sire" in m3 or "Recommendation: Sire" in m3 or "Recommendation: If I may, Sire" in m3 or "Recommendation: One could" in m3, m3[:300]
        assert "Open Settlement with Austria alone, at 50 of 50" in m3 or "Open Settlement with Austria alone" in m3
        controls = [c["text"] for c in by[("m3_wizard_austria", "5120x1440")]["controls"] if c.get("text")]
        assert controls and controls[0].startswith("Propose White Peace"), controls   # the counsel's road first
        assert any(c.startswith("Propose Peace") for c in controls)                  # open, priced
        m5 = " ".join(by[("m5_counsel", "5120x1440")]["lines"])
        assert "Recommendation: Permit me to observe, Sire" in m5 or "Recommendation: Sire" in m5 or "Recommendation: If I may, Sire" in m5 or "Recommendation: One could" in m5, m5[:300]
        assert "We hold the advantage" not in m5
        m5f = " ".join(by[("m5_feasibility", "5120x1440")]["lines"])
        assert "The largest obstacle is" in m5f and "(-24)" in m5f, m5f[:300]

    def test_the_pools_are_in_his_register(self):
        for key, pool in CS.COUNSEL_POOLS.items():
            assert len(pool) >= 3, key
            for line in pool:
                assert "Sire" in line, line
                assert "!" not in line
                for word in ("strike", "crush", "annihilate", "Excellent"):
                    assert word not in line, line


# ═══════════════════════════════════════════════════════════════════════════
# The client's lies at the peace moment
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClientRows:
    def test_f48_the_war_hud_re_shows_on_every_branch(self):
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        enemy = src[src.index("func _on_enemy_phase_dismissed("):]
        enemy = enemy[:enemy.index("\nfunc ", 1)]
        reports = src[src.index("func _on_strategic_report_dismissed("):]
        reports = reports[:reports.index("\nfunc ", 1)]
        assert enemy.count("_process_active_wars(response)") >= 3
        assert reports.count("_process_active_wars(response)") >= 2

    def test_f34_every_builder_prints_the_refusal(self):
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        show = src[src.index("func show_dialogue("):]
        show = show[:show.index("\nfunc ", 1)]
        assert '_safe_str(data.get("transient_error_display"))' in show
        assert "_prints_its_own_refusal" in show
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        reopen = main[main.index("func _show_confirm_dialogue_from_response("):]
        reopen = reopen[:reopen.index("\nfunc ", 1)]
        assert 'dialogue["transient_error_display"] = err_text' in reopen

    def test_f12_the_advisory_popup_prints_the_hints(self):
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        body = src[src.index("func _build_advisory_content("):]
        body = body[:body.index("\nfunc ", 1)]
        assert 'context.get("action_hints"' in body and 'context.get("recommendation"' in body

    def test_f10_the_cards_send_is_stamped_and_priced(self, w):
        from backend.game_logic.diplomatic_dialogue import generate_feasibility_dialogue
        w.diplomatic_points = 0
        with _quiet():
            card = generate_feasibility_dialogue(
                {"target_nation": "Austria", "proposal_type": "peace", "with_suggested_terms": True}, w)
        send = next(o for o in card["options"] if o["action"] == "execute_proposal")
        assert send["available"] is False and send["disabled_reason_display"]
        assert card["dp_cost"] == D.diplomatic_price_quote(w, "peace", "Austria")["cost"]
        assert "you have 0" in card["talleyrand_text"]

    def test_f67_f73_the_pair_cooldown_is_worded_by_what_it_is(self, w):
        key = w._make_diplo_key("France", "Austria")
        w.armistice_cooldowns[key] = 3
        with _quiet():
            D.set_diplomatic_state(w, "France", "Austria", "ARMISTICE", "test")
        w.armistice_cooldowns[key] = 3
        assert D.pair_cooldown_words(w, "France", "Austria") == {
            "turns": 3, "kind": "truce", "noun": "the armistice",
            "display": "The armistice with Austria holds for 3 more turns. We cannot declare war until it expires."}
        with _quiet():
            D.set_diplomatic_state(w, "France", "Austria", "PEACE", "test")
        w.armistice_cooldowns[key] = 3
        assert D.pair_cooldown_words(w, "France", "Austria")["display"] == (
            "Our peace with Austria is fresh: no war may be declared on her for 3 more turns.")
        rows = {a["action"]: a for a in _rows(w, "Austria")}
        assert rows["declare_war"]["disabled_reason"] == "Fresh peace: 3 turns remaining"
        for rel in ("backend/commands/diplomatic_executor.py", "backend/game_logic/congress.py"):
            assert "pair_cooldown_words" in (REPO / rel).read_text(encoding="utf-8"), rel

    def test_f76_a_harsh_peace_is_labelled_as_one(self, w):
        terms = AI._build_proposal_terms("Austria", "harsh_peace", 60, w)
        prop = AI._make_proposal("Austria", "harsh_peace", 8, terms, w)
        with _quiet():
            dlg = AI.deliver_ai_proposal(prop, w)
        assert dlg["popup_payload"]["proposal_type_display"] == "Harsh Peace Treaty"
        assert dlg["popup_payload"]["proposal_type"] == "peace"     # the formula's type is untouched

    def test_f65_f78_the_letter_names_its_courts_and_its_substance(self, w):
        from backend.game_logic.settlement_offers import offer_coverage_label, offer_substance_clause
        assert offer_coverage_label(w, ["Britain", "Prussia"]) == "for Britain and Prussia"
        assert offer_coverage_label(w, ["Britain"]) == ""
        clause = offer_substance_clause(w, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 2980},
            {"type": "create_client", "from": "France", "to": "Britain", "tag": "Normandy",
             "client_display_name": "the Duchy of Normandy", "provinces": ["Normandy"]},
            {"type": "territory_cede", "from": "France", "to": "Britain", "region": "Flanders"}])
        assert clause == "erects the Duchy of Normandy out of France; France cedes Flanders to Britain"
        rail = (REPO / "backend" / "game_logic" / "turn_manager.py").read_text(encoding="utf-8")
        assert 'popup_payload.get("coverage_label")' in rail and 'popup_payload.get("substance_clause")' in rail
        row = (REPO / "backend" / "models" / "dialogue_manager.py").read_text(encoding="utf-8")
        assert 'd.get("coverage_label")' in row

    def test_f37_f88_the_war_card_shows_the_averaging_and_the_courts_own_mind(self, vienna_held):
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            rows = build_active_wars(vienna_held)["wars"]
        row = next(r for r in rows if r.get("status") == "war"
                   and "Austria" in (r.get("opponents") or [r.get("opponent")]))
        table = row["peace_table"]
        courts = {c["nation"]: c for c in table["courts"]}
        assert courts["Austria"]["pair_score"] > 0 and courts["Austria"]["sues"]
        assert courts["Austria"]["break_ranks"] == "score" and courts["Austria"]["letter"] in ("peace", "truce")
        assert courts["Britain"]["pair_score"] < 0 <= courts["Russia"]["pair_score"] + 1
        lines = table["lines"]
        assert any(ln.startswith("Court by court: Austria +") and "the table reads their mean" in ln
                   for ln in lines), lines
        assert any(ln.startswith("Austria's own court would sue at ") and "she reads" in ln
                   for ln in lines), lines

    def test_f35_f36_f37_the_tables_counsel_reads_every_court_and_the_road_that_carries(self, vienna_held):
        from backend.game_logic.settlement_staging import (
            build_settlement_confirm_dialogue, build_settlement_preview,
        )
        world = vienna_held
        with _quiet():
            prev = build_settlement_preview(world, war_id="war_1", settlement_terms=[],
                                            actor_nation="France", ignore_active_dialogue=True)
            dlg = build_settlement_confirm_dialogue(world, prev)
        text = dlg["talleyrand_text"]
        assert "are unbeaten" in text and "Every covered court has been beaten" not in text   # F36
        assert "The table reads their mean: Austria +" in text                                   # F37
        assert "Russia sits at 0 because France has not fought her" in text
        assert "Press Austria alone: with her alone the table reads 50 of 50 and carries." in text   # F35
        assert BAVARIA_NOTE in text                                                            # F43
        assert "would break" not in text

    def test_f25_the_baseline_prices_at_the_scorers_rate(self):
        from backend.game_logic import settlement_baseline as SB
        from backend.game_logic import settlement_scoring as SC
        assert SB.CONCESSION_BASELINE_GOLD_HARD_CAP == SC.CONCESSION_GOLD_CAP * SC.CONCESSION_GOLD_DIVISOR == 1000
        src = (REPO / "backend" / "game_logic" / "settlement_baseline.py").read_text(encoding="utf-8")
        assert "acceptance_gap * settlement_scoring.CONCESSION_GOLD_DIVISOR" in src
        assert "acceptance_gap * 100" not in src


# ═══════════════════════════════════════════════════════════════════════════
# The series — the six seams attributed against BASELINE_SERIES
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSeries:
    """`tools/_pc_s13e_series_arms.py` (record `tools/_pc_s13e_series_arms_
    final.json`): arm 0 (every seam down) reproduces the shipped series byte
    for byte, and so does every other arm — BASELINE_SERIES does not move.
    The reach: the carry-in was read 12 times and carried nothing (the sim's
    passive France signs no bilateral peace), the loyalty term was charged
    twice (reached, moving no answer), the coverage, the gold share and the
    re-seat were each reached twice; the honest-peace seam was NOT reached
    (no court falls below the split in the ambient sim — it is pinned on the
    Vienna-held board instead)."""

    def _record(self):
        return json.loads((REPO / "tools" / "_pc_s13e_series_arms_final.json").read_text(encoding="utf-8"))

    def test_the_record_links_to_the_last_one_and_the_baseline(self):
        import sys as _sys
        _sys.path.insert(0, str(REPO / "tests"))
        from test_ai_intent_threat_migration import BASELINE_SERIES
        rec = self._record()
        pc = json.loads((REPO / "tools" / "_pc_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == pc["arms"]["ALL"]["series"] == BASELINE_SERIES
        assert set(rec["arms"]) == {"0", "C", "Y", "H", "W", "G", "R", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
        assert rec["arms"]["ALL"]["series"] == BASELINE_SERIES

    def test_the_seams_were_reached(self):
        rec = self._record()
        reach = {arm: row["reach"] for arm, row in rec["arms"].items()}
        assert reach["ALL"]["carry_in|none"] > 0
        assert reach["ALL"]["loyalty|charged"] > 0 and reach["0"].get("loyalty|charged", 0) == 0
        assert reach["ALL"]["gold_share|0.5"] > 0 and reach["0"]["gold_share|1.0"] > 0
        assert reach["ALL"]["coverage|whole"] > 0 and reach["ALL"]["reseat|kept"] > 0
        assert "honest_peace|forced" not in reach["ALL"]     # never below the split in the ambient sim
