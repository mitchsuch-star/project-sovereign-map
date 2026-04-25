"""B-B7 Make Amends active-redemption verb tests.

Spec: `docs/RELIABILITY_COMMITMENTS_SPEC.md` §8.6.1 (standard variant only).
Plan: `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` §B-B7.

Covers (~10 focused tests):
  1. Success path — gold -200, DP -1, strike removed, reliability +2,
     relation +5, cooldown set to current_turn + 10
  2. Named-diplomat acknowledgment rendered in result text for all four
     foreign courts (Castlereagh / Hardenberg / Metternich / Einsiedel)
  3. `amends_offered` reaches campaign-log, dispatch queue, and
     notification collector simultaneously
  4-7. Four refusal paths: no active strikes, cooldown active, WAR or
       ARMISTICE state, insufficient resources (gold + DP)
  8. Serialization round-trip — `reparations_cooldown` survives save/load
  9. Cooldown enforcement across save/load — 10-turn window persists
 10. Strike selection rule — matured-first, else lowest-severity active

Not covered here (anti-scope, owned by other slices):
  - Grievance variant `make amends with ... for the abandoned alliance` → B-B4
  - `commitments_notice_amends_offered` committed prose + icon wiring → C-lite
  - Acceptance-formula interaction with repaired strikes → B-B1-lite (landed)
"""
from __future__ import annotations

import copy

import pytest

from backend.commands.executor import CommandExecutor
from backend.display_names import ACTION_DISPLAY, AMENDS_REFUSAL_DISPLAY
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.world_state import WorldState
from backend.notifications import AMENDS_OFFERED


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _amends_world(*, target: str = "Austria", player_gold: int = 500,
                  player_dp: int = 3) -> WorldState:
    """Build a France-player world that can legally invoke Make Amends.

    Defaults:
      - France at PEACE with `target`
      - France holds 500 gold + 3 DP (comfortable margins)
      - No existing cooldown, no active proposals
    """
    world = WorldState(player_nation="France")
    set_diplomatic_state(world, "France", target, "PEACE", "test_setup")
    world.nation_gold["France"] = int(player_gold)
    world.diplomatic_points = int(player_dp)
    # Ensure the cast-diplomat lookup is populated (Metternich, Hardenberg,
    # Castlereagh, Einsiedel, Talleyrand) — WorldState.__init__ handles this
    # but assert defensively so a regression fails here, not in voice assertions.
    assert target in world.diplomats, (
        f"test fixture broken: {target} missing from world.diplomats"
    )
    return world


def _seed_strike(world: WorldState, *, severity: str = "medium",
                 created_on: int = 0, decays_on: int = 10,
                 episode_id: str = "ep_fixture",
                 target: str = "Austria") -> dict:
    """Write a single France→target strike with explicit timing knobs.

    Bypasses `_record_betrayal_strike` so tests can pin exact
    severity / decay fields without worrying about the dual-strike-per-episode
    suppression rule.
    """
    key = f"France|{target}"
    history = getattr(world, "betrayal_history", {}) or {}
    record = history.get(key) or {"strikes": [], "categories": [], "last_turn": 0}
    strikes = list(record.get("strikes", []) or [])
    strike = {
        "severity": severity,
        "turn": int(created_on),
        "episode_id": episode_id,
        "decays_on_turn": int(decays_on),
    }
    strikes.append(strike)
    record["strikes"] = strikes
    record["last_turn"] = int(created_on)
    history[key] = record
    world.betrayal_history = history
    return strike


def _run_make_amends(world: WorldState, *, target: str = "Austria") -> dict:
    """Invoke `make_amends` through the full CommandExecutor pipeline.

    Uses the same parsed-command shape that `_parse_diplomatic_command`
    produces in production, so tests exercise the real dispatch path.
    `parsed_command["command"]` is the inner dict the executor reads.
    """
    executor = CommandExecutor()
    parsed_command = {
        "command": {
            "action": "make_amends",
            "type": "specific",
            "diplomatic_data": {
                "action": "make_amends",
                "diplomat": "Talleyrand",
                "target_nation": target,
            },
        },
    }
    return executor.execute(parsed_command, {"world": world})


