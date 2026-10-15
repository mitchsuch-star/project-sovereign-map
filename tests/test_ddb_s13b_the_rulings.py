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

Part 2, slice 3's sweep (the field):

  DDB-X18  (found by DDB-42) the reckless auto-charge — the second combat
           copy — adds no alarm for a win on the charger's own soil.
  DDB-X19  (found by DDB-43) a treaty cession, and the auto-charge's mirrored
           conquest, between two other courts are dispatch lines too.
  DDB-X20  (found by DDB-42) a province a treaty cedes back to the court that
           held it in 1805, or holds its title, adds no `treaty_annex` alarm.
  DDB-X21  (found by DDB-19) the alternative a cautious objection offers reads
           the attack as the muster reckons it, as the objection does.
  DDB-X22  (found by DDB-17) the charge's banner follows the outcome; the
           resolver's charge line states the mechanic in no outcome's register.

Part 3 (October 15, 2026), its head:

  DDB-X17  (found by DDB-14) the player's glorious charge — typed, answered,
           or fired by an attack's reckless stage — reads the lead's rule
           before it rides: onto peace soil it is refused at no cost in the
           attack's own words, no popup first; the reckless auto-charge picks
           no target there. The AI keeps PT-F1.

Part 3, slice 2 — the rulings' builds (`DESIGN_REFINEMENT.md` §DD-B):

  DDB-R1   ASK FIRST: a typed attack on a marshal out of reach asks, at no
           cost, naming the pursuit's price and first march.
  DDB-R2   the muster gate arms on an unfavourable band for ANY lead (the
           sovereign never); Berthier names it; the commit draws once; the
           free preview is taught.
  DDB-R4   NO AUTO-END ON EITHER POOL: the mirror, WO-22's defer, the C3
           guard, the unread keys and the warning copy are retired.
  DDB-R5   a named marshal's mismatched arm is refused at no cost, naming
           both roads.
  DDB-R7   at a rich peace, the counsel and the dispatch name the law the
           chest can buy.

Part 3, slice 2's sweep:

  DDB-X23  (found by DDB-R2) the parked muster's live check reads the lead's
           reach, not adjacency.
  DDB-X24  (found by DDB-R1) the player's bare attack with nobody in reach
           asks before it marches.

Part 3, slice 3 — the garrison and the retreat:

  DDB-R3   a detachment assaulted at ≥ 4:1 effective odds capitulates whole
           (both boards, one arithmetic; a capital and a depot keep the cap);
           every collapse exit emits its garrison event.
  DDB-X1   a naval landing reads the attack's ONE garrison predicate.
  DDB-X2   the scout, assault and works-halt lines name the 500 floor, the
           4:1 capitulation and a capital's 5,000 line.
  DDB-R6   an engaged marshal's move onto an ally's province names the
           withdrawal and its price (the retreat's own friendly set).
  DDB-X3   the AI's retreat finder's first tier reads AAR-D4's friendly set
           (BASELINE_SERIES re-pinned, the row named).
  DDB-X25  (found by DDB-X2) the help's garrison entry names the thresholds.
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


# ═══════════════════════════════════════════════════════════════════════════
# Part 2, slice 3's sweep — the field
# ═══════════════════════════════════════════════════════════════════════════

def _auto_charge_at(w, where: str):
    import random
    murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
    murat.recklessness = 4
    mack.location, mack.strength = where, 3000
    for name in ("Soult", "Napoleon"):
        w.get_marshal(name).location = "Paris"
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    w.calculate_visibility()
    before = len(w.threat_sources_this_turn)
    random.seed(1)
    with contextlib.redirect_stdout(io.StringIO()):
        out = w._process_reckless_cavalry_turn_start()
    charge = next(r for r in out if r.get("type") == "auto_glorious_charge")
    return charge, [r for r in w.threat_sources_this_turn[before:] if r.get("target") == "France"]


class TestDDBX18:
    """Found by DDB-42: the reckless auto-charge's mirrored pipeline still
    alarmed Europe for a win on France's own soil."""

    def test_a_charge_won_on_our_own_soil_adds_no_alarm(self, w):
        charge, rows = _auto_charge_at(w, "Lorraine")
        assert charge["attacker_won"] is True
        assert w.get_region("Lorraine").controller == "France"
        assert not [r for r in rows if r.get("source") in ("battle_win", "decisive_victory")], rows

    def test_a_charge_won_on_an_allys_soil_still_alarms(self, w):
        charge, rows = _auto_charge_at(w, "Swabia")
        assert charge["attacker_won"] is True
        assert [r for r in rows if r.get("source") == "battle_win"], rows


def _war(w, a: str, b: str) -> None:
    key = w._make_diplo_key(a, b)
    w.diplomatic_states[key] = "WAR"
    w.war_start_turns[key] = int(w.current_turn)
    w.invalidate_bloc_members_cache()


class TestDDBX19:
    """Found by DDB-43: a province changing hands between two other courts by
    TREATY (and by the auto-charge's mirrored conquest) went unannounced."""

    def test_a_cession_between_other_courts_is_a_dispatch_line(self, w):
        _war(w, "Prussia", "Austria")
        before = len(w.pending_dispatch_events)
        with contextlib.redirect_stdout(io.StringIO()):
            result = w._ratify_treaty({
                "type": "peace", "proposer_nation": "Prussia", "target_nation": "Austria",
                "sweeteners": [], "demands": [{"type": "territory_cede", "regions": ["Bohemia"]}],
            })
        assert result is not None
        assert w.get_region("Bohemia").controller == "Prussia"
        changed = [e for e in w.pending_dispatch_events[before:]
                   if (e.get("event_type") or e.get("type")) == "province_changed_hands"]
        assert changed, w.pending_dispatch_events[before:]
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES as T
        line = T["province_changed_hands"].format(
            **changed[0].get("template_vars", changed[0].get("vars", {})))
        assert line == "Bohemia passes from Austria to Prussia."

    def test_the_mirrored_conquest_announces_too(self):
        import inspect
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState._process_reckless_cavalry_turn_start)
        assert "announce_third_party_capture(" in src


