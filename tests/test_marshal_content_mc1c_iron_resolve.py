"""MC-1c pin tests — Davout "Iron Resolve" (MARSHAL_CONTENT_PASS_SPEC.md §4,
memo §1 Davout row; the MC-1 set's only T2/serialized-state slice).

The blessed mechanic (numbers gate-blessed, in-band tunable):
- Fortifying coils +1 resolve stack per fortified turn at the
  _process_tactical_states fortify tick, max 3.
- His NEXT attack consumes ALL stacks for +8% each (max +24%), consumed
  inside marshal.get_attack_modifier() ONLY (GR1/GR4).
- Load-bearing memo correction: a fortified marshal CANNOT attack
  (executor guard), so stacks MUST survive unfortify — the release always
  forfeits the accumulated fortify defense bonus, so peak +24% never rides
  a fortified posture (self-balancing — do not "fix").
- Anti-banking, each pinned: cap 3 (further fortified turns add nothing);
  ANY attack consumes all stacks; stacks CLEAR on move and on
  retreat/broken (the coil only holds while he stands).
- GR5: keyed off the ability NAME — any carrier, either side.
"""

import random as _random

import pytest

from backend.ai.parser_eval import build_world
from backend.commands.executor import CommandExecutor
from backend.game_logic.battle_report import snapshot_attacker_modifiers
from backend.game_logic.combat import CombatResolver
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Helpers (MC-1b patterns — legacy synthetic worlds for mechanics; the
# scenario pipeline is pinned separately in TestBootPins)
# ════════════════════════════════════════════════════════════════════════

FIXED_DICE = {
    "natural": 7, "modified": 9, "is_critical_success": False,
    "is_critical_failure": False, "multiplier": 1.0,
    "skill_bonus": 2, "flanking_bonus": 0,
}

IRON_RESOLVE = {"name": "Iron Resolve", "trigger": "when_fortifying"}


@pytest.fixture()
def fixed_rng(monkeypatch):
    """Fully deterministic combat (MC-1b fixture): fixed dice, midpoint
    variance, no fumble, pinned escape/choice rolls."""
    monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                        lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "randint", lambda a, b: (a + b) // 2)
    monkeypatch.setattr(_random, "random", lambda: 0.0)
    monkeypatch.setattr(_random, "choice", lambda seq: seq[0])


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", ability=None, cavalry=False,
                 morale=100, **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                movement_range=2 if cavalry else 1,
                ability=ability, cavalry=cavalry, spawn_location=location)
    m.morale = morale
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def make_world(*marshals, wars=(("France", "Britain"),)):
    w = WorldState()
    w.marshals = {m.name: m for m in marshals}
    for a, b in wars:
        key = w._make_diplo_key(a, b)
        w.diplomatic_states[key] = "WAR"
    return w


def _davout(stacks=0, **kw):
    m = make_marshal("Davout", ability=dict(IRON_RESOLVE), **kw)
    m.iron_resolve_stacks = stacks
    return m


def _fortify(world, name):
    ex = CommandExecutor()
    return ex._tactical._execute_fortify({"marshal": name}, {"world": world})


def _unfortify(world, name):
    ex = CommandExecutor()
    return ex._tactical._execute_unfortify({"marshal": name}, {"world": world})


def execute_attack(world, attacker_name, target_name):
    executor = CommandExecutor()
    command = {"command": {
        "marshal": attacker_name,
        "action": "attack",
        "target": target_name,
        "_muster_confirmed": True,
    }}
    return executor.execute(command, {"world": world})


def _stack_events(events, name="Davout"):
    return [e for e in events
            if e.get("type") == "iron_resolve_stack" and e.get("marshal") == name]


# ════════════════════════════════════════════════════════════════════════
# Boot pins: the ability block survives the scenario pipeline
# ════════════════════════════════════════════════════════════════════════

class TestBootPins:
    def test_davout_boots_with_iron_resolve(self):
        w = build_world("1805")
        assert w.get_marshal("Davout").ability.get("name") == "Iron Resolve"

    def test_davout_carries_the_trigger_key(self):
        w = build_world("1805")
        assert w.get_marshal("Davout").ability.get("trigger") == "when_fortifying"

    def test_boots_with_zero_stacks(self):
        w = build_world("1805")
        assert w.get_marshal("Davout").iron_resolve_stacks == 0

    def test_card_goes_active(self):
        # The tenth blessed ability — the MC-1a waiting pin flips with it.
        w = build_world("1805")
        cards = build_marshal_overview(w)
        card = next(c for c in cards if c["name"] == "Davout")
        assert card["ability_active"] is True
        assert card["ability_name"] == "Iron Resolve"


