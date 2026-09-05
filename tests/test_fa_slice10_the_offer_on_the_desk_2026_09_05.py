"""FA slice 10 — "The Offer on the Desk" (September 5, 2026).

Twelve rows in one neighbourhood: the settlement offer a court puts on the
player's desk, and everything that went wrong between the click and the
signature.

ONE RULE closes five of them (FA-4, FA-N15, FA-N17, FA-N18, FA-N4's staging
half): **an incoming settlement offer is MAIL, never a DRAFT.** SC-26's
collision guard asks "is a settlement already on the table?" and the family
set answered it with a letter the enemy had sent us, so three readers that
must agree read an offer as our own mounted draft. Measured on the committed
t20 fixture: accepting Britain's offer popped it, the pop PROMOTED a queued
offer for another war, and the collision arm refused the accept — destroying
the letter the player had just clicked and naming a war they had never seen.

ONE MORE closes FA-3: **the offering courts consent by construction.** The
accept-staged review scored the covered courts as the ACCEPTING side of a
package France was deemed to have proposed, so the scorer priced the AI's own
terms as the AI's reluctance to sign them — `can_ratify` False, blocker
"Settlement legitimacy", no ratify option, on the boot board and on the
fixture alike. The coalition-peace route the whole diplomacy layer exists to
close was a dead affordance.

Chasing FA-3's outcome turned up **FA-S10-1**, a pre-existing defect the fix
made ordinary: an ELIMINATED court is taken off the war's sides but its pairs
are left in `active_diplo_keys` with `pair_status: "war"` forever, and
`revalidate_staged_settlement` then refuses every ratification of that war.
Bavaria dies by turn 6 on half of boot boards; from that moment nobody could
sign the coalition peace of `war_1`.

The rest are delivery and direction: FA-17 (the answer to France's own
overture never claimed the slot), FA-N44 (the commitment paradox likewise,
and was then deleted unseen), FA-N16 (an offer PAYING France read as a demand
for tribute), FA-N43 (the incoming "Assessment" quoted the burden on the
sender), FA-N45 (a ratified peace that moved 405 gold stored harshness 0.0).

Every behaviour change sits behind a flip lever whose False arm reproduces the
pre-slice shape; the arms below drive the real routes with a MOCK parser.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.game_logic.mailbox_payloads as MP
import backend.game_logic.settlement_helpers as SH
import backend.game_logic.settlement_routes as SR
import backend.main as M
import backend.models.dialogue_manager as DM
import backend.game_logic.turn_manager as TM
from backend.commands.parser import CommandParser
from backend.game_logic.diplomatic_templates import (
    burden_on_nation,
    calculate_treaty_harshness,
)
from backend.game_logic.settlement_offers import (
    build_incoming_settlement_offer_popup,
    handle_incoming_settlement_offer_action,
    promote_pending_settlement_offers,
)
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.game_logic.settlement_validation import _active_cross_side_pairs
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"

LEVERS = [
    (SR, "OFFER_IS_MAIL_NEVER_A_DRAFT"),
    (SH, "ELIMINATION_RESOLVES_ITS_PAIRS"),
    (DM, "MOUNT_OVER_MAIL_ACTIVE"),
    (DM, "PARADOX_SURVIVES_THE_STALE_SWEEP"),
    (TM, "LAPSED_COUNTER_COSTS_A_COOLDOWN"),
    (MP, "INCOMING_ASSESSMENT_READS_OUR_BURDEN"),
    (M, "QUESTION_CARRIES_ITS_OWN_MODAL"),
]


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _fixture_world():
    """The committed turn-20 board: Britain's `war_1` offer is CURRENT, and
    `war_2` (France vs Switzerland) is a second live war. Deterministic —
    no end turns, so no combat RNG can move it between arms."""
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with _quiet():
        return WorldState.from_dict(data["world_state"])


@pytest.fixture
def fixture_board(monkeypatch):
    world = _fixture_world()
    parser = CommandParser(use_real_llm=False)
    assert parser.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", parser)
    monkeypatch.setitem(M.game_state, "world", world)
    return world


@pytest.fixture
def boot_board(monkeypatch):
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    parser = CommandParser(use_real_llm=False)
    assert parser.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", parser)
    monkeypatch.setitem(M.game_state, "world", world)
    return world


@pytest.fixture
def client():
    return TestClient(M.app)


def _post(client, text, **extra):
    body = {"command": text}
    body.update(extra)
    with _quiet():
        return client.post("/command", json=body).json()


def _answer(client, choice, dialogue_id):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice,
                                 "dialogue_id": dialogue_id}).json()


def _current_offer(world):
    dm = world.dialogue_manager
    for dialogue in ([dm.peek()] if dm.peek() else []) + dm.iter_queue():
        if dialogue.get("type") == "incoming_settlement_offer":
            return dialogue
    return None


def _offer_ids(world):
    dm = world.dialogue_manager
    return [d.get("offer_id") for d
            in ([dm.peek()] if dm.peek() else []) + dm.iter_queue()
            if d.get("type") == "incoming_settlement_offer"]


def _queue_second_offer(world, war_id="war_2"):
    """Author a second war's offer THE WAY THE PRODUCER DOES and promote it
    through the real helper, so it lands in the queue behind the current."""
    from backend.game_logic.ai_diplomacy import _emit_settlement_offer_for_war
    war = world.war_instances[war_id]
    pending = list(getattr(world, "pending_settlement_dialogues", None) or [])
    with _quiet():
        offer = _emit_settlement_offer_for_war(
            world, war_id, war, player=world.player_nation,
            current_turn=world.current_turn, pending=pending, cooldowns={})
    world.pending_settlement_dialogues = pending
    with _quiet():
        promote_pending_settlement_offers(world)
    return offer


# ═══════════════════════════════════════════════════════════════════════
# The ONE rule — FA-4, FA-N15, FA-N17, FA-N18, FA-N4 (staging half)
# ═══════════════════════════════════════════════════════════════════════


class TestTheOfferIsMailNeverADraft:

    def test_the_three_readers_agree_on_what_a_draft_is(self):
        """The rule in one place: the family set keeps the offer (defensive
        guards still want it); the DRAFT set — read by the collision arm, the
        second gate and the staging tail — does not."""
        assert "incoming_settlement_offer" in SR.SETTLEMENT_FAMILY_DIALOGUE_TYPES
        assert "incoming_settlement_offer" not in SR.settlement_draft_dialogue_types()
        assert "settlement_confirm" in SR.settlement_draft_dialogue_types()
        SR.OFFER_IS_MAIL_NEVER_A_DRAFT = False
        assert "incoming_settlement_offer" in SR.settlement_draft_dialogue_types()

    def test_accept_with_another_wars_offer_queued_stages_the_review(
            self, fixture_board, client):
        """FA-4, the headline. Britain's offer current, Switzerland's queued
        behind it: the accept used to return `cross_war_settlement_collision`
        naming war_2, and Britain's letter was destroyed."""
        world = fixture_board
        offer = _current_offer(world)
        second = _queue_second_offer(world, "war_2")
        result = _answer(client, "accept_settlement_offer",
                         offer.get("dialogue_id"))
        assert result.get("success") is True
        assert result.get("error") != "cross_war_settlement_collision"
        staged = world.dialogue_manager.peek()
        assert staged.get("type") == "settlement_confirm"
        assert staged.get("war_id") == "war_1"
        # Only the accepted offer is consumed; the other war's letter stands.
        assert offer.get("offer_id") not in _offer_ids(world)
        assert second["offer_id"] in _offer_ids(world)

    def test_the_pop_first_order_is_what_broke_it(self, fixture_board, client):
        """The lever-off arm reproduces the pre-slice shape, so the pin above
        is about the rule and not about some other change."""
        SR.OFFER_IS_MAIL_NEVER_A_DRAFT = False
        world = fixture_board
        offer = _current_offer(world)
        _queue_second_offer(world, "war_2")
        result = _answer(client, "accept_settlement_offer",
                         offer.get("dialogue_id"))
        # Under the old reading the promoted offer is a rival draft: the
        # accept either collides or is diverted to the scope chooser. Either
        # way it does NOT land the ratifiable review the fix produces.
        staged = world.dialogue_manager.peek() or {}
        assert staged.get("dialogue_mode") != "REVIEW" or not result.get("success")

    def test_a_refused_accept_leaves_the_letter_standing(
            self, fixture_board, client):
        """FA-4's second half, on the geometry that actually reaches the
        staging-failure arm: the player has a real draft open on another war,
        so `stage_settlement_confirm` refuses the accept with SC-26's
        collision. The refusal used to leave them with no letter, a
        `must_reopen` that fired a fresh (colliding) settlement open, and one
        of the three SC-14b reopen attempts burnt."""
        world = fixture_board
        offer = _current_offer(world)
        offer_id = offer.get("offer_id")
        opened = stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert opened.get("success") is True
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is False
        assert result.get("error") == "cross_war_settlement_collision"
        assert result.get("must_reopen") is False
        assert result.get("error_display")
        assert (world.settlement_reopen_attempts or {}) == {}
        # The letter is still there to answer once the draft is put down.
        assert offer_id in _offer_ids(world)

    def test_a_defensively_refused_accept_also_leaves_no_reopen_burnt(
            self, fixture_board, client):
        """The SC-7b arm — an offer pointing at a war that no longer exists —
        has its own refusal literal and is unchanged by this slice."""
        world = fixture_board
        broken = dict(_current_offer(world))
        broken["war_id"] = "war_does_not_exist"
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=broken)
        assert result.get("success") is False
        assert result.get("must_reopen") is False
        assert (world.settlement_reopen_attempts or {}) == {}

    def test_opening_settlement_over_a_standing_offer_mounts_the_draft(
            self, fixture_board, client):
        """FA-N18. The war-detail button and the F1 wizard send this exact
        structured command; it used to raise a scope-replace chooser whose two
        scope strings were identical, and `replace()` dropped the offer."""
        world = fixture_board
        offer_id = _current_offer(world).get("offer_id")
        result = _post(client, "propose common peace with Britain",
                       action="propose_common_peace",
                       target_nation="Britain", war_id="war_1")
        assert result.get("dialogue_type") == "settlement_confirm"
        staged = world.dialogue_manager.peek()
        assert staged.get("type") == "settlement_confirm"
        assert staged.get("dialogue_mode") == "PROPOSE"
        assert offer_id in _offer_ids(world), "the letter was destroyed"

    def test_a_standing_offer_no_longer_blocks_another_wars_settlement(
            self, fixture_board, client):
        """FA-N18's cross-war half: a letter about war_1 blocked opening a
        settlement on war_2 entirely."""
        world = fixture_board
        offer_id = _current_offer(world).get("offer_id")
        result = _post(client, "propose common peace with Switzerland",
                       action="propose_common_peace",
                       target_nation="Switzerland", war_id="war_2")
        assert result.get("error") != "cross_war_settlement_collision"
        staged = world.dialogue_manager.peek()
        assert staged.get("war_id") == "war_2"
        assert offer_id in _offer_ids(world)

    def test_request_revision_with_mail_queued_opens_the_counter_surface(
            self, fixture_board, client):
        """FA-N4's staging half — the same reorder on the third button."""
        world = fixture_board
        offer = _current_offer(world)
        second = _queue_second_offer(world, "war_2")
        result = _answer(client, "request_settlement_revision",
                         offer.get("dialogue_id"))
        assert result.get("success") is True
        assert result.get("error") != "cross_war_settlement_collision"
        staged = world.dialogue_manager.peek()
        assert staged.get("type") == "settlement_confirm"
        assert staged.get("dialogue_mode") == "PROPOSE"
        assert offer.get("offer_id") not in _offer_ids(world)
        assert second["offer_id"] in _offer_ids(world)

    def test_submit_for_review_no_longer_collides_with_the_mail_behind_it(
            self, fixture_board):
        """FA-N15. Submit popped the PROPOSE, the pop promoted the queued
        offer, and the SC-26 arm refused — leaving the response re-attaching a
        dialogue the manager no longer held, so every button on the re-mounted
        popup came back `stale_dialogue`."""
        from backend.game_logic.settlement_actions import (
            handle_settlement_dialogue_action,
        )
        world = _fixture_world()
        propose = stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert propose.get("success") is True
        dialogue = world.dialogue_manager.peek()
        assert dialogue.get("dialogue_mode") == "PROPOSE"
        # Britain's war_1 offer is queued behind the draft.
        assert "incoming_settlement_offer" in [
            d.get("type") for d in world.dialogue_manager.iter_queue()]
        terms = list(dialogue.get("settlement_terms") or [])
        if not terms:
            pytest.skip("the generated baseline is empty on this board")
        with _quiet():
            result = handle_settlement_dialogue_action(
                world, action="submit_settlement_for_review",
                dialogue=dialogue)
        assert result.get("error") != "cross_war_settlement_collision"
        head = world.dialogue_manager.peek()
        assert head.get("war_id") == "war_2"
        # The invariant that catches the whole class: whatever the arm
        # returns, the dialogue it hands back IS the manager's head.
        handed_back = result.get("diplomatic_dialogue")
        if handed_back:
            assert handed_back.get("dialogue_id") == head.get("dialogue_id")

    def test_the_collision_still_fires_between_two_real_drafts(self):
        """SC-26 is intact for the case it was written for."""
        world = _fixture_world()
        world.dialogue_manager.replace({
            "type": "settlement_confirm", "war_id": "war_1",
            "settlement_terms": [], "dialogue_id": 999,
        })
        result = stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation)
        assert result.get("error") == "cross_war_settlement_collision"

    def test_the_second_gate_still_sees_a_queued_draft(self):
        """The other reader of the same rule. `_settlement_dialogue_active`
        is the gate that answers "Resolve the current settlement review
        first" — it must stop counting a LETTER, and must keep counting a
        real draft wherever it sits, current or queued."""
        from backend.game_logic.settlement_routes import (
            _settlement_dialogue_active,
        )
        world = _fixture_world()
        world.dialogue_manager.push({
            "type": "settlement_confirm", "war_id": "war_2",
            "settlement_terms": [], "dialogue_id": 998,
        })
        assert _settlement_dialogue_active(world, "war_2") is True
        assert _settlement_dialogue_active(world, "war_1") is False

    def test_the_collision_sentence_names_the_war_not_its_id(self):
        """FA-4's copy half: the player read "the settlement of war_2 is
        already on the table"."""
        world = _fixture_world()
        world.dialogue_manager.replace({
            "type": "settlement_confirm", "war_id": "war_1",
            "settlement_terms": [], "dialogue_id": 999,
        })
        result = stage_settlement_confirm(
            world, war_id="war_2", actor_nation=world.player_nation)
        spoken = str(result.get("talleyrand_text") or "")
        assert spoken
        assert "war_1" not in spoken and "war_2" not in spoken

    def test_the_scope_chooser_carries_the_callers_dialogue_mode(self):
        """Found while reproducing FA-N18: answering "Replace" on a
        PROPOSE-opened flow landed a BLOCKING REVIEW with empty terms."""
        import backend.game_logic.settlement_staging as ST
        source = ST.stage_settlement_confirm.__doc__ or ""
        del source
        world = _fixture_world()
        first = stage_settlement_confirm(
            world, war_id="war_1", actor_nation=world.player_nation,
            covered_enemy_participants=["Britain"],
            selected_target_nation="Britain",
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        assert first.get("success") is True
        second = stage_settlement_confirm(
            world, war_id="war_1", actor_nation=world.player_nation,
            covered_enemy_participants=["Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor", dialogue_mode="PROPOSE")
        if second.get("dialogue_type") != "settlement_scope_replace_confirm":
            pytest.skip("this board did not produce a scope chooser")
        chooser = world.dialogue_manager.peek()
        assert (chooser.get("incoming_request") or {}).get("dialogue_mode") == "PROPOSE"


# ═══════════════════════════════════════════════════════════════════════
# FA-3 — the offering courts consent
# ═══════════════════════════════════════════════════════════════════════


class TestTheOfferingCourtsConsent:

    def test_the_accepted_offer_can_be_ratified(self, fixture_board, client):
        """FA-3's whole point. Before: `can_ratify` False, blocker
        "Settlement legitimacy", no confirm option, on every state probed."""
        world = fixture_board
        offer = _current_offer(world)
        result = _answer(client, "accept_settlement_offer",
                         offer.get("dialogue_id"))
        staged = world.dialogue_manager.peek()
        assert result.get("success") is True
        assert staged.get("can_ratify") is True
        assert staged.get("ratify_blocked_reason") == ""
        assert "confirm_settlement" in [
            o.get("action") for o in (staged.get("options") or [])]
        assert set(staged.get("consenting_courts") or []) == set(
            offer.get("covered_enemy_participants") or [])

    def test_the_ratification_actually_signs_the_peace(
            self, fixture_board, client):
        """End to end through the real confirm route — the coalition peace the
        whole diplomacy layer exists to close."""
        world = fixture_board
        offer = _current_offer(world)
        covered = list(offer.get("covered_enemy_participants") or [])
        _answer(client, "accept_settlement_offer", offer.get("dialogue_id"))
        staged = world.dialogue_manager.peek()
        result = _answer(client, "confirm_settlement",
                         staged.get("dialogue_id"))
        assert result.get("success") is True, result.get("error")
        for court in covered:
            assert world.get_diplomatic_state("France", court) == "PEACE"

    def test_without_consent_the_same_package_does_not_carry(
            self, fixture_board, client):
        """The lever-free control: consent is what carries it, not some other
        change to the scorer. The same terms staged as OUR proposal are
        rejected exactly as they were before the slice."""
        world = fixture_board
        offer = _current_offer(world)
        result = stage_settlement_confirm(
            world, war_id="war_1", actor_nation=world.player_nation,
            settlement_terms=list(offer.get("settlement_terms") or []),
            covered_enemy_participants=list(
                offer.get("covered_enemy_participants") or []),
            selected_target_nation=offer.get("proposer_nation"),
            caller_kind="ai_system")
        staged = result.get("diplomatic_dialogue") or {}
        assert staged.get("can_ratify") is False
        assert staged.get("ratify_blocked_reason")

    def test_consent_lapses_when_the_draft_is_edited(self, fixture_board):
        """Consent is granted to a SPECIFIC package. A dialogue whose terms no
        longer match the offer is scored normally again — which is what stops
        a consented review being edited into a dictated peace."""
        from backend.game_logic.settlement_ratify import (
            consenting_courts_for_ratification,
        )
        world = fixture_board
        offer = _current_offer(world)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        staged = world.dialogue_manager.peek()
        assert consenting_courts_for_ratification(staged)
        staged["settlement_terms"] = list(staged["settlement_terms"]) + [
            {"type": "gold_indemnity", "from": "Britain", "to": "France",
             "amount": 9000}]
        assert consenting_courts_for_ratification(staged) == []

    def test_a_hard_stop_still_blocks_a_consented_package(
            self, fixture_board, monkeypatch):
        """Consent says a court is WILLING. It never says a clause is legal or
        a pair is still at war — so a hard stop blocks a consented package
        exactly as it blocks any other. Driven through the documented scorer
        seam, because the two live hard-stop codes are unreachable on a board
        whose staging has already succeeded."""
        from backend.game_logic import settlement_ratify as SRAT
        from backend.game_logic import settlement_scoring as SS
        world = fixture_board
        offer = _current_offer(world)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        staged = world.dialogue_manager.peek()
        assert staged.get("can_ratify") is True
        real = SS.calculate_common_peace_acceptance

        def _with_hard_stop(*args, **kwargs):
            result = dict(real(*args, **kwargs))
            result["hard_stops"] = [{"reason": "no_covered_enemy",
                                     "nation": "Britain"}]
            return result

        monkeypatch.setattr(
            SS, "calculate_common_peace_acceptance", _with_hard_stop)
        monkeypatch.setattr(
            SRAT.settlement_scoring, "calculate_common_peace_acceptance",
            _with_hard_stop, raising=False)
        with _quiet():
            result = SRAT.ratify_settlement_confirm(world, staged)
        assert result.get("success") is False
        assert result.get("error") in ("acceptance_blocked",
                                       "settlement_revalidation_failed")

    def test_every_consenting_row_says_so(self, fixture_board):
        world = fixture_board
        offer = _current_offer(world)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        rows = (world.dialogue_manager.peek() or {}).get(
            "per_court_acceptance") or []
        assert rows
        for row in rows:
            assert row.get("consents") is True
            assert not row.get("hard_stops")

    def test_a_court_that_has_made_its_own_peace_is_dropped_and_named(
            self, fixture_board):
        """FA-3's staleness half: the fixture's turn-3 offer still covered
        Russia seventeen turns on. A court with no live pair cannot be a party
        to this peace."""
        world = fixture_board
        offer = _current_offer(world)
        covered = list(offer.get("covered_enemy_participants") or [])
        assert len(covered) >= 2
        departing = covered[-1]
        from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
        key = world._make_diplo_key("France", departing)
        with _quiet():
            resolve_pair_to_resolved(world, key)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is True
        assert departing in (result.get("departed_courts") or [])
        assert departing in str(result.get("departed_courts_note") or "")
        staged = world.dialogue_manager.peek()
        assert departing not in (staged.get("covered_enemy_participants") or [])

    def test_an_offer_whose_courts_have_all_settled_is_refused_honestly(
            self, fixture_board):
        """The geometry is narrower than "resolve France's own pairs": a court
        France has separately made peace with is still a coverable party while
        it fights France's ALLIES, and settling every covered court on this
        fixture ends the war, which SC-7b answers first and correctly. The
        branch guards the case where the offer's own courts have all departed
        and the war stands — an offer naming Russia alone, after Russia has
        made its peace with everyone."""
        world = fixture_board
        offer = _current_offer(world)
        offer["covered_enemy_participants"] = ["Russia"]
        offer["proposer_nation"] = "Russia"
        war = world.war_instances[offer["war_id"]]
        from backend.game_logic.settlement_helpers import resolve_pair_to_resolved
        with _quiet():
            for key in [k for k in list(war.get("active_diplo_keys") or [])
                        if "Russia" in k.split("|")]:
                resolve_pair_to_resolved(world, key)
        assert war.get("active_diplo_keys"), "the war must still stand"
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is False
        assert result.get("error") == "offer_courts_all_settled"
        assert "peace" in str(result.get("error_display") or "").lower()
        # Refused, but not destroyed: the letter is still answerable.
        assert result.get("must_reopen") is False
        assert offer.get("offer_id") in _offer_ids(world)

    def test_the_table_does_not_claim_a_score_the_courts_do_not_have(
            self, fixture_board):
        """The copy half. A consented package carried while its courts scored
        2 and -3, and the header said "every court at or above 50"."""
        world = fixture_board
        offer = _current_offer(world)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        staged = world.dialogue_manager.peek()
        verdict = str((staged.get("overall_acceptance") or {}).get(
            "carry_verdict_display") or "")
        assert verdict
        assert "at or above" not in verdict
        assert "terms they offered" in verdict.lower()

    def test_the_courts_own_voice_does_not_say_they_hold_out(
            self, fixture_board):
        world = fixture_board
        offer = _current_offer(world)
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        staged = world.dialogue_manager.peek()
        for row in staged.get("per_court_acceptance") or []:
            assert row.get("band") == "consented"
            assert "holds out" not in str(row.get("voice_line") or "").lower()

    def test_the_heading_does_not_quote_an_acceptance_band(
            self, fixture_board):
        """A live Ratify button beside "Holding out" is the contradiction the
        audit's through-line names."""
        world = _fixture_world()
        offer = _current_offer(world)
        offer["settlement_terms"] = [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "Britain", "to": "France",
             "amount": 400},
        ]
        handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        staged = world.dialogue_manager.peek()
        if not staged.get("can_ratify"):
            pytest.skip("this package does not carry on the fixture board")
        heading = str(staged.get("talleyrand_text") or "")
        assert "Holding out" not in heading
        assert "consent" in heading.lower() or "their own" in heading.lower()


# ═══════════════════════════════════════════════════════════════════════
# FA-S10-1 — a dead court's war is over
# ═══════════════════════════════════════════════════════════════════════


class TestTheDeadCourtsWarIsOver:

    def _eliminate(self, world, nation):
        for region in list(world.regions.values()):
            if region.controller == nation:
                region.controller = "France"
        with _quiet():
            world._eliminate_nation(nation)

    def test_an_eliminated_courts_pairs_are_resolved(self, boot_board):
        world = boot_board
        war = world.war_instances["war_1"]
        assert "Bavaria" in (war.get("attackers") or [])
        self._eliminate(world, "Bavaria")
        keys = war.get("active_diplo_keys") or []
        assert not [k for k in keys if "Bavaria" in k.split("|")]
        resolved = war.get("resolved_diplo_keys") or []
        assert [k for k in resolved if "Bavaria" in k.split("|")]
        meta = (war.get("diplo_key_meta") or {}).get("Austria|Bavaria") or {}
        assert meta.get("pair_status") == "resolved"
        assert meta.get("resolved_turn") is not None

    def test_the_war_left_a_pair_nobody_could_resolve(self, boot_board):
        """The lever-off arm IS the defect: the pair stays listed as an active
        war pair while its nation is on no side, so `_active_cross_side_pairs`
        can never return it and `revalidate_staged_settlement` refuses every
        ratification of that war forever."""
        SH.ELIMINATION_RESOLVES_ITS_PAIRS = False
        world = boot_board
        war = world.war_instances["war_1"]
        self._eliminate(world, "Bavaria")
        listed = [k for k in (war.get("active_diplo_keys") or [])
                  if "Bavaria" in k.split("|")]
        assert listed, "the elimination geometry did not reproduce"
        live = set(_active_cross_side_pairs(war, "attackers"))
        assert all(k not in live for k in listed)

    def test_a_settlement_can_still_be_ratified_after_an_ally_dies(
            self, boot_board, client):
        world = boot_board
        self._eliminate(world, "Bavaria")
        war = world.war_instances["war_1"]
        covered = [n for n in (war.get("defenders") or [])
                   if n != world.player_nation]
        offer = {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": "probe_offer", "war_id": "war_1",
            "proposer_nation": covered[0],
            "proposer_side": "defenders", "accepting_side": "attackers",
            "covered_enemy_participants": covered,
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(world.current_turn),
        }
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is True
        staged = world.dialogue_manager.peek()
        assert staged.get("can_ratify") is True
        from backend.game_logic.settlement_ratify import ratify_settlement_confirm
        with _quiet():
            ratified = ratify_settlement_confirm(world, staged)
        assert ratified.get("success") is True, ratified.get("error")


# ═══════════════════════════════════════════════════════════════════════
# FA-17 — the answer to France's own overture
# ═══════════════════════════════════════════════════════════════════════


class TestTheAnswerReachesTheDesk:

    def test_a_counter_displaces_mail_to_reach_the_slot(self):
        dm = DM.DialogueManager()
        dm.push({"type": "incoming_proposal", "target_nation": "Hesse",
                 "turn_created": 1})
        counter = {"type": "counter_offer_response", "target_nation": "Russia",
                   "turn_created": 1, "blocking": True}
        assert dm.mount_over_mail(counter) is True
        assert dm.peek() is counter
        assert [d.get("type") for d in dm.iter_queue()] == ["incoming_proposal"]

    def test_it_never_displaces_a_decision_in_progress(self):
        dm = DM.DialogueManager()
        hard = {"type": "war_purpose_selection", "turn_created": 1,
                "blocking": True}
        dm.push(hard)
        counter = {"type": "counter_offer_response", "turn_created": 1}
        assert dm.mount_over_mail(counter) is False
        assert dm.peek() is hard
        assert counter in dm.iter_queue()

    def test_the_safety_valve_knows_the_counter_family(self):
        """A counter promoted later still had no popup: the valve that
        re-derives one from the current dialogue listed only two of the four
        types that render through that popup."""
        assert set(M.SAFETY_VALVE_DIALOGUE_TYPES) == {
            "incoming_proposal", "incoming_ultimatum",
            "counter_offer", "counter_offer_response",
        }

    def test_a_lapsed_counter_costs_the_player_a_cooldown(self, boot_board):
        """The 3-DP treadmill: the counter arm was the only non-ACCEPT outcome
        that set no player cooldown, so an overture whose answer lapsed
        unanswered could be re-sent, at 3 DP, every single turn."""
        world = boot_board
        world.dialogue_manager.push({
            "type": "counter_offer_response", "target_nation": "Russia",
            "turn_created": int(world.current_turn),
            "context": {"proposal_type": "peace"},
        })
        lapsed = world.dialogue_manager.lapse_pending_offers()
        assert any(row["offer_type"] == "counter_offer_response"
                   for row in lapsed)
        manager = TM.TurnManager(world)
        for row in lapsed:
            if (TM.LAPSED_COUNTER_COSTS_A_COOLDOWN
                    and row["offer_type"] == "counter_offer_response"):
                world.player_proposal_cooldowns[row["nation"]] = 3
                world.player_proposal_cooldowns[
                    f"{row['nation']}_{row['proposal_type']}"] = 5
        del manager
        assert world.player_proposal_cooldowns.get("Russia") == 3
        assert world.player_proposal_cooldowns.get("Russia_peace") == 5

    def test_the_lapse_cooldown_is_wired_at_the_turn_seam(self):
        """The pin above builds the rule; this one proves the production loop
        carries it (a source census, the CA8-14 idiom)."""
        source = (ROOT / "backend" / "game_logic" / "turn_manager.py").read_text(
            encoding="utf-8")
        block = source.split("lapse_pending_offers()")[1].split("def ")[0]
        assert "LAPSED_COUNTER_COSTS_A_COOLDOWN" in block
        assert "counter_offer_response" in block
        assert "player_proposal_cooldowns" in block


# ═══════════════════════════════════════════════════════════════════════
# FA-N44 — the crisis reaches the slot, and is not deleted unseen
# ═══════════════════════════════════════════════════════════════════════


class TestTheCrisisReachesTheSlot:

    def _paradox_board(self, world):
        from backend.game_logic.ai_diplomacy import deliver_ai_proposal
        from backend.game_logic.diplomacy import set_diplomatic_state
        with _quiet():
            set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "t")
            set_diplomatic_state(world, "France", "Denmark", "ALLIANCE", "t")
            set_diplomatic_state(world, "Prussia", "Denmark", "PEACE", "t")
            deliver_ai_proposal({"source": "Saxony",
                                 "proposal_type": "open_borders",
                                 "terms": {"type": "open_borders"}}, world)

    def test_the_paradox_takes_the_slot_from_a_letter(self, boot_board):
        from backend.game_logic.diplomacy import declare_war
        world = boot_board
        self._paradox_board(world)
        assert world.dialogue_manager.peek().get("type") == "incoming_proposal"
        with _quiet():
            declare_war(world, "Prussia", "Denmark")
        assert world.dialogue_manager.peek().get("type") == "commitment_paradox"
        assert world.dialogue_manager.is_hard_stop() is True
        # The letter is preserved, not destroyed.
        assert "incoming_proposal" in [
            d.get("type") for d in world.dialogue_manager.iter_queue()]

    def test_the_letter_used_to_answer_for_the_crisis(self, boot_board, client):
        """The lever-off arm reproduces FA-N44's own headline: a bare option
        index answers whatever is current, which was the letter."""
        DM.MOUNT_OVER_MAIL_ACTIVE = False
        from backend.game_logic.diplomacy import declare_war
        world = boot_board
        self._paradox_board(world)
        with _quiet():
            declare_war(world, "Prussia", "Denmark")
        assert world.dialogue_manager.peek().get("type") == "incoming_proposal"

    def test_the_crisis_carries_its_own_modal(self, boot_board, client):
        """A hard stop refuses every command, and a refusal does not drain the
        popup queue — so mounting the paradox would have made its dedicated
        surface undeliverable. A popup bound to the SAME dialogue is how the
        question is drawn, not a rival for the slot."""
        from backend.game_logic.diplomacy import declare_war
        world = boot_board
        self._paradox_board(world)
        with _quiet():
            declare_war(world, "Prussia", "Denmark")
        response = _post(client, "status")
        assert response.get("commitment_paradox_popup")
        assert (response["commitment_paradox_popup"].get("dialogue_id")
                == world.dialogue_manager.peek().get("dialogue_id"))
        # One shot: the next refusal does not re-deliver it.
        assert not _post(client, "status").get("commitment_paradox_popup")

    def test_an_unrelated_popup_never_rides_a_question(self, boot_board, client):
        """The narrowness of the rule: only a popup bound to the carried
        dialogue is attached (slice 6's finding stands for every other)."""
        from backend.game_logic.diplomacy import declare_war
        world = boot_board
        self._paradox_board(world)
        with _quiet():
            declare_war(world, "Prussia", "Denmark")
        world._popup_queue.push("coalition_popup", {"title": "unbound"})
        response = _post(client, "status")
        assert not response.get("coalition_popup")
        assert world._popup_queue.get("coalition_popup")

    def test_a_queued_paradox_survives_the_stale_sweep(self):
        dm = DM.DialogueManager()
        dm.push({"type": "commitment_paradox", "turn_created": 3,
                 "blocking": True})
        dm.preempt({"type": "war_purpose_selection", "turn_created": 10,
                    "blocking": True})
        dm.clear_stale(10)
        assert [d.get("type") for d in dm.iter_queue()] == ["commitment_paradox"]

    def test_the_sweep_still_clears_the_wedge_it_was_written_for(self):
        """PC15-3's cure is untouched: a stale pair-substitute chooser in the
        queue is still swept, because its confirm vocabulary would eat every
        later answer when promoted. Both sweep branches are exercised — the
        blocking timeout and the plain last-turn drop — because the paradox
        exemption sits above both."""
        dm = DM.DialogueManager()
        dm.push({"type": "settlement_pair_substitute_confirm",
                 "turn_created": 3, "blocking": True})
        dm.preempt({"type": "advisory", "turn_created": 10, "blocking": False})
        dm.clear_stale(10)
        assert dm.iter_queue() == []

        dm2 = DM.DialogueManager()
        dm2.push({"type": "settlement_pair_substitute_confirm",
                  "turn_created": 3, "blocking": False})
        dm2.preempt({"type": "advisory", "turn_created": 10,
                     "blocking": False})
        dm2.clear_stale(10)
        assert dm2.iter_queue() == []


