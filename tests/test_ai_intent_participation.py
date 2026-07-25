"""AI-2d (Stage C half) — the participation surface (§4.2b, §12.6).

Sell-neutrality and the sponsor arms ship with AI-2 (their tests live
in test_ai_intent_peacetime.py / test_ai_intent_counterplay.py — the
one-row tracking rule keeps this file pointing at the same row). This
file owns the ALLEGIANCE AUCTION: a minor's flip announced as in play,
biddable through the D5 instruments, resolved by lean + standing offer.
Join / broker arms are Stage D (the landing split, §4.2b).
"""

from pathlib import Path

import pytest

from backend.game_logic.ai_diplomacy import (
    ALLEGIANCE_AUCTION_WINDOW,
    process_allegiance_auctions,
)
from backend.game_logic.instruments import grant_directed_sponsorship
from backend.game_logic.intent import IntentView
from backend.models.world_state import WorldState

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client"
                 / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_dict(
        WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _crest(monkeypatch, nations):
    """Monkeypatch the intent chokepoint: the named minors crest at
    `bandwagon`; everyone else reads indifferent."""

    def fake(nation, w):
        if nation in nations:
            return IntentView(nation=nation, want_id="test_design",
                              want_title="Test", want_type="acquire_regions",
                              against="Austria", weight=66,
                              price="bandwagon")
        return IntentView(nation=nation, want_id=None, want_title=None,
                          want_type=None, against=None, weight=0,
                          price="indifferent")

    monkeypatch.setattr("backend.game_logic.intent.get_nation_intent", fake)


class TestAuctionOpens:
    def test_crest_announces_the_flip(self, world, monkeypatch):
        _crest(monkeypatch, {"Denmark"})
        events = process_allegiance_auctions(world)
        opened = [e for e in events
                  if e["type"] == "allegiance_auction_opened"]
        assert len(opened) == 1
        assert opened[0]["nation"] == "Denmark"
        record = world.allegiance_auctions["Denmark"]
        assert (record["resolves_turn"] - record["opened_turn"]
                == ALLEGIANCE_AUCTION_WINDOW)

    def test_announced_once_not_every_turn(self, world, monkeypatch):
        _crest(monkeypatch, {"Denmark"})
        process_allegiance_auctions(world)
        again = process_allegiance_auctions(world)
        assert not [e for e in again
                    if e["type"] == "allegiance_auction_opened"]

    def test_majors_never_auction(self, world, monkeypatch):
        _crest(monkeypatch, {"Austria", "Russia"})
        events = process_allegiance_auctions(world)
        assert events == []

    def test_boot_world_is_dormant(self, world):
        """No minor crests at bandwagon on the 1805 boot (real intent)."""
        assert process_allegiance_auctions(world) == []
        assert world.allegiance_auctions == {}


class TestAuctionResolves:
    def _open_and_ripen(self, world, monkeypatch, nation="Denmark"):
        _crest(monkeypatch, {nation})
        process_allegiance_auctions(world)
        world.current_turn += ALLEGIANCE_AUCTION_WINDOW
        return nation

    def test_sponsorship_outbids_bare_relations(self, world, monkeypatch):
        """The D5 bid decides the flip: Britain's standing patronage
        beats a mild relation lean."""
        nation = self._open_and_ripen(world, monkeypatch)
        # Make Britain a ranked suitor with a heavy standing bid.
        monkeypatch.setattr(
            "backend.game_logic.coalition.identify_ranked_bloc_shares",
            lambda w: [("Britain", 0.3), ("Austria", 0.2)])
        # Britain's raw lean trails France's; the patronage decides —
        # and the winner's relation clears the pact's ratify gate
        # (the review's honest-flip fix: no announced flip without a
        # real treaty).
        world.nation_relations[world._make_diplo_key(nation, "Britain")] = 30
        world.nation_relations[world._make_diplo_key(nation, "France")] = 35
        grant_directed_sponsorship(
            world, payer="Britain", recipient=nation, aim="Austria",
            amount_per_turn=200)
        events = process_allegiance_auctions(world)
        resolved = [e for e in events
                    if e["type"] == "allegiance_auction_resolved"]
        assert resolved and resolved[0]["winner"] == "Britain"
        assert resolved[0]["outcome"] == "flipped"
        assert world.get_diplomatic_state(nation, "Britain") == (
            "DEFENSIVE_ALLIANCE")
        assert nation not in world.allegiance_auctions

    def test_player_winner_gets_an_offer_not_an_imposition(
            self, world, monkeypatch):
        nation = self._open_and_ripen(world, monkeypatch)
        monkeypatch.setattr(
            "backend.game_logic.coalition.identify_ranked_bloc_shares",
            lambda w: [("France", 0.4)])
        world.nation_relations[world._make_diplo_key(nation, "France")] = 40
        events = process_allegiance_auctions(world)
        resolved = [e for e in events
                    if e["type"] == "allegiance_auction_resolved"]
        assert resolved and resolved[0]["winner"] == "France"
        assert resolved[0]["outcome"] == "player_offer"
        # The pact arrives through the mailbox — the player may refuse.
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "incoming_proposal"
        assert world.get_diplomatic_state(nation, "France") != (
            "DEFENSIVE_ALLIANCE")

    def test_passed_crest_lapses_the_auction(self, world, monkeypatch):
        nation = self._open_and_ripen(world, monkeypatch)
        # The want cools before resolution (§3.1a — a reading, never a
        # latch): the auction lapses instead of forcing a flip.
        monkeypatch.setattr(
            "backend.game_logic.intent.get_nation_intent",
            lambda n, w: IntentView(nation=n, want_id=None,
                                    want_title=None, want_type=None,
                                    against=None, weight=0,
                                    price="indifferent"))
        events = process_allegiance_auctions(world)
        resolved = [e for e in events
                    if e["type"] == "allegiance_auction_resolved"]
        assert resolved and resolved[0]["outcome"] == "lapsed"
        assert resolved[0]["winner"] is None
        assert nation not in world.allegiance_auctions

    def test_window_holds_before_resolution(self, world, monkeypatch):
        _crest(monkeypatch, {"Denmark"})
        process_allegiance_auctions(world)
        events = process_allegiance_auctions(world)  # same turn — early
        assert not [e for e in events
                    if e["type"] == "allegiance_auction_resolved"]
        assert "Denmark" in world.allegiance_auctions


class TestAuctionPlumbing:
    def test_open_auction_survives_a_save(self, world, monkeypatch):
        _crest(monkeypatch, {"Denmark"})
        process_allegiance_auctions(world)
        restored = WorldState.from_dict(world.to_dict())
        assert restored.allegiance_auctions == world.allegiance_auctions

    def test_pre_stage_c_save_reads_empty(self, world):
        data = world.to_dict()
        data.pop("allegiance_auctions")
        restored = WorldState.from_dict(data)
        assert restored.allegiance_auctions == {}

    def test_deckless_world_never_auctions(self):
        bare = WorldState(player_nation="France")
        assert process_allegiance_auctions(bare) == []

    def test_events_reach_the_campaign_log(self, world, monkeypatch):
        from backend.campaign_log import filter_campaign_log
        _crest(monkeypatch, {"Denmark"})
        process_allegiance_auctions(world)
        visible = filter_campaign_log(world.event_log, world)
        assert any(e.get("type") == "allegiance_auction_opened"
                   for e in visible)
