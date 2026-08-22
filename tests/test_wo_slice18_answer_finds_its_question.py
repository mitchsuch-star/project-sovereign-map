"""Row WO, slice 18 — "The Answer Finds Its Question" (August 22, 2026).

The WO-35/36/38 build, from the verification memo
`docs/audits/WO_35_36_38_VERIFICATION_2026_08_21.md` (authoritative — it
corrects both filed rows), in the memo's order:

  WO-39 (P2, FIRST — it blocked everything) the commitment-paradox handler
        disabled input unconditionally before a two-branch send; a third
        emitted choice left input disabled with no request in flight, and
        ESC cannot open the pause menu over a visible modal — unrecoverable.
  WO-38 (P1, hand-reproduced) a stale STRATEGIC objection hijacked the
        answer to a DIFFERENT marshal's tactical objection: the router
        checked the strategic slot FIRST, a strategic objection blocks
        nothing, and nothing cleared it at the turn boundary. Measured:
        with Ney's tactical objection on screen, "trust" gave Davout +8
        trust and fortified Davout. Fix = the tactical slot wins, AND the
        unanswered strategic objection lapses at the turn boundary WITH a
        told message (slice 16 established the order is never created at
        objection time, so the lapse loses nothing not already lost).
  WO-35 (pending_interrupt half ONLY) `/load` attaches a restored marshal
        interrupt and the client raises it through the same predicate/route
        pair the command path uses. `pending_objection` is deliberately NOT
        attached — the saved dict records no tactical/strategic
        discriminator and the strategic arm would render a modal with no
        buttons and no ESC exit (the filed fix was a soft-lock).
  WO-36 + WO-40 (client-side, zero backend change) the world-swap reset now
        clears `_redemption_recheck_turn` (WO-36's real cause — the stale
        latch skipped the PT-B1 recovery poll on a same-turn reload) and
        the four cross-campaign stashes (WO-40).

Every test names the mutation that kills it.
"""