class TestDDBX20:
    """Found by DDB-42: a treaty handing a court back its own 1805 or titled
    province charged +8 `treaty_annex`, as for an annexation."""

    def _cede(self, w, region: str):
        _war(w, "France", "Prussia")
        before = len(w.threat_sources_this_turn)
        with contextlib.redirect_stdout(io.StringIO()):
            result = w._ratify_treaty({
                "type": "peace", "proposer_nation": "France", "target_nation": "Prussia",
                "sweeteners": [], "demands": [{"type": "territory_cede", "regions": [region]}],
            })
        assert result is not None
        assert w.get_region(region).controller == "France"
        return [r for r in w.threat_sources_this_turn[before:]
                if r.get("target") == "France" and r.get("source") == "treaty_annex"]

    def test_a_province_ceded_back_is_no_annexation(self, w):
        w.get_region("Lorraine").controller = "Prussia"  # France's own in 1805
        w.invalidate_active_nations_cache()
        assert self._cede(w, "Lorraine") == []

    def test_an_annexation_still_alarms(self, w):
        rows = self._cede(w, "Silesia")
        assert rows and int(rows[0]["amount"]) == 8, rows

    def test_the_seam(self):
        from backend.game_logic import game_end as GE
        from backend.models.world_state import cession_recovers_province
        assert cession_recovers_province({}, "France", "France")
        assert cession_recovers_province({"kind": GE.TITLE_TREATY, "holder": "France"}, "Austria", "France")
        assert not cession_recovers_province({}, "Austria", "France")


class TestDDBX21:
    """Found by DDB-19: the V1 objection's alternative (retreat / fortify /
    defend) still read one corps against one marshal."""

    def test_the_alternative_reads_the_musters_totals(self, w):
        from backend.commands.disobedience import DisobedienceSystem
        from backend.commands.objection_v2 import muster_expected_totals
        davout, mack = w.get_marshal("Davout"), w.get_marshal("Mack")
        totals = muster_expected_totals(davout, mack, w)
        assert totals is not None and totals[0] > davout.strength
        ratio = DisobedienceSystem()._get_strength_ratio_for_alternative(davout, "Mack", w)
        assert ratio == pytest.approx(totals[0] / totals[1])


class TestDDBX22:
    """Found by DDB-17: "a devastating cavalry assault" stood over a charge
    that was thrown back, and the resolver's charge line claimed
    "devastating damage" before the outcome."""

    def test_a_beaten_charge_is_not_called_devastating(self, client):
        import random
        c, w = client
        murat = w.get_marshal("Murat")
        murat.strength, murat.recklessness = 2000, 3
        w.calculate_visibility()
        random.seed(2)
        r = _post(c, "/command", {"command": "Murat, charge Mack"})
        assert r.get("success"), r.get("message")
        assert "GLORIOUS CHARGE! Murat leads the cavalry in!" in r["message"], r["message"]
        assert "devastating" not in r["message"].split("Murat's forces")[0], r["message"]

    def test_a_won_charge_keeps_its_banner(self, client):
        import random
        c, w = client
        murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
        murat.recklessness = 3
        mack.strength = 3000
        w.calculate_visibility()
        random.seed(2)
        r = _post(c, "/command", {"command": "Murat, charge Mack"})
        assert "GLORIOUS CHARGE! Murat leads a devastating cavalry assault!" in r["message"], r["message"]


# ═══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S13b part 3 — the head: DDB-X17
# ═══════════════════════════════════════════════════════════════════════════

def _murat_before_nassau(w, recklessness: int):
    """Murat on France's Rhineland; Mack across the frontier on Hesse's
    Nassau — a court France is at peace with."""
    murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
    murat.location, murat.recklessness = "Rhineland", recklessness
    mack.location, mack.strength = "Nassau", 3000
    w._build_marshal_index()
    w.invalidate_active_nations_cache()
    w.calculate_visibility()
    return murat, mack


