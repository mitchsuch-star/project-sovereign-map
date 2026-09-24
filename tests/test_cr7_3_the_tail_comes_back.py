"""CR-7-3 — "Nothing is dropped in silence, and the tail comes back."

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-3 (+ CQ-10, the bare comma). Reproduced on this HEAD before a line
was written (September 22, 2026):

* `Ney, march to Karaman, then Davout, fortify` — "Cannot enter Karaman"
  and NOT ONE WORD about Davout; `dropped_sequel` absent from the wire.
* `Ney, fortify then attack Mack` → objection → `insist` / `trust` /
  `compromise`: the note re-surfaced on 0 of 3 arms (the production
  comment at the drop site claimed it would).
* `dropped_sequel`: 8 producers, 0 consumers, absent from every response.
* `Ney, march to Swabia then attack Mack then fortify` — the third clause
  lost in silence. `Ney, fortify, attack Mack` — the FIFTH tail form, still
  swallowed (action=attack); `Ney, march to Swabia, attack Mack` — the
  arrival silently gone (CQ-10).

The rules are `SYSTEMS_REFERENCE.md` §4 Stage 2c; the module is
`backend/commands/relay.py`. Every pin below drives the real `POST /command`
(or the answer endpoints) on the shipped 1805 boot with a mock parser — the
golden corpus reports green in both arms of every fix in this row.
"""

import re
import os
import random as _random

import pytest
from fastapi.testclient import TestClient

import backend.main as M
import backend.commands.objection_v2 as objection_v2
from backend.commands import relay
from backend.commands.parser import CommandParser, sequel_note

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


@pytest.fixture
def steady_temper(monkeypatch):
    """The V2a trigger's ONE source of randomness rolls a ±1 concern shift
    25% of the time; a roll of 0.5 is 'exactly as evaluated', so an
    aggressive marshal's objection to sitting idle fires every time."""
    monkeypatch.setattr(objection_v2.random, "random", lambda: 0.5)


def run(shipped, command, **extra):
    client, _world = shipped
    return client.post("/command", json={"command": command, **extra}).json()


def relay_keys(reply):
    return {k: reply.get(k) for k in ("dropped_sequel", "relay_kind", "relay_command")}


# ═══════════════════════════════════════════════════════════════════════
# The 14-shape battery — the tail is reported on EVERY arm
# ═══════════════════════════════════════════════════════════════════════

BATTERY = [
    # (command, tail, kind)
    ("Davout, fortify then attack Mack", "attack Mack", "contradiction"),
    ("Davout, scout Swabia, then fortify", "fortify", "ready"),
    ("Davout, move to Lorraine, then fortify", "fortify", "ready"),
    ("Soult, march to Bordelais, then fortify", "fortify", "moment"),
    ("Davout, form square, then attack Mack", "attack Mack", "contradiction"),
    ("Davout, defend, then attack Mack", "attack Mack", "contradiction"),
    ("Davout, hold Lorraine until Ney arrives, then fortify", "fortify", "contradiction"),
    ("Ney, march to Karaman, then Davout, fortify", "Davout, fortify", "refused_head"),
    ("Ney, scout Swabia, then Davout, fortify", "Davout, fortify", "ready"),
    ("Davout, unfortify, then attack Mack", "attack Mack", "refused_head"),
    ("Davout, drill, then attack Mack", "attack Mack", "refused_head"),
    ("Ney, march to Swabia then attack Mack then fortify", "fortify", "question"),
    ("Davout, fortify, attack Mack", "attack Mack", "contradiction"),
    ("Talleyrand, propose peace with Austria, then attack Bern", "attack Bern", "question"),
]


