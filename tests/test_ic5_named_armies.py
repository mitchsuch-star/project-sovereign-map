"""Row IC "Independent Command", the second commit (November 19, 2026) — IC-5: NAMED ARMIES.

The user's ruling in Plan Mode: "Yes, named armies" — form an army, name it, give it an order by name
("Army of Italy, hold"). An army is a saved group of the player's own marshals and nothing more: no bonus,
no cost, no rule of the game reads it (`backend/game_logic/armies.py`; `docs/SYSTEMS_REFERENCE.md` §230).

Pinned here, on the shipped 1805 board through the real `POST /command`:

* the four verbs of the free action `army` — form · add · remove · disband — and the list;
* a marshal is in ONE army at most; an army left with nobody dissolves and says so;
* a name that cannot be an army's is refused in plain words (the bare collective words, a man's name, a
  province, a court, no "army" in it);
* a member who is no longer ours to order drops out (he falls, is dismissed, is taken prisoner);
* "Army of Italy, hold" addresses it — in `/command` and in the read-back alike — although the bare word
  "army" already means every corps;
* the store is saved only when it holds something, an old save loads none, and forming an army can be
  taken back;
* the twelve steps: every list an action must stand in holds `army` (and `set_war_goal`).
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib

import pytest

from backend.commands import directive as DV
from backend.commands import take_back as TB
from backend.game_logic import armies

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


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
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
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


def _preview(client, line: str) -> dict:
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


def _rolls(world) -> dict:
    return {name: list(row["members"]) for name, row in world.armies.items()}


# ═══ the four verbs ══════════════════════════════════════════════════════════

class TestTheFourVerbs:
    def test_form_names_an_army_and_says_how_to_use_it(self, client, world):
        reply = _say(client, "form the Army of Italy with Massena and Ney")
        assert reply["success"], reply["message"]
        assert reply["message"] == (
            "The Army of Italy is formed: Massena and Ney. Press its chip beside your marshals to "
            "select its men, or say “Army of Italy, hold”.")
        assert _rolls(world) == {"Army of Italy": ["Massena", "Ney"]}
        assert world.armies["Army of Italy"]["formed_turn"] == world.current_turn
        assert reply["armies"] == [{"name": "Army of Italy", "members": ["Massena", "Ney"],
                                    "members_shown": ["Massena", "Ney"], "in_field": 2}]

    def test_it_is_free_and_nobody_objects(self, client, world):
        actions, admin, gold = world.actions_remaining, world.admin_actions_remaining, world.gold
        reply = _say(client, "form the Army of Italy with Massena and Ney")
        assert (world.actions_remaining, world.admin_actions_remaining, world.gold) == (actions, admin, gold)
        assert reply["action_info"]["cost"] == 0
        assert not reply.get("pending_objection") and reply.get("state") != "awaiting_player_choice"
        assert world.get_action_cost("army") == 0

    def test_add_remove_and_disband(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        added = _say(client, "add Lannes to the Army of Italy")
        assert added["message"] == "Lannes joins the Army of Italy (now Massena, Ney and Lannes)."
        gone = _say(client, "remove Massena from the Army of Italy")
        assert gone["message"] == "Massena leaves the Army of Italy (now Ney and Lannes)."
        assert _rolls(world) == {"Army of Italy": ["Ney", "Lannes"]}
        done = _say(client, "disband the Army of Italy")
        assert done["success"] and done["message"].startswith("The Army of Italy is disbanded.")
        assert world.armies == {} and "armies" not in done      # absent = none

    @pytest.mark.parametrize("line", ["Army of Italy, disband", "the Army of Italy: disband",
                                      "Army of Italy, break up"])
    def test_the_army_named_first_then_disband_is_a_disband(self, client, world, line):
        """The review: the army's name opened the line, so it was read as an order to its first man
        ("Massena, disband" — an order nobody knows) and the army was never disbanded."""
        _say(client, "form the Army of Italy with Massena and Ney")
        assert DV.address(world, line) is None                  # never an order to several
        reply = _say(client, line)
        assert reply["success"], reply["message"]
        assert world.armies == {}
        assert DV.address(world, line) is None                  # nor once it is gone ("army" alone is
                                                                 # the collective word)

    def test_a_removal_that_takes_nobody_out_says_why(self, client, world):
        """The review: "Nobody you named is not in the Army of Italy" said the opposite of what
        happened, and a name that is no marshal of ours was dropped in silence."""
        _say(client, "form the Army of Italy with Massena and Ney")
        reply = _say(client, "remove Davout from the Army of Italy")
        assert reply["success"] is False
        assert reply["message"] == "Davout is not in the Army of Italy, which holds Massena and Ney."
        from backend.game_logic import armies
        said = armies.remove(world, "Army of Italy", ["Xyzzy"])
        assert said["success"] is False and said["message"] == (
            "“Xyzzy” is not one of your marshals — nobody was taken out of the Army of Italy, which holds "
            "Massena and Ney.")
        assert world.armies["Army of Italy"]["members"] == ["Massena", "Ney"]

    def test_the_forms_that_open_with_the_mans_name(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        assert _say(client, "Lannes joins the Army of Italy")["success"]
        assert _say(client, "Massena leaves the Army of Italy")["success"]
        assert _rolls(world) == {"Army of Italy": ["Ney", "Lannes"]}

    def test_forming_under_a_name_that_exists_gives_it_those_men(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        again = _say(client, "form the Army of Italy with Davout and Soult")
        assert again["message"] == "The Army of Italy now holds Davout and Soult."
        assert _rolls(world) == {"Army of Italy": ["Davout", "Soult"]}

    def test_the_list(self, client, world):
        assert "You have formed no army yet." in _say(client, "armies")["message"]
        _say(client, "form the Army of Italy with Massena and Ney")
        assert _say(client, "armies")["message"] == "Your armies — Army of Italy: Massena and Ney."

    def test_each_verb_writes_one_line_to_the_campaign_log(self, client, world):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        assert {"army_roster", "war_goal"} <= set(CAMPAIGN_LOG_TYPES)
        before = len(world.event_log)
        reply = _say(client, "form the Army of Italy with Massena and Ney")
        events = [e for e in world.event_log[before:] if e.get("type") == "army_roster"]
        assert len(events) == 1 and events[0]["op"] == "form" and events[0]["army"] == "Army of Italy"
        assert format_event_oneliner(events[0], world.player_nation) == reply["message"]
        _say(client, "armies")                                   # asking writes none
        assert len([e for e in world.event_log[before:] if e.get("type") == "army_roster"]) == 1


# ═══ the rules ═══════════════════════════════════════════════════════════════

class TestTheRules:
    def test_a_marshal_is_in_one_army_at_most(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        reply = _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        assert "Ney leaves the Army of Italy." in reply["message"]
        assert _rolls(world) == {"Army of Italy": ["Massena"], "Army of the Rhine": ["Davout", "Soult", "Ney"]}
        assert armies.army_of(world, "Ney") == "Army of the Rhine"

    def test_an_army_left_with_nobody_dissolves_and_says_so(self, client, world):
        _say(client, "form the Army of Italy with Massena")
        reply = _say(client, "form the Army of the Rhine with Massena and Ney")
        assert "The Army of Italy has no corps left and is dissolved." in reply["message"]
        assert list(world.armies) == ["Army of the Rhine"]
        last = _say(client, "remove Massena and Ney from the Army of the Rhine")
        assert "it has no corps left and is dissolved" in last["message"] and world.armies == {}

    @pytest.mark.parametrize("line, why", [
        ("form the army with Davout and Lannes", "already means every corps you have"),
        ("form the Grande Armée with Davout and Lannes", "already means every corps you have"),
        ("form Ney's Army with Davout and Lannes", "An army is not named after a man"),
        ("form the Army of Davout with Soult and Lannes", "An army is not named after a man"),
    ])
    def test_a_name_that_cannot_be_an_armys_is_refused_in_plain_words(self, client, world, line, why):
        reply = _say(client, line)
        assert reply["success"] is False and why in reply["message"], reply["message"]
        assert world.armies == {}
        # … and the read-back says the same before Enter
        assert _preview(client, line)["kind"] == "refusal"

    def test_the_name_rule_itself(self, world):
        assert armies.name_refusal(world, "Army of Italy") == ""
        assert armies.name_refusal(world, "Army of the Rhine") == ""
        assert armies.name_refusal(world, "Armée du Nord") == ""
        assert "must hold the word “army”" in armies.name_refusal(world, "The Old Guard")
        assert "too long" in armies.name_refusal(world, "Army of " + "x" * 60)
        assert armies.name_refusal(world, "Army of ##") != ""
        assert armies.tidy('  the  "Army  of Italy" ') == "Army of Italy"

    def test_only_the_players_own_men_can_be_put_in_one(self, client, world):
        reply = _say(client, "form the Army of Italy with Ney and Mack")
        assert reply["success"] is False and "Mack is not yours to put in an army" in reply["message"]
        assert world.armies == {}

    def test_an_unknown_army_is_named_with_the_ones_that_exist(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        reply = _say(client, "disband the Army of Spain")
        assert reply["success"] is False
        assert reply["message"] == "There is no army called “Army of Spain”. Your armies: Army of Italy."

    def test_lines_that_only_look_like_it_are_left_alone(self, world):
        for line in ("Ney, form square", "form square", "raise an army with fresh conscripts",
                     "Lannes joins the army at Ulm", "who is in the Army of Italy?", "disband"):
            assert armies.read_order(world, line) is None, line

    def test_the_seam_down_nothing_is_an_army(self, client, world, monkeypatch):
        world.armies = {"Army of Italy": {"members": ["Massena", "Ney"], "formed_turn": 1}}
        monkeypatch.setattr(armies, "armies_can_be_named", lambda: False)
        assert armies.read_order(world, "form the Army of Spain with Ney and Soult") is None
        assert armies.address_of(world, "Army of Italy, hold") is None
        assert armies.payload(world) == []


# ═══ who drops out ═══════════════════════════════════════════════════════════

class TestWhoDropsOut:
    def _army(self, world, *names):
        world.armies = {"Army of Italy": {"members": list(names), "formed_turn": 1}}

    def test_a_prisoner_leaves_his_army(self, world):
        self._army(world, "Massena", "Ney")
        world.capture_marshal(world.get_marshal("Ney"), "Austria")
        assert _rolls(world) == {"Army of Italy": ["Massena"]}
        line = next(e for e in world.event_log if e.get("type") == "army_roster")["line"]
        assert line == "Ney is no longer with the Army of Italy (now Massena)."

    def test_a_dismissed_man_leaves_and_an_empty_army_is_dissolved(self, world):
        self._army(world, "Ney")
        assert world.stand_down_marshal(world.get_marshal("Ney")) is True
        assert world.armies == {}
        said = [e["line"] for e in world.event_log if e.get("type") == "army_roster"]
        assert said == ["The Army of Italy has no corps left and is dissolved."]

    def test_a_man_who_falls_leaves_his_army(self, world):
        self._army(world, "Massena", "Ney")
        world.destroy_marshal(world.get_marshal("Massena"), "battle")
        assert _rolls(world) == {"Army of Italy": ["Ney"]}

    def test_the_readers_never_wait_for_the_prune(self, world):
        """A member who is no longer ours is filtered where he is read, whatever the store still holds."""
        self._army(world, "Massena", "Ney", "Nobody")
        world.get_marshal("Ney").captured_by = "Austria"
        assert armies.members(world, "Army of Italy") == ["Massena"]
        assert armies.payload(world)[0]["members"] == ["Massena"]

    def test_a_board_with_no_army_is_never_touched(self, world):
        before = world.to_dict()
        assert armies.roll_call(world) == [] and armies.prune(world) == []
        assert world.to_dict() == before


# ═══ "Army of Italy, hold" ═══════════════════════════════════════════════════

class TestTheArmyIsAddressedByName:
    def test_the_address_is_read_before_the_word_army_means_everyone(self, client, world):
        from backend.commands import group_orders as G
        assert G.collective_head("Army of the Rhine, hold")["who"].lower() == "army"   # today's reading
        assert DV.address(world, "Army of the Rhine, hold")["kind"] == "everyone"      # … with no such army
        _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        found = DV.address(world, "Army of the Rhine, hold")
        assert (found["kind"], found["army"], found["names"], found["rest"]) == (
            "army", "Army of the Rhine", ["Davout", "Soult", "Ney"], "hold")
        assert DV.address(world, "the army of the rhine marches on Lorraine")["army"] == "Army of the Rhine"
        assert DV.address(world, "everyone, hold")["kind"] == "everyone"               # the army as a whole

    def test_it_opens_the_list_of_its_men(self, client, world):
        _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        listing = _say(client, "Army of the Rhine, hold", list_first=True)["directive"]
        assert listing["kind"] == "army" and listing["who"] == "The Army of the Rhine"
        assert listing["army"] == "Army of the Rhine" and listing["line"] == "Army of the Rhine, hold"
        assert [r["marshal"] for r in listing["rows"]] == ["Davout", "Soult", "Ney"]
        members = [r["marshal"] for r in listing["rows"] if r["ticked"]]
        reply = _say(client, listing["line"], members=members, expect_ap=listing["total"])
        assert reply["success"], reply["message"]
        assert "The order goes to the Army of the Rhine, corps by corps" in reply["message"]
        for name in members:
            assert world.get_marshal(name).strategic_order is not None, name

    def test_its_chip_sent_by_a_click_lists_each_mans_click_order(self, client, world):
        """The client names an army it selected whole (its chip, then a province, or the card's Hold):
        "Army of the Rhine, march to Lorraine" with `click` — the list titled by the army, each man's own
        click order (a move next door at one action), the head saying "go to"."""
        _say(client, "form the Army of the Rhine with Davout and Ney")
        with _quiet():
            got = client.get("/directive_quote", params={"line": "Army of the Rhine, march to Lorraine",
                                                         "click": "1"}).json()
        listing = got["directive"]
        assert listing["who"] == "The Army of the Rhine" and listing["order"] == "go to Lorraine"
        assert [(r["marshal"], r["ap"]) for r in listing["rows"]] == [("Davout", 1), ("Ney", 1)]
        assert all("move to Lorraine" in r["says"] for r in listing["rows"])
        reply = _say(client, listing["line"], members=["Davout", "Ney"], expect_ap=2, click=True)
        assert reply["success"] and reply["action_info"]["cost"] == 2, reply["message"]
        assert "The order goes to the Army of the Rhine, corps by corps — 2 corps, 2 actions" in reply["message"]
        assert "'go to Lorraine'" in reply["message"]
        assert {world.get_marshal(n).location for n in ("Davout", "Ney")} == {"Lorraine"}

    def test_the_read_back_reads_it_the_same(self, client, world):
        _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        got = _preview(client, "Army of the Rhine, hold")
        assert got["directive"] is True
        assert got["parts"][0]["text"] == "The Army of the Rhine · hold · 3 corps"

    def test_an_attack_is_one_mans_order_and_says_so(self, client, world):
        _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        got = _preview(client, "Army of the Rhine, attack Mack")
        assert got["directive"] is False and got["marshal"] == "Davout"
        assert got["parts"][-1]["text"] == "one man’s order, not one for each corps of the Army of the Rhine"
        reply = _say(client, "Army of the Rhine, attack Mack", list_first=True)
        assert not reply.get("directive")
        assert "(The Army of the Rhine: this is one man's order, not one for each corps — Davout took it.)" \
            in reply["message"]

    def test_a_refused_army_order_never_says_a_man_took_it(self, client, world):
        """The review: "(… — Davout took it.)" was added to a refusal too — an order nobody took."""
        _say(client, "form the Army of the Rhine with Davout, Soult and Ney")
        world.actions_remaining = 0
        reply = _say(client, "Army of the Rhine, attack Mack")
        assert reply["success"] is False, reply["message"]
        assert "took it" not in reply["message"]
        assert "(The Army of the Rhine: this is one man's order, not one for each corps — it was for Davout alone.)" \
            in reply["message"]

    def test_an_army_with_nobody_in_the_field_is_said(self, client, world):
        _say(client, "form the Army of Italy with Massena")
        world.get_marshal("Massena").administrative = True
        reply = _say(client, "Army of Italy, hold")
        assert reply["success"] is False
        assert reply["message"] == ("The Army of Italy has no corps in the field to take an order, "
                                    "Sire — nothing spent.")


# ═══ saved, loaded, taken back ═══════════════════════════════════════════════

class TestSavedLoadedAndTakenBack:
    def test_the_store_is_saved_only_when_it_holds_something(self, client, world):
        from backend.models.world_state import WorldState
        assert "armies" not in world.to_dict()                      # an ordinary save is what it was
        _say(client, "form the Army of Italy with Massena and Ney")
        saved = world.to_dict()
        assert saved["armies"] == {"Army of Italy": {"members": ["Massena", "Ney"],
                                                     "formed_turn": world.current_turn}}
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(saved, default=str)))
        assert again.armies == saved["armies"] and again.to_dict()["armies"] == saved["armies"]

    def test_an_old_save_loads_none(self, _snapshot):
        from backend.models.world_state import WorldState
        old = json.loads(_snapshot)
        assert "armies" not in old and "war_goals" not in old
        with _quiet():
            assert WorldState.from_dict(old).armies == {}

    def test_forming_an_army_can_be_taken_back(self, client, world):
        assert {"armies", "war_goals"} <= TB.ORDER_KEYS
        reply = _say(client, "form the Army of Italy with Massena and Ney")
        assert reply["undo"]["available"] is True
        with _quiet():
            back = client.post("/undo").json()
        assert back["taken_back"] is True and world.armies == {} and "armies" not in back

    def test_a_take_back_puts_a_disbanded_army_back(self, client, world):
        _say(client, "form the Army of Italy with Massena and Ney")
        _say(client, "disband the Army of Italy")
        with _quiet():
            client.post("/undo")
        assert _rolls(world) == {"Army of Italy": ["Massena", "Ney"]}


# ═══ the twelve steps ════════════════════════════════════════════════════════

class TestTheTwelveSteps:
    """CLAUDE.md "Adding a new action", for the two free actions of this commit."""

    ACTIONS = ("army", "set_war_goal")

    def test_every_list_an_action_must_stand_in_holds_them(self, world):
        from backend.ai import validation as V
        from backend.commands.parser import CommandParser
        from backend.display_names import ACTION_DISPLAY, DEFIANCE_DISPLAY, OBJECTION_DISPLAY
        with _quiet():
            parser = CommandParser(use_real_llm=False)
        for action in self.ACTIONS:
            assert action in V.VALID_ACTIONS and action in V.META_ACTIONS, action     # step 1
            assert action in parser.valid_actions, action                             # step 3
            assert world._action_costs[action] == 0, action                           # step 4
            for table in (ACTION_DISPLAY, OBJECTION_DISPLAY, DEFIANCE_DISPLAY):       # steps 9, 10
                assert table.get(action), action
            assert action in V.NEVER_STRATEGIC_ACTIONS, action     # never upgraded to a standing order

    def test_the_other_steps(self):
        """Steps 2, 6, 11 and 12 (the review: the class's name promised all twelve and read five; step 5
        is the router-words test's, step 7 the next test's, step 8 `TestSavedLoadedAndTakenBack`)."""
        from backend.ai.prompt_builder import FEW_SHOT_TEMPLATES
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        source = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
        corpus = json.loads((REPO / "tests" / "data" / "parser_golden_corpus.json").read_text(encoding="utf-8"))
        taught = {str(t["output"].get("action")) for t in FEW_SHOT_TEMPLATES if isinstance(t.get("output"), dict)}
        covered = {str((e.get("expected") or {}).get("action")) for e in corpus["entries"]}
        for action in self.ACTIONS:
            assert f'elif action == "{action}":' in source, action          # step 2: the dispatch
            assert action in taught, action                                 # step 6: the model's example
            assert action in covered, action                                # step 12: the golden corpus
        assert {"army_roster", "war_goal"} <= set(CAMPAIGN_LOG_TYPES)       # step 11: the log's types

    def test_neither_is_an_order_a_marshal_can_object_to(self):
        """Step 7, recorded: a list and an aim are the player's own bookkeeping — a PURCHASE's judgement
        (`purchase_levy`): absent from `objection_actions` on purpose."""
        source = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
        listed = source[source.index("objection_actions = ["):].split("]", 1)[0]
        for action in self.ACTIONS:
            assert f'"{action}"' not in listed

    def test_the_built_in_reader_reaches_them_and_the_router_words_are_current(self, world):
        from backend.commands.parser import CommandParser
        from tools import gen_routed_order_words as GEN
        with _quiet():
            parser = CommandParser(use_real_llm=False)
            army = parser.parse("form the Army of Italy with Massena and Ney", {"world": world}, world=world)
            goal = parser.parse("the war goal is Vienna", {"world": world}, world=world)
        assert army["success"] and army["command"]["action"] == "army" and not army["command"].get("marshal")
        assert goal["success"] and goal["command"]["action"] == "set_war_goal"
        assert GEN.TARGET_PATH.read_text(encoding="utf-8") == GEN.render(GEN.harvest())

    def test_a_court_keeps_no_named_army(self, world):
        from backend.commands.directive_executor import DirectiveExecutor
        executor = DirectiveExecutor(None)
        refused = executor._execute_army({"_acting_nation": "Austria",
                                          "raw_command": "form the Army of Italy with Mack"},
                                         {"world": world})
        assert refused["success"] is False and world.armies == {}
