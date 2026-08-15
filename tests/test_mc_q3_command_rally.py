"""
MC gate Q3 amendment (July 10, 2026): the command skill is WIRED — "The Rally".

Gate record: docs/MARSHAL_CONTENT_PASS_SPEC.md §4 (Q3 amended at the gate:
wire command now, flatten + hide administration behind the owned MC-2b row).

Mechanic (single source in marshal.py — Golden Rule 1 spirit):
- Command >= 8 (RALLY_FAST_COMMAND): retreat AND broken recovery advance
  2 stages/turn — retreat recovers in 2 turns (not 3), broken in 2 (not 4).
- Command <= 3 (RALLY_POOR_COMMAND): retreat-recovery effectiveness penalties
  run 10pp deeper (-55%/-40%/-25% instead of -45%/-30%/-15%); recovery TIME
  is unchanged. Broken state has no effectiveness channel — poor arm is
  retreat-only by design.
- Command 4-7: byte-identical baseline. The shipped 1805 campaign roster is
  flat-5 (unchanged until MC-2 lands authored skills); the LEGACY
  fixture/rollback roster authors Ney command 8 / Davout 9 / Wellington 9,
  so the fast tier is LIVE in legacy mode — deliberate: they are the
  inspiring-commander tier.
- GR5: the tick site processes ALL marshals — enemy armies rally identically.
- Administration stays unwired: hidden from the marshal card (backend filter
  + Godot list) until MC-2b lands its mechanic.

TestReviewPassSurfaces pins the surfaces a post-implementation adversarial
review found still hardcoding recovery numbers (executor block messages,
voluntary-retreat copy, the shattered-army message, the map tooltip's
tactical_state payload, and the recovered-tick rally-note guard).
"""

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.dispatch import _derive_marshal_status
from backend.game_logic.marshal_overview import build_marshal_overview


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_marshal(name="Ney", location="Belgium", strength=30000, nation="France",
                 personality="aggressive", command=5, **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation, spawn_location=location)
    m.skills["command"] = command
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def make_world(*marshals):
    w = WorldState()
    w.marshals = {m.name: m for m in marshals}
    return w


def tick(world):
    """One recovery tick via the real seam (same path as end-of-turn)."""
    return world._process_tactical_states()


def start_retreat(marshal):
    marshal.retreating = True
    marshal.retreat_recovery = 0


def start_broken(marshal):
    marshal.broken = True
    marshal.broken_recovery = 0


# ═══════════════════════════════════════════════════════
# BASELINE (command 4-7): byte-identical to pre-wiring behavior
# ═══════════════════════════════════════════════════════

class TestBaselineUnchanged:
    def test_default_marshal_boots_command_5(self):
        m = make_marshal()
        assert m.skills["command"] == 5
        assert m.get_rally_stages_per_turn() == 1

    def test_baseline_retreat_recovers_in_three_ticks(self):
        m = make_marshal(command=5)
        start_retreat(m)
        w = make_world(m)
        tick(w)
        assert m.retreat_recovery == 1 and m.retreating
        tick(w)
        assert m.retreat_recovery == 2 and m.retreating
        tick(w)
        assert not m.retreating and m.retreat_recovery == 0

    def test_baseline_broken_recovers_in_four_ticks(self):
        m = make_marshal(command=7)
        start_broken(m)
        w = make_world(m)
        for expected_stage in (1, 2, 3):
            tick(w)
            assert m.broken_recovery == expected_stage and m.broken
        tick(w)
        assert not m.broken and m.broken_recovery == 0

    def test_baseline_penalties_unchanged(self):
        m = make_marshal(command=5)
        assert m.get_retreat_stage_penalty(0) == 0.45
        assert m.get_retreat_stage_penalty(1) == 0.30
        assert m.get_retreat_stage_penalty(2) == 0.15
        assert m.get_retreat_stage_penalty(3) == 0.0

    def test_baseline_recovery_message_format_unchanged(self):
        m = make_marshal(command=5)
        start_retreat(m)
        w = make_world(m)
        events = [e for e in tick(w) if e.get("type") == "retreat_recovery"]
        assert len(events) == 1
        assert events[0]["penalty"] == "-30%"
        # CA9-N37 (pin re-blessed): the sentence gained its terminator.
        # Without it the rally note ran straight on — "penalty: -40% The
        # rout's disorder lingers" — and the bare arm ended mid-air. The
        # MC-Q3 claim this pins (a command-5 marshal's baseline penalty
        # string) is unchanged.
        assert events[0]["message"] == (
            f"{m.name}'s army is recovering. Effectiveness penalty: -30%.")

    def test_command_4_gets_normal_penalties(self):
        """Boundary: the poor arm starts at <= 3, not 4."""
        m = make_marshal(command=4)
        assert m.get_retreat_stage_penalty(0) == 0.45

    def test_command_7_gets_normal_speed(self):
        """Boundary: the fast arm starts at >= 8, not 7."""
        m = make_marshal(command=7)
        assert m.get_rally_stages_per_turn() == 1


