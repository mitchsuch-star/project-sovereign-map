"""Live playthrough (August 1, 2026) — the defects it found, pinned.

A 10-turn HTTP-driven 1805 campaign (the post-AI-phase creative-audit
addendum session) surfaced these. Every test reproduces a defect that was
seen live, not a hypothetical:

1. GHOST ENGAGEMENT — Mack, captured at Nassau and held at Paris (the
   captor's capital, strength 0 by design), "engaged" Mortier for four
   turns: "Cannot advance while engaged with enemy forces" from an empty
   room. The movement executor's engaged filter lacked the strength > 0
   guard every sibling filter has.
2. FRIENDLY-FIRE CAPTURE HINT — "[HINT] Franconia is undefended — attack
   to capture it!" named Bavaria's province (France's own bloc ally, with
   Deroy's 22k corps standing in it) and later Holland's Gelderland (a
   French vassal). The hint never checked war state with the controller.
3. IRON MARSHAL MISATTRIBUTION — Archduke John's and Moore's fortify
   lines carried "(Iron Marshal: …)" — Davout's epithet hardcoded onto
   the generic cautious kit (the July-9 misattribution class; three
   sites had been missed).
4. OBJECTION-THEN-FAILURE — Massena (engaged at Milan) objected to a
   fortify order; the player INSISTED through the drama; only then did
   execution fail on the engagement. The engaged check must run in
   pre-validation, before the objection ever fires.
5. OBJECTION-PENDING MISROUTE — with Massena's objection pending,
   typing "proceed" returned Berthier's "There is no pending diplomatic
   matter to respond to, Sire." while every real order stayed blocked on
   the objection.
6. UNANSWERABLE OFFER WORDS — with Britain's settlement offer active,
   typed "reject the offer" fell through to the parser and became a
   downgrade-relations clarification: the soft-stop matcher read only the
   dialogue's top-level options (settlement offers keep theirs inside
   popup_payload) and had no article-tolerant matching.
7. STALE OFFER CLAUSE ON DELIVERY — GET /pending_envoy served the
   popup payload cached at offer creation; a turn-3 offer read at turn 7
   still claimed Britain held Flanders and Orleanais after Spain had
   retaken both. (/mailbox/activate was fixed July 25; the delivery
   surface kept the stale cache.)
8. SELF-CONTRADICTING RETREAT — "Carniola cannot be reached, Sire — it
   is Austria-held soil and we are at war; Soult falls back to Carniola
   instead." When the doctrine's own safe pick IS the refused stated
   destination (a surrounded army), the note must say so honestly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def executor():
    return CommandExecutor()


def _game_state(world):
    return {"world": world}


def _capture_marshal_at(world, marshal_name: str, captor: str):
    """Put a marshal into the W6-7 captured state by hand: strength 0,
    held at the captor's capital — exactly what the live capture pipeline
    produces (combat_executor: 'off the map, held at the captor's
    capital')."""
    m = world.marshals[marshal_name]
    m.captured_by = captor
    m.captured_turn = int(world.current_turn)
    m.strength = 0
    m.location = world.get_nation_capital(captor)
    return m


# ═══════════════════════════════════════════════════════════════════════
# 1. A captured marshal's ghost must not engage anyone
# ═══════════════════════════════════════════════════════════════════════

class TestGhostEngagement:
    def test_prisoner_at_capital_does_not_block_movement(self, world, executor):
        # Mack, captured, held at Paris — the live shape.
        _capture_marshal_at(world, "Mack", "France")
        mortier = world.marshals["Ney"]
        mortier.location = "Paris"
        # An adjacent region made enemy-held so the engaged branch (which
        # only fires for non-friendly targets) is the one under test.
        world.capture_region("Champagne", "Britain")
        world.actions_remaining = 4

        result = executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Ney",
                        "action": "move", "target": "Champagne"},
        }, _game_state(world))

        assert "engaged with enemy forces" not in str(result.get("message", "")), (
            "a strength-0 prisoner held at the capital counted as an "
            "engagement — Mack's ghost pinned the garrison of Paris")

    def test_real_enemy_still_engages(self, world, executor):
        # Positive control: a live enemy in the region must still block.
        mack = world.marshals["Mack"]
        mack.location = "Paris"
        assert mack.strength > 0 and world.is_at_war("France", "Austria")
        ney = world.marshals["Ney"]
        ney.location = "Paris"
        world.capture_region("Champagne", "Britain")
        world.actions_remaining = 4

        result = executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Ney",
                        "action": "move", "target": "Champagne"},
        }, _game_state(world))

        assert not result.get("success")
        assert "engaged" in str(result.get("message", "")).lower()


