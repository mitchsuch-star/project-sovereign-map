"""CR-7-8 — the queue's second re-open trigger, MEASURED.

    python -m tools.cr7_8_order_completions [--script tools/playtest_scripts/commanded_full40.json]
                                            [--turns 40] [--seed historical]

Counts, for PLAYER marshals only, how many times `StrategicOrderProcessor.
_complete_order` and `_break_order` fire across a driven campaign — the
committed COMMANDED arm by default (`commanded_full40.json`, the arm the
FA-D27 ruling was dated on).

WHY THIS EXISTS. The cross-turn order queue (an N-step standing order held
across turns) is RETIRED BY CONTRACT (`COMMAND_ROBUSTNESS_SPEC.md` §9): the
hook every queue design would advance on, `_complete_order`, fired ONCE in
fourteen driven turns across three standing marches when the queue was
investigated, and `_break_order` fired ZERO times while two of the three
orders died at one of the other 41 `strategic_order = None` sites. A queue
built on that hook is furniture. The contract's SECOND re-open condition is
therefore measurable, not aesthetic: if player order completions on this arm
rise above the floor stated in the spec, the churn that made the queue
furniture has been fixed and the queue is re-opened.

MEASURED September 22, 2026 (HEAD a40114d4 + CR-7-2..8, seed `historical`,
`LLM_MODE=mock`, 40 loops, 160 commands): **0 completions, 0 breaks** for
player marshals — the commanded script issues only adjacent tactical moves,
so no standing march ever forms. Record the number beside the date whenever
this is re-run.

In-process, deterministic (PYTHONHASHSEED pinned like the driver), no server.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--script", default="tools/playtest_scripts/commanded_full40.json")
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--name", default="cr7-8-order-completions")
    args = ap.parse_args(argv)

    os.environ.setdefault("LLM_MODE", "mock")
    os.environ.setdefault("PYTHONHASHSEED", "0")
    os.environ.setdefault("INK_IRON_SAVE_DIR",
                          os.path.join(os.environ.get("TEMP", "."), "cr7_8_saves"))
    out_dir = os.path.join(os.environ.get("TEMP", "."), "cr7_8_runs")
    sys.argv = ["tools/playtest_driver.py", "--script", args.script,
                "--turns", str(args.turns), "--seed", args.seed,
                "--name", args.name, "--diplomacy", "accept", "--out", out_dir]

    import backend.commands.strategic as strategic
    completes: list = []
    breaks: list = []
    original_complete = strategic.StrategicOrderProcessor._complete_order
    original_break = strategic.StrategicOrderProcessor._break_order

    def spy_complete(self, marshal, world, reason):
        if getattr(marshal, "nation", "") == world.player_nation:
            completes.append((int(world.current_turn), marshal.name, reason[:60]))
        return original_complete(self, marshal, world, reason)

    def spy_break(self, marshal, world, reason):
        if getattr(marshal, "nation", "") == world.player_nation:
            breaks.append((int(world.current_turn), marshal.name, reason[:60]))
        return original_break(self, marshal, world, reason)

    strategic.StrategicOrderProcessor._complete_order = spy_complete
    strategic.StrategicOrderProcessor._break_order = spy_break
    try:
        import tools.playtest_driver as driver
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                driver.main()
            except SystemExit:
                pass
    finally:
        strategic.StrategicOrderProcessor._complete_order = original_complete
        strategic.StrategicOrderProcessor._break_order = original_break

    print(f"script={args.script} seed={args.seed} turns={args.turns}")
    print(f"PLAYER _complete_order fires: {len(completes)}")
    for row in completes:
        print("   ", row)
    print(f"PLAYER _break_order fires: {len(breaks)}")
    for row in breaks:
        print("   ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
