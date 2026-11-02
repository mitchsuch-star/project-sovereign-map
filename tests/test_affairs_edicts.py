"""RE-6 — "Affairs of State": the Edicts (`docs/RECURRING_EVENTS_SPEC.md` §0 Q2,
§6.2 E1–E3, §14 the sizing, §16 "RE-6", §17 the owner row; the landing record
§25). A fixed-term decree on the laws' closed effect set — eight turns in
force, then eight turns of rest; gold and one administrative action, no
upkeep — offered by a letter of state under the one register, and taken by
the courts that keep a laws deck at the same prices (GR5).

The pins here drive the real seams on the booted 1805 world armed with the
staged fixture (`tests/fixtures/affairs_block.json`, the shipped block
verbatim): the second lifecycle in `reforms.effect_terms` (a source that
expires — derived from the turn, never ticked), the three premises clause
by clause, the `edict` op (shown = applied), the one gate and the one writer,
the courts' rung and verb, the Moniteur's line, the save round trip, the
validator's refusals, the budget, and the purity of every reader.
"""
import contextlib
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import dispatch as DP
from backend.game_logic import moments as MO
from backend.game_logic import reforms
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
E1, E2, E3 = "the_magazines", "the_remounts", "camps_of_instruction"
OFFERS = (E1, E2, E3)
HOME = "Lorraine"                                   # Napoleon's seat at the 1805 boot
CHOICE = {"accept": "accept_ai_proposal", "decline": "reject_ai_proposal"}
GREAT_POWERS = ("Austria", "Prussia", "Russia", "Britain")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _block():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


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
def armed(world):
    world.moments = MO.from_block(_block())
    world.__dict__.pop("_affairs_memo", None)
    return world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def _at(world, turn):
    world.current_turn = int(turn)
    world.invalidate_active_nations_cache()
    world.__dict__.pop("_affairs_memo", None)


def _tick(world):
    with _quiet():
        return MO.tick(world)


def _run(world, turns):
    out = {}
    for turn in turns:
        _at(world, turn)
        delivered = _tick(world)
        if delivered:
            out[int(turn)] = delivered
    return out


def _letter(world, moment_id):
    dm = world.dialogue_manager
    for d in [dm.peek()] + list(dm.iter_queue()):
        if MO.is_moment_letter(d) and MO.moment_id_of(d) == moment_id:
            return d
    return None


def _make_current(world, letter):
    dm = world.dialogue_manager
    if dm.peek() is not letter:
        dm.remove_matching(lambda d: d is letter)
        dm.preempt(letter)
    assert dm.peek() is letter


def _answer(world, client, mid, answer):
    letter = _letter(world, mid)
    assert letter is not None, mid
    _make_current(world, letter)
    with _quiet():
        result = client.post("/respond_to_diplomatic_dialogue",
                             json={"choice": CHOICE[answer], "dialogue_id": letter["dialogue_id"]}).json()
    return result


def _no_moments(world):
    for e in MO.deck(world):
        world.moments["state"][str(e["id"])] = {"status": "passed", "turn": 1, "reason": "premise"}


def _entry(world, template):
    e = AF.template_by_id(world, template)
    assert e is not None, template
    return e


def _read(world, template, lord="France"):
    world.__dict__.pop("_affairs_memo", None)
    return AF.premise_holds(world, _entry(world, template), lord)


def _occ(template, turn=7):
    return {"id": f"{template}#1", "lord": "France", "bind": {}, "tier": 1, "turn": int(turn)}


# ── the boards ───────────────────────────────────────────────────────────────

def _quiet_board(world, gold=5_000):
    """The boot with the dated moments passed, the chest at `gold`, the fleet
    under the Marine's bar (no Haiti letter), the Staff's door out of the
    morning (the chest under its bar): the offers' own premises decide."""
    from backend.game_logic import naval
    _no_moments(world)
    world.nation_gold["France"] = int(gold)
    naval.get_fleet(world, "France")["ships"] = 20
    world.__dict__.pop("_affairs_memo", None)


def _magazines_board(world, gold=5_000):
    """E1 alone: at war (the boot), Bernadotte on campaign pay at Franconia
    (the boot), the depots full so the Remounts stand aside."""
    from backend.models.world_state import MAX_CAVALRY_POOL
    _quiet_board(world, gold)
    world.manpower_pools["France"]["cavalry"] = int(MAX_CAVALRY_POOL)
    world.__dict__.pop("_affairs_memo", None)


def _remounts_board(world, gold=5_000, pct=59):
    """E2 alone: every corps at home (no campaign pay), the pool at `pct` %."""
    from backend.models.world_state import MAX_CAVALRY_POOL
    _quiet_board(world, gold)
    world.marshals["Bernadotte"].location = HOME
    world.manpower_pools["France"]["cavalry"] = int(MAX_CAVALRY_POOL) * int(pct) // 100
    world.__dict__.pop("_affairs_memo", None)


def _peace(world):
    for court in GREAT_POWERS:
        world.diplomatic_states[world._make_diplo_key("France", court)] = "PEACE"
    world.war_exhaustion["France"] = 0
    world.invalidate_active_nations_cache()


def _camps_board(world, gold=5_000):
    """E3 alone: at peace with every great power, the Charges on the crown
    alone, the depots full."""
    from backend.models.world_state import MAX_CAVALRY_POOL
    _quiet_board(world, gold)
    _peace(world)
    world.manpower_pools["France"]["cavalry"] = int(MAX_CAVALRY_POOL)
    world.__dict__.pop("_affairs_memo", None)


