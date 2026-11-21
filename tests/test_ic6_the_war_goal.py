"""Row IC "Independent Command", the second commit (November 19, 2026) — IC-6: THE WAR GOAL.

The design's §9 (`docs/INDEPENDENT_COMMAND_SPEC.md`): one thing a war aims at — a place or an enemy army —
named by the player, free. It is said on the desk's WAR line, ringed on the map, and (only once one is set)
TO DECIDE offers the march that closes on it as one list (`backend/game_logic/war_goals.py`;
`docs/SYSTEMS_REFERENCE.md` §230). It moves no rule of the game.

It is NOT the war's PURPOSE (`world.war_objectives`, a Cabinet act). The typed words "set war goal" used to
be a second spelling of the purpose; they mean this now, and the purpose keeps its four.

Pinned here, on the shipped 1805 board through the real `POST /command`:

* set — a place a court at war with us holds, or an enemy army by its commander — and clear; ONE goal a war;
* what cannot be a goal is refused in plain words, by one predicate the read-back asks too;
* the desk: THE WAR line names it, `desk.goals` carries it for the map, and a row offers the march as a list;
* the fog: an army's place is given only where the player can see him;
* reached, and dropped when its war ends;
* UNSET: the desk is, to the byte, what it was;
* saved only when held; an old save loads none; a goal can be taken back.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib

import pytest

from backend.commands import take_back as TB
from backend.game_logic import today, war_goals

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


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


# ═══ naming it ═══════════════════════════════════════════════════════════════

class TestNamingTheGoal:
    @pytest.mark.parametrize("line", [
        "the war goal is Vienna", "set the war goal to Vienna", "make Vienna the war goal",
        "war goal: Vienna", "set war goal Vienna", "the goal of the war is Vienna",
        "the war goal is the city of Vienna",
    ])
    def test_a_place_an_enemy_holds(self, client, world, line):
        reply = _say(client, line)
        assert reply["success"], reply["message"]
        assert world.war_goals == {"Austria": {"kind": "place", "target": "Vienna",
                                               "turn": world.current_turn}}
        # the war as the war panel names it (the directives' blind reading 3: "the war with Austria"
        # beside a panel that said "War with the Third Coalition")
        assert reply["message"] == ("The goal of the war with the Third Coalition is now Vienna. "
                                    "The desk names it and the map rings it.")

    @pytest.mark.parametrize("line", ["make Mack the war goal", "the war goal is Mack's army",
                                      "the war goal is the army of Mack"])
    def test_an_enemy_army_by_its_commander(self, client, world, line):
        reply = _say(client, line)
        assert reply["success"], reply["message"]
        assert world.war_goals["Austria"]["kind"] == "army" and world.war_goals["Austria"]["target"] == "Mack"
        assert "is now Mack's army." in reply["message"]

    def test_it_is_free_and_nobody_objects(self, client, world):
        actions, admin, gold = world.actions_remaining, world.admin_actions_remaining, world.gold
        reply = _say(client, "the war goal is Vienna")
        assert (world.actions_remaining, world.admin_actions_remaining, world.gold) == (actions, admin, gold)
        assert reply["action_info"]["cost"] == 0 and not reply.get("pending_objection")

    def test_one_goal_a_war(self, client, world):
        """Austria, Britain and Russia fight ONE war (the Third Coalition): a goal against any of them
        replaces the one that war had."""
        _say(client, "the war goal is Vienna")
        reply = _say(client, "make Mack the war goal")
        assert "(It was Vienna.)" in reply["message"]
        assert list(world.war_goals) == ["Austria"]
        russian = next(name for name, region in world.regions.items() if region.controller == "Russia")
        again = _say(client, f"the war goal is {russian}")
        assert again["success"] and list(world.war_goals) == ["Russia"]
        assert "(It was Mack's army.)" in again["message"]

    def test_clearing_it(self, client, world):
        assert _say(client, "clear the war goal")["message"] == "No war goal is set, Sire."
        _say(client, "the war goal is Vienna")
        reply = _say(client, "clear the war goal")
        assert reply["success"] and world.war_goals == {}
        # (the review: named as the war panel names the war, as setting it is)
        assert reply["message"] == "The war with the Third Coalition has no goal now (it was Vienna)."
        _say(client, "the war goal is Vienna")
        assert _say(client, "clear the war goal against Britain")["success"]     # a court of the same war
        assert world.war_goals == {}

    @pytest.mark.parametrize("line, why", [
        ("the war goal is Paris", "Paris is yours already"),
        ("the war goal is Berlin", "Berlin is held by Prussia, and you are not at war with it"),
        ("set war goal Munich", "Munich is held by Bavaria, and you are not at war with it"),
        ("the war goal is Atlantis", "I know no province or enemy commander called “Atlantis”"),
        ("make Ney the war goal", "I know no province or enemy commander called “Ney”"),
    ])
    def test_what_cannot_be_a_goal_is_refused_in_plain_words(self, client, world, line, why):
        reply = _say(client, line)
        assert reply["success"] is False and why in reply["message"], reply["message"]
        assert world.war_goals == {}
        # ONE predicate (`war_goals.aim`): the read-back refuses it before Enter
        assert _preview(client, line)["kind"] == "refusal"

    def test_a_slip_is_offered_back(self, client, world):
        reply = _say(client, "the war goal is Vienne")
        assert reply["success"] is False and "Did you mean Vienna?" in reply["message"]

    def test_the_read_back_names_it_before_enter(self, client, world):
        got = _preview(client, "the war goal is Vienna")
        assert got["kind"] == "order" and got["action"] == "set_war_goal" and got["free"] is True
        assert [p["text"] for p in got["parts"]] == ["The war goal · Vienna", "free"]
        assert _preview(client, "make Mack the war goal")["parts"][0]["text"] == "The war goal · Mack’s army"

    def test_a_question_is_never_an_order(self, world):
        assert war_goals.read_order("what is the war goal?") is None
        assert war_goals.read_order("Ney, attack Mack") is None
        assert war_goals.read_order("set war purpose conquest against Austria") is None

    def test_it_writes_one_line_to_the_campaign_log(self, client, world):
        from backend.campaign_log import format_event_oneliner
        before = len(world.event_log)
        reply = _say(client, "the war goal is Vienna")
        events = [e for e in world.event_log[before:] if e.get("type") == "war_goal"]
        assert len(events) == 1 and (events[0]["against"], events[0]["target"]) == ("Austria", "Vienna")
        assert format_event_oneliner(events[0], world.player_nation) == reply["message"]


# ═══ the name clash ══════════════════════════════════════════════════════════

class TestTheGoalIsNotThePurpose:
    """ "objective" already means the war's PURPOSE (`world.war_objectives`); the goal is the army's aim."""

    def test_set_war_goal_no_longer_opens_the_purpose(self, client, world):
        purposes = json.dumps(world.to_dict().get("war_objectives"), sort_keys=True, default=str)
        reply = _say(client, "set war goal Vienna")
        assert reply["success"] and world.war_goals["Austria"]["target"] == "Vienna"
        assert not reply.get("diplomatic_dialogue") and not reply.get("war_purpose_popup")
        assert json.dumps(world.to_dict().get("war_objectives"), sort_keys=True, default=str) == purposes

    def test_the_purpose_keeps_its_own_words(self, world):
        from backend.commands.parser import CommandParser
        with _quiet():
            parser = CommandParser(use_real_llm=False)
            for line in ("set war purpose conquest against Austria", "war purpose conquest Austria",
                         "set objective conquest against Austria", "declare purpose conquest against Austria"):
                parsed = parser.parse(line, {"world": world}, world=world)
                assert (parsed.get("command") or {}).get("action") == "set_war_purpose", line

    def test_the_client_s_cabinet_door_lets_every_goal_and_army_line_through(self):
        """The client claims a typed line that carries a diplomatic keyword for the Cabinet (it is sent
        nowhere). "set war goal" left that list; no form of the two new actions carries another."""
        import re
        source = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        block = source[source.index("const DIPLO_FAMILY_KEYWORDS = ["):]
        block = block[:block.index("\n]")]
        keywords = re.findall(r'^\t"([^"]+)",', block, re.M)
        assert len(keywords) > 60 and "set war goal" not in keywords and "war purpose" in keywords
        war_room = re.findall(r'^\t"([^"]+)",',
                              source[source.index("const DIPLO_WAR_ROOM_KEYWORDS = ["):].split("\n]")[0], re.M)
        lines = ["the war goal is Vienna", "set the war goal to Vienna", "make Vienna the war goal",
                 "war goal: Vienna", "set war goal Vienna", "make Mack the war goal",
                 "clear the war goal", "clear the war goal against Austria",
                 "form the Army of Italy with Massena and Ney", "add Lannes to the Army of Italy",
                 "remove Ney from the Army of Italy", "disband the Army of Italy", "armies",
                 "Army of Italy, hold", "Army of the Rhine, march to Lorraine"]
        for line in lines:
            low = line.lower()
            assert not any(word in low for word in keywords + war_room), line

    def test_the_backends_purpose_keywords_dropped_it_too(self):
        source = (REPO / "backend" / "ai" / "llm_client.py").read_text(encoding="utf-8")
        block = source[source.index("_war_purpose_keywords = ["):].split("]", 1)[0]
        assert '"set war goal"' not in block and '"set war purpose"' in block


# ═══ the desk ════════════════════════════════════════════════════════════════

class TestTheDesk:
    def test_unset_the_desk_is_what_it_was(self, client, world):
        """The approved plan: "Unset: no code path changes" — no goal, no new key, no new row."""
        desk = _say(client, "status")["desk"]
        assert sorted(desk) == ["danger", "decide", "first_open", "more", "peace", "shown", "war"]
        assert desk["war"]["text"] == ("War with the Third Coalition (Britain + Austria + Russia): "
                                       "to hold the homeland.")
        assert all("goal" not in part for part in desk["war"]["parts"])
        # (row IC, Session 3: the design's first morning also says Masséna, far
        # from the Emperor, could be set on his own — the last, a tier-3 row)
        assert [row["id"] for row in desk["decide"]] == ["reach:Mack", "reach:ArchdukeJohn",
                                                         "own_free:Massena"]
        assert all(row["door"]["kind"] != "directive" for row in desk["decide"])

    def test_the_war_line_names_it_and_the_map_gets_its_ring(self, client, world):
        desk = _say(client, "the war goal is Vienna")["desk"]
        assert desk["war"]["text"] == ("War with the Third Coalition (Britain + Austria + Russia): "
                                       "to hold the homeland — your war goal: Vienna.")
        assert desk["war"]["parts"][0]["goal"] == "your war goal: Vienna"
        assert desk["goals"] == [{"war": "Britain", "court": "Austria", "kind": "place",
                                  "target": "Vienna", "shown": "Vienna", "status": "open",
                                  "region": "Vienna", "line": "your war goal: Vienna"}]

    def test_a_row_offers_the_march_as_one_list(self, client, world):
        desk = _say(client, "the war goal is Vienna")["desk"]
        row = desk["decide"][0]                                   # the player's own aim leads the idle rows
        assert row["id"] == "goal:Austria" and row["tier"] == today.TIER_WASTES
        # (directives' blind reading 1: no count where every corps with no orders can go — "8 corps
        # with no orders" stood over "7 corps of yours have no orders and Mack…", the same corps)
        assert row["text"] == "Your corps with no orders can march on Vienna, your war goal — press to list them."
        assert len(row["text"]) <= today.ROW_CAP
        door = row["door"]
        assert door["kind"] == "directive" and door["click"] is True
        assert door["line"] == ("Ney, Davout, Soult, Lannes, Murat, Bernadotte, Massena and Napoleon, "
                                "march to Vienna")
        assert row["more"].startswith("No orders: Ney, Davout")
        # the door's line IS a list the game draws — each man's own order, priced
        with _quiet():
            got = client.get("/directive_quote", params={"line": door["line"], "click": "1"}).json()
        assert got["success"] and len(got["directive"]["rows"]) == 8
        assert got["directive"]["who"].startswith("Ney, Davout")

    def test_the_rows_about_an_enemy_beside_them_still_stand(self, client, world):
        desk = _say(client, "the war goal is Vienna")["desk"]
        assert [row["id"] for row in desk["decide"]] == ["goal:Austria", "reach:Mack", "reach:ArchdukeJohn",
                                                         "own_free:Massena"]

    def test_one_corps_alone_is_his_own_row(self, client, world):
        _say(client, "the war goal is Vienna")
        idle = [m for m in world.get_field_marshals() if m.name != "Massena"]
        for m in idle:
            m.fortified = True                                    # only Massena has nothing to do
        row = _say(client, "status")["desk"]["decide"][0]
        assert row["text"] == "Massena has no orders and can march on Vienna, your war goal."
        assert row["door"] == {"kind": "marshal", "marshal": "Massena"}

    def test_with_no_action_left_it_is_no_matter(self, client, world):
        """Lever L4's own rule: a corps with no orders is no row when no action is left."""
        _say(client, "the war goal is Vienna")
        world.actions_remaining = 0
        assert all(not row["id"].startswith("goal:") for row in _say(client, "status")["desk"]["decide"])

    def test_what_now_says_it(self, client, world):
        _say(client, "the war goal is Vienna")
        assert "Your corps with no orders can march on Vienna, your war goal — press to list them." \
            in _say(client, "what now?")["message"]

    def test_some_of_the_corps_with_no_orders_are_counted(self, client, world, monkeypatch):
        """Where only some of the corps with no orders can be sent, the row counts them."""
        from backend.game_logic import war_goals
        _say(client, "the war goal is Vienna")
        real = war_goals.marchers

        def all_but_massena(w, goal, free):
            names, order = real(w, goal, free)
            return [n for n in names if n != "Massena"], order
        monkeypatch.setattr(war_goals, "marchers", all_but_massena)
        row = _say(client, "status")["desk"]["decide"][0]
        assert row["text"] == "7 of your corps with no orders can march on Vienna, your war goal — press to list them."

    def test_an_army_goal_closes_on_him_where_the_staff_knows_where_he_stands(self, client, world):
        desk = _say(client, "make Mack the war goal")["desk"]
        assert desk["war"]["text"].endswith("— your war goal: Mack's army.")
        row = desk["decide"][0]
        assert row["text"] == "Your corps with no orders can close on Mack's army, your war goal — press to list them."
        assert row["door"]["line"].endswith(", pursue Mack")
        with _quiet():
            got = client.get("/directive_quote", params={"line": row["door"]["line"], "click": "1"}).json()
        assert got["success"], got.get("message")                 # a pursuit by the desk's list fans out

    def test_reading_the_desk_changes_nothing(self, client, world):
        _say(client, "the war goal is Vienna")
        before = world.to_dict()
        for _ in range(3):
            today.desk(world)
        assert world.to_dict() == before


