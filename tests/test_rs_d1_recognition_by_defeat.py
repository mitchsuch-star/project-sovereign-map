"""RS-D1 "Recognition by defeat" — Score Finish Step 1 "The peace holds"
(September 29, 2026). Gate record: docs/SCORE_FINISH_SPEC.md §6.1 (RULED
September 28, 2026, items 1–8); landing record §3 Step 1; rules
SYSTEMS_REFERENCE.md §81.

The ruling: a SIGNED peace that leaves a great power's capital held by
France or her vassal chain latches its recognition at the Congress of
Paris (`kind: "capital"`), and the latch breaks when the capital leaves the
bloc. Its riders: the scorer reads a retained capital as a capital LOST
(recognition costs a defeat, not a white peace); every courtship lever
quotes its cost in turns; the SUES projection and the war-arm price name
the road; the review and the ratification summary say what the signature
buys.

Every pin drives the real seams — `_ratify_treaty`, the settlement table's
staging and ratification, `congress.answer`/`price`, the per-turn tick —
and reads the answer back; nothing here pins a source string.
"""

import contextlib
import copy
import io
import json
import math
import re
from pathlib import Path

import pytest

from backend.game_logic import congress, game_end
from backend.game_logic import settlement_scoring as SS
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")
T24 = (REPO / "docs" / "audits" / "playtest_digests" / "rs0928-hand-played"
       / "retest_t24_summonable.json")

# The AAR's turn-9 shape (test_sr1a): France holds the four Austrian
# provinces by conquest, the war still on, nothing signed.
THE_FOUR = ("Vienna", "Bohemia", "Moravia", "Tyrol")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _boot() -> WorldState:
    with _quiet():
        return WorldState.from_scenario(SCEN)


def _hold(world, region, holder, taken_from, kind=game_end.TITLE_CONQUEST):
    world.regions[region].controller = holder
    game_end.record_province_title(world, region, kind, taken_from, holder)
    world.invalidate_active_nations_cache()


def _ratify(world, proposer, target, ptype="peace", demands=None):
    with _quiet():
        return world._ratify_treaty({
            "proposer_nation": proposer, "target_nation": target,
            "type": ptype, "sweeteners": [], "demands": list(demands or [])})


def _signed(world, court):
    return ((congress.record(world) or {}).get("signed") or {}).get(court)


def _stage_titles(w, need=None):
    """Title France up to `need` provinces by treaty, minors only."""
    need = congress.hold_titled(w) if need is None else need
    for nation in ("Hanover", "Denmark", "Portugal", "Sardinia", "Naples",
                   "Saxony", "Hesse"):
        for region in sorted(w.get_nation_regions(nation)):
            if congress.titled(w)["count"] >= need:
                return
            if region == "Lisbon":
                continue
            _hold(w, region, "France", nation, kind=game_end.TITLE_TREATY)


def _sit(w):
    _stage_titles(w)
    w.diplomatic_points = 6
    with _quiet():
        result = congress.summon(w)
    assert result["success"], result["message"]
    return result


def _tick(w, n=1):
    with _quiet():
        for _ in range(n):
            w.current_turn += 1
            game_end.process_end_of_turn(w, turn_ended=w.current_turn - 1)


@pytest.fixture
def vienna_road():
    w = _boot()
    for region in THE_FOUR:
        _hold(w, region, "France", "Austria")
    return w


# ════════════════════════════════════════════════════════════════════════
# 1. The latch
# ════════════════════════════════════════════════════════════════════════

