"""IGR-F — the small courts write one letter, not five.

`docs/INGAME_REVIEW_FIXES_SPEC.md` §2 IGR-F. Routine asks from the lesser
courts stop arriving as N sequential blocking modals and ride ONE derived
letter-book instead, answerable row by row with each court's own voice
intact. Great-power and settlement traffic is untouched.

Three things this file exists to pin, each found by measuring master before
any code was written:

  1. **The predicate is a CONJUNCTION and the type half is load-bearing.**
     A minor court suing for peace arrives on the *identical*
     `incoming_proposal` dtype as its open-borders request, so a tier-only
     digest would batch a peace offer as routine mail. Worse,
     `_build_proposal_terms` deliberately REWRITES `terms["type"]`
     (`design_purchase` -> `open_borders`, `sell_neutrality` ->
     `non_aggression`), so a digest keyed on the terms would batch a
     province cession and a binding neutrality compact. The stable
     `context["proposal_type"]` is the only safe key.

  2. **`tier == "minor"` is the WRONG tier test.** Reis Efendi is the
     Ottoman diplomat and the Ottoman is authored `secondary`
     (`nation_config.py`), so `== "minor"` would leave untouched one of the
     two voice lines the review named as being flattened.

  3. **The blocking modal is resurrected by the SAFETY VALVE**
     (`main._include_popup_passthroughs`), not by the popup queue. It
     re-derives a modal from the ACTIVE dialogue on every response cycle
     until it is answered. Suppressing the popup slot alone does nothing.

And one pre-existing P1 fixed in passing, reproduced by hand first: with
N >= 2 proposals the popup slot held the LAST arrival while `push` had made
the FIRST one current, so the client rendered one court's letter and its
id-bound answer was refused as `stale_dialogue`. The multi-court surface
this slice exists to fix was already unanswerable.
"""

import copy

import pytest

from backend.game_logic import ai_diplomacy
from backend.game_logic.envoy_digest import (
    ROUTINE_DIGEST_TYPES,
    build_envoy_digest,
    collect_routine_small_court_dialogues,
    is_routine_small_court,
)
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _world():
    return WorldState(player_nation="France")


def _proposal(nation, proposal_type, terms_type=None, recipient="France"):
    """A producer-shaped proposal dict, as `_make_proposal` builds it.

    `terms_type` defaults to `proposal_type` but is separable on purpose:
    the whole point of keying on the stable label is that the two diverge.
    """
    tt = terms_type or proposal_type
    return {
        "source": nation,
        "recipient": recipient,
        "proposal_type": proposal_type,
        "priority": 1,
        "terms": {
            "type": tt,
            "proposer_nation": nation,
            "target_nation": "France",
            "clauses": [tt],
            "sweeteners": [],
            "demands": [],
        },
        "talleyrand_assessment": "",
        "decision_reason": "hegemony_pressure",
        "turn_generated": 1,
    }


def _deliver(world, nation, proposal_type, terms_type=None):
    return ai_diplomacy.deliver_ai_proposal(
        _proposal(nation, proposal_type, terms_type), world)


def _dialogue(nation, proposal_type, dtype="incoming_proposal",
              terms_type=None):
    """A dialogue shaped exactly like `build_ai_proposal_dialogue`'s output,
    without going through delivery (so the predicate can be probed alone)."""
    tt = terms_type or proposal_type
    return {
        "type": dtype,
        "target_nation": nation,
        "talleyrand_text": "",
        "options": [],
        "context": {
            "proposal": {"type": tt},
            "source_nation": nation,
            "acceptance_score": 0,
            "decision_reason": "hegemony_pressure",
            "proposal_type": proposal_type,
        },
        "turn_created": 1,
        "blocking": False,
        "popup_payload": {
            "from_nation": nation,
            "proposal_type": tt,
            "diplomat_line": f"{nation} speaks.",
            "clauses": ["Clause: Open borders"],
            "acceptance_hint": "",
            "diplomat_name": "an envoy",
        },
    }


def _valve(world):
    """Run the real response pipeline and return what the client would be
    shown as the blocking incoming-proposal modal (None when none)."""
    import backend.main as main_module

    response = {}
    main_module._include_popup_passthroughs(response, world)
    return response.get("incoming_proposal")


# ════════════════════════════════════════════════════════════════
# THE PREDICATE
# ════════════════════════════════════════════════════════════════

