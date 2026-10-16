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

Part 2, slice S13b-2 (October 15, 2026) — the table's P3s:

  DDB-22  the harsher dial reads "Demand more of <court>".
  DDB-23  every stream names its term; a generous armistice lists the truce first.
  DDB-24  a war's sides are named by court; a court's white peace says it
          settles the whole war, beside the per-court road.
  DDB-25  "What terms would they accept?" opens the terms with their acceptance;
          the strength line says who outmatches whom.
  DDB-26  the band promises a counter only when one can be built; the preview
          is titled by its treaty, the treaty first, its mechanics above the score.
  DDB-27  the assessment reads the war score live; the battlefield line is gated.
  DDB-28  the review's petition line grants or declines on the staged draft.
  DDB-29  a court that leaves the war leaves no draft naming it.
  DDB-30  "Less generous" restores exactly the previous round.
  DDB-31  the buy-off chip names the design that wakes next and its price.
  DDB-32  the Treaties book lists the 1805 alliances as what they are.
  DDB-33  Ease stops at the scorer's gold ceiling and says so; a client
          state's provinces count as promised.
  DDB-34  the auction's dispatch line names the Cabinet chip; the advice offers the bid.
  DDB-35  Propose Peace stands in the WAR state, behind the paradox.
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
    def test_the_per_court_peace_is_open_with_the_ally_named(self, w):
        # PC-R1 (S13e part 1, §46 B + C): the paradox no longer shuts the
        # chip — the leader's peace carries Bavaria's pair, and the chip
        # says so in the one wording.
        war_id = next(iter(w.get_war_instances_by_participant("Austria")))
        chip = SS.separate_peace_chip(w, "Austria", war_id=war_id, staged_terms=[], actor="France")
        assert chip.get("available", True) is not False
        assert chip["separate_peace_display"] == (
            "Bavaria's war with Austria ends in this instrument; she takes nothing by it.")
        elig = SV.evaluate_pair_peace_substitute_eligibility(
            w, war_id=war_id, actor_nation="France", target_nation="Austria",
            action="seek_bilateral_peace")
        assert elig["eligible"] is True
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert "Utils.set_available(btn, aff_available" in src

    def test_the_drafts_note_says_the_peace_carries_bavaria(self, client):
        # PC-R1: the block (and the armistice it sold) is retired; the Send
        # arm stays live and the draft carries the one note.
        c, w = client
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "Talleyrand, propose peace to Austria"})
        d = r["diplomatic_dialogue"]
        send = next(o for o in d["options"] if o["action"] == "execute_proposal")
        assert send.get("available", True) is not False
        assert d["separate_peace_note"] == (
            "Mark one thing, Sire: Bavaria's war with Austria ends in this instrument; "
            "she takes nothing by it.")
        assert "commitment_block_warning" not in d


class TestDDB9:
    def test_the_generic_menus_peace_is_stamped_by_the_one_verdict(self, client):
        # PC-R1: the paradox no longer refuses, so the menu's Propose peace
        # is open on the boot; the stamp (`_stamp_menu_sends`) still closes
        # a send the verdict refuses — here, a peace the purse cannot pay.
        c, w = client
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "Talleyrand, propose to Austria"})
        d = r["diplomatic_dialogue"]
        assert d["type"] == "proposal_options"
        peace = next(o for o in d["options"] if o["action"] == "execute_proposal")
        assert peace.get("available", True) is not False
        from backend.game_logic import diplomatic_dialogue as DD
        assert "_stamp_menu_sends" in __import__("inspect").getsource(DD)

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


# ═══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S13b part 2, slice 2 — the table's P3s, DDB-22 … DDB-35
# ═══════════════════════════════════════════════════════════════════════════

def _respond(c, choice, w, **params) -> dict:
    body = {"choice": choice,
            "dialogue_id": (w.pending_diplomatic_dialogue or {}).get("dialogue_id")}
    if params:
        body["action_params"] = params
    return _post(c, "/respond_to_diplomatic_dialogue", body)


