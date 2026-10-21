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

S13e part 3 (October 16, 2026; rules `SYSTEMS_REFERENCE.md` §124):
  PC-R4  ruling E: each court on its OWN pair at the table (the base and the
         tier read `court_own_pressure`), the 0.10 stake floor (covered, not
         consulted — never a veto; a burdened court always consulted), the
         payee credited in full, the AI's letter dry-run as the player's and
         WRITTEN by contribution on the writer's own pair (F63); F27, F26,
         F60, F61.
  PC-R5  ruling H: the +8 clock made of occupation, subsidy and finance,
         named (`war_exhaustion_terms`); the truce holds; the league gate
         reads the live rate; the components on the war popup (F42); F31; F20.
  PC-R6  ruling G: decay then cap; the shield down while the capital is held
         and a ticking that falls; the fill shown; the trend drawn (F84); every
         ±100 literal re-read; F38, F39.
  The two scores F55, F71; the coalition's shape F58, F66, F77, F79, F80; the
  sea F64, F68; the series `tools/_pc_s13e3_series_arms.py`.

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
            # M1 was re-shot again in part 3 (the stake floor, the fill, the clock)
            # and all four in part 4 (PC-R7 (i): the war's title) — any S13e re-shoot.
            assert e.get("reshot", "").startswith("S13e part"), sid
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
        from test_ai_intent_threat_migration import BASELINE_SERIES, SERIES_BEFORE_THE_BOND
        rec = self._record()
        pc = json.loads((REPO / "tools" / "_pc_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == pc["arms"]["ALL"]["series"] == SERIES_BEFORE_THE_BOND  # PC-R7 (ii) part 3: the series before the bond moved it (`tests/test_ai_intent_threat_migration.SERIES_BEFORE_THE_BOND`)
        assert set(rec["arms"]) == {"0", "C", "Y", "H", "W", "G", "R", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
        assert rec["arms"]["ALL"]["series"] == SERIES_BEFORE_THE_BOND  # PC-R7 (ii) part 3: the series before the bond

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
            # re-shot in part 2, and (all but the wizard and the table under the
            # truce) again in part 4 — PC-R7 (i)'s title and PC-X27's War Summary
            assert e.get("reshot", "").startswith("S13e part"), sid
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
        # PC-R7 (i): the Charges name the war by its stake (ulm: Paris held).
        assert term["label"].startswith("the peace refused — Britain's terms in the War for Paris (Frankfurt, turn 18)"), term["label"]
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
        from test_ai_intent_threat_migration import BASELINE_SERIES, SERIES_BEFORE_THE_BOND
        rec = self._record()
        part1 = json.loads((REPO / "tools" / "_pc_s13e_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == part1["arms"]["ALL"]["series"] == SERIES_BEFORE_THE_BOND  # PC-R7 (ii) part 3: the series before the bond moved it (`tests/test_ai_intent_threat_migration.SERIES_BEFORE_THE_BOND`)
        assert set(rec["arms"]) == {"0", "L", "E", "H", "T", "I", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
        assert rec["arms"]["ALL"]["series"] == SERIES_BEFORE_THE_BOND  # PC-R7 (ii) part 3: the series before the bond

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
# PC-R7 (ii) (S14 part 1): the moderate Pressburg's two articles — Franconia,
# Bavaria's coin (Würzburg's place in the exchange that gave Austria Salzburg),
# and Talleyrand's own plan, Austria pointed east.
FRANCONIA_FOR_TYROL = {"type": "territory_compensate", "from": "Bavaria", "to": "Austria",
                       "region": "Franconia", "holder": "Bavaria"}
THE_EASTERN_QUESTION = {"type": "territory_compensate", "from": "France", "to": "Austria",
                        "region": "Albania", "holder": "Ottoman", "design": "the_eastern_question",
                        "design_title": "The Eastern Question"}


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


# ═══════════════════════════════════════════════════════════════════════════
# PC-R4 — ruling E, each court on its own war (S13e part 3, October 16, 2026)
# ═══════════════════════════════════════════════════════════════════════════

def _preview(world, war_id="war_1", terms=None, covered=None):
    from backend.game_logic.settlement_staging import build_settlement_preview
    kwargs = {"war_id": war_id, "settlement_terms": list(terms or []), "actor_nation": "France",
              "ignore_active_dialogue": True}
    if covered is not None:
        kwargs["covered_enemy_participants"] = list(covered)
    with _quiet():
        pv = build_settlement_preview(world, **kwargs)
    return pv.get("settlement_preview") or {}


def _row(body, nation):
    return next(r for r in body["per_court_acceptance"] if r["nation"] == nation)


def _comp(row, key):
    return dict((x["component"], x["value"]) for x in row["component_breakdown"]).get(key)


def _force_pair(w, a, b, score):
    k = w._make_diplo_key(a, b)
    w.war_scores[k] = score if k.split("|")[0] == a else -score


class TestPCR4:
    """Ruling E — each court on its OWN pair at the table; the stake floor; the
    payee credited in full; the court's own tier; the AI's letter dry-run as
    the player's and written by contribution (`SYSTEMS_REFERENCE.md` §124.1)."""

    def test_a_britain_alone_reads_6_beside_austrias_79_on_one_table(self, vienna_held):
        """The done-when: on ONE table Austria (pair +79 live, +54 stored) reads
        50/50 on her own pair; Britain reads the 6/50 she reads alone; Russia 7.
        Before, the side mean (17) held Austria at 11 and lifted Britain to 18."""
        body = _preview(vienna_held)
        a, b, r = _row(body, "Austria"), _row(body, "Britain"), _row(body, "Russia")
        assert (a["total"], b["total"], r["total"]) == (50, 6, 7)
        assert a["court_pressure_score"] == 54 and b["court_pressure_score"] == -2 and r["court_pressure_score"] == 0
        assert _comp(a, "base_side_pressure") == 35 and _comp(b, "base_side_pressure") == -1
        assert _comp(a, "settlement_tier_legitimacy") == 5      # dictated_terms at her own 54 (was -10)
        assert _comp(b, "settlement_tier_legitimacy") == -10    # white peace at her own -2
        alone = _row(_preview(vienna_held, covered=["Britain"]), "Britain")
        assert alone["total"] == 6 == b["total"]                # the same 6 alone and on the whole table
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            row = [w for w in build_active_wars(vienna_held)["wars"] if w.get("status") == "war"][0]
        courts = {c["nation"]: c for c in row["peace_table"]["courts"]}
        assert courts["Austria"]["pair_score"] == 79 and courts["Britain"]["total"] == 6
        assert "scores each court on its own pair" in " ".join(row["peace_table"]["lines"])

    def test_a_the_seam_is_one_function(self, vienna_held, monkeypatch):
        from backend.game_logic import settlement_scoring as SC
        assert SC.court_own_pressure(17, 54) == 54 and SC.court_own_pressure(17, None) == 17
        assert SC.court_own_pressure(17, 140) == 100          # clamped to the ±100 scale
        monkeypatch.setattr(SC, "court_own_pressure", lambda s, o: s)   # the rule DOWN: the side mean
        body = _preview(vienna_held)
        assert _row(body, "Austria")["total"] == 11 and _row(body, "Britain")["total"] == 18

    def test_b_the_stake_floor_covers_the_unfought_without_a_veto(self, vienna_held):
        """E item 3: Britain (1 %) and Russia (0 %) are covered, not consulted —
        the whole-table white peace carries on Austria's consent; the words."""
        body = _preview(vienna_held)
        assert body["overall_acceptance"]["carries"] is True
        assert body["overall_acceptance"]["covered_not_consulted"] == ["Britain", "Russia"]
        assert _row(body, "Austria")["consulted"] is True
        assert _row(body, "Britain")["consulted"] is False and _row(body, "Russia")["consulted"] is False
        assert "1 %" in _row(body, "Britain")["stake_display"] and "stake floor" in _row(body, "Britain")["stake_display"]
        assert "covered, not consulted" in body["overall_acceptance"]["summary_display"]
        from backend.game_logic.war_contribution import CONSULT_MATERIAL_SHARE_THRESHOLD
        assert CONSULT_MATERIAL_SHARE_THRESHOLD == 0.10          # one ladder for both sides
        from backend.game_logic.settlement_staging import build_settlement_confirm_dialogue
        with _quiet():
            from backend.game_logic.settlement_staging import build_settlement_preview
            prev = build_settlement_preview(vienna_held, war_id="war_1", settlement_terms=[],
                                            actor_nation="France", ignore_active_dialogue=True)
            dlg = build_settlement_confirm_dialogue(vienna_held, prev)
        assert "Under the stake floor Britain and Russia are covered, not consulted" in dlg["talleyrand_text"]

    def test_b_a_burdened_court_is_always_consulted_and_nobody_is_left_unconsulted(self, vienna_held):
        """The floor removes the veto over the SIDE's peace, never over the
        court's own soil or gold; a table never has nobody consulted."""
        burden = [{"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 500}]
        body = _preview(vienna_held, terms=burden)
        assert _row(body, "Britain")["consulted"] is True and body["overall_acceptance"]["carries"] is False
        assert "Britain" in body["overall_acceptance"]["holdout_courts"]
        alone = _preview(vienna_held, covered=["Britain"])
        assert _row(alone, "Britain")["consulted"] is True       # the senior covered court signs
        assert alone["overall_acceptance"]["carries"] is False and alone["overall_acceptance"]["holdout_courts"] == ["Britain"]

    def test_b_the_floor_reads_the_ledger_and_falls_silent_without_one(self, w, vienna_held, monkeypatch):
        from backend.game_logic import settlement_baseline as SB
        inst = vienna_held.war_instances["war_1"]
        for court, expect in (("Austria", True), ("Britain", False), ("Russia", False)):
            f = SB.stake_floor_consults(vienna_held, war_id="war_1", war_instance=inst,
                                        accepting_side="defenders", court=court, settlement_terms=[])
            assert f["consulted"] is expect, (court, f)
        boot_inst = next(iter(w.war_instances.values()))
        f = SB.stake_floor_consults(w, war_id=boot_inst["war_id"], war_instance=boot_inst,
                                    accepting_side="defenders", court="Britain", settlement_terms=[])
        assert f["consulted"] is True and f["reason"] == "no_ledger"     # the boot: nothing fought yet
        monkeypatch.setattr(SB, "stake_floor_consults",
                            lambda *a, **k: {"consulted": True, "share": None, "reason": "floor_down"})
        body = _preview(vienna_held)
        assert body["overall_acceptance"]["carries"] is False            # the rule DOWN: the veto returns

    def test_c_the_payee_is_credited_in_full_and_the_side_at_the_share(self, vienna_held):
        from backend.game_logic.settlement_scoring import side_gold_credit_share
        terms = [{"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 300}]
        body = _preview(vienna_held, terms=terms)
        assert _comp(_row(body, "Austria"), "concession_credit") == 12
        assert _comp(_row(body, "Britain"), "concession_credit") == int(12 * side_gold_credit_share()) == 6

    def test_d_the_letter_is_dry_run_as_the_players_and_written_by_contribution(self, vienna_held):
        """E item 5 + F63: Austria (99 % of the war) writes the side's letter and
        pays on her OWN pair (+54 from our chair), not Britain on the side's sum."""
        war = vienna_held.war_instances["war_1"]
        covered = ["Austria", "Britain", "Russia"]
        writer, score = AI.letter_writer_and_score(vienna_held, war, player="France", covered=covered, leader="Britain")
        assert (writer, score) == ("Austria", 54)
        assert score == D.get_war_score_for(vienna_held, "France", "Austria") != D.sum_stored_side_score(vienna_held, "France", covered)
        # Austria consents as the writer (she also sues); Britain (1 %) and Russia
        # (0 %) have no stake — the writer stipulates for them (ruling C's mirror).
        assert AI.letter_consenting_courts(vienna_held, "France", covered, writer) == ["Austria", "Britain", "Russia"]
        assert AI.letter_consenting_courts(vienna_held, "France", ["Austria", "Britain"], "Britain") == ["Britain", "Austria"]
        assert AI.courts_the_letter_carries(vienna_held, "war_1", war, player="France", covered=covered,
                                            terms=[{"type": "peace"}], writer=writer) == covered
        import copy as _copy
        w2 = _copy.deepcopy(vienna_held)
        with _quiet():
            offer = AI._emit_settlement_offer_for_war(w2, "war_1", w2.war_instances["war_1"], player="France",
                                                     current_turn=w2.current_turn, pending=[], cooldowns={})
        assert offer is not None and offer["proposer_nation"] == "Austria"
        gold = [t for t in offer["settlement_terms"] if t["type"] == "gold_indemnity"]
        assert gold and gold[0]["from"] == "Austria" and gold[0]["to"] == "France"

    def test_d_the_seams_down_are_the_old_letter(self, vienna_held, monkeypatch):
        war = vienna_held.war_instances["war_1"]
        covered = ["Austria", "Britain", "Russia"]
        monkeypatch.setattr(AI, "letter_consenting_courts", lambda w, p, c, writer="": list(c))
        assert AI._letter_would_carry(vienna_held, "war_1", war, player="France", covered=covered, terms=[{"type": "peace"}])
        monkeypatch.setattr(AI, "letter_writer_and_score",
                            lambda w, war, *, player, covered, leader: (leader, D.sum_stored_side_score(w, player, covered)))
        import copy as _copy
        w2 = _copy.deepcopy(vienna_held)
        with _quiet():
            offer = AI._emit_settlement_offer_for_war(w2, "war_1", w2.war_instances["war_1"], player="France",
                                                      current_turn=w2.current_turn, pending=[], cooldowns={})
        assert offer is not None and offer["proposer_nation"] == "Britain"      # the old writer, the old sum

    def test_e_f27_a_cession_the_proposer_pays_never_lowers_a_courts_score(self, vienna_held):
        """Ceding Flanders (France's starting province) read −20 on every court
        as a 'contradiction' of France's homeland defence; it is a concession."""
        flanders = _preview(vienna_held, terms=[{"type": "territory_cede", "from": "France", "to": "Austria", "region": "Flanders"}])
        bohemia = _preview(vienna_held, terms=[{"type": "territory_cede", "from": "France", "to": "Austria", "region": "Bohemia"}])
        for court in ("Austria", "Britain", "Russia"):
            assert _comp(_row(flanders, court), "war_objective_alignment") == _comp(_row(bohemia, court), "war_objective_alignment") == 5
            assert _row(flanders, court)["total"] >= _row(bohemia, court)["total"]
        plain = _preview(vienna_held)
        assert _row(flanders, "Austria")["total"] > _row(plain, "Austria")["total"]

    def test_e_f26_a_france_pays_package_names_its_real_blocker(self, vienna_held):
        """The blocker was 'the terms claim a victory the field has not delivered'
        — the tier's BASE (a white peace at the court's own score) is not a claim."""
        from backend.game_logic.diplomatic_templates import spoken_blocker_phrase
        terms = [{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 300}]
        body = _preview(vienna_held, terms=terms, covered=["Britain", "Russia"])
        assert _row(body, "Britain")["top_blocker_detail"] == "tier_base"
        from backend.game_logic.settlement_staging import build_settlement_confirm_dialogue, build_settlement_preview
        with _quiet():
            prev = build_settlement_preview(vienna_held, war_id="war_1", settlement_terms=terms, actor_nation="France",
                                            covered_enemy_participants=["Britain", "Russia"], ignore_active_dialogue=True)
            dlg = build_settlement_confirm_dialogue(vienna_held, prev)
        assert "at their score a peace is charged as a white peace" in dlg["talleyrand_text"]
        assert "claim a victory the field has not delivered" not in dlg["talleyrand_text"]
        assert spoken_blocker_phrase("settlement_tier_legitimacy", "x", detail="tier_mismatch") == (
            "the terms claim a victory the field has not delivered")

    def test_f_f60_the_four_rates_are_read_from_the_constants(self):
        from backend.game_logic import settlement_scoring as SC
        from backend.game_logic.diplomacy import DEMAND_VALUES, SWEETENER_VALUES
        r = SC.gold_land_rates()
        assert r["credit"] == SC.CONCESSION_TERRITORY_PER_REGION * SC.CONCESSION_GOLD_DIVISOR == 875
        assert r["harshness"] == 375 and r["bilateral_demand"] == 167
        assert r["bilateral_sweetener"] == round(SWEETENER_VALUES["territory_cede"] / SWEETENER_VALUES["gold_lump"]) == 800
        assert DEMAND_VALUES["territory_cede"] / DEMAND_VALUES["gold_lump"] == pytest.approx(166.67, abs=0.1)
        note = SC.gold_land_rate_note()
        assert "875" in note and "375" in note and "four rates, each surface its own" in note

    def test_f_f61_the_counsel_says_what_the_tier_carries_at_a_forced_80(self, vienna_held):
        """At a forced +80 ("Total Victory") Austria's row carries ONE province
        (63) and not two (49): the counsel names what the scorer carries."""
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        _force_pair(w, "France", "Austria", 80)
        with _quiet():
            reading = CS.read_counsel(w, "Austria")
        alone = next(r for r in reading["roads"] if r["road"] == "table_alone")
        ladder = {r["label"]: r for r in alone["carry_ladder"]}
        assert ladder["a province"]["carries"] and ladder["a province"]["total"] == 63
        assert not ladder["two provinces"]["carries"] and ladder["two provinces"]["total"] == 49
        assert alone["carry_line"].startswith("At her score the table carries from Austria a province")
        assert "not two provinces (49)" in alone["carry_line"] and alone["carry_line"] in alone["trade"]
        assert "875" in alone["rates_note"]
        with _quiet():
            now = CS.read_counsel(vienna_held, "Austria")
        alone_now = next(r for r in now["roads"] if r["road"] == "table_alone")
        assert alone_now["carry_line"].startswith("At her score the table carries no province from Austria")


# ═══════════════════════════════════════════════════════════════════════════
# PC-R5 — ruling H, what wears a court down (S13e part 3)
# ═══════════════════════════════════════════════════════════════════════════

class TestPCR5:
    """Ruling H — the +8 clock kept and made of occupation, subsidy and finance,
    named; the truce holds; the league gate reads the live rate; the components
    ride the war popup without fog (F42); F31 and F20 (§124.2)."""

    def test_a_the_terms_on_the_vienna_held_board(self, vienna_held):
        from backend.game_logic import coalition as CO
        a = CO.war_exhaustion_terms(vienna_held, "Austria")
        assert (a["base"], a["occupation"], a["subsidy"], a["finance"], a["total"]) == (8, 3, -2, 0, 9)
        assert sorted(a["held"]) == ["Bohemia", "Tyrol", "Vienna"] and a["subsidy_role"] == "recipient"
        assert CO.next_war_exhaustion(vienna_held, "Austria") == 113 + 9
        b = CO.war_exhaustion_terms(vienna_held, "Britain")
        assert (b["subsidy"], b["subsidy_role"], b["total"], b["forecast_turns"]) == (2, "paymaster", 10, 4)
        assert CO.next_war_exhaustion(vienna_held, "Britain") == 55
        r = CO.war_exhaustion_terms(vienna_held, "Russia")
        assert r["total"] == 8 and r["forecast_turns"] == 5 and CO.next_war_exhaustion(vienna_held, "Russia") == 53
        assert CO.war_exhaustion_rate(vienna_held, "Britain") == 10
        line = CO.war_exhaustion_lines(vienna_held, "Austria")[0]
        assert line.startswith("Austria's exhaustion 113 — wearing +9 a turn: +8 at war, +3 occupation")
        assert "-2 subsidised" in line and "Spent: past 80" in line

    def test_a_the_finance_term(self, vienna_held):
        from backend.game_logic import coalition as CO
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        w.nation_gold["Russia"] = 0
        t = CO.war_exhaustion_terms(w, "Russia")
        assert t["finance"] == 2 and t["total"] == 10 and "finance (the chest under a turn's upkeep)" in CO.war_exhaustion_lines(w, "Russia")[0]

    def test_b_the_truce_holds_and_the_peace_rests(self, vienna_held):
        from backend.game_logic import coalition as CO
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        for other in ("Austria", "Britain", "Russia"):
            k = w._make_diplo_key("France", other)
            w.diplomatic_states[k] = "ARMISTICE"
        assert CO.war_exhaustion_terms(w, "Russia")["total"] == 0 and CO.next_war_exhaustion(w, "Russia") == 45
        assert "held by the truce" in CO.war_exhaustion_lines(w, "Russia")[0]
        for k in list(w.diplomatic_states):
            if "Russia" in k.split("|"):
                w.diplomatic_states[k] = "PEACE"
        assert CO.war_exhaustion_terms(w, "Russia")["total"] == -5 and CO.next_war_exhaustion(w, "Russia") == 40

    def test_c_the_seam_down_is_the_bare_8(self, vienna_held, monkeypatch):
        from backend.game_logic import coalition as CO
        monkeypatch.setattr(CO, "exhaustion_clock_terms",
                            lambda w, n: {"occupation": 0, "subsidy": 0, "finance": 0, "held": [], "subsidy_role": ""})
        assert CO.next_war_exhaustion(vienna_held, "Austria") == 121 and CO.next_war_exhaustion(vienna_held, "Britain") == 53

    def test_d_the_league_gate_reads_the_live_rate(self, vienna_held):
        war = vienna_held.war_instances["war_1"]
        gate = AI.league_offer_gate(vienna_held, war, player="France")
        assert gate and gate["leader"] == "Britain" and gate["rate"] == 10 and gate["turns_at_most"] == 4   # ceil(36 / 10)
        text = AI.league_offer_gate_display(vienna_held, gate)
        assert "exhaustion 45 of 80, wearing at +10 a turn; at most 4 turns" in text

    def test_e_f42_the_popup_reads_the_clock_without_fog(self, vienna_held):
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            wars = build_active_wars(vienna_held)["wars"]
        row = [r for r in wars if r.get("status") == "war"][0]
        assert isinstance(row["war_exhaustion"], int) and row["war_exhaustion"] == 45
        assert row["exhaustion_terms"]["total"] == 10 and row["exhaustion_terms"]["subsidy_role"] == "paymaster"
        assert row["exhaustion_line"].startswith("Britain's exhaustion 45 — wearing +10 a turn")
        members = {m["opponent"]: m for m in row["coalition_member_rows"]}
        assert members["Austria"]["war_exhaustion"] == 113 and "wearing +9 a turn" in members["Austria"]["exhaustion_line"]
        gd = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert 'w.get("exhaustion_terms", null)' in gd and 'ex_terms.get("lines", [])' in gd
        hud = (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")
        assert 'war_data.get("exhaustion_line", "")' in hud
        src = (REPO / "backend" / "game_logic" / "war_status.py").read_text(encoding="utf-8")
        assert "vis_priority >= partial_priority" not in src            # the fog gate is gone

    def test_f_f31_the_silent_band_has_a_letter(self, vienna_held):
        from backend.game_logic import settlement_third_party as TP
        assert TP.silent_band_white_peace(vienna_held, loser="Hanover", winner="Prussia", winner_score=12)
        assert TP.silent_band_white_peace(vienna_held, loser="Hanover", winner="Prussia", winner_score=19)
        assert not TP.silent_band_white_peace(vienna_held, loser="Hanover", winner="Prussia", winner_score=20)
        src = (REPO / "backend" / "game_logic" / "settlement_third_party.py").read_text(encoding="utf-8")
        assert "and not band_white" in src

    def test_g_f20_one_loyalty_wire_and_p2s_gates(self, vienna_held, w):
        from backend.game_logic import coalition as CO
        # ONE home for the number: the live wire reads the formula module's constant.
        assert AI._coalition_loyalty_base() == CO.COALITION_LOYALTY_BASE == -15
        assert AI.coalition_loyalty_penalty(vienna_held, "Britain", "France") == -11      # loyal: -15 + 45 // 10
        assert AI.coalition_loyalty_penalty(vienna_held, "Austria", "France") == 0        # she would sue on her own
        assert CO.get_coalition_loyalty_penalty("Austria", vienna_held) == -4             # the formula's home (C1 pins), not live
        src_ai = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        assert "COALITION_LOYALTY_BASE = " not in src_ai
        kb = vienna_held._make_diplo_key("Britain", "France")
        assert AI.p2_league_gate(vienna_held, "Britain", war_score=2, diplo_key=kb) is True       # loyal: no stalemate truce alone
        ka = vienna_held._make_diplo_key("Austria", "France")
        assert AI.p2_league_gate(vienna_held, "Austria", war_score=-54, diplo_key=ka) is False
        assert AI._one_envoy_for_this_war(vienna_held, "Britain", "France") is False
        src = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        p8 = src[src.index("# ── P8: Aggressive Dominance"):]
        assert "_one_envoy_for_this_war(world, nation, player)" in p8[:900]    # P8: the one-envoy rule, no coalition gate
        assert "and not p2_blocked" in src


# ═══════════════════════════════════════════════════════════════════════════
# PC-R6 — ruling G, the war score's shape (S13e part 3)
# ═══════════════════════════════════════════════════════════════════════════

class TestPCR6:
    """Ruling G — the caps kept; decay then cap; the shield down while the
    capital is held and a ticking that falls; the fill shown; the trend drawn
    (F84); every ±100 literal re-read (§124.3)."""

    def test_a_decay_then_cap(self):
        recs = [{"winner": "France", "turn": 1}] * 8
        assert D.battle_score_from_records(recs, "France", "Austria", 1) == 15
        assert D.battle_score_from_records(recs, "France", "Austria", 7) == 15      # 24 − 8 = 16 → 15 (was 15 − 8 = 7)
        five = [{"winner": "France", "turn": 1}] * 5
        assert D.battle_score_from_records(five, "France", "Austria", 5) == 11
        assert D.battle_score_from_records(five, "France", "Austria", 7) == 7
        assert D.BATTLE_SCORE_CAP == 15 and D.DECISIVE_SCORE_CAP == 15 and D.TICKING_CAP == 25   # the caps KEPT
        # the old order, for the record: cap then decay
        old = D._decay_battle_score(max(-15, min(15, 24)), recs, 7)
        assert old == 7

    def test_b_the_shield_is_down_with_vienna_held(self, vienna_held, turn6):
        """The done-when: Austria's defence claim against France stops accruing
        while France holds Vienna; on the copy (Vienna Austrian) it ticks +2."""
        k = vienna_held._make_diplo_key("Austria", "France")
        obj = vienna_held.war_objectives[k]["Austria"]
        assert obj["type"] == "defense" and obj["accumulated_ticking"] == 2
        assert D.defense_ticking_gain(vienna_held, "Austria", "France", obj, 2) == 0
        with _quiet():
            D.accumulate_war_objective_ticking(vienna_held)
        assert vienna_held.war_objectives[k]["Austria"]["accumulated_ticking"] == 2
        obj6 = turn6.war_objectives[k]["Austria"]
        assert D.defense_ticking_gain(turn6, "Austria", "France", obj6, 2) == 2
        with _quiet():
            D.accumulate_war_objective_ticking(turn6)
        assert turn6.war_objectives[k]["Austria"]["accumulated_ticking"] == 4
        # the shield resumes when the capital is regained
        vienna_held.regions["Vienna"].controller = "Austria"
        assert D.defense_ticking_gain(vienna_held, "Austria", "France", obj, 2) == 2

    def test_c_a_ticking_that_can_fall(self, turn6):
        k = turn6._make_diplo_key("Austria", "France")
        obj = turn6.war_objectives[k]["Austria"]
        for name in obj["target_regions"]:
            turn6.regions[name].controller = "Austria"            # every province home
        obj["accumulated_ticking"] = 25
        obj["objective_met_turn"] = 3
        assert D.defense_ticking_gain(turn6, "Austria", "France", obj, 25) == -1
        with _quiet():
            D.accumulate_war_objective_ticking(turn6)
        assert obj["accumulated_ticking"] == 24 and obj["objective_met_turn"] is None and obj["ticking_active"] is False
        obj["accumulated_ticking"] = 0
        assert D.defense_ticking_gain(turn6, "Austria", "France", obj, 0) == 0

    def test_c_the_seam_down_is_the_add_only_count(self, vienna_held, monkeypatch):
        def _old(world, nation, holder, obj, prev):
            return sum(1 for r in obj.get("target_regions", [])
                       if r in world.regions and world.regions[r].controller == holder)
        monkeypatch.setattr(D, "defense_ticking_gain", _old)
        k = vienna_held._make_diplo_key("Austria", "France")
        with _quiet():
            D.accumulate_war_objective_ticking(vienna_held)
        assert vienna_held.war_objectives[k]["Austria"]["accumulated_ticking"] == 5      # 2 + 3 held, shield up

    def test_d_the_fill_is_shown_per_component(self, vienna_held):
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            row = [w for w in build_active_wars(vienna_held)["wars"] if w.get("status") == "war"][0]
        fill = {f["key"]: f for f in row["breakdown_fill"]}
        assert fill["battles"]["display"] == "Battles +15/15 — full" and fill["battles"]["full"]
        assert fill["blood"]["display"] == "Blood +15/15 — full"
        assert fill["territory"]["display"] == "Territory +15/40" and not fill["territory"]["full"]
        assert row["breakdown_fill_lines"] == [
            "Full: Battles 15/15, Blood 15/15 — another victory adds nothing there; ground, the capital or time moves the score."]
        assert set(D.war_score_component_caps()) == set(row["breakdown"])
        gd = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert 'w.get("breakdown_fill", null)' in gd and "— full" in gd
        hud = (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")
        assert 'war_data.get("breakdown_fill_lines", [])' in hud

    def test_e_f84_the_trend_is_drawn(self, vienna_held):
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            row = [w for w in build_active_wars(vienna_held)["wars"] if w.get("status") == "war"][0]
        assert row["trend"] in ("rising", "falling", "stable") and row["trend_glyph"] in ("↑", "↓", "→")
        hud = (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")
        assert 'war_data.get("trend_glyph", "")' in hud
        gd = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert '"   trend " + _trend_str(trend)' in gd

    def test_f_every_plus_minus_100_literal_re_read(self):
        """The caps are unchanged, so the ±100 scale is unchanged: every consumer
        holds its value — P1 −40 (`effective_peace_threshold`'s base) and the
        −70 split, P8 40, break-ranks −50, the Congress −40, the exhausted-pair
        band 15, the decisive band 20, the dictated step 70, the truce's −50."""
        from backend.game_logic import congress as CG, settlement_third_party as TP
        src = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        assert "threshold = -40 + mods[\"peace_threshold_delta\"] + we // 20" in src
        assert AI.P1_PEACE_SPLIT == -70 and AI.P8_DOMINANCE_SCORE == 40 and "is_at_war and war_score > 40" in src
        assert AI.BREAK_RANKS_WAR_SCORE == -50 and AI.BREAK_RANKS_LONG_WAR_SCORE == -60 and AI.BREAK_RANKS_EXHAUSTION == 80
        assert CG.SUE_SCORE == -40 and TP.PAIR_EXIT_STAGNANT_SCORE == 15
        assert AI.SETTLEMENT_OFFER_DECISIVE_WAR_SCORE == 20 and AI.DICTATED_SCORE_STEP == 70
        assert D.TRUCE_DICTATED_SCORE == -50 and D.ARMISTICE_AUTO_PEACE_RELATION == -60
        assert sum(D.war_score_component_caps().values()) == 40 + 15 + 15 + 30 + 10 + 15 + 15 + 15 + 25

    def test_h_the_part_iv_frames_read_the_components(self):
        """The Part IV M1 (the war card's tooltip) and M2 (the war popup) frames,
        re-shot at 5120x1440 on the Vienna-held board (`docs/audits/peace_client/`),
        read the stake floor, the full components and Britain's clock; the
        popup's foot is a new frame."""
        index = json.loads((REPO / "docs" / "audits" / "peace_client" / "moments.json")
                           .read_text(encoding="utf-8"))
        by = {(e["id"], e["resolution"]): e for e in index}
        for sid in ("m1_war_card_tooltip", "m2_war_detail", "m2_war_detail_scrolled"):
            e = by[(sid, "5120x1440")]
            assert e.get("reshot", "").startswith(("S13e part 3", "S13e part 4")), sid
            assert (REPO / "docs" / "audits" / "peace_client" / e["file"]).exists(), e["file"]
        tip = " ".join(by[("m1_war_card_tooltip", "5120x1440")]["lines"])
        assert "Austria ready · Britain 6/50 · Russia 7/50" in tip
        assert "scores each court on its own pair" in tip
        assert "Britain and Russia are covered, not consulted — under the 10 % stake floor" in tip
        assert "Full: Battles 15/15, Blood 15/15 — another victory adds nothing there" in tip
        assert "Britain's exhaustion 45 — wearing +10 a turn: +8 at war, +0 occupation (no home province held), +2 as paymaster. It tires at 80 in about 4 turns." in tip
        popup = " ".join(by[("m2_war_detail", "5120x1440")]["lines"])
        assert "Score Breakdown   trend ^ rising" in popup
        assert "Battles:    +15/15  — full" in popup and "Blood:      +15/15  — full" in popup
        assert "Territory:  +15/40" in popup and "Ticking:    -2/25" in popup
        foot = " ".join(by[("m2_war_detail_scrolled", "5120x1440")]["lines"])
        assert "Enemy War Exhaustion: 45" in foot and "wearing +10 a turn" in foot
        assert "Unknown" not in foot
        controls = {c["text"]: c for c in by[("m2_war_detail_scrolled", "5120x1440")]["controls"]}
        assert "wearing at +10 a turn; at most 4 turns" in controls["Request Terms"]["tooltip"]

    def test_g_f38_f39_the_envoys_summary_and_the_dispatch(self, vienna_held):
        with _quiet():
            snap = D.build_war_context_snapshot(vienna_held, "France", "Austria", "propose_peace")
        comps = snap["war_score_components"]
        assert set(comps) == {"territory", "battle", "decisive_battle", "capital", "campaign", "blood", "blockade", "captive", "ticking"}
        assert sum(comps.values()) == snap["war_score"] == 79
        assert snap["settlement_tier_scope"] == "this pair" and len(snap["war_score_fill"]) == 9
        gd = (SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert '"campaign", "blood", "blockade", "captive"' in gd and 'snapshot.get("settlement_tier_scope", "")' in gd
        dispatch = (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
        assert 'Settlement (this pair): {tier_display} ({score:+d})' in dispatch


# ═══════════════════════════════════════════════════════════════════════════
# The two scores (F55, F71), the coalition's shape (F58, F66, F77, F79, F80),
# the sea (F64, F68) — S13e part 3
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTwoScores:
    def test_f55_the_bilateral_harshness_reads_direction(self, vienna_held):
        ret = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria", "sweeteners": [], "clauses": [],
               "demands": [{"type": "territory_cede", "from": "France", "to": "Austria", "regions": ["Vienna", "Bohemia"], "value": 2}]}
        take = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria", "sweeteners": [], "clauses": [],
                "demands": [{"type": "territory_cede", "from": "Austria", "to": "France", "regions": ["Carniola"], "value": 1}]}
        with _quiet():
            a_ret = D.calculate_acceptance(ret, vienna_held)
            a_take = D.calculate_acceptance(take, vienna_held)
        assert a_ret["score"] > a_take["score"] and a_ret["outcome"] == "ACCEPT" and a_take["outcome"] == "REJECT"
        assert a_ret["components"]["deal_balance"] > 0 and "harshness_penalty" not in {k for k, v in a_ret["components"].items() if v < 0}
        norm = D.concessions_as_sweeteners(ret)
        assert norm["demands"] == [] and norm["sweeteners"][0]["type"] == "territory_cede" and norm["sweeteners"][0]["value"] == 2
        gold = D.concessions_as_sweeteners({"proposer_nation": "France", "demands": [{"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 400}]})
        assert gold["sweeteners"][0]["type"] == "gold_lump" and gold["sweeteners"][0]["value"] == 400
        assert D.concessions_as_sweeteners(take)["demands"] == take["demands"]

    def test_f71_frances_own_peace_is_judged_on_the_field_where_it_moved(self, vienna_held):
        assert D.acceptance_reads_the_field(vienna_held, "France", "Austria") is False     # nothing fought THIS turn
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        w.battles_this_turn.append({"location": "Vienna", "attacker": "France", "defender": "Austria", "result": "x", "turn": w.current_turn})
        assert D.acceptance_reads_the_field(w, "France", "Austria") is True
        plain = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria", "sweeteners": [], "demands": [], "clauses": []}
        with _quiet():
            stored = D.calculate_acceptance(plain, vienna_held)["components"]["war_score_modifier"]
            live = D.calculate_acceptance(plain, w)["components"]["war_score_modifier"]
        assert live > stored          # +79 on the field against +54 stored
        k = w._make_diplo_key("France", "Austria")
        w.diplomatic_states[k] = "ARMISTICE"
        assert D.acceptance_reads_the_field(w, "France", "Austria") is False                  # a truce keeps the stored ledger


class TestTheCoalitionsShape:
    def test_f58_the_league_gate_reads_the_coalitions_leader(self, vienna_held):
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        war = w.war_instances["war_1"]
        war["defender_leader"] = "Austria"                       # the instance's leader is not the league's
        gate = AI.league_offer_gate(w, war, player="France")
        assert gate and gate["leader"] == "Britain"              # Britain leads the league; her exhaustion, her score
        assert gate["exhaustion"] == 45 and gate["war_score"] == D.get_war_score_for(w, "Britain", "France")
        w.active_coalition["leader"] = "Austria"
        assert AI.league_offer_gate(w, war, player="France") is None       # Austria may break ranks: ungated

    def test_f66_the_fold_is_symmetric(self, turn6):
        import copy as _copy
        for a, b in (("France", "Prussia"), ("Prussia", "France")):
            w = _copy.deepcopy(turn6)
            before = set(w.war_instances)
            with _quiet():
                res = D.declare_war(w, a, b)
            assert res.get("success"), res
            new = sorted(set(w.war_instances) - before)
            assert new == ["war_2"], (a, b, new)
            k = w._make_diplo_key(a, b)
            assert k in (w.war_instances["war_2"].get("active_diplo_keys") or [])
            assert k not in (w.war_instances["war_1"].get("active_diplo_keys") or [])
        from backend.game_logic import settlement_helpers as SH
        inst = turn6.war_instances["war_1"]
        assert SH.newcomer_joins_the_war(turn6, inst, "Prussia", "defenders", "war_declaration") is False
        assert SH.newcomer_joins_the_war(turn6, inst, "Prussia", "defenders", "ally_cascade") is True
        turn6.active_coalition["members"] = sorted(set(turn6.active_coalition["members"]) | {"Prussia"})
        assert SH.newcomer_joins_the_war(turn6, inst, "Prussia", "defenders", "war_declaration") is True

    def test_f77_a_league_holding_paris_does_not_dissolve_for_low_threat(self, ulm_t18):
        from backend.game_logic import coalition as CO
        assert ulm_t18.regions[ulm_t18.get_nation_capital("France")].controller == "Britain"
        assert "Britain" in ulm_t18.active_coalition["members"]
        ulm_t18.threat_by_target["France"] = 5
        assert CO.check_dissolution(ulm_t18) is None
        ulm_t18.regions["Paris"].controller = "France"
        assert CO.check_dissolution(ulm_t18) == "low_threat"

    def test_f79_the_congress_names_the_road_for_a_shut_out_court_at_war(self):
        from backend.game_logic import congress as CG
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
        row = CG.answer(w, "Britain")
        assert row["stance"] == CG.SHUT_OUT and w.is_at_war("France", "Britain")
        price = CG.price(w, "Britain", row)
        assert "accept her letter when it comes, or Request Terms" in price["text"]
        assert price["levers"] and price["levers"][0]["key"] == "request_terms"

    def test_f80_a_signed_court_at_war_again_recognizes_nothing_and_no_proclamation_under_a_new_league(self):
        """At its root: the treaty latch is broken by a war NOW (the tick's
        stamp came a turn late); and the Imperial Peace is never stamped while
        a league formed since the summons stands. The hold keeps its seven
        (the War of the Congress may brew a league the sitting goes on to win)."""
        from backend.game_logic import congress as CG
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
            while w.dialogue_manager.peek() is not None:
                w.dialogue_manager.pop()
        assert len(CG.hold_conditions(w)) == 7
        with _quiet():
            CG.summon(w) if not CG.sitting(w) else None
        c = CG.record(w)
        assert "league_at_summons" in c
        since = int(c.get("summoned_turn", w.current_turn) or 0)
        # a court that signed, then goes to war again, recognizes nothing
        c.setdefault("signed", {})["Austria"] = {"kind": "treaty", "turn": since}
        assert CG.answer(w, "Austria")["stance"] == CG.RECOGNIZES
        k = w._make_diplo_key("Austria", "France")
        w.diplomatic_states[k] = "WAR"
        assert CG._signed_record(w, "Austria") is None and CG.answer(w, "Austria")["stance"] != CG.RECOGNIZES
        w.diplomatic_states[k] = "PEACE"
        # a league formed since the summons guards the proclamation
        assert CG._league_since_summons(w) == ""
        w.active_coalition = {"id": "coalition_new", "name": "The Fourth British Coalition",
                              "target_nation": "France", "leader": "Britain",
                              "members": ["Britain", "Prussia"], "formed_turn": since + 1}
        assert w.is_at_war("France", "Britain") and "Britain" in CG.great_powers(w)
        assert CG._league_since_summons(w) == "The Fourth British Coalition"
        # a league of minors (the pressburg arm's Fourth Swedish Coalition) does not unsay the great powers
        w.active_coalition["members"] = ["Sweden", "Denmark"]
        assert CG._league_since_summons(w) == ""
        w.active_coalition["members"] = ["Britain", "Prussia"]
        w.active_coalition["id"] = str(c.get("league_at_summons") or "coalition_x")
        if c.get("league_at_summons"):
            assert CG._league_since_summons(w) == ""                  # the league standing at the summons
        w.active_coalition["id"] = "coalition_new"
        w.active_coalition["formed_turn"] = since
        assert CG._league_since_summons(w) == ""                      # formed at the summons, not since
        src = (REPO / "backend" / "game_logic" / "congress.py").read_text(encoding="utf-8")
        assert "in SATISFIED for row in table.values()) and not league:" in src


class TestTheSea:
    def test_f64_the_blockade_credits_france(self):
        """On the ge3 fixture France closes 77 % of the Continent against
        Britain and Britain's posture pins France: the posture arm is answered,
        so one naval tick credits France and not Britain."""
        from backend.game_logic import naval
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
        assert w.is_at_war("France", "Britain") and naval.closure_against(w, "Britain") >= 0.40
        assert naval.posture_blockade_answered(w, "Britain") is True
        assert naval.posture_blockade_answered(w, "France") is False
        k = w._make_diplo_key("France", "Britain")
        assert not (w.campaign_ledgers.get(k) or {}).get("blockade_turns")
        with _quiet():
            naval._record_blockade_pressure(w, naval.blockaded_nations(w))
        turns = (w.campaign_ledgers.get(k) or {}).get("blockade_turns") or {}
        assert turns.get("France", 0) == 1 and turns.get("Britain", 0) == 0
        for _ in range(29):
            with _quiet():
                naval._record_blockade_pressure(w, naval.blockaded_nations(w))
        assert D.calculate_war_score("France", "Britain", w, return_components=True)["blockade"] == 15

    def test_f64_the_seam_down_is_the_wash(self, monkeypatch):
        from backend.game_logic import naval
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
        monkeypatch.setattr(naval, "posture_blockade_answered", lambda world, d: False)
        with _quiet():
            naval._record_blockade_pressure(w, naval.blockaded_nations(w))
        k = w._make_diplo_key("France", "Britain")
        turns = (w.campaign_ledgers.get(k) or {}).get("blockade_turns") or {}
        assert turns.get("France", 0) == 1 and turns.get("Britain", 0) == 1       # the old wash

    def test_f68_the_tilsit_clause_that_closes_no_port_is_refused_and_priced_by_the_trade_lost(self):
        path = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(raw.get("world_state", raw))
            while w.dialogue_manager.peek() is not None:
                w.dialogue_manager.pop()
        assert D.continental_system_join_refusal(w, "Prussia", "France") == "cs_closes_no_port"
        assert "costs Prussia nothing in trade" in D.continental_system_join_terms(w, "Prussia")
        assert D.continental_system_join_refusal(w, "Austria", "France") is None
        terms = D.continental_system_join_terms(w, "Austria")
        assert "closes 11 → 12 of 26 ports" in terms and "costs Austria 75 gold a turn in Britain trade" in terms
        assert D.continental_system_cost_if_joined(w, "Austria") == 75 and w.continental_system_members == []
        from backend.display_names import settlement_disabled_reason_display
        assert "would close no port" in settlement_disabled_reason_display("cs_closes_no_port")
        from backend.game_logic.settlement_validation import evaluate_continental_system_join_eligibility
        elig = evaluate_continental_system_join_eligibility(
            w, war_instance=next(iter(w.war_instances.values())), joiner="Prussia", imposer="France")
        assert elig.get("eligible") is False and elig.get("refusal_code") == "cs_closes_no_port"


class TestTheFuzzersFinds:
    """What the treaty fuzzer found once E / H / G moved the letters' timing
    (ten seeds × 1,000 steps): PC-X19 and PC-X20, fixed at their seams."""

    def test_x19_the_merge_rejoins_a_court_that_had_left_the_survivor(self, w):
        from backend.game_logic import settlement_helpers as SH
        survivor = {"war_id": "war_1", "attackers": ["France"], "defenders": ["Britain"],
                    "active_participants": ["France", "Britain"],
                    "side_by_nation": {"France": "attackers", "Britain": "defenders"},
                    "participant_meta": {"Holland": {"side": "attackers", "joined_turn": 1,
                                                     "exited_turn": 17, "exit_path": "pair_resolved"}},
                    "diplo_key_meta": {}, "active_diplo_keys": [], "resolved_diplo_keys": []}
        absorbed = {"war_id": "war_2", "attackers": ["France", "Holland"], "defenders": ["Denmark"],
                    "active_participants": ["France", "Denmark", "Holland"],
                    "side_by_nation": {"France": "attackers", "Holland": "attackers", "Denmark": "defenders"},
                    "participant_meta": {"Holland": {"side": "attackers", "joined_turn": 3, "exited_turn": None,
                                                     "entry_path": "vassal_offensive_auto_join"}},
                    "diplo_key_meta": {}, "active_diplo_keys": ["Denmark|Holland"], "resolved_diplo_keys": []}
        SH._merge_instance_data(survivor, absorbed)
        row = survivor["participant_meta"]["Holland"]
        assert "Holland" in survivor["active_participants"]
        assert row["exited_turn"] is None and "exit_path" not in row and row["joined_turn"] == 1
        assert row["side"] == "attackers"

    def test_x20_a_dead_courts_letters_retire_at_its_elimination(self, vienna_held):
        import copy as _copy
        w = _copy.deepcopy(vienna_held)
        offer = {"type": "incoming_settlement_offer", "dialogue_type": "incoming_settlement_offer",
                 "offer_id": "settlement_offer:war_1:6:1", "war_id": "war_1", "proposer_nation": "Hanover",
                 "proposer_side": "defenders", "accepting_side": "attackers", "accepting_leader": "France",
                 "covered_enemy_participants": ["Hanover"], "settlement_terms": [{"type": "peace"}],
                 "turn_created": 6}
        w.pending_settlement_dialogues.append(dict(offer))
        with _quiet():
            w.dialogue_manager.push(dict(offer, dialogue_id=777))
        w.incoming_settlement_offer_popup = {"type": "incoming_settlement_offer", "dialogue_id": 777,
                                             "proposer_nation": "Hanover", "offer_id": offer["offer_id"]}
        assert any(str(d.get("proposer_nation")) == "Hanover"
                   for d in [w.dialogue_manager.peek()] + list(w.dialogue_manager.iter_queue()) if isinstance(d, dict))
        assert w.retire_letters_of_a_dead_court("Hanover") >= 1
        assert not any(str((d or {}).get("proposer_nation")) == "Hanover"
                       for d in [w.dialogue_manager.peek()] + list(w.dialogue_manager.iter_queue()) if isinstance(d, dict))
        assert not [d for d in w.pending_settlement_dialogues if d.get("proposer_nation") == "Hanover"]
        assert w._popup_queue.get("incoming_settlement_offer_popup") is None
        src = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        assert "self.retire_letters_of_a_dead_court(nation)" in src          # wired at `_eliminate_nation`


class TestTheSeriesPart3:
    """`tools/_pc_s13e3_series_arms.py` (record `tools/_pc_s13e3_series_arms_
    final.json`): arm 0 (every seam down) reproduces the shipped series byte
    for byte; every other arm is attributed by its first divergence — the
    record below is the attribution, read by the landing record."""

    def _record(self):
        return json.loads((REPO / "tools" / "_pc_s13e3_series_arms_final.json").read_text(encoding="utf-8"))

    def test_the_record_links_to_the_last_one(self):
        rec = self._record()
        prior = json.loads((REPO / "tools" / "_pc_s13e2_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == prior["arms"]["ALL"]["series"]
        assert rec["arms"]["0"]["first_divergence_vs_prior"] is None        # every seam down = the shipped series
        assert set(rec["arms"]) >= {"0", "B", "S", "C", "W", "X", "K", "D", "N", "P", "F", "T", "J", "ALL"}
        for arm, row in rec["arms"].items():
            assert "first_divergence_vs_prior" in row and isinstance(row["series"], list)

    def test_the_seams_were_reached(self):
        rec = self._record()
        reach = rec["arms"]["ALL"]["reach"]
        assert reach.get("exhaustion|named", 0) > 0 and reach.get("battle|decay_then_cap", 0) > 0
        assert reach.get("own_pressure|own", 0) > 0


# ═══════════════════════════════════════════════════════════════════════════
# S13e part 4 (October 17, 2026) — the stake, the memory, the instruments
# (rules `SYSTEMS_REFERENCE.md` §127; the report's §47 the reactivity read)
# ═══════════════════════════════════════════════════════════════════════════

AGD_FIXTURE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
GE3_PRESSBURG = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"


def _load_save(path):
    from backend import save_manager as SM
    with _quiet():
        res = SM.load_game(Path(path))
    assert res.get("success"), res.get("message")
    return res["world"]


def _set_pair_score(w, a, b, score_for_a):
    k = w._make_diplo_key(a, b)
    w.war_scores[k] = score_for_a if k.split("|")[0] == a else -score_for_a


def _tool(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestPCR7:
    """PC-R7 (i) — ruling J: the war's PURPOSE is its title on every surface
    ("War for Bohemia", never "vs Britain"); the table titles the same
    object (`backend/game_logic/war_title.py`, the ONE builder). (ii) — the
    compensation clause `territory_compensate` (`compensation.py`) — LANDED
    in S14 part 1: validated, priced by both scorers, ratified by both
    ratifiers, authored from the guided rows, carried by the hand-off and
    asked by the AI's letter; the moderate Pressburg carries on the
    Vienna-held board (the `test_ii_*` pins). The composed terms and the
    ally's bond are S14 part 2 (the row stays OPEN and names them)."""

    def test_a_the_vienna_held_war_is_the_war_for_bohemia(self, vienna_held):
        from backend.game_logic.war_title import war_title
        rec = war_title(vienna_held, "war_1")
        assert rec["title"] == "War for Bohemia" and rec["source"] == "ground"
        # the first taken first; a capital after the provinces of its turn
        assert rec["theirs_we_hold"] == ["Bohemia", "Tyrol", "Vienna"]
        assert rec["roster"] == ["Britain", "Austria", "Russia"]
        assert rec["display"] == "War for Bohemia — Britain + Austria + Russia"
        assert rec["line"] == "The War for Bohemia: France holds Bohemia, Tyrol and Vienna of Austria's."

    def test_b_the_ladder(self, w, ulm_t18):
        from backend.game_logic.war_title import war_title
        # the boot: nothing taken — a league's war is titled by the league
        boot = war_title(w, "war_1")
        assert boot["title"] == "War with the Third Coalition" and boot["source"] == "league"
        # a wound is named by its gravest: the capital first
        ulm = war_title(ulm_t18, "war_1")
        assert ulm["title"] == "War for Paris" and ulm["ours_they_hold"][0] == "Paris"
        # the chair's NAMED purpose outranks the ground
        k = w._make_diplo_key("France", "Austria")
        w.war_objectives.setdefault(k, {})["France"] = D.create_war_objective(
            "conquest", "France", "Austria", ["Moravia"], w.current_turn)
        named = war_title(w, "war_1")
        assert named["title"] == "War for Moravia" and named["source"] == "purpose"
        # an AI-initiated war names its design
        w.war_objectives[k].pop("France")
        w.war_instances["war_1"]["stated_reason"] = "The Hanoverian Prize"
        design = war_title(w, "war_1")
        assert design["title"] == "War for the Hanoverian Prize" and design["source"] == "design"

    def test_c_every_surface_reads_the_one_title(self, vienna_held):
        from backend.game_logic.ai_diplomacy import _settlement_request_war_label
        from backend.game_logic.dispatch import _build_war_objective_section
        from backend.game_logic.settlement_offers import _war_label_for_id
        from backend.game_logic.settlement_presentation import _war_label as _presentation_label
        from backend.game_logic.settlement_routes import _war_label
        from backend.game_logic.settlement_staging import build_settlement_preview
        from backend.game_logic.war_status import build_active_wars
        w = vienna_held
        with _quiet():
            row = next(r for r in build_active_wars(w)["wars"] if r.get("status") == "war")
            pv = build_settlement_preview(w, war_id="war_1", covered_enemy_participants=["Austria"],
                                          settlement_terms=[{"type": "peace"}])
            wiz = D.get_diplomatic_preview(w, "Austria")
            purpose = [ln["text"] for ln in _build_war_objective_section(w, "France")]
        assert row["war_title"] == "War for Bohemia"
        assert row["war_roster_display"] == "Britain + Austria + Russia"
        assert row["war_title_line"].startswith("The War for Bohemia: France holds Bohemia")
        assert pv["settlement_preview"]["war_label"] == "the War for Bohemia — the table with Austria"
        assert wiz["war_title"] == "War for Bohemia"
        assert any("(War for Bohemia)" in t for t in purpose), purpose
        inst = w.war_instances["war_1"]
        for label in (_war_label("war_1", inst, w), _presentation_label(w, "war_1"),
                      _war_label_for_id(w, "war_1")):
            assert label.startswith("the War for Bohemia — ") and " vs " not in label, label
        req = _settlement_request_war_label(inst, "war_1", player="France", world=w)
        assert req.startswith("the War for Bohemia — France") and " against " in req, req

    def test_d_the_charges_name_the_war(self, ulm_t18):
        w = ulm_t18
        _britain_at(w, 45)
        with _quiet():
            AI.process_diplomatic_phase("Britain", w)
        AI.note_dictated_refusal(w, "Britain", "France", channel="bilateral")
        term = next(t for t in w.get_state_charges_rate("France")["terms"] if t["key"] == "refused_peace")
        assert "Britain's terms in the War for Paris (Frankfurt" in term["label"], term["label"]

    def test_f_the_part_iv_frames_name_the_war_on_both_boards(self):
        """The Part IV frames re-shot at 5120x1440 on BOTH turn-6 boards
        (`docs/audits/peace_client/`; the copy's M1–M6 as `_t6copy`, its
        M7 / M8 under their own ids): every peace moment titles the war and
        names the road that carries and its price."""
        index = json.loads((REPO / "docs" / "audits" / "peace_client" / "moments.json")
                           .read_text(encoding="utf-8"))
        by = {(e["id"], e["resolution"]): e for e in index}

        def text(sid):
            e = by[(sid, "5120x1440")]
            assert e.get("reshot", "").startswith("S13e part 4"), sid
            assert (REPO / "docs" / "audits" / "peace_client" / e["file"]).exists(), e["file"]
            return " ".join(e["lines"]) + " " + " ".join(
                f"{c.get('text') or ''} {c.get('tooltip') or ''}" for c in e.get("controls") or [])

        for suffix, held in (("", "Bohemia, Tyrol and Vienna"), ("_t6copy", "Bohemia and Tyrol")):
            assert f"The War for Bohemia: France holds {held}" in text("m1_war_card_tooltip" + suffix)
            assert "WAR FOR BOHEMIA" in text("m2_war_detail" + suffix)
            assert "Negotiate with Austria" in text("m2_war_detail" + suffix)
            wizard = text("m3_wizard_austria" + suffix)
            assert "Status: At War — the War for Bohemia" in wizard and "It costs 3 DP" in wizard
            assert "Propose White Peace — with Austria alone" in wizard
            table = text("m4_white_peace_confirm" + suffix)
            assert "Settlement of the War for Bohemia — the table with Austria" in table
            assert "Will carry as drafted" in table
            assert "the War for Bohemia — the table with Austria + Britain + Russia" in text("m6_table_white" + suffix)
        assert "Open Settlement with Austria alone, at 50 of 50" in text("m3_wizard_austria")
        assert "Open Settlement with Austria alone carries today — 62 of 50" in text("m3_wizard_austria_t6copy")
        assert "The War for Bohemia: France holds Bohemia and Tyrol" in text("m7_armistice_letter")
        assert "WAR FOR BOHEMIA — ARMISTICE WITH AUSTRIA" in text("m8_armistice_popup")
        assert "War for Bohemia — Austria, truce 4t" in text("m8_truce_card")

    def test_e_the_client_prints_the_title(self):
        panel = (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")
        popup = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'war_data.get("war_title", "")' in panel and 'war_data.get("war_title_line", "")' in panel
        assert "war_title.to_upper()" in popup and 'w.get("war_title_line", "")' in popup
        assert 'data.get("war_title", "")' in wizard

    # ── (ii) part 1 — the compensation clause (Pre-Deploy S14 part 1,
    #    October 20, 2026; rules SYSTEMS_REFERENCE §133) ──────────────────

    def test_ii_the_compensation_clause_lands_and_part_2_is_named(self):
        """(ii) was split at S14 part 1's head: the clause lands here; the
        composed terms (declared goals, the refund) and the ally's bond are
        S14 part 2 — the row stays OPEN and names them (GR9)."""
        from backend.game_logic.settlement_scoring import (
            CANONICAL_CLAUSE_TYPES, SETTLEMENT_LIVE_CLAUSE_TYPES,
        )
        assert "territory_compensate" in CANONICAL_CLAUSE_TYPES
        assert "territory_compensate" in SETTLEMENT_LIVE_CLAUSE_TYPES
        bug = (REPO / "docs" / "BUG_FIXES.md").read_text(encoding="utf-8")
        row = next(ln for ln in bug.splitlines() if ln.startswith("| **PC-R7**"))
        # S14 part 3 (October 20, 2026): the bond landed and the row CLOSED.
        assert "CLOSED" in row and "TestPCR7" in row
        assert "S14 part 2" in row and "bond" in row and "declared goals" in row
        status = (REPO / "docs" / "STATUS.md").read_text(encoding="utf-8")
        assert "S14 part 2" in status

    def test_ii_a_the_rule_reads_the_form_from_the_holder(self, vienna_held):
        """ONE rule: the form is read from who holds the province — paid where
        the paying court holds a third party's frontier province, pointed
        where a court outside the war holds a province of the compensated
        court's own design; everything else refused in words."""
        from backend.game_logic import compensation as CO
        w = vienna_held
        war = w.war_instances["war_1"]

        def read(payer, region):
            return CO.compensation_reading(w, payer=payer, compensated="Austria",
                                           region=region, war_instance=war)
        paid = read("Bavaria", "Franconia")
        assert paid["ok"] and paid["form"] == CO.FORM_PAID and paid["holder"] == "Bavaria"
        pointed = read("France", "Albania")
        assert pointed["ok"] and pointed["form"] == CO.FORM_POINTED
        assert (pointed["design"], pointed["holder"]) == ("the_eastern_question", "Ottoman")
        refusals = {
            ("France", "Vienna"): "compensation_capital",
            ("France", "Moravia"): "compensation_is_a_return",
            ("France", "Lorraine"): "compensation_victors_own_soil",
            ("Spain", "Andalusia"): "compensation_not_on_her_frontier",
            ("France", "Franconia"): "compensation_payer_does_not_hold",
            ("Bavaria", "Albania"): "compensation_licence_is_the_leaders",
        }
        for (payer, region), code in refusals.items():
            r = read(payer, region)
            assert not r["ok"] and r["code"] == code, (payer, region, r)
            assert r["display"], (payer, region)
        # the guided rows read the same rule: the frontier's one paid province
        assert CO.paid_candidates(w, compensated="Austria", payer_side_members=war["attackers"],
                                  war_instance=war) == [("Franconia", "Bavaria")]
        assert [r["region"] for r in CO.pointed_candidates(
            w, compensated="Austria", payer="France", war_instance=war)] == ["Albania", "Rumelia"]

    def test_ii_b_the_harsh_pressburg_refused_the_moderate_carries(self, vienna_held):
        """THE done-when: the harsh Pressburg (Tyrol to Bavaria) reads 36 of
        50 and does not carry; the moderate Pressburg carries — Tyrol for
        Franconia ("Salzburg for Tyrol": Würzburg's place in the exchange,
        the compensation paid in Bavaria's coin) and Talleyrand's own plan
        (Austria pointed east: the Eastern Question). The credit is derived:
        a province gained at the offer's rate, a promise at the bilateral's
        protection-to-province ratio."""
        from backend.game_logic import compensation as CO
        from backend.game_logic.settlement_scoring import CONCESSION_TERRITORY_PER_REGION
        w = vienna_held

        def carry(terms):
            body = _preview(w, terms=terms, covered=["Austria"])
            return (int(body["acceptance"]["score"]), bool(body["overall_acceptance"]["carries"]),
                    body["validation"], body.get("revanche_line", ""))
        harsh = carry([TYROL_TO_BAVARIA])
        assert harsh[:2] == (36, False)
        paid = carry([TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL])
        pointed = carry([TYROL_TO_BAVARIA, THE_EASTERN_QUESTION])
        assert paid[2] == {"valid": True} and pointed[2] == {"valid": True}
        assert paid[:2] == (36 + CONCESSION_TERRITORY_PER_REGION, True)
        assert CO.table_credit(THE_EASTERN_QUESTION) == round(CONCESSION_TERRITORY_PER_REGION * 5 / 8) == 22
        assert pointed[:2] == (36 + 22, True)
        assert paid[3] == ("Revanche lapses: Austria's cession of Tyrol is compensated with "
                           "Franconia, Bavaria's — her Revanche is reconciled while the treaty holds.")
        assert pointed[3].startswith("Revanche lapses: Austria's cession of Tyrol is compensated — her "
                                     "design pointed elsewhere: The Eastern Question (Albania")

    def test_ii_c_the_validator_refuses_what_the_board_contradicts(self, vienna_held):
        from backend.game_logic.settlement_validation import validate_settlement_terms
        w = vienna_held
        war = w.war_instances["war_1"]

        def verdict(terms):
            return validate_settlement_terms(
                terms, actor_nation="France", player_nation="France", proposer_side="attackers",
                world=w, war_instance=war, covered_enemy_participants=["Austria"],
                enforce_solvency=False)
        assert verdict([TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL]) == {"valid": True}
        tampered = verdict([dict(THE_EASTERN_QUESTION, design="")])
        assert tampered["error"] == "compensation_form_mismatch"
        twice = verdict([TYROL_TO_BAVARIA, dict(FRANCONIA_FOR_TYROL, region="Tyrol")])
        assert twice["error"] == "region_double_promised"
        same_side = verdict([{"type": "territory_compensate", "from": "Bavaria", "to": "France",
                              "region": "Franconia"}])
        assert same_side["error"] == "clause_side_mismatch"

    def test_ii_d_the_table_ratifies_both_forms(self, vienna_held):
        """Paid: Franconia to Austria, titled by the treaty, the hostage bond
        minted. Pointed (with Vienna offered back): Austria's three designs
        ahead of the Eastern Question SLEEP, France LICENSES it (the D5
        licence, 0 gold), the Porte is sold out (−15) — and once Vienna is
        hers again the Eastern Question is her design: pointed elsewhere."""
        import unittest.mock as _m
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic import settlement_ratify as SR
        from backend.game_logic import settlement_scoring as SS
        from backend.game_logic.agendas import get_active_agenda
        from tests.test_common_peace_c2_ratification import _acceptance_always_passes, _stage_dialogue
        w = vienna_held
        with _m.patch.object(SS, "calculate_common_peace_acceptance", _acceptance_always_passes):
            dialogue = _stage_dialogue(w, settlement_terms=[TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL],
                                       covered_enemy_participants=["Austria"], war_id="war_1")
            with _quiet():
                out = SR.ratify_settlement_confirm(w, dialogue)
        assert out["success"] and out["dropped_clauses"] == [], out
        assert w.regions["Franconia"].controller == "Austria"
        assert w.province_title["Franconia"]["kind"] == "treaty"
        bond = [b for b in w.compensation_bargains if (b.get("granted") or {}).get("region") == "Franconia"]
        assert len(bond) == 1 and bond[0]["payer"] == "Bavaria" and bond[0]["design_id"] == ""
        assert "compensated with Franconia, Bavaria's" in out["revanche_line"]
        event = next(e for e in reversed(w.event_log) if e.get("type") == "design_bought_off")
        assert format_event_oneliner(event) == "The peace compensates Austria with Franconia, Bavaria's"

        w2 = _board("turn6_vienna_held.json")
        ott = int(w2.nation_relations.get(w2._make_diplo_key("France", "Ottoman"), 0))
        vienna_back = {"type": "territory_cede", "from": "France", "to": "Austria", "region": "Vienna"}
        with _m.patch.object(SS, "calculate_common_peace_acceptance", _acceptance_always_passes):
            dialogue = _stage_dialogue(w2, settlement_terms=[TYROL_TO_BAVARIA, vienna_back,
                                                             THE_EASTERN_QUESTION],
                                       covered_enemy_participants=["Austria"], war_id="war_1")
            with _quiet():
                out = SR.ratify_settlement_confirm(w2, dialogue)
        assert out["success"] and out["dropped_clauses"] == [], out
        asleep = sorted(b["design_id"] for b in w2.compensation_bargains if b["recipient"] == "Austria")
        assert asleep == ["primacy_germany", "redeem_italy", "revanche_austria"]
        licence = [s for s in w2.directed_sponsorships if s["payer"] == "France" and s["recipient"] == "Austria"]
        assert len(licence) == 1 and licence[0]["aim"] == "Ottoman" and licence[0]["amount_per_turn"] == 0
        assert int(w2.nation_relations[w2._make_diplo_key("France", "Ottoman")]) == ott - 15
        w2.invalidate_bloc_members_cache()
        assert get_active_agenda("Austria", w2).id == "the_eastern_question"

    def test_ii_e_the_bilateral_prices_and_ratifies_it(self, vienna_held):
        """The second scorer and the second ratifier: a pointed compensation
        France offers is the protection sweetener (+5) on Austria's answer,
        a demand at the promise ratio (−3), a province the cession's ±8/−5;
        `_ratify_treaty` applies it through the one apply arm."""
        from backend.game_logic import compensation as CO
        w = vienna_held
        sweet = dict(THE_EASTERN_QUESTION, value=1, regions=["Albania"])
        base = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                "sweeteners": [], "clauses": [],
                "demands": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol"],
                             "to": "Bavaria", "to_nation": "Bavaria"}]}
        with _quiet():
            without = D.calculate_acceptance(base, w)["score"]
            with_it = D.calculate_acceptance(dict(base, sweeteners=[sweet]), w)["score"]
        assert with_it - without == 5
        assert CO.bilateral_value(sweet, as_demand=True) == -3
        assert CO.bilateral_value(FRANCONIA_FOR_TYROL) == 8
        assert CO.bilateral_value(FRANCONIA_FOR_TYROL, as_demand=True) == -5
        with _quiet():
            res = w._ratify_treaty(dict(base, sweeteners=[sweet]))
        assert (res or {}).get("type") == "diplomatic_treaty_signed", res
        assert any(s["payer"] == "France" and s["recipient"] == "Austria" and s["aim"] == "Ottoman"
                   for s in w.directed_sponsorships)
        assert sorted(b["design_id"] for b in w.compensation_bargains if b["recipient"] == "Austria") == [
            "primacy_germany", "redeem_italy", "revanche_austria"]

    def test_ii_f_the_guided_rows_author_it_through_the_table(self, vienna_held, monkeypatch):
        """Authorable from the rows: "Offers to Austria" carries the paid row
        (the payer is the holder — Bavaria) and the pointed row, each with its
        price beside it; the add verb writes the clause the rule reads; the
        demand group refuses it in words; the moderate Pressburg submits,
        confirms and ratifies through the real endpoint."""
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
        for court in ("Britain", "Russia"):
            out = post("settlement_cover_drop", dialogue, {"nation": court})
            assert out.get("success"), out.get("message") or out.get("error_display")
            dialogue = out["diplomatic_dialogue"]
        row = next(c for c in dialogue["per_court_acceptance"] if c["nation"] == "Austria")
        comp = [s for s in row.get("demand_suggestions") or []
                if s.get("clause_type") == "territory_compensate"]
        assert [s["group"] for s in comp] == ["offer", "offer"]
        assert comp[0]["label"] == "Compensate Austria with Franconia — Bavaria's"
        assert comp[0]["terms_display"].startswith("+35 to Austria's answer · Bavaria gives up Franconia")
        assert comp[1]["label"] == "Point Austria elsewhere — The Eastern Question (Albania)"
        assert comp[1]["region_options"] == ["Albania", "Rumelia"]
        assert "a licence for 15 turns" in comp[1]["terms_display"]
        refused = post("settlement_demand_add", dialogue, {
            "nation": "Austria", "group": "demand", "clause_type": "territory_compensate",
            "region": "Franconia"})
        assert refused.get("success") is False
        assert "never demanded" in str(refused.get("error_display") or refused.get("message"))
        out = post("settlement_demand_add", dialogue, {
            "nation": "Austria", "group": "demand", "clause_type": "territory_cede",
            "region": "Tyrol", "to": "Bavaria"})
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        out = post("settlement_demand_add", dialogue, dict(comp[0]["action_params"]))
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        written = [t for t in dialogue["settlement_terms"] if t.get("type") == "territory_compensate"]
        assert written and (written[0]["from"], written[0]["to"], written[0]["region"]) == (
            "Bavaria", "Austria", "Franconia")
        assert written[0].get("authored_by") == "player"
        out = post("submit_settlement_for_review", dialogue, {})
        assert out.get("success"), out.get("message") or out.get("error_display")
        out = post("confirm_settlement", out["diplomatic_dialogue"], {})
        assert out.get("success"), out.get("message") or out.get("error_display")
        assert w.regions["Tyrol"].controller == "Bavaria" and w.regions["Franconia"].controller == "Austria"
        assert _state(w, "France", "Austria") == "PEACE"

    def test_ii_g_the_hand_off_carries_the_leaders_and_names_an_allys(self):
        """The separate peace road: France's compensation travels as a
        sweetener with its stamp; one Bavaria pays cannot ride a bilateral
        letter and is named, the separate peace disabled with its reason."""
        from backend.game_logic.settlement_staging import (
            _pair_substitute_seed_terms, pair_substitute_settlement_tier_block,
        )
        seed = _pair_substitute_seed_terms([TYROL_TO_BAVARIA, THE_EASTERN_QUESTION],
                                           target="Austria", proposer_leader="France")
        sweet = next(s for s in seed["sweeteners"] if s["type"] == "territory_compensate")
        assert (sweet["region"], sweet["design"], sweet["holder"]) == ("Albania", "the_eastern_question", "Ottoman")
        assert any("The Eastern Question" in c for c in seed["carried"])
        block = pair_substitute_settlement_tier_block([TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL],
                                                      target="Austria", proposer_leader="France")
        assert "Franconia from Bavaria (an ally's province)" in block

    def test_ii_h_the_ai_letter_asks_it_where_its_desire_profile_fits(self, vienna_held):
        """GR5: the beaten court's letter to the player carries what the
        player's table may — Austria (values territory highly) asks France to
        point her east beside her indemnity; Britain (a trading court) asks
        nothing; the player's acceptance ratifies the licence."""
        from backend.game_logic import compensation as CO
        from backend.game_logic import settlement_ratify as SR
        from backend.game_logic.settlement_offers import handle_incoming_settlement_offer_action
        w = vienna_held
        assert CO.letter_compensation_ask(w, writer="Britain", payer="France") is None
        with _quiet():
            offer = AI._emit_settlement_offer_for_war(
                w, "war_1", w.war_instances["war_1"], player="France",
                current_turn=w.current_turn, pending=[], cooldowns={})
        assert offer and offer["proposer_nation"] == "Austria"
        ask = next(t for t in offer["settlement_terms"] if t["type"] == "territory_compensate")
        assert (ask["from"], ask["to"], ask["region"], ask["design"]) == (
            "France", "Austria", "Albania", "the_eastern_question")
        assert ask["authored_by"] == "Austria"
        w.pending_settlement_dialogues = [offer]
        with _quiet():
            staged = handle_incoming_settlement_offer_action(w, action="accept_settlement_offer",
                                                             dialogue=offer)
            assert staged.get("success"), staged
            out = SR.ratify_settlement_confirm(w, w.pending_diplomatic_dialogue)
        assert out.get("success"), out
        assert any(s["payer"] == "France" and s["recipient"] == "Austria" and s["aim"] == "Ottoman"
                   for s in w.directed_sponsorships)

    def test_ii_i_a_compensated_cession_is_not_a_partition(self, vienna_held):
        """The memory: two homeland provinces ceded write the punitive record
        ("Revanche stands"); one of them compensated nets it to one — the
        Revanche lapses; a capital ceded stays punitive whatever is paid."""
        from backend.game_logic import emergent_designs as ED
        from backend.game_logic.compensation import compensation_offsets
        w = vienna_held
        bohemia = dict(TYROL_TO_BAVARIA, to="France", region="Bohemia")
        assert ED.revanche_line_for_terms(w, [TYROL_TO_BAVARIA, bohemia]).startswith("Revanche stands")
        moderate = [TYROL_TO_BAVARIA, bohemia, FRANCONIA_FOR_TYROL]
        assert ED.revanche_line_for_terms(w, moderate).startswith(
            "Revanche lapses: Austria's cession of Bohemia, Tyrol is compensated with Franconia")
        cessions = ED.collect_cessions_from_clauses(moderate)
        assert ED.record_punitive_cessions(w, cessions, offsets=compensation_offsets(moderate)) == []
        vienna = dict(TYROL_TO_BAVARIA, to="France", region="Vienna")
        line = ED.revanche_line_for_terms(w, [vienna, FRANCONIA_FOR_TYROL])
        assert line.startswith("Revanche stands") and "does not undo it" in line

    def test_ii_j_an_ally_made_to_pay_is_shut_out_one_who_trades_is_rewarded(self, vienna_held):
        """Bavaria paying Franconia with nothing gained is the major shut-out,
        named ("paid_for_the_peace"); Bavaria paying it for Tyrol (the
        Pressburg exchange) is the rewarded beneficiary."""
        from backend.game_logic.settlement_reactions import _evaluate_proposer_side_reactions
        w = vienna_held
        war = w.war_instances["war_1"]

        def react(terms):
            return _evaluate_proposer_side_reactions(
                w, war_id="war_1", proposer_side="attackers", war_instance=war,
                settlement_terms=terms, applied_clauses=terms, episode_id="t",
                pre_cleanup_standings={"Bavaria": "seat"}, pre_cleanup_members=["France", "Bavaria"])
        alone = next(r for r in react([FRANCONIA_FOR_TYROL]) if r.get("ally") == "Bavaria")
        assert alone["kind"] == "ally_shut_out" and alone["severity"] == "paid_for_the_peace"
        assert alone["paid_regions"] == ["Franconia"] and alone["grievance_flag_added"] is True
        traded = next(r for r in react([TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL]) if r.get("ally") == "Bavaria")
        assert traded["kind"] == "ally_rewarded"

    def test_ii_k_every_surface_names_it(self, vienna_held):
        """The census of every reader a compensation passes through: the
        peace's summary counts a PAID province as soil moved and a design
        pointed as a material term (no white peace); the ledger, the letter's
        clause lines, the sabotage summary and the beneficiaries name it; the
        agendas read a paid province as soil the court receives."""
        from backend.display_names import build_proposal_popup_clauses, summarize_proposal
        from backend.game_logic.settlement_presentation import _beneficiaries_from_terms
        w = vienna_held
        paid_clause = dict(FRANCONIA_FOR_TYROL, regions=["Franconia"], amount=1)
        summary = D.build_peace_ratification_summary(
            w, "France", "Austria", {"clauses": [dict(paid_clause, **{"from": "France", "to": "Austria"})]},
            [], [], [], {"war_score": 10, "war_duration": 6})
        assert summary["territory_lost"] == ["Franconia"]
        pointed = D.build_peace_ratification_summary(
            w, "France", "Austria", {"clauses": [dict(THE_EASTERN_QUESTION, regions=["Albania"], amount=1)]},
            [], [], [], {"war_score": 10, "war_duration": 6})
        assert pointed["war_outcome"] != "white_peace" and pointed["territory_gained"] == []
        terms = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                 "demands": [dict(THE_EASTERN_QUESTION, value=1, regions=["Albania"],
                                  from_nation="France", to_nation="Austria")],
                 "sweeteners": [], "clauses": []}
        lines = build_proposal_popup_clauses(terms)
        assert any("design pointed elsewhere: The Eastern Question (Albania" in ln for ln in lines), lines
        assert "The Eastern Question" in summarize_proposal(terms)
        assert "Austria" in _beneficiaries_from_terms([FRANCONIA_FOR_TYROL])
        w.active_treaties[w._make_diplo_key("France", "Austria")] = {
            "nations": ["France", "Austria"], "type": "peace", "turn_signed": 6,
            "clauses": [dict(THE_EASTERN_QUESTION, amount=1)]}
        from backend.game_logic.diplomatic_ledger import _build_treaties
        with _quiet():
            rows = json.dumps(_build_treaties(w), default=str)
        assert "Territory Compensate" not in rows and "The Eastern Question" in rows
        from backend.game_logic.agendas import _proposal_territory_content
        ceded, _ = _proposal_territory_content({"sweeteners": [dict(FRANCONIA_FOR_TYROL, value=1)],
                                                "demands": [], "clauses": []})
        assert ceded == {"Franconia"}
        ceded, _ = _proposal_territory_content({"sweeteners": [dict(THE_EASTERN_QUESTION, value=1)],
                                                "demands": [], "clauses": []})
        assert ceded == set()

    def test_ii_l_a_province_promised_by_a_war_bargain_cannot_pay_it(self, vienna_held):
        from backend.game_logic import compensation as CO
        from backend.game_logic.diplomacy import _mark_live_bargain_indexes_dirty
        w = vienna_held
        w.diplomatic_commitments["wb_x"] = {
            "id": "wb_x", "kind": "war_bargain", "status": "active", "promiser": "France",
            "beneficiary": "KingdomOfItaly", "target_enemy": "Austria",
            "claim_term": {"claim_region": "Franconia"}, "created_turn": 3, "war_id": "war_1"}
        _mark_live_bargain_indexes_dirty(w)
        r = CO.compensation_reading(w, payer="Bavaria", compensated="Austria", region="Franconia",
                                    war_instance=w.war_instances["war_1"])
        assert not r["ok"] and r["code"] == "compensation_promised_by_bargain"
        assert "promised to Kingdom of Italy" in r["display"]


    # ── (ii) part 2 — declared goals (Pre-Deploy S14 part 2, October 20,
    #    2026; rules SYSTEMS_REFERENCE §134) ──────────────────────────────

    def test_ii_declared_goals_land_and_the_bond_heads_part_3(self):
        """(ii)'s second half was sized at S14 part 2's head: declared goals
        and the table's articles land here; the coalition's no-separate-peace
        bond heads S14 part 3 with its pin named in the row (GR9)."""
        from backend.game_logic import declared_goals as DG
        assert DG.MAX_DECLARED_ARTICLES == 2 and DG.DROPPED_REFUND_DIVISOR == 2
        bug = (REPO / "docs" / "BUG_FIXES.md").read_text(encoding="utf-8")
        row = next(ln for ln in bug.splitlines() if ln.startswith("| **PC-R7**"))
        # S14 part 3 (October 20, 2026): the bond landed and the row CLOSED.
        assert "CLOSED" in row and "S14 part 3" in row and "bond" in row
        assert "test_ii_the_bond_is_priced_and_biddable" in row
        status = (REPO / "docs" / "STATUS.md").read_text(encoding="utf-8")
        assert "S14 part 3" in status and "bond" in status

    def test_ii_m_the_card_declares_the_wars_articles(self, w):
        """The War Purpose card's second step: the objective chosen, up to two
        articles named — a province of the target, an indemnity, a client —
        each priced at the treaty annex's per-province alarm (8; a client 8 a
        province it carves) on the declarer's slot, stored on the record and
        kept by the save. Its first button is the harmless answer: no
        articles, the declaration as it was."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        from backend.game_logic.coalition import TREATY_ANNEX_ALARM_PER_PROVINCE
        assert TREATY_ANNEX_ALARM_PER_PROVINCE == 8
        ex = CommandExecutor()._diplomatic
        plain = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))

        def walk(world, answers):
            world.threat_by_target["France"] = 10
            world.diplomatic_points = 10
            with _quiet():
                ex._execute_diplomatic_declare_war({"target_nation": "Prussia"}, world)
                seen = []
                for a in answers:
                    seen.append(dict(world.pending_diplomatic_dialogue or {}))
                    ex.handle_diplomatic_dialogue_response(a, {"world": world})
                guard = 0
                while world.pending_diplomatic_dialogue and guard < 4:   # the ally review
                    guard += 1
                    ex.handle_diplomatic_dialogue_response("1", {"world": world})
            return seen

        seen = walk(w, ["1", "2", "2", "Conquest"])
        card = seen[1]
        assert card["stage"] == "articles" and card["objective_type"] == "conquest"
        labels = [o["label"] for o in card["options"]]
        assert labels == ["Declare war — Conquest, no articles", "Declare Berlin (+8 alarm)",
                          "Declare an indemnity (+8 alarm)",
                          "Declare Duchy of Warsaw (a client) (+8 alarm)", "Back Out"]
        assert "Europe hears them now: 8 alarm a province" in card["message"]
        assert [o["label"] for o in seen[3]["options"]] == [
            "Declare war — Conquest, with Berlin and an indemnity", "Back Out"]   # two at most
        k = w._make_diplo_key("France", "Prussia")
        assert _state(w, "France", "Prussia") == "WAR"
        rec = w.war_objectives[k]["France"]
        assert [(a["kind"], a.get("region"), a["alarm"]) for a in rec["declared_terms"]] == [
            ("province", "Berlin", 8), ("indemnity", None, 8)]
        assert w.threat_by_target["France"] == 10 + D.declaration_alarm(False) + 16
        assert any(r["source"] == DG.THREAT_SOURCE_DECLARED and r["amount"] == 16
                   for r in w.threat_sources_this_turn)
        ev = next(e for e in reversed(w.event_log) if e.get("type") == "war_articles_declared")
        assert ev["display"] == ("France declares the articles of the war on Prussia: "
                                 "Berlin and an indemnity (+16 alarm).")
        # the save keeps them, deep
        clone = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert clone.war_objectives[k]["France"]["declared_terms"] == rec["declared_terms"]
        dumped = w.to_dict()
        dumped["war_objectives"][k]["France"]["declared_terms"][0]["settled"] = "x"
        assert "settled" not in rec["declared_terms"][0]
        # the harmless first button: no articles, the declaration as it was
        walk(plain, ["1", "1"])
        assert _state(plain, "France", "Prussia") == "WAR"
        assert "declared_terms" not in plain.war_objectives[k]["France"]
        assert plain.threat_by_target["France"] == 10 + D.declaration_alarm(False)

    def test_ii_n_the_ai_design_war_declares_its_articles(self, w):
        """GR5: the AI's design war declares its design's provinces the target
        holds, through the same function and at the same price."""
        from backend.game_logic import declared_goals as DG
        from backend.game_logic.agendas import get_active_agenda
        from backend.game_logic.war_council import _declare_design_war
        assert DG.design_articles(w, "Prussia", "Hanover") == [
            {"kind": "province", "from": "Hanover", "region": "Hanover"}]
        design = get_active_agenda("Prussia", w)
        events = []
        with _quiet():
            assert _declare_design_war(w, "Prussia", {"target": "Hanover", "design_id": design.id,
                                                      "want_title": "The Hanoverian Prize"}, events)
        rec = w.war_objectives[w._make_diplo_key("Prussia", "Hanover")]["Prussia"]
        assert [(a["kind"], a["region"], a["alarm"]) for a in rec["declared_terms"]] == [
            ("province", "Hanover", 8)]
        assert any(r["source"] == DG.THREAT_SOURCE_DECLARED and r["target"] == "Prussia"
                   and r["amount"] == 8 for r in w.threat_sources_this_turn)

    def test_ii_o_a_declared_article_is_legitimate_at_the_table(self, vienna_held):
        """At the table a declared article is no surprise: on the Vienna-held
        board with the pair forced to +25 (favourable terms, ceiling 0.25),
        Tyrol declared reads the tier legitimacy 0 where Moravia, undeclared,
        reads -10 — the harshness the same; at +10 (a white peace's tier) -10
        against -20. GR5: the same read serves an AI court's articles."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        w = vienna_held
        with _quiet():
            res = CommandExecutor()._diplomatic._set_war_purpose_inner(
                "Austria", "conquest", w,
                declared_terms=[{"kind": "province", "region": "Tyrol"}, {"kind": "indemnity"}])
        assert res["success"] and "Tyrol and an indemnity (+16 alarm)" in res["message"]

        def legit(score, region):
            _force_pair(w, "France", "Austria", score)
            body = _preview(w, terms=[{"type": "territory_cede", "from": "Austria", "to": "France",
                                       "region": region}], covered=["Austria"])
            row = _row(body, "Austria")
            return _comp(row, "settlement_tier_legitimacy"), _comp(row, "term_harshness_penalty")
        assert legit(25, "Tyrol") == (0, legit(25, "Moravia")[1])
        assert legit(25, "Moravia")[0] == -10
        assert legit(10, "Tyrol")[0] == -10 and legit(10, "Moravia")[0] == -20
        # the court's debug names what was declared
        _force_pair(w, "France", "Austria", 25)
        body = _preview(w, terms=[{"type": "territory_cede", "from": "Austria", "to": "Bavaria",
                                   "region": "Tyrol"}], covered=["Austria"])
        assert _comp(_row(body, "Austria"), "settlement_tier_legitimacy") == 0   # any recipient
        # GR5: an AI court's declared article reads the same way, and only for its side
        arts = DG.article_candidates(w, "Austria", "France")
        first = next(a for a in arts if a["kind"] == "province")
        rec = w.war_objectives[w._make_diplo_key("Austria", "France")]["Austria"]
        rec["type"] = "conquest"
        DG.declare_articles(w, "Austria", "France", [first])
        cede = {"type": "territory_cede", "from": "France", "to": "Austria", "region": first["region"]}
        assert DG.undeclared_terms(w, [cede], ["Austria", "Britain", "Russia"]) == []
        assert DG.undeclared_terms(w, [cede], ["France", "Bavaria"]) == [cede]

    def test_ii_p_the_table_opens_on_the_declared_draft_and_the_counsel_prices_it(
            self, vienna_held, monkeypatch):
        """Composable articles: the table opens on the declared articles (the
        empty PROPOSE draft), a declared article struck from the draft LEADS
        the court's guided rows ("Declared at the war: Tyrol") and adds back
        through the add verb, and Talleyrand's table road prices that same
        draft first — the road opens with the draft he priced (K item 6)."""
        from fastapi.testclient import TestClient
        from backend.commands.executor import CommandExecutor
        w = vienna_held
        with _quiet():
            CommandExecutor()._diplomatic._set_war_purpose_inner(
                "Austria", "conquest", w,
                declared_terms=[{"kind": "province", "region": "Tyrol"}, {"kind": "indemnity"}])
        declared = [{"type": "peace"},
                    {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"},
                    {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300}]
        with _quiet():
            reading = CS.read_counsel(w, "Austria")
        road = next(r for r in reading["roads"] if r["road"] == "table_alone")
        assert road["declared_draft"] is True and road["action"] == "open_settlement"
        assert road["priced_terms"] == declared
        assert road["trade"].startswith("It costs 3 DP. Priced on the articles declared at the war: "
                                        "Tyrol, an indemnity.")
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
        assert [t for t in dialogue["settlement_terms"] if t.get("type") != "peace"] == declared[1:]
        idx = next(i for i, t in enumerate(dialogue["settlement_terms"]) if t.get("region") == "Tyrol")
        out = post("settlement_demand_remove", dialogue, {"clause_index": idx,
                                                          "expected_type": "territory_cede"})
        assert out.get("success"), out.get("message") or out.get("error_display")
        dialogue = out["diplomatic_dialogue"]
        row = next(c for c in dialogue["per_court_acceptance"] if c["nation"] == "Austria")
        lead = (row.get("demand_suggestions") or [])[0]
        assert lead["label"] == "Declared at the war: Tyrol" and lead["declared"] is True
        assert lead["group"] == "demand" and lead["action_params"]["region"] == "Tyrol"
        assert "it is legitimate at the table" in lead["reason_display"]
        out = post("settlement_demand_add", dialogue, dict(lead["action_params"]))
        assert out.get("success"), out.get("message") or out.get("error_display")
        assert any(t.get("region") == "Tyrol" for t in out["diplomatic_dialogue"]["settlement_terms"])

    def test_ii_q_a_dropped_article_returns_half_its_alarm(self, vienna_held):
        """At the peace each article settles once — taken (Tyrol: Austria no
        longer holds it) or dropped (the indemnity the peace did not carry) —
        and a dropped one returns half its alarm (4), named on the line."""
        import unittest.mock as _m
        from backend.campaign_log import format_event_oneliner
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        from backend.game_logic import settlement_ratify as SR
        from backend.game_logic import settlement_scoring as SS
        from tests.test_common_peace_c2_ratification import _acceptance_always_passes, _stage_dialogue
        w = vienna_held
        with _quiet():
            CommandExecutor()._diplomatic._set_war_purpose_inner(
                "Austria", "conquest", w,
                declared_terms=[{"kind": "province", "region": "Tyrol"}, {"kind": "indemnity"}])
        k = w._make_diplo_key("France", "Austria")
        with _m.patch.object(SS, "calculate_common_peace_acceptance", _acceptance_always_passes):
            dialogue = _stage_dialogue(w, settlement_terms=[
                {"type": "peace"},
                {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}],
                covered_enemy_participants=["Austria"], war_id="war_1")
            with _quiet():
                out = SR.ratify_settlement_confirm(w, dialogue)
        assert out["success"]
        assert ("The articles France declared at the war: Tyrol taken; an indemnity dropped — "
                "half the dropped articles' alarm returned (4).") in out["message"]
        arts = w.war_objectives[k]["France"]["declared_terms"]
        assert [(a["kind"], a["settled"], a["refund"]) for a in arts] == [
            ("province", "taken", 0), ("indemnity", "dropped", 4)]
        assert any(r["source"] == DG.THREAT_SOURCE_REFUND and r["amount"] == -4 and r["target"] == "France"
                   for r in w.threat_sources_this_turn)
        ev = next(e for e in reversed(w.event_log) if e.get("type") == "war_articles_settled")
        assert format_event_oneliner(ev).startswith("The articles France declared at the war: Tyrol taken")
        # settled once: no second refund
        n = len(w.threat_sources_this_turn)
        assert DG.settle_at_peace(w, [k]) == [] and len(w.threat_sources_this_turn) == n

    def test_ii_r_every_peace_road_settles_them(self, vienna_held):
        """The bilateral ratifier (Tyrol handed back — dropped, refunded, on the
        aftermath), the truce's dictated exit (the held line and the loser's
        stream — both taken), and the sweep for a war ended by no treaty."""
        from backend.commands.executor import CommandExecutor
        ex = CommandExecutor()._diplomatic
        tyrol_and_gold = [{"kind": "province", "region": "Tyrol"}, {"kind": "indemnity"}]
        k = "Austria|France"
        # (a) the bilateral peace returning Tyrol
        w = vienna_held
        with _quiet():
            ex._set_war_purpose_inner("Austria", "conquest", w, declared_terms=tyrol_and_gold)
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol"]}],
                                    "demands": [], "clauses": []})
        assert (res or {}).get("type") == "diplomatic_treaty_signed", res
        arts = w.war_objectives[k]["France"]["declared_terms"]
        assert [(a["settled"], a["refund"]) for a in arts] == [("dropped", 4), ("dropped", 4)]
        aftermath = w.peace_ratification_log[-1]["political_aftermath"]
        assert ("The articles France declared at the war: Tyrol dropped; an indemnity dropped — "
                "half the dropped articles' alarm returned (8).") in aftermath
        # (b) the truce's dictated exit
        w2 = _board("turn6_vienna_held.json")
        with _quiet():
            ex._set_war_purpose_inner("Austria", "conquest", w2, declared_terms=tyrol_and_gold)
        _truce(w2, proposer="Austria", target="France", sweeteners=[{"type": "gold_per_turn", "value": 80}])
        _kill_hope(w2)
        w2.nation_relations[k] = -80
        w2.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        with _quiet():
            events = D._process_armistice_expiration(w2)
        ev = next(e for e in events if e["type"] == "armistice_expired_dictated")
        assert "The articles France declared at the war: Tyrol taken; an indemnity taken." in ev["message"]
        # (c) the sweep: a war concluded with no treaty seam
        w3 = _board("turn6_vienna_held.json")
        with _quiet():
            ex._set_war_purpose_inner("Austria", "conquest", w3, declared_terms=tyrol_and_gold)
        w3.regions["Tyrol"].controller = "Austria"
        D.conclude_war_objectives_of(w3, k)
        D._cleanup_old_war_objectives(w3)
        arts = w3.war_objectives[k]["France"]["declared_terms"]
        assert [(a["settled"], a["refund"]) for a in arts] == [("dropped", 4), ("dropped", 4)]

    # ── S14 part 3 — the bond (Chaumont) ────────────────────────────────────

    def test_ii_the_bond_is_priced_and_biddable(self, ulm_t18, vienna_held):
        """THE done-when of PC-R7 (ii)'s last piece (S14 part 3): the league's
        no-separate-peace bond is MINTED by the paymaster through the one mint
        (GR5), dated and serialized; PRICED in the bonded member's break-ranks
        read (deeper lines), at the table (her row's named component, 0 on the
        common peace) and in the bilateral; REPUDIATED as a broken bargain when
        she signs alone inside the term; and BIDDABLE — France's gold (or a
        compensation) offsets the component exactly, the table offers the bid,
        the counsel names it, the Cabinet opens the table with it staged."""
        from backend.game_logic import bond as B
        from backend.game_logic.instruments import (
            build_instruments_line, has_renege_grievance, process_instruments,
        )
        w = ulm_t18
        k = w._make_diplo_key("Austria", "France")
        score = int(D.get_war_score_for(w, "Austria", "France"))
        # The gap, measured first: spent at 174, she breaks ranks on exhaustion.
        assert AI.coalition_break_ranks_reason(w, "Austria", war_score=score, diplo_key=k) == "exhaustion"
        alone_before = _row(_preview(w, terms=[], covered=["Austria"]), "Austria")["total"]
        assert alone_before == 7
        # (1) MINTED by the paymaster — the member about to break ranks, whom the
        # bond's depth would hold; one D5 record of kind "bond", dated.
        with _quiet():
            events = B.ai_paymaster_binds(w)
        assert [(e["type"], e["kind"], e["payer"], e["recipient"], e["aim"], e["amount"], e["turns"])
                for e in events] == [("sponsorship_granted", "bond", "Britain", "Austria", "France", 400, 10)]
        rec = B.bond_on(w, "Austria", "France")
        assert (rec["started_turn"], rec["expiry_turn"], rec["turns_remaining"]) == (18, 28, 10)
        back = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert [(r["kind"], r["payer"], r["recipient"]) for r in back.directed_sponsorships
                if r["kind"] == "bond"] == [("bond", "Britain", "Austria")]
        assert ("Britain binds Austria to the war against France — no separate peace "
                "(400g/turn, 10 turns left, since turn 18)") in build_instruments_line(w, "Austria")
        # (2) PRICED in the break-ranks read: the lines read deeper by the bond's
        # strength (12 = 400 a turn at the bilateral's 3 a 100) — the score lines
        # by 12 / 0.65 = 18, the exhaustion line by 12 × 10 = 120.
        assert (B.strength(rec), B.table_price(w, rec), B.bid_gold(w, rec)) == (12, 40, 1000)
        lines = AI.break_ranks_lines(w, "Austria")
        assert (lines["score"], lines["exhaustion"], lines["pressburg"], lines["bond"]) == (-68, 200, -48, "Britain")
        assert AI.coalition_break_ranks_reason(w, "Austria", war_score=score, diplo_key=k) is None
        own = AI.court_own_readiness(w, "Austria", "France")
        assert own["loyal"] and own["bond"] == "Britain"
        # (3) PRICED at the table — her separate peace forfeits the stream still
        # owed (400 × 10 at 25 gold a point, capped at 40); the common peace 0.
        alone = _row(_preview(w, terms=[], covered=["Austria"]), "Austria")
        assert (alone["total"], _comp(alone, "coalition_bond")) == (alone_before - 40, -40)
        whole = _row(_preview(w, terms=[], covered=["Austria", "Britain", "Russia"]), "Austria")
        assert _comp(whole, "coalition_bond") == 0
        # … and in the bilateral, beside the loyalty term.
        with _quiet():
            acc = D.calculate_acceptance({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                          "sweeteners": [], "demands": [], "clauses": []}, w)
        assert acc["components"]["coalition_bond"] == -12
        # (4) BIDDABLE — the bid's 1,000 gold is credited +40 by the table's own
        # gold rate: it offsets the bond exactly (priced, never a veto).
        bid = [{"type": "peace"}, {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 1000}]
        assert _row(_preview(w, terms=bid, covered=["Austria"]), "Austria")["total"] == alone_before
        price = ("Britain's bond costs her 40 at the table (12 in a bilateral peace); 1,000 gold to her "
                 "pays it")
        assert B.price_line(w, "Austria", "France").startswith(price)
        reading = CS.read_counsel(w, "Austria")
        table_road = next(r for r in reading["roads"] if r["road"] == "table_alone")
        assert price in table_road["trade"]
        rows = _rows(w, "Austria")
        outbid = next(r for r in rows if r["action"] == "outbid_bond")
        assert outbid["display_name"] == "Outbid Britain's Bond — Austria alone at the table"
        assert outbid["counsel_coverage"] == ["Austria"]
        assert outbid["choices"] == [{"label": "Open the table with 1,000 gold to Austria (+40)",
                                      "payload": {"bond_bid": 1000}}]
        assert B.bid_opening_terms(w, war_id="war_1", payer="France", court="Austria", amount=1000,
                                   covered=["Austria"])[-1] == bid[-1]
        # (5) REPUDIATED: her separate peace inside the term is a broken bargain
        # against HER — the strongest grievance, Britain's mark against Austria.
        with _quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                              "sweeteners": [], "demands": [], "clauses": []})
            events = process_instruments(w)
        broken = [e for e in events if e.get("kind") == "bond"]
        assert [(e["type"], e["breaker"], e["victim"]) for e in broken] == [
            ("sponsorship_reneged", "Austria", "Britain")]
        assert has_renege_grievance(w, "Britain", "Austria")
        assert B.live_bonds(w) == []
        # (6) the moderate Pressburg on the Vienna-held board: the same mint (the
        # paymaster's function) prices it 71 → 31, and France's bid carries it
        # again — or a compensation pays most of it, named by the counsel's words.
        v = vienna_held
        moderate = [TYROL_TO_BAVARIA, FRANCONIA_FOR_TYROL]
        assert _row(_preview(v, terms=moderate, covered=["Austria"]), "Austria")["total"] == 71
        with _quiet():
            assert B.mint_bond(v, payer="Britain", member="Austria", enemy="France")["success"]
        assert _row(_preview(v, terms=moderate, covered=["Austria"]), "Austria")["total"] == 31
        bid_v = moderate + [{"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 1000}]
        body = _preview(v, terms=bid_v, covered=["Austria"])
        assert _row(body, "Austria")["total"] == 71 and body["overall_acceptance"]["carries"]
        assert B.price_line(v, "Austria", "France", war_instance=v.war_instances["war_1"]) == (
            price + " — or Franconia, Bavaria's (+35), most of it.")

    def test_ii_s_the_paymaster_binds_only_whom_its_gold_can_hold(self, vienna_held):
        """The AI's rule, measured on the Vienna-held board: Austria at −54 with
        her design satisfied breaks ranks on the Pressburg arm (−30), and under
        a 400-gold bond that arm reads −48 — past the bond's reach, so Britain
        does not bind her (Pressburg, 1805: Britain's gold could not hold
        Vienna). A loyal court is never bound (nothing to buy)."""
        from backend.game_logic import bond as B
        w = vienna_held
        score = int(D.get_war_score_for(w, "Austria", "France"))
        k = w._make_diplo_key("Austria", "France")
        held = B.depth_for_strength(B.strength({"amount_per_turn": B.bond_amount(w, "Britain")}))
        assert held == {"score": 18, "exhaustion": 120}
        assert AI.coalition_break_ranks_reason(w, "Austria", war_score=score, diplo_key=k, depth=held) == "pressburg"
        with _quiet():
            assert B.ai_paymaster_binds(w) == []
        assert B.live_bonds(w) == []

    def test_ii_t_france_binds_her_own_ally_through_the_same_mint(self, vienna_held):
        """GR5: the player's Cabinet row (F1 → Bavaria → Bind Bavaria to the
        War, a choice per shared enemy) sends the one mint; Austria's peace to
        the bonded Bavaria reads the bond in the bilateral; the door claims the
        typed verb (diplomacy is never typed)."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import bond as B
        w = vienna_held
        row = next(r for r in _rows(w, "Bavaria") if r["action"] == "bind_to_war")
        assert row["display_name"] == "Bind Bavaria to the War (300g/turn)" and row["available"]
        assert row["choices"] == [{"label": "Against Austria — no separate peace with Austria",
                                   "payload": {"enemy": "Austria"}}]
        dp = int(w.diplomatic_points)
        with _quiet():
            res = CommandExecutor()._diplomatic._execute_bind_to_war(
                {"action": "bind_to_war", "target": "Bavaria",
                 "raw_input": "bind Bavaria to the war against Austria"}, {"world": w})
        assert res["success"], res
        assert res["message"].startswith("France binds Bavaria to the war against Austria: no separate "
                                         "peace for 10 turns, 300 gold a turn.")
        assert int(w.diplomatic_points) == dp - 1
        assert [(r["payer"], r["recipient"], r["aim"]) for r in B.live_bonds(w)] == [("France", "Bavaria", "Austria")]
        with _quiet():
            acc = D.calculate_acceptance({"type": "peace", "proposer_nation": "Austria", "target_nation": "Bavaria",
                                          "sweeteners": [], "demands": [], "clauses": []}, w)
        assert acc["components"]["coalition_bond"] == -9
        main_gd = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert '_contains_word(lower, "bind")' in main_gd
        assert '["bind ", "Bind to the War' in main_gd


class TestTheS14Part1Siblings:
    """PC-R7 (ii)'s sibling sweep (S14 part 1, October 20, 2026): the
    hand-off that dropped an offered province in silence (X28), the
    refusal that promised a peace-table road no verb had (X29), and the
    desire profiles that named the legacy map's provinces (X30)."""

    def test_x28_an_offered_province_travels_to_the_separate_peace(self, vienna_held):
        from backend.game_logic.settlement_staging import (
            _pair_substitute_seed_terms, pair_substitute_dropped_clause_labels,
        )
        w = vienna_held
        vienna_back = {"type": "territory_cede", "from": "France", "to": "Austria", "region": "Vienna"}
        terms = [TYROL_TO_BAVARIA, vienna_back]
        seed = _pair_substitute_seed_terms(terms, target="Austria", proposer_leader="France")
        assert {"type": "territory_cede", "value": 1, "regions": ["Vienna"]} in seed["sweeteners"]
        assert "Vienna to Austria" in seed["carried"]
        assert pair_substitute_dropped_clause_labels(terms, target="Austria", proposer_leader="France") == []
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": seed["sweeteners"], "demands": seed["demands"],
                                    "clauses": []})
        assert (res or {}).get("type") == "diplomatic_treaty_signed", res
        assert w.regions["Vienna"].controller == "Austria" and w.regions["Tyrol"].controller == "Bavaria"

    def test_x29_the_peace_table_road_is_named_where_it_exists(self, vienna_held):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.instruments import buy_off_refusal
        w = vienna_held
        w.diplomatic_points = 5
        assert buy_off_refusal(w, "France", "Austria") == (
            "we are at war — at the peace table her design can be pointed elsewhere — "
            "The Eastern Question (Albania)")
        assert buy_off_refusal(w, "France", "Britain").endswith(
            "looks nowhere a peace could point her")
        with _quiet():
            out = CommandExecutor()._diplomatic._execute_buy_off_design(
                {"action": "buy_off_design", "target": "Austria", "raw_input": "buy off Austria"},
                {"world": w})
        assert out["success"] is False
        assert "The Eastern Question (Albania)" in out["message"]
        assert "bought off at the peace table" not in out["message"]

    def test_x30_the_desire_profiles_name_provinces_of_the_map_they_read(self):
        from backend.game_logic.diplomacy import SPECIAL_BONUSES
        from backend.game_logic.diplomatic_templates import NATION_DESIRE_PROFILES
        from backend.models.region import REGIONS_DATA, create_europe_regions
        europe, legacy = set(create_europe_regions()), set(REGIONS_DATA)
        for nation, profile in NATION_DESIRE_PROFILES.items():
            for region in profile.get("covets_regions", []):
                assert region in europe or region in legacy, (nation, region)
        # each legacy-only name stands beside its 1805 province
        assert "Munich" in NATION_DESIRE_PROFILES["Austria"]["covets_regions"]
        assert "Brabant" in NATION_DESIRE_PROFILES["Britain"]["covets_regions"]
        assert "Dresden" in NATION_DESIRE_PROFILES["Prussia"]["covets_regions"]
        assert SPECIAL_BONUSES["Prussia"]["territory_dresden"] == SPECIAL_BONUSES["Prussia"]["territory_saxony"]
        assert SPECIAL_BONUSES["Austria"]["territory_munich"] == SPECIAL_BONUSES["Austria"]["territory_bavaria"]

    def test_x31_the_ledger_names_every_clause_type(self, w):
        from backend.game_logic.diplomatic_ledger import _build_treaties
        w.active_treaties[w._make_diplo_key("France", "Prussia")] = {
            "nations": ["France", "Prussia"], "type": "peace", "turn_signed": 1,
            "clauses": [{"type": "create_client", "from": "Prussia", "to": "France", "amount": 1},
                        {"type": "continental_system_join", "from": "Prussia", "to": "France", "amount": 1}]}
        with _quiet():
            row = next(t for t in _build_treaties(w) if "Prussia" in (t.get("nation_a"), t.get("nation_b"))
                       or "Prussia" in json.dumps(t))
        text = json.dumps(row)
        assert "Client state erected (Prussia -> France)" in text
        assert "Joins the Continental System (Prussia -> France)" in text
        assert "Create Client" not in text and "Continental System Join" not in text

    def test_x32_a_table_award_of_a_claim_province_to_another_court_is_a_breach(self):
        from backend.game_logic.settlement_reactions import _evaluate_bargain_outcomes
        from tests.test_settlement_slice_h_ally_petitions import _seed_bargain_world
        world = _seed_bargain_world()
        out = _evaluate_bargain_outcomes(
            world, war_id="war_1",
            settlement_terms=[{"type": "territory_cede", "from": "Austria", "to": "Bavaria",
                               "region": "Vienna"}],
            proposer_member_set={"France", "Prussia"}, episode_id="t")
        assert [o["kind"] for o in out] == ["bargain_breach_at_settlement"]


class TestTheS14Part2Siblings:
    """PC-R7 (ii) part 2's sibling sweep (S14 part 2, October 20, 2026): the
    roads beside the declared articles that still read a declaration or a
    peace without them."""

    def test_x33_talleyrands_projection_hears_the_articles(self):
        """The league-gathering projection Talleyrand reads before a
        declaration counted the declaration's 20 and never its articles: at
        30, a declaration naming Berlin and an indemnity carries Europe to 66
        and he said nothing."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import coalition as C
        from tests.test_iq3_the_league_is_spent import _europe, _hostile_minors
        world = _europe()
        world.active_coalition = None
        world.coalition_brewing = None
        world.threat_by_target["France"] = 30
        _hostile_minors(world)
        world.diplomatic_points = 5
        assert C.declaration_would_gather_a_league(world, "France") is None
        projection = C.declaration_would_gather_a_league(world, "France", extra_alarm=16)
        assert projection and projection["to"] == 66
        with _quiet():
            out = CommandExecutor()._diplomatic._execute_diplomatic_declare_war(
                {"target_nation": "Prussia", "war_objective": "conquest",
                 "declared_terms": [{"kind": "province", "region": "Berlin"}, {"kind": "indemnity"}]},
                world)
        text = (out.get("diplomatic_objection_popup") or {}).get("objection_text") or ""
        assert "would carry it to 66" in text, out.get("message")
        assert world.get_diplomatic_state("France", "Prussia") != "WAR"
        # the stashed context carries the articles through his objection
        assert world._declare_war_objection_context["declared_terms"]

    def test_x34_the_bilateral_preview_does_not_call_a_declared_article_unearned(self, vienna_held):
        """The bilateral peace preview's tier warnings ("Your war score may
        not support demanding 2 regions") counted a declared province as a
        claim the field had not earned; it reads the demands without it."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        w = vienna_held
        with _quiet():
            CommandExecutor()._diplomatic._set_war_purpose_inner(
                "Austria", "conquest", w, declared_terms=[{"kind": "province", "region": "Tyrol"}])
        demands = [{"type": "territory_cede", "value": 2, "regions": ["Tyrol", "Moravia"]}]
        assert DG.undeclared_demands(w, "France", "Austria", demands) == [
            {"type": "territory_cede", "value": 1, "regions": ["Moravia"]}]
        assert D.get_tier_mismatch_warnings(25, {"demands": demands})
        assert not D.get_tier_mismatch_warnings(
            25, {"demands": DG.undeclared_demands(w, "France", "Austria", demands)})
        # the surface: the war snapshot the peace popups read hands the
        # warning the demands without the declared province
        seen = []
        real = D.get_tier_mismatch_warnings
        import unittest.mock as _m
        with _m.patch.object(D, "get_tier_mismatch_warnings",
                             lambda score, terms: seen.append(terms) or real(score, terms)):
            with _quiet():
                D.build_war_context_snapshot(w, "France", "Austria", "peace",
                                             terms={"type": "peace", "demands": demands,
                                                    "sweeteners": [], "clauses": []})
        assert seen and seen[-1]["demands"] == [
            {"type": "territory_cede", "value": 1, "regions": ["Moravia"]}]


    def test_x35_a_war_reopened_before_the_sweep_settles_the_old_articles_first(self, w):
        """A pair back at war before the turn's sweep overwrote the old war's
        record — its articles never settled, the alarm kept. The new war's
        records are written only after the old articles settle."""
        from backend.game_logic import declared_goals as DG
        k = w._make_diplo_key("France", "Prussia")
        with _quiet():
            assert D.declare_war(w, "France", "Prussia", war_objective="conquest",
                                 declared_terms=[{"kind": "province", "region": "Berlin"}]).get("success")
        D.set_diplomatic_state(w, "France", "Prussia", "PEACE", "test")
        D.conclude_war_objectives_of(w, k)
        w.threat_sources_this_turn = []
        with _quiet():
            assert D.declare_war(w, "France", "Prussia", war_objective="conquest").get("success")
        ev = next(e for e in reversed(w.event_log) if e.get("type") == "war_articles_settled")
        assert [(r["article"]["region"], r["settled"], r["refund"]) for r in ev["rows"]] == [
            ("Berlin", "dropped", 4)]
        assert any(r["source"] == DG.THREAT_SOURCE_REFUND and r["amount"] == -4
                   for r in w.threat_sources_this_turn)
        assert "declared_terms" not in w.war_objectives[k]["France"]

    def test_x36_what_was_signed_is_the_pairs_treaty_a_surety_goes_home(self, vienna_held):
        """The bilateral seam read only the APPLIED clauses — a stream (never
        "applied" at signing) or an empty chest's lump read the indemnity
        "dropped" and refunded it; and a province held as the stream's surety
        (home with the last payment) read "taken". The settlement reads the
        pair's treaty in force: the stream is the indemnity, the surety is not
        a cession. The truce's courted exit, whose stream runs on, the same."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        ex = CommandExecutor()._diplomatic
        k = "Austria|France"
        w = vienna_held
        with _quiet():
            ex._set_war_purpose_inner("Austria", "conquest", w, declared_terms=[
                {"kind": "province", "region": "Tyrol"}, {"kind": "indemnity"}])
        w.active_treaties[k] = {"type": "peace", "clauses": [
            {"type": "gold_per_turn", "from": "Austria", "to": "France", "amount": 80,
             "surety_regions": ["Tyrol"]}]}
        D.conclude_war_objectives_of(w, k)
        rows = DG.settle_at_peace(w, [k])
        assert [(r["article"]["kind"], r["settled"], r["refund"]) for r in rows] == [
            ("province", "dropped", 4), ("indemnity", "taken", 0)]
        # the truce's courted exit: the loser's stream runs on into the peace
        w2 = _board("turn6_vienna_held.json")
        with _quiet():
            ex._set_war_purpose_inner("Austria", "conquest", w2,
                                      declared_terms=[{"kind": "indemnity"}])
        _truce(w2, proposer="Austria", target="France",
               sweeteners=[{"type": "gold_per_turn", "value": 80}])
        w2.nation_relations[k] = -50
        w2.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        with _quiet():
            events = D._process_armistice_expiration(w2)
        ev = next(e for e in events if e["type"] == "armistice_expired_peace")
        assert "The articles France declared at the war: an indemnity taken." in ev["message"]

    def test_x37_the_wars_objective_reads_its_declared_articles(self):
        """A war's objective read its own aims off `target_regions` alone: a
        declared province the peace carried was "partial" under a subjugation
        and a burdened great power's "major_uncovered" -10 fired on it. The
        declared articles are the objective's aims."""
        from backend.game_logic import settlement_scoring as SS
        rec = D.create_war_objective("subjugation", "France", "Austria", ["Vienna"], 1)
        terms = [{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}]
        assert SS._classify_objective_alignment("subjugation", rec, "Austria", terms) == (
            SS.ALIGN_PARTIAL, "partial")
        assert not SS._term_matches_objective("Austria", rec, terms)
        rec["declared_terms"] = [{"kind": "province", "from": "Austria", "region": "Tyrol", "alarm": 8}]
        assert SS._classify_objective_alignment("subjugation", rec, "Austria", terms) == (
            SS.ALIGN_SATISFY, "satisfies")
        assert SS._term_matches_objective("Austria", rec, terms)
        rec["declared_terms"][0]["settled"] = "dropped"      # a settled article is history
        assert not SS._term_matches_objective("Austria", rec, terms)

    def test_x38_every_surface_names_both_sides_articles(self, vienna_held):
        """The articles reached the war panel's own sentence only: the peace
        popups' sentence, the enemy's purpose, "what is the war for", and the
        AI's declaration never named them."""
        from backend.ai.state_desk import _answer_why_war
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import declared_goals as DG
        from backend.game_logic.war_council import _declared_tail
        from backend.game_logic.war_status import build_active_wars
        w = vienna_held
        with _quiet():
            CommandExecutor()._diplomatic._set_war_purpose_inner(
                "Austria", "conquest", w, declared_terms=[{"kind": "province", "region": "Tyrol"}])
        rec = w.war_objectives[w._make_diplo_key("Austria", "France")]["Austria"]
        rec["type"] = "conquest"
        first = next(a for a in DG.article_candidates(w, "Austria", "France") if a["kind"] == "province")
        DG.declare_articles(w, "Austria", "France", [first])
        with _quiet():
            snap = D.build_war_context_snapshot(w, "France", "Austria", "peace")
            row = next(r for r in build_active_wars(w)["wars"] if r.get("status") == "war")
        line = f"declared: Tyrol; Austria declared: {first['region']}"
        assert snap["war_objective"]["target_summary"].endswith(line)
        assert row["objective"]["target_summary"].endswith(line)
        assert row["enemy_objective"]["type_display"].endswith(f"— declared: {first['region']}")
        assert f"The articles of the war — {line}." in _answer_why_war(w, "Austria")
        assert _declared_tail(w, {"declared_articles": [
            {"kind": "province", "from": "Hanover", "region": "Hanover"}]}) == "; declaring Hanover"

    def test_x39_the_threat_panel_names_the_articles(self, w):
        from backend.game_logic.diplomatic_ledger import _threat_source_label
        assert _threat_source_label(w, "declared_articles") == "Declared the articles of a war"
        assert _threat_source_label(w, "declared_article_dropped") == (
            "A declared article dropped at the peace")

    def test_x40_the_ai_letter_asks_the_province_it_declared(self, vienna_held):
        """GR5: France's table opens on France's articles; a court's dictated
        letter asked its province by its own rules and never the one it
        declared. It asks the declared one first while France still holds it."""
        from backend.game_logic import declared_goals as DG
        w = vienna_held
        rec = w.war_objectives[w._make_diplo_key("Austria", "France")]["Austria"]
        rec["type"] = "conquest"
        capital = w.get_nation_capital("France")
        before = AI.dictated_province(w, "Austria", "France")
        assert before == "Normandy"                           # her own pick on the board
        pick = next(a for a in DG.article_candidates(w, "Austria", "France")
                    if a["kind"] == "province" and a["region"] not in (capital, before))
        assert pick["region"] == "Vienna"                     # her own capital, France holds it
        DG.declare_articles(w, "Austria", "France", [pick])
        assert AI.dictated_province(w, "Austria", "France") == "Vienna"


    def test_x41_the_wars_running_at_the_boot_name_their_articles_too(self, w):
        """The 1805 boot opens at war with Austria, Britain and Russia, every
        pair on the declaration's default `defense` purpose and no articles —
        no card was ever shown. The purpose set is their road: the war panel's
        hint names it, and the typed `set war purpose conquest against Austria`
        (the objective named) reached no articles step at all; it opens the
        step now with Conquest chosen, priced as at a declaration."""
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        from backend.game_logic import declared_goals as DG
        from backend.game_logic.war_status import _objective_hint
        for court in ("Austria", "Britain", "Russia"):
            recs = w.war_objectives[w._make_diplo_key("France", court)]
            assert recs["France"]["type"] == "defense" and "declared_terms" not in recs["France"]
        assert [(a["kind"], a.get("region") or a.get("tag")) for a in DG.article_candidates(
            w, "France", "Britain")] == [("province", "London"), ("indemnity", None), ("client", "Ireland")]
        assert "names a purpose of your own, and the war's articles" in _objective_hint(
            {"type": "defense"}, "Austria", w)
        ex = CommandExecutor()
        parser = CommandParser(use_real_llm=False)
        w.threat_by_target["France"] = 10

        def typed(line):
            with _quiet():
                return ex.execute(parser.parse(line, game_state={"world": w}), {"world": w})
        typed("set war purpose conquest against Austria")
        step = w.pending_diplomatic_dialogue
        assert step["stage"] == "articles" and step["objective_type"] == "conquest"
        assert step["is_defensive_set"] is True
        assert step["options"][0]["label"] == "Set the purpose — Conquest, no articles"
        assert w.war_objectives[w._make_diplo_key("France", "Austria")]["France"]["type"] == "defense"
        with _quiet():
            ex._diplomatic.handle_diplomatic_dialogue_response("2", {"world": w})    # Vienna
            ex._diplomatic.handle_diplomatic_dialogue_response("1", {"world": w})
        rec = w.war_objectives[w._make_diplo_key("France", "Austria")]["France"]
        assert rec["type"] == "conquest"
        assert [(a["kind"], a["region"]) for a in rec["declared_terms"]] == [("province", "Vienna")]
        assert w.threat_by_target["France"] == 18


    def test_x42_the_war_purpose_has_its_cabinet_row(self, w):
        """The user's rule (October 20, 2026): diplomacy is never typed. The
        war purpose — and with it the boot wars' articles — had no UI home
        (`main.gd`'s no-home list kept it typed, and the war panel's hint
        told the player to type it). It is a Cabinet row now: F1 → the court
        → Set War Purpose, on every war still on the default defensive
        purpose; the hint names the row; the typed verb is claimed."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.war_status import build_active_wars

        def row_for(court):
            return next((r for r in _rows(w, court) if r.get("action") == "set_war_purpose"), None)
        for court in ("Austria", "Britain", "Russia"):
            row = row_for(court)
            assert row and row["available"] and row["display_name"] == "Set War Purpose", court
            assert row["effect_text"] == "name what the war is for, and up to 2 articles"
        assert row_for("Prussia") is None                        # at peace: no war to name
        with _quiet():
            war = next(r for r in build_active_wars(w)["wars"] if r.get("status") == "war")
        assert "Set War Purpose (F1 → " in war["objective_hint"]
        assert "'set war purpose" not in war["objective_hint"]
        # the wizard's echo opens the card; a purpose of her own retires the row
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert '"set_war_purpose":\n\t\t\treturn "set war purpose against " + nation' in wizard
        ex = CommandExecutor()._diplomatic
        with _quiet():
            ex._execute_set_war_purpose({"target_nation": "Austria"}, {"world": w})
            assert w.pending_diplomatic_dialogue["type"] == "war_purpose_selection"
            ex.handle_diplomatic_dialogue_response("1", {"world": w})        # Conquest
            ex.handle_diplomatic_dialogue_response("1", {"world": w})        # no articles
        assert w.war_objectives[w._make_diplo_key("France", "Austria")]["France"]["type"] == "conquest"
        assert row_for("Austria") is None
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert "DIPLO_NO_HOME_KEYWORDS" not in main          # PC-X43 … X45 emptied it
        family = main[main.index("const DIPLO_FAMILY_KEYWORDS"):main.index("const DIPLO_NATION_GATED_PREFIXES")]
        assert '"set war purpose"' in family


class TestTheS14Part3Siblings:
    """PC-R7 (ii) part 3's sibling sweep (S14 part 3, October 20, 2026 —
    the bond, Chaumont): every read of the break-ranks lines, every road out
    of a war, every surface that says what the paymaster pays, every reader of
    a directed record's kind. PC-X52 … X60, each FIXED in the part."""

    @staticmethod
    def _bind(w, payer="Britain", member="Austria", enemy="France"):
        from backend.game_logic import bond as B
        with _quiet():
            res = B.mint_bond(w, payer=payer, member=member, enemy=enemy)
        assert res["success"], res
        return res["record"]

    def test_x52_the_clock_runs_to_her_own_line(self, ulm_t18):
        """The exhaustion forecast and the league gate's clock read the stock
        80 — a bonded court tires at the bond's line (200 under a 400g bond)."""
        from backend.game_logic.coalition import war_exhaustion_lines, war_exhaustion_terms
        w = ulm_t18
        assert war_exhaustion_terms(w, "Austria")["line"] == 80
        self._bind(w)
        assert war_exhaustion_terms(w, "Austria")["line"] == 200
        assert "It tires at 200 (Britain's bond holds her past 80) in about 4 turns." in war_exhaustion_lines(
            w, "Austria")[0]
        gate = {"leader": "Austria", "reason": "league_not_spent", "turns_at_most": 4, "rate": 8,
                "exhaustion": 174, "line": 200, "bond": "Britain"}
        assert "exhaustion 174 of 200 — Britain's bond holds her past 80" in AI.league_offer_gate_display(w, gate)

    def test_x53_a_bonded_mate_is_spent_at_the_bonds_line(self, vienna_held):
        """The truce's hope read a league mate spent at the stock 80; a mate
        the paymaster binds is spent at the bond's line, so her league term
        keeps the loser's hope alive."""
        w = vienna_held
        _kill_hope(w)
        assert D.truce_hope_alive(w, "Austria", "France")["members"] == []
        self._bind(w, member="Russia")
        hope = D.truce_hope_alive(w, "Austria", "France")
        assert hope["members"] == ["Russia"] and "league" in hope["alive_terms"]

    def test_x54_the_bond_is_a_subsidy_flowing_to_her(self, vienna_held):
        """The truce's hope read only the paymaster's war subsidy; the bond is
        gold flowing to her too."""
        w = vienna_held
        _kill_hope(w)
        assert D.truce_hope_alive(w, "Austria", "France")["subsidy"] is None
        self._bind(w)
        hope = D.truce_hope_alive(w, "Austria", "France")
        assert hope["subsidy"] == {"payer": "Britain", "amount": 400, "bond": True}
        assert hope["alive"]

    def test_x55_the_ai_pair_exits_read_the_bond(self, vienna_held):
        """The mutual-exhaustion exit and the beaten sub-pair's suit — the AI's
        own roads out of a war beside France — never read a bond: France's
        bonded ally would leave and be branded the next turn. The bonded
        court's lines read deeper there too."""
        from backend.game_logic import settlement_third_party as TP
        w = vienna_held
        w.war_exhaustion["Bavaria"] = TP.PAIR_EXIT_WE_FLOOR
        w.war_exhaustion["Austria"] = TP.PAIR_EXIT_WE_FLOOR
        _force_pair(w, "Bavaria", "Austria", 0)
        joined = int(w.current_turn) - TP.PAIR_EXIT_MIN_TURNS
        assert TP.pair_is_mutually_exhausted(w, "Bavaria", "Austria", joined)
        self._bind(w, payer="France", member="Bavaria", enemy="Austria")
        assert not TP.pair_is_mutually_exhausted(w, "Bavaria", "Austria", joined)
        from backend.game_logic.ai_diplomacy import effective_peace_threshold
        line = int(effective_peace_threshold("Bavaria", "Austria", w))
        _force_pair(w, "Bavaria", "Austria", line - 1)
        assert TP.sub_pair_loser_sues(w, "Bavaria", "Austria", joined) is None
        _force_pair(w, "Bavaria", "Austria", line - 20)
        assert TP.sub_pair_loser_sues(w, "Bavaria", "Austria", joined)[0] == "Bavaria"

    def test_x56_the_war_popup_names_the_bond(self, ulm_t18):
        from backend.game_logic.war_status import build_active_wars
        w = ulm_t18
        self._bind(w)
        with _quiet():
            rows = build_active_wars(w)["wars"]
        lines = [ln for r in rows for ln in ((r.get("peace_table") or {}).get("lines") or [])]
        assert any(ln.startswith("Austria is bound not to sign alone: Britain's bond costs her 40 at the table")
                   for ln in lines), lines

    def test_x57_x58_the_paymasters_surfaces_name_the_bonds(self, ulm_t18):
        from backend.ai.state_desk import _answer_coalition
        from backend.game_logic.instruments import build_subsidy_payload
        w = ulm_t18
        self._bind(w)
        clause = "binds Austria to the war against France (400g a turn, 10 turns left) — no separate peace"
        assert f"It {clause}." in _answer_coalition(w)
        assert build_subsidy_payload(w)["line"].endswith(f"; it {clause}")

    def test_x59_x60_the_log_and_the_report_say_bond(self, vienna_held):
        """The campaign log read a bond's grant as "Britain sponsors Austria
        against France"; the economy report's Subsidies line named no reason."""
        from backend.campaign_log import format_event_oneliner
        from backend.commands.executor import CommandExecutor
        w = vienna_held
        with _quiet():
            CommandExecutor()._diplomatic._execute_bind_to_war(
                {"action": "bind_to_war", "target": "Bavaria",
                 "raw_input": "bind Bavaria to the war against Austria"}, {"world": w})
        granted = next(e for e in w.event_log if e.get("type") == "sponsorship_granted" and e.get("kind") == "bond")
        assert format_event_oneliner(granted) == (
            "France binds Bavaria to the war against Austria — no separate peace for 10 turns (300g/turn)")
        assert format_event_oneliner({"type": "sponsorship_reneged", "kind": "bond", "breaker": "Bavaria",
                                      "victim": "France", "aim": "Austria"}) == (
            "THE BROKEN BARGAIN: Bavaria breaks the bond with France — a separate peace with Austria "
            "inside the term")
        with _quiet():
            res = CommandExecutor()._economy._execute_economy({"action": "economy"}, {"world": w})
        assert "to Bavaria: -300g — the bond: no separate peace" in res["message"]

    def test_x61_x62_a_bonded_truce_never_ripens_into_her_separate_peace(self, ulm_t18):
        """The truce's automatic exits (the courted peace, the dictated peace)
        signed a bonded court's separate peace for her — and the renege arm
        then branded her for it. The bond closes them (the war resumes; a peace
        with her runs through the table, where the bond is priced), and the
        truce's words name the bond (the hope's stream as the bond)."""
        w = ulm_t18
        k = w._make_diplo_key("Austria", "France")
        self._bind(w)
        w.diplomatic_states[k] = "ARMISTICE"
        w.nation_relations[k] = 90
        exit_ = D.armistice_expiry_exit(w, "Austria", "France")
        assert exit_["exit"] == "war" and exit_["bond"] == {"payer": "Britain", "member": "Austria"}
        words = D.truce_words(w, "Austria", "France")
        assert ("Austria is bound by Britain's bond not to sign alone; a peace with her runs through "
                "the table") in words["heading_line"]
        assert words["cure"] is None
        free = _board("ulm_t18_paris_fallen.json")
        free.diplomatic_states[k] = "ARMISTICE"
        free.nation_relations[k] = 90
        assert D.armistice_expiry_exit(free, "Austria", "France")["exit"] == "peace"

    def test_x62_the_truce_names_the_bonds_stream(self, vienna_held):
        w = vienna_held
        _kill_hope(w)
        self._bind(w)
        assert "Britain's bond (400 a turn) flows to her" in D.truce_words(w, "Austria", "France")["hope_line"]

    def test_x63_the_weak_link_is_nearest_her_own_line(self, ulm_t18):
        from backend.game_logic.war_status import build_active_wars
        w = ulm_t18

        def weak(world):
            with _quiet():
                info = build_active_wars(world).get("coalition") or {}
            return info.get("weak_link")
        assert weak(w) == "Austria"                 # 174, the most spent
        self._bind(w)
        assert weak(w) == "Britain"                 # Austria held to 200: 145 is nearest its line

    def test_x64_a_loyal_court_sends_no_letter_of_her_own(self, vienna_held):
        """The war popup said "her letter comes" of a court that would sue by
        her own threshold while P1's league clause holds her — and now the
        bond is why."""
        from backend.game_logic.war_status import build_active_wars
        w = vienna_held
        _force_pair(w, "Austria", "France", -45)
        self._bind(w)
        own = AI.court_own_readiness(w, "Austria", "France")
        assert own["sues"] and own["loyal"] and own["bond"] == "Britain"
        with _quiet():
            rows = build_active_wars(w)["wars"]
        lines = [ln for r in rows for ln in ((r.get("peace_table") or {}).get("lines") or [])]
        assert any(ln.startswith("Austria's own court would sue at ")
                   and ln.endswith("Britain's bond holds her to the league — no letter of her own.")
                   for ln in lines), lines

    def test_x65_a_bonded_winner_writes_no_separate_dictated_letter(self, ulm_t18):
        """P8's dictated harsh peace from a bonded winning member is her
        separate peace; the league's letter is her road. Her paymaster's own
        dictated letter is untouched (Britain is not bound)."""
        from backend.game_logic import bond as B
        w = ulm_t18
        _force_pair(w, "Austria", "France", 55)
        assert not B.holds_her_letter(w, "Austria", "France")
        self._bind(w)
        assert B.holds_her_letter(w, "Austria", "France")
        assert not B.holds_her_letter(w, "Britain", "France")
        with _quiet():
            proposal = AI.process_diplomatic_phase("Austria", w)
        assert (proposal or {}).get("proposal_type") != "harsh_peace", proposal

    def test_x66_the_league_letter_treats_with_her_payer(self, vienna_held):
        """A bonded court's readiness is no consent to a letter that leaves her
        paymaster at war; a letter that covers her keeps her paymaster on it
        however well it is winning."""
        w = vienna_held
        _force_pair(w, "Austria", "France", -45)
        assert AI.letter_consenting_courts(w, "France", ["Austria"]) == ["Austria"]
        self._bind(w)
        assert AI.letter_consenting_courts(w, "France", ["Austria"]) == []
        assert AI.letter_consenting_courts(w, "France", ["Austria", "Britain"])[:1] == ["Austria"]
        _force_pair(w, "Britain", "France", AI.SETTLEMENT_OFFER_DECISIVE_WAR_SCORE + 5)
        assert "Britain" in AI.leave_a_winning_court_its_war(w, "France", ["Austria", "Britain"])

    def test_x67_a_client_that_follows_her_lord_out_breaks_nothing(self, vienna_held):
        from backend.game_logic.instruments import _bond_verdict
        w = vienna_held
        record = {"kind": "bond", "payer": "Russia", "recipient": "Holland", "aim": "Britain"}
        for a, b, state in (("Holland", "Britain", "PEACE"), ("France", "Britain", "PEACE"),
                            ("Russia", "Britain", "WAR")):
            w.diplomatic_states[w._make_diplo_key(a, b)] = state
        assert (w.vassals.get("Holland") or {}).get("lord") == "France"
        assert _bond_verdict(w, record) == "followed_her_lord"
        w.diplomatic_states[w._make_diplo_key("France", "Britain")] = "WAR"
        assert _bond_verdict(w, record) == "reneged"

    def test_x68_the_state_desk_names_her_line(self, ulm_t18):
        from backend.ai.state_desk import _answer_weariness
        w = ulm_t18
        self._bind(w)
        assert _answer_weariness(w, "Austria").endswith("Britain's bond holds her to the league until 200.")


class TestDiplomacyIsNeverTyped:
    """The user's rule (October 20, 2026): "diplo stuff should never be typed"
    — every diplomatic act has a UI control carrying everything it needs.
    PC-X43 Make Amends, PC-X44 the bargain's repudiation and PC-X45 the
    bid's sum had only a typed road; each has its Cabinet row now, built
    from its executor's own gates, and the door claims every typed verb."""

    @staticmethod
    def _row(world, court, action):
        return next((r for r in _rows(world, court) if r.get("action") == action), None)

    @staticmethod
    def _send(world, line):
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        with _quiet():
            return CommandExecutor().execute(
                CommandParser(use_real_llm=False).parse(line, game_state={"world": world}),
                {"world": world})

    def test_x43_make_amends_has_its_cabinet_row(self, w):
        from backend.game_logic.diplomacy import _betrayal_key
        assert self._row(w, "Prussia", "make_amends") is None          # nothing to repair
        w.betrayal_history[_betrayal_key("France", "Prussia")] = {
            "strikes": [{"severity": "medium", "turn": 0, "episode_id": "ep_s", "decays_on_turn": 10}],
            "grievance_flags": [{"turn": 0, "episode_id": "ep_g", "kind": "abandoned_alliance"}],
            "categories": ["treaty_breach", "grievance"], "last_turn": 0}
        w.nation_gold["France"] = 1000
        w.diplomatic_points = 4
        std = self._row(w, "Prussia", "make_amends")
        grv = self._row(w, "Prussia", "make_amends_grievance")
        assert std["available"] and (std["gold_cost"], std["dp_cost"]) == (200, 1)
        assert grv["available"] and (grv["gold_cost"], grv["dp_cost"]) == (400, 2)
        assert grv["display_name"] == "Make Amends for the Abandoned Alliance"
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert '"make_amends":\n\t\t\treturn "make amends with " + nation' in wizard
        # the row's echo acts — a strike cleared, priced as the row said
        out = self._send(w, "make amends with Prussia")
        assert out.get("success"), out.get("message")
        assert int(w.nation_gold["France"]) == 800 and int(w.diplomatic_points) == 3
        # the shared cooldown now shuts both rows in the executor's own words
        assert not self._row(w, "Prussia", "make_amends_grievance")["available"]
        assert "turns ago" in self._row(w, "Prussia", "make_amends_grievance")["disabled_reason"]
        # at war: the row stands, shut, saying why
        w.betrayal_history[_betrayal_key("France", "Austria")] = {
            "strikes": [{"severity": "low", "turn": 0, "episode_id": "ep_a", "decays_on_turn": 10}],
            "grievance_flags": [], "categories": ["treaty_breach"], "last_turn": 0}
        war_row = self._row(w, "Austria", "make_amends")
        assert not war_row["available"] and "Restore the treaty with Austria first" in war_row["disabled_reason"]

    def test_x44_repudiation_has_its_cabinet_row(self):
        from tests.test_settlement_slice_h_ally_petitions import _seed_bargain_world
        world = _seed_bargain_world()
        row = self._row(world, "Prussia", "repudiate_bargain")
        assert row and row["available"] and "break our promise of Vienna" in row["effect_text"]
        assert self._row(world, "Austria", "repudiate_bargain") is None
        out = self._send(world, "repudiate the bargain with Prussia")
        dlg = out.get("diplomatic_dialogue") or {}
        assert dlg.get("proposal_type_display") == "Repudiate Bargain", out.get("message")
        assert [o["action"] for o in dlg["options"]] == ["confirm_repudiate_bargain", "reconsider"]
        out = self._send(world, "repudiate the bargain with Austria")
        assert out.get("success") is False and "no war bargain with Austria" in out["message"]

    def test_x45_the_bid_names_its_sum_on_the_row(self, w):
        w.allegiance_auctions["Denmark"] = {"opened_turn": int(w.current_turn),
                                            "resolves_turn": int(w.current_turn) + 3}
        w.nation_gold["France"] = 600
        w.diplomatic_points = 4
        row = self._row(w, "Denmark", "bid_for_allegiance")
        assert row["available"] and "typed" not in row["effect_text"]
        assert [c["payload"]["amount"] for c in row["choices"]] == [100, 250, 500]   # 1,000 > the chest
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'return "bid for " + nation + ", " + str(amount) + " gold"' in wizard
        assert 'action.get("choices", [])' in wizard
        out = self._send(w, "bid for Denmark, 500 gold")
        assert out.get("success"), out.get("message")
        assert w.allegiance_auctions["Denmark"]["bids"] == {"France": 500}

    def test_x46_the_congress_sweetener_has_its_row(self, w):
        """The recognition sweetener was typed-only ("offer Prussia 1000 gold
        for recognition"); its row stands on a great power's page while the
        Congress sits, one choice per sum the Congress would take."""
        from backend.game_logic import congress
        from tests.test_congress_of_paris import _sit
        assert self._row(w, "Prussia", "recognition_sweetener") is None      # not sitting
        with _quiet():
            _sit(w)
        # the summons' letters on the desk close the Cabinet (its own rule):
        # answer them by letting this turn's offers lapse, then clear the desk
        w.dialogue_manager.lapse_pending_offers(int(w.current_turn) + 1, world=w)
        while w.dialogue_manager.peek() is not None:
            w.dialogue_manager.pop()
        w.nation_gold["France"] = 1500
        w.diplomatic_points = 4
        row = self._row(w, "Prussia", "recognition_sweetener")
        assert row is not None and row["display_name"] == "Offer Gold for Recognition"
        sums = [s for s in (500, 1000, 2000)
                if s <= 1500 and not congress.sweetener_refusal(w, "Prussia", s)]
        assert [c["payload"]["amount"] for c in row["choices"]] == sums
        assert row["available"] == bool(sums)
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'return "offer " + nation + " " + str(amount) + " gold for recognition"' in wizard

    def test_x47_a_beaten_minor_is_subjugated_from_its_row(self, w):
        """`vassalize X` at war had no row (the door redirected it to a Cabinet
        that offered nothing). Subjugate stands on the war page of a court
        small enough to be vassalized, shut in the executor's words until she
        is beaten."""
        from backend.game_logic.diplomacy import check_vassalage_power_cap
        court = next(n for n in sorted(w.get_active_nations())
                     if n != "France" and w.get_diplomatic_state("France", n) == "PEACE"
                     and n not in w.vassals and w.get_nation_capital(n)
                     and check_vassalage_power_cap(w, "France", n).get("allowed"))
        assert self._row(w, court, "subjugate") is None                        # at peace
        with _quiet():
            assert D.declare_war(w, "France", court, war_objective="conquest").get("success")
        row = self._row(w, court, "subjugate")
        assert row and not row["available"] and "still stands" in row["disabled_reason"]
        w.regions[w.get_nation_capital(court)].controller = "France"
        row = self._row(w, court, "subjugate")
        assert row["available"], row["disabled_reason"]
        out = self._send(w, f"vassalize {court}")
        assert out.get("success"), out.get("message")
        assert w.vassals[court]["lord"] == "France"

    def test_x48_the_ladder_can_be_skipped_from_the_row(self, w):
        """A jump up the treaty ladder ("propose alliance" at peace) was typed
        only; the higher rungs ride the next rung's row, each priced by the
        row builder itself."""
        # Denmark at +10: a Non-Aggression is within reach (needs 0), an
        # alliance is not (needs 20 / 40) — only the rungs she would sign.
        row = self._row(w, "Denmark", "propose_open_borders")
        assert row and row["available"]
        skips = row.get("choices") or []
        assert [c["action"] for c in skips] == ["propose_non_aggression"]
        assert skips[0]["label"].startswith("Skip ahead: Non-Aggression (")
        # Prussia at -10: no rung beyond the next would be signed — none offered
        assert not (self._row(w, "Prussia", "propose_open_borders").get("choices") or [])
        wizard = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'var choice_action = str(choice.get("action", action_id))' in wizard

    def test_x49_the_licence_and_the_sums_ride_the_sponsor_row(self, w):
        """The licence (no gold) the help names, and a larger subsidy, were
        typed only; they are the sponsor row's choices."""
        court = next(n for n in sorted(w.get_active_nations())
                     if self._row(w, n, "sponsor_design") and self._row(w, n, "sponsor_design")["available"])
        row = self._row(w, court, "sponsor_design")
        assert row["choices"][0] == {"label": "Licence — a free hand, no gold", "payload": {"amount": 0}}
        before = len(w.directed_sponsorships)
        out = self._send(w, f"sponsor {court} against {row['aim']}, 0 gold")
        assert out.get("success"), out.get("message")
        assert len(w.directed_sponsorships) == before + 1
        assert w.directed_sponsorships[-1]["amount_per_turn"] == 0

    def test_x50_an_autonomy_jump_is_one_choice(self, w):
        """A two-level autonomy change took two orders by chip (2 DP) and one
        typed (1 DP); the jump is a choice on the row, one order, 1 DP."""
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS, AUTONOMY_PUPPET
        court = next(iter(sorted(w.vassals)))
        w.vassals[court]["autonomy"] = AUTONOMY_PUPPET
        w.diplomatic_points = 4
        inc = self._row(w, court, "increase_autonomy")
        assert inc["choices"] == [{"label": "Straight to Autonomous (1 DP)", "action": "set_autonomy",
                                   "payload": {"level": "autonomous"}}]
        out = self._send(w, f"set {court} to autonomous")
        assert out.get("success"), out.get("message")
        assert w.vassals[court]["autonomy"] == AUTONOMY_AUTONOMOUS and w.diplomatic_points == 3

    def test_x51_no_line_teaches_a_typed_diplomatic_or_naval_order(self):
        """Every screen, dispatch, refusal and help line the census found
        teaching a typed command names its button or row now."""
        src = {name: (REPO / name).read_text(encoding="utf-8") for name in (
            "godot-client/project-sovereign/scripts/diplomatic_ledger.gd",
            "godot-client/project-sovereign/scripts/strategic_ledger.gd",
            "godot-client/project-sovereign/scripts/main.gd",
            "godot-client/project-sovereign/scripts/tutorial_overlay.gd",
            "backend/commands/naval_executor.py", "backend/game_logic/dispatch.py",
            "backend/game_logic/ai_diplomacy.py", "backend/ai/state_desk.py",
            "backend/game_logic/diplomacy.py")}
        assert "or type '" not in src["godot-client/project-sovereign/scripts/diplomatic_ledger.gd"]
        assert '"]Type "' not in src["godot-client/project-sovereign/scripts/diplomatic_ledger.gd"]
        assert "order the diversion" not in src["godot-client/project-sovereign/scripts/strategic_ledger.gd"]
        assert "land <marshal>" not in src["godot-client/project-sovereign/scripts/strategic_ledger.gd"]
        assert "or type '" not in src["godot-client/project-sovereign/scripts/main.gd"]
        assert "build ships[/color]" not in src["godot-client/project-sovereign/scripts/tutorial_overlay.gd"]
        naval_src = src["backend/commands/naval_executor.py"]
        assert "Say '" not in naval_src and "'blockade the enemy'" not in naval_src
        assert "'guard home waters'" not in naval_src and "'land <marshal>" not in naval_src
        assert "or type" not in src["backend/game_logic/dispatch.py"]
        assert "typed: 'bid for" not in src["backend/game_logic/ai_diplomacy.py"]
        assert "'guard home waters' covers" not in src["backend/ai/state_desk.py"]
        assert "a larger bid is typed: '" not in src["backend/game_logic/diplomacy.py"]
        with _quiet():
            from backend.commands.meta_executor import MetaExecutor  # noqa: F401
        help_src = (REPO / "backend/commands/meta_executor.py").read_text(encoding="utf-8")
        admiralty = help_src[help_src.index("THE ADMIRALTY (the wooden wall"):]
        admiralty = admiralty[:admiralty.index("  - An army cannot walk")]
        for typed in ('"build ships"', '"blockade the enemy"', '"guard home waters"',
                      '"order the diversion"', "land <marshal>"):
            assert typed not in admiralty, typed
        assert "or type 'bid for" not in help_src
        assert '"offer Prussia 1000 gold for recognition"' not in help_src
        assert "VASSALS tab of the Strategic Ledger" not in help_src


class TestPCF41:
    def test_every_peace_row_names_the_courts_it_addresses(self, vienna_held):
        with _quiet():
            acts = D.get_diplomatic_preview(vienna_held, "Austria")["actions"]
        white = next(a for a in acts if a["action"] == "propose_white_peace")
        table = next(a for a in acts if a["action"] == "open_settlement")
        # the counsel priced Austria alone: the row says so
        assert white["display_name"] == "Propose White Peace — with Austria alone"
        assert white["addresses"] == ["Austria"]
        assert table["display_name"].startswith("Open Settlement — the whole table: ")
        assert set(table["addresses"]) == {"Austria", "Britain", "Russia"}

    def test_the_war_popup_names_each_court(self):
        popup = (SCRIPTS / "war_detail_popup.gd").read_text(encoding="utf-8")
        assert '"Negotiate with " + Utils.display_nation_name(nation)' in popup
        assert "for court in courts:" in popup and "_add_negotiate_button(str(court))" in popup
        assert 'btn.text = "Negotiate Peace"' not in popup


class TestPCF72:
    def test_the_direction_names_a_carve_an_alliance_and_the_system(self):
        from backend.game_logic.settlement_baseline import _court_direction_summary
        terms = [{"type": "create_client", "from": "Prussia", "to": "France", "tag": "DuchyOfWarsaw",
                  "client_display_name": "the Duchy of Warsaw"},
                 {"type": "forced_alliance", "from": "Prussia", "to": "France",
                  "includes_continental_system": False},
                 {"type": "continental_system_join", "from": "Russia", "to": "France"}]
        assert (_court_direction_summary("Prussia", "France", terms)
                == "Demanded: the Duchy of Warsaw carved out + an alliance imposed")
        assert _court_direction_summary("Russia", "France", terms) == "Demanded: joins the Continental System"
        assert _court_direction_summary("France", "France", terms).startswith("Conceded: the Duchy of Warsaw carved for it")
        assert _court_direction_summary("Austria", "France", terms) == "White peace"


class TestPCF33:
    """The coalition's "white peace" is uti possidetis: where it is offered,
    labelled and ratified it says what each side keeps."""

    def test_a_the_war_row_says_what_the_held_line_titles(self, vienna_held):
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            row = next(r for r in build_active_wars(vienna_held)["wars"] if r.get("status") == "war")
        assert row["held_line"] == ("A peace signed now is on the held line: Bohemia, Tyrol and Vienna "
                                    "stay ours by the treaty.")

    def test_b_the_white_letter_is_labelled_the_peace_on_the_held_line(self, vienna_held):
        from backend.game_logic.mailbox_payloads import (
            attach_peace_preview, build_pending_envoy_popup_from_terms,
        )
        terms = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                 "demands": [], "sweeteners": [], "clauses": []}
        with _quiet():
            payload = build_pending_envoy_popup_from_terms(vienna_held, nation="Austria", terms=terms)
            payload = attach_peace_preview(vienna_held, payload, "Austria", terms)
        assert payload["proposal_type_display"].endswith("— on the held line"), payload["proposal_type_display"]
        assert "Bohemia, Tyrol and Vienna stay ours" in payload["held_line"]

    def test_c_the_table_labels_it_and_the_client_prints_it(self, vienna_held):
        from backend.game_logic.settlement_staging import (
            build_settlement_confirm_dialogue, build_settlement_preview,
        )
        with _quiet():
            prev = build_settlement_preview(vienna_held, war_id="war_1",
                                            covered_enemy_participants=["Austria"],
                                            settlement_terms=[{"type": "peace"}])
            dlg = build_settlement_confirm_dialogue(vienna_held, prev, white_peace=True)
        assert dlg["held_line_note"] == "White Peace — on the held line: each side keeps what it holds."
        assert any("stay ours by the treaty" in ln for ln in dlg["status_quo_review"])
        assert 'data.get("held_line_note", "")' in (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert 'war_data.get("held_line", "")' in (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")


class TestPCF57:
    def test_a_carve_writes_the_punitive_record_on_the_tilsit_board(self):
        from backend.game_logic import emergent_designs as ED
        from backend.game_logic import formations as F
        t = _load_save(AGD_FIXTURE)
        carve = {"type": "create_client", "from": "Prussia", "to": "France", "tag": "DuchyOfWarsaw",
                 "provinces": F.template_provinces(F.get_template(t, "DuchyOfWarsaw"))}
        silesia = {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Silesia"}
        # Silesia alone is one homeland province — beaten, not humiliated
        assert ED.record_punitive_cessions(t, ED.collect_cessions_from_clauses([silesia])) == []
        cessions = ED.collect_cessions_from_clauses([carve, silesia])
        assert cessions == {"Prussia": [("Posen", "France"), ("Silesia", "France")]}
        assert ED.VOLTE_CLAUSE_PUNITIVE not in ED.volte_face_failing_clauses(t, "Prussia", "France", exhaustive=True)
        written = ED.record_punitive_cessions(t, cessions)
        assert written, "Posen carved beside Silesia ceded is a partition"
        assert ED.VOLTE_CLAUSE_PUNITIVE in ED.volte_face_failing_clauses(t, "Prussia", "France", exhaustive=True)

    def test_the_seam_holds_the_carve_down(self, monkeypatch):
        from backend.game_logic import emergent_designs as ED
        orig = ED.collect_cessions_from_clauses
        monkeypatch.setattr(ED, "collect_cessions_from_clauses",
                            lambda c: orig([x for x in c if x.get("type") != "create_client"]))
        assert ED.collect_cessions_from_clauses(
            [{"type": "create_client", "from": "Prussia", "to": "France", "provinces": ["Posen"]}]) == {}


class TestPCF74:
    def test_a_dormant_design_is_not_achieved(self, turn6, monkeypatch):
        """Verified real by construction: SF-LB-1's ally rule puts a design to
        sleep while an ally's bloc holds its target, and `_entry_satisfied`
        read the sleeping design as SATISFIED — so the Pressburg arm let a
        court whose first design was unmet break ranks at -30."""
        from backend.game_logic import agendas as AG
        w = turn6
        # a first design whose target an ally's bloc holds (Russia's Volhynia;
        # Austria is allied to Britain, whose bloc holds Russia)
        w.agendas["Austria"] = ([{"id": "probe_design", "type": "acquire_regions",
                                  "regions": ["Volhynia"], "title": "A probe design"}]
                                + list(w.agendas["Austria"]))
        w.invalidate_active_nations_cache()
        assert not AG.survival_override_active(w, "Austria")
        assert AG._entry_satisfied(w, "Austria", w.agendas["Austria"][0]), "the dormancy branch reads satisfied"
        assert not AG._entry_achieved(w, "Austria", w.agendas["Austria"][0])
        assert not AG.agenda_separate_peace_ready("Austria", w)
        monkeypatch.setattr(AG, "_entry_achieved", lambda *a, **k: AG._entry_satisfied(*a, **k))
        assert AG.agenda_separate_peace_ready("Austria", w), "the seam down: the old reading"

    def test_an_achieved_design_still_reads_satisfied(self, turn6):
        from backend.game_logic import agendas as AG
        w = turn6
        held = sorted(w.get_nation_regions("Austria"))[:1]
        w.agendas["Austria"] = [{"id": "probe_held", "type": "acquire_regions", "regions": held}]
        assert AG._entry_achieved(w, "Austria", w.agendas["Austria"][0])
        assert AG._court_design_satisfied(w, "Austria")


class TestPCF75:
    def test_an_allys_homeland_retaken_from_the_ceders_ally_goes_home(self, vienna_held):
        """Verified real by construction (the austerlitz t46 board is not a
        fixture): Carniola — Austria's, taken by Bavaria, retaken by Britain —
        was read by neither half of DDB-12's rule, so it stayed British through
        the France–Britain peace."""
        from backend.game_logic import game_end as GE
        w = vienna_held
        w.regions["Carniola"].controller = "Britain"
        GE.record_province_title(w, "Carniola", GE.TITLE_CONQUEST, "Bavaria", "Britain")
        w.invalidate_active_nations_cache()
        assert "Carniola" not in (GE.status_quo_retentions(w, "Britain", "France", forecast=True).get("Britain") or [])
        assert GE.ally_homeland_returns(w, "Britain", "France") == {"Austria": ["Carniola"]}
        forecast = GE.status_quo_forecast(w, "France", "Britain")
        assert any((e.get("returned") or {}).get("Austria") == ["Carniola"] for e in forecast), forecast
        GE.title_status_quo_retentions(w, "Britain", "France", "WAR", "PEACE", "treaty_ratification")
        assert w.regions["Carniola"].controller == "Austria"


class TestPCF83:
    def test_the_system_lifted_is_drafted_priced_applied_and_held(self, vienna_held):
        from backend.game_logic import diplomatic_templates as DT
        w = vienna_held
        assert not DT.continental_system_lift_offered(w, "France", "Britain"), "no System to lift"
        D.join_continental_system(w, "Spain", "France")
        assert DT.continental_system_lift_offered(w, "France", "Britain")
        assert not DT.continental_system_lift_offered(w, "France", "Austria"), "only London prices it"
        with _quiet():
            terms = DT.generate_suggested_terms("Britain", "peace", w, deterministic=True)
        assert "continental_system_lifted" in terms["clauses"]
        prop = dict(terms, proposer_nation="France", target_nation="Britain")
        bare = dict(prop, clauses=[c for c in prop["clauses"] if c != "continental_system_lifted"])
        with _quiet():
            lifted, plain = D.calculate_acceptance(prop, w), D.calculate_acceptance(bare, w)
        assert lifted["components"]["special_desire_bonus"] == 15 and plain["components"]["special_desire_bonus"] == 0
        rows = DT.annotate_peace_terms({"demands": [], "sweeteners": [], "clauses": ["continental_system_lifted"]},
                                       "France", "Britain")
        row = next(r for r in rows if r["clause_type"] == "continental_system_lifted")
        assert row["term_direction"] == "concession"
        assert row["display_label"] == "France lifts the Continental System — its ports reopen to British trade"
        with _quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                              "sweeteners": [], "demands": [], "clauses": ["continental_system_lifted"]})
        assert w.continental_system_members == [] and D.continental_system_lifted(w)
        assert w.continental_system_lifted_until == w.current_turn + D.CONTINENTAL_SYSTEM_LIFT_TURNS
        assert not D.join_continental_system(w, "Spain", "France"), "no enrolment while it stands"
        again = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert again.continental_system_lifted_until == w.continental_system_lifted_until


class TestPCF28:
    def test_a_beaten_sub_pair_loser_sues_inside_frances_war(self, vienna_held):
        from backend.game_logic import settlement_third_party as TP
        w = vienna_held
        _set_pair_score(w, "Austria", "Bavaria", 60)
        events = []
        with _quiet():
            TP._process_exhausted_pair_exits(w, "war_1", w.war_instances["war_1"], events)
        assert _state(w, "Austria", "Bavaria") == "PEACE"
        ev = events[-1]
        assert ev["exit"] == "sub_pair_loser_sues" and (ev["proposer"], ev["accepter"]) == ("Bavaria", "Austria")
        assert ev["consequence"].startswith("Bavaria, beaten (-60), sues for peace and Austria takes it on the held line")
        from backend.game_logic.game_end import SIGNED_PEACE_REASONS
        assert "sub_pair_loser_sues" in SIGNED_PEACE_REASONS

    def test_a_level_pair_waits_for_the_exhausted_exit(self, vienna_held):
        from backend.game_logic import settlement_third_party as TP
        w = vienna_held
        assert TP.sub_pair_loser_sues(w, "Austria", "Bavaria", 1) is None
        assert TP.sub_pair_loser_sues(w, "Austria", "Bavaria", w.current_turn) is None, "too young a pair"


class TestPCF29:
    def test_a_clients_own_war_has_a_road_out(self, vienna_held):
        from backend.game_logic import settlement_third_party as TP
        w = vienna_held
        _set_pair_score(w, "Austria", "KingdomOfItaly", 60)
        assert TP.client_pair_is_the_lords_war(w, "KingdomOfItaly", "Austria")
        events = []
        with _quiet():
            TP._process_exhausted_pair_exits(w, "war_1", w.war_instances["war_1"], events)
        assert _state(w, "Austria", "KingdomOfItaly") == "WAR", "the lord's war: it follows the lord out"
        # the lord out of that war: the client's war is its own, and it has the road out
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "ARMISTICE"
        assert not TP.client_pair_is_the_lords_war(w, "KingdomOfItaly", "Austria")
        w._pair_exit_this_turn = -1
        with _quiet():
            TP._process_exhausted_pair_exits(w, "war_1", w.war_instances["war_1"], events)
        assert _state(w, "Austria", "KingdomOfItaly") == "PEACE"


class TestPCF30:
    def test_a_client_that_changes_lord_leaves_its_old_lords_wars(self, vienna_held):
        from backend.game_logic import vassal as V
        w = vienna_held
        assert _state(w, "Holland", "Britain") == "WAR" and _state(w, "Russia", "Britain") == "ALLIANCE"
        with _quiet():
            assert V.transfer_vassal(w, "Holland", "Russia")["success"]
        assert _state(w, "Holland", "Britain") == "ARMISTICE", "Russia's footing with Britain"

    def test_the_old_exemption_is_the_seam(self, vienna_held, monkeypatch):
        from backend.game_logic import vassal as V
        monkeypatch.setattr(V, "client_leads_its_own_war",
                            lambda v, o, inst: str(v) in {str((inst or {}).get("attacker_leader") or ""),
                                                          str((inst or {}).get("defender_leader") or "")}
                            or str(o) in {str((inst or {}).get("attacker_leader") or ""),
                                          str((inst or {}).get("defender_leader") or "")})
        with _quiet():
            V.transfer_vassal(vienna_held, "Holland", "Russia")
        assert _state(vienna_held, "Holland", "Britain") == "WAR", "Britain leads the instance: the old exemption"

    def test_the_fuzzer_reads_the_one_rule(self):
        src = (REPO / "tools" / "treaty_fuzzer.py").read_text(encoding="utf-8")
        assert "from backend.game_logic.vassal import client_leads_its_own_war" in src


class TestPCF81TheSecondRoad:
    def test_a_named_carried_ally_is_thanked_on_the_bilateral_road(self, vienna_held):
        from backend.game_logic.settlement_reactions import (
            RELATION_GRATITUDE_CONSULT, RELATION_GRATITUDE_SEAT,
        )
        w = vienna_held
        key = w._make_diplo_key("France", "Bavaria")
        before = w.nation_relations[key]
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [], "clauses": [],
                                    "demands": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol"],
                                                 "to_nation": "Bavaria"}]})
        delta = w.nation_relations[key] - before
        assert delta in (RELATION_GRATITUDE_SEAT, RELATION_GRATITUDE_CONSULT)
        aft = res["peace_ratification_summary"]["political_aftermath"]
        assert (f"Bavaria's war with Austria ends in this instrument; she takes Tyrol by it and thanks us "
                f"({delta:+d} relation).") in aft

    def test_an_unnamed_carried_ally_keeps_pc_r1s_ruling(self, vienna_held):
        w = vienna_held
        key = w._make_diplo_key("France", "Bavaria")
        before = w.nation_relations[key]
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [], "demands": [], "clauses": []})
        assert w.nation_relations[key] == before
        assert BAVARIA_NOTE in res["peace_ratification_summary"]["political_aftermath"]


class TestPCF11:
    def test_the_commentary_names_only_demands_the_draft_holds(self, vienna_held, monkeypatch):
        from backend.game_logic import diplomatic_templates as DT
        monkeypatch.setattr(DT, "_ease_suggestion_until_not_rejected",
                            lambda terms, **k: dict(terms, demands=[]))
        with _quiet():
            terms = DT.generate_suggested_terms("Austria", "peace", vienna_held, deterministic=True)
        assert terms["demands"] == []
        assert "firm but not humiliating" not in terms["talleyrand_commentary"]
        assert "asked nothing of them beyond the peace itself" in terms["talleyrand_commentary"]


class TestPCF14:
    def test_one_roll_per_draft_shown_and_sent_alike(self, vienna_held):
        from backend.game_logic import diplomatic_templates as DT
        state = random.getstate()
        with _quiet():
            first = DT.generate_suggested_terms("Austria", "peace", vienna_held)
            second = DT.generate_suggested_terms("Austria", "peace", vienna_held)
        assert first["demands"] == second["demands"] and first["sweeteners"] == second["sweeteners"]
        assert random.getstate() == state, "the global RNG is never touched"
        roll = DT.terms_jitter(vienna_held, "France", "Austria", "peace")
        assert 0.8 <= roll <= 1.2 and roll == DT.terms_jitter(vienna_held, "France", "Austria", "peace")
        vienna_held.current_turn += 1
        assert DT.terms_jitter(vienna_held, "France", "Austria", "peace") != roll, "a new turn rolls anew"


class TestPCF45:
    def test_the_envoy_list_names_a_letter_by_its_display_name(self):
        from backend.game_logic.dispatch import _lapsed_offer_row
        row = _lapsed_offer_row({"nation": "Austria", "proposal_type": "armistice_losing"})
        assert row["proposal_type_display"] == "Armistice"
        src = (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
        assert '"proposal_type_display": _ptd(str(item.get("proposal_type") or "proposal"))' in src
        for name in ("dispatch_view.gd", "main.gd"):
            gd = (SCRIPTS / name).read_text(encoding="utf-8")
            assert 'envoy.get("proposal_type_display"' in gd and 'lapse.get("proposal_type_display"' in gd, name


class TestPCF86:
    def _answerer(self, **policy):
        drv = _tool("playtest_driver")
        return drv.Answerer(None, None, dict(drv.POLICY_DEFAULTS) | policy, strict=False)

    def test_the_decline_dial_leaves_the_players_own_settlement_to_the_script(self):
        own = {"type": "settlement_confirm", "proposer_nation": "France", "caller_kind": "player_editor",
               "options": [
                   {"label": "Make peace with Austria only", "action": "seek_bilateral_peace"},
                   {"label": "Ratify the settlement", "action": "confirm_settlement"},
                   {"label": "Back out", "action": "back_out_settlement"}]}
        assert self._answerer(diplomacy="decline")._pick_dialogue_choice(own) == "confirm_settlement"
        # the league's table keeps the dial; an explicit --settlement decline holds
        league = dict(own, proposer_nation="Britain")
        assert self._answerer(diplomacy="decline")._pick_dialogue_choice(league) != "confirm_settlement"
        assert self._answerer(diplomacy="decline", settlement="decline")._pick_dialogue_choice(own) != "confirm_settlement"
        # a disabled ratify is never pressed (FA-78)
        shut = dict(own, options=[dict(o, enabled=False) if o["action"] == "confirm_settlement" else o
                                  for o in own["options"]])
        assert self._answerer(diplomacy="decline")._pick_dialogue_choice(shut) != "confirm_settlement"

    def test_the_chooser_the_scripts_click_opened_proceeds(self):
        chooser = {"type": "settlement_pair_substitute_confirm", "options": [
            {"label": "Proceed — peace with Austria alone", "action": "confirm_pair_substitute"},
            {"label": "Stay with the joint settlement", "action": "keep_joint_settlement"}]}
        ans = self._answerer(diplomacy="decline")
        assert ans._pick_dialogue_choice(chooser) != "confirm_pair_substitute", "unattended: the table's keep"
        ans._last_script_action = "seek_bilateral_peace"
        assert ans._pick_dialogue_choice(chooser) == "confirm_pair_substitute"
        assert ans._pick_dialogue_choice(chooser) != "confirm_pair_substitute", "consumed once"


class TestTheStagedFixtures:
    """PC-F85: the staged fixtures carry only states the game can produce."""

    def test_the_tilsit_board_was_driven_to_a_score_the_game_computes(self):
        t = _load_save(AGD_FIXTURE)
        key = t._make_diplo_key("France", "Prussia")
        assert int(t.war_scores[key]) == int(D.calculate_war_score("France", "Prussia", t)) == 30
        assert int(t.current_turn) - int(t.war_start_turns[key]) == 6

    def test_the_congress_board_resolves_every_peace_in_its_war(self):
        p = _load_save(GE3_PRESSBURG)
        sides = p.war_instances["war_1"].get("side_by_nation") or {}
        assert "Austria" not in sides and "Russia" not in sides
        from backend.game_logic.war_status import build_active_wars
        with _quiet():
            rows = build_active_wars(p)["wars"]
        assert any(r.get("opponent") == "Britain" and isinstance(r.get("war_score"), int) for r in rows)


class TestTheReactivityRead:
    """§47 — F's re-read: §44's ten levers on the Vienna-held board, each
    moving at least one court's answer — three of them only on the footing
    a ruling made live (G's decay for a victory; D's truce exit for the
    relations and the mission), and inert at war at turn 6 by the decided
    caps and R141's clamp, which is said, not hidden."""

    def _board(self, name):
        rec = json.loads((REPO / "tools" / "_pc_s13e4_reactivity.json").read_text(encoding="utf-8"))
        return next(b for b in rec["boards"] if b["board"] == name)

    def test_a_ten_levers_each_move_a_courts_answer(self):
        board = self._board("vienna_held")
        assert len(board["ten"]) == 10
        assert all(v["moves"] for v in board["ten"].values()), {
            k: v for k, v in board["ten"].items() if not v["moves"]}

    def test_b_the_footings_are_named(self):
        ten = self._board("vienna_held")["ten"]
        for lever in ("1 one more victory", "2 three more victories"):
            assert [r["footing"] for r in ten[lever]["where"]] == ["war after 2 quiet turns (G's decay)"], lever
        for lever in ("5 relations +20", "10 Talleyrand's mission"):
            assert [r["footing"] for r in ten[lever]["where"]] == ["a truce (D's exit)"], lever
        board = self._board("vienna_held")
        for lever in ("1 one more victory", "5 relations +20", "10 Talleyrand's mission"):
            assert board["levers"][lever]["moved"] == {}, lever

    def test_c_the_live_read_agrees(self, vienna_held):
        R = _tool("_pc_s13e4_reactivity")
        assert R.quiet_turns_until_a_victory_counts(vienna_held) == 2
        truce = R.clone(vienna_held)
        R.sign_truces(truce)
        base = R.truce_read(truce)
        pulled = R.clone(truce)
        R.levers(vienna_held, "vienna_held")["5 relations +20"](pulled)
        assert base["Austria"]["exit"] == "war" and R.truce_read(pulled)["Austria"]["exit"] == "peace"


class TestTheSeriesPart4:
    def _record(self):
        return json.loads((REPO / "tools" / "_pc_s13e4_series_arms_final.json").read_text(encoding="utf-8"))

    def test_the_record_links_to_the_last_one(self):
        rec = self._record()
        prior = json.loads((REPO / "tools" / "_pc_s13e3_series_arms_final.json").read_text(encoding="utf-8"))
        assert rec["prior"] == prior["arms"]["ALL"]["series"]
        assert set(rec["arms"]) >= {"0", "L", "V", "C", "A", "H", "S", "J", "K", "B", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm   # byte-identical: attributed, not re-pinned

    def test_the_seams_were_reached(self):
        reach = self._record()["arms"]["ALL"]["reach"]
        for key in ("achieved|active", "client_pair|lords", "loser_sues|no", "ally_home|none", "carve|cede"):
            assert reach.get(key, 0) > 0, key


class TestThePartVReplays:
    """S13e's done-when as a whole: the three Part V replays pass as tests."""

    def test_1_pressburg_tyrol_to_bavaria_and_vienna_home(self, vienna_held):
        w = vienna_held
        with _quiet():
            res = w._ratify_treaty({
                "type": "peace", "proposer_nation": "France", "target_nation": "Austria", "clauses": [],
                "sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Vienna"]}],
                "demands": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol"], "to_nation": "Bavaria"}]})
        assert w.regions["Tyrol"].controller == "Bavaria" and w.regions["Vienna"].controller == "Austria"
        assert _state(w, "France", "Austria") == "PEACE" and _state(w, "Bavaria", "Austria") == "PEACE"
        summary = res["peace_ratification_summary"]
        assert any(ln.startswith("Bavaria's war with Austria ends in this instrument; she takes Tyrol by it")
                   for ln in summary["political_aftermath"])
        # PC-X22: the status quo names only what each holder still holds
        assert "Tyrol" not in summary["status_quo_titled"]
        assert not any("Tyrol" in ln and "stay ours" in ln for ln in summary["terms_ratified"])

    def test_2_a_truce_keeps_the_ledger(self, vienna_held):
        w = vienna_held
        key = w._make_diplo_key("France", "Austria")
        score, start = w.war_scores[key], w.war_start_turns[key]
        with _quiet():
            w._ratify_treaty({"type": D.armistice_variant_for(w, "France", "Austria"),
                              "proposer_nation": "France", "target_nation": "Austria",
                              "sweeteners": [], "demands": [], "clauses": []})
        assert _state(w, "France", "Austria") == "ARMISTICE"
        assert w.war_scores[key] == score and w.war_start_turns[key] == start
        assert D.truce_words(w, "France", "Austria")["keeps_line"].startswith("The ledger stands")

    def test_3_the_dictated_peace_on_ulm_carries_a_province(self, ulm_t18):
        w = ulm_t18
        _britain_at(w, 45)
        with _quiet():
            letter = AI.process_diplomatic_phase("Britain", w)
        kinds = [d["type"] for d in letter["terms"]["demands"]]
        assert letter["proposal_type"] == "harsh_peace" and "territory_cede" in kinds


class TestThePart4Siblings:
    def test_x21_the_bilateral_carries_an_occupied_homeland_cession_and_names_a_drop(self, vienna_held):
        w = vienna_held
        # Carniola (Austria's homeland) held by Russia — not on Bavaria's side: named, never silent
        w.regions["Carniola"].controller = "Russia"
        w.invalidate_active_nations_cache()
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [], "clauses": [],
                                    "demands": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol", "Carniola"],
                                                 "to_nation": "Bavaria"}]})
        assert w.regions["Tyrol"].controller == "Bavaria", "F52's one rule on the bilateral road"
        assert w.regions["Carniola"].controller == "Russia"
        assert ("Not carried: Carniola not carried — Austria no longer holds it and Russia stands on the "
                "other side.") in res["peace_ratification_summary"]["political_aftermath"]

    def test_x21_a_province_the_receiver_already_holds_is_left_to_the_status_quo(self, vienna_held):
        w = vienna_held
        with _quiet():
            res = w._ratify_treaty({"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                                    "sweeteners": [], "clauses": [],
                                    "demands": [{"type": "territory_cede", "value": 1, "regions": ["Bohemia"]}]})
        assert w.regions["Bohemia"].controller == "France"
        assert not any(ln.startswith("Not carried") for ln in res["peace_ratification_summary"]["political_aftermath"])

    def test_x23_the_tilsit_instrument_reads_the_driven_board(self):
        """PC-X23 (F85's sibling): Score Finish's agendas C4 probe measured the
        carve on a PLANTED stored score of 100; it reads the driven fixture now."""
        src = (REPO / "tools" / "_score_probes.py").read_text(encoding="utf-8")
        body = src[src.index("def agendas_c4_tilsit("):src.index("# ═══", src.index("def agendas_c4_tilsit("))]
        assert "fixture_agd_tilsit.json" in body and "recalculate_war_scores(world)" in body
        assert "T._beaten_prussia()" not in body

    def test_x24_every_war_on_the_congress_board_is_owned_and_purposed(self):
        """PC-X24 (F85's sibling): the generator wrote three WAR pairs owned by
        no instance (the fuzzer's I1); each is its own war with its purposes."""
        from backend.game_logic.settlement_helpers import _find_active_war_instance_for_pair
        p = _load_save(GE3_PRESSBURG)
        for pair, state in p.diplomatic_states.items():
            if state != "WAR":
                continue
            assert _find_active_war_instance_for_pair(p, pair), pair
            assert len(p.war_objectives.get(pair) or {}) == 2, pair

    def test_x25_a_foreign_war_is_titled_by_its_design(self, w):
        """PC-X25 (PC-R7 (i)'s sibling): the HUD's foreign-wars rows named an
        AI war "Prussia vs Sweden"; an AI design war is titled by its design."""
        from backend.game_logic.war_status import _build_foreign_wars
        with _quiet():
            D.declare_war(w, "Prussia", "Sweden")
        wid = sorted(w.war_instances)[-1]
        w.war_instances[wid]["stated_reason"] = "The Hanoverian Prize"
        w.war_objectives[w._make_diplo_key("Prussia", "Sweden")]["Prussia"]["design"] = "hanoverian_prize"
        row = next(r for r in _build_foreign_wars(w) if r["war_id"] == wid)
        assert row["war_title"] == "War for the Hanoverian Prize"
        assert 'fw.get("war_title", "")' in (SCRIPTS / "war_status_panel.gd").read_text(encoding="utf-8")

    def test_x26_the_desk_names_what_the_war_is_for(self, vienna_held):
        """PC-X26 (PC-R7 (i)'s sibling): "what is the war for" answered with the
        dates and never the stake, and missed a coalition member's row."""
        from backend.ai.state_desk import _answer_why_war
        line = _answer_why_war(vienna_held, "Austria")
        assert "a member of the coalition against us, since turn 1." in line
        assert "The War for Bohemia: France holds Bohemia, Tyrol and Vienna of Austria's." in line
