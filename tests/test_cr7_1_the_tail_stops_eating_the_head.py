"""CR-7-1 — "The tail stops eating the head" (the Command-Road Queue, slice 1).

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-1. Reproduced on this HEAD before a line was written (September 22,
2026): **40 of 40** non-movement compound shapes (10 heads × 4 tail forms)
were SWALLOWED at `CommandParser.parse` — `action=attack`, no strategic
order, no `dropped_sequel`, no warning — and at `POST /command`
`Ney, fortify then attack Mack` marched Rhineland→Swabia, fought, went
24,000 → 21,720, was NOT fortified, spent 1 AP and said nothing.

The seam was one predicate in `parser._split_sequential_orders`: the
attack-on-arrival exemption declined to split ANY tail beginning with an
attack verb unless the head was FA-7's stand-still vocabulary — a list of
the heads that had been REPORTED, not the question "can this head carry
the tail". The rule is inverted: a tail fuses onto a head only if the head
can CARRY an arrival — a MOVE_TO / PURSUE with a destination, derived from
the ONE strategic routing table, or a standing order carrying `until`.

⚠ `python -m backend.ai.parser_eval` reports 688/688 in BOTH arms of this
fix (measured, this session). A green corpus is not evidence here; every
pin below drives `CommandParser.parse` on the shipped 1805 boot or the real
`POST /command` seam, and the sensitivity arm flips the lever to prove the
battery reds without the fix.
"""

