"""SR-5r RF-3 "The AI enacts" — attribute the re-measured WO slice-9 and
slice-10 board pins to the one RF-3 lever.

    .venv/Scripts/python.exe tools/_rf3_wo_attribution.py

Runs the two files' own probes in hash-pinned children, exactly as their
runners do, twice: once as shipped, and once with
`backend.game_logic.reforms.THE_AI_ENACTS` set DOWN in the child before the
world boots (never a source edit). The claim the re-seated pins carry — "with
the RF-3 lever down in the child the VP-R1 figures return" — is what this
measures. Writes tools/_rf3_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RF3_DOWN = ("import backend.game_logic.reforms as _RF3\n"
            "_RF3.THE_AI_ENACTS = False\n")
RF3_FLIP = "backend.game_logic.reforms:THE_AI_ENACTS=False"


def spawn(probe: str, flags: str, marker: str, rf3_down: bool) -> dict:
    import tests.test_wo_slice10_enemy_direction_gate as T
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    code = "import sys\n" + T._LEVER_PRELUDE + (RF3_DOWN if rf3_down else "") + probe
    proc = subprocess.run([sys.executable, "-c", code, flags], env=env,
                          cwd=str(ROOT), capture_output=True, text=True,
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split(marker)[-1].splitlines()[0])


def rebellion(cap: bool, rf3_down: bool):
    import tests.test_wo_slice9_the_courting_cap as W9
    return W9._rebellion_turn(cap, (RF3_FLIP,) if rf3_down else ())


def main() -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    jobs = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for down in (False, True):
            jobs[("ambient_ungated", down)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "000", "WO10=", down)
            jobs[("ambient_gated", down)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "111", "WO10=", down)
            jobs[("cool_ungated", down)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "000", "WO10C=", down)
            jobs[("cool_gated", down)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "111", "WO10C=", down)
            jobs[("rebellion_uncapped", down)] = pool.submit(rebellion, False, down)
            jobs[("rebellion_capped", down)] = pool.submit(rebellion, True, down)
        out = {}
        for (name, down), fut in jobs.items():
            out.setdefault("rf3_down" if down else "shipped", {})[name] = fut.result()
    report = {}
    for arm, data in out.items():
        ungated = data["ambient_ungated"]
        seams: dict = {}
        for name, _q, _m in ungated["hits"]:
            seams[name] = seams.get(name, 0) + 1
        pairs = Counter((q, m) for _s, q, m in ungated["hits"])
        report[arm] = {
            "ungated_seams": seams,
            "ungated_pairs": {f"{q}->{m}": n for (q, m), n in sorted(pairs.items())},
            "ungated_series": ungated["series"],
            "gated_series": data["ambient_gated"]["series"],
            "gated_hits": data["ambient_gated"]["hits"],
            "cooldowns": {"ungated": data["cool_ungated"]["writes"],
                          "gated": data["cool_gated"]["writes"]},
            "rebellion": {"uncapped": data["rebellion_uncapped"],
                          "capped": data["rebellion_capped"]},
        }
        print(f"[{arm}] seams {seams}")
        print(f"[{arm}] pairs {report[arm]['ungated_pairs']}")
        print(f"[{arm}] ungated series {ungated['series']}")
        print(f"[{arm}] gated series   {report[arm]['gated_series']}")
        print(f"[{arm}] cooldowns {report[arm]['cooldowns']} rebellion {report[arm]['rebellion']}")
    (ROOT / "tools" / "_rf3_wo_attribution.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
