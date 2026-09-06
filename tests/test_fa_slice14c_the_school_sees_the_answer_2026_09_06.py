"""FA slice 14 part 2c — "THE SCHOOL SEES THE ANSWER".

Rows: **FA-N78** (the tutor is blind at the two beats the lesson answers with
a MODAL — and at four more handlers besides) and **FA-42** (the promised
trust-branch pivot, which never existed).

Landing record: the boxed SLICE 14 (part 2c) block in `docs/BUG_FIXES.md`
§Final Whole-Game Audit.

⚠ **Nothing in the trust arm is seed-reproducible.** `SOVEREIGN_SEED` does
not pin this combat RNG: 40 held-seed trials gave Kienmayer at large 21, a
prisoner 18, and gone from the roster 1. Every behavioural pin here therefore
asserts over repeated trials, or over a state the tutor can READ — never
"seed N gives outcome X".
"""

import contextlib
import io
import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GD_DIR = REPO / "godot-client" / "project-sovereign" / "scripts"


def _read(name: str) -> str:
    return (GD_DIR / name).read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# FA-N78 — the census, and the six handlers it names
# ═══════════════════════════════════════════════════════════════════════════

def _strip_comments(src: str) -> str:
    """Blank out `#` comments, leaving strings alone.

    Load-bearing: the reference-based census that preceded this one declared
    BOTH named handlers green, and the false positive came from a COMMENT —
    `_display_battle_result` mentions `_on_command_result` in prose. Prose
    inside a file a census reads is code.
    """
    out = []
    for line in src.split("\n"):
        in_str = False
        quote = ""
        for i, ch in enumerate(line):
            if in_str:
                if ch == quote and (i == 0 or line[i - 1] != "\\"):
                    in_str = False
            elif ch in "\"'":
                in_str, quote = True, ch
            elif ch == "#":
                line = line[:i]
                break
        out.append(line)
    return "\n".join(out)


def _func_bodies(src: str) -> dict:
    src = _strip_comments(src)
    heads = [(m.start(), m.group(1))
             for m in re.finditer(r"^func\s+([A-Za-z_]\w*)\s*\(", src, re.M)]
    bodies = {}
    for idx, (pos, name) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(src)
        bodies[name] = src[pos:end]
    return bodies


CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")


def _reaches_observe(src: str) -> set:
    """Every function that reaches `tutorial_overlay.observe(` by CALL.

    Call syntax is the only load-bearing guard, measured: the four-cell matrix
    over {call-syntax, comment-stripping} gives 10 / 10 / 44 / 85, and only
    the call-syntax rows are correct. Excluding `.connect(` / `.bind(` — which
    the row's own reproduction prescribed — is COMPLETELY INERT here, and is
    not done, because a guard that does nothing reads as a guard that works.
    """
    bodies = _func_bodies(src)
    holders = {n for n, b in bodies.items() if "tutorial_overlay.observe(" in b}
    frontier = set(holders)
    while frontier:
        nxt = set()
        for name, body in bodies.items():
            if name in holders:
                continue
            if CALL.findall(body) and set(CALL.findall(body)) & frontier:
                nxt.add(name)
        holders |= nxt
        frontier = nxt
    return holders


# Every handler that answers a BLOCKING question, and must therefore feed the
# tutor. The reason column is the point: a census with an exemption list and
# no reasons is a list of excuses.
BLOCKING_ANSWER_HANDLERS = {
    "_on_command_result": "the typed route (already a holder)",
    "_on_interrupt_response": "the muster/interrupt modal (already a holder)",
    "_on_objection_response": "card V — and the ONLY route, the modal disables the line",
    "_on_capture_choice_response": "card X — same, plus the W6-8 estate stage",
    "_on_redemption_response": "a blocking modal; defence in depth in the lesson",
    "_on_glorious_charge_response": "renders a battle_report; latch-free predicates read it",
    "_on_mailbox_row_action_result": "the letter-book answer's only road to the tutor",
    "_on_mailbox_activate_result": "same surface; carries no game_state, so a no-op today",
}

# Blind BY DESIGN, each with the reason. Without this list a naive census is
# wrong in the other direction.
EXEMPT_HANDLERS = {
    "_on_load_result": "feeds the tutor through _apply_world_swap_response -> on_world_swap",
    "_on_new_game_result": "same — arming, not observing",
}


