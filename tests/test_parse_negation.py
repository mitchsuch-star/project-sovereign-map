"""PARSE-NEG — the fast parser is confidently WRONG above the LLM gate.

Row: `docs/BUG_FIXES.md` §PARSE-NEG. Every defect pinned here parsed at
confidence 0.80-0.95, above `LLM_FALLBACK_CONFIDENCE_THRESHOLD = 0.7`, so the
live provider was never consulted and an API key could not have fixed any of
it. The golden corpus never caught it because none of these phrasings were in
it — the corpus rows added alongside this file close that.

The suite is organised as three layers:

  1. `TestClauseGuardUnits` — the pure functions in `backend/ai/clause_guards`.
  2. `TestParserBehaviour` — the production call shape,
     `CommandParser.parse(text, game_state, world=world)`, on the shipped 1805
     board. These are the rows that matter: they assert what a player gets.
  3. `TestGuardsStayNarrow` + `TestRefusalReachesThePlayer` — the counter-
     examples. Every guard here trades safety against reach, and a guard that
     over-fires is a new defect, not a fix; these rows fail if one does.

Assertions are written as "not the old wrong answer" wherever the old answer
is the interesting fact, so a regression that merely changes the wrong action
to a different wrong action still reds.
"""

import pytest
from fastapi.testclient import TestClient

from backend.ai.clause_guards import (
    has_executable_residue,
    is_question,
    mentions_stand_down,
    strip_condition_clauses,
    strip_negated_clauses,
)
from backend.ai.llm_client import LLM_FALLBACK_CONFIDENCE_THRESHOLD
from backend.ai.parser_eval import SCENARIO_1805_PATH, build_llm_game_state
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState


@pytest.fixture(scope="module")
def board():
    world = WorldState.from_scenario(str(SCENARIO_1805_PATH))
    return CommandParser(use_real_llm=False), world, build_llm_game_state(world)


def run(board, text):
    parser, world, game_state = board
    return parser.parse(text, game_state, world=world)


def action_of(board, text):
    result = run(board, text)
    return result["command"]["action"] if result.get("success") else None


# ════════════════════════════════════════════════════════════════════════
# 1. The guards themselves
# ════════════════════════════════════════════════════════════════════════

