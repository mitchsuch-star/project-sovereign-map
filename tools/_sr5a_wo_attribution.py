"""SR-5a "The chest" — attribute the re-measured WO slice-9 and slice-10 board
pins to the ruled balance package (the tools/_rf3_wo_attribution.py pattern).

    .venv/Scripts/python.exe tools/_sr5a_wo_attribution.py

Runs the two files' own probes in hash-pinned children, exactly as their
runners do, twice: once on the shipped scenario, and once with the PRE-SLICE
scenario swapped in the child (`WorldState.from_scenario` wrapped before the
world boots; the shipped file is never written). The claim the re-seated pins
carry — "on the pre-slice scenario the drill-fix figures return" — is what
this measures. Writes tools/_sr5a_wo_attribution.json.
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

import _sr5a_series_arms as ARMS  # noqa: E402

SWAP = r"""
from backend.models.world_state import WorldState as _WS
_orig_fs = _WS.from_scenario.__func__
def _swap_fs(cls, path, seed=None):
    if str(path).replace("\\", "/").endswith("europe_1805.json"):
        path = {prior!r}
    return _orig_fs(cls, path, seed=seed)
_WS.from_scenario = classmethod(_swap_fs)
"""


def child_env() -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT),
               SOVEREIGN_SEED="historical", LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    return env


def spawn(probe: str, flags: str, marker: str, prior: str | None) -> dict:
    import tests.test_wo_slice10_enemy_direction_gate as T
    code = "import sys\n" + T._LEVER_PRELUDE + (
        SWAP.format(prior=prior) if prior else "") + probe
    proc = subprocess.run([sys.executable, "-c", code, flags], env=child_env(),
                          cwd=str(ROOT), capture_output=True, text=True,
                          timeout=1800)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads(proc.stdout.split(marker)[-1].splitlines()[0])


def rebellion(cap: bool, prior: str | None):
    """`_rebellion_turn`, with the scenario it boots made a parameter."""
    import tests.test_wo_slice9_the_courting_cap as W9
    scenario = prior or str(ARMS.SCENARIO)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as handle:
        handle.write(W9._REBELLION_RUNNER)
        script = handle.name
    try:
        result = subprocess.run(
            [sys.executable, script, str(ROOT), scenario, "1" if cap else "0"],
            env=child_env(), cwd=str(ROOT), capture_output=True, text=True,
            timeout=600)
    finally:
        os.unlink(script)
    assert result.returncode == 0, result.stderr[-2000:]
    line = [ln for ln in result.stderr.splitlines()
            if ln.startswith("REBELLION=")][-1]
    raw = line[len("REBELLION="):]
    return None if raw == "None" else int(raw)


def main() -> int:
    import tests.test_wo_slice10_enemy_direction_gate as T
    prior = ARMS.write_variant("wo_prior", False, False)
    jobs = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for arm, scen in (("shipped", None), ("pre_slice", prior)):
            jobs[("ambient_ungated", arm)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "000", "WO10=", scen)
            jobs[("ambient_gated", arm)] = pool.submit(
                spawn, T._AMBIENT_PROBE, "111", "WO10=", scen)
            jobs[("cool_ungated", arm)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "000", "WO10C=", scen)
            jobs[("cool_gated", arm)] = pool.submit(
                spawn, T._COOLDOWN_PROBE, "111", "WO10C=", scen)
            jobs[("rebellion_uncapped", arm)] = pool.submit(rebellion, False, scen)
            jobs[("rebellion_capped", arm)] = pool.submit(rebellion, True, scen)
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
    (ROOT / "tools" / "_sr5a_wo_attribution.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