# ═══════════════════════════════════════════════════════════════════════════
# The deck — three offers under the one register (§5, §6.2)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDeck:
    def test_the_three_offers_are_authored_as_ruled(self, armed):
        for template, price, effect in ((E1, 2500, {"type": "supply_capacity", "value": 1.25}),
                                        (E2, 1500, {"type": "recruit_price", "arm": "cavalry", "value": 0.8}),
                                        (E3, 2000, {"type": "drill_morale", "value": 5})):
            e = _entry(armed, template)
            assert e["shape"] == "offer" and e["kind"] == "affair"
            block = AF.edict_block(e)
            assert block["price"] == price and block["term"] == 8 and block["rest"] == 8
            assert block["effects"] == [effect]
            assert [op["op"] for op in e["accept"]["ops"]] == ["admin", "edict"]
            assert e["decline"]["ops"] == []
            assert e["when"]["edict"] == template and e["when"]["predicate"] in AF.OFFER_PREDICATES
            assert e["source"] and re.search(r"\bmay\b", e["watch"]) and "will" not in e["watch"]
            assert e["record"].startswith("Historically")
            assert e["cooldown"] == 8 and e["cap"] == 2

    def test_every_line_sits_within_its_limit(self, armed):
        for template in OFFERS:
            e = _entry(armed, template)
            for key in ("title", "record", "line", "counsel", "watch", "source"):
                assert len(e[key]) <= AF.TEXT_MAX[key], (template, key)
            block = AF.edict_block(e)
            assert len(block["name"]) <= AF.TEXT_MAX["edict_name"]
            assert len(block["court_press"]) <= AF.TEXT_MAX["court_press"]
            for side in ("accept", "decline"):
                for key in ("echo", "press", "remember", "situation"):
                    if key in e[side]:
                        assert len(e[side][key]) <= AF.TEXT_MAX[key], (template, side, key)
            for variant in e.get("variants") or []:
                assert variant["key"] == "arrival" and len(variant["text"]) <= AF.TEXT_MAX["variant"]

    def test_the_op_table_and_the_constants(self):
        assert "edict" in MO.OPS and len(MO.OPS) == 11
        assert "edict" in AF.AFFAIR_OPS and "edict" in MO.DECLINE_FORBIDDEN_OPS
        assert "edict" not in MO.OP_BOUNDS                       # the moments' own vocabulary is closed
        assert AF.EDICT_EFFECT_TYPES == ("supply_capacity", "recruit_price", "drill_morale")
        assert set(AF.EDICT_EFFECT_TYPES) <= set(reforms.WIRED_EFFECT_TYPES)
        assert set(AF.OFFER_PREDICATES) <= set(AF.PREDICATES)

    def test_the_holders_change_hands_on_their_turns(self, armed):
        """E2 Dejean → Lacuée de Cessac after 3 January 1810 (T104); E3 Berthier
        → Clarke after 9 August 1807 (T46) — the §12 table, display only."""
        e2, e3 = _entry(armed, E2), _entry(armed, E3)
        assert MO.voice_of(armed, e2, issued=40) == "Dejean, Minister of War Administration"
        assert MO.voice_of(armed, e2, issued=104) == "Lacuée de Cessac, Minister of War Administration"
        assert MO.voice_of(armed, e3, issued=20) == "Berthier, Minister of War"
        assert MO.voice_of(armed, e3, issued=46) == "Clarke, Minister of War"
        assert MO.voice_of(armed, _entry(armed, E1), issued=60) == "Daru, Intendant-General"

    def test_the_lockstep_of_fixture_and_scenario(self):
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        assert scenario["affairs"] == _block()["affairs"]
        assert [e["id"] for e in scenario["affairs"]["deck"]][-3:] == list(OFFERS)


# ═══════════════════════════════════════════════════════════════════════════
# The three premises, clause by clause (§6.2)
# ═══════════════════════════════════════════════════════════════════════════

class TestThePremises:
    def test_the_boot_offers_nothing_for_a_chest_of_eight_hundred(self, armed):
        for template in OFFERS:
            assert _read(armed, template)["holds"] is False
            assert "gold is asked" in AF.edict_refusal(armed, "France", _entry(armed, template), with_reserve=True)

    def test_the_magazines_on_a_corps_drawing_campaign_pay(self, armed):
        _magazines_board(armed)
        read = _read(armed, E1)
        assert read["holds"] is True and read["measure"] == 1     # Bernadotte at Franconia
        armed.marshals["Bernadotte"].location = HOME
        assert _read(armed, E1)["holds"] is False                 # every corps at home, the coalition formed

    def test_the_magazines_on_the_storm_gathering(self, armed):
        """At peace, no corps abroad: a coalition brewing against France (the
        gauge's "Brewing" tier) carries the clause; one already formed does not."""
        from backend.game_logic.coalition import brewing_gate
        _camps_board(armed)                                       # at peace, the depots full
        armed.marshals["Bernadotte"].location = HOME
        armed.active_coalition = None
        armed.threat_level = int(brewing_gate(armed, "France"))
        read = _read(armed, E1)
        assert read["holds"] is True and read["measure"] == 0
        armed.threat_level = int(brewing_gate(armed, "France")) - 1
        assert _read(armed, E1)["holds"] is False
        armed.threat_level = 100
        armed.active_coalition = {"target_nation": "France", "members": ["Austria"]}
        assert _read(armed, E1)["holds"] is False

    def test_the_remounts_on_the_depots_under_sixty_percent(self, armed):
        _remounts_board(armed, pct=59)
        read = _read(armed, E2)
        assert read["holds"] is True and read["measure"] == 59
        _remounts_board(armed, pct=61)
        assert _read(armed, E2)["holds"] is False
        assert _read(armed, E1)["holds"] is False                 # no corps abroad

    def test_the_remounts_on_a_cavalry_corps_under_sixty_percent_of_its_establishment(self, armed):
        """The second clause (the measure's finding: the depots alone reached
        no board): the horse lost on campaign — Murat's reserve at 50 % of
        its establishment premises the letter with the depots full; at 61 %
        it does not; a captured corps and an infantry corps count for nothing."""
        _remounts_board(armed, pct=100)
        murat = armed.marshals["Murat"]
        assert getattr(murat, "cavalry", False) and murat.starting_strength > 0
        assert _read(armed, E2)["holds"] is False
        murat.strength = murat.starting_strength // 2
        read = _read(armed, E2)
        assert read["holds"] is True and read["measure"] == 50
        murat.strength = murat.starting_strength * 61 // 100
        assert _read(armed, E2)["holds"] is False
        murat.strength = murat.starting_strength // 2
        murat.captured_by = "Austria"
        assert _read(armed, E2)["holds"] is False
        murat.captured_by = ""
        ney = armed.marshals["Ney"]
        ney.strength = ney.starting_strength // 2                  # infantry: not the horse
        murat.strength = murat.starting_strength
        assert _read(armed, E2)["holds"] is False
        assert AF._weakest_cavalry_corps_pct(armed, "France") == 100

    def test_the_camps_at_the_golden_peace(self, armed):
        _camps_board(armed)
        assert _read(armed, E3)["holds"] is True
        armed.war_exhaustion["France"] = 10                       # the long war wears on: not the golden peace
        assert _read(armed, E3)["holds"] is False
        armed.war_exhaustion["France"] = 0
        armed.diplomatic_states[armed._make_diplo_key("France", "Prussia")] = "WAR"
        armed.invalidate_active_nations_cache()
        assert _read(armed, E3)["holds"] is False                 # at war with one great power

    def test_the_purse_bar_is_the_laws_rung_s(self, armed):
        """price + the AI's reserve + five turns of the slate's upkeep — one
        source with the courts' rung; the letter's own plan asks the price alone."""
        _remounts_board(armed, gold=2_499)
        assert _read(armed, E2)["holds"] is False
        armed.nation_gold["France"] = 2_500
        assert _read(armed, E2)["holds"] is True
        armed.nation_gold["France"] = 1_499
        assert "1,500 gold is asked" in AF.edict_refusal(armed, "France", _entry(armed, E2))
        armed.nation_gold["France"] = 1_500
        assert AF.edict_refusal(armed, "France", _entry(armed, E2)) == ""


