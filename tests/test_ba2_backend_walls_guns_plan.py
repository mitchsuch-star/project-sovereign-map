"""The walls, the guns and the plan (row BA, session BA-2) — the backend gate.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15.5.4 (a garrison assault and a
standalone bombardment each get a tableau) and §15.5.5 (the plan of battle:
the `plan` beat of Act I and the "bring" rows of the attack quote). Row BA,
session BA-2.

What is pinned: both payloads ride the field battle's two transports and
carry a script made only of numbers the resolver produced; the fog case of
every beat (the player a party / a watcher at FULL / out of sight); the
tableau is written on a COPY of the logged event; the supporting salvo is a
beat of its battle, never a tableau of its own; the `plan` beat tells the
player's own orders and never the enemy's; `bring_quotes` is pure and offers
exactly the orders the muster ladder says would change the muster; three
seats a side, the sovereign's corps second. Display only (Golden Rule 6): no
assertion here reads a mechanic that the tableau does not already carry.
"""

import copy
import json
import random

import pytest

from backend.commands import order_quotes
from backend.game_logic import siege_diorama
from backend.game_logic.battle_diorama import (
    build_battle_diorama,
    snapshot_pre_battle_strengths,
)
from backend.game_logic.siege_diorama import (
    ASSAULT,
    BOMBARDMENT,
    CAPITULATED,
    HELD,
    STORMED,
    build_assault_diorama,
    build_bombardment_diorama,
    garrison_name,
)
from backend.models.intel import FULL, PARTIAL
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _board():
    from tools.ba1_stage_battles import _board as board
    return board()


def _place(world, **where):
    from tools.ba1_stage_battles import _place as place
    place(world, **where)


def _quiet():
    from tools.ba1_stage_battles import _quiet as quiet
    return quiet()


def _gs(world, executor):
    return {"world": world, "executor": executor}


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


def _beats(payload, kind=None, act=None, side=None):
    out = []
    for block in ((payload or {}).get("script") or {}).get("acts") or []:
        if act and block["act"] != act:
            continue
        out.extend(b for b in block["beats"]
                   if (kind is None or b["kind"] == kind)
                   and (side is None or b["side"] == side))
    return out


def _acts(payload):
    return [block["act"] for block in payload["script"]["acts"]]


def _walk(node, path="payload"):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from _walk(value, f"{path}[{i}]")
    else:
        yield path, node


def _storm(garrison, *, detachment=False, fortified=False, who="Ney",
           at="Bohemia", target="Vienna"):
    """The real attack road against a crafted garrison. -> (world, result)."""
    world, executor = _board()
    region = world.get_region(target)
    region.garrison_strength = garrison
    region.garrison_detachment = detachment
    if fortified:
        region.buildings.append({"type": "fortification", "damaged": False})
    _place(world, **{who: at})
    random.seed(7)
    with _quiet():
        result = executor._execute_attack(
            world.marshals[who], target, world, _gs(world, executor))
    assert result.get("success"), result.get("message")
    return world, result


def _marmont_board(support=None):
    """Marmont (the gunner) commissioned and placed in the Rhineland."""
    from backend.game_logic.recruitment import commission_marshal, find_candidate
    world, executor = _board()
    world.nation_gold["France"] = int(world.nation_gold.get("France", 0)) + 5000
    with _quiet():
        commission_marshal(world, "France", find_candidate(world, "France", "Marmont"))
    _place(world, Marmont="Rhineland")
    if support:
        from tools.ba1_stage_battles import _support
        _support(world, "Marmont", support)
    return world, executor


def _shell(world, executor, battery="Marmont", target="Mack"):
    random.seed(1)
    with _quiet():
        return executor._execute_attack(
            world.marshals[battery], target, world, _gs(world, executor))


# ── hand-made inputs for the builders ────────────────────────────────────

def _facts(**over):
    base = dict(attacker_before=20000, attacker_losses=1000, garrison_before=8000,
                garrison_losses=2000, capitulated=False, defender_nation="Prussia",
                fortified=False, drilled=0, iron=0)
    base.update(over)
    return base


def _assault_result(held=True):
    if held:
        return {"success": True, "events": [{"type": "garrison_assault"}]}
    return {"success": True, "events": [{"type": "garrison_destroyed"},
                                        {"type": "conquest"}]}


def _br(**over):
    base = {
        "attacker": {"name": "Marmont", "casualties": 45, "remaining": 2955, "morale": 90},
        "defender": {"name": "Mack", "casualties": 3180, "remaining": 48820, "morale": 97},
        "collateral": [], "fort_degraded": False, "fort_old": 0, "fort_new": 0,
        "berthier_observation": "The guns speak.",
    }
    for key, value in over.items():
        base[key] = value
    return base


def _salvo(br, region="Waterloo", at="Belgium"):
    return {"success": True, "bombardment_result": br,
            "events": [{"type": "bombardment", "defender_location": region,
                        "attacker_location": at}]}


