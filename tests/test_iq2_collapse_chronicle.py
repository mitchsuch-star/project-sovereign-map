"""IQ-2 "The Collapse Is Legible" — the chronicle half (campaign log + Le Moniteur).

Measured in the played 40-turn campaigns: a France reduced to one province,
then to none, kept a chronicle that un-wrote its own losses and a paper that
narrated an ordinary campaign.

  D1  `_is_player_event` read `captured_by` and never `captured_from`, so a
      province WE lost fell to the fog arm, and once it was no longer ours
      `decay_intel` dropped it: 27 of 27 own-loss rows fell to 5 within two
      end turns (28 -> 3 at 0 provinces). Le Moniteur reads the same filter.
      Lever: campaign_log.PLAYER_LOSSES_ARE_PLAYER_EVENTS.
  D2  `WorldState.log_event` stamps `holdings_left` (and `holdings_realm`) on
      a province taken from the player — the ONE chokepoint every
      `region_captured` producer passes through, read AFTER the controller
      change — and the one-liner says so at 0 and 1. Gated on the collapse
      lever and sandbox worlds; ZERO new campaign-log types.
  D3  Le Moniteur: (a) a collapse lead before the triumph/reverse arms;
      (b) the Bourse prints a deficit as one (lever THE_BOURSE_READS_THE_DEFICIT);
      (c) the masthead and the quiet leads stop dating the paper from an
      enemy-held Paris (lever THE_MONITEUR_SEES_THE_CAPITAL_LOST);
      (d) a special edition, weight 97, on the loss that leaves the realm at
      the collapse ceiling, keyed for the WO-44 dedupe.

The binding scope note: legible, never terminal. No sentence here may say or
imply that the campaign ends — pinned below.
"""

import contextlib
import io
from pathlib import Path

import pytest

import backend.campaign_log as CL
from backend.campaign_log import filter_campaign_log, format_event_oneliner
from backend.game_logic import collapse as C
from backend.game_logic import gazette as G
from backend.models.intel import FULL, UNKNOWN
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client"
            / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

FORBIDDEN = ("campaign ends", "game over", "defeat", "eliminated",
             "last chance")


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


def _collapse(world, keep=(), to="Austria"):
    """Hand every French province but `keep` to a court at war with France."""
    for name in world.get_nation_regions("France"):
        if name not in keep:
            world.regions[name].controller = to
    world.invalidate_active_nations_cache()


@contextlib.contextmanager
def _lever(module, name, value):
    old = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, old)


def _loss(region, by="Austria", frm="France", **extra):
    ev = {"type": "region_captured", "region": region, "captured_by": by,
          "captured_from": frm, "method": "secure"}
    ev.update(extra)
    return ev


def _emperor_taken(turn=12):
    return {"type": "marshal_captured", "turn": turn, "marshal": "Napoleon",
            "nation": "France", "captor": "Austria", "sovereign": True}


def _french_battle(outcome="attacker_victory", location="Swabia"):
    return {"type": "battle", "attacker": "Ney", "defender": "Mack",
            "attacker_nation": "France", "defender_nation": "Austria",
            "location": location, "outcome": outcome}


# ════════════════════════════════════════════════════════════════════════
# D1 — the chronicle keeps our own losses
# ════════════════════════════════════════════════════════════════════════

