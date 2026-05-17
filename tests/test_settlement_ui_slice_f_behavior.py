"""Slice F settlement UI/routing behavioral tests.

Companion to `test_settlement_ui_slice_f_source.py`. The source-string
tests pin contract strings; this file pins actual behavior — return
shapes, error paths, payload field presence, side-effect assertions —
so the wiring this slice introduces cannot regress silently.

Coverage targets:
- `resolve_or_backfill_war_instance_for_settlement(requested_war_id=...)`
  for every new error code + the war-id-scoped success path.
- `handle_incoming_settlement_offer_action` for accept / reject /
  request_revision / unknown-action / empty-war-id paths.
- `CommandRequest.action` / `target_nation` / `war_id` forwarding into
  the parsed command dict.
- `_enrich_acceptance_display` shape (band / band_phrase / top_components
  with `component_display` and signed `value_display`).
- `build_contribution_share_rows` produces `side_label` and
  `is_beneficiary` for the live preview path.
- `build_settlement_review` produces `uncovered_enemy_display_chips`.
- Confirm dialogue's `route_id` matches the event-side format
  (`"{war_id}:{turn}"`) so the diplomatic-ledger focus highlight survives.
"""

from __future__ import annotations

import asyncio

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.display_names import (
    settlement_disabled_reason_display,
    side_label_display,
    SIDE_LABEL_DISPLAY,
)
from backend.game_logic.diplomacy import get_available_diplomatic_actions
from backend.game_logic.settlement_helpers import (
    resolve_or_backfill_war_instance_for_settlement,
)
from backend.game_logic.settlement_preview import (
    _enrich_acceptance_display,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    evaluate_open_settlement_eligibility,
    handle_incoming_settlement_offer_action,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_presentation import (
    build_contribution_share_rows,
    build_settlement_review,
)
from backend.game_logic.war_status import build_active_wars
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


def _install_war(world: WorldState, war_id: str = "war_1") -> dict:
    war = make_synthetic_war_instance(
        war_id,
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances[war_id] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()
    return war


# ---------------------------------------------------------------------------
# resolve_or_backfill_war_instance_for_settlement(requested_war_id=...)
# ---------------------------------------------------------------------------


def test_resolve_with_war_id_invalid_returns_invalid_war_id():
    world = WorldState()
    _install_war(world)

    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria", requested_war_id="war_does_not_exist",
    )

    assert result["ok"] is False
    assert result["error"] == "invalid_war_id"
    assert result["war_id"] == "war_does_not_exist"


def test_resolve_with_ended_war_id_returns_inactive_war_instance():
    world = WorldState()
    war = _install_war(world)
    war["ended_turn"] = 5

    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria", requested_war_id="war_1",
    )

    assert result["ok"] is False
    assert result["error"] == "inactive_war_instance"


def test_resolve_with_war_id_target_not_in_war_returns_state_changed():
    world = WorldState()
    _install_war(world)
    # Target nation that is not a participant of war_1.
    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Russia", requested_war_id="war_1",
    )

    assert result["ok"] is False
    assert result["error"] == "war_state_changed_since_open"


def test_resolve_with_war_id_same_side_returns_state_changed():
    world = WorldState()
    _install_war(world)
    # Both nations on the attackers side — would mean Austria switched.
    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Saxony", requested_war_id="war_1",
    )

    assert result["ok"] is False
    assert result["error"] == "war_state_changed_since_open"


def test_resolve_with_war_id_success_returns_war_id_scoped_flag():
    world = WorldState()
    _install_war(world)

    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria", requested_war_id="war_1",
    )

    assert result["ok"] is True
    assert result["war_id"] == "war_1"
    assert result["backfilled"] is False
    assert result["war_id_scoped"] is True


def test_resolve_without_war_id_falls_back_to_legacy_path():
    world = WorldState()
    _install_war(world)

    result = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria",
    )

    assert result["ok"] is True
    assert result["war_id"] == "war_1"
    # Legacy (non-war-id-scoped) path does not stamp war_id_scoped.
    assert "war_id_scoped" not in result


def test_resolve_disambiguates_when_two_wars_share_a_pair():
    """The whole point of the new requested_war_id parameter."""
    world = WorldState()
    _install_war(world, war_id="war_a")
    war_b = make_synthetic_war_instance(
        "war_b",
        attackers=["France", "Bavaria"],
        defenders=["Austria", "Russia"],
        attacker_leader="France",
        defender_leader="Russia",
        created_turn=2,
        created_sequence=2,
    )
    world.war_instances["war_b"] = war_b
    for pair in war_b["active_diplo_keys"]:
        world.diplomatic_states.setdefault(pair, "WAR")
    world.invalidate_war_instance_indexes()

    a = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria", requested_war_id="war_a",
    )
    b = resolve_or_backfill_war_instance_for_settlement(
        world, "France", "Austria", requested_war_id="war_b",
    )

    assert a["war_id"] == "war_a"
    assert b["war_id"] == "war_b"


