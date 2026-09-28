"""SR-5b "The second road at sea" — Score Mandate Chunk 5
(`docs/SCORE_MANDATE_PLAN.md` §2), September 28, 2026. Rules
`docs/SYSTEMS_REFERENCE.md` §77.

  * AAR-D7 — the expedition names the levers that move its odds: a won
    diversion first, a smaller corps, the fleet at the readiness it climbs
    toward, ten more sail, an ally's squadron beside ours. Every lever is
    `naval.expedition_slip_odds` — the resolver's own odds — re-asked with
    one thing changed (lever `naval.THE_EXPEDITION_NAMES_ITS_LEVERS`).
  * NV-D9 "The Naval Yard" — RULED by the user ("Build them in SR-5b"): a
    court with an admiralty raises a yard at a coastal city of its own with a
    mooring, 1,200 gold, 4 turns, one administrative action, at most two per
    court; the yard is a SITE (keels, embarkation), never a RATE, and never a
    port (lever `naval.NAVAL_YARDS_CAN_BE_BUILT`).
  * NV-D3 privateers — STRUCK by the user's ruling ("we can strike
    privateer").
"""
import contextlib
import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.game_logic import naval as N
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.region import BUILDING_TYPES, can_build
from backend.models.world_state import (
    WorldState, apply_plunder_effects, apply_secure_effects)
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = (ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "europe_1805.json")
DOCS = ROOT / "docs"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def board(monkeypatch):
    """The live 1805 board behind POST /command, mock parser, a full chest."""
    C.board_env(monkeypatch)
    M.world.nation_gold["France"] = 20_000
    return M.world


def _post(text):
    return C.post(TestClient(M.app), {"command": text})


def _refill(world):
    """A fresh day of orders, so several admin orders can be sent in one
    test (each `build` is one administrative action)."""
    world.admin_actions_remaining = 4
    world.actions_remaining = 4


def _unblockade_france(world):
    """Britain stands on guard: France's crews stop rotting."""
    N.get_fleet(world, "Britain")["posture"] = "guard"
    assert not N.is_blockaded(world, "France")


def _finish_works(world, turns=4):
    """Advance only the construction timers (no AI, no combat)."""
    events = []
    for _ in range(turns):
        events += world.process_construction_timers()
    return events


def _lever(levers, key):
    return next((lv for lv in levers if lv["key"] == key), None)


def _french_yard_candidates(world):
    """France's provinces that could take a yard — computed off the board,
    never a hard-coded list (the map can move)."""
    return [name for name, refusal in N.naval_yard_sites(world, "France")]


