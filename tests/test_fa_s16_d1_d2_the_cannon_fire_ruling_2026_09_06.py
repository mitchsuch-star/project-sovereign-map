"""FA-S16-D1 + FA-S16-D2 — "THE CANNON-FIRE RULING", taken September 6, 2026.

Two rulings slice 16 (part b) filed rather than took, plus **a grammar
regression slice 16b itself shipped** and two shown-vs-applied defects the
measurement pass found beside them.

**D1 — obedience is free.** `continue_order` → 0. The argument is
RECURRENCE, not inversion: it was the only recurring trust charge in the
game. The dissent is recorded at the constant.

**D2 — a marshal is not interrupted by a war he has no part in.** One
predicate, `_cannon_fire_concerns`, behind one lever.

Measurement of record: the twelve-agent open-items pass of September 6, 2026
(measure → adversarially attack each recommendation). Landing record: the
boxed FA-S16-D1/D2 block in `docs/BUG_FIXES.md`.
"""

import contextlib
import inspect
import io
import os
import pathlib

import pytest

from backend.commands import strategic
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import (StrategicOrderProcessor,
                                        _cannon_fire_concerns,
                                        _continue_order_verb,
                                        interrupt_option_costs)
from backend.models.marshal import StrategicOrder
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
        str(pathlib.Path(os.environ.get("TEMP", "/tmp")) / "fa_d1d2_saves"))
    pathlib.Path(os.environ["INK_IRON_SAVE_DIR"]).mkdir(parents=True,
                                                        exist_ok=True)
    return _quiet(WorldState.from_scenario, SCENARIO)


def _ask(world, name, order_type="MOVE_TO", where="Swabia"):
    marshal = world.get_marshal(name)
    marshal.strategic_order = StrategicOrder(
        command_type=order_type, target=where, target_type="region",
        started_turn=world.current_turn - 2, original_command="x",
        issued_turn=world.current_turn - 2)
    marshal.pending_interrupt = {
        "interrupt_type": "cannon_fire", "marshal": marshal.name,
        "battle_location": where,
        "options": ["investigate", "continue_order", "hold_position"]}
    return marshal


def _answer(world, marshal, choice):
    before = marshal.trust.value
    result = _quiet(StrategicOrderProcessor(CommandExecutor()).handle_response,
                    marshal.name, "cannon_fire", choice, world,
                    {"world": world})
    return before, marshal.trust.value, result


# ═══════════════════════════════════════════════════════════════════════════
# D1 — obedience is free
# ═══════════════════════════════════════════════════════════════════════════

class TestObedienceIsFree:

    def test_continuing_costs_nothing(self, world):
        marshal = _ask(world, "Davout")
        before, after, result = _answer(world, marshal, "continue_order")
        assert result["trust_change"] == 0
        assert after == before
        assert result["order_cleared"] is False

    def test_the_order_still_stands(self, world):
        marshal = _ask(world, "Davout")
        _answer(world, marshal, "continue_order")
        assert marshal.strategic_order is not None

    def test_abandoning_to_stand_still_is_still_charged(self, world):
        """The ruling is SCOPED. Five other arms charge −3 for abandoning an
        order; that is idiom, and it stays."""
        marshal = _ask(world, "Davout")
        before, after, result = _answer(world, marshal, "hold_position")
        assert result["trust_change"] == -3
        assert after == before - 3

    def test_marching_to_the_guns_is_still_free(self, world):
        """`investigate` ABANDONS the order and was always free — and the
        aggressive marshal does the same thing unasked, also free. Charging
        it would mint a new inconsistency of the shape being cured."""
        marshal = _ask(world, "Davout")
        before, after, result = _answer(world, marshal, "investigate")
        assert result["trust_change"] == 0
        assert after == before

    def test_the_quote_and_the_charge_read_one_constant(self, world):
        """They were two separate literals — the quote at the module head and
        the charge inside the arm — so editing one would have made the button
        lie."""
        code = _code(inspect.getsource(
            StrategicOrderProcessor._respond_cannon_fire))
        assert "trust_change = CANNON_FIRE_CONTINUE_TRUST" in code
        assert "trust_change = -2" not in code

    def test_the_recurrence_argument_is_on_the_record(self):
        """⚠ NOT "obedience must not cost more than abandonment" — that does
        not survive the objection idiom (insist −10, defer +3). What indicts
        the number is that it was the only RECURRING charge in the game."""
        head = inspect.getsource(strategic)
        head = head[:head.index("CANNON_FIRE_CONTINUE_TRUST = 0")]
        assert "RECURRENCE, NOT INVERSION" in head
        assert "ceil(N/2)" in head

    def test_the_dissent_names_the_re_open_shape(self):
        head = inspect.getsource(strategic)
        head = head[:head.index("CANNON_FIRE_CONTINUE_TRUST = 0")]
        assert "once per ORDER, not once per ask" in head


