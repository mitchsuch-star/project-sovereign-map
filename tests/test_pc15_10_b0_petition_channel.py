"""PC15-10 slice B0 — the petition-channel opener (spec =
docs/PETITION_POPUP_REVISIT_SPEC.md §9, gate-free).

F4  the CENTRAL occupancy guard: `_push_petition` owns channel policy and
    returns a status ("queued"/"blocked"/"dormant"); producers stamp their
    trigger latches ONLY on "queued" (closes S8: a latch can no longer
    burn on a push the channel swallowed).
F3  no silent losses: the two remaining loss modes (rivalry
    blocked-when-occupied; war-weary blocked-when-occupied) emit a
    narration line — the CARD loss stays WAD, the MOMENT does not vanish.
F5  four latents: S1 the mutual-spiral beat carried no "level" key and
    was silently cappable · S4 the two rivalry call chains disagreed on
    what `new_value` means (derived vs stored) · S6 the separation
    retirement burst · S9 a loaded petition was invisible until the next
    end turn (the only PRIORITY_ORDER member that is a plain attribute).
F7  the drain family: /load destroyed one restored popup per load;
    /strategic_response could lose a queued Proclamation FOREVER;
    /mailbox/activate double-delivered — plus the route census that ends
    the class.
"""

import inspect
import re
from pathlib import Path

import pytest

from backend.game_logic import jealousy as J
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign" /
                 "assets" / "maps" / "europe_1805.json")


@pytest.fixture()
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _dummy_petition():
    return {"kind": "jealousy_confrontation", "title": "t", "body": "b",
            "options": [], "context": {}, "turn": 1}


# ════════════════════════════════════════════════════════════════════════
# F4 — the central guard
# ════════════════════════════════════════════════════════════════════════

class TestF4CentralGuard:
    def test_free_channel_queues(self, world):
        p = _dummy_petition()
        assert J._push_petition(world, p) == J.PETITION_QUEUED
        assert world.pending_marshal_petition is p
        assert world._popup_queue.get("pending_marshal_petition") is p

    def test_occupied_channel_blocks_and_never_overwrites(self, world):
        """The fifth-producer simulation: a new producer that pushes with
        no guard of its own is caught by the CHANNEL — the unconditional
        overwrite (how a declare-war once destroyed a queued
        confrontation) is structurally gone."""
        first = _dummy_petition()
        assert J._push_petition(world, first) == J.PETITION_QUEUED
        second = _dummy_petition()
        assert J._push_petition(world, second) == J.PETITION_BLOCKED
        assert world.pending_marshal_petition is first, (
            "an occupied channel was overwritten — the F4 guard is gone")

    def test_identity_repush_is_allowed(self, world):
        """The per-turn re-pusher (and the S9 load re-prime) re-push the
        OBJECT already holding the slot — identity exempts them."""
        p = _dummy_petition()
        J._push_petition(world, p)
        world._popup_queue.pop_highest()  # delivered but unanswered
        assert J._push_petition(world, p) == J.PETITION_QUEUED
        assert world._popup_queue.get("pending_marshal_petition") is p

    def test_dormant_world_returns_dormant(self, world):
        world.scenario_name = "tutorial"    # the TUT-F5 discriminator
        assert J._push_petition(world, _dummy_petition()) == \
            J.PETITION_DORMANT
        assert world.pending_marshal_petition is None

    def test_confrontation_latch_stamps_only_on_queued(self, world):
        """A blocked confrontation keeps its retry: the pair@level key is
        NOT stamped while the channel is occupied."""
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        world.pending_marshal_petition = _dummy_petition()
        ney.jealous_of = davout.name
        J.apply_jealousy(world, ney, davout, delta=2, threshold=1,
                         events=[])
        seen = set(getattr(world, "jealousy_confrontations_seen", []) or [])
        assert not any(k.startswith(J._pair_key(ney.name, davout.name))
                       for k in seen), (
            "a blocked confrontation burned its pair@level key — the "
            "level's audience is deleted instead of deferred")

    def test_war_weary_status_contract(self, world):
        marshal = world.marshals["Ney"]
        status = J.queue_war_weary_petition(world, marshal, "Austria",
                                            {"action": "declare_war"})
        assert status == J.PETITION_QUEUED
        assert world.pending_marshal_petition["kind"] == "war_weary"
        # occupied now — a second ask blocks
        assert J.queue_war_weary_petition(
            world, marshal, "Prussia", {}) == J.PETITION_BLOCKED

    def test_executor_stamp_sits_inside_the_queued_branch(self):
        """Source pin (S8): the `_ww_seen` stamp must be reachable only
        through the PETITION_QUEUED arm."""
        from backend.commands import diplomatic_executor as de
        src = inspect.getsource(de)
        at = src.index("queue_war_weary_petition")
        window = src[at:at + 900]
        assert "PETITION_QUEUED" in window
        stamp = window.index("_ww_seen.add")
        assert window.index("PETITION_QUEUED") < stamp