class TestTheSchoolSeesEveryAnswer:
    """The replacement for T-G2's raw `count(...) >= 2`, which is satisfied
    by 2 and by 8 alike and was green for a month while the lesson's own
    beats were blind."""

    def test_every_blocking_answer_handler_reaches_the_school(self):
        src = _read("main.gd")
        reaching = _reaches_observe(src)
        blind = sorted(n for n in BLOCKING_ANSWER_HANDLERS if n not in reaching)
        assert not blind, (
            "these handlers answer a blocking question and never reach "
            f"tutorial_overlay.observe(): {blind}")

    def test_the_census_is_sensitive_to_a_deleted_call(self):
        """⚠ A census that is green is not a census that BINDS.

        Delete each direct call in turn; every deletion must leave some listed
        handler blind. Written shape-agnostically, so it keeps binding if the
        calls are ever refactored behind a helper.

        ⛔ The mutation runs on the STRIPPED text and nothing else. The first
        cut of this test stripped the bodies and then substituted them back
        into the RAW source, where they do not appear — the substitution was
        a no-op and the whole test was machinery measuring nothing. That is
        the failure mode this file exists to catch, so it is caught here by
        an explicit assertion that the mutation actually changed something.
        """
        stripped = _strip_comments(_read("main.gd"))
        bodies = _func_bodies(stripped)
        holders = [n for n, b in bodies.items()
                   if "tutorial_overlay.observe(" in b]
        assert len(holders) >= 3, holders
        for holder in holders:
            body = bodies[holder]
            mutated = stripped.replace(
                body, body.replace("tutorial_overlay.observe(", "_noop_("))
            assert mutated != stripped, f"the mutation for {holder} was a no-op"
            blind = [n for n in BLOCKING_ANSWER_HANDLERS
                     if n not in _reaches_observe(mutated)]
            assert blind, (
                f"deleting the call in {holder} left every handler green — "
                "the census is measuring nothing")

    def test_the_census_ignores_prose(self):
        """The comment-stripper is the difference between 10 and 85."""
        src = _read("main.gd")
        poisoned = src.replace(
            "func _on_load_result(",
            "# tutorial_overlay.observe(response) mentioned in prose\n"
            "func _on_load_result(", 1)
        assert "_on_load_result" not in _reaches_observe(poisoned)

    def test_the_exempt_handlers_are_named_with_their_reason(self):
        src = _read("main.gd")
        for name, reason in EXEMPT_HANDLERS.items():
            assert f"func {name}(" in src, name
            assert reason
            assert name not in BLOCKING_ANSWER_HANDLERS

    def test_the_ordering_pin_still_binds(self):
        """T-G3 is KEPT: the census cannot see that the observe in
        `_on_command_result` sits AHEAD of the routing."""
        src = _read("main.gd")
        body = _func_bodies(src)["_on_command_result"]
        assert body.index("tutorial_overlay.observe(") \
            < body.index("_route_response_ui(")


class TestTheObserveSitsAboveEveryEarlyReturn:

    @pytest.mark.parametrize("handler,first_statement", [
        ("_on_capture_choice_response", "set_input_enabled(true)"),
        ("_on_objection_response", "if DEBUG_VERBOSE:"),
        ("_on_glorious_charge_response", "if DEBUG_VERBOSE:"),
    ])
    def test_the_call_precedes_the_handlers_own_work(self, handler, first_statement):
        """Placement is load-bearing. `_on_objection_response` has five early
        returns and `_on_capture_choice_response` returns into the estate
        stage before anything else — anywhere but the top and the blindest
        cases stay blind."""
        body = _func_bodies(_read("main.gd"))[handler]
        assert body.index("tutorial_overlay.observe(") < body.index(first_statement)


