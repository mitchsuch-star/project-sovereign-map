"""FA slice 16 (part c) — "THE NAME AND THE NOTICE".

**FA-100** (half a), **FA-95**, **FA-69**, **FA-93 + FA-N50 + FA-N47** as one
edit, and **FA-65**. Two rows of the group are FILED as rulings rather than
built: FA-44 (a second absolute casualty floor, against a landed sibling's
recorded dissent) and FA-98 (suppress a beat while leaving its state alive).

Reproduction of record: `docs/audits/fa_build_2026_09_04/repro/
REPRO_L_slice16_at_head.md`, group `FA-44, FA-65, FA-69, FA-93, FA-95,
FA-98, FA-100`. Landing record: the boxed SLICE 16 (part c) block in
`docs/BUG_FIXES.md`.
"""

import contextlib
import inspect
import io
import os
import pathlib

import pytest

from backend.commands.capture_executor import _estate_holder_display
from backend.commands.tactical_executor import _square_break_infinitive
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "europe_1805.json")


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _code(source):
    return "\n".join(ln for ln in source.split("\n")
                     if not ln.lstrip().startswith("#"))


@pytest.fixture
def world():
    os.environ.setdefault(
        "INK_IRON_SAVE_DIR",
        str(pathlib.Path(os.environ.get("TEMP", "/tmp")) / "fa_s16c_saves"))
    pathlib.Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(parents=True,
                                                        exist_ok=True)
    return _quiet(WorldState.from_scenario, SCENARIO)


# ═══════════════════════════════════════════════════════════════════════════
# FA-100 (half a) — three wipes the block's own comment argued against
# ═══════════════════════════════════════════════════════════════════════════

class TestALoadedWorldKeepsWhatFromDictRestored:
    """The three stores are serialized, restored by `from_dict`, and cleared
    at the real boundary by `_advance_turn_internal` — which is exactly the
    contract the five deliberate non-clears beside them cite. Measured: 4
    threat sources live, 4 after `from_dict`, **0 after `load_game`**, and
    the ledger's "why" rows went with them, 2 → 0."""

    @staticmethod
    def _round_trip(world, tmp_path):
        from backend import save_manager
        path = tmp_path / "s16c.json"
        _quiet(save_manager.save_game, world, "s16c", path)
        out = _quiet(save_manager.load_game, path)
        return out["world"] if isinstance(out, dict) else out

    def test_the_three_wipes_are_gone(self):
        from backend import save_manager
        src = inspect.getsource(save_manager.load_game)
        block = src[src.index("Clear transient per-turn data"):]
        block = _code(block[:block.index("# Fog of War: recalculate visibility")])
        for name in ("mild_concerns_this_turn", "gold_spent_this_turn",
                     "threat_sources_this_turn"):
            assert f"world.{name} = " not in block, name

    def test_the_dedupe_list_survives(self, world, tmp_path):
        """It is a per-marshal DEDUPE list, so the wipe let a marshal who had
        already raised a mild concern raise it again — the WO-23
        budget-refresh shape."""
        world.mild_concerns_this_turn = [{"marshal": "Ney", "concern": "x"}]
        assert self._round_trip(world, tmp_path).mild_concerns_this_turn == [
            {"marshal": "Ney", "concern": "x"}]

    def test_the_spend_record_survives(self, world, tmp_path):
        world.gold_spent_this_turn = {"Ney": 50}
        assert self._round_trip(world, tmp_path).gold_spent_this_turn == {
            "Ney": 50}

    def test_the_alarms_reasons_survive(self, world, tmp_path):
        world.threat_sources_this_turn = [
            {"source": "conquest", "amount": 5},
            {"source": "vassalage", "amount": 3}]
        assert len(self._round_trip(
            world, tmp_path).threat_sources_this_turn) == 2

    def test_the_real_boundary_still_clears_them(self, world):
        """It is only safe to keep them because the turn boundary empties
        them. Falsifiable: if `_advance_turn_internal` stopped clearing, a
        loaded save would carry them forever."""
        src = _code(inspect.getsource(WorldState._advance_turn_internal))
        for name in ("mild_concerns_this_turn", "gold_spent_this_turn",
                     "threat_sources_this_turn"):
            assert f"self.{name}" in src, name

    def test_the_block_states_the_reason_for_all_eight(self):
        from backend import save_manager
        src = inspect.getsource(save_manager.load_game)
        block = src[src.index("Clear transient per-turn data"):]
        block = block[:block.index("# Fog of War: recalculate visibility")]
        for name in ("diplomatic_trust_applied", "attacks_this_turn",
                     "objection_popups_this_turn", "mild_concerns_this_turn",
                     "gold_spent_this_turn", "threat_sources_this_turn"):
            assert name in block, f"{name} is not named as an exemption"


