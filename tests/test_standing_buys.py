"""AU-3a "the three buys" (docs/AUTHORITY_CURRENCY_SPEC.md §5.3, the landing
record §6.5): authority the Emperor spends on purpose — "Decree it" on the
three Edict letters, "By my word" on an objection (both roads), "Honour him"
on the confrontation card and "By decree" on the rivalry card. One price
rule: a price lands whole or its button is closed with the reason
(`standing.refusal`, the grip's 60); each buy raises the next by one for the
turn and the five before it, at most three (`standing.push_price`). The seam
is `standing.buys_armed` (arm AUY); the courts' own Decree is parked with the
courts' flip (AU-14, `standing.courts_move`).
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.commands import vindication as V
from backend.game_logic import affairs as AF
from backend.game_logic import jealousy as J
from backend.game_logic import moments as MO
from backend.game_logic import standing as ST
from backend.models.world_state import MAX_CAVALRY_POOL
from tests import _chip_census as C
from tests.test_action_cost_honesty import _board, _order, _post  # noqa: F401
from tests.test_ach_f_rows import _MACK_BEYOND_THE_MUSTER

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"
E1, E2, E3 = "the_magazines", "the_remounts", "camps_of_instruction"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    w = M.world
    w.moments = MO.from_block(json.loads(FIXTURE.read_text(encoding="utf-8")))
    for e in MO.deck(w):
        w.moments["state"][str(e["id"])] = {"status": "passed", "turn": 1, "reason": "premise"}
    w.__dict__.pop("_affairs_memo", None)
    return w


@pytest.fixture
def client(monkeypatch):
    return _board(monkeypatch)


def _remounts_board(w, gold=6_000, authority=90):
    """E2 standing: every corps home, the horse at 59 % of its establishment."""
    w.nation_gold["France"] = int(gold)
    w.marshals["Bernadotte"].location = "Lorraine"
    w.manpower_pools["France"]["cavalry"] = int(MAX_CAVALRY_POOL) * 59 // 100
    w.authority_tracker.authority = int(authority)
    w.__dict__.pop("_affairs_memo", None)
    occ = {"id": f"{E2}#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7}
    w.moments["state"][f"{E2}#1"] = dict(occ, status="fired")
    return MO.entry(w, E2), occ


# ═══════════════════════════════════════════════════════════════════════════
# The spine
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSpine:
    def test_the_seam_is_armed_and_held_down_on_its_arm(self):
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert ST.buys_armed() is True
        assert STANDING_SEAMS_BY_ROW["AUY"] == ["backend.game_logic.standing:buys_armed=False"]
        assert AF.row_armed("AU-3a") is True and "AU-3a" in AF.SINCE_ROWS
        rig = (REPO / "tools" / "_standing_series_arms.py").read_text(encoding="utf-8")
        assert "bought_word_given" in rig and "court_decrees_in_authority" in rig

    def test_the_recency_rise_window_and_cap(self, world):
        tracker = world.authority_tracker
        world.current_turn = 10
        assert ST.push_price(world, "France", 4) == 4
        tracker.held["pushes"] = [5, 6]                      # 10 − 5 = 5: inside the window of six
        assert ST.push_price(world, "France", 4) == 6
        tracker.held["pushes"] = [4]                          # 10 − 4 = 6: out of it
        assert ST.push_price(world, "France", 4) == 4
        tracker.held["pushes"] = [9, 9, 10, 10, 10]
        assert ST.push_price(world, "France", 4) == 4 + ST.PUSH_RISE_MAX

    def test_a_buy_books_its_turn_only_when_it_lands(self, world):
        world.current_turn = 3
        world.authority_tracker.authority = 90
        out = ST.buy(world, "France", 4, "honoured", party="Ney", marshal="Ney")
        assert out["applied"] == -4 and out["price"] == 4 and world.authority_tracker.held["pushes"] == [3]
        world.authority_tracker.authority = 61
        refused = ST.buy(world, "France", 4, "honoured", party="Ney", marshal="Ney")
        assert refused["applied"] == 0 and refused["refusal"].endswith("— refused")
        assert world.authority_tracker.held["pushes"] == [3] and int(world.authority_tracker.authority) == 61

    def test_a_court_keeps_no_recency_and_pays_at_its_floors(self, world):
        assert ST.push_price(world, "Austria", 5) == 5
        assert ST.offer(world, "Austria", 5)["refusal"] == ""

    def test_the_causes_are_in_the_creditors_voice(self):
        from backend.display_names import AUTHORITY_CAUSES, authority_cause
        for key in ("edict_decreed", "word_given", "word_lost", "honoured", "by_decree"):
            assert key in AUTHORITY_CAUSES, key
        assert authority_cause("word_given", marshal="Ney") == "your word given over Ney's objection"
        assert authority_cause("by_decree", marshal="Davout", other="Lannes") == \
            "Davout and Lannes reconciled by decree"
        assert "word_lost" in ST.FIELD_DENT_KEYS          # the Bulletin may repay it, as an insistence lost

    def test_the_words_price_by_his_trust_tier(self):
        class _M:
            def __init__(self, t):
                self.trust = type("T", (), {"value": t})()
        assert [ST.word_base(_M(t)) for t in (85, 60, 40, 20)] == [2, 3, 4, 5]

    def test_the_words_offer_and_its_stake(self, world, monkeypatch):
        offer = ST.word_offer(world, world.marshals["Ney"])
        assert set(offer) == {"price", "before", "after", "line", "refusal", "stake"}
        assert offer["stake"] == ("By your word: no trust or defiance; lost within 3 turns, "
                                  "trust −5 and authority −3.")
        monkeypatch.setattr(ST, "buys_armed", lambda *a, **k: False)
        assert ST.word_offer(world, world.marshals["Ney"]) == {}


# ═══════════════════════════════════════════════════════════════════════════
# Decree it — the Edict letters' third answer
# ═══════════════════════════════════════════════════════════════════════════

class TestDecreeIt:
    def test_the_letter_offers_three_answers(self, world):
        e, occ = _remounts_board(world)
        payload = MO.letter_payload(world, e, 7, 8, occ)
        assert [a["action"] for a in payload["answers"]] == [
            "accept_ai_proposal", "reject_ai_proposal", "decree_ai_proposal"]
        assert payload["button_decree"] == "auth 90 → 87 · 1 action · 8 turns"
        assert payload["choice_display"]["decree"] == "Decree it"
        assert payload["clauses"].index(payload["answers"][2]["quote"]) < \
            payload["clauses"].index(payload["answers"][1]["quote"])     # the two purses, then the refusal

    def test_the_decree_spends_authority_and_an_action_never_gold(self, world):
        e, occ = _remounts_board(world)
        p = MO.plan(world, e, MO.ANSWER_DECREE, occ)
        assert p["ok"] and [(r["op"], r.get("currency")) for r in p["rows"]] == [("admin", None), ("edict", "authority")]
        edict = p["rows"][1]
        assert (edict["amount"], edict["authority"], edict["party"]) == (0, 3, "Dejean")
        gold, admin = int(world.nation_gold["France"]), int(world.admin_actions_remaining)
        with _quiet():
            MO._apply(world, p)
        assert int(world.nation_gold["France"]) == gold and int(world.admin_actions_remaining) == admin - 1
        assert int(world.authority_tracker.authority) == 87
        assert [x[0]["id"] for x in AF.edicts_in_force(world, "France")] == [E2]
        last = world.authority_tracker.moves[-1]
        assert (last["key"], last["party"], last["delta"]) == ("edict_decreed", "Dejean", -3)
        assert last["cause"] == "the Remounts decreed on the Emperor's word"
        assert AF.runtime(world)[AF.EDICT_AUTHORITY_KEY]["France"] == 3

    def test_refused_under_the_floor_with_its_reason(self, world):
        e, occ = _remounts_board(world, authority=62)
        p = MO.plan(world, e, MO.ANSWER_DECREE, occ)
        assert not p["ok"] and "under 60" in p["refusal"] and p["refusal"].endswith("— refused")
        assert MO.answer_verdict(world, {"moment_id": f"{E2}#1", "type": "incoming_proposal",
                                         "is_moment": True}, "decree_ai_proposal") is not None

    def test_the_verdict_and_the_road(self):
        from backend.commands.dialogue_routing import DIALOGUE_ACTION_KEYWORDS
        from backend.game_logic.treaty import ACCEPT_ACTIONS
        assert "decree_ai_proposal" in ACCEPT_ACTIONS
        assert DIALOGUE_ACTION_KEYWORDS["decree"] == ["decree_ai_proposal"]
        assert MO.ANSWER_ACTIONS[MO.ANSWER_DECREE] == "decree_ai_proposal"

    def test_held_down_the_letter_reads_its_two_answers(self, world, monkeypatch):
        e, occ = _remounts_board(world)
        monkeypatch.setattr(ST, "buys_armed", lambda *a, **k: False)
        payload = MO.letter_payload(world, e, 7, 8, occ)
        assert [a["action"] for a in payload["answers"]] == ["accept_ai_proposal", "reject_ai_proposal"]
        assert "button_decree" not in payload
        assert MO.plan(world, e, MO.ANSWER_DECREE, occ)["refusal"] == "This letter cannot be decreed, Sire."

    def test_no_other_letter_can_be_decreed(self, world):
        e = MO.entry(world, "chancellors_letters")
        occ = {"id": "chancellors_letters#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7}
        assert MO.decree_side(e, occ) == {}
        assert MO.plan(world, e, MO.ANSWER_DECREE, occ)["ok"] is False

    def test_the_courts_decree_rides_the_courts_flip(self, world, monkeypatch):
        """AU-14: measured, not inert — a court whose gold refuses decrees in
        authority at its floors (the courts boot at 60). Parked behind
        `courts_move()` until the user's "Flip, flat grip" (November 6, 2026)
        flipped it with the courts' other writes; arm AUC holds it down —
        re-pinned consciously from `test_the_courts_decree_is_parked_with_the_courts_flip`."""
        e = MO.entry(world, E2)
        assert ST.courts_move() is True
        assert AF.edict_refusal(world, "Austria", e, currency="authority") == ""
        monkeypatch.setattr(ST, "courts_move", lambda *a, **k: False)        # arm AUC
        assert AF.edict_refusal(world, "Austria", e, currency="authority") == \
            "the courts' Decree waits for the courts' flip."
        monkeypatch.setattr(ST, "courts_move", lambda *a, **k: True)
        before = int(world.nation_authority.get("Austria", 60))
        with _quiet():
            AF.decree_for_court(world, "Austria", e, currency="authority")
        assert int(world.nation_authority["Austria"]) == before - 3
        assert AF.edict_state(world, "Austria", e) == "in_force"


# ═══════════════════════════════════════════════════════════════════════════
# By my word — both objection roads, and its verdict
# ═══════════════════════════════════════════════════════════════════════════

class TestByMyWord:
    def test_the_tactical_word_costs_authority_never_trust(self, client):
        ney = M.world.get_marshal("Ney")
        asked, _spent, _ = _order(client, "Ney, defend")
        assert asked.get("choices") == ["trust", "insist", "compromise", "word"]
        word = (asked.get("objection") or {}).get("word") or {}
        assert word["price"] == 3 and word["line"].startswith("Authority 100 → 97")       # TRUSTING
        trust = int(ney.trust.value)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "word"})
        assert reply.get("success") and spent == 1, reply.get("message")
        assert int(ney.trust.value) == trust and int(M.world.authority_tracker.authority) == 97
        assert str(reply.get("message")).startswith("By your word, Ney carries out the order as given.")
        assert M.world.authority_tracker.moves[-1]["key"] == "word_given"
        assert M.world.pending_objection is None

    def test_the_strategic_word_stamps_its_verdict(self, client):
        M.world.get_marshal("Mack").strength = _MACK_BEYOND_THE_MUSTER
        _order(client, "Davout, pursue Mack")
        assert M.world.pending_strategic_objection["word"]["price"] == 2           # DEVOTED
        davout = M.world.get_marshal("Davout")
        trust = int(davout.trust.value)
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "word"})
        assert reply.get("success") and spent == 2, reply.get("message")
        assert int(davout.trust.value) == trust and int(M.world.authority_tracker.authority) == 98
        pending = M.world.vindication_tracker.pending["Davout"]
        assert pending["choice"] == "word" and pending["executed_order"]["action"] == "pursue"
        assert str(reply.get("message")).endswith("By your word: Authority 100 → 98 — "
                                                  "the marshals' calm holds above 70.")

    def test_refused_under_the_floor_with_its_reason_the_objection_kept(self, client):
        M.world.authority_tracker.authority = 61
        asked, _spent, _ = _order(client, "Ney, defend")
        assert "word" not in asked.get("choices")
        reply, spent, _ = _post(client, "/respond_to_objection", {"choice": "word"})
        assert reply.get("success") is False and reply.get("objection_kept") is True and spent == 0
        assert str(reply.get("message")).startswith("Your word cannot be given, Sire — Authority 61 → 58")
        assert M.world.pending_objection is not None

    def test_the_typed_words(self, client):
        from backend.commands.dialogue_routing import format_answer_words, objection_answer_is_plain
        assert format_answer_words(["trust", "insist", "word"]) == "'trust', 'insist' or 'by my word'"
        assert objection_answer_is_plain("insist on my word", "insist")       # still an Insist
        assert objection_answer_is_plain("by my word", "word")
        _order(client, "Ney, defend")
        reply, _spent, _ = _order(client, "By my word")
        assert reply.get("success"), reply.get("message")
        assert M.world.authority_tracker.moves[-1]["key"] == "word_given"

    @pytest.mark.parametrize("result, trust, authority, judged", [
        ("defeat", -5, -3, True), ("victory", 0, 0, True), ("draw", 0, 0, True)])
    def test_the_verdict_is_loss_only_within_three_turns(self, world, result, trust, authority, judged):
        tracker = V.VindicationTracker()
        order = {"action": "attack", "target": "Mack", "marshal": "Ney"}
        tracker.record_choice("Ney", "word", order, None, executed_order=order, turn=4)
        world.current_turn = 7
        ney = world.marshals["Ney"]
        t0, a0 = int(ney.trust.value), int(world.authority_tracker.authority)
        out = tracker.resolve_battle("Ney", result, world, defender_name="Mack", battle_region="Swabia")
        assert out is not None and out["choice"] == "word"
        assert int(ney.trust.value) - t0 == trust and int(world.authority_tracker.authority) - a0 == authority
        if result == "defeat":
            assert world.authority_tracker.moves[-1]["key"] == "word_lost"

    def test_past_the_window_the_question_goes_unjudged(self, world):
        tracker = V.VindicationTracker()
        order = {"action": "attack", "target": "Mack", "marshal": "Ney"}
        tracker.record_choice("Ney", "word", order, None, executed_order=order, turn=4)
        world.current_turn = 8
        a0 = int(world.authority_tracker.authority)
        assert tracker.resolve_battle("Ney", "defeat", world, defender_name="Mack", battle_region="Swabia") is None
        assert int(world.authority_tracker.authority) == a0 and "Ney" not in tracker.pending


# ═══════════════════════════════════════════════════════════════════════════
# Honour him and By decree — the marshals' cards
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCards:
    def _confront(self, w, authority=90):
        murat, ney = w.marshals["Murat"], w.marshals["Ney"]
        murat.jealous_of, murat.jealousy_turns_remaining = "Ney", 3
        w.authority_tracker.authority = authority
        with _quiet():
            J.queue_confrontation_petition(w, murat, ney, level=0)
        return J.refresh_petition_affordability(w.pending_marshal_petition, w)

    def test_honour_rides_last_priced_in_authority(self, world):
        pet = self._confront(world)
        honour = pet["options"][-1]
        assert honour["id"] == "honour" and honour["cost_note"] == "4 authority" and honour["enabled"]
        assert honour["detail"].startswith("Murat's grievance ends and his trust rises 2; Ney, passed over, loses 2.")

    def test_honour_ends_the_grievance_and_marks_the_payback(self, world):
        self._confront(world)
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        tm, tn = int(murat.trust.value), int(ney.trust.value)
        with _quiet():
            res = J.handle_petition_response(world, "honour", executor=None, game_state={"world": world})
        assert res["success"] and murat.jealous_of is None
        assert (int(murat.trust.value) - tm, int(ney.trust.value) - tn) == (2, -2)
        assert int(world.authority_tracker.authority) == 86
        assert world.authority_tracker.held["honoured:Murat"] == int(world.current_turn)
        assert ST.honour_repaid(world, "France", "Murat") == 2

    def test_honour_is_closed_under_the_floor(self, world):
        pet = self._confront(world, authority=62)
        honour = pet["options"][-1]
        assert honour["enabled"] is False and honour["available"] is False
        assert honour["detail"] == honour["unavailable_reason"] and "under 60" in honour["detail"]

    def _rivals(self, w, value=-1):
        davout, lannes = w.marshals["Davout"], w.marshals["Lannes"]
        davout.set_relationship("Lannes", value)
        lannes.set_relationship("Davout", value)
        w.pending_marshal_petition = None
        with _quiet():
            J.queue_rivalry_petition(w, davout, lannes, value)
        return J.refresh_petition_affordability(w.pending_marshal_petition, w)

    @pytest.mark.parametrize("value", [-1, -2])
    def test_by_decree_rides_last_on_either_tier_and_lifts_a_rung(self, world, value):
        world.authority_tracker.authority = 90
        pet = self._rivals(world, value)
        decree = pet["options"][-1]
        assert decree["id"] == "decree" and decree["cost_note"] == "5 authority" and decree["enabled"]
        with _quiet():
            res = J.handle_petition_response(world, "decree", executor=None, game_state={"world": world})
        assert res["success"], res.get("message")
        assert world.marshals["Davout"].relationships["Lannes"] == value + 1
        assert world.authority_tracker.moves[-1]["key"] == "by_decree"

    def test_an_entrenched_pair_is_closed_with_its_reason(self, world):
        J._set_escalation_level(world.marshals["Davout"], "Lannes", J.ESCALATION_PERMANENT_LEVEL)
        world.authority_tracker.authority = 90
        decree = self._rivals(world, -1)["options"][-1]
        assert decree["enabled"] is False
        assert decree["unavailable_reason"] == "Their breach is entrenched: no decree lifts them above rivals."

    def test_the_recency_rise_reaches_the_cards(self, world):
        world.authority_tracker.authority = 90
        world.authority_tracker.held["pushes"] = [int(world.current_turn)]
        assert self._rivals(world, -1)["options"][-1]["cost_note"] == "6 authority"


# ═══════════════════════════════════════════════════════════════════════════
# The client and the instruments
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClient:
    def test_the_decree_rides_the_counters_slot(self):
        src = (SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        pinned = "counter_btn.visible = not is_counter and not is_ultimatum and not is_petition"
        assert src.index(pinned) < src.index("_is_decree_letter = is_moment and not _moment_answer(")
        assert 'choice_made.emit("decree", current_data)' in src
        assert 'action = "decree_ai_proposal"' in src and '"button_decree"' in src

    def test_the_third_answer_sits_third_on_the_row(self):
        """AU-16: the Counter's slot sat between Accept and Decline, so a decree
        letter's row read Accept · Decree · Decline while its preamble says a
        lapse "takes the second answer" — the Decline, second in the list. The
        decree letter seats the slot after the Decline; every other register
        puts it back between Accept and Reject."""
        src = (SCRIPTS / "incoming_proposal_popup.gd").read_text(encoding="utf-8")
        at = src.index("var answer_row: Node = counter_btn.get_parent()")
        block = src[at:src.index("reject_btn.disabled = false", at)]
        assert ("if _is_decree_letter and counter_btn.get_index() < reject_btn.get_index():\n"
                "\t\tanswer_row.move_child(counter_btn, reject_btn.get_index())") in block
        assert ("elif not _is_decree_letter and counter_btn.get_index() > reject_btn.get_index():\n"
                "\t\tanswer_row.move_child(counter_btn, reject_btn.get_index())") in block
        assert src.index("_is_decree_letter = is_moment and not _moment_answer(") < at

    def test_the_word_is_a_code_built_button_beside_insist(self):
        src = (SCRIPTS / "objection_dialog.gd").read_text(encoding="utf-8")
        assert 'word_button.name = "WordButton"' in src
        assert "move_child(word_button, insist_button.get_index() + 1)" in src
        assert 'choice_made.emit("word")' in src and '"word": objection.get("word"' in src
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert 'choice_text = "You give your word: the order stands as given."' in main

    def test_the_shrink_keeps_a_tall_panel_below_the_bar(self):
        """AU-15: the shrink re-centred a panel the clamp had stood below the
        bar — the five answers at 2.0 rode over the top bar."""
        utils = (SCRIPTS / "utils.gd").read_text(encoding="utf-8")
        at = utils.index("static func shrink_centered_panel_to_content(")
        body = utils[at:utils.index("\n# ──", at)]
        assert "if need > view.y - 88.0 - 2.0 * top_bar_growth():" in body
        assert "panel.offset_top = TOP_BAR_HEIGHT + HUD_MARGIN + top_bar_growth() - view.y / 2.0" in body
        scene = (SCENES / "objection_dialog.tscn").read_text(encoding="utf-8")
        assert scene.count("custom_minimum_size = Vector2(0, 45)") == 3

    def test_the_driver_dials(self):
        driver = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'AFFAIR_MODES = MOMENT_MODES + ("lapse", "decree")' in driver
        assert 'choices=["", "trust", "insist", "compromise", "word"]' in driver
        assert 'choices=["", "first_enabled", "rotate", "buy"]' in driver


class TestTheFrames:
    """The four surfaces the buys dress, shot at 1.0 and 2.0 and censused at the
    five physical resolutions (`docs/audits/uxr0/readability_au3a_buys_2026_11_05.json`)."""
    SURFACES = ("objection_dialog", "petition_command_closed", "petition_rivalry_decree",
                "affair_letter_the_magazines")

    def test_the_rivalry_staging_is_wired(self):
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        shots = (REPO / "tools" / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert 'record("petition_rivalry_decree", rivalry,' in cap
        assert '"id": "petition_rivalry_decree",' in shots

    @pytest.mark.parametrize("surface", SURFACES)
    def test_the_surface_is_shot_at_both_scales(self, surface):
        for tail in ("", "_X2"):
            png = REPO / "docs" / "audits" / f"IQ10_{surface.upper()}{tail}_2026_11_05.png"
            assert png.exists() and png.stat().st_size > 8000, png

    def test_the_readability_census_reads_no_red_and_no_p1(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS
        record = json.loads((REPO / "docs" / "audits" / "uxr0" / "readability_au3a_buys_2026_11_05.json")
                            .read_text(encoding="utf-8"))
        assert set(record["surfaces"]) == set(self.SURFACES)
        for sid, row in record["surfaces"].items():
            assert len(row["readings"]) == len(PHYSICAL_RESOLUTIONS), sid
            for label, reading in row["readings"].items():
                counts = reading["counts"]
                assert counts["rows"] > 0 and counts["red"] == 0 and counts["p1"] == 0, (sid, label)
