"""SR-5r DP-1 — "The bank" (`docs/REFORMS_SPEC.md` §9; §11 T6; SR-D3 Q3 RULED
September 27, 2026).

Diplomatic points bank ONE turn, for every court (GR5): at the refill,
carry = min(unspent, regen) and the pool = min(DP_BANK_CAP = 7, regen +
carry) — `diplomacy.dp_refill`, the one rule. Zero new serialized fields: the
unspent pool before the refill IS the carry. Shown = applied: the dispatch's
regen breakdown names "+N carried from last turn", and the displayed ceiling
is regen + carried — never a pool over its own printed maximum (the NP
audit's "DP: 6/5" lesson), even after a load drops the refill's transient.
Lever `diplomacy.DIPLOMATIC_POINTS_CARRY` — down, the pool resets to the
regen each turn exactly as before.

Measured before landing (`tools/_dp1_measure.py`): on the ambient board the
fuller AI pools (≈3–4 → ≈6–7) unlock NOTHING — the same 21 spends (27 points)
on both arms, and the threat series is byte-identical.
"""
import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import diplomacy as DG
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


def regen_of(world, nation):
    """The court's regen alone: refill an empty pool."""
    if nation == world.player_nation:
        world.diplomatic_points = 0
    else:
        world.nation_dp[nation] = 0
    with _quiet():
        DG._process_dp_regen(world)
    return (world.diplomatic_points if nation == world.player_nation
            else world.nation_dp[nation])


def refill(world):
    with _quiet():
        DG._process_dp_regen(world)


class TestTheRule:

    @pytest.mark.parametrize("regen, unspent, pool, carried", [
        (5, 0, 5, 0),
        (5, 2, 7, 2),
        (5, 5, 7, 2),      # the cap binds
        (3, 5, 6, 3),      # a carry never exceeds the regen
        (3, 1, 4, 1),
        (5, -2, 5, 0),     # a debt carries nothing
    ])
    def test_the_refill(self, regen, unspent, pool, carried):
        assert DG.dp_refill(regen, unspent) == (pool, carried)

    def test_the_cap(self):
        assert DG.DP_BANK_CAP == 7

    def test_lever_down_the_pool_resets(self, monkeypatch):
        monkeypatch.setattr(DG, "DIPLOMATIC_POINTS_CARRY", False)
        assert DG.dp_refill(5, 5) == (5, 0)


class TestT6:

    def test_the_player_carries_one_turn_up_to_seven_and_no_further(self, world):
        regen = regen_of(world, "France")
        assert regen == 5
        refill(world)                                  # spent nothing
        assert world.diplomatic_points == 7
        refill(world)
        assert world.diplomatic_points == 7            # and no further

    def test_every_court_banks_the_same_way(self, world):
        regen = regen_of(world, "Austria")
        refill(world)
        assert world.nation_dp["Austria"] == min(DG.DP_BANK_CAP, 2 * regen)

    def test_a_spent_pool_carries_nothing(self, world):
        regen = regen_of(world, "France")
        refill(world)
        world.diplomatic_points = 0                    # spent it all
        refill(world)
        assert world.diplomatic_points == regen

    def test_what_is_left_carries(self, world):
        regen = regen_of(world, "France")
        world.diplomatic_points = 1
        refill(world)
        assert world.diplomatic_points == regen + 1

    def test_lever_down_nothing_banks(self, world, monkeypatch):
        monkeypatch.setattr(DG, "DIPLOMATIC_POINTS_CARRY", False)
        regen = regen_of(world, "France")
        refill(world)
        assert world.diplomatic_points == regen


class TestShownIsApplied:

    def _regen_row(self, world):
        rows = [e for e in world.pending_dispatch_events
                if e.get("type") == "diplomatic_dp_regen"]
        return rows[-1]["template_vars"]

    def test_the_dispatch_names_the_carry(self, world):
        regen_of(world, "France")
        world.pending_dispatch_events = []
        refill(world)
        row = self._regen_row(world)
        assert row["dp"] == 7
        assert row["breakdown"].endswith("+2 carried from last turn")

    def test_no_carry_no_words(self, world):
        regen_of(world, "France")
        world.diplomatic_points = 0
        world.pending_dispatch_events = []
        refill(world)
        assert "carried" not in self._regen_row(world)["breakdown"]

    def test_the_ceiling_is_regen_plus_carried(self, world):
        regen_of(world, "France")
        refill(world)
        assert DG.displayed_dp_ceiling(world) == world.diplomatic_points == 7
        world.diplomatic_points = 3                     # spent four
        assert DG.displayed_dp_ceiling(world) == 7      # this turn's ceiling holds

    def test_never_a_pool_over_its_printed_maximum_after_a_load(self, world):
        regen_of(world, "France")
        refill(world)
        world._dp_refill = {}                           # a load drops the transient
        assert DG.displayed_dp_ceiling(world) >= world.diplomatic_points == 7

    def test_the_top_bar_reads_the_same_ceiling(self, world):
        regen_of(world, "France")
        refill(world)
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/command", json={"command": "status"}).json()
        assert r["max_diplomatic_points"] == DG.displayed_dp_ceiling(world) == 7
        assert r["diplomatic_points"] == 7

    def test_the_transient_is_never_saved(self, world):
        regen_of(world, "France")
        refill(world)
        assert "_dp_refill" not in world.to_dict()