class TestTheFourteenShapes:

    @pytest.mark.parametrize("command,tail,kind", BATTERY)
    def test_the_tail_is_reported_with_its_verdict(self, shipped, command, tail, kind):
        reply = run(shipped, command)
        assert reply.get("dropped_sequel") == tail, relay_keys(reply)
        assert reply.get("relay_kind") == kind, (relay_keys(reply), reply.get("message"))
        assert reply.get("relay_kind") in relay.RELAY_KINDS
        assert f'"{tail}"' in (reply.get("message") or ""), reply.get("message")

    def test_fourteen_of_fourteen(self, shipped):
        """The contract's number, as one census over the battery above."""
        seen = 0
        for command, tail, _kind in BATTERY:
            M._reset_world_state()
            reply = run(shipped, command)
            if reply.get("dropped_sequel") == tail and reply.get("relay_note"):
                seen += 1
        assert seen == len(BATTERY) == 14

    @pytest.mark.parametrize("command", [c for c, _t, k in BATTERY if k != "ready"])
    def test_only_ready_hands_the_line_back(self, shipped, command):
        """`relay_command` is ABSENT — not null — on every other kind, which
        is what makes the client's fill impossible there."""
        reply = run(shipped, command)
        assert "relay_command" not in reply, relay_keys(reply)

    @pytest.mark.parametrize("command,tail,expected_line", [
        ("Davout, scout Swabia, then fortify", "fortify", "Davout, fortify"),
        ("Davout, move to Lorraine, then fortify", "fortify", "Davout, fortify"),
        ("Ney, scout Swabia, then Davout, fortify", "Davout, fortify", "Davout, fortify"),
    ])
    def test_ready_re_addresses_the_tail_for_the_seal(self, shipped, command, tail, expected_line):
        reply = run(shipped, command)
        assert reply.get("relay_command") == expected_line, relay_keys(reply)
        assert "on the line" in (reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════
# The user's note: "fortify and attack is a contradiction"
# ═══════════════════════════════════════════════════════════════════════

class TestTheContradictionIsNamedNotInvited:

    def test_fortify_then_attack_names_the_works(self, shipped):
        reply = run(shipped, "Davout, fortify then attack Mack")
        assert M.world.get_marshal("Davout").fortified is True
        assert reply["relay_kind"] == "contradiction"
        assert "abandons the works" in reply["relay_note"]
        assert "relay_command" not in reply
        assert "must follow as its own command" not in (reply.get("message") or "")

    def test_a_standing_hold_names_the_hold(self, shipped):
        reply = run(shipped, "Davout, hold Lorraine until Ney arrives, then fortify")
        assert reply["relay_kind"] == "contradiction"
        assert "end his standing hold" in reply["relay_note"]

    def test_the_moment_names_the_destination_and_the_eta(self, shipped):
        reply = run(shipped, "Soult, march to Bordelais, then fortify")
        soult = M.world.get_marshal("Soult")
        assert soult.strategic_order is not None
        assert reply["relay_kind"] == "moment"
        assert "Bordelais" in reply["relay_note"]
        assert re.search(r"\d+ turns?\b", reply["relay_note"]), reply["relay_note"]  # F2 LV-9
        assert "relay_command" not in reply

    def test_a_tactical_move_that_completes_now_is_ready(self, shipped):
        """The reverse pair is coherent: fortify AT the new province."""
        reply = run(shipped, "Davout, move to Lorraine, then fortify")
        assert M.world.get_marshal("Davout").location == "Lorraine"
        assert reply["relay_kind"] == "ready"
        assert reply["relay_command"] == "Davout, fortify"

    def test_the_refused_head_cancels_the_tail(self, shipped):
        """Rule 4: the tail is never promoted to a new head."""
        _client, world = shipped
        davout_before = world.get_marshal("Davout").fortified
        reply = run(shipped, "Ney, march to Karaman, then Davout, fortify")
        assert reply.get("success") is False
        assert reply["relay_kind"] == "refused_head"
        assert "did not go out" in reply["relay_note"]
        assert '"Davout, fortify"' in reply["message"]
        assert M.world.get_marshal("Davout").fortified == davout_before


# ═══════════════════════════════════════════════════════════════════════
# The question arms — the tail waits, then comes back re-judged
# ═══════════════════════════════════════════════════════════════════════

class TestTheObjectionArm:

    @pytest.mark.parametrize("answer,kind", [
        ("insist", "contradiction"),   # he fortifies as ordered → attack would undo it
        ("trust", "ready"),            # he does his own thing → nothing to undo
        ("compromise", "ready"),
    ])
    def test_the_tail_is_reported_after_each_answer(self, shipped, steady_temper, answer, kind):
        first = run(shipped, "Ney, fortify then attack Mack")
        assert first.get("pending_objection"), first.get("message")
        assert first["relay_kind"] == "question"
        assert first["dropped_sequel"] == "attack Mack"
        assert M.world._pending_relay is not None
        reply = run(shipped, answer)
        assert reply.get("dropped_sequel") == "attack Mack", relay_keys(reply)
        assert reply.get("relay_kind") == kind, (relay_keys(reply), reply.get("message"))
        assert '"attack Mack"' in (reply.get("message") or "")
        assert M.world._pending_relay is None

    def test_the_popup_route_carries_it_too(self, shipped, steady_temper):
        client, _world = shipped
        first = run(shipped, "Ney, fortify then attack Mack")
        assert first.get("pending_objection")
        reply = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert reply.get("dropped_sequel") == "attack Mack", relay_keys(reply)
        assert reply.get("relay_kind") == "contradiction"

    def test_the_question_kind_fills_nothing(self, shipped, steady_temper):
        first = run(shipped, "Ney, fortify then attack Mack")
        assert "relay_command" not in first
        assert "waits behind the question" in first["relay_note"]


class TestTheInterruptArm:

    def test_the_tail_waits_behind_the_bad_odds_question(self, shipped):
        client, _world = shipped
        first = run(shipped, "Ney, march to Swabia then attack Mack then fortify")
        assert first.get("pending_interrupt"), first.get("message")
        assert first["relay_kind"] == "question"
        interrupt = first["pending_interrupt"]
        reply = client.post("/strategic_response", json={
            "marshal_name": "Ney", "response_type": interrupt["interrupt_type"],
            "choice": "attack_anyway"}).json()
        assert reply.get("dropped_sequel") == "fortify", relay_keys(reply)
        assert reply.get("relay_kind") in ("moment", "ready", "contradiction")
        assert '"fortify"' in (reply.get("message") or "")


class TestTheClarificationArm:

    def test_the_tail_waits_behind_the_which_marshal_question(self, shipped):
        """The CR-2 clarifications are built OUTSIDE the executor result, so
        the first cut reported nothing on this arm (measured: `march to
        Lorraine, then fortify` asked "Which marshal?" with no relay key)."""
        first = run(shipped, "march to Lorraine, then fortify")
        assert first.get("state") == "awaiting_clarification", first.get("message")
        assert first.get("relay_kind") == "question", relay_keys(first)
        assert first.get("dropped_sequel") == "fortify"
        assert "relay_command" not in first
        assert '"fortify"' in (first.get("message") or "")
        assert M.world._pending_relay is not None

    def test_the_reissue_re_derives_the_tail(self, shipped):
        """A which-marshal clarification reissues the WHOLE compound, so
        the tail is parsed again and re-judged (the march is multi-turn:
        the tail is held for its moment)."""
        first = run(shipped, "march to Lorraine, then fortify")
        assert first.get("state") == "awaiting_clarification"
        reply = run(shipped, "Davout")
        assert reply.get("success") is True, reply.get("message")
        assert reply.get("dropped_sequel") == "fortify", relay_keys(reply)
        assert reply.get("relay_kind") == "moment", relay_keys(reply)
        assert M.world._pending_relay is None

    def test_the_did_you_mean_arm_carries_it_too(self, shipped):
        """`Grouchy` is not on the 1805 board (a one-key slip like `Davut`
        is auto-corrected and never asks), so the addressee question fires
        — and it used to fire with the fortify lost in silence."""
        first = run(shipped, "Grouchy, scout Swabia, then fortify")
        assert first.get("state") == "awaiting_clarification", first.get("message")
        assert first.get("relay_kind") == "question", relay_keys(first)
        assert first.get("dropped_sequel") == "fortify"
        assert '"fortify"' in (first.get("message") or "")
        reply = run(shipped, "Davout")
        assert reply.get("success") is True, reply.get("message")
        assert reply.get("relay_kind") == "ready", relay_keys(reply)
        assert reply.get("relay_command") == "Davout, fortify"

    def test_a_marshal_less_head_re_addresses_to_the_man_who_acted(self, shipped):
        """`scout Swabia, then fortify` is executed by whoever the executor
        chose (the actor rides the first event, not the response); the
        relayed tail names HIM rather than arriving bare."""
        reply = run(shipped, "scout Swabia, then fortify")
        assert reply.get("success") is True, reply.get("message")
        actor = (reply.get("events") or [{}])[0].get("marshal")
        assert actor and M.world.get_marshal(actor).nation == "France", reply.get("events")
        assert reply.get("relay_kind") == "ready"
        assert reply.get("relay_command") == f"{actor}, fortify"
        assert (reply.get("message") or "").startswith(actor)


# ═══════════════════════════════════════════════════════════════════════
# The stash — one command's life, never serialized
# ═══════════════════════════════════════════════════════════════════════

class TestTheStashLifetime:

    def test_an_unrelated_command_supersedes_it(self, shipped, steady_temper):
        run(shipped, "Ney, fortify then attack Mack")
        assert M.world._pending_relay is not None
        reply = run(shipped, "status")
        assert M.world._pending_relay is None
        assert "dropped_sequel" not in reply

    def test_the_turn_boundary_clears_it(self, shipped, steady_temper):
        run(shipped, "Ney, fortify then attack Mack")
        assert M.world._pending_relay is not None
        M.world.advance_turn()
        assert M.world._pending_relay is None

    def test_it_is_not_serialized(self, shipped, steady_temper):
        """The integrity check the contract insists on: a serialized relay
        would be the cross-turn queue wearing a disguise (CR-7-8)."""
        run(shipped, "Ney, fortify then attack Mack")
        assert M.world._pending_relay is not None
        assert "_pending_relay" not in M.world.to_dict()
        assert "pending_relay" not in M.world.to_dict()

    def test_load_game_does_not_resurrect_it(self, shipped, steady_temper, tmp_path):
        from backend.save_manager import load_game, save_game
        run(shipped, "Ney, fortify then attack Mack")
        assert M.world._pending_relay is not None
        path = tmp_path / "relay.json"
        saved = save_game(M.world, "relay", filepath=path)
        assert saved["success"], saved
        loaded = load_game(path)
        assert loaded["success"], loaded
        assert getattr(loaded["world"], "_pending_relay", "MISSING") is None

    def test_the_stash_is_created_only_by_a_question(self, shipped):
        run(shipped, "Davout, scout Swabia, then fortify")
        assert M.world._pending_relay is None


# ═══════════════════════════════════════════════════════════════════════
# CQ-10 — the bare comma, with its negative controls
# ═══════════════════════════════════════════════════════════════════════

class TestTheBareComma:

    def test_the_fifth_form_no_longer_swallows(self, shipped):
        _client, world = shipped
        davout = world.get_marshal("Davout")
        location, strength = davout.location, davout.strength
        reply = run(shipped, "Davout, fortify, attack Mack")
        assert reply.get("success") is True, reply.get("message")
        assert not reply.get("battle_report")
        davout = M.world.get_marshal("Davout")
        assert davout.fortified is True
        assert (davout.location, davout.strength) == (location, strength)
        assert reply.get("dropped_sequel") == "attack Mack"

    def test_the_comma_arrival_keeps_the_attack(self, shipped):
        reply = M.parser.parse("Ney, march to Swabia, attack Mack",
                               M.get_llm_game_state(), world=M.world)
        assert reply.get("strategic_type") == "MOVE_TO"
        assert reply.get("attack_on_arrival") is True
        assert reply.get("dropped_sequel") is None

    @pytest.mark.parametrize("command", [
        "Ney, attack Mack",                    # the address comma
        "Ney, Davout, attack Mack",            # a list of addressees
        "Ney and Davout, attack Mack",         # FA-50's address form
        "Marshal Ney, attack Mack",            # the honorific
    ])
    def test_the_address_comma_is_never_a_boundary(self, shipped, command):
        reply = M.parser.parse(command, M.get_llm_game_state(), world=M.world)
        assert reply.get("success"), reply
        assert reply["command"]["action"] == "attack"
        assert reply["command"]["target"] == "Mack"
        assert reply.get("dropped_sequel") is None

    def test_the_muster_control_is_re_measured(self, shipped):
        """FA-50's pin, re-taken here rather than trusted: the address form
        still musters both, with no note."""
        reply = run(shipped, "Ney and Davout, attack Mack")
        assert reply.get("battle_report"), reply.get("message")
        assert "One order at a time" not in (reply.get("message") or "")

    def test_a_diplomatic_head_is_never_split_at_its_address(self, shipped):
        """Talleyrand alone opens the nation picker, so `fast_parse` is not
        `unknown` for him — the FA-50 gate alone would have split
        `Talleyrand, build rapport with Saxony` into a picker and a dropped
        mission (measured on the corpus)."""
        reply = M.parser.parse("Talleyrand, build rapport with Saxony",
                               M.get_llm_game_state(), world=M.world)
        assert reply.get("success"), reply
        diplo = reply["command"].get("diplomatic_data") or {}
        assert diplo.get("target_nation") == "Saxony", diplo
        assert reply.get("dropped_sequel") is None

    def test_a_unit_whose_name_is_a_verb_is_not_a_head(self, shipped):
        reply = run(shipped, "the Guard, attack Mack")
        assert "Berthier" in (reply.get("message") or "")
        assert reply.get("dropped_sequel") is None

    def test_a_refused_whole_sentence_is_not_split(self, shipped):
        """`should Mack advance, fortify` is the inversion the guards refuse;
        splitting it would execute a clause of a conditional order."""
        reply = run(shipped, "Ney, should Mack advance, fortify")
        assert reply.get("success") is False
        assert M.world.get_marshal("Ney").fortified is False
        assert reply.get("dropped_sequel") is None

    def test_a_leading_filler_is_not_a_head(self, shipped):
        """FA-R3's own pin, re-taken: `Ney, wait, march to Lorraine` is a
        2-AP standing march — the `wait,` is WO-6's interjection, not a
        head. The first cut of the comma arm split it into a free wait and
        a dropped march (found by the full suite, September 22, 2026)."""
        _client, world = shipped
        ap = world.actions_remaining
        reply = run(shipped, "Ney, wait, march to Lorraine")
        assert reply.get("success") is True, reply.get("message")
        assert reply.get("dropped_sequel") is None, relay_keys(reply)
        assert M.world.get_marshal("Ney").strategic_order is not None
        assert ap - M.world.actions_remaining == 2

    @pytest.mark.parametrize("command", [
        "no wait, Ney, retreat",
        "hold on, Davout, fortify",
    ])
    def test_the_other_filler_shapes_stay_whole(self, shipped, command):
        reply = M.parser.parse(command, M.get_llm_game_state(), world=M.world)
        assert reply.get("success"), reply
        assert reply.get("dropped_sequel") is None

    def test_emphasis_is_one_order(self, shipped):
        reply = M.parser.parse("Ney, attack Mack, charge!",
                               M.get_llm_game_state(), world=M.world)
        assert reply["command"]["action"] == "attack"
        assert reply.get("dropped_sequel") is None

    def test_a_third_clause_behind_the_arrival_is_reported(self, shipped):
        reply = M.parser.parse("Ney, march to Swabia then attack Mack then fortify",
                               M.get_llm_game_state(), world=M.world)
        assert reply.get("strategic_type") == "MOVE_TO"
        assert reply.get("attack_on_arrival") is True
        assert reply.get("dropped_sequel") == "fortify"


# ═══════════════════════════════════════════════════════════════════════
# The wording, the instrument, the AI
# ═══════════════════════════════════════════════════════════════════════

class TestTheWordsAndTheRecord:

    def test_the_parser_sentence_no_longer_invites_a_resend(self):
        note = sequel_note("attack Mack")
        assert "One order at a time" in note
        assert '"attack Mack"' in note
        assert "must follow as its own command" not in note

    def test_a_relayed_send_is_recorded_on_the_history(self, shipped):
        run(shipped, "Davout, fortify", relayed=True)
        assert M.world.command_history[-1].get("relayed") is True
        run(shipped, "Davout, unfortify")
        assert "relayed" not in M.world.command_history[-1]

    def test_the_ai_never_sees_a_relay(self, shipped):
        """GR5 by construction: the stash is written only by the player's
        own /command; an AI turn plants nothing."""
        _client, world = shipped
        from backend.game_logic.turn_manager import TurnManager  # noqa: F401
        run(shipped, "end turn")
        assert M.world._pending_relay is None

    def test_the_client_fills_at_the_one_chokepoint(self):
        """The Godot half, pinned by reading the source: the fill rides
        `set_input_enabled(true)`, the stash is taken on all three response
        roads, and the send flags an unchanged relay."""
        path = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        assert "func _stash_relay(" in src and "func _fill_pending_relay(" in src
        assert src.count("_stash_relay(response)") >= 3
        enable = src[src.index("func set_input_enabled"):src.index("func _show_objection_dialog")]
        assert "_fill_pending_relay()" in enable
        send = src[src.index("func _execute_command"):]
        send = send[:send.index("\nfunc ", 10)]
        assert "api_client.send_command(command, _on_command_result, relayed)" in send
        api = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                           "scripts", "api_client.gd")
        with open(api, encoding="utf-8") as handle:
            assert 'body["relayed"] = true' in handle.read()


class TestNothingReachesTheEngine:
    """CR-7-3 is a parser / response slice: the AI types nothing, so the
    ambient board cannot move. `strategic.pick_contact_enemy` (CR-7-6) is
    the only executor change in this row and it is pinned in its own file."""

    def test_no_new_serialized_world_field(self):
        from backend.models.world_state import WorldState
        keys = set(WorldState(player_nation="France").to_dict())
        assert not any("relay" in k for k in keys), sorted(k for k in keys if "relay" in k)
