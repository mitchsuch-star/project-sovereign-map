"""RE-1 — "Affairs of State": the engine, UNARMED (`docs/RECURRING_EVENTS_SPEC.md`
§5 the block, §7 the pacing, §8 one function, §9 the engine, §10 the seeds,
§11 the saves, §13 Rule 8, §16 "RE-1"; row RE built before S15 by the user's
ruling of October 31, 2026 — §0c).

The shipped 1805 boot authors no `moments.affairs` key, so every pin here arms
the real booted world with the staged fixture
`tests/fixtures/affairs_block.json` (the S14c deck as ruled, plus T1 the
Arch-Chancellor's Letters, T2 the Host's Claims at two corps and T3 Berthier's
Memorial exactly as §6.1 authors them) and drives the real seams: the
occurrence rows and their frozen {lord, bind, tier}; the derived cooldowns and
caps; the pulse on `historical` and across the ten seeds; shown = applied for
the two new ops on three boards, the grip floor included; `bites`; the
moments' arrival turns invariant armed against unarmed, and the free
withdrawal; the look-ahead; a save round trip and the backfill; the
validator's refusals; the Rule 8 and seed censuses; the alarm untouched; the
trace's teeth on the new ops; ERR-2 (the Secretariat).
"""
import contextlib
import copy
import io
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import imperial_designs as ID
from backend.game_logic import moments as MO
from tests import _chip_census as C

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
MOMENTS_FIXTURE = REPO / "tests" / "fixtures" / "moments_block.json"
SWEEP_SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
               "eylau", "friedland", "wagram", "lodi", "rivoli"]
CORPS = ("Ney", "Davout", "Soult", "Lannes", "Murat")     # France's marshals at home at boot
T1, T2, T3 = "chancellors_letters", "the_host", "berthiers_memorial"


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
    return world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def _at(world, turn):
    world.current_turn = int(turn)
    world.invalidate_active_nations_cache()


def _tick(world):
    with _quiet():
        return MO.tick(world)


def _run(world, turns):
    """Tick the mornings `turns` in order; the ids delivered, by turn."""
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


def _rel(world, court):
    return int(world.nation_relations.get(world._make_diplo_key("France", court), 0))


def _no_moments(world):
    """Every dated and causal moment passed, so the affairs stand alone."""
    for e in MO.deck(world):
        world.moments["state"][str(e["id"])] = {"status": "passed", "turn": 1, "reason": "premise"}


def _quarter(world, names, region="Swabia"):
    """France's corps `names` quartered on `region` (Swabia is Bavaria's)."""
    for name in names:
        world.marshals[name].location = region


def _afield(world, authority=80, region="Swabia"):
    world.marshals["Napoleon"].location = region
    world.authority_tracker.authority = int(authority)


def _rows(world):
    return dict(AF.all_occurrences(world))


def _moment_rows(world):
    return [e for e in world.event_log if e.get("type") == "moment"]


def _receipts(world):
    return [e["template_vars"]["line"] for e in world.pending_dispatch_events
            if e["type"] == "moment_receipt"]


# ═══════════════════════════════════════════════════════════════════════════
# Unarmed — the shipped boot authors no `affairs` key
# ═══════════════════════════════════════════════════════════════════════════

class TestUnarmed:
    def test_the_shipped_boot_is_unarmed_and_the_tick_writes_nothing(self, world):
        assert "affairs" not in world.moments["block"]
        assert AF.armed(world) is False and MO.armed(world) is True
        before = copy.deepcopy(world.moments)
        for turn in (1, 2, 3, 7, 8):
            _at(world, turn)
            assert all(not MO.is_occurrence(x) for x in _tick(world))
        after = copy.deepcopy(world.moments)
        after["state"] = before["state"]            # the moments' own rows aside
        assert after == before and "affairs" not in world.moments
        assert AF.watch(world) == [] and AF.deliver_due(world) == []
        assert AF.runtime(world) == {} and "affairs" not in world.moments

    def test_the_shipped_scenario_authors_no_affairs_key(self):
        block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        assert "affairs" not in block
        from tools._s14c_sweep_record import mechanical_block
        assert set(mechanical_block(block)) == {"owner", "pacing", "deck"}

    def test_every_affairs_reader_answers_nothing_on_an_unarmed_world(self, world):
        assert AF.deck(world) == [] and AF.block(world) == {}
        assert MO.affairs_deck(world) == [] and MO.entry(world, "the_host#1") is None
        assert AF.withdraw_standing(world, ["bavarian_match"]) == []
        assert AF.resolve_courts(world) == []


# ═══════════════════════════════════════════════════════════════════════════
# The store and the ids
# ═══════════════════════════════════════════════════════════════════════════