# ═══════════════════════════════════════════════════════════════════════════
# AAR-D7 — the expedition names its levers
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLevers:

    def test_no_override_is_the_old_quote(self):
        """Every live caller passes neither override, so the quote, the
        confirm and the resolver read exactly what they always read."""
        w = _boot()
        for target in ("Munster", "London", "Cornwall", "Normandy", "Lisbon"):
            for troops in (3000, 9000, 15000):
                plain = N.expedition_slip_odds(w, "France", target, troops)
                assert plain == N.expedition_slip_odds(
                    w, "France", target, troops, window=None, escort_extra=0.0)
        # The record's own window still drives the default reading.
        N.get_fleet(w, "France")["window_turns"] = 2
        assert (N.expedition_slip_odds(w, "France", "London", 9000)
                == N.expedition_slip_odds(w, "France", "London", 9000,
                                          window=True))

    def test_the_window_override_halves_the_watch(self):
        """The diversion lever's counterfactual is the §5.3 window itself:
        the watch halved (WINDOW_COVERAGE_FACTOR) and the window's +25."""
        w = _boot()
        shut = N.expedition_slip_odds(w, "France", "London", 9000)
        opened = N.expedition_slip_odds(w, "France", "London", 9000,
                                        window=True)
        assert not shut["window"] and opened["window"]
        assert abs(opened["coverage"]
                   - shut["coverage"] * N.WINDOW_COVERAGE_FACTOR) <= 0.1
        assert opened["odds"] > shut["odds"]

    def test_each_lever_is_the_resolvers_own_odds_reasked(self):
        w = _boot()
        troops = 12000
        levers = N.expedition_odds_levers(w, "France", "London", troops)
        assert levers, "London is watched — something must move the odds"
        div = _lever(levers, "diversion")
        assert div["odds"] == N.expedition_slip_odds(
            w, "France", "London", troops, window=True)["odds"]
        corps = _lever(levers, "corps")
        assert corps["odds"] == N.expedition_slip_odds(
            w, "France", "London", N.EXPEDITION_LEVER_CORPS)["odds"]
        sail = _lever(levers, "sail")
        assert sail["odds"] == N.expedition_slip_odds(
            w, "France", "London", troops,
            escort_extra=N.EXPEDITION_LEVER_SAIL * N.NEW_SHIP_READINESS
            / 100.0)["odds"]
        base = N.expedition_slip_odds(w, "France", "London", troops)["odds"]
        for lv in levers:
            assert lv["gain"] == lv["odds"] - base >= N.EXPEDITION_LEVER_MIN_GAIN

    def test_ten_more_sail_is_ten_green_keels(self):
        """The sail lever's arithmetic IS `lay_down_ship`'s fold: ten keels
        at NEW_SHIP_READINESS add exactly 10 x 40 / 100 effective."""
        w = _boot()
        rec = N.get_fleet(w, "France")
        before = N.effective_strength(rec)
        for _ in range(N.EXPEDITION_LEVER_SAIL):
            rec["built_this_turn"] = 0
            N.lay_down_ship(w, "France")
        gained = N.effective_strength(rec) - before
        assert abs(gained - N.EXPEDITION_LEVER_SAIL * N.NEW_SHIP_READINESS
                   / 100.0) < 0.5  # readiness is rounded to a whole point

    def test_a_lever_under_the_floor_is_not_named(self):
        """Munster is open water (the patrol must catch us), where ten more
        sail barely move the odds — below the floor it is not offered."""
        w = _boot()
        troops = 12000
        base = N.expedition_slip_odds(w, "France", "Munster", troops)["odds"]
        with_sail = N.expedition_slip_odds(
            w, "France", "Munster", troops,
            escort_extra=N.EXPEDITION_LEVER_SAIL * N.NEW_SHIP_READINESS
            / 100.0)["odds"]
        assert with_sail - base < N.EXPEDITION_LEVER_MIN_GAIN
        levers = N.expedition_odds_levers(w, "France", "Munster", troops)
        assert _lever(levers, "sail") is None

    def test_an_unopposed_passage_has_no_levers(self):
        w = _boot()
        _unblockade_france(w)
        quote = N.expedition_slip_odds(w, "France", "Lisbon", 12000)
        assert quote["coverer"] is None and quote["odds"] == 100
        assert N.expedition_odds_levers(w, "France", "Lisbon", 12000) == []
        assert N.levers_line([]) == ""

    def test_the_diversion_lever_follows_the_diversions_own_gate(self):
        w = _boot()
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "diversion") is not None
        N.get_fleet(w, "France")["diversion_last_turn"] = int(w.current_turn)
        assert not all(t["met"] for t in N.diversion_terms_for(w, "France"))
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "diversion") is None
        N.get_fleet(w, "France")["diversion_last_turn"] = -1
        N.get_fleet(w, "France")["window_turns"] = 2   # already open
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "diversion") is None

    def test_the_admiralty_terms_are_the_levers_terms(self):
        """ONE source for THE ADMIRALTY's diversion terms and the lever."""
        w = _boot()
        report = N.build_admiralty_report(w)
        assert report["diversion_terms"] == N.diversion_terms_for(w, "France")

    def test_the_readiness_lever_uses_the_ticks_own_ceiling(self):
        w = _boot()
        _unblockade_france(w)
        rec = N.get_fleet(w, "France")
        rec["readiness"] = 50
        ceiling = N.readiness_ceiling(w, "France")
        levers = N.expedition_odds_levers(w, "France", "London", 9000)
        lever = _lever(levers, "readiness")
        assert lever is not None
        turns = -(-(ceiling - 50) // N.READINESS_TICK)
        assert f"readiness {ceiling} ({turns} turns in port)" in lever["label"]
        ships = int(rec["ships"])
        assert lever["odds"] == N.expedition_slip_odds(
            w, "France", "London", 9000,
            escort_extra=ships * (ceiling - 50) / 100.0)["odds"]
        # The tick climbs to exactly that ceiling in that many turns.
        for _ in range(turns):
            N._readiness_tick(w)
        assert rec["readiness"] == ceiling

    def test_the_tick_is_unchanged_by_the_ceiling_helper(self):
        """`readiness_ceiling` was lifted out of `_readiness_tick`: the war
        drill ceiling 75 against a superior fleet, 100 blockading at war."""
        w = _boot()
        _unblockade_france(w)
        assert N.readiness_ceiling(w, "France") == N.NAVY_DRILL_CEILING
        N.get_fleet(w, "Britain")["posture"] = "blockade"
        assert N.readiness_ceiling(w, "Britain") == N.READINESS_MAX

    def test_no_readiness_lever_under_blockade(self):
        w = _boot()
        assert N.is_blockaded(w, "France")
        N.get_fleet(w, "France")["readiness"] = 50
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "readiness") is None

    def test_the_sail_lever_needs_a_yard(self):
        w = _boot()
        N.get_fleet(w, "France")["dockyards"] = []
        assert N.controlled_dockyards(w, "France") == []
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "sail") is None

    def test_the_ally_lever_names_a_court_at_war_with_the_watcher(self):
        w = _boot()
        with _quiet():
            set_diplomatic_state(w, "Denmark", "Britain", "WAR")
        levers = N.expedition_odds_levers(w, "France", "London", 9000)
        ally = _lever(levers, "ally")
        denmark = N.get_fleet(w, "Denmark")
        expected = N.expedition_slip_odds(
            w, "France", "London", 9000,
            escort_extra=N.POOL_ALLIED * N.effective_strength(denmark))["odds"]
        assert ally is not None and ally["odds"] == expected
        assert "Denmark" in ally["label"]
        assert f"{int(denmark['ships'])} sail" in ally["label"]
        # Allied, the squadron pools — the lever is spent and the base odds
        # are what the lever promised.
        with _quiet():
            set_diplomatic_state(w, "France", "Denmark", "ALLIANCE")
        assert N.expedition_slip_odds(w, "France", "London", 9000)["odds"] \
            == expected
        assert _lever(N.expedition_odds_levers(w, "France", "London", 9000),
                      "ally") is None

    def test_levers_are_sorted_most_first_and_capped(self):
        w = _boot()
        with _quiet():
            set_diplomatic_state(w, "Denmark", "Britain", "WAR")
        levers = N.expedition_odds_levers(w, "France", "London", 15000)
        assert 0 < len(levers) <= N.EXPEDITION_LEVERS_SHOWN
        odds = [lv["odds"] for lv in levers]
        assert odds == sorted(odds, reverse=True)

    def test_the_corps_lever_is_a_new_marshals_corps(self):
        from backend.game_logic.recruitment import RECRUIT_MARSHAL_CORPS
        assert N.EXPEDITION_LEVER_CORPS == RECRUIT_MARSHAL_CORPS
        w = _boot()
        assert _lever(N.expedition_odds_levers(
            w, "France", "London", N.EXPEDITION_LEVER_CORPS), "corps") is None

    def test_the_line_reads_each_lever_and_its_odds(self):
        levers = [{"label": "a won diversion first (45 in 100)", "odds": 91},
                  {"label": "a 5,000-man corps", "odds": 75}]
        assert N.levers_line(levers) == (
            "What moves the odds: a won diversion first (45 in 100) → 91 · "
            "a 5,000-man corps → 75")

    def test_the_lever_down_names_nothing(self, monkeypatch):
        w = _boot()
        lannes = w.get_marshal("Lannes")
        lannes.strength, lannes.location = 12000, "Bordelais"
        monkeypatch.setattr(N, "THE_EXPEDITION_NAMES_ITS_LEVERS", False)
        assert N.expedition_odds_levers(w, "France", "London", 12000) == []
        rows = [r for rs in N.expedition_landing_options(w, "France").values()
                for r in rs]
        assert rows and all("levers" not in r for r in rows)

    def test_every_landing_row_carries_its_own_levers(self):
        """The payload memoises the line per (corps size, watcher, mode);
        re-asked directly, every row agrees (the memo's drift pin)."""
        w = _boot()
        lannes, murat = w.get_marshal("Lannes"), w.get_marshal("Murat")
        lannes.strength, lannes.location = 12000, "Bordelais"
        murat.strength, murat.location = 9000, "Brittany"
        opts = N.expedition_landing_options(w, "France")
        rows = [(region, row) for region, rs in opts.items() for row in rs]
        assert len(rows) > 20
        for region, row in rows:
            direct = N.levers_line(N.expedition_odds_levers(
                w, "France", region, row["strength"]))
            assert row.get("levers", "") == direct, region
        assert any(row.get("levers") for _r, row in rows)

    def test_the_confirm_names_the_levers(self, board):
        lannes = board.get_marshal("Lannes")
        lannes.strength, lannes.location = 12000, "Bordelais"
        reply = _post("land Lannes in Munster")
        msg = reply.get("message") or ""
        expected = N.levers_line(N.expedition_odds_levers(
            board, "France", "Munster", 12000))
        assert expected and f" {expected}. Sail? (yes / no)" in msg, msg

    def test_the_admiralty_land_chips_name_the_levers(self):
        w = _boot()
        lannes = w.get_marshal("Lannes")
        lannes.strength, lannes.location = 12000, "Bordelais"
        chips = N.build_admiralty_report(w)["expedition_chips"]
        land = [c for c in chips if c["command"].startswith("land ")]
        assert land and all("What moves the odds:" in c["note"] for c in land)