# ═══════════════════════════════════════════════════════════════════════════
# FA-95 — a countdown printed as elapsed time
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCooldownCountsForward:

    @staticmethod
    def _refuse(world, **extra):
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        from backend.commands.executor import CommandExecutor
        executor = DiplomaticExecutor(CommandExecutor())
        return _quiet(executor._execute_diplomatic_proposal,
                      dict({"target_nation": "Austria"}, **extra), world)

    def test_the_refusal_counts_down_not_back(self, world):
        world.player_proposal_cooldowns["Austria"] = 3
        message = self._refuse(world)["message"]
        assert "3 more turns" in message
        assert "turns ago" not in message

    def test_one_turn_is_singular(self, world):
        world.player_proposal_cooldowns["Austria"] = 1
        assert "1 more turn." in self._refuse(world)["message"]

    def test_the_per_type_refusal_counts_down_too(self, world):
        world.player_proposal_cooldowns["Austria_alliance"] = 2
        message = self._refuse(world, proposal_type="alliance")["message"]
        assert "2 more turns" in message
        assert "turns ago" not in message

    def test_the_court_is_named_not_keyed(self, world):
        """Both refusals printed the raw machine key, so a formed nation was
        addressed by a name it no longer has."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        src = _code(inspect.getsource(
            DiplomaticExecutor._execute_diplomatic_proposal))
        head = src[:src.index("proposal_type = diplomatic_data.get")]
        assert "{target_nation} rejected" not in head
        assert "formed_display_name(world, target_nation)" in head

    def test_the_make_amends_sibling_is_NOT_swept(self):
        """⚠ It shares the "only N turns ago" phrasing and is CORRECT — it
        computes genuinely elapsed time, and a standing pin asserts its
        wording. Sweeping it would have redded that pin and broken a true
        sentence."""
        from backend import display_names
        amends = display_names.AMENDS_REFUSAL_DISPLAY["cooldown_active"]
        assert "turns ago" in amends


# ═══════════════════════════════════════════════════════════════════════════
# FA-69 — the estate holder's name, on all seven surfaces
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEstateHolderIsNamed:

    def test_the_machine_key_is_still_the_machine_key(self):
        """⚠ `_handle_estate_choice` re-reads `estate_holder` with
        `world.marshals.get(...)`. A humanised value fails that lookup and
        returns "The estate question has lapsed." — so the display forms ride
        BESIDE it, never instead of it."""
        from backend.commands import capture_executor
        src = _code(inspect.getsource(
            capture_executor.CaptureExecutor._maybe_mount_estate_choice))
        assert '"estate_holder": holder.name,' in src
        assert '"estate_holder_display": humanize_entity_name(' in src

    def test_the_display_helper_humanises(self):
        assert _estate_holder_display(
            {"estate_holder_display": "Archduke Charles"}) == "Archduke Charles"

    def test_a_pre_fix_save_still_renders(self):
        """A save taken before this slice carries no `_display` key. It falls
        through to the humaniser rather than to the raw string."""
        assert _estate_holder_display(
            {"estate_holder": "ArchdukeCharles"}) == "Archduke Charles"

    def test_garbage_is_a_question_mark_not_a_throw(self):
        for bad in (None, {}, {"estate_holder": ""}, "not a dict"):
            assert _estate_holder_display(bad) == "?"

    def test_every_backend_sentence_reads_a_display_form(self):
        """SIX backend sites, not the two the row names or the four the
        earlier pass found: the two it missed are the confiscate and respect
        OUTCOME sentences, so the raw key survived the ANSWER as well as the
        question."""
        src = _code((REPO / "backend" / "commands" / "capture_executor.py")
                    .read_text(encoding="utf-8"))
        for dead in ("Marshal {holder.name}'s title is extinguished",
                     "Marshal {holder.name}'s title stands",
                     "sustains Marshal {holder.name}'s",
                     "{pending.get('estate_holder', '?')}"):
            assert dead not in src, dead

    def test_the_blocking_message_reads_it_too(self):
        src = _code((REPO / "backend" / "commands" / "executor.py")
                    .read_text(encoding="utf-8"))
        assert "estate_holder_display" in src

    def test_the_client_reads_the_display_keys_with_a_fallback(self):
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "capture_choice_dialog.gd").read_text(encoding="utf-8")
        assert 'data.get("estate_holder_display", "")' in gd
        assert 'data.get("estate_holder_nation_display", "")' in gd
        assert "Utils.display_nation_name(" in gd

    def test_the_endow_surface_was_swept_too(self):
        """One function over, same blast radius — an ENEMY holder's key on
        the endow refusal. 1805's single-word French names hide it on the
        sibling that reads the player's own marshal."""
        from backend.game_logic import dotation
        src = inspect.getsource(dotation.check_estate_eligibility)
        assert "FA-69" in src


