"""Row CC, CC-3 "Select, click, Enter" (+ drag) — Pre-Deploy S13c part 2,
October 17, 2026 (plan `~/.claude/plans/sorted-yawning-clover.md` §CC-3 and
its decision D4: map gestures open a modal confirm card, panel chips send
directly).

On an EMPTY line a click on a piece of ours SELECTS him: a ring at his feet, a
status strip, and every province he can march to tinted by the march's own
clock. The cursor draws the quote's road as a ghost line; a click opens the
confirm card on the EXACT quote — the command, its price, its clock, the order
it replaces, whether he may object — with [Send] [Put in line] [Cancel]. A piece
of ours dragged 8 px and dropped is the same gesture in one motion.

The pins:

* THE REACH IS THE ROAD LAW — `GET /march_reach` reads every province in ONE
  pathfinding pass per rung of `plot_route`'s ladder (`WorldState.
  weighted_paths_from`; the cautious avoid-set computed once — Rule 8), and it
  is pinned equal to the per-province readers it replaces: the one-pass search
  to `find_weighted_path` (ties included), `strategic.march_roads` to
  `march_road`, and a province is in the reach exactly when its
  `march_quote` is taken, with the quote's own road and turns.
* THE EXACT QUOTE — `GET /march_quotes?marshal=…&dest=|enemy=|ally=…` is the
  panel's own quote dict; an enemy we cannot see is refused without a word of
  where he is; both routes are read-only.
* THE CLIENT, DRIVEN (`tools/cc_client_harness.gd`, the real `main.tscn`, real
  keys and real mouse events through `root.push_input`): the selection
  lifecycle, the card's command equal to the quote's, Enter and Esc on the
  card (Enter never reaches the line or ends the turn), the panel shut while a
  corps is selected, every clearing rule, and the drag threshold. SKIPS when
  the engine is absent — and a skip is not a pass.

CC-2's drift census (`tests/test_cc2_march_here.py`) is untouched: the card's
command IS `march_quote`'s, the command that census sends to POST /command.
"""

import contextlib
import io
import json
import os
import random
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import strategic as S
from backend.commands.order_quotes import (
    attack_quote, march_quote, march_quotes_for_region, march_reach, support_quote,
)
from backend.display_names import humanize_entity_name
from backend.models.intel import FULL, PARTIAL
from tests import _chip_census as C
from tests.test_cc_click_and_command import _pick_board

REPO = C.REPO
PROJECT = C.PROJECT
HARNESS = REPO / "tools" / "cc_client_harness.gd"
MAIN_GD = PROJECT / "scripts" / "main.gd"
MAP_GD = PROJECT / "scenes" / "map_renderer_base.gd"
CARD_GD = PROJECT / "scripts" / "order_confirm_card.gd"
LAYER_GD = PROJECT / "scenes" / "map_order_layer.gd"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _src(path):
    return path.read_text(encoding="utf-8")


def _func(src, name):
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 1)
    return src[start:] if nxt < 0 else src[start:nxt]


@pytest.fixture
def client(monkeypatch):
    """A mock-parser 1805 board for ONE test (the suite's conftest pins the
    bare world before every test, so the test re-opens the campaign)."""
    C.board_env(monkeypatch)
    return TestClient(M.app)


def _field(world):
    return [m for m in world.get_player_marshals()
            if int(m.strength or 0) > 0 and not getattr(m, "captured_by", "")]


# ═══ the reach is the road law ══════════════════════════════════════════════

class TestTheOnePassIsTheTargetedSearch:
    """`weighted_paths_from(start, …)[end]` is `find_weighted_path(start, end,
    …)` — the same path, ties included — for the lawful and the cautious
    variants of the ladder."""

    def test_every_end_from_every_corps_of_ours(self, client):
        C.boot()
        w = M.world
        starts = sorted({m.location for m in _field(w)})
        avoid = S.enemy_occupied_regions(w, w.player_nation, fog_aware=True)
        assert avoid, "the boot board sights no enemy — the avoid arm is vacuous"
        cells = bad = 0
        for start in starts:
            for pf in (None, w.player_nation):
                for av in (None, avoid):
                    every = w.weighted_paths_from(start, avoid_regions=av, passable_for=pf)
                    for end in w.regions:
                        cells += 1
                        if every.get(end) != w.find_weighted_path(start, end, avoid_regions=av,
                                                                  passable_for=pf):
                            bad += 1
        assert cells >= 2000 and bad == 0, (cells, bad)   # 5 provinces × 4 variants × 126

    def test_a_closed_or_avoided_province_ends_a_road_and_never_carries_one(self, client):
        """The destination's two exemptions: an avoided province is reachable
        as an END, and no road passes THROUGH it."""
        C.boot()
        w = M.world
        start = next(m.location for m in _field(w))
        neighbour = sorted(w.regions[start].adjacent_regions)[0]
        every = w.weighted_paths_from(start, avoid_regions=[neighbour])
        assert every[neighbour][-1] == neighbour
        assert all(neighbour not in path[:-1] for path in every.values())