class TestPredicateTier:
    def test_a_minor_courts_routine_ask_is_batched(self):
        world = _world()
        assert is_routine_small_court(
            _dialogue("PapalStates", "open_borders"), world) is True

    def test_a_secondary_courts_routine_ask_is_batched(self):
        """THE Ottoman case. `tier == "minor"` would have excluded Reis
        Efendi, whose line the review named as the writing being flattened."""
        world = _world()
        assert world.get_power_tier("Ottoman") == "secondary"
        assert is_routine_small_court(
            _dialogue("Ottoman", "open_borders"), world) is True

    @pytest.mark.parametrize("major", ["France", "Britain", "Russia",
                                       "Austria", "Prussia"])
    def test_no_great_power_is_ever_batched(self, major):
        """Great-power traffic stays as it is — even the routine types."""
        world = _world()
        for ptype in sorted(ROUTINE_DIGEST_TYPES):
            assert is_routine_small_court(
                _dialogue(major, ptype), world) is False

    def test_an_unauthored_tag_resolves_through_the_secondary_default(self):
        """`get_power_tier` returns None, not the default — every caller
        applies `or _POWER_TIER_DEFAULT` itself. A newly-minted carve client
        must land in the letter-book, not fall out of the predicate."""
        world = _world()
        assert world.get_power_tier("Ruritania") is None
        assert is_routine_small_court(
            _dialogue("Ruritania", "open_borders"), world) is True

    def test_the_na6c_carve_clients_are_authored_small(self):
        world = _world()
        for tag in ("DuchyOfWarsaw", "Normandy", "RomanRepublic"):
            assert is_routine_small_court(
                _dialogue(tag, "non_aggression"), world) is True


class TestPredicateType:
    @pytest.mark.parametrize("ptype", ["open_borders", "non_aggression",
                                       "friendly_gift"])
    def test_the_three_routine_families_are_batched(self, ptype):
        world = _world()
        assert is_routine_small_court(_dialogue("Hesse", ptype), world) is True

    @pytest.mark.parametrize("ptype", [
        "peace", "harsh_peace", "armistice", "armistice_losing",
        "armistice_winning", "alliance", "defensive_alliance", "vassalage",
        "broker_peace", "ultimatum", "opportunistic",
    ])
    def test_no_consequential_ask_is_ever_batched(self, ptype):
        """A minor suing for peace rides the SAME dtype as its open-borders
        request. Tier alone would have batched it."""
        world = _world()
        assert is_routine_small_court(_dialogue("Bavaria", ptype), world) is False

    def test_the_allowlist_is_positive_not_a_denylist(self):
        """An unrecognised future P-rung label must default to a modal."""
        world = _world()
        assert is_routine_small_court(
            _dialogue("Bavaria", "some_future_rung_2027"), world) is False

    @pytest.mark.parametrize("ptype,rewritten", [
        ("design_purchase", "open_borders"),
        ("sell_neutrality", "non_aggression"),
        ("harsh_peace", "peace"),
    ])
    def test_the_terms_rewrite_cannot_smuggle_a_consequential_ask_in(
            self, ptype, rewritten):
        """`_build_proposal_terms` rewrites `terms["type"]` to a legal treaty
        state. Keying on it would batch a province cession and a binding
        neutrality compact as routine mail."""
        world = _world()
        dialogue = _dialogue("Bavaria", ptype, terms_type=rewritten)
        assert dialogue["context"]["proposal"]["type"] in ROUTINE_DIGEST_TYPES \
            or rewritten == "peace"
        assert is_routine_small_court(dialogue, world) is False


class TestPredicateDialogueType:
    @pytest.mark.parametrize("dtype", [
        "incoming_ultimatum", "incoming_settlement_offer",
        "ally_settlement_petition", "counter_offer",
        "counter_offer_response", "settlement_confirm", "proposal_confirm",
    ])
    def test_only_incoming_proposal_is_batched(self, dtype):
        world = _world()
        assert is_routine_small_court(
            _dialogue("Bavaria", "open_borders", dtype=dtype), world) is False

    def test_garbage_input_is_refused_rather_than_crashing(self):
        world = _world()
        for junk in (None, "", 3, [], {}, {"type": "incoming_proposal"}):
            assert is_routine_small_court(junk, world) is False


# ════════════════════════════════════════════════════════════════
# DELIVERY — the slot and the safety valve
# ════════════════════════════════════════════════════════════════

