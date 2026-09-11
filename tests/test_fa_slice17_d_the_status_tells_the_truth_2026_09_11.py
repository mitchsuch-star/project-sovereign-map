"""FA slice 17, part d — "The Status Tells the Truth" (FA-N28, N29, N36, N65,
N58, N30, N27).

Seven rows about the two morning surfaces reporting a marshal's state, landed
in REPRO_L's order (N28 → N29 → N36 + N65 → N58 → N30 → N27) because the
first three share one vocabulary and landing N36 first would have opened a
NEW cross-surface contradiction (the ledger saying `awaiting_decision` while
the dispatch still said `awaiting`).

Nothing here can move an AI decision: every seam is a renderer or a
renderer's producer. `BASELINE_SERIES` and M1–M7 are byte-identical by
construction, and that is stated as a fact about the seams, not as evidence.

Two pins flip CONSCIOUSLY in other files and say why at the flip:
`test_creative_audit_ca9_2026_08_08.py::TestN37RoutRecovery::test_stage_three_must_stay_good`
(its premise — "the final stage of retreat_recovery is the only recovery news"
— is exactly what FA-N58 retires) is rewritten in place.
"""

import ast
import contextlib
import io
import pathlib
import re

import pytest

from backend.game_logic import dispatch as D
from backend.game_logic import ledger as L
from backend.game_logic.dispatch import build_morning_dispatch
from backend.game_logic.ledger import build_strategic_ledger
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
GD = REPO / "godot-client" / "project-sovereign" / "scripts"
READY_LINE = "Your armies stand ready, Sire. The initiative is ours."


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _world():
    return _quiet(WorldState.from_scenario, SCENARIO)


def _order_to_swabia():
    return StrategicOrder(command_type="MOVE_TO", target="Swabia",
                          target_type="region", started_turn=1,
                          original_command="x", path=["Swabia"])


def _bad_odds(name="Ney"):
    return {"interrupt_type": "contact_bad_odds", "marshal": name, "enemy": "Mack",
            "location": "Swabia",
            "options": ["attack_anyway", "go_around", "hold_position", "cancel_order"]}


def _last_stand(name, where):
    return {"interrupt_type": "last_stand", "marshal": name, "enemy": "Mack",
            "enemy_nation": "Austria", "location": where,
            "options": ["fight_to_the_last", "attempt_breakout"]}


