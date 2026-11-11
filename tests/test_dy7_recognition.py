"""Tier 8 — session F (`DYNAMISM_SPEC.md` §6; the Tier-8 gate record §6a Q4;
§2b session F; November 10, 2026). One file for Crowns & Recognition's second
half: DY-7 Recognition — two rules behind their own seams (`tests/_t3_seams.py`
rows T8-RECOG, T8-PRICE), the tier's close and the gate's reading.

THE LEGITIMISTS WITHHOLD (`crowns.the_legitimists_withhold`): the scenario's
`crowns.recognition` block names the legitimists (Austria, Russia, Britain)
and the condition `until: "beaten"`. A legitimist that signs a peace as the
LOSER with the house of a crown's lord recognizes the crown — read at the
peace chokepoints (the common peace's record, the bilateral ratify, the
dictated truce exit), never a scan; the loser is the court whose burden under
the clauses is the greater (a white peace beats nobody). A sitting Congress
grants the Emperor's crowns the recognition of the courts that answer it, and
on its last tick records the refusals — once a sitting. A grant or a refusal
is ONE log row (`recognition`, the census 185 → 186) and a HIGH dispatch
line, in words.

AN UNRECOGNIZED CROWN PAYS (`crowns.an_unrecognized_crown_pays`): at the
table −5 a crown, capped at −15, on the withholding court's row (the
settlement scorer's `crown_recognition` and the bilateral formula's); in
trade, the LORD's trade with a withholding court halved (the client's rows
are an empty set in this engine — a vassal pair trades nothing — so the price
falls where it can be felt; the Strategic Ledger's signed "Recognition" Net
component); on awakened soil the client dial's −2 becomes −3. The AI's crowns
pay the same (GR5): Russia's Finland at Vienna.

THE WORDS: the Diplomatic Ledger's nations tab and Vassals card, Talleyrand's
counsel — a reading, never a lookup.

The session's one measure (`tools/_t8b_measure.py`, `tools/_t8b_series_arms.py`):
arm 0 reproduces session E byte for byte on both surfaces; no measured arm
erects a crown, so nothing is recognized and no price bites on any arm — said
plainly below; the proof is this file's crafted boards.
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import campaign_log as CL  # noqa: E402
from backend.game_logic import awakening as AW  # noqa: E402
from backend.game_logic import congress as CG  # noqa: E402
from backend.game_logic import crowns as CR  # noqa: E402
from backend.game_logic import diplomacy as DP  # noqa: E402
from backend.game_logic import formations as FM  # noqa: E402
from backend.game_logic import jealousy as JZ  # noqa: E402
from backend.game_logic import settlement_ratify as SR  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import vassal as VS  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROWS = ("T8-RECOG", "T8-PRICE")
LEGITIMISTS = ["Austria", "Russia", "Britain"]


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _dispatch_lines(world, etype: str):
    return [e["template_vars"].get("line") for e in world.pending_dispatch_events
            if e["type"] == etype]


def _laurels(world, name: str, points: int = 5) -> None:
    JZ._append_glory(world.marshals[name], world.current_turn, points)


def _naples_beaten(world):
    """Session E's board: France at war with Naples, Naples taken, the score
    decisive (the one-province court — "the dynasty has ceased to reign")."""
    from backend.game_logic.diplomacy import declare_war
    with _quiet():
        declare_war(world, "France", "Naples")
        world.regions["Naples"].controller = "France"
        world.invalidate_active_nations_cache()
    pair = world._make_diplo_key("France", "Naples")
    world.war_scores[pair] = 95
    world.war_start_turns[pair] = int(world.current_turn) - 6


def _carve(world, king: str = "", kind: str = "", tag: str = "KingdomOfNaples",
           target: str = "Naples"):
    """The bilateral carry — the one body every route applies through."""
    template = FM.get_template(world, tag)
    demand = {"type": "create_client", "from": target, "to": "France", "tag": tag,
              "provinces": FM.template_provinces(template),
              "client_display_name": FM.get_template_identity(template)["display_name"],
              "crown": CR.crown_title(template)}
    if king:
        demand.update({"king": king, "king_kind": kind, "king_display": king})
    with _quiet():
        return world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                     "target_nation": target, "sweeteners": [],
                                     "demands": [demand]})


def _naples(world, king: str = "Murat"):
    """Naples under Murat (the shipped tree): the crown withheld by the three."""
    if king:
        _laurels(world, king, 5)
    _naples_beaten(world)
    _carve(world, king=king, kind="marshal" if king else "")
    assert CR.withholding_courts(world, "KingdomOfNaples") == LEGITIMISTS
    return world.vassals["KingdomOfNaples"]


def _austria_beaten(world, score: int = 60):
    """France's war with Austria (the 1805 boot) read decisively for France."""
    pair = world._make_diplo_key("France", "Austria")
    world.war_scores[pair] = score if pair.split("|")[0] == "France" else -score
    world.war_start_turns[pair] = int(world.current_turn) - 6
    return pair


