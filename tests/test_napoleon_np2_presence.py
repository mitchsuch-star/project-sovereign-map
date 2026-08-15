"""NP-2 — The Presence (NAPOLEON_SPEC.md §5, gate §14.1 Q3◆).

Three mechanics, all content-dormant without an authored sovereign:
- the aura: +10%/+10% (N1/N2) for every friendly corps in the sovereign's
  province, stamped by _calculate_coordination_context as its own
  multiplicative factor OUTSIDE the coordination caps, registered in
  COORDINATION_TRANSIENT_FIELDS (the CA8-19(i) lesson);
- the fear (N3): the AI needs bigger odds against the Emperor's stack —
  and the aura of invincibility is EARNED: fear reads imperial grip, full
  at >=70, gone at <=30 ("his losses have weight", user direction);
- discipline under the eye (§5.3): +1 grievance threshold for a marshal
  co-located with his sovereign, DR-3 hair-triggers exempt.
Plus §5.4: emperor-led battles move authority (+2 victory / -5 defeat).
"""

import random as _random

import pytest

import backend.ai.enemy_ai as enemy_ai_module
import backend.commands.combat_executor as combat_executor_module
from backend.ai.enemy_ai import EnemyAI, sovereign_fear_factor
from backend.commands.executor import CommandExecutor
from backend.game_logic import jealousy
from backend.game_logic.battle_report import (
    snapshot_attacker_modifiers,
    snapshot_defender_modifiers,
)
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Fixtures (the MC-V idiom)
# ════════════════════════════════════════════════════════════════════════

def CE():
    """A combat sub-executor with its parent (the house wiring)."""
    return CommandExecutor()._combat


def AI():
    return EnemyAI(CommandExecutor())


def make_marshal(name, location="Belgium", strength=30000, nation="France",
                 personality="cautious", cavalry=False, artillery=False,
                 **kw):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation,
                movement_range=2 if cavalry else 1,
                cavalry=cavalry, artillery=artillery,
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


FIXED_DICE = {
    "natural": 7, "modified": 9, "is_critical_success": False,
    "is_critical_failure": False, "multiplier": 1.0,
    "skill_bonus": 2, "flanking_bonus": 0,
}


@pytest.fixture()
def fixed_rng(monkeypatch):
    monkeypatch.setattr(CombatResolver, "roll_combat_dice",
                        lambda self, marshal, flanking_bonus=0: dict(FIXED_DICE))
    monkeypatch.setattr(_random, "uniform", lambda a, b: (a + b) / 2.0)
    monkeypatch.setattr(_random, "random", lambda: 0.5)


def execute_attack(world, attacker_name, target_name):
    executor = CommandExecutor()
    command = {"command": {
        "marshal": attacker_name,
        "action": "attack",
        "target": target_name,
        "_muster_confirmed": True,
    }}
    return executor.execute(command, {"world": world})


# ════════════════════════════════════════════════════════════════════════
# The aura — stamp, read, caps, clears (§5.1)
# ════════════════════════════════════════════════════════════════════════

