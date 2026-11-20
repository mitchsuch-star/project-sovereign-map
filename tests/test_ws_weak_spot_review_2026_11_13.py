"""The weak-spot review (November 13, 2026) — the user's "review the code for
weak spots and fix them", read beside Session UI-6's staged commit by six
read-only readers and confirmed by hand before a line was changed. The rows:
`docs/BUG_FIXES.md` §WS.

Fixed here, each with its behaviour test:

  WS-1  the door is this machine's — a request carrying a foreign Origin, or
        addressed to a foreign Host, is refused (403) before any route; CORS
        is granted to pages served here only (it was `*`).
  WS-2  a field on peace soil, the commander OUT of sight — the one unseen
        answer (it said he "serves" the SOIL's court, and so told the soil).
  WS-3  guns never rally a corps (the bombardment's morale floor lifted a
        beaten corps up to the forced-retreat threshold).
  WS-4  the autosave's slot is the autosave's (a manual save could take its
        file; the delete guard read one spelling; the write was not synced).
  WS-5  the objection's folded notes are THIS objection's (stale hovers).
  WS-6  a quote holds the lock a POST holds (the readback and the click
        quotes stamp the board and the dice, and put them back).
  WS-7  an option digit is a decimal digit (a typed superscript raised).
  WS-8  a storming corps loses no more men than it brought.
  WS-9  a pinned Generals screen stays open when a chip is double-clicked.

Filed OPEN, heading Session H (S15): WS-10 … WS-15 and WS-R — strict-xfail
pins that turn red the day the behaviour lands, so the row closes with it.
(WS-11 landed November 14, 2026 with row BA's first session; its pin passes.
WS-12 and WS-14 landed November 20, 2026 with row IC's Session 2 — IC-8; their
pins pass, and their behaviour is `tests/test_ic8_the_line.py`.)
"""
from __future__ import annotations

import errno
import inspect
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import save_manager
from backend.commands import combat_executor as ce
from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"

_OPEN_S15 = ("OPEN — heads Session H (S15) by rule 10's sibling sweep "
             "(BUG_FIXES.md §WS); this pin turns red the day the behaviour lands")
# WS-12 and WS-14 moved November 20, 2026 from Session H's head to row IC's IC-8 (the review of
# "on his own": the read-back of typed tasks depends on them — INDEPENDENT_COMMAND_SPEC.md §8.7)
# and were FIXED there the same day (row IC, Session 2): their strict-xfail pins turned red the day
# the behaviour landed, as they said they would, and are re-seated below as passes. The behaviour
# tests are `tests/test_ic8_the_line.py` (`TestWS12…`, `TestGRD33…`, `TestWS14…`).


