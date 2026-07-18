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
        # NA-2 §5.3 (conscious flip of the NA-1 negative control): the
        # guard court's non_aggression ask now voices agenda_pursuit — the
        # pact IS its design. An ask that does NOT advance the design
        # keeps the stock ladder.
        assert determine_ai_offer_decision_reason(
            "Denmark", "non_aggression", world) == "agenda_pursuit"
        assert determine_ai_offer_decision_reason(
            "Denmark", "open_borders", world) != "agenda_pursuit"

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


# ═══════════════════ NA-2: THE ACCEPTANCE TERM (§5.2) ═════════════════════

def _bilateral(ptype, proposer, target, sweeteners=None, demands=None,
               clauses=None):
    return {
        "type": ptype,
        "proposer_nation": proposer,
        "target_nation": target,
        "sweeteners": list(sweeteners or []),
        "demands": list(demands or []),
        "clauses": list(clauses or []),
    }


class TestAgendaAcceptanceMod:
    """agenda_acceptance_mod — both directions, exclusivity, dormancy."""

    def test_bare_peace_entrenches_denial(self, world):
        """Austria refuses the peace that does not return Milan (-8)."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ENTRENCH, agenda_acceptance_mod,
        )
        proposal = _bilateral("peace", "France", "Austria")
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ENTRENCH

    def test_cession_of_design_target_advances(self, world):
        """Ceding Savoy (a redeem_italy target France holds) scores +12."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ADVANCE, agenda_acceptance_mod,
        )
        proposal = _bilateral(
            "peace", "France", "Austria",
            sweeteners=[{"type": "territory_cede", "value": 1,
                         "regions": ["Savoy"]}],
        )
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ADVANCE

    def test_string_clause_form_advances(self, world):
        """The territory_<lower> clause form (generate_suggested_terms
        shape) is recognized as a cession to the target."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ADVANCE, agenda_acceptance_mod,
        )
        proposal = _bilateral("peace", "France", "Austria",
                              clauses=["territory_savoy"])
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ADVANCE

    def test_advance_wins_over_entrench(self, world):
        """A war-ending peace WITH a design cession is an advance, not an
        entrenchment — the two arms are mutually exclusive."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ADVANCE, agenda_acceptance_mod,
        )
        proposal = _bilateral(
            "peace", "France", "Austria",
            sweeteners=[{"type": "territory_cede", "value": 1,
                         "regions": ["Milan"]}],
        )
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ADVANCE

    def test_bare_armistice_never_entrenches(self, world):
        """A BARE pause legitimizes nothing (protects AUD-b armistice
        tuning — AUD-b armistices carry no design content)."""
        from backend.game_logic.agendas import agenda_acceptance_mod
        for ptype in ("armistice", "armistice_losing", "armistice_winning"):
            proposal = _bilateral(ptype, "France", "Austria")
            assert agenda_acceptance_mod(proposal, world) == 0, ptype

    def test_armistice_with_design_strip_demand_entrenches(self, world):
        """DELIBERATE (adversarial-review pin): an armistice DEMANDING a
        held design region is a real ask with real content — the
        demand-strip arm prices it on any proposal type."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ENTRENCH, agenda_acceptance_mod,
        )
        _conquer(world, "Milan", "Austria")
        world.invalidate_bloc_members_cache()
        proposal = _bilateral(
            "armistice_winning", "France", "Austria",
            demands=[{"type": "territory_cede", "value": 1,
                      "regions": ["Milan"]}],
        )
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ENTRENCH

    def test_peace_from_armistice_state_still_entrenches(self, world):
        """The armistice-first route still ends in 'the peace that does
        not return Milan' — the formal peace entrenches from ARMISTICE
        state exactly as from WAR (adversarial-review fix)."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ENTRENCH, agenda_acceptance_mod,
        )
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ARMISTICE"
        world.invalidate_bloc_members_cache()
        proposal = _bilateral("peace", "France", "Austria")
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ENTRENCH

    def test_demand_stripping_held_target_entrenches(self, world):
        """Demanding a HELD design region asks the court to legitimize the
        loss — entrench, on any proposal type."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ENTRENCH, agenda_acceptance_mod,
        )
        _conquer(world, "Milan", "Austria")  # held target; Piedmont unmet
        world.invalidate_bloc_members_cache()
        proposal = _bilateral(
            "open_borders", "France", "Austria",
            demands=[{"type": "territory_cede", "value": 1,
                      "regions": ["Milan"]}],
        )
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ENTRENCH

    def test_deny_agenda_cession_out_of_bloc_advances(self, world):
        """France ceding Flanders to Britain takes it out of the hegemon's
        bloc — Britain's low_countries design advances (+12)."""
        from backend.game_logic.agendas import (
            AGENDA_ACCEPT_ADVANCE, agenda_acceptance_mod,
        )
        proposal = _bilateral(
            "peace", "France", "Britain",
            sweeteners=[{"type": "territory_cede", "value": 1,
                         "regions": ["Flanders"]}],
        )
        assert agenda_acceptance_mod(proposal, world) == AGENDA_ACCEPT_ADVANCE

    def test_deckless_target_scores_zero(self, world):
        """France (no deck) and a deckless world score 0 by construction."""
        from backend.game_logic.agendas import agenda_acceptance_mod
        to_france = _bilateral("peace", "Austria", "France")
        assert agenda_acceptance_mod(to_france, world) == 0
        world.agendas = {}
        world.invalidate_bloc_members_cache()
        bare = _bilateral("peace", "France", "Austria")
        assert agenda_acceptance_mod(bare, world) == 0

    def test_survival_override_scores_zero(self, world):
        """A court fighting for its life has no design term."""
        from backend.game_logic.agendas import (
            agenda_acceptance_mod, get_active_agenda,
        )
        _conquer(world, "Vienna", "France")  # capital lost -> survival
        world.invalidate_bloc_members_cache()
        view = get_active_agenda("Austria", world)
        assert view is not None and view.survival
        proposal = _bilateral("peace", "France", "Austria")
        assert agenda_acceptance_mod(proposal, world) == 0


