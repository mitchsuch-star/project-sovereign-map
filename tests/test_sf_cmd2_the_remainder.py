"""SF-CMD-2 "the census's remainder" — Score Finish Step 7 slice 5a
(SCORE_FINISH_SPEC.md §3 Step 7; rules SYSTEMS_REFERENCE.md §93.6; rows
BUG_FIXES.md CX5-L5-F3 / F4 / F5 / N4 / N5, NP-X8 / X9 / X10, NPC-10 /
NPC-18 / NPC-26). The second name (CQ-8 / CQ-38) is pinned beside CRT-11's
role half in tests/test_crt11_the_second_name_is_heard.py; F6 (the CX-5
class's own pins) in tests/test_cx1_a_question_never_orders.py.

Every pin drives the real `POST /command` on a fresh SHIPPED 1805 boot
(Ney and Davout at Rhineland, Soult and the Emperor at Lorraine, Lannes and
Murat at Franche-Comte, Mack at Swabia) unless it names a code-level
completion. Reproduced at HEAD `c5ef3a60` before a line was written:

  * "Lannes, carry out the retreat" / "keep retreating" -> the shrug.
  * the addressed shrug of a line about somebody else's retreat offered
    scout / defend, never the retreat, never why.
  * "Lannes, pursue Mack's retreat" -> "Cannot find 'Mack'S Retreat' to
    pursue."
  * "Lannes, smash the retreating column" fought, then said "Name another
    and he will turn."
  * "Ney moves to Lorraine", "Napoleon moves to Rhineland", "the Emperor
    moves to Rhineland" -> each shrugged.
  * "I will hold talks with Prussia myself" -> "Region 'Talks' not found.
    Did you mean 'Wales'?"
  * "Ney, support the Emperor" -> "Cannot find marshal 'Emperor' to support.
    Available French marshals: … Napoleon".
  * "Murat, ride down the Austrians at Swabia" -> the shrug; with no Austrian
    at Swabia, "attack the Austrians at Swabia" -> "Murat cannot attack
    Bavaria — they are our ally" (the word Austria nowhere).
"""

import inspect

import pytest
from fastapi.testclient import TestClient

import backend.ai.attack_vocabulary as AV
import backend.ai.llm_client as LC
import backend.ai.strategic_parser as SP
import backend.commands.combat_executor as CE
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


def parse(text):
    return M.parser.parse(text, M.get_llm_game_state(), world=M.world)


def verb(text):
    r = parse(text)
    return ((r.get("command") or {}).get("action") or r.get("action")
            or r.get("partial_action"))


# ═══════════════════════════════════════════════════════════════════════════
# CX5-L5-F3 / F4 — the retreat carried out, and the retreat continued
# ═══════════════════════════════════════════════════════════════════════════

CARRIED_OUT = [
    "Lannes, carry out the retreat",
    "Lannes, conduct the retreat",
    "Lannes, beat a retreat",
    "Lannes, perform a retreat",
    "Lannes, effect the withdrawal",
    "Lannes, undertake the retreat",
]
# The continued retreat: the "…retreating" forms were caught by the
# participle rule meant for "the retreating Austrians", and the continued
# "falling / pulling back" forms by nothing (the plain-retreat rule reads only
# the bare "fall back") — the lever holds both.
CONTINUED = [
    "Lannes, keep retreating",
    "Lannes, go on retreating",
    "Lannes, resume retreating",
    "Lannes, keep on retreating",
    "Lannes, keep falling back",
    "Lannes, carry on falling back",
    "Lannes, keep pulling back",
    "Lannes, keep on falling back",
]
# Measured with the lever down: these were ALREADY his own retreat (the
# withdraw keyword reads them) — pinned, never claimed for the lever.
CONTINUED_PLAIN = [
    "Lannes, keep withdrawing",
    "Lannes, continue withdrawing",
]


