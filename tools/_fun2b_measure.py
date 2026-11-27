"""Row FUN, Session FUN-2b — "peace terms priced" — the measure (November 27,
2026; `docs/NEXT_SESSION_PROMPT.md`'s FUN-2b block; `SYSTEMS_REFERENCE.md` §241).

THE RULE, WRITTEN BEFORE THE DATA (the brief's own words, kept here verbatim
before any run):
    on the ten ambient seeds, no peace France signs takes a court's every
    province.
Read here as (the plan approved in Plan Mode, item (b) of its measure):
    on each of the ten ambient seeds, France beats Austria's field armies on
    turn 3 and takes four of its provinces through the capture chokepoint on
    turns 4-7 (Tyrol, Carniola, Croatia, Moravia — a garrison left in each;
    Vienna left to Austria), the rest of Europe played by the computer; on
    turn 10 France
    opens the peace table for its war with Austria, covering Austria alone,
    TWICE on copies of that board: AS PLAYED (the war score it has then) and
    DECISIVE (its war score with Austria set to 100 — the strongest France the
    table can face). Each time it takes the guided opening draft and every
    land row the table still offers, one at a time; it then tries to add each
    province Austria still holds by hand (on a copy), and to buy all of Austria
    with 5,000 gold. It signs the guided package (Submit, then Ratify).
    PASS on a seed when ALL hold in BOTH readings:
      (1) every land row offered (not greyed) re-scores Austria at 50 or more
          the moment it is offered;
      (2) the hand-pick of the province that would leave Austria nothing is
          refused, and no hand-picked package takes every province;
      (3) the buy-all package is refused (`takes_every_province`);
      (4) after the signature Austria still holds a province and stands;
      (5) the fear the signature wrote is exactly the table's forecast, and the
          provinces France already held wrote none.
    Bar: 10 of 10. A missed bar is reported as missed, never moved.

    .venv/Scripts/python.exe tools/_fun2b_measure.py [--seeds ...] [--jobs 4] [--out F]
    .venv/Scripts/python.exe tools/_fun2b_measure.py --child --seed S

Writes tools/_fun2b_measure_2026_11_27.json by default.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
AMBIENT_K = 10_000
TAKEN = ["Tyrol", "Carniola", "Croatia", "Moravia"]
TABLE_TURN = 10
NOTES = [
    "Smoke run 1 of the first script (three provinces, the table on turn 8; historical) read "
    "France's war score with Austria at 9: no land was offered and even the bare peace was "
    "refused, so nothing was measured. The script was strengthened (five provinces, Vienna "
    "among them, the table on turn 10) and a DECISIVE reading (the war score set to 100) added "
    "beside the played one.",
    "Smoke run 2 read Austria refusing every peace in both readings — France holding Vienna "
    "counts as her capital lost (RS-D1) — and the table's opening draft (its gold at the near "
    "floor, 35) refused even at 100, so nothing was signed and checks 4-5 held only vacuously. "
    "The measured script leaves Vienna to Austria (four provinces taken) and its player, after "
    "reading the opening draft (check 1 reads its land too), strips it to the bare peace before "
    "taking every land row still offered — the best case for land at the table.",
]
GARRISON = 3000
SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
         "eylau", "friedland", "wagram", "lodi", "rivoli"]


def _quiet():
    import contextlib
    import io
    return contextlib.redirect_stdout(io.StringIO())


def _war_with(world, a: str, b: str) -> str:
    for war_id, inst in (getattr(world, "war_instances", {}) or {}).items():
        side = inst.get("side_by_nation") or {}
        if (a in side and b in side and side[a] != side[b]
                and a in (inst.get("active_participants") or [])
                and b in (inst.get("active_participants") or [])):
            return str(war_id)
    return ""


def _act(world, action: str, dialogue: dict, **params) -> dict:
    from backend.game_logic.settlement_actions import handle_settlement_dialogue_action
    with _quiet():
        return handle_settlement_dialogue_action(
            world, action=action, dialogue=dialogue, action_params={"action": action, **params})


def child(seed: str) -> dict:
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_MAP", None)
    sys.path.insert(0, str(ROOT))
    import copy
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic import fear as F
    from backend.game_logic import land_price as LP
    from backend.game_logic.diplomacy import get_war_score_for
    from backend.game_logic.settlement_staging import stage_settlement_confirm
    from backend.game_logic.settlement_validation import validate_settlement_terms
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    with _quiet():
        world = WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    taken = []
    for i in range(TABLE_TURN - 1):
        turn = int(world.current_turn)
        if turn == 3:
            for m in [m for m in world.marshals.values() if m.nation == "Austria"]:
                world.destroy_marshal(m, "destroyed", victor="France")
        if 4 <= turn <= 3 + len(TAKEN):
            name = TAKEN[turn - 4]
            if world.regions[name].controller == "Austria":
                with _quiet():
                    world.capture_region(name, "France")
                world.regions[name].garrison_strength = GARRISON
                world.regions[name].garrison_detachment = True
                taken.append(name)
        random.seed(AMBIENT_K + i)
        with _quiet():
            tm.end_turn(game_state)

    out = {"seed": seed, "turn": int(world.current_turn), "taken": taken,
           "france_holds_of_austria": sorted(r for r in TAKEN
                                             if world.regions[r].controller == "France"),
           "austria_holds": sorted(world.get_nation_regions("Austria")), "readings": {}}
    war_id = _war_with(world, "France", "Austria")
    if not war_id:
        out["error"] = "France and Austria are no longer at war at the table's turn"
        return out
    out["war_id"] = war_id
    for reading in ("as_played", "decisive"):
        board = copy.deepcopy(world)
        if reading == "decisive":
            key = board._make_diplo_key("France", "Austria")
            board.war_scores[key] = 100 if key.split("|")[0] == "France" else -100
        out["readings"][reading] = _read_table(board, war_id, copy=copy, F=F, LP=LP,
                                               get_war_score_for=get_war_score_for,
                                               stage_settlement_confirm=stage_settlement_confirm,
                                               validate_settlement_terms=validate_settlement_terms)
    out["checks"] = {f"{reading}:{name}": bool(ok)
                     for reading, got in out["readings"].items()
                     for name, ok in (got.get("checks") or {"table_did_not_open": False}).items()}
    return out


def _read_table(world, war_id, *, copy, F, LP, get_war_score_for, stage_settlement_confirm,
                validate_settlement_terms) -> dict:
    """One reading of the table on `world` (a copy): the guided path, the
    hand-picks, the buy-all probe, the signature, the five checks."""
    inst = world.war_instances[war_id]
    side = inst["side_by_nation"]["France"]
    out = {"war_score": int(get_war_score_for(world, "France", "Austria")),
           "austria_holds": sorted(world.get_nation_regions("Austria"))}
    table = LP.table_for(world, war_id=war_id, war_instance=inst, proposer_side=side,
                         proposer_side_leader="France", covered=["Austria"])
    with _quiet():
        staged = stage_settlement_confirm(
            world, war_id=war_id, actor_nation="France", settlement_terms=None,
            covered_enemy_participants=["Austria"], selected_target_nation="Austria",
            caller_kind="player_editor", dialogue_mode="PROPOSE")
    if not staged.get("success"):
        out["error"] = f"the table did not open: {staged.get('error')}"
        return out
    dialogue = staged["diplomatic_dialogue"]
    out["opening_terms"] = [dict(t) for t in dialogue.get("settlement_terms") or []]
    out["opening_total"] = next((r.get("total") for r in dialogue.get("per_court_acceptance") or []
                                 if r.get("nation") == "Austria"), None)
    offered, bad_offers, picks = [], [], []

    def land_rows(d):
        for row in d.get("per_court_acceptance") or []:
            if row.get("nation") != "Austria":
                continue
            return [s for s in (row.get("demand_suggestions") or [])
                    if s.get("group") == "demand"
                    and s.get("clause_type") in ("territory_cede", "create_client")]
        return []

    greyed = [{"label": s.get("label"), "price": s.get("price"),
               "why": s.get("disabled_reason_display")}
              for s in land_rows(dialogue) if s.get("available") is False]
    # check (1) reads the opening draft's own land too
    for term in out["opening_terms"]:
        if term.get("type") in ("territory_cede", "create_client") and term.get("from") == "Austria":
            if (table.total(out["opening_terms"], "Austria") or 0) < 50:
                bad_offers.append(f"opening draft: {term.get('region') or term.get('tag')}")
    # the player strips the draft to the bare peace, then takes every land row offered
    with _quiet():
        staged = stage_settlement_confirm(
            world, war_id=war_id, actor_nation="France", settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=["Austria"], selected_target_nation="Austria",
            caller_kind="player_editor", dialogue_mode="PROPOSE")
    dialogue = staged.get("diplomatic_dialogue") or dialogue
    out["bare_total"] = next((r.get("total") for r in dialogue.get("per_court_acceptance") or []
                              if r.get("nation") == "Austria"), None)
    for _ in range(10):
        rows = [s for s in land_rows(dialogue) if s.get("available") is not False]
        if not rows:
            break
        sugg = rows[0]
        params = dict(sugg.get("action_params") or {})
        terms = [dict(t) for t in dialogue.get("settlement_terms") or []]
        clause = ({"type": "territory_cede", "from": "Austria", "to": "France",
                   "region": params.get("region")}
                  if sugg.get("clause_type") == "territory_cede" else
                  {"type": "create_client", "from": "Austria", "to": "France",
                   "tag": params.get("tag"), "provinces": list(sugg.get("provinces") or [])})
        after = table.total(terms + [clause], "Austria")
        offered.append({"label": sugg.get("label"), "price": sugg.get("price"), "after": after})
        if after is None or int(after) < 50:
            bad_offers.append(sugg.get("label"))
        res = _act(world, "settlement_demand_add", dialogue, **params)
        if not res.get("success") or not res.get("diplomatic_dialogue"):
            picks.append({"label": sugg.get("label"), "refused": res.get("error")})
            break
        dialogue = res["diplomatic_dialogue"]
    guided_terms = [dict(t) for t in dialogue.get("settlement_terms") or []]
    out["offered"] = offered
    out["greyed_at_open"] = greyed
    out["guided_terms"] = guided_terms
    out["land_line"] = next((r.get("land_line") for r in dialogue.get("per_court_acceptance") or []
                             if r.get("nation") == "Austria"), None)
    out["fear_line"] = dialogue.get("fear_line")

    # (2) the hand-picks, on a copy: every province Austria still holds
    probe_world = copy.deepcopy(world)
    probe = copy.deepcopy(dialogue)
    hand = []
    last_refused = False
    whole_ever = False
    for region in sorted(probe_world.get_nation_regions("Austria")):
        if any(t.get("region") == region for t in probe.get("settlement_terms") or []):
            continue
        res = _act(probe_world, "settlement_demand_add", probe, nation="Austria", group="demand",
                   clause_type="territory_cede", region=region)
        hand.append({"region": region, "success": bool(res.get("success")), "error": res.get("error")})
        if res.get("error") == "takes_every_province":
            last_refused = True
        if res.get("success") and res.get("diplomatic_dialogue"):
            probe = res["diplomatic_dialogue"]
            if LP.takes_every_province(probe_world, "Austria", probe.get("settlement_terms") or []):
                whole_ever = True
    out["hand_picks"] = hand

    # (3) the buy-all package
    buy_all = ([{"type": "peace"}]
               + [{"type": "territory_cede", "from": "Austria", "to": "France", "region": r}
                  for r in sorted(world.get_nation_regions("Austria"))]
               + [{"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 5000}])
    verdict_all = validate_settlement_terms(buy_all[:8], world=world, war_instance=inst,
                                            proposer_side=side, enforce_solvency=False)
    out["buy_all"] = {"valid": bool(verdict_all.get("valid")), "error": verdict_all.get("error")}

    # (4), (5) the signature
    forecast = F.table_forecast(world, guided_terms)
    before = dict(world.court_grudges)
    held_before = {r for r in TAKEN if world.regions[r].controller == "France"}
    sub = _act(world, "submit_settlement_for_review", dialogue)
    if sub.get("success") and sub.get("diplomatic_dialogue"):
        conf = _act(world, "confirm_settlement", sub["diplomatic_dialogue"])
        signed = {"success": bool(conf.get("success")), "error": conf.get("error"),
                  "message": str(conf.get("message") or "")[:300]}
    else:
        signed = {"success": False, "error": sub.get("error"),
                  "message": str(sub.get("error_display") or "")[:300]}
    after = dict(world.court_grudges)
    delta = {c: after.get(c, 0) - before.get(c, 0) for c in set(after) | set(before)
             if after.get(c, 0) != before.get(c, 0)}
    # the fade does not run inside a signature; the delta is the signature's own
    out["signed"] = signed
    out["austria_after"] = sorted(world.get_nation_regions("Austria"))
    out["austria_stands"] = "Austria" in world.get_active_nations()
    out["fear_forecast"] = forecast["adds"]
    out["fear_written"] = delta
    out["held_land_ceded"] = sorted(r for r in held_before
                                    if any(t.get("region") == r for t in guided_terms))
    out["checks"] = {
        "1_offers_within_the_war": not bad_offers,
        "2_last_province_refused": bool(last_refused) and not whole_ever,
        "3_buy_all_refused": verdict_all.get("error") == "takes_every_province",
        "4_austria_stands": bool(out["austria_after"]) and out["austria_stands"],
        "5_fear_as_forecast": (not signed.get("success")) or delta == {
            c: a for c, a in forecast["adds"].items() if a},
    }
    return out


def verdict(run: dict) -> dict:
    checks = run.get("checks") or {}
    readings = run.get("readings") or {}
    return {"pass": bool(checks) and all(checks.values()),
            "failed": sorted(k for k, ok in checks.items() if not ok),
            "war_score": {k: v.get("war_score") for k, v in readings.items()},
            "signed": {k: (v.get("signed") or {}).get("success") for k, v in readings.items()},
            "land_signed": {k: [t.get("region") or t.get("tag") for t in v.get("guided_terms") or []
                                if t.get("type") in ("territory_cede", "create_client")]
                            for k, v in readings.items()}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--seed", default="historical")
    ap.add_argument("--seeds", default=",".join(SEEDS))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_fun2b_measure_2026_11_27.json"))
    args = ap.parse_args()
    if args.child:
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise SystemExit("PYTHONHASHSEED must be 0 (spawn me as a subprocess)")
        print("PAYLOAD=" + json.dumps(child(args.seed), default=str))
        return 0
    seeds = [s for s in args.seeds.split(",") if s]

    def spawn(seed):
        env = dict(os.environ)
        env.update(PYTHONHASHSEED="0", PYTHONPATH=str(ROOT), SOVEREIGN_SEED=seed, LLM_MODE="mock")
        for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "INK_IRON_SEAMS"):
            env.pop(k, None)
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child",
                               "--seed", seed], env=env, cwd=str(ROOT), capture_output=True,
                              timeout=3600)
        out = proc.stdout.decode("utf-8", errors="replace")
        if proc.returncode != 0:
            return {"seed": seed, "error": proc.stderr.decode("utf-8", errors="replace")[-3000:]}
        return json.loads([ln for ln in out.splitlines() if ln.startswith("PAYLOAD=")][-1][8:])

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        runs = list(pool.map(spawn, seeds))
    record = {"rule": __doc__.split("THE RULE, WRITTEN BEFORE THE DATA")[1].split("    .venv")[0].strip(),
              "notes": NOTES, "runs": {}, "verdicts": {}}
    for run in runs:
        seed = run["seed"]
        record["runs"][seed] = run
        if "error" in run:
            print(f"{seed:>12}: ERROR {str(run['error'])[-400:]}")
            record["verdicts"][seed] = {"pass": False, "error": str(run["error"])[-400:]}
            continue
        record["verdicts"][seed] = verdict(run)
        print(f"{seed:>12}: {record['verdicts'][seed]}")
    passed = sum(1 for s in seeds if record["verdicts"].get(s, {}).get("pass"))
    record["summary"] = {"passed": passed, "of": len(seeds), "bar": len(seeds)}
    print(f"FUN-2b: {passed} of {len(seeds)} seeds pass (bar {len(seeds)})")
    Path(args.out).write_text(json.dumps(record, indent=1, default=str) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
