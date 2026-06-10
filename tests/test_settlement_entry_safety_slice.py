"""G2-Slice-2 Entry Safety behavioral tests (SC-8, SC-8b, SC-10, SC-11, SC-11b, SC-12, SC-13).

Tests multi-war disambiguation, eligibility-gated CTAs, coalition target
threading, and selected_target_nation persistence through staging.
"""

from __future__ import annotations

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.diplomacy import get_diplomatic_preview
from backend.game_logic.settlement_helpers import (
    resolve_or_backfill_war_instance_for_settlement,
)
from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    evaluate_open_settlement_eligibility,
    stage_settlement_confirm,
)
from backend.game_logic.war_status import build_active_wars
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _make_world() -> WorldState:
    world = WorldState()
    world.player_nation = "France"
    world.current_turn = 5
    return world


def _install_multi_party_war(world: WorldState, war_id: str = "war_1",
                              attackers=None, defenders=None,
                              attacker_leader="France",
                              defender_leader="Austria") -> dict:
    attackers = attackers or ["France", "Saxony"]
    defenders = defenders or ["Austria", "Prussia"]
    war = make_synthetic_war_instance(
        war_id,
        attackers=attackers,
        defenders=defenders,
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances[war_id] = war
    for pair in war["active_diplo_keys"]:
        a, b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 50
    world.invalidate_war_instance_indexes()
    return war


def _install_two_shared_wars(world: WorldState) -> tuple:
    """Install two multi-party wars both involving France and Austria."""
    war1 = _install_multi_party_war(
        world, "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
    )
    war2 = make_synthetic_war_instance(
        "war_2",
        attackers=["France", "Bavaria"],
        defenders=["Austria", "Russia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=2,
        created_sequence=2,
    )
    world.war_instances["war_2"] = war2
    for pair in war2["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 30
    world.invalidate_war_instance_indexes()
    return war1, war2


# ═══════════════════════════════════════════════════════════════════════════
# SC-8: Multi-war wizard disambiguation
# ═══════════════════════════════════════════════════════════════════════════


class TestMultiWarWizardDisambiguation:
    def test_single_shared_war_directly_available(self):
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        preview = get_diplomatic_preview(world, "Austria")
        actions = preview.get("actions", [])
        settlement_action = next(
            (a for a in actions if a["action"] == "open_settlement"), None
        )
        assert settlement_action is not None
        assert settlement_action["available"] is True
        assert settlement_action["war_id"] == "war_1"

    def test_multi_war_shared_pair_disables_wizard_settlement(self):
        """SC-8: two France/Austria wars must not auto-pick."""
        world = _make_world()
        _install_two_shared_wars(world)
        preview = get_diplomatic_preview(world, "Austria")
        actions = preview.get("actions", [])
        settlement_action = next(
            (a for a in actions if a["action"] == "open_settlement"), None
        )
        assert settlement_action is not None
        assert settlement_action["available"] is False
        assert settlement_action.get("disabled_reason_display", "") != ""
        eligibility = settlement_action.get("eligibility", {})
        assert eligibility.get("error") == "multi_war_ambiguity"
        assert "available_wars" in eligibility
        assert sorted(eligibility["available_wars"]) == ["war_1", "war_2"]

    def test_multi_war_never_auto_picks_sorted_first(self):
        """SC-8: the wizard must never silently choose common_wars[0]."""
        world = _make_world()
        _install_two_shared_wars(world)
        preview = get_diplomatic_preview(world, "Austria")
        actions = preview.get("actions", [])
        settlement_action = next(
            (a for a in actions if a["action"] == "open_settlement"), None
        )
        assert settlement_action["available"] is False


# ═══════════════════════════════════════════════════════════════════════════
# SC-8b: Typed/free-text multi-war rejection
# ═══════════════════════════════════════════════════════════════════════════


class TestTypedCommandMultiWarAmbiguity:
    def test_no_war_id_multi_war_rejects_ambiguity(self):
        """SC-8b: typed command without war_id must reject multi-war."""
        world = _make_world()
        _install_two_shared_wars(world)
        result = resolve_or_backfill_war_instance_for_settlement(
            world, "France", "Austria", requested_war_id="",
        )
        assert result["ok"] is False
        assert result["error"] == "multi_war_ambiguity"
        assert "available_wars" in result
        assert sorted(result["available_wars"]) == ["war_1", "war_2"]

    def test_no_war_id_single_war_still_resolves(self):
        """SC-8b: single shared war still resolves directly."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = resolve_or_backfill_war_instance_for_settlement(
            world, "France", "Austria", requested_war_id="",
        )
        assert result["ok"] is True
        assert result["war_id"] == "war_1"

    def test_explicit_war_id_bypasses_disambiguation(self):
        """With explicit war_id, multi-war is fine."""
        world = _make_world()
        _install_two_shared_wars(world)
        result = resolve_or_backfill_war_instance_for_settlement(
            world, "France", "Austria", requested_war_id="war_2",
        )
        assert result["ok"] is True
        assert result["war_id"] == "war_2"

    def test_executor_rejects_multi_war_without_war_id(self):
        """SC-8b: executor returns failure with humanized disambiguation."""
        world = _make_world()
        _install_two_shared_wars(world)
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        command = {"action": "propose_common_peace", "target_nation": "Austria"}
        result = executor._execute_propose_common_peace(command, {"world": world})
        assert result.get("success") is False
        assert "multi_war_ambiguity" in str(result.get("error", ""))


# ═══════════════════════════════════════════════════════════════════════════
# SC-10: War-status eligibility via active hostile-pair checks
# ═══════════════════════════════════════════════════════════════════════════


class TestWarStatusSettlementEligibility:
    def test_multi_party_war_shows_settlement_available(self):
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        wars = build_active_wars(world)
        assert any(
            w["settlement_available"] for w in wars.get("wars", [])
        )

    def test_one_to_one_war_hides_settlement(self):
        """SC-10: one-to-one wars must not show settlement."""
        world = _make_world()
        war = make_synthetic_war_instance(
            "war_bilateral",
            attackers=["France"],
            defenders=["Austria"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_bilateral"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            world.war_scores[pair] = 50
        world.invalidate_war_instance_indexes()
        wars = build_active_wars(world)
        war_rows = wars.get("wars", [])
        for w in war_rows:
            assert w["settlement_available"] is False

    def test_partial_settlement_hides_cta_when_only_bilateral_remains(self):
        """SC-10: partially settled multi-party war with one active pair left."""
        world = _make_world()
        war = _install_multi_party_war(
            world, "war_1",
            attackers=["France", "Saxony"],
            defenders=["Austria", "Prussia"],
        )
        # Resolve all pairs except France|Austria (simulating partial settlement)
        meta = war.setdefault("diplo_key_meta", {})
        for pair in list(war["active_diplo_keys"]):
            if pair != "Austria|France":
                meta.setdefault(pair, {})["pair_status"] = "resolved"
                war["active_diplo_keys"].remove(pair)
        world.invalidate_war_instance_indexes()
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id="war_1", actor_nation="France",
            ignore_active_dialogue=True,
        )
        # After partial settlement leaves one active hostile pair, common
        # settlement should not remain available.
        assert eligibility["available"] is False
        assert eligibility["error"] == "one_to_one_war"
        wars = build_active_wars(world)
        austria_row = next(
            (w for w in wars.get("wars", []) if w["opponent"] == "Austria"),
            None,
        )
        assert austria_row is not None
        assert austria_row["settlement_available"] is False
        assert austria_row["settlement_eligibility"]["error"] == "one_to_one_war"
        assert austria_row["settlement_disabled_reason_display"] != ""

    def test_eligibility_cache_uses_evaluate_not_unique_count(self):
        """SC-10: war-status must use evaluate_open_settlement_eligibility."""
        world = _make_world()
        war = _install_multi_party_war(world, "war_1")
        # Remove France from war leader to test not_side_leader
        war["attacker_leader"] = "Saxony"
        world.invalidate_war_instance_indexes()
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id="war_1", actor_nation="France",
            ignore_active_dialogue=True,
        )
        assert eligibility.get("available") is False
        assert eligibility.get("error") == "not_side_leader"
        wars = build_active_wars(world)
        austria_row = next(
            (w for w in wars.get("wars", []) if w["opponent"] == "Austria"),
            None,
        )
        if austria_row:
            assert austria_row["settlement_available"] is False
            assert austria_row["settlement_eligibility"]["error"] == "not_side_leader"
            assert austria_row["settlement_disabled_reason_display"] != ""

    def test_war_status_fails_closed_when_eligibility_probe_throws(self, monkeypatch):
        """SC-10: evaluator exceptions must not fall back to unique-count CTA."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")

        import backend.game_logic.settlement_validation as settlement_validation

        def boom(*args, **kwargs):
            raise RuntimeError("probe failed")

        monkeypatch.setattr(
            settlement_validation, "evaluate_open_settlement_eligibility", boom
        )
        wars = build_active_wars(world)
        austria_row = next(
            (w for w in wars.get("wars", []) if w["opponent"] == "Austria"),
            None,
        )
        assert austria_row is not None
        assert austria_row["settlement_available"] is False
        assert austria_row["settlement_eligibility"]["error"] == "settlement_eligibility_unavailable"
        assert austria_row["settlement_disabled_reason_display"] != ""


# ═══════════════════════════════════════════════════════════════════════════
# SC-13: selected_target_nation threading
# ═══════════════════════════════════════════════════════════════════════════


class TestSelectedTargetNationThreading:
    def test_stage_settlement_confirm_persists_selected_target(self):
        """SC-13: staged dialogue carries selected_target_nation."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            density="medium",
        )
        assert result["success"] is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["selected_target_nation"] == "Austria"

    def test_stage_without_selected_target_uses_first_covered(self):
        """SC-13: fallback to covered[0] when no explicit target."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            density="medium",
        )
        assert result["success"] is True
        dialogue = result["diplomatic_dialogue"]
        # Should still have a value (fallback to first covered enemy)
        assert dialogue["selected_target_nation"] != ""
        assert dialogue["selected_target_nation"] in dialogue["covered_enemy_participants"]

    def test_reopen_target_reads_selected_target_first(self):
        """SC-13: _reopen_target uses selected_target_nation before covered[0]."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Prussia",
            density="medium",
        )
        dialogue = result["diplomatic_dialogue"]
        from backend.game_logic.settlement_preview import _reopen_target
        reopen = _reopen_target("war_1", dialogue)
        assert reopen["target_nation"] == "Prussia"
        assert "diagnostic_fallback_target" not in reopen

    def test_reopen_target_diagnostic_when_no_selected_target(self):
        """SC-13: missing selected_target flags diagnostic fallback."""
        dialogue = {
            "covered_enemy_participants": ["Austria", "Prussia"],
            "proposer_side": "attackers",
        }
        from backend.game_logic.settlement_preview import _reopen_target
        reopen = _reopen_target("war_1", dialogue)
        assert reopen["target_nation"] == "Austria"
        assert reopen.get("diagnostic_fallback_target") is True
        assert "error_display" in reopen

    def test_executor_threads_target_nation_as_selected_target(self):
        """SC-13 (GT-Slice-4 re-home): the editor's `selected_target_nation`
        command field is retired with the structured submit transport; the
        executor threads `target_nation` into staging and the staged dialogue
        resolves it as the selected target."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        command = {
            "action": "propose_common_peace",
            "target_nation": "Prussia",
            "war_id": "war_1",
        }
        result = executor._execute_propose_common_peace(command, {"world": world})
        assert result.get("success") is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["selected_target_nation"] == "Prussia"

    def test_executor_defaults_selected_target_to_target_nation(self):
        """SC-13: when no explicit selected_target, use target_nation."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        command = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "war_id": "war_1",
            "covered_enemy_participants": ["Austria"],
        }
        result = executor._execute_propose_common_peace(command, {"world": world})
        assert result.get("success") is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["selected_target_nation"] == "Austria"

    def test_covered_enemy_participants_forwarded_to_stage(self):
        """SC-13: covered_enemy_participants is carried through staging."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        executor = DiplomaticExecutor.__new__(DiplomaticExecutor)
        command = {
            "action": "propose_common_peace",
            "target_nation": "Austria",
            "war_id": "war_1",
            "selected_target_nation": "Austria",
            "covered_enemy_participants": ["Austria"],
        }
        result = executor._execute_propose_common_peace(command, {"world": world})
        assert result.get("success") is True
        dialogue = result["diplomatic_dialogue"]
        assert "Austria" in dialogue["covered_enemy_participants"]

    def test_stage_can_require_explicit_covered_scope(self):
        """SC-13: production staging can fail closed without explicit scope."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            density="medium",
            require_explicit_scope=True,
        )
        assert result.get("success") is False
        assert result["error"] == "no_covered_enemy_participants"

    def test_stage_rejects_selected_target_outside_covered_scope(self):
        """SC-13: selected_target_nation must be within covered participants."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Austria"],
            density="medium",
            require_explicit_scope=True,
        )
        assert result.get("success") is False
        assert result["error"] == "selected_target_not_covered"