class TestClauseGuardUnits:

    def test_blanking_preserves_every_character_position(self):
        """The whole design rests on this. Splicing instead of blanking would
        silently move the CR-2 executor-eligibility scan, the 'Marshal <Name>'
        capture and the unresolved-address demotion, all of which index into
        the command text."""
        raw = "Ney, hold your position, do not attack"
        guarded, applied = strip_negated_clauses(raw)
        assert applied
        assert len(guarded) == len(raw)
        assert guarded.index("hold") == raw.index("hold")

    @pytest.mark.parametrize("text", [
        "Ney, never attack Mack",
        "Ney, don't attack",
        "Ney, do not attack",
        "Ney, no attack",
        "Davout, do not retreat",
        "Ney, avoid attacking Mack",
        "Ney, refuse to attack",
    ])
    def test_negation_markers_blank_their_clause(self, text):
        guarded, applied = strip_negated_clauses(text)
        assert applied, f"no negation detected in {text!r}"
        assert "attack" not in guarded.lower()
        assert "retreat" not in guarded.lower()

    def test_no_longer_belongs_to_stand_down_not_negation(self):
        """"Ney, no longer attack" is an unambiguous instruction to cancel a
        standing order, so it is deliberately NOT a negation marker — routing
        it to the refusal would throw away intent the player made plain."""
        assert not strip_negated_clauses("Ney, no longer attack")[1]
        assert mentions_stand_down("ney, no longer attack")

    def test_negation_leaves_the_surviving_order_alone(self):
        guarded, _ = strip_negated_clauses("Ney, hold your position, do not attack")
        assert "hold your position" in guarded
        assert "attack" not in guarded

    def test_bare_no_is_not_a_negation_marker(self):
        """`no quarter` ships in attack_vocabulary as an ATTACK idiom, so a
        bare 'no' can never be a marker."""
        guarded, applied = strip_negated_clauses("Ney, give them no quarter")
        assert not applied
        assert "quarter" in guarded

    def test_until_clause_runs_to_the_end_of_the_utterance(self):
        """Terminating `until` at 'then' would leave 'attack' standing and
        re-open the headline defect."""
        guarded, refuse = strip_condition_clauses(
            "Ney, hold until Davout arrives then attack")
        assert not refuse
        assert "attack" not in guarded.lower()
        assert "hold" in guarded

    def test_real_condition_refuses_but_elliptical_one_does_not(self):
        _, refuse_real = strip_condition_clauses("Ney, when Davout arrives, attack")
        _, refuse_elliptical = strip_condition_clauses("when ready then retreat")
        assert refuse_real
        assert not refuse_elliptical, (
            "the two-word floor is what keeps the corpus pin "
            "cr2-when-ready-then-retreat-not-split green")

    def test_pursue_idiom_is_not_a_temporal_condition(self):
        guarded, refuse = strip_condition_clauses("Ney, go after Blucher")
        assert not refuse
        assert "blucher" in guarded.lower()

    def test_once_more_is_not_a_condition(self):
        guarded, refuse = strip_condition_clauses("Ney, attack once more")
        assert not refuse
        assert "attack" in guarded

    def test_should_inversion_only_with_a_third_party_subject(self):
        assert strip_condition_clauses("Ney, should Mack advance, fortify")[1]
        assert not strip_condition_clauses("Ney, you should attack Mack")[1]
        assert not strip_condition_clauses(
            "Talleyrand, should we declare war on Prussia?")[1]

    def test_stand_down_needs_an_order_noun(self):
        assert mentions_stand_down("ney, stop attacking")
        assert mentions_stand_down("ney, attack no more")
        assert mentions_stand_down("ney, call off the assault")
        assert not mentions_stand_down("talleyrand, stop the war with britain")
        assert not mentions_stand_down("stop davout's pension")

    def test_question_needs_an_interrogative_lead_and_one_more_signal(self):
        assert is_question("how do I attack?")
        assert is_question("how does recruiting work")
        assert is_question("Talleyrand, what about Prussia?")
        # A polite ORDER, not a question — `would` is excluded on purpose.
        assert not is_question("would you have Ney attack Mack")
        # No lead: an order that merely ends in a question mark.
        assert not is_question("Ney, attack Mack?")
        # Lead but no second signal: still an order.
        assert not is_question("can you attack Mack")

    def test_residue_ignores_the_address_and_the_diplomat_names(self):
        assert not has_executable_residue("Talleyrand,        ", "Talleyrand")
        assert has_executable_residue("Ney, hold position", "Ney")


# ════════════════════════════════════════════════════════════════════════
# 2. What the player actually gets
# ════════════════════════════════════════════════════════════════════════

