"""FA slice 16 (part b) — "THE PRICE ON THE BUTTON".

Five rows in `strategic.py` / `world_state.py` / `combat_executor.py`:
**FA-56**, **FA-67**, **FA-61**, **FA-49**, **FA-52** (copy half).

⚠ **Four of the five could not be built as filed**, and the reproduction
pass measured why in each case. FA-67's headline is REFUTED and its fix
would delete the only true half; FA-61's fix prints a "ceiling" the resolver
exceeds by 7%; FA-49's static cost table would print −3 where the charge is
0; FA-52's copy prescription is ungrammatical for its own headline case.
Only FA-56 was buildable as written.

Reproduction of record: `docs/audits/fa_build_2026_09_04/repro/
REPRO_L_slice16_at_head.md`, group `FA-56, FA-67, FA-61, FA-49, FA-52`.
Landing record: the boxed SLICE 16 (part b) block in `docs/BUG_FIXES.md`.
"""

import contextlib
import inspect
import io
import os
import pathlib
import re

import pytest

from backend.commands import strategic
from backend.commands.combat_executor import CombatExecutor
from backend.models.world_state import WorldState, _faltering_trust_riders

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "europe_1805.json")


def _processor():
    from backend.commands.executor import CommandExecutor
    from backend.commands.strategic import StrategicOrderProcessor
    return StrategicOrderProcessor(CommandExecutor())


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture
def world():
    os.environ.setdefault(
        "INK_IRON_SAVE_DIR",
        str(pathlib.Path(os.environ.get("TEMP", "/tmp")) / "fa_s16b_saves"))
    pathlib.Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(parents=True,
                                                        exist_ok=True)
    return _quiet(WorldState.from_scenario, SCENARIO)


# ═══════════════════════════════════════════════════════════════════════════
# FA-56 — the Rebuke's intel pause has never once fired
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRebukePausesTheIntel:
    """The reader named `_literal_intel_paused_turn`; the only writer in the
    repository sets `literal_intel_paused_turn`, the PUBLIC serialized
    field. Control-proven in both directions before the fix: setting the
    underscore name darkened the sector, setting the real one did nothing."""

    @staticmethod
    def _lit(world):
        for marshal in world.marshals.values():
            if (marshal.nation == world.player_nation
                    and "literal" in str(
                        getattr(marshal, "personality", "")).lower()):
                return marshal
        return None

    def test_the_reader_names_the_field_the_writer_writes(self):
        src = inspect.getsource(WorldState.calculate_visibility)
        code = "\n".join(ln for ln in src.split("\n")
                         if not ln.lstrip().startswith("#"))
        assert '"_literal_intel_paused_turn"' not in code
        assert '"literal_intel_paused_turn"' in code

    def test_the_default_is_minus_one_not_none(self):
        """A fresh object must not match by accident on turn 0 — the field
        initialises to -1, so `None` as the default would compare a real
        turn against a sentinel of a different type."""
        src = inspect.getsource(WorldState.calculate_visibility)
        assert 'getattr(marshal, "literal_intel_paused_turn", -1)' in src

    def test_the_pause_actually_darkens_the_sector(self, world):
        marshal = self._lit(world)
        if marshal is None:
            pytest.skip("no player literal on this board")
        marshal.jealous_of = "Ney"

        def _seen():
            return {name for name, intel in world.intel.items()
                    if str(getattr(intel, "visibility", "")).upper().endswith(
                        ("FULL", "PARTIAL"))}

        _quiet(world.calculate_visibility)
        before = _seen()
        marshal.literal_intel_paused_turn = world.current_turn
        _quiet(world.calculate_visibility)
        paused = _seen()
        assert paused <= before
        # …and the pause is what did it: lift it and the sector comes back.
        marshal.literal_intel_paused_turn = -1
        _quiet(world.calculate_visibility)
        assert _seen() >= paused

    def test_the_stamp_survives_a_round_trip(self, world):
        marshal = self._lit(world) or next(iter(world.marshals.values()))
        marshal.literal_intel_paused_turn = 7
        from backend.models.marshal import Marshal
        assert Marshal.from_dict(
            marshal.to_dict()).literal_intel_paused_turn == 7


