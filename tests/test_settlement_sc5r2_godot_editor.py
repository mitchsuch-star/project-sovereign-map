"""Settlement draft round-trip + active-vs-archived routing + incoming-offer
label/copy alignment (SC-5R-2 lineage, re-homed by GT-Slice-4).

GT-Slice-4 retired the SC-5R-2 freeform editor (scene, script, EDIT payload
contract, structured Submit-for-Review POST). What this bundle still pins is
the surviving draft-lifecycle contract on the GUIDED surface:

- the scoped draft store round-trip: Back Out (`suspend_settlement_editor`)
  preserves the scoped draft; reopening Settlement restores it (PF-2
  war-scoped fallback) onto the guided PROPOSE surface;
- Submit for Review is the `submit_settlement_for_review` dialogue action
  (PROPOSE -> REVIEW), with no editor-mount flag anywhere;
- war-detail re-open of an active war routes to the live surface; an
  archived war routes to the Diplomatic Ledger Treaties tab instead;
- incoming settlement offer action labels match behavior, and Request
  Revision counter-authoring lands guided PROPOSE seeded from the offer.

The editor scene/script source pins and EDIT-contract gates were deleted
with the editor itself (spec §5 / §9 GT-Slice-4 editor-test disposition).
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    build_incoming_settlement_offer_popup,
    handle_incoming_settlement_offer_action,
    load_scoped_settlement_draft,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


GODOT_ROOT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
MAIN_SCRIPT = GODOT_ROOT / "scripts" / "main.gd"


# CH-1 stable-seam note: the scorer is patched at
# backend.game_logic.settlement_scoring.calculate_common_peace_acceptance,
# so wrap-the-real side effects must capture the real function at import
# time (a lazy import inside the side effect would fetch the mock).
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance as _REAL_COMMON_PEACE_ACCEPTANCE,
)


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_body(path: Path, function_name: str) -> str:
    source = _read_source(path)
    marker = f"func {function_name}"
    start = source.find(marker)
    assert start != -1, f"{path} missing {marker}"
    next_func = re.search(r"\nfunc\s+\w+", source[start + 1:])
    end = len(source) if next_func is None else start + 1 + next_func.start()
    return source[start:end]


def _return_lines(function_body: str) -> list[str]:
    lines = []
    for line in function_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("return "):
            lines.append(stripped)
    return lines


def _install_common_peace_war(world: WorldState, *, war_score: int = 70) -> dict:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, _b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = war_score if a == "Austria" else -war_score
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


def _acceptance_accepts(*args, **kwargs):
    real = _REAL_COMMON_PEACE_ACCEPTANCE
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _gold_indemnity_clause(amount: int = 200) -> dict:
    return {
        "type": "gold_indemnity",
        "from": "Austria",
        "to": "France",
        "amount": amount,
    }


# ═══════════════════════════════════════════════════════════════════════════
# C. Backend draft round-trip via scoped draft_key
# ═══════════════════════════════════════════════════════════════════════════


class TestBackendDraftRoundTrip:
    def test_propose_common_peace_restores_scoped_draft_when_no_terms_passed(self):
        """SC-5R-2 round-trip (GT-Slice-4 re-home): a scoped draft saved on
        suspend is restored on a subsequent `propose_common_peace` open. The
        restored draft seeds the staged guided PROPOSE surface with the
        prior clauses."""
        world = WorldState()
        _install_common_peace_war(world)
        # Save a scoped draft via the canonical helper.
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{"type": "peace"}, _gold_indemnity_clause(150)],
        )
        executor = DiplomaticExecutor(None)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_common_peace(
                {
                    "action": "propose_common_peace",
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria", "Prussia"],
                },
                {"world": world},
            )
        assert result.get("success"), result
        assert result.get("draft_restored_from_scope") is True
        staged = result.get("diplomatic_dialogue") or {}
        terms = staged.get("settlement_terms") or []
        # Compare by clause type to avoid display-only field drift.
        types = [str(t.get("type", "")) for t in terms]
        assert "peace" in types
        assert "gold_indemnity" in types

    def test_propose_common_peace_no_scoped_draft_lands_fresh_propose(self):
        """Re-front Slice 1: with no scoped draft, opening a settlement lands
        the conversational PROPOSE surface with a freshly generated baseline —
        NOT a restored draft and NOT the old blank EDIT form."""
        world = WorldState()
        _install_common_peace_war(world)
        executor = DiplomaticExecutor(None)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = executor._execute_propose_common_peace(
                {
                    "action": "propose_common_peace",
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria", "Prussia"],
                },
                {"world": world},
            )
        assert result.get("draft_restored_from_scope") is not True
        assert result.get("propose_on_mount") is True
        assert result.get("open_editor_on_mount") is not True
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("dialogue_mode") == "PROPOSE"
        # The PROPOSE surface always carries the per-court acceptance block.
        assert staged.get("per_court_acceptance")

    def test_submit_for_review_from_guided_propose_lands_review_without_editor_mount(self):
        """GT-Slice-4 migration of the old editor Submit-for-Review round
        trip: the guided PROPOSE surface submits through the
        `submit_settlement_for_review` dialogue action and lands the blocking
        REVIEW carrying the staged terms verbatim — and no editor mount flag
        exists anywhere in the response."""
        from backend.game_logic.settlement_preview import (
            handle_settlement_dialogue_action,
        )

        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause(275)],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
                dialogue_mode="PROPOSE",
            )
            propose_dialogue = staged["diplomatic_dialogue"]
            assert propose_dialogue["dialogue_mode"] == "PROPOSE"
            result = handle_settlement_dialogue_action(
                world,
                action="submit_settlement_for_review",
                dialogue=propose_dialogue,
            )
        assert result.get("success"), result
        assert "open_editor_on_mount" not in result
        review = result.get("diplomatic_dialogue") or {}
        assert review.get("dialogue_mode") == "REVIEW"
        amounts = [
            int(t.get("amount", 0))
            for t in (review.get("settlement_terms") or [])
            if t.get("type") == "gold_indemnity"
        ]
        assert 275 in amounts

    def test_scoped_draft_restore_is_war_scoped_with_target_preference(self):
        """PF-2 (Gate-4 pre-flight D4) supersedes the SC-5R-1 isolation pin:
        the real reopen route cannot reconstruct the suspend-time scope (it
        sends no covered list and always targets the war's defender leader),
        so same-war lookups fall back — exact key, then (war, target)
        prefix, then war-wide most-recent. A settlement is ONE multi-court
        table per war (SC-26), so war-scoped restore matches the player's
        "draft kept" mental model. Cross-WAR isolation still holds."""
        world = WorldState()
        _install_common_peace_war(world)
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=[_gold_indemnity_clause(150)],
        )
        # Same war, different target: the war-wide fallback restores the
        # kept draft instead of silently regenerating a baseline (D4).
        restored = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
        )
        assert restored == [_gold_indemnity_clause(150)]
        # Cross-war isolation holds: nothing bleeds across war ids.
        assert load_scoped_settlement_draft(
            world,
            war_id="war_2",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
        ) is None
        # Target preference: when the asked-for target has its own draft,
        # it wins over another court's more recent save.
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
            settlement_terms=[_gold_indemnity_clause(75)],
        )
        restored_austria = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=[],
        )
        assert restored_austria == [_gold_indemnity_clause(150)]

    def test_suspend_settlement_editor_choice_pops_hardstop_and_keeps_draft(self):
        """SC-5R-2 follow-up bug fix: the editor Back Out sends the string
        choice `suspend_settlement_editor`. The dialogue resolver routes it
        to the settlement handler even though it is absent from the REVIEW
        options[] surface; the handler pops the staged settlement_confirm
        hard-stop (so ordinary commands are no longer held) while PRESERVING
        the scoped draft for same-turn reopen. This is the distinguishing
        behavior from `back_out_settlement`, which discards."""
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause(150)]
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        # The staged settlement_confirm is a hard-stop that would hold
        # ordinary commands at the executor gate.
        assert world.dialogue_manager.is_hard_stop() is True
        executor = DiplomaticExecutor(None)
        result = executor.handle_diplomatic_dialogue_response(
            "suspend_settlement_editor", {"world": world},
        )
        assert result.get("success") is True
        assert result.get("action") == "suspend_settlement_editor"
        assert result.get("mutated") is False
        # Bug fix: the hard-stop is popped so the next command is not held.
        assert world.dialogue_manager.is_hard_stop() is False
        # Scoped draft preserved verbatim for same-turn reopen.
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            == terms
        )


# ═══════════════════════════════════════════════════════════════════════════
# D. Active-vs-archived settlement review routing
# ═══════════════════════════════════════════════════════════════════════════


class TestActiveVsArchivedRouting:
    def test_main_war_settlement_clicked_routes_archived_war_to_history(self):
        """SC-5R-2: when the cached war list does NOT contain an active
        row for the clicked war_id, main.gd routes to the Diplomatic
        Ledger settlement history surface instead of POSTing a stale
        propose_common_peace."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        helper_body = _function_body(MAIN_SCRIPT, "_is_war_archived_in_cache")
        process_body = _function_body(MAIN_SCRIPT, "_process_active_wars")
        assert "_seen_war_ids[cached_war_id] = true" in process_body
        assert "return bool(_seen_war_ids.get(war_id, false))" in helper_body
        assert '"surface": "settlement_history"' in click_body
        # Routes the existing recovery_route helper so the existing
        # settlement_history wiring stays single-source.
        assert "_route_settlement_recovery_route" in click_body
        assert _return_lines(helper_body)[-1] != "return false"

    def test_main_war_settlement_clicked_continues_to_post_for_active_war(self):
        """Active wars still POST `propose_common_peace` so the live
        review surface mounts. The structured payload includes war_id,
        target_nation, and the propose_common_peace action."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        helper_body = _function_body(MAIN_SCRIPT, "_is_war_archived_in_cache")
        assert 'if str(w.get("war_instance_id", w.get("war_id", ""))) == war_id:' in helper_body
        assert '"action": "propose_common_peace"' in click_body

    def test_active_vs_archived_routing_guard_runs_before_post(self):
        """The archive check must run BEFORE the POST so a stale click
        does not waste a backend round trip. The early return uses
        `_route_settlement_recovery_route` for the ledger handoff."""
        click_body = _function_body(MAIN_SCRIPT, "_on_war_settlement_clicked")
        idx_archived = click_body.find("if _is_war_archived_in_cache(war_id):")
        idx_post = click_body.find('"action": "propose_common_peace"', idx_archived)
        assert idx_archived != -1
        assert idx_post > idx_archived, (
            "Archive-route check must precede propose_common_peace POST"
        )


# ═══════════════════════════════════════════════════════════════════════════
# E. Incoming-offer action labels match behavior
# ═══════════════════════════════════════════════════════════════════════════


class TestIncomingOfferLabelsMatchBehavior:
    def _make_offer(self, world: WorldState) -> dict:
        return {
            "type": "incoming_settlement_offer",
            "offer_id": "settlement_offer:war_1:2:1",
            "war_id": "war_1",
            "proposer_nation": "Austria",
            "proposer_side": "defenders",
            "accepting_side": "attackers",
            "covered_enemy_participants": ["Austria"],
            "settlement_terms": [
                {"type": "peace"},
                _gold_indemnity_clause(150),
            ],
            "turn_created": 2,
        }

    def test_review_settlement_offer_label_replaces_accept_settlement(self):
        """SC-5R-2: `accept_settlement_offer` stages a settlement_confirm
        REVIEW; the action label must read as a review action, not an
        immediate ratification."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("accept_settlement_offer") == "Review Settlement Offer"

    def test_reject_offer_label_replaces_reject_settlement(self):
        """`Reject Offer` reads correctly because the action only
        removes the pending offer; it does not reject a settlement
        that has been ratified."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("reject_settlement_offer") == "Reject Offer"

    def test_review_settlement_offer_description_promises_review_not_ratification(
        self,
    ):
        """The description must not promise immediate ratification —
        the backend handler stages a fresh settlement_confirm review,
        and the player still has to ratify on the next popup."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        accept_opt = next(
            opt for opt in popup["options"] if opt.get("action") == "accept_settlement_offer"
        )
        description = str(accept_opt.get("description", "")).lower()
        # Must promise a review path, not a one-click ratify.
        assert "review" in description
        # Must NOT claim it ratifies.
        assert "ratif" not in description or "still requires a final confirm" in description.lower() or "still requires" in description

    def test_request_revision_label_preserved(self):
        """`Request Revision` label / description stayed correct after
        the SC-5R-2 label fix — this regression pin proves the rewrite
        did not accidentally collateral-damage the counter-editor path."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        labels = {opt.get("action"): opt.get("label") for opt in popup.get("options", [])}
        assert labels.get("request_settlement_revision") == "Request Revision"

    def test_all_three_offer_actions_remain_available_after_label_rewrite(self):
        """The label rewrite is copy-only; all three actions remain
        available and route through the same handler."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        popup = build_incoming_settlement_offer_popup(world, offer)
        actions = {opt.get("action") for opt in popup.get("options", [])}
        assert actions == {
            "accept_settlement_offer",
            "request_settlement_revision",
            "reject_settlement_offer",
        }

    def test_request_revision_routes_to_guided_propose_seeded_from_offer(self):
        """GT-Slice-4 (§5 re-point, OQ-4(b)): Request Revision lands the
        guided PROPOSE surface seeded with the exact offered terms — no
        editor mount — and the counter provenance is preserved."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = self._make_offer(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = handle_incoming_settlement_offer_action(
                world,
                action="request_settlement_revision",
                dialogue=offer,
            )
        assert result.get("success"), result
        assert "open_editor_on_mount" not in result
        assert result.get("counter_to_offer_id") == offer["offer_id"]
        assert result.get("counter_seed_terms") == offer["settlement_terms"]
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("dialogue_mode") == "PROPOSE"
        assert "can_edit_terms" not in staged
        seeded_amounts = [
            int(t.get("amount", 0))
            for t in (staged.get("settlement_terms") or [])
            if t.get("type") == "gold_indemnity"
        ]
        assert 150 in seeded_amounts
