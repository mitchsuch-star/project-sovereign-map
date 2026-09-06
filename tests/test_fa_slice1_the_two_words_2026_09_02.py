"""Final Whole-Game Audit — slice 1, "The Two Words".

The parsing family a first-time player meets in an hour, all of it measured
on the SHIPPED mock-default build before a line was written.

* **FA-7** (P1, the strongest row in the audit) — the guards knew every way
  to say *not that* and none at all to say *not YET*, so `Ney, delay the
  attack` fought a real battle at confidence 0.95. Above the 0.7 escalation
  gate, so no key in any mode could have corrected it. Nine phrasings
  reproduce; the row files five.
* **FA-6** (P2, amended from P1 on an owner challenge — AP do not carry
  over) — a non-command advanced the turn irreversibly, and inconsistently:
  `what happens next turn` ran the enemy phase, `what should we do next
  turn?` did not.
* **FA-N22** — the client's gate was the same substring test, so the two had
  to be narrowed TOGETHER; narrowing either alone leaves the other
  classifying.
* **FA-11** (P2) — `lift the blockade` PUT THE FLEET TO SEA. So did `raise`,
  `end`, `call off`, `break` and `stop`. And `Ney, blockade Vienna` — a
  siege phrasing — stood the fleet out and charged for it.
* **FA-22** (P2) — an addressee the roster cannot bind is dropped and the
  order auto-assigned: `the Iron Marshal, attack Mack` sent SOULT, into a
  real battle, in the same response.
* **FA-50** (P3, re-read P2) — the title says the second clause is dropped;
  measured, it is EXECUTED BY THE FIRST MARSHAL in place of the order given.
* **FA-54** (P3, re-read P2) — `Ney, march to Mainz` marches six provinces
  WEST to Maine and says nothing, while `move to Mainz` discloses.

Every one of these is driven through the real `POST /command` seam on a
fresh 1805 boot with the mock parser, because four of the six rows have a
defect the parser alone cannot show.
"""