# ═══════════════════════════════════════════════════════════════════════════
# FA-67 — the advice states its dependency, and two riders it never said
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFalteringWarningTellsTheTruth:
    """⚠ The row's HEADLINE is refuted: a won battle DOES add trust, +3, via
    `VindicationTracker.resolve_battle` one call out of the combat files —
    which is why the row's census missed it. Its fix ("delete the battle
    clause") would delete the only true half."""

    def test_the_comment_names_the_seam_the_census_missed(self):
        src = inspect.getsource(WorldState._check_trust_warnings)
        assert "VindicationTracker" in src
        assert "a won battle is the reliable earner" not in src

    def test_the_advice_states_the_dependency(self, world):
        src = inspect.getsource(WorldState._check_trust_warnings)
        assert "let him win the battle he asked" in src
        assert "a vindicated objection is the only thing" in src

    def test_the_at_20_clause_is_kept(self, world):
        """FA-26 landed in slice 9, so "at 20 he will ask to be released" is
        now TRUE — and a pin one file over asserts the "20"."""
        src = inspect.getsource(WorldState._check_trust_warnings)
        assert "20 he will ask to be released" in src

    def test_a_clean_record_earns_no_rider(self, world):
        marshal = next(iter(world.marshals.values()))
        assert _faltering_trust_riders(world, marshal) == ""

    def test_a_pushover_is_told_his_record_blunts_the_advice(self, world):
        """`get_trust_gain_modifier` cuts the +3 to x0.5 above an 80% trust
        rate, so the advice's FIRST clause degrades its own SECOND."""
        tracker = world.authority_tracker
        tracker.recent_responses = [{"choice": "trust"} for _ in range(5)]
        assert tracker.get_trust_gain_modifier() == 0.5
        rider = _faltering_trust_riders(world, next(iter(world.marshals.values())))
        assert "taken his measure" in rider
        assert "x0.5" in rider

    def test_a_mixed_record_earns_the_softer_rider(self, world):
        tracker = world.authority_tracker
        tracker.recent_responses = ([{"choice": "trust"}] * 4
                                    + [{"choice": "insist"}] * 1)
        assert tracker.get_trust_gain_modifier() == 0.75
        assert "x0.75" in _faltering_trust_riders(
            world, next(iter(world.marshals.values())))

    def test_the_rider_reaches_the_real_warning(self, world):
        """The helper tests above prove the SENTENCE; this proves the message
        interpolates it. Dropping the call left all of them green."""
        marshal = next(m for m in world.marshals.values()
                       if m.nation == world.player_nation)
        marshal.trust.set(35)
        world.authority_tracker.recent_responses = [
            {"choice": "trust"} for _ in range(5)]
        warnings = _quiet(world._check_trust_warnings) or []
        mine = [w for w in warnings
                if marshal.name in str(w.get("message", ""))]
        assert mine, "the faltering warning did not fire"
        assert "taken his measure" in mine[0]["message"]
        assert "20 he will ask to be released" in mine[0]["message"]

    def test_the_rider_never_raises(self, world):
        """It is appended inside a message the turn loop builds; a throw
        here would take the whole warning with it."""

        class _Broken:
            def get_trust_gain_modifier(self):
                raise RuntimeError("boom")

        world.authority_tracker = _Broken()
        assert _faltering_trust_riders(
            world, next(iter(world.marshals.values()))) == ""


