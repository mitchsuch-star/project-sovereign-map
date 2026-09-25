"""GE-1 verification round (September 25, 2026) — the pins for every finding
the adversarial check of the review-round commit e5d67800 confirmed.

Four lenses attacked the FIX, not the finding (the close · the clocks · the
titles · the words), each finding sent to a refuter on a read-only snapshot:
29 filed, 27 survived. Record: docs/ENDGAME_PLAN.md §6 GE-1, the
verification-round addendum; rules: SYSTEMS_REFERENCE.md §64.2. Each test
names the finding it pins (V<n>, the check's own index), and drives the seam
the finding reproduced on.
"""

import contextlib
import io
import json
import random

import pytest

from backend.game_logic import fall, game_end
from tests.test_ge1_review_round import (
    _boot, _cede_from, _final_save, _napoleon_alone_at_lorraine, _post,
    _reduce_france_to, _set, _tick,
)


@pytest.fixture
def client(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend import save_manager as SM
    from tests._chip_census import board_env
    prior = (M.world, M.game_state.get("world"), M.parser)
    monkeypatch.setattr(SM, "SAVE_DIR", tmp_path)
    board_env(monkeypatch)
    yield TestClient(M.app), M
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _carve_posen(w, also_take=()):
    """France at war with Prussia holds Posen (and `also_take`), then a
    peace carves the Duchy of Warsaw out of Posen — the Tilsit shape."""
    from backend.game_logic.diplomacy import declare_war
    _quiet(declare_war, w, "France", "Prussia")
    for region in ("Posen",) + tuple(also_take):
        _quiet(w.capture_region, region, "France")
    w.war_scores[w._make_diplo_key("France", "Prussia")] = 100
    _quiet(w._ratify_treaty, {
        "type": "peace", "proposer_nation": "France",
        "target_nation": "Prussia", "sweeteners": [],
        "demands": [{"type": "create_client", "value": 1,
                     "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                     "client_display_name": "Duchy of Warsaw"}]})
    assert w.regions["Posen"].controller == "DuchyOfWarsaw"


# ════════════════════════════════════════════════════════════════════════
# V0 — no question after the Fall, on any road
# ════════════════════════════════════════════════════════════════════════

class TestNoQuestionAfterTheFall:
    def test_the_fatal_end_turn_raises_no_redemption(self, client):
        """V0 (P2): the soil clock's fifth end turn, a marshal at trust 15 —
        the fatal response asks nothing and the world keeps no question."""
        tc, M = client
        w = M.world
        _reduce_france_to(w, {"Brittany"})
        w.marshals["Davout"].trust.set(15)
        fallen = None
        for i in range(8):
            r = _post(tc, "/command", {"command": "end turn"}, seed=5100 + i)
            if r.get("game_over"):
                fallen = r
                break
        assert fallen is not None and fallen["ending"]["cause"] == game_end.CAUSE_SOIL
        assert not fallen.get("redemption_event")
        assert fallen.get("state") != "awaiting_redemption_choice"
        assert w.pending_redemption is None
        with contextlib.redirect_stdout(io.StringIO()):
            pending = tc.get("/pending_redemption").json()
        assert not pending.get("has_pending")

    def test_a_pause_save_after_the_fall_loads_clean(self, client, monkeypatch):
        """V0: a question standing in a save written after the Fall is not
        raised by its load."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = M.world
        _napoleon_alone_at_lorraine(w)
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert r["game_over"] is True
        davout = w.marshals["Davout"]
        davout.trust.set(15)
        davout.redemption_pending = True
        w.pending_redemption = {"marshal": "Davout", "trust": 15}
        saved = _post(tc, "/save", {"save_name": "after the fall"})
        assert saved.get("success"), saved
        name = saved.get("filename") or next(
            p.name for p in _final_save(w).parent.glob("*.json")
            if "after" in p.name)
        loaded = _post(tc, "/load", {"filename": name})
        assert loaded["game_over"] is True
        assert not loaded.get("redemption_event")
        assert M.world.pending_redemption is None

    def test_every_producer_is_gated(self):
        """V0: the checker, the standing read and the hoist all answer
        nothing once a terminal ending is recorded."""
        from backend.commands.disobedience import (
            DisobedienceSystem, hoist_tactical_redemption, standing_redemption)
        w = _boot()
        davout = w.marshals["Davout"]
        davout.trust.set(15)
        game_end.record_ending(w, "defeat", game_end.CAUSE_CHAINS)
        assert DisobedienceSystem().check_redemption_threshold(davout, w) is None
        w.pending_redemption = {"marshal": "Davout"}
        davout.redemption_pending = True
        assert standing_redemption(w) is None
        assert w.pending_redemption is None
        assert hoist_tactical_redemption(
            [{"type": "redemption_event", "redemption_event": {"marshal": "Davout"}}],
            w) is None

    def test_the_envelope_drops_a_question_staged_before_the_stamp(self):
        """V0: a result that staged its question BEFORE the death (the same
        command's trust dock, then the fall) carries it in the envelope's
        `extra` — the terminal attach drops it."""
        import backend.main as M
        w = _boot()
        game_end.record_ending(w, "defeat", game_end.CAUSE_CHAINS)
        response = _quiet(M.build_base_response, w, message="x",
                          redemption_event={"marshal": "Davout"},
                          state="awaiting_redemption_choice")
        assert response["game_over"] is True
        assert "redemption_event" not in response
        assert response.get("state") != "awaiting_redemption_choice"

    def test_a_closed_campaign_is_cleared_on_every_response(self, client, monkeypatch):
        """V0 (the close's clearing runs on EVERY call): an interrupt
        standing in a pause save written after the Fall is not raised by
        its load, though the loaded record is already closed."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = M.world
        _napoleon_alone_at_lorraine(w)
        _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert game_end.terminal_ending(w)["closed"] is True
        w.marshals["Davout"].pending_interrupt = {
            "interrupt_type": "contact", "marshal": "Davout",
            "options": ["attack", "hold_position", "cancel_order"]}
        saved = _post(tc, "/save", {"save_name": "later"})
        name = saved.get("filename") or next(
            p.name for p in _final_save(w).parent.glob("*.json")
            if "later" in p.name)
        loaded = _post(tc, "/load", {"filename": name})
        assert loaded["game_over"] is True
        assert not loaded.get("pending_interrupt")
        assert M.world.marshals["Davout"].pending_interrupt is None

    def test_the_command_writer_does_not_write_it_back(self):
        """V0: `main._include_command_redemption_event` runs after the close
        and must not re-seed the question."""
        import backend.main as M
        w = _boot()
        game_end.record_ending(w, "defeat", game_end.CAUSE_CHAINS)
        response = {}
        M._include_command_redemption_event(
            response, {"redemption_event": {"marshal": "Davout"}}, w)
        assert "redemption_event" not in response
        assert w.pending_redemption is None


# ════════════════════════════════════════════════════════════════════════
# V1 — the Emperor killed in his OWN standing order ends the pass
# ════════════════════════════════════════════════════════════════════════

class TestTheOwnOrderDeath:
    def test_no_order_marches_after_him(self, monkeypatch):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        ran = []

        def _step(self, marshal, world, game_state):
            ran.append(marshal.name)
            if marshal.name == "Napoleon":
                world.destroy_marshal(marshal, cause="battle", victor="Austria")
            return {"marshal": marshal.name, "message": "step"}

        monkeypatch.setattr(StrategicOrderProcessor, "_execute_strategic_turn", _step)
        monkeypatch.setattr(StrategicOrderProcessor, "_check_interrupts",
                            lambda self, marshal, world: None, raising=False)
        for name in ("Napoleon", "Soult"):
            m = w.marshals[name]
            m.strategic_order = StrategicOrder(
                command_type="HOLD", target=m.location, target_type="region",
                started_turn=w.current_turn - 1, original_command="hold",
                issued_turn=w.current_turn - 1)
        _quiet(StrategicOrderProcessor(CommandExecutor()).process_strategic_orders,
               w, {"world": w})
        assert game_end.terminal_ending(w)["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert "Napoleon" in ran and "Soult" not in ran

    def test_the_grievance_pass_and_autonomy_rest_after_it(self, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.game_logic import jealousy
        from backend.game_logic.turn_manager import TurnManager
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        calls = {"jealousy": 0, "autonomous": 0}

        def _strategic(self, world, game_state):
            world.destroy_marshal(world.marshals["Napoleon"], cause="battle",
                                  victor="Austria")
            return []

        def _jealousy(world):
            calls["jealousy"] += 1

        def _autonomous(self, game_state):
            calls["autonomous"] += 1
            return None
        monkeypatch.setattr(EnemyAI, "process_nation_turn",
                            lambda self, nation, world, game_state: [])
        monkeypatch.setattr(EnemyAI, "execute_admin_phase",
                            lambda self, nation, world, game_state: [])
        monkeypatch.setattr(StrategicOrderProcessor, "process_strategic_orders", _strategic)
        monkeypatch.setattr(jealousy, "process_turn", _jealousy)
        monkeypatch.setattr(TurnManager, "_process_autonomous_marshals", _autonomous)
        _quiet(TurnManager(w, CommandExecutor()).end_turn, {"world": w})
        assert game_end.terminal_ending(w)["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert calls == {"jealousy": 0, "autonomous": 0}


# ════════════════════════════════════════════════════════════════════════
# V2 / V3 — the Final save, and the lever that governs the close
# ════════════════════════════════════════════════════════════════════════

class TestTheFinalSave:
    def test_a_legacy_final_save_is_adopted_not_copied(self, client, monkeypatch):
        """V2: a Final save that does not name itself (the 975f1f13 shape)
        is adopted at load — no '(2)', '(3)', '(4)' on every load."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        _napoleon_alone_at_lorraine(M.world)
        _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        final = _final_save(M.world)
        data = json.loads(final.read_text(encoding="utf-8"))
        for record in data["world_state"]["endings"]:
            record.pop("final_save", None)
            record.pop("closed", None)
        final.write_text(json.dumps(data), encoding="utf-8")
        before = sorted(p.name for p in final.parent.glob("*.json"))
        for _ in range(3):
            loaded = _post(tc, "/load", {"filename": final.name})
            assert loaded["game_over"] is True
        after = sorted(p.name for p in final.parent.glob("*.json"))
        assert after == before
        assert game_end.terminal_ending(M.world)["final_save"] == str(final)

    def test_the_lever_gates_the_close_only(self, client, monkeypatch):
        """V3: THE_WAR_IS_CLOSED_AT_ONE_SEAM=False skips the close (no
        rebuild, no clearing) — and, as its comment now says, the attach
        rides every response either way."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        monkeypatch.setattr(game_end, "THE_WAR_IS_CLOSED_AT_ONE_SEAM", False)
        _napoleon_alone_at_lorraine(M.world)
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert r["game_over"] is True and r["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert not game_end.terminal_ending(M.world).get("closed")
        import inspect
        src = inspect.getsource(game_end)
        assert "It does NOT restore the pre-review /command-only attach" in src


# ════════════════════════════════════════════════════════════════════════
# V4 / V8 — a truce on its last turn, and a truce at a count of nought
# ════════════════════════════════════════════════════════════════════════

def _truce_with_everyone(w, relation=-90, turns_run=None):
    from backend.game_logic.diplomacy import ARMISTICE_DURATION
    for nation in list(w.get_nations_at_war_with("France")):
        _set(w, "France", nation, "ARMISTICE")
        key = w._make_diplo_key("France", nation)
        w.nation_relations[key] = relation
        if turns_run is not None:
            w.armistice_turns[key] = int(turns_run)
    return ARMISTICE_DURATION


class TestTheTruceOnItsLastTurn:
    def test_the_soil_clock_resumes_and_is_dated(self):
        """V4 (P2): 4 of 5, a truce that collapses into war at THIS advance —
        dated, critical, and the date is the date the Fall is stamped."""
        from backend.game_logic.diplomacy import (
            ARMISTICE_DURATION, _process_armistice_expiration)
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 4)
        _truce_with_everyone(w, relation=-90, turns_run=ARMISTICE_DURATION - 1)
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        assert view["ticking"] is False and view["resuming"] is True
        assert view["falls_at_end_of_turn"] == w.current_turn
        warn = fall.warning_state(w)
        assert warn["severity"] == "critical"
        sentence = fall.arm_clock_sentence(w, view)
        assert "the truce ends this turn and the war resumes" in sentence
        assert "stands still" not in sentence
        promised = view["falls_at_end_of_turn"]
        _quiet(_process_armistice_expiration, w)       # the advance's own step
        stamped = _tick(w, 1)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_SOIL]
        assert stamped[0]["turn"] == promised

    def test_a_truce_that_ends_in_peace_is_not_a_resumption(self):
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 4)
        _truce_with_everyone(w, relation=-30, turns_run=ARMISTICE_DURATION - 1)
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        assert view["resuming"] is False and view["truce_ends"] == "peace"
        assert view["falls_at_end_of_turn"] is None
        assert fall.warning_state(w)["severity"] == "warning"

    def test_the_chains_clock_resumes_on_the_captors_last_truce_turn(self):
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 9)
        _set(w, "France", "Austria", "ARMISTICE")
        key = w._make_diplo_key("France", "Austria")
        w.nation_relations[key] = -90
        w.armistice_turns[key] = ARMISTICE_DURATION - 1
        view = fall.get_fall_state(w)["arms"][fall.ARM_CHAINS]
        assert view["resuming"] is True
        assert view["falls_at_end_of_turn"] == w.current_turn
        assert fall.warning_state(w)["severity"] == "critical"
        assert "ends this turn and the war resumes" in fall.arm_clock_sentence(w, view)
        # …and a truce that ends in PEACE says the peace frees him.
        w.nation_relations[key] = -20
        view = fall.get_fall_state(w)["arms"][fall.ARM_CHAINS]
        assert "ends in peace this turn, and the peace frees him" in \
            fall.arm_clock_sentence(w, view)

    def test_a_truce_at_nought_is_not_a_peace(self):
        """V8: in a truce with every court, the count at 0 — never 'at
        peace', never 'a new war'."""
        w = _boot()
        _truce_with_everyone(w)
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 1)
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        assert view["turns"] == 0 and view["paused_by"] == "truce"
        sentence = fall.arm_clock_sentence(w, view)
        assert "no clock runs while the truce holds" in sentence
        assert "at peace" not in sentence and "a new war" not in sentence
        assert "at peace" not in fall.scope_sentence(w)

    def test_the_paused_count_is_stated_in_turns_of_war(self):
        """V4's second half: 'falls after N more turns of war', the unit the
        ticking sentence uses — never 'falls N turns later'."""
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 3)
        _truce_with_everyone(w)
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        sentence = fall.arm_clock_sentence(w, view)
        assert "falls after 2 more turns of war" in sentence
        assert "turns later" not in sentence


# ════════════════════════════════════════════════════════════════════════
# V5 / V6 — no court out of war with his realm holds the Emperor
# ════════════════════════════════════════════════════════════════════════

class TestNoCourtOutOfWarHoldsHim:
    def test_an_emptied_corps_at_peace_is_set_down_at_home(self):
        """V5 (P2): no court at war to take him — he goes home, never to the
        strongest court at peace."""
        from backend.campaign_log import format_event_oneliner
        w = _boot()
        for nation in list(w.get_nations_at_war_with("France")):
            _set(w, "France", nation, "PEACE")
        nap = w.marshals["Napoleon"]
        nap.strength = 0
        removed = _quiet(w.destroy_marshal, nap, cause="attrition")
        assert removed is False
        assert not nap.captured_by
        assert nap.strength == w.RANSOM_RETURN_STRENGTH
        assert w.regions[nap.location].controller == "France"
        assert fall.get_fall_state(w) is None
        row = [e for e in w.event_log if e.get("type") == "marshal_released"][-1]
        line = format_event_oneliner(row)
        assert "no court at war to take him" in line
        assert "restored to France by" not in line

    def test_at_war_he_is_still_taken(self):
        """Control: with a court at war, the fallback takes him as before."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        nap.strength = 0
        assert _quiet(w.destroy_marshal, nap, cause="attrition") is False
        assert nap.captured_by and w.is_at_war("France", nap.captured_by)

    def test_a_spent_guard_breaks_out_with_its_escort(self, client, monkeypatch):
        """V5's road: the breakout on a SPENT Guard no longer pays a toll it
        cannot — the Emperor keeps his last men instead of standing at 0."""
        tc, M = client
        w = M.world
        nap = _napoleon_alone_at_lorraine(w, strength=60)
        mack = w.marshals["Mack"]
        mack.location = "Lorraine"
        w._build_marshal_index()
        nap.pending_interrupt = {
            "interrupt_type": "last_stand", "marshal": "Napoleon",
            "enemy": "Mack", "enemy_nation": "Austria", "location": "Lorraine",
            "raised_turn": int(w.current_turn), "raised_by_ai": False,
            "options": ["fight_to_the_last", "attempt_breakout"],
            "sovereign": True, "message": "spent"}
        monkeypatch.setattr(random, "random", lambda: 0.0)
        with contextlib.redirect_stdout(io.StringIO()):
            r = tc.post("/strategic_response", json={
                "marshal_name": "Napoleon", "response_type": "last_stand",
                "choice": "attempt_breakout"}).json()
        assert "cuts his way out" in r["message"], r["message"]
        assert "last of his escort" in r["message"]
        assert nap.strength > 0 and not nap.captured_by

    def test_a_vassal_treaty_with_his_captor_frees_him(self):
        """V6 (P2): WAR→VASSAL with the captor releases him."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Austria", context="t")
        _set(w, "France", "Austria", "VASSAL")
        assert not nap.captured_by
        assert w.regions[nap.location].controller == "France"

    def test_releasing_a_captor_satellite_frees_him(self):
        """V6: VASSAL→PEACE (the release) frees him too."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "VASSAL"
        w.capture_marshal(nap, "Austria", context="t")
        _set(w, "France", "Austria", "PEACE")
        assert not nap.captured_by

    def test_a_truce_still_holds_him(self):
        """Control: WAR→ARMISTICE pauses the clock; it frees nobody."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Austria", context="t")
        _set(w, "France", "Austria", "ARMISTICE")
        assert nap.captured_by == "Austria"

    def test_the_rule_is_for_sovereigns_only(self):
        """Control: an ordinary prisoner's W6-7 rule is unchanged — a vassal
        treaty does not send Davout home."""
        w = _boot()
        davout = w.marshals["Davout"]
        w.capture_marshal(davout, "Austria", context="t")
        _set(w, "France", "Austria", "VASSAL")
        assert davout.captured_by == "Austria"


# ════════════════════════════════════════════════════════════════════════
# V7 / V10 — the escort home is on the record, in the right words
# ════════════════════════════════════════════════════════════════════════

class TestTheEscortIsOnTheRecord:
    def _escort(self):
        from backend.game_logic import withdrawal
        w = _boot()
        nap = w.marshals["Napoleon"]
        _set(w, "France", "Prussia", "PEACE")
        nap.location = "Berlin"
        nap.strength = 40000
        nap.road_home_offered = True
        event = _quiet(withdrawal._intern, w, nap, "France")
        return w, nap, event

    def test_the_soil_is_named_by_its_adjective(self):
        """V10: 'Prussian soil', never 'Prussia soil'."""
        _w, _nap, event = self._escort()
        assert event["type"] == "sovereign_escorted_home"
        assert "Prussian soil" in event["message"]
        assert "Prussia soil" not in event["message"]

    def test_the_chronicle_says_his_corps_was_interned(self):
        """V7: the log row reads as an internment, not a restoration."""
        from backend.campaign_log import format_event_oneliner
        w, nap, _event = self._escort()
        row = [e for e in w.event_log if e.get("type") == "marshal_released"][-1]
        line = format_event_oneliner(row)
        assert "INTERNED at Berlin by Prussia" in line
        assert "35,000 men" in line
        assert "restored to France" not in line
        assert nap.road_home_offered is False

    def test_the_briefing_carries_it(self):
        """V7: the tactical event is on the dispatch whitelist, as a warning."""
        from backend.game_logic import dispatch
        assert "sovereign_escorted_home" in dispatch._DISPATCH_EVENT_TYPES

    def test_a_lapsing_warning_is_not_kept_for_a_man_already_home(self):
        """V7: the 'no nearer home … 0 turns' beat is dropped for a marshal
        who is home (the Emperor escorted home in the same advance)."""
        from backend.game_logic import dispatch
        w, nap, _event = self._escort()
        w.log_event({"type": "evacuation_lapsing", "nation": "France",
                     "marshal": "Napoleon", "turns_left": 0,
                     "region": "Berlin", "turn": w.current_turn})
        head = dispatch._build_headline(w, "France", record=False) or {}
        texts = [head.get("text", "")] + [b.get("text", "") for b in
                                           head.get("sub_beats") or []]
        assert not any("no nearer home" in t for t in texts)

    def test_the_other_internment_lines_use_the_adjective_too(self):
        """V10 (the two sibling messages in `_intern`)."""
        from backend.game_logic import withdrawal
        w = _boot()
        _set(w, "France", "Prussia", "PEACE")
        davout = w.marshals["Davout"]
        davout.location = "Berlin"
        event = _quiet(withdrawal._intern, w, davout, "France")
        assert "Prussian soil" in event["message"]


# ════════════════════════════════════════════════════════════════════════
# V11 – V16 — the signature belongs to the courts that signed it
# ════════════════════════════════════════════════════════════════════════

class TestTheSignatories:
    def test_a_satellites_war_does_not_unsign_the_cession(self):
        """V11 (P2): Switzerland (France's satellite) at war with Austria,
        France and Austria at peace — Tyrol stays signed."""
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        _set(w, "Austria", "Switzerland", "PEACE")
        _set(w, "Austria", "Switzerland", "WAR")
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_TREATY
        game_end.reconcile_province_titles(w)
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_TREATY
        assert "Tyrol" in game_end.reconciled_regions(w, "Austria")

    def test_the_signatories_war_does(self):
        """Control: France and Austria at war breaks it."""
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        _set(w, "Austria", "France", "WAR")
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_CONQUEST

    def test_the_settlement_bookkeeping_hop_is_not_a_renewed_war(self):
        """V12 (P2): ARMISTICE→WAR→VASSAL inside one ratification."""
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        _set(w, "France", "Austria", "WAR",
             reason="common_peace_vassalage_ratification")
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_TREATY

    def test_a_reclaim_carries_the_record_home(self):
        """V13 (P2): a grant reclaimed from a rebel stays treaty-titled."""
        from backend.game_logic.vassal import grant_region_to_vassal
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        _set(w, "Austria", "KingdomOfItaly", "PEACE")
        _quiet(grant_region_to_vassal, w, "KingdomOfItaly", "Tyrol", actor="France")
        game_end.reconcile_province_titles(w)
        assert w.province_title["Tyrol"]["holder"] == "KingdomOfItaly"
        # The rebellion: the row gone, the war declared, the grant reclaimed.
        del w.vassals["KingdomOfItaly"]
        _set(w, "France", "KingdomOfItaly", "WAR")
        w.regions["Tyrol"].controller = "France"
        w.invalidate_active_nations_cache()
        assert game_end.province_title_kind(w, "Tyrol", "France") == "treaty"
        game_end.reconcile_province_titles(w)
        rec = w.province_title["Tyrol"]
        assert rec["holder"] == "France" and rec["kind"] == game_end.TITLE_TREATY
        assert "Tyrol" in game_end.reconciled_regions(w, "Austria")

    def test_a_carve_reconciles_only_the_provinces_carved(self):
        """V14 (P2): an unsigned conquest handed to the carved client is
        not a cession."""
        w = _boot()
        _carve_posen(w, also_take=("Silesia",))
        assert w.province_title["Silesia"]["kind"] == game_end.TITLE_CONQUEST
        w.regions["Silesia"].controller = "DuchyOfWarsaw"
        w.invalidate_active_nations_cache()
        game_end.reconcile_province_titles(w)
        reconciled = game_end.reconciled_regions(w, "Prussia")
        assert "Posen" in reconciled
        assert "Silesia" not in reconciled

    def test_a_repudiated_treaty_ends_the_reconciliation(self):
        """V15: `break treaty` without a war unsigns it."""
        from backend.game_logic.diplomacy import break_treaty
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        w.diplomatic_points = 5
        key = w._make_diplo_key("France", "Austria")
        assert key in w.active_treaties
        result = _quiet(break_treaty, key, "France", w)
        assert result["success"] is True
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_CONQUEST
        assert "Tyrol" not in game_end.reconciled_regions(w, "Austria")

    def test_a_released_carve_stays_reconciled(self):
        """V16: the client released in peace — no treaty broken."""
        from backend.game_logic.vassal import release_vassal
        w = _boot()
        _carve_posen(w)
        assert "Posen" in game_end.reconciled_regions(w, "Prussia")
        _quiet(release_vassal, w, "DuchyOfWarsaw")
        assert "DuchyOfWarsaw" not in w.vassals
        assert "Posen" in game_end.reconciled_regions(w, "Prussia")

    def test_the_carve_record_is_a_treaty_record(self):
        w = _boot()
        _carve_posen(w)
        rec = w.province_title["Posen"]
        assert rec["kind"] == game_end.TITLE_TREATY
        assert rec["from"] == "Prussia" and rec["holder"] == "DuchyOfWarsaw"
        assert rec["house"] == "France" and rec.get("carve") is True


# ════════════════════════════════════════════════════════════════════════
# V17 / V25 / V28 — the record paragraph, in one unit
# ════════════════════════════════════════════════════════════════════════

def _home(w, n):
    return [r for r in w.nation_starting_regions["France"] if r != "Paris"][:n]


def _fall_in_chains(w):
    w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
    _tick(w, 10)
    return " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])


class TestTheRecordParagraph:
    def test_courts_are_ranked_over_distinct_provinces(self):
        """V17 (P2): Berry lost three times to Austria, two provinces to
        Britain — Britain took the most."""
        w = _boot()
        berry, artois, rhine = _home(w, 3)
        for _ in range(3):
            w.capture_region(berry, "Austria")
            w.capture_region(berry, "France")
        w.capture_region(berry, "Austria")
        w.capture_region(artois, "Britain")
        w.capture_region(rhine, "Britain")
        text = _fall_in_chains(w)
        assert "3 provinces were lost to the enemy; Britain took the most." in text

    def test_one_province_names_the_court_that_took_it_last(self):
        """V17 (C)."""
        w = _boot()
        berry = _home(w, 1)[0]
        w.capture_region(berry, "Austria")
        w.capture_region(berry, "France")
        w.capture_region(berry, "Britain")
        text = _fall_in_chains(w)
        assert "One province was lost, to Britain." in text

    def test_a_partial_record_counts_the_losses(self):
        """V25: a record kept before the distinct list existed."""
        w = _boot()
        w.campaign_totals = {"provinces_lost": 5, "lost_to": {"Austria": 5}}
        game_end.totals(w)
        w.capture_region(_home(w, 1)[0], "Britain")
        text = _fall_in_chains(w)
        assert "Provinces were lost to the enemy 6 times, most often to Austria." in text
        assert "One province was lost" not in text

    @pytest.mark.parametrize("name,expected", [
        ("Battle of Munich", "The Battle of Munich"),
        ("Second Battle of Swabia", "The Second Battle of Swabia"),
        ("The Great Battle of Swabia", "The Great Battle of Swabia"),
        ("the assault on Vienna", "The assault on Vienna"),
    ])
    def test_a_battle_opens_its_sentence_with_its_article(self, name, expected):
        """V28."""
        assert game_end._battle_subject(name) == expected


# ════════════════════════════════════════════════════════════════════════
# V18 / V19 / V23 — the Verdict's lines and the cause line say what is true
# ════════════════════════════════════════════════════════════════════════

class TestTheLinesSayWhatIsTrue:
    def test_a_fall_is_always_the_eclipse(self):
        """V18 (P2): a larger Empire whose Emperor fell in chains — the
        eclipse, its first line naming the loss that drove it."""
        w = _boot()
        for region in list(w.get_nation_regions("Austria"))[:6]:
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        _fall_in_chains(w)
        verdict = game_end.terminal_ending(w)["summary"]["verdict"]
        assert verdict["tier"] == "eclipse"
        assert "no greater than it began" not in verdict["lines"][0]
        assert "lost its Emperor to his captors" in verdict["lines"][0]

    def test_the_forcing_is_the_fall_not_the_score(self):
        """V18: the same inputs that grade 'ascendant' grade the eclipse
        once the Fall is recorded — never an ascendant funeral."""
        w = _boot()
        inputs = game_end.verdict_inputs(w)
        inputs.update({"provinces_held": inputs["opening_provinces"] * 2,
                       "great_powers_knocked_out": ["Austria", "Prussia"],
                       "emperor": "dead", "fallen": False, "humbled": False})
        assert game_end.verdict_tier(w, dict(inputs))["tier"] != "eclipse"
        inputs["fallen"] = True
        assert game_end.verdict_tier(w, dict(inputs))["tier"] == "eclipse"

    def test_a_contested_reign_without_its_capital(self):
        """V18: 'holds what it held' is never said with Paris lost."""
        w = _boot()
        inputs = game_end.verdict_inputs(w)
        inputs.update({"provinces_held": inputs["opening_provinces"],
                       "capital_held": False, "capital": "Paris"})
        tier = game_end.VERDICT_TIERS[2]
        lines = game_end._tier_lines(w, "contested", tier[3], inputs)
        assert "holds what it held" not in lines[0]
        assert "Paris is in enemy hands" in lines[0]

    def test_an_ascendant_reign_with_its_emperor_in_chains(self):
        w = _boot()
        inputs = game_end.verdict_inputs(w)
        inputs.update({"provinces_held": inputs["opening_provinces"] + 10,
                       "emperor": "captive"})
        tier = game_end.VERDICT_TIERS[1]
        lines = game_end._tier_lines(w, "ascendant", tier[3], inputs)
        assert "surer" not in lines[0]
        assert "its Emperor is a prisoner" in lines[0]

    def test_the_abdication_names_the_province_it_still_holds(self):
        """V19 (P2): never 'with no soil left to govern' while Brittany is
        French."""
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 5)
        record = game_end.terminal_ending(w)
        assert record["cause"] == game_end.CAUSE_SOIL
        text = " ".join(record["summary"]["epilogue"]["paragraphs"])
        assert "with only Brittany left to govern" in text
        assert "no soil left" not in text

    def test_a_clock_that_started_late_claims_no_count_at_war(self):
        """V23: a captive Emperor on a pre-GE-1 save — the clock starts at
        load, it never paused, and '10 of them at war' was false."""
        w = _boot()
        w.current_turn = 3
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        w.current_turn = 12
        w.fall_clock = {}
        _tick(w, 10)
        record = game_end.terminal_ending(w)
        assert record["cause"] == game_end.CAUSE_CHAINS
        assert record["cause_line"] == "The Emperor, a prisoner these 19 turns, is deposed."

    def test_a_truce_that_paused_it_is_still_named(self):
        """V23 control: pauses that account for the difference keep the
        clause."""
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 8)
        _set(w, "France", "Britain", "ARMISTICE")
        _tick(w, 2)
        _set(w, "France", "Britain", "WAR")
        _tick(w, 2)
        record = game_end.terminal_ending(w)
        assert record["cause_line"] == ("The Emperor, a prisoner these 12 turns — "
                                        "10 of them at war with his captor — is deposed.")


# ════════════════════════════════════════════════════════════════════════
# V20 / V21 — the field he was TAKEN on, and the verdict about scale
# ════════════════════════════════════════════════════════════════════════

class TestTheTakenEmperorReport:
    def test_taken_in_his_own_attack(self, client, monkeypatch):
        """V20 (P2): the 85% branch is named on the message, the report and
        the diorama — and his fate replaces the verdict about scale (V21)."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 0)
        nap = _napoleon_alone_at_lorraine(M.world, strength=60)
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert nap.captured_by == "Austria"
        assert "is taken — Austria holds him prisoner" in r["message"]
        report = r.get("battle_report") or {}
        assert report.get("observation") == \
            "The Emperor himself was taken on that field — Austria holds him."
        diorama = r.get("battle_diorama") or {}
        if diorama:
            assert "watched this field" not in diorama.get("observation", "")

    def test_an_ordinary_marshals_capture_is_still_appended(self):
        """Control (the FA-S17-11 ruling): the scale verdict stays for an
        ordinary marshal."""
        from backend.commands.combat_executor import CombatExecutor
        from tests.conftest import MarshalFactory
        soult = MarshalFactory.infantry(name="Soult", location="Belgium", strength=0)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium", nation="Austria",
                                    strength=9000)
        soult.captured_by = "Austria"
        br = {"battle_report": {"observation": "Scarcely an action, Sire."}}
        CombatExecutor._stamp_capture_on_report(br, soult, mack, {"Soult", "Mack"})
        obs = br["battle_report"]["observation"]
        assert obs.startswith("Scarcely an action")
        assert "Soult was taken on that field" in obs


# ════════════════════════════════════════════════════════════════════════
# V22 / V26 / V27 — the goal, the ledger and the dead court
# ════════════════════════════════════════════════════════════════════════

class TestTheOtherWords:
    def test_the_goal_names_the_turn_history_judged(self):
        """V22: a Verdict stamped after the authored turn (a pre-GE-1 save
        loaded late) is named on its own date."""
        from backend.ai.first_contact import answer_first_contact
        w = _boot()
        w.current_turn = 50
        _tick(w, 1)
        verdict = next(r for r in w.endings if r["cause"] == game_end.CAUSE_VERDICT)
        assert verdict["turn"] == 50
        text = answer_first_contact("goal", "how do I win", w)
        assert f"{verdict['calendar_label']} (turn 50)" in text
        assert "(turn 44)" not in text

    def test_the_tier_is_title_cased_properly(self):
        from backend.ai.first_contact import _tier_title_case
        assert _tier_title_case("A REIGN OF TRIUMPH") == "A Reign of Triumph"
        assert _tier_title_case("AN EMPIRE CONTESTED") == "An Empire Contested"
        assert _tier_title_case("THE ECLIPSE") == "The Eclipse"

    def test_no_courts_recover_when_no_europe_is_left(self):
        """V26: the cooldown headline and its gate note are gone the turn
        the last courts fall together."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        w = _boot()
        for region in list(w.regions.values()):
            if (region.controller and region.controller != "France"
                    and region.controller not in w.vassals):
                region.controller = "France"
        w.invalidate_active_nations_cache()
        # The league dissolved with the last of its members: no coalition
        # stands, none brews, the cooldown runs.
        w.active_coalition = None
        w.coalition_brewing = None
        w.coalition_cooldown = 5
        w.threat_level = 100
        boe = build_diplomatic_ledger(w)["balance_of_europe"]
        assert boe["headline_case"] != "COOLDOWN"
        assert "no new coalition gathers" not in str(boe.get("headline_note") or "")

    def test_the_dead_court_keeps_its_article(self):
        """V27."""
        from backend.game_logic.diplomacy import dead_court_refusal
        w = _boot()
        for region in list(w.get_nation_regions("PapalStates")):
            w.regions[region].controller = "France"
        for name in [m.name for m in w.marshals.values() if m.nation == "PapalStates"]:
            del w.marshals[name]
        w.invalidate_active_nations_cache()
        w._build_marshal_index()
        message = dead_court_refusal(w, "PapalStates")
        assert message.startswith("The court of the Papal States no longer exists")
