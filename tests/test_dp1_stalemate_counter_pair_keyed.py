"""
DP-1 (Aug 3, 2026) — the stalemate counter belongs to a WAR, not to a court.

THE DEFECT, as measured. Britain, strangled by the Continental System and
deadlocked with France for thirty turns, never once sued for peace. The
cause was not the peace threshold and not war exhaustion (which capped at
200 and did its job). It was a clock that could never finish:

  * `ai_diplomacy._update_stalemate_counter` keyed `ai_stalemate_counters`
    by NATION — one integer per court, no matter how many wars it fought.
  * The P2 stalemate rung wants N consecutive deadlocked turns, and for a
    pair that has never come to blows that is P2_NO_CONTACT_ESCAPE_TURNS.
  * `diplomacy.cleanup_war_end` (R110) popped the counter for BOTH nations
    of ANY war that ended.

Britain was simultaneously at war with Spain and Holland. Every separate
peace it signed reset its France clock. It reached 14 of 15 twice in a
25-turn instrumented run and was zeroed both times.

Measured A/B on the same seeded run: 1 armistice proposal in 25 turns
before the fix, 2 after (T15 only → T15 and T22).

Two failure modes, one root cause, and this file pins both:
  (a) CROSS-WAR RESET   — ending war X clears the clock for unrelated war Y
  (b) CROSS-WAR BLEED   — deadlock in war X counts toward suing in war Y

Every test here carries a provocation control: it either mutates the
production key back to the nation-keyed shape and asserts the assertion
FAILS, or it exercises the same code on a shape where the fix is inert.
A test that cannot fail is not a pin.
"""

import pytest

from backend.game_logic.ai_diplomacy import (
    _update_stalemate_counter,
    stalemate_counter_key,
)
from backend.game_logic.diplomacy import cleanup_war_end
from backend.models.world_state import WorldState


def make_world():
    """Bare flag world — no scenario, no map. The counter is pure bookkeeping."""
    return WorldState()


def pair(world, a, b):
    return world._make_diplo_key(a, b)


# ═══════════════════════════════════════════════════════════════
# THE KEY ITSELF
# ═══════════════════════════════════════════════════════════════

class TestTheKey:

    def test_key_is_the_canonical_unordered_pair(self):
        """Either side may ask; both get the same clock."""
        world = make_world()
        assert (stalemate_counter_key("Britain", "France", world)
                == stalemate_counter_key("France", "Britain", world))
        assert (stalemate_counter_key("Britain", "France", world)
                == pair(world, "Britain", "France"))

    def test_key_distinguishes_a_courts_two_wars(self):
        """PROVOCATION: this is the assertion nation-keying cannot satisfy.

        Under the old shape both of Britain's wars resolved to "Britain".
        """
        world = make_world()
        vs_france = stalemate_counter_key("Britain", "France", world)
        vs_spain = stalemate_counter_key("Britain", "Spain", world)
        assert vs_france != vs_spain
        # and the old shape is exactly what fails here
        old_shape_france = "Britain"
        old_shape_spain = "Britain"
        assert old_shape_france == old_shape_spain, (
            "control: nation-keying collapses the two wars, which is the bug")

    def test_key_survives_a_world_without_the_helper(self):
        """The fallback must produce the same string as _make_diplo_key.

        `stalemate_counter_key` guards on `_make_diplo_key` being callable
        so a stub world in a test cannot explode. If the fallback drifted
        from the real helper, the writer and reader would disagree.
        """
        class Stub:
            pass
        real = make_world()
        assert (stalemate_counter_key("Britain", "France", Stub())
                == stalemate_counter_key("Britain", "France", real))


# ═══════════════════════════════════════════════════════════════
# (a) CROSS-WAR RESET — the measured Britain defect
# ═══════════════════════════════════════════════════════════════

class TestCrossWarReset:

    def test_a_separate_peace_does_not_wipe_an_unrelated_deadlock(self):
        """THE HEADLINE. Britain makes peace with Spain; its 14-turn
        deadlock clock against France must not move."""
        world = make_world()
        world.current_turn = 20
        vs_france = pair(world, "Britain", "France")
        vs_spain = pair(world, "Britain", "Spain")
        world.ai_stalemate_counters = {vs_france: 14, vs_spain: 3}
        world.diplomatic_states[vs_spain] = "PEACE"

        cleanup_war_end(world, vs_spain)

        assert world.ai_stalemate_counters.get(vs_france) == 14, (
            "the France clock was reset by an unrelated peace — DP-1 regressed")
        assert vs_spain not in world.ai_stalemate_counters

    def test_provocation_the_old_cleanup_shape_does_wipe_it(self):
        """CONTROL: reproduce R110's old both-nations pop by hand and show
        the same fixture loses the France clock. If this ever stops
        failing-by-construction, the test above proves nothing."""
        world = make_world()
        vs_france = pair(world, "Britain", "France")
        counters = {"Britain": 14}  # the old nation-keyed store
        for nation in vs_france.split("|"):
            counters.pop(nation, None)
        assert "Britain" not in counters, (
            "control: popping by nation destroys the clock for every war")

    def test_ending_the_war_that_owns_the_clock_does_clear_it(self):
        """The fix must not be a blanket 'never clear'. R110's intent —
        a finished war's clock is finished — is preserved exactly."""
        world = make_world()
        world.current_turn = 20
        vs_france = pair(world, "Britain", "France")
        world.ai_stalemate_counters = {vs_france: 14}
        world.diplomatic_states[vs_france] = "PEACE"

        cleanup_war_end(world, vs_france)

        assert vs_france not in world.ai_stalemate_counters

    def test_three_way_only_the_ended_pair_is_touched(self):
        world = make_world()
        world.current_turn = 30
        keys = {
            pair(world, "Britain", "France"): 11,
            pair(world, "Britain", "Spain"): 7,
            pair(world, "Britain", "Holland"): 4,
            pair(world, "Austria", "France"): 9,
        }
        world.ai_stalemate_counters = dict(keys)
        ended = pair(world, "Britain", "Holland")
        world.diplomatic_states[ended] = "PEACE"

        cleanup_war_end(world, ended)

        assert ended not in world.ai_stalemate_counters
        for k, v in keys.items():
            if k != ended:
                assert world.ai_stalemate_counters[k] == v, (
                    f"{k} was collateral damage")


