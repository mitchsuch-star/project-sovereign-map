"""Row FUN, Session FUN-2 "conquest with a cost" — its behaviour test
(November 26, 2026; `docs/GAMEPLAY_REVIEW_2026_11_25.md` §1.3, §5;
`SYSTEMS_REFERENCE.md` §240; the rules in `backend/game_logic/fear.py`).

The user's second play: "I beat Austria in the first war by eliminating them and
got to keep all the land, then a coalition of every country formed later." FUN-2
gives each court its own fear of France; only the afraid with a border or a stake
join a league, and a league needs three; a declaration angers the target and its
friends only; the order card warns before a capture that erases a court; land
taken by arms must be held, or it rises. Every rule is armed by the 1805
campaign's own `fear` block — an unarmed world keeps the old rules byte for byte.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from backend.game_logic import coalition as CO
from backend.game_logic import fear as F
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parent.parent
SCENARIO = os.path.join("godot-client", "project-sovereign", "assets", "maps", "europe_1805.json")
CLIENT = REPO / "godot-client" / "project-sovereign"
AUSTRIA_ORDER = ["Bohemia", "Carniola", "Moravia", "Hungary", "Croatia", "Tyrol", "Vienna"]


@pytest.fixture(scope="module")
def _booted():
    return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(_booted):
    return WorldState.from_dict(_booted.to_dict())


def _erase_austria(world, upto=None):
    for name in AUSTRIA_ORDER[:upto]:
        world.capture_region(name, "France")


def _clear_austrian_armies(world):
    """The rising tests read the count alone: no hostile army drains the ground."""
    for m in world.marshals.values():
        if m.nation == "Austria":
            m.location = "Vienna"
            m.strength = 0


def _turn(world):
    """The two halves of `advance_turn` the rising reads, nothing else."""
    world.process_stability_growth()
    return F.tick_risings(world, list(world._rising_due))


# ═══════════════════════════════════════════════════════════════════════
# 1. The store — armed by the campaign, nothing elsewhere
# ═══════════════════════════════════════════════════════════════════════

class TestTheStore:

    def test_the_1805_campaign_arms_the_rules(self, world):
        assert world.fear_rules == {"join": 50, "leave": 25, "fade": 2, "rises": 4}
        assert world.court_grudges == {}
        assert F.armed(world) and F.chooses(world)

    def test_an_unarmed_world_writes_nothing(self):
        bare = WorldState(player_nation="France")
        assert bare.fear_rules is None and not F.chooses(bare)
        data = bare.to_dict()
        assert "court_grudges" not in data and "fear_rules" not in data
        assert F.league_min(bare) == 2

    def test_a_save_carries_it_whole(self, world):
        world.court_grudges = {"Saxony": 56}
        world.fear_book["faded"]["Russia"] = 3
        back = WorldState.from_dict(world.to_dict())
        assert back.court_grudges == {"Saxony": 56}
        assert back.fear_rules == world.fear_rules
        assert back.fear_book["faded"] == {"Russia": 3}

    def test_a_save_without_the_rules_gains_them(self, world):
        world.fear_rules = None
        assert F.backfill(world, {"fear": {"join": 50, "leave": 25, "fade": 2, "rises": 4}})
        assert F.chooses(world)

    def test_the_block_is_clamped(self):
        assert F.clean_block({"join": 999, "leave": 999, "fade": 0, "rises": 1}) == {
            "join": 90, "leave": 80, "fade": 1, "rises": 2}
        assert F.clean_block("nope") is None


# ═══════════════════════════════════════════════════════════════════════
# 2. The write — 8 x nearness x stake, the capital x3
# ═══════════════════════════════════════════════════════════════════════

class TestTheWrite:

    def test_a_province_frightens_the_loser_and_its_neighbours_most(self, world):
        d = F.capture_deltas(world, "Bohemia", "Austria", "France")
        assert d["Saxony"] == 8 and d["Russia"] == 8 and d["Ottoman"] == 8   # Austria's neighbours
        assert d["Prussia"] == 4                                              # one court between
        assert d["Britain"] == 2                                              # farther
        assert d["Austria"] == 16                                             # it lost it: x2
        assert "France" not in d and "KingdomOfItaly" not in d                # France's house

    def test_a_capital_counts_three_times(self, world):
        d = F.capture_deltas(world, "Vienna", "Austria", "France")
        assert d["Saxony"] == 24 and d["Prussia"] == 12 and d["Britain"] == 6
        assert d["Austria"] == 48

    def test_a_court_that_wants_it_counts_twice(self, world):
        assert "Tyrol" in F._design_regions(world, "Bavaria")
        assert F.capture_deltas(world, "Tyrol", "Austria", "France")["Bavaria"] == 16

    def test_nearness_holds_while_the_loser_shrinks(self, world):
        """Russia borders Austria's lands though France's conquests come
        between it and what Austria still holds (the homeland reading)."""
        _erase_austria(world, upto=4)
        assert F.nearness(world, "Russia", "Austria") == 1.0

    def test_taking_back_our_own_soil_frightens_nobody(self, world):
        home = (world.nation_starting_regions.get("France") or [])[0]
        world.regions[home].controller = "Austria"
        world.invalidate_active_nations_cache()
        assert F.capture_deltas(world, home, "Austria", "France") == {}
        world.capture_region(home, "France")
        assert world.court_grudges == {}

    def test_the_capture_writes_it_once(self, world):
        expected = F.capture_deltas(world, "Bohemia", "Austria", "France")
        world.capture_region("Bohemia", "France")
        assert world.court_grudges == expected
        assert world.fear_book["causes"]["Saxony"][-1]["region"] == "Bohemia"

    def test_a_computer_courts_capture_frightens_nobody_of_france(self, world):
        assert F.capture_deltas(world, "Bohemia", "Austria", "Prussia") == {}

    def test_fear_fades_two_a_turn(self, world):
        world.court_grudges = {"Saxony": 10, "Hesse": 1}
        F.fade(world)
        assert world.court_grudges == {"Saxony": 8}


# ═══════════════════════════════════════════════════════════════════════
# 3. The league — the afraid with a border or a stake, three of them
# ═══════════════════════════════════════════════════════════════════════

class TestTheLeague:

    def test_erasing_austria_frightens_its_neighbours_past_the_line(self, world):
        _erase_austria(world)
        for court in ("Saxony", "Ottoman", "Russia"):
            assert F.fear_of(world, court) > 50, (court, F.fear_of(world, court))
        assert CO.qualifies_for_coalition("Saxony", world)
        assert CO.qualifies_for_coalition("Ottoman", world)
        assert not CO.qualifies_for_coalition("Bavaria", world)     # our ally
        assert not CO.qualifies_for_coalition("Prussia", world)     # 36: under the line

    def test_fear_without_a_border_or_a_stake_never_joins(self, world):
        assert not F.border_or_stake(world, "Naples")
        world.court_grudges = {"Naples": 90}
        assert not CO.qualifies_for_coalition("Naples", world)
        assert F.why_out(world, "Naples") == "she neither borders us nor lost or wants land we hold"

    def test_an_ally_never_joins(self, world):
        world.court_grudges = {"Spain": 90}
        assert world.are_allies("France", "Spain")
        assert not CO.qualifies_for_coalition("Spain", world)

    def test_relations_no_longer_choose_the_league(self, world):
        world.modify_nation_relation("France", "Prussia", -90)
        assert not CO.qualifies_for_coalition("Prussia", world)

    def test_a_truce_still_binds(self, world):
        _erase_austria(world)
        key = world._make_diplo_key("France", "Saxony")
        world.armistice_cooldowns[key] = 5
        assert not CO.qualifies_for_coalition("Saxony", world)
        assert CO.league_excluded("Saxony", world)

    def test_a_league_needs_three(self, world):
        assert F.league_min(world) == 3
        world.active_coalition = None
        for court in ("Britain", "Russia", "Austria"):   # nobody already at war with us
            world.diplomatic_states[world._make_diplo_key("France", court)] = "PEACE"
        world.court_grudges = {"Saxony": 60, "Ottoman": 60}
        _erase_austria(world, upto=2)       # Bohemia, Carniola: borders with both
        qualifying = [c for c in ("Saxony", "Ottoman") if CO.qualifies_for_coalition(c, world)]
        assert qualifying == ["Saxony", "Ottoman"]
        assert not CO.a_league_the_brew_could_form(world, qualifying, "France")
        assert not CO.form_coalition(qualifying, world).get("success")

    def test_the_old_rule_still_holds_two_in_an_unarmed_world(self, world):
        world.fear_rules = None
        assert F.league_min(world) == 2

    def test_a_standing_league_takes_the_afraid(self, world):
        _erase_austria(world)
        assert world.active_coalition and "Saxony" not in world.active_coalition["members"]
        events = CO.process_coalition_turn(world)
        members = world.active_coalition["members"]
        assert "Saxony" in members and "Ottoman" in members
        assert set(world.active_coalition["by_fear"]) >= {"Saxony", "Ottoman"}
        joined = [e["message"] for e in events if e.get("type") == "coalition_member_joined"]
        assert any(m.startswith("Saxony joins the Third Coalition against us") for m in joined)
        assert any(m.startswith("The Ottoman Empire joins") for m in joined)

    def test_the_boot_league_keeps_its_own_members(self, world):
        """The Third Coalition's members are at war for their own reasons —
        none joined by fear, so none fades home."""
        assert "by_fear" not in world.active_coalition
        CO.process_coalition_turn(world)
        assert {"Britain", "Russia"} <= set(world.active_coalition["members"])

    def test_the_faded_go_home_and_take_our_peace(self, world):
        _erase_austria(world)
        CO.process_coalition_turn(world)
        world.court_grudges["Saxony"] = 20
        events = F.faded_home(world)
        assert "Saxony" not in world.active_coalition["members"]
        assert any("Saxony leaves the Third Coalition" in e["message"] for e in events)
        # said once: the league's plain "has left the coalition" line does not follow it
        left = [e["message"] for e in events if e.get("type") == "coalition_member_left"]
        assert len(left) == 1 and left[0].startswith("Saxony leaves the Third Coalition")
        assert world.is_at_war("France", "Saxony")                 # France's word ends the war
        assert F.peace_readiness(world, "France", "Saxony") == F.PEACE_READINESS
        from backend.game_logic.diplomacy import calculate_acceptance
        result = calculate_acceptance({"type": "peace", "proposer_nation": "France",
                                       "target_nation": "Saxony"}, world)
        assert result["components"].get("fear_faded_mod") == F.PEACE_READINESS

    def test_at_war_courts_join_a_forming_league_only_with_a_border_or_stake(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Naples", "WAR", reason="fun2-test")
        assert world.is_at_war("France", "Naples") and not F.border_or_stake(world, "Naples")
        at_war = CO._league_at_war_members(world, "France")
        assert "Naples" not in at_war                      # at war, no border, no stake
        assert "Britain" in at_war                         # the Channel's sea link is a border
        world.fear_rules = None
        assert "Naples" in CO._league_at_war_members(world, "France")   # the old rule

    def test_a_congress_refuser_is_never_booked_as_joining_by_fear(self, world, monkeypatch):
        from backend.game_logic import congress
        monkeypatch.setattr(congress, "refuser_qualifies", lambda w, n, t: n == "Prussia")
        _erase_austria(world)
        world.court_grudges.pop("Prussia", None)                     # no fear at all
        assert CO.qualifies_for_coalition("Prussia", world)          # by the Congress, not fear
        CO.process_coalition_turn(world)
        league = world.active_coalition
        assert "Prussia" in league["members"]
        assert "Prussia" not in league.get("by_fear", [])
        F.faded_home(world)                                         # fear 0: stamped, she would leave
        assert "Prussia" in world.active_coalition["members"]       # she never "fades home"
        assert F.peace_readiness(world, "France", "Prussia") == 0

    def test_with_the_fear_seam_down_relations_choose_again(self, world, monkeypatch):
        monkeypatch.setattr(F, "fear_chooses_the_league", lambda: False)
        world.modify_nation_relation("France", "Prussia", -90)
        assert CO.qualifies_for_coalition("Prussia", world)
        assert F.league_min(world) == 2
        assert F.capture_deltas(world, "Bohemia", "Austria", "France") == {}


# ═══════════════════════════════════════════════════════════════════════
# 4. The declaration — the target and its friends
# ═══════════════════════════════════════════════════════════════════════

class TestTheDeclaration:

    def test_a_declaration_angers_the_target_and_its_friends(self, world):
        from backend.game_logic.diplomacy import declaration_angers, declare_war
        friends = declaration_angers(world, "France", "Prussia")
        assert set(friends) == {"Russia", "Sweden", "Saxony", "Hanover", "Hesse"}
        before = {n: world.nation_relations.get(world._make_diplo_key("France", n), 0)
                  for n in world.get_active_nations() if n != "France"}
        declare_war(world, "France", "Prussia")
        after = {n: world.nation_relations.get(world._make_diplo_key("France", n), 0)
                 for n in before}
        assert after["Spain"] == before["Spain"] and after["Naples"] == before["Naples"]
        assert after["Saxony"] < before["Saxony"]

    def test_an_unarmed_world_angers_every_court(self, world):
        from backend.game_logic.diplomacy import declaration_angers
        world.fear_rules = None
        assert set(declaration_angers(world, "France", "Prussia")) == (
            set(world.get_active_nations()) - {"France", "Prussia"})

    def test_the_clause_names_whose_friends_pay(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(15, "France", aggressor="Russia", friends_of="Prussia") == (
            "Russia's relations with Prussia's friends and neighbours, France's included, fall 15")
        assert "every court" in declaration_cost_clause(15, "France", aggressor="Russia")


# ═══════════════════════════════════════════════════════════════════════
# 5. The card — "Erase this country?"
# ═══════════════════════════════════════════════════════════════════════

class TestTheCard:

    def test_the_last_province_says_it_erases_and_who_would_march(self, world):
        _erase_austria(world, upto=6)
        w = F.capture_warning(world, "Vienna", "France")
        assert w["last"] and w["court"] == "Austria"
        assert w["line"].startswith("Taking Vienna erases Austria.")
        assert "Saxony" in w["joiners"]
        assert "the Third Coalition against us at the end of this turn" in w["line"]
        assert w["peace_label"] == "Offer Austria peace now"
        assert w["short"].startswith("erases Austria")

    def test_an_attack_says_if(self, world):
        _erase_austria(world, upto=6)
        w = F.capture_warning(world, "Vienna", "France", attack=True)
        assert w["line"].startswith("If Vienna falls, it erases Austria.")

    def test_a_crossing_says_who_would_fear_france(self, world):
        """Never "the fear of Saxony" (read as Saxony's fearsomeness)."""
        world.court_grudges = {"Saxony": 46}
        w = F.capture_warning(world, "Bohemia", "France")
        assert w["line"] == ("Taking Bohemia would make Saxony fear France past 50, enough to join "
                             "the Third Coalition against us at the end of this turn.")
        assert "the fear of" not in w["line"] and "league" not in w["line"]

    def test_a_vassal_holders_last_province_is_no_erasure(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        world.vassals["Naples"] = {"lord": "Russia", "loyalty": 60, "autonomy": 2}
        set_diplomatic_state(world, "France", "Naples", "WAR", reason="fun2-test")
        w = F.capture_warning(world, "Naples", "France")
        assert w is None or not w["last"]

    def test_no_news_no_warning(self, world):
        assert F.capture_warning(world, "Bohemia", "France") is None

    def test_the_quote_carries_it_and_the_card_opens(self, world):
        from types import SimpleNamespace
        from backend.commands.order_quotes import with_fear
        _erase_austria(world, upto=6)
        q = with_fear(world, SimpleNamespace(nation="France"), {"ok": True, "confirm": False}, "Vienna")
        assert q["erase"]["last"] and q["confirm"] is True
        refused = with_fear(world, SimpleNamespace(nation="France"), {"ok": False}, "Vienna")
        assert "erase" not in refused

    def test_an_unarmed_world_never_warns(self, world):
        world.fear_rules = None
        _erase_austria(world, upto=6)
        assert F.capture_warning(world, "Vienna", "France") is None


# ═══════════════════════════════════════════════════════════════════════
# 6. The rising — land taken by arms must be held
# ═══════════════════════════════════════════════════════════════════════

class TestTheRising:

    def test_an_unheld_conquest_does_not_settle_and_rises_after_four_turns(self, world):
        _clear_austrian_armies(world)
        world.capture_region("Tyrol", "France")
        tyrol = world.regions["Tyrol"]
        seen = []
        for _ in range(4):
            seen.append(F.rises_in(world, tyrol))
            events = _turn(world)
        assert seen == [4, 3, 2, 1]
        assert tyrol.controller == "Austria" and tyrol.stability == F.RISEN_STABILITY
        assert tyrol.garrison_strength == F.RISEN_GARRISON
        assert any(e["type"] == "province_rose" for e in events)

    def test_troops_hold_it(self, world):
        _clear_austrian_armies(world)
        world.capture_region("Tyrol", "France")
        tyrol = world.regions["Tyrol"]
        tyrol.garrison_strength, tyrol.garrison_detachment = 3000, True
        for _ in range(5):
            _turn(world)
        assert tyrol.controller == "France" and tyrol.unheld_turns == 0
        assert tyrol.stability > 25

    def test_the_morning_warns_a_turn_before(self, world):
        _clear_austrian_armies(world)
        world.capture_region("Tyrol", "France")
        events = []
        for _ in range(3):
            events = _turn(world)
        restless = [e for e in events if e["type"] == "province_restless"]
        assert restless and restless[0]["message"].startswith("Tyrol will rise next turn")

    def test_an_erased_court_rises_again(self, world):
        _clear_austrian_armies(world)
        _erase_austria(world)
        assert "Austria" not in world.get_active_nations()
        for name in AUSTRIA_ORDER:                      # every province held but the Tyrol
            if name != "Tyrol":
                region = world.regions[name]
                region.garrison_strength, region.garrison_detachment = 3000, True
        events = []
        for _ in range(4):
            events += _turn(world)
        rose = [e for e in events if e["type"] == "province_rose"]
        assert rose and rose[0]["reborn"] and rose[0]["court"] == "Austria"
        assert "Austria" in world.get_active_nations()

    def test_the_province_window_reads_the_count(self, world):
        _clear_austrian_armies(world)
        world.capture_region("Tyrol", "France")
        entry = world.get_filtered_game_state_summary()["map_data"]["Tyrol"]
        assert entry["rises_in"] == 4 and entry["rises_to"] == "Austria"
        assert "rises_in" not in world.get_filtered_game_state_summary()["map_data"]["Paris"]

    def test_a_court_risen_again_can_fall_again(self, world):
        _clear_austrian_armies(world)
        _erase_austria(world)
        assert "Austria" in (getattr(world, "_eliminated_teardown_done", None) or set())
        for name in AUSTRIA_ORDER:
            if name != "Tyrol":
                world.regions[name].garrison_strength = 3000
                world.regions[name].garrison_detachment = True
        for _ in range(4):
            _turn(world)
        assert world.regions["Tyrol"].controller == "Austria"
        assert "Austria" not in (getattr(world, "_eliminated_teardown_done", None) or set())

    def test_a_vassals_conquest_never_rises(self, world):
        world.capture_region("Tyrol", "KingdomOfItaly")
        assert not F.rising_applies(world, world.regions["Tyrol"])

    def test_an_unarmed_world_settles_as_before(self, world):
        world.fear_rules = None
        _clear_austrian_armies(world)
        world.capture_region("Tyrol", "France")
        world.process_stability_growth()
        assert world.regions["Tyrol"].stability == 30 and world.regions["Tyrol"].unheld_turns == 0


# ═══════════════════════════════════════════════════════════════════════
# 7. Recruits wait for settled land
# ═══════════════════════════════════════════════════════════════════════

class TestTheMirror:
    """FUN2-1: the reckless charge's capture, as the chokepoint takes it."""

    def test_the_charge_takes_the_province_hostile_and_frightens(self, world):
        region = world.regions["Bohemia"]
        prior = dict((world.province_title or {}).get("Bohemia") or {})
        deltas = F.capture_deltas(world, "Bohemia", "Austria", "France")
        region.controller = "France"
        world.invalidate_active_nations_cache()
        region.garrison_strength = 5000
        threat = int(world.threat_level)
        F.mirror_capture(world, "Bohemia", "Austria", "France", "", prior, deltas)
        assert region.stability == 25 and region.unheld_turns == 0
        assert region.garrison_strength == 0
        assert int(world.threat_level) == min(100, threat + 2)
        assert world.court_grudges == deltas

    def test_down_or_unarmed_the_mirror_is_as_it_was(self, world, monkeypatch):
        monkeypatch.setattr(F, "the_charge_takes_as_the_chokepoint_does", lambda: False)
        region = world.regions["Bohemia"]
        region.controller = "France"
        F.mirror_capture(world, "Bohemia", "Austria", "France", "", {}, {"Saxony": 8})
        assert region.stability == 100 and world.court_grudges == {}


class TestTheRecruits:

    def _thin(self, world):
        keep = set((world.nation_starting_regions.get("France") or [])[:2])
        for name, region in world.regions.items():
            if region.controller == "France" and name not in keep:
                region.controller = "Spain"
        world.invalidate_active_nations_cache()

    def test_a_hostile_conquest_adds_no_cavalry(self, world):
        self._thin(world)
        before = world.get_manpower_regen_rates("France")["cavalry"]
        world.capture_region("Hungary", "France")            # plains, stability 25
        assert world.get_manpower_regen_rates("France")["cavalry"] == before
        world.regions["Hungary"].stability = 60              # Settling
        assert world.get_manpower_regen_rates("France")["cavalry"] > before

    def test_an_unarmed_world_counts_it_at_once(self, world):
        world.fear_rules = None
        self._thin(world)
        before = world.get_manpower_regen_rates("France")["cavalry"]
        world.capture_region("Hungary", "France")
        assert world.get_manpower_regen_rates("France")["cavalry"] > before


# ═══════════════════════════════════════════════════════════════════════
# 8. The surfaces — the ledger, the map, the log, the client
# ═══════════════════════════════════════════════════════════════════════

class TestTheSurfaces:

    def test_the_ledger_carries_who_fears_you(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        _erase_austria(world, upto=3)
        boe = build_diplomatic_ledger(world)["balance_of_europe"]
        rows = boe["fear_rows"]
        assert rows and rows[0]["fear"] >= rows[-1]["fear"]
        assert all(isinstance(r["fear"], int) for r in rows)
        assert boe["fear_line"] == 50
        assert "passes 50" in boe["fear_footer"] and "needs 3 countries" in boe["fear_footer"]
        # the blind reading (Nov 26): "unless … or …" — either reason keeps a country out
        assert "unless it is our ally, our vassal or under truce with us, or it neither" in boe["fear_footer"]

    def test_the_map_mode_reads_court_fear(self, world):
        _erase_austria(world, upto=2)
        summary = world.get_filtered_game_state_summary()
        assert summary["fear_line"] == 50 and summary["court_fear"]["Saxony"] == 16
        assert set(summary["fear_house"]) == {"France", "Holland", "KingdomOfItaly", "Switzerland"}
        assert not (set(summary["court_fear"]) & set(summary["fear_house"]))

    def test_the_league_rows_speak_in_fear(self, world):
        world.active_coalition = None
        rows = CO.league_rows(world)
        assert rows and all("fear of France" in r["text"] for r in rows)

    def test_the_log_tells_a_rising_and_a_join(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        assert {"province_rose", "coalition_member_joined"} <= CAMPAIGN_LOG_TYPES
        rose = format_event_oneliner({"type": "province_rose", "region": "Tyrol",
                                      "target_nation": "Austria", "nation": "France"})
        assert rose == "Tyrol rose against us and went back to Austria."
        joined = format_event_oneliner({"type": "coalition_member_joined", "nation": "Ottoman",
                                        "coalition": "Third Coalition"})
        assert joined.startswith("The Ottoman Empire joined the Third Coalition against us")

    def test_the_card_draws_the_warning_and_the_peace_button(self):
        card = (CLIENT / "scripts" / "order_confirm_card.gd").read_text(encoding="utf-8")
        assert "func _erase_lines(q: Dictionary)" in card and '"peace:" + court' in card
        assert "signal peace_requested(nation: String)" in card
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert "order_card.peace_requested.connect(_on_order_card_peace)" in main
        assert '"fear": "Who fears you"' in main

    def test_the_map_has_the_fear_mode(self):
        base = (CLIENT / "scenes" / "map_renderer_base.gd").read_text(encoding="utf-8")
        assert 'MAP_FILL_MODE_ORDER: Array = ["blended", "political", "terrain", "fear"]' in base
        assert "func update_court_fear(" in base and "func fear_color(" in base

    def test_the_province_window_and_the_ledger_say_it(self):
        panel = (CLIENT / "scripts" / "region_panel.gd").read_text(encoding="utf-8")
        assert "static func rising_line(data: Dictionary)" in panel
        # the real-client press (Nov 27): it leads, with the figures, before ACTIONS
        assert "rising_lead = rising_line(data)" in panel
        assert "+ folded_facts + rising_lead + bbcode.substr(actions_at)" in panel
        ledger = (CLIENT / "scripts" / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert "WHO FEARS YOU" in ledger and "func _fear_block(" in ledger

    def test_the_old_rules_texts_say_the_fear_rule_on_the_armed_board(self, world):
        """The review's gap: the s14h / iq3 / vp2 pins now read these surfaces on an
        unarmed board; on the 1805 campaign each says the rule that holds there."""
        from backend.game_logic.instruments import (
            buyoff_league_clause, guarantee_honour_cost_clause, licensed_war_cost_clause)
        assert "does not change her fear of France" in buyoff_league_clause(-20, world=world)
        assert "with its friends and neighbours" in guarantee_honour_cost_clause(world=world)
        sponsorship = licensed_war_cost_clause(world, "France", "Prussia", "Hanover")
        assert "Hanover's friends and neighbours" in sponsorship and "every court" not in sponsorship
        world.fear_rules = None
        assert "every court" in licensed_war_cost_clause(world, "France", "Prussia", "Hanover")
        assert "with every other" in guarantee_honour_cost_clause(world=world)

    def test_berthier_says_the_fear_rule_on_the_league_headlines(self, world):
        from backend.game_logic import dispatch as D
        for cls in ("league_joins", "league_paid"):
            assert D._pick_berthier_note(world, "France", [], {}, cls) == D._FEAR_LEAGUE_NOTES[cls]
        world.fear_rules = None
        assert D._pick_berthier_note(world, "France", [], {}, "league_joins") == (
            D._HEADLINE_BERTHIER_NOTES["league_joins"])

    def test_the_armed_peaces_levers_say_the_fear_rule(self, world, monkeypatch):
        from backend.game_logic import coalition as CO_mod
        from backend.game_logic.diplomatic_advisory import armed_peace_war_room_lines
        monkeypatch.setattr(CO_mod, "armed_peace_reading", lambda w, ahead=0: {
            "holds": True, "hegemon": "France", "share": 0.4, "watch": 45, "gate": 60,
            "quiet_turns": 3, "fuse_turns_left": 17, "courts": []})
        levers = " ".join(armed_peace_war_room_lines(world))
        assert "whose fear of France stays at 50 or under" in levers and "-10" not in levers

    def test_the_codex_says_it_in_plain_words(self):
        codex = (CLIENT / "scripts" / "codex_terms.gd").read_text(encoding="utf-8")
        assert '["Fear", "Each country\'s own fear of France' in codex
        assert "A country whose fear passes 50 joins — unless it is your ally" in codex
        assert "relations below -10" not in codex


# ═══════════════════════════════════════════════════════════════════════
# 9. The seams — one a rule, all up
# ═══════════════════════════════════════════════════════════════════════

class TestTheShippedApp:
    """The second repair workflow's review: the front page's pins now read an unarmed board,
    so the shipped app's own endpoints are read here on the armed one."""

    def test_the_endpoints_carry_the_fear_on_the_armed_board(self, world, monkeypatch):
        import backend.main as M
        from fastapi.testclient import TestClient
        _erase_austria(world, upto=3)
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setitem(M.game_state, "world", world)
        client = TestClient(M.app)
        led = client.get("/diplomatic_ledger").json()
        boe = led.get("balance_of_europe") or (led.get("ledger") or {}).get("balance_of_europe") or {}
        assert boe.get("fear_rows") and boe.get("fear_line") == 50
        assert all(isinstance(r["fear"], int) for r in boe["fear_rows"])
        state = client.get("/status").json()["game_state"]
        assert state["court_fear"]["Saxony"] >= 16 and state["fear_line"] == 50
        assert state["map_data"]["Bohemia"]["stability_label"] == "Hostile"
        assert client.get("/dispatch").status_code == 200

    def _board(self, world, monkeypatch):
        """Austria down to Vienna, Mack standing in it, Davout next door."""
        import backend.main as M
        from fastapi.testclient import TestClient
        _erase_austria(world, upto=6)
        world.marshals["Mack"].location = "Vienna"
        world.marshals["Davout"].location = "Moravia"
        world.calculate_visibility()
        monkeypatch.setattr(M, "world", world)
        monkeypatch.setitem(M.game_state, "world", world)
        return TestClient(M.app)

    def test_a_march_onto_a_defended_province_says_its_price(self, world, monkeypatch):
        """The real-client press (Nov 27): with Mack in Vienna the march card offers
        "Attack Mack instead", a chip that sends the battle at once with no card of
        its own — so the march card says what Vienna's fall would cost, first."""
        client = self._board(world, monkeypatch)
        q = client.get("/march_quotes", params={"marshal": "Davout", "dest": "Vienna"}).json()["quote"]
        assert (q.get("ground") or {}).get("code") == "enemy_corps"
        assert q["erase"]["line"].startswith("If Vienna falls, it erases Austria.")
        assert q["confirm"] is True and q["erase"]["court"] == "Austria"

    def test_the_province_window_says_its_price(self, world, monkeypatch):
        """The province window's march and attack chips send at once too: the panel's
        one GET carries the same warning, drawn above them with the peace button."""
        client = self._board(world, monkeypatch)
        quoted = client.get("/march_quotes", params={"region": "Vienna"}).json()
        assert quoted["erase"]["line"].startswith("If Vienna falls, it erases Austria.")
        assert quoted["erase"]["peace_label"] == "Offer Austria peace now"
        # a province of our own is no news
        assert "erase" not in client.get("/march_quotes", params={"region": "Moravia"}).json()

    def test_the_map_tooltip_counts_the_rising_too(self):
        """The real-client press (Nov 27): the hover said "Hostile" and nothing of
        the count — the Descent camp's count is on both, so the rising is too."""
        src = (CLIENT / "scenes" / "map_renderer_base.gd").read_text(encoding="utf-8")
        assert 'var rises_in := int(data.get("rises_in", 0))' in src
        assert '"No troops here: it rises %s%s"' in src

    def test_the_province_window_draws_it_with_the_peace_button(self):
        panel = (CLIENT / "scripts" / "region_panel.gd").read_text(encoding="utf-8")
        main = (CLIENT / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert "static func erase_lines(erase) -> String:" in panel
        assert 'out = erase_lines(_quotes.get("erase", null)) + out' in panel
        assert 'meta_str.begins_with("peace:")' in panel and "peace_requested.emit(peace_court)" in panel
        assert "region_panel.peace_requested.connect(_on_region_peace_requested)" in main


class TestTheSeams:

    def test_every_seam_is_up(self):
        from tests._fun2_seams import SEAMS
        assert len(SEAMS) == 7
        for _row, module, name in SEAMS:
            assert getattr(module, name)() is True
