"""Row REV's open follow-ups, closed (Aug 31, 2026).

The Aug 30 whole-systems review left four items on `docs/REV_FOLLOWUPS.md`,
each with the reason it was left rather than fixed. This file pins the two
that are code:

* **REV-F1** — `battles_this_turn` wiped on load. Filed PLAUSIBLE because one
  adversarial refuter confirmed the mechanism and the other called the
  consequence masked by another guard. Settled by EXPERIMENT, through the
  typed command path, on five seeds: nothing masks it.
* **REV-V3** — the notice rail's unmapped tail. 33 of the backend's 57
  notification types had no renderer join and arrived as the anonymous
  priority pill. The floor pin the review left behind is replaced here by a
  full census: every type is either joined or in a documented exempt set.

Method note kept from the review round: a source-substring pin must never
read the prose written to explain its own fix, so every structural assertion
here goes through `_code_only`.
"""

import contextlib
import io
import os
import random
import tempfile
from pathlib import Path

import pytest

from backend import save_manager
from backend.commands.executor import CommandExecutor
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState


def _read(path):
    return io.open(path, encoding="utf-8").read()


def _code_only(text: str) -> str:
    """`text` with comments and docstrings removed — see the note in
    `tests/test_review_2026_08_30.py`. Five pins in that file were INERT on
    their first mutation sweep for exactly one reason: they read the comment
    that explains the fix."""
    import io as _io
    import tokenize
    out = []
    try:
        for tok in tokenize.generate_tokens(_io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING and tok.line.strip().startswith(
                    ('"""', "'''", 'r"""')):
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return chr(10).join(out)


def _code_norm(text: str) -> str:
    """`_code_only` with all whitespace squeezed out.

    `_code_only` returns one token per line, so a multi-token needle like
    `world.battles_this_turn = []` never matches it — a trap of exactly the
    shape the helper exists to prevent, since the pin would read as passing.
    Squeeze both sides and compare.
    """
    import re
    return re.sub(r"\s+", "", _code_only(text))


def _code_only_gd(text: str) -> str:
    """GDScript with `#` comments stripped, quotes respected.

    Same lesson as `_code_only`, different language: `main.gd`'s fixes each
    carry a comment naming the expression they added, so a bare substring
    scan finds the prose and passes with the code deleted. A blunt
    `line.split("#")` would also eat every colour literal in the file.
    """
    out = []
    for line in text.splitlines():
        quote = ""
        cut = len(line)
        for index, char in enumerate(line):
            if quote:
                if char == quote:
                    quote = ""
            elif char in (chr(34), chr(39)):
                quote = char
            elif char == "#":
                cut = index
                break
        out.append(line[:cut])
    return chr(10).join(out)


# ══════════════════════════════════════════════════════════════════════════
# REV-F1 — the battle record survives a mid-turn save/load
# ══════════════════════════════════════════════════════════════════════════


def _charge_world():
    """Ney (reckless cavalry) beside Wellington, one turn into a war.

    Recklessness 2 is carried from an EARLIER turn — the ordinary case: it
    persists, resetting only on an attacking loss or on a charge. At 2 he
    clears `_execute_charge`'s `>= 1` gate without tripping the recklessness-3
    charge popup.
    """
    world = WorldState()
    world.marshals.clear()
    ney = Marshal(name="Ney", location="Belgium", strength=60000,
                  personality="aggressive", nation="France", cavalry=True,
                  movement_range=2, spawn_location="Paris")
    ney.recklessness = 2
    world.marshals["Ney"] = ney
    world.marshals["Wellington"] = Marshal(
        name="Wellington", location="Waterloo", strength=45000,
        personality="cautious", nation="Britain", spawn_location="Netherlands")
    world.marshals["Blucher"] = Marshal(
        name="Blucher", location="Rhineland", strength=30000,
        personality="aggressive", nation="Prussia", spawn_location="Berlin")
    world.action_points = 10
    # the once-per-campaign opening briefing, already seen
    world.opening_attack_guidance_shown = True
    return world


def _issue(executor, world, action, marshal, target):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return executor.execute(
            {"command": {"action": action, "marshal": marshal,
                         "target": target}}, {"world": world})


def _roundtrip(world):
    """Through the production save format and `load_game` — not `from_dict`.
    The clear under test lived in `load_game`, so a `to_dict`/`from_dict`
    round trip would have passed while the game was still broken."""
    handle, path = tempfile.mkstemp(suffix=".json")
    os.close(handle)
    try:
        save_manager.save_game(world, "REV-F1", filepath=Path(path))
        result = save_manager.load_game(Path(path))
    finally:
        os.unlink(path)
    assert result["success"], result["message"]
    return result["world"]


class TestTheChargeGateSurvivesAMidTurnReload:
    """V2-2 refuses a second engagement of the same pair in one turn, and the
    list it reads was force-cleared by `load_game`.

    Measured, five seeds, byte-identical per seed: attack to a stalemate,
    charge -> refused. Save, reload, charge -> the full 2x-damage GLORIOUS
    CHARGE lands. Every other gate on the path (cavalry, aggressive,
    recklessness, AP, range, terrain, the naval crossing) survives the round
    trip, so the refuter's "masked by another guard" does not hold.
    """

    @staticmethod
    def _attack_then(executor, world):
        random.seed(1)
        attack = _issue(executor, world, "attack", "Ney", "Wellington")
        assert attack.get("success") is True
        assert world.battles_this_turn, "the attack must record the battle"
        assert world.get_marshal("Wellington").strength > 0
        assert world.get_marshal("Ney").recklessness >= 1
        return world

    def test_the_control_arm_refuses(self):
        """The gate is live at all — without this, the pin below could pass
        because the charge was impossible for some unrelated reason."""
        executor = CommandExecutor()
        world = self._attack_then(executor, _charge_world())
        result = _issue(executor, world, "charge", "Ney", "Wellington")
        assert result.get("success") is False
        assert "already engaged" in result.get("message", "")

    def test_the_reloaded_arm_refuses_too(self):
        """THE pin. Fails the moment `load_game` clears the record again."""
        executor = CommandExecutor()
        world = _roundtrip(self._attack_then(executor, _charge_world()))
        result = _issue(executor, world, "charge", "Ney", "Wellington")
        assert result.get("success") is False, (
            "a mid-turn save/load bought a second GLORIOUS CHARGE on a pair "
            "already engaged this turn")
        assert "already engaged" in result.get("message", "")

    def test_a_different_enemy_is_still_chargeable_after_a_reload(self):
        """The negative control: the fix restores the record, it does not
        disable the charge."""
        executor = CommandExecutor()
        world = _roundtrip(self._attack_then(executor, _charge_world()))
        world.get_marshal("Blucher").location = "Belgium"
        random.seed(2)
        result = _issue(executor, world, "charge", "Ney", "Blucher")
        assert "already engaged" not in (result.get("message") or "")

    def test_the_record_itself_crosses_the_save(self):
        executor = CommandExecutor()
        before = self._attack_then(executor, _charge_world())
        after = _roundtrip(before)
        assert [dict(b) for b in after.battles_this_turn] == \
               [dict(b) for b in before.battles_this_turn]


class TestTheNonClearIsDocumentedWhereItLives:
    def _block(self):
        src = _read("backend/save_manager.py")
        body = src[src.index("# Clear transient per-turn data"):]
        return body[:body.index("world.threat_sources_this_turn")]

    def test_load_game_no_longer_wipes_the_battle_record(self):
        assert "world.battles_this_turn=[]" not in _code_norm(self._block())

    def test_the_fields_that_should_still_be_cleared_still_are(self):
        """The flip is scoped: two transient stores keep being wiped."""
        code = _code_norm(self._block())
        assert "world.mild_concerns_this_turn=[]" in code
        assert "world.gold_spent_this_turn={}" in code

    def test_the_contract_the_non_clear_cites_is_real(self):
        """It is only safe to keep the record because the REAL turn boundary
        empties it. Falsifiable: if `clear_turn_battles` stopped clearing,
        a loaded save would carry a stale record forever."""
        world = WorldState()
        world.record_battle("Belgium", "Ney", "Wellington", "stalemate")
        assert world.battles_this_turn
        world.clear_turn_battles()
        assert world.battles_this_turn == []


# ══════════════════════════════════════════════════════════════════════════
# REV-V3 — the notice rail names every row it shows
# ══════════════════════════════════════════════════════════════════════════

RAIL = "godot-client/project-sovereign/scripts/notification_bar.gd"
PHOSPHOR = os.path.join(
    "godot-client", "project-sovereign", "assets", "ui", "icons", "phosphor")

# The three dynamic producers — call sites whose notification TYPE is a
# variable, resolved below from the backend's own tables rather than guessed.
# This allowlist is the anti-drift device: a NEW dynamic producer lands here
# unresolved and fails `test_no_unknown_dynamic_producer`, which forces the
# next author to teach the census how to read it instead of slipping past.
KNOWN_DYNAMIC_SITES = {
    ("diplomacy.py", "_emit_bargain_notification"),
    ("diplomacy.py", "_emit_commitments_notification"),
    ("settlement_reactions.py", "_queue_settlement_notification"),
}

# Mapped, but no producer can ever emit them: they are COMMITMENTS_ROUTES
# *event* keys, and the routing layer either rewrites the type on the way out
# (`diplomatic_treaty_broken` ships as `treaty_broken`) or never makes a
# notification of them at all. Harmless rows — but pinned, so a typo'd key
# cannot join the maps unnoticed.
ROUTE_ONLY_MAP_KEYS = {
    "bargain_ratified", "bargain_triggered", "commitment_paradox",
    "commitment_paradox_resolved", "diplomatic_treaty_broken",
    "witness_strike_recorded",
}


def _gd_map(head):
    """Parse one GDScript `const NAME = { ... }` block into a dict.

    Line-wise to the first bare `}` — `src.index("}", i)` would stop at the
    first brace inside a COMMENT, which is exactly the kind of accident this
    census exists to catch.
    """
    import re
    lines = _read(RAIL).splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(head))
    out = {}
    for line in lines[start + 1:]:
        if line.strip() == "}":
            break
        found = re.match(r'\s*"([a-z0-9_]+)"\s*:\s*"([A-Za-z0-9\-]+)"\s*,', line)
        if found:
            out[found.group(1)] = found.group(2)
    return out


