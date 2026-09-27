"""PC15-10 B1 — "The Antechamber" (`docs/PETITION_POPUP_REVISIT_SPEC.md` §4 F1,
§6 Q1(a)/Q2(a) RULED; Score Mandate Chunk 4, taken with SR-4c, Sept 26 2026).

Routine audiences stop being interrupts. Every petition carries a TIER set by
its builder from the ruled table — AUDIENCE = {jealousy confrontation L0/L1,
rivalry @−1, the shadow petition}; CRISIS = {L2, L3, rivalry @−2,
Fontainebleau, war-weary} (a legacy card with no tier is CRISIS). A crisis
card keeps today's road (the slot + the PopupQueue + the modal); an audience
card takes the slot WITHOUT the queue, is announced on the rail (a
JEALOUSY_CONFRONTATION / RIVALRY_CONFRONTATION row whose button opens it), on
the Generals card, in the dispatch, and is served on demand by
`GET /marshal_petition` to the SAME dialog and the SAME answer endpoint. A
crisis arriving while an audience holds the slot evicts it and un-stamps its
latch, so the audience returns on the pair's next fire.

Lever `jealousy.THE_ANTECHAMBER` — False = every card is CRISIS (the modal
channel as it was).
"""

import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import notifications as N
from backend.game_logic import jealousy as J
from tests import _chip_census as C


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    w = M.world
    w.authority_tracker.authority = 50
    w.pending_marshal_petition = None
    return w


def _queue_has_petition(world):
    return world._popup_queue.get("pending_marshal_petition") is not None


def _rail(world, ntype):
    return [n for n in world.notifications.get_pending() if n.get("type") == ntype]


def _fire(world, who, whom, delta=2, threshold=2):
    events = []
    J.apply_jealousy(world, world.marshals[who], world.marshals[whom],
                     delta=delta, threshold=threshold, events=events)
    return events


# ═══════════════════════════ THE TIER TABLE (Q1(a)) ════════════════════════

class TestTheTierTable:
    @pytest.mark.parametrize("kind,context,tier", [
        ("jealousy_confrontation", {"escalation_level": 0}, "audience"),
        ("jealousy_confrontation", {"escalation_level": 1}, "audience"),
        ("jealousy_confrontation", {"escalation_level": 2}, "crisis"),
        ("jealousy_confrontation", {"escalation_level": 3}, "crisis"),
        ("rivalry_confrontation", {"new_value": -1}, "audience"),
        ("rivalry_confrontation", {"new_value": -2}, "crisis"),
        ("fontainebleau", {}, "crisis"),
        ("war_weary", {}, "crisis"),
        ("shadow_command", {}, "audience"),
        ("something_new", {}, "crisis"),
    ])
    def test_the_ruled_table(self, kind, context, tier):
        assert J.petition_tier_for(kind, context) == tier

    def test_a_legacy_card_without_a_tier_is_a_crisis(self):
        assert J.petition_tier({"kind": "jealousy_confrontation"}) == "crisis"

    def test_lever_down_every_card_is_a_crisis(self, monkeypatch):
        monkeypatch.setattr(J, "THE_ANTECHAMBER", False)
        assert J.petition_tier({"kind": "jealousy_confrontation",
                                "tier": "audience"}) == "crisis"


# ═══════════════════════════ THE AUDIENCE ROAD ═════════════════════════════

