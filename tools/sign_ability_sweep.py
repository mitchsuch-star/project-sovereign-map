"""DD-1 S6 — THE SIGN-ABILITY SWEEP (October 11, 2026; PRE_DEPLOY_PLAN.md
§3.1 "The instrument" 1; rules SYSTEMS_REFERENCE.md §106).

On every arm the driver runs (`tools/score_run.py`'s own diplomacy arms) and
on three fresh seeds, every surface that shows an answerable letter, an
enabled chip, a priced Congress row or a counsel line is dry-run through the
REAL ratifier AT THE MOMENT IT IS SHOWN — never a second implementation of
its rules: the dry run is the accept road itself on a clone of the world
(`WorldState.from_dict(world.to_dict())`, the save road, ~7 ms on the 1805
board), so whatever the ratifier would say to the player's click, it says to
the sweep first. Two counts fall out:

    A  "shown as signable, refused when signed"  — the surface promised and
       the ratifier (dry, or real when the driver clicked) refused;
    B  "refused without naming the clause"       — a refusal (dry or real)
       whose message matches none of the ratifier's own clause shapes.

The six surfaces and their moments:
    letter      DialogueManager.push / preempt / open_flow / replace (arrived),
                _promote / activate_mailbox_item (shown) — every accept-shaped
                option of an incoming letter dry-run through
                `handle_diplomatic_dialogue_response` on the clone, chased
                through a settlement_confirm or a conflict alert it opens;
    chip        get_available_diplomatic_actions — every `propose_*` row with
                `available: True`, dry-run as `_ratify_treaty` on the clone
                (the player's send road defers the court's answer to end
                turn; the chip's promise is that the ratifier would sign);
    counsel     diplomatic_advisory._recommend_action — every hint naming a
                treaty type;
    congress    congress.build_congress_payload — every row with a `peace`
                lever;
    settlement  settlement_staging.build_settlement_preview (white peace) for
                every live war the player is in — the preview's `carries`
                against `propose_white_peace` + `confirm_settlement` on the
                clone;
    real        WorldState._ratify_treaty and ratify_settlement_confirm on the
                LIVE world — every real sign, with its verdict.
The chip / counsel / congress / settlement surfaces are polled at the top of
`TurnManager.end_turn` (the board the player saw all turn); a letter is read
at its own arrival and again when it becomes current.

    .venv/Scripts/python.exe tools/sign_ability_sweep.py                       # every arm + the three seeds, in parallel
    .venv/Scripts/python.exe tools/sign_ability_sweep.py --arms FC,OP           # some arms
    .venv/Scripts/python.exe tools/sign_ability_sweep.py --summarize            # the table from the committed records
    .venv/Scripts/python.exe tools/sign_ability_sweep.py --child spec.json      # (internal) one arm with the spies installed

Records: docs/audits/dd1/sign_ability_<ARM>.json (one per arm; every row
carries turn, surface, moment, court, type, the promise and the verdict).
Exit code 0 always — the sweep is a measurement; its pins live in
tests/test_dd1_sign_ability_sweep.py.
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

RECORDS_DIR = ROOT / "docs" / "audits" / "dd1"
SCRIPTS = "tools/playtest_scripts"
T24_SAVE = "docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json"
GE3_FIXTURE = "tests/fixtures/playtest_saves/fixture_ge3_pressburg.json"

# The arms: score_run's own diplomacy-feeding arms (their argv verbatim) and
# three fresh seeds of the COMMANDED script (the one that plays all forty
# loops and answers the table).
ARMS: Dict[str, List[str]] = {
    "FC": ["--script", f"{SCRIPTS}/sr_exit_first_contact.json", "--turns", "2",
           "--diplomacy", "decline"],
    "OP": ["--script", f"{SCRIPTS}/sr_exit_aar_typed.json", "--turns", "18",
           "--objection", "insist", "--diplomacy", "accept"],
    "VOLTE": ["--script", f"{SCRIPTS}/volte_court_austria.json", "--turns", "40",
              "--diplomacy", "accept"],
    "CONG": ["--script", f"{SCRIPTS}/score_congress_sitting.json", "--from-save", T24_SAVE,
             "--diplomacy", "accept", "--turns", "9"],
    "PRESS": ["--script", f"{SCRIPTS}/ge3_pressburg.json", "--from-save", GE3_FIXTURE,
              "--diplomacy", "accept", "--stop-on-ending", "--turns", "12"],
    "REACH-AAR": ["--script", f"{SCRIPTS}/sr1e_aar_road.json", "--turns", "40",
                  "--objection", "insist", "--diplomacy", "accept"],
}
FRESH_SEEDS = ("dd1-one", "dd1-two", "dd1-three")
for _seed in FRESH_SEEDS:
    ARMS[f"SEED-{_seed}"] = ["--script", f"{SCRIPTS}/commanded_full40.json", "--turns", "40",
                             "--diplomacy", "accept", "--seed", _seed]
QUICK_ARMS = {
    "FC": ARMS["FC"],
    "SEED-quick": ["--script", f"{SCRIPTS}/commanded_full40.json", "--turns", "4",
                   "--diplomacy", "accept", "--seed", "dd1-quick"],
}

LETTER_TYPES = frozenset({
    "incoming_proposal", "counter_offer", "counter_offer_response", "incoming_ultimatum",
    "incoming_settlement_offer", "ally_settlement_petition", "conflict_alert",
})
ACCEPT_ACTIONS = frozenset({
    "accept_ai_proposal", "accept_counter_offer", "accept_ai_ultimatum",
    "accept_settlement_offer", "grant_ally_petition_clause", "honor_bargain_in_settlement",
})
# The surfaces' chips and the treaty type each promises (diplomacy.py
# `get_available_diplomatic_actions`).
CHIP_TYPES = {
    "propose_peace": "peace", "propose_armistice": "armistice",
    "propose_open_borders": "open_borders", "propose_non_aggression": "non_aggression",
    "propose_defensive_alliance": "defensive_alliance", "propose_alliance": "alliance",
    "propose_vassal": "vassalage",
}
_COUNSEL_RX = re.compile(
    r"Propose (peace|armistice|alliance|non-aggression pact|defensive alliance|open borders)",
    re.I)
_COUNSEL_TYPES = {
    "peace": "peace", "armistice": "armistice", "alliance": "alliance",
    "non-aggression pact": "non_aggression", "defensive alliance": "defensive_alliance",
    "open borders": "open_borders",
}
# The ratifier's own clause shapes (count B reads a refusal against these).
CLAUSES = [
    ("no_downgrade", re.compile(r"would be a downgrade|would be no upgrade|already (have|at)", re.I)),
    ("relation_floor", re.compile(r"[Rr]elations with .* stand at -?\d+;.* needs -?\d+|relations .* below", re.I)),
    ("ap_clause", re.compile(r"AP demands require", re.I)),
    ("one_war_bargain", re.compile(r"only one war bargain", re.I)),
    ("war_bargain", re.compile(r"Invalid war bargain", re.I)),
    ("vassal_cap", re.compile(r"Cannot vassalize|too powerful to subjugate", re.I)),
    ("leader_only", re.compile(r"Only the war leader can settle", re.I)),
    ("fresh_peace", re.compile(r"fresh peace with", re.I)),
    ("truce_cooldown", re.compile(r"truce'?s cooldown|cooldown binds", re.I)),
    ("congress_sits", re.compile(r"the Congress of Paris sits|Congress sits", re.I)),
    ("acceptance", re.compile(r"acceptance_(blocked|rejected)|would not (carry|sign)|refuses the terms|rejects? the terms", re.I)),
    ("settlement_code", re.compile(r"\b(no_covered_enemy|no_direct_war_score|inactive_war_instance|invalid_war_id|"
                                   r"incoming_offer_war_(invalid|archived)|not_side_leader|one_to_one_war|"
                                   r"multi_war_ambiguity|stale_offer|offer_expired)\b", re.I)),
    ("paradox", re.compile(r"paradox|conflict with|already allied|would put us at war with", re.I)),
    ("insufficient_dp", re.compile(r"[Ii]nsufficient DP|diplomatic points", re.I)),
    ("in_transit", re.compile(r"in transit|IN_TRANSIT|already carries|en route to a foreign court", re.I)),
    ("eliminated", re.compile(r"eliminated|no longer exists", re.I)),
    ("one_to_one_war", re.compile(r"one-on-one war", re.I)),
    ("war_changed", re.compile(r"changed while the review was open", re.I)),
    ("not_at_war", re.compile(r"not at war with", re.I)),
    ("petition_table_closed", re.compile(r"settlement table for this war is not open", re.I)),
    ("already_given", re.compile(r"given elsewhere by our own hand|cannot be ceded", re.I)),
    ("no_dominant_pressure", re.compile(r"no single dominant pressure", re.I)),
    ("legitimacy", re.compile(r"[Ss]ettlement legitimacy|[Ll]eader'?s own losses", re.I)),
]
# A raw snake_case code in a player-facing refusal is itself the "unnamed"
# class (the clause is named to the engine, not to the player).
_RAW_CODE_RX = re.compile(r"\b[a-z]+(?:_[a-z]+){2,}\b")


def _display_shapes() -> List[str]:
    """Every settlement refusal the display layer can say — read off the
    display maps themselves, so a refusal in the player's words is 'named'."""
    try:
        from backend import display_names as DN
    except Exception:
        return []
    shapes: List[str] = []
    for attr in ("SETTLEMENT_DISABLED_REASON_DISPLAY", "ALLY_ENTRY_BLOCK_DISPLAY"):
        table_ = getattr(DN, attr, None) or {}
        shapes.extend(str(v) for v in table_.values() if isinstance(v, str) and len(v) > 12)
    return shapes


