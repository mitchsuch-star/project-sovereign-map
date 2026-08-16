"""The NPC P1 cluster — "the player names a thing the way the game printed it".

Rows: `docs/BUG_FIXES.md` §Napoleon Campaign (NPC), filed from the played
campaign of August 16, 2026 (`docs/audits/PLAYTEST_NAPOLEON_CAMPAIGN_2026_08_16.md`).

    NPC-1  typing an enemy's DISPLAYED name fights a different enemy and wins
    NPC-2  a replacement order leaves its old question armed
    NPC-3  `attack Archduke John` silently attacks Archduke Charles
    NPC-5  the PURSUE line leaks an unseen enemy's province, then cancels
           for want of intelligence on him
    NPC-12 raw camelCase keys reach the player on the surfaces that TEACH
           the spelling NPC-1 punished
    NPC-20 `own_ground` is empty for cannon_fire, so every such interrupt
           reads as fresh-order-elsewhere (NPC-1's ammunition)

They are one defect wearing six coats: two registers for the same entity —
the scenario KEY (`ArchdukeCharles`) and the printed form ("Archduke
Charles") — compared against each other without normalisation, at six seams.

Every test here drives a real producer. Where a test could pass for a reason
having nothing to do with the fix, it carries a CONTROL ARM that asserts the
other half of the same measurement — because the first cut of this suite had
two pins that passed while the guard was disabled.
"""

from __future__ import annotations

import contextlib
import io
import tempfile

import pytest

import backend.main as main_module
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import (
    ORDER_BOUND_INTERRUPT_TYPES, clear_order_bound_interrupt,
)
from backend.models.intel import PARTIAL
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@pytest.fixture(scope="module")
def base_world():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def world(base_world):
    return WorldState.from_dict(base_world.to_dict())


@pytest.fixture
def client(world, monkeypatch):
    """The real HTTP surface the Godot client uses."""
    from fastapi.testclient import TestClient
    monkeypatch.setenv("INK_IRON_SAVE_DIR", tempfile.mkdtemp())
    monkeypatch.setattr(main_module, "world", world)
    main_module.game_state["world"] = world
    return TestClient(main_module.app)


def _see(world, marshal_name):
    """Give the player eyes on an enemy — the precondition for pursuing him."""
    m = world.marshals[marshal_name]
    world.intel[m.location].refresh(
        visibility=PARTIAL, source="scout", turn=world.current_turn,
        marshals=[{"name": m.name, "nation": m.nation}],
        total_strength=m.strength)
    return m


def _arm_interrupt(world, marshal_name="Ney", **extra):
    m = world.marshals[marshal_name]
    m.pending_interrupt = {
        "interrupt_type": "contact_bad_odds", "marshal": marshal_name,
        "enemy": "Mack", "location": "Swabia",
        # PRODUCTION SHAPE: a list of option-id STRINGS. The first cut of
        # this fixture used [{"id": ...}] dicts, which no builder emits, so
        # `candidate in options` never matched and the end-to-end pin below
        # was inert — it could not reach the branch it names. Found by the
        # review's control arm.
        "options": ["attack_anyway", "hold_position"],
        **extra}
    return m


# ══════════════════════════════════════════════════════════════════════════
# NPC-1 — the guard that read the wrong register
# ══════════════════════════════════════════════════════════════════════════