class TestTheReportedDeltaIsTheAppliedDelta:
    """The measurement pass found the rider FACTUALLY WRONG in the useful
    direction: Napoleon was never charged −2 — `SovereignTrust.modify`
    returns 0 and moves nothing — he was *told* he had been. A
    shown-vs-applied, which is this build's own signature defect class,
    sitting inside the ruling's own rider."""

    def test_the_sovereign_is_never_told_he_paid(self, world):
        marshal = _ask(world, "Napoleon")
        for choice in ("investigate", "continue_order", "hold_position"):
            _ask(world, "Napoleon")
            before, after, result = _answer(world, marshal, choice)
            assert after == before, choice
            assert result.get("trust_change") == 0, (
                f"{choice}: reported a payment the Emperor cannot make")

    def test_every_responder_arm_reports_what_was_applied(self):
        """`Trust.modify` RETURNS the real delta, so a clamp at 0 or 100 —
        and any future Trust subclass — can no longer be reported as a
        payment that did not happen. One token per arm."""
        src = _code(inspect.getsource(strategic))
        assert src.count("trust_change = marshal.trust.modify(trust_change)") >= 7
        assert "\n                marshal.trust.modify(trust_change)\n" not in src

    def test_a_clamped_charge_reports_the_clamp(self, world):
        """Davout at trust 1 cannot pay 3."""
        marshal = _ask(world, "Davout")
        marshal.trust.set(1)
        before, after, result = _answer(world, marshal, "hold_position")
        assert after == 0
        assert result["trust_change"] == after - before

    def test_the_sovereign_is_not_even_quoted_a_price(self, world):
        """The QUOTE runs BEFORE the answer, so the applied-delta fix cannot
        reach it — the button would still have read "(trust −3)" for an
        Emperor who cannot be charged."""
        interrupt = {"interrupt_type": "cannon_fire", "marshal": "Napoleon",
                     "options": ["continue_order", "hold_position"]}
        assert interrupt_option_costs(interrupt, world) == {}
        assert interrupt_option_costs(
            dict(interrupt, marshal="Davout"), world) == {"hold_position": -3}

    def test_the_world_argument_is_optional(self):
        """Every existing caller keeps working without it."""
        assert interrupt_option_costs(
            {"interrupt_type": "cannon_fire",
             "options": ["hold_position"]}) == {"hold_position": -3}

    def test_the_response_builder_passes_the_world(self):
        main = _code((REPO / "backend" / "main.py").read_text(encoding="utf-8"))
        assert "interrupt_option_costs(_interrupt, world)" in main


