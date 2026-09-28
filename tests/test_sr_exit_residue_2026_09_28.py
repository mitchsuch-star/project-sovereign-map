"""The session exit of September 28, 2026 — its ONE residue slice (docs/
SCORE_MANDATE_PLAN.md §5; memo docs/audits/SR_SESSION_EXIT_2026_09_28.md):
the desk reads the laws and the points, and the morning lead names its
occupier as printed.

* R1 (SRX-11) — the bare word "laws" (like "economy" and "status") asks for
  the laws; the exit's laws arm typed it and got Berthier's shrug.
* R2 (SRX-12) — a question that NAMES a law ("what does the Code Abroad
  do?") is answered with what the law does, not its price alone.
* R3 (SRX-13) — a refused law's line states its price once (it had said
  "3,000 gold, then 150 gold a turn — the Artillery Reserve costs 3,000
  gold; the treasury holds 800").
* R4 (SRX-14) — "how many diplomatic points do I have?" is the desk's:
  "diplomatic" holds "diplomat", one of the diplomat's address names, so the
  count opened Talleyrand's assessment (and, answered with its first options,
  a peace proposal). The answer reads the pool, its ceiling, the refill's
  split and the day's orders off the sources the top bar and the header
  print.
* R5 (SRX-15) — the soil alarm's clause names the corps that took the
  province by its printed name ("Archduke Charles's corps"), not its key.
* R6 (SRX-16) — the fortify refusal's long form names the foe as printed
  ("Enemy present: Archduke Charles, Archduke John"), like its short form.
* R7 (SRX-17) — the three instruments (guarantee, sponsor, buy off) refuse
  a court the board has eliminated, with the invest verb's own predicate and
  sentence, and charge nothing; a living court's guarantee names it as
  printed.
"""
import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.ai.first_contact as FC
import backend.ai.llm_client as LC
import backend.ai.question_desk as QD
import backend.main as M
from backend.game_logic import reforms as R
from tests import _chip_census as C


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield M.world
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _say(text):
    client = TestClient(M.app)
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _parse(text):
    with _quiet():
        return M.parser.parse(text, M.game_state)


# ═══════════════════════════ R1 — THE BARE WORD ═══════════════════════════════

class TestTheBareWordAsksForTheLaws:

    @pytest.mark.parametrize("text", ["laws", "the laws", "Laws", "our laws of state",
                                      "Berthier, laws", "reforms"])
    def test_the_bare_word_is_the_laws_answer(self, world, text):
        reply = _say(text)
        assert reply["success"] is True, reply["message"]
        assert reply["message"].startswith("The laws of state, Sire."), reply["message"]

    def test_a_law_order_is_still_an_order(self, world):
        world.nation_gold["France"] = 60000
        reply = _say("enact the Staff")
        assert "Enact it?" in reply["message"], reply["message"]

    def test_the_lever_down_is_the_old_shrug(self, world, monkeypatch):
        monkeypatch.setattr(LC, "THE_BARE_WORD_ASKS_FOR_THE_LAWS", False)
        reply = _say("laws")
        assert not reply["message"].startswith("The laws of state"), reply["message"]


# ═══════════════════════════ R2 + R3 — THE LAWS ANSWER ════════════════════════

class TestTheNamedLawSaysWhatItDoes:

    def test_what_does_the_code_abroad_do(self, world):
        says = R.find_law(world, "France", "code_abroad")["says"].strip()
        reply = _say("what does the Code Abroad do")
        assert says.rstrip(".") in reply["message"], reply["message"]

    def test_only_the_named_law_says(self, world):
        staff = R.find_law(world, "France", "grand_quartier_general")["says"].strip()
        code = R.find_law(world, "France", "code_abroad")["says"].strip()
        reply = _say("what does the Code Abroad do")
        assert staff.rstrip(".") not in reply["message"]
        assert code.rstrip(".") in reply["message"]

    def test_an_in_force_named_law_says_too(self, world):
        world.nation_gold["France"] = 60000
        R.enact_law(world, "France", R.find_law(world, "France", "code_abroad"))
        says = R.find_law(world, "France", "code_abroad")["says"].strip()
        reply = _say("what does the Code Abroad do")
        assert "is in force" in reply["message"] and says.rstrip(".") in reply["message"]

    def test_the_lever_down_prices_it_alone(self, world, monkeypatch):
        monkeypatch.setattr(FC, "THE_LAW_NAMED_SAYS_WHAT_IT_DOES", False)
        says = R.find_law(world, "France", "code_abroad")["says"].strip()
        assert says.rstrip(".") not in _say("what does the Code Abroad do")["message"]