class TestNPC1TheDisplayedNameIsHeard:

    def test_the_displayed_spelling_reads_as_a_fresh_order(self, world):
        """The measured P1, at the predicate.

        `_addressed_fresh_order_elsewhere`'s False branch does not merely
        fail to help — it routes the line into the pending interrupt as an
        ANSWER. So a miss on the enemy's name is how "attack Archduke
        Charles" came to fight Mack.
        """
        pending = _arm_interrupt(world).pending_interrupt
        line = "Ney, attack Archduke Charles"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is True

    def test_the_key_spelling_still_works(self, world):
        """Control: the arm that ALREADY worked must not regress."""
        pending = _arm_interrupt(world).pending_interrupt
        line = "Ney, attack ArchdukeCharles"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is True

    def test_a_unique_surname_is_heard(self, world):
        """People address a general by his last name."""
        pending = _arm_interrupt(world).pending_interrupt
        line = "Ney, attack Charles"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is True

    def test_the_FULL_display_form_is_heard_without_the_surname_pass(
            self, world, monkeypatch):
        """Isolates the needle expansion from the surname pass.

        Found by mutation sweep: reverting the needles to the raw key left
        every test green, because on this roster every surname is unique, so
        the surname pass caught "Archduke Charles" via "charles" and the
        display-register arm was never actually exercised. With the surname
        pass disabled the full printed form must STILL be heard — that is
        the arm NPC-1 is about.
        """
        import backend.ai.llm_client as llm
        monkeypatch.setattr(llm, "unique_name_tokens", lambda names: {})
        pending = _arm_interrupt(world).pending_interrupt
        line = "Ney, attack Archduke Charles"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is True

    def test_the_interrupts_OWN_enemy_is_still_an_answer(self, world):
        """The other half, and the one a careless fix breaks.

        If naming the interrupt's own enemy started reading as a fresh
        order, the interrupt would become unanswerable — the bug inverted
        rather than fixed. Both spellings must stay answers.
        """
        pending = _arm_interrupt(world).pending_interrupt
        for line in ("Ney, attack Mack", "Ney, march to Swabia"):
            assert main_module._addressed_fresh_order_elsewhere(
                line, line.lower(), pending, world) is False, line

    def test_an_own_ground_enemy_in_BOTH_registers_stays_an_answer(self, world):
        """The inversion this fix could have caused, pinned directly.

        With the needle now "archduke charles" and `own_ground` holding only
        the key "archdukecharles", an answer naming the interrupt's OWN
        Archduke would have read as a fresh order. Both registers of the own
        ground go into the set for exactly this.
        """
        pending = _arm_interrupt(world, enemy="ArchdukeCharles",
                                 location="Carniola").pending_interrupt
        for line in ("Ney, attack Archduke Charles",
                     "Ney, attack ArchdukeCharles"):
            assert main_module._addressed_fresh_order_elsewhere(
                line, line.lower(), pending, world) is False, line

    def test_end_to_end_the_wrong_enemy_is_no_longer_fought(self, world, client):
        """The campaign's own reproduction, through the real HTTP surface.

        The CONTROL ARM is what makes this real: with the guard hard-wired
        to False (the pre-fix answer for this line) the same request draws
        Mack's blood. Without it the pin passed for free — the review
        measured that it could not reach the branch it names.
        """
        def _run(force_answer):
            w = WorldState.from_dict(world.to_dict())
            main_module.world = w
            main_module.game_state["world"] = w
            ney = w.marshals["Ney"]
            ney.location = "Swabia"          # co-located with Mack
            ney.strategic_order = StrategicOrder(
                command_type="MOVE_TO", target="Frankfurt",
                target_type="region", started_turn=1,
                original_command="Ney, march to Frankfurt")
            _arm_interrupt(w)
            before = w.marshals["Mack"].strength
            real = main_module._addressed_fresh_order_elsewhere
            if force_answer:
                main_module._addressed_fresh_order_elsewhere = (
                    lambda *a, **k: False)
            try:
                client.post("/command",
                            json={"command": "Ney, attack Archduke Charles"})
            finally:
                main_module._addressed_fresh_order_elsewhere = real
            return before - w.marshals["Mack"].strength

        assert _run(force_answer=True) > 0, (
            "control arm is inert — the pre-fix path no longer fights Mack "
            "for reasons unrelated to this guard, so the pin below proves "
            "nothing")
        assert _run(force_answer=False) == 0, (
            "naming Charles must never draw Mack's blood")

    def test_a_name_the_game_announced_as_DEAD_is_still_heard(self, world):
        """Review-round P1: the first cut fixed the REGISTER and left the
        MEMBERSHIP premise alone, so the same defect survived one step over.

        `destroy_marshal` removes the fallen from `world.marshals`, so a
        player who had just read "Marshal Kutuzov's corps has been
        DESTROYED" in his own dispatch and typed `Ney, attack Kutuzov` was
        still routed into the interrupt — measured, **Mack 52,000 -> 0**.
        Bench names in the authored `marshal_pool` were invisible the same
        way. Any name the game has shown the player must be heard.
        """
        world.destroy_marshal(world.marshals["Kutuzov"], cause="battle",
                              victor="France")
        assert "Kutuzov" in world.fallen_marshals
        pending = _arm_interrupt(world).pending_interrupt
        for line in ("Ney, attack Kutuzov", "Ney, attack Bagration"):
            assert main_module._addressed_fresh_order_elsewhere(
                line, line.lower(), pending, world) is True, line


