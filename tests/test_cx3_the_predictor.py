"""CX-3 — THE PREDICTOR, and the drift pin that keeps it honest.

Row CX. Owning spec: `docs/COMMAND_EXPERIENCE_SPEC.md` §3.3 and §5.

TWO THINGS, ONE RULE
====================
The user asked for *"a text predictor, or a way to make it more efficient"*.
What landed is a grammar-aware completion list in the command line plus a
prefix-filtered history — and the rule that makes both safe is the one IQ-10
found the hard way:

    **THE GAME MUST NOT OFFER A SENTENCE IT CANNOT READ.**

IQ10-6 was one instance: the game printed *"gather intelligence on Austria"*
and only `gather intel on` parsed. This file turns that into a census. It
takes every command-shaped string the game OFFERS — the completer's own verb
table, and every phrasing quoted in the COMMAND REFERENCE — fills the slots
with real names from the shipped 1805 board, and runs them through the REAL
parser. A phrasing the game teaches and the parser refuses is a failure here.

It found one immediately, and it is the same shape as IQ10-6: the help text
documents `cancel - "cancel Ney" / "halt Ney" (1 AP)`, and the cancel keyword
list held `"cancel "`, `"halt order"`, `"halt orders"`, `" halt"` and
`", halt"` — **every form except the one the manual prints.**

WHAT THE PREDICTOR IS, AND WHY IT IS THAT SHAPE
===============================================
Measured over the 1,416 archived commands before anything was written, and
two measurements overturned the obvious instinct:

* **Inline ghost text loses on its own numbers.** After three characters the
  top-ranked proposal is the intended command 29.1% of the time and something
  else 63.4%. Wrong two times in three is noise on the one surface the player
  is concentrating on. A short ranked list wins.
* **Raising `MAX_HISTORY` alone makes the feature worse** — each Up press
  costs a keystroke, so a longer unfiltered walk costs more than it saves
  (16.3% at 50 against 14.8% at 10). *Filtered*, the same change is worth
  12.6% → 21.4%. The two findings are only inconsistent if you change one at
  a time, so CX-3 changes both.

And it completes **the slot the player is in**, not the whole line: the
grammar is `<Marshal>, <verb> <target>`, the prefix says which slot you are
in, and the target roster is chosen by the verb. That is why five accurate
lines are possible where five guesses were not.

FOG
===
The completer's only board source is the `/command` response's own
`game_state`, whose `enemies` dict the backend has already fog-filtered, so
nothing it generates can name a hidden corps. History stays SESSION-ONLY and
is deliberately never written to `user://`: 4.7% of the archived commands
name a marshal fogged on the 1805 boot board, and `Ney, attack Archduke
Charles` parses at 0.95 and executes — a persisted history would carry those
names into a campaign that never saw them.
"""

import io
import contextlib
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAIN_GD = REPO / "godot-client" / "project-sovereign" / "scripts" / "main.gd"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def board():
    from backend.ai.parser_eval import build_world, build_llm_game_state
    from backend.commands.parser import CommandParser
    with _quiet():
        world = build_world("1805")
        state = build_llm_game_state(world)
        parser = CommandParser(use_real_llm=False)
    return world, state, parser


def _parse(board, text):
    world, state, parser = board
    with _quiet():
        return parser.parse(text, state, world=world)


def _execute(text):
    """Drive the REAL endpoint on a FRESH board.

    The census runs at the EXECUTOR, not at the parser, because that is where
    the other half of the family lives: the help text also teaches
    `"Davout, hold Ulm"`, which PARSES perfectly and is then refused with
    "Region 'Ulm' not found" — the 126-province map has Swabia, and Ulm is a
    town inside it. A parser-level census would have called that green.
    """
    from fastapi.testclient import TestClient
    from backend.ai.parser_eval import build_world
    from backend.commands.parser import CommandParser
    import backend.main as main_module
    with _quiet():
        world = build_world("1805")
        main_module.world = world
        main_module.game_state = {"world": world}
        main_module.parser = CommandParser(use_real_llm=False)
        return TestClient(main_module.app).post(
            "/command", json={"command": text}).json()