class TestTheStoreAndTheIds:
    def test_the_fixture_arms_both_decks_and_the_dated_deck_stays_its_own(self, armed):
        assert AF.armed(armed)
        assert [e["id"] for e in MO.deck(armed)] == ["bavarian_match", "throne_of_holland",
                                                      "crown_of_the_reich", "decree_of_berlin"]
        assert [e["id"] for e in AF.deck(armed)] == [T1, T2, T3]

    def test_an_occurrence_id_resolves_to_its_template(self, armed):
        assert MO.entry(armed, "the_host#2")["id"] == T2
        assert MO.entry(armed, T2)["id"] == T2
        assert MO.entry(armed, "bavarian_match")["id"] == "bavarian_match"
        assert MO.entry(armed, "nowhere#1") is None
        assert MO.template_of("the_host#12") == T2 and MO.template_of("bavarian_match") == "bavarian_match"
        assert MO.is_occurrence("the_host#1") and not MO.is_occurrence("the_host")

    def test_the_moments_rows_are_blind_to_occurrences(self):
        state = {"bavarian_match": {"status": "fired", "turn": 8},
                 "the_host#1": {"status": "fired", "turn": 7},
                 "the_host#2": {"status": "passed", "turn": 11, "reason": "crowded"}}
        assert set(MO.moment_rows(state)) == {"bavarian_match"}

    def test_the_runtime_store_round_trips_as_ints_and_short_strings(self):
        raw = {"moments": {"block": _block(), "state": {"the_host#1": {"status": "fired", "turn": 7}},
                           "affairs": {"streaks": {"the_host|Bavaria": 3, "x": "no"}, "morning": 7,
                                       "due": {"berthiers_memorial|": 6}, "not_before": 4,
                                       "flag": True, "list": [1, 2]}}}
        store = MO.store_from_data(raw)
        assert store["affairs"] == {"streaks": {"the_host|Bavaria": 3}, "morning": 7,
                                    "due": {"berthiers_memorial|": 6}, "not_before": 4}
        assert store["block"]["affairs"]["deck"][1]["id"] == T2

    def test_scaled_op_multiplies_the_listed_amounts_unless_a_tier_is_authored(self):
        assert MO.scaled_op({"op": "gold", "amount": 300}, 3)["amount"] == 900
        assert MO.scaled_op({"op": "relation", "delta": -2}, 2)["delta"] == -4
        assert MO.scaled_op({"op": "authority", "amount": -5, "tiers": {"2": -8}}, 2)["amount"] == -8
        assert MO.scaled_op({"op": "gold", "amount": 300}, 1) == {"op": "gold", "amount": 300}
        # an administrative action is one; a point and a law are never tiered by the multiplier
        assert MO.scaled_op({"op": "admin", "amount": 1}, 2)["amount"] == 1
        assert MO.scaled_op({"op": "dp", "amount": 1}, 3)["amount"] == 1
        assert MO.scaled_op({"op": "dp", "amount": 1, "tiers": {"3": 2}}, 3)["amount"] == 2

    def test_tiers_from_the_two_scale_shapes(self, armed):
        host = MO.entry(armed, T2)
        assert [AF.tier_of(host, n) for n in (2, 3, 4, 5, 6, 9)] == [1, 1, 2, 2, 3, 3]
        chancellor = MO.entry(armed, T1)
        assert [AF.tier_of(chancellor, n) for n in (6, 11, 12, 20)] == [1, 1, 2, 2]
        assert AF.tier_of(MO.entry(armed, T3), 50) == 1


# ═══════════════════════════════════════════════════════════════════════════
# The pulse — timing only, no dice (§10)
# ═══════════════════════════════════════════════════════════════════════════

class TestThePulse:
    def test_historical_gives_the_authored_values(self, armed):
        assert armed.campaign_seed == "historical"
        assert AF.pulse_first(armed) == 7 and AF.pulse_gap(armed, 0) == 5 and AF.pulse_gap(armed, 3) == 5
        assert AF.pacing(armed) == {"first": 7, "first_band": (6, 9), "gap": 5, "gap_band": (4, 7),
                                    "cap_act": 6, "wait": 4}

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_every_seed_draws_inside_its_band(self, armed, seed):
        armed.campaign_seed = seed
        assert 6 <= AF.pulse_first(armed) <= 9
        assert all(4 <= AF.pulse_gap(armed, n) <= 7 for n in range(8))

    def test_the_band_varies_across_the_sweep_and_the_draw_is_stateless(self, armed):
        firsts = set()
        for seed in SWEEP_SEEDS:
            armed.campaign_seed = seed
            firsts.add(AF.pulse_first(armed))
            assert AF.pulse_first(armed) == AF.pulse_first(armed)
        assert len(firsts) > 1

    def test_no_die_and_no_seed_read_outside_affairs(self):
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        code = re.sub(r'""".*?"""', "", src, flags=re.S)
        code = "\n".join(line.split("#")[0] for line in code.splitlines())
        assert "import random" not in code and "random." not in code and "ai_rng" not in code
        moments_src = (BACKEND / "game_logic" / "moments.py").read_text(encoding="utf-8")
        moments_code = re.sub(r'""".*?"""', "", moments_src, flags=re.S)
        assert "seeded_" not in moments_code and "campaign_seed" not in moments_code