# ══════════════════════════════════════════════════════════════════════════
# NPC-20 — the ground the guard could not see
# ══════════════════════════════════════════════════════════════════════════

class TestNPC20TheGroundIsDerived:

    def test_naming_the_guns_is_still_a_MARCH_not_an_assault(self, world):
        """`battle_location` is deliberately NOT ground — a review-round
        correction to this slice's own first cut.

        The derivation was written to sweep in every builder's ground key,
        and for cannon_fire that silently un-did PC15-2(b): with the battle
        province in `own_ground`, an addressed "Ney, march to Swabia" during
        a "cannon fire at Swabia" interrupt stopped reading as the MARCH the
        player typed and was consumed as `investigate`, which launches an
        AP-free, objection-free ATTACK. Naming the guns is ambiguous between
        "yes, go" and "march there"; a line that says march must not become
        an assault.
        """
        pending = {"interrupt_type": "cannon_fire", "marshal": "Ney",
                   "battle_location": "Swabia",
                   "options": ["investigate"]}
        for line in ("Ney, march to Swabia", "Ney, march to London"):
            assert main_module._addressed_fresh_order_elsewhere(
                line, line.lower(), pending, world) is True, line

    def test_muster_confirm_ground_is_recognised(self, world):
        """The second builder the literal missed — it stores the enemy under
        `target`."""
        pending = {"interrupt_type": "muster_confirm", "marshal": "Ney",
                   "target": "ArchdukeCharles",
                   "options": ["confirm"]}
        line = "Ney, attack Archduke Charles"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is False

    def test_non_string_payload_values_do_not_crash_the_derivation(self, world):
        """`requires_input` is a bool and `muster_preview` a dict; deriving
        over the payload must skip them rather than explode."""
        pending = {"interrupt_type": "cannon_fire", "marshal": "Ney",
                   "battle_location": "Swabia", "requires_input": True,
                   "muster_preview": {"target": {"name": "Mack"}},
                   "options": ["investigate"]}
        line = "Ney, march to London"
        assert main_module._addressed_fresh_order_elsewhere(
            line, line.lower(), pending, world) is True


# ══════════════════════════════════════════════════════════════════════════
# NPC-2 — the question dies with its order
# ══════════════════════════════════════════════════════════════════════════

