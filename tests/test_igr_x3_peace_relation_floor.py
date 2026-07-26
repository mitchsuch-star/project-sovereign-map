"""IGR-X3 — a beaten enemy signs; it does not have to like you first.

`docs/BUG_FIXES.md` IGR-X3. The player could not end a war bilaterally with
any of the three courts the 1805 campaign opens against, in either direction,
because `STATE_RELATION_REQUIREMENTS["PEACE"] = -60` vetoed the ratification
after the acceptance formula had already said yes.

Four things made that a defect rather than a difficulty, all measured:

  1. **It charged hostility twice.** `calculate_acceptance` already carries a
     relations term, and R141 deliberately DAMPENS it during war to
     `max(-10, min(10, rel/4))` with the recorded rationale "prevents deep
     hatred from making wartime peace mathematically impossible". The floor
     re-imposed absolutely what R141 had just made partial.
  2. **It applied to the player alone** (`if is_player_treaty:`). Two AI
     courts at -95 signed peace freely — a Golden Rule 5 violation with no
     countervailing contract, and one born as scaffolding in the commit that
     unified AI-AI ratification.
  3. **It was a route artefact.** The multilateral settlement never consulted
     it, so the identical peace was legal or illegal depending only on which
     surface produced it.
  4. **It was never gate-blessed.** The number was authored as the
     armistice-EXPIRY branch condition — a job `ARMISTICE_AUTO_PEACE_RELATION`
     still does — and became a veto on a proposed peace only when a cleanup
     commit wired a function that had been dead for three days.

And the escape the game advertised was a lie: the one place it taught the
route said "five turns of quiet may cool tempers enough to sign" while
relation decay skipped ARMISTICE outright, so the quiet cooled nothing and
the war resumed unchanged. That is almost certainly what produced the bug
report. A truce now really does thaw.
"""

import pytest

from backend.game_logic import diplomacy as D
from backend.game_logic.diplomacy import (
    ARMISTICE_AUTO_PEACE_RELATION,
    ARMISTICE_DURATION,
    ARMISTICE_THAW_PER_TURN,
    STATE_RELATION_REQUIREMENTS,
    TRANSITION_RULES,
    check_relation_requirement,
    set_diplomatic_state,
)
from backend.models.world_state import WorldState


def _world():
    return WorldState(player_nation="France")


def _at_war(world, other, relation):
    set_diplomatic_state(world, "France", other, "WAR", "igr-x3-fixture")
    world.nation_relations[world._make_diplo_key("France", other)] = relation
    return world


def _peace(proposer, target):
    return {
        "type": "peace",
        "proposer_nation": proposer,
        "target_nation": target,
        "clauses": [],
        "sweeteners": [],
        "demands": [],
    }


# ════════════════════════════════════════════════════════════════
# THE RULE
# ════════════════════════════════════════════════════════════════

class TestTheFloorIsGoneForPeaceOnly:
    def test_peace_has_no_relation_requirement(self):
        assert STATE_RELATION_REQUIREMENTS["PEACE"] is None

    @pytest.mark.parametrize("relation", [-100, -95, -90, -80, -61, 0, 100])
    def test_no_hatred_blocks_a_peace(self, relation):
        assert check_relation_requirement("WAR", "PEACE", relation) is True
        assert check_relation_requirement("ARMISTICE", "PEACE", relation) is True

    @pytest.mark.parametrize("state,req", [
        ("OPEN_BORDERS", -20),
        ("NON_AGGRESSION", 0),
        ("DEFENSIVE_ALLIANCE", 20),
        ("ALLIANCE", 40),
    ])
    def test_the_friendship_ladder_is_untouched(self, state, req):
        """Nobody has to like you to stop shooting; somebody does have to
        like you to march beside you. `validate_transition` permits ANY
        upward jump, so these numbers are the only thing preventing
        WAR -> ALLIANCE."""
        assert STATE_RELATION_REQUIREMENTS[state] == req
        assert check_relation_requirement("WAR", state, req) is True
        assert check_relation_requirement("WAR", state, req - 1) is False

    def test_the_dead_spec_row_does_not_contradict_the_live_one(self):
        """`TRANSITION_RULES[...]["relation_req"]` has no production reader —
        `get_transition_dp_cost` consumes `dp_cost` alone. Leaving -60 there
        would be a spec table disagreeing with the rule that ships."""
        assert TRANSITION_RULES[("ARMISTICE", "PEACE")]["relation_req"] is None


