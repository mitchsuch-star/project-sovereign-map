"""Slice H — full-agency ally settlement petitions (approved July 3, 2026).

Behavior coverage for the two petition types deferred by SC-32 /
G2-Slice-G2b and landed by `docs/SETTLEMENT_SLICE_H_ALLY_PETITIONS_SPEC.md`
v1.0: `request_reward_or_restoration` + `demand_bargain_honor`, the
Grant / Decline / Honor verbs through the demand-add/restage seam, the
D-H1 protected dial provenance, the §5 `ally_petition_state` store, the
§6 anti-spam contract, and the §4.4 ratification interlock (a
would-breach staging always surfaces the petition first).
"""

from __future__ import annotations

from typing import Mapping
from unittest.mock import patch

from backend.game_logic.diplomacy import (
    _mark_live_bargain_indexes_dirty,
    create_war_objective,
    set_diplomatic_state,
)
from backend.game_logic.settlement_preview import (
    ALLY_PETITION_COOLDOWN_TURNS,
    ALLY_PETITION_DECLINE_RELATION_DELTA,
    ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR,
    ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
    ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
    ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
    ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
    ALLY_SETTLEMENT_PETITION_REWARD,
    handle_ally_settlement_petition_action,
    handle_settlement_dialogue_action,
    queue_ally_settlement_petitions_for_player_action,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

# CH-1 stable-seam note: the scorer is patched at
# backend.game_logic.settlement_scoring.calculate_common_peace_acceptance.
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance as _REAL_COMMON_PEACE_ACCEPTANCE,
)

SCORER_SEAM = (
    "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"
)


def _acceptance_accepts(*args, **kwargs):
    result = _REAL_COMMON_PEACE_ACCEPTANCE(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _install_war(world: WorldState, *, attackers, defenders) -> Mapping:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=list(attackers),
        defenders=list(defenders),
        attacker_leader="France",
        defender_leader=defenders[0],
        created_turn=int(world.current_turn),
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 70
    world.invalidate_war_instance_indexes()
    return war


def _seed_restoration_world() -> WorldState:
    """France + Prussia vs Austria; Austria occupies Berlin (Prussia's
    starting soil) — the always-eligible restoration basis."""
    world = WorldState()
    world.current_turn = 5
    _install_war(world, attackers=("France", "Prussia"), defenders=("Austria",))
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "test")
    world.regions["Berlin"].controller = "Austria"
    return world


def _seed_contribution_world(ally: str = "Prussia") -> WorldState:
    """France + ally vs Austria; the ally presses an objective claim on
    Vienna (held by Austria) — the contribution basis."""
    world = WorldState()
    world.current_turn = 5
    _install_war(world, attackers=("France", ally), defenders=("Austria",))
    key = world._make_diplo_key(ally, "Austria")
    world.war_objectives[key] = {
        ally: create_war_objective(
            "conquest", ally, "Austria", ["Vienna"], world.current_turn
        )
    }
    return world


def _seed_bargain_world() -> WorldState:
    """France + Prussia vs Austria with a live war bargain: France pledged
    its claim on Vienna (vs Austria) to secure Prussia's arms."""
    world = WorldState()
    world.current_turn = 5
    _install_war(world, attackers=("France", "Prussia"), defenders=("Austria",))
    world.diplomatic_commitments["wb_1"] = {
        "id": "wb_1",
        "kind": "war_bargain",
        "status": "active",
        "promiser": "France",
        "beneficiary": "Prussia",
        "target_enemy": "Austria",
        "claim_term": {"claim_region": "Vienna"},
        "created_turn": 3,
        "war_id": "war_1",
    }
    _mark_live_bargain_indexes_dirty(world)
    return world


def _petitions(world: WorldState):
    dm = world.dialogue_manager
    items = []
    current = dm.peek()
    if isinstance(current, Mapping):
        items.append(current)
    items.extend(d for d in dm.iter_queue() if isinstance(d, Mapping))
    return [
        d
        for d in items
        if d.get("type") == ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
    ]


def _queue_stage_trigger(world: WorldState, terms=None):
    return queue_ally_settlement_petitions_for_player_action(
        world,
        trigger_action="stage_settlement",
        war_id="war_1",
        covered_enemy_participants=["Austria"],
        settlement_terms=terms or [],
    )


# ---------------------------------------------------------------------------
# Petition firing — bases, floors, no-false-affordance
# ---------------------------------------------------------------------------


