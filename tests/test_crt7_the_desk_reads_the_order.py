"""CRT-7 — "The desk answers what the order would do" (the CR-6 triage,
slice 7; build contract = `docs/COMMAND_ROBUSTNESS_SPEC.md` §12.3; rows
DESK-1 / 2 / 4 / 5 / 7 / 8 / 9 / 11 / 12 / 13 / 14 / 15 / 16 + DESK-6's dead
clause, and the Creative AAR's desk rows AAR-17 / AAR-19 / AAR-23 / AAR-29 /
AAR-31; landed as Score Mandate Chunk 3 SR-3a part (ii), September 26, 2026).

Reproduced on this HEAD at the real `POST /command` before a line was
written, on the shipped 1805 boot:

    `who am I fighting and why`         "I cannot answer that from the dispatches"
    `is Vienna safe?`                   the same shrug
    `What does Kutuzov have with him?`  the same shrug
    `How long until the armistice …`    the same shrug, in a truce too
    `who are my allies`                 the same shrug, pointing at nothing
    `how is the war effort`             pointed at the ECONOMY tab ("effort"
                                        contains "fort")
    `what happened last turn`           "I cannot interpret that order"
    `why not attack Kutuzov`            "…within reach of Kutuzov at PODOLIA" —
                                        a cell the player had never seen
    `what if I attack Deroy`            a MUSTER against our Bavarian ally
    `what if I attack Mack` (truce)     a MUSTER the order refuses
    `how much is a gun`                 "654 gold for 10,000 artillery" — no
                                        commander of guns serves
    `how much is a battalion`           654 for 10,000 where the order raises
                                        3,000 for 741 under Davout
    `what is my income`                 3,400 + 350 − 2,630 = 1,120 against a
                                        printed Net of +1,842
    `who is winning`                    three even scores for ONE coalition war
    `what can I do` at 0 actions        four orders the game refuses
    the boot's `Ney, drill`             refused ("enemy forces nearby")
    `where is Ney` (fallen)             the shrug

The through-line: every desk answer asks the SEAM that would refuse or charge
the order. Each rule sits behind its own lever whose down arm reproduces the
row; every wire pin reads the WORLD (the action points, the states) and the
answer, never only the answer.
"""

import re

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.counsel as COUNSEL
import backend.ai.question_desk as QD
import backend.commands.executor as EX
import backend.commands.strategic_executor as SE
import backend.commands.tactical_executor as TE
import backend.main as M
from backend.commands.meta_executor import MetaExecutor
from backend.commands.parser import CommandParser


# ═══════════════════════════════════════════════════════════════════════════
# The board
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams with a mock parser (the
    CRT-1 idiom). The suite pins `SOVEREIGN_SCENARIO=none`; these rows need
    Ney at Rhineland, Mack at Swabia, Kutuzov unseen and Deroy an ally."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def ask(client, world, question):
    """A question spends nothing: the military and administrative actions
    are read before and after, and the message is returned."""
    before = (int(world.actions_remaining), int(world.admin_actions_remaining))
    data = post(client, question)
    after = (int(world.actions_remaining), int(world.admin_actions_remaining))
    assert before == after, (question, before, after)
    assert not data.get("battle_report"), question
    return str(data.get("message") or "")


def truce(world, court="Austria", elapsed=2):
    key = world._make_diplo_key("France", court)
    world.diplomatic_states[key] = "ARMISTICE"
    world.armistice_turns[key] = elapsed
    world.invalidate_bloc_members_cache()
    return key


def see(world, region_name):
    from backend.models.intel import PARTIAL
    world.get_region_intel(region_name).visibility = PARTIAL


SHRUG = "cannot answer that"