_DISPLAY_SHAPES: Optional[List[str]] = None


def clause_of(message: str) -> str:
    global _DISPLAY_SHAPES
    text = str(message or "")
    if _RAW_CODE_RX.search(text):
        return "unnamed"
    for name, rx in CLAUSES:
        if rx.search(text):
            return name
    if _DISPLAY_SHAPES is None:
        _DISPLAY_SHAPES = _display_shapes()
    for shape in _DISPLAY_SHAPES:
        if shape[:40] in text:
            return "display_map"
    return "unnamed"


# ═══════════════════════════════════════════════════════════════════════════
# THE CHILD — one arm with the spies installed
# ═══════════════════════════════════════════════════════════════════════════

class _Sweep:
    """The spy state of one arm: the rows, the dry-run depth guard, the
    executor the dry runs share and the live-world reader."""

    def __init__(self, arm: str, record_path: Path):
        self.arm = arm
        self.record_path = record_path
        self.rows: List[Dict[str, Any]] = []
        self.dry_depth = 0
        self.errors: List[str] = []
        self.clone_ms: List[float] = []
        self._executor = None
        self._seen_letters: set = set()
        self.started = time.time()

    # ── the live world ────────────────────────────────────────────────
    def live_world(self):
        try:
            import backend.main as M
            return M.game_state.get("world")
        except Exception:
            return None

    def is_live(self, world) -> bool:
        return world is not None and world is self.live_world()

    def executor(self):
        if self._executor is None:
            from backend.commands.executor import CommandExecutor
            self._executor = CommandExecutor()
        return self._executor

    # ── the clone ────────────────────────────────────────────────────
    def clone(self, world):
        from backend.models.world_state import WorldState
        t0 = time.perf_counter()
        copy_ = WorldState.from_dict(world.to_dict())
        self.clone_ms.append((time.perf_counter() - t0) * 1000.0)
        return copy_

    # ── the record ────────────────────────────────────────────────────
    def record(self, **row) -> Dict[str, Any]:
        row.setdefault("arm", self.arm)
        row["clause"] = clause_of(row.get("message", "")) if row.get("verdict") == "refused" else ""
        self.rows.append(row)
        return row

    def flush(self) -> None:
        self.record_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "arm": self.arm,
            "rows": self.rows,
            "errors": self.errors,
            "clone_ms_mean": round(sum(self.clone_ms) / len(self.clone_ms), 2) if self.clone_ms else None,
            "clones": len(self.clone_ms),
            "seconds": round(time.time() - self.started, 1),
            "counts": summarize(self.rows),
        }
        self.record_path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n",
                                    encoding="utf-8")

    # ── the dry runs ─────────────────────────────────────────────────
    def _classify(self, clone, result, before_states: Dict[str, str]) -> Dict[str, Any]:
        """Read one accept road's result on the clone."""
        out: Dict[str, Any] = {}
        if not isinstance(result, dict):
            out.update(verdict="error", message=f"non-dict result {type(result).__name__}")
            return out
        message = str(result.get("message") or result.get("error_display") or result.get("error") or "")
        moved = sorted(k for k, v in (clone.diplomatic_states or {}).items()
                       if before_states.get(k) != v)
        out["state_moved"] = moved
        if result.get("success") is False or result.get("type") == "diplomatic_treaty_failed":
            out.update(verdict="refused", message=message)
            return out
        current = clone.dialogue_manager.peek() if getattr(clone, "dialogue_manager", None) else None
        ctype = str((current or {}).get("type") or "")
        if ctype in ("settlement_confirm", "conflict_alert", "alliance_paradox",
                     "commitment_paradox", "settlement_pair_substitute_confirm"):
            out.update(verdict="asked", message=message, asked_type=ctype,
                       asked_text=str((current or {}).get("talleyrand_text")
                                      or (current or {}).get("message") or "")[:300])
            return out
        out.update(verdict="signed", message=message)
        return out

    def _chase(self, clone, first: Dict[str, Any]) -> Dict[str, Any]:
        """A letter that opened a second question on accept: answer it the
        way the player would ('accept anyway' / confirm) and read the end.
        A settlement confirm that offers no Ratify IS the refusal — its own
        `ratify_blocked_reason` / hard stops are the message."""
        asked = first.get("asked_type")
        action = {"settlement_confirm": "confirm_settlement",
                  "conflict_alert": "accept_ai_proposal",
                  "alliance_paradox": None, "commitment_paradox": None,
                  "settlement_pair_substitute_confirm": "confirm_pair_substitute"}.get(asked)
        if not action:
            return {}
        before = dict(clone.diplomatic_states or {})
        current = clone.dialogue_manager.peek() or {}
        option_ids = {str(o.get("action") or "") for o in (current.get("options") or []) if isinstance(o, dict)}
        if action not in option_ids:
            stops = [str((hs or {}).get("reason") or hs) for hs in (current.get("hard_stops") or [])]
            reason = str(current.get("ratify_blocked_reason") or "; ".join(stops)
                         or current.get("talleyrand_text") or current.get("message") or "")
            return {"verdict": "refused", "message": reason[:400], "button_shown": False,
                    "options": sorted(option_ids)}
        try:
            result = self.executor().handle_diplomatic_dialogue_response(
                action, {"world": clone, "executor": self.executor()},
                dialogue_id=current.get("dialogue_id"))
        except Exception as exc:  # the road itself raised — a finding
            return {"verdict": "error", "message": f"{type(exc).__name__}: {exc}"}
        return self._classify(clone, result, before)

    def dry_sign_letter(self, world, dialogue: Dict[str, Any], action: str) -> Dict[str, Any]:
        """The accept road on a clone with THIS letter current."""
        state = random.getstate()
        self.dry_depth += 1
        try:
            clone = self.clone(world)
            dm = clone.dialogue_manager
            did = dialogue.get("dialogue_id")
            target = None
            if dm.peek() is not None and dm.peek().get("dialogue_id") == did:
                target = dm.peek()
            else:
                for item in list(dm._queue):
                    if item.get("dialogue_id") == did:
                        target = item
                        dm._queue.remove(item)
                        if dm._current is not None:
                            dm._queue.append(dm._current)
                        dm._current = item
                        break
            if target is None:
                return {"verdict": "error", "message": "letter not found on the clone"}
            before = dict(clone.diplomatic_states or {})
            try:
                result = self.executor().handle_diplomatic_dialogue_response(
                    action, {"world": clone, "executor": self.executor()}, dialogue_id=did)
            except Exception as exc:
                return {"verdict": "error", "message": f"{type(exc).__name__}: {exc}"}
            out = self._classify(clone, result, before)
            if out.get("verdict") == "asked":
                out["after_ask"] = self._chase(clone, out)
            return out
        finally:
            self.dry_depth -= 1
            random.setstate(state)

    def dry_sign_proposal(self, world, court: str, ptype: str) -> Dict[str, Any]:
        """The ratifier on a clone for a player→court treaty of `ptype`."""
        state = random.getstate()
        self.dry_depth += 1
        try:
            clone = self.clone(world)
            player = getattr(clone, "player_nation", "France")
            if ptype == "armistice":
                from backend.game_logic.diplomacy import armistice_variant_for
                ptype = armistice_variant_for(clone, player, court)
            proposal = {"type": ptype, "proposer_nation": player, "target_nation": court,
                        "sweeteners": [], "demands": [], "clauses": []}
            before = dict(clone.diplomatic_states or {})
            try:
                event = clone._ratify_treaty(proposal)
            except Exception as exc:
                return {"verdict": "error", "message": f"{type(exc).__name__}: {exc}", "type_sent": ptype}
            moved = sorted(k for k, v in (clone.diplomatic_states or {}).items() if before.get(k) != v)
            if event is None:
                return {"verdict": "silent", "message": "", "type_sent": ptype, "state_moved": moved}
            if event.get("type") == "diplomatic_treaty_failed":
                return {"verdict": "refused", "message": str(event.get("message") or ""),
                        "type_sent": ptype, "state_moved": moved}
            return {"verdict": "signed", "message": str(event.get("message") or "")[:200],
                    "type_sent": ptype, "state_moved": moved}
        finally:
            self.dry_depth -= 1
            random.setstate(state)

    def dry_white_peace(self, world, war_id: str, target: str) -> Dict[str, Any]:
        """propose_white_peace + confirm_settlement on a clone."""
        state = random.getstate()
        self.dry_depth += 1
        try:
            clone = self.clone(world)
            gs = {"world": clone, "executor": self.executor()}
            before = dict(clone.diplomatic_states or {})
            cmd = {"command": {"action": "propose_white_peace", "target_nation": target,
                               "war_id": war_id, "marshal": None, "type": "diplomatic"},
                   "raw_input": f"propose white peace with {target}"}
            try:
                staged = self.executor().execute(cmd, gs)
            except Exception as exc:
                return {"verdict": "error", "message": f"{type(exc).__name__}: {exc}"}
            if not isinstance(staged, dict) or staged.get("success") is False:
                msg = ""
                if isinstance(staged, dict):
                    msg = str(staged.get("message") or staged.get("error_display") or staged.get("error") or "")
                return {"verdict": "refused", "message": msg, "stage": "propose"}
            current = clone.dialogue_manager.peek() or {}
            if str(current.get("type") or "") != "settlement_confirm":
                return {"verdict": "error", "message": f"no settlement_confirm after propose ({current.get('type')})",
                        "stage": "propose"}
            # The confirm's own promise: the Ratify button (`confirm_settlement`
            # among its options, `can_ratify`); without it the surface itself
            # says no, with `ratify_blocked_reason` / its hard stops.
            option_ids = {str(o.get("action") or "") for o in (current.get("options") or []) if isinstance(o, dict)}
            if "confirm_settlement" not in option_ids:
                stops = [str((hs or {}).get("reason") or hs) for hs in (current.get("hard_stops") or [])]
                return {"verdict": "not_shown", "stage": "confirm",
                        "message": str(current.get("ratify_blocked_reason") or "; ".join(stops) or ""),
                        "button_shown": False, "options": sorted(option_ids)}
            try:
                result = self.executor().handle_diplomatic_dialogue_response(
                    "confirm_settlement", gs, dialogue_id=current.get("dialogue_id"))
            except Exception as exc:
                return {"verdict": "error", "message": f"{type(exc).__name__}: {exc}", "stage": "confirm"}
            out = self._classify(clone, result, before)
            out["stage"] = "confirm"
            out["button_shown"] = True
            return out
        finally:
            self.dry_depth -= 1
            random.setstate(state)

    # ── the surfaces ─────────────────────────────────────────────────
    def read_letter(self, world, dialogue: Dict[str, Any], moment: str) -> None:
        if not isinstance(dialogue, dict) or dialogue.get("type") not in LETTER_TYPES:
            return
        key = (dialogue.get("dialogue_id"), moment)
        if key in self._seen_letters:
            return
        self._seen_letters.add(key)
        from backend.commands.dialogue_routing import dialogue_court
        court = ""
        try:
            court = dialogue_court(dialogue) or ""
        except Exception:
            pass
        ctx = dialogue.get("context") or {}
        ptype = str(ctx.get("proposal_type") or (ctx.get("proposal") or {}).get("type")
                    or dialogue.get("proposal_type") or dialogue.get("type") or "")
        for option in dialogue.get("options") or []:
            if not isinstance(option, dict):
                continue
            action = str(option.get("action") or "")
            if action not in ACCEPT_ACTIONS:
                continue
            shown = option.get("enabled") is not False
            row = {"turn": int(getattr(world, "current_turn", 0) or 0), "surface": "letter",
                   "moment": moment, "court": court, "type": ptype, "letter_type": dialogue.get("type"),
                   "dialogue_id": dialogue.get("dialogue_id"), "action": action,
                   "label": option.get("label", ""), "shown_signable": bool(shown),
                   "disabled_reason": option.get("reason", "") if not shown else ""}
            if shown:
                row.update(self.dry_sign_letter(world, dialogue, action))
            else:
                row.update(verdict="not_shown", message="")
            self.record(**row)

    def poll(self, world) -> None:
        """The read-only surfaces, as the player would open them."""
        if world is None or self.dry_depth:
            return
        turn = int(getattr(world, "current_turn", 0) or 0)
        player = getattr(world, "player_nation", "France")
        state = random.getstate()
        try:
            courts = [n for n in world.get_active_nations() if n != player]
        except Exception as exc:
            self.errors.append(f"t{turn} active nations: {exc}")
            courts = []
        # 1 — the chips
        try:
            from backend.game_logic.diplomacy import get_available_diplomatic_actions
            for court in courts:
                try:
                    rows = get_available_diplomatic_actions(world, court)
                except Exception as exc:
                    self.errors.append(f"t{turn} chips {court}: {exc}")
                    continue
                for chip in rows or []:
                    action = str(chip.get("action") or "")
                    if action not in CHIP_TYPES:
                        continue
                    shown = bool(chip.get("available"))
                    row = {"turn": turn, "surface": "chip", "moment": "shown", "court": court,
                           "type": CHIP_TYPES[action], "action": action, "shown_signable": shown,
                           "disabled_reason": str(chip.get("disabled_reason") or "") if not shown else "",
                           "likelihood": str(chip.get("likelihood") or "")}
                    if shown:
                        row.update(self.dry_sign_proposal(world, court, CHIP_TYPES[action]))
                    else:
                        row.update(verdict="not_shown", message="")
                    self.record(**row)
        except Exception as exc:
            self.errors.append(f"t{turn} chips: {exc}")
        # 2 — the counsel
        try:
            from backend.game_logic.diplomatic_advisory import _recommend_action
            for court in courts:
                try:
                    rec = _recommend_action(court, world)
                except Exception as exc:
                    self.errors.append(f"t{turn} counsel {court}: {exc}")
                    continue
                hints = list(rec.get("action_hints") or []) if isinstance(rec, dict) else []
                for hint in hints:
                    m = _COUNSEL_RX.search(str(hint))
                    if not m:
                        continue
                    ptype = _COUNSEL_TYPES[m.group(1).lower()]
                    row = {"turn": turn, "surface": "counsel", "moment": "shown", "court": court,
                           "type": ptype, "action": str(hint), "shown_signable": True}
                    row.update(self.dry_sign_proposal(world, court, ptype))
                    self.record(**row)
        except Exception as exc:
            self.errors.append(f"t{turn} counsel: {exc}")
        # 3 — the Congress table
        try:
            from backend.game_logic.congress import build_congress_payload
            payload = build_congress_payload(world)
            for entry in (payload or {}).get("courts") or []:
                court = str(entry.get("nation") or "")
                for lever in entry.get("levers") or []:
                    if str(lever.get("key") or "") != "peace":
                        continue
                    ptype = "peace" if world.is_at_war(court, player) else "peace"
                    row = {"turn": turn, "surface": "congress", "moment": "shown", "court": court,
                           "type": ptype, "action": str(lever.get("text") or ""), "shown_signable": True,
                           "stance": str(entry.get("stance") or "")}
                    row.update(self.dry_sign_proposal(world, court, ptype))
                    self.record(**row)
        except Exception as exc:
            self.errors.append(f"t{turn} congress: {exc}")
        # 4 — the settlement preview (white peace) for every live war
        try:
            from backend.game_logic.settlement_staging import build_settlement_preview
            war_ids = list(world.get_war_instances_by_participant(player) or [])
            for war_id in war_ids:
                war = (world.war_instances or {}).get(war_id) or {}
                if war.get("ended_turn") is not None:
                    continue
                side = (war.get("side_by_nation") or {}).get(player)
                other = "defenders" if side == "attackers" else "attackers"
                opposing = [n for n in (war.get(other) or []) if n in (war.get("active_participants") or [])
                            and world.is_at_war(player, n)]
                if not opposing:
                    continue
                leader_key = "defender_leader" if other == "defenders" else "attacker_leader"
                leader = str(war.get(leader_key) or "")
                target = leader if leader in opposing else opposing[0]
                try:
                    preview = build_settlement_preview(
                        world, war_id=str(war_id), proposer_side=side, settlement_terms=[],
                        actor_nation=player, ignore_active_dialogue=True)
                except Exception as exc:
                    self.errors.append(f"t{turn} settlement preview {war_id}: {exc}")
                    continue
                overall = (preview or {}).get("overall_acceptance") or {}
                carries = overall.get("carries")
                if carries is None:
                    carries = str(overall.get("band") or overall.get("verdict") or "").lower() in ("accept", "acceptable", "carries")
                preview_carries = bool(preview and preview.get("success", True) and carries)
                dry = self.dry_white_peace(world, str(war_id), target)
                button = bool(dry.get("button_shown"))
                if dry.get("verdict") == "not_shown" and preview_carries:
                    # The preview promised a package that carries; the confirm
                    # offered no Ratify — the table said yes, the treaty no.
                    dry["verdict"] = "refused"
                row = {"turn": turn, "surface": "settlement", "moment": "shown", "court": target,
                       "type": "white_peace", "war_id": str(war_id), "action": "propose_white_peace",
                       "shown_signable": preview_carries or button, "preview_carries": preview_carries,
                       "preview_verdict": str(overall.get("carry_verdict_display") or overall.get("band")
                                              or overall.get("verdict") or ""),
                       "preview_error": str((preview or {}).get("error") or "")}
                row.update(dry)
                self.record(**row)
        except Exception as exc:
            self.errors.append(f"t{turn} settlement: {exc}")
        finally:
            random.setstate(state)


