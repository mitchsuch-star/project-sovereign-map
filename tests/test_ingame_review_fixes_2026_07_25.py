"""In-game review fixes — July 25, 2026 (NA-6c/6d + AI-3r cross-element pass).

Four defects found by playing the real client and fixed in-session:

  R1  P1  Declaring war on a treaty partner soft-locked in an infinite modal
          loop (war purpose -> treaty warning -> Talleyrand objection ->
          war purpose -> ...). Each path cleared one bypass flag and dropped
          the other, so neither gate could ever be satisfied at once.
  R2  P1  Every AP-priced marshal-petition arm arrived permanently disabled:
          `enabled` was baked at BUILD time (inside the turn pass, before
          advance_turn refills AP) and rendered after the refill.
  R3  P2  Beat-7 stand-down copy: campaign_log + dispatch each kept a private
          4-entry cause map, degrading AI-3r's exposed / outmatched /
          penniless to the `starved` phrase ("the moment passed") — the very
          §0.3 lie AI-3r was written to kill.
  R4  P2  The command terminal's scrollback swallowed the mouse wheel
          (RichTextLabel with fit_content inside a ScrollContainer, missing
          scroll_active = false).
"""

import os
import re

import pytest

from backend.campaign_log import format_event_oneliner
from backend.game_logic import war_council
from backend.game_logic.jealousy import refresh_petition_affordability


# ══════════════════════════════════════════════════════════════════════
# R1 — the declare-war soft-lock
# ══════════════════════════════════════════════════════════════════════

class TestDeclareWarSoftLock:
    """Both bypass flags must survive the round trip through BOTH gates."""

    def _source(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backend", "commands", "diplomatic_executor.py",
        )
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_objection_stashes_context_that_survives_delivery(self):
        """The popup is POPPED by the passthrough that delivers it, so the
        declare-war context must be stashed somewhere that outlives it."""
        src = self._source()
        popup_block = src[src.index('"type": "talleyrand_objection"'):]
        popup_block = popup_block[:popup_block.index("return {")]
        assert "_declare_war_objection_context" in popup_block, (
            "raising the declare-war objection must stash war_objective + the "
            "treaty resolution on a transient attr; reading them back off the "
            "popup fails because _include_popup_passthroughs already popped it"
        )
        assert '"_treaty_warning_resolved"' in popup_block
        assert '"war_objective"' in popup_block

    def test_objection_proceed_passes_both_flags(self):
        """`Proceed Anyway` re-enters with confirmed_objection AND the
        treaty resolution — the loop is broken only if BOTH ride along."""
        src = self._source()
        idx = src.index('if popup_action == "diplomatic_declare_war":')
        block = src[idx:idx + 1800]
        assert '"confirmed_objection": True' in block
        assert '"_treaty_warning_resolved": popup_treaty_resolved' in block
        assert "_declare_war_objection_context" in block, (
            "the objection-proceed path must read the stashed context"
        )
        assert "world._declare_war_objection_context = None" in block, (
            "the transient context must be consumed, not left to leak into a "
            "later, unrelated declaration"
        )

    def test_force_declare_war_preserves_confirmed_objection(self):
        """The mirror half: the treaty-warning 'Proceed' must not discard an
        objection the player already answered."""
        src = self._source()
        idx = src.index('elif action == "force_declare_war":')
        block = src[idx:idx + 1800]
        assert '"confirmed_objection"' in block, (
            "force_declare_war must carry confirmed_objection through, or an "
            "objection answered before the treaty warning fires twice"
        )

    def test_no_path_sets_only_one_flag(self):
        """Regression guard: every declare-war re-entry that sets one bypass
        flag sets the other too."""
        src = self._source()
        for match in re.finditer(r"_execute_diplomatic_declare_war\(\s*\{(.{0,700}?)\}\s*,\s*world",
                                 src, re.S):
            body = match.group(1)
            has_treaty = "_treaty_warning_resolved" in body
            has_obj = "confirmed_objection" in body
            # A first-entry call sets neither; a re-entry must set both.
            assert has_treaty == has_obj, (
                "a declare-war re-entry sets only one bypass flag — this is "
                f"exactly the July 25 soft-lock shape:\n{body.strip()[:400]}"
            )


# ══════════════════════════════════════════════════════════════════════
# R2 — petition affordability is decided at DELIVERY, not at build
# ══════════════════════════════════════════════════════════════════════

class _APWorld:
    def __init__(self, ap):
        self.actions_remaining = ap


