"""FA slice 17 (part g) — "THE CLIENT TELLS THE TRUTH" (September 11, 2026).

Seven rows, all on the client's word or the docs' word: FA-70 (the war
detail printed enemy exhaustion twice or never), FA-82 (Skip/Conclude
latched the School off forever), FA-94 (no ESC on the read-and-dismiss
surfaces), FA-S13-1 (the map keys read different fields, the bare M said
nothing, the credits line hard-coded the shipped layout), FA-N81 (the F1
wizard ignored the transit gate its rows are refused by), FA-81 (README and
the School never mention the Emperor), FA-101 (a dead owner on a
KNOWN_SILENT save state — recorded ACCEPTED-UNREACHABLE with the argument).

Source censuses here are scoped to CODE — a function body, a signal line,
a `match` arm — never to the comment that explains the guard (slice 13's
lesson), and each carries a behavioural sibling where the engine can be
asked: the wizard rows are driven through `get_available_diplomatic_actions`
and the executor through `/command`; the FA-101 argument is measured, not
quoted.
"""

import contextlib
import io
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT = REPO_ROOT / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"
MAPS = CLIENT / "assets" / "maps"


def _read(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _code_only(text: str) -> str:
    """Full-line comments dropped. Never split a line on `#` — part e's
    lesson: a `#`-splitting stripper guts `[color=#…` strings."""
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


def _func_body(src: str, header: str) -> str:
    """The text of one GDScript function: from `header` to the next
    top-level `func`/`static func`/`signal`/`var` line."""
    at = src.index(header)
    rest = src[at + len(header):]
    nxt = re.search(r"\n(?:func |static func |signal |var |const |@onready )", rest)
    return rest[: nxt.start()] if nxt else rest


@pytest.fixture(scope="module")
def world_1805():
    from backend.models.world_state import WorldState
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(MAPS / "europe_1805.json"))


@pytest.fixture
def client(world_1805, monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend import save_manager
    from backend.commands.parser import CommandParser
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setattr(save_manager, "SAVE_DIR", tmp_path / "saves")
    (tmp_path / "saves").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(M, "world", world_1805)
    monkeypatch.setattr(M, "game_state", {"world": world_1805})
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app)


def _post(client, text):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": text}).json()


# ═══════════════════════════════════════════════════════════════════════
# FA-70 — the war detail says "Enemy War Exhaustion" exactly once
# ═══════════════════════════════════════════════════════════════════════

class TestFA70ExhaustionIsPrintedOnce:

    def _region(self):
        # Review round (L3-3): CODE only — "Unknown" was being read off the
        # FA-70 comment beside the arm.
        src = _code_only(_read(SCRIPTS / "war_detail_popup.gd"))
        we_at = src.index("\tif we != null:")
        naval_at = src.index('\tif naval_line != "":', we_at)
        return src, src[we_at:naval_at], src[naval_at:naval_at + 400]

    def test_the_unknown_arm_belongs_to_the_exhaustion_test(self):
        """NV-12 inserted the fleet block between the `if` and its `else`, so
        a fleetless court printed a figure AND "Unknown" and a fogged
        fleet-holder printed neither. The `else` must close `if we != null`
        BEFORE the fleet line is even read."""
        _src, between, _after = self._region()
        assert re.search(r"\n\telse:\n", between), between
        assert "Enemy War Exhaustion: [color=" in between
        assert between.count("Enemy War Exhaustion") == 2, "one figure arm, one Unknown arm"
        assert "Unknown" in between.split("\n\telse:\n", 1)[1]

    def test_the_fleet_block_stands_alone(self):
        _src, _between, after = self._region()
        block = after.split("\n\n", 1)[0]  # up to the blank line that ends it
        assert "Their fleet:" in block
        assert "\telse:" not in block, "a fleetless court must print nothing here"

    def test_the_exhaustion_line_is_never_written_twice_for_one_court(self):
        src, _b, _a = self._region()
        body = _func_body(src, "func _render_war_detail(") if "func _render_war_detail(" in src else src
        assert body.count("Enemy War Exhaustion:") == 2, (
            "exactly the figure arm and the Unknown arm — a third writer is the defect back")


