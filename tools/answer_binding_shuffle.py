"""DD-1 S6 — THE ANSWER-BINDING SHUFFLE (October 11, 2026; PRE_DEPLOY_PLAN.md
§3.1 "The instrument" 3; rules SYSTEMS_REFERENCE.md §106).

Three letters from three courts are delivered through the REAL producer
(`ai_diplomacy.deliver_ai_proposal`, relations set so SF-V1 does not withhold
them) in EVERY delivery order, and at every queue position (the letter on
top; a queued letter brought up by `POST /mailbox/activate`); then every
typed answer and every button is sent through the real endpoints and the
outcome read against the shipped contract (IQ-7's closed grammar, CA9's
court guard, W6-0 / FA-N5's identity binding):

    bare answer            -> binds to the CURRENT letter only
    named answer, current  -> answers that court
    named answer, queued   -> REFUSED naming that court (the letter-book tail);
                              nothing promoted, nothing applied
    fail-closed shapes     -> answer nothing (a question, a condition, a deferral)
    button + own id        -> answers that letter
    button + queued id     -> refused as stale (`stale_dialogue`), nothing applied
    mailbox/respond        -> answers that mailbox item

A MISBIND is an answer applied to a court other than the one named, a bare
answer applied to a non-current letter, a refusal naming the wrong court, a
fail-closed line that relayed anything, or an answer that moved more than
the one letter it names. Every (order, position, form) is one row.

    .venv/Scripts/python.exe tools/answer_binding_shuffle.py                 # the record -> docs/audits/dd1/answer_binding.json
    .venv/Scripts/python.exe tools/answer_binding_shuffle.py --list          # every row, one line each
    .venv/Scripts/python.exe tools/answer_binding_shuffle.py --write-ledger  # rewrite tests/data/answer_binding_known_misbinds.json

Exit code 0 always — the shuffle is a measurement; its pin is
tests/test_dd1_answer_binding_shuffle.py (the ledger is the ratchet).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import itertools
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RECORD = ROOT / "docs" / "audits" / "dd1" / "answer_binding.json"
LEDGER = ROOT / "tests" / "data" / "answer_binding_known_misbinds.json"
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
PLAYER = "France"

# Three courts at PEACE with France on the 1805 boot, three treaty types the
# ratifier signs at the relation each needs (SF-V1 would withhold the rest).
LETTERS = [
    ("Prussia", "alliance", 60),
    ("Denmark", "non_aggression", 20),
    ("Saxony", "open_borders", 0),
]
# The typed forms, each with the court it names ("" = bare) and the outcome the
# contract requires: answer | refuse_named | nothing
TYPED_FORMS = [
    ("accept", "", "answer"),
    ("yes", "", "answer"),
    ("reject", "", "answer"),
    ("counter", "", "answer"),
    ("accept {court}'s offer", "{court}", "named"),
    ("reject the offer from {court}", "{court}", "named"),
    ("we shall accept {court}'s offer", "{court}", "named"),
    ("decline {court}'s {matter}", "{court}", "named"),
    ("{court}, yes", "{court}", "named_bare"),
    ("accept {court}'s offer if the others agree", "{court}", "nothing"),
    ("shall we accept?", "", "nothing"),
    ("accept later", "", "nothing"),
    ("accept tomorrow", "", "nothing"),
]
MATTER = {"alliance": "alliance", "non_aggression": "pact", "open_borders": "offer"}
BUTTON_ACTIONS = ("accept_ai_proposal", "reject_ai_proposal", "counter_ai_proposal")


@contextlib.contextmanager
def _quiet():
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        yield


def _env() -> None:
    os.environ["LLM_MODE"] = "mock"
    os.environ.setdefault("INK_IRON_SAVE_DIR", tempfile.mkdtemp(prefix="answer_binding_saves_"))
    os.environ["DEBUG_MODE"] = "false"
    os.environ["INK_DEBUG"] = "0"
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        os.environ.pop(key, None)


def _ordinary(nation: str, ptype: str) -> Dict[str, Any]:
    return {"source": nation, "recipient": PLAYER, "proposal_type": ptype, "priority": 1,
            "terms": {"type": ptype, "proposer_nation": nation, "target_nation": PLAYER,
                      "clauses": [ptype], "sweeteners": [], "demands": []},
            "talleyrand_assessment": "", "decision_reason": "hegemony_pressure",
            "turn_generated": 1}


class Board:
    """One fresh boot per staging: the world swapped into `backend.main`
    (world + game_state + parser together — the TestClient reads them)."""

    def __init__(self):
        import backend.main as M
        from backend.commands.parser import CommandParser
        from backend.models.world_state import WorldState
        from fastapi.testclient import TestClient
        self.M = M
        self.client = TestClient(M.app)
        self._parser = CommandParser(use_real_llm=False)
        with _quiet():
            self._template = WorldState.from_scenario(str(SCENARIO), seed="historical").to_dict()

    def stage(self, order: List[int]) -> List[Dict[str, Any]]:
        """A fresh board (the boot cloned through the save road); the three
        letters delivered in `order`; returns the delivered dialogues in
        DELIVERY order."""
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        from backend.models.world_state import WorldState
        with _quiet():
            world = WorldState.from_dict(json.loads(json.dumps(self._template, default=str)))
        self.M.world = world
        self.M.game_state = {"world": world, "executor": self.M.game_state.get("executor"),
                             "debug_mode": False}
        self.M.parser = self._parser
        dm = world.dialogue_manager
        dm._queue = []
        dm._current = None
        world.incoming_proposal_popup = None
        world.proposal_result_popup = None
        delivered = []
        for idx in order:
            court, ptype, relation = LETTERS[idx]
            world.nation_relations[world._make_diplo_key(court, PLAYER)] = int(relation)
            with _quiet():
                dlg = deliver_ai_proposal(_ordinary(court, ptype), world)
            assert isinstance(dlg, dict) and dlg.get("dialogue_id") is not None, (court, ptype, dlg)
            delivered.append(dlg)
        return delivered

    @property
    def world(self):
        return self.M.world

    def snapshot(self) -> Dict[str, Any]:
        w = self.world
        dm = w.dialogue_manager
        cur = dm.peek()
        return {
            "current": cur.get("dialogue_id") if cur else None,
            "queue": [d.get("dialogue_id") for d in dm.iter_queue()],
            "states": dict(w.diplomatic_states),
            "cooldowns": dict(getattr(w, "ai_proposal_cooldowns", {}) or {}),
        }

    def typed(self, line: str) -> Dict[str, Any]:
        with _quiet():
            return self.client.post("/command", json={"command": line}).json()

    def button(self, choice, dialogue_id=None) -> Dict[str, Any]:
        with _quiet():
            return self.client.post("/respond_to_diplomatic_dialogue",
                                    json={"choice": choice, "dialogue_id": dialogue_id}).json()

    def activate(self, mailbox_id: int) -> Dict[str, Any]:
        with _quiet():
            return self.client.post("/mailbox/activate", json={"mailbox_id": int(mailbox_id)}).json()

    def mailbox_respond(self, mailbox_id: int, choice: str) -> Dict[str, Any]:
        with _quiet():
            return self.client.post("/mailbox/respond",
                                    json={"mailbox_id": int(mailbox_id), "choice": choice}).json()


def _court_of(dlg: Dict[str, Any]) -> str:
    return str(dlg.get("target_nation") or (dlg.get("context") or {}).get("source_nation") or "")


def _moved(before: Dict[str, Any], after: Dict[str, Any], delivered: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Which letters left the manager, which states / cooldowns moved."""
    ids_before = {before["current"], *before["queue"]} - {None}
    ids_after = {after["current"], *after["queue"]} - {None}
    gone = sorted(ids_before - ids_after)
    courts_gone = [_court_of(d) for d in delivered if d.get("dialogue_id") in gone]
    states_moved = sorted(k for k in set(before["states"]) | set(after["states"])
                          if before["states"].get(k) != after["states"].get(k))
    cooldowns_moved = sorted(k for k in set(before["cooldowns"]) | set(after["cooldowns"])
                             if before["cooldowns"].get(k) != after["cooldowns"].get(k))
    return {"gone": gone, "courts_gone": courts_gone, "states_moved": states_moved,
            "cooldowns_moved": cooldowns_moved, "current_before": before["current"],
            "current_after": after["current"]}


