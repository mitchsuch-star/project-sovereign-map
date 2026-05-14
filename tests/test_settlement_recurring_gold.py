"""SC-33 / G2-Slice-9 - Recurring Gold Payments.

Behavior tests for the cleanup slice that flips `gold_per_turn` from
hidden to live in the settlement editor, lands the validator bounds
(`amount >= 10`, `1 <= turns <= 20`) plus projected-solvency budget
conflict, registers ratified obligations on
`world.recurring_settlement_payments`, and processes one tick per
income phase through `process_recurring_settlement_payments`.

The 4 spec-required tests are:

- `test_gold_per_turn_absent_until_recurring_payment_slice_lands`
- `test_gold_per_turn_authors_preview_mutates_and_records_recurring_payment`
- `test_gold_per_turn_affordability_and_duration_validation`
- `test_gold_per_turn_history_and_voice_explain_recurring_obligation`

Secondary coverage:

- Clause control schema live + required keys
- Validator amount-too-small / duration-out-of-range / budget conflict
- Ratification registers obligation, does not move gold immediately
- Tick transfers, decrements `turns_remaining`, completion drops record
- Partial payment when payer balance < amount
- Cancellation conditions: payer eliminated, payer vassalized,
  recipient eliminated, renewed war between pair
- Save/load round-trip preserves recurring obligations
- `applied_clauses_preview` rows carry payer_balance_before /
  payer_balance_after_first_payment / projected_total_obligation /
  first_payment_turn
- Harshness projection uses `amount * turns`
- Voice Bible families registered
- Smoke fixture exists
"""

from __future__ import annotations

import copy
import os
from unittest.mock import patch

from backend.display_names import settlement_disabled_reason_display
from backend.game_logic.diplomatic_templates import (
    SETTLEMENT_VOICE_TEMPLATES,
    calculate_raw_treaty_harshness,
)
from backend.game_logic.settlement_preview import (
    _apply_settlement_terms,
    _check_gold_payment_budget_conflict,
    process_recurring_settlement_payments,
    ratify_settlement_confirm,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.game_logic.settlement_presentation import (
    build_applied_clauses_preview,
)
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONTROL_SCHEMA,
    GOLD_PER_TURN_MAX_TURNS,
    GOLD_PER_TURN_MIN_AMOUNT,
    GOLD_PER_TURN_MIN_TURNS,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
    SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES,
)
from backend.models.world_state import (
    SMOKE_START_ENV,
    SMOKE_START_SETTLEMENT_RECURRING_GOLD,
    WorldState,
)
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixture helpers
# ═══════════════════════════════════════════════════════════════════════════


def _install_recurring_gold_war(world: WorldState) -> dict:
    """Install a France vs Britain + Prussia war suitable for recurring
    gold authoring tests. France is the proposer-side leader; Britain is
    the accepting leader and natural recipient.
    """
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Britain", "Prussia"],
        attacker_leader="France",
        defender_leader="Britain",
        created_turn=2,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 0
        world.battle_records[pair] = []
    world.current_turn = 5
    world.nation_gold["France"] = 2000
    world.nation_gold["Britain"] = 500
    world.invalidate_war_instance_indexes()
    return war


# ═══════════════════════════════════════════════════════════════════════════
# Required #1 — `gold_per_turn` is no longer absent under SC-33.
# ═══════════════════════════════════════════════════════════════════════════