# ════════════════════════════════════════════════════════════════════════════
# 1. SUCCESS PATH — cost, strike removal, reliability, relation, cooldown
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsSuccess:

    def test_success_deducts_cost_and_sets_all_deltas(self):
        world = _amends_world()
        _seed_strike(world, severity="medium", created_on=0, decays_on=10,
                     episode_id="ep_01")

        starting_gold = int(world.nation_gold["France"])
        starting_dp = int(world.diplomatic_points)
        starting_reliability = int(world.diplomatic_reliability.get("France", 0))
        rel_key = world._make_diplo_key("France", "Austria")
        starting_relation = int(world.nation_relations.get(rel_key, 0))

        result = _run_make_amends(world)

        assert result["success"] is True
        assert result["action"] == "make_amends"
        assert result["target_nation"] == "Austria"
        assert result["gold_spent"] == 200
        assert result["dp_spent"] == 1

        # Resources spent exactly
        assert int(world.nation_gold["France"]) == starting_gold - 200
        assert int(world.diplomatic_points) == starting_dp - 1
        # Reliability +2 (clamped)
        assert (int(world.diplomatic_reliability["France"])
                == starting_reliability + 2)
        # Relation +5
        assert (int(world.nation_relations[rel_key])
                == starting_relation + 5)
        # Cooldown set to current_turn + 10
        cooldown_key = world._make_diplo_key("France", "Austria")
        expected_expiry = int(world.current_turn) + 10
        assert int(world.reparations_cooldown[cooldown_key]) == expected_expiry
        # Strike removed (was the only one seeded)
        history_key = "France|Austria"
        assert history_key not in world.betrayal_history, (
            "sole strike pruning should drop the pair entry"
        )

    def test_success_preserves_other_pair_strikes(self):
        """Amends on Austria must not scrub strikes France owes Prussia."""
        world = _amends_world(target="Austria")
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "test_setup")
        _seed_strike(world, severity="medium", created_on=0, decays_on=10,
                     episode_id="ep_austria", target="Austria")
        _seed_strike(world, severity="high", created_on=0, decays_on=10,
                     episode_id="ep_prussia", target="Prussia")

        result = _run_make_amends(world, target="Austria")

        assert result["success"] is True
        # Prussia pair still carries its strike
        assert "France|Prussia" in world.betrayal_history
        prussia_strikes = world.betrayal_history["France|Prussia"]["strikes"]
        assert len(prussia_strikes) == 1
        assert prussia_strikes[0]["episode_id"] == "ep_prussia"
        # Austria pair cleared
        assert "France|Austria" not in world.betrayal_history

    def test_success_reliability_clamps_at_100(self):
        world = _amends_world()
        _seed_strike(world)
        world.diplomatic_reliability["France"] = 99

        _run_make_amends(world)

        # +2 from 99 would be 101; reliability must clamp to 100
        assert int(world.diplomatic_reliability["France"]) == 100


# ════════════════════════════════════════════════════════════════════════════
# 2. NAMED-DIPLOMAT ACKNOWLEDGMENT (all four foreign courts)
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsNamedAcknowledgment:

    @pytest.mark.parametrize("nation,diplomat,line_fragment", [
        ("Austria", "Metternich",
         "Austria acknowledges the courtesy"),
        ("Prussia", "Hardenberg",
         "Prussia records the gesture"),
        ("Britain", "Castlereagh",
         "The gesture is noted"),
        ("Saxony", "Einsiedel",
         "Saxony is grateful for the gesture"),
    ])
    def test_named_diplomat_line_appears_in_result(
        self, nation, diplomat, line_fragment,
    ):
        world = _amends_world(target=nation)
        _seed_strike(world, target=nation)

        result = _run_make_amends(world, target=nation)

        assert result["success"] is True
        assert result["target_diplomat"] == diplomat
        message = result["message"]
        # Diplomat name surfaces as the speaker
        assert diplomat in message, (
            f"expected diplomat name {diplomat!r} in result text, got:\n{message}"
        )
        # Committed Voice Bible line fragment appears verbatim
        assert line_fragment in message, (
            f"expected committed line fragment {line_fragment!r} in result "
            f"text, got:\n{message}"
        )
        # Talleyrand frame also present (both voices per §8.6.1 design intent)
        assert "Talleyrand" in message


# ════════════════════════════════════════════════════════════════════════════
# 3. `amends_offered` EMIT SURFACES (campaign log, dispatch, notification)
# ════════════════════════════════════════════════════════════════════════════

