"""Tier 6 — session C (`DYNAMISM_SPEC.md` §5; the Tier-6 gate record §5a,
ruled November 10, 2026 in Plan Mode at the session's head under the user's
delegation — "rule yourself be rigorous make it good"; §2b session C).
One file for the Awakening's first half: DY-4, three rules behind their own
seams (`tests/_t3_seams.py` rows T6-STIR, T6-ULCER, T6-LETTERS).

THE STORE AND THE SCALAR (`backend/game_logic/awakening.py`, seam
`the_people_stir`): a PER-COURT scalar 0–100 (Q2) inside
`world.moments["awakening"]` — the T5 precedent — armed by the scenario's
top-level `awakening` block (the two thresholds authored, validator-clamped);
every court of the boot roster carries it, eliminated ones and the player's
house included; the occupied-home count is DERIVED once a turn off the boot
homeland against the holders' HOUSES (§5a C1 — a maintained counter would
drift on the first treaty; C2 — a client's soil under its lord is home);
the bands +1/+2/+3, the cool −1, the lump −10 on home rule; the event
writes at their ONE sites (a dictated peace by rank, the sovereign captured,
a client squeezed); the beats — one `awakening` log row per phase crossing
(the census 183 → 184) and a HIGH dispatch line, in words.

THE ULCER (seam `the_ulcer_bleeds`): an occupier's supply cap ×0.75 on soil
whose boot owner stands at `risen` — France's too (Q3); the owner's own army
never bleeds, nobody bleeds on home-held soil, an ally beside the occupier
bleeds; the doctrine's step stays the multiplier's last.

THE LETTERS (seam `the_people_write`, row DY-4 of `affairs.SINCE_ROWS`): The
People Stir and The Ulcer ride the affairs deck in lockstep (the scenario and
the fixture), their predicates the scalar's own thresholds; the `awakening`
op — the twelfth — cools a people on an Accept, quoted in words.
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
from backend.game_logic import affairs as AF  # noqa: E402
from backend.game_logic import awakening as AW  # noqa: E402
from backend.game_logic import emergent_designs as EM  # noqa: E402
from backend.game_logic import game_end as GE  # noqa: E402
from backend.game_logic import moments as MO  # noqa: E402
from backend.game_logic import vassal as VS  # noqa: E402
from backend.modding.validator import validate_scenario  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
LETTERS = ("the_people_stir", "the_ulcer")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _scenario() -> dict:
    return json.loads(SCENARIO.read_text(encoding="utf-8"))


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _events(world, etype: str):
    return [e for e in world.event_log if e.get("type") == etype]


def _takes(world, nation: str, *regions: str) -> None:
    with _quiet():
        for region_name in regions:
            world.capture_region(region_name, nation)


def _holds(world, holder: str, *regions: str) -> None:
    """A province set by hand — a treaty's write, a carve, a hand-back (the
    fifteen writers outside the chokepoint): the derived count must see it."""
    for region_name in regions:
        world.regions[region_name].controller = holder
    world.invalidate_active_nations_cache()


def _dispatch_lines(world, etype: str):
    from backend.game_logic.dispatch import _format_dispatch_event_text
    return [_format_dispatch_event_text(e["type"], e["template_vars"])
            for e in world.pending_dispatch_events if e["type"] == etype]


def _client_of(world, client: str, lord: str) -> None:
    record = dict(world.vassals["Holland"])
    record["lord"] = lord
    world.vassals[client] = record
    world.invalidate_bloc_members_cache()
    world.invalidate_active_nations_cache()


def _set(world, court: str, value: int) -> None:
    """Set a court's level by the ONE writer (the beats it crosses are logged)."""
    AW.move(world, court, value - AW.level(world, court), "test")


# ═══════════════════════════════════════════════════════════════════════
# The block — the gate's thresholds, the validator, the store
# ═══════════════════════════════════════════════════════════════════════

