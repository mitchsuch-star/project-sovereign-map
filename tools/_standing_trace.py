"""AU-1 "the books and the figure" (`docs/AUTHORITY_CURRENCY_SPEC.md` §5.8, §7
step 1): the standing's production-time trace — the instrument that came
BEFORE the books, so the books could be measured against it.

ONE read-only observer, shared by the sweep (`tools/ai_v_sweep.py`, every
run), the driver (`tools/playtest_driver.py --standing-trace`, opt-in — every
other digest stays byte-identical) and the measure's record (`record`,
below). It wraps the player's writer on `AuthorityTracker` — `move` once the
books are open, `modify_authority` on the tree before them — the enclosing
functions of the direct writers, the courts' writer, and
`WorldState.advance_turn`, and CALLS THROUGH: it evaluates nothing the engine
does not, so a run with the trace is the run without it.

Each morning (every `advance_turn`) is one row::

    {"turn", "standing", "grip", "presence", "courts", "grace",
     "change", "booked", "residual", "courts_residual"}

`change` — the standing now against the last morning's (the first row reads
the boot figure); `booked` — the sum of the move rows since; `residual` =
`change − booked`: what moved the figure that no book recorded. `courts` —
the courts' table that morning; `courts_residual` — the same reading per
court, non-zero entries only. `grace` — each of the lord's marshals'
`expectation_grace_turn` (the Claims of the Army read it at AU-2a).

Each write is one row::

    {"turn", "lord", "before", "after", "asked", "delta", "key", "cause",
     "party", "site"}

`asked` — the delta the caller passed; `delta` — what the clamp applied;
`key` / `cause` / `party` — the books' entry (empty on the tree before them);
`site` — the first frame outside the store (`file:function`).

Each unbooked change inside a direct writer's function is one row
(`direct`): `{"turn", "delta", "site"}` — the trace diffs the tracker
around `AuthorityTracker.record_response`, `VindicationTracker.resolve_battle`,
`DisobedienceSystem.handle_redemption_response`,
`StrategicExecutor._handle_strategic_objection_from_endpoint`,
`MetaExecutor._execute_debug` and `main.debug_set_authority`, net of the
moves booked during the call. On the tree before the books `residual` names
these sites; once every write goes through the one writer, `direct` is empty
and `residual` reads 0 on every arm — the pin (`tests/test_standing_books.py`).
A rollback (`AuthorityTracker.restore`) un-books the moves it undoes, so the
RS-5 refused Trust leaves no residual either.

`summary()` is what the driver writes to `meta["standing_trace"]` and the
sweep to `final["standing_trace"]`; `record` composes the committed record
(`tools/_standing_before_final.json` on HEAD, `tools/_standing_final.json`
after the slice) from a measure directory, the sweep's runs and the road
arms::

    .venv/Scripts/python.exe tools/_standing_trace.py record \
        --driver-dirs DIR[,DIR…] --sweep DIR --out FILE --commit SHA [--note …]

Seeded paths, not laws: every figure is reported per arm.
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]

# The fixed lines every price is read against (AUTHORITY_CURRENCY_SPEC.md §1.2).
LINES = (85, 80, 70, 60, 50, 30)
# The store's own files: a write's `site` is the first frame outside them.
_OWN = ("authority.py", "standing.py", "_standing_trace.py")

# The direct writers' enclosing functions (module, owner attribute path, site label).
DIRECT_WRITERS = (
    ("backend.models.authority", "AuthorityTracker.record_response", "authority.py:record_response"),
    ("backend.commands.vindication", "VindicationTracker.resolve_battle", "vindication.py:resolve_battle"),
    ("backend.commands.disobedience", "DisobedienceSystem.handle_redemption_response",
     "disobedience.py:handle_redemption_response"),
    ("backend.commands.strategic_executor", "StrategicExecutor._handle_strategic_objection_from_endpoint",
     "strategic_executor.py:_handle_strategic_objection_from_endpoint"),
    ("backend.commands.meta_executor", "MetaExecutor._execute_debug", "meta_executor.py:_execute_debug"),
    ("backend.main", "debug_set_authority", "main.py:debug_set_authority"),
)


def _site() -> str:
    """The first frame outside the store — `file:function`."""
    f = sys._getframe(1)
    while f is not None:
        name = os.path.basename(f.f_code.co_filename)
        if name not in _OWN:
            return f"{name}:{f.f_code.co_name}"
        f = f.f_back
    return "?"


def _resolve(module, dotted: str):
    owner = module
    *path, name = dotted.split(".")
    for step in path:
        owner = getattr(owner, step)
    return owner, name


class StandingTrace:
    """The observer (see the module docstring). `world_getter` reads the
    live world (the driver swaps worlds on a reload); without one the trace
    finds the world through the arguments of the function it wraps."""

    def __init__(self, world_getter: Optional[Callable[[], Any]] = None):
        self.mornings: List[Dict[str, Any]] = []
        self.moves: List[Dict[str, Any]] = []
        self.direct: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.skipped: List[str] = []
        self.world_getter = world_getter
        self._saved: List[tuple] = []
        self._first: Optional[int] = None      # the standing before the first observed write or morning
        self._last: Optional[int] = None       # the standing at the last morning
        self._booked = 0                       # the moves booked since the last morning
        self._booked_total = 0                 # the running total the direct wrappers net against
        self._courts_first: Dict[str, int] = {}
        self._courts_last: Dict[str, int] = {}
        self._courts_booked: Dict[str, int] = {}
        self._world_seen = None

    # -- the world ---------------------------------------------------------
    def _world(self, *candidates):
        for c in candidates:
            if c is None:
                continue
            if hasattr(c, "authority_tracker") and hasattr(c, "current_turn"):
                return c
            if isinstance(c, dict) and hasattr(c.get("world"), "authority_tracker"):
                return c["world"]
            inner = getattr(c, "world", None)
            if hasattr(inner, "authority_tracker"):
                return inner
        if self.world_getter is not None:
            try:
                return self.world_getter()
            except Exception:
                return None
        return self._world_seen

    def _turn(self, world=None) -> int:
        world = self._world(world)
        if world is not None:
            self._world_seen = world
        return int(getattr(world, "current_turn", 0) or 0) if world is not None else 0

    def _player(self, world=None) -> str:
        world = self._world(world)
        return str(getattr(world, "player_nation", "") or "") if world is not None else ""

    # -- install -----------------------------------------------------------
    def _swap(self, owner, name: str, new) -> None:
        self._saved.append((owner, name, getattr(owner, name)))
        setattr(owner, name, new)

    def install(self) -> "StandingTrace":
        from backend.models import authority as AU
        from backend.models.world_state import WorldState
        trace = self
        Tracker = AU.AuthorityTracker
        has_books = hasattr(Tracker, "move")

        # -- the player's writer --------------------------------------------
        if has_books:
            real_move = Tracker.move

            def move(self_, *a, **k):
                before = int(self_.authority)
                seq_before = int((getattr(self_, "held", {}) or {}).get("seq", 0) or 0)
                trace._note_first(before)
                applied = real_move(self_, *a, **k)
                try:
                    asked = int(a[0] if a else k.get("delta", 0))
                    ring = getattr(self_, "moves", None) or []
                    row = ring[-1] if ring and int(ring[-1].get("seq", 0) or 0) > seq_before else {}
                    trace._book(self_, before, int(self_.authority), asked, row)
                except Exception as exc:          # observability must not kill the run
                    trace.errors.append(f"move: {exc!r}")
                return applied
            self._swap(Tracker, "move", move)

            real_restore = Tracker.restore

            def restore(self_, *a, **k):
                before = int(self_.authority)
                kept = {int(r.get("seq", 0) or 0) for r in (getattr(self_, "moves", None) or [])}
                out = real_restore(self_, *a, **k)
                try:
                    trace._unbook(self_, before, kept)
                except Exception as exc:
                    trace.errors.append(f"restore: {exc!r}")
                return out
            self._swap(Tracker, "restore", restore)
        else:
            real_mod = Tracker.modify_authority

            def modify_authority(self_, delta):
                before = int(self_.authority)
                trace._note_first(before)
                out = real_mod(self_, delta)
                try:
                    trace._book(self_, before, int(self_.authority), int(delta), {})
                except Exception as exc:
                    trace.errors.append(f"modify_authority: {exc!r}")
                return out
            self._swap(Tracker, "modify_authority", modify_authority)

        # -- the courts' writer ---------------------------------------------
        if has_books:
            from backend.game_logic import standing as ST
            real_court_move = ST.move

            def court_move(world, lord, delta, *a, **k):
                player = str(getattr(world, "player_nation", "") or "")
                table = getattr(world, "nation_authority", None)
                before = int(table.get(lord, 60) or 0) if isinstance(table, dict) and lord != player else None
                out = real_court_move(world, lord, delta, *a, **k)
                if before is not None:
                    try:
                        trace._book_court(world, lord, before, int(table.get(lord, 60) or 0), int(delta),
                                          str(a[0] if a else k.get("cause", "")))
                    except Exception as exc:
                        trace.errors.append(f"court move: {exc!r}")
                return out
            self._swap(ST, "move", court_move)
        else:
            from backend.game_logic import diplomacy as DP
            from backend.game_logic import reforms as RF
            real_spend = RF._spend_authority

            def _spend_authority(world, nation, amount):
                table = getattr(world, "nation_authority", None)
                court = isinstance(table, dict) and nation != getattr(world, "player_nation", None)
                before = int(table.get(nation, 0) or 0) if court else None
                out = real_spend(world, nation, amount)
                if before is not None:
                    trace._book_court(world, nation, before, int(table.get(nation, 0) or 0), -int(amount), "law")
                return out
            self._swap(RF, "_spend_authority", _spend_authority)
            real_capture = WorldState._apply_sovereign_capture_consequences

            def _apply_sovereign_capture_consequences(world, marshal, captor_nation):
                table = getattr(world, "nation_authority", None)
                court = isinstance(table, dict) and marshal.nation != getattr(world, "player_nation", None)
                before = int(table.get(marshal.nation, 75) or 0) if court else None
                out = real_capture(world, marshal, captor_nation)
                if before is not None:
                    trace._book_court(world, marshal.nation, before, int(table.get(marshal.nation, 0) or 0),
                                      -int(getattr(world, "SOVEREIGN_CAPTURE_AUTHORITY_SHOCK", 40)),
                                      "sovereign_captured")
                return out
            self._swap(WorldState, "_apply_sovereign_capture_consequences",
                       _apply_sovereign_capture_consequences)
            real_mna = DP.modify_nation_authority

            def modify_nation_authority(world, nation, delta, *a, **k):
                table = getattr(world, "nation_authority", None)
                before = int(table.get(nation, 60) or 0) if isinstance(table, dict) else None
                out = real_mna(world, nation, delta, *a, **k)
                if before is not None:
                    trace._book_court(world, nation, before, int(table.get(nation, 60) or 0), int(delta), "")
                return out
            self._swap(DP, "modify_nation_authority", modify_nation_authority)

        # -- the direct writers ---------------------------------------------
        import importlib
        for module_name, dotted, site in DIRECT_WRITERS:
            # the API module is wrapped only where it is already loaded (the
            # driver's in-process transport); importing it into the sweep would
            # boot a second world and move the RNG under the run
            if module_name == "backend.main" and module_name not in sys.modules:
                self.skipped.append(f"{site}: backend.main is not loaded in this process")
                continue
            try:
                module = importlib.import_module(module_name)
                owner, name = _resolve(module, dotted)
                real = getattr(owner, name)
            except Exception as exc:
                self.errors.append(f"direct {site}: {exc!r}")
                continue
            self._swap(owner, name, self._direct_wrapper(real, site))

        # -- the morning ----------------------------------------------------
        real_advance = WorldState.advance_turn

        def advance_turn(world, *a, **k):
            out = real_advance(world, *a, **k)
            try:
                trace._morning(world)
            except Exception as exc:
                trace.errors.append(f"morning: {exc!r}")
            return out
        self._swap(WorldState, "advance_turn", advance_turn)
        return self

    def uninstall(self) -> None:
        while self._saved:
            owner, name, original = self._saved.pop()
            setattr(owner, name, original)

    def _direct_wrapper(self, real, site: str):
        trace = self

        def _tracker(a, k):
            for c in list(a) + list(k.values()):
                if hasattr(c, "record_response") and hasattr(c, "authority"):
                    return c
            world = trace._world(*a, *k.values())
            return getattr(world, "authority_tracker", None) if world is not None else None

        if inspect.iscoroutinefunction(real):
            async def wrapped(*a, **k):
                tracker = _tracker(a, k)
                before = int(tracker.authority) if tracker is not None else None
                booked0 = trace._booked_total
                try:
                    return await real(*a, **k)
                finally:
                    if tracker is not None:
                        trace._settle_direct(tracker, before, booked0, site)
            return wrapped

        def wrapped(*a, **k):
            tracker = _tracker(a, k)
            before = int(tracker.authority) if tracker is not None else None
            booked0 = trace._booked_total
            if before is not None:
                trace._note_first(before)
            try:
                return real(*a, **k)
            finally:
                if tracker is not None:
                    trace._settle_direct(tracker, before, booked0, site)
        return wrapped

    # -- the books ---------------------------------------------------------
    def _note_first(self, before: int) -> None:
        if self._first is None:
            self._first = int(before)
        if self._last is None:
            self._last = int(before)

    def _book(self, tracker, before: int, after: int, asked: int, row: Dict[str, Any]) -> None:
        delta = int(after) - int(before)
        self.moves.append({
            "turn": self._turn(), "lord": self._player(), "before": int(before), "after": int(after),
            "asked": int(asked), "delta": delta, "seq": int(row.get("seq", 0) or 0),
            "key": str(row.get("key") or ""), "cause": str(row.get("cause") or ""),
            "party": str(row.get("party") or ""), "site": _site()})
        self._booked += delta
        self._booked_total += delta

    def _unbook(self, tracker, before: int, kept: set) -> None:
        """A rollback (`restore`): the moves the ring no longer holds are
        un-booked, and the tracker's figure is the snapshot's again."""
        now = {int(r.get("seq", 0) or 0) for r in (getattr(tracker, "moves", None) or [])}
        gone = kept - now
        undone = 0
        for row in self.moves:
            if row.get("seq") in gone and not row.get("rolled_back"):
                row["rolled_back"] = True
                undone += int(row["delta"])
        self._booked -= undone
        self._booked_total -= undone
        # a restore to a figure the ring does not explain (a snapshot taken
        # before the trace was installed) is a direct write, said so
        unexplained = (int(tracker.authority) - int(before)) + undone
        if unexplained:
            self.direct.append({"turn": self._turn(), "delta": unexplained, "site": "authority.py:restore"})

    def _settle_direct(self, tracker, before: int, booked0: int, site: str) -> None:
        diff = int(tracker.authority) - int(before)
        unbooked = diff - (self._booked_total - booked0)
        if unbooked:
            self.direct.append({"turn": self._turn(), "delta": int(unbooked), "site": site})

    def _book_court(self, world, lord: str, before: int, after: int, asked: int, cause: str) -> None:
        delta = int(after) - int(before)
        if lord not in self._courts_first:
            self._courts_first[lord] = int(before)
        if lord not in self._courts_last:
            self._courts_last[lord] = int(before)
        self.moves.append({
            "turn": self._turn(world), "lord": str(lord), "before": int(before), "after": int(after),
            "asked": int(asked), "delta": delta, "seq": 0, "key": str(cause or ""), "cause": "",
            "party": "", "site": _site()})
        self._courts_booked[lord] = self._courts_booked.get(lord, 0) + delta

    # -- the morning row -----------------------------------------------------
    def _morning(self, world) -> None:
        self._world_seen = world
        player = str(getattr(world, "player_nation", "") or "")
        tracker = getattr(world, "authority_tracker", None)
        standing = int(getattr(tracker, "authority", 0) or 0) if tracker is not None else 0
        if self._first is None:
            self._first = standing
        if self._last is None:
            self._last = standing
        change = standing - self._last
        residual = change - self._booked
        courts = {str(n): int(v or 0) for n, v in (getattr(world, "nation_authority", {}) or {}).items()}
        courts_residual: Dict[str, int] = {}
        for n, v in courts.items():
            if n not in self._courts_first:
                self._courts_first[n] = v
            last = self._courts_last.get(n)
            if last is not None:
                r = (v - last) - self._courts_booked.get(n, 0)
                if r:
                    courts_residual[n] = r
        grip, presence = -1, -1
        try:
            from backend.models.authority import get_imperial_grip, sovereign_aura_strength
            grip = int(get_imperial_grip(world, player))
            sovereign = next((m for m in world.marshals.values()
                              if getattr(m, "nation", None) == player and getattr(m, "is_sovereign", False)
                              and not getattr(m, "captured_by", "") and int(getattr(m, "strength", 0) or 0) > 0),
                             None)
            if sovereign is not None:
                presence = int(round(10 * float(sovereign_aura_strength(world, player))))
        except Exception as exc:
            self.errors.append(f"grip: {exc!r}")
        grace = {str(m.name): int(getattr(m, "expectation_grace_turn", -1) or -1)
                 for m in world.marshals.values() if getattr(m, "nation", None) == player}
        self.mornings.append({
            "turn": int(getattr(world, "current_turn", 0) or 0), "standing": standing, "grip": grip,
            "presence": presence, "courts": courts, "grace": grace, "change": change,
            "booked": self._booked, "residual": residual, "courts_residual": courts_residual})
        self._last = standing
        self._booked = 0
        self._courts_last = dict(courts)
        self._courts_booked = {}

    # -- the verdict -------------------------------------------------------
    def summary(self, world=None) -> Dict[str, Any]:
        world = self._world(world)
        tracker = getattr(world, "authority_tracker", None) if world is not None else None
        end = int(getattr(tracker, "authority", 0) or 0) if tracker is not None else (
            self.mornings[-1]["standing"] if self.mornings else (self._last or 0))
        tail = {"since_turn": self.mornings[-1]["turn"] if self.mornings else 0,
                "change": end - (self._last if self._last is not None else end), "booked": self._booked}
        tail["residual"] = tail["change"] - tail["booked"]
        residuals = [m["residual"] for m in self.mornings]
        total = sum(residuals) + tail["residual"]
        explained = sum(int(d["delta"]) for d in self.direct)
        by_site: Dict[str, int] = {}
        for d in self.direct:
            by_site[d["site"]] = by_site.get(d["site"], 0) + int(d["delta"])
        series = [m["standing"] for m in self.mornings]
        lows = series + [end] + ([self._first] if self._first is not None else [])
        crossings = []
        for row in self.moves:
            if row.get("lord") != self._player(world) or row.get("rolled_back"):
                continue
            for line in LINES:
                if row["before"] >= line > row["after"]:
                    crossings.append({"turn": row["turn"], "line": line, "direction": "down"})
                elif row["before"] < line <= row["after"]:
                    crossings.append({"turn": row["turn"], "line": line, "direction": "up"})
        by_cause: Dict[str, Dict[str, int]] = {}
        for row in self.moves:
            label = row.get("key") or row.get("site") or "?"
            if row.get("lord") != self._player(world):
                label = f"{row.get('lord')}:{label}"
            entry = by_cause.setdefault(label, {"n": 0, "sum": 0, "asked": 0})
            entry["n"] += 1
            entry["sum"] += int(row["delta"])
            entry["asked"] += int(row["asked"])
        courts: Dict[str, Dict[str, int]] = {}
        for n, first in self._courts_first.items():
            values = [m["courts"].get(n, first) for m in self.mornings] + [first]
            courts[n] = {"start": first, "end": self._courts_last.get(n, first),
                         "min": min(values), "max": max(values)}
        return {"measured": True,
                "mornings": self.mornings, "moves": self.moves, "direct": self.direct, "tail": tail,
                "residual": {"total": total, "explained": explained, "unexplained": total - explained,
                             "turns": [m["turn"] for m in self.mornings if m["residual"]],
                             "by_site": by_site},
                "start": self._first if self._first is not None else end,
                "min": min(lows), "max": max(lows), "end": end,
                "crossings": crossings, "by_cause": by_cause, "courts": courts,
                "skipped": list(self.skipped), "errors": list(self.errors)}


def unmeasured(reason: str) -> Dict[str, Any]:
    return {"measured": False, "reason": reason}


SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
PROBE_NOT_DRIVEN = ("disobedience.py:handle_redemption_response (a whole redemption arc to stage)",
                    "strategic_executor.py:_handle_strategic_objection_from_endpoint (the RS-5 refused Trust)",
                    "main.py:debug_set_authority (the HTTP route keeps its own handler object; the"
                    " console verb `_execute_debug` is the same write, driven)")


def probe_direct_writers() -> Dict[str, Any]:
    """The direct writers a measured arm seldom reaches, driven on purpose on
    the 1805 boot with the trace installed: six Trust answers (the trust
    pattern's −3 at `record_response`), four Insist answers (the balanced
    hand's +1), an Insist vindicated by a defeat (`resolve_battle`'s −5),
    the console's set (`_execute_debug`), then one advance for the morning
    row. On the tree before the books every one is a `direct` row and the
    residual names it; after AU-1 each goes through the one writer and the
    residual reads 0. The three writers not driven are named in the row."""
    import types
    os.environ.setdefault("LLM_MODE", "mock")
    os.environ.pop("SOVEREIGN_SCENARIO", None)
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    world = WorldState.from_scenario(str(SCENARIO))
    trace = StandingTrace(lambda: world).install()
    try:
        tracker = world.authority_tracker
        turn = int(world.current_turn)
        for _ in range(6):
            tracker.record_response("trust", turn)
        for _ in range(4):
            tracker.record_response("insist", turn)
        world.vindication_tracker.record_choice(
            "Ney", "insist", {"action": "attack", "marshal": "Ney"}, turn=turn)
        world.vindication_tracker.resolve_battle("Ney", "defeat", types.SimpleNamespace(world=world))
        executor = CommandExecutor()
        executor._meta._execute_debug({"action": "debug", "target": "set_authority 70"},
                                      {"world": world, "executor": executor, "debug_mode": True})
        world.advance_turn()
    finally:
        trace.uninstall()
    out = trace.summary(world)
    out["not_driven"] = list(PROBE_NOT_DRIVEN)
    return out


# ═══════════════════════════════════════════════════════════════════════
# The record — the arms' summaries composed into one committed file
# ═══════════════════════════════════════════════════════════════════════

def arm_row(family: str, arm: str, trace: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not trace or not trace.get("measured"):
        return {"family": family, "arm": arm, "measured": False,
                "reason": str((trace or {}).get("reason") or "no trace in the run")}
    res = trace.get("residual") or {}
    downs = Counter(c["line"] for c in trace.get("crossings") or [] if c.get("direction") == "down")
    return OrderedDict([
        ("family", family), ("arm", arm), ("measured", True),
        ("mornings", len(trace.get("mornings") or [])),
        ("start", trace.get("start")), ("min", trace.get("min")), ("max", trace.get("max")), ("end", trace.get("end")),
        ("moves", sum(1 for m in trace.get("moves") or [] if not m.get("rolled_back"))),
        ("by_cause", trace.get("by_cause") or {}),
        ("residual_total", int(res.get("total", 0) or 0)),
        ("residual_unexplained", int(res.get("unexplained", 0) or 0)),
        ("residual_sites", res.get("by_site") or {}),
        ("residual_turns", res.get("turns") or []),
        ("crossings_down", {str(line): int(downs.get(line, 0)) for line in LINES if downs.get(line)}),
        ("courts_end", {n: v.get("end") for n, v in (trace.get("courts") or {}).items()}),
        ("errors", trace.get("errors") or []),
    ])


def collect(driver_dirs: List[Path], sweep: Optional[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for root in driver_dirs:
        for meta_path in sorted(root.rglob("arms/*/meta.json")):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception as exc:
                rows.append({"family": root.name, "arm": meta_path.parent.name, "measured": False,
                             "reason": f"unreadable meta: {exc!r}"})
                continue
            family = meta_path.parents[2].name
            rows.append(arm_row(family, meta_path.parent.name, meta.get("standing_trace")))
    if sweep is not None:
        for path in sorted(sweep.glob("arm*.json")):
            try:
                digest = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                rows.append({"family": "sweep", "arm": path.stem, "measured": False,
                             "reason": f"unreadable run: {exc!r}"})
                continue
            rows.append(arm_row("sweep", path.stem, (digest.get("final") or {}).get("standing_trace")))
    return rows


def compose(rows: List[Dict[str, Any]], commit: str, note: str) -> Dict[str, Any]:
    sites: Dict[str, Dict[str, int]] = {}
    for r in rows:
        for site, total in (r.get("residual_sites") or {}).items():
            entry = sites.setdefault(site, {"arms": 0, "sum": 0})
            entry["arms"] += 1
            entry["sum"] += int(total)
    measured = [r for r in rows if r.get("measured")]
    return OrderedDict([
        ("_what", "AU-1 — the standing's trace over the measured arms (AUTHORITY_CURRENCY_SPEC.md §5.8): "
                  "per arm the start / min / max / end of the lord's authority, the moves by cause (by site "
                  "on the tree before the books), the residual (the morning's change the books did not "
                  "record) with the direct writers it names, the lines crossed downward, the courts' end "
                  "figures. Seeded paths, not laws."),
        ("commit", commit), ("date", time.strftime("%Y-%m-%d")), ("note", note),
        ("arms", len(rows)), ("measured", len(measured)),
        ("residual_total", sum(int(r.get("residual_total", 0) or 0) for r in measured)),
        ("residual_unexplained", sum(int(r.get("residual_unexplained", 0) or 0) for r in measured)),
        ("residual_sites", sites),
        ("arms_with_residual", [f"{r['family']}/{r['arm']}" for r in measured if r.get("residual_total")]),
        ("unmeasured", [f"{r['family']}/{r['arm']}: {r.get('reason')}" for r in rows if not r.get("measured")]),
        ("rows", rows),
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="compose the committed record from the arms' metas and the sweep's runs")
    r.add_argument("--driver-dirs", default="", help="comma-separated run roots scanned for arms/*/meta.json")
    r.add_argument("--sweep", default="", help="`tools/ai_v_sweep.py --all --out DIR`")
    r.add_argument("--out", required=True)
    r.add_argument("--commit", default="")
    r.add_argument("--note", default="")
    r.add_argument("--probe", action="store_true",
                   help="drive the direct writers on purpose and add the probe's row")
    args = ap.parse_args()
    dirs = [Path(p.strip()).resolve() for p in args.driver_dirs.split(",") if p.strip()]
    rows = collect(dirs, Path(args.sweep).resolve() if args.sweep else None)
    if args.probe:
        sys.path.insert(0, str(ROOT))
        probe = probe_direct_writers()
        row = arm_row("probe", "direct_writers", probe)
        row["direct"] = probe.get("direct")
        row["not_driven"] = probe.get("not_driven")
        rows.insert(0, row)
    record = compose(rows, args.commit, args.note)
    Path(args.out).write_bytes((json.dumps(record, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"{record['arms']} arms ({record['measured']} measured); residual total {record['residual_total']}, "
          f"unexplained {record['residual_unexplained']}; sites {record['residual_sites']}")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