# ═══════════════════════════════════════════════════════════════════════════
# NV-D9 — the naval yard
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNavalYard:

    def test_the_ruled_price(self):
        assert BUILDING_TYPES["naval_yard"] == {
            "gold_cost": 1200, "build_time": 4,
            "allowed_in": ["capital", "major_city", "city"]}
        assert N.NAVAL_YARD_MAX_PER_NATION == 2

    def test_the_site_needs_an_anchorage(self):
        w = _boot()
        w.nation_gold["France"] = 20_000
        ok, why, _ = can_build(w, w.regions["Paris"], "naval_yard", "France")
        assert not ok and "has no anchorage" in why

    def test_a_dockyard_is_not_raised_twice(self):
        w = _boot()
        w.nation_gold["France"] = 20_000
        ok, why, _ = can_build(w, w.regions["Normandy"], "naval_yard", "France")
        assert not ok and why == "Normandy is already a dockyard."

    def test_a_court_without_an_admiralty_raises_no_yard(self):
        """NV-0's ruling of record: no navies row, no naval establishment."""
        w = _boot()
        assert N.get_fleet(w, "Sardinia") is None
        w.nation_gold["Sardinia"] = 20_000
        ok, why, _ = can_build(w, w.regions["Cagliari"], "naval_yard",
                               "Sardinia")
        assert not ok and "no naval establishment" in why

    def test_a_town_takes_no_yard(self):
        w = _boot()
        w.nation_gold["France"] = 20_000
        moor = N.mooring_provinces(w)
        town = next(name for name in w.get_nation_regions("France")
                    if name in moor
                    and w.regions[name].region_type in ("town", "rural")
                    and name not in N.all_dockyard_provinces(w))
        ok, why, _ = can_build(w, w.regions[town], "naval_yard", "France")
        assert not ok and "don't support buildings" in why

    def test_the_candidates_are_computed_not_listed(self):
        w = _boot()
        w.nation_gold["France"] = 20_000
        sites = _french_yard_candidates(w)
        assert len(sites) >= 2
        for name in sites:
            region = w.regions[name]
            assert region.controller == "France"
            assert name in N.mooring_provinces(w)
            assert region.region_type in ("capital", "major_city", "city")

    def test_the_cap_is_two_per_court(self, board):
        a, b, c = _french_yard_candidates(board)[:3]
        for site in (a, b):
            _refill(board)
            reply = _post(f"build a naval yard in {site}")
            assert reply.get("success"), reply.get("message")
        _refill(board)
        reply = _post(f"build a naval yard in {c}")
        assert not reply.get("success")
        assert "raised our 2 yards" in (reply.get("message") or "")
        assert N.raised_yards(board, "France") == sorted([a, b])

    def test_a_raised_yard_is_a_site_and_never_a_rate_or_a_port(self, board):
        rec = N.get_fleet(board, "France")
        rec["dockyards"] = []            # every authored yard lost
        refusal = N.check_build_fleet(board, "France")
        assert "A naval yard may be raised at" in refusal
        closure = N.closure_against(board, "Britain")
        ports = N.continental_ports_total(board)
        rate = N.build_rate(board, "France")
        site = _french_yard_candidates(board)[0]
        _refill(board)
        assert _post(f"build a naval yard in {site}").get("success")
        assert N.controlled_dockyards(board, "France") == []   # still rising
        events = _finish_works(board)
        assert N.controlled_dockyards(board, "France") == [site]
        assert rec["built_dockyards"] == [site]
        assert N.check_build_fleet(board, "France") is None
        assert N.build_rate(board, "France") == rate
        assert N.continental_ports_total(board) == ports
        assert N.closure_against(board, "Britain") == closure
        done = [e for e in events if e.get("building") == "naval_yard"]
        assert done and "the yards together still lay down" in done[0]["message"]

    def test_the_yard_serves_only_while_it_stands(self, board):
        site = _french_yard_candidates(board)[0]
        _refill(board)
        assert _post(f"build a naval yard in {site}").get("success")
        _finish_works(board)
        region = board.regions[site]
        assert site in N.controlled_dockyards(board, "France")
        apply_secure_effects(region)                     # damaged
        assert site not in N.all_dockyard_provinces(board)
        assert N.raised_yards(board, "France") == [site]  # still counts
        _refill(board)
        repaired = _post(f"repair naval yard in {site}")
        assert repaired.get("success"), repaired.get("message")
        assert site in N.controlled_dockyards(board, "France")
        apply_plunder_effects(board, region, "France")   # razed
        assert site not in N.all_dockyard_provinces(board)
        assert N.raised_yards(board, "France") == []     # the cap is freed

    def test_conquest_grants_the_raised_yard(self, board):
        site = _french_yard_candidates(board)[0]
        _refill(board)
        assert _post(f"build a naval yard in {site}").get("success")
        _finish_works(board)
        board.regions[site].controller = "Spain"
        board.invalidate_active_nations_cache()
        assert site in N.controlled_dockyards(board, "Spain")
        assert site not in N.controlled_dockyards(board, "France")

    def test_a_province_is_one_courts_yard(self):
        w = _boot()
        assert N.register_built_yard(w, "Artois", "France")
        assert N.register_built_yard(w, "Artois", "Spain")
        assert "Artois" not in N.get_fleet(w, "France").get("built_dockyards")
        assert N.get_fleet(w, "Spain")["built_dockyards"] == ["Artois"]
        assert not N.register_built_yard(w, "Cagliari", "Sardinia")

    def test_the_yard_rides_the_save(self, board):
        site = _french_yard_candidates(board)[0]
        _refill(board)
        assert _post(f"build a naval yard in {site}").get("success")
        _finish_works(board)
        with _quiet():
            loaded = WorldState.from_dict(board.to_dict())
        assert N.get_fleet(loaded, "France")["built_dockyards"] == [site]
        assert (N.controlled_dockyards(loaded, "France")
                == N.controlled_dockyards(board, "France"))

    def test_the_blockade_marks_a_raised_yard(self, board):
        assert N.is_blockaded(board, "France")
        site = _french_yard_candidates(board)[0]
        _refill(board)
        assert _post(f"build a naval yard in {site}").get("success")
        _finish_works(board)
        assert site in N.map_naval_overlay(board)["blockaded_ports"]
        assert site in N.nation_dockyards(board, "France")

    def test_the_region_panel_states_its_terms(self, board):
        site = _french_yard_candidates(board)[0]
        with _quiet():
            summary = board.get_game_state_summary()
        terms = summary["map_data"][site]["build_terms"]["naval_yard"]
        assert terms == {"cost": 1200, "turns": 4, "refusal": "",
                         "raised": 0, "cap": 2}
        assert "naval_yard" not in summary["map_data"]["Paris"]["build_terms"]
        board.nation_gold["France"] = 500
        with _quiet():
            summary = board.get_game_state_summary()
        short = summary["map_data"][site]["build_terms"]["naval_yard"]
        assert short["refusal"].startswith("Insufficient gold!")

    @pytest.mark.parametrize("phrase,site_index", [
        ("build a naval yard in {site}", 0),
        ("construct a dockyard at {site}", 1),
        ("build a shipyard in {site}", 0),
    ])
    def test_the_parser_reads_the_yard(self, board, phrase, site_index):
        site = _french_yard_candidates(board)[site_index]
        _refill(board)
        reply = _post(phrase.format(site=site))
        assert reply.get("success"), reply.get("message")
        rising = board.regions[site].building_under_construction or {}
        assert rising.get("type") == "naval_yard"

    def test_build_ships_still_lays_a_keel(self, board):
        ships = int(N.get_fleet(board, "France")["ships"])
        _refill(board)
        reply = _post("build ships")
        assert reply.get("success"), reply.get("message")
        assert int(N.get_fleet(board, "France")["ships"]) == ships + 1

    def test_the_desk_prices_the_yard(self, board):
        reply = _post("how much is a naval yard")
        assert "1,200 gold and 4 turns" in (reply.get("message") or "")

    def test_the_road_names_the_yard_where_none_is_held(self, board):
        N.get_fleet(board, "France")["dockyards"] = []
        site = N.naval_yard_sites(board, "France")[0][0]
        report = N.build_admiralty_report(board)
        chips = report["expedition_chips"]
        assert chips and chips[0]["command"] == f"build naval yard in {site}"
        assert chips[0]["enabled"] is True
        assert "a naval yard may be raised at" in \
            report["expedition_terms"][0]["detail"]
        lannes = board.get_marshal("Lannes")
        lannes.strength, lannes.location = 12000, "Paris"
        reply = _post("land Lannes in Munster")
        assert "A naval yard may be raised at" in (reply.get("message") or "")

    def test_the_lever_down_raises_no_yard(self, monkeypatch):
        w = _boot()
        w.nation_gold["France"] = 20_000
        site = _french_yard_candidates(w)[0]
        monkeypatch.setattr(N, "NAVAL_YARDS_CAN_BE_BUILT", False)
        ok, _why, _ = can_build(w, w.regions[site], "naval_yard", "France")
        assert not ok
        assert N.naval_yard_terms(w, w.regions[site], "France") is None
        assert N.naval_yard_sites(w, "France") == []