# ═══════════════════════════════════════════════════════════════════════
# 2. The capture hint may only name provinces of courts we are AT WAR with
# ═══════════════════════════════════════════════════════════════════════

class TestCaptureHintWarScope:
    def _move(self, world, executor, marshal_name, target):
        world.actions_remaining = 4
        return executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": marshal_name,
                        "action": "move", "target": target},
        }, _game_state(world))

    def test_ally_province_never_hinted(self, world, executor):
        # Recreate the live board: France takes Swabia, whose neighbour
        # Franconia is Bavaria's (French bloc ally — NOT at war).
        world.capture_region("Swabia", "France")
        for m in world.marshals.values():
            if m.nation != "France" and m.location == "Swabia":
                m.location = "Vienna"
        ney = world.marshals["Ney"]
        ney.location = "Rhineland"
        assert not world.is_at_war("France", "Bavaria")

        result = self._move(world, executor, "Ney", "Swabia")

        hints = result.get("capture_hints") or []
        assert "Franconia" not in hints, (
            "the hint recommended attacking an ALLY's province — an attack "
            "there is a new war, not a walkover")
        assert "Franconia is undefended" not in str(result.get("message", ""))

    def test_at_war_province_still_hinted(self, world, executor):
        # SAME region, opposite premise: hand Franconia to Austria (at war)
        # and empty it — now the hint must fire. Together with the ally arm
        # this pins that the filter keys on WAR STATE, not on geography.
        world.capture_region("Swabia", "France")
        world.capture_region("Franconia", "Austria")
        for m in world.marshals.values():
            if m.location in ("Swabia", "Franconia") and m.name != "Ney":
                m.location = "Vienna"
        world.get_region("Franconia").garrison_strength = 0
        world.update_intel_from_scout("Franconia", world.current_turn)
        assert world.is_at_war("France", "Austria")
        ney = world.marshals["Ney"]
        ney.location = "Rhineland"

        result = self._move(world, executor, "Ney", "Swabia")

        assert "Franconia" in (result.get("capture_hints") or []), (
            "the war-scoped filter must not silence legitimate hints")


# ═══════════════════════════════════════════════════════════════════════
# 3. "Iron Marshal" is Davout's epithet, not the cautious kit's name
# ═══════════════════════════════════════════════════════════════════════

class TestIronMarshalCaption:
    def _fortify(self, world, executor, marshal_name):
        world.actions_remaining = 4
        m = world.marshals[marshal_name]
        # Clean slate: own soil, no enemies, defensive stance.
        world.capture_region(m.location, m.nation)
        for other in world.marshals.values():
            if other.nation != m.nation and other.location == m.location:
                other.location = "Vienna" if m.nation == "France" else "Paris"
        from backend.models.marshal import Stance
        m.stance = Stance.DEFENSIVE
        return executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": marshal_name,
                        "action": "fortify", "target": None},
        }, _game_state(world))

    def test_non_davout_cautious_gets_kit_name(self, world, executor):
        assert world.marshals["Bernadotte"].personality == "cautious"
        result = self._fortify(world, executor, "Bernadotte")
        msg = str(result.get("message", ""))
        assert "Iron Marshal" not in msg, (
            "Davout's epithet captioned another marshal's fortify — the "
            "live pass had it on Archduke John and Moore")
        assert "(Cautious:" in msg

    def test_davout_keeps_his_epithet(self, world, executor):
        result = self._fortify(world, executor, "Davout")
        assert "(Iron Marshal:" in str(result.get("message", ""))


