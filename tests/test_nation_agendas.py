"""Nation Agendas NA-0 (substrate) + NA-1 (legibility) — behavior pins.

Gate record + build contract: docs/NATION_AGENDAS_SPEC.md (§0 gate, §3
architecture, §4 authored decks, §5.1 legibility seams, §7 completion
definitions).

NA-0 pins: boot actives for every authored deck (Austria=redeem_italy,
Prussia=hanoverian_prize, Britain=low_countries, Russia=arbiter_of_europe),
the survival override, cache invalidation, serialization round-trip, and
the v1.1 dormancy pins (satellite decks latent while vassalized, live the
turn the nation is free).

NA-1 pins: ledger agenda row, war-room design line + the satisfy-their-
design recommendation, the agenda_pursuit motive reason (all 5 registers —
a missing register key is a hard KeyError in the composer), the dispatch
shift beat with first-observation suppression + seen-map dedup, and the
campaign-log event type.
"""

from pathlib import Path

import pytest

from backend.game_logic.agendas import (
    AGENDA_RESOLVE_ADVANCING,
    AGENDA_RESOLVE_SATISFIED,
    SURVIVAL_AGENDA_ID,
    agenda_concerns_player_bloc,
    agenda_satisfiable_by_player,
    build_agenda_payload,
    get_active_agenda,
    get_agenda_resolve_delta,
    process_agenda_shifts,
)
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _conquer(world, region_name, nation):
    world.regions[region_name].controller = nation
    world.invalidate_active_nations_cache()


def _war(world, a, b):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.invalidate_bloc_members_cache()


# ═══════════════════════ NA-0: BOOT ACTIVATION PINS ═══════════════════════

class TestBootActivation:
    @pytest.mark.parametrize("nation,agenda_id", [
        ("Austria", "redeem_italy"),
        ("Prussia", "hanoverian_prize"),
        ("Britain", "low_countries"),
        ("Russia", "arbiter_of_europe"),
        ("Sweden", "scourge_of_the_usurper"),
        ("Ottoman", "guard_the_straits"),
        ("Sardinia", "house_of_savoy_restored"),
        ("Denmark", "neutrality_of_the_north"),
    ])
    def test_boot_active_agendas(self, world, nation, agenda_id):
        view = get_active_agenda(nation, world)
        assert view is not None, f"{nation} should have an active agenda at boot"
        assert view.id == agenda_id
        assert view.title
        assert not view.survival

    @pytest.mark.parametrize("nation", [
        "France", "Spain", "Naples", "Portugal", "PapalStates",
        "Bavaria", "Saxony", "Hesse", "Hanover",
    ])
    def test_deckless_nations_have_no_agenda(self, world, nation):
        assert get_active_agenda(nation, world) is None

    def test_boot_hegemon_is_france_above_floor(self, world):
        from backend.game_logic.coalition import _identify_max_bloc_share
        hegemon, share = _identify_max_bloc_share(world)
        assert hegemon == "France"
        assert share >= 0.33  # low_countries / arbiter predicates depend on it


# ═══════════════════════ NA-0: DORMANCY PINS (v1.1) ═══════════════════════

class TestSatelliteDormancy:
    @pytest.mark.parametrize("nation", ["KingdomOfItaly", "Holland"])
    def test_dormant_while_vassalized(self, world, nation):
        assert nation in world.vassals  # boot satellite
        assert nation in world.agendas  # deck IS authored
        assert get_active_agenda(nation, world) is None

    @pytest.mark.parametrize("nation,agenda_id", [
        ("KingdomOfItaly", "risorgimento"),
        ("Holland", "the_seventeen_provinces"),
    ])
    def test_wakes_the_turn_the_nation_is_free(self, world, nation, agenda_id):
        del world.vassals[nation]
        world.invalidate_active_nations_cache()
        view = get_active_agenda(nation, world)
        assert view is not None
        assert view.id == agenda_id


# ═══════════════════════ NA-0: PREDICATES & PRIORITY ══════════════════════