class TestDDB22:
    def test_the_harsher_dial_says_demand_more(self, client):
        c, w = client
        w.diplomatic_points = 9
        d = _post(c, "/command", {"command": "propose common peace with Austria"})["diplomatic_dialogue"]
        assert d["dialogue_mode"] == "PROPOSE"
        labels = {row["nation"]: [a["label"] for a in row.get("dial_actions") or []]
                  for row in d["per_court_acceptance"]}
        assert "Demand more of Austria" in labels["Austria"]
        assert not any(lab.startswith("Press ") for labs in labels.values() for lab in labs)


class TestDDB23:
    def test_every_stream_names_its_term(self):
        from backend.display_names import format_terms_for_display, stream_term_phrase
        from backend.game_logic.diplomatic_templates import annotate_peace_terms
        assert stream_term_phrase({"type": "gold_per_turn", "value": 50}) == " for as long as the treaty stands"
        assert stream_term_phrase({"type": "gold_per_turn", "amount": 50, "turns": 5}) == " for 5 turns"
        assert stream_term_phrase({"type": "gold_lump", "value": 50}) == ""
        terms = {"type": "vassalage", "sweeteners": [{"type": "ap_per_turn", "value": 1}],
                 "demands": [], "clauses": []}
        assert "France concedes 1 AP/turn for as long as the treaty stands" in format_terms_for_display(
            terms, "vassalage", "Bavaria")
        (row,) = annotate_peace_terms(terms, "France", "Bavaria")
        assert row["display_label"] == "France cedes 1 AP per turn to Bavaria for as long as the treaty stands"

    def test_a_generous_round_on_an_armistice_keeps_the_armistice_first(self, client):
        c, w = client
        w.diplomatic_points = 9
        d = _post(c, "/command", {"command": "Talleyrand, propose armistice to Austria"})["diplomatic_dialogue"]
        r = _respond(c, "modify_generous", w)
        rows = [t["display_label"] for t in r["diplomatic_dialogue"]["war_context_snapshot"]["annotated_terms"]]
        assert rows[0].startswith("Armistice (cease hostilities temporarily)"), rows
        assert any("per turn to Austria for as long as the treaty stands" in t for t in rows[1:]), rows
        assert d["war_context_snapshot"]["annotated_terms"][0]["type"] == "treaty"


class TestDDB24:
    def test_the_sides_are_named_by_court(self, w):
        from backend.game_logic.settlement_presentation import side_court_label
        assert side_court_label(w, ["France", "Bavaria", "Spain"]) == "France"
        assert side_court_label(w, ["Austria", "Britain", "Russia"]) == "The Third Coalition"
        w.active_coalition = None
        assert side_court_label(w, ["Austria", "Britain"], leader="Britain") == "Britain"
        src = (REPO / "backend" / "game_logic" / "settlement_presentation.py").read_text(encoding="utf-8")
        assert '"side_label": side_label_display(side)' not in src

    def test_a_white_peace_from_a_court_s_page_says_it_settles_the_whole_war(self, client):
        c, w = client
        w.diplomatic_points = 9
        r = _post(c, "/command", {"command": "Talleyrand, propose white peace with Austria",
                                  "action": "propose_white_peace", "target_nation": "Austria"})
        d = r["diplomatic_dialogue"]
        assert d["scope_note"] == ("This white peace settles the whole war — with Austria, Britain "
                                   "and Russia. To settle with Austria alone, choose "
                                   "'Make peace with Austria only'.")
        assert d["talleyrand_text"].startswith(d["scope_note"])
        assert "Make peace with Austria only" in [o["label"] for o in d["options"]]


