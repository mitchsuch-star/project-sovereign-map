"""DOCTRINES_SPEC §0.2 — the pre-build reach census of the ten doctrine clauses.

Read-only instrumentation: it changes no rule and writes nothing to the repo
except its own JSON. For each DRAFT clause in `docs/DOCTRINES_SPEC.md` §2 it
counts how often that clause's SEAM is reached by the court that would carry
it, on two kinds of board:

  ambient  the BASELINE_SERIES board — 40 turns, a passive France, the M7
           per-turn re-seed — on the named campaign seeds
  driver   `tools/playtest_driver.py` with a committed script (a France that
           is commanded), 40 turns, `--objection insist --diplomacy decline`

What is counted (per nation):
  - arrival rolls, with each roll's deterministic sum, and the arrival odds
    the roll would have under a ±10 SCORE shift vs a ±10 THRESHOLD shift
    (DOCTRINES_SPEC RV-1: the 5% fumble above 80 makes the score shift
    non-monotone);
  - battles by side, and the lopsided-defeat morale penalty the loser paid
    (`combat.decisiveness_morale_penalty`);
  - recruits by arm (the manpower pool that fell — so the substitute market
    and marshal commissions, which draw no manpower, are NOT counted);
  - drill completions, and whether the corps ended the drill at 95 morale or
    less (room for the whole of a +5 more);
  - marshal-turns an army stood UNFED (D-R2: not home soil, not an ALLY or
    VASSAL host, no naval lifeline), in the authored DRAFT poor-country list,
    and in stripped country (war damage >= 0.20 / 0.25 / 0.30), read where
    the attrition pass reads it — after that turn's war-damage recovery tick;
  - the five great powers' treasuries at attrition passes 1/11/21/31/40
    (each sampled before that turn's income).

Each arm runs in its own subprocess with PYTHONHASHSEED=0 and LLM_MODE=mock
(the series idiom); the instrumentation is installed IN THE CHILD before the
board boots, and it only wraps — every wrapped call returns the original's
result unchanged.

    .venv/Scripts/python.exe tools/_dc_reach_census.py [--arms all|name,name]

Writes tools/_dc_reach_census.json (committed with the review, DOCTRINES_SPEC
§0.2). Rerun it at DC-1 against the lever-up tree: T6 compares the two.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DRIVER = ROOT / "tools" / "playtest_driver.py"

# The DRAFT authored list (DOCTRINES_SPEC D-R1).
POOR = ["East Prussia", "Posen", "Samogitia", "Lithuania", "White Russia",
        "Volhynia", "Leon", "Aragon", "Galicia", "Alentejo", "Beira",
        "Rumelia", "Epirus", "Albania"]
GREAT = ["France", "Britain", "Russia", "Austria", "Prussia"]

ARMS = {
    "ambient-historical": {"mode": "ambient", "seed": "historical"},
    "ambient-ulm": {"mode": "ambient", "seed": "ulm"},
    "ambient-austerlitz": {"mode": "ambient", "seed": "austerlitz"},
    "ambient-eylau": {"mode": "ambient", "seed": "eylau"},
    "commanded-full40": {"mode": "driver", "seed": "historical",
                         "script": "commanded_full40.json"},
    "aar-road": {"mode": "driver", "seed": "historical",
                 "script": "sr1e_aar_road.json"},
    "pressburg-road": {"mode": "driver", "seed": "historical",
                       "script": "gev_pressburg_road.json"},
    # SR-7d DC-1 (DOCTRINES_SPEC T3 / T6): the Jena road — a real campaign
    # that goes to war with Prussia and marches east to Posen and East
    # Prussia, so Prussia's and Russia's clauses are reached and France's
    # flaw bites on the listed poor country.
    "jena-road": {"mode": "driver", "seed": "historical",
                  "script": "dc_jena_road.json"},
}


# ════════════════════════════════════════════════════════════════════════
# THE CHILD — instrumentation (wrap, count, return the original's result)
# ════════════════════════════════════════════════════════════════════════

def _p_arrive(det: int, thr: int, v: int = 8) -> float:
    """The resolver's own arrival probability (`_arrival_probability`),
    restated so the census can price counterfactual shifts: score > thr over
    a uniform jitter of ±v, then a 5% fumble when the score is above 80."""
    tot = 0.0
    for j in range(-v, v + 1):
        s = det + j
        if s <= thr:
            continue
        tot += 0.95 if s > 80 else 1.0
    return tot / (2 * v + 1)


def child(mode: str, seed: str, script: str) -> None:
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    import backend.commands.combat_executor as CE
    import backend.commands.economy_executor as EE
    import backend.game_logic.combat as CB
    import backend.models.world_state as WS

    C = collections.Counter()
    ARR = collections.defaultdict(list)

    # ── SR-7d (the lever-up tree): the doctrine seams themselves, counted
    # where they fire — a supply BITE is the bill (forecast=False) reading a
    # factor under 1.0, never a predicate hit (T6).
    try:
        import backend.game_logic.doctrines as DC
        _o_supply = DC.supply_factor

        def _supply(world, nation, region, forecast=True, extra_damage=0.0):
            out = _o_supply(world, nation, region, forecast, extra_damage)
            if out[0] < 1.0:
                key = "bill" if not forecast else "forecast"
                C[f"doctrine_supply_{key}|{nation}"] += 1
                if key == "bill" and region is not None and getattr(region, "controller", None) == nation:
                    C[f"doctrine_supply_bill_on_conquered|{nation}"] += 1
            return out
        DC.supply_factor = _supply

        _o_shift = DC.arrival_bar_shift

        def _shift(world, reinforcer, primary):
            out = _o_shift(world, reinforcer, primary)
            if out[0]:
                C[f"doctrine_arrival_shift|{nation_of(reinforcer)}|{out[1]}"] += 1
            return out
        DC.arrival_bar_shift = _shift

        _o_rec = DC.recruit_price_term

        def _rec(world, nation):
            out = _o_rec(world, nation)
            if out:
                C[f"doctrine_recruit_term|{nation}"] += 1
            return out
        DC.recruit_price_term = _rec

        _o_pen = DC.scaled_defeat_penalty

        def _pen(marshal, base):
            out = _o_pen(marshal, base)
            if out[1] is not None:
                C[f"doctrine_defeat_scaled|{nation_of(marshal)}|{out[1]['name']}"] += 1
            return out
        DC.scaled_defeat_penalty = _pen

        _o_cured = DC.flaw_cured

        def _cured(world, nation):
            out = _o_cured(world, nation)
            if out:
                C[f"doctrine_cured_reads|{nation}"] += 1
            return out
        DC.flaw_cured = _cured
    except Exception as exc:                              # pragma: no cover
        C["doctrine_spy_error"] = repr(exc)
    DEC = collections.defaultdict(list)
    SUP = collections.defaultdict(list)
    DRILL = collections.defaultdict(list)
    TREAS = collections.defaultdict(list)
    REC = collections.Counter()
    SIDES = collections.Counter()
    last_world = {"w": None}

    def nation_of(m):
        return getattr(m, "nation", "?")

    orig_score = CE.CombatExecutor._calculate_arrival_score
    battle_ctx = {"region": None}

    def score(self, reinforcing_marshal, primary_combatant, world):
        det = self._arrival_deterministic(reinforcing_marshal, primary_combatant, world)
        # The resolver's own bar (a SUPPORT for the primary, or a PURSUE whose
        # quarry stands in the battle region, is a written order: 60, else
        # 65) — read through `_arrival_threshold`, which restates it exactly.
        thr = self._arrival_threshold(reinforcing_marshal, primary_combatant,
                                      battle_ctx["region"], world)
        # RV-2: the three causes of a man's own that the corps system must
        # not offset — an ability that keeps him away, a live grievance
        # against the lead, a hostile pair.
        ability = (getattr(reinforcing_marshal, "ability", None) or {}).get("name", "")
        exempt = (ability == "Eyes on a Crown"
                  or getattr(reinforcing_marshal, "jealous_of", None) == primary_combatant.name
                  or reinforcing_marshal.get_relationship(primary_combatant.name) == -2)
        ARR[nation_of(reinforcing_marshal)].append((int(det), int(thr), bool(exempt)))
        return orig_score(self, reinforcing_marshal, primary_combatant, world)

    CE.CombatExecutor._calculate_arrival_score = score

    orig_reinf = CE.CombatExecutor._calculate_reinforcements

    def reinf(self, primary, defender, battle_region, nation, world):
        battle_ctx["region"] = battle_region
        out = orig_reinf(self, primary, defender, battle_region, nation, world)
        for r in out or []:
            if r.get("reason") == "literal_personality":
                C[f"literal_no_march|{nation_of(world.marshals.get(r.get('marshal')))}"] += 1
            if r.get("reason") == "doctrine_delayed":
                C[f"doctrine_delayed|{nation_of(world.marshals.get(r.get('marshal')))}"] += 1
            if r.get("doctrine_arrived"):
                C[f"doctrine_arrived|{nation_of(world.marshals.get(r.get('marshal')))}"] += 1
        return out

    CE.CombatExecutor._calculate_reinforcements = reinf

    orig_rb = CB.CombatResolver.resolve_battle

    def rb(self, attacker, defender, *a, **kw):
        out = orig_rb(self, attacker, defender, *a, **kw)
        SIDES[("attacker", nation_of(attacker))] += 1
        SIDES[("defender", nation_of(defender))] += 1
        outcome = out.get("raw_outcome") or out.get("outcome")
        # The deferred (coordinated) result carries the raw casualties at the
        # top level; the immediate (solo) result nests them per side.
        if "attacker_raw_casualties" in out:
            ac = out["attacker_raw_casualties"]
            dc = out["defender_raw_casualties"]
        else:
            ac = (out.get("attacker") or {}).get("casualties", 0)
            dc = (out.get("defender") or {}).get("casualties", 0)
        if outcome in ("defender_victory", "defender_tactical_victory"):
            DEC[nation_of(attacker)].append(CB.decisiveness_morale_penalty(ac, dc))
        elif outcome in ("attacker_victory", "attacker_tactical_victory"):
            DEC[nation_of(defender)].append(CB.decisiveness_morale_penalty(dc, ac))
        return out

    CB.CombatResolver.resolve_battle = rb

    orig_recruit = EE.EconomyExecutor._execute_recruit

    def recruit(self, command, game_state, raw_text=""):
        world = game_state.get("world")
        before = ({n: dict(p) for n, p in (world.manpower_pools or {}).items()}
                  if world else {})
        out = orig_recruit(self, command, game_state, raw_text=raw_text)
        if world is not None and isinstance(out, dict) and out.get("success"):
            for n, pool in (world.manpower_pools or {}).items():
                for arm, v in pool.items():
                    if v < before.get(n, {}).get(arm, v):
                        REC[(n, arm)] += 1
        return out

    EE.EconomyExecutor._execute_recruit = recruit

    orig_drill = WS.WorldState._apply_drill_morale

    def drill(self, marshal):
        before = int(marshal.morale)
        gain = orig_drill(self, marshal)
        DRILL[nation_of(marshal)].append((before, int(gain)))
        return gain

    WS.WorldState._apply_drill_morale = drill

    orig_attr = WS.WorldState.process_supply_attrition

    home_regions = {}

    def bite(self, m, region, factor):
        """Would a cap of `factor` × today's effective cap raise this
        marshal's attrition rate? Pooled nation-blind, as the engine pools."""
        here = [x for x in self.marshals.values()
                if x.location == region.name and x.strength > 0]
        total = sum(x.strength for x in here)
        cap_now = self.get_effective_supply_cap(m.nation, region)
        cap_flaw = int(region.supply_capacity
                       * self._supply_multiplier(m.nation, region) * factor)
        r_now = WS.WorldState.supply_attrition_rate(total, cap_now, len(here))
        r_flaw = WS.WorldState.supply_attrition_rate(total, cap_flaw, len(here))
        return (r_flaw - r_now) * m.strength

    def france_flaw(self):
        """DOCTRINES_SPEC P1 (the design review): living off the land read
        two ways, for every French marshal at this pass —
          FLAG      D-R2 as drafted: not controlled by France, not an ally or
                    vassal host, no lifeline (the army is unfed today);
          HOMELAND  the amended reading: outside France's 1805 homeland and
                    not on an ally's or vassal's soil, whoever holds it — a
                    conquered province feeds at 80% of its fed rate.
        Each in the listed poor country or stripped country (>= 0.25)."""
        if not home_regions:
            home_regions.update({r: n for n, rs in
                                 (getattr(self, "nation_starting_regions", {}) or {}).items()
                                 for r in rs})
        for m in list(self.marshals.values()):
            if m.nation != "France" or getattr(m, "strength", 0) <= 0:
                continue
            region = self.get_region(m.location)
            if region is None or not region.controller:
                continue
            wd = float(getattr(region, "war_damage", 0.0) or 0.0)
            poor = region.name in POOR or wd >= 0.25
            if not poor:
                continue
            ally_host = (region.controller != "France"
                         and self.get_diplomatic_state("France", region.controller)
                         in self.ALLY_SUPPLY_STATES)
            unfed_today = (region.controller != "France" and not ally_host
                           and self._supply_multiplier("France", region) == 1.0)
            homeland = home_regions.get(region.name) == "France"
            for key, applies in (("FLAG", unfed_today),
                                 ("HOMELAND", (not homeland) and not ally_host)):
                if not applies:
                    continue
                C[f"france_flaw_hits|{key}"] += 1
                extra = bite(self, m, region, 0.8)
                if extra > 0:
                    C[f"france_flaw_bites|{key}"] += 1
                    C[f"france_flaw_extra_men|{key}"] += int(extra)
                    if region.controller == "France":
                        C[f"france_flaw_bites_on_conquered|{key}"] += 1

    def attr(self):
        last_world["w"] = self
        france_flaw(self)
        for m in list(self.marshals.values()):
            if getattr(m, "strength", 0) <= 0:
                continue
            region = self.get_region(m.location)
            if region is None or not region.controller:
                continue
            # UNFED as D-R2 defines it: not home soil, not an ALLY/VASSAL
            # host, and no naval lifeline. The multiplier alone cannot say
            # it — a home coast STRANGLED by a hostile fleet also reads 1.0,
            # and home soil never takes the flaw.
            fed_by_land = (region.controller == m.nation
                           or self.get_diplomatic_state(m.nation, region.controller)
                           in self.ALLY_SUPPLY_STATES)
            if fed_by_land:
                if self._supply_multiplier(m.nation, region) == 1.0:
                    C[f"home_or_ally_strangled|{m.nation}"] += 1
                continue
            if self._supply_multiplier(m.nation, region) != 1.0:
                continue  # a naval lifeline feeds him
            C[f"unfed|{m.nation}"] += 1
            wd = float(getattr(region, "war_damage", 0.0) or 0.0)
            for t in (0.2, 0.25, 0.3):
                if wd >= t:
                    C[f"unfed_stripped>={t}|{m.nation}"] += 1
            if region.name in POOR:
                C[f"unfed_in_listed_poor|{m.nation}"] += 1
                SUP[m.nation].append(region.name)
            here = sum(x.strength for x in self.marshals.values()
                       if x.location == region.name and x.strength > 0
                       and x.nation == m.nation)
            if here > int(region.supply_capacity * 0.8):
                C[f"unfed_over_80pct_cap|{m.nation}"] += 1
        for n in GREAT:
            TREAS[n].append(int(self.nation_gold.get(n, 0)))
        return orig_attr(self)

    WS.WorldState.process_supply_attrition = attr

    if mode == "ambient":
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        world = WS.WorldState.from_scenario(str(SCENARIO))
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        game_state = {"world": world, "executor": executor}
        for turn in range(40):
            random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
            tm.end_turn(game_state)
        last_world["w"] = world
    else:
        out_dir = tempfile.mkdtemp(prefix="dc_reach_")
        sys.argv = [str(DRIVER), "--name", "dc_reach", "--turns", "40",
                    "--script", str(ROOT / "tools" / "playtest_scripts" / script),
                    "--objection", "insist", "--diplomacy", "decline",
                    "--out", out_dir]
        try:
            runpy.run_path(str(DRIVER), run_name="__main__")
        except SystemExit:
            pass

    rep = {"arrival": {}, "lopsided_defeats": {}, "battles": {}, "recruits": {},
           "drills": {}, "unfed_in_listed_poor": {}, "counters": dict(C),
           "treasury_at_attrition_pass_1_11_21_31_40": {}}
    for n, rows in ARR.items():
        k = max(len(rows), 1)
        worse = better = exempt_rolls = 0
        acc = {"base": 0.0, "score+10": 0.0, "score-10": 0.0, "bar-10": 0.0,
               "bar+10": 0.0, "bar-10_with_RV2_exemptions": 0.0}
        for det, thr, exempt in rows:
            p0 = _p_arrive(det, thr)
            pu, pd = _p_arrive(det + 10, thr), _p_arrive(det - 10, thr)
            acc["base"] += p0
            acc["score+10"] += pu
            acc["score-10"] += pd
            acc["bar-10"] += _p_arrive(det, thr - 10)
            acc["bar+10"] += _p_arrive(det, thr + 10)
            acc["bar-10_with_RV2_exemptions"] += p0 if exempt else _p_arrive(det, thr - 10)
            worse += pu < p0 - 1e-9
            better += pd > p0 + 1e-9
            exempt_rolls += exempt
        rep["arrival"][n] = {
            "rolls": len(rows),
            "mean_deterministic": round(sum(r[0] for r in rows) / k, 1),
            **{f"P_{key}": round(v / k, 3) for key, v in acc.items()},
            "rolls_a_+10_score_makes_LESS_likely": worse,
            "rolls_a_-10_score_makes_MORE_likely": better,
            "rolls_RV2_would_exempt": exempt_rolls,
        }
    for n, v in DEC.items():
        paid = [x for x in v if x > 0]
        rep["lopsided_defeats"][n] = {"defeats": len(v), "penalty_paid": len(paid),
                                      "mean_penalty_paid": round(sum(paid) / max(1, len(paid)), 1)}
    rep["battles"] = {f"{role}|{n}": c for (role, n), c in sorted(SIDES.items())}
    rep["recruits"] = {f"{n}|{arm}": c for (n, arm), c in sorted(REC.items())}
    rep["drills"] = {n: {"drills": len(v),
                         "room_for_five_more_morale": sum(1 for b, g in v if b + g <= 95)}
                     for n, v in DRILL.items()}
    rep["unfed_in_listed_poor"] = {n: sorted(set(v)) for n, v in SUP.items()}
    # Sampled inside each turn's attrition pass, before that turn's income:
    # pass 21 is the chest a court carries into turn 21's income, i.e. about
    # "turn 20" in the spec's prose.
    rep["treasury_at_attrition_pass_1_11_21_31_40"] = {
        n: [v[i] for i in (0, 10, 20, 30, 39) if i < len(v)] for n, v in TREAS.items()}
    w = last_world["w"]
    if w is not None:
        rep["artillery_marshals_at_end"] = sorted(
            f"{m.nation}:{k}" for k, m in w.marshals.items() if getattr(m, "artillery", False))
    print("CENSUS=" + json.dumps(rep))