# ---------------------------------------------------------------------------
# handle_incoming_settlement_offer_action
# ---------------------------------------------------------------------------


def _stage_offer_dialogue(world: WorldState, war_id: str = "war_1") -> dict:
    """Synthesize the dialogue an AI producer would push (currently
    unimplemented in this slice). Validates the handler's behavior even
    though no live producer exists yet."""
    dialogue = {
        "type": "incoming_settlement_offer",
        "dialogue_type": "incoming_settlement_offer",
        "war_id": war_id,
        "covered_enemy_participants": ["Austria"],
        "proposer_side": "defenders",
        "options": [
            {"label": "Accept", "action": "accept_settlement_offer"},
            {"label": "Reject", "action": "reject_settlement_offer"},
            {"label": "Revise", "action": "request_settlement_revision"},
        ],
        "blocking": False,
        "turn_created": world.current_turn,
    }
    world.dialogue_manager.replace(dialogue)
    return dialogue


def test_handle_incoming_offer_reject_succeeds_after_sc5_reversal():
    """SC-5 reversal (May 15, 2026 / Slice G1 commit 1): with the
    deferral flag off, `reject_settlement_offer` succeeds, removes
    the matching pending entry, and emits `mutated=False`. The
    dialogue_manager pop only fires when the offer is the active
    dialogue slot."""
    world = WorldState()
    _install_war(world)
    dialogue = _stage_offer_dialogue(world)
    # Mirror the offer into pending_settlement_dialogues so the
    # canonical cleanup path has something to remove.
    world.pending_settlement_dialogues.append(dialogue)

    result = handle_incoming_settlement_offer_action(
        world, action="reject_settlement_offer", dialogue=dialogue,
    )

    assert result["success"] is True
    assert result["action"] == "reject_settlement_offer"
    assert result["mutated"] is False
    # Pending entry removed; active offer slot popped (it was the
    # active dialogue).
    assert world.pending_settlement_dialogues == []


def test_handle_incoming_offer_revise_opens_counter_editor_after_sc5_reversal_commit2():
    """SC-5 reversal commit 2: `request_settlement_revision` opens a
    real counter editor by staging `settlement_confirm` in
    player-editor mode seeded with the offered terms. The result no
    longer surfaces a `counter_edit_hint` placeholder — it stages a
    full settlement_confirm and the original offer is removed."""
    world = WorldState()
    _install_war(world)
    dialogue = _stage_offer_dialogue(world)
    # Add the fields the counter route preserves into the staged
    # settlement_confirm. The legacy `_stage_offer_dialogue` synth was
    # written before commit 1 stabilized the offer dict shape.
    dialogue["offer_id"] = "offer_x"
    dialogue["settlement_terms"] = [{"type": "peace"}]
    dialogue["selected_target_nation"] = "Austria"
    dialogue["proposer_nation"] = "Austria"
    dialogue["accepting_side"] = "attackers"
    dialogue["accepting_leader"] = "France"

    result = handle_incoming_settlement_offer_action(
        world, action="request_settlement_revision", dialogue=dialogue,
    )

    assert result["success"] is True
    assert result["action"] == "request_settlement_revision"
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["counter_to_offer_id"] == "offer_x"
    assert result["counter_seed_terms"] == [{"type": "peace"}]


def test_handle_incoming_offer_accept_stages_settlement_confirm_after_sc5_reversal():
    """SC-5 reversal: `accept_settlement_offer` stages a real
    `settlement_confirm` for the player, removes the matching
    pending entry, and echoes the offer_id on the result."""
    world = WorldState()
    _install_war(world)
    dialogue = _stage_offer_dialogue(world)
    world.pending_settlement_dialogues.append(dialogue)

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=dialogue,
    )

    # Whatever the staging outcome (depends on the synthetic war
    # geometry), the handler must report success/failure with a real
    # error path — not the legacy `incoming_offer_deferred` no-op.
    assert result.get("error") != "incoming_offer_deferred"
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["action"] == "accept_settlement_offer"
    # Pending entry was cleaned up so the one-active-offer guard
    # resets for the next producer tick.
    assert world.pending_settlement_dialogues == []


