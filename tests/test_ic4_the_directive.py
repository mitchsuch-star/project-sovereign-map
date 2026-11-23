"""Row IC "Independent Command", the second commit (November 19, 2026) — IC-4: THE DIRECTIVE.

The user's ruling in Plan Mode: "One list for all" — any order to SEVERAL marshals (the collective words,
a list of names, a named army, a group selected on the map) is shown as ONE list first — each man's order,
its price, whether he may object — and sent on one confirmation, as one Take-back unit
(`backend/commands/directive.py`; `docs/SYSTEMS_REFERENCE.md` §230).

Pinned here, on the shipped 1805 board through the real endpoints:

* THE LIST IS THE TRUTH — the rows shown equal what the server does for the ticked rows; the price charged
  equals the total shown; an unticked row is never touched; a refused row costs nothing and is reported; a
  question stops the run and names who waits; one directive is one Take-back unit; a list that no longer
  holds is refused and drawn afresh; a man charged more than his row said puts the whole board back.
* READING IT CHANGES NOTHING — asking for the list writes nothing, casts no die, leaves Take back open and
  writes no history.
* ONE READER — each row is the read-back's own reading of that man's line.
* THE FUZZ — random who x what x ticks through the list and the give: no exception, a row a member, the
  cost never above the pool or the list, every row charged what it was quoted, and no saved key outside an
  order's own books moved.
* THE CENSUS (step 0) — every line to several corps in the committed scripts and the golden corpus, with how
  the reader takes it; the France band's script has none.

The real client is driven at the first player's own setup by
`tests/test_dd_b_the_client_hands.py::TestRowICDirectives`.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import random

import pytest

from backend.commands import directive as DV
from backend.commands import group_orders as G
from backend.commands import take_back as TB

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
CENSUS = REPO / "tests" / "data" / "directive_lines_census.json"

QUESTION_KEYS = ("pending_objection", "pending_strategic_objection", "pending_interrupt",
                 "requires_input", "awaiting_response", "clarification", "pending_glorious_charge",
                 "pending_capture_choice", "diplomatic_dialogue")
BATTLE_KEYS = ("battle_report", "battle_diorama", "battle_day", "combat_result")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _snapshot():
    from backend.models.world_state import WorldState
    with _quiet():
        return json.dumps(WorldState.from_scenario(str(SCENARIO)).to_dict(), default=str)


@pytest.fixture
def world(_snapshot):
    """The shipped 1805 board, a private copy per test."""
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_dict(json.loads(_snapshot))


@pytest.fixture
def client(world, monkeypatch):
    """The real endpoints on the shipped 1805 board (the keyless parser); the objection's mood roll and
    the defiance roll pinned flat (the project's rule for objection pins)."""
    import backend.commands.defiance as DEF
    import backend.main as main_module
    from backend.commands import executor as executor_mod
    from backend.commands import objection_v2 as ov2
    from backend.commands import strategic_executor as se_mod
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    flat = (lambda concern: concern)
    for module in (executor_mod, se_mod, ov2):
        monkeypatch.setattr(module, "apply_mood_variance", flat)
    monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(main_module, "world", world)
    monkeypatch.setattr(main_module, "game_state", {"world": world})
    with _quiet():
        monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))
    TB.new_board()
    yield TestClient(main_module.app)
    TB.new_board()


def _say(client, text: str, **extra) -> dict:
    with _quiet():
        return client.post("/command", json=dict({"command": text}, **extra)).json()


def _ask(client, text: str) -> dict:
    reply = _say(client, text, list_first=True)
    assert reply.get("directive"), reply.get("message")
    return reply["directive"]


def _give(client, listing: dict, members=None, **extra) -> dict:
    if members is None:
        members = [r["marshal"] for r in listing["rows"] if r["ticked"]]
    by = {r["marshal"]: r for r in listing["rows"]}
    expect = sum(int(by[n]["ap"]) for n in members)
    return _say(client, listing["line"], members=members, expect_ap=extra.pop("expect_ap", expect), **extra)


def _preview(client, line: str) -> dict:
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _quote(client, line: str, click: bool = False) -> dict:
    with _quiet():
        return client.get("/directive_quote",
                          params={"line": line, "click": "1" if click else ""}).json()


def _marshal_json(world, name: str) -> str:
    return json.dumps(world.get_marshal(name).to_dict(), sort_keys=True, default=str)


def _board_of(saved: dict) -> dict:
    """A save dict less the log of what was typed (a give that is refused is still a line the player
    sent — the history keeps it, as it keeps any refused order; nothing else may move)."""
    return {key: value for key, value in saved.items() if key != "command_history"}


def _board(world) -> dict:
    return _board_of(world.to_dict())


def _carries_a_question(reply: dict) -> bool:
    return (reply.get("state") in ("awaiting_player_choice", "awaiting_clarification")
            or any(reply.get(key) for key in QUESTION_KEYS))


# ═══ step 0: the census ══════════════════════════════════════════════════════