class TestRewardPetitionFiring:
    def test_restoration_basis_fires_with_exact_candidate_clause(self):
        world = _seed_restoration_world()
        queued = _queue_stage_trigger(world)
        assert len(queued) == 1
        petition = queued[0]
        assert petition["petition_type"] == ALLY_SETTLEMENT_PETITION_REWARD
        assert petition["basis"] == "restoration"
        assert petition["ally_nation"] == "Prussia"
        assert petition["candidate_clause"] == {
            "type": "territory_cede",
            "from": "Austria",
            "to": "Prussia",
            "region": "Berlin",
        }
        actions = {o["action"] for o in petition["options"]}
        assert actions == {
            ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
            ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
        }
        popup = petition["popup_payload"]
        assert popup["basis_display"]
        assert popup["candidate_clause_display"]
        assert "Berlin" in popup["candidate_clause_display"]

    def test_restoration_basis_exempt_from_standing_floor(self):
        # D-H3: Saxony (minor, zero contribution) may still petition when
        # its homeland is occupied.
        world = WorldState()
        world.current_turn = 5
        _install_war(
            world, attackers=("France", "Saxony"), defenders=("Austria",)
        )
        world.regions["Dresden"].controller = "Austria"
        world.nation_starting_regions.setdefault("Saxony", ["Dresden"])
        queued = _queue_stage_trigger(world)
        assert len(queued) == 1
        assert queued[0]["ally_nation"] == "Saxony"
        assert queued[0]["basis"] == "restoration"

    def test_contribution_basis_requires_seat_or_consult_standing(self):
        # D-H3: a no-standing minor with a claim gets NO reward petition...
        world_minor = _seed_contribution_world(ally="Saxony")
        assert _queue_stage_trigger(world_minor) == []
        # ...while a major (automatic seat) with the same claim petitions.
        world_major = _seed_contribution_world(ally="Prussia")
        queued = _queue_stage_trigger(world_major)
        assert len(queued) == 1
        assert queued[0]["basis"] == "contribution"
        assert queued[0]["claim_region"] == "Vienna"

    def test_no_false_affordance_when_claim_already_promised(self):
        # The candidate clause must pre-validate (§3.2): Berlin already
        # promised elsewhere in the draft → no petition fires.
        world = _seed_restoration_world()
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "France",
                "region": "Berlin",
            },
        ]
        assert _queue_stage_trigger(world, terms) == []

    def test_solicited_lock_holds_for_full_agency_types(self):
        world = _seed_restoration_world()
        not_solicited = queue_ally_settlement_petitions_for_player_action(
            world,
            trigger_action="turn_tick",
            war_id="war_1",
            covered_enemy_participants=["Austria"],
            settlement_terms=[],
        )
        assert not_solicited == []
        assert _petitions(world) == []

    def test_max_two_live_petitions(self):
        world = _seed_restoration_world()
        for i in range(2):
            world.dialogue_manager.push({
                "type": ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE,
                "petition_key": f"synthetic:{i}",
                "blocking": False,
            })
        assert _queue_stage_trigger(world) == []


# ---------------------------------------------------------------------------
# Decline — D-H2 light memory + cooldown
# ---------------------------------------------------------------------------


class TestDecline:
    def test_decline_records_memory_relation_dip_and_cooldown(self):
        world = _seed_restoration_world()
        queued = _queue_stage_trigger(world)
        petition = queued[0]
        relation_key = world._make_diplo_key("France", "Prussia")
        before = int(world.nation_relations.get(relation_key, 0))
        result = handle_ally_settlement_petition_action(
            world,
            action=ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
            dialogue=petition,
        )
        assert result["success"] is True
        after = int(world.nation_relations.get(relation_key, 0))
        assert after == before + ALLY_PETITION_DECLINE_RELATION_DELTA
        memories = [
            m
            for records in world.settlement_memories.values()
            for m in records
            if m.get("memory_type") == "petition_declined"
        ]
        assert len(memories) == 1
        assert memories[0]["subject"] == "Prussia"
        # D-H2: no betrayal strike for the conversation.
        assert not world.betrayal_history
        entry = world.ally_petition_state["war_1|Prussia"]
        assert entry["cooldown_until_turn"] == (
            world.current_turn + ALLY_PETITION_COOLDOWN_TURNS
        )
        assert ALLY_SETTLEMENT_PETITION_REWARD in entry["declined_types"]
        assert _petitions(world) == []

    def test_cooldown_blocks_refire_until_expiry(self):
        world = _seed_restoration_world()
        petition = _queue_stage_trigger(world)[0]
        handle_ally_settlement_petition_action(
            world,
            action=ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
            dialogue=petition,
        )
        assert _queue_stage_trigger(world) == []
        world.current_turn += ALLY_PETITION_COOLDOWN_TURNS
        refired = _queue_stage_trigger(world)
        assert len(refired) == 1
        assert refired[0]["ally_nation"] == "Prussia"