# ═══ the fog ═════════════════════════════════════════════════════════════════

class TestTheFog:
    def _hidden(self, world):
        from backend.game_logic.intel_surfaces import in_sight
        player = world.player_nation
        return next(m for m in world.marshals.values()
                    if m.nation != player and int(m.strength or 0) > 0
                    and world.is_at_war(player, m.nation) and not in_sight(world, player, m))

    def test_a_man_out_of_sight_can_be_named_and_his_place_is_never_given(self, client, world):
        hidden = self._hidden(world)
        reply = _say(client, f"make {hidden.name} the war goal")
        assert reply["success"], reply["message"]                 # his name and side are public
        text = json.dumps({"message": reply["message"], "desk": reply["desk"]}, default=str)
        assert str(hidden.location) not in text
        goal = reply["desk"]["goals"][0]
        assert goal["kind"] == "army" and goal["region"] == ""    # no ring where the fog keeps him
        assert all(not row["id"].startswith("goal:") for row in reply["desk"]["decide"])
        # (the review) no ring is promised where none is drawn — the reply and the war's window
        assert "The desk names it; the map will ring his army once he is in sight." in reply["message"]
        assert "the map rings it" not in reply["message"]
        from backend.game_logic.war_status import build_active_wars
        row = next(w for w in build_active_wars(world)["wars"] if w.get("war_goal"))
        assert row["war_goal_ringed"] is False

    def test_the_desk_plots_the_roads_once_for_a_board_that_has_not_moved(self, client, world, monkeypatch):
        """Rule 8 (the review): the desk asks who can march on the goal on EVERY reply, and a place goal
        plots a road for each idle corps — kept for the state it was read on."""
        from backend.commands import order_quotes as Q
        _say(client, "the war goal is Vienna")
        calls = []
        real = Q._road
        monkeypatch.setattr(Q, "_road", lambda *a, **k: calls.append(1) or real(*a, **k))
        war_goals._MARCHERS_CACHE.clear()
        today.desk(world)
        first = len(calls)
        today.desk(world)
        assert first > 0 and len(calls) == first                 # the second read plotted no road
        world.actions_remaining -= 1                              # an order spent: the board moved
        today.desk(world)
        assert len(calls) > first

    def test_a_ringed_goal_says_so_in_the_wars_window(self, client, world):
        from backend.game_logic.war_status import build_active_wars
        _say(client, "the war goal is Vienna")
        row = next(w for w in build_active_wars(world)["wars"] if w.get("war_goal"))
        assert row["war_goal"] == "your war goal: Vienna" and row["war_goal_ringed"] is True
        world.get_region("Vienna").controller = world.player_nation
        world.invalidate_active_nations_cache()
        row = next(w for w in build_active_wars(world)["wars"] if w.get("war_goal"))
        assert row["war_goal"] == "your war goal: Vienna (taken)" and row["war_goal_ringed"] is False

    def test_a_man_in_sight_is_ringed_where_he_stands(self, client, world):
        goal = _say(client, "make Mack the war goal")["desk"]["goals"][0]
        assert goal["region"] == world.get_marshal("Mack").location == "Swabia"


