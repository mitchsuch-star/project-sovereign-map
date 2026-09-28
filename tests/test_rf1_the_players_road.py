"""SR-5r RF-1 — "The player's road" (`docs/REFORMS_SPEC.md` §2, §5, §8 "The
words", §11 T4/T5; gate record §0 RULED, readings §0.1 CONFIRMED September 27,
2026 — R1 the Staff pays upkeep, R5 laws lapse before rentes, largest first,
R8 "The Arrears").

RF-1 lands the lifecycle on top of RF-0's store:
  * `enact_law` / `repeal_law` through the shared executor (CLAUDE.md's
    new-action checklist) — ONE predicate refuses free and names why
    (`reforms.law_refusal` / `repeal_refusal`), ONE mutation charges exactly
    the quoted price (`reforms.enact_law`, R8 shown = applied);
  * the words — `enact the Staff`, the authored name, accents folded; a
    QUESTION or a hedge is answered, never enacted; an order put to a marshal
    is refused in words, free; the minister and the Emperor are decoration;
  * the "Laws" Net component through the EC-U2 recipe;
  * the lapse loop, BEFORE ESP-4's rente default (R5) — the largest upkeep
    first, the charge refunded and folded out of the applied record (Net ==
    the measured change in the chest), the Arrears clock started (R8);
  * the Staff at the player's refill AND at the AI restore (GR5, §5);
  * `law_enacted` / `law_repealed` / `law_lapsed` in the campaign log.
Lever `reforms.THE_STATE_HAS_LAWS` — down, the state has no laws.
"""
import contextlib
import io

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import campaign_log as CL
from backend.game_logic import reforms as R
from backend.game_logic.ledger import NET_GOLD_COMPONENTS, _build_economy
from backend.models.world_state import WorldState
from tests import _chip_census as C

STAFF_ID = "grand_quartier_general"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def post(client, command, *, answer_the_council=True):
    """RF-4a (Sept 27, 2026): an enactment is quoted first — the Council of
    State's confirm on the clarification channel (REFORMS_SPEC §8a, pinned in
    `test_rf4a_the_laws_tab.py`). This helper answers that quote "yes", so
    RF-1's pins keep reading the enactment itself; a refusal is never quoted
    and comes straight back."""
    with _quiet():
        r = client.post("/command", json={"command": command}).json()
        if answer_the_council and r.get("law_confirm"):
            r = client.post("/command", json={"command": "yes"}).json()
        return r


def staff(world, nation="France"):
    return next(r for r in R.deck(world, nation) if R.is_staff(r))


def _events(world, etype):
    return [e for e in world.event_log if e.get("type") == etype]


def _add_law(world, nation, law_id, upkeep, price=1000, currency="gold"):
    """A test-authored second law (RF-2 authors the real catalogue): no
    effect clause, so it touches no seam — it only bills and lapses."""
    row = {"id": law_id, "name": f"The {law_id.replace('_', ' ').title()}",
           "date": "1806", "currency": currency, "price": price,
           "upkeep": upkeep, "effects": [], "says": "test law"}
    world.reforms[nation].append(row)
    return row


# ═══════════════════════════════ ENACT ════════════════════════════════════════

