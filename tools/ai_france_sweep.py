"""AI-run France sweep (REV 2026-11-06) -- what happens when the courts' own AI plays France.

REPORT-ONLY experiment harness. Follows tools/ai_v_sweep.py's idiom exactly
(RunCapture / derive_metrics / child_env / spawn_run are imported from it, so
the ambient schedule, the per-turn `random.seed(K + turn)` re-seed placed LAST
before `TurnManager.end_turn`, and PYTHONHASHSEED=0 per subprocess are the
sweep's own).  The ONLY addition is France's phase BEFORE that re-seed:

  1. `EnemyAI.process_nation_turn('France', ...)`  - the military phase
  2. `EnemyAI.execute_admin_phase('France', ...)`  - recruits / laws / commissions
  3. incoming diplomacy answered by the courts' own acceptance formula
     (`diplomacy.calculate_acceptance`) built from the dialogue's own terms.

The AI's executor is wrapped (`AnsweringExecutor`): because `_acting_nation`
equals `world.player_nation` the executor treats France's commands as the
PLAYER's, so objections, captures, clarifications and hard-stop dialogues are
raised against France; the wrapper auto-answers each and logs it.

Honest scope (also in notes): France's OWN overtures do not exist --
`ai_diplomacy.process_diplomatic_phase` returns None for the player, so an AI
France never declares war, never sues for peace, never courts an ally.

Usage (one run, spawned with PYTHONHASHSEED=0):
  python tools/ai_france_sweep.py --run --seed historical --turns 40 --json-out F
  python tools/ai_france_sweep.py --all --out DIR
"""

import argparse
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ai_v_sweep as base  # noqa: E402

SEEDS = list(base.SWEEP_SEEDS)
ACCEPT_TOKENS = ("accept", "grant", "return", "honor", "proceed", "confirm")
DECLINE_TOKENS = ("reject", "decline", "refuse", "defy", "keep", "cancel",
                  "dismiss", "no", "close")


def _opt_id(option):
    if isinstance(option, dict):
        return str(option.get("action") or option.get("id")
                   or option.get("label") or "")
    return str(option)


def _enabled(option):
    return not (isinstance(option, dict) and option.get("enabled") is False)


def _pick(options, tokens):
    for option in options:
        if not _enabled(option):
            continue
        parts = set(_opt_id(option).lower().replace("-", "_").split("_"))
        if parts & set(tokens):
            return _opt_id(option)
    return None


class AnsweringExecutor:
    """Thin wrapper handed to EnemyAI. Delegates, then answers what is now
    pending against the 'player' (France). Every answer is logged."""

    def __init__(self, real, brain):
        self._real = real
        self._brain = brain

    def __getattr__(self, name):
        return getattr(self._real, name)

    def execute(self, command, game_state):
        result = self._real.execute(command, game_state)
        try:
            self._brain.after_command(command, result, game_state)
        except Exception:
            self._brain.harness_errors.append(
                traceback.format_exc()[-600:])
        return result


