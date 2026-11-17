"""The battle in acts (row BA, session BA-1) — the script's behaviour gate.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15 (the gate record of November 14,
2026; §15.5.2 the contract). The script is display only (Golden Rule 6): these
tests read the response surface and never assert on mechanics.

What is pinned: the script rides the tableau's payload on both transports;
every beat is made from a number the battle produced; an act with no beat is
not played; a beat names only a corps the payload shows (fog is correctness);
an enemy's roll and his road off the field are never printed; every number is
an int; great and dramatic battles are `full`, the rest `brief`.
"""

import json
from unittest.mock import patch

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import battle_script
from backend.game_logic.battle_diorama import (
    build_battle_diorama,
    snapshot_pre_battle_strengths,
)
from backend.game_logic.battle_script import ACTS, build_battle_script, temper_of
from backend.models.intel import FULL, PARTIAL
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _mk(name, location, strength, nation="France", personality="cautious", **kw):
    return Marshal(
        name=name, location=location, strength=int(strength),
        personality=personality, nation=nation, movement_range=1,
        tactical_skill=7, spawn_location=location, **kw)


def _world(*marshals):
    world = WorldState()
    world.marshals = {m.name: m for m in marshals}
    nations = sorted({m.nation for m in marshals})
    for i, a in enumerate(nations):
        for b in nations[i + 1:]:
            world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"
    return world


def _attack(world, attacker, target_name, die=5, variance=0.0):
    executor = CommandExecutor()
    with patch("backend.game_logic.combat.random.randint", return_value=die), \
            patch("backend.game_logic.combat.random.uniform", return_value=variance):
        return executor._execute_attack(attacker, target_name, world, {"world": world})


def _result(outcome="attacker_victory", victor="Ney", atk=("Ney", 3000, 37000, 80, False),
            dfn=("Mack", 9000, 21000, 22, True), **extra):
    result = {
        "outcome": outcome, "victor": victor,
        "attacker": {"name": atk[0], "casualties": atk[1], "remaining": atk[2],
                     "morale": atk[3], "forced_retreat": atk[4]},
        "defender": {"name": dfn[0], "casualties": dfn[1], "remaining": dfn[2],
                     "morale": dfn[3], "forced_retreat": dfn[4]},
        "battle_name": "Battle of Waterloo",
        "battle_report": {"observation": "A clean victory."},
        "attacker_roll": {"natural": 8, "modified": 11, "skill_bonus": 2,
                          "flanking_bonus": 1, "multiplier": 1.125,
                          "is_critical_success": False, "is_critical_failure": False},
        "fortune": {"attacker": 4, "defender": -6},
        "modifier_snapshot": {"attacker": [], "defender": []},
    }
    result.update(extra)
    return result


def _build(world, attacker, defender, battle_result, *, region="Waterloo",
           atk_participants=None, def_participants=None, atk_reinf=None,
           def_reinf=None, conquered=False, total_engaged=0, facts=None):
    atk_participants = atk_participants or [attacker]
    def_participants = def_participants or [defender]
    return build_battle_diorama(
        world=world, attacker=attacker, defender=defender,
        battle_result=battle_result, battle_region=region,
        atk_participants=atk_participants, def_participants=def_participants,
        pre_strengths=snapshot_pre_battle_strengths(atk_participants, def_participants),
        atk_distribution={}, def_distribution={},
        attacker_reinforcements=atk_reinf or [],
        defender_reinforcements=def_reinf or [],
        region_conquered=conquered, total_engaged=total_engaged,
        script_facts=facts)


def _beats(script, act=None, kind=None):
    out = []
    for block in script["acts"]:
        if act and block["act"] != act:
            continue
        out.extend(b for b in block["beats"] if kind is None or b["kind"] == kind)
    return out


def _pair():
    ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
    mack = _mk("Mack", "Waterloo", 30000, nation="Austria", personality="literal")
    return ney, mack, _world(ney, mack)


