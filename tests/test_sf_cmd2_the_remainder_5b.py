"""SF-CMD-2's remainder, part b — Score Finish Step 7 slice 5b
(SCORE_FINISH_SPEC.md §3 Step 7; rules SYSTEMS_REFERENCE.md §93.7; rows
BUG_FIXES.md RS-12, RS-15, CX3-X2, CX3-X3, PC15-13, SF-V9, SF7-X9, SF7-X10,
SF7-X11; CX-BEHAV-1's census is re-keyed in tests/test_cx3_the_predictor.py).

Every pin drives the real `POST /command` on a fresh SHIPPED 1805 boot (Ney
and Davout at Rhineland, Soult and the Emperor at Lorraine, Lannes and Murat
at Franche-Comte, Massena at Milan, Mack at Swabia). Reproduced at HEAD
before a line was written:

  * Davout fortified: "what if Davout attacks Mack?" weighed a favorable
    muster; the order is refused ("fortified … unfortify first").
  * Every corps on ground that builds nothing: "what can I do" offered only
    "end turn" while 48 builds were legal elsewhere.
  * "march to Ulm" asked "Which marshal shall march to Ulm, Sire?" — eight
    choices, every one refused ("Region 'Ulm' not found.").
  * "Ney, march to Austerlitz" → "Did you mean 'Ulster'?"; Thuringia →
    Lithuania, Wagram → Karaman, Marengo → Aragon, Lombardy → Normandy.
  * "Ney, march to Alsace" → "Nearby: Wales, Andalusia, Balearics".
  * "Ney, scout Alsace" scouted every neighbour for an action (SF7-X9).
  * "Ney, fall back while Mack advances" retreated and then answered "Mack
    cannot be reached, Sire — no such province" (SF7-X10).
  * "Davout, recruit infantry in Rhineland" with Davout at Lorraine raised
    3,000 men at Lorraine for 741 gold (SF7-X11).
  * The HOLD arm (SF-V9): "We're short of guns - raise some artillery at
    Paris." → "There is no 'We're' in the order of battle"; "murat needs
    more horse, get me some cavalry in franche-comte" → the shrug; "Get a
    fort built at Milan in case the Archduke comes down out of Tyrol." → "a
    contingency, not an order".
"""

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.counsel as CO
import backend.ai.llm_client as LC
import backend.ai.question_desk as QD
import backend.commands.clarification as CL
import backend.commands.economy_executor as EE
import backend.commands.executor as EX
import backend.commands.parser as PR
import backend.commands.strategic_executor as SE
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def text_of(response):
    return str(response.get("message") or response.get("error") or "")


def footprint(world):
    return (int(world.actions_remaining),
            int(getattr(world, "admin_actions_remaining", 0) or 0),
            int(world.gold),
            {m.name: (m.location, int(m.strength)) for m in world.get_player_marshals()})


# ═══════════════════════════════════════════════════════════════════════════
# RS-12 — the what-if reads the order's state first
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWhatIfReadsTheState:

    def test_a_fortified_corps_is_refused_not_weighed(self, shipped):
        client, world = shipped
        world.get_marshal("Davout").fortified = True
        message = text_of(post(client, "what if Davout attacks Mack?"))
        assert message == ("The order would be refused, Sire: Davout is fortified "
                           "— unfortify first. Nothing spent."), message
        assert "MUSTER" not in message

    def test_a_drill_lock_and_a_spent_turn_are_said(self, shipped):
        client, world = shipped
        davout = world.get_marshal("Davout")
        davout.drilling_locked = True
        davout.drill_complete_turn = 3
        assert "locked in drill until turn 3" in text_of(
            post(client, "what if Davout attacks Mack?"))
        davout.drilling_locked = False
        world.actions_remaining = 0
        assert "no military action left this turn — nothing spent" in text_of(
            post(client, "what if Davout attacks Mack?"))

    def test_a_free_corps_is_still_weighed(self, shipped):
        client, _world = shipped
        assert "MUSTER" in text_of(post(client, "what if Davout attacks Mack?"))

    def test_it_spends_nothing(self, shipped):
        client, world = shipped
        world.get_marshal("Davout").fortified = True
        before = footprint(world)
        post(client, "what if Davout attacks Mack?")
        assert footprint(world) == before

    def test_the_lever_down_weighs_the_muster(self, shipped, monkeypatch):
        client, world = shipped
        world.get_marshal("Davout").fortified = True
        monkeypatch.setattr(QD, "THE_WHAT_IF_READS_THE_ORDERS_STATE", False)
        assert "MUSTER" in text_of(post(client, "what if Davout attacks Mack?"))


