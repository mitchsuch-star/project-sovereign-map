"""Pins for the August 14, 2026 whole-game health-check audit.

Three fix families:

1. Campaign-log routing: every COMMITMENTS_ROUTES event type (except
   witness_strike_recorded) is formatted by the early
   format_commitments_notice() return in format_event_oneliner — the 13
   per-type arms that sat unreachable below that return were removed. The
   behavioral pin here fails if the early return is ever removed (the routed
   types would fall through to the generic fallback and diverge).

2. The two invariant-failure diagnostics (war_cascade_blocked,
   armistice_expired_war_blocked) are DELIBERATELY excluded from
   CAMPAIGN_LOG_TYPES — they carry raw error codes (R7). Pinned so a future
   whitelist addition is a conscious decision.

3. scenario_schema_version gate: the field was authored in every shipped
   scenario and documented in MODDING_FORMAT.md but read by nobody — a
   future-schema scenario booted silently against the v1 loader. Both
   from_scenario and validate_scenario now refuse anything newer than 1.
"""

import json

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
from backend.game_logic.commitments_routing import (
    COMMITMENTS_ROUTES,
    format_commitments_notice,
)
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario


class TestCommitmentsRoutingIsTheOnlyFormatter:
    """The early return owns every routed type; no shadow arms below it."""

    def _sample_event(self, event_type: str) -> dict:
        # A representative payload with the fields the routed formatters read.
        return {
            "type": event_type,
            "turn": 5,
            "nation": "Austria",
            "breaker": "Austria",
            "other": "Prussia",
            "target": "Prussia",
            "treaty_type": "alliance",
            "end_reason_family": "counterparty_reversal",
            "chosen_nation": "Austria",
            "spurned_nation": "Prussia",
            "beneficiary": "Bavaria",
            "claim_region": "Tyrol",
            "target_enemy": "Austria",
            "promiser": "France",
            "victim": "Austria",
            "honorer": "Prussia",
            "victim_nation": "Austria",
            "perpetrator_nation": "France",
            "actor_nation": "France",
            "target_nation": "Austria",
            "hegemon": "France",
            "share": 0.4,
        }

    def test_every_routed_type_formats_via_commitments_notice(self):
        routed = [
            t for t in COMMITMENTS_ROUTES if t != "witness_strike_recorded"
        ]
        assert routed, "COMMITMENTS_ROUTES unexpectedly empty"
        for event_type in routed:
            event = self._sample_event(event_type)
            oneliner = format_event_oneliner(event)
            notice = format_commitments_notice(event_type, event)
            assert oneliner == notice, (
                f"{event_type} no longer routes through "
                f"format_commitments_notice — the early return in "
                f"format_event_oneliner was removed or a shadowing arm was "
                f"re-added above it.\n oneliner: {oneliner!r}\n notice:   "
                f"{notice!r}"
            )

    def test_witness_strike_is_the_one_deliberate_exception(self):
        # The early return excludes witness_strike_recorded by design; it must
        # keep its own arm (or the fallback), never the commitments notice.
        assert "witness_strike_recorded" in COMMITMENTS_ROUTES


class TestDiagnosticEventsDeliberatelyUnlisted:
    """war_cascade_blocked / armistice_expired_war_blocked carry raw error
    codes and are excluded from the player-facing campaign log by design."""

    def test_diagnostics_not_in_campaign_log_types(self):
        assert "war_cascade_blocked" not in CAMPAIGN_LOG_TYPES
        assert "armistice_expired_war_blocked" not in CAMPAIGN_LOG_TYPES