class TestTheBlock:
    def test_the_shipped_block_and_the_thresholds(self, world):
        assert _scenario()["awakening"] == {"stirring": 40, "risen": 70}
        assert AW.armed(world) and (AW.stirring(world), AW.risen(world)) == (40, 70)
        assert AW.STORE_KEY in world.moments
        assert AW.store(world)["courts"] == {}, "every people quiet at the boot"

    def test_the_shipped_file_keeps_its_eleven_warnings(self):
        result = validate_scenario(_scenario(), check_adjacency=True)
        assert result.is_valid and len(result.warnings) == 11
        assert not [w for w in result.warnings if w.path.startswith("awakening")]

    def test_the_shape_is_hard(self):
        data = _scenario()
        data["awakening"] = {"stirring": 80, "risen": 70, "temper": 3}
        result = validate_scenario(data, check_adjacency=True)
        paths = {e.path for e in result.errors}
        assert "awakening.stirring" in paths and "awakening.temper" in paths
        data["awakening"] = {"stirring": 0, "risen": 100}
        result = validate_scenario(data, check_adjacency=True)
        assert {"awakening.stirring", "awakening.risen"} <= {e.path for e in result.errors}
        data["awakening"] = [40, 70]
        assert any(e.path == "awakening" for e in validate_scenario(data, check_adjacency=True).errors)
        data["awakening"] = {}
        assert validate_scenario(data, check_adjacency=True).is_valid, "an empty block arms the defaults"

    def test_the_reader_tolerates_what_the_validator_refuses(self):
        assert AW.clean_block({}) == {"stirring": 40, "risen": 70}
        assert AW.clean_block({"stirring": 80, "risen": 70}) == {"stirring": 40, "risen": 70}
        assert AW.clean_block({"stirring": 0, "risen": 250}) == {"stirring": 1, "risen": 99}
        assert AW.clean_block(None) is None and AW.clean_block([40, 70]) is None

    def test_the_store_rides_the_moments_store_and_survives_a_save(self, world):
        from backend.models.world_state import WorldState
        world.current_turn = 5
        _takes(world, "Austria", "Munich", "Swabia")
        AW.tick(world)
        _set(world, "Spain", 55)
        data = world.to_dict()
        assert set(data) == set(WorldState().to_dict()), "no new top-level field"
        again = WorldState.from_dict(data)
        assert AW.store(again) == AW.store(world)
        assert AW.level(again, "Spain") == 55 and AW.occupied(again, "Bavaria") == 2
        assert AW.store(again)["houses"] == {"Holland": "France", "KingdomOfItaly": "France",
                                             "Switzerland": "France"}

    def test_a_world_that_authors_none_writes_nothing(self):
        from backend.models.world_state import WorldState
        bare = WorldState()
        assert bare.moments == {} and not AW.armed(bare)
        assert AW.tick(bare) == [] and AW.move(bare, "Prussia", 50, "test") is None
        assert AW.note_dictated_peace(bare, "Prussia") is None
        assert AW.ulcer_factor(bare, "France", bare.regions["Paris"]) == 1.0
        assert AW.people_stir(bare, "France", {}) == {"holds": False, "bind": {}, "measure": None, "latch": False}
        assert bare.moments == {}

    def test_a_pre_tier_6_save_gains_the_store_on_load(self, world):
        from backend.models.world_state import WorldState
        data = world.to_dict()
        data["moments"].pop(AW.STORE_KEY)
        old = WorldState.from_dict(data)
        assert not AW.armed(old)
        assert AW.backfill(old, _scenario()) is True
        assert AW.armed(old) and AW.store(old)["courts"] == {}
        assert AW.store(old)["houses"]["KingdomOfItaly"] == "France"
        assert AW.backfill(old, _scenario()) is False, "a store carried is never overwritten"

    def test_the_boot_web_is_the_peoples_memory(self, world):
        assert AW.boot_house(world, "KingdomOfItaly") == "France"
        assert AW.boot_house(world, "Holland") == "France"
        assert AW.boot_house(world, "Spain") == "Spain" and AW.boot_house(world, "Austria") == "Austria"
        assert "KingdomOfItaly" in AW.boot_courts(world) and "France" in AW.boot_courts(world)


# ═══════════════════════════════════════════════════════════════════════
# The derived count — §5a C1 / C2
# ═══════════════════════════════════════════════════════════════════════

class TestTheDerivedCount:
    def test_nothing_is_occupied_at_the_boot(self, world):
        assert all(AW.occupied_count(world, c) == 0 for c in AW.boot_courts(world))

    def test_the_count_is_derived_off_the_boot_homeland(self, world):
        _takes(world, "Austria", "Munich", "Swabia")
        assert AW.occupied_count(world, "Bavaria") == 2
        _takes(world, "Bavaria", "Munich")
        assert AW.occupied_count(world, "Bavaria") == 1
        assert AW.occupied_count(world, "Austria") == 0

    def test_a_treaty_write_counts_the_same_as_a_capture(self, world):
        _holds(world, "Prussia", "Hanover")
        with _quiet():
            GE.record_province_title(world, "Hanover", GE.TITLE_TREATY, "Hanover", "Prussia")
        assert AW.occupied_count(world, "Hanover") >= 1, "the people read the map, not the treaty"

    def test_a_clients_soil_under_its_lord_is_home(self, world):
        milan = AW.homeland(world, "KingdomOfItaly")[0]
        _holds(world, "France", milan)
        assert not AW.is_foreign_held(world, "KingdomOfItaly", milan)
        _holds(world, "Austria", milan)
        assert AW.is_foreign_held(world, "KingdomOfItaly", milan)

    def test_foreign_held_reads_the_house(self, world):
        _client_of(world, "Bavaria", "France")
        _holds(world, "Bavaria", "Tyrol")
        assert AW.is_foreign_held(world, "Austria", "Tyrol"), "France's client on Austrian soil"
        _holds(world, "France", "Galicia")
        assert AW.is_foreign_held(world, "Spain", "Galicia"), "an ally's soil is still its people's"
        world.regions["Galicia"].controller = ""
        assert not AW.is_foreign_held(world, "Spain", "Galicia"), "an empty controller is nobody's garrison"

    def test_a_court_subjugated_later_keeps_its_boot_house(self, world):
        """Spain under Joseph, Austria under the Emperor's Pressburg: the new
        lord's holdings are foreign — the people rise against the garrisons
        of the lord imposed on them (DY-5's client dial reads the same)."""
        _holds(world, "France", "Vienna", "Tyrol")
        _client_of(world, "Austria", "France")
        assert AW.home_houses(world, "Austria") == {"Austria"}
        assert AW.occupied_count(world, "Austria") == 2
        assert AW.held_by_house(world, "Austria", "France") == 2
        _set(world, "Austria", 45)
        read = AW.people_stir(world, "France", {})
        assert read["holds"] and read["bind"]["host"] == "Austria", "the Emperor's own client is his affair"
        _set(world, "Austria", 75)
        assert AW.ulcer_factor(world, "France", world.regions["Vienna"]) == 0.75

    def test_a_boot_client_is_home_while_it_stays_and_foreign_once_it_broke_free(self, world):
        first = AW.homeland(world, "Holland")[0]
        _holds(world, "France", first)
        assert AW.home_houses(world, "Holland") == {"Holland", "France"}
        assert AW.occupied_count(world, "Holland") == 0
        with _quiet():
            assert VS.release_vassal(world, "Holland")["success"]
        assert AW.home_houses(world, "Holland") == {"Holland"}
        assert AW.occupied_count(world, "Holland") == 1, "its old lord's garrison is foreign from then on"
        # an erased boot client keeps its lord's house: the Kingdom of Italy under France
        assert AW.home_houses(world, "KingdomOfItaly") == {"KingdomOfItaly", "France"}


# ═══════════════════════════════════════════════════════════════════════
# The raises
# ═══════════════════════════════════════════════════════════════════════