class TestThePlayerCanEndAWar:
    @pytest.mark.parametrize("court,relation", [
        ("Britain", -90), ("Austria", -80), ("Russia", -80),
    ])
    def test_the_player_may_propose_peace_at_boot_hatred(self, court, relation):
        """The measured 1805 boot hatreds. All three were unendable."""
        world = _at_war(_world(), court, relation)
        event = world._ratify_treaty(_peace("France", court))
        assert event["type"] == "diplomatic_treaty_signed"
        assert world.get_diplomatic_state("France", court) == "PEACE"

    def test_the_player_may_accept_a_peace_the_ai_offered(self):
        """The other direction — `is_player_treaty` covers both, so the AI
        used to offer France a treaty the engine would not let France take."""
        world = _at_war(_world(), "Britain", -90)
        event = world._ratify_treaty(_peace("Britain", "France"))
        assert event["type"] == "diplomatic_treaty_signed"
        assert world.get_diplomatic_state("France", "Britain") == "PEACE"

    def test_the_player_still_cannot_buy_friendship(self):
        world = _at_war(_world(), "Austria", -80)
        for kind in ("open_borders", "non_aggression",
                     "defensive_alliance", "alliance"):
            fresh = _at_war(_world(), "Austria", -80)
            event = fresh._ratify_treaty(dict(_peace("France", "Austria"),
                                              type=kind))
            assert event["type"] == "diplomatic_treaty_failed", kind
            assert fresh.get_diplomatic_state("France", "Austria") == "WAR"
        assert world.get_diplomatic_state("France", "Austria") == "WAR"

    def test_the_ai_is_no_longer_privileged(self):
        """GR5. This ALREADY worked for the AI — the point is that the two
        sides now run the same rule rather than the player running a harsher
        one."""
        world = _world()
        set_diplomatic_state(world, "Austria", "Prussia", "WAR", "fixture")
        world.nation_relations[
            world._make_diplo_key("Austria", "Prussia")] = -95
        event = world._ratify_treaty(_peace("Austria", "Prussia"))
        assert event["type"] == "ai_ai_treaty"
        assert world.get_diplomatic_state("Austria", "Prussia") == "PEACE"

    def test_hostility_still_prices_the_peace_it_no_longer_vetoes(self):
        """The point is not that hatred stops mattering. It stops being
        absolute. The scorer's own relations term still pushes against a
        peace — R141 just caps how hard."""
        from backend.game_logic.diplomacy import calculate_acceptance

        hated = _at_war(_world(), "Britain", -90)
        warm = _at_war(_world(), "Britain", 0)
        terms = _peace("France", "Britain")
        hated_mod = calculate_acceptance(
            terms, hated)["components"].get("relation_modifier", 0)
        warm_mod = calculate_acceptance(
            terms, warm)["components"].get("relation_modifier", 0)
        assert hated_mod < warm_mod
        assert hated_mod >= -10, "R141 clamps the wartime relations term"


# ════════════════════════════════════════════════════════════════
# THE TRUCE ACTUALLY COOLS TEMPERS NOW
# ════════════════════════════════════════════════════════════════

class TestTheTruceThaws:
    def test_a_truce_thaws_toward_the_neutral_band(self):
        world = _at_war(_world(), "Britain", -90)
        set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "fixture")
        key = world._make_diplo_key("France", "Britain")
        seen = []
        for _ in range(4):
            D._process_relation_decay(world)
            seen.append(world.nation_relations[key])
        assert seen == [-87, -84, -81, -78]

    def test_war_still_freezes(self):
        """Guns firing is not a cooling-off period. Only the ARMISTICE half
        of the old two-state skip was wrong."""
        world = _at_war(_world(), "Austria", -80)
        key = world._make_diplo_key("France", "Austria")
        for _ in range(10):
            D._process_relation_decay(world)
        assert world.nation_relations[key] == -80

    def test_peace_still_drifts_at_the_old_rate(self):
        """The ordinary peacetime drift is untouched — the thaw is a truce
        rate, not a new global one."""
        world = _world()
        set_diplomatic_state(world, "France", "Saxony", "PEACE", "fixture")
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = -50
        D._process_relation_decay(world)
        assert world.nation_relations[key] == -49

    def test_two_truces_carry_a_boot_hatred_over_the_expiry_line(self):
        """The authored expiry fork becomes reachable by the passive route
        the game already advertises: `>= ARMISTICE_AUTO_PEACE_RELATION` at
        expiry converts to PEACE, below it the war resumes."""
        world = _at_war(_world(), "Britain", -90)
        key = world._make_diplo_key("France", "Britain")
        outcomes = []
        for _ in range(2):
            set_diplomatic_state(world, "France", "Britain",
                                 "ARMISTICE", "fixture")
            world.armistice_turns = {}
            for _ in range(ARMISTICE_DURATION):
                D._process_relation_decay(world)
                events = D._process_armistice_expiration(world)
                if events:
                    outcomes.append(events[0]["type"])
                    break
        assert outcomes == ["armistice_expired_war", "armistice_expired_peace"]
        assert world.nation_relations[key] == ARMISTICE_AUTO_PEACE_RELATION
        assert world.get_diplomatic_state("France", "Britain") == "PEACE"

    def test_the_thaw_is_symmetric(self):
        """It runs on the same tick for every pair — the AI's truces cool
        exactly as fast as the player's."""
        world = _world()
        set_diplomatic_state(world, "Austria", "Prussia", "ARMISTICE", "fix")
        key = world._make_diplo_key("Austria", "Prussia")
        world.nation_relations[key] = -70
        D._process_relation_decay(world)
        assert world.nation_relations[key] == -70 + ARMISTICE_THAW_PER_TURN

    def test_the_thaw_does_not_overshoot_into_affection(self):
        """The drift targets the +-10 band, as it always did."""
        world = _world()
        set_diplomatic_state(world, "France", "Saxony", "ARMISTICE", "fixture")
        key = world._make_diplo_key("France", "Saxony")
        world.nation_relations[key] = -9
        for _ in range(5):
            D._process_relation_decay(world)
        assert world.nation_relations[key] == -9


