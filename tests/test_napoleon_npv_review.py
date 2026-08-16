"""NP-V — the measured pass: pins for every defect the adversarial review
and the live drive found in row NP (NAPOLEON_SPEC §13 NP-V).

Each class names the finding it closes. Written to FAIL if the production
fix is reverted — the review's own lens 6 caught this file's predecessors
asserting producer dicts and formulas-against-themselves, so every pin
here reads an APPLIED value or a rendered string.

Findings closed:
  P1  the Presence evaporated when the Emperor marched to the guns
      (attacker-side arrivals relocate to the battle region, so they were
      in NEITHER coordination set — the aura fired only when he FAILED
      to join).
  P1  the Shadow only ever fired on a same-province battle between
      marshals who liked him (participants are rebuilt after the victor
      advances, and the A-D4 hostile filter drops the sovereign).
  P1  a CAPTURED sovereign was still commandable through the NP-1 address
      forms, and came home from captivity fortified.
  P2  a broken/routed Emperor granted no aura but still deterred the AI.
  P2  the 1-AP discount lived at 2 of 4 pricing sites (a REFUSAL skew).
  P2  `presence_note` was written, pinned and never rendered.
  P2  the apex card rendered no ability block and no personality line.
  P2  "Marshal Napoleon" in the chronicle under a THE EMPEROR TAKEN
      masthead.
  P2  the trailing self-marker became the phantom province "Bavaria
      Myself" (live-drive finding).
  P3  the last stand named the CAPTOR'S CAPITAL as the field he died on
      (pre-existing; row NP made it the game's biggest moment).
"""

import random as _random

import pytest

import backend.ai.enemy_ai as enemy_ai_module
from backend.ai.enemy_ai import EnemyAI
from backend.campaign_log import format_event_oneliner
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser, _find_player_sovereign
from backend.display_names import marshal_honorific
from backend.game_logic import jealousy
from backend.game_logic.combat import CombatResolver
from backend.game_logic.marshal_overview import (
    _PERSONALITY_DESCRIPTIONS,
    _WIRED_ABILITY_MARSHALS,
    build_marshal_overview,
)
from backend.models.marshal import Marshal, Stance
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
        w.diplomatic_states[w._make_diplo_key(a, b)] = "WAR"
    w._build_marshal_index()
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


def attack(world, who, target):
    return CommandExecutor().execute(
        {"command": {"marshal": who, "action": "attack", "target": target,
                     "_muster_confirmed": True}},
        {"world": world})


# ════════════════════════════════════════════════════════════════════════
# P1 — the Presence reaches the army that MARCHES
# ════════════════════════════════════════════════════════════════════════

class TestPresenceReachesTheMarchingArmy:
    """The aura is sampled AT BATTLE TIME by spying on the modifier read —
    reading `sovereign_presence` after `execute` is invalid, the clear has
    already run (the review's own methodology note)."""

    def _spy(self, monkeypatch):
        seen = {}
        real = Marshal.get_attack_modifier

        def spy(self, strength_ratio=None, consume=True):
            seen.setdefault(self.name,
                            getattr(self, "sovereign_presence", "ABSENT"))
            return real(self, strength_ratio, consume)

        monkeypatch.setattr(Marshal, "get_attack_modifier", spy)
        return seen

    def test_the_emperor_marching_to_the_guns_carries_his_presence(
            self, fixed_rng, monkeypatch):
        # The defect: Napoleon co-located with Ney at Belgium, Ney attacks
        # Waterloo. Napoleon joins as a reinforcement and RELOCATES to the
        # battle region — he used to land in neither eligible set, so the
        # aura fired on nobody.
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", location="Belgium", strength=40000,
                           personality="aggressive")
        mack = make_marshal("Mack", location="Waterloo", strength=20000,
                            nation="Austria")
        w = make_world(nap, ney, mack)
        seen = self._spy(monkeypatch)
        result = attack(w, "Ney", "Mack")
        assert result.get("success"), result.get("message")
        assert seen.get("Ney") == 1.0, (
            f"the marching army must carry the aura, saw {seen}")

    def test_the_report_names_it_on_a_cross_province_attack(self, fixed_rng):
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", location="Belgium", strength=40000,
                           personality="aggressive")
        mack = make_marshal("Mack", location="Waterloo", strength=20000,
                            nation="Austria")
        w = make_world(nap, ney, mack)
        rows = ((attack(w, "Ney", "Mack").get("battle_report") or {})
                .get("modifier_breakdown") or {}).get("attacker") or []
        assert any(r.get("label") == "The Emperor commands in person"
                   for r in rows), rows

    def test_control_no_sovereign_no_aura(self, fixed_rng, monkeypatch):
        ney = make_marshal("Ney", location="Belgium", strength=40000,
                           personality="aggressive")
        dav = make_marshal("Davout", location="Belgium", strength=20000)
        mack = make_marshal("Mack", location="Waterloo", strength=20000,
                            nation="Austria")
        w = make_world(ney, dav, mack)
        seen = self._spy(monkeypatch)
        attack(w, "Ney", "Mack")
        assert seen.get("Ney") in (0.0, "ABSENT")