class TestAnAudienceWaitsInTheAntechamber:
    def test_an_audience_takes_the_slot_but_not_the_queue(self, world):
        events = _fire(world, "Massena", "Davout")
        petition = world.pending_marshal_petition
        assert petition is not None and petition["tier"] == "audience"
        assert not _queue_has_petition(world), "an audience is never a modal"
        rows = _rail(world, N.JEALOUSY_CONFRONTATION)
        assert rows, "the rail announces it"
        details = rows[-1]["details"]
        assert details["marshal"] == "Massena"
        assert details["review_target"] == "marshal_petition"
        assert any(e.get("type") == "marshal_audience" for e in
                   J._pending_events(world) + events)

    def test_the_command_response_carries_no_modal(self, world):
        _fire(world, "Massena", "Davout")
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/command", json={"command": "status"}).json()
        assert r.get("marshal_petition") is None
        audience = r.get("marshal_audience")
        assert audience and audience["marshal"] == "Massena", audience

    def test_the_end_turn_response_defers_no_audience(self, world):
        _fire(world, "Massena", "Davout")
        client = TestClient(M.app)
        with _quiet():
            r = client.post("/command", json={"command": "end turn"}).json()
        deferred = r.get("deferred_marshal_petition")
        assert not deferred or deferred.get("tier") != "audience", deferred

    def test_get_serves_the_card_and_the_same_endpoint_answers_it(self, world):
        _fire(world, "Massena", "Davout")
        client = TestClient(M.app)
        with _quiet():
            got = client.get("/marshal_petition").json()
        card = got.get("petition")
        assert card and card["kind"] == "jealousy_confrontation"
        assert {o["id"] for o in card["options"]} >= {"acknowledge", "rebuke"}
        with _quiet():
            answered = client.post("/marshal_petition_response",
                                   json={"choice": "acknowledge"}).json()
        assert answered.get("success"), answered.get("message")
        assert world.pending_marshal_petition is None
        assert not _rail(world, N.JEALOUSY_CONFRONTATION), "the rail row leaves with the card"
        with _quiet():
            after = client.get("/marshal_petition").json()
        assert after.get("petition") is None

    def test_the_turn_pass_never_queues_a_standing_audience(self, world):
        _fire(world, "Massena", "Davout")
        world._jealousy_processed_turn = None
        with _quiet():
            J.process_turn(world)
        assert world.pending_marshal_petition is not None
        assert not _queue_has_petition(world)

    def test_a_stale_audience_is_retired_by_the_turn_pass_and_says_so(self, world):
        _fire(world, "Massena", "Davout")
        J.clear_jealousy(world, world.marshals["Massena"], resolved_by_action=False)
        world._jealousy_processed_turn = None
        with _quiet():
            events = J.process_turn(world)
        assert world.pending_marshal_petition is None
        assert not _rail(world, N.JEALOUSY_CONFRONTATION)
        lines = [e["message"] for e in events
                 if e.get("type") == "marshal_audience" and e.get("retired")]
        assert lines and "no longer presses the matter" in lines[-1], lines

    def test_get_retires_a_stale_card_and_says_so(self, world):
        _fire(world, "Massena", "Davout")
        J.clear_jealousy(world, world.marshals["Massena"], resolved_by_action=False)
        client = TestClient(M.app)
        with _quiet():
            got = client.get("/marshal_petition").json()
        assert got.get("petition") is None
        assert "no longer presses the matter" in got.get("message", "")
        assert world.pending_marshal_petition is None

    def test_the_rail_row_opens_the_card(self):
        """Source join: the rail's review target is routed to the opener."""
        from pathlib import Path
        src = (Path(__file__).resolve().parents[1] / "godot-client"
               / "project-sovereign" / "scripts" / "main.gd").read_text(encoding="utf-8")
        at = src.index('if review_target == "marshal_petition":')
        assert "_open_marshal_audience()" in src[at:at + 120]
        assert "api_client.get_marshal_petition(" in src

    def test_the_generals_card_carries_the_chip(self, world):
        _fire(world, "Massena", "Davout")
        fields = J.build_glory_card_fields(world.marshals["Massena"], world)
        assert fields.get("seeks_audience") is True
        other = J.build_glory_card_fields(world.marshals["Davout"], world)
        assert not other.get("seeks_audience")


# ═══════════════════════════ THE CRISIS ROAD ═══════════════════════════════