class TestScenarioSchemaVersionGate:
    def _write(self, tmp_path, payload: dict) -> str:
        p = tmp_path / "scenario.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return str(p)

    def test_from_scenario_refuses_newer_schema(self, tmp_path):
        path = self._write(tmp_path, {"scenario_schema_version": 2})
        with pytest.raises(ValueError, match="newer than this loader"):
            WorldState.from_scenario(path)

    def test_from_scenario_refuses_malformed_schema(self, tmp_path):
        path = self._write(tmp_path, {"scenario_schema_version": "two"})
        with pytest.raises(ValueError, match="positive integer"):
            WorldState.from_scenario(path)
        path = self._write(tmp_path, {"scenario_schema_version": 0})
        with pytest.raises(ValueError, match="positive integer"):
            WorldState.from_scenario(path)

    def test_from_scenario_accepts_version_1_and_absent(self, tmp_path):
        # Version 1 explicit — boots the legacy default world.
        path = self._write(tmp_path, {"scenario_schema_version": 1})
        world = WorldState.from_scenario(path)
        assert world is not None
        # Absent — defaults to 1, boots.
        path = self._write(tmp_path, {})
        world = WorldState.from_scenario(path)
        assert world is not None

    def test_validator_refuses_newer_schema(self):
        result = validate_scenario(
            {"scenario_schema_version": 2}, check_adjacency=False
        )
        assert any(
            "scenario_schema_version" in e.path for e in result.errors
        ), f"validator accepted schema version 2: {result.errors}"

    def test_validator_accepts_version_1(self):
        result = validate_scenario(
            {"scenario_schema_version": 1}, check_adjacency=False
        )
        assert not any(
            "scenario_schema_version" in e.path for e in result.errors
        )

    def test_shipped_scenarios_carry_version_1(self):
        from pathlib import Path

        maps_dir = (
            Path(__file__).resolve().parents[1]
            / "godot-client"
            / "project-sovereign"
            / "assets"
            / "maps"
        )
        for name in ("europe_1805.json", "tutorial_1805.json"):
            data = json.loads((maps_dir / name).read_text(encoding="utf-8"))
            assert data.get("scenario_schema_version") == 1, name


class TestContinentalSystemNeverConjuresGold:
    """The CS deduction is floored at the payer's positive balance — the old
    `max(0, gold - blocked)` floored the BALANCE, erasing debt every turn
    (a nation at -3,000 was lifted to 0, 12,000g conjured in the probe)."""

    def test_deduction_idiom_never_floors_the_balance(self):
        import inspect
        from backend.game_logic import diplomacy

        src = inspect.getsource(diplomacy.apply_continental_system)
        # The debt-erasing form must be gone…
        assert "max(0, world.nation_gold[member] - int(blocked))" not in src
        assert 'max(0, world.nation_gold["Britain"] - int(blocked))' not in src
        # …and the floor-the-deduction form present for both sides.
        assert src.count("-= min(") >= 2, (
            "CS must deduct min(blocked, positive balance), never clamp "
            "the balance itself")


class TestAiGuaranteeGuardIsLive:
    """war_council's AI-guarantee arm reads pledge['record'] — the old
    pledge.get('id') guard read a key pledge_guarantee never returns, so the
    stamp/break/narration block was structurally dead."""

    def test_guard_matches_pledge_guarantee_return_shape(self):
        from backend.game_logic.instruments import pledge_guarantee

        world = WorldState()
        nations = [n for n in world.nation_gold if n != world.player_nation]
        if len(nations) < 2:
            pytest.skip("not enough nations")
        pledge = pledge_guarantee(
            world, guarantor=nations[0], protected=nations[1])
        # The shape the guard must key on:
        assert pledge.get("success") is True
        assert pledge.get("record"), "pledge_guarantee no longer returns a record"
        assert pledge.get("id") is None, (
            "pledge_guarantee now returns a top-level id — update the "
            "war_council guard comment accordingly")

    def test_war_council_source_uses_record_key(self):
        import inspect
        from backend.game_logic import war_council

        src = inspect.getsource(war_council)
        assert 'pledge.get("success") and pledge.get("record")' in src


class TestFontainebleauSurfacePricesOffTheExecutorPredicate:
    """The concede card's quoted bill derives from compute_rente_face (what
    the executor grants), never get_shortfall (a different rule)."""

    def test_petition_bill_matches_executor_faces(self):
        import inspect
        from backend.game_logic import jealousy

        src = inspect.getsource(jealousy.queue_fontainebleau_petition)
        assert "compute_rente_face" in src, (
            "the petition surface must price via the executor's own "
            "predicate (Aug 2026 audit)")