class TestDeliverySuppression:
    def test_a_small_courts_letter_never_claims_the_modal_slot(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        assert world.incoming_proposal_popup is None
        assert world.dialogue_manager.get_mailbox_count() == 1

    def test_the_safety_valve_does_not_resurrect_a_letter_as_a_modal(self):
        """The valve re-derives a modal from the ACTIVE dialogue on every
        response cycle. Without gating it, suppressing the slot achieves
        nothing at all."""
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        assert world.pending_diplomatic_dialogue["target_nation"] == "Bavaria"
        assert _valve(world) is None
        # ...and it stays gone, cycle after cycle.
        assert _valve(world) is None
        assert _valve(world) is None

    def test_a_great_powers_letter_still_raises_its_modal(self):
        world = _world()
        _deliver(world, "Prussia", "open_borders")
        shown = _valve(world)
        assert shown is not None
        assert shown["from_nation"] == "Prussia"

    def test_a_minors_peace_offer_still_raises_its_modal(self):
        world = _world()
        _deliver(world, "Bavaria", "peace")
        shown = _valve(world)
        assert shown is not None
        assert shown["from_nation"] == "Bavaria"

    def test_three_letters_raise_no_modal_at_all(self):
        world = _world()
        for nation in ("Bavaria", "Hesse", "PapalStates"):
            _deliver(world, nation, "open_borders")
        assert _valve(world) is None
        assert build_envoy_digest(world)["count"] == 3


class TestPopupSlotMirrorsTheActiveDialogue:
    """The pre-existing P1, reproduced by hand before it was fixed:

    `deliver_ai_proposal` wrote the popup slot UNCONDITIONALLY, so on a turn
    carrying two or more proposals the client was shown the LAST arrival
    while `push` had made the FIRST one current. The client round-trips the
    rendered `dialogue_id`, and the W6-0 guard refuses any id that is not the
    current top — so the first click on a multi-court turn was ALWAYS
    refused with "another matter has arrived since".
    """

    def test_the_shown_modal_is_the_answerable_dialogue(self):
        world = _world()
        _deliver(world, "Prussia", "open_borders")   # major -> becomes current
        _deliver(world, "Britain", "peace")          # major -> queued
        shown = _valve(world)
        current = world.dialogue_manager.peek()
        assert shown["from_nation"] == current["target_nation"]
        assert shown["dialogue_id"] == current["dialogue_id"]

    def test_the_answer_the_client_would_send_is_accepted(self, monkeypatch):
        """End to end through the real guard, not just an id comparison."""
        import backend.main as main_module

        world = _world()
        main_module._set_active_world(world)
        _deliver(world, "Prussia", "open_borders")
        _deliver(world, "Britain", "non_aggression")
        shown = _valve(world)

        result = main_module.executor.handle_diplomatic_dialogue_response(
            "accept", {"world": world, "executor": main_module.executor},
            dialogue_id=int(shown["dialogue_id"]),
        )
        assert result.get("stale_dialogue") is not True

    def test_a_queued_arrival_does_not_overwrite_the_slot(self):
        world = _world()
        _deliver(world, "Prussia", "peace")
        first = copy.deepcopy(world.incoming_proposal_popup)
        _deliver(world, "Austria", "alliance")
        assert world.incoming_proposal_popup == first


# ════════════════════════════════════════════════════════════════
# THE DIGEST PAYLOAD
# ════════════════════════════════════════════════════════════════

class TestDigestPayload:
    def test_no_letters_means_no_digest(self):
        world = _world()
        assert build_envoy_digest(world) is None
        _deliver(world, "Prussia", "open_borders")
        assert build_envoy_digest(world) is None

    def test_the_voice_line_survives_onto_the_row(self):
        """The whole point of the slice: volume was flattening the per-nation
        writing. The row carries the diplomat's own spoken line."""
        world = _world()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        expected = dialogue["popup_payload"]["diplomat_line"]
        assert expected  # the builder really did compose one
        row = build_envoy_digest(world)["items"][0]
        assert row["diplomat_line"] == expected

    def test_the_row_carries_both_identities_an_answer_needs(self):
        world = _world()
        dialogue = _deliver(world, "Hesse", "non_aggression")
        row = build_envoy_digest(world)["items"][0]
        assert row["mailbox_id"] == dialogue["mailbox_id"]
        assert row["dialogue_id"] == dialogue["dialogue_id"]

    def test_ptd3_row_title_follows_the_lead_clause(self):
        """PT-D3 (Aug-1 re-measure): a friendly_gift whose terms were
        rewritten to open_borders must not be titled 'Gift of Friendship'
        above a lead clause reading 'Proposal: Open Borders Agreement' —
        the header follows the terms the letter actually carries."""
        world = _world()
        _deliver(world, "Bavaria", "friendly_gift", terms_type="open_borders")
        row = build_envoy_digest(world)["items"][0]
        assert row["proposal_type_display"] == "Open Borders Agreement", (
            "the row title contradicted the row's own clauses")
        lead = str(row["clauses"][0]) if row["clauses"] else ""
        assert row["proposal_type_display"] in lead, (
            "title/lead-clause coherence is the whole point of the fix")
        # The STABLE label stays for the batching predicate (the guard
        # test below this class depends on it).
        assert row["proposal_type"] == "friendly_gift"

    def test_ptd3_agreeing_labels_stay_byte_stable(self):
        world = _world()
        _deliver(world, "Hesse", "non_aggression")
        row = build_envoy_digest(world)["items"][0]
        assert row["proposal_type_display"] == "Non-Aggression Pact"

    def test_the_active_letter_is_listed_first_and_marked(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        _deliver(world, "Hesse", "open_borders")
        items = build_envoy_digest(world)["items"]
        assert items[0]["from_nation"] == "Bavaria"
        assert items[0]["state"] == "ACTIVE"
        assert items[1]["state"] == "WAITING"

    def test_raw_nation_tags_are_preserved_for_the_client_to_repair(self):
        """Baking a static display name here is the NA-6 stage-3 dead-name
        hazard: the client's `formation_overrides` pass can only rename a
        still-raw tag."""
        world = _world()
        _deliver(world, "KingdomOfItaly", "open_borders")
        row = build_envoy_digest(world)["items"][0]
        assert row["from_nation"] == "KingdomOfItaly"

    def test_lapsing_count_is_not_the_badge_count(self):
        """`pending_envoy_count` counts persistent settlement offers too,
        which do NOT lapse. A "these lapse at turn end" header derived from
        it would be a lie."""
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        world.dialogue_manager.push({
            "type": "incoming_settlement_offer",
            "proposer_nation": "Austria",
            "war_id": "w1",
            "turn_created": 1,
        })
        digest = build_envoy_digest(world)
        assert digest["lapsing_count"] == 1
        assert world.dialogue_manager.get_mailbox_count() == 2

    def test_every_digest_row_really_does_lapse(self):
        world = _world()
        for nation in ("Bavaria", "Hesse"):
            _deliver(world, nation, "open_borders")
        for dlg in collect_routine_small_court_dialogues(world):
            assert dlg["type"] in DialogueManager.CURRENT_TURN_OFFER_TYPES

    def test_the_deadline_note_discloses_the_silent_cooldown(self):
        """Ignoring a row costs a 6-turn per-type silence from that court
        that the player has never been told about. A frictionless digest
        makes that far easier to incur."""
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        note = build_envoy_digest(world)["deadline_note"].lower()
        assert "lapse" in note
        assert "turn ends" in note
        assert "seasons" in note


class TestDigestHeadline:
    def _headline(self, nations):
        world = _world()
        for nation in nations:
            _deliver(world, nation, "open_borders")
        return build_envoy_digest(world)["headline"]

    def test_one_court_is_named(self):
        assert self._headline(["Bavaria"]) == "Bavaria writes."

    def test_a_short_list_loses_no_names(self):
        line = self._headline(["Bavaria", "Hesse", "PapalStates"])
        for name in ("Bavaria", "Hesse", "Papal States"):
            assert name in line

    def test_a_crowd_states_the_true_number(self):
        """Review [6]: this asserted `"5" in line` and then compared a helper
        that rebuilt the digest and returned `len(items)` — tautologically 5,
        never touching the headline. A `count + 10` mutation confined to this
        branch survived. Now it pins the whole sentence against the count the
        payload itself reports."""
        world = _world()
        for nation in ["Bavaria", "Hesse", "PapalStates", "Saxony", "Denmark"]:
            _deliver(world, nation, "open_borders")
        digest = build_envoy_digest(world)
        assert digest["count"] == 5
        assert digest["headline"] == "5 of the lesser courts write."

    def test_the_headline_names_a_formed_court_by_its_living_name(self):
        """Review [2]: the headline used the bare camelCase splitter, which
        knows nothing about NA-6 formations — so it baked a DEAD NAME the
        client could never repair (the repair pass matches on the still-raw
        tag, and "Kingdom Of Italy" no longer contains one).

        On the real 1805 board, because a formation needs its authored deck to
        resolve a display name at all."""
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        scenario = (root / "godot-client" / "project-sovereign" / "assets"
                    / "maps" / "europe_1805.json")
        world = WorldState.from_scenario(str(scenario))
        _deliver(world, "KingdomOfItaly", "open_borders")
        assert build_envoy_digest(world)["headline"] == "Kingdom of Italy writes."

        world.nation_formations = {
            "KingdomOfItaly": {"id": "risorgimento", "sponsor": "France",
                               "turn": 1}}
        assert build_envoy_digest(world)["headline"] == "Italy writes."

    def test_the_headline_agrees_with_the_row_label(self):
        """They sit twenty pixels apart. The Ottoman rendered as "Ottoman" in
        the sentence and "Ottoman Empire" on the row, with no formation
        involved at all — the splitter simply is not the R7 chokepoint."""
        from backend.game_logic.formations import formed_display_name

        for tag in ("Ottoman", "KingdomOfItaly", "PapalStates"):
            world = _world()
            _deliver(world, tag, "open_borders")
            digest = build_envoy_digest(world)
            # `from_nation` stays RAW so the client resolves it; the headline
            # is finished prose and must already carry the same answer.
            assert digest["items"][0]["from_nation"] == tag
            assert formed_display_name(world, tag) in digest["headline"]


class TestDigestTitle:
    """Review [7]: the noun follows the roster. `!= "major"` deliberately
    includes the SECONDARY courts, and calling the Porte a small court in a
    header is a different claim from batching its routine mail."""

    def test_all_minor_courts_read_as_small_courts(self):
        world = _world()
        for nation in ("Bavaria", "Hesse"):
            _deliver(world, nation, "open_borders")
        assert build_envoy_digest(world)["title"] == "THE SMALL COURTS WRITE"

    def test_a_secondary_court_drops_the_word_small(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        _deliver(world, "Ottoman", "open_borders")
        assert build_envoy_digest(world)["title"] == "THE COURTS WRITE"

    def test_one_letter_is_not_plural(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        assert build_envoy_digest(world)["title"] == "A SMALL COURT WRITES"
        world2 = _world()
        _deliver(world2, "Ottoman", "open_borders")
        assert build_envoy_digest(world2)["title"] == "A COURT WRITES"


class TestDigestIsPure:
    def test_building_the_digest_mutates_nothing(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        _deliver(world, "Hesse", "friendly_gift")
        before = copy.deepcopy(world.dialogue_manager.to_dict())
        events_before = len(world.event_log)
        build_envoy_digest(world)
        build_envoy_digest(world)
        assert world.dialogue_manager.to_dict() == before
        assert len(world.event_log) == events_before

    def test_the_row_is_a_copy_not_a_view_of_the_dialogue(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        row = build_envoy_digest(world)["items"][0]
        row["diplomat_line"] = "TAMPERED"
        row["clauses"].append("TAMPERED")
        dialogue = world.dialogue_manager.peek()
        assert dialogue["popup_payload"]["diplomat_line"] != "TAMPERED"
        assert "TAMPERED" not in dialogue["popup_payload"]["clauses"]


# ════════════════════════════════════════════════════════════════
# THE RESPONSE ENVELOPE
# ════════════════════════════════════════════════════════════════

class TestResponseEnvelope:
    def test_every_gameplay_response_carries_the_key(self):
        import backend.main as main_module

        world = _world()
        main_module._set_active_world(world)
        response = main_module.build_base_response(world, success=True)
        assert "envoy_digest" in response
        assert response["envoy_digest"] is None
        _deliver(world, "Bavaria", "open_borders")
        assert main_module.build_base_response(
            world, success=True)["envoy_digest"]["count"] == 1

    def test_the_browse_endpoint_serves_the_same_derived_payload(self):
        import backend.main as main_module

        world = _world()
        main_module._set_active_world(world)
        _deliver(world, "Bavaria", "open_borders")
        payload = main_module.get_mailbox()
        assert payload["envoy_digest"]["count"] == 1
        assert payload["envoy_digest"] == build_envoy_digest(world)

    def test_the_digest_is_deferred_behind_the_end_turn_report(self):
        """Every `_post_hud_response_routes` entry returns from
        `_on_command_result` before the enemy-phase dialog and the dispatch
        are shown. A choice surface arriving on that response would swallow
        the whole end-turn tail — the NA-6b P1. So it is blanked there and
        rebuilt on the next response."""
        import backend.main as main_module

        world = _world()
        main_module._set_active_world(world)
        _deliver(world, "Bavaria", "open_borders")
        response = main_module.build_base_response(world, success=True)
        assert response["envoy_digest"] is not None

        response = {"enemy_phase": {"nations": []}}
        main_module._apply_command_popup_contract(response, {}, world)
        assert response["envoy_digest"] is None
        # ...and nothing was consumed: the very next response has it back.
        assert build_envoy_digest(world)["count"] == 1


# ════════════════════════════════════════════════════════════════
# POST /mailbox/respond
# ════════════════════════════════════════════════════════════════

class TestMailboxRespond:
    def _setup(self):
        import backend.main as main_module

        world = _world()
        main_module._set_active_world(world)
        return main_module, world

    def test_a_queued_letter_is_answerable_by_mailbox_id(self):
        """The W6-0 guard refuses any dialogue_id that is not the current
        top, so this only works because the endpoint activates first and
        derives the id server-side."""
        main_module, world = self._setup()
        _deliver(world, "Bavaria", "open_borders")
        third = _deliver(world, "PapalStates", "open_borders")
        assert world.dialogue_manager.peek() is not third

        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=third["mailbox_id"], choice="accept"))

        assert result["success"] is True
        assert result.get("stale_dialogue") is not True
        assert result["digest_row_answered"] == third["mailbox_id"]
        assert world.get_diplomatic_state("France", "PapalStates") == "OPEN_BORDERS"

    def test_declining_applies_the_real_rejection_path(self):
        main_module, world = self._setup()
        dialogue = _deliver(world, "Hesse", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="reject"))
        assert result["success"] is True
        assert world.get_diplomatic_state("France", "Hesse") != "OPEN_BORDERS"
        assert any(e.get("type") == "ai_proposal_rejected"
                   for e in world.event_log)

    def test_answering_raises_no_result_modal(self):
        """Three accepts would otherwise raise three `proposal_result`
        modals — the same storm, moved one surface downstream.

        Both halves of the suppression are pinned. `proposal_result is None`
        alone is satisfied by the demotion failsafe at the tail of
        `_respond_to_dialogue_sync`, so it does NOT bind the PL-14 gate:
        under a mutation that ignores `suppress_result_popup` the net still
        builds a popup and the failsafe still nulls it. What distinguishes
        them is `digest_row_result` — populated only when something actually
        made a popup that had to be demoted. For the letter-book's scoped
        types nothing does, and the outcome rides `message` instead.
        """
        main_module, world = self._setup()
        for nation in ("Bavaria", "Hesse", "PapalStates"):
            _deliver(world, nation, "open_borders")
        for row in list(build_envoy_digest(world)["items"]):
            result = main_module.respond_to_mailbox_item(
                main_module.MailboxRespondRequest(
                    mailbox_id=row["mailbox_id"], choice="accept"))
            assert result["success"] is True
            assert result.get("proposal_result") is None
            assert result.get("digest_row_result") is None
        assert world.proposal_result_popup is None
        assert build_envoy_digest(world) is None

    def test_a_popup_set_by_a_handler_survives_to_the_next_response(self):
        """Whatever raises a result popup, the letter-book must neither show
        it (a modal chain) nor destroy it (review finding [1]). It waits.

        This replaces an earlier `digest_row_result` demotion, which the same
        review showed had no client reader and which the drain fix made
        unreachable — one rule now covers both: the letter-book never touches
        the popup queue."""
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        world.dialogue_manager.activate_mailbox_item(dialogue["mailbox_id"])
        world.proposal_result_popup = {
            "target_nation": "Bavaria",
            "proposal_type": "Diplomatic Action",
            "outcome": "ACCEPT",
            "message": "set by a handler",
        }
        result = main_module._respond_to_dialogue_sync(
            "accept", dialogue_id=dialogue["dialogue_id"],
            suppress_result_popup=True)
        assert result.get("proposal_result") is None
        assert world.proposal_result_popup["message"] == "set by a handler"

    def test_the_outcome_still_reaches_the_player_inline(self):
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert "Bavaria" in str(result["message"])

    def test_a_great_powers_letter_cannot_be_answered_from_the_letter_book(self):
        """The endpoint must never become a way to accept a consequential
        treaty with one unconsidered click."""
        main_module, world = self._setup()
        dialogue = _deliver(world, "Prussia", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert result["success"] is False
        assert "letter-book" in result["message"]
        assert world.get_diplomatic_state("France", "Prussia") != "OPEN_BORDERS"

    def test_a_minors_alliance_cannot_be_answered_from_the_letter_book(self):
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "defensive_alliance")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert result["success"] is False
        assert world.get_diplomatic_state(
            "France", "Bavaria") != "DEFENSIVE_ALLIANCE"

    def test_an_unknown_row_is_refused_with_its_own_reason(self):
        """The MESSAGE, not just `success is False` — a row that never
        existed and a row too weighty to answer here are different refusals
        and both set `digest_row_failed`, so the flag alone binds nothing.
        A vanished letter must not be reported as one the player may not
        answer: rows DO vanish unanswered (coalition formation removes every
        live proposal from a joining court, silently)."""
        main_module, world = self._setup()
        _deliver(world, "Bavaria", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(mailbox_id=9999, choice="accept"))
        assert result["success"] is False
        assert result["digest_row_failed"] == 9999
        assert "no longer among the pending envoys" in result["message"]
        assert "letter-book" not in result["message"]

    def test_a_hard_stop_blocks_the_letter_book_and_says_so(self):
        """`activate_mailbox_item` refuses while a hard stop holds the slot.
        Firing anyway would land the answer on the hard stop."""
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        world.dialogue_manager.preempt({
            "type": "settlement_confirm",
            "turn_created": 1,
        })
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert result["success"] is False
        assert world.pending_diplomatic_dialogue["type"] == "settlement_confirm"

    def test_the_response_is_a_full_gameplay_envelope(self):
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert isinstance(result["pending_envoy_count"], int)
        assert "envoy_digest" in result
        assert "active_wars" in result
        assert "game_state" in result

    def test_answering_a_row_does_not_destroy_a_queued_popup(self):
        """Review [1]: `build_base_response` DRAINS the popup queue and
        `pop_highest` REMOVES the entry — but the letter-book's client handler
        reads only `success`/`message`, so the payload died in the response.
        Reachable on the ordinary path: the enemy-phase response defers every
        choice popup, then the letter-book opens over them. A one-shot
        `diplomatic_sabotage_popup` was lost PERMANENTLY."""
        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        world.diplomatic_sabotage_popup = {"probe": True}
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        assert result["success"] is True
        assert world.diplomatic_sabotage_popup == {"probe": True}
        assert result.get("diplomatic_sabotage") is None

    @pytest.mark.parametrize("mailbox_id,setup", [
        (9999, None),
        (None, "great_power"),
    ])
    def test_a_refused_click_does_not_destroy_a_queued_popup_either(
            self, mailbox_id, setup):
        main_module, world = self._setup()
        if setup == "great_power":
            mailbox_id = _deliver(world, "Prussia", "open_borders")["mailbox_id"]
        else:
            _deliver(world, "Bavaria", "open_borders")
        world.diplomatic_sabotage_popup = {"probe": True}
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=mailbox_id, choice="accept"))
        assert result["success"] is False
        assert world.diplomatic_sabotage_popup == {"probe": True}

    def test_the_response_still_carries_every_popup_key(self):
        """Not draining must not mean not present — the Godot contract wants
        the keys on every gameplay response."""
        from backend.models.cooldown_manager import PopupQueue

        main_module, world = self._setup()
        dialogue = _deliver(world, "Bavaria", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=dialogue["mailbox_id"], choice="accept"))
        for key in set(PopupQueue.RESPONSE_KEYS.values()):
            assert key in result

    def test_the_digest_refreshes_in_the_same_response(self):
        main_module, world = self._setup()
        _deliver(world, "Bavaria", "open_borders")
        second = _deliver(world, "Hesse", "open_borders")
        result = main_module.respond_to_mailbox_item(
            main_module.MailboxRespondRequest(
                mailbox_id=second["mailbox_id"], choice="accept"))
        assert result["envoy_digest"]["count"] == 1
        assert result["envoy_digest"]["items"][0]["from_nation"] == "Bavaria"