class TestTheCensus:
    """Every line to several corps in the committed scripts and the corpus, and how the reader takes it."""

    def test_the_census_is_current(self, client, world):
        import backend.main as main_module
        from tools import _ic_directive_census as census
        built = census.render(census.build(board=(main_module, world)))
        assert CENSUS.read_text(encoding="utf-8") == built, (
            "the directive census is stale — run tools/_ic_directive_census.py and read the diff")

    def test_the_bands_script_and_the_series_send_no_line_to_several(self):
        record = json.loads(CENSUS.read_text(encoding="utf-8"))
        assert record["band_script_lines"] == 0
        assert (REPO / "tools" / "playtest_scripts" / "commanded_full40.json").exists()
        # every row the reader takes is one of the four it knows
        assert {r["takes"] for r in record["rows"]} <= {"fan_out", "one_order", "answer", "none"}
        assert record["counts"]["by_takes"].get("fan_out", 0) >= 20


# ═══ who the line is for ═════════════════════════════════════════════════════

class TestWhoTheLineIsFor:
    @pytest.mark.parametrize("line, kind, names, rest", [
        ("everyone, fortify", "everyone", [], "fortify"),
        ("all marshals march to Swabia", "everyone", [], "march to Swabia"),
        ("the army marches on Swabia", "everyone", [], "march to Swabia"),
        ("everyone stop", "everyone", [], "stop"),
        ("Ney and Davout, fortify", "list", ["Ney", "Davout"], "fortify"),
        ("Ney, Lannes and Murat, march to Ulm", "list", ["Ney", "Lannes", "Murat"], "march to Ulm"),
        ("Ney and Davout will fortify", "list", ["Ney", "Davout"], "fortify"),
        ("Lannes and Murat, both of you move to Rhineland", "list", ["Lannes", "Murat"],
         "move to Rhineland"),
    ])
    def test_the_address_is_read_from_the_words(self, world, line, kind, names, rest):
        found = DV.address(world, line)
        assert found is not None and found["kind"] == kind, found
        assert found["names"] == names and found["rest"] == rest, found

    def test_the_corps_at_a_province(self, world):
        found = DV.address(world, "everyone at Lorraine, fortify")
        assert (found["kind"], found["at"], found["rest"]) == ("at", "Lorraine", "fortify")

    @pytest.mark.parametrize("line", [
        "Ney, fortify", "Ney, support Davout", "Lannes support Ney, Murat support Lannes",
        "grant Ney and Murat a rente", "status", "what can Ney do", "",
    ])
    def test_an_order_to_one_man_or_to_nobody_is_none(self, world, line):
        assert DV.address(world, line) is None

    def test_the_seam_down_a_list_is_no_address(self, world, monkeypatch):
        monkeypatch.setattr(DV, "a_named_list_is_one_directive", lambda: False)
        assert DV.address(world, "Ney and Davout, fortify") is None
        assert DV.address(world, "everyone, fortify")["kind"] == "everyone"   # the collective is AO's

    def test_an_attack_by_a_list_stays_one_battle(self, client, world):
        """The plan: "Attack stays one battle (the first man leads, the muster calls the others)".
        Sharpened by the review: the old pin passed on any reply that named Soult."""
        before = int(world.actions_remaining)
        soult_was = world.get_marshal("Soult").location
        reply = _say(client, "Ney and Soult, attack Mack", list_first=True)
        assert not reply.get("directive") and not reply.get("group")    # never listed, never fanned out
        battles = [e for e in reply.get("events") or [] if e.get("type") == "battle"]
        assert len(battles) == 1 and reply.get("battle_report"), reply.get("events")   # ONE battle …
        assert reply["message"].startswith("MUSTER — Ney")                               # … Ney leads it
        assert reply.get("relay_command") == "Soult, support Ney"       # Soult's own order handed back
        assert world.get_marshal("Soult").location == soult_was         # he did not attack on his own
        assert int(world.actions_remaining) == before - 1               # one attack's price


# ═══ the list ════════════════════════════════════════════════════════════════