# ═══════════════════════════════════════════════════════════════════════════
# The completer's table, read out of the .gd and driven
# ═══════════════════════════════════════════════════════════════════════════

def _gd_source():
    return MAIN_GD.read_text(encoding="utf-8")


def _gd_table(name):
    """Extract a `const NAME := [ ... ]` array-of-arrays from main.gd.

    ⚠ The close bracket is the one at DEPTH 0. The first draft took
    `source.index("]")`, which closes the FIRST ROW — so it read a one-row
    table, found nothing to complain about, and called a twelve-row table
    green. The mutation would have been inert; the sweep's lesson applied
    before the sweep ran.
    """
    source = _gd_source()
    start = source.index(f"const {name} := [")
    open_at = source.index("[", start)
    depth = 0
    end = None
    for i in range(open_at, len(source)):
        if source[i] == "[":
            depth += 1
        elif source[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    assert end is not None, name
    rows = re.findall(r"\[([^\]]*)\]", source[open_at + 1:end])
    return [[part.strip().strip('"') for part in row.split(",")]
            for row in rows]


def _gd_function(name, until):
    """The BODY of a function with comments and docstring stripped.

    A pin about CODE must not be satisfied by a comment that names the thing
    it forbids — this file's own `CanvasLayer` assertion was, on the first
    run, by the comment explaining why the row is NOT a CanvasLayer. That is
    the project's recurring inert-pin shape and it is cheap to close.
    """
    source = _gd_source()
    body = source[source.index(f"func {name}"):source.index(f"func {until}")]
    # ⚠ Strip triple-quoted blocks WHOLE. A line-by-line toggle keyed on
    # `startswith('"""')` never sees a docstring whose closing quotes sit at
    # the end of a prose line, which is most of them — the first draft
    # swallowed every body it was given and returned the signature alone.
    body = re.sub(r'"""[\s\S]*?"""', "", body)
    out = []
    for line in body.splitlines():
        if line.strip().startswith("#"):
            continue
        out.append(line.split("  #")[0])
    stripped = "\n".join(out)
    assert stripped.count("\n") > 2, (name, "the body came back empty")
    return stripped


class TestTheCompleterOffersNothingItCannotRead:
    """Every line the completer can produce, filled with real names from the
    shipped board and run through the real parser."""

    def test_the_verb_table_is_readable_from_the_gd(self):
        verbs = _gd_table("_MARSHAL_VERBS")
        assert len(verbs) >= 10, verbs
        for verb, slot, action in verbs:
            assert slot in ("", "E", "R", "M"), (verb, slot)
            assert action, verb

    def test_every_marshal_verb_parses_to_the_action_it_claims(self, board):
        world, state, _parser = board
        marshal = "Ney"
        enemy = next(iter(state["enemies"]))
        other = next(name for name in state["marshals"] if name != marshal)
        region = world.get_marshal(marshal).location
        failures = []
        for verb, slot, action in _gd_table("_MARSHAL_VERBS"):
            target = {"": "", "E": enemy, "R": region, "M": other}[slot]
            line = f"{marshal}, {verb}" + (f" {target}" if target else "")
            result = _parse(board, line)
            command = result.get("command") or {}
            if not result.get("success") or command.get("action") != action:
                failures.append((line, result.get("success"),
                                 command.get("action"), action))
        assert not failures, failures

    def test_every_bare_command_parses(self, board):
        failures = []
        for row in _gd_table("_BARE_COMMANDS"):
            line, action = row[0], row[1]
            result = _parse(board, line)
            command = result.get("command") or {}
            if not result.get("success") or command.get("action") != action:
                failures.append((line, result.get("success"),
                                 command.get("action"), action))
        assert not failures, failures

    def test_the_marshal_slot_is_offered_with_the_comma_the_parser_wants(self):
        """The completer emits `"<Marshal>, "` — with the comma — because the
        comma is what binds the addressee. CX-1 measured what happens without
        it: `Nay attack Mack` sent a marshal the player never named into a
        real battle."""
        source = _gd_source()
        assert 'var line := str(name) + ", "' in source, (
            "the addressee completion must carry its comma")


# ═══════════════════════════════════════════════════════════════════════════
# THE DRIFT PIN — every phrasing the game PRINTS must be one it can READ
# ═══════════════════════════════════════════════════════════════════════════

class TestTheGameCanReadWhatItPrints:
    """The IQ10-6 rule as a census over the COMMAND REFERENCE.

    Not every quoted string in that body is a command — it also quotes
    ability names ("Iron Resolve") and display labels — so the census takes
    the phrasings that are quoted BESIDE a documented verb, and any string it
    cannot classify is reported rather than silently skipped.
    """

    # Quoted strings in the help body that are NOT commands, each with the
    # reason it is exempt. An allowlist, so a NEW non-command string fails
    # the census until somebody says what it is.
    NOT_COMMANDS = {
        "Bravest of the Brave", "Child of Victory", "Eyes on a Crown",
        "First Horseman of Europe", "Iron Resolve", "Roland of the Army",
        "Drillmaster of Boulogne",
    }

    @staticmethod
    def _help_body():
        from backend.commands.meta_executor import MetaExecutor
        from backend.ai.parser_eval import build_world
        with _quiet():
            world = build_world("1805")
            return MetaExecutor(None)._execute_help({}, world)["message"]

    def test_the_body_is_reachable_and_substantial(self):
        body = self._help_body()
        assert "COMMAND REFERENCE" in body
        assert len(body) > 5000, len(body)

    def test_every_quoted_phrasing_the_manual_teaches_is_typable(self, board):
        """⚠ This is the pin that found `halt Ney`. The help text documents
        it as the twin of `cancel Ney`, and the cancel keyword list held every
        form of the word EXCEPT that one."""
        body = self._help_body()
        quoted = sorted(set(re.findall(r'"([^"\n]{3,70})"', body)))
        assert len(quoted) > 30, len(quoted)
        failures = []
        for phrase in quoted:
            if phrase in self.NOT_COMMANDS:
                continue
            result = _parse(board, phrase)
            command = result.get("command") or {}
            action = command.get("action")
            if not result.get("success") or action in (None, "unknown"):
                failures.append((phrase, result.get("success"), action))
        assert not failures, failures

    def test_every_quoted_phrasing_survives_the_EXECUTOR(self):
        """Parsing is not enough. `"Davout, hold Ulm"` parses perfectly and
        the executor answers "Region 'Ulm' not found" — the map has Swabia,
        and a parser-level census calls that green."""
        body = self._help_body()
        quoted = sorted(set(re.findall(r'"([^"\n]{3,70})"', body)))
        refusals = ("not found", "cannot parse", "Unknown target",
                    "I cannot interpret", "no such", "eludes me")
        failures = []
        for phrase in quoted:
            if phrase in self.NOT_COMMANDS:
                continue
            message = (_execute(phrase).get("message")
                       or _execute(phrase).get("error") or "")
            for needle in refusals:
                if needle.lower() in message.lower():
                    failures.append((phrase, message[:120]))
                    break
        assert not failures, failures

    def test_the_exemption_list_is_not_a_wildcard(self):
        """Every exempt string must actually BE in the body — an exemption for
        a string nobody prints is an exemption that hides the next one."""
        body = self._help_body()
        missing = [phrase for phrase in self.NOT_COMMANDS
                   if f'"{phrase}"' not in body]
        assert not missing, missing


# ═══════════════════════════════════════════════════════════════════════════
# The history walk
# ═══════════════════════════════════════════════════════════════════════════

class TestTheHistoryWalk:
    """The client half, pinned by reading the source. Each assertion names
    the behaviour rather than a line number.

    ⛔ CX-7 CORRECTION. This docstring used to claim "there is no headless
    way to press Up in this project, and the alternative is no pin at all",
    and the review round refuted it by doing it: the same
    `Viewport.push_input(InputEventKey)` the row already used for Tab reaches
    `_on_command_input_gui_input`, where KEY_UP is handled four lines below
    KEY_TAB. **FOUR confirmed defects were living behind that belief** — the
    board dropped on the ordinary boot path, the completer silent after a
    history recall, two of three offers unreachable by any key, and the row
    rendering at half again the size of the game's prose — and the censuses
    in this file are green about every one of them, because a census can
    only see what is written, not what happens.

    These stay: they are cheap, they run without an engine, and they pin the
    INTENT. The behaviour is pinned by `test_cx7_predictor_driven.py`, which
    drives the real scene with real keys."""

    def test_the_window_was_raised_with_its_reason(self):
        source = _gd_source()
        assert "const MAX_HISTORY = 50" in source
        assert "prefix-filtered" in source

    def test_the_walk_is_filtered(self):
        source = _gd_source()
        assert "func _history_pool() -> Array:" in source
        # ⚠ Scoped to the pool's OWN body. `begins_with(prefix.to_lower())`
        # also appears in `_starts_with_ci`, the completer's helper — so an
        # assertion over the whole file survives deleting the filter here,
        # which is exactly what the mutation sweep reported.
        pool = _gd_function("_history_pool", "_history_previous")
        assert "begins_with(prefix.to_lower())" in pool, pool
        assert "out.append(past)" in pool, pool
        # …and both walks read the pool, not the raw array.
        previous = source[source.index("func _history_previous"):
                          source.index("func _add_to_history")]
        assert "_history_pool()" in previous
        assert "command_history[history_index]" not in previous

    def test_walking_off_the_end_gives_the_typed_prefix_back(self):
        nxt = _gd_function("_history_next", "_add_to_history")
        assert "_history_anchor" in nxt
        assert 'command_input.text = ""' not in nxt, (
            "a filtered walk that blanks the line costs the keystrokes it "
            "just saved")

    def test_history_is_never_persisted(self):
        """The fog rule. A history written to `user://` would carry a
        marshal's name into a campaign that never saw him."""
        source = _gd_source()
        for line in source.splitlines():
            if "command_history" in line and "user://" in line:
                pytest.fail(line)
        assert "_history_anchor" in source


class TestTheCompletionSurface:
    """Where the row draws, and what it refuses to do."""

    def test_it_draws_inside_the_terminal_not_on_a_canvas_layer(self):
        """IQ-10's lesson: a surface authored at a fixed size breaks at
        Interface Scale 2.0. A child of the terminal's own VBox inherits
        `content_scale_factor` by construction rather than by a clamp."""
        install = _gd_function("_install_suggestion_row", "_own_marshal_names")
        assert "CanvasLayer" not in install, install
        assert "layout.add_child(_suggestion_row)" in install
        assert "layout.move_child" in install

    def test_accepting_a_completion_never_sends_it(self):
        """The tutorial's own rule — "NEVER sends a command … muscle memory
        for a typed-command game" — applied to the completer."""
        accept = _gd_function("_accept_suggestion", "_refresh_after_accept")
        assert "send_command" not in accept
        assert "_execute_command" not in accept

    def test_the_enemy_roster_comes_from_the_fog_filtered_payload(self):
        enemies = _gd_function("_visible_enemy_names", "_region_names")
        assert '_last_game_state.get("enemies"' in enemies
        # …and nowhere does the completer reach for a roster of its own.
        assert "get_enemies_of_nation" not in _gd_source()

    def test_escape_closes_the_list_before_it_releases_focus(self):
        source = _gd_source()
        assert "if not _suggestions.is_empty():" in source
        block = source[source.index("elif event.keycode == KEY_ESCAPE:"):]
        block = block[:400]
        assert "_clear_suggestions()" in block
        assert "release_focus" in block

    def test_tab_is_the_accept_key_and_was_free(self):
        """`KEY_TAB` was handled only with `alt_pressed` before CX-3, so
        nothing was taken from the player to make room for it."""
        source = _gd_source()
        assert "elif event.keycode == KEY_TAB and _accept_suggestion():" in source
        assert "KEY_TAB, KEY_QUOTELEFT:" in source, (
            "the Alt+Tab terminal toggle must survive")
