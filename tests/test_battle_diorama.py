"""Battle Diorama (row BD) — the contingents[] payload behaviour gate.

Owner: docs/BATTLE_DIORAMA_SPEC.md (scope of record = the eval memo §6,
docs/audits/BATTLE_DIORAMA_EVAL_2026_07_17.md). Covers the eval's one-test
contract: single-army AND multi-army payloads, fog-filtered enemy
contingents (PARTIAL vs FULL), the significance predicate, and the
serialization round-trip through main.py's whitelist.

The payload is display-only (GR6): these tests read the response surface
and never assert on mechanics.
"""

import json
from unittest.mock import patch

from backend.commands.executor import CommandExecutor
from backend.game_logic.battle_diorama import (
    MAX_CONTINGENTS_PER_SIDE,
    build_battle_diorama,
    derive_register,
    marshal_arm,
    snapshot_pre_battle_strengths,
)
from backend.models.intel import FULL, PARTIAL
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _mk(name, location, strength, nation="France", personality="cautious",
        **kw):
    return Marshal(
        name=name, location=location, strength=int(strength),
        personality=personality, nation=nation, movement_range=1,
        tactical_skill=7, spawn_location=location, **kw)


def _world(*marshals):
    world = WorldState()
    world.marshals = {}
    nations = set()
    for m in marshals:
        world.marshals[m.name] = m
        nations.add(m.nation)
    # Every cross-nation pair is at war — the attack path stages a War
    # Purpose declaration otherwise instead of resolving the battle.
    nation_list = sorted(nations)
    for i, a in enumerate(nation_list):
        for b in nation_list[i + 1:]:
            world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"
    return world


def _attack(world, attacker, target_name):
    executor = CommandExecutor()
    game_state = {"world": world}
    with patch('backend.game_logic.combat.random.randint', return_value=5), \
         patch('backend.game_logic.combat.random.uniform', return_value=0.0):
        return executor._execute_attack(
            attacker, target_name, world, game_state)


def _battle_result(outcome="attacker_victory", victor="Ney",
                   atk_cas=3000, atk_rem=37000, def_cas=9000, def_rem=21000,
                   atk_retreat=False, def_retreat=False,
                   name="Battle of Waterloo", observation="A clean victory."):
    return {
        "outcome": outcome,
        "victor": victor,
        "attacker": {"name": "Ney", "casualties": atk_cas,
                     "remaining": atk_rem, "morale": 80,
                     "forced_retreat": atk_retreat},
        "defender": {"name": "Mack", "casualties": def_cas,
                     "remaining": def_rem, "morale": 40,
                     "forced_retreat": def_retreat},
        "battle_name": name,
        "battle_report": {"observation": observation},
    }


def _build(world, attacker, defender, battle_result, *, region="Waterloo",
           atk_participants=None, def_participants=None, pre=None,
           atk_dist=None, def_dist=None, atk_reinf=None, def_reinf=None,
           conquered=False, total_engaged=0):
    atk_participants = atk_participants or [attacker]
    def_participants = def_participants or [defender]
    if pre is None:
        pre = snapshot_pre_battle_strengths(atk_participants, def_participants)
    return build_battle_diorama(
        world=world, attacker=attacker, defender=defender,
        battle_result=battle_result, battle_region=region,
        atk_participants=atk_participants, def_participants=def_participants,
        pre_strengths=pre,
        atk_distribution=atk_dist or {}, def_distribution=def_dist or {},
        attacker_reinforcements=atk_reinf or [],
        defender_reinforcements=def_reinf or [],
        region_conquered=conquered, total_engaged=total_engaged)


# ════════════════════════════════════════════════════════════════════════
# 1. Single-army payload through the real attack path
# ════════════════════════════════════════════════════════════════════════

