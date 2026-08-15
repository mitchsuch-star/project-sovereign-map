"""NP-4 — The Peril: the Eagle in Chains (NAPOLEON_SPEC.md §7, gate §14.1
Q2 RULED capture-only, the Brétigny frame).

A sovereign never dies in v1. The ONE removal seam (destroy_marshal,
PC15-1) converts him to capture; the fate machinery never rolls his coin —
the Guard buys every non-encircled escape at GUARD_ESCAPE_TOLL, and only
true encirclement takes him (through the last-stand interrupt, his own
copy). Capture = authority −40 (both sides, GR5) + the LIVE-derived
Captive Eagle ±15 war-score component + the sovereign ransom (5,000g) +
the suggested-terms Brétigny stage. Three roads home: peace (mutual
release), the priced clause, and military rescue — which the survey proved
did NOT exist and this slice builds (sovereign-scoped, dormancy-safe).
"""

import random as _random

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.game_logic import gazette
from backend.game_logic.diplomacy import (
    CAPTIVE_EAGLE_SCORE,
    SOVEREIGN_RANSOM,
    calculate_side_war_score,
    calculate_war_score,
)
from backend.game_logic.diplomatic_templates import generate_suggested_terms
from backend.game_logic.dispatch import (
    HEADLINE_WEIGHTS,
    _HEADLINE_BERTHIER_NOTES,
    _HEADLINE_TEMPLATES,
)
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                spawn_location=location)
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def make_sovereign(name="Napoleon", nation="France", location="Belgium",
                   strength=10000, **kw):
    return make_marshal(name, location=location, strength=strength,
                        nation=nation, personality="sovereign", **kw)


def make_world(*marshals, wars=(("France", "Austria"),)):
    w = WorldState()
    w.marshals = {m.name: m for m in marshals}
    for a, b in wars:
        key = w._make_diplo_key(a, b)
        w.diplomatic_states[key] = "WAR"
    return w


def CE():
    return CommandExecutor()._combat


# ════════════════════════════════════════════════════════════════════════
# The death guard at the ONE removal seam (§7.1)
# ════════════════════════════════════════════════════════════════════════

class TestDeathGuard:
    def test_destroy_converts_to_capture(self):
        s = make_sovereign()
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, e)
        removed = w.destroy_marshal(s, cause="battle", victor="Austria")
        assert removed is False
        assert "Napoleon" in w.marshals
        assert s.captured_by == "Austria"
        assert "Napoleon" not in w.fallen_marshals

    def test_no_victor_falls_back_to_strongest_at_war(self):
        s = make_sovereign()
        e1 = make_marshal("Mack", nation="Austria", strength=20000)
        e2 = make_marshal("Kutuzov", nation="Russia", strength=50000)
        w = make_world(s, e1, e2, wars=(("France", "Austria"),
                                        ("France", "Russia")))
        w.destroy_marshal(s, cause="attrition")
        assert s.captured_by == "Russia"

    def test_prisoner_still_never_destroyed(self):
        s = make_sovereign(captured_by="Austria", strength=0)
        w = make_world(s)
        assert w.destroy_marshal(s, cause="battle") is False
        assert "Napoleon" in w.marshals

    def test_control_ordinary_marshal_still_dies(self):
        m = make_marshal("Ney", personality="aggressive")
        w = make_world(m)
        assert w.destroy_marshal(m, cause="battle", victor="Austria") is True
        assert "Ney" not in w.marshals
        assert "Ney" in w.fallen_marshals

    def test_elimination_keeps_a_sovereign_prisoner(self):
        # A crowned prisoner of a dying court is not swept with its army.
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                captured_by="France", strength=0,
                                location="Paris")
        mack = make_marshal("Mack", nation="Austria")
        w = make_world(kaiser, mack)
        w._eliminate_nation("Austria")
        assert "Kaiser" in w.marshals
        assert "Mack" not in w.marshals

    def test_elimination_converts_a_standing_sovereign(self):
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                location="Bavaria")
        w = make_world(kaiser)
        # Production precondition: elimination fires at ZERO regions —
        # strip Austria's soil first (the raw fixture map still gave it
        # Bavaria/Vienna/Bohemia, which made the teardown's WAR->PEACE
        # release the fresh prisoner to a court that still "existed").
        for region in w.regions.values():
            if region.controller == "Austria":
                region.controller = "France"
        w.invalidate_active_nations_cache()
        w._eliminate_nation("Austria")
        # Converted to capture by the death guard — and neither the
        # prisoner-sweep fallback nor the teardown's mutual release may
        # undo it (a crown without a court stays his captor's guest).
        assert "Kaiser" in w.marshals
        assert kaiser.captured_by == "France"