# ---------------------------------------------------------------------------
# Grant — clause injection through the restage seam + D-H1 protection
# ---------------------------------------------------------------------------


def _mount_settlement(world: WorldState):
    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Austria",
        dialogue_mode="PROPOSE",
    )
    assert result["success"] is True
    mounted = world.dialogue_manager.peek()
    assert mounted["type"] == "settlement_confirm"
    return mounted


class TestGrant:
    def test_grant_lands_clause_with_ally_petition_provenance(self):
        world = _seed_restoration_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            _mount_settlement(world)
            petitions = _petitions(world)
            assert len(petitions) == 1
            result = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
                dialogue=petitions[0],
            )
        assert result["success"] is True
        assert result["petition_granted"]["ally_nation"] == "Prussia"
        mounted = world.dialogue_manager.peek()
        assert mounted["type"] == "settlement_confirm"
        granted = [
            t
            for t in mounted["settlement_terms"]
            if t.get("type") == "territory_cede"
            and t.get("to") == "Prussia"
        ]
        assert len(granted) == 1
        assert granted[0]["authored_by"] == "ally_petition"
        assert granted[0]["region"] == "Berlin"
        # Petition consumed + resolution recorded.
        assert _petitions(world) == []
        entry = world.ally_petition_state["war_1|Prussia"]
        assert ALLY_SETTLEMENT_PETITION_REWARD in entry["granted_types"]
        # The grant voice beat rides the restaged dialogue extras.
        beats = result.get("authoring_voice_beats") or []
        assert any(b.get("kind") == "ally_petition_granted" for b in beats)

    def test_dial_sweep_never_drops_granted_clause(self):
        # D-H1 (approved): a More-Generous sweep must not silently
        # un-reward the ally — the granted territory line survives.
        world = _seed_restoration_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            _mount_settlement(world)
            petition = _petitions(world)[0]
            handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
                dialogue=petition,
            )
            mounted = world.dialogue_manager.peek()
            dial_result = handle_settlement_dialogue_action(
                world,
                action="settlement_dial_generous",
                dialogue=mounted,
                action_params={},
            )
        assert dial_result["success"] is True
        surviving = [
            t
            for t in dial_result["settlement_terms"]
            if t.get("authored_by") == "ally_petition"
        ]
        assert len(surviving) == 1
        assert surviving[0]["region"] == "Berlin"

    def test_grant_degrades_to_lapse_when_draft_changed(self):
        # G1 click-time re-run pattern: the draft changed since queue time
        # (Berlin now promised elsewhere) → refusal-free lapse, petition
        # removed, NO cooldown (the ally may re-petition on next staging).
        world = _seed_restoration_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            _mount_settlement(world)
            petition = _petitions(world)[0]
            mounted = world.dialogue_manager.peek()
            blocking_terms = list(mounted["settlement_terms"]) + [{
                "type": "territory_cede",
                "from": "Austria",
                "to": "France",
                "region": "Berlin",
            }]
            mounted["settlement_terms"] = blocking_terms
            result = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
                dialogue=petition,
            )
        assert result["success"] is True
        assert result["petition_lapsed"] is True
        assert result["mutated"] is False
        assert _petitions(world) == []
        entry = world.ally_petition_state.get("war_1|Prussia") or {}
        assert int(entry.get("cooldown_until_turn", 0) or 0) == 0

    def test_grant_from_suspended_table_stages_draft_with_clause(self):
        # The REAL Godot answer path: mailbox activation is blocked while
        # the settlement hard-stop is mounted, so the player SUSPENDS the
        # table (draft kept), activates the petition, then grants. Grant
        # must honor the suspended scoped draft and re-mount it with the
        # granted clause.
        world = _seed_restoration_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            _mount_settlement(world)
            petition = _petitions(world)[0]
            mounted = world.dialogue_manager.peek()
            suspend = handle_settlement_dialogue_action(
                world,
                action="suspend_settlement_editor",
                dialogue=mounted,
                action_params={},
            )
            assert suspend["success"] is True
            # The queued petition auto-promotes to the active slot — the
            # state the mailbox answer arrives in.
            assert world.dialogue_manager.peek()["type"] == (
                ALLY_SETTLEMENT_PETITION_DIALOGUE_TYPE
            )
            result = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
                dialogue=petition,
            )
        assert result["success"] is True
        mounted_after = world.dialogue_manager.peek()
        assert mounted_after["type"] == "settlement_confirm"
        granted = [
            t
            for t in mounted_after["settlement_terms"]
            if t.get("authored_by") == "ally_petition"
        ]
        assert len(granted) == 1
        assert granted[0]["region"] == "Berlin"
        assert _petitions(world) == []
        entry = world.ally_petition_state["war_1|Prussia"]
        assert ALLY_SETTLEMENT_PETITION_REWARD in entry["granted_types"]

    def test_grant_refused_without_mounted_propose_table(self):
        world = _seed_restoration_world()
        petition = _queue_stage_trigger(world)[0]
        result = handle_ally_settlement_petition_action(
            world,
            action=ALLY_SETTLEMENT_PETITION_GRANT_ACTION,
            dialogue=petition,
        )
        assert result["success"] is False
        assert result["error"] == "petition_table_not_mounted"
        assert result["petition_retained"] is True
        # The petition dialogue survives for a later grant.
        assert len(_petitions(world)) == 1