def _walk(node, path="payload"):
    """Every scalar in a payload, with its path."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from _walk(value, f"{path}[{i}]")
    else:
        yield path, node


# ════════════════════════════════════════════════════════════════════════
# 1. The script rides the payload through the real attack road
# ════════════════════════════════════════════════════════════════════════

class TestTheScriptRidesThePayload:
    def _solo(self):
        ney, mack, world = _pair()
        result = _attack(world, ney, "Mack")
        assert result.get("success"), result.get("message")
        return result

    def test_on_the_command_result_and_on_the_battle_event(self):
        result = self._solo()
        script = result["battle_diorama"]["script"]
        assert script and script["version"] == 1
        assert result["events"][0]["diorama"]["script"] is script

    def test_the_acts_come_in_order_and_an_empty_act_is_not_played(self):
        script = self._solo()["battle_diorama"]["script"]
        played = [block["act"] for block in script["acts"]]
        assert played == [act for act in ACTS if act in played]
        assert all(block["beats"] for block in script["acts"])
        # no guns on this board: the cannonade is not played
        assert "cannonade" not in played

    def test_the_dice_the_battle_rolled_are_the_dice_on_the_table(self):
        result = self._solo()
        (dice,) = _beats(result["battle_diorama"]["script"], "crisis", "dice")
        assert dice["natural"] == 10 and dice["weight"] == "head"   # two fives
        assert dice["modified"] == dice["natural"] + dice["skill"] + dice["flank"]
        assert dice["fortune_attacker"] == 0 and dice["fortune_defender"] == 0
        assert "rolls 10" in dice["text"]

    def test_a_coordinated_battle_tells_who_marched(self):
        probe = WorldState()
        flank = next(n for n in probe.get_region("Waterloo").adjacent_regions
                     if n != "Belgium")
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        davout = _mk("Davout", flank, 30000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, davout, mack)
        with patch("random.randint", return_value=8):   # every corps arrives
            result = _attack(world, ney, "Mack")
        script = result["battle_diorama"]["script"]
        (arrival,) = _beats(script, "approach", "arrive")
        assert arrival["actor"] == "Davout" and arrival["origin"] == flank
        assert arrival["side"] == "attacker" and arrival["concealed"] is False
        assert flank in arrival["text"]
        assert script["tempers"] == {"Ney": "aggressive", "Davout": "cautious",
                                     "Mack": "cautious"}

    def test_the_whole_payload_is_json_and_carries_no_float(self):
        result = self._solo()
        payload = result["battle_diorama"]
        json.dumps(payload)
        floats = [path for path, value in _walk(payload) if isinstance(value, float)]
        assert floats == [], floats

    def test_the_same_battle_writes_the_same_script(self):
        a = self._solo()["battle_diorama"]["script"]
        b = self._solo()["battle_diorama"]["script"]
        assert a == b


# ════════════════════════════════════════════════════════════════════════
# 2. Every beat is made from a number the battle produced
# ════════════════════════════════════════════════════════════════════════

class TestTheApproach:
    def test_the_last_hour_is_the_arrival_rolls_own_margin(self):
        ney, mack, world = _pair()
        davout = _mk("Davout", "Belgium", 30000)
        lannes = _mk("Lannes", "Belgium", 20000, personality="aggressive")
        world.marshals.update({"Davout": davout, "Lannes": lannes})
        rows = [
            {"marshal": "Davout", "arrived": True, "score": 67, "threshold": 65,
             "origin": "Netherlands"},
            {"marshal": "Lannes", "arrived": True, "score": 90, "threshold": 65,
             "origin": "Rhine", "has_explicit_order": True},
        ]
        payload = _build(world, ney, mack, _result(),
                         atk_participants=[ney, davout, lannes], atk_reinf=rows)
        late, ordered = _beats(payload["script"], "approach", "arrive")
        assert late["late"] is True and late["margin"] == 2 and late["weight"] == "head"
        assert "at the last hour (his march: 67, where 65 was needed)" in late["text"]
        assert ordered["late"] is False and ordered["ordered"] is True
        assert ordered["weight"] == "detail" and "as ordered" in ordered["text"]

    def test_the_other_sides_roll_is_never_printed(self):
        ney, mack, world = _pair()
        charles = _mk("Charles", "Waterloo", 25000, nation="Austria")
        world.marshals["Charles"] = charles
        rows = [{"marshal": "Charles", "arrived": True, "score": 66, "threshold": 65,
                 "origin": "Rhine"}]
        payload = _build(world, ney, mack, _result(),
                         def_participants=[mack, charles], def_reinf=rows)
        (arrival,) = _beats(payload["script"], "approach", "arrive")
        assert arrival["late"] is True and arrival["concealed"] is True
        assert "score" not in arrival and "bar" not in arrival and "margin" not in arrival
        assert "66" not in arrival["text"] and "65" not in arrival["text"]

    def test_the_shelf_is_told_with_its_reason_and_its_grudge(self):
        ney, mack, world = _pair()
        bern = _mk("Bernadotte", "Belgium", 20000)
        bern.jealous_of = "Ney"
        world.marshals["Bernadotte"] = bern
        rows = [{"marshal": "Bernadotte", "arrived": False,
                 "reason": "eyes_on_a_crown"}]
        payload = _build(world, ney, mack, _result(), atk_reinf=rows)
        (absent,) = _beats(payload["script"], "approach", "absent")
        assert absent["actor"] == "Bernadotte" and absent["status"] == "refused"
        assert "weighed his own ambitions" in absent["text"]
        assert "He resents Ney's glory." in absent["text"]
        assert absent["weight"] == "head"   # the player's own man who did not come

    def test_the_flank_names_its_provinces_and_its_plus_on_the_dice(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result(), facts={
            "flanking_bonus": 2, "flanking_origins": {"Rhine", "Belgium"}})
        (flank,) = _beats(payload["script"], "approach", "flank")
        assert flank["bonus"] == 2 and flank["origins"] == ["Belgium", "Rhine"]
        assert "2 provinces (Belgium, Rhine): +2 on the dice" in flank["text"]

    def test_no_flank_no_beat(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result(), facts={"flanking_bonus": 0})
        assert _beats(payload["script"], "approach", "flank") == []

    def test_the_ground_and_the_works_are_the_defenders_own_rows(self):
        ney, mack, world = _pair()
        result = _result(modifier_snapshot={"attacker": [], "defender": [
            {"label": "Terrain (Hills)", "value": 15, "type": "bonus"},
            {"label": "Fortified position", "value": 8, "type": "bonus"},
            {"label": "Square formation", "value": 5, "type": "bonus"}]})
        (ground,) = _beats(_build(world, ney, mack, result)["script"], "approach", "ground")
        assert ground["terrain_pct"] == 15 and ground["works_pct"] == 8
        assert ground["square"] is True
        assert ground["text"] == ("Mack stands on the heights (+15%), behind field "
                                  "works (+8%), formed in square.")

    def test_the_emperor_in_person_and_a_dimmed_star(self):
        nap = _mk("Napoleon", "Belgium", 10000, personality="sovereign")
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(nap, mack)
        for label, dimmed in (("The Emperor commands in person", False),
                              ("The Emperor commands in person (his star dims)", True)):
            result = _result(victor="Napoleon", atk=("Napoleon", 900, 9100, 80, False),
                             modifier_snapshot={"attacker": [
                                 {"label": label, "value": 7, "type": "bonus"}],
                                 "defender": []})
            (presence,) = _beats(_build(world, nap, mack, result)["script"],
                                 "approach", "presence")
            assert presence["pct"] == 7 and presence["dimmed"] is dimmed
            assert presence["weight"] == "head" and "+7%" in presence["text"]


class TestTheCannonade:
    def _guns(self, **bombardment):
        base = {"attacker": {"name": "Marmont", "casualties": 180},
                "defender": {"name": "Mack", "casualties": 1240}}
        base.update(bombardment)
        return {"auto_bombardment_results": [{"success": True,
                                              "bombardment_result": base}]}

    def test_a_supporting_battery_fires_first_with_its_own_figures(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result(), facts=self._guns())
        (battery,) = _beats(payload["script"], "cannonade", "battery")
        assert battery["actor"] == "Marmont" and battery["target"] == "Mack"
        assert battery["dealt"] == 1240 and battery["taken"] == 180
        assert "1,240 fall" in battery["text"]

    def test_the_works_the_guns_knocked_down(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result(), facts=self._guns(
            fort_degraded=True, fort_old=12, fort_new=2))
        (battery,) = _beats(payload["script"], "cannonade", "battery")
        assert "from 12% to 2%" in battery["text"]

    def test_guns_on_overwatch_are_the_attackers_own_row(self):
        ney, mack, world = _pair()
        result = _result(modifier_snapshot={"attacker": [
            {"label": "Artillery overwatch", "value": 6, "type": "penalty"}],
            "defender": []})
        payload = _build(world, ney, mack, result, facts={"overwatch_count": 2})
        (overwatch,) = _beats(payload["script"], "cannonade", "overwatch")
        assert overwatch["guns"] == 2 and overwatch["pct"] == 6
        assert "−6% on every attacker" in overwatch["text"]


class TestTheAssault:
    @pytest.mark.parametrize("personality,temper,words", [
        ("aggressive", "aggressive", "goes in at the head of his men"),
        ("cautious", "cautious", "comes on by measured steps"),
        ("literal", "literal", "advances to his mark, as ordered, and no further"),
        ("sovereign", "sovereign", "The line dresses on the Emperor"),
        ("loyalist", "steady", "leads the attack in"),
    ])
    def test_each_temperament_closes_in_its_own_way(self, personality, temper, words):
        lead = _mk("Ney", "Belgium", 40000, personality=personality)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(lead, mack)
        payload = _build(world, lead, mack, _result())
        advance = _beats(payload["script"], "assault", "advance")[0]
        assert advance["temper"] == temper and words in advance["text"]
        assert payload["script"]["tempers"]["Ney"] == temper
        assert temper_of(lead) == temper

    def test_the_personality_figure_is_the_reports_own_row(self):
        ney, mack, world = _pair()
        result = _result(modifier_snapshot={"attacker": [
            {"label": "Personality (aggressive)", "value": 20, "type": "bonus"}],
            "defender": []})
        advance = _beats(_build(world, ney, mack, result)["script"], "assault", "advance")[0]
        assert advance["pct"] == 20 and "(+20%)" in advance["text"]
        assert "aggressive" not in advance["text"]   # no internal key on the face

    @pytest.mark.parametrize("side,label,value,kind,needle", [
        ("attacker", "Iron Resolve (2 stacks)", 16, "ability", "Iron Resolve (+16%)"),
        ("attacker", "Counter-Punch Mastery", 20, "ability", "Counter-Punch Mastery (+20%)"),
        ("attacker", "Drill training", 20, "drilled", "drilled battalions go in as one (+20%)"),
        ("attacker", "Cavalry counter (vs artillery)", 30, "overrun", "rides over the guns"),
        ("attacker", "Glorious Charge", 100, "charge", "double the blood"),
        ("defender", "Reverse Slope Defense", 5, "ability", "Reverse Slope Defense (+5%)"),
        ("defender", "Child of Victory (outnumbered)", 10, "ability", "Child of Victory (+10%)"),
        ("defender", "Habsburg Resolve", 3, "ability", "Habsburg Resolve (+3%)"),
        ("defender", "Immovable (literal hold)", 15, "ability", "exactly where he was posted"),
    ])
    def test_a_named_ability_or_state_is_a_head_beat(self, side, label, value, kind, needle):
        ney, mack, world = _pair()
        rows = {"attacker": [], "defender": []}
        rows[side].append({"label": label, "value": value, "type": "bonus"})
        script = _build(world, ney, mack, _result(modifier_snapshot=rows))["script"]
        (beat,) = _beats(script, "assault", kind)
        assert beat["side"] == side and beat["weight"] == "head"
        assert needle in beat["text"] and beat["pct"] == value

    def test_a_penalty_prints_its_minus(self):
        ney, mack, world = _pair()
        rows = {"attacker": [{"label": "Exhaustion", "value": 10, "type": "penalty"}],
                "defender": [{"label": "Caught drilling", "value": 25, "type": "penalty"}]}
        script = _build(world, ney, mack, _result(modifier_snapshot=rows))["script"]
        (tired,) = _beats(script, "assault", "exhausted")
        (caught,) = _beats(script, "assault", "caught")
        assert "(−10%)" in tired["text"] and tired["penalty"] is True
        assert "caught at drill (−25%)" in caught["text"]

    def test_the_square_against_the_horse(self):
        murat = _mk("Murat", "Belgium", 22000, personality="aggressive", cavalry=True)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(murat, mack)
        rows = {"attacker": [{"label": "Square formation (vs cavalry)", "value": 40,
                              "type": "penalty"}], "defender": []}
        result = _result(victor="Murat", atk=("Murat", 3000, 19000, 70, False),
                         modifier_snapshot=rows)
        (square,) = _beats(_build(world, murat, mack, result)["script"], "assault", "square")
        assert square["text"] == "Mack's squares stand against the horse (−40%)."

    def test_neys_shock_is_named_though_the_report_has_no_row_for_it(self):
        ney, mack, world = _pair()
        ney.ability = {"name": "Bravest of the Brave", "trigger": "when_attacking"}
        result = _result(ability_triggered="Ney's 'Bravest of the Brave' inspires the assault!")
        beats = _beats(_build(world, ney, mack, result)["script"], "assault", "ability")
        assert [b["ability"] for b in beats] == ["Bravest of the Brave"]

    def test_a_row_the_approach_or_the_guns_told_is_not_told_twice(self):
        ney, mack, world = _pair()
        rows = {"attacker": [{"label": "Flanking", "value": 2, "type": "bonus"},
                             {"label": "Artillery overwatch", "value": 3, "type": "penalty"},
                             {"label": "The Emperor commands in person", "value": 10,
                              "type": "bonus"}],
                "defender": [{"label": "Terrain (Forest)", "value": 10, "type": "bonus"},
                             {"label": "Fortified position", "value": 8, "type": "bonus"}]}
        script = _build(world, ney, mack, _result(modifier_snapshot=rows))["script"]
        assert [b["kind"] for b in _beats(script, "assault")] == ["advance", "advance"]


class TestTheCrisis:
    def test_who_broke_and_at_what_morale(self):
        ney, mack, world = _pair()
        mack.retreated_this_turn = True
        (broke,) = _beats(_build(world, ney, mack, _result())["script"], "crisis", "break")
        assert broke["actor"] == "Mack" and broke["how"] == "routed"
        assert broke["morale"] == 22 and "breaks at 22% morale" in broke["text"]

    def test_a_day_that_hangs_says_so(self):
        ney, mack, world = _pair()
        result = _result(outcome="stalemate", victor=None,
                         dfn=("Mack", 4000, 26000, 48, False))
        script = _build(world, ney, mack, result)["script"]
        assert _beats(script, "crisis", "break") == []
        (stand,) = _beats(script, "crisis", "stand")
        assert stand["text"] == "Neither line gives way: the day hangs."

    def test_a_natural_twelve_and_a_natural_two_are_called_out(self):
        ney, mack, world = _pair()
        for natural, flag, needle in ((12, "is_critical_success", "Twelve on the dice"),
                                      (2, "is_critical_failure", "Two on the dice")):
            roll = {"natural": natural, "modified": natural, "skill_bonus": 0,
                    "flanking_bonus": 0, "is_critical_success": False,
                    "is_critical_failure": False}
            roll[flag] = True
            (dice,) = _beats(_build(world, ney, mack, _result(attacker_roll=roll))["script"],
                             "crisis", "dice")
            assert needle in dice["text"]
            assert dice["critical"] == ("success" if natural == 12 else "failure")

    def test_the_dice_carry_each_sides_fortune_and_the_swing(self):
        ney, mack, world = _pair()
        (dice,) = _beats(_build(world, ney, mack, _result())["script"], "crisis", "dice")
        assert (dice["natural"], dice["skill"], dice["flank"], dice["modified"]) == (8, 2, 1, 11)
        assert dice["fortune_attacker"] == 4 and dice["fortune_defender"] == -6
        assert dice["swing"] == 12   # 85% + 2.5 a point, in whole percent, less 100
        assert "rolls 8, +2 for his eye for ground, +1 for the flank: 11." in dice["text"]

    def test_a_line_that_closes_ranks(self):
        ney, mack, world = _pair()
        mack.ability = {"name": "Habsburg Resolve"}
        mack.morale = 20
        result = _result(outcome="attacker_tactical_victory",
                         dfn=("Mack", 6000, 24000, 20, False))
        (holds,) = _beats(_build(world, ney, mack, result)["script"], "crisis", "holds")
        assert holds["morale"] == 20 and "close ranks at 20% morale" in holds["text"]
        # the enemy's line is SEEN to close ranks; the bar it holds to is his own
        assert "floor" not in holds

    def test_our_own_line_that_closes_ranks_carries_its_floor(self):
        """The enemy attacks; the player's defender holds at his ability's bar."""
        ney, mack, world = _pair()
        ney.location, mack.location = "Waterloo", "Belgium"
        ney.ability = {"name": "Habsburg Resolve"}
        ney.morale = 20
        result = _result(outcome="attacker_tactical_victory", victor="Mack",
                         atk=("Mack", 3000, 27000, 80, False),
                         dfn=("Ney", 6000, 34000, 20, False))
        payload = _build(world, mack, ney, result)
        assert payload["player_side"] == "defender"
        (holds,) = _beats(payload["script"], "crisis", "holds")
        assert holds["actor"] == "Ney" and holds["floor"] == 15

    def test_a_corps_beside_the_lead_that_gave_way(self):
        ney, mack, world = _pair()
        charles = _mk("Charles", "Rhine", 25000, nation="Austria")
        charles.retreated_this_turn = True
        world.marshals["Charles"] = charles
        script = _build(world, ney, mack,
                        _result(dfn=("Mack", 9000, 21000, 40, False)),
                        def_participants=[mack, charles])["script"]
        (broke,) = _beats(script, "crisis", "break")
        assert broke["actor"] == "Charles" and broke["text"] == "Charles's corps gives way."


class TestThePursuit:
    def test_the_pursuit_and_the_old_fox(self):
        murat = _mk("Murat", "Belgium", 22000, personality="aggressive", cavalry=True)
        murat.ability = {"name": "First Horseman of Europe"}
        kutuzov = _mk("Kutuzov", "Waterloo", 30000, nation="Russia")
        kutuzov.ability = {"name": "The Old Fox"}
        kutuzov.retreated_this_turn = True
        world = _world(murat, kutuzov)
        result = _result(victor="Murat", atk=("Murat", 2000, 20000, 80, False),
                         dfn=("Kutuzov", 9000, 21000, 22, True), pursuit_damage=2500)
        (pursue,) = _beats(_build(world, murat, kutuzov, result)["script"],
                           "pursuit", "pursue")
        assert pursue["damage"] == 2500 and pursue["halved"] is True
        assert pursue["target"] == "Kutuzov" and pursue["weight"] == "head"
        assert "First Horseman of Europe" in pursue["text"] and "2,500 more" in pursue["text"]
        assert "halved the harvest" in pursue["text"]

    def test_vorwarts_pursues_where_it_is_authored(self):
        """Blücher's ability is not in the 1805 game (§15.4); the beat is the
        number's, wherever the number exists."""
        blucher = _mk("Blucher", "Belgium", 30000, nation="Prussia",
                      personality="aggressive")
        blucher.ability = {"name": "Vorwärts!"}
        ney = _mk("Ney", "Waterloo", 30000)
        ney.retreated_this_turn = True
        world = _world(blucher, ney)
        result = _result(victor="Blucher", atk=("Blucher", 2000, 28000, 80, False),
                         dfn=("Ney", 9000, 21000, 22, True), pursuit_damage=3000)
        (pursue,) = _beats(_build(world, blucher, ney, result)["script"], "pursuit", "pursue")
        assert pursue["damage"] == 3000 and pursue["halved"] is False
        assert "Vorwärts!" in pursue["text"]

    def test_our_own_road_off_the_field_is_named_and_the_enemys_is_not(self):
        ney, mack, world = _pair()
        mack.retreated_this_turn = True
        mack.location = "Rhine"           # where he fled: his intelligence
        script = _build(world, ney, mack, _result())["script"]
        (leave,) = _beats(script, "pursuit", "leave")
        assert leave["actor"] == "Mack" and leave["to"] == ""
        assert leave["text"] == "Mack leaves the field." and "Rhine" not in json.dumps(script)

        ney2 = _mk("Ney", "Netherlands", 40000, personality="aggressive")   # fled there
        ney2.retreated_this_turn = True
        mack2 = _mk("Mack", "Belgium", 30000, nation="Austria")
        world2 = _world(ney2, mack2)
        result = _result(outcome="attacker_victory", victor="Mack",
                         atk=("Mack", 3000, 27000, 80, False),
                         dfn=("Ney", 9000, 31000, 20, True))
        script2 = _build(world2, mack2, ney2, result, region="Waterloo")["script"]
        (ours,) = _beats(script2, "pursuit", "leave")
        assert ours["actor"] == "Ney" and ours["to"] == "Netherlands"
        assert ours["text"] == "Ney falls back on Netherlands."

    def test_a_reinforcer_who_marched_home_after_a_day_not_won(self):
        ney, mack, world = _pair()
        davout = _mk("Davout", "Netherlands", 30000)
        world.marshals["Davout"] = davout
        result = _result(outcome="stalemate", victor=None,
                         dfn=("Mack", 4000, 26000, 48, False))
        script = _build(world, ney, mack, result, atk_participants=[ney, davout],
                        facts={"reinforcer_origin": {"Davout": "Netherlands"}})["script"]
        (leave,) = _beats(script, "pursuit", "leave")
        assert leave["how"] == "withdrew" and leave["to"] == "Netherlands"
        assert leave["text"] == "Davout withdraws to Netherlands after the battle."

    def test_the_advance_and_the_province(self):
        ney, mack, world = _pair()
        mack.retreated_this_turn = True
        script = _build(world, ney, mack, _result(), conquered=True,
                        facts={"advanced_to": "Waterloo"})["script"]
        (advance,) = _beats(script, "pursuit", "advance_to")
        (province,) = _beats(script, "pursuit", "province")
        assert advance["to"] == "Waterloo" and advance["text"] == "Ney advances into Waterloo."
        assert advance["contested"] is False
        assert province["weight"] == "head" and province["text"] == "Waterloo falls to France."

    def test_an_advance_into_a_province_the_enemy_still_holds_says_so(self):
        """A narrow day leaves both armies in the province (the battle's own
        line: "Both armies remain in the field"). Without the clause, "the
        day hangs" followed by "Ney advances into Swabia" read as a
        contradiction — seen on the campaign's opening battle."""
        ney, mack, world = _pair()
        result = _result(outcome="attacker_tactical_victory",
                         dfn=("Mack", 9000, 21000, 28, False))
        script = _build(world, ney, mack, result, facts={"advanced_to": "Waterloo"})["script"]
        (advance,) = _beats(script, "pursuit", "advance_to")
        assert advance["text"] == "Ney advances into Waterloo, where Mack still stands."
        assert advance["contested"] is True
        assert _beats(script, "crisis", "stand")

    def test_battered_works_and_a_free_blow_earned(self):
        ney, mack, world = _pair()
        result = _result(outcome="defender_tactical_victory", victor="Mack",
                         dfn=("Mack", 3000, 27000, 60, False),
                         fortification_degraded=True, fortification_old=12,
                         fortification_new=7, counter_punch_earned=True)
        script = _build(world, ney, mack, result)["script"]
        (works,) = _beats(script, "pursuit", "works")
        assert (works["old"], works["new"]) == (12, 7) and "12% to 7%" in works["text"]
        # The free blow is the ENEMY's here: the game tells that to nobody
        # (its notice goes to the player's own defender), so neither does the script.
        assert _beats(script, "pursuit", "counter_punch") == []

    def test_a_free_blow_is_told_to_our_own_defender(self):
        ney, mack, world = _pair()
        ney.location, mack.location = "Waterloo", "Belgium"
        result = _result(outcome="defender_tactical_victory", victor="Ney",
                         atk=("Mack", 5000, 25000, 60, False),
                         dfn=("Ney", 3000, 37000, 70, False), counter_punch_earned=True)
        (free,) = _beats(_build(world, mack, ney, result)["script"], "pursuit", "counter_punch")
        assert free["actor"] == "Ney" and free["text"] == "Ney has held, and a free blow is his."