class TestTheRaises:
    def test_the_bands(self):
        assert [AW.band_raise(n) for n in (0, 1, 2, 3, 5, 6, 12)] == [0, 1, 1, 2, 2, 3, 3]

    def test_the_tick_raises_by_band(self, world):
        # Austria's soil, not Bavaria's last province (that road signs at the
        # last — T4-2 — and its peace writes the dictated raise, tested apart)
        _takes(world, "France", "Tyrol", "Moravia")
        assert AW.tick(world) == [] and AW.level(world, "Austria") == 1
        assert AW.occupied(world, "Austria") == 2
        _takes(world, "France", "Bohemia")
        AW.tick(world)
        assert AW.level(world, "Austria") == 3 and AW.occupied(world, "Austria") == 3
        assert AW.level(world, "France") == 0 and "France" not in AW.store(world)["courts"]

    def test_a_dictated_peace_raises_by_rank(self, world):
        with _quiet():
            EM.record_punitive_cessions(world, {"Austria": [("Vienna", "France")]})
            EM.record_punitive_cessions(world, {"Spain": [("Madrid", "France")]})
            EM.record_punitive_cessions(world, {"Bavaria": [("Munich", "Austria")]})
        assert (AW.level(world, "Austria"), AW.level(world, "Spain"), AW.level(world, "Bavaria")) == (15, 10, 5)
        assert AW.dictated_peace_raise(world, "Hesse") == 5

    def test_a_peace_below_the_bar_writes_nothing(self, world):
        with _quiet():
            EM.record_punitive_cessions(world, {"Austria": [("Tyrol", "France")]})
        assert AW.level(world, "Austria") == 0

    def test_the_sovereign_captured(self, world):
        """Bayonne in reverse — the Emperor taken: the player's house carries
        the scalar like every court (Q3's corollary)."""
        from backend.game_logic.fall import sovereign_of
        napoleon = sovereign_of(world, "France")
        assert napoleon is not None and napoleon.is_sovereign
        with _quiet():
            world.capture_marshal(napoleon, "Austria", context="test")
        assert AW.level(world, "France") == AW.SOVEREIGN_CAPTURED_RAISE
        assert AW.level(world, "Austria") == 0

    def test_a_client_squeezed_and_relieved(self, world):
        _set(world, "Holland", 30)
        world.diplomatic_points = 10
        with _quiet():
            assert VS.change_vassal_autonomy(world, "Holland", 0, actor="France")["success"]
        assert AW.level(world, "Holland") == 35
        with _quiet():
            assert VS.change_vassal_autonomy(world, "Holland", 2, actor="France")["success"]
        assert AW.level(world, "Holland") == 25

    def test_the_seam_down_moves_nothing(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-STIR"])
        _takes(world, "Austria", "Munich", "Swabia")
        assert AW.tick(world) == [] and AW.store(world)["courts"] == {}
        assert AW.move(world, "Spain", 50, "test") is None and AW.level(world, "Spain") == 0
        with _quiet():
            EM.record_punitive_cessions(world, {"Austria": [("Vienna", "France")]})
        assert AW.level(world, "Austria") == 0 and _events(world, "awakening") == []


# ═══════════════════════════════════════════════════════════════════════
# The cools
# ═══════════════════════════════════════════════════════════════════════

class TestTheCools:
    def test_minus_one_a_turn_with_none_occupied(self, world):
        _set(world, "Spain", 10)
        AW.tick(world)
        assert AW.level(world, "Spain") == 9

    def test_the_lump_when_home_rule_returns(self, world):
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 30)
        AW.tick(world)
        assert (AW.level(world, "Bavaria"), AW.occupied(world, "Bavaria")) == (31, 1)
        _takes(world, "Bavaria", "Munich")
        AW.tick(world)
        assert (AW.level(world, "Bavaria"), AW.occupied(world, "Bavaria")) == (20, 0)
        AW.tick(world)
        assert AW.level(world, "Bavaria") == 19, "the lump once, the cool every turn"

    def test_a_release_restores_home_rule(self, world):
        _set(world, "Holland", 30)
        with _quiet():
            assert VS.release_vassal(world, "Holland")["success"]
        assert AW.level(world, "Holland") == 20

    def test_clamped_0_to_100(self, world):
        AW.move(world, "Spain", 500, "test")
        assert AW.level(world, "Spain") == 100
        AW.move(world, "Spain", -500, "test")
        assert AW.level(world, "Spain") == 0 and "Spain" not in AW.store(world)["courts"]


# ═══════════════════════════════════════════════════════════════════════
# The beats — one row per phase crossing, in words
# ═══════════════════════════════════════════════════════════════════════

