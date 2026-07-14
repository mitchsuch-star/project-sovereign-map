"""
Combat Overhaul — Phase 5 (Vassals): VS-1 recovery lever + teach it, VS-2 dead-code cleanup.

VS-1: the steady satellite bleed (-2/turn) was HIDDEN behind an abs(delta) >= 3
event gate until it crossed 20 — the player never saw a healthy-band vassal
slipping, nor learned the levers to arrest it. The gate is lowered to >= 2 and a
recovery hint teaches the three arresting actions (invest / garrison / autonomy)
while the vassal is still in the healthy band (>= 40).

VS-2: the "war weariness" contribution read get_coalition_loyalty_penalty for a
lord's own satellite, which is never a coalition member AGAINST its lord, so the
term was always 0. Deleted; loyalty drift is now independent of coalition state.

Exit: a falling vassal can be arrested by a surfaced action.
"""

from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    process_vassal_loyalty, invest_in_vassal, change_vassal_autonomy,
    AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS,
)


def _make_world():
    world = WorldState()
    world.current_turn = 5
    world.player_nation = "France"
    return world


def _add_vassal(world, name="Saxony", loyalty=80, autonomy=AUTONOMY_SATELLITE):
    world.vassals[name] = {"lord": "France", "loyalty": loyalty, "autonomy": autonomy}
    # Zero the lord relation so tests isolate the autonomy-drift mechanic
    # (the default France/Saxony relation of 40 would add +2 via relation//20
    # and mask the -2 satellite bleed under test).
    world.nation_relations[world._make_diplo_key(name, "France")] = 0
    return world.vassals[name]


def _vassal_events(events, name="Saxony"):
    return [e for e in events if e.get("type") == "vassal_loyalty" and e.get("vassal") == name]


# ═══════════════════════════════════════════════════════════════════════════
# VS-1a: the event gate now surfaces the steady satellite bleed
# ═══════════════════════════════════════════════════════════════════════════

class TestVS1EventGate:
    def test_satellite_drift_now_surfaces(self):
        """A bare satellite (drift -2, no garrison) now fires an event that the
        old abs(delta) >= 3 gate would have swallowed."""
        world = _make_world()
        _add_vassal(world, loyalty=80)
        events = _vassal_events(process_vassal_loyalty(world))
        assert len(events) == 1
        assert events[0]["delta"] == -2

    def test_gate_still_ignores_net_zero(self):
        """A garrisoned satellite whose garrison exactly offsets drift produces
        no event (delta 0 < 2) — the gate lowered to 2, not to noise."""
        world = _make_world()
        v = _add_vassal(world, loyalty=80)
        # No garrison wired in a bare world, so force a net-zero via autonomy
        # confidence (+1) vs nothing — instead assert the pure math: an
        # autonomous vassal drifts +1, which is < 2 and must stay silent.
        v["autonomy"] = AUTONOMY_AUTONOMOUS
        events = _vassal_events(process_vassal_loyalty(world))
        assert events == []


# ═══════════════════════════════════════════════════════════════════════════
# VS-1b: the recovery hint teaches the levers in the healthy band
# ═══════════════════════════════════════════════════════════════════════════

class TestVS1RecoveryHint:
    def test_hint_present_when_falling_in_healthy_band(self):
        world = _make_world()
        _add_vassal(world, loyalty=80)
        e = _vassal_events(process_vassal_loyalty(world))[0]
        assert e["recovery_hint"]
        for lever in ("Invest", "garrison", "autonomy"):
            assert lever.lower() in e["recovery_hint"].lower()
        # Folded into the surfaced dispatch message too.
        assert e["recovery_hint"] in e["message"]

    def test_no_hint_when_rising(self):
        """A vassal whose net loyalty is RISING is not 'falling' — no lecture.
        Drive delta positive above the gate with two shared wars (-2 satellite
        + 2×2 common-enemy = +2) and assert the event carries no recovery hint."""
        world = _make_world()
        _add_vassal(world, loyalty=60)
        world.battles_this_turn = []
        world.get_active_nations = lambda: ["France", "Saxony", "Austria", "Russia"]
        for foe in ("Austria", "Russia"):
            fk = world._make_diplo_key("France", foe)
            sk = world._make_diplo_key("Saxony", foe)
            world.diplomatic_states[fk] = "WAR"
            world.diplomatic_states[sk] = "WAR"
        e = _vassal_events(process_vassal_loyalty(world))[0]
        assert e["delta"] > 0
        assert e["recovery_hint"] == ""

    def test_no_hint_below_healthy_band(self):
        """Below 40 the crisis advisories take over; the event fires (drift is
        visible) but carries no healthy-band teaching line."""
        world = _make_world()
        _add_vassal(world, loyalty=30)
        e = _vassal_events(process_vassal_loyalty(world))[0]
        assert e["delta"] == -2
        assert e["recovery_hint"] == ""


# ═══════════════════════════════════════════════════════════════════════════
# VS-2: the dead "war weariness" coalition term is gone
# ═══════════════════════════════════════════════════════════════════════════

class TestVS2DeadCode:
    def test_coalition_membership_no_longer_touches_loyalty(self):
        """A satellite that is (contrived) a coalition member would have taken a
        halved -7 'war weariness' hit under the old code. With VS-2 deleted, its
        drift is pure autonomy (-2)."""
        world = _make_world()
        _add_vassal(world, loyalty=80)
        world.active_coalition = {"members": ["Saxony"], "leader": "Austria"}
        world.war_exhaustion = {"Saxony": 0}
        e = _vassal_events(process_vassal_loyalty(world))[0]
        assert e["delta"] == -2

    def test_reason_never_names_war_weariness(self):
        world = _make_world()
        _add_vassal(world, loyalty=80)
        world.active_coalition = {"members": ["Saxony"], "leader": "Austria"}
        world.war_exhaustion = {"Saxony": 0}
        e = _vassal_events(process_vassal_loyalty(world))[0]
        assert "war weariness" not in e.get("reason", "")
        assert "war weariness" not in e.get("message", "")


# ═══════════════════════════════════════════════════════════════════════════
# Exit criterion: a falling vassal can be arrested by a surfaced action
# ═══════════════════════════════════════════════════════════════════════════

class TestArrestingLevers:
    def test_invest_arrests_the_fall(self):
        world = _make_world()
        _add_vassal(world, loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 1000
        result = invest_in_vassal(world, "Saxony")
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 60  # +10 arrests the slide

    def test_grant_autonomy_reverses_drift(self):
        """Granting autonomy flips the satellite -2 drift to +1: the fall stops
        and reverses without spending gold each turn."""
        world = _make_world()
        _add_vassal(world, loyalty=50, autonomy=AUTONOMY_SATELLITE)
        world.diplomatic_points = 3
        res = change_vassal_autonomy(world, "Saxony", AUTONOMY_AUTONOMOUS)
        assert res["success"]
        before = world.vassals["Saxony"]["loyalty"]
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == before + 1
