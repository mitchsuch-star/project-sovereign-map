"""AU-1 "the books and the figure" — the pins (`docs/AUTHORITY_CURRENCY_SPEC.md`
§5.2, §5.6, §5.8, §6 the AU-1 row; the rules `SYSTEMS_REFERENCE.md` §169).

One writer, one ring, one quote: `backend/game_logic/standing.py` is the only
door to the lord's authority in production (the AST census), every write
names a cause from `display_names.AUTHORITY_CAUSES` (the cause census), the
tracker books every move in its ring and fires the threshold events on every
crossing (re-armed on the way up), the strategic rollback restores the whole
store, the instrument's `residual` reads 0 on a scripted run, the chip's key
rides every base response, the dent clause lands on the morning's line in
both views and a quiet morning is byte-identical, the letters say
"authority". The committed records: the HEAD record names the direct
writers; the slice's record reads 0.
"""
from __future__ import annotations

import ast
import json
import os
import string
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
BACKEND = REPO / "backend"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
STORE_FILES = {"backend/models/authority.py", "backend/game_logic/standing.py"}
# the one wrapper that forwards a cause by name (its own callers must pass a literal)
CAUSE_FORWARDERS = {("backend/game_logic/diplomacy.py", "modify_nation_authority")}


def _rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _production_trees():
    for path in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        yield _rel(path), ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _is_main_guard(node: ast.AST) -> bool:
    """`if __name__ == "__main__":` — a demo block, never production."""
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    left = node.test.left
    return (isinstance(left, ast.Name) and left.id == "__name__"
            and any(isinstance(c, ast.Constant) and c.value == "__main__" for c in node.test.comparators))


def _walk(tree: ast.AST):
    """Every node outside a `__main__` guard, with its enclosing function."""
    stack = [(tree, None)]
    while stack:
        node, func = stack.pop()
        if _is_main_guard(node):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = node
        yield node, func
        for child in ast.iter_child_nodes(node):
            stack.append((child, func))


@pytest.fixture(scope="module")
def world():
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def tracker():
    from backend.models.authority import AuthorityTracker
    return AuthorityTracker()


# ═══════════════════════════════════════════════════════════════════════
# The censuses
# ═══════════════════════════════════════════════════════════════════════

class TestTheAstCensus:
    """No write to the store outside its two files (§5.2 "one writer")."""

    def test_no_assignment_to_authority_outside_the_store(self):
        offenders = []
        for rel, tree in _production_trees():
            if rel in STORE_FILES:
                continue
            for node, _ in _walk(tree):
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                    targets = [node.target]
                for t in targets:
                    if isinstance(t, ast.Attribute) and t.attr == "authority":
                        offenders.append(f"{rel}:{node.lineno}")
                    if isinstance(t, ast.Subscript):
                        v = t.value
                        name = v.attr if isinstance(v, ast.Attribute) else getattr(v, "id", "")
                        if name == "nation_authority":
                            offenders.append(f"{rel}:{node.lineno} (nation_authority)")
        assert not offenders, offenders

    def test_no_call_to_the_old_writers_outside_the_store(self):
        offenders = []
        for rel, tree in _production_trees():
            if rel in STORE_FILES:
                continue
            for node, _ in _walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr in ("modify_authority", "modify_nation_authority")):
                    offenders.append(f"{rel}:{node.lineno}")
        assert not offenders, offenders

    def test_the_rollback_restores_the_whole_store(self):
        src = (BACKEND / "commands" / "strategic_executor.py").read_text(encoding="utf-8")
        assert "world.authority_tracker.snapshot()" in src
        assert "world.authority_tracker.restore(_tracker_before)" in src
        assert "_tracker_before[0]" not in src


def _cause_keys(arg: ast.AST, func) -> list:
    """The literal keys a cause argument can take: a constant, both arms of
    a conditional, or a name assigned from constants in the same function."""
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return [arg.value]
    if isinstance(arg, ast.IfExp):
        return _cause_keys(arg.body, func) + _cause_keys(arg.orelse, func)
    if isinstance(arg, ast.Name) and func is not None:
        keys = []
        for node in ast.walk(func):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == arg.id for t in node.targets):
                keys.extend(_cause_keys(node.value, func))
        return keys
    return []


def _writer_calls():
    for rel, tree in _production_trees():
        if rel in STORE_FILES:
            continue
        for node, func in _walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in ("move", "spend", "regrow"):
                continue
            owner = node.func.value
            if not (isinstance(owner, ast.Name) and owner.id in ("standing", "_standing")):
                continue
            yield rel, func, node


