"""RR6-X3 "one sighting rule" (Pre-Deploy S14b's head, October 21, 2026) —
which of the slice's changes moved a commanded arm's GAME?

    python tools/_rr6_x3_arm_attribution.py child DOWN OUT_DIR -- <driver argv>
    python tools/_rr6_x3_arm_attribution.py run --out DIR [--arms CMD-H,FLD,...] [--jobs 4]

`child` runs `tools/playtest_driver.py` IN-PROCESS with the named changes held
down at their seams (DOWN is a comma list, or `none`), the pre-slice behaviour
restored exactly:

  rule  — `intel_surfaces.last_seen` answers from the store alone
          (`get_last_known_location`, the entry tree's order, gate and
          objection) and `record_shown_sightings` writes nothing;
  x8    — `WorldState.get_visible_enemies_in_region` reads a STALE province's
          live occupants again (the entry tree's attack quotes, closed-soil
          march and SUPPORT safety).

`run` drives every arm three ways — all down, `rule` down alone, `x8` down
alone — beside the shipped tree's own `score_run.py run` arms, and prints the
first turn each GAME stream (`tools/_sf_rr6_arm_attribution.stream`) parts
from the entry archive (`docs/audits/score_runs/2026_10_21_rr6/slice`). An
all-down arm equal to the entry archive proves the slice's game moves are its
seams' and nobody else's; the single-seam arms name which.

The display changes (the dispatch's live rows at PARTIAL, the map's STALE
ghosts, the status report, the desk's wording) never reach a GAME stream.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENTRY = ROOT / "docs" / "audits" / "score_runs" / "2026_10_21_rr6" / "slice"
ARMS = ("CMD-H", "CMD-A", "CMD-M", "OP", "FLD", "DL", "LAW", "VOLTE")
CONFIGS = {"all_down": "rule,x8", "rule_down": "rule", "x8_down": "x8"}


def _hold_down(down: set) -> None:
    if "rule" in down:
        from backend.game_logic import intel_surfaces as IS

        def _store_only(world, viewer, name):
            known = world.get_last_known_location(name) if name else None
            if not known:
                return None
            return {"location": known[0], "intel_turn": known[1],
                    "visibility": known[2], "source": "snapshot"}

        IS.last_seen = _store_only
        IS.record_shown_sightings = lambda world, shown: 0
    if "x8" in down:
        from backend.models import world_state as WS
        from backend.models.intel import FULL, PARTIAL, STALE, get_strength_band

        def _entry_rule(self, region_name, nation):
            intel = self.get_region_intel(region_name)
            if intel.visibility == FULL:
                return self.get_enemies_in_region(region_name, nation)
            if intel.visibility in (PARTIAL, STALE):
                return [{"name": m.name, "nation": m.nation,
                         "strength_band": get_strength_band(m.strength),
                         "fog_level": intel.visibility}
                        for m in self.get_enemies_in_region(region_name, nation)]
            return []

        WS.WorldState.get_visible_enemies_in_region = _entry_rule


def child(down_spec: str, argv: list) -> int:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "tools"))
    down = set() if down_spec in ("", "none") else set(down_spec.split(","))
    _hold_down(down)
    import playtest_driver as PD
    sys.argv = ["playtest_driver.py"] + argv
    try:
        PD.main()
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


def _argv_of(arm: str, out: pathlib.Path) -> list:
    rec = json.loads((ENTRY / "run.json").read_text(encoding="utf-8"))["arms"][arm]["cmd"]
    argv = list(rec)
    argv[argv.index("--out") + 1] = str(out)
    return argv


def run(out_dir: pathlib.Path, arms, jobs: int) -> dict:
    env = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock", PYTHONIOENCODING="utf-8")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START",
                "SOVEREIGN_SEED", "PYTHONDONTWRITEBYTECODE"):
        env.pop(key, None)
    jobs_list = []
    for cfg, spec in CONFIGS.items():
        for arm in arms:
            target = out_dir / cfg / "arms"
            target.mkdir(parents=True, exist_ok=True)
            jobs_list.append((cfg, spec, arm, target))

    def _one(job):
        cfg, spec, arm, target = job
        argv = [sys.executable, str(pathlib.Path(__file__).resolve()), "child", spec,
                str(target), "--"] + _argv_of(arm, target)
        saves = out_dir / cfg / f"_saves_{arm}"
        p = subprocess.run(argv, cwd=str(ROOT), env=dict(env, INK_IRON_SAVE_DIR=str(saves)),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2400)
        return cfg, arm, p.returncode

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        codes = list(pool.map(_one, jobs_list))
    return {f"{c}/{a}": rc for c, a, rc in codes}


def compare(out_dir: pathlib.Path, shipped: pathlib.Path, arms) -> dict:
    sys.path.insert(0, str(ROOT))
    from tools import score_run as SR
    from tools._sf_rr6_arm_attribution import first_parting, stream
    entry = SR.load_arms(ENTRY)
    runs = {"shipped": SR.load_arms(shipped)}
    for cfg in CONFIGS:
        runs[cfg] = SR.load_arms(out_dir / cfg)
    result = {}
    for arm in arms:
        result[arm] = {}
        for name, loaded in runs.items():
            if arm not in loaded or arm not in entry:
                result[arm][name] = "missing"
                continue
            p = first_parting(stream(entry[arm], "game"), stream(loaded[arm], "game"))
            result[arm][name] = ("equal" if p is None else
                                 f"parts at turn {p[0]}: {str(p[1])[:140]} | {str(p[2])[:140]}")
    return result


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "child":
        down, _out, sep = sys.argv[2], sys.argv[3], sys.argv[4]
        assert sep == "--"
        return child(down, sys.argv[5:])
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--shipped", required=True,
                   help="a `score_run.py run` of the same arms on the shipped tree")
    r.add_argument("--arms", default=",".join(ARMS))
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--record", default="")
    args = ap.parse_args()
    out_dir = pathlib.Path(args.out)
    arms = [a for a in args.arms.split(",") if a]
    codes = run(out_dir, arms, args.jobs)
    result = {"exit": codes, "game_vs_entry": compare(out_dir, pathlib.Path(args.shipped), arms)}
    for arm, row in result["game_vs_entry"].items():
        for name, verdict in row.items():
            print(f"{arm:6s} {name:10s} {verdict}")
    if args.record:
        pathlib.Path(args.record).write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