class TestAcceptanceWiring:
    """The term rides calculate_acceptance: components, sum, feedback,
    preview labels."""

    def test_component_and_sum_negative(self, world):
        from backend.game_logic.agendas import AGENDA_ACCEPT_ENTRENCH
        from backend.game_logic.diplomacy import calculate_acceptance
        result = calculate_acceptance(
            _bilateral("peace", "France", "Austria"), world)
        assert result["components"]["agenda_mod"] == AGENDA_ACCEPT_ENTRENCH

    def test_component_positive_with_cession(self, world):
        from backend.game_logic.agendas import AGENDA_ACCEPT_ADVANCE
        from backend.game_logic.diplomacy import calculate_acceptance
        result = calculate_acceptance(
            _bilateral(
                "peace", "France", "Austria",
                sweeteners=[{"type": "territory_cede", "value": 1,
                             "regions": ["Savoy"]}]),
            world)
        assert result["components"]["agenda_mod"] == AGENDA_ACCEPT_ADVANCE

    def test_term_moves_the_score(self, world):
        """+12 vs -8: the same peace differs by exactly the two constants
        on the agenda component — pin the component delta, not the whole
        formula (deal balance moves too when a cession is added)."""
        from backend.game_logic.diplomacy import calculate_acceptance
        bare = calculate_acceptance(
            _bilateral("peace", "France", "Austria"), world)
        ceded = calculate_acceptance(
            _bilateral(
                "peace", "France", "Austria",
                sweeteners=[{"type": "territory_cede", "value": 1,
                             "regions": ["Savoy"]}]),
            world)
        assert (ceded["components"]["agenda_mod"]
                - bare["components"]["agenda_mod"]) == 20

    def test_legacy_world_component_zero(self, world):
        """No authored decks -> 0 (legacy fixture pins byte-identical)."""
        from backend.game_logic.diplomacy import calculate_acceptance
        world.agendas = {}
        world.invalidate_bloc_members_cache()
        result = calculate_acceptance(
            _bilateral("peace", "France", "Austria"), world)
        assert result["components"]["agenda_mod"] == 0

    def test_term_is_coupled_into_the_score(self, world):
        """Adversarial-review pin: the SAME bare peace scored with and
        without the deck differs by exactly the entrench constant at the
        SCORE level — deleting '+ agenda_mod_value' from raw_score fails
        here, not just in the components dict."""
        from backend.game_logic.agendas import AGENDA_ACCEPT_ENTRENCH
        from backend.game_logic.diplomacy import calculate_acceptance
        proposal = _bilateral("peace", "France", "Austria")
        with_deck = calculate_acceptance(proposal, world)
        world.agendas = {}
        world.invalidate_bloc_members_cache()
        without_deck = calculate_acceptance(proposal, world)
        assert (with_deck["score"] - without_deck["score"]
                ) == AGENDA_ACCEPT_ENTRENCH

    def test_confirm_snapshot_labels_the_term(self, world):
        """The crafted-terms confirm popup (build_war_context_snapshot)
        renders direction-aware copy, never the raw 'Agenda Mod' key.
        With relations recovered (relation_mod 0), the bare-peace agenda
        entrenchment (-8) is deterministically the largest obstacle."""
        from backend.game_logic.diplomacy import build_war_context_snapshot
        key = world._make_diplo_key("France", "Austria")
        world.nation_relations[key] = 0
        terms = {"type": "peace", "sweeteners": [], "demands": [],
                 "clauses": []}
        snapshot = build_war_context_snapshot(
            world, "France", "Austria", "peace", terms=terms)
        preview = snapshot.get("acceptance_preview") or {}
        assert preview.get("largest_negative") == "Entrenches their denial"
        assert "Agenda Mod" not in (preview.get("largest_positive", ""),
                                    preview.get("largest_negative", ""))

    def test_feedback_string_reachable(self):
        """agenda_mod is trackable and its FEEDBACK_STRINGS row resolves."""
        from backend.display_names import FEEDBACK_STRINGS
        from backend.game_logic.diplomacy import _generate_feedback
        assert "agenda_mod" in FEEDBACK_STRINGS
        components = {"agenda_mod": -8}
        text = _generate_feedback("REJECT", components)
        assert FEEDBACK_STRINGS["agenda_mod"]["negative"] in text

    def test_preview_shows_entrench_label(self, world):
        """The R17d top-3 breakdown names the term by direction. The
        armistice pair-cooldown (a real post-armistice war state) makes
        propose_peace the scored best action, so the peace entrenchment
        surfaces."""
        from backend.game_logic.diplomacy import get_diplomatic_preview
        key = world._make_diplo_key("France", "Austria")
        world.armistice_cooldowns = dict(
            getattr(world, "armistice_cooldowns", {}) or {})
        world.armistice_cooldowns[key] = 3
        preview = get_diplomatic_preview(world, "Austria")
        acceptance = preview.get("acceptance_preview") or {}
        negatives = acceptance.get("negative") or []
        agenda_rows = [e for e in negatives if e["key"] == "agenda_mod"]
        assert agenda_rows, f"agenda_mod missing from preview: {negatives}"
        assert agenda_rows[0]["label"] == "Entrenches their denial"