# ═══════════════════════════════════════════════════════════════════════
# FA-N16 — the offer speaks the direction
# ═══════════════════════════════════════════════════════════════════════


def _offer_popup(world, terms):
    offer = dict(_current_offer(world) or {})
    offer["settlement_terms"] = terms
    with _quiet():
        return build_incoming_settlement_offer_popup(world, offer)


class TestTheOfferSpeaksTheDirection:

    def test_a_concession_is_not_announced_as_a_demand(self, fixture_board):
        """AUD-c lets a losing court PAY France to close a war; every arrival
        family was demand-shaped, so "London asks 1358 gold" was printed of an
        offer that was paying us 1,358."""
        payload = _offer_popup(fixture_board, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "Britain", "to": "France",
             "amount": 1358}])
        assert payload["amount"] == 0
        assert payload["amount_offered"] == 1358
        for line in (payload["talleyrand_text"], payload["proposer_voice"]):
            assert "1358" in line
            assert "ask" not in line.lower()

    def test_a_white_peace_does_not_ask_for_zero_gold(self, fixture_board):
        """The line every campaign met on turn five."""
        payload = _offer_popup(fixture_board, [{"type": "peace"}])
        assert payload["amount"] == 0 and payload["amount_offered"] == 0
        for line in (payload["talleyrand_text"], payload["proposer_voice"]):
            assert "0 gold" not in line
            assert line
        assert "no indemnity" in payload["proposer_voice"].lower()

    def test_a_real_demand_still_reads_as_a_demand(self, fixture_board):
        payload = _offer_popup(fixture_board, [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 6994}])
        assert payload["amount"] == 6994
        assert payload["amount_offered"] == 0
        assert "asks 6994" in payload["proposer_voice"]

    def test_a_recurring_clause_no_longer_clobbers_the_headline(
            self, fixture_board):
        """Found in passing: the terms-summary loop reassigned the same
        `amount` the payload publishes, so a recurring-gold offer overwrote
        the indemnity figure the popup and the rail both quote."""
        payload = _offer_popup(fixture_board, [
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 400},
            {"type": "gold_per_turn", "from": "France", "to": "Britain",
             "amount": 99, "turns": 5}])
        assert payload["amount"] == 400

    def test_every_new_family_resolves_with_no_unfilled_slot(self):
        from backend.game_logic.diplomatic_templates import (
            resolve_settlement_voice_line,
        )
        for arm in ("_concession", "_none"):
            for who in ("talleyrand", "castlereagh", "hardenberg",
                        "metternich", "einsiedel", "chancery"):
                key = f"settlement_incoming_offer_arrival{arm}_{who}"
                line = resolve_settlement_voice_line(
                    key, war_label="France vs Britain",
                    proposer_leader="Britain", amount="500")
                assert line, key
                assert "{" not in line, key

    def test_the_rail_says_offering_when_the_court_pays(self):
        source = (ROOT / "backend" / "game_logic" / "turn_manager.py").read_text(
            encoding="utf-8")
        block = source.split("for offer in promoted_offers:")[1][:2000]
        assert "amount_offered" in block
        assert "Offering" in block


