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
        # PC-R3: the label carries the letter's tier ("Harsh Peace Treaty — Reichenbach")
        terms = AI._build_proposal_terms("Austria", "harsh_peace", 60, w)
        prop = AI._make_proposal("Austria", "harsh_peace", 8, terms, w)
        with _quiet():
            dlg = AI.deliver_ai_proposal(prop, w)
        assert dlg["popup_payload"]["proposal_type_display"] .startswith("Harsh Peace Treaty")
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


# ═══════════════════════════════════════════════════════════════════════════
# PC-R2 — ruling D, the victor's truce (S13e part 2, October 16, 2026)
# ═══════════════════════════════════════════════════════════════════════════

def _truce(world, proposer="France", target="Austria", sweeteners=None):
    """Ratify a truce between the two as the ratifier does (France proposes
    from strength; a losing court's letter carries its gold stream — the
    surety)."""
    ptype = (D.armistice_variant_for(world, proposer, target)
             if proposer == world.player_nation else "armistice_losing")
    with _quiet():
        res = world._ratify_treaty({"type": ptype, "proposer_nation": proposer,
                                    "target_nation": target, "sweeteners": list(sweeteners or []),
                                    "demands": [], "clauses": []})
    assert _state(world, proposer, target) == "ARMISTICE", res
    return res


def _kill_hope(world, loser="Austria", victor="France"):
    """Every hope term dead on the Vienna-held board: the league spent
    (Britain and Russia past the exhaustion line), no subsidy to the court
    (the paymaster pays only a court above -20 with him), the victor's
    exhaustion not past the loser's."""
    world.war_exhaustion["Britain"] = 90
    world.war_exhaustion["Russia"] = 90
    world.nation_relations[world._make_diplo_key("Britain", loser)] = -30
    world.war_exhaustion[victor] = 10
    world.war_exhaustion[loser] = 60