class TestPredicatesAndPriority:
    def test_deck_priority_falls_to_second_entry(self, world):
        # Prussia takes Hanover -> hanoverian_prize satisfied; at peace,
        # armed_neutrality (guard) activates by deck order.
        _conquer(world, "Hanover", "Prussia")
        view = get_active_agenda("Prussia", world)
        assert view is not None
        assert view.id == "armed_neutrality"

    def test_guard_inactive_at_war(self, world):
        _conquer(world, "Hanover", "Prussia")
        _war(world, "Prussia", "Russia")
        world.invalidate_active_nations_cache()
        assert get_active_agenda("Prussia", world) is None

    def test_austria_satisfied_italy_falls_to_germany(self, world):
        for region in ("Milan", "Piedmont", "Savoy"):
            _conquer(world, region, "Austria")
        view = get_active_agenda("Austria", world)
        assert view is not None
        assert view.id == "primacy_germany"

    def test_acquire_counts_own_vassal_holdings_as_met(self, world):
        # Sardinia's targets held by Sardinia + a Sardinian vassal -> inactive.
        world.vassals["Naples"] = {"lord": "Sardinia", "loyalty": 50,
                                   "autonomy": "satellite"}
        _conquer(world, "Piedmont", "Naples")
        _conquer(world, "Savoy", "Sardinia")
        assert get_active_agenda("Sardinia", world) is None

    def test_deny_inactive_inside_hegemon_bloc(self, world):
        # Britain allied to the hegemon sits inside the bloc — never
        # threatened by its own bloc.
        key = world._make_diplo_key("Britain", "France")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Britain", world)
        assert view is None or view.id != "low_countries"

    def test_contain_inactive_inside_hegemon_bloc(self, world):
        key = world._make_diplo_key("Russia", "France")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        assert get_active_agenda("Russia", world) is None

    def test_paymaster_activates_when_deny_satisfied(self, world):
        # Strip the Low Countries from the French bloc -> low_countries
        # satisfied; at war with the hegemon + treasury above floor,
        # the paymaster posture takes over.
        for region in ("Flanders", "Brabant", "Amsterdam"):
            _conquer(world, region, "Britain")
        _war(world, "Britain", "France")
        world.nation_gold["Britain"] = 2500
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Britain", world)
        assert view is not None
        assert view.id == "paymaster"

    def test_paymaster_needs_treasury_above_floor(self, world):
        for region in ("Flanders", "Brabant", "Amsterdam"):
            _conquer(world, region, "Britain")
        _war(world, "Britain", "France")
        world.nation_gold["Britain"] = 2000  # floor is exclusive
        world.invalidate_active_nations_cache()
        assert get_active_agenda("Britain", world) is None

    def test_paymaster_coalition_membership_arm(self, world):
        # No direct war with the hegemon — membership in an active
        # coalition targeting it activates the posture.
        for region in ("Flanders", "Brabant", "Amsterdam"):
            _conquer(world, region, "Britain")
        world.diplomatic_states.pop(
            world._make_diplo_key("Britain", "France"), None)
        world.active_coalition = {"leader": "Britain",
                                  "members": ["Britain", "Russia"],
                                  "target_nation": "France"}
        world.nation_gold["Britain"] = 2500
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Britain", world)
        assert view is not None
        assert view.id == "paymaster"


# ═══════════════════════ NA-0: SURVIVAL OVERRIDE ══════════════════════════

class TestSurvivalOverride:
    def test_capital_lost_overrides_deck(self, world):
        _conquer(world, "Vienna", "France")
        view = get_active_agenda("Austria", world)
        assert view is not None
        assert view.survival
        assert view.id == SURVIVAL_AGENDA_ID

    def test_player_nation_gets_survival_too(self, world):
        # GR5: France has no deck but the Knife at the Throat applies.
        _conquer(world, "Paris", "Austria")
        view = get_active_agenda("France", world)
        assert view is not None
        assert view.survival

    def test_majority_homeland_lost_capital_held(self, world):
        # The second disjunct of the §3.1 band: majority of the homeland
        # gone while the capital still stands.
        home = list(world.nation_starting_regions["Austria"])
        capital = world.get_nation_capital("Austria")
        losable = [r for r in home if r != capital]
        majority = len(home) // 2 + 1
        for region in losable[:majority]:
            _conquer(world, region, "France")
        assert world.regions[capital].controller == "Austria"
        view = get_active_agenda("Austria", world)
        assert view is not None
        assert view.survival

    def test_eliminated_nation_has_no_agenda(self, world):
        # Elimination outranks the deck AND the survival posture.
        for region in world.get_nation_regions("Sardinia"):
            _conquer(world, region, "France")
        assert "Sardinia" not in world.get_active_nations()
        assert get_active_agenda("Sardinia", world) is None