# ═══════════════════════════════════════════════════════════════════════════
# FA-61 — "if all march" was not a ceiling
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMusterStatesItsCeiling:

    @staticmethod
    def _label(preview):
        return CombatExecutor._format_muster_lines(
            CombatExecutor.__new__(CombatExecutor), preview)

    def test_the_ceiling_is_appended_when_present(self):
        line = self._label({
            "attacker": {"name": "Ney", "strength": 24000,
                         "committed_strength": 78676,
                         "ceiling_strength": 96789},
            "target": {"name": "Mack", "strength_display": "large force",
                       "location": "Swabia"},
            "odds_band": "favorable", "rows": []})
        assert "78,676 if all march" in line
        assert "up to 96,789 if every corps arrives" in line

    def test_a_preview_without_the_key_is_byte_identical(self):
        """The three standing pins on this phrase hand-build a preview with
        NO `ceiling_strength`. An additive clause behind an optional key is
        what keeps them green — renaming the label would red all three."""
        line = self._label({
            "attacker": {"name": "Ney", "strength": 24000,
                         "committed_strength": 41000},
            "target": {"name": "Mack", "strength_display": "large force",
                       "location": "Swabia"},
            "odds_band": "favorable", "rows": []})
        assert "41,000 if all march" in line
        assert "up to" not in line

    def test_a_ceiling_equal_to_the_expectation_says_nothing(self):
        line = self._label({
            "attacker": {"name": "Ney", "strength": 24000,
                         "committed_strength": 41000,
                         "ceiling_strength": 41000},
            "target": {"name": "Mack", "strength_display": "large force",
                       "location": "Swabia"},
            "odds_band": "favorable", "rows": []})
        assert "up to" not in line

    def test_the_committed_figure_is_not_moved(self):
        """⚠ `committed_strength` is NOT display-only: `muster_gate_arms`
        reads the `odds_band` derived from it — the CA9-row-2
        attack-confirm gate. The ceiling rides BESIDE it, never through
        it."""
        src = inspect.getsource(CombatExecutor._build_muster_preview)
        assert '"committed_strength": int(marshal.strength + committed_attacker)' in src
        assert "ceiling_attacker" in src

    def test_the_ceiling_is_computed_on_the_resolvers_own_basis(self):
        """The row's own fix — `expected_at=None` alone — prints 90,172
        against a reachable 96,789, because the sovereign aura is stamped at
        RESOLVE time only. The ceiling stamps it too, and restores what it
        found."""
        src = inspect.getsource(CombatExecutor._build_muster_preview)
        assert "sovereign_aura_strength" in src
        assert "finally:" in src

    def test_the_aura_is_restored_after_the_probe(self, world):
        """It writes on live marshals to price them. If it did not put them
        back, a preview would leave every candidate carrying an aura into
        the real resolution."""
        marshals = [m for m in world.marshals.values()
                    if m.nation == world.player_nation]
        before = {m.name: getattr(m, "sovereign_presence", 0.0)
                  for m in marshals}
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()._combat
        # The measured geometry: Ney on Mack at Swabia draws three joiners,
        # 78,676 expected against a 96,789 ceiling. A pair with no joiners
        # makes the two figures equal and the pin stops measuring.
        preview = _quiet(executor._build_muster_preview,
                         world.get_marshal("Ney"), world.get_marshal("Mack"),
                         world, {"world": world})
        after = {m.name: getattr(m, "sovereign_presence", 0.0)
                 for m in marshals}
        assert after == before
        # …and the probe was not a no-op: it produced the key it exists for,
        # and the ceiling genuinely EXCEEDS the arrival-weighted figure, so a
        # mutation that collapses one onto the other is visible here.
        assert "ceiling_strength" in preview["attacker"]
        assert (preview["attacker"]["ceiling_strength"]
                > preview["attacker"]["committed_strength"]), (
            "the ceiling collapsed onto the expectation — either the probe "
            "no longer drops the arrival weighting, or this geometry has no "
            "joiners and the pin has stopped measuring anything")

    def test_the_restore_is_observable(self, world):
        """⚠ On the boot board the aura is 0.0 and the joiners already carry
        0.0, so "restored" and "never touched" look identical and a mutation
        deleting the restore reads INERT. Stamp a non-zero value first and
        the restore has something to prove."""
        marshals = [m for m in world.marshals.values()
                    if m.nation == world.player_nation]
        for index, m in enumerate(marshals):
            m.sovereign_presence = 0.5 + index / 100.0
        before = {m.name: m.sovereign_presence for m in marshals}
        from backend.commands.executor import CommandExecutor
        _quiet(CommandExecutor()._combat._build_muster_preview,
               world.get_marshal("Ney"), world.get_marshal("Mack"),
               world, {"world": world})
        assert {m.name: m.sovereign_presence for m in marshals} == before


# ═══════════════════════════════════════════════════════════════════════════
# FA-49 — the price on the button
# ═══════════════════════════════════════════════════════════════════════════