import os

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.ai.clause_guards import (
    END_TURN_PHRASINGS,
    is_bare_end_turn,
    strip_deferred_clauses,
)
from backend.commands.parser import CommandParser

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams, with a mock parser.

    The suite pins `SOVEREIGN_SCENARIO=none` (the bare flag world), which has
    no marshals and no fleet — a board these rows are not about. `.env` sets
    `LLM_MODE=anthropic`, so the parser swap is also what keeps this free.
    """
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


# ═══════════════════════════════════════════════════════════════════════
# FA-7 — "not YET" is not "not that"
# ═══════════════════════════════════════════════════════════════════════

class TestADeferredOrderIsNotFoughtNow:

    DEFERRALS = [
        "Ney, delay the attack",          # the row's headline
        "Ney, postpone the attack",
        "Ney, defer the attack",          # not in the row's list
        "Ney, put off the attack",        # not in the row's list
        "Ney, hold off on attacking Mack",
        "Ney, attack Mack later",
        "Ney, attack Mack tomorrow",      # not in the row's list
        "Ney, attack Mack next turn",     # the FA-6 overlap
    ]

    @pytest.mark.parametrize("command", DEFERRALS)
    def test_no_battle_is_fought_and_nothing_is_spent(self, shipped, command):
        _client, world = shipped
        ney = world.get_marshal("Ney")
        before = (ney.location, ney.strength, world.actions_remaining,
                  world.current_turn)
        reply = run(shipped, command)
        ney = M.world.get_marshal("Ney")
        assert reply.get("success") is False, reply.get("message")
        assert not reply.get("battle_report"), command
        assert not reply.get("turn_ended"), command
        assert (ney.location, ney.strength, M.world.actions_remaining,
                M.world.current_turn) == before

    def test_the_refusal_is_a_deferral_not_a_prohibition(self, shipped):
        """A deferral is a DIFFERENT failure and must not wear a
        prohibition's words: the player did not forbid the order, they named
        a turn the engine cannot hold a dispatch until."""
        message = run(shipped, "Ney, attack Mack later").get("message") or ""
        assert "no drawer for tomorrow" in message, message
        assert "no order goes out" not in message, message
        # …and it names what to do instead, including the one thing the
        # player might actually have meant.
        assert "end turn" in message

    def test_a_prohibition_still_answers_as_a_prohibition(self, shipped):
        """The negative control. Negation wins the label when both fire."""
        message = run(shipped, "Ney, never attack Mack").get("message") or ""
        assert "no order goes out" in message, message

    @pytest.mark.parametrize("command,action_word", [
        ("Ney, hold here and attack next turn", "hold"),
        ("Ney, scout Swabia and next turn attack", "scout"),
    ])
    def test_a_coordinate_order_for_this_turn_survives(
            self, shipped, command, action_word):
        """The scoping half, and the mirror of PARSE-NEG's own rule: a
        deferral scopes to its clause. The adverb CLOSES the clause in the
        first and LEADS it in the second — same rule either way."""
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert not reply.get("turn_ended")
        assert not reply.get("battle_report")
        assert action_word in (reply.get("message") or "").lower(), reply

    def test_the_deferral_guard_blanks_in_place(self):
        """Index-preserving, like every guard in the module — every
        position-aware rule downstream indexes into the command text."""
        text = "Ney, attack Mack later"
        effective, applied = strip_deferred_clauses(text)
        assert applied is True
        assert len(effective) == len(text)
        assert effective.startswith("Ney,")
        assert "attack" not in effective

    def test_a_sentence_with_no_deferral_is_returned_unchanged(self):
        text = "Ney, attack Mack"
        assert strip_deferred_clauses(text) == (text, False)


class TestWaitForThenAttackDoesNotAttack:
    """FA-7's third clause. `_ATTACK_ON_ARRIVAL_TAIL_RE` refuses to split any
    tail beginning with an attack verb, so the whole sentence stayed one
    parse and `attack` outranked `wait`. Attack-on-arrival is a MOVEMENT
    idiom: a first clause ordering the marshal to STAND STILL carries no
    arrival for it to protect."""

    def test_it_fights_nothing_this_turn(self, shipped):
        _client, world = shipped
        before = (world.get_marshal("Ney").location, world.actions_remaining)
        reply = run(shipped, "Ney, wait for Davout then attack Mack")
        assert not reply.get("battle_report"), reply.get("message")
        assert (M.world.get_marshal("Ney").location,
                M.world.actions_remaining) == before

    def test_the_dropped_tail_is_declared(self, shipped):
        message = run(shipped,
                      "Ney, wait for Davout then attack Mack").get("message")
        assert "One order at a time" in (message or ""), message

    def test_the_engines_own_until_shape_is_untouched(self, shipped):
        """`until` is the ONE condition the engine implements, and
        `Ney, hold until Davout arrives then attack` is a pinned corpus row.
        It must stay a single parse."""
        reply = run(shipped, "Ney, hold until Davout arrives then attack")
        assert reply.get("success") is True
        assert "will hold" in (reply.get("message") or "")
        assert "One order at a time" not in (reply.get("message") or "")

    def test_attack_on_arrival_still_rides_a_march(self, shipped):
        reply = run(shipped, "Ney, march to Vienna then attack")
        assert "One order at a time" not in (reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════
# FA-6 + FA-N22 — the turn ends when the player says so, and only then
# ═══════════════════════════════════════════════════════════════════════

class TestOnlyABareEndTurnEndsTheTurn:

    NOT_COMMANDS = [
        "what happens next turn",
        "we will decide next turn",
        "next turn Ney attacks Mack",
        "Davout, attack next turn",
        "recruit next turn",
    ]

    @pytest.mark.parametrize("command", NOT_COMMANDS)
    def test_a_sentence_that_merely_mentions_it_holds_the_turn(
            self, shipped, command):
        _client, world = shipped
        before = (world.current_turn, world.actions_remaining)
        reply = run(shipped, command)
        assert not reply.get("turn_ended"), command
        assert not reply.get("enemy_phase"), command
        assert (M.world.current_turn, M.world.actions_remaining) == before

    @pytest.mark.parametrize("command", [
        "end turn", "next turn", "END TURN", "  next turn  ", "next turn.",
        "end_turn",
    ])
    def test_every_bare_form_still_ends_it(self, shipped, command):
        reply = run(shipped, command)
        assert reply.get("turn_ended"), command
        assert M.world.current_turn == 2

    def test_the_order_survives_and_the_turn_does_not_end(self, shipped):
        """`Ney attack Mack and end turn`. The row's own behaviour_test asks
        for AP unchanged here — which would mean throwing the attack away,
        exactly what the defect did. Executing it and holding the turn is
        the half that loses nothing."""
        reply = run(shipped, "Ney attack Mack and end turn")
        assert not reply.get("turn_ended")
        assert reply.get("battle_report"), reply.get("message")
        assert M.world.actions_remaining == 3

    def test_until_next_turn_is_a_condition_not_an_end_turn(self, shipped):
        reply = run(shipped, "Davout, fortify until next turn")
        assert not reply.get("turn_ended")
        assert "fortifies" in (reply.get("message") or "").lower()


class TestTheClientGateSpeaksTheSameVocabulary:
    """FA-N22. A client-side gate on a server-side vocabulary must speak that
    vocabulary — and the shipped client's was COARSER than the parser it
    mirrors, so `Davout, fortify until next turn` fortified on the server and
    ended the turn in the client. This EVALUATES both gates against the same
    fixture set rather than grepping for keywords."""

    FIXTURES = [
        ("end turn", True), ("next turn", True), ("end_turn", True),
        ("END TURN", True), ("  next turn  ", True), ("next turn.", True),
        ("Davout, fortify until next turn", False),
        ("what happens next turn", False),
        ("Ney, attack Mack next turn", False),
        ("end turn now", False),
        ("Murat, wait until next turn", False),
        # FA-R4 (slice 14): the desk may be ADDRESSED. These are the arms
        # that make the parity pin bind to the new behaviour rather than
        # merely agreeing about it.
        ("Berthier, end turn", True),
        ("Sire, end turn", True),
        ("Berthier, next turn", True),
        ("Berthier: end turn", True),
        ("berthier , end turn", True),
        # Still not an end turn: a second address is not stripped, and an
        # addressed ORDER is an order.
        ("Berthier, Sire, end turn", False),
        ("Berthier, hold Rhineland", False),
        ("Ney, end turn", False),
    ]

    @staticmethod
    def _client_gate(command):
        """The client's predicate, re-derived from `main.gd` itself.

        FA-R4 (slice 14) made this STRIP-AWARE, and it had to. The gate now
        removes one leading address to the desk before comparing, and the
        original derivation harvested EQUALITY NEEDLES ONLY — so it agreed
        with the backend on every fixture whether or not the `.gd` carried
        the strip, and deleting the strip again would have left this pin
        green. It was about to go inert for the one behaviour the row adds.

        Both halves are now derived from the source: the equality needles as
        before, and the address vocabulary from the helper's own list. If the
        helper is deleted, `_strip_desk_address(` disappears from the gate's
        body, `stripping` goes False, and the addressed fixtures below fail.
        """
        import re

        path = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        body = src[src.index("func _is_end_turn_phrasing("):]
        body = body[:body.index("func _execute_end_turn():")]
        needles = re.findall(r'c\s*==\s*"([^"]+)"', body)
        assert needles, "the client gate changed shape — re-derive this pin"

        stripping = "_strip_desk_address(" in body
        addresses = []
        if stripping:
            helper = src[src.index("func _strip_desk_address("):]
            helper = helper[:helper.index("\n\n\nfunc ")]
            listed = re.search(r'for\s+\w+\s+in\s+\[([^\]]*)\]', helper)
            assert listed, ("the client's address vocabulary changed shape — "
                            "re-derive this pin")
            addresses = re.findall(r'"([^"]+)"', listed.group(1))
            assert addresses, "the client strips no addresses at all"

        text = command.lower().strip()
        while text and text[-1] in ".!? \t":
            text = text[:-1]
        text = text.strip()
        if stripping:
            for addr in addresses:
                if not text.startswith(addr):
                    continue
                rest = text[len(addr):].lstrip(" \t")
                if rest[:1] in (",", ":"):
                    text = rest[1:].strip()
                    break
        return text in needles

    @pytest.mark.parametrize("command,expected", FIXTURES)
    def test_both_gates_agree(self, command, expected):
        assert is_bare_end_turn(command) is expected, command
        assert self._client_gate(command) is expected, command

    def test_the_client_no_longer_uses_a_substring_test(self):
        path = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        body = src[src.index("func _is_end_turn_phrasing("):]
        body = body[:body.index("func _execute_end_turn():")]
        assert 'c.find("end turn")' not in body
        assert 'c.find("next turn")' not in body

    def test_the_vocabulary_itself_is_unchanged(self):
        """This fix is a NARROWING. `end the turn` is deliberately still not
        a phrasing (it shrugs, as it did before); adding it would be a
        widening rather than this row."""
        assert END_TURN_PHRASINGS == ("end turn", "end_turn", "next turn")


# ═══════════════════════════════════════════════════════════════════════
# FA-11 — the fleet obeys the order it was given
# ═══════════════════════════════════════════════════════════════════════

def _posture(world):
    return (world.fleets.get("France") or {}).get("posture")


def _set_posture(world, value):
    world.fleets["France"]["posture"] = value


class TestTheBlockadeInversionIsObeyed:

    INVERSIONS = ["lift the blockade", "raise the blockade",
                  "end the blockade", "call off the blockade",
                  "break the blockade", "stop the blockade"]

    @pytest.mark.parametrize("command", INVERSIONS)
    def test_it_lifts_the_blockade(self, shipped, command):
        """Every one of these PUT THE FLEET TO SEA — the opposite of the
        order — for 1 AP. The row lists four verbs; a direction test catches
        eight."""
        _client, world = shipped
        _set_posture(world, "blockade")
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert _posture(M.world) == "guard", command

    @pytest.mark.parametrize("command,expected", [
        ("blockade the enemy", "blockade"),
        ("blockade Britain", "blockade"),
    ])
    def test_the_positive_controls_still_stand_out_to_sea(
            self, shipped, command, expected):
        _client, world = shipped
        _set_posture(world, "guard")
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert _posture(M.world) == expected

    @pytest.mark.parametrize("command,expected", [
        ("guard home waters", "guard"),
        ("recall the fleet", "guard"),
    ])
    def test_the_guard_controls_still_come_home(
            self, shipped, command, expected):
        _client, world = shipped
        _set_posture(world, "blockade")
        assert run(shipped, command).get("success") is True
        assert _posture(M.world) == expected


class TestTheAdmiraltyTakesItsOrdersFromTheEmperor:

    @pytest.mark.parametrize("command", [
        "Ney, blockade Vienna", "Davout, blockade the city",
        "Ney, blockade Mack", "Ney, besiege and blockade Vienna",
    ])
    def test_a_siege_phrasing_never_moves_the_fleet(self, shipped, command):
        """MEMBERSHIP, never truthiness — `blockade Britain` and `guard home
        waters` must survive, and neither is a region or a marshal."""
        _client, world = shipped
        before = world.actions_remaining
        reply = run(shipped, command)
        assert reply.get("success") is False, reply.get("message")
        assert _posture(M.world) == "guard"
        assert M.world.actions_remaining == before

    @pytest.mark.parametrize("command", [
        "the enemy is in home waters",
        "our trade is hurting under the blockade",
        "report on the blockade",
        "Britain threatens our home waters",
    ])
    def test_a_report_is_not_an_order(self, shipped, command):
        """The only guard that catches the class carrying neither a marshal
        nor a province. Driven from BLOCKADE, where a wrong `guard` would
        actually move the fleet."""
        _client, world = shipped
        _set_posture(world, "blockade")
        before = world.actions_remaining
        reply = run(shipped, command)
        assert reply.get("success") is False, reply.get("message")
        assert _posture(M.world) == "blockade", command
        assert M.world.actions_remaining == before

    @pytest.mark.parametrize("command", [
        "send an expedition to Ireland to break the blockade",
        "mount an expedition against the blockade",
        "a diversion against the blockade",
        "embark the army and run the blockade",
    ])
    def test_a_sibling_errand_reaches_its_own_verb(self, shipped, command):
        """Free Ireland and the Grand Diversion, eaten by the arm above them
        in the chain. Both halves yield — the producer's branch order AND
        the executor's own rule — so they agree by construction."""
        _client, world = shipped
        _set_posture(world, "guard")
        run(shipped, command)
        assert _posture(M.world) == "guard", command

    def test_a_redundant_posture_is_not_a_paid_no_op(self, shipped):
        """Without this the row's own behaviour_test cannot pass: `lift the
        blockade` from a fleet already guarding prepended "The fleet already
        holds that station." and still charged 1 AP."""
        _client, world = shipped
        _set_posture(world, "guard")
        before = world.actions_remaining
        reply = run(shipped, "lift the blockade")
        assert reply.get("success") is False
        assert M.world.actions_remaining == before

    def test_the_structured_door_is_still_open(self, shipped):
        """The AI/wizard path. Measured production-DEAD today — `posture` is
        absent from `providers.PARSE_TOOL` and no producer writes it — so
        the raw-text rule is the whole implementation. The door stays open,
        and is NOT subject to the typed idempotence gate."""
        from backend.commands.executor import CommandExecutor

        _client, world = shipped
        _set_posture(world, "guard")
        result = CommandExecutor()._naval._execute_set_fleet_posture(
            {"action": "set_fleet_posture", "posture": "guard"},
            {"world": world})
        assert result["success"] is True, result