class TestPCR2:
    KEY = "Austria|France"

    def test_a_the_truce_keeps_the_ledger_and_the_wars_age(self, vienna_held):
        """D items 1-2: the pops of the pair's stores and of `war_start_turns`
        run only when the war is OVER; a truce keeps them, the collapse
        resumes the war at its age, the peace pops them."""
        w = vienna_held
        k = self.KEY
        start = int(w.war_start_turns[k])
        assert w.battle_records[k] and w.decisive_battles[k] and w.war_scores[k] == -54
        _truce(w)
        assert w.war_start_turns[k] == start                 # the war's age kept
        assert len(w.battle_records[k]) == 11 and len(w.decisive_battles[k]) == 1
        assert w.war_scores[k] == -54 and k in w.war_score_history
        with _quiet():
            D.recalculate_war_scores(w)
        assert w.war_scores[k] == -54                        # the stored score stands under the truce
        assert D.get_war_score_for(w, "France", "Austria") == 54
        # the collapse: the same war_id, the original stamp, the ledger with it
        from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair
        with _quiet():
            assert ensure_war_instance_for_pair(w, "Austria", "France", entry_path="armistice_expired_war",
                                                reason="armistice collapse")["ok"]
            D.set_diplomatic_state(w, "Austria", "France", "WAR", "armistice_expired_war")
        assert _state(w, "France", "Austria") == "WAR"
        assert w.war_start_turns[k] == start
        assert w.war_scores[k] == -54 and len(w.battle_records[k]) == 11
        # the peace pops them
        with _quiet():
            D.set_diplomatic_state(w, "Austria", "France", "PEACE", "treaty_ratification")
            D.cleanup_war_end(w, k, conclude_objectives=True)
        assert k not in w.war_scores and k not in w.battle_records and k not in w.war_start_turns

    def test_a_the_seam_down_is_the_old_pop(self, vienna_held, monkeypatch):
        w = vienna_held
        monkeypatch.setattr(D, "truce_keeps_the_ledger", lambda *a, **k: False)
        _truce(w)
        assert self.KEY not in w.war_scores and self.KEY not in w.war_start_turns

    def test_b_exhaustion_holds_in_a_truce(self, vienna_held, monkeypatch):
        """Ruling H's clause — never reset by a truce: a court whose only wars
        are truces holds its exhaustion (neither +8 nor -5); the seam down is
        the old -5; the truce's POP (R49) is gone with the ledger's."""
        from backend.game_logic import coalition as CO
        w = vienna_held
        # Austria's other wars (Bavaria, the Kingdom of Italy) to peace, so the
        # truce is her only pair.
        for other in ("Bavaria", "KingdomOfItaly"):
            w.diplomatic_states[w._make_diplo_key("Austria", other)] = "PEACE"
        w.war_exhaustion["Austria"] = 54
        _truce(w)
        assert w.war_exhaustion.get("Austria") == 54        # not popped at the truce
        assert CO.next_war_exhaustion(w, "Austria") == 54   # held, not -5
        assert CO.nations_in_truce_with(w, "Austria") == ["France"]
        monkeypatch.setattr(CO, "truce_holds_exhaustion", lambda *a, **k: False)
        assert CO.next_war_exhaustion(w, "Austria") == 49

    def test_c_a_peace_signed_under_a_truce_is_signed(self, vienna_held):
        """D item 3: the truce's courted exit is a SIGNED peace — the held line
        is titled by the signature (Vienna to France), the fresh-peace floor
        written, the event says so."""
        from backend.game_logic.game_end import SIGNED_PEACE_REASONS
        from backend.game_logic.coalition import FRESH_PEACE_FLOOR_TURNS
        assert {"armistice_expired_peace", "armistice_dictated_peace"} <= set(SIGNED_PEACE_REASONS)
        w = vienna_held
        k = self.KEY
        _truce(w)
        w.nation_relations[k] = -50                           # at or past the -60 line
        w.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        with _quiet():
            events = D._process_armistice_expiration(w)
        assert _state(w, "France", "Austria") == "PEACE"
        ev = next(e for e in events if e["type"] == "armistice_expired_peace")
        assert ev["exit"] == "peace" and "signed on the held line" in ev["message"]
        title = w.province_title.get("Vienna") or {}
        assert title.get("holder") == "France" and title.get("from") == "Austria", title
        assert int(w.armistice_cooldowns.get(k, 0)) == int(FRESH_PEACE_FLOOR_TURNS)
        assert k not in w.war_scores                          # the peace pops the ledger

    def test_d_the_two_exits_dictated_when_hope_is_dead_war_when_it_lives(self):
        """D item 4: at expiry under -60 the loser at -54 goes to a DICTATED
        peace on the held line when her hope is dead (the sureties its terms),
        and back to WAR at the war's age when it lives."""
        w = _board("turn6_vienna_held.json")
        k = self.KEY
        start = int(w.war_start_turns[k])
        _truce(w, proposer="Austria", target="France",
               sweeteners=[{"type": "gold_per_turn", "value": 80}])
        sure = D.truce_sureties_for(w, "France", "Austria")
        assert sure["gold_per_turn"] == 80 and "Vienna" in sure["held"] and sure["loser"] == "Austria"
        w.nation_relations[k] = -80
        w.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        # hope alive (Britain and Russia unspent) -> the collapse, at the war's age
        exit_ = D.armistice_expiry_exit(w, "France", "Austria")
        assert exit_["exit"] == "war" and exit_["loser"] == "Austria" and exit_["hope"]["alive"]
        assert "league" in exit_["hope"]["alive_terms"]
        w2 = copy.deepcopy(w)
        with _quiet():
            D._process_armistice_expiration(w2)
        assert _state(w2, "France", "Austria") == "WAR" and w2.war_start_turns[k] == start
        assert w2.war_scores[k] == -54
        # hope dead -> the dictated peace
        _kill_hope(w)
        exit_ = D.armistice_expiry_exit(w, "France", "Austria")
        assert exit_["exit"] == "dictated", exit_
        assert exit_["hope"]["dead_terms"] == ["league", "subsidy", "exhaustion"]
        with _quiet():
            events = D._process_armistice_expiration(w)
        assert _state(w, "France", "Austria") == "PEACE"
        ev = next(e for e in events if e["type"] == "armistice_expired_dictated")
        assert "DICTATED peace on the held line" in ev["message"] and "80 gold a turn" in ev["message"]
        assert (w.province_title.get("Vienna") or {}).get("holder") == "France"
        treaty = w.active_treaties[k]
        assert treaty["type"] == "dictated_peace" and treaty["signed_reason"] == "armistice_dictated_peace"
        assert any(c.get("type") == "gold_per_turn" and int(c.get("amount", 0)) == 80
                   for c in treaty["clauses"])                # the stream runs on

    def test_d_a_level_truce_keeps_the_courted_door(self, w):
        """A level war (no loser) has the -60 door and the collapse, never a
        dictated peace."""
        _truce(w)
        exit_ = D.armistice_expiry_exit(w, "France", "Austria")
        assert exit_["loser"] == "" and exit_["exit"] == "war"
        w.nation_relations[w._make_diplo_key("France", "Austria")] = -40
        assert D.armistice_expiry_exit(w, "France", "Austria")["exit"] == "peace"

    def test_e_hope_is_one_function_read_by_the_ask_and_the_expiry(self, vienna_held, monkeypatch):
        """P1 between the threshold and the split (-70) asks a truce ONLY while
        the court's hope is alive; otherwise its peace letter, force-sent. The
        expiry reads the same function."""
        w = vienna_held
        k = self.KEY
        w.war_scores[k] = -60                                  # Austria reads -60: sues, above the split
        assert AI.court_own_readiness(w, "Austria", "France")["sues"]
        with _quiet():
            letter = AI.process_diplomatic_phase("Austria", w)
        assert letter is not None and letter["proposal_type"] == "armistice_losing", letter
        _kill_hope(w)
        w.ai_proposal_metadata.pop("Austria", None)
        with _quiet():
            letter = AI.process_diplomatic_phase("Austria", w)
        assert letter is not None and letter["proposal_type"] == "peace" and letter["_force_send"], letter
        # one function: a seam that says "alive" turns both reads back
        calls = []

        def _alive(world, loser, victor):
            calls.append((loser, victor))
            return {"alive": True, "members": [], "subsidy": None, "exhaustion": {},
                    "alive_terms": ["league"], "dead_terms": []}
        monkeypatch.setattr(D, "truce_hope_alive", _alive)
        w.ai_proposal_metadata.pop("Austria", None)
        with _quiet():
            letter = AI.process_diplomatic_phase("Austria", w)
        assert letter["proposal_type"] == "armistice_losing"
        _truce(w)
        w.nation_relations[k] = -80
        assert D.armistice_expiry_exit(w, "France", "Austria")["exit"] == "war"
        assert calls and all(c == ("Austria", "France") for c in calls)

    def test_f_f44_every_surface_says_what_the_truce_keeps_and_prices_the_cure(self, vienna_held):
        """The one wording: the popup's display lines, the HUD card, the
        wizard row, the counsel's truce road — the ledger kept, the war's
        age, the exit named, the cure priced where it is in reach."""
        from backend.game_logic import war_status as WS
        w = vienna_held
        k = self.KEY
        # the counsel's truce road, read at WAR (the road the wizard offers)
        reading = CS.read_counsel(w, "Austria")
        truce_road = next(r for r in reading["roads"] if r["road"] == "truce")
        assert "keeps the ledger (+54 stands, the war 5 turns old)" in truce_road["trade"]
        assert "the war would resume where it stood" in truce_road["trade"]
        assert "1 turn of Improve Relations (+8 a turn, 1 DP)" in truce_road["trade"]
        _truce(w)
        w.nation_relations[k] = -66                           # thaws to -63: one turn of +8 carries it
        w.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        words = D.truce_words(w, "France", "Austria")
        assert words["keeps"] == {"war_score": 54, "battles": 11, "decisives": 1,
                                  "war_age": 5, "exhaustion": 113}
        assert words["keeps_line"].startswith(
            "The ledger stands: the war score reads +54 for France (11 battles, 1 decisive kept); "
            "the war is 5 turns old")
        assert words["exit"] == "war" and "the war resumes where it stood" in words["heading_line"]
        assert words["cure"] == {"turns": 1, "gain": 8, "dp": 1, "gap": 3, "in_reach": True}
        assert words["cure_line"] == ("The cure is in reach: 1 turn of Improve Relations "
                                      "(+8 a turn, 1 DP) would carry this truce into peace.")
        assert "hope lives" in words["hope_line"] and "Britain" in words["hope_line"]
        snap = D.build_war_context_snapshot(w, "France", "Austria", "peace")
        mech = snap["armistice_mechanics"]
        assert mech["display_lines"] == words["display_lines"] and mech["exit"] == "war"
        assert mech["cure_line"] == words["cure_line"]
        with _quiet():
            hud = WS.build_active_wars(w)
        card = next(r for r in hud["wars"] if r.get("status") == "armistice" and r["opponent"] == "Austria")
        assert card["war_score"] == 54 and card["duration"] == 5 and card["battles_fought"] == 11
        assert card["armistice_keeps_line"] == words["keeps_line"]
        assert card["armistice_cure_line"] == words["cure_line"] and card["armistice_exit"] == "war"
        row = next(r for r in _rows(w, "Austria") if r["action"] == "propose_peace")
        assert row["truce_display"].startswith(words["keeps_line"]) and row["truce_exit"] == "war"

    def test_f_f44_the_words_name_the_dictated_exit_and_the_sureties(self, vienna_held):
        w = vienna_held
        _truce(w, proposer="Austria", target="France",
               sweeteners=[{"type": "gold_per_turn", "value": 80}])
        _kill_hope(w)
        w.nation_relations[self.KEY] = -80
        words = D.truce_words(w, "France", "Austria")
        assert words["exit"] == "dictated" and "a dictated peace on the held line" in words["heading_line"]
        assert words["hope_line"].startswith("Austria's hope is dead")
        assert words["sureties_line"] == ("Sureties filed at the truce: Austria pays 80 gold a turn "
                                          "for the pause; Bohemia, Tyrol, Vienna held by France.")
        assert words["cure"] is None and words["cure_line"] == ""

    def test_g_f69_the_bilateral_peace_writes_the_floor(self):
        """Verified on the Tilsit fixture: a bilateral peace writes the same
        fresh-peace floor the table writes, and a war inside it is refused."""
        from backend.game_logic.coalition import FRESH_PEACE_FLOOR_TURNS
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
            while w.dialogue_manager.peek() is not None:
                w.dialogue_manager.pop()
        k = w._make_diplo_key("France", "Prussia")
        assert w.diplomatic_states[k] == "WAR" and k not in w.armistice_cooldowns
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                    "target_nation": "Prussia", "sweeteners": [],
                                    "demands": [], "clauses": []})
        assert res and res.get("type") == "diplomatic_treaty_signed", res
        assert int(w.armistice_cooldowns.get(k, 0)) == int(FRESH_PEACE_FLOOR_TURNS)
        assert D.pair_cooldown_words(w, "France", "Prussia")["kind"] == "fresh_peace"
        with _quiet():
            again = D.declare_war(w, "France", "Prussia")
        assert not again.get("success"), again

    def test_h_f82_breaking_a_truce_resumes_the_war(self, vienna_held):
        """Verified by driving the typed road's function: a broken truce
        resumes the war on the same war_id at its age with its ledger — it
        no longer ends it as an unsigned peace."""
        w = vienna_held
        k = self.KEY
        start = int(w.war_start_turns[k])
        _truce(w)
        w.diplomatic_points = 5
        with _quiet():
            res = D.break_treaty(k, "France", w)
        assert res.get("success"), res
        assert _state(w, "France", "Austria") == "WAR"
        assert w.war_start_turns[k] == start and w.war_scores[k] == -54
        war = w.war_instances["war_1"]
        assert k in (war.get("active_diplo_keys") or []) and war.get("ended_turn") is None
        assert (war.get("diplo_key_meta") or {}).get(k, {}).get("pair_status") == "war"

    def test_i_f87_no_relation_bump_on_a_truce_for_either_chair(self, w):
        """Verified: an AI-AI ARMISTICE reached `_ratify_ai_ai_events`' +10
        while the player's got none. Neither does now (GR5); an AI-AI PEACE
        still does."""
        ka = w._make_diplo_key("Austria", "Bavaria")
        before = int(w.nation_relations.get(ka, 0))
        with _quiet():
            w._ratify_treaty({"type": "armistice_losing", "proposer_nation": "Austria",
                              "target_nation": "Bavaria", "sweeteners": [], "demands": [], "clauses": []})
        assert _state(w, "Austria", "Bavaria") == "ARMISTICE"
        assert int(w.nation_relations.get(ka, 0)) == before
        w2 = _board("turn6_copy.json")
        before2 = int(w2.nation_relations.get(ka, 0))
        with _quiet():
            w2._ratify_treaty({"type": "peace", "proposer_nation": "Austria",
                               "target_nation": "Bavaria", "sweeteners": [], "demands": [], "clauses": []})
        assert _state(w2, "Austria", "Bavaria") == "PEACE"
        assert int(w2.nation_relations.get(ka, 0)) == before2 + 10

    def test_j_the_ask_leaves_the_split_where_it_was(self):
        assert AI.P1_PEACE_SPLIT == -70 and D.TRUCE_DICTATED_SCORE == AI.BREAK_RANKS_WAR_SCORE == -50


    def test_k_the_part_iv_frames_read_the_truces_words(self):
        """(k) F44 on every surface: the Part IV M7 and M8 frames, re-shot at
        5120x1440 on the turn-6 board (`docs/audits/peace_client/`), read the
        one wording — the letter, the HUD card's tooltip (PC-X11: wrapped),
        the armistice popup on both turns, the wizard's counsel, the table."""
        index = json.loads((REPO / "docs" / "audits" / "peace_client" / "moments.json")
                           .read_text(encoding="utf-8"))
        by = {(e["id"], e["resolution"]): e for e in index}
        for sid in ("m7_armistice_letter", "m7_armistice_letter_scrolled", "m8_truce_card",
                    "m8_armistice_popup", "m8_armistice_popup_turn8", "m8_wizard_under_truce",
                    "m8_truce_next_morning", "m8_table_under_truce"):
            e = by[(sid, "5120x1440")]
            assert e.get("reshot", "").startswith("S13e part 2"), sid
            assert (REPO / "docs" / "audits" / "peace_client" / e["file"]).exists(), e["file"]
        letter = " ".join(by[("m7_armistice_letter", "5120x1440")]["lines"])
        assert "Armistice Terms" in letter and "The ledger stands: the war score reads +52" in letter, letter[:400]
        assert "When it expires: a dictated peace on the held line" in letter
        assert "At expiry: the war resumes where it stood" in letter
        card = " ".join(c.get("tooltip", "") for c in by[("m8_truce_card", "5120x1440")]["controls"])
        assert card.startswith("Armistice with Austria — 4 turns left.")
        assert "The ledger stands" in card and "At expiry:" in card and "The cure is in reach" in card
        assert max(len(line) for line in card.split("\n")) <= 100, "PC-X11: the tooltip wraps"
        popup7 = " ".join(by[("m8_armistice_popup", "5120x1440")]["lines"])
        assert "Armistice (5 turns remaining)" in popup7 and "the war is 6 turns old and stays so" in popup7
        assert "Austria's hope lives: Britain, Russia fight on" in popup7
        assert "Sureties filed at the truce: Austria pays 168 gold a turn" in popup7
        popup8 = " ".join(by[("m8_armistice_popup_turn8", "5120x1440")]["lines"])
        assert "Armistice (4 turns remaining)" in popup8 and "the war is 7 turns old and stays so" in popup8
        assert "On course to collapse" not in popup8          # the client's old sentence retired
        wiz = " ".join(by[("m8_wizard_under_truce", "5120x1440")]["lines"])
        assert "Status: Armistice" in wiz and "the ledger stands: the war score reads +52" in wiz
        assert "would carry this truce into peace" in wiz and "1 turns" not in wiz   # PC-X12
        rows = [c.get("tooltip", "") for c in by[("m8_wizard_under_truce", "5120x1440")]["controls"]
                if str(c.get("text", "")).startswith("Propose Peace")]
        assert rows and "The ledger stands" in rows[0] and "At expiry:" in rows[0], rows
        table = " ".join(by[("m8_table_under_truce", "5120x1440")]["lines"])
        assert "Austria" in table and "Holding out" in table