# ════════════════════════════════════════════════════════════════════════
# P1 — the Shadow follows the aura's audience
# ════════════════════════════════════════════════════════════════════════

class TestShadowFollowsTheAura:
    def test_shadow_fires_on_a_cross_province_attack(self, fixed_rng):
        """The ordinary case: a marshal sorties from the Emperor's HQ into
        an adjacent province. The victor ADVANCES before the glory step,
        so the rebuilt participant list no longer holds the sovereign —
        the Shadow used to miss and he banked full glory."""
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", location="Belgium", strength=60000,
                           personality="aggressive")
        mack = make_marshal("Mack", location="Waterloo", strength=8000,
                            nation="Austria")
        w = make_world(nap, ney, mack)
        attack(w, "Ney", "Mack")
        shadowed = sum(e["points"] for e in ney.glory_events)

        ney2 = make_marshal("Ney", location="Belgium", strength=60000,
                            personality="aggressive")
        mack2 = make_marshal("Mack", location="Waterloo", strength=8000,
                             nation="Austria")
        w2 = make_world(ney2, mack2)
        attack(w2, "Ney", "Mack")
        full = sum(e["points"] for e in ney2.glory_events)

        assert full > 0, "control battle must bank glory"
        assert shadowed == int(full * jealousy.GLORY_SHADOW_MULT), (
            f"under the Emperor's eye {full} should dim to "
            f"{int(full * jealousy.GLORY_SHADOW_MULT)}, saw {shadowed}")

    def test_the_hostile_pair_gets_NEITHER_aura_nor_shadow(
            self, fixed_rng, monkeypatch):
        """The A-D4 pair, RULED and pinned rather than forced.

        Bernadotte is authored at −2 with the Emperor, so the hostile
        no-show refuses to let Napoleon march to his battle: they did not
        fight the same field. The coherent outcome is that he gets
        NEITHER half — no +10%, and his laurels stay his own. (That is
        also the historically apt one: Bernadotte is the marshal who
        built a legend outside the shadow.)

        What the review found and this pins is the INCONSISTENCY that
        used to sit here: he mustered in the Emperor's province, was
        stamped with the aura at his ORIGIN, marched away alone, and
        fought at +10% with full glory — buffed by a man who refused to
        come. Both halves now key on the same audience.
        """
        seen = {}
        real = Marshal.get_attack_modifier

        def spy(self, strength_ratio=None, consume=True):
            seen.setdefault(self.name,
                            getattr(self, "sovereign_presence", "ABSENT"))
            return real(self, strength_ratio, consume)

        monkeypatch.setattr(Marshal, "get_attack_modifier", spy)

        nap = make_sovereign(location="Belgium")
        bern = make_marshal("Bernadotte", location="Belgium", strength=60000,
                            personality="cautious")
        nap.set_relationship("Bernadotte", -2)
        bern.set_relationship("Napoleon", -2)
        mack = make_marshal("Mack", location="Waterloo", strength=8000,
                            nation="Austria")
        w = make_world(nap, bern, mack)
        attack(w, "Bernadotte", "Mack")

        assert nap.location == "Belgium", "the hostile no-show must hold"
        assert seen.get("Bernadotte") in (0.0, "ABSENT"), (
            f"no aura from a man who refused to march, saw {seen}")

        bern2 = make_marshal("Bernadotte", location="Belgium", strength=60000,
                             personality="cautious")
        mack2 = make_marshal("Mack", location="Waterloo", strength=8000,
                             nation="Austria")
        w2 = make_world(bern2, mack2)
        attack(w2, "Bernadotte", "Mack")
        assert (sum(e["points"] for e in bern.glory_events)
                == sum(e["points"] for e in bern2.glory_events)), \
            "and no shadow either — the two halves must agree"

    def test_explicit_verdict_overrides_the_participant_scan(self):
        """The override is the primary source; the scan is the fallback."""
        a = make_marshal("Ney", personality="aggressive")
        d = make_marshal("Mack", nation="Austria")
        w = make_world(a, d)
        jealousy.record_battle_glory(
            w, a, d, attacker_won=True, defender_won=False,
            attacker_casualties=100, defender_casualties=5000,
            conquered=True, pre_attacker_strength=30000,
            pre_defender_strength=30000,
            attacker_participants=[a], defender_participants=[d],
            attacker_shadow=True)          # no sovereign anywhere in sight
        shadowed = sum(e["points"] for e in a.glory_events)

        a2 = make_marshal("Ney", personality="aggressive")
        d2 = make_marshal("Mack", nation="Austria")
        w2 = make_world(a2, d2)
        jealousy.record_battle_glory(
            w2, a2, d2, attacker_won=True, defender_won=False,
            attacker_casualties=100, defender_casualties=5000,
            conquered=True, pre_attacker_strength=30000,
            pre_defender_strength=30000,
            attacker_participants=[a2], defender_participants=[d2])
        full = sum(e["points"] for e in a2.glory_events)
        assert full > 0 and shadowed == int(full * jealousy.GLORY_SHADOW_MULT)