class FranceBrain:
    NATION = "France"

    def __init__(self, world, executor, game_state, steward=False):
        from backend.ai.enemy_ai import EnemyAI
        self.steward = bool(steward)
        self.world = world
        self.real = executor
        self.game_state = game_state
        self.log = []          # answers: [turn, kind, detail]
        self.harness_errors = []
        self.phase_errors = []
        self.refused = []      # commands the executor refused: [turn, action, msg]
        self.acts = {}         # action counts issued by France's AI
        self.cmds = []         # [turn, marshal, action, target, ok, msg]
        self.ai = EnemyAI(AnsweringExecutor(executor, self))
        self.battles = []      # held dicts (REV-X1 identity)
        self._battle_seen = {}
        self.diplo = {"accepted": 0, "declined": 0, "formula": 0,
                      "fallback": 0, "unanswered": 0}

    # -- bookkeeping ---------------------------------------------------
    def note(self, kind, detail):
        self.log.append([int(self.world.current_turn), kind, str(detail)[:200]])

    def sample_battles(self):
        for b in list(self.world.battles_this_turn):
            if id(b) in self._battle_seen:
                continue
            self._battle_seen[id(b)] = b
            row = dict(b)
            for side in ("attacker", "defender"):
                m = self.world.marshals.get(b.get(side))
                row[side + "_nation"] = getattr(m, "nation", "?")
            self.battles.append(row)

    # -- after every France command -----------------------------------
    def after_command(self, command, result, game_state):
        world = self.world
        action = (command or {}).get("command", command or {})
        if isinstance(action, dict):
            act = str(action.get("action", ""))
            self.acts[act] = self.acts.get(act, 0) + 1
            self.cmds.append([int(world.current_turn), action.get("marshal"),
                              act, action.get("target"),
                              bool((result or {}).get("success", False)),
                              str((result or {}).get("message", ""))[:110]])
        if isinstance(result, dict) and not result.get("success", True):
            self.refused.append([int(world.current_turn),
                                 str((action or {}).get("action", "?")
                                     if isinstance(action, dict) else "?"),
                                 str(result.get("message", ""))[:160]])
        self.answer_pending(game_state, result)

    def answer_pending(self, game_state, result=None):
        world = self.world
        for _ in range(8):
            progressed = False
            if getattr(world, "pending_objection", None) is not None:
                r = self.real.handle_objection_response("trust", game_state)
                self.note("objection->trust", (r or {}).get("message", ""))
                progressed = True
                if getattr(world, "pending_objection", None) is not None:
                    world.pending_objection = None
                    self.note("objection-force-cleared", "")
            if getattr(world, "pending_strategic_objection", None) is not None:
                r = self.real.handle_objection_response("trust", game_state)
                self.note("strategic_objection->trust",
                          (r or {}).get("message", ""))
                progressed = True
                if getattr(world, "pending_strategic_objection", None) is not None:
                    world.pending_strategic_objection = None
                    self.note("strategic-objection-force-cleared", "")
            pend = getattr(world, "pending_capture_choice", None)
            if pend is not None:
                word = "respect" if pend.get("stage") == "estate" else "secure"
                r = self.real.handle_capture_choice(word, game_state)
                self.note(f"capture->{word}", pend.get("region", ""))
                progressed = True
                if getattr(world, "pending_capture_choice", None) is pend:
                    world.pending_capture_choice = None
                    self.note("capture-force-cleared", pend.get("region", ""))
            if isinstance(result, dict) and result.get("pending_glorious_charge"):
                r = self.real.respond_to_glorious_charge("restrain", world)
                self.note("glorious_charge->restrain", result.get("marshal", ""))
                progressed = True
                result = None
            for m in world.get_marshals_by_nation(self.NATION):
                intr = getattr(m, "pending_interrupt", None)
                if isinstance(intr, dict) and intr.get("interrupt_type") == "last_stand":
                    from backend.commands.strategic import StrategicOrderProcessor
                    opts = intr.get("options") or []
                    pick = "fight_to_the_last" if "fight_to_the_last" in opts else (opts[0] if opts else "continue")
                    r = StrategicOrderProcessor(self.real).handle_response(
                        m.name, "last_stand", pick, world, game_state)
                    self.note("last_stand->" + pick, m.name)
                    progressed = True
                    if getattr(m, "pending_interrupt", None) is intr:
                        m.pending_interrupt = None
                        self.note("last-stand-force-cleared", m.name)
            if (isinstance(result, dict)
                    and result.get("state") == "awaiting_clarification"):
                self.note("clarification-left", result.get("message", ""))
                result = None
            hs = world.dialogue_manager.is_hard_stop()
            if hs:
                self.answer_hard_stop(game_state)
                progressed = True
            if not progressed:
                break

    # -- hard stops -----------------------------------------------------
    def answer_hard_stop(self, game_state):
        world = self.world
        dlg = world.pending_diplomatic_dialogue
        if not dlg:
            return
        dtype = str(dlg.get("type", ""))
        options = dlg.get("options") or []
        choice = None
        if dtype == "war_purpose_selection":
            choice = next((_opt_id(o) for o in options if _enabled(o)), None)
        elif dtype == "force_declare_war_confirmation":
            from backend.game_logic.war_council import can_declare_war
            target = dlg.get("target_nation") or ""
            ok = can_declare_war(world, self.NATION, target).get("ok")
            choice = (_pick(options, ("proceed", "confirm", "declare"))
                      if ok else _pick(options, ("cancel", "back", "stand")))
        elif "paradox" in dtype:
            choice = _pick(options, ("honor", "honour"))
        else:
            choice = _pick(options, ("cancel", "keep", "reject")) \
                or next((_opt_id(o) for o in options if _enabled(o)), None)
        if choice is None:
            self.note("hard-stop-UNANSWERED", dtype)
            self.diplo["unanswered"] += 1
            world.dialogue_manager._current = None
            return
        r = self.real.handle_diplomatic_dialogue_response(
            choice, game_state, dialogue_id=dlg.get("dialogue_id"))
        self.note(f"hardstop {dtype}->{choice}",
                  (r or {}).get("message", ""))
        if world.pending_diplomatic_dialogue is dlg:
            world.dialogue_manager._current = None
            self.note("hardstop-force-cleared", dtype)

    # -- incoming diplomacy (France as the courts' recipient) ----------
    def _decide(self, dlg):
        """True = accept. The courts' own formula on the dialogue's terms;
        documented fallback when the terms cannot be scored."""
        from backend.game_logic import diplomacy as dip
        world = self.world
        context = dlg.get("context") or {}
        terms = dict(context.get("proposal") or {})
        dtype = str(dlg.get("type", ""))
        if dtype == "incoming_ultimatum":
            return False, "ultimatum->defy"
        source = (context.get("source_nation") or terms.get("proposer_nation")
                  or "")
        if terms.get("type") and source:
            terms["proposer_nation"] = source
            terms["target_nation"] = self.NATION
            terms.setdefault("sweeteners", [])
            terms.setdefault("demands", [])
            terms.setdefault("clauses", [])
            try:
                res = dip.calculate_acceptance(terms, world)
                self.diplo["formula"] += 1
                return res["outcome"] == "ACCEPT", f"formula:{res['outcome']}:{res['score']}:{terms.get('type')}"
            except Exception as exc:
                why = f"formula-error:{exc}"[:60]
        else:
            why = "no-terms"
        # documented fallback
        self.diplo["fallback"] += 1
        ptype = str(terms.get("type") or context.get("proposal_type") or "")
        if "peace" in ptype or "armistice" in ptype:
            wars = [n for n in world.get_active_nations()
                    if n != self.NATION
                    and world.get_diplomatic_state(self.NATION, n) == "WAR"]
            return len(wars) >= 3, f"fallback({why}):{ptype}:wars={len(wars)}"
        return False, f"fallback({why}):{ptype}"

    def answer_diplomacy(self, game_state):
        world = self.world
        mgr = world.dialogue_manager
        from backend.game_logic.moments import is_moment_letter
        done = set()
        for _ in range(40):
            if mgr.is_hard_stop():
                self.answer_hard_stop(game_state)
                continue
            cand = [d for d in ([mgr.peek()] if mgr.peek() else [])
                    + list(mgr.iter_queue())
                    if id(d) not in done and not is_moment_letter(d)]
            if not cand:
                break
            dlg = cand[0]
            done.add(id(dlg))
            if mgr.peek() is not dlg:
                mid = dlg.get("mailbox_id")
                if mid is None or mgr.activate_mailbox_item(mid) is not dlg:
                    self.note("mail-unactivatable", dlg.get("type"))
                    self.diplo["unanswered"] += 1
                    continue
            options = dlg.get("options") or []
            dtype = str(dlg.get("type", ""))
            ptype = str((dlg.get("context") or {}).get("proposal_type", ""))
            special = None
            if dtype == "vassal_rebellion_imminent":
                special = ("invest_vassal_rebellion" if self.steward
                           else "accept_vassal_rebellion")
                accept, why = True, "rebellion:" + special
            elif dtype == "ally_settlement_petition":
                special = next((_opt_id(o) for o in options if _enabled(o)), None)
                accept, why = True, "ally-petition:first"
            elif ptype == "client_petition":
                accept, why = (self.steward, "client_petition:steward"
                               if self.steward else "client_petition:decline")
            else:
                accept, why = self._decide(dlg)
            choice = special or (_pick(options, ACCEPT_TOKENS) if accept
                                 else _pick(options, DECLINE_TOKENS))
            if choice is None:
                choice = next((_opt_id(o) for o in options if _enabled(o)),
                              "accept" if accept else "reject")
            r = self.real.handle_diplomatic_dialogue_response(
                choice, game_state, dialogue_id=dlg.get("dialogue_id"))
            ok = bool((r or {}).get("success", False))
            key = "accepted" if accept else "declined"
            self.diplo[key if ok else "unanswered"] += 1
            self.note(f"diplo {dlg.get('type')} {why} -> {choice} ok={ok}",
                      (r or {}).get("message", ""))
            if world.pending_diplomatic_dialogue is dlg:
                # the executor did not consume it (refused): leave it to lapse
                mgr._current = None
                try:
                    mgr._queue.append(dlg)
                except Exception:
                    pass

    # -- the phase -------------------------------------------------------
    def step(self, turn):
        world, gs = self.world, self.game_state
        self.answer_pending(gs)
        self.answer_diplomacy(gs)
        for label, fn in (
                ("military", lambda: self.ai.process_nation_turn(
                    self.NATION, world, gs)),
                ("admin", lambda: self.ai.execute_admin_phase(
                    self.NATION, world, gs))):
            try:
                fn()
            except Exception:
                self.phase_errors.append(
                    [turn, label, traceback.format_exc()[-700:]])
            self.answer_pending(gs)
        self.answer_diplomacy(gs)
        self.sample_battles()