class TestTheCapitalLatch:

    def test_a_white_peace_that_leaves_vienna_in_our_hands_latches(self, vienna_road):
        """Item 1: the bilateral ratifier. A white peace that cedes nothing
        by clause used to write no latch at all (the retest's two Austrian
        peaces); it now latches by the capital, with the capital named."""
        w = vienna_road
        _ratify(w, "Austria", "France")
        rec = _signed(w, "Austria")
        assert rec == {"turn": w.current_turn, "broken": None,
                       "kind": "capital", "capital": "Vienna"}
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.RECOGNIZES and row["by"] == "treaty"
        assert row["reason"] == (
            "it signed the peace that left Vienna in our hands (turn 1)")

    def test_the_settlement_table_latches_by_the_same_read(self, vienna_road, monkeypatch):
        """Item 1: the whole-war table. The scorer is patched at its stable
        seam so the package carries; the latch is the ratifier's own."""
        from backend.game_logic.settlement_ratify import ratify_settlement_confirm
        w = vienna_road
        real = SS.calculate_common_peace_acceptance

        def carries(*args, **kwargs):
            out = real(*args, **kwargs)
            out = dict(out)
            out["score"] = 100
            out["verdict"] = "accept"
            return out

        monkeypatch.setattr(SS, "calculate_common_peace_acceptance", carries)
        with _quiet():
            staged = stage_settlement_confirm(
                w, war_id="war_1", settlement_terms=[{"type": "peace"}],
                covered_enemy_participants=["Austria"])
        assert staged["success"], staged
        dialogue = w.pending_diplomatic_dialogue
        assert "Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty." in dialogue["message"]
        assert dialogue["recognition_note"].startswith("Recognition: Austria")
        with _quiet():
            result = ratify_settlement_confirm(w, dialogue)
        assert result["success"], result
        assert _signed(w, "Austria")["kind"] == "capital"
        assert "Vienna stays ours by this treaty" in result["message"]

    def test_a_vassals_held_capital_latches_and_an_allys_does_not(self, vienna_road):
        """Item 2: the bloc is France and her vassal chain — never an ally.
        The Kingdom of Italy is a French client; Spain is an ally."""
        w = vienna_road
        w.regions["Vienna"].controller = "KingdomOfItaly"
        w.invalidate_active_nations_cache()
        assert w._top_overlord("KingdomOfItaly") == "France"
        _ratify(w, "Austria", "France")
        assert _signed(w, "Austria")["kind"] == "capital"

        w2 = _boot()
        for region in THE_FOUR:
            _hold(w2, region, "France", "Austria")
        w2.regions["Vienna"].controller = "Spain"
        w2.invalidate_active_nations_cache()
        assert w2.get_diplomatic_state("Spain", "France") == "ALLIANCE"
        _ratify(w2, "Austria", "France")
        assert _signed(w2, "Austria") is None

    def test_the_kinds_keep_their_precedence(self, vienna_road):
        """A cession peace still writes `beaten`; a peace signed at the
        table still writes `table`; the capital is the third road."""
        w = vienna_road
        assert congress.note_ratification(
            w, ["Austria"], True, beaten=["Austria"], capital_kept=["Austria"]
        ) == {"Austria": "beaten"}
        assert _signed(w, "Austria")["kind"] == "beaten"
        w2 = vienna_road
        w2.congress = None
        assert congress.note_ratification(
            w2, ["Austria"], True, capital_kept=["Austria"]) == {"Austria": "capital"}
        w3 = _boot()
        for region in THE_FOUR:
            _hold(w3, region, "France", "Austria")
        w3.diplomatic_states[w3._make_diplo_key("Austria", "France")] = "PEACE"
        w3.invalidate_active_nations_cache()
        _sit(w3)
        assert congress.note_ratification(
            w3, ["Austria"], True, capital_kept=["Austria"]) == {"Austria": "table"}

    def test_a_minor_never_latches_and_a_peace_that_ends_no_war_writes_nothing(self, vienna_road):
        w = vienna_road
        assert congress.note_ratification(w, ["Bavaria"], True,
                                          capital_kept=["Bavaria"]) == {}
        assert congress.note_ratification(w, ["Austria"], False,
                                          capital_kept=["Austria"]) == {}
        assert _signed(w, "Austria") is None

    def test_a_truce_never_latches(self, vienna_road):
        """Item 6: only a SIGNED PEACE. A truce ends no war."""
        w = vienna_road
        result = _ratify(w, "Austria", "France", ptype="armistice")
        assert result["type"] == "diplomatic_treaty_signed"
        assert w.get_diplomatic_state("Austria", "France") == "ARMISTICE"
        assert _signed(w, "Austria") is None

    def test_a_truce_that_runs_out_into_peace_never_latches(self, vienna_road):
        """The expiry road (`game_end.count_peace`) is not a signature."""
        w = vienna_road
        _ratify(w, "Austria", "France", ptype="armistice")
        with _quiet():
            game_end.count_peace(w, "Austria", "France")
        assert _signed(w, "Austria") is None

    def test_the_lever_down_restores_ruling_two(self, vienna_road, monkeypatch):
        """SR-1a's ruling (2): a retention is not a cession the court
        signed, and no latch is written."""
        monkeypatch.setattr(congress, "A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES", False)
        w = vienna_road
        _ratify(w, "Austria", "France")
        assert not (congress.record(w) or {}).get("signed")

    def test_the_latch_round_trips(self, vienna_road):
        w = vienna_road
        _ratify(w, "Austria", "France")
        with _quiet():
            again = WorldState.from_dict(w.to_dict())
        assert _signed(again, "Austria") == _signed(w, "Austria")
        assert congress.answer(again, "Austria")["by"] == "treaty"


