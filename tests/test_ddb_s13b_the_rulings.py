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

Part 2 (October 15, 2026), its head:

  DDB-X9   a court's settlement offer lists who keeps what in the ratifier's
           own words (`status_quo_forecast_lines` per covered pair), as the
           review does — one reading on one board.
  DDB-X11  one demand-side reading at x0.65: the war-age maximum scales with
           the credit (30 -> 65); the AI's send filter is re-read at the
           shipped weight, so a beaten court's honest letter is sent.
  DDB-X12  (found by DDB-X9) a court's bilateral peace letter names what each
           side keeps, as France's own preview does.

Part 2, slice 2's sweep (the table's P3s):

  DDB-X13  (found by DDB-30) a harsher round steps back too ("Milder terms").
  DDB-X14  (found by DDB-27) the advice quotes the war score live.
  DDB-X15  (found by DDB-25) the overview and the war-room counsel say who
           outmatches whom.
  DDB-X16  (found by DDB-26) the armistice quote and the per-court chip promise
           a counter only when the generator can build one.
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


# ═══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S13b part 2 — the found rows at its head
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client(monkeypatch):
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _post(client, path: str, body: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post(path, json=body).json()


def _get(client, path: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.get(path).json()


def _sea_18(w) -> None:
    """The sea #18 board: France holds Vienna, Bavaria has retaken
    Franche-Comte from Austria."""
    from backend.game_logic import game_end as GE
    w.regions["Vienna"].controller = "France"
    GE.record_province_title(w, "Vienna", GE.TITLE_CONQUEST, "Austria", "France")
    w.regions["Franche-Comte"].controller = "Bavaria"
    GE.record_province_title(w, "Franche-Comte", GE.TITLE_CONQUEST, "Austria", "Bavaria")
    w.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X9 — the letter's status quo is the ratifier's
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX9:
    _SAID = [
        "Status quo: Franche-Comte returns to us by the treaty — homeland retaken by an ally.",
        "Status quo: Vienna stays ours by the treaty — titled.",
    ]

    @staticmethod
    def _offer(w, seq: int = 1) -> dict:
        war_id = next(wid for wid, inst in w.war_instances.items()
                      if isinstance(inst, dict) and inst.get("ended_turn") is None
                      and {"France", "Austria"} <= set(inst.get("side_by_nation") or {}))
        side = w.war_instances[war_id]["side_by_nation"]
        return {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": f"settlement_offer:{war_id}:{w.current_turn}:{seq}",
            "war_id": war_id,
            "proposer_nation": "Austria",
            "proposer_side": side["Austria"],
            "accepting_side": side["France"],
            "accepting_leader": "France",
            "covered_enemy_participants": ["Austria"],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(w.current_turn),
        }

    @staticmethod
    def _status(letter: dict) -> list:
        return [s for s in letter["terms_summary"]
                if s.startswith("Status quo:") or "closed frontier" in s]

    def test_the_letter_and_the_review_say_the_same_thing(self, client):
        from backend.game_logic.settlement_offers import promote_pending_settlement_offers
        c, w = client
        _sea_18(w)
        offer = self._offer(w)
        w.pending_settlement_dialogues = [offer]
        with contextlib.redirect_stdout(io.StringIO()):
            promote_pending_settlement_offers(w)
        box = _get(c, "/mailbox")
        item = next(i for i in box["items"] if i.get("source_nation") == "Austria"
                    and i.get("item_type") == "incoming_settlement_offer")
        shown = _post(c, "/mailbox/activate", {"mailbox_id": item["mailbox_id"]})
        letter = shown["incoming_settlement_offer"]
        assert self._status(letter) == self._SAID, letter["terms_summary"]
        review = _post(c, "/respond_to_diplomatic_dialogue", {
            "choice": "accept_settlement_offer",
            "dialogue_id": (w.pending_diplomatic_dialogue or {}).get("dialogue_id")})
        assert review["diplomatic_dialogue"]["status_quo_review"] == self._SAID

    def test_a_conquest_outside_a_homeland_is_listed(self, w):
        from backend.game_logic import game_end as GE
        from backend.game_logic.settlement_offers import build_incoming_settlement_offer_popup
        hanoverian = sorted(w.nation_starting_regions["Hanover"])[0]
        w.regions[hanoverian].controller = "France"
        GE.record_province_title(w, hanoverian, GE.TITLE_CONQUEST, "Austria", "France")
        w.invalidate_active_nations_cache()
        letter = build_incoming_settlement_offer_popup(w, self._offer(w))
        assert f"Status quo: {hanoverian} stays ours by the treaty — titled." in self._status(letter)

    def test_the_package_s_own_carve_is_left_out(self, w):
        from backend.game_logic.settlement_offers import build_incoming_settlement_offer_popup
        _sea_18(w)
        offer = self._offer(w)
        offer["settlement_terms"] = [{"type": "peace"}, {
            "type": "territory_cede", "from": "France", "to": "Austria", "region": "Vienna"}]
        status = self._status(build_incoming_settlement_offer_popup(w, offer))
        assert not any("Vienna" in s for s in status), status
        assert any("Franche-Comte returns to us" in s for s in status)


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X12 (found by DDB-X9) — a court's peace letter names what each keeps
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX12:
    _AUSTRIA = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                "demands": [{"type": "gold_lump", "value": 300}], "sweeteners": [], "clauses": []}

    def test_the_letter_lists_the_status_quo_as_the_preview_does(self, client):
        from backend.game_logic.ai_diplomacy import _make_proposal, deliver_ai_proposal
        from backend.game_logic.treaty import refresh_letter_verdict
        _c, w = client
        _sea_18(w)
        with contextlib.redirect_stdout(io.StringIO()):
            letter = deliver_ai_proposal(_make_proposal("Austria", "peace", 5, dict(self._AUSTRIA), w), w)
        payload = letter["popup_payload"]
        # A bilateral peace resolves France and Austria alone: Bavaria's
        # retaken Franche-Comte is her own war's, so only Vienna is said.
        said = ["Status quo: Vienna stays ours by the treaty — titled."]
        assert payload["status_quo_forecast"]["lines"] == said
        rows = [t["display_label"] for t in payload["war_context_snapshot"]["annotated_terms"]
                if t.get("type") == "status_quo"] or [
                    s for s in payload.get("clauses") or [] if s.startswith("Status quo:")]
        assert rows == said
        # Re-read at every show, never said twice.
        again = refresh_letter_verdict(w, letter)
        rows_again = [t["display_label"] for t in again["war_context_snapshot"]["annotated_terms"]
                      if t.get("type") == "status_quo"] or [
                          s for s in again.get("clauses") or [] if s.startswith("Status quo:")]
        assert rows_again == said


# ═══════════════════════════════════════════════════════════════════════════
# DDB-X11 — one demand-side reading at x0.65
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX11:
    def test_the_war_age_maximum_scales_with_the_credit(self):
        assert D.WAR_AGE_PENALTY_MAX == round(30 * SC.BASE_SIDE_PRESSURE_SCALE / 0.3) == 65
        assert D.war_age_acceptance_mod(0, extracts_value=True) == -65
        assert D.war_age_acceptance_mod(0, extracts_value=False) == 0

    def test_a_two_turn_war_at_plus_thirty_recommends_no_extraction(self, w):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        from tests.test_ca9_row1_war_age_penalty import _at_war
        assert D.bilateral_war_score_weight() == 0.65
        _at_war(w, age=1, war_score=30)
        assert not (generate_suggested_terms("Prussia", "peace", w).get("demands") or [])
        _at_war(w, age=D.WAR_AGE_PENALTY_WINDOW + 1, war_score=30)
        assert generate_suggested_terms("Prussia", "peace", w).get("demands")

    @staticmethod
    def _beaten_prussia(war_score: int):
        from tests import test_da1_ai_intelligence as DA
        world = DA.make_world()
        DA._clear_opening_bloc(world)
        DA.set_war(world, "France", "Prussia")
        DA.set_diplomat_personality(world, "Prussia", "hawk")
        DA.set_relation(world, "France", "Prussia", 20)
        world.war_exhaustion["Prussia"] = 60
        DA.set_war_score(world, "Prussia", "France", war_score)
        return world

    def test_a_beaten_court_s_honest_letter_is_sent(self):
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        world = self._beaten_prussia(-58)
        with contextlib.redirect_stdout(io.StringIO()):
            letter = process_diplomatic_phase("Prussia", world)
        assert letter is not None
        terms = letter["terms"]
        assert terms["type"] == "armistice_losing" and not terms["demands"]
        # The player reads it at its honest x0.65 score.
        assert D.calculate_acceptance(terms, world)["score"] < 20

    def test_the_floor_falls_by_exactly_the_extra_steepness(self):
        from backend.game_logic.ai_diplomacy import _send_floor
        world = self._beaten_prussia(-58)
        honest = {"proposal_type": "armistice_losing",
                  "terms": {"type": "armistice_losing", "target_nation": "France",
                            "sweeteners": [], "demands": []}}
        assert _send_floor(honest, world, "Prussia") == 20 - round(0.35 * 58)
        asks = {"proposal_type": "peace",
                "terms": {"type": "peace", "target_nation": "France",
                          "demands": [{"type": "gold_lump", "value": 100}]}}
        assert _send_floor(asks, world, "Prussia") == 20


# ═══════════════════════════════════════════════════════════════════════════
# Part 2, slice 2's sweep — the siblings the table's P3s found
# ═══════════════════════════════════════════════════════════════════════════

def _respond(c, choice, w, **params) -> dict:
    body = {"choice": choice,
            "dialogue_id": (w.pending_diplomatic_dialogue or {}).get("dialogue_id")}
    if params:
        body["action_params"] = params
    return _post(c, "/respond_to_diplomatic_dialogue", body)


class TestDDBX13:
    """Found by DDB-30: a harsher round could not be stepped back either."""

    def test_less_harsh_restores_the_previous_round(self, client):
        c, w = client
        w.diplomatic_points = 9
        first = _post(c, "/command", {"command": "Talleyrand, propose armistice to Austria"})["diplomatic_dialogue"]
        harsh = _respond(c, "modify_harsh", w)["diplomatic_dialogue"]
        assert "Milder terms" in [o["label"] for o in harsh["options"]]
        back = _respond(c, "less_generous", w)["diplomatic_dialogue"]
        assert back["proposal_terms_summary"] == first["proposal_terms_summary"]
        assert [o["label"] for o in back["options"]] == [o["label"] for o in first["options"]]


class TestDDBX14:
    """Found by DDB-27: the advice quoted the STORED war score."""

    def test_the_advice_quotes_the_live_score(self, client):
        c, w = client
        for region in ("Vienna", "Bohemia", "Moravia", "Tyrol"):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        live = D.live_war_score_for(w, "France", "Austria")
        assert live != D.get_war_score_for(w, "France", "Austria")
        adv = _post(c, "/command", {"command": "Talleyrand, what about Austria?"})["diplomatic_dialogue"]
        assert f"War score stands at {live} from our perspective." in adv["talleyrand_text"]


class TestDDBX15:
    """Found by DDB-25: the overview and the war-room counsel used the ladder
    word too ("Military: overmatched", "Their overmatched military position")."""

    def test_every_strength_line_names_its_direction(self, w):
        from backend.game_logic import diplomatic_advisory as DA
        src = (REPO / "backend" / "game_logic" / "diplomatic_advisory.py").read_text(encoding="utf-8")
        assert 'f"Military: {advantage}' not in src
        assert "Their {advantage} military position" not in src
        overview = DA._diplomatic_overview(w)
        text = str(overview.get("talleyrand_text") or overview)
        assert "In the field" in text


class TestDDBX16:
    """Found by DDB-26: the armistice quote and the per-court chip promised a
    counter by score band alone."""

    def test_one_counter_aware_band_for_every_reader(self, w, monkeypatch):
        from backend.game_logic import ai_diplomacy as AI
        monkeypatch.setattr(AI, "generate_counter_offer", lambda *a, **k: None)
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                    "sweeteners": [], "demands": [], "clauses": []}
        assert D.counter_aware_likelihood(w, proposal, 35) == "Doubtful"
        assert D.counter_aware_likelihood(w, proposal, 60) == "Favorable"
        src = (REPO / "backend" / "game_logic" / "settlement_staging.py").read_text(encoding="utf-8")
        assert '"band": counter_aware_likelihood(world, proposal, score)' in src
        dsrc = (REPO / "backend" / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        assert "return counter_aware_likelihood(world, proposal, score), score" in dsrc
