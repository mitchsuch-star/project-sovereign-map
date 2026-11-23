"""Row IC, Session 4b, continued (November 23, 2026) — the user's "fix warplans":
does a minor rise as often with the war plans up as with them down, on a sample
wide enough to tell a cause from chance?

WHY. The deploy gate's clause 2 ("a minor raised to secondary rank on at least
one of the thirty seeds", the user's ruling of November 18) reads ZERO with the
plans up — before the fix (Session 4b, `_ic4_promotions_wide_2026_11_23.json`)
and after it (`_ic4_promotions_wide_2026_11_23_fix.json`: the fix lets Bavaria
take the Tyrol on aspern again, and she then lacks the 3,000 gold of the crown
before Austria takes it back). With the plans down the thirty raise a minor on
two seeds (aspern, borodino) — a rate near one seed in fifteen, where thirty
seeds read zero by chance alone about one time in eight. This sample answers
the question the thirty cannot: cause, or chance.

THE RULE, WRITTEN BEFORE ANY DATA:
  Sample    200 FRESH seeds (`ic4b-wide-000` … `ic4b-wide-199` — none of the
            thirty), forty turns, the ambient runner and reading of the
            promotions surface (`_oc_measure._wide_promotions`), two arms on the
            SAME seeds: 0 (every seam of the session down — the plans down) and
            +PLAN (the plans up, as fixed — the seam held up, so the arm reads
            the same whatever the tree ships).
  Reading   P0 = seeds raising a minor in arm 0; P1 = in arm +PLAN.
            P1 >= P0 / 2  -> "no suppression shown": the thirty-seed zero is
                            the sample's; reported to the user with the gate,
                            which stays as he ruled it (the thirty) — the
                            decision to switch the plans on is his.
            P1 <  P0 / 2  -> "the plans suppress a minor's rise": the seeds
                            raising in arm 0 and not in +PLAN are traced for the
                            cause before anything else is decided.
  Never     a substitute for the gate's thirty, or a seed list chosen after
            the data.

THE RESULT (written after the data; `_ic4b_wide_promotions_2026_11_23.json`;
the plans-up arm was first named ALL, on a frozen copy that carried the seam
up, and renamed +PLAN so a re-run reads the same whatever the tree ships — the
re-run gave the same numbers):
P0 = 9 (Denmark 5, Bavaria 3, Hesse 1), P1 = 8 (Bavaria 5, Hesse 3) — "no
suppression shown" on the count the gate reads. At 9 in 200, thirty seeds
read zero about one time in four. No seed raises a minor in both arms: which
court rises, and when, follows the world's fall. PER COURT it is not even —
the plans close Denmark's road (5 to 0; a one-sided chance near 3 in 100):
traced on three of her five seeds (and borodino), the coalition's opening
moves Russia's money to Sweden a turn sooner and Sweden arms at turn 8 — her
menace to Denmark 21,600 to 23,400 with the plans up against 15,600 with them
down, so Denmark's reserve rises to its cap and her free strength falls (about
13,500 against 18,000 at turn 8) — and Denmark's war council reads her
outmatched on every turn she would fight: no crisis opens, no war on Sweden.
Bavaria and Hesse rise more often. The pooled rule cannot see one court's road
close; the per-court table goes to the user with the gate.

    .venv/Scripts/python.exe tools/_ic4b_wide_promotions.py --jobs 6
Run from a FROZEN COPY of the tree (its records copied back).
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SEEDS = tuple(f"ic4b-wide-{n:03d}" for n in range(200))
OUT = ROOT / "tools" / "_ic4b_wide_promotions_2026_11_23.json"


def main() -> int:
    from tools import _ic4_measure as M
    from tools import _oc_measure as OC

    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    thirty = set(OC.WIDE_SEEDS) | set(__import__("tools.ai_v_sweep", fromlist=["SWEEP_SEEDS"]).SWEEP_SEEDS)
    assert not thirty & set(SEEDS), "the sample must be fresh"
    record = {"_note": __doc__.split("THE RULE")[0].strip(), "seeds": list(SEEDS), "arms": {}}
    for arm in ("0", "+PLAN"):
        seams = ";".join(M.held(arm))
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            got = dict(zip(SEEDS, pool.map(lambda sd: OC._wide_promotions(sd, seams), SEEDS)))
        raising = sorted(sd for sd, v in got.items() if v)
        courts = collections.Counter(court for v in got.values() for _turn, court in v)
        record["arms"][arm] = {"seams_held": M.held(arm), "seeds": got, "seeds_raising": raising,
                               "count": len(raising), "courts": dict(courts)}
        print(f"[ic4b-wide] arm {arm}: {len(raising)} of {len(SEEDS)} seeds raise a minor "
              f"{dict(courts)}", flush=True)
    p0, p1 = record["arms"]["0"]["count"], record["arms"]["+PLAN"]["count"]
    verdict = "no suppression shown" if p1 * 2 >= p0 else "the plans suppress a minor's rise"
    only0 = sorted(set(record["arms"]["0"]["seeds_raising"]) - set(record["arms"]["+PLAN"]["seeds_raising"]))
    only1 = sorted(set(record["arms"]["+PLAN"]["seeds_raising"]) - set(record["arms"]["0"]["seeds_raising"]))
    record["reading"] = {"P0": p0, "P1": p1, "verdict": verdict,
                         "raise_down_only": only0, "raise_up_only": only1}
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8")
    print(f"[ic4b-wide] P0 {p0}, P1 {p1} -> {verdict}; down only {only0}; up only {only1}", flush=True)
    print(f"[ic4b-wide] written {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
