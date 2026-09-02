"""FA-N2 / FA-N3 / FA-N4(half) / FA-N5 / FA-N37 — the verification pass's P1s.

The September 2, 2026 verification pass of the Final Whole-Game Audit
(``docs/audits/FINAL_AUDIT_VERIFICATION_2026_09_02.md`` §5) filed five new P1s
the audit itself had missed, every one of them the audit's own through-line
one layer further out: *the game computes the right answer and then acts on a
different one.*

**The suite was completely blind to all of them.** Measured before this file
existed: 19,387 tests pass green while ``do not accept`` signs a treaty, a
battle that annihilates the enemy is reported as inconclusive, and the
vassal-rebellion modal signs a non-aggression pact with an unrelated great
power. Every test here fails when its fix is reverted; that is the file's
whole purpose.

Row map:
  FA-N2  — a negated answer to any pending dialogue executed the affirmative.
  FA-N3  — a battle an aggressive marshal fought under a standing order was
           reported INCONCLUSIVE, and his ``last_combat_result`` corrupted.
  FA-N4  — (second half only) a REFUSED Request Revision was narrated in
           Talleyrand's success voice. The staging half is a settlement-slice
           change; see the landing record for why it is not here.
  FA-N5  — blocking modals answered whatever dialogue was on top.
  FA-N37 — the same defect from the delivery side.
"""

import ast
import re
from pathlib import Path

import pytest