class TestACrisisIsStillAModal:
    def test_the_damage_going_permanent_is_a_modal(self, world):
        J._set_escalation_level(world.marshals["Massena"], "Davout",
                                J.ESCALATION_PERMANENT_LEVEL)
        _fire(world, "Massena", "Davout")
        petition = world.pending_marshal_petition
        assert petition["tier"] == "crisis"
        assert _queue_has_petition(world)
        assert not _rail(world, N.JEALOUSY_CONFRONTATION)

    def test_a_crisis_evicts_an_audience_and_unstamps_its_latch(self, world):
        _fire(world, "Massena", "Davout")
        audience = world.pending_marshal_petition
        pair = J._pair_key("Massena", "Davout")
        assert f"{pair}@L0" in (world.jealousy_confrontations_seen or [])
        J._set_escalation_level(world.marshals["Lannes"], "Soult",
                                J.ESCALATION_PERMANENT_LEVEL)
        _fire(world, "Lannes", "Soult")
        crisis = world.pending_marshal_petition
        assert crisis is not audience and crisis["tier"] == "crisis"
        assert _queue_has_petition(world)
        assert f"{pair}@L0" not in (world.jealousy_confrontations_seen or []), \
            "the evicted audience must return on the pair's next fire"
        assert J.last_audience_turn(world.marshals["Massena"]) < 0, \
            "an evicted audience was never heard"
        assert not _rail(world, N.JEALOUSY_CONFRONTATION)

    def test_the_eviction_says_so(self, world):
        _fire(world, "Massena", "Davout")
        J._set_escalation_level(world.marshals["Lannes"], "Soult",
                                J.ESCALATION_PERMANENT_LEVEL)
        _fire(world, "Lannes", "Soult")
        lines = [e["message"] for e in J._pending_events(world)
                 if e.get("type") == "marshal_audience" and e.get("evicted")]
        assert lines and "Massena" in lines[-1] and "ask again" in lines[-1], lines

    def test_a_breach_evicts_harsh_words_and_their_key_survives_the_write(self, world):
        """The same-store clobber the first cut shipped: a rivalry crisis
        (@−2) evicting a rivalry audience (@−1) of ANOTHER pair — the
        producer's own snapshot must not write the evicted key back."""
        massena = world.marshals["Massena"]
        massena.set_relationship("Ney", -1)
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": -1}])
        audience = world.pending_marshal_petition
        assert audience and audience["tier"] == "audience"
        audience_key = f"{J._pair_key('Massena', 'Ney')}@-1"
        assert audience_key in world.rivalry_transitions_seen
        lannes = world.marshals["Lannes"]
        lannes.set_relationship("Davout", -2)
        J.check_rivalry_transitions(world, [{
            "marshal": "Lannes", "toward": "Davout", "change": -1}])
        crisis = world.pending_marshal_petition
        assert crisis is not audience and crisis["tier"] == "crisis"
        assert audience_key not in world.rivalry_transitions_seen
        assert f"{J._pair_key('Lannes', 'Davout')}@-2" in world.rivalry_transitions_seen

    def test_an_audience_does_not_evict_a_crisis(self, world):
        J._set_escalation_level(world.marshals["Lannes"], "Soult",
                                J.ESCALATION_PERMANENT_LEVEL)
        _fire(world, "Lannes", "Soult")
        crisis = world.pending_marshal_petition
        _fire(world, "Massena", "Davout")
        assert world.pending_marshal_petition is crisis

    def test_lever_down_an_audience_is_a_modal(self, world, monkeypatch):
        monkeypatch.setattr(J, "THE_ANTECHAMBER", False)
        _fire(world, "Massena", "Davout")
        assert _queue_has_petition(world)
        assert not _rail(world, N.JEALOUSY_CONFRONTATION)


class TestTheLoadReprimeReadsTheTier:
    def test_a_loaded_audience_is_not_primed_into_the_queue(self, world):
        from backend.models.world_state import WorldState
        _fire(world, "Massena", "Davout")
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.pending_marshal_petition is not None
        assert loaded._popup_queue.get("pending_marshal_petition") is None

    def test_a_loaded_crisis_is_primed(self, world):
        from backend.models.world_state import WorldState
        J._set_escalation_level(world.marshals["Massena"], "Davout",
                                J.ESCALATION_PERMANENT_LEVEL)
        _fire(world, "Massena", "Davout")
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded._popup_queue.get("pending_marshal_petition") is not None
