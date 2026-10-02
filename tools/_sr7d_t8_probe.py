"""SR-7d DC-2 — the T8 probe (DOCTRINES_SPEC §6 T8): per rival, on the four
ambient seeds, the turn its cure takes effect, which half of the purse test
held its Staff back until then, and every lapse — with the rung that saves
for the Staff UP (the shipped tree) and DOWN (the flip arm).

    .venv/Scripts/python.exe tools/_sr7d_t8_probe.py

Each arm runs in its own hash-pinned child on the ambient board (40 turns,
the M7 per-turn re-seed — the BASELINE_SERIES idiom). Writes
tools/_sr7d_t8_probe.json (committed with the landing record).

Pass (T8): no rival's flaw is cured before turn 10, and at least two of the
four have a cure in effect by turn 30 on the historical seed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ("historical", "ulm", "austerlitz", "eylau")
RIVALS = ("Austria", "Prussia", "Russia", "Britain")

CHILD = r"""
import sys, random, contextlib, io, json
sys.path.insert(0, {root!r})
RIVALS = {rivals!r}
import backend.game_logic.reforms as RF
RF.THE_AI_SAVES_FOR_THE_STAFF = {saves!r}
from backend.game_logic import doctrines as DC
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
SCEN = {scenario!r}
with contextlib.redirect_stdout(io.StringIO()):
    world = WorldState.from_scenario(SCEN)
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {{"world": world, "executor": executor}}
rec = {{n: {{"cured_turn": None, "held_by": [], "lapses": 0, "staff_turn": None,
            "cure_law_turn": None}} for n in RIVALS}}
was = {{n: False for n in RIVALS}}
for turn in range(40):
    random.seed(10_000 + turn)
    with contextlib.redirect_stdout(io.StringIO()):
        tm.end_turn(game_state)
    now = int(world.current_turn)
    for n in RIVALS:
        cured = DC.flaw_cured(world, n)
        if cured and not was[n]:
            rec[n]["cured_turn"] = now
        if was[n] and not cured:
            rec[n]["lapses"] += 1
        was[n] = cured
        staff = DC.staff_law(world, n)
        if staff is not None and RF.is_in_force(staff) and rec[n]["staff_turn"] is None:
            rec[n]["staff_turn"] = int(staff.get("enacted_turn"))
        law = DC.cure_law(world, n)
        if law is not None and RF.is_in_force(law) and rec[n]["cure_law_turn"] is None:
            rec[n]["cure_law_turn"] = int(law.get("enacted_turn"))
        if staff is not None and not RF.is_in_force(staff):
            why = RF.ai_purse_refusal(world, n, staff)
            half = ("chest" if why.startswith("the chest") else
                    "net" if why.startswith("the forecast Net") else
                    "authority" if why else "none")
            rec[n]["held_by"].append(half)
out = {{}}
for n in RIVALS:
    held = rec[n]["held_by"]
    out[n] = {{"cured_turn": rec[n]["cured_turn"], "staff_turn": rec[n]["staff_turn"],
              "cure_law_turn": rec[n]["cure_law_turn"], "lapses": rec[n]["lapses"],
              "held_by_chest": held.count("chest"), "held_by_net": held.count("net"),
              "held_by_authority": held.count("authority"), "turns_waiting": len(held)}}
print("T8=" + json.dumps(out))
"""


def run(seed: str, saves: bool) -> dict:
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), SOVEREIGN_SEED=seed, LLM_MODE="mock")
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = CHILD.format(root=str(ROOT), saves=saves, rivals=RIVALS,
                        scenario=str(ROOT / "godot-client" / "project-sovereign" / "assets"
                                     / "maps" / "europe_1805.json"))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"{seed} saves={saves} failed:\n{proc.stdout[-1500:]}\n{proc.stderr[-3000:]}")
    line = [ln for ln in proc.stdout.splitlines() if ln.startswith("T8=")][-1]
    return json.loads(line[3:])


def main() -> int:
    out = {"pass_rule": "no rival cured before turn 10; >= 2 of 4 cured by turn 30 on historical",
           "arms": {}}
    for saves in (True, False):
        for seed in SEEDS:
            key = f"{'saves' if saves else 'rung_as_rf3'}|{seed}"
            print(key, "...", flush=True)
            out["arms"][key] = run(seed, saves)
            print("  ", out["arms"][key], flush=True)
    hist = out["arms"]["saves|historical"]
    cured_by_30 = sum(1 for n in RIVALS if hist[n]["cured_turn"] is not None and hist[n]["cured_turn"] <= 30)
    before_10 = [n for key, arm in out["arms"].items() if key.startswith("saves|")
                 for n in RIVALS if arm[n]["cured_turn"] is not None and arm[n]["cured_turn"] < 10]
    out["t8"] = {"cured_by_30_on_historical": cured_by_30, "cured_before_10": before_10,
                 "pass": cured_by_30 >= 2 and not before_10}
    print("T8:", out["t8"])
    (ROOT / "tools" / "_sr7d_t8_probe.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