# ═══════════════════════ NA-0: CACHE & SERIALIZATION ══════════════════════

class TestCacheAndSerialization:
    def test_cache_invalidation_recomputes_same_turn(self, world):
        assert get_active_agenda("Austria", world).id == "redeem_italy"
        _conquer(world, "Vienna", "France")  # helper invalidates
        assert get_active_agenda("Austria", world).survival

    def test_cache_is_per_turn(self, world):
        get_active_agenda("Austria", world)
        assert world._agenda_cache_turn == world.current_turn
        # A stale cache from a previous turn is rebuilt, not reused.
        world._agenda_cache_turn = world.current_turn - 1
        world._agenda_cache = {"Austria": None}
        assert get_active_agenda("Austria", world) is not None

    def test_production_diplomatic_seam_flushes_cache(self, world):
        # The P1 review fix: war/alliance state changes activation, and the
        # PRODUCTION seam (set_diplomatic_state -> invalidate_bloc_members_
        # cache) must flush the agenda cache — no hand invalidation here.
        from backend.game_logic.diplomacy import set_diplomatic_state
        assert get_active_agenda("Denmark", world).id == "neutrality_of_the_north"
        set_diplomatic_state(world, "France", "Denmark", "WAR", "test")
        assert get_active_agenda("Denmark", world) is None  # guard broken

    def test_decks_and_seen_map_round_trip(self, world):
        world.nation_agenda_seen["Austria"] = "redeem_italy"
        restored = WorldState.from_dict(world.to_dict())
        assert restored.agendas["Austria"][0]["id"] == "redeem_italy"
        assert restored.agendas["KingdomOfItaly"][0]["id"] == "risorgimento"
        assert restored.nation_agenda_seen == {"Austria": "redeem_italy"}
        assert get_active_agenda("Austria", restored).id == "redeem_italy"

    def test_boot_seen_map_empty(self, world1805):
        assert world1805.nation_agenda_seen == {}

    def test_pre_na_save_defaults(self):
        # Absent keys on old saves = no decks / fresh bookkeeping.
        legacy = WorldState(player_nation="France")
        data = legacy.to_dict()
        data.pop("agendas", None)
        data.pop("nation_agenda_seen", None)
        restored = WorldState.from_dict(data)
        assert restored.agendas == {}
        assert restored.nation_agenda_seen == {}


# ═══════════════════════ NA-0: RESOLVE FEEDERS (pure) ═════════════════════