class TestAmendsOfferedEmits:

    def test_campaign_log_event_emitted(self):
        world = _amends_world()
        strike = _seed_strike(world, episode_id="ep_camp")

        _run_make_amends(world)

        log_events = [
            e for e in world.event_log if e.get("type") == "amends_offered"
        ]
        assert len(log_events) == 1
        event = log_events[0]
        assert event["episode_id"]
        assert event["actor_nation"] == "France"
        assert event["target_nation"] == "Austria"
        assert event["gold_spent"] == 200
        assert event["dp_spent"] == 1
        assert event["relation_delta"] == 5
        assert event["reliability_delta"] == 2
        assert event["cleared_strike_episode_id"] == strike["episode_id"]
        assert event["episode_id"] != event["cleared_strike_episode_id"]
        assert event["cleared_strike_severity"] == strike["severity"]
        assert event["cooldown_turns"] == 10
        assert event["target_diplomat"] == "Metternich"

    def test_campaign_log_whitelist_includes_amends_offered(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP

        assert "amends_offered" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["amends_offered"] == "diplomacy"

    def test_dispatch_event_queued(self):
        world = _amends_world()
        strike = _seed_strike(world, episode_id="ep_dispatch")

        _run_make_amends(world)

        dispatch_events = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "amends_offered"
        ]
        assert len(dispatch_events) == 1
        payload = dispatch_events[0]
        assert payload["fog_rule"] == "partial_on_nation"
        tvars = payload["template_vars"]
        assert tvars["episode_id"]
        assert tvars["actor_nation"] == "France"
        assert tvars["target_nation"] == "Austria"
        assert tvars["reliability_delta"] == 2
        assert tvars["relation_delta"] == 5
        assert tvars["cleared_strike_episode_id"] == strike["episode_id"]
        assert tvars["episode_id"] != tvars["cleared_strike_episode_id"]
        assert tvars["speaker_attribution"] == "envoy"

    def test_notification_added(self):
        world = _amends_world()
        strike = _seed_strike(world, episode_id="ep_notification")

        _run_make_amends(world)

        amends_notifs = [
            n for n in world.notifications.get_pending()
            if n.get("type") == AMENDS_OFFERED
        ]
        assert len(amends_notifs) == 1
        notif = amends_notifs[0]
        # Priority = NORMAL (COMMITMENTS_PRESENTATION_SPEC §10.3)
        assert int(notif["priority"]) == 0
        assert notif["title"] == "Amends Offered"
        details = notif["details"]
        assert details["template_key"] == "commitments_notice_amends_offered"
        assert details["icon"] == "icon_amends_offered"
        assert details["label"] == "Amends Offered"
        assert details["speaker"] == "envoy_to_target_diplomat"
        assert details["review_target"] == "ledger_commitments"
        assert details["episode_id"]
        assert details["actor_nation"] == "France"
        assert details["target_nation"] == "Austria"
        assert details["target_diplomat"] == "Metternich"
        assert details["reliability_delta"] == 2
        assert details["relation_delta"] == 5
        assert details["cleared_strike_episode_id"] == strike["episode_id"]
        assert details["episode_id"] != details["cleared_strike_episode_id"]
        assert details["cooldown_turns"] == 10

    def test_oneliner_format_renders(self):
        """Regression guard: if `amends_offered` is in the log whitelist but
        `format_event_oneliner` has no branch for it, the log overlay would
        fall through to the default `str()` path. Verify the branch exists.
        """
        from backend.campaign_log import format_event_oneliner

        event = {
            "type": "amends_offered",
            "actor_nation": "France",
            "target_nation": "Austria",
            "gold_spent": 200,
            "dp_spent": 1,
        }
        line = format_event_oneliner(event)
        assert "France offered amends to Austria" in line
        assert "200g" in line
        assert "1 DP" in line


