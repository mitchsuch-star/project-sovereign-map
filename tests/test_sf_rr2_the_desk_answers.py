"""Score Finish Step 9, SF-RR2 "the desk answers what was asked" (October 21,
2026; rules SYSTEMS_REFERENCE.md §137).

Every row the final reading filed against the state desk, reproduced at
`POST /command` on a fresh 1805 boot before a line was written:

    `Could Soult drill his corps today?`                        (SFR-H4)
        -> "Not today, Sire — Soult: Mack is at Swabia …" (the verb unnamed)
    `How many turns would it take Davout to march from Rhineland to Lorraine?`
        -> "Davout already stands at Rhineland …"                 (SFR-H8)
    `What happens if I order Davout to fortify in the Rhineland?`
        -> "Davout already stands at Rhineland, Sire."            (SFR-H9)
    `Berthier, which of my marshals can get at Mack soonest?`
        -> "Mack stands at Swabia, Sire — large force …"          (SFR-H10)
    `who's in the Third Coalition besides Britain?` -> the shrug (SFR-H11 i)
    `… enemy strength is 44% of ours. Does that count the Russians …?`
        -> "Russia: no word of Buxhowden …" (whereabouts)         (SFR-H11 ii)
    `why did that fail` (after a refusal) -> the shrug            (SFR-H12)
    `whats the flaw in our doctrine` -> the shrug                  (SFR-H14)
    nine plain questions -> the shrug                              (SFR-D2)
    `Talleyrand, how is the Prussian mission going?` -> a brief of the court (SFR-D16)
    `how many action points do I have?` -> the rules of the day    (SFR-D19)
    `what would Britain accept for peace?` -> "scores 30 — COUNTER_OFFER";
    `Talleyrand, would Austria take a white peace?` -> a brief     (SFR-D26)

Every answer is composed from a builder some surface already prints; every
row's SEAM held down reproduces its row (the DD-B idiom — no module lever);
every question spends nothing.
"""

from __future__ import annotations

import json
import re

import pytest
from fastapi.testclient import TestClient

import backend.ai.question_desk as QD
import backend.ai.state_desk as SD
import backend.main as M
from backend.commands.parser import CommandParser

SHRUG = "I cannot answer that from the dispatches"


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


def ask(client, world, line):
    """A question: answered, and nothing spent."""
    before = (int(world.actions_remaining), int(world.admin_actions_remaining),
              int(world.diplomatic_points))
    r = post(client, line)
    after = (int(world.actions_remaining), int(world.admin_actions_remaining),
             int(world.diplomatic_points))
    assert before == after, (line, before, after)
    return str(r.get("message") or "")


# ═════════════ SFR-H4: the refusal names its verb ═════════════════════════════

class TestSFRH4TheRefusalNamesItsVerb:

    def test_the_drill_question_names_the_drill(self, shipped):
        client, world = shipped
        answer = ask(client, world, "Could Soult drill his corps today?")
        assert answer.startswith("Not today, Sire — Soult cannot drill: Mack is at Swabia"), answer
        assert not world.marshals["Soult"].drilling

    def test_seam_down_drops_the_verb(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_refusal_sentence",
                            lambda shown, said, why: f"Not today, Sire — {shown}: {why}.")
        answer = ask(client, world, "Could Soult drill his corps today?")
        assert answer.startswith("Not today, Sire — Soult: Mack is at Swabia"), answer


# ═════════════ SFR-H8: the march reads its destination ════════════════════════