class TestTheList:
    def test_asking_shows_the_list_and_does_nothing(self, client, world):
        before = world.to_dict()
        dice = random.getstate()
        history = len(world.command_history)
        reply = _say(client, "everyone, fortify", list_first=True)
        listing = reply["directive"]
        assert reply["success"] is True and reply["message"] == ""
        assert not reply.get("group")                      # nothing was carried out
        assert world.to_dict() == before                   # nothing written …
        assert random.getstate() == dice                   # … no die cast …
        assert len(world.command_history) == history       # … no history entry
        assert reply["action_info"]["cost"] == 0
        field = [m.name for m in world.get_field_marshals()]
        assert [r["marshal"] for r in listing["rows"]] == field
        assert listing["who"] == "Every corps" and listing["order"] == "fortify"
        assert listing["line"] == "everyone, fortify" and listing["have"] == 4

    def test_the_read_only_road_gives_the_same_list_and_writes_nothing(self, client, world):
        before = world.to_dict()
        dice = random.getstate()
        got = _quote(client, "Ney, Davout and Soult, march to Lorraine")
        assert got["success"] and world.to_dict() == before and random.getstate() == dice
        assert got["directive"] == _ask(client, "Ney, Davout and Soult, march to Lorraine")

    def test_the_ticks_go_while_the_actions_last(self, client, world):
        listing = _ask(client, "everyone, fortify")
        ticked = [r for r in listing["rows"] if r["ticked"]]
        assert sum(r["ap"] for r in ticked) == listing["total"] <= listing["have"]
        # the next man who could go would not fit
        rest = [r for r in listing["rows"] if r["ok"] and not r["ticked"]]
        assert rest and all(listing["total"] + r["ap"] > listing["have"] for r in rest[:1])

    def test_a_man_who_will_not_go_says_why_and_wears_no_tick(self, client, world):
        listing = _ask(client, "Ney, Davout and Soult, march to Lorraine")
        rows = {r["marshal"]: r for r in listing["rows"]}
        assert world.get_marshal("Soult").location == "Lorraine"
        assert rows["Soult"]["ok"] is False and rows["Soult"]["ticked"] is False
        assert rows["Soult"]["why"] == "already stands at Lorraine"
        assert rows["Ney"]["ok"] and rows["Ney"]["says"] == "march to Lorraine"
        assert listing["who"] == "Ney, Davout and Soult"

    def test_each_row_is_the_read_backs_own_reading_of_that_line(self, client, world):
        """ONE reader: the list, the read-back and the price check cannot drift."""
        for line in ("everyone, march to Swabia", "everyone, fortify", "Ney, Murat and Lannes, hold",
                     "everyone, drill"):
            for row in _ask(client, line)["rows"]:
                one = _preview(client, row["line"])
                assert row["ok"] == (one["kind"] == "order" and one["ok"]), (line, row, one)
                if row["ok"]:
                    assert (row["ap"], row["turns"], row["objection"]) == (
                        one["ap"], one["turns"], one["objection"]), (line, row["marshal"])

    def test_a_group_sent_by_a_click_takes_each_mans_own_plain_order(self, client, world):
        """Row PW's rule on the group: a move next door is the one-action move, as his single click
        sends it — where the typed march charges the standing order's two."""
        clicked = _quote(client, "Ney, Davout and Soult, march to Lorraine", click=True)["directive"]
        typed = _ask(client, "Ney, Davout and Soult, march to Lorraine")
        for name in ("Ney", "Davout"):
            with _quiet():
                single = client.get("/march_quotes", params={"marshal": name, "dest": "Lorraine"}).json()["quote"]
            row = next(r for r in clicked["rows"] if r["marshal"] == name)
            assert row["line"] == single["command"] and row["ap"] == single["ap"] == 1, (row, single)
            assert "move to Lorraine" in row["says"]
            assert next(r for r in typed["rows"] if r["marshal"] == name)["ap"] == 2
        assert clicked["click"] is True and clicked["total"] == 2
        # the head says neither "march" nor "move" of a click group — its rows say which
        assert clicked["order"] == "go to Lorraine" and typed["order"] == "march to Lorraine"

    def test_an_orders_own_notes_reach_its_row(self, client, world):
        """The review: the re-seated card pins check only the riders' names (`_RIDERS`); a quote's riders
        must reach a row's notes — the typed road (the read-back's quote) and the click road alike."""
        typed = _ask(client, "Ney, Davout and Soult, march to Vienna")
        ney = next(r for r in typed["rows"] if r["marshal"] == "Ney")
        assert any("Mack blocks the road at Swabia" in note for note in ney["notes"]), ney   # `contact`
        clicked = _quote(client, "Bernadotte, Massena and Murat, march to Lorraine", click=True)["directive"]
        massena = next(r for r in clicked["rows"] if r["marshal"] == "Massena")
        assert any(note.startswith("The first march costs") for note in massena["notes"]), massena   # `march_cost`

    def test_no_row_says_where_a_man_out_of_sight_stands(self, client, world):
        from backend.game_logic.intel_surfaces import in_sight
        player = world.player_nation
        hidden = next(m for m in world.marshals.values()
                      if m.nation != player and int(m.strength or 0) > 0
                      and world.is_at_war(player, m.nation) and not in_sight(world, player, m))
        reply = _say(client, f"everyone, pursue {hidden.name}", list_first=True)
        text = json.dumps({"directive": reply.get("directive"), "message": reply.get("message")})
        assert str(hidden.location) not in text, text[:400]
        if reply.get("directive"):
            assert not reply["directive"]["sendable"]
            assert all(not r["ok"] and not r["ticked"] for r in reply["directive"]["rows"])

    def test_one_corps_is_no_list(self, client, world):
        """An address that reaches one man is his order — carried out at once, as before."""
        by_place: dict = {}
        for m in world.get_field_marshals():
            by_place.setdefault(m.location, []).append(m.name)
        place, (alone,) = next((p, names) for p, names in by_place.items() if len(names) == 1)
        reply = _say(client, f"everyone at {place}, wait", list_first=True)
        assert not reply.get("directive")                  # never listed …
        assert reply["group"]["rows"] == [                 # … it went, as one man's order
            {"marshal": alone, "sent": True, "line": f"{alone}, wait", "why": "", "ap": 0}]

    def test_everyone_stop_lists_each_recall_with_its_price_and_trust(self, client, world):
        for name in ("Ney", "Davout"):
            assert _say(client, f"{name}, march to Lorraine")["success"]
        world.actions_remaining = 4
        listing = _ask(client, "everyone stop")
        assert listing["order"] == "recall their standing orders"
        rows = {r["marshal"]: r for r in listing["rows"]}
        assert set(rows) == {"Ney", "Davout"}
        for row in rows.values():
            assert row["ok"] and row["ap"] == 1 and row["says"] == "recall his march"
            assert row["notes"] == ["No trust lost — the order was given this turn."]
        done = _give(client, listing)
        assert done["success"] and world.get_marshal("Ney").strategic_order is None
        assert world.get_marshal("Davout").strategic_order is None and done["action_info"]["cost"] == 2


# ═══ the give: the list is the truth ═════════════════════════════════════════