def _gunners(*extra, battery_nation="France", target_nation="Austria"):
    battery = _mk("Marmont", "Belgium", 3000, nation=battery_nation, artillery=True)
    target = _mk("Mack", "Waterloo", 50000, nation=target_nation)
    world = _world(battery, target, _mk("Watcher", "Paris", 5000), *extra)
    return world, battery, target


# ════════════════════════════════════════════════════════════════════════
# A. The assault
# ════════════════════════════════════════════════════════════════════════

class TestTheAssault:
    def test_held_assault_is_a_tableau_on_both_transports(self):
        world, result = _storm(25000)          # Ney against Vienna's 25,000: it holds
        payload = result["battle_diorama"]
        assert payload["kind"] == ASSAULT and payload["fate"] == HELD
        assert result["events"][0]["diorama"] is payload
        event = result["events"][0]
        assert event["type"] == "garrison_assault"
        (garrison,) = payload["defender"]["contingents"]
        assert garrison["garrison"] is True and garrison["name"] == garrison_name("Vienna")
        assert garrison["status"] == "engaged"
        assert garrison["casualties"] == event["garrison_losses"]
        assert garrison["remaining"] == event["garrison_remaining"]
        assert garrison["committed"] == garrison["remaining"] + garrison["casualties"] == 25000
        (ney,) = payload["attacker"]["contingents"]
        assert ney["status"] == "engaged" and ney["casualties"] == event["attacker_losses"]
        assert ney["committed"] - ney["casualties"] == ney["remaining"]

    def test_held_assault_reads_as_a_failed_assault_with_no_dice(self):
        payload = _storm(25000)[1]["battle_diorama"]
        assert payload["outcome"] == "defender_victory"
        assert payload["player_side"] == "attacker"
        assert payload["banner"] == "THE ASSAULT FAILS"
        assert payload["significant"] is True and payload["dramatic"] is False
        assert _acts(payload) == ["approach", "assault", "crisis", "pursuit"]
        assert "cannonade" not in _acts(payload)
        assert _beats(payload, "wall_holds") and _beats(payload, "dice") == []
        assert _beats(payload, "repulsed")

    def test_the_assault_is_logged_without_its_tableau(self):
        world, result = _storm(25000)
        logged = [e for e in world.event_log if e.get("type") == "garrison_assault"]
        assert logged and not any("diorama" in e for e in world.event_log)

    def test_stormed_wall_falls_and_the_province_is_taken(self):
        _world_, result = _storm(6000)         # a capital's garrison under the 5,000 line
        payload = result["battle_diorama"]
        assert payload["fate"] == STORMED and payload["outcome"] == "attacker_victory"
        (garrison,) = payload["defender"]["contingents"]
        assert garrison["remaining"] == 0 and garrison["status"] == "destroyed"
        assert payload["dramatic"] is True and payload["script"]["form"] == "full"
        assert payload["banner"] == "THE WALLS ARE CARRIED"
        assert _beats(payload, "wall_falls")
        assert payload["region_conquered"] is True and _beats(payload, "province")
        assert "sub_banner" not in payload and _beats(payload, "occupy") == []
        assert result["events"][0]["diorama"] is payload

    def test_stormed_fortified_wall_starts_an_occupation_not_a_conquest(self):
        _world_, result = _storm(6000, fortified=True)
        payload = result["battle_diorama"]
        assert result.get("occupation_started") and payload["fate"] == STORMED
        assert payload["region_conquered"] is False and payload["fortified"] is True
        assert payload["siege_turns"] == 1 and payload["sub_banner"]
        (occupy,) = _beats(payload, "occupy")
        assert occupy["turns"] == 1 and _beats(payload, "province") == []
        assert result["events"][0]["diorama"] is payload

    def test_a_detachment_at_four_to_one_capitulates(self):
        _world_, result = _storm(3000, detachment=True)
        payload = result["battle_diorama"]
        assert payload["fate"] == CAPITULATED
        assert payload["banner"] == "THE GARRISON CAPITULATES"
        assert _beats(payload, "capitulates") and _beats(payload, "wall_falls") == []
        assert payload["outcome"] == "attacker_victory"

    def test_the_enemy_assaults_the_players_garrison(self):
        world, executor = _board()
        _place(world, Mack="Artois")
        random.seed(7)
        with _quiet():
            result = executor._execute_attack(
                world.marshals["Mack"], "Paris", world, _gs(world, executor))
        payload = result["battle_diorama"]
        assert payload["player_side"] == "defender" and payload["fate"] == HELD
        assert payload["banner"] == "THE WALLS HOLD" and payload["register"] == "triumph"
        (walls,) = _beats(payload, "walls")
        assert walls["weight"] == "head"
        assert payload["defender"]["contingents"][0]["nation"] == "France"

    def test_a_third_partys_assault_is_shown_only_at_full_sight(self):
        mack = _mk("Mack", "Belgium", 20000, nation="Austria")
        region_owner = _mk("Blucher", "Rhine", 9000, nation="Prussia")
        world = _world(mack, region_owner, _mk("Ney", "Paris", 5000))
        region = world.get_region("Waterloo")
        world.update_intel_from_transit("Waterloo", 1)
        assert world.get_region_intel("Waterloo").visibility == PARTIAL
        assert build_assault_diorama(world, mack, region, _assault_result(),
                                     _facts(), True) is None
        # and the wrapper leaves a hidden result with no tableau at all
        hidden = siege_diorama.with_assault_tableau(
            world, copy.deepcopy(_assault_result()), mack, region, _facts(), held=True)
        assert "battle_diorama" not in hidden
        world.update_intel_from_battle("Waterloo", 1)
        assert world.get_region_intel("Waterloo").visibility == FULL
        payload = build_assault_diorama(world, mack, region, _assault_result(),
                                        _facts(), True)
        assert payload["player_side"] is None and payload["register"] == "observer"
        assert payload["kind"] == ASSAULT

    def test_the_storming_sides_own_rows_are_told_only_to_the_player(self):
        ney = _mk("Ney", "Belgium", 20000)
        mack = _mk("Mack", "Belgium", 20000, nation="Austria")
        world = _world(ney, mack)
        region = world.get_region("Waterloo")
        # the player storms Prussian walls: the drilled row is told
        ours = build_assault_diorama(world, ney, region, _assault_result(),
                                     _facts(drilled=2), True)
        assert ours["player_side"] == "attacker"
        (drilled,) = _beats(ours, "drilled")
        assert drilled["pct"] == 20
        # the enemy storms the player's walls with a drilled corps: never told
        theirs = build_assault_diorama(world, mack, region, _assault_result(),
                                       _facts(drilled=2, iron_pct=15,
                                              defender_nation="France"), True)
        assert theirs["player_side"] == "defender"
        assert _beats(theirs, "drilled") == [] and _beats(theirs, "ability") == []
        assert "drilled" not in json.dumps(theirs["script"])
        # and a watcher is told neither
        third = _mk("Blucher", "Belgium", 20000, nation="Prussia")
        watched_world = _world(third, mack, _mk("Soult", "Paris", 5000))
        watched_world.update_intel_from_battle("Waterloo", 1)
        watched = build_assault_diorama(watched_world, mack,
                                        watched_world.get_region("Waterloo"),
                                        _assault_result(), _facts(drilled=2), True)
        assert watched["player_side"] is None and _beats(watched, "drilled") == []


