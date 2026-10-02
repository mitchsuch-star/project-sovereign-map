"""Score Finish Step 3 (October 2, 2026) — the exit's own fixes, pinned.

The Step 3 exit run (`score_run.py check` against the baseline) read two
items ✓→✗ that were the INSTRUMENT or a seam one board over, not the
slice:

- **narration C4** — on CMD-H turn 40 Deroy was taken at Franche-Comte in
  the enemy phase and the next morning's intelligence rows still carried
  his three-turn-old Franconia label: `intel_surfaces.enemy_sightings`
  skipped a prisoner on the LIVE read (`captured_by`) and never on the
  frozen snapshots. A prisoner is not a sighting
  (`A_PRISONER_IS_NOT_A_SIGHTING`).
- **combat C1** — the `attack_anyway` answer to a contact question opened
  the battle on its muster (`strategic.THE_ANSWERED_CONTACT_PRINTS_ITS_MUSTER`),
  and the digest printed the question and the battle with nothing between:
  the answered interrupt's reply was never rendered. The driver now prints
  the reply's muster line under the POPUP row
  (`playtest_driver.THE_DIGEST_PRINTS_THE_ANSWERED_MUSTER`).
"""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import pytest

from backend.game_logic import intel_surfaces as IS
from backend.models.intel import FULL, STALE
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
sys.path.insert(0, str(REPO / "tools"))


def _world():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


def _stale_label(world, name, nation, region, turn):
    intel = world.intel[region]
    intel.visibility = STALE
    intel.last_updated_turn = turn
    intel.known_marshals = [{"name": name, "nation": nation, "strength": 7507}]


class TestAPrisonerIsNotASighting:
    def _staged(self):
        """Mack, captured by France this morning (he stands in a French
        cell), with a stale Franconia label from three turns ago."""
        world = _world()
        world.current_turn = 40
        mack = world.marshals["Mack"]
        mack.captured_by = "France"
        mack.location = "Paris"
        for intel in world.intel.values():
            if intel.visibility == FULL:
                intel.known_marshals = [km for km in intel.known_marshals if km.get("name") != "Mack"]
        _stale_label(world, "Mack", "Austria", "Franconia", 37)
        return world

    def test_the_prisoners_stale_label_never_rides(self):
        world = self._staged()
        rows = IS.enemy_sightings(world, "France")
        assert not [r for r in rows if r["roster_name"] == "Mack"], rows

    def test_a_free_mans_stale_label_still_rides(self):
        world = self._staged()
        world.marshals["Mack"].captured_by = ""
        world.marshals["Mack"].location = "Brittany"        # out of every FULL province
        rows = IS.enemy_sightings(world, "France")
        row = next(r for r in rows if r["roster_name"] == "Mack")
        assert row["location"] == "Franconia" and row["source"] == "snapshot"

    def test_lever_down_the_prisoner_rides_again(self, monkeypatch):
        monkeypatch.setattr(IS, "A_PRISONER_IS_NOT_A_SIGHTING", False)
        world = self._staged()
        rows = IS.enemy_sightings(world, "France")
        assert [r for r in rows if r["roster_name"] == "Mack"]


class TestTheDigestPrintsTheAnsweredMuster:
    def _drive(self, tmp_path, lever, monkeypatch):
        import playtest_driver as PD
        monkeypatch.setattr(PD, "THE_DIGEST_PRINTS_THE_ANSWERED_MUSTER", lever)
        digest = PD.Digest(tmp_path, {"name": "step3-exit-pin", "seed": "historical", "llm": "mock", "transport": "test", "policy": {}})
        question = {"message": "Ney: 'Charles blocks the path. Odds unfavorable. Your orders?'"}
        reply = {"message": "Ney attacks Charles. MUSTER — Ney (10,382) vs Charles (33,327) at Bohemia — unfavorable.\n\nBattle lines…"}

        class Answerer:
            def begin_post(self):
                pass

            def scan(self, current):
                return [reply] if current is question else []

        PD.drain(None, digest, Answerer(), question, strict=False)
        return (tmp_path / "digest.md").read_text(encoding="utf-8") if (tmp_path / "digest.md").exists() else ""

    def test_the_reply_muster_rides_under_the_popup(self, tmp_path, monkeypatch):
        md = self._drive(tmp_path, True, monkeypatch)
        assert "  - ↳ Ney attacks Charles. MUSTER — Ney" in md, md

    def test_lever_down_the_muster_is_dropped(self, tmp_path, monkeypatch):
        md = self._drive(tmp_path, False, monkeypatch)
        assert "MUSTER" not in md
