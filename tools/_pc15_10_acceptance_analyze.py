"""PC15-10 B5 — read the flagship digests (and the acceptance probe's ledger)
into `docs/PETITION_POPUP_REVISIT_SPEC.md` §8's numbers.

    .venv/Scripts/python.exe tools/_pc15_10_acceptance_analyze.py \
        BEFORE_digest.jsonl AFTER_digest.jsonl [PROBE.json]

§8 item 1: blocking petition modals (the digest's `popup` rows keyed
`marshal_petition`) and the longest run of consecutive turns carrying one.
Item 3: audiences heard (`marshal_audience`). Item 5: the per-kind table.
Items 2 and 4 read the probe (`tools/_pc15_10_acceptance_probe.py`).
"""
import collections
import json
import re
import sys


def petitions(digest_jsonl):
    turn = 0
    modals, audiences = [], []
    with open(digest_jsonl, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "turn":
                turn = int(r.get("turn", turn))
            elif r.get("kind") == "popup" and r.get("key") in ("marshal_petition",
                                                               "marshal_audience"):
                summary = str(r.get("summary", ""))
                who = re.search(r"Marshal (\w+)", summary)
                row = {"turn": turn, "kind": summary.split(",", 1)[0].strip(),
                       "who": who.group(1) if who else "", "answer": r.get("answer", "")}
                (modals if r["key"] == "marshal_petition" else audiences).append(row)
    return modals, audiences


def longest_streak(turns):
    best = run = 0
    prev = None
    for t in sorted(set(turns)):
        run = run + 1 if prev is not None and t == prev + 1 else 1
        best, prev = max(best, run), t
    return best


def report(label, digest_jsonl):
    modals, audiences = petitions(digest_jsonl)
    turns = [m["turn"] for m in modals]
    print(f"== {label}: {len(modals)} petition MODALS on {len(set(turns))} turns; "
          f"longest consecutive-turn streak {longest_streak(turns)}; "
          f"{len(audiences)} AUDIENCES heard")
    print("   per kind (modal):", dict(collections.Counter(m["kind"] for m in modals)))
    print("   per kind (audience):", dict(collections.Counter(a["kind"] for a in audiences)))
    for m in modals:
        print(f"   t{m['turn']:>2} MODAL    {m['kind']:<24} {m['who']:<12} -> {m['answer']}")
    for a in audiences:
        print(f"   t{a['turn']:>2} AUDIENCE {a['kind']:<24} {a['who']:<12} -> {a['answer']}")


def probe_report(path):
    with open(path, encoding="utf-8") as fh:
        probe = json.load(fh)
    rows = probe["rows"]
    print(f"== probe: {len(rows)} petition moments; driver exit {probe['exit']}")
    print("   by status:", dict(collections.Counter(r["status"] for r in rows)))
    print("   by fate:", dict(collections.Counter(str(r["fate"]) for r in rows)))
    print(f"   SILENT LOSSES (queued, no fate, not standing): {len(probe['silent'])}")
    fires = probe.get("fire_lines", [])
    print(f"   fire lines: {len(fires)}, capped by the drama cap: "
          f"{sum(1 for f in fires if f[3] == 'capped')}")
    for r in rows:
        if r["status"] == "blocked" and r["kind"] == "jealousy_confrontation":
            hit = [f[3] for f in fires if f[0] == r["turn"] and f[1] == r["speaker"]]
            print(f"   blocked t{r['turn']} {r['speaker']} L{r['level']}: fire line {hit or 'NONE'}")
    l1 = [r for r in rows if r["tier"] == "audience"
          and r["kind"] == "jealousy_confrontation" and r["level"] == 1]
    died = [r for r in l1 if not r["opened"]
            and str(r["fate"]) in ("retired:superseded", "evicted")]
    print(f"   Q1 observable: {len(l1)} L1 audiences; {len(died)} died unopened")


if __name__ == "__main__":
    report("BEFORE", sys.argv[1])
    report("AFTER", sys.argv[2])
    if len(sys.argv) > 3:
        probe_report(sys.argv[3])