class TestTheReachIsTheQuote:

    def _check(self, world):
        cells = taken = 0
        for m in _field(world):
            roads = S.march_roads(world, m, "MOVE_TO")
            reach = march_reach(world, m)
            for dest in world.regions:
                cells += 1
                assert roads[dest] == S.march_road(world, m, dest, "MOVE_TO"), (m.name, dest)
                q = march_quote(world, m, dest)
                assert (dest in reach["reach"]) == q["ok"], (m.name, dest, q["refusal"])
                if q["ok"]:
                    taken += 1
                    row = reach["reach"][dest]
                    if not q["already"]:
                        assert row["turns"] == q["turns"] and row["road"] == q["road"], (m.name, dest)
        return cells, taken

    def test_on_the_boot_board(self, client):
        C.boot()
        cells, taken = self._check(M.world)
        assert cells >= 1000 and taken >= 300, (cells, taken)

    def test_with_one_action_left(self, client):
        """A march costs 2: the reach is empty and says so in the probe's words."""
        C.boot()
        M.world.actions_remaining = 1
        self._check(M.world)
        ordinary = next(m for m in _field(M.world) if m.personality != "literal"
                        and not getattr(m, "is_sovereign", False))
        r = march_reach(M.world, ordinary)
        assert r["ok"] is False and r["reach"] == {}
        assert r["refusal"] == march_quote(M.world, ordinary, sorted(M.world.regions)[0])["refusal"]

    def test_a_fortified_corps(self, client):
        C.boot()
        m = _field(M.world)[0]
        m.fortified = True
        self._check(M.world)
        assert march_reach(M.world, m)["reach"] == {}

    def test_an_order_already_standing(self, client):
        """`_standing_quote`'s identical order — taken at 0 AP — is in the
        reach, marked."""
        C.boot()
        w = M.world
        m, dest = next((m, d) for m in _field(w) if not getattr(m, "is_sovereign", False)
                       for d, row in sorted(march_reach(w, m)["reach"].items())
                       if row["turns"] >= 2 and march_quote(w, m, d)["objection"] == "none"
                       and not march_quote(w, m, d)["contact"])
        with _quiet():
            client.post("/command", json={"command": f"{humanize_entity_name(m.name)}, march to {dest}"})
        w = M.world
        m = w.get_marshal(m.name)
        assert m.strategic_order is not None
        row = march_reach(w, m)["reach"][dest]
        assert row["already"] is True
        assert march_quote(w, m, dest)["already"] is True
        self._check(w)

    def test_the_cautious_avoid_set_is_read_once(self, client, monkeypatch):
        """Rule 8: the avoid-set scans every province — once per selection,
        never once per destination."""
        C.boot()
        w = M.world
        cautious = next(m for m in _field(w) if m.personality == "cautious")
        calls = []
        real = S.enemy_occupied_regions

        def counted(*a, **k):
            calls.append(1)
            return real(*a, **k)
        monkeypatch.setattr(S, "enemy_occupied_regions", counted)
        march_reach(w, cautious)
        assert len(calls) == 1
        calls.clear()
        for dest in sorted(w.regions)[:5]:
            S.march_road(w, cautious, dest)
        assert len(calls) == 5   # sensitive: the per-destination reader scans each time


# ═══ the routes ═════════════════════════════════════════════════════════════