# ═══════════════════════════════════════════════════════════════════════════
# The arrival — the Host's Claims, frozen at delivery (§5, §6.1)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheArrival:
    def test_the_hosts_claims_arrive_on_the_first_morning_of_the_pulse(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))                  # + Bernadotte at Franconia = 3 corps
        assert _run(armed, range(1, 7)) == {}                # due from turn 3, the pulse opens at 7
        assert _run(armed, [7]) == {7: ["the_host#1"]}
        row = MO.status_row(armed, "the_host#1")
        assert row == {"id": "the_host#1", "status": "fired", "turn": 7, "lord": "France",
                       "bind": {"host": "Bavaria"}, "tier": 1}
        letter = _letter(armed, "the_host#1")
        assert letter is not None and MO.is_moment_letter(letter)
        payload = letter["popup_payload"]
        assert payload["moment_id"] == "the_host#1" and payload["register"] == "affair"
        assert payload["occurrence"] == "the_host#1" and payload["title"] == "The Host's Claims"
        # RE-2 (§12b.2 line 2): the host's letter is signed by its minister
        # from the cast (Montgelas), "for the court of Munich" — RE-1's
        # placeholder "The court of Bavaria" retired with the dress.
        assert payload["diplomat_name"] == "Montgelas"
        assert (payload["writer"], payload["office"]) == ("Montgelas", "for the court of Munich")
        assert payload["board"][0].startswith("3 of your corps stand on Bavaria's soil")
        assert "Pay the host's claims: 300 gold" in payload["answers"][0]["quote"]
        assert "Live off the land: Bavaria's goodwill" in payload["answers"][1]["quote"]
        notices = [n for n in armed.notifications.get_pending()
                   if (n.get("details") or {}).get("moment_id") == "the_host#1"]
        assert len(notices) == 1
        assert [(e["phase"], e["moment"], e["nation"], e.get("register")) for e in _moment_rows(armed)] == [
            ("arrived", "the_host#1", "France", "affair")]

    def test_the_tier_is_frozen_at_delivery_and_survives_the_corps_marching_home(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout", "Lannes"))        # 4 corps: tier 2
        _run(armed, range(1, 8))
        row = MO.status_row(armed, "the_host#1")
        assert row["tier"] == 2
        for name in ("Ney", "Davout", "Lannes"):
            armed.marshals[name].location = "Lorraine"
        plan = MO.plan(armed, MO.entry(armed, "the_host#1"), "accept", row)
        assert plan["rows"][0]["amount"] == 600 and plan["id"] == "the_host#1" and plan["lord"] == "France"
        assert plan["receipt"] == "−600 gold"
        decline = MO.plan(armed, MO.entry(armed, "the_host#1"), "decline", row)
        assert [r["op"] for r in decline["rows"]] == ["relation", "loyalty"]
        assert decline["rows"][0]["delta"] == -4 and decline["rows"][1].get("courts") == []

    def test_the_accept_applies_its_quote_through_the_endpoint(self, armed, client):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.nation_gold["France"] = 5000
        _run(armed, range(1, 8))
        letter = _letter(armed, "the_host#1")
        _make_current(armed, letter)
        rel, gold = _rel(armed, "Bavaria"), armed.nation_gold["France"]
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue",
                                 json={"choice": "accept_ai_proposal",
                                       "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert armed.nation_gold["France"] == gold - 300 and _rel(armed, "Bavaria") == rel
        row = MO.status_row(armed, "the_host#1")
        assert row["status"] == "answered" and row["answer"] == "accept" and row["receipt"] == "−300 gold"
        assert row["echo"] == "the Bavaria chancery: the account between Bavaria and Paris is square for the season."
        assert _letter(armed, "the_host#1") is None
        assert [e["phase"] for e in _moment_rows(armed)] == ["arrived", "answered"]
        assert _moment_rows(armed)[-1]["register"] == "affair"

    def test_the_decline_on_an_ally_bills_its_goodwill_and_leaves_the_purse(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))
        letter = _letter(armed, "the_host#1")
        rel, gold, loyalty = _rel(armed, "Bavaria"), armed.nation_gold["France"], dict(armed.vassals)
        with _quiet():
            result = MO.answer(armed, letter, "decline")
        assert result["success"] is True
        assert _rel(armed, "Bavaria") == rel - 2 and armed.nation_gold["France"] == gold
        assert {k: v["loyalty"] for k, v in armed.vassals.items()} == {k: v["loyalty"] for k, v in loyalty.items()}
        row = MO.status_row(armed, "the_host#1")
        assert row["receipt"] == f"Bavaria {rel} → {rel - 2}" and row["echo"] == ""

    def test_a_client_host_is_billed_in_loyalty_never_in_goodwill(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"), region="Milan")   # + Massena: 3 corps on the Kingdom of Italy
        _run(armed, range(1, 8))
        row = MO.status_row(armed, "the_host#1")
        assert row["bind"] == {"host": "KingdomOfItaly"} and row["tier"] == 1
        letter = _letter(armed, "the_host#1")
        rel, loyalty = _rel(armed, "KingdomOfItaly"), armed.vassals["KingdomOfItaly"]["loyalty"]
        with _quiet():
            MO.answer(armed, letter, "decline")
        assert armed.vassals["KingdomOfItaly"]["loyalty"] == loyalty - 2
        assert _rel(armed, "KingdomOfItaly") == rel

    def test_a_standing_letter_re_plans_at_every_read_but_keeps_its_id(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))
        letter = _letter(armed, "the_host#1")
        armed.nation_gold["France"] = 100
        payload = MO.refresh_letter(armed, letter)
        assert payload["moment_id"] == "the_host#1"
        assert "300 gold (the treasury holds 100)" in payload["answers"][0]["quote"]
        verdict = MO.answer_verdict(armed, letter, "accept_ai_proposal")
        assert not verdict.ok and "300 gold is asked" in verdict.message


# ═══════════════════════════════════════════════════════════════════════════
# Cooldowns, caps, the crowd-out (§7, §11)
# ═══════════════════════════════════════════════════════════════════════════

class TestCooldownsAndCaps:
    def test_the_cooldown_is_derived_from_the_rows_and_the_cap_resets_at_the_verdict(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))
        with _quiet():
            MO.answer(armed, _letter(armed, "the_host#1"), "accept")
        assert _run(armed, range(8, 17)) == {}               # cooldown 10 from turn 7
        assert _run(armed, [17]) == {17: ["the_host#2"]}
        with _quiet():
            MO.answer(armed, _letter(armed, "the_host#2"), "accept")
        assert _run(armed, range(18, 44)) == {}              # cap 2 per host an act
        assert _run(armed, [44]) == {44: ["the_host#3"]}     # the second act (Q12)
        assert AF.act_count(armed, 44) == 1

    def test_a_crowded_out_affair_writes_its_row_and_arms_the_cooldown(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 7, "foregrounded": True,
                                         "foregrounded_turn": 7}}
        rel, gold = _rel(armed, "Bavaria"), armed.nation_gold["France"]
        assert _run(armed, range(1, 11)) == {}
        assert AF.runtime(armed)["due"] == {"the_host|Bavaria": 4}   # four busy mornings waited, 7–10
        assert _run(armed, [11]) == {}                        # the fifth: crowded out
        assert AF.runtime(armed)["due"] == {}
        row = MO.status_row(armed, "the_host#1")
        assert row == {"id": "the_host#1", "status": "passed", "reason": "crowded", "turn": 11,
                       "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1}
        assert _rel(armed, "Bavaria") == rel and armed.nation_gold["France"] == gold   # nothing applied
        assert [(e["phase"], e["reason"]) for e in _moment_rows(armed)] == [("passed", "crowded")]
        armed.war_intents = {}
        assert _run(armed, range(12, 21)) == {}               # the cooldown from 11
        assert _run(armed, [21]) == {21: ["the_host#2"]}

    def test_the_set_aside_line_is_aggregated_and_only_for_a_watched_matter(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 1, "foregrounded": True,
                                         "foregrounded_turn": 1}}
        _run(armed, range(1, 12))
        assert MO.status_row(armed, "the_host#1")["reason"] == "crowded"
        assert _receipts(armed) == []                         # its Watch never showed
        armed.moments["state"].clear()
        _no_moments(armed)
        AF.runtime(armed)["due"].clear()
        _at(armed, 12)
        assert AF.watch(armed) == ["3 corps on Bavaria's soil: 11 of 3 mornings — its court may present its claims."]
        _run(armed, range(12, 18))                            # five busy mornings, 12–16: crowded at 17
        assert MO.status_row(armed, "the_host#1")["reason"] == "crowded"
        assert _receipts(armed) == ["The Secretariat set aside 1 matter"]

    def test_a_due_mark_is_dropped_silently_when_the_premise_falls(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 7, "foregrounded": True,
                                         "foregrounded_turn": 7}}
        _run(armed, range(1, 9))
        assert AF.runtime(armed)["due"] == {"the_host|Bavaria": 2}
        for name in ("Ney", "Davout"):
            armed.marshals[name].location = "Lorraine"
        _run(armed, [9])
        assert AF.runtime(armed)["due"] == {} and _rows(armed) == {}

    def test_a_matter_held_by_the_pulse_is_not_crowded_out(self, armed):
        """P8's ruled "about T13": the pulse decides when the deck may speak;
        waiting on the gap or the look-ahead is never a busy desk."""
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))                              # the look-ahead holds 7
        assert AF.runtime(armed).get("due", {}) == {}
        _run(armed, [8])                                      # the Match arrives: the gap closes the pulse
        assert AF.runtime(armed)["due"] == {}
        with _quiet():
            MO.answer(armed, _letter(armed, "bavarian_match"), "decline")
        _run(armed, range(9, 13))                             # the gap: nothing waits, nothing ages
        assert AF.runtime(armed)["due"] == {}
        assert _run(armed, [13]) == {13: ["the_host#1"]}
        assert AF.runtime(armed)["due"] == {}