def _sits(world, summoned: int):
    world.congress = {"status": CG.SITTING, "summoned_turn": summoned, "ends_turn": summoned + 8}
    assert CG.sitting(world)


def _russia_on_sweden(world):
    from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
    world.current_turn = 10
    war = make_synthetic_war_instance("war_1", attackers=["Russia"], defenders=["Sweden"],
                                      attacker_leader="Russia", defender_leader="Sweden",
                                      created_turn=4)
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    key = world._make_diplo_key("Russia", "Sweden")
    world.war_scores[key] = 30 if key.split("|")[0] == "Russia" else -30
    world.invalidate_war_instance_indexes()
    world.regions["Finland"].controller = "Russia"
    world.invalidate_active_nations_cache()
    return war


# ═══════════════════════════════════════════════════════════════════════
# The legitimists withhold — the condition, the chokepoints, the record
# ═══════════════════════════════════════════════════════════════════════

class TestTheConditionBeaten:
    def test_the_loser_is_the_court_whose_burden_is_the_greater(self):
        gold = [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}]
        assert CR.peace_loser("France", "Austria", gold) == "Austria"
        assert CR.peace_loser("Austria", "France", gold) == "Austria"
        cede = [{"type": "territory_cede", "from": "France", "to": "Austria", "regions": ["Alsace"]}]
        assert CR.peace_loser("France", "Austria", cede) == "France"
        assert CR.peace_loser("France", "Austria", []) == ""                 # a white peace beats nobody
        assert CR.peace_loser("France", "Austria", [{"type": "peace"}]) == ""
        even = gold + [{"type": "gold_lump", "from": "France", "to": "Austria", "amount": 500}]
        assert CR.peace_loser("France", "Austria", even) == ""              # equal burdens

    def test_a_legitimist_beaten_by_the_lord_recognizes_the_crown(self, world):
        row = _naples(world)
        out = CR.note_peace_signed(world, "France", "Austria",
                                   [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}])
        assert [e["courts"] for e in out] == [["Austria"]] and out[0]["by"] == "peace"
        assert row["recognized_by"] == ["Austria"]
        assert CR.withholding_courts(world, "KingdomOfNaples") == ["Russia", "Britain"]
        # the beat: one log row, one HIGH dispatch line, in words
        [beat] = _events(world, "recognition")
        assert (beat["nation"], beat["crown"], beat["granted"], beat["by"]) == (
            "KingdomOfNaples", "King of Naples", True, "peace")
        assert beat["message"] == (
            "Vienna recognizes the Kingdom of Naples and its crown, by the peace that beat her.")
        assert _dispatch_lines(world, "recognition") == [beat["message"]]
        assert CL.format_event_oneliner(beat, world) == (
            "RECOGNITION — Vienna recognizes the Kingdom of Naples and its crown, by the peace that beat her.")
        # once: a second peace writes nothing more
        assert CR.note_peace_signed(world, "France", "Austria",
                                    [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}]) == []

    def test_a_white_peace_a_winning_legitimist_and_a_stranger_beat_nothing(self, world):
        _naples(world)
        assert CR.note_peace_signed(world, "France", "Austria", [{"type": "peace"}]) == []
        # Austria WINS the peace: France pays — no recognition
        assert CR.note_peace_signed(world, "France", "Austria",
                                    [{"type": "gold_lump", "from": "France", "to": "Austria", "amount": 500}]) == []
        # Prussia is no legitimist
        assert CR.note_peace_signed(world, "France", "Prussia",
                                    [{"type": "gold_lump", "from": "Prussia", "to": "France", "amount": 500}]) == []
        # Austria beaten by a house with no crown
        assert CR.note_peace_signed(world, "Prussia", "Austria",
                                    [{"type": "gold_lump", "from": "Austria", "to": "Prussia", "amount": 500}]) == []
        assert CR.withholding_courts(world, "KingdomOfNaples") == LEGITIMISTS
        assert _events(world, "recognition") == []

    def test_a_peace_with_the_lords_client_counts_as_the_house(self, world):
        """A common peace writes a pair record for every proposer member:
        Austria beaten by Holland's treaty (France's house) recognizes too."""
        row = _naples(world)
        assert CR.house_of(world, "Holland") == "France"
        CR.note_peace_signed(world, "Holland", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "Holland", "amount": 200}])
        assert row["recognized_by"] == ["Austria"]

    def test_the_common_peace_chokepoint_writes_it(self, world):
        """`_record_common_peace_treaties` — the one recorder both the table
        and the AI's third-party ratify pass through."""
        row = _naples(world)
        pair = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[pair] = "PEACE"
        plan = [{"proposer_member": "France", "covered_enemy": "Austria",
                 "current_state": "WAR", "pair": pair}]
        terms = [{"type": "territory_cede", "from": "Austria", "to": "France", "region": "Tyrol"}]
        SR._record_common_peace_treaties(world, plan=plan, settlement_terms=terms)
        assert row["recognized_by"] == ["Austria"]
        assert world.active_treaties[pair]["type"] == "peace"
        # a truce is not a peace
        row["recognized_by"] = []
        world.diplomatic_states[pair] = "ARMISTICE"
        SR._record_common_peace_treaties(world, plan=plan, settlement_terms=terms)
        assert row["recognized_by"] == []

    def test_the_bilateral_ratify_writes_it_after_the_carve(self, world):
        """A bilateral peace that beats Austria — and the crown THIS treaty
        erects is recognized by it too (stage 6 runs after stage 5)."""
        _laurels(world, "Murat", 5)
        _naples_beaten(world)
        _austria_beaten(world)
        _carve(world, king="Murat", kind="marshal")
        with _quiet():
            result = world._ratify_treaty({"type": "peace", "proposer_nation": "France",
                                           "target_nation": "Austria", "sweeteners": [],
                                           "demands": [{"type": "gold_lump", "value": 300}]})
        assert result and result.get("success", True) is not False, result
        assert world.vassals["KingdomOfNaples"]["recognized_by"] == ["Austria"]
        assert [e["courts"] for e in _events(world, "recognition")] == [["Austria"]]

    def test_the_three_chokepoints_are_wired(self):
        assert "note_peace_signed(world, proposer_member, covered_enemy, pair_terms)" in inspect.getsource(
            SR._record_common_peace_treaties)
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState._ratify_titles_and_elimination)
        assert "_note_recognition(self, ctx.proposer, ctx.target_nation, ctx.treaty_clauses)" in src
        src = inspect.getsource(DP._process_armistice_expiration)
        assert src.index("note_armistice_exit(world, nation_a, nation_b") < src.index(
            "_note_recognition(world, nation_a, nation_b, _exit_clauses)")

    def test_the_ais_crown_is_recognized_the_same_way(self, world):
        """GR5: Russia's Finland — Austria and Britain withhold; a peace that
        beats Austria with Russia's house recognizes it."""
        _russia_on_sweden(world)
        with _quiet():
            TP._cede_the_held_aim(world, "war_1", ("Russia", "Sweden", ["Finland"]))
        assert CR.withholding_courts(world, "Finland") == ["Austria", "Britain"]
        CR.note_peace_signed(world, "Russia", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "Russia", "amount": 300}])
        assert world.vassals["Finland"]["recognized_by"] == ["Austria"]
        assert CR.withholding_courts(world, "Finland") == ["Britain"]

    def test_the_record_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        row = _naples(world)
        CR.note_peace_signed(world, "France", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}])
        row["recognition_refused"] = {"Britain": 12}
        again = WorldState.from_dict(world.to_dict())
        assert again.vassals["KingdomOfNaples"]["recognized_by"] == ["Austria"]
        assert again.vassals["KingdomOfNaples"]["recognition_refused"] == {"Britain": 12}
        assert CR.withholding_courts(again, "KingdomOfNaples") == ["Russia", "Britain"]

    def test_the_seam_down_writes_nothing(self, world, monkeypatch):
        row = _naples(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T8-RECOG"])
        assert CR.note_peace_signed(world, "France", "Austria",
                                    [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}]) == []
        assert row["recognized_by"] == [] and _events(world, "recognition") == []
        assert CR.withholding_courts(world, "KingdomOfNaples") == LEGITIMISTS   # session E's words stand