class TestDDB25:
    def test_the_button_opens_the_terms_with_their_acceptance(self, client):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        c, w = client
        adv = _post(c, "/command", {"command": "Talleyrand, what about Austria?"})["diplomatic_dialogue"]
        opt = next(o for o in adv["options"] if o["label"] == "What terms would they accept?")
        assert opt["action"] == "assess_terms"
        card = _respond(c, "assess_terms", w)["diplomatic_dialogue"]
        assert card["type"] == "feasibility"
        draft = generate_suggested_terms("Austria", "peace", w, deterministic=True)
        send = next(o for o in card["options"] if o["action"] == "execute_proposal")
        assert send["label"] == "Propose these terms"
        assert send["terms"]["demands"] == list(draft.get("demands") or [])
        assert card["talleyrand_text"].startswith("Sire, the terms I would draft: ")
        assert card["context"]["suggested_terms"]
        score = D.calculate_acceptance({"type": draft.get("type") or "peace", "proposer_nation": "France",
                                        "target_nation": "Austria",
                                        "sweeteners": list(draft.get("sweeteners") or []),
                                        "demands": list(draft.get("demands") or []),
                                        "clauses": list(draft.get("clauses") or [])}, w)["score"]
        assert card["context"]["acceptance_score"] == int(score)

    def test_the_strength_line_names_its_direction(self):
        from backend.game_logic.diplomatic_advisory import strength_sentence
        assert strength_sentence("overmatched") == "In the field we outmatch them decisively."
        assert strength_sentence("superior") == "In the field they outmatch us."
        src = (REPO / "backend" / "game_logic" / "diplomatic_advisory.py").read_text(encoding="utf-8")
        assert 'f"Their military strength is {advantage} relative to ours. "' not in src


class TestDDB26:
    def test_the_band_promises_a_counter_only_when_one_is_constructible(self):
        assert D.get_likelihood_descriptor(35) == "Doubtful — may counter"
        assert D.get_likelihood_descriptor(35, False) == "Doubtful"
        assert D.get_likelihood_descriptor(45, False) == "Uncertain"
        assert D.get_likelihood_descriptor(45, True) == "Uncertain — a counter is likely"

    def test_the_preview_is_titled_by_its_treaty_and_lists_it_first(self, client):
        c, w = client
        w.diplomatic_points = 9
        d = _post(c, "/command", {"command": "Talleyrand, propose armistice to Austria"})["diplomatic_dialogue"]
        snap = d["war_context_snapshot"]
        assert snap["preview_title"] == "ARMISTICE PREVIEW"
        assert snap["annotated_terms"][0]["display_label"] == (
            "Armistice (cease hostilities temporarily) — France and Austria")
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        body = src[src.index("func _build_peace_preview_content"):]
        body = body[:body.index("\nfunc ")]
        assert 'snapshot.get("preview_title", "PEACE PREVIEW")' in body
        assert body.index("[b]Armistice Terms[/b]") < body.index("[b]Acceptance Estimate[/b]")


class TestDDB27:
    def test_the_assessment_reads_the_battles_since_the_last_end_turn(self, w):
        before = D.get_assessment_text(w, "Austria")
        for region in ("Vienna", "Bohemia", "Moravia", "Tyrol"):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        assert D.get_war_score_for(w, "France", "Austria") <= 20, "the stored score is stale"
        after = D.get_assessment_text(w, "Austria")
        assert after != before
        assert D.live_war_score_for(w, "France", "Austria") > 20

    def test_the_battlefield_line_is_gated_on_the_score(self, w):
        for region in ("Vienna", "Bohemia", "Moravia", "Tyrol"):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        text, _ = D._base_recommendation_and_mission(w, "Austria", [], 3, False, {})
        assert "A battlefield victory would change their calculus" not in text