# ═══════════════════════════════════════════════════════
# THE RALLY (command >= 8): recovery twice as fast
# ═══════════════════════════════════════════════════════

class TestFastRally:
    def test_command_8_is_the_fast_threshold(self):
        assert make_marshal(command=8).get_rally_stages_per_turn() == 2
        assert make_marshal(command=9).get_rally_stages_per_turn() == 2

    def test_fast_retreat_recovers_in_two_ticks(self):
        m = make_marshal(name="Davout", personality="cautious", command=9)
        start_retreat(m)
        w = make_world(m)
        tick(w)
        assert m.retreat_recovery == 2 and m.retreating
        tick(w)
        assert not m.retreating and m.retreat_recovery == 0

    def test_fast_broken_recovers_in_two_ticks(self):
        m = make_marshal(name="Davout", personality="cautious", command=9)
        start_broken(m)
        w = make_world(m)
        tick(w)
        assert m.broken_recovery == 2 and m.broken
        tick(w)
        assert not m.broken and m.broken_recovery == 0

    def test_fast_rally_stage_never_overshoots(self):
        """From stage 2, a 2-stage advance clamps at the recovered threshold."""
        m = make_marshal(command=9)
        m.retreating = True
        m.retreat_recovery = 2
        w = make_world(m)
        tick(w)
        assert not m.retreating and m.retreat_recovery == 0

    def test_fast_rally_message_carries_the_note(self):
        m = make_marshal(name="Davout", command=9)
        start_retreat(m)
        w = make_world(m)
        events = [e for e in tick(w) if e.get("type") == "retreat_recovery"]
        assert len(events) == 1
        assert events[0]["penalty"] == "-15%"  # jumped 0 -> 2
        assert "rallies the survivors" in events[0]["message"]

    def test_fast_broken_message_carries_the_note(self):
        m = make_marshal(name="Davout", command=9)
        start_broken(m)
        w = make_world(m)
        events = [e for e in tick(w) if e.get("type") == "broken_recovery"]
        assert len(events) == 1
        assert events[0]["turns_left"] == 1  # ceil((4-2)/2)
        assert "ahead of schedule" in events[0]["message"]

    def test_gr5_enemy_marshal_rallies_identically(self):
        """Golden Rule 5: an enemy-nation high-command marshal uses the SAME
        tick — Archduke Charles rallies exactly like Davout would."""
        m = make_marshal(name="Archduke Charles", nation="Austria",
                         personality="cautious", command=8)
        start_retreat(m)
        w = make_world(m)
        tick(w)
        tick(w)
        assert not m.retreating


# ═══════════════════════════════════════════════════════
# POOR RALLY (command <= 3): deeper penalties, same duration
# ═══════════════════════════════════════════════════════

class TestPoorRally:
    def test_poor_penalties_run_10pp_deeper(self):
        m = make_marshal(name="Mack", nation="Austria", command=3)
        assert abs(m.get_retreat_stage_penalty(0) - 0.55) < 1e-9
        assert abs(m.get_retreat_stage_penalty(1) - 0.40) < 1e-9
        assert abs(m.get_retreat_stage_penalty(2) - 0.25) < 1e-9

    def test_poor_recovered_stage_has_no_penalty(self):
        """The deepening only applies to penalized stages — never to 3+."""
        m = make_marshal(command=2)
        assert m.get_retreat_stage_penalty(3) == 0.0

    def test_poor_combat_effectiveness_is_lower(self):
        base = make_marshal(name="A", command=5, morale=50)
        poor = make_marshal(name="B", command=3, morale=50)
        for m in (base, poor):
            m.retreating = True
            m.retreat_recovery = 0
        # base_eff 1.0: base -> 0.55, poor -> 0.45
        assert abs(base.get_combat_effectiveness() - 0.55) < 1e-9
        assert abs(poor.get_combat_effectiveness() - 0.45) < 1e-9

    def test_poor_recovery_time_unchanged(self):
        """Low command deepens the penalty; it never slows the clock."""
        m = make_marshal(name="Mack", command=3)
        start_retreat(m)
        w = make_world(m)
        tick(w)
        tick(w)
        assert m.retreating
        tick(w)
        assert not m.retreating

    def test_poor_message_shows_the_deeper_number_and_note(self):
        """The percentage shown IS the percentage applied (single source)."""
        m = make_marshal(name="Mack", command=3)
        start_retreat(m)
        w = make_world(m)
        events = [e for e in tick(w) if e.get("type") == "retreat_recovery"]
        assert events[0]["penalty"] == "-40%"  # stage 1, deepened
        assert "disorder lingers" in events[0]["message"]