# ════════════════════════════════════════════════════════════════
# THE SWALLOWED ACCEPTANCE
# ════════════════════════════════════════════════════════════════

class TestARefusedRatificationIsNeverReportedAsAcceptance:
    def _accept(self, world, kind):
        """Through the REAL dispatch the popup's Accept button reaches, not
        the private handler — the swallow was only ever visible end to end."""
        from backend.commands.executor import CommandExecutor

        world.dialogue_manager.push({
            "type": "incoming_proposal",
            "target_nation": "Austria",
            "talleyrand_text": "",
            "options": [{"label": "Accept", "action": "accept_ai_proposal"}],
            "context": {
                "proposal": dict(_peace("Austria", "France"), type=kind),
                "source_nation": "Austria",
                "proposal_type": kind,
            },
            "turn_created": 1,
            "blocking": False,
        })
        return CommandExecutor().handle_diplomatic_dialogue_response(
            "accept", {"world": world})

    def test_a_failed_ratification_reports_failure(self):
        """Measured on master before the fix, verbatim: `success: true` with
        "You have accepted Britain's proposal. Relations with France are
        insufficient for PEACE." — the offer consumed, the cooldown applied,
        and the war carrying on."""
        world = _at_war(_world(), "Austria", -80)
        result = self._accept(world, "open_borders")
        assert result["success"] is False
        assert "could not be ratified" in result["message"]
        assert "you have accepted" not in result["message"].lower()
        assert world.get_diplomatic_state("France", "Austria") == "WAR"

    def test_a_failed_ratification_does_not_burn_the_acceptance_cooldown(self):
        """Nothing was accepted, so the court must stay free to raise it
        again — the cooldown is what made the old swallow permanent."""
        world = _at_war(_world(), "Austria", -80)
        before = dict(getattr(world, "ai_proposal_cooldowns", {}) or {})
        self._accept(world, "open_borders")
        after = dict(getattr(world, "ai_proposal_cooldowns", {}) or {})
        assert after == before

    def test_a_successful_ratification_is_untouched(self):
        world = _at_war(_world(), "Austria", -80)
        result = self._accept(world, "peace")
        assert result["success"] is True
        assert "You have accepted" in result["message"]
        assert world.get_diplomatic_state("France", "Austria") == "PEACE"


# ════════════════════════════════════════════════════════════════
# THE COPY THAT TAUGHT A MECHANISM THAT DID NOT EXIST
# ════════════════════════════════════════════════════════════════

class TestTheGateWarning:
    def _warning(self, kind, relation):
        from backend.game_logic.diplomatic_dialogue import (
            _enrich_proposal_summary,
        )
        world = _at_war(_world(), "Britain", relation)
        dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Britain",
            "options": [{"action": "execute_proposal",
                         "terms": dict(_peace("France", "Britain"),
                                       type=kind)}],
            "context": {},
        }
        enriched = _enrich_proposal_summary(dialogue, "Britain", kind, world)
        return str(enriched.get("ratification_gate_warning", ""))

    def test_peace_carries_no_gate_warning_because_there_is_no_gate(self):
        assert self._warning("peace", -90) == ""

    def test_the_friendship_ladder_still_names_its_gate(self):
        warning = self._warning("non_aggression", -80)
        assert "-80" in warning and "0" in warning

    def test_the_false_armistice_counsel_is_gone(self):
        """It read "five turns of quiet may cool tempers enough to sign"
        while decay skipped ARMISTICE, so quiet cooled nothing. Deleted
        rather than reworded — and the mechanism it described is now real."""
        import inspect

        from backend.game_logic import diplomatic_dialogue

        source = inspect.getsource(diplomatic_dialogue._enrich_proposal_summary)
        assert "may cool tempers enough to sign" not in source

    def test_no_surface_still_promises_quiet_alone_cools_tempers(self):
        """Belt and braces across the whole backend — the phrase must not
        survive anywhere, because the advice it gave was the defect."""
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "backend"
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            assert "may cool tempers enough to sign" not in text, path
