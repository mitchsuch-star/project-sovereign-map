"""SR-2c / PR-D1c — "The spend is the war's own" (Score Mandate Chunk 2
DIPLOMACY, September 26, 2026; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2; row
`DESIGN_REFINEMENT.md` PR-D1c — this is the behaviour test the row names).

A treaty that dissolves the league keeps whole the alarm of every live war the
target DECLARED on a court outside the league — the declaration's own stamp on
its pair, inside the already-serialized war instance — capped by the slot as
it stood; the league's own war is still halved.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

import backend.game_logic.coalition as C
from backend.game_logic.diplomacy import declare_war
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")

@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _europe():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


# ═══════════════════════════════════════════════════════════════════════
# PR-D1c — the spend is the war's own
# ═══════════════════════════════════════════════════════════════════════

def _declare(world, target):
    with _quiet():
        r = declare_war(world, "France", target)
    assert r.get("success"), r
    return r


class TestTheSpendIsTheWarsOwn:

    def test_the_declaration_stamps_its_alarm_on_the_pair(self):
        w = _europe()
        w.diplomatic_points = 5
        _declare(w, "Prussia")
        key = w._make_diplo_key("France", "Prussia")
        meta = next(inst["diplo_key_meta"][key] for inst in w.war_instances.values()
                    if key in (inst.get("diplo_key_meta") or {}))
        assert meta["declared_by"] == "France"
        from backend.game_logic.diplomacy import declaration_alarm
        assert meta["declaration_alarm"] == declaration_alarm(False)

    def test_declarations_on_outside_courts_survive_the_leagues_peace(self):
        """The row's scenario: alarm 70, declare on Prussia and Denmark (→ 100,
        clipped), the league's peace — the outside wars' 40 is kept whole,
        capped by the slot as it stood."""
        w = _europe()
        w.diplomatic_points = 6
        w.threat_by_target["France"] = 70
        _declare(w, "Prussia")
        _declare(w, "Denmark")
        assert int(w.threat_by_target["France"]) == 100
        members = list(w.active_coalition["members"])
        assert "Prussia" not in members and "Denmark" not in members
        w.threat_sources_this_turn = []          # a later turn
        outside = C.declared_alarm_outside_the_league(w, "France", members)
        assert outside == 40
        spent = C.league_spent_alarm(w, "France", league_members=members)
        assert spent == {"from": 100, "to": 90}   # 100 // 2 + 40, capped at 100

    def test_the_leagues_own_war_is_still_halved(self):
        w = _europe()
        w.threat_by_target["France"] = 90
        w.threat_sources_this_turn = []
        members = list(w.active_coalition["members"])
        assert C.declared_alarm_outside_the_league(w, "France", members) == 0
        assert C.league_spent_alarm(w, "France", league_members=members) == {"from": 90, "to": 45}

    def test_a_court_that_joined_the_league_is_the_leagues_war(self):
        """A declaration on a court that is a member at dissolution is the
        war the treaty ends — halved, not kept."""
        w = _europe()
        w.diplomatic_points = 5
        w.threat_by_target["France"] = 60
        _declare(w, "Prussia")
        members = list(w.active_coalition["members"]) + ["Prussia"]
        assert C.declared_alarm_outside_the_league(w, "France", members) == 0

    def test_a_peace_ends_the_stamp(self):
        w = _europe()
        w.diplomatic_points = 5
        w.threat_by_target["France"] = 60
        _declare(w, "Prussia")
        members = list(w.active_coalition["members"])
        assert C.declared_alarm_outside_the_league(w, "France", members) == 20
        from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
        with _quiet():
            resolve_pair_to_resolved(w, w._make_diplo_key("France", "Prussia"))
        assert C.declared_alarm_outside_the_league(w, "France", members) == 0

    def test_the_lever_down_halves_everything(self, monkeypatch):
        monkeypatch.setattr(C, "THE_SPEND_IS_THE_WARS_OWN", False)
        w = _europe()
        w.diplomatic_points = 6
        w.threat_by_target["France"] = 70
        _declare(w, "Prussia")
        _declare(w, "Denmark")
        w.threat_sources_this_turn = []
        members = list(w.active_coalition["members"])
        assert C.league_spent_alarm(w, "France", league_members=members) == {"from": 100, "to": 50}

    def test_the_real_dissolution_reads_the_leagues_members(self):
        src = (REPO / "backend" / "game_logic" / "coalition.py").read_text(encoding="utf-8")
        start = src.index("def dissolve_coalition(")
        body = src[start:start + 6000]
        assert "_dissolve_members = list(coalition.get(\"members\") or [])" in body
        assert "league_members=_dissolve_members" in body