class TestPetitionAffordability:

    def _petition(self):
        return {
            "kind": "jealousy_confrontation",
            "options": [
                {"id": "acknowledge", "label": "Acknowledge", "enabled": True},
                {"id": "promise", "label": "Promise Glory",
                 "cost_note": "1 AP", "ap_cost": 1,
                 "enabled": False},          # baked at AP 0 during the turn pass
                {"id": "rebuke", "label": "Rebuke", "enabled": True},
            ],
        }

    def test_priced_arm_reenabled_when_player_can_afford_it(self):
        """The live defect: shown at 4/4 AP but built at 0 AP."""
        out = refresh_petition_affordability(self._petition(), _APWorld(4))
        promise = next(o for o in out["options"] if o["id"] == "promise")
        assert promise["enabled"] is True
        assert "unavailable_reason" not in promise

    def test_priced_arm_stays_disabled_when_genuinely_unaffordable(self):
        out = refresh_petition_affordability(self._petition(), _APWorld(0))
        promise = next(o for o in out["options"] if o["id"] == "promise")
        assert promise["enabled"] is False

    def test_disabled_arm_states_its_reason(self):
        """GR9: never grey a player-facing choice silently."""
        out = refresh_petition_affordability(self._petition(), _APWorld(0))
        promise = next(o for o in out["options"] if o["id"] == "promise")
        assert "action point" in promise["unavailable_reason"]
        assert "you have 0" in promise["unavailable_reason"]

    def test_free_arms_untouched(self):
        out = refresh_petition_affordability(self._petition(), _APWorld(0))
        for oid in ("acknowledge", "rebuke"):
            opt = next(o for o in out["options"] if o["id"] == oid)
            assert opt["enabled"] is True
            assert "unavailable_reason" not in opt

    def test_does_not_mutate_the_stored_petition(self):
        """The world's copy must not be rewritten by a render."""
        petition = self._petition()
        before = petition["options"][1]["enabled"]
        refresh_petition_affordability(petition, _APWorld(4))
        assert petition["options"][1]["enabled"] is before

    def test_malformed_petitions_pass_through(self):
        assert refresh_petition_affordability(None, _APWorld(4)) is None
        assert refresh_petition_affordability({}, _APWorld(4)) == {}

    def test_every_priced_option_in_jealousy_declares_ap_cost(self):
        """Any arm with an 'N AP' cost_note must carry ap_cost, or the
        refresher cannot re-derive it and the arm silently stays dead."""
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backend", "game_logic", "jealousy.py",
        )
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        priced = re.findall(r'"cost_note":\s*(?:f?"[^"]*AP[^"]*"|f"\{[A-Z_]+\} AP")', src)
        assert priced, "expected priced petition arms to exist"
        # Every priced literal must be followed by an ap_cost within the dict.
        for match in re.finditer(r'\{"id":.*?\}', src, re.S):
            body = match.group(0)
            if re.search(r'"cost_note":\s*f?"[^"]*AP', body) or '{CONFRONT_PROMISE_AP} AP' in body:
                assert '"ap_cost"' in body, (
                    f"priced petition option lacks ap_cost:\n{body[:260]}"
                )

    def test_main_refreshes_petition_at_the_delivery_seam(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backend", "main.py",
        )
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        assert "refresh_petition_affordability" in src, (
            "the popup passthrough must re-derive affordability, since the "
            "petition was built before advance_turn refilled AP"
        )


# ══════════════════════════════════════════════════════════════════════
# R3 — beat-7 cause copy covers the WHOLE AI-3r taxonomy
# ══════════════════════════════════════════════════════════════════════

AI3R_CAUSES = ("exposed", "outmatched", "penniless")
STARVED_PHRASE = "the moment passed"


class TestCrisisCauseCopy:

    def test_every_engine_cause_has_its_own_short_phrase(self):
        seen = {}
        for cause in war_council._CRISIS_CAUSE_COPY:
            phrase = war_council.crisis_cause_phrase(cause)
            assert phrase, cause
            seen[cause] = phrase
        # No two distinct causes may share copy — that is how the lie hid.
        assert len(set(seen.values())) == len(seen), seen

    @pytest.mark.parametrize("cause", AI3R_CAUSES)
    def test_ai3r_causes_never_render_as_starved(self, cause):
        assert war_council.crisis_cause_phrase(cause) != STARVED_PHRASE

    @pytest.mark.parametrize("cause", AI3R_CAUSES)
    def test_campaign_log_oneliner_is_honest(self, cause):
        line = format_event_oneliner({
            "type": "crisis_passed",
            "nation": "Prussia",
            "target": "Hanover",
            "cause": cause,
        })
        assert "THE CRISIS PASSES" in line
        assert STARVED_PHRASE not in line, (
            f"campaign log rendered '{cause}' as the starved phrase: {line}"
        )

    @pytest.mark.parametrize("cause", AI3R_CAUSES)
    def test_dispatch_headline_is_honest(self, cause):
        from backend.game_logic.dispatch import _crisis_cause_headline
        assert _crisis_cause_headline(cause) != STARVED_PHRASE

    def test_starved_itself_still_says_the_moment_passed(self):
        assert war_council.crisis_cause_phrase("starved") == STARVED_PHRASE

    def test_soft_block_mapping_unchanged(self):
        """busy / ladder legitimately ARE decayed moments."""
        assert war_council._SOFT_BLOCK_CAUSE["busy"] == "starved"
        assert war_council._SOFT_BLOCK_CAUSE["ladder"] == "starved"
        for cause in AI3R_CAUSES:
            assert war_council._SOFT_BLOCK_CAUSE[cause] == cause


