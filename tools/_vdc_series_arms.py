"""VD-C "The Contingent" + its riders + SR-8c — the BASELINE_SERIES
attribution (Score Finish Step 5, October 3, 2026).

The slice MOVES the series by design: on the ambient board the boot
satellites share France's war (Holland with Britain, the Kingdom of Italy
with Austria), so two contingents take the field on turn 2 — 14,000 men on
France's flag that Austria's council weighs. The series is re-recorded ONCE
from this script's ALL arm; arm 0 (every lever DOWN in the child before the
40-turn ambient sim boots, the slice-9 idiom, and the one DATA change — the
`ostfriesland` deck entry — stripped from the booted world) must reproduce
the recorded series byte for byte. Each lever is measured ALONE (on top of
arm 0) and LEFT OUT (from ALL), and the reach of each is COUNTED in the
child, so a byte-identical arm says why.

    python tools/_vdc_series_arms.py [--arms 0,ALL,...]

Writes tools/_vdc_series_arms_final.json (committed with the landing record).
Run with --prior <the SF-LB-2b series> once BASELINE_SERIES is re-recorded
(the default reads the recorded constant).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

LEVERS = {
    "C": ("backend.game_logic.contingent", "THE_CLIENT_SENDS_ITS_CONTINGENT"),
    "P": ("backend.game_logic.contingent", "THE_CLIENT_PAYS_ITS_MEN"),
    "G": ("backend.game_logic.vassal", "A_CLIENTS_OWN_MEN_ARE_NOT_THE_LORDS_GARRISON"),
    "W": ("backend.game_logic.vassal", "THREATS_WALK_EVERY_LORD"),
    "H": ("backend.game_logic.vassal", "THE_HINT_RIDES_THE_TURN"),
    "B": ("backend.game_logic.emergent_designs", "A_CLIENTS_PARTITION_IS_THE_HEGEMONS"),
    "R": ("backend.game_logic.contingent", "A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL"),
}
DATA = ("D",)   # the ostfriesland deck entry (IQ7-D3), stripped in the child when down
ALL_KEYS = set(LEVERS) | set(DATA)
ARMS = {"0": set(), "ALL": set(ALL_KEYS)}
for key in sorted(ALL_KEYS):
    ARMS[f"only_{key}"] = {key}
    ARMS[f"all_but_{key}"] = set(ALL_KEYS) - {key}

CHILD = r"""
import sys, runpy, atexit, collections, importlib
UP = set({up!r})
ALL = {all_levers!r}
for key, (mod_name, name) in ALL.items():
    mod = importlib.import_module(mod_name)
    setattr(mod, name, key in UP)
import backend.models.world_state as WSM
_c = collections.Counter()
_o_boot = WSM.WorldState.from_scenario.__func__
def _boot(cls, *a, **k):
    w = _o_boot(cls, *a, **k)
    if "D" not in UP:
        deck = (w.agendas or {{}}).get("Holland") or []
        w.agendas["Holland"] = [e for e in deck if e.get("id") != "ostfriesland"]
    return w
WSM.WorldState.from_scenario = classmethod(_boot)
import backend.game_logic.contingent as CG
_o_pass = CG.process_vassal_contingents
def _pass(world):
    out = _o_pass(world)
    for e in out:
        _c["contingent|" + str(e.get("beat")) + "|" + str(e.get("vassal"))] += 1
    return out
CG.process_vassal_contingents = _pass
import backend.game_logic.vassal as V
_o_court = V.attempt_vassal_courting
def _court(world, nation):
    out = _o_court(world, nation)
    for e in out:
        if e.get("lord") != getattr(world, "player_nation", "France"):
            _c["courting_ai_lord|" + str(e.get("vassal"))] += 1
    return out
V.attempt_vassal_courting = _court
_o_cascade = V.check_defection_cascade
def _cascade(world):
    out = _o_cascade(world)
    for e in out:
        if e.get("lord") != getattr(world, "player_nation", "France"):
            _c["cascade_ai_lord|" + str(e.get("vassal"))] += 1
    return out
V.check_defection_cascade = _cascade
_o_garrison = V.lord_garrison_present
def _garrison(world, lord, capital):
    out = _o_garrison(world, lord, capital)
    if out:
        _c["garrison_term|" + str(capital)] += 1
    return out
V.lord_garrison_present = _garrison
import backend.game_logic.emergent_designs as ED
_o_volte = ED.volte_face_failing_clauses
def _volte(world, power, hegemon, **k):
    out = _o_volte(world, power, hegemon, **k)
    if out and out[0] in (ED.VOLTE_CLAUSE_PUNITIVE, ED.VOLTE_CLAUSE_REVANCHE):
        _c["volte_foreclosed|" + str(power) + "|" + str(out[0])] += 1
    return out
ED.volte_face_failing_clauses = _volte
_o_client = CG.is_clients_general
def _client(marshal):
    out = _o_client(marshal)
    if out:
        _c["clients_general|" + str(getattr(marshal, "name", ""))] += 1
    return out
CG.is_clients_general = _client
def _dump():
    print("VDC=" + repr(dict(_c)))
atexit.register(_dump)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def run_arm(up: set) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(k, None)
    code = CHILD.format(up=sorted(up), all_levers=LEVERS, runner=str(RUNNER))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"arm failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    lines = proc.stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    counts = [ln for ln in lines if ln.startswith("VDC=")]
    payload["vdc"] = ast.literal_eval(counts[-1].split("=", 1)[1]) if counts else None
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def recorded_series() -> list:
    src = RUNNER.read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--prior", default="", help="JSON list: the pre-slice series (default: the recorded constant)")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_vdc_series_arms_final.json"))
    args = ap.parse_args()
    prior = json.loads(args.prior) if args.prior else recorded_series()
    out = {"prior": prior,
           "levers": {k: f"{m}.{n}" for k, (m, n) in LEVERS.items()},
           "data": {"D": "europe_1805.json agendas.Holland 'ostfriesland' (IQ7-D3)"},
           "arm_levers": {k: sorted(v) for k, v in ARMS.items()}, "arms": {}}
    for arm in [x.strip() for x in args.arms.split(",") if x.strip()]:
        up = ARMS[arm]
        print(f"arm {arm} (up: {sorted(up) or 'none'}) ...", flush=True)
        payload = run_arm(up)
        series = payload["series"]
        out["arms"][arm] = {
            "levers_up": sorted(up), "series": series,
            "first_divergence_vs_prior": first_divergence(series, prior),
            "provinces": payload.get("provinces"),
            "reach": payload.get("vdc"),
        }
        print(f"   divergence vs prior: {out['arms'][arm]['first_divergence_vs_prior']}",
              flush=True)
    if "ALL" in out["arms"]:
        for arm, rec in out["arms"].items():
            rec["first_divergence_vs_all"] = first_divergence(
                rec["series"], out["arms"]["ALL"]["series"])
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