# ═══════════════════════════════════════════════════════════════════════
# FA-22 — an addressee the roster cannot bind is a refusal
# ═══════════════════════════════════════════════════════════════════════

class TestAnUnboundAddresseeRefuses:

    ADDRESSED = [
        "the Iron Marshal, attack Mack",
        "Iron Marshal, attack Mack",
        "Berthier, attack Mack",
        "Prince of Moskowa, attack Mack",
        "the cavalry, attack Mack",
        "the reserve, attack Mack",
    ]

    @pytest.mark.parametrize("command", ADDRESSED)
    def test_nobody_else_is_sent(self, shipped, command):
        """Every one of these sent SOULT into a real battle, in the same
        response, with the only disclosure being his name inside the MUSTER
        line."""
        _client, world = shipped
        before = {n: (m.location, m.strength)
                  for n, m in world.marshals.items()
                  if m.nation == world.player_nation}
        ap_before = world.actions_remaining
        reply = run(shipped, command)
        after = {n: (m.location, m.strength)
                 for n, m in M.world.marshals.items()
                 if m.nation == M.world.player_nation}
        assert reply.get("success") is False, reply.get("message")
        assert not reply.get("battle_report"), command
        assert after == before, command
        assert M.world.actions_remaining == ap_before

    def test_the_refusal_names_what_the_player_typed(self, shipped):
        message = run(shipped, "the Iron Marshal, attack Mack").get("message")
        assert "no 'Iron Marshal' in the order of battle" in (message or "")

    @pytest.mark.parametrize("command", [
        "Berthier, retreat", "the Iron Marshal, retreat",
    ])
    def test_the_army_wide_retreat_is_covered_too(self, shipped, command):
        """Wider than the row: this ran a WHOLE-ARMY retreat — eight
        marshals, 2,270 men, ZERO AP, no confirm — while `Ney, retreat`
        costs none."""
        _client, world = shipped
        before = sum(m.strength for m in world.marshals.values()
                     if m.nation == world.player_nation)
        run(shipped, command)
        after = sum(m.strength for m in M.world.marshals.values()
                    if m.nation == M.world.player_nation)
        assert after == before, command

    def test_the_scout_arm_is_covered_too(self, shipped):
        _client, world = shipped
        before = world.actions_remaining
        reply = run(shipped, "Berthier, scout Swabia")
        assert reply.get("success") is False
        assert M.world.actions_remaining == before

    def test_no_raw_error_string_reaches_the_player(self, shipped):
        """`the Guard, attack Mack` — the ONE shape the guard cannot claim,
        because the unit's name IS an order verb — answered with the raw
        internal 'Error: No target or world state'."""
        message = run(shipped, "the Guard, attack Mack").get("message") or ""
        assert not message.startswith("Error:"), message
        assert "Berthier" in message

    @pytest.mark.parametrize("command", [
        "attack Mack",                  # CR-6's blessed instant pick
        "retreat",                      # the bare general retreat
        "Ney, attack Mack",
        "Ney, retreat",
        "Marshal Soult, attack Mack",   # CR-0's honorific form
        "Napoleon, attack Mack",        # the sovereign
    ])
    def test_the_bare_and_bound_forms_are_untouched(self, shipped, command):
        assert run(shipped, command).get("success") is True, command

    def test_an_order_is_not_an_addressee(self, shipped):
        """What keeps `attack Bern, then hold your positions` working: its
        pre-comma phrase names a VERB, so nobody was addressed."""
        from backend.commands.executor import CommandExecutor

        _client, world = shipped
        assert CommandExecutor()._unbound_addressee(
            {"type": "auto_assign_attack"},
            {"raw_input": "attack Bern, then hold your positions"},
            world) is None