class TestDDBX17:
    """Found by DDB-14's sweep: the glorious charge, and the reckless
    auto-charge, could still take the field on soil France is at peace
    with. The player's charge now reads the lead's rule before it rides."""

    _SAID = ("Murat cannot march on Mack: Nassau is Hesse's soil, and we are "
             "at peace with Hesse — no corps of ours may take the field there.")

    def test_a_typed_charge_onto_peace_soil_is_refused_at_no_cost(self, client):
        c, w = client
        murat, mack = _murat_before_nassau(w, 2)
        ap, square = w.actions_remaining, murat.square_formation
        r = _post(c, "/command", {"command": "Murat, charge Mack"})
        assert r.get("success") is False
        assert self._SAID in r["message"], r["message"]
        assert w.actions_remaining == ap and murat.recklessness == 2
        assert murat.location == "Rhineland" and mack.strength == 3000
        assert murat.square_formation == square
        assert w.pending_diplomatic_dialogue is None

    def test_the_charge_and_the_attack_say_one_thing(self, client):
        c, w = client
        _murat_before_nassau(w, 1)
        charge = _post(c, "/command", {"command": "Murat, charge Mack"})
        attack = _post(c, "/command", {"command": "Murat, attack Mack"})
        assert charge["message"] == attack["message"] == self._SAID

    def test_no_popup_and_no_objection_comes_first(self, client):
        """At recklessness 3 an ordered attack used to mount the CHARGE /
        RESTRAIN popup — both answers then refused. Pre-validated: neither
        the popup nor an objection is raised."""
        c, w = client
        murat, _ = _murat_before_nassau(w, 3)
        r = _post(c, "/command", {"command": "Murat, attack Mack"})
        assert r.get("success") is False and self._SAID in r["message"], r
        assert not r.get("pending_glorious_charge")
        assert murat.pending_glorious_charge is False
        assert not r.get("objection") and not r.get("awaiting_objection_response")
        assert w.pending_objection is None
        assert murat.recklessness == 3

    def test_no_redirect_offers_an_alternative_on_peace_soil(self):
        """The redirect popup's list skips an alternative standing on soil
        we are at peace with (the WO-25 board: Wellington on urban Paris,
        the only alternative on Prussia's Rhineland, France at peace with
        Prussia) — no popup; the attack goes in without the charge."""
        from backend.commands.executor import CommandExecutor
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.cavalry(name="Ney", location="Belgium",
                                     strength=40000, personality="aggressive")
        ney.recklessness = 3
        wel = MarshalFactory.enemy(name="Wellington", location="Paris",
                                   nation="Britain", strength=3000)
        alt = MarshalFactory.enemy(name="Uxbridge", location="Rhineland",
                                   nation="Britain", strength=2000)
        world = WorldFactory.with_marshals([ney, wel, alt])
        for a, b, st in (("France", "Britain", "WAR"), ("France", "Prussia", "PEACE")):
            world.diplomatic_states[world._make_diplo_key(a, b)] = st
        with contextlib.redirect_stdout(io.StringIO()):
            ex = CommandExecutor()
            res = ex.execute({"command": {"marshal": "Ney", "action": "attack",
                                          "target": "Wellington"}}, {"world": world})
        assert res.get("charge_redirected") is None, res.get("message")
        assert ney.pending_glorious_charge is False
        assert alt.strength == 2000

    def test_the_reckless_auto_charge_picks_no_target_on_peace_soil(self, w):
        murat, mack = _murat_before_nassau(w, 4)
        for m in w.marshals.values():
            if m.name != "Mack" and m.nation != "France" and w.is_at_war("France", m.nation):
                m.strength = 0
        with contextlib.redirect_stdout(io.StringIO()):
            out = w._process_reckless_cavalry_turn_start()
        mine = [e for e in out if e.get("marshal") == "Murat"]
        assert [e["type"] for e in mine] == ["reckless_no_target"], mine
        assert ("Mack stands on Nassau, Hesse's soil, and we are at peace "
                "with Hesse." in mine[0]["message"]), mine[0]["message"]
        assert murat.location == "Rhineland" and mack.strength == 3000
        assert w.get_region("Nassau").controller == "Hesse"

    def test_the_reckless_auto_charge_rides_for_an_open_field_instead(self, w):
        """The nearest foe on peace soil is passed over for the nearest on
        an open field (Swabia is Bavaria's, our ally's)."""
        import random
        murat, mack = _murat_before_nassau(w, 4)
        other = next(m for m in w.marshals.values()
                     if m.nation == "Austria" and m.name != "Mack" and m.strength > 0)
        other.location, other.strength = "Swabia", 2000
        w._build_marshal_index()
        random.seed(1)
        with contextlib.redirect_stdout(io.StringIO()):
            out = w._process_reckless_cavalry_turn_start()
        mine = [e for e in out if e.get("marshal") == "Murat"]
        assert [(e["type"], e.get("target")) for e in mine] == [
            ("auto_glorious_charge", other.name)], mine
        assert mack.strength == 3000

    def test_the_ai_keeps_pt_f1(self, w):
        """GR5's named difference: the AI's charge is never refused on a
        third party's soil, and its auto-charge picks such a target."""
        from backend.commands.combat_executor import charge_on_peace_soil
        from backend.models.world_state import reckless_charge_peace_owner
        mack = w.get_marshal("Mack")
        murat = w.get_marshal("Murat")
        murat.location = "Nassau"
        mack.location = "Swabia"
        w._build_marshal_index()
        assert reckless_charge_peace_owner(w, mack, murat) is None
        with contextlib.redirect_stdout(io.StringIO()):
            from backend.commands.executor import CommandExecutor
            ex = CommandExecutor()
        assert charge_on_peace_soil(ex._combat, mack, murat, w) is None

    def test_a_charge_on_his_own_field_is_no_march(self, w):
        """A charge on a foe in the marshal's own province does not cross a
        frontier: the lead's rule reads it as no march (DDB-14)."""
        from backend.models.world_state import reckless_charge_peace_owner
        murat, mack = _murat_before_nassau(w, 4)
        murat.location = "Nassau"
        assert reckless_charge_peace_owner(w, murat, mack) is None


# ═══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S13b part 3, slice 2 — the orders: DDB-R1, R2, R4, R5, R7
# ═══════════════════════════════════════════════════════════════════════════

def _kutuzov_three_marches_off(w):
    """Ney on Rhineland; Kutuzov seen at Bohemia, three marches off — the
    road's first march is Swabia, Bavaria's soil."""
    ney, kut = w.get_marshal("Ney"), w.get_marshal("Kutuzov")
    kut.location = "Bohemia"
    w.get_marshal("Mack").location = "Munich"
    w._build_marshal_index()
    w.calculate_visibility()
    return ney, kut


