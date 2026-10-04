"""VD-C "The Contingent" — VASSAL_DEEPENING_SPEC.md §9.1 (Score Finish Step 5
SR-8a; rules SYSTEMS_REFERENCE.md §90), with its three IQ-7 riders:
IQ7-X1 (courting and the defection cascade walk every lord), IQ7-X2 (the
dead code deleted — pinned by its absence) and IQ7-X3 (the recovery hint
rides the crossing and the first fall of a downturn).

Every pin runs on the SHIPPED 1805 board (`europe_1805.json`, seed
`historical`) through the real passes — `contingent.process_vassal_contingents`,
`vassal.process_vassal_loyalty`, the four exits' own functions — so a pin
binds to production, never to a copy of a rule.

Measured facts the gate record rests on (October 3, 2026):
* boot sizes Holland 6,500 / Kingdom of Italy 7,500 / Switzerland 4,500
  (450 / 500 / 300 gold of province income x 15, loyalty 100);
* the boot raise: Holland (at war with Britain) and the Kingdom of Italy (at
  war with Austria) share France's war; Switzerland shares none and sends
  nothing;
* France's upkeep and fielded total are unchanged by the two contingents
  (2,630 gold, 189,000 men) — the client pays its men.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from backend.game_logic import contingent as C
from backend.game_logic import vassal as V
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
PLAYER = "France"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def boot():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(boot):
    return WorldState.from_dict(boot.to_dict())


def _key(w, a, b):
    return w._make_diplo_key(a, b)


def _set_state(w, a, b, state):
    w.diplomatic_states[_key(w, a, b)] = state
    w.invalidate_active_nations_cache()
    w.invalidate_bloc_members_cache()


def _pass(w):
    with _quiet():
        return C.process_vassal_contingents(w)


def _loyalty_tick(w):
    with _quiet():
        return V.process_vassal_loyalty(w)


def _beats(events, beat=None):
    return [e for e in events if e.get("type") == C.LOG_TYPE
            and (beat is None or e.get("beat") == beat)]


def _raised(w, vassal="Holland"):
    events = _pass(w)
    record = w.vassal_contingents[vassal]
    return record, w.marshals[record["marshal"]], events


def _end_holland_war(w):
    """Holland's only shared war is with Britain: end it for Holland alone."""
    _set_state(w, "Holland", "Britain", "PEACE")
    assert not C.shared_enemies(w, PLAYER, "Holland")


# ═══════════════════════════════════════════════════════════════════════════
# The size — income x loyalty, the pool, the bounds
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSize:
    def test_the_boot_sizes(self, world):
        assert C.contingent_income(world, "Holland") == 450
        assert C.contingent_size(world, "Holland") == 6500
        assert C.contingent_size(world, "KingdomOfItaly") == 7500
        assert C.contingent_size(world, "Switzerland") == 4500

    def test_loyalty_scales_it(self, world):
        assert C.contingent_size(world, "Holland", loyalty=60) == 4000

    def test_the_pool_bounds_it(self, world):
        world.manpower_pools["Holland"]["infantry"] = 4200
        assert C.contingent_size(world, "Holland") == 4000
        world.manpower_pools["Holland"]["infantry"] = 2900
        assert C.contingent_size(world, "Holland") == 0

    def test_the_cap(self, world):
        for name in ("Gelderland", "Brabant", "Friesland"):
            world.regions[name].income_value = 400
        assert C.contingent_income(world, "Holland") > 800
        world.manpower_pools["Holland"]["infantry"] = 50000
        assert C.contingent_size(world, "Holland") == C.CONTINGENT_MAX