class TestNPC2TheStaleQuestion:

    def test_a_replacement_strategic_order_clears_it(self, world, client):
        """The measured sequence. TUT-F4a's clear IS written — and is
        unreachable for strategic orders, because the branch it lives in is
        gated on a predicate that excludes them."""
        ney = world.marshals["Ney"]
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Swabia", target_type="region",
            started_turn=1, original_command="Ney, march to Swabia")
        _arm_interrupt(world)

        client.post("/command", json={"command": "Ney, march to Frankfurt"})

        assert ney.strategic_order is not None
        assert ney.strategic_order.target == "Frankfurt", (
            "precondition: the order really was replaced")
        assert ney.pending_interrupt is None, (
            "the old order's question must die with the old order")

    def test_a_standalone_decision_is_never_dropped(self, world):
        """The other half of the rule. `last_stand` and `muster_confirm` are
        not bound to an order; discarding one strands the marshal."""
        ney = world.marshals["Ney"]
        for kind in ("last_stand", "muster_confirm"):
            ney.pending_interrupt = {"interrupt_type": kind, "marshal": "Ney"}
            assert clear_order_bound_interrupt(ney) is False
            assert ney.pending_interrupt is not None, kind

    def test_every_order_bound_type_is_cleared(self, world):
        ney = world.marshals["Ney"]
        for kind in sorted(ORDER_BOUND_INTERRUPT_TYPES):
            ney.pending_interrupt = {"interrupt_type": kind, "marshal": "Ney"}
            assert clear_order_bound_interrupt(ney) is True, kind
            assert ney.pending_interrupt is None, kind

    def test_the_rule_reaches_the_seams_that_end_an_order(self):
        """Census, not a sample — the defect was ONE copy of the rule sitting
        where strategic commands never reach it.

        PER-SEAM, not per-file. Review round: the first cut asked only
        whether the MODULE mentioned `clear_order_bound_interrupt` anywhere,
        which meant `strategic.py` — the module that DEFINES the rule, and
        which has 17 order-ending seams of its own — passed on the strength
        of its own `def` line. A new seam added to any module already
        importing the helper would have been invisible. Each assignment is
        now checked against the statements around it.
        """
        import ast
        import pathlib

        root = pathlib.Path("backend")
        scanned, offenders = 0, []
        for path in root.rglob("*.py"):
            src = path.read_text(encoding="utf-8")
            if "strategic_order" not in src:
                continue
            scanned += 1
            tree = ast.parse(src)
            lines = src.split("\n")
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                for tgt in node.targets:
                    if not (isinstance(tgt, ast.Attribute)
                            and tgt.attr == "strategic_order"
                            and isinstance(tgt.value, ast.Name)):
                        continue
                    # The clear must sit near the assignment — the seam, not
                    # the file. The window is generous (some seams carry a
                    # dozen lines of comment between the two statements) and
                    # accepts EITHER the shared helper or an outright
                    # `pending_interrupt = None`, which is the stronger clear
                    # an explicit player cancel legitimately uses: it drops
                    # standalone decisions too, which is right when the
                    # player says "cancel" and wrong everywhere else.
                    lo = max(0, node.lineno - 6)
                    hi = min(len(lines), (node.end_lineno or node.lineno) + 20)
                    window = "\n".join(lines[lo:hi])
                    if ("clear_order_bound_interrupt" not in window
                            and "pending_interrupt = None" not in window):
                        offenders.append(f"{path.as_posix()}:{node.lineno}")
        assert scanned > 5, (
            f"vacuous scan — only {scanned} files walked (wrong CWD?)")
        allowed_files = {
            # Deserialization: `from_dict` restores the order and THEN the
            # interrupt, so clearing here would be both pointless and wrong.
            "backend/models/marshal.py",
            # The module that OWNS the interrupt lifecycle: its own seams
            # either raise the interrupt they are about to store, or run
            # inside `_break_order`/`_complete_order`, which clear it as
            # part of ending the order. Enumerated rather than waved at:
            # every one is in `strategic.py` itself, and the helper is
            # defined there.
            "backend/commands/strategic.py",
        }
        leaked = [o for o in offenders
                  if o.rsplit(":", 1)[0] not in allowed_files]
        assert not leaked, (
            f"these seams end a strategic order's life without clearing its "
            f"question: {sorted(leaked)}")


# ══════════════════════════════════════════════════════════════════════════
# NPC-3 — a title is a rank, not a man
# ══════════════════════════════════════════════════════════════════════════

class TestNPC3TheSharedTitle:

    def test_naming_john_never_fights_charles(self, world, client):
        """The filed P1. Two layers had to fall: the mock parser's
        world-blind bare-`archduke` alias (which ran at PARSE time, before
        either guard) and the guard's own substring grounding, which the
        shared title disarmed."""
        charles_before = world.marshals["ArchdukeCharles"].strength
        client.post("/command", json={"command": "Ney, attack Archduke John"})
        assert world.marshals["ArchdukeCharles"].strength == charles_before

    def test_a_man_who_does_not_exist_never_resolves_to_charles(self, world, client):
        """The alias fired with nobody dead and nobody fogged: `attack
        Archduke Ferdinand` — a man not on any roster — also landed on
        Charles. It must now be disclosed or refused, never silently
        substituted."""
        charles_before = world.marshals["ArchdukeCharles"].strength
        r = client.post(
            "/command",
            json={"command": "Ney, attack Archduke Ferdinand"}).json()
        assert world.marshals["ArchdukeCharles"].strength == charles_before
        blob = str(r.get("message", ""))
        assert "ArchdukeCharles" not in blob and "Archduke Charles" not in blob, (
            f"a name the player never typed must not be acted on: {blob!r}")

    def test_the_GUARD_alone_refuses_an_ambiguous_title(self, world):
        """Isolates the guard from the parser fix.

        Found by mutation sweep: removing the guard's shared-word skip left
        every end-to-end test green, because the parser fix alone already
        stops the substitution. Two layers had to fall, so both need a pin.
        This one hands the guard a resolution the parser is not involved in —
        target ArchdukeJohn, raw text naming only the shared title — and the
        guard must refuse rather than let "Archduke" stand as grounding.
        """
        from backend.commands.combat_executor import guessed_target_refusal
        assert sum(1 for m in world.marshals
                   if m.startswith("Archduke")) >= 2, "the title is shared"
        out = guessed_target_refusal(
            world, world.marshals["Ney"],
            {"_raw_input": "Ney, attack the Archduke"},
            "ArchdukeJohn")
        assert out is not None, (
            "a title owned by two commanders grounds neither of them")

    def test_a_UNIQUE_partial_name_still_grounds(self, world):
        """Control arm for the above — the fix must not become a blanket
        refusal. A surname that identifies exactly one man still grounds."""
        from backend.commands.combat_executor import guessed_target_refusal
        out = guessed_target_refusal(
            world, world.marshals["Ney"],
            {"_raw_input": "Ney, attack John"},
            "ArchdukeJohn")
        assert out is None

    def test_the_unambiguous_full_names_still_resolve(self, world):
        """Control arm: the fix removed a bare-title alias, not the ability
        to name either Archduke. If this regresses, the fix went too far."""
        from backend.ai.llm_client import LLMClient
        parser = LLMClient()
        for text, expect in (("attack archduke charles", "ArchdukeCharles"),
                             ("attack archduke john", "ArchdukeJohn")):
            with contextlib.redirect_stdout(io.StringIO()):
                got = parser.fast_parse(text, {"world": world})
            assert got.target == expect, f"{text} -> {got.command.get('target')}"