# ═══════════════════════════════════════════════════════════════════════
# FA-82 — choosing the School is the consent that clears the latch
# ═══════════════════════════════════════════════════════════════════════

class TestFA82TheSchoolCanBeChosenAgain:

    def test_choosing_the_school_clears_the_latch(self):
        body = _func_body(_read(SCRIPTS / "main_menu.gd"), "func _launch(")
        assert 'if action == "tutorial":' in body
        arm = body.split('if action == "tutorial":', 1)[1]
        assert "UiSettings.set_tutorial_done(false)" in arm.split("\n\n", 1)[0]

    def test_the_school_choice_is_the_only_writer_of_false(self):
        writers = sorted(p.name for p in SCRIPTS.glob("*.gd")
                         if "set_tutorial_done(false)" in _read(p))
        assert writers == ["main_menu.gd"], writers

    def test_conclude_still_latches(self):
        assert "set_tutorial_done(true)" in _read(SCRIPTS / "tutorial_overlay.gd")


# ═══════════════════════════════════════════════════════════════════════
# FA-94 — ESC dismisses what is read-and-dismiss, and nothing that decides
# ═══════════════════════════════════════════════════════════════════════

class TestFA94EscapeDismissesOnlyWhatIsReadAndDismiss:

    def test_popup_base_routes_ui_cancel_through_the_overridable_control(self):
        body = _func_body(_read(SCRIPTS / "popup_base.gd"), "func _unhandled_input(")
        assert 'is_action_pressed("ui_cancel")' in body
        assert "esc_control()" in body
        assert "control.pressed.emit()" in body, "the HANDLER runs, so the dismissal signal fires"
        assert "set_input_as_handled()" in body
        assert "close_popup()" not in body, (
            "a bare close hides the card and orphans the stashed surfaces — the soft-lock class")

    def test_the_default_control_is_null(self):
        body = _func_body(_read(SCRIPTS / "popup_base.gd"), "func esc_control()")
        code = [ln for ln in body.splitlines() if ln.strip() and not ln.strip().startswith("#")
                and '"""' not in ln and not ln.strip().startswith(("NULL", "must", "option", "read", "ESC", "control", "bare", "every"))]
        assert code and code[-1].strip() == "return null", body

    def test_a_disabled_or_absent_control_declines_without_consuming(self):
        body = _func_body(_read(SCRIPTS / "popup_base.gd"), "func _unhandled_input(")
        guard = body.split("var control := esc_control()", 1)[1]
        assert "control == null or control.disabled" in guard
        assert guard.index("return") < guard.index("set_input_as_handled()")

    def test_only_the_proclamation_overrides_it(self):
        overriders = sorted(p.name for p in SCRIPTS.glob("*.gd")
                            if "func esc_control()" in _read(p))
        assert overriders == ["popup_base.gd", "proclamation_popup.gd"], overriders
        body = _func_body(_read(SCRIPTS / "proclamation_popup.gd"), "func esc_control()")
        assert "return acknowledge_btn" in body

    def test_the_decision_popups_inherit_the_null_default(self):
        """The interrupt (the rightmost cannon-fire option is `hold_position`
        at −3 trust) and the paradox are DECISIONS: they extend PopupBase and
        must not override the control."""
        for name in ("interrupt_popup.gd", "commitment_paradox_popup.gd"):
            src = _read(SCRIPTS / name)
            assert "extends PopupBase" in src, name
            assert "func esc_control" not in src, name

    def test_the_letter_book_closes_on_escape(self):
        body = _func_body(_read(SCRIPTS / "mailbox_panel.gd"), "func _unhandled_input(")
        assert 'is_action_pressed("ui_cancel")' in body
        assert "_on_close()" in body
        assert "if not visible" in body or "if visible" in body