# ═══════════════════════════════════════════════════════════════════════════
# The two ops — shown = applied on three boards (§5, Q6)
# ═══════════════════════════════════════════════════════════════════════════

OCC_T1 = {"id": "chancellors_letters#1", "lord": "France", "bind": {}, "tier": 1}


class TestTheTwoOps:
    def test_the_op_table_grew_by_two_and_no_affair_reaches_the_alarm(self):
        assert set(MO.OPS) >= {"authority", "admin"} and len(MO.OPS) == 9
        assert "alarm" in AF.BARRED_OPS and "alarm" not in AF.AFFAIR_OPS

    @pytest.mark.parametrize("authority, loss", [(80, 5), (73, 2), (70, 0)])
    def test_authority_delivers_min_of_the_price_and_the_grip_above_the_floor(self, armed, authority, loss):
        armed.authority_tracker.authority = authority
        e = MO.entry(armed, T1)
        p = MO.plan(armed, e, "decline", OCC_T1)
        row = p["rows"][0]
        assert (row["before"], row["loss"], row["after"]) == (authority, loss, authority - loss)
        assert f"Authority {authority} → {authority - loss}" in p["quote"]
        MO._apply(armed, p)
        assert armed.authority_tracker.authority == authority - loss

    def test_the_floor_is_on_the_grip_of_a_losing_war_and_never_a_rise(self, armed, monkeypatch):
        from backend.models import authority as A
        monkeypatch.setattr(A, "_worst_war_score", lambda w, n: -35)      # the losing-war dock, −8
        armed.authority_tracker.authority = 85
        assert A.get_imperial_grip(armed, "France") == 77
        p = MO.plan(armed, MO.entry(armed, T1), "decline", OCC_T1)
        assert (p["rows"][0]["loss"], p["rows"][0]["after"]) == (5, 80)
        armed.authority_tracker.authority = 75                           # grip 67: under the floor
        p = MO.plan(armed, MO.entry(armed, T1), "decline", OCC_T1)
        assert (p["rows"][0]["loss"], p["rows"][0]["after"]) == (0, 75)
        MO._apply(armed, p)
        assert armed.authority_tracker.authority == 75

    def test_a_court_without_a_tracker_is_skipped(self, armed):
        p = MO.plan(armed, MO.entry(armed, T1), "decline", dict(OCC_T1, lord="Austria"))
        assert p["rows"][0]["skip"] is True and p["effect"] == "no change."

    def test_admin_spends_one_of_the_days_actions_and_is_closed_with_none_left(self, armed):
        armed.admin_actions_remaining = 2
        e = MO.entry(armed, T1)
        p = MO.plan(armed, e, "accept", OCC_T1)
        assert p["ok"] and p["lines"] == ["1 administrative action (1 left today)"]
        MO._apply(armed, p)
        assert armed.admin_actions_remaining == 1
        armed.admin_actions_remaining = 0
        p = MO.plan(armed, e, "accept", OCC_T1)
        # RE-2: the refusal is the closed button's second line (≤ 40, §12b.2)
        assert not p["ok"] and p["refusal"] == "the day's administration is spoken for."
        assert len(p["refusal"]) <= MO.BUTTON_LINE_MAX

    def test_a_closed_accept_leaves_the_letter_standing(self, armed):
        _no_moments(armed)
        _afield(armed, authority=80)
        _run(armed, range(1, 8))
        letter = _letter(armed, "chancellors_letters#1")
        assert letter is not None
        armed.admin_actions_remaining = 0
        with _quiet():
            result = MO.answer(armed, letter, "accept")
        assert result["success"] is False and "is not open" in result["message"]
        assert MO.status(armed, "chancellors_letters#1") == "fired" and _letter(armed, "chancellors_letters#1") is letter

    def test_the_trace_judges_the_new_ops_figures(self, armed):
        from tools._moments_trace import _delivered
        armed.authority_tracker.authority = 80
        armed.admin_actions_remaining = 2
        rows = _delivered(armed, "France", {"op": "authority", "after": 75, "loss": 5})
        assert rows == [{"op": "authority", "figure": "authority", "quoted": 75, "delivered": 80}]
        rows = _delivered(armed, "France", {"op": "admin", "after": 1})
        assert rows == [{"op": "admin", "figure": "administrative actions", "quoted": 1, "delivered": 2}]


# ═══════════════════════════════════════════════════════════════════════════
# `bites` — the Arch-Chancellor writes only where the price bites (§6.1)
# ═══════════════════════════════════════════════════════════════════════════