# ═══════════════════════════════════════════════════════════════════════
# 4. Fortify-while-engaged fails BEFORE the objection, not after
# ═══════════════════════════════════════════════════════════════════════

class TestFortifyEngagedPreValidation:
    def test_no_objection_for_a_doomed_fortify(self, world, executor):
        # The live shape: Massena engaged at Milan by Charles, ordered to
        # fortify. Aggressive marshal + defensive order = objection bait —
        # which is exactly why the engaged check must come first.
        massena = world.marshals["Massena"]
        charles = world.marshals["ArchdukeCharles"]
        charles.location = massena.location
        assert charles.strength > 0
        assert world.is_at_war("France", "Austria")
        world.actions_remaining = 4
        world.pending_objection = None

        result = executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Massena",
                        "action": "fortify", "target": None},
        }, _game_state(world))

        assert not result.get("success")
        assert "cannot fortify while engaged" in str(result.get("message", ""))
        assert world.pending_objection is None, (
            "the objection fired for an action that could never execute — "
            "the player insisted through the drama and THEN got the failure")


# ═══════════════════════════════════════════════════════════════════════
# 5 + 6. Typed answers reach the thing that is actually pending
# ═══════════════════════════════════════════════════════════════════════

def _client_with(world):
    """Swap BOTH world handles (/command reads the module global, the
    GET endpoints read game_state) and force the mock parser so the
    suite never calls the live LLM."""
    import backend.main as main_module
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    client = TestClient(main_module.app)
    originals = (main_module.game_state["world"], main_module.world,
                 main_module.parser)
    main_module.game_state["world"] = world
    main_module.world = world
    main_module.parser = CommandParser(use_real_llm=False)
    return client, main_module, originals


def _restore(main_module, originals):
    (main_module.game_state["world"], main_module.world,
     main_module.parser) = originals


class TestObjectionPendingReprompt:
    def test_proceed_reprompts_the_objection(self, world):
        client, main_module, originals = _client_with(world)
        try:
            world.pending_objection = {
                "marshal": "Massena",
                "message": "Massena firmly objects.",
                "severity": 55,
                "type": "major_objection",
                "original_order": {"marshal": "Massena", "action": "fortify"},
            }
            # No diplomatic dialogue on a fresh world (the property is
            # read-only over the dialogue manager) — only the objection.
            assert world.pending_diplomatic_dialogue is None

            resp = client.post("/command", json={"command": "proceed"}).json()

            msg = str(resp.get("message", ""))
            assert "no pending diplomatic matter" not in msg.lower(), (
                "Berthier denied any pending matter while Massena's "
                "objection blocked every order")
            assert "Massena" in msg
            assert "trust" in msg and "insist" in msg
        finally:
            _restore(main_module, originals)


