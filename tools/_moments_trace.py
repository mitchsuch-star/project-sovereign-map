"""S14c part 4 (`docs/EVENTS_SPEC.md` §7): the moments' production-time trace.

ONE read-only observer, shared by the sweep (`tools/ai_v_sweep.py`, every
run), the driver (`tools/playtest_driver.py --moments-trace`, opt-in — every
other digest stays byte-identical) and the VP-1 road arms
(`tools/_vp1_road_arms.py`). It wraps `moments._tick`, `moments.premise`,
`moments._apply`, `moments.answer` and the crisis read the tick makes
(`war_council.foreground_in_tenure`) and CALLS THROUGH: it evaluates nothing
the engine does not, so a run with the trace is the run without it.

Each armed morning is one row::

    {"turn", "open", "crisis", "true", "false", "delivered", "passed"}

`true` / `false` — the entries whose premise the tick evaluated that
morning; the tick evaluates only a pending entry inside its window with its
road gate open, so an id in `true` was DUE that morning. `crisis` — the
tick's own crisis read (None on a morning with no candidate, when it never
asks). `open` — letters standing at the tick's entry. `passed` — the store
rows the morning wrote `passed`, by reason.

Each application of a plan (an answer, a lapse, a crowd-out) is one row::

    {"turn", "moment", "kind", "answer", "shown", "applied", "rows"}

`shown` — the quote the letter carried when it was answered (the letter's
own payload, read before the answer; "" for a lapse or a crowd-out, which
have no button); `applied` — the quote of the plan `_apply` received;
`rows` — each op's quoted `after` beside the world's value read right after
the application (`delivered`).

`judge()` reads both against the record's rules:

  ceilings (every arm)  R3: at most one letter delivered a morning;
                        `max_open`: the open count at the tick's entry plus
                        its delivery never exceeds it; R1: none delivered
                        while the tick read a crisis; none delivered whose
                        premise read false that morning;
  floors                every moment ever DUE ends arrived (fired /
                        answered / lapsed) or `passed(crowded)` — on
                        screen, never silent (S14C-X24); a moment still
                        pending when the run stops is reported, not judged;
  shown = applied       every answer's applied quote equals the one shown,
                        and every quoted figure equals the world's after.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

ARRIVED = ("fired", "answered", "lapsed")


class MomentsTrace:
    """The observer (see the module docstring). `world_getter` reads the
    live world at `summary()` (the driver swaps worlds on a reload)."""

    def __init__(self, world_getter: Optional[Callable[[], Any]] = None):
        self.mornings: List[Dict[str, Any]] = []
        self.applications: List[Dict[str, Any]] = []
        self.world_getter = world_getter
        self._frame: Optional[Dict[str, Any]] = None
        self._answering: Optional[Dict[str, Any]] = None
        self._saved: List[tuple] = []
        self.errors: List[str] = []

    # -- install ---------------------------------------------------------
    def install(self) -> "MomentsTrace":
        from backend.game_logic import moments as MO
        from backend.game_logic import war_council as WC
        trace = self
        real_tick, real_premise, real_fg = MO._tick, MO.premise, WC.foreground_in_tenure
        real_apply, real_answer = MO._apply, MO.answer

        def premise(world, e):
            result = real_premise(world, e)
            frame = trace._frame
            if frame is not None:
                frame["true" if result else "false"].append(str((e or {}).get("id") or ""))
            return result

        def foreground_in_tenure(world, *args, **kwargs):
            result = real_fg(world, *args, **kwargs)
            frame = trace._frame
            if frame is not None and frame["crisis"] is None:
                frame["crisis"] = bool(result)
            return result

        def _tick(world):
            before = {k: dict(v) for k, v in MO._state(world).items() if isinstance(v, dict)}
            frame = {"turn": MO._turn(world),
                     "open": sum(1 for r in before.values() if r.get("status") == MO.STATUS_FIRED),
                     "crisis": None, "true": [], "false": [], "delivered": [], "passed": {}}
            trace._frame = frame
            delivered: List[str] = []
            try:
                delivered = list(real_tick(world))
            finally:
                trace._frame = None
                frame["delivered"] = list(delivered)
                for mid, row in MO._state(world).items():
                    if (mid not in before and isinstance(row, dict)
                            and row.get("status") == MO.STATUS_PASSED):
                        frame["passed"][str(mid)] = str(row.get("reason") or "")
                trace.mornings.append(frame)
            return delivered

        def answer(world, dialogue, answer_key):
            shown = ""
            try:
                action = MO.ANSWER_ACTIONS.get(str(answer_key), "")
                for a in ((dialogue or {}).get("popup_payload") or {}).get("answers") or []:
                    if a.get("action") == action:
                        shown = str(a.get("quote") or "")
            except Exception as exc:  # observability must not kill the run
                trace.errors.append(f"answer: {exc!r}")
            trace._answering = {"answer": str(answer_key), "shown": shown}
            try:
                return real_answer(world, dialogue, answer_key)
            finally:
                trace._answering = None

        def _apply(world, p):
            real_apply(world, p)
            try:
                trace._record_application(world, p)
            except Exception as exc:
                trace.errors.append(f"apply: {exc!r}")

        for owner, name, new in ((MO, "_tick", _tick), (MO, "premise", premise),
                                 (MO, "_apply", _apply), (MO, "answer", answer),
                                 (WC, "foreground_in_tenure", foreground_in_tenure)):
            self._saved.append((owner, name, getattr(owner, name)))
            setattr(owner, name, new)
        return self

    def uninstall(self) -> None:
        while self._saved:
            owner, name, original = self._saved.pop()
            setattr(owner, name, original)

    # -- the application rows --------------------------------------------
    def _record_application(self, world, p: Dict[str, Any]) -> None:
        from backend.game_logic import moments as MO
        answering = self._answering
        if answering is not None:
            kind = "answer"
        elif self._frame is not None:
            kind = "crowded"
        else:
            kind = "lapse"
        lord = MO.owner(world)
        rows = []
        for row in p.get("rows") or []:
            rows.extend(_delivered(world, lord, row))
        self.applications.append({
            "turn": MO._turn(world), "moment": str(p.get("id") or ""), "kind": kind,
            "answer": str(p.get("answer") or ""),
            "shown": (answering or {}).get("shown", ""), "applied": str(p.get("quote") or ""),
            "rows": rows})

    # -- the verdict -------------------------------------------------------
    def summary(self, world=None) -> Dict[str, Any]:
        world = world if world is not None else (self.world_getter() if self.world_getter else None)
        from backend.game_logic import moments as MO
        state = {str(k): dict(v) for k, v in (MO._state(world).items() if world is not None else [])
                 if isinstance(v, dict)}
        pacing = MO.pacing(world) if world is not None else dict(MO.PACING_DEFAULTS)
        return {"measured": True,
                "judged": judge(self.mornings, self.applications, state, pacing),
                "mornings": self.mornings, "applications": self.applications,
                "errors": list(self.errors)}


def _delivered(world, lord: str, row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Each quoted figure of one op beside the world's value after it."""
    from backend.game_logic import moments as MO
    op = str(row.get("op") or "")
    out: List[Dict[str, Any]] = []

    def put(figure, quoted, value):
        out.append({"op": op, "figure": figure, "quoted": quoted, "delivered": value})

    if op == "gold":
        put("treasury", int(row["after"]), int((world.nation_gold or {}).get(lord, 0) or 0))
    elif op == "dp":
        from backend.game_logic.vassal import _dp_available
        put("diplomatic points", int(row["after"]), int(_dp_available(world, lord)))
    elif op == "relation" and not row.get("skip"):
        put(f"{row['court']} goodwill", int(row["after"]), int(MO._relation(world, lord, row["court"])))
    elif op == "alarm":
        put("alarm", int(row["after"]),
            int((getattr(world, "threat_by_target", {}) or {}).get(lord, 0) or 0))
    elif op == "loyalty":
        for court_row in row.get("courts") or []:
            vrow = (getattr(world, "vassals", {}) or {}).get(court_row["court"]) or {}
            put(f"{court_row['court']} loyalty", int(court_row["after"]), int(vrow.get("loyalty", 0) or 0))
    elif op == "autonomy" and "loyalty_after" in row:
        vrow = (getattr(world, "vassals", {}) or {}).get(row["court"]) or {}
        put(f"{row['court']} autonomy", int(row["level"]), int(vrow.get("autonomy", 0) or 0))
        put(f"{row['court']} loyalty", int(row["loyalty_after"]), int(vrow.get("loyalty", 0) or 0))
        put("ports shut", int(row["ports_after"]), _ports(world))
    elif op == "enact_law" and "ports_after" in row:
        from backend.game_logic import reforms
        law = reforms.find_law(world, lord, str(row["law"]))
        put(f"{row['law']} in force", 1, int(bool(law is not None and reforms.is_in_force(law))))
        put("ports shut", int(row["ports_after"]), _ports(world))
    return out


