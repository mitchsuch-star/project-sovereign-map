"""Row IC, Session 4b (IC4-R1) — THE VOICE'S BLIND READING: the draw.

Session 4's key was drawn by a fixed seeded procedure that was never kept in
the repository (`docs/audits/ic_client/session4/README.md`). This is that
procedure, kept, so a round can be drawn again:

* PAIRS — the plan's question ("two lines with no names: which marshal said
  which, and what told you?"): two of the six men who judge for themselves and
  ONE kind both have their own set for, one line from each man's own set; each
  man in four pairs (twelve pairs). Session 4b draws the pairs that confused
  the readers (Ney with Lannes, Masséna with Davout) at least twice each.
* SIXWAY — the harder test besides: five kinds every one of the six has his own
  set for, each a lettered table of the six men's lines, shuffled.

The key is written BEFORE any reader sees a line. Every kind of line the men
say may be drawn — the hold-proposal lines and the "free" lines (Session 4b)
included.

    .venv/Scripts/python.exe tools/_ic4b_voice_key.py --seed 20261123 --out docs/audits/ic_client/session4b/_blind_key_round1.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SIX = ("Ney", "Davout", "Murat", "Lannes", "Massena", "Bernadotte")
CONFUSED = (("Ney", "Lannes"), ("Massena", "Davout"))
SHOWN = {"Massena": "Masséna"}
WHO = {
    "Ney": "Ney — a bold marshal, famous for his courage and his impatience to fight.",
    "Davout": "Davout — a careful marshal, strict, exact, who counts every man and never wastes one.",
    "Murat": "Murat — a bold cavalry marshal who loves to ride and charge.",
    "Lannes": "Lannes — a bold marshal who marches to the sound of the guns and leads assaults himself.",
    "Massena": "Masséna — a stubborn marshal who never gives up ground he holds.",
    "Bernadotte": "Bernadotte — a slow, politic marshal who is never in a hurry and always has an excuse.",
}


def draw(seed: int) -> dict:
    """A draw of twelve pairs: the greedy pairing can corner itself (each man
    in four pairs, no line twice), so it is tried again on the seed's next
    sub-seed until twelve stand — deterministic for a seed."""
    for attempt in range(200):
        key = _draw(random.Random(f"{seed}:{attempt}" if attempt else seed), seed)
        if len(key["pairs"]) == 12:
            key["attempt"] = attempt
            return key
    raise SystemExit("no full draw of twelve pairs for this seed")


def _draw(rng, seed: int) -> dict:
    from backend.game_logic import own_voice as V
    sets = {man: {k: list(v) for k, v in V.LINES.get(man, {}).items() if v} for man in SIX}
    shared_kinds = sorted(set.intersection(*(set(sets[m]) for m in SIX)))
    # pairs: each man in four; the two confused pairings drawn twice each first
    count = {m: 0 for m in SIX}
    pairs = []
    used: set = set()
    wanted = [CONFUSED[0], CONFUSED[0], CONFUSED[1], CONFUSED[1]]
    # the plan: every draw includes the "act on your own" lines and the
    # hold-proposal lines (added after Session 4's last round, never read)
    forced = {0: "free", 2: "proposal_hold"}
    others = [(a, b) for i, a in enumerate(SIX) for b in SIX[i + 1:]
              if (a, b) not in CONFUSED and (b, a) not in CONFUSED]
    rng.shuffle(others)
    for i, (a, b) in enumerate(wanted + others):
        if len(pairs) == 12:
            break
        if count[a] >= 4 or count[b] >= 4:
            continue
        # never the same line twice in a draw (a reader shown one line twice
        # gets a free check): only kinds where each man has a line left
        kinds = sorted(k for k in set(sets[a]) & set(sets[b])
                       if set(sets[a][k]) - used and set(sets[b][k]) - used)
        if not kinds:
            continue
        kind = forced[i] if forced.get(i) in kinds else rng.choice(kinds)
        la = rng.choice(sorted(set(sets[a][kind]) - used))
        lb = rng.choice(sorted(set(sets[b][kind]) - used))
        used.update({la, lb})
        first, second = (a, la), (b, lb)
        if rng.random() < 0.5:
            first, second = second, first
        men = sorted([a, b])
        pairs.append({"n": len(pairs) + 1, "kind": kind, "men": [SHOWN.get(m, m) for m in men],
                      "line1": first[1], "line2": second[1],
                      "key": {"line1": SHOWN.get(first[0], first[0]), "line2": SHOWN.get(second[0], second[0])}})
        count[a] += 1
        count[b] += 1
    sixway = []
    six_kinds = rng.sample([k for k in shared_kinds if k not in ("free", "proposal_hold")],
                           min(4, len(shared_kinds) - 2))
    six_kinds.insert(rng.randrange(len(six_kinds) + 1), rng.choice(["free", "proposal_hold"]))
    for kind in six_kinds:
        # (never a line already drawn — in the pairs or in an earlier set)
        if any(not (set(sets[m][kind]) - used) for m in SIX):
            return {"pairs": [], "sixway": []}
        rows = [(m, rng.choice(sorted(set(sets[m][kind]) - used))) for m in SIX]
        used.update(line for _m, line in rows)
        rng.shuffle(rows)
        sixway.append({"kind": kind, "rows": [{"letter": "ABCDEF"[i], "line": line,
                                               "key": SHOWN.get(m, m)} for i, (m, line) in enumerate(rows)]})
    return {"_note": ("Written BEFORE any reader saw a line (row IC, Session 4b, IC4-R1). `pairs` is the "
                      "plan's question 1 (two lines, two named marshals: which said which); `sixway` the "
                      "harder test besides. The confused pairings (Ney/Lannes, Massena/Davout) drawn twice each."),
            "seed": seed, "kinds_drawn_from": shared_kinds, "who": WHO, "pairs": pairs, "sixway": sixway}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    key = draw(args.seed)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(key, indent=1, ensure_ascii=False), encoding="utf-8")
    print("written", out, len(key["pairs"]), "pairs,", len(key["sixway"]), "six-way sets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