# ════════════════════════════════════════════════════════════════════════
# 2. The breakers
# ════════════════════════════════════════════════════════════════════════

class TestTheThreeBreakers:
    """Item 2: the latch breaks when the capital leaves the bloc — handed
    back, retaken by its court, or taken by a third party. The read is
    derived (`_signed_record`); the tick stamps the break with its reason."""

    def _latched(self):
        w = _boot()
        for region in THE_FOUR:
            _hold(w, region, "France", "Austria")
        _ratify(w, "Austria", "France")
        assert congress.answer(w, "Austria")["by"] == "treaty"
        return w

    @pytest.mark.parametrize("taker", ["Austria", "Russia", "Bavaria"])
    def test_the_capital_leaving_the_bloc_breaks_the_latch(self, taker):
        w = self._latched()
        w.regions["Vienna"].controller = taker
        w.invalidate_active_nations_cache()
        assert congress._signed_record(w, "Austria") is None
        row = congress.answer(w, "Austria")
        assert row["by"] != "treaty"

    def test_retaken_by_force_through_the_capture_seam(self):
        w = self._latched()
        with _quiet():
            assert w.capture_region("Vienna", "Austria")
        assert congress._signed_record(w, "Austria") is None

    def test_the_tick_stamps_the_break_with_its_reason(self):
        w = self._latched()
        _sit(w)
        assert congress.answer(w, "Austria")["by"] == "treaty"
        w.regions["Vienna"].controller = "Austria"
        w.invalidate_active_nations_cache()
        _tick(w)
        rec = _signed(w, "Austria")
        assert rec["broken"] == {"turn": w.current_turn,
                                 "reason": "Vienna left our hands"}
        assert congress.answer(w, "Austria")["by"] != "treaty"

    def test_a_capital_that_stays_keeps_the_latch_through_the_sitting(self):
        w = self._latched()
        _sit(w)
        _tick(w, 3)
        assert _signed(w, "Austria")["broken"] is None
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES

    def test_a_vassals_capital_moving_within_the_bloc_does_not_break(self):
        w = self._latched()
        w.regions["Vienna"].controller = "KingdomOfItaly"
        w.invalidate_active_nations_cache()
        assert congress._signed_record(w, "Austria")["kind"] == "capital"


# ════════════════════════════════════════════════════════════════════════
# 3. The price rider
# ════════════════════════════════════════════════════════════════════════

class TestThePriceRider:
    """Item 3: recognition by defeat costs a defeat. The scorer reads a
    great power's retained capital as a capital LOST and forfeits the
    kept-all bonus, so a white peace does not buy it for nothing."""

    def test_a_retained_capital_reads_as_a_capital_lost(self, vienna_road):
        w = vienna_road
        with_rider = SS.calculate_leader_own_losses(
            w, accepting_leader="Austria", settlement_terms=[{"type": "peace"}],
            capital_retained_by_proposer=True)
        without = SS.calculate_leader_own_losses(
            w, accepting_leader="Austria", settlement_terms=[{"type": "peace"}])
        assert with_rider["capital_lost"] and with_rider["capital_retained_by_proposer"]
        assert not with_rider["kept_all_with_holdings"]
        assert not without["capital_lost"] and not without["capital_retained_by_proposer"]
        assert without["kept_all_with_holdings"]
        assert (without["score"] - with_rider["score"]
                == SS.LEADER_KEEPS_ALL_BONUS - SS.LEADER_LOSS_CAPITAL)

    def test_the_read_names_the_bloc_not_the_ally_nor_a_returned_capital(self, vienna_road):
        w = vienna_road
        war = w.war_instances["war_1"]
        kw = dict(proposer_side="attackers", accepting_leader="Austria")
        peace = [{"type": "peace"}]
        assert SS.capital_retained_by_proposer_bloc(w, war, settlement_terms=peace, **kw)
        # a term that hands Vienna back
        assert not SS.capital_retained_by_proposer_bloc(
            w, war, settlement_terms=peace + [{"type": "territory_return",
                                              "regions": ["Vienna"]}], **kw)
        # a great power only
        assert not SS.capital_retained_by_proposer_bloc(
            w, war, settlement_terms=peace, proposer_side="attackers",
            accepting_leader="Bavaria")
        # the vassal chain is the bloc; an ally is not
        w.regions["Vienna"].controller = "KingdomOfItaly"
        w.invalidate_active_nations_cache()
        assert SS.capital_retained_by_proposer_bloc(w, war, settlement_terms=peace, **kw)
        w.regions["Vienna"].controller = "Spain"
        w.invalidate_active_nations_cache()
        assert not SS.capital_retained_by_proposer_bloc(w, war, settlement_terms=peace, **kw)
        w.regions["Vienna"].controller = "Austria"
        w.invalidate_active_nations_cache()
        assert not SS.capital_retained_by_proposer_bloc(w, war, settlement_terms=peace, **kw)