class TestDDBR1:
    """DDB-D1 — ASK FIRST: a typed attack on a marshal out of reach asks, at
    no cost, naming the pursuit's price and its first march."""

    _ASK = ("Kutuzov stands at Bohemia, three marches off. Pursue him (2 AP — a "
            "standing order; the first march takes Ney to Swabia, Bavaria's "
            "soil), or cancel?")

    def test_the_attack_asks_and_spends_nothing(self, client):
        c, w = client
        ney, _ = _kutuzov_three_marches_off(w)
        r = _post(c, "/command", {"command": "Ney, attack Kutuzov in Bohemia"})
        assert r.get("state") == "awaiting_clarification", r
        assert r["message"] == self._ASK, r["message"]
        assert w.actions_remaining == 4 and ney.strategic_order is None
        assert ney.location == "Rhineland"

    @pytest.mark.parametrize("answer", ["yes", "pursue", "Ney, attack Kutuzov"])
    def test_yes_pursues_with_npc_d4s_terms(self, client, answer):
        c, w = client
        ney, _ = _kutuzov_three_marches_off(w)
        _post(c, "/command", {"command": "Ney, attack Kutuzov in Bohemia"})
        r = _post(c, "/command", {"command": answer})
        assert r.get("success") is True, r.get("message")
        assert getattr(ney.strategic_order, "command_type", None) == "PURSUE"
        assert "A standing order, not a single attack" in r["message"], r["message"]
        assert ney.location == "Swabia" and w.actions_remaining == 2
        # The player's own words ride the order (NPC-11).
        assert ney.strategic_order.original_command == "Ney, attack Kutuzov in Bohemia"

    @pytest.mark.parametrize("answer", ["no", "cancel"])
    def test_no_spends_nothing(self, client, answer):
        c, w = client
        ney, _ = _kutuzov_three_marches_off(w)
        _post(c, "/command", {"command": "Ney, attack Kutuzov in Bohemia"})
        r = _post(c, "/command", {"command": answer})
        assert "the order is withdrawn" in r["message"]
        assert w.actions_remaining == 4 and ney.strategic_order is None
        assert ney.location == "Rhineland"

    def test_take_keeps_todays_upgrade(self, client):
        c, w = client
        ney, _ = _kutuzov_three_marches_off(w)
        r = _post(c, "/command", {"command": "Ney, take Kutuzov"})
        assert r.get("state") != "awaiting_clarification"
        assert getattr(ney.strategic_order, "command_type", None) == "PURSUE"

    def test_a_foe_across_the_first_march_is_named(self, client):
        c, w = client
        _kutuzov_three_marches_off(w)
        w.get_marshal("Mack").location = "Swabia"
        w._build_marshal_index()
        w.calculate_visibility()
        r = _post(c, "/command", {"command": "Ney, attack Kutuzov"})
        assert "the first march meets Mack at Swabia, Bavaria's soil" in r["message"], r

    def test_strategic_and_unordered_roads_never_ask(self, w):
        from types import SimpleNamespace
        from backend.commands.combat_executor import pursuit_ask
        ney, kut = _kutuzov_three_marches_off(w)
        for cmd in (None, {}, {"_raw_input": "x", "_pursuit_confirmed": True},
                    {"_raw_input": "x", "_strategic_execution": True},
                    {"_raw_input": "x", "_jealousy_autonomous": True},
                    {"_raw_input": "x", "_defiance": True},
                    {"_raw_input": "x", "_muster_confirmed": True}):
            ctx = SimpleNamespace(command=cmd, world=w, marshal=ney, enemy_by_name=kut)
            assert pursuit_ask(ctx, 2) is None, cmd

    def test_the_ai_never_reaches_it(self, w):
        """The range check's upgrade arm is the player's; an AI marshal out
        of reach is refused, never asked."""
        from backend.commands.executor import CommandExecutor
        with contextlib.redirect_stdout(io.StringIO()):
            ex = CommandExecutor()
            kut = w.get_marshal("Kutuzov")
            r = ex._combat._execute_attack(kut, "Ney", w, {"world": w},
                                           command={"_raw_input": "x"})
        assert r.get("state") != "awaiting_clarification"


def _ney_outmatched(w, personality="aggressive"):
    ney = w.get_marshal("Ney")
    for n in ("Davout", "Soult", "Lannes", "Murat", "Napoleon", "Massena", "Bernadotte"):
        w.get_marshal(n).location = "Paris"
    ney.location, ney.strength, ney.personality = "Rhineland", 8000, personality
    w._build_marshal_index()
    w.calculate_visibility()
    return ney


class TestDDBR2:
    """DDB-D2 — the muster gate widened to "potential disaster" for any
    personality; the free preview taught."""

    def test_a_non_cautious_lead_pauses_on_an_unfavourable_band(self, client):
        c, w = client
        _ney_outmatched(w)
        r = _post(c, "/command", {"command": "Ney, attack Mack"})
        assert r.get("requires_input") is True, r.get("message")
        assert (r.get("pending_interrupt") or {}).get("interrupt_type") == "muster_confirm"
        assert r["message"].startswith("Berthier stays the order a moment, Sire: "
                                       "before Ney marches on Mack, read the muster.")
        assert "The muster reads unfavorable." in r["message"]
        assert w.actions_remaining == 4

    def test_cancel_spends_nothing(self, client):
        c, w = client
        ney = _ney_outmatched(w)
        _post(c, "/command", {"command": "Ney, attack Mack"})
        r = _post(c, "/strategic_response", {"marshal_name": "Ney", "response_type": "muster_confirm", "choice": "cancel_order"})
        assert "stands down" in str(r.get("message")), r
        assert w.actions_remaining == 4 and ney.pending_interrupt is None

    def test_a_cautious_lead_still_halts_in_his_own_words(self, client, monkeypatch):
        """(His objection, which comes first, is held down: the voice of the
        pause is the subject.)"""
        from backend.commands import executor as EX
        monkeypatch.setattr(EX, "evaluate_situation",
                            lambda *a, **k: EX.ConcernLevel.NONE)
        c, w = client
        _ney_outmatched(w, personality="cautious")
        r = _post(c, "/command", {"command": "Ney, attack Mack"})
        assert r.get("requires_input") is True
        assert r["message"].startswith("Ney halts before the order is carried out.")

    def test_the_sovereign_never_pauses(self):
        from types import SimpleNamespace
        from backend.commands.combat_executor import player_muster_gate_arms
        assert player_muster_gate_arms(
            SimpleNamespace(personality="sovereign", is_sovereign=True), "unfavorable") is False
        assert player_muster_gate_arms(
            SimpleNamespace(personality="aggressive", is_sovereign=False), "unfavorable") is True
        assert player_muster_gate_arms(
            SimpleNamespace(personality="cautious", is_sovereign=False), "favorable") is False

    def test_the_ais_gate_constants_are_untouched(self):
        from backend.commands import objection_v2 as O
        assert O.MUSTER_GATE_BAND == "unfavorable"
        assert O.MUSTER_GATE_PERSONALITIES == frozenset({"cautious"})

    def test_a_committed_attack_draws_its_objection_once(self, client, monkeypatch):
        """The muster's Commit re-issues the attack exempt from a second
        objection draw (`_muster_confirmed`)."""
        from backend.commands import executor as EX
        c, w = client
        _ney_outmatched(w)
        _post(c, "/command", {"command": "Ney, attack Mack"})
        calls = []
        real = EX.evaluate_situation
        monkeypatch.setattr(EX, "evaluate_situation",
                            lambda *a, **k: calls.append(a[1]) or real(*a, **k))
        r = _post(c, "/strategic_response", {"marshal_name": "Ney", "response_type": "muster_confirm", "choice": "attack_anyway"})
        assert r.get("success") is True, r.get("message")
        assert not r.get("objection") and w.pending_objection is None
        assert not calls

    def test_every_muster_riding_a_result_teaches_the_preview(self, client):
        c, w = client
        _ney_outmatched(w)
        w.get_marshal("Ney").strength = 90000
        w.get_marshal("Mack").strength = 3000
        r = _post(c, "/command", {"command": "Ney, attack Mack"})
        assert r.get("success") is True and not r.get("requires_input"), r.get("message")
        assert ("Ask 'what if Ney attacks Mack' to read the muster before you "
                "commit — it costs nothing." in r["message"]), r["message"]

    def test_the_help_and_the_tutor_name_it(self, client):
        c, _w = client
        r = _post(c, "/command", {"command": "help"})
        assert '"what if Ney attacks Mack" - the MUSTER before you commit' in r["message"]
        card = (REPO / "godot-client" / "project-sovereign" / "scripts"
                / "tutorial_overlay.gd").read_text(encoding="utf-8")
        assert "what if Ney attacks Mack[/color] and Berthier reads it for nothing" in card