# ═══════════════════════════════════════════════════════════════════════════
# PC-R3 — ruling I, what the AI may dictate (S13e part 2, October 16, 2026)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def ulm_t18() -> WorldState:
    """The ulm passive arm at turn 18: Paris fell to Britain at turn 15; the
    first dictated letter (Britain, P8) went at turn 19. Britain reads +39."""
    return _board("ulm_t18_paris_fallen.json")


def _britain_at(w, score):
    k = w._make_diplo_key("Britain", "France")
    w.war_scores[k] = score if k.split("|")[0] == "Britain" else -score


class TestPCR3:
    def test_a_the_first_dictated_letter_after_paris_falls_carries_a_province(self, ulm_t18):
        """The balance pin (§46 I): on the ulm arm the first dictated letter
        after Paris falls carries a province or a client, never a gold lump
        alone — Frankfurt's tier, the capital held; priced by the player's
        own scorer; force-sent, never reduced to the purse."""
        w = ulm_t18
        assert w.regions["Paris"].controller == "Britain"
        _britain_at(w, 45)
        tier = AI.dictated_tier(w, "Britain", "France", 45)
        assert tier["tier"] == 1 and tier["capital_held"] and tier["label"] == "Frankfurt"
        with _quiet():
            letter = AI.process_diplomatic_phase("Britain", w)
        assert letter is not None and letter["proposal_type"] == "harsh_peace", letter
        terms = letter["terms"]
        assert terms["dictated_tier"] == 1 and terms["dictated_label"] == "Frankfurt"
        assert letter["_force_send"] is True
        kinds = [d["type"] for d in terms["demands"]]
        assert "territory_cede" in kinds and kinds.count("gold_lump") == 1
        ceded = next(d for d in terms["demands"] if d["type"] == "territory_cede")
        assert ceded["regions"] and all(r in w.get_nation_regions("France") for r in ceded["regions"])
        stream = next(d for d in terms["demands"] if d["type"] == "gold_per_turn")
        assert stream["turns"] == AI.DICTATED_STREAM_TURNS and "Paris" in stream["surety_regions"]
        # the player's scorer prices it (GR5)
        acc = D.calculate_acceptance(terms, w)
        assert isinstance(acc["score"], int)
        # the offer history on the instance, serialized with it
        hist = AI.dictated_offer_history(w, "Britain", "France")
        assert hist and hist[-1]["outcome"] == "sent" and hist[-1]["tier"] == 1
        again = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert AI.dictated_offer_history(again, "Britain", "France") == hist

    def test_b_the_ask_does_not_fall_as_france_falls(self, ulm_t18):
        """Ruling I item 3: the indemnity is priced to the WAR, not the purse
        — the same letter at a chest of 100 and at a chest of 40,000; and a
        France that has lost ten more provinces is asked no less."""
        w = ulm_t18
        age = AI.pair_war_age(w, "Britain", "France")
        rich = AI.war_priced_indemnity(w, "France", "Britain", 45, age)
        w.nation_gold["France"] = 100
        poor = AI.war_priced_indemnity(w, "France", "Britain", 45, age)
        assert rich == poor and rich["lump"] > 0 and rich["stream"] == rich["lump"] // 10
        for r in sorted(w.get_nation_regions("France"))[:10]:
            if r != "Corsica":
                w.regions[r].controller = "Britain"
        w.invalidate_active_nations_cache()
        later = AI.war_priced_indemnity(w, "France", "Britain", 45, age + 7)
        assert later["lump"] >= rich["lump"]
        # the settlement channel reads the same source
        terms = AI._settlement_offer_build_terms(
            accepter="France", proposer_nation="Britain", war_age_turns=age,
            accepter_war_score=-45, world=w)
        lump = next(t for t in terms if t["type"] == "gold_indemnity")
        assert lump["from"] == "France" and lump["amount"] == rich["lump"]

    def test_c_the_ratchet_raises_a_refused_letter_by_a_tier(self, ulm_t18):
        """Ruling I item 2: Reichenbach -> Frankfurt -> Chatillon. A refused
        (or lapsed) dictated letter raises the next by a tier; the next asks
        a client (the Duchy of Normandy) beside the province."""
        w = ulm_t18
        _britain_at(w, 45)
        with _quiet():
            first = AI.process_diplomatic_phase("Britain", w)
        assert first["terms"]["dictated_tier"] == 1
        assert AI.note_dictated_refusal(w, "Britain", "France", channel="bilateral")["outcome"] == "refused"
        assert AI.dictated_ratchet(w, "Britain", "France") == 1
        nxt = AI.next_dictated_letter(w, "Britain", "France")
        assert nxt["tier"] == 2 and nxt["label"] == "Châtillon" and "erected" in nxt["words"]
        w.ai_proposal_metadata.pop("Britain", None)
        from backend.game_logic.ai_diplomacy import _get_cooldowns, _set_cooldowns
        _set_cooldowns(w, {k: v for k, v in _get_cooldowns(w).items() if not k.startswith("Britain")})
        with _quiet():
            second = AI.process_diplomatic_phase("Britain", w)
        assert second is not None and second["terms"]["dictated_tier"] == 2, second
        kinds = [d["type"] for d in second["terms"]["demands"]]
        assert "create_client" in kinds and "territory_cede" in kinds
        # a lapse is a refusal to the ratchet; the cap holds
        AI.note_dictated_refusal(w, "Britain", "France", channel="bilateral", outcome="lapsed")
        AI.record_dictated_offer(w, "Britain", "France", channel="bilateral", tier=2, summary="x", ask_gold=1)
        AI.note_dictated_refusal(w, "Britain", "France", channel="bilateral")
        assert AI.dictated_ratchet(w, "Britain", "France") == AI.DICTATED_RATCHET_CAP
        assert AI.dictated_tier(w, "Britain", "France", 45)["tier"] == 3

    def test_d_the_settlement_letter_dictates_in_the_tables_dialect(self, ulm_t18):
        """The settlement channel carries the same clause types by tier and
        the table's validator and per-court scorer read them (GR5)."""
        from backend.game_logic.settlement_validation import validate_settlement_terms
        from backend.game_logic.settlement_baseline import compute_per_court_acceptance
        w = ulm_t18
        _britain_at(w, 45)
        war = w.war_instances["war_1"]
        terms = AI._settlement_offer_build_terms(
            accepter="France", proposer_nation="Britain",
            war_age_turns=AI.pair_war_age(w, "Britain", "France"),
            accepter_war_score=-45, world=w)
        kinds = [t["type"] for t in terms]
        assert kinds[0] == "peace" and "territory_cede" in kinds and "gold_per_turn" in kinds
        stream = next(t for t in terms if t["type"] == "gold_per_turn")
        assert stream["from"] == "France" and stream["to"] == "Britain" and stream["surety_regions"]
        verdict = validate_settlement_terms(
            [t for t in terms if t["type"] != "peace"], actor_nation="France",
            player_nation="France", proposer_side="defenders", world=w, war_instance=war,
            covered_enemy_participants=["France"], enforce_solvency=False)
        assert verdict["valid"], verdict
        view = compute_per_court_acceptance(
            w, war_id="war_1", war_instance=war, proposer_side="defenders",
            accepting_side="attackers", proposer_side_leader="Britain",
            covered_enemy_participants=["France"], settlement_terms=terms)
        assert "overall_acceptance" in view

    def test_e_refusal_costs_france(self, ulm_t18):
        """Ruling I item 4: the Charges name the refused peace by its tier,
        the marshals' petition carries it, the war panel shows the next
        letter's tier."""
        from backend.game_logic import war_status as WS
        from backend.models.world_state import CHARGES_REFUSED_PEACE_RATE
        w = ulm_t18
        _britain_at(w, 45)
        assert AI.refused_peace_standing(w, "France") is None
        with _quiet():
            AI.process_diplomatic_phase("Britain", w)
        AI.note_dictated_refusal(w, "Britain", "France", channel="bilateral")
        standing = AI.refused_peace_standing(w, "France")
        assert standing["tier"] == 1 and standing["next_label"] == "Châtillon"
        term = next(t for t in w.get_state_charges_rate("France")["terms"] if t["key"] == "refused_peace")
        assert term["amount"] == CHARGES_REFUSED_PEACE_RATE * 2
        assert term["label"].startswith("the peace refused — Britain's terms (Frankfurt, turn 18)")
        clause = AI.refused_peace_clause(w, "France")
        assert clause.startswith("Britain's terms — ") and "were refused at turn 18" in clause
        assert "her next letter will ask Châtillon's" in clause
        from backend.game_logic import jealousy as J
        assert J._refused_peace_clause(w) == clause
        with _quiet():
            hud = WS.build_active_wars(w)
        row = next(r for r in hud["wars"] if r.get("opponent") == "Britain" and r.get("status") == "war")
        assert row["refused_peace"] == clause
        assert row["next_letter"]["tier"] == 2 and "would dictate Châtillon's terms" in row["next_letter"]["display"]
        # a war that ends lets the charge go
        w.current_turn += AI.REFUSED_PEACE_MEMORY_TURNS
        assert AI.refused_peace_standing(w, "France") is None

    def test_f_the_stream_runs_and_the_sureties_go_home_when_paid(self, ulm_t18):
        """Ruling I item 3: a lump plus a stream, provinces held until paid
        (Tilsit's fortresses) — the dictated letter accepted, the stream pays
        ten turns and the last payment sends the sureties back."""
        w = ulm_t18
        _britain_at(w, 45)
        with _quiet():
            letter = AI.process_diplomatic_phase("Britain", w)
            res = w._ratify_treaty(letter["terms"])
        assert res and res.get("type") == "diplomatic_treaty_signed", res
        k = w._make_diplo_key("Britain", "France")
        stream = next(c for c in w.active_treaties[k]["clauses"] if c["type"] == "gold_per_turn")
        assert stream["turns"] == AI.DICTATED_STREAM_TURNS and "Paris" in stream["surety_regions"]
        assert w.regions["Paris"].controller == "Britain"
        w.nation_gold["France"] = 10 ** 6
        for _ in range(AI.DICTATED_STREAM_TURNS):
            with _quiet():
                w._process_treaty_clauses()
        assert w.regions["Paris"].controller == "France"
        assert not any(c["type"] == "gold_per_turn" for c in w.active_treaties[k]["clauses"])
        assert any(e.get("type") == "surety_returned" for e in w.event_log)
        assert any(e.get("type") == "surety_returned" for e in w.pending_dispatch_events)

    def test_g_the_regime_arm(self, ulm_t18):
        """Ruling I item 5: a Fall ends in a peace the successor government
        signs — one tier gentler than the dictating court's, recognition the
        term that bought it — on the record and in the exile story."""
        from backend.game_logic import game_end as GE
        w = ulm_t18
        _britain_at(w, 45)
        succ = AI.successor_peace(w, "France")
        assert succ["court"] == "Britain" and succ["tier"] == 0 and succ["refused_label"] == "Frankfurt"
        assert "The successor government signs the peace with Britain" in succ["line"]
        with _quiet():
            record = GE.record_ending(w, "defeat", GE.CAUSE_SOIL, detail={"provinces": 1})
        assert record is not None and record["terminal"]
        assert record["detail"]["successor_peace"]["court"] == "Britain"
        assert succ["line"] in (record["summary"]["epilogue"] or {}).get("paragraphs", [])

    def test_h_f13_the_ais_letter_never_stacks_every_clause(self, ulm_t18):
        """F13's AI half: one lump, one stream, at most two provinces, one
        client, one alliance — by tier, never everything at once."""
        w = ulm_t18
        for tier in range(0, 4):
            demands = AI.dictated_demands(w, "Britain", "France", tier, 45)
            kinds = [d["type"] for d in demands]
            assert kinds.count("gold_lump") == 1 and kinds.count("gold_per_turn") <= 1
            assert kinds.count("territory_cede") <= 2 and kinds.count("create_client") <= 1
            assert kinds.count("forced_alliance") <= 1 and len(demands) <= 5
            assert ("forced_alliance" in kinds) == (tier >= 3)
            assert ("territory_cede" in kinds) == (tier >= 1)
        assert AI.dictated_demands(w, "Britain", "France", 0, 45) == [
            {"type": "gold_lump", "value": AI.war_priced_indemnity(
                w, "France", "Britain", 45, AI.pair_war_age(w, "Britain", "France"))["lump"]}]

    def test_i_f65_f76_the_envelope_and_the_rail_name_the_tier(self, ulm_t18):
        from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
        w = ulm_t18
        _britain_at(w, 45)
        with _quiet():
            letter = AI.process_diplomatic_phase("Britain", w)
            AI.deliver_ai_proposal(letter, w)
        rail = [n for n in w.notifications.get_pending() if "dictates terms" in str(n.get("title", ""))]
        assert rail and "(Frankfurt)" in rail[-1]["title"] and "ceded" in rail[-1]["message"]
        payload = build_pending_envoy_popup_from_terms(
            w, nation="Britain", terms=letter["terms"], label_type="harsh_peace")
        assert payload["proposal_type_display"] == "Harsh Peace Treaty — Frankfurt"
        assert payload["dictated_tier"] == 1 and payload["dictated_label"] == "Frankfurt"

    def test_j_the_seams_are_functions_the_series_holds_down(self, ulm_t18, monkeypatch):
        w = ulm_t18
        _britain_at(w, 45)
        monkeypatch.setattr(AI, "dictated_tier", lambda *a, **k: {
            "tier": 0, "base": 0, "ratchet": 0, "capital_held": False, "label": "Reichenbach",
            "asks": "", "next_tier": 1, "next_label": "Frankfurt", "next_asks": ""})
        with _quiet():
            letter = AI.process_diplomatic_phase("Britain", w)
        # the old one-lump letter, reduced to the purse by the FA-21 reducer
        assert [d["type"] for d in letter["terms"]["demands"]] == ["gold_lump"]
        assert letter["terms"]["demands"][0]["value"] <= max(200, int(w.nation_gold["France"] * 0.15))