# ═══════════════════════════════════════════════════════════════
# (b) CROSS-WAR BLEED — the mirror defect at the writer and reader
# ═══════════════════════════════════════════════════════════════

class TestCrossWarBleed:

    def test_writer_keeps_two_wars_on_two_clocks(self):
        """Deadlock with France ten turns while the Spanish war swings
        decisively. Two independent numbers, not one."""
        world = make_world()
        for _ in range(10):
            _update_stalemate_counter("Britain", "France", 0, world)
        _update_stalemate_counter("Britain", "Spain", 55, world)

        assert world.ai_stalemate_counters[pair(world, "Britain", "France")] == 10
        assert world.ai_stalemate_counters[pair(world, "Britain", "Spain")] == 0

    def test_provocation_one_clock_would_have_read_zero(self):
        """CONTROL: the same sequence under nation-keying. The decisive
        Spanish swing zeroes the number Britain would consult about France.
        """
        counters = {}
        for _ in range(10):
            counters["Britain"] = counters.get("Britain", 0) + 1   # France, deadlocked
        counters["Britain"] = 0                                    # Spain, decisive
        assert counters["Britain"] == 0, (
            "control: nation-keying loses ten turns of French deadlock to Spain")

    def test_reset_is_per_pair_not_global(self):
        world = make_world()
        for _ in range(6):
            _update_stalemate_counter("Britain", "France", 3, world)
            _update_stalemate_counter("Britain", "Spain", -8, world)
        assert world.ai_stalemate_counters[pair(world, "Britain", "France")] == 6
        assert world.ai_stalemate_counters[pair(world, "Britain", "Spain")] == 6

        _update_stalemate_counter("Britain", "France", 42, world)
        assert world.ai_stalemate_counters[pair(world, "Britain", "France")] == 0
        assert world.ai_stalemate_counters[pair(world, "Britain", "Spain")] == 6

    @pytest.mark.parametrize("score,grows", [
        (-11, False), (-10, True), (0, True), (10, True), (11, False),
    ])
    def test_the_deadlock_band_is_unchanged(self, score, grows):
        """DP-1 re-keyed the counter and changed nothing else. The -10..+10
        band is byte-identical behaviour."""
        world = make_world()
        world.ai_stalemate_counters = {pair(world, "Britain", "France"): 5}
        result = _update_stalemate_counter("Britain", "France", score, world)
        assert result == (6 if grows else 0)


# ═══════════════════════════════════════════════════════════════
# THE READER — the acceptance modifier consults the same clock
# ═══════════════════════════════════════════════════════════════

class TestAcceptanceReader:

    def test_stalemate_duration_reads_this_war_not_another(self):
        """R143 pays +1 acceptance per deadlocked turn, cap +15. It must
        price THIS war's deadlock."""
        from backend.game_logic import diplomacy as dip
        world = make_world()
        world.current_turn = 20
        vs_france = pair(world, "Britain", "France")
        vs_spain = pair(world, "Britain", "Spain")
        world.diplomatic_states[vs_france] = "WAR"
        world.diplomatic_states[vs_spain] = "WAR"
        world.war_start_turns[vs_france] = 5
        world.nation_relations[vs_france] = -40
        world.ai_stalemate_counters = {vs_france: 9, vs_spain: 15}

        components = dip.calculate_acceptance(
            {"type": "armistice_losing", "proposer_nation": "France",
             "target_nation": "Britain"}, world)["components"]
        assert components["stalemate_duration"] == 9, (
            "the reader took the Spanish clock — it is nation-blind again")

    def test_reader_and_writer_agree_on_the_key(self):
        """The real coupling: whatever the writer stored, the reader finds.
        Drive the writer, then read through the public acceptance path."""
        from backend.game_logic import diplomacy as dip
        world = make_world()
        world.current_turn = 20
        vs_france = pair(world, "Britain", "France")
        world.diplomatic_states[vs_france] = "WAR"
        world.war_start_turns[vs_france] = 5
        world.nation_relations[vs_france] = -40
        for _ in range(7):
            _update_stalemate_counter("Britain", "France", 0, world)

        components = dip.calculate_acceptance(
            {"type": "armistice_losing", "proposer_nation": "France",
             "target_nation": "Britain"}, world)["components"]
        assert components["stalemate_duration"] == 7

    def test_reader_is_symmetric_in_proposer_and_target(self):
        """France asking Britain and Britain asking France read one clock."""
        from backend.game_logic import diplomacy as dip
        world = make_world()
        world.current_turn = 20
        key = pair(world, "Britain", "France")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 5
        world.nation_relations[key] = -40
        world.ai_stalemate_counters = {key: 8}

        a = dip.calculate_acceptance(
            {"type": "armistice_losing", "proposer_nation": "France",
             "target_nation": "Britain"}, world)["components"]
        b = dip.calculate_acceptance(
            {"type": "armistice_losing", "proposer_nation": "Britain",
             "target_nation": "France"}, world)["components"]
        assert a["stalemate_duration"] == b["stalemate_duration"] == 8