class TestTheBeats:
    def test_a_phase_crossed_once_each_way(self, world):
        world.current_turn = 7
        assert AW.move(world, "Spain", 39, "test") is None
        beat = AW.move(world, "Spain", 1, "test")
        assert beat and (beat["phase"], beat["direction"]) == ("stirring", "up")
        assert AW.move(world, "Spain", 10, "test") is None, "inside a phase, no beat"
        risen = AW.move(world, "Spain", 25, "test")
        assert risen["phase"] == "risen" and "HAVE RISEN" in risen["message"]
        down = AW.move(world, "Spain", -31, "test")
        assert (down["phase"], down["direction"]) == ("stirring", "down")
        quiet = AW.move(world, "Spain", -5, "test")
        assert quiet["phase"] == "quiet" and "home rule" in quiet["message"]
        rows = _events(world, "awakening")
        assert [(r["phase"], r["direction"]) for r in rows] == [
            ("stirring", "up"), ("risen", "up"), ("stirring", "down"), ("quiet", "down")]
        assert all(r["nation"] == "Spain" and r["turn"] == 7 for r in rows)
        assert len(_dispatch_lines(world, "awakening")) == 4

    def test_a_jump_across_two_phases_names_the_higher(self, world):
        beat = AW.move(world, "Spain", 90, "test")
        assert beat["phase"] == "risen" and len(_events(world, "awakening")) == 1

    def test_the_one_new_log_type_and_the_census(self):
        assert "awakening" in CL.CAMPAIGN_LOG_TYPES
        assert len(CL.CAMPAIGN_LOG_TYPES) == 185  # 184->185 flipped consciously: DY-5 (Nov 10, 2026) adds `levee` — a nation's liberation levée rises or stands down, its National Guard armed (DYNAMISM_SPEC.md §5; `awakening._the_levee_beats`); no inert type retired in exchange  # 183->184 flipped consciously: DY-4 (Nov 10, 2026) adds `awakening` — a people of Europe crosses a phase of the Awakening (stirring, risen, quiet again; DYNAMISM_SPEC.md §5; DY-0's column reads the prefix); no inert type retired in exchange  # 182->183 flipped consciously: DY-2 adds `question_turns`  # 181->182 flipped consciously: T4-3 adds `rank_promotion`  # 180->181 flipped consciously: AU-2b adds `te_deum`  # 179->180 flipped consciously: S14c part 1 adds `moment`  # 178->179 flipped consciously: VP-1 adds `imperial_design`  # 176->178 flipped consciously: PC-R7 (ii) part 2 adds `war_articles_declared` and `war_articles_settled`  # 175->176 flipped consciously: PC-R2 adds `surety_returned`  # 173->175 flipped consciously: DD-1 S8 Step 3 adds `allegiance_bid` and `province_returned`  # 164->165 flipped consciously: IQ-7 adds `client_petition_answered`  # 165->166 flipped consciously: GE-1 adds `campaign_ending`  # 166->167 flipped consciously: GE-3 adds the congress chronicle type  # 167->168 flipped consciously: VP-M1 adds `marshal_wounded`  # 168->171 flipped consciously: RF-1 adds `law_enacted` / `law_repealed` / `law_lapsed`  # 171->172 flipped consciously: VD-C adds `vassal_contingent`  # 172->173 flipped consciously: TILSIT adds `continental_system_membership`
        assert CL.CATEGORY_MAP["awakening"] == "diplomacy"
        from backend.game_logic import gazette as GZ
        assert "awakening" in GZ._COURT_TYPES

    def test_the_beat_is_a_lead_at_high_priority(self):
        from backend.game_logic import dispatch as D
        assert D._DIPLOMATIC_EVENT_TEMPLATES["awakening"] == "{line}"
        assert D._DIPLOMATIC_EVENT_PRIORITY["awakening"] == "HIGH"
        assert "awakening" in CL.LOG_TIER_LEAD

    def test_the_one_liner_and_the_court_knowledge(self, world):
        world.current_turn = 9
        _takes(world, "Austria", "Munich", "Swabia")
        AW.tick(world)
        _set(world, "Bavaria", 41)
        _set(world, "Bavaria", 71)
        stir, risen = _events(world, "awakening")
        assert CL.format_event_oneliner(stir, player_nation="France", world=world) == (
            "THE PEOPLE OF BAVARIA STIR — 2 home provinces under foreign garrisons")
        assert CL.format_event_oneliner(risen, player_nation="France", world=world) == (
            "THE PEOPLE OF BAVARIA HAVE RISEN — an occupier's columns bleed on their roads")
        assert risen in CL.filter_campaign_log(world.event_log, world), "court knowledge across Europe"

    def test_never_a_figure_of_the_scalar(self, world):
        _set(world, "Spain", 73)
        [row] = _events(world, "awakening")
        for text in (row["message"], CL.format_event_oneliner(row, player_nation="France", world=world),
                     *_dispatch_lines(world, "awakening")):
            assert "73" not in text and "70" not in text

    def test_the_sweeps_column_reads_the_rows(self, world):
        from tools.ai_v_sweep import derive_metrics
        _set(world, "Spain", 45)
        [row] = _events(world, "awakening")
        assert row["type"].startswith("awakening") and row["nation"] == "Spain"
        assert 'startswith("awakening")' in inspect.getsource(derive_metrics)


# ═══════════════════════════════════════════════════════════════════════
# The ulcer — `_supply_multiplier`'s read
# ═══════════════════════════════════════════════════════════════════════

class TestTheUlcer:
    def test_the_occupier_bleeds_at_risen_and_not_below(self, world):
        _takes(world, "Austria", "Munich")
        munich = world.regions["Munich"]
        _set(world, "Bavaria", 69)
        assert AW.ulcer_factor(world, "Austria", munich) == 1.0
        _set(world, "Bavaria", 70)
        assert AW.ulcer_factor(world, "Austria", munich) == AW.ULCER_SUPPLY_FACTOR

    def test_france_bleeds_too(self, world):
        _takes(world, "France", "Galicia")
        _set(world, "Spain", 80)
        galicia = world.regions["Galicia"]
        assert AW.ulcer_factor(world, "France", galicia) == 0.75, "Q3: the Spanish ulcer"
        # the multiplier composes: home 1.5×, the doctrine's clause where it
        # bites (France lives off the land in Spain), the ulcer — read the
        # ulcer's own share against the seam held down
        with_ulcer = world._supply_multiplier("France", galicia)
        with pytest.MonkeyPatch.context() as mp:
            hold_down(mp, T3_SEAMS_BY_ROW["T6-ULCER"])
            without = world._supply_multiplier("France", galicia)
        assert with_ulcer == pytest.approx(without * 0.75)
        assert world.get_effective_supply_cap("France", galicia) == int(galicia.supply_capacity * with_ulcer)

    def test_the_owners_own_army_never_bleeds_and_home_held_soil_feeds(self, world):
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 80)
        assert AW.ulcer_factor(world, "Bavaria", world.regions["Munich"]) == 1.0
        assert AW.ulcer_factor(world, "Austria", world.regions["Franconia"]) == 1.0, "Bavaria holds it"
        assert AW.ulcer_factor(world, "France", world.regions["Franconia"]) == 1.0

    def test_an_ally_beside_the_occupier_bleeds_too(self, world):
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 80)
        assert AW.ulcer_factor(world, "Russia", world.regions["Munich"]) == 0.75

    def test_a_clients_lord_is_home_on_its_soil(self, world):
        milan = AW.homeland(world, "KingdomOfItaly")[0]
        _holds(world, "France", milan)
        _set(world, "KingdomOfItaly", 90)
        assert AW.ulcer_factor(world, "France", world.regions[milan]) == 1.0
        _holds(world, "Austria", milan)
        assert AW.ulcer_factor(world, "Austria", world.regions[milan]) == 0.75

    def test_shown_equals_applied(self, world):
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 80)
        munich = world.regions["Munich"]
        cap = world.get_effective_supply_cap("Austria", munich)
        assert cap == int(munich.supply_capacity * world.HOME_SUPPLY_MULTIPLIER * 0.75)
        assert world.get_effective_supply_cap("Austria", munich, forecast=False) == cap, "the bill reads the same"

    def test_the_doctrine_stays_last(self):
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState._supply_multiplier)
        assert src.index("ulcer_factor(") < src.index("supply_factor(self, nation, region")

    def test_the_seam_down_reads_one(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-ULCER"])
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 80)
        assert AW.ulcer_factor(world, "Austria", world.regions["Munich"]) == 1.0