class TestARefusedLawStatesItsPriceOnce:

    def test_the_price_is_said_once(self, world):
        world.nation_gold["France"] = 800
        text = FC._laws_answer("what laws are in force", world)
        start = text.index("The Artillery Reserve:")
        line = text[start:text.index(".", start)]
        assert line.count("3,000") == 1, line
        assert line.endswith("the treasury holds 800"), line

    def test_an_authority_price_keeps_its_unit(self, world):
        world.authority_tracker.authority = 5
        text = FC._laws_answer("what laws are in force", world)
        assert "the court holds 5 authority" in text, text

    def test_other_refusals_stay_whole(self, world):
        world.nation_gold["France"] = 60000
        world.admin_actions_remaining = 0
        text = FC._laws_answer("what laws are in force", world)
        assert "takes an admin action; none remains this turn" in text, text

    def test_the_lever_down_repeats_it(self, world, monkeypatch):
        monkeypatch.setattr(FC, "A_REFUSED_LAW_STATES_ITS_PRICE_ONCE", False)
        world.nation_gold["France"] = 800
        text = FC._laws_answer("what laws are in force", world)
        assert "the Artillery Reserve costs 3,000 gold" in text


# ═══════════════════════════ R4 — THE POINTS ══════════════════════════════════

class TestTheDeskCountsThePoints:

    @pytest.mark.parametrize("text", [
        "how many diplomatic points do I have", "how many diplomatic points do we have?",
        "Talleyrand, how many points do we have?", "how many actions do I have left",
        "how many orders do I have", "how many admin actions do I have left",
        "how many DP do I have"])
    def test_the_question_is_the_desks(self, world, text):
        result = _parse(text)
        command = result.get("command") or {}
        assert command.get("action") == "status", (text, command)
        assert (command.get("question") or {}).get("kind") == "points", (text, command)

    def test_the_answer_reads_the_pool_the_refill_and_the_orders(self, world):
        world._dp_refill = {"France": (5, 2)}
        world.diplomatic_points = 7
        reply = _say("how many diplomatic points do I have")
        text = reply["message"]
        assert reply["success"] is True and "An astute question" not in text, text
        assert "holds 7 diplomatic points of 7" in text, text
        assert "5 came with this morning's refill and 2 were carried from last turn" in text
        summary = world.get_action_summary()
        assert (f"Today {summary['actions_remaining']} of {summary['max_actions']} orders remain"
                in text), text
        assert world.pending_diplomatic_dialogue is None or not world.pending_diplomatic_dialogue

    def test_it_costs_nothing(self, world):
        before = (world.actions_remaining, world.admin_actions_remaining,
                  world.diplomatic_points)
        _say("how many diplomatic points do I have")
        assert (world.actions_remaining, world.admin_actions_remaining,
                world.diplomatic_points) == before

    def test_the_desks_own_classifier_knows_the_kind(self):
        """`classify_board_question` answers for every caller that asks the
        desk directly — not only the parser's early read."""
        assert QD.classify_board_question("how many actions do I have left") == {
            "kind": "points", "subject": "", "subject_type": "board"}
        assert QD.classify_board_question("how many men does Ney have") is None or \
            QD.classify_board_question("how many men does Ney have")["kind"] != "points"

    def test_a_diplomatic_order_still_reaches_talleyrand(self, world):
        command = _parse("Talleyrand, improve relations with Prussia").get("command") or {}
        assert command.get("action") != "status", command

    def test_the_lever_down_is_the_old_assessment(self, world, monkeypatch):
        monkeypatch.setattr(QD, "THE_DESK_COUNTS_THE_POINTS", False)
        command = _parse("how many diplomatic points do I have").get("command") or {}
        assert command.get("action") == "diplomatic_advisory", command


# ═══════════════════════════ R5 — THE OCCUPIER, AS PRINTED ═════════════════════