def _strip_gd_comments(src: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


# ═══════════════════════════════════════════════════════════════════════
# FA-N28 — a decision outranks the order it lacks
# ═══════════════════════════════════════════════════════════════════════

class TestFAN28ADecisionOutranksTheOrderItLacks:

    def test_levers_default_on(self):
        assert D.DECISION_OUTRANKS_THE_ORDER_IT_LACKS is True
        assert D.HALTED_IS_NOT_READY is True
        assert L.THE_LEDGER_SEES_THE_HALT is True
        assert L.THE_ORDERS_TAB_KNOWS_ITS_PRISONERS is True
        assert D.RECOVERY_COMPLETION_REACHES_THE_BRIEFING is True
        assert D.RAW_EVENT_KEYS_NEVER_PRINT is True
        assert D.ARREARS_AGE_IS_THE_MARSHALS is True

    def test_an_order_free_last_stand_is_reported_as_a_decision(self):
        w = _world()
        m = w.get_marshal("Massena")
        m.strategic_order = None
        m.pending_interrupt = _last_stand("Massena", m.location)
        status, note = D._derive_marshal_status(m, w)
        assert status == "awaiting_decision", (status, note)
        assert "awaiting your word" in note
        rows = D._build_marshal_status(w, "France")
        row = next(r for r in rows if r["name"] == "Massena")
        assert row["status"] == "awaiting_decision"

    def test_an_order_free_muster_confirm_is_reported_as_a_decision(self):
        w = _world()
        m = w.get_marshal("Davout")
        m.strategic_order = None
        m.pending_interrupt = {"interrupt_type": "muster_confirm", "marshal": "Davout",
                               "target": "Mack", "options": ["attack_anyway", "cancel_order"]}
        status, note = D._derive_marshal_status(m, w)
        assert status == "awaiting_decision", (status, note)
        assert "awaiting your word" in note and "Mack" in note

    def test_the_order_bound_arm_still_reports_a_decision(self):
        """CONTROL: the pre-existing arm (order + interrupt) must not regress."""
        w = _world()
        ney = w.get_marshal("Ney")
        ney.strategic_order = _order_to_swabia()
        ney.pending_interrupt = _bad_odds()
        status, note = D._derive_marshal_status(ney, w)
        assert status == "awaiting_decision"
        assert "Mack bars the way" in note

    def test_no_decision_no_order_is_awaiting(self):
        w = _world()
        m = w.get_marshal("Massena")
        m.strategic_order = None
        m.pending_interrupt = None
        assert D._derive_marshal_status(m, w)[0] in ("awaiting", "idle_restless")

    def test_the_lever_down_reproduces_awaiting_orders(self, monkeypatch):
        monkeypatch.setattr(D, "DECISION_OUTRANKS_THE_ORDER_IT_LACKS", False)
        w = _world()
        m = w.get_marshal("Massena")
        m.strategic_order = None
        m.pending_interrupt = _last_stand("Massena", m.location)
        assert D._derive_marshal_status(m, w) == ("awaiting", "Awaiting orders."), (
            "the defect: a life-or-death question filed as 'Awaiting orders.'")

    def test_both_renderers_give_the_halt_its_own_glyph(self):
        for name in ("main.gd", "dispatch_view.gd"):
            src = _strip_gd_comments((GD / name).read_text(encoding="utf-8"))
            block = src[src.index("match m_status:"):]
            block = block[:block.index("_:")]
            assert '"awaiting_decision":' in block, f"{name}: the halt renders with the default glyph"


# ═══════════════════════════════════════════════════════════════════════
# FA-N29 — the note does not call a halted army ready
# ═══════════════════════════════════════════════════════════════════════

class TestFAN29HaltedIsNotReady:

    def _halted_ney(self):
        w = _world()
        ney = w.get_marshal("Ney")
        ney.strategic_order = _order_to_swabia()
        ney.pending_interrupt = _bad_odds()
        return w, ney

    def test_a_halted_marshal_silences_the_ready_line(self):
        w, ney = self._halted_ney()
        d = _quiet(build_morning_dispatch, w)
        statuses = {m["name"]: m["status"] for m in d["marshals"]}
        assert statuses["Ney"] == "awaiting_decision"
        assert d.get("berthier_note") != READY_LINE, d.get("berthier_note")

    def test_the_same_army_unhalted_is_ready(self):
        """FALSIFIABLE in the other direction."""
        w, ney = self._halted_ney()
        ney.pending_interrupt = None
        ney.strategic_order = None
        d = _quiet(build_morning_dispatch, w)
        assert d.get("berthier_note") == READY_LINE, d.get("berthier_note")

    def test_the_lever_down_reproduces_the_false_reassurance(self, monkeypatch):
        monkeypatch.setattr(D, "HALTED_IS_NOT_READY", False)
        w, ney = self._halted_ney()
        d = _quiet(build_morning_dispatch, w)
        assert d.get("berthier_note") == READY_LINE, "the defect"


# ═══════════════════════════════════════════════════════════════════════
# FA-N36 — the Strategic Ledger sees the halt
# ═══════════════════════════════════════════════════════════════════════

class TestFAN36TheLedgerSeesTheHalt:

    def _halted(self):
        w = _world()
        ney = w.get_marshal("Ney")
        ney.strategic_order = _order_to_swabia()
        ney.pending_interrupt = _bad_odds()
        return w, ney

    def test_forces_and_orders_both_say_halted(self):
        w, ney = self._halted()
        ledger = _quiet(build_strategic_ledger, w)
        forces = next(f for f in ledger["forces"] if f["name"] == "Ney")
        assert forces["status"] == "awaiting_decision", forces
        assert "HALTED" in forces["strategic_order"]
        assert "turns left" not in forces["strategic_order"]
        orders = next(o for o in ledger["orders"] if o["marshal"] == "Ney")
        assert orders["has_order"] is True
        assert orders["path_remaining"] == 0, "the client composes '(N regions left)' from this"
        assert "awaiting your word" in orders["condition"]

    def test_the_same_order_without_a_halt_is_unchanged(self):
        w, ney = self._halted()
        ney.pending_interrupt = None
        ledger = _quiet(build_strategic_ledger, w)
        forces = next(f for f in ledger["forces"] if f["name"] == "Ney")
        assert forces["status"] == "moving_to"
        assert forces["strategic_order"] == "March Swabia (1 turns left)"
        orders = next(o for o in ledger["orders"] if o["marshal"] == "Ney")
        assert orders["path_remaining"] == 1
        assert orders["condition"] == "1 region(s) left"

    def test_dispatch_and_ledger_share_one_word(self):
        w, ney = self._halted()
        assert D._derive_marshal_status(ney, w)[0] == L._derive_status(ney) == "awaiting_decision"

    def test_the_lever_down_reproduces_moving_to(self, monkeypatch):
        monkeypatch.setattr(L, "THE_LEDGER_SEES_THE_HALT", False)
        w, ney = self._halted()
        ledger = _quiet(build_strategic_ledger, w)
        forces = next(f for f in ledger["forces"] if f["name"] == "Ney")
        assert forces["status"] == "moving_to", "the defect: a frozen man reported as marching"
        orders = next(o for o in ledger["orders"] if o["marshal"] == "Ney")
        assert orders["path_remaining"] == 1


# ═══════════════════════════════════════════════════════════════════════
# FA-N65 — the prisoner leaves the ORDERS tab
# ═══════════════════════════════════════════════════════════════════════

class TestFAN65ThePrisonerLeavesTheOrdersTab:

    def test_a_captured_marshal_has_no_orders_row(self):
        w = _world()
        _quiet(w.capture_marshal, w.marshals["Ney"], "Austria", "probe")
        ledger = _quiet(build_strategic_ledger, w)
        assert not [o for o in ledger["orders"] if o["marshal"] == "Ney"], (
            "'Ney at Vienna │ No active orders' — a prisoner listed as awaiting orders")
        forces = next(f for f in ledger["forces"] if f["name"] == "Ney")
        assert forces["status"] == "captured", "FA-32's half is untouched"

    def test_the_free_man_keeps_his_row(self):
        w = _world()
        ledger = _quiet(build_strategic_ledger, w)
        assert [o for o in ledger["orders"] if o["marshal"] == "Ney"]

    def test_the_lever_down_lists_the_prisoner_as_idle(self, monkeypatch):
        monkeypatch.setattr(L, "THE_ORDERS_TAB_KNOWS_ITS_PRISONERS", False)
        w = _world()
        _quiet(w.capture_marshal, w.marshals["Ney"], "Austria", "probe")
        ledger = _quiet(build_strategic_ledger, w)
        row = next(o for o in ledger["orders"] if o["marshal"] == "Ney")
        assert row["order_type"] == "No active orders" and row["location"] == "Vienna"


# ═══════════════════════════════════════════════════════════════════════
# FA-N58 — the recovery's completion reaches the briefing
# ═══════════════════════════════════════════════════════════════════════

class TestFAN58RecoveryReachesTheBriefing:

    def test_retreat_recovered_is_good_news(self):
        rows = D._build_turn_events(
            [{"type": "retreat_recovered", "marshal": "Ney", "nation": "France",
              "message": "Ney's army has fully recovered and is combat ready."}], "France")
        assert len(rows) == 1 and rows[0]["severity"] == "good", rows

    def test_parity_with_the_broken_sibling(self):
        rows = D._build_turn_events(
            [{"type": "broken_recovered", "marshal": "Ney", "nation": "France", "message": "x"},
             {"type": "retreat_recovered", "marshal": "Ney", "nation": "France", "message": "y"}],
            "France")
        assert [r["severity"] for r in rows] == ["good", "good"]

    def test_the_real_tick_produces_it_and_the_briefing_keeps_it(self):
        w = _world()
        ney = w.get_marshal("Ney")
        ney.retreating = True
        ney.retreat_recovery = 2
        events = _quiet(w._process_tactical_states)
        kinds = [e.get("type") for e in events]
        assert "retreat_recovered" in kinds, kinds
        rows = D._build_turn_events(events, "France")
        mine = [r for r in rows if r["type"] == "retreat_recovered"]
        assert len(mine) == 1 and mine[0]["severity"] == "good"
        assert ney.retreating is False

    def test_the_intermediate_stages_stay_info(self):
        for stage in (1, 2):
            rows = D._build_turn_events(
                [{"type": "retreat_recovery", "stage": stage, "message": "r", "nation": "France"}], "France")
            assert rows[0]["severity"] == "info"

    def test_the_lever_down_drops_the_completion(self, monkeypatch):
        monkeypatch.setattr(D, "RECOVERY_COMPLETION_REACHES_THE_BRIEFING", False)
        rows = D._build_turn_events(
            [{"type": "retreat_recovered", "marshal": "Ney", "nation": "France", "message": "x"}], "France")
        assert rows == [], "the defect: the one piece of recovery news the player is owed, dropped at the whitelist"


# ═══════════════════════════════════════════════════════════════════════
# FA-N30 — no raw key reaches the briefing
# ═══════════════════════════════════════════════════════════════════════

class TestFAN30NoRawKeyReachesTheBriefing:

    def test_an_unknown_type_renders_nothing(self):
        assert D._format_dispatch_event_text("no_such_event_type", {}) == ""

    def test_the_lever_down_leaks_the_key(self, monkeypatch):
        monkeypatch.setattr(D, "RAW_EVENT_KEYS_NEVER_PRINT", False)
        assert D._format_dispatch_event_text("no_such_event_type", {}) == "Diplomatic event: no_such_event_type"

    def test_the_settlement_offer_line_is_the_producers_own_sentence(self):
        w = _world()
        w.pending_dispatch_events = [{
            "type": "settlement_offer_arrival", "war_id": "w1", "offer_id": "o1",
            "proposer_nation": "Austria", "war_label": "the war", "amount": 500,
            "message": "Austria has offered terms to settle the war. Asking 500 gold.",
            "turn": int(w.current_turn), "event_family": "diplomatic"}]
        rows = D._build_diplomatic_events_section(w, "France")
        assert len(rows) == 1
        assert rows[0]["text"] == "Austria has offered terms to settle the war. Asking 500 gold."
        assert rows[0]["priority"] == "HIGH"

    def test_an_event_with_neither_template_nor_message_is_dropped(self):
        w = _world()
        w.pending_dispatch_events = [{"type": "no_such_event_type", "template_vars": {}, "fog_rule": "always"}]
        assert D._build_diplomatic_events_section(w, "France") == []

    def test_the_two_typed_events_now_have_sentences(self):
        aside = D._format_dispatch_event_text(
            "hegemony_relaxation_aside", {"hegemon": "France", "share": 0.31, "band": 1, "label": "France"})
        assert aside and "hegemony_relaxation_aside" not in aside and "31%" in aside
        blow = D._format_dispatch_event_text(
            "diplomatic_mission_blowback", {"nation": "Prussia", "delta": -3, "value": -12})
        assert blow and "Prussia" in blow and "-3" in blow and "diplomatic_mission_blowback" not in blow

    @staticmethod
    def _literal_producer_types(source: str) -> set:
        """Every literal event type a producer emits: the second positional
        argument of `queue_dispatch_event(...)`, and the `"type"` of any dict
        appended to a `pending_dispatch_events` list."""
        found = set()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            fname = getattr(func, "id", None) or getattr(func, "attr", None)
            if fname == "queue_dispatch_event" and len(node.args) >= 2:
                arg = node.args[1]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.add(arg.value)
            if fname == "append" and isinstance(func, ast.Attribute):
                owner = ast.unparse(func.value)
                if "dispatch_events" in owner and node.args and isinstance(node.args[0], ast.Dict):
                    for k, v in zip(node.args[0].keys, node.args[0].values):
                        if (isinstance(k, ast.Constant) and k.value == "type"
                                and isinstance(v, ast.Constant) and isinstance(v.value, str)):
                            found.add(v.value)
        return found

    def test_every_producer_type_has_a_sentence_or_carries_its_own(self):
        """The census that stops the class recurring."""
        types = set()
        for path in (REPO / "backend").rglob("*.py"):
            types |= self._literal_producer_types(path.read_text(encoding="utf-8"))
        assert "settlement_offer_arrival" in types and "hegemony_relaxation_aside" in types, (
            "the census lost the two producers it exists to see")
        orphans = sorted(t for t in types if not D.dispatch_event_type_is_renderable(t))
        assert orphans == [], f"producers whose type would have printed a raw key: {orphans}"

    def test_the_census_is_sensitive(self):
        synthetic = ('def f(world):\n'
                     '    queue_dispatch_event(world, "totally_new_beat", {}, "always")\n'
                     '    world.pending_dispatch_events.append({"type": "bare_new_beat", "message": "m"})\n')
        found = self._literal_producer_types(synthetic)
        assert found == {"totally_new_beat", "bare_new_beat"}
        assert not D.dispatch_event_type_is_renderable("totally_new_beat")


# ═══════════════════════════════════════════════════════════════════════
# FA-N27 — the arrears age is the marshal's, not the page's
# ═══════════════════════════════════════════════════════════════════════

class TestFAN27TheArrearsAgeIsTheMarshals:

    def _eroding(self, w, name, grace_turn):
        m = w.get_marshal(name)
        m.battles_won = 6            # an expectation, and no estate to meet it
        m.dotation_regions = []
        m.pension = 0
        m.expectation_grace_turn = grace_turn
        return m

    def _estate_lines(self, dispatch):
        head = dispatch.get("headline") or {}
        texts = [head.get("text", "")] + [b.get("text", "") for b in (head.get("sub_beats") or [])]
        return [t for t in texts if "unrewarded" in t or "without settlement" in t or "arrears" in t or "grievance" in t]

    @pytest.mark.parametrize("prior_runs", [2, 3, 4])
    def test_the_escalated_line_carries_the_true_age(self, prior_runs):
        """⚠ Over ALL THREE variants. The first cut of this pin simulated one
        run count, which lands on the LAST variant (step = run − LEAD_MAX − 1),
        so a mutation restoring `{turns}` in the first variant came back INERT
        in the sweep. Prior runs 2/3/4 render steps 0/1/2."""
        w = _world()
        w.current_turn = 17
        self._eroding(w, "Ney", grace_turn=0)          # age 17
        w.headline_lead_memory = {"class": "estate_eroding", "identity": "estate_eroding:Ney",
                                  "streak": prior_runs, "runs": {"estate_eroding:Ney": prior_runs}}
        d = _quiet(build_morning_dispatch, w)
        lines = self._estate_lines(d)
        assert lines, d.get("headline")
        assert any("17" in t for t in lines), lines
        run = prior_runs + 1
        assert not any(f" {run} turns" in t or f"is {run} turns" in t for t in lines), lines

    def test_the_lever_down_prints_the_run_counter(self, monkeypatch):
        monkeypatch.setattr(D, "ARREARS_AGE_IS_THE_MARSHALS", False)
        w = _world()
        w.current_turn = 17
        self._eroding(w, "Ney", grace_turn=0)
        w.headline_lead_memory = {"class": "estate_eroding", "identity": "estate_eroding:Ney",
                                  "streak": 5, "runs": {"estate_eroding:Ney": 5}}
        d = _quiet(build_morning_dispatch, w)
        lines = self._estate_lines(d)
        assert lines and any("6" in t for t in lines) and not any("17" in t for t in lines), lines

    def test_the_longest_eroding_marshal_is_the_one_named(self):
        """The one-candidate limit is KEPT (one estate line per page) but the
        candidate is the man who has waited longest, not dict order."""
        w = _world()
        w.current_turn = 20
        self._eroding(w, "Ney", grace_turn=16)          # age 4 — just eroding
        self._eroding(w, "Davout", grace_turn=8)        # age 12
        d = _quiet(build_morning_dispatch, w)
        head = d.get("headline") or {}
        texts = [head.get("text", "")] + [b.get("text", "") for b in (head.get("sub_beats") or [])]
        estate = [t for t in texts if "Davout" in t or "Ney" in t]
        assert any("Davout" in t for t in estate), texts

    def test_a_missing_age_still_renders_the_authored_line(self):
        """The `setdefault` guard: a candidate without `age` (a pre-fix save's
        memory, or another producer) must not go silent in the escalation
        block — the CA9 pins that build exactly that shape stay green."""
        assert 'fmt.setdefault("age", _run)' in (REPO / "backend" / "game_logic" / "dispatch.py").read_text(encoding="utf-8")