class TestTheCauseCensus:
    """Every production write names a cause the table has, with the fields
    its text needs (§5.2)."""

    def test_every_writer_call_names_a_key_from_the_table(self):
        from backend.display_names import AUTHORITY_CAUSES
        offenders, seen = [], 0
        for rel, func, call in _writer_calls():
            seen += 1
            if (rel, getattr(func, "name", "")) in CAUSE_FORWARDERS:
                continue
            cause = next((k.value for k in call.keywords if k.arg == "cause"), None)
            if cause is None:
                cause = call.args[3] if len(call.args) > 3 else None
            keys = _cause_keys(cause, func) if cause is not None else []
            if not keys or any(k not in AUTHORITY_CAUSES or k == "unattributed" for k in keys):
                offenders.append(f"{rel}:{call.lineno} {keys or ast.dump(cause) if cause is not None else 'no cause'}")
        # the survey's 32 sites: 24 `modify_authority` calls (the capture's two branches became one call)
        # and 8 direct writes (three inside the tracker, two the rollback's snapshot / restore),
        # plus the two wrappers that forward a cause (`_spend_authority`, `modify_nation_authority`);
        # AU-2b adds two `regrow` writes — the ceremonies' (`moments._apply_authority`) and the
        # Show's (`imperial_designs.decree`, an Act with a `ceiling`)
        assert seen == 31, seen
        assert not offenders, offenders

    def test_every_key_used_is_given_its_fields(self):
        from backend.display_names import AUTHORITY_CAUSES
        offenders = []
        for rel, func, call in _writer_calls():
            cause = next((k.value for k in call.keywords if k.arg == "cause"), None)
            if cause is None:
                cause = call.args[3] if len(call.args) > 3 else None
            given = {k.arg for k in call.keywords if k.arg}
            for key in _cause_keys(cause, func) if cause is not None else []:
                needed = {f for _, f, _, _ in string.Formatter().parse(AUTHORITY_CAUSES.get(key, "")) if f}
                if needed - given:
                    offenders.append(f"{rel}:{call.lineno} {key} lacks {sorted(needed - given)}")
        assert not offenders, offenders

    def test_the_table_is_whole(self):
        from backend.display_names import AUTHORITY_CAUSES, authority_cause
        assert all(isinstance(v, str) and v for v in AUTHORITY_CAUSES.values())
        assert authority_cause("own_hand_lost", battle="Elchingen") == "the field at Elchingen under your own hand"
        assert authority_cause("sovereign_captured", sovereign="Napoleon", region="Bohemia") == "Napoleon taken at Bohemia"
        assert authority_cause("law", law="the Berlin Decree") == "the law enacted: the Berlin Decree"
        assert authority_cause("not_a_key") == "not_a_key"                # never lost to its wording
        assert authority_cause("field_won") == "the field at {battle}, won against the odds"   # a missing field shows itself


# ═══════════════════════════════════════════════════════════════════════
# The tracker
# ═══════════════════════════════════════════════════════════════════════