_SWEEP: Optional[_Sweep] = None


def install_spies(sweep: _Sweep) -> None:
    """Patch the CLASSES and MODULES (never an instance) once the backend is
    imported; every spy returns early during a dry run and for any world that
    is not the live one."""
    from backend.models.dialogue_manager import DialogueManager
    from backend.models.world_state import WorldState
    from backend.game_logic.turn_manager import TurnManager
    from backend.game_logic import settlement_ratify as SR
    from backend.game_logic import settlement_actions as SA

    def _live_dm(dm) -> Optional[Any]:
        if sweep.dry_depth:
            return None
        world = sweep.live_world()
        if world is None or getattr(world, "dialogue_manager", None) is not dm:
            return None
        return world

    def _wrap_arrival(name):
        original = getattr(DialogueManager, name)

        def spy(self, dialogue, *a, **k):
            out = original(self, dialogue, *a, **k)
            world = _live_dm(self)
            if world is not None:
                try:
                    sweep.read_letter(world, dialogue, "arrived")
                    if self.peek() is dialogue:
                        sweep.read_letter(world, dialogue, "shown")
                except Exception as exc:
                    sweep.errors.append(f"{name}: {type(exc).__name__}: {exc}")
            return out
        spy.__name__ = name
        setattr(DialogueManager, name, spy)

    for _name in ("push", "preempt", "open_flow", "replace"):
        _wrap_arrival(_name)

    def _wrap_shown(name):
        original = getattr(DialogueManager, name)

        def spy(self, *a, **k):
            out = original(self, *a, **k)
            world = _live_dm(self)
            if world is not None and self.peek() is not None:
                try:
                    sweep.read_letter(world, self.peek(), "shown")
                except Exception as exc:
                    sweep.errors.append(f"{name}: {type(exc).__name__}: {exc}")
            return out
        spy.__name__ = name
        setattr(DialogueManager, name, spy)

    for _name in ("_promote", "activate_mailbox_item"):
        _wrap_shown(_name)

    _end_turn = TurnManager.end_turn

    def end_turn_spy(self, game_state=None):
        if not sweep.dry_depth and sweep.is_live(getattr(self, "world", None)):
            try:
                sweep.poll(self.world)
            except Exception as exc:
                sweep.errors.append(f"poll: {type(exc).__name__}: {exc}")
        return _end_turn(self, game_state)
    TurnManager.end_turn = end_turn_spy

    _ratify = WorldState._ratify_treaty

    def ratify_spy(self, proposal):
        event = _ratify(self, proposal)
        if not sweep.dry_depth and sweep.is_live(self):
            player = getattr(self, "player_nation", "France")
            proposer = str(proposal.get("proposer_nation") or proposal.get("proposer") or "")
            target = str(proposal.get("target_nation") or proposal.get("target") or "")
            is_player = player in (proposer, target)
            if event is None:
                verdict, message = "silent", ""
            elif event.get("type") == "diplomatic_treaty_failed":
                verdict, message = "refused", str(event.get("message") or "")
            else:
                verdict, message = "signed", str(event.get("message") or "")[:200]
            sweep.record(turn=int(getattr(self, "current_turn", 0) or 0), surface="real",
                         moment="signed", court=(target if proposer == player else proposer),
                         type=str(proposal.get("type") or ""), action="_ratify_treaty",
                         shown_signable=None, is_player=is_player, proposer=proposer, target=target,
                         verdict=verdict, message=message)
        return event
    WorldState._ratify_treaty = ratify_spy

    _confirm = SR.ratify_settlement_confirm

    def confirm_spy(world, dialogue):
        result = _confirm(world, dialogue)
        if not sweep.dry_depth and sweep.is_live(world):
            ok = isinstance(result, dict) and result.get("success") is not False
            message = "" if ok else str((result or {}).get("error_display") or (result or {}).get("error") or "")
            sweep.record(turn=int(getattr(world, "current_turn", 0) or 0), surface="real",
                         moment="signed", court=str((dialogue or {}).get("selected_target_nation")
                                                   or (dialogue or {}).get("target_nation") or ""),
                         type="settlement", war_id=str((dialogue or {}).get("war_id") or ""),
                         action="ratify_settlement_confirm", shown_signable=None, is_player=True,
                         verdict="signed" if ok else "refused", message=message)
        return result
    SR.ratify_settlement_confirm = confirm_spy
    SA.ratify_settlement_confirm = confirm_spy


