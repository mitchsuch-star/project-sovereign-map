"""AI-2a — diplomacy-path convergence (docs/AI_INTENT_SPEC.md §4.2, the
six seams; Stage B's parallel refactor track).

NO BEHAVIOUR CHANGE is the contract: the player-facing proposal flow —
generation, delivery, dialogue, cooldowns applied — is byte-identical
before and after (the legacy `{nation}|...` cooldown keys ARE the
recipient=player arm, so saves and existing pins hold unedited), and the
AI-AI ratify outcomes are unchanged. What is NEW is the refusal moment:
the serialized `diplomatic_refusals` record and its public campaign-log
event, without which AI-3's ladder gate is unsatisfiable (§5 pin 8).
"""

from pathlib import Path

import pytest

from backend.game_logic.ai_diplomacy import (
    NATION_REJECTION_COOLDOWN,
    REFUSAL_DEDUPE_TURNS,
    REFUSAL_MEMORY_TURNS,
    TYPE_REJECTION_COOLDOWN,
    _build_proposal_terms,
    _cooldown_keys,
    _is_on_cooldown,
    _make_proposal,
    _resolve_ai_ai_proposal,
    apply_rejection_cooldowns,
    get_refused_asks,
    record_diplomatic_refusal,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState(player_nation="France")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


# ════════════════════════════════════════════════════════════════════════
# Seam 1 — the recipient-explicit envelope (default = byte-identical)
# ════════════════════════════════════════════════════════════════════════

class TestEnvelope:
    def test_terms_default_target_is_player(self, world):
        terms = _build_proposal_terms("Prussia", "non_aggression", 0, world)
        assert terms["proposer_nation"] == "Prussia"
        assert terms["target_nation"] == "France"

    def test_terms_recipient_explicit(self, world):
        terms = _build_proposal_terms("Prussia", "non_aggression", 0, world,
                                      recipient="Austria")
        assert terms["target_nation"] == "Austria"

    def test_proposal_default_recipient_player_with_assessment(self, world):
        terms = _build_proposal_terms("Prussia", "non_aggression", 0, world)
        proposal = _make_proposal("Prussia", "non_aggression", 4, terms,
                                  world)
        assert proposal["recipient"] == "France"
        assert proposal["talleyrand_assessment"] is not None

    def test_proposal_foreign_recipient_has_no_talleyrand(self, world):
        # Talleyrand does not annotate other people's mail.
        terms = _build_proposal_terms("Prussia", "non_aggression", 0, world,
                                      recipient="Austria")
        proposal = _make_proposal("Prussia", "non_aggression", 4, terms,
                                  world, recipient="Austria")
        assert proposal["recipient"] == "Austria"
        assert proposal["talleyrand_assessment"] is None


# ════════════════════════════════════════════════════════════════════════
# Seam 4 — ordered cooldown keys; legacy format IS the player arm
# ════════════════════════════════════════════════════════════════════════

class TestCooldownReKey:
    def test_player_keys_are_the_legacy_format(self, world):
        assert _cooldown_keys("Prussia", "non_aggression", world) == (
            "Prussia|nation", "Prussia|non_aggression")
        assert _cooldown_keys("Prussia", "non_aggression", world,
                              recipient="France") == (
            "Prussia|nation", "Prussia|non_aggression")

    def test_foreign_recipient_keys_are_ordered(self, world):
        assert _cooldown_keys("Prussia", "non_aggression", world,
                              recipient="Austria") == (
            "Prussia>Austria|nation", "Prussia>Austria|non_aggression")

    def test_player_rejection_writes_legacy_keys_byte_identically(self,
                                                                  world):
        apply_rejection_cooldowns("Prussia", "non_aggression", world)
        cooldowns = world.ai_proposal_cooldowns
        assert cooldowns["Prussia|nation"] == NATION_REJECTION_COOLDOWN
        assert cooldowns["Prussia|non_aggression"] == TYPE_REJECTION_COOLDOWN
        assert not any(">" in key for key in cooldowns)

    def test_directional_cooldowns_do_not_collapse(self, world):
        # "Prussia asks Austria" must never block "Austria asks Prussia" —
        # the _make_diplo_key collapse the spec names as the trap.
        apply_rejection_cooldowns("Prussia", "non_aggression", world,
                                  recipient="Austria")
        assert _is_on_cooldown("Prussia", "non_aggression", world,
                               recipient="Austria")
        assert not _is_on_cooldown("Austria", "non_aggression", world,
                                   recipient="Prussia")
        # And the player arm is untouched by a court-to-court cooldown.
        assert not _is_on_cooldown("Prussia", "non_aggression", world)


# ════════════════════════════════════════════════════════════════════════
# Seam 5 — the refusal record (the moment that did not exist)
# ════════════════════════════════════════════════════════════════════════

class TestRefusalRecord:
    def test_record_and_read_ordered(self, world):
        assert record_diplomatic_refusal(world, "Prussia", "Austria",
                                         "non_aggression")
        asks = get_refused_asks(world, "Prussia", "Austria")
        assert len(asks) == 1
        assert asks[0]["type"] == "non_aggression"
        # The reverse direction is a different record.
        assert get_refused_asks(world, "Austria", "Prussia") == []

    def test_dedupe_window(self, world):
        assert record_diplomatic_refusal(world, "Prussia", "Austria", "x")
        assert not record_diplomatic_refusal(world, "Prussia", "Austria",
                                             "x")
        world.current_turn += REFUSAL_DEDUPE_TURNS
        assert record_diplomatic_refusal(world, "Prussia", "Austria", "x")

    def test_memory_pruning(self, world):
        record_diplomatic_refusal(world, "Prussia", "Austria", "x")
        world.current_turn += REFUSAL_MEMORY_TURNS
        assert get_refused_asks(world, "Prussia", "Austria") == []

    def test_serialization_roundtrip(self, world):
        record_diplomatic_refusal(world, "Prussia", "Austria", "x")
        restored = WorldState.from_dict(world.to_dict())
        assert (restored.diplomatic_refusals
                == world.diplomatic_refusals)

    def test_pre_ai2a_save_reads_empty(self, world):
        data = world.to_dict()
        data.pop("diplomatic_refusals", None)
        assert WorldState.from_dict(data).diplomatic_refusals == {}

    def test_player_reject_writes_the_record(self, world1805):
        # The executor path: France refuses a court's envoy.
        world = WorldState.from_dict(world1805.to_dict())
        from backend.game_logic.ai_diplomacy import (
            _build_proposal_terms as build_terms,
            _make_proposal as make_proposal,
            deliver_ai_proposal,
        )
        terms = build_terms("Prussia", "non_aggression", 0, world)
        proposal = make_proposal("Prussia", "non_aggression", 4, terms,
                                 world)
        deliver_ai_proposal(proposal, world)
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        # incoming_proposal options: 1=Accept, 2=Reject, 3=Counter.
        result = executor.handle_diplomatic_dialogue_response(
            2, {"world": world})
        assert result.get("success"), result
        asks = get_refused_asks(world, "Prussia", "France")
        assert asks and asks[0]["type"] == "non_aggression"


# ════════════════════════════════════════════════════════════════════════
# Seam 3 — one resolution arm; ratify byte-identical; refusal is public
# ════════════════════════════════════════════════════════════════════════

def _ai_ai_proposal(initiator, target, ptype="defensive_alliance"):
    return {"type": ptype, "proposer": initiator, "target": target}


class TestAiAiResolution:
    def test_ratify_outcome_unchanged(self, world1805, monkeypatch):
        # Both sides accept → the exact pre-AI-2a normalized ratify call.
        world = WorldState.from_dict(world1805.to_dict())
        import backend.game_logic.ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance",
                            lambda *a, **k: 80)
        event = _resolve_ai_ai_proposal(
            _ai_ai_proposal("Austria", "Prussia", "non_aggression"), world)
        assert event is not None
        assert event.get("type") != "ai_ai_proposal_refused"
        # R43 pair cooldown written on ratify, exactly as before.
        key = "ai_ai|" + world._make_diplo_key("Austria", "Prussia")
        assert world.ai_proposal_cooldowns.get(key, 0) > 0

    def test_refusal_recorded_and_logged(self, world1805, monkeypatch):
        world = WorldState.from_dict(world1805.to_dict())
        import backend.game_logic.ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance",
                            lambda proposal, evaluator, other, w:
                            10 if evaluator == "Prussia" else 80)
        event = _resolve_ai_ai_proposal(
            _ai_ai_proposal("Austria", "Prussia"), world)
        assert event is not None
        assert event["type"] == "ai_ai_proposal_refused"
        assert event["refused_by"] == "Prussia"
        assert get_refused_asks(world, "Austria", "Prussia")
        # Review fix [12]: the PUBLIC half — the event reached the world's
        # event log (the campaign log's source), not just the return value.
        assert any(e.get("type") == "ai_ai_proposal_refused"
                   for e in world.event_log)
        # ...and the fog filter (diplomacy has no fog) lets it through to
        # the player's campaign log surface (review fix [14] — it was
        # silently dropped by filter_campaign_log before).
        from backend.campaign_log import filter_campaign_log
        visible = filter_campaign_log(world.event_log, world)
        assert any(e.get("type") == "ai_ai_proposal_refused"
                   for e in visible)
        # Deduped: an identical refusal inside the window returns None
        # (no second campaign-log line — the every-turn re-poll is quiet).
        assert _resolve_ai_ai_proposal(
            _ai_ai_proposal("Austria", "Prussia"), world) is None

    def test_proposer_side_balk_is_silent(self, world1805, monkeypatch):
        # Review fix [7]/[15]: when the PROPOSER's own acceptance fails
        # while the recipient would sign, the ask never happened — no
        # record (a false "the recipient said no" would feed AI-3's
        # escalation), no event, and never "{X} rebuffs {X}".
        world = WorldState.from_dict(world1805.to_dict())
        import backend.game_logic.ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance",
                            lambda proposal, evaluator, other, w:
                            10 if evaluator == "Austria" else 80)
        assert _resolve_ai_ai_proposal(
            _ai_ai_proposal("Austria", "Prussia"), world) is None
        assert get_refused_asks(world, "Austria", "Prussia") == []

    def test_refusal_event_type_registered(self):
        from backend.campaign_log import (
            CAMPAIGN_LOG_TYPES,
            format_event_oneliner,
        )
        assert "ai_ai_proposal_refused" in CAMPAIGN_LOG_TYPES
        line = format_event_oneliner({
            "type": "ai_ai_proposal_refused",
            "proposer": "Austria",
            "recipient": "Prussia",
            "refused_by": "Prussia",
            "proposal_type": "defensive_alliance",
            "turn": 3,
        })
        assert "Prussia" in line and "Austria" in line

    def test_transport_routes_foreign_recipient_off_the_mailbox(
            self, world1805, monkeypatch):
        # Seam 2: a court-to-court envelope never touches the player's
        # mailbox, notifications or popup.
        world = WorldState.from_dict(world1805.to_dict())
        import backend.game_logic.ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance", lambda *a, **k: 10)
        terms = _build_proposal_terms("Austria", "non_aggression", 0,
                                      world, recipient="Prussia")
        proposal = _make_proposal("Austria", "non_aggression", 4, terms,
                                  world, recipient="Prussia")
        depth_before = len(getattr(world.dialogue_manager, "_queue", []))
        active_before = world.dialogue_manager.peek()
        mod.deliver_ai_proposal(proposal, world)
        assert world.dialogue_manager.peek() == active_before
        assert len(getattr(world.dialogue_manager, "_queue",
                           [])) == depth_before
        assert get_refused_asks(world, "Austria", "Prussia")

    def test_phase_still_ratifies_on_the_live_path(self, world1805,
                                                   monkeypatch):
        # Review fix [9] (the old form was a tautology): the July-2026
        # AI-AI fix must survive the refactor — the LIVE trigger loop
        # (evaluate → converged resolve → ratify) must actually produce a
        # treaty. Deterministic construction: Russia and Sweden both at
        # war with France, warm (40), at PEACE with each other → trigger 1
        # fires defensive_alliance; acceptance pinned high so the pin
        # tests the plumbing, not the scorer.
        world = WorldState.from_dict(world1805.to_dict())
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Sweden", "WAR", "test")
        world.enemy_nations = ["Russia", "Sweden"]
        import backend.game_logic.ai_diplomacy as mod
        monkeypatch.setattr(mod, "_ai_ai_acceptance", lambda *a, **k: 80)
        events = mod.process_ai_ai_diplomatic_phase(world)
        assert any(e.get("nation_a") == "Russia"
                   and e.get("nation_b") == "Sweden"
                   for e in events), events
        assert world.get_diplomatic_state("Russia", "Sweden") == \
            "DEFENSIVE_ALLIANCE"