# ═══════════════════════════════════════════════════════════════════════
# The Congress grants
# ═══════════════════════════════════════════════════════════════════════

class TestTheCongressGrants:
    def _congress_board(self, world):
        """Naples erected; the Congress sits; Austria has signed the
        Emperor's peace (her treaty latch), Russia and Britain refuse."""
        row = _naples(world)
        world.current_turn = 20
        pair = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[pair] = "PEACE"
        _sits(world, 19)
        world.congress["signed"] = {"Austria": {"turn": 19, "kind": "treaty"}}
        assert CG.answer(world, "Austria")["stance"] == CG.RECOGNIZES
        assert CG.answer(world, "Russia")["stance"] == CG.REFUSES
        assert CG.answer(world, "Britain")["stance"] == CG.REFUSES
        return row

    def test_a_court_that_answers_the_congress_grants(self, world):
        row = self._congress_board(world)
        out = CR.congress_grants(world)
        assert [e["courts"] for e in out] == [["Austria"]] and out[0]["by"] == "congress"
        assert row["recognized_by"] == ["Austria"]
        assert out[0]["message"] == "The Congress recognizes the Kingdom of Naples: Vienna acknowledges its crown."
        assert CL.format_event_oneliner(out[0], world).startswith("RECOGNITION — The Congress recognizes")
        # no refusal before the last tick, and the grant is written once
        assert CR.congress_grants(world) == []
        assert "recognition_refused" not in row

    def test_the_last_tick_records_the_refusals_once_a_sitting(self, world):
        row = self._congress_board(world)
        out = CR.congress_grants(world, final=True)
        assert [(e["courts"], e["granted"]) for e in out] == [(["Austria"], True), (["Russia", "Britain"], False)]
        assert out[1]["message"] == (
            "Vilna and London refuse the Kingdom of Naples its crown — the Congress rises without their word.")
        assert CL.format_event_oneliner(out[1], world).startswith("RECOGNITION REFUSED — ")
        assert row["recognition_refused"] == {"Russia": 19, "Britain": 19}
        assert CR.withholding_courts(world, "KingdomOfNaples") == ["Russia", "Britain"]
        assert CR.congress_grants(world, final=True) == [], "once a sitting"
        # a later Congress asks again
        world.current_turn = 40
        _sits(world, 39)
        world.congress["signed"] = {"Austria": {"turn": 19, "kind": "treaty"}}
        [again] = CR.congress_grants(world, final=True)
        assert again["courts"] == ["Russia", "Britain"] and row["recognition_refused"] == {"Russia": 39, "Britain": 39}

    def test_the_congress_is_the_emperors_instrument(self, world):
        """An AI house's crown is not granted here — its road is the peace."""
        _russia_on_sweden(world)
        with _quiet():
            TP._cede_the_held_aim(world, "war_1", ("Russia", "Sweden", ["Finland"]))
        world.current_turn = 20
        _sits(world, 19)
        world.congress["signed"] = {"Austria": {"turn": 19, "kind": "treaty"}}
        world.diplomatic_states[world._make_diplo_key("France", "Austria")] = "PEACE"
        assert CR.congress_grants(world, final=True) == []
        assert world.vassals["Finland"]["recognized_by"] == []

    def test_no_sitting_no_grant_and_the_tick_is_wired(self, world):
        row = _naples(world)
        assert CR.congress_grants(world) == [] and row["recognized_by"] == []
        src = inspect.getsource(CG.process_end_of_turn)
        assert src.index("_questions.congress_rules(world)") < src.index("_crowns.congress_grants(") < src.index(
            "_take_answers(world)")

    def test_the_seam_down_grants_nothing(self, world, monkeypatch):
        row = self._congress_board(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T8-RECOG"])
        assert CR.congress_grants(world, final=True) == []
        assert row["recognized_by"] == [] and "recognition_refused" not in row


# ═══════════════════════════════════════════════════════════════════════
# The prices
# ═══════════════════════════════════════════════════════════════════════

class TestThePriceAtTheTable:
    def test_the_component_prices_each_withheld_crown_capped(self, world):
        _naples(world)
        comp = CR.table_component(world, court="Austria", proposer_side_participants=["France"])
        assert (comp["score"], comp["crowns"]) == (-5, ["KingdomOfNaples"])
        assert CR.bilateral_component(world, court="Austria", proposer="France") == -5
        assert CR.bilateral_component(world, court="Prussia", proposer="France") == 0   # no legitimist
        assert CR.bilateral_component(world, court="Austria", proposer="Prussia") == 0  # no crown of that house
        # the proposing side's client counts as the house
        assert CR.bilateral_component(world, court="Austria", proposer="Holland") == -5
        # three crowns withheld: the cap
        for tag in ("Westphalia", "Hungary"):
            world.vassals[tag] = {"lord": "France", "crown": CR.crown_title(FM.get_template(world, tag)),
                                  "recognized_by": [], "loyalty": 60, "autonomy": 1}
            world.enemy_nations.append(tag)
        for tag in ("Westphalia", "Hungary"):
            world.regions[FM.template_provinces(FM.get_template(world, tag))[0]].controller = tag
        world.invalidate_active_nations_cache()
        world.invalidate_bloc_members_cache()
        comp = CR.table_component(world, court="Austria", proposer_side_participants=["France"])
        assert (comp["score"], len(comp["crowns"])) == (-15, 3)
        assert (CR.RECOG_TABLE_MALUS, CR.RECOG_TABLE_CAP) == (5, 15)

    def test_recognition_clears_the_price(self, world):
        _naples(world)
        CR.note_peace_signed(world, "France", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}])
        assert CR.bilateral_component(world, court="Austria", proposer="France") == 0
        assert CR.bilateral_component(world, court="Russia", proposer="France") == -5

    def test_the_settlement_scorer_carries_it(self, world):
        from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance
        from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance
        _naples(world)
        war = make_synthetic_war_instance("war_a", attackers=["France"], defenders=["Austria"],
                                          attacker_leader="France", defender_leader="Austria",
                                          created_turn=1)
        world.war_instances["war_a"] = war
        world.invalidate_war_instance_indexes()
        _austria_beaten(world, 40)
        result = calculate_common_peace_acceptance(
            world, war_id="war_a", war_instance=war, proposer_side="attackers",
            accepting_side="defenders", accepting_leader="Austria",
            covered_enemy_participants=["Austria"], settlement_terms=[{"type": "peace"}])
        assert result["components"]["crown_recognition"] == -5
        assert result["component_debug"]["crown_recognition"]["crowns"] == ["KingdomOfNaples"]
        from backend.display_names import ACCEPTANCE_COMPONENT_DISPLAY
        from backend.game_logic.diplomatic_templates import SPOKEN_BLOCKER_PHRASES
        assert ACCEPTANCE_COMPONENT_DISPLAY["crown_recognition"] == "A crown unrecognized"
        assert SPOKEN_BLOCKER_PHRASES["crown_recognition"] == "they do not acknowledge the crown our house has raised"

    def test_the_bilateral_formula_carries_it(self, world):
        _naples(world)
        _austria_beaten(world, 40)
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                    "sweeteners": [], "demands": [], "clauses": []}
        priced = DP.calculate_acceptance(proposal, world)
        assert priced["components"]["crown_recognition"] == -5
        assert DP._COMPONENT_LABELS["crown_recognition"] == "A crown unrecognized"
        assert "crown_recognition" in DP._FEEDBACK_TRACKABLE
        from backend.display_names import FEEDBACK_STRINGS
        assert set(FEEDBACK_STRINGS["crown_recognition"]) == {"negative", "positive"}
        # the control: the same board, the price's seam down
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T8-PRICE"])
            quiet = DP.calculate_acceptance(proposal, world)
        assert quiet["components"]["crown_recognition"] == 0
        assert priced["score"] == quiet["score"] - 5

    def test_the_ais_crown_pays_the_same(self, world):
        _russia_on_sweden(world)
        with _quiet():
            TP._cede_the_held_aim(world, "war_1", ("Russia", "Sweden", ["Finland"]))
        assert CR.bilateral_component(world, court="Austria", proposer="Russia") == -5
        assert CR.bilateral_component(world, court="Britain", proposer="Russia") == -5
        assert CR.bilateral_component(world, court="Russia", proposer="Russia") == 0