from backend.ai.clause_guards import negation_marker_spans
from backend.commands.dialogue_routing import (
    DIALOGUE_ACTION_KEYWORDS,
    _self_negating_answer_tokens,
    match_dialogue_answer,
    text_the_player_still_means,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO = str(
    REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

ROSTER = ["Ney", "Davout", "Soult", "Murat", "Lannes", "Bernadotte", "Massena"]

PROPOSAL = {"type": "incoming_proposal", "options": [
    {"label": "Accept", "action": "accept_ai_proposal"},
    {"label": "Reject", "action": "reject_ai_proposal"},
    {"label": "Counter-offer", "action": "counter_ai_proposal"},
]}
ULTIMATUM = {"type": "incoming_ultimatum", "options": [
    {"label": "Yield", "action": "yield_ultimatum"},
    {"label": "Defy", "action": "defy_ultimatum"},
]}
ALLY_ENTRY = {"type": "proposal_confirm", "options": [
    {"label": "Accept Ally Entry", "action": "ally_entry_accept_all"},
    {"label": "Proceed Without Allies", "action": "ally_entry_proceed_without"},
    {"label": "Back Out", "action": "ally_entry_back_out"},
]}
ADVISORY = {"type": "advisory", "options": [
    {"label": "Execute", "action": "execute_suggestion"},
    {"label": "Dismiss", "action": "dismiss"},
]}


# ══════════════════════════════════════════════════════════════════════
# FA-N2 — a refusal is not consent
# ══════════════════════════════════════════════════════════════════════

class TestFAN2NegatedAnswers:

    @pytest.mark.parametrize("line", [
        "do not accept",
        "don't accept",
        "never accept",
        "we will not accept this",
        "I refuse to accept these terms",
        "under no circumstances accept",
        "do not accept these terms, reconsider",
    ])
    def test_a_negated_accept_answers_nothing(self, line):
        """Every one of these returned ``accept`` and SIGNED THE TREATY."""
        assert match_dialogue_answer(
            PROPOSAL, line.lower(), ROSTER, world_regions=[]) is None

    @pytest.mark.parametrize("line", [
        "do not yield", "we will not yield", "never yield",
    ])
    def test_a_negated_yield_concedes_nothing(self, line):
        """``we will not yield`` CONCEDED the ultimatum — the demanded
        provinces ceded by a sentence refusing to cede them."""
        assert match_dialogue_answer(
            ULTIMATUM, line.lower(), ROSTER, world_regions=[]) is None

    @pytest.mark.parametrize("line,expected", [
        ("accept", "accept"),
        ("reject", "reject"),
        ("accept prussia's proposal", "accept"),
        ("reject the offer", "reject"),
    ])
    def test_the_affirmative_still_answers(self, line, expected):
        """The negative control. A guard that refused everything would pass
        every test above and ship a dialogue nobody can answer."""
        assert match_dialogue_answer(
            PROPOSAL, line, ROSTER, world_regions=[]) == expected

    def test_a_bare_not_is_a_documented_limit_not_a_claim(self):
        """``strip_negated_clauses`` deliberately excludes a bare ``not`` (it
        collides with CR-4's ``not you, Davout`` rewrite), so ``not accept``
        is NOT caught. Recorded here rather than discovered later: this row's
        scope is the marker vocabulary PARSE-NEG already ships, and widening
        it is a PARSE-NEG change."""
        assert match_dialogue_answer(
            PROPOSAL, "not accept", ROSTER, world_regions=[]) == "accept"


class TestFAN2SelfNegatingTokensAreExempt:
    """A token that IS a negation may still answer; a negation ABOUT an
    answer may not. Both exemptions are load-bearing on shipped content."""

    def test_the_label_that_is_a_negation_still_answers(self):
        assert match_dialogue_answer(
            ALLY_ENTRY, "proceed without allies", ROSTER,
            world_regions=[]) == "proceed without allies"

    def test_negating_that_label_does_not_answer_with_it(self):
        """A naive exemption (restore every occurrence) answered this WITH
        the very option the sentence refuses."""
        assert match_dialogue_answer(
            ALLY_ENTRY, "never proceed without allies", ROSTER,
            world_regions=[]) is None

    def test_the_keyword_that_is_a_negation_still_answers(self):
        """A label-only exemption reds this — measured, it was the single
        red in a 19,391-test suite."""
        assert match_dialogue_answer(
            ADVISORY, "never mind", ROSTER, world_regions=[]) == "never mind"
        assert match_dialogue_answer(
            ADVISORY, "never mind the money", ROSTER) == "never mind"

    def test_an_order_wearing_the_keyword_still_does_not_answer(self):
        assert match_dialogue_answer(
            ADVISORY, "never mind the enemy, ney attack", ROSTER,
            world_regions=[]) is None

    def test_the_token_set_is_computed_not_enumerated(self):
        """Today exactly two self-negating answer tokens exist in the shipped
        game. The guard must find a THIRD automatically — an enumeration
        would silently stop protecting new content."""
        tokens = set(_self_negating_answer_tokens(ALLY_ENTRY["options"]))
        assert "proceed without allies" in tokens
        assert "never mind" in tokens
        invented = {"options": [
            {"label": "Do not intervene", "action": "stand_aside"},
            {"label": "Intervene", "action": "intervene"},
        ]}
        assert "do not intervene" in set(
            _self_negating_answer_tokens(invented["options"]))
        assert match_dialogue_answer(
            invented, "do not intervene", ROSTER,
            world_regions=[]) == "do not intervene"

    def test_the_second_self_negating_label_is_protected_too(self):
        """The jealousy Fontainebleau refusal is labelled (with its quote
        marks) ``"The Empire does not beg"`` — ``does not`` is a negation
        marker, so blanking would have made it unanswerable. Restored by the
        same computed rule, with no line of code naming it.

        It is here because a hand-written regex census over ``"label": "..."``
        MISSED it (the label embeds quote marks), and the AST census below
        found it. The unquoted form does not match, and did not before this
        row either — the label carries its quotes."""
        dialogue = {"options": [
            {"label": '"The Empire does not beg"', "action": "refuse_terms"},
            {"label": "Sue for peace", "action": "sue_for_peace"},
        ]}
        assert match_dialogue_answer(
            dialogue, '"the empire does not beg"', ROSTER,
            world_regions=[]) == '"the empire does not beg"'
        assert match_dialogue_answer(
            dialogue, "sue for peace", ROSTER,
            world_regions=[]) == "sue for peace"

    def test_the_census_of_shipped_labels_is_still_two(self):
        """A tripwire on content, not a rule. If a third self-negating LABEL
        is authored, this fails and the author reads the exemption's
        contract — then raises the number and names the label."""
        labels = set()
        for path in (REPO_ROOT / "backend").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Dict):
                    continue
                for key, value in zip(node.keys, node.values):
                    if (isinstance(key, ast.Constant) and key.value == "label"
                            and isinstance(value, ast.Constant)
                            and isinstance(value.value, str)):
                        labels.add(value.value)
        negating = sorted(
            lab for lab in labels
            if negation_marker_spans(lab.lower().strip()))
        assert negating == ['"The Empire does not beg"',
                            "Proceed Without Allies"], negating

    def test_exactly_one_keyword_is_self_negating(self):
        negating = sorted(
            kw for kw in DIALOGUE_ACTION_KEYWORDS if negation_marker_spans(kw))
        assert negating == ["never mind"], negating


class TestFAN2TheGuardsStillReadWhatWasSaid:
    """The regression the first cut of this fix SHIPPED, and the reason the
    file says *an answer is read from what the player still MEANS; an order
    is detected from what they SAID.*

    Reassigning ``raw_lower`` to the stripped line fed the blanked text to
    the two guards as well as to the matching arms — silently disarming
    both, because a prohibition is still military content and a name inside
    a prohibition is still a name. **No pin in the suite bound either guard
    against negated input**, so the full suite stayed green at 19,387 with
    the regression in tree, and the one pin that should have caught it went
    VACUOUS instead of red (``never mind the money`` stopped reaching
    ``_names_a_marshal``, so mutating that guard to bare containment — the
    precise defect its own comment cites — no longer failed).
    """

    CONFIRM = {"type": "settlement_confirm", "options": [
        {"label": "Confirm", "action": "confirm_settlement"},
        {"label": "Revise Terms", "action": "revise_terms"},
        {"label": "Cancel", "action": "cancel_settlement"},
    ]}

    @pytest.mark.parametrize("line", [
        "without ney, cancel",
        "avoid ney, cancel",
        "instead of ney, cancel",
        "rather than send ney, cancel",
        "davout will not march, cancel",
    ])
    def test_a_marshal_named_inside_a_negation_is_still_a_marshal(self, line):
        """UX23-R5 under negation. The first cut answered ``cancel`` to all
        but the last — measured, ``without ney, cancel`` CANCELLED THE
        SETTLEMENT."""
        assert match_dialogue_answer(
            self.CONFIRM, line, ROSTER,
            world_regions=["Paris", "Swabia"]) is None

    @pytest.mark.parametrize("dialogue_key,line", [
        ("confirm", "cancel, do not march north"),
        ("confirm", "cancel; never attack swabia"),
        ("confirm", "confirm, do not attack"),
        ("proposal", "accept, never march on paris"),
    ])
    def test_a_forbidden_order_is_still_military_content(self, dialogue_key,
                                                         line):
        """The Aug-30 guard under negation. The first cut answered every one
        of these, discarding the order half of the sentence without telling
        the player — and `accept, never march on paris` SIGNED THE TREATY,
        measured end to end through /command on the 1805 boot."""
        dialogue = self.CONFIRM if dialogue_key == "confirm" else PROPOSAL
        assert match_dialogue_answer(
            dialogue, line, ROSTER,
            world_regions=["Paris", "Swabia"]) is None

    def test_the_negation_fix_still_holds_alongside_both_guards(self):
        """The three rules coexist: refuse the negated answer, keep the
        marshal guard, keep the military guard, and still answer plainly."""
        assert match_dialogue_answer(
            PROPOSAL, "do not accept", ROSTER, world_regions=[]) is None
        assert match_dialogue_answer(
            PROPOSAL, "accept", ROSTER, world_regions=[]) == "accept"
        assert match_dialogue_answer(
            self.CONFIRM, "cancel", ROSTER,
            world_regions=["Paris"]) == "cancel"


class TestFAN2IndexPreservation:
    """The restore is a character splice into an index-preserving blank. If
    ``strip_negated_clauses`` ever stopped preserving length the splice would
    corrupt the line silently, so pin the contract it rests on."""

    @pytest.mark.parametrize("line", [
        "do not accept", "never mind the money", "proceed without allies",
        "ney, hold your position, do not attack",
    ])
    def test_the_guard_never_changes_the_length_of_the_line(self, line):
        assert len(
            text_the_player_still_means(line, PROPOSAL["options"])) == len(line)


# ══════════════════════════════════════════════════════════════════════
# FA-N3 — a battle reports what happened
# ══════════════════════════════════════════════════════════════════════

def _standing_order_world():
    from backend.models.marshal import StrategicOrder
    from backend.models.world_state import WorldState
    world = WorldState.from_scenario(SCENARIO)
    ney = world.get_marshal("Ney")
    ney.location = "Rhineland"
    ney.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Frankfurt", target_type="region",
        started_turn=world.current_turn - 1,
        original_command="Ney, march to Frankfurt",
        issued_turn=world.current_turn - 1)
    mack = world.get_marshal("Mack")
    mack.location = "Frankfurt"
    world.calculate_visibility()
    return world, ney, mack