class TestTheAIRaisesAYard:
    """GR5: the same verb, price and gate as the player — P1.81."""

    def _spain_without_a_yard(self):
        w = _boot()
        N.get_fleet(w, "Spain")["dockyards"] = []
        w.nation_gold["Spain"] = 10_000
        assert w.is_at_war("Spain", "Britain")
        return w

    def test_a_navy_without_a_yard_raises_one(self):
        w = self._spain_without_a_yard()
        order = N.find_ai_naval_yard(w, "Spain", 10_000)
        lawful = [n for n, r in N.naval_yard_sites(w, "Spain") if not r]
        assert order == {"marshal": None, "action": "build",
                         "target": lawful[0], "building_type": "naval_yard",
                         "_acting_nation": "Spain"}

    def test_the_order_runs_through_the_shared_executor(self):
        w = self._spain_without_a_yard()
        order = N.find_ai_naval_yard(w, "Spain", 10_000)
        from backend.commands.executor import CommandExecutor
        with _quiet():
            result = CommandExecutor().execute(
                {"command": {"marshal": None, "action": "build",
                             "target": order["target"],
                             "building_type": "naval_yard",
                             "_acting_nation": "Spain", "type": "specific"}},
                {"world": w})
        assert result.get("success"), result.get("message")
        assert (w.regions[order["target"]].building_under_construction
                or {}).get("type") == "naval_yard"
        # Never a second yard while one is rising.
        assert N.find_ai_naval_yard(w, "Spain", 10_000) is None

    def test_the_rung_holds_its_hand(self):
        w = self._spain_without_a_yard()
        assert N.find_ai_naval_yard(w, "Spain", 1_000) is None      # poor
        # Ports only — with the gold for a site, so the crews test binds.
        w.nation_gold["Austria"] = 50_000
        assert any(not r for _n, r in N.naval_yard_sites(w, "Austria"))
        assert N.find_ai_naval_yard(w, "Austria", 50_000) is None
        boot = _boot()
        assert N.find_ai_naval_yard(boot, "Spain", 50_000) is None  # has yards
        with _quiet():
            set_diplomatic_state(w, "Spain", "Britain", "PEACE")
        if not w.get_nations_at_war_with("Spain"):
            assert N.find_ai_naval_yard(w, "Spain", 50_000) is None  # at peace

    def test_the_lever_down_silences_the_rung(self, monkeypatch):
        w = self._spain_without_a_yard()
        monkeypatch.setattr(N, "NAVAL_YARDS_CAN_BE_BUILT", False)
        assert N.find_ai_naval_yard(w, "Spain", 50_000) is None

    def test_the_rung_sits_after_the_keel_rung(self):
        import inspect
        from backend.ai.enemy_ai import EnemyAI
        src = inspect.getsource(EnemyAI._pick_admin_action)
        assert src.index("find_ai_build_fleet") < src.index(
            "find_ai_naval_yard") < src.index("find_ai_expedition")


