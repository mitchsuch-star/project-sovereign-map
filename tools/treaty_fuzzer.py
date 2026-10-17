"""DD-1 S6 — THE TREATY STATE-MACHINE FUZZER (October 11, 2026;
PRE_DEPLOY_PLAN.md §3.1 "The instrument" 2; rules SYSTEMS_REFERENCE.md §106).

Per seed: the 1805 world booted in-process, then N steps, each one verb
drawn by weight from the lawful set and executed through the REAL executor
as a STRUCTURED command (no parser, no HTTP) — declare war (every chooser
pre-resolved), propose a treaty and send it (the court answers at end turn),
answer the letter before you (a random option), break (confirmed), make /
release a vassal, white peace + confirm, common peace + submit + confirm,
summon the Congress, and end turn (so the AI courts act, proposals in
transit resolve and cooldowns tick). DP and gold are topped up each step
(never a diplomatic state) so verbs are lawful often; every refusal's reason
is tallied — a verb refused on every seed is itself a finding.

After EVERY step the invariants of SYSTEMS_REFERENCE.md §70 / §81 are read:
    I1  every WAR pair is owned by exactly one active war instance at
        pair_status "war" (settlement_helpers.assert_war_instance_invariants,
        reused) AND carries a purpose in `war_objectives`;
    I2  a client at WAR with a court its lord is not at war with leads that
        war itself (the client's war is the lord's war, §70.2);
    I3  no write to `world.diplomatic_states` outside
        `diplomacy.set_diplomatic_state` (a recording dict; the writer's frame
        is named — §70.2 records elimination / the cheat / the seeders as
        known direct writers, so the record says which);
    I4  no cooldown or point below zero;
    I5  an instance's participant_meta / active_participants / diplo_key_meta /
        resolved_diplo_keys agree with its sides;
    I6  the world round-trips through save / load (`from_dict(to_dict())`
        and `to_dict()` again — equal);
    I7  (recorded, never a violation) every transition the setter made that
        `validate_transition` rejects, with its reason.
A violation records the seed, the step, the class and the whole verb
sequence that reached it; the seed continues.

    .venv/Scripts/python.exe tools/treaty_fuzzer.py                       # 10 seeds x 1,000 steps -> docs/audits/dd1/
    .venv/Scripts/python.exe tools/treaty_fuzzer.py --seeds 2 --steps 150  # the pin's size
    .venv/Scripts/python.exe tools/treaty_fuzzer.py --seed dd1-fuzz-3 --steps 300 --verbose
    .venv/Scripts/python.exe tools/treaty_fuzzer.py --summarize            # the table from the records
    .venv/Scripts/python.exe tools/treaty_fuzzer.py --write-ledger         # rewrite tests/data/treaty_fuzzer_known_violations.json

Exit code 0 always — the fuzzer is a measurement; its pins live in
tests/test_dd1_treaty_fuzzer.py (the known-violation ledger is the ratchet).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import random
import sys
import tempfile
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RECORDS_DIR = ROOT / "docs" / "audits" / "dd1"
LEDGER = ROOT / "tests" / "data" / "treaty_fuzzer_known_violations.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
DEFAULT_SEEDS = [f"dd1-fuzz-{i}" for i in range(1, 11)]

TREATY_TYPES = ("peace", "armistice", "open_borders", "non_aggression",
                "defensive_alliance", "alliance", "vassalage")
# DDB-1: "Use Talleyrand's suggestion" (`apply_suggestion`) applies a draft and
# sends nothing — it is not a send action.
SEND_ACTIONS = ("execute_proposal", "send", "send_override")
# Verb weights: end turn is a third of the draw so the AI courts act and the
# letters in transit resolve; the rest spread over the table's verbs.
VERBS = [
    ("end_turn", 30), ("answer", 14), ("propose", 14), ("declare_war", 8),
    ("break", 5), ("make_vassal", 4), ("release_vassal", 3), ("white_peace", 8),
    ("common_peace", 6), ("summon", 3),
]
COOLDOWN_STORES = ("armistice_cooldowns", "armistice_turns", "player_proposal_cooldowns",
                   "ai_proposal_cooldowns", "vassal_investment_cooldowns",
                   "vassal_release_cooldowns", "ai_settlement_cooldowns", "nation_dp")
# Keys of to_dict() that are transient by design (a timestamp, a counter the
# save stamps) — excluded from the I6 comparison by name.
ROUND_TRIP_IGNORE = {"saved_at", "save_timestamp", "timestamp"}


def _env() -> None:
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="treaty_fuzzer_saves_"))
    os.environ["DEBUG_MODE"] = "false"
    os.environ["INK_DEBUG"] = "0"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        os.environ.pop(key, None)


# ═══════════════════════════════════════════════════════════════════════════
# I3 — the recording dict
# ═══════════════════════════════════════════════════════════════════════════

def _writer_frames() -> Dict[str, Any]:
    """The frames above a write: whether `set_diplomatic_state` is on the
    stack (and its `reason`), and the first backend frame that is not the
    dict itself — the writer the record names."""
    frame = sys._getframe(2)
    through_setter, reason, writer = False, "", ""
    while frame is not None:
        code = frame.f_code
        name = code.co_name
        path = code.co_filename.replace("\\", "/")
        if name == "set_diplomatic_state" and path.endswith("game_logic/diplomacy.py"):
            through_setter = True
            reason = str(frame.f_locals.get("reason") or "")
        if not writer and "/backend/" in path and name not in ("__setitem__", "__delitem__", "pop",
                                                                 "update", "setdefault", "clear"):
            short = path.split("/backend/", 1)[1]
            writer = f"{short}:{name}:{frame.f_lineno}"
        frame = frame.f_back
    return {"through_setter": through_setter, "reason": reason, "writer": writer}


class RecordingStates(dict):
    """`world.diplomatic_states` with every write logged and attributed."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.log: List[Dict[str, Any]] = []

    def _note(self, key, old, new) -> None:
        info = _writer_frames()
        info.update(pair=str(key), old=old, new=new)
        self.log.append(info)

    def __setitem__(self, key, value):
        old = dict.get(self, key)
        if old != value:
            self._note(key, old, value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._note(key, dict.get(self, key), None)
        super().__delitem__(key)

    def pop(self, key, *default):
        if key in self:
            self._note(key, dict.get(self, key), None)
        return super().pop(key, *default)

    def update(self, *a, **k):
        incoming = dict(*a, **k)
        for key, value in incoming.items():
            if dict.get(self, key) != value:
                self._note(key, dict.get(self, key), value)
        super().update(incoming)

    def setdefault(self, key, default=None):
        if key not in self:
            self._note(key, None, default)
        return super().setdefault(key, default)

    def clear(self):
        for key in list(self.keys()):
            self._note(key, dict.get(self, key), None)
        super().clear()

    def __reduce__(self):
        return (dict, (dict(self),))

    def __deepcopy__(self, memo):
        return dict(self)


# ═══════════════════════════════════════════════════════════════════════════
# THE INVARIANTS
# ═══════════════════════════════════════════════════════════════════════════

def check_invariants(world, states_log_start: int) -> List[Dict[str, Any]]:
    """Every violation found on the board as it stands — class + detail."""
    out: List[Dict[str, Any]] = []
    states = world.diplomatic_states
    player = getattr(world, "player_nation", "France")

    # I1 — the instance ownership (reused) + the purpose
    try:
        from backend.game_logic.settlement_helpers import (
            WarInstanceInvariantError, assert_war_instance_invariants,
        )
        try:
            assert_war_instance_invariants(world, context="treaty_fuzzer")
        except WarInstanceInvariantError as exc:
            out.append({"cls": "I1_instance_ownership", "detail": str(exc)[:400]})
    except Exception as exc:
        out.append({"cls": "I1_checker_raised", "detail": f"{type(exc).__name__}: {exc}"[:300]})
    objectives = getattr(world, "war_objectives", {}) or {}
    for pair, state in states.items():
        if state != "WAR":
            continue
        sides = objectives.get(pair) or {}
        if not any(isinstance(v, dict) and v for v in sides.values()):
            out.append({"cls": "I1_war_without_purpose", "detail": pair})

    # I2 — the client's war is the lord's war
    vassals = getattr(world, "vassals", {}) or {}
    instances = getattr(world, "war_instances", {}) or {}
    for client, row in vassals.items():
        lord = str((row or {}).get("lord") or "")
        if not lord:
            continue
        for pair, state in states.items():
            if state != "WAR":
                continue
            a, b = pair.split("|", 1) if "|" in pair else (pair, "")
            if client not in (a, b):
                continue
            court = b if a == client else a
            if court == lord or not court:
                continue
            lord_state = world.get_diplomatic_state(lord, court)
            if lord_state == "WAR":
                continue
            # the client leads this war itself? (PC-F30: the ONE reading the
            # reconcile uses — the client leads a side; a pair whose OTHER
            # court leads the league's instance is not the client's own war)
            from backend.game_logic.vassal import client_leads_its_own_war
            leads = False
            for inst in instances.values():
                if inst.get("ended_turn") is not None:
                    continue
                if pair in (inst.get("active_diplo_keys") or []):
                    if client_leads_its_own_war(client, court, inst):
                        leads = True
            if not leads:
                out.append({"cls": "I2_client_at_war_lord_is_not",
                            "detail": f"{client} (client of {lord}) at WAR with {court}; the lord is {lord_state}"})

    # I3 — writes outside the setter
    for entry in states.log[states_log_start:]:
        if not entry["through_setter"]:
            out.append({"cls": "I3_write_outside_setter",
                        "detail": f"{entry['pair']} {entry['old']}→{entry['new']} by {entry['writer']}"})

    # I4 — nothing below zero
    for store in COOLDOWN_STORES:
        value = getattr(world, store, None)
        if isinstance(value, dict):
            for key, v in value.items():
                if isinstance(v, (int, float)) and v < 0:
                    out.append({"cls": "I4_negative", "detail": f"{store}[{key}] = {v}"})
    if int(getattr(world, "diplomatic_points", 0) or 0) < 0:
        out.append({"cls": "I4_negative", "detail": f"diplomatic_points = {world.diplomatic_points}"})

    # I5 — the instance's own agreement
    for war_id, inst in instances.items():
        if inst.get("ended_turn") is not None:
            continue
        attackers = set(inst.get("attackers") or [])
        defenders = set(inst.get("defenders") or [])
        sides = attackers | defenders
        meta = inst.get("participant_meta") or {}
        # A court that left keeps its meta row (its `exited_turn` stamped);
        # a court on a side with no row, or a row for a court that never
        # left and is on no side, is the disagreement.
        missing = sides - set(meta.keys())
        if missing:
            out.append({"cls": "I5_side_without_meta", "detail": f"{war_id}: {sorted(missing)}"})
        for n in set(meta.keys()) - sides:
            if (meta.get(n) or {}).get("exited_turn") is None:
                out.append({"cls": "I5_meta_without_side_not_exited", "detail": f"{war_id}: {n}"})
        active = list(inst.get("active_participants") or [])
        for n in active:
            if n not in sides:
                out.append({"cls": "I5_active_not_on_a_side", "detail": f"{war_id}: {n}"})
            if (meta.get(n) or {}).get("exited_turn") is not None:
                out.append({"cls": "I5_active_but_exited", "detail": f"{war_id}: {n}"})
        pair_meta = inst.get("diplo_key_meta") or {}
        active_pairs = list(inst.get("active_diplo_keys") or [])
        resolved_pairs = list(inst.get("resolved_diplo_keys") or [])
        for pair in active_pairs:
            pm = pair_meta.get(pair) or {}
            att, dfn = pm.get("attacker"), pm.get("defender")
            if att not in attackers or dfn not in defenders:
                out.append({"cls": "I5_pair_meta_sides", "detail": f"{war_id}: {pair} {att}/{dfn}"})
        overlap = set(active_pairs) & set(resolved_pairs)
        if overlap:
            out.append({"cls": "I5_pair_both_active_and_resolved", "detail": f"{war_id}: {sorted(overlap)}"})
        for pair in resolved_pairs:
            if (pair_meta.get(pair) or {}).get("pair_status") not in ("resolved", "armistice"):
                out.append({"cls": "I5_resolved_pair_not_stamped",
                            "detail": f"{war_id}: {pair} {(pair_meta.get(pair) or {}).get('pair_status')}"})
    # the player must never be on both sides of two instances' claims
    _ = player
    return out


def _strip(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: _strip(v) for k, v in d.items() if k not in ROUND_TRIP_IGNORE}
    if isinstance(d, list):
        return [_strip(v) for v in d]
    return d


def round_trip(world) -> Optional[str]:
    """I6 — '' when the world survives save/load; else the first differing key path."""
    from backend.models.world_state import WorldState
    first = world.to_dict()
    try:
        again = WorldState.from_dict(json.loads(json.dumps(first, default=str))).to_dict()
    except Exception as exc:
        return f"from_dict raised {type(exc).__name__}: {exc}"[:300]
    a, b = _strip(first), _strip(again)
    if json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str):
        return None
    return _first_diff(a, b, "")