def _run_orders(world):
    from backend.commands.executor import CommandExecutor
    from backend.commands.strategic import StrategicOrderProcessor
    reports = StrategicOrderProcessor(
        CommandExecutor()).process_strategic_orders(world, {"world": world})
    return [r for r in reports
            if isinstance(r, dict) and r.get("marshal") == "Ney"]


class TestFAN3TheBattleReportsItsOutcome:

    def test_an_annihilation_is_reported_as_a_victory(self, monkeypatch):
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        world, ney, mack = _standing_order_world()
        ney.strength = 60000
        mack.strength = 12000
        rows = _run_orders(world)
        assert rows, "the aggressive contact arm did not fire"
        row = rows[0]
        assert row.get("outcome") == "victory", row.get("message")
        assert row.get("order_status") == "continues"
        assert "inconclusive" not in str(row.get("message", "")).lower()
        # The interrupt asking "shall I press on?" must not be armed.
        assert (ney.pending_interrupt or {}).get(
            "interrupt_type") != "combat_stalemate"
        # Loop prevention must not count a total victory as a failed attempt.
        assert ney.strategic_order.combat_attempts == 0

    def test_the_marshals_own_combat_record_is_not_corrupted(self, monkeypatch):
        """The consequence the row itself missed: ``_post_combat_pipeline``
        already writes the correct value inside ``_execute_attack``, and this
        function then overwrote it with ``stalemate``. Identical attacks gave
        different records depending only on whether a standing order was in
        force."""
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        world, ney, mack = _standing_order_world()
        ney.strength = 60000
        mack.strength = 12000
        _run_orders(world)
        assert ney.last_combat_result == "victory"

    def test_the_stored_outcome_speaks_the_readers_vocabulary(self, monkeypatch):
        """``order.last_combat_result`` used to store combat.py's raw
        six-word outcome — a fourth vocabulary no reader in the file
        speaks."""
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        world, ney, mack = _standing_order_world()
        ney.strength = 60000
        mack.strength = 12000
        _run_orders(world)
        order = world.get_marshal("Ney").strategic_order
        assert order is None or order.last_combat_result in {
            "victory", "defeat", "stalemate"}

    def test_the_dead_read_could_never_have_worked(self):
        """Structural, and the reason this survived for months: ``combat.py``
        assigns six outcome words and NONE of them is the literal ``victory``
        or ``defeat`` the arms compared against."""
        source = (REPO_ROOT / "backend" / "game_logic" / "combat.py").read_text(
            encoding="utf-8")
        assigned = set(re.findall(r'outcome\s*=\s*"([a-z_]+)"', source))
        assert assigned == {
            "mutual_destruction", "defender_victory", "attacker_victory",
            "defender_tactical_victory", "attacker_tactical_victory",
            "stalemate",
        }, assigned
        assert "victory" not in assigned and "defeat" not in assigned

    def test_the_victor_is_read_not_the_outcome_word(self):
        """Drift pin. If a future edit reverts to reading
        ``events[0]["outcome"]`` alone, the annihilation test goes red — this
        one names why."""
        source = (REPO_ROOT / "backend" / "commands" / "strategic.py").read_text(
            encoding="utf-8")
        body = source[source.index("def _handle_combat_result"):]
        body = body[:body.index("\n    def ", 10)]
        assert 'event.get("victor")' in body
        assert '"attacker_won"' in body