import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
MAIN_GD = (REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd")
MAIN_PY = REPO / "backend" / "main.py"


def _suppress():
    return contextlib.redirect_stdout(io.StringIO())


def _world():
    world = WorldState(player_nation="France")
    world.actions_remaining = 4
    world.admin_actions_remaining = 2
    return world


def _tactical_objection(marshal="Ney", trust_gain=3):
    """The shape executor.py's raise site stores (test_disobedience idiom)."""
    return {
        "type": "major_objection",
        "marshal": marshal,
        "concern_level": "MODERATE",
        "message": f"{marshal} objects.",
        "original_order": {"action": "attack", "marshal": marshal,
                           "target": "Waterloo"},
        "suggested_alternative": None,
        "compromise": None,
        "trust_gain": trust_gain,
        "insist_penalty": -5,
    }


def _strategic_objection(marshal="Davout", target="Ney"):
    """The key set strategic_executor.py's raise site stores (lines
    1069-1093) — the same shape slice 16's tests use, so a live-produced
    objection and this one cannot drift apart without slice 16 noticing."""
    return {
        "type": "strategic",
        "concern_level": "MODERATE",
        "trust_tier": "NEUTRAL",
        "tone": "formal",
        "insist_penalty": -10,
        "trust_gain": 8,
        "compromise_gain": 3,
        "should_object": True,
        "severity": "major",
        "message": f"{marshal} questions the order.",
        "marshal": marshal,
        "personality": "cautious",
        "reason": "v2_cautious_support",
        "options": [
            {"type": "proceed", "text": "Proceed", "trust_change": -10,
             "ap_cost": 2},
            {"type": "preferred",
             "text": "Trust: Do not issue the SUPPORT order",
             "action": "cancel", "target": target,
             "trust_change": 8, "ap_cost": 1},
            {"type": "compromise", "text": "Timed SUPPORT (3 turns)",
             "trust_change": 3, "ap_cost": 2,
             "compromise": {"max_turns": 3}},
        ],
        "original_command": {"marshal": marshal, "action": "support",
                             "target": target},
        "parsed_command": {"command": {"marshal": marshal, "action": "support",
                                       "target": target}},
        "strategic_type": "SUPPORT",
        "path": [],
        "target": target,
        "marshal_name": marshal,
    }


# ═══════════════════════════════════════════════════════════════════
# WO-38 — the tactical objection wins the answer route
# ═══════════════════════════════════════════════════════════════════


class TestWO38TheTacticalObjectionWins:

    def test_the_answer_reaches_the_marshal_on_screen(self):
        """THE MEASURED HIJACK, dead. With Ney's tactical objection standing
        and a stale Davout strategic objection in the sibling slot, "trust"
        must resolve NEY's question — the one whose block message the player
        is reading — and leave Davout untouched.

        Mutation: restore the bare `pending_strategic_objection is not None`
        check ahead of the tactical read (drop the `pending_objection is
        None and` half of the condition)."""
        world = _world()
        ney_before = world.get_marshal("Ney").trust.value
        davout_before = world.get_marshal("Davout").trust.value
        world.pending_objection = _tactical_objection("Ney", trust_gain=3)
        world.pending_strategic_objection = _strategic_objection("Davout")
        ex = CommandExecutor()
        with _suppress():
            result = ex.handle_objection_response("trust", {"world": world})
        assert result.get("success") is not False or "Ney" in str(
            result.get("message", "")), result
        assert world.pending_objection is None, (
            "the tactical question was not consumed — the strategic slot "
            "captured the answer again")
        assert world.pending_strategic_objection is not None, (
            "the strategic slot was consumed by an answer aimed at Ney")
        assert world.get_marshal("Ney").trust.value > ney_before, (
            "Ney's trust did not move — his answer went elsewhere")
        assert world.get_marshal("Davout").trust.value == davout_before, (
            "Davout was paid for an answer addressed to Ney — the hijack")

    def test_a_strategic_only_slot_still_answers(self):
        """FALSIFIABLE NEGATIVE — with no tactical question standing, the
        strategic slot is still answerable exactly as before this slice.

        Mutation: reorder into `pending_objection is None and` becoming
        `pending_objection is not None and` (the inverted guard would send
        a strategic-only answer to the no-objection refusal)."""
        world = _world()
        world.pending_objection = None
        world.pending_strategic_objection = _strategic_objection("Davout")
        ex = CommandExecutor()
        with _suppress():
            result = ex.handle_objection_response("trust", {"world": world})
        # The trust arm of a SUPPORT objection is the slice-16
        # decline-to-issue: the slot resolves, nothing errors.
        assert world.pending_strategic_objection is None
        assert result.get("success") is True, result

    def test_nothing_pending_still_refuses(self):
        """The no-objection refusal is untouched."""
        world = _world()
        world.pending_objection = None
        world.pending_strategic_objection = None
        ex = CommandExecutor()
        with _suppress():
            result = ex.handle_objection_response("trust", {"world": world})
        assert result["success"] is False
        assert "No objection pending" in result["message"]


# ═══════════════════════════════════════════════════════════════════
# WO-38 — the unanswered strategic objection lapses, and is TOLD
# ═══════════════════════════════════════════════════════════════════


class TestWO38TheStrategicObjectionLapses:

    def test_the_slot_clears_at_the_turn_boundary(self):
        """Nothing used to clear it — the stale slot lived forever and was
        WO-35's save-restored silent occupant.

        Mutation: delete the lapse block in `_advance_turn_internal`."""
        world = _world()
        world.pending_strategic_objection = _strategic_objection("Davout")
        with _suppress():
            world.advance_turn()
        assert world.pending_strategic_objection is None

    def test_the_lapse_is_told(self):
        """A lapse the player is not told about is a silent loss — the memo's
        condition on the lapse was that it must be TOLD.

        Mutation: keep the clear, drop the `tactical_events.append`."""
        world = _world()
        world.pending_strategic_objection = _strategic_objection("Davout")
        with _suppress():
            world.advance_turn()
        lapses = [e for e in world.get_last_tactical_events()
                  if e.get("type") == "strategic_objection_lapsed"]
        assert len(lapses) == 1
        assert lapses[0]["marshal"] == "Davout"
        assert "lapses" in lapses[0]["message"]
        assert "never issued" in lapses[0]["message"], (
            "the message must say what was lost — nothing, because the "
            "order was never created (slice 16)")

    def test_the_lapse_survives_the_fog_filter(self):
        """The end-turn surface fog-filters tactical events; a player
        marshal's lapse line must pass or the telling is a fiction.

        Mutation: strip the `marshal` key from the lapse event (the filter
        drops location-less events owned by nobody only when they carry no
        marshal/nation; a player-marshal event is kept by ownership)."""
        from backend.commands.meta_executor import (
            _filter_tactical_events_by_fog,
        )
        world = _world()
        world.pending_strategic_objection = _strategic_objection("Davout")
        with _suppress():
            world.advance_turn()
        lapses = [e for e in world.get_last_tactical_events()
                  if e.get("type") == "strategic_objection_lapsed"]
        kept = _filter_tactical_events_by_fog(lapses, world)
        assert kept == lapses, "the lapse line was fogged away"

    def test_the_tactical_slot_is_not_lapsed(self):
        """DELIBERATE — the tactical objection blocks every command
        including end turn, so it cannot legitimately cross the boundary
        unanswered; lapsing it would delete the one question that is
        actually on screen. Pinned so a later cleanup does not 'symmetrize'
        this.

        Mutation: widen the lapse block to clear `pending_objection` too."""
        world = _world()
        world.pending_objection = _tactical_objection("Ney")
        with _suppress():
            world.advance_turn()
        assert world.pending_objection is not None

    def test_a_clean_boundary_emits_no_lapse_event(self):
        """FALSIFIABLE NEGATIVE — no stale slot, no lapse line.

        Mutation: make the lapse unconditional."""
        world = _world()
        world.pending_strategic_objection = None
        with _suppress():
            world.advance_turn()
        assert not [e for e in world.get_last_tactical_events()
                    if e.get("type") == "strategic_objection_lapsed"]


# ═══════════════════════════════════════════════════════════════════
# WO-35 — the restored interrupt is attached at /load
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def swapped():
    """A mock-parser TestClient over a world THIS test owns (the slice-15
    idiom — swap the module world, game_state and parser singleton or the
    request silently runs against the developer's live world)."""
    import backend.main as m
    from backend.commands.parser import CommandParser as _CP

    saved = (m.parser, m.world, m.game_state)
    m.parser = _CP(use_real_llm=False)
    m.world = WorldState(player_nation="France")
    m.game_state = {"world": m.world}
    try:
        yield TestClient(m.app), m
    finally:
        m.parser, m.world, m.game_state = saved


def _last_stand_interrupt(marshal="Ney"):
    """The order-FREE shape combat_executor stores — the member of the
    family that never re-surfaces on its own."""
    return {
        "interrupt_type": "last_stand",
        "marshal": marshal,
        "enemy": "Wellington",
        "enemy_nation": "Britain",
        "options": ["fight_to_the_last", "attempt_breakout"],
        "message": f"{marshal} is ENCIRCLED, Sire.",
    }


class TestWO35TheInterruptSurvivesTheLoad:

    @pytest.fixture
    def saved(self, swapped, tmp_path, monkeypatch):
        from backend import save_manager

        client, m = swapped
        monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path)
        return client, m, tmp_path

    def _save(self, m, tmp_path, name="wo35"):
        from backend import save_manager
        with _suppress():
            save_manager.save_game(m.world, save_name=name,
                                   filepath=tmp_path / f"{name}.json")

    def test_load_attaches_the_restored_interrupt(self, saved):
        """Mutation: delete the pending_interrupt scan at the `/load`
        tail."""
        client, m, tmp_path = saved
        ney = m.world.get_marshal("Ney")
        ney.pending_interrupt = _last_stand_interrupt("Ney")
        self._save(m, tmp_path)
        ney.pending_interrupt = None
        data = client.post("/load", json={"filename": "wo35.json"}).json()
        assert data["success"] is True
        attached = data.get("pending_interrupt")
        assert attached, "the restored interrupt was not attached"
        assert attached["marshal"] == "Ney"
        assert attached["interrupt_type"] == "last_stand"

    def test_a_captured_marshals_interrupt_is_not_attached(self, saved):
        """Hazard-4 idiom: a marshal who no longer stands must not attach a
        question nobody can act on.

        Mutation: drop the strength/captured_by guard from the scan."""
        client, m, tmp_path = saved
        ney = m.world.get_marshal("Ney")
        ney.pending_interrupt = _last_stand_interrupt("Ney")
        ney.strength = 0
        ney.captured_by = "Britain"
        self._save(m, tmp_path)
        data = client.post("/load", json={"filename": "wo35.json"}).json()
        assert data["success"] is True
        assert not data.get("pending_interrupt"), (
            "a captured marshal's stale interrupt was attached")

    def test_an_enemy_marshals_interrupt_is_not_attached(self, saved):
        """The scan is player-scoped — an ENEMY marshal's internal state is
        not the player's question (and would leak fogged state besides).

        Mutation: iterate `world.marshals.values()` instead of
        `get_player_marshals()`."""
        client, m, tmp_path = saved
        enemy = next(mm for mm in m.world.marshals.values()
                     if mm.nation != m.world.player_nation)
        enemy.pending_interrupt = _last_stand_interrupt(enemy.name)
        self._save(m, tmp_path)
        data = client.post("/load", json={"filename": "wo35.json"}).json()
        assert data["success"] is True
        assert not data.get("pending_interrupt")

    def test_load_attaches_no_objection_keys(self, saved):
        """THE DELIBERATE NON-ATTACH, pinned. The filed WO-35 fix — attach
        `pending_objection` at /load — is a soft-lock: the saved dict
        records no tactical/strategic discriminator and the strategic modal
        arm renders `options == []`, a modal with no buttons and no ESC
        exit. The objection stays answerable by its typed words (the block
        names them); modal-at-load is the declared slice-12 remainder.

        Mutation: add the objection attach without a discriminator."""
        client, m, tmp_path = saved
        m.world.pending_objection = _tactical_objection("Ney")
        self._save(m, tmp_path)
        data = client.post("/load", json={"filename": "wo35.json"}).json()
        assert data["success"] is True
        assert not data.get("pending_objection"), (
            "an objection attach without a discriminator renders a "
            "buttonless modal — the memo's named soft-lock")
        assert not data.get("objection")

    def test_a_restored_strategic_objection_still_reexecutes(self, saved):
        """Memo hazard 6: a strategic objection stores `original_command` /
        `parsed_command` which the answer path re-reads to re-execute —
        pin that the ROUND-TRIPPED dict still drives the handler rather
        than KeyError-ing on a lost field. (The dict shape is the raise
        site's own key set; slice 16's tests bind that shape.)

        Mutation: drop `original_command` from `to_dict`'s round-trip (any
        serialization regression on the stored dict)."""
        client, m, tmp_path = saved
        m.world.pending_strategic_objection = _strategic_objection("Davout")
        self._save(m, tmp_path)
        m.world.pending_strategic_objection = None
        data = client.post("/load", json={"filename": "wo35.json"}).json()
        assert data["success"] is True
        restored = m.world.pending_strategic_objection
        assert restored is not None, "the slot did not round-trip"
        assert restored.get("original_command", {}).get("action") == "support"
        ex = CommandExecutor()
        with _suppress():
            result = ex.handle_objection_response(
                "trust", {"world": m.world})
        assert isinstance(result, dict) and "message" in result
        assert m.world.pending_strategic_objection is None, (
            "the restored objection could not be answered")


