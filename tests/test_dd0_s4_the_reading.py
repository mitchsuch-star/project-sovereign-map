"""DD-0 S4 "The Command Road" — THE READING and THE EXIT PREDICATE
(October 10, 2026; PRE_DEPLOY_PLAN.md §3.0 "the structural fix"; rules
SYSTEMS_REFERENCE.md §104; rows BUG_FIXES.md §DD-0 S3 DD0-9 / DD0-10 and
the sixteen open command rows SFR-H2 … SFR-D41).

Two structures and the vocabulary they carry, driven through the real
`POST /command` on a fresh 1805 board with the trace on:

  The Reading (backend/ai/reading.py)      — one tokenised reading, peeled
      from the outside in; the typed line is never spliced, the string the
      readers see is COMPOSED from spans. The 30 ledger rows and the six
      keyless shrugs of the third blind set are its acceptance.
  The exit predicate (backend/commands/exit_predicate.py) — "did I act on
      the marshal, place and arm that were named?": a stationary arm at a
      province the marshal is not in is refused by name (SFR-D7); a
      substitution the reply does not name is appended to it.
  The vocabulary — the sixteen open command rows, each a reading: the law
      verb (H2), the typo after "Tell X to" and the precaution (H3), the
      affordability premise (H5), the bench (H6), the levy that names the
      man (H7), the past-battle premise (H13), the reward's reason (D8),
      the Guard as the men (D9), the compound's second half (D10), the
      standing premise (D20), the halt-and-hold (D24), the second man on
      the relay (D25), take-back / return-to (D37), the arrival sequel's
      honest note (D38), the recruit arm disclosed (D41).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
from pathlib import Path

import pytest

from backend.ai import reading as R
from backend.commands import exit_predicate as XP

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="dd0_s4_"))
    from fastapi.testclient import TestClient
    with contextlib.redirect_stdout(io.StringIO()):
        import backend.main as M
        c = TestClient(M.app)
    originals = (M.game_state["world"], M.world, M.parser)
    try:
        yield c, M
    finally:
        M.game_state["world"], M.world, M.parser = originals


def _fresh(M):
    from backend.ai import parser_eval as pe
    from backend.commands.parser import CommandParser
    with contextlib.redirect_stdout(io.StringIO()):
        world = pe.build_world("1805")
        M.game_state["world"] = world
        M.world = world
        M.parser = CommandParser(use_real_llm=False)
    return world


def _post(client, line, stage=None):
    """A fresh board, optionally staged by `stage(world)`, then the line."""
    c, M = client
    world = _fresh(M)
    if stage is not None:
        stage(world)
    with contextlib.redirect_stdout(io.StringIO()):
        r = c.post("/command", json={"command": line, "trace": True})
    return r.json()


def _rules(reply, stage):
    return [r["rule"] for r in reply.get("parse_trace", []) if r["stage"] == stage]


def _parsed(reply):
    for r in reply.get("parse_trace", []):
        if r["stage"] == "parse" and r["rule"] == "result":
            return r["detail"]
    return {}


FRIENDS = ["Ney", "Davout", "Soult", "Lannes", "Murat", "Massena", "Bernadotte", "Napoleon"]
FOES = ["Mack", "ArchdukeJohn", "ArchdukeCharles", "Kutuzov"]
PLACES = ["Rhineland", "Swabia", "Lorraine", "Frankfurt", "Munich", "Milan", "Tyrol", "Brabant"]


def _read(line):
    return R.read(line, FRIENDS, FOES, PLACES, ["Austria", "Prussia", "Sweden"])


# ═════════════════════════ THE READING, PURE ═════════════════════════════════

class TestTheReadingIsSpansNotSplices:
    def test_the_typed_line_is_immutable_and_the_text_is_composed(self):
        r = _read("stand behind Ney, Davout, in case Mack turns on him")
        assert r.typed == "stand behind Ney, Davout, in case Mack turns on him"
        assert {s.kind for s in r.spans} == {"tail"}
        assert r.address == "Davout" and r.address_rotated
        assert r.text() == "Davout, stand behind Ney"
        assert [x[0] for x in r.rows] == ["peel_precaution", "peel_trailing_vocative"]
        assert "in case" in r.notes

    @pytest.mark.parametrize("line,composed", [
        ("cancel, the men are rested", "cancel"),
        ("wait, Ney", "Ney, wait"),
        ("retire, Ney", "Ney, retire"),
        ("Ney, retire, the men are rested", "Ney, retire"),
        ("protect Davout's flank, Ney", "Ney, protect Davout's flank"),
        ("attack Davout, Ney", "Ney, attack Davout"),
        ("Ney, take Swabia with Lannes in support", "Ney, take Swabia, then Lannes, support Ney"),
        ("ney frankfurt with Lannes in support", "ney frankfurt, then Lannes, support Ney"),
        ("Ney, hold position because the men are ready with Lannes in support",
         "Ney, hold position, then Lannes, support Ney"),
        ("hold position because the men are ready, Ney", "Ney, hold position"),
        ("Prince Murat, keep on John's heels", "Murat, keep on John's heels"),
        ("Davout will cover the Marshal Ney's advance", "Davout, cover the Marshal Ney's advance"),
        ("It's Mack's turn. Ney, at him.", "Ney, attack Mack"),
        ("Lannes: Swabia, via the shortest road", "Lannes: Swabia"),
        ("attack Davout, Ney, the men are rested", "Ney, attack Davout"),
        ("wait, please Ney", "Ney, wait"),
        ("attack Davout, Ney — thank you", "Ney, attack Davout"),
        ("Murat, charge Mack, the cavalry is fresh", "Murat, charge Mack"),
        ("Bernadotte, exercise the troops, they're green", "Bernadotte, exercise the troops"),
        ("Good. Ney, attack Mack.", "Ney, attack Mack"),
    ])
    def test_the_stages_compose_the_line(self, line, composed):
        assert _read(line).text() == composed

    @pytest.mark.parametrize("line", [
        "Ney, attack Mack", "Davout, support Ney", "support Ney", "Ney, the men are rested",
        "Davout, hold Rhineland, Ney", "Ney will not attack Mack",
        "Ney, retreat, Mack is attacking", "Massena, hold Milan at all costs",
        "Ney, march to Swabia and attack Mack when you get there",
        "Ney, attack Mack, then Davout, support him", "maybe Gen. Ney, hold",
        "what's in Tyrol? Massena, find out", "Marshal Ney moves to Lorraine", "Marshal Ney: Brabant.",
        "Lannes, march back to Franche-Comte", "stay here, then attack Mack",
        "recruit infantry in Paris, 5000 men", "Talleyrand: nonaggression with Denmark, Sweden too if you can",
    ])
    def test_a_line_with_nothing_to_peel_is_left_whole(self, line):
        r = _read(line)
        assert r.rows == [], (line, r.rows, r.text())

    def test_foe_forms_add_the_surname_when_it_names_one_foe(self):
        forms = R.foe_forms(FOES)
        assert "John" in forms and "Charles" in forms and "Archduke John" in forms
        assert R.foe_named_in("keep on John's heels", FOES) == "ArchdukeJohn"
        assert R.foe_named_in("It's Mack's turn.", FOES) == "Mack"


# ═════════════════════════ THE LEDGER'S ROWS, AT THE WIRE ════════════════════

class TestTheLedgerRowsRead:
    @pytest.mark.parametrize("line,action", [
        ("cancel, the men are rested", "cancel"),
        ("please, cancel, the men are rested", "cancel"),
        ("wait, Ney", "wait"),
        ("retire, Ney", "retreat"),
        ("Ney, retire, the men are rested", "retreat"),
        ("send Soult to Orleanais, the men are rested", "move"),
        ("ney frankfurt, the men are rested", "move"),
        ("someone attcak Mack", "attack"),
        ("everyone reterat", "retreat"),
    ])
    def test_the_comma_aside_the_vocative_and_the_typo(self, client, line, action):
        reply = _post(client, line)
        assert _parsed(reply).get("action") == action, (line, reply.get("parse_trace"))

    @pytest.mark.parametrize("line,head_action,head_target", [
        ("Ney, attak Mack with Lannes in support", "attack", "Mack"),
        ("Ney, mvoe to Lorraine with Lannes in support", "move", "Lorraine"),
        ("Ney, take Swabia with Lannes in support", "attack", "Swabia"),
        ("Ney moves to Lorraine with Lannes in support", "move", "Lorraine"),
        ("Marshal Soult will relocate his corps to Nivernais. with Lannes in support", "move", "Nivernais"),
        ("ney frankfurt with Lannes in support", "move", "Frankfurt"),
    ])
    def test_the_second_man_rides_the_relay_whatever_the_head(self, client, line, head_action, head_target):
        reply = _post(client, line)
        assert "peel_support_suffix" in _rules(reply, "reading"), reply.get("parse_trace")
        parsed = _parsed(reply)
        assert parsed.get("action") == head_action and parsed.get("target") == head_target, parsed
        assert parsed.get("strategic_type") != "SUPPORT"
        assert "Lannes, support" in str(reply.get("dropped_sequel") or "")

    def test_the_hold_with_a_reason_and_a_second_man(self, client):
        reply = _post(client, "Ney, hold position because the men are ready with Lannes in support")
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "HOLD" and parsed.get("target") == "Rhineland", parsed
        reply = _post(client, "hold position because the men are ready, Ney")
        parsed = _parsed(reply)
        assert parsed.get("marshal") == "Ney" and parsed.get("target") == "Rhineland", parsed

    @pytest.mark.parametrize("line", ["protect Davout, Ney", "protect Davout's flank, Ney"])
    def test_the_trailing_name_is_the_addressee(self, client, line):
        reply = _post(client, line)
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "SUPPORT" and parsed.get("target") == "Davout", parsed
        assert parsed.get("marshal") == "Ney"

    def test_attack_davout_ney_refuses_by_name(self, client):
        reply = _post(client, "attack Davout, Ney")
        assert "Ney will not attack our own" in reply["message"]

    def test_the_ledger_is_at_its_floor(self):
        ledger = json.loads((REPO / "tests" / "data" / "metamorphic_known_failures.json").read_text(encoding="utf-8"))
        assert ledger["count"] == len(ledger["failures"]) == 0


# ═════════════════════════ THE SIX KEYLESS SHRUGS ════════════════════════════

class TestTheSixShrugsRead:
    def test_at_him_after_the_rhetoric(self, client):
        reply = _post(client, "It's Mack's turn. Ney, at him.")
        assert "peel_rhetoric" in _rules(reply, "reading") and "rewrite_at_him" in _rules(reply, "reading")
        assert _parsed(reply).get("target") == "Mack"
        assert "MUSTER" in reply["message"]

    def test_the_demonym_line_stays_the_live_parsers_and_is_never_misread(self, client):
        """`Ney, hit the Austrians` is the one of the six that stays keyless-
        honest: IQ-9's gate pins "hit the <demonym>" as a phrasing the live
        parser reads (its cassette), so the mock shrugs rather than guess —
        nothing runs, nothing is spent."""
        reply = _post(client, "Ney, hit the Austrians")
        assert reply["success"] is False
        assert "MUSTER" not in reply["message"] and "dispatch" not in _rules(reply, "dispatch")

    def test_the_surname_on_his_heels(self, client):
        reply = _post(client, "Prince Murat, keep on John's heels")
        assert "read_address" in _rules(reply, "reading")
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "PURSUE" and "John" in str(parsed.get("target")), parsed
        assert "Cannot find" not in reply["message"]

    def test_cover_his_advance_is_support(self, client):
        reply = _post(client, "Davout will cover the Marshal Ney's advance")
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "SUPPORT" and parsed.get("target") == "Ney", parsed

    def test_stand_behind_him_in_case(self, client):
        reply = _post(client, "stand behind Ney, Davout, in case Mack turns on him")
        parsed = _parsed(reply)
        assert parsed.get("marshal") == "Davout" and parsed.get("strategic_type") == "SUPPORT", parsed
        assert parsed.get("target") == "Ney"
        assert "precaution" in reply["message"]

    def test_the_bench_question(self, client):
        reply = _post(client, "Promote someone to marshal — Berthier, who do we have?")
        assert "Candidates:" in reply["message"]
        assert "Another" not in reply["message"]


# ═════════════════════════ THE EXIT PREDICATE ════════════════════════════════

class TestTheExitPredicate:
    @pytest.mark.parametrize("line,who,there,named", [
        ("Massena, drill your men and rest them at Munich", "Massena", "Milan", "Munich"),
        ("Ney, defend Swabia", "Ney", "Rhineland", "Swabia"),
        ("Lannes, fortify Lorraine", "Lannes", "Franche-Comte", "Lorraine"),
    ])
    def test_a_stationary_arm_at_another_province_is_refused_by_name(self, client, line, who, there, named):
        reply = _post(client, line)
        assert reply["success"] is False
        assert f"{who} stands at {there}, not {named}" in reply["message"], reply["message"]
        assert f"'{who}, move to {named}'" in reply["message"]
        assert "place_mismatch_refused" in _rules(reply, "executor")
        assert reply.get("free_action") is True or "Nothing has been relayed" in reply["message"]

    def test_the_arm_where_he_stands_is_not_refused(self, client):
        reply = _post(client, "Massena, fortify Milan")
        assert "place_mismatch_refused" not in _rules(reply, "executor")
        reply = _post(client, "Davout, drill")
        assert "place_mismatch_refused" not in _rules(reply, "executor")

    def test_a_strategic_hold_at_a_province_is_a_march_and_hold(self, client):
        reply = _post(client, "Davout, hold Lorraine")
        assert "place_mismatch_refused" not in _rules(reply, "executor")

    def test_the_place_pre_check_is_pure(self):
        class _M:
            name, location = "Ney", "Rhineland"

        class _W:
            regions = {"Rhineland": object(), "Swabia": object()}

            def get_marshal(self, n):
                return _M() if n == "Ney" else None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Swabia"}, "drill", _W()) is not None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Rhineland"}, "drill", _W()) is None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Swabia"}, "move", _W()) is None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Mack"}, "drill", _W()) is None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Swabia", "_strategic_execution": True},
                                  "drill", _W()) is None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Swabia", "strategic_type": "HOLD"},
                                  "defend", _W()) is None
        assert XP.place_pre_check({"marshal": "Ney", "target": "Swabia"}, "garrison", _W()) is None

    def test_disclose_names_an_unnamed_substitution_and_nothing_else(self):
        entered = {"marshal": "Ney", "action": "attack", "target": "Mack"}
        assert XP.disclose(entered, dict(entered), {"success": True, "message": "Ney attacks Mack"}) is None
        exited = {"marshal": "Ney", "action": "attack", "target": "ArchdukeJohn"}
        out = XP.disclose(entered, exited, {"success": True, "message": "The attack goes in."})
        assert out and "you named Mack" in out and "Archduke John" in out
        assert XP.disclose(entered, exited, {"success": True, "message": "Ney attacks Archduke John"}) is None
        assert XP.disclose(entered, exited, {"success": False, "message": "refused"}) is None
        picked = {"marshal": "Soult", "action": "attack", "target": "Mack"}
        assert XP.disclose({"action": "attack", "target": "Mack"}, picked,
                           {"success": True, "message": "MUSTER — Soult vs Mack"}) is None
        out = XP.disclose({"action": "attack", "target": "Mack"}, picked, {"success": True, "message": "Done."})
        assert out and "the order went to Soult" in out
        asked = {"marshal": "Soult", "action": "recruit", "requested_type": "cavalry"}
        out = XP.disclose(asked, dict(asked), {"success": True, "message": "Soult recruits 3,000 men"})
        assert out and "you asked for cavalry" in out
        assert XP.disclose(asked, dict(asked), {"success": True, "message": "Soult recruits 3,000 infantry"}) is None

    def test_the_recruit_arm_is_disclosed_on_the_wire(self, client):
        def rich(world):
            world.gold = 50_000
        reply = _post(client, "Soult, recruit cavalry", stage=rich)
        assert "infantry" in reply["message"].lower()

    def test_an_auto_pick_names_its_man(self, client):
        reply = _post(client, "someone attack Mack")
        assert "command_changed" in _rules(reply, "executor")
        who = _parsed(reply)
        assert who.get("marshal") is None
        assert "Soult" in reply["message"] or "MUSTER" in reply["message"]


# ═════════════════════════ THE SIXTEEN OPEN ROWS ═════════════════════════════

class TestTheSixteenOpenRows:
    def test_h2_pass_the_law_enacts(self, client):
        reply = _post(client, "Please pass the Staff law")
        assert "rewrite_pass_a_law" in _rules(reply, "parser")
        assert "Marshal 'Staff'" not in reply["message"]
        assert "Grand Quartier" in reply["message"] or "enact" in reply["message"].lower()

    def test_h3_the_typo_after_tell_and_the_precaution(self, client):
        reply = _post(client, "Tell Massena to fortfy at Milan in case Archduke John comes down from the Tyrol")
        assert "peel_precaution" in _rules(reply, "reading")
        assert "repair_leading_verb_typo" in _rules(reply, "parser")
        assert _parsed(reply).get("action") == "fortify"

    def test_h5_the_affordability_premise_is_the_price_check(self, client):
        reply = _post(client, "If we can still afford it, put a supply depot up in the Rhineland")
        assert "strip_affordability_premise" in _rules(reply, "parser")
        assert "rewrite_build_idiom" in _rules(reply, "parser")
        assert "Supply Depot" in reply["message"] or "depot" in reply["message"].lower()
        assert "contingency" not in reply["message"]

    @pytest.mark.parametrize("line", ["Stables in Burgundy, please", "I want a supply depot in Savoy",
                                      "Fortress at Lorraine, build it"])
    def test_the_build_register(self, client, line):
        reply = _post(client, line)
        assert _parsed(reply).get("action") == "build", (line, reply.get("parse_trace"))

    def test_h6_the_bench(self, client):
        reply = _post(client, "Commission another marshal")
        assert "Another" not in reply["message"] and "Candidates:" in reply["message"]

    def test_h7_the_levy_on_foreign_ground_names_the_man(self, client):
        def on_swabia(world):
            world.marshals["Davout"].location = "Swabia"
        reply = _post(client, "raise more infantry for Davout's corps", stage=on_swabia)
        assert "We do not control Swabia" in reply["message"], reply["message"]
        assert "Davout stands there" in reply["message"]

    def test_h13_the_battle_premise(self, client):
        reply = _post(client, "If Ney beat Mack, give him a rente for it")
        assert "no such battle is on the record" in reply["message"]
        assert "contingency" not in reply["message"]

        def won(world):
            world.event_log.append({"type": "battle", "attacker": {"name": "Ney"},
                                    "defender": {"name": "Mack"}, "outcome": "attacker_victory"})
            world.gold = 50_000
        reply = _post(client, "If Ney beat Mack, give him a rente for it", stage=won)
        assert "contingency" not in reply["message"] and "no such battle" not in reply["message"]
        assert "rente" in reply["message"].lower() or "Ney" in reply["message"]

    def test_d8_the_reward_for_a_reason(self, client):
        reply = _post(client, "reward Murat for his charge at Swabia")
        assert "rewrite_reward_idiom" in _rules(reply, "parser")
        assert "needs one victory" not in reply["message"]

    def test_d9_drill_your_guard_is_a_drill(self, client):
        reply = _post(client, "Napoleon, drill your guard")
        assert _parsed(reply).get("action") == "drill", _parsed(reply)
        assert "will hold" not in reply["message"]

    def test_d10_the_compound_keeps_its_halves(self, client):
        reply = _post(client, "dig in at Milan and hold the line")
        assert "strip_hold_the_line_tail" in _rules(reply, "parser")
        assert _parsed(reply).get("action") in ("fortify",), _parsed(reply)
        # the unfortify of open ground stays the honest refusal (CX-R2's payload
        # is the executor's gate); the relay names the march that did not go
        # out — the silence the row filed is closed by the note, not a no-op
        reply = _post(client, "Lannes, unfortify and march on Bohemia")
        assert "not currently fortified" in reply["message"]
        assert reply.get("dropped_sequel") == "march on Bohemia"
        assert '"march on Bohemia"' in reply["message"] and "not relayed" in reply["message"]
        reply = _post(client, "Lannes, break camp and march to Bohemia")
        assert _parsed(reply).get("action") == "move" and _parsed(reply).get("target") == "Bohemia"

    def test_d20_the_standing_premise(self, client):
        reply = _post(client, "attack Mack if he is still standing")
        assert "contingency" not in reply["message"]
        assert "MUSTER" in reply["message"]

        def gone(world):
            world.marshals["Mack"].strength = 0
        reply = _post(client, "attack Mack if he is still standing", stage=gone)
        assert "The order rested on Mack still standing" in reply["message"]

    def test_d24_stop_chasing_and_hold(self, client):
        reply = _post(client, "Ney, stop chasing John and hold where you are")
        assert "strip_stop_chasing" in _rules(reply, "parser")
        parsed = _parsed(reply)
        assert parsed.get("strategic_type") == "HOLD" and parsed.get("target") == "Rhineland", parsed
        assert "destination" not in reply["message"]
        reply = _post(client, "Ney, stop chasing John")
        assert _parsed(reply).get("action") == "cancel"

    def test_d25_the_second_man_is_named_and_offered(self, client):
        reply = _post(client, "Lannes and Murat, scout Tyrol")
        assert "Murat, scout Tyrol" in reply["message"]
        assert reply.get("dropped_sequel") == "Murat, scout Tyrol"

    @pytest.mark.parametrize("line,target", [
        ("Soult, take Lyonnais back from Paget", "Lyonnais"),
        ("Napoleon, return to Paris", "Paris"),
        ("Ney, keep going to Provence", "Provence"),
        ("Ney, take Provence back", "Provence"),
    ])
    def test_d37_the_common_phrasings(self, client, line, target):
        reply = _post(client, line)
        parsed = _parsed(reply)
        assert parsed.get("target") == target and parsed.get("action") in ("move", "attack"), (line, parsed)

    def test_d38_the_arrival_sequel_is_named_not_silent(self, client):
        reply = _post(client, "Soult, march to Burgundy and then fortify")
        assert "waits behind it" in reply["message"]
        assert "Give it when he arrives" in reply["message"]

    def test_d41_asked_for_cavalry_told_of_infantry(self, client):
        def rich(world):
            world.gold = 50_000
        reply = _post(client, "Soult, recruit cavalry", stage=rich)
        assert "infantry" in reply["message"].lower()
        assert "cavalry" in reply["message"].lower() or "commands infantry" in reply["message"]

    @pytest.mark.parametrize("line,action", [
        ("Let the Guard attack Mack", "attack"),
        ("The Guard will support Soult.", "move"),
        ("the guard stays put", "wait"),
        ("Have the Guard dig in.", "fortify"),
    ])
    def test_the_guard_as_a_subject_is_the_emperors_corps(self, client, line, action):
        reply = _post(client, line)
        assert "rewrite_guard_subject" in _rules(reply, "parser")
        parsed = _parsed(reply)
        assert parsed.get("marshal") == "Napoleon" and parsed.get("action") == action, parsed

    def test_chase_him_down_is_a_pursuit(self, client):
        reply = _post(client, "Davout, chase Mack down wherever he runs")
        assert _parsed(reply).get("strategic_type") == "PURSUE"
        assert "Mack Down" not in reply["message"]

    def test_fall_on_his_flank_is_an_attack_and_the_second_half_rides(self, client):
        reply = _post(client, "Ney, fall on Mack's flank; Murat, charge his centre")
        parsed = _parsed(reply)
        assert parsed.get("marshal") == "Ney" and parsed.get("action") == "attack" and parsed.get("target") == "Mack"
        assert "Murat" in str(reply.get("dropped_sequel") or "")
