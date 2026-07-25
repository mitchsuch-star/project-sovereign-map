"""NA-5 — AI ultimatums to the player (R162) — behavior pins.

Gate answers + completion definition: docs/NATION_AGENDAS_SPEC.md §8.

Pins: the trigger gate stack (each condition falsified), terms carry the
agenda target as the demand, issue sets the 15-turn cooldown and never
reduces the player's threat, max one live ultimatum world-wide, the
rejection marker (planted / capped / expiring / serialized), accept
transfers demands player→issuer through the shared clause arms with NO
player-threat addition, lapse is NOT a rejection, the incoming_ultimatum
dtype wiring (dialogue manager taxonomy + Godot + main.py routes), and
GR5 (any authored acquire-design nation can issue).

Corpus note (§8 completion): NO new typed player commands were added —
Yield/Defy resolve through the existing dialogue-response path (option
labels + the action_map aliases), so the golden corpus is deliberately
untouched. Pinned by test_ultimatum_actions_are_dialogue_actions_not_commands.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.ai_diplomacy import (
    AI_ULTIMATUM_COOLDOWN_TURNS,
    AI_ULTIMATUM_STRENGTH_RATIO,
    _generate_agenda_ultimatum,
    _has_live_ultimatum,
    _national_strength,
    _ultimatum_demandable_regions,
    apply_ultimatum_rejection_cooldowns,
    build_ai_proposal_dialogue,
    deliver_ai_proposal,
    process_diplomatic_phase,
)
from backend.game_logic.coalition import (
    ULTIMATUM_REJECTION_PRESSURE_CAP,
    ULTIMATUM_REJECTION_PRESSURE_TURNS,
    _calculate_ultimatum_rejection_threat,
    record_ultimatum_rejection,
)
from backend.game_logic.diplomatic_templates import generate_ultimatum_terms
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)
GODOT_SCRIPTS = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _make_ultimatum_ready(world, nation="Prussia", region="Hanover"):
    """Arrange every §8 gate to hold for `nation` over `region`:
    peace everywhere (disables the P1/P2/P7/P8 masks), threat 0 (disables
    the P3 shelter rung), the design target in the player's DIRECT hands,
    hostile relation, and a fog-free strength ratio above the gate."""
    for other in list(world.get_active_nations()):
        if other == world.player_nation:
            continue
        key = world._make_diplo_key(world.player_nation, other)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
    world.invalidate_bloc_members_cache()
    world.threat_level = 0
    world.regions[region].controller = world.player_nation
    world.invalidate_active_nations_cache()
    world.nation_relations[world._make_diplo_key(world.player_nation, nation)] = -20
    for m in world.marshals.values():
        if m.nation == world.player_nation:
            m.strength = 2000
        elif m.nation == nation:
            m.strength = 40000
    assert _national_strength(nation, world) >= (
        _national_strength(world.player_nation, world) * AI_ULTIMATUM_STRENGTH_RATIO
    ), "fixture must clear the strength gate"
    return world


def _fire(world, nation="Prussia"):
    return process_diplomatic_phase(nation, world)


# ═══════════════════════ §8 TRIGGER — POSITIVE + GR5 ═══════════════════════

class TestUltimatumTrigger:
    @pytest.mark.parametrize("nation,region", [
        ("Prussia", "Hanover"),   # hanoverian_prize
        ("Austria", "Milan"),     # redeem_italy — GR5: any authored acquire court
    ])
    def test_fires_when_all_gates_hold(self, world, nation, region):
        _make_ultimatum_ready(world, nation, region)
        proposal = _fire(world, nation)
        assert proposal is not None, f"{nation} should issue an ultimatum"
        assert proposal["proposal_type"] == "ultimatum"
        assert proposal["_force_send"] is True
        terms = proposal["terms"]
        assert terms["type"] == "ultimatum_demand"
        assert terms["sweeteners"] == []  # pure extortion, no sugar
        cede = [d for d in terms["demands"] if d["type"] == "territory_cede"]
        assert len(cede) == 1
        assert region in cede[0]["regions"], (
            "the agenda target must ride the demand (§8 Building Blocks)"
        )

    def test_issue_sets_fifteen_turn_cooldown(self, world):
        _make_ultimatum_ready(world)
        _fire(world)
        assert world.ai_proposal_cooldowns.get("Prussia|ultimatum") == (
            AI_ULTIMATUM_COOLDOWN_TURNS
        )

    def test_issue_does_not_reduce_player_threat(self, world):
        _make_ultimatum_ready(world)
        world.threat_level = 45  # an AI demand is not exculpatory (§8, pinned)
        before = world.threat_level
        proposal = _fire(world)
        assert proposal is not None
        assert world.threat_level == before

    # ── each gate falsified in turn ──

    def test_no_fire_at_war(self, world):
        _make_ultimatum_ready(world)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.invalidate_bloc_members_cache()
        proposal = _fire(world)
        assert proposal is None or proposal.get("proposal_type") != "ultimatum"

    def test_no_fire_relation_not_hostile(self, world):
        _make_ultimatum_ready(world)
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = 0
        proposal = _fire(world)
        assert proposal is None or proposal.get("proposal_type") != "ultimatum"

    def test_no_fire_without_player_held_target(self, world):
        _make_ultimatum_ready(world)
        # hand Hanover back to its own crown — the design stays active but
        # nothing is demandable from the player's own hand
        world.regions["Hanover"].controller = "Hanover"
        world.invalidate_active_nations_cache()
        assert _ultimatum_demandable_regions("Prussia", world) == []
        proposal = _fire(world)
        # AI-2 (Stage C) conscious narrowing: with the P-Intent rung
        # live, Prussia at `align` against Hanover-held-by-Hanover may
        # legitimately court FRANCE instead (the alignment ask — the
        # Schönbrunn negotiation, played). The pin this test owns is
        # only that no ULTIMATUM fires without a demandable target.
        assert proposal is None or (
            proposal.get("proposal_type") != "ultimatum")

    def test_no_fire_inside_player_bloc(self, world):
        _make_ultimatum_ready(world)
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        assert _generate_agenda_ultimatum("Prussia", world) is None

    def test_no_fire_below_strength_ratio(self, world):
        _make_ultimatum_ready(world)
        for m in world.marshals.values():
            if m.nation == "Prussia":
                m.strength = 2200  # ~1.1x France's 2000-each — below 1.25x
        assert _generate_agenda_ultimatum("Prussia", world) is None

    def test_no_fire_on_cooldown(self, world):
        _make_ultimatum_ready(world)
        world.ai_proposal_cooldowns = {"Prussia|ultimatum": 5}
        assert _generate_agenda_ultimatum("Prussia", world) is None

    def test_no_fire_second_live_ultimatum_worldwide(self, world):
        _make_ultimatum_ready(world, "Prussia", "Hanover")
        proposal = _fire(world, "Prussia")
        deliver_ai_proposal(proposal, world)
        assert _has_live_ultimatum(world)
        # Austria is ALSO fully ready — but the world already holds one
        world.regions["Milan"].controller = "France"
        world.invalidate_active_nations_cache()
        world.nation_relations[world._make_diplo_key("France", "Austria")] = -20
        for m in world.marshals.values():
            if m.nation == "Austria":
                m.strength = 40000
        assert _generate_agenda_ultimatum("Austria", world) is None

    def test_no_fire_deckless_nation(self, world):
        # Spain has no authored deck — no acquire design, no ultimatum
        _make_ultimatum_ready(world, "Spain", "Hanover")
        assert _generate_agenda_ultimatum("Spain", world) is None

    def test_capital_never_demanded(self, world):
        # the generator's capital guard: a demand list naming the player's
        # capital produces NO territory demand at all
        terms = generate_ultimatum_terms(
            "France", world, issuer="Prussia", demand_regions=["Paris"])
        assert not any(d["type"] == "territory_cede" for d in terms["demands"])

    def test_player_issued_generator_unchanged(self, world):
        # both kwargs omitted = the legacy player-issued path (byte-compat)
        terms = generate_ultimatum_terms("Prussia", world)
        assert terms["type"] == "ultimatum_demand"
        assert terms["sweeteners"] == []
        assert terms["demands"], "player path still produces demands"


# ═══════════════════════ DIALOGUE + TRANSPORT WIRING ═══════════════════════

class TestUltimatumDialogue:
    def _delivered(self, world):
        _make_ultimatum_ready(world)
        proposal = _fire(world)
        return deliver_ai_proposal(proposal, world), proposal

    def test_dialogue_shape(self, world):
        dialogue, _ = self._delivered(world)
        assert dialogue["type"] == "incoming_ultimatum"
        actions = [o["action"] for o in dialogue["options"]]
        assert actions == ["accept_ai_ultimatum", "reject_ai_ultimatum"]
        assert "counter_ai_proposal" not in actions  # not a negotiation
        assert dialogue["context"]["proposal_type"] == "ultimatum"
        assert dialogue["popup_payload"]["is_ultimatum"] is True

    def test_delivery_sets_popup_and_notification(self, world):
        self._delivered(world)
        assert world.incoming_proposal_popup["is_ultimatum"] is True
        titles = [n.get("title", "") for n in world.notifications._pending]
        assert any("Ultimatum from Prussia" in t for t in titles)

    def test_dialogue_taxonomy(self):
        # lapses at end of turn, mailbox-eligible, outranks routine proposals
        assert "incoming_ultimatum" in DialogueManager.CURRENT_TURN_OFFER_TYPES
        assert "incoming_ultimatum" in DialogueManager.SOFT_STOP_MAILBOX_TYPES
        assert DialogueManager.DIALOGUE_PRIORITY["incoming_ultimatum"] == 2
        assert DialogueManager.MAILBOX_SUMMARY_LABELS["incoming_ultimatum"] == "Ultimatum"

    def test_pending_envoy_recovery_builder(self, world):
        from backend.main import _build_pending_envoy_popup_from_dialogue
        dialogue, _ = self._delivered(world)
        popup = _build_pending_envoy_popup_from_dialogue(world, dialogue)
        assert popup["is_ultimatum"] is True
        assert popup["from_nation"] == "Prussia"

    def test_no_second_proposal_while_ultimatum_pending(self, world):
        self._delivered(world)
        # the per-nation dedup sees the pending ultimatum (mailbox type)
        assert process_diplomatic_phase("Prussia", world) is None

    def test_godot_dtype_wired(self):
        # the standing dialogue-popup rule: dtype in the main.gd routes +
        # the popup renders the ultimatum register
        main_gd = (GODOT_SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert main_gd.count('"incoming_ultimatum"') >= 2, (
            "incoming_ultimatum must ride both the pending-envoy and "
            "mailbox-activate dtype routes in main.gd"
        )
        popup_gd = (GODOT_SCRIPTS / "incoming_proposal_popup.gd").read_text(
            encoding="utf-8")
        assert "is_ultimatum" in popup_gd
        assert "ULTIMATUM" in popup_gd

    def test_backend_routes_wired(self):
        main_py = (REPO_ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        assert main_py.count('"incoming_ultimatum"') >= 2, (
            "incoming_ultimatum must ride the /pending_envoy and "
            "/mailbox/activate dtype branches"
        )

    def test_ultimatum_actions_are_dialogue_actions_not_commands(self):
        # §8 completion corpus rule: no new typed player commands — the
        # responses are dialogue actions, so the golden corpus stays as-is
        from backend.ai.validation import VALID_ACTIONS
        assert "accept_ai_ultimatum" not in VALID_ACTIONS
        assert "reject_ai_ultimatum" not in VALID_ACTIONS


# ═══════════════════════ RESOLUTION: YIELD / DEFY / LAPSE ══════════════════

class TestUltimatumResolution:
    def _deliver(self, world, nation="Prussia", region="Hanover"):
        _make_ultimatum_ready(world, nation, region)
        proposal = _fire(world, nation)
        dialogue = deliver_ai_proposal(proposal, world)
        return CommandExecutor(), dialogue

    def test_yield_transfers_demands_to_issuer(self, world):
        executor, _ = self._deliver(world)
        result = executor.handle_diplomatic_dialogue_response(
            "yield", {"world": world})
        assert result["success"] is True
        # the design target changed hands — player → issuer
        assert world.regions["Hanover"].controller == "Prussia"
        # the gold_per_turn demand became a tribute clause player → issuer
        key = world._make_diplo_key("France", "Prussia")
        treaty = world.active_treaties.get(key)
        assert treaty is not None
        clause = next(c for c in treaty["clauses"] if c["type"] == "gold_per_turn")
        assert clause["from"] == "France"
        assert clause["to"] == "Prussia"
        # dialogue concluded + result popup set
        assert world.pending_diplomatic_dialogue is None
        assert world.proposal_result_popup["outcome"] == "accepted"
        assert any(e.get("type") == "ai_ultimatum_accepted"
                   for e in world.event_log)

    def test_yield_adds_no_player_threat(self, world):
        executor, _ = self._deliver(world)
        world.threat_level = 10
        executor.handle_diplomatic_dialogue_response("yield", {"world": world})
        # the AI annexed FRENCH soil — that is not French aggression: the
        # PLAYER's slot is untouched. (AI-4a step 5, Stage D: the annexing
        # BENEFICIARY now accrues in its OWN slot — Prussia's here — which
        # is the new correct behaviour, not this pin's subject.)
        assert world.threat_level == 10
        assert not any(s.get("source") == "ultimatum_annex"
                       for s in world.threat_sources_this_turn
                       if s.get("target", "France") == "France")
        assert any(s.get("source") == "ultimatum_annex"
                   and s.get("target") == "Prussia"
                   for s in world.threat_sources_this_turn)

    def test_yield_plants_no_marker(self, world):
        executor, _ = self._deliver(world)
        executor.handle_diplomatic_dialogue_response("yield", {"world": world})
        assert world.ultimatum_rejection_pressure == {}

    def test_defy_plants_marker_and_floors_cooldown(self, world):
        executor, _ = self._deliver(world)
        result = executor.handle_diplomatic_dialogue_response(
            "defy", {"world": world})
        assert result["success"] is True
        assert world.ultimatum_rejection_pressure["Prussia"] == (
            world.current_turn + ULTIMATUM_REJECTION_PRESSURE_TURNS
        )
        # rejection re-arms: nation cooldown + the 15-turn floor survives
        # (apply_rejection_cooldowns would have clobbered it down to 6)
        assert world.ai_proposal_cooldowns["Prussia|ultimatum"] == (
            AI_ULTIMATUM_COOLDOWN_TURNS
        )
        assert world.ai_proposal_cooldowns["Prussia|nation"] >= 1
        # nothing changed hands
        assert world.regions["Hanover"].controller == "France"
        assert world.proposal_result_popup["outcome"] == "rejected"
        assert any(e.get("type") == "ai_ultimatum_rejected"
                   for e in world.event_log)

    def test_defy_never_declares_war(self, world):
        executor, _ = self._deliver(world)
        executor.handle_diplomatic_dialogue_response("defy", {"world": world})
        # §8: no unilateral AI declare-war path — the coalition remains
        # the war-maker
        assert not world.is_at_war("France", "Prussia")

    def test_typed_accept_reject_aliases_resolve(self, world):
        executor, _ = self._deliver(world)
        result = executor.handle_diplomatic_dialogue_response(
            "reject", {"world": world})
        assert result["success"] is True
        assert "Prussia" in world.ultimatum_rejection_pressure

    def test_lapse_is_not_rejection(self, world):
        self._deliver(world)
        lapsed = world.dialogue_manager.lapse_pending_offers()
        assert any(i["offer_type"] == "incoming_ultimatum" for i in lapsed)
        assert world.ultimatum_rejection_pressure == {}
        # and the issue-time cooldown still bars a next-turn re-send
        assert world.ai_proposal_cooldowns["Prussia|ultimatum"] == (
            AI_ULTIMATUM_COOLDOWN_TURNS
        )


# ═══════════════════════ THE PRESSURE MARKER (DD8 IDIOM) ═══════════════════

class TestRejectionPressure:
    def test_marker_feeds_threat_capped(self, world):
        turn = world.current_turn
        world.ultimatum_rejection_pressure = {
            "Prussia": turn + 5, "Austria": turn + 5, "Russia": turn + 5,
        }
        # 3 active x 2/turn = 6, capped at 4
        assert _calculate_ultimatum_rejection_threat(world) == (
            ULTIMATUM_REJECTION_PRESSURE_CAP
        )

    def test_marker_expires_and_prunes(self, world):
        turn = world.current_turn
        world.ultimatum_rejection_pressure = {
            "Prussia": turn,          # expired (<= current turn)
            "Austria": turn + 3,      # live
        }
        assert _calculate_ultimatum_rejection_threat(world) == 2
        assert "Prussia" not in world.ultimatum_rejection_pressure

    def test_recorder_guards_and_refresh(self, world):
        assert record_ultimatum_rejection(world, "France") is False  # never self
        assert record_ultimatum_rejection(world, "") is False
        assert record_ultimatum_rejection(world, "Prussia") is True
        first = world.ultimatum_rejection_pressure["Prussia"]
        world.current_turn += 2
        assert record_ultimatum_rejection(world, "Prussia") is True
        assert world.ultimatum_rejection_pressure["Prussia"] == first + 2  # refresh, not stack

    def test_rejection_cooldown_applier_floors_not_overwrites(self, world):
        world.ai_proposal_cooldowns = {"Prussia|ultimatum": 14, "Prussia|nation": 9}
        apply_ultimatum_rejection_cooldowns("Prussia", world)
        assert world.ai_proposal_cooldowns["Prussia|ultimatum"] == 15
        assert world.ai_proposal_cooldowns["Prussia|nation"] == 9  # max() kept

    def test_serialization_round_trip(self, world):
        world.ultimatum_rejection_pressure = {"Prussia": 12, "Austria": 30}
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.ultimatum_rejection_pressure == {"Prussia": 12, "Austria": 30}

    def test_fresh_world_boots_empty(self, world):
        assert world.ultimatum_rejection_pressure == {}