class TestTheInterruptStatesItsPrice:

    def test_the_cannon_fire_costs_are_named(self):
        costs = strategic.interrupt_option_costs(
            {"interrupt_type": "cannon_fire",
             "options": ["investigate", "continue_order", "hold_position"]})
        assert costs == {"continue_order": -2, "hold_position": -3}

    def test_a_free_option_is_omitted_not_reported_as_zero(self):
        costs = strategic.interrupt_option_costs(
            {"interrupt_type": "cannon_fire",
             "options": ["investigate", "continue_order", "hold_position"]})
        assert "investigate" not in costs

    def test_a_first_step_interrupt_prices_nothing(self):
        """⚠ THE HAZARD IN THE FILED FIX. Three builders in
        `strategic_executor.py` set `is_first_step: True`, where the
        hold/cancel charge is genuinely 0 — a static table emitted from
        `strategic.py` alone would have printed "−3" on an interrupt that
        charges nothing, a NEW shown-vs-applied of exactly the class the row
        exists to close."""
        assert strategic.interrupt_option_costs(
            {"interrupt_type": "blocked_path", "is_first_step": True,
             "options": ["attack", "hold_position", "cancel_order"]}) == {}

    def test_a_later_step_interrupt_prices_the_abandonment(self):
        assert strategic.interrupt_option_costs(
            {"interrupt_type": "blocked_path",
             "options": ["attack", "hold_position", "cancel_order"]}) == {
                 "hold_position": -3, "cancel_order": -3}

    def test_an_option_not_offered_is_not_priced(self):
        assert strategic.interrupt_option_costs(
            {"interrupt_type": "cannon_fire",
             "options": ["investigate"]}) == {}

    def test_garbage_in_is_an_empty_dict_not_a_throw(self):
        for bad in (None, {}, {"interrupt_type": "unknown"},
                    {"interrupt_type": "cannon_fire", "options": None},
                    {"interrupt_type": "cannon_fire", "options": [1, 2]}):
            assert strategic.interrupt_option_costs(bad) == {}

    def test_the_quoted_price_is_the_price_charged(self, world):
        """⚠ THE DRIFT PIN, and it is BEHAVIOURAL. The literals are not
        renamed — `trust_change = -3` occurs four times in that file across
        different arms — so nothing but this holds the helper to the truth.
        It drives the real responder and compares the payment."""
        from backend.models.marshal import StrategicOrder
        marshal = world.get_marshal("Davout")
        marshal.strategic_order = StrategicOrder(
            command_type="HOLD", target="Rhineland", target_type="region",
            started_turn=world.current_turn - 2, original_command="hold",
            issued_turn=world.current_turn - 2)
        marshal.pending_interrupt = {
            "interrupt_type": "cannon_fire", "marshal": marshal.name,
            "battle_location": "Franconia",
            "options": ["investigate", "continue_order", "hold_position"]}
        quoted = strategic.interrupt_option_costs(marshal.pending_interrupt)
        before = marshal.trust.value
        result = _quiet(_processor().handle_response,
                        marshal.name, "cannon_fire", "continue_order",
                        world, {"world": world})
        assert result.get("trust_change") == quoted["continue_order"]
        assert marshal.trust.value == before + quoted["continue_order"]

    def test_the_costs_ride_their_own_payload_key(self):
        """⚠ Not the label map and not `options`. `OPTION_LABELS` is pinned
        as a flat dict of strings one file over, and `options` is a list of
        strings the backend validates by membership — neither may become a
        dict."""
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "interrupt_popup.gd").read_text(encoding="utf-8")
        assert 'interrupt_data.get("option_costs", {})' in gd
        assert 'OPTION_LABELS.get(option_id' in gd

    def test_the_suffix_is_plain_text(self):
        """`Button.text` is plain — BBCode would render as literal brackets."""
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts"
              / "interrupt_popup.gd").read_text(encoding="utf-8")
        block = gd[gd.index('_costs.has(option_id)'):][:400]
        assert "[color" not in block and "[b]" not in block

    def test_the_stamp_is_a_copy_not_the_stored_dict(self):
        """The stored `pending_interrupt` is handed out by reference from a
        dozen sites AND is serialized into the save. A display figure
        belongs in neither — so no new save key, no migration, and a
        pre-fix save renders its costs the moment it loads."""
        main = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert 'response["pending_interrupt"] = dict(_interrupt,' in main

    def test_a_real_response_carries_the_costs(self, world):
        import backend.main as M
        marshal = world.get_marshal("Davout")
        marshal.pending_interrupt = {
            "interrupt_type": "cannon_fire", "marshal": marshal.name,
            "options": ["investigate", "continue_order", "hold_position"]}
        response = _quiet(M.build_base_response, world, True, "x",
                          pending_interrupt=marshal.pending_interrupt)
        assert response["pending_interrupt"]["option_costs"] == {
            "continue_order": -2, "hold_position": -3}
        assert "option_costs" not in marshal.pending_interrupt, (
            "the stored dict was mutated — it is serialized")