# ════════════════════════════════════════════════════════════════════════
# B. The bombardment
# ════════════════════════════════════════════════════════════════════════

class TestTheBombardment:
    def test_a_standalone_salvo_is_the_cannonade_alone(self):
        world, executor = _marmont_board()
        result = _shell(world, executor)
        payload = result["battle_diorama"]
        assert payload["kind"] == BOMBARDMENT and payload["banner"] == "THE GUNS SPEAK"
        assert result["events"][0]["type"] == "bombardment"
        assert result["events"][0]["diorama"] is payload
        assert _acts(payload) == ["cannonade"]
        assert _beats(payload, "battery") and _beats(payload, "dice") == []
        assert payload["significant"] is False and payload["dramatic"] is False
        assert payload["player_side"] == "attacker"

    def test_the_event_log_is_never_written_with_the_tableau(self):
        world, executor = _marmont_board()
        _shell(world, executor)
        logged = [e for e in world.event_log if isinstance(e, dict)]
        assert any(e.get("type") == "bombardment" for e in logged)
        assert not any("diorama" in e for e in logged)
        assert '"script"' not in json.dumps(world.event_log, default=str)
        assert "battle_diorama" not in json.dumps(world.to_dict(), default=str)

    def test_it_opens_by_itself_only_when_it_destroys_or_levels(self):
        world, battery, target = _gunners()
        dead = build_bombardment_diorama(world, battery, target, _salvo(_br(
            defender={"name": "Mack", "casualties": 5000, "remaining": 0, "morale": 0})))
        assert dead["significant"] is True and dead["dramatic"] is True
        assert dead["banner"] == "DESTROYED UNDER THE GUNS" and _beats(dead, "destroyed")
        levelled = build_bombardment_diorama(world, battery, target, _salvo(_br(
            fort_degraded=True, fort_old=20, fort_new=0)))
        assert levelled["significant"] and levelled["dramatic"]
        assert levelled["banner"] == "THE WORKS ARE LEVELLED"
        (works,) = _beats(levelled, "works")
        assert "levelled" in works["text"]
        battered = build_bombardment_diorama(world, battery, target, _salvo(_br(
            fort_degraded=True, fort_old=30, fort_new=20)))
        assert battered["significant"] is False and battered["dramatic"] is False
        assert battered["banner"] == "THE GUNS SPEAK"
        (works,) = _beats(battered, "works")
        assert "30%" in works["text"] and "20%" in works["text"]
        assert (battered["works_old"], battered["works_new"]) == (30, 20)

    def test_a_corps_standing_by_is_a_bystander_on_the_defence(self):
        john = _mk("John", "Waterloo", 15000, nation="Austria")
        lannes = _mk("Lannes", "Waterloo", 12000)
        world, battery, target = _gunners(john, lannes)
        payload = build_bombardment_diorama(world, battery, target, _salvo(_br(
            collateral=[{"name": "John", "casualties": 500},
                        {"name": "Lannes", "casualties": 300, "friendly_fire": True}])))
        by_name = {c["name"]: c for c in payload["defender"]["contingents"]}
        assert by_name["John"]["bystander"] is True
        assert by_name["John"]["friendly_fire"] is False
        assert by_name["Lannes"]["bystander"] is True
        assert by_name["Lannes"]["friendly_fire"] is True
        assert "bystander" not in by_name["Mack"]
        ours = [b for b in _beats(payload, "bystander") if b["actor"] == "Lannes"]
        assert len(ours) == 1 and ours[0]["weight"] == "head" and ours[0]["ours"] is True
        theirs = [b for b in _beats(payload, "bystander") if b["actor"] == "John"]
        assert theirs and theirs[0]["ours"] is False

    def test_a_watched_salvo_tells_the_guns_and_nothing_of_their_side(self):
        john = _mk("John", "Waterloo", 15000, nation="Prussia")
        world, battery, target = _gunners(john, battery_nation="Austria",
                                          target_nation="Prussia")
        br = _br(fort_degraded=True, fort_old=30, fort_new=20,
                 collateral=[{"name": "John", "casualties": 500}])
        world.update_intel_from_transit("Waterloo", 1)
        assert build_bombardment_diorama(world, battery, target, _salvo(br)) is None
        world.update_intel_from_battle("Waterloo", 1)
        payload = build_bombardment_diorama(world, battery, target, _salvo(br))
        assert payload["player_side"] is None
        (battery_beat,) = _beats(payload, "battery")
        assert " from Belgium" not in battery_beat["text"]
        assert "taken" not in battery_beat
        for kind in ("works", "bystander", "shaken"):
            assert _beats(payload, kind) == [], kind

    def test_the_supporting_salvo_has_no_tableau_of_its_own(self):
        world, executor = _marmont_board(support="Ney")
        result = _shell(world, executor, battery="Ney")
        payload = result["battle_diorama"]
        assert "kind" not in payload            # a field battle's payload
        assert result["events"][0]["type"] == "battle"
        (plan,) = _beats(payload, "plan")
        assert plan["guns"] == ["Marmont"]
        # the guns are a beat of the battle, nothing more
        assert _beats(payload, "battery", act="cannonade")
        assert not any("diorama" in e for e in world.event_log if isinstance(e, dict))