# ════════════════════════════════════════════════════════════════
# WHAT MUST NOT CHANGE
# ════════════════════════════════════════════════════════════════

class TestUntouched:
    def test_no_new_popup_queue_slot(self):
        from backend.models.cooldown_manager import PopupQueue

        assert len(PopupQueue.PRIORITY_ORDER) == 11
        assert len(PopupQueue.RESPONSE_KEYS) == 11

    def test_no_new_campaign_log_type(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES

        assert len(CAMPAIGN_LOG_TYPES) == 160  # 157->158 flipped consciously: PC15-1 adds `marshal_destroyed` (corps annihilation had NO event type — Ney and Murat fell unannounced in the Aug-15 flagship). Prior: 156->157 CA9-F13 `order_voided_by_battle`.  # 158->160 flipped consciously: WIN-D3 adds `evacuation_granted` + `evacuation_lapsing` (internment itself reuses PC15-1's `marshal_destroyed` with cause="interned").

    def test_no_new_dialogue_type(self):
        assert "envoy_digest" not in DialogueManager.DIALOGUE_PRIORITY
        assert "envoy_digest" not in DialogueManager.SOFT_STOP_MAILBOX_TYPES

    def test_the_letters_are_not_collapsed_into_one_dialogue(self):
        """Lapse applies a per-nation acceptance cooldown, a per-type lapse
        cooldown and one `offer_lapsed` record PER item. Collapsing N courts
        into one aggregate dialogue would silently destroy N-1 of each."""
        world = _world()
        for nation in ("Bavaria", "Hesse", "PapalStates"):
            _deliver(world, nation, "open_borders")
        lapsed = world.dialogue_manager.lapse_pending_offers()
        assert len(lapsed) == 3
        assert {row["nation"] for row in lapsed} == {
            "Bavaria", "Hesse", "PapalStates"}

    def test_the_badge_still_counts_every_pending_envoy(self):
        world = _world()
        _deliver(world, "Bavaria", "open_borders")
        _deliver(world, "Prussia", "peace")
        assert world.dialogue_manager.get_mailbox_count() == 2


# ════════════════════════════════════════════════════════════════
# THE CLIENT CONTRACT (source pins — the panel has no pytest coverage)
# ════════════════════════════════════════════════════════════════

def _gd(name):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    path = (root / "godot-client" / "project-sovereign" / "scripts" / name)
    return path.read_text(encoding="utf-8")


class TestClientContract:
    def test_the_digest_is_not_a_pre_empting_route(self):
        """Every `_post_hud_response_routes` entry returns from
        `_on_command_result` BEFORE `_display_result`. Routing the letter-book
        there would have swallowed the output of the command the player had
        just typed — replacing a storm of modals with a surface that eats
        your orders."""
        source = _gd("main.gd")
        start = source.index("_post_hud_response_routes = [")
        end = source.index("]", start)
        assert "envoy_digest" not in source[start:end]

    def test_the_digest_is_raised_from_the_control_return_tail(self):
        source = _gd("main.gd")
        start = source.index("func _return_control_to_player")
        end = source.index("\nfunc ", start + 10)
        assert "_show_pending_envoy_digest()" in source[start:end]

    def test_closing_the_letter_book_hands_control_back(self):
        source = _gd("main.gd")
        start = source.index("func _on_mailbox_panel_closed")
        end = source.index("\nfunc ", start + 10)
        assert "set_input_enabled(true)" in source[start:end]

    def test_the_panel_is_latched_per_turn(self):
        """Derived fresh on every response — without the latch a closed panel
        re-opens on the next one, which is an infinite modal."""
        source = _gd("main.gd")
        start = source.index("func _show_pending_envoy_digest")
        end = source.index("\nfunc ", start + 10)
        body = source[start:end]
        assert "_envoy_digest_shown_turn = _pending_envoy_digest_turn" in body
        assert "mailbox_panel.visible" in body

    def test_the_row_buttons_latch_while_an_answer_is_in_flight(self):
        source = _gd("mailbox_panel.gd")
        start = source.index("func _on_row_action")
        end = source.index("\nfunc ", start + 10)
        assert "set_row_buttons_enabled(false)" in source[start:end]

    def test_only_digest_rows_get_inline_buttons(self):
        source = _gd("mailbox_panel.gd")
        assert "var digest_row = _digest_rows.get(mailbox_id)" in source
        assert "if digest_row != null:" in source

    def test_the_client_posts_to_the_atomic_endpoint(self):
        assert "/mailbox/respond" in _gd("api_client.gd")

    # ── Review [3]: eight `.gd` mutations survived 83/83. These are the two
    # load-bearing ones plus the call sites the repo pins by convention
    # everywhere except here. The panel has no runtime test, in a repo that
    # has already shipped a `.gd` regression that killed the client for a day.

    def _body(self, name, func):
        source = _gd(name)
        start = source.index(f"func {func}")
        end = source.index("\nfunc ", start + 10)
        return source[start:end]

    def test_the_digest_is_actually_stashed(self):
        """`_pending_envoy_digest_turn` is written positively in exactly one
        place with exactly one call site. Delete either and
        `_show_pending_envoy_digest` returns false forever — the letter-book
        never auto-raises and every other test still passes."""
        body = self._body("main.gd", "_on_command_result")
        assert "_stash_envoy_digest(response)" in body
        stash = self._body("main.gd", "_stash_envoy_digest")
        assert "_pending_envoy_digest_turn = digest_turn" in stash

    def test_the_row_action_signal_is_connected(self):
        assert ("mailbox_panel.row_action.connect(_on_mailbox_row_action)"
                in _gd("main.gd"))

    def test_the_row_action_actually_calls_the_endpoint(self):
        body = self._body("main.gd", "_on_mailbox_row_action")
        assert "api_client.respond_to_mailbox_item(" in body

    def test_a_failed_answer_re_enables_the_buttons(self):
        body = self._body("main.gd", "_on_mailbox_row_action_result")
        assert "set_row_buttons_enabled(true)" in body

    def test_a_lone_letter_still_opens_the_panel_not_a_modal(self):
        """Reverting two tokens sends a single small-court letter back into
        `activate_mailbox_item` — the exact modal this slice replaces — on
        what the measurements say is the common board state."""
        body = self._body("main.gd", "_on_mailbox_list_result")
        assert "if count == 1 and not has_digest:" in body

    def test_the_latches_are_cleared_on_a_world_swap(self):
        body = self._body("main.gd", "_reset_frontend_state_for_world_swap")
        assert "_envoy_digest_shown_turn = -1" in body
        assert "_pending_envoy_digest_turn = -1" in body

    def test_the_panel_header_is_not_overwritten_by_the_digest(self):
        """Review [4]: the 'they lapse at turn end' promise is false over a
        settlement offer, which never lapses — so it is a caption over the
        digest's own rows, not the panel-wide subtitle."""
        source = _gd("mailbox_panel.gd")
        assert 'title_label.text = "PENDING ENVOYS (%d)" % count' in source
        assert "func _build_digest_caption" in source