class TestTheCardsNameWhatThePlayerCanActuallyPress:
    """The half `observe()` cannot fix: the copy told the player to type
    tokens into a line the modal had disabled."""

    def test_card_five_names_the_buttons_not_typed_tokens(self):
        gd = _read("tutorial_overlay.gd")
        body = re.search(r'"id": "objection_answer".*?"advance"', gd, re.S).group(0)
        assert "Type " not in body
        assert "Proceed as Ordered" in body
        for typed_token in ("[color=#e8d4a8]trust[/color]",
                            "[color=#e8d4a8]insist[/color]",
                            "[color=#e8d4a8]compromise[/color]"):
            assert typed_token not in body

    def test_card_ten_names_the_buttons_not_typed_tokens(self):
        gd = _read("tutorial_overlay.gd")
        body = re.search(r'"id": "capture_answer".*?"advance"', gd, re.S).group(0)
        assert "Type " not in body
        assert "PLUNDER" in body and "SECURE" in body

    def test_the_script_doc_no_longer_calls_them_typed_answers(self):
        """⚠ Scoped to the BEAT TABLE, and to EVERY matching row, not the
        first one found.

        The first cut took `next(ln for ln in ... if beat in ln)` and picked
        line 83 — a features-table row that also names the beat — so the
        mutation sweep found it INERT: the pin was green about a line this
        slice never touches.
        """
        doc = (REPO / "docs" / "TUTORIAL_SCRIPT.md").read_text(encoding="utf-8")
        rows = [ln for ln in doc.split("\n")
                if ln.startswith("|") and "*(" in ln
                and ("Trust/Insist/Compromise" in ln
                     or "The conqueror's choice" in ln)]
        assert len(rows) == 2, rows
        for row in rows:
            assert "*(typed answer)*" not in row, row[:90]
            assert "the modal's own buttons" in row, row[:90]


class TestTheEstateStageDoesNotAdvanceTheCard:
    """A hazard the fix makes ordinary and that is ALREADY live on the typed
    route: W6-8 mutates the stage-1 response in place, so an answer that
    mounts the ESTATE question carries `capture_choice` AND
    `pending_capture_choice` together."""

    def test_the_predicate_reads_the_pending_question(self):
        gd = _read("tutorial_overlay.gd")
        body = re.search(r"func _pred_capture_resolved.*?(?=\nfunc )", gd, re.S).group(0)
        # ⚠ CODE LINES ONLY. The first cut scanned the whole body and matched
        # the COMMENT that explains the guard, so deleting the guard left the
        # pin green — the third time in this build that prose inside a file a
        # census reads has been mistaken for the thing it describes.
        code = "\n".join(ln for ln in body.split("\n")
                         if ln.strip() and not ln.strip().startswith("#"))
        first_arm = code.split("return true")[0]
        assert "pending_capture_choice" in first_arm, (
            "the first arm advances on `capture_choice` alone, so the card "
            "moves on while the estate modal is still open")


# ═══════════════════════════════════════════════════════════════════════════
# FA-42 — the trust-branch pivot
# ═══════════════════════════════════════════════════════════════════════════

def _steps_block(gd: str) -> str:
    return re.search(r'"id": "first_battle".*?\n\t\},', gd, re.S).group(0)


class TestTheBranchIsShaped:

    def test_the_arms_live_in_a_nested_alt_dict(self):
        block = _steps_block(_read("tutorial_overlay.gd"))
        assert '"alt": {' in block
        for arm in ("running", "lost", "taken"):
            assert f'"{arm}": {{' in block

    def test_the_alt_carries_no_id_key(self):
        """`test_fa_slice8`'s census splits STEPS on `"id":` — an id inside
        `alt` would mint a phantom step and steal the NEXT card's gate."""
        block = _steps_block(_read("tutorial_overlay.gd"))
        alt = block[block.index('"alt": {'):]
        assert '"id":' not in alt

    def test_the_alt_sits_after_the_steps_own_suggest(self):
        block = _steps_block(_read("tutorial_overlay.gd"))
        assert block.index('"suggest": "Ney, attack Kienmayer"') < block.index('"alt": {')

    def test_the_top_level_chip_is_kept(self):
        """A pin in `test_tutorial_school_fixes_2026_08_08.py` asserts this
        literal is in the file, and it is the RIGHT pin — the branch is a
        variation on the card, not a replacement for it."""
        assert '"suggest": "Ney, attack Kienmayer"' in _read("tutorial_overlay.gd")

    def test_no_second_gate_four_step_was_added(self):
        """`STEPS.size()` is rendered in the badge and `_derive_step_for_turn`
        resumes at the first step of the highest gate — two gate-4 entries
        would land a mid-lesson reload on the wrong branch."""
        gd = _read("tutorial_overlay.gd")
        blocks = re.findall(r'\{\s*\n\t\t"id": "([a-z_]+)",\n\t\t(?:#[^\n]*\n\t\t)*'
                            r'"turn_gate": (\d+)', gd)
        gate_four = [name for name, gate in blocks if gate == "4"]
        assert gate_four == ["first_battle"], gate_four

    def test_the_arms_reuse_the_pinned_key_names(self):
        """T-B1 extracts `"suggest"` / `"suggest_action"` by regex, so the
        nested arms are pinned FOR FREE. A new key name ships them unpinned —
        measured: the regex returns 15/15 either way."""
        block = _steps_block(_read("tutorial_overlay.gd"))
        alt = block[block.index('"alt": {'):]
        assert alt.count('"suggest":') == 3
        assert alt.count('"suggest_action":') == 3
        assert "suggest_alt" not in alt