# ═══════════════════════════════════════════════════════════════════════════
# AAR-17 — the first questions a player asks
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWarQuestion:
    """`wars`: the war banner's own rows, our purpose, their designs."""

    PHRASINGS = ["who am I fighting and why", "who are we at war with",
                 "who is at war with us", "who are our enemies",
                 "who am I fighting", "why are we at war", "am I at war"]

    @pytest.mark.parametrize("q", PHRASINGS)
    def test_the_courts_at_war_are_named_with_the_purpose(self, shipped, q):
        client, world = shipped
        message = ask(client, world, q)
        for court in ("Austria", "Britain", "Russia"):
            assert court in message, (q, message)
        assert "Third Coalition" in message, (q, message)
        assert "Our purpose" in message and "homeland" in message, (q, message)
        assert "Redeem Italy" in message, (q, message)   # Austria's design
        assert SHRUG not in message, (q, message)

    def test_the_lever_down_is_the_shrug(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_DESK_ANSWERS_THE_WAR_QUESTION", False)
        message = ask(client, world, "who am I fighting and why")
        assert SHRUG in message, message

    def test_a_truce_is_listed_under_truce(self, shipped):
        client, world = shipped
        truce(world, "Austria", elapsed=1)
        message = ask(client, world, "who are we at war with")
        assert "Under truce: Austria" in message, message


class TestOurAllies:
    @pytest.mark.parametrize("q", ["who are my allies", "do we have any allies",
                                   "who is allied with us", "who stands with us"])
    def test_the_allies_and_the_clients_are_named(self, shipped, q):
        client, world = shipped
        message = ask(client, world, q)
        for court in ("Spain", "Bavaria"):
            assert court in message, (q, message)
        for client_state in ("Holland", "Kingdom of Italy", "Switzerland"):
            assert client_state in message, (q, message)
        assert "Diplomatic Ledger" in message, message
        assert SHRUG not in message, (q, message)

    def test_the_allies_are_the_engines_own_predicate(self, shipped):
        client, world = shipped
        allies = {n for n in world.get_active_nations()
                  if n != "France" and world.are_allies("France", n)}
        assert allies == {"Spain", "Bavaria"}, allies
        message = ask(client, world, "who are my allies")
        for other in world.get_active_nations():
            if other in allies or other == "France":
                continue
            if other in ("Holland", "KingdomOfItaly", "Switzerland"):
                continue   # the clients, named in their own clause
            assert QD._court(world, other) not in message.split("Our clients")[0], (other, message)


class TestIsItSafe:
    def test_a_province_beside_a_visible_enemy_names_him(self, shipped):
        client, world = shipped
        message = ask(client, world, "is Rhineland safe?")
        assert message.startswith("Rhineland is ours"), message
        assert "Ney" in message and "Davout" in message, message
        assert "Mack" in message and "Swabia" in message and "one march away" in message, message
        assert "held, but threatened" in message, message

    def test_a_fogged_threat_and_a_fogged_garrison_are_never_named(self, shipped):
        client, world = shipped
        from backend.models.intel import PARTIAL
        assert not world.get_region_intel("Vienna").visibility_at_least(PARTIAL)
        garrison = int(world.get_region("Vienna").garrison_strength)
        assert garrison > 0
        message = ask(client, world, "is Vienna safe?")
        assert "Vienna is Austria's" in message, message
        assert "no intelligence on what holds it" in message, message
        assert f"{garrison:,}" not in message, message
        for hidden in ("Podolia", "Kutuzov"):
            assert hidden not in message, message

    def test_a_quiet_province_looks_safe(self, shipped):
        client, world = shipped
        message = ask(client, world, "is Brittany safe?")
        assert "Brittany is ours" in message, message
        assert "looks safe today" in message, message
        assert "so far as our intelligence reaches" in message, message

    def test_the_garrison_gate_reads_the_fog(self, shipped):
        _, world = shipped
        fogged = QD._answer_safe(world, "France", "Vienna")
        see(world, "Vienna")
        seen = QD._answer_safe(world, "France", "Vienna")
        garrison = int(world.get_region("Vienna").garrison_strength)
        assert f"{garrison:,}" not in fogged and f"{garrison:,}" in seen, (fogged, seen)


class TestWhatDoesHeHave:
    def test_a_visible_enemy_is_answered_with_the_report_s_band(self, shipped):
        client, world = shipped
        message = ask(client, world, "What does Mack have with him?")
        assert "Mack" in message and "Swabia" in message, message
        assert "large force" in message or "men" in message, message

    def test_a_fogged_enemy_is_answered_honestly(self, shipped):
        client, world = shipped
        message = ask(client, world, "What does Kutuzov have with him?")
        assert "no word of Kutuzov" in message and "Podolia" not in message, message

    def test_the_court_s_want_is_still_the_wants_kind(self, shipped):
        client, world = shipped
        message = ask(client, world, "what does Austria want")
        assert "Redeem Italy" in message, message


class TestTheTruceClock:
    def test_the_turns_left_are_the_engine_s_own_rule(self, shipped):
        client, world = shipped
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        key = truce(world, "Austria", elapsed=2)
        message = ask(client, world, "How long until the armistice with Austria expires?")
        assert f"{ARMISTICE_DURATION - 2} turns to run" in message, message
        assert "Austria" in message, message
        relation = int(world.nation_relations.get(key, 0))
        assert f"{relation:+d}" in message and "-60" in message, message
        assert "the war would resume" in message, message

    def test_no_truce_says_so(self, shipped):
        client, world = shipped
        message = ask(client, world, "How long until the armistice with Russia expires?")
        assert "no armistice with Russia" in message and "are at war" in message, message
        assert "At War" not in message, message

    def test_no_court_named_lists_every_truce(self, shipped):
        client, world = shipped
        truce(world, "Austria", elapsed=1)
        message = ask(client, world, "when does the truce end")
        assert "Austria" in message and "4 turns to run" in message, message

    def test_the_attack_refusal_agrees_with_the_clock(self, shipped):
        """DESK-4's rider: `_make_diplomatic_error` printed the cooldown the
        engine writes ONCE at the truce's start (5, never decremented) as
        "turns remaining" — every turn of the truce. It reads the clock."""
        client, world = shipped
        truce(world, "Austria", elapsed=2)
        clock = ask(client, world, "How long until the armistice with Austria expires?")
        what_if = ask(client, world, "what if I attack Mack")
        assert "3 turns to run" in clock, clock
        assert "3 turns remaining" in what_if, what_if
        assert "MUSTER" not in what_if and "would be refused" in what_if, what_if

    def test_one_turn_left_is_singular(self, shipped):
        _, world = shipped
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.diplomacy import ARMISTICE_DURATION
        truce(world, "Austria", elapsed=ARMISTICE_DURATION - 1)
        block = CommandExecutor()._make_diplomatic_error(
            world, "France", world.get_marshal("Mack"))
        assert "(1 turn remaining)" in block["message"], block


class TestTheWarEffort:
    def test_the_national_weariness_is_read(self, shipped):
        client, world = shipped
        world.war_exhaustion["France"] = 12
        message = ask(client, world, "how is the war effort")
        assert "France's war weariness stands at 12" in message, message
        assert "Economy tab" not in message, message
        assert "Austria" in message, message   # the readable court's line

    def test_a_fogged_court_is_said_unread(self, shipped):
        client, world = shipped
        message = ask(client, world, "how is the war effort")
        assert "we cannot read" in message, message


class TestTheNews:
    def test_the_boot_has_no_last_turn(self, shipped):
        client, world = shipped
        message = ask(client, world, "what happened last turn")
        assert "just opened" in message, message
        assert "press R" in message and "Moniteur" in message, message
        assert "cannot interpret" not in message, message

    def test_a_dispatch_is_read_back(self, shipped):
        client, world = shipped
        world.last_morning_dispatch = {
            "turn": 3,
            "headline": {"text": "Vienna has fallen to Marshal Ney."},
            "turn_events": [{"message": "Davout took Swabia"},
                            {"message": "Mack retreated to Bavaria"}],
        }
        message = ask(client, world, "what happened last turn")
        assert "Vienna has fallen" in message, message
        assert "Davout took Swabia" in message and "Mack retreated" in message, message

    @pytest.mark.parametrize("text", ["what happened last turn", "what happened",
                                      "what became of Ney", "what went wrong"])
    def test_a_past_tense_wh_lead_is_a_question(self, text):
        assert CG.is_question(text, []) is True, text

    def test_the_past_tense_lever_down_reproduces_the_shrug(self, monkeypatch):
        monkeypatch.setattr(CG, "A_PAST_TENSE_WH_IS_A_QUESTION", False)
        assert CG.is_question("what happened last turn", []) is False

    def test_an_order_shaped_past_tense_stays_out(self):
        # "what took Vienna" is "take Vienna" one word over — a closed list.
        assert CG.is_question("what took Vienna", []) is False

    @pytest.mark.parametrize("q", ["is Vienna safe?", "who are my allies",
                                   "how is the war effort", "what happened last turn",
                                   "when does the truce end"])
    def test_the_war_question_lever_down_returns_each_kind_to_the_shrug(
            self, shipped, monkeypatch, q):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_DESK_ANSWERS_THE_WAR_QUESTION", False)
        message = ask(client, world, q)
        assert SHRUG in message, (q, message)


# ═══════════════════════════════════════════════════════════════════════════
# DESK-1 / DESK-4 — the what-if is fog-honest and refuses like the order
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWhatIfIsFogHonest:
    @pytest.mark.parametrize("q", ["why not attack Kutuzov", "what if I attack Kutuzov",
                                   "should I attack Kutuzov"])
    def test_no_hidden_province_is_named(self, shipped, q):
        client, world = shipped
        from backend.models.intel import PARTIAL
        kutuzov = world.get_marshal("Kutuzov")
        assert not world.get_region_intel(kutuzov.location).visibility_at_least(PARTIAL)
        message = ask(client, world, q)
        assert kutuzov.location not in message, (q, message)
        assert "no word of Kutuzov" in message, (q, message)
        assert "no battle to weigh" in message, (q, message)

    def test_the_lever_down_leaks_the_cell(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_WHAT_IF_IS_FOG_HONEST", False)
        message = ask(client, world, "why not attack Kutuzov")
        assert world.get_marshal("Kutuzov").location in message, message

    def test_a_seen_foe_out_of_reach_still_names_his_province(self, shipped):
        client, world = shipped
        kutuzov = world.get_marshal("Kutuzov")
        see(world, kutuzov.location)
        message = ask(client, world, "what if I attack Kutuzov")
        assert kutuzov.location in message and "within reach" in message, message


class TestTheWhatIfRefusesLikeTheOrder:
    def test_an_ally_is_never_mustered_against(self, shipped):
        client, world = shipped
        deroy = world.get_marshal("Deroy")
        assert world.are_allies("France", deroy.nation)
        message = ask(client, world, "what if I attack Deroy")
        assert "MUSTER" not in message, message
        assert "our ally" in message and "would be refused" in message, message

    def test_the_lever_down_musters_against_the_ally(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_WHAT_IF_REFUSES_LIKE_THE_ORDER", False)
        message = ask(client, world, "what if I attack Deroy")
        assert "MUSTER" in message, message

    def test_the_refusal_is_the_order_s_own_predicate(self, shipped):
        _, world = shipped
        from backend.commands.combat_executor import friendly_fire_refusal
        deroy = world.get_marshal("Deroy")
        assert friendly_fire_refusal(world, world.get_marshal("Ney"), deroy.nation)
        assert "would be refused" in QD._answer_what_if(world, "France", "Deroy")

    def test_a_court_at_peace_is_warned_before_the_muster(self, shipped):
        client, world = shipped
        prussian = next(m for m in world.marshals.values()
                        if m.nation == "Prussia" and m.strength > 0)
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
        see(world, prussian.location)
        message = ask(client, world, f"what if I attack {QD._display(prussian.name)}")
        assert "at peace with Prussia" in message, message
        assert "declaration of war" in message, message
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"

    def test_a_war_foe_still_musters(self, shipped):
        client, world = shipped
        message = ask(client, world, "what if I attack Mack")
        assert "MUSTER" in message and "Nothing has been ordered" in message, message


# ═══════════════════════════════════════════════════════════════════════════
# DESK-2 — the price is the quote
# ═══════════════════════════════════════════════════════════════════════════

def cheapest_quote(world, arm):
    from backend.commands.economy_executor import recruit_quote
    best, seen = None, set()
    for marshal in world.get_player_marshals():
        if marshal.strength <= 0 or marshal.captured_by or marshal.location in seen:
            continue
        seen.add(marshal.location)
        quote = recruit_quote(world, marshal.location, arm, "France")
        if quote.get("ok") and (best is None or quote["price"] < best["price"]):
            best = dict(quote, where=marshal.location)
    return best


class TestThePriceIsTheQuote:
    def test_the_battalion_is_priced_by_the_executor(self, shipped):
        client, world = shipped
        quote = cheapest_quote(world, "infantry")
        assert quote, "no levy raises on the boot"
        message = ask(client, world, "how much is a battalion")
        assert f"{int(quote['price']):,} gold for {int(quote['amount']):,} infantry" in message, (quote, message)
        assert f"recruit infantry in {quote['where']}" in message, message
        assert quote["recipient"] in message, message
        assert "10,000" not in message, message

    def test_a_gun_with_no_gun_marshal_is_the_refusal(self, shipped):
        client, world = shipped
        message = ask(client, world, "how much is a gun")
        assert "No artillery can be raised today" in message, message
        assert "Marmont" in message, message
        assert "654" not in message and "10,000" not in message, message

    def test_the_horse_the_chest_cannot_pay_says_so(self, shipped):
        client, world = shipped
        message = ask(client, world, "how much is cavalry")
        assert "treasury holds 800" in message, message
        assert "refused until it can pay" in message, message

    def test_the_lever_down_quotes_the_ledger_s_ten_thousand(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_PRICE_IS_THE_QUOTE", False)
        message = ask(client, world, "how much is a gun")
        assert "10,000 artillery" in message, message

    def test_the_cheapest_levy_wins_over_the_first(self, shipped):
        """The sweep's first INERT: on the boot ONE province levies, so the
        first quote was the cheapest by accident. Staged: Ney (the wasteful
        Intendance, ×1.15) alone at Champagne — iterated FIRST — and Davout
        (thrifty, ×0.85) at Rhineland; the answer must quote Rhineland."""
        client, world = shipped
        from backend.commands.economy_executor import recruit_quote
        world.nation_gold["France"] = 5000   # every levy affordable; the price decides
        ney = world.get_marshal("Ney")
        ney.location = "Provence"            # own soil, out of the capital's reach
        capital = world.get_nation_capital("France")
        assert not recruit_quote(world, capital, "infantry", "France").get("ok")
        first = recruit_quote(world, "Provence", "infantry", "France")
        assert first.get("ok") and first["recipient"] == "Ney", first
        assert list(world.get_player_marshals())[0].name == "Ney"
        best = cheapest_quote(world, "infantry")
        assert best["where"] != "Provence", best
        assert int(best["price"]) < int(first["price"]), (best, first)
        message = ask(client, world, "how much is a battalion")
        assert f"'recruit infantry in {best['where']}'" in message, (best, message)
        assert f"{int(best['price']):,} gold" in message, message
        # The dearer first quote is never the ORDER offered (the capital's own
        # refusal may still name Ney's ground as the remedy — that is honest).
        assert "'recruit infantry in Provence'" not in message, message

    def test_the_bare_order_s_ground_is_quoted_first(self, shipped):
        """`recruit infantry` is raised at the capital; where a receiver
        stands within reach of it, that quote is the answer."""
        _, world = shipped
        from backend.commands.economy_executor import recruit_quote
        capital = world.get_nation_capital("France")
        world.get_marshal("Ney").location = capital
        quote = recruit_quote(world, capital, "infantry", "France")
        assert quote.get("ok"), quote
        answer = QD._answer_levy_price(world, "France", "infantry")
        assert f"{int(quote['price']):,} gold" in answer and f"at {capital}" in answer, answer


# ═══════════════════════════════════════════════════════════════════════════
# DESK-5 — the income sentence sums
# ═══════════════════════════════════════════════════════════════════════════

def _figures(clause):
    return [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", clause)]


class TestTheIncomeSentenceSums:
    def test_the_named_figures_sum_to_the_net(self, shipped):
        client, world = shipped
        from backend.game_logic.ledger import _build_economy
        econ = _build_economy(world, "France")
        message = ask(client, world, "what is my income")
        credits = _figures(message.split("In:")[1].split("Out:")[0])
        debits = _figures(message.split("Out:")[1].split("Net")[0])
        net = int(re.search(r"Net ([+-]?[\d,]+)", message).group(1).replace(",", ""))
        assert sum(credits) - sum(debits) == net, (credits, debits, net)
        assert net == int(econ["net"]), (net, econ["net"])
        assert "treasury" in message and "Net" in message, message

    def test_the_lever_down_reproduces_the_sentence_that_does_not_sum(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_INCOME_SENTENCE_SUMS", False)
        message = ask(client, world, "what is my income")
        m = re.search(r"yield ([\d,]+) and trade ([\d,]+); the army costs ([\d,]+)\. Net \+?([\d,]+)", message)
        assert m, message
        income, trade, army, net = (int(x.replace(",", "")) for x in m.groups())
        assert income + trade - army != net, message

    def test_every_non_zero_component_is_named(self, shipped):
        _, world = shipped
        from backend.game_logic.ledger import NET_GOLD_COMPONENTS, _build_economy
        econ = _build_economy(world, "France")
        answer = QD._answer_treasury(world, "France")
        for key in NET_GOLD_COMPONENTS:
            value = int(econ.get(key) or 0)
            if value:
                assert f"{abs(value):,}" in answer, (key, value, answer)


# ═══════════════════════════════════════════════════════════════════════════
# DESK-7 — who is winning reads the banner
# ═══════════════════════════════════════════════════════════════════════════

class TestWhoIsWinningReadsTheBanner:
    def test_the_coalition_is_one_war_level_score(self, shipped):
        client, world = shipped
        message = ask(client, world, "who is winning")
        assert "the Third Coalition (Britain, Austria and Russia) +0" in message, message
        assert message.count("evenly matched") == 1, message

    def test_a_court_with_no_marshal_on_the_board_is_still_named(self, shipped):
        client, world = shipped
        court = next(n for n in world.get_active_nations()
                     if n != "France"
                     and not any(m.nation == n for m in world.marshals.values())
                     and world.get_diplomatic_state("France", n) == "PEACE")
        world.diplomatic_states[world._make_diplo_key("France", court)] = "WAR"
        world.invalidate_bloc_members_cache()
        message = ask(client, world, "who is winning")
        assert QD._court(world, court) in message, (court, message)

    def test_the_lever_down_lists_the_courts_with_marshals(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "WHO_IS_WINNING_READS_THE_BANNER", False)
        message = ask(client, world, "who is winning")
        assert "Third Coalition" not in message and message.count("evenly matched") == 3, message

    def test_the_rows_are_the_banner_s_own(self, shipped):
        _, world = shipped
        from backend.game_logic.war_status import build_active_wars
        rows = build_active_wars(world)["wars"]
        answer = QD._answer_winning(world, "France")
        for row in rows:
            assert f"{int(row['war_score']):+d}" in answer, (row["war_score"], answer)


# ═══════════════════════════════════════════════════════════════════════════
# DESK-8 / DESK-14 — the router points at the right screen
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRouterPointsRight:
    def test_the_war_effort_is_not_a_fort(self):
        assert MetaExecutor.question_topic("how is the war effort") == "courts"
        assert MetaExecutor.question_topic("what is our exhaustion") == "courts"

    def test_allies_have_a_screen(self):
        assert MetaExecutor.question_topic("who are my allies") == "courts"

    def test_the_purse_still_routes(self):
        assert MetaExecutor.question_topic("how much gold do we have") == "economy"
        assert MetaExecutor.question_topic("can I build a fort") == "economy"

    def test_the_lever_down_reproduces_the_substring_pointer(self, monkeypatch):
        monkeypatch.setattr(MetaExecutor, "THE_ROUTER_READS_WHOLE_WORDS", False)
        assert MetaExecutor.question_topic("how is the war effort") == "economy"

    def test_the_shrug_names_the_screen(self, shipped):
        client, world = shipped
        message = ask(client, world, "what are the terms of the alliance with Spain")
        assert "Diplomatic Ledger" in message, message


# ═══════════════════════════════════════════════════════════════════════════
# DESK-9 / DESK-13 / DESK-16 / DESK-6 / AAR-19 — the counsel
# ═══════════════════════════════════════════════════════════════════════════

def _refused(data):
    if data.get("pending_objection") or data.get("awaiting_response"):
        return False
    return data.get("success") is False


class TestTheCounsel:
    def test_at_zero_actions_the_counsel_names_end_turn(self, shipped):
        client, world = shipped
        world.actions_remaining = 0
        message = ask(client, world, "what can I do")
        lines = [ln.strip() for ln in message.splitlines()]
        assert COUNSEL.END_TURN_LINE in lines, message
        for verb in (", attack ", ", march to ", ", fortify", ", drill"):
            assert verb not in message, message
        assert "recruit infantry" in message, message   # the purse's actions remain

    def test_the_action_point_lever_down_offers_the_refused_orders(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(COUNSEL, "THE_COUNSEL_READS_THE_ACTION_POINTS", False)
        world.actions_remaining = 0
        message = ask(client, world, "what can I do")
        assert ", attack " in message and "end turn" not in message, message

    def test_with_no_administrative_action_the_purse_is_silent(self, shipped):
        _, world = shipped
        world.admin_actions_remaining = 0
        assert COUNSEL.economy_counsel(world, "France", limit=3) == []

    def test_every_offered_order_is_taken_at_the_wire(self, shipped, monkeypatch):
        """CX-R2's rule for the counsel: each line `what can I do` prints on
        the boot is sent, on a fresh boot each, and none is refused."""
        _, world = shipped
        lines = COUNSEL.what_can_i_do(world, "France", limit=6)
        assert len(lines) >= 4, lines
        for line in lines:
            order = line.split(" — ")[0].strip()
            M._reset_world_state()
            monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
            client = TestClient(M.app)
            data = post(client, order)
            assert not _refused(data), (order, data.get("message"))

    def test_a_drill_the_executor_refuses_is_not_offered(self, shipped):
        _, world = shipped
        from backend.commands.tactical_executor import drill_refusal
        assert drill_refusal(world, world.get_marshal("Ney")) != ("", "")
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert "Ney, drill" not in lines, lines
        for line in lines:
            if line.endswith(", drill"):
                marshal = world.get_marshal(line[:-len(", drill")])
                assert drill_refusal(world, marshal) == ("", ""), line

    def test_the_refusal_lever_down_offers_the_drill_beside_the_enemy(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(COUNSEL, "THE_COUNSEL_READS_THE_REFUSALS", False)
        monkeypatch.setattr(COUNSEL, "THE_COUNSEL_SPREADS_THE_ORDERS", False)
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert "Ney, drill" in lines, lines

    def test_works_are_not_offered_to_an_engaged_corps(self, shipped):
        """The sweep's second INERT: with the whole roster free, the engaged
        Ney was consumed by the attack line and the fortify loop stopped at
        Davout before it reached him. Staged so Ney is the ONLY free corps —
        the refusal is then the one thing between him and a fortify line."""
        _, world = shipped
        from backend.commands.tactical_executor import fortify_refusal
        mack = world.get_marshal("Mack")
        ney = world.get_marshal("Ney")
        ney.location = mack.location
        for other in world.get_player_marshals():
            if other.name != "Ney":
                other.drilling_locked = True
        assert [m.name for m in world.get_player_marshals()
                if COUNSEL._is_free_to_order(m)] == ["Ney"]
        assert fortify_refusal(world, ney) != ("", "")
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert "Ney, attack Mack" in lines, lines
        assert "Ney, fortify" not in lines, lines

    def test_a_fortify_from_neutral_needs_two_actions(self, shipped):
        _, world = shipped
        world.actions_remaining = 1
        for m in world.get_player_marshals():
            assert getattr(m.stance, "name", "") == "NEUTRAL"
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert not any(line.endswith(", fortify") for line in lines), lines

    def test_the_orders_are_spread_across_the_army(self, shipped):
        _, world = shipped
        lines = COUNSEL.military_counsel(world, "France", limit=4)
        names = {line.split(",")[0] for line in lines}
        assert len(names) >= 3, lines
        assert lines[0] == "Ney, attack Mack", lines   # the first line the doors quote

    def test_the_spread_lever_down_names_one_man(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(COUNSEL, "THE_COUNSEL_SPREADS_THE_ORDERS", False)
        lines = COUNSEL.military_counsel(world, "France", limit=4)
        names = {line.split(",")[0] for line in lines}
        assert names == {"Ney"}, lines

    def test_a_marshal_who_moved_this_turn_is_not_marched_again(self, shipped):
        _, world = shipped
        for m in world.get_player_marshals():
            m.moved_this_turn = True
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert not any(", march to " in line for line in lines), lines

    def test_the_march_closes_on_the_enemy(self, shipped):
        _, world = shipped
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        march = next(line for line in lines if ", march to " in line)
        name, destination = march.split(", march to ")
        marshal = world.get_marshal(name)
        region = world.get_region(marshal.location)
        enemy_places = {e.location for e in world.get_visible_enemies("France")}
        chosen = min(world.get_distance(destination, p) for p in enemy_places)
        for other in region.adjacent_regions:
            if COUNSEL._move_would_be_refused(world, marshal, other):
                continue
            assert min(world.get_distance(other, p) for p in enemy_places) >= chosen, (march, other)

    def test_the_free_to_order_clause_reads_the_real_flags(self, shipped):
        _, world = shipped
        ney = world.get_marshal("Ney")
        ney.drilling_locked = True
        assert COUNSEL._is_free_to_order(ney) is False
        ney.drilling_locked = False
        ney.drilling = True
        assert COUNSEL._is_free_to_order(ney) is False
        ney.drilling = False
        ney.is_drilling = True   # the flag no Marshal has — DESK-6's dead clause
        assert COUNSEL._is_free_to_order(ney) is True

    def test_no_attack_across_a_shut_crossing_is_offered(self, shipped):
        _, world = shipped
        from backend.game_logic.naval import crossing_check_reach
        ney = world.get_marshal("Ney")
        moore = world.get_marshal("Moore")
        ney.location = "Normandy"
        see(world, moore.location)
        assert moore.location in world.get_region("Normandy").adjacent_regions
        verdict = crossing_check_reach(world, "France", "Normandy", moore.location, ney.strength)
        assert not verdict.get("allowed"), verdict
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert not any("attack Moore" in line for line in lines), lines

    def test_the_crossing_lever_down_offers_the_shut_attack(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(COUNSEL, "THE_COUNSEL_READS_THE_CROSSING", False)
        ney = world.get_marshal("Ney")
        moore = world.get_marshal("Moore")
        ney.location = "Normandy"
        see(world, moore.location)
        lines = COUNSEL.military_counsel(world, "France", limit=8)
        assert "Ney, attack Moore" in lines, lines

    def test_the_levy_line_is_the_quote(self, shipped):
        _, world = shipped
        quote = cheapest_quote(world, "infantry")
        line = COUNSEL._levy_terms(world, "France")
        assert line == (f"recruit infantry in {quote['where']} — {int(quote['price']):,}g "
                        f"for {int(quote['amount']):,} men under {quote['recipient']}"), line


# ═══════════════════════════════════════════════════════════════════════════
# DESK-15 — our own captured and fallen
# ═══════════════════════════════════════════════════════════════════════════

class TestOurOwnCapturedAndFallen:
    def test_a_prisoner_is_answered(self, shipped):
        client, world = shipped
        world.get_marshal("Ney").captured_by = "Austria"
        message = ask(client, world, "where is Ney")
        assert "prisoner of Austria" in message, message

    @pytest.mark.parametrize("q", ["where is Ney", "what is Ney doing",
                                   "how many men does Ney have"])
    def test_a_fallen_marshal_is_answered_in_the_first_person(self, shipped, q):
        client, world = shipped
        ney = world.get_marshal("Ney")
        assert world.destroy_marshal(ney, cause="battle") is True
        message = ask(client, world, q)
        assert "Marshal Ney fell at Rhineland on turn 1" in message, (q, message)
        assert "commissioned in his place" in message, message
        assert SHRUG not in message, message

    def test_a_dismissed_marshal_is_not_mourned(self, shipped):
        client, world = shipped
        world.destroy_marshal(world.get_marshal("Ney"), cause="dismissed", log=False)
        message = ask(client, world, "where is Ney")
        assert "dismissed from the service" in message, message
        assert "fell" not in message, message

    def test_the_lever_down_is_the_shrug(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "OUR_OWN_FALLEN_ARE_ANSWERED", False)
        world.destroy_marshal(world.get_marshal("Ney"), cause="battle")
        message = ask(client, world, "where is Ney")
        assert SHRUG in message, message

    def test_a_foreign_tombstone_keeps_the_enemy_arm(self, shipped):
        _, world = shipped
        assert QD.own_fallen_names(world) == []
        world.destroy_marshal(world.get_marshal("Mack"), cause="battle")
        assert "Mack" not in QD.own_fallen_names(world)


# ═══════════════════════════════════════════════════════════════════════════
# DESK-11 / DESK-12
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMusterPrintsNames:
    def test_the_what_if_names_the_man(self, shipped):
        client, world = shipped
        message = ask(client, world, "what if I attack Archduke John")
        assert "Archduke John" in message and "ArchdukeJohn" not in message, message


class TestTheDeadHalf:
    def test_the_at_war_pattern_has_no_peace_half(self):
        pattern = next(p for k, p in QD._WIDE_KINDS if k == "at_war").pattern
        assert "peace" not in pattern, pattern

    def test_the_at_war_answer_still_reports_a_peace(self, shipped):
        client, world = shipped
        message = ask(client, world, "am I at war with Prussia")
        assert "No, Sire" in message and "Peace" in message, message


# ═══════════════════════════════════════════════════════════════════════════
# AAR-23 — the insist arm names its price
# ═══════════════════════════════════════════════════════════════════════════

class TestTheInsistArmNamesItsPrice:
    def test_the_terms_are_the_executor_s_figure(self, shipped):
        _, world = shipped
        from backend.models.marshal import Stance
        murat = world.get_marshal("Murat")
        assert murat.stance == Stance.NEUTRAL
        assert TE.insist_terms(world, murat, "fortify") == (2, "he must first go defensive")
        murat.stance = Stance.DEFENSIVE
        assert TE.insist_terms(world, murat, "fortify") == (1, "")
        assert TE.insist_terms(world, murat, "attack") == (1, "")

    def test_the_objection_payload_carries_the_price(self, shipped, monkeypatch):
        client, world = shipped
        # The objection's mood variance is the ONE random roll in the V2a
        # triggers (`apply_mood_variance`'s own docstring: mock it); pinned
        # to identity so Murat's evaluated concern is the concern that fires.
        monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
        data = post(client, "Murat, fortify")
        assert data.get("pending_objection") is True, data.get("message")
        objection = data.get("objection") or {}
        assert objection.get("insist_ap_cost") == 2, objection
        assert objection.get("insist_note") == "he must first go defensive", objection
        assert "Insisting costs 2 actions" in str(data.get("message")), data.get("message")
        assert int(world.actions_remaining) == 4   # nothing charged yet

    def test_the_lever_down_leaves_the_payload_bare(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(TE, "THE_INSIST_ARM_NAMES_ITS_PRICE", False)
        monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
        data = post(client, "Murat, fortify")
        assert data.get("pending_objection") is True
        objection = data.get("objection") or {}
        assert "insist_ap_cost" not in objection and "insist_note" not in objection
        assert "Insisting costs" not in str(data.get("message"))

    def test_the_client_renders_the_price_on_the_button(self):
        import pathlib
        src = pathlib.Path("godot-client/project-sovereign/scripts/objection_dialog.gd").read_text(encoding="utf-8")
        assert 'objection_data.has("insist_note")' in src
        assert "Proceed as Ordered (%d AP" in src


# ═══════════════════════════════════════════════════════════════════════════
# AAR-29 — Berthier suggests only orders the game takes
# ═══════════════════════════════════════════════════════════════════════════

class TestBerthierSuggestsOnlyRealOrders:
    AAR = ('Sire, I did not follow. Perhaps "Berthier, conduct a diplomatic '
           'mission to Bennigsen in Hungary" or "Berthier, propose white peace '
           'with Kutuzov in Bohemia"?')

    def test_an_invented_order_is_replaced_by_the_counsel(self, shipped):
        _, world = shipped
        gs = M.get_llm_game_state()
        cleaned = M.parser.llm.sanitise_berthier_reply(self.AAR, gs)
        assert "Bennigsen" not in cleaned and "white peace" not in cleaned, cleaned
        counsel = COUNSEL.what_can_i_do(world, "France", limit=4)
        assert counsel[0] in cleaned, cleaned

    def test_a_real_order_is_left_alone(self, shipped):
        _, world = shipped
        gs = M.get_llm_game_state()
        reply = 'Forgive me, Sire. Perhaps "Ney, attack Mack"?'
        assert M.parser.llm.sanitise_berthier_reply(reply, gs) == reply

    def test_a_cabinet_sentence_is_never_offered_to_type(self, shipped):
        _, world = shipped
        gs = M.get_llm_game_state()
        assert M.parser.llm._quoted_order_is_taken("propose alliance with Prussia", gs) is False
        assert M.parser.llm._quoted_order_is_taken("Ney, attack Mack", gs) is True
        assert M.parser.llm._quoted_order_is_taken("conduct a review of the guns", gs) is False

    def test_the_lever_down_returns_the_reply_untouched(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(type(M.parser.llm), "BERTHIER_SUGGESTS_ONLY_ORDERS_THE_GAME_TAKES", False)
        gs = M.get_llm_game_state()
        assert M.parser.llm.sanitise_berthier_reply(self.AAR, gs) == self.AAR

    # The authored IQ-9 recovery cassette was stamped against the pre-slice
    # prompt; the hook's drift pin (`TestCassetteHygiene`) caught the counsel
    # block and the cassette was RE-STAMPED. This pin keeps the attribution:
    # the lever down reproduces the pre-slice fingerprint byte for byte, the
    # lever up reproduces the re-stamped one — so the re-stamp is this block
    # and nothing else.
    PRE_CRT7_RECOVERY_PROMPT_SHA256 = (
        "582b90ffac45f4b90d3240c9a7129fa16e1a6c561acbdb69f6307de646400a34")

    @pytest.mark.parametrize("lever", [False, True])
    def test_the_recovery_cassette_drift_is_this_block_alone(self, monkeypatch, lever):
        import backend.ai.prompt_builder as PB
        from backend.ai.parser_eval import build_llm_game_state, build_world
        from tests._parser_replay import (armed_parser, body_kind, fingerprint,
                                          load_all_cassettes, load_manifest)
        monkeypatch.setattr(PB, "THE_RECOVERY_PROMPT_NAMES_THE_COUNSEL", lever)
        cassettes = load_all_cassettes()
        entry = cassettes["gibberish-berthier.recovery"]
        world = build_world(entry["world"])
        gs = build_llm_game_state(world)
        parser, replay = armed_parser(list(cassettes.values()), entry["world"],
                                      load_manifest())
        parser.llm.generate_berthier_recovery(entry["utterance"], gs, {},
                                              skip_llm=False)
        calls = getattr(replay, "calls", None)
        if calls is None:
            calls = replay.messages.calls
        body = [c for c in calls if body_kind(c) != "parse"][-1]
        live = fingerprint(body)["prompt_sha256"]
        expected = (entry["request"]["prompt_sha256"] if lever
                    else self.PRE_CRT7_RECOVERY_PROMPT_SHA256)
        assert live == expected

    def test_the_prompt_hands_the_model_the_counsel(self, shipped):
        _, world = shipped
        from backend.ai.prompt_builder import build_berthier_recovery_prompt
        gs = M.get_llm_game_state()
        _system, user = build_berthier_recovery_prompt("flibbertigibbet the guns", gs)
        assert "Orders the board takes this morning" in user, user
        counsel = COUNSEL.what_can_i_do(world, "France", limit=4)
        assert f"- {counsel[0]}" in user, user
        assert "never invent a commander" in user


# ═══════════════════════════════════════════════════════════════════════════
# AAR-31 — the objection names its concern
# ═══════════════════════════════════════════════════════════════════════════

class TestTheObjectionNamesItsConcern:
    def test_a_cautious_march_objection_names_the_road(self, shipped):
        _, world = shipped
        from backend.commands.objection_v2 import ConcernLevel
        davout = world.get_marshal("Davout")
        assert davout.personality == "cautious"
        line = M.executor._strategic._generate_objection_message(
            davout, "move_to", {"target": "Provence"}, ConcernLevel.MODERATE, "firm")
        assert "Provence" in line and "enemy country" in line, line
        assert "I have concerns about this order" not in line

    def test_the_default_still_names_the_order(self, shipped):
        _, world = shipped
        from backend.commands.objection_v2 import ConcernLevel
        davout = world.get_marshal("Davout")
        line = M.executor._strategic._generate_objection_message(
            davout, "hold", {"target": "Swabia"}, ConcernLevel.MODERATE, "firm")
        assert "hold at Swabia" in line, line
        assert "I have concerns about this order" not in line

    def test_the_lever_down_is_the_reasonless_line(self, shipped, monkeypatch):
        _, world = shipped
        from backend.commands.objection_v2 import ConcernLevel
        monkeypatch.setattr(SE, "THE_OBJECTION_NAMES_ITS_CONCERN", False)
        line = M.executor._strategic._generate_objection_message(
            world.get_marshal("Davout"), "move_to", {"target": "Provence"},
            ConcernLevel.MODERATE, "firm")
        assert "I have concerns about this order" in line, line

    def test_the_support_arm_is_untouched(self, shipped):
        _, world = shipped
        from backend.commands.objection_v2 import ConcernLevel
        line = M.executor._strategic._generate_objection_message(
            world.get_marshal("Davout"), "support", {}, ConcernLevel.MODERATE, "firm")
        assert "enemy country" in line