# ════════════════════════════════════════════════════════════════════════
# C. Every number an int
# ════════════════════════════════════════════════════════════════════════

class TestEveryNumberAnInt:
    def test_the_assault_payload_is_json_with_no_float(self):
        payload = _storm(25000)[1]["battle_diorama"]
        json.dumps(payload)
        assert [p for p, v in _walk(payload) if isinstance(v, float)] == []
        stormed = _storm(6000, fortified=True)[1]["battle_diorama"]
        json.dumps(stormed)
        assert [p for p, v in _walk(stormed) if isinstance(v, float)] == []

    def test_the_bombardment_payload_is_json_with_no_float(self):
        world, executor = _marmont_board()
        payload = _shell(world, executor)["battle_diorama"]
        json.dumps(payload)
        assert [p for p, v in _walk(payload) if isinstance(v, float)] == []


# ════════════════════════════════════════════════════════════════════════
# E. The plan of battle (Act I of a field battle)
# ════════════════════════════════════════════════════════════════════════

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
           def_reinf=None, facts=None):
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
        region_conquered=False, total_engaged=0, script_facts=facts)


def _pair():
    ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
    mack = _mk("Mack", "Waterloo", 30000, nation="Austria", personality="literal")
    return ney, mack, _world(ney, mack)


def _rows(attacker=(), defender=()):
    return {"modifier_snapshot": {"attacker": list(attacker), "defender": list(defender)}}


def _row(label, value=10, kind="bonus"):
    return {"label": label, "value": value, "type": kind}


_DAVOUT = {"marshal": "Davout", "arrived": True, "has_explicit_order": True,
           "score": 80, "threshold": 55, "origin": "Netherlands"}