class TestTheRoutes:

    def test_the_reach_route_answers_in_shape(self, client):
        C.boot()
        m = _field(M.world)[0]
        with _quiet():
            r = client.get("/march_reach", params={"marshal": m.name}).json()
        assert r["success"] is True and r["marshal"] == m.name and r["ok"] is True
        assert isinstance(r["ap"], int) and isinstance(r["range"], int)
        assert r["reach"] and all(isinstance(row["turns"], int) for row in r["reach"].values())
        assert r == json.loads(json.dumps(march_reach(M.world, M.world.get_marshal(m.name))))

    def test_the_exact_quote_is_the_panels_own(self, client):
        C.boot()
        w = M.world
        m = _field(w)[0]
        dest = next(d for d in sorted(w.regions) if d != m.location)
        with _quiet():
            r = client.get("/march_quotes", params={"marshal": m.name, "dest": dest}).json()
        assert r["success"] is True
        assert r["quote"] == json.loads(json.dumps(march_quote(w, w.get_marshal(m.name), dest)))
        row = next(q for q in march_quotes_for_region(w, dest)["march"] if q["marshal"] == m.name)
        assert r["quote"]["command"] == row["command"] and r["quote"]["ap"] == row["ap"]

    def test_an_enemy_and_an_ally(self, client):
        C.boot()
        w = M.world
        m, ally = _field(w)[0], _field(w)[1]
        seen = [e for e in w.get_visible_enemies(w.player_nation)
                if w.is_at_war(w.player_nation, e.nation) and int(e.strength) > 0]
        assert seen, "the boot board sights no enemy at war"
        foe = seen[0]
        with _quiet():
            a = client.get("/march_quotes", params={"marshal": m.name, "enemy": foe.name}).json()
            s = client.get("/march_quotes", params={"marshal": m.name, "ally": ally.name}).json()
        assert a["quote"] == json.loads(json.dumps(attack_quote(w, w.get_marshal(m.name), foe)))
        assert s["quote"] == json.loads(json.dumps(support_quote(w, w.get_marshal(m.name), ally)))

    def test_an_unseen_enemy_is_refused_without_a_word_of_him(self, client):
        C.boot()
        w = M.world
        m = _field(w)[0]
        unseen = [e for e in w.marshals.values()
                  if e.nation != w.player_nation and int(e.strength or 0) > 0
                  and w.is_at_war(w.player_nation, e.nation)
                  and w.get_region_intel(e.location).visibility not in (FULL, PARTIAL)]
        assert unseen, "every enemy corps is in sight on the boot board"
        foe = unseen[0]
        with _quiet():
            r = client.get("/march_quotes", params={"marshal": m.name, "enemy": foe.name}).json()
        assert r["success"] is False
        assert foe.location not in r["message"]
        # Sensitive: the same corps, in sight, is quoted.
        w.get_region_intel(foe.location).visibility = FULL
        with _quiet():
            again = client.get("/march_quotes", params={"marshal": m.name, "enemy": foe.name}).json()
        assert again["success"] is True

    def test_only_a_corps_of_ours_in_the_field_is_quoted(self, client):
        C.boot()
        w = M.world
        foreign = next(e for e in w.marshals.values() if e.nation != w.player_nation)
        with _quiet():
            for name in (foreign.name, "Nobody", ""):
                assert client.get("/march_reach", params={"marshal": name}).json()["success"] is False
                assert client.get("/march_quotes", params={"marshal": name or "x",
                                                           "dest": "Swabia"}).json()["success"] is False

    def test_the_routes_write_nothing(self, client):
        C.boot()
        w = M.world
        before = json.dumps(w.to_dict(), sort_keys=True, default=str)
        dm_before = json.dumps(w.dialogue_manager.to_dict(), sort_keys=True, default=str)
        state = random.getstate()
        with _quiet():
            for m in _field(w):
                client.get("/march_reach", params={"marshal": m.name})
                for dest in sorted(w.regions)[:12]:
                    client.get("/march_quotes", params={"marshal": m.name, "dest": dest})
        assert random.getstate() == state, "a quote rolled the game's dice"
        assert json.dumps(M.world.dialogue_manager.to_dict(), sort_keys=True, default=str) == dm_before
        assert json.dumps(M.world.to_dict(), sort_keys=True, default=str) == before

    def test_a_province_hidden_by_fog_names_no_corps_in_the_reach(self, client):
        """The reach carries roads and turns only — never a corps (the quote's
        note is fetched per target, and the CC-2 fog pins hold it)."""
        C.boot()
        r = march_reach(M.world, _field(M.world)[0])
        assert set(r) == {"success", "marshal", "shown", "location", "ap", "range", "ok",
                          "refusal", "reach"}
        assert all(set(row) <= {"turns", "road", "already"} for row in r["reach"].values())


