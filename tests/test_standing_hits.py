"""AU-2a "the hits" — the pins (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.4, §6 the
AU-2a row; the rules `SYSTEMS_REFERENCE.md` §170).

The bills offered in every campaign, never forced — each through AU-1's one
writer with its cause: the Chancellor's letter at any standing and the Host's
Complaint clamped at the floor and said (the user's "Clamp it first", November
4, 2026; `tests/test_affairs_nondominance.py` pins the two letters' rules; here
the deck's authoring keys and the validator), the
Claims of the Army on the dotation tick (Berthier presenting), the word
broken in `_record_treaty_breach` (−3 a strike, −6 an episode) and Make
Amends repaying it (never beyond the debt, never above the ceiling), the
stakes told in figures on the objection dialog and the vindication's own
sentences; and the three seams a series arm holds down (AUP / AUK / AUW)
reproducing the tree before the slice.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world():
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(world):
    return copy.deepcopy(world)


def _stage_claim(w, name="Lannes", opened=6, now=20, steps=2):
    """A marshal's claim fourteen turns unpaid at `now`, the chest able."""
    from backend.game_logic.dotation import compute_rente_face, get_rente_cost
    m = w.marshals[name]
    m.expectation_steps = steps
    w.current_turn = now
    m.expectation_grace_turn = opened
    rente = int(get_rente_cost(compute_rente_face(m, w), w, "France"))
    assert rente > 0
    w.nation_gold["France"] = 20 * rente + 100
    return m, rente


# ═══════════════════════════════════════════════════════════════════════
# The two letters at the floor — the deck's keys and the validator
# ═══════════════════════════════════════════════════════════════════════

class TestTheDeckAtTheFloor:
    def test_the_deck_and_the_fixture_carry_the_floor_and_the_rows_keys(self):
        for path in (SCENARIO, FIXTURE):
            block = json.loads(path.read_text(encoding="utf-8"))
            deck = (block.get("moments") or block).get("affairs", block.get("affairs") or {}).get("deck") \
                if "moments" in block or "affairs" in block else None
            if deck is None:
                deck = block["deck"]
            by_id = {e["id"]: e for e in deck}
            chancellor, host = by_id["chancellors_letters"], by_id["the_host"]
            assert chancellor["bites"] == "floor" and chancellor["bites_since"] == "AU-2a"
            # the user's "Clamp it first" (November 4, 2026): the Host at any standing
            assert host["bites"] == "clamp" and "bites_since" not in host
            op = host["decline"]["ops"][0]
            assert op == {"op": "authority", "amount": -2, "tiers": {"2": -3, "3": -4}, "since": "AU-2a"}
            assert host["decline"]["button_line"].startswith("auth {authority_before} → {authority_after} · ")

    def test_the_validator_accepts_the_shipped_deck_and_refuses_a_stray_row(self, world):
        from backend.modding import validator as V
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        with _quiet():
            result = V.validate_scenario(data)
        assert not [e for e in result.errors if "since" in str(e) or "button_line" in str(e)], result.errors[:5]
        bad = copy.deepcopy(data)
        deck = bad["moments"]["affairs"]["deck"]
        host = next(e for e in deck if e["id"] == "the_host")
        host["decline"]["ops"][0]["since"] = "AU-9"
        host["bites_since"] = "AU-9"
        with _quiet():
            result = V.validate_scenario(bad)
        errors = [str(e) for e in result.errors]
        assert any("since" in e and "AU-2a" in e for e in errors), errors[:5]
        assert any("bites_since" in e for e in errors), errors[:5]

    def test_a_clamp_needs_a_price_besides_authority(self, world):
        """The user's "Clamp it first": only a refusal that costs something else
        may clamp — clamped, the Chancellor's Decline (authority alone) would be
        free at the floor, so the validator refuses it; a clause `bites_since`
        stays the floor's alone."""
        from backend.modding import validator as V
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        bad = copy.deepcopy(data)
        deck = bad["moments"]["affairs"]["deck"]
        chancellor = next(e for e in deck if e["id"] == "chancellors_letters")
        chancellor["bites"] = "clamp"
        chancellor.pop("bites_since", None)
        host = next(e for e in deck if e["id"] == "the_host")
        host["bites_since"] = "AU-2a"
        with _quiet():
            result = V.validate_scenario(bad)
        errors = [str(e) for e in result.errors]
        assert any("deck[0].bites:" in e and "priced besides authority" in e for e in errors), errors[:5]
        assert any("deck[1].bites_since" in e for e in errors), errors[:5]
        relation_only = copy.deepcopy(data)
        host = next(e for e in relation_only["moments"]["affairs"]["deck"] if e["id"] == "the_host")
        host["decline"]["ops"] = [host["decline"]["ops"][0], host["decline"]["ops"][1]]   # relation `unless` vassal
        with _quiet():
            result = V.validate_scenario(relation_only)
        assert any("priced besides authority" in str(e) for e in result.errors), result.errors[:5]

    def test_the_seams_are_named_functions(self):
        from backend.game_logic import standing
        assert standing.hits_armed() is True and standing.claims_armed() is True and standing.breach_armed() is True
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert set(STANDING_SEAMS_BY_ROW) == {"AUB", "AUP", "AUK", "AUW"}

    def test_the_host_decline_names_the_authority_first_and_its_minister(self, w):
        from backend.game_logic import affairs, moments as MO
        e = affairs.template_by_id(w, "the_host")
        occ = {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1}
        p = MO.plan(w, e, MO.ANSWER_DECLINE, occ)
        rows = p["rows"]
        assert [r["op"] for r in rows] == ["authority", "relation", "loyalty"]
        assert (rows[0]["before"], rows[0]["after"], rows[0]["loss"]) == (100, 98, 2)
        assert p["receipt"].startswith("auth 100 → 98 · ")
        assert rows[0]["letter"] == e["title"] and rows[0]["party"]      # the host's minister
        occ2 = dict(occ, tier=2)
        assert next(r for r in MO.plan(w, e, MO.ANSWER_DECLINE, occ2)["rows"] if r["op"] == "authority")["loss"] == 3