# ═══════════════════════════════════════════════════════════════════════
# The letters — the deck, the predicates, the op
# ═══════════════════════════════════════════════════════════════════════

class TestTheLetters:
    def test_the_two_letters_in_lockstep(self):
        scenario = _scenario()["moments"]["affairs"]
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"]
        assert scenario == fixture
        ids = [e["id"] for e in fixture["deck"]]
        # DY-5 (session D) appends The Nation in Arms after the two
        assert ids[-3:-1] == list(LETTERS) and len(ids) == 13
        for e in fixture["deck"][-3:-1]:
            # the Host's `clamp` shape (the user's "Clamp it first", AU-2a): a
            # people's rising arrives on a bled board too; the Decline is priced
            # in the host's goodwill and loyalty beside the clamped authority
            assert e["since"] == "DY-4" and e["shape"] == "bill" and e["bites"] == "clamp"
            assert [op["op"] for op in e["accept"]["ops"]] == ["gold", "admin", "awakening"]
            assert e["accept"]["ops"][2]["court"] == "$host"
            assert [op["op"] for op in e["decline"]["ops"]] == ["authority", "relation", "loyalty"]
            assert e["decline"]["ops"][1]["unless"] == "vassal"
            assert "may" in e["watch"] and "will" not in e["watch"]
        assert fixture["deck"][-3]["when"] == {"predicate": "people_stir"}
        assert fixture["deck"][-2]["when"] == {"predicate": "people_risen"}

    def test_the_predicates_and_the_row_are_registered(self):
        assert AF.PREDICATES["people_stir"] is AF._people_stir and AF.PREDICATE_PARAMS["people_stir"] == ()
        assert AF.PREDICATES["people_risen"] is AF._people_risen
        assert "DY-4" in AF.SINCE_ROWS and AF.row_armed("DY-4") is True

    def test_the_letters_sit_in_the_shipped_deck(self, world):
        assert [e["id"] for e in MO.affairs_deck(world)][-3:-1] == list(LETTERS)

    def test_the_predicates_read_the_thresholds(self, world):
        no = {"holds": False, "bind": {}, "measure": None, "latch": False}
        assert AW.people_stir(world, "France", {}) == no
        _takes(world, "France", "Munich")
        assert AW.people_stir(world, "France", {}) == no, "a quiet people writes nothing"
        _set(world, "Bavaria", 40)
        read = AW.people_stir(world, "France", {})
        assert read["holds"] and read["bind"] == {"host": "Bavaria"} and read["measure"] == 1
        assert AW.people_risen(world, "France", {}) == no
        _set(world, "Bavaria", 70)
        assert AW.people_stir(world, "France", {}) == no
        risen = AW.people_risen(world, "France", {})
        assert risen["holds"] and risen["bind"]["host"] == "Bavaria"

    def test_the_most_occupied_court_is_the_host(self, world):
        _takes(world, "France", "Munich")
        _takes(world, "France", "Galicia", "Castile")
        _set(world, "Bavaria", 50)
        _set(world, "Spain", 50)
        assert AW.people_stir(world, "France", {})["bind"]["host"] == "Spain"

    def test_the_lords_own_clients_and_another_houses_garrisons_never_bind(self, world):
        _set(world, "Holland", 55)
        _holds(world, "France", *AW.homeland(world, "Holland")[:1])
        assert not AW.people_stir(world, "France", {})["holds"], "a client's soil under its lord is home"
        _takes(world, "Austria", "Munich")
        _set(world, "Bavaria", 55)
        assert not AW.people_stir(world, "France", {})["holds"], "Austria's garrisons are not the Emperor's affair"

    def test_the_seam_holds_the_templates_out(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T6-LETTERS"])
        assert AF.row_armed("DY-4") is False
        assert not set(LETTERS) & {e["id"] for e in MO.affairs_deck(world)}
        _takes(world, "France", "Munich")
        _set(world, "Bavaria", 50)
        assert not AW.people_stir(world, "France", {})["holds"]

    def test_the_op_plans_in_words_and_applies_through_the_one_writer(self, world):
        _set(world, "Bavaria", 72)
        plan = MO.OPS["awakening"][0](world, "France", {"op": "awakening", "court": "Bavaria", "delta": -20})
        assert (plan["before"], plan["after"]) == (72, 52)
        assert plan["line"] == "the people of Bavaria quieten (risen → stirring)"
        assert not any(ch.isdigit() for ch in plan["line"])
        MO.OPS["awakening"][1](world, "France", plan)
        assert AW.level(world, "Bavaria") == 52
        assert [r["phase"] for r in _events(world, "awakening")] == ["risen", "stirring"]
        unarmed = MO.OPS["awakening"][0](world, "France", {"op": "awakening", "court": "", "delta": -20})
        assert unarmed["skip"]

    def test_the_op_is_an_accepts_alone_and_the_dated_deck_cannot_author_it(self):
        assert "awakening" in AF.AFFAIR_OPS and AF.AFFAIR_OP_BOUNDS["awakening"] == (-30, -1)
        assert "awakening" in MO.DECLINE_FORBIDDEN_OPS and "awakening" not in AF.DECLINE_ALLOWED_OPS
        assert "awakening" not in MO.OP_BOUNDS and "awakening" not in AF.BARRED_OPS
        assert len(MO.OPS) == 13   # DY-5 (session D): + `national_guard`, flipped consciously

    def test_the_validator_refuses_a_decline_and_a_delta_out_of_band(self):
        data = _scenario()
        deck = {e["id"]: e for e in data["moments"]["affairs"]["deck"]}
        deck["the_ulcer"]["decline"]["ops"].append({"op": "awakening", "court": "$host", "delta": -5})
        deck["the_people_stir"]["accept"]["ops"][2]["delta"] = -60
        result = validate_scenario(data, check_adjacency=True)
        messages = " ".join(e.message for e in result.errors)
        assert "A Decline carries only" in messages
        assert any(e.path.endswith("ops[2].delta") for e in result.errors)

    def test_on_a_held_occupation_the_letters_arrive_by_their_own_conditions(self, world):
        """"Events appear": the frozen board — France holds six Austrian
        provinces by treaty, the map held still, the mornings advanced by
        hand (the peoples' tick, then the moments' tick) and the Emperor's
        post read each morning (every standing letter declined). The people
        stir at the 15th morning (+3 a turn to 40), The People Stir arrives
        three mornings later — the premise two mornings old, the pulse's gap
        from the Proclamation past — the rising comes at the 25th and The
        Ulcer five mornings after it. The desk's own rules do the rest (RE
        §7: the pulse, the longest-standing premise); the measured arms never
        hold a people's soil this long, so this board is the letters' proof."""
        for r in ("Vienna", "Bohemia", "Moravia", "Tyrol", "Hungary", "Carniola"):
            _holds(world, "France", r)
            with _quiet():
                GE.record_province_title(world, r, GE.TITLE_TREATY, "Austria", "France")
        arrivals = {}
        for _ in range(32):
            world.current_turn += 1
            dm = world.dialogue_manager
            for letter in list(dm.iter_queue()) + ([dm.peek()] if dm.peek() else []):
                if MO.is_moment_letter(letter):
                    with _quiet():
                        MO.answer(world, letter, "decline")
            with _quiet():
                AW.tick(world)
                for mid in MO.tick(world):
                    arrivals.setdefault(MO.template_of(mid), world.current_turn)
        beats = [(e["turn"], e["phase"]) for e in _events(world, "awakening") if e["nation"] == "Austria"]
        assert beats == [(15, "stirring"), (25, "risen")]
        assert arrivals["the_people_stir"] == 18 and arrivals["the_ulcer"] == 30
        rows = {k: v for k, v in MO._state(world).items() if "#" in k}
        assert rows["the_people_stir#1"]["status"] == "answered" and rows["the_ulcer#1"]["status"] == "answered"
        assert rows["the_people_stir#1"]["bind"] == {"host": "Austria"}

    def test_the_bind_fills_the_slots(self, world):
        _takes(world, "France", "Munich")
        _set(world, "Bavaria", 50)
        [entry] = [e for e in MO.affairs_deck(world) if e["id"] == "the_people_stir"]
        read = AW.people_stir(world, "France", {})
        text = AF.fill_slots(world, entry["line"], {"bind": read["bind"], "lord": "France"}, entry,
                             n=read["measure"], m=1)
        assert "Bavaria" in text and "{" not in text


# ═══════════════════════════════════════════════════════════════════════
# The scale contract, the seams, the numbers
# ═══════════════════════════════════════════════════════════════════════

class TestTheScaleContract:
    def test_the_module_never_walks_the_map(self):
        src = inspect.getsource(AW)
        assert "regions.values()" not in src and "regions.items()" not in src
        assert "get_nation_regions" not in src or "regions.values()" not in src

    def test_every_seam_is_registered_and_zero_arg(self):
        import importlib
        for row in ("T6-STIR", "T6-ULCER", "T6-LETTERS"):
            [spec] = T3_SEAMS_BY_ROW[row]
            module_path, rest = spec.split(":")
            name = rest.split("=")[0]
            seam = getattr(importlib.import_module(module_path), name)
            assert seam() is True and inspect.signature(seam).parameters == {}

    def test_the_numbers_are_the_gates(self):
        assert (AW.AWAKE_STIRRING_DEFAULT, AW.AWAKE_RISEN_DEFAULT) == (40, 70)
        assert AW.OCCUPIED_BANDS == ((6, 3), (3, 2), (1, 1))
        assert AW.DICTATED_PEACE_RAISE == {"major": 15, "secondary": 10, "minor": 5}
        assert (AW.SOVEREIGN_CAPTURED_RAISE, AW.CLIENT_SQUEEZED_RAISE) == (10, 5)
        assert (AW.QUIET_COOL, AW.HOME_RULE_LUMP, AW.ULCER_SUPPLY_FACTOR) == (1, 10, 0.75)

    def test_the_tick_runs_before_the_mornings_letters(self):
        from backend.models.world_state import WorldState
        src = inspect.getsource(WorldState._advance_turn_internal)
        assert src.index("_awakening.tick(self)") < src.index("_moments.tick(self)")


# ═══════════════════════════════════════════════════════════════════════
# The session's one measure — four arms on three surfaces, each ALONE
# (`tools/_t6_measure.py`; `tools/_t6_series_arms.py`). Seeded paths,
# not laws (DYNAMISM_SPEC.md §5a's landing note; SYSTEMS_REFERENCE.md §203).
# ═══════════════════════════════════════════════════════════════════════

def _record(name: str) -> dict:
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


def _dump(row) -> str:
    return json.dumps(row, sort_keys=True)


SEEDS = ("austerlitz", "eylau", "friedland", "historical", "jena", "lodi",
         "marengo", "rivoli", "ulm", "wagram")
STAMP = "2026_11_10"
AMBIENT_ARMS = (("0", "t6_control"), ("STIR", "t6_stir"), ("ULCER", "t6_ulcer"), ("ALL", "t6"))


class TestTheSessionCMeasure:
    """The records of the final tree (the sweep ran twice: the first run's
    read of a subjugated court's soil as "home" to its new lord was refined
    before the record — §5a C2 — and the second run reproduces the first on
    every surface). Seeded paths, not laws; read honestly."""

    def _sig(self, label: str) -> dict:
        return _record(f"_dy_signature_{label}_{STAMP}.json")

    def _census(self, label: str) -> dict:
        return _record(f"_{label}_census_{STAMP}.json")

    def test_arm_0_reproduces_session_bs_records_on_both_surfaces(self):
        b = _record("_dy_signature_t5_2026_11_10.json")
        ctl = self._sig("t6_control")
        for seed in SEEDS:
            assert _dump(ctl["seeds"][seed]) == _dump(b["seeds"][seed]), seed
        harness = _record(f"_t6_chain_d_{STAMP}.json")
        prior = _record("_t5_chain_d_2026_11_10.json")["arms"]["ALL"]
        for seed in SEEDS:
            mine = harness["arms"]["0"][seed]
            assert _dump({k: mine.get(k) for k in prior[seed]}) == _dump(prior[seed]), seed
        assert self._census("t6_control")["totals"]["awakening_beats"] == 0

    def test_the_scalar_alone_moves_every_ambient_seed_by_the_column_and_nothing_else(self):
        ctl, stir = self._sig("t6_control"), self._sig("t6_stir")
        for seed in SEEDS:
            a, b = ctl["seeds"][seed]["signature"], stir["seeds"][seed]["signature"]
            moved = {k for k in a if _dump(a[k]) != _dump(b.get(k))}
            assert moved == {"awakening_events"}, (seed, moved)
            assert dict(stir["seeds"][seed]["story_class"])["awakened"], seed
        for arm, label in AMBIENT_ARMS:
            assert self._sig(label)["story_class_count"] == 10, arm

    def test_the_peoples_that_stir_on_the_ambient_board(self):
        """The FRENCH people stir on every seed — the idle France loses its
        home provinces to the coalition — and rise on seven; the Bavarians
        stir on seven (Munich and Swabia under Austria, two provinces at +1 a
        turn) and quieten on marengo at 41 (Austria's peace hands them back);
        no other people reaches 40 in forty turns — the bands are the pace."""
        census = self._census("t6")
        beats = {s: [(b["court"], b["phase"], b["direction"]) for b in census["seeds"][s]["awakening_beats"]]
                 for s in SEEDS}
        assert all(("France", "stirring", "up") in beats[s] for s in SEEDS)
        risen = {s for s in SEEDS if ("France", "risen", "up") in beats[s]}
        assert risen == {"austerlitz", "friedland", "historical", "jena", "lodi", "ulm", "wagram"}
        bavaria = {s for s in SEEDS if ("Bavaria", "stirring", "up") in beats[s]}
        assert bavaria == {"friedland", "historical", "jena", "marengo", "rivoli", "ulm", "wagram"}
        assert beats["marengo"][-1] == ("Bavaria", "quiet", "down")
        assert {b[0] for s in SEEDS for b in beats[s]} == {"France", "Bavaria"}
        assert census["totals"]["awakening_beats"] == 25
        first = {s: min(b["turn"] for b in census["seeds"][s]["awakening_beats"]) for s in SEEDS}
        assert all(25 <= t <= 33 for t in first.values()), first

    def test_the_ulcer_alone_moves_ulm_and_the_bill_rises_on_six_seeds(self):
        stir, ulcer, final = self._sig("t6_stir"), self._sig("t6_ulcer"), self._sig("t6")
        movers = [s for s in SEEDS if _dump(ulcer["seeds"][s]) != _dump(stir["seeds"][s])]
        assert movers == ["ulm"]
        a, b = stir["seeds"]["ulm"]["signature"], ulcer["seeds"]["ulm"]["signature"]
        assert {k for k in a if _dump(a[k]) != _dump(b.get(k))} == {"captures_outside_aim"}
        assert (self._census("t6_stir")["totals"]["captures_outside_aim"],
                self._census("t6_ulcer")["totals"]["captures_outside_aim"]) == (248, 251)
        assert all(_dump(final["seeds"][s]) == _dump(ulcer["seeds"][s]) for s in SEEDS), "the letters move nothing ambiently"
        bill = {arm: self._census(label)["totals"]["supply_losses"] for arm, label in AMBIENT_ARMS}
        assert bill["0"] == bill["STIR"] == 1190952 and bill["ULCER"] == bill["ALL"] == 1196439
        per = {s: (sum(self._census("t6_stir")["seeds"][s]["supply_losses"].values()),
                   sum(self._census("t6_ulcer")["seeds"][s]["supply_losses"].values())) for s in SEEDS}
        risen = {s for s, (x, y) in per.items() if y > x}
        assert risen == {"friedland", "historical", "jena", "lodi", "ulm", "wagram"}, per
        assert all(y >= x for x, y in per.values()), per
        # the idle France is never an occupier: its own bill does not move;
        # the invaders of a risen France pay
        french = {arm: sum(self._census(label)["seeds"][s]["supply_losses"].get("France", 0) for s in SEEDS)
                  for arm, label in AMBIENT_ARMS}
        assert len(set(french.values())) == 1
        austria = {arm: sum(self._census(label)["seeds"][s]["supply_losses"].get("Austria", 0) for s in SEEDS)
                   for arm, label in AMBIENT_ARMS}
        assert austria["ULCER"] - austria["STIR"] == 5152

    def test_the_honest_totals_and_the_raised_gates_clauses(self):
        fin = self._census("t6")["totals"]
        assert fin["annexations_outside_aim"] == 0 and fin["questions_turned"] == 26
        assert (fin["alarm_guarantees"], fin["guarantees_honoured"], fin["last_refuges"]) == (10, 6, 22)
        assert fin["rank_promotions"] == 0, "the raised gate's second clause: unmet, reported"
        sig = self._sig("t6")
        assert all(sig["seeds"][s]["signature"]["eliminations"] == [[t, "KingdomOfItaly"]]
                   for s, t in zip(SEEDS, (10, 7, 23, 9, 7, 10, 21, 7, 10, 9))), "the third clause: unmet"
        assert all(sig["seeds"][s]["signature"]["formations"] == [] for s in SEEDS)

    def test_the_harness_the_march_does_not_visibly_bleed(self):
        """Chain D: the scalar alone moves no world-line but the column —
        Austria's people stir on every seed and rise at 29–31, Russia's on
        eight; the ulcer re-routes austerlitz and eylau, the Estonia turns
        stand on every seed, and France's bill falls 2.2% net — the ulcer
        taxes the cap and a corps under it pays nothing. Reported, never
        gated: §5's "the march bleeds" is not met as written."""
        harness = _record(f"_t6_chain_d_{STAMP}.json")
        arms = harness["arms"]

        def world_line(row):
            return _dump({k: v for k, v in row.items() if k not in ("awakening_events", "supply_losses")})

        assert all(world_line(arms["STIR"][s]) == world_line(arms["0"][s]) for s in SEEDS)
        for s in SEEDS:
            events = arms["STIR"][s]["awakening_events"]
            assert [t for t, n in events if n == "Austria"] and 19 <= events[0][0] <= 21, (s, events)
        with_russia = {s for s in SEEDS if any(n == "Russia" for _, n in arms["STIR"][s]["awakening_events"])}
        assert with_russia == set(SEEDS) - {"eylau", "friedland"}
        movers = [s for s in SEEDS if world_line(arms["ULCER"][s]) != world_line(arms["STIR"][s])]
        assert movers == ["austerlitz", "eylau"]
        assert all(world_line(arms["ALL"][s]) == world_line(arms["ULCER"][s]) for s in SEEDS)
        for s in SEEDS:
            estonia = [t for t, prov, _ in arms["ALL"][s]["france_captures"] if prov == "Estonia"]
            assert estonia == [t for t, prov, _ in arms["0"][s]["france_captures"] if prov == "Estonia"], s
        assert (arms["ULCER"]["austerlitz"]["france_provinces_final"], arms["ULCER"]["eylau"]["france_provinces_final"]) == (48, 36)
        bill = {arm: sum(arms[arm][s]["supply_losses"].get("France", 0) for s in SEEDS) for arm in ("0", "ULCER")}
        assert bill == {"0": 499833, "ULCER": 488612}
        assert all(harness["totals"][arm]["annexations_outside_aim"] == 0 for arm in ("0", "STIR", "ULCER", "ALL"))
        assert (harness["totals"]["0"]["captures_outside_aim"], harness["totals"]["ALL"]["captures_outside_aim"]) == (118, 117)

    def test_the_france_band_holds_on_every_arm(self):
        band = _record(f"_t6_band_{STAMP}.json")
        lo, hi = band["band"]
        for arm, rows in band["arms"].items():
            figures = {name: rows[name]["provinces"] for name in ("CMD-H", "CMD-A", "CMD-M")}
            assert figures == {"CMD-H": 28, "CMD-A": 27, "CMD-M": 26}, arm
            assert all(lo <= v <= hi for v in figures.values()), arm

    def test_the_standing_series_does_not_move(self):
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        rec = _record("_t6_series_arms_final.json")
        assert rec["prior"] == BASELINE_SERIES
        assert list(rec["arms"]) == ["0", "STIR", "ULCER", "ALL"]
        for arm, row in rec["arms"].items():
            assert row["first_divergence_vs_prior"] is None and row["series"] == BASELINE_SERIES, arm
        reach = {arm: rec["arms"][arm]["reach"]["counts"] for arm in rec["arms"]}
        assert (reach["0"]["moves"], reach["STIR"]["raises"], reach["STIR"]["beats"]) == (0, 139, 3)
        assert (reach["STIR"]["ulcer_bites"], reach["ULCER"]["ulcer_bites"]) == (0, 145)
        assert reach["ALL"]["letters_people_stir"] == 0 and reach["ALL"]["letters_people_risen"] == 0

    def test_the_letters_never_hold_on_a_measured_arm_and_the_record_says_why(self):
        """The pacing chain re-recorded (the deck changed): on the 53 measured
        arms The People Stir's premise never held on 52 and held one morning
        on the hand-played DDB-25 conquest board; The Ulcer's never — no
        measured arm holds a people's soil fourteen turns. The frozen-board
        pin above is the letters' proof."""
        rec = _record("_s14c_sweep_final.json")
        verdicts = {}
        for family in ("sweep", "commanded", "accept", "road", "road_accept", "reach_aar", "saves", "haiti"):
            for name, row in (rec.get(family) or {}).items():
                for t in ("the_people_stir", "the_ulcer"):
                    verdicts.setdefault(t, {})[f"{family}/{name}"] = row["affairs_reach"][t]["verdict"]
        assert len(verdicts["the_people_stir"]) == 53
        assert all(v == "premise never held" for v in verdicts["the_ulcer"].values())
        held = {k: v for k, v in verdicts["the_people_stir"].items() if v != "premise never held"}
        assert held == {"saves/DDB-25-conquest": "never due (premise held 1 morning)"}, held