# ═══════════════════════════════════════════════════════════════════════════
# SR5B-1 — a refused order keeps the standing order (found playing the arm)
# ═══════════════════════════════════════════════════════════════════════════

class TestARefusedOrderKeepsTheStandingOrder:
    """Soult marching on Lisbon; `Soult, attack Lisbon` refused "cannot
    reach"; the march was gone with no word (the strategic override cancels
    BEFORE the order runs). Lever `executor.A_REFUSED_ORDER_KEEPS_THE_
    STANDING_ORDER`."""

    def test_a_refused_attack_keeps_the_march(self, board):
        assert _post("Soult, march to Bordelais").get("success")
        soult = board.get_marshal("Soult")
        before = soult.strategic_order.to_dict()
        reply = _post("Soult, attack Lisbon")
        assert reply.get("success") is False
        assert soult.strategic_order is not None
        assert soult.strategic_order.to_dict() == before

    def test_a_refused_order_keeps_a_hold_and_its_ground(self, board):
        assert _post("Ney, hold Rhineland").get("success")
        ney = board.get_marshal("Ney")
        assert ney.strategic_order.command_type == "HOLD"
        # The per-turn order pass puts him in place (issuance does not);
        # staged here so the pin binds the hold's ground, not two Falses.
        ney.holding_position, ney.hold_region = True, "Rhineland"
        held = (True, "Rhineland")
        reply = _post("Ney, attack Lisbon")
        assert reply.get("success") is False
        assert ney.strategic_order is not None
        assert ney.strategic_order.command_type == "HOLD"
        assert (ney.holding_position, ney.hold_region) == held

    def test_the_orders_own_question_comes_back_with_it(self, board):
        """Asked of the executor itself: on the typed road the pending
        question answers the next line naming the marshal first (main.py's
        interrupt route), so it never reaches the override at all."""
        assert _post("Soult, march to Bordelais").get("success")
        soult = board.get_marshal("Soult")
        question = {"interrupt_type": "cannon_fire", "marshal": "Soult",
                    "location": "Swabia"}
        soult.pending_interrupt = dict(question)
        with _quiet():
            result = M.executor.execute(
                {"command": {"marshal": "Soult", "action": "attack",
                             "target": "Lisbon", "type": "specific",
                             "raw_command": "Soult, attack Lisbon"}},
                M.game_state)
        assert result.get("success") is False
        assert soult.strategic_order is not None
        assert soult.pending_interrupt == question

    def test_an_order_carried_out_still_replaces_the_standing_order(self, board):
        assert _post("Ney, hold Rhineland").get("success")
        ney = board.get_marshal("Ney")
        reply = _post("Ney, attack Mack")
        events = reply.get("events") or []
        fought = any(isinstance(e, dict) and e.get("type") == "battle"
                     for e in events) or reply.get("battle_result")
        assert fought, reply.get("message")
        assert ney.strategic_order is None
        assert not ney.holding_position

    def test_the_lever_down_loses_the_march(self, board, monkeypatch):
        from backend.commands import executor as EX
        monkeypatch.setattr(EX, "A_REFUSED_ORDER_KEEPS_THE_STANDING_ORDER",
                            False)
        assert _post("Soult, march to Bordelais").get("success")
        soult = board.get_marshal("Soult")
        assert _post("Soult, attack Lisbon").get("success") is False
        assert soult.strategic_order is None