class TestTheListIsTheTruth:
    def test_the_rows_shown_are_what_is_done_and_the_price_is_the_total(self, client, world):
        world.actions_remaining = 12
        listing = _ask(client, "everyone, fortify")
        members = [r["marshal"] for r in listing["rows"] if r["ok"] and r["objection"] == "none"]
        assert len(members) >= 3
        untouched = {r["marshal"]: _marshal_json(world, r["marshal"])
                     for r in listing["rows"] if r["marshal"] not in members}
        reply = _give(client, listing, members=members)
        assert reply["success"], reply["message"]
        rows = {r["marshal"]: r for r in reply["group"]["rows"]}
        by = {r["marshal"]: r for r in listing["rows"]}
        for name in members:
            assert rows[name]["sent"] is True and rows[name]["line"] == by[name]["line"]
            assert rows[name]["ap"] == by[name]["ap"]              # charged what the row said
            assert world.get_marshal(name).fortified is True
        assert reply["action_info"]["cost"] == sum(by[n]["ap"] for n in members)
        assert world.actions_remaining == 12 - reply["action_info"]["cost"]
        # an unticked row is never touched — and is reported as not ticked
        for name, was in untouched.items():
            assert _marshal_json(world, name) == was, name
            assert rows[name] == {"marshal": name, "sent": False, "line": "", "why": "not ticked", "ap": 0}

    def test_the_reply_names_the_men_it_went_to(self, client, world):
        listing = _ask(client, "Davout and Soult, fortify")
        reply = _give(client, listing)
        assert "The order goes to Davout and Soult, corps by corps — 2 corps, 4 actions for the 4 in hand" \
            in reply["message"]

    def test_the_typed_roads_head_prices_a_fortify_as_the_executor_charges_it(self, client, world):
        """IC-D10, rule 10's sibling of S14G-X167 (found by the war-table walk): the typed fan-out — no
        list asked, as a script sends it — priced each fortify from a NEUTRAL stance at the table's one
        action ("2 corps, 2 actions for the 4 in hand") while the executor charged two (the stance first);
        its pool check let a man go whom the executor then refused for want of the second action."""
        for name in ("Davout", "Soult"):
            assert world.get_marshal(name).stance.name == "NEUTRAL"
        reply = _say(client, "Davout and Soult, fortify")
        assert "2 corps, 4 actions for the 4 in hand" in reply["message"], reply["message"]
        assert reply["action_info"]["cost"] == 4
        world.actions_remaining = 3
        for name in ("Davout", "Soult"):
            world.get_marshal(name).fortified = False
            world.get_marshal(name).stance = type(world.get_marshal(name).stance).NEUTRAL
        reply = _say(client, "Davout and Soult, fortify")
        rows = {r["marshal"]: r for r in reply["group"]["rows"]}
        assert rows["Davout"]["sent"] and rows["Soult"]["why"] == "the actions were spent before him"
        assert "Nothing left for Soult today" in reply["message"], reply["message"]

    def test_a_renewed_hold_with_a_new_watch_goes_as_its_row_said(self, client, world):
        """IC4-N1's sibling (row IC, Session 4b): the list's run read the hold's
        refusal WITHOUT the typed line — "already holding here" for a man who
        holds his ground — while his row (read with the line) said it goes. A
        hold with a new if-then is a new order on both roads; the same hold
        again is refused, free, on both."""
        world.actions_remaining = 12
        for name in ("Davout", "Soult"):
            assert _say(client, f"{name}, hold")["success"]
        line = "Davout and Soult, hold. If attacked, dig in."
        listing = _ask(client, line)
        rows = {r["marshal"]: r for r in listing["rows"]}
        assert rows["Davout"]["ok"] and rows["Soult"]["ok"], listing["rows"]
        reply = _give(client, listing)
        assert reply["success"], reply["message"]
        sent = {r["marshal"]: r for r in reply["group"]["rows"]}
        assert sent["Davout"]["sent"] and sent["Soult"]["sent"], reply["group"]["rows"]
        again = _say(client, line)
        rows = {r["marshal"]: r for r in again["group"]["rows"]}
        for name in ("Davout", "Soult"):
            assert rows[name]["sent"] is False and rows[name]["ap"] == 0, rows[name]

    def test_a_refused_row_costs_nothing_and_is_reported(self, client, world):
        """The collective's own rule, on a list: Soult stands at Lorraine already."""
        world.actions_remaining = 12
        reply = _say(client, "Ney, Davout and Soult, march to Lorraine")       # no list asked: it goes
        rows = {r["marshal"]: r for r in reply["group"]["rows"]}
        assert rows["Soult"]["sent"] is False and rows["Soult"]["ap"] == 0
        assert "already" in rows["Soult"]["why"]
        assert rows["Ney"]["sent"] and rows["Davout"]["sent"]
        assert reply["action_info"]["cost"] == rows["Ney"]["ap"] + rows["Davout"]["ap"]
        assert "Soult" in reply["message"]

    def test_a_question_stops_the_run_and_names_who_waits(self, client, world):
        """An aggressive Ney asked to fortify in reach of Mack objects (the roll pinned flat): he asks
        the player himself, Soult waits behind his question and goes on when it is answered."""
        listing = _ask(client, "Ney and Soult, fortify")
        assert next(r for r in listing["rows"] if r["marshal"] == "Ney")["objection"] == "possible"
        reply = _give(client, listing)
        assert _carries_a_question(reply), reply["message"]
        rows = {r["marshal"]: r for r in reply["group"]["rows"]}
        assert rows["Ney"].get("asked") is True and rows["Ney"]["sent"] is False
        assert rows["Soult"]["sent"] is False and rows["Soult"]["why"] == "waits behind Ney's question"
        assert "The order waits for Soult behind Ney's question." in reply["message"]
        assert world.get_marshal("Soult").fortified is False
        with _quiet():
            answered = client.post("/respond_to_objection", json={"choice": "insist"}).json()
        assert "The order goes on." in answered["message"], answered["message"]
        assert world.get_marshal("Soult").fortified is True and world._pending_group is None

    def test_the_question_leaves_who_went_and_who_waits_for_the_log(self, client, world):
        """The driven war-table walk found it (IC-D2): the question's window carries only the question,
        so the order's head and who waits were never shown. `group.said` is the reply less the question's
        own words — the client says it before the window."""
        listing = _ask(client, "Ney and Soult, fortify")
        reply = _give(client, listing)
        assert _carries_a_question(reply), reply["message"]
        said = reply["group"]["said"]
        lines = said.splitlines()
        assert lines[0].startswith("The order goes to Ney and Soult, corps by corps")
        assert lines[-1] == "The order waits for Soult behind Ney's question."
        assert all(line in reply["message"].splitlines() for line in lines)
        asked = [line for line in reply["message"].splitlines() if line not in lines]
        assert asked and not any(line in said for line in asked)       # the question is the window's
        assert "said" not in (_give(client, _ask(client, "Davout and Soult, fortify"))["group"])  # no question, no said

    def test_a_list_stopped_by_a_question_is_headed_at_the_prices_it_showed(self, client, world, monkeypatch):
        """IC-D3, found by the same walk: a question pops the list's prices off the stash (the men who
        wait go on later at their own price), and the head — built after the run — then priced the order
        at the TYPED march: "5 actions for the 4 in hand" beside a list that said 4. The head reads the
        prices the list showed. (Davout's question is forced: the click group moves Ney and Davout next
        door at one action each, where the typed march costs each two.)"""
        import backend.main as main_module
        clicked = _quote(client, "Ney, Davout and Soult, march to Lorraine", click=True)["directive"]
        assert clicked["total"] == 2
        real, calls = main_module._result_carries_question, []

        def davout_asks(result):
            calls.append(1)
            return True if len(calls) == 2 else real(result)
        monkeypatch.setattr(main_module, "_result_carries_question", davout_asks)
        reply = _give(client, clicked, click=True)
        head = reply["message"].splitlines()[0]
        assert "2 corps, 2 actions for the" in head, head
        assert reply["group"]["said"].splitlines()[0] == head

    def test_a_list_that_no_longer_holds_is_refused_and_drawn_afresh(self, client, world):
        listing = _ask(client, "Davout and Soult, fortify")
        assert listing["total"] == 4
        world.actions_remaining = 3                                 # the board moves on: an action is spent
        before = world.to_dict()
        reply = _give(client, listing)
        assert reply["success"] is False and reply["directive_stale"] is True
        assert "needs 4 actions and 3 remain" in reply["message"] and "Nothing was sent" in reply["message"]
        assert _board(world) == _board_of(before) and reply["action_info"]["cost"] == 0
        fresh = reply["directive"]
        assert fresh["have"] == 3 and fresh["total"] == 2            # the list as it stands now

    def test_a_price_other_than_the_one_seen_is_refused(self, client, world):
        listing = _ask(client, "Davout and Soult, fortify")
        before = world.to_dict()
        reply = _give(client, listing, expect_ap=1)
        assert reply["success"] is False and reply["directive_stale"] is True
        assert "The price has changed since the list was drawn" in reply["message"]
        assert _board(world) == _board_of(before)

    def test_a_ticked_man_who_cannot_go_is_refused_whole(self, client, world):
        listing = _ask(client, "Ney, Davout and Soult, march to Lorraine")
        before = world.to_dict()
        reply = _give(client, listing, members=["Ney", "Soult"], expect_ap=2)
        assert reply["success"] is False and reply["directive_stale"] is True
        assert "Soult can no longer take this order" in reply["message"]
        assert _board(world) == _board_of(before)

    def test_a_request_with_members_never_reaches_the_ordinary_executor(self, client, world):
        before = world.to_dict()
        reply = _say(client, "Ney, fortify", members=["Ney", "Davout"], expect_ap=2)
        assert reply["success"] is False
        assert "cannot be given to several corps as one list" in reply["message"]
        assert _board(world) == _board_of(before)
        assert world.get_marshal("Ney").fortified is False and world.actions_remaining == 4

    def test_a_list_directive_leaves_no_relay_behind(self, client, world):
        """The parser still reads a list as "the first man, the rest handed back"; once the list has
        gone as ONE order that reading is let go — no man is handed his order a second time."""
        world.actions_remaining = 12
        listing = _ask(client, "Davout, Soult and Napoleon, fortify")
        reply = _give(client, listing)
        assert "relay_command" not in reply and not reply.get("dropped_sequel")
        assert "waits behind it" not in reply["message"] and "You named" not in reply["message"]
        assert all(world.get_marshal(n).fortified for n in ("Davout", "Soult", "Napoleon"))

    def test_the_click_group_goes_as_the_list_said(self, client, world):
        clicked = _quote(client, "Ney, Davout and Soult, march to Lorraine", click=True)["directive"]
        reply = _give(client, clicked, click=True)
        assert reply["success"] and reply["action_info"]["cost"] == clicked["total"] == 2
        assert world.get_marshal("Ney").location == "Lorraine"
        assert world.get_marshal("Davout").location == "Lorraine"
        assert [r["line"] for r in reply["group"]["rows"] if r["sent"]] == [
            "Ney, move to Lorraine", "Davout, move to Lorraine"]

    def test_the_seam_down_the_list_rides_the_relay_even_when_asked_first(self, client, world, monkeypatch):
        monkeypatch.setattr(DV, "a_named_list_is_one_directive", lambda: False)
        reply = _say(client, "Davout and Soult, fortify", list_first=True)
        assert not reply.get("directive")
        assert world.get_marshal("Davout").fortified is True
        assert world.get_marshal("Soult").fortified is False
        assert reply.get("relay_command") == "Soult, fortify"