# ════════════════════════════════════════════════════════════════════════
# Stack growth at the fortify tick (+1/turn, cap 3, shown = applied)
# ════════════════════════════════════════════════════════════════════════

class TestStackGrowth:
    def test_fortified_tick_grants_stack_with_event(self):
        davout = _davout()
        world = make_world(davout)
        assert _fortify(world, "Davout")["success"] is True
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 1
        evs = _stack_events(events)
        assert len(evs) == 1
        # Shown = applied: the event names the exact bonus the coil carries.
        assert evs[0]["stacks"] == 1
        assert evs[0]["attack_bonus_pct"] == 8
        assert "+8%" in evs[0]["message"]
        assert "Iron Resolve" in evs[0]["message"]

    def test_growth_to_cap_three(self):
        davout = _davout()
        world = make_world(davout)
        _fortify(world, "Davout")
        for _ in range(3):
            events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 3
        assert _stack_events(events)[0]["attack_bonus_pct"] == 24
        # Shown = applied at EVERY stack count, not just the first — a
        # message hardcoding "+8%" must fail here (review fix, LOW).
        assert "+24%" in _stack_events(events)[0]["message"]
        assert "3/3" in _stack_events(events)[0]["message"]

    def test_cap_further_turns_add_nothing(self):
        # Anti-banking: the 4th fortified turn grants no stack and no event.
        davout = _davout()
        world = make_world(davout)
        _fortify(world, "Davout")
        for _ in range(3):
            world._process_tactical_states()
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 3
        assert _stack_events(events) == []

    def test_no_stack_without_the_ability(self):
        # GR5: name-keyed — an ordinary cautious marshal fortifying gains none.
        plain = make_marshal("Mortier")
        world = make_world(plain)
        _fortify(world, "Mortier")
        events = world._process_tactical_states()
        assert plain.iron_resolve_stacks == 0
        assert _stack_events(events, "Mortier") == []

    def test_no_stack_when_not_fortified(self):
        davout = _davout()
        world = make_world(davout)
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0
        assert _stack_events(events) == []

    def test_accrues_during_decay_phase_too(self):
        # Any turn spent fortified counts — including after growth maxes and
        # decay begins (fortify decay itself untouched by this slice).
        davout = _davout()
        world = make_world(davout)
        _fortify(world, "Davout")
        davout.cumulative_fortification_turns = 10  # deep in decay territory
        davout.defense_bonus = 0.15
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 1
        assert len(_stack_events(events)) == 1


# ════════════════════════════════════════════════════════════════════════
# The load-bearing memo correction: stacks SURVIVE unfortify
# ════════════════════════════════════════════════════════════════════════

class TestSurvivesUnfortify:
    def test_stacks_survive_unfortify(self):
        davout = _davout()
        world = make_world(davout)
        _fortify(world, "Davout")
        world._process_tactical_states()
        world._process_tactical_states()
        assert davout.iron_resolve_stacks == 2
        result = _unfortify(world, "Davout")
        assert result["success"] is True
        assert davout.fortified is False
        assert davout.defense_bonus == 0      # the release price: the fortify bonus
        assert davout.iron_resolve_stacks == 2  # the coil holds — he stood his ground

    def test_coil_uncoil_spring(self, fixed_rng):
        # The full rhythm: three patient turns fortified NEXT to the enemy
        # (fortifying while co-located is blocked — "engaged with enemy
        # forces"), unfortify, then the III Corps counterstroke at +24% —
        # never while still fortified (executor guard: a fortified marshal
        # cannot attack).
        davout = _davout()
        enemy = make_marshal("Mack", strength=25000, nation="Britain", morale=100)
        world = make_world(davout, enemy)
        enemy.location = world.get_region("Belgium").adjacent_regions[0]
        assert _fortify(world, "Davout")["success"] is True
        for _ in range(3):
            world._process_tactical_states()
        assert davout.iron_resolve_stacks == 3

        blocked = execute_attack(world, "Davout", "Mack")
        assert blocked.get("success") is False  # fortified: cannot attack
        assert davout.iron_resolve_stacks == 3  # nothing consumed by the refusal

        _unfortify(world, "Davout")
        result = execute_attack(world, "Davout", "Mack")
        assert "Iron Resolve: +24%" in result.get("message", "")
        assert davout.iron_resolve_stacks == 0