class TestThePlanOfBattle:
    def test_a_bare_one_corps_attack_has_no_plan(self):
        ney, mack, world = _pair()
        payload = _build(world, ney, mack, _result(
            outcome="attacker_tactical_victory", dfn=("Mack", 4000, 26000, 60, False)))
        assert _beats(payload, "plan") == []
        heads = [b["kind"] for b in _beats(payload) if b["weight"] == "head"]
        assert heads == ["advance", "dice", "stand"]

    def test_an_attacker_who_is_the_player_has_his_orders_named(self):
        ney, mack, world = _pair()
        davout = _mk("Davout", "Netherlands", 30000)
        world.marshals["Davout"] = davout
        payload = _build(world, ney, mack, _result(), atk_participants=[ney, davout],
                         atk_reinf=[dict(_DAVOUT)])
        (plan,) = _beats(payload, "plan")
        assert plan["side"] == "attacker" and plan["weight"] == "head"
        assert plan["supports"] == ["Davout"] and plan["came"] == 1
        assert "ordered in support" in plan["text"]

    def test_the_flank_the_drill_the_stance_and_the_guns_are_told(self):
        ney, mack, world = _pair()
        rows = _rows(attacker=[_row("Drill training", 20), _row("Aggressive stance", 10)])
        facts = {"flanking_bonus": 1, "flanking_origins": ["A", "B"],
                 "auto_bombardment_results": [{"bombardment_result": {
                     "attacker": {"name": "Marmont", "casualties": 0},
                     "defender": {"name": "Mack", "casualties": 900}}}]}
        payload = _build(world, ney, mack, _result(**rows), facts=facts)
        (plan,) = _beats(payload, "plan")
        assert plan["flank"] == 1 and "+1 on the dice" in plan["text"]
        assert plan["drilled"] == 20 and "a drilled assault" in plan["text"]
        assert plan["stance"] == "aggressive"
        assert plan["guns"] == ["Marmont"]
        assert plan["supports"] == [] and plan["came"] == 0

    def test_an_ordered_corps_that_did_not_come_is_named_but_not_counted(self):
        ney, mack, world = _pair()
        rows = [dict(_DAVOUT, arrived=False, reason="low_score"),
                dict(_DAVOUT, marshal="Lannes")]
        payload = _build(world, ney, mack, _result(), atk_reinf=rows)
        (plan,) = _beats(payload, "plan")
        assert plan["supports"] == ["Davout", "Lannes"] and plan["came"] == 1

    def test_the_enemys_orders_are_never_told(self):
        ney, mack, world = _pair()
        facts = {"flanking_bonus": 1, "flanking_origins": ["A", "B"]}
        rows = _rows(attacker=[_row("Drill training", 20)])
        # the enemy attacks the player's lead, with orders and a drill of his own
        enemy_attack = _build(world, mack, ney, _result(
            victor="Mack", atk=("Mack", 3000, 27000, 80, False),
            dfn=("Ney", 9000, 31000, 40, False), **rows),
            atk_reinf=[dict(_DAVOUT, marshal="Charles")], facts=facts)
        assert _beats(enemy_attack, "plan", side="attacker") == []
        # the player attacks an enemy who is fortified and ordered: not his to read
        enemy_rows = _rows(defender=[_row("Fortified position", 12),
                                     _row("Aggressive stance", 10)])
        ours = _build(world, ney, mack, _result(**enemy_rows),
                      def_reinf=[dict(_DAVOUT, marshal="Charles")])
        assert _beats(ours, "plan", side="defender") == []

    def test_a_defending_player_is_told_his_dispositions_and_not_the_ground_twice(self):
        ney, mack, world = _pair()
        rows = _rows(defender=[_row("Terrain (Hills)", 15), _row("Fortified position", 12)])
        payload = _build(world, mack, ney, _result(
            victor="Mack", atk=("Mack", 3000, 27000, 80, False),
            dfn=("Ney", 9000, 31000, 40, False), **rows))
        (plan,) = _beats(payload, "plan")
        assert plan["side"] == "defender" and plan["weight"] == "head"
        assert plan["text"].startswith("Your dispositions:")
        assert plan["works_pct"] == 12 and plan["terrain_pct"] == 15
        assert _beats(payload, "ground") == []

    def test_ground_the_map_gave_is_no_order_of_his(self):
        ney, mack, world = _pair()
        rows = _rows(defender=[_row("Terrain (Hills)", 15)])
        payload = _build(world, mack, ney, _result(
            victor="Mack", atk=("Mack", 3000, 27000, 80, False),
            dfn=("Ney", 9000, 31000, 40, False), **rows))
        assert _beats(payload, "plan") == []
        (ground,) = _beats(payload, "ground")
        assert "on the heights" in ground["text"]

    def test_a_watched_battle_has_no_plan(self):
        mack = _mk("Mack", "Belgium", 30000, nation="Austria")
        blucher = _mk("Blucher", "Waterloo", 30000, nation="Prussia")
        world = _world(mack, blucher, _mk("Ney", "Paris", 5000))
        world.update_intel_from_battle("Waterloo", 1)
        rows = _rows(attacker=[_row("Drill training", 20)],
                     defender=[_row("Fortified position", 12)])
        payload = _build(world, mack, blucher, _result(
            victor="Mack", atk=("Mack", 3000, 27000, 80, False),
            dfn=("Blucher", 9000, 21000, 22, True), **rows),
            atk_reinf=[dict(_DAVOUT, marshal="Mack2")],
            facts={"flanking_bonus": 1, "flanking_origins": ["A", "B"]})
        assert payload["player_side"] is None
        assert _beats(payload, "plan") == []