class TestParserBehaviour:

    @pytest.mark.parametrize("text,forbidden", [
        ("Ney, never attack Mack", "attack"),
        ("Ney, don't attack", "attack"),
        ("Ney, do not attack", "attack"),
        ("Ney, no attack", "attack"),
        ("Davout, do not retreat", "retreat"),
        ("Davout, don't fortify", "fortify"),
        ("Ney, never charge the guns", "charge"),
        ("Ney, avoid attacking Mack", "attack"),
        ("Ney, refuse to attack", "attack"),
        ("do not build a depot", "build"),
    ])
    def test_a_forbidden_order_is_never_issued(self, board, text, forbidden):
        result = run(board, text)
        assert not result.get("success")
        assert result.get("refusal") == "negation"
        # And the failure is a REFUSAL, not the generic shrug — the parser
        # understood the sentence exactly.
        assert result.get("refusal_phrase")

    def test_the_order_survives_when_only_the_negation_is_removed(self, board):
        assert action_of(board, "Ney, hold your position, do not attack") == "hold"
        assert action_of(board, "Ney, hold. Do not attack.") == "hold"
        assert action_of(board, "Ney, instead of attacking, fortify") == "fortify"
        assert action_of(board, "Ney, rather than attack, hold") == "hold"
        assert action_of(board, "Ney, without attacking, move to Lorraine") == "move"

    def test_the_negated_clause_leaves_no_residue_in_the_target(self, board):
        """It used to become the destination: 'your position, do not attack'
        and '. Do Not Attack.' were both rendered as provinces."""
        for text in ("Ney, hold your position, do not attack",
                     "Ney, hold. Do not attack."):
            target = run(board, text)["command"].get("target") or ""
            assert "attack" not in target.lower()

    def test_negation_cannot_declare_a_war(self, board):
        """The severest row the evaluation turned up, and it is not in the
        filed table: an irreversible nation-level act, from a negation, at
        confidence 0.95."""
        for text in ("don't declare war on Austria",
                     "Talleyrand, never declare war on Prussia",
                     "do not invade Prussia",
                     "Talleyrand, do not propose peace with Austria"):
            result = run(board, text)
            assert not result.get("success"), text
            assert result.get("refusal") == "negation", text

    def test_standing_an_order_down_cancels_it(self, board):
        for text in ("Ney, stop attacking", "Ney, cease the attack",
                     "Ney, attack no more", "Ney, no longer attack"):
            assert action_of(board, text) == "cancel", text

    @pytest.mark.parametrize("text", [
        "how do I attack?",
        "how do i attack",
        "can I attack Mack?",
        "should I attack?",
        "what does fortify do?",
        "does fortify help?",
        "why can't I move?",
        "is Ney able to attack?",
        "what happens if I retreat?",
        "how does recruiting work",
        "what is a rente?",
        "when should I fortify?",
        "where is Mack?",
    ])
    def test_a_question_is_answered_not_executed(self, board, text):
        result = run(board, text)
        assert result.get("success"), text
        # FA slice 7 (Sept 4, 2026), flipped consciously: a FACT question the
        # intelligence report already answers ("where is Mack?") now routes to
        # `status` carrying the classified question — still a free READ, never
        # an order, no target. Advice and "how do I" keep the command reference.
        assert result["command"]["action"] in ("help", "status"), text
        if result["command"]["action"] == "status":
            assert result["command"].get("question"), text
        assert result["command"].get("target") is None, text

    def test_conditional_orders_are_refused_not_executed_now(self, board):
        for text in ("Ney, if Mack advances fall back to Lorraine",
                     "if Mack advances, Ney should fall back to Lorraine",
                     "Ney, attack if Davout supports",
                     "Ney, when Davout arrives, attack",
                     "Ney, move to Lorraine after Davout arrives",
                     "Ney, attack Mack once Davout arrives",
                     "Ney, should Mack advance, fortify"):
            result = run(board, text)
            assert not result.get("success"), text
            assert result.get("refusal") == "conditional", text

    def test_until_is_scoped_not_refused(self, board):
        """`until` is the one condition StrategicCondition implements. The
        keyword inside its clause must stop outranking the main verb without
        the condition itself being lost."""
        result = run(board, "Ney, hold until Davout arrives then attack")
        assert result["command"]["action"] == "hold"
        assert result["strategic_type"] == "HOLD"
        assert result["strategic_condition"] == {"until_marshal_arrives": "Davout"}

    def test_elliptical_condition_still_issues_the_main_order(self, board):
        assert action_of(board, "Ney, unless attacked, hold position") == "hold"
        # Pinned as ACCEPTED, not ideal: 'if outnumbered' is one word, so this
        # retreats now. Recorded so the trade-off stays visible.
        assert action_of(board, "Ney, retreat if outnumbered") == "retreat"

    def test_go_to_a_province_is_a_march(self, board):
        result = run(board, "Ney, go to Lorraine")
        assert result["command"]["action"] == "move"
        assert result["command"]["target"] == "Lorraine"

    def test_destination_is_the_last_preposition(self, board):
        for text in ("I would like to move to Lorraine",
                     "Ney, I want you to move to Lorraine"):
            assert run(board, text)["command"]["target"] == "Lorraine", text

    @pytest.mark.parametrize("text,ghost", [
        ("Ney, form square", "Normandy"),
        ("set the fleet to home waters", "Stockholm"),
        ("grant Ney a rente", "Crete"),
        ("Ney, stop attacking", "Estonia"),
        ("Ney, attack no more", "Moore"),
        ("we lost the attack", "Ulster"),
        ("I was thinking of attacking", "Wales"),
        ("wait what", "White Russia"),
    ])
    def test_no_province_is_conjured_out_of_ordinary_english(self, board, text, ghost):
        """Each `ghost` is the real province the free-text target scan used to
        produce for that sentence, at confidence 0.8-0.9, as the place a
        marshal was ordered to take."""
        result = run(board, text)
        target = (result.get("command") or {}).get("target")
        assert target != ghost, f"{text!r} still conjures {ghost}"

    def test_hold_the_pass_holds(self, board):
        """Two defects in four words: 'pass' the noun fired the turn-passing
        verb, and the leftover noun fuzzed into a standing HOLD on Nassau."""
        result = run(board, "Ney, hold the pass")
        assert result["command"]["action"] == "hold"
        assert result["command"]["target"] != "Nassau"