class TestDDBR4:
    """DDB-D4 — NO AUTO-END ON EITHER POOL."""

    def test_the_last_military_action_leaves_the_turn(self, client):
        c, w = client
        w.actions_remaining, w.admin_actions_remaining = 1, 0
        r = _post(c, "/command", {"command": "Davout, defend"})
        assert r.get("success") is True
        assert w.current_turn == 1
        assert "the last order the day could take" in r["message"]
        assert (r.get("action_info") or {}).get("turn_advanced") is False
        r = _post(c, "/command", {"command": "end turn"})
        assert w.current_turn == 2

    def test_the_last_admin_action_leaves_the_turn_too(self, client):
        c, w = client
        w.actions_remaining, w.admin_actions_remaining = 0, 1
        r = _post(c, "/command", {"command": "recruit for Davout"})
        assert r.get("success") is True, r.get("message")
        assert w.current_turn == 1
        assert "the last order the day could take" in r["message"]

    def test_the_retired_machinery_is_gone(self):
        from backend.commands.executor import CommandExecutor
        assert not hasattr(CommandExecutor, "_auto_end_turn_defer_notice")
        src = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
        assert "should_end_turn" not in src
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert "const AUTO_END_WARNING" not in gd and "AUTO_END_WAITS_WARNING :=" not in gd
        assert 'const DAY_SPENT_BUTTON_TEXT := "End Turn (E) ▸"' in gd

    def test_old_saves_load(self, w):
        data = json.loads(json.dumps(w.to_dict(), default=str))
        data["auto_advanced_to_turn"] = 3
        back = WorldState.from_dict(data)
        assert back._auto_advanced_to_turn == 3
        assert back.to_dict()["auto_advanced_to_turn"] == 3


class TestDDBR5:
    """DDB-D5 — REFUSE AT NO COST, NAMING BOTH ROADS."""

    def test_a_mismatched_arm_spends_nothing_and_names_both_roads(self, client):
        c, w = client
        davout = w.get_marshal("Davout")
        gold, admin = w.gold, w.admin_actions_remaining
        pool = dict(getattr(w, "manpower_pools", {}) or {})
        strength = davout.strength
        r = _post(c, "/command", {"command": "recruit artillery for Davout"})
        assert r.get("success") is False
        assert r["message"] == (
            "Davout commands infantry — 'Davout, recruit' raises foot for him; "
            "guns are raised by an artillery corps — commission Marmont (4,500g). "
            "Nothing was spent."), r["message"]
        assert (w.gold, w.admin_actions_remaining, davout.strength) == (gold, admin, strength)
        assert dict(getattr(w, "manpower_pools", {}) or {}) == pool

    def test_the_nearest_commander_of_the_arm_is_named(self, client):
        c, _w = client
        r = _post(c, "/command", {"command": "recruit cavalry for Davout"})
        assert r["message"] == (
            "Davout commands infantry — 'Davout, recruit' raises foot for him; "
            "horse are raised by a cavalry corps — 'Murat, recruit' raises them "
            "at Franche-Comte. Nothing was spent."), r["message"]

    def test_his_own_arm_still_levies(self, client):
        c, w = client
        gold = w.gold
        r = _post(c, "/command", {"command": "recruit infantry for Davout"})
        assert r.get("success") is True, r.get("message")
        assert w.gold < gold


def _at_peace(w, gold: int) -> None:
    for key, state in list(w.diplomatic_states.items()):
        if "France" in key.split("|") and state in ("WAR", "ARMISTICE"):
            w.diplomatic_states[key] = "PEACE"
    w.invalidate_active_nations_cache()
    w.invalidate_bloc_members_cache()
    w.gold = gold