# ════════════════════════════════════════════════════════════════════════
# The Guard buys the road (§7.0, N15)
# ════════════════════════════════════════════════════════════════════════

class TestGuardEscape:
    def test_cornered_sovereign_never_rolls_the_coin(self, monkeypatch):
        # Even a rigged always-capture coin cannot take him when a road
        # exists — the Guard buys it at 30%.
        monkeypatch.setattr(_random, "random", lambda: 0.99)
        s = make_sovereign(strength=4000)
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, e)
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: "Paris")
        ce = CE()
        result = ce._check_marshal_fate(s, e, w)
        assert result is None  # the normal retreat proceeds
        assert s.captured_by == ""
        assert s.strength == 4000 - int(4000 * ce.GUARD_ESCAPE_TOLL)
        assert "Guard bought the road" in s._sovereign_toll_note

    def test_toll_note_reaches_the_retreat_message(self, monkeypatch):
        monkeypatch.setattr(_random, "random", lambda: 0.99)
        s = make_sovereign(strength=4000)
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, e)
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: "Paris")
        msg = CE()._apply_forced_retreat_or_break(s, e, w)
        assert "Guard bought the road" in msg
        assert s._sovereign_toll_note == ""  # read once, then cleared

    def test_control_marshal_still_rolls(self, monkeypatch):
        monkeypatch.setattr(_random, "random", lambda: 0.99)  # > 0.60
        m = make_marshal("Ney", personality="cautious", strength=4000)
        e = make_marshal("Mack", nation="Austria")
        w = make_world(m, e)
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: "Paris")
        CE()._check_marshal_fate(m, e, w)
        assert m.captured_by == "Austria"

    def test_encircled_player_sovereign_gets_the_interrupt(self, monkeypatch):
        s = make_sovereign(strength=8000)
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, e)
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: None)
        msg = CE()._check_marshal_fate(s, e, w)
        assert "ENCIRCLED" in msg
        pending = s.pending_interrupt
        assert pending["interrupt_type"] == "last_stand"
        assert pending["sovereign"] is True
        assert "does not surrender" in pending["message"]
        assert s.captured_by == ""  # awaiting the word

    def test_encircled_ai_sovereign_fights_and_is_taken(self, monkeypatch):
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                location="Bavaria", strength=8000)
        e = make_marshal("Ney", personality="aggressive", location="Bavaria")
        w = make_world(kaiser, e)
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: None)
        start = e.strength
        msg = CE()._check_marshal_fate(kaiser, e, w)
        assert "LAST STAND" in msg
        assert kaiser.captured_by == "France"
        assert e.strength < start  # he bled them first

    def test_breakout_success_still_burns_the_toll(self, monkeypatch):
        s = make_sovereign(strength=8000)
        e = make_marshal("Mack", nation="Austria")
        w = make_world(s, e)
        s.pending_interrupt = {
            "interrupt_type": "last_stand", "marshal": "Napoleon",
            "enemy": "Mack", "enemy_nation": "Austria", "sovereign": True,
            "options": ["fight_to_the_last", "attempt_breakout"],
        }
        monkeypatch.setattr(_random, "random", lambda: 0.0)  # success
        monkeypatch.setattr(w, "get_safe_retreat_destination",
                            lambda *a, **k: "Paris")
        proc = StrategicOrderProcessor(CommandExecutor())
        result = proc.handle_response("Napoleon", "last_stand",
                                      "attempt_breakout", w, {"world": w})
        assert result["success"] is True
        assert "Guard bought the road" in result["message"]
        assert s.strength < 8000
        assert s.captured_by == ""

    def test_fight_to_the_last_ends_in_the_cell(self):
        s = make_sovereign(strength=8000)
        e = make_marshal("Mack", nation="Austria", strength=40000)
        w = make_world(s, e)
        s.pending_interrupt = {
            "interrupt_type": "last_stand", "marshal": "Napoleon",
            "enemy": "Mack", "enemy_nation": "Austria", "sovereign": True,
            "options": ["fight_to_the_last", "attempt_breakout"],
        }
        proc = StrategicOrderProcessor(CommandExecutor())
        result = proc.handle_response("Napoleon", "last_stand",
                                      "fight_to_the_last", w, {"world": w})
        assert result["success"] is True
        assert s.captured_by == "Austria"


