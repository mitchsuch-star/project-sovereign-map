"""AU-2b "the lumps and the Show" — the pins (`docs/AUTHORITY_CURRENCY_SPEC.md`
§5.5, the §6 AU-2b row; the rules `SYSTEMS_REFERENCE.md` §171).

Standing comes back by play, never by waiting — each lump through
`standing.regrow` (the ceiling 95, a keyed cooldown in the tracker's `held`),
each parked for the courts: the Te Deum at a war's end (never a truce, once
per twelve turns, Le Moniteur's line), the Bulletin of the Field on a laurel
victory (a battle by `jealousy.is_laurel` and out-bled two to one — the
plan's reading of §4.1 reading 5) repaying the field's dents of the last ten
turns and never a price, the Return to the seat after eight turns away
repaying the Council's dents, the honour's payback seam (inert until AU-3a),
the Show's two Acts with their `ceiling`, the ceremonies' +2 on two dated
letters; and the seam AUS held down reproducing the tree before the slice.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def world():
    os.environ.setdefault("LLM_MODE", "mock")
    from backend.models.world_state import WorldState
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(world):
    w = copy.deepcopy(world)
    w.authority_tracker.authority = 80
    w.current_turn = 10
    return w


def _score(w, lord, court, value):
    key = w._make_diplo_key(lord, court)
    w.war_scores[key] = value if key.split("|")[0] == lord else -value
    return key


def _last(w):
    return w.authority_tracker.moves[-1]


# ═══════════════════════════════════════════════════════════════════════
# The Te Deum
# ═══════════════════════════════════════════════════════════════════════

class TestTheTeDeum:
    def test_a_war_won_sings_one_and_the_moniteur_prints_it(self, w):
        from backend.game_logic import diplomacy as D, gazette as G
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        key = _score(w, "France", "Austria", 30)
        with _quiet():
            D.cleanup_war_end(w, key)
        assert w.authority_tracker.authority == 84
        assert (_last(w)["key"], _last(w)["cause"]) == ("te_deum", "the Te Deum for the peace with Austria")
        events = [e for e in w.get_events_since_turn(0) if e.get("type") == "te_deum"]
        assert events and events[-1]["court"] == "Austria" and events[-1]["war_score"] == 30
        # §4.1 reading 4: the Moniteur's line stays generic; the books name the court
        assert format_event_oneliner(events[-1], player_nation="France", world=w) == \
            "PARIS — A Te Deum is sung at Notre-Dame for the peace"
        assert "te_deum" in CAMPAIGN_LOG_TYPES and "te_deum" in G._COURT_TYPES

    def test_a_truce_and_a_level_peace_sing_nothing(self, w):
        from backend.game_logic import diplomacy as D
        key = _score(w, "France", "Austria", 30)
        with _quiet():
            D.cleanup_war_end(w, key, conclude_objectives=False)
        assert w.authority_tracker.authority == 80
        key = _score(w, "France", "Russia", 24)
        with _quiet():
            D.cleanup_war_end(w, key)
        assert w.authority_tracker.authority == 80

    def test_a_three_pair_settlement_pays_once(self, w):
        from backend.game_logic import diplomacy as D
        for court in ("Austria", "Russia", "Britain"):
            key = _score(w, "France", court, 40)
            with _quiet():
                D.cleanup_war_end(w, key)
        assert w.authority_tracker.authority == 84
        assert [m["key"] for m in w.authority_tracker.moves].count("te_deum") == 1

    def test_the_twelve_turn_cooldown(self, w):
        from backend.game_logic import standing as ST
        assert ST.te_deum_on_peace(w, _score(w, "France", "Austria", 30)) == 4
        w.current_turn = 21
        assert ST.te_deum_on_peace(w, _score(w, "France", "Russia", 30)) == 0
        w.current_turn = 22
        assert ST.te_deum_on_peace(w, _score(w, "France", "Russia", 30)) == 4

    def test_a_court_sings_nothing(self, w):
        from backend.game_logic import standing as ST
        before = dict(w.nation_authority)
        assert ST.te_deum_on_peace(w, _score(w, "Austria", "Russia", 60)) == 0
        assert w.nation_authority == before


# ═══════════════════════════════════════════════════════════════════════
# The Bulletin of the Field
# ═══════════════════════════════════════════════════════════════════════

class TestTheBulletin:
    def test_a_laurel_is_a_battle_out_bled_two_to_one(self):
        from backend.game_logic import standing as ST
        assert ST.laurel_victory(3000, 8000) is True       # a battle, the enemy bled 2.7 to 1
        assert ST.laurel_victory(0, 2000) is True          # a flawless win
        assert ST.laurel_victory(5000, 6000) is False      # a battle, not a laurel
        assert ST.laurel_victory(100, 300) is False        # out-bled, but no battle (is_laurel's size)
        assert ST.laurel_victory(0, 0) is False

    def test_the_bulletin_repays_the_field_and_never_a_price(self, w):
        from backend.game_logic import standing as ST
        ST.move(w, "France", -5, "field_lost", battle="Ulm")
        ST.move(w, "France", -3, "letter_declined", letter="The Arch-Chancellor's Letters")
        ST.move(w, "France", -5, "own_hand_lost", battle="Elchingen")
        ST.move(w, "France", -3, "claims", marshal="Lannes")
        assert w.authority_tracker.authority == 64
        assert ST.bulletin(w, "France", "Austerlitz", 3000, 8000) == (4, 8)
        assert w.authority_tracker.authority == 76
        assert [m["key"] for m in w.authority_tracker.moves[-2:]] == ["bulletin", "bulletin_repaid"]
        paid = w.authority_tracker.held["bulletin_paid"]
        assert sorted(paid.values()) == [3, 5]                 # oldest first: Ulm's 5, then 3 of Elchingen's
        w.current_turn = 13
        assert ST.bulletin(w, "France", "Jena", 1000, 9000) == (4, 2)   # the rest of Elchingen, each point once
        w.current_turn = 16
        assert ST.bulletin(w, "France", "Eylau", 1000, 9000) == (4, 0)  # the letter and the claim never repaid

    def test_the_window_the_cooldown_and_the_ceiling(self, w):
        from backend.game_logic import standing as ST
        w.current_turn = 2
        ST.move(w, "France", -5, "field_lost", battle="Ulm")
        w.current_turn = 12
        assert ST.bulletin(w, "France", "Austerlitz", 3000, 8000) == (4, 0)   # ten turns on: out of the window
        w.current_turn = 14
        assert ST.bulletin(w, "France", "Austerlitz", 3000, 8000) == (0, 0)   # one per three turns
        w.authority_tracker.authority = 95
        w.current_turn = 20
        assert ST.bulletin(w, "France", "Austerlitz", 3000, 8000) == (0, 0)   # the ceiling
        assert ST.bulletin_line(0, 0, "Austerlitz") == ""
        assert ST.bulletin_line(4, 3, "Austerlitz") == (
            "\n\n[The Bulletin of the Grande Armée] The field at Austerlitz is read in every church in "
            "France. (Authority +4, and +3 of the field's dents repaid)")

    def test_the_pipeline_reads_it_on_the_throne_s_line_and_never_on_a_garrison(self):
        from backend.commands.executor import CommandExecutor
        from tests.test_r1_pipeline_enforcement import _make_basic_ctx, _setup_war_world
        world = _setup_war_world()
        world.authority_tracker.authority = 70
        out = CommandExecutor()._post_combat_pipeline(_make_basic_ctx(world), world)
        assert world.authority_tracker.authority == 74          # 3,000 against 8,000: a laurel, +4
        assert "[The Bulletin of the Grande Armée] The field at Belgium" in out.get("sovereign_prestige_msg", "")
        world = _setup_war_world()
        world.authority_tracker.authority = 70
        CommandExecutor()._post_combat_pipeline(_make_basic_ctx(world, is_garrison=True), world)
        assert world.authority_tracker.authority == 70


# ═══════════════════════════════════════════════════════════════════════
# The Return, the payback
# ═══════════════════════════════════════════════════════════════════════

class TestTheReturnAndThePayback:
    def test_eight_turns_away_then_the_seat_repays_the_council(self, w):
        from backend.game_logic import standing as ST
        nap = w.marshals["Napoleon"]
        ST.council_dent(w, "France", 8)
        nap.location = "Lorraine"
        assert ST.the_return(w, "France") == 0 and w.authority_tracker.held["away_since"] == 10
        w.current_turn = 15
        nap.location = "Paris"
        assert ST.the_return(w, "France") == 0                  # a short trip repays nothing
        assert "away_since" not in w.authority_tracker.held
        nap.location = "Lorraine"
        ST.the_return(w, "France")
        w.current_turn = 23
        nap.location = "Paris"
        assert ST.the_return(w, "France") == 5
        assert w.authority_tracker.held["council_owed"] == 3
        assert _last(w)["cause"] == "the Emperor's return to Paris, the Council's account settled"

    def test_the_chancellors_decline_books_the_council_s_dent_and_the_host_s_does_not(self, w):
        from backend.game_logic import affairs, moments as MO
        chancellor = affairs.template_by_id(w, "chancellors_letters")
        p = MO.plan(w, chancellor, MO.ANSWER_DECLINE)
        with _quiet():
            MO._apply(w, p)
        assert w.authority_tracker.held["council_owed"] == 5
        host = affairs.template_by_id(w, "the_host")
        p = MO.plan(w, host, MO.ANSWER_DECLINE,
                    {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1})
        with _quiet():
            MO._apply(w, p)
        assert w.authority_tracker.held["council_owed"] == 5

    def test_the_honour_pays_back_once_within_eight_turns(self, w):
        from backend.game_logic import standing as ST
        assert ST.honour_repaid(w, "France", "Ney") == 0         # inert until AU-3a writes the mark
        w.authority_tracker.held["honoured:Ney"] = 3
        assert ST.honour_repaid(w, "France", "Ney") == 2
        assert _last(w)["cause"] == "Ney honoured, and the field won"
        assert ST.honour_repaid(w, "France", "Ney") == 0
        w.authority_tracker.held["honoured:Davout"] = 1
        assert ST.honour_repaid(w, "France", "Davout") == 0      # expired, popped unpaid
        assert "honoured:Davout" not in w.authority_tracker.held


# ═══════════════════════════════════════════════════════════════════════
# The Show and the ceremonies
# ═══════════════════════════════════════════════════════════════════════

class TestTheShow:
    def test_the_two_acts_carry_their_ceiling_and_the_validator_reads_it(self):
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        acts = {a["id"]: a for a in data["imperial_designs"]["acts"]}
        assert (acts["feast_of_saint_napoleon"]["price"], acts["feast_of_saint_napoleon"]["effects"]) == (
            2500, [{"type": "authority", "amount": 5}])
        assert (acts["arc_de_triomphe"]["price"], acts["arc_de_triomphe"]["effects"]) == (
            5000, [{"type": "authority", "amount": 8}])
        assert all(acts[a]["ceiling"] == 95 and acts[a]["since"] == "AU-2b"
                   for a in ("feast_of_saint_napoleon", "arc_de_triomphe"))
        assert "ceiling" not in acts["temple_of_glory"]
        with _quiet():
            assert validate_scenario(data).is_valid
        bad = copy.deepcopy(data)
        bad["imperial_designs"]["acts"][4]["ceiling"] = 99
        bad["imperial_designs"]["acts"][5]["since"] = "AU-9"
        with _quiet():
            errors = [str(e) for e in validate_scenario(bad).errors]
        assert any("acts[4].ceiling" in e for e in errors) and any("acts[5].since" in e for e in errors)

    def test_the_quote_the_ceiling_the_refusal_and_the_temple(self, w):
        from backend.game_logic import imperial_designs as ID
        with _quiet():
            ID.proclaim(w, "rhine")
        w.nation_gold["France"] = 30000
        w.authority_tracker.authority = 90
        arc = ID.act(w, "arc_de_triomphe")
        assert ID.act_effect_lines(w, arc) == ["authority +5 — the ceiling 95 holds"]
        assert ID.act_refusal(w, "arc_de_triomphe", admin_actions=2) is None
        with _quiet():
            ID.decree(w, "arc_de_triomphe")
        assert w.authority_tracker.authority == 95
        assert _last(w)["cause"] == "the Act: The Arc de Triomphe"
        assert ID.act_refusal(w, "feast_of_saint_napoleon", admin_actions=2) == (
            "The Feast of Saint Napoleon adds nothing at authority 95: new gains stop at 95, Sire.")
        with _quiet():
            ID.decree(w, "temple_of_glory")
        assert w.authority_tracker.authority == 100              # the Temple alone reaches 100
        assert _last(w)["cause"] == "the Act: The Temple of Glory"      # AU-9: the title, never the id

    def test_the_design_reward_names_the_design(self, w):
        """AU-9: a design's reward is booked under its title, never its id."""
        from backend.game_logic import imperial_designs as ID
        design = next(d for r in ID._store(w)["block"]["roads"] for d in r.get("designs") or []
                      if (d.get("reward") or {}).get("type") == "authority")
        ID._pay_one_shot(w, design)
        assert _last(w)["cause"] == f"{design['title']} fulfilled"