class TestTheFallenProvinceNamesItsOccupierAsPrinted:
    """SRX-15: the laws arm's turn-9 morning lead read "Sire — Rhineland has
    fallen. … ArchdukeCharles's corps of 19,418 stands there." The intel
    stores the marshal's KEY; the soil alarm's clause was the one name in the
    dispatch not passed through the humaniser, and the client translates
    nation keys only. FA-D8's own pin names Moore, whose key is his name."""

    EVT = {"type": "region_captured", "region": "Rhineland", "captured_by": "Austria",
           "previous_controller": "France", "nation": "Austria"}

    def _stage(self, world):
        region = world.get_region("Rhineland")
        region.controller = "Austria"
        world.marshals["ArchdukeCharles"].location = "Rhineland"
        eyes = next(n for n in region.adjacent_regions
                    if world.get_region(n).controller == "France")
        world.marshals["Ney"].location = eyes  # our own eyes, one march off
        with _quiet():
            world.calculate_visibility()
        intel = world.intel.get("Rhineland")
        assert intel is not None and any(
            km.get("name") == "ArchdukeCharles" for km in intel.known_marshals), \
            "the staging must put the Archduke in our intel of Rhineland"

    def test_the_clause_prints_the_name_not_the_key(self, world):
        from backend.game_logic import dispatch as D
        self._stage(world)
        text = D._home_captured_lever(world, "Rhineland", "France", dict(self.EVT))
        assert "Archduke Charles's corps of" in text and "stands there" in text, text
        assert "ArchdukeCharles" not in text, text

    def test_the_headline_reads_it_too(self, world):
        from backend.game_logic import dispatch as D
        self._stage(world)
        headline = D._HEADLINE_TEMPLATES["home_captured"].format(
            region="Rhineland",
            lever=D._home_captured_lever(world, "Rhineland", "France", dict(self.EVT)))
        assert "ArchdukeCharles" not in headline and "Archduke Charles's corps" in headline


# ═══════════════════════════ R6 — THE ENGAGED REFUSAL ═════════════════════════

class TestTheEngagedRefusalNamesTheFoe:
    """SRX-16: the AAR and Chunk 4 arms (turn 3): "Massena cannot fortify
    while engaged with enemy forces! Enemy present: ArchdukeCharles,
    ArchdukeJohn." — the long refusal read the roster keys while its own
    short form already printed the name."""

    def test_both_forms_print_the_names(self, world):
        from backend.commands.tactical_executor import fortify_refusal
        ney = world.marshals["Ney"]
        for key in ("ArchdukeCharles", "ArchdukeJohn"):
            world.marshals[key].location = ney.location
        long_form, short_form = fortify_refusal(world, ney)
        assert "Enemy present: Archduke Charles, Archduke John." in long_form, long_form
        assert "ArchdukeCharles" not in long_form and "ArchdukeJohn" not in long_form
        assert short_form.startswith("Archduke Charles stands here"), short_form

    def test_the_typed_road_reads_it(self, world):
        ney = world.marshals["Ney"]
        world.marshals["ArchdukeCharles"].location = ney.location
        reply = _say("Ney, fortify")
        assert "Enemy present: Archduke Charles" in reply["message"], reply["message"]

    def test_the_drill_refusal_names_a_foe_one_march_off(self, world):
        """The laws arm (turn 8): "Soult cannot drill with enemy forces
        nearby! ArchdukeCharles is at Rhineland, just one region away." """
        from backend.commands.tactical_executor import drill_refusal
        ney = world.marshals["Ney"]
        around = set(world.get_region(ney.location).adjacent_regions)
        for other in world.marshals.values():   # Mack stands at Swabia at boot
            if other.nation != "France" and other.location in around:
                other.location = "Vienna"
        near = world.get_region(ney.location).adjacent_regions[0]
        world.marshals["ArchdukeCharles"].location = near
        with _quiet():
            world.calculate_visibility()
        long_form, _short = drill_refusal(world, ney, stance_gate=False)
        assert f"Archduke Charles is at {near}, just one region away." in long_form, long_form
        assert "ArchdukeCharles" not in long_form

    def test_the_drill_refusal_names_a_foe_on_the_field(self, world):
        from backend.commands.tactical_executor import drill_refusal
        ney = world.marshals["Ney"]
        world.marshals["ArchdukeCharles"].location = ney.location
        long_form, _short = drill_refusal(world, ney, stance_gate=False)
        assert "(Archduke Charles) present at" in long_form, long_form
        assert "ArchdukeCharles" not in long_form


