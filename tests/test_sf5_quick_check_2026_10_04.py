"""The Step 5 quick check (Score Finish, October 4, 2026; BUG_FIXES §Score
Finish Step 5 SF5-RV1 … SF5-RV12).

Step 5 "the client stands" landed at `fe720296`. The user asked for a quick
check before Step 6: two read-only reviewers attacked the slice — one the VD-C
contingent lifecycle, one the slice's riders — and every finding below was
reproduced on the shipped 1805 board before it was fixed. Each pin drives the
real code path (the executor, the per-turn passes, `POST /command`,
`POST /strategic_response`) and flips with its lever.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import contingent as C
from backend.game_logic import vassal as V
from backend.models.marshal import StrategicOrder


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def _raise_holland(world):
    """Holland's contingent on the boot board (France and Holland share the
    war with Britain). Returns its marshal."""
    beat = C.raise_contingent(world, "Holland")
    assert beat is not None, "Holland could not raise its contingent"
    record = C.contingent_record(world, "Holland")
    return world.marshals[record["marshal"]]


def _end_shared_war(world):
    for a, b in (("France", "Britain"), ("Holland", "Britain")):
        world.diplomatic_states[world._make_diplo_key(a, b)] = "PEACE"


def _renew_shared_war(world):
    for a, b in (("France", "Britain"), ("Holland", "Britain")):
        world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"


# ═══════════════════════ SF5-RV1 — the lord does not fill the client's ranks ═══════════════════════

class TestTheLordDoesNotFillTheClientsRanks:
    def test_a_named_recruit_into_the_contingent_is_refused_free(self, shipped):
        client, world = shipped
        dumonceau = _raise_holland(world)
        before = (int(world.gold), int(dumonceau.strength),
                  int(world.manpower_pools["France"]["infantry"]))
        r = post(client, f"{dumonceau.name}, recruit infantry")
        assert r.get("success") is False
        assert "belong to Holland" in r.get("message", "")
        assert (int(world.gold), int(dumonceau.strength),
                int(world.manpower_pools["France"]["infantry"])) == before

    def test_substitutes_for_the_contingent_are_refused(self, shipped):
        client, world = shipped
        dumonceau = _raise_holland(world)
        strength = int(dumonceau.strength)
        r = post(client, f"buy substitutes for {dumonceau.name}")
        assert r.get("success") is False
        assert "belong to Holland" in r.get("message", "")
        assert int(dumonceau.strength) == strength

    def test_the_levy_selector_passes_over_the_contingent(self, shipped):
        _client, world = shipped
        dumonceau = _raise_holland(world)
        dumonceau.location = "Flanders"
        ready, passed = world.ready_marshals_near("Flanders", for_levy=True)
        assert dumonceau.name not in [m.name for m, _d in ready]
        assert any(dumonceau.name in p and "contingent" in p for p in passed)
        # The combat auto-pick keeps him: a contingent fights under orders.
        ready_any, _ = world.ready_marshals_near("Flanders")
        assert dumonceau.name in [m.name for m, _d in ready_any]

    def test_the_quote_and_the_unnamed_levy_never_name_him(self, shipped):
        client, world = shipped
        dumonceau = _raise_holland(world)
        dumonceau.location = "Flanders"
        from backend.commands.economy_executor import recruit_quote
        assert recruit_quote(world, "Flanders").get("recipient") != dumonceau.name
        strength = int(dumonceau.strength)
        post(client, "recruit infantry in Flanders")
        assert int(dumonceau.strength) == strength

    def test_the_ai_admin_pick_skips_a_contingent(self, shipped, monkeypatch):
        _client, world = shipped
        dumonceau = _raise_holland(world)
        dumonceau.location = "Flanders"   # the AI levies only on its own soil
        dumonceau.starting_strength = int(dumonceau.strength) * 4  # badly bled
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(M.executor)
        picked = ai._find_weakest_marshal_for_admin("France", world, threshold=1.0)
        assert picked is None or picked.name != dumonceau.name
        monkeypatch.setattr(C, "THE_LORD_DOES_NOT_FILL_THE_CLIENTS_RANKS", False)
        picked = ai._find_weakest_marshal_for_admin("France", world, threshold=1.0)
        assert picked is not None and picked.name == dumonceau.name

    def test_lever_down_the_named_recruit_reaches_the_executor(self, shipped, monkeypatch):
        _client, world = shipped
        dumonceau = _raise_holland(world)
        monkeypatch.setattr(C, "THE_LORD_DOES_NOT_FILL_THE_CLIENTS_RANKS", False)
        assert C.lord_fill_refusal(world, dumonceau) == ""
        assert C.levy_passes_over(world, dumonceau) is None


# ═══════════════════════ SF5-RV2 — the renewed war recalls the colours ═══════════════════════

class TestTheRenewedWarRecallsTheColours:
    def _homeward(self, world):
        dumonceau = _raise_holland(world)
        dumonceau.location = "Flanders"
        _end_shared_war(world)
        C.process_vassal_contingents(world)
        assert C.contingent_record(world, "Holland")["state"] == "homeward"
        assert C.is_contingent_home_order(dumonceau.strategic_order)
        return dumonceau

    def test_the_home_order_is_withdrawn_when_the_war_resumes(self, shipped):
        _client, world = shipped
        dumonceau = self._homeward(world)
        _renew_shared_war(world)
        events = C.process_vassal_contingents(world)
        assert C.contingent_record(world, "Holland")["state"] == "serving"
        assert dumonceau.strategic_order is None
        assert any(e.get("beat") == "back_to_the_colours" for e in events)

    def test_lever_down_the_march_home_stands(self, shipped, monkeypatch):
        _client, world = shipped
        dumonceau = self._homeward(world)
        monkeypatch.setattr(C, "THE_RENEWED_WAR_RECALLS_THE_COLOURS", False)
        _renew_shared_war(world)
        C.process_vassal_contingents(world)
        assert C.is_contingent_home_order(dumonceau.strategic_order)

    def test_an_order_the_lord_gave_stands(self, shipped):
        _client, world = shipped
        dumonceau = self._homeward(world)
        dumonceau.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Artois", target_type="region",
            started_turn=int(world.current_turn), original_command="march to Artois",
            path=["Artois"])
        _renew_shared_war(world)
        C.process_vassal_contingents(world)
        assert dumonceau.strategic_order is not None
        assert dumonceau.strategic_order.target == "Artois"


# ═══════════════════════ SF5-RV3 — the raise beat keeps the fog ═══════════════════════

class TestTheRaiseBeatKeepsTheFog:
    def _rival_raise(self, world, monkeypatch, lever=True):
        monkeypatch.setattr(C, "THE_RAISE_BEAT_KEEPS_THE_FOG", lever)
        world.vassals["Holland"]["lord"] = "Spain"  # Spain shares Holland's war with Britain
        host = C._find_host(world, "Spain", world.get_nation_capital("Holland"))
        assert host is not None, "Spain has no field marshal to name"
        world.intel.pop(host.location, None)  # out of the player's sight
        beat = C.raise_contingent(world, "Holland")
        return host, beat

    def test_an_unseen_rival_host_is_not_named(self, shipped, monkeypatch):
        _client, world = shipped
        host, beat = self._rival_raise(world, monkeypatch)
        assert host.location not in beat["message"]
        assert beat.get("host") == ""

    def test_lever_down_the_line_names_where_he_stands(self, shipped, monkeypatch):
        _client, world = shipped
        host, beat = self._rival_raise(world, monkeypatch, lever=False)
        assert host.location in beat["message"]

    def test_the_players_own_host_is_always_named(self, shipped):
        _client, world = shipped
        world.marshals["Ney"].location = "Flanders"
        beat = C.raise_contingent(world, "Holland")
        assert beat.get("host")


# ═══════════════════════ SF5-RV4 — an override keeps them from home ═══════════════════════

class TestAnOverrideKeepsThemFromHome:
    def _homeward(self, world):
        dumonceau = _raise_holland(world)
        dumonceau.location = "Flanders"
        _end_shared_war(world)
        C.process_vassal_contingents(world)
        return dumonceau

    def test_the_lords_override_is_charged_on_the_next_tick(self, shipped):
        client, world = shipped
        dumonceau = self._homeward(world)
        r = post(client, f"{dumonceau.name}, fortify")
        assert r.get("success") is not False, r.get("message")
        assert dumonceau.strategic_order is None
        world.current_turn += 1   # the tick reads the stamp at N + 1
        assert C.contingent_kept_from_home(world, "Holland") is True
        world.current_turn += 1   # and only once
        assert C.contingent_kept_from_home(world, "Holland") is False

    def test_lever_down_the_override_dodges_the_bleed(self, shipped, monkeypatch):
        client, world = shipped
        dumonceau = self._homeward(world)
        monkeypatch.setattr(C, "THE_OVERRIDE_KEEPS_THEM_FROM_HOME", False)
        post(client, f"{dumonceau.name}, fortify")
        world.current_turn += 1
        assert C.contingent_kept_from_home(world, "Holland") is False

    def test_a_restored_home_order_costs_nothing(self, shipped):
        _client, world = shipped
        dumonceau = self._homeward(world)
        C.note_lord_override(world, dumonceau)   # stamped, but the order stands
        world.current_turn += 1
        assert C.is_contingent_home_order(dumonceau.strategic_order)
        assert C.contingent_kept_from_home(world, "Holland") is False


# ═══════════════════════ SF5-RV5 — a fallen crown disbands its men ═══════════════════════

class TestAFallenCrownDisbandsItsMen:
    def _fall_holland(self, world):
        dumonceau = _raise_holland(world)
        for name in list(world.get_nation_regions("Holland")):
            world.regions[name].controller = "France"
        world.invalidate_active_nations_cache()
        world.vassals.pop("Holland", None)
        return dumonceau

    def test_the_contingent_disbands_and_no_pool_is_credited(self, shipped):
        _client, world = shipped
        dumonceau = self._fall_holland(world)
        pool = int(world.manpower_pools.get("Holland", {}).get("infantry", 0) or 0)
        events = C.process_vassal_contingents(world)
        assert any(e.get("beat") == "disbanded" for e in events)
        assert dumonceau.name not in world.marshals
        assert dumonceau.name not in (world.fallen_marshals or {})
        assert int(world.manpower_pools.get("Holland", {}).get("infantry", 0) or 0) == pool
        assert C.contingent_record(world, "Holland") is None

    def test_lever_down_it_is_recalled_home(self, shipped, monkeypatch):
        _client, world = shipped
        self._fall_holland(world)
        monkeypatch.setattr(C, "THE_FALLEN_CROWN_DISBANDS_ITS_MEN", False)
        events = C.process_vassal_contingents(world)
        assert any(e.get("beat") == "home" for e in events)


# ═══════════════════════ SF5-RV6 — an order aimed at him ends with him ═══════════════════════

class TestAnOrderAimedAtHimEndsWithHim:
    def test_a_support_order_on_a_stood_down_contingent_is_cancelled(self, shipped):
        _client, world = shipped
        dumonceau = _raise_holland(world)
        ney = world.marshals["Ney"]
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT", target=dumonceau.name, target_type="marshal",
            started_turn=int(world.current_turn), original_command=f"support {dumonceau.name}",
            path=[])
        assert world.stand_down_marshal(dumonceau) is True
        assert ney.strategic_order is None


# ═══════════════════════ SF5-RV7 — the popup button waits on a hard stop ═══════════════════════

@pytest.fixture
def interrupt_board(shipped):
    client, world = shipped
    ney, mack = world.marshals["Ney"], world.marshals["Mack"]
    ney.location = mack.location
    ney.strategic_order = StrategicOrder(
        command_type="PURSUE", target="Mack", target_type="marshal",
        started_turn=int(world.current_turn), original_command="pursue Mack",
        path=[mack.location])
    ney.pending_interrupt = {
        "marshal": "Ney", "interrupt_type": "contact_bad_odds", "enemy": "Mack",
        "location": ney.location, "is_first_step": True,
        "options": ["attack_anyway", "hold_position", "cancel_order"],
        "message": "Ney faces poor odds against Mack."}
    return client, world


def _battles(world):
    return len([e for e in world.event_log if e.get("type") == "battle"])


class TestThePopupButtonWaitsOnAHardStop:
    def _stage_hard_stop(self, client, world):
        post(client, "declare war on Prussia")
        assert world.dialogue_manager.is_hard_stop(), "no hard stop staged"

    def test_the_button_relays_nothing_under_a_hard_stop(self, interrupt_board):
        client, world = interrupt_board
        self._stage_hard_stop(client, world)
        battles = _battles(world)
        r = client.post("/strategic_response", json={
            "marshal_name": "Ney", "response_type": "contact_bad_odds",
            "choice": "attack_anyway"}).json()
        assert r.get("success") is False
        assert "nothing was relayed" in r.get("message", "")
        ney = world.marshals["Ney"]
        assert ney.pending_interrupt and ney.strategic_order is not None
        assert _battles(world) == battles

    def test_lever_down_the_button_runs_the_answer(self, interrupt_board, monkeypatch):
        client, world = interrupt_board
        self._stage_hard_stop(client, world)
        monkeypatch.setattr(M, "A_HARD_STOP_OUTRANKS_AN_INTERRUPT", False)
        r = client.post("/strategic_response", json={
            "marshal_name": "Ney", "response_type": "contact_bad_odds",
            "choice": "attack_anyway"}).json()
        assert "nothing was relayed" not in (r.get("message") or "")


# ═══════════════════════ SF5-RV8 — no client's general is jealous ═══════════════════════

class TestNoClientsGeneralIsJealous:
    """Staged as the reviewer measured it: Bavaria vassalized by treaty and its
    literal general Deroy assimilated; Ney marches every turn, so the
    sidelining counter climbs (a literal is sidelined only while a fellow
    marshal is engaged)."""

    def _drive(self, world):
        V.create_vassal_treaty(world, "France", "Bavaria")
        V.assimilate_vassal_marshals(world, "Bavaria")
        general = world.marshals["Deroy"]
        assert C.is_clients_general(general) or not C.A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL
        ney = world.marshals["Ney"]
        from backend.game_logic import jealousy as J
        events = []
        for _ in range(6):
            ney.strategic_order = StrategicOrder(
                command_type="MOVE_TO", target="Alsace", target_type="region",
                started_turn=int(world.current_turn), original_command="march to Alsace",
                path=["Alsace"])
            events += J.process_turn(world)
            world.current_turn += 1
        return general, events

    def test_an_assimilated_literal_never_envies_the_ladder(self, shipped):
        _client, world = shipped
        general, events = self._drive(world)
        assert general.consecutive_hold_turns >= 3   # the trigger was reachable
        assert not getattr(general, "jealous_of", None)
        assert not any(e.get("marshal") == general.name for e in events
                       if str(e.get("type", "")).startswith("jealousy"))

    def test_lever_down_the_literal_fallback_makes_him_jealous(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(C, "A_CLIENTS_GENERAL_IS_NOT_THE_EMPERORS_MARSHAL", False)
        general, _events = self._drive(world)
        assert getattr(general, "jealous_of", None)


# ═══════════════════════ SF5-RV9 — the question re-prompt consumes nothing ═══════════════════════

def _cannon_fire(world):
    """A cautious marshal's cannon-fire ask (it quotes a trust cost on Hold
    Position — FA-49), Davout marching under a standing order."""
    davout = world.marshals["Davout"]
    davout.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Bavaria", target_type="region",
        started_turn=int(world.current_turn), original_command="march to Bavaria",
        path=["Bavaria"])
    davout.pending_interrupt = {
        "marshal": "Davout", "interrupt_type": "cannon_fire",
        "battle_location": "Swabia", "requires_input": True,
        "options": ["investigate", "continue_order", "hold_position"],
        "message": "Davout: 'Cannon fire at Swabia, Sire. Investigate?'"}
    return davout


class TestTheRepromptConsumesNothing:
    def test_no_popup_is_drained_and_the_costs_ride(self, shipped):
        client, world = shipped
        davout = _cannon_fire(world)
        world.diplomatic_sabotage_popup = {"title": "staged", "message": "staged"}
        r = post(client, "should we investigate?")
        assert r.get("success") is False
        assert world.diplomatic_sabotage_popup is not None   # still queued
        from backend.commands.strategic import interrupt_option_costs
        costs = interrupt_option_costs(davout.pending_interrupt, world)
        assert costs, "the staged interrupt quotes no cost — the pin would prove nothing"
        assert (r.get("pending_interrupt") or {}).get("option_costs") == costs
        assert davout.strategic_order is not None and davout.pending_interrupt

    def test_lever_down_the_first_cut_drops_the_costs(self, shipped, monkeypatch):
        client, world = shipped
        _cannon_fire(world)
        monkeypatch.setattr(M, "A_QUESTION_REPROMPT_CONSUMES_NOTHING", False)
        r = post(client, "should we investigate?")
        assert "option_costs" not in (r.get("pending_interrupt") or {})

    def test_a_relayed_tail_waits_on(self, shipped):
        client, world = shipped
        _cannon_fire(world)
        world._pending_relay = {"tail": "then fortify", "marshal": "Davout",
                                "head_action": "move", "turn": int(world.current_turn)}
        post(client, "should we investigate?")
        assert (getattr(world, "_pending_relay", None) or {}).get("tail") == "then fortify"


# ═══════════════════════ SF5-RV10 — a satellite courts as its lord ═══════════════════════

class TestASatelliteCourtsAsItsLord:
    def test_frances_satellite_spares_the_client_of_frances_ally(self, shipped, monkeypatch):
        _client, world = shipped
        assert world.get_diplomatic_state("France", "Spain") in ("ALLIANCE", "DEFENSIVE_ALLIANCE")
        assert V.courtier_is_the_lords_ally(world, "Holland", {"lord": "Spain"}) is True
        monkeypatch.setattr(V, "A_SATELLITE_COURTS_AS_ITS_LORD", False)
        assert V.courtier_is_the_lords_ally(world, "Holland", {"lord": "Spain"}) is False


# ═══════════════════════ SF5-RV11 — the hint memory follows the row ═══════════════════════

class TestTheHintMemoryFollowsTheRow:
    def test_a_released_court_loses_its_mark(self, shipped):
        _client, world = shipped
        world.vassal_hint_spent = ["Switzerland"]
        world.vassals.pop("Switzerland", None)
        V.process_vassal_loyalty(world)
        assert "Switzerland" not in world.vassal_hint_spent

    def test_lever_down_the_mark_outlives_the_row(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(V, "THE_HINT_MEMORY_FOLLOWS_THE_ROW", False)
        world.vassal_hint_spent = ["Switzerland"]
        world.vassals.pop("Switzerland", None)
        V.process_vassal_loyalty(world)
        assert "Switzerland" in world.vassal_hint_spent


# ═══════════════════════ SF5-RV12 — the cascade line keeps the fog ═══════════════════════

class TestTheCascadeLineKeepsTheFog:
    def _rival_cascade(self, world, monkeypatch):
        world.vassals["Switzerland"]["lord"] = "Austria"
        world.vassals["Switzerland"]["loyalty"] = 10
        world.diplomatic_states[world._make_diplo_key("Austria", "France")] = "WAR"
        from backend.game_logic import diplomacy
        monkeypatch.setattr(diplomacy, "get_war_score_for", lambda w, a, b: -40)
        monkeypatch.setattr(V.random, "random", lambda: 0.0)
        world.cascade_triggered = set()
        return [e for e in V.check_defection_cascade(world)
                if e.get("vassal") == "Switzerland"]

    def test_a_rival_lords_satellite_carries_its_fog_keys(self, shipped, monkeypatch):
        _client, world = shipped
        events = self._rival_cascade(world, monkeypatch)
        assert events, "the staged cascade did not fire"
        event = events[0]
        assert event["nation"] == "Austria"
        assert event["location"] == world.get_nation_capital("Switzerland")
        assert "Switzerland is wavering" in event["message"]
        from backend.commands.meta_executor import _filter_tactical_events_by_fog
        world.intel.pop(event["location"], None)
        assert _filter_tactical_events_by_fog([event], world) == []

    def test_lever_down_the_event_has_no_fog_key(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(V, "THE_CASCADE_LINE_KEEPS_THE_FOG", False)
        events = self._rival_cascade(world, monkeypatch)
        assert events and "location" not in events[0]
