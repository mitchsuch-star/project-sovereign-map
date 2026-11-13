"""Session UI-5, P11 "Backend": the attack card's force bar, the war row's side,
the first-open reset route and the end turn's autosave receipt."""
import contextlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.order_quotes import attack_quote
from backend.game_logic import first_open
from backend.models.intel import FULL
from tests import _chip_census as C

SCENARIO = (Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _boot():
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_boot.to_dict(), default=str)))


@pytest.fixture
def client(monkeypatch):
    save_dir = Path(tempfile.mkdtemp()) / "saves"
    C.board_env(monkeypatch)
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        yield TestClient(M.app)


FORCE_KEYS = {"ours", "theirs_low", "theirs_high", "theirs_label", "odds"}


# ── 1. the force block ────────────────────────────────────────────────────

class TestForceBlock:
    def test_present_with_ints_on_an_in_reach_attack(self, w):
        ney, mack = w.get_marshal("Ney"), w.get_marshal("Mack")
        q = attack_quote(w, ney, mack)
        assert q["ok"] and q["kind"] == "attack"
        f = q["force"]
        assert set(f) == FORCE_KEYS
        for k in ("ours", "theirs_low", "theirs_high"):
            assert type(f[k]) is int
        assert f["ours"] >= int(ney.strength) and f["theirs_label"]
        assert q == json.loads(json.dumps(q))            # a JSON round trip is identity

    def test_fogged_foe_reads_its_band_never_the_true_figure(self, w):
        ney, mack = w.get_marshal("Ney"), w.get_marshal("Mack")
        assert w.intel["Swabia"].visibility != FULL
        f = attack_quote(w, ney, mack)["force"]
        assert f["theirs_label"] == "large force"
        assert (f["theirs_low"], f["theirs_high"]) == (40000, 69999)
        assert f["theirs_low"] != int(mack.strength) or f["theirs_high"] != int(mack.strength)
        assert f["odds"] == ""                            # a band word would read him back

    def test_full_sight_gives_one_exact_figure_and_the_odds_word(self, w):
        ney, mack = w.get_marshal("Ney"), w.get_marshal("Mack")
        w.intel["Swabia"].visibility = FULL
        f = attack_quote(w, ney, mack)["force"]
        assert f["theirs_low"] == f["theirs_high"] == int(mack.strength)
        assert f["odds"]

    def test_no_intel_is_unknown_zero(self, w):
        ney, mack = w.get_marshal("Ney"), w.get_marshal("Mack")
        w.intel.pop("Swabia", None)
        f = attack_quote(w, ney, mack)["force"]
        assert (f["theirs_low"], f["theirs_high"], f["theirs_label"]) == (0, 0, "strength unknown")

    def test_absent_on_the_march_branch_and_on_a_refusal(self, w):
        far = attack_quote(w, w.get_marshal("Soult"), w.get_marshal("ArchdukeJohn"))
        assert far["kind"] == "march_attack" and "force" not in far
        w.actions_remaining = 0
        refused = attack_quote(w, w.get_marshal("Ney"), w.get_marshal("Mack"))
        assert refused["ok"] is False and "force" not in refused

    def test_a_failure_leaves_the_quote_without_force(self, w, monkeypatch):
        from backend.commands import order_quotes as OQ

        def boom(*a, **k):
            raise RuntimeError("x")
        monkeypatch.setattr(OQ, "_band_range", boom)
        q = attack_quote(w, w.get_marshal("Ney"), w.get_marshal("Mack"))
        assert q["ok"] and "force" not in q


# ── 2. france_side ────────────────────────────────────────────────────────

class TestFranceSide:
    def test_every_war_row_carries_france_side(self, w):
        from backend.game_logic.war_status import build_active_wars
        wars = build_active_wars(w)["wars"]
        assert wars
        for row in wars:
            assert row["france_side"] in ("attackers", "defenders", "")
        instances = w.war_instances or {}
        for row in wars:
            inst = instances.get(row.get("war_instance_id") or "")
            if isinstance(inst, dict) and inst.get("side_by_nation", {}).get(w.player_nation):
                assert row["france_side"] == inst["side_by_nation"][w.player_nation]


# ── 3. the first-open reset ───────────────────────────────────────────────

class TestFirstOpenReset:
    def test_the_route_clears_the_seen_set(self, client):
        world = M.game_state["world"]
        assert first_open.mark_seen(world, "laws") and first_open.mark_seen(world, "cabinet")
        assert first_open.is_seen(world, "laws")
        r = client.post("/first_open/reset").json()
        assert r["success"] is True and r["cleared"] == 2 and r["message"]
        assert world.first_opens == {}
        assert first_open.line_for(world, "laws")         # the line shows again

    def test_reset_unit(self):
        from backend.models.world_state import WorldState
        world = WorldState(player_nation="France")
        first_open.mark_seen(world, "designs")
        assert first_open.reset(world) == 1 and first_open.reset(world) == 0


# ── 5. the autosave receipt ───────────────────────────────────────────────

class TestAutosaveReceipt:
    def test_end_turn_reports_the_autosave(self, client):
        with _quiet():
            r = client.post("/command", json={"command": "end turn"}).json()
        assert r.get("autosaved") is True, r.keys()
        assert isinstance(r["autosave_label"], str) and r["autosave_label"]

    def test_a_failed_save_reads_false_and_still_rides(self, client):
        with _quiet(), patch("backend.save_manager._autosave",
                             return_value={"success": False, "message": "disk"}):
            r = client.post("/command", json={"command": "end turn"}).json()
        assert r.get("autosaved") is False