class TestAuraStampAndRead:
    def test_band_with_and_without_the_sovereign(self):
        """The §12.3 band test: a 2-marshal French stack with/without the
        sovereign — the exact aura delta, independent of coordination."""
        a = make_marshal("Ney", personality="aggressive")
        b = make_marshal("Davout", personality="cautious")
        w = make_world(a, b)
        ce = CE()
        ce._calculate_coordination_context(a, w)
        base_atk = a.get_attack_modifier(1.0, consume=False)
        base_def = a.get_defense_modifier()

        s = make_sovereign()
        w2 = make_world(make_marshal("Ney", personality="aggressive"),
                        make_marshal("Davout", personality="cautious"), s)
        a2 = w2.marshals["Ney"]
        ce._calculate_coordination_context(a2, w2)
        aura_atk = a2.get_attack_modifier(1.0, consume=False)
        aura_def = a2.get_defense_modifier()

        # The aura is its own multiplicative factor — never eaten by the
        # coordination caps. (Coordination itself differs between the two
        # worlds — a third corps adds per-ally % — so compare against the
        # RE-STAMPED base, not raw ratios.)
        assert a2.sovereign_presence == 1.0
        assert aura_atk == pytest.approx(
            base_atk / (1.0 + a.total_coordination_attack_bonus)
            * (1.0 + a2.total_coordination_attack_bonus)
            * (1.0 + Marshal.SOVEREIGN_PRESENCE_ATTACK))
        assert aura_def <= 1.75
        assert aura_def > base_def

    def test_sovereign_carries_his_own_presence(self):
        s = make_sovereign()
        w = make_world(s)
        CE()._calculate_coordination_context(s, w)
        assert s.sovereign_presence == 1.0
        assert s.get_attack_modifier(1.0, consume=False) == pytest.approx(
            1.0 + Marshal.SOVEREIGN_PRESENCE_ATTACK)

    def test_enemy_sovereign_stamps_his_own_side(self):
        # GR5: both sides compute independently — an enemy-authored
        # sovereign works identically.
        kaiser = make_sovereign("Kaiser", nation="Austria")
        guard = make_marshal("Mack", nation="Austria")
        w = make_world(kaiser, guard)
        CE()._calculate_coordination_context(guard, w)
        assert guard.sovereign_presence == 1.0
        assert kaiser.sovereign_presence == 1.0

    def test_no_sovereign_no_stamp(self):
        a = make_marshal("Ney", personality="aggressive")
        b = make_marshal("Davout", personality="cautious")
        w = make_world(a, b)
        CE()._calculate_coordination_context(a, w)
        assert getattr(a, "sovereign_presence", 0.0) == 0.0

    def test_broken_sovereign_grants_no_aura(self):
        s = make_sovereign(broken=True)
        a = make_marshal("Ney", personality="aggressive")
        w = make_world(s, a)
        CE()._calculate_coordination_context(a, w)
        assert getattr(a, "sovereign_presence", 0.0) == 0.0

    def test_registered_transient_and_cleared(self):
        assert "sovereign_presence" in Marshal.COORDINATION_TRANSIENT_FIELDS
        s = make_sovereign()
        s.sovereign_presence = 1.0
        s.clear_coordination_transients()
        assert s.sovereign_presence == 0.0
        s.sovereign_presence = 1.0
        s.clear_combat_transient_state()
        assert s.sovereign_presence == 0.0

    def test_never_serialized(self):
        s = make_sovereign()
        s.sovereign_presence = 1.0
        assert "sovereign_presence" not in s.to_dict()

    def test_defense_cap_still_binds(self):
        s = make_sovereign()
        d = make_marshal("Davout", personality="cautious")
        d.fortified = True
        d.defense_bonus = 0.60
        w = make_world(s, d)
        CE()._calculate_coordination_context(d, w)
        assert d.get_defense_modifier() <= 1.75

    def test_flip_lever_reproduces_pre_slice(self, monkeypatch):
        monkeypatch.setattr(combat_executor_module,
                            "SOVEREIGN_PRESENCE_ACTIVE", False)
        s = make_sovereign()
        a = make_marshal("Ney", personality="aggressive")
        w = make_world(s, a)
        CE()._calculate_coordination_context(a, w)
        assert getattr(a, "sovereign_presence", 0.0) == 0.0


class TestAuraShownEqualsApplied:
    def test_battle_report_rows_both_sides(self):
        atk = make_marshal("Ney", personality="aggressive")
        atk.sovereign_presence = 1.0
        deff = make_marshal("Mack", nation="Austria")
        deff.sovereign_presence = 1.0
        atk_rows = snapshot_attacker_modifiers(atk, deff, "plains", 0.0, 0, False)
        def_rows = snapshot_defender_modifiers(deff, atk, "plains", 0.0)
        assert any(r["label"] == "The Emperor commands in person"
                   and r["value"] == 10 and r["type"] == "bonus"
                   for r in atk_rows)
        assert any(r["label"] == "The Emperor commands in person"
                   for r in def_rows)

    def test_no_row_without_presence(self):
        atk = make_marshal("Ney", personality="aggressive")
        deff = make_marshal("Mack", nation="Austria")
        rows = snapshot_attacker_modifiers(atk, deff, "plains", 0.0, 0, False)
        assert not any("Emperor" in r["label"] for r in rows)

    def test_muster_preview_note(self):
        s = make_sovereign()
        a = make_marshal("Ney", personality="aggressive")
        e = make_marshal("Mack", nation="Austria", location="Bavaria")
        w = make_world(s, a, e)
        preview = CE()._build_muster_preview(
            a, e, w, {"world": w})
        assert "The Emperor commands in person" in preview.get(
            "presence_note", "")

    def test_muster_preview_silent_without_sovereign(self):
        a = make_marshal("Ney", personality="aggressive")
        e = make_marshal("Mack", nation="Austria", location="Bavaria")
        w = make_world(a, e)
        preview = CE()._build_muster_preview(
            a, e, w, {"world": w})
        assert "presence_note" not in preview

    def test_live_battle_report_carries_the_row(self, fixed_rng):
        s = make_sovereign()
        a = make_marshal("Ney", personality="aggressive", strength=40000)
        e = make_marshal("Mack", nation="Austria", strength=15000)
        w = make_world(s, a, e)
        result = execute_attack(w, "Ney", "Mack")
        report = result.get("battle_report") or {}
        rows = (report.get("modifier_breakdown") or {}).get("attacker") or []
        assert any(r.get("label") == "The Emperor commands in person"
                   for r in rows), rows


# ════════════════════════════════════════════════════════════════════════
# The fear (§5.2, N3) — and the aura of invincibility that losses erode
# ════════════════════════════════════════════════════════════════════════