def _ports(world) -> int:
    from backend.game_logic import naval
    target = naval.trade_dominance_nation(world)
    return int(naval.closed_ports_against(world, target)) if target else 0


def judge(mornings: List[Dict[str, Any]], applications: List[Dict[str, Any]],
          state: Dict[str, Dict[str, Any]], pacing: Dict[str, int]) -> Dict[str, Any]:
    """The ceilings, the floors and shown = applied (the module docstring)."""
    max_open = int((pacing or {}).get("max_open", 1))
    ceilings: List[Dict[str, Any]] = []
    due: Dict[str, int] = {}
    arrived: Dict[str, int] = {}
    passed: Dict[str, str] = {}
    for m in mornings:
        turn = int(m.get("turn", 0))
        delivered = [str(x) for x in m.get("delivered") or []]
        if len(delivered) > 1:
            ceilings.append({"turn": turn, "rule": "R3", "moments": delivered})
        if delivered and int(m.get("open", 0)) + len(delivered) > max_open:
            ceilings.append({"turn": turn, "rule": "max_open", "moments": delivered})
        if delivered and m.get("crisis"):
            ceilings.append({"turn": turn, "rule": "R1", "moments": delivered})
        for mid in delivered:
            if mid not in (m.get("true") or []) or mid in (m.get("false") or []):
                ceilings.append({"turn": turn, "rule": "premise", "moments": [mid]})
            arrived.setdefault(mid, turn)
        for mid in m.get("true") or []:
            due.setdefault(str(mid), turn)
        for mid, reason in (m.get("passed") or {}).items():
            passed[str(mid)] = str(reason)
    floors: Dict[str, Dict[str, Any]] = {}
    for mid, first in sorted(due.items()):
        row = state.get(mid) or {}
        status = str(row.get("status") or "")
        verdict = ("pending" if not status else
                   "ok" if status in ARRIVED or (status == "passed" and row.get("reason") == "crowded")
                   else "silent")
        floors[mid] = {"first_due": first, "status": status,
                       "reason": str(row.get("reason") or ""), "verdict": verdict}
    mismatches = []
    for a in applications:
        if a.get("kind") == "answer" and a.get("shown") and a["shown"] != a.get("applied"):
            mismatches.append({"turn": a.get("turn"), "moment": a.get("moment"), "figure": "quote",
                               "quoted": a["shown"], "delivered": a.get("applied")})
        for r in a.get("rows") or []:
            if int(r.get("quoted", 0)) != int(r.get("delivered", 0)):
                mismatches.append(dict(r, turn=a.get("turn"), moment=a.get("moment")))
    return {"mornings": len(mornings), "ceiling_breaches": ceilings,
            "floors": floors, "floor_breaches": sorted(m for m, f in floors.items() if f["verdict"] == "silent"),
            "arrived": arrived, "passed": passed,
            "answers": [{"turn": a.get("turn"), "moment": a.get("moment"), "kind": a.get("kind"),
                         "answer": a.get("answer"), "figures": len(a.get("rows") or [])}
                        for a in applications],
            "shown_equals_applied": not mismatches, "mismatches": mismatches}


def unmeasured(reason: str) -> Dict[str, Any]:
    return {"measured": False, "reason": reason}
