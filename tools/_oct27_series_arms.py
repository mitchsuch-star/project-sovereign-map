"""The October 27, 2026 enemy-AI sweep — the BASELINE_SERIES attribution.

Seven read-only audits over the enemy diplomacy AI and the enemy military AI
landed ~40 fixes in one commit; the ambient 40-turn historical series
(`tests/test_ai_intent_threat_migration.py --emit-series`) moved. Every
backend seam the AI's path walks is an ARM here: the arm runs the shipped
tree with THAT seam's function(s) swapped back to their HEAD (pre-sweep)
bodies — loaded from `git show HEAD:<path>` into a scratch module, so the
old body runs against the current helpers — and reports where its series
first diverges from the prior. Arm 0 swaps EVERY seam back and must
reproduce the prior series byte for byte; ALL is the shipped tree, the
series to record.

    python tools/_oct27_series_arms.py [--arms 0,AIR,P7,...,ALL] [--jobs 3]

Arms (the sweep's rows, `docs/BUG_FIXES.md` §OCT27):
    AIR  the AI-AI refusal: a balking proposer records nothing; a recipient's
         refusal rests the ordered pair (`_resolve_ai_ai_proposal`)
    P7   the proposal rungs' slot gates: P7's refused pact, the sell-
         neutrality ask the transport withholds, the repeat-ask aside
         (`process_diplomatic_phase`, `_generate_intent_ask`)
    BUD  the mailbox budgets count delivered letters
         (`TurnManager._process_ai_diplomatic_phase`)
    RG   the repeat-ask governor and the never-shorter rejection cooldown
         (`apply_rejection_cooldowns`)
    FL   a refusal flushes the intent cache (`record_diplomatic_refusal`)
    AU   the allegiance auction's rest, its already-allied and fallen closes
         (`process_allegiance_auctions`, `_announce_allegiance_close`)
    PR   the province-return tick never moves the player's province
         (`process_province_returns`)
    AL   the alignment ask yields inside the dedupe window
         (`_evaluate_ai_ai_proposal`)
    GB   the counter's gold bridge prices the line (`_gold_bridge_counter`,
         `_try_add_desired_clauses`)
    RV   the rivalry's region scan through the per-turn cache
         (`_process_ai_ai_rivalry`)
    CO   the coalition: the lowered gate's cancel floor, the exhaustion
         mark's re-arm, the successor's target, the pivot's card
         (`process_coalition_turn`, `add_war_exhaustion_from_battle`,
         `remove_coalition_member`)
    OB   an ally is never the obstacle (`agendas._acquire_active`,
         `agendas._unmet_targets`, `intent._derive_against`)
    GU   a dead or client guarantor answers for nobody
         (`instruments.live_guarantees_of` -> the unfiltered read)
    WC   the war council: overtaken, the consecutive stall, the failed
         declaration, the dead guarantor (`_crisis_cause_of_death`,
         `process_war_council`, `_honour_guarantees`)
    FR   the frontier cache flushes with its siblings
         (`WorldState.invalidate_bloc_members_cache`)
    TP   the third-party peace: the applied terms, the broker guard, the
         capped pair-exit floor (`attempt_third_party_settlement`,
         `pair_is_mutually_exhausted`)
    BD   the bond's exhaustion depth one short of the cap
         (`bond.depth_for_strength`)
    CG   the Congress fore-warning latch (`congress._take_answers`)
    MG   the war-instance merge keeps the letters and sureties
         (`settlement_helpers._merge_instance_data`)
    TR   the ratifier reads a demand's direction by either spelling
         (`treaty.treaty_clauses_of`)
    RD   the readiness letter reads P1's own choice (`court_own_readiness`;
         a display field, armed to prove it)
    EA1  P3.8 liberation at war and across open water
    EA2  P3.5 the fortified corps' capture intent gated
    EA3  P3.7 homeland defence across open water
    EA4  the action budget (`_process_nation_turn_marked`)
    EA5  the engagement rungs never strike a league fellow
         (`_engageable_enemies`, `_get_counter_punch_action`,
         `jealousy.find_autonomous_attack_target`)
    EA6  reckless cavalry takes an empty province
         (`CombatExecutor._attack_reckless_cavalry`)
    EA7  the recovery rung: fortified waits, a held destination re-picks
    EA8  the supply move never walks into a held province
    EA9  the artillery screen's unfortify (`_evaluate_marshal`)
    EA10 artillery still setting up takes no walk-in
         (`_find_undefended_capture`)
    EA11 a stance order the marshal's blood forbids
         (`_select_next_marshal_action`)
    EA12 the survival action reads the defend predicate
         (`_get_survival_action`)
    EA13 P4.6's ordered staging frontier and its ally fallback
         (`_find_coordinated_attack`)
    EA14 the surrounded arm never strikes a league fellow
         (`_get_stagnation_action`)

LOADONLY loads every HEAD module and swaps nothing (the import side effects
alone; it must equal ALL). Display-only changes are not armed (they cannot move the series): the
dissolution reason's words, the raw tags in the letters, the bargain rail's
names, the auction's close lines, the chronicle's article, the war title's
suffix, the settlement rail's frame, the readiness letter's word, the
override send's verdict and the failed ratification's cooldown (player
roads). Writes tools/_oct27_series_arms_final.json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "test_ai_intent_threat_migration.py"

OLD_MODULES = {
    "ai_diplomacy": "backend/game_logic/ai_diplomacy.py",
    "coalition": "backend/game_logic/coalition.py",
    "agendas": "backend/game_logic/agendas.py",
    "intent": "backend/game_logic/intent.py",
    "war_council": "backend/game_logic/war_council.py",
    "settlement_third_party": "backend/game_logic/settlement_third_party.py",
    "bond": "backend/game_logic/bond.py",
    "congress": "backend/game_logic/congress.py",
    "settlement_helpers": "backend/game_logic/settlement_helpers.py",
    "treaty": "backend/game_logic/treaty.py",
    "enemy_ai": "backend/ai/enemy_ai.py",
    "jealousy": "backend/game_logic/jealousy.py",
    "combat_executor": "backend/commands/combat_executor.py",
    "turn_manager": "backend/game_logic/turn_manager.py",
    "world_state": "backend/models/world_state.py",
}

# arm -> [(current module import path, attribute path, old module key, old attribute path)]
SWAPS = {
    "AIR": [("backend.game_logic.ai_diplomacy", "_resolve_ai_ai_proposal", "ai_diplomacy", "_resolve_ai_ai_proposal")],
    "P7": [("backend.game_logic.ai_diplomacy", "process_diplomatic_phase", "ai_diplomacy", "process_diplomatic_phase"),
           ("backend.game_logic.ai_diplomacy", "_generate_intent_ask", "ai_diplomacy", "_generate_intent_ask")],
    "BUD": [("backend.game_logic.turn_manager", "TurnManager._process_ai_diplomatic_phase", "turn_manager", "TurnManager._process_ai_diplomatic_phase")],
    "RG": [("backend.game_logic.ai_diplomacy", "apply_rejection_cooldowns", "ai_diplomacy", "apply_rejection_cooldowns")],
    "FL": [("backend.game_logic.ai_diplomacy", "record_diplomatic_refusal", "ai_diplomacy", "record_diplomatic_refusal")],
    "AU": [("backend.game_logic.ai_diplomacy", "process_allegiance_auctions", "ai_diplomacy", "process_allegiance_auctions"),
           ("backend.game_logic.ai_diplomacy", "_announce_allegiance_close", "ai_diplomacy", "_announce_allegiance_close")],
    "PR": [("backend.game_logic.ai_diplomacy", "process_province_returns", "ai_diplomacy", "process_province_returns")],
    "AL": [("backend.game_logic.ai_diplomacy", "_evaluate_ai_ai_proposal", "ai_diplomacy", "_evaluate_ai_ai_proposal")],
    "GB": [("backend.game_logic.ai_diplomacy", "_gold_bridge_counter", "ai_diplomacy", "_gold_bridge_counter"),
           ("backend.game_logic.ai_diplomacy", "_try_add_desired_clauses", "ai_diplomacy", "_try_add_desired_clauses")],
    "RV": [("backend.game_logic.ai_diplomacy", "_process_ai_ai_rivalry", "ai_diplomacy", "_process_ai_ai_rivalry")],
    "CO": [("backend.game_logic.coalition", "process_coalition_turn", "coalition", "process_coalition_turn"),
           ("backend.game_logic.coalition", "add_war_exhaustion_from_battle", "coalition", "add_war_exhaustion_from_battle"),
           ("backend.game_logic.coalition", "remove_coalition_member", "coalition", "remove_coalition_member")],
    "OB": [("backend.game_logic.agendas", "_acquire_active", "agendas", "_acquire_active"),
           ("backend.game_logic.agendas", "_unmet_targets", "agendas", "_unmet_targets"),
           ("backend.game_logic.intent", "_derive_against", "intent", "_derive_against")],
    "GU": [("backend.game_logic.instruments", "live_guarantees_of", None, "UNFILTERED")],
    "WC": [("backend.game_logic.war_council", "_crisis_cause_of_death", "war_council", "_crisis_cause_of_death"),
           ("backend.game_logic.war_council", "process_war_council", "war_council", "process_war_council"),
           ("backend.game_logic.war_council", "_honour_guarantees", "war_council", "_honour_guarantees")],
    "FR": [("backend.models.world_state", "WorldState.invalidate_bloc_members_cache", "world_state", "WorldState.invalidate_bloc_members_cache")],
    "TP": [("backend.game_logic.settlement_third_party", "attempt_third_party_settlement", "settlement_third_party", "attempt_third_party_settlement"),
           ("backend.game_logic.settlement_third_party", "pair_is_mutually_exhausted", "settlement_third_party", "pair_is_mutually_exhausted")],
    "BD": [("backend.game_logic.bond", "depth_for_strength", "bond", "depth_for_strength")],
    "CG": [("backend.game_logic.congress", "_take_answers", "congress", "_take_answers")],
    "MG": [("backend.game_logic.settlement_helpers", "_merge_instance_data", "settlement_helpers", "_merge_instance_data")],
    "TR": [("backend.game_logic.treaty", "treaty_clauses_of", "treaty", "treaty_clauses_of")],
    "RD": [("backend.game_logic.ai_diplomacy", "court_own_readiness", "ai_diplomacy", "court_own_readiness")],
    "EA1": [("backend.ai.enemy_ai", "EnemyAI._find_liberation_target", "enemy_ai", "EnemyAI._find_liberation_target")],
    "EA2": [("backend.ai.enemy_ai", "EnemyAI._check_fortification_opportunity", "enemy_ai", "EnemyAI._check_fortification_opportunity")],
    "EA3": [("backend.ai.enemy_ai", "EnemyAI._find_homeland_defense", "enemy_ai", "EnemyAI._find_homeland_defense")],
    "EA4": [("backend.ai.enemy_ai", "EnemyAI._process_nation_turn_marked", "enemy_ai", "EnemyAI._process_nation_turn_marked")],
    "EA5": [("backend.ai.enemy_ai", "EnemyAI._engageable_enemies", "enemy_ai", "EnemyAI._engageable_enemies"),
            ("backend.ai.enemy_ai", "EnemyAI._get_counter_punch_action", "enemy_ai", "EnemyAI._get_counter_punch_action"),
            ("backend.game_logic.jealousy", "find_autonomous_attack_target", "jealousy", "find_autonomous_attack_target")],
    "EA6": [("backend.commands.combat_executor", "CombatExecutor._attack_reckless_cavalry", "combat_executor", "CombatExecutor._attack_reckless_cavalry")],
    "EA7": [("backend.ai.enemy_ai", "EnemyAI._get_recovery_action", "enemy_ai", "EnemyAI._get_recovery_action")],
    "EA8": [("backend.ai.enemy_ai", "EnemyAI._supply_pressure_move", "enemy_ai", "EnemyAI._supply_pressure_move")],
    "EA9": [("backend.ai.enemy_ai", "EnemyAI._evaluate_marshal", "enemy_ai", "EnemyAI._evaluate_marshal")],
    "EA10": [("backend.ai.enemy_ai", "EnemyAI._find_undefended_capture", "enemy_ai", "EnemyAI._find_undefended_capture")],
    "EA11": [("backend.ai.enemy_ai", "EnemyAI._select_next_marshal_action", "enemy_ai", "EnemyAI._select_next_marshal_action")],
    "EA12": [("backend.ai.enemy_ai", "EnemyAI._get_survival_action", "enemy_ai", "EnemyAI._get_survival_action")],
    "EA13": [("backend.ai.enemy_ai", "EnemyAI._find_coordinated_attack", "enemy_ai", "EnemyAI._find_coordinated_attack")],
    "EA14": [("backend.ai.enemy_ai", "EnemyAI._get_stagnation_action", "enemy_ai", "EnemyAI._get_stagnation_action")],
    "EA15": [("backend.ai.enemy_ai", "EnemyAI._stagnation_fallback_dests", None, "ALLDESTS")],
}
SEAMS = tuple(SWAPS)
ARMS = {"0": set(SEAMS), **{s: {s} for s in SEAMS}, "ALL": set(), "LOADONLY": {"LOADONLY"}}

CHILD = r"""
import sys, runpy, importlib.util, functools, types
DOWN = set({down!r})
OLD_DIR = r"{old_dir}"
SWAPS = {swaps!r}
_old_cache = {{}}
def _old(key):
    if key not in _old_cache:
        spec = importlib.util.spec_from_file_location("oct27_old_" + key, OLD_DIR + "/" + key + ".py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod      # dataclasses resolve their module by name
        spec.loader.exec_module(mod)
        _old_cache[key] = mod
    return _old_cache[key]
def _resolve(obj, dotted):
    parts = dotted.split(".")
    for p in parts[:-1]:
        obj = getattr(obj, p)
    return obj, parts[-1]
import importlib
def _rebind(old_fn, cur_module):
    # The HEAD body run against the CURRENT module's globals - its levers,
    # its helpers - so an arm isolates exactly one function's logic.
    fn = types.FunctionType(old_fn.__code__, cur_module.__dict__, old_fn.__name__,
                            old_fn.__defaults__, old_fn.__closure__)
    fn.__kwdefaults__ = old_fn.__kwdefaults__
    fn.__doc__ = old_fn.__doc__
    return fn
if "LOADONLY" in DOWN:
    # Load every HEAD module and swap nothing: the import side effects alone.
    for key in {oldkeys!r}:
        _old(key)
    DOWN = set()
for arm in sorted(DOWN):
    for cur_mod, cur_attr, old_key, old_attr in SWAPS[arm]:
        cur_module = importlib.import_module(cur_mod)
        target, name = _resolve(cur_module, cur_attr)
        if old_key is None and old_attr == "UNFILTERED":
            def _unfiltered(world, protected):
                return [r for r in (getattr(world, "diplomatic_guarantees", []) or [])
                        if isinstance(r, dict) and r.get("protected") == protected]
            setattr(target, name, _unfiltered)
            continue
        if old_key is None and old_attr == "ALLDESTS":
            def _all_dests(self, world, origin, target_region, dests):
                return list(dests)
            setattr(target, name, _all_dests)
            continue
        holder, oname = _resolve(_old(old_key), old_attr)
        old_fn = _rebind(getattr(holder, oname), cur_module)
        if arm == "RG":
            _inner = old_fn
            def old_fn(*a, escalate=True, **k):
                return _inner(*a, **k)
        setattr(target, name, old_fn)
sys.argv = [r"{runner}", "--emit-series"]
runpy.run_path(r"{runner}", run_name="__main__")
"""


def _write_old_modules() -> str:
    old_dir = tempfile.mkdtemp(prefix="oct27_old_")
    for key, rel in OLD_MODULES.items():
        blob = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                              capture_output=True, check=True).stdout
        Path(old_dir, key + ".py").write_bytes(blob)
    return old_dir


def run_arm(down: set, old_dir: str) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    for k in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE"):
        env.pop(k, None)
    code = CHILD.format(down=sorted(down), runner=str(RUNNER), old_dir=old_dir,
                        swaps={k: SWAPS[k] for k in sorted(down) if k in SWAPS},
                        oldkeys=sorted(OLD_MODULES))
    proc = subprocess.run([sys.executable, "-c", code], env=env, cwd=str(ROOT),
                          capture_output=True, timeout=3600)
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"arm {sorted(down)} failed:\n{stdout[-2000:]}\n{stderr[-3000:]}")
    lines = stdout.splitlines()
    payload = json.loads([ln for ln in lines if ln.startswith("PAYLOAD=")][-1][len("PAYLOAD="):])
    return payload


def first_divergence(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def prior_series() -> list:
    # HEAD's series, never the working tree's: the sweep re-pins
    # BASELINE_SERIES, and a re-run must still attribute against the prior.
    rel = RUNNER.relative_to(ROOT).as_posix()
    text = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                          capture_output=True, check=True).stdout.decode("utf-8")
    m = re.search(r"^BASELINE_SERIES = (\[[^\]]*\])", text, re.M)
    return json.loads(m.group(1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default=str(ROOT / "tools" / "_oct27_series_arms_final.json"))
    args = ap.parse_args()
    prior = prior_series()
    names = [x.strip() for x in args.arms.split(",") if x.strip()]
    old_dir = _write_old_modules()
    out = {"prior": prior, "seams_down": {k: sorted(ARMS[k]) for k in names}, "arms": {}}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = dict(zip(names, pool.map(lambda a: run_arm(ARMS[a], old_dir), names)))
    shipped = results["ALL"]["series"] if "ALL" in results else None
    for arm in names:
        payload = results[arm]
        series = payload["series"]
        out["arms"][arm] = {"down": sorted(ARMS[arm]), "series": series,
                            "first_divergence_vs_prior": first_divergence(series, prior),
                            "first_divergence_vs_shipped": (first_divergence(series, shipped)
                                                            if shipped is not None else None)}
        print(f"arm {arm:>8}: divergence vs prior {out['arms'][arm]['first_divergence_vs_prior']}"
              f"  vs shipped {out['arms'][arm]['first_divergence_vs_shipped']}", flush=True)
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