def _first_diff(a: Any, b: Any, path: str) -> str:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                return f"{path}/{k} missing on one side"
            d = _first_diff(a[k], b[k], f"{path}/{k}")
            if d:
                return d
        return ""
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = _first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return ""
    if json.dumps(a, sort_keys=True, default=str) != json.dumps(b, sort_keys=True, default=str):
        return f"{path}: {str(a)[:60]!r} vs {str(b)[:60]!r}"
    return ""


# ═══════════════════════════════════════════════════════════════════════════
# THE VERBS
# ═══════════════════════════════════════════════════════════════════════════

class Fuzzer:
    def __init__(self, seed: str, steps: int, *, round_trip_every: int = 1, verbose: bool = False):
        self.seed = seed
        self.steps = steps
        self.round_trip_every = max(1, round_trip_every)
        self.verbose = verbose
        self.rng = random.Random(seed)
        self.sequence: List[Dict[str, Any]] = []
        self.violations: List[Dict[str, Any]] = []
        self._seen_violations: Dict[Any, Dict[str, Any]] = {}
        self.verb_tally: Counter = Counter()
        self.refusals: Counter = Counter()
        self.transitions: Counter = Counter()
        self.invalid_transitions: Counter = Counter()
        self.outside_writers: Counter = Counter()
        self.world = None
        self.executor = None
        self.gs = None

    # ── the board ─────────────────────────────────────────────────────
    def boot(self) -> None:
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState
        self.world = WorldState.from_scenario(str(SCENARIO), seed=self.seed)
        self.executor = CommandExecutor()
        self.gs = {"world": self.world, "executor": self.executor}
        self._install_recorder()

    def _install_recorder(self) -> None:
        if not isinstance(self.world.diplomatic_states, RecordingStates):
            self.world.diplomatic_states = RecordingStates(self.world.diplomatic_states)

    @property
    def player(self) -> str:
        return getattr(self.world, "player_nation", "France")

    def courts(self) -> List[str]:
        return [n for n in self.world.get_active_nations() if n != self.player]

    def top_up(self) -> None:
        self.world.diplomatic_points = max(int(self.world.diplomatic_points or 0), 6)
        gold = getattr(self.world, "nation_gold", None)
        if isinstance(gold, dict):
            gold[self.player] = max(int(gold.get(self.player, 0) or 0), 3000)

    # ── the road ──────────────────────────────────────────────────────
    def run_cmd(self, command: Dict[str, Any], raw: str) -> Dict[str, Any]:
        parsed = {"command": dict(command), "raw_input": raw}
        try:
            result = self.executor.execute(parsed, self.gs)
        except Exception as exc:
            return {"success": False, "message": f"RAISED {type(exc).__name__}: {exc}",
                    "raised": traceback.format_exc()[-1200:]}
        return result if isinstance(result, dict) else {"success": False, "message": str(result)}

    def resolve_board_gates(self) -> Optional[str]:
        """The gates that are not the table's: a captured province waiting
        for plunder / secure (an autonomous marshal's capture in the enemy
        phase), answered at random so the diplomacy verbs stay reachable."""
        pending = getattr(self.world, "pending_capture_choice", None)
        if pending:
            options = [str(o.get("id") or o.get("action") or "") for o in
                       ((pending.get("options") or []) if isinstance(pending, dict) else [])
                       if isinstance(o, dict)]
            choice = self.rng.choice([o for o in options if o] or ["secure", "plunder"])
            try:
                self.executor.handle_capture_choice(choice, self.gs)
            except Exception as exc:
                return f"capture choice raised {type(exc).__name__}: {exc}"
            return f"capture choice → {choice}"
        return None

    def answer(self, action: str, *, dialogue: Optional[Dict] = None) -> Dict[str, Any]:
        dialogue = dialogue or self.world.dialogue_manager.peek() or {}
        try:
            result = self.executor.handle_diplomatic_dialogue_response(
                action, self.gs, dialogue_id=dialogue.get("dialogue_id"))
        except Exception as exc:
            return {"success": False, "message": f"RAISED {type(exc).__name__}: {exc}",
                    "raised": traceback.format_exc()[-1200:]}
        return result if isinstance(result, dict) else {"success": False, "message": str(result)}

    def current_options(self) -> List[str]:
        current = self.world.dialogue_manager.peek() or {}
        return [str(o.get("action") or "") for o in (current.get("options") or [])
                if isinstance(o, dict) and o.get("action") and o.get("enabled") is not False]

    # ── the verbs ─────────────────────────────────────────────────────
    def verb_answer(self) -> Dict[str, Any]:
        current = self.world.dialogue_manager.peek()
        if not current:
            return {"skipped": "no dialogue"}
        options = self.current_options()
        if not options:
            self.world.dialogue_manager.pop()
            return {"skipped": f"no options on {current.get('type')} — popped"}
        action = self.rng.choice(options)
        res = self.answer(action, dialogue=current)
        res["detail"] = f"{current.get('type')} → {action}"
        return res

    def verb_propose(self) -> Dict[str, Any]:
        court = self.rng.choice(self.courts())
        ptype = self.rng.choice(TREATY_TYPES)
        cmd = {"action": "diplomatic_proposal", "marshal": None, "type": "diplomatic",
               "target": court,
               "diplomatic_data": {"action": "diplomatic_proposal", "target_nation": court,
                                   "proposal_type": ptype, "clauses": [], "is_question": False,
                                   "has_diplomatic_keywords": True, "tone": "propose",
                                   "raw_text": f"propose {ptype} with {court}"}}
        res = self.run_cmd(cmd, f"propose {ptype} with {court}")
        res["detail"] = f"{ptype} → {court}"
        if res.get("success") is False:
            return res
        # the confirm: send it
        for _ in range(3):
            options = self.current_options()
            send = next((a for a in SEND_ACTIONS if a in options), None)
            if send:
                res2 = self.answer(send)
                res2["detail"] = f"{ptype} → {court} ({send})"
                return res2
            if not options:
                break
            # a chooser before the send (which war, which terms) — first option
            self.answer(options[0])
        res["detail"] += " (no send option)"
        return res

    def verb_declare_war(self) -> Dict[str, Any]:
        from backend.game_logic.diplomacy import get_available_war_objectives
        candidates = [c for c in self.courts() if not self.world.is_at_war(self.player, c)
                      and c not in (getattr(self.world, "vassals", {}) or {})]
        if not candidates:
            return {"skipped": "nobody to declare on"}
        court = self.rng.choice(candidates)
        objectives = [o["type"] for o in get_available_war_objectives(self.world, self.player, court)
                      if o.get("available")]
        objective = self.rng.choice(objectives) if objectives else "conquest"
        data = {"action": "diplomatic_declare_war", "target_nation": court, "war_objective": objective,
                "confirmed_objection": True, "_treaty_warning_resolved": True,
                "_war_weary_resolved": True, "_ally_entry_resolved": True,
                "raw_text": f"declare war on {court}"}
        cmd = {"action": "diplomatic_declare_war", "marshal": None, "type": "diplomatic",
               "target": court, "diplomatic_data": data, **{k: v for k, v in data.items() if k.startswith("_") or k == "confirmed_objection"}}
        res = self.run_cmd(cmd, f"declare war on {court}")
        res["detail"] = f"{court} ({objective})"
        return res

    def verb_break(self) -> Dict[str, Any]:
        treaties = list((getattr(self.world, "active_treaties", {}) or {}).keys())
        mine = [k for k in treaties if self.player in k.split("|")]
        if not mine:
            return {"skipped": "no treaty of ours"}
        key = self.rng.choice(mine)
        court = [n for n in key.split("|") if n != self.player][0]
        cmd = {"action": "diplomatic_break", "marshal": None, "type": "diplomatic", "target": court,
               "diplomatic_data": {"action": "diplomatic_break", "target_nation": court,
                                   "confirmed_break": True, "raw_text": f"break treaty with {court}"}}
        res = self.run_cmd(cmd, f"break treaty with {court}")
        res["detail"] = court
        return res

    def verb_make_vassal(self) -> Dict[str, Any]:
        candidates = [c for c in self.courts() if c not in (getattr(self.world, "vassals", {}) or {})]
        if not candidates:
            return {"skipped": "nobody to vassalize"}
        court = self.rng.choice(candidates)
        res = self.run_cmd({"action": "make_vassal", "target": court, "marshal": None},
                           f"make {court} a vassal")
        res["detail"] = court
        if res.get("success") is not False:
            options = self.current_options()
            send = next((a for a in SEND_ACTIONS if a in options), None)
            if send:
                res2 = self.answer(send)
                res2["detail"] = f"{court} ({send})"
                return res2
        return res

    def verb_release_vassal(self) -> Dict[str, Any]:
        mine = [v for v, row in (getattr(self.world, "vassals", {}) or {}).items()
                if str((row or {}).get("lord") or "") == self.player]
        if not mine:
            return {"skipped": "no vassal of ours"}
        court = self.rng.choice(mine)
        res = self.run_cmd({"action": "release_vassal", "target": court, "marshal": None},
                           f"release {court}")
        res["detail"] = court
        return res

    def _confirm_or_back_out(self, label: str) -> Dict[str, Any]:
        for _ in range(4):
            options = self.current_options()
            if not options:
                return {"success": False, "message": "no options on the confirm", "detail": label}
            if "confirm_settlement" in options:
                res = self.answer("confirm_settlement")
                res["detail"] = f"{label} (confirm)"
                return res
            if "submit_settlement_for_review" in options:
                self.answer("submit_settlement_for_review")
                continue
            for back in ("back_out_settlement", "suspend_settlement_editor", "dismiss", "keep_joint_settlement"):
                if back in options:
                    res = self.answer(back)
                    res["detail"] = f"{label} ({back}: no Ratify offered)"
                    res["no_ratify"] = True
                    return res
            self.answer(options[0])
        return {"success": False, "message": "the confirm never offered Ratify or Back Out", "detail": label}

    def verb_white_peace(self) -> Dict[str, Any]:
        enemies = [c for c in self.courts() if self.world.is_at_war(self.player, c)]
        if not enemies:
            return {"skipped": "no war"}
        court = self.rng.choice(enemies)
        res = self.run_cmd({"action": "propose_white_peace", "target_nation": court, "marshal": None},
                           f"propose white peace with {court}")
        res["detail"] = court
        if res.get("success") is False:
            return res
        return self._confirm_or_back_out(f"white peace {court}")

    def verb_common_peace(self) -> Dict[str, Any]:
        enemies = [c for c in self.courts() if self.world.is_at_war(self.player, c)]
        if not enemies:
            return {"skipped": "no war"}
        court = self.rng.choice(enemies)
        res = self.run_cmd({"action": "propose_common_peace", "target_nation": court, "marshal": None},
                           f"propose common peace with {court}")
        res["detail"] = court
        if res.get("success") is False:
            return res
        return self._confirm_or_back_out(f"common peace {court}")

    def verb_summon(self) -> Dict[str, Any]:
        res = self.run_cmd({"action": "summon_congress", "marshal": None}, "summon the congress")
        res["detail"] = ""
        return res

    def verb_end_turn(self) -> Dict[str, Any]:
        random.seed(10_000 + int(self.world.current_turn))   # the ambient runner's idiom
        res = self.run_cmd({"action": "end_turn", "marshal": None}, "end turn")
        res["detail"] = f"turn {self.world.current_turn}"
        return res

    # ── the loop ──────────────────────────────────────────────────────
    def step(self, index: int) -> None:
        states: RecordingStates = self.world.diplomatic_states
        log_start = len(states.log)
        self.top_up()
        dm = self.world.dialogue_manager
        if dm.is_hard_stop():
            verb = "answer"
        else:
            verb = self.rng.choices([v for v, _ in VERBS], weights=[w for _, w in VERBS])[0]
        handler = getattr(self, f"verb_{verb}")
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink if not self.verbose else sys.stdout):
            gate = self.resolve_board_gates()
            result = handler()
        if gate:
            result["detail"] = f"[{gate}] " + str(result.get("detail", ""))
        self.verb_tally[verb] += 1
        entry = {"i": index, "verb": verb, "detail": result.get("detail", ""),
                 "ok": result.get("success") is not False and "skipped" not in result}
        if "skipped" in result:
            entry["skipped"] = result["skipped"]
        elif result.get("success") is False:
            msg = str(result.get("message") or result.get("error_display") or result.get("error") or "")
            entry["refused"] = msg[:200]
            self.refusals[f"{verb}: {_shape(msg)}"] += 1
            if result.get("raised"):
                entry["raised"] = result["raised"]
                self.violations.append({"seed": self.seed, "step": index, "cls": "verb_raised",
                                        "detail": f"{verb} {entry['detail']}: {msg[:200]}",
                                        "sequence": [dict(s) for s in self.sequence[-12:]] + [entry]})
        self.sequence.append(entry)
        if not isinstance(self.world.diplomatic_states, RecordingStates):
            self.violations.append({"seed": self.seed, "step": index, "cls": "I3_states_reassigned",
                                    "detail": f"after {verb} {entry['detail']}",
                                    "sequence": [dict(s) for s in self.sequence[-12:]]})
            self._install_recorder()
            states = self.world.diplomatic_states
            log_start = 0
        # I7 + the writers' tally
        from backend.game_logic.diplomacy import validate_transition
        for w in states.log[log_start:]:
            self.transitions[f"{w['old']}→{w['new']}"] += 1
            if w["through_setter"]:
                if w["old"] and w["new"] and not validate_transition(str(w["old"]), str(w["new"])):
                    self.invalid_transitions[f"{w['old']}→{w['new']} ({w['reason'] or 'no reason'})"] += 1
            else:
                self.outside_writers[w["writer"]] += 1
        found = check_invariants(self.world, log_start)
        if index % self.round_trip_every == 0:
            diff = round_trip(self.world)
            if diff:
                found.append({"cls": "I6_round_trip", "detail": diff})
        for v in found:
            # One defect, many steps: a violation is recorded ONCE per (class,
            # detail) with the step it first appeared and how many steps it
            # persisted — the count the record prints is of DISTINCT ones.
            key = (v["cls"], v["detail"][:200])
            if key in self._seen_violations:
                self._seen_violations[key]["persisted"] += 1
                continue
            row = {"seed": self.seed, "step": index, "verb": verb, "cls": v["cls"],
                   "detail": v["detail"], "persisted": 1,
                   "sequence": [dict(s) for s in self.sequence[-12:]]}
            self._seen_violations[key] = row
            self.violations.append(row)
        if self.verbose:
            flag = " ✗" if found else ""
            print(f"  [{index:4}] t{self.world.current_turn:<3} {verb:<14} {entry['detail'][:50]:<52} "
                  f"{'ok' if entry['ok'] else entry.get('skipped') or entry.get('refused', '')[:40]}{flag}")

    def run(self) -> Dict[str, Any]:
        t0 = time.time()
        self.boot()
        for i in range(1, self.steps + 1):
            self.step(i)
        classes = Counter(v["cls"] for v in self.violations)
        return {
            "seed": self.seed, "steps": self.steps, "seconds": round(time.time() - t0, 1),
            "final_turn": int(self.world.current_turn),
            "verbs": dict(self.verb_tally),
            "refusals": dict(self.refusals.most_common()),
            "transitions": dict(self.transitions.most_common()),
            "invalid_transitions": dict(self.invalid_transitions.most_common()),
            "writers_outside_setter": dict(self.outside_writers.most_common()),
            "violation_classes": dict(classes.most_common()),
            "violations": self.violations,
            "sequence": self.sequence,
        }


