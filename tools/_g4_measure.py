"""Session G4 — the open readings, ruled and built (DYNAMISM_SPEC.md §7d;
November 11, 2026): the session's ONE measure sweep, eleven arms on the three
gate surfaces (§2b rule 2: one switch a rule, one sweep a session). Each arm
raises one more seam, in this order:

    arm 0        the ten session-G4 seams down — MUST reproduce session
                 G3's records byte for byte (`_dy_signature_g3_2026_11_11.json`,
                 and arm CLIENT of `_g3_chain_d_2026_11_11.json`);
    arm FORM     + a nation is proclaimed on what it holds
                 (`formations.a_nation_is_proclaimed_on_what_it_holds`);
    arm WON      + an ally's soil is not won (`agendas.an_allys_soil_is_not_won`);
    arm LAPSE    + a pact lapses at the vassalage
                 (`vassal.a_pact_lapses_at_the_vassalage`);
    arm REAR     + a backer is no menace (`war_council.a_backer_is_no_menace`);
    arm CEILING  + a commission reads the arming ceiling
                 (`recruitment.a_commission_reads_the_arming_ceiling`);
    arm ALLY     + the Emperor's ally takes no separate peace
                 (`settlement_third_party.the_emperors_ally_takes_no_separate_peace`);
    arm GUNS     + no guns from a sanctuary
                 (`combat_executor.no_guns_from_a_sanctuary`);
    arm WAGON    + a bandwagoner joins a neighbour's war
                 (`war_council.a_bandwagoner_joins_a_neighbours_war`);
    arm HOUSE    + a client joins no war against a client of a house it is
                 at peace with — the treaty fuzzer's catch
                 (`diplomacy.a_client_joins_no_war_against_a_house_at_peace`);
    arm ALL      + the people drive out a foreign king
                 (`crowns.the_people_drive_out_a_foreign_king`) — the shipped
                 tree.

Per arm it runs the three instruments the Concert's sessions used, each a
chain of children under `INK_IRON_SEAMS` (the AU-2c hook), sequentially and
ALONE — no backend, test or deck edit lands while it runs:

  * the ten ambient `SWEEP_SEEDS` x 40 turns (`tools/_t3_4_measure.py`) — a
    DY signature record and a census per arm;
  * the AI-France harness, the ten seeds x 40 turns
    (`tools/_t3_5_chain_d.py --arms … --arm-seams …`) — ONE record holding
    the eleven arms;
  * the France band on the COMMANDED arms (the deploy gate's difficulty
    guard, 23–28): `score_run.ARMS` CMD-H / CMD-A / CMD-M, forty turns
    through `tools/playtest_driver.py`, each arm through the driver's own
    `--seam`; France's provinces on the last ledger row, into ONE record.

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.

    .venv/Scripts/python.exe tools/_g4_measure.py [--arms 0,FORM,…,ALL]
        [--surfaces ambient,d,band] [--stamp 2026_11_11]
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEAMS = {
    "FORM": "backend.game_logic.formations:a_nation_is_proclaimed_on_what_it_holds=False",
    "WON": "backend.game_logic.agendas:an_allys_soil_is_not_won=False",
    "LAPSE": "backend.game_logic.vassal:a_pact_lapses_at_the_vassalage=False",
    "REAR": "backend.game_logic.war_council:a_backer_is_no_menace=False",
    "CEILING": "backend.game_logic.recruitment:a_commission_reads_the_arming_ceiling=False",
    "ALLY": "backend.game_logic.settlement_third_party:the_emperors_ally_takes_no_separate_peace=False",
    "GUNS": "backend.commands.combat_executor:no_guns_from_a_sanctuary=False",
    "WAGON": "backend.game_logic.war_council:a_bandwagoner_joins_a_neighbours_war=False",
    "HOUSE": "backend.game_logic.diplomacy:a_client_joins_no_war_against_a_house_at_peace=False",
    "KING": "backend.game_logic.crowns:the_people_drive_out_a_foreign_king=False",
}
ORDER = tuple(SEAMS)


def _down_after(raised: int):
    """The seams still DOWN once the first `raised` of ORDER are up."""
    return [SEAMS[name] for name in ORDER[raised:]]


# arm -> (the seams held DOWN, the ambient records' label)
ARMS = {"0": (_down_after(0), "g4_control")}
for _i, _name in enumerate(ORDER[:-1], start=1):
    ARMS[_name] = (_down_after(_i), f"g4_{_name.lower()}")
ARMS["ALL"] = ([], "g4")


def _run(cmd, seams: str = "") -> None:
    env = dict(os.environ)
    env.pop("INK_IRON_SEAMS", None)
    if seams:
        env["INK_IRON_SEAMS"] = seams
    print("[g4]", " ".join(str(c) for c in cmd), f"(seams down: {seams or 'none'})", flush=True)
    rc = subprocess.run([sys.executable, *map(str, cmd)], cwd=str(ROOT), env=env).returncode
    if rc != 0:
        raise SystemExit(f"[g4] failed (rc {rc}): {cmd}")


BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")


def _band(arms, stamp: str) -> None:
    """The France band on the commanded arms: each arm's three driver runs
    side by side, France's provinces off the last `ledger` row."""
    import json
    from concurrent.futures import ThreadPoolExecutor

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / "g4_band"
    record = {"_note": ("Session G4 (the open readings, ruled and built) — the France band on the "
                        "commanded arms (DYNAMISM_SPEC.md §2: the deploy gate's difficulty guard, "
                        "23–28): score_run's CMD-H / CMD-A / CMD-M (commanded_full40.json, forty "
                        "turns, the mock parser) per arm — France's provinces on the last ledger "
                        "row; written by tools/_g4_measure.py --surfaces band (a chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams = [flag for spec in ARMS[arm][0] for flag in ("--seam", spec)]

        def _one(name, arms_dir=arms_dir, seams=seams, arm=arm):
            print(f"[g4] band {arm} {name} ...", flush=True)
            result = SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name]["argv"]) + seams)
            if result["exit"] != 0:
                raise SystemExit(f"[g4] band {arm} {name} failed: {result}")
            rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                    .read_text(encoding="utf-8").splitlines() if line.strip()]
            ledgers = [r for r in rows if r.get("kind") == "ledger"]
            turns = [r for r in rows if r.get("kind") == "turn"]
            return name, {"provinces": int(ledgers[-1]["provinces"]),
                          "turn": int(turns[-1]["turn"]) if turns else None,
                          "status": result["status"]}

        with ThreadPoolExecutor(max_workers=3) as pool:
            record["arms"][arm] = dict(pool.map(_one, BAND_ARMS))
        record["arms"][arm]["seams_down"] = list(ARMS[arm][0])
    out = ROOT / "tools" / f"_g4_band_{stamp}.json"
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[g4] band written {out}: "
          + str({a: {n: v['provinces'] for n, v in r.items() if n in BAND_ARMS}
                 for a, r in record['arms'].items()}), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--surfaces", default="ambient,d,band")
    ap.add_argument("--stamp", default="2026_11_11")
    ap.add_argument("--turns", type=int, default=40)
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    surfaces = set(args.surfaces.split(","))
    tools = ROOT / "tools"
    if "ambient" in surfaces:
        for arm in arms:
            down, label = ARMS[arm]
            _run([tools / "_t3_4_measure.py", "--turns", args.turns,
                  "--label", label.replace("_", "-"),
                  "--out", tools / f"_dy_signature_{label}_{args.stamp}.json",
                  "--census", tools / f"_{label}_census_{args.stamp}.json"],
                 seams=";".join(down))
    if "d" in surfaces:
        cmd = [tools / "_t3_5_chain_d.py", "--turns", args.turns, "--arms", ",".join(arms),
               "--out", tools / f"_g4_chain_d_{args.stamp}.json",
               "--run-dir", tools / "playtest_runs" / "g4_chain_d"]
        for arm in arms:
            if ARMS[arm][0]:
                cmd += ["--arm-seams", f"{arm}={';'.join(ARMS[arm][0])}"]
        _run(cmd)
    if "band" in surfaces:
        _band(arms, args.stamp)
    print("[g4] the sweep is written", flush=True)


if __name__ == "__main__":
    main()