# ═══════════════════════════════════════════════════════════════════════════
# RS-15 — the counsel's build line finds ground that takes a building
# ═══════════════════════════════════════════════════════════════════════════

def _every_corps_on_ground_that_builds_nothing(world):
    for m in world.get_player_marshals():
        region = world.get_region(m.location)
        if region is not None and region.controller == world.player_nation:
            region.stability = 40
    world.actions_remaining = 0


class TestTheCounselFindsGround:

    def test_a_build_is_offered_elsewhere(self, shipped):
        client, world = shipped
        _every_corps_on_ground_that_builds_nothing(world)
        message = text_of(post(client, "what can I do"))
        assert "build supply depot in Paris — 300g" in message, message

    def test_every_offered_build_is_one_the_executor_takes(self, shipped):
        _client, world = shipped
        _every_corps_on_ground_that_builds_nothing(world)
        lines = CO._build_terms(world, world.player_nation, limit=2)
        assert lines
        for line in lines:
            order = line.split(" — ")[0]
            M._reset_world_state()
            M.parser = CommandParser(use_real_llm=False)
            _every_corps_on_ground_that_builds_nothing(M.world)
            client = TestClient(M.app)
            reply = post(client, order)
            assert reply.get("success"), (order, text_of(reply))

    def test_the_lever_down_goes_silent_again(self, shipped, monkeypatch):
        _client, world = shipped
        _every_corps_on_ground_that_builds_nothing(world)
        monkeypatch.setattr(CO, "THE_BUILD_LINE_FINDS_GROUND_THAT_TAKES_IT", False)
        assert CO._build_terms(world, world.player_nation, limit=2) == []


# ═══════════════════════════════════════════════════════════════════════════
# CX3-X2 — no "Which marshal?" about a place the map lacks
# ═══════════════════════════════════════════════════════════════════════════