# ════════════════════════════════════════════════════════════════════════
# Consume-on-attack: exact +8/+16/+24% deltas, GR1/GR4, no banking
# ════════════════════════════════════════════════════════════════════════

class TestConsume:
    @pytest.mark.parametrize("stacks,expected", [(1, 1.08), (2, 1.16), (3, 1.24)])
    def test_exact_modifier_delta_vs_control(self, stacks, expected):
        coiled = _davout(stacks=stacks)
        control = _davout(stacks=0)
        ratio = coiled.get_attack_modifier() / control.get_attack_modifier()
        assert ratio == pytest.approx(expected)

    def test_consume_zeroes_stacks(self):
        davout = _davout(stacks=3)
        davout.get_attack_modifier()
        assert davout.iron_resolve_stacks == 0

    def test_no_banking_second_attack_gets_nothing(self):
        davout = _davout(stacks=3)
        control = _davout(stacks=0)
        first = davout.get_attack_modifier()
        second = davout.get_attack_modifier()
        assert first > second
        assert second == pytest.approx(control.get_attack_modifier())

    def test_defending_does_not_consume(self):
        davout = _davout(stacks=3)
        davout.get_defense_modifier()
        assert davout.iron_resolve_stacks == 3

    def test_name_keyed_not_marshal_keyed(self):
        # GR5 negative arm: stacks without the ability name grant nothing
        # (unreachable in play — only carriers accrue — but the arm must
        # key off the NAME, never off "Davout").
        plain = make_marshal("Davout", ability=None)
        plain.iron_resolve_stacks = 3
        control = make_marshal("Davout", ability=None)
        assert plain.get_attack_modifier() == pytest.approx(
            control.get_attack_modifier())

    def test_garrison_assault_consumes_and_names_it(self):
        # "ANY attack consumes all stacks" — the garrison assault reads the
        # same single-source modifier (GR1) and its message names the release.
        # 20k garrison cannot collapse in one assault (loss ratio cap 0.50)
        # — this pins the GARRISON-HOLDS branch's message.
        davout = _davout(stacks=2, location="Belgium")
        world = make_world(davout)
        region = world.get_region("London") or next(iter(world.regions.values()))
        region.garrison_strength = 20000
        region.garrison_detachment = False
        ex = CommandExecutor()
        result = ex._combat._resolve_garrison_combat(
            davout, region, world, {"world": world})
        assert davout.iron_resolve_stacks == 0
        assert "Garrison holds" in result.get("message", "")
        assert "Iron Resolve" in result.get("message", "")
        assert "+16%" in result.get("message", "")

    def test_garrison_collapse_branch_names_it_too(self):
        # Review fix (LOW): the COLLAPSE branch composes its own message —
        # a 5,500 garrison drops below the 5,000 threshold in one assault,
        # so the iron note must ride that copy as well.
        davout = _davout(stacks=2, location="Belgium")
        world = make_world(davout)
        region = world.get_region("London") or next(iter(world.regions.values()))
        region.garrison_strength = 5500
        region.garrison_detachment = False
        ex = CommandExecutor()
        result = ex._combat._resolve_garrison_combat(
            davout, region, world, {"world": world})
        assert davout.iron_resolve_stacks == 0
        assert "Garrison collapses" in result.get("message", "")
        assert "Iron Resolve" in result.get("message", "")
        assert "+16%" in result.get("message", "")


# ════════════════════════════════════════════════════════════════════════
# Clears: move / forced retreat / broken / capture (the coil only holds
# while he stands)
# ════════════════════════════════════════════════════════════════════════

