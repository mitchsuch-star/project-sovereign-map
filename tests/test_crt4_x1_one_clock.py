"""CRT-4-X1 "One clock" (Score Finish Step 2 / SR-6a, October 2, 2026).

Every order-ETA surface read ONE clock, `strategic.order_turns_remaining`,
and that clock counted PROVINCES: the dispatch's "N turns out", the issuing
turn's report row, the per-turn MOVE_TO row (`len(path)`), the Ledger's
"(N turns left)" — while the relay's "~N turns" was ceil(len / range) and
forgot the issuing turn's skipped tick. Measured on the shipped boot before
a line changed: Murat (range 2) -> Paris read "4 turns left" on the Ledger
and arrived after 3 end turns; Soult (range 1) -> Gascony read "3 turns
left" on the issuing turn and arrived after 4.

The clock is `march_turns`'s: END TURNS until the man stands at the end —
ceil(steps / range), +1 on a surface read BEFORE the issuing turn's skipped
tick (the Ledger, the relay, the desk) for an order issued that turn. The
report rows are read AT the tick and take no +1.

Pins are DRIVEN: the orders are given at `POST /command`, the turns ended,
and every surface's number is held against the arrival the board produced.
"""
import re

import pytest
from fastapi.testclient import TestClient

import backend.commands.strategic as S
import backend.commands.relay as R
import backend.game_logic.ledger as L
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.marshal import StrategicOrder


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def _order(path, issued=None):
    o = StrategicOrder(command_type="MOVE_TO", target="Vienna", target_type="region",
                       started_turn=3, original_command="test")
    o.path = list(path)
    if issued is not None:
        o.issued_turn = issued
    return o


class TestTheClock:
    """The arithmetic, in isolation."""

    def test_range_aware(self):
        assert S.order_turns_remaining(_order(["A", "B", "C", "D", "E"]), 5, movement_range=2) == 3
        assert S.order_turns_remaining(_order(["A", "B", "C", "D"]), 5, movement_range=2) == 2
        assert S.order_turns_remaining(_order(["A", "B", "C"]), 5) == 3
        assert S.order_turns_remaining(_order([]), 5, movement_range=2) == 0

    def test_a_surface_read_before_the_issuing_tick_counts_it(self):
        o = _order(["A", "B", "C"], issued=5)
        assert S.order_turns_remaining(o, 5, before_tick=True) == 4
        assert S.order_turns_remaining(o, 5) == 3            # at the tick
        assert S.order_turns_remaining(o, 6, before_tick=True) == 3  # a later turn

    def test_the_clock_is_march_turns(self):
        # The desk's number for a fresh order (the whole road, first `range`
        # taken at issue) equals the Ledger's read on the issuing turn.
        for road_len in range(1, 9):
            for rng in (1, 2):
                after = road_len - min(rng, road_len)
                o = _order(["x"] * after, issued=7)
                ledger = S.order_turns_remaining(o, 7, movement_range=rng, before_tick=True)
                assert ledger == S.march_turns(road_len, rng), (road_len, rng)

    def test_lever_down_is_the_roads_length(self, monkeypatch):
        monkeypatch.setattr(S, "ONE_CLOCK", False)
        o = _order(["A", "B", "C", "D", "E"], issued=5)
        assert S.order_turns_remaining(o, 5, movement_range=2, before_tick=True) == 5
        assert S.order_eta_phrase(o, 5, movement_range=2) == " — 5 turns out"

    def test_the_timed_order_keeps_its_own_count(self):
        from backend.models.marshal import StrategicCondition
        o = _order(["A", "B"], issued=5)
        o.condition = StrategicCondition(max_turns=3)
        o.command_type = "HOLD"
        assert S.order_turns_remaining(o, 5, movement_range=2, before_tick=True) == \
            S.order_turns_remaining(o, 5)


def _ledger_turns(world, name):
    row = next(r for r in L.build_strategic_ledger(world)["forces"] if r["name"] == name)
    m = re.search(r"\((\d+) turns left\)", row["strategic_order"])
    return int(m.group(1)) if m else None


def _dispatch_eta(payload, name):
    rows = payload.get("morning_dispatch", {}).get("marshals", [])
    row = next((r for r in rows if r["name"] == name), None)
    if row is None:
        return None
    note = row.get("status_note", "")
    if "arrives next turn" in note:
        return 1
    m = re.search(r"(\d+) turns out", note)
    return int(m.group(1)) if m else None