class TestTheRetreatIsCarriedOut:

    @pytest.fixture(autouse=True)
    def _no_mood_roll(self, monkeypatch):
        # An aggressive Lannes "bristles at the retreat order but obeys"; the
        # objection's mood roll promotes that to a refusal one time in ten
        # (CX-7's note) — pinned, the project's rule for objection pins.
        monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                            lambda concern: concern)

    @pytest.mark.parametrize("line", CARRIED_OUT + CONTINUED + CONTINUED_PLAIN)
    def test_the_line_is_his_own_retreat(self, shipped, line):
        """Read on the MARSHAL, not the message: the retreat shrug itself
        names the retreat, so a message assertion passes on a shrug (the
        slice's own sweep caught exactly that). A retreat is free and puts
        him in retreat recovery."""
        client, world = shipped
        response = post(client, line)
        message = text_of(response)
        assert world.get_marshal("Lannes").in_retreat_recovery(), (line, message[:200])
        assert "I read the retreat in your words" not in message, line
        assert world.actions_remaining == 4, line

    @pytest.mark.parametrize("line", CARRIED_OUT + CONTINUED)
    def test_the_lever_down_shrugs_again(self, shipped, monkeypatch, line):
        assert verb(line) == "retreat", line
        monkeypatch.setattr(LC, "THE_RETREAT_IS_CARRIED_OUT", False)
        assert verb(line) != "retreat", line

    @pytest.mark.parametrize("line", CONTINUED_PLAIN)
    def test_the_plain_continued_forms_were_never_the_levers(self, shipped,
                                                            monkeypatch, line):
        monkeypatch.setattr(LC, "THE_RETREAT_IS_CARRIED_OUT", False)
        assert verb(line) == "retreat", line

    def test_somebody_elses_retreat_continued_is_still_somebody_elses(self, shipped):
        """The participle rule is untouched: "the retreating Austrians" and
        "their continued retreat" are not his."""
        assert LC._retreat_is_carried_on("keep retreating")
        assert not LC._retreat_is_carried_on("press the retreating austrians")
        assert LC._retreat_is_a_noun("block their continued retreat")


# ═══════════════════════════════════════════════════════════════════════════
# CX5-L5-F5 — the shrug offers the retreat and says why
# ═══════════════════════════════════════════════════════════════════════════