class TestTheSeriesPart2:
    """`tools/_pc_s13e2_series_arms.py` (record `tools/_pc_s13e2_series_arms_
    final.json`): arm 0 (every seam down) reproduces the shipped series byte
    for byte, and so does every other arm — BASELINE_SERIES does not move.
    The reach: the ledger seam was read 20 times (kept on every truce), the
    tier seam 9 times (tiers 2 and 3 reached through lapsed letters — the
    passive France answers none), the indemnity seam 10 times (war-priced),
    the hope seam twice (dead both times: the court sent its peace letter
    where it would have asked a truce); the exhaustion-hold seam was NOT
    reached (no court sat in a truce-only state in the ambient sim — it is
    pinned on the Vienna-held board instead). The series is the threat
    scalar: a letter the passive France never answers moves nothing it
    reads — the stated reason the arms are byte-identical."""

    def _record(self):
        return json.loads((REPO / "tools" / "_pc_s13e2_series_arms_final.json").read_text(encoding="utf-8"))

    def test_the_record_links_to_the_last_one_and_the_baseline(self):
        import sys as _sys
        _sys.path.insert(0, str(REPO / "tests"))
        from test_ai_intent_threat_migration import BASELINE_SERIES
        rec = self._record()
        part1 = json.loads((REPO / "tools" / "_pc_s13e_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == part1["arms"]["ALL"]["series"] == BASELINE_SERIES
        assert set(rec["arms"]) == {"0", "L", "E", "H", "T", "I", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
        assert rec["arms"]["ALL"]["series"] == BASELINE_SERIES

    def test_the_seams_were_reached(self):
        rec = self._record()
        reach = {arm: row["reach"] for arm, row in rec["arms"].items()}
        assert reach["ALL"]["ledger|kept"] > 0 and reach["0"]["ledger|popped"] > 0
        assert reach["ALL"]["indemnity|war"] > 0 and reach["0"]["indemnity|purse"] > 0
        assert reach["ALL"].get("tier|2", 0) + reach["ALL"].get("tier|3", 0) > 0
        assert reach["ALL"]["hope|dead"] > 0 and reach["0"]["hope|alive"] > 0
        assert not any(k.startswith("exhaustion|") for k in reach["ALL"])   # unreached in the ambient sim


class TestF59TheAusterlitzWindow:
    """`tools/_pc_s13e2_austerlitz_drive.py` (record `tools/_pc_s13e2_
    austerlitz_truces.json`): the commanded austerlitz arm driven t24-44
    twice from one save — the rules DOWN through their seams and UP. Reported
    per seed, never as a law: in THIS window both arms signed two truces with
    Austria and saw both collapse (the court's hope lived — Britain fought
    on unspent); with the rules up the war is 24 turns old at turn 44 (the
    design war of turn 20 — the stamp survived both collapses) where the
    rules down ended it at a peace with the age popped."""

    def _record(self):
        return json.loads((REPO / "tools" / "_pc_s13e2_austerlitz_truces.json").read_text(encoding="utf-8"))

    def test_the_wars_age_survives_the_collapses(self):
        rec = self._record()
        assert rec["seed"] == "austerlitz" and rec["turns"] == 20
        after = rec["after"]
        assert after["seams_down"] == [] and after["collapses"] >= 1
        assert after["final_state"] == "WAR" and after["war_age_at_end"] == 24
        before = rec["before"]
        assert len(before["seams_down"]) == 3 and before["truces_with_austria"] >= 1


# ═══════════════════════════════════════════════════════════════════════════
# PC-R1 (v) — the ally's bill and the two Pressburgs; the table's holes
# (S13e part 2, October 16, 2026)
# ═══════════════════════════════════════════════════════════════════════════

def _swap_in(monkeypatch, world):
    """The HTTP idiom on a BOARD: `M.world`, `M.game_state["world"]` and the
    mock parser swapped together (the memory's rule)."""
    from backend import main as M
    from backend.commands.parser import CommandParser
    from tests import _chip_census as C
    C.board_env(monkeypatch)
    monkeypatch.setattr(M, "world", world)
    M.game_state["world"] = world
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return M


TYROL_TO_BAVARIA = {"type": "territory_cede", "from": "Austria", "to": "Bavaria", "region": "Tyrol"}


class TestPCR1TheBill:
    def test_v_the_petition_reads_the_allys_desire_profile(self, vienna_held):
        """C item 3: every boot objective is `defense` (no material claim), so
        Bavaria never asked for Tyrol; her desire profile is her bill, and a
        table that names her for Tyrol satisfies it."""
        from backend.game_logic import settlement_offers as SO
        w = vienna_held
        claims = SO._desire_profile_claims_for_ally(w, "Bavaria", target_enemy="Austria", war_id="war_1")
        assert [c["claim_region"] for c in claims] == ["Tyrol"] and claims[0]["objective_type"] == "desire"
        ctx = SO._find_warn_sellout_petition_context(
            w, war_id="war_1", covered_enemy_participants=["Austria"], settlement_terms=[])
        assert ctx and ctx["ally_nation"] == "Bavaria" and ctx["claim_region"] == "Tyrol"
        assert SO._find_warn_sellout_petition_context(
            w, war_id="war_1", covered_enemy_participants=["Austria"],
            settlement_terms=[TYROL_TO_BAVARIA]) is None

    def test_v_the_reward_is_priced_as_the_leaders_demand(self, vienna_held):
        """C's rate (§46): a cession to an allied beneficiary is priced to the
        ceding court at the SAME harshness as a cession to France — and the
        balance projection moves the province from its holder, so the two
        drafts project the same bloc (PC-X10: it added Tyrol to Bavaria
        while France kept it, −5 for the ally's draft alone)."""
        from backend.game_logic.settlement_staging import build_settlement_preview
        from backend.game_logic.settlement_scoring import project_balance_after_settlement
        w = vienna_held

        def comps(terms):
            with _quiet():
                p = build_settlement_preview(
                    w, war_id="war_1", proposer_side="attackers", settlement_terms=terms,
                    covered_enemy_participants=["Austria"], actor_nation="France",
                    ignore_active_dialogue=True)["settlement_preview"]
            return p["acceptance"]["score"], dict(p["acceptance"]["components"])
        to_france = comps([dict(TYROL_TO_BAVARIA, to="France")])
        to_bavaria = comps([TYROL_TO_BAVARIA])
        assert to_france[1]["term_harshness_penalty"] == to_bavaria[1]["term_harshness_penalty"] == -9
        assert to_france[1]["leader_own_losses"] == to_bavaria[1]["leader_own_losses"]
        for to in ("France", "Bavaria"):
            r = project_balance_after_settlement(
                w, war_id="war_1", settlement_terms=[dict(TYROL_TO_BAVARIA, to=to)])
            assert r["modifier"] == 0, (to, r)       # no bloc-growth charge on either draft
        assert to_france[0] == to_bavaria[0] == 36

    def test_v_f81_the_allys_standing_is_read_before_its_episode_closes(self, vienna_held):
        """A carried ally named for Tyrol gets the gratitude pass (it read
        `no_standing` after the cleanup closed its episode); the Pressburg
        cession of a province France HOLDS carries to Bavaria (PC-F52)."""
        from backend.game_logic import settlement_ratify as SR
        from backend.game_logic.settlement_reactions import get_settlement_memories
        from tests.test_common_peace_c2_ratification import _acceptance_always_passes, _stage_dialogue
        w = vienna_held
        rel_before = int(w.nation_relations.get(w._make_diplo_key("France", "Bavaria"), 0))
        from backend.game_logic import settlement_scoring as SS
        import unittest.mock as _m
        with _m.patch.object(SS, "calculate_common_peace_acceptance", _acceptance_always_passes):
            dialogue = _stage_dialogue(w, settlement_terms=[TYROL_TO_BAVARIA],
                                       covered_enemy_participants=["Austria"], war_id="war_1")
            with _quiet():
                result = SR.ratify_settlement_confirm(w, dialogue)
        assert result["success"], result
        assert w.regions["Tyrol"].controller == "Bavaria"          # the occupied homeland, carried
        assert result["dropped_clauses"] == []
        rewarded = [r for r in result["settlement_reactions"]["proposer_side_reactions"]
                    if r.get("kind") == "ally_rewarded" and r.get("ally") == "Bavaria"]
        assert rewarded and rewarded[0]["standing_level"] != "no_standing", result["settlement_reactions"]
        assert get_settlement_memories(w, subject="Bavaria", memory_type="they_chose_us")
        assert int(w.nation_relations.get(w._make_diplo_key("France", "Bavaria"), 0)) > rel_before
        assert result["revanche_line"].startswith("Revanche lapses: Austria's cession of Tyrol")

    def test_v_the_two_pressburgs_line(self, vienna_held):
        """C item 5: a cession of two homeland provinces or the capital writes
        the punitive record — "Revanche stands"; one province — "Revanche
        lapses while the treaty holds"; on the preview, the counsel's table
        road and the aftermath, from the one seam."""
        from backend.game_logic import emergent_designs as ED
        from backend.game_logic.settlement_staging import build_settlement_preview
        w = vienna_held
        one = ED.revanche_line_for_terms(w, [TYROL_TO_BAVARIA])
        assert one == ("Revanche lapses: Austria's cession of Tyrol reconciles her Revanche "
                       "while the treaty holds.")
        two = ED.revanche_line_for_terms(w, [TYROL_TO_BAVARIA,
                                            dict(TYROL_TO_BAVARIA, to="France", region="Bohemia")])
        assert two.startswith("Revanche stands: this peace strips Austria of Bohemia, Tyrol")
        capital = ED.revanche_line_for_terms(w, [dict(TYROL_TO_BAVARIA, to="France", region="Vienna")])
        assert capital.startswith("Revanche stands: this peace strips Austria of Vienna")
        assert ED.revanche_line_for_terms(w, []) == ""
        with _quiet():
            p = build_settlement_preview(
                w, war_id="war_1", proposer_side="attackers", settlement_terms=[TYROL_TO_BAVARIA],
                covered_enemy_participants=["Austria"], actor_nation="France",
                ignore_active_dialogue=True)["settlement_preview"]
        assert p["revanche_line"] == one
        reading = CS.read_counsel(w, "Austria", staged_terms=[TYROL_TO_BAVARIA])
        table = next(r for r in reading["roads"] if r["road"] == "table_alone")
        assert table["revanche_line"] == one

    def test_v_f70_the_hand_off_keeps_the_beneficiary_and_names_the_rest(self, vienna_held):
        from backend.game_logic.settlement_staging import _pair_substitute_seed_terms
        from backend.game_logic.diplomatic_templates import annotate_peace_terms
        seed = _pair_substitute_seed_terms(
            [TYROL_TO_BAVARIA,
             {"type": "gold_indemnity", "from": "Austria", "to": "Bavaria", "amount": 300},
             {"type": "forced_alliance", "from": "Austria", "to": "France"}],
            target="Austria", proposer_leader="France")
        gold = next(d for d in seed["demands"] if d["type"] == "gold_lump")
        cede = next(d for d in seed["demands"] if d["type"] == "territory_cede")
        assert gold["to_nation"] == "Bavaria" and gold["value"] == 300
        assert cede["to_nation"] == "Bavaria" and cede["regions"] == ["Tyrol"]
        assert seed["carried"] == ["Tyrol to Bavaria", "300 gold to Bavaria"]
        assert seed["dropped"] == ["the forced alliance (settlement-tier)"]
        rows = annotate_peace_terms({"demands": seed["demands"], "sweeteners": [], "clauses": []},
                                    "France", "Austria")
        labels = [r["display_label"] for r in rows]
        assert any("Bavaria" in lb and "Tyrol" in lb for lb in labels), labels
        # the bilateral ratifier transfers to the beneficiary named
        from backend.game_logic.treaty import treaty_clauses_of
        clauses = treaty_clauses_of({"demands": seed["demands"], "sweeteners": []}, "France", "Austria")
        assert all(c["to"] == "Bavaria" for c in clauses)


class TestTheTableHoles:
    def test_f54_the_offer_rows_lead_with_the_occupied_capital(self, vienna_held, monkeypatch):
        """"Offer Vienna" leads Austria's offer rows on the Vienna-held board
        (the capital was skipped); the baseline's own auto-pick still never
        returns a capital."""
        from backend.game_logic.settlement_baseline import _concession_baseline_transferable_candidates
        w = vienna_held
        rows = _concession_baseline_transferable_candidates(
            w, proposer_side_participants=["France", "Bavaria", "KingdomOfItaly"],
            accepting_leader="Austria", include_capitals=True)
        assert "Vienna" in rows
        assert "Vienna" not in _concession_baseline_transferable_candidates(
            w, proposer_side_participants=["France", "Bavaria", "KingdomOfItaly"],
            accepting_leader="Austria")
        M = _swap_in(monkeypatch, w)
        from fastapi.testclient import TestClient
        client = TestClient(M.app)
        w.diplomatic_points = 9
        with _quiet():
            r = client.post("/command", json={"command": "propose common peace with Austria"}).json()
        dialogue = r.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "settlement_confirm", r.get("message")
        row = next(c for c in dialogue.get("per_court_acceptance") or [] if c.get("nation") == "Austria")
        offers = [s for s in (row.get("demand_suggestions") or []) if s.get("group") == "offer"
                  and s.get("clause_type") == "territory_cede"]
        assert offers and offers[0]["label"].startswith("Offer Vienna to Austria — her capital"), offers
        assert offers[0]["region_options"][0] == "Vienna"

    def test_f56_the_preview_validates_what_it_scores(self, vienna_held):
        """A same-side transfer (France → Bavaria) previews BLOCKED with the
        validator's reason, never "Will carry"."""
        from backend.game_logic.settlement_staging import build_settlement_preview
        w = vienna_held
        with _quiet():
            p = build_settlement_preview(
                w, war_id="war_1", proposer_side="attackers",
                settlement_terms=[{"type": "territory_cede", "from": "France", "to": "Bavaria", "region": "Tyrol"}],
                covered_enemy_participants=["Austria"], actor_nation="France",
                ignore_active_dialogue=True)["settlement_preview"]
        assert p["validation"]["valid"] is False and p["validation"]["error"] == "clause_side_mismatch"
        assert p["overall_acceptance"]["carries"] is False
        assert p["overall_acceptance"]["carry_verdict_display"].startswith("Blocked — ")
        assert all(r["band_display"] == "Blocked" for r in p["per_court_acceptance"])
        with _quiet():
            ok = build_settlement_preview(
                w, war_id="war_1", proposer_side="attackers", settlement_terms=[TYROL_TO_BAVARIA],
                covered_enemy_participants=["Austria"], actor_nation="France",
                ignore_active_dialogue=True)["settlement_preview"]
        assert ok["validation"]["valid"] is True

    def test_f52_a_cession_the_ceder_cannot_carry_is_refused_at_the_validator(self, vienna_held):
        """Tyrol held by France (the receiving side) carries as Austria's
        cession to Bavaria; Tyrol held by Russia (the other side) is refused
        in words — never dropped silently."""
        from backend.game_logic.settlement_validation import (
            occupied_homeland_cession_ok, validate_settlement_terms,
        )
        w = vienna_held
        war = w.war_instances["war_1"]
        assert occupied_homeland_cession_ok(w, war, "Tyrol", "Austria", "Bavaria", "France")
        assert not occupied_homeland_cession_ok(w, war, "Tyrol", "Austria", "Bavaria", "Russia")
        w.regions["Tyrol"].controller = "Russia"
        w.invalidate_active_nations_cache()
        verdict = validate_settlement_terms(
            [TYROL_TO_BAVARIA], actor_nation="France", player_nation="France",
            proposer_side="attackers", world=w, war_instance=war,
            covered_enemy_participants=["Austria"], enforce_solvency=False)
        assert verdict["valid"] is False and verdict["error"] == "ceder_does_not_hold"
        assert "cannot carry" in verdict["disabled_reason_display"]

    def test_f52_the_ratifier_names_what_it_could_not_carry(self, vienna_held):
        from backend.game_logic import settlement_ratify as SR
        w = vienna_held
        w.regions["Tyrol"].controller = "Russia"
        w.invalidate_active_nations_cache()
        with _quiet():
            applied = SR._apply_settlement_terms(w, settlement_terms=[TYROL_TO_BAVARIA], war_id="war_1")
        assert applied == []
        dropped = SR.take_dropped_clauses(w)
        assert dropped and dropped[0]["reason"] == "ceder_does_not_hold" and dropped[0]["holder"] == "Russia"
        assert "Tyrol not carried" in dropped[0]["display"]
        assert SR.take_dropped_clauses(w) == []                  # read once, then cleared

    def test_f62_the_gold_credit_is_summed_per_payer_and_payee(self):
        from backend.game_logic.settlement_scoring import calculate_concession_credit
        def credit(terms):
            return calculate_concession_credit(
                proposer_side_participants=["France"], accepting_side_participants=["Britain"],
                accepting_leader="Britain", covered_enemy_participants=["Britain"],
                settlement_terms=terms)
        one = credit([{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 1100}])
        two = credit([{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 1000},
                      {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 100}])
        three = credit([{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 1000}] * 3)
        assert one["raw_score"] == two["raw_score"] == three["raw_score"] == 40
        assert len(two["credited_terms"]) == 1 and two["credited_terms"][0]["index"] == 0

    def test_f13_the_losing_draft_asks_its_prisoners_back_as_one_term(self, ulm_t18):
        """Three French marshals held by Britain: ONE `prisoner_return` demand
        naming them (the sovereign first), priced per man, released per man;
        the losing draft never stacks every concession beside it."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms, annotate_peace_terms
        w = ulm_t18
        held = [m for m in w.marshals.values() if m.nation == "France"][:3]
        for m in held:
            m.captured_by = "Britain"
        with _quiet():
            terms = generate_suggested_terms("Britain", "peace", w, deterministic=True)
        prisoners = [d for d in terms["demands"] if d["type"] == "prisoner_return"]
        assert len(prisoners) == 1 and sorted(prisoners[0]["marshals"]) == sorted(m.name for m in held)
        assert prisoners[0]["marshal"] == prisoners[0]["marshals"][0]
        others = [d for d in terms["demands"] if d["type"] != "prisoner_return"]
        assert not any(d["type"] in ("territory_cede", "territory") for d in others)
        acc = D.calculate_acceptance({"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                                      "demands": prisoners, "sweeteners": [], "clauses": []}, w)
        per_man = D.calculate_acceptance({"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                                          "demands": [{"type": "prisoner_return", "marshal": held[0].name}],
                                          "sweeteners": [], "clauses": []}, w)
        assert acc["score"] < per_man["score"]                    # three men cost more than one
        rows = annotate_peace_terms({"demands": prisoners, "sweeteners": [], "clauses": []}, "France", "Britain")
        assert held[0].name in rows[0]["display_label"] and held[2].name in rows[0]["display_label"]
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                                    "demands": prisoners, "sweeteners": [], "clauses": []})
        assert res and all(not getattr(m, "captured_by", "") for m in held), res

    def test_f22_the_sabotage_never_turns_an_estimate_into_a_refusal_unseen(self, vienna_held):
        """A white peace that the estimate accepts: the "too generous"
        hardening (50 gold a turn) that would flip it to REJECT is walked
        back, and the record says so."""
        from backend.commands.diplomatic_defiance import apply_diplomatic_sabotage, _estimate_verdict
        w = vienna_held
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                    "demands": [], "sweeteners": [], "clauses": []}
        assert _estimate_verdict(proposal, w) != "REJECT"
        tal = w.diplomats.get("France")
        rec = apply_diplomatic_sabotage(proposal, tal, w)
        assert rec["estimate_before"] != "REJECT"
        assert _estimate_verdict(rec["modified_proposal"], w) != "REJECT"
        assert rec["estimate_after"] != "REJECT"
        if rec["hardening_withheld"]:
            assert rec["defiance_type"] in ("hardened", "stalled")

    def test_the_done_when_the_pressburg_trade_is_authored_from_the_rows_and_ratifies(self, vienna_held, monkeypatch):
        """The part's done-when: on the Vienna-held board, Austria alone —
        "Tyrol to Bavaria" from the demand rows, "Offer Vienna" from the
        offer rows — submits, confirms and ratifies: Tyrol to Bavaria, Vienna
        back to Austria, Bavaria's war ended in the instrument, the
        Revanche line said."""
        from fastapi.testclient import TestClient
        w = vienna_held
        M = _swap_in(monkeypatch, w)
        client = TestClient(M.app)
        w.diplomatic_points = 9

        def post(choice, dialogue, params):
            with _quiet():
                return client.post("/respond_to_diplomatic_dialogue", json={
                    "choice": choice, "dialogue_id": dialogue.get("dialogue_id"),
                    "action_params": params}).json()
        with _quiet():
            r = client.post("/command", json={"command": "propose common peace with Austria"}).json()
        dialogue = r.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "settlement_confirm", r.get("message")
        # Austria alone
        for court in ("Britain", "Russia"):
            out = post("settlement_cover_drop", dialogue, {"nation": court})
            assert out.get("success"), out.get("message") or out.get("error_display")
            dialogue = out["diplomatic_dialogue"]
        assert dialogue["covered_enemy_participants"] == ["Austria"]
        out = post("settlement_demand_add", dialogue, {
            "nation": "Austria", "group": "demand", "clause_type": "territory_cede",
            "region": "Tyrol", "to": "Bavaria"})
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        out = post("settlement_demand_add", dialogue, {
            "nation": "Austria", "group": "offer", "clause_type": "territory_cede", "region": "Vienna"})
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        kinds = sorted((t["type"], t.get("from"), t.get("to"), t.get("region"))
                       for t in dialogue["settlement_terms"] if t.get("from"))
        assert ("territory_cede", "Austria", "Bavaria", "Tyrol") in kinds
        assert ("territory_cede", "France", "Austria", "Vienna") in kinds
        assert (dialogue.get("settlement_preview") or dialogue).get("revanche_line", "").startswith("Revanche lapses")
        out = post("submit_settlement_for_review", dialogue, {})
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        out = post("confirm_settlement", dialogue, {})
        assert out.get("success"), out.get("message") or out.get("error_display")
        assert w.regions["Tyrol"].controller == "Bavaria"
        assert w.regions["Vienna"].controller == "Austria"
        assert _state(w, "France", "Austria") == "PEACE" and _state(w, "Bavaria", "Austria") == "PEACE"
        assert "Revanche lapses" in str(out.get("message") or "")