# ════════════════════════════════════════════════════════════════════════
# P1 — a prisoner gives no orders, and comes home as he should
# ════════════════════════════════════════════════════════════════════════

class TestCapturedSovereignIsNotCommandable:
    def test_parse_seam_refuses_a_prisoner(self):
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", personality="aggressive")
        w = make_world(nap, ney)
        assert _find_player_sovereign(w) == "Napoleon"
        w.capture_marshal(nap, "Austria", context="test")
        assert _find_player_sovereign(w) is None

    def test_first_person_order_does_not_reach_a_prisoner(self):
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", personality="aggressive")
        w = make_world(nap, ney)
        w.capture_marshal(nap, "Austria", context="test")
        parsed = CommandParser().parse("I fortify", None, world=w)
        assert (parsed.get("command") or {}).get("marshal") != "Napoleon"

    def test_release_does_not_carry_captivity_state_home(self):
        nap = make_sovereign(location="Belgium")
        w = make_world(nap)
        nap.fortified = True
        nap.defense_bonus = 25
        nap.stance = Stance.DEFENSIVE
        w.capture_marshal(nap, "Austria", context="test")
        assert w.release_captured_marshal("Napoleon", reason="ransom")
        assert nap.fortified is False
        assert nap.defense_bonus == 0
        assert nap.stance == Stance.NEUTRAL


# ════════════════════════════════════════════════════════════════════════
# P2 — the fear tracks the aura's audience
# ════════════════════════════════════════════════════════════════════════

class TestFearMatchesTheAura:
    def test_a_routed_emperor_no_longer_deters(self):
        nap = make_sovereign(broken=True, retreated_this_turn=True,
                             retreat_recovery=3)
        ney = make_marshal("Ney", personality="aggressive")
        w = make_world(nap, ney)
        ai = EnemyAI(CommandExecutor())
        assert ai._evaluate_target_ratio(1.0, ney, w) == pytest.approx(1.0)

    def test_a_standing_emperor_still_deters(self):
        nap = make_sovereign()
        ney = make_marshal("Ney", personality="aggressive")
        w = make_world(nap, ney)
        ai = EnemyAI(CommandExecutor())
        assert ai._evaluate_target_ratio(1.0, ney, w) == pytest.approx(
            enemy_ai_module.SOVEREIGN_FEAR_FACTOR)


# ════════════════════════════════════════════════════════════════════════
# P2 — one price for a strategic order (GR1)
# ════════════════════════════════════════════════════════════════════════

class TestStrategicOrderAPSingleSource:
    def test_the_predicate(self):
        assert make_sovereign().strategic_order_ap() == 1
        assert make_marshal("Soult", personality="literal"
                            ).strategic_order_ap() == 1
        assert make_marshal("Ney", personality="aggressive"
                            ).strategic_order_ap() == 2
        assert make_marshal("Ney", personality="aggressive"
                            ).strategic_order_ap(auto_upgrade=True) == 1

    def test_no_pricing_site_hardcodes_the_discount(self):
        """The skew was a REFUSAL difference: the same order priced 1 or 2
        depending on which verb reached it."""
        import pathlib
        import re
        root = pathlib.Path(__file__).resolve().parents[1] / "backend"
        pattern = re.compile(r"1 if is_literal else 2")
        offenders = [str(p) for p in root.rglob("*.py")
                     if pattern.search(p.read_text(encoding="utf-8"))]
        assert not offenders, offenders