# ═══ one Take-back unit ══════════════════════════════════════════════════════

class TestOneTakeBackUnit:
    def test_one_directive_is_one_take_back(self, client, world):
        before = world.to_dict()
        reply = _give(client, _ask(client, "Davout and Soult, fortify"))
        assert reply["undo"]["available"] is True and reply["undo"]["kept"] == 1
        with _quiet():
            back = client.post("/undo").json()
        assert back["success"] and back["taken_back"] is True
        after = world.to_dict()
        for key in ("marshals", "actions_remaining", "regions", "gold"):
            assert after[key] == before[key], key
        assert world.actions_remaining == 4

    def test_asking_for_a_list_leaves_a_kept_order_kept(self, client, world):
        first = _say(client, "Soult, fortify")
        assert first["undo"]["available"] is True
        asked = _say(client, "everyone, drill", list_first=True)
        assert asked.get("directive") and asked["undo"] == first["undo"]

    def test_the_give_writes_one_line_of_history_and_the_ask_none(self, client, world):
        start = len(world.command_history)
        listing = _ask(client, "Davout and Soult, fortify")
        assert len(world.command_history) == start
        _give(client, listing)
        assert len(world.command_history) == start + 1
        assert world.command_history[-1]["raw_input"] == "Davout and Soult, fortify"

    def test_a_voiced_small_concern_no_longer_closes_take_back(self, client, world, monkeypatch):
        """IC-D1 (the sibling of "one directive is one Take-back unit"): Ney grumbles as he complies —
        no popup, no answer asked — and that remark alone made the order stand."""
        from backend.commands import executor as executor_mod
        from backend.commands.objection_v2 import ConcernLevel
        monkeypatch.setattr(executor_mod, "apply_mood_variance",
                            lambda concern: concern if concern == ConcernLevel.NONE else ConcernLevel.MILD)
        assert "mild_concerns_this_turn" in TB.ORDER_KEYS
        reply = _say(client, "Ney, fortify")
        assert reply["success"] and not _carries_a_question(reply), reply["message"]
        assert world.mild_concerns_this_turn, "the pin needs a concern that was voiced"
        assert reply["undo"]["available"] is True, reply["undo"]
        with _quiet():
            assert client.post("/undo").json()["taken_back"] is True
        assert world.get_marshal("Ney").fortified is False and not world.mild_concerns_this_turn