class TestSoloBattlePayload:
    def _run(self):
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        mack = _mk("Mack", "Waterloo", 20000, nation="Austria")
        world = _world(ney, mack)
        result = _attack(world, ney, "Mack")
        assert result.get("success"), result.get("message")
        return result

    def test_payload_present_on_result_and_event(self):
        result = self._run()
        payload = result.get("battle_diorama")
        assert payload, "player attack must carry a diorama payload"
        assert result["events"][0].get("diorama") is payload

    def test_single_contingent_each_side(self):
        payload = self._run()["battle_diorama"]
        assert len(payload["attacker"]["contingents"]) == 1
        assert len(payload["defender"]["contingents"]) == 1
        lead = payload["attacker"]["contingents"][0]
        assert lead["name"] == "Ney"
        assert lead["lead"] is True
        assert lead["nation"] == "France"

    def test_committed_is_pre_battle_strength(self):
        result = self._run()
        payload = result["battle_diorama"]
        assert payload["attacker"]["contingents"][0]["committed"] == 40000
        assert payload["defender"]["contingents"][0]["committed"] == 20000

    def test_numbers_match_the_event_surface(self):
        # Shown = the numbers every other surface already prints.
        result = self._run()
        payload = result["battle_diorama"]
        event = result["events"][0]
        atk = payload["attacker"]["contingents"][0]
        assert atk["casualties"] == event["attacker"]["casualties"]
        assert atk["remaining"] == event["attacker"]["remaining"]

    def test_player_side_and_register(self):
        payload = self._run()["battle_diorama"]
        assert payload["player_side"] == "attacker"
        assert payload["register"] in ("triumph", "defeat", "grim")
        assert payload["significant"] is True  # player involved

    def test_battle_name_engraved(self):
        payload = self._run()["battle_diorama"]
        assert payload["battle_name"].startswith("Battle of")

    def test_payload_json_serializable(self):
        payload = self._run()["battle_diorama"]
        json.dumps(payload)  # raises on any leaked object


class TestDefensiveBattlePayload:
    def test_enemy_attack_frames_player_as_defender(self):
        mack = _mk("Mack", "Belgium", 40000, nation="Austria")
        ney = _mk("Ney", "Waterloo", 20000)
        world = _world(mack, ney)
        result = _attack(world, mack, "Ney")
        assert result.get("success")
        payload = result.get("battle_diorama")
        assert payload
        assert payload["player_side"] == "defender"
        # The defender's-eye register: never "observer" for our own line.
        assert payload["register"] in ("triumph", "defeat", "grim")


# ════════════════════════════════════════════════════════════════════════
# 2. Multi-army: contingents, distribution, cap
# ════════════════════════════════════════════════════════════════════════

class TestCoordinatedBattlePayload:
    def _run(self):
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        davout = _mk("Davout", "Belgium", 30000)
        mack = _mk("Mack", "Waterloo", 35000, nation="Austria")
        world = _world(ney, davout, mack)
        result = _attack(world, ney, "Mack")
        assert result.get("success"), result.get("message")
        return result

    def test_both_corps_present_lead_first(self):
        payload = self._run()["battle_diorama"]
        names = [c["name"] for c in payload["attacker"]["contingents"]]
        assert names[0] == "Ney"
        assert "Davout" in names

    def test_per_corps_casualties_sum_to_side_total(self):
        result = self._run()
        payload = result["battle_diorama"]
        event = result["events"][0]
        side_sum = sum(
            c["casualties"] for c in payload["attacker"]["contingents"])
        assert side_sum == payload["attacker"]["casualties_total"]
        assert side_sum == event["attacker"]["casualties"]

    def test_committed_totals_are_pre_battle(self):
        payload = self._run()["battle_diorama"]
        assert payload["attacker"]["committed_total"] == 70000

    def test_marching_ally_status_reinforced(self):
        # Davout stood BESIDE Ney and marched to the guns through the real
        # arrival system — the tableau says "reinforced", not "engaged".
        payload = self._run()["battle_diorama"]
        davout = next(c for c in payload["attacker"]["contingents"]
                      if c["name"] == "Davout")
        assert davout["status"] == "reinforced"
        assert davout["lead"] is False

    def test_defender_side_ally_on_the_field_is_engaged(self):
        # An ally already standing ON the battle region fought where it
        # stood — that is the "engaged" status.
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        hohenlohe = _mk("Hohenlohe", "Waterloo", 15000, nation="Austria")
        world = _world(ney, mack, hohenlohe)
        result = _attack(world, ney, "Mack")
        assert result.get("success")
        payload = result["battle_diorama"]
        ally = next(c for c in payload["defender"]["contingents"]
                    if c["name"] == "Hohenlohe")
        assert ally["status"] == "engaged"