def france_snapshot(world):
    from backend.game_logic import reforms
    nat = "France"
    marshals = world.get_marshals_by_nation(nat)
    men = sum(int(m.strength) for m in marshals)
    regions = world.get_nation_regions(nat)
    sats = sorted(v for v, s in (world.vassals or {}).items()
                  if s.get("lord") == nat)
    captured = sorted(m.name for m in world.marshals.values()
                      if getattr(m, "captured_by", "") and
                      getattr(m, "nation", "") == nat)
    coal = world.active_coalition
    brew = world.coalition_brewing
    wars = sorted(n for n in world.get_active_nations()
                  if n != nat and world.get_diplomatic_state(nat, n) == "WAR")
    return {
        "turn": int(world.current_turn),
        "provinces": len(regions),
        "men": men,
        "marshals": len(marshals),
        "gold": int(world.nation_gold.get(nat, 0)),
        "laws": len(reforms.laws_in_force(world, nat)),
        "satellites": sats,
        "captured": captured,
        "at_war_with": wars,
        "coalition": (None if not coal else
                      {k: coal.get(k) for k in ("name", "leader", "members")
                       if k in coal}),
        "brewing": bool(brew),
        "active_nations": len(world.get_active_nations()),
        "authority": int(getattr(getattr(world, "authority_tracker", None),
                                 "authority", 0) or 0),
    }


