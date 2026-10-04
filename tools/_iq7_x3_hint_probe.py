"""IQ7-X3 / VD-C's measure-first probe (Step 5, October 3, 2026).

Runs a playtest-driver arm in-process and counts, over the whole run, the
`vassal_loyalty` events the loyalty pass produced and how many of them
carried the per-tick `recovery_hint` (the line IQ7-X3 says repeats on 67-89
lines per 40-turn arm). It also records, every tick, whether the lord fields
a corps of each satellite's own colours (`lord_fields_the_vassals_regiments`
— the predicate IQ-7 R1's regiments clause rides on) and every VD-C
contingent beat, so the same run is VD-C's completion evidence.

    .venv/Scripts/python.exe tools/_iq7_x3_hint_probe.py --out X.json -- <driver args>

The driver args are passed through verbatim (e.g. the commanded arm:
`--script tools/playtest_scripts/commanded_full40.json --turns 40
--diplomacy accept --seed historical`). Nothing in the backend is changed:
the probe wraps the two vassal passes at their module attributes, which
`diplomacy.process_diplomatic_turn` imports at call time.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    if os.environ.get("PYTHONHASHSEED") is None:
        import subprocess
        env = dict(os.environ, PYTHONHASHSEED="0")
        raise SystemExit(subprocess.call([sys.executable, *sys.argv], env=env))
    raw = sys.argv[1:]
    if "--" in raw:
        split = raw.index("--")
        own, driver_args = raw[:split], raw[split + 1:]
    else:
        own, driver_args = raw, []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(own)

    from backend.game_logic import vassal as V
    record = {"ticks": [], "loyalty_events": 0, "hinted": 0,
              "hint_lines": [], "regiments_true": {}, "contingent_beats": []}
    real_loyalty = V.process_vassal_loyalty

    def _loyalty(world):
        events = real_loyalty(world)
        turn = int(world.current_turn)
        for event in events:
            if event.get("type") != "vassal_loyalty":
                continue
            record["loyalty_events"] += 1
            if event.get("recovery_hint"):
                record["hinted"] += 1
                record["hint_lines"].append(
                    {"turn": turn, "vassal": event.get("vassal"),
                     "delta": event.get("delta"),
                     "new": event.get("new_loyalty"),
                     "crossing": bool(event.get("tier_crossing"))})
        row = {"turn": turn, "loyalty": {}, "regiments": {}}
        for name, state in (world.vassals or {}).items():
            row["loyalty"][name] = int(state.get("loyalty", 0))
            fields = V.lord_fields_the_vassals_regiments(world, state.get("lord"), name)
            row["regiments"][name] = bool(fields)
            if fields:
                record["regiments_true"].setdefault(name, []).append(turn)
        record["ticks"].append(row)
        return events

    V.process_vassal_loyalty = _loyalty
    try:  # VD-C's pass, when the tree has it (absent on a pre-VD-C tree)
        from backend.game_logic import contingent as C
        real_pass = C.process_vassal_contingents

        def _contingents(world):
            beats = real_pass(world)
            for beat in beats:
                record["contingent_beats"].append(
                    {k: beat.get(k) for k in ("turn", "beat", "vassal", "lord",
                                              "marshal", "outcome", "reason",
                                              "strength", "survivors",
                                              "raised", "location", "host",
                                              "target", "message")})
            return beats

        C.process_vassal_contingents = _contingents
    except ImportError:
        pass
    sys.argv = ["playtest_driver.py", *driver_args]
    from tools import playtest_driver
    try:
        playtest_driver.main()
    except SystemExit:
        pass
    Path(args.out).write_text(json.dumps(record, indent=1, default=str),
                              encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("loyalty_events", "hinted")}),
          "regiments_true:", {k: (v[0], len(v)) for k, v in record["regiments_true"].items()},
          "beats:", len(record["contingent_beats"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
