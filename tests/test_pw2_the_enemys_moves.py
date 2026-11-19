"""Row PW "Plain Words", part 2 (November 18, 2026) — the enemy's moves, played on the map.

The user, mid-session, of the report that opened when he ended the turn: "while you were away isnt thematic
or sensible, can we show the pieces moving or something better? thinj on it". The report TOLD the turn; the
map now SHOWS it first — the pieces march (the fog's markers too), the provinces that changed hands take
their colour where the eye already is and wear a plaque for a moment, and then the report opens with the
same lines. Any press ends it.

The backend's half (the plaques' words) is pinned on behaviour; the client's on its source, and driven in
the real client at the first player's own setup by `tests/test_dd_b_the_client_hands.py`
(`TestRowPWTheEnemysMovesArePlayedOnTheMap`).
"""

from __future__ import annotations

import pathlib
import re

import pytest

from backend.game_logic import while_you_waited as WYW
from backend.models.intel import FULL
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


@pytest.fixture
def board():
    """The flag world: France at war with Britain and Prussia."""
    world = WorldState()
    for m in world.marshals.values():
        if m.location == "Rhineland" and m.nation != world.player_nation:
            m.location = "Dresden"
    world._intel_entry("Rhineland").visibility = FULL
    return world


class TestThePlaquesAreTheReportsOwnWords:
    def test_a_province_lost_wears_who_took_it(self, board):
        before = WYW.snapshot(board)
        before["corps"].pop("Belgium", None)
        board.get_region("Belgium").controller = "Britain"
        board.get_marshal("Ney").location = "Paris"
        board.get_marshal("Wellington").location = "Belgium"
        board._intel_entry("Belgium").visibility = FULL
        digest = WYW.digest(board, before, {"nations": {"Britain": {"actions": [{"events": [{
            "type": "conquest", "marshal": "Wellington", "region": "Belgium", "unopposed": True,
            "captured_by": "Britain", "captured_from": "France"}]}]}}}, [])
        assert digest["plaques"] == [{"region": "Belgium", "tone": "bad", "text": "Belgium — lost to Britain"}]

    def test_a_battle_is_rimmed_by_how_it_went(self):
        rows = WYW._plaques([], [], [
            {"place": "Ulm", "result": "won"}, {"place": "Jena", "result": "lost"},
            {"place": "Eylau", "result": "none"}, {"place": "Wagram", "result": "open"},
            {"place": "", "result": "won"}], [], [])
        assert rows == [
            {"region": "Ulm", "tone": "good", "text": "Ulm — battle won"},
            {"region": "Jena", "tone": "bad", "text": "Jena — battle lost"},
            {"region": "Eylau", "tone": "battle", "text": "Eylau — battle — no winner"},
            {"region": "Wagram", "tone": "battle", "text": "Wagram — battle — no winner yet"},
        ]

    def test_the_players_own_losses_lead_and_the_map_wears_six_at_most(self):
        lost = [{"region": f"L{i}", "to_shown": "Austria"} for i in range(4)]
        friends = [{"region": "Swabia", "from_shown": "Bavaria", "to_shown": "Austria"}]
        gained = [{"region": "Tyrol"}]
        friends_gained = [{"region": "Hanover", "to_shown": "Holland"}]
        rows = WYW._plaques(lost, friends, [{"place": "Ulm", "result": "open"}], gained, friends_gained)
        assert len(rows) == WYW.MAX_PLAQUES == 6
        assert [r["region"] for r in rows] == ["L0", "L1", "L2", "L3", "Swabia", "Ulm"]
        assert rows[4] == {"region": "Swabia", "tone": "bad", "text": "Swabia — Bavaria lost it to Austria"}
        tail = WYW._plaques([], [], [], gained, friends_gained)
        assert tail == [{"region": "Tyrol", "tone": "good", "text": "Tyrol — now yours"},
                        {"region": "Hanover", "tone": "good", "text": "Hanover — now Holland's"}]

    def test_a_quiet_turn_wears_none(self, board):
        digest = WYW.digest(board, WYW.snapshot(board), {"nations": {}}, [])
        assert digest["quiet"] is True and digest["plaques"] == []