# ════════════════════════════════════════════════════════════════════════════
# 4-7. REFUSAL PATHS (four Talleyrand-voiced advisories)
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsRefusals:

    def test_refusal_no_active_strikes(self):
        world = _amends_world()
        # No strikes seeded — France holds a clean slate vs Austria.

        result = _run_make_amends(world)

        assert result["success"] is False
        expected = AMENDS_REFUSAL_DISPLAY["no_active_strikes"].format(
            nation="Austria",
        )
        assert result["message"] == expected
        # Clean slate preserved — nothing mutated
        assert "France|Austria" not in world.betrayal_history
        assert world.reparations_cooldown == {}

    def test_refusal_cooldown_active(self):
        world = _amends_world()
        _seed_strike(world)
        # Manually set a live cooldown ending 7 turns from now
        cooldown_key = world._make_diplo_key("France", "Austria")
        world.reparations_cooldown[cooldown_key] = int(world.current_turn) + 7

        result = _run_make_amends(world)

        assert result["success"] is False
        # turns_since = 10 - 7 = 3 (three turns elapsed since last use)
        expected = AMENDS_REFUSAL_DISPLAY["cooldown_active"].format(
            nation="Austria", turns_since=3,
        )
        assert result["message"] == expected

    @pytest.mark.parametrize("blocked_state", ["WAR", "ARMISTICE"])
    def test_refusal_war_or_armistice(self, blocked_state):
        world = _amends_world()
        set_diplomatic_state(
            world, "France", "Austria", blocked_state, "test_setup",
        )
        _seed_strike(world)

        result = _run_make_amends(world)

        assert result["success"] is False
        expected = AMENDS_REFUSAL_DISPLAY["war_or_armistice"].format(
            nation="Austria",
        )
        assert result["message"] == expected
        # Ensure no state mutations leaked through — cooldown still empty
        assert world.reparations_cooldown == {}

    def test_refusal_insufficient_gold(self):
        world = _amends_world(player_gold=199)
        _seed_strike(world)

        result = _run_make_amends(world)

        assert result["success"] is False
        expected = AMENDS_REFUSAL_DISPLAY["insufficient_gold"].format(
            nation="Austria", required=200, available=199,
        )
        assert result["message"] == expected
        # Gold + DP untouched
        assert int(world.nation_gold["France"]) == 199

    def test_refusal_insufficient_dp(self):
        world = _amends_world(player_dp=0)
        _seed_strike(world)

        result = _run_make_amends(world)

        assert result["success"] is False
        expected = AMENDS_REFUSAL_DISPLAY["insufficient_dp"].format(
            nation="Austria", required=1, available=0,
        )
        assert result["message"] == expected

    def test_refusal_missing_target_nation(self):
        """Executor must reject the action when `target_nation` is absent
        so the player sees a Talleyrand-voiced prompt instead of a crash."""
        world = _amends_world()
        _seed_strike(world)
        executor = CommandExecutor()
        parsed_command = {
            "command": {
                "action": "make_amends",
                "type": "specific",
                "diplomatic_data": {
                    "action": "make_amends",
                    "diplomat": "Talleyrand",
                    # target_nation omitted on purpose
                },
            },
        }

        result = executor.execute(parsed_command, {"world": world})

        assert result["success"] is False
        assert "which nation" in result["message"].lower()

    def test_refusal_self_targeted(self):
        """Spec §8.6.1 non-goal: France cannot Make Amends with itself."""
        world = _amends_world()
        _seed_strike(world)

        result = _run_make_amends(world, target="France")

        assert result["success"] is False
        assert "France" in result["message"]
        # No cooldown set, no strike removed
        assert world.reparations_cooldown == {}


# ════════════════════════════════════════════════════════════════════════════
# 8-9. SERIALIZATION + COOLDOWN PERSISTENCE ACROSS SAVE/LOAD
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsPersistence:

    def test_reparations_cooldown_round_trips(self):
        world = _amends_world()
        _seed_strike(world)
        _run_make_amends(world)

        cooldown_key = world._make_diplo_key("France", "Austria")
        expected_expiry = int(world.reparations_cooldown[cooldown_key])

        restored = WorldState.from_dict(copy.deepcopy(world.to_dict()))

        assert (int(restored.reparations_cooldown[cooldown_key])
                == expected_expiry)

    def test_empty_cooldown_field_survives_round_trip(self):
        """Defensive: a fresh world with no amends ever invoked should
        still round-trip without spurious keys appearing."""
        world = WorldState(player_nation="France")
        restored = WorldState.from_dict(copy.deepcopy(world.to_dict()))
        assert restored.reparations_cooldown == {}

    def test_cooldown_blocks_reinvocation_after_save_load(self):
        """After save/load, the 10-turn cooldown still refuses a second
        attempt until the original expiry turn is reached."""
        world = _amends_world()
        _seed_strike(world, episode_id="ep_1")
        first = _run_make_amends(world)
        assert first["success"] is True

        # Save / load
        restored = WorldState.from_dict(copy.deepcopy(world.to_dict()))
        # Seed a new strike on the reloaded world so only cooldown blocks us
        _seed_strike(restored, episode_id="ep_2")

        second = _run_make_amends(restored)
        assert second["success"] is False
        # Message shape matches cooldown-active advisory
        assert "offered amends to Austria" in second["message"]

        # Advance to expiry turn: current + 10 should unblock
        restored.current_turn = int(restored.current_turn) + 10
        third = _run_make_amends(restored)
        assert third["success"] is True


