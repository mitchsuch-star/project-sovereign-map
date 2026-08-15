"""NP-0 — The Sovereign Substrate (NAPOLEON_SPEC.md §3.1/§6.1/§13, gate §14.1).

The fourth implemented personality: ``sovereign`` — the player embodied.
This file is the never-do pin set (spec §2), written as a BOTH-SIDES
regression gate: every guard keys on ``Marshal.is_sovereign`` (derived from
the already-serialized personality string — zero new serialized fields), so
an enemy-authored sovereign inherits the whole kit (GR5).

The pins, from the spec:
  - Never on the glory ladder, never crowned, never accrues glory, never an
    envy target, never a jealous subject.
  - Expectation forever 0; endow/rente refused in character; never eroding.
  - Trust never moves (structural: SovereignTrust no-ops modify/set across
    all 22 direct ``.trust.modify`` call sites); never autonomous.
  - No objection: evaluate_situation and evaluate_strategic_situation both
    return NONE (including the universal form_square MILD).
  - No voice: pick_marshal_voice and pick_enemy_voice return "".
  - AI: plays aggressive under AI control; delegation resolves to ASK;
    personality combat modifiers are 1.0; never reckless cavalry.
  - Never benched: the validator refuses a sovereign in marshal_pool;
    never dismissed (the debug arm refuses).
  - Dormancy: shipped legacy/tutorial content has no sovereign — every
    mechanism above is content-gated and inert until one is authored
    (the authoring slice lands with the NP-V measured pass).
"""

import pytest

from backend.ai.enemy_ai import get_effective_ai_personality
from backend.commands.delegation import classify_arm
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import (
    ConcernLevel,
    evaluate_situation,
    evaluate_strategic_situation,
)
from backend.game_logic import dotation, jealousy
from backend.game_logic.enemy_voice import pick_enemy_voice
from backend.game_logic.marshal_voice import pick_marshal_voice
from backend.models.marshal import (
    Marshal,
    create_enemy_marshals,
    create_marshal_from_data,
    create_starting_marshals,
)
from backend.models.personality import (
    IMPLEMENTED_PERSONALITIES,
    Personality,
    get_personality,
)
from backend.models.personality_modifiers import (
    get_attack_modifier_for_personality,
    get_defense_modifier_for_personality,
)
from backend.models.trust import SovereignTrust, Trust
from backend.models.world_state import WorldState
from backend.modding.validator import validate_marshal, validate_scenario


# ════════════════════════════════════════════════════════════════════════
# Fixtures (the MC-V idiom — hand-built worlds, no scenario contact)
# ════════════════════════════════════════════════════════════════════════

def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", cavalry=False, **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                movement_range=2 if cavalry else 1,
                cavalry=cavalry, spawn_location=location)
    for k, v in kw.items():
        setattr(m, k, v)
    return m


