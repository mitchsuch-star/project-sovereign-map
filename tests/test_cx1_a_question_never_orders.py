"""CX slice 1 — "A QUESTION NEVER ORDERS".

Row CX ("The Hand on the Keyboard"). Owner record:
`docs/COMMAND_ROBUSTNESS_SPEC.md` §10; rules `docs/SYSTEMS_REFERENCE.md` §50.

THE FINDING, measured on the shipped 1805 boot through `POST /command`
=====================================================================
The fast parser chooses an action by keyword. `is_question` was the only thing
standing between a question and the imperative inside it, and it required an
interrogative LEAD plus one more signal — a "?", a first person, or (for a
WH-lead) an auxiliary. Three whole families carried none of those:

    "why not attack Mack"        → a REAL BATTLE. AP 4→3; Ney −946, Davout
                                   −1,025, Soult −1,980, Lannes −709, Murat
                                   −867 and the Emperor's Guard −394.
    "why not retreat"            → a GENERAL RETREAT: all eight corps fell
                                   back, Massena losing 2,100 men to movement
                                   attrition.
    "what about attack Mack"     → a battle.
    "how about retreat"          → the army retreated.
    "is it time to build a depot in Paris" → 300 gold and an admin AP spent.
    "can Ney attack Mack"        → a battle (and `may` / `does` / `is …
                                   attacking` with it).
    "retreat?"                   → the whole army marched.
    "who holds Swabia"           → "Which marshal shall hold Swabia, Sire?" —
                                   the question desk's OWN advertised kind,
                                   shadowed by the HOLD verb and ONE answer
                                   from an order.

FOUR ARMS, one lever (`clause_guards.A_QUESTION_NEVER_ORDERS`)
==============================================================
  (a) `who` / `whom` / `whose` / `why` lead a question on their own — no
      English imperative opens with them. Deliberately four words and not
      "every WH-lead": the corpus itself pins "when ready then retreat" as a
      RETREAT.
  (b) the deliberative openers — "what about …", "how about …", "is it time
      to …" — the way a person MUSES at a war table.
  (c) THE SUBJECT DECIDES, the rule FA slice 7's review round already wrote
      for will/would/shall, extended to the other modal leads and given the
      live roster: "can NEY attack Mack" asks about a third party; "can YOU
      attack Mack" is still a polite order. It stands down before a trailing
      clause, because "should Mack advance, fortify" is an inverted
      CONDITIONAL and belongs to the condition guard's refusal.
  (d) an UNADDRESSED line ending in "?" is a question. An addressed one keeps
      its order: "Ney, attack Mack?" is a hesitant order and has been
      documented as one since FA slice 7.

WHAT IS DELIBERATELY LEFT EXECUTING — stated, not overlooked
============================================================
  * `end turn?` — `is_bare_end_turn` strips a trailing "?" ON PURPOSE (FA-R4).
    The behaviour it replaced (a question mark saving you from an accidental
    turn advance, and its absence not) was itself the defect that rule exists
    to kill. Untouched here, and pinned below so a later slice cannot "fix" it
    by accident.
  * `Ney, attack Mack?` — an addressed order, per (d).
  * `can you attack Mack`, `would you have Ney attack Mack`, `do attack Mack`
    — second-person and emphatic imperatives.
  * `when ready then retreat` — a corpus pin.

MEASURED REACH
==============
A 677-case sweep of (question lead × order verb) on a fresh 1805 board per
case: **668 clean, 9 executing, and all nine are the controls above.** Before
the slice the same sweep executed 30. The golden corpus moves **0 of 447
entries** under either arm of the lever (`TestTheCorpusDoesNotMove`).
"""

import io
import contextlib

import pytest

from backend.ai import clause_guards as CG


# ═══════════════════════════════════════════════════════════════════════════
# Harness — a fresh 1805 board per utterance, driven at POST /command
# ═══════════════════════════════════════════════════════════════════════════

