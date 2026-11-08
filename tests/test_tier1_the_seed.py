"""Tier 1 — the seed at New Game (`DYNAMISM_SPEC.md` §2 Tier 1; the plan's
S15-R row; November 8, 2026).

The contract: a plain player New Game ROLLS a readable campaign seed
(`roll_campaign_seed()` — adjective-noun-NN, never `historical`) and SHOWS
it (the /new_game reply and its message, the first morning's briefing line,
the save rows the load dialog prints, the menu box prefilled from GET
/test's `suggested_seed`); an explicit seed in the request beats
everything; the SOVEREIGN_SEED env beats the roll — so the suite (conftest
pins the env to `historical`), every harness arm and every live-verify rig
keeps today's boot byte for byte and NEVER rolls; a School lesson
(scenario override) never rolls either — a lesson's beats stay identical
for every player.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import backend.main as M  # noqa: E402
from backend.game_logic.campaign_variance import (  # noqa: E402
    HISTORICAL_SEED,
    is_historical,
    roll_campaign_seed,
)

ROLL_SHAPE = re.compile(r"^[a-z]+-[a-z]+-\d{2}$")


@pytest.fixture()
def client():
    return TestClient(M.app)


# ═══════════════════════════════════════════════════════════════════════
# The roll itself
# ═══════════════════════════════════════════════════════════════════════
class TestTheRoll:
    def test_readable_and_never_historical(self):
        for _ in range(40):
            seed = roll_campaign_seed()
            assert ROLL_SHAPE.match(seed), seed
            assert not is_historical(seed), seed

    def test_the_rolls_vary(self):
        assert len({roll_campaign_seed() for _ in range(20)}) > 1

    def test_the_roll_consumes_no_ambient_random(self):
        """§5 pin 2: the module-RNG streams are pinned by 21 test files —
        the roll draws from `secrets`, never from `random`."""
        random.seed(12345)
        before = random.getstate()
        roll_campaign_seed()
        assert random.getstate() == before


# ═══════════════════════════════════════════════════════════════════════
# The route's precedence
# ═══════════════════════════════════════════════════════════════════════
class TestTheRoute:
    def test_an_explicit_seed_beats_the_env(self, client):
        reply = client.post("/new_game",
                            json={"seed": "violet-danube-07"}).json()
        assert reply["success"] is True
        assert reply["campaign_seed"] == "violet-danube-07"
        assert M.world.campaign_seed == "violet-danube-07"
        assert "the seed is 'violet-danube-07'" in reply["message"]

    def test_the_env_beats_the_roll(self, client):
        """THE SUITE-SAFETY LAW: under the conftest env pin a bare
        /new_game must neither roll nor change its message — every
        existing harness arm and archived digest depends on it."""
        reply = client.post("/new_game", json={}).json()
        assert reply["success"] is True
        assert reply["campaign_seed"] == HISTORICAL_SEED
        assert M.world.campaign_seed == HISTORICAL_SEED
        assert reply["message"].startswith("New campaign started.")
        assert "seed" not in reply["message"]

    def test_a_bare_new_game_rolls_without_the_env(self, client,
                                                   monkeypatch):
        monkeypatch.delenv("SOVEREIGN_SEED", raising=False)
        reply = client.post("/new_game", json={}).json()
        assert reply["success"] is True
        seed = reply["campaign_seed"]
        assert ROLL_SHAPE.match(seed), seed
        assert not is_historical(seed)
        assert M.world.campaign_seed == seed
        assert f"the seed is '{seed}'" in reply["message"]

    def test_a_school_lesson_never_rolls(self, client, monkeypatch):
        """A lesson's beats are identical for every player — the scenario
        override keeps today's resolution even with no env set."""
        monkeypatch.delenv("SOVEREIGN_SEED", raising=False)
        reply = client.post("/new_game",
                            json={"scenario": "tutorial"}).json()
        assert reply["success"] is True
        assert reply["campaign_seed"] == HISTORICAL_SEED

    def test_the_menu_box_gets_a_suggestion(self, client):
        payload = client.get("/test").json()
        assert ROLL_SHAPE.match(str(payload.get("suggested_seed", ""))), \
            payload.get("suggested_seed")


# ═══════════════════════════════════════════════════════════════════════
# Shown: the first morning, the save rows, the load round trip
# ═══════════════════════════════════════════════════════════════════════
class TestTheSeedIsShown:
    def test_the_first_morning_names_the_seed(self, client):
        reply = client.post("/new_game",
                            json={"seed": "iron-eagle-12"}).json()
        situation = (reply.get("morning_dispatch") or {}).get("situation") or {}
        assert situation.get("campaign_seed") == "iron-eagle-12"
        assert "iron-eagle-12" in str(situation.get("campaign_seed_line"))

    def test_a_later_morning_carries_no_seed_line(self, client):
        """Boot only — every later briefing renders exactly as before."""
        from backend.game_logic.dispatch import _build_situation
        client.post("/new_game", json={"seed": "iron-eagle-12"})
        later = _build_situation(M.world, M.world.player_nation, boot=False)
        assert "campaign_seed_line" not in later

    def test_the_save_rows_carry_the_seed(self, client):
        client.post("/new_game", json={"seed": "pale-courier-33"})
        rows = client.get("/saves").json().get("saves") or []
        autosaves = [r for r in rows
                     if r.get("filename", "").startswith("autosave")]
        assert autosaves, rows
        assert autosaves[0]["metadata"]["campaign_seed"] == "pale-courier-33"

    def test_the_seed_survives_the_load(self, client):
        client.post("/new_game", json={"seed": "pale-courier-33"})
        rows = client.get("/saves").json().get("saves") or []
        autosave_name = next(r["filename"] for r in rows
                             if r.get("filename", "").startswith("autosave"))
        reply = client.post("/load",
                            json={"filename": autosave_name}).json()
        assert reply["success"] is True
        assert M.world.campaign_seed == "pale-courier-33"


# ═══════════════════════════════════════════════════════════════════════
# The client's own wiring (text pins — the parse harness owns the syntax)
# ═══════════════════════════════════════════════════════════════════════
class TestTheClientWiring:
    GD = REPO / "godot-client" / "project-sovereign" / "scripts"

    def test_the_menu_seed_box_rides_begin_alone(self):
        menu = (self.GD / "main_menu.gd").read_text(encoding="utf-8")
        assert "suggested_seed" in menu
        assert 'action == "new_game"' in menu
        boot = (self.GD / "menu_boot.gd").read_text(encoding="utf-8")
        assert "take_seed" in boot

    def test_the_api_body_carries_the_seed_only_when_given(self):
        api = (self.GD / "api_client.gd").read_text(encoding="utf-8")
        assert 'if seed != "":' in api and '"seed"' in api

    def test_both_briefing_renderers_print_the_line(self):
        for name in ("dispatch_view.gd", "main.gd"):
            src = (self.GD / name).read_text(encoding="utf-8")
            assert "campaign_seed_line" in src, name

    def test_the_load_row_prints_the_seed(self):
        src = (self.GD / "load_dialog.gd").read_text(encoding="utf-8")
        assert "campaign_seed" in src