# ═══════════════════ NA-2: COVETS UNIFICATION (§5.2) ══════════════════════

class TestCovetsUnification:
    def test_agenda_covets_by_type(self, world):
        from backend.game_logic.agendas import get_agenda_covets
        assert get_agenda_covets("Austria", world) == [
            "Milan", "Piedmont", "Savoy"]
        # deny: listed regions in the hegemon bloc's hands (vassal-held
        # Brabant/Amsterdam count — Holland sits in France's bloc)
        assert get_agenda_covets("Britain", world) == [
            "Flanders", "Brabant", "Amsterdam"]
        assert get_agenda_covets("Prussia", world) == ["Hanover"]
        # postures yield nothing (profile fallback territory)
        assert get_agenda_covets("Russia", world) == []
        assert get_agenda_covets("France", world) == []

    def test_bargain_interest_reads_live_agendas_first(self, world):
        """Milan is nobody's authored profile covet but IS Austria's live
        design target — the claim now has an authored basis."""
        from backend.game_logic.diplomacy import _has_bargain_strategic_interest
        assert _has_bargain_strategic_interest(world, "Britain", "Milan")

    def test_bargain_interest_profile_fallback_still_works(self, world):
        """Bohemia rides only Austria's static profile row — fallback."""
        from backend.game_logic.diplomacy import _has_bargain_strategic_interest
        assert _has_bargain_strategic_interest(world, "Britain", "Bohemia")

    def test_bargain_interest_uncoveted_region_false(self, world):
        from backend.game_logic.diplomacy import _has_bargain_strategic_interest
        assert not _has_bargain_strategic_interest(
            world, "Britain", "Andalusia")

    def test_suggested_terms_prefer_agenda_target(self, world):
        """Losing the war, the suggested sweetener is a live DESIGN target.
        (Austria's profile covets stay as fallback data: Tyrol and Bohemia
        ARE 126-map regions — just not French-held at boot; only "Bavaria"
        is a nation name, not a province. The agenda source is consulted
        first regardless.)"""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        key = world._make_diplo_key("France", "Austria")
        # sign: positive = first-alphabetically (Austria) winning
        world.war_scores[key] = 30
        terms = generate_suggested_terms("Austria", "peace", world)
        cessions = [s for s in terms.get("sweeteners", [])
                    if s.get("type") == "territory_cede"]
        assert cessions, f"no cession suggested: {terms}"
        assert cessions[0]["regions"][0] in ("Milan", "Piedmont", "Savoy")

    def test_dead_nation_desires_territory_rows_deleted(self):
        """The unreachable counter-offer territory rows are gone (8.EVAL
        AUD-d disposition)."""
        from backend.game_logic.ai_diplomacy import NATION_DESIRES
        for nation, desires in NATION_DESIRES.items():
            for desire in desires:
                assert desire.get("type") != "territory", nation

    def test_commentary_names_the_agenda_region(self, world):
        """Adversarial-review fix: Talleyrand's commentary names the
        region his own terms just offered (Savoy), not the stale profile
        row ('Bavaria is Austria's natural sphere...')."""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        key = world._make_diplo_key("France", "Austria")
        world.war_scores[key] = 30  # Austria winning -> France sweetens
        terms = generate_suggested_terms("Austria", "peace", world)
        cessions = [s for s in terms.get("sweeteners", [])
                    if s.get("type") == "territory_cede"]
        assert cessions
        offered = cessions[0]["regions"][0]
        commentary = terms.get("talleyrand_commentary", "")
        assert offered in commentary
        assert "Bavaria" not in commentary

    def test_commentary_conquer_hint_names_live_covet(self, world):
        """The conquer-this-first hint points at the LIVE design covet
        (Hanover), not the dead profile advice ('Hardenberg dreams of
        Saxony... Conquer it first')."""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        terms = generate_suggested_terms("Prussia", "non_aggression", world)
        commentary = terms.get("talleyrand_commentary", "")
        assert "Hanover" in commentary
        assert "Saxony" not in commentary