def make_sovereign(name="Napoleon", nation="France", location="Paris",
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


def inject_glory(marshal, turn, points):
    """Bypass the _append_glory guard to prove downstream filters hold
    even against leaked/legacy glory events."""
    marshal.glory_events.append({"turn": int(turn), "points": int(points)})


# ════════════════════════════════════════════════════════════════════════
# The single source
# ════════════════════════════════════════════════════════════════════════

class TestSingleSource:
    def test_sovereign_is_the_fourth_implemented_personality(self):
        assert IMPLEMENTED_PERSONALITIES == {
            "aggressive", "cautious", "literal", "sovereign"}

    def test_enum_member_exists_and_string_resolves(self):
        assert Personality.SOVEREIGN.value == "sovereign"
        assert get_personality("sovereign") is Personality.SOVEREIGN

    def test_is_sovereign_derives_from_personality(self):
        assert make_sovereign().is_sovereign is True
        for p in ("aggressive", "cautious", "literal"):
            assert make_marshal("M", personality=p).is_sovereign is False

    def test_is_sovereign_is_a_property_not_a_field(self):
        # Zero new serialized fields (spec pillar 5): the property never
        # appears in vars(), so serialization enforcement stays green.
        m = make_sovereign()
        assert "is_sovereign" not in vars(m)
        assert "is_sovereign" not in m.to_dict()

    def test_sovereign_round_trips_serialization(self):
        m = make_sovereign()
        m2 = Marshal.from_dict(m.to_dict())
        assert m2.personality == "sovereign"
        assert m2.is_sovereign is True


# ════════════════════════════════════════════════════════════════════════
# The glory court (spec §6.1) — both sides
# ════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nation", ["France", "Austria"])
class TestGloryCourt:
    def test_glory_never_accrues(self, nation):
        s = make_sovereign(nation=nation)
        jealousy._append_glory(s, turn=5, points=3)
        assert s.glory_events == []

    def test_battle_glory_never_accrues_to_a_sovereign_primary(self, nation):
        s = make_sovereign(nation=nation, location="Belgium")
        enemy_nation = "Austria" if nation == "France" else "France"
        e = make_marshal("Mack", nation=enemy_nation, personality="cautious")
        w = make_world(s, e)
        jealousy.record_battle_glory(
            w, s, e, attacker_won=True, defender_won=False,
            attacker_casualties=1000, defender_casualties=5000,
            conquered=True, pre_attacker_strength=10000,
            pre_defender_strength=30000)
        assert s.glory_events == []
        # The control proves the call binds: the beaten enemy primary
        # recorded his defeat.
        assert e.glory_events != []

    def test_never_on_the_ladder_even_with_injected_glory(self, nation):
        s = make_sovereign(nation=nation)
        peer = make_marshal("Peer", nation=nation, personality="aggressive")
        w = make_world(s, peer)
        inject_glory(s, w.current_turn, 10)
        names = [m.name for m, _ in jealousy.get_nation_ladder(w, nation)]
        assert s.name not in names
        assert "Peer" in names

    def test_never_crowned(self, nation):
        s = make_sovereign(nation=nation)
        peer = make_marshal("Peer", nation=nation, personality="aggressive")
        w = make_world(s, peer)
        inject_glory(s, w.current_turn, 10)
        jealousy.recompute_crowns(w)
        assert getattr(s, "glory_crowned", False) is False

    def test_never_an_envy_target(self, nation):
        s = make_sovereign(nation=nation)
        envious = make_marshal("Envious", nation=nation,
                               personality="aggressive")
        w = make_world(s, envious)
        inject_glory(s, w.current_turn, 10)  # far above the envious man
        assert jealousy.find_jealousy_target(envious, w) is None

    def test_never_a_jealous_subject(self, nation):
        s = make_sovereign(nation=nation)
        star = make_marshal("Star", nation=nation, personality="aggressive")
        w = make_world(s, star)
        inject_glory(star, w.current_turn, 10)
        assert jealousy.find_jealousy_target(s, w) is None


# ════════════════════════════════════════════════════════════════════════
# The reward economy (spec §6.1)
# ════════════════════════════════════════════════════════════════════════

class TestRewardEconomy:
    def test_expectation_forever_zero(self):
        s = make_sovereign(battles_won=25)
        assert dotation.get_expectation(s) == 0

    def test_never_shortfall_never_eroding(self):
        s = make_sovereign(battles_won=25)
        w = make_world(s)
        w.sovereign_map = "europe"
        assert dotation.get_shortfall(s, w) == 0
        s.expectation_grace_turn = 3  # even with a stale grace clock
        assert dotation.is_eroding(s, w) is False

    def test_endow_refused_in_character(self):
        s = make_sovereign()
        w = make_world(s)
        w.sovereign_map = "europe"
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Napoleon", "action": "grant_dotation",
                         "target": "Belgium"}},
            {"world": w})
        assert result["success"] is False
        assert "the Empire is his estate" in result["message"]

    def test_rente_refused_in_character(self):
        s = make_sovereign()
        w = make_world(s)
        w.sovereign_map = "europe"
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"marshal": "Napoleon", "action": "grant_pension"}},
            {"world": w})
        assert result["success"] is False
        assert "treasury is already his" in result["message"]


