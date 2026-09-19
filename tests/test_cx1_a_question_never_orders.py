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


# ═══════════════════════════════════════════════════════════════════════════
# THE SWEEP'S OWN FINDINGS — every arm pinned DIRECTLY on the predicate
# ═══════════════════════════════════════════════════════════════════════════
# The first mutation sweep returned ten INERT rows, and an INERT mutation is
# a question. Four of these arms were inert because the SECOND guard this
# slice added — `AN_ADDRESS_NEEDS_NO_COMMA` in the executor — catches the
# same sentence one layer down, so deleting the clause-guard arm changed
# nothing observable end to end. That is defence in depth working, and it is
# also a pin that proves nothing.
#
# The project's own rule applies: darken the second road in the isolation
# pin, never weaken the assertion. These pin `is_question` DIRECTLY, which no
# executor guard can reach.

class TestEachArmOfTheGuardDirectly:
    """One pin per arm, on the predicate itself."""

    ROSTER = ["Ney", "Davout", "Soult", "Mack", "Swabia", "Vienna"]

    # ⚠ The arms OVERLAP, and the first draft of these pins did not allow for
    # it: `whose corps is at Swabia` carries an auxiliary, so the pre-CX rule
    # already called it a question, and `is Swabia defended` names a subject
    # in the roster, so arm (d) already did. Darkening one arm and asserting
    # False on a sentence another arm covers is an assertion about the wrong
    # thing. Each list below is therefore split: what the arm must ANSWER,
    # and the narrower set that ONLY it reaches.

    ARM_A = ["why not attack Mack", "why not retreat", "who holds Swabia",
             "whose corps is at Swabia", "whom shall we attack",
             "why did Ney fall back"]
    # No auxiliary anywhere, and a WH lead — so the subject arm is skipped by
    # construction and the old auxiliary rule finds nothing.
    ARM_A_ONLY = ["why not attack Mack", "why not retreat", "who holds Swabia"]

    ARM_C = ["is Swabia defended", "are the Austrians at Swabia",
             "was the battle won", "does Ney hold Swabia", "did Ney attack",
             "has Vienna fallen", "had Ney attacked"]
    # A copular or perfect lead whose SUBJECT is not in any roster, so arm (d)
    # cannot reach it either.
    ARM_C_ONLY = ["is the bridge held", "was the assault repulsed",
                  "has the depot been built", "are the roads open",
                  "did the levy arrive"]

    @pytest.mark.parametrize("text", ARM_A)
    def test_arm_a_answers_the_four_subject_wh_leads(self, text):
        assert CG.is_question(text, self.ROSTER) is True, text

    @pytest.mark.parametrize("text", ARM_A_ONLY)
    def test_arm_a_is_the_only_thing_holding_these(self, text):
        saved = CG._SUBJECT_WH_WORDS
        try:
            CG._SUBJECT_WH_WORDS = frozenset()
            assert CG.is_question(text, self.ROSTER) is False, text
        finally:
            CG._SUBJECT_WH_WORDS = saved

    @pytest.mark.parametrize("text", ARM_C)
    def test_arm_c_answers_the_leads_with_no_imperative_form(self, text):
        assert CG.is_question(text, self.ROSTER) is True, text

    @pytest.mark.parametrize("text", ARM_C_ONLY)
    def test_arm_c_is_the_only_thing_holding_these(self, text):
        assert CG.is_question(text, self.ROSTER) is True, text
        saved = CG._NEVER_IMPERATIVE_LEADS
        try:
            CG._NEVER_IMPERATIVE_LEADS = frozenset()
            assert CG.is_question(text, self.ROSTER) is False, text
        finally:
            CG._NEVER_IMPERATIVE_LEADS = saved

    def test_arm_c_stands_down_before_a_trailing_clause(self):
        """An inverted conditional is not a question. `_TRAILING_CLAUSE_RE`
        is what keeps "should Mack advance, fortify" — and its copular twin —
        out of the arm and on the condition guard's refusal."""
        assert CG.is_question("is Mack advancing, fortify", self.ROSTER) is False
        assert CG.is_question("is Mack advancing", self.ROSTER) is True
        assert CG.is_question("should Mack advance, fortify", self.ROSTER) is False
        assert CG.is_question("should Mack advance", self.ROSTER) is True

    def test_have_is_deliberately_not_a_lead(self):
        """"have Ney attack Mack" is the CAUSATIVE IMPERATIVE and a real
        order; "has"/"had" cannot open one. If `have` is ever added to the
        lead set this pin goes red, which is the point."""
        assert CG.is_question("have Ney attack Mack", self.ROSTER) is False
        assert CG.is_question("has Ney attacked Mack", self.ROSTER) is True
        assert CG.is_question("had Ney attacked Mack", self.ROSTER) is True

    def test_the_causative_imperative_still_marches(self):
        """…and end to end, so the predicate pin above is not the only
        evidence."""
        _, footprint = _drive("have Ney attack Mack")
        assert footprint["ap"][1] < footprint["ap"][0], footprint

    def test_arm_b_the_deliberative_openers(self):
        for text in ("what about attack Mack", "how about retreat",
                     "is it time to attack", "what say you to a march"):
            assert CG.is_question(text, self.ROSTER) is True, text

    def test_arm_e_the_unaddressed_question_mark(self):
        assert CG.is_question("retreat?") is True
        assert CG.is_question("Ney, attack Mack?") is False
        assert CG.is_question("Marshal Ney, retreat?") is False

    def test_arm_d_the_subject(self):
        assert CG.is_question("can Ney attack Mack", self.ROSTER) is True
        assert CG.is_question("can you attack Mack", self.ROSTER) is False
        assert CG.is_question("can Ney attack Mack") is False   # no roster