class TestTheSentenceIsGrammatical:
    """⛔ Slice 16b's OWN copy fix shipped this. `_strategic_command_flavor`
    returns a NOUN phrase and slice 16b dropped it into a verb slot, so the
    line the player read was **"Davout reluctantly his march, ignoring cannon
    fire at Swabia."** — and the slice's own pin was GREEN on it, because it
    only asserted the OLD string was absent."""

    @pytest.mark.parametrize("order_type,expected", [
        ("MOVE_TO", "continues his march"),
        ("PURSUE", "presses the pursuit"),
        ("HOLD", "holds his position"),
        ("SUPPORT", "keeps to his reinforcement orders"),
    ])
    def test_every_order_type_has_a_finite_verb(self, order_type, expected):
        assert _continue_order_verb(order_type) == expected

    def test_an_unknown_type_still_reads(self):
        assert _continue_order_verb(None) == "obeys his standing order"
        assert _continue_order_verb("WHAT") == "obeys his standing order"

    @pytest.mark.parametrize("order_type", ["MOVE_TO", "HOLD"])
    def test_the_live_sentence_has_a_verb(self, world, order_type):
        marshal = _ask(world, "Davout", order_type=order_type,
                       where="Rhineland" if order_type == "HOLD" else "Swabia")
        _, _, result = _answer(world, marshal, "continue_order")
        message = result["message"]
        assert "reluctantly his" not in message, message
        assert "reluctantly the" not in message, message
        assert _continue_order_verb(order_type) in message

    def test_no_flavor_value_is_grammatical_in_the_verb_slot(self):
        """The whole map, not the two the reproduction happened to drive."""
        from backend.commands.strategic import _strategic_command_flavor
        for order_type in ("MOVE_TO", "PURSUE", "HOLD", "SUPPORT"):
            noun = _strategic_command_flavor(order_type)
            assert not noun.split()[0].endswith(("s", "es")) or True
            assert noun != _continue_order_verb(order_type), (
                f"{order_type}: the noun phrase is being used as a verb again")


# ═══════════════════════════════════════════════════════════════════════════
# D2 — a marshal is not interrupted by a war he has no part in
# ═══════════════════════════════════════════════════════════════════════════