class TestFear:
    def test_full_fear_at_boot_grip(self):
        s = make_sovereign()
        guard = make_marshal("Ney", personality="aggressive")
        w = make_world(s, guard)
        ai = AI()
        base = 1.0
        ratio = ai._evaluate_target_ratio(base, guard, w)
        # boot authority 100 -> grip 100 -> full fear
        assert ratio == pytest.approx(base * 0.75)

    def test_fear_covers_the_sovereign_himself(self):
        s = make_sovereign()
        w = make_world(s)
        ratio = AI()._evaluate_target_ratio(1.0, s, w)
        assert ratio == pytest.approx(0.75)

    def test_no_fear_without_sovereign(self):
        a = make_marshal("Ney", personality="aggressive")
        w = make_world(a)
        assert AI()._evaluate_target_ratio(1.0, a, w) == pytest.approx(1.0)

    def test_gr5_french_ai_fears_enemy_sovereign(self):
        kaiser = make_sovereign("Kaiser", nation="Austria")
        w = make_world(kaiser)
        # evaluator reads the TARGET's stack — side-agnostic by construction
        assert AI()._evaluate_target_ratio(
            1.0, kaiser, w) == pytest.approx(0.75)

    def test_fear_factor_reads_the_grip(self, monkeypatch):
        import backend.models.authority as authority_module
        w = make_world(make_sovereign())
        for grip, expected in ((100, 0.75), (70, 0.75), (50, 0.875),
                               (30, 1.0), (0, 1.0)):
            monkeypatch.setattr(authority_module, "get_imperial_grip",
                                lambda world, nation, g=grip: g)
            assert sovereign_fear_factor(w, "France") == pytest.approx(
                expected), grip

    def test_losses_erode_the_aura_live(self):
        # The integration arm: crater the player's authority (capture-shock
        # scale) and the fear washes out — the AI stops flinching.
        s = make_sovereign()
        w = make_world(s)
        w.authority_tracker.modify_authority(-80)  # 100 -> 20, grip <= 30
        assert AI()._evaluate_target_ratio(
            1.0, s, w) == pytest.approx(1.0)

    def test_flip_lever_reproduces_pre_slice(self, monkeypatch):
        monkeypatch.setattr(enemy_ai_module, "SOVEREIGN_FEAR_ACTIVE", False)
        s = make_sovereign()
        w = make_world(s)
        assert AI()._evaluate_target_ratio(
            1.0, s, w) == pytest.approx(1.0)


# ════════════════════════════════════════════════════════════════════════
# Discipline under the eye (§5.3)
# ════════════════════════════════════════════════════════════════════════

class TestDiscipline:
    def _pair(self, rel):
        m = make_marshal("Ney", personality="aggressive")
        t = make_marshal("Davout", personality="cautious")
        m.set_relationship("Davout", rel)
        return m, t

    def test_professional_calmed_at_headquarters(self):
        m, t = self._pair(0)  # neutral: base 2
        away = jealousy._threshold_for(m, t, authority=50)
        here = jealousy._threshold_for(m, t, authority=50, under_the_eye=True)
        assert away == (2, False)
        assert here == (3, False)

    def test_hair_trigger_seethes_in_the_emperors_tent(self):
        # DR-3 exemption intact: a Rival (-1, base 1) is NOT calmed.
        m, t = self._pair(-1)
        here = jealousy._threshold_for(m, t, authority=50, under_the_eye=True)
        assert here == (1, False)

    def test_sovereign_locations_map(self):
        s = make_sovereign(location="Paris")
        a = make_marshal("Ney", location="Paris", personality="aggressive")
        w = make_world(s, a)
        assert jealousy._sovereign_locations(w) == {"France": "Paris"}
        s.captured_by = "Austria"
        assert jealousy._sovereign_locations(w) == {}


# ════════════════════════════════════════════════════════════════════════
# The Emperor's prestige rides his own battles (§5.4, N4/N5)
# ════════════════════════════════════════════════════════════════════════

class TestEmperorLedAuthority:
    def test_emperor_led_victory_plus_two(self, fixed_rng):
        s = make_sovereign(strength=40000)
        e = make_marshal("Mack", nation="Austria", strength=15000)
        w = make_world(s, e)
        w.authority_tracker.authority = 80
        result = execute_attack(w, "Napoleon", "Mack")
        assert result.get("success") is True
        # stronger side won: no outnumbered arm, only the emperor-led +2
        assert w.authority_tracker.authority == 82

    def test_emperor_led_defeat_minus_five(self, fixed_rng):
        s = make_sovereign(strength=8000)
        s.morale = 100
        e = make_marshal("Mack", nation="Austria", strength=60000)
        e.fortified = True
        e.defense_bonus = 0.5
        w = make_world(s, e)
        w.authority_tracker.authority = 80
        result = execute_attack(w, "Napoleon", "Mack")
        assert result.get("success") is True
        # weaker side lost: no outnumbering arm, only the emperor-led -5
        assert w.authority_tracker.authority == 75

    def test_control_marshal_battle_moves_nothing_extra(self, fixed_rng):
        a = make_marshal("Ney", personality="aggressive", strength=40000)
        e = make_marshal("Mack", nation="Austria", strength=15000)
        w = make_world(a, e)
        w.authority_tracker.authority = 80
        execute_attack(w, "Ney", "Mack")
        # stronger side won, not emperor-led: no authority movement at all
        assert w.authority_tracker.authority == 80