def _truce(world, court="Austria", elapsed=2):
    key = world._make_diplo_key("France", court)
    world.diplomatic_states[key] = "ARMISTICE"
    world.armistice_turns[key] = elapsed
    world.invalidate_bloc_members_cache()
    return key


class TestTheTruceRefusalsNameTheFoeAndReadTheClock:
    """SRX-16 widened: the AAR arm (turn 8) printed "Cannot attack
    ArchdukeCharles — armistice with Austria (4 turns remaining)". Its
    pursue-road sibling printed the key too, and — found in passing — still
    read the war-entry floor in `armistice_cooldowns` for its clock, where
    SR-3a (ii)'s CRT-7 rider had moved the attack road onto the truce's own
    (`ARMISTICE_DURATION - armistice_turns`)."""

    def test_the_attack_road_prints_the_names(self, world):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        _truce(world, elapsed=2)
        block = CommandExecutor()._make_diplomatic_error(
            world, "France", world.get_marshal("ArchdukeCharles"))
        assert block["message"] == (
            f"Cannot attack Archduke Charles — armistice with Austria "
            f"({ARMISTICE_DURATION - 2} turns remaining)."), block

    def test_the_pursue_road_prints_the_names_and_reads_the_truces_clock(self, world):
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        charles = world.marshals["ArchdukeCharles"]
        ney = world.marshals["Ney"]
        ney.location = next(n for n in world.get_region(charles.location).adjacent_regions)
        with _quiet():
            world.calculate_visibility()
        key = _truce(world, elapsed=2)
        world.armistice_cooldowns[key] = ARMISTICE_DURATION + 5  # the floor, not the clock
        reply = _say("Ney, pursue Archduke Charles")
        text = reply["message"]
        assert reply["success"] is False, text
        assert (f"Cannot pursue Archduke Charles — armistice with Austria "
                f"({ARMISTICE_DURATION - 2} turns remaining).") in text, text
        assert "ArchdukeCharles" not in text


# ═══════════════════════════ R7 — AN ELIMINATED COURT ═════════════════════════

class TestAnEliminatedCourtBindsNoInstrument:
    """SRX-17: the Chunk 4 arm's board (turn 13): "guarantee Kingdom of
    Italy" a turn after the kingdom was eliminated charged 1 DP and pledged
    to defend soil it no longer had, while "invest in" the same court was
    refused. The three instruments share one gate, and it now asks the
    invest verb's own predicate (GE-V)."""

    def _eliminate_italy(self, world):
        for region in [r for r in world.regions.values()
                       if r.controller == "KingdomOfItaly"]:
            region.controller = "Austria"
        with _quiet():
            world.invalidate_active_nations_cache()
            world._eliminate_nation("KingdomOfItaly", "Austria")
            world.invalidate_active_nations_cache()
        assert "KingdomOfItaly" not in world.get_active_nations()

    @pytest.mark.parametrize("text", [
        "guarantee Kingdom of Italy",
        "sponsor Kingdom of Italy against Austria, 200 gold",
        "buy off Kingdom of Italy"])
    def test_every_instrument_refuses_and_charges_nothing(self, world, text):
        self._eliminate_italy(world)
        dp, gold = world.diplomatic_points, world.nation_gold["France"]
        reply = _say(text)
        assert reply["success"] is False, reply["message"]
        assert "no longer exists as a court — it was eliminated. No instrument can bind it." \
            in reply["message"], reply["message"]
        assert (world.diplomatic_points, world.nation_gold["France"]) == (dp, gold)

    def test_invest_keeps_its_own_sentence(self, world):
        self._eliminate_italy(world)
        reply = _say("invest in Kingdom of Italy")
        assert "it was eliminated. Nothing can be invested in it." in reply["message"]

    def test_a_living_court_is_still_guaranteed_by_its_printed_name(self, world):
        dp = world.diplomatic_points
        reply = _say("guarantee Papal States")
        assert reply["success"] is True, reply["message"]
        assert reply["message"].startswith("France guarantees Papal States."), reply["message"]
        assert "PapalStates" not in reply["message"]
        assert world.diplomatic_points == dp - 1
