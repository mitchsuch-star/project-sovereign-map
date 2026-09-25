"""FA slice 17, Phase 3 (September 11, 2026) — the fixes the re-score playtest
forced, each behind a lever whose False arm reproduces the prior board.

  FA-S17-5 (P1) the defense claim names its holder, and the war-level
           `ticking` sum is clamped like its eight siblings
  FA-S17-6 (P2) every rebellion exit retires the "rebellion imminent" question
  FA-S17-7 (P2) the Guard cannot buy a road it cannot pay
  FA-S17-8 (P3) the cascade one-liner reads the field its producer writes
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import diplomacy as D
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-5 — the claim names its holder; the sum is clamped
# ═══════════════════════════════════════════════════════════════════════
class TestTheDefenseClaimNamesItsHolder:
    """On the 1805 boot every French pair carries FA-D4's default `defense`
    objective over the 28 home provinces. Austria takes Paris."""

    @staticmethod
    def _paris_to_austria(w):
        w.get_region("Paris").controller = "Austria"
        w.invalidate_active_nations_cache()
        with _quiet():
            D.accumulate_war_objective_ticking(w)

    def _tick(self, w, court):
        key = w._make_diplo_key("France", court)
        return int((w.war_objectives.get(key) or {}).get("France", {}).get("accumulated_ticking", 0))

    def test_only_the_court_that_holds_paris_is_owed(self):
        w = _boot()
        self._paris_to_austria(w)
        assert self._tick(w, "Austria") == 1
        assert self._tick(w, "Britain") == 0
        assert self._tick(w, "Russia") == 0

    def test_a_province_nobody_took_ticks_for_nobody(self):
        w = _boot()
        with _quiet():
            D.accumulate_war_objective_ticking(w)
        for court in ("Austria", "Britain", "Russia"):
            assert self._tick(w, court) == 0

    def test_lever_down_charges_every_court_for_one_loss(self, monkeypatch):
        monkeypatch.setattr(D, "THE_DEFENSE_TICK_NAMES_ITS_HOLDER", False)
        w = _boot()
        self._paris_to_austria(w)
        assert self._tick(w, "Austria") == 1
        assert self._tick(w, "Britain") == 1
        assert self._tick(w, "Russia") == 1

    def test_the_war_level_ticking_is_clamped_like_its_siblings(self):
        w = _boot()
        courts = ["Austria", "Britain", "Russia"]
        for court in courts:
            key = w._make_diplo_key("France", court)
            w.war_objectives[key]["France"]["accumulated_ticking"] = D.TICKING_CAP
        with _quiet():
            comps = D.calculate_side_war_score("France", courts, w, return_components=True)
        assert comps["ticking"] == D.TICKING_CAP
        assert abs(comps["ticking"]) <= D.TICKING_CAP

    def test_lever_down_sums_the_claims_unclamped(self, monkeypatch):
        monkeypatch.setattr(D, "THE_TICKING_SUM_IS_CLAMPED", False)
        w = _boot()
        courts = ["Austria", "Britain", "Russia"]
        for court in courts:
            key = w._make_diplo_key("France", court)
            w.war_objectives[key]["France"]["accumulated_ticking"] = D.TICKING_CAP
        with _quiet():
            comps = D.calculate_side_war_score("France", courts, w, return_components=True)
        assert comps["ticking"] == 3 * D.TICKING_CAP

    def test_a_france_that_lost_paris_is_not_winning_the_coalition_war(self):
        """The measured shape: Paris held by Austria, and nine turns of the
        claim on the pair — the side score must read LOSING, so the peace
        table never pays the loser."""
        w = _boot()
        w.get_region("Paris").controller = "Austria"
        w.invalidate_active_nations_cache()
        with _quiet():
            for _ in range(9):
                D.accumulate_war_objective_ticking(w)
        courts = [c for c in ("Austria", "Britain", "Russia")]
        with _quiet():
            comps = D.calculate_side_war_score("France", courts, w, return_components=True)
        assert comps["ticking"] <= D.TICKING_CAP
        assert comps["total"] < 0, comps


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-6 — every rebellion exit retires the question
# ═══════════════════════════════════════════════════════════════════════
class TestTheRebellionRetiresItsQuestion:
    @staticmethod
    def _staged(w, vassal="Switzerland"):
        w.dialogue_manager.push({"type": "vassal_rebellion_imminent",
                                 "context": {"vassal_name": vassal, "lord": "France"},
                                 "options": [{"id": "accept_vassal_rebellion"}]})
        w.vassal_rebellion_imminent_popups = [{"nation": vassal}]
        w.vassal_rebellion_imminent_popup = {"nation": vassal}
        return w

    @staticmethod
    def _standing(w, vassal="Switzerland"):
        dm = w.dialogue_manager
        queued = any(d.get("type") == "vassal_rebellion_imminent"
                     and d.get("context", {}).get("vassal_name") == vassal
                     for d in list(getattr(dm, "queue", []) or []))
        cur = dm.peek() if hasattr(dm, "peek") else None
        current = bool(cur and cur.get("type") == "vassal_rebellion_imminent"
                       and cur.get("context", {}).get("vassal_name") == vassal)
        popups = any(p.get("nation") == vassal for p in (w.vassal_rebellion_imminent_popups or []))
        return queued or current or popups or bool(getattr(w, "vassal_rebellion_imminent_popup", None))

    def test_the_war_exit_retires_it(self):
        from backend.game_logic import vassal as V
        w = _boot()
        assert "Switzerland" in w.vassals
        self._staged(w)
        assert self._standing(w)
        w.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(w)
        assert "Switzerland" not in w.vassals
        assert not self._standing(w), "the question outlived the rebellion"

    def test_lever_down_leaves_it_standing(self, monkeypatch):
        from backend.game_logic import vassal as V
        monkeypatch.setattr(V, "THE_REBELLION_RETIRES_ITS_QUESTION", False)
        w = _boot()
        self._staged(w)
        w.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(w)
        assert "Switzerland" not in w.vassals
        assert self._standing(w)

    def test_the_transfer_exit_still_retires_it(self):
        from backend.game_logic import vassal as V
        w = _boot()
        self._staged(w)
        with _quiet():
            V.transfer_vassal(w, "Switzerland", "Austria", reason="test")
        assert not self._standing(w)


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-7 — the Guard cannot buy a road it cannot pay
# ═══════════════════════════════════════════════════════════════════════
class TestTheGuardCannotBuyARoadItCannotPay:
    @staticmethod
    def _cornered_sovereign(strength):
        from backend.commands.executor import CommandExecutor
        # `is_sovereign` is DERIVED from the personality string (NP-0, zero
        # new serialized fields) — the property has no setter by design.
        nap = MarshalFactory.infantry(name="Napoleon", location="Belgium", strength=strength,
                                      personality="sovereign")
        assert nap.is_sovereign
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria", strength=40000)
        world = WorldFactory.with_marshals([nap, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        ex = CommandExecutor()
        with _quiet():
            msg = ex._combat._check_marshal_fate(nap, mack, world)
        return nap, msg

    def test_a_guard_that_can_pay_buys_the_road(self):
        # Flipped consciously (GE-V / GE-D2, Sept 25, 2026): the floor the
        # toll respects is GUARD_SPENT_FLOOR (1,000 men), not the 50-man
        # rubble line — a 1,000-man Guard paying 300 would be left under it
        # and is ASKED instead; a 3,000-man Guard still buys the road.
        nap, msg = self._cornered_sovereign(3000)
        assert msg is None
        assert nap.strength == 2100
        assert nap.pending_interrupt is None
        assert "bought the road" in getattr(nap, "_sovereign_toll_note", "")

    def test_a_guard_the_toll_would_spend_is_asked_instead(self):
        nap, msg = self._cornered_sovereign(60)
        ask = nap.pending_interrupt
        assert ask and ask["interrupt_type"] == "last_stand" and ask.get("sovereign") is True
        assert "SPENT" in ask["message"] and "cannot buy another road" in ask["message"]
        assert nap.strength == 60, "no toll is taken from a road that cannot be bought"
        assert msg and "awaiting your word" in msg

    def test_lever_down_pays_the_toll_into_the_rubble(self, monkeypatch):
        from backend.commands.combat_executor import CombatExecutor
        monkeypatch.setattr(CombatExecutor, "THE_GUARD_CANNOT_BUY_A_ROAD_IT_CANNOT_PAY", False)
        nap, msg = self._cornered_sovereign(60)
        assert nap.pending_interrupt is None
        assert nap.strength == 0, "the prior toll: 60 - 18 = 42, under the 50-man rubble floor -> 0"


# ═══════════════════════════════════════════════════════════════════════
# FA-S17-8 — the cascade one-liner reads `defender`
# ═══════════════════════════════════════════════════════════════════════
class TestTheCascadeOneLinerReadsTheProducer:
    def test_the_defender_is_named(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "defensive_cascade", "defender": "Spain",
                                      "ally": "France", "against": "Britain", "turn": 3})
        assert "Spain joins war via France" in line
        assert "Unknown" not in line

    def test_the_old_field_still_reads(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "defensive_cascade", "nation": "Bavaria",
                                      "ally": "France", "turn": 3})
        assert "Bavaria joins war via France" in line

    def test_the_producer_writes_defender(self):
        src = (ROOT / "backend" / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        i = src.index('"type": "defensive_cascade",')
        assert '"defender": nation,' in src[i:i + 200]