# ═══════════════════════════════════════════════════════════════════
# The client half — source pins over main.gd (the house .gd idiom)
# ═══════════════════════════════════════════════════════════════════


def _gd_func_body(src: str, name: str) -> str:
    start = src.index(f"func {name}(")
    rest = src[start:]
    nxt = re.search(r"\nfunc ", rest[1:])
    body = rest[:nxt.start() + 1] if nxt else rest
    assert 100 < len(body) < 8000, (
        f"the function-body extraction returned {len(body)} chars — it has "
        f"drifted off the function it claims to bound")
    return body


class TestWO39TheParadoxHandlerHandsTheTerminalBack:

    def test_the_unknown_arm_reenables_input(self):
        """WO-39: input is disabled before a two-branch send; the third arm
        must hand the terminal back (ESC cannot open the pause menu over a
        visible modal, so there is no other exit).

        Mutation: delete the `else` branch."""
        src = MAIN_GD.read_text(encoding="utf-8")
        body = _gd_func_body(src, "_on_commitment_paradox_choice")
        else_arm = re.search(r"\telse:\n(.*)$", body, re.S)
        assert else_arm, "the handler has no third arm again"
        assert "set_input_enabled(true)" in else_arm.group(1), (
            "the third arm exists but does not re-enable input")


class TestWO36TheWorldSwapResetClearsTheStashes:

    RESET_LINES = [
        "_redemption_recheck_turn = -1",
        "pending_redemption_data = null",
        "pending_proclamation_data = null",
        "pending_diorama_data = null",
        "last_battle_diorama = null",
    ]

    def test_the_five_survivors_are_reset(self):
        """WO-36's real cause (the stale recheck latch) + WO-40's four
        cross-campaign stashes, all cleared in the ONE world-swap reset.

        Mutation: delete any one line."""
        src = MAIN_GD.read_text(encoding="utf-8")
        body = _gd_func_body(src, "_reset_frontend_state_for_world_swap")
        for line in self.RESET_LINES:
            assert line in body, f"the reset lost: {line}"

    def test_the_dead_verb_is_gone(self):
        """The fallback advertised `demand_obedience`, which the backend
        retired (Phase 3) and rejects; the typed intercept forwarded it to a
        guaranteed refusal; and BOTH display arms (the choice echo and the
        result banner) matched only the dead verb, so the Staff transfer the
        dialog actually emits echoed an empty line and never reached its
        banner.

        Mutation: restore the old verb in any of the four spots. (Comments
        may name the dead verb; the pin binds its QUOTED code forms.)"""
        src = MAIN_GD.read_text(encoding="utf-8")
        assert '"demand_obedience"' not in src
        assert "'demand_obedience'" not in src
        assert '"administrative_role"' in src