def test_handle_incoming_offer_accept_with_empty_war_id_returns_invalid_war_id():
    """SC-5 reversal: empty-`war_id` accept now reaches the SC-7b
    canonical humanized rejection path."""
    world = WorldState()
    _install_war(world)
    dialogue = _stage_offer_dialogue(world, war_id="")

    result = handle_incoming_settlement_offer_action(
        world, action="accept_settlement_offer", dialogue=dialogue,
    )

    assert result["success"] is False
    assert result["error"] == "invalid_war_id"
    assert result["error_display"] == settlement_disabled_reason_display(
        "invalid_war_id"
    )
    assert result["mutated"] is False


def test_handle_incoming_offer_unknown_action_returns_unknown_action_error():
    """SC-5 reversal: unknown offer actions now return the canonical
    `unknown_settlement_offer_action` error rather than the legacy
    deferred short-circuit."""
    world = WorldState()
    _install_war(world)
    dialogue = _stage_offer_dialogue(world)

    result = handle_incoming_settlement_offer_action(
        world, action="not_a_real_action", dialogue=dialogue,
    )

    assert result["success"] is False
    assert result["error"] == "unknown_settlement_offer_action"
    assert result["mutated"] is False


# ---------------------------------------------------------------------------
# CommandRequest action / target_nation / war_id forwarding
# ---------------------------------------------------------------------------


def test_command_request_model_accepts_optional_structured_fields():
    """The structured fields land on the parsed command dict so the
    diplomatic_executor can read `cmd.get("war_id")` directly."""
    from backend.main import CommandRequest

    req = CommandRequest(
        command="propose common peace with Austria",
        action="propose_common_peace",
        target_nation="Austria",
        war_id="war_1",
    )

    assert req.command == "propose common peace with Austria"
    assert req.action == "propose_common_peace"
    assert req.target_nation == "Austria"
    assert req.war_id == "war_1"


def test_command_request_model_accepts_command_only():
    """Backwards compatibility: legacy POST bodies without the new fields
    must continue to work."""
    from backend.main import CommandRequest

    req = CommandRequest(command="propose common peace with Austria")

    assert req.action is None
    assert req.target_nation is None
    assert req.war_id is None


def test_diplomatic_dialogue_endpoint_preserves_must_reopen(monkeypatch):
    """Revise Terms depends on `must_reopen` reaching Godot.

    Without this passthrough, the backend returns only text and a
    reopen_target; main.gd never reopens the settlement popup flow.
    """
    import backend.main as main_module

    class FakeWorld:
        game_over = False
        pending_diplomatic_dialogue = {
            "type": "settlement_confirm",
            "war_id": "war_1",
        }
        proposal_result_popup = None

    class FakeExecutor:
        def handle_diplomatic_dialogue_response(self, choice, game_state):
            assert choice == 2
            return {
                "success": True,
                "message": "Reopen this settlement review to revise terms.",
                "must_reopen": True,
                "reopen_target": {
                    "surface": "settlement_review",
                    "war_id": "war_1",
                    "target_nation": "Austria",
                },
                "suppress_proposal_result_popup": True,
            }

    monkeypatch.setattr(main_module, "world", FakeWorld())
    monkeypatch.setattr(main_module, "game_state", {"world": main_module.world})
    monkeypatch.setattr(main_module, "executor", FakeExecutor())
    monkeypatch.setattr(
        main_module,
        "build_base_response",
        lambda world, success, message, **_kwargs: {
            "success": success,
            "message": message,
        },
    )
    monkeypatch.setattr(
        main_module,
        "_include_peace_ratification_summary",
        lambda response, result: None,
    )

    response = asyncio.run(
        main_module.respond_to_diplomatic_dialogue({"choice": 2})
    )

    assert response["success"] is True
    assert response["must_reopen"] is True
    assert response["reopen_target"]["war_id"] == "war_1"
    assert response["reopen_target"]["target_nation"] == "Austria"


def test_propose_common_peace_consumes_structured_war_id():
    """End-to-end: cmd dict carries war_id, executor passes it through."""
    world = WorldState()
    _install_war(world)
    world.player_nation = "France"
    executor = DiplomaticExecutor.__new__(DiplomaticExecutor)

    command = {
        "action": "propose_common_peace",
        "target_nation": "Austria",
        "war_id": "war_1",
    }
    result = executor._execute_propose_common_peace(
        command, {"world": world},
    )

    assert result["success"] is True
    assert result["war_id"] == "war_1"


def test_propose_common_peace_with_invalid_war_id_returns_humanized_error():
    world = WorldState()
    _install_war(world)
    world.player_nation = "France"
    executor = DiplomaticExecutor.__new__(DiplomaticExecutor)

    result = executor._execute_propose_common_peace(
        {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "war_id": "war_does_not_exist",
        },
        {"world": world},
    )

    assert result["success"] is False
    assert result["error"] == "invalid_war_id"
    assert result["error_display"] == "This war can no longer be found."