# ════════════════════════════════════════════════════════════════════════
# The trust freeze — structural, all 22 direct call sites covered
# ════════════════════════════════════════════════════════════════════════

class TestTrustFreeze:
    def test_ctor_installs_frozen_trust(self):
        s = make_sovereign()
        assert isinstance(s.trust, SovereignTrust)

    def test_modify_trust_noops(self):
        s = make_sovereign()
        start = s.trust.value
        assert s.modify_trust(-100) == 0
        assert s.modify_trust(+30) == 0
        assert s.trust.value == start

    def test_direct_trust_modify_noops(self):
        # The 22 direct `.trust.modify(...)` call sites across the backend
        # are covered by the object itself, not by the wrapper.
        s = make_sovereign()
        start = s.trust.value
        assert s.trust.modify(-100) == 0
        assert s.trust.set(5) is None
        assert s.trust.value == start

    def test_freeze_survives_from_dict(self):
        # from_dict REPLACES the trust object — the frozen class must be
        # re-installed on load.
        s = make_sovereign()
        loaded = Marshal.from_dict(s.to_dict())
        assert isinstance(loaded.trust, SovereignTrust)
        assert loaded.trust.modify(-100) == 0

    def test_serialized_shape_is_stable(self):
        assert SovereignTrust(100).to_dict() == {"value": 100}

    def test_never_autonomous(self):
        s = make_sovereign()
        start = s.trust.value
        s.modify_trust(-100)
        s.trust.modify(-100)
        assert s.trust.value == start
        assert s.autonomous is False

    def test_ordinary_marshal_trust_still_moves(self):
        # Control: the freeze binds ONLY the sovereign.
        m = make_marshal("Ney", personality="aggressive")
        assert m.modify_trust(-10) == -10
        assert m.trust.value == 60


# ════════════════════════════════════════════════════════════════════════
# No objection, no voice (spec §2 pillar 1)
# ════════════════════════════════════════════════════════════════════════

class TestNoFrictionNoVoice:
    def test_tactical_objection_always_none(self):
        s = make_sovereign()
        for action in ("retreat", "defend", "wait", "fortify", "attack"):
            level = evaluate_situation(s, action, {"action": action}, None)
            assert level == ConcernLevel.NONE, action

    def test_form_square_universal_mild_suppressed(self):
        # Control first: an aggressive marshal with BOTH cavalry and guns
        # adjacent grumbles MILD — the universal arm fires before the
        # personality dispatch, so it needs its own sovereign guard.
        s = make_sovereign(location="Belgium")
        control = make_marshal("Ney", personality="aggressive",
                               location="Belgium")
        cav = make_marshal("EnemyCav", nation="Austria", location="Belgium",
                           personality="aggressive", cavalry=True)
        art = make_marshal("EnemyGuns", nation="Austria", location="Belgium",
                           personality="cautious")
        art.artillery = True
        w = make_world(s, control, cav, art)
        gs = {"world": w}
        assert evaluate_situation(
            control, "form_square", {"action": "form_square"}, gs
        ) == ConcernLevel.MILD
        assert evaluate_situation(
            s, "form_square", {"action": "form_square"}, gs
        ) == ConcernLevel.NONE

    def test_strategic_objection_always_none(self):
        s = make_sovereign()
        rival = make_marshal("Rival", personality="cautious")
        s.set_relationship("Rival", -2)
        w = make_world(s, rival)
        gs = {"world": w}
        assert evaluate_strategic_situation(
            s, "SUPPORT", "Rival", [], gs) == ConcernLevel.NONE
        # Control: a hostile cautious marshal SUPPORTing his enemy objects.
        hater = make_marshal("Hater", personality="cautious")
        hater.set_relationship("Rival", -2)
        w2 = make_world(hater, rival)
        assert evaluate_strategic_situation(
            hater, "SUPPORT", "Rival", [], {"world": w2}) != ConcernLevel.NONE

    def test_no_marshal_voice(self):
        assert pick_marshal_voice("Napoleon", "sovereign", "won_field") == ""

    def test_no_enemy_voice_either_side(self):
        # An enemy-authored sovereign (NP-6's Tsar) must not speak the
        # cautious filler bank.
        assert pick_enemy_voice("Alexander", "sovereign", "beat_you") == ""