# ════════════════════════════════════════════════════════════════════════
# The consequences (§7.2, N8/N9)
# ════════════════════════════════════════════════════════════════════════

class TestCaptureConsequences:
    def test_player_sovereign_capture_shocks_authority(self):
        s = make_sovereign()
        w = make_world(s)
        start = w.authority_tracker.authority
        w.capture_marshal(s, "Austria", context="test")
        assert w.authority_tracker.authority == max(
            0, start - w.SOVEREIGN_CAPTURE_AUTHORITY_SHOCK)

    def test_enemy_sovereign_capture_shocks_their_authority(self):
        kaiser = make_sovereign("Kaiser", nation="Austria")
        w = make_world(kaiser)
        w.nation_authority["Austria"] = 75
        w.capture_marshal(kaiser, "France", context="test")
        assert w.nation_authority["Austria"] == 35

    def test_capture_event_carries_the_sovereign_key(self):
        s = make_sovereign()
        w = make_world(s)
        w.capture_marshal(s, "Austria", context="test")
        event = [e for e in w.event_log
                 if e.get("type") == "marshal_captured"][-1]
        assert event["sovereign"] is True

    def test_ordinary_capture_is_not_sovereign(self):
        m = make_marshal("Ney", personality="aggressive")
        w = make_world(m)
        start = w.authority_tracker.authority
        w.capture_marshal(m, "Austria", context="test")
        event = [e for e in w.event_log
                 if e.get("type") == "marshal_captured"][-1]
        assert event["sovereign"] is False
        assert w.authority_tracker.authority == start

    def test_captive_eagle_component(self):
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        w = make_world(s)
        comp = calculate_war_score("Austria", "France", w,
                                   return_components=True)
        assert comp["captive"] == CAPTIVE_EAGLE_SCORE
        mirror = calculate_war_score("France", "Austria", w,
                                     return_components=True)
        assert mirror["captive"] == -CAPTIVE_EAGLE_SCORE
        side = calculate_side_war_score("Austria", ["France"], w,
                                        return_components=True)
        assert side["captive"] == CAPTIVE_EAGLE_SCORE

    def test_release_clears_the_component_live(self):
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        w = make_world(s)
        w.release_captured_marshal("Napoleon", reason="peace_treaty")
        comp = calculate_war_score("Austria", "France", w,
                                   return_components=True)
        assert comp["captive"] == 0

    def test_sovereign_ransom_constant(self):
        assert SOVEREIGN_RANSOM == 5000

    def test_dispatch_class_outranks_home_captured(self):
        assert HEADLINE_WEIGHTS["sovereign_captured"] > \
            HEADLINE_WEIGHTS["home_captured"]
        assert "sovereign_captured" in _HEADLINE_TEMPLATES
        assert "sovereign_captured" in _HEADLINE_BERTHIER_NOTES

    def test_gazette_special_editions(self):
        s = make_sovereign()
        w = make_world(s)
        taken = {"type": "marshal_captured", "nation": "France",
                 "captor": "Austria", "sovereign": True}
        assert gazette._special_reason(w, [taken]) == "THE EMPEROR TAKEN"
        crowned = {"type": "marshal_captured", "nation": "Austria",
                   "captor": "France", "sovereign": True}
        assert gazette._special_reason(w, [crowned]) == "a crowned head taken"
        plain = {"type": "marshal_captured", "nation": "France",
                 "captor": "Austria", "sovereign": False}
        assert gazette._special_reason(
            w, [plain]) == "a marshal of France lost"