# ════════════════════════════════════════════════════════════════════════
# F3 — no silent losses
# ════════════════════════════════════════════════════════════════════════

class TestF3NarrationFallbacks:
    def test_blocked_rivalry_emits_the_line_and_keeps_the_key(self, world):
        world.pending_marshal_petition = _dummy_petition()
        massena = world.marshals["Massena"]
        massena.set_relationship("Ney", -1)
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": -1,
            "new_value": -1, "nation": "France"}])
        events = getattr(world, "_pending_jealousy_turn_events", []) or []
        notes = [e for e in events if e.get("type") == "rivalry_blocked_note"]
        assert notes, "the blocked rivalry moment vanished silently"
        assert "Massena" in notes[0]["message"]
        # WAD pin: the card is lost, the key is NOT stamped (a mend and
        # re-break may still petition), and the occupying petition stands.
        seen = set(getattr(world, "rivalry_transitions_seen", []) or [])
        assert f"{J._pair_key('Massena', 'Ney')}@-1" not in seen
        assert world.pending_marshal_petition["title"] == "t"

    def test_the_two_notes_are_cap_exempt(self):
        """Each note REPLACES a lost card — collapsing it into the
        '…further matters' tail would re-silence the loss."""
        assert "rivalry_blocked_note" in J.JEALOUSY_NARRATION_EXEMPT
        assert "war_weary_blocked_note" in J.JEALOUSY_NARRATION_EXEMPT

    def test_the_two_notes_reach_the_dispatch_whitelist(self):
        """The IGR-B trap: an event type absent from
        _DISPATCH_EVENT_TYPES is produced and never rendered."""
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES
        assert "rivalry_blocked_note" in _DISPATCH_EVENT_TYPES
        assert "war_weary_blocked_note" in _DISPATCH_EVENT_TYPES

    def test_war_weary_blocked_branch_exists_at_the_seam(self):
        """Source pin: the executor's BLOCKED arm emits the bit-back line
        (the QUEUED arm is behavior-tested via test_estate_riders_esp)."""
        from backend.commands import diplomatic_executor as de
        src = inspect.getsource(de)
        assert "war_weary_blocked_note" in src
        assert "bit back his counsel" in src


# ════════════════════════════════════════════════════════════════════════
# F5 — the four latents
# ════════════════════════════════════════════════════════════════════════

class TestF5S1MutualSpiralLevel:
    def test_producer_stamps_the_level_key(self):
        """Source pin: the mutual-spiral dispatch beat carries "level" —
        without it the cap exemption read 0 and filed the channel's most
        dramatic sentence under ROUTINE."""
        src = inspect.getsource(J)
        at = src.index("is now mutual — each schemes against the other")
        window = src[at:at + 700]
        assert '"level": level' in window, (
            "the mutual-spiral beat lost its level key — it is silently "
            "cappable again (F5-S1)")

    def test_a_leveled_mutual_event_survives_the_cap(self, world):
        """Behavior: the beat outlives a hot routine turn."""
        events = [{"type": "jealousy_escalation", "message": "the spiral",
                   "nation": "France", "marshal": "Ney", "target": "Davout",
                   "level": J.ESCALATION_MUTUAL_LEVEL}]
        for i in range(J.JEALOUSY_DISPATCH_CAP + 3):
            events.append({"type": "jealousy_fired",
                           "message": f"routine {i}", "nation": "France",
                           "marshal": "Ney"})
        J._cap_routine_drama(world, events, 0)
        assert any(e.get("message") == "the spiral" for e in events), (
            "the mutual spiral was collapsed into the tail")