# ════════════════════════════════════════════════════════════════════════
# THE PARENT — one subprocess per arm, hash-pinned
# ════════════════════════════════════════════════════════════════════════

def run_arm(name: str, spec: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = spec["seed"]
    env["LLM_MODE"] = "mock"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING"):
        env.pop(key, None)
    cmd = [sys.executable, str(Path(__file__).resolve()), "--child",
           spec["mode"], spec["seed"], spec.get("script", "")]
    proc = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=3600)
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("CENSUS=")]
    if proc.returncode != 0 or not lines:
        raise SystemExit(f"arm {name} failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    return json.loads(lines[-1][len("CENSUS="):])


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="all")
    ap.add_argument("--out", default=str(ROOT / "tools" / "_dc_reach_census.json"))
    args = ap.parse_args()
    wanted = list(ARMS) if args.arms == "all" else args.arms.split(",")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {name: pool.submit(run_arm, name, ARMS[name]) for name in wanted}
        results = {name: fut.result() for name, fut in futures.items()}
    for name in wanted:
        r = results[name]
        print(f"== {name}")
        print("   arrival rolls:", {n: v["rolls"] for n, v in r["arrival"].items()})
        print("   battles:", r["battles"])
        print("   recruits:", r["recruits"])
        print("   drills:", r["drills"])
        print("   lopsided defeats:", r["lopsided_defeats"])
        print("   counters:", {k: v for k, v in r["counters"].items() if not k.startswith("doctrine_")})
        print("   doctrine:", {k: v for k, v in r["counters"].items() if k.startswith("doctrine_")})
    Path(args.out).write_text(json.dumps({
        "about": ("DOCTRINES_SPEC §0.2 reach census; re-run at SR-7d DC-1 on the lever-up "
                  "tree with the Jena road (T6) — the doctrine_* counters are the seams "
                  "themselves (a supply BITE = the bill reading a factor under 1.0); the "
                  "pre-build france_flaw_* counters are kept for the comparison and now read "
                  "against a cap the flaw has already reduced"),
        "poor_country_draft": POOR,
        "arms": {name: {"spec": ARMS[name], "census": results[name]} for name in wanted}},
        indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