# ═══ reached, and dropped ════════════════════════════════════════════════════

class TestReachedAndDropped:
    def test_a_place_taken_reads_taken_and_stops_calling_for_a_march(self, client, world):
        _say(client, "the war goal is Vienna")
        world.get_region("Vienna").controller = world.player_nation
        world.invalidate_active_nations_cache()
        desk = _say(client, "status")["desk"]
        assert desk["war"]["text"].endswith("— your war goal: Vienna (taken).")
        assert desk["goals"][0]["status"] == "taken" and desk["goals"][0]["region"] == ""
        assert all(not row["id"].startswith("goal:") for row in desk["decide"])

    def test_an_army_destroyed_reads_destroyed(self, client, world):
        """Destroyed by the player's own battle (the tombstone's victor): he knows it."""
        _say(client, "make Mack the war goal")
        world.destroy_marshal(world.get_marshal("Mack"), "battle", victor=world.player_nation)
        assert _say(client, "status")["desk"]["war"]["text"].endswith("— your war goal: Mack's army (destroyed).")

    def test_a_fall_out_of_the_players_sight_is_not_told(self, client, world):
        """FOG (the review): a commander destroyed in a battle the player had no part in leaves the goal
        as it stood — open, unringed — until the war ends; only his name and side are public."""
        _say(client, "make Mack the war goal")
        world.destroy_marshal(world.get_marshal("Mack"), "battle", victor="Russia")
        desk = _say(client, "status")["desk"]
        assert desk["war"]["text"].endswith("— your war goal: Mack's army."), desk["war"]["text"]
        assert desk["goals"][0]["status"] == "open" and desk["goals"][0]["region"] == ""
        assert all(not row["id"].startswith("goal:") for row in desk["decide"])

    def test_a_goal_whose_war_is_over_is_dropped_as_the_turn_begins(self, client, world):
        from backend.game_logic import armies
        _say(client, "the war goal is Vienna")
        for key in list(world.diplomatic_states):
            if "France" in key.split("|") and "Austria" in key.split("|"):
                world.diplomatic_states[key] = "PEACE"
        assert war_goals.status(world, "Austria", world.war_goals["Austria"]) == "gone"
        assert war_goals.payload(world, {"wars": []}) == []        # never shown once gone …
        said = armies.roll_call(world)                             # … and pruned at the turn's start
        assert world.war_goals == {} and said and "is dropped" in said[0]
        assert [e["op"] for e in world.event_log if e.get("type") == "war_goal"][-1] == "drop"

    def test_a_board_with_no_goal_is_never_touched(self, world):
        before = world.to_dict()
        assert war_goals.prune(world) == [] and war_goals.payload(world, {"wars": []}) == []
        assert world.to_dict() == before


