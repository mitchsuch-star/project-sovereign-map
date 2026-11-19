"""Row PW "Plain Words", part 3 (November 19, 2026) — the finishing pass.

The user, after part 2's hand-over listed what was left: "fix these the general game ux and perhaps animate
pieces moving and make sure the game isnt clunky or wierd to play and everything makes sense … dont ask me
questions use reason", then "sound when they move too think of a human playing game, also evaluate the
utility of the parser and typed commands … is there a way to make it fun".

What it built, pinned here: the last order TAKEN BACK (`backend/commands/take_back.py`; the Take back chip,
Ctrl+Z, the typed `undo`); a march that WALKS its road, leaves a trail and is heard; the changed provinces
flashing once; a word beside every bare counter; trust and authority said for what they are; Talleyrand's
figure in everyday words beside a table that adds up to it; the map's key; the empty command line offering
what typing is best at; Esc setting a letter aside. PW2-D1 (no price tag says "AP") is closed in
`test_pw2_the_screens.py`. The real client is driven at the first player's own setup by
`tests/test_dd_b_the_client_hands.py::TestRowPW3TheFinishingPass`.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import pathlib
import re
from types import SimpleNamespace

import pytest

from backend.commands import take_back as TB
from backend.game_logic import counsel as CO

REPO = pathlib.Path(__file__).resolve().parents[1]
CLIENT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"


def _src(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^\S|\Z)", source, re.S | re.M)
    assert match, f"no func {name}"
    return match.group(0)


@contextlib.contextmanager
def _shipped_board(monkeypatch):
    """A fresh SHIPPED 1805 board behind the real app with the mock parser -> (client, backend.main).
    (The suite pins `SOVEREIGN_SCENARIO=none`; these rows need France's marshals in the field.)"""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            M._reset_world_state()
            M.parser = CommandParser(use_real_llm=False)
        yield TestClient(M.app), M
    finally:
        M.world, M.game_state["world"], M.parser = prior
        TB.new_board()


# ═════════════════════════════════════════════════════════════════════════════
# 1. The take-back — the rule, on a board small enough to read
# ═════════════════════════════════════════════════════════════════════════════

class _Board:
    """A world as the take-back sees one: a save dict, a turn, whose soil is whose."""

    def __init__(self):
        self.state = {
            "actions_remaining": 4, "gold": 800, "command_history": [], "battles_this_turn": [],
            "marshals": {"Ney": {"location": "Paris"}},
            "regions": {"Paris": {"controller": "France"}, "Lyon": {"controller": "France"},
                        "Baden": {"controller": "Austria"}},
            "intel": {"Paris": {"visibility": "full"}, "Lyon": {"visibility": "partial"},
                      "Baden": {"visibility": "unknown"}},
            "treaties": [],
        }
        self.current_turn = 3
        self.player_nation = "France"
        self.vassals = {}
        self.regions = {name: SimpleNamespace(controller=row["controller"])
                        for name, row in self.state["regions"].items()}
        self.restored = 0

    def to_dict(self):
        return copy.deepcopy(self.state)

    def _restore_from_snapshot(self, snapshot):
        self.state = copy.deepcopy(snapshot)
        self.restored += 1

    def calculate_visibility(self):
        pass


def _order(board, change, reply=None, words="Ney, move to Lyon"):
    """One command: the board marked, changed as the order changes it, the reply settled."""
    before = TB.mark(board)
    change(board.state)
    board.state["command_history"].append(words)
    out = {"success": True}
    out.update(reply or {})
    TB.settle(board, before, out, words)
    return out


def _march(state):
    state["marshals"]["Ney"]["location"] = "Lyon"
    state["actions_remaining"] -= 1
    state["intel"]["Lyon"] = {"visibility": "full"}       # his own soil, seen better: nothing new


@pytest.fixture(autouse=True)
def _an_empty_stack():
    TB.forget()
    TB._WHY_NOT = "nothing"
    yield
    TB.forget()
    TB._WHY_NOT = "nothing"


class TestTheTakeBackRule:

    def test_an_order_that_showed_and_rolled_nothing_is_kept_and_comes_back_whole(self):
        board = _Board()
        opening = board.to_dict()
        _order(board, _march)
        offer = TB.offer(board)
        assert offer["available"] is True and offer["words"] == "Ney, move to Lyon" and offer["kept"] == 1
        result = TB.take_back(board)
        assert result["ok"] is True and "Ney, move to Lyon" in result["message"]
        assert "its actions are yours again" in result["message"]
        assert board.state == opening and board.restored == 1
        assert TB.offer(board) == {"available": False, "words": "", "kept": 0, "why": TB.WHY["nothing"]}
        assert TB.take_back(board)["ok"] is False, "nothing is taken back twice"

    def test_a_question_changes_nothing_and_leaves_the_kept_order_kept(self):
        board = _Board()
        _order(board, _march)
        _order(board, lambda state: None, words="what can Ney do?")
        assert TB.offer(board)["words"] == "Ney, move to Lyon"
        # help's own bookkeeping (a hint marked shown) is no order either
        _order(board, lambda state: state.update(muster_hint_shown=True), words="what if Ney attacks Mack")
        assert TB.offer(board)["words"] == "Ney, move to Lyon"
        for key in ("muster_hint_shown", "coordination_tutorial_shown", "first_open_seen", "command_history"):
            assert TB._inert(key), key
        for key in ("marshals", "treaties", "diplomatic_points", "dialogue_manager"):
            assert not TB._inert(key), key

    @pytest.mark.parametrize("change, reply, why", [
        (lambda s: s.update(actions_remaining=s["actions_remaining"] - 1), {"pending_objection": True}, "question"),
        (lambda s: s.update(actions_remaining=s["actions_remaining"] - 1), {"requires_input": True}, "question"),
        (lambda s: s["battles_this_turn"].append("Lyon"), {}, "battle"),
        (lambda s: s.update(actions_remaining=s["actions_remaining"] - 1), {"battle_report": {"x": 1}}, "battle"),
        (lambda s: s["regions"]["Baden"].update(controller="France"), {}, "ground"),
        (lambda s: s["intel"]["Baden"].update(visibility="partial"), {}, "fog"),
        (lambda s: s["treaties"].append("a pact"), {}, "more"),
        (lambda s: s.update(actions_remaining=s["actions_remaining"] - 1), {"success": False}, "refused"),
    ])
    def test_an_order_that_did_more_stands_and_says_why(self, change, reply, why):
        board = _Board()
        _order(board, _march)                      # one kept order …
        _order(board, change, reply, words="the order that stands")
        offer = TB.offer(board)
        assert offer["available"] is False and offer["why"] == TB.WHY[why], offer
        assert offer["kept"] == 0, "… and nothing before an order that stands can be reached past it"

    def test_the_turn_moving_on_closes_it(self):
        board = _Board()
        _order(board, _march)
        board.current_turn = 4
        assert TB.offer(board)["available"] is False
        assert TB.offer(board)["why"] == TB.WHY["turn"]

    def test_orders_stack_and_come_back_newest_first(self):
        board = _Board()
        seen = [board.to_dict()]
        for n in range(3):
            _order(board, lambda state: state.update(gold=state["gold"] - 100), words=f"order {n}")
            seen.append(board.to_dict())
        for n in (2, 1, 0):
            assert TB.offer(board)["words"] == f"order {n}"
            assert TB.take_back(board)["ok"] is True
            board.state["command_history"] = []          # (the comparison leaves the log out)
            want = dict(seen[n], command_history=[])
            assert board.state == want, n
        assert TB.offer(board)["available"] is False

    def test_the_stack_is_short(self):
        board = _Board()
        for n in range(TB.MAX_KEPT + 4):
            _order(board, lambda state: state.update(gold=state["gold"] - 1), words=f"order {n}")
        assert TB.offer(board)["kept"] == TB.MAX_KEPT

    def test_anything_else_done_closes_it_and_another_board_has_nothing_kept(self):
        board = _Board()
        _order(board, _march)
        TB.forget()
        assert TB.offer(board) == {"available": False, "words": "", "kept": 0, "why": TB.WHY["since"]}
        _order(board, _march)
        other = _Board()
        assert TB.offer(other)["available"] is False

    def test_the_seam_down_offers_nothing(self, monkeypatch):
        board = _Board()
        _order(board, _march)
        monkeypatch.setattr(TB, "a_taken_order_can_be_taken_back", lambda: False)
        assert TB.offer(board)["available"] is False and TB.offer(board)["why"] == TB.WHY["off"]
        assert TB.take_back(board)["ok"] is False and board.restored == 0
        assert TB.mark(board) is None

    def test_the_typed_words_that_ask_for_it(self):
        for line in ("undo", "Undo.", "un-do", "oops", "take that back", "take it back!", "please undo",
                     "take back my last order", "undo that"):
            assert TB.is_take_back_line(line), line
        for line in ("redo", "undo the alliance with Bavaria", "Ney, take Vienna back", "go back", ""):
            assert not TB.is_take_back_line(line), line

    def test_the_posts_that_keep_it(self):
        assert {"/command", "/undo", "/save"} <= set(TB.KEEPING_POSTS)
        for moving in ("/respond_to_objection", "/cancel_order", "/load", "/new_game", "/mailbox/respond"):
            assert moving not in TB.KEEPING_POSTS, moving

    def test_every_why_is_a_plain_sentence(self):
        for key, words in TB.WHY.items():
            assert words.endswith(".") and "AP" not in words and len(words) < 90, key


class TestTheTakeBackOnTheRealRoad:
    """End to end: the app's own command road, its `/undo`, the typed `undo`, and the other POSTs."""

    @pytest.fixture
    def client(self, monkeypatch):
        with _shipped_board(monkeypatch) as served:
            yield served

    @staticmethod
    def _board(M) -> str:
        state = M.world.to_dict()
        state.pop("command_history", None)
        return json.dumps(state, sort_keys=True, default=str)

    def _a_kept_order(self, client, M):
        """An order of this board that goes through and can be taken back (a stance, in turn, for each of
        the player's own marshals — one that objects is answered and left standing)."""
        player = M.world.player_nation
        for marshal in [m for m in M.world.marshals.values() if m.nation == player]:
            for verb in ("defend", "go aggressive"):
                before = self._board(M)
                with contextlib.redirect_stdout(io.StringIO()):
                    reply = client.post("/command", json={"command": f"{marshal.name}, {verb}"}).json()
                if (reply.get("undo") or {}).get("available"):
                    return before, reply, f"{marshal.name}, {verb}"
                if M.world.pending_objection:
                    with contextlib.redirect_stdout(io.StringIO()):
                        client.post("/command", json={"command": "insist"})
        pytest.fail("no order of this board could be taken back")

    def test_every_reply_says_whether_an_order_can_be_taken_back(self, client):
        client, M = client
        with contextlib.redirect_stdout(io.StringIO()):
            reply = client.post("/command", json={"command": "status"}).json()
        assert reply["undo"] == {"available": False, "words": "", "kept": 0, "why": TB.WHY["nothing"]}

    def test_the_button_puts_the_board_back_whole(self, client):
        client, M = client
        before, reply, words = self._a_kept_order(client, M)
        assert reply["undo"]["words"] == words
        assert self._board(M) != before
        with contextlib.redirect_stdout(io.StringIO()):
            back = client.post("/undo", json={}).json()
        assert back["success"] is True and back["taken_back"] is True and words in back["message"]
        assert back["undo"]["available"] is False
        assert self._board(M) == before, "the board stands as it did before the order"
        assert M.world is M.game_state["world"], "the same world object stands behind the app"

    def test_the_typed_undo_takes_it_back_and_berthier_says_why_when_none_is_kept(self, client):
        client, M = client
        before, _reply, words = self._a_kept_order(client, M)
        with contextlib.redirect_stdout(io.StringIO()):
            back = client.post("/command", json={"command": "undo"}).json()
            again = client.post("/command", json={"command": "undo"}).json()
        assert back.get("taken_back") is True and words in back["message"]
        assert self._board(M) == before
        assert again.get("taken_back") is not True
        assert TB.WHY["nothing"] in again["message"], again["message"]
        assert "until it shows you something new" in again["message"]

    def test_another_answer_given_closes_it(self, client):
        client, M = client
        self._a_kept_order(client, M)
        with contextlib.redirect_stdout(io.StringIO()):
            client.post("/first_open/reset", json={})
            back = client.post("/undo", json={}).json()
        assert back["success"] is False and back["message"] == TB.WHY["since"]

    def test_a_save_keeps_it(self, client, tmp_path, monkeypatch):
        client, M = client
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path))
        _before, _reply, words = self._a_kept_order(client, M)
        with contextlib.redirect_stdout(io.StringIO()):
            client.post("/notifications/dismiss", json={"id": "nothing"})
        assert TB.offer(M.world)["words"] == words

    def test_the_route_is_a_decorator_on_the_driver(self):
        source = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert '@app.post("/command")\n@_records_transcript\n@_keeps_the_take_back\ndef execute_command(' in source
        assert '"undo": _take_back.offer(world),' in source, "every reply carries the offer"
        assert "if request.url.path not in _take_back.KEEPING_POSTS:\n                    _take_back.forget()" in source