# ═══════════════════════════════════════════════════════════════════════
# FA-50 — two orders on one line
# ═══════════════════════════════════════════════════════════════════════

class TestTheSecondClauseNeverSuppliesTheAction:

    @pytest.mark.parametrize("command", [
        "Ney, attack Mack and hold Rhineland",
        "Ney, attack Mack and march to Vienna",
        "Ney, attack Mack and Davout scout Swabia",
        "Ney, attack Mack; Davout, support Soult",
    ])
    def test_the_first_order_is_the_one_carried(self, shipped, command):
        """The title says the second clause is 'silently dropped'. Measured,
        it was EXECUTED BY THE FIRST MARSHAL in place of the order given, at
        2 AP, reported as success."""
        reply = run(shipped, command)
        assert reply.get("battle_report"), reply.get("message")
        assert M.world.get_marshal("Ney").location == "Swabia"

    @pytest.mark.parametrize("command", [
        "Ney, attack Mack and hold Rhineland",
        "Ney, attack Mack; Davout, support Soult",
        "Ney, fortify and scout Swabia",
    ])
    def test_the_dropped_tail_is_declared(self, shipped, command):
        assert "One order at a time" in (run(shipped, command).get("message")
                                         or ""), command

    def test_a_targetless_first_clause_still_wins(self, shipped):
        """`Ney, fortify and scout Swabia` — clause 1 carries no object of
        its own, so the split is decided by clause 2 carrying one."""
        reply = run(shipped, "Ney, fortify and scout Swabia")
        assert "scouts Swabia" not in (reply.get("message") or "")

    @pytest.mark.parametrize("command", [
        "Ney, defend and hold", "Ney, fortify and hold position",
        "secure and hold vienna", "defend and hold belgium",
    ])
    def test_the_hold_idioms_are_one_order(self, shipped, command):
        """`llm_client`'s own hold branch enumerates these three verbatim.
        They name an object and are still ONE order, which is why the split
        cannot be widened to a bare `and <verb>` without exempting them."""
        assert "One order at a time" not in (run(shipped, command).get("message")
                                             or ""), command

    def test_the_idiom_list_matches_the_parsers_own(self):
        """A drift pin: the exemption is a copy of `llm_client`'s hold
        keywords and must stay one."""
        path = os.path.join(REPO_ROOT, "backend", "ai", "llm_client.py")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        for idiom in ('"defend and hold"', '"fortify and hold"',
                      '"secure and hold"'):
            assert idiom in src, idiom

    def test_the_address_form_is_not_split(self, shipped):
        """`Ney and Davout, attack Mack` must still muster both. The guard is
        `fast_parse("Ney").action == "unknown"` — incidental and unasserted
        until now, and the muster surface depends on it."""
        reply = run(shipped, "Ney and Davout, attack Mack")
        assert reply.get("battle_report"), reply.get("message")
        assert "One order at a time" not in (reply.get("message") or "")

    def test_a_bare_marshal_name_does_not_parse_as_an_order(self, shipped):
        """The mechanism behind the pin above, asserted directly."""
        _client, world = shipped
        parse = M.parser.llm.fast_parse("Ney", {"world": world})
        assert parse.action == "unknown"