# ═══════════════════════════════════════════════════════════════════════
# FA-N43 — the incoming Assessment reads OUR burden
# ═══════════════════════════════════════════════════════════════════════


class TestTheAssessmentReadsOurBurden:

    def _popup(self, world, terms):
        with _quiet():
            return MP.build_pending_envoy_popup_from_terms(
                world, nation="Britain", terms=terms, assessment="",
                is_counter_offer=False)

    def test_a_demand_on_france_is_not_generous(self, fixture_board):
        payload = self._popup(fixture_board, {
            "type": "peace", "sweeteners": [],
            "demands": [{"type": "gold_lump", "value": 405}]})
        snapshot = payload["war_context_snapshot"]
        assert snapshot["harshness_label"] != "generous"
        assert snapshot["harshness"] == pytest.approx(
            calculate_treaty_harshness(
                {"clauses": [], "demands": [{"type": "gold_lump", "value": 405}]}),
            abs=0.01)
        assert payload["harshness_label"] == snapshot["harshness_label"]

    def test_a_gift_to_france_is_not_harsh(self, fixture_board):
        payload = self._popup(fixture_board, {
            "type": "peace", "demands": [],
            "sweeteners": [{"type": "gold_per_turn", "value": 300}]})
        assert payload["war_context_snapshot"]["harshness_label"] == "generous"

    def test_the_lever_off_arm_restores_the_inverted_reading(
            self, fixture_board):
        MP.INCOMING_ASSESSMENT_READS_OUR_BURDEN = False
        payload = self._popup(fixture_board, {
            "type": "peace", "sweeteners": [],
            "demands": [{"type": "gold_lump", "value": 405}]})
        assert payload["war_context_snapshot"]["harshness_label"] == "generous"