class TestContingentCap:
    def test_cap_and_reserve_tail(self):
        lead = _mk("Ney", "Waterloo", 30000)
        extras = [_mk(f"Corps{i}", "Waterloo", 10000 + i) for i in range(5)]
        mack = _mk("Mack", "Waterloo", 20000, nation="Austria")
        world = _world(lead, mack, *extras)
        payload = _build(
            world, lead, mack, _battle_result(),
            atk_participants=[lead] + extras)
        side = payload["attacker"]
        assert len(side["contingents"]) == MAX_CONTINGENTS_PER_SIDE
        assert side["reserve_count"] == 2
        # The lead is never capped out.
        assert side["contingents"][0]["name"] == "Ney"
        # Totals still count EVERY corps, shown or reserved.
        assert side["committed_total"] == 30000 + sum(
            10000 + i for i in range(5))


# ════════════════════════════════════════════════════════════════════════
# 3. Status vocabulary
# ════════════════════════════════════════════════════════════════════════

class TestStatuses:
    def test_routed_primary_pair_only(self):
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 12000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(
            world, ney, mack,
            _battle_result(def_retreat=True, def_cas=6000, def_rem=6000))
        assert payload["defender"]["contingents"][0]["status"] == "routed"

    def test_destroyed_when_nothing_remains(self):
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 8000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(
            world, ney, mack,
            _battle_result(def_cas=8000, def_rem=0))
        assert payload["defender"]["contingents"][0]["status"] == "destroyed"
        assert payload["defender"]["contingents"][0]["remaining"] == 0

    def test_reinforced_status_from_arrival_record(self):
        ney = _mk("Ney", "Waterloo", 40000)
        lannes = _mk("Lannes", "Waterloo", 25000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, lannes, mack)
        payload = _build(
            world, ney, mack, _battle_result(),
            atk_participants=[ney, lannes],
            atk_dist={"Ney": 2000, "Lannes": 1000},
            atk_reinf=[{"marshal": "Lannes", "arrived": True}])
        lan = next(c for c in payload["attacker"]["contingents"]
                   if c["name"] == "Lannes")
        assert lan["status"] == "reinforced"
        assert lan["casualties"] == 1000


class TestNoShowShelf:
    def test_player_no_show_with_reason_and_grudge(self):
        ney = _mk("Ney", "Waterloo", 40000)
        bernadotte = _mk("Bernadotte", "Belgium", 20000)
        bernadotte.jealous_of = "Davout"
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, bernadotte, mack)
        payload = _build(
            world, ney, mack, _battle_result(),
            atk_reinf=[{"marshal": "Bernadotte", "arrived": False,
                        "reason": "eyes_on_a_crown"}])
        shelf = [c for c in payload["attacker"]["contingents"]
                 if c["status"] == "failed_arrive"]
        assert len(shelf) == 1
        assert shelf[0]["name"] == "Bernadotte"
        assert shelf[0]["absence_reason"] == "weighed his own ambitions"
        # Eval §3: the grudge EXPLAINS the gap — it is never minted by it.
        assert shelf[0]["grudge"] == "He resents Davout's glory."

    def test_literal_no_show_reason(self):
        ney = _mk("Ney", "Waterloo", 40000)
        soult = _mk("Soult", "Belgium", 20000, personality="literal")
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, soult, mack)
        payload = _build(
            world, ney, mack, _battle_result(),
            atk_reinf=[{"marshal": "Soult", "arrived": False,
                        "reason": "literal_personality"}])
        shelf = [c for c in payload["attacker"]["contingents"]
                 if c["status"] == "failed_arrive"]
        assert shelf[0]["absence_reason"] == "awaits explicit orders"

    def test_enemy_grudge_never_leaks(self):
        # Enemy jealousy runs on a faction proxy — a per-marshal grudge
        # line for an enemy corps would leak internals the player may
        # not read.
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        mack.jealous_of = "ArchdukeCharles"
        world = _world(ney, mack)
        payload = _build(world, ney, mack, _battle_result())
        assert "grudge" not in payload["defender"]["contingents"][0]


# ════════════════════════════════════════════════════════════════════════
# 4. Fog of war (the eval's de-risk must #1)
# ════════════════════════════════════════════════════════════════════════