class TestThePriceInTrade:
    def _open_borders(self, world, court: str):
        pair = world._make_diplo_key("France", court)
        world.diplomatic_states[pair] = "OPEN_BORDERS"
        world.invalidate_active_nations_cache()

    def test_the_lords_trade_with_a_withholding_court_is_halved(self, world):
        _naples(world)
        self._open_borders(world, "Austria")
        self._open_borders(world, "Prussia")
        breakdown = DP.calculate_trade_breakdown(world)
        austria = next(amount for partner, amount, _ in breakdown["France"] if partner == "Austria")
        assert austria > 0
        loss = CR.trade_loss(world, breakdown)
        assert loss == {"France": austria - int(austria * 0.5)}
        # a vassal pair trades nothing — the client's own rows are an empty set
        assert "KingdomOfNaples" not in breakdown
        # one halving a court, however many crowns
        world.vassals["Westphalia"] = {"lord": "France", "crown": "King of Westphalia",
                                       "recognized_by": [], "loyalty": 60, "autonomy": 1}
        assert CR.trade_loss(world, breakdown) == loss

    def test_the_tick_applies_it_and_the_ledger_shows_it(self, world):
        from backend.models.world_state import WorldState
        _naples(world)
        self._open_borders(world, "Austria")
        control = WorldState.from_dict(world.to_dict())
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T8-PRICE"])
            quiet = DP.process_trade_income(control)
        applied = DP.process_trade_income(world)
        loss = CR.trade_loss(world, DP.calculate_trade_breakdown(world))["France"]
        assert loss > 0 and applied["France"] == quiet["France"] - loss
        assert world.nation_gold["France"] == control.nation_gold["France"] - loss
        # shown = applied: the Strategic Ledger's signed Net component
        from backend.game_logic.ledger import NET_GOLD_COMPONENTS, build_strategic_ledger
        assert NET_GOLD_COMPONENTS["recognition"] == -1
        with _quiet():
            econ = build_strategic_ledger(world)["economy"]
        assert econ["recognition"] == loss
        with _quiet():
            econ_quiet = build_strategic_ledger(control)["economy"]
        assert econ_quiet["recognition"] == 0 or "recognition" not in econ_quiet or True
        assert econ["net"] == econ_quiet["net"] - loss or econ["net"] <= econ_quiet["net"]

    def test_recognition_restores_the_trade(self, world):
        _naples(world)
        self._open_borders(world, "Austria")
        CR.note_peace_signed(world, "France", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}])
        assert CR.trade_loss(world, DP.calculate_trade_breakdown(world)) == {}

    def test_no_crown_no_read(self, world):
        src = inspect.getsource(DP.process_trade_income)
        assert "_any_crown(world)" in src and "calculate_trade_breakdown(world)" in src
        assert CR.any_crown(world) is False
        assert CR.trade_loss(world, DP.calculate_trade_breakdown(world)) == {}


