"""Row IC, Session 2b — the task to prove himself: the measure
(INDEPENDENT_COMMAND_SPEC.md §13 "R-INERT", its ONE exception; November 20, 2026).

Session 2b replaces the trust crisis's "Grant Autonomy" with a task to prove
himself and removes the old engine. R-INERT's one written exception is the
audience: a run whose driver answered an audience with the old default answers
it with the task now, so such a run may move. Two arms:

    BAND      score_run's CMD-H / CMD-A / CMD-M (commanded_full40.json, forty
              turns, the mock parser) as they stand — the deploy gate's
              difficulty guard (DYNAMISM_SPEC.md §2: France holds 23–28
              provinces at turn 40). Read per seed: the provinces, and whether a
              trust crisis came up at all (the digest's `POPUP redemption`
              rows). The standing reading is 26 / 27 / 28 with no crisis on any
              seed (`tools/_ic2_band_2026_11_20.json`).
    AUDIENCE  the PROVOKING script (score_run's DRAMA arm:
              commanded_provoke40.json under `--objection insist`, the one that
              drives trust down) on the same three seeds, the audience answered
              with `--answer` (default: the driver's own default). This is the
              arm that meets the audience; it is read, never gated — no gate
              reads the provoking script.

Run it twice to compare: on the tree BEFORE the change with
`--answer grant_autonomy --tag before`, and on the tree after with `--tag after`
(the driver's default is then the task). Run ALONE — no backend, test or deck
edit lands while it runs.

    .venv/Scripts/python.exe tools/_ic2b_measure.py [--arms BAND,AUDIENCE]
        [--answer ""] [--tag after] [--stamp 2026_11_20] [--jobs 3]

THIS PARENT RUNS PLAIN (never `-X utf8`): the children print cp1252.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
STANDING = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}      # _ic2_band_2026_11_20.json, arm ALL
SEEDS = {"H": "historical", "A": "austerlitz", "M": "marengo"}
# The lines of a digest that tell what a man did while out of the player's hands.
TELLING = re.compile(r"prove himself|on a roll|acted without orders|INDEPENDENT COMMAND|"
                     r"AUTONOMY|acts on his own|under your orders again", re.IGNORECASE)


def _strip(argv, flag):
    """`argv` without `flag` and its value."""
    out, skip = [], False
    for item in argv:
        if skip:
            skip = False
            continue
        if item == flag:
            skip = True
            continue
        out.append(item)
    return out


def _read(arms_dir: pathlib.Path, name: str, result: dict) -> dict:
    rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
            .read_text(encoding="utf-8").splitlines() if line.strip()]
    ledgers = [r for r in rows if r.get("kind") == "ledger"]
    turns = [r for r in rows if r.get("kind") == "turn"]
    crises, turn = [], None
    for row in rows:
        if row.get("kind") == "turn":
            turn = row.get("turn")
        elif row.get("kind") == "popup" and row.get("key") == "redemption":
            crises.append({"turn": turn, "who": row.get("summary"), "answer": row.get("answer")})
    digest = arms_dir / name / "digest.md"
    told = []
    if digest.is_file():
        for line in digest.read_text(encoding="utf-8", errors="replace").splitlines():
            if TELLING.search(line):
                told.append(line.strip()[:220])
    return {"provinces": int(ledgers[-1]["provinces"]) if ledgers else None,
            "turn": int(turns[-1]["turn"]) if turns else None,
            "status": result["status"], "trust_crises": len(crises),
            "crises": crises, "told": told[:40]}


def measure(arms, answer: str, jobs: int, tag: str) -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / f"ic2b_{tag}"
    record = {"_note": ("Row IC, Session 2b (the task to prove himself) — arm BAND: the France band on "
                        "the commanded arms (DYNAMISM_SPEC.md §2, 23–28): score_run's CMD-H / CMD-A / "
                        "CMD-M per seed, and the trust crises that came up; arm AUDIENCE: the provoking "
                        "script (score_run's DRAMA arm) on the same seeds with the audience answered by "
                        "`answer` ('' = the driver's own default) — read, never gated. Written by "
                        "tools/_ic2b_measure.py (a chain run ALONE)."),
              "band": list(BAND), "standing": dict(STANDING), "answer": answer, "tag": tag, "arms": {}}

    def _run(arms_dir, name, argv):
        print(f"[ic2b] {tag} {name} ...", flush=True)
        result = SR._run_driver(ROOT, arms_dir, name, argv)
        if result["exit"] != 0:
            raise SystemExit(f"[ic2b] {name} failed: {result}")
        return name, _read(arms_dir, name, result)

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = {}
        for arm in arms:
            arms_dir = run_dir / arm
            arms_dir.mkdir(parents=True, exist_ok=True)
            if arm == "BAND":
                futures[arm] = [pool.submit(_run, arms_dir, name, list(SR.ARMS[name]["argv"]))
                                for name in BAND_ARMS]
            elif arm == "AUDIENCE":
                base = _strip(_strip(list(SR.ARMS["DRAMA"]["argv"]), "--redemption"), "--seed")
                extra = ["--redemption", answer] if answer else []
                futures[arm] = [pool.submit(_run, arms_dir, f"AUD-{key}",
                                            base + ["--seed", seed] + extra)
                                for key, seed in SEEDS.items()]
            else:
                raise SystemExit(f"[ic2b] no such arm: {arm}")
        for arm, jobs_ in futures.items():
            record["arms"][arm] = dict(f.result() for f in jobs_)
    if "BAND" in record["arms"]:
        band = record["arms"]["BAND"]
        record["band_holds"] = all(BAND[0] <= band[n]["provinces"] <= BAND[1] for n in BAND_ARMS)
        record["band_is_the_standing_reading"] = all(
            band[n]["provinces"] == STANDING[n] for n in BAND_ARMS)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="BAND,AUDIENCE")
    ap.add_argument("--answer", default="", help="the audience's answer on arm AUDIENCE ('' = the driver's default)")
    ap.add_argument("--tag", default="after", help="before | after — names the record and the run folder")
    ap.add_argument("--stamp", default="2026_11_20")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default="", help="the record's path (default: tools/_ic2b_<tag>_<stamp>.json)")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    record = measure(arms, args.answer, args.jobs, args.tag)
    out = (pathlib.Path(args.out) if args.out
           else ROOT / "tools" / f"_ic2b_{args.tag}_{args.stamp}.json")
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ic2b] written {out}: "
          + str({a: {n: (v["provinces"], v["trust_crises"]) for n, v in r.items()}
                 for a, r in record["arms"].items()}), flush=True)


if __name__ == "__main__":
    main()