# ═══ the guard ═══════════════════════════════════════════════════════════════

class TestTheGuard:
    def test_a_man_charged_more_than_his_row_said_puts_the_board_back(self, client, world, monkeypatch):
        """Patched at the CLASS (the project's rule for the server's singletons): Soult's order comes
        back one action dearer than the list said."""
        import backend.main as main_module
        listing = _ask(client, "Davout and Soult, fortify")
        executor_type = type(main_module.executor)
        real = executor_type.execute

        def dearer(self, parsed, game_state):
            result = real(self, parsed, game_state)
            if (parsed.get("command") or {}).get("marshal") == "Soult" and isinstance(
                    result.get("action_info"), dict):
                result["action_info"]["cost"] = int(result["action_info"].get("cost") or 0) + 1
            return result

        monkeypatch.setattr(executor_type, "execute", dearer)
        before = world.to_dict()
        dice = random.getstate()
        reply = _give(client, listing)
        assert reply["success"] is False and reply["directive_stale"] is True
        assert "would have cost more than the list said" in reply["message"]
        assert _board(world) == _board_of(before)
        assert random.getstate() == dice
        assert world.get_marshal("Davout").fortified is False        # Davout's own order is undone too
        assert world.actions_remaining == 4 and world._pending_group is None

    def test_the_most_a_give_can_cost_is_the_total_shown(self, world):
        listing = {"rows": [{"marshal": "A", "ap": 2, "ok": True}, {"marshal": "B", "ap": 1, "ok": True}],
                   "staff": None, "have": 4}
        assert DV.total_for(listing, ["A", "B"]) == 3 and DV.stale(listing, ["A", "B"], 3) == ""
        staff = dict(listing, staff={"ap": 2, "covers": ["A", "B"]})
        assert DV.total_for(staff, ["A", "B"]) == 2          # the Staff's one price: its whole column …
        assert DV.total_for(staff, ["A"]) == 2               # … and each man's own once a man is left out


# ═══ the Staff's one order ═══════════════════════════════════════════════════

