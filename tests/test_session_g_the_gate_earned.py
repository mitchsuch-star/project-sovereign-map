"""Session G — the gate earned (`DYNAMISM_SPEC.md` §7a; the user's "Earn them
first", November 11, 2026). One file for the content session that follows
Tier 8: two rules behind their own seams (`tests/_t3_seams.py` rows G-PACT,
G-CHEST), the measure's reading of the deploy gate's clauses 2 and 3.

THE DIAGNOSIS (the records and four in-process probes of the ambient seeds):
the unattended board's France signs nothing for forty turns, so the Third
Coalition war never ends and every built road to a formation or a promotion
(the quiet window, the corridor, the gift, Austria's Milan) waits on a peace
the idle France never signs; Denmark, cast on austerlitz and lodi, reaches
`fight` but Sweden outgrows her (12,000 → 76,000 against 47,747) — the force
gate holds rightly. ONE defect stood in the only roads left: a court signed a
DEFENSIVE ALLIANCE with the very court whose province its live design covets
— the cast Naples with the Pope at turn 3 on jena and wagram, Hanover with
Hesse at turn 16 on marengo (one turn after Hesse's final demand) — and the
ally clause then read the want as "won"; the crisis passed. And the AI's
purse bar for a promotion law (3,000 + 1,000 reserve + five turns' upkeep =
4,500) sat beyond a minor's chest inside forty turns.

THE PACT WITH THE COVETED (`ai_diplomacy.no_pact_with_the_coveted`): no
defensive alliance or alliance between a coveter and the coveted — the poll's
gate (`_evaluate_ai_ai_proposal` over `_evaluate_ai_ai_triggers`) and the
recipient-addressed road's guard (`_resolve_ai_ai_proposal`), ONE read
(`pact_with_the_coveted`). A NAP is untouched.

A CROWN IS BOUGHT WITH THE WHOLE CHEST (`reforms.a_crown_is_bought_with_the_
whole_chest`): the AI's purse bar for a promotion law is the price and
arrears alone; every other law keeps the reserve; the Net test stands.

The session's one measure (`tools/_gate_measure.py`, `_gate_series_arms.py`):
arm 0 reproduces session F byte for byte; arm ALL reads the gate's clauses —
honestly, whichever way they fall (`TestTheSessionGMeasure`).
"""
from __future__ import annotations

import contextlib
import inspect
import io
import json
import random
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import agendas as AG  # noqa: E402
from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import reforms as RF  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
ROWS = ("G-PACT", "G-CHEST")


def _world(seed: str = "historical"):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed=seed)


@pytest.fixture()
def world():
    return _world("historical")


@pytest.fixture()
def jena():
    """The seed that casts Naples: `roman_expedition` at her deck's head."""
    return _world("jena")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _state(world, a: str, b: str) -> str:
    return str(world.get_diplomatic_state(a, b))


def _set_relation(world, a: str, b: str, value: int) -> None:
    world.nation_relations[world._make_diplo_key(a, b)] = int(value)


def _run_turns(world, turns: int) -> None:
    """The series runner's in-process loop (`_emit_series`): the enemy
    phase and the AI–AI poll run inside `end_turn`."""
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    with _quiet():
        for turn in range(turns):
            random.seed(10_000 + turn)
            tm.end_turn(game_state)


# ═══════════════════════════════════════════════════════════════════════
# The pact with the coveted
# ═══════════════════════════════════════════════════════════════════════