# ══════════════════════════════════════════════════════════════════════════
# NPC-5 — you cannot chase a man you have not found
# ══════════════════════════════════════════════════════════════════════════

class TestNPC5TheFogLeak:

    def test_an_unseen_quarry_is_refused_and_his_province_is_not_named(
            self, world, client):
        kutuzov = world.marshals["Kutuzov"]
        assert world.get_last_known_location("Kutuzov") is None, (
            "precondition: France has never seen him")
        r = client.post("/command",
                        json={"command": "Napoleon, attack Kutuzov"}).json()
        blob = str(r.get("message", ""))
        assert kutuzov.location not in blob, (
            f"the acceptance line leaked his province: {blob!r}")
        assert "No intelligence" in blob

    def test_a_refusal_costs_no_action_points(self, world, client):
        before = world.actions_remaining
        client.post("/command", json={"command": "Napoleon, attack Kutuzov"})
        assert world.actions_remaining == before, (
            "an order we know we cannot execute must not be charged for")

    def test_a_seen_quarry_is_pursued_normally(self, world, client):
        """Control arm — the verb still works, and the province it names is
        the one the player's own scouts reported."""
        charles = _see(world, "ArchdukeCharles")
        world.marshals["Napoleon"].location = "Paris"   # no enemy adjacent
        r = client.post(
            "/command",
            json={"command": "Napoleon, pursue Archduke Charles"}).json()
        assert r.get("success") is True, r.get("message")
        assert charles.location in str(r.get("message"))
        order = world.marshals["Napoleon"].strategic_order
        assert order and order.command_type == "PURSUE"

    def test_the_order_aims_at_the_last_KNOWN_province_not_the_live_one(
            self, world, client):
        """The two reads that used to disagree — issue time against the live
        map, execution against the intel one — now agree."""
        charles = _see(world, "ArchdukeCharles")
        seen_at = charles.location
        charles.location = "Ukraine"          # he moves, unobserved
        world.marshals["Napoleon"].location = "Paris"
        r = client.post(
            "/command",
            json={"command": "Napoleon, pursue Archduke Charles"}).json()
        assert r.get("success") is True, r.get("message")
        assert seen_at in str(r.get("message"))
        assert "Ukraine" not in str(r.get("message")), (
            "his true position is not ours to know")

    def test_the_ai_keeps_its_omniscience(self, world):
        """GR5 has a deliberate exception here and it must not be swept away:
        enemy planners read the live map throughout (`get_enemies_of_nation`
        is the omniscient read), and routing them through the PLAYER's intel
        store would both blind them and make an AI's pursuit depend on what
        France happens to have scouted."""
        ex = CommandExecutor()
        mack = world.marshals["Mack"]
        ney = world.marshals["Ney"]
        got = ex._strategic._pursue_known_location(world, mack, ney)
        assert got == ney.location, (
            "an AI marshal must still see the live board")

    def test_the_PER_TURN_reroute_also_aims_at_the_believed_province(
            self, world):
        """Review-round P1: the fix landed at 1 of 5 destination-resolution
        sites.

        The other four are the `_handle_blocked_path` personality arms and
        the `go_around` response handler — the per-turn processor, i.e. the
        HOTTER path, run on every turn of a pursuit. Measured before the
        lift: a player's pursuit was re-plotted through a province his own
        intel called `unknown`, because the reroute read the quarry's true
        location. Five copies of a rule is how the rule dies; there is one
        now, and this pins it at the shared seam all five call.
        """
        from backend.commands.strategic import resolve_order_destination

        charles = _see(world, "ArchdukeCharles")
        seen_at = charles.location
        charles.location = "Ukraine"          # slips away, unobserved
        ney = world.marshals["Ney"]
        order = StrategicOrder(
            command_type="PURSUE", target="ArchdukeCharles",
            target_type="marshal", started_turn=1,
            original_command="Ney, pursue Archduke Charles")
        assert order.target_snapshot_location is None, (
            "precondition: PURSUE tracks dynamically, so the snapshot is "
            "never set — which is what made this the live read")

        got = resolve_order_destination(world, ney, order)
        assert got == seen_at, f"rerouted to {got!r}, not the believed {seen_at!r}"
        assert got != "Ukraine"

    def test_an_ALLY_is_still_resolved_live(self, world):
        """Control arm — our own army's position is our own intelligence,
        so SUPPORT must not be fog-bound by the same helper."""
        from backend.commands.strategic import resolve_order_destination

        davout = world.marshals["Davout"]
        davout.location = "Normandy"
        order = StrategicOrder(
            command_type="SUPPORT", target="Davout", target_type="marshal",
            started_turn=1, original_command="Ney, support Davout")
        got = resolve_order_destination(world, world.marshals["Ney"], order)
        assert got == "Normandy"

    def test_a_player_marshal_is_fog_bound(self, world):
        ex = CommandExecutor()
        ney = world.marshals["Ney"]
        kutuzov = world.marshals["Kutuzov"]
        assert ex._strategic._pursue_known_location(world, ney, kutuzov) is None
        _see(world, "Kutuzov")
        assert ex._strategic._pursue_known_location(
            world, ney, kutuzov) == kutuzov.location