class TestTheStaffsOneOrder:
    def _staff_on(self, world):
        from backend.game_logic import reforms
        row = next(r for r in reforms.deck(world, world.player_nation) if reforms.is_staff(r))
        row["enacted_turn"] = world.current_turn
        assert reforms.staff_actions(world, world.player_nation) == 1

    def test_the_whole_column_ticked_rides_the_staffs_price(self, client, world):
        self._staff_on(world)
        have = int(world.actions_remaining)
        listing = _ask(client, "everyone, march to Franconia")
        staff = listing["staff"]
        assert staff and staff["ap"] == G.ARMY_ORDER_AP and listing["total"] == G.ARMY_ORDER_AP
        covered = [r["marshal"] for r in listing["rows"] if r["covered"]]
        assert covered == staff["covers"] and all(
            r["ticked"] for r in listing["rows"] if r["covered"])
        reply = _say(client, listing["line"], members=covered, expect_ap=listing["total"])
        if not _carries_a_question(reply):
            assert reply["action_info"]["cost"] == G.ARMY_ORDER_AP
            assert world.actions_remaining == have - G.ARMY_ORDER_AP
            assert reply["group"]["army"] is True

    def test_one_man_left_out_and_each_goes_at_his_own_price(self, client, world):
        self._staff_on(world)
        world.actions_remaining = 20
        listing = _ask(client, "everyone, march to Franconia")
        covered = listing["staff"]["covers"]
        assert len(covered) >= 3
        fewer = covered[:-1]
        by = {r["marshal"]: r for r in listing["rows"]}
        own = sum(by[n]["ap"] for n in fewer)
        assert DV.total_for(listing, fewer) == own > G.ARMY_ORDER_AP
        # the Staff's price is refused for a column with a man left out …
        stale = _say(client, listing["line"], members=fewer, expect_ap=G.ARMY_ORDER_AP)
        assert stale["success"] is False and stale["directive_stale"] is True
        # … and each man's own price is taken
        reply = _say(client, listing["line"], members=fewer, expect_ap=own)
        if not _carries_a_question(reply):
            assert reply["group"]["army"] is False and reply["action_info"]["cost"] == own


# ═══ the read-back ═══════════════════════════════════════════════════════════

class TestTheReadBack:
    def test_a_line_to_several_reads_as_the_list_it_will_open(self, client, world):
        got = _preview(client, "Davout and Soult, fortify")
        assert got["kind"] == "order" and got["directive"] is True and got["action"] == "fortify"
        said = [p["text"] for p in got["parts"]]
        assert said[0] == "Davout and Soult · fortify · 2 corps"
        assert said[1] == "4 actions for the 4 in hand" and said[-1] == "Enter shows the list"
        many = _preview(client, "everyone, fortify")
        assert many["directive"] is True and many["parts"][0]["text"] == "Every corps · fortify · 8 corps"

    def test_it_says_how_many_will_not_go(self, client, world):
        got = _preview(client, "Ney, Davout and Soult, march to Lorraine")
        said = [p["text"] for p in got["parts"]]
        assert said[0] == "Ney, Davout and Soult · march to Lorraine · 2 corps" and "1 will not go" in said

    def test_an_order_to_one_man_is_no_directive(self, client, world):
        assert _preview(client, "Ney, fortify")["directive"] is False
        assert _preview(client, "Ney and Soult, attack Mack")["directive"] is False

    def test_reading_it_writes_nothing(self, client, world):
        before = world.to_dict()
        dice = random.getstate()
        for line in ("everyone, fortify", "Davout and Soult, hold", "everyone, march to Swabia"):
            _preview(client, line)
        assert world.to_dict() == before and random.getstate() == dice


# ═══ the reader's own gaps, found by the fuzz and closed at the reader ═══════

class TestTheReaderMeetsTheExecutorsGates:
    """IC-D2 … IC-D5: the read-back the list reuses priced four orders the game then refused, or charged
    more for. Each is closed where the reading is made, so a single typed order reads right too."""

    def test_a_move_beyond_one_march_is_the_march_and_is_priced_as_it(self, client, world):
        massena = world.get_marshal("Massena")
        far = next(name for name in world.regions
                   if world.get_distance(massena.location, name) == 3
                   and world.get_region(name).controller == world.player_nation)
        got = _preview(client, f"Massena, move to {far}")
        assert got["kind"] == "order" and got["ap"] == massena.strategic_order_ap(order_type="MOVE_TO")
        assert "too far for one move — he marches there" in [p["text"] for p in got["parts"]]
        before = int(world.actions_remaining)
        reply = _say(client, f"Massena, move to {far}")
        if reply["success"] and not _carries_a_question(reply):
            assert before - int(world.actions_remaining) == got["ap"]

    def test_a_move_to_where_he_stands_is_refused_as_the_game_refuses_it(self, client, world):
        got = _preview(client, "Soult, move to Lorraine")
        assert got["kind"] == "refusal" and got["refusal"] == "Soult — is already in Lorraine"
        assert _say(client, "Soult, move to Lorraine")["success"] is False
        assert world.actions_remaining == 4

    def test_a_cavalryman_is_not_quoted_a_square(self, client, world):
        murat = world.get_marshal("Murat")
        assert getattr(murat, "cavalry", False)
        got = _preview(client, "Murat, form square")
        assert got["kind"] == "refusal" and "cavalry cannot form an infantry square" in got["refusal"]
        assert _say(client, "Murat, form square")["success"] is False

    def test_a_scout_beyond_his_reach_is_refused(self, client, world):
        from backend.commands.movement_executor import scout_range
        ney = world.get_marshal("Ney")
        far = next(name for name in world.regions
                   if world.get_distance(ney.location, name) == scout_range(ney) + 1)
        got = _preview(client, f"Ney, scout {far}")
        assert got["kind"] == "refusal" and "too far to scout" in got["refusal"]
        assert _say(client, f"Ney, scout {far}")["success"] is False

    def test_everyone_wait_is_free_with_no_action_left(self, client, world):
        """`wait` is never priced by the executor; the fan-out counted an action a corps and said "the
        pool is spent" of an order that costs nothing."""
        world.actions_remaining = 0
        listing = _ask(client, "everyone, wait")
        calm = [r["marshal"] for r in listing["rows"] if r["ok"] and r["objection"] == "none"]
        assert len(calm) >= 2 and all(r["ap"] == 0 for r in listing["rows"] if r["ok"])
        reply = _say(client, f"{calm[0]} and {calm[1]}, wait")          # no list asked: it goes
        assert "Nothing left for" not in reply["message"]
        assert "2 corps, 0 actions for the 0 in hand" in reply["message"]
        assert all(r["sent"] for r in reply["group"]["rows"]) and reply["action_info"]["cost"] == 0


