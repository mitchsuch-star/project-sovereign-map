"""Session G3 — the rule's reach on the AI-France harness, read off the kept
runs (DYNAMISM_SPEC.md §7c; November 11, 2026): per arm and seed, every
DEFENSIVE ALLIANCE or ALLIANCE a court-to-court treaty signed with a court
that answered to a lord at that turn, and the courts that changed lords
(the boundary: a pact standing when a court becomes a client stands).

The run directory (`tools/playtest_runs/g3_chain_d/<arm>/<seed>.json`, written
by `tools/_g3_measure.py --surfaces d`) is gitignored; this record is what is
committed and pinned (`TestTheSessionG3Measure`).

    .venv/Scripts/python.exe tools/_g3_client_pacts.py [--run-dir …] [--out …]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOOT = {"Holland": "France", "KingdomOfItaly": "France", "Switzerland": "France"}
PACTS = ("Defensive Alliance", "Alliance")


def read_run(path: pathlib.Path) -> dict:
    """One kept run: the client pacts signed, the lords' changes, and the
    courts that left a vassalage — the lord map walked event by event."""
    data = json.loads(path.read_text(encoding="utf-8"))
    lords = dict(BOOT)
    pacts, transfers, exits = [], [], []
    for row in data.get("turns") or []:
        turn = int(row.get("turn", 0))
        for event in row.get("events") or []:
            etype = str(event.get("type") or "")
            court = str(event.get("vassal") or event.get("nation") or "")
            if etype == "vassal_transferred":
                lords[court] = str(event.get("to_lord") or "")
                transfers.append([turn, court, str(event.get("from_lord") or ""), lords[court]])
            elif etype == "vassal_broke_free" or (
                    etype == "vassal_defected" and str(event.get("outcome") or "").startswith("free")):
                if lords.pop(court, None):
                    exits.append([turn, court, str(event.get("exit") or event.get("outcome") or "")])
            elif etype == "nation_eliminated":
                lords.pop(court, None)
            elif etype == "diplomatic_ai_ai_treaty" and event.get("treaty_type") in PACTS:
                a, b = str(event.get("nation_a") or ""), str(event.get("nation_b") or "")
                for client, other in ((a, b), (b, a)):
                    lord = lords.get(client)
                    if lord and other != lord and lords.get(other) != lord:
                        pacts.append([turn, client, lord, other, str(event.get("treaty_type"))])
                        break
    return {"client_pacts": pacts, "transfers": transfers, "exits": exits}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=str(ROOT / "tools" / "playtest_runs" / "g3_chain_d"))
    ap.add_argument("--out", default=str(ROOT / "tools" / "_g3_client_pacts_2026_11_11.json"))
    args = ap.parse_args()
    record = {"_note": ("Session G3 (a client swears no pact of its own) — on the AI-France harness's "
                        "kept runs, every defensive alliance or alliance a court-to-court treaty "
                        "signed with a court that answered to a lord at that turn "
                        "[turn, client, lord, other, treaty], the lords' changes [turn, court, from, "
                        "to] and the exits [turn, court, how]; written by tools/_g3_client_pacts.py "
                        "from tools/playtest_runs/g3_chain_d (gitignored)."),
              "arms": {}, "totals": {}}
    for arm_dir in sorted(p for p in pathlib.Path(args.run_dir).iterdir() if p.is_dir()):
        seeds = {path.stem: read_run(path) for path in sorted(arm_dir.glob("*.json"))}
        record["arms"][arm_dir.name] = seeds
        record["totals"][arm_dir.name] = {
            "client_pacts": sum(len(r["client_pacts"]) for r in seeds.values()),
            "transfers": sum(len(r["transfers"]) for r in seeds.values()),
        }
    pathlib.Path(args.out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("[g3] client pacts written", args.out, record["totals"])


if __name__ == "__main__":
    main()
