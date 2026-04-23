"""B-B4 DG-4 call-to-arms follow-through tests.

Spec:
  - `docs/RELIABILITY_COMMITMENTS_SPEC.md` §8.6.1a (Make Amends grievance variant)
  - `docs/RELIABILITY_COMMITMENTS_SPEC.md` §8.8, §8.8.4, §8.8.7a, §8.8.9
  - `docs/RELIABILITY_COMMITMENTS_SPEC.md` §9.3 (composite floor with-DG-4 clause)
Plan: `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` §B-B4.

Covers (~27 focused tests):

  Grievance helpers (§8.8.4):
    - Add / count / FIFO-remove grievance flags
    - Capped count for acceptance formula vs raw count for ledger
    - Persistence through save/load round-trip
    - Pair pruning when strikes + flags both reach zero

  `grievance_modifier` (§8.8.9 + §9.3):
    - -30 per active flag
    - Saturates at 3 (max -90)
    - 0 when pair clean / self-targeted

  Composite floor (§9.3 with-DG-4):
    - Political subtotal `hegemony + betrayal + grievance` is clamped to -60
    - Raw term values preserved in `components` debug output
    - `composite_floor_applied` is False when subtotal is > -60

  `emit_call_to_arms_refused_defensive` (§8.8 + §8.8.7a):
    - Adds victim strike + grievance flag + -10 reliability
    - Emits `diplomatic_treaty_broken` with
      `end_reason_family = defensive_refusal_termination`
    - Downgrades ALLIANCE / DEFENSIVE_ALLIANCE to PEACE same turn
    - No-op alliance side when pair is not bound
    - Bloc cache is invalidated on termination
    - Episode-id reuse honors caller-provided id

  Make Amends grievance variant (§8.6.1a):
    - Parser disambiguation on `for the abandoned alliance`
    - Success path: gold -400, DP -2, reliability +3, relation +8, grievance removed
    - Distinct from strike-clearing: strike coexists untouched, grievance cleared
    - Refusal when no active grievance (even if strikes exist)
    - Refusal when cooldown shared with standard variant is active
    - `amends_offered` emits with `amends_variant="grievance"` on all three surfaces

  Display labels + campaign log:
    - `END_REASON_FAMILY_DISPLAY` carries the new family
    - Campaign-log one-liner distinguishes grievance variant from standard
"""
from __future__ import annotations

import pytest

from backend.commands.executor import CommandExecutor
from backend.display_names import (
    AMENDS_REFUSAL_DISPLAY,
    END_REASON_FAMILY_DISPLAY,
)
from backend.game_logic.diplomacy import (
    END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION,
    _add_grievance_flag,
    _get_active_grievance_flag_count,
    _get_capped_grievance_flag_count,
    _get_grievance_flags,
    _remove_oldest_grievance_flag,
    calculate_acceptance,
    emit_call_to_arms_refused_defensive,
    grievance_modifier,
    set_diplomatic_state,
)
from backend.models.world_state import WorldState
from backend.notifications import AMENDS_OFFERED


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _world(*, player_gold: int = 800, player_dp: int = 4) -> WorldState:
    """Build a France-player world at PEACE with Britain/Prussia/Austria/Saxony."""
    world = WorldState(player_nation="France")
    for nation in ("Britain", "Prussia", "Austria", "Saxony"):
        set_diplomatic_state(world, "France", nation, "PEACE", "test_setup")
    world.nation_gold["France"] = int(player_gold)
    world.diplomatic_points = int(player_dp)
    return world


def _seed_grievance(
    world: WorldState,
    *,
    breaker: str = "France",
    victim: str = "Austria",
    episode_id: str = "ep_grief",
    turn: int = 0,
    grievance_type: str = "defensive_call_refused",
) -> dict:
    """Append a grievance flag via the first-party helper (exercise the seam)."""
    prior_turn = int(getattr(world, "current_turn", 0))
    world.current_turn = int(turn)
    try:
        flag = _add_grievance_flag(
            world,
            breaker=breaker,
            victim=victim,
            grievance_type=grievance_type,
            episode_id=episode_id,
            source_episode_type="call_to_arms_refused_defensive",
        )
    finally:
        world.current_turn = prior_turn
    return flag