# ═══════════════════════════════════════════════════════════════════════════
# CX-5 — "THE RETREAT IS SOMETIMES A NOUN"
# ═══════════════════════════════════════════════════════════════════════════
# `_mentions_screening_idiom` (July 18, 2026) understood this failure mode
# exactly and closed it with an ALLOWLIST OF FOUR VERBS. Measured on the 1805
# boot through POST /command, SEVEN more phrasings are the same defect one
# word over, and every one marched the player's OWN marshal away — free, at
# 0 AP, with the retreat's −45% effectiveness penalty, at confidence 0.90,
# which is ABOVE the escalation gate, so no key in any mode could ever have
# corrected it.
#
# The allowlist is INVERTED: "retreat" after a determiner is a NOUN, and only
# a small set of verbs ("sound the retreat", "order the retreat") means carry
# one out. The measurement supports the asymmetry — all four of those
# correctly retreated on the same board before the fix and still do.

class TestTheRetreatIsSometimesANoun:

    SOMEBODY_ELSES = [
        "Lannes, cut down the retreat",
        "Lannes, cut off the retreat",
        "Lannes, press the retreat",
        "Lannes, block the retreat",
        "Lannes, exploit the retreat",
        "Lannes, punish the retreat",
        "Lannes, ride down the retreating Austrians",
        "Lannes, harry the retreat",
        "Lannes, cover the retreat",
        "Lannes, screen the withdrawal",
    ]
    HIS_OWN = [
        "Lannes, retreat",
        "Lannes, fall back",
        "Lannes, pull back",
        "Lannes, retire",
        "Lannes, sound the retreat",
        "Lannes, order the retreat",
        "Lannes, begin the retreat",
        "Lannes, call the retreat",
    ]

    @pytest.mark.parametrize("utterance", SOMEBODY_ELSES)
    def test_he_does_not_march_away(self, utterance):
        response, footprint = _drive(utterance)
        _assert_inert(utterance, response, footprint)

    @pytest.mark.parametrize("utterance", HIS_OWN)
    def test_a_real_retreat_still_retreats(self, utterance):
        """⚠ Asserted on the BEHAVIOUR, not on the geography. The first draft
        asserted the marshal MOVED, and the mutation sweep caught it going red
        on a tree where the retreat resolver kept him where he was — which a
        retreat may legitimately do when there is nowhere better to stand.
        A pin about "did he retreat" must not depend on which province he
        lands in."""
        response, footprint = _drive(utterance)
        message = (response.get("message") or response.get("error") or "")
        assert "retreat" in message.lower(), (utterance, message[:160])
        assert "cannot parse" not in message, (utterance, message[:160])
        assert "order of battle" not in message, (utterance, message[:160])

    def test_the_pursuit_of_a_retreating_enemy_is_untouched(self):
        """`pursue` wins the chain long before the retreat branch, and the
        participle rule must not reach it: this is a real order that fights."""
        _, footprint = _drive("Lannes, pursue the retreating enemy")
        assert footprint["ap"][1] < footprint["ap"][0], footprint

    def test_the_lever(self):
        from backend.ai import llm_client as LC
        assert LC.A_RETREAT_CAN_BE_A_NOUN is True
        original = LC.A_RETREAT_CAN_BE_A_NOUN
        try:
            LC.A_RETREAT_CAN_BE_A_NOUN = False
            response, _footprint = _drive("Lannes, cut down the retreat")
            message = (response.get("message") or "")
            assert "retreats from" in message, (
                "lever off = the defect reproduces", message[:160])
        finally:
            LC.A_RETREAT_CAN_BE_A_NOUN = original

    def test_the_four_screening_verbs_are_still_covered_by_their_own_guard(self):
        """`_mentions_screening_idiom` is KEPT, not replaced: FA-73 pins its
        exact wording, and `cover the rear / army / corps / flank` is its own
        idiom that the noun rule does not reach."""
        from backend.ai.llm_client import _mentions_screening_idiom
        for text in ("cover the retreat", "screen the withdrawal",
                     "protect the rear", "shield the army"):
            assert _mentions_screening_idiom(text), text

    def test_the_noun_rule_and_the_carry_out_set(self):
        from backend.ai.llm_client import _retreat_is_a_noun
        for text in ("cut down the retreat", "press the retreat",
                     "ride down the retreating austrians",
                     "block the enemy retreat", "exploit their withdrawal"):
            assert _retreat_is_a_noun(text) is True, text
        for text in ("retreat", "retreat to lorraine", "sound the retreat",
                     "order a general retreat", "begin the retreat",
                     "retreat the army"):
            assert _retreat_is_a_noun(text) is False, text


