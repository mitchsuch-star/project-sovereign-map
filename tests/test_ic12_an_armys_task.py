"""Row IC, Session 3b — IC-12, AN ARMY'S TASK and "TAKE THE WAR GOAL" (November 21, 2026).

The design is `docs/INDEPENDENT_COMMAND_SPEC.md` §9, §9.1, §15 ("Session 3b"); the rules
`docs/SYSTEMS_REFERENCE.md` §234; the module `backend/commands/army_task.py`.

The user's words (November 20, 2026): "if army has differner personalities they arent all doing same
thing every turn" — and his direction for every man set on his own: they "really do stuff", work with
each other, "help their friends"; the order is guidance.

What is pinned here, on the shipped 1805 board through the real `POST /command`:

  * WHICH LINES ARE A TASK — a take, a chase, a hold with a place named; "attack", "hold" with no
    place, fortify, drill, march and support stay what they were; "by exact orders" asks for the plain
    order to each corps; every task verb of the word table is read to its task;
  * WHO COMMANDS — the man named in the line, the man named for the army, else the highest-ranked of
    its men who may be set on his own, with why the men above him do not;
  * THE LIST — its commander on his own (2 actions, his row locked), every other man following him
    (1 action, not counted), who is left out and why; nothing spent before Give; Give as ONE order and
    ONE Take-back unit; the count full and its offer; nobody qualifies and its offer; the same task
    again adds the men left behind;
  * THE ARMY MOVES AS ONE — a follower moves in the pass right after his commander, before the enemy,
    and does what "Tonight" said; he is not ticked by the standing-order pass, is not drawn off by
    distant cannon fire, and a hand order does not end his following;
  * THE WAR GOAL — "Ney, take the war goal" and its refusals; a changed goal is a list that turns the
    men who serve it at 1 action each, and lets go the men left unticked; a goal cleared lets them all
    go; a goal reached becomes the hold of it;
  * the saves, the seam, the screens' payloads.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib

import pytest

import backend.main as M
from backend.commands import army_task as AT
from backend.commands import directive as DV
from backend.commands import take_back as TB
from backend.game_logic import armies, war_goals
from backend.game_logic import own_order as O

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
ARMY = "Army of the Rhine"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _snapshot():
    from backend.models.world_state import WorldState
    with _quiet():
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_dict(json.loads(_snapshot))


@pytest.fixture
def client(world, monkeypatch):
    import backend.main as main_module
    from backend.commands import parse_preview as PP
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    monkeypatch.setattr(main_module, "world", world)
    monkeypatch.setattr(main_module, "game_state", {"world": world})
    with _quiet():
        monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))
    TB.new_board()
    PP.invalidate()
    yield TestClient(main_module.app)
    TB.new_board()
    PP.invalidate()


def _say(client, text: str, **extra) -> dict:
    with _quiet():
        return client.post("/command", json=dict({"command": text}, **extra)).json()


def _preview(client, line: str) -> dict:
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _ask(client, line: str) -> dict:
    """The list a line opens (`list_first`), or {} when the reply is no list."""
    reply = _say(client, line, list_first=True)
    return reply.get("directive") or {}


def _give(client, listing: dict, members=None) -> dict:
    members = members if members is not None else [r["marshal"] for r in listing["rows"] if r["ticked"]]
    total = sum(int(r["ap"]) for r in listing["rows"] if r["marshal"] in members)
    return _say(client, listing["line"], list_first=True, members=members, expect_ap=total)


def _row(listing: dict, name: str) -> dict:
    return next(r for r in listing["rows"] if r["marshal"] == name)


def _heads(reading: dict, role: str) -> list:
    return [p["text"] for p in reading.get("parts") or [] if p.get("role") == role]


def _form(client, who="Ney, Davout and Soult", name=ARMY) -> None:
    reply = _say(client, f"form the {name} with {who}")
    assert reply["success"], reply["message"]


# ═══ which lines are a task ═════════════════════════════════════════════════

class TestWhichLinesAreATask:
    @pytest.mark.parametrize("rest, kind", [
        ("take Swabia", "take"), ("capture Swabia", "take"), ("seize Swabia.", "take"),
        ("chase Mack", "pursue"), ("pursue Mack until he is destroyed", "pursue"),
        ("hold Lorraine", "hold"), ("guard Lorraine", "hold"),
        ("take the war goal", "take"), ("chase the war goal", "pursue"),
        ("attack Swabia on its own", "take"), ("march on Swabia as it sees fit", "take"),
        ("take Swabia boldly", "take"),
    ])
    def test_a_take_a_chase_and_a_hold_with_a_place_are_a_task(self, world, rest, kind):
        got = AT.read(world, ARMY, rest)
        assert got is not None and got["kind"] == kind, rest

    @pytest.mark.parametrize("rest", [
        "hold", "hold fast", "hold for 3 turns", "fortify", "drill", "march to Swabia", "fall back",
        "support Ney", "follow Ney", "attack Swabia", "attack Mack", "stop",
        "hold Lorraine by exact orders", "take Swabia to the letter",
    ])
    def test_every_other_order_stays_what_it_was(self, world, rest):
        assert AT.read(world, ARMY, rest) is None, rest

    def test_the_task_verbs_are_the_word_tables(self):
        from backend.ai import task_words, word_table
        assert AT.TAKE_VERBS == tuple(task_words.ARMY_TASK["take"])
        assert set(task_words.ARMY_TASK["chase"]) == set(word_table.ARMY_TASK["chase"])
        assert "attack" not in AT.TAKE_VERBS, "an army's attack is one battle today"

    def test_every_task_verb_is_read_to_its_task(self, client):
        """The census: no verb is promised that the line does not read (the word table's rule)."""
        for verbs, obj, words in ((AT.TAKE_VERBS, "Swabia", "take Swabia"),
                                  (AT.CHASE_VERBS, "Mack", "chase Mack"),
                                  (AT.HOLD_VERBS, "Lorraine", "hold Lorraine"),
                                  (AT.MARKED_VERBS, "Swabia", "take Swabia")):
            for verb in verbs:
                got = _preview(client, f"Davout, {verb} {obj} on your own")
                assert got["kind"] == "order" and got["ok"], (verb, got.get("parts"))
                assert _heads(got, "head") == [f"Davout · on his own: {words}"], verb

    def test_the_address_carries_the_task_and_exact_orders_do_not(self, client, world):
        _form(client)
        found = DV.address(world, f"{ARMY}, take Swabia")
        assert found["kind"] == "army" and found["task"]["kind"] == "take"
        plain = DV.address(world, f"{ARMY}, hold Lorraine by exact orders")
        assert "task" not in plain and plain["rest"] == "hold Lorraine"
        assert "task" not in DV.address(world, f"{ARMY}, hold")

    def test_an_attack_is_still_its_first_mans_one_battle(self, client):
        _form(client)
        got = _preview(client, f"{ARMY}, attack Mack")
        assert got["directive"] is False
        assert _heads(got, "note")[-1] == f"one man’s order, not one for each corps of the {ARMY}"

    def test_hold_with_no_place_is_the_same_order_for_each_corps(self, client):
        _form(client)
        listing = _ask(client, f"{ARMY}, hold")
        assert "task" not in listing and listing["order"] == "hold"
        assert {r["says"] for r in listing["rows"] if r["ok"]} <= {"hold", "hold Rhineland", "hold Lorraine"}

    def test_by_exact_orders_gives_the_plain_order_to_each(self, client):
        _form(client)
        listing = _ask(client, f"{ARMY}, hold Lorraine by exact orders")
        assert "task" not in listing and listing["order"] == "hold Lorraine"
        assert all(not r["says"].startswith("on his own") for r in listing["rows"])


# ═══ who commands ═══════════════════════════════════════════════════════════

class TestWhoCommands:
    def test_the_highest_ranked_who_may_be_set_on_his_own(self, client, world):
        _form(client)                       # Ney (bold), Davout (careful), Soult (to the letter)
        who = AT.commander(world, ARMY, "take")
        assert who["lead"] == "Ney" and who["named"] == ""
        assert who["why"] == "the highest-ranked of its men who can be set on his own"
        assert who["passed"] == [("Soult", "follows orders to the letter")]
        assert who["next"] == ["Davout"]

    def test_the_list_says_who_and_why(self, client):
        _form(client)
        lead = _row(_ask(client, f"{ARMY}, take Swabia"), "Ney")
        assert lead["notes"][0] == (f"Commands the {ARMY} — the highest-ranked of its men who can be set "
                                    "on his own. (Soult outranks him but takes only exact orders.) "
                                    "He takes your one place for a man on his own.")

    def test_a_commander_named_in_the_line(self, client):
        _form(client)
        listing = _ask(client, f"{ARMY} under Davout, take Swabia")
        assert listing["task"]["lead"] == "Davout" and listing["line"] == f"{ARMY} under Davout, take Swabia"
        assert _row(listing, "Davout")["notes"][0].startswith(f"Commands the {ARMY} — you named him for this task.")
        assert _row(listing, "Ney")["says"] == "follow Davout"

    def test_a_man_who_is_not_of_the_army_cannot_be_named(self, client):
        _form(client)
        reply = _say(client, f"{ARMY} under Lannes, take Swabia", list_first=True)
        assert reply["success"] is False and not reply.get("directive")
        assert reply["message"].startswith(f"Lannes is not one of the {ARMY}'s corps in the field")
        assert reply["message"].endswith("Nothing was spent.")

    @pytest.mark.parametrize("line", [
        f"Davout commands the {ARMY}", f"put Davout in command of the {ARMY}",
        f"give the {ARMY} to Davout", f"make Davout commander of the {ARMY}",
    ])
    def test_a_commander_named_for_the_army(self, client, world, line):
        _form(client)
        before = int(world.actions_remaining)
        reply = _say(client, line)
        assert reply["success"], reply["message"]
        assert reply["message"].startswith(f"Davout commands the {ARMY}.")
        assert armies.commander(world, ARMY) == "Davout" and int(world.actions_remaining) == before
        who = AT.commander(world, ARMY, "take")
        assert (who["lead"], who["why"]) == ("Davout", "you named him to command the army")

    def test_naming_a_commander_from_outside_brings_him_in(self, client, world):
        _form(client)
        reply = _say(client, f"Lannes commands the {ARMY}")
        assert reply["success"] and "He joins the Army of the Rhine." in reply["message"]
        assert armies.members(world, ARMY)[-1] == "Lannes" and armies.commander(world, ARMY) == "Lannes"

    def test_relieving_the_commander_clears_it(self, client, world):
        _form(client)
        _say(client, f"Davout commands the {ARMY}")
        reply = _say(client, f"relieve the commander of the {ARMY}")
        assert reply["success"], reply["message"]
        assert reply["message"].startswith(f"Davout no longer commands the {ARMY}")
        assert armies.commander(world, ARMY) == "" and "commander" not in world.armies[ARMY]
        again = _say(client, f"relieve the commander of the {ARMY}")
        assert again["success"] is False and again["message"].startswith("Nobody is named to command")

    def test_a_commander_who_leaves_commands_no_longer(self, client, world):
        _form(client)
        _say(client, f"Davout commands the {ARMY}")
        _say(client, f"remove Davout from the {ARMY}")
        assert armies.commander(world, ARMY) == ""
        assert AT.commander(world, ARMY, "take")["lead"] == "Ney"

    def test_the_words_that_name_a_commander_are_not_a_march(self, world):
        # with no such army, "Ney leads the army to Vienna" is no line of the roll
        assert armies.read_order(world, "Ney leads the army to Vienna") is None
        assert armies.read_order(world, "Ney commands the Army of Nowhere") is None

    def test_the_read_back_names_him_and_offers_the_next(self, client):
        _form(client)
        got = _preview(client, f"{ARMY}, take Swabia")
        assert got["directive"] is True and got["kind"] == "order"
        assert _heads(got, "head") == [f"The {ARMY} · on its own: take Swabia"]
        taken = _heads(got, "taken")
        assert taken[0] == ("Ney commands — the highest-ranked of its men who can be set on his own; "
                            "he is set on his own (2 actions)")
        assert taken[-1].startswith("Davout and Soult follow him — 1 action each")
        labels = [c["label"] for c in got["candidates"]]
        assert "Davout commands instead" in labels and "Plain orders to each corps instead" in labels
        line = next(c["line"] for c in got["candidates"] if c["label"] == "Davout commands instead")
        assert line == f"{ARMY} under Davout, take Swabia"


# ═══ the list ═══════════════════════════════════════════════════════════════

class TestTheList:
    def test_one_list_its_commander_on_his_own_the_rest_following(self, client, world):
        _form(client)
        before = int(world.actions_remaining)
        listing = _ask(client, f"{ARMY}, take Swabia")
        assert int(world.actions_remaining) == before, "nothing is spent before Give"
        assert listing["kind"] == "army" and listing["who"] == f"The {ARMY}"
        assert listing["order"] == "take Swabia, on its own" and listing["line"] == f"{ARMY}, take Swabia"
        assert listing["task"] == {"army": ARMY, "lead": "Ney", "lead_shown": "Ney", "words": "take Swabia",
                                   "why_lead": "the highest-ranked of its men who can be set on his own",
                                   "next": ["Davout"]}
        assert [(r["marshal"], r["says"], r["ap"], r["ok"]) for r in listing["rows"]] == [
            ("Ney", "on his own: take Swabia", 2, True),
            ("Davout", "follow Ney", 1, True),
            ("Soult", "follow Ney", 1, True)]
        assert _row(listing, "Ney").get("locked") is True
        assert not _row(listing, "Davout").get("locked")
        assert listing["total"] == 4 and all(r["ticked"] for r in listing["rows"])
        assert all(isinstance(r["ap"], int) and isinstance(r["turns"], int) for r in listing["rows"])

    def test_the_commanders_row_says_his_first_move_and_his_odds(self, client):
        _form(client)
        lead = _row(_ask(client, f"{ARMY}, take Swabia"), "Ney")
        # (row IC, Session 4b — "He moves at turn start": said as an intention)
        assert lead["notes"][1].startswith("At the start of next turn he means to — if nothing changes "
                                           "first: Ney attacks Mack at Swabia")
        assert "he goes in when they are our " in lead["notes"][1], "his odds, said with his first night"
        assert " to their 10 or better" in lead["notes"][1], "both figures the same way round"
        # (read blind: "is Murat in the army?" — a senior who is not one of its men is said to be)
        assert lead["notes"][2] == ("Murat (not of this army) outranks Ney and has no order — he will "
                                    "resent Ney for it")
        assert lead["tones"] == ["info", "tonight", "warn"]
        # (read blind: "what do Lannes and Murat do?" — men beside his battle who are not of
        # the army may join all the same, and the list says so)
        assert "beside him (they may join, of this army or not)" in lead["notes"][1], lead["notes"][1]
        # short enough for the men who follow him to stand on the same screen: his answer and
        # the small print are the read-back's and his card's (pressed at the first player's setup)
        assert len(lead["notes"]) == 3 and lead["voice"].startswith("“")

    def test_his_odds_are_said_once_with_his_first_move_or_apart(self, client):
        """His odds stand once on his row: in his first move's line when it is
        an attack, else apart (row IC, Session 4b: his judgement may strike a
        chance beside the ground he holds — Mack at Swabia, beside the Emperor)."""
        _form(client, who="Davout and Soult")
        lead = _row(_ask(client, f"{ARMY}, hold Rhineland"), "Davout")
        night = [n for n in lead["notes"] if n.startswith(AT.FIRST_MOVE)]
        said_with = bool(night) and "he goes in when" in night[0]
        assert said_with != any(n.startswith("He attacks only when the odds are our ") for n in lead["notes"])

    def test_a_followers_row_says_his_own_part(self, client):
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        davout, soult = _row(listing, "Davout"), _row(listing, "Soult")
        assert davout["notes"][0].startswith(
            "Moves with Ney at the start of each turn, and may join Ney's battles next to him — about ")
        assert davout["notes"][0].endswith("times in 100. He takes none of your places for men on their own.")
        # the man who follows orders to the letter: his order is his written word
        assert soult["notes"][0].startswith(
            "To the letter: marches where Ney marches, and this order is his written word to join "
            "Ney's battles next to him")
        # the plain support order's own terms do not hold for an army's follower
        for row in (davout, soult):
            assert not any("He will drop this order" in n or "lapses of itself" in n for n in row["notes"])

    def test_give_sends_it_as_one_order(self, client, world):
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        reply = _give(client, listing)
        assert reply["success"], reply["message"]
        assert reply["message"].splitlines()[0] == (
            f"The {ARMY} is given its task — Ney commands, on his own; Davout and Soult follow him — "
            "4 actions for the 4 in hand.")
        assert int(world.actions_remaining) == 0
        ney = world.get_marshal("Ney")
        assert (O.own(ney) or {}).get("task") == "take" and O.own(ney)["army"] == ARMY
        for name in ("Davout", "Soult"):
            order = world.get_marshal(name).strategic_order
            assert (order.command_type, order.target, order.standing_follow) == ("SUPPORT", "Ney", True)
            assert AT.following(world, world.get_marshal(name)) is ney
        assert O.count(world) == 1, "the followers are not counted among those on their own"
        assert [(r["marshal"], r["sent"], r["ap"]) for r in reply["group"]["rows"]] == [
            ("Ney", True, 2), ("Davout", True, 1), ("Soult", True, 1)]

    def test_take_back_undoes_all_of_it(self, client, world):
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        with _quiet():
            undone = client.post("/undo").json()
        assert undone["success"], undone.get("message")
        assert int(world.actions_remaining) == 4 and O.count(world) == 0
        assert all(world.get_marshal(n).strategic_order is None for n in ("Ney", "Davout", "Soult"))

    def test_nobody_follows_a_commander_who_is_left_out(self, client, world):
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        reply = _give(client, listing, members=["Davout", "Soult"])
        assert reply["success"] is False and reply.get("directive"), reply["message"]
        assert reply["message"].startswith(
            "Ney commands this task — the others follow him, so his own row cannot be left out.")
        assert int(world.actions_remaining) == 4 and world.get_marshal("Davout").strategic_order is None

    def test_a_man_already_on_his_own_keeps_his_task_and_is_left_out(self, client, world):
        O.COUNT_AT_START, kept = 2, O.COUNT_AT_START
        try:
            _form(client)
            assert _say(client, "Davout, hold Rhineland on your own")["success"]
            listing = _ask(client, f"{ARMY}, take Swabia")
            assert _row(listing, "Davout")["ok"] is False
            assert _row(listing, "Davout")["why"] == "on his own: hold Rhineland — not included"
            _give(client, listing)
            assert O.own(world.get_marshal("Davout"))["task"] == "hold", "he keeps his own task"
        finally:
            O.COUNT_AT_START = kept

    def test_the_count_full_says_so_and_offers_the_stand_down(self, client, world):
        assert _say(client, "Massena, hold Milan on your own")["success"]
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        assert listing["sendable"] is False and not any(r["ticked"] for r in listing["rows"])
        assert listing["note"] == ("You already have as many on their own as you may — on their own: 1 of "
                                   "the 1 you may have. Ney cannot take the army's task until a place is free.")
        assert listing["offer"] == {
            "label": "Stand down Massena (free) and list again", "kind": "send",
            "line": "Massena, stand down", "then": f"{ARMY}, take Swabia",
            "tip": ("Massena is the lowest-ranked of your men on their own (hold Milan). Standing him "
                    "down frees a place; the list is then drawn again.")}
        assert _row(listing, "Davout")["why"] == "would follow Ney — who cannot take the task as things stand"
        # said once, plainly (pressed: "the count is full — on their own: 1 of the 1 …" stood twice)
        assert _row(listing, "Ney")["why"] == "would command — but no place is free for another man on his own"
        # the offer, pressed: the stand-down is sent, and the list drawn again can be given
        assert _say(client, listing["offer"]["line"])["success"]
        again = _ask(client, listing["offer"]["then"])
        assert again["sendable"] is True and "offer" not in again and _row(again, "Ney")["ok"]

    def test_nobody_can_command_says_why_and_offers_plain_orders(self, client, world):
        _form(client, who="Soult and Napoleon", name="Army of the Reserve")
        listing = _ask(client, "Army of the Reserve, hold Lorraine")
        assert listing["sendable"] is False and listing["task"]["lead"] == ""
        assert [(r["marshal"], r["why"]) for r in listing["rows"]] == [
            ("Soult", "follows orders to the letter"), ("Napoleon", "the Emperor commands himself")]
        assert listing["offer"]["kind"] == "list"
        assert listing["offer"]["line"] == "Army of the Reserve, hold Lorraine by exact orders"
        plain = _ask(client, listing["offer"]["line"])
        assert "task" not in plain and plain["sendable"] is True
        # without the list (a script's road) the same refusal is said, free
        reply = _say(client, "Army of the Reserve, hold Lorraine")
        assert reply["success"] is False and reply["message"].startswith(
            "No man of the Army of the Reserve can be set on his own, Sire — Soult follows orders to the "
            "letter; Napoleon the Emperor commands himself.")
        assert int(world.actions_remaining) == 4

    def test_the_same_task_again_adds_the_men_left_behind(self, client, world):
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        _give(client, listing, members=["Ney", "Davout"])            # Soult left for later
        world.actions_remaining = 4
        again = _ask(client, f"{ARMY}, take Swabia")
        assert again["task"]["lead"] == "Ney" and again["task"]["why_lead"] == "he commands it on its own already"
        assert _row(again, "Ney")["ok"] is False
        assert _row(again, "Ney")["why"] == f"commands the {ARMY} on its own already — take Swabia"
        assert _row(again, "Davout")["why"] == "follows Ney already"
        assert (_row(again, "Soult")["ok"], _row(again, "Soult")["ticked"], again["total"]) == (True, True, 1)
        assert _give(client, again)["success"]
        assert AT.following(world, world.get_marshal("Soult")) is world.get_marshal("Ney")
        assert O.count(world) == 1

    def test_without_the_list_it_is_carried_out_at_once(self, client, world):
        """A request with no `list_first` (a script, the band's driver) runs the same lines."""
        _form(client)
        reply = _say(client, f"{ARMY}, take Swabia")
        assert reply["success"] and not reply.get("directive")
        assert O.own(world.get_marshal("Ney"))["army"] == ARMY
        assert AT.following(world, world.get_marshal("Davout")) is world.get_marshal("Ney")

    def test_an_army_of_one_is_listed_too(self, client):
        _form(client, who="Ney and Soult", name="Army of the Vanguard")
        _say(client, "remove Soult from the Army of the Vanguard")
        listing = _ask(client, "Army of the Vanguard, take Swabia")
        assert [(r["marshal"], r["says"]) for r in listing["rows"]] == [("Ney", "on his own: take Swabia")]


# ═══ the army moves as one ══════════════════════════════════════════════════

class TestTheArmyMovesAsOne:
    def _given(self, client, world, line=f"{ARMY}, hold Lorraine", who="Ney and Davout"):
        _form(client, who=who)
        listing = _ask(client, line)
        assert _give(client, listing)["success"]
        return world.get_marshal("Ney"), world.get_marshal("Davout")

    def test_a_follower_is_one_only_while_his_friend_commands_his_army(self, client, world):
        ney, davout = self._given(client, world)
        assert AT.following(world, davout) is ney and AT.followers(world, ney) == [davout]
        assert AT.following(world, ney) is None
        _say(client, f"remove Davout from the {ARMY}")
        assert AT.following(world, davout) is None, "out of the army, his order is an ordinary follow"

    def test_he_is_not_drawn_off_by_distant_cannon_fire(self, client, world):
        from backend.commands import strategic as S
        from backend.models.marshal import StrategicOrder
        _form(client, who="Davout and Ney")
        _say(client, f"Davout commands the {ARMY}")
        assert _give(client, _ask(client, f"{ARMY}, hold Rhineland"), members=["Davout"])["success"]
        davout, ney, lannes = (world.get_marshal(n) for n in ("Davout", "Ney", "Lannes"))

        def follow() -> StrategicOrder:
            return StrategicOrder(command_type="SUPPORT", target="Davout", target_type="marshal",
                                  started_turn=1, issued_turn=1, original_command="follow Davout",
                                  standing_follow=True)
        # the order in question, handed in before he holds it (the order's reply reads it so)
        assert AT.following(world, ney, follow()) is davout
        assert S.aggressive_interrupt_applies(world, ney, follow()) is False
        ney.strategic_order = follow()                      # a bold man, following
        assert AT.following(world, ney) is davout
        assert S.aggressive_interrupt_applies(world, ney) is False
        assert S.aggressive_interrupt_clause(world, ney) == ""
        assert S.StrategicOrderProcessor(M.executor)._check_interrupts(ney, world) is None
        # the same order outside the army's task is dropped for the guns, as it always was
        lannes.strategic_order = follow()
        assert AT.following(world, lannes) is None and S.aggressive_interrupt_applies(world, lannes) is True
        # …and a plain support of the commander is no part of the army's task either
        ney.strategic_order.standing_follow = False
        assert AT.following(world, ney) is None

    def test_the_followers_move_with_him_as_the_turn_opens(self, client, world):
        """Row IC, Session 4b — "He moves at turn start": the turn after the
        task is given OPENS with the commander's move, his follower's right
        after it (the army moves as one); no preview is kept, and the
        follower's card says what he did."""
        ney, davout = self._given(client, world)             # both at Rhineland; Lorraine is next door
        assert (ney.location, davout.location) == ("Rhineland", "Rhineland")
        reply = _say(client, "end turn")
        own_rows = [r for r in reply["strategic_reports"] if r.get("own")]
        order = [r["marshal"] for r in own_rows]
        assert order.index("Davout") == order.index("Ney") + 1, order
        rows = {r["marshal"]: r for r in own_rows}
        assert rows["Ney"]["act"] != "start", "his first move is the turn after he is given"
        assert rows["Davout"]["follows"] == "Ney" and rows["Davout"]["action"].startswith("army_")
        if rows["Ney"]["act"] == "march":
            assert rows["Davout"]["action"] in ("army_follow", "army_with"), rows["Davout"]
        assert AT.this_turn(world, davout) == rows["Davout"]["message"]

    def test_the_standing_order_pass_does_not_tick_him(self, client, world):
        self._given(client, world)
        _say(client, "end turn")
        reply = _say(client, "end turn")
        mine = [r for r in reply["strategic_reports"] if r.get("marshal") == "Davout"]
        assert [r["action"] for r in mine] == ["army_follow"], "one row: the pass's own — never the tick's"

    def test_a_follower_starts_no_attack_of_his_own(self, client, world):
        """The army takes Swabia, where Mack stands: the commander attacks, the followers stand by —
        the arrival roll may bring them into THAT battle; none attacks separately (R-TOGETHER)."""
        _form(client)
        assert _give(client, _ask(client, f"{ARMY}, take Swabia"))["success"]
        reply = _say(client, "end turn")                     # the turn opens with the army's move
        lead = next(r for r in reply["strategic_reports"] if r.get("own") and r["marshal"] == "Ney")
        rows = {r["marshal"]: r for r in reply["strategic_reports"] if r.get("own") and r.get("follows")}
        assert set(rows) == {"Davout", "Soult"}
        assert not any(r["act"] in ("attack", "strike") for r in rows.values())
        if lead["act"] == "attack":
            assert {r["action"] for r in rows.values()} <= {"army_join", "army_stand_by"}

    def test_a_hand_order_does_not_end_his_following(self, client, world):
        ney, davout = self._given(client, world)
        world.actions_remaining = 4
        reply = _say(client, "Davout, fortify")
        assert reply["success"], reply["message"]
        assert AT.following(world, davout) is ney, "his follow order stands"
        # (row IC, Session 4b: a hand order is on top of his move; it costs no later move)
        reading = AT.follower_reading(world, davout, ney, str(ney.location or ""))
        assert "your order" not in reading["line"]

    def test_a_hand_order_does_not_end_the_commanders_task_either(self, client, world):
        ney, davout = self._given(client, world)
        world.actions_remaining = 4
        assert _say(client, "Ney, fortify")["success"]
        assert (O.own(ney) or {}).get("army") == ARMY and AT.following(world, davout) is ney

    def test_when_his_task_ends_they_follow_by_an_ordinary_order(self, client, world):
        ney, davout = self._given(client, world)
        reply = _say(client, "Ney, stand down")
        assert reply["success"] and O.count(world) == 0
        assert (f"Davout still follows Ney, by an ordinary order now — “{ARMY}, stop” recalls him."
                in reply["message"])
        assert davout.strategic_order is not None and AT.following(world, davout) is None

    def test_a_new_commander_takes_the_army_from_the_old(self, client, world):
        """ONE man at an army's head: the old commander keeps his task as his own."""
        O.COUNT_AT_START, kept = 2, O.COUNT_AT_START
        try:
            _form(client)
            assert _give(client, _ask(client, f"{ARMY}, hold Lorraine"), members=["Ney"])["success"]
            ney, davout = world.get_marshal("Ney"), world.get_marshal("Davout")
            assert O.own(ney)["army"] == ARMY
            world.actions_remaining = 4
            listing = _ask(client, f"{ARMY} under Davout, hold Rhineland")
            assert _row(listing, "Davout")["ok"] and _row(listing, "Davout")["locked"] is True
            assert _row(listing, "Ney")["why"] == (
                f"on his own: hold Lorraine — he keeps that task as his own, and commands the {ARMY} no longer")
            assert _give(client, listing, members=["Davout"])["success"]
            assert O.own(davout)["army"] == ARMY
            assert O.own(ney)["task"] == "hold" and "army" not in O.own(ney)
            assert AT.task_of(world, ARMY)["lead"] == "Davout"
        finally:
            O.COUNT_AT_START = kept

    def test_a_bold_follower_may_object_and_his_row_says_so(self, client, world):
        """A bold man told to follow with an enemy in reach may object, as to any order of yours —
        the list says so before Give, and his question stops the rest behind him (§230)."""
        _form(client, who="Davout and Ney")
        _say(client, f"Davout commands the {ARMY}")
        listing = _ask(client, f"{ARMY}, hold Rhineland")
        assert _row(listing, "Ney")["objection"] == "possible"
        assert "A marshal who objects asks you, and the rest wait behind his question." in listing["help"]


# ═══ the war goal ═══════════════════════════════════════════════════════════

class TestTheWarGoal:
    def _austrian(self, world, n=2):
        ney = world.get_marshal("Ney")
        held = sorted((int(world.get_distance(ney.location, name)), name)
                      for name, region in world.regions.items()
                      if getattr(region, "controller", "") == "Austria")
        return [name for _d, name in held[:n]]

    def test_with_no_goal_it_is_refused_free_with_why(self, client, world):
        got = _preview(client, "Ney, take the war goal")
        assert got["kind"] == "refusal"
        assert _heads(got, "bad") == ["No war goal is set — name one first: ‘the war goal is Vienna’"]
        reply = _say(client, "Ney, take the war goal")
        assert reply["success"] is False and reply["message"].startswith("No war goal is set, Sire")
        assert int(world.actions_remaining) == 4

    def test_it_sets_him_on_his_own_toward_the_goal(self, client, world):
        first = self._austrian(world)[0]
        assert _say(client, f"the war goal is {first}")["success"]
        got = _preview(client, "Ney, take the war goal")
        assert _heads(got, "head") == [f"Ney · on his own: take {first}"] and got["ap"] == 2
        assert (f"he serves your war goal ({first}) — name a new goal and he is turned to it, 1 action"
                in _heads(got, "taken"))
        reply = _say(client, "Ney, take the war goal")
        assert reply["success"], reply["message"]
        spec = O.own(world.get_marshal("Ney"))
        assert (spec["task"], spec["target"], spec["goal"]) == ("take", first, "Austria")
        assert [m.name for m in war_goals.serving(world, "Austria")] == ["Ney"]
        assert O.payload(world, world.get_marshal("Ney"))["goal"] is True

    def test_a_man_who_follows_orders_to_the_letter_is_told_why(self, client, world):
        _say(client, f"the war goal is {self._austrian(world)[0]}")
        got = _preview(client, "Soult, take the war goal")
        assert got["kind"] == "refusal"
        assert _heads(got, "bad")[0].startswith("Soult cannot be set on his own: Soult follows orders to the letter")

    def test_an_army_goal_out_of_sight_cannot_be_chased(self, client, world):
        from backend.display_names import humanize_entity_name
        hidden = next(m for m in world.marshals.values()
                      if m.nation == "Austria" and m not in (world.get_visible_enemies("France") or []))
        shown = humanize_entity_name(hidden.name)
        assert _say(client, f"make {shown} the war goal")["success"]
        task = war_goals.task_for(world, world.get_marshal("Ney"))
        assert task["refusal"].startswith(f"France does not see {shown}, Sire — a chase needs an army in sight.")
        got = _preview(client, "Ney, take the war goal")
        assert got["kind"] == "refusal"
        assert _heads(got, "bad") == [f"France does not see {shown} — a chase needs an army in sight"]

    def test_a_changed_goal_is_a_list_that_turns_the_men_who_serve_it(self, client, world):
        first, second = self._austrian(world)
        _say(client, f"the war goal is {first}")
        assert _say(client, "Ney, take the war goal")["success"]
        got = _preview(client, f"the war goal is {second}")
        assert got["directive"] is True
        assert _heads(got, "head") == [f"The war goal · {second} · 1 man to turn"]
        assert _heads(got, "taken") == [f"Ney serves the war goal — he turns to {second} (1 action)"]
        before = int(world.actions_remaining)
        listing = _ask(client, f"the war goal is {second}")
        assert world.war_goals["Austria"]["target"] == first, "nothing changes before Give"
        assert int(world.actions_remaining) == before
        assert listing["kind"] == "goal" and listing["who"] == "The men serving your war goal"
        assert listing["order"] == f"turn to {second} — your new war goal"
        assert listing["line"] == f"the war goal is {second}" and listing["total"] == 1
        assert listing["say"].startswith(f"The war goal becomes {second} (it was {first}) when you Give")
        row = _row(listing, "Ney")
        assert (row["says"], row["ap"], row["ticked"]) == (f"on his own: take {second}", 1, True)
        assert row["notes"][0] == (f"Untick him and he keeps to his task (take {first}) — he then serves "
                                   "the war goal no longer.")
        # short, as a commander's row is: his first move, then what warns
        assert row["notes"][1].startswith("At the start of next turn he means to — if nothing changes first: ")
        assert not any(n.startswith(("he makes his first move", "“", "on his own —")) for n in row["notes"])
        reply = _give(client, listing)
        assert reply["success"], reply["message"]
        assert world.war_goals["Austria"]["target"] == second
        spec = O.own(world.get_marshal("Ney"))
        assert (spec["target"], spec["goal"]) == (second, "Austria")
        assert int(world.actions_remaining) == before - 1

    def test_a_man_left_unticked_keeps_his_target_and_serves_it_no_longer(self, client, world):
        first, second = self._austrian(world)
        _say(client, f"the war goal is {first}")
        _say(client, "Ney, take the war goal")
        listing = _ask(client, f"the war goal is {second}")
        before = int(world.actions_remaining)
        reply = _give(client, listing, members=[])           # the goal named, nobody ticked
        assert reply["success"], reply["message"]
        assert reply["message"].splitlines()[0].startswith(
            f"The goal of the war with the Third Coalition is now {second}.")
        assert reply["message"].splitlines()[-1] == (
            f"Ney keeps to his task (take {first}) and serves the war goal no longer.")
        assert world.war_goals["Austria"]["target"] == second
        spec = O.own(world.get_marshal("Ney"))
        assert spec["target"] == first and "goal" not in spec
        assert int(world.actions_remaining) == before, "naming the goal is free"
        assert war_goals.serving(world, "Austria") == []

    def test_clearing_the_goal_lets_every_man_go(self, client, world):
        first = self._austrian(world)[0]
        _say(client, f"the war goal is {first}")
        _say(client, "Ney, take the war goal")
        reply = _say(client, "clear the war goal")
        assert reply["success"]
        assert reply["message"].endswith(f"Ney keeps to his task (take {first}) and serves the war goal no longer.")
        spec = O.own(world.get_marshal("Ney"))
        assert spec["target"] == first and "goal" not in spec

    def test_a_goal_reached_becomes_the_hold_of_it(self, client, world):
        first = self._austrian(world)[0]
        _say(client, f"the war goal is {first}")
        _say(client, "Ney, take the war goal")
        ney = world.get_marshal("Ney")
        region = world.get_region(first)
        for foe in list(world.marshals.values()):
            if foe.location == first and foe.nation != "France":
                foe.location = self._austrian(world, 3)[-1]
        region.controller = "France"
        ney.location = first
        row = O._life(world, ney)
        assert row["message"] == f"Ney has taken {first} and holds it now. Your war goal is won."
        spec = O.own(ney)
        assert spec["task"] == "hold" and "goal" not in spec

    def test_the_armys_form(self, client, world):
        first = self._austrian(world)[0]
        _form(client)
        _say(client, f"the war goal is {first}")
        listing = _ask(client, f"{ARMY}, take the war goal")
        assert listing["task"]["lead"] == "Ney" and listing["order"] == f"take {first}, on its own"
        assert _give(client, listing)["success"]
        spec = O.own(world.get_marshal("Ney"))
        assert (spec["goal"], spec["army"], spec["target"]) == ("Austria", ARMY, first)


# ═══ the saves, the seam, the screens ═══════════════════════════════════════

class TestSavesSeamAndScreens:
    def test_a_save_keeps_the_commander_the_army_and_the_goal(self, client, world):
        from backend.models.world_state import WorldState
        _form(client)
        assert world.to_dict()["armies"][ARMY] == {"members": ["Ney", "Davout", "Soult"], "formed_turn": 1}
        _say(client, f"Davout commands the {ARMY}")
        # (Ney, a bold man, may object to following and ask first — he is left for later)
        assert _give(client, _ask(client, f"{ARMY}, hold Rhineland"), members=["Davout", "Soult"])["success"]
        saved = world.to_dict()
        assert saved["armies"][ARMY]["commander"] == "Davout"
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(saved, default=str)))
        assert again.armies == saved["armies"]
        davout = again.get_marshal("Davout")
        assert O.own(davout)["army"] == ARMY
        assert AT.following(again, again.get_marshal("Soult")) is davout

    def test_an_old_save_reads_no_commander(self, world):
        from backend.models.world_state import WorldState
        data = world.to_dict()
        data["armies"] = {"Army of Italy": {"members": ["Massena"], "formed_turn": 2}}
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(data, default=str)))
        assert again.armies == {"Army of Italy": {"members": ["Massena"], "formed_turn": 2}}
        assert armies.commander(again, "Army of Italy") == ""

    def test_the_seam_down_an_armys_take_is_its_first_mans_battle_again(self, client, monkeypatch):
        _form(client)
        monkeypatch.setattr(AT, "an_army_takes_a_task", lambda: False)
        got = _preview(client, f"{ARMY}, take Swabia")
        assert got["directive"] is False
        assert _heads(got, "note")[-1] == f"one man’s order, not one for each corps of the {ARMY}"

    def test_the_armys_chip_says_its_task_only_while_it_has_one(self, client, world):
        _form(client)
        assert armies.payload(world) == [{"name": ARMY, "members": ["Ney", "Davout", "Soult"],
                                          "members_shown": ["Ney", "Davout", "Soult"], "in_field": 3}]
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        chip = armies.payload(world)[0]
        assert chip["task"] == {"lead": "Ney", "lead_shown": "Ney", "words": "take Swabia",
                                "line": "on its own: take Swabia", "followers": ["Soult", "Davout"]}

    def test_the_desk_counts_the_commander_once_and_names_his_followers(self, client, world):
        """Row IC, Session 4b — "He moves at turn start": the desk counts the
        commander once; it says what he DID as the turn opened (nothing yet,
        the turn the task is given) — no preview of what he will do."""
        _form(client)
        reply = _give(client, _ask(client, f"{ARMY}, take Swabia"))
        own = reply["desk"]["own"]
        assert (own["n"], own["of"]) == (1, 1)
        assert own["this_turn"] == [] and "tonight" not in own
        card = O.payload(world, world.get_marshal("Ney"))
        assert card["army"] == ARMY and card["followers"] == ["Soult", "Davout"]

    def test_the_cards_say_who_commands_and_who_follows(self, client, world):
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        card = O.payload(world, world.get_marshal("Ney"))
        assert card["army"] == ARMY and card["followers"] == ["Soult", "Davout"]
        held = AT.follower_payload(world, world.get_marshal("Davout"))
        assert (held["lead"], held["army"], held["task"]) == ("Ney", ARMY, "take Swabia")
        assert isinstance(held["odds"], int) and held["first_move_next"] is True and held["this_turn"] == ""
        assert AT.follower_payload(world, world.get_marshal("Lannes")) is None

    def test_the_mornings_status_says_who_commands_and_who_follows(self, client, world):
        from backend.game_logic import dispatch
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        key, note = dispatch._derive_marshal_status(world.get_marshal("Ney"), world)
        assert key == "on_his_own" and note.startswith(f"On his own: take Swabia. He commands the {ARMY}.")
        key, note = dispatch._derive_marshal_status(world.get_marshal("Davout"), world)
        assert (key, note) == ("en_route", f"Follows Ney — the {ARMY}'s task (take Swabia).")

    def test_the_read_back_names_the_man_a_senior_resents(self, client):
        """Pressed: "Murat outranks him" stood before the reading had said who "him" was."""
        _form(client)
        warns = _heads(_preview(client, f"{ARMY}, take Swabia"), "warn")
        assert warns == ["Murat (not of this army) outranks Ney and has no order — he will resent Ney for it"]

    def test_the_list_says_when_a_man_it_names_is_not_of_the_army(self):
        """Read blind, round 1: the men beside the commander's battle and the senior who
        resents the task were taken for men of the army. The words, by themselves."""
        men = ("Ney", "Davout", "Soult")
        night = ("At the start of next turn he means to — if nothing changes first: Ney attacks Mack at "
                 "Swabia, with {} beside him ({}) — the odds are our 19.2 to their 10, and he goes in when "
                 "they are 5 to 10 or better")
        mixed = AT._beside_for_the_list(night.format("Davout, Lannes and Murat", "they may join"), men)
        assert "beside him (they may join, of this army or not) — the odds" in mixed
        outside = AT._beside_for_the_list(night.format("Lannes", "he may join"), men)
        assert "beside him (he may join, though not of this army) — the odds" in outside
        ours = night.format("Davout and Soult", "they may join")
        assert AT._beside_for_the_list(ours, men) == ours, "all of the army: nothing added"
        assert AT._beside_for_the_list(night.format("Lannes", "he may join"), ()) \
            == night.format("Lannes", "he may join"), "no army in hand (a changed war goal's row)"
        slight = "Davout outranks him and has no order — he will resent it (his regard for Ney drops)"
        assert AT._slight_for_the_list(slight, "Ney", men) == (
            "Davout outranks Ney and has no order — he will resent Ney for it"), "one of the army: no aside"
        assert AT._tone(AT._slight_for_the_list(slight, "Ney", men)) == "warn"

    def test_a_barred_road_names_who_bars_it(self, client, world):
        """Read blind, round 1: "…May become a great battle — he bars the road to Tyrol" — who?"""
        _say(client, "the war goal is Tyrol")
        nights = _heads(_preview(client, "Ney, take the war goal"), "tonight")
        assert nights and nights[0].startswith("At the start of next turn he means to — if nothing changes "
                                               "first: Ney attacks Mack at Swabia")
        assert nights[0].endswith(" — Mack bars the road to Tyrol"), nights[0]

    def test_give_it_a_task_writes_a_ready_sentence(self, client, world):
        _form(client)
        with _quiet():
            got = client.get("/task_presets", params={"army": ARMY}).json()
        assert got["success"] and got["army"] == ARMY and got["lead"] == "Ney"
        assert got["line"].startswith(f"{ARMY}, ")
        assert AT.read(world, ARMY, got["line"][len(ARMY) + 2:]) is not None, "the sentence is a task"
        with _quiet():
            none = client.get("/task_presets", params={"army": "Army of Nowhere"}).json()
        assert none["success"] is False

    def test_a_slight_no_longer_makes_the_order_stand(self, client, world):
        """IC3B-1 (and Session 3's sibling): one man set on his own while a bold senior stands idle
        writes that senior's resentment in the court's book — the order's own consequence, taken
        back with it. Before, the note alone made Take back refuse."""
        assert "marshal_ledger" in TB.ORDER_KEYS
        before = json.dumps(world.to_dict().get("marshal_ledger"), sort_keys=True, default=str)
        reply = _say(client, "Ney, take Swabia on your own")
        assert reply["success"] and "he resents it" in reply["message"]
        written = json.dumps(world.to_dict().get("marshal_ledger"), sort_keys=True, default=str)
        assert written != before, "the slight is written in the court's book"
        with _quiet():
            undone = client.post("/undo").json()
        assert undone["success"], undone.get("message")
        assert O.count(world) == 0 and int(world.actions_remaining) == 4
        assert json.dumps(world.to_dict().get("marshal_ledger"), sort_keys=True, default=str) == before, \
            "…and un-written with the order"

    def test_the_new_keys_are_in_the_take_backs_unit(self):
        # the commander rides `armies`, the task `strategic_orders` / `marshals`, the goal `war_goals`
        assert {"armies", "war_goals", "strategic_orders", "marshals"} <= TB.ORDER_KEYS