class TestTheMapPlaysTheBoardInTwoBeats:
    """`map_renderer_base.play_all_regions` / `finish_play`."""

    MAP = _src(SCENES / "map_renderer_base.gd")

    def test_beat_one_holds_the_old_colours_while_the_pieces_march(self):
        play = _func(self.MAP, "play_all_regions")
        assert 'if str(old_holder) != str(new_holder):' in play
        assert 'kept["controller"] = old_holder' in play, "a province that changed hands keeps its colour"
        assert "update_all_regions(held)" in play and "_play_final = map_data" in play
        assert 'return {"changed": changed, "moved": marched}' in play
        pieces = _func(self.MAP, "_update_war_table_pieces")
        # (row PW part 3: the piece WALKS its road in the board's time — the played board's `_play_seconds`,
        # else the road's own length)
        assert ("var seconds: float = _play_seconds if _play_seconds > 0.0 else "
                "march_seconds(road_names.size() - 1)") in pieces
        assert "piece.march(road_layer, seconds)" in pieces

    def test_the_fogs_markers_march_too(self):
        """Most enemy corps are markers ("Mack ?"): static nodes that jumped."""
        play = _func(self.MAP, "play_all_regions")
        assert "var was: Dictionary = _play_places(region_marshals, region_fogged_forces)" in play
        assert 'if bool(a["piece"]) and bool(b["piece"]) and pieces_layer != null:' in play, (
            "piece to piece is the standee's own march")
        assert 'for key in ["marshals", "fogged_forces"]:' in play, (
            "the marcher is held out of the board the march is shown on")
        places = _func(self.MAP, "_play_places")
        assert 'not (str(f.get("name", "")) in ["", "?"])' in places, "a nameless force cannot be followed"
        marker = _func(self.MAP, "_play_spawn_marker")
        assert "force_layer.add_child(marker)" in marker, "the next board's rebuild frees it"
        assert 'tween_property(marker, "position"' in marker

    def test_beat_two_is_the_new_board_whole_and_only_once(self):
        finish = _func(self.MAP, "finish_play")
        assert "if _play_final.is_empty():" in finish and "return false" in finish
        assert "update_all_regions(final)" in finish
        update = _func(self.MAP, "update_all_regions")
        assert update.split("var wired_data", 1)[0].count("_play_final = {}") == 1, (
            "a board from anywhere else ends a played one: an older board never lands over a newer")

    def test_a_played_board_finishes_itself(self):
        """The review (PW2-R9): a letter, a petition or a paradox that answers the end of the turn first
        returns before the telling — the board would stand in its old colours with its marchers out."""
        assert "const PLAY_SELF_FINISH_S := 0.3" in self.MAP
        play = _func(self.MAP, "play_all_regions")
        assert "get_tree().create_timer(march_s + PLAY_SELF_FINISH_S).timeout.connect(" in play
        assert "_play_self_finish.bind(_play_serial))" in play
        own = _func(self.MAP, "_play_self_finish")
        assert "if serial == _play_serial:" in own, "a later board, or the caller's own finish, stands it down"
        finish = _func(self.MAP, "finish_play")
        assert finish.index("_play_serial += 1") < finish.index("if _play_final.is_empty():")
        main = _src(SCRIPTS / "main.gd")
        routed = main[main.index("if _route_response_ui(response, _post_hud_response_routes, _render_own_result):"):][:420]
        assert "_pw_replay_board = {}" in routed