class TestTheTracker:
    def test_a_move_is_booked_with_its_cause_and_clamped(self, tracker):
        assert tracker.move(+5, "field_won", "the field at Ulm, won against the odds", turn=3) == 0   # 100 stays 100
        assert tracker.moves == []                                          # a zero move is no row
        assert tracker.move(-5, "own_hand_lost", "the field at Elchingen under your own hand", "", turn=4) == -5
        assert tracker.authority == 95
        row = tracker.moves[-1]
        assert (row["seq"], row["turn"], row["delta"], row["key"]) == (1, 4, -5, "own_hand_lost")
        assert row["cause"] == "the field at Elchingen under your own hand"
        assert tracker.held["seq"] == 1 and tracker.held["turn"] == 4

    def test_the_ring_keeps_twenty_four(self, tracker):
        from backend.models.authority import MOVES_KEPT
        for i in range(30):
            tracker.move(-1 if i % 2 == 0 else +1, "debug_set", "x")   # down first: a +1 at 100 is no row
        assert len(tracker.moves) == MOVES_KEPT == 24
        assert [m["seq"] for m in tracker.moves] == list(range(7, 31))

    def test_a_direct_set_is_an_unattributed_move(self, tracker):
        tracker.authority = 80
        assert tracker.authority == 80 and tracker.moves[-1]["key"] == "unattributed"
        tracker.modify_authority(-5)
        assert tracker.authority == 75 and tracker.moves[-1]["key"] == "unattributed"

    def test_the_events_fire_on_any_write_and_re_arm(self, tracker):
        assert tracker.move(-35, "field_lost", "the field at X, lost with the numbers") == -35
        event = tracker.pop_event()
        assert event and event["threshold"] == 70 and event["type"] == "authority_event"
        assert event["title"] == event["name"] == "Whispers of Weakness"
        assert event["message"] == event["description"]
        assert event["cause"] == "the field at X, lost with the numbers" and event["authority"] == 65
        assert tracker.pop_event() is None
        tracker.move(+10, "field_won", "y")                                 # 75: the line re-arms
        assert tracker._crossed_thresholds == []
        tracker.move(-10, "field_lost", "z")                                # 65 again: it fires again
        assert tracker.pop_event()["threshold"] == 70

    def test_the_deepest_line_of_one_move(self, tracker):
        tracker.move(-80, "sovereign_captured", "Napoleon taken at Bohemia")
        events = tracker.held["events"]
        assert [e["threshold"] for e in events] == [30] and events[0]["title"] == "Emperor in Name Only"
        assert tracker._crossed_thresholds == [70, 50, 30]

    def test_record_response_returns_the_crossing_and_books_the_pattern(self, tracker):
        tracker.move(-28, "field_lost", "x")                                # 72
        event = None
        for _ in range(3):
            event = tracker.record_response("trust", 5) or event
        assert tracker.authority == 69 and tracker.moves[-1]["key"] == "trust_pattern"
        assert event and event["threshold"] == 70

    def test_snapshot_and_restore_round_trip(self, tracker):
        tracker.move(-5, "field_lost", "x", turn=2)
        snap = tracker.snapshot()
        tracker.move(-7, "debug_set", "d", turn=2)
        tracker.record_response("insist", 2)
        tracker.restore(snap)
        assert tracker.to_dict() == snap and tracker.authority == 95 and len(tracker.moves) == 1

    def test_serialization_carries_the_books_and_loads_no_phantom_move(self, tracker):
        from backend.models.authority import AuthorityTracker
        tracker.move(-5, "field_lost", "x", turn=2)
        tracker.move(-35, "field_lost", "y", turn=3)                        # a crossing queued
        data = json.loads(json.dumps(tracker.to_dict()))
        assert set(data) >= {"authority", "recent_responses", "_crossed_thresholds", "moves", "held"}
        loaded = AuthorityTracker.from_dict(data)
        assert loaded.to_dict() == tracker.to_dict() and len(loaded.moves) == 2
        assert loaded.pop_event()["threshold"] == 70


# ═══════════════════════════════════════════════════════════════════════
# The standing module
# ═══════════════════════════════════════════════════════════════════════