class TestResolveFeeders:
    def test_war_advancing_agenda_hardens_resolve(self, world):
        # France's bloc holds Milan — Austria's war against France advances
        # redeem_italy.
        _war(world, "Austria", "France")
        assert (get_agenda_resolve_delta("Austria", "France", world)
                == AGENDA_RESOLVE_ADVANCING)

    def test_satisfied_first_entry_sues_sooner(self, world):
        for region in ("Milan", "Piedmont", "Savoy"):
            _conquer(world, region, "Austria")
        _war(world, "Austria", "France")
        assert (get_agenda_resolve_delta("Austria", "France", world)
                == AGENDA_RESOLVE_SATISFIED)

    def test_survival_override_sues_sooner(self, world):
        _conquer(world, "Vienna", "France")
        assert (get_agenda_resolve_delta("Austria", "France", world)
                == AGENDA_RESOLVE_SATISFIED)

    def test_irrelevant_war_changes_nothing(self, world):
        _war(world, "Denmark", "Sweden")
        assert get_agenda_resolve_delta("Denmark", "Sweden", world) == 0

    def test_agenda_concerns_player_bloc(self, world):
        assert agenda_concerns_player_bloc("Austria", world)   # Milan is French-bloc
        assert not agenda_concerns_player_bloc("Denmark", world)

    def test_satisfiable_by_player(self, world):
        assert agenda_satisfiable_by_player("Austria", world)
        # contain_hegemon is never table-satisfiable.
        assert not agenda_satisfiable_by_player("Russia", world)

    def test_vassal_never_has_resolve_voice(self, world):
        # KoI's capital (Milan) falls — survival would fire, but the
        # dormancy rule holds at every entry point: a vassal returns 0.
        _conquer(world, "Milan", "Austria")
        assert get_agenda_resolve_delta("KingdomOfItaly", "Austria", world) == 0

    def test_allying_into_the_bloc_is_dormancy_not_satisfaction(self, world):
        # Britain allied to the hegemon: low_countries goes DORMANT, but
        # its targets remain in hegemon-bloc hands — the design is NOT
        # satisfied, so no satisfied-sues-sooner resolve push.
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "Britain", "France", "ALLIANCE", "test")
        assert get_active_agenda("Britain", world) is None or \
            get_active_agenda("Britain", world).id != "low_countries"
        assert get_agenda_resolve_delta("Britain", "Russia", world) == 0

    def test_is_agenda_satisfied_on_a_stale_view(self, world):
        from backend.game_logic.agendas import is_agenda_satisfied
        view = get_active_agenda("Austria", world)  # redeem_italy
        assert not is_agenda_satisfied(view, world)
        for region in ("Milan", "Piedmont", "Savoy"):
            _conquer(world, region, "Austria")
        assert is_agenda_satisfied(view, world)


# ═══════════════════════ NA-0: VALIDATOR ══════════════════════════════════

def _minimal_scenario(agendas):
    return {
        "scenario_name": "t",
        "player_nation": "France",
        "marshals": {},
        "regions": {
            "Paris": {"name": "Paris", "terrain": "plains",
                      "starting_controller": "France",
                      "adjacent_regions": []},
        },
        "agendas": agendas,
    }