class TestTheReportWaitsForTheMap:
    MAIN = _src(SCRIPTS / "main.gd")

    def test_only_a_turn_whose_report_will_open_is_played(self):
        due = _func(self.MAIN, "_pw_replay_due")
        for guard in ('.has("enemy_phase")', "UiSettings.get_play_enemy_moves()", "UiSettings.get_reduce_motion()",
                      'DisplayServer.get_name() == "headless"'):
            assert guard in due, guard
        assert "_pw_digest_has_news(digest) or not _enemy_phase_is_quiet_fog(response.enemy_phase)" in due
        hud = _func(self.MAIN, "_sync_response_hud")
        assert "_update_map_from_game_state(response.game_state, _pw_replay_due(response))" in hud
        refresh = _func(self.MAIN, "_update_map_from_game_state")
        assert "map_area.play_all_regions(game_state.map_data, PW_REPLAY_MARCH_S)" in refresh
        assert "map_area.update_all_regions(game_state.map_data)" in refresh

    def test_the_report_opens_when_the_telling_ends(self):
        result = _func(self.MAIN, "_on_command_result")
        branch = result.split("pending_enemy_phase_response = response  # Store for post-enemy-phase flow", 1)[1][:400]
        assert "if not _pw_replay_board.is_empty():" in branch
        assert "_pw_play_then_report(response.enemy_phase, turn, wyw)" in branch
        assert "_show_enemy_phase_dialog(response.enemy_phase, turn, wyw)" in branch
        play = _func(self.MAIN, "_pw_play_then_report")
        assert "_pw_replay_then = _show_enemy_phase_dialog.bind(enemy_phase, turn, digest)" in play
        assert play.index("create_timer(PW_REPLAY_MARCH_S)") < play.index("map_area.finish_play()") \
            < play.index("_pw_replay_plaques_show(plaques)") < play.index("_pw_replay_finish(false)")
        finish = _func(self.MAIN, "_pw_replay_finish")
        assert "map_area.finish_play()" in finish and "then.call()" in finish
        assert "_pw_replay_clear_stage()" in finish

    def test_any_press_ends_it(self):
        head = _func(self.MAIN, "_input").split("_ui6_press_outside_folds_the_log(event)", 1)[0]
        assert "if _pw_replay_running and _pw_replay_skips(event):" in head
        assert "_pw_replay_finish(true)" in head and "get_viewport().set_input_as_handled()" in head
        skips = _func(self.MAIN, "_pw_replay_skips")
        assert "MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT" in skips and "event.echo" in skips

    def test_a_modifier_alone_is_no_answer(self):
        """The review (PW2-R11): Shift, Alt on its way to Alt+Tab, the screenshot key."""
        assert ("const PW_REPLAY_NO_SKIP_KEYS := [KEY_SHIFT, KEY_CTRL, KEY_ALT, KEY_META, KEY_CAPSLOCK, "
                "KEY_NUMLOCK,") in self.MAIN
        skips = _func(self.MAIN, "_pw_replay_skips")
        assert ("return not (event.keycode in PW_REPLAY_NO_SKIP_KEYS) and not event.alt_pressed and not "
                "event.meta_pressed") in skips

    def test_the_map_takes_no_pointer_while_it_is_told(self):
        """The review (PW2-R10): the map's `_input` runs before main's — the press that skipped the telling
        also picked the province under the cursor."""
        assert "map_area.pointer_blocked_check = _map_pointer_blocked" in self.MAIN
        blocked = _func(self.MAIN, "_map_pointer_blocked")
        assert "return _pw_replay_running or _is_modal_dialog_open()" in blocked
        gate = _func(_src(SCENES / "map_renderer_base.gd"), "_should_handle_map_pointer_event")
        assert "if _pointer_is_blocked():" in gate

    def test_the_stage_is_plain_and_stands_under_every_window(self):
        assert 'const PW_REPLAY_BANNER := "THE ENEMY MOVES"' in self.MAIN
        assert 'const PW_REPLAY_SKIP_HINT := "click, or press any key, to skip"' in self.MAIN
        stage = _func(self.MAIN, "_pw_replay_stage")
        assert "_pw_replay_layer.layer = 24" in stage, "over the map, under the war card (25) and every window"
        plaques = _func(self.MAIN, "_pw_replay_plaques_show")
        assert 'map_area.screen_point_of_region(str(row.get("region", "")))' in plaques
        assert "box.position.y += want.y + 4.0" in plaques, "two plaques never stand on each other"

    def test_the_switch_is_a_players_default_and_a_harness_keeps_the_report(self):
        settings = _src(SCRIPTS / "ui_settings.gd")
        assert '_config().get_value("orders", "play_enemy_moves", not harness_active())' in settings
        panel = _src(SCRIPTS / "settings_panel.gd")
        assert '_add_switch("Show the enemy\'s moves on the map", "PlayEnemyMovesToggle"' in panel
        assert "UiSettings.set_play_enemy_moves(on)" in panel
        tool = _src(REPO / "tools" / "dd_b_client.gd")
        assert 'UiSettings._cfg.set_value("orders", "play_enemy_moves", true)' in tool, (
            "the instrument at the player's own setup plays as his game does")
        assert "while _replay_running() and Time.get_ticks_msec() - telling < REPLAY_MAX_MS:" in tool