class TestDDB28:
    def test_the_review_s_petition_line_grants_on_the_staged_draft(self, client):
        c, w = client
        w.diplomatic_points = 9
        munich = next(r for r in sorted(w.nation_starting_regions["Bavaria"])
                      if r != w.get_nation_capital("Bavaria")) if len(
            w.nation_starting_regions["Bavaria"]) > 1 else sorted(w.nation_starting_regions["Bavaria"])[0]
        w.regions[munich].controller = "Austria"
        w.invalidate_active_nations_cache()
        d = _post(c, "/command", {"command": "propose common peace with Austria"})["diplomatic_dialogue"]
        petitions = d.get("ally_petitions") or []
        assert petitions and petitions[0]["ally_nation"] == "Bavaria", petitions
        key = petitions[0]["petition_key"]
        r = _respond(c, "settlement_answer_petition", w, nation="Bavaria", petition_key=key, answer="grant")
        assert r["success"] is True, r.get("message")
        staged = r["diplomatic_dialogue"]
        assert staged["type"] == "settlement_confirm"
        assert any(t.get("type") == "territory_cede" and t.get("region") == munich
                   and t.get("to") == "Bavaria" for t in staged["settlement_terms"]), staged["settlement_terms"]

    def test_decline_answers_on_the_table_and_the_line_carries_both(self, client):
        c, w = client
        w.diplomatic_points = 9
        home = sorted(w.nation_starting_regions["Bavaria"])
        w.regions[home[-1]].controller = "Austria"
        w.invalidate_active_nations_cache()
        d = _post(c, "/command", {"command": "propose common peace with Austria"})["diplomatic_dialogue"]
        key = d["ally_petitions"][0]["petition_key"]
        r = _respond(c, "settlement_answer_petition", w, nation="Bavaria", petition_key=key, answer="decline")
        assert r["success"] is True, r.get("message")
        assert not [q for q in w.dialogue_manager.iter_queue() if q.get("type") == "ally_settlement_petition"]
        assert r["diplomatic_dialogue"]["type"] == "settlement_confirm"
        assert not r["diplomatic_dialogue"].get("ally_petitions")
        src = (SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        assert "[url=petition:%d:grant]" in src and "[url=petition:%d:decline]" in src
        assert '"settlement_answer_petition"' in (SCRIPTS / "main.gd").read_text(encoding="utf-8")


class TestDDB29:
    def test_a_court_leaving_the_war_leaves_no_draft_naming_it(self, w):
        war_id = next(iter(w.get_war_instances_by_participant("Austria")))
        SS.save_scoped_settlement_draft(w, war_id=war_id, selected_target_nation="Austria",
                                        covered_enemy_participants=["Austria", "Britain", "Russia"],
                                        settlement_terms=[{"type": "peace"}])
        SS.save_scoped_settlement_draft(w, war_id=war_id, selected_target_nation="Britain",
                                        covered_enemy_participants=["Britain"],
                                        settlement_terms=[{"type": "peace"}])
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "France", "Austria", "PEACE", "common_peace_settlement")
        selected = {k.split(":")[2] for k in w.pending_settlement_drafts_by_key}
        assert selected == {"Britain"}


class TestDDB30:
    def test_less_generous_restores_exactly_the_previous_round(self, client):
        c, w = client
        w.diplomatic_points = 9
        first = _post(c, "/command", {"command": "Talleyrand, propose armistice to Austria"})["diplomatic_dialogue"]
        assert "less_generous" not in [o["action"] for o in first["options"]]
        r1 = _respond(c, "modify_generous", w)["diplomatic_dialogue"]
        r2 = _respond(c, "modify_generous", w)["diplomatic_dialogue"]
        assert "less_generous" in [o["action"] for o in r2["options"]]
        back = _respond(c, "less_generous", w)["diplomatic_dialogue"]
        assert back["proposal_terms_summary"] == r1["proposal_terms_summary"]
        assert [o["label"] for o in back["options"]] == [o["label"] for o in r1["options"]]
        home = _respond(c, "less_generous", w)["diplomatic_dialogue"]
        assert home["proposal_terms_summary"] == first["proposal_terms_summary"]


class TestDDB31:
    def test_the_buy_off_chip_names_the_design_that_wakes_next(self, w):
        from backend.game_logic.instruments import next_design_after_buyoff
        relations = dict(w.nation_relations)
        bargains = list(getattr(w, "compensation_bargains", []) or [])
        nxt = next_design_after_buyoff(w, "France", "Prussia")
        assert nxt and nxt["title"] and nxt["price"] > 0
        assert dict(w.nation_relations) == relations
        assert list(getattr(w, "compensation_bargains", []) or []) == bargains
        acts = D.get_available_diplomatic_actions(w, "Prussia")
        acts = acts.get("actions") if isinstance(acts, dict) else acts
        chip = next(a for a in acts if a["action"] == "buy_off_design")
        text = str(chip.get("effect_text") or chip.get("description") or "")
        assert f"Buying it wakes {nxt['title']} next ({nxt['price']}g to buy off in turn)." in text