class TestSliceRequired:
    def test_gold_per_turn_absent_until_recurring_payment_slice_lands(self):
        # SC-33 / G2-Slice-9 - DWL-SET-SC33 inversion: the slice landing
        # this test removes the prior absence assertion and proves the
        # clause is now live, authorable, validated, and ratifiable.
        assert "gold_per_turn" in SETTLEMENT_LIVE_CLAUSE_TYPES
        assert "gold_per_turn" in SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES
        row = CLAUSE_CONTROL_SCHEMA["gold_per_turn"]
        assert row["enabled"] is True
        assert row["visibility"] == "live"
        assert row["required_keys"] == sorted(
            CANONICAL_CLAUSE_TYPES["gold_per_turn"]["required"]
        )

    def test_gold_per_turn_authors_preview_mutates_and_records_recurring_payment(self):
        # Author → preview → ratify path. Ratification must register an
        # obligation on `world.recurring_settlement_payments` (not move
        # gold immediately), and the first per-turn tick must transfer
        # the amount.
        world = WorldState()
        _install_recurring_gold_war(world)
        terms = [
            {"type": "peace"},
            {
                "type": "gold_per_turn",
                "from": "France",
                "to": "Britain",
                "amount": 100,
                "turns": 5,
            },
        ]
        validation = validate_settlement_terms(
            terms, actor_nation="France", player_nation="France", world=world,
        )
        assert validation["valid"] is True, validation
        # Direct mutation through the apply helper (settles the preview
        # / ratify contract without standing up the full dialogue
        # state machine that other tests cover).
        applied = _apply_settlement_terms(
            world,
            settlement_terms=terms,
            war_id="war_1",
            settlement_route_id="settlement:war_1:5:1",
        )
        assert any(c.get("type") == "gold_per_turn" for c in applied)
        # Ratification did NOT move gold immediately; the first payment
        # lands on the next turn's income phase tick.
        assert world.nation_gold["France"] == 2000
        assert world.nation_gold["Britain"] == 500
        # Obligation registered on world state.
        assert len(world.recurring_settlement_payments) == 1
        obligation = world.recurring_settlement_payments[0]
        assert obligation["from"] == "France"
        assert obligation["to"] == "Britain"
        assert obligation["amount_per_turn"] == 100
        assert obligation["turns_remaining"] == 5
        assert obligation["total_turns"] == 5
        assert obligation["war_id"] == "war_1"
        assert obligation["settlement_route_id"] == "settlement:war_1:5:1"
        assert obligation["payment_id"].startswith("recurring_gold:France:Britain:")

    def test_gold_per_turn_affordability_and_duration_validation(self):
        # SC-33 validator bounds: amount >= 10, 1 <= turns <= 20, and
        # the projected-solvency budget conflict refuses unaffordable
        # combined obligations.
        world = WorldState()
        _install_recurring_gold_war(world)
        # Amount too small.
        bad_amount = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 5, "turns": 3,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert bad_amount["valid"] is False
        assert bad_amount["error"] == "gold_per_turn_amount_too_small"
        # Duration below minimum.
        bad_low = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 100, "turns": 0,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert bad_low["valid"] is False
        assert bad_low["error"] == "gold_per_turn_duration_out_of_range"
        # Duration above max.
        bad_high = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 100, "turns": GOLD_PER_TURN_MAX_TURNS + 1,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert bad_high["valid"] is False
        assert bad_high["error"] == "gold_per_turn_duration_out_of_range"
        # Budget conflict: amount * turns > current_gold + max(0, net_income) * max_turns.
        world.nation_gold["France"] = 50
        # Strip France's regions so net income is 0.
        for region in world.regions.values():
            if region.controller == "France":
                region.controller = "Britain"
        world.nation_gold["France"] = 50
        bad_budget = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 100, "turns": 5,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert bad_budget["valid"] is False
        assert bad_budget["error"] == "gold_payment_budget_conflict"

    def test_gold_per_turn_history_and_voice_explain_recurring_obligation(self):
        # Dispatch templates + Voice Bible families are wired for the
        # authored / ratified / completed / partial / cancelled phases.
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES
        for ev in (
            "settlement_recurring_gold_paid",
            "settlement_recurring_gold_partial",
            "settlement_recurring_gold_completed",
            "settlement_recurring_gold_cancelled",
        ):
            assert ev in _DIPLOMATIC_EVENT_TEMPLATES, ev
            tmpl = _DIPLOMATIC_EVENT_TEMPLATES[ev]
            # Each dispatch line names the from / to nation + war (or
            # cancellation reason) so the player can read it cold.
            assert "{from_nation}" in tmpl
            assert "{to_nation}" in tmpl
        for fam in (
            "settlement_recurring_gold_authored_talleyrand",
            "settlement_recurring_gold_ratified_talleyrand",
            "settlement_recurring_gold_completed_talleyrand",
        ):
            assert fam in SETTLEMENT_VOICE_TEMPLATES, fam
            body = SETTLEMENT_VOICE_TEMPLATES[fam]
            assert "TODO" not in body.upper(), fam
            # Each Talleyrand line frames recurring obligation directly.
            assert (
                "recurring" in body.lower()
                or "per turn" in body.lower()
                or "installment" in body.lower()
                or "obligation" in body.lower()
                or "gold" in body.lower()
            ), fam


# ═══════════════════════════════════════════════════════════════════════════
# Validator behavior (negative + positive cases)
# ═══════════════════════════════════════════════════════════════════════════