def _report_turns(payload, name):
    for r in payload.get("strategic_reports") or []:
        if r.get("marshal") == name and r.get("turns_remaining") is not None:
            return int(r["turns_remaining"])
    return None


def _drive(client, world, name, destination, max_turns=8):
    """Issue the march, then end turns until the man stands at `destination`.
    Returns (ledger_at_issue, [per-morning dispatch ETA], [per-tick report
    row], end turns driven)."""
    r = post(client, f"{name}, march to {destination}")
    assert r.get("success"), r.get("message")
    order = world.marshals[name].strategic_order
    assert order is not None and order.command_type == "MOVE_TO", r.get("message")
    ledger_at_issue = _ledger_turns(world, name)
    mornings, rows = [], []
    for turn in range(1, max_turns + 1):
        payload = post(client, "end turn")
        assert payload.get("success") is not False, payload.get("message")
        rows.append(_report_turns(payload, name))
        if world.marshals[name].location == destination:
            return ledger_at_issue, mornings, rows, turn
        mornings.append(_dispatch_eta(payload, name))
    raise AssertionError(f"{name} never reached {destination}: {world.marshals[name].location}")


class TestEverySurfaceAgreesWithTheArrival:

    def test_an_infantry_march(self, shipped):
        client, world = shipped
        ledger, mornings, rows, driven = _drive(client, world, "Soult", "Gascony")
        assert driven == 4, (ledger, mornings, rows, driven)
        assert ledger == driven, "the Ledger on the issuing turn counts the skipped tick"
        # Each morning's dispatch names the end turns still ahead.
        for i, eta in enumerate(mornings):
            assert eta == driven - (i + 1), (mornings, driven)
        # Each tick's report row names the end turns still ahead of it.
        for i, left in enumerate(rows[:-1]):
            assert left == driven - (i + 1), (rows, driven)

    @pytest.mark.parametrize("start,destination", [("Brittany", "Languedoc"),
                                                   ("Provence", "Bordelais")])
    def test_a_cavalry_march_is_not_overstated(self, shipped, start, destination):
        """Murat is STAGED on a quiet western road: from his boot province
        the only roads west pass Burgundy, where Mack's guns at Franche-Comte
        turn him round on turn 2 (a fact about the board, not the clock)."""
        client, world = shipped
        murat = world.marshals["Murat"]
        assert murat.movement_range == 2
        murat.location = start
        world._build_marshal_index()
        world.calculate_visibility()
        ledger, mornings, rows, driven = _drive(client, world, "Murat", destination)
        assert ledger == driven, (ledger, mornings, rows, driven)
        for i, eta in enumerate(mornings):
            assert eta == driven - (i + 1), (mornings, driven)
        for i, left in enumerate(rows[:-1]):
            assert left == driven - (i + 1), (rows, driven)

    def test_the_road_length_would_have_lied(self, shipped):
        """The lever-down reading of the same boards — the row's own numbers:
        an infantry order read on the issuing turn is one short (Soult ->
        Gascony: 3 provinces left, 4 end turns), and a cavalry road is not
        a turn a province."""
        client, world = shipped
        post(client, "Soult, march to Gascony")
        soult = world.marshals["Soult"].strategic_order
        assert _ledger_turns(world, "Soult") == len(soult.path) + 1
        murat = world.marshals["Murat"]
        murat.location = "Provence"
        world._build_marshal_index()
        world.calculate_visibility()
        post(client, "Murat, march to Bordelais")
        order = murat.strategic_order
        assert len(order.path) == 1 and _ledger_turns(world, "Murat") == 2

    def test_the_relay_counts_the_skipped_tick(self, shipped):
        client, world = shipped
        r = post(client, "Soult, march to Gascony then fortify")
        note = str(r.get("relay_note") or r.get("message") or "")
        m = re.search(r"~(\d+) turn", note)
        assert m, note
        assert int(m.group(1)) == _ledger_turns(world, "Soult"), note

    def test_the_desk_reads_the_same_clock(self, shipped):
        client, world = shipped
        asked = post(client, "can Soult reach Gascony?")
        m = re.search(r"in (\d+) turns", str(asked.get("message", "")))
        assert m, asked.get("message")
        post(client, "Soult, march to Gascony")
        assert int(m.group(1)) == _ledger_turns(world, "Soult")