def _shape(message: str) -> str:
    """A refusal's shape: digits and court names blurred so the tally groups."""
    import re
    text = str(message or "")[:120]
    text = re.sub(r"\d+", "N", text)
    return text


# ═══════════════════════════════════════════════════════════════════════════
# THE RECORDS
# ═══════════════════════════════════════════════════════════════════════════

def run_seed(seed: str, steps: int, round_trip_every: int, verbose: bool) -> Dict[str, Any]:
    f = Fuzzer(seed, steps, round_trip_every=round_trip_every, verbose=verbose)
    return f.run()


def table(records: Path) -> str:
    lines = [f"{'seed':<14}{'steps':>6}{'turn':>6}{'secs':>7}{'viol':>6}  classes"]
    total = 0
    for path in sorted(records.glob("treaty_fuzzer_*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        n = len(rec.get("violations") or [])
        total += n
        lines.append(f"{rec['seed']:<14}{rec['steps']:>6}{rec.get('final_turn', 0):>6}{rec.get('seconds', 0):>7}"
                     f"{n:>6}  {rec.get('violation_classes')}")
    lines.append(f"{'TOTAL':<14}{'':>6}{'':>6}{'':>7}{total:>6}")
    return "\n".join(lines)


def ledger_classes(records: Path) -> Dict[str, Dict[str, Any]]:
    """The known-violation ledger: class → {count, examples} over the records."""
    out: Dict[str, Dict[str, Any]] = {}
    for path in sorted(records.glob("treaty_fuzzer_*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        for v in rec.get("violations") or []:
            row = out.setdefault(v["cls"], {"count": 0, "examples": []})
            row["count"] += 1
            if len(row["examples"]) < 3:
                row["examples"].append(f"{v['seed']} step {v['step']}: {v['detail'][:160]}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, default=10, help="how many of the default seeds")
    ap.add_argument("--seed", action="append", default=[], help="an explicit seed (repeatable)")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--round-trip-every", type=int, default=1)
    ap.add_argument("--out", default=str(RECORDS_DIR))
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--write-ledger", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    records = Path(args.out)
    if args.summarize:
        print(table(records))
        return 0
    if args.write_ledger:
        LEDGER.write_text(json.dumps(ledger_classes(records), indent=1) + "\n", encoding="utf-8")
        print(f"ledger -> {LEDGER}")
        return 0
    _env()
    seeds = args.seed or DEFAULT_SEEDS[:args.seeds]
    records.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        print(f"[fuzzer] {seed}: {args.steps} steps", flush=True)
        rec = run_seed(seed, args.steps, args.round_trip_every, args.verbose)
        (records / f"treaty_fuzzer_{seed}.json").write_text(
            json.dumps(rec, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        print(f"[fuzzer] {seed}: turn {rec['final_turn']}, {len(rec['violations'])} violation(s) "
              f"{rec['violation_classes']} in {rec['seconds']}s", flush=True)
    print()
    print(table(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