# ═══════════════════════════════════════════════════════════════════════════
# FA-93 + FA-N50 — one frame, an infinitive on both sides
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSquareBreakReadsAsEnglish:

    @pytest.mark.parametrize("action,expected", [
        ("attack", "to attack"), ("move", "to march"),
        ("fortify", "to fortify"), ("drill", "to drill"),
        ("recruit", "to recruit"), ("garrison", "to garrison"),
        ("charge", "to charge"), ("stance_change", "to change stance"),
    ])
    def test_the_action_names_are_infinitives(self, action, expected):
        assert _square_break_infinitive(action) == expected

    @pytest.mark.parametrize("order,expected", [
        ("MOVE_TO", "to march"), ("PURSUE", "to pursue"),
        ("HOLD", "to hold"), ("SUPPORT", "to support"),
    ])
    def test_the_strategic_enums_go_through_the_shared_map(self, order,
                                                           expected):
        """FA-N50: the raw enum reached the player — "to MOVE TO"."""
        assert _square_break_infinitive(order) == expected

    def test_the_default_survives(self):
        assert _square_break_infinitive(None) == "to act"
        assert _square_break_infinitive("strategic order") == "to act"

    def test_the_two_rows_frames_cannot_both_ship(self):
        """⚠ FA-93's second option ("breaks formation AND {display}") would
        ship "breaks formation and March" the moment FA-N50 routes the
        strategic types through `STRATEGIC_ORDER_DISPLAY`, whose values are
        infinitive/noun forms. Exactly one frame survives, and it is "to"."""
        from backend.commands import tactical_executor
        src = _code(inspect.getsource(
            tactical_executor.TacticalExecutor._auto_break_square))
        assert "breaks formation and" not in src
        assert "breaks formation " in src

    def test_the_infinitive_map_is_scoped_to_this_seam(self):
        """Not a second same-shaped table in `display_names`, where a future
        caller could reach for the wrong one."""
        from backend import display_names
        assert not hasattr(display_names, "ACTION_INFINITIVE")