class TestWO35TheWorldSwapRaisesTheInterrupt:

    def test_the_swap_handler_consults_the_route_pair(self):
        """Same predicate/route pair as the command path, so the two cannot
        drift (the WO-30 discipline).

        Mutation: delete the interrupt arm from
        `_apply_world_swap_response`."""
        src = MAIN_GD.read_text(encoding="utf-8")
        body = _gd_func_body(src, "_apply_world_swap_response")
        assert "_response_has_interrupt_route" in body
        assert "_route_interrupt_response" in body

    def test_capture_wins_over_interrupt_at_load(self):
        """PRECEDENCE, pinned consciously (memo hazard 2): a world can carry
        both. The command path's route table runs capture (POST index 1)
        before interrupt; the load path must agree or the player sees a
        different modal depending on how the world arrived.

        Mutation: swap the two arms."""
        src = MAIN_GD.read_text(encoding="utf-8")
        body = _gd_func_body(src, "_apply_world_swap_response")
        assert (body.index("_response_has_capture_choice_route")
                < body.index("_response_has_interrupt_route"))

    def test_the_route_pair_still_exists(self):
        """The pins above are meaningful only while the pair they name are
        the real ones. Mutation: rename either."""
        src = MAIN_GD.read_text(encoding="utf-8")
        assert "func _response_has_interrupt_route(" in src
        assert "func _route_interrupt_response(" in src


# ═══════════════════════════════════════════════════════════════════
# The backend attach comment cannot silently outlive its code
# ═══════════════════════════════════════════════════════════════════


class TestTheLoadTailShape:

    def test_the_interrupt_scan_sits_beside_the_capture_attach(self):
        """One tail, both attaches — the census (slice 15) classifies
        `pending_interrupt` LOAD_REATTACHED on the strength of this code.

        Mutation: delete the scan (the census would then classify a key
        `/load` no longer delivers)."""
        src = MAIN_PY.read_text(encoding="utf-8")
        tail = src[src.index('@app.post("/load")'):]
        tail = tail[:tail.index('@app.get("/saves")')]
        assert "pending_capture_choice" in tail
        assert "pending_interrupt" in tail
        assert "get_player_marshals" in tail