# ═══ the source pins ════════════════════════════════════════════════════════

class TestTheCardIsTheGesturesOwn:

    def test_the_card_is_a_registered_modal(self):
        src = _src(MAIN_GD)
        assert 'dialog_manager.register("order_card", "res://scenes/order_confirm_card.tscn")' in src
        assert "dialog_manager.modal_shown.connect(_on_modal_shown)" in src

    def test_nothing_on_the_line_goes_beneath_the_card(self):
        """The guard is the FIRST statement — ahead of the bare Enter that
        confirms an armed end turn."""
        body = _func(_src(MAIN_GD), "_execute_command")
        first = [ln.strip() for ln in body.split('"""', 2)[2].strip().splitlines()]
        assert first[2:4] == ["if _order_card_open():", "return"], first[:4]
        assert body.index("if _order_card_open():") < body.index("if command.is_empty():")

    def test_the_card_takes_every_key_while_it_is_up(self):
        body = _func(_src(CARD_GD), "_input")
        assert body.index("get_viewport().set_input_as_handled()") < body.index("match event.keycode:")

    def test_the_cards_send_goes_down_the_typed_road(self):
        body = _func(_src(MAIN_GD), "_send_map_order")
        for step in ("if not command_input.editable:", "_add_to_history(command)",
                     "_retire_line_latches()", "set_input_enabled(false)",
                     "api_client.send_command(command, _on_map_order_result)"):
            assert step in body, step
        assert body.index("_retire_line_latches()") < body.index("api_client.send_command(")

    def test_the_esc_ladder_lets_the_selection_go_before_the_panel(self):
        src = _src(MAIN_GD)
        # Re-seated October 18, 2026 (row CC, CC-5): the step reads
        # `_order_engaged()` — a Ctrl-click group is let go by the same Esc.
        # Re-seated October 19, 2026 (DDB-54, Pre-Deploy S13b part 4): the
        # ladder is ONE function, `_escape_closes_topmost`, which the
        # unfocused `_unhandled_input` reads with the selection step and the
        # command line's own Esc reads after clearing the selection itself.
        ladder = _func(src, "_escape_closes_topmost")
        assert "_escape_closes_topmost(true)" in _func(src, "_unhandled_input")
        assert (ladder.index("top_bar.close_all_screens()")
                < ladder.index("if include_selection and _order_engaged() and not _is_modal_dialog_open():")
                < ladder.index("region_panel.close_panel()"))
        line_esc = _func(src, "_on_command_input_gui_input")
        esc = line_esc[line_esc.index("elif event.keycode == KEY_ESCAPE:"):]
        assert (esc.index("_clear_suggestions()") < esc.index("_clear_order_selection()")
                < esc.index("_escape_closes_topmost()")
                < esc.index("command_input.release_focus()"))

    def test_every_send_lets_the_selection_go(self):
        src = _src(MAIN_GD)
        for fn in ("_retire_line_latches", "_execute_command", "_send_end_turn",
                   "_reset_frontend_state_for_world_swap", "_on_map_dismiss_requested"):
            assert "_clear_order_selection()" in _func(src, fn), fn
        assert "_clear_order_selection()" in _func(src, "_on_screen_changed")
        assert "_reread_order_selection()" in _func(src, "_update_map_from_game_state")