class TestDDBR7:
    """DDB-D7 — KEEP THE RICH PEACE, SURFACE ITS SINK."""

    def test_at_a_rich_peace_both_surfaces_name_the_law(self, client):
        from backend.game_logic.dispatch import build_morning_dispatch
        c, w = client
        _at_peace(w, 31889)
        with contextlib.redirect_stdout(io.StringIO()):
            situation = build_morning_dispatch(w, []).get("situation") or {}
        assert situation.get("law_sink") == (
            "the chest could found the Grand Quartier Général — 9,000g")
        r = _post(c, "/command", {"command": "what can I do"})
        assert "enact the Staff — 9,000g" in r["message"], r["message"]

    def test_the_counsel_names_it_where_the_purse_test_holds_back(self, w, monkeypatch):
        from backend.ai import counsel
        from backend.game_logic import reforms as R
        _at_peace(w, 31889)
        monkeypatch.setattr(R, "ai_purse_refusal", lambda *a, **k: "held back")
        lines = counsel.economy_counsel(w, "France")
        assert lines and lines[0].startswith("enact the Staff — 9,000g"), lines

    def test_nothing_at_war_or_when_nothing_is_affordable(self, w):
        from backend.ai import counsel
        from backend.game_logic import reforms as R
        w.gold = 31889
        assert R.peace_sink_line(w, "France") == ""          # the 1805 boot is at war
        assert counsel._peace_sink_terms(w, "France") is None
        _at_peace(w, 2000)
        assert R.peace_sink_line(w, "France") == ""
        _at_peace(w, 31889)
        key = w._make_diplo_key("France", "Austria")
        w.diplomatic_states[key] = "ARMISTICE"
        assert R.peace_sink_line(w, "France") == ""
        assert R.peace_sink_law(w, "Austria") is None


# ═══════════════════════════════════════════════════════════════════════════
# Part 3, slice 2's sweep — the orders
# ═══════════════════════════════════════════════════════════════════════════

class TestDDBX23:
    """Found by DDB-R2's sweep: the parked muster's live check read
    adjacency, not the lead's reach — a cavalryman's committed attack two
    provinces off was retired as "marched away" from a muster that had not
    moved, and the attack never went in."""

    def test_a_committed_charge_two_provinces_off_goes_in(self, client):
        c, w = client
        murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
        for n in ("Davout", "Soult", "Lannes", "Ney", "Napoleon", "Massena", "Bernadotte"):
            w.get_marshal(n).location = "Paris"
        murat.location, murat.strength = "Lorraine", 6000
        mack.location = "Franconia"
        w._build_marshal_index()
        w.calculate_visibility()
        assert w.get_distance("Lorraine", "Franconia") == 2 == murat.movement_range
        r = _post(c, "/command", {"command": "Murat, attack Mack"})
        assert (r.get("pending_interrupt") or {}).get("interrupt_type") == "muster_confirm"
        strength = mack.strength
        r = _post(c, "/strategic_response", {"marshal_name": "Murat",
                                             "response_type": "muster_confirm",
                                             "choice": "attack_anyway"})
        assert r.get("success") is True and not r.get("decision_retired"), r.get("message")
        assert mack.strength < strength

    def test_beyond_his_reach_it_is_still_retired(self, w):
        from backend.commands.strategic import muster_is_live
        murat, mack = w.get_marshal("Murat"), w.get_marshal("Mack")
        murat.location, mack.location = "Lorraine", "Bohemia"
        w._build_marshal_index()
        w.calculate_visibility()
        live, reason = muster_is_live(murat, w, {"interrupt_type": "muster_confirm",
                                                 "target": "Mack"})
        assert live is False and "Mack" in reason


class TestDDBX24:
    """Found by DDB-R1's sweep: the player's bare "attack" with nobody in
    reach marched a non-literal marshal a step at once — R1's class. It
    asks first, in R1's words."""

    def test_a_bare_attack_out_of_reach_asks(self, client):
        c, w = client
        ney, kut = w.get_marshal("Ney"), w.get_marshal("Kutuzov")
        for m in w.marshals.values():
            if m.nation != "France" and w.is_at_war("France", m.nation) and m.name != "Kutuzov":
                m.location = "Podolia"
        kut.location = "Bohemia"
        w._build_marshal_index()
        w.calculate_visibility()
        r = _post(c, "/command", {"command": "Ney, attack"})
        assert r.get("state") == "awaiting_clarification", r.get("message")
        assert r["message"].startswith("Kutuzov stands at Bohemia, three marches off.")
        assert ney.location == "Rhineland" and w.actions_remaining == 4
        r = _post(c, "/command", {"command": "yes"})
        assert getattr(ney.strategic_order, "command_type", None) == "PURSUE", r.get("message")

    def test_without_the_pursuits_price_the_step_stands(self, client):
        """An ask whose every answer must fail is never asked: with one
        action left the pursuit cannot be paid, and the step is taken."""
        c, w = client
        ney, kut = w.get_marshal("Ney"), w.get_marshal("Kutuzov")
        for m in w.marshals.values():
            if m.nation != "France" and w.is_at_war("France", m.nation) and m.name != "Kutuzov":
                m.location = "Podolia"
        kut.location = "Bohemia"
        w._build_marshal_index()
        w.calculate_visibility()
        w.actions_remaining = 1
        r = _post(c, "/command", {"command": "Ney, attack"})
        assert r.get("state") != "awaiting_clarification"
        assert "moving toward Kutuzov" in str(r.get("message")), r.get("message")


# ═══════════════════════════════════════════════════════════════════════════
# Part 3, slice 3 — the garrison and the retreat: DDB-R3, X1, X2, R6, X3
# ═══════════════════════════════════════════════════════════════════════════