# ═══════════════════════════════════════════════════════════════════════════
# The call — a loyal satellite in a shared war
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCall:
    def test_the_boot_raise(self, world):
        events = _pass(world)
        raised = _beats(events, "raised")
        assert sorted(e["vassal"] for e in raised) == ["Holland", "KingdomOfItaly"]
        assert "Switzerland" not in world.vassal_contingents
        holland = world.vassal_contingents["Holland"]
        dumonceau = world.marshals["Dumonceau"]
        assert holland["marshal"] == "Dumonceau" and holland["lord"] == PLAYER
        assert (dumonceau.nation, dumonceau.original_nation) == (PLAYER, "Holland")
        assert (dumonceau.location, dumonceau.strength) == ("Amsterdam", 6500)
        assert dumonceau.strategic_order is None   # it awaits the lord's orders
        teulie = world.marshals["Teulie"]
        assert (teulie.location, teulie.strength) == ("Milan", 7500)
        assert world.manpower_pools["Holland"]["infantry"] == 12000 - 6500
        assert world.manpower_pools["KingdomOfItaly"]["infantry"] == 15000 - 7500

    def test_the_raise_beat_names_the_men_the_payer_and_the_host(self, world):
        events = _pass(world)
        line = next(e for e in _beats(events, "raised") if e["vassal"] == "Holland")["message"]
        assert line.startswith("Holland sends 6,500 men under Dumonceau to the colours at Amsterdam")
        assert "await the orders of France" in line
        assert "The nearest host is Davout at Rhineland." in line
        assert "Holland pays them" in line
        italy = next(e for e in _beats(events, "raised") if e["vassal"] == "KingdomOfItaly")["message"]
        assert italy.startswith("The Kingdom of Italy sends 7,500 men under Teulie")
        assert "They stand with Massena." in italy

    def test_the_beat_is_logged_and_dispatched(self, world):
        _pass(world)
        logged = [e for e in world.event_log if e.get("type") == C.LOG_TYPE]
        assert {e["vassal"] for e in logged} == {"Holland", "KingdomOfItaly"}
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == C.DISPATCH_TYPE]
        assert len(queued) == 2 and all(e["fog_rule"] == "always" for e in queued)

    def test_a_wavering_satellite_sends_nothing(self, world):
        world.vassals["Holland"]["loyalty"] = V.CONTRIBUTION_LOYAL_MIN - 1
        _pass(world)
        assert "Holland" not in world.vassal_contingents

    def test_no_shared_war_no_contingent(self, world):
        _end_holland_war(world)
        _pass(world)
        assert "Holland" not in world.vassal_contingents

    def test_a_resting_satellite_waits(self, world):
        world.vassals["Holland"]["contingent_rest_until"] = int(world.current_turn) + 1
        _pass(world)
        assert "Holland" not in world.vassal_contingents

    def test_a_lord_already_fielding_its_men(self, world):
        ney = world.marshals["Ney"]
        ney.original_nation = "Holland"     # an assimilated Dutch corps
        _pass(world)
        assert "Holland" not in world.vassal_contingents

    def test_one_contingent_at_a_time(self, world):
        _pass(world)
        names = {r["marshal"] for r in world.vassal_contingents.values()}
        _pass(world)
        assert {r["marshal"] for r in world.vassal_contingents.values()} == names
        assert "Daendels" not in world.marshals

    def test_the_lever_down_raises_nothing(self, world, monkeypatch):
        monkeypatch.setattr(C, "THE_CLIENT_SENDS_ITS_CONTINGENT", False)
        assert _pass(world) == []
        assert world.vassal_contingents == {}

    def test_the_commander_is_the_first_free_one(self, world):
        world.fallen_marshals["Dumonceau"] = {"nation": PLAYER, "turn": 1,
                                              "location": "Ulm", "cause": "battle"}
        _pass(world)
        assert world.vassal_contingents["Holland"]["marshal"] == "Daendels"

    def test_past_the_authored_list_the_contingent_is_named_for_its_court(self, world):
        for name in ("Dumonceau", "Daendels", "Chasse"):
            world.fallen_marshals[name] = {"nation": PLAYER, "turn": 1,
                                           "location": "Ulm", "cause": "battle"}
        _pass(world)
        assert world.vassal_contingents["Holland"]["marshal"] == "Dutch Contingent"

    def test_gr5_an_ai_lord_raises_the_same(self, world):
        """Switzerland staged as AUSTRIA's satellite at war with France —
        Austria's own war — raises Austria's contingent by the same rule."""
        world.vassals["Switzerland"]["lord"] = "Austria"
        _set_state(world, "France", "Switzerland", "WAR")
        assert C.shared_enemies(world, "Austria", "Switzerland") == ["France"]
        _pass(world)
        record = world.vassal_contingents["Switzerland"]
        amey = world.marshals[record["marshal"]]
        assert record["marshal"] == "Amey" and record["lord"] == "Austria"
        assert (amey.nation, amey.original_nation, amey.strength) == ("Austria", "Switzerland", 4500)


# ═══════════════════════════════════════════════════════════════════════════
# The client pays its men
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClientPaysItsMen:
    def test_the_lords_bill_and_establishment_are_unchanged(self, world):
        before = world.calculate_turn_upkeep(PLAYER)
        _pass(world)
        after = world.calculate_turn_upkeep(PLAYER)
        assert after["total"] == before["total"] == 2630
        assert after["total_strength"] == before["total_strength"] == 189000
        assert "Dumonceau" not in {b["marshal"] for b in after["breakdown"]}

    def test_the_lever_down_bills_them(self, world, monkeypatch):
        _pass(world)
        monkeypatch.setattr(C, "THE_CLIENT_PAYS_ITS_MEN", False)
        billed = world.calculate_turn_upkeep(PLAYER)
        assert billed["total_strength"] == 189000 + 6500 + 7500


class TestTheClientsOwnMenAreNotTheLordsGarrison:
    def test_a_contingent_at_home_is_not_the_lords_garrison(self, world):
        """Dumonceau mustered at Amsterdam flies France's flag — but he is
        Holland's own men, so VP-D1's +2 garrison term does not light."""
        _raised(world)
        assert not V.lord_garrison_present(world, PLAYER, "Amsterdam")

    def test_a_french_corps_in_the_capital_still_is(self, world):
        _raised(world)
        world.marshals["Ney"].location = "Amsterdam"
        assert V.lord_garrison_present(world, PLAYER, "Amsterdam")

    def test_lever_down_the_contingent_counts(self, world, monkeypatch):
        monkeypatch.setattr(V, "A_CLIENTS_OWN_MEN_ARE_NOT_THE_LORDS_GARRISON", False)
        _raised(world)
        assert V.lord_garrison_present(world, PLAYER, "Amsterdam")