class TestTheMapKeepsItsGestures:

    def test_the_left_release_is_read(self):
        body = _func(_src(MAP_GD), "_input")
        assert ("if event is InputEventMouseButton and not event.pressed "
                "and event.button_index == MOUSE_BUTTON_LEFT:") in body
        assert "_release_piece_drag(event)" in body

    def test_a_pressed_piece_follows_the_cursor_over_a_panel_as_a_pan_does(self):
        body = _func(_src(MAP_GD), "_should_handle_map_pointer_event")
        assert "if is_panning or not _drag_pending.is_empty():" in body

    def test_the_middle_drag_pan_is_unchanged(self):
        body = _func(_src(MAP_GD), "_input")
        assert "elif event.button_index == MOUSE_BUTTON_MIDDLE:\n\t\t\tis_panning = true" in body

    def test_the_drag_threshold_is_eight_pixels(self):
        assert "const PIECE_DRAG_THRESHOLD_PX := 8.0" in _src(MAP_GD)

    def test_with_a_selection_the_province_beats_the_fleet(self):
        left = _src(MAP_GD)
        left = left[left.index("elif event.button_index == MOUSE_BUTTON_LEFT:"):]
        left = left[:left.index("elif event.button_index == MOUSE_BUTTON_RIGHT:")]
        # Re-seated October 18, 2026 (row CC, CC-5): `order_engaged()` — a
        # Ctrl-click group's click is an order too, and beats the fleets.
        assert "if not order_engaged() and hovered_fleet.size() > 0:" in left
        assert "if not order_engaged() and hovered_sea_link.size() > 0:" in left
        assert left.index("_arm_piece_drag(event)") < left.index("fleet_clicked.emit(")

    def test_the_order_layer_and_the_card_are_in_the_parse_check(self):
        text = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        for path in ("res://scenes/map_order_layer.gd", "res://scripts/order_confirm_card.gd",
                     "res://scenes/order_confirm_card.tscn"):
            assert f'"{path}"' in text, path


# ═══ the client, driven ═════════════════════════════════════════════════════

def _cc3_board(client):
    """The real backend's answers for one corps of ours: his reach and the
    exact quotes the card will show."""
    C.boot()
    spec = _pick_board()
    w = M.world
    gs = spec["game_state"]
    map_data = gs["map_data"]

    def empty(region):
        row = map_data.get(region, {})
        return not row.get("marshals") and not row.get("fogged_forces")

    subject = dest = None
    for m in sorted(_field(w), key=lambda m: (getattr(m, "is_sovereign", False), m.name)):
        reach = march_reach(w, m)
        near = [d for d in sorted(w.regions[m.location].adjacent_regions)
                if d in reach["reach"] and empty(d)]
        if reach["ok"] and near:
            subject, dest = m, near[0]
            break
    assert subject is not None, "no corps of ours has an empty province beside him in reach"
    with _quiet():
        reach = client.get("/march_reach", params={"marshal": subject.name}).json()

        def q(**kw):
            return client.get("/march_quotes", params=dict(marshal=subject.name, **kw)).json()["quote"]
        refused = next(d for d in sorted(w.regions)
                       if d != subject.location and not march_quote(w, subject, d)["ok"])
        far = refused
        cc3 = {
            "subject": subject.name,
            "subject_location": subject.location,
            "reach": reach,
            "dest": dest,
            "dest_quote": q(dest=dest),
            "drag_dest": dest,
            "drag_quote": q(dest=dest),
            "refused_dest": refused,
            "refused_quote": q(dest=refused),
            "far_dest": far,
        }
        foes = [e for e in w.get_visible_enemies(w.player_nation)
                if w.is_at_war(w.player_nation, e.nation) and int(e.strength) > 0
                and e.name in (gs.get("enemies") or {})]
        if foes:
            cc3.update(enemy=foes[0].name, enemy_location=foes[0].location,
                       enemy_quote=q(enemy=foes[0].name))
        ally = next(m for m in _field(w) if m.name != subject.name)
        cc3.update(ally=ally.name, ally_location=ally.location, ally_quote=q(ally=ally.name))
    spec["cc3"] = cc3
    return spec


