"""AI-5c — The Arbiter's Offer (docs/AI_INTENT_SPEC.md §12.5, §11.1
Stage E; landing record §18).

Armed mediation: a NON-BELLIGERENT major with a live contain/arbiter
design offers to mediate a French war above an exhaustion floor. The
brokered terms ride the EXISTING incoming-settlement machinery — the
offer is an `incoming_settlement_offer` with mediator provenance, so
accept/decline/revise run identical plumbing. Accept opens the same
settlement review, credited (relations); refusal is a DERIVED
consequence only: the pin-8 refusal record, which the mediator's own
intent weight reads until the record's memory window closes — refusing
mediation IS the ramp toward the next coalition, by machinery (Prague
1813). No new threat namespace, no auto-join, no new dtype.

On the shipped 1805 board every contain-class court boots as a
belligerent, so mediation is structurally dormant at boot — pinned.
"""

from pathlib import Path

import pytest

from backend.game_logic.ai_diplomacy import (
    MEDIATION_COOLDOWN_TURNS,
    MEDIATION_CREDIT_RELATIONS,
    MEDIATION_REFUSED_RELATIONS,
    MEDIATION_WE_FLOOR,
    get_refused_asks,
    process_mediation_offers,
)
from backend.game_logic.intent import (
    WEIGHT_MEDIATION_REBUFFED,
    get_nation_intent,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _free_the_arbiter(world, mediator="Russia"):
    """Surgically retire the mediator from the boot coalition war: every
    diplomatic pair to PEACE, and an exit stamped on the boot instance
    (a war participant may not mediate its own war)."""
    turn = int(world.current_turn)
    for other in list(world.get_active_nations()):
        if other == mediator:
            continue
        key = world._make_diplo_key(mediator, other)
        if world.diplomatic_states.get(key) in ("WAR", "ARMISTICE"):
            world.diplomatic_states[key] = "PEACE"
    for war in world.war_instances.values():
        if not isinstance(war, dict):
            continue
        side_by = war.get("side_by_nation") or {}
        if mediator in side_by:
            side_by.pop(mediator, None)
        active = war.get("active_participants") or []
        if mediator in active:
            active.remove(mediator)
        meta = war.get("participant_meta") or {}
        if mediator in meta and not meta[mediator].get("exited_turn"):
            meta[mediator]["exited_turn"] = turn
    world.invalidate_bloc_members_cache()


def _weary_boot_war(world):
    """Age the boot coalition war past the offer floor and make France
    weary enough to invite good offices."""
    for war in world.war_instances.values():
        if isinstance(war, dict) and war.get("ended_turn") is None:
            war["created_turn"] = int(world.current_turn) - 4
    world.war_exhaustion[world.player_nation] = MEDIATION_WE_FLOOR + 20


class TestProducer:
    def test_boot_board_is_structurally_dormant(self, world):
        """Every contain-class 1805 court boots as a belligerent — no
        arbiter exists to speak, by authored design."""
        _weary_boot_war(world)
        assert process_mediation_offers(world) == []

    def test_the_arbiter_offers_over_a_weary_war(self, world):
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        produced = process_mediation_offers(world)
        assert len(produced) == 1
        offer = produced[0]
        assert offer["type"] == "incoming_settlement_offer"
        assert offer["mediator"] == "Russia"
        assert offer["mediator_interest"] == "Arbiter of Europe"
        assert offer in world.pending_settlement_dialogues
        assert world.ai_proposal_cooldowns.get(
            "Russia|mediation") == MEDIATION_COOLDOWN_TURNS

    def test_exhaustion_floor_gates(self, world):
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        world.war_exhaustion[world.player_nation] = MEDIATION_WE_FLOOR - 20
        assert process_mediation_offers(world) == []

    def test_mediator_cooldown_blocks_the_next_season(self, world):
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        produced = process_mediation_offers(world)
        assert produced
        # Clear the pending offer and the per-war producer clock — only
        # the MEDIATOR's own cooldown remains, and it holds.
        world.pending_settlement_dialogues = []
        world.ai_settlement_cooldowns = {}
        assert process_mediation_offers(world) == []

    def test_a_belligerent_arbiter_never_speaks(self, world):
        """An armistice is a paused war, not neutrality — the agendas
        doctrine applies to good offices too."""
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        key = world._make_diplo_key("Russia", "Ottoman")
        world.diplomatic_states[key] = "ARMISTICE"
        world.invalidate_bloc_members_cache()
        assert process_mediation_offers(world) == []

    def test_bare_world_is_inert(self):
        bare = WorldState()
        assert process_mediation_offers(bare) == []


class TestCourierSurface:
    def test_popup_names_the_arbiter_and_its_interest(self, world):
        """§12.5's Courier contract: the mediator's interest is NAMED on
        the offer surface, and Talleyrand says what scorning costs."""
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        offer = process_mediation_offers(world)[0]
        popup = build_incoming_settlement_offer_popup(world, offer)
        assert popup["mediator"] == "Russia"
        assert "good offices" in popup["proposer_voice"]
        assert "Russia" in popup["proposer_voice"]
        assert "Arbiter of Europe" in popup["proposer_voice"]
        assert "arbiter scorned" in popup["talleyrand_text"]

    def test_unmediated_offers_carry_no_arbiter_keys(self, world):
        """The standard producer's offers are byte-shaped as before —
        the mediation fields exist only under a mediator."""
        from backend.game_logic.ai_diplomacy import (
            process_settlement_offer_phase,
        )
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )
        _weary_boot_war(world)
        produced = process_settlement_offer_phase(world)
        assert produced
        offer = produced[0]
        assert "mediator" not in offer
        popup = build_incoming_settlement_offer_popup(world, offer)
        assert "mediator" not in popup