class TestFogFiltering:
    def _third_party_world(self):
        # Austria attacks Britain — France merely watches.
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        moore = _mk("Moore", "Waterloo", 20000, nation="Britain")
        return _world(mack, moore), mack, moore

    def test_third_party_battle_hidden_below_full(self):
        world, mack, moore = self._third_party_world()
        world.update_intel_from_transit("Waterloo", 1)  # PARTIAL only
        assert world.get_region_intel("Waterloo").visibility == PARTIAL
        payload = _build(world, mack, moore, _battle_result(
            victor="Mack", name="Battle of Waterloo"))
        assert payload is None

    def test_third_party_battle_visible_at_full(self):
        world, mack, moore = self._third_party_world()
        world.update_intel_from_battle("Waterloo", 1)
        assert world.get_region_intel("Waterloo").visibility == FULL
        payload = _build(world, mack, moore, _battle_result(victor="Mack"))
        assert payload is not None
        assert payload["player_side"] is None
        assert payload["register"] == "observer"

    def test_enemy_no_show_needs_full_visibility_of_its_region(self):
        # A corps that never marched reveals its REGION, not the battle:
        # below FULL it must not appear on the shelf.
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        # Vienna, not Belgium: a no-show on FRANCE'S OWN soil is visible by
        # definition — the fog question only exists on foreign ground.
        kutuzov = _mk("Kutuzov", "Vienna", 25000, nation="Austria")
        world = _world(ney, mack, kutuzov)
        reinf = [{"marshal": "Kutuzov", "arrived": False,
                  "reason": "arrival_failed"}]

        world.update_intel_from_transit("Vienna", 1)  # PARTIAL
        assert world.get_region_intel("Vienna").visibility == PARTIAL
        hidden = _build(world, ney, mack, _battle_result(),
                        def_reinf=reinf)
        assert all(c["name"] != "Kutuzov"
                   for c in hidden["defender"]["contingents"])

        world.update_intel_from_battle("Vienna", 1)  # FULL
        shown = _build(world, ney, mack, _battle_result(),
                       def_reinf=reinf)
        assert any(c["name"] == "Kutuzov" and c["status"] == "failed_arrive"
                   for c in shown["defender"]["contingents"])

    def test_player_no_show_always_visible(self):
        # The Bernadotte drama is a player-side read — no fog on our own.
        ney = _mk("Ney", "Waterloo", 40000)
        grouchy = _mk("Grouchy", "Belgium", 20000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, grouchy, mack)
        payload = _build(
            world, ney, mack, _battle_result(),
            atk_reinf=[{"marshal": "Grouchy", "arrived": False,
                        "reason": "arrival_failed"}])
        assert any(c["name"] == "Grouchy"
                   for c in payload["attacker"]["contingents"])


# ════════════════════════════════════════════════════════════════════════
# 5. Significance + drama predicates
# ════════════════════════════════════════════════════════════════════════

class TestSignificance:
    def _third_party(self, **kw):
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        moore = _mk("Moore", "Waterloo", 20000, nation="Britain")
        world = _world(mack, moore)
        world.update_intel_from_battle("Waterloo", 1)
        return _build(world, mack, moore, _battle_result(**kw)), world

    def test_decisive_third_party_significant(self):
        payload, _ = self._third_party(outcome="attacker_victory",
                                       victor="Mack")
        assert payload["significant"] is True

    def test_routine_third_party_not_significant(self):
        payload, _ = self._third_party(
            outcome="attacker_tactical_victory", victor="Mack",
            def_retreat=False, def_rem=15000, def_cas=5000)
        assert payload["significant"] is False

    def test_player_battle_always_significant(self):
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(world, ney, mack, _battle_result(
            outcome="attacker_tactical_victory", def_rem=15000))
        assert payload["significant"] is True

    def test_great_battle_flag(self):
        ney = _mk("Ney", "Waterloo", 90000)
        mack = _mk("Mack", "Waterloo", 80000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(
            world, ney, mack, _battle_result(
                outcome="stalemate", victor=None),
            total_engaged=int(WorldState.GREAT_BATTLE_THRESHOLD))
        assert payload["great_battle"] is True
        assert payload["significant"] is True


class TestDrama:
    """`dramatic` gates the UNINVITED surface (enemy-phase auto-play):
    routine incoming raids stay one click away; broken lines, falls of
    provinces, decisive fields, and massed corps seize the screen."""

    def _base(self, **kw):
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, mack)
        conquered = kw.pop("conquered", False)
        return _build(world, ney, mack, _battle_result(**kw),
                      conquered=conquered)

    def test_routine_tactical_exchange_not_dramatic(self):
        payload = self._base(outcome="attacker_tactical_victory",
                             def_rem=15000, def_cas=5000)
        assert payload["dramatic"] is False

    def test_decisive_is_dramatic(self):
        payload = self._base(outcome="attacker_victory")
        assert payload["dramatic"] is True

    def test_rout_is_dramatic(self):
        payload = self._base(outcome="attacker_tactical_victory",
                             def_retreat=True, def_rem=15000)
        assert payload["dramatic"] is True

    def test_conquest_is_dramatic(self):
        payload = self._base(outcome="attacker_tactical_victory",
                             def_rem=15000, conquered=True)
        assert payload["dramatic"] is True

    def test_multi_corps_is_dramatic(self):
        ney = _mk("Ney", "Waterloo", 40000)
        davout = _mk("Davout", "Waterloo", 30000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, davout, mack)
        payload = _build(
            world, ney, mack,
            _battle_result(outcome="attacker_tactical_victory",
                           def_rem=15000),
            atk_participants=[ney, davout],
            atk_dist={"Ney": 2000, "Davout": 1000})
        assert payload["dramatic"] is True