@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    exe = C.engine()
    if exe is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    with pytest.MonkeyPatch.context() as mp:
        C.board_env(mp)
        spec = _cc3_board(TestClient(M.app))
    work = tmp_path_factory.mktemp("cc3")
    out = work / "out.json"
    log = work / "godot.log"
    spec_path = work / "spec.json"
    spec_path.write_text(json.dumps(dict(spec, out=str(out))), encoding="utf-8")
    env = dict(os.environ, CC_SPEC=str(spec_path))
    proc = subprocess.run(
        [exe, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    # UXR3-83 (S15, October 26, 2026): a chip label binds its spaces (U+00A0)
    # in the bbcode; this door reads them as spaces, as the instruments do.
    result = json.loads(out.read_text(encoding="utf-8").replace("\u00a0", " "))
    assert "error" not in result, result.get("error")
    text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["script_errors"] = text.count("SCRIPT ERROR")
    result["script_error_lines"] = [ln for ln in text.splitlines() if "SCRIPT ERROR" in ln][:5]
    result["spec"] = spec
    return result


def _cc3(driven):
    return driven["spec"]["cc3"]


class TestTheHarnessRanClean:

    def test_no_script_errors(self, driven):
        assert driven["script_errors"] == 0, driven["script_error_lines"]

    def test_the_drag_reached_the_map(self, driven):
        """Sensitive: the pushed press landed on his piece, uncovered."""
        assert driven["d_piece_uncovered"] is True
        assert driven["d_hovered_piece"] == _cc3(driven)["subject"]


class TestTheSelection:

    def test_a_click_on_a_piece_of_ours_on_an_empty_line_selects_him(self, driven):
        cc3 = _cc3(driven)
        assert driven["k1_selected"] == cc3["subject"]
        assert driven["k1_panel_open"] is False
        assert driven["k1_ring"] is True
        assert driven["k1_reach_asked"] == ["march_reach:" + cc3["subject"]]

    def test_the_strip_says_what_each_click_does(self, driven):
        shown = humanize_entity_name(_cc3(driven)["subject"])
        assert driven["k1_strip_loading"].startswith(
            f"{shown} selected — click a province: march · an enemy: attack · "
            "a marshal: support · Esc cancels")
        assert "Reading his roads" in driven["k1_strip_loading"]
        n = len(_cc3(driven)["reach"]["reach"])
        assert f"{n} provinces on his roads" in driven["k1_strip"]
        for band in ("this turn", "1 turn", "2–3 turns", "4+ turns"):
            assert band in driven["k1_strip"], band

    def test_the_reach_is_tinted_by_its_eta_band(self, driven):
        cc3 = _cc3(driven)
        assert driven["k1_tint_before"] is False      # nothing dimmed before it is known
        assert driven["k1_tint"] is True
        assert driven["k1_band_count"] == len(cc3["reach"]["reach"])
        turns = cc3["reach"]["reach"][cc3["dest"]]["turns"]
        assert driven["k1_band_dest"] == (0 if turns <= 0 else 1 if turns == 1 else 2 if turns <= 3 else 3)
        assert driven["k1_band_far"] == -1            # out of reach: no band

    def test_the_panel_stays_shut_while_he_is_selected(self, driven):
        assert driven["k12_panel_first"] is True      # sensitive: the click opens it with none
        assert driven["k12_panel_after_select"] is False
        assert driven["k12_panel_after_click"] is False
        assert driven["k12_card_after_click"] is True


class TestTheGhostRoad:

    def test_the_cursor_draws_the_reachs_road_at_once(self, driven):
        cc3 = _cc3(driven)
        road = cc3["reach"]["reach"][cc3["dest"]]["road"]
        assert driven["k2_ghost_points"] == len(road) + 1   # his feet, then the road
        assert driven["k2_ghost_label"].endswith(f"· {cc3['reach']['ap']} AP")

    def test_at_rest_the_exact_quote_is_fetched_once(self, driven):
        cc3 = _cc3(driven)
        assert driven["k2_quote_asked"] == [f"order_quote:{cc3['subject']}|dest|{cc3['dest']}"]
        q = cc3["dest_quote"]
        assert driven["k2_ghost_label_exact"].endswith(f"· {q['ap']} AP")
        assert driven["k2_ghost_kind"] == q["kind"]


class TestTheCard:

    def test_a_click_opens_the_card_on_the_quotes_command(self, driven):
        cc3 = _cc3(driven)
        assert driven["k3_card_open"] is True and driven["k3_modal"] is True
        assert driven["k3_card_command"] == cc3["dest_quote"]["command"]
        assert driven["k3_panel_open"] is False
        assert driven["k3_asked_again"] == []         # the quote in hand is kept

    def test_enter_sends_exactly_the_cards_command(self, driven):
        cc3 = _cc3(driven)
        assert driven["k4_sent"] == ["send:" + cc3["dest_quote"]["command"]]
        assert driven["k4_card_open"] is False
        assert driven["k4_history_last"] == cc3["dest_quote"]["command"]

    def test_enter_never_reaches_the_line_or_ends_the_turn(self, driven):
        assert "send:end turn" not in driven["k4_sent"]
        assert driven["k4_latch"] is False            # the send retired the armed end turn
        assert driven["k4_line"] == ""

    def test_a_send_lets_the_selection_go(self, driven):
        assert driven["k4_selected"] == ""
        assert driven["k4_ring"] is False and driven["k4_tint"] is False

    def test_esc_on_the_card_returns_to_the_selection(self, driven):
        assert driven["k5_card_open"] is False
        assert driven["k5_sends"] == []
        assert driven["k5_selected_after_card_esc"] == _cc3(driven)["subject"]

    def test_the_next_esc_lets_him_go_from_the_line_and_from_the_map(self, driven):
        assert driven["k5_selected_after_line_esc"] == ""
        assert driven["k5_selected_after_map_esc"] == ""
        assert driven["k5_pause_open"] is False       # the ladder took ONE step

    def test_under_the_card_every_key_is_the_cards(self, driven):
        assert driven["k5b_sends"] == []              # a bare E ended no turn
        assert driven["k5b_card_open"] is True

    def test_put_in_line_writes_the_command_and_sends_nothing(self, driven):
        cc3 = _cc3(driven)
        assert driven["k6_line"] == cc3["dest_quote"]["command"]
        assert driven["k6_sends"] == []
        assert driven["k6_selected"] == "" and driven["k6_card_open"] is False

    def test_an_enemy_is_the_attack_quote(self, driven):
        cc3 = _cc3(driven)
        if "enemy" not in cc3:
            pytest.fail("the boot board sights no enemy at war for the attack arm")
        assert driven["k7_asked"] == [f"order_quote:{cc3['subject']}|enemy|{cc3['enemy']}"]
        assert driven["k7_card_command"] == cc3["enemy_quote"]["command"]
        assert cc3["enemy_quote"]["kind"] in ("attack", "march_attack")

    def test_an_enemys_fog_chip_is_the_attack_quote(self, driven):
        """CC-X11 (found by the Mode C walk): partial sight names the corps on
        his fog chip, and the panel's ATTACK row offers him — a click on the
        chip with a corps selected was read as a march to his province."""
        cc3 = _cc3(driven)
        assert driven["k7b_asked"] == [f"order_quote:{cc3['subject']}|enemy|{cc3['enemy']}"]
        assert driven["k7b_card_command"] == cc3["enemy_quote"]["command"]
        # The control arm: the province clicked off the chip is a march there.
        assert driven["k7c_asked"] == [f"order_quote:{cc3['subject']}|dest|{cc3['enemy_location']}"]

    def test_a_corps_of_ours_is_the_support_quote(self, driven):
        cc3 = _cc3(driven)
        assert driven["k8_asked"] == [f"order_quote:{cc3['subject']}|ally|{cc3['ally']}"]
        assert driven["k8_card_command"] == cc3["ally_quote"]["command"]
        assert cc3["ally_quote"]["kind"] == "support"

    def test_a_refused_order_says_why_and_cannot_be_sent(self, driven):
        cc3 = _cc3(driven)
        assert cc3["refused_quote"]["ok"] is False
        assert driven["k8b_sendable"] is False
        assert cc3["refused_quote"]["refusal"] in driven["k8b_terms"]
        assert driven["k8b_sends"] == []
        assert driven["k8b_card_open"] is False       # its Enter only closed the card
        assert driven["k8b_selected"] == cc3["subject"]


class TestTheClearingRules:

    def test_nothing_acts_while_a_command_is_on_the_wire(self, driven):
        assert driven["k9_card_open"] is False and driven["k9_asked"] == []

    def test_a_draft_owns_the_clicks(self, driven):
        assert driven["k10_selected_with_draft"] == ""
        assert driven["k10_panel_with_draft"] is True
        assert driven["k10_selected_after_typing"] == ""

    def test_a_line_filled_by_code_owns_the_clicks_too(self, driven):
        """CC-X12 (CC-3's sweep): a suggestion taken or the history walked
        writes the line with no text_changed — the click must still be CC-1's
        pen (the province written where the caret waits), not a card."""
        cc3 = _cc3(driven)
        assert driven["k10b_selected"] == ""
        assert driven["k10b_card_open"] is False and driven["k10b_asked"] == []
        assert driven["k10b_line"].endswith(", march to " + cc3["dest"])

    @pytest.mark.parametrize("rule", ["right_click", "click_him_again", "screen", "modal",
                                      "end_turn", "missing_from_board", "world_swap"])
    def test_the_selection_is_let_go(self, driven, rule):
        assert driven["k11_rules"][rule] == "", rule

    def test_a_new_board_with_him_standing_reads_his_roads_again(self, driven):
        rules = driven["k11_rules"]
        assert rules["standing_on_new_board"] == _cc3(driven)["subject"]
        assert rules["reach_asked_again"] == 1


class TestTheDrag:

    def test_a_press_waits_and_eight_pixels_make_a_drag(self, driven):
        cc3 = _cc3(driven)
        assert driven["d1_pending"] is True
        assert driven["d1_selected_on_press"] == ""
        assert driven["d1_dragging_at_5"] is False
        assert driven["d1_dragging_at_9"] is True
        assert driven["d1_selected"] == cc3["subject"]
        assert driven["d1_reach_asked"] == ["march_reach:" + cc3["subject"]]

    def test_the_ghost_follows_to_the_drop(self, driven):
        cc3 = _cc3(driven)
        road = cc3["reach"]["reach"][cc3["drag_dest"]]["road"]
        assert driven["d1_ghost_points"] == len(road) + 1
        assert driven["d1_ghost_kind"] == "march"

    def test_the_drop_opens_the_card_on_that_provinces_quote(self, driven):
        cc3 = _cc3(driven)
        assert driven["d1_asked"] == [f"order_quote:{cc3['subject']}|dest|{cc3['drag_dest']}"]
        assert driven["d1_card_open"] is True
        assert driven["d1_card_command"] == cc3["drag_quote"]["command"]
        assert driven["d1_selected_after_card_esc"] == cc3["subject"]

    def test_the_card_stands_clear_of_the_road_it_confirms(self, driven):
        """Found by the Mode C walk: centred, the card hid the very road it
        asked the player to confirm. It takes the centre, the top, the bottom
        or a side — wherever it covers least of the road and the strip."""
        assert driven["d1_road_rect"][2] > 0, "no road was drawn to stand clear of"
        assert driven["d1_card_covers_road"] is False, (driven["d1_card_rect"], driven["d1_road_rect"])
        assert driven["d1_card_on_screen"] is True

    def test_a_drop_on_open_water_lets_it_go(self, driven):
        assert driven["d_water"][0] >= 0, "no open water on screen to drop on"
        assert driven["d2_selected"] == ""
        assert driven["d2_card_open"] is False and driven["d2_dragging"] is False

    def test_esc_mid_drag_lets_it_go_and_goes_no_further(self, driven):
        assert driven["d3_dragging"] is True
        assert driven["d3_dragging_after"] is False
        assert driven["d3_selected"] == ""
        assert driven["d3_pause_open"] is False
        assert driven["d3_card_open"] is False

    def test_a_press_released_where_it_stands_is_the_click(self, driven):
        assert driven["d4_selected"] == _cc3(driven)["subject"]

    def test_a_draft_keeps_the_piece_a_pen(self, driven):
        shown = humanize_entity_name(_cc3(driven)["subject"])
        assert driven["d5_pending"] is False
        assert driven["d5_line"].endswith(", march to " + shown)
        assert driven["d5_selected"] == ""


class TestTheRestoredTerminal:

    def test_a_terminal_restored_after_orders_stands_on_its_newest_line(self, driven):
        """CC-X13 (found by the Mode C walk): the replies to orders given with
        the terminal minimized were written into a log whose hidden scroll
        never measured them — restored, it showed old scrollback."""
        assert driven["x13_end"] > 0, "the log never overflowed its view"
        assert driven["x13_at_end"] is True, (driven["x13_scroll"], driven["x13_end"])


class TestTheDrivenBoard:

    def test_the_driven_enemy_is_one_we_see(self, client):
        """The harness's attack arm clicks a corps the player SEES — the
        route refuses the unseen (pinned above)."""
        spec = _cc3_board(client)
        w = M.world
        seen = {e.name for e in w.get_visible_enemies(w.player_nation)}
        assert "enemy" in spec["cc3"], "the boot board sights no enemy at war"
        assert spec["cc3"]["enemy"] in seen
        assert re.fullmatch(r"[A-Za-z]+", spec["cc3"]["subject"])