# ═══════════════════════════════════════════════════════════════════════
# FA-S13-1 — the two map-key routes agree, the bare M speaks, the credits
# line knows which build it is in
# ═══════════════════════════════════════════════════════════════════════

class TestFAS131TheMapKeysAgree:

    def test_the_renderer_reads_keycode_like_the_alt_route(self):
        renderer = _code_only(_func_body(_read(SCENES / "map_renderer_base.gd"), "func _unhandled_input("))
        assert "match event.keycode:" in renderer
        assert "physical_keycode" not in renderer, "the comment may name it; the code must not read it"
        main = _read(SCRIPTS / "main.gd")
        assert re.search(r"_alt_game_key\(event\.keycode\)", main), "the Alt route is fed the same field"

    def test_the_bare_m_key_reports_through_the_one_sentence(self):
        renderer_src = _read(SCENES / "map_renderer_base.gd")
        assert "signal map_mode_changed(mode: String)" in renderer_src
        renderer = _func_body(renderer_src, "func _unhandled_input(")
        assert "map_mode_changed.emit(cycle_map_fill_mode())" in renderer
        main = _read(SCRIPTS / "main.gd")
        assert "map_area.map_mode_changed.connect(_on_map_mode_changed)" in main
        alt = _func_body(main, "func _alt_game_key(")
        assert "_on_map_mode_changed(map_area.cycle_map_fill_mode())" in alt
        handler = _code_only(_func_body(main, "func _on_map_mode_changed("))
        assert 'Map view: " + mode' in handler
        assert _code_only(main).count("Map view: ") == 1, "ONE printer, or the two routes drift apart"

    def test_the_credits_line_branches_on_the_build(self):
        src = _read(SCRIPTS / "settings_panel.gd")
        at = src.index("var terms_where :=")
        block = src[at:src.index("credit.text =", at)]
        assert 'OS.has_feature("editor")' in block
        assert "repository root" in block
        assert "beside the game" in block and "licenses\\\\" in block
        assert 'Full terms: " + terms_where' in src


# ═══════════════════════════════════════════════════════════════════════
# FA-N81 — the wizard greys exactly what the transit gate refuses
# ═══════════════════════════════════════════════════════════════════════

def _rows(world, court="Prussia"):
    from backend.game_logic.diplomacy import get_available_diplomatic_actions
    return {r["action"]: r for r in get_available_diplomatic_actions(world, court)}


def _in_transit(world):
    """Set the state, hand back a restorer."""
    prior = getattr(world, "talleyrand_state", "IDLE")
    world.talleyrand_state = "IN_TRANSIT"

    def restore():
        world.talleyrand_state = prior
    return restore


def _wizard_echo_table():
    """(action_id -> typed echo) from diplomacy_wizard.gd's OWN table, the
    GDScript concatenation evaluated as Python (`+` and `str()` agree)."""
    src = _read(SCRIPTS / "diplomacy_wizard.gd")
    body = _func_body(src, "func _build_command(")
    table = {}
    for arm in re.finditer(r'\n\t\t"([a-z_]+)":\n(.*?)(?=\n\t\t"[a-z_]+":|\n\treturn "")', body, re.S):
        action_id, arm_body = arm.group(1), arm.group(2)
        ret = re.search(r"return (.+)", arm_body)
        assert ret, action_id
        echo = eval(ret.group(1), {"nation": "Prussia", "aim": "Austria", "amount": 200, "str": str})
        table[action_id] = echo
    assert len(table) >= 20, table
    return table