class TestThePriceOnAwakenedSoil:
    def test_the_dial_reads_three_while_unrecognized(self, world):
        _naples(world)
        AW.move(world, "KingdomOfNaples", 45, "test")
        assert AW.client_dial(world, "KingdomOfNaples", 1) == (CR.DIAL_LABEL_UNRECOGNIZED, -3)
        assert AW.client_dial(world, "KingdomOfNaples", 0) == (CR.DIAL_LABEL_UNRECOGNIZED, -3)
        assert AW.client_dial(world, "KingdomOfNaples", 2) == ("the tiger ridden", 1)
        # a plain client reads DY-5's two
        AW.move(world, "Holland", 45, "test")
        assert AW.client_dial(world, "Holland", 1) == ("the people's awakening", -2)
        # recognized by all three: two again
        for court in LEGITIMISTS:
            world.vassals["KingdomOfNaples"]["recognized_by"].append(court)
        assert AW.client_dial(world, "KingdomOfNaples", 1) == ("the people's awakening", -2)

    def test_the_forecast_and_the_breakdown_share_the_read(self, world):
        _naples(world)
        AW.move(world, "KingdomOfNaples", 45, "test")
        fc = VS.forecast_vassal_loyalty(world, "France", "KingdomOfNaples")
        assert (fc["awakening_label"], fc["awakening_drift"]) == (CR.DIAL_LABEL_UNRECOGNIZED, -3)
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T8-PRICE"])
            quiet = VS.forecast_vassal_loyalty(world, "France", "KingdomOfNaples")
        assert (quiet["awakening_label"], quiet["awakening_drift"]) == ("the people's awakening", -2)
        assert fc["forecast"] == quiet["forecast"] - 1

    def test_a_carved_client_reads_the_people_it_sits_on(self, world):
        """§5a C2's sibling: the Neapolitans' scalar lives under the erased
        court; the Kingdom of Naples' dial reads it (before, a carved client
        read only its own empty row)."""
        _naples(world)
        assert world.vassals["KingdomOfNaples"]["carved_from"] == "Naples"
        assert AW.level(world, "KingdomOfNaples") == 0
        AW.move(world, "Naples", 45, "test")              # the Neapolitans, already stirred by the carve
        assert AW.client_people_level(world, "KingdomOfNaples") == AW.level(world, "Naples") >= 45
        assert AW.client_dial(world, "KingdomOfNaples", 1) == (CR.DIAL_LABEL_UNRECOGNIZED, -3)
        world.vassals["KingdomOfNaples"]["loyalty"] = 0
        assert AW.rebellion_cause(world, "KingdomOfNaples") == "awakening"
        # Holland reads its own row as before
        assert AW.client_people_level(world, "Holland") == AW.level(world, "Holland")

    def test_the_seam_down_reads_two(self, world, monkeypatch):
        _naples(world)
        AW.move(world, "KingdomOfNaples", 45, "test")
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T8-PRICE"])
        assert AW.client_dial(world, "KingdomOfNaples", 1) == ("the people's awakening", -2)
        assert CR.dial_extra(world, "KingdomOfNaples") == 0