class TestValidator:
    def test_shipped_scenario_validates(self):
        import json
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        result = validate_scenario(data, check_adjacency=False)
        assert result.is_valid, [str(e) for e in result.errors]

    def test_invalid_type_hard_fails(self):
        result = validate_scenario(_minimal_scenario({
            "France": [{"id": "x", "type": "conquer_the_moon", "title": "X"}],
        }))
        assert not result.is_valid
        assert any("Invalid agenda type" in str(e) for e in result.errors)

    def test_region_typed_requires_regions(self):
        result = validate_scenario(_minimal_scenario({
            "France": [{"id": "x", "type": "acquire_regions", "title": "X"}],
        }))
        assert not result.is_valid
        assert any("non-empty 'regions'" in str(e) for e in result.errors)

    def test_unknown_region_hard_fails(self):
        result = validate_scenario(_minimal_scenario({
            "France": [{"id": "x", "type": "acquire_regions", "title": "X",
                        "regions": ["Atlantis"]}],
        }))
        assert not result.is_valid
        assert any("Atlantis" in str(e) for e in result.errors)

    def test_unknown_nation_warns_not_errors(self):
        result = validate_scenario(_minimal_scenario({
            "Atlantis": [{"id": "x", "type": "guard_neutrality", "title": "X",
                          "regions": ["Paris"]}],
        }))
        assert result.is_valid
        assert any("unknown nation" in str(w) for w in result.warnings)

    def test_duplicate_id_hard_fails(self):
        result = validate_scenario(_minimal_scenario({
            "France": [
                {"id": "x", "type": "guard_neutrality", "title": "X",
                 "regions": ["Paris"]},
                {"id": "x", "type": "guard_neutrality", "title": "Y",
                 "regions": ["Paris"]},
            ],
        }))
        assert not result.is_valid
        assert any("Duplicate agenda id" in str(e) for e in result.errors)

    def test_missing_id_and_title_hard_fail(self):
        result = validate_scenario(_minimal_scenario({
            "France": [{"type": "paymaster"}],
        }))
        assert not result.is_valid
        messages = [str(e) for e in result.errors]
        assert any("requires an 'id'" in m for m in messages)
        assert any("requires a 'title'" in m for m in messages)

    def test_reserved_survival_id_hard_fails(self):
        result = validate_scenario(_minimal_scenario({
            "France": [{"id": "survival", "type": "paymaster", "title": "X"}],
        }))
        assert not result.is_valid
        assert any("reserved" in str(e) for e in result.errors)

    @pytest.mark.parametrize("params", [
        {"type": "contain_hegemon", "share_floor": 1.5},
        {"type": "contain_hegemon", "share_floor": 0},
        {"type": "contain_hegemon", "share_floor": None},
        {"type": "contain_hegemon", "share_floor": "high"},
        {"type": "paymaster", "treasury_floor": -5},
        {"type": "paymaster", "treasury_floor": None},
        {"type": "paymaster", "treasury_floor": "rich"},
    ])
    def test_bad_floor_params_hard_fail(self, params):
        result = validate_scenario(_minimal_scenario({
            "France": [{"id": "x", "title": "X", **params}],
        }))
        assert not result.is_valid
        assert any("floor" in str(e) for e in result.errors)

    def test_null_floors_never_reach_runtime_crash(self, world):
        # Belt-and-braces beyond the validator: the runtime reader uses the
        # (x or default) idiom, so a None floor cannot TypeError.
        world.agendas["Russia"] = [{"id": "r", "type": "contain_hegemon",
                                    "title": "R", "share_floor": None}]
        world._agenda_cache = None
        view = get_active_agenda("Russia", world)
        assert view is not None and view.id == "r"


# ═══════════════════════ NA-1: LEDGER ROW ═════════════════════════════════

class TestLedgerRow:
    def test_nations_tab_carries_agenda(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)
        rows = {row["name"]: row for row in ledger["nations"]}
        austria = rows["Austria"]["agenda"]
        assert austria is not None
        assert austria["id"] == "redeem_italy"
        assert austria["title"] == "Redeem Italy"
        assert austria["stance_line"]
        # Deckless nation renders null — renderers omit (bloc_stamp contract).
        assert rows["Spain"]["agenda"] is None

    def test_stance_line_names_the_holder(self, world):
        payload = build_agenda_payload("Austria", world)
        assert "Milan" in payload["stance_line"]

    def test_godot_renderer_reads_agenda(self):
        # Source-scrape pin (the test_session8b pattern) — the .gd renderer
        # consumes the new key.
        gd = (Path(__file__).resolve().parents[1] / "godot-client"
              / "project-sovereign" / "scripts" / "diplomatic_ledger.gd")
        source = gd.read_text(encoding="utf-8")
        assert 'n.get("agenda")' in source


# ═══════════════════════ NA-1: WAR ROOM ═══════════════════════════════════