# ════════════════════════════════════════════════════════════════════════
# 3. The guards must not over-fire
# ════════════════════════════════════════════════════════════════════════

class TestGuardsStayNarrow:

    @pytest.mark.parametrize("text,action", [
        ("Ney, attack Mack", "attack"),
        ("Davout, fortify", "fortify"),
        ("Ney, move to Lorraine", "move"),
        ("Soult, scout Swabia", "scout"),
        ("Ney, march to Vienna", "move"),
        ("Ney, hold until relieved", "hold"),
        ("Ney, pursue Mack", "attack"),
        ("Ney, support Davout", "move"),
        ("Ney, dig in", "fortify"),
        ("Ney, charge Mack", "charge"),
        ("Ney, give them no quarter", "attack"),
        ("Ney, attack without hesitation", "attack"),
        ("Ney, march to Vienna and attack", "attack"),
        ("Ney, attack once more", "attack"),
        ("Ney, go after Blucher", "attack"),
    ])
    def test_ordinary_orders_are_untouched(self, board, text, action):
        assert action_of(board, text) == action, text

    @pytest.mark.parametrize("text", [
        "would you have Ney attack Mack",
        "have Ney attack Mack",
        "tell Ney to attack Mack",
        "order Ney to attack Mack",
        "Ney is to attack Mack",
        "Ney shall attack Mack",
        "can you attack Mack",
    ])
    def test_polite_orders_still_march(self, board, text):
        """The question guard's boundary. `would`/`will`/`shall` front ORDERS,
        and a modal lead with no question mark and no first-person subject is
        an order too."""
        result = run(board, text)
        assert result["command"]["action"] == "attack", text
        assert result["command"]["target"] == "Mack", text

    def test_talleyrands_desk_keeps_its_own_answer_for_questions(self, board):
        """The advisory desk answers a question better than the help screen
        does, so the clause guards yield to it entirely. This case caught two
        of the fix's own regressions during the build."""
        result = run(board, "Talleyrand, should we declare war on Prussia?")
        assert result["command"]["diplomatic_data"]["action"] == "diplomatic_advisory"
        result = run(board, "Talleyrand, what about Prussia?")
        assert result["command"]["diplomatic_data"]["action"] == "diplomatic_advisory"

    def test_stand_down_does_not_eat_peace_or_pensions(self, board):
        peace = run(board, "Talleyrand, stop the war with Britain")
        assert peace["command"]["diplomatic_data"]["proposal_type"] == "peace"
        assert action_of(board, "stop Davout's pension") == "revoke_pension"

    def test_go_to_war_is_still_a_declaration(self, board):
        result = run(board, "go to war with Britain")
        assert result["command"]["action"] == "diplomatic_declare_war"

    def test_typos_still_auto_correct(self, board):
        """The target-scan tightening is a typo-SHAPE gate, not a ban on
        fuzzy matching."""
        assert run(board, "Ney, march to viena")["command"]["target"] == "Vienna"
        assert run(board, "Ney, attack Mac")["command"]["target"] == "Mack"

    def test_debug_and_cheat_arguments_are_never_blanked(self, board):
        """Both take literal arguments that can contain guard markers."""
        result = run(board, "cheat gold 500")
        assert result["command"]["action"] == "cheat"
        assert result["command"]["cheat_args"] == ["500"]

    def test_raw_command_records_what_the_player_typed(self, board):
        """Not the clause-guarded working copy — CR-5 attribution and the
        campaign log quote this back."""
        typed = "Ney, hold your position, do not attack"
        assert run(board, typed)["command"]["raw_command"] == typed