# ════════════════════════════════════════════════════════════════════════════
# 10. STRIKE SELECTION RULE — matured-first, else lowest-severity active
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsStrikeSelection:

    def test_prefers_oldest_matured_strike(self):
        """When multiple matured strikes coexist, the one with the earliest
        `decays_on_turn` must be cleared (same contract as §8.6 passive decay)."""
        world = _amends_world()
        world.current_turn = 20
        # Two matured strikes; their `decays_on_turn` are both in the past.
        _seed_strike(world, severity="high", created_on=0, decays_on=5,
                     episode_id="ep_oldest_matured")
        _seed_strike(world, severity="high", created_on=2, decays_on=10,
                     episode_id="ep_newer_matured")
        # One fresh, high-severity strike that should NOT be touched.
        _seed_strike(world, severity="high", created_on=18, decays_on=28,
                     episode_id="ep_fresh")

        result = _run_make_amends(world)
        assert result["success"] is True
        assert result["cleared_strike_episode_id"] == "ep_oldest_matured"

        remaining = world.betrayal_history["France|Austria"]["strikes"]
        ep_ids = {s["episode_id"] for s in remaining}
        assert "ep_oldest_matured" not in ep_ids
        assert {"ep_newer_matured", "ep_fresh"} == ep_ids

    def test_falls_back_to_lowest_severity_when_no_matured(self):
        """If no strike has reached its decay turn, the lowest-severity
        strike (with the oldest creation-turn tiebreaker) must be cleared."""
        world = _amends_world()
        world.current_turn = 0
        # All three strikes still well inside their decay windows.
        _seed_strike(world, severity="high", created_on=0, decays_on=10,
                     episode_id="ep_high")
        _seed_strike(world, severity="medium", created_on=0, decays_on=8,
                     episode_id="ep_medium")
        _seed_strike(world, severity="low", created_on=0, decays_on=6,
                     episode_id="ep_low_first")
        _seed_strike(world, severity="low", created_on=0, decays_on=6,
                     episode_id="ep_low_second")

        result = _run_make_amends(world)
        assert result["success"] is True
        # Lowest severity ("low") wins; both "low" entries are tied on turn,
        # so the selection must land on one of the two "low" strikes, never
        # on "medium" / "high". Spec tiebreaker is oldest creation turn, then
        # whatever stable order `min` produces — both satisfy the contract.
        assert result["cleared_strike_severity"] == "low"
        assert result["cleared_strike_episode_id"] in (
            "ep_low_first", "ep_low_second",
        )
        # Higher-severity strikes still in place
        remaining = world.betrayal_history["France|Austria"]["strikes"]
        remaining_severities = [s["severity"] for s in remaining]
        assert remaining_severities.count("high") == 1
        assert remaining_severities.count("medium") == 1


# ════════════════════════════════════════════════════════════════════════════
# 11. ACTION DISPLAY WIRING (R7 single-source-of-truth)
# ════════════════════════════════════════════════════════════════════════════

class TestMakeAmendsDisplayNames:

    def test_action_display_entry(self):
        """`make_amends` must be translatable via the central ACTION_DISPLAY
        map so log renderers never emit the raw internal identifier."""
        assert ACTION_DISPLAY["make_amends"] == "offers amends to"

    def test_refusal_display_contract(self):
        """All five refusal codes the executor returns must have a
        Talleyrand-voiced advisory template, and none may be empty."""
        expected = {
            "no_active_strikes",
            "cooldown_active",
            "war_or_armistice",
            "insufficient_gold",
            "insufficient_dp",
        }
        assert expected <= set(AMENDS_REFUSAL_DISPLAY.keys())
        for key, template in AMENDS_REFUSAL_DISPLAY.items():
            assert template.strip(), f"empty advisory for {key!r}"
            assert "{nation}" in template, (
                f"advisory {key!r} must accept {{nation}} slot"
            )