class TestFAN3TheGloriousChargeIsNotADraw:

    def test_a_charge_event_is_read_by_its_own_flag(self):
        """The charge event carries no ``victor`` key at all — the row's own
        prescribed one-liner would have left it reporting stalemate."""
        from backend.commands.strategic import StrategicOrderProcessor

        class _Order:
            command_type = "MOVE_TO"
            combat_attempts = 0
            last_combat_enemy = ""
            last_combat_turn = 0
            last_combat_result = ""

        class _M:
            def __init__(self):
                self.name = "Ney"
                self.location = "Rhineland"
                self.strategic_order = _Order()
                self.in_combat_this_turn = False
                self.last_combat_turn = 0
                self.last_combat_location = ""
                self.last_combat_result = ""
                self.pending_interrupt = None

        class _E:
            name = "Mack"

        class _W:
            current_turn = 3

        proc = StrategicOrderProcessor.__new__(StrategicOrderProcessor)
        won = proc._handle_combat_result(
            _M(), _E(),
            {"events": [{"type": "glorious_charge", "attacker_won": True}]},
            _W(), {})
        assert won["outcome"] == "victory"
        lost = proc._handle_combat_result(
            _M(), _E(),
            {"events": [{"type": "glorious_charge", "attacker_won": False}]},
            _W(), {})
        assert lost["outcome"] == "defeat"

    def test_an_artillery_annihilation_is_not_a_draw(self):
        """The shape the first cut of this fix MISSED, found by attacking it.

        `combat_executor`'s `auto_kill_event` (the auto-bombardment kill) is
        `type: "battle"` with `outcome: "attacker_victory"` and **no victor
        key at all** — a fourth event shape. A victor-only read finds nothing
        and falls to the draw arm, so a corps annihilated by artillery under
        a standing order still reported "inconclusive". The marshal is always
        the attacker at this seam, so the attacker/defender half of
        combat.py's own vocabulary is the answer."""
        from backend.commands.strategic import StrategicOrderProcessor

        class _Order:
            command_type = "MOVE_TO"
            combat_attempts = 0
            last_combat_enemy = ""
            last_combat_turn = 0
            last_combat_result = ""

        class _M:
            def __init__(self):
                self.name = "Ney"
                self.location = "Rhineland"
                self.strategic_order = _Order()
                self.in_combat_this_turn = False
                self.last_combat_turn = 0
                self.last_combat_location = ""
                self.last_combat_result = ""
                self.pending_interrupt = None

        class _E:
            name = "Mack"

        class _W:
            current_turn = 3

        proc = StrategicOrderProcessor.__new__(StrategicOrderProcessor)
        for word, expected in (("attacker_victory", "victory"),
                               ("attacker_tactical_victory", "victory"),
                               ("defender_victory", "defeat"),
                               ("defender_tactical_victory", "defeat"),
                               ("mutual_destruction", "stalemate"),
                               ("stalemate", "stalemate")):
            row = proc._handle_combat_result(
                _M(), _E(),
                {"events": [{"type": "battle", "outcome": word,
                             "auto_bombardment_kill": True}]},
                _W(), {})
            assert row["outcome"] == expected, (word, row["outcome"])

    def test_a_victor_with_no_outcome_word_is_still_read(self):
        """ISOLATION for the victor read. With the outcome-word fallback in
        place the two paths agree on every real event, so a sweep found the
        victor mutation inert. This shape has only the victor — which is the
        idiom `_respond_blocked_path` uses and the one this fix was written
        around."""
        from backend.commands.strategic import StrategicOrderProcessor

        class _Order:
            command_type = "MOVE_TO"
            combat_attempts = 0
            last_combat_enemy = ""
            last_combat_turn = 0
            last_combat_result = ""

        class _M:
            def __init__(self):
                self.name = "Ney"
                self.location = "Rhineland"
                self.strategic_order = _Order()
                self.in_combat_this_turn = False
                self.last_combat_turn = 0
                self.last_combat_location = ""
                self.last_combat_result = ""
                self.pending_interrupt = None

        class _E:
            name = "Mack"

        class _W:
            current_turn = 3

        proc = StrategicOrderProcessor.__new__(StrategicOrderProcessor)
        won = proc._handle_combat_result(
            _M(), _E(), {"events": [{"type": "battle", "victor": "Ney"}]},
            _W(), {})
        assert won["outcome"] == "victory"
        lost = proc._handle_combat_result(
            _M(), _E(), {"events": [{"type": "battle", "victor": "Mack"}]},
            _W(), {})
        assert lost["outcome"] == "defeat"

    def test_the_battle_is_found_when_it_is_not_the_first_event(self):
        """ISOLATION PIN. The row's own prescribed one-liner reads
        `events[0]` and trusts it. Every arm above happens to put the battle
        first, so a sweep of the scan found the pin INERT — the scan and an
        index read are indistinguishable on a one-event result. Here they are
        not: a march event precedes the battle, and index-0 reading yields no
        victor and reports a total victory as a draw."""
        from backend.commands.strategic import StrategicOrderProcessor

        class _Order:
            command_type = "MOVE_TO"
            combat_attempts = 0
            last_combat_enemy = ""
            last_combat_turn = 0
            last_combat_result = ""

        class _M:
            def __init__(self):
                self.name = "Ney"
                self.location = "Rhineland"
                self.strategic_order = _Order()
                self.in_combat_this_turn = False
                self.last_combat_turn = 0
                self.last_combat_location = ""
                self.last_combat_result = ""
                self.pending_interrupt = None

        class _E:
            name = "Mack"

        class _W:
            current_turn = 3

        proc = StrategicOrderProcessor.__new__(StrategicOrderProcessor)
        row = proc._handle_combat_result(
            _M(), _E(),
            {"events": [
                {"type": "move", "marshal": "Ney", "to": "Frankfurt"},
                {"type": "battle", "outcome": "attacker_victory",
                 "victor": "Ney"},
            ]},
            _W(), {})
        assert row["outcome"] == "victory"