class TestTheStanding:
    def test_the_gates_are_what_the_rulings_say(self):
        from backend.game_logic import standing
        assert standing.PURCHASE_FLOOR == 60 and standing.CEILING == 95
        assert standing.keeps_books() is True and standing.courts_move() is False

    def test_the_refusal_is_the_sixty_line_on_the_grip(self, world):
        from backend.game_logic import standing
        assert standing.refusal(world, "France", +5) == ""
        assert standing.refusal(world, "France", -40) == ""            # the grip stays at 60
        reason = standing.refusal(world, "France", -45)
        assert "under 60" in reason and "refused" in reason and "100 → 55" in reason

    def test_the_quote_is_the_laws_line_and_the_presence(self, world):
        from backend.game_logic import standing
        from backend.game_logic.reforms import authority_line
        q = standing.quote(world, "France", -15)
        assert (q["before"], q["after"], q["refusal"]) == (100, 85, "")
        assert q["line"] == authority_line(100, 85)
        q = standing.quote(world, "France", -20)
        assert "the Presence +10% → +9%" in q["line"]                 # 80 on the grip: the aura dims

    def test_a_spend_lands_whole_or_not_at_all(self, world):
        from backend.game_logic import standing
        import copy
        w = copy.deepcopy(world)
        refused = standing.spend(w, "France", 45, "debug_set")
        assert refused["applied"] == 0 and refused["refusal"] and w.authority_tracker.authority == 100
        paid = standing.spend(w, "France", 15, "debug_set")
        assert paid["applied"] == -15 and w.authority_tracker.authority == 85

    def test_regrow_stops_at_the_ceiling_and_keeps_its_cooldown(self, world):
        from backend.game_logic import standing
        import copy
        w = copy.deepcopy(world)
        standing.move(w, "France", -8, "debug_set")                    # 92
        assert standing.regrow(w, "France", 4, "act", "te_deum", every=12, act="x") == 3   # 95, not 96
        assert standing.regrow(w, "France", 4, "act", "te_deum", every=12, act="x") == 0   # the ceiling
        standing.move(w, "France", -8, "debug_set")                    # 87
        assert standing.regrow(w, "France", 4, "act", "te_deum", every=12, act="x") == 0   # the cooldown
        w.current_turn += 12
        assert standing.regrow(w, "France", 4, "act", "te_deum", every=12, act="x") == 4

    def test_a_court_is_clamped_with_no_ring(self, world):
        from backend.game_logic import standing
        import copy
        w = copy.deepcopy(world)
        assert standing.standing_of(w, "Prussia") == 60
        assert standing.move(w, "Prussia", -15, "law", law="the Articles of War") == -15
        assert w.nation_authority["Prussia"] == 45
        assert standing.move(w, "Prussia", -100, "sovereign_captured", sovereign="x", region="y") == -45
        assert standing.regrow(w, "Prussia", 4, "act", "te_deum", act="x") == 0   # parked behind courts_move()

    def test_ai_refusal_is_the_reforms_own_floors(self, world):
        from backend.game_logic import standing, reforms
        import copy
        w = copy.deepcopy(world)
        w.nation_authority["Prussia"] = 44
        assert standing.ai_refusal(w, "Prussia", 15) == "authority 44 → 29 is under 30"
        assert standing.ai_refusal(w, "Prussia", 14) in ("", "authority 30 would leave fewer than 3 diplomatic points a turn")
        # the reforms' purse test reads the one gate (its chest and Net tests come first)
        src = (BACKEND / "game_logic" / "reforms.py").read_text(encoding="utf-8")
        body = src[src.index("def ai_purse_refusal"):src.index("def ai_repeal_before_lapse")]
        assert "standing.ai_refusal(world, nation, int(quote[\"price\"]))" in body
        assert "AI_AUTHORITY_FLOOR" not in body.split("standing.ai_refusal")[1]

    def test_the_payload_is_the_chips_key(self, world):
        from backend.game_logic import standing
        import copy
        w = copy.deepcopy(world)
        standing.move(w, "France", -5, "own_hand_lost", battle="Elchingen")
        p = standing.payload(w, "France")
        assert set(p) == {"value", "label", "grip", "presence", "moves"}
        assert (p["value"], p["grip"], p["presence"]) == (95, 95, 10)
        assert all(isinstance(p[k], int) for k in ("value", "grip", "presence"))
        assert p["moves"][0] == {"turn": 1, "delta": -5, "cause": "the field at Elchingen under your own hand", "party": ""}
        for _ in range(7):
            standing.move(w, "France", -1, "debug_set")
        assert len(standing.payload(w, "France")["moves"]) == 5

    def test_the_quote_is_what_a_law_applies(self, world):
        from backend.game_logic import reforms, standing
        import copy
        w = copy.deepcopy(world)
        row = next(r for r in reforms.deck(w, "France") if r.get("currency") == "authority")
        w.nation_gold["France"] = 10 ** 6
        quote = standing.quote(w, "France", -int(row["price"]))
        assert quote["line"].rstrip(".") in reforms.terms_line(w, "France", row)
        reforms.enact_law(w, "France", row)
        assert w.authority_tracker.authority == quote["after"]
        last = w.authority_tracker.moves[-1]
        assert last["key"] == "law" and last["cause"] == f"the law enacted: {reforms.display_name(row)}"

    def test_the_quote_is_what_a_letter_applies(self, world):
        from backend.game_logic import affairs, moments as MO, standing
        import copy
        w = copy.deepcopy(world)
        e = affairs.template_by_id(w, "chancellors_letters")
        assert e is not None
        p = MO.plan(w, e, "decline")
        row = next(r for r in p["rows"] if r["op"] == "authority")
        assert (row["before"], row["loss"], row["after"]) == (100, 5, 95) and not row["floor"]
        assert row["line"] == standing.quote(w, "France", -5)["line"].rstrip(".")
        assert row["letter"] == e["title"] and row["party"] == "Cambacérès"
        MO._apply(w, p)
        assert w.authority_tracker.authority == row["after"]
        last = w.authority_tracker.moves[-1]
        assert last["key"] == "letter_declined" and last["party"] == "Cambacérès"
        assert last["cause"] == f"{e['title']} declined"

    def test_at_the_floor_the_clamp_is_said(self, world):
        """AU-3 (BUG_FIXES.md §AU): the Decline that takes nothing says so."""
        from backend.game_logic import affairs, moments as MO
        import copy
        w = copy.deepcopy(world)
        w.authority_tracker.authority = 71
        e = affairs.template_by_id(w, "chancellors_letters")
        row = next(r for r in MO.plan(w, e, "decline")["rows"] if r["op"] == "authority")
        assert row["loss"] == 0 and row["floor"] is True
        assert row["line"].startswith("Authority 71 → 71 — nothing is taken: the floor holds at 71")

    def test_the_word_on_the_letters(self, world):
        from backend.game_logic import moments as MO
        assert MO._derived_button_line(world, "France", [{"op": "authority", "before": 85, "after": 80}]) == "authority 85 → 80"
        deck = json.loads(SCENARIO.read_text(encoding="utf-8"))
        text = json.dumps(deck)
        assert "standing {authority_before}" not in text and "authority {authority_before}" in text