class TestFAN81TheWizardMirrorsTheTransitGate:

    def test_in_transit_every_gated_row_is_greyed_with_the_gates_own_reason(self, world_1805):
        from backend.commands.diplomatic_executor import (
            TRANSIT_DISABLED_REASON, TRANSIT_GATED_WIZARD_ACTIONS)
        idle = _rows(world_1805)
        restore = _in_transit(world_1805)
        try:
            transit = _rows(world_1805)
        finally:
            restore()
        gated = [a for a in transit if a in TRANSIT_GATED_WIZARD_ACTIONS]
        assert len(gated) >= 4, sorted(transit)
        assert any(a.startswith("propose_") for a in gated), "a proposal row must be on the board"
        for a in gated:
            assert transit[a]["available"] is False, a
            assert transit[a]["disabled_reason"] == TRANSIT_DISABLED_REASON, a
            assert transit[a]["disabled_reason_display"] == TRANSIT_DISABLED_REASON, a
        for a in transit:
            if a not in TRANSIT_GATED_WIZARD_ACTIONS:
                assert transit[a].get("available") == idle[a].get("available"), a

    def test_the_defect_is_reproduced_with_the_lever_down(self, world_1805, monkeypatch):
        from backend.game_logic import diplomacy
        from backend.commands.diplomatic_executor import TRANSIT_GATED_WIZARD_ACTIONS
        monkeypatch.setattr(diplomacy, "WIZARD_MIRRORS_THE_TRANSIT_GATE", False)
        idle = _rows(world_1805)
        restore = _in_transit(world_1805)
        try:
            transit = _rows(world_1805)
        finally:
            restore()
        lied = [a for a in transit if a in TRANSIT_GATED_WIZARD_ACTIONS
                and not a.startswith("mission_") and transit[a].get("available")]
        assert lied, "the prior builder rendered at least one refused row enabled"
        for a in lied:
            assert transit[a].get("available") == idle[a].get("available")

    def test_the_vassal_branch_greys_its_cancel_row_too(self, world_1805):
        """The cancel row is built by ONE helper both branches call; a mission
        against a court later vassalized keeps it — and in transit it is
        refused like the rest."""
        from backend.commands.diplomatic_executor import TRANSIT_DISABLED_REASON
        vassal = next(iter(getattr(world_1805, "vassals", {}) or {}), None)
        assert vassal, "the 1805 boot has vassals"
        prior_mission = getattr(world_1805, "active_diplomatic_mission", None)
        world_1805.active_diplomatic_mission = {"type": "IMPROVE_RELATIONS", "target": vassal,
                                                "initial_relation": 0, "turns_active": 1}
        restore = _in_transit(world_1805)
        try:
            rows = _rows(world_1805, vassal)
        finally:
            restore()
            world_1805.active_diplomatic_mission = prior_mission
        assert "cancel_mission" in rows, sorted(rows)
        assert rows["cancel_mission"]["available"] is False
        assert rows["cancel_mission"]["disabled_reason"] == TRANSIT_DISABLED_REASON

    def test_the_executor_refuses_what_the_wizard_greys(self, world_1805, client):
        from backend.commands.diplomatic_executor import TRANSIT_GATED_WIZARD_ACTIONS
        table = _wizard_echo_table()
        restore = _in_transit(world_1805)
        try:
            for action_id in sorted(TRANSIT_GATED_WIZARD_ACTIONS):
                r = _post(client, table[action_id])
                assert r.get("success") is False, (action_id, r.get("message"))
                assert "en route" in str(r.get("message", "")), (action_id, r.get("message"))
            # and a row the wizard leaves enabled is NOT met by the transit refusal
            r = _post(client, table["buy_off_design"])
            assert "en route" not in str(r.get("message", "")), r.get("message")
        finally:
            restore()

    def test_the_set_is_the_wizards_own_echo_table_read_through_the_parser(self, world_1805):
        """Drift pin: every wizard id whose typed echo parses INTO the gated
        executor dispatch is in the set, and no id outside it does. The two
        structured rows (`open_settlement`, `propose_white_peace`) dispatch by
        their payload action, which the wizard names in code."""
        from backend.commands.diplomatic_executor import (
            TRANSIT_GATED_EXECUTOR_ACTIONS, TRANSIT_GATED_WIZARD_ACTIONS)
        from backend.commands.parser import CommandParser
        wizard_src = _read(SCRIPTS / "diplomacy_wizard.gd")
        structured = {}
        payload_fn = _func_body(wizard_src, "func _structured_payload_for_action(")
        for arm in re.finditer(r'if action_id == "([a-z_]+)":(.*?)(?=\n\tif action_id|\n\treturn)', payload_fn, re.S):
            m = re.search(r'"action":\s*"([a-z_]+)"', arm.group(2))
            assert m, arm.group(1)
            structured[arm.group(1)] = m.group(1)
        assert structured == {"open_settlement": "propose_common_peace",
                              "propose_white_peace": "propose_white_peace",
                              "grant_region_to_vassal": "grant_region_to_vassal"}, structured
        parser = CommandParser(use_real_llm=False)
        table = _wizard_echo_table()
        drift = []
        for action_id, echo in sorted(table.items()):
            if action_id in structured:
                action = structured[action_id]
            else:
                with contextlib.redirect_stdout(io.StringIO()):
                    parsed = parser.parse(echo, {"world": world_1805}, world=world_1805)
                # `parse()` wraps the command: {"success", "command": {"action", …}, …}
                action = str(((parsed or {}).get("command") or {}).get("action") or "")
            gated_by_executor = action in TRANSIT_GATED_EXECUTOR_ACTIONS
            if gated_by_executor != (action_id in TRANSIT_GATED_WIZARD_ACTIONS):
                drift.append((action_id, echo, action))
        assert not drift, drift
        assert set(table) >= TRANSIT_GATED_WIZARD_ACTIONS, sorted(TRANSIT_GATED_WIZARD_ACTIONS - set(table))

    def test_the_executor_dispatch_tuple_is_the_gates_domain(self):
        """The gate refuses everything `_execute_diplomatic` dispatches but
        feasibility; the set beside it must be exactly that tuple."""
        from backend.commands.diplomatic_executor import TRANSIT_GATED_EXECUTOR_ACTIONS
        src = _read(REPO_ROOT / "backend" / "commands" / "executor.py")
        at = src.index("# DIPLOMATIC COMMANDS (Phase 8 Session 3)")
        tup = re.search(r"elif action in \((.*?)\):", src[at:], re.S).group(1)
        names = set(re.findall(r'"([a-z_]+)"', tup))
        assert names == TRANSIT_GATED_EXECUTOR_ACTIONS | {"diplomatic_feasibility"}, (
            names ^ (TRANSIT_GATED_EXECUTOR_ACTIONS | {"diplomatic_feasibility"}))