def run_one(seed, ambient_base, turns, steward=False):
    if os.environ.get("PYTHONHASHSEED") != "0":
        base._die("PYTHONHASHSEED must be 0")
    os.environ["SOVEREIGN_SEED"] = seed
    os.environ["LLM_MODE"] = "mock"
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    os.environ.pop("SOVEREIGN_MAP", None)
    # T3-5: the measure's seam channel (AU-2c's hook, `tools/_seams_env.py`)
    # reaches this child too — a chain holds a seam down through
    # `INK_IRON_SEAMS` exactly as the ambient sweep's children do.
    from tools._seams_env import apply_from_env
    apply_from_env()
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic import game_end
    from backend.game_logic.turn_manager import TurnManager
    from backend.models.world_state import WorldState

    world = WorldState.from_scenario(str(base.SCENARIO_PATH))
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    capture = base.RunCapture(world)
    brain = FranceBrain(world, executor, game_state, steward=steward)

    digest = {
        "meta": {"seed": seed, "ambient_base": int(ambient_base),
                 "turns": int(turns), "script": "ai_france", "steward": bool(steward),
                 "player": capture.player,
                 "france_needles": list(capture.france_needles)},
        "boot": capture.capture_boot(),
        "turns": [],
    }
    series = [france_snapshot(world)]
    ending = None
    for turn in range(turns):
        brain.step(turn)
        random.seed(ambient_base + turn)
        result = tm.end_turn(game_state)
        brain.sample_battles()
        brain.answer_pending(game_state)
        digest["turns"].append(capture.capture_turn(result))
        series.append(france_snapshot(world))
        term = game_end.terminal_ending(world)
        if term is not None:
            ending = {"turn": int(world.current_turn),
                      "cause": term.get("cause"), "kind": term.get("kind")}
            break
    digest["final"] = capture.capture_final()
    digest["derived"] = base.derive_metrics(digest)
    digest["france_series"] = series
    digest["ending"] = ending
    digest["all_endings"] = [
        {"kind": e.get("kind"), "cause": e.get("cause"),
         "turn": e.get("turn"), "terminal": e.get("terminal")}
        for e in game_end.endings(world)]
    fb = [b for b in brain.battles if "France" in (
        b.get("attacker_nation"), b.get("defender_nation"))]
    digest["france_battles"] = len(fb)
    digest["all_battles"] = len(brain.battles)
    digest["france_battle_rows"] = [
        [b.get("turn"), b.get("location"), b.get("attacker"),
         b.get("attacker_nation"), b.get("defender"),
         b.get("defender_nation"), b.get("result")]
        for b in brain.battles][:200]
    digest["ai_france"] = {
        "acts": brain.acts,
        "cmds": brain.cmds,
        "diplo": brain.diplo,
        "answers": brain.log[:400],
        "answer_counts": _count_kinds(brain.log),
        "refused": brain.refused[:200],
        "refused_count": len(brain.refused),
        "phase_errors": brain.phase_errors[:10],
        "harness_errors": brain.harness_errors[:10],
        "marshal_fates": _marshal_fates(world),
    }
    return digest