def test_open_settlement_eligibility_rejects_one_to_one_war():
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()

    result = evaluate_open_settlement_eligibility(world, war_id="war_1")

    assert result["available"] is False
    assert result["error"] == "one_to_one_war"
    assert result["disabled_reason_display"] == (
        "Use bilateral peace or armistice for a one-on-one war."
    )


def test_diplomacy_wizard_action_disables_settlement_without_common_war_instance():
    world = WorldState()
    pair = world._make_diplo_key("France", "Austria")
    world.diplomatic_states[pair] = "WAR"

    actions = get_available_diplomatic_actions(world, "Austria")
    action = next(a for a in actions if a["action"] == "open_settlement")

    assert action["available"] is False
    assert action["disabled_reason_display"] == (
        "Use bilateral peace or armistice for a one-on-one war."
    )
    assert action["war_id"] is None


# ---------------------------------------------------------------------------
# _enrich_acceptance_display shape
# ---------------------------------------------------------------------------


def test_enrich_acceptance_display_humanizes_band_and_components():
    enriched = _enrich_acceptance_display({
        "score": 42,
        "band": "near_acceptable",
        "feedback": [
            {"component": "term_harshness_penalty", "value": -25},
            {"component": "leader_own_losses", "value": -15},
            {"component": "war_exhaustion", "value": -8},
            {"component": "base_side_pressure", "value": 30},
        ],
    })

    assert enriched["band"] == "near_acceptable"
    assert enriched["band_display"] == "Near acceptable"
    assert enriched["band_phrase"].startswith("Close")
    # Top components are capped at 3.
    assert len(enriched["top_components"]) == 3
    first = enriched["top_components"][0]
    assert first["component_display"] == "Term harshness"
    # value_display formats with explicit sign so the popup does not need
    # to compute it: -25 → "-25", +30 → "+30".
    assert first["value_display"] == "-25"
    assert enriched["top_blocker_display"] == "Term harshness"
    assert enriched["top_blocker_value_display"] == "-25"


def test_enrich_acceptance_display_handles_empty_feedback():
    enriched = _enrich_acceptance_display({"score": 0, "band": "blocked"})

    assert enriched["band"] == "blocked"
    assert enriched["band_display"] == "Blocked"
    assert enriched["top_components"] == []
    assert "top_blocker_display" not in enriched


# ---------------------------------------------------------------------------
# build_contribution_share_rows: side_label + is_beneficiary
# ---------------------------------------------------------------------------


def test_contribution_rows_include_humanized_side_label():
    world = WorldState()
    _install_war(world)

    contribution = build_contribution_share_rows(world, "war_1")

    assert contribution["rows"], "fixture should produce at least one row"
    for row in contribution["rows"]:
        # No raw enum should reach the popup — every row carries a
        # humanized `side_label`. Raw `side` is preserved for downstream
        # mechanical use but the popup reads side_label.
        assert row["side_label"] in {"Attackers", "Defenders"}
        assert row["side"] in {"attackers", "defenders"}
        assert row["side_label"] == SIDE_LABEL_DISPLAY[row["side"]]


def test_contribution_rows_set_is_beneficiary_from_terms():
    world = WorldState()
    _install_war(world)

    terms = [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "regions": ["Bohemia"]},
        {"type": "vassalage", "from": "Prussia", "to": "Saxony"},
    ]
    contribution = build_contribution_share_rows(
        world, "war_1", settlement_terms=terms,
    )

    by_nation = {row["nation"]: row for row in contribution["rows"]}
    assert by_nation["France"]["is_beneficiary"] is True
    assert by_nation["Saxony"]["is_beneficiary"] is True
    assert by_nation["Austria"]["is_beneficiary"] is False
    assert by_nation["Prussia"]["is_beneficiary"] is False


def test_contribution_rows_default_is_beneficiary_false_when_no_terms():
    world = WorldState()
    _install_war(world)

    contribution = build_contribution_share_rows(world, "war_1")

    assert all(row["is_beneficiary"] is False for row in contribution["rows"])


def test_side_label_display_helper_handles_unknown():
    assert side_label_display("attackers") == "Attackers"
    assert side_label_display("defenders") == "Defenders"
    # Unknown side enum returns empty string (no leak).
    assert side_label_display("") == ""
    assert side_label_display("garbage_enum") == "Garbage Enum"