def _run_grievance_amends(world: WorldState, *, target: str = "Austria") -> dict:
    """Invoke the grievance variant through the full CommandExecutor pipeline."""
    executor = CommandExecutor()
    parsed_command = {
        "command": {
            "action": "make_amends",
            "type": "specific",
            "diplomatic_data": {
                "action": "make_amends",
                "diplomat": "Talleyrand",
                "target_nation": target,
                "amends_variant": "grievance",
            },
        },
    }
    return executor.execute(parsed_command, {"world": world})


# ════════════════════════════════════════════════════════════════════════════
# 1. GRIEVANCE FLAG HELPERS (§8.8.4)
# ════════════════════════════════════════════════════════════════════════════

class TestGrievanceHelpers:

    def test_add_flag_creates_pair_record_and_persists(self):
        world = _world()
        flag = _seed_grievance(world, turn=3)

        assert _get_active_grievance_flag_count(world, "France", "Austria") == 1
        assert flag["grievance_type"] == "defensive_call_refused"
        assert flag["episode_id"] == "ep_grief"
        assert flag["turn"] == 3
        assert flag["source_episode_type"] == "call_to_arms_refused_defensive"

        record = world.betrayal_history["France|Austria"]
        assert "grievance" in record["categories"]
        assert record["last_turn"] == 3

    def test_active_count_zero_when_pair_is_clean(self):
        world = _world()
        assert _get_active_grievance_flag_count(world, "France", "Austria") == 0

    def test_capped_count_saturates_at_three(self):
        world = _world()
        for idx in range(5):
            _seed_grievance(
                world, episode_id=f"ep_{idx}", turn=idx,
            )
        assert _get_active_grievance_flag_count(world, "France", "Austria") == 5
        assert _get_capped_grievance_flag_count(world, "France", "Austria") == 3

    def test_remove_oldest_uses_fifo_turn_then_episode_id(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_b", turn=5)
        _seed_grievance(world, episode_id="ep_a", turn=5)  # same turn, earlier id
        _seed_grievance(world, episode_id="ep_c", turn=10)

        removed = _remove_oldest_grievance_flag(world, "France", "Austria")
        assert removed is not None
        assert removed["episode_id"] == "ep_a", (
            "same-turn tie must break by episode_id lexicographic order"
        )
        remaining_ids = {
            f["episode_id"]
            for f in _get_grievance_flags(world, "France", "Austria")
        }
        assert remaining_ids == {"ep_b", "ep_c"}

    def test_remove_flag_prunes_pair_when_strikes_and_flags_empty(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_only", turn=0)
        _remove_oldest_grievance_flag(world, "France", "Austria")
        assert "France|Austria" not in world.betrayal_history

    def test_remove_flag_keeps_pair_when_strikes_remain(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_gf", turn=0)
        # Seed a standalone strike alongside the grievance.
        key = "France|Austria"
        record = world.betrayal_history[key]
        record["strikes"].append({
            "severity": "medium", "turn": 0, "episode_id": "ep_strike",
            "decays_on_turn": 10,
        })
        world.betrayal_history[key] = record

        _remove_oldest_grievance_flag(world, "France", "Austria")
        assert key in world.betrayal_history, "strike retention must keep the pair"
        assert not world.betrayal_history[key]["grievance_flags"]
        assert len(world.betrayal_history[key]["strikes"]) == 1

    def test_save_load_roundtrip_preserves_grievance_flags(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_save", turn=7)
        serialized = world.to_dict()

        restored = WorldState.from_dict(serialized)
        flags = _get_grievance_flags(restored, "France", "Austria")
        assert len(flags) == 1
        assert flags[0]["episode_id"] == "ep_save"
        assert flags[0]["turn"] == 7
        assert flags[0]["grievance_type"] == "defensive_call_refused"
        assert flags[0]["source_episode_type"] == "call_to_arms_refused_defensive"


# ════════════════════════════════════════════════════════════════════════════
# 2. grievance_modifier (§8.8.9 + §9.3)
# ════════════════════════════════════════════════════════════════════════════

class TestGrievanceModifier:

    def test_zero_when_no_flag(self):
        world = _world()
        assert grievance_modifier("France", "Austria", world) == 0

    def test_zero_when_self_targeted(self):
        world = _world()
        _seed_grievance(world)
        assert grievance_modifier("France", "France", world) == 0
        assert grievance_modifier("", "Austria", world) == 0
        assert grievance_modifier("France", "", world) == 0

    def test_linear_with_flags_up_to_three(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_1", turn=0)
        assert grievance_modifier("France", "Austria", world) == -30
        _seed_grievance(world, episode_id="ep_2", turn=1)
        assert grievance_modifier("France", "Austria", world) == -60
        _seed_grievance(world, episode_id="ep_3", turn=2)
        assert grievance_modifier("France", "Austria", world) == -90

    def test_saturates_at_three_for_stacking_cap(self):
        world = _world()
        for idx in range(6):
            _seed_grievance(world, episode_id=f"ep_{idx}", turn=idx)
        assert grievance_modifier("France", "Austria", world) == -90, (
            "grievance_modifier must saturate at -90 per spec §8.8.4"
        )


# ════════════════════════════════════════════════════════════════════════════
# 3. COMPOSITE FLOOR (§9.3 with-DG-4 clause)
# ════════════════════════════════════════════════════════════════════════════

class TestCompositeFloor:

    def _build_peace_proposal(self, target: str = "Austria") -> dict:
        return {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": target,
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }

    def test_clean_pair_has_no_floor_and_zero_grievance(self):
        world = _world()
        result = calculate_acceptance(self._build_peace_proposal(), world)
        components = result["components"]
        assert components["grievance_modifier"] == 0
        assert components["grievance_flag_count_raw"] == 0
        assert components["composite_floor_applied"] is False
        assert components["composite_floor"] == 0
        assert components["composite_floor_adjustment"] == 0

    def test_floor_clamps_political_subtotal_at_negative_sixty(self):
        world = _world()
        # Three grievances saturate at -90; composite floor lifts to -60.
        for idx in range(3):
            _seed_grievance(world, episode_id=f"ep_{idx}", turn=idx)
        result = calculate_acceptance(self._build_peace_proposal(), world)
        components = result["components"]

        assert components["grievance_modifier"] == -90
        assert components["grievance_flag_count_raw"] == 3
        assert components["composite_floor_applied"] is True
        assert components["composite_floor"] == -60
        # Raw subtotal is -90; composite adjustment is +30 (lift to -60).
        assert components["composite_floor_adjustment"] == 30

    def test_floor_exposes_raw_terms_when_clamped(self):
        """Spec §9.3 "Floor exposure" — raw terms remain visible."""
        world = _world()
        # Saturate grievance; also seed three active strikes to push the
        # bilateral term to -18 (so the worst-case subtotal reads -108).
        for idx in range(3):
            _seed_grievance(world, episode_id=f"ep_g{idx}", turn=idx)
        key = "France|Austria"
        record = world.betrayal_history[key]
        for idx in range(3):
            record["strikes"].append({
                "severity": "high",
                "turn": idx,
                "episode_id": f"ep_s{idx}",
                "decays_on_turn": 10,
            })
        world.betrayal_history[key] = record

        result = calculate_acceptance(self._build_peace_proposal(), world)
        components = result["components"]
        # Raw term values are preserved regardless of the clamp.
        assert components["bilateral_betrayal_mod"] == -18
        assert components["grievance_modifier"] == -90
        assert components["composite_floor_applied"] is True
        assert components["composite_floor"] == -60

    def test_four_plus_grievances_still_capped_by_stacking_rule(self):
        """Spec §8.8.4 "4+ grievances" — raw count visible, modifier capped."""
        world = _world()
        for idx in range(5):
            _seed_grievance(world, episode_id=f"ep_{idx}", turn=idx)
        result = calculate_acceptance(self._build_peace_proposal(), world)
        components = result["components"]

        assert components["grievance_flag_count_raw"] == 5, (
            "raw count must reflect the underlying data for the ledger"
        )
        assert components["grievance_modifier"] == -90, (
            "stacking cap holds at 3 flags per pair"
        )


# ════════════════════════════════════════════════════════════════════════════
# 4. emit_call_to_arms_refused_defensive (§8.8 + §8.8.7a)
# ════════════════════════════════════════════════════════════════════════════

class TestCallToArmsRefusedDefensive:

    def test_records_strike_grievance_and_reliability(self):
        world = _world()
        # Give Russia a reliability of 20 so the drop is visible.
        world.diplomatic_reliability["Russia"] = 20
        # Russia and Austria share an ALLIANCE (the call is from Austria).
        # Russia is not in the default cast — register it first so
        # `set_diplomatic_state` can resolve the key deterministically.
        set_diplomatic_state(world, "Russia", "Austria", "ALLIANCE", "setup")

        result = emit_call_to_arms_refused_defensive(
            world,
            breaker="Russia",
            victim="Austria",
            severity="high",
        )

        assert result["strike_record"]["recorded"] is True
        assert result["grievance_flag"]["grievance_type"] == "defensive_call_refused"
        assert result["reliability_after"] == 10, "10 = 20 - 10 per §8.8.2"
        assert int(world.diplomatic_reliability["Russia"]) == 10

        flags = _get_grievance_flags(world, "Russia", "Austria")
        assert len(flags) == 1
        assert flags[0]["episode_id"] == result["episode_id"]

    def test_alliance_termination_on_defensive_refusal(self):
        world = _world()
        set_diplomatic_state(
            world, "Russia", "Austria", "DEFENSIVE_ALLIANCE", "setup",
        )

        result = emit_call_to_arms_refused_defensive(
            world, breaker="Russia", victim="Austria",
        )

        assert result["alliance_terminated"] is True
        assert result["previous_alliance_state"] == "DEFENSIVE_ALLIANCE"
        assert world.get_diplomatic_state("Russia", "Austria") == "PEACE"

    def test_no_alliance_means_no_termination_event(self):
        world = _world()
        set_diplomatic_state(world, "Russia", "Austria", "NON_AGGRESSION", "setup")

        result = emit_call_to_arms_refused_defensive(
            world, breaker="Russia", victim="Austria",
        )
        assert result["alliance_terminated"] is False
        # NON_AGGRESSION should survive.
        assert world.get_diplomatic_state("Russia", "Austria") == "NON_AGGRESSION"

    def test_emits_treaty_broken_with_defensive_refusal_family(self):
        world = _world()
        set_diplomatic_state(world, "Russia", "Austria", "ALLIANCE", "setup")

        emit_call_to_arms_refused_defensive(
            world, breaker="Russia", victim="Austria",
        )

        treaty_broken_events = [
            e for e in world.event_log
            if e.get("type") == "diplomatic_treaty_broken"
        ]
        assert treaty_broken_events, "expected diplomatic_treaty_broken emit"
        event = treaty_broken_events[-1]
        assert event["end_reason_family"] == END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION
        assert event["end_reason_action"] == "defensive_refusal"
        # §8.8.7a cascade clause: the refusal episode owns strike + grievance,
        # so the breach event contributes no additional strike.
        assert event["applied_reliability_delta"] == 0, (
            "defensive_refusal_termination applies no independent reliability drop"
        )

    def test_bloc_cache_invalidated_on_termination(self):
        """§8.8.7a requires `get_bloc_members` to reflect post-termination geometry."""
        world = _world()
        set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
        # Warm the cache.
        pre_members = set(world.get_bloc_members("France"))
        assert "Austria" in pre_members, (
            "Austria should be in France's bloc via ALLIANCE"
        )

        emit_call_to_arms_refused_defensive(
            world, breaker="France", victim="Austria",
        )
        post_members = set(world.get_bloc_members("France"))
        assert "Austria" not in post_members, (
            "same-turn termination must shrink the bloc read"
        )

    def test_episode_id_reuse_honors_caller_input(self):
        world = _world()
        result = emit_call_to_arms_refused_defensive(
            world,
            breaker="Russia",
            victim="Austria",
            episode_id="episode_lock",
        )
        assert result["episode_id"] == "episode_lock"
        assert result["grievance_flag"]["episode_id"] == "episode_lock"

    def test_rejects_self_targeted_refusal(self):
        world = _world()
        with pytest.raises(ValueError):
            emit_call_to_arms_refused_defensive(
                world, breaker="France", victim="France",
            )


# ════════════════════════════════════════════════════════════════════════════
# 5. MAKE AMENDS — GRIEVANCE VARIANT (§8.6.1a)
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsGrievanceVariant:

    def test_success_deducts_costs_and_applies_deltas(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_grief_1", turn=0)
        rel_key = world._make_diplo_key("France", "Austria")
        starting_reliability = int(world.diplomatic_reliability.get("France", 0))
        starting_relation = int(world.nation_relations.get(rel_key, 0))

        result = _run_grievance_amends(world)

        assert result["success"] is True
        assert result["amends_variant"] == "grievance"
        assert result["grievance_variant"] is True
        assert result["gold_spent"] == 400
        assert result["dp_spent"] == 2

        assert int(world.nation_gold["France"]) == 800 - 400
        assert int(world.diplomatic_points) == 4 - 2
        assert (int(world.diplomatic_reliability["France"])
                == starting_reliability + 3)
        assert int(world.nation_relations[rel_key]) == starting_relation + 8

        # Flag removed, cooldown set
        assert _get_active_grievance_flag_count(world, "France", "Austria") == 0
        cooldown_key = world._make_diplo_key("France", "Austria")
        expected_expiry = int(world.current_turn) + 10
        assert int(world.reparations_cooldown[cooldown_key]) == expected_expiry

    def test_grievance_variant_leaves_standalone_strike_untouched(self):
        """Spec §8.6.1a: removing grievance does NOT clear strikes."""
        world = _world()
        _seed_grievance(world, episode_id="ep_grief", turn=0)
        # Add an unrelated strike on the same pair.
        key = "France|Austria"
        record = world.betrayal_history[key]
        record["strikes"].append({
            "severity": "medium", "turn": 0,
            "episode_id": "ep_strike", "decays_on_turn": 10,
        })
        world.betrayal_history[key] = record

        result = _run_grievance_amends(world)
        assert result["success"] is True

        # Strike survives the grievance-variant call
        assert len(world.betrayal_history[key]["strikes"]) == 1
        assert world.betrayal_history[key]["strikes"][0]["episode_id"] == "ep_strike"
        # Grievance was removed
        assert not world.betrayal_history[key].get("grievance_flags", [])

    def test_refusal_when_no_grievance_even_with_strikes(self):
        """Spec §8.6.1a refusal: distinct from `no_active_strikes`."""
        world = _world()
        # Strike but no grievance flag.
        key = "France|Austria"
        world.betrayal_history[key] = {
            "strikes": [{
                "severity": "medium", "turn": 0,
                "episode_id": "ep_strike", "decays_on_turn": 10,
            }],
            "grievance_flags": [],
            "categories": ["treaty_breach"],
            "last_turn": 0,
        }

        result = _run_grievance_amends(world)
        assert result["success"] is False
        assert "abandoned alliance to repair" in result["message"], (
            "expected Talleyrand advisory to cite the grievance-specific refusal"
        )
        # Resources untouched
        assert int(world.nation_gold["France"]) == 800
        assert int(world.diplomatic_points) == 4

    def test_refusal_when_cooldown_active_shared_with_standard_variant(self):
        """Spec §8.6.1a: one Make Amends of any variant per pair per 10 turns."""
        world = _world()
        _seed_grievance(world, episode_id="ep_gf", turn=0)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.reparations_cooldown[diplo_key] = int(world.current_turn) + 5

        result = _run_grievance_amends(world)
        assert result["success"] is False
        assert "only" in result["message"] and "turns ago" in result["message"]
        # Flag still intact
        assert _get_active_grievance_flag_count(world, "France", "Austria") == 1

    def test_refusal_when_at_war(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_war", turn=0)
        set_diplomatic_state(world, "France", "Austria", "WAR", "test_war")

        result = _run_grievance_amends(world)
        assert result["success"] is False
        assert "ransom" in result["message"], (
            "expected `war_or_armistice` Talleyrand advisory verbiage"
        )

    def test_refusal_on_insufficient_gold_uses_grievance_cost(self):
        world = _world(player_gold=300)  # less than 400
        _seed_grievance(world, episode_id="ep_g", turn=0)

        result = _run_grievance_amends(world)
        assert result["success"] is False
        assert "400 gold" in result["message"], (
            "the grievance-variant shortfall message must quote the 400g cost"
        )

    def test_refusal_on_insufficient_dp_uses_grievance_cost(self):
        world = _world(player_dp=1)  # less than 2
        _seed_grievance(world, episode_id="ep_g", turn=0)

        result = _run_grievance_amends(world)
        assert result["success"] is False
        assert "2 DP" in result["message"]

    def test_amends_offered_emits_on_all_three_surfaces(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_emit", turn=0)

        result = _run_grievance_amends(world)
        assert result["success"] is True

        # Campaign log
        log_events = [
            e for e in world.event_log
            if e.get("type") == "amends_offered"
        ]
        assert log_events, "amends_offered must reach campaign log"
        event = log_events[-1]
        assert event["amends_variant"] == "grievance"
        assert event["grievance_variant"] is True
        assert event["cleared_grievance_episode_id"] == "ep_emit"
        assert event["cleared_grievance_type"] == "defensive_call_refused"
        assert event["gold_spent"] == 400
        assert event["dp_spent"] == 2

        # Dispatch queue
        dispatch_events = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "amends_offered"
        ]
        assert dispatch_events, "amends_offered must reach dispatch queue"
        template_vars = dispatch_events[-1]["template_vars"]
        assert template_vars["amends_variant"] == "grievance"
        assert template_vars["grievance_variant"] is True

        # Notification collector
        notifications = [
            n for n in world.notifications.get_pending()
            if n.get("type") == AMENDS_OFFERED
        ]
        assert notifications, "amends_offered must reach notifications"
        details = notifications[-1].get("details", {}) or {}
        assert details["amends_variant"] == "grievance"
        assert "for the abandoned alliance" in notifications[-1]["message"]

    def test_result_message_names_grievance_variant_explicitly(self):
        world = _world()
        _seed_grievance(world, episode_id="ep_msg", turn=0)
        result = _run_grievance_amends(world)
        assert result["success"] is True
        assert "abandoned alliance" in result["message"], (
            "result text must tell Napoleon the gesture was the grievance variant"
        )


# ════════════════════════════════════════════════════════════════════════════
# 6. PARSER DISAMBIGUATION (standard vs grievance)
# ════════════════════════════════════════════════════════════════════════════

class TestParserDisambiguation:

    def _parse(self, command: str) -> dict:
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        result = client.parse_command_structured(command)
        # `diplomatic_data` is on the ParseResult for diplomatic paths.
        return result.to_dict().get("diplomatic_data", {}) or {}

    def test_default_phrasing_parses_as_standard(self):
        data = self._parse("Talleyrand, make amends with Austria")
        assert data.get("action") == "make_amends"
        assert data.get("amends_variant") == "standard"

    def test_abandoned_alliance_phrasing_parses_as_grievance(self):
        data = self._parse(
            "Talleyrand, make amends with Austria for the abandoned alliance",
        )
        assert data.get("action") == "make_amends"
        assert data.get("amends_variant") == "grievance"

    def test_non_amends_path_defaults_variant_to_standard(self):
        data = self._parse("Talleyrand, propose peace to Austria")
        assert data.get("amends_variant") == "standard", (
            "non-make_amends paths must still populate the key "
            "with the standard default"
        )


# ════════════════════════════════════════════════════════════════════════════
# 7. DISPLAY LABELS + CAMPAIGN LOG ONE-LINERS
# ════════════════════════════════════════════════════════════════════════════

class TestDisplayLabels:

    def test_end_reason_family_display_carries_defensive_refusal(self):
        assert END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION in (
            END_REASON_FAMILY_DISPLAY
        )
        label = END_REASON_FAMILY_DISPLAY[
            END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION
        ]
        assert "refus" in label.lower(), (
            "display label must name the refusal, not generic rupture wording"
        )

    def test_amends_refusal_display_carries_no_active_grievance_row(self):
        assert "no_active_grievance" in AMENDS_REFUSAL_DISPLAY
        rendered = AMENDS_REFUSAL_DISPLAY["no_active_grievance"].format(
            nation="Austria",
        )
        assert "no abandoned alliance to repair" in rendered

    def test_campaign_log_oneliner_distinguishes_variants(self):
        from backend.campaign_log import format_event_oneliner

        standard_event = {
            "type": "amends_offered",
            "actor_nation": "France",
            "target_nation": "Austria",
            "gold_spent": 200,
            "dp_spent": 1,
            "amends_variant": "standard",
        }
        standard_line = format_event_oneliner(standard_event)
        assert "offered amends to Austria " in standard_line
        assert "abandoned alliance" not in standard_line
        assert "(200g, 1 DP)" in standard_line

        grievance_event = {
            "type": "amends_offered",
            "actor_nation": "France",
            "target_nation": "Austria",
            "gold_spent": 400,
            "dp_spent": 2,
            "amends_variant": "grievance",
        }
        grievance_line = format_event_oneliner(grievance_event)
        assert "abandoned alliance" in grievance_line
        assert "(400g, 2 DP)" in grievance_line