class TestBites:
    def test_no_letter_at_full_standing_and_none_under_the_floor(self, armed):
        _no_moments(armed)
        _afield(armed, authority=100)
        assert _run(armed, range(1, 14)) == {}
        assert AF.streak_of(armed, MO.entry(armed, T1), "") == 13     # the premise held throughout
        armed.authority_tracker.authority = 71
        assert _run(armed, range(14, 20)) == {}

    def test_the_letter_comes_where_the_decline_lands_below_the_aura(self, armed):
        _no_moments(armed)
        _afield(armed, authority=80)
        assert _run(armed, range(1, 8)) == {7: ["chancellors_letters#1"]}
        row = MO.status_row(armed, "chancellors_letters#1")
        assert row["tier"] == 1 and row["bind"] == {"region": "Swabia", "sovereign": "Napoleon"}
        payload = _letter(armed, "chancellors_letters#1")["popup_payload"]
        assert payload["diplomat_name"] == "Cambacérès, Arch-Chancellor of the Empire"
        assert "Authority 80 → 75" in payload["answers"][1]["quote"]
        assert payload["board"] == ["The Emperor is afield at Swabia, 7 mornings running; his standing is 80."]

    def test_twelve_mornings_afield_raise_the_price_to_eight(self, armed):
        _no_moments(armed)
        _afield(armed, authority=80)
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 7, "foregrounded": True,
                                         "foregrounded_turn": 7}}
        _run(armed, range(1, 12))                             # crowded out at 11
        armed.war_intents = {}
        assert _run(armed, range(12, 22)) == {21: ["chancellors_letters#2"]}
        row = MO.status_row(armed, "chancellors_letters#2")
        assert row["tier"] == 2
        p = MO.plan(armed, MO.entry(armed, T1), "decline", row)
        assert p["rows"][0]["amount"] == -8 and p["rows"][0]["after"] == 72

    def test_the_door_arrives_at_war_with_the_chest_above_the_bar(self, armed):
        _no_moments(armed)
        assert _run(armed, range(1, 8)) == {}                 # the chest holds 800
        armed.nation_gold["France"] = 20_000
        assert _run(armed, range(8, 11)) == {}                # at war 4 turns running: the streak
        assert _run(armed, [11]) == {11: ["berthiers_memorial#1"]}
        payload = _letter(armed, "berthiers_memorial#1")["popup_payload"]
        assert "9,000 gold now, then 300 gold a turn" in payload["answers"][0]["quote"]
        assert payload["answers"][1]["quote"] == "Not now: no change."


# ═══════════════════════════════════════════════════════════════════════════
# The moments stay blind; the free withdrawal; the look-ahead (§7, P8)
# ═══════════════════════════════════════════════════════════════════════════

def _scripted_moments(world):
    """Thirty mornings on a booted world: the Match at 8, Holland's premise
    flipping inside her lead (18 → 19), the Crown anchored at 19 (told 20,
    lag 1); every moment answered on its morning, every affair left standing."""
    _quarter(world, ("Ney", "Davout"))
    state = ID._state(world)
    state["road"], state["proclaimed_turn"] = "rhine", 10
    state["fulfilled"]["rhine.confederation"] = 19
    arrivals = {}
    for turn in range(1, 31):
        if turn == 18:
            world.vassals["Holland"]["loyalty"] = 90
        if turn == 19:
            world.vassals["Holland"]["loyalty"] = 66
        _at(world, turn)
        for mid in _tick(world):
            if MO.is_occurrence(mid):
                continue
            arrivals[mid] = turn
            with _quiet():
                MO.answer(world, _letter(world, mid), "decline")
    return arrivals


class TestTheMomentsAreBlind:
    def test_the_moments_arrival_turns_are_invariant_armed_against_unarmed(self, world):
        from backend.models.world_state import WorldState
        block = _block()
        unarmed_block = {k: v for k, v in block.items() if k != "affairs"}
        with _quiet():
            control = WorldState.from_scenario(str(SCENARIO))
        control.moments = MO.from_block(unarmed_block)
        world.moments = MO.from_block(block)
        # The Crown told at 20, lag 1 → 21, held one morning by the moments' own
        # min_gap (3) from Holland's arrival at 19 — the same on both arms.
        expected = {"bavarian_match": 8, "throne_of_holland": 19, "crown_of_the_reich": 22}
        assert _scripted_moments(control) == expected
        assert _scripted_moments(world) == expected
        rows = _rows(world)
        assert rows["the_host#1"]["turn"] == 13 and rows["the_host#1"]["status"] == "withdrawn"
        assert rows["the_host#1"]["set_aside_for"] == "throne_of_holland"

    def test_a_moment_withdraws_a_standing_affair_free(self, armed, monkeypatch):
        monkeypatch.setattr(AF, "LOOK_AHEAD", 0)             # let the affair land on 7
        _quarter(armed, ("Ney", "Davout"))
        assert _run(armed, range(1, 8)) == {7: ["the_host#1"]}
        rel, gold = _rel(armed, "Bavaria"), armed.nation_gold["France"]
        assert _run(armed, [8]) == {8: ["bavarian_match"]}
        row = MO.status_row(armed, "the_host#1")
        assert row["status"] == "withdrawn" and row["withdrawn_turn"] == 8
        assert row["set_aside_for"] == "bavarian_match"
        assert row["receipt"] == "The Host's Claims was set aside for The Bavarian Match"
        assert _letter(armed, "the_host#1") is None and _letter(armed, "bavarian_match") is not None
        assert _rel(armed, "Bavaria") == rel and armed.nation_gold["France"] == gold
        assert _receipts(armed) == ["The Host's Claims was set aside for The Bavarian Match"]
        assert [(e["phase"], e["moment"]) for e in _moment_rows(armed)] == [
            ("arrived", "the_host#1"), ("arrived", "bavarian_match"), ("withdrawn", "the_host#1")]
        assert armed.incoming_proposal_popup["moment_id"] == "bavarian_match"
        assert not [n for n in armed.notifications.get_pending()
                    if (n.get("details") or {}).get("moment_id") == "the_host#1"]
        with _quiet():
            MO.answer(armed, _letter(armed, "bavarian_match"), "decline")
        assert _run(armed, range(9, 18)) == {}                # the cooldown re-armed from 8
        assert _run(armed, [18]) == {18: ["the_host#2"]}

    def test_the_look_ahead_stands_an_affair_aside_before_a_dated_moment(self, armed):
        _quarter(armed, ("Ney", "Davout"))
        assert _run(armed, range(1, 8)) == {}                 # due, but the Match opens at 8
        assert AF.moment_imminent(armed, 7) is True and AF.moment_imminent(armed, 5) is False
        assert _run(armed, [8]) == {8: ["bavarian_match"]}
        with _quiet():
            MO.answer(armed, _letter(armed, "bavarian_match"), "decline")
        assert _run(armed, range(9, 13)) == {}                # the gap from the Match
        assert _run(armed, [13]) == {13: ["the_host#1"]}      # P8: "the first affair about T13"

    def test_the_look_ahead_ignores_a_moment_whose_premise_is_false(self, armed):
        _quarter(armed, ("Ney", "Davout"))
        armed.diplomatic_states[armed._make_diplo_key("France", "Bavaria")] = "PEACE"
        armed.nation_relations[armed._make_diplo_key("France", "Bavaria")] = 10
        armed.vassals["Bavaria"] = {"lord": "France", "loyalty": 60, "autonomy": 1,
                                    "path": "treaty", "tribute_rate": 0.75}
        armed.diplomatic_states[armed._make_diplo_key("France", "Bavaria")] = "VASSAL"
        armed.invalidate_active_nations_cache()
        assert MO.premise(armed, MO.entry(armed, "bavarian_match")) is True   # a vassal is warm
        armed.vassals.pop("Bavaria")
        armed.diplomatic_states[armed._make_diplo_key("France", "Bavaria")] = "PEACE"
        armed.invalidate_active_nations_cache()
        assert MO.premise(armed, MO.entry(armed, "bavarian_match")) is False
        world_due = AF.candidates(armed, 7)
        assert world_due == []                                # Bavaria at peace is no host
        assert AF.moment_imminent(armed, 7) is False