def run_child(spec_path: str) -> int:
    global _SWEEP
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    sweep = _Sweep(spec["arm"], Path(spec["record"]))
    _SWEEP = sweep
    atexit.register(sweep.flush)
    import playtest_driver as PD
    _make = PD.make_inprocess_transport

    def make_and_spy(args, out_dir):
        tx = _make(args, out_dir)
        install_spies(sweep)
        return tx
    PD.make_inprocess_transport = make_and_spy
    sys.argv = ["playtest_driver.py", "--name", f"dd1-{spec['arm']}", "--fresh", "--out",
                spec["out_dir"], "--llm", "mock"] + list(spec["argv"])
    try:
        PD.main()
    except SystemExit as exc:
        code = int(exc.code or 0) if isinstance(exc.code, int) else 0
        sweep.flush()
        return code
    sweep.flush()
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# THE PARENT — the arms, the records, the table
# ═══════════════════════════════════════════════════════════════════════════

def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """A and B, per surface — read off the rows alone."""
    a_rows, b_rows = [], []
    for row in rows:
        verdict = row.get("verdict")
        surface = row.get("surface")
        if surface == "real":
            if verdict == "refused" and row.get("is_player"):
                b_rows.append(row) if row.get("clause") == "unnamed" else None
            continue
        if row.get("shown_signable") and verdict == "refused":
            a_rows.append(row)
        if verdict == "refused" and row.get("clause") == "unnamed":
            b_rows.append(row)
        after = row.get("after_ask") or {}
        if row.get("shown_signable") and after.get("verdict") == "refused":
            a_rows.append(dict(row, verdict="refused", message=after.get("message", ""),
                               clause=clause_of(after.get("message", "")), via="after_ask"))
            if clause_of(after.get("message", "")) == "unnamed":
                b_rows.append(a_rows[-1])
    # The real refusals that followed a signable showing of the same (court,
    # type) in the same turn are A's "refused when signed" half.
    shown = {(r.get("turn"), r.get("court"), r.get("type")) for r in rows
             if r.get("surface") != "real" and r.get("shown_signable")}
    real_refused = [r for r in rows if r.get("surface") == "real" and r.get("verdict") == "refused"
                    and r.get("is_player")]
    a_real = [r for r in real_refused if (r.get("turn"), r.get("court"), r.get("type")) in shown]
    by_surface = Counter(r.get("surface") for r in a_rows)
    return {
        "A_shown_signable_refused": len(a_rows) + len(a_real),
        "A_dry": len(a_rows), "A_real": len(a_real),
        "A_by_surface": dict(by_surface),
        "B_refused_unnamed": len(b_rows),
        "B_messages": sorted({str(r.get("message") or "")[:160] for r in b_rows}),
        "shown": sum(1 for r in rows if r.get("surface") != "real" and r.get("shown_signable")),
        "letters": sum(1 for r in rows if r.get("surface") == "letter"),
        "real_signs": sum(1 for r in rows if r.get("surface") == "real"),
        "real_refused_player": len(real_refused),
        "asked": sum(1 for r in rows if r.get("verdict") == "asked"),
        "errors": sum(1 for r in rows if r.get("verdict") == "error"),
        "verdicts": dict(Counter(f"{r.get('surface')}:{r.get('verdict')}" for r in rows)),
    }


