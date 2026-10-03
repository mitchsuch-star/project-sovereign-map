"""SF-LB-2 "The Defenceless Prize" — attribute the re-measured WO slice-9
and slice-10 board pins to the slice's levers (the
tools/_sr7d_wo_attribution.py pattern, one more link in the chain).

    .venv/Scripts/python.exe tools/_sf_lb2_wo_attribution.py

Runs the two files' own probes in hash-pinned children, exactly as their
runners do, twice: once on the shipped tree, and once with EVERY SF-LB-2
lever set DOWN in the child before the world boots (the slice-9 idiom; the
source is never written). The claim the re-seated pins carry — "with the
SF-LB-2 levers down the SR-7d figures return" — is what this measures.
Writes tools/_sf_lb2_wo_attribution.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import _sf_lb2_series_arms as ARMS  # noqa: E402

LEVERS_DOWN = "\n".join(
    f"import {mod} as _m_{i}\nsetattr(_m_{i}, {name!r}, False)"
    for i, (mod, name) in enumerate(ARMS.LEVERS.values())
) + "\n"
FLIPS = [f"{mod}:{name}=0" for mod, name in ARMS.LEVERS.values()]


def child_env() -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    return env


def spawn(probe: str, flags: str, marker: str, down: bool) -> dict:
    import tests.test_wo_slice10_enemy_direction_gate as T
    code = "import sys\n" + T._LEVER_PRELUDE + (LEVERS_DOWN if down else "") + probe
    proc = subprocess.run([sys.executable, "-c", code, flags], env=child_env(),
                          cwd=str(ROOT), capture_output=True, text=True,
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split(marker)[-1].splitlines()[0])


def rebellion(cap: bool, down: bool):
    """`_rebellion_turn`, with the SF-LB-2 levers made a parameter."""
    import tests.test_wo_slice9_the_courting_cap as W9
    scenario = str(ROOT / "godot-client" / "project-sovereign" / "assets"
                   / "maps" / "europe_1805.json")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as handle:
        handle.write(W9._REBELLION_RUNNER)
        script = handle.name
    try:
        result = subprocess.run(
            [sys.executable, script, str(ROOT), scenario, "1" if cap else "0",
             *(FLIPS if down else [])],
            env=child_env(), cwd=str(ROOT), capture_output=True, text=True,
            timeout=900)
    finally:
        os.unlink(script)
    assert result.returncode == 0, result.stderr[-2000:]
    line = [ln for ln in result.stderr.splitlines()
            if ln.startswith("REBELLION=")][-1]
    raw = line[len("REBELLION="):]
    return None if raw == "None" else int(raw)


def main() -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    jobs = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for arm, down in (("shipped", False), ("levers_down", True)):
            jobs[("ambient_ungated", arm)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "000", "WO10=", down)
            jobs[("ambient_gated", arm)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "111", "WO10=", down)
            jobs[("cool_ungated", arm)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "000", "WO10C=", down)
            jobs[("cool_gated", arm)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "111", "WO10C=", down)
            jobs[("rebellion_uncapped", arm)] = pool.submit(rebellion, False, down)
            jobs[("rebellion_capped", arm)] = pool.submit(rebellion, True, down)
        out: dict = {}
        for (name, arm), fut in jobs.items():
            out.setdefault(arm, {})[name] = fut.result()
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
    (ROOT / "tools" / "_sf_lb2_wo_attribution.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
