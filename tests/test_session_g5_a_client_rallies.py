"""Session G5 — a client rallies against the house (DYNAMISM_SPEC.md §7e;
November 11, 2026).

The user's word, at session G4's close: "do what you deem best then tell me
what next". Of the readings session G4 left with him, ONE was changed:
reading (d), the neutral client. Session G4 closed the treaty fuzzer's I2 by
keeping a client at peace with the aggressor's lord OUT of her own lord's
defence. Played on the real road that reads badly: Britain buys Holland, she
marches on France, the Emperor's allies fight her — and his own two clients
stand by, because neither had fought Britain. A turncoat with a foreign
patron was safer than a plain rebel.

The fault was the HALF war, not the rally. Where her lord already fights
the aggressor's house, the client takes up his war with it — her pair with
the house on HIS war instance, beside him — and then marches on its client
as before. Where her lord is at peace with that house she still stays out.
An ally's policy is its own and is untouched.
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import agendas as AG  # noqa: E402
from backend.game_logic import diplomacy as DI  # noqa: E402
from backend.game_logic import game_end as GE  # noqa: E402
from backend.game_logic import vassal as V  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from backend.game_logic.settlement_helpers import (  # noqa: E402
    _find_active_war_instance_for_pair,
)
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402
from tests.test_session_g4_the_open_readings import (  # noqa: E402
    _flush, _quiet, _saxony_under_britain, _set_state, _state, _world,
)
from tools.treaty_fuzzer import RecordingStates, check_invariants  # noqa: E402

ROW = "G5-RALLY"


@pytest.fixture()
def world():
    return _world("historical")


def _bought(world, court: str, buyer: str = "Britain") -> str:
    """The bribe's transfer road, as `vassal.attempt_vassal_bribe` walks it:
    the buyer and the bought make peace, the client changes lords, and — its
    new lord at war with its old — takes the field against him."""
    lord = world.vassals[court]["lord"]
    with _quiet():
        if _state(world, buyer, court) in ("WAR", "ARMISTICE"):
            DI.set_diplomatic_state(world, buyer, court, "PEACE", "coalition_defection")
            DI.cleanup_war_end(world, world._make_diplo_key(buyer, court),
                               conclude_objectives=True)
        assert V.transfer_vassal(world, court, buyer, reason="coalition_defection")["success"]
        return V._client_takes_the_field(world, court, lord, buyer, [],
                                         exit_old_wars=False, fallback_peace=False)


def _side(world, a: str, b: str, court: str) -> str:
    war_id = _find_active_war_instance_for_pair(world, world._make_diplo_key(a, b))
    return str(((world.war_instances.get(war_id) or {}).get("side_by_nation") or {}).get(court))


def _fuzzer_reads(world, start: int = 0) -> list:
    return [row for row in check_invariants(world, start)
            if row["cls"].startswith(("I1", "I2"))]


# ══════════════════════════════════════════════════════════════════════════
# The rule
# ══════════════════════════════════════════════════════════════════════════

class TestAClientRalliesAgainstTheHouse:
    def test_the_boot_facts_the_rule_stands_on(self, world):
        """Each of the Emperor's clients boots on its own front: Holland
        against Britain, the Kingdom of Italy against Austria, Switzerland
        against nobody."""
        assert _state(world, "France", "Britain") == "WAR"
        assert _state(world, "Holland", "Britain") == "WAR"
        assert _state(world, "KingdomOfItaly", "Britain") == "PEACE"
        assert _state(world, "KingdomOfItaly", "Austria") == "WAR"
        assert _state(world, "Switzerland", "Britain") == "PEACE"

    def test_a_bought_client_is_marched_on_by_the_clients_it_left(self, world):
        world.diplomatic_states = RecordingStates(world.diplomatic_states)
        start = len(world.diplomatic_states.log)
        assert _bought(world, "Holland") == "war"
        assert _state(world, "Holland", "France") == "WAR"
        for client in ("KingdomOfItaly", "Switzerland"):
            assert _state(world, client, "Holland") == "WAR", client
            assert _state(world, client, "Britain") == "WAR", client
        assert _fuzzer_reads(world, start) == []

    def test_she_takes_up_her_lords_war_beside_him(self, world):
        """Her pair with the house sits on the LORD's war with it, on his
        side; her pair with its client on the client's own war."""
        _bought(world, "Holland")
        lords_war = _find_active_war_instance_for_pair(
            world, world._make_diplo_key("France", "Britain"))
        for client in ("KingdomOfItaly", "Switzerland"):
            assert _find_active_war_instance_for_pair(
                world, world._make_diplo_key(client, "Britain")) == lords_war
            assert (_side(world, client, "Britain", client)
                    == _side(world, "France", "Britain", "France"))
            assert (_side(world, client, "Holland", client)
                    == _side(world, "France", "Holland", "France"))

    def test_neutral_switzerland_goes_over_and_the_rest_rally(self, world):
        world.diplomatic_states = RecordingStates(world.diplomatic_states)
        start = len(world.diplomatic_states.log)
        assert _bought(world, "Switzerland") == "war"
        assert _state(world, "KingdomOfItaly", "Switzerland") == "WAR"
        assert _state(world, "KingdomOfItaly", "Britain") == "WAR"
        assert _state(world, "Holland", "Switzerland") == "WAR"      # she fought Britain already
        assert _fuzzer_reads(world, start) == []

    def test_the_declared_war_road_too(self, world):
        """Session G4's crafted board: a client of Britain declares on France."""
        _saxony_under_britain(world)
        with _quiet():
            assert DI.declare_war(world, "Saxony", "France")["success"] is True
        for client in ("KingdomOfItaly", "Switzerland", "Holland"):
            assert _state(world, client, "Saxony") == "WAR", client
            assert _state(world, client, "Britain") == "WAR", client

    def test_the_way_out_is_her_lords_peace(self, world):
        """The wars she took up end where her lord's does: the offer surface
        already counts them among the clients that follow him out."""
        _bought(world, "Holland")
        pairs = {tuple(sorted(p)) for p in
                 DI.client_pairs_that_follow(world, "France", "Britain", "PEACE")}
        assert {("Britain", "KingdomOfItaly"), ("Britain", "Switzerland"),
                ("Holland", "KingdomOfItaly"), ("Holland", "Switzerland"),
                ("France", "Holland")} <= pairs
        line = DI.clients_following_line(world, "France", "Britain", "PEACE", "France")
        assert line == ("Our clients follow us out of the war: Kingdom of Italy, Switzerland. "
                        "Their clients follow them: Holland.")

    def test_the_words_say_both_wars(self, world):
        _saxony_under_britain(world)
        with _quiet():
            result = DI.declare_war(world, "Saxony", "France")
        text = " ".join(str(m) for m in (result.get("messages") or [result.get("message", "")]))
        rows = [e for e in world.event_log
                if e.get("type") == "vassal_auto_join_war" and e.get("vassal") == "Switzerland"]
        assert {e.get("against") for e in rows} == {"Britain", "Saxony"}
        assert all(e.get("lord") == "France" for e in rows)
        assert "§" not in text