class TestF5S4StoredNotDerived:
    def test_battle_path_derived_value_cannot_stamp_a_deeper_latch(
            self, world):
        """The battle chain passes the DERIVED value (stored − 1 for a
        live grievance); the latch and the card must follow STORED."""
        massena = world.marshals["Massena"]
        ney = world.marshals["Ney"]
        massena.set_relationship("Ney", -1)
        massena.jealous_of = "Ney"           # derived reads -2
        assert massena.get_relationship("Ney") == -2
        J.check_rivalry_transitions(world, [{
            "marshal": "Massena", "toward": "Ney", "change": -1,
            "new_value": -2,                  # what the battle path passes
            "nation": "France"}])
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["context"]["new_value"] == -1, (
            "a derived -2 stamped a @-2 card on a stored -1 pair (F5-S4)")
        seen = set(world.rivalry_transitions_seen or [])
        assert f"{J._pair_key('Massena', 'Ney')}@-1" in seen
        assert f"{J._pair_key('Massena', 'Ney')}@-2" not in seen

    def test_stored_zero_does_not_transition_on_a_derived_dip(self, world):
        """A grievance alone (stored 0, derived -1) is not a rivalry
        transition — the stored value never moved."""
        murat = world.marshals["Murat"]
        # simulate an unauthored pair (the MC-3 web authors Murat|Ney -1)
        murat.set_relationship("Ney", 0)
        murat.jealous_of = "Ney"
        assert murat.relationships.get("Ney", 0) == 0
        J.check_rivalry_transitions(world, [{
            "marshal": "Murat", "toward": "Ney", "change": -1,
            "new_value": -1, "nation": "France"}])
        assert world.pending_marshal_petition is None


class TestF5S6RetirementCollapse:
    def _flag(self, world, a: str, b: str):
        first, second = (a, b) if a < b else (b, a)
        ma, mb = world.marshals[first], world.marshals[second]
        ma.separation_flagged[second] = True
        mb.separation_flagged[first] = True

    def test_bulk_mend_emits_one_line(self, world):
        self._flag(world, "Davout", "Ney")
        self._flag(world, "Massena", "Murat")
        events = J.process_turn(world)
        closes = [e for e in events
                  if e.get("type") == "jealousy_separation_warning"
                  and "settled" in e.get("message", "")]
        assert len(closes) == 1, (
            f"a bulk-mend turn emitted {len(closes)} retirement bullets "
            f"(F5-S6 collapse gone)")
        assert closes[0].get("retired_pairs") == 2
        assert "files" in closes[0]["message"]

    def test_single_mend_keeps_the_original_sentence(self, world):
        self._flag(world, "Davout", "Ney")
        events = J.process_turn(world)
        closes = [e for e in events
                  if e.get("type") == "jealousy_separation_warning"
                  and "settled" in e.get("message", "")]
        assert len(closes) == 1
        assert "closes the file on" in closes[0]["message"]
        assert "Davout" in closes[0]["message"]
        assert "Ney" in closes[0]["message"]


class TestF5S9LoadRePrime:
    def test_loaded_petition_is_deliverable_immediately(self, world):
        J._push_petition(world, _dummy_petition())
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        # the round-trip pin (existing) — still pending
        assert world2.pending_marshal_petition is not None
        # the NEW delivery pin: the queue is primed, so the FIRST response
        # cycle can serve the card — not the first end turn.
        assert world2._popup_queue.get("pending_marshal_petition") \
            is not None, (
            "a loaded petition is invisible until the next end turn "
            "(F5-S9): the field was restored but the queue never primed")

    def test_no_petition_no_prime(self, world):
        assert world.pending_marshal_petition is None
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2._popup_queue.get("pending_marshal_petition") is None