def _count_kinds(log):
    out = {}
    for _, kind, _ in log:
        k = kind.split(" ")[0]
        out[k] = out.get(k, 0) + 1
    return out


def _marshal_fates(world):
    out = {}
    for m in world.marshals.values():
        if getattr(m, "nation", "") == "France":
            out[m.name] = {"strength": int(m.strength),
                           "captured_by": getattr(m, "captured_by", ""),
                           "loc": getattr(m, "location", "")}
    return out


def spawn(seed, ambient_base, turns, json_out, timeout=900, steward=False):
    env = base.child_env(seed)
    args = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
            "--run", "--seed", seed, "--ambient-base", str(ambient_base),
            "--turns", str(turns), "--json-out", str(json_out)]
    if steward:
        args.append("--steward")
    # T3-5: the child prints UTF-8 (`-X utf8`); a cp1252 reader thread died
    # on it silently, losing exactly the stderr a failure line prints.
    proc = subprocess.run(args, env=env, cwd=str(REPO_ROOT),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    if proc.returncode != 0:
        print(f"FAILED {seed}: {proc.stderr[-1500:]}")
    return proc.returncode


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--seed", default="historical")
    p.add_argument("--ambient-base", type=int, default=base.AMBIENT_K)
    p.add_argument("--turns", type=int, default=40)
    p.add_argument("--json-out", default="")
    p.add_argument("--out", default="")
    p.add_argument("--seeds", default="")
    p.add_argument("--steward", action="store_true",
                   help="grant client petitions, invest against rebellion")
    a = p.parse_args()
    if a.run:
        d = run_one(a.seed, a.ambient_base, a.turns, steward=a.steward)
        Path(a.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json_out).write_text(json.dumps(d, indent=1, default=str),
                                    encoding="utf-8")
        print("WROTE", a.json_out)
        return
    if a.all:
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        seeds = a.seeds.split(",") if a.seeds else SEEDS
        for s in seeds:
            rc = spawn(s, a.ambient_base, a.turns, out / f"{s}.json", steward=a.steward)
            print(s, "rc", rc, flush=True)
        return
    p.print_help()


if __name__ == "__main__":
    main()
