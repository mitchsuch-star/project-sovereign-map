"""SF-CL-1 "The forecast keeps its word" — the census (October 3, 2026;
SCORE_FINISH_SPEC.md §3 Step 4).

Reads the `forecast` rows the playtest driver's ForecastLedger writes to each
arm's digest.jsonl (prediction beside commitment, one row per surface) and
reports every divergence class:

    .venv/Scripts/python.exe tools/forecast_census.py docs/audits/score_runs/<run>/arms
    .venv/Scripts/python.exe tools/forecast_census.py <run>/arms --json out.json

Classes (each a sentence the game said and what the resolver then did):
  expected_miss        every promised corps fought and the battle's massed
                       effective strength still fell outside
                       [EXPECTED_FLOOR × "expect about X", "up to Y"] — the
                       muster's own arithmetic, a lie
  shortfall_from_absences  the figure missed because a promised corps did not
                       fight (its reason and the odds the row quoted beside it)
                       — the die the row priced, not a lie
  solo_mismatch        no WILL JOIN row, yet the massed strength was not the
                       lead's own
  unpromised_arrival   a corps the muster said WILL NOT fought anyway
  promised_absent      a WILL JOIN corps that did not fight (informational —
                       the preview quotes arrival ODDS, so a no-show is the
                       die, not a lie; the rate is reported beside the odds)
  band_disagreement    an objection or a bad-odds interrupt named a band and
                       the muster that followed named another
  scout_vs_assault     a scout named a garrison and an assault on that
                       province within SCOUT_WINDOW turns met a different one
                       (regen allowed — CAPITAL_GARRISON_REGEN_PER_TURN × turns)
  band_inversion       the C2 read: per band, how often the attacker out-bled
                       the defender
Exit code 0 always — the census is a measurement; its pins live in
tests/test_sf_cl1_the_forecast_keeps_its_word.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_FLOOR = 0.80
SCOUT_WINDOW = 4


def _rows(arms_dir: Path):
    for jsonl in sorted(Path(arms_dir).glob("*/digest.jsonl")):
        arm = jsonl.parent.name
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("kind") == "forecast":
                row["_arm"] = arm
                yield row


def census(arms_dir: Path, regen_per_turn: int = 0) -> dict:
    rows = list(_rows(arms_dir))
    out = {
        "rows": len(rows),
        "by_family": dict(Counter(r.get("family") for r in rows)),
        "expected_miss": [], "shortfall_from_absences": [], "solo_mismatch": [], "unpromised_arrival": [],
        "promised_absent": [], "band_disagreement": [], "scout_vs_assault": [],
        "band_inversion": {}, "promise_rate": None,
    }
    musters = [r for r in rows if r.get("family") == "muster"]
    battles = [r for r in musters if isinstance(r.get("committed"), dict)
               and r["committed"].get("total") is not None]
    promised = arrived_n = 0
    bands = defaultdict(list)
    for r in battles:
        p, c = r["predicted"], r["committed"]
        exp, ceil, total = int(p["expected"]), int(p.get("ceiling") or p["expected"]), int(c["total"])
        tag = f"{r['_arm']} t{r.get('turn')} {p.get('lead_name')}→{p.get('target')}"
        wj = set(p.get("will_join") or [])
        fought = set(c.get("arrived") or [])
        if wj:
            if total < EXPECTED_FLOOR * exp or total > max(ceil, exp):
                entry = {"where": tag, "expected": exp, "ceiling": ceil, "total": total}
                if wj <= fought:
                    # every promised corps fought and the figure still missed:
                    # the muster's arithmetic, not the die
                    out["expected_miss"].append(entry)
                else:
                    entry["absent"] = sorted(wj - fought)
                    entry["quoted_odds"] = {n: (p.get("arrival_odds") or {}).get(n)
                                            for n in sorted(wj - fought)}
                    out["shortfall_from_absences"].append(entry)
        elif total != int(p["lead"]):
            # A coordinated battle the muster read as solo (no WILL JOIN row)
            # whose massed strength was not the lead's own — a corps the
            # preview never listed carried weight.
            out["solo_mismatch"].append({"where": tag, "lead": int(p["lead"]), "total": total})
        wn = set(p.get("will_not") or [])
        arrived = fought
        for name in sorted(arrived & wn):
            out["unpromised_arrival"].append({"where": tag, "marshal": name})
        promised += len(wj)
        arrived_n += len(wj & arrived)
        for name in sorted(wj - arrived):
            status = next((s for n, s in (c.get("absent") or []) if n == name), "unlisted")
            out["promised_absent"].append({"where": tag, "marshal": name, "status": status})
        if p.get("band") and c.get("own_losses") is not None and c.get("enemy_losses") is not None:
            bands[p["band"]].append(int(c["own_losses"]) < int(c["enemy_losses"]))
    out["promise_rate"] = (round(arrived_n / promised, 3) if promised else None, arrived_n, promised)
    out["band_inversion"] = {b: {"out_bled": sum(v), "battles": len(v),
                                 "rate": round(sum(v) / len(v), 2) if v else None}
                             for b, v in sorted(bands.items())}
    # band_disagreement: objection / interrupt rows vs the next muster of the
    # same arm, turn, marshal and target.
    judged = [r for r in rows if r.get("family") in ("objection", "interrupt") and r.get("band")]
    for j in judged:
        follow = next((m for m in musters
                       if m["_arm"] == j["_arm"] and m.get("turn") == j.get("turn")
                       and m["predicted"].get("lead_name") == j.get("marshal")
                       and (not j.get("target") or m["predicted"].get("target") == j.get("target"))
                       and m.get("seq", 0) > j.get("seq", 0)), None)
        if follow and follow["predicted"].get("band") and follow["predicted"]["band"] != j["band"]:
            out["band_disagreement"].append({
                "where": f"{j['_arm']} t{j.get('turn')} {j.get('marshal')}→{j.get('target')}",
                "family": j["family"], "said": j["band"], "muster": follow["predicted"]["band"]})
    # scout_vs_assault
    scouts = [r for r in rows if r.get("family") == "scout" and r.get("garrison") is not None]
    assaults = [r for r in rows if r.get("family") == "garrison_assault"]
    for s in scouts:
        for a in assaults:
            if (a["_arm"] == s["_arm"] and a.get("region") == s.get("region")
                    and 0 <= int(a.get("turn", 0)) - int(s.get("turn", 0)) <= SCOUT_WINDOW):
                gap = int(a.get("turn", 0)) - int(s.get("turn", 0))
                allowed = regen_per_turn * gap
                if abs(int(a["garrison_before"]) - int(s["garrison"])) > allowed:
                    out["scout_vs_assault"].append({
                        "where": f"{s['_arm']} t{s.get('turn')}→t{a.get('turn')} {s.get('region')}",
                        "scouted": int(s["garrison"]), "met": int(a["garrison_before"]),
                        "allowed_regen": allowed})
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arms_dir")
    ap.add_argument("--json")
    ap.add_argument("--regen", type=int, default=None,
                    help="garrison regen per turn allowed between a scout and an assault "
                         "(default: the engine's CAPITAL_GARRISON_REGEN_PER_TURN)")
    args = ap.parse_args()
    regen = args.regen
    if regen is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from backend.models.world_state import CAPITAL_GARRISON_REGEN_PER_TURN
            regen = int(CAPITAL_GARRISON_REGEN_PER_TURN)
        except Exception:  # noqa: BLE001
            regen = 0
    out = census(Path(args.arms_dir), regen)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"forecast rows: {out['rows']} {out['by_family']}")
    for key in ("expected_miss", "shortfall_from_absences", "solo_mismatch", "unpromised_arrival",
                "band_disagreement", "scout_vs_assault"):
        print(f"{key}: {len(out[key])}")
        for item in out[key][:12]:
            print("   ", item)
    print(f"promised_absent: {len(out['promised_absent'])} (promise rate {out['promise_rate']})")
    for item in out["promised_absent"][:8]:
        print("   ", item)
    print("band_inversion:", out["band_inversion"])
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