# ═══════════════════════════════════════════════════════════════════════════
# Saves and the backfill (§11)
# ═══════════════════════════════════════════════════════════════════════════

class TestSavesAndTheBackfill:
    def test_the_store_survives_a_round_trip_rows_and_runtime(self, armed):
        from backend.models.world_state import WorldState
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout", "Lannes"))
        _run(armed, range(1, 8))
        AF.watch(armed)
        restored = WorldState.from_dict(json.loads(json.dumps(armed.to_dict())))
        assert restored.moments == armed.moments
        assert restored.moments["state"]["the_host#1"]["tier"] == 2
        assert restored.moments["affairs"]["streaks"] == {"the_host|Bavaria": 7}
        assert restored.moments["affairs"]["watched"] == {}   # the letter stood: nothing to watch
        assert "_affairs_memo" not in restored.to_dict()

    def test_the_backfill_arms_a_pre_re_store_three_mornings_out(self, armed):
        del armed.moments["block"]["affairs"]
        assert not AF.armed(armed)
        _at(armed, 9)
        assert MO.backfill_affairs(armed, {"moments": _block()}) is True
        assert AF.armed(armed) and armed.moments["affairs"] == {"not_before": 12}
        assert MO.backfill_affairs(armed, {"moments": _block()}) is False       # never overwritten
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        assert _run(armed, range(9, 12)) == {}
        assert _run(armed, [12]) == {12: ["the_host#1"]}

    def test_the_save_manager_backfills_from_the_scenario_and_is_a_no_op_today(self, armed, tmp_path, monkeypatch):
        from backend import save_manager as SM
        del armed.moments["block"]["affairs"]
        SM._backfill_affairs(armed)                            # the shipped scenario authors none
        assert not AF.armed(armed)
        scenario = tmp_path / "scenario.json"
        scenario.write_text(json.dumps({"moments": _block()}), encoding="utf-8")
        monkeypatch.setattr(SM, "_BACKFILL_SCENARIOS",
                            {str(armed.scenario_name): (str(tmp_path), "scenario.json")})
        monkeypatch.setattr(SM.Path, "parents", property(lambda self: [Path("/"), Path("/")]), raising=False)
        SM._backfill_affairs(armed)
        assert AF.armed(armed) and armed.moments["affairs"]["not_before"] == armed.current_turn + 3

    def test_a_backfill_needs_a_moments_store(self, world):
        world.moments = {}
        assert MO.backfill_affairs(world, {"moments": _block()}) is False


# ═══════════════════════════════════════════════════════════════════════════
# The validator — at least 25 refusals (§5, §16)
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


def _aff(b, i=0):
    return b["affairs"]["deck"][i]