class TestWarRoom:
    def test_recommendation_satisfy_their_design(self, world):
        from backend.game_logic.diplomatic_advisory import (
            _build_situation_recommendation,
        )
        _war(world, "France", "Austria")
        war_rows = [{"opponent": "Austria", "opponent_display": "Austria",
                     "war_score": 10, "trend": "stable",
                     "request_terms_state": {"state": "available"}}]
        rec = _build_situation_recommendation(world, "France", war_rows,
                                              None, "defensive")
        assert rec is not None
        assert rec["kind"] == "request_terms"
        assert rec["target_nation"] == "Austria"
        assert "design" in rec["label"].lower()
        assert "Redeem Italy" in rec["text"]

    def test_losing_war_still_outranks_agenda_counsel(self, world):
        from backend.game_logic.diplomatic_advisory import (
            _build_situation_recommendation,
        )
        _war(world, "France", "Austria")
        war_rows = [{"opponent": "Austria", "opponent_display": "Austria",
                     "war_score": -30, "trend": "worsening",
                     "request_terms_state": {"state": "available"}}]
        rec = _build_situation_recommendation(world, "France", war_rows,
                                              None, "defensive")
        assert rec is not None
        assert "design" not in rec["label"].lower()

    def test_no_terms_route_falls_to_proposal_arm(self, world):
        from backend.game_logic.diplomatic_advisory import (
            _build_situation_recommendation,
        )
        _war(world, "France", "Austria")
        war_rows = [{"opponent": "Austria", "opponent_display": "Austria",
                     "war_score": 10, "trend": "stable",
                     "request_terms_state": {"state": "cooldown"}}]
        rec = _build_situation_recommendation(world, "France", war_rows,
                                              None, "defensive")
        assert rec is not None
        assert rec["kind"] == "open_proposal"
        assert rec["target_nation"] == "Austria"
        assert "design" in rec["label"].lower()

    def test_coalition_member_design_satisfiable(self, world):
        # The Pressburg counsel: satisfying a NON-leader coalition member
        # is how coalitions crack. Britain leads; Austria's design is the
        # one France can satisfy (Britain's Low Countries stripped first).
        from backend.game_logic.diplomatic_advisory import (
            _build_situation_recommendation,
        )
        for region in ("Flanders", "Brabant", "Amsterdam"):
            _conquer(world, region, "Britain")
        _war(world, "France", "Austria")
        _war(world, "France", "Britain")
        war_rows = [{"opponent": "Britain",
                     "opponents": ["Britain", "Austria"],
                     "opponent_display": "Britain + Austria",
                     "war_score": 0, "trend": "stable",
                     "request_terms_state": {"state": "cooldown"}}]
        rec = _build_situation_recommendation(world, "France", war_rows,
                                              None, "defensive")
        assert rec is not None
        assert rec["target_nation"] == "Austria"
        assert "design" in rec["label"].lower()

    def test_assess_situation_names_the_design(self, world):
        from backend.game_logic.diplomatic_advisory import generate_advisory
        _war(world, "France", "Austria")
        result = generate_advisory(None, "assess_situation", world)
        assert "Austria's design: Redeem Italy" in result["talleyrand_text"]


# ═══════════════════════ NA-1: MOTIVE LINES ═══════════════════════════════

class TestMotiveLines:
    def test_all_five_registers_authored(self):
        # A missing (register, reason) key is a hard KeyError in the
        # composer once the reason passes the _MOTIVE_REASONS gate.
        from backend.game_logic.diplomatic_templates import (
            _INCOMING_MOTIVE_LINES, _MOTIVE_REASONS,
        )
        assert "agenda_pursuit" in _MOTIVE_REASONS
        for register in ("hawk", "schemer", "dove", "chancery", "loyalist"):
            variants = _INCOMING_MOTIVE_LINES[(register, "agenda_pursuit")]
            assert len(variants) == 2

    @pytest.mark.parametrize("diplomat", ["Metternich", "Hardenberg",
                                          "Castlereagh"])
    def test_named_overrides_authored(self, diplomat):
        from backend.game_logic.diplomatic_templates import _NAMED_MOTIVE_LINES
        assert (diplomat, "agenda_pursuit") in _NAMED_MOTIVE_LINES

    def test_composer_voices_agenda_pursuit(self, world):
        from backend.game_logic.diplomatic_templates import (
            compose_incoming_diplomat_line,
        )
        line = compose_incoming_diplomat_line(
            world, nation="Austria", proposal_type="non_aggression",
            decision_reason="agenda_pursuit")
        assert line
        # Metternich's named lines speak of Austria/Vienna by name.
        assert "Austria" in line or "Vienna" in line

    def test_decision_reason_agenda_arm(self, world):
        from backend.game_logic.diplomacy import (
            determine_ai_offer_decision_reason,
        )
        # Austria's design targets the player's bloc -> agenda_pursuit...
        assert determine_ai_offer_decision_reason(
            "Austria", "non_aggression", world) == "agenda_pursuit"
        # ...but never outranks the peace-family war_overload override.
        assert determine_ai_offer_decision_reason(
            "Austria", "peace", world) == "war_overload"
        # A court whose design is elsewhere keeps the stock ladder.
        assert determine_ai_offer_decision_reason(
            "Denmark", "non_aggression", world) != "agenda_pursuit"

    def test_display_row_exists(self):
        from backend.display_names import diplomatic_decision_reason_display
        assert diplomatic_decision_reason_display(
            "agenda_pursuit") == "national design"