# ═══════════════════════════════════════════════════════════════════════
# FA-81 — the Emperor is taught where the marshals are
# ═══════════════════════════════════════════════════════════════════════

class TestFA81TheEmperorIsTaught:

    def test_the_readme_names_the_emperor_beside_the_seven(self):
        text = _read(REPO_ROOT / "deploy" / "README_TESTER.txt")
        assert "Seven marshals and the Emperor himself" in text
        block = text[text.index("THE EMPEROR"):]
        head = block[:900]
        for phrase in ("Napoleon", "never objects", "CAPTURED", "+1 diplomatic point", "Not in the School"):
            assert phrase in head, phrase

    def test_the_school_script_carries_the_np_inventory(self):
        text = _read(REPO_ROOT / "docs" / "TUTORIAL_SCRIPT.md")
        at = text.index("### The Emperor (SHIPPED")
        section = text[at:text.index("### Naval (SHIPPED", at)]
        rows = [ln for ln in section.splitlines() if ln.startswith("| ") and "Priority" not in ln
                and not ln.startswith("|---")]
        assert len(rows) >= 4, rows
        assert "sovereign-free" in section
        assert "Must-know" in section

    def test_the_roster_pin_is_derived_from_the_scenario(self):
        src = _read(REPO_ROOT / "tests" / "test_prebuild_fixes_2026_08_14.py")
        body = src[src.index("def test_current_roster_present"):]
        body = body[:body.index("\n    def ")] if "\n    def " in body else body
        assert "europe_1805.json" in body
        # Review round (L3-2): assert the DERIVATION, not the absence of a name —
        # the sweep's kill came from a comment the mutation itself planted.
        assert re.search(r'scenario\["marshals"\]\.items\(\)', body), "the roster must come from the scenario"
        assert "len(french) == 8" in body, "and the count must be pinned"
        assert '"MASSENA"' not in body, "the hard-coded seven is what stayed green with the Emperor missing"
        assert "THE EMPEROR" in body