# ═══════════════════ NA-2: R155 CADENCE (§5.3) ════════════════════════════

class TestHawkPersistence:
    def _activate_guard(self, world):
        """Prussia takes Hanover -> hanoverian_prize satisfied ->
        armed_neutrality (guard) active while at peace."""
        _conquer(world, "Hanover", "Prussia")
        world.invalidate_bloc_members_cache()
        from backend.game_logic.agendas import get_active_agenda
        view = get_active_agenda("Prussia", world)
        assert view is not None and view.id == "armed_neutrality"

    def test_ask_advances_agenda_pins(self, world):
        from backend.game_logic.agendas import ask_advances_agenda
        # acquire active at boot: nothing in the ask vocabulary advances it
        assert not ask_advances_agenda("Prussia", "non_aggression", world)
        self._activate_guard(world)
        assert ask_advances_agenda("Prussia", "non_aggression", world)
        assert not ask_advances_agenda("Prussia", "open_borders", world)
        assert not ask_advances_agenda("Britain", "non_aggression", world)

    def test_hawk_reasks_agenda_type_sooner(self, world):
        """Hardenberg (hawk) ignores the last 2 turns of the TYPE cooldown
        for the ask his court's design IS."""
        from backend.game_logic.ai_diplomacy import _is_on_cooldown
        self._activate_guard(world)
        world.ai_proposal_cooldowns = {"Prussia|non_aggression": 2}
        assert not _is_on_cooldown("Prussia", "non_aggression", world)
        world.ai_proposal_cooldowns = {"Prussia|non_aggression": 3}
        assert _is_on_cooldown("Prussia", "non_aggression", world)

    def test_dove_keeps_full_wait(self, world):
        """Personality stays the governor — dove asks once."""
        from backend.game_logic.ai_diplomacy import _is_on_cooldown
        self._activate_guard(world)
        world.diplomats["Prussia"].personality = "dove"
        world.ai_proposal_cooldowns = {"Prussia|non_aggression": 2}
        assert _is_on_cooldown("Prussia", "non_aggression", world)

    def test_non_matching_type_keeps_full_wait(self, world):
        from backend.game_logic.ai_diplomacy import _is_on_cooldown
        self._activate_guard(world)
        world.ai_proposal_cooldowns = {"Prussia|open_borders": 2}
        assert _is_on_cooldown("Prussia", "open_borders", world)

    def test_nation_cooldown_untouched(self, world):
        from backend.game_logic.ai_diplomacy import _is_on_cooldown
        self._activate_guard(world)
        world.ai_proposal_cooldowns = {"Prussia|nation": 1}
        assert _is_on_cooldown("Prussia", "non_aggression", world)

    def test_p3_candidates_lead_with_design_ask(self, world):
        """The guard court's shelter ask leads with its own pact; the boot
        acquire court keeps the stock ladder-first order."""
        from backend.game_logic.ai_diplomacy import _hegemony_ask_candidates
        boot = _hegemony_ask_candidates("Prussia", "PEACE", 40, world)
        assert boot and boot[0] == "open_borders"  # ladder from PEACE
        self._activate_guard(world)
        guard = _hegemony_ask_candidates("Prussia", "PEACE", 40, world)
        assert guard and guard[0] == "non_aggression"

    def test_design_ask_voices_agenda_pursuit(self, world):
        from backend.game_logic.diplomacy import (
            determine_ai_offer_decision_reason,
        )
        self._activate_guard(world)
        reason = determine_ai_offer_decision_reason(
            "Prussia", "non_aggression", world)
        assert reason == "agenda_pursuit"