class TestWhereSheStillStaysOut:
    def test_the_seam_down_is_session_g4(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW[ROW])
        assert _bought(world, "Holland") == "war"
        for client in ("KingdomOfItaly", "Switzerland"):
            assert _state(world, client, "Holland") == "PEACE", client
            assert _state(world, client, "Britain") == "PEACE", client

    def test_her_lord_at_peace_with_the_house_she_fights_no_half_war(self, world):
        """The aggressor answers to Prussia, and the Emperor is at peace
        with Prussia: nothing of his to take up."""
        world.vassals["Saxony"] = dict(world.vassals["Holland"], lord="Prussia")
        _set_state(world, "Prussia", "Saxony", "VASSAL")
        _flush(world)
        assert _state(world, "France", "Prussia") != "WAR"
        assert DI.client_keeps_its_peace_with_the_house(world, "Switzerland", "Saxony") is True
        cascade: list = []
        calls: list = []
        joined = DI._rally_against_the_house(
            world, "Switzerland", "France", "Saxony",
            lambda *a: calls.append(a) or {"ok": True}, cascade)
        assert joined is False and cascade == [] and calls == []
        assert _state(world, "Switzerland", "Prussia") != "WAR"

    def test_the_war_record_refusing_the_pair_keeps_her_out(self, world, monkeypatch):
        _saxony_under_britain(world)
        monkeypatch.setattr(DI, "attach_pair_to_war_instance",
                            lambda *a, **k: {"ok": False, "error": "refused"})
        cascade: list = []
        joined = DI._rally_against_the_house(
            world, "Switzerland", "France", "Saxony", lambda *a: {"ok": False}, cascade)
        assert joined is False and cascade == []
        assert _state(world, "Switzerland", "Britain") == "PEACE"

    def test_a_board_without_war_records_uses_the_cascades_own_writer(self, world, monkeypatch):
        _saxony_under_britain(world)
        import backend.game_logic.settlement_helpers as SH
        monkeypatch.setattr(SH, "_find_active_war_instance_for_pair", lambda *a, **k: None)
        calls: list = []
        cascade: list = []
        with _quiet():
            joined = DI._rally_against_the_house(
                world, "Switzerland", "France", "Saxony",
                lambda *a: calls.append(a) or {"ok": True, "war_id": ""}, cascade)
        assert joined is True
        assert calls == [("Britain", "Switzerland", "vassal_defensive_auto_join")]
        assert _state(world, "Switzerland", "Britain") == "WAR"
        assert cascade == [{"vassal": "Switzerland", "lord": "France", "target": "Britain",
                            "cascade_type": "vassal_defensive_auto_join"}]

    def test_a_client_already_in_the_lords_war_is_untouched(self, world):
        """Holland fights Britain from the boot: the read never reaches the
        rally, and she marches on the client as she always did."""
        _saxony_under_britain(world)
        assert DI.client_keeps_its_peace_with_the_house(world, "Holland", "Saxony") is False

    def test_an_allys_policy_is_its_own(self, world):
        """Bavaria is the Emperor's ally, at war with Austria and at peace
        with Britain. She answers the alliance against the client that
        attacked him and keeps her peace with its lord — the rule is a
        client's, whose foreign policy is its lord's (session G3). The
        fuzzer reads the board clean: the bought client leads its own war."""
        world.diplomatic_states = RecordingStates(world.diplomatic_states)
        start = len(world.diplomatic_states.log)
        assert _state(world, "France", "Bavaria") == "ALLIANCE"
        _bought(world, "Holland")
        assert _state(world, "Bavaria", "Holland") == "WAR"
        assert _state(world, "Bavaria", "Britain") == "PEACE"
        assert _fuzzer_reads(world, start) == []