# ═══════════════════════════════════════════════════════════════════════════
# R12 — the client's general is not the Emperor's marshal
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClientsGeneral:
    def _glory(self, marshal, world, points):
        marshal.glory_events = [{"turn": int(world.current_turn), "points": points}]

    def test_no_rung_on_the_lords_ladder(self, world):
        from backend.game_logic import jealousy as J
        _, dumonceau, _ = _raised(world)
        assert C.is_clients_general(dumonceau)
        self._glory(dumonceau, world, 9)
        assert dumonceau not in [m for m, _g in J.get_nation_ladder(world, PLAYER)]

    def test_he_envies_no_one_and_no_one_envies_him(self, world):
        from backend.game_logic import jealousy as J
        _, dumonceau, _ = _raised(world)
        ney = world.marshals["Ney"]
        self._glory(ney, world, 5)
        self._glory(dumonceau, world, 1)
        assert J.find_jealousy_target(dumonceau, world) is None
        self._glory(dumonceau, world, 9)
        ney.glory_events = []
        assert J.find_jealousy_target(ney, world) is not dumonceau

    def test_he_expects_nothing_from_his_lords_purse(self, world):
        from backend.game_logic import dotation as D
        _, dumonceau, _ = _raised(world)
        dumonceau.expectation_steps = 3
        assert D.get_expectation(dumonceau) == 0
        world.current_turn = 20
        assert D.expectation_rise_blocked(dumonceau, world) == "his own court rewards him"
        assert D.raise_expectation(dumonceau, world) is False

    def test_a_marshal_of_his_own_colours_is_not_a_clients_general(self, world):
        ney = world.marshals["Ney"]
        ney.original_nation = "France"
        assert not C.is_clients_general(ney)

    def test_lever_down_he_is_one_of_the_marshals(self, world, monkeypatch):
        from backend.game_logic import dotation as D
        from backend.game_logic import jealousy as J
        monkeypatch.setattr(C, "A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL", False)
        _, dumonceau, _ = _raised(world)
        self._glory(dumonceau, world, 9)
        assert dumonceau in [m for m, _g in J.get_nation_ladder(world, PLAYER)]
        dumonceau.expectation_steps = 3
        assert D.get_expectation(dumonceau) > 0


# ═══════════════════════════════════════════════════════════════════════════
# The dead — the satellite's grief
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDead:
    def test_its_dead_bleed_the_satellite(self, world):
        record, dumonceau, _ = _raised(world)
        world.vassals["Holland"]["loyalty"] = 80
        dumonceau.strength -= 2600
        events = _loyalty_tick(world)
        assert record["last_strength"] == 3900
        holland = next(e for e in events if e.get("vassal") == "Holland")
        assert "the contingent's dead" in holland["reason"]
        # -5 for 2,600 dead, against the boot's +2 shared war, -2 drift
        assert holland["delta"] == -5

    def test_one_tick_costs_at_most_ten(self, world):
        _, dumonceau, _ = _raised(world)
        world.vassals["Holland"]["loyalty"] = 80
        dumonceau.strength = 600   # 5,900 dead
        assert C.contingent_dead_tick(world, "Holland") == 5900
        dumonceau.strength = 600
        world.vassal_contingents["Holland"]["last_strength"] = 6500
        events = _loyalty_tick(world)
        holland = next(e for e in events if e.get("vassal") == "Holland")
        assert holland["delta"] == -C.CONTINGENT_DEAD_LOYALTY_CAP

    def test_a_contingent_destroyed_is_lost(self, world):
        record, dumonceau, _ = _raised(world)
        world.vassals["Holland"]["loyalty"] = 80
        with _quiet():
            world.destroy_marshal(dumonceau, cause="battle", victor="Britain")
        assert C.contingent_dead_tick(world, "Holland") == 6500
        before = world.vassals["Holland"]["loyalty"]
        events = _pass(world)
        lost = _beats(events, "lost")
        assert lost and lost[0]["outcome"] == "decimated" and lost[0]["fate"] == "destroyed"
        assert world.vassals["Holland"]["loyalty"] == before - C.CONTINGENT_DECIMATED_LOYALTY
        assert "Holland" not in world.vassal_contingents
        assert world.vassals["Holland"]["contingent_rest_until"] == \
            int(world.current_turn) + C.CONTINGENT_REST_TURNS