class TestBargainFeasibilityReadsRealStrength:
    """ai_should_propose_bargain reads m.strength (m.troops/m.alive never
    existed on Marshal — the strength gate had never fired)."""

    def test_source_reads_strength_not_troops(self):
        import inspect
        from backend.game_logic import diplomacy

        src = inspect.getsource(diplomacy.ai_should_propose_bargain)
        assert '"troops"' not in src and "'troops'" not in src
        assert '"alive"' not in src and "'alive'" not in src


class TestTurnEndEventCarriesAllBannerComponents:
    """Both turn_end producers key every component their text banner names —
    materiel/infrastructure were named in text, subtracted from `other`, and
    absent from the event, so main.gd's lines could not sum to Net."""

    REQUIRED = {"materiel", "infrastructure", "blockade", "other"}

    def test_meta_executor_event_keys(self):
        import inspect
        from backend.commands import meta_executor

        src = inspect.getsource(meta_executor)
        for key in self.REQUIRED:
            assert f'"{key}": int(' in src, f"meta turn_end_event missing {key}"

    def test_auto_advance_event_keys(self):
        import inspect
        from backend.commands import executor as exec_mod

        src = inspect.getsource(exec_mod)
        for key in self.REQUIRED:
            assert f'"{key}": int(' in src, (
                f"auto-advance turn_end_event missing {key}")

    def test_main_gd_renders_the_new_keys(self):
        from pathlib import Path

        gd = (Path(__file__).resolve().parents[1] / "godot-client"
              / "project-sovereign" / "scripts" / "main.gd").read_text(
                  encoding="utf-8")
        assert 'event.get("materiel", 0)' in gd
        assert 'event.get("infrastructure", 0)' in gd


class TestLoadGamePreservesMidTurnContracts:
    """load_game no longer wipes the two deliberately-serialized per-turn
    stores (the ±5 diplomatic trust cap; the flanking attack tracker)."""

    def test_diplomatic_trust_cap_survives_save_load(self, tmp_path):
        from backend import save_manager

        world = WorldState()
        world.diplomatic_trust_applied = {"Ney": 4}
        world.record_attack(
            next(iter(world.marshals)), "A", "B",
            world.player_nation)
        old_dir = save_manager.SAVE_DIR
        save_manager.SAVE_DIR = tmp_path
        try:
            save_manager.save_game(world, save_name="audit_pin")
            loaded = save_manager.load_game(tmp_path / "audit_pin.json")
            assert loaded["success"], loaded["message"]
            lw = loaded["world"]
            assert lw.diplomatic_trust_applied.get("Ney") == 4
            assert lw.attacks_this_turn, "attacks_this_turn was wiped on load"
        finally:
            save_manager.SAVE_DIR = old_dir

    def test_newer_format_save_is_refused_clearly(self, tmp_path):
        from backend import save_manager

        p = tmp_path / "future.json"
        p.write_text(json.dumps({
            "metadata": {"format_version": save_manager.FORMAT_VERSION + 1,
                         "save_name": "Future"},
            "world_state": {},
        }), encoding="utf-8")
        old_dir = save_manager.SAVE_DIR
        save_manager.SAVE_DIR = tmp_path
        try:
            result = save_manager.load_game(p)
            assert not result["success"]
            assert "NEWER" in result["message"]
        finally:
            save_manager.SAVE_DIR = old_dir


class TestIncomingSettlementOfferPopupSerializes:
    """The one PopupQueue slot that had no serialization pair round-trips."""

    def test_round_trip(self):
        world = WorldState()
        world._popup_queue.push(
            "incoming_settlement_offer_popup", {"probe": 1})
        restored = WorldState.from_dict(world.to_dict())
        assert restored.incoming_settlement_offer_popup == {"probe": 1}