class TestResolution:
    def _produce(self, world):
        _free_the_arbiter(world, "Russia")
        _weary_boot_war(world)
        offers = process_mediation_offers(world)
        assert offers
        return offers[0]

    def test_reject_scorns_the_arbiter(self, world):
        """Refusal is derived-only: the pin-8 refusal record plus a
        relations chill — no threat write anywhere."""
        from backend.game_logic.settlement_offers import (
            handle_incoming_settlement_offer_action,
        )
        offer = self._produce(world)
        key = world._make_diplo_key("France", "Russia")
        relation_before = int(world.nation_relations.get(key, 0) or 0)
        threat_before = int(world.threat_level)
        result = handle_incoming_settlement_offer_action(
            world, action="reject_settlement_offer", dialogue=offer)
        assert result["success"] is True
        asks = get_refused_asks(world, "Russia", "France")
        assert any(e.get("type") == "mediation" for e in asks)
        assert int(world.nation_relations.get(key, 0) or 0) == (
            relation_before + MEDIATION_REFUSED_RELATIONS)
        assert int(world.threat_level) == threat_before

    def test_refusal_hardens_the_arbiter_then_expires(self, world):
        """The §12.5 elegance clause as a test: the refusal feeds the
        mediator's own ladder through a derived weight term, and it
        EXPIRES with the record's memory window — no latch."""
        from backend.game_logic.settlement_offers import (
            handle_incoming_settlement_offer_action,
        )
        offer = self._produce(world)
        world.invalidate_bloc_members_cache()
        view = get_nation_intent("Russia", world)
        assert view.want_id == "arbiter_of_europe"
        assert view.against == "France"
        weight_before = view.weight
        handle_incoming_settlement_offer_action(
            world, action="reject_settlement_offer", dialogue=offer)
        world.invalidate_bloc_members_cache()
        weight_after = get_nation_intent("Russia", world).weight
        assert weight_after - weight_before == WEIGHT_MEDIATION_REBUFFED
        # The record's window closes; the grudge cools by itself.
        world.current_turn = int(world.current_turn) + 13
        world.invalidate_bloc_members_cache()
        cooled = get_nation_intent("Russia", world).weight
        assert cooled == weight_before + _jitter_drift(world, cooled,
                                                       weight_before)

    def test_accept_opens_the_review_and_credits_the_mediator(self, world):
        from backend.game_logic.settlement_offers import (
            handle_incoming_settlement_offer_action,
        )
        offer = self._produce(world)
        key = world._make_diplo_key("France", "Russia")
        relation_before = int(world.nation_relations.get(key, 0) or 0)
        result = handle_incoming_settlement_offer_action(
            world, action="accept_settlement_offer", dialogue=offer)
        assert result.get("success") is True
        assert result.get("dialogue_type") == "settlement_confirm"
        assert result.get("mediator") == "Russia"
        assert int(world.nation_relations.get(key, 0) or 0) == (
            relation_before + MEDIATION_CREDIT_RELATIONS)

    def test_a_lapsed_offer_writes_no_refusal(self, world):
        """Ignoring the courier is not scorning him (the NA-5 lapse
        doctrine) — only an answered rejection writes the record."""
        self._produce(world)
        assert get_refused_asks(world, "Russia", "France") == []


def _jitter_drift(world, cooled, before):
    """The historical seed pins jitter to 0, so cooling lands exactly on
    the pre-refusal weight; the helper exists to make the equality's
    meaning explicit rather than magic."""
    return 0