class TestTheObjectPronounIsNotASubject:
    """⛔ A REGRESSION THIS ROW SHIPPED AND THEN CAUGHT, pinned so it cannot
    come back. The subject arm's first draft put the OBJECT pronouns in its
    third-person set, and `it` follows an imperative as its object far more
    often than it follows a modal as its subject:

        "do it"        → a QUESTION
        "Ney, do it"   → a QUESTION

    A plain affirmative and a plain order. **The whole 23,618-test suite was
    green about both**, because nothing pinned either — which is why the
    probe that found it was a hand-written adversarial pass over the fix
    rather than a test run.
    """

    ROSTER = ["Ney", "Davout", "Mack", "Swabia"]

    @pytest.mark.parametrize("utterance", [
        "do it", "do it now", "Ney, do it", "do them", "do that", "do this",
        "have it done", "do so",
    ])
    def test_an_imperative_with_an_object_pronoun_is_an_order(self, utterance):
        assert CG.is_question(utterance, self.ROSTER) is False, utterance

    @pytest.mark.parametrize("utterance", [
        "is it done", "does it matter", "did it work", "has it fallen",
    ])
    def test_and_the_copular_leads_still_ask_about_it(self, utterance):
        """Unaffected: `is` / `does` / `did` / `has` have no imperative form
        at all, so arm (c) answers them whatever follows."""
        assert CG.is_question(utterance, self.ROSTER) is True, utterance

    @pytest.mark.parametrize("utterance", [
        "is he attacking", "do they hold", "did she arrive",
    ])
    def test_the_true_subject_pronouns_still_ask(self, utterance):
        assert CG.is_question(utterance, self.ROSTER) is True, utterance

    def test_do_it_reaches_the_executor_as_an_order(self):
        """End to end: it must not be answered as a question."""
        response, _footprint = _drive("Ney, do it")
        message = (response.get("message") or response.get("error") or "")
        assert "cannot answer that" not in message, message
        assert "COMMAND REFERENCE" not in message, message[:200]