# ═══════════════════════════════════════════════════════════════════════
# The Claims of the Army
# ═══════════════════════════════════════════════════════════════════════

class TestTheClaimsOfTheArmy:
    def test_a_claim_is_billed_once_at_fourteen_turns_with_berthier_presenting(self, w):
        from backend.game_logic import standing
        m, rente = _stage_claim(w)
        assert standing.claims_of_the_army(w, m, 13) == 0
        assert standing.claims_of_the_army(w, m, 14) == -3
        assert w.authority_tracker.authority == 97
        move = w.authority_tracker.moves[-1]
        assert (move["key"], move["party"], move["cause"]) == ("claims", "Lannes", "Lannes's claim, fourteen turns unpaid")
        assert w.authority_tracker.held["claims"] == ["Lannes:6"]
        assert standing.claims_of_the_army(w, m, 14) == 0           # once per claim
        assert standing.claims_of_the_army(w, m, 15) == 0
        line = [e for e in w.pending_dispatch_events if e.get("type") == "moment_receipt"][-1]["template_vars"]
        assert line["register"] == "claims"
        assert line["line"] == ("Berthier presents the claims of the army: Lannes, fourteen turns unpaid "
                                "while the chest could pay his rente — authority 100 → 97.")

    def test_a_re_opened_claim_is_a_new_claim(self, w):
        from backend.game_logic import standing
        m, _ = _stage_claim(w)
        assert standing.claims_of_the_army(w, m, 14) == -3
        m.expectation_grace_turn = 9                                  # the claim re-opened later
        assert standing.claims_of_the_army(w, m, 14) == -3
        assert w.authority_tracker.held["claims"] == ["Lannes:6", "Lannes:9"]

    def test_not_when_the_chest_is_short_nor_under_the_floor_nor_for_a_court(self, w):
        from backend.game_logic import standing
        m, rente = _stage_claim(w)
        w.nation_gold["France"] = 20 * rente - 1
        assert standing.claims_of_the_army(w, m, 14) == 0
        w.nation_gold["France"] = 20 * rente + 100
        w.authority_tracker.authority = 82                           # 82 − 3 = 79, under the floor 80
        assert standing.claims_of_the_army(w, m, 14) == 0
        w.authority_tracker.authority = 83
        assert standing.claims_of_the_army(w, m, 14) == -3            # 83 − 3 = 80 lands whole
        court = next(x for x in w.marshals.values() if x.nation == "Austria")
        court.expectation_steps = 2
        court.expectation_grace_turn = 6
        w.nation_gold["Austria"] = 10 ** 6
        assert standing.claims_of_the_army(w, court, 14) == 0         # the courts' books are AU-4's

    def test_the_tick_bills_it_and_the_morning_says_it(self, w):
        from backend.game_logic import dispatch
        m, _ = _stage_claim(w)
        with _quiet():
            w._process_dotation_state()
            d = dispatch.build_morning_dispatch(w)
        assert any(mv["key"] == "claims" and mv["party"] == "Lannes" for mv in w.authority_tracker.moves)
        events = [e for e in d.get("diplomatic_events") or [] if e.get("type") == "moment_receipt"]
        assert [e["text"] for e in events] == [
            "Berthier presents the claims of the army: Lannes, fourteen turns unpaid while the chest "
            "could pay his rente — authority 100 → 97."]
        assert events[0]["priority"] == "HIGH"
        assert d["situation"]["authority_label"] == \
            "Strong — down 3 since yesterday: Lannes's claim, fourteen turns unpaid (−3)"

    def test_the_seam_down_bills_nothing(self, w, monkeypatch):
        from backend.game_logic import standing
        monkeypatch.setattr(standing, "claims_armed", lambda *a, **k: False)
        m, _ = _stage_claim(w)
        assert standing.claims_of_the_army(w, m, 14) == 0 and not w.authority_tracker.moves