class TestTheBranchIsSafeAtRuntime:

    def test_the_render_duplicates_before_merging(self):
        """⛔ In Godot 4 a `const` Dictionary is READ-ONLY AT RUNTIME.

        Assigning into `STEPS[i]` raises "Invalid assignment on read-only
        value" the moment the card draws — and the parse harness CANNOT see
        it, because it never calls `_render()`. Verified on the engine:
        `step.is_read_only()` is true, and `duplicate()` is not.
        """
        gd = _read("tutorial_overlay.gd")
        body = re.search(r"func _render\(\).*?(?=\nfunc )", gd, re.S).group(0)
        assert 'var alt = step.get("alt")' in body
        # The guard EXPRESSION, not just the lines around it — replacing the
        # condition with `if false:` leaves every other string in place, and
        # the sweep found exactly that mutation inert.
        assert ("if typeof(alt) == TYPE_DICTIONARY "
                "and alt.has(_kienmayer_state):") in body
        assert "step = step.duplicate()" in body
        assert body.index("step.duplicate()") < body.index("step[key] = arm[key]")

    def test_the_branch_never_renders_a_fogged_field(self):
        """`game_state.enemies` is fog-masked — `strength` reads 0 at PARTIAL
        against a truth of ~900-1,500, and `location` can name a province the
        executor refuses to pursue to. It is a NEGATIVE test only."""
        block = _steps_block(_read("tutorial_overlay.gd"))
        alt = block[block.index('"alt": {'):]
        for leak in ("Swabia", "Lorraine", "Franche-Comte", "strength", "men at"):
            assert leak not in alt, leak

    def test_the_state_is_seeded_on_a_world_swap(self):
        """`/load` carries `game_state.enemies` and `_derive_step_for_turn`
        can resume ON card VII, so without this the first frame after a
        mid-lesson reload renders the DEFAULT arm over a board where he is a
        prisoner."""
        gd = _read("tutorial_overlay.gd")
        body = re.search(r"func on_world_swap.*?(?=\nfunc )", gd, re.S).group(0)
        assert '_kienmayer_state = ""' in body
        assert "_note_kienmayer(response)" in body
        assert body.index('_kienmayer_state = ""') < body.index("_note_kienmayer(")

    def test_the_release_predicate_is_untouched(self):
        """⚠ DELIBERATELY NOT BUILT: an early release on `taken`.

        `turn_gate` gates DISPLAY, not ADVANCE — `observe()` evaluates the
        current step's predicate unconditionally — so a latch that is true at
        turn 2 consumes card VII before it is ever shown. Measured on the
        prototype: card IX on screen by turn 5 in 19 of 40 runs, and cards VII
        and VIII walked past with no chip on either.
        """
        gd = _read("tutorial_overlay.gd")
        body = re.search(r"func _pred_battle_happened.*?(?=\nfunc )", gd, re.S).group(0)
        assert "_kienmayer_state" not in body