# ═══════════════════════════════════════════════════════════════════════════
# The records
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRecords:

    def test_privateers_are_struck(self):
        spec = (DOCS / "NAVAL_SPEC.md").read_text(encoding="utf-8")
        row = next(line for line in spec.splitlines()
                   if line.startswith("| ~~NV-D3~~"))
        assert "STRUCK" in row and "September 28, 2026" in row

    def test_the_yard_is_landed_in_the_spec(self):
        spec = (DOCS / "NAVAL_SPEC.md").read_text(encoding="utf-8")
        row = next(line for line in spec.splitlines()
                   if line.startswith("| ~~NV-D9~~"))
        assert "BUILT" in row and "SR-5b" in row

    def test_the_systems_reference_carries_the_rules(self):
        ref = (DOCS / "SYSTEMS_REFERENCE.md").read_text(encoding="utf-8")
        assert re.search(r"^## 77\. ", ref, re.MULTILINE)

    def test_aar_d7_is_closed(self):
        rows = (DOCS / "DESIGN_REFINEMENT.md").read_text(encoding="utf-8")
        row = next(line for line in rows.splitlines()
                   if line.startswith("| **AAR-D7**")
                   or line.startswith("| ~~**AAR-D7**~~"))
        assert "BUILT" in row and "SR-5b" in row