# ═══════════════════════════════════════════════════════════════════════════
# The lifecycle — granted by the letter, read at every seam, expired by the
# turn alone, remembered by the save (§16 "RE-6" done-when)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLifecycle:
    def test_the_magazines_arrive_on_the_pulse_and_the_accept_decrees(self, armed, client):
        _magazines_board(armed)                                   # 5,000: under the Staff's bar
        delivered = _run(armed, range(1, 8))
        assert delivered == {7: [f"{E1}#1"]}, delivered
        letter = _letter(armed, f"{E1}#1")
        payload = letter["popup_payload"]
        assert payload["writer"] == "Daru" and payload["office"] == "Intendant-General"
        assert payload["button_accept"] == "−2,500 gold · 1 action · 8 turns"
        assert payload["button_decline"] == "no change"
        assert "fed provinces feed 25% more men (×1.25) until" in payload["answers"][0]["quote"]
        assert payload["board"][0].startswith("1 of your corps draw campaign pay on foreign soil; the chest holds 5,000 gold against 2,500")
        region = armed.regions[HOME]
        cap_before = armed.get_effective_supply_cap("France", region)
        admin_before = armed.admin_actions_remaining
        result = _answer(armed, client, f"{E1}#1", "accept")
        assert result["success"] is True
        lines = result["message"].split("\n")
        assert lines[0].startswith("The Magazines — Stock the magazines:")
        assert lines[1] == "Daru: the contracts are signed; the convoys roll for the Rhine depots tonight."
        assert len(lines) == 2 and result.get("moment_answered") == {"id": f"{E1}#1", "answer": "accept"}
        assert armed.nation_gold["France"] == 5_000 - 2_500 and armed.admin_actions_remaining == admin_before - 1
        row = MO.status_row(armed, f"{E1}#1")
        assert row["status"] == "answered" and row["until"] == 15 and row["receipt"] == "−2,500 gold · 1 action · 8 turns"
        assert AF.edict_state(armed, "France", _entry(armed, E1)) == "in_force"
        assert AF.edicts_in_force(armed, "France") == [(_entry(armed, E1), 15)]
        # the seam: the fed supply multiplier, through `reforms.effect_terms`
        assert reforms.supply_capacity_terms(armed, "France") == [("the Magazines", 1.25)]
        cap_after = armed.get_effective_supply_cap("France", region)
        assert abs(cap_after / cap_before - 1.25) < 0.01, (cap_before, cap_after)
        # the LAWS book's EDICTS block, on the payload and on GET /ledger
        edicts = reforms.laws_payload(armed, "France")["edicts"]
        assert edicts == [{"id": E1, "name": "the Magazines", "spoken": "The Magazines",
                           "effects": ["fed provinces feed 25% more men (×1.25)"],
                           "until": 15, "until_words": MO._dateline(armed, 15),
                           "status_line": f"In force until {MO._dateline(armed, 15)}."}]
        with _quiet():
            ledger = client.get("/ledger").json()["ledger"]
        assert ledger["laws"]["edicts"] == edicts
        # the Correspondence's slip knows the term
        slip = next(s for s in MO.correspondence(armed)["answered"] if s["id"] == f"{E1}#1")
        assert slip["until"] == 15 and slip["in_force"] is True and {"kind": "laws", "nation": ""} in slip["chips"]
        # the answered log row carries the Moniteur's line
        logged = [ev for ev in armed.event_log if ev.get("type") == "moment" and ev.get("phase") == "answered"][-1]
        assert logged["press"] == "PARIS — The Intendance contracts for the magazines of the Grande Armée."
        # the morning after: the receipt in SITUATION (RE-R's seam), the premise closed
        _at(armed, 8)
        with _quiet():
            situation = DP._build_situation(armed, "France")
        assert situation["affair_receipt"] == [
            f"The magazines are stocked; the fed provinces carry a quarter more men until {MO._dateline(armed, 15)}."]
        assert _read(armed, E1)["holds"] is False
        assert AF.edict_refusal(armed, "France", _entry(armed, E1)).startswith("The Magazines stands until")

    def test_the_term_ends_by_the_turn_alone_and_the_rest_follows(self, armed):
        _magazines_board(armed, gold=12_000)
        e = _entry(armed, E1)
        p = MO.plan(armed, e, MO.ANSWER_ACCEPT, _occ(E1, turn=7))
        assert p["ok"], p["refusal"]
        _at(armed, 7)
        MO._apply(armed, p)
        for turn, state, factor in ((7, "in_force", 1.25), (14, "in_force", 1.25), (15, "resting", 1.0),
                                    (22, "resting", 1.0), (23, "available", 1.0)):
            _at(armed, turn)
            assert AF.edict_state(armed, "France", e) == state, turn
            assert reforms.supply_capacity_factor(armed, "France") == factor, turn
        _at(armed, 15)
        assert AF.edict_refusal(armed, "France", e).startswith("The Magazines rests until")
        assert _read(armed, E1)["holds"] is False
        _at(armed, 23)
        assert AF.edict_refusal(armed, "France", e) == "" and _read(armed, E1)["holds"] is True
        assert AF.last_decree_turn(armed, "France") == 7

    def test_the_store_survives_a_save_and_a_load(self, armed):
        from backend.models.world_state import WorldState
        _magazines_board(armed, gold=12_000)
        _at(armed, 7)
        MO._apply(armed, MO.plan(armed, _entry(armed, E1), MO.ANSWER_ACCEPT, _occ(E1, turn=7)))
        with _quiet():
            again = WorldState.from_dict(armed.to_dict())
        runtime = again.moments["affairs"]
        assert runtime["edicts"] == {f"France|{E1}": 15} and runtime["decreed"] == {f"France|{E1}": 1}
        assert runtime["edict_gold"] == {"France": 2500}
        assert [(e["id"], u) for e, u in AF.edicts_in_force(again, "France")] == [(E1, 15)]
        assert reforms.supply_capacity_factor(again, "France") == 1.25
        assert reforms.laws_signature(again, "France") == reforms.laws_signature(armed, "France")

    def test_the_remounts_price_the_cavalry_levy_alone(self, armed):
        _remounts_board(armed, gold=6_000)
        _at(armed, 3)
        MO._apply(armed, MO.plan(armed, _entry(armed, E2), MO.ANSWER_ACCEPT, _occ(E2, turn=3)))
        assert reforms.recruit_price_terms(armed, "France", "cavalry") == [("the Remounts", 0.8)]
        assert reforms.recruit_price_terms(armed, "France", "infantry") == []
        assert reforms.recruit_price_terms(armed, "Austria", "cavalry") == []
        from backend.commands.executor import CommandExecutor
        with _quiet():
            economy = CommandExecutor()._economy
        region = armed.regions[HOME]
        cost, terms = economy._recruit_cost_terms(region, armed, 300, nation="France", arm="cavalry")
        assert any("×0.8 by the Remounts" in t for t in terms), terms
        cost_inf, terms_inf = economy._recruit_cost_terms(region, armed, 200, nation="France", arm="infantry")
        assert not any("Remounts" in t for t in terms_inf)

    def test_the_camps_raise_every_drill_and_name_themselves(self, armed):
        _camps_board(armed, gold=6_000)
        _at(armed, 7)
        assert armed.drill_morale_gain("France", trained=False) == 10
        MO._apply(armed, MO.plan(armed, _entry(armed, E3), MO.ANSWER_ACCEPT, _occ(E3, turn=7)))
        assert reforms.drill_morale_bonus(armed, "France") == 5
        assert armed.drill_morale_gain("France", trained=False) == 15
        assert armed.drill_morale_gain("Austria", trained=False) == 10
        note = armed._drill_law_note(armed.marshals["Ney"], 15)
        assert "the Camps of Instruction" in note, note

    def test_the_decline_spends_nothing_and_the_offer_returns_after_its_cooldown(self, armed, client):
        _remounts_board(armed, gold=6_000)
        assert _run(armed, range(1, 8)) == {7: [f"{E2}#1"]}
        result = _answer(armed, client, f"{E2}#1", "decline")
        assert result["success"] is True and result["message"].endswith("Let the depots wait: no change.")
        assert armed.nation_gold["France"] == 6_000
        row = MO.status_row(armed, f"{E2}#1")
        assert row["status"] == "answered" and "until" not in row
        assert AF.edicts_in_force(armed, "France") == []
        assert _run(armed, range(8, 15)) == {}                     # the cooldown of eight
        assert _run(armed, [15]) == {15: [f"{E2}#2"]}
        payload = MO.refresh_letter(armed, _letter(armed, f"{E2}#2"))
        assert payload["chapter"] == "The depots were filled once before; the War Administration asks for the fairs' credit again."
        assert payload["board"][-1] == (f"In {MO._dateline(armed, 7)} the depots waited; "
                                        f"the War Administration writes again.")

    def test_a_standing_letter_closes_its_accept_when_the_chest_falls_short(self, armed, client):
        _magazines_board(armed)
        _run(armed, range(1, 8))
        armed.nation_gold["France"] = 2_000
        p = MO.plan(armed, _entry(armed, E1), MO.ANSWER_ACCEPT, MO.status_row(armed, f"{E1}#1"))
        assert not p["ok"] and p["refusal"] == "2,500 gold is asked; the treasury holds 2,000."
        result = _answer(armed, client, f"{E1}#1", "accept")
        assert result["success"] is False and "2,500 gold is asked" in result["message"]
        assert MO.status_row(armed, f"{E1}#1")["status"] == "fired"           # the letter stands
        assert armed.nation_gold["France"] == 2_000