# ════════════════════════════════════════════════════════════════════════
# P2 — the surfaces the player actually reads
# ════════════════════════════════════════════════════════════════════════

class TestSurfaces:
    def test_presence_note_is_rendered_not_just_produced(self):
        nap = make_sovereign(location="Belgium")
        ney = make_marshal("Ney", location="Belgium", strength=40000,
                           personality="aggressive")
        mack = make_marshal("Mack", location="Waterloo", strength=20000,
                            nation="Austria")
        w = make_world(nap, ney, mack)
        ce = CommandExecutor()._combat
        preview = ce._build_muster_preview(ney, mack, w, {"world": w})
        rendered = ce._format_muster_lines(preview)
        assert "The Emperor commands in person" in rendered

    def test_apex_card_carries_ability_and_personality_line(self):
        nap = make_sovereign()
        w = make_world(nap)
        nap.ability = {"name": "The Presence", "description": "d",
                       "trigger": "t", "effect": "e"}
        card = build_marshal_overview(w)[0]
        assert "Napoleon" in _WIRED_ABILITY_MARSHALS
        assert card.get("ability_active") is True, card
        assert "sovereign" in _PERSONALITY_DESCRIPTIONS
        assert card.get("personality_description")

    def test_the_chronicle_does_not_demote_him(self):
        nap = make_sovereign()
        w = make_world(nap)
        w.capture_marshal(nap, "Austria", context="test")
        captured = [e for e in w.event_log
                    if e.get("type") == "marshal_captured"][-1]
        assert "Marshal" not in format_event_oneliner(captured)
        assert "EMPEROR" in format_event_oneliner(captured)
        assert "Marshal" not in captured["message"]
        w.release_captured_marshal("Napoleon", reason="ransom")
        released = [e for e in w.event_log
                    if e.get("type") == "marshal_released"][-1]
        assert "Marshal" not in format_event_oneliner(released)

    def test_control_an_ordinary_marshal_keeps_his_rank(self):
        ney = make_marshal("Ney", personality="aggressive")
        w = make_world(ney)
        w.capture_marshal(ney, "Austria", context="test")
        captured = [e for e in w.event_log
                    if e.get("type") == "marshal_captured"][-1]
        assert format_event_oneliner(captured).startswith("Marshal Ney")
        assert marshal_honorific(w, "Ney") == "Marshal Ney"


# ════════════════════════════════════════════════════════════════════════
# P3 — the last stand names the field he died on
# ════════════════════════════════════════════════════════════════════════

class TestLastStandField:
    def test_the_field_is_not_the_captors_capital(self):
        nap = make_sovereign(location="Swabia", strength=8000)
        mack = make_marshal("Mack", location="Swabia", strength=50000,
                            nation="Austria")
        w = make_world(nap, mack)
        msg = CommandExecutor()._combat._resolve_last_stand_fight(
            nap, mack, w)
        assert "turns at bay at Swabia" in msg, msg
        assert "turns at bay at Vienna" not in msg


# ════════════════════════════════════════════════════════════════════════
# The blessed numbers, pinned as APPLIED behaviour (review lens 6: the
# band test compared the formula to itself, and N2/N6 had no pin at all)
# ════════════════════════════════════════════════════════════════════════

class TestBlessedNumbersAreApplied:
    def test_n1_attack_aura_is_ten_percent_applied(self):
        m = make_marshal("Ney", personality="cautious")
        base = m.get_attack_modifier(1.0, consume=False)
        m.sovereign_presence = 1.0
        assert m.get_attack_modifier(1.0, consume=False) == pytest.approx(
            base * 1.10)

    def test_n2_defence_aura_is_ten_percent_applied(self):
        m = make_marshal("Ney", personality="cautious")
        base = m.get_defense_modifier()
        m.sovereign_presence = 1.0
        assert m.get_defense_modifier() == pytest.approx(base * 1.10)

    def test_n6_shadow_halves_a_known_score(self):
        a = make_marshal("Ney", personality="aggressive")
        s = make_sovereign()
        d = make_marshal("Mack", nation="Austria")
        w = make_world(a, s, d)
        jealousy.record_battle_glory(
            w, a, d, attacker_won=True, defender_won=False,
            attacker_casualties=100, defender_casualties=9000,
            conquered=True, pre_attacker_strength=10000,
            pre_defender_strength=30000,
            attacker_participants=[a, s], defender_participants=[d])
        # victory + decisive + conquered + outnumbered = 4 -> 2
        assert sum(e["points"] for e in a.glory_events) == 2