class TestTheShrugOffersTheRetreat:

    def test_the_shrug_names_the_reading_and_both_orders(self, shipped):
        client, world = shipped
        message = text_of(post(client, "Lannes, cut down the retreat"))
        assert "I read the retreat in your words as the enemy's" in message
        assert "'Lannes, retreat'" in message
        assert "'Lannes, attack Mack'" in message
        assert world.actions_remaining == 4

    def test_the_foe_it_offers_is_one_we_are_at_war_with_and_can_see(self, shipped):
        client, world = shipped
        from backend.models.intel import FULL, PARTIAL
        message = text_of(post(client, "Lannes, press the retreat"))
        offered = message.split("'Lannes, attack ")[1].split("'")[0]
        foe = world.get_marshal(offered)
        assert foe is not None and world.is_at_war("France", foe.nation)
        assert world.get_region_intel(foe.location).visibility in (FULL, PARTIAL)

    def test_the_lever_down_restores_the_old_templates(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(LC, "THE_SHRUG_OFFERS_THE_RETREAT", False)
        message = text_of(post(client, "Lannes, cut down the retreat"))
        assert "I read the retreat in your words" not in message

    def test_a_shrug_with_no_retreat_word_is_untouched(self, shipped):
        client, _world = shipped
        message = text_of(post(client, "Lannes, flibber the gizzard"))
        assert "I read the retreat in your words" not in message


# ═══════════════════════════════════════════════════════════════════════════
# CX5-L5-N4 — the pursuit names the man
# ═══════════════════════════════════════════════════════════════════════════

class TestThePursuitNamesTheMan:

    @pytest.mark.parametrize("line", [
        "Lannes, pursue Mack's retreat",
        "Lannes, pursue Mack's column",
        "Lannes, pursue Mack's army",
    ])
    def test_the_quarry_is_mack(self, shipped, line):
        client, world = shipped
        response = post(client, line)
        message = text_of(response)
        assert "Cannot find" not in message, message[:200]
        assert "pursues Mack" in message or "Mack" in message, message[:200]
        assert world.actions_remaining < 4, line

    def test_the_possessive_helper(self):
        assert SP._possessive_quarry("mack's retreat") == "mack"
        assert SP._possessive_quarry("mack’s retreating column") == "mack"
        assert SP._possessive_quarry("mack") == "mack"
        assert SP._possessive_quarry("the retreating enemy") == "the retreating enemy"

    def test_the_lever_down_loses_the_man(self, shipped, monkeypatch):
        monkeypatch.setattr(SP, "A_PURSUIT_NAMES_THE_MAN", False)
        assert SP._possessive_quarry("mack's retreat") == "mack's retreat"


# ═══════════════════════════════════════════════════════════════════════════
# CX5-L5-N5 — the disclosure keeps its tense
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDisclosureKeepsItsTense:

    def test_the_branch_that_fought_says_he_engaged(self, shipped):
        client, _world = shipped
        response = post(client, "Lannes, smash the retreating column")
        message = text_of(response)
        assert response.get("battle_report") or "Casualties" in message, message[:200]
        assert "Lannes engaged Mack at Swabia, the nearest in sight" in message
        assert "he will turn" not in message

    def test_the_lever_down_keeps_the_future_tense(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(EX, "THE_DISCLOSURE_KEEPS_ITS_TENSE", False)
        message = text_of(post(client, "Lannes, smash the retreating column"))
        assert "Name another and he will turn" in message


# ═══════════════════════════════════════════════════════════════════════════
# NP-X9 — the inflected order is the order (every marshal, not only the
# Emperor); NP-X10 — the dead fallback is gone; NP-X8 — the anchor guard
# ═══════════════════════════════════════════════════════════════════════════

class TestTheInflectedOrder:

    @pytest.mark.parametrize("line,who,where", [
        ("Ney moves to Lorraine", "Ney", "Lorraine"),
        ("Napoleon moves to Rhineland", "Napoleon", "Rhineland"),
        ("the Emperor moves to Rhineland", "Napoleon", "Rhineland"),
        ("Ney marches to Lorraine", "Ney", "Lorraine"),
    ])
    def test_the_marshal_moves(self, shipped, line, who, where):
        client, world = shipped
        post(client, line)
        assert world.get_marshal(who).location == where, line

    def test_every_inflected_order_verb_parses_for_every_marshal(self, shipped):
        """NP-X9's completion: the standing verb guard iterates INFLECTIONS
        (it iterated bare stems only; "moves" was dead for every marshal)."""
        dead = []
        for v in PR._SOVEREIGN_ORDER_VERBS.split("|"):
            inflected = ("fortifies" if v == "fortify"
                         else v + "es" if v.endswith(("ch", "sh", "s", "x"))
                         else v + "s")
            for head in ("Napoleon", "the Emperor", "Ney"):
                if verb(f"{head} {inflected} Belgium") in (None, "unknown"):
                    dead.append(f"{head} {inflected}")
        assert not dead, dead

    @pytest.mark.parametrize("line", [
        "Mack moves to Swabia",           # an enemy at the head is narration
        "Ney moves to Lorraine?",         # a question is the question guard's
    ])
    def test_narration_and_questions_are_not_restated(self, shipped, line):
        client, world = shipped
        post(client, line)
        assert world.get_marshal("Ney").location == "Rhineland"
        assert world.actions_remaining == 4

    def test_the_rewrite(self):
        gs = M.get_llm_game_state()
        assert PR.rewrite_inflected_order("Ney moves to Lorraine", gs) == \
            "Ney, move to Lorraine"
        assert PR.rewrite_inflected_order("Soult fortifies", gs) == "Soult, fortify"
        assert PR.rewrite_inflected_order(
            "the Emperor marches to Swabia", gs, "Napoleon") == \
            "the Emperor, march to Swabia"
        assert PR.rewrite_inflected_order("Mack moves to Swabia", gs) == \
            "Mack moves to Swabia"

    def test_the_lever_down_shrugs_again(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(PR, "THE_ORDER_VERB_LOSES_ITS_INFLECTION", False)
        post(client, "Ney moves to Lorraine")
        assert world.get_marshal("Ney").location == "Rhineland"

    def test_np_x10_the_dead_fallback_is_deleted(self, shipped):
        params = inspect.signature(PR._find_player_sovereign).parameters
        assert list(params) == ["world"]
        assert PR._find_player_sovereign(None) is None
        assert PR._find_player_sovereign(M.world) == "Napoleon"

    def test_np_x8_every_first_person_anchor_reaches_the_sovereign(self, shipped):
        """NP-X8's completion: the anchor-set iteration guard (the verb guard's
        mirror). Every anchor's "<marshal>, <anchor> me" is SUPPORT of the
        Emperor at `POST /command` — none resolves a reference the parser
        cannot act on."""
        from backend.commands.context_carryover import _FIRST_PERSON_SUPPORT_ANCHORS
        dead = []
        for anchor in sorted(_FIRST_PERSON_SUPPORT_ANCHORS):
            M._reset_world_state()
            M.parser = CommandParser(use_real_llm=False)
            client = TestClient(M.app)
            post(client, f"Ney, {anchor} me")
            order = M.world.get_marshal("Ney").strategic_order
            if not order or (order.command_type, order.target) != ("SUPPORT", "Napoleon"):
                dead.append(anchor)
        assert not dead, dead


# ═══════════════════════════════════════════════════════════════════════════
# NPC-10 — talks are not a hold
# ═══════════════════════════════════════════════════════════════════════════

class TestTalksAreNotAHold:

    @pytest.mark.parametrize("line", [
        "I will hold talks with Prussia myself",
        "hold talks with Prussia",
        "hold a conference with Prussia",
        "Talleyrand, hold negotiations with Prussia",
    ])
    def test_it_is_diplomacy_never_a_hold_on_a_province(self, shipped, line):
        client, world = shipped
        message = text_of(post(client, line))
        assert "Talks" not in message and "Wales" not in message, message[:200]
        assert "Which marshal" not in message, message[:200]
        assert "Prussia" in message, message[:200]
        assert world.actions_remaining == 4
        assert all(getattr(m, "strategic_order", None) is None
                   for m in world.get_player_marshals())

    def test_a_real_hold_still_holds(self, shipped):
        client, world = shipped
        post(client, "Ney, hold Rhineland")
        order = world.get_marshal("Ney").strategic_order
        assert order is not None and order.command_type == "HOLD"

    def test_the_lever_down_restores_the_misreading(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(PR, "TALKS_ARE_NOT_A_HOLD", False)
        message = text_of(post(client, "I will hold talks with Prussia myself"))
        assert "Talks" in message


# ═══════════════════════════════════════════════════════════════════════════
# NPC-18 — "the Emperor" is a referent
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEmperorIsAReferent:

    @pytest.mark.parametrize("line", [
        "Ney, support the Emperor",
        "Ney, support his Majesty",
    ])
    def test_ney_supports_the_sovereign(self, shipped, line):
        client, world = shipped
        post(client, line)
        order = world.get_marshal("Ney").strategic_order
        assert order is not None
        assert (order.command_type, order.target) == ("SUPPORT", "Napoleon")

    def test_the_refusal_lists_him_by_his_title(self, shipped):
        client, _world = shipped
        response = post(client, "Ney, support Zorg")
        listed = str(response.get("suggestion") or text_of(response))
        assert "the Emperor" in listed
        assert "Napoleon" not in listed.split("Available French marshals:")[-1]

    def test_the_lever_down_restores_the_refusal(self, shipped, monkeypatch):
        client, _world = shipped
        monkeypatch.setattr(SE, "THE_EMPEROR_IS_A_REFERENT", False)
        message = text_of(post(client, "Ney, support the Emperor"))
        assert "Cannot find marshal" in message


# ═══════════════════════════════════════════════════════════════════════════
# NPC-26 — "ride down" a foe, and a named court is answered about itself
# ═══════════════════════════════════════════════════════════════════════════

def _mack_away(world):
    world.get_marshal("Mack").location = "Bohemia"


class TestTheNamedCourtIsAnswered:

    @pytest.mark.parametrize("line", [
        "Murat, ride down the Austrians at Swabia",
        "Murat, ride down Mack",
    ])
    def test_riding_down_a_foe_is_the_attack(self, shipped, line):
        client, world = shipped
        message = text_of(post(client, line))
        assert "MUSTER" in message or "Casualties" in message, message[:200]
        assert world.actions_remaining == 3

    @pytest.mark.parametrize("line", [
        "Murat, ride down to Swabia",       # a road, not a foe
        "Lannes, ride down the retreat",    # somebody's retreat (CX-5's)
    ])
    def test_riding_down_a_road_or_a_retreat_is_not(self, shipped, line):
        assert verb(line) != "attack", line

    @pytest.mark.parametrize("line", [
        "Murat, ride down the Austrians at Swabia",
        "Murat, attack the Austrians at Swabia",
    ])
    def test_no_named_court_at_the_province_is_said_of_that_court(self, shipped, line):
        client, world = shipped
        _mack_away(world)
        response = post(client, line)
        message = text_of(response)
        assert "No Austrian force is in sight at Swabia" in message, message[:240]
        assert "Swabia is Bavaria's soil" in message, message[:240]
        assert "The nearest Austrian force in sight is" in message, message[:240]
        assert world.actions_remaining == 4
        # the endpoint folds the suggestion into the message: the order that
        # reaches the nearest of the court the player named, in sight
        assert "Order 'Murat, attack " in message, message[:300]

    def test_the_holder_named_keeps_its_own_refusal(self, shipped):
        client, world = shipped
        _mack_away(world)
        message = text_of(post(client, "Murat, attack the Bavarians at Swabia"))
        assert "cannot attack Bavaria" in message, message[:200]

    def test_the_levers_down(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(AV, "A_FOE_IS_RIDDEN_DOWN", False)
        assert verb("Murat, ride down Mack") != "attack"
        monkeypatch.setattr(AV, "A_FOE_IS_RIDDEN_DOWN", True)
        monkeypatch.setattr(CE, "A_NAMED_NATION_IS_ANSWERED", False)
        _mack_away(world)
        message = text_of(post(client, "Murat, attack the Austrians at Swabia"))
        assert "cannot attack Bavaria" in message, message[:200]