# ═══════════════════════════════════════════════════════
# PLAYER-FACING SURFACES: dispatch ETA + card payload
# ═══════════════════════════════════════════════════════

class TestSurfaces:
    def test_dispatch_eta_baseline_retreat(self):
        m = make_marshal(command=5)
        start_retreat(m)
        w = make_world(m)
        status, note = _derive_marshal_status(m, w)
        assert status == "retreating"
        assert note == f"Recovers T{int(w.current_turn) + 3}."

    def test_dispatch_eta_fast_rally_retreat(self):
        m = make_marshal(command=9)
        start_retreat(m)
        w = make_world(m)
        status, note = _derive_marshal_status(m, w)
        assert status == "retreating"
        assert note == f"Recovers T{int(w.current_turn) + 2}."

    def test_dispatch_eta_fast_rally_broken(self):
        m = make_marshal(command=9)
        start_broken(m)
        w = make_world(m)
        status, note = _derive_marshal_status(m, w)
        assert status == "broken"
        assert note == f"Reforms T{int(w.current_turn) + 2}."

    def test_dispatch_eta_baseline_broken(self):
        m = make_marshal(command=5)
        start_broken(m)
        w = make_world(m)
        status, note = _derive_marshal_status(m, w)
        assert status == "broken"
        assert note == f"Reforms T{int(w.current_turn) + 4}."

    def test_card_hides_administration_where_mechanic_not_live(self):
        """MC-2b display contract (extends the Q3 hide test): administration
        is wired Europe-only (The Intendance), so the card shows the row
        exactly where the mechanic is live. A non-Europe world (the legacy
        rollback fixture) keeps the pre-MC-2b hidden state — GR9: no
        advertised stat that does nothing."""
        m = make_marshal()
        w = make_world(m)
        w.player_nation = "France"
        cards = build_marshal_overview(w)
        assert len(cards) == 1
        skills = cards[0]["skills"]
        assert "administration" not in skills
        assert "command" in skills
        assert set(skills) == {"tactical", "shock", "defense",
                               "logistics", "command"}
        assert cards[0]["admin_note"] == ""
        assert "administration" not in cards[0]["skill_notes"]

    def test_card_displays_administration_on_europe(self):
        """MC-2b: the row is RESTORED where The Intendance prices recruits."""
        m = make_marshal()
        w = make_world(m)
        w.player_nation = "France"
        w.sovereign_map = "europe"
        cards = build_marshal_overview(w)
        assert len(cards) == 1
        skills = cards[0]["skills"]
        assert set(skills) == {"tactical", "shock", "defense",
                               "logistics", "administration", "command"}
        assert "administration" in cards[0]["skill_notes"]

    def test_administration_still_serializes(self):
        """The reserved value survives save/load untouched (MC-2b data)."""
        m = make_marshal()
        m.skills["administration"] = 7
        restored = Marshal.from_dict(m.to_dict())
        assert restored.skills["administration"] == 7


# ═══════════════════════════════════════════════════════
# REVIEW-PASS SURFACES: every remaining hardcoded recovery number
# ═══════════════════════════════════════════════════════