# ════════════════════════════════════════════════════════════════════════
# The Brétigny stage — captivity is peace leverage (§7.2)
# ════════════════════════════════════════════════════════════════════════

class TestBretignyTerms:
    def test_their_draft_leads_with_our_emperor(self):
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        e = make_marshal("Mack", nation="Austria", location="Bavaria")
        w = make_world(s, e)
        terms = generate_suggested_terms("Austria", "peace", w)
        demands = terms.get("demands", [])
        assert demands and demands[0]["type"] == "prisoner_return"
        assert demands[0]["marshal"] == "Napoleon"

    def test_our_draft_leads_with_their_kaiser(self):
        kaiser = make_sovereign("Kaiser", nation="Austria",
                                captured_by="France", strength=0,
                                location="Paris")
        e = make_marshal("Mack", nation="Austria", location="Bavaria")
        w = make_world(kaiser, e)
        terms = generate_suggested_terms("Austria", "peace", w)
        sweeteners = terms.get("sweeteners", [])
        assert sweeteners and sweeteners[0]["type"] == "prisoner_return"
        assert sweeteners[0]["marshal"] == "Kaiser"

    def test_no_captive_no_clause(self):
        e = make_marshal("Mack", nation="Austria", location="Bavaria")
        w = make_world(e)
        terms = generate_suggested_terms("Austria", "peace", w)
        for bucket in ("demands", "sweeteners"):
            assert not any(t.get("type") == "prisoner_return"
                           for t in terms.get(bucket, []))


# ════════════════════════════════════════════════════════════════════════
# The three roads home (§7.3)
# ════════════════════════════════════════════════════════════════════════

class TestRoadsHome:
    def test_peace_frees_him(self):
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        w = make_world(s)
        released = w.release_mutual_prisoners("France", "Austria")
        assert "Napoleon" in released
        assert s.captured_by == ""
        assert s.strength == w.RANSOM_RETURN_STRENGTH
        assert s.morale == 50

    def test_rescue_by_storming_the_cell(self):
        # NP-4 BUILT this road — the spec's "may already work" was false.
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        w = make_world(s)
        region = w.regions.get("Bavaria")
        if region is None:
            pytest.skip("fixture world lacks Bavaria")
        region.controller = "Austria"
        w.capture_region("Bavaria", "France")
        assert s.captured_by == ""
        assert s.strength == w.RANSOM_RETURN_STRENGTH

    def test_storm_by_a_third_party_frees_nothing(self):
        s = make_sovereign(captured_by="Austria", strength=0,
                           location="Bavaria")
        w = make_world(s, wars=(("France", "Austria"),
                                ("Russia", "Austria")))
        region = w.regions.get("Bavaria")
        if region is None:
            pytest.skip("fixture world lacks Bavaria")
        region.controller = "Austria"
        w.capture_region("Bavaria", "Russia")
        assert s.captured_by == "Austria"  # Russia keeps no French Emperor

    def test_authority_does_not_snap_back_on_release(self):
        s = make_sovereign()
        w = make_world(s)
        w.capture_marshal(s, "Austria", context="test")
        shocked = w.authority_tracker.authority
        w.release_captured_marshal("Napoleon", reason="ransom")
        assert w.authority_tracker.authority == shocked