# ════════════════════════════════════════════════════════════════════════
# 3. Fog is correctness
# ════════════════════════════════════════════════════════════════════════

class TestFog:
    def _third_party(self, visibility):
        mack = _mk("Mack", "Belgium", 30000, nation="Austria")
        blucher = _mk("Blucher", "Waterloo", 30000, nation="Prussia")
        ney = _mk("Ney", "Rhine", 10000)
        world = _world(mack, blucher, ney)
        if visibility == FULL:
            world.update_intel_from_battle("Waterloo", 1)
        else:
            world.update_intel_from_transit("Waterloo", 1)
        assert world.get_region_intel("Waterloo").visibility == visibility
        result = _result(victor="Mack", atk=("Mack", 3000, 27000, 80, False),
                         dfn=("Blucher", 9000, 21000, 22, True))
        return _build(world, mack, blucher, result)

    def test_a_battle_out_of_sight_has_no_payload_and_so_no_script(self):
        assert self._third_party(PARTIAL) is None

    def test_a_battle_in_full_sight_is_told_without_either_sides_figures(self):
        payload = self._third_party(FULL)
        script = payload["script"]
        assert payload["player_side"] is None and script["acts"]
        for beat in _beats(script, "approach", "arrive"):
            assert "score" not in beat

    def _watched(self, **extra):
        """A battle between two other courts, in full sight, with everything
        a battle report would carry: rows on both armies, a battery off the
        field, both sides' corps marching in, works battered, a free blow."""
        mack = _mk("Mack", "Belgium", 30000, nation="Austria")
        john = _mk("John", "Netherlands", 20000, nation="Austria")
        blucher = _mk("Blucher", "Waterloo", 30000, nation="Prussia", personality="aggressive")
        gneisenau = _mk("Gneisenau", "Rhine", 20000, nation="Prussia")
        world = _world(mack, john, blucher, gneisenau, _mk("Ney", "Paris", 10000))
        world.update_intel_from_battle("Waterloo", 1)
        rows = {
            "attacker": [{"label": "Personality (cautious)", "value": 5, "type": "bonus"},
                         {"label": "Drill training", "value": 20, "type": "bonus"},
                         {"label": "Artillery overwatch", "value": 6, "type": "penalty"}],
            "defender": [{"label": "Terrain (Hills)", "value": 15, "type": "bonus"},
                         {"label": "Fortified position", "value": 12, "type": "bonus"},
                         {"label": "Caught drilling", "value": 20, "type": "penalty"},
                         {"label": "Personality (aggressive)", "value": 10, "type": "bonus"}],
        }
        result = _result(victor="Mack", atk=("Mack", 3000, 27000, 80, False),
                         dfn=("Blucher", 9000, 21000, 22, True),
                         modifier_snapshot=rows, ability_triggered=True,
                         fortification_degraded=True, fortification_old=12,
                         fortification_new=7, counter_punch_earned=True, **extra)
        mack.ability = {"name": "Shock"}
        facts = {
            "flanking_bonus": 1, "flanking_origins": ["Belgium", "Netherlands"],
            "overwatch_count": 2, "reinforcer_origin": {"John": "Netherlands"},
            "auto_bombardment_results": [{"bombardment_result": {
                "attacker": {"name": "Smola", "casualties": 0},
                "defender": {"name": "Blucher", "casualties": 900}}}],
        }
        atk_rows = [{"marshal": "John", "arrived": True, "score": 70, "threshold": 55,
                     "origin": "Netherlands", "has_explicit_order": True}]
        def_rows = [{"marshal": "Gneisenau", "arrived": True, "score": 67, "threshold": 65,
                     "origin": "Rhine"}]
        return _build(world, mack, blucher, result, atk_participants=[mack, john],
                      def_participants=[blucher, gneisenau], atk_reinf=atk_rows,
                      def_reinf=def_rows, facts=facts)

    def test_a_watched_battle_tells_no_row_of_either_army(self):
        payload = self._watched()
        script, text = payload["script"], json.dumps(payload["script"])
        assert payload["player_side"] is None
        # who came, the dice, who broke — told
        assert {b["actor"] for b in _beats(script, "approach", "arrive")} == {"John", "Gneisenau"}
        assert _beats(script, "crisis", "dice") and _beats(script, "crisis", "break")
        assert [b["temper"] for b in _beats(script, "assault", "advance")] == ["cautious", "aggressive"]
        # no modifier row, no tactical state, no battery off the field
        for kind in ("drilled", "caught", "ability", "overwatch", "battery", "works",
                     "counter_punch", "holds", "presence"):
            assert _beats(script, kind=kind) == [], kind
        for needle in ("Smola", "drill", "Fortified", "field works", "+5%", "+10%", "+20%",
                       "12% to 7%", "free blow"):
            assert needle not in text, needle
        # the ground is the map's: the heights, and nothing of the works on them
        (ground,) = _beats(script, "approach", "ground")
        assert "on the heights" in ground["text"] and "works" not in ground["text"]
        assert ground["works_pct"] == 0 and ground["square"] is False

    def test_no_side_of_a_watched_battle_is_told_whence_or_why(self):
        script = self._watched()["script"]
        text = json.dumps(script)
        assert "Netherlands" not in text and "Rhine" not in text
        for beat in _beats(script, "approach", "arrive"):
            assert not ({"origin", "ordered", "score", "bar", "margin"} & set(beat)), beat
            assert "as ordered" not in beat["text"] and " from " not in beat["text"]
        (flank,) = _beats(script, "approach", "flank")
        assert flank["origins"] == [] and flank["text"] == "The attack turns the flank: +1 on the dice."

    def _fought(self, player_attacks: bool):
        """Ney's army and Mack's, each with a corps that marched in under
        orders from a province beside the field."""
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        davout = _mk("Davout", "Netherlands", 30000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        charles = _mk("Charles", "Rhine", 25000, nation="Austria")
        if not player_attacks:
            ney.location, davout.location = "Waterloo", "Rhine"
            mack.location, charles.location = "Belgium", "Netherlands"
        world = _world(ney, davout, mack, charles)
        french = [{"marshal": "Davout", "arrived": True, "score": 80, "threshold": 55,
                   "origin": davout.location, "has_explicit_order": True}]
        austrian = [{"marshal": "Charles", "arrived": True, "score": 67, "threshold": 65,
                     "origin": charles.location, "has_explicit_order": True,
                     "doctrine_arrived": True, "doctrine": "The Hofkriegsrat"}]
        facts = {"flanking_bonus": 1,
                 "flanking_origins": sorted([ney.location if player_attacks else mack.location,
                                             davout.location if player_attacks else charles.location]),
                 "reinforcer_origin": {"Davout": davout.location, "Charles": charles.location}}
        if player_attacks:
            return _build(world, ney, mack, _result(), atk_participants=[ney, davout],
                          def_participants=[mack, charles], atk_reinf=french,
                          def_reinf=austrian, facts=facts)
        result = _result(victor="Mack", atk=("Mack", 3000, 27000, 80, False),
                         dfn=("Ney", 9000, 31000, 40, False))
        return _build(world, mack, ney, result, atk_participants=[mack, charles],
                      def_participants=[ney, davout], atk_reinf=austrian,
                      def_reinf=french, facts=facts)

    @pytest.mark.parametrize("player_attacks", [True, False])
    def test_the_enemys_corps_is_seen_to_come_and_never_whence_or_why(self, player_attacks):
        """He goes back to that province after the battle: naming it would
        put an enemy corps on the map where the fog has none. His orders and
        his court's doctrine are his own too."""
        payload = self._fought(player_attacks)
        arrivals = {b["actor"]: b for b in _beats(payload["script"], "approach", "arrive")}
        ours, theirs = arrivals["Davout"], arrivals["Charles"]
        assert ours["origin"] and ours["ordered"] is True and ours["score"] == 80
        assert f" from {ours['origin']} " in ours["text"] and "as ordered" in ours["text"]
        assert theirs["concealed"] is True
        assert not ({"origin", "ordered", "score", "bar", "margin"} & set(theirs)), theirs
        assert theirs["text"] == "Charles comes up at the last hour."
        assert "Hofkriegsrat" not in json.dumps(payload["script"])

    def test_an_enemy_attacks_flank_is_told_without_its_provinces(self):
        script = self._fought(player_attacks=False)["script"]
        (flank,) = _beats(script, "approach", "flank")
        assert flank["origins"] == [] and flank["bonus"] == 1
        assert flank["text"] == "The attack turns the flank: +1 on the dice."
        ours = self._fought(player_attacks=True)["script"]
        (flank,) = _beats(ours, "approach", "flank")
        assert flank["origins"] == ["Belgium", "Netherlands"]
        assert "from 2 provinces (Belgium, Netherlands)" in flank["text"]

    def test_an_enemy_no_show_is_told_only_where_the_shelf_shows_him(self):
        ney, mack, world = _pair()
        # Vienna, not French soil: the fog question only exists on foreign ground.
        charles = _mk("Charles", "Vienna", 25000, nation="Austria")
        world.marshals["Charles"] = charles
        rows = [{"marshal": "Charles", "arrived": False, "reason": "low_score"}]
        world.update_intel_from_transit("Vienna", 1)
        assert world.get_region_intel("Vienna").visibility == PARTIAL
        hidden = _build(world, ney, mack, _result(), def_reinf=rows)
        assert _beats(hidden["script"], "approach", "absent") == []
        assert "Charles" not in json.dumps(hidden["script"])
        world.update_intel_from_battle("Vienna", 1)
        assert world.get_region_intel("Vienna").visibility == FULL
        seen = _build(world, ney, mack, _result(), def_reinf=rows)
        (absent,) = _beats(seen["script"], "approach", "absent")
        assert absent["actor"] == "Charles" and absent["weight"] == "detail"

    def test_a_beat_never_names_a_corps_the_cap_did_not_seat(self):
        ney, mack, world = _pair()
        extras = []
        for i in range(6):
            m = _mk(f"Corps{i}", "Belgium", 9000 - i)
            m.retreated_this_turn = True
            world.marshals[m.name] = m
            extras.append(m)
        rows = [{"marshal": m.name, "arrived": True, "score": 90, "threshold": 65,
                 "origin": "Rhine"} for m in extras]
        payload = _build(world, ney, mack, _result(),
                         atk_participants=[ney] + extras, atk_reinf=rows)
        seated = {c["name"] for side in ("attacker", "defender")
                  for c in payload[side]["contingents"]}
        # BA-2: three seats a side (the lead and two wings); the other four of
        # the seven stand in reserve, and two of the six arrivals are seated.
        assert payload["attacker"]["reserve_count"] == 4
        named = {b["actor"] for b in _beats(payload["script"]) if b["actor"]}
        assert named <= seated and len(_beats(payload["script"], "approach", "arrive")) == 2
        assert set(payload["script"]["tempers"]) == seated


# ════════════════════════════════════════════════════════════════════════
# 4. The form, and the script's own safety
# ════════════════════════════════════════════════════════════════════════

class TestTheForm:
    def test_a_decisive_or_great_battle_plays_in_full(self):
        ney, mack, world = _pair()
        assert _build(world, ney, mack, _result())["script"]["form"] == "full"
        great = _build(world, ney, mack,
                       _result(outcome="attacker_tactical_victory",
                               dfn=("Mack", 4000, 26000, 60, False)),
                       total_engaged=world.GREAT_BATTLE_THRESHOLD)
        assert great["great_battle"] and great["script"]["form"] == "full"

    def test_an_ordinary_exchange_plays_brief(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack,
                         _result(outcome="attacker_tactical_victory",
                                 dfn=("Mack", 4000, 26000, 60, False)))
        assert payload["significant"] and not payload["dramatic"]
        assert payload["script"]["form"] == "brief"
        # a brief battle still has its head beats: the attack, the dice, the day
        heads = [b["kind"] for b in _beats(payload["script"]) if b["weight"] == "head"]
        assert heads == ["advance", "dice", "stand"]

    def test_a_caller_with_no_facts_still_gets_what_the_result_tells(self):
        ney, mack, world = _pair()
        script = build_battle_script(
            world, _build(world, ney, mack, _result()), ney, mack, _result(), [], [])
        assert [block["act"] for block in script["acts"]] == [
            "approach", "assault", "crisis", "pursuit"]

    def test_a_battle_result_with_nothing_in_it_does_not_raise(self):
        ney, mack, world = _pair()
        bare = {"outcome": "stalemate", "victor": None,
                "attacker": {"name": "Ney"}, "defender": {"name": "Mack"}}
        payload = _build(world, ney, mack, bare)
        assert _beats(payload["script"], "crisis", "dice") == []

    def test_a_script_that_fails_costs_the_battle_nothing(self, monkeypatch):
        def boom(*args, **kwargs):
            raise RuntimeError("the script fell over")

        monkeypatch.setattr(battle_script, "build_battle_script", boom)
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result())
        assert payload is not None and "script" not in payload
        assert payload["attacker"]["contingents"][0]["name"] == "Ney"

    def test_the_module_reads_no_region_table(self):
        """Golden Rule 8: the script is built on every battle of every court."""
        import inspect
        assert "regions.values()" not in inspect.getsource(battle_script)