# ══════════════════════════════════════════════════════════════════════════
# The gate's read — found by the sweep: a court under the knife keeps its
# authored aims in the annexation count
# ══════════════════════════════════════════════════════════════════════════

def _holds_by_conquest(world, court: str, region: str, since: int) -> None:
    former = world.regions[region].controller
    world.regions[region].controller = court
    GE.record_province_title(world, region, GE.TITLE_CONQUEST, former, court)
    world.province_title[region]["since"] = int(since)
    _flush(world)


def _under_the_knife(world, court: str, taker: str = "France") -> None:
    """Most of the court's homeland in another's hands, its seat still its own."""
    seat = world.get_nation_capital(court)
    home = [r for r in world.nation_starting_regions[court] if r != seat]
    for region in home[: len(home) // 2 + 2]:
        world.regions[region].controller = taker
    _flush(world)
    assert world.regions[seat].controller == court
    assert AG.survival_override_active(world, court) is True


class TestTheGateReadsTheAuthoredAims:
    """On marengo with the clients rallying Austria ended the forty turns
    with two of her seven homeland provinces — and the gate's read called
    Milan and Piedmont, taken twenty turns earlier in her war with France,
    "annexations outside aim". Both stand in her authored Italian design."""

    def test_the_boot_facts(self, world):
        assert {"Milan", "Piedmont"} <= WC._house_aims(world, "Austria")
        assert "Bern" not in WC._house_aims(world, "Austria")
        assert AG.survival_override_active(world, "Austria") is False

    def test_a_court_under_the_knife_keeps_its_authored_aims_in_the_count(self, world):
        world.current_turn = 30
        _holds_by_conquest(world, "Austria", "Milan", since=10)
        assert GE.holds_by_title(world, "Milan", "Austria") is True
        assert WC.annexations_outside_aim(world) == {}
        _under_the_knife(world, "Austria")
        assert WC._house_aims(world, "Austria") == set()                 # no voice
        assert "Milan" in WC._house_aims(world, "Austria", authored=True)
        assert WC.annexations_outside_aim(world) == {}

    def test_the_seam_down_is_the_read_that_miscounted(self, world, monkeypatch):
        world.current_turn = 30
        _holds_by_conquest(world, "Austria", "Milan", since=10)
        _under_the_knife(world, "Austria")
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G5-AIMS"])
        assert WC.annexations_outside_aim(world) == {"Austria": ["Milan"]}

    def test_sprawl_is_still_counted_under_the_knife(self, world):
        """The read forgives nothing off the deck: Bern is in no Austrian design."""
        world.current_turn = 30
        _holds_by_conquest(world, "Austria", "Bern", since=10)
        _holds_by_conquest(world, "Austria", "Milan", since=10)
        _under_the_knife(world, "Austria")
        assert WC.annexations_outside_aim(world) == {"Austria": ["Bern"]}

    def test_a_court_with_its_voice_reads_the_same_either_way(self, world, monkeypatch):
        world.current_turn = 30
        _holds_by_conquest(world, "Austria", "Bern", since=10)
        _holds_by_conquest(world, "Austria", "Milan", since=10)
        up = WC.annexations_outside_aim(world)
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G5-AIMS"])
        assert WC.annexations_outside_aim(world) == up == {"Austria": ["Bern"]}

    def test_the_terms_keep_the_voice(self, world):
        """What a holder may KEEP at a peace still reads the design voice: a
        court fighting for its life keeps only what it declared."""
        assert "Milan" in WC.keepable_regions(world, "Austria", "KingdomOfItaly")
        _under_the_knife(world, "Austria")
        assert "Milan" not in WC.keepable_regions(world, "Austria", "KingdomOfItaly")
        assert AG.acquire_design_regions(world, "Austria") == []
        assert any("Milan" in design
                   for design in AG.acquire_design_regions(world, "Austria", authored=True))

    def test_no_rule_of_play_reads_the_count(self):
        """The read is the instrument's (`tools/ai_v_sweep.py`'s final
        capture): nothing under `backend/` calls it, so the seam moves no
        world — the measured world-lines are the rally's alone."""
        callers = []
        for path in (REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "annexations_outside_aim(" in text:
                callers.append((path.name, text.count("annexations_outside_aim(")))
        assert callers == [("war_council.py", 1)]


class TestTheSeam:
    def test_the_rule_has_its_row_and_ships_up(self):
        seam = DI.a_client_rallies_against_the_house
        assert seam() is True and inspect.signature(seam).parameters == {}
        assert T3_SEAMS_BY_ROW[ROW] == [f"{seam.__module__}:{seam.__name__}=False"]

    def test_the_gates_read_has_its_row_and_ships_up(self):
        seam = WC.the_gate_reads_the_authored_aims
        assert seam() is True and inspect.signature(seam).parameters == {}
        assert T3_SEAMS_BY_ROW["G5-AIMS"] == [f"{seam.__module__}:{seam.__name__}=False"]
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW["G5-AIMS"])
            assert WC.the_gate_reads_the_authored_aims() is False

    def test_the_row_joins_the_recorded_boards_hold_list(self):
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert T3_SEAMS_BY_ROW[ROW][0] in OCT27_SEAMS_DOWN
        assert T3_SEAMS_BY_ROW["G5-AIMS"][0] in OCT27_SEAMS_DOWN

    def test_the_row_holds_its_own_seam_down(self):
        with pytest.MonkeyPatch.context() as m:
            hold_down(m, T3_SEAMS_BY_ROW[ROW])
            assert DI.a_client_rallies_against_the_house() is False
        assert DI.a_client_rallies_against_the_house() is True

    def test_session_g4s_seam_down_is_still_session_g3(self, world, monkeypatch):
        """The two seams nest: with session G4's down the client joins the
        half war as session G3's tree did, whatever this one reads."""
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["G4-HOUSE"])
        _bought(world, "Holland")
        assert _state(world, "KingdomOfItaly", "Holland") == "WAR"
        assert _state(world, "KingdomOfItaly", "Britain") == "PEACE"

    def test_the_fuzzers_ledger_is_still_empty(self):
        ledger = json.loads((REPO / "tests" / "data" / "treaty_fuzzer_known_violations.json")
                            .read_text(encoding="utf-8"))
        assert ledger == {}