# ═══════════════════════════════════════════════════════════════════════
# The instrument on a scripted run
# ═══════════════════════════════════════════════════════════════════════

class TestTheResidual:
    def test_residual_zero_on_a_scripted_run(self, world):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import standing
        from tools._standing_trace import StandingTrace
        import copy
        w = copy.deepcopy(world)
        trace = StandingTrace(lambda: w).install()
        try:
            t = w.authority_tracker
            for _ in range(6):
                t.record_response("trust", int(w.current_turn))
            for _ in range(4):
                t.record_response("insist", int(w.current_turn))
            w.vindication_tracker.record_choice("Ney", "insist", {"action": "attack", "marshal": "Ney"})
            w.vindication_tracker.resolve_battle("Ney", "defeat", types.SimpleNamespace(world=w))
            executor = CommandExecutor()
            executor._meta._execute_debug({"action": "debug", "target": "set_authority 70"},
                                          {"world": w, "executor": executor, "debug_mode": True})
            standing.move(w, "France", -5, "own_hand_lost", battle="Elchingen")
            snap = t.snapshot()
            standing.move(w, "France", -9, "debug_set")
            t.restore(snap)                                             # the RS-5 rollback un-books
            w.advance_turn()
            standing.move(w, "France", +5, "field_won", battle="Ulm")
            w.advance_turn()
        finally:
            trace.uninstall()
        s = trace.summary(w)
        assert s["measured"] and len(s["mornings"]) == 2
        assert all(m["residual"] == 0 for m in s["mornings"]), s["mornings"]
        assert s["residual"] == {"total": 0, "explained": 0, "unexplained": 0, "turns": [], "by_site": {}}
        assert s["direct"] == [] and s["tail"]["residual"] == 0
        keys = [m["key"] for m in s["moves"] if m["lord"] == "France" and not m.get("rolled_back")]
        assert "trust_pattern" in keys and "insisted_lost" in keys and "debug_set" in keys and "own_hand_lost" in keys
        assert any(m.get("rolled_back") for m in s["moves"])


# ═══════════════════════════════════════════════════════════════════════
# The figure, the box, the dent, the joins
# ═══════════════════════════════════════════════════════════════════════