# ════════════════════════════════════════════════════════════════════════
# 4. The levers quote their turns; the projection names the road
# ════════════════════════════════════════════════════════════════════════

class TestTheLeversQuoteTheirTurns:

    def test_the_clause_reads_the_courting_rate_and_the_sitting(self):
        w = _boot()
        per = congress.courting_rate(w)
        assert per == 8, "the Cabinet's applied IMPROVE figure on the 1805 board"
        turns = math.ceil(40 / per)
        assert congress.courtship_clause(w, 40) == (
            f" — about {turns} turns at +{per} a turn; the Congress sits 8")
        assert congress.courtship_clause(w, 8 * 9) == (
            f" — about 9 turns at +{per} a turn; the Congress sits 8 — not within one sitting")
        assert congress.courtship_clause(w, 0) == ""
        _sit(w)
        left = congress.congress_turns(w) - congress.day_of_sitting(w)
        assert congress.courtship_clause(w, 8 * 9) == (
            f" — about 9 turns at +{per} a turn — not within this sitting ({left} turns remain)")
        assert congress.courtship_clause(w, 8) == (
            f" — about 1 turn at +{per} a turn ({left} turns remain of this sitting)")

    def test_the_clause_is_silent_with_the_lever_down(self, monkeypatch):
        monkeypatch.setattr(congress, "THE_LEVERS_QUOTE_THEIR_TURNS", False)
        w = _boot()
        assert congress.courtship_clause(w, 40) == ""
        price = congress.price(w, "Prussia")
        rel = next(l for l in price["levers"] if l["key"] == "relation")
        assert rel["text"] == "better relations (court them)"
        assert all("a turn" not in b["text"] for b in price["bundle"])

    def test_every_courtship_lever_on_the_table_carries_it(self):
        """Prussia at peace, refusing: the relation lever, the bundle's
        relation row and the bundle sentence all quote the turns."""
        w = _boot()
        price = congress.price(w, "Prussia")
        rel = next(l for l in price["levers"] if l["key"] == "relation")
        # SF-LB-3 (Score Finish Step 7b) — a conscious flip: a quote that
        # names its court reads the STEPPED road (`diplomacy.courtship_road`,
        # the drift included), and Prussia's warm relation drifts toward
        # zero, so the honest road is longer than the flat ceil(points / 8)
        # this pin was written against — 9 turns, past one sitting. The
        # clause's two shapes are both legal; the arithmetic is pinned in
        # tests/test_sf_page_the_front_page_of_the_peace.py.
        m = re.search(r"\(court them — about (\d+) turns? at \+8 a turn; "
                      r"the Congress sits 8( — not within one sitting)?\)", rel["text"])
        assert m, rel["text"]
        assert bool(m.group(2)) == (int(m.group(1)) > 8)
        row = next(b for b in price["bundle"] if b["key"] == "relation")
        assert row["turns_clause"].startswith(" — about ") and row["turns_clause"] in row["text"]
        assert row["text"] in price["text"]

    def test_the_sues_projection_names_the_road(self, vienna_road):
        """A court whose capital we hold always SUES (it never reads
        REFUSES-at-war), so the road is named on the projection before a
        summons and on the suing court's price while it sits."""
        w = vienna_road
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES and row["projected"]
        assert row["reason"].endswith(
            "; a peace that leaves Vienna in our hands recognizes the order")
        assert "the peace it signs then recognizes the order" in congress.price(w, "Austria")["text"]
        _sit(w)
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES and not row["projected"]
        assert row["reason"].endswith("recognizes the order")
        price = congress.price(w, "Austria")
        assert "a peace signed while the Congress sits recognizes the order" in price["text"]
        assert [l["key"] for l in price["levers"]] == ["peace"]

    def test_without_the_capital_the_projection_says_nothing_of_it(self):
        w = _boot()
        for region in ("Bohemia", "Moravia"):
            _hold(w, region, "France", "Austria")
        assert "recognizes the order" not in congress.answer(w, "Austria")["reason"]

    def test_the_lever_down_leaves_the_projection_alone(self, vienna_road, monkeypatch):
        monkeypatch.setattr(congress, "A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES", False)
        w = vienna_road
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES
        assert "recognizes the order" not in row["reason"]