class TestEnact:

    def test_enact_the_staff_charges_its_price_and_one_admin_action(self, world, client):
        world.nation_gold["France"] = 12000
        admin = world.admin_actions_remaining
        military = world.actions_remaining
        r = post(client, "enact the Staff")
        assert r["success"] is True, r
        assert world.nation_gold["France"] == 3000
        assert world.admin_actions_remaining == admin - 1
        assert world.actions_remaining == military, "an act of state costs no order"
        row = staff(world)
        assert row["enacted_turn"] == world.current_turn
        assert "9,000 gold" in r["message"] and "300 gold a turn" in r["message"]

    def test_the_enactment_is_logged_with_what_was_paid(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        logged = _events(world, "law_enacted")
        assert len(logged) == 1
        ev = logged[0]
        assert ev["nation"] == "France" and ev["law"] == STAFF_ID
        assert ev["gold"] == 9000 and ev["authority"] == 0
        assert ev["upkeep"] == 300 and ev["restored"] is False

    def test_the_spend_is_counted_in_the_turn_summary(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        assert world.gold_spent_this_turn.get("France") == 9000

    @pytest.mark.parametrize("words", [
        "enact the Grand Quartier General",
        "enact the Grand Quartier Général",
        "enact grand quartier general",
        "enact the Quartier General",          # a word short: one law holds it
        "Talleyrand, enact the Staff",
        "Sire, enact the staff",
    ])
    def test_the_law_is_named_many_ways(self, world, client, words):
        world.nation_gold["France"] = 12000
        r = post(client, words)
        assert r["success"] is True, (words, r.get("message"))
        assert R.is_in_force(staff(world))

    def test_a_price_the_chest_cannot_pay_is_refused_free(self, world, client):
        world.nation_gold["France"] = 8999
        admin = world.admin_actions_remaining
        r = post(client, "enact the Staff")
        assert r["success"] is False
        assert world.nation_gold["France"] == 8999
        assert world.admin_actions_remaining == admin
        assert not R.is_in_force(staff(world))
        # shown = applied: the executor's refusal IS the predicate's text
        world.admin_actions_remaining = admin
        assert R.law_refusal(world, "France", STAFF_ID) in r["message"]
        assert "The Grand Quartier Général costs 9,000 gold; the treasury holds 8,999." \
            in r["message"]

    def test_already_in_force_is_refused_free(self, world, client):
        world.nation_gold["France"] = 30000
        post(client, "enact the Staff")
        gold = world.nation_gold["France"]
        admin = world.admin_actions_remaining
        r = post(client, "enact the Staff")
        assert r["success"] is False and "already in force" in r["message"]
        assert world.nation_gold["France"] == gold
        assert world.admin_actions_remaining == admin

    def test_an_unknown_law_lists_the_courts_laws(self, world, client):
        # ⚑ RF-2 (Sept 27, 2026): this pin named "the Code Abroad" as a law
        # France does not have — RF-2 authored it. The Concordat (1801) is
        # not a law of state here.
        world.nation_gold["France"] = 30000
        admin = world.admin_actions_remaining
        r = post(client, "enact the Concordat")
        assert r["success"] is False
        assert "no law called 'Concordat'" in r["message"]
        assert "the Grand Quartier Général (9,000 gold)" in r["message"]
        assert world.admin_actions_remaining == admin

    def test_no_admin_action_left_is_refused_free(self, world, client):
        world.nation_gold["France"] = 30000
        world.admin_actions_remaining = 0
        r = post(client, "enact the Staff")
        assert r["success"] is False
        assert world.nation_gold["France"] == 30000
        assert not R.is_in_force(staff(world))

    def test_the_predicate_refuses_the_admin_arm_by_itself(self, world):
        """The executor's pre-gate answers first on the typed road; the
        predicate's own admin arm is what the AI rung (its own budget) and the
        chip read — pinned without the pre-gate."""
        world.nation_gold["France"] = 30000
        assert "admin action" in R.law_refusal(world, "France", STAFF_ID,
                                                admin_actions=0)
        assert R.law_refusal(world, "France", STAFF_ID, admin_actions=1) == ""

    def test_lever_down_the_state_has_no_laws(self, world, client, monkeypatch):
        monkeypatch.setattr(R, "THE_STATE_HAS_LAWS", False)
        world.nation_gold["France"] = 30000
        r = post(client, "enact the Staff")
        assert r["success"] is False
        assert "no laws" in r["message"]
        assert world.nation_gold["France"] == 30000


# ═══════════════════════════════ THE WORDS ════════════════════════════════════

class TestTheWords:

    @pytest.mark.parametrize("words", [
        "should I enact the Staff?",
        "can we repeal the staff",
        "what laws can I enact?",
        "perhaps enact the staff",
        "Talleyrand, should we enact the Staff?",
    ])
    def test_a_question_or_a_hedge_is_answered_and_nothing_is_enacted(
            self, world, client, words):
        world.nation_gold["France"] = 30000
        admin = world.admin_actions_remaining
        r = post(client, words)
        assert r["success"] is True
        assert "The laws of state, Sire." in r["message"]
        assert "Nothing has been enacted." in r["message"]
        assert world.nation_gold["France"] == 30000
        assert world.admin_actions_remaining == admin
        assert not R.is_in_force(staff(world))

    def test_the_answer_quotes_the_one_price(self, world, client):
        world.nation_gold["France"] = 30000
        r = post(client, "what laws can I enact?")
        assert "The Grand Quartier Général: 9,000 gold, then 300 gold a turn" in r["message"]
        assert "ready to enact" in r["message"]

    def test_the_answer_names_the_arrears_after_a_lapse(self, world, client):
        row = staff(world)
        row["lapsed_turn"] = world.current_turn
        world.nation_gold["France"] = 30000
        r = post(client, "what laws can I enact?")
        assert "4,500 gold and 300 gold in arrears" in r["message"]
        assert "disperses in 9 turns" in r["message"]

    @pytest.mark.parametrize("words,verb", [
        ("Ney, enact the Staff", "enact"),
        ("Ney enact the Staff", "enact"),
        ("Davout, repeal the Staff", "repeal"),
    ])
    def test_an_order_put_to_a_marshal_is_refused_in_words_free(
            self, world, client, words, verb):
        world.nation_gold["France"] = 30000
        if verb == "repeal":
            R.enact_law(world, "France", staff(world))
        gold = world.nation_gold["France"]
        admin = world.admin_actions_remaining
        r = post(client, words)
        assert r["success"] is False
        assert f"The laws are the Emperor's to {verb}, Sire" in r["message"]
        assert "commands a corps, not the state" in r["message"]
        assert world.nation_gold["France"] == gold
        assert world.admin_actions_remaining == admin

    def test_the_emperor_himself_is_not_misaddressed(self, world, client):
        world.nation_gold["France"] = 30000
        r = post(client, "Napoleon, enact the Staff")
        assert r["success"] is True, r.get("message")
        assert R.is_in_force(staff(world))

    def test_a_parse_that_names_the_emperor_is_not_refused(self, world):
        """The typed road strips the Emperor as decoration, so the executor
        never sees him there (measured). A LIVE-model parse may still name
        the sovereign marshal: the executor's exemption is what keeps his own
        act of state from being refused as a marshal's."""
        world.nation_gold["France"] = 30000
        sovereign = next(m.name for m in world.marshals.values()
                         if getattr(m, "is_sovereign", False))
        with _quiet():
            result = M.executor._reforms._execute_enact_law(
                {"action": "enact_law", "marshal": sovereign, "target": "the Staff",
                 "confirmed": True},
                M.game_state)
        assert result["success"] is True, result.get("message")
        assert R.is_in_force(staff(world))
        with _quiet():
            refused = M.executor._reforms._execute_repeal_law(
                {"action": "repeal_law", "marshal": "Ney", "target": "the Staff"},
                M.game_state)
        assert refused["success"] is False
        assert "Marshal Ney commands a corps" in refused["message"]

    @pytest.mark.parametrize("words", [
        "enact the Staff in three turns",
        "enact the staff, perhaps",
    ])
    def test_a_trailing_hedge_or_deferral_is_answered(self, world, client, words):
        """The law route's own hedge guard (the Congress's rule): CRT-3's
        hedge rule reads a LEADING hedge ("perhaps enact …"); a verb at the
        head with the hedge or the deferral behind it is this guard's alone."""
        world.nation_gold["France"] = 30000
        r = post(client, words)
        assert "The laws of state, Sire." in r["message"], r.get("message")
        assert not R.is_in_force(staff(world))
        assert world.nation_gold["France"] == 30000

    def test_the_answer_puts_a_refusal_in_its_place(self, world, client):
        world.nation_gold["France"] = 800
        r = post(client, "what laws can I enact?")
        assert ("then 300 gold a turn — the Grand Quartier Général costs 9,000 "
                "gold; the treasury holds 800.") in r["message"], r["message"]

    def test_a_negated_order_is_refused(self, world, client):
        world.nation_gold["France"] = 30000
        r = post(client, "don't enact the Staff")
        assert r["success"] is False
        assert not R.is_in_force(staff(world))
        assert world.nation_gold["France"] == 30000

    def test_the_parse_carries_no_marshal_and_no_standing_order(self, world):
        with _quiet():
            parsed = M.parser.parse("enact the Staff", M.get_llm_game_state(),
                                    world=world)
        command = parsed.get("command") or {}
        assert command.get("action") == "enact_law"
        assert not command.get("marshal")
        assert not parsed.get("strategic_type")

    def test_the_verbs_are_order_words_for_the_addressee_rule(self):
        from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
        assert {"enact", "reenact", "repeal"} <= set(ROUTED_ORDER_WORDS)


# ═══════════════════════════════ REPEAL ═══════════════════════════════════════

class TestRepeal:

    def test_repeal_takes_one_admin_action_and_refunds_nothing(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        gold = world.nation_gold["France"]
        admin = world.admin_actions_remaining
        r = post(client, "repeal the Staff")
        assert r["success"] is True, r
        assert world.nation_gold["France"] == gold, "nothing is refunded (R4)"
        assert world.admin_actions_remaining == admin - 1
        row = staff(world)
        assert "enacted_turn" not in row
        assert "lapsed_turn" not in row, "a repeal never earns the Arrears (R8)"
        assert "full price (9,000 gold)" in r["message"]
        logged = _events(world, "law_repealed")
        assert logged and logged[-1]["law"] == STAFF_ID

    def test_a_law_not_in_force_cannot_be_repealed(self, world, client):
        admin = world.admin_actions_remaining
        r = post(client, "repeal the Staff")
        assert r["success"] is False and "not in force" in r["message"]
        assert world.admin_actions_remaining == admin

    def test_a_repealed_law_costs_its_full_price_again(self, world, client):
        world.nation_gold["France"] = 30000
        post(client, "enact the Staff")
        post(client, "repeal the Staff")
        world.admin_actions_remaining = 2
        before = world.nation_gold["France"]
        r = post(client, "enact the Staff")
        assert r["success"] is True
        assert before - world.nation_gold["France"] == 9000

    def test_the_repeal_predicate_reads_the_given_budget(self, world):
        R.enact_law(world, "France", staff(world))
        assert "admin action" in R.repeal_refusal(world, "France", STAFF_ID,
                                                  admin_actions=0)
        assert R.repeal_refusal(world, "France", STAFF_ID, admin_actions=1) == ""


# ═══════════════════════════════ THE STAFF (T5) ═══════════════════════════════

class TestTheStaffAtTheRefill:

    def test_the_fifth_action_arrives_at_the_next_refill_not_before(self, world, client):
        world.nation_gold["France"] = 12000
        before = world.max_actions_per_turn
        post(client, "enact the Staff")
        assert world.max_actions_per_turn == before, "not this turn (§2.1)"
        with _quiet():
            world.advance_turn()
        assert world.max_actions_per_turn == before + 1
        assert world.actions_remaining == before + 1

    def test_the_staff_is_derived_never_written_into_bonus_actions(self, world):
        R.enact_law(world, "France", staff(world))
        assert int(getattr(world, "bonus_actions", 0) or 0) == 0
        assert world.calculate_max_actions() == 5

    def test_it_stacks_with_the_administrative_role(self, world):
        world.bonus_actions = 1
        R.enact_law(world, "France", staff(world))
        assert world.calculate_max_actions() == 6

    def test_a_repeal_takes_it_away_at_the_next_refill(self, world):
        row = staff(world)
        R.enact_law(world, "France", row)
        with _quiet():
            world.advance_turn()
        assert world.max_actions_per_turn == 5
        R.repeal_law(world, "France", row)
        with _quiet():
            world.advance_turn()
        assert world.max_actions_per_turn == 4

    def test_an_ai_court_gets_the_same_fifth_action_gr5(self, world):
        base = world.base_nation_actions["Austria"]
        world.nation_gold["Austria"] = 50000
        R.enact_law(world, "Austria", staff(world, "Austria"))
        with _quiet():
            world.advance_turn()
        assert world.nation_actions["Austria"] == base + 1

    def test_an_ai_courts_lapse_takes_it_at_the_following_refill(self, world):
        base = world.base_nation_actions["Austria"]
        row = staff(world, "Austria")
        R.enact_law(world, "Austria", row)
        world.nation_gold["Austria"] = -60000
        with _quiet():
            world.advance_turn()          # the refill counts it; then it lapses
        assert row.get("lapsed_turn") == world.current_turn
        assert world.nation_actions["Austria"] == base + 1
        with _quiet():
            world.advance_turn()          # the following refill does not
        assert world.nation_actions["Austria"] == base


# ═══════════════════════════════ THE NET LINE ═════════════════════════════════

class TestTheLawsLine:

    def test_laws_is_a_signed_net_component(self):
        assert NET_GOLD_COMPONENTS["laws"] == -1

    def test_the_income_phase_bills_the_laws_in_force(self, world):
        assert world.calculate_turn_income("France")["laws"] == 0
        R.enact_law(world, "France", staff(world))
        assert world.calculate_turn_income("France")["laws"] == 300

    def test_the_bill_reaches_the_chest(self, world):
        world.nation_gold["France"] = 20000
        with _quiet():
            twin = WorldState.from_dict(world.to_dict())
        R.enact_law(world, "France", staff(world))
        world.nation_gold["France"] = 20000
        with _quiet():
            world.advance_turn()
            twin.advance_turn()
        applied = world._income_phase_results["France"]
        assert applied["laws"] == 300
        assert twin._income_phase_results["France"]["laws"] == 0
        assert (twin._income_phase_results["France"]["net"]
                - applied["net"]) == 300

    def test_the_ledger_net_is_the_signed_sum_with_laws(self, world):
        R.enact_law(world, "France", staff(world))
        world.nation_gold["France"] = 20000
        with _quiet():
            world.advance_turn()
        econ = _build_economy(world, "France",
                              income_data=world._income_phase_results["France"])
        assert econ["laws"] == 300
        total = sum(sign * int(econ.get(k, 0))
                    for k, sign in NET_GOLD_COMPONENTS.items())
        assert total == int(econ["net"])

    def test_the_end_turn_banner_prints_the_laws_line(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        world.nation_gold["France"] = 20000
        r = post(client, "end turn")
        assert "| Laws: -300g" in r["message"], r["message"][-600:]

    def test_no_laws_line_when_none_is_in_force(self, world, client):
        r = post(client, "end turn")
        assert "Laws:" not in r["message"]

    def test_the_treasury_report_names_each_law(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        r = post(client, "show me the treasury")
        assert "Laws: -300g  (1 in force)" in r["message"], r["message"]
        assert "the Grand Quartier Général: -300g/turn" in r["message"]


# ═══════════════════════════════ THE LAPSE (T4, R5) ═══════════════════════════

class TestTheLapse:

    def _stage(self, world, gold, *laws):
        for row in laws:
            R.enact_law(world, "France", row)
        world.nation_gold["France"] = gold
        world._income_phase_results = {"France": {
            "laws": R.law_upkeep_bill(world, "France"), "net": -1000}}

    def test_the_largest_upkeep_lapses_first_and_the_refund_makes_the_chest_whole(
            self, world):
        small = _add_law(world, "France", "small_act", upkeep=100)
        big = staff(world)
        self._stage(world, -250, small, big)
        R.process_law_lapses(world)
        assert "enacted_turn" not in big and big["lapsed_turn"] == world.current_turn
        assert R.is_in_force(small), "the chest is whole after one lapse"
        assert world.nation_gold["France"] == 50

    def test_it_sheds_laws_until_the_chest_is_whole(self, world):
        small = _add_law(world, "France", "small_act", upkeep=100)
        big = staff(world)
        self._stage(world, -350, small, big)
        R.process_law_lapses(world)
        assert not R.is_in_force(small) and not R.is_in_force(big)
        assert world.nation_gold["France"] == 50

    def test_a_tie_lapses_the_most_recently_enacted(self, world):
        first = _add_law(world, "France", "first_act", upkeep=100)
        second = _add_law(world, "France", "second_act", upkeep=100)
        R.enact_law(world, "France", first)
        world.current_turn += 3
        R.enact_law(world, "France", second)
        assert R.lapse_order(world, "France")[0] is second

    def test_the_refund_is_folded_out_of_the_applied_record(self, world):
        self._stage(world, -100, staff(world))
        R.process_law_lapses(world)
        applied = world._income_phase_results["France"]
        assert applied["laws"] == 0
        assert applied["net"] == -700, "Net == the measured change (ESP-4 shape)"

    def test_the_lapse_is_logged_and_told(self, world):
        self._stage(world, -100, staff(world))
        events = R.process_law_lapses(world)
        logged = _events(world, "law_lapsed")
        assert logged and logged[-1]["law"] == STAFF_ID and logged[-1]["upkeep"] == 300
        told = [e for e in events if e["type"] == "law_lapsed"]
        assert told, "the player's end-turn report hears of it"
        msg = told[0]["message"]
        assert "the law lapses" in msg
        assert "4,800 gold" in msg, "the Arrears price, a turn after the lapse"
        assert "extra order of the day" in msg

    def test_a_solvent_chest_sheds_nothing(self, world):
        self._stage(world, 0, staff(world))
        assert R.process_law_lapses(world) == []
        assert R.is_in_force(staff(world))

    def test_gr5_an_ai_court_lapses_by_the_same_rule_and_is_not_told(self, world):
        row = staff(world, "Austria")
        R.enact_law(world, "Austria", row)
        world.nation_gold["Austria"] = -10
        events = R.process_law_lapses(world)
        assert row["lapsed_turn"] == world.current_turn
        assert world.nation_gold["Austria"] == 290
        assert events == [], "only the player's own lapse reaches his report"
        assert any(e["nation"] == "Austria" for e in _events(world, "law_lapsed"))

    def test_lever_down_nothing_lapses(self, world, monkeypatch):
        self._stage(world, -100, staff(world))
        monkeypatch.setattr(R, "THE_STATE_HAS_LAWS", False)
        assert R.process_law_lapses(world) == []
        assert world.nation_gold["France"] == -100

    def test_the_lapse_runs_before_the_rente_default_and_the_bankruptcy(
            self, world, monkeypatch):
        """R5 in the turn itself: when ESP-4's default and the bankruptcy
        check run, the unpaid law has ALREADY lapsed."""
        row = staff(world)
        R.enact_law(world, "France", row)
        world.nation_gold["France"] = -60000
        seen = {}
        real_dot = WorldState._process_dotation_state
        real_bank = WorldState._update_bankruptcy

        def dot(self):
            seen.setdefault("dotation", "lapsed_turn" in row)
            return real_dot(self)

        def bank(self, nation):
            if nation == "France":
                seen.setdefault("bankruptcy", "lapsed_turn" in row)
            return real_bank(self, nation)

        monkeypatch.setattr(WorldState, "_process_dotation_state", dot)
        monkeypatch.setattr(WorldState, "_update_bankruptcy", bank)
        with _quiet():
            world.advance_turn()
        assert seen == {"dotation": True, "bankruptcy": True}

    def test_the_end_turn_report_tells_the_lapse(self, world, client):
        world.nation_gold["France"] = 12000
        post(client, "enact the Staff")
        world.nation_gold["France"] = -40000
        r = post(client, "end turn")
        told = [e for e in (r.get("tactical_events") or [])
                if isinstance(e, dict) and e.get("type") == "law_lapsed"]
        assert told and "the law lapses" in told[0]["message"]


# ═══════════════════════════════ THE ARREARS (R8) ═════════════════════════════

class TestRestoringALapsedLaw:

    @pytest.mark.parametrize("dead,paid", [(1, 4800), (5, 6000), (10, 7500), (11, 9000)])
    def test_the_restoration_charges_exactly_the_quoted_price(self, world, dead, paid):
        row = staff(world)
        row["lapsed_turn"] = world.current_turn - dead + 1
        world.nation_gold["France"] = 20000
        quote = R.restoration_price(world, "France", row)
        outcome = R.enact_law(world, "France", row)
        assert outcome["gold"] == paid == quote["price"] + quote["arrears"]
        assert world.nation_gold["France"] == 20000 - paid
        assert "lapsed_turn" not in row and R.is_in_force(row)

    def test_the_restoration_is_logged_as_a_restoration(self, world):
        row = staff(world)
        row["lapsed_turn"] = world.current_turn
        world.nation_gold["France"] = 20000
        R.enact_law(world, "France", row)
        assert _events(world, "law_enacted")[-1]["restored"] is True

    def test_the_typed_restoration_says_what_it_paid(self, world, client):
        row = staff(world)
        row["lapsed_turn"] = world.current_turn - 4
        world.nation_gold["France"] = 20000
        r = post(client, "re-enact the staff")
        assert r["success"] is True, r
        assert "restored for 4,500 gold and 1,500 gold in arrears (5 turns unpaid)" \
            in r["message"]
        assert world.nation_gold["France"] == 14000

    def test_an_authority_law_restores_for_half_its_authority_and_gold_arrears(self, world):
        row = _add_law(world, "France", "code_abroad", upkeep=100, price=15,
                       currency="authority")
        row["lapsed_turn"] = world.current_turn - 1
        world.nation_gold["France"] = 5000
        before = world.authority_tracker.authority
        outcome = R.enact_law(world, "France", row)
        assert outcome["authority"] == 8
        assert outcome["gold"] == 200
        assert world.authority_tracker.authority == before - 8
        assert world.nation_gold["France"] == 4800


# ═══════════════════════════════ THE CAMPAIGN LOG ═════════════════════════════

class TestTheCampaignLog:

    def test_the_three_types_are_logged_types(self):
        assert {"law_enacted", "law_repealed", "law_lapsed"} <= set(CL.CAMPAIGN_LOG_TYPES)

    @pytest.mark.parametrize("event,line", [
        ({"type": "law_enacted", "nation": "France",
          "name": "The Grand Quartier Général", "upkeep": 300},
         "France enacts the Grand Quartier Général (300g a turn)"),
        ({"type": "law_enacted", "nation": "Austria", "restored": True,
          "name": "The Corps d'Armée", "upkeep": 300},
         "Austria restores the Corps d'Armée (300g a turn)"),
        ({"type": "law_repealed", "nation": "France",
          "name": "The Grand Quartier Général", "upkeep": 300},
         "France repeals the Grand Quartier Général"),
        ({"type": "law_lapsed", "nation": "Prussia",
          "name": "The General Staff", "upkeep": 300},
         "Prussia cannot pay for the General Staff (300g a turn) — the law lapses"),
    ])
    def test_the_one_liners(self, event, line):
        assert CL.format_event_oneliner(event, "France") == line

    def test_a_rival_courts_law_is_court_knowledge(self, world):
        """Diplomacy has no fog (§8): Austria's enactment reaches the
        player's filtered campaign log wherever her armies stand."""
        world.nation_gold["Austria"] = 50000
        R.enact_law(world, "Austria", staff(world, "Austria"))
        shown = CL.filter_campaign_log(world.event_log, world)
        assert any(e.get("type") == "law_enacted" and e.get("nation") == "Austria"
                   for e in shown)