class TestTheFigure:
    def test_the_base_response_carries_the_key_and_drains_the_crossing(self, world):
        import backend.main as M
        from backend.game_logic import standing
        import copy
        w = copy.deepcopy(world)
        standing.move(w, "France", -35, "field_lost", battle="Austerlitz")
        response = M.build_base_response(w, include_popup_passthroughs=False, queue_informational_notices=False,
                                         include_notifications=False, drain_draft_notices=False)
        assert response["authority"]["value"] == 65 and response["authority"]["moves"][0]["delta"] == -35
        box = response["authority_event"]
        assert box["title"] == "Whispers of Weakness" and box["message"] and box["cause"].startswith("the field at Austerlitz")
        again = M.build_base_response(w, include_popup_passthroughs=False, queue_informational_notices=False,
                                      include_notifications=False, drain_draft_notices=False)
        assert "authority_event" not in again                            # read, then cleared

    def test_the_dent_lands_on_the_morning_line_once_and_a_quiet_morning_is_byte_identical(self, world):
        import backend.main as M
        from backend.game_logic import dispatch, standing
        import copy
        w = copy.deepcopy(world)
        quiet = dispatch._build_situation(w, "France")["authority_label"]
        assert quiet == "Divine Right"          # AU-17: the tracker's word, the chip's
        standing.move(w, "France", -5, "own_hand_lost", battle="Elchingen")
        standing.move(w, "France", -5, "insisted_lost", party="Ney", marshal="Ney")
        dispatch.build_morning_dispatch(w)
        label = w.last_morning_dispatch["situation"]["authority_label"]
        assert label == ("Divine Right — down 10 since yesterday: the field at Elchingen under your own hand (−5), "
                         "Ney's objection overruled, and the field lost (−5)")
        assert M._readable_dispatch(w)["situation"]["authority_label"] == label   # the stored dispatch, re-served
        assert dispatch._build_situation(w, "France")["authority_label"] == "Divine Right"  # stamped: quiet
        standing.move(w, "France", -6, "field_lost", battle="Ulm")                   # 84: the aura's line
        assert dispatch._build_situation(w, "France")["authority_label"].endswith("; the Presence falls below 85")

    def test_the_connection_test_carries_the_key_at_boot(self):
        """The boot's `GET /test` feeds the top bar before the first command and
        does not pass `build_base_response` — the key rides it by name."""
        src = (BACKEND / "main.py").read_text(encoding="utf-8")
        body = src[src.index("def test_connection"):]
        body = body[:body.index("\n@app.")]
        assert '"authority": __import__("backend.game_logic.standing", fromlist=["payload"]).payload(' in body

    def test_both_views_print_the_label(self):
        for name in ("main.gd", "dispatch_view.gd"):
            assert 'situation.get("authority_label"' in (SCRIPTS / name).read_text(encoding="utf-8"), name

    def test_the_join_and_the_chip(self):
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert 'diplo_data["authority"] = response.get("authority", {})' in main      # the hand-copy (the Aug 30 trap)
        assert 'response.has("authority_event") and response.authority_event is Dictionary' in main
        box = main[main.index("func _display_authority_event"):]
        box = box[:box.index("\nfunc ")]
        assert 'authority_event.get("title"' in box and 'authority_event.get("message"' in box
        assert 'authority_event.get("cause"' in box
        bar = (SCRIPTS / "top_bar.gd").read_text(encoding="utf-8")
        assert "_build_authority_chip()" in bar[bar.index("func _ready"):bar.index("func _ready") + 8000]
        assert 'if data.has("authority"):' in bar and "update_authority_chip(data.get(\"authority\"))" in bar
        assert 'chip.name = "AuthorityChip"' in bar
        for line in ("value < 50", "value < 71", "value < 85"):
            assert line in bar, line
        assert "_refresh_authority_text()" in bar[bar.index("func _fit_bar"):]


# ═══════════════════════════════════════════════════════════════════════
# The records
# ═══════════════════════════════════════════════════════════════════════

class TestTheRecords:
    def test_the_head_record_names_the_direct_writers(self):
        rec = json.loads((REPO / "tools" / "_standing_before_final.json").read_text(encoding="utf-8"))
        assert rec["measured"] >= 55 and rec["residual_unexplained"] == 0
        assert rec["residual_total"] < 0
        assert {"authority.py:record_response", "vindication.py:resolve_battle"} <= set(rec["residual_sites"])

    def test_the_slices_record_reads_zero(self):
        rec = json.loads((REPO / "tools" / "_standing_final.json").read_text(encoding="utf-8"))
        assert rec["measured"] >= 55 and rec["residual_total"] == 0 and rec["residual_unexplained"] == 0
        assert rec["residual_sites"] == {} and rec["arms_with_residual"] == []
        rows = {f"{r['family']}/{r['arm']}": r for r in rec["rows"] if r.get("measured")}
        assert all(r["errors"] == [] for r in rows.values())
        # the sentence a tester repeats: no choice-class move ends under the purchases' floor is AU-3a's;
        # here only the instrument's own floor — every arm's moves carry a cause
        assert all("" not in r["by_cause"] for r in rows.values())

    def test_the_series_rig_reproduces_the_prior_on_every_arm(self):
        rec = json.loads((REPO / "tools" / "_standing_series_arms_final.json").read_text(encoding="utf-8"))
        assert set(rec["arms"]) >= {"0", "AUB", "ALL"}
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None, arm
        assert rec["arms"]["ALL"]["reach"]["counts"]["rows_booked"] > 0
        assert rec["arms"]["AUB"]["reach"]["counts"]["rows_booked"] == 0