# ═══════════════════════════════════════════════════════════════════════════
# The courts — the same prices, the one gate, the one writer (GR5); the rung
# measured first behind `affairs.ai_decrees`, escalated, and ARMED by the
# user's word of November 2, 2026 — "Flip it on" (§25.3, §25.6)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def courts_up(monkeypatch):
    """The shipped default since the user's word; held explicitly so the
    pins below read the same whichever way the seam is later ruled."""
    monkeypatch.setattr(AF, "ai_decrees", lambda: True)


class TestTheCourts:
    def test_the_rung_is_armed_by_the_user_s_word_and_the_seam_holds_it_down(self, armed, monkeypatch):
        """Shipped: `ai_decrees()` is True — the courts decree at the player's
        prices; the series rig's AFE arm holds the rung down (the letters and
        the lifecycle stand), and False parks it again in one line."""
        from tests._affairs_seams import AFFAIRS_SEAMS_BY_ROW, hold_down
        armed.nation_gold["Austria"] = 20_000
        assert AF.ai_decrees() is True
        assert AF.find_ai_edict(armed, "Austria", 20_000, 2) is not None
        hold_down(monkeypatch, AFFAIRS_SEAMS_BY_ROW["AFE"])
        assert AF.ai_decrees() is False and AF.find_ai_edict(armed, "Austria", 20_000, 2) is None
        _magazines_board(armed, gold=12_000)
        assert _read(armed, E1)["holds"] is True

    def test_the_rung_decrees_the_first_live_offer_at_the_laws_rung_s_bar(self, armed, courts_up):
        armed.nation_gold["Austria"] = 20_000
        assert AF.find_ai_edict(armed, "Austria", 20_000, 2) == {"action": "decree_edict", "target": E2}
        assert AF.find_ai_edict(armed, "Austria", 2_499, 2) is None          # under the bar
        assert AF.find_ai_edict(armed, "Austria", 20_000, 0) is None         # no action left
        assert AF.find_ai_edict(armed, "France", 20_000, 2) is None          # never the player
        armed.nation_gold["Bavaria"] = 20_000
        assert AF.find_ai_edict(armed, "Bavaria", 20_000, 2) is None         # no laws deck, no decree

    def test_the_verb_grants_through_the_one_writer_and_the_moniteur_prints_it(self, armed, courts_up):
        from backend.commands.executor import CommandExecutor
        from backend.campaign_log import filter_campaign_log
        from backend.game_logic.gazette import _affair_courts_line
        armed.nation_gold["Austria"] = 20_000
        alarm_before = dict(getattr(armed, "threat_by_target", {}) or {})
        with _quiet():
            ex = CommandExecutor()
            result = ex.execute({"command": {"action": "decree_edict", "target": E2, "_acting_nation": "Austria",
                                             "type": "specific"}}, {"world": armed})
        assert result["success"] is True
        assert result["message"] == f"Austria decrees the Remounts until {MO._dateline(armed, armed.current_turn + 8)}."
        assert armed.nation_gold["Austria"] == 18_500 and armed.gold_spent_this_turn["Austria"] == 1_500
        assert AF.edict_state(armed, "Austria", _entry(armed, E2)) == "in_force"
        assert reforms.recruit_price_terms(armed, "Austria", "cavalry") == [("the Remounts", 0.8)]
        assert reforms.recruit_price_terms(armed, "France", "cavalry") == []
        assert dict(getattr(armed, "threat_by_target", {}) or {}) == alarm_before
        runtime = armed.moments["affairs"]
        assert runtime["decreed"] == {f"Austria|{E2}": 1} and runtime["edict_gold"] == {"Austria": 1500}
        row = [ev for ev in armed.event_log if ev.get("type") == "moment" and ev.get("nation") == "Austria"][-1]
        assert row["phase"] == "outcome" and row["register"] == "affair"
        assert row["line"] == "Austria decrees the Remounts for 8 turns (1,500 gold)"
        assert row["press"] == "VIENNA — The court of Austria buys remounts for its horse."
        seen = [ev for ev in filter_campaign_log(armed.event_log, armed) if ev is row]
        assert seen and _affair_courts_line(row) == row["press"]
        # the same morning: in force, so the rung moves on (the gate is read fresh)
        assert AF.find_ai_edict(armed, "Austria", 18_500, 1) is None
        with _quiet():
            again = ex.execute({"command": {"action": "decree_edict", "target": E2, "_acting_nation": "Austria",
                                            "type": "specific"}}, {"world": armed})
        assert again["success"] is False and again["message"].startswith("The Remounts stands until")

    def test_the_cadence_and_the_lapse_guard(self, armed, monkeypatch, courts_up):
        armed.nation_gold["Austria"] = 20_000
        _at(armed, 5)
        AF.grant_edict(armed, "Austria", _entry(armed, E2))
        # a court with a war-intent in tenure against it: the Magazines' storm clause
        armed.war_intents["Prussia"] = {"coveter": "Prussia", "target": "Austria", "design_id": "silesia",
                                        "foregrounded": True, "foregrounded_turn": 5}
        assert _read(armed, E1, "Austria")["holds"] is True
        assert AF.find_ai_edict(armed, "Austria", 18_500, 2) is None       # one decree every three turns
        _at(armed, 8)
        assert AF.find_ai_edict(armed, "Austria", 18_500, 2) == {"action": "decree_edict", "target": E1}
        monkeypatch.setattr(reforms, "ai_holds_the_purse", lambda world, nation: True)
        assert AF.find_ai_edict(armed, "Austria", 18_500, 2) is None       # a law would lapse: no spend

    def test_the_courts_up_series_record_attributes_the_move(self):
        """The series rig's first run with the rung UP, before the ruling
        (`tools/_affairs_series_arms_re6.json`): the letters alone leave the
        ambient alarm byte-identical to the pre-RE-6 baseline (arm AFE);
        every seam down reproduces the pre-RE-H series (arm 0); the courts'
        decrees alone move it from turn 10 (arm ALL, 13 edicts granted) — the
        move the user read before saying "Flip it on"."""
        from tests.test_ai_intent_threat_migration import SERIES_BEFORE_RE_6, SERIES_BEFORE_RE_H
        record = json.loads((REPO / "tools" / "_affairs_series_arms_re6.json").read_text(encoding="utf-8"))
        arms = record["arms"]
        assert record["prior"] == arms["AFE"]["series"] == SERIES_BEFORE_RE_6
        assert arms["0"]["series"] == SERIES_BEFORE_RE_H
        assert arms["ALL"]["series"] != SERIES_BEFORE_RE_6 and arms["ALL"]["first_divergence_vs_prior"] == 10
        assert arms["ALL"]["reach"]["counts"]["edicts_granted"] == 13
        assert arms["AFE"]["reach"]["counts"]["edicts_granted"] == 0

    def test_the_player_never_reaches_the_verb(self, armed):
        from backend.ai.validation import VALID_ACTIONS
        from backend.commands.executor import CommandExecutor
        assert "decree_edict" not in VALID_ACTIONS
        parser_src = (BACKEND / "commands" / "parser.py").read_text(encoding="utf-8")
        assert '"decree_edict"' not in parser_src
        with _quiet():
            ex = CommandExecutor()
            for command in ({"action": "decree_edict", "target": E2, "type": "specific"},
                            {"action": "decree_edict", "target": E2, "_acting_nation": "France", "type": "specific"}):
                result = ex.execute({"command": command}, {"world": armed})
                assert result["success"] is False and result["message"] == "The Edicts come by letter, Sire."

    def test_the_admin_chain_carries_the_rung_at_one_point_seven_nine(self):
        src = (BACKEND / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        i = src.index("Priority 1.78")
        j = src.index("Priority 1.79")
        k = src.index("Priority 1.8:")
        assert i < j < k and "find_ai_edict(world, nation, treasury, admin_ap)" in src[j:k]
        assert '"decree_edict" not in skip_actions' in src[j:k]


# ═══════════════════════════════════════════════════════════════════════════
# The validator (§5, §16 "RE-6")
# ═══════════════════════════════════════════════════════════════════════════

def _scenario_with(block):
    data = json.loads(SCENARIO.read_text(encoding="utf-8"))
    data["moments"] = block
    return data


def _errors(block):
    from backend.modding.validator import validate_scenario
    return [e for e in validate_scenario(_scenario_with(block)).errors if e.path.startswith("moments")]


def _bad(mutate):
    block = _block()
    mutate(block)
    return {e.path for e in _errors(block)}


def _aff(b, i):
    return b["affairs"]["deck"][i]


class TestTheValidator:
    def test_the_fixture_validates(self):
        assert _errors(_block()) == []

    @pytest.mark.parametrize("label, mutate, path", [
        ("a gold op on an offer", lambda b: _aff(b, 4)["accept"]["ops"].append({"op": "gold", "amount": 100}),
         "moments.affairs.deck[4].accept.ops"),
        ("an offer's decline with an op", lambda b: _aff(b, 4)["decline"]["ops"].append({"op": "relation", "court": "Austria", "delta": -2}),
         "moments.affairs.deck[4].decline.ops"),
        ("an effect outside the ruling's three", lambda b: _aff(b, 4)["edict"].update(effects=[{"type": "actions", "value": 1}]),
         "moments.affairs.deck[4].edict.effects[0]"),
        ("a force-limit floor by decree", lambda b: _aff(b, 4)["edict"].update(effects=[{"type": "force_limit", "tier": "major"}]),
         "moments.affairs.deck[4].edict.effects[0]"),
        ("a clause the seam does not read", lambda b: _aff(b, 4)["edict"].update(effects=[{"type": "supply_capacity", "value": 1.25, "arm": "all"}]),
         "moments.affairs.deck[4].edict.effects[0]"),
        ("three clauses", lambda b: _aff(b, 4)["edict"].update(effects=[{"type": "drill_morale", "value": 5}] * 3),
         "moments.affairs.deck[4].edict.effects"),
        ("a price out of band", lambda b: _aff(b, 4)["edict"].update(price=6000), "moments.affairs.deck[4].edict.price"),
        ("a term out of band", lambda b: _aff(b, 4)["edict"].update(term=3), "moments.affairs.deck[4].edict.term"),
        ("a rest out of band", lambda b: _aff(b, 4)["edict"].update(rest=17), "moments.affairs.deck[4].edict.rest"),
        ("an offer without an edict block", lambda b: _aff(b, 4).pop("edict"), "moments.affairs.deck[4].edict"),
        ("an offer's accept without the admin action", lambda b: _aff(b, 4)["accept"].update(ops=[{"op": "edict"}]),
         "moments.affairs.deck[4].accept.ops"),
        ("an edict op on a bill", lambda b: _aff(b, 1)["accept"]["ops"].append({"op": "edict"}),
         "moments.affairs.deck[1].accept.ops[1]"),
        ("an edict block on a bill", lambda b: _aff(b, 1).update(edict=dict(_aff(b, 4)["edict"])),
         "moments.affairs.deck[1].edict"),
        ("an edict op in a dated letter", lambda b: b["deck"][0]["accept"]["ops"].insert(0, {"op": "edict"}),
         "moments.deck[0].accept.ops[0]"),
        ("a premise naming another entry", lambda b: _aff(b, 4)["when"].update(edict="the_remounts"),
         "moments.affairs.deck[4].when.edict"),
        ("a premise without its entry", lambda b: _aff(b, 4)["when"].pop("edict"), "moments.affairs.deck[4].when.edict"),
        ("a threshold out of band", lambda b: _aff(b, 5)["when"].update(below_pct=95), "moments.affairs.deck[5].when.below_pct"),
        ("a court press past 160", lambda b: _aff(b, 4)["edict"].update(court_press="P" * 161),
         "moments.affairs.deck[4].edict.court_press"),
        ("a decree's name past 40", lambda b: _aff(b, 4)["edict"].update(name="N" * 41), "moments.affairs.deck[4].edict.name"),
    ])
    def test_each_bad_block_is_refused(self, label, mutate, path):
        assert path in _bad(mutate), label


# ═══════════════════════════════════════════════════════════════════════════
# The register and the budget (§12c)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRegisterAndTheBudget:
    def test_the_court_press_fills_its_slots_for_every_court_with_a_deck(self, armed):
        for court, seat in (("Austria", "VIENNA"), ("Prussia", "BERLIN"), ("Russia", "ST PETERSBURG"),
                            ("Britain", "LONDON"), ("Ottoman", "CONSTANTINOPLE")):
            for template in OFFERS:
                e = _entry(armed, template)
                own = AF._seat_of(armed, court)
                text = AF.fill_slots(armed, AF.edict_block(e)["court_press"], {"lord": court, "until": 20}, e,
                                     seat=own, SEAT=own.upper())
                assert "{" not in text and "?" not in text and text.startswith(own.upper()), (court, text)
                if court == "Austria":
                    assert text.startswith(seat)

    def test_no_slot_is_left_open_in_the_reaction_copy(self, armed):
        row = {"id": f"{E1}#1", "lord": "France", "bind": {}, "tier": 1, "turn": 7, "answered_turn": 7, "until": 15}
        for template in OFFERS:
            e = _entry(armed, template)
            for side in ("accept", "decline"):
                for key in ("echo", "situation", "press", "remember"):
                    text = e[side].get(key)
                    if text:
                        filled = AF.fill_slots(armed, text, row, e)
                        assert "{" not in filled and "?" not in filled, (template, side, key, filled)
            assert "{" not in AF.fill_slots(armed, e["line"], row, e)

    def test_the_budget_holds_two_lines_and_no_second_surface(self, armed, client):
        """The answer's two lines, one receipt the morning after and none the
        morning after that, one COURTS line; no popup, no rail notice."""
        _magazines_board(armed)
        _run(armed, range(1, 8))
        notices_before = len(list(getattr(armed.notifications, "notifications", []) or []))
        result = _answer(armed, client, f"{E1}#1", "accept")
        assert len(result["message"].split("\n")) == 2
        assert not armed.incoming_proposal_popup
        assert len(list(getattr(armed.notifications, "notifications", []) or [])) <= notices_before
        _at(armed, 8)
        with _quiet():
            assert len(DP._build_situation(armed, "France")["affair_receipt"]) == 1
        _at(armed, 9)
        with _quiet():
            assert "affair_receipt" not in DP._build_situation(armed, "France")
        from backend.game_logic.gazette import _affair_courts_line
        rows = [ev for ev in armed.event_log if ev.get("type") == "moment" and ev.get("register") == "affair"
                and ev.get("moment") == f"{E1}#1"]
        assert [_affair_courts_line(r) for r in rows if _affair_courts_line(r)] == [
            "PARIS — The Intendance contracts for the magazines of the Grande Armée."]


# ═══════════════════════════════════════════════════════════════════════════
# The client and the frames (the LAWS book's EDICTS block, the slip's term,
# the three letters in the dress) — the second commit
# ═══════════════════════════════════════════════════════════════════════════

FRAME_DATE = "2026_11_02"
AUDITS = REPO / "docs" / "audits"
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
FRAME_STEMS = ("IQ10_AFFAIR_LETTER_THE_MAGAZINES", "IQ10_AFFAIR_LETTER_THE_REMOUNTS",
               "IQ10_AFFAIR_LETTER_CAMPS_OF_INSTRUCTION", "IQ10_LEDGER_LAWS_EDICTS")
SHOT_IDS = ("affair_letter_the_magazines", "affair_letter_the_remounts",
            "affair_letter_camps_of_instruction", "ledger_laws_edicts")


class TestTheClientAndTheFrames:
    def test_the_laws_book_renders_the_edicts_block_without_a_chip(self):
        src = (SCRIPTS / "strategic_ledger.gd").read_text(encoding="utf-8")
        body = src[src.index("func _render_laws_tab"):]
        body = body[:body.index("\nfunc ", 1)]
        for needle in ('laws.get("edicts", null)', "THE EDICTS", "No edict is in force.", '"spoken"',
                       '"status_line"', '"effects"'):
            assert needle in body, needle
        block = body[body.index('laws.get("edicts", null)'):]
        assert "_chip_row(" not in block.split('laws.get("footer"')[0]       # a decree is bought by letter
        assert body.index('laws.get("edicts", null)') < body.index('laws.get("footer"')

    def test_the_slip_prints_the_term(self):
        src = (SCRIPTS / "dispatch_view.gd").read_text(encoding="utf-8")
        body = src[src.index("func _corr_body_bbcode"):]
        body = body[:body.index("\nfunc ", 1)]
        for needle in ('row.get("until_label", "")', '"In force until "', '"Expired "', 'row.get("in_force", false)'):
            assert needle in body, needle

    def test_the_four_shots_are_registered_and_staged(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("iq10_run_captures", REPO / "tools" / "iq10_run_captures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        shots = {s["id"]: s for s in mod.SHOTS}
        for sid, needles in (("affair_letter_the_magazines", ("Daru, Intendant-General", "Stock the magazines", "−2,500 gold · 1 action · 8 turns")),
                             ("affair_letter_the_remounts", ("Dejean, Minister of War", "Buy the remounts", "−1,500 gold · 1 action · 8 turns")),
                             ("affair_letter_camps_of_instruction", ("Berthier, Minister of War", "Form the camps", "−2,000 gold · 1 action · 8 turns")),
                             ("ledger_laws_edicts", ("THE EDICTS", "In force until", "no chip on either"))):
            row = shots[sid]
            assert row["payload"] == sid
            for needle in needles:
                assert needle in row["must_show"], (sid, needle)
        assert shots["ledger_laws_edicts"]["scene"] == "res://scenes/strategic_ledger.tscn" and shots["ledger_laws_edicts"]["tab"] == 7
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        for sid in SHOT_IDS:
            assert f'record("{sid}"' in cap, sid

    def test_the_frames_are_committed_at_both_scales_and_named_in_the_plan(self):
        plan = (REPO / "docs" / "UX_UI_REVIEW_PLAN.md").read_text(encoding="utf-8")
        for stem in FRAME_STEMS:
            for tail in ("", "_X2"):
                png = AUDITS / f"{stem}{tail}_{FRAME_DATE}.png"
                assert png.exists() and png.stat().st_size > 8000, png
            assert stem in plan, stem

    def test_the_record_covers_the_four_at_every_resolution_with_no_red(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS, totals
        record = json.loads((AUDITS / "uxr0" / f"readability_edicts_{FRAME_DATE}.json").read_text(encoding="utf-8"))
        for sid in SHOT_IDS:
            surf = record["surfaces"][sid]
            keys = set(surf["readings"])
            for (w, h) in PHYSICAL_RESOLUTIONS:
                assert any(k.startswith(f"{w}x{h}@") for k in keys), (sid, w, h, keys)
            for key, r in surf["readings"].items():
                assert r["ok"] and r["counts"]["rows"] > 0 and r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, key, r)
        t = totals(record)
        assert t["red"] == 0 and t["p1"] == 0, t


# ═══════════════════════════════════════════════════════════════════════════
# Purity and the censuses (RE3-10's rule; the ratchet)
# ═══════════════════════════════════════════════════════════════════════════

class TestPurityAndTheCensuses:
    def test_every_reader_writes_nothing_on_a_fresh_boot(self):
        from backend.models.world_state import WorldState
        with _quiet():
            world = WorldState.from_scenario(str(SCENARIO))
        assert AF.armed(world) and "affairs" not in world.moments
        before = json.dumps(world.to_dict(), sort_keys=True)
        reforms.supply_capacity_factor(world, "France")
        reforms.drill_morale_bonus(world, "France")
        reforms.recruit_price_terms(world, "France", "cavalry")
        reforms.laws_payload(world, "France")
        reforms.laws_signature(world, "France")
        AF.edicts_in_force(world, "France")
        AF.edict_state(world, "France", _entry(world, E1))
        AF.edict_refusal(world, "France", _entry(world, E1), with_reserve=True)
        AF.last_decree_turn(world, "Austria")
        prior = world.nation_gold["Austria"]
        world.nation_gold["Austria"] = 20_000
        AF.find_ai_edict(world, "Austria", 20_000, 2)
        world.nation_gold["Austria"] = prior
        assert "affairs" not in world.moments
        assert json.dumps(world.to_dict(), sort_keys=True) == before

    def test_the_section_s_one_writer_is_grant_edict(self):
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        start = src.index("# RE-6 — the Edicts")
        end = src.index("# RE-R — the reactions")
        assert start < end
        section = src[start:end]
        writers = [m.start() for m in re.finditer(r"runtime\(world\)", section)]
        grant = section.index("def grant_edict(")
        grant_end = section.index("\ndef ", grant + 1)
        assert writers and all(grant < w < grant_end for w in writers), "a reader called runtime()"
        for forbidden in ("log_event", "add_notification", "queue_dispatch_event", "random."):
            assert forbidden not in section

    def test_the_log_filter_lets_a_court_s_decree_through_without_growing(self):
        from backend.campaign_log import filter_campaign_log
        import inspect
        src = inspect.getsource(filter_campaign_log)
        assert '"law_enacted", "law_repealed", "law_lapsed", "moment"' in src
        assert len(src.splitlines()) <= 500

    def test_the_hash_strips_the_decree_s_copy_and_keeps_its_terms(self):
        import copy
        from tools._s14c_sweep_record import deck_sha
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        reworded = copy.deepcopy(scenario)
        reworded["affairs"]["deck"][4]["edict"]["name"] = "another name"
        reworded["affairs"]["deck"][4]["edict"]["court_press"] = "another press"
        assert deck_sha(reworded) == deck_sha(scenario)
        moved = copy.deepcopy(scenario)
        moved["affairs"]["deck"][4]["edict"]["price"] = 2600
        assert deck_sha(moved) != deck_sha(scenario)
        termed = copy.deepcopy(scenario)
        termed["affairs"]["deck"][4]["edict"]["term"] = 9
        assert deck_sha(termed) != deck_sha(scenario)

    def test_the_trace_counts_the_decree_as_delivered(self, armed):
        from tools._moments_trace import _delivered
        _magazines_board(armed, gold=12_000)
        _at(armed, 7)
        p = MO.plan(armed, _entry(armed, E1), MO.ANSWER_ACCEPT, _occ(E1, turn=7))
        MO._apply(armed, p)
        row = next(r for r in p["rows"] if r["op"] == "edict")
        figures = _delivered(armed, "France", row)
        assert {(f["figure"], f["quoted"], f["delivered"]) for f in figures} == {
            ("treasury", 12_000 - 2_500, 12_000 - 2_500), (f"{E1} in force", 1, 1)}