class TestThePactWithTheCoveted:
    def test_the_read_names_the_coveter_in_either_order(self, jena, world):
        assert AG.get_active_agenda("Naples", jena).id == "roman_expedition"
        assert AD.pact_with_the_coveted(jena, "Naples", "PapalStates") == "Naples"
        assert AD.pact_with_the_coveted(jena, "PapalStates", "Naples") == "Naples"
        assert AD.pact_with_the_coveted(jena, "Naples", "Ottoman") == ""
        # Hesse's Westphalian Duchy is live at boot on every seed
        assert AD.pact_with_the_coveted(world, "Hanover", "Hesse") == "Hesse"
        assert AD.pact_with_the_coveted(world, "Hesse", "Hanover") == "Hesse"
        # Prussia covets Hanover's province, not Sweden's
        assert AD.pact_with_the_coveted(world, "Prussia", "Sweden") == ""
        assert AD.pact_with_the_coveted(world, "Prussia", "Hanover") == "Prussia"
        # the coveted province's HOUSE: a client's soil is its lord's
        assert AD.pact_with_the_coveted(world, "Austria", "KingdomOfItaly") == "Austria"
        assert AD.pact_with_the_coveted(world, "Naples", "Naples") == ""

    def test_the_poll_never_proposes_a_pact_to_the_coveted(self, jena):
        """Trigger 5's board (both cold to France, no pacts, the threat up):
        a defensive alliance would follow — the gate returns None; the same
        board with the seam down proposes it."""
        jena.threat_level = 60
        for court in ("Naples", "PapalStates"):
            _set_relation(jena, "France", court, -20)
        _set_relation(jena, "Naples", "PapalStates", 20)
        assert AD._evaluate_ai_ai_triggers("Naples", "PapalStates", jena) == {
            "type": "defensive_alliance", "proposer": "Naples", "target": "PapalStates"}
        assert AD._evaluate_ai_ai_proposal("Naples", "PapalStates", jena) is None
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G-PACT"])
            assert AD._evaluate_ai_ai_proposal("Naples", "PapalStates", jena) == {
                "type": "defensive_alliance", "proposer": "Naples", "target": "PapalStates"}
        # a pair that covets nothing passes through untouched
        assert AD._evaluate_ai_ai_proposal("Naples", "Ottoman", jena) == \
            AD._evaluate_ai_ai_triggers("Naples", "Ottoman", jena)

    def test_the_upgrade_ladder_stops_below_a_pact(self, world):
        """Trigger 3 upgrades a warm pair one step; between Hesse and Hanover
        the design ask (trigger 0a) leads and passes through, the step
        NON_AGGRESSION → DEFENSIVE ALLIANCE is the pact and stops — and the
        gate touches only the pact types."""
        world.threat_level = 0
        _set_relation(world, "Hesse", "Hanover", 60)
        for court in ("Hesse", "Hanover"):
            _set_relation(world, "France", court, 10)
        key = world._make_diplo_key("Hesse", "Hanover")
        world.diplomatic_states[key] = "NON_AGGRESSION"
        raw = AD._evaluate_ai_ai_triggers("Hesse", "Hanover", world)
        assert raw["type"] in ("design_ask", "defensive_alliance")
        gated = AD._evaluate_ai_ai_proposal("Hesse", "Hanover", world)
        if raw["type"] == "defensive_alliance":
            assert gated is None
        else:
            assert gated == raw
        # the pact step itself, isolated: the triggers' own answer at the
        # NAP rung is the defensive alliance; the gate returns None for it
        with pytest.MonkeyPatch.context() as m:
            m.setattr(AD, "_evaluate_ai_ai_triggers",
                      lambda a, b, w: {"type": "defensive_alliance", "proposer": a, "target": b})
            assert AD._evaluate_ai_ai_proposal("Hesse", "Hanover", world) is None
            assert AD._evaluate_ai_ai_proposal("Hesse", "Ottoman", world) == {
                "type": "defensive_alliance", "proposer": "Hesse", "target": "Ottoman"}
            m.setattr(AD, "_evaluate_ai_ai_triggers",
                      lambda a, b, w: {"type": "non_aggression", "proposer": a, "target": b})
            assert AD._evaluate_ai_ai_proposal("Hesse", "Hanover", world)["type"] == "non_aggression"

    def test_the_road_refuses_with_its_reason(self, jena):
        proposal = {"type": "defensive_alliance", "proposer": "PapalStates", "target": "Naples"}
        event = AD._resolve_ai_ai_proposal(proposal, jena)
        assert event["type"] == "ai_ai_proposal_refused"
        assert (event["refused_by"], event["reason"], event["covetous"]) == ("Naples", "covets", "Naples")
        assert [e for e in jena.event_log if e.get("type") == "ai_ai_proposal_refused"
                and e.get("reason") == "covets"]
        assert _state(jena, "Naples", "PapalStates") not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
        # a NAP is no pact — the road keeps it
        nap = AD._resolve_ai_ai_proposal(
            {"type": "non_aggression", "proposer": "PapalStates", "target": "Naples"}, jena)
        assert nap is None or nap.get("reason") != "covets"

    def test_on_jenas_board_the_understudy_keeps_her_ambition(self):
        """The probe's board: four turns of the unattended jena seed. With the
        rule Naples' Roman Expedition stays at her deck's head and no pact
        with the Pope stands; with the seam down the pact signs at turn 3 and
        the September Treaty resurfaces — the defect as measured."""
        with_rule = _world("jena")
        _run_turns(with_rule, 4)
        assert AG.get_active_agenda("Naples", with_rule).id == "roman_expedition"
        assert _state(with_rule, "Naples", "PapalStates") not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
        assert not [e for e in with_rule.event_log if e.get("type") == "diplomatic_ai_ai_treaty"
                    and {e.get("nation_a"), e.get("nation_b")} == {"Naples", "PapalStates"}]
        control = _world("jena")
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G-PACT"])
            _run_turns(control, 4)
        assert _state(control, "Naples", "PapalStates") == "DEFENSIVE_ALLIANCE"
        assert AG.get_active_agenda("Naples", control).id == "september_treaty"

    def test_the_seam_down_reads_nothing(self, jena, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G-PACT"])
        assert AD.pact_with_the_coveted(jena, "Naples", "PapalStates") == ""
        proposal = {"type": "defensive_alliance", "proposer": "PapalStates", "target": "Naples"}
        event = AD._resolve_ai_ai_proposal(proposal, jena)
        assert event is None or event.get("reason") != "covets"


# ═══════════════════════════════════════════════════════════════════════
# A crown is bought with the whole chest
# ═══════════════════════════════════════════════════════════════════════

class TestTheCrownBoughtWithTheWholeChest:
    def test_a_promotion_laws_bar_is_its_price(self, world):
        row = RF.find_law(world, "Hesse", "the_grand_ducal_title")
        assert RF.is_promotion(row) and int(row["price"]) == 3000 and int(row["upkeep"]) == 100
        assert RF._purse_bar(world, "Hesse", row) == 3000
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G-CHEST"])
            assert RF._purse_bar(world, "Hesse", row) == 3000 + RF.AI_PURSE_RESERVE + RF.AI_PURSE_UPKEEP_TURNS * 100
        assert (RF.AI_PURSE_RESERVE, RF.AI_PURSE_UPKEEP_TURNS) == (1000, 5)
        for court, law_id in (("Bavaria", "the_royal_crown"), ("Saxony", "the_royal_dignity"),
                              ("Denmark", "both_shores_of_the_sound"), ("Sardinia", "the_mainland_restored")):
            crown = RF.find_law(world, court, law_id)
            assert RF.is_promotion(crown) and RF._purse_bar(world, court, crown) == int(crown["price"])

    def test_every_other_law_keeps_the_reserve(self, world):
        staff = next(r for r in RF.deck(world, "Prussia") if not RF.is_promotion(r)
                     and str(r.get("currency") or "gold") == "gold")
        quote = RF.restoration_price(world, "Prussia", staff)
        expected = (int(quote["price"]) + int(quote["arrears"]) + RF.AI_PURSE_RESERVE
                    + RF.AI_PURSE_UPKEEP_TURNS * (RF.law_upkeep_bill(world, "Prussia") + int(staff.get("upkeep", 0) or 0)))
        assert RF._purse_bar(world, "Prussia", staff) == expected
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G-CHEST"])
            assert RF._purse_bar(world, "Prussia", staff) == expected

    def test_the_refusal_reads_the_bar_and_the_grounds_still_bind(self, world):
        """The purse half of `ai_purse_refusal` reads the new bar; the
        grounds (six quiet turns on Westphalia) still refuse the law."""
        row = RF.find_law(world, "Hesse", "the_grand_ducal_title")
        world.nation_gold["Hesse"] = 3200
        assert "under the bar" not in RF.ai_purse_refusal(world, "Hesse", row)
        world.nation_gold["Hesse"] = 2900
        assert "under the bar (3000)" in RF.ai_purse_refusal(world, "Hesse", row)
        assert RF.law_refusal(world, "Hesse", "the_grand_ducal_title", admin_actions=1)


# ═══════════════════════════════════════════════════════════════════════
# The seams
# ═══════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_rows_are_registered_and_apply(self, monkeypatch):
        for row in ROWS:
            assert T3_SEAMS_BY_ROW[row]
        hold_down(monkeypatch, [s for row in ROWS for s in T3_SEAMS_BY_ROW[row]])
        assert AD.no_pact_with_the_coveted() is False
        assert RF.a_crown_is_bought_with_the_whole_chest() is False

    def test_the_seams_are_zero_arg_functions_not_levers(self):
        for fn in (AD.no_pact_with_the_coveted, RF.a_crown_is_bought_with_the_whole_chest):
            assert inspect.signature(fn).parameters == {} and fn() is True

    def test_the_one_read_sits_at_both_sites(self):
        assert "pact_with_the_coveted(world, nation_a, nation_b)" in inspect.getsource(AD._evaluate_ai_ai_proposal)
        assert "pact_with_the_coveted(world, initiator, target)" in inspect.getsource(AD._resolve_ai_ai_proposal)
        assert "is_promotion(row)" in inspect.getsource(RF._purse_bar)
        assert "no_pact_with_the_coveted()" in inspect.getsource(AD.pact_with_the_coveted)


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — three arms on three surfaces, each ALONE
# (`tools/_gate_measure.py`; `tools/_gate_series_arms.py`). Seeded paths,
# not laws (DYNAMISM_SPEC.md §7a; SYSTEMS_REFERENCE.md §207).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_11"
AMBIENT_ARMS = (("0", "gate_control"), ("PACT", "gate_pact"), ("ALL", "gate"))
ARM_NAMES = tuple(a for a, _ in AMBIENT_ARMS)


class TestTheSessionGMeasure:
    """Written from the records after the sweep ran ALONE. Arm 0 reproduces
    session F; the clauses are read off arm ALL exactly as they fell."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_fs_records_on_both_surfaces(self):
        f = _record("_dy_signature_t8b_2026_11_10.json")
        ctl = self._sig("gate_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(f["seeds"][seed]), seed
        f_census, ctl_census = _record("_t8b_census_2026_11_10.json"), self._census("gate_control")
        assert all(ctl_census["totals"][k] == v for k, v in f_census["totals"].items())
        harness = _record(f"_gate_chain_d_{STAMP}.json")
        prior = _record("_t8b_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed

    def test_the_band_holds_on_every_arm(self):
        band = _record(f"_gate_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert all(23 <= arms[n]["provinces"] <= 28 for n in ("CMD-H", "CMD-A", "CMD-M")), arm

    def test_the_series_does_not_move_and_the_seams_are_read(self):
        series = _record("_gate_series_arms_final.json")
        for arm in ARM_NAMES:
            row = series["arms"][arm]
            assert row["first_divergence_vs_prior"] is None, arm
            counts = row["reach"]["counts"]
            assert counts["pact_seam_reads"] > 6000 and counts["chest_seam_reads"] == 303, arm
            assert counts["crown_bar_reads"] == 0, arm      # no promotion law reaches the bar on the rig
        assert series["arms"]["0"]["reach"]["counts"]["pact_bites"] == 0
        assert series["arms"]["PACT"]["reach"]["counts"]["pact_bites"] == 105   # the rig's pacts refused, the series unmoved
        assert series["arms"]["ALL"]["reach"]["counts"]["pact_bites"] == 105

    UNMOVED = ("austerlitz", "eylau", "friedland", "historical", "rivoli", "ulm")
    MOVED = ("jena", "lodi", "marengo", "wagram")

    def test_the_pact_rule_alone_moves_four_seeds_and_earns_both_clauses(self):
        """Arm PACT: six seeds byte-identical to session F; on lodi Hesse takes
        Westphalia (turn 25), Hanover signs the aim peace (26) and the Grand
        Ducal Title is enacted at 33 — clause 2; on wagram the cast Naples
        asks the Pope thrice, opens her crisis at 27, declares at 29, storms
        Rome and the Papal States are erased at 31 — clause 3; on marengo
        Hesse holds Westphalia from 25 but her chest is under the 4,500 bar
        inside forty turns; on jena Naples stands at `fight` from turn 8 and
        Austria takes the Pope under her wing by a pact at 23 (Austria covets
        none of his soil) — the deterrence the design means."""
        ctl, pact = self._sig("gate_control"), self._sig("gate_pact")
        assert pact["story_class_count"] == 10
        for seed in self.UNMOVED:
            assert _dump(pact["seeds"][seed]) == _dump(ctl["seeds"][seed]), seed
        for seed in self.MOVED:
            assert _dump(pact["seeds"][seed]) != _dump(ctl["seeds"][seed]), seed
        sig = {seed: pact["seeds"][seed]["signature"] for seed in SEEDS}
        assert {seed: sig[seed]["rank_promotions"] for seed in SEEDS if sig[seed]["rank_promotions"]} == {
            "lodi": [[33, "Hesse"]]}
        assert sig["wagram"]["eliminations"] == [[9, "KingdomOfItaly"], [31, "PapalStates"]]
        assert all(sig[seed]["eliminations"] == [[t, "KingdomOfItaly"]] for seed, t in zip(
            ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi", "marengo", "rivoli", "ulm"),
            (10, 7, 23, 9, 7, 10, 21, 7, 10)))
        assert sig["wagram"]["war_turns"] == [11, 11, 29, 33] and sig["lodi"]["war_turns"] == [12, 12, 23, 25]
        census = self._census("gate_pact")
        assert census["seeds"]["lodi"]["rank_promotions"] == [
            {"court": "Hesse", "grounds": ["Westphalia"], "law": "the_grand_ducal_title", "turn": 33}]
        assert census["seeds"]["marengo"]["rank_promotions"] == []

    def test_the_whole_chest_buys_marengos_crown_and_the_gate_reads_met(self):
        """Arm ALL (the shipped tree): clause 1 — 10 of 10; clause 2 — Hesse
        at secondary rank on lodi (33) AND marengo (40, the chest rule's own
        seed: Hanover's indemnity there was 243 gold, not lodi's 2,250);
        clause 3 — the roster reads {Kingdom of Italy} on nine seeds and
        {Kingdom of Italy, Papal States} on wagram, two distinct readings."""
        ctl, pact, done = self._sig("gate_control"), self._sig("gate_pact"), self._sig("gate")
        assert done["story_class_count"] == 10, "clause 1: met"
        for seed in self.UNMOVED:
            assert _dump(done["seeds"][seed]) == _dump(ctl["seeds"][seed]), seed
        for seed in ("jena", "lodi", "wagram"):
            assert _dump(done["seeds"][seed]) == _dump(pact["seeds"][seed]), seed
        sig = {seed: done["seeds"][seed]["signature"] for seed in SEEDS}
        assert {seed: sig[seed]["rank_promotions"] for seed in SEEDS if sig[seed]["rank_promotions"]} == {
            "lodi": [[33, "Hesse"]], "marengo": [[40, "Hesse"]]}, "clause 2: met on two seeds"
        rosters = {(tuple(sorted(n for _, n in sig[seed]["eliminations"])), tuple(sig[seed]["formations"]))
                   for seed in SEEDS}
        assert rosters == {(("KingdomOfItaly",), ()), (("KingdomOfItaly", "PapalStates"), ())}, "clause 3: met"
        census = self._census("gate")
        assert census["seeds"]["marengo"]["rank_promotions"] == [
            {"court": "Hesse", "grounds": ["Westphalia"], "law": "the_grand_ducal_title", "turn": 40}]
        assert [c for c in census["seeds"]["marengo"]["signed_cessions"] if c["accepter"] == "Hesse"][0][
            "consequence"].startswith("Hesse takes Westphalia. Hanover pays 243 gold.")
        assert [c for c in census["seeds"]["lodi"]["signed_cessions"] if c["accepter"] == "Hesse"][0][
            "consequence"].startswith("Hesse takes Westphalia. Hanover pays 2,250 gold.")
        assert census["totals"]["crowns_erected"] == 0 and census["totals"]["recognitions"] == 0
        assert census["totals"]["annexations_outside_aim"] == 0
        assert census["totals"]["captures_outside_aim"] == 269        # 251 on arm 0: the understudies' wars

    def test_the_band_moves_one_province_on_the_commanded_middle_arm(self):
        band = _record(f"_gate_band_{STAMP}.json")
        arms = {arm: tuple(band["arms"][arm][n]["provinces"] for n in ("CMD-H", "CMD-A", "CMD-M")) for arm in ARM_NAMES}
        assert arms == {"0": (28, 27, 26), "PACT": (28, 27, 25), "ALL": (28, 27, 25)}

    def test_the_harness_moves_six_seeds_and_promotes_nobody(self):
        """Chain D (the AI-run France): the pact rule moves six seeds (the
        understudies' wars run there too; `captures_outside_aim` 117 → 130),
        no court is promoted and no crown rises — reported, never gated."""
        harness = _record(f"_gate_chain_d_{STAMP}.json")
        arms = harness["arms"]
        moved = [s for s in SEEDS if _dump(arms["PACT"][s]) != _dump(arms["0"][s])]
        assert moved == ["friedland", "historical", "jena", "lodi", "marengo", "wagram"]
        assert all(_dump(arms["ALL"][s]) == _dump(arms["PACT"][s]) for s in SEEDS)
        assert (harness["totals"]["0"]["captures_outside_aim"], harness["totals"]["ALL"]["captures_outside_aim"]) == (117, 130)
        assert all(harness["totals"][arm]["rank_promotions"] == 0 and harness["totals"][arm]["crowns_erected"] == 0
                   for arm in ARM_NAMES)