# ════════════════════════════════════════════════════════════════════════
# 5. The wording (item 4)
# ════════════════════════════════════════════════════════════════════════

class TestTheWording:

    def test_the_bilateral_summary_carries_the_recognition_line(self, vienna_road):
        w = vienna_road
        result = _ratify(w, "Austria", "France")
        lines = result["peace_ratification_summary"]["terms_ratified"]
        assert lines[-1] == ("Recognition: Austria will recognize the order at "
                             "the Congress — Vienna stays ours by this treaty.")
        # the stash is read once
        assert game_end.take_recognition_lines(w) == []

    def test_a_peace_that_latches_nothing_says_nothing(self):
        w = _boot()
        result = _ratify(w, "Austria", "France")
        assert not any("Recognition:" in line for line in
                       result["peace_ratification_summary"].get("terms_ratified", []))

    def test_the_review_says_what_the_signature_buys_and_a_return_clause_silences_it(self, vienna_road):
        w = vienna_road
        note = congress.recognition_by_capital_preview(
            w, ["Austria", "Britain"], [{"type": "peace"}])
        assert note == ["Recognition: Austria will recognize the order at the "
                        "Congress — Vienna stays ours by this treaty."]
        assert congress.recognition_by_capital_preview(
            w, ["Austria"], [{"type": "territory_return", "regions": ["Vienna"]}]) == []
        assert congress.recognition_by_capital_preview(w, ["Bavaria"], []) == []

    def test_the_preview_is_silent_with_the_lever_down(self, vienna_road, monkeypatch):
        monkeypatch.setattr(congress, "A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES", False)
        assert congress.recognition_by_capital_preview(vienna_road, ["Austria"], []) == []


# ════════════════════════════════════════════════════════════════════════
# 6. The retest's turn-24 save, with Austria latched (item 7 + RS-D1's
#    rider on the cascade: a recognizing court is not marched by the league)
# ════════════════════════════════════════════════════════════════════════

class TestTheTurn24ReplayWithAustriaLatched:

    def test_the_league_forms_without_austria_and_forty_seven_holds(self):
        from backend.game_logic.turn_manager import TurnManager
        save = json.loads(T24.read_text(encoding="utf-8"))
        with _quiet():
            w = WorldState.from_dict(save["world_state"])
        assert w.regions["Vienna"].controller == "France"
        assert w.get_diplomatic_state("Austria", "France") == "PEACE"
        # The peace Austria signed on the played road kept Vienna in French
        # hands: with RS-D1 it would have latched. Latch it as that peace
        # would have.
        assert congress.note_ratification(
            w, ["Austria"], True, capital_kept=["Austria"]) == {"Austria": "capital"}
        with _quiet():
            assert congress.summon(w)["success"]
        tm = TurnManager(w)
        counts, stances, states = [], [], []
        with _quiet():
            for _ in range(8):
                tm.end_turn()
                counts.append(congress.titled(w)["count"])
                stances.append(congress.answer(w, "Austria")["stance"])
                states.append(w.get_diplomatic_state("Austria", "France"))
                if (w.congress or {}).get("status") != congress.SITTING:
                    break
        assert all(c >= 47 for c in counts), counts
        assert set(states) == {"PEACE"}, states
        assert set(stances) == {congress.RECOGNIZES}, stances
        assert _signed(w, "Austria")["broken"] is None