# ---------------------------------------------------------------------------
# build_settlement_review: uncovered_enemy_display_chips
# ---------------------------------------------------------------------------


def test_settlement_review_emits_uncovered_chips_for_partial_settlement():
    review = build_settlement_review(
        war_id="war_1",
        war_label="Austrian War",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria"],
        terms=[],
        allies=[
            {"nation": "France", "side": "attackers"},
            {"nation": "Saxony", "side": "attackers"},
            {"nation": "Austria", "side": "defenders"},
            {"nation": "Prussia", "side": "defenders"},
        ],
        warnings=[],
        acceptance=None,
        density="medium",
        awe_tags=[],
    )

    assert "uncovered_enemy_display_chips" in review
    # Austria is covered; Prussia is the unsettled enemy.
    assert review["uncovered_enemy_display_chips"] == ["Prussia"]
    # Proposer-side allies are NOT in uncovered chips.
    assert "France" not in review["uncovered_enemy_display_chips"]
    assert "Saxony" not in review["uncovered_enemy_display_chips"]


def test_settlement_review_emits_no_uncovered_chips_for_whole_war_settlement():
    review = build_settlement_review(
        war_id="war_1",
        war_label="Austrian War",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria", "Prussia"],
        terms=[],
        allies=[
            {"nation": "Austria", "side": "defenders"},
            {"nation": "Prussia", "side": "defenders"},
        ],
        warnings=[],
        acceptance=None,
        density="medium",
        awe_tags=[],
    )

    assert review["uncovered_enemy_display_chips"] == []


# ---------------------------------------------------------------------------
# Confirm dialogue route_id matches event-side format
# ---------------------------------------------------------------------------


def test_confirm_dialogue_route_id_matches_event_format():
    """G2-Slice-3 SC-14c inversion: the dialogue's route_id must use the
    `settlement:{war_id}:{turn}:{seq}` format so two same-turn settlement
    events for one war can share a `(war_id, turn)` window without
    colliding on the `seq` counter. The event side reads the staged value
    verbatim instead of recomputing."""
    world = WorldState()
    _install_war(world)
    world.current_turn = 7

    preview = build_settlement_preview(world, war_id="war_1")
    dialogue = build_settlement_confirm_dialogue(world, preview)

    assert dialogue["route_id"] == "settlement:war_1:7:1"
    assert dialogue["route_id"].startswith("settlement:")
    # The legacy `{war_id}:{turn}` format must not be re-introduced.
    assert dialogue["route_id"] != "war_1:7"
    # Prefix-style route_ids from earlier drafts must NOT be re-introduced.
    assert "settlement_summary:" not in dialogue["route_id"]
    assert dialogue["route"]["route_id"] == "settlement:war_1:7:1"

    next_dialogue = build_settlement_confirm_dialogue(world, preview)
    assert next_dialogue["route_id"] == "settlement:war_1:7:2"


def test_confirm_dialogue_carries_uncovered_chips_for_popup():
    """The confirm dialogue surfaces uncovered_enemy_display_chips at
    the top level so the popup does not need to dig into review_sections."""
    world = WorldState()
    _install_war(world)

    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        covered_enemy_participants=["Austria"],
    )

    dialogue = result["diplomatic_dialogue"]
    assert "uncovered_enemy_display_chips" in dialogue
    assert "Prussia" in dialogue["uncovered_enemy_display_chips"]


# ---------------------------------------------------------------------------
# War detail common-settlement affordance
# ---------------------------------------------------------------------------


def test_active_wars_hide_common_settlement_for_one_to_one_war():
    world = WorldState()
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()

    result = build_active_wars(world)
    austria = next(w for w in result["wars"] if w["opponent"] == "Austria")

    assert austria["war_instance_id"] == "war_1"
    assert austria["settlement_available"] is False


def test_active_wars_show_common_settlement_for_multi_party_war():
    world = WorldState()
    _install_war(world)

    result = build_active_wars(world)
    austria = next(w for w in result["wars"] if w["opponent"] == "Austria")

    assert austria["war_instance_id"] == "war_1"
    assert austria["settlement_available"] is True


# ---------------------------------------------------------------------------
# settlement_disabled_reason_display covers the new internal-failure codes
# ---------------------------------------------------------------------------


def test_disabled_reason_display_translates_internal_failure_codes():
    # The two newly-added internal codes must humanize, not leak
    # "Unknown_Settlement_Action" via the generic fallback.
    assert (
        settlement_disabled_reason_display("unknown_settlement_action")
        == "That settlement choice is not recognized."
    )
    assert (
        settlement_disabled_reason_display("unknown_settlement_offer_action")
        == "That settlement-offer choice is not recognized."
    )