# ══════════════════════════════════════════════════════════════════════
# FA-N5 / FA-N37 — a blocking modal answers its own dialogue
# ══════════════════════════════════════════════════════════════════════

def _client_world(monkeypatch):
    from fastapi.testclient import TestClient

    import backend.main as main_module
    from backend.commands.parser import CommandParser
    from backend.models.world_state import WorldState
    monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
    world = WorldState.from_scenario(SCENARIO)
    monkeypatch.setattr(main_module, "parser", CommandParser(use_real_llm=False))
    monkeypatch.setattr(main_module, "world", world)
    monkeypatch.setattr(main_module, "game_state", {"world": world})
    return world, TestClient(main_module.app)


def _prussian_letter(world):
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    world.nation_relations[world._make_diplo_key("France", "Prussia")] = 60
    deliver_ai_proposal({"proposal_type": "non_aggression",
                         "source": "Prussia",
                         "terms": {"type": "non_aggression"}}, world)


def _letter_then_rebellion(world):
    """The exact measured scene: Prussia's letter holds the dialogue slot
    when the Holland rebellion is raised."""
    from backend.game_logic.vassal import process_vassal_loyalty
    _prussian_letter(world)
    for row in world.vassals.values():
        if row.get("lord") == "France":
            row["loyalty"] = 9
    process_vassal_loyalty(world)


def _queue_a_sabotage_dialogue(world) -> int:
    """A live-but-not-current dialogue, so its popup is DELAYED rather than
    reaped. A synthetic id belonging to no dialogue is a DEAD id, and the
    gate correctly drops those — which is a different rule being tested
    elsewhere in this class."""
    dialogue = {
        "type": "sabotage_confrontation",
        "target_nation": "Austria",
        "turn_created": int(world.current_turn),
        "options": [{"label": "Confront", "action": "confront_sabotage"},
                    {"label": "Overlook", "action": "overlook_sabotage"}],
    }
    world.dialogue_manager.push(dialogue)
    assert world.dialogue_manager.peek() is not dialogue, (
        "precondition: the letter must still hold the slot")
    return int(dialogue["dialogue_id"])