class TestDDB32:
    def test_the_treaties_book_lists_the_1805_alliances(self, w):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        rows = {(t["nation_b"], t.get("note")) for t in build_diplomatic_ledger(w)["treaties"]
                if t.get("inherited")}
        assert ("Bavaria", "an alliance of 1805, not a treaty of ours") in rows
        assert ("Spain", "an alliance of 1805, not a treaty of ours") in rows
        src = (SCRIPTS / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'bool(t.get("inherited", false))' in src


class TestDDB33:
    def test_ease_stops_at_the_scorer_s_gold_ceiling_and_says_so(self):
        notes: list = []
        terms = [{"type": "peace"},
                 {"type": "gold_indemnity", "from": "France", "to": "Britain", "amount": 950}]
        out = SS._redial_settlement_terms(terms=terms, scope_courts=["Britain"], direction="generous",
                                          proposer_side_leader="France", protected_notes=notes)
        gold = next(t for t in out if t["type"] == "gold_indemnity")
        assert gold["amount"] == 1000
        again = SS._redial_settlement_terms(terms=out, scope_courts=["Britain"], direction="generous",
                                            proposer_side_leader="France", protected_notes=notes)
        assert next(t for t in again if t["type"] == "gold_indemnity")["amount"] == 1000
        assert "Gold past 1,000 buys nothing more from Britain at this table, Sire." in notes

    def test_a_client_state_s_provinces_count_as_promised(self):
        from backend.game_logic.settlement_baseline import _promised_regions_in_terms
        promised = _promised_regions_in_terms([
            {"type": "create_client", "from": "Britain", "to": "France", "provinces": ["Ulster", "Leinster"]},
            {"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}])
        assert promised == {"Ulster", "Leinster", "Tyrol"}


class TestDDB34:
    def test_the_dispatch_line_names_the_cabinet_chip(self):
        from backend.game_logic import dispatch
        text = dispatch._format_dispatch_event_text("allegiance_in_play", {"nation": "Sardinia"})
        assert text.endswith("Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.")

    def test_the_advice_menu_offers_the_bid_while_the_auction_is_open(self, client):
        c, w = client
        w.allegiance_auctions = {"Sardinia": {"resolves_turn": int(w.current_turn) + 3, "bids": {}}}
        w.diplomatic_points = 9
        d = _post(c, "/command", {"command": "Talleyrand, propose to Sardinia"})["diplomatic_dialogue"]
        bid = next(o for o in d["options"] if o["action"] == "execute_suggestion")
        assert bid["label"].startswith("Bid for their allegiance (")
        dp, gold = w.diplomatic_points, w.nation_gold["France"]
        r = _respond(c, "execute_suggestion", w)
        assert r["success"] is True, r.get("message")
        assert w.diplomatic_points == dp - 1 and w.nation_gold["France"] < gold
        assert w.allegiance_auctions["Sardinia"]["bids"].get("France")


class TestDDB35:
    def test_propose_peace_stands_in_a_one_on_one_war(self, w):
        with contextlib.redirect_stdout(io.StringIO()):
            for ally in ("Bavaria", "Spain", "Holland", "KingdomOfItaly"):
                if w.get_diplomatic_state(ally, "Austria") == "WAR":
                    D.set_diplomatic_state(w, ally, "Austria", "PEACE", "test_fixture")
        acts = D.get_available_diplomatic_actions(w, "Austria")
        acts = acts.get("actions") if isinstance(acts, dict) else acts
        row = next(a for a in acts if a["action"] == "propose_peace")
        assert row["display_name"] == "Propose Peace" and row["available"] is True, row

    def test_an_ally_still_at_war_rides_the_row_as_a_note(self, w):
        # PC-R1 (S13e part 1): the row stays open; the one verdict's note
        # says the leader's peace carries Bavaria's pair.
        acts = D.get_available_diplomatic_actions(w, "Austria")
        acts = acts.get("actions") if isinstance(acts, dict) else acts
        row = next(a for a in acts if a["action"] == "propose_peace")
        assert row["available"] is True
        assert row["separate_peace_display"] == (
            "Bavaria's war with Austria ends in this instrument; she takes nothing by it.")
        from backend.display_names import settlement_disabled_reason_display
        assert "Propose Peace or Propose Armistice" in settlement_disabled_reason_display("one_to_one_war")