class TestTheValidator:
    def test_the_fixture_validates(self):
        assert _errors(_block()) == []

    def test_the_moments_deck_alone_still_validates(self):
        assert _errors(json.loads(MOMENTS_FIXTURE.read_text(encoding="utf-8"))) == []

    @pytest.mark.parametrize("label, mutate, path", [
        ("unknown predicate", lambda b: _aff(b)["when"].update(predicate="omen"), "moments.affairs.deck[0].when"),
        ("an op the table lacks", lambda b: _aff(b)["accept"]["ops"].append({"op": "war_exhaustion", "amount": 6}),
         "moments.affairs.deck[0].accept.ops[1]"),
        ("the alarm, barred", lambda b: _aff(b, 1)["accept"]["ops"].append({"op": "alarm", "amount": 1, "source": "moment_reich"}),
         "moments.affairs.deck[1].accept.ops[1]"),
        ("autonomy, barred", lambda b: _aff(b, 1)["accept"]["ops"].append({"op": "autonomy", "court": "Holland", "level": 2}),
         "moments.affairs.deck[1].accept.ops[1]"),
        ("a priced decline", lambda b: _aff(b, 1)["decline"]["ops"].append({"op": "gold", "amount": 100}),
         "moments.affairs.deck[1].decline.ops[2]"),
        ("admin on a decline", lambda b: _aff(b, 1)["decline"]["ops"].append({"op": "admin", "amount": 1}),
         "moments.affairs.deck[1].decline.ops[2]"),
        ("no source", lambda b: _aff(b).pop("source"), "moments.affairs.deck[0].source"),
        ("no watch", lambda b: _aff(b).pop("watch"), "moments.affairs.deck[0].watch"),
        ("a watch that promises", lambda b: _aff(b).update(watch="Cambacérès will write."), "moments.affairs.deck[0].watch"),
        ("an authority price without bites", lambda b: _aff(b).pop("bites"), "moments.affairs.deck[0].bites"),
        ("an id with the reserved #", lambda b: _aff(b).update(id="the_host#1"), "moments.affairs.deck[0].id"),
        ("an id that is a moment's", lambda b: _aff(b).update(id="bavarian_match"), "moments.affairs.deck[0].id"),
        ("an id that is a law's", lambda b: _aff(b).update(id="berlin_decree"), "moments.affairs.deck[0].id"),
        ("a moment id with the reserved #", lambda b: b["deck"][0].update(id="bavarian#match"), "moments.deck[0].id"),
        ("the wrong kind", lambda b: _aff(b).update(kind="letter"), "moments.affairs.deck[0].kind"),
        ("an unknown shape", lambda b: _aff(b).update(shape="edict"), "moments.affairs.deck[0].shape"),
        ("a door with two ops", lambda b: _aff(b, 2)["accept"]["ops"].append({"op": "gold", "amount": 100}),
         "moments.affairs.deck[2].accept.ops"),
        ("a door with a priced decline", lambda b: _aff(b, 2)["decline"]["ops"].append({"op": "relation", "court": "Austria", "delta": -2}),
         "moments.affairs.deck[2].decline.ops"),
        ("a title past 40", lambda b: _aff(b).update(title="T" * 41), "moments.affairs.deck[0].title"),
        ("a record past 240", lambda b: _aff(b).update(record="R" * 241), "moments.affairs.deck[0].record"),
        ("four variants", lambda b: _aff(b).update(variants=[{"key": "arrival", "value": "first", "text": "x"}] * 4),
         "moments.affairs.deck[0].variants"),
        ("a variant keyed to no fact", lambda b: _aff(b).update(variants=[{"key": "weather", "value": "rain", "text": "x"}]),
         "moments.affairs.deck[0].variants[0]"),
        ("a streak out of band", lambda b: _aff(b).update(streak=13), "moments.affairs.deck[0].streak"),
        ("a cooldown under the gap", lambda b: _aff(b).update(cooldown=4), "moments.affairs.deck[0].cooldown"),
        ("a cap of five", lambda b: _aff(b).update(cap=5), "moments.affairs.deck[0].cap"),
        ("a grace of seven", lambda b: _aff(b).update(grace=7), "moments.affairs.deck[0].grace"),
        ("gold out of band", lambda b: _aff(b, 1)["accept"]["ops"][0].update(amount=2500),
         "moments.affairs.deck[1].accept.ops[0].amount"),
        ("a positive authority", lambda b: _aff(b)["decline"]["ops"][0].update(amount=5),
         "moments.affairs.deck[0].decline.ops[0].amount"),
        ("a tier out of band", lambda b: _aff(b)["decline"]["ops"][0].update(tiers={"2": -12}),
         "moments.affairs.deck[0].decline.ops[0].tiers.2"),
        ("an unknown road", lambda b: _aff(b).update(roads=["moon"]), "moments.affairs.deck[0].roads"),
        ("a law not the owner's", lambda b: _aff(b, 2)["when"].update(law="landwehr"), "moments.affairs.deck[2].when.law"),
        ("the pulse's first out of band", lambda b: b["affairs"]["pacing"].update(first={"value": 12, "band": [6, 9]}),
         "moments.affairs.pacing.first.value"),
        ("a band not holding its value", lambda b: b["affairs"]["pacing"].update(gap={"value": 5, "band": [6, 7]}),
         "moments.affairs.pacing.gap.band"),
        ("a wait of nine", lambda b: b["affairs"]["pacing"].update(wait=9), "moments.affairs.pacing.wait"),
        ("a named voice with no name", lambda b: _aff(b)["voice"].pop("name"), "moments.affairs.deck[0].voice.name"),
        ("an unknown speaker", lambda b: _aff(b)["voice"].update(speaker="envoy", nation="Austria"), "moments.affairs.deck[0].voice"),
        ("an `ends` date that is not its turn", lambda b: _aff(b).update(ends={"date": "1808-11-07", "turn": 70}),
         "moments.affairs.deck[0].ends.date"),
        ("a scale with no measure", lambda b: _aff(b).update(scale={"at": 12}), "moments.affairs.deck[0].scale"),
        ("a latch asking more than its window", lambda b: _aff(b).update(latch={"of": 12, "at_least": 13}),
         "moments.affairs.deck[0].latch.at_least"),
        ("a caption past 36", lambda b: _aff(b)["accept"].update(caption="C" * 37), "moments.affairs.deck[0].accept.caption"),
        ("a button line past 40 rendered", lambda b: _aff(b)["accept"].update(button_line="B" * 41),
         "moments.affairs.deck[0].accept.button_line"),
        ("a relation op on an unknown court", lambda b: _aff(b, 1)["decline"]["ops"][0].update(court="Atlantis"),
         "moments.affairs.deck[1].decline.ops[0].court"),
        ("a min_corps of nine", lambda b: _aff(b, 1)["when"].update(min_corps=9), "moments.affairs.deck[1].when.min_corps"),
    ])
    def test_each_bad_block_is_refused(self, label, mutate, path):
        assert path in _bad(mutate), label

    def test_the_refusal_table_is_at_least_twenty_five_deep(self):
        src = Path(__file__).read_text(encoding="utf-8")
        assert src.count('"moments.affairs.') >= 25

    def test_an_ends_in_its_season_and_a_latch_pass(self):
        def mutate(b):
            _aff(b).update(ends={"date": "1808-11-07", "turn": 76}, latch={"of": 12, "at_least": 4})
        assert _bad(mutate) == set()

    def test_the_calendar_inverse_stays_the_validator_s_alone(self):
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        assert "turn_for_date" not in src and "calendar" not in src.replace("campaign", "")