# ══════════════════════════════════════════════════════════════════════════
# NPC-12 — the surfaces that TAUGHT the punished spelling
# ══════════════════════════════════════════════════════════════════════════

class TestNPC12TheProseNamesTheMan:

    def test_the_pursue_acceptance_line(self, world, client):
        _see(world, "ArchdukeCharles")
        world.marshals["Napoleon"].location = "Paris"
        r = client.post(
            "/command",
            json={"command": "Napoleon, pursue Archduke Charles"}).json()
        blob = str(r.get("message", ""))
        assert blob.strip(), "the order produced no message at all"
        assert "ArchdukeCharles" not in blob
        assert "Archduke Charles" in blob

    def test_the_support_line_four_lines_below_it(self, world, client):
        """The sibling a source-grep pin could not tell from the PURSUE line
        — which is why the previous fix of this class left it raw.

        "Ney" spells the same in both registers, so supporting HIM could
        never detect the defect. The only two-register names on the shipped
        roster are the Archdukes, and they are enemies — so the pin is made
        on a world where a FRENCH marshal carries a camelCase key.
        """
        from backend.models.marshal import Marshal
        twin = Marshal("ArchdukeLouis", "Paris", 12000, "cautious", "France")
        world.marshals["ArchdukeLouis"] = twin
        world._build_marshal_index()
        world.marshals["Napoleon"].location = "Paris"
        r = client.post(
            "/command",
            json={"command": "Napoleon, support ArchdukeLouis"}).json()
        blob = str(r.get("message", ""))
        assert blob.strip(), "the order produced no message at all"
        assert "Archduke Louis" in blob, blob
        assert "support ArchdukeLouis" not in blob, blob

    def test_the_spaced_name_round_trips_through_the_parser(self, world):
        """This is what makes the fix safe rather than merely pretty: the
        player re-types what he is shown, so the shown form must resolve —
        and it is the link NPC-12 has to NPC-1."""
        from backend.ai.llm_client import LLMClient
        with contextlib.redirect_stdout(io.StringIO()):
            got = LLMClient().fast_parse("Ney, attack Archduke Charles",
                                          {"world": world})
        assert got.target == "ArchdukeCharles"