# ═══════════════════════════════════════════════════════════════════════════
# The road home — crowned, decimated, or merely home
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRoadHome:
    def test_the_peace_sends_it_home(self, world):
        record, dumonceau, _ = _raised(world)
        dumonceau.location = "Rhineland"
        _end_holland_war(world)
        events = _pass(world)
        beat = _beats(events, "marching_home")
        assert beat and beat[0]["target"] == "Amsterdam"
        assert record["state"] == "homeward"
        order = dumonceau.strategic_order
        assert C.is_contingent_home_order(order) and order.command_type == "MOVE_TO"
        assert order.target == "Amsterdam"

    def test_arriving_home_it_stands_down_without_a_tombstone(self, world):
        record, dumonceau, _ = _raised(world)
        pool_before = world.manpower_pools["Holland"]["infantry"]
        dumonceau.strength = 5000
        _end_holland_war(world)
        events = _pass(world)            # it stands at Amsterdam: home at once
        home = _beats(events, "home")
        assert home and home[0]["reason"] == "home" and home[0]["outcome"] == "home"
        assert "Dumonceau" not in world.marshals
        assert "Dumonceau" not in world.fallen_marshals
        assert world.manpower_pools["Holland"]["infantry"] == pool_before + 5000
        assert "Holland" not in world.vassal_contingents

    def test_after_its_homecoming_the_satellite_rests(self, world):
        _raised(world)
        _end_holland_war(world)
        _pass(world)                       # home at once (it stands at Amsterdam)
        assert world.vassals["Holland"]["contingent_rest_until"] ==             int(world.current_turn) + C.CONTINGENT_REST_TURNS
        _set_state(world, "Holland", "Britain", "WAR")
        _pass(world)
        assert "Holland" not in world.vassal_contingents
        world.current_turn = int(world.current_turn) + C.CONTINGENT_REST_TURNS
        _pass(world)
        assert "Holland" in world.vassal_contingents

    def test_crowned_with_victory(self, world):
        _, dumonceau, _ = _raised(world)
        world.vassals["Holland"]["loyalty"] = 80
        dumonceau.battles_won += 1
        dumonceau.strength = 5000
        _end_holland_war(world)
        events = _pass(world)
        home = _beats(events, "home")[0]
        assert home["outcome"] == "crowned"
        assert world.vassals["Holland"]["loyalty"] == 80 + C.CONTINGENT_CROWN_LOYALTY
        assert "crowned with victory" in home["message"]

    def test_decimated(self, world):
        _, dumonceau, _ = _raised(world)
        world.vassals["Holland"]["loyalty"] = 80
        dumonceau.battles_won += 1        # a victory does not crown the dead
        dumonceau.strength = 3000         # < half of 6,500
        _end_holland_war(world)
        events = _pass(world)
        home = _beats(events, "home")[0]
        assert home["outcome"] == "decimated"
        assert world.vassals["Holland"]["loyalty"] == 80 - C.CONTINGENT_DECIMATED_LOYALTY
        assert "decimated" in home["message"]

    def test_kept_from_home_the_satellite_bleeds(self, world):
        from backend.models.marshal import StrategicOrder
        record, dumonceau, _ = _raised(world)
        dumonceau.location = "Rhineland"
        _end_holland_war(world)
        _pass(world)
        assert record["state"] == "homeward"
        dumonceau.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Swabia", target_type="region",
            started_turn=int(world.current_turn), original_command="march to Swabia",
            path=["Rhineland", "Swabia"])
        world.vassals["Holland"]["loyalty"] = 80
        assert C.contingent_kept_from_home(world, "Holland")
        events = _loyalty_tick(world)
        holland = next(e for e in events if e.get("vassal") == "Holland")
        assert "its men kept from home" in holland["reason"]

    def test_a_lost_road_is_given_again(self, world):
        record, dumonceau, _ = _raised(world)
        dumonceau.location = "Rhineland"
        _end_holland_war(world)
        _pass(world)
        dumonceau.strategic_order = None       # a battle or a stall took it
        _pass(world)
        assert C.is_contingent_home_order(dumonceau.strategic_order)

    def test_after_eight_turns_it_finds_its_own_way(self, world):
        record, dumonceau, _ = _raised(world)
        dumonceau.location = "Rhineland"
        _end_holland_war(world)
        _pass(world)
        world.current_turn = int(world.current_turn) + C.CONTINGENT_HOMEWARD_TURNS
        events = _pass(world)
        home = _beats(events, "home")
        assert home and home[0]["reason"] == "found_its_way"
        assert "Dumonceau" not in world.marshals

    def test_a_new_shared_war_returns_it_to_service(self, world):
        record, dumonceau, _ = _raised(world)
        dumonceau.location = "Rhineland"
        _end_holland_war(world)
        _pass(world)
        _set_state(world, "Holland", "Britain", "WAR")
        _pass(world)
        assert record["state"] == "serving" and record["homeward_turn"] is None

    def test_the_ai_walks_its_contingent_home(self, world):
        """GR5: an AI lord's contingent on the road home is walked by the
        AI's own P1.2 rung (the evaluator, so a failure names the rung)."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        world.vassals["Switzerland"]["lord"] = "Austria"
        _set_state(world, "France", "Switzerland", "WAR")
        _pass(world)
        amey = world.marshals["Amey"]
        amey.location = "Tyrol"
        _set_state(world, "France", "Switzerland", "PEACE")
        _pass(world)
        assert C.is_contingent_home_order(amey.strategic_order)
        step = C.contingent_next_step(world, amey)
        assert step
        with _quiet():
            action, _ = EnemyAI(CommandExecutor())._evaluate_marshal(amey, "Austria", world)
        assert action["action"] == "move" and action["target"] == step


# ═══════════════════════════════════════════════════════════════════════════
# The four exits — peace (above), release, transfer, rebellion
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFourExits:
    def test_a_release_recalls_it(self, world):
        _raised(world)
        with _quiet():
            result = V.release_vassal(world, "Holland")
        assert result.get("success") is True
        assert "Dumonceau" not in world.marshals
        assert "Holland" not in world.vassal_contingents
        assert any(e.get("beat") == "home" and e.get("reason") == "recalled"
                   for e in world.event_log if e.get("type") == C.LOG_TYPE)

    def test_a_rebellion_release_walks_it_out(self, world):
        _raised(world)
        with _quiet():
            V.release_vassal(world, "Holland", rebellion=True)
        dumonceau = world.marshals["Dumonceau"]
        assert (dumonceau.nation, dumonceau.original_nation, dumonceau.strength) == \
            ("Holland", None, 6500)
        assert "Holland" not in world.vassal_contingents
        assert any(e.get("beat") == "walked_out"
                   for e in world.event_log if e.get("type") == C.LOG_TYPE)

    def test_a_transfer_recalls_it(self, world):
        _raised(world)
        with _quiet():
            result = V.transfer_vassal(world, "Holland", "Prussia")
        assert result.get("success") is True
        assert "Dumonceau" not in world.marshals       # never re-keyed to Prussia
        assert "Holland" not in world.vassal_contingents

    def test_a_rebellion_walks_it_out(self, world):
        _raised(world)
        world.vassals["Holland"]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(world)
        dumonceau = world.marshals["Dumonceau"]
        assert dumonceau.nation == "Holland" and dumonceau.strength == 6500
        assert "Holland" not in world.vassal_contingents
        walked = [e for e in world.event_log
                  if e.get("type") == C.LOG_TYPE and e.get("beat") == "walked_out"]
        assert walked and "out of France's lines" in walked[0]["message"]

    def test_a_fallen_lord_frees_its_contingent(self, world):
        """FA-S12-2's fifth exit: an AI lord eliminated — its satellite's
        contingent walks out under its own flag before the lord's sweep."""
        world.vassals["Switzerland"]["lord"] = "Austria"
        _set_state(world, "France", "Switzerland", "WAR")
        _pass(world)
        with _quiet():
            world._eliminate_nation("Austria")
        amey = world.marshals["Amey"]
        assert (amey.nation, amey.strength) == ("Switzerland", 4500)
        assert "Switzerland" not in world.vassal_contingents
        assert any(e.get("beat") == "walked_out" and e.get("vassal") == "Switzerland"
                   for e in world.event_log if e.get("type") == C.LOG_TYPE)

    def test_stand_down_never_removes_a_prisoner_or_the_sovereign(self, world):
        record, dumonceau, _ = _raised(world)
        dumonceau.captured_by = "Britain"
        assert world.stand_down_marshal(dumonceau) is False
        assert "Dumonceau" in world.marshals
        assert world.stand_down_marshal("Napoleon") is False
        assert "Napoleon" in world.marshals

    def test_an_exit_nobody_hooked_is_reconciled(self, world):
        _raised(world)
        del world.vassals["Holland"]        # a row deleted by an unnamed path
        world.invalidate_active_nations_cache()
        events = _pass(world)
        assert "Holland" not in world.vassal_contingents
        assert "Dumonceau" not in world.marshals
        assert _beats(events, "home")