# ═══════════════════════════════════════════════════════════════════════════
# Censuses — Rule 8, no nation literal, the alarm untouched, the one-liner
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCensuses:
    def test_no_province_scan_in_the_engine(self):
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        assert ".regions.values()" not in src and ".regions.items()" not in src

    def test_no_nation_literal_in_the_engine(self):
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        from backend.nation_config import EUROPE_ROSTER
        code = re.sub(r'""".*?"""', "", src, flags=re.S)
        code = "\n".join(line.split("#")[0] for line in code.splitlines())
        assert not [n for n in EUROPE_ROSTER if re.search(rf'["\']{n}["\']', code)]

    def test_no_lever_and_no_underscore_attribute_is_serialized(self):
        from tools._code_health_census import LEVER_RE
        src = (BACKEND / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        assert not LEVER_RE.search(src)

    def test_the_alarm_is_never_touched_by_an_affair(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        _afield(armed, authority=80)
        armed.nation_gold["France"] = 20_000
        before = dict(getattr(armed, "threat_by_target", {}) or {})
        delivered = {}
        for turn in range(1, 30):
            for mid in _run(armed, [turn]).get(turn, []):    # answered on its morning, by turns
                delivered[turn] = mid
                with _quiet():
                    MO.answer(armed, _letter(armed, mid), "accept" if turn % 2 else "decline")
        assert dict(getattr(armed, "threat_by_target", {}) or {}) == before
        # T3's door never opens here: the two Accepts spent both of the day's
        # administrative actions (no refill in a tick-only run), and the Staff's
        # premise reads `law_refusal` — "no admin action left" — as not offered.
        assert delivered == {7: "chancellors_letters#1", 12: "the_host#1", 17: "chancellors_letters#2",
                             22: "the_host#2"}

    def test_the_one_liner_speaks_the_affairs_phases_and_the_moments_as_before(self):
        from backend import campaign_log as CL
        base = {"type": "moment", "nation": "France", "title": "The Host's Claims", "register": "affair"}
        assert "an affair of state is laid before the Emperor" in CL.format_event_oneliner({**base, "phase": "arrived"})
        assert CL.format_event_oneliner({**base, "phase": "withdrawn", "line": "set aside"}) == "set aside"
        assert CL.format_event_oneliner({**base, "phase": "outcome", "line": "home whole"}) == "home whole"
        assert CL.format_event_oneliner({**base, "phase": "unknown"}) == "An affair of state: The Host's Claims"
        moment = {"type": "moment", "phase": "arrived", "nation": "France", "title": "The Bavarian Match"}
        assert CL.format_event_oneliner(moment) == "The Bavarian Match — a letter of the record is laid before the Emperor"
        assert CL.format_event_oneliner({**moment, "phase": "odd"}) == "A moment of history: The Bavarian Match"
        # no new log type: the affairs ride `moment` (the IQ-7 census owns the count pin)
        assert "moment" in CL.CAMPAIGN_LOG_TYPES and "affair" not in CL.CAMPAIGN_LOG_TYPES
        assert AF.RECEIPT_EVENT == MO.RECEIPT_EVENT == "moment_receipt"

    def test_err2_the_letters_office_is_the_secretariat(self, armed):
        assert MO.SECRETARIAT == "The Secretariat"
        assert MO.voice_of(armed, {"voice": {"speaker": "cabinet"}}) == "The Secretariat"
        assert MO.voice_of(armed, {"voice": {"speaker": "named", "name": ""}}) == "The Secretariat"
        assert MO.voice_of(armed, {"voice": {"speaker": "office", "name": "The Treasury"}}) == "The Treasury"
        # RE-2: the host speaks through its minister from the cast (Montgelas);
        # a court the cast does not name writes as its chancery.
        assert MO.voice_of(armed, {"voice": {"speaker": "host"}}, {"bind": {"host": "Bavaria"}}) == "Montgelas"
        assert MO.voice_of(armed, {"voice": {"speaker": "host"}}, {"bind": {"host": "Ruritania"}}) == "The Chancery of Ruritania"
        src = (BACKEND / "game_logic" / "moments.py").read_text(encoding="utf-8")
        assert '"The Cabinet"' not in src
        assert '"The Cabinet"' not in (BACKEND / "models" / "dialogue_manager.py").read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# The Watch and the trace
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWatchAndTheTrace:
    def test_the_watch_names_the_nearest_due_matters_and_says_may(self, armed):
        _quarter(armed, ("Ney", "Davout"))
        armed.nation_gold["France"] = 20_000
        _run(armed, [1, 2])
        lines = AF.watch(armed)
        assert lines == ["3 corps on Bavaria's soil: 2 of 3 mornings — its court may present its claims.",
                         "At war 2 of 4 turns, and the chest could found the headquarters — Berthier may write."]
        assert all("may" in line and "will" not in line for line in lines)
        assert AF.runtime(armed)["watched"] == {T2: 2, T3: 2}
        _afield(armed, authority=80)
        _run(armed, [3])
        assert len(AF.watch(armed)) == 2                      # at most two a morning

    def test_the_watch_is_silent_while_a_letter_stands(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))
        assert MO.status(armed, "the_host#1") == "fired"
        assert AF.watch(armed) == []

    def test_the_trace_reads_an_affairs_morning_and_judges_it_whole(self, armed):
        from tools._moments_trace import MomentsTrace
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        trace = MomentsTrace(lambda: armed).install()
        try:
            _run(armed, range(1, 8))
            with _quiet():
                MO.answer(armed, _letter(armed, "the_host#1"), "accept")
        finally:
            trace.uninstall()
        morning = trace.mornings[-1]
        assert morning["turn"] == 7 and morning["delivered"] == ["the_host#1"]
        assert morning["affairs"]["delivered"] == ["the_host#1"] and T2 in morning["affairs"]["true"]
        judged = trace.summary(armed)["judged"]
        assert judged["ceiling_breaches"] == [] and judged["floor_breaches"] == []
        assert judged["floors"]["the_host|Bavaria"]["verdict"] == "ok"
        assert judged["shown_equals_applied"] is True
        assert judged["answers"][-1]["moment"] == "the_host#1"

    def test_the_trace_subtracts_a_withdrawn_letter_from_the_open_count(self, armed, monkeypatch):
        from tools._moments_trace import MomentsTrace
        monkeypatch.setattr(AF, "LOOK_AHEAD", 0)
        _quarter(armed, ("Ney", "Davout"))
        trace = MomentsTrace(lambda: armed).install()
        try:
            _run(armed, range(1, 9))
        finally:
            trace.uninstall()
        morning = trace.mornings[-1]
        assert morning["turn"] == 8 and morning["open"] == 1 and morning["delivered"] == ["bavarian_match"]
        assert morning["affairs"]["withdrawn"] == ["the_host#1"]
        judged = trace.summary(armed)["judged"]
        assert judged["ceiling_breaches"] == []
        assert judged["floors"]["the_host|Bavaria"]["verdict"] == "ok"

    def test_a_due_affair_whose_premise_fell_is_released_not_silent(self, armed):
        from tools._moments_trace import MomentsTrace
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.war_intents = {"Prussia": {"coveter": "Prussia", "target": "Hanover",
                                         "opened_turn": 7, "foregrounded": True,
                                         "foregrounded_turn": 7}}
        trace = MomentsTrace(lambda: armed).install()
        try:
            _run(armed, range(1, 9))
            for name in ("Ney", "Davout"):
                armed.marshals[name].location = "Lorraine"
            _run(armed, [9, 10])
        finally:
            trace.uninstall()
        judged = trace.summary(armed)["judged"]
        assert judged["floors"]["the_host|Bavaria"]["verdict"] == "released"
        assert judged["floor_breaches"] == []