def _judge(expect: str, named_court: str, current_court: str, response: Dict[str, Any],
           moved: Dict[str, Any], courts: List[str]) -> Dict[str, Any]:
    """The verdict: bound | misbind, with the reason."""
    msg = str(response.get("message") or "")
    gone = moved["courts_gone"]
    others_moved = [c for c in courts if c != (named_court or current_court)
                    and any(c in k for k in moved["states_moved"] + moved["cooldowns_moved"])]
    if expect == "answer":                      # the bare form: the current letter
        if gone == [current_court] and not others_moved:
            return {"verdict": "bound", "why": "the current letter answered"}
        if not gone and response.get("success") is False:
            # a bare word the grammar did not take (e.g. no counter on this type)
            return {"verdict": "bound", "why": "refused, nothing moved"}
        return {"verdict": "misbind", "why": f"bare answer moved {gone or 'nothing'} / others {others_moved}"}
    if expect in ("named", "named_bare"):
        if named_court == current_court:
            if gone == [current_court] and not others_moved:
                return {"verdict": "bound", "why": "the named (current) letter answered"}
            if expect == "named_bare" and not gone and response.get("dialogue_reprompt"):
                return {"verdict": "bound", "why": "re-prompted, nothing moved"}
            if not gone and response.get("success") is False:
                return {"verdict": "bound", "why": "refused, nothing moved"}
            return {"verdict": "misbind", "why": f"named current moved {gone or 'nothing'} / others {others_moved}"}
        # the named court is QUEUED
        if gone or others_moved:
            return {"verdict": "misbind", "why": f"named queued court {named_court}: moved {gone} / others {others_moved}"}
        if response.get("court_mismatch") and named_court in msg:
            return {"verdict": "bound", "why": "refused naming the queued court"}
        if response.get("dialogue_reprompt") or response.get("success") is False:
            if named_court in msg or current_court in msg or expect == "named_bare":
                return {"verdict": "bound", "why": "refused / re-prompted, nothing moved"}
            # The stable class (the reply's wording is the desk's flavour);
            # the reply itself rides the row.
            return {"verdict": "misbind", "why": "refusal names neither court (the line fell to the order desk)"}
        return {"verdict": "misbind", "why": "queued court: an unexpected reply"}
    if expect == "nothing":
        if not gone and not others_moved and not moved["states_moved"]:
            return {"verdict": "bound", "why": "nothing relayed"}
        return {"verdict": "misbind", "why": f"a fail-closed line moved {gone} / {moved['states_moved']}"}
    if expect == "button_own":
        if gone == [named_court] and not others_moved:
            return {"verdict": "bound", "why": "the letter with that id answered"}
        return {"verdict": "misbind", "why": f"button own id moved {gone or 'nothing'} / others {others_moved}"}
    if expect == "button_stale":
        if not gone and not moved["states_moved"] and response.get("stale_dialogue"):
            return {"verdict": "bound", "why": "stale id refused"}
        return {"verdict": "misbind", "why": f"queued id: moved {gone} / stale={response.get('stale_dialogue')} {msg[:100]}"}
    if expect == "button_bare":
        if gone == [current_court] and not others_moved:
            return {"verdict": "bound", "why": "no id: the current letter answered"}
        return {"verdict": "misbind", "why": f"button no id moved {gone or 'nothing'}"}
    if expect == "mailbox":
        if gone == [named_court] and not others_moved:
            return {"verdict": "bound", "why": "the mailbox item answered"}
        if not gone and response.get("success") is False:
            return {"verdict": "bound", "why": f"refused, nothing moved: {msg[:80]}"}
        return {"verdict": "misbind", "why": f"mailbox respond moved {gone or 'nothing'}"}
    return {"verdict": "misbind", "why": f"unknown expectation {expect}"}