def _tyrol_detachment(w, ney_strength: int, garrison: int = 3000):
    """The conquest #18 shape on the 1805 boot: a 3,000 Austrian detachment
    on Tyrol, Ney beside it at Munich."""
    ney, tyrol = w.get_marshal("Ney"), w.get_region("Tyrol")
    for m in w.marshals.values():
        if m.location == "Tyrol" and m.nation != "France":
            m.location = "Vienna"
    ney.location, ney.strength = "Munich", ney_strength
    tyrol.garrison_strength, tyrol.garrison_detachment = garrison, True
    w._build_marshal_index()
    w.calculate_visibility()
    return ney, tyrol


def _exchange(w, region, attacker_effective, garrison_effective):
    from backend.commands.executor import CommandExecutor
    with contextlib.redirect_stdout(io.StringIO()):
        combat = CommandExecutor()._combat
    return combat.garrison_exchange(40000, attacker_effective,
                                    int(region.garrison_strength),
                                    garrison_effective, region=region)


class TestDDBR3:
    """DDB-D3 — BUILD FA-D28'S OPEN HALF FOR DETACHMENTS: at ≥ 4:1 effective
    odds an assault takes a detachment whole."""

    def test_a_detachment_at_four_to_one_falls_in_one_assault(self, client):
        c, w = client
        ney, tyrol = _tyrol_detachment(w, 19000)
        r = _post(c, "/command", {"command": "Ney, attack Tyrol"})
        assert r.get("success") is True, r.get("message")
        assert tyrol.garrison_strength == 0 and tyrol.controller == "France"
        assert "The detachment capitulates to odds of 4:1 or better (3,000 -> 0)." in r["message"]
        events = {e["type"]: e for e in r.get("events") or []}
        assert events["garrison_destroyed"]["capitulated"] is True
        assert "conquest" in events          # the seam fix: both events ride

    def test_at_two_to_one_it_loses_the_capped_half(self, client):
        c, w = client
        _ney, tyrol = _tyrol_detachment(w, 6000)
        r = _post(c, "/command", {"command": "Ney, attack Tyrol"})
        assert tyrol.garrison_strength == 1500 and tyrol.controller == "Austria", r.get("message")

    def test_a_capital_and_a_depot_keep_the_cap(self, w):
        vienna, flanders = w.get_region("Vienna"), w.get_region("Flanders")
        for region in (vienna, flanders):
            assert not region.garrison_detachment
            garrison = int(region.garrison_strength)
            _att, lost = _exchange(w, region, 5 * garrison, garrison)
            assert lost == int(garrison * 0.50), (region.name, lost)

    def test_one_arithmetic_for_both_boards(self, w):
        """The desk's forecast and the AI's assault read the same exchange."""
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import garrison_report as GR
        ney, tyrol = _tyrol_detachment(w, 19000)
        forecast = GR.assault_forecast(w, ney, tyrol)
        assert forecast["breaks"] and forecast["remaining"] == 0
        # The AI's side: Austria storms a French detachment at the same odds.
        lorraine = w.get_region("Lorraine")
        for m in w.marshals.values():
            if m.location == "Lorraine":
                m.location = "Paris"
        lorraine.garrison_strength, lorraine.garrison_detachment = 2000, True
        mack = w.get_marshal("Mack")
        mack.location, mack.strength = "Rhineland", 60000
        w._build_marshal_index()
        with contextlib.redirect_stdout(io.StringIO()):
            ex = CommandExecutor()
            r = ex._combat._resolve_garrison_combat(mack, lorraine, w, {"world": w})
        assert lorraine.garrison_strength == 0, r.get("message")
        assert any(e.get("type") == "garrison_destroyed" for e in r.get("events") or [])


class TestDDBX1:
    """Found while ruling: a naval landing re-implemented "garrison fights"
    without SR-7a's 500-man floor — it now reads the attack's ONE predicate."""

    def test_the_landing_reads_the_one_predicate(self, w):
        from backend.commands.naval_executor import landing_garrison_fights
        from backend.game_logic.garrison_report import garrison_fights
        munster = w.get_region("Munster")
        for strength, detach in ((400, True), (600, True), (6000, False), (4000, False)):
            munster.garrison_strength, munster.garrison_detachment = strength, detach
            assert landing_garrison_fights(munster, "France") is garrison_fights(munster), strength
        munster.garrison_strength, munster.garrison_detachment = 400, True
        assert landing_garrison_fights(munster, "France") is False
        assert landing_garrison_fights(munster, munster.controller) is False

    def test_a_landing_on_a_detachment_under_500_takes_its_surrender(self, w, monkeypatch):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import naval
        munster = w.get_region("Munster")
        for m in w.marshals.values():
            if m.location == "Munster" and m.nation != "France":
                m.location = "London"
        munster.garrison_strength, munster.garrison_detachment = 400, True
        bern = w.get_marshal("Bernadotte")
        bern.strength = 12000
        bern.location = naval.controlled_dockyards(w, "France")[0]
        w._build_marshal_index()
        monkeypatch.setattr(naval, "resolve_expedition",
                            lambda world, marshal, target: {"landed": True, "coverer": None,
                                                            "odds": 100})
        with contextlib.redirect_stdout(io.StringIO()):
            ex = CommandExecutor()
            r = ex._naval._execute_naval_expedition(
                {"action": "naval_expedition", "marshal": "Bernadotte",
                 "target": "Munster", "confirmed": True}, {"world": w})
        assert r.get("success") is True, r.get("message")
        assert "The detachment of 400 at Munster lays down its arms." in r["message"], r["message"]
        assert "assaults the Munster garrison" not in r["message"]
        assert munster.garrison_strength == 0