# ═══ the fuzz ════════════════════════════════════════════════════════════════

class TestTheFuzz:
    """Random directives — who x what x ticks — through the list and the give."""

    ORDERS = ("fortify", "unfortify", "drill", "defend", "hold", "wait", "garrison", "stop",
              "scout {near}", "move to {near}", "march to {far}", "march to {near}",
              "support {who}", "follow {who}", "hold {near}", "form square")

    @pytest.mark.parametrize("seed", [1805, 1812])
    def test_what_the_list_says_is_what_happens(self, client, _snapshot, monkeypatch, seed):
        import backend.main as main_module
        from backend.models.world_state import WorldState
        rng = random.Random(seed)
        given = 0
        for _round in range(45):
            with _quiet():
                world = WorldState.from_dict(json.loads(_snapshot))
            monkeypatch.setattr(main_module, "world", world)
            monkeypatch.setattr(main_module, "game_state", {"world": world})
            TB.new_board()
            ours = [m.name for m in world.get_field_marshals()]
            world.actions_remaining = rng.choice([0, 1, 2, 3, 4, 4, 6, 12])
            who = rng.choice(ours)
            here = world.get_marshal(who).location
            near = rng.choice(sorted(world.get_region(here).adjacent_regions))
            order = rng.choice(self.ORDERS).format(near=near, far=rng.choice(sorted(world.regions)),
                                                   who=who)
            form = rng.choice(["everyone", "list", "list", "at", "click"])
            click = form == "click"
            if form == "everyone":
                line = f"everyone, {order}"
            elif form == "at":
                line = f"everyone at {here}, {order}"
            else:
                chosen = rng.sample(ours, rng.randint(2, min(5, len(ours))))
                line = ", ".join(chosen[:-1]) + " and " + chosen[-1] + ", " + order
            pool = int(world.actions_remaining)
            if click:
                listing = _quote(client, line, click=True).get("directive")
            else:
                listing = _say(client, line, list_first=True).get("directive")
            if listing is None:
                continue          # no order to several: it went (or was refused) as the game always took it
            assert int(world.actions_remaining) == pool, line          # asking spends nothing
            addressed = len(listing["rows"])
            assert addressed >= 2, line
            can_go = [r for r in listing["rows"] if r["ok"]]
            picked, left = [], int(listing["have"])
            for row in rng.sample(can_go, len(can_go)):
                if row["ap"] <= left and rng.random() < 0.7:
                    picked.append(row["marshal"])
                    left -= row["ap"]
            members = [r["marshal"] for r in listing["rows"] if r["marshal"] in picked]
            if not members:
                continue
            by = {r["marshal"]: r for r in listing["rows"]}
            staff = listing.get("staff")
            expect = DV.total_for(listing, members)
            before = world.to_dict()
            untouched = {n: _marshal_json(world, n) for n in by if n not in members}
            reply = _say(client, listing["line"], members=members, expect_ap=expect, click=click)
            world = main_module.world
            assert not reply.get("directive_stale"), (line, members, reply.get("message"))
            given += 1
            rows = {r["marshal"]: r for r in reply["group"]["rows"]}
            assert len(rows) == addressed, (line, rows)                # a row a member
            cost = int(reply["action_info"]["cost"])
            assert cost <= pool and cost <= expect, (line, members, cost, expect)
            if staff is None:
                assert cost == sum(int(r["ap"]) for r in rows.values()), (line, rows)
            question = _carries_a_question(reply)
            battle = any(reply.get(key) for key in BATTLE_KEYS)
            for name in members:
                row = rows[name]
                if row["sent"] and staff is None:
                    assert row["ap"] == by[name]["ap"], (line, name, by[name], row)
                if not (question or battle):
                    assert row["sent"], (line, name, row)              # quoted to go, and went
            if not (question or battle):
                for name, was in untouched.items():
                    assert _marshal_json(world, name) == was, (line, name)
                changed = {key for key in TB._changed_keys(before, world.to_dict()) if not TB._inert(key)}
                assert changed <= TB.ORDER_KEYS, (line, sorted(changed - TB.ORDER_KEYS))
        assert given >= 12, given     # the run really gave orders
