"""RE-5 — the dial's instrument (`docs/RECURRING_EVENTS_SPEC.md` §17 Q13; the
landing record §26.3): `tools/_affairs_lapse_share.py` reads the share of
affairs lapsing off the saves' occurrence rows — lapsed over lapsed plus
answered, a withdrawal and a pass counted apart — per save, per template and
in all, and `--check` exits 2 over the dial's threshold (60 %). A raw JSON
reader: a save written by `save_manager` reads, and so does a bare world.
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools import _affairs_lapse_share as LS  # noqa: E402

SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
HAND_PLAYED = sorted(REPO.glob("tools/playtest_runs/dd_b_2026_10_2*/*/saves/autosave.json"))


def _save(path: Path, turn: int, rows: dict, wrapper: str = "world_state") -> None:
    world = {"current_turn": turn, "moments": {"state": rows}}
    data = {"metadata": {"save_name": path.stem, "turn": turn}, wrapper: world} if wrapper else world
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def crafted(tmp_path):
    """Two saves: the first with three lapses, one answer, one withdrawal and
    one pass across two templates; the second with one answer and a letter
    standing; beside them a file that is not a save."""
    _save(tmp_path / "a.json", 22, {
        "the_remounts#1": {"status": "lapsed", "turn": 12},
        "the_remounts#2": {"status": "lapsed", "turn": 20},
        "santo_domingo#1": {"status": "answered", "turn": 7, "answer": "accept"},
        "santo_domingo#2": {"status": "lapsed", "turn": 19},
        "the_host#1": {"status": "withdrawn", "turn": 7, "set_aside_for": "bavarian_match"},
        "berthiers_memorial#1": {"status": "passed", "turn": 11, "reason": "crowded"},
        "bavarian_match": {"status": "answered", "turn": 8},           # a dated moment: no `#`, not an affair
    })
    _save(tmp_path / "b.json", 9, {
        "santo_domingo#1": {"status": "answered", "turn": 7, "answer": "decline"},
        "the_magazines#1": {"status": "fired", "turn": 9},
    }, wrapper="world")
    (tmp_path / "notes.json").write_text("[1, 2, 3]", encoding="utf-8")
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")
    return tmp_path


class TestTheShare:
    def test_the_shares_per_save_per_template_and_in_all(self, crafted):
        record = LS.measure(sorted(crafted.glob("*.json")))
        by = {s["save"]: s for s in record["saves"]}
        assert set(by) == {"a.json", "b.json"} and record["unread"] == ["broken.json", "notes.json"]
        a = by["a.json"]
        assert a["turn"] == 22 and a["rows"] == 6
        assert a["counts"] == {"lapsed": 3, "answered": 1, "withdrawn": 1, "passed": 1, "fired": 0, "other": 0}
        assert a["share"] == 75.0
        assert a["templates"]["the_remounts"]["share"] == 100.0
        assert a["templates"]["santo_domingo"]["share"] == 50.0
        assert a["templates"]["the_host"]["share"] is None          # a withdrawal is not the player's silence
        assert a["templates"]["berthiers_memorial"]["share"] is None
        b = by["b.json"]
        assert b["counts"]["answered"] == 1 and b["counts"]["fired"] == 1 and b["share"] == 0.0
        assert record["overall"]["counts"]["lapsed"] == 3 and record["overall"]["counts"]["answered"] == 2
        assert record["overall"]["share"] == 60.0                   # 3 of 5
        assert record["affairs_seen"] == 8
        assert LS.verdict(record, 60.0) == "under" and LS.verdict(record, 59.0) == "over"

    def test_nothing_to_read_is_said_so(self, tmp_path):
        _save(tmp_path / "fresh.json", 1, {})
        record = LS.measure([tmp_path / "fresh.json"])
        assert record["overall"]["share"] is None and record["affairs_seen"] == 0
        assert LS.verdict(record, 60.0) == "no affairs answered or lapsed yet"

    def test_the_check_exit_code_and_the_record(self, crafted, capsys):
        out = crafted / "share.json"
        assert LS.main(["--saves", str(crafted), "--out", str(out), "--check", "59"]) == 2
        assert LS.main(["--saves", str(crafted), "--check"]) == 0            # 60.0 is not over 60
        assert LS.main(["--saves", str(crafted)]) == 0
        record = json.loads(out.read_text(encoding="utf-8"))
        assert record["verdict"] == "over" and record["threshold_pct"] == 59.0
        text = capsys.readouterr().out
        assert "ALL" in text and "the dial's evidence (over 59 % lapsing): over" in text
        assert "unread (not a save): broken.json, notes.json" in text


class TestTheSavesTheGameWrites:
    def test_a_save_written_by_save_manager_reads(self, tmp_path):
        """The real shape: the shipped boot with occurrence rows written into
        the moments' state, saved by `save_manager.save_game`, read back by
        path and by directory."""
        from backend.game_logic import moments as MO
        from backend.models.world_state import WorldState
        from backend.save_manager import save_game
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState.from_scenario(str(SCENARIO))
        MO._state(world).update({
            "santo_domingo#1": {"status": "answered", "turn": 7, "answer": "accept", "id": "santo_domingo#1", "lord": "France"},
            "the_remounts#1": {"status": "lapsed", "turn": 12, "id": "the_remounts#1", "lord": "France"},
        })
        path = tmp_path / "re5.json"
        assert save_game(world, "RE-5 share", filepath=path)["success"]
        rec = LS.read_save(path)
        assert rec["turn"] == 1 and set(rec["rows"]) == {"santo_domingo#1", "the_remounts#1"}
        record = LS.measure([path])
        assert record["overall"]["share"] == 50.0

    def test_the_hand_played_starts_read_as_no_affairs_yet(self):
        """The six DD-B autosaves of October 24–25 predate the engine: they
        read without error and say so."""
        if not HAND_PLAYED:
            pytest.skip("the hand-played saves are not in this checkout")
        record = LS.measure(HAND_PLAYED)
        assert len(record["saves"]) == len(HAND_PLAYED) and record["unread"] == []
        assert record["affairs_seen"] == 0
        assert LS.verdict(record, 60.0) == "no affairs answered or lapsed yet"

    def test_the_default_directory_honours_the_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path))
        assert LS.default_save_dir() == tmp_path