class TestDDBX2:
    """Found while ruling: the garrison copy said a detachment "fights to the
    last man" though under 500 it lays down its arms; the lines now name the
    500 floor, the 4:1 capitulation and a capital's 5,000 line."""

    def test_the_scout_line_names_the_thresholds(self, w):
        from backend.game_logic.garrison_report import describe_garrison
        _ney, tyrol = _tyrol_detachment(w, 19000)
        line = describe_garrison(w, tyrol, "France")
        assert "lays down its arms below 500" in line, line
        assert "capitulates whole to a storm at 4:1 odds" in line, line
        assert "last man" not in line
        vienna = describe_garrison(w, w.get_region("Vienna"), "France")
        assert "it breaks below 5,000" in vienna, vienna

    def test_the_assault_line_names_them(self, w):
        from backend.game_logic import garrison_report as GR
        ney, tyrol = _tyrol_detachment(w, 6000)
        f = GR.assault_forecast(w, ney, tyrol)
        line = GR.assault_muster_line(w, ney, tyrol, f["attacker_effective"],
                                      f["garrison_effective"], f["coordination"])
        assert "it would capitulate whole at 4:1" in line, line
        assert "lays down its arms below 500" in line and "last man" not in line

    def test_the_works_halt_line_names_them(self, w):
        from backend.commands.combat_executor import works_halt_line
        ney, tyrol = _tyrol_detachment(w, 6000)
        line = works_halt_line(w, ney, tyrol)
        assert "capitulates whole to a storm at 4:1" in line, line
        assert "lays down its arms below 500" in line and "last man" not in line
        vienna = w.get_region("Vienna")
        assert "it breaks below 5,000" in works_halt_line(w, ney, vienna)


def _davout_engaged_beside_swabia(w):
    """diplomacy-first #16: Davout engaged at Lorraine, Swabia (Bavaria's,
    our ally) beside him."""
    davout, mack = w.get_marshal("Davout"), w.get_marshal("Mack")
    davout.location, mack.location = "Lorraine", "Lorraine"
    w._build_marshal_index()
    w.calculate_visibility()
    return davout


class TestDDBR6:
    """DDB-D6 — KEEP THE RULE, FIX THE SENTENCE."""

    def test_a_move_onto_an_allys_province_names_the_withdrawal(self, client):
        from backend.commands.movement_executor import retreat_initial_penalty_pct
        c, w = client
        davout = _davout_engaged_beside_swabia(w)
        assert w.get_region("Swabia").controller == "Bavaria"
        pct = retreat_initial_penalty_pct(davout)
        r = _post(c, "/command", {"command": "Davout, move to Swabia"})
        assert r.get("success") is False
        assert r["message"].startswith(
            f"Davout is engaged with Mack at Lorraine: a march cannot carry him "
            f"off the field. He may withdraw onto Swabia — 'Davout, retreat to "
            f"Swabia' (free, −{pct}% effectiveness, once a turn) — or fight."), r["message"]
        assert "Cannot advance" not in r["message"]
        assert davout.location == "Lorraine" and w.actions_remaining == 4

    def test_the_named_order_works_at_the_price_named(self, client):
        from backend.commands.movement_executor import retreat_initial_penalty_pct
        c, w = client
        davout = _davout_engaged_beside_swabia(w)
        pct = retreat_initial_penalty_pct(davout)
        r = _post(c, "/command", {"command": "Davout, retreat to Swabia"})
        assert r.get("success") is True, r.get("message")
        assert davout.location == "Swabia"
        assert f"-{pct}%" in r["message"], r["message"]

    def test_the_friendly_list_is_the_retreats_own(self, w):
        from backend.commands.movement_executor import MovementExecutor
        davout = _davout_engaged_beside_swabia(w)
        refusal = MovementExecutor.move_refusal_probe(
            w, davout, w.get_region("Bohemia"), "Bohemia")
        friendly = set(refusal["retreat_options"])
        for name in w.get_region("Lorraine").adjacent_regions:
            region = w.get_region(name)
            expected = (w.retreat_soil_is_friendly("France", region.controller)
                        and not any(m.nation != "France" and m.strength > 0
                                    and w.is_at_war("France", m.nation)
                                    for m in w.get_marshals_in_region(name)))
            assert (name in friendly) == expected, name
        assert "Swabia" in friendly
        assert refusal["message"].startswith("Cannot advance while engaged with Mack")

    def test_once_a_turn_is_said(self, w):
        from backend.commands.movement_executor import MovementExecutor
        davout = _davout_engaged_beside_swabia(w)
        davout.retreated_this_turn = True
        refusal = MovementExecutor.move_refusal_probe(
            w, davout, w.get_region("Swabia"), "Swabia")
        assert "already fallen back once this turn" in refusal["message"]


class TestDDBX3:
    """Found while ruling: the AI's retreat finder's first tier read own soil
    only — it reads AAR-D4's friendly set, as the player's retreat does."""

    def test_the_ai_falls_back_onto_an_allys_province(self, w):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        kut = w.get_marshal("Kutuzov")
        # Kutuzov on Bohemia (Austria's, an ally of Russia): the only own or
        # allied neighbour is the ally's.
        kut.location = "Bohemia"
        w._build_marshal_index()
        with contextlib.redirect_stdout(io.StringIO()):
            ai = EnemyAI(CommandExecutor())
        dest = ai._find_retreat_destination(kut, "Russia", w)
        assert dest is not None
        assert w.retreat_soil_is_friendly("Russia", w.get_region(dest).controller), dest

    def test_the_seam_reads_the_one_set(self, w):
        from backend.ai.enemy_ai import ai_retreat_soil_is_friendly
        for controller in ("Russia", "Austria", "Britain", "France", "Bavaria", None):
            assert (ai_retreat_soil_is_friendly(w, "Russia", controller)
                    == w.retreat_soil_is_friendly("Russia", controller)), controller


class TestDDBX25:
    """Found by DDB-X2's sweep: the help's garrison entry said a detachment
    "Fights to destruction." — it names the floor and the 4:1 too."""

    def test_the_help_names_the_thresholds(self, client):
        c, _w = client
        r = _post(c, "/command", {"command": "help"})
        assert "Fights to destruction" not in r["message"]
        assert "it lays down its arms below 500, and" in r["message"]
        assert "capitulates whole to an assault at 4:1 odds." in r["message"]