class TestNoQuestionForAPlaceTheMapLacks:

    @pytest.mark.parametrize("line,expect", [
        ("march to Ulm", "Region 'Ulm' not found."),
        ("march to Jena", "Region 'Jena' not found."),
        ("move to Austerlitz", "Region 'Austerlitz' not found."),
        ("hold Ulm", "Region 'Ulm' not found."),
    ])
    def test_the_refusal_answers_free_with_no_question(self, shipped, line, expect):
        client, world = shipped
        before = footprint(world)
        reply = post(client, line)
        assert text_of(reply) == expect, text_of(reply)
        assert "Which marshal" not in text_of(reply)
        # no question staged: nothing waits for an answer
        assert reply.get("state") != "awaiting_clarification", reply.get("state")
        assert not reply.get("clarification_registered")
        assert footprint(world) == before

    def test_a_place_the_map_has_still_asks(self, shipped):
        client, _world = shipped
        reply = post(client, "march to Swabia")
        assert "Which marshal shall march to Swabia" in text_of(reply)
        assert reply.get("state") == "awaiting_clarification", reply.get("state")

    def test_a_typo_the_map_reads_still_asks(self, shipped):
        client, _world = shipped
        assert "Which marshal" in text_of(post(client, "march to Swabbia"))

    def test_a_raw_typo_a_live_reading_hands_over_is_not_refused(self, shipped):
        """The mock parser corrects "Swabbia" before the clarification sees
        it; a live reading may hand the raw typo over — the matcher reads it,
        so the question still stands (the slice's sweep found the endpoint pin
        could not reach this branch)."""
        parsed = {"success": True,
                  "command": {"action": "move", "target": "Swabbia"}}
        assert CL.destination_refusal(M.world, parsed, M.executor) is None
        parsed["command"]["target"] = "Ulm"
        assert CL.destination_refusal(M.world, parsed, M.executor) == "Region 'Ulm' not found."

    def test_the_lever_down_asks_regardless(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(CL, "A_QUESTION_NAMES_A_PLACE_THAT_EXISTS", False)
        assert "Which marshal shall march to Ulm" in text_of(post(client, "march to Ulm"))


# ═══════════════════════════════════════════════════════════════════════════
# CX3-X3 + PC15-13 — a printed guess keeps the first letter; the roads
# ═══════════════════════════════════════════════════════════════════════════

ACROSS_EUROPE = ["Austerlitz", "Thuringia", "Wagram", "Marengo", "Lombardy"]
RHINELAND_ROADS = "From Rhineland the roads lead to: Swabia, Lorraine, Frankfurt, Gelderland."


class TestAPrintedGuessKeepsTheFirstLetter:

    @pytest.mark.parametrize("place", ACROSS_EUROPE)
    @pytest.mark.parametrize("verb", ["march to", "move to"])
    def test_no_guess_across_europe_the_roads_instead(self, shipped, place, verb):
        client, _world = shipped
        message = text_of(post(client, f"Ney, {verb} {place}"))
        assert message == f"Region '{place}' not found. {RHINELAND_ROADS}", message

    def test_a_real_typo_still_asks(self, shipped):
        client, _world = shipped
        assert "Did you mean 'Vienna'?" in text_of(post(client, "Ney, march to Venetia"))

    @pytest.mark.parametrize("typo,place", [
        ("Swabbia", "Swabia"), ("Silezia", "Silesia"), ("Tirol", "Tyrol")])
    def test_a_close_typo_still_auto_corrects(self, typo, place, shipped):
        region, err = EX.CommandExecutor()._fuzzy_match_region(typo, M.world)
        assert err is None and region.name == place

    def test_a_low_confidence_typo_keeps_its_guess(self, shipped):
        client, _world = shipped
        assert "Did you mean 'Bordelais'?" in text_of(
            post(client, "Davout, march to Bordeuex"))

    def test_with_no_corps_to_read_from_the_refusal_alone(self, shipped):
        region, err = EX.CommandExecutor()._fuzzy_match_region("Alsace", M.world)
        assert region is None and err["message"] == "Region 'Alsace' not found."

    def test_the_march_road_reads_the_roads_pc15_13(self, shipped):
        client, _world = shipped
        assert text_of(post(client, "Ney, march to Alsace")) == (
            f"Region 'Alsace' not found. {RHINELAND_ROADS}")

    def test_a_demoted_guess_on_the_march_road_names_the_roads(self, shipped):
        """Jena auto-corrects to Vienna (75, a different first letter): the
        march road swallows that error class (CA8-28) and its own fallback
        now gives the roads for a single unknown name — never "I could not
        make out a destination"."""
        client, _world = shipped
        message = text_of(post(client, "Ney, march to Jena"))
        assert message == f"Region 'Jena' not found. {RHINELAND_ROADS}", message

    def test_the_terrain_noun_keeps_its_copy(self, shipped):
        client, _world = shipped
        assert "The map knows no pass by that name" in text_of(
            post(client, "Ney, hold the pass"))

    def test_the_levers_down(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(EX, "A_PRINTED_GUESS_KEEPS_THE_FIRST_LETTER", False)
        assert "Did you mean 'Ulster'?" in text_of(post(client, "Ney, march to Austerlitz"))
        monkeypatch.setattr(SE, "THE_MARCH_ROAD_READS_ITS_ROADS", False)
        assert "Nearby: Wales" in text_of(post(client, "Ney, march to Alsace"))


# ═══════════════════════════════════════════════════════════════════════════
# SF7-X9 — the scout keeps its place; SF7-X10 — a condition's foe is no
# target; SF7-X11 — a named levy ground is honoured
# ═══════════════════════════════════════════════════════════════════════════

class TestTheScoutKeepsItsPlace:

    def test_an_unknown_place_is_refused_free(self, shipped):
        client, world = shipped
        before = footprint(world)
        message = text_of(post(client, "Ney, scout Alsace"))
        assert message == f"Region 'Alsace' not found. {RHINELAND_ROADS}", message
        assert footprint(world) == before

    @pytest.mark.parametrize("line", ["Ney, scout the area", "Ney, scout ahead",
                                      "Ney, scout for the enemy"])
    def test_a_generic_object_keeps_the_bare_scout(self, shipped, line):
        client, world = shipped
        message = text_of(post(client, line))
        assert "Ney scouts from Rhineland" in message, message

    def test_a_known_place_is_scouted(self, shipped):
        client, _world = shipped
        assert "Ney scouts Swabia" in text_of(post(client, "Ney, scout Swabia"))

    def test_the_lever_down_runs_the_bare_scout(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(LC, "A_SCOUTED_PLACE_IS_KEPT", False)
        assert "Ney scouts from Rhineland" in text_of(post(client, "Ney, scout Alsace"))


class TestAConditionsFoeIsNoTarget:

    @pytest.fixture(autouse=True)
    def _no_mood_roll(self, monkeypatch):
        # Ney "bristles at the retreat order but obeys"; the objection's mood
        # roll can promote that to a refusal — pinned (objection-pin rule).
        monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                            lambda concern: concern)

    @pytest.mark.parametrize("line", [
        "Ney, fall back while Mack advances",
        "Ney, fall back before Mack arrives",
        "Ney, fall back in case Mack advances",
    ])
    def test_the_retreat_names_no_foe_as_its_ground(self, shipped, line):
        client, world = shipped
        message = text_of(post(client, line))
        assert world.get_marshal("Ney").in_retreat_recovery(), message
        assert "cannot be reached" not in message, message

    def test_the_lever_down_binds_the_foe_again(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(PR, "A_BLANKED_CLAUSE_NAMES_NO_TARGET", False)
        assert "Mack cannot be reached" in text_of(
            post(client, "Ney, fall back while Mack advances"))


class TestTheLevyGroundIsHonoured:

    def test_a_different_province_is_refused_free(self, shipped):
        client, world = shipped
        world.get_marshal("Davout").location = "Lorraine"
        before = footprint(world)
        message = text_of(post(client, "Davout, recruit infantry in Rhineland"))
        assert message.startswith("Davout stands at Lorraine, Sire — a corps raises "
                                  "its levy where it stands, not at Rhineland."), message
        assert "'recruit in Rhineland'" in message
        assert footprint(world) == before

    @pytest.mark.parametrize("line", ["Davout, recruit infantry in Lorraine",
                                      "Davout, recruit infantry"])
    def test_his_own_province_still_levies(self, shipped, line):
        client, world = shipped
        world.get_marshal("Davout").location = "Lorraine"
        assert "Davout recruits" in text_of(post(client, line))

    def test_the_lever_down_levies_at_his_province(self, shipped, monkeypatch):
        client, world = shipped
        world.get_marshal("Davout").location = "Lorraine"
        monkeypatch.setattr(EE, "A_NAMED_LEVY_GROUND_IS_HONOURED", False)
        assert "Davout recruits 3,000 infantry at Lorraine" in text_of(
            post(client, "Davout, recruit infantry in Rhineland"))


# ═══════════════════════════════════════════════════════════════════════════
# SF-V9 — the HOLD arm's blind sentences that still missed
# ═══════════════════════════════════════════════════════════════════════════

class TestTheHoldArmsWorklist:

    def test_a_contraction_is_never_a_name(self, shipped):
        client, _world = shipped
        message = text_of(post(client, "We're short of guns - raise some artillery at Paris."))
        assert "There is no 'We're'" not in message, message
        assert "No marshal of artillery can reach Paris" in message, message
        assert CG.never_an_address("we're") and CG.never_an_address("it’s")

    def test_get_me_some_cavalry_is_the_levy(self, shipped):
        client, _world = shipped
        message = text_of(post(client, "murat needs more horse, get me some cavalry in franche-comte"))
        assert "Murat's cavalry levy" in message, message
        assert "get me a report" and LC._GET_ME_TROOPS_RE.search("get me some guns")
        assert not LC._GET_ME_TROOPS_RE.search("get me a report on swabia")

    def test_a_trailing_in_case_is_a_precaution(self, shipped):
        client, world = shipped
        message = text_of(post(client, "Davout, build a supply depot at Rhineland in case Mack comes"))
        assert "Construction started: Supply Depot in Rhineland" in message, message

    def test_a_leading_in_case_is_still_a_contingency(self, shipped):
        client, _world = shipped
        assert "that is a contingency, not an order" in text_of(
            post(client, "In case Mack comes, fall back"))

    def test_the_passive_build_is_the_build(self, shipped):
        client, _world = shipped
        assert "Construction started: Fortification in Rhineland" in text_of(
            post(client, "Davout, get a fort built at Rhineland"))
        # the blind line itself: read right, refused by the board (Milan is
        # the Kingdom of Italy's)
        assert "Cannot build in Milan" in text_of(post(
            client, "Get a fort built at Milan in case the Archduke comes down out of Tyrol."))

    def test_the_levers_down(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(CG, "A_CONTRACTION_IS_NEVER_A_NAME", False)
        assert "There is no 'We're'" in text_of(
            post(client, "We're short of guns - raise some artillery at Paris."))
        monkeypatch.setattr(CG, "AN_IN_CASE_IS_A_PRECAUTION", False)
        assert "contingency" in text_of(
            post(client, "Davout, build a supply depot at Rhineland in case Mack comes"))
        monkeypatch.setattr(LC, "A_GET_ME_TROOPS_IS_A_LEVY", False)
        assert "Murat's cavalry levy" not in text_of(post(client, "Murat, get me some cavalry"))
        monkeypatch.setattr(LC, "A_WORK_GOT_BUILT_IS_BUILT", False)
        assert "Construction started" not in text_of(
            post(client, "Davout, get a fort built at Rhineland"))