# ═══════════════════════════════════════════════════════════════════════════
# SC-11/SC-11b/SC-12: Coalition eligibility and target
# ═══════════════════════════════════════════════════════════════════════════


class TestCoalitionSettlementGating:
    def test_evaluate_eligibility_rejects_one_to_one_war(self):
        """SC-11: coalition CTA should be eligibility-gated."""
        world = _make_world()
        war = make_synthetic_war_instance(
            "war_bilateral",
            attackers=["France"],
            defenders=["Austria"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_bilateral"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
        world.invalidate_war_instance_indexes()
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id="war_bilateral", actor_nation="France",
        )
        assert eligibility["available"] is False
        assert eligibility["error"] == "one_to_one_war"

    def test_evaluate_eligibility_available_for_multi_party(self):
        """SC-11: multi-party shared war is eligible."""
        world = _make_world()
        _install_multi_party_war(world, "war_1")
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id="war_1", actor_nation="France",
        )
        assert eligibility["available"] is True
        assert "coverable_enemy_participants" in eligibility

    def test_non_leader_cannot_open_settlement(self):
        """SC-11: only side leader can open settlement."""
        world = _make_world()
        war = _install_multi_party_war(world, "war_1")
        war["attacker_leader"] = "Saxony"
        eligibility = evaluate_open_settlement_eligibility(
            world, war_id="war_1", actor_nation="France",
        )
        assert eligibility["available"] is False
        assert eligibility["error"] == "not_side_leader"


# ═══════════════════════════════════════════════════════════════════════════
# SC-8b inversion: test_resolve_without_war_id_rejects_multi_war_ambiguity
# (This inverts the old test_resolve_without_war_id_falls_back_to_legacy_path)
# ═══════════════════════════════════════════════════════════════════════════


class TestLegacyFallbackInversion:
    def test_resolve_without_war_id_rejects_multi_war_ambiguity(self):
        """Inverts old test_resolve_without_war_id_falls_back_to_legacy_path.

        The old test asserted the legacy behavior of picking the first
        matching war. The new behavior MUST reject with multi_war_ambiguity.
        """
        world = _make_world()
        _install_two_shared_wars(world)
        result = resolve_or_backfill_war_instance_for_settlement(
            world, "France", "Austria", requested_war_id="",
        )
        assert result["ok"] is False
        assert result["error"] == "multi_war_ambiguity"
        # Must NOT silently pick a war
        assert "war_id" not in result or not result.get("war_id")