class TestReviewPassSurfaces:
    def _blocked_message(self, marshal):
        """Order a recovering marshal to fortify; return the block message."""
        w = WorldState()
        w.marshals[marshal.name] = marshal
        result = CommandExecutor().execute(
            {"command": {"marshal": marshal.name, "action": "fortify"}},
            {"world": w})
        assert not result["success"]
        return result["message"]

    def test_executor_retreat_block_counts_down_command_aware(self):
        m = make_marshal(name="Blocked A", command=5)
        m.retreating = True
        m.retreat_recovery = 0
        assert "Recovery: 3 turn(s) remaining" in self._blocked_message(m)
        m2 = make_marshal(name="Blocked B", command=5)
        m2.retreating = True
        m2.retreat_recovery = 2
        # Pre-fix this surface read a phantom constant-3 attribute
        assert "Recovery: 1 turn(s) remaining" in self._blocked_message(m2)
        m3 = make_marshal(name="Blocked C", command=9)
        m3.retreating = True
        m3.retreat_recovery = 0
        assert "Recovery: 2 turn(s) remaining" in self._blocked_message(m3)

    def test_executor_broken_block_command_aware(self):
        m = make_marshal(name="Broken A", command=9)
        m.broken = True
        m.broken_recovery = 0
        assert "Recovery: 2 turn(s) remaining" in self._blocked_message(m)
        m2 = make_marshal(name="Broken B", command=5)
        m2.broken = True
        m2.broken_recovery = 0
        assert "Recovery: 4 turn(s) remaining" in self._blocked_message(m2)

    def test_forced_retreat_flee_message_command_aware(self):
        """The '(recovering for N turns)' figure tracks rally speed."""
        executor = CommandExecutor()
        for command, expected in ((5, "recovering for 3 turns"),
                                  (9, "recovering for 2 turns")):
            m = make_marshal(name=f"Flee {command}", location="Paris",
                             command=command)
            enemy = make_marshal(name=f"Foe {command}", location="Paris",
                                 nation="Britain")
            w = WorldState()
            w.marshals = {m.name: m, enemy.name: enemy}
            msg = executor._combat._apply_forced_retreat_or_break(
                m, enemy, w, skip_fate=True)
            assert expected in msg, msg

    def test_shattered_message_command_aware(self):
        """The surrounded/shattered arm of the SAME function agrees."""
        executor = CommandExecutor()
        for command, expected in ((5, "recruit for 4 turns"),
                                  (9, "recruit for 2 turns")):
            m = make_marshal(name=f"Shattered {command}", location="Paris",
                             command=command)
            enemy = make_marshal(name=f"Trap {command}", location="Paris",
                                 nation="Britain")
            w = WorldState()
            w.marshals = {m.name: m, enemy.name: enemy}
            w.get_safe_retreat_destination = lambda *a, **k: None  # surrounded
            msg = executor._combat._apply_forced_retreat_or_break(
                m, enemy, w, skip_fate=True)
            assert expected in msg, msg

    def test_voluntary_retreat_message_command_aware(self):
        """'Will recover over N turns' + the stage-0 penalty display track
        command (poor arm shows the deepened -55%)."""
        for command, penalty, turns in ((5, "-45%", "3"), (3, "-55%", "3"),
                                        (9, "-45%", "2")):
            # Literal personality: never objects (W6-5 doctrine), so the
            # retreat executes and the message is reachable deterministically
            m = make_marshal(name=f"Voluntary {command}", location="Paris",
                             personality="literal", command=command)
            enemy = make_marshal(name=f"Threat {command}", location="Paris",
                                 nation="Britain")
            w = WorldState()
            w.marshals = {m.name: m, enemy.name: enemy}
            w.diplomatic_states[w._make_diplo_key("France", "Britain")] = "WAR"
            result = CommandExecutor().execute(
                {"command": {"marshal": m.name, "action": "retreat"}},
                {"world": w})
            assert result["success"], result.get("message")
            assert f"Will recover over {turns} turns." in result["message"]
            assert penalty in result["message"]

    def test_map_tooltip_payload_command_aware(self):
        """The tactical_state payload carries derived display values so the
        Godot tooltip never renders a hardcoded table (GR2: int turns)."""
        m = make_marshal(name="Tooltip", location="Paris", command=9)
        m.retreating = True
        m.retreat_recovery = 0
        m.broken = True
        m.broken_recovery = 0
        poor = make_marshal(name="Tooltip Poor", location="Paris", command=3)
        poor.retreating = True
        poor.retreat_recovery = 0
        w = WorldState()
        w.marshals = {m.name: m, poor.name: poor}
        summary = w.get_game_state_summary()
        states = {}
        for region_data in summary["map_data"].values():
            for md in region_data.get("marshals", []):
                if "tactical_state" in md:
                    states[md["name"]] = md["tactical_state"]
        assert states["Tooltip"]["retreat_penalty"] == "-45%"
        assert states["Tooltip"]["broken_turns_left"] == 2
        assert isinstance(states["Tooltip"]["broken_turns_left"], int)
        assert states["Tooltip Poor"]["retreat_penalty"] == "-55%"

    def test_no_recovering_line_on_the_recovered_tick(self):
        """PC15-14 (flipped consciously from the old '0% (recovered)'
        pin): when recovery COMPLETES this tick there is NO 'recovering…
        penalty: 0%' non-event at all — the `retreat_recovered` completion
        event alone carries the news. The rally-note guard this pin
        originally held is subsumed: no recovering line, no note."""
        m = make_marshal(name="Guard", command=9)
        m.retreating = True
        m.retreat_recovery = 2
        w = make_world(m)
        events = tick(w)
        recovering = [e for e in events
                      if e.get("type") == "retreat_recovery"]
        recovered = [e for e in events
                     if e.get("type") == "retreat_recovered"]
        assert recovering == [], (
            "the 0% 'recovering' non-event returned (PC15-14)")
        assert len(recovered) == 1