class TestTheMeasurement:
    """§9 "Measure before landing" — the committed `tools/_dp1_measure.json`."""

    DATA = json.loads((ROOT / "tools" / "_dp1_measure.json").read_text(encoding="utf-8"))

    def test_a_fuller_pool_unlocks_nothing_on_the_ambient_board(self):
        assert self.DATA["off"]["spends"] == self.DATA["on"]["spends"]
        assert self.DATA["off"]["points"] == self.DATA["on"]["points"]
        assert self.DATA["off"]["series"] == self.DATA["on"]["series"]

    def test_the_ai_pools_sit_near_the_cap(self):
        on = self.DATA["on"]["mean_pool"]
        off = self.DATA["off"]["mean_pool"]
        assert all(on[n] > off[n] for n in on)
        assert max(on.values()) <= DG.DP_BANK_CAP

    def test_the_measured_series_is_the_shipped_series(self):
        """RE-SEATED by the AI drill fix (September 27, 2026): DP-1 measured
        against the RF-3 record, which the drill fix's arm 0 (every drill
        lever down) reproduces byte for byte; the drill fix's arm 1 is the
        standing series."""
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        drill = json.loads((ROOT / "tools" / "_drill_fix_series_arms.json").read_text(
            encoding="utf-8"))
        assert self.DATA["on"]["series"] == drill["recorded"]
        assert drill["arms"]["0"]["series"] == drill["recorded"]
        # RE-SEATED by SR-5a "The chest" (September 28, 2026): one more link —
        # the drill fix's arm 1 is the prior record SR-5a's arm 0 (the
        # pre-slice scenario, every lever down) reproduces byte for byte, and
        # SR-5a's arm 1 (the ruled balance package) is the standing series.
        sr5a = json.loads((ROOT / "tools" / "_sr5a_series_arms.json").read_text(
            encoding="utf-8"))
        assert drill["arms"]["1"]["series"] == sr5a["recorded"]
        assert sr5a["arms"]["0"]["series"] == sr5a["recorded"]
        # RE-SEATED by Score Finish Step 3 "Europe acts without France" (October
        # 2, 2026): one more link — SR-5a's arm 1 is the prior record Step 3's
        # arm 0 (every Step-3 lever down in the child) reproduces byte for
        # byte, and Step 3's ALL arm (the shipped tree) is the standing series
        # (`tools/_step3_series_arms_final.json`, fifteen arms).
        step3 = json.loads((ROOT / "tools" / "_step3_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sr5a["arms"]["1"]["series"] == step3["prior"]
        assert step3["arms"]["0"]["series"] == step3["prior"]
        # RE-SEATED by SR-7d "The Doctrines" (October 3, 2026): one more link —
        # Step 3's ALL arm is the prior record SR-7d's arm 0 (every doctrine
        # lever down in the child) reproduces byte for byte, and SR-7d's ALL
        # arm (the shipped tree: the five doctrines, the cures, the rung that
        # saves for the Staff) is the standing series
        # (`tools/_sr7d_series_arms_final.json`, nine arms).
        sr7d = json.loads((ROOT / "tools" / "_sr7d_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert step3["arms"]["ALL"]["series"] == sr7d["prior"]
        assert sr7d["arms"]["0"]["series"] == sr7d["prior"]
        # RE-SEATED by SF-LB-2 "The Defenceless Prize" (October 3, 2026): one
        # more link — SR-7d's ALL arm is the prior record SF-LB-2's arm 0
        # (every SF-LB-2 lever down in the child) reproduces byte for byte,
        # and SF-LB-2's ALL arm (the shipped tree: Prussia takes Hanover) is
        # the standing series (`tools/_sf_lb2_series_arms_final.json`, ten
        # arms).
        sflb2 = json.loads((ROOT / "tools" / "_sf_lb2_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sr7d["arms"]["ALL"]["series"] == sflb2["prior"]
        assert sflb2["arms"]["0"]["series"] == sflb2["prior"]
        # RE-SEATED by SF-LB-2b "The Chest the Council Can Spend" (October 3,
        # 2026): one more link — SF-LB-2's ALL arm is the prior record
        # SF-LB-2b's arm 0 (the one lever down in the child) reproduces byte
        # for byte, and SF-LB-2b's ALL arm (the shipped tree: the crisis opens
        # on the ladder's turn) is the standing series
        # (`tools/_sf_lb2b_series_arms_final.json`, two arms).
        sflb2b = json.loads((ROOT / "tools" / "_sf_lb2b_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sflb2["arms"]["ALL"]["series"] == sflb2b["prior"]
        assert sflb2b["arms"]["0"]["series"] == sflb2b["prior"]
        # RE-SEATED by VD-C "The Contingent" (October 3, 2026): one more link
        # — SF-LB-2b's ALL arm is the prior record VD-C's arm 0 (every lever
        # down and the deck entry stripped in the child) reproduces byte for
        # byte, and VD-C's ALL arm (the shipped tree: the boot satellites send
        # their contingents) is the standing series
        # (`tools/_vdc_series_arms_final.json`, eighteen arms).
        vdc = json.loads((ROOT / "tools" / "_vdc_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert sflb2b["arms"]["ALL"]["series"] == vdc["prior"]
        assert vdc["arms"]["0"]["series"] == vdc["prior"]
        # RE-SEATED by §6 row 16 "the coordination is read on the field"
        # (October 4, 2026): one more link — VD-C's ALL arm is the prior
        # record the field read's arm 0 (both levers down in the child)
        # reproduces byte for byte, and its ALL arm (the shipped tree) is the
        # standing series (`tools/_coord_field_series_arms_final.json`).
        coord = json.loads((ROOT / "tools" / "_coord_field_series_arms_final.json").read_text(
            encoding="utf-8"))
        assert vdc["arms"]["ALL"]["series"] == coord["prior"]
        assert coord["arms"]["0"]["series"] == coord["prior"]
        assert BASELINE_SERIES == coord["arms"]["ALL"]["series"]