# ════════════════════════════════════════════════════════════════════════
# F. bring_quotes
# ════════════════════════════════════════════════════════════════════════

def _brought(world, executor, lead, enemy):
    """The corps the muster ladder says a written order COULD bring, read off
    the ladder as the muster's own hint reads it — from where each stands now.
    `bring_quotes` offers those of them the order really brings."""
    from backend.commands.combat_executor import answering_defender
    combat = executor._combat
    where = answering_defender(world, enemy).location
    beside = set(world.get_region(where).adjacent_regions)
    expected = {}
    for m in world.get_player_marshals():
        if m.name == lead.name or int(m.strength or 0) <= 0 or getattr(m, "captured_by", ""):
            continue
        if m.location != where and m.location not in beside:
            continue
        will, code = combat._muster_reason(m, lead, where, lead.nation, world)
        if not will:
            if code in order_quotes.BROUGHT_BY_AN_ORDER:
                expected[m.name] = code
        elif code != "has_support_order" and m.location != where:
            row = combat._arrival_odds_row(lead, m, where, world, code)
            if (int(row["arrival_odds_with_support"])
                    >= int(row["arrival_odds"]) + order_quotes.BRING_ODDS_GAIN):
                expected[m.name] = code
    return expected


def _send_support(ex, w, name, lead_name):
    """`<name>, support <lead>` sent down the executor's own road; an objection
    the chip said was possible is answered Insist. Returns (result, objected)."""
    parsed = {"command": {"raw_input": f"{name}, support {lead_name}", "marshal": name,
                          "action": "support", "target": lead_name},
              "is_strategic": True, "strategic_type": "SUPPORT"}
    random.seed(11)
    objected = False
    with _quiet():
        result = ex.execute(parsed, {"world": w})
        if getattr(w, "pending_strategic_objection", None) is not None:
            objected = True
            result = ex.handle_objection_response("insist", {"world": w})
    return result, objected


def _asks(m, result) -> bool:
    """The order raised the marshal's question (a road blocked by a corps we
    see): the client stops on "<NAME> REPORTS … Your orders?"."""
    return bool(getattr(m, "pending_interrupt", None)) or bool(result.get("requires_input"))