class TestRegister:
    def test_matrix(self):
        assert derive_register("attacker", "attacker_victory") == "triumph"
        assert derive_register("attacker", "defender_victory") == "defeat"
        assert derive_register("defender", "attacker_victory") == "defeat"
        assert derive_register("defender", "defender_tactical_victory") == "triumph"
        assert derive_register("attacker", "stalemate") == "grim"
        assert derive_register("defender", "mutual_destruction") == "grim"
        assert derive_register(None, "attacker_victory") == "observer"


# ════════════════════════════════════════════════════════════════════════
# 6. Display flourishes
# ════════════════════════════════════════════════════════════════════════

class TestFlourishes:
    def test_arm_derivation_matches_map_summary(self):
        inf = _mk("A", "Paris", 1000)
        cav = _mk("B", "Paris", 1000, cavalry=True)
        art = _mk("C", "Paris", 1000, artillery=True)
        assert marshal_arm(inf) == "infantry"
        assert marshal_arm(cav) == "cavalry"
        assert marshal_arm(art) == "artillery"

    def test_crowned_laurel_rides_the_contingent(self):
        ney = _mk("Ney", "Waterloo", 40000)
        ney.glory_crowned = True
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(world, ney, mack, _battle_result())
        assert payload["attacker"]["contingents"][0]["crowned"] is True

    def test_origin_nation_flies_its_own_colours(self):
        ney = _mk("Ney", "Waterloo", 40000)
        deroy = _mk("Deroy", "Waterloo", 15000)
        deroy.original_nation = "Bavaria"
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, deroy, mack)
        payload = _build(
            world, ney, mack, _battle_result(),
            atk_participants=[ney, deroy],
            atk_dist={"Ney": 2000, "Deroy": 500})
        d = next(c for c in payload["attacker"]["contingents"]
                 if c["name"] == "Deroy")
        assert d["origin_nation"] == "Bavaria"

    def test_observation_rides_the_payload(self):
        ney = _mk("Ney", "Waterloo", 40000)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        world = _world(ney, mack)
        payload = _build(world, ney, mack, _battle_result(
            observation="Mack's line dissolved at the first volley."))
        assert payload["observation"] == \
            "Mack's line dissolved at the first volley."


# ════════════════════════════════════════════════════════════════════════
# 7. Snapshot + transport
# ════════════════════════════════════════════════════════════════════════

class TestSnapshotAndTransport:
    def test_snapshot_captures_both_sides(self):
        a = _mk("A", "Paris", 12345)
        b = _mk("B", "Paris", 678, nation="Austria")
        snap = snapshot_pre_battle_strengths([a], [b])
        assert snap == {"A": 12345, "B": 678}

    def test_whitelisted_on_the_command_response(self):
        # Register-or-dropped (eval §3): the /command response builder only
        # copies whitelisted fields.
        from backend.main import _COMMAND_RESULT_SIMPLE_FIELDS
        assert "battle_diorama" in _COMMAND_RESULT_SIMPLE_FIELDS

    def test_event_transport_for_enemy_phase(self):
        # The enemy-phase dialog reads the EVENT copy — an AI attack's
        # battle event must carry the same payload object.
        mack = _mk("Mack", "Belgium", 40000, nation="Austria")
        ney = _mk("Ney", "Waterloo", 20000)
        world = _world(mack, ney)
        result = _attack(world, mack, "Ney")
        assert result.get("success")
        assert result["events"][0].get("diorama") is \
            result.get("battle_diorama")