class TestSFRH8TheMarchReadsItsDestination:

    LINE = "How many turns would it take Davout to march from Rhineland to Lorraine?"

    def test_the_destination_is_the_province_after_to(self):
        dest, origin = SD._destination("march from rhineland to lorraine", ["Rhineland", "Lorraine"])
        assert (dest, origin) == ("Lorraine", "Rhineland")
        assert SD._destination("march to lorraine from rhineland", ["Lorraine", "Rhineland"]) == ("Lorraine", "Rhineland")
        assert SD._destination("march to lorraine", ["Lorraine"]) == ("Lorraine", "")

    def test_the_question_answers_the_march_to_lorraine(self, shipped):
        client, world = shipped
        answer = ask(client, world, self.LINE)
        assert "'Davout, march to Lorraine'" in answer, answer
        assert "Rhineland -> Lorraine" in answer
        assert "already stands" not in answer
        assert world.marshals["Davout"].location == "Rhineland"
        assert world.marshals["Davout"].strategic_order is None

    def test_a_wrong_origin_is_said_and_read_from_where_he_stands(self, shipped):
        client, world = shipped
        answer = ask(client, world, "How long would it take Davout to march from Paris to Lorraine?")
        assert answer.startswith("Davout stands at Rhineland, not Paris, Sire"), answer
        assert "Lorraine" in answer

    def test_seam_down_reads_the_first_province(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_destination", lambda norm, places: (places[0] if places else "", ""))
        answer = ask(client, world, self.LINE)
        assert answer.startswith("Davout already stands at Rhineland"), answer


# ═════════════ SFR-H9: the what-if reads its verb ═════════════════════════════

class TestSFRH9TheWhatIfReadsItsVerb:

    LINE = "What happens if I order Davout to fortify in the Rhineland?"

    def test_the_fortify_what_if_answers_the_fortify(self, shipped):
        client, world = shipped
        answer = ask(client, world, self.LINE)
        assert answer.startswith("Davout would fortify at Rhineland today, Sire — 1 action."), answer
        assert "Fortify digs the corps in where it stands" in answer
        assert "Iron Resolve" in answer
        assert answer.endswith("Nothing has been ordered.")
        assert not world.marshals["Davout"].fortified

    def test_a_place_elsewhere_says_he_must_march_first(self, shipped):
        client, world = shipped
        answer = ask(client, world, "What happens if I order Davout to fortify in Lorraine?")
        assert answer.startswith("Davout stands at Rhineland, not Lorraine, Sire"), answer
        assert "must march there first" in answer

    def test_a_refused_verb_gives_its_reason(self, shipped):
        client, world = shipped
        answer = ask(client, world, "What happens if Ney drills?")
        assert answer.startswith("Ney cannot drill today, Sire: Mack is at Swabia"), answer

    def test_seam_down_reads_a_march(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_what_if_question", lambda asked: None)
        answer = ask(client, world, self.LINE)
        assert answer.startswith("Davout already stands at Rhineland"), answer


# ═════════════ SFR-H10: who can strike him, soonest ═══════════════════════════

class TestSFRH10WhoCanStrike:

    LINE = "Berthier, which of my marshals can get at Mack soonest?"

    def test_every_corps_is_ranked_by_when_it_can_strike(self, shipped):
        client, world = shipped
        answer = ask(client, world, self.LINE)
        assert answer.startswith("Mack stands at Swabia, Sire."), answer
        today = answer.split("can strike him today")[0]
        for name in ("Ney", "Davout", "Soult", "Murat", "Lannes", "Bernadotte", "Napoleon"):
            assert name in today, (name, answer)
        assert "Next: Massena from Milan, 2 turns to Swabia." in answer
        # the attack's own reach and the march's own clock
        for m in world.get_player_marshals():
            if m.name in today:
                assert world.get_distance(m.location, "Swabia") <= m.movement_range

    def test_a_corps_held_by_its_state_is_said_held(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        answer = ask(client, world, "who can stop Mack?")
        assert "Within reach but held today: Davout — fortified — unfortify first." in answer, answer

    def test_a_man_no_roster_holds_is_answered_never_shrugged(self, shipped):
        client, world = shipped
        answer = ask(client, world, "who can stop Paget?")
        assert answer == "I know no foreign corps under Paget, Sire.", answer

    def test_seam_down_answers_where_he_stands(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_strike_question", lambda asked: None)
        assert ask(client, world, self.LINE).startswith("Mack stands at Swabia, Sire — large force")
        assert SHRUG in ask(client, world, "who can stop Paget?")


# ═════════════ SFR-H11: the coalition by name, the figure's scope ═════════════

class TestSFRH11TheCoalitionAndTheFigure:

    FIGURE = ("The dispatch says enemy strength is 44% of ours. Does that count the "
              "Russians, or only the armies we've actually spotted?")

    def test_the_coalition_besides_britain(self, shipped):
        client, world = shipped
        answer = ask(client, world, "who's in the Third Coalition besides Britain?")
        assert answer.startswith("Besides Britain: Austria and Russia, Sire."), answer
        assert "led by Britain" in answer

    def test_the_figure_says_what_it_counts(self, shipped):
        client, world = shipped

        def _find(node):
            if isinstance(node, dict):
                if "strength_ratio_pct" in node:
                    return node["strength_ratio_pct"]
                return next((v for v in map(_find, node.values()) if v is not None), None)
            return None
        pct = int(_find(world.last_morning_dispatch))   # the morning's own figure
        answer = ask(client, world, self.FIGURE)
        assert answer.startswith(f"The dispatch's figure ({pct}%) weighs the enemy corps in our intelligence"), answer
        assert "unscouted armies are not counted" in answer
        assert "Russia is not in it" in answer
        assert "no word of Kutuzov" in answer
        assert "Sire — Sire" not in answer

    def test_the_figure_unnamed_lists_the_courts_left_out(self, shipped):
        client, world = shipped
        answer = ask(client, world, "does the enemy strength figure count everyone?")
        assert "Not in it:" in answer and "Russia" in answer.split("Not in it:")[1], answer

    def test_seams_down_reproduce_both_halves(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_coalition_named_question", lambda asked: None)
        monkeypatch.setattr(SD, "_strength_figure_question", lambda asked: None)
        assert SHRUG in ask(client, world, "who's in the Third Coalition besides Britain?")
        assert ask(client, world, self.FIGURE).startswith("Sire — Russia: no word of Buxhowden")


# ═════════════ SFR-H12: why did that fail ═════════════════════════════════════

class TestSFRH12WhyDidThatFail:

    def test_a_refused_order_is_explained_by_its_own_words(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        refused = post(client, "Davout, attack Mack")
        assert refused.get("success") is False
        answer = ask(client, world, "why did that fail")
        head = str(refused.get("message")).strip().split("\n\n")[0]
        assert answer.startswith("Your last order — 'Davout, attack Mack' — was refused, Sire: "), answer
        assert head[:60] in answer

    def test_a_question_whose_answer_was_a_refusal(self, shipped):
        """The TYPED arm's own sequence (t6): the question's answer read as
        a failed order to the player."""
        client, world = shipped
        post(client, "Davout, fortify")
        post(client, "can Davout attack Mack")
        answer = ask(client, world, "why did that fail")
        assert answer.startswith("'can Davout attack Mack' was a question, Sire, and nothing was spent"), answer
        assert "Davout is fortified — unfortify first" in answer

    def test_an_order_that_went_through_did_not_fail(self, shipped):
        client, world = shipped
        post(client, "Napoleon, take up a defensive position")
        post(client, "where is Mack?")
        answer = ask(client, world, "why was my order refused?")
        assert answer.startswith("Your last order — 'Napoleon, take up a defensive position' — did not fail"), answer

    def test_the_reply_is_display_only_and_never_saved(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        post(client, "Davout, attack Mack")
        assert getattr(world, "_last_order_reply", None)
        blob = json.dumps(world.to_dict(), default=str)
        assert "_last_order_reply" not in blob and "_last_reply" not in blob

    def test_seam_down_shrugs(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_why_question", lambda asked: None)
        post(client, "Davout, fortify")
        post(client, "Davout, attack Mack")
        assert SHRUG in ask(client, world, "why did that fail")


# ═════════════ SFR-H14: the doctrine's flaw ═══════════════════════════════════

class TestSFRH14TheDoctrinesFlaw:

    @pytest.mark.parametrize("line", ["whats the flaw in our doctrine",
                                      "what's the weakness of our doctrine?",
                                      "what is the strength of our army's doctrine"])
    def test_the_flaw_is_the_doctrine_answer(self, shipped, line):
        client, world = shipped
        answer = ask(client, world, line)
        assert answer.startswith("Our army fights by The Corps System, Sire."), answer
        assert "Its flaw, Living off the land" in answer

    def test_seam_down_shrugs(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "doctrine_flaw_kind", lambda: None)
        assert SHRUG in ask(client, world, "whats the flaw in our doctrine")


# ═════════════ SFR-D2: the plain questions ════════════════════════════════════

PLAIN = [
    ("what happened at Swabia?", "Nothing at Swabia is on our record, Sire."),
    ("who holds Bavaria?", "Bavaria is a court, Sire, not a province — it holds 3 provinces"),
    ("who deserves a reward?", "The ladder of glory"),
    ("who are we STILL at war with?", "We are at war with the Third Coalition"),
    ("is the war with Austria over?", "Not yet, Sire — we are at war with Austria."),
    ("how loyal are my marshals?", "Their trust, Sire: Bernadotte 40"),
    ("who could become our vassal?", "Propose Vassal row"),
    ("is Sardinia still in play?", "No, Sire — Sardinia's allegiance is not in play today."),
]


class TestSFRD2ThePlainQuestions:

    @pytest.mark.parametrize("line,expect", PLAIN)
    def test_each_is_answered(self, shipped, line, expect):
        client, world = shipped
        answer = ask(client, world, line)
        assert expect in answer, (line, answer)
        assert SHRUG not in answer

    @pytest.mark.parametrize("line,expect", PLAIN)
    def test_seam_down_shrugs(self, shipped, monkeypatch, line, expect):
        client, world = shipped
        monkeypatch.setattr(SD, "_plain_question", lambda asked: None)
        answer = ask(client, world, line)
        assert expect not in answer, (line, answer)

    def test_a_battle_is_on_the_record_at_its_place(self, shipped):
        client, world = shipped
        post(client, "Ney, attack Mack")
        answer = ask(client, world, "what happened at Swabia?")
        assert answer.startswith("At Swabia, Sire — turn 1: The Great Battle of Swabia"), answer

    def test_an_open_auction_is_in_play(self, shipped):
        client, world = shipped
        world.allegiance_auctions["Sardinia"] = {"opened_turn": 1, "resolves_turn": 4}
        answer = ask(client, world, "is Sardinia still in play?")
        assert answer.startswith("Yes, Sire — Sardinia's allegiance is in play; the flip resolves in 3 turns"), answer
        assert "F1 → the court → Bid for Their Allegiance" in answer
        assert "In play: Sardinia" in ask(client, world, "is Naples in play?")

    def test_the_vassal_rows_are_the_cabinets_own(self, shipped):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        client, world = shipped
        answer = ask(client, world, "who could become our vassal?")
        for court in ("Bavaria", "Spain"):
            row = next(r for r in get_available_diplomatic_actions(world, court)
                       if r["action"] == "propose_vassal")
            assert row["available"]
            assert f"{court} ({str(row['likelihood']).lower()}, {int(row['likelihood_score'])})" in answer

    def test_will_he_obey_names_the_rule_and_his_gift(self, shipped):
        client, world = shipped
        answer = ask(client, world, "will bernadotte actualy obey me? the help says he may not march for me at all")
        assert answer.startswith("Bernadotte's trust stands at 40 of 100"), answer
        assert "below 40 he objects and may defy an order" in answer
        assert "Bernadotte —" in answer and "(G)" in answer


# ═════════════ SFR-D16 / SFR-D26: Talleyrand answers from the desk ════════════

class TestSFRD16TheMission:

    def test_the_mission_is_asked(self, shipped):
        client, world = shipped
        assert ask(client, world, "Talleyrand, how is your mission going?").startswith(
            "Talleyrand has no mission running, Sire.")
        post(client, "Talleyrand, improve relations with Prussia")
        post(client, "Begin mission")
        answer = ask(client, world, "Talleyrand, how is the Prussian mission going?")
        assert answer.startswith("Improving Relations — Prussia, Sire: Relations with Prussia"), answer
        assert "1 DP a turn" in answer and "The Cabinet's Recall ends it." in answer
        assert "cancel mission" not in answer.lower()   # diplomacy is never typed
        other = ask(client, world, "Talleyrand, how goes the Austrian mission?")
        assert other.startswith("Talleyrand has no mission at Austria, Sire — he is at Prussia"), other

    def test_seam_down_keeps_the_advisory(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_mission_question", lambda asked: None)
        monkeypatch.setattr(SD, "_talleyrand_mission", lambda norm, court: None)
        post(client, "Talleyrand, improve relations with Prussia")
        post(client, "Begin mission")
        answer = ask(client, world, "Talleyrand, how is the Prussian mission going?")
        assert "Improving Relations — Prussia" not in answer, answer


class TestSFRD19ActionPoints:

    @pytest.mark.parametrize("line", ["how many action points do I have?",
                                      "How many action points do I have to spend this turn?",
                                      "how many AP do I have left?"])
    def test_the_count_leads(self, shipped, line):
        client, world = shipped
        answer = ask(client, world, line)
        assert answer.startswith("Today 4 of 4 orders (military actions) remain, Sire, and 2 of 2 administrative actions."), answer
        assert "Talleyrand holds 5 diplomatic points of 5" in answer

    def test_seam_down_reads_the_rules(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "action_points_kind", lambda text: None)
        assert ask(client, world, "how many action points do I have?").startswith(
            "Each turn gives the day's orders")


class TestSFRD26ThePeaceInWords:

    @pytest.mark.parametrize("line,court", [
        ("what would Britain accept for peace?", "Britain"),
        ("Talleyrand, would Austria take a white peace right now?", "Austria"),
        ("Talleyrand, what would Austria accept for peace?", "Austria"),
    ])
    def test_the_estimate_is_in_words(self, shipped, line, court):
        from backend.game_logic.diplomacy import calculate_acceptance
        client, world = shipped
        score = int(calculate_acceptance({"type": "peace", "proposer_nation": "France",
                                          "target_nation": court, "terms": {}}, world)["score"])
        answer = ask(client, world, line)
        assert answer.startswith(f"A white peace put to {court} today reads {score} of the 50 a signature needs"), answer
        assert not re.search(r"\b(?:COUNTER_OFFER|REJECT|ACCEPT)\b", answer)
        assert "Talleyrand's reading:" in answer
        assert f"The Cabinet (F1 → {court}) sends it" in answer

    def test_the_talleyrand_question_reaches_the_desk(self):
        assert SD.classify_talleyrand_question(
            "Talleyrand, would Austria take a white peace right now?", "Austria")["kind"] == "peace_forecast"
        assert SD.classify_talleyrand_question(
            "Talleyrand, how is the Prussian mission going?", "Prussia")["kind"] == "mission"
        # every other question keeps the advisory
        assert SD.classify_talleyrand_question("Talleyrand, should we declare war on Prussia?", "Prussia") is None
        assert SD.classify_talleyrand_question("Talleyrand, assess Austria", "Austria") is None

    def test_seam_down_restores_the_code_word_and_the_brief(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_verdict_words", lambda outcome: outcome)
        monkeypatch.setattr(SD, "_talleyrand_peace", lambda norm, court: None)
        monkeypatch.setattr(SD, "_talleyrand_board", lambda text, court: None)
        assert re.search(r"reads -?\d+ of the 50 a signature needs — (?:REJECT|COUNTER_OFFER|ACCEPT), Sire",
                         ask(client, world, "what would Britain accept for peace?"))
        brief = ask(client, world, "Talleyrand, would Austria take a white peace right now?")
        assert "We are at war with Austria, Sire" in brief, brief


# ═════════════ the siblings (Rule 10): RR2-X1 … X12 ═══════════════════════════

class TestTheSiblings:

    def test_x1_a_report_filed_today_is_not_zero_turns_ago(self, shipped, monkeypatch):
        client, world = shipped
        import backend.ai.question_desk as qd
        charles = next(n for n, m in world.marshals.items() if m.nation == "Austria" and "Charles" in n)
        monkeypatch.setattr(qd, "_last_report_of", lambda w, n: ("Tyrol", 0))
        monkeypatch.setattr(type(world.get_region_intel("Tyrol")), "visibility_at_least",
                            lambda self, level: False)
        _enemy, line = SD._visible_foe(world, charles)
        assert "in today's report" in line and "0 turns ago" not in line, line

    def test_x2_why_never_explains_itself_nor_a_shrug(self, shipped):
        client, world = shipped
        post(client, "Napoleon, take up a defensive position")
        post(client, "flurble wibble?")
        first = ask(client, world, "why did that fail")
        second = ask(client, world, "why did that fail")
        assert first == second, (first, second)
        assert first.startswith("Your last order — 'Napoleon, take up a defensive position'"), first

    def test_x3_an_arrival_at_once_is_this_very_turn(self, shipped):
        client, world = shipped
        answer = ask(client, world, "how long from Rhineland to Lorraine for Davout?")
        assert "this very turn" in answer and "0 turns" not in answer, answer

    def test_x4_reach_from_elsewhere(self, shipped):
        client, world = shipped
        answer = ask(client, world, "can Ney reach Vienna from Bohemia?")
        assert answer.startswith("Ney stands at Rhineland, not Bohemia, Sire — reckoned from where he stands: "
                                 "Yes, Sire — Ney can reach Vienna"), answer

    @pytest.mark.parametrize("line,expect", [
        ("what if Murat scouts Tyrol?", "Tyrol lies 2 marches from Franche-Comte, Sire — a scout reveals only a neighbouring province."),
        ("what happens if Ney retreats?", "Ney would fall back today, Sire — free."),
        ("what if Soult holds Lorraine?", "Soult would hold at Lorraine today, Sire"),
        ("what happens if Ney defends?", "Ney would defend at Rhineland today, Sire — 1 action."),
        ("what if I have Murat charge Mack?", "MUSTER — Murat"),
    ])
    def test_x5_the_what_if_verbs(self, shipped, line, expect):
        client, world = shipped
        answer = ask(client, world, line)
        assert expect in answer, (line, answer)
        assert "(not defending)" not in answer

    def test_x6_why_cant_he_and_why_did_my_attack_fail(self, shipped):
        client, world = shipped
        post(client, "Davout, fortify")
        assert ask(client, world, "why can't Davout attack?") == \
            "Not today, Sire — Davout cannot attack: fortified — unfortify first."
        post(client, "Davout, attack Mack")
        assert ask(client, world, "why did my attack fail?").startswith(
            "Your last order — 'Davout, attack Mack' — was refused, Sire")

    @pytest.mark.parametrize("line,expect", [
        ("Talleyrand, who could become our vassal?", "Propose Vassal row"),
        ("Talleyrand, is Sardinia still in play?", "No, Sire — Sardinia's allegiance is not in play today."),
        ("Talleyrand, what does Austria want?", "Austria pursues Redeem Italy"),
        ("Talleyrand, who is in the coalition?", "Third Coalition: Austria, Britain and Russia, led by Britain"),
        ("Talleyrand, is the war with Austria over?", "Not yet, Sire — we are at war with Austria."),
        ("Talleyrand, would Prussia accept an alliance?", "An alliance put to Prussia today reads"),
        ("Talleyrand, what are Austria's chances of making peace?", "A white peace put to Austria today reads"),
    ])
    def test_x7_talleyrand_answers_from_the_desk(self, shipped, line, expect):
        client, world = shipped
        answer = ask(client, world, line)
        assert expect in answer, (line, answer)
        assert "I do not find 'Talleyrand'" not in answer

    def test_x7_seam_down_keeps_the_generic_brief(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(SD, "_talleyrand_board", lambda text, court: None)
        assert "Propose Vassal row" not in ask(client, world, "Talleyrand, who could become our vassal?")

    def test_x7_his_own_assessments_stay_his(self, shipped):
        client, world = shipped
        for line in ("Talleyrand, assess Austria", "Talleyrand, can we make peace with Austria?"):
            parsed = M.parser.parse(line, M.get_llm_game_state(), world=world)
            assert (parsed.get("command") or {}).get("action") != "status", (line, parsed.get("command"))

    def test_x8_a_bare_percentage_asked_what_it_counts(self, shipped):
        client, world = shipped
        answer = ask(client, world, "does the 44% count the Russians?")
        assert answer.startswith("The dispatch's figure ("), answer
        assert "Russia is not in it" in answer

    def test_x9_the_doctrines_possessive_flaw(self, shipped):
        client, world = shipped
        assert "Its flaw, Living off the land" in ask(client, world, "whats our doctrine's flaw")

    def test_x10_every_court_is_accounted_for(self, shipped):
        client, world = shipped
        answer = ask(client, world, "who could become our vassal?")
        assert ("At war with us: Austria, Britain and Russia — a court at war is made a vassal "
                "only by a dictated peace.") in answer, answer
        assert "stand below open borders with us — the row needs open borders or better." in answer
        # a court the row shuts is named with its own reason
        world.diplomatic_points = 0
        answer = ask(client, world, "who could become our vassal?")
        assert "Shut today: Bavaria — " in answer and "Spain — " in answer, answer

    def test_x11_the_truce_is_scored_as_the_cabinets_row(self, shipped):
        from backend.game_logic.diplomacy import (armistice_variant_for, calculate_acceptance)
        client, world = shipped
        score = int(calculate_acceptance({"type": armistice_variant_for(world, "France", "Austria"),
                                          "proposer_nation": "France", "target_nation": "Austria",
                                          "terms": {}}, world)["score"])
        answer = ask(client, world, "Talleyrand, would Austria accept an armistice?")
        assert answer.startswith(f"A truce put to Austria today reads {score} of the 50"), answer
        assert "The Cabinet (F1 → Austria) sends it." in answer

    def test_x12_a_generic_follow_never_overrides_an_attack(self, shipped):
        client, world = shipped
        r = post(client, "Davout strikes Mack, cavalry to follow.")
        assert str(r.get("message")).startswith("MUSTER — Davout"), r.get("message")
        assert world.marshals["Davout"].strategic_order is None
        assert world.marshals["Davout"].location in ("Rhineland", "Swabia")

    def test_x12_seam_down_restores_the_march_to_bernadotte(self, shipped, monkeypatch):
        import backend.commands.parser as P
        client, world = shipped
        monkeypatch.setattr(P, "_a_generic_follow_keeps_the_attack", lambda *args: False)
        r = post(client, "Davout attacks Mack, cavalry to follow.")
        assert "support" in str(r.get("message")).lower(), r.get("message")


# ═════════════ the HOLD's twenty questions on the boot ════════════════════════

class TestTheHoldQuestions:
    """SF-RR2's done-when on the wire: the HOLD arm's twenty blind questions
    (`tools/playtest_scripts/score_hold_2026_10_05.json`, turn 1) shrug at
    most once on a fresh boot."""

    def test_at_most_one_shrug(self, shipped):
        import pathlib
        client, world = shipped
        script = json.loads(pathlib.Path("tools/playtest_scripts/score_hold_2026_10_05.json")
                            .read_text(encoding="utf-8"))
        shrugs = [q["line"] for q in script["hold"]["questions"]
                  if SHRUG in ask(client, world, q["line"])]
        assert len(shrugs) <= 1, shrugs


class TestS14DX29TheLawsAnswer:
    """S14D-X29 (October 23, 2026): the desk's laws answer gave no key, no
    currency and no lapse where every other surface says 'T, then 8'."""

    def test_the_desk_names_the_key_the_currencies_and_the_lapse(self):
        from backend.ai.state_desk import _rule_text
        from backend.game_logic.reforms import ARREARS_WINDOW_TURNS
        from backend.models.world_state import WorldState as _WS
        text = _rule_text(_WS(player_nation="France"), "laws", False)
        assert "T, then 8 (Alt+8 while you type)" in text
        assert "in gold or in authority" in text and "heaviest upkeep lapses first" in text
        assert f"within {int(ARREARS_WINDOW_TURNS)} turns at half its price plus the arrears" in text