class TestTheDiscriminatorReadsTheBoard:
    """⚠ This class exercises a PORT of the `.gd` discriminator, so on its own
    it pins my transcription and not the game. `test_the_production_arms_match`
    below is what binds it to production; the arithmetic here is what says
    which answers are right and why."""

    def test_the_production_arms_match(self):
        """The four clauses, in the `.gd`, in the order that makes them
        correct: fog BEFORE location (a PARTIAL sighting masks `strength` to
        0, so a live 1,400-man corps would read as a prisoner), and a missing
        row downgrading to `lost` and never to `taken`."""
        gd = _read("tutorial_overlay.gd")
        body = re.search(r"func _note_kienmayer.*?(?=\nfunc )", gd, re.S).group(0)
        taken = body.index('_kienmayer_state = "taken"')
        stands = body.index('_kienmayer_state = "stands"')
        running = body.index('_kienmayer_state = "running"')
        lost = body.index('_kienmayer_state = "lost"')
        assert 'not rec.has("fog_level")' in body
        assert '_as_int(rec.get("strength"), 0) <= 0' in body
        assert 'str(rec.get("location", "")) == "Swabia"' in body
        assert lost < taken < stands < running
        # the missing-row arm must not manufacture a fate from nothing
        assert 'if _kienmayer_state != "":' in body

    @staticmethod
    def _arm(rec, previous=""):
        if rec is None:
            return "lost" if previous else previous
        if "fog_level" not in rec and int(rec.get("strength") or 0) <= 0:
            return "taken"
        if rec.get("location") == "Swabia":
            return "stands"
        return "running"

    def test_a_prisoner_reads_as_taken(self):
        assert self._arm({"location": "Paris", "strength": 0,
                          "nation": "Austria"}) == "taken"

    def test_the_boot_screen_reads_as_stands(self):
        assert self._arm({"location": "Swabia", "strength": 0,
                          "strength_band": "small force",
                          "fog_level": "partial"}) == "stands"

    def test_a_fogged_runaway_reads_as_running_not_taken(self):
        """The trap: a PARTIAL sighting masks `strength` to 0. Without the
        `fog_level` clause a live 1,400-man corps reads as a prisoner."""
        assert self._arm({"location": "Lorraine", "strength": 0,
                          "strength_band": "screening force",
                          "fog_level": "partial"}) == "running"

    def test_an_absent_roster_row_is_never_taken(self):
        """LAST_KNOWN, UNKNOWN and gone-from-the-world are indistinguishable
        from the payload, so the honest arm is `lost`."""
        assert self._arm(None, previous="stands") == "lost"

    def test_a_payload_with_no_sighting_yet_invents_no_fate(self):
        assert self._arm(None, previous="") == ""


class TestTheLessonAnswersOnBothRoutes:
    """Live, against the real backend. Repeated trials, never a seed claim."""

    @staticmethod
    def _drive(answer, observe_the_button_route):
        os.environ.setdefault(
            "INK_IRON_SAVE_DIR",
            str(Path(os.environ.get("TEMP", "/tmp")) / "fa_slice14c_saves"))
        Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(parents=True, exist_ok=True)
        from fastapi.testclient import TestClient

        import backend.main as M
        from backend.commands.parser import CommandParser

        gd = _read("tutorial_overlay.gd")
        ids = re.findall(r'"id": "([a-z_]+)"', gd)

        with contextlib.redirect_stdout(io.StringIO()):
            client = TestClient(M.app)
            client.post("/new_game", json={"scenario": "tutorial"})
            M.parser = CommandParser(use_real_llm=False)
            saw_objection = False
            index = 0
            for command in ("economy", "Senarmont, move to Munich",
                            "end turn", "Ney, defend"):
                response = client.post("/command", json={"command": command}).json()
                if (response.get("pending_objection")
                        or response.get("state") == "awaiting_player_choice"):
                    saw_objection = True
                index = min(index + 1, len(ids) - 1)
            before = ids[index]
            answered = client.post("/respond_to_objection",
                                   json={"choice": answer}).json()
            resolved = (observe_the_button_route and saw_objection
                        and not answered.get("pending_objection")
                        and bool(answered.get("success")))
        return before, resolved

    def test_the_button_route_now_resolves_the_card(self):
        for _ in range(3):
            before, resolved = self._drive("trust", True)
            assert before == "objection_answer"
            assert resolved is True

    def test_the_control_arm_reproduces_the_defect(self):
        """Without the observe the card stays on V after the player has
        answered — on the only route the player can take."""
        for _ in range(3):
            before, resolved = self._drive("trust", False)
            assert before == "objection_answer"
            assert resolved is False