# ═══════════════════════════════════════════════════════════════════════════
# VS-4 Rule 1b and IQ-7 R1 — the regiments clause comes true
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRegimentsClause:
    def test_the_lord_fields_the_satellites_regiments(self, world):
        assert not V.lord_fields_the_vassals_regiments(world, PLAYER, "Holland")
        _raised(world)
        assert V.lord_fields_the_vassals_regiments(world, PLAYER, "Holland")
        assert V.lord_fields_the_vassals_regiments(world, PLAYER, "KingdomOfItaly")

    def test_the_wavering_line_carries_the_regiments_clause(self, world):
        _raised(world)
        line = V.tier_crossing_line("Holland", 61, 58, world=world, lord=PLAYER)
        assert line.endswith(V._WAVERING_REGIMENTS_CLAUSE.strip())

    def test_a_wavering_contingent_holds_back_from_the_muster(self, world):
        from backend.commands.combat_executor import CombatExecutor
        _raised(world)
        teulie = world.marshals["Teulie"]
        massena = world.marshals["Massena"]
        teulie.location = "Piedmont"          # adjacent to Milan
        ex = CombatExecutor.__new__(CombatExecutor)
        assert ex._is_reinforcement_eligible(teulie, massena, "Milan", PLAYER, world)
        world.vassals["KingdomOfItaly"]["loyalty"] = V.CONTRIBUTION_LOYAL_MIN - 1
        assert not ex._is_reinforcement_eligible(teulie, massena, "Milan", PLAYER, world)


# ═══════════════════════════════════════════════════════════════════════════
# IQ7-X1 — courting and the cascade walk every lord (GR5)
# ═══════════════════════════════════════════════════════════════════════════