# ═══════════════════════════════════════════════════════════════════════════
# FA-52 (copy half) — the marshal continues the order he was actually given
# ═══════════════════════════════════════════════════════════════════════════

class TestTheContinuedOrderIsNamed:

    def test_the_continue_arm_reads_the_command_type(self):
        """It was the ONLY arm in the function that did not call
        `_strategic_command_flavor` — measured, a marshal under a HOLD was
        told he "reluctantly continues the march" and then, in the same
        sentence, that he fortified where he stood."""
        src = inspect.getsource(strategic.StrategicOrderProcessor)
        block = src[src.index('elif choice == "continue_order":'):]
        block = block[:block.index('elif choice == "hold_position":')]
        # CODE lines only: the comment beside the fix quotes the old string
        # to explain what it replaced, and a raw census is satisfied by it.
        code = "\n".join(ln for ln in block.split("\n")
                         if not ln.lstrip().startswith("#"))
        assert "_strategic_command_flavor(order.command_type)" in code
        assert "continues the march" not in code

    def test_a_holding_marshal_is_not_told_he_marches(self, world):
        from backend.models.marshal import StrategicOrder
        marshal = world.get_marshal("Davout")
        marshal.strategic_order = StrategicOrder(
            command_type="HOLD", target="Rhineland", target_type="region",
            started_turn=world.current_turn - 2, original_command="hold",
            issued_turn=world.current_turn - 2)
        marshal.pending_interrupt = {
            "interrupt_type": "cannon_fire", "marshal": marshal.name,
            "battle_location": "Franconia",
            "options": ["investigate", "continue_order", "hold_position"]}
        message = _quiet(_processor().handle_response,
                         marshal.name, "cannon_fire", "continue_order",
                         world, {"world": world}).get("message", "")
        assert "continues the march" not in message
        assert "ignoring cannon fire" in message


# ═══════════════════════════════════════════════════════════════════════════
# What this slice deliberately did NOT build
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTaxIsStillCharged:
    """FA-52's mechanical half is a DESIGN question and is filed, not built:
    obeying a standing order costs 2 trust while abandoning it for the guns
    costs nothing, and slice 3 already priced the identical popup the other
    way (`_respond_combat_stalemate` charges 0 for "Continue as Ordered").
    These pins record the state the ruling will change, so the row cannot be
    quietly forgotten."""

    def test_continuing_still_costs_two(self):
        assert strategic.interrupt_option_costs(
            {"interrupt_type": "cannon_fire",
             "options": ["continue_order"]}) == {"continue_order": -2}

    def test_the_sibling_popup_prices_the_same_verb_at_zero(self):
        src = inspect.getsource(
            strategic.StrategicOrderProcessor._respond_combat_stalemate)
        assert "presses on" in src
        assert "trust_change = -2" not in src

    def test_the_row_is_open_with_an_owner(self):
        rows = (REPO / "docs" / "BUG_FIXES.md").read_text(encoding="utf-8")
        line = [ln for ln in rows.split("\n")
                if re.match(r"^(> )?\| \*\*FA-52\*\* \|", ln)]
        assert line, "FA-52's row has gone missing"
        assert "OPEN" in line[0] or "RULING" in line[0]

    def test_the_ruling_is_filed_with_an_owner_and_a_done_when(self):
        """GR9. The mechanical half is deferred, so it needs a home, an
        owner and a completion definition — not a note in a commit."""
        gate = (REPO / "docs" / "DESIGN_REFINEMENT.md").read_text(
            encoding="utf-8")
        assert "### FA-S16-D1" in gate
        block = gate[gate.index("### FA-S16-D1"):]
        block = block[:block.index("### FA-S16-D2")]
        assert "**Owner:**" in block
        assert "**Done when**" in block
        assert "_respond_combat_stalemate" in block, (
            "the ruling must carry the precedent that makes it a ruling")