# ═══════════════════════════════════════════════════════════════════════
# The word broken, and Make Amends
# ═══════════════════════════════════════════════════════════════════════

class TestTheWordBroken:
    PREVIEW = {"fault_nation": "France", "injured_party": "Prussia", "episode_id": "ep-1"}

    def test_three_a_strike_six_an_episode_with_the_court_as_party(self, w):
        from backend.game_logic import standing
        assert standing.breach(w, self.PREVIEW) == -3
        assert standing.breach(w, self.PREVIEW) == -3
        assert standing.breach(w, self.PREVIEW) == 0
        assert w.authority_tracker.authority == 94
        move = w.authority_tracker.moves[-1]
        assert (move["key"], move["party"], move["cause"]) == ("breach", "Prussia", "the word broken to Prussia")
        assert w.authority_tracker.held["breach:ep-1"] == 6 and w.authority_tracker.held["owed:Prussia"] == 6
        assert standing.breach(w, dict(self.PREVIEW, episode_id="ep-2")) == -3   # a new episode

    def test_a_courts_breach_moves_nothing(self, w):
        from backend.game_logic import standing
        assert standing.breach(w, {"fault_nation": "Prussia", "injured_party": "France", "episode_id": "x"}) == 0
        assert w.nation_authority["Prussia"] == 60 and not w.authority_tracker.moves

    def test_make_amends_repays_the_debt_under_the_ceiling(self, w):
        from backend.game_logic import standing
        w.authority_tracker.authority = 90
        standing.breach(w, self.PREVIEW)                                # 87, owed 3
        assert standing.amends(w, "France", "Prussia") == 2             # 89
        assert standing.amends(w, "France", "Prussia") == 1             # 90, the debt repaid
        assert standing.amends(w, "France", "Prussia") == 0             # nothing owed
        assert "owed:Prussia" not in w.authority_tracker.held
        assert w.authority_tracker.moves[-1]["cause"] == "amends made to Prussia"
        assert standing.amends(w, "France", "Austria") == 0             # no debt to that court

    def test_the_ceiling_holds_a_repayment(self, w):
        from backend.game_logic import standing
        standing.breach(w, self.PREVIEW)
        standing.breach(w, self.PREVIEW)                                   # 100 → 94, owed 6
        assert standing.amends(w, "France", "Prussia") == 1                    # 95: the ceiling
        assert standing.amends(w, "France", "Prussia") == 0
        assert w.authority_tracker.held["owed:Prussia"] == 5

    def test_the_breach_recorder_and_both_amends_call_the_writer(self):
        src = (BACKEND / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        body = src[src.index("def _record_treaty_breach("):src.index("# CENTRALIZED DIPLOMATIC STATE SETTER")]
        assert "_standing.breach(world, breach_preview)" in body
        ex = (BACKEND / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        assert ex.count("_standing.amends(world, player, target_nation)") == 2
        confirm = ex[ex.index('"type": "force_declare_war_confirmation"') - 2000:ex.index('"type": "force_declare_war_confirmation"')]
        assert "warning_text += _standing.breach_confirm_clause(world, player)" in confirm

    def test_the_confirms_quote_is_the_first_strike(self, w):
        from backend.game_logic import standing
        assert standing.quote(w, "France", -standing.BREACH_STRIKE)["line"] == \
            "Authority 100 → 97 — the marshals' calm holds above 70."

    def test_the_seam_down_books_nothing(self, w, monkeypatch):
        from backend.game_logic import standing
        monkeypatch.setattr(standing, "breach_armed", lambda *a, **k: False)
        assert standing.breach(w, self.PREVIEW) == 0 and standing.amends(w, "France", "Prussia") == 0
        assert not w.authority_tracker.moves


# ═══════════════════════════════════════════════════════════════════════
# The stakes told in figures
# ═══════════════════════════════════════════════════════════════════════

class TestTheStakesTold:
    def test_the_stake_line_names_the_vindications_figures(self):
        from backend.game_logic import standing
        assert standing.insist_stake_line() == (
            "If the field is lost under your insistence: trust −5, authority −5; won: authority +5. "
            "A compromise: authority +2 won, trust −2 and authority −2 lost.")

    def test_both_objection_paths_stamp_it_and_the_dialog_prints_it(self):
        ex = (BACKEND / "commands" / "executor.py").read_text(encoding="utf-8")
        assert 'objection["stake_line"] = _standing.insist_stake_line()' in ex
        st = (BACKEND / "commands" / "strategic_executor.py").read_text(encoding="utf-8")
        assert '"stake_line": __import__("backend.game_logic.standing",' in st
        gd = (SCRIPTS / "objection_dialog.gd").read_text(encoding="utf-8")
        assert '"stake_line": objection.get("stake_line", response.get("stake_line", ""))' in gd   # the join
        assert 'message_label.text += "\\n\\n" + stake_line' in gd

    def test_the_vindication_applies_its_constants_and_says_them(self, w):
        from backend.commands import vindication as VI
        assert (VI.INSIST_WIN_AUTHORITY, VI.INSIST_LOSS_AUTHORITY, VI.INSIST_LOSS_TRUST) == (5, -5, -5)
        w.vindication_tracker.record_choice("Ney", "insist", {"action": "attack", "marshal": "Ney"})
        result = w.vindication_tracker.resolve_battle("Ney", "defeat", types.SimpleNamespace(world=w))
        assert result["message"].endswith("(trust −5, authority −5).")
        assert w.authority_tracker.authority == 95 and w.authority_tracker.moves[-1]["key"] == "insisted_lost"
        w.vindication_tracker.record_choice("Ney", "compromise", {"action": "attack", "marshal": "Ney"})
        result = w.vindication_tracker.resolve_battle("Ney", "victory", types.SimpleNamespace(world=w))
        assert result["message"].endswith("(authority +2).") and w.authority_tracker.authority == 97


class TestTheClampAndTheBreachAreSaid:
    """The user's "Clamp it first" (November 4, 2026) and its sweep: a price the
    floor clamps says what it kept (AU-7), and the word broken is quoted on
    every choice that breaks a treaty, not the declaration's alone (AU-8)."""

    def test_a_partial_clamp_says_how_much_is_taken(self, w):
        from backend.game_logic import affairs, moments as MO
        e = affairs.template_by_id(w, "the_host")
        w.authority_tracker.authority = 72
        occ = {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 2}
        p = MO.plan(w, e, MO.ANSWER_DECLINE, occ)
        row = next(r for r in p["rows"] if r["op"] == "authority")
        assert (row["loss"], row["after"], row["floor"]) == (1, 71, True)
        assert row["line"].endswith("the floor holds at 71 on the Emperor's grip (72): only 1 of the 3 is taken")
        assert p["receipt"].startswith("auth 72 → 71 · ")
        w.authority_tracker.authority = 73
        row = next(r for r in MO.plan(w, e, MO.ANSWER_DECLINE, occ)["rows"] if r["op"] == "authority")
        assert row["line"].endswith("only 2 of the 3 are taken")

    def test_under_the_floor_the_line_says_the_grip_is_under_it(self, w):
        from backend.game_logic import affairs, moments as MO
        e = affairs.template_by_id(w, "the_host")
        w.authority_tracker.authority = 60
        occ = {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1}
        p = MO.plan(w, e, MO.ANSWER_DECLINE, occ)
        row = next(r for r in p["rows"] if r["op"] == "authority")
        assert row["loss"] == 0 and row["floor"] is True
        assert row["line"] == ("Authority 60 → 60 — nothing is taken: the Emperor's grip (60) "
                               "is under the floor of 71")
        MO._apply(w, p)
        assert w.authority_tracker.authority == 60

    def test_the_manual_break_quotes_the_word_broken(self):
        from backend.commands.executor import CommandExecutor
        from tests.conftest import WorldFactory
        world = WorldFactory.basic()
        key = world._make_diplo_key(world.player_nation, "Prussia")
        world.active_treaties[key] = {"type": "non_aggression",
                                      "nations": [world.player_nation, "Prussia"], "turn_created": 1}
        world.diplomatic_states[key] = "NON_AGGRESSION"
        world.diplomatic_points = 5
        with _quiet():
            result = CommandExecutor()._diplomatic._execute_diplomatic_break(
                {"target_nation": "Prussia", "action": "diplomatic_break"}, world)
        message = result.get("message", "")
        assert "Shall I proceed?" in message, message
        assert "And the court keeps its own count: Authority " in message, message

    def test_the_paradox_quotes_the_word_broken_once(self):
        from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        set_diplomatic_state(world, "France", "Britain", "ALLIANCE", "test_setup")
        set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "test_setup")
        set_diplomatic_state(world, "Britain", "Prussia", "PEACE", "test_setup")
        with _quiet():
            declare_war(world, "Britain", "Prussia")
        message = (world.commitment_paradox_popup or {}).get("message", "")
        assert message.count("Either way, the court keeps its own count: Authority ") == 1, message

    def test_the_clamped_letter_is_shot_at_both_scales(self):
        """The said clamp on the real letter (`tools/iq10_capture_payloads.py`'s bled
        board, authority 64): the frames at 1.0 and 2.0."""
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        assert 'record("affair_letter_the_host_clamped"' in cap
        shots = (REPO / "tools" / "iq10_run_captures.py").read_text(encoding="utf-8")
        assert '("the_host_clamped",' in shots
        for tail in ("", "_X2"):
            png = REPO / "docs" / "audits" / f"IQ10_AFFAIR_LETTER_THE_HOST_CLAMPED{tail}_2026_11_04.png"
            assert png.exists() and png.stat().st_size > 8000, png

    def test_held_down_the_quotes_go_quiet(self, w, monkeypatch):
        from backend.game_logic import standing
        assert standing.breach_quote(w, "France").startswith("Authority 100 → 97")
        monkeypatch.setattr(standing, "breach_armed", lambda *a, **k: False)
        assert standing.breach_confirm_clause(w, "France") == ""
        assert standing.breach_paradox_clause(w, "France") == ""


class TestTheCausesAndTheCensuses:
    def test_the_three_new_keys_have_their_fields(self):
        from backend.display_names import AUTHORITY_CAUSES, authority_cause
        assert authority_cause("claims", marshal="Lannes") == "Lannes's claim, fourteen turns unpaid"
        assert authority_cause("breach", court="Prussia") == "the word broken to Prussia"
        assert authority_cause("amends", court="KingdomOfItaly") == "amends made to Kingdom of Italy"
        assert {"claims", "breach", "amends"} <= set(AUTHORITY_CAUSES)

    def test_the_modding_doc_names_the_keys(self):
        doc = (REPO / "docs" / "MODDING_FORMAT.md").read_text(encoding="utf-8")
        assert "`bites_since`" in doc and "`since`" in doc and "the Host's Complaint" in doc