def _producible_types():
    """Every notification type any backend producer can emit.

    Derived from the backend — an AST walk over every `create_notification`
    call plus the two commitments/bargain emit seams and the settlement route
    table — never from strings typed here. A rename on the producer side
    therefore breaks this census instead of silently un-joining the rail.
    """
    import ast
    import glob
    from backend.game_logic.settlement_presentation import SETTLEMENT_ROUTES
    import backend.notifications as notifications

    consts = {k: v for k, v in vars(notifications).items()
              if k.isupper() and isinstance(v, str)}

    def resolve(node, local_strings):
        if isinstance(node, ast.Tuple) and node.elts:
            node = node.elts[0]
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return local_strings.get(node.id) or consts.get(node.id)
        if isinstance(node, ast.Attribute):
            return consts.get(node.attr)
        return None

    types, unresolved = set(), set()
    for path in sorted(glob.glob("backend/**/*.py", recursive=True)):
        tree = ast.parse(_read(path))
        local_strings = {
            target.id: node.value.value
            for node in tree.body if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            for target in node.targets if isinstance(target, ast.Name)
        }
        parents = {child: parent for parent in ast.walk(tree)
                   for child in ast.iter_child_nodes(parent)}

        def enclosing(node):
            cursor = parents.get(node)
            while cursor is not None:
                if isinstance(cursor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return cursor.name
                cursor = parents.get(cursor)
            return "<module>"

        base = os.path.basename(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and \
                    node.name == "_emit_bargain_notification":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Dict):
                        for value in sub.values:
                            got = resolve(value, local_strings)
                            if got:
                                types.add(got)
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or \
                getattr(node.func, "id", None)
            if name == "create_notification":
                arg = next((kw.value for kw in node.keywords
                            if kw.arg == "notification_type"), None)
                if arg is None and node.args:
                    arg = node.args[0]
                got = resolve(arg, local_strings) if arg is not None else None
                (types.add(got) if got
                 else unresolved.add((base, enclosing(node))))
            elif name == "_emit_commitments_notification" and len(node.args) >= 2:
                got = resolve(node.args[1], local_strings)
                (types.add(got) if got
                 else unresolved.add((base, enclosing(node))))

    types |= {key for key, route in SETTLEMENT_ROUTES.items()
              if route.get("rail_spotlight") == "yes"}
    return types, unresolved


class TestTheRailNamesEveryRowItShows:
    """The full census the Aug 30 review left as a floor.

    That round pinned nine known-good rows and said in its own docstring that
    33 types were still unmapped, because choosing 33 glyphs and 33 codes is a
    content decision. This is the census: every type a producer can emit is
    joined in BOTH maps, or stands in `notifications.RAIL_EXEMPT_TYPES` with
    a reason.
    """

    def test_every_producible_type_has_a_label_and_a_glyph(self):
        producible, _ = _producible_types()
        labels = _gd_map("const TYPE_ICONS = {")
        glyphs = _gd_map("const TYPE_ICON_SVGS = {")
        assert not producible - set(labels), (
            "these arrive as the anonymous priority pill: "
            + repr(sorted(producible - set(labels))))
        assert not producible - set(glyphs), (
            "label without a glyph is a half-join: "
            + repr(sorted(producible - set(glyphs))))

    def test_the_two_maps_are_keyed_identically(self):
        """The half-join guard, stated once rather than per row."""
        assert set(_gd_map("const TYPE_ICONS = {")) == \
            set(_gd_map("const TYPE_ICON_SVGS = {"))

    def test_the_exempt_set_is_exactly_what_no_producer_emits(self):
        """Both directions. A type in the exempt set that acquires a producer
        fails here, and so does a producible type left out of the maps — so
        reviving one means joining the rail in the same commit."""
        from backend.notifications import RAIL_EXEMPT_TYPES
        import backend.notifications as notifications
        producible, _ = _producible_types()
        declared = {v for k, v in vars(notifications).items()
                    if k.isupper() and isinstance(v, str) and v == k.lower()}
        assert declared - producible == set(RAIL_EXEMPT_TYPES)

    def test_every_exempt_type_carries_its_reason(self):
        from backend.notifications import RAIL_EXEMPT_TYPES
        assert RAIL_EXEMPT_TYPES
        for ntype, reason in RAIL_EXEMPT_TYPES.items():
            assert len(reason) > 40, ntype

    def test_no_unknown_dynamic_producer(self):
        """The census resolves three variable-typed producers from the
        backend's own tables. A fourth must not appear unnoticed."""
        _, unresolved = _producible_types()
        assert unresolved == KNOWN_DYNAMIC_SITES

    def test_no_map_key_is_a_type_nothing_can_emit(self):
        """Catches a typo'd join. The only legitimate residents are the six
        COMMITMENTS_ROUTES event keys the routing layer never ships as a
        notification type."""
        producible, _ = _producible_types()
        assert set(_gd_map("const TYPE_ICONS = {")) - producible == \
            ROUTE_ONLY_MAP_KEYS

    def test_the_glyphs_named_exist_on_disk(self):
        """A glyph name with no SVG renders nothing — worse than the pill it
        replaced. (The review's own copy of this pin covered 32 rows; this one
        covers all 66.)"""
        for glyph in set(_gd_map("const TYPE_ICON_SVGS = {").values()):
            assert os.path.exists(os.path.join(PHOSPHOR, glyph + ".svg")), glyph

    def test_no_label_is_the_priority_default_it_replaces(self):
        """INF / NEW / ALT are what an UNJOINED row shows. A join that spells
        one of them is a join that changed nothing."""
        for ntype, label in _gd_map("const TYPE_ICONS = {").items():
            assert label not in ("INF", "NEW", "ALT"), ntype

    def test_the_new_constants_are_the_backends_own(self):
        """The three types this round found had always shipped as bare string
        literals at the producer, so the constants file under-reported what a
        player could receive. Asserted through the constants, not strings
        typed here, so a rename breaks the test."""
        from backend.notifications import (
            ARMISTICE_EXPIRED, MARSHAL_LAST_STAND, VINDICATION_EXPIRED,
        )
        labels = _gd_map("const TYPE_ICONS = {")
        glyphs = _gd_map("const TYPE_ICON_SVGS = {")
        for constant in (ARMISTICE_EXPIRED, MARSHAL_LAST_STAND,
                         VINDICATION_EXPIRED):
            assert constant in labels and constant in glyphs

    def test_the_producers_name_the_constants(self):
        """The other half of that fix: nothing in the backend still spells
        those three types as a literal."""
        import glob
        for path in glob.glob("backend/**/*.py", recursive=True):
            if path.replace(chr(92), "/").endswith("backend/notifications.py"):
                continue
            code = _code_norm(_read(path))
            for literal in ('"armistice_expired"', '"marshal_last_stand"',
                            '"vindication_expired"'):
                assert literal not in code, (path, literal)


# ══════════════════════════════════════════════════════════════════════════
# REV-V4 — the two end-turn ordering fixes, and the shapes they exist for
# ══════════════════════════════════════════════════════════════════════════

SCENARIO_1805 = os.path.join(
    "godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")


@pytest.fixture
def board_endpoint():
    """The 1805 board behind `/command`, with the debug verbs armed.

    Swaps the module-global `world` AND `game_state` AND the parser singleton
    — `/command` reads all three, and a test that swaps only one silently
    drives the wrong world (and, in mock-less builds, the live LLM).
    """
    from fastapi.testclient import TestClient
    import backend.main as main_module
    from backend.commands.parser import CommandParser

    keep = (main_module.world, main_module.game_state, main_module.parser)
    world = WorldState.from_scenario(SCENARIO_1805)
    main_module.world = world
    main_module.game_state = {"world": world, "debug_mode": True}
    main_module.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(main_module.app), world
    finally:
        (main_module.world, main_module.game_state,
         main_module.parser) = keep


def _issue_http(client, text):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return client.post("/command", json={"command": text}).json()


class TestTheEndTurnShapesTheTwoFixesExistFor:
    """Both fixes are ORDERING inside `main.gd`, so the client tests can only
    be source-text greps. What CAN be pinned here is the precondition: that
    the backend really does put these things on ONE end-turn response.

    That is not academic. The row's own staging recipe — a standing march
    into an undefended province — cannot produce the capture question at all
    (IGR-X5 made an automated hop pass `auto_secure=True`), and nothing
    caught it, which is why the review's staging attempt failed and was
    misattributed to an enemy pre-empting the march. These pins name the
    routes that DO reach each shape, so the next person staging them starts
    from something measured.
    """

    def test_a_completing_occupation_asks_inside_the_end_turn_response(
            self, board_endpoint):
        """FLOW 1. A FORTIFIED province is not captured on the attack — it is
        occupied, and `_process_tactical_states` finishes the occupation
        INSIDE `advance_turn`. So the question arrives alongside the whole
        narrative of the turn, which is exactly the collision the stash fixes.
        """
        client, world = board_endpoint
        _issue_http(client, "debug freeze_enemies")
        _issue_http(client, "debug add_building Bohemia fortification")
        _issue_http(client, "debug set_location Ney Franconia")
        _issue_http(client, "debug set_strength Ney 90000")

        attack = _issue_http(client, "Ney, attack Bohemia")
        assert attack.get("success") is True
        assert world.get_marshal("Ney").occupation_region == "Bohemia", (
            "the fort must start an occupation rather than capture outright — "
            "without that there is no end-turn capture at all")

        out = _issue_http(client, "end turn")
        assert out.get("pending_capture_choice") is True
        assert out.get("capture_data", {}).get("region") == "Bohemia"
        # ...and it is on the SAME response as the turn's own narrative.
        assert out.get("enemy_phase") is not None
        assert out.get("morning_dispatch")
        assert (out.get("events") or [{}])[0].get("type") == "turn_end"

    def test_a_standing_march_auto_secures_and_never_asks(
            self, board_endpoint):
        """The negative control, and the correction to the row's recipe: the
        automated hop passes `auto_secure=True`, so it takes the province in
        silence. Staging the capture question this way is impossible."""
        client, world = board_endpoint
        _issue_http(client, "debug freeze_enemies")
        _issue_http(client, "debug set_location Ney Franconia")
        _issue_http(client, "debug set_strength Ney 90000")
        _issue_http(client, "Ney, march to Bohemia")

        out = _issue_http(client, "end turn")
        assert world.get_region("Bohemia").controller == "France", (
            "the march must actually take it, or this control proves nothing")
        assert not out.get("pending_capture_choice")

    def test_a_blocked_literal_march_puts_an_ask_on_the_end_turn_response(
            self, board_endpoint):
        """FLOW 2. Soult is the authored LITERAL, and a literal whose
        destination is held halts and asks — `destination_blocked`,
        requires_input, no odds maths and no combat RNG. That report is what
        early-returns out of both dismissal handlers ahead of their own
        `_show_pending_dispatch()`."""
        client, world = board_endpoint
        _issue_http(client, "debug freeze_enemies")
        # Two hops out, so the order is still STANDING when the turn ends —
        # issued from an adjacent province it resolves on the spot and no
        # end-turn report is produced at all.
        _issue_http(client, "debug set_location Soult Orleanais")
        _issue_http(client, "Soult, march to Swabia")

        _issue_http(client, "end turn")
        out = _issue_http(client, "end turn")

        asks = [r for r in (out.get("strategic_reports") or [])
                if r.get("requires_input")]
        assert asks, "no input-requiring strategic report on the end turn"
        assert asks[0].get("interrupt_type") == "destination_blocked"
        assert out.get("enemy_phase") is not None
        assert out.get("morning_dispatch")


class TestTheTwoOrderingFixesAreStillInMainGd:
    """Source-text, deliberately: both fixes are pure control flow in the
    client. The review's own pins live in `test_review_2026_08_30.py`; these
    two add what those do not say — that the raise is reachable from the
    tail, and that the stash is keyed on the end-turn shape above."""

    def _main_gd(self):
        return _read("godot-client/project-sovereign/scripts/main.gd")

    def test_the_capture_stash_is_keyed_on_the_end_turn_response(self):
        src = self._main_gd()
        body = src[src.index("func _response_has_capture_choice_route("):]
        body = body[:body.index("func ", 40)]
        body = _code_only_gd(body)
        assert "enemy_phase" in body and "pending_capture_response = response" in body

    def test_the_interrupt_tail_shows_the_dispatch(self):
        """Scoped to the ORDINARY exit, not the whole function.

        Caught by the mutation sweep: `_process_next_interrupt` already
        called `_show_pending_dispatch()` in its redemption arm, so a
        function-wide substring pin stayed green with the fix deleted. The
        slice starts after that arm returns."""
        src = self._main_gd()
        body = src[src.index("func _process_next_interrupt("):]
        body = body[:body.index("func ", 40)]
        tail = _code_only_gd(body[body.index("# All interrupts processed"):])
        assert "_show_pending_dispatch()" in tail
        assert "_show_pending_diorama()" in tail, (
            "and it must come before the diorama raise, which returns")
        assert tail.index("_show_pending_dispatch()") <             tail.index("_show_pending_diorama()")