class TestBringQuotes:
    def test_the_rows_are_the_orders_the_muster_says_would_bring_a_corps(self):
        world, executor = _board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        rows = order_quotes.bring_quotes(world, ney, mack)
        assert isinstance(rows, list) and rows
        for row in rows:
            assert row["kind"] == "support"
            assert row["command"] == f"{row['marshal']}, support Ney"
            m = world.marshals[row["marshal"]]
            assert isinstance(row["ap"], int)
            assert row["ap"] == m.strategic_order_ap(order_type="SUPPORT")
            assert row["why"]
            assert (row["code"] in order_quotes.BROUGHT_BY_AN_ORDER
                    or row["odds_with"] >= row["odds_now"] + order_quotes.BRING_ODDS_GAIN)
            # the odds under the order are real odds, above nothing
            assert 0 < row["odds_with"] <= 100
            assert f"about {row['odds_with']}% under a written order" in row["why"]
        offered = {r["marshal"]: r["code"] for r in rows}
        could = _brought(world, executor, ney, mack)
        assert set(offered) <= set(could) and all(offered[n] == could[n] for n in offered)
        assert offered["Soult"] == "literal_awaits_orders"

    def test_it_offers_exactly_the_orders_that_deliver(self):
        """The oracle is the game. Each corps the ladder says an order could
        bring is SENT that order on a fresh board; it is offered if and only if
        the order is taken without a question and the muster then counts him
        among those who answer the guns, with odds above nothing (and, for a
        man who would have come anyway, fifteen points better). On the opening
        board the order marches Bernadotte to Munich, from whose mountains he
        cannot reach the field — the ladder, read from Franconia, gives him
        47 % — and it stops Murat on "Mack blocks the path at Swabia … Your
        orders?" (his road to Ney runs through Mack). Neither is offered."""
        world, executor = _board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        offered = {r["marshal"] for r in order_quotes.bring_quotes(world, ney, mack)}
        could = _brought(world, executor, ney, mack)
        assert set(could) == {"Murat", "Soult", "Bernadotte"}, "the opening board"
        delivered = set()
        for name in could:
            w, ex = _board()
            lead, foe, m = w.marshals["Ney"], w.marshals["Mack"], w.marshals[name]
            came, code = ex._combat._muster_reason(m, lead, "Swabia", "France", w)
            before = (int(ex._combat._arrival_odds_row(lead, m, "Swabia", w, code)["arrival_odds"])
                      if came else -1)
            result, _objected = _send_support(ex, w, name, "Ney")
            order = m.strategic_order
            assert order is not None and order.command_type == "SUPPORT" and order.target == "Ney"
            asks = _asks(m, result)
            assert asks == (name == "Murat"), f"{name}: the order raised a question = {asks}"
            note = ex._combat._bad_odds_muster_note(lead, foe, w)
            named = name in note.split(" would answer the guns")[0]
            after = (100 if m.location == "Swabia" else int(ex._combat._arrival_odds_row(
                lead, m, "Swabia", w, "has_support_order")["arrival_odds"]))
            if (not asks and named and after > 0
                    and (before < 0 or after >= before + order_quotes.BRING_ODDS_GAIN)):
                delivered.add(name)
        assert offered == delivered == {"Soult"}

    def test_every_leads_chips_deliver_on_the_opening_board(self):
        """The same oracle for EVERY corps that could lead on Mack, not Ney
        alone: each offered order is sent on a fresh board. He takes it at once
        — or objects, as his chip said he might (`objection: possible`), and
        takes it when the Emperor insists — no question is raised, nothing is
        fought, and the lead's muster then counts him as ordered, with odds
        above nothing."""
        world, executor = _board()
        mack = world.marshals["Mack"]
        offers = []
        for lead in world.get_player_marshals():
            if lead.location == mack.location or int(lead.strength or 0) <= 0:
                continue
            for b in order_quotes.bring_quotes(world, lead, mack):
                assert b["ok"] and b["odds_with"] > 0
                offers.append((lead.name, b["marshal"], b["command"], b["objection"]))
        assert len(offers) >= 7
        assert {lead for lead, *_ in offers} >= {"Ney", "Davout", "Lannes", "Murat", "Napoleon"}
        # Murat is brought to Lannes, who stands beside him (no road to walk) —
        # never to Ney or Davout, whose roads from him run through Mack
        assert {lead for lead, name, *_ in offers if name == "Murat"} == {"Lannes"}
        for lead_name, name, command, objection in offers:
            w, ex = _board()
            lead, foe, m = w.marshals[lead_name], w.marshals["Mack"], w.marshals[name]
            men = (int(m.strength), int(foe.strength), foe.location)
            assert command == f"{name}, support {lead_name}"
            result, objected = _send_support(ex, w, name, lead_name)
            assert not objected or objection == "possible", f"{command}: the chip did not say he may object"
            assert not _asks(m, result), f"{command}: the order raised his question"
            order = m.strategic_order
            assert order is not None and order.command_type == "SUPPORT" and order.target == lead_name, command
            assert (int(m.strength), int(foe.strength), foe.location) == men, f"{command}: something was fought"
            came, code = ex._combat._muster_reason(m, lead, "Swabia", "France", w)
            assert came and code == "has_support_order", (command, came, code)
            assert int(ex._combat._arrival_odds_row(lead, m, "Swabia", w, code)["arrival_odds"]) > 0, command

    def test_an_order_that_would_raise_his_question_is_not_offered(self):
        """Mack stands on Murat's road to Ney. The order's first step is then
        no march: Murat asks ("Mack blocks the path at Swabia … Your orders?"),
        and of the four answers ONE keeps the order (Go Around), one sends him
        in alone (Commit the Attack) and two abandon it with the action spent
        (Hold Position, Cancel Order). An order that asks is not an order that
        brings: no row — found by pressing the chip in the real client
        (`tools/ba2_mode_c_walk.py`), where the first oracle, which read the
        muster with the question still standing, had passed it."""
        from backend.commands.strategic import StrategicOrderProcessor
        world, _executor = _board()
        ney, mack, murat = (world.marshals[n] for n in ("Ney", "Mack", "Murat"))
        quote = order_quotes.support_quote(world, murat, ney)
        assert quote["ok"] and quote["road"][0] == "Swabia" and quote["contact"]
        assert order_quotes._first_step_asks(world, quote, ney.location)
        assert "Murat" not in {r["marshal"] for r in order_quotes.bring_quotes(world, ney, mack)}
        # a road that does not pass the foe asks nothing: Soult's to Ney
        soult = order_quotes.support_quote(world, world.marshals["Soult"], ney)
        assert soult["ok"] and not order_quotes._first_step_asks(world, soult, ney.location)
        kept, fought = {}, set()
        for answer in ("attack_anyway", "go_around", "hold_position", "cancel_order"):
            w, ex = _board()
            m, foe = w.marshals["Murat"], w.marshals["Mack"]
            result, _objected = _send_support(ex, w, "Murat", "Ney")
            asked = m.pending_interrupt
            assert _asks(m, result) and asked["interrupt_type"] == "contact_bad_odds"
            assert answer in asked["options"]
            spent, men = int(w.actions_remaining), int(foe.strength)
            with _quiet():
                StrategicOrderProcessor(ex).handle_response(
                    "Murat", "contact_bad_odds", answer, w, {"world": w})
            assert int(w.actions_remaining) == spent, "the action was spent when the order was written"
            order = m.strategic_order
            kept[answer] = order is not None and order.command_type == "SUPPORT"
            if int(foe.strength) != men:
                fought.add(answer)
        assert fought == {"attack_anyway"}
        assert kept["go_around"] and not kept["hold_position"] and not kept["cancel_order"]

    def test_an_order_that_marches_him_out_of_reach_is_not_offered(self):
        """`_stop_this_turn` is the first march of the quote's own road, short
        of a corps we see on it; `_odds_under_the_order` reads the roll from
        there on a COPY — the corps itself is not moved."""
        world, executor = _board()
        ney, bern = world.marshals["Ney"], world.marshals["Bernadotte"]
        quote = order_quotes.support_quote(world, bern, ney)
        assert quote["ok"] and quote["road"][0] == "Munich"
        assert order_quotes._stop_this_turn(world, bern, quote) == "Munich"
        here = bern.location
        from_munich = order_quotes._odds_under_the_order(
            executor._combat, ney, bern, "Munich", "Swabia", world)
        from_here = order_quotes._odds_under_the_order(
            executor._combat, ney, bern, here, "Swabia", world)
        assert bern.location == here == "Franconia"
        assert from_munich == 0 < from_here
        assert not order_quotes._first_step_asks(world, quote, ney.location)
        # a corps we see on the first step of the road: he does not move
        murat = world.marshals["Murat"]
        blocked = order_quotes.support_quote(world, murat, ney)
        assert blocked["road"][0] == "Swabia" and blocked["contact"]
        assert order_quotes._stop_this_turn(world, murat, blocked) == murat.location

    def test_it_is_pure(self):
        world, _executor = _board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        hint = copy.deepcopy(getattr(world, "muster_hint_shown", None))
        random.seed(11)
        state = random.getstate()
        order_quotes.bring_quotes(world, ney, mack)
        assert random.getstate() == state
        assert getattr(world, "muster_hint_shown", None) == hint

    def test_the_promise_holds_the_order_it_quotes_brings_him(self):
        world, executor = _board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        rows = [r for r in order_quotes.bring_quotes(world, ney, mack)
                if r["code"] == "literal_awaits_orders"]
        if not rows:
            pytest.skip("this board offers no literal marshal an order")
        name = rows[0]["marshal"]
        parsed = {"command": {"raw_input": rows[0]["command"], "marshal": name,
                              "action": "support", "target": "Ney"},
                  "is_strategic": True, "strategic_type": "SUPPORT"}
        with _quiet():
            out = executor.execute(parsed, {"world": world})
        assert out.get("success") is True, out.get("message")
        m = world.marshals[name]
        beside = set(world.get_region("Swabia").adjacent_regions) | {"Swabia"}
        assert m.location in beside, f"{name} marched out of reach: {m.location}"
        assert executor._combat._muster_reason(
            m, ney, "Swabia", "France", world) == (True, "has_support_order")
        # and he is no longer offered the order he holds
        assert name not in {r["marshal"] for r in order_quotes.bring_quotes(world, ney, mack)}

    def test_the_attack_quote_carries_the_same_rows(self):
        world, _executor = _board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        quote = order_quotes.attack_quote(world, ney, mack)
        assert quote["kind"] == "attack"
        assert ([r["command"] for r in quote["bring"]]
                == [r["command"] for r in order_quotes.bring_quotes(world, ney, mack)])
        assert quote["bring"]
        support = order_quotes.support_quote(world, world.marshals["Davout"], ney)
        assert support["bring"] == []

    def test_an_enemy_lead_gets_nothing(self):
        world, _executor = _board()
        assert order_quotes.bring_quotes(world, world.marshals["Mack"],
                                         world.marshals["Ney"]) == []


