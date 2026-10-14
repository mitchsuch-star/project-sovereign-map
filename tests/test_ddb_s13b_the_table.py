"""Pre-Deploy S13b part 1, slice S13b-2 — DD-B's table P2s, DDB-4 … DDB-12
(October 14, 2026; `docs/BUG_FIXES.md` §DD-B; rules `SYSTEMS_REFERENCE.md`
§116).

  DDB-4   Counter is "Let Talleyrand haggle (1 DP)"; a dry run decides before
          any DP is charged — no counter, the offer stands and nothing is
          spent; a peace letter's war score is re-read whenever it is shown.
  DDB-5   the settlement review lists every province whose title the treaty
          fixes (the ratifier's own status-quo rule), the player's homeland
          first; the white peace says "each side keeps what it holds".
  DDB-6   a term France pays is never "a victory the field has not
          delivered": an Ease on a white peace raises the court's score.
  DDB-7   the counsel's recommended action and a running mission's Cancel
          stand first; a list taller than its pane says "▼ more below".
  DDB-8   the per-court separate peace reads the paradox: shut with "Bavaria
          is still at war with Austria"; the block text quotes the
          armistice's own likelihood.
  DDB-9   the generic menu's Propose peace arrives disabled under the
          paradox; the proposal popup renders `transient_error_display`.
  DDB-10  the Recall chip sends its order; the help and the Congress table
          name the Cabinet controls; the priced bid passes the door.
  DDB-11  the per-court chip shows the bilateral estimate it hands off.
  DDB-12  a co-belligerent's homeland retaken by an ally is titled back home.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import diplomacy as D
from backend.game_logic import game_end as GE
from backend.game_logic import settlement_scoring as SC
from backend.game_logic import settlement_staging as SS
from backend.game_logic import settlement_validation as SV
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


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


def _deliver(w, court: str, terms: dict, ptype: str = "peace") -> dict:
    from backend.game_logic.ai_diplomacy import _make_proposal, deliver_ai_proposal
    with contextlib.redirect_stdout(io.StringIO()):
        return deliver_ai_proposal(_make_proposal(court, ptype, 5, terms, w), w)


# ═══════════════════════════════════════════════════════════════════════════
# DDB-4 — Counter
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB4:
    _AUSTRIA = {"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                "demands": [{"type": "gold_lump", "value": 300}], "sweeteners": [], "clauses": []}
    _SPAIN = {"type": "peace", "proposer_nation": "Spain", "target_nation": "France",
              "demands": [{"type": "gold_lump", "value": 3000}], "sweeteners": [], "clauses": []}

    def test_the_button_says_what_it_does_and_may_cost(self, client):
        _c, w = client
        letter = _deliver(w, "Austria", dict(self._AUSTRIA))
        counter = next(o for o in letter["options"] if o["action"] == "counter_ai_proposal")
        assert counter["label"] == "Let Talleyrand haggle (1 DP)"
        assert counter["description"] == ("He sends a counter of his own choosing; if he "
                                          "finds none, nothing is spent and the offer stands")
        src = (SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        assert 'counter_btn.text = "Let Talleyrand haggle (1 DP)"' in src

    def test_no_counter_the_offer_stands_and_nothing_is_spent(self, client):
        c, w = client
        letter = _deliver(w, "Austria", dict(self._AUSTRIA))
        dp = w.diplomatic_points
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "counter_ai_proposal", "dialogue_id": letter["dialogue_id"]})
        assert out["success"] is False
        assert out["message"] == "Talleyrand finds no counter Austria could take — the offer stands."
        assert w.diplomatic_points == dp
        assert (w.pending_diplomatic_dialogue or {}).get("dialogue_id") == letter["dialogue_id"]
        assert out.get("incoming_proposal"), "the letter is re-mounted"

    def test_a_counter_found_is_charged_and_sent(self, client):
        c, w = client
        w.nation_dp["Spain"] = 5
        letter = _deliver(w, "Spain", dict(self._SPAIN))
        dp = w.diplomatic_points
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "counter_ai_proposal", "dialogue_id": letter["dialogue_id"]})
        assert out["success"] is True
        assert w.diplomatic_points == dp - 1
        assert (w.pending_diplomatic_dialogue or {}).get("type") == "counter_offer"

    def test_the_war_score_is_re_read_whenever_the_letter_is_shown(self, client):
        from backend.game_logic.treaty import refresh_letter_verdict
        _c, w = client
        letter = _deliver(w, "Austria", dict(self._AUSTRIA))
        before = letter["popup_payload"]["war_context_snapshot"]["war_score"]
        for region in ("Vienna", "Bohemia", "Moravia", "Tyrol"):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        payload = refresh_letter_verdict(w, letter)
        assert payload["war_context_snapshot"]["war_score"] > before


# ═══════════════════════════════════════════════════════════════════════════
# DDB-5 / DDB-12 — what the treaty titles
# ═══════════════════════════════════════════════════════════════════════════

def _vienna_and_franche_comte(w) -> None:
    w.regions["Vienna"].controller = "France"
    GE.record_province_title(w, "Vienna", GE.TITLE_CONQUEST, "Austria", "France")
    w.regions["Franche-Comte"].controller = "Bavaria"
    GE.record_province_title(w, "Franche-Comte", GE.TITLE_CONQUEST, "Austria", "Bavaria")
    w.invalidate_active_nations_cache()


class TestDDB5:
    def test_the_review_lists_what_the_treaty_titles_homeland_first(self, client):
        c, w = client
        _vienna_and_franche_comte(w)
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "propose common peace with Austria"})
        review = r["diplomatic_dialogue"]["status_quo_review"]
        assert review == [
            "Status quo: Franche-Comte returns to us by the treaty — homeland retaken by an ally.",
            "Status quo: Vienna stays ours by the treaty — titled.",
        ]

    def test_our_homeland_held_by_the_enemy_leads_the_list(self, client):
        c, w = client
        w.regions["Vienna"].controller = "France"
        GE.record_province_title(w, "Vienna", GE.TITLE_CONQUEST, "Austria", "France")
        w.regions["Franche-Comte"].controller = "Austria"
        GE.record_province_title(w, "Franche-Comte", GE.TITLE_CONQUEST, "France", "Austria")
        w.invalidate_active_nations_cache()
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "propose common peace with Austria"})
        review = r["diplomatic_dialogue"]["status_quo_review"]
        assert review[0].startswith("Franche-Comte stays with Austria by this peace"), review
        assert any("Vienna stays ours" in line for line in review)

    def test_the_white_peace_says_each_side_keeps_what_it_holds(self):
        from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
        from backend.game_logic.settlement_presentation import _term_display
        line = resolve_settlement_voice_line("settlement_white_peace_heading_talleyrand", war_label="X vs Y")
        assert "no map redrawn" not in line
        assert "each side keeps what it holds, now by treaty" in line
        assert _term_display({"type": "peace"}) == (
            "End hostilities — each side keeps what it holds, now by treaty")

    def test_a_consented_row_shows_no_score(self):
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert 'if _safe_str(row.get("band")) == "consented":' in src
        assert '"[b]What the treaty titles[/b]' in src


class TestDDB12:
    def test_an_allys_retaken_homeland_goes_home_at_the_signature(self, w):
        _vienna_and_franche_comte(w)
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "Bavaria", "Austria", "PEACE", "common_peace_settlement")
        assert w.regions["Franche-Comte"].controller == "France"
        assert "Franche-Comte" not in (w.province_title or {})
        (row,) = [e for e in w.event_log if e.get("type") == "province_returned"
                  and e.get("by") == "status_quo"]
        assert (row["nation"], row["target_nation"], row["region"]) == ("France", "Bavaria", "Franche-Comte")

    def test_the_home_nation_is_the_starting_homeland(self, w):
        assert GE.home_nation_of(w, "Franche-Comte") == "France"
        assert GE.home_nation_of(w, "Vienna") == "Austria"

    def test_a_conquest_from_a_neutral_courts_soil_stays_with_its_holder(self, w):
        hanoverian = sorted(w.nation_starting_regions["Hanover"])[0]
        w.regions[hanoverian].controller = "Bavaria"
        GE.record_province_title(w, hanoverian, GE.TITLE_CONQUEST, "Austria", "Bavaria")
        w.invalidate_active_nations_cache()
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "Bavaria", "Austria", "PEACE", "common_peace_settlement")
        assert w.regions[hanoverian].controller == "Bavaria"
        assert w.province_title[hanoverian]["kind"] == GE.TITLE_TREATY


# ═══════════════════════════════════════════════════════════════════════════
# DDB-6 — France's own gold is a concession, not a claim
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB6:
    def _score(self, w, terms):
        war_id = next(iter(w.get_war_instances_by_participant("Britain")))
        inst = w.war_instances[war_id]
        side = inst["side_by_nation"]["France"]
        acc = "defenders" if side == "attackers" else "attackers"
        return SC.calculate_common_peace_acceptance(
            w, war_id=war_id, war_instance=inst, proposer_side=side, accepting_side=acc,
            accepting_leader="Britain", covered_enemy_participants=["Britain"],
            settlement_terms=terms)

    def test_an_ease_on_a_white_peace_raises_the_score(self, w):
        white = self._score(w, [{"type": "peace"}])
        eased = self._score(w, [{"type": "peace"},
                                {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 100}])
        assert white["components"].get("settlement_tier_legitimacy") is not None
        assert eased["score"] > white["score"], (white["score"], eased["score"])
        tier = SC.calculate_settlement_tier_legitimacy(
            0, 0.0, [{"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 100}],
            proposer_side_participants=["France"])
        assert tier["tier"] == "white_peace" and tier["exceeded_ceiling"] is False

    def test_a_term_the_court_pays_still_claims_a_victory(self):
        tier = SC.calculate_settlement_tier_legitimacy(
            0, 0.0, [{"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 100}],
            proposer_side_participants=["France"])
        assert tier["exceeded_ceiling"] is True


# ═══════════════════════════════════════════════════════════════════════════
# DDB-7 — the counsel's row first, and the cue below the fold
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB7:
    def test_the_recommended_mission_and_a_running_cancel_stand_first(self):
        rows = [{"action": "propose_vassal", "display_name": "Propose Vassal"},
                {"action": "declare_war", "display_name": "Declare War"},
                {"action": "mission_improve_relations", "display_name": "Improve Relations"},
                {"action": "cancel_mission", "display_name": "Cancel: Court Nation"}]
        out = D.counsel_first([dict(r) for r in rows],
                              "Talleyrand recommends: Improve Relations mission", "IMPROVE_RELATIONS")
        assert [r["action"] for r in out[:2]] == ["cancel_mission", "mission_improve_relations"]
        assert all(r.get("counsel_first") for r in out[:2])
        named = D.counsel_first([dict(r) for r in rows[:2]],
                                "Talleyrand recommends: Propose Vassal", "")
        assert named[0]["action"] == "propose_vassal"

    def test_the_preview_puts_the_counsel_first(self, client):
        c, w = client
        preview = _get(c, "/diplomatic_preview?nation=Saxony")
        if preview.get("recommended_mission"):
            assert preview["actions"][0].get("counsel_first") is True

    def test_the_wizard_keeps_them_on_top_and_cues_the_fold(self):
        src = (SCRIPTS / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert 'bool(action.get("counsel_first", false))' in src
        assert "actions = counsel + others" in src
        assert '_more_below.text = "▼ more below"' in src
        assert '_more_below.theme_type_variation = &"Caption"' in src
        assert "Utils.COLOR_INFO" in src[src.index("_more_below = Label.new()"):][:600]


# ═══════════════════════════════════════════════════════════════════════════
# DDB-8 / DDB-9 — the paradox, before the click
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB8:
    def test_the_per_court_peace_is_shut_with_the_ally_named(self, w):
        war_id = next(iter(w.get_war_instances_by_participant("Austria")))
        chip = SS.separate_peace_chip(w, "Austria", war_id=war_id, staged_terms=[], actor="France")
        assert chip["available"] is False
        assert chip["disabled_reason_display"] == (
            "Bavaria is still at war with Austria — a separate peace would break her war.")
        elig = SV.evaluate_pair_peace_substitute_eligibility(
            w, war_id=war_id, actor_nation="France", target_nation="Austria",
            action="seek_bilateral_peace")
        assert elig["refusal_code"] == "commitment_paradox"
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert "Utils.set_available(btn, aff_available" in src

    def test_the_block_text_quotes_the_armistices_own_likelihood(self, client):
        c, w = client
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "Talleyrand, propose peace to Austria"})
        send = next(o for o in r["diplomatic_dialogue"]["options"] if o["action"] == "execute_proposal")
        likely, score = D.armistice_likelihood(w, "France", "Austria")
        assert send["available"] is False
        assert f"the court reads it {likely} ({score})" in send["unavailable_reason"]


class TestDDB9:
    def test_the_generic_menus_peace_is_disabled_with_its_reason(self, client):
        c, w = client
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "Talleyrand, propose to Austria"})
        d = r["diplomatic_dialogue"]
        assert d["type"] == "proposal_options"
        peace = next(o for o in d["options"] if o["action"] == "execute_proposal")
        assert peace["available"] is False
        assert "Bavaria (who is still at war with Austria)" in peace["disabled_reason_display"]
        assert "Propose an armistice instead" in peace["disabled_reason_display"]

    def test_the_popup_renders_the_transient_error(self):
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        body = src[src.index("func _build_content(data: Dictionary)"):]
        body = body[:body.index("\nfunc ")]
        assert 'data.get("transient_error_display")' in body


# ═══════════════════════════════════════════════════════════════════════════
# DDB-10 — the Cabinet's controls, named; the priced bid, typed
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB10:
    def test_the_recall_chip_sends_its_order(self):
        src = (SCRIPTS / "notification_bar.gd").read_text(encoding="utf-8")
        row = src[src.index("func _create_mission_row"):]
        row = row[:row.index("\nfunc ")]
        assert "notification_action_requested.emit(recall)" in row
        assert "suggest_command.emit(recall)" not in row

    def test_the_help_names_the_cabinet_controls(self):
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(encoding="utf-8")
        block = src[src.index("THE COMPACTS"):]
        block = block[:block.index("\n\n")]
        for control in ("F1 -> Prussia -> Buy Off Their Design",
                        "F1 -> Prussia -> Sponsor Their Design",
                        "F1 -> Saxony -> Guarantee Their Borders"):
            assert control in block, control
        assert '"buy off Prussia"' not in block

    def test_the_congress_names_the_buy_off_control(self, w):
        from backend.game_logic import congress
        src = (REPO / "backend" / "game_logic" / "congress.py").read_text(encoding="utf-8")
        assert '"command": f"buy off {court}\'s design"' not in src
        assert '→ Buy Off Their Design")' in src
        led = (SCRIPTS / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert ']In the Cabinet: " + "; ".join(PackedStringArray(controls))' in led
        assert '_cstr(lv, "control")' in led
        assert congress is not None

    def test_the_door_passes_the_priced_bid_and_names_the_control(self):
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        door = src[src.index("func _redirect_diplomatic_command"):]
        door = door[:door.index("\nfunc ")]
        assert "if _is_priced_bid(lower):" in door
        assert "_cabinet_control_for(lower)" in door
        assert '["buy off", "Buy Off Their Design"]' in src

    def test_the_bid_chips_say_a_larger_bid_is_typed(self, w):
        w.allegiance_auctions = {"Saxony": {"resolves_turn": 4, "bids": {}}}
        (row,) = D._bid_actions(w, "France", "Saxony")
        assert row["effect_text"].endswith("; a larger bid is typed: 'bid for Saxony, 500 gold'")
        src = (REPO / "backend" / "game_logic" / "ai_diplomacy.py").read_text(encoding="utf-8")
        assert "A larger bid is " in src and "typed: 'bid for {nation}, 500 gold'." in src


# ═══════════════════════════════════════════════════════════════════════════
# DDB-11 — the chip's own estimate
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB11:
    def test_the_chip_shows_the_bilateral_estimate_it_hands_off(self, w):
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "Bavaria", "Austria", "PEACE", "test_fixture")
        war_id = next(iter(w.get_war_instances_by_participant("Austria")))
        terms = [{"type": "peace"}, {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 300}]
        chip = SS.separate_peace_chip(w, "Austria", war_id=war_id, staged_terms=terms, actor="France")
        est = chip["bilateral_estimate"]
        seed = SS._pair_substitute_seed_terms(terms, target="Austria", proposer_leader="France")
        assert seed["demands"] == [{"type": "gold_lump", "value": 300}]
        score = D.calculate_acceptance({"type": "peace", "proposer_nation": "France",
                                        "target_nation": "Austria", "demands": seed["demands"],
                                        "sweeteners": [], "clauses": []}, w)["score"]
        assert est["score"] == int(score)
        assert chip["label"] == f"Separate peace with Austria — alone: {est['score']} ({est['band']})"