# ═══════════════════ NA-2: PRESSBURG + COURTING (§5.4) ════════════════════

class TestPressburgArm:
    def _satisfy_austria(self, world):
        for region_name in ("Milan", "Piedmont", "Savoy"):
            _conquer(world, region_name, "Austria")
        world.invalidate_bloc_members_cache()

    def test_separate_peace_ready_pins(self, world):
        from backend.game_logic.agendas import agenda_separate_peace_ready
        assert not agenda_separate_peace_ready("Austria", world)
        self._satisfy_austria(world)
        assert agenda_separate_peace_ready("Austria", world)

    def test_survival_also_ready(self, world):
        from backend.game_logic.agendas import (
            agenda_separate_peace_ready, survival_override_active,
        )
        _conquer(world, "Vienna", "France")  # capital lost -> survival
        world.invalidate_bloc_members_cache()
        assert survival_override_active(world, "Austria")
        assert agenda_separate_peace_ready("Austria", world)

    def test_vassalized_never_ready(self, world):
        from backend.game_logic.agendas import agenda_separate_peace_ready
        self._satisfy_austria(world)
        world.vassals["Austria"] = {"lord": "France", "loyalty": 50,
                                    "autonomy": 1}
        world.invalidate_bloc_members_cache()
        assert not agenda_separate_peace_ready("Austria", world)

    def test_deckless_survival_still_ready(self, world):
        """DELIBERATE (adversarial-review pin): the survival arm needs no
        authored deck — the Knife at the Throat (§3.1) is universal, so a
        capital-lost coalition member on ANY world (legacy fixtures
        included) may break ranks to save the dynasty. A deckless nation
        with its capital HELD is never ready."""
        from backend.game_logic.agendas import agenda_separate_peace_ready
        world.agendas = {}
        world.invalidate_bloc_members_cache()
        assert not agenda_separate_peace_ready("Austria", world)
        _conquer(world, "Vienna", "France")
        world.invalidate_bloc_members_cache()
        assert agenda_separate_peace_ready("Austria", world)

    def test_satisfied_member_breaks_ranks(self, world):
        """The Pressburg pin pair: at war_score -49 (past the P1 threshold,
        NOT past the stock -50 coalition gate) a satisfied Austria sues for
        a separate armistice; the boot (denied) Austria stays loyal."""
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        key = world._make_diplo_key("Austria", "France")
        world.war_scores[key] = -49  # Austria (first in key) losing 49

        blocked = process_diplomatic_phase("Austria", world)
        assert blocked is None, (
            f"denied coalition member should stay loyal: {blocked}")

        self._satisfy_austria(world)
        proposal = process_diplomatic_phase("Austria", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "armistice_losing"
        assert proposal["source"] == "Austria"


class TestCourtingBias:
    def test_vassal_holds_agenda_target_pins(self, world):
        from backend.game_logic.agendas import vassal_holds_agenda_target
        # Austria's redeem_italy targets Milan/Piedmont — Kingdom of Italy soil
        assert vassal_holds_agenda_target("Austria", "KingdomOfItaly", world)
        assert not vassal_holds_agenda_target("Austria", "Holland", world)
        # Russia's contain posture wants no province of anyone
        assert not vassal_holds_agenda_target("Russia", "KingdomOfItaly", world)

    def test_austria_courts_the_kingdom_of_italy_first(self, world):
        """Dict order alone would court Holland (first vassal); the bias
        courts the vassal holding the design targets."""
        from backend.game_logic.vassal import attempt_vassal_courting
        assert list(world.vassals.keys())[0] == "Holland"
        for state in world.vassals.values():
            state["loyalty"] = 40
        world.nation_dp["Austria"] = 4
        events = attempt_vassal_courting(world, "Austria")
        courted = [e for e in events if e["type"] == "vassal_courting"]
        assert courted and courted[0]["vassal"] == "KingdomOfItaly"

    def test_unconcerned_courter_keeps_stock_order(self, world):
        """Russia (contain posture) has no territorial design — the bias
        is inert and dict order stands."""
        from backend.game_logic.vassal import attempt_vassal_courting
        for state in world.vassals.values():
            state["loyalty"] = 40
        world.nation_dp["Russia"] = 4
        events = attempt_vassal_courting(world, "Russia")
        courted = [e for e in events if e["type"] == "vassal_courting"]
        assert courted and courted[0]["vassal"] == "Holland"


# ═══════════════════ NA-2: STANCE-LINE COPY FIX ═══════════════════════════

class TestStanceLineCopy:
    def test_eponymous_holder_reads_as_coveting(self, world):
        """The live wart from the July 17 in-game review: 'Their court will
        not rest while Hanover holds Hanover.'"""
        payload = build_agenda_payload("Prussia", world)
        assert payload is not None
        assert "Hanover holds Hanover" not in payload["stance_line"]
        assert payload["stance_line"] == (
            "Their court will not rest while Hanover remains beyond "
            "their grasp.")

    def test_distinct_holder_copy_unchanged(self, world):
        payload = build_agenda_payload("Austria", world)
        assert payload is not None
        assert payload["stance_line"] == (
            "Their court will not rest while Kingdom of Italy holds Milan.")