# ═══════════════════════════════════════════════════════════════════════
# FA-54 — the destination the player did not name
# ═══════════════════════════════════════════════════════════════════════

class TestASubstitutedDestinationIsDisclosed:

    @pytest.mark.parametrize("command", [
        "Ney, march to Mainz",   # the strategic route — was SILENT
        "Ney, move to Mainz",    # the tactical route — already disclosed
        "Soult, hold Mainz",     # a STANDING order — was silent
        "Ney, march to Lisboa",
    ])
    def test_the_note_reaches_the_player(self, shipped, command):
        message = run(shipped, command).get("message") or ""
        assert "Our maps read" in message, message

    @pytest.mark.parametrize("command", ["Ney, move to Main",
                                         "Ney, march to Main"])
    def test_a_prefix_exonym_is_disclosed_too(self, shipped, command):
        """The predicate was blind to its own case: `any(len(w) >= 4 and
        (w in _tn or _tn in w))` grounds `main` against `maine`. Main is the
        Frankfurt river line; a player who knows 1805 types it for the same
        reason he types Mainz."""
        assert "Our maps read Maine" in (run(shipped, command).get("message")
                                         or ""), command

    def test_a_refusal_discloses_it_as_well(self, shipped):
        """Measured, the note reached the player on 2 of 8 paths: `Ney, move
        to Lisboa` answered "Cannot enter Lisbon" without ever admitting the
        player had typed Lisboa."""
        message = run(shipped, "Ney, move to Lisboa").get("message") or ""
        assert "Cannot enter Lisbon" in message
        assert "Our maps read Lisbon" in message

    def test_the_standing_hold_no_longer_contradicts_itself(self, shipped):
        """`Soult will hold Maine. Marching to Maine. "Soult, hold Mainz."` —
        the CR-5 rider-(d) verbatim quote and the substituted province
        contradicting each other inside one sentence, on a standing order."""
        message = run(shipped, "Soult, hold Mainz").get("message") or ""
        assert "Soult, hold Mainz" in message
        assert "Our maps read Maine" in message

    @pytest.mark.parametrize("command", [
        "Ney, move to Lorraine", "Soult, hold Lorraine",
    ])
    def test_a_correctly_typed_destination_gets_no_note(self, shipped, command):
        """Or the fix trades a silent march for a chatty one."""
        assert "Our maps read" not in (run(shipped, command).get("message")
                                       or ""), command

    def test_the_two_routes_share_one_helper(self):
        """`move` and `march` disagreeing about disclosing the SAME
        substitution is the CA8-28 two-routes shape one level down. One
        function, imported by both, so they cannot drift again."""
        from backend.commands.movement_executor import (
            destination_grounding_note,
        )
        import backend.commands.strategic_executor as strategic

        assert strategic.destination_grounding_note is destination_grounding_note

    def test_the_helper_grounds_on_exact_tokens(self):
        from backend.commands.movement_executor import (
            destination_grounding_note,
        )

        assert destination_grounding_note("Ney, move to Maine", "Maine") == ""
        assert destination_grounding_note("Ney, move to Main", "Maine") != ""
        # No raw text rides for AI / strategic / mock callers, which
        # synthesize the name and have nothing to disclose.
        assert destination_grounding_note("", "Maine") == ""
        assert destination_grounding_note("Ney, move to Mainz", "") == ""


