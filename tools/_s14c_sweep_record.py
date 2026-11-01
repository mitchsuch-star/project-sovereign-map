"""S14c part 4 (`docs/EVENTS_SPEC.md` §7, §9 Part 4) — the moments' measurement,
recorded. Composes `tools/_s14c_sweep_final.json` from part 4's runs, every one
carrying the moments' production-time trace (`tools/_moments_trace.py`):

    --sweep DIR         `tools/ai_v_sweep.py --all --out DIR` — arm A (control),
                        arm B (variance), arm C (the ten SWEEP_SEEDS) and the
                        scripted France; the trace rides every run
    --commanded DIR     the archived commanded arms (`tools/score_run.py run`
                        with `--moments-trace` on each driver)
    --accept DIR        CMD-A / CMD-M / CMD-H with `--moment accept --moments-trace`
    --road DIR          `tools/_vp1_road_arms.py --out DIR` (the trace rides
                        every road arm)
    --road-accept DIR   VP1-RH with `--moment accept` (the same tool, its --out)

Each arm keeps the trace's verdict — the ceilings, the floors, shown = applied —
its mornings, and each moment's reach composed from the trace alone (seeded
paths, not laws): "arrived T8, answered accept", "arrived T18, lapsed T19",
"passed T11 (premise)", "crowded out T19", or "pending — the last morning T28".
The record carries the shipped deck's MECHANICAL hash — ids, kinds, windows,
grace, predicates, roads, ops and pacing; never the display copy (a title, a
voice, a record line, a caption), since the trace measures arrivals and
answers, not words (S14D-X42, October 24, 2026): a deck whose MECHANICS are
edited after the measurement reds `tests/test_moments_pacing.py` until it is
measured again; a corrected line does not.

    python tools/_s14c_sweep_record.py --sweep DIR --commanded DIR --accept DIR \\
        --road DIR --road-accept DIR [--out tools/_s14c_sweep_final.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))   # RE-3: the armed block's hash reads the engine's display keys
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
OUT = ROOT / "tools" / "_s14c_sweep_final.json"


# The deck's display copy — what the letter SAYS, never when it arrives or what
# its answers do. Excluded from the measured identity (S14D-X42). RE-3 (P12):
# a moment's counsel line and an authored button line are copy too.
DISPLAY_KEYS = ("title", "voice", "record", "counsel")
ANSWER_DISPLAY_KEYS = ("caption", "button_line")
DECK_SHA_NOTE = ("S14D-X42, October 24, 2026: the hash is the deck's MECHANICAL identity (display copy "
                 "struck — tools/_s14c_sweep_record.py mechanical_block); RE-1 descends into the "
                 "recurring deck under `affairs`; RE-3 strikes a moment's `counsel` and `button_line` too")


def mechanical_block(block: dict) -> dict:
    """The block with its display copy struck: the measured identity. RE-1
    (RECURRING_EVENTS_SPEC.md §16b): the recurring deck under `affairs` is
    descended into the same way — its display keys (`affairs.DISPLAY_KEYS`,
    the variants' `text`, the answers' and the forms' copy) struck, never
    the keys that time an arrival or price an answer. A block with no
    `affairs` key hashes as it did."""
    out = {k: v for k, v in (block or {}).items() if k not in ("deck", "affairs")}
    deck = []
    for e in (block or {}).get("deck") or []:
        if not isinstance(e, dict):
            deck.append(e)
            continue
        m = {k: v for k, v in e.items() if k not in DISPLAY_KEYS}
        for side in ("accept", "decline"):
            if isinstance(m.get(side), dict):
                m[side] = {k: v for k, v in m[side].items() if k not in ANSWER_DISPLAY_KEYS}
        deck.append(m)
    out["deck"] = deck
    affairs = (block or {}).get("affairs")
    if isinstance(affairs, dict):
        out["affairs"] = _mechanical_affairs(affairs)
    return out


def _mechanical_affairs(affairs: dict) -> dict:
    from backend.game_logic import affairs as AF

    def strip_side(side):
        return {k: v for k, v in side.items() if k not in AF.ANSWER_DISPLAY_KEYS} \
            if isinstance(side, dict) else side

    def strip_entry(e):
        if not isinstance(e, dict):
            return e
        m = {k: v for k, v in e.items() if k not in AF.DISPLAY_KEYS}
        if isinstance(m.get("variants"), list):
            m["variants"] = [{k: v for k, v in variant.items() if k not in AF.VARIANT_DISPLAY_KEYS}
                             if isinstance(variant, dict) else variant for variant in m["variants"]]
        for side in ("accept", "decline"):
            if side in m:
                m[side] = strip_side(m[side])
        if isinstance(m.get("forms"), dict):
            m["forms"] = {name: ({**{k: v for k, v in form.items()
                                      if k not in AF.DISPLAY_KEYS and k not in ("accept", "decline")},
                                  **{side: strip_side(form[side]) for side in ("accept", "decline")
                                     if side in form}}
                                 if isinstance(form, dict) else form)
                          for name, form in m["forms"].items()}
        return m

    out = {k: v for k, v in affairs.items() if k != "deck"}
    out["deck"] = [strip_entry(e) for e in affairs.get("deck") or []]
    return out


def deck_sha(block: dict) -> str:
    """The shipped block's MECHANICAL identity (sorted keys, the display copy
    struck; the record and the pin agree)."""
    return hashlib.sha256(json.dumps(mechanical_block(block), sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def reach(trace: dict, deck_ids: list) -> dict:
    """Each moment's fate on one arm, read off the trace's own rows."""
    mornings = trace.get("mornings") or []
    applications = trace.get("applications") or []
    last = max([int(m.get("turn", 0)) for m in mornings] or [0])
    out = {}
    for mid in deck_ids:
        arrived = next((int(m["turn"]) for m in mornings if mid in (m.get("delivered") or [])), None)
        passed = next(((int(m["turn"]), m["passed"][mid]) for m in mornings
                       if mid in (m.get("passed") or {})), None)
        answer = next((a for a in applications if a.get("moment") == mid
                       and a.get("kind") in ("answer", "lapse")), None)
        if arrived is not None:
            if answer is None:
                out[mid] = f"arrived T{arrived}, standing at the last morning T{last}"
            elif answer["kind"] == "lapse":
                out[mid] = f"arrived T{arrived}, lapsed T{answer['turn']} (its decline)"
            else:
                out[mid] = f"arrived T{arrived}, answered {answer['answer']} T{answer['turn']}"
        elif passed is not None:
            turn, why = passed
            out[mid] = f"crowded out T{turn} (its receipt)" if why == "crowded" else f"passed T{turn} ({why})"
        else:
            out[mid] = f"pending — the last morning T{last}"
    return out


# The deck's own figure lines (`moments._op_gold`'s "900 gold (the treasury
# holds 11,649)", the receipt's "standing 100 → 92"); a law's price in a
# quote ("9,000 gold now, then 300 gold a turn") is the law's, not an op's.
_GOLD_LUMP = re.compile(r"(\d[\d,]*) gold \(the treasury holds")
_STANDING = re.compile(r"standing (\d+) → (\d+)")


def answered_figures(application: dict) -> dict:
    """RE-3 (§14 the brakes): what ONE answered or lapsed letter of state
    took, read off its application — the deck's gold lump and the standing
    it cost (its quote's own figure lines), beside every figure row the
    trace delivered."""
    quote = str(application.get("shown") or application.get("applied") or "")
    gold = sum(int(m.replace(",", "")) for m in _GOLD_LUMP.findall(quote))
    standing = sum(int(a) - int(b) for a, b in _STANDING.findall(quote))
    return {"occ": str(application.get("moment") or ""), "turn": int(application.get("turn", 0) or 0),
            "kind": str(application.get("kind") or ""), "answer": str(application.get("answer") or ""),
            "gold": gold, "standing": standing, "quote": quote,
            "figures": [{"op": r.get("op"), "figure": r.get("figure"), "quoted": r.get("quoted"),
                         "delivered": r.get("delivered")} for r in (application.get("rows") or [])]}


def affairs_reach(trace: dict, templates: list) -> dict:
    """RE-3 (ERR-3): each recurring template's fate on one arm, read off the
    trace alone — its occurrences (arrived Tn and answered / lapsed /
    withdrawn / standing), what each answer took (`answers`, §14's band),
    the rows crowded out, the mornings its premise held, its first due mark
    and the floor's verdict; and ONE word for the arm: arrived | crowded |
    due (released | pending) | never due (held n) | premise never held."""
    mornings = trace.get("mornings") or []
    judged = trace.get("judged") or {}
    applications = trace.get("applications") or []
    last = max([int(m.get("turn", 0)) for m in mornings] or [0])
    out = {}
    for template in templates:
        prefix = f"{template}#"
        arrived = {k: int(v) for k, v in (judged.get("arrived") or {}).items() if str(k).startswith(prefix)}
        withdrawn = {}
        held = 0
        for m in mornings:
            frame = m.get("affairs") or {}
            if template in (frame.get("true") or []):
                held += 1
            for occ in frame.get("withdrawn") or []:
                if str(occ).startswith(prefix):
                    withdrawn[str(occ)] = int(m.get("turn", 0))
        lines = []
        answers = []
        for occ, turn in sorted(arrived.items(), key=lambda kv: kv[1]):
            answer = next((a for a in applications if a.get("moment") == occ
                           and a.get("kind") in ("answer", "lapse")), None)
            if answer is not None:
                answers.append(answered_figures(answer))
            if occ in withdrawn:
                lines.append(f"{occ} arrived T{turn}, withdrawn T{withdrawn[occ]} (free)")
            elif answer is None:
                lines.append(f"{occ} arrived T{turn}, standing at the last morning T{last}")
            elif answer.get("kind") == "lapse":
                lines.append(f"{occ} arrived T{turn}, lapsed T{answer.get('turn')} (its decline)")
            else:
                lines.append(f"{occ} arrived T{turn}, answered {answer.get('answer')} T{answer.get('turn')}")
        crowded = [f"{occ} crowded out ({reason})" for occ, reason in (judged.get("passed") or {}).items()
                   if str(occ).startswith(prefix)]
        floors = {k: v for k, v in (judged.get("floors") or {}).items() if str(k).startswith(template)}
        first_due = min([int(v.get("first_due", 0) or 0) for v in floors.values()
                         if int(v.get("first_due", 0) or 0) > 0] or [0]) or None
        verdicts = sorted({str(v.get("verdict") or "") for v in floors.values()})
        if lines:
            word = "arrived"
        elif crowded:
            word = "crowded"
        elif first_due:
            word = "due, " + ("released" if verdicts == ["released"] else "pending")
        elif held:
            word = f"never due (premise held {held} morning{'' if held == 1 else 's'})"
        else:
            word = "premise never held"
        out[template] = {"verdict": word, "occurrences": lines, "answers": answers, "crowded": crowded,
                         "premise_mornings": held, "first_due": first_due, "last_morning": last}
    return out


def row(trace: dict, deck_ids: list, templates: list = (), **extra) -> dict:
    judged = trace.get("judged") or {}
    out = {"measured": bool(trace.get("measured")), "mornings": int(judged.get("mornings", 0) or 0),
           "ceiling_breaches": judged.get("ceiling_breaches") or [],
           "floor_breaches": judged.get("floor_breaches") or [],
           "floors": judged.get("floors") or {},
           "shown_equals_applied": bool(judged.get("shown_equals_applied", True)),
           "mismatches": judged.get("mismatches") or [],
           "context_drift": judged.get("context_drift") or [],
           "answers": judged.get("answers") or [],
           "reach": reach(trace, deck_ids),
           "affairs_reach": affairs_reach(trace, list(templates)),
           "errors": trace.get("errors") or []}
    out.update(extra)
    return out


def _sweep(root: Path, deck_ids: list, templates: list = ()) -> dict:
    out = {}
    for path in sorted(root.glob("arm*.json")):
        digest = json.loads(path.read_text(encoding="utf-8"))
        trace = (digest.get("final") or {}).get("moments_trace") or {}
        derived = digest.get("derived") or {}
        meta = digest.get("meta") or {}
        out[path.stem] = row(trace, deck_ids, templates, seed=meta.get("seed"),
                             ambient_base=meta.get("ambient_base"), script=meta.get("script"),
                             metrics={"max_per_turn": derived.get("moments_max_per_producing_turn", 0),
                                      "open_max": derived.get("open_letters_max", 0),
                                      "during_foreground": derived.get("letters_during_foreground", 0),
                                      "fire_turns": derived.get("fire_turns", {}),
                                      "affair_turns": derived.get("affair_turns", {})})
    return out


def _driver_arms(root: Path, deck_ids: list, templates: list = ()) -> dict:
    out = {}
    for meta_path in sorted(root.glob("arms/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        trace = meta.get("moments_trace") or {}
        if trace:
            out[meta_path.parent.name] = row(trace, deck_ids, templates, status=meta.get("status"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", required=True)
    ap.add_argument("--commanded", required=True)
    ap.add_argument("--accept", required=True)
    ap.add_argument("--road", required=True, help="the road arms' --out directory")
    ap.add_argument("--road-accept", required=True, help="Road I answered: its --out directory")
    # RE-3 (ERR-3): the treaty road and the six hand-played starts — their
    # own families, so the nine commanded arms stay the nine the pin names
    ap.add_argument("--reach-aar", default="", help="REACH-AAR's --out directory (RE-3)")
    ap.add_argument("--saves", default="", help="the hand-played starts' --out directory (RE-3)")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
    deck_ids = [e["id"] for e in block["deck"]]
    templates = [str(e.get("id")) for e in ((block.get("affairs") or {}).get("deck") or [])
                 if isinstance(e, dict)]
    record = {
        "_part": ("S14c part 4 — the moments over the 10-seed sweep and the arms, each run "
                  "carrying the production-time trace (docs/EVENTS_SPEC.md §7, §17); RE-3 — the "
                  "recurring deck's reach beside them (RECURRING_EVENTS_SPEC.md §16, ERR-3)"),
        "deck_sha": deck_sha(block), "deck_sha_note": DECK_SHA_NOTE,
        "pacing": block.get("pacing") or {}, "deck": deck_ids, "affairs_deck": templates,
        "sweep": _sweep(Path(args.sweep), deck_ids, templates),
        "commanded": _driver_arms(Path(args.commanded), deck_ids, templates),
        "accept": _driver_arms(Path(args.accept), deck_ids, templates),
        "road": _driver_arms(Path(args.road), deck_ids, templates),
        "road_accept": _driver_arms(Path(args.road_accept), deck_ids, templates),
        "reach_aar": _driver_arms(Path(args.reach_aar), deck_ids, templates) if args.reach_aar else {},
        "saves": _driver_arms(Path(args.saves), deck_ids, templates) if args.saves else {},
    }
    Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for family in ("sweep", "commanded", "accept", "road", "road_accept", "reach_aar", "saves"):
        rows = record[family]
        print(f"{family:12s} arms {len(rows):2d}  ceiling breaches "
              f"{sum(len(r['ceiling_breaches']) for r in rows.values())}  floor breaches "
              f"{sum(len(r['floor_breaches']) for r in rows.values())}  shown=applied "
              f"{all(r['shown_equals_applied'] for r in rows.values())}")
    for template in templates:
        words = {}
        for family in ("sweep", "commanded", "accept", "road", "road_accept", "reach_aar", "saves"):
            for name, r in record[family].items():
                words[f"{family}/{name}"] = (r.get("affairs_reach") or {}).get(template, {}).get("verdict", "")
        arrived = sum(1 for w in words.values() if w == "arrived")
        print(f"{template:22s} arrived on {arrived} of {len(words)} arms")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