# ═══ the client's half, read off its scripts ════════════════════════════════
# (the driven walk `tests/test_dd_b_the_client_hands.py::TestRowIC12AnArmysTask`
# presses all of it in the real game; these hold where no engine is installed)

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _gd(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _gd_func(text: str, name: str) -> str:
    start = text.index(f"func {name}(")
    end = text.find("\nfunc ", start + 1)
    other = text.find("\nstatic func ", start + 1)
    ends = [e for e in (end, other) if e != -1]
    return text[start:min(ends)] if ends else text[start:]


class TestTheClientsHalf:
    def test_the_list_card_wears_the_tasks_title_cost_line_and_offer(self):
        card = _gd("order_confirm_card.gd")
        assert "signal directive_offer_requested(offer: Dictionary)" in card
        title = _gd_func(card, "_dir_title")
        assert '"A TASK FOR THE " + str((task as Dictionary).get("army", "")).to_upper()' in title
        assert 'return "A NEW WAR GOAL"' in title
        tail = _gd_func(card, "_dir_tail")
        assert '" on his own, " + men + " following him."' in tail
        # the offer wears the middle button, and its press stays on the card for the host
        assert "line_button.visible = offer is Dictionary" in _gd_func(card, "open_directive")
        assert "directive_offer_requested.emit(" in _gd_func(card, "_on_line")

    def test_the_commanders_row_is_locked_on_the_card(self):
        card = _gd("order_confirm_card.gd")
        keep = _gd_func(card, "_dir_keep_the_lead")
        assert 'bool(r.get("locked", false))' in keep
        assert "_dir_ticks[lead] = true" in keep and "_dir_ticks[str(k)] = false" in keep
        assert "_dir_keep_the_lead(key)" in _gd_func(card, "_toggle_dir")
        assert "_dir_keep_the_lead(key)" in _gd_func(card, "_on_dir_ticked")

    def test_a_tasks_list_takes_the_wider_card_and_keeps_its_place_when_drawn_again(self):
        card = _gd("order_confirm_card.gd")
        assert "const CARD_WIDTH_TASK := 780.0" in card
        assert "return CARD_WIDTH_TASK" in _gd_func(card, "_authored_width")
        hold = _gd_func(card, "hold_for_redraw")
        assert "_dir_anchor = keep" in hold and '"reading": true' in hold
        main = _gd("main.gd")
        offer = _gd_func(main, "_on_directive_offer")
        assert "order_card.hold_for_redraw(" in offer and "close_given" not in offer

    def test_a_goals_list_may_be_given_with_nobody_ticked(self):
        card = _gd("order_confirm_card.gd")
        assert "(members.is_empty() and not goal_list)" in _gd_func(card, "_paint_directive")
        assert "if members.is_empty() and not is_goal_list():" in _gd_func(card, "_on_send")
        assert "(members.is_empty() and not names_only)" in _gd_func(_gd("main.gd"), "_send_directive")

    def test_the_chip_the_cards_and_the_desk_say_the_army_is_on_its_own(self):
        assert 'b.text += " · on its own"' in _gd("marshal_chip_row.gd")
        assert "task_key" in _gd_func(_gd("marshal_chip_row.gd"), "_army_signature_of"), \
            "a chip is drawn again when its army's task changes"
        card = _gd("selection_card.gd")
        own_row = _gd_func(card, "_own_row")
        assert ']Commands the " + army + "[/color]"' in own_row
        # ONE line for the army and the goal (his card stands whole); Session 4b:
        # no "Tonight" line — what he did this turn, his odds said once
        assert own_row.count('words += "\\n[color=#" + Utils.COLOR_GOLD + "]Commands the "') == 1
        assert 'own.get("this_turn", "")' in own_row and "Tonight" not in own_row
        assert own_row.count("He attacks only when the odds are ") == 1
        assert "]Follows \" + lead + \"[/color]" in _gd_func(card, "_follows_row")
        assert '"follows": _dict_of(ts.get("follows", {}))' in _gd("marshal_state.gd")
        assert '"ArmyTask", "Give it a task…"' in card and "army_task_pressed.emit(_army_name)" in card
        assert "the \" + str(army.get(\"name\", \"\")) + \", \"" in _gd_func(_gd("desk_lines.gd"), "_fill_own")

    def test_the_help_teaches_the_task_without_the_reserved_words(self):
        terms = _gd("codex_terms.gd")
        assert '["An army\'s task", "Give a named army a task' in terms
        assert '["Army of Italy, take Swabia", "A task for a named army' in terms
        assert '["Ney, take the war goal", "Gives him the war\'s goal as his task' in terms

    def test_the_offers_round_trip_leaves_the_card_in_the_players_hands(self):
        """The review (IC3B-V1 … V3). Source pins — the offer's order is on its way for a few
        milliseconds, and no walk of the real client can press Esc inside them."""
        main = _gd("main.gd")
        came_back = _gd_func(main, "_on_directive_offer_result")
        let_go = came_back.index("if order_card == null or not _order_card_open()")
        assert let_go < came_back.index("_open_directive_line(then, false)"), \
            "a card the player closed while the order was on its way is not opened again"
        # nothing is drawn behind a window the reply raised — ANOTHER window: the card is itself a
        # registered modal, and asking "is a modal open?" while it is up is always yes (this fix
        # was wrong so the first time: the list never came back, and the driven walk caught it)
        assert 'dialog_manager.is_any_modal_open_but("order_card")' in came_back
        assert "or not went or another_window:" in came_back
        assert "_is_modal_dialog_open()" not in came_back
        assert "str(key) != dialog_name and entry.modal" in _gd_func(_gd("dialog_manager.gd"),
                                                                    "is_any_modal_open_but")
        pressed = _gd_func(main, "_on_directive_offer")
        plain = pressed.index("_open_directive_line(line, false)")
        assert pressed.index("_directive_card_typed = typed", plain) > plain, \
            "Cancel on the plain list puts the typed line back too"
        assert '_directive_card_typed = ""' not in pressed, "Esc on the held card puts the typed line back"
        # a changed goal whose men cannot be turned is still a goal that Give names
        paint = _gd_func(_gd("order_confirm_card.gd"), "_paint_directive")
        assert paint.index("elif members.is_empty() and is_goal_list():") < paint.index("elif _dir_pick.is_empty():")
        assert "no man can be turned to it today" in paint

    def test_the_rows_are_measured_at_the_width_the_scroll_leaves_them(self):
        """IC3B-C10 (pressed at the first player's setup): a blank line stood under a row whose
        last words just fitted — the words were measured 6 px narrower than they are drawn."""
        measure = _gd_func(_gd("order_confirm_card.gd"), "_dir_rows_height")
        assert "_dir_scroll.get_v_scroll_bar().get_combined_minimum_size().x" in measure
        assert "var text_w := inner - bar_w" in measure


# ═══ the review before the commit (IC3B-V4 … V8) ════════════════════════════

class TestTheReviewsRows:

    def test_nobody_follows_a_commander_whose_own_line_could_not_be_read(self, client, world, monkeypatch):
        """IC3B-V4: a line the parser could not read never reached the stamp that stops the rest —
        and his men were sent (and charged) to follow a man with no task."""
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        # unread on the FAN-OUT only: the give's own check reads every row first (and would
        # answer "the list no longer holds") — the hole was past it, where a line fails late
        from backend.commands import group_orders as GO
        parser_class = type(M.parser)
        real_parse, real_run = parser_class.parse, GO._run_members
        on_the_road = {"now": False}

        def run(*args, **kwargs):
            on_the_road["now"] = True
            try:
                return real_run(*args, **kwargs)
            finally:
                on_the_road["now"] = False

        def unread_for_the_commander(self, line, *args, **kwargs):
            if on_the_road["now"] and str(line).startswith("Ney, take Swabia"):
                return {"success": False, "error": "The order could not be read."}
            return real_parse(self, line, *args, **kwargs)

        monkeypatch.setattr(GO, "_run_members", run)
        monkeypatch.setattr(parser_class, "parse", unread_for_the_commander)
        before = int(world.actions_remaining)
        reply = _give(client, listing)
        assert "did not take the task, so nobody follows him" in reply["message"], reply["message"]
        assert int(world.actions_remaining) == before, "nobody was charged"
        for name in ("Ney", "Davout", "Soult"):
            assert world.get_marshal(name).strategic_order is None, name
        assert AT.task_of(world, ARMY) == {}

    def test_the_commander_holds_the_task_before_any_man_is_sent_after_him(self, client, world):
        _form(client)
        stash = {"task": {"lead": "Ney", "army": ARMY}}
        assert AT.lead_stands(world, stash, "Ney") is True, "his own line is never held back"
        assert AT.lead_stands(world, stash, "Davout") is False, "he holds no task yet"
        _give(client, _ask(client, f"{ARMY}, take Swabia"), members=["Ney"])
        assert AT.lead_stands(world, stash, "Davout") is True
        assert AT.lead_stands(world, {"goal": {"court": "Austria"}}, "Davout") is True, "a goal's list has no commander"

    def test_no_stand_down_is_offered_where_a_freed_place_would_not_help(self, client, world):
        """IC3B-V5: the count full AND the named commander cannot be set on his own for another
        reason — the list offered to stand a man down for nothing, and blamed the count."""
        _form(client)
        assert _say(client, "Lannes, hold Lorraine on your own")["success"]     # the one place is taken
        world.get_marshal("Davout").trust.set(10)                               # ... and Davout is not trusted
        listing = _ask(client, f"{ARMY} under Davout, take Swabia")
        assert listing["sendable"] is False and "offer" not in listing, listing.get("offer")
        assert "You already have as many" not in listing["note"]
        assert listing["note"].startswith("Davout cannot take the army's task: ")
        assert "trust in you is 10" in listing["note"]

    def test_a_new_commander_named_over_the_old_one_is_said_before_give(self, client, world):
        """IC3B-V7: "… under Davout" while Ney commands — Ney's row said only "not included"."""
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        assert AT.task_of(world, ARMY)["lead"] == "Ney"
        listing = _ask(client, f"{ARMY} under Davout, take Swabia")
        ney = _row(listing, "Ney")
        assert ney["ok"] is False
        assert ney["why"] == (f"on his own: take Swabia — he keeps that task as his own, and commands "
                              f"the {ARMY} no longer")

    def test_a_disbanded_armys_commander_commands_nothing_and_a_new_army_of_its_name_is_not_his(
            self, client, world):
        """IC3B-V6: the mark on his task is the army's NAME — it outlived the army."""
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        ney, davout = world.get_marshal("Ney"), world.get_marshal("Davout")
        assert AT.following(world, davout) is ney
        reply = _say(client, f"disband the {ARMY}")
        assert reply["success"] and f"Ney commands the {ARMY} no longer" in reply["message"], reply["message"]
        assert "army" not in (O.own(ney) or {}) and O.on_his_own(ney), "he keeps his task as his own"
        assert AT.following(world, davout) is None and davout.strategic_order is not None, \
            "his men follow by an ordinary order"
        _form(client)                                             # a NEW army of the same name
        assert AT.following(world, davout) is None and AT.task_of(world, ARMY) == {}

    def test_a_commander_taken_out_of_his_army_leads_it_no_longer(self, client, world):
        _form(client)
        _give(client, _ask(client, f"{ARMY}, take Swabia"))
        reply = _say(client, f"remove Ney from the {ARMY}")
        assert reply["success"] and f"Ney commands the {ARMY} no longer" in reply["message"], reply["message"]
        assert AT.following(world, world.get_marshal("Davout")) is None
        assert AT.task_of(world, ARMY) == {}
        # the derived test itself asks BOTH to be its men (before any tidying runs)
        O.own(world.get_marshal("Ney"))["army"] = ARMY
        assert AT.following(world, world.get_marshal("Davout")) is None

    def test_a_goal_dropped_by_the_turns_pruning_lets_its_men_go(self, client, world):
        """IC3B-V8: the war ends, the goal is pruned — and the mark that he served it stayed."""
        first = TestTheWarGoal()._austrian(world, 1)[0]
        _say(client, f"the war goal is {first}")
        assert _say(client, "Ney, take the war goal")["success"]
        ney = world.get_marshal("Ney")
        court = str((O.own(ney) or {}).get("goal") or "")
        assert court and war_goals.serving(world) == [ney]
        # the goal has nothing left to aim at: the turn's own pruning drops it
        import backend.game_logic.war_goals as WG
        real = WG.status
        try:
            WG.status = lambda w, c, g: "gone" if c == court else real(w, c, g)
            said = WG.prune(world)
        finally:
            WG.status = real
        assert court not in world.war_goals
        assert any(line.startswith("Ney keeps to his task (take ") and "serves no war goal now" in line
                   for line in said), said
        assert "goal" not in (O.own(ney) or {}) and O.on_his_own(ney)
        assert war_goals.serving(world) == []

    def test_a_second_order_in_the_line_is_said_not_to_be_part_of_the_task(self, client):
        """IC3B-V9: "…, then hold Lorraine" was dropped without a word — for one man set on his
        own too, where the ordinary read-back says "a second order waits behind it"."""
        _form(client)
        said = "a second order is not part of his task: “hold Lorraine” — give it as a line of its own"
        assert said in _heads(_preview(client, "Ney, take Swabia then hold Lorraine on your own"), "warn")
        assert said in _heads(_preview(client, f"{ARMY}, take Swabia then hold Lorraine"), "warn")
        lead = _row(_ask(client, f"{ARMY}, take Swabia then hold Lorraine"), "Ney")
        assert said in lead["notes"] and lead["tones"][lead["notes"].index(said)] == "warn"
        assert not any("a second order" in t for t in _heads(_preview(client, f"{ARMY}, take Swabia"), "warn"))

    def test_the_mark_leaves_the_comma_that_sets_other_words_apart(self):
        """IC3B-X1 (found by the metamorphic corpus on this session's first golden row with a mark):
        the mark of judgement took the comma beside it — and a reason or a name set apart by
        that comma ran into the order, which was then no order at all."""
        from backend.ai import own_words as W
        assert W.set_aside_marks("Ney, take Swabia on your own, the men are rested") == (
            "Ney, take Swabia, the men are rested", ["on your own"])
        assert W.set_aside_marks("take Swabia on your own, Ney") == ("take Swabia, Ney", ["on your own"])
        assert W.set_aside_marks("Ney, take Swabia on your own") == ("Ney, take Swabia", ["on your own"])
        assert W.set_aside_marks("On your own, Ney, take Swabia")[0] == "Ney, take Swabia"
        # a how-bold word is the task's own: it rides with it, as it always did
        assert W.set_aside_marks("Davout, hold Rhineland on your own, carefully")[0] == (
            "Davout, hold Rhineland carefully")

    def test_the_lists_help_and_the_goals_note_say_the_two_things_the_readers_missed(self, client, world):
        """The blind reading's levers R3 and R6."""
        _form(client)
        listing = _ask(client, f"{ARMY}, take Swabia")
        assert listing["help"].startswith("Untick a follower to leave him out; untick Ney and nobody goes. ")
        first, second = TestTheWarGoal()._austrian(world)
        _say(client, f"the war goal is {first}")
        assert _say(client, "Ney, take the war goal")["success"]
        goal = _ask(client, f"the war goal is {second}")
        assert goal["say"].endswith("naming it is free. What costs is turning the 1 man who serves it: 1 action. "
                                    "A man you leave unticked keeps his old target and serves the goal no longer.")
