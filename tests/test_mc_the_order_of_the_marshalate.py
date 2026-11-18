"""Row MC — "Mon Cousin": the Order of the Marshalate (docs/MARSHALATE_SPEC.md;
backend/game_logic/precedence.py). November 17, 2026, by the user's "look into
marshal relationships and make sure the pecking order and their relationships
is engaging and well designed" under "make decisions yourself soundly with
research".

What these pin: the opening's seats and causes and the 1805 reading; the one
writer and the book; renown; the order (captives kept); titles of victory (the
price, the honour, who is passed over and who is not); the two-way bonds
(brothers, the shared defeat and the account, the rescue, the silence, a quarrel
cooling — never an authored one —, serving under a junior); the claim; the
audience's cause and its quiet answer (GRD-17); the payloads; the save; and
that with every seam down the court is the commit before.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.game_logic import jealousy as J
from backend.game_logic import precedence as P
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def opening():
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(opening):
    w = WorldState.from_dict(opening.to_dict())
    # a strong Emperor: a title's or an account's price lands whole above the
    # purchase floor (60) — the floor's own refusal is the buy's, pinned elsewhere
    w.authority_tracker.authority = 90
    return w


def _m(world, name):
    return world.marshals[name]


def _result(outcome, atk="Ney", dfd="Mack", atk_cas=2000, def_cas=6000, atk_left=20000, def_left=20000,
            atk_retreat=False, def_retreat=False):
    return {"outcome": outcome,
            "attacker": {"name": atk, "casualties": atk_cas, "remaining": atk_left, "forced_retreat": atk_retreat},
            "defender": {"name": dfd, "casualties": def_cas, "remaining": def_left, "forced_retreat": def_retreat}}


# ════════════════════════════ the opening ════════════════════════════════

class TestTheOpening:

    def test_the_order_of_france_is_the_list_of_1804(self, world):
        order = [m.name for m in P.order_of_precedence(world, "France")]
        assert order == ["Murat", "Massena", "Bernadotte", "Soult", "Lannes", "Ney", "Davout"]
        assert [P.seat_of(world, _m(world, n)) for n in order] == [2, 5, 7, 8, 10, 12, 13]
        assert "Napoleon" not in order, "the sovereign holds no place among his marshals"

    def test_the_courts_seat_their_senior_general_first(self, world):
        assert [m.name for m in P.order_of_precedence(world, "Austria")][:3] == [
            "ArchdukeCharles", "ArchdukeJohn", "Mack"]

    def test_every_authored_pair_has_its_founding_incident_and_cause(self, world):
        import json
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        for name, m in data["marshals"].items():
            for other, value in (m.get("relationships") or {}).items():
                if not int(value) or other not in world.marshals:
                    continue
                cause = P.cause_of(world, name, other)
                assert cause, (name, other)
                assert cause == data["relationship_causes"][f"{name}->{other}"], (name, other)

    def test_three_enmities_read_as_they_stood_in_1805(self, world):
        for a, b in (("Davout", "Bernadotte"), ("Murat", "Bernadotte"), ("Bernadotte", "Napoleon")):
            assert _m(world, a).relationships[b] == -1 and _m(world, b).relationships[a] == -1, (a, b)

    def test_seam_down_the_seeds_read_as_before(self, monkeypatch, opening):
        monkeypatch.setattr(P, "the_seeds_read_as_of_1805", lambda: False)
        w = WorldState.from_scenario(str(SCENARIO))
        for a, b in (("Davout", "Bernadotte"), ("Murat", "Bernadotte"), ("Bernadotte", "Napoleon")):
            assert w.marshals[a].relationships[b] == -2 and w.marshals[b].relationships[a] == -2

    def test_every_seam_down_is_the_commit_before(self, monkeypatch):
        from tests._ba6_seams import BA6_SEAMS_BY_ROW
        from tests._oct27_seams import hold_down
        specs = [s for row in ("MC0", "MCBOOK", "MCSEEDS", "MCBONDS", "MCRANK") for s in BA6_SEAMS_BY_ROW[row]]
        hold_down(monkeypatch, specs)
        w = WorldState.from_scenario(str(SCENARIO))
        assert w.marshal_ledger == {} and w.marshal_accounts == []
        assert all(int(getattr(m, "seniority", 0) or 0) == 0 for m in w.marshals.values())
        d = w.to_dict()
        assert "marshal_ledger" not in d and "marshal_accounts" not in d
        assert not any(k in m for m in d["marshals"].values()
                       for k in ("seniority", "renown", "honours", "title_due", "last_claim_turn"))


# ═══════════════════════════ the book ════════════════════════════════════

class TestTheBook:

    def test_note_moves_the_stored_view_and_writes_the_cause(self, world):
        ney, soult = _m(world, "Ney"), _m(world, "Soult")
        moved = P.note(world, ney, soult, "rescue", "Swabia", da=+1)
        assert moved == (1, 0) and ney.relationships["Soult"] == 0
        assert P.cause_of(world, "Ney", "Soult") == "Soult came up when Ney was hard pressed at Swabia (turn 1)"
        rows = [e for e in world.event_log if e.get("type") == "marshal_bond"]
        assert rows and "Ney's view of Soult: Professional" in rows[-1]["line"]

    def test_a_floor_stops_a_move_and_never_pushes_a_view_back(self, world):
        a, b = _m(world, "Lannes"), _m(world, "Soult")
        a.set_relationship("Soult", -2)
        assert P.note(world, a, b, "blamed_the_lead", "Tyrol", da=-1, floor_a=-1) == (0, 0)
        assert a.relationships["Soult"] == -2

    def test_the_book_keeps_four_and_the_founding_one(self, world):
        ney, murat = _m(world, "Ney"), _m(world, "Murat")
        for i in range(6):
            P.record(world, "Ney", "Murat", "harsh_words", "", a_to_b=0)
        kept = P.incidents(world, "Ney", "Murat")
        assert len(kept) == P.BOOK_KEEP and kept[0]["kind"] == "seed"


# ══════════════════════ renown and the order ═════════════════════════════

class TestRenownAndTheOrder:

    def test_a_laurel_is_banked_and_a_defeat_costs_one(self, world):
        ney = _m(world, "Ney")
        J._append_glory(ney, 1, 3)
        J._append_glory(ney, 2, -2)
        assert ney.renown == 2
        J._append_glory(_m(world, "Napoleon"), 1, 4)
        assert int(getattr(_m(world, "Napoleon"), "renown", 0) or 0) == 0, "the sovereign accrues nothing"

    def test_a_captive_keeps_his_place_marked(self, world):
        murat = _m(world, "Murat")
        murat.captured_by = "Austria"
        assert P.place_in_the_order(world, murat) == (1, 7)
        assert P.card_fields(world, murat)["captive"] is True

    def test_his_place_trails_his_deeds(self, world):
        davout = _m(world, "Davout")
        davout.renown = 9
        assert P.trails_his_deeds(world, davout), "7th in the order, 1st in renown"
        assert not P.trails_his_deeds(world, _m(world, "Murat"))


# ═════════════════════════ titles of victory ══════════════════════════════

class TestTitlesOfVictory:

    def test_a_decisive_victory_puts_a_title_in_the_gift(self, world):
        ney = _m(world, "Ney")
        P.victory_earns(world, ney, 3, "Swabia", shadowed=False)
        assert ney.title_due["name"] == "Duke of Swabia" and ney.title_due["expires"] == world.current_turn + 8
        rows = [e for e in world.event_log if e.get("type") == "title_in_the_gift"]
        assert rows and rows[-1]["marshal"] == "Ney"

    def test_under_the_emperors_eye_no_title_is_earned(self, world):
        lannes = _m(world, "Lannes")
        P.victory_earns(world, lannes, 4, "Swabia", shadowed=True)
        assert lannes.title_due is None

    def test_a_small_victory_earns_none(self, world):
        P.victory_earns(world, _m(world, "Soult"), 2, "Swabia", shadowed=False)
        assert _m(world, "Soult").title_due is None

    def test_conferring_costs_authority_raises_him_and_names_who_resents_it(self, world):
        ney = _m(world, "Ney")
        ney.renown = 4
        _m(world, "Murat").renown = 3      # his deeds rival Ney's: passed over
        _m(world, "Soult").renown = 0      # clearly fewer laurels: knows it was earned
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        quote = P.confer_quote(world, ney)
        assert quote["ok"] and quote["passed_over"] == ["Murat"], quote
        before = world.authority_tracker.authority
        trust = ney.trust.value
        result = P.confer_title(world, "Ney")
        assert result["success"] and world.authority_tracker.authority < before
        assert P.tier_of(ney) == 1 and P.style_of(ney) == "Duke of Swabia"
        assert ney.trust.value == min(100, trust + P.TITLE_TRUST)
        assert [m.name for m in P.order_of_precedence(world, "France")][0] == "Ney"
        assert _m(world, "Murat").relationships["Ney"] == -1, "a slight makes a Rival..."
        assert _m(world, "Soult").relationships["Ney"] == -1, "(Soult's authored rivalry, untouched)"
        assert "raised above Murat" in P.cause_of(world, "Murat", "Ney")

    def test_a_slight_never_makes_a_hostile_by_itself(self, world):
        ney, murat = _m(world, "Ney"), _m(world, "Murat")
        murat.set_relationship("Ney", -1)
        murat.renown = ney.renown = 4
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        P.confer_title(world, "Ney")
        assert murat.relationships["Ney"] == -1

    def test_a_friend_is_glad_of_it(self, world):
        ney, lannes = _m(world, "Ney"), _m(world, "Lannes")
        lannes.renown = ney.renown = 4
        assert lannes.relationships["Ney"] == 1
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        assert "Lannes" not in P.confer_quote(world, ney)["passed_over"]

    def test_the_title_lapses_from_the_gift(self, world):
        ney = _m(world, "Ney")
        P.victory_earns(world, ney, 3, "Swabia", shadowed=False)
        world.current_turn += P.TITLE_DUE_TURNS + 1
        assert P.title_in_the_gift(world, ney) is None
        P._lapse_titles(world)
        assert ney.title_due is None

    def test_a_court_confers_its_own_by_the_same_rule(self, world):
        charles = _m(world, "ArchdukeCharles")
        P.victory_earns(world, charles, 4, "Bohemia", shadowed=False)
        P._courts_confer(world)
        assert P.style_of(charles) == "Duke of Bohemia"

    def test_a_duke_may_be_made_prince_by_a_greater_victory(self, world):
        ney = _m(world, "Ney")
        ney.honours = [{"tier": 1, "name": "Duke of Swabia", "place": "Swabia", "turn": 1}]
        P.victory_earns(world, ney, 3, "Tyrol", shadowed=False)
        assert ney.title_due is None, "a prince's title wants a greater victory"
        P.victory_earns(world, ney, 4, "Tyrol", shadowed=False)
        assert ney.title_due["name"] == "Prince of Tyrol"


# ═══════════════════════════ the bonds ════════════════════════════════════

class TestTheBonds:

    def test_brothers_in_arms_after_a_fourth_victory(self, world):
        ney, lannes = _m(world, "Ney"), _m(world, "Lannes")
        lannes.set_relationship("Ney", 1)
        for _ in range(P.BROTHERS_AT):
            P.after_shared_battle(world, attacker=ney, defender=_m(world, "Mack"),
                                  battle_result=_result("attacker_victory", atk_cas=3000, def_cas=9000),
                                  region="Swabia", attacker_participants=[ney, lannes],
                                  defender_participants=[_m(world, "Mack")])
        assert ney.relationships["Lannes"] == 2 and lannes.relationships["Ney"] == 2
        assert "brothers in arms" in P.cause_of(world, "Ney", "Lannes")

    def test_a_skirmish_makes_no_brothers(self, world):
        ney, lannes = _m(world, "Ney"), _m(world, "Lannes")
        lannes.set_relationship("Ney", 1)
        for _ in range(P.BROTHERS_AT + 2):
            P.after_shared_battle(world, attacker=ney, defender=_m(world, "Mack"),
                                  battle_result=_result("attacker_victory", atk_cas=10, def_cas=30),
                                  region="Swabia", attacker_participants=[ney, lannes],
                                  defender_participants=[_m(world, "Mack")])
        assert ney.relationships["Lannes"] == 1

    def test_a_courts_shared_defeat_sours_the_view_of_its_lead(self, world):
        charles, john = _m(world, "ArchdukeCharles"), _m(world, "ArchdukeJohn")
        mack = _m(world, "Mack")
        P.after_shared_battle(world, attacker=mack, defender=_m(world, "Ney"),
                              battle_result=_result("defender_victory", atk="Mack", dfd="Ney",
                                                    atk_cas=9000, def_cas=2000, atk_retreat=True),
                              region="Swabia", attacker_participants=[mack, john],
                              defender_participants=[_m(world, "Ney")])
        assert john.relationships["Mack"] == -1, "a professional view falls a rung"
        assert "blames Mack" in P.cause_of(world, "ArchdukeJohn", "Mack")
        del charles

    def test_a_friend_forgives_the_first_defeat(self, world):
        mack, john = _m(world, "Mack"), _m(world, "ArchdukeJohn")
        john.set_relationship("Mack", 1)
        P.sour_on(world, mack, [john], "Swabia")
        assert john.relationships["Mack"] == 1
        P.sour_on(world, mack, [john], "Swabia")
        assert john.relationships["Mack"] == 0

    def test_the_players_joint_defeat_asks_an_account_first(self, world):
        ney, soult = _m(world, "Ney"), _m(world, "Soult")
        P.after_shared_battle(world, attacker=ney, defender=_m(world, "Mack"),
                              battle_result=_result("defender_victory", atk_cas=9000, def_cas=2000, atk_retreat=True),
                              region="Swabia", attacker_participants=[ney, soult],
                              defender_participants=[_m(world, "Mack")])
        assert soult.relationships["Ney"] == -1, "nothing has soured yet (Soult's authored -1)"
        assert world.marshal_accounts and world.marshal_accounts[0]["lead"] == "Ney"

    def test_under_the_emperors_eye_nothing_sours(self, world):
        ney, soult, napoleon = _m(world, "Ney"), _m(world, "Soult"), _m(world, "Napoleon")
        P.after_shared_battle(world, attacker=ney, defender=_m(world, "Mack"),
                              battle_result=_result("defender_victory", atk_cas=9000, def_cas=2000, atk_retreat=True),
                              region="Swabia", attacker_participants=[ney, soult, napoleon],
                              defender_participants=[_m(world, "Mack")])
        assert not world.marshal_accounts

    def test_a_rescue_mends_even_a_hostile_view(self, world):
        ney, davout = _m(world, "Ney"), _m(world, "Davout")
        ney.set_relationship("Davout", -2)
        P.after_shared_battle(world, attacker=_m(world, "Mack"), defender=ney,
                              battle_result=_result("stalemate", atk="Mack", dfd="Ney", atk_cas=3000,
                                                    def_cas=3000, atk_left=40000, def_left=15000),
                              region="Swabia", attacker_participants=[_m(world, "Mack")],
                              defender_participants=[ney, davout], defender_reinforcements=[davout])
        assert ney.relationships["Davout"] == -1
        assert "came up when Ney was hard pressed" in P.cause_of(world, "Ney", "Davout")

    def test_the_silence_of_a_hostile_comrade_is_remembered(self, world):
        ney, bern = _m(world, "Ney"), _m(world, "Bernadotte")
        bern.set_relationship("Ney", -2)
        ney.set_relationship("Bernadotte", -1)
        region = world.get_region(ney.location)
        bern.location = region.adjacent_regions[0]
        P.after_shared_battle(world, attacker=ney, defender=_m(world, "Mack"),
                              battle_result=_result("defender_victory", atk_cas=9000, def_cas=2000),
                              region=ney.location, attacker_participants=[ney],
                              defender_participants=[_m(world, "Mack")])
        assert ney.relationships["Bernadotte"] == -2
        assert "did not march to the guns" in P.cause_of(world, "Ney", "Bernadotte")

    def test_a_senior_resents_serving_under_a_junior(self, world):
        davout, murat = _m(world, "Davout"), _m(world, "Murat")
        murat.set_relationship("Davout", 0)
        P.after_shared_battle(world, attacker=davout, defender=_m(world, "Mack"),
                              battle_result=_result("attacker_victory"),
                              region="Swabia", attacker_participants=[davout, murat],
                              defender_participants=[_m(world, "Mack")])
        assert murat.relationships["Davout"] == -1
        P.after_shared_battle(world, attacker=davout, defender=_m(world, "Mack"),
                              battle_result=_result("attacker_victory"),
                              region="Swabia", attacker_participants=[davout, murat],
                              defender_participants=[_m(world, "Mack")])
        assert murat.relationships["Davout"] == -1, "never below Rival by this road; once in eight turns"
        line = P.order_card_line(world, davout, [murat])
        assert "ranks above Davout" in line or "rival to Davout" in line

    def _attack_card(self, world, monkeypatch, joining):
        from backend.commands import order_quotes as Q
        davout, mack = _m(world, "Davout"), _m(world, "Mack")
        mack.location = davout.location             # within reach, on our own soil
        monkeypatch.setattr(Q, "_force_block", lambda w, m, e: {
            "ours": 60000, "ours_weight": 60000, "theirs_low": 20000, "theirs_high": 20000,
            "theirs_label": "20,000 men", "odds": "favorable", "joining": list(joining)})
        return Q.attack_quote(world, davout, mack)

    def test_the_attack_card_names_the_court_beforehand(self, world, monkeypatch):
        _m(world, "Murat").set_relationship("Davout", 0)
        q = self._attack_card(world, monkeypatch, ["Murat"])
        assert q["ok"], q.get("refusal")
        assert "Murat ranks above Davout and will resent serving under him" in q["note"]

    def test_a_friend_serves_gladly_and_the_card_says_nothing_of_rank(self, world, monkeypatch):
        _m(world, "Murat").set_relationship("Davout", 1)
        q = self._attack_card(world, monkeypatch, ["Murat"])
        assert "ranks above" not in str(q.get("note") or "")

    def test_seam_down_the_card_is_silent_on_the_court(self, world, monkeypatch):
        monkeypatch.setattr(P, "the_card_names_the_court", lambda: False)
        _m(world, "Murat").set_relationship("Davout", 0)
        q = self._attack_card(world, monkeypatch, ["Murat"])
        assert "ranks above" not in str(q.get("note") or "")

    def test_a_quarrel_of_play_cools_and_an_authored_one_does_not(self, world):
        ney, soult, massena = _m(world, "Ney"), _m(world, "Soult"), _m(world, "Massena")
        P.note(world, massena, ney, "harsh_words", "", da=-1)
        assert massena.relationships["Ney"] == -1
        world.current_turn += P.THAW_TURNS + 1
        P._cool(world)
        assert massena.relationships["Ney"] == 0, "a quarrel the campaign made cools"
        assert ney.relationships["Soult"] == -1, "an authored rivalry is character"
        del soult


# ═══════════════════════ the account and the claim ════════════════════════

class TestTheAccountAndTheClaim:

    def _account(self, world):
        world.marshal_accounts = [{"lead": "Ney", "others": ["Soult"], "place": "Swabia",
                                   "turn": world.current_turn}]
        return P._account_card(world, world.marshal_accounts[0])

    def test_the_card_offers_four_answers_with_their_prices(self, world):
        card = self._account(world)
        assert [o["id"] for o in card["options"]] == ["take_it", "on_the_lead", "on_another", "let_it_lie"]
        assert card["tier"] == "audience" and "Swabia" in card["title"]

    def test_the_emperor_takes_it(self, world):
        card = self._account(world)
        before = world.authority_tracker.authority
        r = P.apply_account(world, "take_it", card["context"])
        assert r["success"] and world.authority_tracker.authority < before
        assert _m(world, "Soult").relationships["Ney"] == -1 and not world.marshal_accounts

    def test_it_falls_on_another(self, world):
        card = self._account(world)
        P.apply_account(world, "on_another", card["context"])
        assert _m(world, "Ney").relationships["Soult"] == -2

    def test_an_unseen_account_lies_after_three_turns(self, world):
        self._account(world)
        world.pending_marshal_petition = {"kind": "other"}
        world.current_turn += P.ACCOUNT_SHOWS_FOR + 1
        P._push_accounts(world)
        assert not world.marshal_accounts

    def test_the_claim_and_its_three_answers(self, world):
        davout = _m(world, "Davout")
        davout.renown = 9
        davout.glory_events = [{"turn": 1, "points": 4, "place": "Bavaria"}]
        card = P._claim_card(world, davout)
        assert [o["id"] for o in card["options"]] == ["grant", "not_yet", "rebuke"]
        assert "Duke of Bavaria" in card["options"][0]["label"]
        r = P.apply_claim(world, "grant", card["context"])
        assert r["success"] and P.style_of(davout) == "Duke of Bavaria"


# ═══════════════ the audience's cause and its quiet answer ═════════════════

class TestTheAudienceNamesItsCause:

    def test_the_card_names_the_rivals_laurels(self, world):
        murat, ney = _m(world, "Murat"), _m(world, "Ney")
        ney.glory_events = [{"turn": 1, "points": 4, "place": "Swabia"}]
        murat.jealous_of = "Ney"
        murat.jealousy_turns_remaining = 3
        world.pending_marshal_petition = None
        J.queue_confrontation_petition(world, murat, ney)
        body = world.pending_marshal_petition["body"]
        assert "He has not forgotten Ney's laurels at Swabia (turn 1)." in body

    def test_the_quiet_answer_says_what_follows(self, world):
        murat, ney = _m(world, "Murat"), _m(world, "Ney")
        murat.jealous_of = "Ney"
        murat.jealousy_turns_remaining = 2
        r = J._apply_confrontation_choice(world, "acknowledge", {"marshal": "Murat", "target": "Ney"})
        assert r["message"].startswith("Murat's grievance stands: for 2 more turns")
        assert "runs its course" not in r["message"] and "Free" not in r["message"]


# ══════════════════════ the screens and the save ══════════════════════════

class TestTheScreensAndTheSave:

    def test_the_card_and_the_order(self, world):
        card = P.card_fields(world, _m(world, "Ney"))
        assert (card["place"], card["of"], card["seat"]) == (6, 7, 12)
        bonds = {b["other"]: b for b in card["bonds"]}
        assert bonds["Lannes"]["view_label"] == "Friendly" and bonds["Lannes"]["cause"]
        assert all(isinstance(card[k], int) for k in ("place", "of", "seat", "tier", "renown", "renown_place"))
        order = P.order_payload(world, "France")
        assert [r["name"] for r in order["rows"]][:2] == ["Murat", "Massena"]
        assert len(order["pairs"]) <= 3

    def test_a_temporary_grievance_is_marked_and_named_by_the_laurels(self, world):
        murat, ney = _m(world, "Murat"), _m(world, "Ney")
        ney.glory_events = [{"turn": 1, "points": 4, "place": "Swabia"}]
        murat.jealous_of = "Ney"
        row = next(b for b in P.bonds_of(world, murat) if b["other"] == "Ney")
        assert row["temporary"] and row["view"] == -2 and "laurels at Swabia" in row["cause"]

    def test_the_court_round_trips_a_save(self, world):
        ney = _m(world, "Ney")
        ney.renown = 5
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        P.confer_title(world, "Ney")
        w2 = WorldState.from_dict(world.to_dict())
        n2 = w2.marshals["Ney"]
        assert (n2.renown, n2.honours, n2.seniority) == (ney.renown, ney.honours, ney.seniority)
        assert w2.marshal_ledger == world.marshal_ledger

    def test_an_old_save_reads_an_empty_court(self, world):
        d = world.to_dict()
        d.pop("marshal_ledger", None)
        for m in d["marshals"].values():
            for k in ("seniority", "renown", "honours", "title_due", "last_claim_turn"):
                m.pop(k, None)
        w = WorldState.from_dict(d)
        assert w.marshal_ledger == {} and w.marshals["Ney"].honours == []
        assert P.order_of_precedence(w, "France"), "an old save still has an order (roster seats)"

    def test_the_log_tells_the_three_new_rows(self, world):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "title_conferred", "marshal": "Ney", "title": "Duke of Swabia",
                                      "passed_over": ["Murat"]})
        assert line == "Marshal Ney is created Duke of Swabia — passed over: Murat"
        line = format_event_oneliner({"type": "title_in_the_gift", "marshal": "Ney",
                                      "title": "Duke of Swabia", "turns": 8})
        assert "in the Emperor's gift" in line and "8 turns" in line
        assert format_event_oneliner({"type": "marshal_bond", "line": "x — y."}) == "x — y."

    def test_the_endpoint_confers(self, world, monkeypatch):
        from backend import main as M
        ney = _m(world, "Ney")
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        monkeypatch.setattr(M, "world", world)
        r = M.confer_title(SimpleNamespace(marshal="Ney"))
        assert r.get("success") is True and P.style_of(ney) == "Duke of Swabia"


# ═════════════ the Auerstedt rule reads its namesake (BA-6, row SILENCE) ═════════════

class TestTheAuerstedtRuleReadsItsNamesake:
    """The court count's find (`tools/_ba6_court_rule_2026_11_17.json`): ten
    AI-played French campaigns recorded no silence at all, because the rule
    remembered a silence only when the battle was lost or hung — and
    Auerstedt, its namesake, was a victory won outnumbered. A Hostile
    comrade's silence is now remembered when the lead was hard pressed, won
    or not (`precedence.a_silence_is_remembered_when_pressed`)."""

    def _auerstedt(self, world, *, davout_men, prussians):
        davout, bern = _m(world, "Davout"), _m(world, "Bernadotte")
        bern.set_relationship("Davout", -2)          # he will not march unordered
        davout.set_relationship("Bernadotte", -1)
        bern.location = world.get_region(davout.location).adjacent_regions[0]
        bern.strategic_order = None
        P.after_shared_battle(world, attacker=_m(world, "Mack"), defender=davout,
                              battle_result=_result("defender_victory", atk="Mack", dfd="Davout",
                                                    atk_cas=12000, def_cas=7000,
                                                    atk_left=prussians - 12000,
                                                    def_left=davout_men - 7000),
                              region=davout.location, attacker_participants=[_m(world, "Mack")],
                              defender_participants=[davout])
        return davout

    def test_a_victory_won_hard_pressed_remembers_the_silence(self, world):
        davout = self._auerstedt(world, davout_men=26000, prussians=60000)
        assert davout.relationships["Bernadotte"] == -2, "Davout won, and never forgave him"
        assert "did not march to the guns" in P.cause_of(world, "Davout", "Bernadotte")

    def test_a_victory_won_with_the_odds_forgets_it(self, world):
        davout = self._auerstedt(world, davout_men=60000, prussians=26000)
        assert davout.relationships["Bernadotte"] == -1, "not pressed and not lost: nothing to remember"

    def test_seam_down_reads_only_a_battle_lost_or_hung(self, world, monkeypatch):
        monkeypatch.setattr(P, "a_silence_is_remembered_when_pressed", lambda: False)
        davout = self._auerstedt(world, davout_men=26000, prussians=60000)
        assert davout.relationships["Bernadotte"] == -1, "as row MC built it"

    def test_the_rescue_reads_the_same_pressure(self, world):
        """ONE reading of 'hard pressed' (`_hard_pressed`) for the rescue and
        the silence, so the two can never disagree about the same field."""
        assert P._hard_pressed(_result("defender_victory", atk="Mack", dfd="Davout", atk_cas=12000,
                                       def_cas=7000, atk_left=48000, def_left=19000), False)
        assert not P._hard_pressed(_result("defender_victory", atk="Mack", dfd="Davout", atk_cas=1000,
                                           def_cas=1000, atk_left=19000, def_left=48000), False)
        assert not P._hard_pressed({}, True)


class TestTheCourtsWordsSayTheRule:
    """BA6-X11 (the lived court's capture, November 17, 2026): the brothers' cause said "a third
    victory together" where the rule makes friends brothers at the FOURTH (`BROTHERS_AT`)."""

    def test_the_brothers_line_names_the_count_the_rule_uses(self):
        ordinal = {3: "third", 4: "fourth", 5: "fifth"}[P.BROTHERS_AT]
        assert P.INCIDENT_LINES["brothers"].startswith(f"a {ordinal} victory together")


class TestTheRosterLineKeepsItsFigure:
    """BA6-X12 (the fit report on the lived court's Generals screen at five sizes): a long place
    beside a wide badge cut the roster line at the place — "Amster…" — and lost the strength."""

    def test_a_line_that_does_not_fit_keeps_the_strength(self):
        row = (REPO / "godot-client" / "project-sovereign" / "scripts" / "marshal_roster_row.gd").read_text(
            encoding="utf-8")
        assert "sub.resized.connect(_fit_sub.bind(sub))" in row
        fit = row.split("func _fit_sub(", 1)[1].split("\nfunc ", 1)[0]
        assert "get_string_size(_sub_full" in fit and "want = _sub_short" in fit
        assert "_sub_short = _men_of(card)" in row
        assert "tooltip_text = _sub_line(card) + " in row, "the place rides the hover"


class TestTheCardCarriesTheCourt:
    """BA6-X13 (the lived court's capture): the spec's §4 promises a marshal's honours on his card,
    and the client rendered them nowhere; the default Generals card had no place in the order either."""

    def test_the_cards_body_opens_with_the_court_and_names_the_honours(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts" / "marshal_management.gd").read_text(
            encoding="utf-8")
        body = src.split("func _detail_body(", 1)[1].split("\nfunc ", 1)[0]
        assert '_caption("The court") + court' in body and body.index("_court_line(m)") < body.index("_skills_grid(m)")
        line = src.split("func _court_line(", 1)[1].split("\nfunc ", 1)[0]
        assert 'court.get("honours", [])' in line and ']honours: "' in line

    def test_the_payload_carries_the_honours_the_card_reads(self, world):
        ney = _m(world, "Ney")
        P.victory_earns(world, ney, 4, "Swabia", shadowed=False)
        assert P.confer_title(world, "Ney").get("success") is True
        fields = P.card_fields(world, ney)
        assert [h["name"] for h in fields["honours"]] == ["Duke of Swabia"]
        assert fields["style"] == "Duke of Swabia" and fields["place"] >= 1