# ══════════════════════════════════════════════════════════════════════
# R5 — the pair-substitute promise must match the carry-over's reach
# ══════════════════════════════════════════════════════════════════════

class TestPairSubstituteCarryHonesty:
    """Played live: authored 'Erect Duchy of Warsaw from Prussia's lands',
    was told "Your drafted terms for Prussia carry into the talks", and got
    a bare white peace — create_client was settlement-tier and was dropped.

    IGR-D gate Q2 answered that as a SPLIT and this class was flipped with
    it: `create_client` now CARRIES (Tilsit carved the Duchy of Warsaw out
    of Prussia alone), so the honest copy must stop warning about it. The
    remaining identity clauses still cannot travel — and they no longer
    merely get named in a description, they DISABLE the bilateral peace
    (`TestSettlementTierClauseDisablesTheBilateralRoute` below).
    """

    def test_create_client_no_longer_warns_because_it_carries(self):
        """Consciously flipped by IGR-D. Was
        `test_create_client_is_named_as_not_carrying`."""
        from backend.game_logic.settlement_staging import (
            PAIR_SUBSTITUTE_CARRIED_TYPES,
            _pair_substitute_carry_description,
        )
        assert "create_client" in PAIR_SUBSTITUTE_CARRIED_TYPES
        dialogue = {"settlement_terms": [
            {"type": "create_client", "from": "Prussia", "to": "France",
             "tag": "DuchyOfWarsaw", "provinces": ["Posen"]},
        ]}
        text = _pair_substitute_carry_description(dialogue, "Prussia")
        assert "except" not in text, (
            "a carried clause must not be listed as left behind: " + text
        )
        assert text.endswith("carry into the talks.")

    def test_a_settlement_tier_clause_is_still_named(self):
        """The other half of the split — vassalage never travels, and the
        copy must keep saying so."""
        from backend.game_logic.settlement_staging import (
            _pair_substitute_carry_description,
        )
        dialogue = {"settlement_terms": [
            {"type": "vassalage", "from": "Prussia", "to": "France"},
        ]}
        text = _pair_substitute_carry_description(dialogue, "Prussia")
        assert "vassalage" in text
        assert "joint settlement" in text

    def test_money_and_territory_still_promise_a_clean_carry(self):
        from backend.game_logic.settlement_staging import (
            _pair_substitute_carry_description,
        )
        dialogue = {"settlement_terms": [
            {"type": "gold_indemnity", "from": "Prussia", "amount": 300},
            {"type": "territory_cede", "from": "Prussia", "region": "Posen"},
        ]}
        text = _pair_substitute_carry_description(dialogue, "Prussia")
        assert "carry into the talks." in text
        assert "except" not in text

    def test_other_courts_clauses_are_not_warned_about(self):
        """A clause aimed at Austria says nothing about the Prussia talks."""
        from backend.game_logic.settlement_staging import (
            _pair_substitute_carry_description,
        )
        dialogue = {"settlement_terms": [
            {"type": "create_client", "from": "Austria", "region": "Rome"},
        ]}
        text = _pair_substitute_carry_description(dialogue, "Prussia")
        assert "except" not in text

    def test_carried_type_set_matches_the_seed_functions_reach(self):
        """Drift guard: the copy's notion of 'carries' must equal the set of
        clause types _pair_substitute_seed_terms actually translates."""
        import inspect
        from backend.game_logic import settlement_actions
        from backend.game_logic.settlement_staging import (
            PAIR_SUBSTITUTE_CARRIED_TYPES,
        )
        src = inspect.getsource(settlement_actions._pair_substitute_seed_terms)
        handled = set(re.findall(r'ttype == "([a-z_]+)"', src))
        assert handled == set(PAIR_SUBSTITUTE_CARRIED_TYPES), (
            "the pair-substitute confirm copy and the carry-over logic have "
            f"drifted: seed handles {sorted(handled)}, copy claims "
            f"{sorted(PAIR_SUBSTITUTE_CARRIED_TYPES)}"
        )


# ══════════════════════════════════════════════════════════════════════
# R4 — the terminal must hand the wheel to its ScrollContainer
# ══════════════════════════════════════════════════════════════════════

class TestTerminalWheelScroll:

    def test_output_display_yields_the_wheel(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "godot-client", "project-sovereign", "scenes", "main.tscn",
        )
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        idx = src.index('[node name="OutputDisplay"')
        block = src[idx:src.index("[node", idx + 10)]
        assert "fit_content = true" in block
        assert "scroll_active = false" in block, (
            "OutputDisplay must set scroll_active=false: with fit_content its "
            "own scroll has zero range, so it swallowed the wheel and the "
            "parent OutputScroll never received it"
        )