# ════════════════════════════════════════════════════════════════════════
# 4. End to end
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app)
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestRefusalReachesThePlayer:

    def test_negation_gets_its_own_berthier_line(self, endpoint):
        data = endpoint.post("/command", json={"command": "Ney, never attack Mack"}).json()
        assert data["success"] is False
        assert "no order goes out" in data["message"]
        # Not the generic recovery shrug.
        assert "cannot interpret" not in data["message"]
        # And it is free: a refusal must never bill an action point.
        assert data["action_info"]["cost"] == 0

    def test_conditional_gets_a_different_line_that_teaches_the_supported_form(
            self, endpoint):
        data = endpoint.post(
            "/command",
            json={"command": "Ney, if Wellington advances fall back to Paris"}).json()
        assert data["success"] is False
        assert "contingency" in data["message"]
        assert "hold until" in data["message"]

    def test_a_question_shows_the_command_reference(self, endpoint):
        data = endpoint.post("/command", json={"command": "how do I attack?"}).json()
        assert data["success"] is True

    def test_no_army_moves_on_a_refusal(self, endpoint):
        import backend.main as main_module
        before = {m.name: m.location for m in main_module.world.marshals.values()}
        endpoint.post("/command", json={"command": "Ney, never attack Wellington"})
        after = {m.name: m.location for m in main_module.world.marshals.values()}
        assert before == after


class TestRefusalIsTerminal:
    """A DEVIATION from the filed prescription, recorded deliberately.

    BUG_FIXES §PARSE-NEG asks for the confidence to be demoted "so the LLM is
    actually consulted". The confidence IS demoted — but escalation is
    declined for a refusal, because under forced tool-use every model reply
    must name an action from the enum, and the one sentence we would be handing
    over is the one whose only verb the player forbade. Whenever an order
    survives the negated clause the guard returns it and never reaches here.
    """

    def test_confidence_is_honestly_below_the_gate(self):
        from backend.ai.llm_client import LLMClient
        result = LLMClient(use_real_api=False)._parse_with_mock("Ney, never attack Mack")
        assert result.confidence < LLM_FALLBACK_CONFIDENCE_THRESHOLD
        assert result.refusal == "negation"

    def test_escalation_is_declined_for_a_refusal(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        client.provider_name = "anthropic"
        client.api_key = "test-key-not-used"
        refusal = client._parse_with_mock("Ney, never attack Mack")
        assert client._should_fallback_to_llm(refusal, {"marshals": {}}) is False
        # …while an ordinary low-confidence parse still escalates, so this is a
        # refusal rule and not a blanket short-circuit.
        vague = client._parse_with_mock("Soult, dig in where you are")
        assert vague.confidence < LLM_FALLBACK_CONFIDENCE_THRESHOLD
        assert client._should_fallback_to_llm(vague, {"marshals": {}}) is True