# ---------------------------------------------------------------------------
# Bargain honor — §4 firing, §4.4 interlock, D-H5 auto-adjust
# ---------------------------------------------------------------------------


class TestBargainHonor:
    def test_would_breach_staging_surfaces_petition_before_ratification(self):
        # §4.4 interlock: staging is the ONLY route to ratification, and a
        # staged package that would breach a live bargain (claim region
        # awarded to a third party) must queue the petition at that gate.
        world = _seed_bargain_world()
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "Saxony",
                "region": "Vienna",
            },
        ]
        queued = _queue_stage_trigger(world, terms)
        assert len(queued) == 1
        petition = queued[0]
        assert petition["petition_type"] == (
            ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR
        )
        assert petition["ally_nation"] == "Prussia"
        assert petition["basis"] == "imminent_breach"
        # §4.2: the consequence ladder reads the landed breach constants.
        assert "-6 reliability" in petition["consequence_display"]
        assert "-10 relation" in petition["consequence_display"]
        actions = {o["action"] for o in petition["options"]}
        assert actions == {
            ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
            ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
        }

    def test_abandonment_detected_when_peace_forgets_the_claim(self):
        world = _seed_bargain_world()
        queued = _queue_stage_trigger(world, [{"type": "peace"}])
        assert len(queued) == 1
        assert queued[0]["basis"] == "abandonment"
        assert queued[0]["candidate_clause"]["to"] == "France"
        assert queued[0]["candidate_clause"]["region"] == "Vienna"

    def test_no_petition_when_staged_terms_leave_bargain_safe(self):
        world = _seed_bargain_world()
        # France gains the claim region at this table — the pledge is safe.
        terms = [
            {"type": "peace"},
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "France",
                "region": "Vienna",
            },
        ]
        assert _queue_stage_trigger(world, terms) == []

    def test_honor_click_retargets_breach_award_to_france(self):
        # D-H5: auto-adjust via restage — the conflicting third-party
        # award of the claim region is retargeted to France, voiced.
        world = _seed_bargain_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                selected_target_nation="Austria",
                settlement_terms=[
                    {"type": "peace"},
                    {
                        "type": "territory_cede",
                        "from": "Austria",
                        "to": "Saxony",
                        "region": "Vienna",
                    },
                ],
                dialogue_mode="PROPOSE",
            )
            assert result["success"] is True
            petitions = _petitions(world)
            assert len(petitions) == 1
            honor = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
                dialogue=petitions[0],
            )
        assert honor["success"] is True
        assert honor["bargain_honored"]["case"] == "imminent_breach"
        mounted = world.dialogue_manager.peek()
        awards = [
            t
            for t in mounted["settlement_terms"]
            if t.get("type") == "territory_cede"
            and "Vienna" in (
                list(t.get("regions") or [])
                + ([t.get("region")] if t.get("region") else [])
            )
        ]
        assert len(awards) == 1
        assert awards[0]["to"] == "France"
        assert awards[0]["authored_by"] == "ally_petition"
        entry = world.ally_petition_state["war_1|Prussia"]
        assert ALLY_SETTLEMENT_PETITION_BARGAIN_HONOR in entry["granted_types"]

    def test_honor_click_injects_cession_for_abandonment(self):
        world = _seed_bargain_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                selected_target_nation="Austria",
                settlement_terms=[{"type": "peace"}],
                dialogue_mode="PROPOSE",
            )
            assert result["success"] is True
            petitions = _petitions(world)
            assert len(petitions) == 1
            assert petitions[0]["basis"] == "abandonment"
            honor = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
                dialogue=petitions[0],
            )
        assert honor["success"] is True
        assert honor["bargain_honored"]["case"] == "abandonment"
        mounted = world.dialogue_manager.peek()
        injected = [
            t
            for t in mounted["settlement_terms"]
            if t.get("authored_by") == "ally_petition"
        ]
        assert len(injected) == 1
        assert injected[0]["to"] == "France"
        assert injected[0]["region"] == "Vienna"

    def test_honor_lapses_when_bargain_no_longer_at_risk(self):
        world = _seed_bargain_world()
        with patch(SCORER_SEAM, side_effect=_acceptance_accepts):
            stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                selected_target_nation="Austria",
                settlement_terms=[{"type": "peace"}],
                dialogue_mode="PROPOSE",
            )
            petitions = _petitions(world)
            assert len(petitions) == 1
            # The bargain resolves out from under the petition.
            world.diplomatic_commitments["wb_1"]["status"] = "fulfilled"
            _mark_live_bargain_indexes_dirty(world)
            honor = handle_ally_settlement_petition_action(
                world,
                action=ALLY_SETTLEMENT_PETITION_HONOR_ACTION,
                dialogue=petitions[0],
            )
        assert honor["success"] is True
        assert honor["petition_lapsed"] is True
        assert _petitions(world) == []