class TestAILordThreats:
    def _austrian_switzerland(self, world, loyalty):
        world.vassals["Switzerland"]["lord"] = "Austria"
        world.vassals["Switzerland"]["loyalty"] = loyalty
        world.invalidate_bloc_members_cache()

    def test_courting_reaches_an_ai_lords_satellite(self, world):
        self._austrian_switzerland(world, 40)
        world.nation_dp["Prussia"] = 4
        with _quiet():
            events = V.attempt_vassal_courting(world, "Prussia")
        assert events and events[0]["vassal"] == "Switzerland" and events[0]["lord"] == "Austria"
        assert world.vassals["Switzerland"]["loyalty"] < 40
        # the player's tray hears nothing of a rival lord's client
        assert not any("Switzerland" in str(n.get("title", ""))
                       for n in world.notifications.get_pending())

    def test_lever_down_a_rival_lords_satellite_is_spared(self, world, monkeypatch):
        monkeypatch.setattr(V, "THREATS_WALK_EVERY_LORD", False)
        self._austrian_switzerland(world, 40)
        world.nation_dp["Prussia"] = 4
        with _quiet():
            assert V.attempt_vassal_courting(world, "Prussia") == []
        assert world.vassals["Switzerland"]["loyalty"] == 40

    def test_the_grip_read_is_the_satellites_own_lords(self, world, monkeypatch):
        """GR5: an AI lord whose grip has spiralled loses its satellite to a
        courting the player's healthy grip would have refused (loyalty 55 is
        above the healthy 50 threshold; Austria's grip 10 widens it)."""
        self._austrian_switzerland(world, 55)
        world.nation_dp["Prussia"] = 4
        monkeypatch.setattr(V, "get_imperial_grip",
                            lambda w, nation: 10 if nation == "Austria" else 100)
        with _quiet():
            events = V.attempt_vassal_courting(world, "Prussia")
        assert events and events[0]["vassal"] == "Switzerland"

    def test_a_lord_never_courts_its_own_satellite(self, world):
        self._austrian_switzerland(world, 40)
        world.nation_dp["Austria"] = 4
        with _quiet():
            assert V.attempt_vassal_courting(world, "Austria") == []

    def test_the_cascade_reaches_an_ai_lords_satellite(self, world, monkeypatch):
        import random
        self._austrian_switzerland(world, 10)
        monkeypatch.setattr(
            "backend.game_logic.diplomacy.get_war_score_for",
            lambda w, a, b: -50 if a == "Austria" else 0)
        monkeypatch.setattr(random, "random", lambda: 0.0)
        with _quiet():
            events = V.check_defection_cascade(world)
        assert any(e["vassal"] == "Switzerland" and e["lord"] == "Austria" for e in events)
        assert world.vassals["Switzerland"]["loyalty"] == V.LOYALTY_MIN
        # "the empire trembles" is the player's own web's line, never a rival's
        assert not [e for e in world.pending_dispatch_events
                    if e.get("type") == "diplomatic_defection_cascade"]

    def test_lever_down_the_cascade_is_the_players_alone(self, world, monkeypatch):
        import random
        monkeypatch.setattr(V, "THREATS_WALK_EVERY_LORD", False)
        self._austrian_switzerland(world, 10)
        monkeypatch.setattr(
            "backend.game_logic.diplomacy.get_war_score_for",
            lambda w, a, b: -50 if a == "Austria" else 0)
        monkeypatch.setattr(random, "random", lambda: 0.0)
        with _quiet():
            events = V.check_defection_cascade(world)
        assert not any(e["vassal"] == "Switzerland" for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# IQ7-X2 — the dead code is gone
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDeadCodeIsGone:
    def test_neither_name_survives_in_the_backend(self):
        hits = []
        for path in (REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for name in ("def get_vassal_warnings", "VASSAL_LOYALTY_CRITICAL ="):
                if name in text:
                    hits.append((path.name, name))
        assert hits == []


# ═══════════════════════════════════════════════════════════════════════════
# IQ7-X3 — the hint rides the turn of the trend, not every tick
# ═══════════════════════════════════════════════════════════════════════════

class TestTheHintRidesTheTurn:
    def _falling_holland(self, world, loyalty=90):
        """No shared war, satellite drift -2: a steady fall."""
        _end_holland_war(world)
        world.vassals["Holland"]["loyalty"] = loyalty

    def _hint(self, events, vassal="Holland"):
        e = next((x for x in events if x.get("vassal") == vassal), None)
        return (e or {}).get("recovery_hint", "")

    def test_a_steady_fall_is_hinted_once(self, world):
        self._falling_holland(world)
        hints = [bool(self._hint(_loyalty_tick(world))) for _ in range(4)]
        assert hints == [True, False, False, False]
        assert "Holland" in world.vassal_hint_spent
        assert "recovery_hint_owed" not in world.vassals["Holland"]   # VS-R Q6

    def test_a_rise_re_arms_it(self, world):
        self._falling_holland(world)
        assert self._hint(_loyalty_tick(world))
        assert not self._hint(_loyalty_tick(world))
        _set_state(world, "Holland", "Britain", "WAR")    # +2 shared war: a standstill
        _loyalty_tick(world)
        assert "Holland" not in world.vassal_hint_spent
        _end_holland_war(world)
        assert self._hint(_loyalty_tick(world))

    def test_a_crossing_always_carries_it(self, world):
        self._falling_holland(world, loyalty=61)
        world.vassal_hint_spent.append("Holland")
        events = _loyalty_tick(world)
        assert self._hint(events)

    def test_lever_down_every_falling_tick(self, world, monkeypatch):
        monkeypatch.setattr(V, "THE_HINT_RIDES_THE_TURN", False)
        self._falling_holland(world)
        hints = [bool(self._hint(_loyalty_tick(world))) for _ in range(3)]
        assert hints == [True, True, True]


# ═══════════════════════════════════════════════════════════════════════════
# The exit's instrument correction — vassals C2 reads the tick, not the battles
# ═══════════════════════════════════════════════════════════════════════════

class _FakeArm:
    def __init__(self, records):
        self.records = records

    def by_turn(self):
        groups = []
        for r in self.records:
            if r.get("kind") == "turn":
                groups.append([r])
            elif groups:
                groups[-1].append(r)
        return groups


class TestTheInstrumentReadsTheTick:
    """Measured on the exit's CMD-A arm (October 4, 2026): Switzerland was
    granted to 93 on turn 7; the end-turn tick started at 93 and closed at 86
    after four French defeats ("the lord's defeats", −6 for every satellite),
    and the band read a false miss. The digest now carries the tick's own row
    and the reader reads the quote against the loyalty the tick started from."""

    def _arm(self, *, with_tick):
        records = [
            {"kind": "turn", "turn": 7},
            {"kind": "popup", "key": "proposal_result",
             "summary": "Switzerland's tribute is remitted for 8 collections (1800g forgone). "
                        "Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP."},
        ]
        if with_tick:
            records.append({"kind": "loyalty", "vassal": "Switzerland", "lord": "France",
                            "old": 93, "new": 86, "delta": -7})
        records.append({"kind": "ledger", "vassals": {"Switzerland": 86}})
        return _FakeArm(records)

    def test_the_tick_row_reads_the_quote_exactly(self):
        import sys
        sys.path.insert(0, str(REPO))
        from tools import _score_probes as P
        verdict = P.vassals_c2_petition_quote({"CMD-A": self._arm(with_tick=True)}, {})
        assert verdict["measured"] is True and verdict["pass"] is True, verdict

    def test_a_lying_quote_still_fails(self):
        import sys
        sys.path.insert(0, str(REPO))
        from tools import _score_probes as P
        arm = self._arm(with_tick=True)
        arm.records[2]["old"] = 88
        verdict = P.vassals_c2_petition_quote({"CMD-A": arm}, {})
        assert verdict["pass"] is False and "the tick started at 88" in verdict["evidence"]

    def test_without_the_row_the_band_reads_as_before(self):
        import sys
        sys.path.insert(0, str(REPO))
        from tools import _score_probes as P
        verdict = P.vassals_c2_petition_quote({"CMD-A": self._arm(with_tick=False)}, {})
        assert verdict["pass"] is False and "quoted 93, ledger 86" in verdict["evidence"]

    def test_a_tick_before_the_grant_is_not_its_tick(self):
        """Measured on CMD-H t6: the end turn's tick (88 → 86) came FIRST and
        the petition was granted in the drain after it (86 → 96) — the ledger
        already reads 96. The tick before the grant is not the grant's."""
        import sys
        sys.path.insert(0, str(REPO))
        from tools import _score_probes as P
        arm = _FakeArm([
            {"kind": "turn", "turn": 6},
            {"kind": "loyalty", "vassal": "Switzerland", "lord": "France",
             "old": 88, "new": 86, "delta": -2},
            {"kind": "popup", "key": "proposal_result",
             "summary": "Switzerland's tribute is remitted for 8 collections (1800g forgone). "
                        "Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP."},
            {"kind": "ledger", "vassals": {"Switzerland": 96}},
        ])
        verdict = P.vassals_c2_petition_quote({"CMD-H": arm}, {})
        assert verdict["pass"] is True, verdict

    def test_the_driver_records_the_tick(self):
        import sys
        sys.path.insert(0, str(REPO))
        from tools import playtest_driver as PD

        class _D:
            def __init__(self):
                self.rows = []

            def record(self, kind, **fields):
                self.rows.append((kind, fields))

        d = _D()
        PD.Digest.loyalty_tick(d, {"events": [
            {"type": "vassal_loyalty", "vassal": "Holland", "lord": "France",
             "old_loyalty": 95, "new_loyalty": 89, "delta": -6},
            {"type": "turn_end"}]})
        assert d.rows == [("loyalty", {"vassal": "Holland", "lord": "France",
                                       "old": 95, "new": 89, "delta": -6})]


# ═══════════════════════════════════════════════════════════════════════════
# The authored commanders — the validator (the MC-4 guard extends here)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheValidator:
    def _validate(self, contingents, marshals=None, pool=None):
        from backend.modding.validator import validate_scenario
        data = {"marshals": marshals or {}, "contingents": contingents}
        if pool is not None:
            data["marshal_pool"] = pool
        return validate_scenario(data, check_adjacency=False)

    def test_the_shipped_table_validates_clean(self):
        import json
        from backend.modding.validator import validate_scenario
        data = json.loads(Path(SCENARIO).read_text(encoding="utf-8"))
        result = validate_scenario(data, check_adjacency=False)
        assert not [e for e in result.errors if "contingents" in e.path]
        assert not [w for w in result.warnings if "contingents" in w.path]
        assert set(data["contingents"]) >= {"Holland", "KingdomOfItaly", "Switzerland"}

    def test_a_retired_personality_hard_fails(self):
        result = self._validate({"Holland": [{"name": "Test", "personality": "balanced"}]})
        assert any(e.path == "contingents.Holland[0].personality" for e in result.errors)

    def test_a_sovereign_never_leads_a_contingent(self):
        result = self._validate({"Holland": [{"name": "Test", "personality": "sovereign"}]})
        assert any("sovereign" in e.message for e in result.errors)

    def test_a_name_must_be_new(self):
        result = self._validate(
            {"Holland": [{"name": "Ney"}]},
            marshals={"Ney": {"name": "Ney", "location": "Paris", "strength": 1000}})
        assert any(e.path == "contingents.Holland[0].name" for e in result.errors)
        result = self._validate(
            {"Holland": [{"name": "Grouchy"}]},
            pool={"France": [{"name": "Grouchy", "personality": "cautious", "cost": 100}]})
        assert any(e.path == "contingents.Holland[0].name" for e in result.errors)
        result = self._validate({"Holland": [{"name": "Twin"}], "Switzerland": [{"name": "Twin"}]})
        assert any(e.path == "contingents.Switzerland[0].name" for e in result.errors)

    def test_a_commander_is_never_commissioned(self):
        result = self._validate({"Holland": [{"name": "Test", "cost": 100}]})
        assert any(e.path == "contingents.Holland[0].cost" for e in result.errors)

    def test_skills_are_one_to_ten(self):
        result = self._validate({"Holland": [{"name": "Test", "skills": {"tactical": 11}}]})
        assert any(e.path == "contingents.Holland[0].skills.tactical" for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════════
# The record — serialized, logged, fog-honest
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRecord:
    def test_the_diplomacy_turn_runs_the_pass(self, world):
        from backend.game_logic.diplomacy import process_diplomacy_turn
        with _quiet():
            events = process_diplomacy_turn(world)
        assert {e["vassal"] for e in _beats(events, "raised")} == {"Holland", "KingdomOfItaly"}

    def test_the_store_survives_a_save(self, world):
        _pass(world)
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.vassal_contingents == world.vassal_contingents
        assert loaded.contingent_commanders == world.contingent_commanders
        assert loaded.marshals["Dumonceau"].original_nation == "Holland"

    def test_a_pre_vdc_save_reads_empty(self, world):
        data = world.to_dict()
        for key in ("vassal_contingents", "contingent_commanders", "vassal_hint_spent"):
            data.pop(key)
        loaded = WorldState.from_dict(data)
        assert loaded.vassal_contingents == {} and loaded.contingent_commanders == {}
        assert loaded.vassal_hint_spent == []

    def test_a_pre_vdc_1805_save_is_armed_with_the_authored_commanders(self, world):
        from backend import save_manager
        authored = {k: [dict(c) for c in v] for k, v in world.contingent_commanders.items()}
        assert authored.get("Holland")
        world.contingent_commanders = {}
        save_manager._backfill_contingent_commanders(world)
        assert world.contingent_commanders == authored

    def test_an_armed_save_is_never_overwritten_and_a_tutorial_gets_none(self, world):
        from backend import save_manager
        world.contingent_commanders = {"Holland": [{"name": "Kept"}]}
        save_manager._backfill_contingent_commanders(world)
        assert world.contingent_commanders == {"Holland": [{"name": "Kept"}]}
        world.contingent_commanders = {}
        world.scenario_name = "tutorial"
        save_manager._backfill_contingent_commanders(world)
        assert world.contingent_commanders == {}

    def test_the_log_type_is_registered_and_reads_its_line(self):
        from backend import campaign_log as CL
        assert C.LOG_TYPE in CL.CAMPAIGN_LOG_TYPES
        assert CL.CATEGORY_MAP[C.LOG_TYPE] == "diplomacy"
        line = CL.format_event_oneliner({"type": C.LOG_TYPE, "vassal": "Holland",
                                         "message": "Holland sends 6,500 men."})
        assert line == "Holland sends 6,500 men."

    def test_a_rival_lords_contingent_is_fog_ruled(self, world):
        world.vassals["Switzerland"]["lord"] = "Austria"
        _set_state(world, "France", "Switzerland", "WAR")
        _pass(world)
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == C.DISPATCH_TYPE
                  and e["template_vars"].get("nation") == "Switzerland"]
        assert queued and queued[0]["fog_rule"] == "partial_on_nation"
