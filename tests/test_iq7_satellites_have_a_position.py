"""IQ-7 "The Satellites Have a Position" — the behaviour tests (contract §2,
T1..T21) for "The Client's Petition" and its four grafts (R1 the honest
wavering line, R2 courting spares the lord's allies, R3 the Garrison option
says what it does, R4 the digest sees the web).

Every pin runs on the SHIPPED 1805 board (`europe_1805.json`, seed
`historical` — the suite pins `SOVEREIGN_SCENARIO=none`, so the board is
booted explicitly here) through the real executor, the real
`/respond_to_diplomatic_dialogue` endpoint and the real `end turn` route
(`TurnManager.end_turn`), under the MOCK parser, following the TestClient
world-swap rule (swap `backend.main.world`, `game_state["world"]` and the
parser together). Every lever has a DOWN arm on its own surface.

Measured facts the contract's own text guessed at, recorded here rather than
hidden (the September 16 landing measurements; navigate by symbol):

* T2 — the boot board's FIRST petition is **Switzerland's relief at turn 6,
  price 225 x 8 = 1,800**. The contract's "Holland relief at turn 6, 2,696"
  is the COMMANDED arm's figure: it exists only once the turn-4 peace has
  ended Holland's shared war with Britain (the +2 shared-enemy term is what
  holds Holland's forecast at 0 on the unplayed board, so Holland has no
  subject there). Sorted tag order then puts Holland first.
* T5 — the contract said "stage Rome". Rome is a CAPITAL, and
  `_grant_region_eligibility` refuses the capital of ANY nation, so the
  literal case cannot occur on the real predicate. Worse: every authored
  risorgimento region is KoI-held, a capital (Milan, Naples, Rome) or French
  homeland (Savoy), and Holland's only design is Flanders (French homeland,
  IQ7-D3) — so on the shipped 1805 board no satellite's authored design
  province is ever grantable and `in_design` is unreachable without staging
  the raw deck. The deck-preference pin therefore extends Holland's own
  authored `the_seventeen_provinces` entry by one staged province (the
  raw-deck read the contract prescribes).
* T12 — Prussia's only acquire target is Hanover, a capital, so "a province
  inside Prussia's own active acquire design" is likewise staged: Brunswick
  (Hanover's soil, conquered land for Prussia, adjoining Amsterdam and
  Gelderland) is added to the authored `hanoverian_prize` regions; the
  design stays ACTIVE because Hanover itself is unmet.
* T10 — no non-homeland province adjoins Bern, so Switzerland can never
  receive THE PROVINCE on this board; the province arm of the bond cap is
  pinned on Holland with a staged Brunswick.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import random
import re
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

with contextlib.redirect_stdout(io.StringIO()):
    import backend.main as M
    from backend import campaign_log as CL
    from backend.commands.parser import CommandParser
    from backend.game_logic import agendas as AG
    from backend.game_logic import ai_diplomacy as AD
    from backend.game_logic import battle_report as BR
    from backend.game_logic import coalition as CO
    from backend.game_logic import diplomacy as D
    from backend.game_logic import vassal as V
    from backend.game_logic.ai_diplomacy import deliver_ai_proposal
    from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
    from backend.game_logic.dispatch import _format_dispatch_event_text
    from backend.game_logic.ledger import build_strategic_ledger
    from backend.game_logic.mailbox_payloads import (
        build_pending_envoy_popup_from_terms,
        client_petition_clauses,
        terms_are_a_client_petition,
    )
    from backend.models.world_state import WorldState
    from backend import save_manager as SM

REPO = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
DRIVER = REPO / "tools" / "playtest_driver.py"
PLAYER = "France"
LEVERS = ("THE_CLIENT_PETITIONS", "AN_UNANSWERED_PETITION_IS_REFUSED",
          "COURTING_SPARES_THE_LORDS_ALLIES", "THE_WAVERING_LINE_IS_HONEST",
          # the IQ-7 review round's four (Sept 18, 2026)
          "THE_DEED_HONOURS_THE_PETITION", "THE_LORD_PAYS_TO_GRANT",
          "THE_TRANSFER_SHEDS_THE_REMISSION", "A_RELIEF_OF_NOTHING_IS_WITHDRAWN")
RAW_TAG = "KingdomOfItaly"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


with _quiet():
    _PARSER = CommandParser(use_real_llm=False)


def _seed_module_rng(world_turn=0):
    """The driver's own determinism scheme (`playtest_driver.seed_module_rng`,
    WO-H slice 1): the engine's AI decisions are module-RNG-free, but combat
    jitter, the courting dispatch roll and the bribe roll ride the unseeded
    `random` module, so an unseeded process can lose the Kingdom of Italy to
    Austria before turn 6 on one run and not the next (measured: a KeyError
    on its row in 1 of ~10 processes). Seeded once at boot per world, every
    board-driving pin below is deterministic."""
    digest = hashlib.sha256(f"historical:{world_turn}".encode()).hexdigest()
    random.seed(int(digest, 16) & 0xFFFFFFFF)


def _europe():
    with _quiet():
        world = WorldState.from_scenario(SCENARIO)
    _seed_module_rng()
    return world


def _key(w, a, b):
    return w._make_diplo_key(a, b)


def _rel(w, a, b):
    return int(w.nation_relations.get(_key(w, a, b), 0) or 0)


def _set_rel(w, a, b, value):
    w.nation_relations[_key(w, a, b)] = int(value)


def _set_state(w, a, b, state):
    w.diplomatic_states[_key(w, a, b)] = state
    w.invalidate_active_nations_cache()


def _pending(w):
    dm = w.dialogue_manager
    return ([dm.peek()] if dm.peek() else []) + list(dm.iter_queue())


def _petitions(w):
    return [d for d in _pending(w) if V.is_client_petition(d)]


def _logged(w, outcome=None):
    rows = [e for e in w.event_log if e.get("type") == "client_petition_answered"]
    if outcome is None:
        return rows
    return [e for e in rows if e.get("outcome") == outcome]


def _titles(w):
    return [n.get("title") for n in w.notifications.to_list()]


def _make_proposal(w, vassal):
    """The §1.1 proposal shape — exactly what `process_vassal_petitions`
    hands `deliver_ai_proposal` for a player lord."""
    terms = V.petition_terms(w, vassal)
    assert terms is not None, f"{vassal} has no subject on this board"
    return {
        "source": vassal, "recipient": w.player_nation,
        "proposal_type": V.CLIENT_PETITION_TYPE,
        "terms": {"type": V.CLIENT_PETITION_TYPE, "proposer_nation": vassal,
                  "target_nation": w.player_nation, "demands": [],
                  "sweeteners": [], "petition": terms},
        "talleyrand_assessment": f"{terms['grant_line']} {terms['refuse_line']}",
        "decision_reason": "client_petition", "_force_send": True,
    }


def _deliver(w, vassal):
    with _quiet():
        return deliver_ai_proposal(_make_proposal(w, vassal), w)


def _deliver_seen(w, client, vassal):
    """Deliver, then let ONE response carry the petition popup — the client's
    own sequence (the delivery response shows the question; the answer's
    response shows the result). Slice 6's rule: a response that carries a
    question never carries a popped popup, so an answer posted against an
    unconsumed delivery would defer its own `proposal_result`."""
    dlg = _deliver(w, vassal)
    _cmd(client, "status")
    return dlg


def _only(w, vassal):
    """Park the other satellites below the standing (loyalty 50), so the
    producer's answer is about `vassal` alone."""
    for name, row in w.vassals.items():
        if name != vassal and row["lord"] == PLAYER:
            row["loyalty"] = 50


def _cmd(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


def _respond(client, choice, dialogue_id=None):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice, "dialogue_id": dialogue_id}).json()


def _end_turn(client):
    """One REAL end turn (the executor -> TurnManager.end_turn), answering
    the one ordinary question the unplayed board asks on its own: a French
    corps that wins a battle unbidden (an autonomous attack or a counter-
    punch — combat jitter rides the unseeded `random` module, so it varies
    per process) raises the W6-8 capture question, which is a hard stop on
    `end turn` until answered. It is answered as the driver's default
    policy answers it (`secure`) and the turn is ended again. Any OTHER
    reason a turn does not advance is a test failure with the reason on it —
    never a silently stalled campaign."""
    world = M.game_state["world"]
    before = int(world.current_turn)
    r = _cmd(client, "end turn")
    for _ in range(3):
        pending = world.pending_capture_choice
        if int(world.current_turn) == before + 1 or not pending:
            break
        # stage 1 (plunder / secure), then W6-8's stage 2 (the estate)
        _cmd(client, "respect" if pending.get("stage") == "estate" else "secure")
        r = _cmd(client, "end turn")
    if int(world.current_turn) != before + 1:
        current = world.dialogue_manager.peek() or {}
        raise AssertionError(
            f"end turn did not advance from {before}: success={r.get('success')} "
            f"message={str(r.get('message'))[:400]!r} current_dialogue="
            f"{current.get('type')}/{current.get('target_nation')} "
            f"hard_stop={world.dialogue_manager.is_hard_stop()}")
    return r


def _pre_slice_tribute(w, vassal):
    """The formula every one of the four hand-copies held before IQ-7:
    effective income of the vassal's non-disrupted provinces x tribute_rate.
    No remission arm — this is the pre-slice arithmetic by construction."""
    row = w.vassals[vassal]
    disrupted = w.get_disrupted_regions()
    income = sum(int(w.regions[r].get_effective_income())
                 for r in w.get_nation_regions(vassal) if r not in disrupted)
    return int(income * float(row.get("tribute_rate", 0.5)))


def _stage_tyrol_for_koi(w):
    """T4: Tyrol (Austrian soil, income 150, adjoins Milan) held by France —
    conquered, non-homeland, non-capital, so VS-3 lists it for the Kingdom
    of Italy. Archduke John's corps stands at Tyrol at boot; it is moved so
    the staged province is not a battlefield."""
    w.regions["Tyrol"].controller = PLAYER
    john = w.marshals.get("ArchdukeJohn")
    if john is not None:
        john.location = "Carniola"
    w.invalidate_active_nations_cache()


def _stage_holland_neighbours(w, controller=PLAYER):
    """Brunswick (150), East Frisia (50), Osnabruck (50) — Hanover's soil,
    adjoining Holland's four provinces; held by `controller` they are
    conquered land it may cede."""
    for name in ("Brunswick", "East Frisia", "Osnabruck"):
        w.regions[name].controller = controller
    w.invalidate_active_nations_cache()


def _make_eligible(w, vassal, turn=6):
    """Past the grace (created_turn 1 on the boot board) at `turn`."""
    w.current_turn = int(turn)
    w.vassals[vassal]["created_turn"] = 1


# ═══════════════════════════════════════════════════════════════════════════
# fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _restore_levers(monkeypatch):
    """Every lever flip in this file goes through monkeypatch, so the shipped
    values are restored after each test whatever a test did."""
    for name in LEVERS:
        monkeypatch.setattr(V, name, getattr(V, name))
    yield


@pytest.fixture
def http(monkeypatch):
    world = _europe()
    assert _PARSER.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", _PARSER)
    monkeypatch.setitem(M.game_state, "world", world)
    return world, TestClient(M.app)


@pytest.fixture
def tribute_spy(monkeypatch):
    """Records, per collection, what each vassal OWED at call time (by both
    formulas) and what it actually PAID. `process_vassal_tribute` is imported
    lazily at its one call site (world_state's income phase), so patching the
    module attribute is seen by the engine."""
    real = V.process_vassal_tribute
    records = []

    def spy(world):
        owed = {v: V.vassal_tribute_owed(world, v) for v in world.vassals}
        old = {v: _pre_slice_tribute(world, v) for v in world.vassals}
        events = real(world)
        records.append({"turn": int(world.current_turn), "owed": owed, "old": old,
                        "paid": {v: int(e["amount"]) for v, e in events.items()}})
        return events

    monkeypatch.setattr(V, "process_vassal_tribute", spy)
    return records


# ═══════════════════════════════════════════════════════════════════════════
# T1 — lever-down silence
# ═══════════════════════════════════════════════════════════════════════════