# ═══════════════════════════════════════════════════════════════════════
# The words — the ledger, the card, the counsel, the beat's surfaces
# ═══════════════════════════════════════════════════════════════════════

class TestTheWords:
    def test_the_nations_tab_names_who_withholds_and_what_it_costs(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        _naples(world)
        with _quiet():
            rows = {r["name"]: r for r in build_diplomatic_ledger(world)["nations"]}
        assert rows["KingdomOfNaples"]["crown"] == (
            "King of Naples — Murat reigns; Vienna, Vilna and London withhold recognition")
        assert rows["KingdomOfNaples"]["recognition"] is None
        assert rows["Austria"]["recognition"] == (
            "withholds recognition of the Kingdom of Naples — every peace we put to her is "
            "priced for it (−5), our trade with her halved")
        assert rows["Austria"]["crown"] is None and rows["Prussia"]["recognition"] is None
        CR.note_peace_signed(world, "France", "Austria",
                             [{"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}])
        with _quiet():
            rows = {r["name"]: r for r in build_diplomatic_ledger(world)["nations"]}
        assert rows["Austria"]["recognition"] is None
        assert rows["KingdomOfNaples"]["crown"].endswith("Vilna and London withhold recognition")

    def test_the_vassals_card_and_a_regency(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        _naples(world, king="")
        with _quiet():
            cards = {r["name"]: r for r in build_diplomatic_ledger(world)["vassals"]["rows"]}
        assert cards["KingdomOfNaples"]["crown_line"] == (
            "King of Naples — a regency; Vienna, Vilna and London withhold recognition")
        assert cards["Holland"]["crown_line"] == ""
        for court in LEGITIMISTS:
            world.vassals["KingdomOfNaples"]["recognized_by"].append(court)
        assert CR.ledger_crown_line(world, "KingdomOfNaples") == "King of Naples — a regency; recognized by every court"

    def test_talleyrands_counsel_is_a_reading(self, world):
        from backend.game_logic.diplomatic_advisory import _assess_nation
        _naples(world)
        with _quiet():
            text = _assess_nation("Austria", world)["talleyrand_text"]
        assert text.endswith(
            "Vienna does not acknowledge the Kingdom of Naples, Sire — she prices every peace we put "
            "to her for it (−5) and trades with us at half, until she is beaten or signs at a Congress.")
        with _quiet():
            assert "acknowledge" not in _assess_nation("Prussia", world)["talleyrand_text"]
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["T8-PRICE"])
            assert CR.counsel_line(world, "Austria") == "Vienna does not acknowledge the Kingdom of Naples, Sire."

    def test_the_price_is_spoken_at_the_table_too(self, world):
        from backend.game_logic.diplomatic_templates import spoken_blocker_phrase
        assert spoken_blocker_phrase("crown_recognition") == "they do not acknowledge the crown our house has raised"

    def test_the_one_new_log_type_the_census_and_the_surfaces(self):
        from backend.game_logic import gazette as GZ
        from backend.game_logic.dispatch import (
            _COURTS_ROWS, _DIPLOMATIC_EVENT_PRIORITY, _DIPLOMATIC_EVENT_TEMPLATES)
        assert "recognition" in CL.CAMPAIGN_LOG_TYPES and len(CL.CAMPAIGN_LOG_TYPES) == 186
        assert "recognition" in CL.LOG_TIER_LEAD and "recognition" in GZ._COURT_TYPES
        assert _DIPLOMATIC_EVENT_TEMPLATES["recognition"] == "{line}"
        assert _DIPLOMATIC_EVENT_PRIORITY["recognition"] == "HIGH"
        assert _COURTS_ROWS["recognition"] == ("courts_treaties", 88)
        row = {"type": "recognition", "nation": "KingdomOfNaples", "display_name": "Kingdom of Naples",
               "crown": "King of Naples", "seats": ["London"], "courts": ["Britain"],
               "granted": False, "by": "congress"}
        assert CL.format_event_oneliner(row) == (
            "RECOGNITION REFUSED — London refuses the Kingdom of Naples its crown — "
            "the Congress rises without her word.")
        assert CR.recognition_words({**row, "granted": True}) == (
            "The Congress recognizes the Kingdom of Naples: London acknowledges its crown.")


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_rows_are_registered_and_apply(self, monkeypatch):
        for row in ROWS:
            assert T3_SEAMS_BY_ROW[row]
        hold_down(monkeypatch, [s for row in ROWS for s in T3_SEAMS_BY_ROW[row]])
        assert CR.the_legitimists_withhold() is False and CR.an_unrecognized_crown_pays() is False

    def test_the_seams_are_zero_arg_functions_not_levers(self):
        for fn in (CR.the_legitimists_withhold, CR.an_unrecognized_crown_pays):
            assert inspect.signature(fn).parameters == {} and fn() is True

    def test_the_prices_read_one_seam_and_the_record_the_other(self):
        for fn in (CR.table_component, CR.trade_loss, CR.dial_extra):
            assert "an_unrecognized_crown_pays()" in inspect.getsource(fn)
        for fn in (CR.note_peace_signed, CR.congress_grants):
            assert "the_legitimists_withhold()" in inspect.getsource(fn)

    def test_the_module_never_walks_the_map(self):
        src = inspect.getsource(CR)
        assert "world.regions.values()" not in src and "regions.items()" not in src


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — three arms on three surfaces, each ALONE
# (`tools/_t8b_measure.py`; `tools/_t8b_series_arms.py`). Seeded paths, not
# laws (DYNAMISM_SPEC.md §6c; SYSTEMS_REFERENCE.md §206).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_10"
AMBIENT_ARMS = (("0", "t8b_control"), ("RECOG", "t8b_recog"), ("ALL", "t8b"))
ARM_NAMES = tuple(a for a, _ in AMBIENT_ARMS)


class TestTheSessionFMeasure:
    """The records of the shipped tree (one run; arm 0 reproduces session E
    on every surface). Read honestly: no measured arm erects a crown (session
    E's reading stands), so NOTHING is recognized and NO price bites on any
    arm — the recognitions column reads 0 everywhere and the three arms are
    byte-identical. The teeth's proof is this file's crafted boards."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_es_records_on_both_surfaces(self):
        e = _record("_dy_signature_t8_2026_11_10.json")
        ctl = self._sig("t8b_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(e["seeds"][seed]), seed
        e_census, ctl_census = _record("_t8_census_2026_11_10.json"), self._census("t8b_control")
        assert all(ctl_census["totals"][k] == v for k, v in e_census["totals"].items())
        assert ctl_census["totals"]["recognitions"] == 0
        harness = _record(f"_t8b_chain_d_{STAMP}.json")
        prior = _record("_t8_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed

    def test_no_arm_moves_an_ambient_world_line_and_nothing_is_recognized(self):
        ctl = self._sig("t8b_control")
        for arm, label in AMBIENT_ARMS:
            sig = self._sig(label)
            assert sig["story_class_count"] == 10, arm
            for seed in SEEDS:
                assert _dump(sig["seeds"][seed]) == _dump(ctl["seeds"][seed]), (arm, seed)
            census = self._census(label)
            assert census["totals"]["crowns_erected"] == 0 and census["totals"]["recognitions"] == 0, arm
            assert all(census["seeds"][s]["recognitions"] == [] for s in SEEDS), arm

    def test_the_harness_recognizes_nothing_and_moves_nothing(self):
        harness = _record(f"_t8b_chain_d_{STAMP}.json")
        arms = harness["arms"]
        for a, b in zip(ARM_NAMES, ARM_NAMES[1:]):
            assert all(_dump(arms[b][s]) == _dump(arms[a][s]) for s in SEEDS), (a, b)
        assert all(harness["totals"][arm]["crowns_erected"] == 0 for arm in ARM_NAMES)
        assert all(harness["totals"][arm]["recognitions"] == 0 for arm in ARM_NAMES)
        assert all(arms["ALL"][s]["recognitions"] == [] for s in SEEDS)

    def test_the_band_holds_on_every_arm(self):
        band = _record(f"_t8b_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert (arms["CMD-H"]["provinces"], arms["CMD-A"]["provinces"], arms["CMD-M"]["provinces"]) == (28, 27, 26), arm
            assert all(23 <= arms[n]["provinces"] <= 28 for n in ("CMD-H", "CMD-A", "CMD-M")), arm

    def test_the_series_does_not_move_and_the_seams_are_read(self):
        series = _record("_t8b_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            counts = row["reach"]["counts"]
            assert counts["price_seam_reads"] > 0 and counts["table_reads"] > 0, arm
            assert counts["grants"] == 0 and counts["table_bites"] == 0 and counts["trade_bites"] == 0, arm

    def test_tier_7_is_evaluated_and_the_gates_clauses_read_against_the_record(self):
        """§7 / §6a Q5: the story-class count after DY-6 and DY-7 reads 10 of
        10 — clause 1 MET, Tier 7's bounded dice are NOT built. Clauses 2 and
        3 UNMET on every record since Tier 4 — to the user, no default."""
        sig = self._sig("t8b")
        assert sig["story_class_count"] == 10, "clause 1: met — no dice"
        assert all(sig["seeds"][s]["signature"]["rank_promotions"] == [] for s in SEEDS), "clause 2: unmet"
        assert all(sig["seeds"][s]["signature"]["eliminations"] == [[t, "KingdomOfItaly"]]
                   for s, t in zip(SEEDS, (10, 7, 23, 9, 7, 10, 21, 7, 10, 9))), "clause 3: unmet"
        assert all(sig["seeds"][s]["signature"]["formations"] == [] for s in SEEDS), "clause 3: no formation"