# ═══════════════════════════════════════════════════════════════════════
# FA-101 — the objection-at-load remainder is ACCEPTED-UNREACHABLE, and the
# argument is measured
# ═══════════════════════════════════════════════════════════════════════

_DEAD_OWNER_PHRASES = ("owner = row WO slice 12", "owned by slice 12", "owner named (slice 12)",
                       "owned by row WO slice 12")


def _names_dead_owner(text: str) -> bool:
    return any(p in text for p in _DEAD_OWNER_PHRASES)


class TestFA101TheObjectionAtLoadIsAcceptedUnreachable:

    FILES = (
        REPO_ROOT / "backend" / "main.py",
        REPO_ROOT / "tests" / "test_wo_slice15_capture_question_holds.py",
        REPO_ROOT / "docs" / "WEIRD_OUTCOMES_SPEC.md",
        REPO_ROOT / "docs" / "BUG_FIXES.md",
    )

    @staticmethod
    def _scope(path, text):
        """BUG_FIXES.md is scoped to the WO-35 row — the FA-101 row itself
        quotes the phrase it asked to strike, and a whole-file grep would
        read the bug's own filing as the bug."""
        if path.name != "BUG_FIXES.md":
            return text
        at = text.index("| **WO-35** |")
        return text[at:text.index("\n", at)]

    def test_no_file_still_names_the_dead_owner(self):
        for path in self.FILES:
            text = self._scope(path, _read(path))
            assert not _names_dead_owner(text), path.name
            assert "ACCEPTED-UNREACHABLE" in text, path.name

    def test_the_census_is_sensitive(self):
        assert _names_dead_owner("… a P3 legibility gap, owner = row WO slice 12.")
        assert not _names_dead_owner("… ACCEPTED-UNREACHABLE (FA-101)")

    def test_the_census_entry_says_so_where_the_census_reads_it(self):
        src = _read(self.FILES[1])
        entry = src[src.index('"pending_objection": "WO-35 remainder'):]
        entry = entry[:entry.index("}")]
        assert "ACCEPTED-UNREACHABLE (FA-101" in entry

    def test_the_turn_cannot_end_and_the_save_verb_is_refused_under_a_standing_objection(
            self, world_1805, client, tmp_path):
        """The measured half of the argument: with a tactical objection
        standing, `end turn` is refused and the turn does not advance (so the
        autosave never runs), and the typed save is refused by the same block
        — the only road to a save carrying the state is a raw POST /save from
        outside the client."""
        world = world_1805
        prior = world.pending_objection
        world.pending_objection = {
            "type": "major_objection", "marshal": "Davout", "message": "Davout objects.",
            "original_order": {"action": "attack", "marshal": "Davout", "target": "Bohemia"},
            "suggested_alternative": None, "alternative": None, "compromise": None,
        }
        turn = world.current_turn
        try:
            r = _post(client, "end turn")
            assert r.get("success") is False, r
            assert "awaits your answer" in str(r.get("message", ""))
            assert world.current_turn == turn
            assert world.pending_objection is not None
            assert not (tmp_path / "saves" / "autosave.json").exists()
            r2 = _post(client, "save game")
            assert r2.get("success") is False and "awaits your answer" in str(r2.get("message", ""))
        finally:
            world.pending_objection = prior
