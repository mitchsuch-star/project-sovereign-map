"""The economy gate (October 5, 2026) — attribute the reading's falls.

    .venv/Scripts/python.exe tools/_econ_gate_exit_attribution.py

The gate's reading (`docs/audits/score_runs/2026_10_05_econ_gate/`) flips
items against the economy audit's v1.1 reading. This re-runs the arms those
items read (DL, DESC and the three commanded seeds) under three variants —
every gate lever DOWN, campaign pay alone down, the lawful road alone down —
each with the instrument's own argv plus the driver's `--lever` flags, checks
each variant with the instrument's own readers, and writes
tools/_econ_gate_exit_attribution.json and the per-variant run dirs under
docs/audits/score_runs/2026_10_05_econ_gate/attribution/.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import score_run as S  # noqa: E402
import _econ_gate_series_arms as ARMS  # noqa: E402

OUT = ROOT / "docs" / "audits" / "score_runs" / "2026_10_05_econ_gate" / "attribution"
GATE = [f"{m}:{n}=0" for m, n in ARMS.LEVERS.values()] + [
    "backend.display_names:THE_ORDER_NAMES_ITS_TARGET=0",
    "backend.game_logic.dispatch:THE_LEAGUES_NEWS_RIDES_BENEATH=0",
]
VARIANTS = {
    "all_gate_levers_down": GATE,
    "campaign_pay_down": ["backend.models.world_state:CAMPAIGN_PAY_ON_FOREIGN_SOIL=0"],
    "lawful_road_down": ["backend.ai.enemy_ai:THE_MARCH_READS_THE_LAWFUL_ROAD=0"],
}
RUN_ARMS = ("DL", "DESC", "CMD-H", "CMD-M", "CMD-A")
ITEMS = ("first_contact.C4", "naval.C3", "narration.C4", "combat_legibility.C3",
         "ai_aliveness.C6", "economy.C1", "living_balance.F1", "narration.C1",
         "ai_aliveness.C1")


def env() -> dict:
    e = dict(os.environ, PYTHONHASHSEED="0", LLM_MODE="mock", PYTHONIOENCODING="utf-8")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        e.pop(key, None)
    return e


def drive(variant: str, arm: str, levers: list) -> int:
    run = OUT / variant
    arms = run / "arms"
    arms.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, str(ROOT / "tools" / "playtest_driver.py"), "--name", arm,
            "--fresh", "--out", str(arms), "--llm", "mock"] + list(S.ARMS[arm]["argv"])
    for lever in levers:
        argv += ["--lever", lever]
    with (arms / f"{arm}.log").open("w", encoding="utf-8") as fh:
        return subprocess.run(argv, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT,
                              env=dict(env(), INK_IRON_SAVE_DIR=str(run / f"_saves_{arm}"))).returncode


def main() -> int:
    jobs = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for variant, levers in VARIANTS.items():
            for arm in RUN_ARMS:
                jobs.append(((variant, arm), pool.submit(drive, variant, arm, levers)))
        codes = {k: f.result() for k, f in jobs}
    report = {"levers": VARIANTS, "exits": {f"{v}/{a}": c for (v, a), c in codes.items()},
              "items": {}}
    for variant in VARIANTS:
        run = OUT / variant
        (run / "run.json").write_text(json.dumps({"arms": {a: {"arm": a} for a in RUN_ARMS}}),
                                      encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "tools" / "score_run.py"), "check", "--run",
                        str(run), "--checklist", str(ROOT / "docs" / "SCORE_CHECKLIST_V1_1.json")],
                       cwd=str(ROOT), env=env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
        checklist = json.loads((run / "checklist.json").read_text(encoding="utf-8"))
        flat = {}
        for key, pillar in checklist["pillars"].items():
            for item in pillar.get("items") or []:
                flat[f"{key}.{item['id']}"] = item
        report["items"][variant] = {
            k: {"measured": flat.get(k, {}).get("measured"),
                "pass": flat.get(k, {}).get("pass"),
                "evidence": str(flat.get(k, {}).get("evidence", ""))[:300]}
            for k in ITEMS}
        for k in ITEMS:
            it = report["items"][variant][k]
            mark = "·" if not it["measured"] else ("✓" if it["pass"] else "✗")
            print(f"[{variant}] {k} {mark} {it['evidence'][:150]}")
    (ROOT / "tools" / "_econ_gate_exit_attribution.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
