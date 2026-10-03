"""SF-LB-1's open question — the AI-vs-AI `fight` bar (October 3, 2026).

Measured on Step 3's exit: 0 AI-vs-AI wars on 7 ambient seeds, because an
acquire design between two AI courts tops out below `PRICE_THRESHOLDS`'
`fight` (85). This probe runs one seeded 40-turn ambient board (the
`--emit-series` loop, hash-pinned by the caller) and records, every turn,
every non-player acquire design aimed at a non-player holder: the weight,
the rung, the asker's standing / free strength against the holder's, the
refusals on record, and the restraint the war council would name. The
counterfactuals are computed OFFLINE from the record (no code is changed):

    .venv/Scripts/python.exe tools/_sf_lb1_fight_bar_probe.py --seed ulm --out X.json

Aggregation: tools/_sf_lb1_fight_bar_probe.py --aggregate a.json b.json …

SF-LB-2 "The Defenceless Prize" (October 3, 2026) made this probe the
slice's harness: every row also records the ONE outmatched reading
(`war_council.holder_outmatched`), the record carries every crisis the
council opened (coveter, target, the turn and the RUNG it opened at) and
every AI-initiated war with its declaration turn, and the aggregate reports
them per seed — the acceptance's variance clause reads the opening turns.

SF-LB-2b "The Chest the Council Can Spend" (October 3, 2026): every row also
carries the OPENING's restraint read (`restraint_forecast`, the chest the
court will have when the turn ends) beside the live one, with both chests;
the aggregate reports the opening turns per seed and their spread.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def run(seed: str, turns: int) -> dict:
    from backend.commands.executor import CommandExecutor
    from backend.game_logic import war_council as WC
    from backend.game_logic.intent import get_nation_intent
    from backend.game_logic.ai_diplomacy import get_refused_asks
    from backend.game_logic.ledger import chest_forecast
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO), seed=seed)
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    player = world.player_nation
    rows = []

    def snapshot(turn):
        vassals = set((getattr(world, "vassals", {}) or {}).keys())
        for nation in world.get_active_nations():
            if nation == player or nation in vassals:
                continue
            try:
                view = get_nation_intent(nation, world)
            except Exception as exc:  # noqa: BLE001
                rows.append({"turn": turn, "nation": nation, "error": str(exc)})
                continue
            if view.want_type != "acquire_regions" or not view.against:
                continue
            against = view.against
            if against == player or against in vassals:
                continue
            refusals = [e for e in get_refused_asks(world, nation, against)
                        if e.get("type") in ("design_ask", "design_purchase")]
            own = WC._standing_strength(world, nation)
            theirs = WC._standing_strength(world, against)
            rows.append({
                "turn": turn, "nation": nation, "against": against,
                "want": view.want_id, "weight": int(view.weight), "price": view.price,
                "own": int(own), "free": int(WC.get_free_strength(world, nation)),
                "theirs": int(theirs),
                "refusals": len(refusals),
                "ladder": bool(WC._ladder_climbed(world, nation, against)),
                "restraint": WC._restraint_block_reason(world, nation, against),
                # SF-LB-2b: the OPENING's read (the chest the court can spend)
                # beside the live one, and both chests.
                "restraint_forecast": WC._restraint_block_reason(
                    world, nation, against, forecast=True),
                "chest": int((getattr(world, "nation_gold", {}) or {}).get(nation, 0)),
                "chest_forecast": int(chest_forecast(world, nation)["projected"]),
                "at_war": bool(world.is_at_war(nation, against)),
                "outmatched": bool(WC.holder_outmatched(world, nation, against)),
            })

    crises = {}
    declared = {}

    def note_crises():
        for coveter, rec in (getattr(world, "war_intents", {}) or {}).items():
            key = f"{coveter}->{rec.get('target')}@{rec.get('opened_turn')}"
            crises.setdefault(key, {
                "coveter": coveter, "target": rec.get("target"),
                "opened_turn": int(rec.get("opened_turn", 0)),
                "opened_at_price": rec.get("opened_at_price"),
            })
        # A council war is recorded the turn it FIRST stands: a minor's
        # elimination (D2) retires the instance before turn 40, so an
        # end-of-run count under-reads (measured on austerlitz).
        for war_id, war in (getattr(world, "war_instances", {}) or {}).items():
            if not isinstance(war, dict) or not war.get("ai_initiated"):
                continue
            if war_id in declared:
                declared[war_id]["ended_turn"] = war.get("ended_turn")
                continue
            meta = war.get("participant_meta") or {}
            joined = [int(m.get("joined_turn")) for m in meta.values()
                      if isinstance(m, dict) and m.get("joined_turn") is not None]
            declared[war_id] = {
                "war_id": war_id,
                "attackers": sorted(war.get("attackers") or []),
                "defenders": sorted(war.get("defenders") or []),
                "started_turn": min(joined) if joined else int(world.current_turn),
                "ended_turn": war.get("ended_turn"),
                "design_id": war.get("design_id"),
            }

    snapshot(0)
    note_crises()
    for turn in range(turns):
        random.seed(10_000 + turn)
        with contextlib.redirect_stdout(io.StringIO()):
            tm.end_turn(game_state)
        snapshot(turn + 1)
        note_crises()
    wars = [k for k, v in world.diplomatic_states.items() if v == "WAR"]
    return {"seed": seed, "rows": rows, "ai_initiated_wars": int(WC.count_ai_initiated_wars(world)),
            "ai_initiated_wars_ever": len(declared),
            "wars_declared": sorted(declared.values(), key=lambda d: (d["started_turn"] or 0, d["war_id"])),
            "crises_opened": sorted(crises.values(), key=lambda c: (c["opened_turn"], c["coveter"])),
            "war_intents": {k: {kk: vv for kk, vv in v.items() if kk in ("target", "opened_turn", "foregrounded", "opened_at_price")}
                            for k, v in (getattr(world, "war_intents", {}) or {}).items()},
            "wars_at_end": wars}


def _openings_by_pair(crises):
    out = {}
    for c in sorted(crises, key=lambda c: (int(c.get("opened_turn", 0)), str(c.get("coveter")))):
        out.setdefault(f"{c['coveter']}->{c['target']}", []).append(int(c["opened_turn"]))
    return out


def aggregate(paths):
    out = {}
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        rows = [r for r in d["rows"] if "weight" in r and not r["at_war"]]
        pairs = {}
        for r in rows:
            k = f"{r['nation']}->{r['against']}"
            pairs.setdefault(k, []).append(r)
        summary = {}
        for k, rs in pairs.items():
            wmax = max(r["weight"] for r in rs)
            top = max(rs, key=lambda r: r["weight"])
            ratio_free = [r["free"] / r["theirs"] if r["theirs"] else 99 for r in rs]
            # counterfactual A: +10 weight while free >= 2x theirs
            cf_a = max(r["weight"] + (10 if (r["theirs"] and r["free"] >= 2 * r["theirs"]) else 0) for r in rs)
            # counterfactual B: the crisis opens at coerce when free >= 2x theirs and the restraints clear
            cf_b_turns = [r["turn"] for r in rs if r["price"] in ("coerce", "fight")
                          and r["theirs"] and r["free"] >= 2 * r["theirs"] and r["restraint"] is None]
            ladder_turns = [r["turn"] for r in rs if r["ladder"]]
            summary[k] = {
                "turns_seen": len(rs), "weight_max": wmax, "price_at_max": top["price"],
                "turn_at_max": top["turn"], "refusals_at_max": top["refusals"],
                "restraint_at_max": top["restraint"],
                "free_ratio_max": round(max(ratio_free), 2),
                "turns_at_coerce_plus": sum(1 for r in rs if r["price"] in ("coerce", "fight")),
                "cf_A_plus10_at_2to1_reaches_85": cf_a >= 85,
                "cf_A_weight_max": cf_a,
                "cf_B_coerce_and_2to1_and_clear_turns": cf_b_turns[:6],
                "ladder_climbed_turns": ladder_turns[:6],
            }
        out[d["seed"]] = {"ai_initiated_wars": d["ai_initiated_wars"],
                          # SF-LB-2b: EVERY opening per pair (a crisis can cool and
                          # re-open — marengo's did, 5 then 10) and the FIRST, which is
                          # what the variance clause reads.
                          "crisis_opening_turns": _openings_by_pair(d.get("crises_opened", [])),
                          "first_opening_turn": {k: v[0] for k, v in
                                                 _openings_by_pair(d.get("crises_opened", [])).items()},
                          "ai_initiated_wars_ever": d.get("ai_initiated_wars_ever"),
                          "wars_declared": d.get("wars_declared", []),
                          "crises_opened": d.get("crises_opened", []),
                          "war_intents": d["war_intents"],
                          "pairs": summary}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--out")
    ap.add_argument("--aggregate", nargs="*")
    args = ap.parse_args()
    if args.aggregate:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(json.dumps(aggregate(args.aggregate), indent=1))
        return 0
    payload = run(args.seed, args.turns)
    Path(args.out).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"{args.seed}: ai_initiated_wars={payload['ai_initiated_wars']} rows={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
