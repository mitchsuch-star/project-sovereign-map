"""First contact — the keyless player's first ten minutes (September 23, 2026).

The keyless first-contact report drove 92 wild sentences at the shipped fast
parser and found ONE canned reply fitting everything: `hello`, `quit`,
`undo`, `what now`, `I'm stuck` and `win the war` all drew "Forgive me, Sire,
but I cannot interpret that order" — a reply that never names `help`, `what
can I do` or `status`, never points `quit` / `restart` / `undo` at the pause
menu, and (its one suggestion) proposed `Ney, move to London` — a march the
Royal Navy shuts at the Channel, which the tactical `move to` road then
ACCEPTED and walked to Normandy to stall. `build a tank` was answered with an
example province that is not on the map; `destroy Austria` fuzzy-matched its
own verb into the Bavarian marshal Deroy; `how many men do I have` and `is
Mack strong` reached no desk. Every claim was reproduced at the real
`POST /command` on the shipped 1805 boot before a line was written.

ONE source, `backend/ai/first_contact.py`, for the vocabulary the parser
routes on and the copy the help executor prints; the counsel stays the ONE
`ai/counsel.what_can_i_do`; the road law stays `strategic.plot_route` +
`issuance_road_refusal`, now read by the tactical belt too.

Every endpoint pin below reads the WORLD (action points, every marshal's
ground and strength, the dialogue slot) as well as the message: nothing the
desk says may cost a point or move a man.
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.first_contact as FC
import backend.main as M
from backend.ai.attack_vocabulary import guard_attack_verb_forms
from backend.ai.first_contact import (THREE_DOORS, answer_first_contact,
                                      first_contact_route)
from backend.ai.question_desk import classify_board_question, classify_question
from backend.commands.parser import CommandParser
from backend.commands.strategic import issuance_road_refusal, plot_route


# ═══════════════════════════════════════════════════════════════════════
# The board
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams with a mock parser (the
    CR-7-1 idiom). The suite pins `SOVEREIGN_SCENARIO=none`; these rows need
    Ney at Rhineland, Mack at Swabia and the Royal Navy in the Channel."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def snapshot(world):
    out = {
        "ap": int(world.actions_remaining),
        "admin": int(getattr(world, "admin_actions_remaining", 0)),
        "gold": int(world.gold),
        "dp": int(world.diplomatic_points),
        "dialogue": (world.pending_diplomatic_dialogue or {}).get("type"),
    }
    for m in world.marshals.values():
        out["m:" + m.name] = (m.location, int(m.strength),
                              bool(getattr(m, "strategic_order", None)))
    return out


def say(client, world, sentence):
    """POST the sentence; assert the board did not move; return the reply."""
    before = snapshot(world)
    reply = post(client, sentence)
    after = snapshot(world)
    moved = {k: (before.get(k), after.get(k)) for k in set(before) | set(after)
             if before.get(k) != after.get(k)}
    assert not moved, (sentence, moved)
    return reply


# ═══════════════════════════════════════════════════════════════════════
# 1. The greeting
# ═══════════════════════════════════════════════════════════════════════

class TestTheGreeting:
    @pytest.mark.parametrize("line", ["hello", "hi", "Good morning", "bonjour Berthier",
                                      "hey there", "Berthier", "Berthier?",
                                      "how are you"])
    def test_a_greeting_is_answered_with_the_three_doors(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        assert "Berthier bows" in msg, msg
        for door in ("'what can I do'", "'status'", "'help'", "F1", "Esc"):
            assert door in msg, (door, msg)
        assert "cannot interpret" not in msg

    def test_the_greeting_quotes_the_counsel_of_the_morning(self, shipped):
        client, world = shipped
        msg = say(client, world, "hello")["message"]
        assert "would be carried out at once" in msg
        # the order quoted is the SAME first line 'what can I do' prints
        options = say(client, world, "what can I do")["message"]
        first = options.split("\n")[1].strip()
        assert first and first in msg, (first, msg)


# ═══════════════════════════════════════════════════════════════════════
# 2. The pause menu is named
# ═══════════════════════════════════════════════════════════════════════

class TestThePauseMenuIsNamed:
    @pytest.mark.parametrize("line", ["quit", "exit", "quit game", "restart", "menu",
                                      "main menu", "options", "settings", "new game",
                                      "start over", "pause", "load game",
                                      "how do I save", "I give up", "Berthier, quit",
                                      "resign", "volume", "fullscreen"])
    def test_a_word_for_the_pause_menu_points_at_esc(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        assert "press Esc" in msg, msg
        assert "Nothing has been relayed" in msg
        assert "cannot interpret" not in msg

    def test_save_and_load_keep_their_literal_meaning(self, shipped):
        """The desk never stands in front of the executor's own meta-commands:
        `save game` SAVES and a bare `load` lists the saves, as before."""
        client, world = shipped
        saved = post(client, "save game")
        assert saved["success"] is True and "saved" in saved["message"].lower(), saved
        listed = post(client, "load")
        assert "saves" in listed["message"].lower(), listed

    def test_the_route_declines_the_literal_meta_prefixes(self):
        for line in ("save", "save game", "save my game", "load", "debug gold",
                     "/debug marshals"):
            assert first_contact_route(line) is None, line


# ═══════════════════════════════════════════════════════════════════════
# 3. Undo is honest
# ═══════════════════════════════════════════════════════════════════════

class TestUndoIsHonest:
    @pytest.mark.parametrize("line", ["undo", "undo that", "can I undo that",
                                      "go back", "take that back", "oops",
                                      "I didn't mean that", "revert"])
    def test_there_is_no_unsaying_an_order(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        assert "no unsaying an order" in msg, msg
        assert "Esc" in msg and "Nothing has been relayed" in msg

    def test_a_standing_order_is_named_as_the_one_thing_that_can_be_stood_down(self, shipped):
        client, world = shipped
        marched = post(client, "Ney, march to Lorraine")
        assert marched["success"] is True, marched
        assert world.get_marshal("Ney").strategic_order is not None
        msg = say(client, world, "undo")["message"]
        assert "'cancel Ney'" in msg, msg

    def test_an_addressed_go_back_is_the_marshals_order_not_the_desks(self, shipped):
        """`Ney, go back` is an order to a marshal (the address is his name,
        not the desk's) and never reaches the undo answer."""
        client, world = shipped
        reply = post(client, "Ney, go back")
        assert "no unsaying" not in str(reply.get("message", ""))
        assert first_contact_route("Ney, go back") is None


# ═══════════════════════════════════════════════════════════════════════
# 4. The stuck player gets the counsel
# ═══════════════════════════════════════════════════════════════════════

class TestTheStuckPlayerGetsTheCounsel:
    @pytest.mark.parametrize("line", ["what now", "now what", "what next", "I'm stuck",
                                      "im stuck", "I am lost", "no idea what to do",
                                      "any suggestions", "advise me", "help me",
                                      "I don't know", "what do I do", "what to do",
                                      "?", "idk", "what would you do",
                                      "Berthier, what now?"])
    def test_a_stuck_phrasing_reaches_the_options_desk(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        assert msg.startswith("These orders would be carried out today, Sire:"), msg
        assert "Ney, attack Mack" in msg, msg
        assert "cannot interpret" not in msg and "cannot answer that" not in msg

    def test_the_options_desk_and_the_typed_question_are_one_answer(self, shipped):
        client, world = shipped
        assert (say(client, world, "what now")["message"]
                == say(client, world, "what can I do")["message"])

    def test_bare_help_keeps_the_command_reference(self, shipped):
        client, world = shipped
        msg = say(client, world, "help")["message"]
        assert "COMMAND REFERENCE" in msg
        assert "Lyon" not in msg, "the manual's example province must be on the map"
        assert "repair Lorraine" in msg

    def test_a_question_about_a_named_foe_is_not_a_stuck_phrasing(self):
        """`what do I do about Mack` carries a subject; the desk's anchored
        vocabulary does not swallow it (it keeps its routed answer)."""
        assert first_contact_route("what do I do about Mack") is None
        assert first_contact_route("what should I do with Ney") is None


# ═══════════════════════════════════════════════════════════════════════
# 5. The goal of the game
# ═══════════════════════════════════════════════════════════════════════

class TestTheGoal:
    @pytest.mark.parametrize("line", ["win the war", "how do I win", "how do we win the war",
                                      "what is the goal", "what am I supposed to do",
                                      "how does this work", "how do I play"])
    def test_the_goal_is_answered_in_a_sentence_not_the_manual(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        assert "COMMAND REFERENCE" not in msg, msg
        # ⚑ GE-1 (Sept 25, 2026) — CONSCIOUS FLIP: the shipped 1805 campaign
        # now ARMS its endings, so "how do I win" names the Verdict and the
        # Fall (GAME_END_SPEC R7 re-pointed `_is_open_ended`); "open-ended"
        # stays the answer on the bare flag world and the tutorial.
        assert "open-ended" not in msg, msg
        assert "Verdict" in msg and "can fall" in msg and "press T" in msg, msg
        assert "Today:" in msg and "'Ney, attack Mack'" in msg, msg
        assert THREE_DOORS in msg

    def test_the_open_ended_line_reads_the_worlds_own_flag(self):
        """The day the Victory Pass lands, `sandbox_mode` turns false and the
        answer turns honest by itself — no copy to remember."""
        class _World:
            sandbox_mode = False
            player_nation = "France"

            def get_player_marshals(self):
                return []

        msg = answer_first_contact("goal", "how do I win", _World())
        assert "open-ended" not in msg
        assert "objectives are on the Strategic Ledger" in msg


# ═══════════════════════════════════════════════════════════════════════
# 6. The shrug names its doors
# ═══════════════════════════════════════════════════════════════════════

class TestTheShrugNamesItsDoors:
    def test_a_line_nobody_can_read_still_names_the_three_doors(self, shipped):
        client, world = shipped
        for line in ("flibbertigibbet the wombat", "purple monkey dishwasher",
                     "asdfgh", "resupply the zeppelins"):
            reply = say(client, world, line)
            msg = reply["message"]
            for door in ("'what can I do'", "'status'", "'help'", "F1"):
                assert door in msg, (line, door, msg)

    def test_the_marshal_only_shrug_names_the_capital_of_the_board(self, shipped):
        """'move to Paris' was hard-coded; the example is the player's
        capital, read from the world."""
        from backend.ai.llm_client import _home_example

        client, world = shipped
        assert _home_example({"world": world}) == world.get_nation_capital("France")

        class _Elsewhere:
            player_nation = "France"

            def get_nation_capital(self, nation):
                return "Strasbourg"

        assert _home_example({"world": _Elsewhere()}) == "Strasbourg"
        assert _home_example({}) == "Paris"


# ═══════════════════════════════════════════════════════════════════════
# 7. The place suggestion reads the road
# ═══════════════════════════════════════════════════════════════════════

class TestThePlaceSuggestionReadsTheRoad:
    def test_a_place_across_the_water_is_never_offered_as_a_march(self, shipped):
        client, world = shipped
        reply = say(client, world, "send the submarines to London")
        msg = reply["message"]
        assert "move to London" not in msg and "attack London" not in msg, msg
        assert "Royal Navy" in msg, msg
        assert "THE ADMIRALTY" in msg and "press T, then 7" in msg, msg
        assert THREE_DOORS in msg

    def test_a_reachable_hostile_place_names_the_corps_with_the_shortest_road(self, shipped):
        client, world = shipped
        reply = say(client, world, "nuke Vienna")
        msg = reply["message"]
        assert "move to Vienna" in msg and "attack Vienna" in msg, msg
        # the man named has a LAWFUL road — the executor's own verdict
        import re
        who = re.search(r"try '([^,]+), move to Vienna'", msg)
        assert who, msg
        marshal = world.get_marshal(who.group(1))
        assert marshal is not None and marshal.nation == "France", who.group(1)
        road, verdict = plot_route(world, marshal, "Vienna", use_weighted=True,
                                   want_verdict=True)
        assert road and issuance_road_refusal(world, marshal, "Vienna", "MOVE_TO",
                                              verdict) is None

    def test_a_place_of_a_court_at_peace_is_never_offered_as_an_attack(self, shipped):
        """Berlin is Prussia's, and France is at peace with Prussia."""
        client, world = shipped
        assert not world.is_at_war("France", "Prussia")
        msg = say(client, world, "nuke Berlin")["message"]
        assert "attack Berlin" not in msg, msg

    def test_a_cold_parse_keeps_the_old_templates(self):
        from backend.ai.llm_client import _place_suggestion
        assert _place_suggestion({}, "London") is None
        assert _place_suggestion(None, "London") is None


# ═══════════════════════════════════════════════════════════════════════
# 8. A verb is never a place
# ═══════════════════════════════════════════════════════════════════════

class TestAVerbIsNeverAPlace:
    @pytest.mark.parametrize("line,nation", [("destroy Austria", "Austria"),
                                             ("destroy Prussia", "Prussia"),
                                             ("crush Austria", "Austria"),
                                             ("smash Prussia", "Prussia")])
    def test_destroy_a_nation_reaches_the_nation_refusal(self, shipped, line, nation):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is False
        msg = reply["message"]
        assert f"{nation} is a nation" in msg, msg
        assert "Bavaria" not in msg and "Deroy" not in msg, msg

    def test_the_verb_forms_cover_the_inflections(self):
        forms = guard_attack_verb_forms()
        for word in ("destroy", "destroys", "destroyed", "destroying", "crush",
                     "crushes", "crushing", "smash", "smashed", "annihilate",
                     "annihilated", "annihilating", "march", "marching", "take",
                     "taking", "hit", "occupy", "occupied"):
            assert word in forms, word

    def test_a_named_enemy_still_musters(self, shipped):
        """Control: the skip list touches the TARGET scan only — `annihilate
        Mack` is still an attack on Mack."""
        client, world = shipped
        reply = post(client, "annihilate Mack")
        assert reply["success"] is True, reply
        assert "Mack" in reply["message"]


# ═══════════════════════════════════════════════════════════════════════
# 9. The example province is on the map
# ═══════════════════════════════════════════════════════════════════════

class TestTheExampleProvinceIsOnTheMap:
    def test_build_with_no_region_names_the_capital(self, shipped):
        client, world = shipped
        reply = post(client, "build a tank")
        msg = reply["message"]
        assert "Lyon" not in msg, msg
        capital = world.get_nation_capital("France")
        assert f"build supply depot at {capital}" in msg, msg
        assert capital in world.regions

    def test_repair_with_no_region_names_the_capital(self, shipped):
        from backend.commands.economy_executor import example_region
        client, world = shipped
        assert example_region(world) == world.get_nation_capital("France")
        reply = M.executor.execute(
            {"success": True, "command": {"action": "repair", "target": None,
                                          "raw_command": "repair"}},
            {"world": world})
        assert reply["success"] is False
        assert f"repair {world.get_nation_capital('France')}" in reply["message"]


# ═══════════════════════════════════════════════════════════════════════
# 10. The army answers
# ═══════════════════════════════════════════════════════════════════════

class TestTheArmyAnswers:
    @pytest.mark.parametrize("line", ["how many men do I have", "how many men do we have",
                                      "how big is my army", "how strong is my army",
                                      "what forces do we have", "how many marshals do I have",
                                      "where is my army", "is my army strong"])
    def test_the_whole_army_is_one_return(self, shipped, line):
        client, world = shipped
        reply = say(client, world, line)
        assert reply["success"] is True, reply
        msg = reply["message"]
        fielded = [m for m in world.get_player_marshals()
                   if int(m.strength) > 0 and not getattr(m, "captured_by", "")]
        total = sum(int(m.strength) for m in fielded)
        assert f"Our army stands at {total:,} men under {len(fielded)} marshals" in msg, msg
        strongest = max(fielded, key=lambda m: int(m.strength))
        assert f"{int(strongest.strength):,} at {strongest.location}" in msg, msg
        assert "press T" in msg

    @pytest.mark.parametrize("line", ["is Mack strong", "is Mack strong?",
                                      "is Mack dangerous", "Berthier, is Mack powerful"])
    def test_is_x_strong_is_the_strength_answer(self, shipped, line):
        client, world = shipped
        msg = say(client, world, line)["message"]
        assert msg.startswith("Mack of Austria"), msg
        assert "cannot answer" not in msg

    def test_the_classifier_reads_the_fourth_name_group(self):
        q = classify_question("is Mack strong", marshals=["Ney"], enemies=["Mack"],
                              regions=["Swabia"])
        assert q == {"kind": "how_many", "subject": "Mack", "subject_type": "enemy"}
        assert classify_board_question("how many men do I have")["kind"] == "own_army"
        assert classify_board_question("what forces do we have")["kind"] == "own_army"


# ═══════════════════════════════════════════════════════════════════════
# 11. The tactical `move to` road reads the law
# ═══════════════════════════════════════════════════════════════════════

class TestTheMoveRoadReadsTheLaw:
    @pytest.mark.parametrize("line", ["Ney, move to London", "Murat, move to London",
                                      "Ney, go to London"])
    def test_a_move_across_shut_water_is_refused_at_issuance_for_nothing(self, shipped, line):
        """The strategic verb refused this at the Channel since FA-46; the
        tactical `move to` — the same order one verb over — accepted it,
        charged 2 AP, walked the corps to Normandy and stalled it there."""
        client, world = shipped
        name = line.split(",")[0]
        before = snapshot(world)
        reply = post(client, line)
        assert reply["success"] is False, reply
        assert "Royal Navy" in reply["message"], reply["message"]
        assert "London" in reply["message"]
        after = snapshot(world)
        assert after["ap"] == before["ap"], "refused at 0 AP"
        assert after["m:" + name] == before["m:" + name], "the corps did not move"
        assert world.get_marshal(name).strategic_order is None

    def test_the_executor_names_the_coverer(self, shipped):
        """The endpoint response whitelists its keys; the executor's own
        result carries the naval verdict the road law produced."""
        _client, world = shipped
        result = M.executor.execute(
            {"success": True, "command": {"marshal": "Ney", "action": "move",
                                          "target": "London",
                                          "raw_command": "Ney, move to London"}},
            {"world": world})
        assert result["success"] is False
        assert result.get("blocked_naval") == "Britain", result
        assert result.get("variable_action_cost") == 0

    def test_the_two_roads_give_one_verdict(self, shipped):
        client, world = shipped
        march = post(client, "Ney, march to London")["message"]
        M._reset_world_state()
        client2 = TestClient(M.app)
        move = post(client2, "Ney, move to London")["message"]
        assert march == move, (march, move)

    def test_a_lawful_far_march_still_forms(self, shipped):
        client, world = shipped
        reply = post(client, "Ney, move to Normandy")
        assert reply["success"] is True, reply
        assert "begins marching to Normandy" in reply["message"]
        order = world.get_marshal("Ney").strategic_order
        assert order is not None and order.target == "Normandy"

    def test_the_ai_road_is_byte_identical(self, shipped):
        """The belt's old two calls (`find_weighted_path` lawful-first, then
        terrain-only) are `plot_route`'s own ladder; for an AI corps the
        verdict is never read and the road is the same list."""
        _client, world = shipped
        mack = world.get_marshal("Mack")
        for dest in ("Vienna", "Paris", "London", "Milan"):
            old = world.find_weighted_path(mack.location, dest, passable_for=None)
            road, verdict = plot_route(world, mack, dest, use_weighted=True,
                                       want_verdict=True)
            assert verdict is None
            assert ([mack.location] + list(road or [])) == (old or [mack.location]), dest


# ═══════════════════════════════════════════════════════════════════════
# 12. The desk fails closed
# ═══════════════════════════════════════════════════════════════════════

class TestTheDeskFailsClosed:
    @pytest.mark.parametrize("line", ["Ney, attack Mack", "Ney, hold", "end turn",
                                      "Ney, march to Lorraine", "recruit for Ney",
                                      "Talleyrand, assess our situation",
                                      "Ney, pause", "Davout, exit Rhineland",
                                      "where is Mack", "what does Austria want"])
    def test_an_order_or_a_board_question_never_reaches_the_desk(self, line):
        assert first_contact_route(line) is None, line

    def test_the_vocabulary_names_no_order_verb_the_parser_knows(self):
        """A pattern that matched an order verb would swallow an order."""
        from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
        forbidden = {"attack", "move", "march", "hold", "fortify", "scout",
                     "retreat", "recruit", "build", "defend", "drill", "charge",
                     "pursue", "support", "bombard", "cancel", "endow"}
        assert forbidden <= set(ROUTED_ORDER_WORDS)
        for word in forbidden:
            assert first_contact_route(word) is None, word
            assert first_contact_route(f"Ney, {word}") is None, word

    def test_the_lever_down_restores_the_shrug(self, shipped, monkeypatch):
        """Sensitivity arm: with the desk off, `hello` draws the old shrug
        and `what now` the old shrug — the pins above are live."""
        client, world = shipped
        monkeypatch.setattr(FC, "FIRST_CONTACT_DESK_ACTIVE", False)
        assert first_contact_route("hello") is None
        msg = post(client, "hello")["message"]
        assert "Berthier bows" not in msg
        assert post(client, "what now")["success"] is False

    def test_every_kind_the_route_mints_is_answered(self):
        for kind in FC.FIRST_CONTACT_HELP_KINDS:
            assert answer_first_contact(kind, "x", None), kind
        assert answer_first_contact("nonsense", "x", None) is None
        assert FC.FIRST_CONTACT_KINDS == FC.FIRST_CONTACT_HELP_KINDS | {"options"}