# ═══ saved, loaded, taken back ═══════════════════════════════════════════════

class TestSavedLoadedAndTakenBack:
    def test_the_store_is_saved_only_when_it_holds_something(self, client, world):
        from backend.models.world_state import WorldState
        assert "war_goals" not in world.to_dict()
        _say(client, "the war goal is Vienna")
        saved = world.to_dict()
        assert saved["war_goals"] == {"Austria": {"kind": "place", "target": "Vienna",
                                                  "turn": world.current_turn}}
        with _quiet():
            again = WorldState.from_dict(json.loads(json.dumps(saved, default=str)))
        assert again.war_goals == saved["war_goals"]

    def test_an_old_save_loads_none(self, _snapshot):
        from backend.models.world_state import WorldState
        with _quiet():
            assert WorldState.from_dict(json.loads(_snapshot)).war_goals == {}

    def test_a_goal_can_be_taken_back(self, client, world):
        reply = _say(client, "the war goal is Vienna")
        assert reply["undo"]["available"] is True
        with _quiet():
            back = client.post("/undo").json()
        assert back["taken_back"] is True and world.war_goals == {}
        assert "goals" not in back["desk"]

    def test_the_seam_down_no_goal_is_read_or_set(self, client, world, monkeypatch):
        world.war_goals = {"Austria": {"kind": "place", "target": "Vienna", "turn": 1}}
        monkeypatch.setattr(war_goals, "a_war_has_a_goal", lambda: False)
        desk = _say(client, "status")["desk"]
        assert "goals" not in desk and "goal:" not in desk["war"]["text"]
        assert _say(client, "the war goal is Vienna")["success"] is False