class TestSettlementOfferTypedAnswer:
    def _offer_dialogue(self, world) -> dict:
        war_id = next(iter(world.war_instances), None)
        assert war_id, "the 1805 boot has live war instances"
        return {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": "settlement_offer:test:1:1",
            "war_id": str(war_id),
            "proposer_nation": "Britain",
            "accepting_side": "attackers",
            "accepting_leader": "France",
            "covered_enemy_participants": ["Britain"],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": int(world.current_turn),
            "popup_payload": {
                "options": [
                    {"label": "Review Settlement Offer",
                     "action": "accept_settlement_offer"},
                    {"label": "Request Revision",
                     "action": "request_settlement_revision"},
                    {"label": "Reject Offer",
                     "action": "reject_settlement_offer"},
                ],
            },
        }

    def test_reject_the_offer_reaches_the_offer(self, world):
        client, main_module, originals = _client_with(world)
        try:
            world.dialogue_manager.push(self._offer_dialogue(world))
            assert world.pending_diplomatic_dialogue is not None

            resp = client.post(
                "/command", json={"command": "reject the offer"}).json()

            msg = str(resp.get("message", ""))
            assert "downgrade" not in msg.lower(), (
                "the natural answer to the on-screen offer became a "
                "downgrade-relations clarification")
            assert "rejected" in msg.lower()
            assert world.pending_diplomatic_dialogue is None, (
                "the offer dialogue must be consumed by the answer")
        finally:
            _restore(main_module, originals)

    def test_unrelated_command_still_passes_through(self, world):
        # The token-subset matcher must not over-capture: an order that
        # shares no full option label keeps flowing to the parser.
        client, main_module, originals = _client_with(world)
        try:
            world.dialogue_manager.push(self._offer_dialogue(world))
            resp = client.post(
                "/command", json={"command": "status"}).json()
            assert "rejected" not in str(resp.get("message", "")).lower()
            assert world.pending_diplomatic_dialogue is not None
        finally:
            _restore(main_module, originals)


# ═══════════════════════════════════════════════════════════════════════
# 7. /pending_envoy must rebuild the offer payload against today's map
# ═══════════════════════════════════════════════════════════════════════

class TestPendingEnvoyRebuildsOfferPayload:
    def test_stale_cache_is_not_served(self, world):
        client, main_module, originals = _client_with(world)
        try:
            war_id = next(iter(world.war_instances), None)
            assert war_id
            dialogue = {
                "type": "incoming_settlement_offer",
                "dialogue_type": "incoming_settlement_offer",
                "offer_id": "settlement_offer:test:2:1",
                "war_id": str(war_id),
                "proposer_nation": "Britain",
                "accepting_side": "attackers",
                "accepting_leader": "France",
                "covered_enemy_participants": ["Britain"],
                "settlement_terms": [{"type": "peace"}],
                "turn_created": int(world.current_turn),
                # The lie a turn-3 offer effectively carried at turn 7.
                "popup_payload": {
                    "description": "STALE — Britain retains everything",
                },
            }
            world.dialogue_manager.push(dialogue)

            resp = client.get("/pending_envoy").json()

            assert resp.get("has_pending")
            popup = resp.get("incoming_settlement_offer") or {}
            assert "STALE" not in str(popup), (
                "the delivery surface served the payload cached at offer "
                "creation — the map it described was turns old")
            assert popup.get("options"), (
                "the rebuilt payload carries the real option set")
        finally:
            _restore(main_module, originals)


# ═══════════════════════════════════════════════════════════════════════
# 8. A surrounded retreat says so — never "X cannot be reached; falls
#    back to X instead"
# ═══════════════════════════════════════════════════════════════════════

class TestSurroundedRetreatNote:
    def test_no_self_contradiction_when_doctrine_pick_is_the_stated_target(
            self, world, executor):
        ney = world.marshals["Ney"]
        ney.location = "Rhineland"
        # In danger: a live enemy shares the field.
        mack = world.marshals["Mack"]
        mack.location = "Rhineland"
        assert world.is_in_danger("Ney")
        # Stated destination made at-war soil, and the doctrine's own
        # safe pick agrees — the surrounded case (live: Soult at Hungary).
        world.capture_region("Swabia", "Austria")
        assert world.is_at_war("France", world.get_region("Swabia").controller)
        world.get_safe_retreat_destination = (
            lambda name, threat=None: "Swabia")
        world.actions_remaining = 4

        result = executor.execute({
            "success": True,
            "command": {"type": "specific", "marshal": "Ney",
                        "action": "retreat", "target": "Swabia"},
        }, _game_state(world))

        msg = str(result.get("message", ""))
        assert "cannot be reached, Sire" not in msg, (
            "the note refused Carniola and then fell back to Carniola in "
            "the same sentence")
        if "falls back" in msg:
            assert "No friendly ground lies open" in msg
