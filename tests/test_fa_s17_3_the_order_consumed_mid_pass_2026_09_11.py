"""FA-S17-3 (P1, found by the Phase-3 playtest, September 11, 2026).

`process_strategic_orders` takes its roster once and then, in pass 1, prints
`order.command_type` for each marshal — but an EARLIER corps' step in the same
pass can consume a LATER corps' order. Measured on the tyrant script, seed
`austerlitz`, world turn 7 (the driver's run BLOCKED): Bernadotte's PURSUE beat
Mack at Bohemia, his advance into Hungary took the co-located Ney along, and
the attack-movement cleared Ney's fresh MOVE_TO; the loop reached Ney with
`strategic_order is None`, raised AttributeError, and `end turn` could not
complete — the same error on every retry.

The pin below is STRUCTURAL: the first corps' step consumes the second's
order by the executor's own hand (a monkeypatched `_execute_strategic_turn`
that nulls it, exactly what the attack-movement did), and the pass must
finish, report the consumed order, and leave the second corps free.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

from backend.commands import strategic as ST
from backend.commands.executor import CommandExecutor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

ROOT = next(p for p in (Path(__file__).resolve().parents[1], Path.cwd()) if (p / "backend").is_dir())
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _order(kind, target, turn, path):
    return StrategicOrder(command_type=kind, target=target, target_type="region",
                          started_turn=turn - 1, issued_turn=None, path=list(path),
                          original_command=f"{kind} {target}")


class TestAnOrderConsumedMidPass:
    def _board(self):
        w = _boot()
        # Bernadotte precedes Ney alphabetically: his step runs first in pass 1.
        bern, ney = w.marshals["Bernadotte"], w.marshals["Ney"]
        bern.location = ney.location = "Franconia"
        bern.strategic_order = _order("MOVE_TO", "Bohemia", int(w.current_turn), ["Bohemia"])
        ney.strategic_order = _order("MOVE_TO", "Bohemia", int(w.current_turn), ["Bohemia"])
        return w, bern, ney

    def test_the_pass_finishes_and_reports_the_consumed_order(self, monkeypatch):
        w, bern, ney = self._board()
        proc = ST.StrategicOrderProcessor(CommandExecutor())
        real = proc._execute_strategic_turn

        def consuming_step(marshal, world, game_state):
            if marshal.name == "Bernadotte":
                # the attack-movement's hand: the co-located colleague is
                # taken along and his order cleared
                ney.location = "Bohemia"
                ney.strategic_order = None
                bern.strategic_order = None
                return {"marshal": "Bernadotte", "command": "MOVE_TO", "order_status": "completed",
                        "message": "Bernadotte arrives at Bohemia."}
            return real(marshal, world, game_state)

        monkeypatch.setattr(proc, "_execute_strategic_turn", consuming_step)
        with contextlib.redirect_stdout(io.StringIO()):
            reports = proc.process_strategic_orders(w, {"world": w})
        rows = {r["marshal"]: r for r in reports if isinstance(r, dict) and r.get("marshal")}
        assert rows["Bernadotte"]["order_status"] == "completed"
        assert rows["Ney"]["order_status"] == "consumed", rows.get("Ney")
        assert "overtaken" in rows["Ney"]["message"] and "Bohemia" in rows["Ney"]["message"]
        assert ney.strategic_order is None and not ney.in_strategic_mode

    def test_an_untouched_roster_reports_as_before(self):
        w, bern, ney = self._board()
        ney.strategic_order = None  # only Bernadotte marches; no consumption
        proc = ST.StrategicOrderProcessor(CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            reports = proc.process_strategic_orders(w, {"world": w})
        assert all(r.get("order_status") != "consumed" for r in reports if isinstance(r, dict))
        assert any(r.get("marshal") == "Bernadotte" for r in reports if isinstance(r, dict))

    def test_the_guard_is_in_pass_one(self):
        """A source pin on the SHAPE: the re-read sits between the dead-marshal
        skip and the print that crashed — pass 2's guard alone does not cover
        pass 1."""
        src = (ROOT / "backend" / "commands" / "strategic.py").read_text(encoding="utf-8")
        i_skip = src.index("SKIP - marshal defeated, order cleared")
        i_guard = src.index("order consumed by an earlier step this pass")
        i_print = src.index('print(f"[STRATEGIC] {marshal.name}: {order.command_type} -> {order.target} "')
        assert i_skip < i_guard < i_print