class TestTheCeremonies:
    @pytest.mark.parametrize("authority, gain, said", [
        (80, 2, "Authority 80 → 82"),
        (94, 1, "the ceiling 95 holds: only 1 of the 2 is gained"),
        (95, 0, "Authority 95 → 95 — nothing is gained: the ceiling 95 holds"),
    ])
    def test_the_match_accepted_is_celebrated_up_to_the_ceiling(self, w, authority, gain, said):
        from backend.game_logic import moments as MO
        w.authority_tracker.authority = authority
        for mid in ("bavarian_match", "throne_of_holland"):
            p = MO.plan(w, MO.entry(w, mid), MO.ANSWER_ACCEPT)
            row = next(r for r in p["rows"] if r["op"] == "authority")
            assert (row["gain"], row["after"]) == (gain, authority + gain) and said in row["line"], (mid, row)
        p = MO.plan(w, MO.entry(w, "bavarian_match"), MO.ANSWER_ACCEPT)
        with _quiet():
            MO._apply(w, p)
        assert w.authority_tracker.authority == authority + gain
        if gain:
            assert (_last(w)["key"], _last(w)["cause"]) == ("ceremony", "The Bavarian Match celebrated")

    def test_the_validator_keeps_a_dated_letter_s_authority_a_gain_on_its_accept(self):
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        bad = copy.deepcopy(data)
        match = next(e for e in bad["moments"]["deck"] if e["id"] == "bavarian_match")
        match["accept"]["ops"][-1]["amount"] = 6
        match["decline"]["ops"].append({"op": "authority", "amount": -2})
        with _quiet():
            errors = [str(e) for e in validate_scenario(bad).errors]
        assert any("deck[0].accept.ops[5].amount" in e for e in errors), errors[:5]
        assert any("deck[0].decline" in e and "Accept alone" in e for e in errors), errors[:5]