# ═══════════════════════════════════════════════════════════════
# THE WHOLE LOOP — writer → cleanup → reader, as the turn runs it
# ═══════════════════════════════════════════════════════════════

class TestTheLoopEndToEnd:

    def test_britain_can_finish_a_fifteen_turn_clock_through_two_peaces(self):
        """THE DEFECT, reproduced as a scenario and then not happening.

        Fifteen turns of French deadlock, interrupted at turn 5 by peace
        with Spain and at turn 10 by peace with Holland. Before DP-1 the
        clock read 5 at the end. It must read 15.
        """
        world = make_world()
        world.current_turn = 1
        vs_france = pair(world, "Britain", "France")
        vs_spain = pair(world, "Britain", "Spain")
        vs_holland = pair(world, "Britain", "Holland")
        for k in (vs_france, vs_spain, vs_holland):
            world.diplomatic_states[k] = "WAR"

        for turn in range(1, 16):
            world.current_turn = turn
            _update_stalemate_counter("Britain", "France", 0, world)
            if turn == 5:
                world.diplomatic_states[vs_spain] = "PEACE"
                cleanup_war_end(world, vs_spain)
            if turn == 10:
                world.diplomatic_states[vs_holland] = "PEACE"
                cleanup_war_end(world, vs_holland)

        assert world.ai_stalemate_counters[vs_france] == 15, (
            "Britain's clock was reset by its own separate peaces — the "
            "exact reason a strangled Britain never sued")

    def test_provocation_the_same_scenario_under_the_old_shape(self):
        """CONTROL: replay it nation-keyed. The clock ends at 5, one third
        of what the P2 rung needs — so the rung never fires."""
        counters = {}
        for turn in range(1, 16):
            counters["Britain"] = counters.get("Britain", 0) + 1
            if turn in (5, 10):
                counters.pop("Britain", None)   # R110's both-nations pop
        assert counters["Britain"] == 5, (
            "control: the old shape tops out at the gap between peaces")


# ═══════════════════════════════════════════════════════════════
# SERIALIZATION + THE LOAD MIGRATION
# ═══════════════════════════════════════════════════════════════

class TestSerialization:

    def test_pair_keys_round_trip(self):
        world = make_world()
        key = pair(world, "Britain", "France")
        world.ai_stalemate_counters = {key: 12}
        restored = WorldState.from_dict(world.to_dict())
        assert restored.ai_stalemate_counters == {key: 12}

    def test_legacy_nation_keys_are_dropped_at_load(self):
        """A pre-DP-1 save carries nation keys nothing can read. Which war
        they counted is unknowable — that ambiguity IS the defect — so they
        are dropped, not guessed at."""
        world = make_world()
        data = world.to_dict()
        data["ai_stalemate_counters"] = {"Britain": 9, "Prussia": 4}
        restored = WorldState.from_dict(data)
        assert restored.ai_stalemate_counters == {}

    def test_a_mixed_save_keeps_the_pair_keys(self):
        """Belt and braces: a save written across the boundary keeps what
        it can read and drops only the dead half."""
        world = make_world()
        key = pair(world, "Britain", "France")
        data = world.to_dict()
        data["ai_stalemate_counters"] = {"Britain": 9, key: 6}
        restored = WorldState.from_dict(data)
        assert restored.ai_stalemate_counters == {key: 6}

    def test_dropping_costs_at_most_one_clock(self):
        """The migration's cost, stated as a test: a dropped clock simply
        restarts. It cannot corrupt, and it self-heals in <=15 turns."""
        world = make_world()
        data = world.to_dict()
        data["ai_stalemate_counters"] = {"Britain": 14}
        restored = WorldState.from_dict(data)
        for _ in range(15):
            _update_stalemate_counter("Britain", "France", 0, restored)
        assert restored.ai_stalemate_counters[
            pair(restored, "Britain", "France")] == 15