def _gd(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(src: str, name: str) -> str:
    """One GDScript function, from its `func` line to the next top-level func."""
    m = re.search(r"(?m)^(?:static )?func %s\(" % re.escape(name), src)
    assert m, f"func {name} is gone"
    rest = src[m.end():]
    nxt = re.search(r"(?m)^(?:static )?func ", rest)
    return src[m.start():m.end() + (nxt.start() if nxt else len(rest))]


@pytest.fixture(scope="module")
def client():
    # ONE portal for the module (a bare TestClient opens a loop and a socket
    # pair per request).
    with TestClient(M.app) as c:
        yield c


def _lock_held() -> bool:
    return any(lock.locked() for lock in list(M._state_locks.values()))


# ═══════════════════════════════════════════════════════════════════════════
# WS-1 — the door is this machine's
# ═══════════════════════════════════════════════════════════════════════════

FOREIGN_ORIGINS = ["https://evil.example", "http://evil.example:8005", "null", "",
                   "chrome-extension://abcdef", "http://127.0.0.1.evil.example",
                   "http://localhost.evil.example:8005", "ftp://127.0.0.1"]
LOCAL_ORIGINS = ["http://127.0.0.1:8005", "http://localhost:8006", "http://[::1]:8005",
                 "http://127.0.0.1", "https://localhost:3000"]


class TestWS1TheDoorIsThisMachines:

    def test_the_game_itself_is_answered(self, client):
        # the Godot client, curl and the playtest driver send no Origin at all
        assert client.get("/saves").status_code == 200

    @pytest.mark.parametrize("origin", LOCAL_ORIGINS)
    def test_a_page_served_here_is_answered_with_cors(self, client, origin):
        r = client.get("/saves", headers={"Origin": origin})
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == origin

    @pytest.mark.parametrize("origin", FOREIGN_ORIGINS)
    def test_a_foreign_page_is_refused_before_any_route(self, client, origin):
        for method, path in (("GET", "/saves"), ("GET", "/parse_preview"),
                             ("POST", "/new_game"), ("POST", "/delete_save"),
                             ("POST", "/command"), ("OPTIONS", "/command")):
            r = client.request(method, path, headers={"Origin": origin})
            assert r.status_code == 403, (method, path, origin)
            assert r.json() == {"success": False, "message": M.FOREIGN_CALLER_MESSAGE}
            assert "access-control-allow-origin" not in r.headers

    def test_a_refused_post_changes_nothing_and_takes_no_lock(self, client):
        world, epoch = M.world, M._STATE_EPOCH
        r = client.post("/new_game", json={}, headers={"Origin": "https://evil.example"})
        assert r.status_code == 403
        assert M.world is world and M._STATE_EPOCH == epoch
        assert M._posts_in_flight() is False

    def test_a_local_preflight_is_granted(self, client):
        r = client.options("/command", headers={
            "Origin": "http://127.0.0.1:8005",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"})
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == "http://127.0.0.1:8005"

    @pytest.mark.parametrize("host", ["evil.example:8005", "evil.example", "10.0.0.5:8005",
                                      "127.0.0.1.evil.example:8005"])
    def test_a_request_addressed_elsewhere_is_refused(self, client, host):
        # a DNS-rebinding page reaches 127.0.0.1 under ITS OWN name
        assert client.get("/saves", headers={"Host": host}).status_code == 403

    @pytest.mark.parametrize("host", ["127.0.0.1:8005", "localhost:8005", "[::1]:8005",
                                      "LOCALHOST:8006", "127.0.0.1"])
    def test_a_request_addressed_here_is_answered(self, client, host):
        assert client.get("/saves", headers={"Host": host}).status_code == 200

    def test_the_guard_is_the_outermost_door(self):
        # registered LAST, so it runs FIRST — before the state lock
        first = M.app.user_middleware[0]
        options = getattr(first, "kwargs", None) or getattr(first, "options", {})
        assert options.get("dispatch") is M.refuse_foreign_callers

    def test_no_wildcard_origin_is_left(self):
        src = inspect.getsource(M)
        assert 'allow_origins=["*"]' not in src
        assert "allow_origin_regex=_LOCAL_ORIGIN_PATTERN" in src


# ═══════════════════════════════════════════════════════════════════════════
# WS-2 — a field on peace soil, the commander out of sight
# ═══════════════════════════════════════════════════════════════════════════

class TestWS2AnUnseenManOnPeaceSoil:

    @staticmethod
    def _pair():
        ours = SimpleNamespace(name="Murat", nation="France", location="Bavaria")
        his = SimpleNamespace(name="Kutuzov", nation="Russia", location="Silesia",
                              captured_by="")
        return ours, his, SimpleNamespace(player_nation="France")

    def test_out_of_sight_on_his_own_courts_soil_he_is_named_by_his_court(self, monkeypatch):
        # UI6-X35's own case, kept: his court is public, the ground is not
        from backend.game_logic import intel_surfaces
        monkeypatch.setattr(intel_surfaces, "in_sight", lambda world, viewer, man: False)
        ours, his, world = self._pair()
        said = ce.peace_soil_refusal(ours, his, {"owner": "Russia"}, world)
        assert said["message"] == (
            "Murat cannot march on Kutuzov: Kutuzov serves Russia, and we are at peace "
            "with Russia — no corps of ours may take the field against him.")
        assert "Silesia" not in said["message"]

    def test_no_real_road_hands_it_his_own_courts_soil(self):
        # ...which is why the words were false on every road that reaches them:
        # the guard returns no block for a man standing on his own court's soil
        src = inspect.getsource(ce.field_on_peace_soil)
        assert 'if enemy_nation and block.get("owner") == enemy_nation:' in src
        for caller in (ce.charge_on_peace_soil,):
            assert "enemy_nation=enemy_marshal.nation" in inspect.getsource(caller)

    def test_out_of_sight_on_a_third_courts_soil_he_gets_the_one_unseen_answer(self, monkeypatch):
        from backend.game_logic import intel_surfaces
        monkeypatch.setattr(intel_surfaces, "in_sight", lambda world, viewer, man: False)
        ours, his, world = self._pair()
        said = ce.peace_soil_refusal(ours, his, {"owner": "Prussia"}, world)
        # the words the pursuit and every other battle order on him answer
        assert said == ce.unseen_target_refusal(world, his, "Murat")
        assert said["message"] == ("No intelligence on Kutuzov's position, Sire. "
                                   "Scout for him before Murat can give chase.")
        # nothing of the ground he stands on, nor of the court that owns it —
        # and never the false "serves <the soil's court>"
        for told in ("Prussia", "Silesia", "serves", "peace", "soil"):
            assert told not in said["message"], told
        assert said["success"] is False and said["variable_action_cost"] == 0
        assert "peace_soil" not in said

    def test_in_sight_the_refusal_names_the_soil_as_before(self, monkeypatch):
        from backend.game_logic import intel_surfaces
        monkeypatch.setattr(intel_surfaces, "in_sight", lambda world, viewer, man: True)
        ours, his, world = self._pair()
        said = ce.peace_soil_refusal(ours, his, {"owner": "Prussia"}, world)
        assert said["message"] == (
            "Murat cannot march on Kutuzov: Silesia is Prussia's soil, and we are at "
            "peace with Prussia — no corps of ours may take the field there.")
        assert said["peace_soil"] == "Prussia" and said["success"] is False

    def test_with_no_board_in_hand_the_words_are_the_seen_ones(self):
        ours, his, _world = self._pair()
        said = ce.peace_soil_refusal(ours, his, {"owner": "Prussia"})
        assert "Silesia is Prussia's soil" in said["message"]


# ═══════════════════════════════════════════════════════════════════════════
# WS-3 — guns never rally a corps
# ═══════════════════════════════════════════════════════════════════════════

def _guns_on(morale: int, square: bool = False):
    world = WorldFactory.basic()
    art = MarshalFactory.artillery(name="TestArt", location="Belgium", strength=25000)
    world.marshals["TestArt"] = art
    for m in world.marshals.values():
        if m.location == "Waterloo" and m.nation != "France" and m.name != "Wellington":
            m.location = "Vienna"
    target = world.marshals["Wellington"]
    target.location, target.strength, target.morale = "Waterloo", 68000, morale
    target.square_formation = square
    return world, art, target, CommandExecutor()


class TestWS3GunsNeverRallyACorps:

    @pytest.mark.parametrize("before, after, stands", [
        (60, 57, 57),     # a steady corps is shaken, as ever
        (26, 23, 25),     # the floor: guns alone never break a corps
        (40, 22, 25),     # a square under shells (-18) stops at the floor
        (25, 22, 25),
        (12, 9, 12),      # THE DEFECT: this read 25 — a beaten corps shelled UP
        (12, -6, 12),
        (0, 0, 0),
    ])
    def test_the_floor_never_lifts(self, before, after, stands):
        assert ce.shelled_morale(before, after) == stands

    @pytest.mark.parametrize("morale", [12, 5, 24])
    def test_a_beaten_corps_is_not_shelled_up_to_the_threshold(self, morale):
        world, art, target, executor = _guns_on(morale)
        result = executor._execute_bombardment(art, target, world, {"world": world})
        assert result.get("success") is not False, result.get("message")
        assert target.morale == morale, "a bombardment lifted a beaten corps' morale"

    def test_a_steady_corps_still_loses_three(self):
        world, art, target, executor = _guns_on(60)
        executor._execute_bombardment(art, target, world, {"world": world})
        assert target.morale == 57

    def test_a_shaken_corps_still_stops_at_the_floor(self):
        world, art, target, executor = _guns_on(26)
        executor._execute_bombardment(art, target, world, {"world": world})
        assert target.morale == ce.FORCED_RETREAT_THRESHOLD

    def test_both_floors_read_the_one_rule(self):
        src = inspect.getsource(CombatExecutor._execute_bombardment)
        assert src.count("shelled_morale(") == 2      # the target, the collateral
        assert "morale = FORCED_RETREAT_THRESHOLD" not in src


# ═══════════════════════════════════════════════════════════════════════════
# WS-4 — the autosave's slot is the autosave's
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def saves(tmp_path, monkeypatch):
    folder = tmp_path / "saves"
    folder.mkdir()
    monkeypatch.setattr(save_manager, "SAVE_DIR", folder)
    return folder


@pytest.fixture
def world():
    return WorldState(player_nation="France")


class TestWS4TheAutosavesSlot:

    @pytest.mark.parametrize("name", ["autosave", "Autosave", "AUTOSAVE", " autosave ", "AutoSave  "])
    def test_a_manual_save_may_not_take_the_slot(self, saves, world, name):
        save_manager.autosave(world)
        slot = saves / save_manager.AUTOSAVE_FILENAME
        before = slot.read_bytes()
        result = save_manager.save_game(world, save_name=name)
        assert result["success"] is False
        assert result["message"] == ("Save failed — that name belongs to the autosave. "
                                     "Choose another.")
        assert slot.read_bytes() == before
        assert sorted(p.name for p in saves.iterdir()) == [save_manager.AUTOSAVE_FILENAME]

    def test_the_typed_save_is_refused_the_same(self, saves, world):
        result = CommandExecutor().execute(
            {"success": True, "raw_command": "save autosave",
             "command": {"action": "meta_command", "raw_command": "save autosave"}},
            {"world": world})
        assert result["success"] is False
        assert "belongs to the autosave" in result["message"]
        assert list(saves.iterdir()) == []

    @pytest.mark.parametrize("name", ["", "   "])
    def test_a_name_that_leaves_no_file_stem_is_refused(self, saves, world, name):
        result = save_manager.save_game(world, save_name=name)
        assert result["success"] is False
        assert result["message"] == "Save failed — name the save first."
        assert list(saves.iterdir()) == []

    def test_every_other_name_still_saves_and_the_autosave_door_is_untouched(self, saves, world):
        assert save_manager.save_game(world, save_name="Before Vienna")["success"] is True
        assert save_manager.save_game(world, save_name="autosave 2")["success"] is True
        assert save_manager.autosave(world)["success"] is True
        assert sorted(p.name for p in saves.iterdir()) == [
            "Before Vienna.json", "autosave 2.json", save_manager.AUTOSAVE_FILENAME]

    @pytest.mark.parametrize("spelling", ["Autosave.json", "AUTOSAVE.JSON", "autosave.json.",
                                          "autosave.json "])
    def test_the_slot_is_not_deleted_by_another_spelling(self, saves, world, spelling):
        save_manager.autosave(world)
        slot = saves / save_manager.AUTOSAVE_FILENAME
        result = save_manager.delete_save(saves / spelling)
        assert result["success"] is False
        assert "Cannot delete autosave" in result["message"]
        assert slot.exists()

    def test_a_named_save_is_still_deleted(self, saves, world):
        save_manager.save_game(world, save_name="Delete Me")
        target = saves / "Delete Me.json"
        assert target.exists()
        assert save_manager.delete_save(target)["success"] is True
        assert not target.exists()

    def test_the_bytes_reach_the_disk_before_the_rename(self, saves, world, monkeypatch):
        order = []
        real_sync, real_replace = save_manager.os.fsync, save_manager.os.replace

        def sync(fd):
            order.append("sync")
            return real_sync(fd)

        def replace(src, dst):
            order.append("replace")
            return real_replace(src, dst)
        monkeypatch.setattr(save_manager.os, "fsync", sync)
        monkeypatch.setattr(save_manager.os, "replace", replace)
        assert save_manager.save_game(world, save_name="Synced")["success"] is True
        assert order == ["sync", "replace"]

    def test_a_file_system_that_refuses_the_sync_still_saves(self, saves, world, monkeypatch):
        def refuse(fd):
            raise OSError(errno.EINVAL, "this file system has no sync")
        monkeypatch.setattr(save_manager.os, "fsync", refuse)
        result = save_manager.save_game(world, save_name="Unsynced")
        assert result["success"] is True
        assert (saves / "Unsynced.json").exists()
        assert not (saves / "Unsynced.tmp").exists()


# ═══════════════════════════════════════════════════════════════════════════
# WS-5 — the objection's folded notes are this objection's (the client)
# ═══════════════════════════════════════════════════════════════════════════

class TestWS5TheObjectionsNotesAreThisObjections:

    def test_the_three_answers_are_cleared_before_any_is_set(self):
        show = _func(_gd("objection_dialog.gd"), "show_objection")
        clear = show.index("_answer.tooltip_text = \"\"")
        assert "for _answer in [trust_button, insist_button, compromise_button]:" in show
        for button in ("trust_button", "insist_button", "compromise_button"):
            first_set = show.index("%s.tooltip_text = str(" % button)
            assert clear < first_set, button


# ═══════════════════════════════════════════════════════════════════════════
# WS-6 — a quote holds the lock a POST holds
# ═══════════════════════════════════════════════════════════════════════════

class TestWS6AQuoteHoldsTheLock:

    def test_the_two_readings_that_stamp_the_board_are_named(self):
        # Row BA (BA-3) added `/battle_day`: its chips are quoted with the
        # word's lend on the pool, stamped and put back — WS-6's own class.
        # Row IC, directives (Nov 19, 2026) added `/directive_quote`: the list of an order to several
        # corps is each man's read-back reading, made under the read-back's own lock — WS-6's class.
        assert M._LOCKED_READS == frozenset({"/parse_preview", "/march_quotes", "/battle_day",
                                             "/directive_quote"})
        src = inspect.getsource(M.serialize_state_mutations)
        assert "request.url.path in _LOCKED_READS" in src
        assert src.count("async with get_state_lock()") == 2

    def test_the_readback_reads_under_the_lock_and_is_no_post(self, client, monkeypatch):
        from backend.commands import parse_preview as pp
        seen = {}

        def reading(world, line, **kwargs):
            seen["held"] = _lock_held()
            seen["post"] = kwargs["posts_in_flight"]()
            return {"success": True, "kind": "none", "line": line, "parts": [],
                    "candidates": [], "epoch": 0}
        monkeypatch.setattr(pp, "preview", reading)
        r = client.get("/parse_preview", params={"line": "Ney, attack Mack"})
        assert r.status_code == 200
        assert seen == {"held": True, "post": False}
        assert not _lock_held()

    def test_the_click_quotes_read_under_the_lock(self, client, monkeypatch):
        from backend.commands import order_quotes
        seen = {}

        def quotes(world, region):
            seen["held"] = _lock_held()
            return {"success": True, "region": region, "quotes": []}
        monkeypatch.setattr(order_quotes, "march_quotes_for_region", quotes)
        region = next(iter(M.world.regions))
        r = client.get("/march_quotes", params={"region": region})
        assert r.status_code == 200
        assert seen == {"held": True}

    def test_a_post_is_in_flight_while_it_runs_and_not_after(self, client, monkeypatch):
        seen = {}

        def save(world, save_name="Quicksave", filepath=None):
            seen["held"] = _lock_held()
            seen["post"] = M._posts_in_flight()
            return {"success": True, "message": "saved", "filepath": ""}
        monkeypatch.setattr(M, "save_game", save)
        epoch = M._STATE_EPOCH
        r = client.post("/save", json={"save_name": "ws6"})
        assert r.status_code == 200
        assert seen == {"held": True, "post": True}
        assert M._posts_in_flight() is False and not _lock_held()
        assert M._STATE_EPOCH == epoch + 1      # a POST still moves the readback's clock

    def test_a_locked_read_does_not_move_the_clock(self, client, monkeypatch):
        from backend.commands import parse_preview as pp
        monkeypatch.setattr(pp, "preview", lambda world, line, **kw: {
            "success": True, "kind": "none", "line": line, "parts": [], "candidates": [],
            "epoch": 0})
        epoch = M._STATE_EPOCH
        assert client.get("/parse_preview", params={"line": "Ney"}).status_code == 200
        assert M._STATE_EPOCH == epoch

    def test_every_other_get_stays_lock_free(self, client, monkeypatch):
        from backend.game_logic import war_status
        seen = {}
        real = war_status.build_active_wars

        def wars(*args, **kwargs):
            seen["held"] = _lock_held()
            return real(*args, **kwargs)
        monkeypatch.setattr(war_status, "build_active_wars", wars)
        assert client.get("/test").status_code == 200
        assert seen == {"held": False}


# ═══════════════════════════════════════════════════════════════════════════
# WS-7 — an option digit is a decimal digit
# ═══════════════════════════════════════════════════════════════════════════

class TestWS7AnOptionDigitIsADecimalDigit:

    @staticmethod
    def _letter_waits():
        return SimpleNamespace(
            dialogue_manager=None, pending_objection=None,
            pending_strategic_objection=None, pending_capture_choice=None,
            pending_diplomatic_dialogue={"options": [{"action": "accept"},
                                                     {"action": "decline"}]},
            get_player_marshals=lambda: [])

    @pytest.mark.parametrize("typed", ["²", "①", "½", "²²"])
    def test_the_readback_reads_a_digit_that_is_no_number_as_no_answer(self, typed):
        from backend.commands import parse_preview as pp
        assert typed.isdigit() or typed == "½"       # what `isdigit` let through
        assert pp._pending_question(self._letter_waits(), typed) is None

    @pytest.mark.parametrize("typed", ["1", "2", "accept", "２"])
    def test_a_real_answer_is_still_an_answer(self, typed):
        from backend.commands import parse_preview as pp
        assert pp._pending_question(self._letter_waits(), typed) == \
            "A letter waits — this line answers it"

    def test_the_command_road_reads_it_the_same(self):
        src = inspect.getsource(M._command_pending_answers)
        assert "_pending_answer_token.isdecimal()" in src
        assert ".isdigit()" not in src


# ═══════════════════════════════════════════════════════════════════════════
# WS-8 — a storming corps loses no more men than it brought
# ═══════════════════════════════════════════════════════════════════════════

class TestWS8AStormingCorpsLosesNoMoreThanItBrought:

    @pytest.mark.parametrize("men", [1, 40, 100, 499])
    def test_a_remnant_under_the_floor(self, men):
        executor = CombatExecutor.__new__(CombatExecutor)
        floor = int(25000 * executor.GARRISON_ASSAULT_LOSS_FLOOR)
        assert floor > men, "the case needs a floor above the remnant"
        lost, _garrison = executor.garrison_exchange(men, men, 25000, 31250)
        assert lost == men

    def test_an_army_above_the_floor_is_unchanged(self):
        executor = CombatExecutor.__new__(CombatExecutor)
        lost, garrison = executor.garrison_exchange(40000, 61000, 25000, 31250)
        assert lost == max(int(40000 * min(0.35, 31250 / 61000 * 0.25)),
                           int(25000 * executor.GARRISON_ASSAULT_LOSS_FLOOR))
        assert garrison == max(int(25000 * min(0.50, 61000 / 31250 * 0.35)), 2500, 1)


# ═══════════════════════════════════════════════════════════════════════════
# WS-9 — a pinned Generals screen stays open (the client)
# ═══════════════════════════════════════════════════════════════════════════

class TestWS9APinnedGeneralsStaysOpen:

    def test_the_pinned_screen_returns_before_the_toggle(self):
        opened = _func(_gd("main.gd"), "_ui6_open_generals")
        pinned = opened.index('if top_bar.get_pinned_screen() == "generals":')
        toggle = opened.index('top_bar.toggle_screen("generals")')
        assert pinned < toggle
        assert opened[pinned:toggle].count("return") == 1
        # the top bar's own rule, which is why the toggle closed it
        toggled = _func(_gd("top_bar.gd"), "toggle_screen")
        assert "if pinned_screen == screen_name:" in toggled and "unpin()" in toggled
        assert "func get_pinned_screen() -> String:" in _gd("top_bar.gd")


# ═══════════════════════════════════════════════════════════════════════════
# The rows filed OPEN (Session H's head) — strict-xfail pins
# ═══════════════════════════════════════════════════════════════════════════

class TestWS10TwoSurfacesClaimTheBareDigits:
    """A ledger pinned at the Side Desk reads the bare digits as its tabs
    ("Keys 1–8 turn the ledger's books", its own lead line) and the selection
    card reads them as its orders (1-7): with the caret off the line the
    ledger wins, with it on the line the card does. UI-6 ruled it for the
    Generals screen (docked, the war room keeps the keys) and not for the two
    ledgers. The user's ruling; this pin reads the war-room-keeps-them answer
    and is rewritten with the row if the ruling is the book's."""

    def test_the_generals_screen_already_stands_aside(self):
        body = _func(_gd("marshal_management.gd"), "_input")
        assert '$PanelContainer.has_meta("side_desk_docked")' in body

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    @pytest.mark.parametrize("script", ["strategic_ledger.gd", "diplomatic_ledger.gd"])
    def test_one_surface_owns_a_bare_digit_while_a_ledger_is_docked(self, script):
        assert "side_desk_docked" in _func(_gd(script), "_input")


class TestWS11ABattleIsRolledAgainByLoading:
    """Every battle draw came off the process-global `random`, which no save
    carries: F5, attack, F9, attack again rolled fresh dice. The courts' own
    decisions were already the campaign seed's (`enemy_ai`, `naval`, the
    fortunes of war); the land battle was not.

    FIXED November 14, 2026 (row BA, BA-1 — the user's "Seed them here,
    first"): in a campaign the game server holds, on a rolled campaign seed,
    the battle draws from its own stream (`campaign_variance.battle_rng`; a
    world a measuring tool builds for itself keeps the stream it pins, and
    `historical` is the fixed table). This pin, filed as a strict xfail,
    turned red the day the dice left the global stream, as it said it would;
    the behaviour tests are `tests/test_ws11_the_dice_are_the_campaigns.py`."""

    def test_the_dice_are_the_campaigns(self):
        from backend.game_logic.combat import CombatResolver
        assert "random.randint(" not in inspect.getsource(CombatResolver.roll_combat_dice)


class TestWS12AModelsNumberMovesAMarshal:
    """Golden Rule 6: in a live-model parse, the `strategic_score` the model
    wrote set morale, trust and a banked attack bonus on the player's marshal
    before the order was dispatched — and a line refused for free kept them.
    FIXED in row IC's Session 2 (IC-8, November 20, 2026; ruled November 17):
    the bonus is retired and the literal marshal's buff reads the fast parser's
    own numbers — behaviour pinned in `tests/test_ic8_the_line.py`."""

    def test_no_number_the_model_wrote_moves_a_marshal(self):
        src = inspect.getsource(CommandExecutor._exec_bonuses_and_clarification)
        assert "apply_strategic_bonuses" not in src


class TestWS13OutnumberedIsReadOnTheTwoLeads:
    """"Outnumbered" compared the two LEAD corps' strengths before the corps
    beside them join: a 4,000-man lead on a 60,000-man stack beat 20,000 men
    "against the odds" (+5 authority, the glory point). FIXED in row BA's
    session BA-6 (November 17, 2026): the odds read the men each side put on
    the field — behaviour pinned in tests/test_ba6_the_weak_spots.py."""

    def test_outnumbered_is_read_on_the_field(self):
        src = inspect.getsource(CombatExecutor._post_combat_pipeline)
        assert "outnumbered = pre_atk < pre_def" not in src


class TestWS14TheReadbackOverclaimsAStandingQuestion:
    """While Berthier's clarification stood, the readback called EVERY line
    "this line answers it"; `/command` passes a line that is no answer on to
    the ordinary road and carries it out. FIXED in row IC's Session 2 (IC-8,
    November 20, 2026): the readback asks `/command`'s own readers — behaviour
    pinned in `tests/test_ic8_the_line.py`."""

    def test_a_fresh_order_is_not_called_an_answer(self):
        from backend.commands import parse_preview as pp
        from backend.commands.clarification import CLARIFICATION_DIALOGUE_TYPE
        desk = SimpleNamespace(peek=lambda: {"type": CLARIFICATION_DIALOGUE_TYPE},
                               is_hard_stop=lambda: False)
        board = SimpleNamespace(
            dialogue_manager=desk, pending_objection=None,
            pending_strategic_objection=None, pending_capture_choice=None,
            pending_diplomatic_dialogue=None, get_player_marshals=lambda: [])
        assert pp._pending_question(board, "Davout, attack Mack") is None


class TestWS15ARefusedAttackCancelsADrill:
    """The attack road's first stage cancelled a first-turn drill (and spent
    the counter-punch, which only the typed road gave back) BEFORE the stages
    that can refuse the order for free. FIXED in row BA's session BA-6
    (November 17, 2026) by the row's second form: an attack that struck no
    blow puts back what the first stage spent — the drill, the counter-punch,
    a square — for every caller (the driver of `_execute_attack`); behaviour
    pinned in tests/test_ba6_the_weak_spots.py."""

    def test_the_drill_is_put_back_for_every_caller_when_no_blow_lands(self):
        # the one door of every road is wrapped (a decorator: the driver stays
        # a driver, CODE-2a)
        src = inspect.getsource(CombatExecutor._execute_attack)
        assert src.lstrip().startswith("@_gives_back_what_no_blow_spent")
        assert CombatExecutor._execute_attack.__wrapped__ is not None


class TestWSRTheReviewsUnconfirmedFinds:
    """The finds the readers reported and the lead did not confirm in the code
    (BUG_FIXES.md §WS lists them): each is confirmed — then fixed, or filed
    under its own id — or refuted, at Session H's head."""

    @pytest.mark.xfail(strict=True, reason=_OPEN_S15)
    def test_every_find_is_confirmed_or_refuted(self):
        sys.path.insert(0, str(REPO))
        from tools import defect_census as census
        assert census.collect()["WS-R"]["state"] == "closed"