# ══════════════════════════════════════════════════════════════════════════
# The session's measure — ONE sweep, three arms, three surfaces, the series
# (`tools/_g5_measure.py`, `tools/_g5_series_arms.py`). Seeded paths, not
# laws (DYNAMISM_SPEC.md §7e; SYSTEMS_REFERENCE.md §211).
# ══════════════════════════════════════════════════════════════════════════

SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_11"
ARM_NAMES = ("0", "RALLY", "ALL")
LABELS = {"0": "g5_control", "RALLY": "g5_rally", "ALL": "g5"}


def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


class TestTheSessionG5Measure:
    """Written from the records after the sweep ran ALONE on the final
    tree. Arm 0 reproduces session G4's shipped arm; arm RALLY adds the
    rule; arm ALL adds the gate's corrected read — the shipped tree."""

    def _sig(self, arm: str) -> dict:
        return _record(f"_dy_signature_{LABELS[arm]}_{STAMP}.json")

    def _census(self, arm: str) -> dict:
        return _record(f"_{LABELS[arm]}_census_{STAMP}.json")

    def _harness(self) -> dict:
        return _record(f"_g5_chain_d_{STAMP}.json")

    def test_arm_0_reproduces_session_g4_on_both_surfaces(self):
        g4, ctl = _record(f"_dy_signature_g4_{STAMP}.json"), self._sig("0")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(g4["seeds"][seed]), seed
        assert _dump(self._census("0")["seeds"]) == _dump(_record(f"_g4_census_{STAMP}.json")["seeds"])
        prior = _record(f"_g4_chain_d_{STAMP}.json")["arms"]["ALL"]
        assert _dump(self._harness()["arms"]["0"]) == _dump(prior)

    def test_the_rally_moves_six_unattended_seeds(self):
        ctl, rally = self._sig("0"), self._sig("RALLY")
        assert [s for s in SEEDS if _dump(rally["seeds"][s]) != _dump(ctl["seeds"][s])] == [
            "eylau", "friedland", "historical", "jena", "marengo", "rivoli"]

    def test_the_gates_read_moves_one_number_and_no_world(self):
        """Arm RALLY to arm ALL: marengo's annexation count alone — the same
        world-line, read by the corrected instrument."""
        rally, shipped = self._sig("RALLY"), self._sig("ALL")
        moved = [s for s in SEEDS if _dump(shipped["seeds"][s]) != _dump(rally["seeds"][s])]
        assert moved == ["marengo"]
        a, b = rally["seeds"]["marengo"], shipped["seeds"]["marengo"]
        assert _dump(a["story_class"]) == _dump(b["story_class"])
        assert [k for k in a["signature"] if _dump(a["signature"][k]) != _dump(b["signature"][k])] == [
            "annexations_outside_aim"]
        by_court = {arm: self._census(arm)["seeds"]["marengo"]["annexations_outside_aim_by_court"]
                    for arm in ARM_NAMES}
        assert by_court == {"0": {}, "RALLY": {"Austria": ["Milan", "Piedmont"]}, "ALL": {}}
        harness = self._harness()["arms"]
        assert _dump(harness["ALL"]) == _dump(harness["RALLY"])

    def test_the_gate_reads_met_on_the_shipped_arm(self):
        shipped, census = self._sig("ALL"), self._census("ALL")
        assert shipped["story_class_count"] == 10
        promoted = {s: shipped["seeds"][s]["signature"]["rank_promotions"] for s in SEEDS
                    if shipped["seeds"][s]["signature"]["rank_promotions"]}
        assert promoted == {"lodi": [[33, "Hesse"]], "marengo": [[39, "Hesse"]]}
        rosters = {s: tuple(n for _, n in shipped["seeds"][s]["signature"]["eliminations"]) for s in SEEDS}
        assert sorted(s for s, r in rosters.items() if r == ("KingdomOfItaly", "PapalStates")) == ["jena", "wagram"]
        assert all(r == ("KingdomOfItaly",) for s, r in rosters.items() if s not in ("jena", "wagram"))
        assert census["totals"]["annexations_outside_aim"] == 0
        assert (census["totals"]["captures_outside_aim"], census["totals"]["rank_promotions"]) == (290, 2)

    def test_the_promotion_check_rests_on_two_seeds_again(self):
        """Session G4 left the clause on lodi alone; the rally's world-line
        brings Hesse's Grand Ducal Title back on marengo, a turn earlier
        than session G3 read it (39 for 40)."""
        counts = {arm: {s: self._sig(arm)["seeds"][s]["signature"]["rank_promotions"] for s in SEEDS
                        if self._sig(arm)["seeds"][s]["signature"]["rank_promotions"]}
                  for arm in ("0", "ALL")}
        assert counts["0"] == {"lodi": [[33, "Hesse"]]}
        assert sorted(counts["ALL"]) == ["lodi", "marengo"]

    def test_friedlands_kingdom_falls_again(self):
        """The cost, reported: the Kingdom of Italy, which sat out Britain's
        bought Swiss on session G4's tree and lived, rallies and is erased
        at 23 — the roster of fallen courts reads two ways, not three."""
        fell = {arm: self._sig(arm)["seeds"]["friedland"]["signature"]["eliminations"]
                for arm in ("0", "ALL")}
        assert fell == {"0": [], "ALL": [[23, "KingdomOfItaly"]]}

    def test_the_band_does_not_move(self):
        band = _record(f"_g5_band_{STAMP}.json")
        for arm in ARM_NAMES:
            arms = band["arms"][arm]
            assert [arms[n]["provinces"] for n in ("CMD-H", "CMD-A", "CMD-M")] == [26, 26, 25], arm

    def test_the_harness_moves_lodi_alone(self):
        """On the AI-France harness's lodi Holland is called against the
        bought Swiss again: she does not drift and rise at 32, and France
        ends at 46 provinces, not 38."""
        mine = self._harness()
        moved = [s for s in SEEDS if _dump(mine["arms"]["ALL"][s]) != _dump(mine["arms"]["0"][s])]
        assert moved == ["lodi"]
        final = {a: mine["arms"][a]["lodi"]["france_provinces_final"] for a in ("0", "ALL")}
        assert final == {"0": 38, "ALL": 46}
        assert (mine["arms"]["0"]["lodi"]["formations"], mine["arms"]["ALL"]["lodi"]["formations"]) == (
            ["Holland"], [])
        for arm in ARM_NAMES:
            totals = mine["totals"][arm]
            assert totals["annexations_outside_aim"] == 0, arm
            assert (totals["rank_promotions"], totals["crowns_erected"], totals["recognitions"]) == (0, 0, 0), arm
        assert [mine["totals"][a]["captures_outside_aim"] for a in ARM_NAMES] == [140, 135, 135]

    def test_the_series_does_not_move_and_the_rule_bites_on_the_rig(self):
        record = _record("_g5_series_arms_final.json")
        for arm in ("0", "RALLY"):
            assert record["arms"][arm]["first_divergence_vs_prior"] is None, arm
            assert record["arms"][arm]["series"] == record["prior"], arm
        assert record["arms"]["0"]["reach"]["counts"] == {
            "rally_seam_reads": 1, "house_occasions": 1, "rally_bites": 0}
        assert record["arms"]["RALLY"]["reach"]["counts"] == {
            "rally_seam_reads": 1, "house_occasions": 1, "rally_bites": 1}