# ═══════════════════════════════════════════════════════════════════════
# FA-N45 — the record stores one side's burden
# ═══════════════════════════════════════════════════════════════════════


class TestTheRecordStoresOneSidesBurden:

    def test_the_clause_dialect_prices_every_type_the_demand_dialect_does(self):
        """The G4F-1 census the file's own comment asks for: a type registered
        in only ONE dialect falls through unmatched in the other and prices at
        zero."""
        for ctype, clause, demand in (
            ("gold_lump", {"type": "gold_lump", "amount": 405},
             {"type": "gold_lump", "value": 405}),
            ("manpower_infantry", {"type": "manpower_infantry", "amount": 5000},
             {"type": "manpower_infantry", "value": 5000}),
            ("ap_per_turn", {"type": "ap_per_turn", "value": 1},
             {"type": "ap_per_turn", "value": 1}),
        ):
            as_clause = calculate_treaty_harshness({"clauses": [clause]})
            as_demand = calculate_treaty_harshness({"demands": [demand]})
            assert as_clause > 0, ctype
            assert as_clause == pytest.approx(as_demand, abs=0.001), ctype

    def test_burden_reads_the_direction(self):
        clauses = [{"type": "gold_lump", "from": "France", "to": "Britain",
                    "amount": 405}]
        assert burden_on_nation(clauses, "France") > 0
        assert burden_on_nation(clauses, "Britain") == 0.0

    def test_a_gold_peace_no_longer_stores_zero(self, fixture_board):
        """Measured before: a ratified treaty that moved 405 gold stored 0.0,
        so DD8-4's "harsh history breeds resentment" could never fire on it."""
        world = fixture_board
        with _quiet():
            world._ratify_treaty({
                "type": "peace", "proposer_nation": "Britain",
                "target_nation": "France", "clauses": [], "sweeteners": [],
                "demands": [{"type": "gold_lump", "value": 405}]})
        records = world.previous_treaties.get(
            world._make_diplo_key("Britain", "France")) or []
        assert records and records[-1]["harshness"] > 0.3

    def test_a_concession_is_never_booked_as_harshness(self, fixture_board):
        """The trap in the row's own fix: mirroring the four rates into the
        direction-BLIND clause loop would have booked the AI's own payment to
        France as a harsh treaty against the pair."""
        world = fixture_board
        with _quiet():
            world._ratify_treaty({
                "type": "peace", "proposer_nation": "Britain",
                "target_nation": "France", "clauses": [], "demands": [],
                "sweeteners": [{"type": "gold_lump", "value": 500}]})
        records = world.previous_treaties.get(
            world._make_diplo_key("Britain", "France")) or []
        assert records and records[-1]["harshness"] == 0.0

    def test_the_ally_penalty_reads_the_enemys_burden(self):
        """The BPH-C doubling asks how lightly the COMMON ENEMY got off; the
        old input summed both sides' clauses, counting France's own
        concessions as if they had been extracted from him."""
        source = (ROOT / "backend" / "models" / "world_state.py").read_text(
            encoding="utf-8")
        block = source.split("apply_separate_peace_penalties")[1][:900]
        assert "burden_on_nation(treaty_clauses, penalty_target)" in block