class TestClears:
    def test_clear_on_move(self):
        davout = _davout(stacks=3)
        davout.move_to("Netherlands")
        assert davout.iron_resolve_stacks == 0

    def test_same_location_move_keeps_stacks(self):
        # move_to to the SAME region is not a move — the coil holds.
        davout = _davout(stacks=3)
        davout.move_to("Belgium")
        assert davout.iron_resolve_stacks == 3

    def test_clear_on_player_move_executor(self):
        davout = _davout(stacks=2)
        world = make_world(davout)
        adjacent = world.get_region("Belgium").adjacent_regions[0]
        ex = CommandExecutor()
        result = ex._movement._execute_move(
            davout, adjacent, world, {"world": world})
        assert result["success"] is True
        assert davout.iron_resolve_stacks == 0

    def test_clear_on_forced_retreat(self, fixed_rng):
        davout = _davout(stacks=3, morale=20)
        enemy = make_marshal("Wellington", strength=40000, nation="Britain",
                             personality="aggressive")
        world = make_world(davout, enemy)
        ex = CommandExecutor()
        msg = ex._combat._apply_forced_retreat_or_break(
            davout, enemy, world, skip_fate=True)
        assert msg
        assert davout.retreating or davout.broken
        assert davout.iron_resolve_stacks == 0

    def test_clear_on_broken(self, fixed_rng, monkeypatch):
        # Surrounded — no safe retreat — the army shatters; the coil dies
        # with the line.
        davout = _davout(stacks=3, morale=20)
        enemy = make_marshal("Wellington", strength=40000, nation="Britain",
                             personality="aggressive")
        world = make_world(davout, enemy)
        monkeypatch.setattr(world, "get_safe_retreat_destination",
                            lambda *a, **k: None)
        ex = CommandExecutor()
        msg = ex._combat._apply_forced_retreat_or_break(
            davout, enemy, world, skip_fate=True)
        assert msg
        assert davout.broken is True
        assert davout.iron_resolve_stacks == 0

    def test_clear_on_capture(self):
        davout = _davout(stacks=3)
        world = make_world(davout)
        ex = CommandExecutor()
        ex._combat._capture_marshal(davout, "Britain", world)
        assert davout.iron_resolve_stacks == 0


# ════════════════════════════════════════════════════════════════════════
# Serialization (the reason this slice ships alone — T2)
# ════════════════════════════════════════════════════════════════════════

class TestSerialization:
    def test_round_trip(self):
        davout = _davout(stacks=2)
        data = davout.to_dict()
        assert data["iron_resolve_stacks"] == 2
        loaded = Marshal.from_dict(data)
        assert loaded.iron_resolve_stacks == 2
        assert loaded.ability.get("name") == "Iron Resolve"

    def test_missing_key_defaults_to_zero(self):
        # Save-compat: pre-MC-1c saves carry no key — load coils nothing.
        davout = _davout(stacks=2)
        data = davout.to_dict()
        del data["iron_resolve_stacks"]
        loaded = Marshal.from_dict(data)
        assert loaded.iron_resolve_stacks == 0


# ════════════════════════════════════════════════════════════════════════
# Legibility: battle-report attacker row + description line (both combat
# result paths) + the fortify-tick event is already pinned above
# ════════════════════════════════════════════════════════════════════════

class TestLegibility:
    def test_battle_report_attacker_row(self):
        # Snapshots run PRE-consumption (memo-verified) — the row names
        # what the assault carried, derived from the blessed constant.
        davout = _davout(stacks=2)
        enemy = make_marshal("Mack", strength=25000, nation="Britain")
        mods = snapshot_attacker_modifiers(davout, enemy, "plains", 0.0, 0, False)
        row = next(m for m in mods if m["label"].startswith("Iron Resolve"))
        assert row["label"] == "Iron Resolve (2 stacks)"
        assert row["value"] == 16
        assert row["type"] == "bonus"

    def test_report_row_rides_the_battle(self, fixed_rng):
        davout = _davout(stacks=3)
        enemy = make_marshal("Mack", strength=25000, nation="Britain")
        result = CombatResolver().resolve_battle(davout, enemy)
        labels = [m["label"] for m in result["modifier_snapshot"]["attacker"]]
        assert "Iron Resolve (3 stacks)" in labels

    def test_description_line_normal_path(self, fixed_rng):
        davout = _davout(stacks=3)
        enemy = make_marshal("Mack", strength=25000, nation="Britain")
        result = CombatResolver().resolve_battle(davout, enemy)
        assert result["iron_resolve_triggered"] is not None
        assert "Iron Resolve: +24%" in result["iron_resolve_triggered"]
        assert "Iron Resolve: +24%" in result["description"]

    def test_description_line_deferred_path(self, fixed_rng):
        # The coordinated/deferred copy must carry the same line (MC-1b
        # review class: a message computed but dropped on one path).
        davout = _davout(stacks=2)
        enemy = make_marshal("Mack", strength=25000, nation="Britain")
        result = CombatResolver().resolve_battle(
            davout, enemy, apply_casualties=False)
        assert result["iron_resolve_triggered"] is not None
        assert "Iron Resolve: +16%" in result["description"]

    def test_no_line_without_stacks(self, fixed_rng):
        davout = _davout(stacks=0)
        enemy = make_marshal("Mack", strength=25000, nation="Britain")
        result = CombatResolver().resolve_battle(davout, enemy)
        assert result["iron_resolve_triggered"] is None
        assert "Iron Resolve" not in result["description"]