def _python() -> str:
    for rel in (("Scripts", "python.exe"), ("bin", "python")):
        cand = ROOT.joinpath(".venv", *rel)
        if cand.exists():
            return str(cand)
    return sys.executable


def run_arm(arm: str, argv: List[str], out_root: Path, records: Path) -> Dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    spec = {"arm": arm, "argv": argv, "out_dir": str(out_root / "runs"),
            "record": str(records / f"sign_ability_{arm}.json")}
    spec_path = out_root / f"spec_{arm}.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["LLM_MODE"] = "mock"
    env["INK_IRON_SAVE_DIR"] = str(out_root / "_saves" / arm)
    env["PYTHONIOENCODING"] = "utf-8"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        env.pop(key, None)
    log = out_root / f"{arm}.log"
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run([_python(), str(Path(__file__).resolve()), "--child", str(spec_path)],
                              cwd=str(ROOT), env=env, stdout=fh, stderr=subprocess.STDOUT, text=True)
    record = Path(spec["record"])
    counts = {}
    if record.exists():
        counts = json.loads(record.read_text(encoding="utf-8")).get("counts") or {}
    return {"arm": arm, "exit": proc.returncode, "seconds": round(time.time() - t0, 1),
            "counts": counts, "log": str(log)}


def table(records: Path, arms: Optional[List[str]] = None) -> str:
    lines = [f"{'arm':<16}{'shown':>6}{'letters':>8}{'real':>6}{'A':>5}{'A-dry':>7}{'A-real':>8}{'B':>5}{'asked':>7}{'err':>5}  A by surface"]
    total_a = total_b = 0
    for path in sorted(records.glob("sign_ability_*.json")):
        arm = path.stem.replace("sign_ability_", "")
        if arms and arm not in arms:
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        c = rec.get("counts") or summarize(rec.get("rows") or [])
        total_a += int(c.get("A_shown_signable_refused", 0))
        total_b += int(c.get("B_refused_unnamed", 0))
        lines.append(f"{arm:<16}{c.get('shown', 0):>6}{c.get('letters', 0):>8}{c.get('real_signs', 0):>6}"
                     f"{c.get('A_shown_signable_refused', 0):>5}{c.get('A_dry', 0):>7}{c.get('A_real', 0):>8}"
                     f"{c.get('B_refused_unnamed', 0):>5}{c.get('asked', 0):>7}{c.get('errors', 0):>5}  "
                     f"{c.get('A_by_surface', {})}")
    lines.append(f"{'TOTAL':<16}{'':>6}{'':>8}{'':>6}{total_a:>5}{'':>7}{'':>8}{total_b:>5}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--child", help="(internal) run one arm from its spec file")
    ap.add_argument("--arms", default="", help="comma list of arms (default: all + the three seeds)")
    ap.add_argument("--quick", action="store_true", help="FC + a 4-turn seed (the pin's live arm)")
    ap.add_argument("--out", default=str(RECORDS_DIR), help="where the records go")
    ap.add_argument("--work", default="", help="the runs' scratch dir (default: a temp dir)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--summarize", action="store_true", help="print the table from the records and exit")
    args = ap.parse_args()
    if args.child:
        return run_child(args.child)
    records = Path(args.out)
    if args.summarize:
        print(table(records))
        return 0
    arms = QUICK_ARMS if args.quick else ARMS
    if args.arms:
        wanted = [a.strip() for a in args.arms.split(",") if a.strip()]
        arms = {k: v for k, v in {**ARMS, **QUICK_ARMS}.items() if k in wanted}
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="sign_ability_"))
    records.mkdir(parents=True, exist_ok=True)
    print(f"[sweep] {len(arms)} arm(s) -> {records}  (work {work})", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(run_arm, arm, argv, work, records): arm for arm, argv in arms.items()}
        for fut in futures:
            res = fut.result()
            results.append(res)
            print(f"[sweep] {res['arm']:<16} exit {res['exit']} {res['seconds']:>7}s  "
                  f"A={res['counts'].get('A_shown_signable_refused', '?')} "
                  f"B={res['counts'].get('B_refused_unnamed', '?')} "
                  f"shown={res['counts'].get('shown', '?')}", flush=True)
    print()
    print(table(records, list(arms)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