class TestFAN5ProducersStampIdentity:

    def test_the_rebellion_popup_carries_its_dialogues_id(self, monkeypatch):
        world, _ = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        popups = world.vassal_rebellion_imminent_popups or []
        assert popups, "no rebellion was raised"
        assert all(p.get("dialogue_id") is not None for p in popups), popups
        queued = [d for d in world.dialogue_manager.iter_queue()
                  if d.get("type") == "vassal_rebellion_imminent"]
        assert queued
        assert {p["dialogue_id"] for p in popups} <= {
            d.get("dialogue_id") for d in queued}

    def test_every_modal_producer_binds_popup_to_dialogue(self):
        """Source pin over the three producers that build a popup and its
        dialogue as separate dicts. A fourth arriving without a binding is
        the next instance of this defect."""
        for rel, marker in (
            ("backend/game_logic/vassal.py",
             'rebellion_popup["dialogue_id"]'),
            ("backend/game_logic/diplomacy.py",
             'paradox_popup["dialogue_id"]'),
            ("backend/game_logic/dispatch.py",
             '"dialogue_id": confrontation.get("dialogue_id")'),
        ):
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            assert marker in text, rel


class TestFAN37TheModalIsNotShownOverAnotherDialogue:

    def test_the_rebellion_modal_waits_for_its_turn(self, monkeypatch):
        world, client = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        assert world.dialogue_manager.peek()["type"] == "incoming_proposal"
        queued_before = len(world.vassal_rebellion_imminent_popups)
        assert queued_before >= 2, "expected Holland and Switzerland"
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("vassal_rebellion_imminent") is None, (
            "the rebellion modal was delivered over an envoy's letter")
        # ISOLATION for the LIST-side guard: the popup is not merely
        # undelivered, it is not even taken OUT of its own list. Asserting
        # only "the list is non-empty" left the auto-pop gate's mutation
        # inert, because the queue-side gate independently blocked delivery.
        assert len(world.vassal_rebellion_imminent_popups) == queued_before
        assert world.vassal_rebellion_imminent_popups[0]["nation"] == "Holland"

    def test_it_is_delivered_once_its_own_dialogue_is_current(self, monkeypatch):
        """Delayed, not dropped — and delayed by exactly one cycle. Answering
        the letter promotes the rebellion dialogue, and the SAME response
        carries the modal, now identified."""
        world, client = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        body = client.post("/respond_to_diplomatic_dialogue", json={
            "choice": "reject_ai_proposal",
            "dialogue_id": world.dialogue_manager.peek().get("dialogue_id"),
        }).json()
        assert world.dialogue_manager.peek()["type"] == \
            "vassal_rebellion_imminent"
        modal = body.get("vassal_rebellion_imminent")
        assert modal is not None, "the rebellion modal was starved"
        assert modal.get("nation") == "Holland"
        assert modal.get("dialogue_id") == \
            world.dialogue_manager.peek().get("dialogue_id")

    def test_the_delivery_gate_stands_on_its_own(self, monkeypatch):
        """ISOLATION PIN for the QUEUE-side guard.

        Two guards close this defect — the auto-pop gate on the rebellion
        LIST and `_pop_deliverable_popup` on the queue — and a mutation sweep
        found each INERT because the other still held. This test reaches the
        queue directly, with a popup that OUTRANKS the mounted letter in
        `PopupQueue.PRIORITY_ORDER` (sabotage is index 1, incoming_proposal
        index 6), so `pop_highest` would hand it over first. A first draft
        used the paradox popup and was itself inert — paradox sits BELOW
        incoming_proposal, so priority, not the gate, was doing the work.
        Reverting the gate must make the wrong modal appear."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        own_id = _queue_a_sabotage_dialogue(world)
        world._popup_queue.push("diplomatic_sabotage_popup", {
            "target_nation": "Austria", "dialogue_id": own_id,
        })
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("diplomatic_sabotage") is None, (
            "a sabotage modal was delivered over an envoy's letter")
        # Delayed, never dropped — its dialogue is alive, merely queued.
        assert world._popup_queue.get("diplomatic_sabotage_popup") is not None

    def test_the_held_popup_is_delivered_when_its_dialogue_is_current(
            self, monkeypatch):
        """The other half: the gate must DELAY, not drop. A guard that
        discarded the blocked popup would satisfy every 'not delivered'
        assertion above and silently lose the question."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        own_id = _queue_a_sabotage_dialogue(world)
        world._popup_queue.push("diplomatic_sabotage_popup", {
            "target_nation": "Austria", "dialogue_id": own_id,
        })
        client.post("/command", json={"command": "status"})
        world.dialogue_manager.replace({
            "type": "sabotage_confrontation", "dialogue_id": own_id,
            "options": [{"label": "Confront", "action": "confront_sabotage"}],
        })
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("diplomatic_sabotage") is not None, (
            "the held popup was dropped instead of delayed")

    def test_a_lower_priority_popup_is_not_starved_behind_a_blocked_one(
            self, monkeypatch):
        """The gate skips past a blocked popup rather than returning empty,
        so an answerable modal still reaches the player this cycle."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        letter_id = world.dialogue_manager.peek().get("dialogue_id")
        world._popup_queue.push("diplomatic_sabotage_popup", {
            "target_nation": "Austria",
            "dialogue_id": (letter_id or 0) + 500,
        })
        world._popup_queue.push("incoming_proposal_popup", {
            "source": "Prussia", "dialogue_id": letter_id,
        })
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("diplomatic_sabotage") is None
        assert body.get("incoming_proposal") is not None, (
            "the answerable popup was starved behind a blocked one")

    def test_a_swept_dialogue_does_not_silence_the_channel_forever(
            self, monkeypatch):
        """P1 THE GATE ITSELF WOULD HAVE INTRODUCED, found by attacking it.

        `DialogueManager.clear_stale` drops a QUEUED blocking dialogue two
        turns after it was created and touches no popup, and `push` stamps an
        id BEFORE the QUEUE_CAP check — so a popup can name a dialogue that
        no longer exists. A gate that only asks *is it current?* holds such a
        popup forever: the vassal-rebellion warning goes permanently silent
        and the zombie is serialized into every save. A dead dialogue's popup
        is reaped, not held."""
        world, client = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        # Sweep the queued rebellion dialogues out from under their popups.
        world.dialogue_manager._queue = [
            d for d in world.dialogue_manager.iter_queue()
            if d.get("type") != "vassal_rebellion_imminent"]
        assert world.vassal_rebellion_imminent_popups, "precondition"
        client.post("/command", json={"command": "status"})
        assert world.vassal_rebellion_imminent_popups == [], (
            "orphaned popups were held instead of reaped")
        # And the channel heals: a fresh pair is delivered normally.
        world.dialogue_manager.pop()
        from backend.game_logic.vassal import process_vassal_loyalty
        for row in world.vassals.values():
            if row.get("lord") == "France":
                row["loyalty"] = 9
        process_vassal_loyalty(world)
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("vassal_rebellion_imminent") is not None

    def test_an_orphan_that_reaches_the_queue_directly_is_reaped_too(
            self, monkeypatch):
        """ISOLATION for the QUEUE-side reaper. The rebellion list has its
        own reaper, which masks this one for that producer — so use a popup
        that never travels through a list. Held forever, it would brick the
        slot and be serialized into every save from then on."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        letter_id = world.dialogue_manager.peek().get("dialogue_id")
        world._popup_queue.push("diplomatic_sabotage_popup", {
            "target_nation": "Austria",
            "dialogue_id": (letter_id or 0) + 900,  # no such dialogue
        })
        body = client.post("/command", json={"command": "status"}).json()
        assert body.get("diplomatic_sabotage") is None
        assert world._popup_queue.get("diplomatic_sabotage_popup") is None, (
            "a popup whose dialogue no longer exists was held, not reaped")

    def test_a_blocked_head_does_not_starve_the_rest_of_the_list(
            self, monkeypatch):
        """`process_vassal_loyalty` appends a fresh entry every turn a vassal
        sits at loyalty <= 10, with no once-per-vassal latch — so peeking at
        index 0 turns transient head-of-line blocking into permanent
        blocking. The auto-pop scans."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        letter_id = world.dialogue_manager.peek().get("dialogue_id")
        world.vassal_rebellion_imminent_popups.append(
            {"nation": "Holland", "loyalty": 9,
             "dialogue_id": (letter_id or 0) + 500})
        world.vassal_rebellion_imminent_popups.append(
            {"nation": "Switzerland", "loyalty": 8,
             "dialogue_id": (letter_id or 0) + 501})
        world.dialogue_manager.push({
            "type": "vassal_rebellion_imminent", "target_nation": "Holland",
            "dialogue_id": (letter_id or 0) + 500, "blocking": True,
            "turn_created": int(world.current_turn),
            "options": [{"label": "Accept Risk",
                         "action": "accept_vassal_rebellion"}]})
        world.dialogue_manager.push({
            "type": "vassal_rebellion_imminent",
            "target_nation": "Switzerland",
            "dialogue_id": (letter_id or 0) + 501, "blocking": True,
            "turn_created": int(world.current_turn),
            "options": [{"label": "Accept Risk",
                         "action": "accept_vassal_rebellion"}]})
        # Make SWITZERLAND's dialogue current — the second entry, not the head.
        world.dialogue_manager.replace({
            "type": "vassal_rebellion_imminent",
            "target_nation": "Switzerland",
            "dialogue_id": (letter_id or 0) + 501, "blocking": True,
            "turn_created": int(world.current_turn),
            "options": [{"label": "Accept Risk",
                         "action": "accept_vassal_rebellion"}]})
        body = client.post("/command", json={"command": "status"}).json()
        modal = body.get("vassal_rebellion_imminent")
        assert modal is not None, "the list was starved behind its head"
        assert modal.get("nation") == "Switzerland"

    def test_an_unbound_popup_is_still_delivered_immediately(self, monkeypatch):
        """The gate is scoped to popups that CARRY an id, which is what keeps
        every surface it was not written for byte-identical. A legacy save's
        popup has no id and must still reach the player."""
        world, client = _client_world(monkeypatch)
        world._popup_queue.push("vassal_rebellion_imminent_popup",
                                {"nation": "Saxony", "loyalty": 4})
        body = client.post("/command", json={"command": "status"}).json()
        assert (body.get("vassal_rebellion_imminent") or {}).get(
            "nation") == "Saxony"


class TestFAN5TheAnswerCannotLandOnAnotherCourt:

    def test_accept_risk_does_not_sign_a_treaty(self, monkeypatch):
        """The measured headline: ``PEACE -> NON_AGGRESSION with Prussia``,
        from a modal about Holland."""
        world, client = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        before = world.get_diplomatic_state("France", "Prussia")
        body = client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": "accept_vassal_rebellion"}).json()
        assert world.get_diplomatic_state("France", "Prussia") == before
        assert "Treaty signed" not in str(body.get("message", ""))

    @pytest.mark.parametrize("token", [
        "accept_vassal_rebellion", "invest_vassal_rebellion",
        "garrison_vassal_rebellion", "confront_sabotage", "honor_defender",
    ])
    def test_a_machine_token_matches_exactly_or_not_at_all(self, token,
                                                           monkeypatch):
        """The floor under identity binding, for an older save or a client
        that sends no id. ``accept_vassal_rebellion`` contains the label
        ``Accept``, and the resolver's containment arm matched it."""
        world, client = _client_world(monkeypatch)
        _letter_then_rebellion(world)
        before = world.get_diplomatic_state("France", "Prussia")
        client.post("/respond_to_diplomatic_dialogue", json={"choice": token})
        assert world.get_diplomatic_state("France", "Prussia") == before

    def test_the_dialogues_own_action_id_still_resolves(self, monkeypatch):
        """Negative control: the guard must not break the buttons that DO
        belong to the mounted dialogue."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        body = client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": "accept_ai_proposal"}).json()
        assert body.get("success") is True, body.get("message")
        assert world.get_diplomatic_state("France", "Prussia") != "PEACE"


class TestFAN2ThirdCopyOnTheFreeTextEndpoint:

    def test_a_negated_answer_over_the_dialogue_endpoint_signs_nothing(
            self, monkeypatch):
        """``POST /respond_to_diplomatic_dialogue`` takes free text and had
        its OWN copy of the keyword scan — the typed-route guard never
        reaches it, and it signed the treaty on ``do not accept``."""
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        before = world.get_diplomatic_state("France", "Prussia")
        body = client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": "do not accept"}).json()
        assert world.get_diplomatic_state("France", "Prussia") == before
        assert "Treaty signed" not in str(body.get("message", ""))

    def test_the_typed_route_refuses_it_too(self, monkeypatch):
        world, client = _client_world(monkeypatch)
        _prussian_letter(world)
        before = world.get_diplomatic_state("France", "Prussia")
        client.post("/command", json={"command": "do not accept"})
        assert world.get_diplomatic_state("France", "Prussia") == before
        assert world.pending_diplomatic_dialogue is not None


class TestClientAnswerSitesCarryIdentity:
    """The Godot half. Every ``send_dialogue_response*`` call in ``main.gd``
    must pass a dialogue id: four of eight passed nothing, and the two that
    answer by bare OPTION INDEX were among them."""

    def test_every_send_site_passes_a_dialogue_id(self):
        text = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
                / "main.gd").read_text(encoding="utf-8")
        calls = re.findall(
            r"api_client\.send_dialogue_response[a-z_]*\((.*)\)", text)
        assert len(calls) >= 8, len(calls)
        assert [c for c in calls if "dialogue_id" not in c] == []


# ══════════════════════════════════════════════════════════════════════
# FA-N4 (second half) — a refusal does not wear the success voice
# ══════════════════════════════════════════════════════════════════════

class TestFAN4TheRefusalSpeaksAsARefusal:

    def test_a_failed_revision_does_not_report_a_counter_draft(self):
        source = (REPO_ROOT / "backend" / "game_logic"
                  / "settlement_offers.py").read_text(encoding="utf-8")
        start = source.index('if action == "request_settlement_revision"')
        branch = source[start:source.index(
            'if action != "accept_settlement_offer"', start)]
        assert 'if result.get("success"):' in branch, (
            "the success voice is assigned unconditionally again")
        assert 'result["message"] = result.get("error_display")' in branch