# ═══════════════════════════════════════════════════════════════════════
# THE ISOLATION PINS
#
# The first mutation sweep of this slice returned TEN INERT pins. Every one
# was the documented pattern: two guards in series, each masking the other,
# so reverting either alone changed nothing. An inert pin proves nothing, so
# each is answered here with a case that reaches ONLY the guard under test —
# never by deleting the mutation.
# ═══════════════════════════════════════════════════════════════════════

class TestTheGuardsAreIsolated:

    # ── FA-7/c: the adverb's clause has an END, not just a start ──────────
    def test_a_clause_after_the_deferred_one_survives(self, shipped):
        """Both earlier cases put the adverb in the LAST clause, where the
        clause end and the end of the line are the same character — so
        blanking to the end of the line was indistinguishable. Here a real
        order follows the deferred clause."""
        effective, applied = strip_deferred_clauses(
            "next turn attack Mack, Ney scout Swabia")
        assert applied is True
        assert "attack" not in effective
        assert "scout Swabia" in effective

    # ── FA-N22/b: the client's OWN strip step, not the emulation's ────────
    def test_the_client_body_still_strips_trailing_punctuation(self):
        """The emulation in `_client_gate` did its own stripping in Python,
        so removing the `.gd`'s strip loop changed nothing it could see."""
        import os

        path = os.path.join(REPO_ROOT, "godot-client", "project-sovereign",
                            "scripts", "main.gd")
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        body = src[src.index("func _is_end_turn_phrasing("):]
        body = body[:body.index("func _execute_end_turn():")]
        assert "c.substr(0, c.length() - 1)" in body, (
            "the client no longer strips trailing punctuation, so "
            "`next turn.` would not end the turn there while it does here")
        assert "while c.length() > 0" in body

    # ── FA-11/c: the producer reorder masks the executor's own yield ──────
    def test_the_posture_rule_yields_to_a_sibling_errand_on_its_own(self):
        """The branch reorder in `llm_client` means these sentences never
        reach `derive_posture` at all — so the executor's own yield was
        untestable through `/command`. Both halves exist so they agree by
        construction; this pins the half the reorder hides."""
        from backend.game_logic.naval import derive_posture

        assert derive_posture(
            "send an expedition to Ireland to break the blockade") is None
        assert derive_posture("a diversion against the blockade") is None
        assert derive_posture("embark the army and run the blockade") is None
        # …and the control: without a sibling errand, the same words derive.
        assert derive_posture("break the blockade") == "guard"

    # ── FA-11/d: the copula arm, masked by the posture-verb arm ───────────
    def test_a_report_carrying_a_posture_verb_is_still_not_an_order(self):
        """"the enemy is in home waters" fails BOTH halves, so removing
        either left it refused. This sentence carries a real posture verb
        and is still a report."""
        from backend.game_logic.naval import sentence_is_an_order

        assert sentence_is_an_order("Britain is blockading our ports") is False
        assert sentence_is_an_order("the fleet is guarding home waters") is False
        assert sentence_is_an_order("how should we guard home waters") is False
        # …and the control.
        assert sentence_is_an_order("guard home waters") is True

    # ── FA-22/c and /e: masked by the order-verb and marshal-set guards ───
    def test_a_bare_command_is_not_an_addressee_at_all(self, shipped):
        """Defence in depth, and measured to be exactly that: every BARE
        order begins with a verb, so the order-verb guard would refuse it
        anyway. This reaches the comma test directly."""
        from backend.commands.executor import CommandExecutor

        _client, world = shipped
        executor = CommandExecutor()
        assert executor._unbound_addressee(
            {"type": "auto_assign_attack"}, {"raw_input": "Berthier"},
            world) is None

    def test_a_phrase_that_names_a_marshal_is_bound(self, shipped):
        """`Ney, attack Mack` sets `command["marshal"]`, so the earlier guard
        returned first and the roster loop was never reached."""
        from backend.commands.executor import CommandExecutor

        _client, world = shipped
        executor = CommandExecutor()
        assert executor._unbound_addressee(
            {"type": "auto_assign_attack"},
            {"raw_input": "Ney, attack Mack"}, world) is None
        assert executor._unbound_addressee(
            {"type": "auto_assign_attack"},
            {"raw_input": "Marshal Soult, attack Mack"}, world) is None
        # …and the control, at the same seam.
        assert executor._unbound_addressee(
            {"type": "auto_assign_attack"},
            {"raw_input": "Berthier, attack Mack"}, world) == "Berthier"

    def test_an_enemy_marshal_is_not_one_of_ours(self, shipped):
        """The roster loop is scoped to the PLAYER's marshals."""
        from backend.commands.executor import CommandExecutor

        _client, world = shipped
        assert CommandExecutor()._unbound_addressee(
            {"type": "auto_assign_attack"},
            {"raw_input": "Mack, attack Ney"}, world) == "Mack"

    # ── FA-50/b: the `and <Marshal>` arm, unpinned by the battle assertion ─
    def test_the_and_marshal_shape_declares_its_tail(self, shipped):
        """The first clause executes whether or not the split fires, so the
        battle assertion could not see this arm. The WARNING can."""
        message = run(shipped,
                      "Ney, attack Mack and Davout scout Swabia").get("message")
        assert "One order at a time" in (message or ""), message
        assert "scout Swabia" in (message or "")

    # ── FA-50/e: masked by the idiom exemption ───────────────────────────
    def test_a_bare_second_verb_is_not_a_second_order(self, shipped):
        """The idiom guard caught every earlier case first. `attack ... and
        hold` is NOT one of the three idioms, and is still one order —
        clause 2 names no object of its own."""
        message = run(shipped, "Ney, attack Mack and hold").get("message")
        assert "One order at a time" not in (message or ""), message

    # ── FA-50/f: masked by the caller's own fast_parse gate ──────────────
    def test_an_unparseable_first_clause_never_splits(self, shipped):
        """The call site re-checks clause 1, so removing the check inside
        the helper changed nothing observable. Asserted at the helper."""
        _client, world = shipped
        assert M.parser._and_clause_is_a_second_order(
            "asdfqwer and hold Rhineland", {"world": world}) is None
        # …and the control at the same seam.
        assert M.parser._and_clause_is_a_second_order(
            "Ney, attack Mack and hold Rhineland",
            {"world": world}) is not None

    # ── FA-54/e: masked by the verbatim-substring arm ────────────────────
    def test_a_multiword_province_is_grounded_by_its_tokens(self):
        """`name.lower() in raw` already answers for a single-word province,
        so emptying the token set changed nothing. A hyphenated province
        typed with spaces reaches ONLY the token arm."""
        from backend.commands.movement_executor import (
            destination_grounding_note,
        )

        assert destination_grounding_note(
            "Ney, move to ile de france", "Ile-de-France") == ""
        assert destination_grounding_note(
            "Ney, move to Franche Comte", "Franche-Comte") == ""
        # …and the control: a genuinely different province still discloses.
        assert destination_grounding_note(
            "Ney, move to Mainz", "Ile-de-France") != ""


    # ── The strategic layer reads the raw utterance too ───────────────────
    def test_a_deferred_clause_never_reaches_the_strategic_layer(self, shipped):
        """Found by probing this slice's OWN fix for the regression class the
        preceding slice shipped. `Ney, attack Mack, and hold Rhineland later`
        created a 2 AP STANDING HOLD on the phantom province "Rhineland
        Later" while the action chain had correctly read `attack` — because
        `detect_strategic_command` runs on text the guard never touched.

        Measured BYTE-IDENTICAL at the pre-slice commit 62779e05, so it is a
        residue this slice should have closed, not a regression it caused.
        PARSE-NEG had already had to re-apply its own guard at this exact
        line, for this exact reason."""
        reply = run(shipped, "Ney, attack Mack, and hold Rhineland later")
        assert reply.get("battle_report"), reply.get("message")
        assert "Rhineland Later" not in (reply.get("message") or "")
        order = M.world.get_marshal("Ney").strategic_order
        assert order is None or getattr(order, "target", None) != "Rhineland Later"

    def test_the_engines_own_until_condition_survives_the_strategic_guard(
            self, shipped):
        """`strip_deferred_clauses` never touches `until`, which is why it is
        safe at a seam where `strip_condition_clauses` is not — blanking a
        condition clause here would destroy the one thing StrategicCondition
        exists to parse."""
        reply = run(shipped, "Ney, hold until Davout arrives then attack")
        assert reply.get("success") is True
        assert "will hold" in (reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════
# ROUND 2 — what the adversarial review of the FIXES found
#
# A nine-lens fleet was run against the SHIPPED slice rather than against
# the findings, on the standing rule that a fix must be attacked as hard as
# a defect. It found a P1 THIS SLICE HAD ITSELF INTRODUCED, of the exact
# class the preceding slice shipped, plus three companions. All four are
# reproduced here, and every one was separated from the pre-slice commit
# 62779e05 by measurement before it was called a regression.
# ═══════════════════════════════════════════════════════════════════════

class TestTheDeferralGuardDoesNotReAddressTheSurvivingOrder:
    """⛔ THE P1 THIS SLICE SHIPPED.

        "Ney, hold your position for now, Davout attack Mack"
            -> "Ney,                           , Davout attack Mack"

    `has_executable_residue` sees `attack`, so no refusal fires — and the
    leading address token is still `Ney,`, so the surviving verb, which
    names its OWN marshal, was re-addressed to HIM. Measured on the shipped
    1805 boot: NEY marched into Swabia and lost 1,164 men on a sentence that
    ordered him to STAND STILL. One command, no confirm modal, irreversible.

    That is FA-7's own headline defect — an order the player postponed being
    fought on the turn they typed it — re-created by FA-7's own fix, and the
    same shape as the P1 the preceding slice shipped: blanked text handed to
    a consumer that reads what is left as the player's intent.

    Reachable with `later`, `tomorrow` and `delay` too, so it was never an
    artefact of one adverb. Blanking the address is NOT enough:
    `CommandParser.parse` runs its own word scan over the raw utterance and
    re-binds the addressee anyway — measured, the two-producers-in-series
    pattern this slice met three times. The answer is FA-50's own rule: one
    order at a time.
    """

    TWO_MARSHALS = [
        "Ney, hold your position for now, Davout attack Mack",
        "Ney, hold your position later, Davout attack Mack",
        "Ney, hold your position tomorrow, Davout attack Mack",
        "Ney, delay the attack, Davout attack Mack",
        "Ney, hold the line for now and Davout, attack Mack",
    ]

    @pytest.mark.parametrize("command", TWO_MARSHALS)
    def test_the_addressee_never_fights_the_other_marshals_battle(
            self, shipped, command):
        _client, world = shipped
        before = {n: (m.location, m.strength)
                  for n, m in world.marshals.items()
                  if m.nation == world.player_nation}
        reply = run(shipped, command)
        after = {n: (m.location, m.strength)
                 for n, m in M.world.marshals.items()
                 if m.nation == M.world.player_nation}
        assert not reply.get("battle_report"), reply.get("message")
        assert after == before, command

    def test_a_residue_naming_no_other_marshal_is_still_the_addressees(
            self, shipped):
        """The discriminator, and why this is a refusal rather than a blanket
        one. `Ney, delay the attack and move to Swabia` names nobody else, so
        the surviving order is still Ney's and it stands — he MOVES, which is
        what he was told to do. (It is then refused by the enemy standing in
        Swabia, which is a different and correct answer; at the pre-slice
        commit this ATTACKED and lost 2,746 men.)"""
        _client, world = shipped
        parsed = M.parser.parse("Ney, delay the attack and move to Swabia",
                                {"world": world}, world)
        assert parsed.get("refusal") is None, parsed
        assert (parsed.get("command") or {}).get("action") == "move"
        assert (parsed.get("command") or {}).get("target") == "Swabia"

    @pytest.mark.parametrize("command", [
        "Ney, delay the attack and support Davout",
        "Ney, postpone the attack and reinforce Davout",
    ])
    def test_another_marshal_as_the_OBJECT_is_not_a_second_order(
            self, shipped, command):
        """The isolation pin the sweep asked for, and it found a false
        refusal in the first cut of this very rule: testing for another
        marshal ANYWHERE in the residue refuses `Ney, delay the attack and
        support Davout`, where Davout is the OBJECT of Ney's own order.

        A SECOND ORDER NAMES ITS MARSHAL FIRST. Subject position is the
        discriminator, and it is the only one that separates these two."""
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert "no drawer for tomorrow" not in (reply.get("message") or "")

    def test_the_predicate_is_pure_and_states_its_own_rule(self):
        from backend.ai.clause_guards import (
            address_governs_only_deferred_text,
        )

        original = "Ney, hold your position later, Davout attack Mack"
        guarded, applied = strip_deferred_clauses(original)
        assert applied is True
        assert address_governs_only_deferred_text(original, guarded, 4) is True
        # A deferral that leaves the addressee's OWN clause standing is not
        # this case.
        other = "Ney, hold here and attack next turn"
        assert address_governs_only_deferred_text(
            other, strip_deferred_clauses(other)[0], 4) is False


class TestForNowIsNotADeferral:
    """`for now` means AT PRESENT — do it, provisionally, this turn. FA-7's
    own fix_shape lists it as a deferral adverb, and it is the opposite.

    Measured with it in the list: these were refused and answered with copy
    insisting Berthier keeps "no drawer for tomorrow's orders" — telling the
    player their order was about tomorrow when it was about today."""

    @pytest.mark.parametrize("command", [
        "Ney, hold your position for now",
        "Ney, fortify for now",
        "Soult, defend Alsace for now",
        "Murat, scout Swabia for now",
        "Ney, attack Mack for now",
    ])
    def test_it_is_an_order_for_this_turn(self, shipped, command):
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert "no drawer for tomorrow" not in (reply.get("message") or "")

    def test_the_guard_does_not_claim_it(self):
        for command in ("Ney, hold your position for now",
                        "Ney, attack Mack for now"):
            assert strip_deferred_clauses(command)[1] is False, command


class TestHoldOffTakesItsPreposition:
    """`hold off ON <doing something>` postpones it. Bare `hold off <foe>`
    is the OPPOSITE — an order to repel him, now — and `hold back from
    <place>` orders him to stay clear of it THIS turn."""

    @pytest.mark.parametrize("command", [
        "Davout, hold off the Austrians",
        "Davout, hold off Mack",
        "Ney, hold back from Swabia",
    ])
    def test_a_bare_hold_off_is_an_order_for_this_turn(self, shipped, command):
        reply = run(shipped, command)
        assert reply.get("success") is True, reply.get("message")
        assert "no drawer for tomorrow" not in (reply.get("message") or "")

    def test_the_on_form_is_still_a_deferral(self, shipped):
        message = run(shipped, "Ney, hold off on attacking Mack").get("message")
        assert "no drawer for tomorrow" in (message or ""), message


class TestBothArmsScopeTheSameWay:
    """The verb arm used the NEGATION clause boundary, which excludes `and`
    on purpose, while the adverb arm has scoped on `and` since it was
    written — two arms of one function disagreeing about their own
    documented rule. Measured: `Ney, delay the attack and move to Swabia`
    blanked the MOVE as well."""

    def test_the_verb_arm_stops_at_a_coordinate_clause(self):
        effective, applied = strip_deferred_clauses(
            "Ney, delay the attack and move to Swabia")
        assert applied is True
        assert "move to Swabia" in effective
        assert "delay" not in effective

    def test_the_adverb_arm_still_does_too(self):
        effective, _applied = strip_deferred_clauses(
            "Ney, hold here and attack next turn")
        assert "hold here" in effective
        assert "attack" not in effective