# ════════════════════════════════════════════════════════════════════════
# F7 — the drain family
# ════════════════════════════════════════════════════════════════════════

def _post_routes():
    import backend.main as main_module
    return sorted({r.path for r in main_module.app.routes
                   if "POST" in (getattr(r, "methods", None) or set())})


class TestF7DrainFamily:
    # The DECLARED census. Every POST route names its popup-drain contract;
    # a new endpoint that forgets to declare itself fails here instead of
    # shipping the next generation of the IGR-X7 class.
    DRAINING = {
        "/command",                    # the main delivery channel
        "/marshal_petition_response",  # answer consumes, next popup rides
        "/respond_to_diplomatic_dialogue",
        "/respond_to_diplomatic_objection",
        "/new_game",                   # fresh world, nothing to lose
        "/delete_save",
        "/debug/set_trust",
        "/debug/set_authority",
    }
    NON_DRAINING = {
        "/respond_to_objection",
        "/capture_choice",
        "/respond_to_redemption",
        "/respond_to_glorious_charge",
        "/strategic_response",         # F7-2 (this slice)
        "/save",
        "/load",                       # F7-1 (this slice)
        "/mailbox/respond",
        "/notifications/dismiss",
        "/cancel_order",
    }
    PLAIN = {                          # no gameplay envelope at all
        "/config/llm",
        "/mailbox/activate",           # F7-3: return-only (this slice)
        "/diplomatic_preview",
        "/debug/acceptance_preview",
    }

    def test_route_census_every_post_endpoint_is_declared(self):
        declared = self.DRAINING | self.NON_DRAINING | self.PLAIN
        live = set(_post_routes())
        undeclared = live - declared
        assert not undeclared, (
            f"POST route(s) with no declared popup-drain contract: "
            f"{sorted(undeclared)} — decide drain/non-drain/plain and add "
            f"them to this census (spec §4-F7-4)")
        ghosts = declared - live
        assert not ghosts, (
            f"census names routes that no longer exist: {sorted(ghosts)}")

    def test_load_handler_is_non_draining(self):
        import backend.main as main_module
        src = inspect.getsource(main_module.load_endpoint)
        assert "include_popup_passthroughs=False" in src, (
            "/load drains again — one restored popup destroyed per load "
            "(F7-1)")
        assert "_fill_popup_keys_without_draining" in src

    def test_strategic_response_is_non_draining(self):
        import backend.main as main_module
        src = inspect.getsource(main_module)
        at = src.index('@app.post("/strategic_response")')
        body = src[at:at + 4000]
        assert "drain_popups=False" in body, (
            "/strategic_response drains again — a queued Proclamation "
            "delivered there is lost FOREVER (F7-2)")

    def test_mailbox_activate_is_return_only(self):
        import backend.main as main_module
        src = inspect.getsource(main_module.activate_mailbox_item)
        assert not re.search(
            r"world\.incoming_proposal_popup\s*=", src), (
            "/mailbox/activate writes the world popup field again — the "
            "queue copy double-delivers on the next /command (F7-3)")

    def test_load_behavior_keeps_the_restored_popup(self, tmp_path,
                                                    monkeypatch):
        """End to end: a save with a queued envoy popup survives /load
        with the popup still deliverable."""
        import backend.main as main_module
        from backend import save_manager
        from fastapi.testclient import TestClient

        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        world = WorldState.from_scenario(str(SCENARIO_PATH))
        world.incoming_proposal_popup = {"from_nation": "Austria",
                                         "proposal_type": "non_aggression"}
        save_manager.save_game(world, filepath=tmp_path / "b0probe.json")

        orig = (main_module.world, main_module.game_state)
        try:
            client = TestClient(main_module.app)
            data = client.post("/load",
                               json={"filename": "b0probe.json"}).json()
            assert data["success"]
            # keys present (contract) but None (nothing drained) …
            assert data.get("incoming_proposal") is None
            # … and the popup still queued for the next /command.
            assert main_module.world.incoming_proposal_popup is not None
        finally:
            (main_module.world, main_module.game_state) = orig