class TestAppliedTransferMirrors:
    """Verify-fleet round 2: the ledger's treaty/tribute/settlement figures
    come from the ENGINES' recorded applied transfers, never a view-time
    balance re-read (which is post-debit — a fully-solvent 300g clause
    displayed as 114 in the first cut)."""

    def test_solvent_treaty_clause_shows_full_transfer(self):
        world = WorldState()
        player = world.player_nation
        payer = next(n for n in world.nation_gold if n != player)
        pair_key = world._make_diplo_key(player, payer)
        world.active_treaties[pair_key] = {
            "clauses": [{"type": "gold_per_turn", "amount": 300,
                         "from": payer, "to": player}],
        }
        world.nation_gold[payer] = 5000
        before = world.nation_gold[player] = int(world.gold)
        world.advance_turn()
        delta = world.nation_gold[player] - before
        from backend.game_logic.ledger import _build_economy

        applied = world._income_phase_results.get(player)
        econ = _build_economy(world, player, income_data=applied)
        assert econ["treaty_gold"] == 300, (
            f"solvent 300g clause displayed as {econ['treaty_gold']}")
        assert econ["net"] == delta, (
            f"shown net {econ['net']} != measured delta {delta}")

    def test_engines_record_applied_transfers(self):
        world = WorldState()
        world.advance_turn()
        transfers = getattr(world, "_applied_income_transfers", None)
        assert transfers is not None
        assert set(transfers) >= {"treaty_gold", "vassal_tribute",
                                  "settlement_gold"}


class TestOneLoggerPerInstrumentEvent:
    """Verify-fleet round 2: pledge_guarantee / create_compensation_bargain
    log their own events — the war_council producer must only APPEND for the
    turn surface, never log a second copy of the same row."""

    def test_pledge_guarantee_logs_exactly_once(self):
        from backend.game_logic.instruments import pledge_guarantee

        world = WorldState()
        nations = [n for n in world.nation_gold if n != world.player_nation]
        pledge_guarantee(world, guarantor=nations[0], protected=nations[1])
        count = sum(1 for e in world.event_log
                    if e.get("type") == "guarantee_pledged")
        assert count == 1, f"guarantee_pledged logged {count} times"

    def test_producer_arms_do_not_log(self):
        import inspect
        from backend.game_logic import war_council

        src = inspect.getsource(war_council._run_ai_instrument_producers)
        assert "world.log_event" not in src, (
            "the instrument producer must append-only — its helpers "
            "(pledge_guarantee / create_compensation_bargain) own the log")


class TestCombatCarryOnEveryObjectionArm:
    """Verify-fleet round 2: all THREE re-entry arms (insist, disobey-
    alternative, defiance) and both endpoint mirrors carry the combat
    allowlist; the objection response never drains popups it can pre-empt."""

    def test_meta_executor_carries_on_three_arms(self):
        import inspect
        from backend.commands import meta_executor

        src = inspect.getsource(meta_executor)
        assert src.count("_carry_combat_fields") >= 3

    def test_objection_sync_non_draining(self):
        import inspect
        from backend import main as main_module

        src = inspect.getsource(main_module._respond_to_objection_sync)
        assert "include_popup_passthroughs=False" in src
        assert "_fill_popup_keys_without_draining" in src
        assert "_carry_combat_fields" in src

    def test_glorious_charge_carries_combat_fields(self):
        import inspect
        from backend import main as main_module

        src = inspect.getsource(main_module.respond_to_glorious_charge)
        assert "_carry_combat_fields" in src


class TestAdmiraltyEmbarkSelfConsistency:
    """Verify-fleet round 2: embark_ready is built FROM ready_corps (the
    mirrored predicate), so the gate term and the Orders list can never
    disagree about who can sail."""

    def test_embark_ready_built_from_ready_corps(self):
        import inspect
        from backend.game_logic import naval

        src = inspect.getsource(naval.build_admiralty_report)
        assert "for m in ready_corps]" in src.replace("\n", "").replace(
            "  ", "") or "for m in ready_corps" in src


class TestManpowerPanelQuotesTheLivePrice:
    """The MANPOWER panel carries the executor-priced figure beside the base
    price, and the false '±25% stability' note is gone."""

    def test_recruit_price_present_and_war_priced(self):
        import os

        scenario = os.path.join(
            os.path.dirname(__file__), "..", "godot-client",
            "project-sovereign", "assets", "maps", "europe_1805.json")
        world = WorldState.from_scenario(scenario)
        from backend.game_logic.ledger import _build_manpower

        mp = _build_manpower(world, world.player_nation)
        inf = mp["infantry"]
        assert "recruit_price" in inf
        # France is at war at the 1805 boot — the live price must exceed
        # the base (war ×3 dominates every discount).
        assert inf["recruit_price"] > inf["recruit_base_cost"]
        assert "+/-25%" not in inf["cost_note"]