@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _fresh_board():
    """A fresh shipped-1805 world installed into `backend.main`.

    The world/game_state/parser triple is the project's known TestClient trap:
    swap fewer than all three and the request silently hits another world.
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
        client = TestClient(main_module.app)
    return world, client


def _drive(utterance):
    """Returns (response, footprint) — the footprint is everything an order
    can move. A question must move none of it."""
    world, client = _fresh_board()
    before = {
        "ap": world.actions_remaining,
        "admin": getattr(world, "admin_actions_remaining", None),
        "gold": world.gold,
        "turn": world.current_turn,
        "marshals": {m.name: (m.location, m.strength)
                     for m in world.get_player_marshals()},
    }
    with _quiet():
        response = client.post("/command", json={"command": utterance}).json()
    after = {
        "ap": world.actions_remaining,
        "admin": getattr(world, "admin_actions_remaining", None),
        "gold": world.gold,
        "turn": world.current_turn,
        "marshals": {m.name: (m.location, m.strength)
                     for m in world.get_player_marshals()},
    }
    moved = sorted(k for k, v in before["marshals"].items()
                   if after["marshals"].get(k) != v)
    footprint = {
        "ap": (before["ap"], after["ap"]),
        "admin": (before["admin"], after["admin"]),
        "gold": (before["gold"], after["gold"]),
        "turn": (before["turn"], after["turn"]),
        "moved": moved,
        "battle": bool(response.get("battle_report")),
    }
    return response, footprint


def _assert_inert(utterance, response, footprint):
    """Nothing an order can move has moved."""
    assert footprint["ap"][0] == footprint["ap"][1], (utterance, footprint)
    assert footprint["admin"][0] == footprint["admin"][1], (utterance, footprint)
    assert footprint["gold"][0] == footprint["gold"][1], (utterance, footprint)
    assert footprint["turn"][0] == footprint["turn"][1], (utterance, footprint)
    assert footprint["moved"] == [], (utterance, footprint)
    assert not footprint["battle"], (utterance, footprint)


# ═══════════════════════════════════════════════════════════════════════════
# The three families that EXECUTED, driven end to end
# ═══════════════════════════════════════════════════════════════════════════

class TestTheQuestionsThatFought:
    """Each of these moved the board before this slice. The AP, the gold, the
    turn and every marshal's position and strength are asserted unchanged —
    not merely `success is False`, which a refusal AFTER a mutation satisfies.
    """

    @pytest.mark.parametrize("utterance", [
        # (a) the four leads no imperative can open
        "why not attack Mack",
        "why not attack",
        "why not retreat",
        "why not move to Swabia",
        "why not fortify",
        "why don't we attack Mack",
        "who holds Swabia",
        "who holds Vienna",
        "whose corps is at Swabia",
        # (b) the deliberative openers
        "what about attack Mack",
        "what about retreat",
        "what about scout Swabia",
        "what about build a depot in Paris",
        "how about attack Mack",
        "how about retreat",
        "is it time to attack Mack",
        "is it time to retreat",
        "is it time to build a depot in Paris",
        # (c) the subject decides — a modal lead naming a third party
        "can Ney attack Mack",
        "may Ney attack Mack",
        "does Ney attack Mack",
        "is Ney attacking Mack",
        "could Davout attack Mack",
        "should Soult attack Mack",
        "has Ney taken Vienna",
        # (d) an unaddressed line that ends in a question mark
        "retreat?",
        "attack?",
        "fortify?",
        "charge?",
    ])
    def test_the_board_does_not_move(self, utterance):
        response, footprint = _drive(utterance)
        _assert_inert(utterance, response, footprint)

    def test_why_not_attack_mack_fought_a_battle_before_this_slice(self):
        """The headline, stated as its own pin so the reach is not lost in a
        parametrize list: the sentence that spent an action point and bled six
        French corps now moves nothing at all."""
        response, footprint = _drive("why not attack Mack")
        assert footprint["ap"] == (4, 4), footprint
        assert not footprint["battle"], footprint
        assert footprint["moved"] == [], footprint

    def test_why_not_retreat_no_longer_marches_the_whole_army(self):
        """Eight corps fell back on this sentence, free and irreversible."""
        _, footprint = _drive("why not retreat")
        assert footprint["moved"] == [], footprint


# ═══════════════════════════════════════════════════════════════════════════
# The controls — what must STILL be an order
# ═══════════════════════════════════════════════════════════════════════════

class TestTheOrdersThatMustStillMarch:

    @pytest.mark.parametrize("utterance,why", [
        ("Ney, attack Mack", "the plain order"),
        ("Ney, attack Mack?", "an ADDRESSED order keeps its question mark "
                              "(documented since FA slice 7)"),
        ("can you attack Mack", "second person — the polite imperative"),
        ("would you have Ney attack Mack", "FA slice 7's own second-person rule"),
        ("do attack Mack", "the emphatic imperative"),
    ])
    def test_the_order_still_executes(self, utterance, why):
        _, footprint = _drive(utterance)
        assert footprint["ap"][1] < footprint["ap"][0], (utterance, why, footprint)

    @pytest.mark.parametrize("utterance", [
        "end turn", "end turn?", "Berthier, end turn",
    ])
    def test_end_turn_keeps_its_question_mark_by_design(self, utterance):
        """FA-R4 strips a trailing "?" from the end-turn vocabulary ON PURPOSE.

        The behaviour it replaced — a question mark saving you from an
        accidental turn advance while the same sentence without one did not —
        was itself the defect that rule was written to kill. This slice does
        not touch it, and the pin exists so a later slice cannot quietly
        "fix" it into an inconsistency.
        """
        _, footprint = _drive(utterance)
        assert footprint["turn"][1] == footprint["turn"][0] + 1, footprint

    def test_an_inverted_conditional_is_refused_not_answered(self):
        """"Ney, should Mack advance, fortify" means "if Mack advances" — a
        CONDITIONAL, which the condition guard refuses. The subject arm stands
        down before a trailing clause so this reaches its own refusal rather
        than becoming a question."""
        from backend.commands.parser import CommandParser
        from backend.ai.parser_eval import build_world, build_llm_game_state
        with _quiet():
            world = build_world("1805")
            state = build_llm_game_state(world)
            parser = CommandParser(use_real_llm=False)
            result = parser.parse("Ney, should Mack advance, fortify",
                                  state, world=world)
        assert not result.get("success")
        assert result.get("refusal") == "conditional", result.get("refusal")


# ═══════════════════════════════════════════════════════════════════════════
# The desk answers what it shadowed
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDeskIsReachedNotShadowed:

    def test_who_holds_swabia_is_answered_not_turned_into_a_hold_order(self):
        """The desk's own `who_holds` kind, which the HOLD verb ate whenever
        the player left the question mark off."""
        response, footprint = _drive("who holds Swabia")
        _assert_inert("who holds Swabia", response, footprint)
        message = response.get("message") or ""
        assert "held by" in message, message
        assert "Which marshal" not in message, message

    def test_wheres_ney_is_answered_like_where_is_ney(self):
        """The auxiliary contracted onto the lead ("where's") could never be
        seen by an auxiliary scan, so the contraction fell to Berthier's
        shrug while the long form answered."""
        long_form, _ = _drive("where is Ney")
        short_form, footprint = _drive("where's Ney")
        _assert_inert("where's Ney", short_form, footprint)
        assert (short_form.get("message") or "") == (long_form.get("message") or "")
        assert "Rhineland" in (short_form.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# The lever, and the guarantee that the corpus does not move under it
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLever:

    def test_the_lever_exists_and_is_on(self):
        assert CG.A_QUESTION_NEVER_ORDERS is True

    def test_the_false_arm_reproduces_the_defect(self):
        """The house rule: a lever's False arm reproduces today's behaviour.

        Here "today" is the DEFECT, so the arm is asserted by making the
        predicate read the way it read before the slice.
        """
        original = CG.A_QUESTION_NEVER_ORDERS
        try:
            CG.A_QUESTION_NEVER_ORDERS = False
            assert CG.is_question("why not attack Mack") is False
            assert CG.is_question("what about attack Mack") is False
            assert CG.is_question("retreat?") is False
            assert CG.is_question("can Ney attack Mack", ["Ney"]) is False
            CG.A_QUESTION_NEVER_ORDERS = True
            assert CG.is_question("why not attack Mack") is True
            assert CG.is_question("what about attack Mack") is True
            assert CG.is_question("retreat?") is True
            assert CG.is_question("can Ney attack Mack", ["Ney"]) is True
        finally:
            CG.A_QUESTION_NEVER_ORDERS = original

    def test_the_roster_arm_is_dormant_without_a_roster(self):
        """`subjects` omitted — every caller outside the parse chain — leaves
        the function byte-identical to before the slice."""
        assert CG.is_question("can Ney attack Mack") is False
        assert CG.is_question("can Ney attack Mack", ["Ney"]) is True

    def test_the_roster_names_every_commander_and_leaks_no_fog(self):
        """⚠ CORRECTED BY MEASUREMENT. The first draft of this pin asserted
        the subject roster was fog-FILTERED and it is not: `_askable_enemy_names`
        is deliberately omniscient about NAMES, and its own docstring says why
        — naming a commander was never the fogged half, his POSITION is, and
        the desk answers that honestly ("no word of Kutuzov's whereabouts").

        That is the right list here and the wider direction is the safer one:
        "can Kutuzov take Vienna" should read as a question whether or not we
        can see him. No fog is leaked, because the roster only decides whether
        a sentence is a QUESTION and a boolean prints nothing.
        """
        from backend.ai.llm_client import _question_subjects
        from backend.ai.parser_eval import build_world, build_llm_game_state
        with _quiet():
            world = build_world("1805")
            state = build_llm_game_state(world)
        names = {str(n).lower() for n in _question_subjects(state)}
        assert "ney" in names and "mack" in names
        # Kutuzov stands at `unknown` visibility on the boot board and is
        # STILL a subject — by design, per the docstring above.
        assert "kutuzov" in names, sorted(names)

    def test_a_question_about_an_unseen_commander_still_answers_honestly(self):
        """The fog guarantee that matters: the wider roster must not turn
        into a wider ANSWER. Kutuzov is a subject, and the reply still refuses
        to say where he is."""
        response, footprint = _drive("where is Kutuzov")
        _assert_inert("where is Kutuzov", response, footprint)
        message = response.get("message") or ""
        assert "no word" in message.lower(), message
        assert "Podolia" not in message, message


class TestTheCorpusDoesNotMove:
    """447 golden-corpus entries over both worlds, under BOTH arms of the
    lever. The slice claims it moves zero rows; this measures it rather than
    asserting it."""

    def test_zero_rows_move_under_either_arm(self):
        from backend.ai.parser_eval import (
            load_corpus, build_world, build_llm_game_state, worlds_for_entry,
            evaluate_entry)
        from backend.commands.parser import CommandParser

        entries = [e for e in load_corpus()["entries"] if not e.get("live_only")]
        results = {}
        original = CG.A_QUESTION_NEVER_ORDERS
        try:
            for arm in (False, True):
                CG.A_QUESTION_NEVER_ORDERS = arm
                with _quiet():
                    worlds = {k: build_world(k) for k in ("legacy", "1805")}
                    states = {k: build_llm_game_state(w)
                              for k, w in worlds.items()}
                    parser = CommandParser(use_real_llm=False)
                    failures = set()
                    for entry in entries:
                        for world_key in worlds_for_entry(entry):
                            if evaluate_entry(parser, entry, world_key,
                                              worlds[world_key],
                                              states[world_key]):
                                failures.add((entry["id"], world_key))
                results[arm] = failures
        finally:
            CG.A_QUESTION_NEVER_ORDERS = original

        assert results[False] == set(), sorted(results[False])
        assert results[True] == set(), sorted(results[True])


class TestTheSweep:
    """The reach claim, measured: of a (lead x verb) grid plus the named
    controls, the ONLY utterances that move the board are the controls."""

    def test_only_the_controls_execute(self):
        import itertools

        leads = ["why not", "why don't we", "why", "who", "whom",
                 "what about", "how about", "is it time to",
                 "can Ney", "may Ney", "does Ney", "is Ney", "could Davout",
                 "should Soult", "has Ney"]
        verbs = ["attack Mack", "retreat", "move to Swabia", "fortify",
                 "scout Swabia", "build a depot in Paris", "hold Lorraine"]
        controls = {
            "Ney, attack Mack", "Ney, attack Mack?", "can you attack Mack",
            "would you have Ney attack Mack", "do attack Mack",
            "end turn", "end turn?", "Berthier, end turn",
            "when ready then retreat",
        }
        cases = [f"{a} {b}" for a, b in itertools.product(leads, verbs)]
        cases += sorted(controls)

        executed = []
        for utterance in cases:
            _, footprint = _drive(utterance)
            moved = (footprint["ap"][0] != footprint["ap"][1]
                     or footprint["gold"][0] != footprint["gold"][1]
                     or footprint["turn"][0] != footprint["turn"][1]
                     or footprint["moved"] or footprint["battle"]
                     or footprint["admin"][0] != footprint["admin"][1])
            if moved:
                executed.append(utterance)

        assert set(executed) <= controls, sorted(set(executed) - controls)
        # …and the controls really do still work, so the pin cannot pass by
        # the whole command surface having gone inert.
        assert len(executed) >= 8, executed


# ═══════════════════════════════════════════════════════════════════════════
# CX slice 1, second half — "AN ADDRESS NEEDS NO COMMA"
# ═══════════════════════════════════════════════════════════════════════════

class TestAnAddressNeedsNoComma:
    """`_unbound_addressee` keyed the whole rule on `raw.partition(",")`, so a
    name typed WITHOUT a comma was not an address at all and the sentence fell
    through to the marshal-less arm.

    Measured on the 1805 boot, one keystroke apart:

        "Nay, attack Mack"  → refused free, and NAMES the miss.
        "Nay attack Mack"   → SOULT fought a real battle. 1 AP, 265 gold,
                              five corps relocated, no question asked.

    Wider than a typo: a bench candidate, the chief of staff, two foreign
    marshals and pure gibberish all sent Soult in, and `Wellington retreat`
    marched the entire army back.
    """

    UNBINDABLE = [
        ("Nay attack Mack", "a one-letter slip"),
        ("Grouchy attack Mack", "a commission candidate on the bench"),
        ("Berthier attack Mack", "the chief of staff"),
        ("Wellington attack Mack", "a foreign marshal"),
        ("Blucher attack Mack", "another foreign marshal"),
        ("Zorglub attack Mack", "pure gibberish"),
        ("Wellington retreat", "…which marched the WHOLE ARMY"),
    ]

    @pytest.mark.parametrize("utterance,why", UNBINDABLE)
    def test_an_unbindable_name_is_refused_free(self, utterance, why):
        response, footprint = _drive(utterance)
        _assert_inert(utterance, response, footprint)
        message = (response.get("message") or response.get("error") or "")
        assert "order of battle" in message, (why, message)

    @pytest.mark.parametrize("utterance", [
        "Ney attack Mack", "Soult attack Mack", "Ney, attack Mack",
    ])
    def test_a_name_the_roster_binds_still_marches(self, utterance):
        _, footprint = _drive(utterance)
        assert footprint["ap"][1] < footprint["ap"][0], footprint

    def test_a_plausible_typo_is_still_REPAIRED_not_refused(self):
        """⚠ Measured, and it corrects this class's first draft, which listed
        `Davoust attack Mack` as unbindable. It is not: FA-80's typo repair
        binds it to DAVOUT before the guard is ever reached, so
        `command["marshal"]` is set and `_unbound_addressee` returns None by
        its own first branch. The order goes to the man the player meant —
        which is the better outcome and must not regress into a refusal."""
        response, _footprint = _drive("Davoust attack Mack")
        message = (response.get("message") or response.get("error") or "")
        assert "order of battle" not in message, message
        assert "Davout" in message, message

    @pytest.mark.parametrize("utterance", [
        "attack", "attack Mack", "retreat",
    ])
    def test_a_genuinely_bare_order_is_untouched(self, utterance):
        """The leading run before the first order verb is EMPTY here, so the
        new arm cannot reach a bare order by construction."""
        response, footprint = _drive(utterance)
        message = (response.get("message") or response.get("error") or "")
        assert "order of battle" not in message, message

    @pytest.mark.parametrize("utterance", [
        "all marshals attack", "everyone hold", "every corps retreat",
        "the army attack",
    ])
    def test_a_collective_address_is_not_an_unbound_name(self, utterance):
        """"all marshals attack" addresses the army, not a person. It must
        keep reaching the marshal-less arm rather than being refused as an
        unknown marshal called "all marshals"."""
        response, _footprint = _drive(utterance)
        message = (response.get("message") or response.get("error") or "")
        assert "order of battle" not in message, message

    def test_the_lever(self):
        from backend.commands.executor import CommandExecutor
        assert CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA is True
        original = CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA
        try:
            CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = False
            _, footprint = _drive("Nay attack Mack")
            assert footprint["battle"], "lever off = the defect reproduces"
            assert footprint["ap"][1] < footprint["ap"][0]
        finally:
            CommandExecutor.AN_ADDRESS_NEEDS_NO_COMMA = original

    def test_the_comma_form_is_unchanged(self):
        """The arm only ever runs when there is NO comma, so the long-standing
        comma behaviour cannot have moved."""
        response, footprint = _drive("Nay, attack Mack")
        _assert_inert("Nay, attack Mack", response, footprint)
        assert "order of battle" in (response.get("message") or "")