class TestD1OwnLossesStayInTheChronicle:

    def test_an_own_loss_survives_decayed_intel(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        ev = _loss("Normandy")
        w.log_event(ev)
        w.get_region_intel("Normandy").visibility = UNKNOWN
        assert filter_campaign_log([ev], w) == [ev]

    def test_lever_down_restores_the_drop(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        ev = _loss("Normandy")
        w.log_event(ev)
        w.get_region_intel("Normandy").visibility = UNKNOWN
        with _lever(CL, "PLAYER_LOSSES_ARE_PLAYER_EVENTS", False):
            assert filter_campaign_log([ev], w) == []

    def test_the_measured_shape_every_own_loss_row_survives(self):
        """27 own-loss rows, every lost province decayed to UNKNOWN — the
        state two end turns produced in the played campaign. All 27 stay;
        lever down, none do (the measured 27 -> few)."""
        w = _boot()
        lost = sorted(r for r in w.get_nation_regions("France") if r != "Brittany")
        assert len(lost) == 27
        rows = []
        for name in lost:
            w.regions[name].controller = "Austria"
            w.invalidate_active_nations_cache()
            ev = _loss(name)
            w.log_event(ev)
            rows.append(ev)
        for name in lost:
            w.get_region_intel(name).visibility = UNKNOWN
        assert len(filter_campaign_log(rows, w)) == 27
        with _lever(CL, "PLAYER_LOSSES_ARE_PLAYER_EVENTS", False):
            assert len(filter_campaign_log(rows, w)) == 0

    def test_a_third_partys_loss_still_needs_eyes(self):
        """The fix is scoped to OUR losses: a Prussian province taken by
        Russia is still fog-gated."""
        w = _boot()
        region = sorted(w.get_nation_regions("Prussia"))[0]
        ev = _loss(region, by="Russia", frm="Prussia")
        w.get_region_intel(region).visibility = UNKNOWN
        assert filter_campaign_log([ev], w) == []
        w.get_region_intel(region).visibility = FULL
        assert filter_campaign_log([ev], w) == [ev]

    def test_scoped_to_the_capture_type(self):
        assert CL._is_player_event(_loss("Normandy"), "France") is True
        assert CL._is_player_event(
            {"type": "move", "captured_from": "France"}, "France") is False


# ════════════════════════════════════════════════════════════════════════
# D2 — the loss carries what it left us
# ════════════════════════════════════════════════════════════════════════

class TestD2HoldingsLeftStamp:

    def test_a_loss_to_one_province_stamps_one(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        ev = _loss("Normandy")
        w.log_event(ev)
        assert ev["holdings_left"] == 1 and type(ev["holdings_left"]) is int
        assert ev["holdings_realm"] == "France"

    def test_a_loss_to_nothing_stamps_zero(self):
        w = _boot()
        _collapse(w)
        ev = _loss("Brittany")
        w.log_event(ev)
        assert ev["holdings_left"] == 0

    def test_the_count_is_read_after_the_controller_change(self):
        """Above the ceiling the count is still stamped — and it is the
        realm AFTER the loss (28 at boot, 27 once Normandy is gone)."""
        w = _boot()
        assert len(w.get_nation_regions("France")) == 28
        w.regions["Normandy"].controller = "Austria"
        w.invalidate_active_nations_cache()
        ev = _loss("Normandy")
        w.log_event(ev)
        assert ev["holdings_left"] == 27

    def test_the_occupation_producer_stamps_the_count_after_its_capture(self):
        """A real producer (`_apply_occupation_capture_effects`, AI arm):
        it mutates the controller THEN logs, so the stamp reads 1."""
        w = _boot()
        _collapse(w, keep=("Brittany", "Normandy"))
        mack = w.marshals["Mack"]
        with contextlib.redirect_stdout(io.StringIO()):
            w._apply_occupation_capture_effects(mack, "Normandy")
        rows = [e for e in w.event_log if e.get("type") == "region_captured"
                and e.get("region") == "Normandy"]
        assert rows and rows[-1]["captured_from"] == "France"
        assert rows[-1]["holdings_left"] == 1

    def test_the_attack_capture_producer_stamps_the_count(self):
        """The other capture_region caller: combat_executor's instant
        capture, AI branch (`_apply_ai_capture_choice`)."""
        from backend.commands.executor import CommandExecutor
        w = _boot()
        target = next(r for r in sorted(w.get_nation_regions("France"))
                      if r != "Brittany"
                      and not w.regions[r].has_building("fortification"))
        _collapse(w, keep=("Brittany", target))
        ex = CommandExecutor()
        with contextlib.redirect_stdout(io.StringIO()):
            result = ex._combat._attempt_region_capture(
                w.marshals["Mack"], target, w, {"world": w})
        assert result["captured"]
        rows = [e for e in w.event_log if e.get("type") == "region_captured"
                and e.get("region") == target]
        assert rows and rows[-1]["holdings_left"] == 1

    def test_a_stamped_key_is_never_overwritten(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        ev = _loss("Normandy", holdings_left=5)
        w.log_event(ev)
        assert ev["holdings_left"] == 5
        assert "holdings_realm" not in ev

    def test_another_courts_loss_is_not_stamped(self):
        w = _boot()
        ev = _loss("Bohemia", by="France", frm="Austria")
        w.log_event(ev)
        assert "holdings_left" not in ev

    def test_the_legacy_world_is_byte_identical(self):
        w = WorldState(player_nation="France")
        assert w.sandbox_mode is False
        ev = _loss("Lyon")
        w.log_event(ev)
        assert set(ev) == {"type", "region", "captured_by", "captured_from",
                           "method", "turn"}

    def test_collapse_lever_down_stamps_nothing(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        ev = _loss("Normandy")
        with _lever(C, "THE_COLLAPSE_IS_LEGIBLE", False):
            w.log_event(ev)
        assert "holdings_left" not in ev and "holdings_realm" not in ev


class TestD2TheOneLiner:

    def test_zero_says_no_province(self):
        line = format_event_oneliner(
            _loss("Brittany", holdings_left=0, holdings_realm="France"))
        assert line == ("Brittany captured by Austria (secure) — France "
                        "holds no province")

    def test_one_says_a_single_province(self):
        line = format_event_oneliner(
            _loss("Normandy", holdings_left=1, holdings_realm="France"))
        assert line.endswith(" — France holds a single province")

    def test_above_the_ceiling_says_nothing_more(self):
        assert format_event_oneliner(
            _loss("Normandy", holdings_left=2, holdings_realm="France")
        ) == "Normandy captured by Austria (secure)"

    def test_an_unstamped_row_is_byte_identical(self):
        assert format_event_oneliner(_loss("Normandy")) == \
            "Normandy captured by Austria (secure)"
        ev = _loss("Normandy")
        del ev["method"]
        assert format_event_oneliner(ev) == "Normandy captured by Austria"

    def test_the_stamped_realm_name_is_the_one_printed(self):
        line = format_event_oneliner(
            _loss("Normandy", holdings_left=1, holdings_realm="the Empire"))
        assert line.endswith(" — the Empire holds a single province")

    def test_the_chronicle_endpoint_prints_it(self):
        """The screen the player reads: GET /campaign_log, driven through
        the real endpoint with the swap idiom."""
        from fastapi.testclient import TestClient

        import backend.main as M
        from backend.commands.parser import CommandParser
        w = _boot()
        _collapse(w, keep=("Brittany",))
        w.log_event(_loss("Normandy"))
        w.get_region_intel("Normandy").visibility = UNKNOWN
        old = (M.parser, M.world, M.game_state)
        try:
            M.parser = CommandParser(use_real_llm=False)
            M.world = w
            M.game_state = {"world": w}
            payload = TestClient(M.app).get("/campaign_log").json()
        finally:
            M.parser, M.world, M.game_state = old
        displays = [e["display"] for t in payload["turns"] for e in t["events"]]
        assert ("Normandy captured by Austria (secure) — France holds a "
                "single province") in displays


# ════════════════════════════════════════════════════════════════════════
# D3(a) — the collapse leads the front page
# ════════════════════════════════════════════════════════════════════════

class TestD3aCollapseLead:

    def test_a_fallen_realm_leads_with_the_fact(self):
        w = _boot()
        _collapse(w)
        lead = G._press_lead(w, [])
        assert lead.startswith("Paris is in Austria's hands and France holds "
                               "no province of her own;"), lead
        assert "the Moniteur counsels patience and trust in the army." in lead
        assert "salons go on" not in lead and "capital watches" not in lead

    def test_the_last_province_away_from_paris(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        lead = G._press_lead(w, [_loss("Normandy")])
        assert lead.startswith("Paris is in Austria's hands; the Government "
                               "speaks of a temporary misfortune. France "
                               "holds a single province: Brittany;"), lead

    def test_the_last_province_is_paris(self):
        w = _boot()
        _collapse(w, keep=("Paris",))
        lead = G._press_lead(w, [])
        assert lead.startswith("France holds a single province: Paris; the "
                               "capital stands"), lead

    def test_the_collapse_outranks_a_triumph_but_reports_it(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        lead = G._press_lead(w, [_french_battle()])
        assert "VICTOIRE" not in lead
        assert lead.startswith("Paris is in Austria's hands")
        assert lead.endswith("At Swabia, the eagles still carry the day.")

    def test_the_emperor_a_prisoner_is_stated(self):
        w = _boot()
        _collapse(w, keep=("Brittany",))
        w.marshals["Napoleon"].captured_by = "Austria"
        lead = G._press_lead(w, [])
        assert "The Emperor is a prisoner of Austria." in lead

    def test_no_army_no_counsel_of_the_army(self):
        w = _boot()
        _collapse(w)
        for m in w.marshals.values():
            if m.nation == "France":
                m.strength = 0
        lead = G._press_lead(w, [])
        assert "counsels patience." in lead and "and the army" not in lead

    @pytest.mark.parametrize("keep", [(), ("Brittany",), ("Paris",)])
    def test_no_lead_promises_an_ending(self, keep):
        w = _boot()
        _collapse(w, keep=keep)
        w.marshals["Napoleon"].captured_by = "Austria"
        for rows in ([], [_french_battle()],
                     [_french_battle(outcome="defender_victory")]):
            lead = G._press_lead(w, rows).lower()
            for phrase in FORBIDDEN:
                assert phrase not in lead, (phrase, lead)

    def test_levers_down_the_pre_iq2_leads_return(self):
        w = _boot()
        _collapse(w)
        with _lever(C, "THE_COLLAPSE_IS_LEGIBLE", False), \
                _lever(G, "THE_MONITEUR_SEES_THE_CAPITAL_LOST", False):
            assert G._press_lead(w, []) == \
                "The continent holds its breath; commerce and the salons go on."
            assert G._press_lead(w, [_loss("Normandy")]) == \
                "The armies of Europe are in motion; the capital watches."

    def test_a_standing_realm_is_untouched(self):
        w = _boot()
        assert G._press_lead(w, []) == \
            "The continent holds its breath; commerce and the salons go on."
        assert G._press_lead(w, [_french_battle()]).startswith("VICTOIRE!")


# ════════════════════════════════════════════════════════════════════════
# D3(c) — the paper is not dated from an enemy-held Paris
# ════════════════════════════════════════════════════════════════════════

def _paris_lost(w):
    w.regions["Paris"].controller = "Austria"
    w.invalidate_active_nations_cache()


class TestD3cTheCapitalLost:

    def test_the_masthead_moves_to_headquarters(self):
        w = _boot()
        _paris_lost(w)
        issue = G.compose_issue(w, 0)
        assert issue["masthead"] == \
            f"LE MONITEUR — Imperial Headquarters, {issue['dateline']}"

    def test_lever_down_the_masthead_reads_paris(self):
        w = _boot()
        _paris_lost(w)
        with _lever(G, "THE_MONITEUR_SEES_THE_CAPITAL_LOST", False):
            issue = G.compose_issue(w, 0)
        assert issue["masthead"].startswith("LE MONITEUR — Paris, ")

    def test_a_held_capital_keeps_paris(self):
        w = _boot()
        assert G.compose_issue(w, 0)["masthead"].startswith(
            "LE MONITEUR — Paris, ")

    def test_the_quiet_leads_name_whose_hands(self):
        """Not keyed on the collapse: France still holds 27 provinces."""
        w = _boot()
        _paris_lost(w)
        assert C.get_collapse_state(w) is None
        fact = ("Paris is in Austria's hands, and the Government speaks of a "
                "temporary misfortune.")
        assert G._press_lead(w, []) == f"The continent holds its breath; {fact}"
        assert G._press_lead(w, [_loss("Paris")]) == \
            f"The armies of Europe are in motion; {fact}"

    def test_a_victory_still_leads_a_realm_that_stands(self):
        w = _boot()
        _paris_lost(w)
        assert G._press_lead(w, [_french_battle()]).startswith("VICTOIRE!")


# ════════════════════════════════════════════════════════════════════════
# D3(b) — the Bourse prints a deficit as one
# ════════════════════════════════════════════════════════════════════════

class TestD3bTheBourse:

    def test_a_negative_treasury_is_a_deficit(self):
        w = _boot()
        w.nation_gold["France"] = -1234
        line = G._bourse_line(w)
        assert "a deficit of 1,234 francs and the rentes fall." in line
        assert "steady" not in line and "-1,234" not in line

    def test_lever_down_the_funds_are_steady_again(self):
        w = _boot()
        w.nation_gold["France"] = -1234
        with _lever(G, "THE_BOURSE_READS_THE_DEFICIT", False):
            line = G._bourse_line(w)
        assert "-1,234" in line and "rentes fall" not in line

    def test_a_standing_bankruptcy_counter_is_a_deficit(self):
        """The engine's own reading: `nation_bankruptcy_turns >= 1` is the
        bankruptcy mercy's predicate — a chest back above zero over a
        standing counter is still in arrears."""
        w = _boot()
        w.nation_gold["France"] = 500
        w.nation_bankruptcy_turns["France"] = 1
        line = G._bourse_line(w)
        assert "500 francs, the State in deficit, and the rentes fall." in line

    def test_a_solvent_treasury_is_byte_identical(self):
        w = _boot()
        w.nation_gold["France"] = 800
        w.nation_bankruptcy_turns["France"] = 0
        now = G._bourse_line(w)
        with _lever(G, "THE_BOURSE_READS_THE_DEFICIT", False):
            assert now == G._bourse_line(w)
        assert "rentes fall" not in now

    def test_the_unblockaded_deficit_line(self):
        import backend.game_logic.naval as N
        w = _boot()
        w.nation_gold["France"] = -50
        with _lever(N, "is_blockaded", lambda world, nation: False):
            assert G._bourse_line(w) == ("THE BOURSE — The Treasury stands at "
                                         "a deficit of 50 francs and the "
                                         "rentes fall.")


# ════════════════════════════════════════════════════════════════════════
# D3(d) — the special edition for the realm reduced
# ════════════════════════════════════════════════════════════════════════

class TestD3dTheRealmReducedEdition:

    def test_the_weight_sits_between_the_emperor_and_the_capital(self):
        for reason in (G.REALM_REDUCED_TO_ONE, G.REALM_WITHOUT_A_PROVINCE):
            assert G._SPECIAL_WEIGHTS[reason] == 97
        assert (G._SPECIAL_WEIGHTS["THE EMPEROR TAKEN"] > 97
                > G._SPECIAL_WEIGHTS["THE CAPITAL HAS FALLEN"])

    def test_one_left(self):
        w = _boot()
        assert G._special_reason(w, [_loss("Normandy", holdings_left=1)]) \
            == G.REALM_REDUCED_TO_ONE

    def test_none_left(self):
        w = _boot()
        assert G._special_reason(w, [_loss("Brittany", holdings_left=0)]) \
            == G.REALM_WITHOUT_A_PROVINCE

    def test_the_lowest_on_the_page_is_the_one_edition(self):
        w = _boot()
        cands = G._special_candidates(w, [
            _loss("Normandy", holdings_left=1),
            _loss("Brittany", holdings_left=0)])
        realm = [c for c in cands if c[0] == 97]
        assert len(realm) == 1
        assert realm[0][1] == G.REALM_WITHOUT_A_PROVINCE
        assert realm[0][2] == f"{G.REALM_WITHOUT_A_PROVINCE}|Brittany"

    def test_above_the_ceiling_and_unstamped_rows_force_nothing(self):
        w = _boot()
        assert G._special_reason(w, [_loss("Normandy", holdings_left=2)]) is None
        assert G._special_reason(w, [_loss("Normandy")]) is None

    def test_another_courts_holdings_never_count(self):
        w = _boot()
        assert G._special_reason(w, [_loss(
            "Limousin", by="France", frm="Austria", holdings_left=0)]) is None

    def test_the_emperor_still_outranks_it(self):
        w = _boot()
        assert G._special_reason(w, [_loss("Normandy", holdings_left=1),
                                     _emperor_taken()]) == "THE EMPEROR TAKEN"

    def test_it_outranks_the_capital_falling_as_the_last_province(self):
        w = _boot()
        assert G._special_reason(w, [_loss("Paris", holdings_left=0)]) \
            == G.REALM_WITHOUT_A_PROVINCE

    def test_lever_down_the_capital_caption_returns(self):
        w = _boot()
        with _lever(C, "THE_COLLAPSE_IS_LEGIBLE", False):
            assert G._special_reason(w, [_loss("Paris", holdings_left=0)]) \
                == "THE CAPITAL HAS FALLEN"

    def _paper(self):
        w = _boot()
        _collapse(w, keep=("Brittany", "Normandy"))
        # An issue was published on turn 11, so turn 13 is off-cadence:
        # only a special can print.
        w.gazette_issues = [{"number": 1, "turn": 11, "dateline": "x",
                             "masthead": "m", "special": False,
                             "special_reason": "", "lead": "", "war": [],
                             "courts": [], "army": [], "bourse": ""}]
        w.regions["Normandy"].controller = "Austria"
        w.invalidate_active_nations_cache()
        return w

    def test_the_real_publication_prints_it(self):
        w = self._paper()
        w.current_turn = 12
        w.log_event(_loss("Normandy"))
        w.current_turn = 13
        with contextlib.redirect_stdout(io.StringIO()):
            issue = G.process_gazette(w)
        assert issue is not None and issue["special"]
        assert issue["special_reason"] == G.REALM_REDUCED_TO_ONE
        assert "Normandy" in issue["special_key"]
        assert issue["masthead"].startswith("LE MONITEUR — Imperial Headquarters, ")
        assert ("Normandy captured by Austria (secure) — France holds a single "
                "province") in issue["war"]
        assert issue["lead"].startswith("Paris is in Austria's hands; the "
                                        "Government speaks")

    def test_the_same_tail_stamped_loss_never_prints_twice(self):
        w = self._paper()
        w.current_turn = 13
        w.log_event(_loss("Normandy"))
        with contextlib.redirect_stdout(io.StringIO()):
            first = G.process_gazette(w)
        assert first and first["special_reason"] == G.REALM_REDUCED_TO_ONE
        w.current_turn = 14
        with contextlib.redirect_stdout(io.StringIO()):
            assert G.process_gazette(w) is None

    def test_lever_down_no_stamp_no_edition(self):
        w = self._paper()
        w.current_turn = 12
        with _lever(C, "THE_COLLAPSE_IS_LEGIBLE", False):
            w.log_event(_loss("Normandy"))
            w.current_turn = 13
            with contextlib.redirect_stdout(io.StringIO()):
                assert G.process_gazette(w) is None

    def test_no_caption_promises_an_ending(self):
        for reason in (G.REALM_REDUCED_TO_ONE, G.REALM_WITHOUT_A_PROVINCE):
            for phrase in FORBIDDEN:
                assert phrase not in reason.lower()