# ═══════════════════════ NA-1: THE SHIFT BEAT ═════════════════════════════

class TestShiftBeat:
    def test_first_observation_is_silent(self, world):
        world.pending_dispatch_events = []
        events = process_agenda_shifts(world)
        assert events == []  # bookkeeping, not announcements
        assert world.nation_agenda_seen["Austria"] == "redeem_italy"
        assert not [e for e in world.pending_dispatch_events
                    if e["type"] == "agenda_shift"]

    def test_shift_announces_once(self, world):
        process_agenda_shifts(world)  # record boot state
        world.pending_dispatch_events = []
        _conquer(world, "Vienna", "France")  # Austria -> survival
        events = process_agenda_shifts(world)
        assert len(events) == 1
        assert events[0]["nation"] == "Austria"
        queued = [e for e in world.pending_dispatch_events
                  if e["type"] == "agenda_shift"]
        assert len(queued) == 1
        assert queued[0]["fog_rule"] == "always"
        logged = [e for e in world.event_log if e["type"] == "agenda_shift"]
        assert len(logged) == 1
        # Dedup: a second poll announces nothing new.
        assert process_agenda_shifts(world) == []

    def test_deactivation_updates_silently(self, world):
        process_agenda_shifts(world)
        world.pending_dispatch_events = []
        # Explicit: keep Britain under the paymaster floor so satisfying
        # low_countries leaves NO active agenda (not a boot-gold coincidence).
        world.nation_gold["Britain"] = 1500
        for region in ("Flanders", "Brabant", "Amsterdam"):
            _conquer(world, region, "Britain")  # low_countries satisfied
        events = process_agenda_shifts(world)
        assert not [e for e in events if e["nation"] == "Britain"]
        assert world.nation_agenda_seen["Britain"] == ""

    def test_advance_turn_runs_the_poll(self, world):
        world.advance_turn()
        assert world.nation_agenda_seen.get("Austria") == "redeem_italy"

    def test_shift_survives_save_load_without_reannounce(self, world):
        process_agenda_shifts(world)
        restored = WorldState.from_dict(world.to_dict())
        restored.pending_dispatch_events = []
        assert process_agenda_shifts(restored) == []


# ═══════════════════════ NA-1: CAMPAIGN LOG ═══════════════════════════════

class TestCampaignLog:
    def test_event_type_registered(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP
        assert "agenda_shift" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["agenda_shift"] == "diplomacy"

    def test_fog_filter_always_shows(self, world):
        from backend.campaign_log import filter_campaign_log
        event = {"type": "agenda_shift", "nation": "Austria",
                 "focus": "Redeem Italy", "turn": 1}
        filtered = filter_campaign_log([event], world)
        assert filtered == [event]

    def test_oneliner_formats(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "agenda_shift", "nation": "Austria",
            "focus": "Redeem Italy",
        })
        assert "Austria" in line
        assert "Redeem Italy" in line

    def test_dispatch_template_exists(self):
        from backend.game_logic.dispatch import (
            _DIPLOMATIC_EVENT_PRIORITY, _DIPLOMATIC_EVENT_TEMPLATES,
        )
        assert "agenda_shift" in _DIPLOMATIC_EVENT_TEMPLATES
        assert "agenda_shift" in _DIPLOMATIC_EVENT_PRIORITY
        text = _DIPLOMATIC_EVENT_TEMPLATES["agenda_shift"].format(
            nation="Austria", focus="Redeem Italy")
        assert "Austria" in text and "Redeem Italy" in text