# ════════════════════════════════════════════════════════════════════════
# Surfaces: marshal card + map tooltip payload (derived fields, Q3 pattern)
# ════════════════════════════════════════════════════════════════════════

class TestSurfaces:
    def test_card_carries_stacks_and_derived_pct(self):
        w = build_world("1805")
        w.get_marshal("Davout").iron_resolve_stacks = 2
        cards = build_marshal_overview(w)
        card = next(c for c in cards if c["name"] == "Davout")
        assert card["iron_resolve_stacks"] == 2
        assert card["iron_resolve_bonus_pct"] == 16
        assert card["iron_resolve_max_stacks"] == 3

    def test_tooltip_payload_carries_derived_fields(self):
        w = build_world("1805")
        davout = w.get_marshal("Davout")
        davout.iron_resolve_stacks = 3
        summary = w.get_game_state_summary()
        entry = next(m for m in summary["map_data"][davout.location]["marshals"]
                     if m["name"] == "Davout")
        ts = entry["tactical_state"]
        assert ts["iron_resolve_stacks"] == 3
        assert ts["iron_resolve_bonus_pct"] == 24
        assert ts["iron_resolve_max_stacks"] == 3


# ════════════════════════════════════════════════════════════════════════
# GR5 symmetry: the ability is name-keyed — an enemy carrier coils and
# springs through the SAME seams
# ════════════════════════════════════════════════════════════════════════