# ═════════════════════════════════════════════════════════════════════════════
# 2. Talleyrand's figure, in everyday words, beside a table that adds up to it
# ═════════════════════════════════════════════════════════════════════════════

class TestTalleyrandsFigureIsSaidPlainly:
    WIZARD = _src(SCRIPTS / "diplomacy_wizard.gd")

    def _reading(self, **road):
        best = {"road": "send_peace", "action": "propose_peace", "label": "Propose Peace", "score": -7,
                "threshold": 50, "carries": False,
                "flip": {"component": "coalition_loyalty", "value": -15,
                         "label": "her loyalty to the league — she has no reason of her own to break ranks yet"}}
        best.update(road)
        return {"nearest": best}

    def test_a_road_that_does_not_carry_says_how_far_short_and_what_weighs_most(self):
        line = CO.plain_line(self._reading())
        assert line == ("In plain words: they would say no to “Propose Peace” today. It stands at -7; "
                        "they agree at 50 or more — 57 short. What counts most against it: "
                        "her loyalty to the league (-15).")

    def test_a_road_that_carries_says_yes(self):
        line = CO.plain_line({"best": dict(self._reading()["nearest"], score=62, carries=True)})
        assert line == ("In plain words: they would say yes to “Propose Peace” today. "
                        "It stands at 62; they agree at 50 or more.")

    def test_a_road_with_no_figure_says_nothing(self):
        assert CO.plain_line({}) == ""
        assert CO.plain_line(self._reading(road="battle")) == ""
        assert CO.plain_line(self._reading(score=None)) == ""
        assert CO.plain_line(self._reading(score=True)) == ""

    def test_the_page_carries_the_line_and_the_act_it_is_about(self):
        source = (REPO / "backend" / "game_logic" / "counsel.py").read_text(encoding="utf-8")
        assert '"plain": plain_line(reading),' in source
        assert '"quoted_action": str(quoted.get("action") or ""),' in source
        diplomacy = (REPO / "backend" / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        assert '_quoted = str((_counsel or {}).get("quoted_action") or "")' in diplomacy
        assert 'if _quoted in ("propose_peace", "propose_armistice"):' in diplomacy
        assert '"others": int(_total - _shown),' in diplomacy

    def test_the_table_adds_up_on_the_real_page(self, monkeypatch):
        with _shipped_board(monkeypatch) as (client, M):
            with contextlib.redirect_stdout(io.StringIO()):
                pages = [client.get("/diplomatic_preview", params={"nation": nation}).json()
                         for nation in ("Austria", "Russia", "Britain", "Prussia")]
        quoted = [page for page in pages if (page.get("counsel") or {}).get("plain")]
        assert quoted, "no court's counsel carries its plain line"
        for page in quoted:
            assert page["counsel"]["plain"].startswith("In plain words: they would say "), page["counsel"]["plain"]
        tables = [page["acceptance_preview"] for page in pages if page.get("acceptance_preview")]
        assert tables, "no court of the board has a factor table"
        for table in tables:
            rows = sum(int(row["value"]) for row in table["positive"] + table["negative"])
            assert rows + int(table["others"]) == int(table["score"]), table
            assert table["for_label"] and int(table["threshold"]) == 50, table

    def test_the_client_prints_the_line_the_act_and_the_total(self):
        assert 'const FACTORS_FOR := "For “%s”"' in self.WIZARD
        assert 'factor_rows.append(["Everything else",' in self.WIZARD
        assert 'for_line += " — all told [b][color=#"' in self.WIZARD
        assert '"]" + str(all_told) + "[/color][/b]; they agree at " + str(agree_at) + " or more"' in self.WIZARD
        show = _func(self.WIZARD, "_show_assessment") if "func _show_assessment(" in self.WIZARD else self.WIZARD
        assert 'str((counsel_payload as Dictionary).get("plain", ""))' in show
        assert show.count("bbcode += plain_part") == 2, "under the whole counsel and under its folded opening"


# ═════════════════════════════════════════════════════════════════════════════
# 3. The march — it walks its road, leaves a trail, and is heard
# ═════════════════════════════════════════════════════════════════════════════

class TestTheMarchWalksItsRoad:
    PIECE = _src(SCENES / "war_table_piece.gd")
    RENDERER = _src(SCENES / "map_renderer_base.gd")
    ORDERS = _src(SCENES / "map_order_layer.gd")
    AUDIO = _src(SCRIPTS / "audio_manager.gd")
    MAIN = _src(SCRIPTS / "main.gd")

    def test_a_piece_walks_leg_by_leg_and_steps_as_it_goes(self):
        march = _func(self.PIECE, "march")
        assert "func march(road: Array, duration: float) -> void:" in march
        assert "if duration <= 0.0 or UiSettings.get_reduce_motion() or not is_inside_tree():" in march, (
            "Reduce motion sets him down at once")
        assert "_move_tween.tween_callback(set_facing.bind(\"r\"))" in march, "he faces the way each leg runs"
        assert 'var step := _move_tween.tween_property(self, "position", p, duration * float(lengths[i]) / total)' in march
        assert "_move_tween.tween_callback(_end_stride)" in march and "_begin_stride()" in march
        lift = _func(self.PIECE, "_set_lift")
        assert 'spr.position = offset if layer == "shadow" else offset - Vector2(0.0, px)' in lift, (
            "the shadow stays on the ground")
        assert _func(self.PIECE, "move_to").strip().endswith("march([target], duration)")

    def test_the_road_is_the_maps_own_links(self):
        road = _func(self.RENDERER, "march_road")
        assert "var links = _march_links()" in road
        assert "for _depth in range(MARCH_MAX_HOPS):" in road
        assert "return [from_region, to_region]" in road, "no road found: the two ends alone"
        assert "const MARCH_STEP_S := 0.36" in self.RENDERER
        assert "const MARCH_MIN_S := 0.6" in self.RENDERER and "const MARCH_MAX_S := 1.6" in self.RENDERER
        game_map = _src(SCENES / "map.gd")
        assert "return _region_topology if not _region_topology.is_empty() else super._march_links()" in game_map

    def test_the_board_marches_its_pieces_and_sounds_them_once(self):
        pieces = _func(self.RENDERER, "_update_war_table_pieces")
        assert "var road_names: Array = march_road(prev_region, region)" in pieces
        assert ("var seconds: float = _play_seconds if _play_seconds > 0.0 else "
                "march_seconds(road_names.size() - 1)") in pieces
        assert "piece.march(road_layer, seconds)" in pieces
        assert "order_layer.add_trail(road_world, nation_color, seconds)" in pieces
        assert "if marched > 0:\n\t\t_sound_the_march(marched_s, marched_horse)" in pieces
        sound = _func(self.RENDERER, "_sound_the_march")
        assert "AudioManager.play_march(seconds, horse)" in sound
        assert 'get_tree().create_timer(seconds).timeout.connect(AudioManager.play.bind("march_halt"))' in sound

    def test_the_marchs_sound_is_the_orders_own_cue(self):
        play = _func(self.AUDIO, "play_march")
        assert 'inst._play_cue("horse_trot" if horse else "order_march", maxf(seconds, 0.6))' in play
        assert '"march_halt": {"files": ["battle/boots_halt.ogg"], "bus": "SFX", "db": -8.0' in self.AUDIO
        assert '"move": "order_march", "march": "order_march", "move_to": "order_march",' in self.AUDIO, (
            "one cue for the order and the march: its throttle makes them one sound")
        marker = _func(self.RENDERER, "_play_spawn_marker")
        assert 'AudioManager.play("march_step")' in marker, "a half-seen force is heard faintly"
        assert "order_layer.add_trail([positions[g[\"from\"]], positions[g[\"to\"]]], nation_color" in marker

    def test_the_trail_is_drawn_as_he_goes_and_fades(self):
        assert "const TRAIL_LINGER_S := 3.2" in self.ORDERS
        trails = _func(self.ORDERS, "_draw_trails")
        assert "var shown := _trail_head(pts, clampf(age / march_s, 0.0, 1.0))" in trails
        assert "if age >= march_s + TRAIL_LINGER_S:" in trails
        draw = _func(self.ORDERS, "_draw")
        assert draw.index("_draw_trails(xform)") < draw.index("_draw_flashes(xform)")

    def test_the_enemys_moves_are_given_the_time_to_walk(self):
        assert "const PW_REPLAY_MARCH_S := 1.4" in self.MAIN

    def test_the_changed_provinces_flash_once(self):
        play = _func(self.MAIN, "_pw_play_then_report")
        assert '_pw_last_replay["flashed"] = true' in play
        assert '"flashed": false, "digest_turn": int(digest.get("turn", -1))}' in play
        say = _func(self.MAIN, "_pw_say_the_digest")
        assert ('var told: bool = bool(_pw_last_replay.get("flashed", false)) \\\n'
                '\t\tand int(_pw_last_replay.get("digest_turn", -1)) == int(digest.get("turn", -2))') in say
        assert "if not told and flash is Array and not flash.is_empty()" in say


# ═════════════════════════════════════════════════════════════════════════════
# 4. The words beside the figures; trust and authority; the map's key
# ═════════════════════════════════════════════════════════════════════════════

class TestEveryCounterWearsAWord:
    MAIN = _src(SCRIPTS / "main.gd")
    TOP = _src(SCRIPTS / "top_bar.gd")
    CARD = _src(SCRIPTS / "selection_card.gd")

    def test_the_desks_counters(self):
        # (the part's own first reading: no reader could say what "Admin" buys or which arm each levy
        # is — the words now say it)
        assert ('["ActionsDisplay/ActionsLabel", "Actions"], '
                '["AdminDisplay/AdminLabel", "Admin (build · recruit)"],\n'
                '\t["ManpowerDisplay/InfLabel", "Recruits: foot"], ["CavalryDisplay/CavLabel", "horse"], '
                '["ArtilleryDisplay/ArtLabel", "guns"],') in self.MAIN
        # each levy is its own group of the status row: the row wraps between them, and the command
        # window's width floor stays its input row's (UXR-X21's driven pin)
        scene = _src(SCENES / "main.tscn")
        for group in ("ManpowerDisplay", "CavalryDisplay", "ArtilleryDisplay"):
            assert f'[node name="{group}" type="HBoxContainer" parent="BottomLeftUI/MainMargin/MainLayout/' \
                   f'Header/HeaderMargin/HeaderContent/StatusSection"]' in scene, group
        dress = _func(self.MAIN, "_ui6_dress_status_row")
        assert "key_label.text = short if folded else str(key_label.get_meta(\"authored\"))" in dress
        assert "key_label.visible = (short != \"\") if folded else true" in dress
        bar = _func(self.MAIN, "_ui6_bar_figures_bbcode")
        assert ']Turn " + str(int(current_turn))' in bar and "]Actions \"" in bar and "]Admin \"" in bar
        tips = _func(self.MAIN, "_ui6_refresh_status_tips")
        assert "Actions left this turn: %d of %d — each order to a marshal spends them" in tips
        assert "Men you can still recruit — infantry %s · cavalry %s · artillery %s" in tips

    def test_the_top_bars_figures(self):
        assert ('const FIGURE_WORDS := {"gold": "Gold", "dp": "Diplomacy", "authority": "Authority", '
                '"threat": "Threat",\n\t"turn": "Turn"}') in self.TOP
        group = _func(self.TOP, "_group")
        assert "if FIGURE_WORDS.has(glyph_name):\n\t\tbox.add_child(_figure_word(glyph_name))" in group
        fit = _func(self.TOP, "_apply_fit_step")
        assert "(word as Label).visible = step < 1 and not _compact" in fit, "the words are the first thing shed"
        chest = _func(self.TOP, "_refresh_treasury_text")
        assert 'var net_tail := " a turn" if _fit_step < 1 and not _compact else ""' in chest, (
            "the reading: \"+828 — I cannot tell the period\"")
        assert 'shown_words + "  " + net_words + net_tail' in chest

    def test_an_orders_price_is_in_words_on_the_card(self):
        slot = _func(self.CARD, "_slot_button")
        assert 'tail = Utils.plural(int(spec["price"]), "action")' in slot
        assert 'var full := label + (" · " + tail if tail != "" else "")' in slot
        strip = _func(self.MAIN, "_render_order_strip")
        assert 'prices = "a province he reaches this turn costs " + Utils.plural(move_ap, "action")' in strip
        assert '+ " · a longer march costs " + Utils.plural(int(_order_reach.get("ap", 0)), "action")' in strip


class TestTrustAndAuthorityAreSaid:
    TOP = _src(SCRIPTS / "top_bar.gd")
    OBJECTION = _src(SCRIPTS / "objection_dialog.gd")
    TERMS = _src(SCRIPTS / "codex_terms.gd")

    def test_the_crowns_hover_says_what_it_is_and_what_each_level_does(self):
        assert 'const AUTHORITY_WORDS := "Authority is your standing as Emperor, from 0 to 100. You spend it' in self.TOP
        assert "Nothing can be bought that would leave it under 60." in self.TOP
        for line in ("85 or more — your presence in a battle is worth its full +10%",
                     "80 or more — marshals obey more readily and defy less",
                     "60 or more — one more diplomatic point a turn",
                     "under 50 — marshals obey less and defy more",
                     "under 30 — one diplomatic point less a turn"):
            assert line in self.TOP, line
        for jargon in ("the Presence (the aura full)", "the spiral", "the marshals' calm"):
            assert jargon not in self.TOP.split("const AUTHORITY_LINES_TOOLTIP")[1].split("\n")[0], jargon
        tooltip = _func(self.TOP, "_authority_tooltip")
        assert 'var lines: Array = ["Authority %d (%s)" % [value, label], AUTHORITY_WORDS]' in tooltip

    def test_the_levels_are_the_rules_own(self):
        """Each line of the hover is a number the game reads."""
        from backend.game_logic import standing
        assert standing.PURCHASE_FLOOR == 60
        spec = (REPO / "docs" / "AUTHORITY_CURRENCY_SPEC.md").read_text(encoding="utf-8")
        for row in ("| **85** | the aura full (grip); the Presence +10 % on the field",
                    "| **80** | obedience ×1.1; defiance −10 points",
                    "| **60** | +1 diplomatic point a turn",
                    "| **50** | obedience ×0.9; defiance +10",
                    "| **30** | −1 diplomatic point a turn; the vassal spiral"):
            assert row in spec, row

    def test_the_objection_says_whose_each_figure_is(self):
        assert 'trust_label.text = "His trust in you: %d (%s)" % [trust, trust_label_text]' in self.OBJECTION
        assert "trust_label.tooltip_text = TRUST_WORDS" in self.OBJECTION
        assert 'authority_label.text = "Your authority: %d" % authority' in self.OBJECTION
        assert "authority_label.tooltip_text = AUTHORITY_WORDS" in self.OBJECTION
        assert "at 80 or more, always" in self.OBJECTION and "At 20 or less he demands an audience." in self.OBJECTION

    def test_help_and_the_typed_desk_say_the_same(self):
        assert '["Authority", "Your standing as Emperor, from 0 to 100, with every marshal and court. You spend it' in self.TERMS
        assert '["Take back", "A slipped order can be taken back: press Take back on the map\'s controls, press Ctrl+Z, or type undo.' in self.TERMS
        titles = re.findall(r'^\t\["([^"]+)", "', self.TERMS, re.M)
        at = titles.index("Take back")
        assert titles[at - 1] == "Supply" and titles[at + 1] == "Taking a province", "the terms stay A to Z"
        assert titles[0] == "Actions" and "Action points (AP)" not in titles
        desk = (REPO / "backend" / "ai" / "state_desk.py").read_text(encoding="utf-8")
        assert '"authority": "Authority is your standing as Emperor, from 0 to 100, with every marshal and court.' in desk
        assert "at 80 or more he always obeys when you insist." in desk


class TestTheMapHasAKey:
    KEY = _src(SCRIPTS / "map_key.gd")
    MAIN = _src(SCRIPTS / "main.gd")

    def test_every_mark_the_readers_named_is_in_it(self):
        entries = re.findall(r'^\t\["([A-Z ]+)", "([a-z]+)", "([^\n]+)"\],$', self.KEY, re.M)
        kinds = [kind for _section, kind, _words in entries]
        assert kinds == ["piece", "name", "fog", "garrison", "sail", "port", "sea", "land", "flash",
                         "reach", "arrow", "trail"]
        words = " ".join(text for _s, _k, text in entries)
        for said in ("fog of war", "12k = 12,000", "ships of the line", "A red anchor: a port under blockade.",
                     "A gold border marks a capital.", "this turn, 1 turn, 2–3 turns, 4 or more"):
            assert said in words, said
        assert "AP" not in words

    def test_its_samples_are_the_maps_own_plaques_and_colours(self):
        renderer = _src(SCENES / "map_renderer_base.gd")
        assert 'const Plaque = preload("res://scripts/map_plaque.gd")' in self.KEY
        for const, value in (("SEA_SHUT", "Color(0.85, 0.25, 0.25, 0.9)"), ("SEA_LANDING", "Color(0.88, 0.55, 0.18, 0.92)"),
                             ("SEA_WINDOW", "Color(0.95, 0.78, 0.2, 0.95)")):
            assert f"const {const} := {value}" in self.KEY, const
            assert value in renderer, f"{const} is the renderer's own tint"
        assert "\nclass_name " not in self.KEY, "loaded by path, as the plaques are"
        # the blockaded port's mark is ONE drawing, the map's (the first reading: it read as a stopwatch)
        layer = _src(SCENES / "map_connection_layer.gd")
        assert "static func draw_anchor(item: CanvasItem, at: Vector2, r: float, color: Color) -> void:" in layer
        assert "draw_anchor(self, glyph_pos, GLYPH_RADIUS, Utils.cv(GLYPH_COLOR))" in layer
        assert "ConnectionLayer.draw_anchor(self, Vector2(w / 2.0, h / 2.0 + 1.0), 7.0, PORT_RED)" in self.KEY
        assert "var rows := [Utils.MAP_CONNECTION_GREY, SEA_SHUT, SEA_LANDING, SEA_WINDOW]" in self.KEY

    def test_it_stands_on_its_own_layer_over_the_controls(self):
        toggle = _func(self.MAIN, "_pw3_toggle_map_key")
        assert "key_layer.layer = 24" in toggle
        fit = _func(self.MAIN, "_pw3_fit_map_key")
        assert "right = minf(right, hud.position.x - Utils.HUD_MARGIN)" in fit, "clear of the war card"
        assert "_map_key.fit(right - left)" in fit
        ladder = _func(self.MAIN, "_escape_closes_topmost")
        assert ladder.index("_map_key.close_key()") < ladder.index("codex.close()"), "Esc puts it away first"
        # … and on the FOCUSED line too, before a selected corps is let go (the driven pin's find: the
        # line keeps focus after an order, and its own Esc let the general go and left the key open)
        line = _func(self.MAIN, "_on_command_input_gui_input")
        assert line.index("_map_key.close_key()") < line.index("elif _order_engaged():")
        keys = _src(SCRIPTS / "keys.gd")
        assert '["map_key", "Map key", KEY_K],' in keys

    def test_the_two_chips_stand_on_the_maps_controls(self):
        build = _func(self.MAIN, "_pw3_build_map_tools")
        assert '_map_key_btn.name = "MapKeyButton"' in build and '_take_back_btn.name = "TakeBackButton"' in build
        assert 'const MAP_KEY_FACE := "Key"' in self.MAIN and 'const TAKE_BACK_FACE := "Take back"' in self.MAIN
        note = _func(self.MAIN, "_pw3_note_take_back")
        assert "Utils.set_available(_take_back_btn, available," in note
        press = _func(self.MAIN, "_pw3_take_back")
        assert "ToastLayer.say(why if why != \"\" else \"There is no order to take back.\", \"\")" in press, (
            "a press that cannot act says why")
        assert "api_client.take_back_last_order(_on_take_back_result)" in press
        hotkeys = _func(self.MAIN, "_ui5_hotkey_core")
        assert "if event.keycode == KEY_Z and event.ctrl_pressed" in hotkeys
        assert 'if on_line and command_input.text != "":\n\t\t\treturn false' in hotkeys, (
            "a line holding a draft keeps Ctrl+Z for its own text")


# ═════════════════════════════════════════════════════════════════════════════
# 5. The typed line — what it is for; a letter's Esc
# ═════════════════════════════════════════════════════════════════════════════

class TestTheEmptyLineOffersWhatTypingIsBestAt:
    MAIN = _src(SCRIPTS / "main.gd")

    def test_the_ideas_are_questions_built_from_the_board(self):
        ideas = _func(self.MAIN, "_pw3_line_ideas")
        for line in ('out.append("what can %s do?" % who)', 'out.append("what if %s attacks %s?" % [who, foe])',
                     'out.append("what now?")',
                     'out.append(("where is %s?" % foe) if foe != "" else "who is my best general?")'):
            assert line in ideas, line
        assert "var foes: Array = _enemy_offers(origin) if origin != \"\" else []" in ideas, (
            "an enemy the fog shows, nearest first — the completer's own pool")

    def test_they_are_asked_for_never_always_on(self):
        build = _func(self.MAIN, "_build_completions")
        assert "if out.is_empty() and _line_ideas_wanted:\n\t\t\treturn _pw3_line_ideas()" in build
        want = _func(self.MAIN, "_pw3_want_line_ideas")
        assert 'if command_input.text.strip_edges() != "":\n\t\treturn' in want
        assert "_line_ideas_wanted = false   # row PW part 3" in _func(self.MAIN, "_clear_suggestions")
        assert "command_input.focus_exited.connect(_pw3_drop_line_ideas)" in self.MAIN
        assert 'const LINE_IDEAS_PLACEHOLDER := "Ask or order · Tab: ideas"' in self.MAIN

    @pytest.mark.parametrize("line, holds", [
        ("what can Ney do?", "Ney stands at"),
        ("what if Ney attacks Mack?", "Were you to give the order, Sire"),
        ("what now?", "orders would be carried out today"),
        ("where is Mack?", "Mack of Austria"),
        ("who is my best general?", "Sire"),
    ])
    def test_the_desk_answers_what_the_ideas_ask(self, line, holds, monkeypatch):
        """An idea is only worth offering if the desk answers it — free."""
        with _shipped_board(monkeypatch) as (client, M):
            with contextlib.redirect_stdout(io.StringIO()):
                reply = client.post("/command", json={"command": line}).json()
        assert reply["success"] is True, reply["message"]
        assert int((reply.get("action_info") or {}).get("cost", 0) or 0) == 0, "a question is free"
        assert holds in reply["message"], reply["message"][:300]
        assert "I cannot answer that" not in reply["message"]


class TestEscSetsALetterAside:
    POPUP = _src(SCRIPTS / "incoming_proposal_popup.gd")

    def test_esc_presses_not_now_and_never_answers(self):
        handler = _func(self.POPUP, "_unhandled_input")
        assert 'if not visible or not event.is_action_pressed("ui_cancel"):' in handler
        assert "if dismiss_btn == null or not dismiss_btn.visible or dismiss_btn.disabled:\n\t\treturn" in handler
        assert "dismiss_btn.pressed.emit()" in handler
        for answer in ("accept_btn", "reject_btn"):
            assert answer not in handler, "an answer is never given by a reflex key"


# ═════════════════════════════════════════════════════════════════════════════
# PW3-D1 — OPEN, owned by Session H's head: the Cabinet's court list has room
# ═════════════════════════════════════════════════════════════════════════════

_PW3_D1 = ("PW3-D1 OPEN — owner Session H's head (BUG_FIXES.md §PW part 3): at Interface Scale 1.8 on a "
           "765-px-tall view the Cabinet's first page shows two courts above a scroll; this pin turns red "
           "the day the page seats its courts in columns (or folds its fixed head), so the row is closed with it")


class TestPW3D1TheCabinetsCourtListHasRoom:

    def test_the_page_is_the_one_the_row_was_filed_on(self):
        wizard = _src(SCRIPTS / "diplomacy_wizard.gd")
        assert "which nation requires our diplomatic attention?" in wizard
        assert "const MORE_BELOW_WORDS := \"▼ more below\"" in wizard

    @pytest.mark.xfail(strict=True, reason=_PW3_D1)
    def test_the_courts_stand_in_columns(self):
        wizard = _src(SCRIPTS / "diplomacy_wizard.gd")
        assert "COURT_LIST_COLUMNS" in wizard, "the first page seats its courts in columns (PW3-D1's landing)"