# ═══════════════════════════════════════════════════════════════════════════
# FA-N47 — the notice survives a refusal and a nested frame
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSquareBreakIsDelivered:

    @staticmethod
    def _executor():
        from backend.commands.executor import CommandExecutor
        return _quiet(CommandExecutor)

    def test_a_refusal_no_longer_swallows_it(self, world):
        """Measured before: a refused march, a refused attack and an organic
        refused drill all broke the square and said nothing."""
        executor = self._executor()
        executor._pending_square_break = {
            "marshal": "Ney", "nation": world.player_nation,
            "message": "\n[Square broken — Ney breaks formation to march]"}
        result = executor._attach_square_break(
            {"success": False, "message": "Region 'Moscow' not found."},
            {"world": world})
        assert "[Square broken" in result["message"]
        assert "Moscow" in result["message"]

    def test_an_enemy_marshals_notice_never_reaches_the_player(self, world):
        """⚠ The enemy AI runs NESTED inside the player's end-turn frame —
        measured depth 2, with Mack's own square breaking there. An unkeyed
        notice delivered from the outermost frame would put an enemy
        marshal's line on the player's end-turn message."""
        executor = self._executor()
        executor._pending_square_break = {
            "marshal": "Mack", "nation": "Austria",
            "message": "\n[Square broken — Mack breaks formation to attack]"}
        result = executor._attach_square_break(
            {"success": True, "message": "Turn ended."}, {"world": world})
        assert "[Square broken" not in result["message"]

    def test_the_notice_is_consumed_exactly_once(self, world):
        executor = self._executor()
        executor._pending_square_break = {
            "marshal": "Ney", "nation": world.player_nation,
            "message": "\n[Square broken — Ney breaks formation to march]"}
        first = executor._attach_square_break(
            {"success": True, "message": "a"}, {"world": world})
        second = executor._attach_square_break(
            {"success": True, "message": "b"}, {"world": world})
        assert "[Square broken" in first["message"]
        assert "[Square broken" not in second["message"]

    def test_a_result_with_no_message_still_gets_the_line(self, world):
        executor = self._executor()
        executor._pending_square_break = {
            "marshal": "Ney", "nation": world.player_nation,
            "message": "\n[Square broken — Ney breaks formation to march]"}
        result = executor._attach_square_break({"success": True},
                                               {"world": world})
        assert result["message"].startswith("[Square broken")

    def test_the_wrapper_actually_delivers_it(self, world):
        """The pins above call `_attach_square_break` directly, so none of
        them notices if `execute` stops calling it. This drives the real
        entry point."""
        executor = self._executor()
        # \u26a0 The square must break DURING the command, not before it: the
        # entry clear exists precisely to stop a notice leaking in from the
        # last one, so a fixture that pre-sets the field is measuring that
        # guard instead of this delivery.
        world.get_marshal("Ney").square_formation = True
        result = _quiet(executor.execute,
                        {"command": {"action": "move", "marshal": "Ney",
                                     "target": "Moscow",
                                     "raw_input": "Ney, march to Moscow"}},
                        {"world": world})
        assert result.get("success") is False, (
            "the fixture needs a REFUSED action \u2014 that is the arm that used "
            "to swallow the notice")
        assert "[Square broken" in str(result.get("message", ""))
        assert "breaks formation to march" in str(result.get("message", ""))

    def test_a_nested_frame_does_not_deliver_it(self, world):
        """\u26a0 Making only the CLEAR depth-aware lets the nested frame reach
        its own emit and prepend the notice onto a message
        `strategic_executor` DISCARDS. Same loss, one frame down, now looking
        fixed."""
        executor = self._executor()
        world.get_marshal("Ney").square_formation = True
        executor._execute_depth = 1          # pretend we are nested
        result = _quiet(executor.execute,
                        {"command": {"action": "move", "marshal": "Ney",
                                     "target": "Moscow",
                                     "raw_input": "Ney, march to Moscow"}},
                        {"world": world})
        assert "[Square broken" not in str(result.get("message", ""))
        assert getattr(executor, "_pending_square_break", None) is not None, (
            "the nested frame consumed a notice it must leave for the outer")

    def test_the_emit_is_outermost_only(self):
        """⚠ Making only the CLEAR depth-aware is not enough — the nested
        frame would reach its own emit and prepend the notice onto a message
        `strategic_executor` DISCARDS when it rebuilds the first-step line.
        Same loss, one frame down, now looking fixed."""
        from backend.commands.executor import CommandExecutor
        body = _code(inspect.getsource(CommandExecutor._execute_one))
        assert "_pending_square_break" not in body
        wrapper = _code(inspect.getsource(CommandExecutor.execute))
        assert "_attach_square_break" in wrapper
        assert "if _depth == 0:" in wrapper

    def test_the_entry_clear_is_kept(self):
        """Without it the notice leaks into the NEXT command."""
        from backend.commands.executor import CommandExecutor
        wrapper = _code(inspect.getsource(CommandExecutor.execute))
        assert "self._pending_square_break = None" in wrapper

    def test_the_depth_counter_unwinds_on_a_throw(self):
        from backend.commands.executor import CommandExecutor
        wrapper = _code(inspect.getsource(CommandExecutor.execute))
        assert "finally:" in wrapper


# ═══════════════════════════════════════════════════════════════════════════
# FA-65 — the remedy reaches the band where it is needed
# ═══════════════════════════════════════════════════════════════════════════