# ---------------------------------------------------------------------------
# Serialization + voice
# ---------------------------------------------------------------------------


class TestSerializationAndVoice:
    def test_ally_petition_state_round_trips_through_save_load(self):
        world = _seed_restoration_world()
        petition = _queue_stage_trigger(world)[0]
        handle_ally_settlement_petition_action(
            world,
            action=ALLY_SETTLEMENT_PETITION_DECLINE_ACTION,
            dialogue=petition,
        )
        snapshot = world.to_dict()
        restored = WorldState.from_dict(snapshot)
        entry = restored.ally_petition_state["war_1|Prussia"]
        assert entry["declined_types"] == [ALLY_SETTLEMENT_PETITION_REWARD]
        assert entry["cooldown_until_turn"] == (
            world.current_turn + ALLY_PETITION_COOLDOWN_TURNS
        )

    def test_pre_slice_h_saves_default_to_empty_state(self):
        world = WorldState()
        snapshot = world.to_dict()
        snapshot.pop("ally_petition_state", None)
        restored = WorldState.from_dict(snapshot)
        assert restored.ally_petition_state == {}

    def test_voice_families_committed_and_d5_clean(self):
        # §7: the D5 auto-scan did not cover the settlement_ally_petition_*
        # prefix — this assertion registers it: every committed template
        # under the prefix obeys the SC-32 D5 boundary.
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES,
            resolve_settlement_voice_line,
        )

        prefixed = {
            key: text
            for key, text in SETTLEMENT_VOICE_TEMPLATES.items()
            if key.startswith("settlement_ally_petition_")
        }
        # Both Slice H ask families + the three resolution families + the
        # lapse notice exist across the named cast + chancery fallback.
        for family in (
            "request_reward_or_restoration",
            "demand_bargain_honor",
            "granted",
            "declined",
            "honored",
        ):
            for suffix in (
                "castlereagh", "hardenberg", "metternich", "einsiedel",
                "chancery",
            ):
                assert (
                    f"settlement_ally_petition_{family}_{suffix}" in prefixed
                ), f"missing template: {family}_{suffix}"
        assert "settlement_ally_petition_lapsed_talleyrand" in prefixed
        for key, text in prefixed.items():
            lowered = text.lower()
            assert "conference" not in lowered, key
            assert "congress" not in lowered, key
            assert "veto" not in lowered, key
        line = resolve_settlement_voice_line(
            "settlement_ally_petition_demand_bargain_honor_hardenberg",
            claim_region="Vienna",
            created_turn_label="turn 3",
            war_label="France vs Austria",
        )
        assert "Vienna" in line and "turn 3" in line

    def test_campaign_log_records_petition_beats(self):
        from backend.campaign_log import (
            CAMPAIGN_LOG_TYPES,
            CATEGORY_MAP,
            format_event_oneliner,
        )

        for event_type in (
            "settlement_ally_petition_granted",
            "settlement_ally_petition_declined",
            "settlement_bargain_honored",
        ):
            assert event_type in CAMPAIGN_LOG_TYPES
            assert CATEGORY_MAP[event_type] == "diplomacy"
        line = format_event_oneliner({
            "type": "settlement_bargain_honored",
            "ally_nation": "Prussia",
            "claim_region": "Vienna",
            "war_label": "France vs Austria",
        })
        assert "Vienna" in line and "Prussia" in line