class TestT1LeverDownSilence:
    def test_twenty_end_turns_issue_nothing_and_tribute_is_the_pre_slice_formula(
            self, http, tribute_spy, monkeypatch):
        w, client = http
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        for _ in range(20):
            _end_turn(client)
            assert not _petitions(w), f"a petition was issued at turn {w.current_turn}"
            for name, row in w.vassals.items():
                assert "petitioned_turn" not in row, name
                assert "remission_left" not in row, name
        assert w.current_turn == 21
        assert not _logged(w)
        # 20 collections: what each satellite PAID is the pre-slice arithmetic
        # (effective income x rate, disruption skipped) on every one of them.
        assert len(tribute_spy) == 20
        for rec in tribute_spy:
            for vassal, old in rec["old"].items():
                assert rec["owed"][vassal] == old, (rec["turn"], vassal)
                if old > 0:
                    assert rec["paid"].get(vassal, 0) == old, (rec["turn"], vassal, rec)

    def test_lever_down_hides_the_display_keys_and_the_producer_returns_nothing(
            self, monkeypatch):
        w = _europe()
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        _make_eligible(w, "Switzerland")
        assert V.process_vassal_petitions(w) == []
        assert not _petitions(w)
        for row in build_diplomatic_ledger(w)["vassals"]["rows"]:
            for key in ("standing", "next_petition_in", "bond", "remission_left",
                        "relation", "relation_modifier"):
                assert key not in row, (row["name"], key)

    def test_lever_down_still_honours_a_stored_remission(self, monkeypatch):
        """Keyed on the DATA: a remission in a save is paid down with the
        lever down (the `vassal_tribute_owed` 0 arm reads the row, never the
        lever)."""
        w = _europe()
        w.vassals["Switzerland"]["remission_left"] = 2
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        assert V.vassal_tribute_owed(w, "Switzerland") == 0
        with _quiet():
            V.process_vassal_tribute(w)
        assert w.vassals["Switzerland"]["remission_left"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# T2 — issuance on the boot board, through the real end-turn route
# ═══════════════════════════════════════════════════════════════════════════

class TestT2IssuanceOnTheBootBoard:
    def test_the_first_petition_is_switzerlands_relief_at_turn_six(self, http):
        w, client = http
        for _ in range(4):
            _end_turn(client)
            assert not _petitions(w), f"early petition at turn {w.current_turn}"
        assert w.current_turn == 5
        _end_turn(client)
        assert w.current_turn == 6
        pets = _petitions(w)
        assert len(pets) == 1
        dlg = pets[0]
        pet = dlg["context"]["proposal"]["petition"]
        assert dlg["target_nation"] == "Switzerland"
        assert pet["subject"] == "relief"
        # price = tribute owed x collections; on the historical seed 225 x 8.
        assert pet["price"] == V.vassal_tribute_owed(w, "Switzerland") * V.REMISSION_COLLECTIONS
        assert pet["price"] == 1800
        assert pet["collections"] == V.REMISSION_COLLECTIONS == 8
        # the shape the transport needs
        assert dlg["type"] == "incoming_proposal"
        assert dlg.get("dialogue_id") is not None
        assert dlg["context"]["proposal_type"] == V.CLIENT_PETITION_TYPE
        assert [o["label"] for o in dlg["options"]] == ["Grant the petition",
                                                         "Refuse the petition"]
        assert [o["action"] for o in dlg["options"]] == ["accept_ai_proposal",
                                                          "reject_ai_proposal"]
        assert not any("counter" in str(o.get("action", "")).lower()
                       for o in dlg["options"])
        payload = dlg["popup_payload"]
        assert payload.get("is_petition") is True
        assert payload["proposal_type_display"] == "Client's Petition"
        # the cadence stamp, at ISSUE, on the petitioner only
        assert w.vassals["Switzerland"]["petitioned_turn"] == 6
        for other in ("Holland", RAW_TAG):
            assert "petitioned_turn" not in w.vassals.get(other, {}), other
        assert "Petition from Switzerland" in _titles(w)
        # it is a mailbox row the player can browse to (queued behind the
        # boot coalition's settlement offer on this turn — measured)
        with _quiet():
            mailbox = client.get("/mailbox").json()
        rows = [i for i in mailbox["items"] if i.get("proposal_type") == V.CLIENT_PETITION_TYPE]
        assert len(rows) == 1
        assert rows[0]["source_nation"] == "Switzerland"
        assert rows[0]["item_type"] == "incoming_proposal"
        assert rows[0]["mailbox_id"] == dlg.get("mailbox_id")

    def test_holland_has_no_subject_on_the_unplayed_board(self):
        """The contract's 'Holland relief at turn 6' is the COMMANDED arm's:
        at boot Holland's shared war with Britain (+2) cancels its drift, so
        the forecast is 0 and the ladder ends. Recorded, not hidden."""
        w = _europe()
        assert V.forecast_vassal_loyalty(w, PLAYER, "Holland")["forecast"] == 0
        assert V.petition_subject(w, "Holland") is None
        assert V.forecast_vassal_loyalty(w, PLAYER, "Switzerland")["forecast"] == -2
        assert V.petition_subject(w, "Switzerland")["subject"] == "relief"


# ═══════════════════════════════════════════════════════════════════════════
# T3 — the relief grant, shown = applied through every reader
# ═══════════════════════════════════════════════════════════════════════════

class TestT3ReliefGrantShownEqualsApplied:
    def test_grant_then_eight_remitted_collections_then_tribute_resumes(
            self, http, tribute_spy):
        w, client = http
        w.vassals["Switzerland"]["loyalty"] = 85
        dlg = _deliver_seen(w, client, "Switzerland")
        pet = dlg["context"]["proposal"]["petition"]
        dp0, rel0 = w.diplomatic_points, _rel(w, "Switzerland", PLAYER)
        r = _respond(client, "grant the petition", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert r["proposal_result"]["outcome"] == "ACCEPT"
        assert r["proposal_result"]["proposal_type"] == "Client's Petition"
        row = w.vassals["Switzerland"]
        assert row["loyalty"] == 85 + pet["loyalty_gain"] == 95
        assert _rel(w, "Switzerland", PLAYER) == rel0 + pet["relation_step"] == 20
        assert w.diplomatic_points == dp0 - 1
        assert row["remission_left"] == 8
        assert not _petitions(w)
        assert "Petition from Switzerland" not in _titles(w)
        assert len(_logged(w, "granted")) == 1
        assert "remitted for 8 collections" in r["message"]
        assert f"({pet['price']}g forgone)" in r["message"]

        # eight collections at 0, every reader agreeing before each one
        for k in range(8):
            assert row["remission_left"] == 8 - k
            assert V.vassal_tribute_owed(w, "Switzerland") == 0
            with _quiet():
                preview = D.get_diplomatic_preview(w, "Switzerland")
            assert preview["vassal_tribute"] == 0
            card = next(x for x in build_diplomatic_ledger(w)["vassals"]["rows"]
                        if x["name"] == "Switzerland")
            assert card["tribute"] == 0 and card["remission_left"] == 8 - k
            projection = build_strategic_ledger(w)["economy"]["vassal_tribute"]
            assert projection == sum(V.vassal_tribute_owed(w, v) for v, s in w.vassals.items()
                                     if s["lord"] == PLAYER)
            _end_turn(client)
            rec = tribute_spy[-1]
            assert rec["owed"]["Switzerland"] == 0
            assert rec["paid"].get("Switzerland", 0) == 0
            # the applied France bucket is exactly what the collections moved
            applied = w._applied_income_transfers["vassal_tribute"].get(PLAYER, 0)
            assert applied == sum(rec["paid"].values())
        assert row["remission_left"] == 0
        # the ninth collection: tribute resumes at the owed figure
        assert V.vassal_tribute_owed(w, "Switzerland") > 0
        _end_turn(client)
        rec = tribute_spy[-1]
        assert rec["owed"]["Switzerland"] > 0
        assert rec["paid"]["Switzerland"] == rec["owed"]["Switzerland"]

    def test_the_relief_gain_is_grip_blunted_like_invest(self):
        """+10 x get_authority_lever_multiplier(grip) — the quote and the
        grant agree, and in the spiral band both are the blunted figure."""
        from backend.models.authority import get_authority_lever_multiplier
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 60
        terms = V.petition_terms(w, "Switzerland")
        mult = get_authority_lever_multiplier(w, PLAYER)
        assert terms["loyalty_gain"] == int(V.PETITION_RELIEF_LOYALTY * mult)
        res = V.grant_petition(w, "Switzerland", PLAYER, terms)
        assert res["success"] and res["loyalty_gain"] == terms["loyalty_gain"]
        assert w.vassals["Switzerland"]["loyalty"] == 60 + terms["loyalty_gain"]

    @pytest.mark.parametrize("grip,mult", [(100, 1.0), (10, 0.4)])
    def test_the_blunting_binds_at_a_spiral_grip_in_quote_and_grant_and_never_on_refusal(
            self, monkeypatch, grip, mult):
        """IQ-7 review [39] (R11, Sept 18, 2026): the pin above runs at the
        boot grip of 100, where the multiplier is 1.0 and "blunted" cannot
        be told from "not blunted". Staged at grip 10 (the spiral band) the
        quote AND the grant are the blunted +4, the refusal and the lapse
        still cost the full 10 (VS-R Q3: never blunted), and the healthy
        arm is the control that the staging itself is what moves it."""
        import backend.models.authority as AUTH
        monkeypatch.setattr(AUTH, "get_imperial_grip", lambda world, nation: grip)
        assert AUTH.get_authority_lever_multiplier(_europe(), PLAYER) == mult
        expected = int(V.PETITION_RELIEF_LOYALTY * mult)
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 60
        terms = V.petition_terms(w, "Switzerland")
        assert terms["loyalty_gain"] == expected and f"loyalty +{expected}" in terms["grant_line"]
        assert V.reprice_petition(w, PLAYER, "Switzerland", terms)["loyalty_gain"] == expected
        res = V.grant_petition(w, "Switzerland", PLAYER, terms)
        assert res["loyalty_gain"] == expected and f"Loyalty +{expected} (60 → {60 + expected})" in res["message"]
        assert w.vassals["Switzerland"]["loyalty"] == 60 + expected
        for how in ("refused", "unanswered"):
            w2 = _europe()
            w2.vassals["Switzerland"]["loyalty"] = 60
            t2 = V.petition_terms(w2, "Switzerland")
            assert t2["refusal_loyalty_applied"] == V.PETITION_REFUSAL_LOYALTY == 10
            r2 = V.refuse_petition(w2, "Switzerland", PLAYER, t2, how=how)
            assert r2["penalty"] is True and w2.vassals["Switzerland"]["loyalty"] == 50, how
            assert V.lapse_forecast(w2, "Switzerland", PLAYER, t2)["loyalty_loss"] == 10


# ═══════════════════════════════════════════════════════════════════════════
# T4 / T5 — THE PROVINCE, and the deck's price
# ═══════════════════════════════════════════════════════════════════════════

class TestT4TheProvinceSubject:
    def test_the_petition_names_tyrol_and_the_grant_cedes_it(self, http):
        """Flipped consciously, IQ-7 review round (Sept 18, 2026), R4/[04]:
        the quoted `loyalty_gain` is CLAMPED to `LOYALTY_MAX − loyalty` (a
        client at 100 is quoted +0 and told its loyalty is already full),
        so the quote is now staged BELOW the ceiling (loyalty 80 before
        issue, where it equals the raw worth) and the at-ceiling arm is
        pinned separately; and R10: the court carries its article
        ("ceded to the Kingdom of Italy")."""
        w, client = http
        _stage_tyrol_for_koi(w)
        # the at-ceiling arm: boot loyalty 100 -> the quote says so
        ceiling = V.petition_terms(w, RAW_TAG)
        assert w.vassals[RAW_TAG]["loyalty"] == 100
        assert ceiling["loyalty_gain"] == 0 and ceiling["loyalty_gain_raw"] == 10
        assert ceiling["loyalty_full"] is True
        assert "loyalty +0 (its loyalty is already full)" in ceiling["grant_line"]
        w.vassals[RAW_TAG]["loyalty"] = 80
        terms = V.petition_terms(w, RAW_TAG)
        assert terms["subject"] == "province" and terms["region"] == "Tyrol"
        assert terms["in_design"] is False
        assert terms["loyalty_gain"] == V.grant_loyalty_bonus(150) == 10
        _make_eligible(w, RAW_TAG)
        with _quiet():
            V.process_vassal_petitions(w)
        pets = _petitions(w)
        assert len(pets) == 1 and pets[0]["target_nation"] == RAW_TAG
        pet = pets[0]["context"]["proposal"]["petition"]
        assert pet["region"] == "Tyrol"
        loy0, dp0, rel0 = w.vassals[RAW_TAG]["loyalty"], w.diplomatic_points, _rel(w, RAW_TAG, PLAYER)
        assert loy0 == 80
        r = _respond(client, "grant the petition", pets[0]["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        row = w.vassals[RAW_TAG]
        assert w.regions["Tyrol"].controller == RAW_TAG
        assert row["granted_regions"] == ["Tyrol"]
        assert row["grant_cooldown"] == V.GRANT_COOLDOWN
        assert row["loyalty"] == loy0 + pet["loyalty_gain"]
        assert w.diplomatic_points == dp0 - V.GRANT_DP_COST
        assert _rel(w, RAW_TAG, PLAYER) == rel0 + pet["relation_step"]
        log = _logged(w, "granted")
        assert len(log) == 1 and log[0]["region"] == "Tyrol" and log[0]["subject"] == "province"
        assert CL.format_event_oneliner(log[0]) == "The Kingdom of Italy's petition for Tyrol — granted."
        assert "Tyrol is ceded to the Kingdom of Italy" in r["message"]

    def test_a_settling_grant_sends_the_ladder_past_the_province(self):
        w = _europe()
        _stage_tyrol_for_koi(w)
        w.vassals[RAW_TAG]["grant_cooldown"] = 2
        # forecast +2 at boot (garrisoned, shared war) -> no relief either
        assert V.petition_subject(w, RAW_TAG) is None


class TestT5TheDecksPrice:
    def test_a_design_province_outranks_a_richer_one_and_carries_the_note(self, http):
        w, client = http
        _stage_holland_neighbours(w)
        grantable = [e["region"] for e in V.list_grantable_regions(w, "Holland", actor=PLAYER)]
        assert grantable == ["Brunswick", "East Frisia", "Osnabruck"]   # richest first
        # the authored deck (Flanders — French homeland, IQ7-D3) extended by
        # a staged province; the raw deck is what the ladder reads
        entry = w.agendas["Holland"][0]
        assert entry["id"] == "the_seventeen_provinces"
        entry["regions"] = list(entry["regions"]) + ["Osnabruck"]
        terms = V.petition_terms(w, "Holland")
        assert terms["region"] == "Osnabruck" and terms["in_design"] is True
        assert terms["income"] == 50
        assert terms["design_note"] == ("Osnabruck belongs to Holland's own design — "
                                        "The Seventeen Provinces, the dream of United Netherlands.")
        dlg = _deliver(w, "Holland")
        assert dlg["popup_payload"]["clauses"][0] == terms["design_note"]
        assert terms["design_note"] in dlg["talleyrand_text"]

    def test_without_a_deck_stake_the_richest_province_is_named(self):
        w = _europe()
        _stage_holland_neighbours(w)
        terms = V.petition_terms(w, "Holland")
        assert terms["region"] == "Brunswick" and terms["in_design"] is False
        assert terms["design_note"] == ""


# ═══════════════════════════════════════════════════════════════════════════
# T6 / T7 / T8 — refuse, lapse, counter
# ═══════════════════════════════════════════════════════════════════════════

class TestT6Refuse:
    def test_refusal_prices_the_client_and_never_touches_the_ai3_ladder(self, http, monkeypatch):
        w, client = http
        calls = []
        real_cool = AD.apply_rejection_cooldowns
        real_refusal = AD.record_diplomatic_refusal
        real_schemer = CO.record_schemer_peace_rejection
        monkeypatch.setattr(AD, "apply_rejection_cooldowns",
                            lambda *a, **k: calls.append("cooldowns") or real_cool(*a, **k))
        monkeypatch.setattr(AD, "record_diplomatic_refusal",
                            lambda *a, **k: calls.append("refusal") or real_refusal(*a, **k))
        monkeypatch.setattr(CO, "record_schemer_peace_rejection",
                            lambda *a, **k: calls.append("schemer") or real_schemer(*a, **k))
        dlg = _deliver_seen(w, client, "Switzerland")
        refusals0 = copy.deepcopy(w.diplomatic_refusals)
        cooldowns0 = copy.deepcopy(w.ai_proposal_cooldowns)
        dp0, rel0 = w.diplomatic_points, _rel(w, "Switzerland", PLAYER)
        r = _respond(client, "refuse the petition", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert w.vassals["Switzerland"]["loyalty"] == 100 - V.PETITION_REFUSAL_LOYALTY
        assert _rel(w, "Switzerland", PLAYER) == rel0 - V.PETITION_RELATION_STEP
        assert w.diplomatic_points == dp0
        assert calls == []
        assert w.diplomatic_refusals == refusals0
        assert w.ai_proposal_cooldowns == cooldowns0
        assert not any(e.get("type") == "ai_proposal_rejected" for e in w.event_log)
        log = _logged(w, "refused")
        assert len(log) == 1 and log[0]["penalty"] is True
        # IQ-7 review R8(e) (Sept 18, 2026): the one-liner carries the price.
        assert CL.format_event_oneliner(log[0]) == (
            "Switzerland's petition for relief from tribute — refused: "
            f"loyalty 100 → 90, bond {rel0} → {rel0 - V.PETITION_RELATION_STEP}.")
        assert not _petitions(w)
        assert r["proposal_result"]["outcome"] == "REJECT"
        assert r["proposal_result"]["proposal_type"] == "Client's Petition"
        assert "Nothing is charged" in r["message"]

    def test_the_bare_reject_keyword_reaches_the_same_arm(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        r = _respond(client, "reject", dlg["dialogue_id"])
        assert r.get("success") is True
        assert w.vassals["Switzerland"]["loyalty"] == 90
        assert len(_logged(w, "refused")) == 1


class TestT7Lapse:
    @pytest.fixture(autouse=True)
    def _pre_sr1d_league(self, monkeypatch):
        """SR-1d (September 26, 2026): PR-D1b gates the league's turn-4 offer,
        so on the shipped board no settlement offer holds the current slot at
        turn 6 — the "ordinary board" pin below stages its queued petition
        behind that letter and runs with the lever down, as the ruling
        allows (the class measures the lapse, not the league's cadence)."""
        from backend.game_logic import ai_diplomacy as _AD
        monkeypatch.setattr(_AD, "THE_LEAGUE_TREATS_WHEN_SPENT", False)

    def test_an_unanswered_petition_lapses_as_a_refusal_through_the_real_end_turn(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        rel0 = _rel(w, "Switzerland", PLAYER)
        _end_turn(client)
        log = _logged(w, "unanswered")
        assert len(log) == 1
        row = log[0]
        assert row["penalty"] is True
        assert row["loyalty_after"] == row["loyalty_before"] - V.PETITION_REFUSAL_LOYALTY
        assert row["relation_before"] == rel0
        assert row["relation_after"] == rel0 - V.PETITION_RELATION_STEP
        # IQ-7 review R8(e) (Sept 18, 2026): the one-liner carries the price.
        assert CL.format_event_oneliner(row) == (
            "Switzerland's petition for relief from tribute — left unanswered, "
            f"refused: loyalty {row['loyalty_before']} → {row['loyalty_after']}, "
            f"bond {rel0} → {rel0 - V.PETITION_RELATION_STEP}.")
        assert not _petitions(w)
        assert not any(d.get("dialogue_id") == dlg["dialogue_id"] for d in _pending(w))
        # the generic lapse bookkeeping still ran for the vassal — benign, recorded
        assert any(e.get("type") == "offer_lapsed" and e.get("nation") == "Switzerland"
                   and e.get("proposal_type") == V.CLIENT_PETITION_TYPE for e in w.event_log)

    def test_lever_down_a_lapse_costs_nothing(self, http, monkeypatch):
        w, client = http
        monkeypatch.setattr(V, "AN_UNANSWERED_PETITION_IS_REFUSED", False)
        _deliver(w, "Switzerland")
        rel0 = _rel(w, "Switzerland", PLAYER)
        _end_turn(client)
        log = _logged(w, "unanswered")
        assert len(log) == 1
        assert log[0]["penalty"] is False
        assert log[0]["loyalty_after"] == log[0]["loyalty_before"]
        assert log[0]["relation_after"] == rel0
        assert CL.format_event_oneliner(log[0]) == ("Switzerland's petition for relief from "
                                                    "tribute — left unanswered.")
        assert not _petitions(w)

    def test_the_lapse_line_states_the_rule_in_force(self, monkeypatch):
        w = _europe()
        assert V.petition_terms(w, "Switzerland")["lapse_line"].endswith("a lapse is a refusal.")
        monkeypatch.setattr(V, "AN_UNANSWERED_PETITION_IS_REFUSED", False)
        line = V.petition_terms(w, "Switzerland")["lapse_line"]
        assert "lapse is a refusal" not in line
        assert f"waits {V.PETITION_INTERVAL_TURNS} turns" in line

    # ── IQ-7 review [38] (R11, Sept 18, 2026): the pins above hand-deliver
    # the petition onto an EMPTY manager, where it is the current dialogue;
    # on the shipped board it is always QUEUED (behind the boot coalition's
    # settlement offer at turn 6), and the lapse hook's capture over
    # `[peek()] + iter_queue()` is the branch real play uses. A peek-only
    # capture left every ordinary lapse free with these pins green.

    def test_the_queued_petition_on_the_ordinary_board_lapses_as_a_refusal(self, http):
        w, client = http
        for _ in range(5):
            _end_turn(client)
        assert w.current_turn == 6
        pets = _petitions(w)
        assert len(pets) == 1 and pets[0]["target_nation"] == "Switzerland"
        head = w.dialogue_manager.peek()
        assert head is not pets[0] and head.get("type") == "incoming_settlement_offer"
        assert pets[0] in list(w.dialogue_manager.iter_queue())
        rel0 = _rel(w, "Switzerland", PLAYER)
        _end_turn(client)
        log = _logged(w, "unanswered")
        assert len(log) == 1 and log[0]["penalty"] is True
        assert log[0]["loyalty_after"] == log[0]["loyalty_before"] - V.PETITION_REFUSAL_LOYALTY
        assert _rel(w, "Switzerland", PLAYER) == rel0 - V.PETITION_RELATION_STEP
        assert not _petitions(w)

    def test_a_petition_queued_behind_a_letter_lapses_as_a_refusal(self, http):
        """The deterministic twin: a routine letter delivered FIRST holds
        the current slot, so the petition is queued whatever the board's
        mail timing does."""
        w, client = http
        letter = {"source": "Prussia", "recipient": PLAYER, "proposal_type": "non_aggression",
                  "priority": 1,
                  "terms": {"type": "non_aggression", "proposer_nation": "Prussia",
                            "target_nation": PLAYER, "clauses": ["non_aggression"],
                            "sweeteners": [], "demands": []},
                  "talleyrand_assessment": "", "decision_reason": "hegemony_pressure",
                  "turn_generated": 1}
        with _quiet():
            head = deliver_ai_proposal(letter, w)
        dlg = _deliver(w, "Switzerland")
        assert w.dialogue_manager.peek() is head and dlg in list(w.dialogue_manager.iter_queue())
        rel0 = _rel(w, "Switzerland", PLAYER)
        _end_turn(client)
        log = _logged(w, "unanswered")
        assert len(log) == 1 and log[0]["penalty"] is True
        assert _rel(w, "Switzerland", PLAYER) == rel0 - V.PETITION_RELATION_STEP
        # both lapsed (the new turn's own mail may have arrived since)
        assert not _petitions(w) and head not in _pending(w)

    def test_lever_down_a_petition_pending_in_a_save_still_lapses_as_a_refusal(self, monkeypatch):
        """Keyed on the DATA, never on the issuing lever (the hook's own
        docstring): a save with a pending petition, loaded with
        `THE_CLIENT_PETITIONS` down, still charges the lapse."""
        w = _europe()
        _deliver(w, "Switzerland")
        with _quiet():
            w2 = WorldState.from_dict(w.to_dict())
        assert len(_petitions(w2)) == 1
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        monkeypatch.setattr(M, "world", w2)
        monkeypatch.setattr(M, "parser", _PARSER)
        monkeypatch.setitem(M.game_state, "world", w2)
        client = TestClient(M.app)
        rel0 = _rel(w2, "Switzerland", PLAYER)
        _end_turn(client)
        log = _logged(w2, "unanswered")
        assert len(log) == 1 and log[0]["penalty"] is True
        assert _rel(w2, "Switzerland", PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_the_mailbox_road_answers_the_queued_petition(self, http):
        w, client = http
        for _ in range(5):
            _end_turn(client)
        dlg = _petitions(w)[0]
        assert w.dialogue_manager.peek() is not dlg
        with _quiet():
            act = client.post("/mailbox/activate", json={"mailbox_id": dlg["mailbox_id"]}).json()
        assert act.get("success") is True and act["incoming_proposal"]["is_petition"] is True
        assert w.dialogue_manager.peek() is dlg
        r = _respond(client, "grant the petition", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        # one popup a response: the re-queued settlement offer's may ride
        # the answer's, and the verdict then the next
        verdict = r.get("proposal_result") or _cmd(client, "status").get("proposal_result")
        assert verdict["outcome"] == "ACCEPT" and verdict["proposal_type"] == "Client's Petition"
        assert w.vassals["Switzerland"]["remission_left"] == V.REMISSION_COLLECTIONS
        assert len(_logged(w, "granted")) == 1 and not _petitions(w)


class TestT8CounterIsRefusedFree:
    def test_counter_through_the_endpoint(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        dp0, rel0, loy0 = w.diplomatic_points, _rel(w, "Switzerland", PLAYER), w.vassals["Switzerland"]["loyalty"]
        r = _respond(client, "counter", dlg["dialogue_id"])
        assert r.get("success") is False
        assert w.diplomatic_points == dp0
        assert _petitions(w) and _petitions(w)[0] is dlg
        assert _rel(w, "Switzerland", PLAYER) == rel0
        assert w.vassals["Switzerland"]["loyalty"] == loy0
        assert not _logged(w)

    def test_counter_at_the_executor_guard(self, http):
        """The dialogue offers no counter option, so the endpoint re-prompts
        before the handler is reached; the guard is the typed route's and the
        driver's honest floor, exercised directly."""
        w, client = http
        dlg = _deliver(w, "Switzerland")
        dp0 = w.diplomatic_points
        with _quiet():
            r = M.executor._handle_counter_ai_proposal(dlg, w)
        assert r["success"] is False
        assert "granted or refused" in r["message"] and "not bargained" in r["message"]
        assert w.diplomatic_points == dp0
        assert _petitions(w) and _petitions(w)[0] is dlg


# ═══════════════════════════════════════════════════════════════════════════
# T9 — eligibility gates (the producer, on the shipped board)
# ═══════════════════════════════════════════════════════════════════════════

class TestT9EligibilityGates:
    def _issue(self, w):
        with _quiet():
            V.process_vassal_petitions(w)
        return _petitions(w)

    def test_a_loyalty_59_never_petitions_60_does(self):
        w = _europe()
        _make_eligible(w, "Switzerland")
        _only(w, "Switzerland")
        w.vassals["Switzerland"]["loyalty"] = V.PETITION_LOYAL_MIN - 1
        assert self._issue(w) == []
        assert "petitioned_turn" not in w.vassals["Switzerland"]
        w.vassals["Switzerland"]["loyalty"] = V.PETITION_LOYAL_MIN
        assert [d["target_nation"] for d in self._issue(w)] == ["Switzerland"]

    def test_b_the_grace_since_creation(self):
        w = _europe()
        w.current_turn = 6
        w.vassals["Switzerland"]["created_turn"] = 2      # 4 turns: no
        assert self._issue(w) == []
        w.vassals["Switzerland"]["created_turn"] = 1      # 5 turns: yes
        assert len(self._issue(w)) == 1

    def test_c_the_cadence_since_the_last_petition(self):
        w = _europe()
        _make_eligible(w, "Switzerland", turn=20)
        w.vassals["Switzerland"]["petitioned_turn"] = 20 - (V.PETITION_INTERVAL_TURNS - 1)
        assert self._issue(w) == []
        assert w.vassals["Switzerland"]["petitioned_turn"] == 13
        w.vassals["Switzerland"]["petitioned_turn"] = 20 - V.PETITION_INTERVAL_TURNS
        assert len(self._issue(w)) == 1
        assert w.vassals["Switzerland"]["petitioned_turn"] == 20

    def test_d_a_disrupted_province_blocks(self):
        w = _europe()
        _make_eligible(w, RAW_TAG)
        _only(w, RAW_TAG)
        _set_rel(w, RAW_TAG, PLAYER, -100)                # forecast +2-5 -> relief
        assert V.petition_subject(w, RAW_TAG)["subject"] == "relief"
        john = w.marshals["ArchdukeJohn"]                 # Austria, at WAR with KoI
        assert w.get_diplomatic_state("Austria", RAW_TAG) == "WAR"
        john.location = "Milan"
        assert "Milan" in w.get_disrupted_regions()
        assert self._issue(w) == []
        assert "petitioned_turn" not in w.vassals[RAW_TAG]
        john.location = "Tyrol"
        assert "Milan" not in w.get_disrupted_regions()
        assert [d["target_nation"] for d in self._issue(w)] == [RAW_TAG]

    def test_e_a_lord_with_no_dp_is_not_asked(self):
        w = _europe()
        _make_eligible(w, "Switzerland")
        w.diplomatic_points = 0
        assert self._issue(w) == []
        assert "petitioned_turn" not in w.vassals["Switzerland"]
        w.diplomatic_points = V.PETITION_DP_COST
        assert len(self._issue(w)) == 1
        assert w.diplomatic_points == V.PETITION_DP_COST     # read, never charged at issue

    def test_f_a_standing_remission_blocks(self):
        """On the RELIEF ladder the gate is masked by construction — a
        remitted client owes 0 tribute, so (g) ends the ladder first (the
        first sweep reported the relief-shaped pin INERT). The gate binds on
        THE PROVINCE: a grantable province while a remission stands."""
        w = _europe()
        _make_eligible(w, "Holland")
        _only(w, "Holland")
        _stage_holland_neighbours(w)
        w.vassals["Holland"]["remission_left"] = 3
        assert V.petition_subject(w, "Holland")["subject"] == "province"   # a subject exists
        assert self._issue(w) == []                                        # ...and (f) blocks it
        assert "petitioned_turn" not in w.vassals["Holland"]
        w.vassals["Holland"]["remission_left"] = 0
        pets = self._issue(w)
        assert len(pets) == 1
        assert pets[0]["context"]["proposal"]["petition"]["subject"] == "province"
        # and the relief ladder under a remission has nothing to ask for
        w2 = _europe()
        w2.vassals["Switzerland"]["remission_left"] = 3
        assert V.petition_subject(w2, "Switzerland") is None

    def test_g_no_subject_no_petition(self):
        w = _europe()
        _make_eligible(w, "Holland")
        _only(w, "Holland")
        assert V.petition_terms(w, "Holland") is None
        assert self._issue(w) == []
        assert "petitioned_turn" not in w.vassals["Holland"]

    def test_at_most_one_petition_per_lord_per_turn_in_sorted_tag_order(self):
        w = _europe()
        w.current_turn = 6
        for name in ("Holland", RAW_TAG, "Switzerland"):
            w.vassals[name]["created_turn"] = 1
        _set_rel(w, "Holland", PLAYER, -20)               # 0 - 1 -> relief
        _set_rel(w, RAW_TAG, PLAYER, -100)                # +2 - 5 -> relief
        for name in ("Holland", RAW_TAG, "Switzerland"):
            assert V.petition_subject(w, name) is not None, name
        pets = self._issue(w)
        assert [d["target_nation"] for d in pets] == ["Holland"]
        assert w.vassals["Holland"]["petitioned_turn"] == 6
        assert "petitioned_turn" not in w.vassals[RAW_TAG]
        assert "petitioned_turn" not in w.vassals["Switzerland"]

    def test_two_lords_each_get_one_petition_on_the_same_turn(self):
        """IQ-7 review [40] (R11, Sept 18, 2026): the pin above puts every
        satellite under France, so "one per LORD" could not be told from
        "one per TURN, world-wide". Holland under Prussia (sorted first)
        and Switzerland under France, both eligible on one turn: Prussia's
        in-place answer AND France's dialogue, both stamps, the Kingdom of
        Italy (no subject) unstamped."""
        w = _holland_under_prussia()
        w.current_turn = 6
        for name in ("Holland", RAW_TAG, "Switzerland"):
            w.vassals[name]["created_turn"] = 1
        assert V.petition_subject(w, "Holland")["subject"] == "relief"
        assert V.petition_subject(w, "Switzerland")["subject"] == "relief"
        assert V.petition_subject(w, RAW_TAG) is None
        pets = self._issue(w)
        assert [d["target_nation"] for d in pets] == ["Switzerland"]
        assert [(e["vassal"], e["lord"], e["subject"], e["outcome"])
                for e in _logged(w)] == [("Holland", "Prussia", "relief", "granted")]
        assert w.nation_dp["Prussia"] == 2
        assert w.vassals["Holland"]["petitioned_turn"] == 6
        assert w.vassals["Switzerland"]["petitioned_turn"] == 6
        assert "petitioned_turn" not in w.vassals[RAW_TAG]


# ═══════════════════════════════════════════════════════════════════════════
# T10 — the bond
# ═══════════════════════════════════════════════════════════════════════════

class TestT10TheBond:
    def test_two_relief_grants_bond_the_client_and_end_the_relief(self):
        w = _europe()
        w.diplomatic_points = 10
        first = V.petition_terms(w, "Switzerland")
        assert first["relation_step"] == 20 and first["standing_after_grant"] == 1
        assert V.grant_petition(w, "Switzerland", PLAYER, first)["success"]
        assert _rel(w, "Switzerland", PLAYER) == 20
        w.vassals["Switzerland"]["remission_left"] = 0     # the collections have run
        second = V.petition_terms(w, "Switzerland")
        assert second is not None and second["subject"] == "relief"
        assert second["standing_now"] == 1 and second["standing_after_grant"] == 2
        assert V.grant_petition(w, "Switzerland", PLAYER, second)["success"]
        assert _rel(w, "Switzerland", PLAYER) == V.PETITION_BOND_CAP == 40
        fc = V.forecast_vassal_loyalty(w, PLAYER, "Switzerland")
        assert fc["relation_modifier"] == 2 and fc["forecast"] >= 0
        w.vassals["Switzerland"]["remission_left"] = 0
        assert V.petition_terms(w, "Switzerland") is None
        _make_eligible(w, "Switzerland", turn=20)
        with _quiet():
            assert V.process_vassal_petitions(w) == []
        assert not _petitions(w)
        # the bond does not decay: ten real advances leave it at 40
        with _quiet():
            for _ in range(10):
                w.advance_turn()
        assert _rel(w, "Switzerland", PLAYER) == 40
        assert "Switzerland" in w.vassals
        # a third grant cannot lift it past the cap
        third = V.grant_petition(w, "Switzerland", PLAYER, {"subject": "relief"})
        assert third["success"] and third["relation_step"] == 0
        assert _rel(w, "Switzerland", PLAYER) == 40

    def test_a_province_grant_at_the_cap_leaves_the_relation_at_forty(self):
        w = _europe()
        _stage_holland_neighbours(w)
        _set_rel(w, "Holland", PLAYER, 40)
        terms = V.petition_terms(w, "Holland")
        assert terms["subject"] == "province" and terms["relation_step"] == 0
        assert "already at the 40 ceiling" in terms["grant_line"]
        res = V.grant_petition(w, "Holland", PLAYER, terms)
        assert res["success"] and res["relation_step"] == 0
        assert _rel(w, "Holland", PLAYER) == 40
        assert w.regions["Brunswick"].controller == "Holland"

    def test_the_bond_step_arithmetic(self):
        assert V._bond_step(0) == 20
        assert V._bond_step(20) == 20
        assert V._bond_step(30) == 10
        assert V._bond_step(40) == 0
        assert V._bond_step(60) == 0
        assert V._standing(40) == 2 and V._standing(-20) == -1 and V._standing(19) == 0

    def test_the_bond_holds_the_loyalty_through_the_real_tick(self):
        """IQ-7 review [43] (R11, Sept 18, 2026): the pin above proves the
        forecast (a second copy of step 6) and the relation, never the
        LOYALTY the bond is for. Below the 100 ceiling (70 — above the
        petition line, under the cap, so an over-delivery cannot clamp
        into a pass) the bonded client holds its position through ten real
        `advance_turn` ticks: the −2 drift is cancelled by the +2 bond, and
        each tick's applied delta equals the forecast."""
        w = _europe()
        w.diplomatic_points = 10
        for _ in range(2):
            terms = V.petition_terms(w, "Switzerland")
            assert V.grant_petition(w, "Switzerland", PLAYER, terms)["success"]
            w.vassals["Switzerland"]["remission_left"] = 0
        assert _rel(w, "Switzerland", PLAYER) == V.PETITION_BOND_CAP
        w.vassals["Switzerland"]["loyalty"] = 70
        assert V.forecast_vassal_loyalty(w, PLAYER, "Switzerland")["forecast"] == 0
        with _quiet():
            for _ in range(10):
                before = w.vassals["Switzerland"]["loyalty"]
                forecast = V.forecast_vassal_loyalty(w, PLAYER, "Switzerland")["forecast"]
                w.advance_turn()
                assert w.vassals["Switzerland"]["loyalty"] - before == forecast == 0
        assert w.vassals["Switzerland"]["loyalty"] == 70
        assert _rel(w, "Switzerland", PLAYER) == V.PETITION_BOND_CAP


# ═══════════════════════════════════════════════════════════════════════════
# T11 — re-validation at answer time
# ═══════════════════════════════════════════════════════════════════════════

class TestT11ReValidationAtAnswer:
    def _grant(self, client, dlg):
        return _respond(client, "grant the petition", dlg["dialogue_id"])

    def _assert_withdrawn(self, w, r, reason_fragment):
        assert r.get("success") is False, r
        assert "withdrawn" in str(r.get("message")), r.get("message")
        assert reason_fragment in str(r.get("message")), r.get("message")
        assert not _petitions(w)
        assert not _logged(w)
        # IQ-7 review [12]/[23] (R10, Sept 18, 2026): CONSCIOUS FLIP — a
        # withdrawal is neither accepted nor rejected; the rail used to
        # title it "Rejected" while the body said "withdrawn".
        assert r["proposal_result"]["outcome"] == "WITHDRAWN"
        assert r["proposal_result"]["proposal_type"] == "Client's Petition"
        assert "withdrawn" in r["proposal_result"]["message"]

    def test_a_released_vassal(self, http):
        w, client = http
        dlg = _deliver_seen(w, client, "Switzerland")
        with _quiet():
            assert V.release_vassal(w, "Switzerland")["success"]
        rel0, dp0 = _rel(w, "Switzerland", PLAYER), w.diplomatic_points
        r = self._grant(client, dlg)
        self._assert_withdrawn(w, r, "no longer a vassal")
        assert _rel(w, "Switzerland", PLAYER) == rel0 and w.diplomatic_points == dp0

    def test_b_a_vassal_transferred_to_prussia(self, http):
        w, client = http
        dlg = _deliver_seen(w, client, "Switzerland")
        with _quiet():
            V.transfer_vassal(w, "Switzerland", "Prussia")
        rel0, dp0 = _rel(w, "Switzerland", PLAYER), w.diplomatic_points
        r = self._grant(client, dlg)
        self._assert_withdrawn(w, r, "no longer answers to")
        assert w.vassals["Switzerland"]["loyalty"] == V.TRANSFER_LOYALTY_RESET
        assert _rel(w, "Switzerland", PLAYER) == rel0 and w.diplomatic_points == dp0
        assert _rel(w, "Switzerland", "Prussia") == 0

    def test_c_a_province_that_can_no_longer_be_ceded(self, http):
        w, client = http
        _stage_tyrol_for_koi(w)
        dlg = _deliver_seen(w, client, RAW_TAG)
        assert dlg["context"]["proposal"]["petition"]["region"] == "Tyrol"
        w.regions["Tyrol"].controller = "Austria"
        w.invalidate_active_nations_cache()
        loy0, rel0, dp0 = w.vassals[RAW_TAG]["loyalty"], _rel(w, RAW_TAG, PLAYER), w.diplomatic_points
        r = self._grant(client, dlg)
        self._assert_withdrawn(w, r, "can no longer be ceded")
        assert w.vassals[RAW_TAG]["loyalty"] == loy0 and _rel(w, RAW_TAG, PLAYER) == rel0
        assert w.diplomatic_points == dp0
        assert not w.vassals[RAW_TAG].get("granted_regions")

    def test_d_a_lord_who_can_no_longer_pay(self, http):
        """IQ-7 review R2 ([03]/[35]/[12], September 18, 2026) — CONSCIOUS
        FLIP of the contract's T11(d) ("set lord DP to 0 -> withdrawn, no
        refusal penalty"). DP is the player's own pool, reset every turn, so
        "spend it, then press Grant" was a free exit from the refusal price
        that Refuse and the lapse both charge. A lord who cannot pay has NOT
        answered: the Grant is refused WITHOUT consuming the petition (not
        popped, the rail notice kept, nothing charged, nothing logged), the
        response re-carries the question with Grant honestly disabled, and
        the lapse then charges the refusal like any other. Lever
        `THE_LORD_PAYS_TO_GRANT` False reproduces the withdrawal."""
        w, client = http
        dlg = _deliver_seen(w, client, "Switzerland")
        w.diplomatic_points = 0
        loy0, rel0 = w.vassals["Switzerland"]["loyalty"], _rel(w, "Switzerland", PLAYER)
        r = self._grant(client, dlg)
        assert r.get("success") is False, r
        assert "stands until the turn ends" in str(r.get("message")), r.get("message")
        assert "cannot spare the diplomatic point" in str(r.get("message"))
        assert _petitions(w) and _petitions(w)[0] is dlg          # not consumed
        assert "Petition from Switzerland" in _titles(w)          # the rail notice kept
        assert not _logged(w)
        assert r.get("proposal_result") is None                   # no verdict was reached
        assert r.get("diplomatic_dialogue") is not None           # the question re-carried
        popup = r.get("incoming_proposal")
        assert isinstance(popup, dict) and popup.get("is_petition") is True
        assert popup.get("grant_enabled") is False and popup.get("grant_reason")
        assert popup.get("dialogue_id") == dlg["dialogue_id"]
        assert w.diplomatic_points == 0
        assert w.vassals["Switzerland"]["loyalty"] == loy0
        assert _rel(w, "Switzerland", PLAYER) == rel0
        assert "remission_left" not in w.vassals["Switzerland"]
        # the typed road refuses the same way and leaves it pending
        r2 = _cmd(client, "grant the petition")
        assert r2.get("success") is False and "stands until the turn ends" in str(r2.get("message"))
        assert _petitions(w) and _petitions(w)[0] is dlg
        # ...and the lapse charges the refusal price, as it always did
        _end_turn(client)
        log = _logged(w, "unanswered")
        assert len(log) == 1 and log[0]["penalty"] is True
        assert w.vassals["Switzerland"]["loyalty"] < loy0
        assert _rel(w, "Switzerland", PLAYER) == rel0 - V.PETITION_RELATION_STEP

    def test_d_lever_down_a_lord_who_cannot_pay_withdraws(self, http, monkeypatch):
        """The False arm of `THE_LORD_PAYS_TO_GRANT` — the 7d10e20c
        withdrawal, byte-for-byte on this surface."""
        w, client = http
        monkeypatch.setattr(V, "THE_LORD_PAYS_TO_GRANT", False, raising=False)
        dlg = _deliver_seen(w, client, "Switzerland")
        w.diplomatic_points = 0
        loy0, rel0 = w.vassals["Switzerland"]["loyalty"], _rel(w, "Switzerland", PLAYER)
        r = self._grant(client, dlg)
        assert r.get("success") is False, r
        assert "withdrawn" in str(r.get("message")) and "cannot spare the diplomatic point" in str(r.get("message"))
        assert not _petitions(w)
        assert not _logged(w)
        assert w.vassals["Switzerland"]["loyalty"] == loy0
        assert _rel(w, "Switzerland", PLAYER) == rel0

    def test_a_moot_refusal_is_not_a_penalty(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        with _quiet():
            V.transfer_vassal(w, "Switzerland", "Prussia")
        rel0 = _rel(w, "Switzerland", PLAYER)
        r = _respond(client, "refuse the petition", dlg["dialogue_id"])
        assert r.get("success") is False and "moot" in str(r.get("message"))
        assert not _petitions(w)
        assert _rel(w, "Switzerland", PLAYER) == rel0
        assert w.vassals["Switzerland"]["loyalty"] == V.TRANSFER_LOYALTY_RESET
        assert not _logged(w)

    # ── IQ-7 review [41] (R11, Sept 18, 2026): release does not retire a
    # pending petition, so `release switzerland` then `end turn` reaches
    # `refuse_petition` with the ROW GONE — the one arm of its guard nothing
    # covered (removing it dereferenced None and the turn never advanced).

    def test_a_released_vassals_petition_is_refused_free_and_reported_withdrawn(self, http):
        w, client = http
        dlg = _deliver_seen(w, client, "Switzerland")
        with _quiet():
            assert V.release_vassal(w, "Switzerland")["success"]
        assert "Switzerland" not in w.vassals
        rel0 = _rel(w, "Switzerland", PLAYER)
        r = _respond(client, "refuse the petition", dlg["dialogue_id"])
        assert r.get("success") is False and "moot" in str(r.get("message"))
        assert r["proposal_result"]["outcome"] == "WITHDRAWN"
        assert not _petitions(w) and not _logged(w)
        assert _rel(w, "Switzerland", PLAYER) == rel0

    def test_a_released_vassals_petition_lapses_free_and_the_turn_advances(self, http):
        w, client = http
        _deliver(w, "Switzerland")
        with _quiet():
            assert V.release_vassal(w, "Switzerland")["success"]
        assert "Switzerland" not in w.vassals and _petitions(w)
        rel0 = _rel(w, "Switzerland", PLAYER)
        r = _end_turn(client)                              # advances, or raises with its reason
        assert not _logged(w) and not _petitions(w)
        assert _rel(w, "Switzerland", PLAYER) == rel0
        receipt = [e for e in r.get("events", []) if e.get("type") == "client_petition_answered"]
        assert receipt and receipt[0]["outcome"] == "withdrawn" and receipt[0]["penalty"] is False

    def test_sensitivity_the_gone_row_arm_is_what_keeps_the_turn_advancing(self, http, monkeypatch):
        """The [41] mutation, applied at the seam: a `refuse_petition` that
        reads the row before the guard (the Q-1 shape) makes `end turn` fail
        after a release — proving the pin above is load-bearing."""
        real = V.refuse_petition

        def mutated(world, vassal_name, lord, petition, how):
            world.vassals[vassal_name]["loyalty"]          # the guard removed: dereferences the gone row
            return real(world, vassal_name, lord, petition, how=how)

        monkeypatch.setattr(V, "refuse_petition", mutated)
        w, client = http
        _deliver(w, "Switzerland")
        with _quiet():
            assert V.release_vassal(w, "Switzerland")["success"]
        before = int(w.current_turn)
        try:
            _cmd(client, "end turn")
        except Exception:
            pass
        assert int(w.current_turn) == before


# ═══════════════════════════════════════════════════════════════════════════
# T12 — GR5: an AI lord answers in place
# ═══════════════════════════════════════════════════════════════════════════

def _holland_under_prussia(dp=3):
    w = _europe()
    with _quiet():
        V.transfer_vassal(w, "Holland", "Prussia")
    row = w.vassals["Holland"]
    row["loyalty"] = 80
    row["created_turn"] = -10
    w.nation_dp["Prussia"] = dp
    return w


class TestT12GR5TheAILord:
    def test_the_relief_is_granted_in_place_with_no_dialogue_or_notification(self):
        w = _holland_under_prussia()
        assert V.forecast_vassal_loyalty(w, "Prussia", "Holland")["forecast"] < 0
        notes0, pending0 = len(w.notifications.to_list()), len(_pending(w))
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert [(e["vassal"], e["lord"], e["subject"], e["outcome"]) for e in events] == [
            ("Holland", "Prussia", "relief", "granted")]
        assert events[0]["nation"] == "Prussia"
        assert len(w.notifications.to_list()) == notes0
        assert len(_pending(w)) == pending0 and not _petitions(w)
        row = w.vassals["Holland"]
        assert w.nation_dp["Prussia"] == 2
        assert row["loyalty"] == 80 + V.PETITION_RELIEF_LOYALTY
        assert row["remission_left"] == V.REMISSION_COLLECTIONS
        assert _rel(w, "Holland", "Prussia") == V.PETITION_RELATION_STEP
        assert row["petitioned_turn"] == w.current_turn
        assert V.vassal_tribute_owed(w, "Holland") == 0
        log = _logged(w, "granted")
        assert len(log) == 1 and log[0]["lord"] == "Prussia"

    def test_a_province_in_the_lords_own_active_design_is_refused_at_the_players_prices(self):
        w = _holland_under_prussia()
        w.regions["Brunswick"].controller = "Prussia"
        w.invalidate_active_nations_cache()
        deck = w.agendas["Prussia"][0]
        assert deck["id"] == "hanoverian_prize" and deck["regions"] == ["Hanover"]
        deck["regions"] = ["Hanover", "Brunswick"]           # Hanover unmet -> still active
        w.invalidate_active_nations_cache()
        view = AG.get_active_agenda("Prussia", w)
        assert view is not None and view.type == "acquire_regions"
        assert "Brunswick" in view.regions
        assert V.petition_terms(w, "Holland")["region"] == "Brunswick"
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert [(e["subject"], e["region"], e["outcome"]) for e in events] == [
            ("province", "Brunswick", "refused")]
        row = w.vassals["Holland"]
        assert w.nation_dp["Prussia"] == 3                    # nothing charged
        assert row["loyalty"] == 80 - V.PETITION_REFUSAL_LOYALTY
        assert _rel(w, "Holland", "Prussia") == -V.PETITION_RELATION_STEP
        assert w.regions["Brunswick"].controller == "Prussia"
        assert not row.get("granted_regions")

    def test_outside_its_design_the_ai_lord_cedes_the_province(self):
        w = _holland_under_prussia()
        w.regions["Brunswick"].controller = "Prussia"
        w.invalidate_active_nations_cache()
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert [(e["subject"], e["region"], e["outcome"]) for e in events] == [
            ("province", "Brunswick", "granted")]
        assert w.regions["Brunswick"].controller == "Holland"
        assert w.vassals["Holland"]["granted_regions"] == ["Brunswick"]
        assert w.nation_dp["Prussia"] == 3 - V.GRANT_DP_COST
        assert _rel(w, "Holland", "Prussia") == 20

    def test_a_penniless_ai_lord_is_not_asked(self):
        w = _holland_under_prussia(dp=0)
        with _quiet():
            assert V.process_vassal_petitions(w) == []
        assert "petitioned_turn" not in w.vassals["Holland"]

    def test_the_prices_are_the_players(self):
        """The same numbers a player grant/refusal moves — the single source
        keys on the row's lord, never on who is answering."""
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 80
        player = V.grant_petition(w, "Switzerland", PLAYER, V.petition_terms(w, "Switzerland"))
        ai_w = _holland_under_prussia()
        with _quiet():
            ai = V.process_vassal_petitions(ai_w)[0]
        ai_row = ai_w.vassals["Holland"]
        assert (player["loyalty_after"] - player["loyalty_before"],
                player["relation_after"] - player["relation_before"],
                player["dp_charged"], player["remission_left"]) == (
            ai_row["loyalty"] - 80, _rel(ai_w, "Holland", "Prussia"), 1, ai_row["remission_left"])
        assert "granted" == ai["outcome"]


# ═══════════════════════════════════════════════════════════════════════════
# T13 — typed-command safety
# ═══════════════════════════════════════════════════════════════════════════

class TestT13TypedCommandSafety:
    def test_grant_autonomy_runs_the_autonomy_verb_and_leaves_the_petition(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        r = _cmd(client, "grant Switzerland autonomy")
        assert w.vassals["Switzerland"]["autonomy"] == V.AUTONOMY_AUTONOMOUS, r.get("message")
        assert _petitions(w) and _petitions(w)[0] is dlg
        assert not _logged(w)

    def test_grant_ney_a_rente_leaves_the_petition(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        _cmd(client, "grant Ney a rente")
        assert _petitions(w) and _petitions(w)[0] is dlg
        assert not _logged(w)

    def test_invest_leaves_the_petition(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        w.vassals["Switzerland"]["loyalty"] = 80
        r = _cmd(client, "invest in Switzerland")
        assert w.vassals["Switzerland"]["loyalty"] == 90, r.get("message")
        assert _petitions(w) and _petitions(w)[0] is dlg
        assert not _logged(w)

    def test_typed_accept_answers_the_petition(self, http):
        w, client = http
        _deliver(w, "Switzerland")
        w.vassals["Switzerland"]["loyalty"] = 80
        _cmd(client, "accept")
        assert len(_logged(w, "granted")) == 1
        assert not _petitions(w)
        assert w.vassals["Switzerland"]["remission_left"] == 8

    def test_typed_do_not_accept_does_not_grant(self, http):
        w, client = http
        dlg = _deliver(w, "Switzerland")
        loy0, rel0, dp0 = w.vassals["Switzerland"]["loyalty"], _rel(w, "Switzerland", PLAYER), w.diplomatic_points
        _cmd(client, "do not accept")
        assert not _logged(w)
        assert _petitions(w) and _petitions(w)[0] is dlg
        assert (w.vassals["Switzerland"]["loyalty"], _rel(w, "Switzerland", PLAYER),
                w.diplomatic_points) == (loy0, rel0, dp0)
        assert "remission_left" not in w.vassals["Switzerland"]

    def test_the_full_label_typed_grants(self, http):
        w, client = http
        _deliver(w, "Switzerland")
        w.vassals["Switzerland"]["loyalty"] = 80
        _cmd(client, "Grant the petition")
        assert len(_logged(w, "granted")) == 1

    def test_the_labels_are_multi_word_and_no_prefix_of_a_verb_phrase(self):
        w = _europe()
        dlg = _deliver(w, "Switzerland")
        for option in dlg["options"]:
            words = option["label"].split()
            assert len(words) >= 3, option["label"]
            assert option["label"].lower() not in ("grant", "refuse", "accept", "reject")


# ═══════════════════════════════════════════════════════════════════════════
# T14 — payload and R7
# ═══════════════════════════════════════════════════════════════════════════

class TestT14PayloadAndR7:
    def _koi_petition(self):
        w = _europe()
        _set_rel(w, RAW_TAG, PLAYER, -60)                    # forecast +2-3 -> relief
        terms = V.petition_terms(w, RAW_TAG)
        assert terms is not None and terms["subject"] == "relief"
        return w, _deliver(w, RAW_TAG), terms

    def test_no_raw_tag_reaches_the_popup_or_the_dialogue(self):
        w, dlg, terms = self._koi_petition()
        payload = dlg["popup_payload"]
        prose = json.dumps([dlg["talleyrand_text"], [o["description"] for o in dlg["options"]],
                            payload["clauses"], payload["talleyrand_assessment"],
                            payload["diplomat_name"], _titles(w), terms["grant_line"],
                            terms["refuse_line"], terms["vassal_display"]])
        assert "Kingdom of Italy" in prose
        assert RAW_TAG not in prose
        # PIN FLIPPED, IQ-7 review pass 3 (Sept 19, 2026, R3-8): the rail
        # TITLE is a sentence fragment, so the court takes its article as the
        # body always has — it was "Petition from Kingdom of Italy".
        assert "Petition from the Kingdom of Italy" in _titles(w)
        # the authored envoy speaks for his court...
        assert payload["diplomat_name"] == w.diplomats[RAW_TAG].name == "Marescalchi"
        # ...and a court WITHOUT a diplomat record is named, never tagged
        # (the generic arm would have said "the KingdomOfItaly ambassador")
        w.diplomats.pop(RAW_TAG)
        dlg2 = _deliver(w, RAW_TAG)
        payload2 = dlg2["popup_payload"]
        # IQ-7 review R10 (Sept 18, 2026): the court carries its article.
        assert payload2["diplomat_name"] == "the envoy of the Kingdom of Italy"
        # `from_nation` is the machine key the .gd humanizes at render; every
        # PROSE key of the payload must be clean
        for key in ("diplomat_name", "clauses", "talleyrand_assessment",
                    "proposal_type_display", "acceptance_hint", "rejection_hint",
                    "diplomat_line"):
            assert RAW_TAG not in json.dumps(payload2.get(key)), key
        assert "the envoy of the Kingdom of Italy brings a petition" in dlg2["talleyrand_text"]
        assert RAW_TAG not in dlg2["talleyrand_text"]

    def test_the_ledger_card_speaks_no_raw_tag(self):
        w, dlg, terms = self._koi_petition()
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == RAW_TAG)
        # `name` is the machine key the .gd humanizes at render (the tab has
        # always carried it); every PROSE value must be clean.
        for key in ("bond", "standing", "recovery_hint", "autonomy_name", "capital"):
            assert RAW_TAG not in str(card.get(key, "")), key
        # IQ-7 review pass 2 P4-2 (Sept 18, 2026): CONSCIOUS FLIP — this
        # fixture DELIVERS the Kingdom's petition, so the ask is ON THE DESK
        # and the card says so: the gate copy below ("5 turns until it may
        # ask") is true of the NEXT ask and read, beside an unanswered one in
        # Envoys, as though none had come. `next_petition_in` keeps the
        # gate's own count.
        assert V.petition_on_the_desk(w, RAW_TAG, PLAYER) is True
        assert card["standing"] == "petition on the desk"
        assert card["standing_key"] == "pending"
        assert card["next_petition_in"] == 5 - (w.current_turn - 1)   # the grace, turn 1
        # ...and only for the client that asked: Switzerland's card is the gate's
        swiss = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"]
                     if r["name"] == "Switzerland")
        assert swiss["standing_key"] == "grace"
        # The ask answered (the dialogue gone), the gate copy returns.
        assert w.dialogue_manager.remove_matching(V.is_client_petition) == 1
        assert V.petition_on_the_desk(w, RAW_TAG, PLAYER) is False
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == RAW_TAG)
        # IQ-7 review R7 ([08]/[20], Sept 18, 2026): CONSCIOUS FLIP — the card
        # reads "may petition" ONLY when every gate passes at the next advance;
        # at turn 1 the grace (b) blocks, so the standing IS the blocking
        # reason and its countdown; and the relation term is the BOND, never
        # a second "standing" on the same card.
        assert card["standing"] == "5 turns until it may ask"
        assert card["standing_key"] == "grace"
        assert card["relation"] == -60 and card["relation_modifier"] == -3
        assert card["bond"] == "-3/turn — bond spent (-60)"
        assert card["remission_left"] == 0
        assert card["next_petition_in"] == 5 - (w.current_turn - 1)   # the grace, turn 1

    def test_the_cadence_arm_and_the_positive_bond_copy(self):
        """IQ-7 review [42] (R11, Sept 18, 2026): the pins above read only
        the grace arm of `next_petition_in` and the NEGATIVE bond copy."""
        w = _europe()
        w.current_turn = 20
        w.vassals["Switzerland"]["created_turn"] = 1
        w.vassals["Switzerland"]["petitioned_turn"] = 20            # stamped this turn
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == "Switzerland")
        assert card["next_petition_in"] == V.PETITION_INTERVAL_TURNS
        assert card["standing"] == f"{V.PETITION_INTERVAL_TURNS} turns until it may ask"
        assert card["standing_key"] == "cadence"
        w.vassals["Switzerland"]["petitioned_turn"] = 20 - V.PETITION_INTERVAL_TURNS + 2
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == "Switzerland")
        assert card["next_petition_in"] == 2 and card["standing"] == "2 turns until it may ask"
        # one turn out the NEXT advance clears it: eligible, countdown 1
        w.vassals["Switzerland"]["petitioned_turn"] = 20 - V.PETITION_INTERVAL_TURNS + 1
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == "Switzerland")
        assert card["next_petition_in"] == 1 and card["standing"] == "may petition"
        _set_rel(w, "Switzerland", PLAYER, 20)
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == "Switzerland")
        assert card["bond"] == "+1/turn — a bond worth one honoured petition (bond 20)"
        _set_rel(w, "Switzerland", PLAYER, 40)
        card = next(r for r in build_diplomatic_ledger(w)["vassals"]["rows"] if r["name"] == "Switzerland")
        assert card["bond"] == "+2/turn — a bond worth two honoured petitions (bond 40)"
        assert card["relation"] == 40 and card["relation_modifier"] == 2

    def test_the_clauses_state_every_price_and_equal_the_single_source(self):
        w, dlg, terms = self._koi_petition()
        payload = dlg["popup_payload"]
        assert payload["is_petition"] is True
        assert payload["clauses"] == [terms["grant_line"], terms["refuse_line"], terms["lapse_line"]]
        assert payload["clauses"] == client_petition_clauses(dlg["context"]["proposal"])
        assert payload["acceptance_hint"] == "" and payload["rejection_hint"] == ""
        assert payload["diplomat_line"] == ""
        grant = terms["grant_line"]
        assert f"loyalty +{terms['loyalty_gain']}" in grant
        assert f"{terms['collections']} collections" in grant
        assert f"({terms['price']}g forgone)" in grant
        assert f"for {terms['dp_cost']} DP" in grant
        assert f"{terms['tribute_per_turn']}g a turn" in grant
        assert f"{terms['standing_after_grant']:+d} a turn" in grant
        refuse = terms["refuse_line"]
        # IQ-7 review R6/R7 ([05]/[19]/[20], Sept 18, 2026): CONSCIOUS FLIP —
        # the refuse line prices the APPLIED loss and names the relation term
        # the client's bond, never "standing" (the standing to petition) and
        # never "drift" (the −2 autonomy term).
        assert (f"loses {terms['refusal_loyalty_applied']} loyalty and its bond with us "
                f"falls {terms['relation_refusal_step_applied']}") in refuse
        assert terms["refusal_loyalty_applied"] == terms["refusal_loyalty"] == 10
        assert terms["relation_refusal_step_applied"] == terms["relation_refusal_step"] == 20
        assert "drift" not in refuse and "standing" not in refuse
        assert f"{terms['standing_after_refusal']:+d} a turn" in refuse
        assert "nothing is charged" in refuse
        assert terms["lapse_line"].endswith("a lapse is a refusal.")
        assert terms["dp_cost"] == V.PETITION_DP_COST == 1
        assert terms["relation_refusal_step"] == V.PETITION_RELATION_STEP
        assert terms["price"] == terms["tribute_per_turn"] * terms["collections"]
        # the option descriptions ARE the lines
        assert [o["description"] for o in dlg["options"]] == [grant, refuse]
        assert terms_are_a_client_petition(dlg["context"]["proposal"])

    def test_the_payload_builder_is_the_one_the_transport_uses(self):
        w, dlg, terms = self._koi_petition()
        rebuilt = build_pending_envoy_popup_from_terms(
            w, nation=RAW_TAG, terms=dlg["context"]["proposal"], assessment="",
            decision_reason="client_petition")
        assert rebuilt["is_petition"] is True
        assert rebuilt["clauses"] == dlg["popup_payload"]["clauses"]
        assert rebuilt["proposal_type_display"] == "Client's Petition"

    def test_r7_the_rail_notices_name_the_court(self):
        """The fix in passing: the rebellion / defection / broke-free rail
        notices printed the RAW tag beside a dispatch line that said "Kingdom
        of Italy". Both the templates and the notification producers."""
        for event_type, variables in (
                ("diplomatic_vassal_rebellion", {"nation": RAW_TAG, "lord": PLAYER}),
                ("diplomatic_vassal_rebellion_imminent", {"nation": RAW_TAG}),
                ("diplomatic_vassal_broke_free_peace", {"nation": RAW_TAG, "lord": PLAYER}),
                ("diplomatic_vassal_broke_free_armistice", {"nation": RAW_TAG, "lord": PLAYER}),
                ("diplomatic_vassal_defected", {"vassal": RAW_TAG, "lord": PLAYER,
                                                "briber": "Switzerland", "nation": PLAYER})):
            text = _format_dispatch_event_text(event_type, variables)
            assert "Kingdom of Italy" in text, (event_type, text)
            assert RAW_TAG not in text, (event_type, text)
        assert _format_dispatch_event_text(
            "diplomatic_vassal_rebellion", {"nation": RAW_TAG, "lord": PLAYER}) == (
            "Sire — the Kingdom of Italy has rebelled against France. It is war.")
        assert _format_dispatch_event_text(
            "diplomatic_vassal_defected", {"vassal": RAW_TAG, "lord": PLAYER,
                                           "briber": "Switzerland", "nation": PLAYER}) == (
            "THE DEFECTION: Switzerland's gold turns the Kingdom of Italy against France.")

    def _no_raw_tag_on_the_rail(self, w):
        for n in w.notifications.to_list():
            assert RAW_TAG not in str(n.get("title")), n
            assert RAW_TAG not in str(n.get("message")), n

    def test_r7_the_rebellion_producers_name_the_court(self):
        # On the boot board the Kingdom of Italy is a co-belligerent in
        # France's war, so its break takes the graceful exit (FA-2's F8b
        # branch): the "breaks free" notice.
        w = _europe()
        w.vassals[RAW_TAG]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(w)
        titles = _titles(w)
        assert "Kingdom of Italy breaks free" in titles, titles
        self._no_raw_tag_on_the_rail(w)
        # Switzerland shares no war, so its break is the WAR exit — the
        # "REBELLED!" notice, the same producer line the Kingdom of Italy
        # would take on a board without the side-conflict.
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 0
        with _quiet():
            V.check_vassal_rebellion(w)
        assert "Switzerland REBELLED!" in _titles(w), _titles(w)
        assert w.get_diplomatic_state("Switzerland", PLAYER) == "WAR"
        # the imminent-rebellion notice (the Kingdom of Italy RISES +2 a tick
        # at boot — garrisoned and sharing a war — so it starts at 5, not 12)
        w = _europe()
        w.vassals[RAW_TAG]["loyalty"] = 5
        with _quiet():
            V.process_vassal_loyalty(w)
        assert w.vassals[RAW_TAG]["loyalty"] <= 10
        assert "Kingdom of Italy Critical!" in _titles(w), _titles(w)
        self._no_raw_tag_on_the_rail(w)

    def test_r7_the_defection_producer_names_the_court(self, monkeypatch):
        """VS-6 with the roll forced: a Switzerland at WAR with France buys
        the Kingdom of Italy free — the CRITICAL notice and its body name the
        court (the re-baseline digests read "turns KingdomOfItaly against
        France" on the rail beside a dispatch line that said it right)."""
        w = _europe()
        _set_state(w, "Switzerland", PLAYER, "WAR")
        w.nation_gold["Switzerland"] = V.BRIBE_FREE_COST
        w.vassals[RAW_TAG]["loyalty"] = 30
        monkeypatch.setattr(V.random, "random", lambda: 0.0)
        with _quiet():
            events = V.attempt_vassal_bribe(w, "Switzerland")
        assert any(e.get("type") == "vassal_defected" for e in events), events
        titles = _titles(w)
        assert "Kingdom of Italy DEFECTS!" in titles, titles
        body = next(n for n in w.notifications.to_list()
                    if n.get("title") == "Kingdom of Italy DEFECTS!")["message"]
        assert "Kingdom of Italy" in body
        self._no_raw_tag_on_the_rail(w)
        assert RAW_TAG not in body

    def test_the_display_name_row_exists(self):
        from backend.display_names import PROPOSAL_TYPE_DISPLAY, proposal_display_name
        assert PROPOSAL_TYPE_DISPLAY[V.CLIENT_PETITION_TYPE] == "Client's Petition"
        assert proposal_display_name(V.CLIENT_PETITION_TYPE) == "Client's Petition"
        assert V.CLIENT_PETITION_TYPE == "client_petition"     # never the Jealousy channel's word


# ═══════════════════════════════════════════════════════════════════════════
# T15 / T16 / T17 — the riders
# ═══════════════════════════════════════════════════════════════════════════

class TestT15R1TheWaveringLineTellsTheTruth:
    def test_the_honest_line_without_regiments(self):
        w = _europe()
        # IQ-7 review [22] (Sept 18, 2026): CONSCIOUS FLIP — the crossing names
        # the COST only ("only coin, a garrison or a province" was false:
        # autonomy mends it, +10) and leaves the remedy to the event's own
        # grip-aware recovery hint; with no hint on the event the line
        # appends that hint itself, so a cost is never told without a lever.
        line = V.tier_crossing_line(RAW_TAG, 61, 59, world=w, lord=PLAYER)
        assert line == ("Kingdom of Italy is no longer a willing ally, Sire — it has lost "
                        "the standing to petition you until its loyalty is mended.")
        assert "regiments" not in line and RAW_TAG not in line
        assert "only coin" not in line
        no_hint = V.tier_crossing_line(RAW_TAG, 61, 59, world=w, lord=PLAYER,
                                       remedy_present=False)
        assert no_hint.startswith(line)
        assert no_hint.endswith(V.recovery_hint_for_grip(V.get_imperial_grip(w, PLAYER)))

    def test_the_regiments_clause_when_the_lord_fields_the_vassals_marshal(self):
        w = _europe()
        marshal = next(m for m in w.marshals.values() if m.nation == PLAYER)
        marshal.original_nation = RAW_TAG
        assert V.lord_fields_the_vassals_regiments(w, PLAYER, RAW_TAG)
        line = V.tier_crossing_line(RAW_TAG, 61, 59, world=w, lord=PLAYER)
        assert line.startswith("Kingdom of Italy is no longer a willing ally")
        assert line.endswith(" Its own regiments will hold back from our musters and our "
                             "reinforcements until its loyalty is mended.")
        # a marshal of those colours serving ANOTHER lord does not count
        marshal.nation = "Prussia"
        assert not V.lord_fields_the_vassals_regiments(w, PLAYER, RAW_TAG)

    def test_lever_down_gives_the_old_sentence(self, monkeypatch):
        w = _europe()
        monkeypatch.setattr(V, "THE_WAVERING_LINE_IS_HONEST", False)
        line = V.tier_crossing_line(RAW_TAG, 61, 59, world=w, lord=PLAYER)
        assert "regiments will hold back from our musters" in line
        assert "standing to petition" not in line

    def test_the_two_arg_call_keeps_the_old_sentence_and_disaffected_is_unchanged(self):
        assert "musters" in V.tier_crossing_line("Bavaria", 60, 58)
        w = _europe()
        assert "call to arms" in V.tier_crossing_line("Switzerland", 35, 33, world=w, lord=PLAYER)

    def test_the_producer_passes_the_world(self):
        """`process_vassal_loyalty`'s crossing beat is the honest line — the
        call site hands the world (and lord) through."""
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 61
        with _quiet():
            events = V.process_vassal_loyalty(w)
        beat = next(e for e in events if e.get("type") == "vassal_loyalty"
                    and e.get("vassal") == "Switzerland")
        assert w.vassals["Switzerland"]["loyalty"] == 59
        assert "standing to petition" in beat.get("tier_crossing", "")
        assert "regiments" not in beat.get("tier_crossing", "")
        assert "standing to petition" in beat.get("message", "")


class TestT16R2CourtingSparesTheLordsAllies:
    def _board(self):
        w = _europe()
        _set_state(w, "Spain", PLAYER, "ALLIANCE")
        w.vassals["Switzerland"]["loyalty"] = 45
        w.nation_dp["Spain"] = 5
        w.nation_dp["Britain"] = 5
        return w

    def test_the_ally_courts_nothing_and_spends_nothing(self):
        w = self._board()
        assert V.courtier_is_the_lords_ally(w, "Spain", w.vassals["Switzerland"])
        events = V.attempt_vassal_courting(w, "Spain")
        assert events == []
        assert w.nation_dp["Spain"] == 5
        assert w.vassals["Switzerland"]["loyalty"] == 45
        assert "court|Spain|Switzerland" not in w.ai_proposal_cooldowns
        assert "courted_turn" not in w.vassals["Switzerland"]
        assert not any("Spain" in str(t) for t in _titles(w))

    def test_a_non_allied_court_still_courts(self):
        w = self._board()
        assert not V.courtier_is_the_lords_ally(w, "Britain", w.vassals["Switzerland"])
        events = V.attempt_vassal_courting(w, "Britain")
        assert events and events[0]["type"] == "vassal_courting"
        assert w.vassals["Switzerland"]["loyalty"] < 45
        assert w.nation_dp["Britain"] == 3

    def test_lever_down_the_ally_courts(self, monkeypatch):
        w = self._board()
        monkeypatch.setattr(V, "COURTING_SPARES_THE_LORDS_ALLIES", False)
        events = V.attempt_vassal_courting(w, "Spain")
        assert events and events[0]["vassal"] == "Switzerland"
        assert w.nation_dp["Spain"] == 3

    def test_a_defensive_ally_is_spared_too_and_a_neutral_is_not(self):
        w = self._board()
        _set_state(w, "Spain", PLAYER, "DEFENSIVE_ALLIANCE")
        assert V.courtier_is_the_lords_ally(w, "Spain", w.vassals["Switzerland"])
        _set_state(w, "Spain", PLAYER, "NON_AGGRESSION")
        assert not V.courtier_is_the_lords_ally(w, "Spain", w.vassals["Switzerland"])
        assert not V.courtier_is_the_lords_ally(w, PLAYER, w.vassals["Switzerland"])

    def test_a_design_stake_holder_that_is_the_lords_ally_is_not_yielded_to(self, monkeypatch):
        """The rival loop in `courtier_yields_to_a_design_stake` applies the
        same rule: an allied stakeholder will stand aside itself, so a
        stakeless courtier never yields the slot to it."""
        w = self._board()
        w.nation_dp["Austria"] = 5
        _set_state(w, "Austria", PLAYER, "ALLIANCE")
        monkeypatch.setattr(AG, "vassal_holds_agenda_target",
                            lambda courter, vassal, world: courter == "Austria")
        state = w.vassals["Switzerland"]
        assert not V.courtier_yields_to_a_design_stake(w, "Britain", "Switzerland", state)
        _set_state(w, "Austria", PLAYER, "PEACE")
        assert V.courtier_yields_to_a_design_stake(w, "Britain", "Switzerland", state)


class TestT17R3TheGarrisonOptionSaysWhatItDoes:
    def test_the_modal_copy_names_no_corps_moves_and_the_capital(self):
        w = _europe()
        w.vassals["Switzerland"]["loyalty"] = 12
        with _quiet():
            V.process_vassal_loyalty(w)
        dlg = next(d for d in _pending(w) if d.get("type") == "vassal_rebellion_imminent")
        assert [o["label"] for o in dlg["options"]] == ["Invest", "Garrison", "Accept Risk"]
        assert [o["action"] for o in dlg["options"]] == [
            "invest_vassal_rebellion", "garrison_vassal_rebellion", "accept_vassal_rebellion"]
        garrison = dlg["options"][1]["description"]
        assert garrison == ("2 AP → Loyalty +10 now. No corps moves: a corps standing in "
                            "Bern adds +2 every turn.")
        popup = w.vassal_rebellion_imminent_popups[-1]
        assert popup["garrison_effect"] == garrison
        assert popup["garrison_ap_cost"] == 2 and popup["invest_cost_dp"] == 1
        assert popup["dialogue_id"] == dlg["dialogue_id"]
        assert f"+{V.GARRISON_LOYALTY_BONUS} every turn" in garrison


# ═══════════════════════════════════════════════════════════════════════════
# T18 / T19 — persistence and the Q6 pin
# ═══════════════════════════════════════════════════════════════════════════

class TestT18SaveLoad:
    def test_a_remission_and_a_pending_petition_survive_the_save(self, tmp_path, monkeypatch):
        w = _europe()
        w.vassals["Switzerland"]["remission_left"] = 5
        w.vassals["Switzerland"]["petitioned_turn"] = 3
        _stage_tyrol_for_koi(w)
        dlg = _deliver(w, RAW_TAG)
        path = tmp_path / "iq7_round_trip.json"
        with _quiet():
            saved = SM.save_game(w, "iq7", filepath=path)
            assert saved["success"], saved
            loaded = SM.load_game(path)
        assert loaded["success"], loaded
        w2 = loaded["world"]
        assert w2.vassals["Switzerland"]["remission_left"] == 5
        assert w2.vassals["Switzerland"]["petitioned_turn"] == 3
        pets = _petitions(w2)
        assert len(pets) == 1 and pets[0]["dialogue_id"] == dlg["dialogue_id"]
        # the remission continues, and the petition is answerable, with the
        # issuing lever DOWN — both keyed on the data
        monkeypatch.setattr(V, "THE_CLIENT_PETITIONS", False)
        assert V.vassal_tribute_owed(w2, "Switzerland") == 0
        with _quiet():
            V.process_vassal_tribute(w2)
        assert w2.vassals["Switzerland"]["remission_left"] == 4
        monkeypatch.setattr(M, "world", w2)
        monkeypatch.setattr(M, "parser", _PARSER)
        monkeypatch.setitem(M.game_state, "world", w2)
        client = TestClient(M.app)
        r = _respond(client, "grant the petition", pets[0]["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert w2.regions["Tyrol"].controller == RAW_TAG
        assert w2.vassals[RAW_TAG]["granted_regions"] == ["Tyrol"]

    def test_the_pure_round_trip_and_an_old_save_without_the_keys(self):
        w = _europe()
        w.vassals["Switzerland"]["remission_left"] = 5
        w.vassals["Switzerland"]["petitioned_turn"] = 3
        with _quiet():
            data = w.to_dict()
            w2 = WorldState.from_dict(data)
        assert w2.vassals["Switzerland"]["remission_left"] == 5
        assert w2.vassals["Switzerland"]["petitioned_turn"] == 3
        for row in data["vassals"].values():
            row.pop("remission_left", None)
            row.pop("petitioned_turn", None)
        with _quiet():
            w3 = WorldState.from_dict(data)
        row = w3.vassals["Switzerland"]
        assert "remission_left" not in row and "petitioned_turn" not in row
        assert V.vassal_tribute_owed(w3, "Switzerland") == _pre_slice_tribute(w3, "Switzerland") > 0
        keys = V.petition_standing_keys(w3, "Switzerland")
        assert keys["remission_left"] == 0
        assert keys["next_petition_in"] == V.PETITION_GRACE_TURNS - (w3.current_turn - 1)
        _make_eligible(w3, "Switzerland")
        with _quiet():
            V.process_vassal_petitions(w3)
        assert len(_petitions(w3)) == 1


class TestT19TheQ6Pin:
    def test_the_loyalty_pass_stamps_no_key_on_the_shipped_board(self):
        """Memo Q6 (`test_vassal_authority_coupling.py::test_no_new_serialized_
        vassal_fields`, unmodified): the loyalty pass writes neither new key.
        Only the PRODUCER stamps `petitioned_turn`; only a GRANT writes
        `remission_left`."""
        w = _europe()
        _make_eligible(w, "Switzerland")
        keys = {name: set(row.keys()) for name, row in w.vassals.items()}
        with _quiet():
            V.process_vassal_loyalty(w)
        for name, row in w.vassals.items():
            assert set(row.keys()) == keys[name], name
        with _quiet():
            V.process_vassal_petitions(w)
        assert set(w.vassals["Switzerland"].keys()) == keys["Switzerland"] | {"petitioned_turn"}


# ═══════════════════════════════════════════════════════════════════════════
# T20 — the driver (R4 and the `--client-petition` dial)
# ═══════════════════════════════════════════════════════════════════════════

def _load_driver(name):
    spec = importlib.util.spec_from_file_location(name, str(DRIVER))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pdriver = _load_driver("playtest_driver_iq7")
_DRIVE_SANDBOX: dict = {}       # run name -> where that driven run autosaved


def _drive(name, turns, *, diplomacy="accept", client_petition="", levers=()):
    """`tools/playtest_driver.py`'s own `run()` in this process (the IQ-6
    idiom: a subprocess would discard a monkeypatched lever). Everything the
    driver touches is restored."""
    keys = ("LLM_MODE", "SOVEREIGN_SEED", "INK_IRON_SAVE_DIR", "DEBUG_MODE",
            "SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START", "SOVEREIGN_MAP")
    prior_env = {k: os.environ.get(k) for k in keys}
    os.environ["LLM_MODE"] = "mock"
    os.environ["SOVEREIGN_SEED"] = "historical"
    prior_main = (M.world, M.game_state.get("world"), M.parser)
    drv = _load_driver(f"playtest_driver_iq7_{name}")
    prior_levers = [(module, attr, getattr(module, attr)) for module, attr, _ in levers]
    tmp = tempfile.mkdtemp(prefix=f"iq7_{name}_")
    # IQ-7 review, SWEEP 2 (measured): `INK_IRON_SAVE_DIR` below is read ONCE, at
    # `backend.save_manager` import, and the MODULE-scoped `driven_grant` is built
    # BEFORE conftest's function-scoped `_isolate_save_dir` — so the driver's boot and
    # its seven end turns autosaved into the developer's own `saves/autosave.json`
    # (its mtime moved on every run of this file). The module attribute is what
    # `autosave` reads; it is restored below.
    import backend.save_manager as _save_manager
    prior_save_dir = _save_manager.SAVE_DIR
    _DRIVE_SANDBOX[name] = Path(tmp) / "saves"
    _save_manager.SAVE_DIR = _DRIVE_SANDBOX[name]
    try:
        for module, attr, value in levers:
            setattr(module, attr, value)
        if any(module is pdriver for module, _, _ in levers):
            for module, attr, value in levers:
                if module is pdriver:
                    setattr(drv, attr, value)
        os.environ["INK_IRON_SAVE_DIR"] = os.path.join(tmp, "saves")
        with _quiet():
            M.parser = CommandParser()
        BR._OBSERVATION_COUNTS.clear()
        ns = argparse.Namespace(
            name=name, turns=turns, seed="historical", llm="mock", scenario="",
            script="", from_save="", http="", out=os.path.join(tmp, "out"),
            save_at="", objection="", diplomacy=diplomacy, redemption="",
            petition="", declare_war="", paradox="", rebellion="", sabotage="",
            reward="", last_stand="", contact="", missions="",
            client_petition=client_petition, reload_every=0, cheats=False,
            strict=False, verbose=False, fresh=True, archive=False)
        with _quiet():
            rc = drv.run(ns)
        assert rc == 0, rc
        world = M.world
    finally:
        _save_manager.SAVE_DIR = prior_save_dir
        for module, attr, value in prior_levers:
            setattr(module, attr, value)
        M.world, M.parser = prior_main[0], prior_main[2]
        M.game_state["world"] = prior_main[1]
        for key, value in prior_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    out_dir = Path(tmp) / "out" / name
    md = (out_dir / "digest.md").read_text(encoding="utf-8")
    records = [json.loads(line) for line in
               (out_dir / "digest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    return md, records, meta, world


POPUP_LINE = re.compile(r"POPUP diplomatic_dialogue: (\w[\w ]*?), client_petition #\d+ → (grant|refuse) the petition")


@pytest.fixture(scope="module")
def driven_grant():
    return _drive("grant", 7)


def test_the_driven_run_autosaves_into_its_own_sandbox(driven_grant):
    """IQ-7 review, SWEEP 2: the suite must never write the developer's `saves/`
    (conftest's own rule) — the module-scoped run autosaves into its sandbox."""
    import backend.save_manager as save_manager
    assert (Path(_DRIVE_SANDBOX["grant"]) / save_manager.AUTOSAVE_FILENAME).is_file()


class TestT20TheDriver:
    def test_the_dial_mirrors_the_diplomacy_policy_and_the_flag_wins(self):
        pol = pdriver.resolve_policy(argparse.Namespace(), {})
        assert "client_petition" not in pol and "client_petition" not in pdriver.POLICY_DEFAULTS
        assert pdriver.client_petition_mode(pol) == "refuse"           # default diplomacy: decline
        for mode in pdriver.ACCEPTING_DIPLOMACY_MODES:
            assert pdriver.client_petition_mode(dict(pol, diplomacy=mode)) == "grant"
        assert pdriver.client_petition_mode(dict(pol, diplomacy="decline")) == "refuse"
        assert pdriver.client_petition_mode(dict(pol, diplomacy="accept", client_petition="refuse")) == "refuse"
        assert pdriver.client_petition_mode(dict(pol, diplomacy="decline", client_petition="grant")) == "grant"
        assert pdriver.resolve_policy(argparse.Namespace(client_petition="refuse"), {})["client_petition"] == "refuse"
        assert pdriver.resolve_policy(argparse.Namespace(client_petition="refuse"),
                                      {"policy": {"client_petition": "grant"}})["client_petition"] == "refuse"
        assert "client_petition" in pdriver.POLICY_FLAG_KEYS
        assert pdriver.CLIENT_PETITION_LABELS == {"grant": "grant the petition",
                                                  "refuse": "refuse the petition"}

    def test_the_answerer_reads_the_producers_predicate_not_the_label_text(self):
        dlg = {"type": "incoming_proposal", "target_nation": "Switzerland", "dialogue_id": 7,
               "options": [{"label": "Grant the petition", "action": "accept_ai_proposal", "description": "g"},
                           {"label": "Refuse the petition", "action": "reject_ai_proposal", "description": "r"}],
               "context": {"proposal_type": V.CLIENT_PETITION_TYPE,
                           "proposal": {"type": V.CLIENT_PETITION_TYPE}, "source_nation": "Switzerland"}}
        popup = {"from_nation": "Switzerland", "proposal_type": V.CLIENT_PETITION_TYPE,
                 "is_petition": True, "dialogue_id": 7, "clauses": ["x"]}

        def answerer(**policy):
            return pdriver.Answerer(None, None, dict(pdriver.POLICY_DEFAULTS, **policy), False)

        assert answerer(diplomacy="accept")._pick_dialogue_choice(dlg) == "grant the petition"
        assert answerer(diplomacy="decline")._pick_dialogue_choice(dlg) == "refuse the petition"
        assert answerer(diplomacy="accept")._pick_dialogue_choice(popup) == "grant the petition"
        assert answerer(diplomacy="decline")._pick_dialogue_choice(popup) == "refuse the petition"
        assert answerer(diplomacy="accept", client_petition="refuse")._pick_dialogue_choice(dlg) == "refuse the petition"
        assert answerer(diplomacy="decline", client_petition="grant")._pick_dialogue_choice(popup) == "grant the petition"
        disabled = json.loads(json.dumps(dlg))
        disabled["options"][0]["enabled"] = False
        disabled["options"][0]["description"] = "no DP"
        a = answerer(diplomacy="accept")
        assert a._pick_dialogue_choice(disabled) is None and a.last_standing_reason == "no DP"
        plain = {"type": "incoming_proposal", "target_nation": "Prussia",
                 "options": [{"label": "Accept", "action": "accept_ai_proposal"},
                             {"label": "Reject", "action": "reject_ai_proposal"}],
                 "context": {"proposal_type": "open_borders", "proposal": {"type": "open_borders"}}}
        assert answerer(diplomacy="decline")._pick_dialogue_choice(plain) == "reject_ai_proposal"

    def test_the_grant_run_prints_the_web_on_every_ledger_row_and_answers_the_petition(self, driven_grant):
        md, records, meta, world = driven_grant
        ledger_lines = [ln for ln in md.splitlines() if ln.startswith("- LEDGER ")]
        assert len(ledger_lines) >= 7
        for line in ledger_lines:
            assert re.search(r" · vassals (\w[\w ]* \d+( · \w[\w ]* \d+)*|none)$", line), line
        assert all(" · vassals " in ln and RAW_TAG not in ln for ln in ledger_lines)
        assert any("Kingdom of Italy" in ln for ln in ledger_lines)
        ledger_records = [r for r in records if r.get("kind") == "ledger"]
        assert ledger_records and all(isinstance(r.get("vassals"), dict) for r in ledger_records)
        assert set(ledger_records[0]["vassals"]) == {"Holland", "Kingdom of Italy", "Switzerland"}
        hits = POPUP_LINE.findall(md)
        assert hits, "no client_petition popup line in the digest"
        assert all(answer == "grant" for _, answer in hits), hits
        # the grant's effect is in the world the run left behind
        petitioner = {"Holland": "Holland", "Switzerland": "Switzerland",
                      "Kingdom of Italy": RAW_TAG}[hits[0][0]]
        row = world.vassals[petitioner]
        assert row.get("remission_left", 0) > 0 or row.get("granted_regions")
        assert _rel(world, petitioner, PLAYER) >= V.PETITION_RELATION_STEP
        assert [e for e in world.event_log if e.get("type") == "client_petition_answered"
                and e.get("outcome") == "granted"]
        assert "client_petition" not in meta.get("policy", {})   # absent unless passed

    def test_the_refuse_arm_refuses(self):
        md, records, meta, world = _drive("refuse", 7, client_petition="refuse")
        hits = POPUP_LINE.findall(md)
        assert hits and all(answer == "refuse" for _, answer in hits), hits
        assert meta["policy"]["client_petition"] == "refuse"
        assert [e for e in world.event_log if e.get("type") == "client_petition_answered"
                and e.get("outcome") == "refused"]

    def test_lever_down_the_ledger_row_is_the_pre_iq7_row(self):
        md, records, meta, world = _drive("web_down", 3,
                                          levers=((pdriver, "THE_DIGEST_SEES_THE_WEB", False),))
        ledger_lines = [ln for ln in md.splitlines() if ln.startswith("- LEDGER ")]
        assert ledger_lines
        assert not any("vassals" in ln for ln in ledger_lines)
        assert not any("vassals" in r for r in records if r.get("kind") == "ledger")

    def test_the_ledger_line_appends_the_web_last(self):
        class Rec:
            NET_COMPONENTS = pdriver.Digest.NET_COMPONENTS
            ledger_line = pdriver.Digest.ledger_line

            def __init__(self):
                self.lines, self.records, self._last_provinces = [], [], None

            def _md(self, s):
                self.lines.append(s)

            def record(self, kind, **f):
                self.records.append({"kind": kind, **f})

        r = Rec()
        r.ledger_line(100, 5, 12, provinces=3,
                      vassals=[("Holland", 88), ("Kingdom of Italy", 84), ("Switzerland", 71)])
        assert r.lines[0].endswith(" · vassals Holland 88 · Kingdom of Italy 84 · Switzerland 71")
        assert r.records[0]["vassals"] == {"Holland": 88, "Kingdom of Italy": 84, "Switzerland": 71}
        r2 = Rec()
        r2.ledger_line(100, 5, 12, provinces=3)
        assert r2.lines[0] == r.lines[0].rsplit(" · vassals", 1)[0]
        assert "vassals" not in r2.records[0]
        r3 = Rec()
        r3.ledger_line(100, 5, 12, provinces=3, vassals=[])
        assert r3.lines[0].endswith(" · vassals none") and r3.records[0]["vassals"] == {}


# ═══════════════════════════════════════════════════════════════════════════
# T21 — the campaign log: the conscious flip and the new type
# ═══════════════════════════════════════════════════════════════════════════

COUNT_PIN = re.compile(r"assert len\((?:CL\.)?CAMPAIGN_LOG_TYPES\) == (\d+)(.*)$")


class TestT21CampaignLog:
    def test_the_type_is_registered(self):
        assert "client_petition_answered" in CL.CAMPAIGN_LOG_TYPES
        assert CL.CATEGORY_MAP["client_petition_answered"] == "diplomacy"
        assert len(CL.CAMPAIGN_LOG_TYPES) == 168  # 164->165 flipped consciously: IQ-7 (Sept 16, 2026) adds `client_petition_answered` — the web's first non-rebellion decision had no persistent surface  # 165->166 flipped consciously: GE-1 adds `campaign_ending` (the Fall, the Verdict, a Humbled Peace each leave one chronicle line)  # 166->167 flipped consciously: GE-3 adds the congress chronicle type (summons, recognitions, the War of the Congress, the dissolution)  # 167->168 flipped consciously: VP-M1 (GE-D1, Sept 25, 2026) adds `marshal_wounded`

    def test_every_count_pin_moved_with_the_rationale(self):
        """The census over the flips: every file that pins the count reads
        the CURRENT count and names the flip that set it on that line. A stale
        count fails here by name. ⚑ GE-1 (Sept 25, 2026) moved it 165 -> 166
        (`campaign_ending`) — flipped consciously: the census now reads 166
        and GE-1, with IQ-7's own flip still on the line before it. ⚑ GE-3
        (Sept 25, 2026) moved it 166 -> 167 (`congress`, the Congress of
        Paris's chronicle) — flipped consciously: the census now reads 167
        and GE-3, with IQ-7's and GE-1's flips still on the line before it.
        ⚑ GE-V / VP-M1 (Sept 25, 2026) moved it 167 -> 168 (`marshal_wounded`,
        the generals' mortality) — flipped consciously: the census now reads
        168 and VP-M1, with the three earlier flips still on the line."""
        pinned = {}
        for path in sorted((REPO / "tests").glob("test_*.py")):
            for line in path.read_text(encoding="utf-8").splitlines():
                m = COUNT_PIN.search(line)
                if m:
                    pinned[path.name] = (int(m.group(1)), m.group(2))
        assert len(pinned) >= 14, sorted(pinned)
        stale = {name: value for name, (value, _) in pinned.items() if value != 168}
        assert stale == {}, stale
        unexplained = [name for name, (_, tail) in pinned.items()
                       if "IQ-7" not in tail or "GE-1" not in tail
                       or "GE-3" not in tail or "VP-M1" not in tail]
        assert unexplained == [], unexplained

    def test_the_one_liners(self):
        base = {"type": "client_petition_answered", "vassal": RAW_TAG, "lord": PLAYER}
        assert CL.format_event_oneliner({**base, "subject": "province", "region": "Tyrol",
                                         "outcome": "granted"}) == (
            "The Kingdom of Italy's petition for Tyrol — granted.")
        assert CL.format_event_oneliner({**base, "vassal": "Switzerland", "subject": "relief",
                                         "outcome": "unanswered", "penalty": True}) == (
            "Switzerland's petition for relief from tribute — left unanswered, refused.")
        assert CL.format_event_oneliner({**base, "vassal": "Switzerland", "subject": "relief",
                                         "outcome": "unanswered", "penalty": False}) == (
            "Switzerland's petition for relief from tribute — left unanswered.")
        assert CL.format_event_oneliner({**base, "subject": "relief", "outcome": "refused"}) == (
            "The Kingdom of Italy's petition for relief from tribute — refused.")

    def test_the_players_own_answer_passes_the_fog(self):
        w = _europe()
        V.refuse_petition(w, "Switzerland", PLAYER, V.petition_terms(w, "Switzerland"), how="refused")
        rows = [e for e in w.event_log if e.get("type") == "client_petition_answered"]
        assert rows
        with _quiet():
            visible = CL.filter_campaign_log(rows, w)
        assert len(visible) == len(rows)

    def test_the_ai_lords_answer_carries_the_lord_as_its_nation(self):
        w = _holland_under_prussia()
        with _quiet():
            events = V.process_vassal_petitions(w)
        assert events[0]["nation"] == "Prussia" and events[0]["type"] == "client_petition_answered"
        assert "Holland" in events[0]["message"] and "remitted" in events[0]["message"]


# ═══════════════════════════════════════════════════════════════════════════
# IQ7-X4 — the PL-14 safety net keeps a DELIVERED result (lead, integration)
# ═══════════════════════════════════════════════════════════════════════════

class TestThePL14SafetyNetKeepsADeliveredResult:
    """`main._respond_to_dialogue_sync`'s PL-14 safety net minted a fallback
    `proposal_result` ("Diplomatic Action", outcome DERIVED from the message
    — REJECT for a GRANTED petition) whenever the handler's own popup had
    already been delivered by the first response build, which pops it and
    clears the world slot; "the slot is empty" read as "the handler forgot".
    Builder B masked it for the petition with `suppress_proposal_result_popup`;
    the guard on the response's own `proposal_result` closes it for EVERY
    handler (`offer_vassalage` measured the same fallback on the wire)."""

    def test_a_granted_petition_keeps_its_own_result_without_the_flag(
            self, http, monkeypatch):
        import backend.commands.diplomatic_executor as DE
        cls = next(c for c in vars(DE).values()
                   if isinstance(c, type) and hasattr(c, "_handle_accept_ai_proposal"))
        real = cls._handle_accept_ai_proposal

        def stripped(self, *a, **k):
            res = real(self, *a, **k)
            if isinstance(res, dict):
                res.pop("suppress_proposal_result_popup", None)   # the mask off
            return res

        monkeypatch.setattr(cls, "_handle_accept_ai_proposal", stripped)
        w, client = http
        w.vassals["Switzerland"]["loyalty"] = 85
        dlg = _deliver_seen(w, client, "Switzerland")
        r = _respond(client, "grant the petition", dlg["dialogue_id"])
        assert r.get("success") is True, r.get("message")
        assert r["proposal_result"]["proposal_type"] == "Client's Petition", r["proposal_result"]
        assert r["proposal_result"]["outcome"] == "ACCEPT"

    def test_the_guard_reads_the_delivered_result(self):
        import inspect
        import backend.main as M
        src = inspect.getsource(M._respond_to_dialogue_sync)
        assert 'and response.get("proposal_result") is None' in src
