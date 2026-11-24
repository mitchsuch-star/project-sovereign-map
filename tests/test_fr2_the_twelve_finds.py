"""Row FR, Session FR-2 — the weak-spot readers' twelve finds (WS-R).

`docs/WEAK_SPOT_FINDS_SPEC.md` (the design; §7 the landing record), `BUG_FIXES.md`
§WS (rows WS-R1 … WS-R12), `SYSTEMS_REFERENCE.md` §238. The November 13, 2026
weak-spot review filed twelve finds it had not confirmed in the code as one row,
WS-R. Each was read in the code at FR-2's head and proved here by behaviour: a
CONFIRMED find carries the test that failed before its fix; a REFUTED one keeps a
cheap guard where it has one.

One class per find (`TestWSR<n>…`). The finds that move the world sit behind the
named seams of `tests/_fr2_seams.py`; each class pins the seam's down state too.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO_PATH))


def _fresh(world1805) -> WorldState:
    with _quiet():
        return WorldState.from_dict(world1805.to_dict())


# ════════════════ WS-R4 — a court's bonus rides the attack it judged ═════════

class TestWSR4ACourtsBonusRidesItsOwnAttack:
    """Find 4. The player's half (a literal marshal's crisp-order buff banked
    with no end) was fixed by GRD-33 in row IC's Session 2 — refuted. The
    courts' half was real: `EnemyAI` scored an attack AFTER it ran
    (`apply_strategic_bonuses(..., is_combat_action=True)`), so the +5 / +10 %
    it earned waited for that marshal's NEXT attack, however many turns later.
    Now the attack is judged before it runs and spends its own bonus; the
    turn-end expiry covers every holder."""

    @staticmethod
    def _mack_attacks_ney(world, monkeypatch, score=90):
        from backend.ai import enemy_ai as EA
        from backend.commands.executor import CommandExecutor
        seen = []
        real = Marshal.get_attack_modifier

        def spy(self, *a, **k):
            if k.get("consume", True):
                seen.append((self.name, int(self.strategic_combat_bonus)))
            return real(self, *a, **k)

        monkeypatch.setattr(Marshal, "get_attack_modifier", spy)
        monkeypatch.setattr(EA, "calculate_ai_strategic_score", lambda **kw: score)
        with _quiet():
            result = EA.EnemyAI(CommandExecutor())._execute_action(
                {"marshal": "Mack", "action": "attack", "target": "Ney"}, {"world": world})
        return result, seen

    def test_the_attack_it_judged_spends_its_own_bonus(self, world1805, monkeypatch):
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        assert int(mack.strategic_combat_bonus) == 0
        result, seen = self._mack_attacks_ney(world, monkeypatch)
        assert result.get("success") and result.get("strategic_score") == 90
        assert seen and seen[0] == ("Mack", 10), seen       # the battle read his +10 %
        assert int(mack.strategic_combat_bonus) == 0         # spent, nothing banked

    def test_its_trust_still_follows_the_act(self, world1805, monkeypatch):
        """The morale and trust of a judged attack still land after it, read
        from the same judgement (+3 trust at a score of 90)."""
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        mack.trust.set(50)
        result, _seen = self._mack_attacks_ney(world, monkeypatch)
        assert result.get("success")
        assert mack.trust.value == 53

    def test_with_the_seam_down_it_waits_for_his_next_attack(self, world1805, monkeypatch):
        from backend.ai import feedback as FB
        monkeypatch.setattr(FB, "a_courts_bonus_rides_its_own_act", lambda: False)
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        result, seen = self._mack_attacks_ney(world, monkeypatch)
        assert result.get("success")
        assert seen and seen[0] == ("Mack", 0), seen         # the old order: none in this battle
        assert int(mack.strategic_combat_bonus) == 10        # … banked for the next

    def test_a_refused_attack_banks_nothing_overnight(self, world1805):
        """What an attack refused before its blow leaves standing is cleared at
        the turn's end, with the player's literal buff (GRD-33's rule)."""
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        mack.strategic_combat_bonus = 10
        with _quiet():
            world.advance_turn()
        assert int(mack.strategic_combat_bonus) == 0

    def test_the_seam_is_named_in_the_fr2_list(self):
        from tests._fr2_seams import FR2_SEAMS_BY_ROW
        assert FR2_SEAMS_BY_ROW["BANK"] == [
            "backend.ai.feedback:a_courts_bonus_rides_its_own_act=False"]

    def test_three_quiet_turns_later_his_attack_carries_nothing(self, world1805, monkeypatch):
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        mack.strategic_combat_bonus = 10                     # the old road's leftover
        with _quiet():
            for _ in range(3):
                world.advance_turn()
        _result, seen = self._mack_attacks_ney(world, monkeypatch, score=0)
        assert seen and all(bonus == 0 for name, bonus in seen if name == "Mack"), seen


# ════════════════ WS-R5 — a corps shelled to nothing is destroyed ═════════════

class TestWSR5AShelledCorpsIsDestroyedAtTheField:
    """Find 5. (a) CONFIRMED: an ordered bombardment that emptied a corps (or
    whose stray shells emptied one) sent it down the forced-retreat road —
    `_check_marshal_fate` returns None at strength 0 — so it routed with 0 men
    and stood on the map until the next night's supply sweep removed it as
    "attrition": no grave at the field, no kill counted, a sovereign spared
    the battlefield's fate. (b) REFUTED: the auto-kill counts its attack.
    (c) RULED, REFUTED: the auto-kill skips the "failed to march to the guns"
    trust loss — no battle was fought, so nobody failed to support one."""

    @staticmethod
    def _board(def_str=40):
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.basic()
        art = MarshalFactory.artillery(name="TestArt", location="Belgium", strength=50000,
                                       nation="France")
        world.marshals["TestArt"] = art
        well = world.marshals["Wellington"]
        well.location, well.strength = "Waterloo", def_str
        return world, art, well

    @staticmethod
    def _fire(world, art, target):
        from unittest.mock import patch
        from backend.commands.executor import CommandExecutor
        with _quiet(), patch("random.uniform", return_value=1.0):
            return CommandExecutor()._execute_bombardment(art, target, world, {"world": world})

    def test_a_corps_shelled_to_nothing_is_gone_at_once(self):
        from backend.game_logic import game_end
        world, art, well = self._board()
        before = int(game_end.totals(world)["enemy_corps_destroyed"])
        result = self._fire(world, art, well)
        assert result["success"]
        assert "Wellington" not in world.marshals                 # no 0-man corps on the map
        grave = world.fallen_marshals["Wellington"]
        assert grave["cause"] == "bombardment" and grave["location"] == "Waterloo"
        assert int(game_end.totals(world)["enemy_corps_destroyed"]) == before + 1
        assert "destroyed" in result["message"]

    def test_the_stray_shells_kill_outright_too(self):
        from unittest.mock import patch
        from backend.commands.executor import CommandExecutor
        from tests.conftest import MarshalFactory
        world, art, well = self._board(def_str=60000)
        weak = MarshalFactory.infantry(name="WeakForce", location="Waterloo", strength=50,
                                       nation="Britain")
        world.marshals["WeakForce"] = weak
        with _quiet(), patch("random.uniform", return_value=1.0), \
                patch("random.random", return_value=0.1):
            CommandExecutor()._execute_bombardment(art, well, world, {"world": world})
        assert "WeakForce" not in world.marshals
        assert world.fallen_marshals["WeakForce"]["location"] == "Waterloo"

    def test_its_own_sides_stray_shells_credit_nobody(self):
        """FR2-3 (the session's review): a corps of the battery's OWN court
        emptied by its stray shells is gone at once, credited to nobody, its
        cause friendly fire — not a battlefield death (a sovereign's own guns
        never roll his fate)."""
        from unittest.mock import patch
        from backend.campaign_log import format_event_oneliner
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.game_end import BATTLEFIELD_CAUSES
        from tests.conftest import MarshalFactory
        world, art, well = self._board(def_str=60000)
        ours = MarshalFactory.infantry(name="OurForce", location="Waterloo", strength=50,
                                       nation="France")
        world.marshals["OurForce"] = ours
        with _quiet(), patch("random.uniform", return_value=1.0), \
                patch("random.random", return_value=0.1):
            CommandExecutor()._execute_bombardment(art, well, world, {"world": world})
        assert "OurForce" not in world.marshals
        grave = world.fallen_marshals["OurForce"]
        assert grave["cause"] == "friendly_fire" and grave["location"] == "Waterloo"
        assert "friendly_fire" not in BATTLEFIELD_CAUSES
        row = next(e for e in world.event_log if e.get("type") == "marshal_destroyed"
                   and e.get("marshal") == "OurForce")
        assert row.get("victor") == ""
        line = format_event_oneliner(row, world.player_nation, world)
        assert "own side's stray shells" in line and "by France" not in line, line

    def test_a_sovereign_meets_the_battlefields_fate(self, world1805):
        """The Emperor shelled to nothing at Lorraine (an Austrian battery in
        Franche-Comte, French soil — Swabia is Bavaria's, at peace): killed with his corps
        (the one death roll) or taken by the battery's court — never left at
        0 men on the map, as the rout left him."""
        from tests.conftest import MarshalFactory
        world = _fresh(world1805)
        nap = world.marshals["Napoleon"]
        nap.strength = 40
        smola = MarshalFactory.artillery(name="Smola", location="Franche-Comte", strength=20000,
                                         nation="Austria")
        world.marshals["Smola"] = smola
        self._fire(world, smola, nap)
        killed = "Napoleon" not in world.marshals and \
            world.fallen_marshals.get("Napoleon", {}).get("cause") == "bombardment"
        taken = getattr(nap, "captured_by", "") == "Austria"
        assert killed or taken

    def test_with_the_seam_down_he_routs_with_nothing(self, world1805, monkeypatch):
        from backend.commands import combat_executor as CE
        from tests.conftest import MarshalFactory
        monkeypatch.setattr(CE, "the_guns_kill_outright", lambda: False)
        world = _fresh(world1805)
        nap = world.marshals["Napoleon"]
        nap.strength = 40
        smola = MarshalFactory.artillery(name="Smola", location="Franche-Comte", strength=20000,
                                         nation="Austria")
        world.marshals["Smola"] = smola
        self._fire(world, smola, nap)
        assert "Napoleon" in world.marshals and nap.strength == 0
        assert not getattr(nap, "captured_by", "")

    def test_the_seam_is_named_in_the_fr2_list(self):
        from tests._fr2_seams import FR2_SEAMS_BY_ROW
        assert FR2_SEAMS_BY_ROW["SHELL"] == [
            "backend.commands.combat_executor:the_guns_kill_outright=False"]


# ════════════════ WS-R7 — a remnant is not a corps ════════════════════════════

class TestWSR7ARemnantIsNotACorps:
    """Find 7, CONFIRMED and commoner than filed: a beaten corps routinely
    survives with 50 to 999 men, and every count of "a corps present" read
    only `strength > 0` — so a 600-man remnant added its arm to combined arms,
    gave the "ally next door" bonus, paired as an ally in coordination,
    marched to the guns, counted as overwatch guns and as a flank. One floor,
    1,000 men (`battle_scale.COUNTED_CORPS_MIN_STRENGTH`, the house's number
    for a corps that counts), read at every one of those counts."""

    @staticmethod
    def _board():
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.basic()
        ney = world.marshals["Ney"]                       # cavalry, Belgium
        hussar = MarshalFactory.infantry(name="Remnant", location=ney.location, strength=600,
                                        nation="France")
        world.marshals["Remnant"] = hussar
        return world, ney, hussar

    def test_a_remnant_adds_no_arm_to_combined_arms(self):
        from backend.commands.executor import CommandExecutor
        world, ney, hussar = self._board()
        ce = CommandExecutor()._combat
        assert ce._count_unit_types(ney.location, "France", world) == 1
        hussar.strength = 1000
        assert ce._count_unit_types(ney.location, "France", world) == 2

    def test_a_remnant_next_door_gives_no_bonus(self):
        from backend.commands.executor import CommandExecutor
        world, ney, hussar = self._board()
        hussar.location = "Waterloo"                      # next door to Belgium
        ce = CommandExecutor()._combat
        count, names = ce._count_adjacent_allies(ney.location, "France", world)
        assert "Remnant" not in names
        hussar.strength = 1000
        count, names = ce._count_adjacent_allies(ney.location, "France", world)
        assert "Remnant" in names

    def test_a_remnant_pairs_as_no_ally_but_still_receives(self):
        from backend.commands.executor import CommandExecutor
        world, ney, hussar = self._board()
        ce = CommandExecutor()._combat
        seen = {}
        real = ce._calculate_per_ally_coordination

        def spy(m, allies):
            seen[m.name] = [a.name for a in allies]
            return real(m, allies)

        ce._calculate_per_ally_coordination = spy
        ce._calculate_coordination_context(ney, world)
        assert seen.get("Ney") == []                      # the remnant is no ally of Ney's
        assert seen.get("Remnant") == ["Ney"]             # … and still has Ney beside him

    def test_a_remnants_attack_is_no_flank(self):
        world, ney, hussar = self._board()
        world.record_attack("Remnant", "Netherlands", "Waterloo", "France")
        world.record_attack("Ney", "Belgium", "Waterloo", "France")
        assert [r["attacker"] for r in world.attacks_this_turn.get("Waterloo", [])] == ["Ney"]

    def test_a_remnant_does_not_march_to_the_guns(self):
        from backend.commands.executor import CommandExecutor
        world, ney, hussar = self._board()
        hussar.location = "Netherlands"                   # next door to Waterloo
        ce = CommandExecutor()._combat
        assert not ce._is_reinforcement_eligible(hussar, ney, "Waterloo", "France", world)
        hussar.strength = 1000
        assert ce._is_reinforcement_eligible(hussar, ney, "Waterloo", "France", world)

    def test_with_the_seam_down_every_count_reads_above_zero_again(self, monkeypatch):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import battle_scale as BS
        monkeypatch.setattr(BS, "a_remnant_is_not_a_corps", lambda: False)
        world, ney, hussar = self._board()
        ce = CommandExecutor()._combat
        assert ce._count_unit_types(ney.location, "France", world) == 2
        world.record_attack("Remnant", "Netherlands", "Waterloo", "France")
        assert world.attacks_this_turn.get("Waterloo")

    def test_the_seam_is_named_in_the_fr2_list(self):
        from tests._fr2_seams import FR2_SEAMS_BY_ROW
        assert FR2_SEAMS_BY_ROW["FLOOR"] == [
            "backend.game_logic.battle_scale:a_remnant_is_not_a_corps=False"]


# ════════════════ WS-R3 — the battle report reads what was applied ════════════

def _report_marshals():
    from tests.conftest import MarshalFactory
    atk = MarshalFactory.infantry(name="Lead", strength=40000, nation="France")
    atk.personality = "literal"                   # no nature term unless a test sets one
    dfn = MarshalFactory.enemy(name="Foe", nation="Austria", strength=40000)
    dfn.personality = "literal"
    return atk, dfn


_RESOLVER_ROWS = ("Flanking", "Cavalry counter", "Square formation (vs", "Glorious Charge",
                  "Ranged bombardment", "Terrain (", "Fortification building")


def _product(rows) -> float:
    prod = 1.0
    for r in rows:
        if any(r["label"].startswith(p) for p in _RESOLVER_ROWS):
            continue
        v = int(r["value"]) / 100.0
        prod *= (1.0 + v) if r["type"] == "bonus" else (1.0 - v)
    return prod


class TestWSR3TheReportReadsWhatWasApplied:
    """Find 3, CONFIRMED on all four and swept: the report re-typed its numbers
    instead of reading get_attack_modifier / get_defense_modifier (golden
    rule 1). Iron Resolve's release still printed the defensive stance's
    -10 % it had undone; the jealous lone attack, the jealousy surge and
    cavalry momentum had no row; the strategic bonus was labelled for a forced
    march nothing grants; the ground's share of a cavalryman's dash was printed
    as a factor of its own; the +75 % defence cap never showed; the battle's
    message lines worked out their own sums ("Bold: +25% total" for +27 %).
    Now the modifier functions note each part they apply and the rows and the
    lines read those parts - the arithmetic untouched (the series' arm 0)."""

    @staticmethod
    def _attack(atk, dfn, terrain="plains"):
        from backend.game_logic.battle_report import snapshot_attacker_modifiers
        rows = snapshot_attacker_modifiers(atk, dfn, terrain, 0.0, 0, False)
        ratio = atk.strength / dfn.strength
        applied = atk.get_attack_modifier(ratio, consume=False, terrain=terrain)
        return rows, applied

    def test_iron_resolves_release_shows_no_stance_cost(self):
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        atk.ability = {"name": "Iron Resolve"}
        atk.iron_resolve_stacks = 3
        atk.stance = Stance.DEFENSIVE
        rows, applied = self._attack(atk, dfn)
        labels = {r["label"]: r for r in rows}
        assert "Defensive stance" not in labels           # the release undid it
        assert labels["Iron Resolve (3 stacks)"]["value"] == 24
        assert _product(rows) == pytest.approx(applied, abs=0.005)

    def test_the_jealous_lone_attack_has_its_row(self):
        atk, dfn = _report_marshals()
        atk.jealous_of = "Davout"
        atk._jealousy_solo_attack = True
        rows, applied = self._attack(atk, dfn)
        row = next(r for r in rows if r["label"] == "Jealous lone attack")
        assert (row["value"], row["type"]) == (15, "bonus")
        assert _product(rows) == pytest.approx(applied, abs=0.005)

    def test_the_jealousy_surge_has_its_row_on_both_sides(self):
        from backend.game_logic.battle_report import snapshot_defender_modifiers
        atk, dfn = _report_marshals()
        atk.personality, atk.jealousy_surge_turns = "aggressive", 1
        rows, applied = self._attack(atk, dfn)
        assert any(r["label"] == "Pride after proving himself" and r["value"] == 10 for r in rows)
        assert _product(rows) == pytest.approx(applied, abs=0.01)
        dfn.personality, dfn.jealousy_surge_turns = "cautious", 1
        drows = snapshot_defender_modifiers(dfn, atk, "plains", 0.0)
        assert any(r["label"] == "Pride after proving himself" and r["value"] == 10 for r in drows)

    def test_cavalry_momentum_has_its_row(self):
        from tests.conftest import MarshalFactory
        atk = MarshalFactory.cavalry(name="Horse", strength=12000, nation="France")
        atk.personality = "literal"
        _a, dfn = _report_marshals()
        atk.attacks_this_turn = 1                          # his second charge today
        rows, applied = self._attack(atk, dfn)
        row = next(r for r in rows if r["label"] == "Cavalry momentum (charged again today)")
        assert (row["value"], row["type"]) == (5, "bonus")
        assert not any(r["label"] == "Exhaustion" for r in rows)
        assert _product(rows) == pytest.approx(applied, abs=0.01)

    def test_the_strategic_bonus_names_no_march(self):
        atk, dfn = _report_marshals()
        atk.strategic_combat_bonus = 10
        rows, _applied = self._attack(atk, dfn)
        assert any(r["label"] == "Confidence in his orders" and r["value"] == 10 for r in rows)
        assert not any("march" in r["label"].lower() for r in rows)

    def test_a_bold_mans_terms_multiply_in_the_row(self):
        """Bold +15 %, +5 % in the aggressive stance, +5 % with drill: the
        factor applied is x1.268 - the row says +27 %."""
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        atk.personality, atk.stance, atk.shock_bonus = "aggressive", Stance.AGGRESSIVE, 2
        rows, applied = self._attack(atk, dfn)
        assert next(r for r in rows if r["label"] == "Bold nature")["value"] == 27
        assert _product(rows) == pytest.approx(applied, abs=0.01)

    def test_the_ground_and_the_dash_multiply_to_what_the_charge_carries(self):
        from tests.conftest import MarshalFactory
        atk = MarshalFactory.cavalry(name="Horse", strength=12000, nation="France")
        atk.personality = "aggressive"                    # reckless cavalry: horse + bold
        atk.recklessness = 3                              # +15 % dash, scaled by the ground
        _a, dfn = _report_marshals()
        assert float(atk._get_recklessness_attack_bonus()) == pytest.approx(0.15)
        rows, applied = self._attack(atk, dfn, terrain="plains")
        assert any(r["label"].startswith("Recklessness") for r in rows)
        assert _product(rows) == pytest.approx(applied, abs=0.01)

    def test_a_kitchen_sink_attack_multiplies_to_the_applied_factor(self):
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        atk.stance, atk.shock_bonus, atk.strategic_combat_bonus = Stance.AGGRESSIVE, 1, 5
        atk.personality = "aggressive"
        atk.jealous_of, atk._jealousy_solo_attack = "Ney", True
        atk.sovereign_presence = 1.0
        atk.overwatch_penalty = 0.10
        rows, applied = self._attack(atk, dfn)
        assert _product(rows) == pytest.approx(applied, abs=0.015)

    def test_the_defence_cap_is_shown_when_it_bites(self):
        from backend.game_logic.battle_report import snapshot_defender_modifiers
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        dfn.stance, dfn.defense_bonus = Stance.DEFENSIVE, 0.50
        dfn.personality, dfn.holding_position = "literal", True
        dfn.square_formation = True
        rows = snapshot_defender_modifiers(dfn, atk, "plains", 0.0)
        applied = dfn.get_defense_modifier(dfn.strength < atk.strength, consume=False)
        assert applied == pytest.approx(1.75)
        cap = next(r for r in rows if r["label"].startswith("Defence limit (the bonuses multiply to +"))
        assert cap["type"] == "penalty" and cap["label"].endswith("the limit is +75%)"), cap
        assert "coordination" not in cap["label"]
        assert _product(rows) == pytest.approx(applied, abs=0.01)

    def test_the_defence_cap_says_coordination_fed_it(self):
        """FR2-4 (the session's review): coordination has no row of its own (by
        Phase 7's design — Berthier tells it), so a cap whose total it fed says
        so: the figure is the bonuses together, coordination included."""
        from backend.game_logic.battle_report import snapshot_defender_modifiers
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        dfn.stance, dfn.defense_bonus = Stance.DEFENSIVE, 0.50
        dfn.personality, dfn.holding_position = "literal", True
        dfn.total_coordination_defense_bonus = 0.10
        rows = snapshot_defender_modifiers(dfn, atk, "plains", 0.0)
        cap = next(r for r in rows if r["label"].startswith("Defence limit ("))
        assert ", coordination included; the limit is +75%)" in cap["label"], cap

    def test_the_lines_quote_the_parts(self):
        """The battle's own lines: the Bold total multiplies (+27 %), and a
        defensive stance Iron Resolve undid is not said to hamper the attack."""
        from unittest.mock import patch
        from backend.game_logic.combat import CombatResolver
        from backend.models.marshal import Stance
        atk, dfn = _report_marshals()
        atk.personality, atk.stance, atk.shock_bonus = "aggressive", Stance.AGGRESSIVE, 2
        with _quiet(), patch("random.randint", return_value=4), \
                patch("random.uniform", return_value=1.0):
            result = CombatResolver().resolve_battle(atk, dfn, terrain="plains")
        assert "Bold: +27% total" in str(result)
        atk2, dfn2 = _report_marshals()
        atk2.ability, atk2.iron_resolve_stacks = {"name": "Iron Resolve"}, 3
        atk2.stance = Stance.DEFENSIVE
        with _quiet(), patch("random.randint", return_value=4), \
                patch("random.uniform", return_value=1.0):
            result2 = CombatResolver().resolve_battle(atk2, dfn2, terrain="plains")
        assert "hampers offensive operations" not in str(result2)
        assert "Iron Resolve: +24% attack" in str(result2)


# ════════════════ WS-R1 — a barred crossing names no unseen man's place ═════════

def _channel_board(world1805, seen: bool):
    """Murat at Paris, Moore at London: the Normandy–London crossing is barred
    by the Royal Navy. `seen` puts a French corps in Normandy (London in view)."""
    world = _fresh(world1805)
    murat, moore = world.marshals["Murat"], world.marshals["Moore"]
    murat.location = "Paris"
    near = set(world.regions["London"].adjacent_regions)
    for m in world.marshals.values():
        if m.nation == world.player_nation and m.location in near:
            m.location = "Paris"
    if seen:
        world.marshals["Ney"].location = "Normandy"
    with _quiet():
        world.calculate_visibility()
        world.decay_intel()
    return world, murat, moore


class TestWSR1ABarredCrossingNamesNoUnseenMansPlace:
    """Find 1, CONFIRMED narrower than filed: an ordered charge — and the attack
    road, its sibling — at a man OUT of sight but within reach met the crossing
    refusal "The crossing from Normandy to London is barred…", naming his
    province (or the road toward him); a charge that fell back to an attack on
    his ground and was refused still carried his terrain in its data. REFUTED:
    "already engaged" names only the two commanders, whose names are public."""

    def test_the_charge_answers_the_unseen_answer(self, world1805):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.intel_surfaces import in_sight
        world, murat, moore = _channel_board(world1805, seen=False)
        assert not in_sight(world, world.player_nation, moore)
        with _quiet():
            r = CommandExecutor()._combat._execute_glorious_charge(
                murat, "Moore", world, {"world": world},
                {"action": "charge", "marshal": "Murat", "target": "Moore"})
        assert r.get("fogged") and not r.get("success")
        assert "London" not in r["message"] and "Normandy" not in r["message"]
        assert "terrain" not in r and "charge_blocked_by_terrain" not in r

    def test_the_attack_answers_the_unseen_answer(self, world1805):
        from backend.commands.executor import CommandExecutor
        world, murat, moore = _channel_board(world1805, seen=False)
        with _quiet():
            r = CommandExecutor()._combat._execute_attack(
                murat, "Moore", world, {"world": world},
                command={"action": "attack", "marshal": "Murat", "target": "Moore"})
        assert r.get("fogged") and not r.get("success")
        assert "London" not in r["message"] and "Normandy" not in r["message"]

    def test_a_province_answers_alike_held_or_empty(self, world1805):
        """FR2-1 (the session's review): "attack London" — a PROVINCE — found
        Moore standing in it out of sight, and WS-R1's guard answered "No
        intelligence on Moore's position" where an empty London heard the
        crossing: typing provinces found which held a man unseen, and who. A
        province answers alike, held or empty (UI6-X28's rule)."""
        from backend.commands.executor import CommandExecutor

        def attack_london(empty):
            world, murat, moore = _channel_board(world1805, seen=False)
            if empty:
                moore.location = "Scotland" if "Scotland" in world.regions else "Wales"
            with _quiet():
                return CommandExecutor()._combat._execute_attack(
                    murat, "London", world, {"world": world},
                    command={"action": "attack", "marshal": "Murat", "target": "London"})

        held, empty = attack_london(False), attack_london(True)
        assert "Moore" not in held["message"] and not held.get("fogged"), held["message"]
        assert held["message"] == empty["message"] and "crossing" in held["message"].lower()

    def test_a_man_in_sight_still_hears_the_crossing(self, world1805):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.intel_surfaces import in_sight
        world, murat, moore = _channel_board(world1805, seen=True)
        assert in_sight(world, world.player_nation, moore)
        with _quiet():
            r = CommandExecutor()._combat._execute_attack(
                murat, "Moore", world, {"world": world},
                command={"action": "attack", "marshal": "Murat", "target": "Moore"})
        assert not r.get("success") and "crossing" in r["message"].lower()


# ════════════════ WS-R2 — a foe in sight that no road reaches ══════════════════

class TestWSR2AFoeInSightNoRoadReaches:
    """Find 2, CONFIRMED in the code and reachable only on a map whose
    provinces do not all connect (a mod's island — the mod checker does not
    test connectivity; the shipped map connects all 126): the target finder
    answered none for "no foe in sight" and for "no road reaches the foe in
    sight" alike, so the second said "No foe is in sight"."""

    @staticmethod
    def _island(world1805, monkeypatch):
        world = _fresh(world1805)
        mack = world.marshals["Mack"]
        island = mack.location
        for name in list(world.regions[island].adjacent_regions):
            nb = world.regions[name]
            nb.adjacent_regions = [r for r in nb.adjacent_regions if r != island]
        world.regions[island].adjacent_regions = []
        if hasattr(world, "_distance_cache"):
            world._distance_cache = {}
        monkeypatch.setattr(type(world), "get_visible_enemies",
                            lambda self, nation: [self.marshals["Mack"]])
        return world

    def test_march_on_the_enemy_says_no_road_reaches_him(self, world1805, monkeypatch):
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        world = self._island(world1805, monkeypatch)
        with _quiet():
            parsed = CommandParser(use_real_llm=False).parse(
                "Ney, march on the enemy", {"world": world}, world=world)
            r = CommandExecutor().execute(parsed, {"world": world})
        assert not r.get("success")
        assert "No road reaches Mack" in r["message"], r["message"]
        assert "No foe is in sight" not in r["message"]

    def test_with_no_foe_in_sight_the_words_stand(self, world1805, monkeypatch):
        from backend.commands.executor import CommandExecutor
        from backend.commands.parser import CommandParser
        world = _fresh(world1805)
        monkeypatch.setattr(type(world), "get_visible_enemies", lambda self, nation: [])
        with _quiet():
            parsed = CommandParser(use_real_llm=False).parse(
                "Ney, march on the enemy", {"world": world}, world=world)
            r = CommandExecutor().execute(parsed, {"world": world})
        assert "No foe is in sight" in r["message"], r["message"]


# ════════════════ WS-R6 — refuted: the gate's roads are priced or dead ═════════

class TestWSR6TheGateAfterAnObjectionIsRefuted:
    """Find 6, REFUTED: every answer that can be reached is priced before
    `_execute_post_objection`'s one-action gate (ACH-X10's
    `_unpayable_tactical_answer`, ACH-F3's `strategic_answer_price`); the
    disobey branch it names cannot run — `disobedience.handle_response` never
    sets `disobeyed`; the gate's strategic branch receives no strategic order;
    and every defiant action costs one action (only "garrison" costs two, and
    it is never a defiance). This guard keeps the first of those true."""

    def test_no_answer_ever_disobeys(self):
        import inspect
        from backend.commands import disobedience
        src = inspect.getsource(disobedience)
        assert "'disobeyed': disobeyed" in src or '"disobeyed": disobeyed' in src
        assert "disobeyed = True" not in src

    def test_every_defiant_action_costs_one(self, world1805):
        from backend.commands.defiance import get_defiant_action
        world = _fresh(world1805)
        for m in world.marshals.values():
            if m.nation != world.player_nation:
                continue
            for order in ("attack", "move", "defend", "fortify", "hold", "MOVE_TO", "PURSUE",
                          "HOLD", "SUPPORT", "scout", "drill"):
                action = get_defiant_action(m, order)
                if action:
                    assert world.get_action_cost(action) == 1, (m.name, order, action)


# ════════════════ WS-R8 — one quiet switch, never a swap ═══════════════════════

class TestWSR8NoThreadSwapsTheServersOutput:
    """Find 8, CONFIRMED and wider than filed: the counsel's `_quiet` and the
    read-back's parses silenced their prints with `redirect_stdout`, which
    swaps the PROCESS's stdout. Two such swaps on two threads that enter and
    leave out of order put back the wrong object — every later print of the
    server lost, the server log's tee ended. The counsel runs in a worker
    thread under the Cabinet's preview with no lock; the ready-task list and
    the order road cross it. Now one switch mutes the current request only."""

    @staticmethod
    def _cross(enter):
        """A enters, B enters, A leaves, B leaves — each printing inside."""
        import threading
        a_in, b_in, a_out = threading.Event(), threading.Event(), threading.Event()

        def a():
            with enter():
                a_in.set()
                b_in.wait(5)
                print("A-inside")
            a_out.set()

        def b():
            a_in.wait(5)
            with enter():
                b_in.set()
                a_out.wait(5)
                print("B-inside")

        ta, tb = threading.Thread(target=a), threading.Thread(target=b)
        ta.start(), tb.start()
        ta.join(10), tb.join(10)

    def test_crossed_swaps_lose_the_servers_output(self):
        """The defect, shown with the old tool: afterwards stdout is a dead buffer."""
        import sys
        saved = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream
        try:
            self._cross(lambda: contextlib.redirect_stdout(io.StringIO()))
            left = sys.stdout
        finally:
            sys.stdout = saved
        assert left is not stream

    def test_crossed_quiets_leave_the_output_whole(self):
        import sys
        from backend.utils.quiet import quiet
        saved = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream
        try:
            self._cross(quiet)
            print("after")
        finally:
            sys.stdout = saved
        text = stream.getvalue()
        assert "after" in text
        assert "A-inside" not in text and "B-inside" not in text

    def test_another_threads_print_goes_through_while_one_is_quiet(self):
        import sys
        import threading
        from backend.utils.quiet import quiet
        saved = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream
        inside, done = threading.Event(), threading.Event()

        def muted():
            with quiet():
                inside.set()
                done.wait(5)
                print("muted")

        try:
            t = threading.Thread(target=muted)
            t.start()
            inside.wait(5)
            print("loud")
            done.set()
            t.join(10)
        finally:
            sys.stdout = saved
        assert "loud" in stream.getvalue() and "muted" not in stream.getvalue()

    def test_the_counsel_and_the_read_back_use_the_switch(self):
        """Neither swaps the process's stdout any more; the counsel's quiet
        mutes its own call's prints and leaves the stream as it found it."""
        import inspect
        import sys
        from backend.commands import parse_preview
        from backend.game_logic import counsel
        assert "contextlib.redirect_stdout(" not in inspect.getsource(parse_preview)
        assert "contextlib.redirect_stdout(" not in inspect.getsource(counsel)
        saved = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream
        try:
            assert counsel._quiet(lambda: print("inner") or 7) == 7
            print("after")
        finally:
            sys.stdout = saved
        assert "after" in stream.getvalue() and "inner" not in stream.getvalue()


# ════════════════ the app road (finds 10 and 11) ═══════════════════════════════

@pytest.fixture(scope="module")
def road():
    """The shipped 1805 board behind the real app and the mock parser (the
    pattern of `tests/test_ic8_the_line.py`): `M.world`, the game state's world
    and `M.parser` swapped together and put back."""
    import json
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend.commands import parse_preview as PP
    mp = pytest.MonkeyPatch()
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        mp.delenv(key, raising=False)
    mp.setenv("LLM_MODE", "mock")
    prior = (M.world, M.game_state.get("world"), M.parser)
    with _quiet():
        M._reset_world_state()
    snap = json.dumps(M.world.to_dict(), default=str)
    try:
        with TestClient(M.app) as client:
            yield client, snap
    finally:
        M.world, M.parser = prior[0], prior[2]
        M.game_state["world"] = prior[1]
        PP.invalidate()
        mp.undo()


def _berlin_board(snap):
    """Kutuzov stands on Prussia's soil at Berlin (a court at peace with
    France), last seen there three turns ago, out of sight; Murat at
    Rhineland, two marches off (by Frankfurt)."""
    import json
    import backend.main as M
    from backend.commands import parse_preview as PP
    from backend.commands.parser import CommandParser
    with _quiet():
        world = WorldState.from_dict(json.loads(snap))
        me = world.player_nation
        world.marshals["Kutuzov"].location = "Berlin"
        world.marshals["Murat"].location = "Rhineland"
        world.marshals["Ney"].location = "Frankfurt"
        world.calculate_visibility()
        world.marshals["Ney"].location = "Lorraine"
        for m in world.marshals.values():
            if m.nation == me and m.location in world.regions["Berlin"].adjacent_regions:
                m.location = "Lorraine"
        world.current_turn += 3
        world.calculate_visibility()
        world.decay_intel()
        M._set_active_world(world)
        M.parser = CommandParser(use_real_llm=False)
    PP.invalidate()
    return world


def _post(client, line):
    import random
    random.seed(1805)
    with _quiet():
        return client.post("/command", json={"command": line}).json()


def _preview(client, line):
    with _quiet():
        return client.get("/parse_preview", params={"line": line}).json()


class TestWSR10AttackAndPursueAgreeOnAManLastSeen:
    """Find 10, CONFIRMED and narrow: a man out of sight, last seen on a third
    court's peace soil. "Attack" answered "No intelligence on his position"
    (WS-2's words), decided on his TRUE ground — false for a player who holds
    a sighting, which the one sighting rule (RR6-X3) treats as where he is —
    while "pursue" accepted his chase from there and the read-back read the
    chase. Now the attack is RR6-X3's own answer (the chase, asked first), and
    no unseen answer says "No intelligence" over a sighting. Kept, by UI6-X16's
    rule: a man out of sight but within reach on open ground is met in battle
    by Enter, and the read-back (which never says whether he is within reach)
    reads the chase."""

    def test_attack_and_pursue_place_him_at_berlin(self, road):
        from backend.game_logic.intel_surfaces import in_sight, last_seen_phrase
        client, snap = road
        world = _berlin_board(snap)
        kut = world.marshals["Kutuzov"]
        assert not in_sight(world, world.player_nation, kut)
        assert last_seen_phrase(world, world.player_nation, "Kutuzov") == \
            "was last seen at Berlin 3 turns ago"
        attack = _post(client, "Murat, attack Kutuzov")
        assert attack.get("clarification_kind") == "pursuit_ask", attack.get("message")
        assert attack["message"].startswith("Kutuzov was last seen at Berlin 3 turns ago"),             attack["message"]
        assert "No intelligence" not in attack["message"]
        world = _berlin_board(snap)
        pursue = _post(client, "Murat, pursue Kutuzov")
        assert "Berlin" in str(pursue.get("message")), pursue.get("message")

    def test_the_read_back_says_what_enter_says(self, road):
        client, snap = road
        _berlin_board(snap)
        reading = _preview(client, "Murat, attack Kutuzov")
        assert reading.get("asks_first") is True, reading
        assert int(reading.get("ap", 0)) == 2, reading
        _berlin_board(snap)
        attack = _post(client, "Murat, attack Kutuzov")
        assert attack.get("clarification_kind") == "pursuit_ask"   # asks first, as read

    def test_a_charge_names_the_sighting_never_no_intelligence(self, road):
        """The charge keeps UI6-X16's refusal (no pursuit stands in for a
        charge), now in true words: out of sight, last seen — on Enter and in
        the read-back (which names no place)."""
        client, snap = road
        _berlin_board(snap).marshals["Murat"].recklessness = 2     # the charge is armed
        charge = _post(client, "Murat, charge Kutuzov")
        assert not charge.get("success")
        assert "last seen at Berlin 3 turns ago" in charge["message"], charge["message"]
        assert "No intelligence" not in charge["message"]
        _berlin_board(snap).marshals["Murat"].recklessness = 2
        reading = _preview(client, "Murat, charge Kutuzov")
        assert reading.get("kind") == "refusal", reading
        assert "is out of sight" in reading.get("refusal", ""), reading
        assert "Berlin" not in str(reading)

    def test_a_province_on_peace_soil_answers_as_an_empty_one(self, road):
        """FR2-1's sibling (the session's review): "attack Berlin" — a PROVINCE
        of a court at peace — found Kutuzov in it out of sight and answered
        "Kutuzov is out of sight … last seen at Berlin" (WS-2's answer, now with
        his sighting), where an empty Berlin offers the war on Prussia. The
        held province now answers as the empty one."""
        client, snap = road
        world = _berlin_board(snap)
        assert world.marshals["Kutuzov"].location == "Berlin"
        held = _post(client, "Murat, attack Berlin")
        world = _berlin_board(snap)
        world.marshals["Kutuzov"].location = "Lithuania" if "Lithuania" in world.regions else "Moscow"
        empty = _post(client, "Murat, attack Berlin")
        assert "Kutuzov" not in str(held.get("message")), held.get("message")
        assert held.get("message") == empty.get("message"), (held.get("message"), empty.get("message"))
        assert bool(held.get("war_purpose_popup")) == bool(empty.get("war_purpose_popup")) is True

    def test_with_no_sighting_no_intelligence_stands(self, road):
        client, snap = road
        world = _berlin_board(snap)
        for region in world.intel.values():
            region.known_marshals = [k for k in (region.known_marshals or [])
                                     if k.get("name") != "Kutuzov"]
        from backend.game_logic.intel_surfaces import last_seen
        if last_seen(world, world.player_nation, "Kutuzov") is not None:
            pytest.skip("the board still carries a sighting of Kutuzov")
        attack = _post(client, "Murat, attack Kutuzov")
        assert "No intelligence on Kutuzov's position" in attack["message"], attack["message"]


class TestWSR11TheReadBackScansOncePerBoard:
    """Find 11, CONFIRMED and modest: every read of a line naming an
    out-of-sight foe scanned every province's intel again (golden rule 8).
    Inside the read-back the scan is now kept for the read-back's own state
    key (the epoch bumps after every order), and the second-name patterns are
    built once per roster. The other name lists were already absorbed by
    Python's own pattern cache, and the routed order words are compiled once
    at import."""

    def test_several_reads_of_one_board_scan_once(self, road):
        from backend.game_logic import intel_surfaces as IS
        client, snap = road
        _berlin_board(snap)
        counts = []
        for _ in range(3):
            before = IS.SIGHTINGS_SCANS[0]
            _preview(client, "Murat, pursue Kutuzov")
            counts.append(IS.SIGHTINGS_SCANS[0] - before)
        assert counts[0] >= 1, counts
        assert counts[1] == 0 and counts[2] == 0, counts

    def test_an_order_between_reads_scans_again(self, road):
        from backend.game_logic import intel_surfaces as IS
        client, snap = road
        _berlin_board(snap)
        _preview(client, "Murat, pursue Kutuzov")
        assert _post(client, "status").get("success")      # any order bumps the epoch
        before = IS.SIGHTINGS_SCANS[0]
        _preview(client, "Murat, pursue Kutuzov")
        assert IS.SIGHTINGS_SCANS[0] - before >= 1

    def test_outside_the_read_back_every_call_scans(self, world1805):
        from backend.game_logic import intel_surfaces as IS
        world = _fresh(world1805)
        before = IS.SIGHTINGS_SCANS[0]
        IS.enemy_sightings(world, world.player_nation)
        IS.enemy_sightings(world, world.player_nation)
        assert IS.SIGHTINGS_SCANS[0] - before == 2

    def test_the_second_name_patterns_are_built_once_per_roster(self):
        from backend.ai import second_name as SN
        SN._patterns.cache_clear()
        SN._patterns("Ney|Davout")
        SN._patterns("Ney|Davout")
        info = SN._patterns.cache_info()
        assert info.hits == 1 and info.misses == 1


# ════════════════ WS-R12 — a salvo is a battle only at a battle's scale ════════

class TestWSR12ASalvoIsABattleOnlyAtABattlesScale:
    """Find 12, settled by the rule written before the data
    (`docs/WEAK_SPOT_FINDS_SPEC.md` §3 as amended at FR-2's Plan Mode; the
    record `tools/_fr2_farm_2026_11_23.json`): a bombardment that killed 1,000
    men or more wrote a won battle (+3, capped at 15) at the cost of about
    1.5 % of the battery. Measured on the band's three seeds over forty turns,
    salvos earned France 65 to 409 war-score points per 1,000 of its own dead
    against about 1 for its won battles — a FARM on all three by clause (b).
    The smallest of the three fixes that ends it by the same rule is the
    first: a salvo writes a battle only past 5,000 dead (five times a
    battle's floor). Its dead still count for the war (the blood ledger)."""

    @staticmethod
    def _war_board():
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.basic()
        art = MarshalFactory.artillery(name="TestArt", location="Belgium", strength=50000,
                                       nation="France")
        world.marshals["TestArt"] = art
        well = world.marshals["Wellington"]
        well.location, well.strength = "Waterloo", 60000
        return world, art, well

    @staticmethod
    def _rows(world):
        key = world._make_diplo_key("France", "Britain")
        return list((getattr(world, "battle_records", {}) or {}).get(key, []))

    @staticmethod
    def _dead(world):
        key = world._make_diplo_key("France", "Britain")
        return dict((getattr(world, "campaign_ledgers", {}) or {}).get(key, {}).get("casualties") or {})

    def _fire(self, world, art, well):
        from unittest.mock import patch
        from backend.commands.executor import CommandExecutor
        with _quiet(), patch("random.uniform", return_value=1.0):
            return CommandExecutor()._execute_bombardment(art, well, world, {"world": world})

    def test_a_salvo_of_a_few_thousand_dead_writes_no_battle(self):
        world, art, well = self._war_board()
        assert world.is_at_war("France", "Britain")
        result = self._fire(world, art, well)
        assert result["success"]
        dead = int(result["bombardment_result"]["defender"]["casualties"])
        assert 1000 <= dead < 5000                      # a battle's floor, not a salvo's
        assert self._rows(world) == []
        assert int(self._dead(world).get("Britain", 0)) >= dead   # the war remembers the dead

    def test_with_the_seam_down_the_salvo_wrote_a_won_battle(self, monkeypatch):
        from backend.game_logic import battle_scale as BS
        monkeypatch.setattr(BS, "a_salvo_is_a_battle_only_at_scale", lambda: False)
        world, art, well = self._war_board()
        self._fire(world, art, well)
        rows = self._rows(world)
        assert len(rows) == 1 and rows[0]["winner"] == "France"

    def test_a_battle_scale_salvo_still_writes_its_battle(self):
        from backend.game_logic import battle_scale as BS
        from backend.game_logic.diplomacy import record_battle
        world, art, well = self._war_board()
        record_battle(world, "France", "Britain", "France", 200, BS.CANNONADE_MIN_CASUALTIES,
                      location="Waterloo", cannonade=True)
        assert len(self._rows(world)) == 1

    def test_an_ordinary_battle_is_untouched(self):
        from backend.game_logic.diplomacy import record_battle
        world, art, well = self._war_board()
        record_battle(world, "France", "Britain", "France", 400, 1200, location="Waterloo")
        assert len(self._rows(world)) == 1

    def test_the_seam_is_named_in_the_fr2_list(self):
        from tests._fr2_seams import FR2_SEAMS_BY_ROW
        assert FR2_SEAMS_BY_ROW["SALVO"] == [
            "backend.game_logic.battle_scale:a_salvo_is_a_battle_only_at_scale=False"]

    def test_the_rule_and_its_record(self):
        import json
        record = json.loads((REPO / "tools" / "_fr2_farm_2026_11_23.json").read_text(encoding="utf-8"))
        verdict = record["verdict"]
        assert verdict["farm"] is True and len(verdict["farm_seeds"]) >= 2
        assert verdict["smallest_fix"] == "F1"
        for seed, reading in record["seeds"].items():
            assert reading["b"]["holds"], seed

    def test_the_fixed_trees_record_is_no_farm(self):
        """The re-run on the final tree (the session's review): not a farm on any
        seed — no salvo wrote a battle, and won battles still score."""
        import json
        record = json.loads((REPO / "tools" / "_fr2_farm_fixed_2026_11_23.json")
                            .read_text(encoding="utf-8"))
        assert record["verdict"]["farm"] is False and record["verdict"]["farm_seeds"] == []
        assert set(record["seeds"]) == {"historical", "austerlitz", "marengo"}
        for seed, reading in record["seeds"].items():
            assert reading["b"]["salvo_rows"] == 0 and not reading["b"]["holds"], seed
            assert reading["b"]["battles_won"] >= 1, seed