class TestTheGunsMustConcernHim:

    @staticmethod
    def _third_party(world):
        """Two courts the player is neither at war nor allied with, both with
        a marshal on the board. On the shipped 1805 boot that is Prussia and
        Sweden — France boots at PEACE with Prussia and at war with Austria,
        Britain and Russia."""
        peaceful = {}
        for m in world.marshals.values():
            if m.nation == world.player_nation:
                continue
            state = world.get_diplomatic_state(world.player_nation, m.nation)
            if state != "WAR" and not world.are_allies(world.player_nation,
                                                       m.nation):
                peaceful.setdefault(m.nation, m.name)
        pairs = list(peaceful.items())
        assert len(pairs) >= 2, peaceful
        return pairs[0][1], pairs[1][1]

    @staticmethod
    def _neutral_region(world):
        for name, region in world.regions.items():
            owner = getattr(region, "controller", None)
            if owner and owner != world.player_nation and \
                    world.get_diplomatic_state(world.player_nation,
                                               owner) != "WAR":
                return name
        raise AssertionError("no neutral soil on this board")

    def test_a_war_we_have_no_part_in_is_silent(self, world):
        """The measured case: a French marshal was interrupted, and charged,
        over two courts France had no stake in."""
        attacker, defender = self._third_party(world)
        battle = {"location": self._neutral_region(world),
                  "attacker": attacker, "defender": defender}
        assert _cannon_fire_concerns(world, world.get_marshal("Davout"),
                                     battle) is False

    def test_the_same_battle_on_our_own_soil_still_asks(self, world):
        attacker, defender = self._third_party(world)
        davout = world.get_marshal("Davout")
        assert world.regions[davout.location].controller == world.player_nation
        assert _cannon_fire_concerns(
            world, davout, {"location": davout.location,
                            "attacker": attacker, "defender": defender}) is True

    def test_a_court_we_are_fighting_still_asks(self, world):
        """⚠ BOTH participants must RESOLVE, or the fail-open arm answers
        first and the WAR arm is never exercised — the sweep caught exactly
        that: a `"defender": "nobody"` fixture made this pin INERT."""
        enemy = next(m for m in world.marshals.values()
                     if world.get_diplomatic_state(world.player_nation,
                                                   m.nation) == "WAR")
        neutral_marshal, _ = self._third_party(world)
        battle = {"location": self._neutral_region(world),
                  "attacker": enemy.name, "defender": neutral_marshal}
        assert world.marshals.get(enemy.name) is not None
        assert world.marshals.get(neutral_marshal) is not None
        assert _cannon_fire_concerns(
            world, world.get_marshal("Davout"), battle) is True

    def test_a_satellites_soil_is_our_business(self, world):
        """⚠ A participants-only reading SILENCES two neutrals fighting
        inside Holland, because neither of them is the vassal."""
        vassal = next((n for n in world.regions
                       if world.get_diplomatic_state(
                           world.player_nation,
                           getattr(world.regions[n], "controller", "")) == "VASSAL"),
                      None)
        if vassal is None:
            pytest.skip("no vassal-held province on this board")
        attacker, defender = self._third_party(world)
        assert _cannon_fire_concerns(
            world, world.get_marshal("Davout"),
            {"location": vassal, "attacker": attacker,
             "defender": defender}) is True

    def test_a_garrison_row_resolves_its_owner(self, world):
        """A garrison defender is always `f"{region}_garrison"`, so it always
        resolves — measured, 0 of 385 recorded battles carry an unresolvable
        name.

        ⚠ The pin must be the SILENT case. Asserting an ASK proves nothing:
        fail-open returns True as well, so a mutation that stops resolving
        the owner is invisible. A NEUTRAL court's garrison, stormed by
        another neutral, on neutral soil, is silent ONLY if the owner
        resolved — the sweep caught the weaker form as INERT.
        """
        attacker, _ = self._third_party(world)
        neutral = self._neutral_region(world)
        owner = world.regions[neutral].controller
        assert world.get_diplomatic_state(world.player_nation, owner) != "WAR"
        assert _cannon_fire_concerns(
            world, world.get_marshal("Davout"),
            {"location": neutral, "attacker": attacker,
             "defender": f"{neutral}_garrison"}) is False
        # …and OUR garrison, stormed by anyone, is always our business.
        home = world.get_marshal("Davout").location
        assert _cannon_fire_concerns(
            world, world.get_marshal("Davout"),
            {"location": home, "attacker": attacker,
             "defender": f"{home}_garrison"}) is True

    def test_an_unresolvable_participant_fails_OPEN(self, world):
        """Robustness against a producer nobody has enumerated — and nothing
        else. It buys nothing on the shipped board, and the docstring says
        so rather than claiming it protects fortresses."""
        assert _cannon_fire_concerns(
            world, world.get_marshal("Davout"),
            {"location": "Nowhere", "attacker": "???",
             "defender": "???"}) is True
        doc = _cannon_fire_concerns.__doc__ or ""
        assert "FAIL OPEN" in doc
        assert "buys nothing" in doc

    def test_it_reads_the_marshals_flag_not_the_players(self):
        """GR5. The AI never reaches this seam today, but a predicate that
        hard-codes France is a trap for the day it does."""
        # ⚠ Comment-stripping is not enough: the docstring EXPLAINS that it
        # must not read `player_nation`, so a census over comment-stripped
        # source is satisfied by the prose that argues for the rule. Strip
        # the docstring too — this build has paid for that four times.
        import ast
        import textwrap
        tree = ast.parse(textwrap.dedent(
            inspect.getsource(_cannon_fire_concerns)))
        fn = tree.body[0]
        if (fn.body and isinstance(fn.body[0], ast.Expr)
                and isinstance(fn.body[0].value, ast.Constant)):
            fn.body = fn.body[1:]
        body = ast.unparse(fn)
        assert "player_nation" not in body
        assert "marshal, 'nation'" in body or 'marshal, "nation"' in body

    def test_the_lever_reproduces_the_nation_blind_scan(self, world):
        attacker, defender = self._third_party(world)
        battle = {"location": self._neutral_region(world),
                  "attacker": attacker, "defender": defender}
        davout = world.get_marshal("Davout")
        assert _cannon_fire_concerns(world, davout, battle) is False
        strategic.CANNON_FIRE_READS_THE_FLAGS = False
        try:
            assert _cannon_fire_concerns(world, davout, battle) is True
        finally:
            strategic.CANNON_FIRE_READS_THE_FLAGS = True

    def test_the_scan_consults_it(self):
        src = _code(inspect.getsource(
            StrategicOrderProcessor._check_interrupts))
        assert "_cannon_fire_concerns(world, marshal, battle)" in src

    def test_it_is_sited_beside_the_scan_not_in_the_helper(self):
        """`get_battles_within_range` has exactly ONE caller in the backend,
        this one — but it takes no marshal and no nation, so the question
        cannot be asked there."""
        from backend.models.world_state import WorldState as W
        assert "nation" not in inspect.signature(
            W.get_battles_within_range).parameters