# ═══════════════════════════════════════════════════════════════════════
# The seam AUS, the causes
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeamAndTheCauses:
    def test_held_down_the_tree_reads_as_before_au_2b(self, w, monkeypatch):
        from backend.game_logic import imperial_designs as ID, moments as MO, standing as ST
        monkeypatch.setattr(ST, "sources_armed", lambda *a, **k: False)
        assert ST.te_deum_on_peace(w, _score(w, "France", "Austria", 40)) == 0
        assert ST.bulletin(w, "France", "Austerlitz", 3000, 8000) == (0, 0)
        w.authority_tracker.held["honoured:Ney"] = 9
        assert ST.honour_repaid(w, "France", "Ney") == 0
        ST.council_dent(w, "France", 5)
        assert "council_owed" not in w.authority_tracker.held
        assert ST.the_return(w, "France") == 0 and "away_since" not in w.authority_tracker.held
        rows = MO.plan(w, MO.entry(w, "bavarian_match"), MO.ANSWER_ACCEPT)["rows"]
        assert "authority" not in [r["op"] for r in rows]
        assert [a["id"] for a in ID.acts(w)] == [
            "temple_of_glory", "princes_dotations", "abolition_of_feudalism", "raft_on_the_niemen"]

    def test_the_seam_is_a_named_function_on_the_rig(self):
        from backend.game_logic import standing as ST
        from tests._standing_seams import STANDING_SEAMS_BY_ROW
        assert ST.sources_armed() is True
        assert STANDING_SEAMS_BY_ROW["AUS"] == ["backend.game_logic.standing:sources_armed=False"]

    def test_the_six_new_causes_have_their_fields(self):
        from backend.display_names import AUTHORITY_CAUSES, authority_cause
        assert authority_cause("te_deum", court="Austria") == "the Te Deum for the peace with Austria"
        assert authority_cause("bulletin", battle="Austerlitz") == "the Bulletin of the field at Austerlitz"
        assert authority_cause("bulletin_repaid", battle="Jena") == "the field's dents repaid by the Bulletin of Jena"
        assert authority_cause("return", capital="Paris") == "the Emperor's return to Paris, the Council's account settled"
        assert authority_cause("honour_repaid", marshal="Ney") == "Ney honoured, and the field won"
        assert authority_cause("ceremony", letter="The Bavarian Match") == "The Bavarian Match celebrated"
        assert {"te_deum", "bulletin", "bulletin_repaid", "return", "honour_repaid", "ceremony"} <= set(AUTHORITY_CAUSES)