class TestReviewFixes:
    """Pre-commit adversarial review (July 10, 2026): 7 confirmed findings.

    The HIGH: the stale `fortified` flag survives forced retreat and
    capture (pre-existing — move_to and _capture_marshal never clear it),
    so the accrual tick must independently refuse marshals who are not
    STANDING, or a routed carrier re-coils during recovery and a prisoner
    coils in captivity."""

    def _stale_fortified(self, davout):
        # The post-rout shape the review live-reproduced: fortified stayed
        # True through the rout while the rout itself cleared the stacks.
        davout.fortified = True
        davout.defense_bonus = 0.09
        davout.iron_resolve_stacks = 0

    def test_no_recoil_while_retreating(self):
        davout = _davout()
        world = make_world(davout)
        self._stale_fortified(davout)
        davout.retreating = True
        davout.retreat_recovery = 0
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0
        assert _stack_events(events) == []

    def test_no_recoil_while_broken(self):
        davout = _davout()
        world = make_world(davout)
        self._stale_fortified(davout)
        davout.broken = True
        davout.broken_recovery = 0
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0
        assert _stack_events(events) == []

    def test_no_recoil_while_captured(self):
        davout = _davout()
        world = make_world(davout)
        self._stale_fortified(davout)
        davout.captured_by = "Britain"
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0
        assert _stack_events(events) == []

    def test_no_recoil_off_field(self):
        # Administrative marshals leave the map (location None) but stay in
        # world.marshals — the tick loop must not coil them off-field.
        davout = _davout()
        world = make_world(davout)
        self._stale_fortified(davout)
        davout.location = None
        events = world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0
        assert _stack_events(events) == []

    def test_routed_carrier_does_not_recoil_through_recovery(self, fixed_rng):
        # The review's live repro, end to end: coil, get routed, and the
        # recovery turns must NOT re-arm the spring he abandoned.
        davout = _davout(morale=20)
        enemy = make_marshal("Wellington", strength=40000, nation="Britain",
                             personality="aggressive")
        world = make_world(davout, enemy)
        davout.fortified = True
        davout.defense_bonus = 0.09
        davout.iron_resolve_stacks = 2
        ex = CommandExecutor()
        ex._combat._apply_forced_retreat_or_break(
            davout, enemy, world, skip_fate=True)
        assert davout.retreating or davout.broken
        assert davout.iron_resolve_stacks == 0
        for _ in range(3):
            world._process_tactical_states()
        assert davout.iron_resolve_stacks == 0

    def test_release_from_captivity_comes_home_uncoiled(self):
        # The one direct location-assignment seam the first cut missed
        # (W6-7 ransom/peace release) — belt-and-braces with the accrual
        # guard, and the seam contract says every direct assignment clears.
        davout = _davout()
        world = make_world(davout)
        ex = CommandExecutor()
        ex._combat._capture_marshal(davout, "Britain", world)
        davout.iron_resolve_stacks = 3  # simulate any future re-coil path
        assert world.release_captured_marshal("Davout") is True
        assert davout.iron_resolve_stacks == 0

    def test_clear_on_reinforcement_arrival(self, fixed_rng):
        # Player-reachable arrival seam (direct location assignment in the
        # coordinated path): a coiled carrier under a written SUPPORT order
        # marches to the guns — the march uncoils him. Decisive win keeps
        # him at the battle region, so ONLY the arrival clear can fire.
        from backend.models.marshal import StrategicOrder
        ney = make_marshal("Ney", location="Belgium", strength=40000,
                           personality="aggressive")
        davout = _davout(stacks=3)
        enemy = make_marshal("Mack", strength=6000, nation="Britain", morale=40)
        world = make_world(ney, davout, enemy)
        davout.location = world.get_region("Belgium").adjacent_regions[0]
        davout.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Davout, support Ney")
        result = execute_attack(world, "Ney", "Mack")
        assert "WILL JOIN" in result.get("message", "")
        assert davout.location == "Belgium"  # arrived and stayed (side won)
        assert davout.iron_resolve_stacks == 0

    def test_debug_teleport_clears(self):
        davout = _davout(stacks=3)
        world = make_world(davout)
        ex = CommandExecutor()
        result = ex._meta._execute_debug(
            {"target": "set_location Davout Paris"},
            {"world": world, "debug_mode": True})
        assert result["success"] is True
        assert davout.iron_resolve_stacks == 0

    def test_debug_admin_cycle_clears(self):
        # Entry clears (leaving the field), and the restore seam clears
        # again (back on the map, no coil) — both direct assignments.
        davout = _davout(stacks=3)
        world = make_world(davout, make_marshal("Ney"))
        ex = CommandExecutor()
        entry = ex._meta._execute_debug(
            {"target": "admin Davout"}, {"world": world, "debug_mode": True})
        assert entry["success"] is True
        assert davout.iron_resolve_stacks == 0
        davout.iron_resolve_stacks = 2  # simulate any off-field re-coil path
        restore = ex._meta._execute_debug(
            {"target": "admin Davout"}, {"world": world, "debug_mode": True})
        assert restore["success"] is True
        assert davout.iron_resolve_stacks == 0


class TestGR5Symmetry:
    def test_enemy_carrier_accrues_at_the_same_tick(self):
        charles = make_marshal("ArchdukeCharles", nation="Britain",
                               ability=dict(IRON_RESOLVE))
        world = make_world(charles)
        charles.fortified = True
        charles.defense_bonus = 0.07
        events = world._process_tactical_states()
        assert charles.iron_resolve_stacks == 1
        assert len(_stack_events(events, "ArchdukeCharles")) == 1

    def test_enemy_carrier_consumes_on_attack(self, fixed_rng):
        charles = make_marshal("ArchdukeCharles", nation="Britain",
                               ability=dict(IRON_RESOLVE))
        charles.iron_resolve_stacks = 3
        defender = make_marshal("Ney", nation="France", strength=25000,
                                personality="aggressive")
        result = CombatResolver().resolve_battle(charles, defender)
        assert charles.iron_resolve_stacks == 0
        assert "Iron Resolve: +24%" in result["description"]