class TestValidator:
    def test_gold_per_turn_minimum_amount_accepted(self):
        world = WorldState()
        _install_recurring_gold_war(world)
        result = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": GOLD_PER_TURN_MIN_AMOUNT, "turns": 1,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert result["valid"] is True, result

    def test_gold_per_turn_maximum_duration_accepted(self):
        world = WorldState()
        _install_recurring_gold_war(world)
        # Use a small per-turn amount so the budget projection passes.
        result = validate_settlement_terms(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": GOLD_PER_TURN_MIN_AMOUNT,
                "turns": GOLD_PER_TURN_MAX_TURNS,
            }],
            actor_nation="France", player_nation="France", world=world,
        )
        assert result["valid"] is True, result

    def test_gold_payment_budget_conflict_helper_returns_no_conflict_when_solvent(self):
        world = WorldState()
        _install_recurring_gold_war(world)
        # France has 2000 gold + region income; small obligations pass.
        terms = [{
            "type": "gold_per_turn", "from": "France",
            "to": "Britain", "amount": 50, "turns": 3,
        }]
        assert _check_gold_payment_budget_conflict(world, terms) is None

    def test_gold_payment_budget_conflict_helper_includes_lump_sum(self):
        # Lump-sum gold + recurring gold combine into the same payer's
        # obligation; total > capacity must trigger
        # `gold_payment_budget_conflict`.
        world = WorldState()
        _install_recurring_gold_war(world)
        world.nation_gold["France"] = 100
        for region in world.regions.values():
            if region.controller == "France":
                region.controller = "Britain"
        terms = [
            {
                "type": "gold_indemnity", "from": "France",
                "to": "Britain", "amount": 80,
            },
            {
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 50, "turns": 4,
            },
        ]
        result = _check_gold_payment_budget_conflict(world, terms)
        assert result is not None
        assert result["error"] == "gold_payment_budget_conflict"

    def test_validator_humanized_disabled_reason_codes_present(self):
        # Display registry exposes humanized copy for each new SC-33
        # refusal code so the editor never leaks raw internal strings.
        assert "Recurring gold payments" in settlement_disabled_reason_display(
            "gold_per_turn_amount_too_small"
        )
        assert "1 and 20" in settlement_disabled_reason_display(
            "gold_per_turn_duration_out_of_range"
        )
        assert "obligation" in settlement_disabled_reason_display(
            "gold_payment_budget_conflict"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Ratification mutation + turn processing
# ═══════════════════════════════════════════════════════════════════════════


class TestRecurringObligationProcessing:
    def _seed_obligation(
        self, world: WorldState, *, amount: int = 100, turns: int = 3,
        leave_at_war: bool = False,
    ) -> dict:
        _install_recurring_gold_war(world)
        terms = [{
            "type": "gold_per_turn", "from": "France",
            "to": "Britain", "amount": amount, "turns": turns,
        }]
        _apply_settlement_terms(
            world, settlement_terms=terms,
            war_id="war_1",
            settlement_route_id="settlement:war_1:5:1",
        )
        if not leave_at_war:
            # Real ratification transitions the bilateral state to
            # PEACE before the next turn's income phase. Tick tests
            # mirror that contract so the `renewed_war` cancellation
            # does not preempt the per-turn tick.
            for pair in list(world.diplomatic_states.keys()):
                if (
                    "France" in pair.split("|")
                    and "Britain" in pair.split("|")
                ):
                    world.diplomatic_states[pair] = "PEACE"
        assert len(world.recurring_settlement_payments) == 1
        return world.recurring_settlement_payments[0]

    def test_first_turn_tick_transfers_gold_and_decrements_remaining(self):
        world = WorldState()
        self._seed_obligation(world, amount=200, turns=3)
        france_before = world.nation_gold["France"]
        britain_before = world.nation_gold["Britain"]
        events = process_recurring_settlement_payments(world)
        assert world.nation_gold["France"] == france_before - 200
        assert world.nation_gold["Britain"] == britain_before + 200
        assert world.recurring_settlement_payments[0]["turns_remaining"] == 2
        assert len(events["paid"]) == 1
        assert events["paid"][0]["amount_paid"] == 200

    def test_partial_payment_when_balance_below_amount_keeps_obligation_alive(self):
        world = WorldState()
        self._seed_obligation(world, amount=300, turns=2)
        world.nation_gold["France"] = 100  # Less than `amount`
        events = process_recurring_settlement_payments(world)
        # Only `min(amount, balance)` transferred.
        assert world.nation_gold["France"] == 0
        # Obligation still alive; turn was consumed.
        assert len(world.recurring_settlement_payments) == 1
        assert world.recurring_settlement_payments[0]["turns_remaining"] == 1
        assert len(events["partial"]) == 1
        assert events["partial"][0]["amount_paid"] == 100
        assert events["partial"][0]["amount_due"] == 300

    def test_natural_completion_drops_record_and_emits_completed_event(self):
        world = WorldState()
        self._seed_obligation(world, amount=50, turns=2)
        process_recurring_settlement_payments(world)
        events = process_recurring_settlement_payments(world)
        assert world.recurring_settlement_payments == []
        assert len(events["completed"]) == 1
        assert events["completed"][0]["total_amount"] == 100

    def test_cancellation_when_recipient_eliminated(self):
        world = WorldState()
        self._seed_obligation(world, amount=50, turns=5)
        world.nation_gold.pop("Britain", None)
        events = process_recurring_settlement_payments(world)
        assert world.recurring_settlement_payments == []
        assert len(events["cancelled"]) == 1
        assert events["cancelled"][0]["reason"] == "recipient_eliminated"

    def test_cancellation_when_payer_eliminated(self):
        world = WorldState()
        self._seed_obligation(world, amount=50, turns=5)
        world.nation_gold.pop("France", None)
        events = process_recurring_settlement_payments(world)
        assert world.recurring_settlement_payments == []
        assert len(events["cancelled"]) == 1
        assert events["cancelled"][0]["reason"] == "payer_eliminated"

    def test_cancellation_when_payer_vassalized(self):
        world = WorldState()
        self._seed_obligation(world, amount=50, turns=5)
        world.vassals["France"] = {"lord": "Britain"}
        events = process_recurring_settlement_payments(world)
        assert world.recurring_settlement_payments == []
        assert len(events["cancelled"]) == 1
        assert events["cancelled"][0]["reason"] == "payer_vassalized"

    def test_cancellation_when_renewed_war_between_payer_and_recipient(self):
        # Real ratification transitions the pair to PEACE; this test
        # simulates a *renewed* war afterwards by leaving (or
        # restoring) the pair at WAR before the next tick.
        world = WorldState()
        self._seed_obligation(world, amount=50, turns=5, leave_at_war=True)
        events = process_recurring_settlement_payments(world)
        assert world.recurring_settlement_payments == []
        assert len(events["cancelled"]) == 1
        assert events["cancelled"][0]["reason"] == "renewed_war"


# ═══════════════════════════════════════════════════════════════════════════
# Applied clauses preview value fields
# ═══════════════════════════════════════════════════════════════════════════


class TestAppliedClausesPreview:
    def test_preview_row_carries_amount_turns_and_projected_total(self):
        world = WorldState()
        _install_recurring_gold_war(world)
        rows = build_applied_clauses_preview(
            [{
                "type": "gold_per_turn", "from": "France",
                "to": "Britain", "amount": 75, "turns": 4,
            }],
            world=world,
        )
        assert len(rows) == 1
        row = rows[0]
        assert row["type"] == "gold_per_turn"
        assert row["amount"] == 75
        assert row["turns"] == 4
        assert row["projected_total_obligation"] == 300
        assert row["payer_balance_before"] == world.nation_gold["France"]
        assert row["payer_balance_after_first_payment"] == max(
            0, world.nation_gold["France"] - 75
        )
        assert row["first_payment_turn"] == world.current_turn + 1


# ═══════════════════════════════════════════════════════════════════════════
# Save / load round-trip
# ═══════════════════════════════════════════════════════════════════════════


class TestSaveLoadRoundTrip:
    def test_recurring_obligation_round_trips_save_load(self):
        world = WorldState()
        _install_recurring_gold_war(world)
        world.recurring_settlement_payments.append({
            "payment_id": "recurring_gold:France:Britain:5:0",
            "from": "France",
            "to": "Britain",
            "amount_per_turn": 80,
            "turns_remaining": 4,
            "total_turns": 5,
            "war_id": "war_1",
            "ratified_turn": 5,
            "settlement_route_id": "settlement:war_1:5:1",
            "source_clause_index": 1,
        })
        snapshot = world.to_dict()
        assert "recurring_settlement_payments" in snapshot
        reloaded = WorldState.from_dict(snapshot)
        assert len(reloaded.recurring_settlement_payments) == 1
        loaded = reloaded.recurring_settlement_payments[0]
        assert loaded["payment_id"] == "recurring_gold:France:Britain:5:0"
        assert loaded["amount_per_turn"] == 80
        assert loaded["turns_remaining"] == 4

    def test_default_empty_for_pre_sc33_saves(self):
        # New-field-default-empty: a snapshot without the recurring field
        # loads to an empty list, not a crash.
        world = WorldState()
        snapshot = world.to_dict()
        snapshot.pop("recurring_settlement_payments", None)
        reloaded = WorldState.from_dict(snapshot)
        assert reloaded.recurring_settlement_payments == []


# ═══════════════════════════════════════════════════════════════════════════
# Harshness projection uses amount * turns
# ═══════════════════════════════════════════════════════════════════════════


class TestHarshnessProjection:
    def test_harshness_projects_full_amount_times_turns_for_finite_stream(self):
        # SC-33 / G2-Slice-9 - finite settlement-style `gold_per_turn`
        # (with explicit `turns`) projects to lump-sum weight on the
        # full obligation. 100 gold/turn for 10 turns = 1000 gold
        # projected; 0.08 / 100 weight = 0.8 harshness contribution.
        treaty = {
            "clauses": [],
            "demands": [
                {
                    "type": "gold_per_turn", "from": "France",
                    "to": "Britain", "amount": 100, "turns": 10,
                },
            ],
        }
        h = calculate_raw_treaty_harshness(treaty)
        assert h > 0.7, h  # Approx 0.8 (allow tolerance)
        assert h < 0.9, h

    def test_bilateral_perpetual_stream_keeps_per_turn_weight(self):
        # A `gold_per_turn` demand without a `turns` field is the legacy
        # bilateral perpetual stream; harshness uses the per-turn weight
        # so existing bilateral acceptance is not perturbed.
        treaty = {
            "clauses": [],
            "demands": [
                {"type": "gold_per_turn", "value": 100},
            ],
        }
        h = calculate_raw_treaty_harshness(treaty)
        assert 0.05 < h < 0.15


# ═══════════════════════════════════════════════════════════════════════════
# Smoke fixture seeding
# ═══════════════════════════════════════════════════════════════════════════


class TestSmokeFixture:
    def test_smoke_start_recurring_gold_seeds_war_and_fixture_metadata(self):
        with patch.dict(
            os.environ, {SMOKE_START_ENV: SMOKE_START_SETTLEMENT_RECURRING_GOLD},
        ):
            world = WorldState()
        assert world.settlement_smoke_fixture.get("name") == (
            SMOKE_START_SETTLEMENT_RECURRING_GOLD
        )
        assert world.settlement_smoke_fixture.get("expected_recurring_payer") == "France"
        assert world.settlement_smoke_fixture.get("expected_recurring_recipient") == "Britain"
        assert world.nation_gold["France"] >= 1500
        assert "war_1" in world.war_instances


# ═══════════════════════════════════════════════════════════════════════════
# Wizard / Godot command path (action id whitelist)
# ═══════════════════════════════════════════════════════════════════════════


class TestWizardCommandPath:
    def test_propose_common_peace_with_gold_per_turn_payload_revalidates(self):
        # Validate that the executor accepts a structured payload with a
        # gold_per_turn clause and forwards it through the validator.
        from backend.commands.diplomatic_executor import DiplomaticExecutor

        world = WorldState()
        _install_recurring_gold_war(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        cmd = {
            "action": "propose_common_peace",
            "war_id": "war_1",
            "selected_target_nation": "Britain",
            "covered_enemy_participants": ["Britain", "Prussia"],
            "settlement_terms": [
                {
                    "type": "gold_per_turn", "from": "France",
                    "to": "Britain", "amount": 100, "turns": 3,
                },
            ],
            "caller_kind": "player_editor",
        }
        result = executor._execute_propose_common_peace(cmd, {"world": world})
        # The executor either succeeds and stages a dialogue, or rejects
        # for unrelated reasons (multi-war ambiguity, acceptance, etc.).
        # The point is that the SC-33 validator did not reject the
        # structured payload as `invalid_clause_type` or
        # `invalid_clause_schema`.
        if not result.get("success"):
            assert result.get("error") not in {
                "invalid_clause_type",
                "invalid_clause_schema",
                "submitted_terms_failed_revalidation",
            }, result