def run(list_rows: bool = False) -> Dict[str, Any]:
    _env()
    board = Board()
    rows: List[Dict[str, Any]] = []
    courts = [c for c, _, _ in LETTERS]
    orders = list(itertools.permutations(range(len(LETTERS))))

    def _row(order, position, form, named, expect, response, moved, current_court):
        verdict = _judge(expect, named, current_court, response, moved, courts)
        row = {"order": [LETTERS[i][0] for i in order], "position": position, "form": form,
               "named": named, "current": current_court, "expect": expect,
               "reply": str(response.get("message") or "")[:200],
               "success": response.get("success"), "moved": moved, **verdict}
        rows.append(row)
        if list_rows:
            flag = "" if verdict["verdict"] == "bound" else "  ✗ MISBIND"
            print(f"{'/'.join(row['order']):<24} {position:<10} {form:<44} -> {verdict['why'][:60]}{flag}")

    for order in orders:
        # ── typed forms, the letter on top as delivered ───────────────
        for form_t, named_t, expect in TYPED_FORMS:
            for target_idx in order:
                court, ptype, _ = LETTERS[target_idx]
                form = form_t.format(court=court, matter=MATTER[ptype])
                named = named_t.format(court=court) if named_t else ""
                if not named and target_idx != order[0]:
                    continue          # a bare form is one row per order
                delivered = board.stage(list(order))
                current_court = _court_of(board.world.dialogue_manager.peek() or {})
                before = board.snapshot()
                response = board.typed(form)
                moved = _moved(before, board.snapshot(), delivered)
                _row(order, "top", form, named, expect, response, moved, current_court)
        # ── typed named forms after bringing a queued letter up ───────
        for form_t, named_t, expect in TYPED_FORMS:
            if not named_t:
                continue
            for target_idx in order[1:]:
                court, ptype, _ = LETTERS[target_idx]
                form = form_t.format(court=court, matter=MATTER[ptype])
                delivered = board.stage(list(order))
                target = next(d for d in delivered if _court_of(d) == court)
                act = board.activate(target["mailbox_id"])
                if not act.get("success"):
                    rows.append({"order": [LETTERS[i][0] for i in order], "position": "activate",
                                 "form": form, "named": court, "current": "", "expect": "activate",
                                 "reply": str(act.get("message") or "")[:200], "success": act.get("success"),
                                 "moved": {}, "verdict": "misbind", "why": "activate refused"})
                    continue
                current_court = _court_of(board.world.dialogue_manager.peek() or {})
                before = board.snapshot()
                response = board.typed(form)
                moved = _moved(before, board.snapshot(), delivered)
                _row(order, "activated", form, court, expect, response, moved, current_court)
        # ── buttons ───────────────────────────────────────────────────
        for action in BUTTON_ACTIONS:
            for target_idx in order:
                court = LETTERS[target_idx][0]
                delivered = board.stage(list(order))
                target = next(d for d in delivered if _court_of(d) == court)
                current_court = _court_of(board.world.dialogue_manager.peek() or {})
                before = board.snapshot()
                response = board.button(action, dialogue_id=target["dialogue_id"])
                moved = _moved(before, board.snapshot(), delivered)
                expect = "button_own" if court == current_court else "button_stale"
                _row(order, "button", f"{action} id={court}", court, expect, response, moved, current_court)
            # no id at all — the current letter
            delivered = board.stage(list(order))
            current_court = _court_of(board.world.dialogue_manager.peek() or {})
            before = board.snapshot()
            response = board.button(action, dialogue_id=None)
            moved = _moved(before, board.snapshot(), delivered)
            _row(order, "button", f"{action} (no id)", "", "button_bare", response, moved, current_court)
        # ── the letter-book's own respond ─────────────────────────────
        for target_idx in order:
            court = LETTERS[target_idx][0]
            delivered = board.stage(list(order))
            target = next(d for d in delivered if _court_of(d) == court)
            current_court = _court_of(board.world.dialogue_manager.peek() or {})
            before = board.snapshot()
            response = board.mailbox_respond(target["mailbox_id"], "accept_ai_proposal")
            moved = _moved(before, board.snapshot(), delivered)
            _row(order, "mailbox", f"mailbox/respond accept {court}", court, "mailbox", response, moved,
                 current_court)

    misbinds = [r for r in rows if r["verdict"] == "misbind"]
    classes = Counter(f"{r['position']}:{re.sub(r'(Prussia|Denmark|Saxony)', '<court>', r['form'])}: {r['why'][:60]}"
                      for r in misbinds)
    return {"rows": rows, "count": len(rows), "misbinds": len(misbinds),
            "misbind_classes": dict(classes.most_common()),
            "letters": [list(x) for x in LETTERS], "orders": len(orders)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out", default=str(RECORD))
    ap.add_argument("--write-ledger", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    rec = run(list_rows=args.list)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n[shuffle] {rec['count']} rows over {rec['orders']} orders — {rec['misbinds']} misbind(s)")
    for cls, n in rec["misbind_classes"].items():
        print(f"  {n:>3}  {cls}")
    if args.write_ledger:
        LEDGER.write_text(json.dumps(rec["misbind_classes"], indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"ledger -> {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