# ════════════════════════════════════════════════════════════════════════
# G. The seats
# ════════════════════════════════════════════════════════════════════════

class TestTheSeats:
    def test_three_seats_a_side_the_rest_in_reserve(self):
        ney, mack, world = _pair()
        extras = [_mk(f"Corps{i}", "Belgium", 9000 - i) for i in range(5)]
        payload = _build(world, ney, mack, _result(), atk_participants=[ney] + extras)
        side = payload["attacker"]
        assert len(side["contingents"]) == 3 and side["reserve_count"] == 3
        assert side["contingents"][0]["name"] == "Ney"

    def test_a_sovereigns_corps_is_seated_second_even_when_smallest(self):
        ney, mack, world = _pair()
        emperor = _mk("Napoleon", "Belgium", 1000, personality="sovereign")
        assert emperor.is_sovereign
        extras = [_mk(f"Corps{i}", "Belgium", 9000 - i) for i in range(4)]
        payload = _build(world, ney, mack, _result(),
                         atk_participants=[ney] + extras + [emperor])
        side = payload["attacker"]
        names = [c["name"] for c in side["contingents"]]
        assert len(names) == 3 and side["reserve_count"] == 3
        assert names[0] == "Ney" and names[1] == "Napoleon"
        assert side["contingents"][1]["sovereign"] is True