# ════════════════════════════════════════════════════════════════════════
# The AI reads (spec §3.1 sweep)
# ════════════════════════════════════════════════════════════════════════

class TestAIReads:
    def test_ai_alias_plays_aggressive(self):
        s = make_sovereign(nation="Austria")
        w = make_world(s)
        assert get_effective_ai_personality(s, w) == "aggressive"

    def test_delegation_resolves_to_ask(self):
        assert classify_arm("sovereign", True) == "ask"
        assert classify_arm("sovereign", False) == "ask"

    def test_personality_combat_modifiers_are_neutral(self):
        for ratio in (0.4, 1.0, 2.5):
            assert get_attack_modifier_for_personality(
                "sovereign", ratio) == 1.0
        assert get_defense_modifier_for_personality(
            "sovereign", "neutral") == 1.0

    def test_never_reckless_cavalry(self):
        s = make_sovereign(cavalry=True)
        assert s.is_reckless_cavalry is False


# ════════════════════════════════════════════════════════════════════════
# Authoring guards — validator, factory, pool, dismissal
# ════════════════════════════════════════════════════════════════════════

class TestAuthoringGuards:
    def test_validator_accepts_a_sovereign_marshal(self):
        result = validate_marshal({"name": "Napoleon", "location": "Paris",
                                   "strength": 10000,
                                   "personality": "sovereign"})
        assert not any("personality" in e.path for e in result.errors)

    def test_factory_constructs_a_sovereign(self):
        m = create_marshal_from_data({"name": "Napoleon", "location": "Paris",
                                      "strength": 10000,
                                      "personality": "sovereign"})
        assert m.is_sovereign is True

    def test_pool_refuses_a_sovereign(self):
        # NP-0 never-do pin: a sovereign is never benched.
        scenario = {
            "marshals": {"Ney": {"name": "Ney", "location": "Paris",
                                 "strength": 10000,
                                 "personality": "aggressive"}},
            "marshal_pool": {"France": [{
                "name": "Bonaparte", "personality": "sovereign",
                "skills": {"tactical": 10}, "cost": 5000,
            }]},
        }
        result = validate_scenario(scenario, check_adjacency=False)
        assert any("never" in e.message or "bench" in e.message
                   for e in result.errors
                   if "marshal_pool" in e.path and "personality" in e.path)

    def test_dismissal_refused(self):
        s = make_sovereign()
        other = make_marshal("Ney", personality="aggressive")
        w = make_world(s, other)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "debug", "target": "dismiss Napoleon"}},
            {"world": w, "debug_mode": True})
        assert result["success"] is False
        assert "does not dismiss its Emperor" in result.get("message", "")
        assert "Napoleon" in w.marshals


# ════════════════════════════════════════════════════════════════════════
# Dormancy — the mechanism is content-gated (spec §2 never-do pins)
# ════════════════════════════════════════════════════════════════════════

class TestDormancy:
    def test_legacy_fixture_world_has_no_sovereign(self):
        marshals = {**create_starting_marshals(), **create_enemy_marshals()}
        assert marshals
        assert not any(m.is_sovereign for m in marshals.values())

    def test_ordinary_marshals_get_plain_trust(self):
        m = make_marshal("Ney", personality="aggressive")
        assert type(m.trust) is Trust