class TestTheUnrestBeatNamesTheRemedy:

    def test_the_beat_carries_the_hint(self):
        from backend.game_logic import dispatch
        text = dispatch._format_dispatch_event_text(
            "diplomatic_vassal_unrest",
            {"nation": "Switzerland", "recovery_hint": "Invest, or garrison."})
        assert "Switzerland" in text
        assert "Invest, or garrison." in text

    def test_a_beat_without_a_hint_still_renders(self):
        """⚠ A `.format()` on a template with an unsupplied key silently
        emits the RAW template, braces and all — which is how the first cut
        shipped "Talleyrand reports unrest in {nation}."."""
        from backend.game_logic import dispatch
        text = dispatch._format_dispatch_event_text(
            "diplomatic_vassal_unrest", {"nation": "Saxony"})
        assert text == "Talleyrand reports unrest in Saxony."
        assert "{" not in text

    def test_the_producer_supplies_it(self):
        from backend.game_logic import vassal
        src = _code(inspect.getsource(vassal.process_vassal_loyalty))
        assert '"recovery_hint": recovery_hint_for_grip(' in src

    def test_the_healthy_band_gate_is_NOT_touched(self):
        """⚠ The filed fix — drop the `>= 40` clause — fires the hint at ANY
        loyalty, including 8, the same turn the CRITICAL rebellion
        notification fires; duplicates the ledger's sentence verbatim in the
        band the ledger already covers; and REDS a standing pin that asserts
        silence at 30. The two bands already partition cleanly."""
        from backend.game_logic import vassal
        src = _code(inspect.getsource(vassal.process_vassal_loyalty))
        assert "if delta < 0 and new_loyalty >= 40:" in src

    def test_the_standing_pin_is_still_green(self):
        """The one pin in the tree that asserts its row's defect. It stays
        green because the per-tick event is untouched — the remedy went onto
        the beat instead."""
        from tests.test_vassal_recovery_lever import TestVS1RecoveryHint
        assert hasattr(TestVS1RecoveryHint, "test_no_hint_below_healthy_band")

    def test_the_third_producer_still_carries_it(self):
        """⚠ The row's "35-39 is a full dead zone, zero hint from either
        producer" is REFUTED: there are THREE producers and the ledger's has
        the INVERSE gate."""
        from backend.game_logic import diplomatic_ledger
        src = _code(inspect.getsource(diplomatic_ledger))
        assert "recovery_hint_for_grip" in src


# ═══════════════════════════════════════════════════════════════════════════
# What this slice deliberately did NOT build
# ═══════════════════════════════════════════════════════════════════════════

class TestTwoRowsAreRulingsNotBuilds:

    def test_fa44_is_filed_with_the_floor_question(self):
        gate = (REPO / "docs" / "DESIGN_REFINEMENT.md").read_text(
            encoding="utf-8")
        assert "### FA-S16-D3" in gate
        block = gate[gate.index("### FA-S16-D3"):]
        block = block[:block.index("### FA-S16-D4")]
        assert "carries a written dissent" in block, (
            "the ruling must name the landed sibling's DISSENT — that "
            "is what makes a second floor a decision, not a patch")
        assert "**Owner:**" in block and "**Done when**" in block

    def test_fa98_is_filed_with_the_beat_question(self):
        gate = (REPO / "docs" / "DESIGN_REFINEMENT.md").read_text(
            encoding="utf-8")
        assert "### FA-S16-D4" in gate
        block = gate[gate.index("### FA-S16-D4"):]
        assert "gate the STATE, not the beats" in block, (
            "the ruling must QUOTE the precedent that points the other "
            "way, not merely cite its id")
        assert "**Owner:**" in block and "**Done when**" in block

    def test_no_third_casualty_floor_was_minted(self):
        """⚠ FLIPPED CONSCIOUSLY September 6, 2026 — the ruling was TAKEN
        (FA-S16-D3) and this pin would now pass VACUOUSLY: the floor lives
        in a third module and is spelled `MIN_BATTLE_CASUALTIES`, so the
        old string check can never fail again.

        Its intent survives and is strengthened. The ruling did not mint a
        third floor — it deleted one, by extracting the war score's own bare
        literal into a shared home. So the pin now asserts the OUTCOME: 500
        untouched and untuned (WO-16's dissent unamended), exactly one
        absolute 1,000 in the tree, and neither reader carrying a private
        copy of it.
        """
        from backend.game_logic import battle_report, battle_scale, dispatch
        assert dispatch.OWN_MAULED_MIN_CASUALTIES == 500
        assert battle_scale.MIN_BATTLE_CASUALTIES == 1000
        for mod in (battle_report, dispatch):
            src = _code(inspect.getsource(mod))
            assert "MIN_CASUALTIES = 1000" not in src
            assert "MIN_BATTLE_CASUALTIES = " not in src