import os
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
import backend.commands.parser as parser_mod
from backend.ai import strategic_parser as sp
from backend.ai.parser_eval import (
    build_llm_game_state,
    build_world,
    evaluate_entry,
    load_corpus,
    worlds_for_entry,
)
from backend.commands.parser import (
    CommandParser,
    _split_sequential_orders,
    promote_tactical_move_with_arrival_tail,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams, with a mock parser
    (the FA-50 fixture). The suite pins `SOVEREIGN_SCENARIO=none`, a board
    with no marshals; these rows need Ney at Rhineland and Mack at Swabia."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def parse(text):
    """The production call shape: `parser.parse(text, llm_game_state, world=)`."""
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


def swallowed(result):
    """The memo's verdict: the tail REPLACED the head."""
    cmd = result.get("command") or {}
    return (cmd.get("action") == "attack" and cmd.get("target") == "Mack"
            and not result.get("is_strategic")
            and not result.get("dropped_sequel"))


# The memo's battery: ten heads, four tail forms, all addressed to Ney at
# Rhineland with Mack visible at Swabia. `bombard` rides the mock chain as an
# `attack` whose bombardment is routed by the raw verb, so the bare head's
# own parse is the reference for every row rather than a hand-typed action.
HEADS = ["fortify", "scout Swabia", "drill your men", "defend", "retreat",
         "unfortify", "form square", "garrison Rhineland", "bombard Mack",
         "recruit infantry"]
TAILS = [" then attack Mack", ", then attack Mack", " and then attack Mack",
         "; attack Mack"]
SHAPES = [f"Ney, {head}{tail}" for head in HEADS for tail in TAILS]


# ═══════════════════════════════════════════════════════════════════════
# (a) The forty shapes — 40 SWALLOWED → 0
# ═══════════════════════════════════════════════════════════════════════

class TestTheFortyShapes:

    @pytest.mark.parametrize("text", SHAPES)
    def test_the_head_keeps_its_order_and_the_tail_is_reported(self, shipped, text):
        head = text[:text.index(" then ")] if " then " in text else text.split(";")[0]
        head = head.rstrip(",").rstrip()
        if head.endswith(" and"):
            head = head[:-4]
        reference = parse(head)["command"]
        result = parse(text)
        assert result["success"], result
        assert not swallowed(result), text
        assert result["command"]["action"] == reference["action"], text
        assert result["command"]["target"] == reference["target"], text
        assert not result.get("is_strategic"), text
        assert result.get("dropped_sequel") == "attack Mack", text
        assert "attack Mack" in (result.get("warning") or ""), text
        assert "One order at a time" in (result.get("warning") or ""), text

    def test_none_of_the_forty_is_swallowed(self, shipped):
        """The memo's kill criterion 2: a PARTIAL fix is worse than none —
        it teaches the player that some compounds are safe."""
        eaten = [text for text in SHAPES if swallowed(parse(text))]
        assert eaten == [], eaten

    def test_the_helper_splits_the_headline(self):
        assert _split_sequential_orders("Ney, fortify then attack Mack") == (
            "Ney, fortify", "attack Mack")

    def test_a_split_head_carries_no_dangling_conjunction(self):
        """`and then` is consumed as one boundary. The old boundary left
        "and" on the head ("Ney, scout Swabia and"), and when the tail was
        an attack verb the exemption then read the phantom "Swabia And"."""
        assert _split_sequential_orders(
            "Ney, scout Swabia and then attack Mack") == ("Ney, scout Swabia",
                                                          "attack Mack")


# ═══════════════════════════════════════════════════════════════════════
# The headline at the endpoint — the corps does what it was told
# ═══════════════════════════════════════════════════════════════════════

class TestTheHeadlineAtTheEndpoint:

    def test_a_cautious_marshal_fortifies_and_does_not_fight(self, shipped):
        """The memo's headline, re-measured on the corps that will obey a
        fortify. Before the fix Davout would have marched into Swabia."""
        _client, world = shipped
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious", davout.personality
        location, strength = davout.location, davout.strength
        reply = run(shipped, "Davout, fortify then attack Mack")
        davout = M.world.get_marshal("Davout")
        assert reply.get("success") is True, reply.get("message")
        assert not reply.get("battle_report"), reply.get("message")
        assert davout.fortified is True
        assert (davout.location, davout.strength) == (location, strength)
        assert davout.strategic_order is None
        message = reply.get("message") or ""
        assert "One order at a time" in message, message
        assert '"attack Mack"' in message, message

    def test_an_aggressive_marshal_objects_to_the_head_not_the_tail(self, shipped):
        """Ney firmly objects to sitting idle — to the FORTIFY, the order he
        was given. Before the fix there was nothing to object to: the tail
        had replaced the head and he was already marching. No battle, no
        movement, no men lost, and the tail is still reported."""
        _client, world = shipped
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        before = (ney.location, ney.strength, ney.fortified,
                  world.actions_remaining)
        reply = run(shipped, "Ney, fortify then attack Mack")
        ney = M.world.get_marshal("Ney")
        assert not reply.get("battle_report"), reply.get("message")
        assert reply.get("pending_objection"), reply
        assert (ney.location, ney.strength, ney.fortified,
                M.world.actions_remaining) == before
        message = reply.get("message") or ""
        assert "One order at a time" in message, message

    @pytest.mark.parametrize("command", [
        "Ney, scout Swabia and then attack Mack",
        "Ney, scout Swabia; attack Mack",
        "Ney, scout Swabia, then attack Mack",
    ])
    def test_a_scout_head_scouts_on_every_boundary_token(self, shipped, command):
        _client, world = shipped
        ney = world.get_marshal("Ney")
        location, strength, ap = ney.location, ney.strength, world.actions_remaining
        reply = run(shipped, command)
        ney = M.world.get_marshal("Ney")
        assert reply.get("success") is True, reply.get("message")
        assert not reply.get("battle_report"), command
        assert (ney.location, ney.strength) == (location, strength)
        assert M.world.actions_remaining == ap - 1
        message = reply.get("message") or ""
        assert "scouts Swabia" in message, message
        assert "One order at a time" in message, message


# ═══════════════════════════════════════════════════════════════════════
# (b) Must-keep, byte-identical
# ═══════════════════════════════════════════════════════════════════════

class TestMustKeep:

    @pytest.mark.parametrize("text", [
        "Ney, march to Swabia then attack Mack",
        "Ney, advance to Swabia then attack Mack",
        "Ney, march to Vienna then attack",
        "Ney, march to Vienna then attack Wellington",
    ])
    def test_a_march_head_fuses_its_arrival(self, shipped, text):
        result = parse(text)
        assert result["success"], result
        assert result.get("is_strategic") is True
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None
        assert "One order at a time" not in (result.get("warning") or "")

    def test_the_engines_one_condition_stays_one_parse(self, shipped):
        """`until` is the ONE condition the engine implements and
        `parseneg-until-then-attack-holds` is a pinned corpus row."""
        result = parse("Ney, hold until Davout arrives then attack Mack")
        assert result["command"]["action"] == "hold"
        assert result.get("strategic_type") == "HOLD"
        assert result.get("strategic_condition") == {"until_marshal_arrives": "Davout"}
        assert result.get("dropped_sequel") is None
        reply = run(shipped, "Ney, hold until Davout arrives then attack Mack")
        assert "will hold" in (reply.get("message") or "")
        assert "One order at a time" not in (reply.get("message") or "")

    def test_a_stand_still_head_still_splits(self, shipped):
        """FA-7's own case, the one the old exemption DID cover."""
        result = parse("Ney, wait for Davout then attack Mack")
        assert result["command"]["action"] == "wait"
        assert result.get("dropped_sequel") == "attack Mack"

    def test_the_cr2_helper_pins_hold(self):
        assert _split_sequential_orders("march to Vienna then attack") is None
        assert _split_sequential_orders("march to Vienna and then attack") is None
        assert _split_sequential_orders("march to Vienna then attack Mack") is None
        assert _split_sequential_orders("attack Bern, then hold your positions") == (
            "attack Bern", "hold your positions")


# ═══════════════════════════════════════════════════════════════════════
# (c) The boundary tokens — `and then` names a province, `;` keeps the arrival
# ═══════════════════════════════════════════════════════════════════════

class TestTheBoundaryTokens:

    @pytest.mark.parametrize("region", ["Swabia", "Vienna", "Bohemia"])
    def test_and_then_yields_a_real_province(self, shipped, region):
        _client, world = shipped
        result = parse(f"Ney, march to {region} and then attack Mack")
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("attack_on_arrival") is True
        assert result["command"]["target"] == region
        assert result["command"]["target"] in world.regions

    def test_the_cr2_pins_own_sentence_no_longer_reads_vienna_and(self, shipped):
        """`test_split_helper_attack_on_arrival_not_split` asserted the
        helper's verdict on "march to Vienna and then attack" and never
        looked at the destination it produced: "Vienna And"."""
        result = parse("Ney, march to Vienna and then attack")
        assert result["command"]["target"] == "Vienna"

    def test_a_semicolon_keeps_the_arrival(self, shipped):
        result = parse("Ney, march to Swabia; attack Mack")
        assert result.get("strategic_type") == "MOVE_TO"
        assert result["command"]["target"] == "Swabia"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None

    # ── the three unit seams, pinned directly so belt and braces cannot
    #    mask each other in the mutation sweep ─────────────────────────────
    def test_strip_conditions_consumes_and_then(self):
        assert sp._strip_conditions("march to vienna and then attack mack") == "march to vienna"
        assert sp._strip_conditions(
            "march to vienna and then engage the austrians") == "march to vienna"
        assert sp._strip_conditions("march to vienna then attack") == "march to vienna"

    def test_clean_target_text_drops_a_dangling_conjunction(self):
        assert sp._clean_target_text("vienna and") == "vienna"
        assert sp._clean_target_text("vienna then") == "vienna"
        assert sp._clean_target_text("belgium and attack") == "belgium"

    def test_the_arrival_hint_reads_a_boundary(self):
        assert sp._detect_attack_on_arrival("march to swabia; attack mack") is True
        assert sp._detect_attack_on_arrival("march to swabia then assault mack") is True
        assert sp._detect_attack_on_arrival("march to swabia and then attack") is True
        assert sp._detect_attack_on_arrival("march to swabia and attack") is True
        assert sp._detect_attack_on_arrival("march to swabia") is False
        # "Holland" ends in the conjunction's letters and is not a boundary.
        assert sp._detect_attack_on_arrival("march to holland") is False


# ═══════════════════════════════════════════════════════════════════════
# (d) The named corpus rows — green with their assertions UNEDITED
# ═══════════════════════════════════════════════════════════════════════

FROZEN_EXPECTED = {
    "cr2-march-to-vienna-then-attack-not-split": {
        "success": True, "marshal": "Ney", "strategic_type": "MOVE_TO"},
    "cr2-march-then-attack-named-object-not-split": {
        "success": True, "marshal": "Ney", "target": "Vienna",
        "strategic_type": "MOVE_TO"},
    "parseneg-until-then-attack-holds": {
        "success": True, "action": "hold", "strategic_type": "HOLD"},
    "fa7-hold-here-and-attack-next-turn-holds": {"success": True, "action": "hold"},
    "fa7-scout-and-next-turn-attack-scouts": {"success": True, "action": "scout"},
    "fa7-wait-for-then-attack-does-not-fight": {"success": True, "not_action": "attack"},
    "secure-and-hold-vienna": {"strategic_type": "HOLD"},
    "defend-and-hold-belgium": {"strategic_type": "HOLD"},
    "fa50-attack-and-hold-keeps-the-attack": {"success": True, "action": "attack"},
}


class TestTheNamedCorpusRowsAreUnedited:

    @pytest.fixture(scope="class")
    def corpus_index(self):
        corpus = load_corpus()
        return {e["id"]: e for e in corpus["entries"]}

    @pytest.mark.parametrize("entry_id", sorted(FROZEN_EXPECTED))
    def test_the_assertion_is_the_one_the_memo_named(self, corpus_index, entry_id):
        assert corpus_index[entry_id]["expected"] == FROZEN_EXPECTED[entry_id]

    @pytest.mark.parametrize("entry_id", sorted(FROZEN_EXPECTED))
    def test_the_row_is_green_on_every_world_it_names(self, corpus_index, entry_id,
                                                      monkeypatch):
        monkeypatch.setenv("LLM_MODE", "mock")
        parser = CommandParser(use_real_llm=False)
        entry = corpus_index[entry_id]
        for world_key in worlds_for_entry(entry):
            world = build_world(world_key)
            mismatches = evaluate_entry(parser, entry, world_key, world,
                                        build_llm_game_state(world))
            assert mismatches == [], (entry_id, world_key, mismatches)


# ═══════════════════════════════════════════════════════════════════════
# (e) The sensitivity arm — restore the old predicate and the battery reds
# ═══════════════════════════════════════════════════════════════════════

class TestTheSensitivityArm:
    """`python -m backend.ai.parser_eval` reports 688/688 with the lever UP
    and 688/688 with it DOWN (measured September 22, 2026), so a green corpus
    is not evidence for this slice. This arm is."""

    def test_the_lever_is_up(self):
        assert parser_mod.TAIL_FUSES_ONLY_ONTO_A_MARCH is True

    def test_at_least_thirty_of_forty_red_without_the_fix(self, shipped, monkeypatch):
        monkeypatch.setattr(parser_mod, "TAIL_FUSES_ONLY_ONTO_A_MARCH", False)
        eaten = [text for text in SHAPES if swallowed(parse(text))]
        assert len(eaten) >= 30, (len(eaten), eaten)

    def test_the_lever_reproduces_the_old_helper_verdict(self, monkeypatch):
        monkeypatch.setattr(parser_mod, "TAIL_FUSES_ONLY_ONTO_A_MARCH", False)
        assert _split_sequential_orders("Ney, fortify then attack Mack") is None
        assert _split_sequential_orders("Ney, wait for Davout then attack Mack") == (
            "Ney, wait for Davout", "attack Mack")

    def test_the_lever_governs_the_rider_and_the_and_arm_too(self, shipped, monkeypatch):
        """False must reproduce the pre-slice behaviour at EVERY seam this
        slice touched, or the arm proves less than it claims."""
        monkeypatch.setattr(parser_mod, "TAIL_FUSES_ONLY_ONTO_A_MARCH", False)
        assert swallowed(parse("Ney, move to Swabia then attack Mack"))
        result = parse("Ney, march to Swabia and attack Mack")
        assert result.get("dropped_sequel") == "attack Mack"


# ═══════════════════════════════════════════════════════════════════════
# The rider (CQ-9) — `move to` / `go to` with an arrival tail is the march
# ═══════════════════════════════════════════════════════════════════════

class TestTheTacticalMoveRider:

    @pytest.mark.parametrize("text", [
        "Ney, move to Swabia then attack Mack",
        "Ney, move to Swabia, then attack Mack",
        "Ney, move to Swabia and then attack Mack",
        "Ney, move to Swabia; attack Mack",
        "Ney, move to Swabia and attack Mack",
        "Ney, go to Swabia then attack Mack",
    ])
    def test_the_compound_is_the_march_idiom(self, shipped, text):
        result = parse(text)
        assert result["success"], result
        assert result.get("strategic_type") == "MOVE_TO"
        assert result["command"]["target"] == "Swabia"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None
        assert not swallowed(result)

    def test_the_typed_text_stays_the_record(self, shipped):
        """R1-11: `raw_input` / `raw_command` carry what the player wrote."""
        typed = "Ney, move to Swabia then attack Mack"
        result = parse(typed)
        assert result["raw_input"] == typed
        assert result["command"]["raw_command"] == typed
        assert promote_tactical_move_with_arrival_tail(typed) == (
            "Ney, march to Swabia then attack Mack")

    def test_a_bare_tactical_move_stays_tactical(self, shipped):
        """The documented design (strategic_parser's header; the pin
        `test_strategic_parser::test_move_is_not_strategic`): bare `move to`
        is the 1-AP tactical move and the executor auto-upgrades a distant
        one. The rider is COMPOUND-ONLY by that measurement."""
        result = parse("Ney, move to Swabia")
        assert result["command"]["action"] == "move"
        assert not result.get("is_strategic")
        assert promote_tactical_move_with_arrival_tail("Ney, move to Swabia") == (
            "Ney, move to Swabia")

    def test_the_adjacent_costs_that_keep_the_rider_compound_only(self, shipped):
        """Measured: an adjacent `move to` is 1 AP; `march to` the same
        province is a 2-AP standing order. Unifying the bare forms at the
        parse layer would double the price of the game's most basic order —
        a balance decision, not this row's. If this pin is ever flipped,
        flip it consciously with that price on the record."""
        _client, world = shipped
        rhine = world.get_region("Rhineland")
        neighbour = next(r for r in rhine.adjacent_regions
                         if world.get_region(r).controller == "France")
        ap = world.actions_remaining
        run(shipped, f"Ney, move to {neighbour}")
        move_cost = ap - M.world.actions_remaining
        M._reset_world_state()
        ap = M.world.actions_remaining
        run(shipped, f"Ney, march to {neighbour}")
        march_cost = ap - M.world.actions_remaining
        assert (move_cost, march_cost) == (1, 2)

    def test_a_support_idiom_is_not_promoted(self, shipped):
        """`move to reinforce Davout` is already a standing SUPPORT; the
        promotion leaves any head that is already an order alone, and the
        `and` arm splits it because SUPPORT cannot carry an arrival."""
        text = "Ney, move to reinforce Davout and attack Mack"
        assert promote_tactical_move_with_arrival_tail(text) == text
        result = parse(text)
        assert result.get("strategic_type") == "SUPPORT"
        assert result["command"]["target"] == "Davout"
        assert result.get("dropped_sequel") == "attack Mack"

    def test_the_promoted_order_reaches_the_executor(self, shipped):
        """Ney, not Davout: a cautious marshal raises a STRATEGIC objection
        to marching on an enemy-held province, which is the objection flow
        and not this seam. Ney's order is created before the contact
        interrupt, and it is the march with its arrival, not a battle."""
        _client, world = shipped
        strength = world.get_marshal("Ney").strength
        reply = run(shipped, "Ney, move to Swabia then attack Mack")
        ney = M.world.get_marshal("Ney")
        assert reply.get("success") is True, reply.get("message")
        assert reply.get("strategic_type") == "MOVE_TO", reply
        assert not reply.get("battle_report"), reply.get("message")
        assert ney.strength == strength
        assert ney.strategic_order is not None
        assert ney.strategic_order.command_type == "MOVE_TO"
        assert ney.strategic_order.attack_on_arrival is True
        assert "One order at a time" not in (reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════
# The `and` form of the arrival idiom — FA-50's arm under the same rule
# ═══════════════════════════════════════════════════════════════════════

class TestTheAndForm:

    def test_march_and_attack_fuses(self, shipped):
        """`_detect_attack_on_arrival`'s own "and attack" hint. FA-50's `and`
        arm had no exemption, so this split into a march plus a "One order
        at a time" note while the `then` form fused (measured on this HEAD)."""
        result = parse("Ney, march to Swabia and attack Mack")
        assert result.get("strategic_type") == "MOVE_TO"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None

    def test_a_non_march_head_still_splits_on_and(self, shipped):
        result = parse("Ney, fortify and attack Mack")
        assert result["command"]["action"] == "fortify"
        assert result.get("dropped_sequel") == "attack Mack"

    def test_fa50s_own_case_is_untouched(self, shipped):
        result = parse("Ney, attack Mack and hold Rhineland")
        assert result["command"]["action"] == "attack"
        assert result["command"]["target"] == "Mack"
        assert result.get("dropped_sequel") == "hold Rhineland"


# ═══════════════════════════════════════════════════════════════════════
# Only a head that can CARRY an arrival fuses one
# ═══════════════════════════════════════════════════════════════════════

class TestOnlyACarryingHeadFuses:

    def test_the_carrying_set_is_the_two_types_the_executor_reads(self):
        assert sp.ARRIVAL_CARRYING_TYPES == frozenset({"MOVE_TO", "PURSUE"})

    def test_a_pursuit_carries_its_arrival(self, shipped):
        result = parse("Ney, pursue Mack then attack him")
        assert result.get("strategic_type") == "PURSUE"
        assert result.get("attack_on_arrival") is True
        assert result.get("dropped_sequel") is None

    def test_a_support_head_reports_the_tail(self, shipped):
        """SUPPORT's executor never reads the flag: fused, the attack was
        stamped and then lost one stage later than the swallow."""
        result = parse("Ney, support Davout then attack Mack")
        assert result.get("strategic_type") == "SUPPORT"
        assert result.get("dropped_sequel") == "attack Mack"

    def test_a_march_with_no_destination_reports_the_tail(self, shipped):
        result = parse("Ney, withdraw then attack Mack")
        assert result["command"]["action"] == "retreat"
        assert result.get("dropped_sequel") == "attack Mack"
        assert not swallowed(result)

    def test_until_rides_a_standing_order_only(self, shipped):
        """A bare `until` arm re-opened the swallow here (measured)."""
        result = parse("Ney, fortify until Davout arrives then attack Mack")
        assert result["command"]["action"] == "fortify"
        assert result.get("dropped_sequel") == "attack Mack"
        assert not swallowed(result)

    def test_the_predicate_reads_the_routing_table(self):
        assert sp.clause_can_carry_an_arrival("Ney, march to Swabia") is True
        assert sp.clause_can_carry_an_arrival("Ney, pursue Mack") is True
        assert sp.clause_can_carry_an_arrival("Ney, fall back to Alsace") is True
        assert sp.clause_can_carry_an_arrival("Ney, withdraw") is False
        assert sp.clause_can_carry_an_arrival("Ney, hold Lorraine") is False
        assert sp.clause_can_carry_an_arrival("Ney, support Davout") is False
        assert sp.clause_can_carry_an_arrival("Ney, fortify") is False
        assert sp.clause_is_a_standing_order("Ney, hold until Davout arrives") is True
        assert sp.clause_is_a_standing_order("Ney, fortify until Davout arrives") is False


# ═══════════════════════════════════════════════════════════════════════
# (f) Nothing reaches the engine — a parser slice, and the AI does not type
# ═══════════════════════════════════════════════════════════════════════

class TestNothingReachesTheEngine:
    """`BASELINE_SERIES` and M1–M7 were run byte-identical without re-record
    this session (63 pins). The structural half: the strategic text reader
    has exactly one production caller, the player's parser, so no AI path
    can see any of the text rules this slice changed."""

    def test_the_strategic_text_reader_has_one_caller(self):
        backend = os.path.join(REPO_ROOT, "backend")
        callers = set()
        for root, _dirs, files in os.walk(backend):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as handle:
                    src = handle.read()
                if re.search(r"(?<![\w.])detect_strategic_command\(", src):
                    callers.add(os.path.relpath(path, REPO_ROOT).replace(os.sep, "/"))
        assert callers == {"backend/commands/parser.py",
                           "backend/ai/strategic_parser.py"}, callers
