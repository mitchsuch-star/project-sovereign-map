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
        # Pin flipped consciously at AI-0d (docs/AI_INTENT_SPEC.md §12.2):
        # Russia allied INTO the hegemon's bloc still deactivates
        # arbiter_of_europe (the contain predicate this test pins), but the
        # deck no longer ends there — the second design, gulf_and_straits,
        # takes over by deck priority. That is the Tilsit route: a Russia
        # in France's camp turns toward the Gulf and the Straits.
        key = world._make_diplo_key("Russia", "France")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        view = get_active_agenda("Russia", world)
        assert view is not None and view.id == "gulf_and_straits"

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

class TestInvertedHegemonyGeometry:
    """PHASE REGRESSION (phase review, July 18, 2026).

    `_hegemon` consumed `coalition._identify_max_bloc_share` raw — "who is
    biggest" — which is the wrong question for an ANTI-hegemon design.
    Coalition formation produces real ALLIANCE states, so once the
    anti-France bloc out-massed France the raw answer became Britain's own
    ally, and every deny/contain/paymaster predicate switched off: the
    designs deleted themselves at the moment they began to succeed, the
    subsidy that funds the coalition stopped, and Britain's deny even read
    SATISFIED while France held the Scheldt — worth +10 resolve and an
    early separate peace for winning nothing.

    Court-relative resolution (the largest bloc the court is NOT in) keeps
    a design pointed at the power it was authored against.
    """

    def _coalition_outmasses_france(self, world):
        """Grow the coalition from NEUTRAL soil, never from France.

        France therefore keeps its boot share (still a hegemon by the
        §3.1 floor, so deny/contain stay legitimately ACTIVE) while the
        allied bloc grows past it — isolating the inverted-geometry
        variable from the unrelated below-the-floor dormancy rule.
        """
        for a, b in (("Austria", "Britain"), ("Austria", "Russia"),
                     ("Britain", "Russia")):
            world.diplomatic_states[world._make_diplo_key(a, b)] = "ALLIANCE"
        protected = set(world.get_bloc_members("France")) | {
            "Austria", "Britain", "Russia",
        }
        taken = 0
        for name, region in list(world.regions.items()):
            # France keeps every province; so do the coalition members
            # (losing their own homeland would trip the survival override
            # and mask the behavior under test).
            if region.controller in protected:
                continue
            if taken < 40:
                region.controller = "Austria"
                taken += 1
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        world._agenda_cache = None
        return world

    def test_setup_actually_inverts_the_raw_hegemon(self, world):
        """Guard the guard: if this stops flipping, the tests below go
        vacuous. France must ALSO stay above the §3.1 floor, or the
        designs would be dormant for an unrelated (authored) reason."""
        from backend.game_logic.agendas import HEGEMON_BLOC_SHARE_FLOOR
        from backend.game_logic.coalition import _identify_max_bloc_share
        assert _identify_max_bloc_share(world)[0] == "France"
        self._coalition_outmasses_france(world)
        assert _identify_max_bloc_share(world)[0] == "Austria"
        from backend.game_logic.agendas import _hegemon
        assert _hegemon(world, "Britain")[1] >= HEGEMON_BLOC_SHARE_FLOOR

    def test_the_court_still_fears_the_power_it_was_authored_against(self, world):
        from backend.game_logic.agendas import _hegemon
        self._coalition_outmasses_france(world)
        assert _hegemon(world)[0] == "Austria", "raw view unchanged"
        assert _hegemon(world, "Britain")[0] == "France"
        assert _hegemon(world, "Russia")[0] == "France"

    def test_the_designs_survive_their_own_success(self, world):
        self._coalition_outmasses_france(world)
        britain = get_active_agenda("Britain", world)
        assert britain is not None and britain.id == "low_countries", (
            "Britain lost its design the moment its coalition out-massed France"
        )
        russia = get_active_agenda("Russia", world)
        assert russia is not None and russia.id == "arbiter_of_europe", (
            "Russia lost its design the moment its coalition out-massed France"
        )

    def test_the_paymaster_keeps_paying_the_coalition_it_funds(self, world):
        from backend.game_logic.agendas import get_paymaster_nation
        world.nation_gold["Britain"] = 9000
        self._coalition_outmasses_france(world)
        assert get_paymaster_nation(world) == "Britain"

    def test_deny_is_not_satisfied_while_the_denied_power_holds_the_targets(
            self, world):
        """The sharpest arm: France still holds the Scheldt."""
        from backend.game_logic.agendas import (
            agenda_separate_peace_ready, entry_satisfied,
        )
        self._coalition_outmasses_france(world)
        assert world.regions["Flanders"].controller == "France"
        low_countries = world.agendas["Britain"][0]
        assert low_countries["id"] == "low_countries"
        assert not entry_satisfied(world, "Britain", low_countries)
        assert get_agenda_resolve_delta("Britain", "Russia", world) == 0
        assert not agenda_separate_peace_ready("Britain", world)

    def test_the_share_floor_gates_activation_not_satisfaction(self, world):
        """An earlier cut returned satisfied below the floor ("the hegemon
        fell"), which is false while the cut-down power holds the targets."""
        from backend.game_logic.agendas import entry_satisfied
        # Cut France below the floor WITHOUT taking the Low Countries.
        keep = {"Flanders", "Brabant", "Amsterdam"}
        taken = 0
        for name, region in list(world.regions.items()):
            if region.controller == "France" and name not in keep and taken < 26:
                region.controller = "Austria"
                taken += 1
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        world._agenda_cache = None
        assert world.regions["Flanders"].controller == "France"
        assert not entry_satisfied(world, "Britain", world.agendas["Britain"][0])


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

    def test_counsel_requires_a_province_the_player_can_actually_cede(
            self, world):
        """PHASE REGRESSION: the counsel gated on BLOC control while
        `generate_suggested_terms` filters to the player's DIRECT holdings.
        With every target sitting in a VASSAL's hands the counsel still
        fired — costing an action, opening talks, and then offering an
        unrelated province that scored the design term at ENTRENCH, i.e.
        strictly worse than ignoring the advice. Mirrors the §16 narrowing
        already applied to NA-5's ultimatum trigger."""
        from backend.game_logic.agendas import get_agenda_covets
        player = world.player_nation
        direct = set(world.get_nation_regions(player))
        assert "Savoy" in direct, "boot control: France holds Savoy directly"
        assert agenda_satisfiable_by_player("Austria", world)

        # Hand the one direct target to a vassal — nothing Austria wants is
        # now France's to sign away.
        world.regions["Savoy"].controller = "KingdomOfItaly"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()
        world._agenda_cache = None
        assert get_agenda_covets("Austria", world), "still coveted, just unsignable"
        assert not set(get_agenda_covets("Austria", world)) & set(
            world.get_nation_regions(player))
        assert not agenda_satisfiable_by_player("Austria", world), (
            "the war room promised a cession the player cannot make"
        )

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


# ═══════════════════ NA-3: RESOLVE WIRING (§5.5) ══════════════════════════

def _set_war_score(world, nation, opponent, score_for_nation):
    """Store a war score expressed from `nation`'s perspective."""
    key = world._make_diplo_key(nation, opponent)
    first = key.split("|")[0]
    world.war_scores[key] = (int(score_for_nation) if first == nation
                             else -int(score_for_nation))


class TestResolveWiring:
    """§5.5 — get_agenda_resolve_delta is CONSUMED at the P1 seam.
    Austria's diplomat is a schemer (peace_threshold_delta 0), boot WE 0,
    no war objectives → the stock effective threshold is exactly -40."""

    def test_advancing_design_holds_the_court_in_the_war(self, world):
        """France's bloc holds Milan — the war ADVANCES redeem_italy, so
        the threshold hardens -40 → -48 and Austria at -45 fights on.
        Deleting the §5.5 wiring fails the second half: the same score
        with the deck stripped sues immediately."""
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        world.active_coalition = None  # isolate P1 from the loyalty gate
        _set_war_score(world, "Austria", "France", -45)
        result = process_diplomatic_phase("Austria", world)
        assert result is None or result.get("proposal_type") not in (
            "peace", "armistice_losing")

        world.agendas = {}
        world.invalidate_bloc_members_cache()
        result = process_diplomatic_phase("Austria", world)
        assert (result is not None
                and result["proposal_type"] == "armistice_losing")

    def test_satisfied_design_sues_sooner_and_breaks_ranks(self, world):
        """Austria holding all of redeem_italy sues at -35 (threshold
        -40 → -30) THROUGH the boot coalition — the Pressburg arm
        (-35 < -30) unlocks the loyalty gate the same turn the resolve
        delta opens the P1 gate: §5.4's 'completed by NA-3' note."""
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        _set_war_score(world, "Austria", "France", -35)
        result = process_diplomatic_phase("Austria", world)
        assert result is None  # advancing design: -35 is nowhere near -48

        for region in ("Milan", "Piedmont", "Savoy"):
            _conquer(world, region, "Austria")
        world.invalidate_bloc_members_cache()
        result = process_diplomatic_phase("Austria", world)
        assert (result is not None
                and result["proposal_type"] == "armistice_losing")


# ═══════════════════ NA-3: ENEMY TARGET BIAS (§5.6) ═══════════════════════

class TestTargetBias:
    @pytest.fixture
    def ai(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        return EnemyAI(CommandExecutor())

    def test_covet_set_derives_from_the_active_design(self, ai, world):
        covets = ai._agenda_covet_set("Austria", world)
        assert covets == {"Milan", "Piedmont", "Savoy"}
        assert ai._agenda_covet_set("France", world) == frozenset()

    def test_deny_design_never_drives_self_conquest(self, ai, world):
        """§3.1 contract (review fix): deny's expressions are resolve/
        acceptance/subsidy targeting — NEVER self-conquest. Britain's
        low_countries deny is boot-active, its diplomatic covets are
        live, but its corps get NO military pull toward Flanders."""
        from backend.game_logic.agendas import (
            get_active_agenda, get_agenda_covets,
        )
        assert get_active_agenda("Britain", world).type == "deny_regions"
        assert get_agenda_covets("Britain", world)  # diplomacy still sees it
        assert ai._agenda_covet_set("Britain", world) == frozenset()

    def test_strategic_enemy_regions_order_agenda_targets_first(
            self, ai, world):
        """§5.6 — min-by-distance callers resolve ties to first-seen, so
        the design's provinces lead the coarse target list."""
        _war(world, "Austria", "KingdomOfItaly")
        regions = ai._get_strategic_enemy_regions("Austria", world)
        assert "Milan" in regions
        covets = ai._agenda_covet_set("Austria", world)
        first_non_covet = next(
            (i for i, r in enumerate(regions) if r not in covets),
            len(regions))
        assert all(r in covets for r in regions[:first_non_covet])
        assert not any(r in covets for r in regions[first_non_covet:])

    def test_p4_aggressive_tiebreak_prefers_the_design(self, ai, world):
        """Equal effective ratio: the enemy standing on Milan wins the
        pick; a strictly better ratio elsewhere still wins (gates and
        strict orderings untouched)."""
        from types import SimpleNamespace
        on_covet = SimpleNamespace(name="A", location="Milan")
        elsewhere = SimpleNamespace(name="B", location="Paris")
        attackable = [(elsewhere, 1.5, 1.5, 1), (on_covet, 1.5, 1.5, 1)]
        pick = ai._pick_personality_target(
            attackable, "aggressive", "Austria", world)
        assert pick is on_covet
        attackable = [(elsewhere, 1.6, 1.6, 1), (on_covet, 1.5, 1.5, 1)]
        pick = ai._pick_personality_target(
            attackable, "aggressive", "Austria", world)
        assert pick is elsewhere

    def test_p4_nearest_pick_gets_two_hops_of_credit(self, ai, world):
        from types import SimpleNamespace
        from backend.game_logic.agendas import AGENDA_TARGET_DISTANCE_BONUS
        assert AGENDA_TARGET_DISTANCE_BONUS == 2
        on_covet = SimpleNamespace(name="A", location="Milan")
        nearer = SimpleNamespace(name="B", location="Paris")
        # Milan at 3 hops beats a non-design target at 2 (3-2 < 2)…
        attackable = [(nearer, 1.5, 1.5, 2), (on_covet, 1.5, 1.5, 3)]
        pick = ai._pick_personality_target(
            attackable, "cautious", "Austria", world)
        assert pick is on_covet
        # …but never one engaged in the same region (credit is bounded).
        attackable = [(nearer, 1.5, 1.5, 0), (on_covet, 1.5, 1.5, 3)]
        pick = ai._pick_personality_target(
            attackable, "cautious", "Austria", world)
        assert pick is nearer

    def test_p7_distance_credit_only_for_covets(self, ai, world):
        real = world.get_distance("Vienna", "Milan")
        biased = ai._agenda_biased_distance("Vienna", "Milan", "Austria", world)
        assert biased == real - 2
        assert (ai._agenda_biased_distance("Vienna", "Milan", "France", world)
                == world.get_distance("Vienna", "Milan"))

    def test_deckless_world_is_byte_identical(self, ai, world):
        """Legacy guard: no decks → empty covets → every bias inert."""
        world.agendas = {}
        world.invalidate_bloc_members_cache()
        assert ai._agenda_covet_set("Austria", world) == frozenset()
        assert (ai._agenda_biased_distance("Vienna", "Milan", "Austria", world)
                == world.get_distance("Vienna", "Milan"))

    def test_p4_flow_routes_through_the_biased_pick(
            self, ai, world, monkeypatch):
        """Review fix pin: the P4 CALL-SITE — reverting the pick site to
        the pre-NA-3 inline max/min fails here, whatever the helpers do."""
        from backend.ai.enemy_ai import EnemyAI
        calls = []
        original = EnemyAI._pick_personality_target

        def spy(self, attackable, personality, nation, w):
            calls.append(nation)
            return original(self, attackable, personality, nation, w)

        monkeypatch.setattr(EnemyAI, "_pick_personality_target", spy)
        mack = world.marshals["Mack"]
        ney = world.marshals["Ney"]
        ney.location = "Bavaria"          # adjacent to Mack@Swabia
        ney.strength = 1000               # easy odds for the Austrian
        mack.strength = 60000
        action = ai._find_attack_opportunity(mack, "Austria", world)
        assert calls, "P4 must route its pick through the NA-3 helper"
        assert action is not None and action["action"] == "attack"

    def test_p7_flow_routes_through_the_biased_distance(
            self, ai, world, monkeypatch):
        """Review fix pin: the P7 CALL-SITE — the aggressive nearest-
        target choice must consult the agenda-biased distance."""
        from backend.ai.enemy_ai import EnemyAI
        calls = []
        original = EnemyAI._agenda_biased_distance

        def spy(self, from_region, to_region, nation, w):
            calls.append((from_region, to_region))
            return original(self, from_region, to_region, nation, w)

        monkeypatch.setattr(EnemyAI, "_agenda_biased_distance", spy)
        # Massena@Milan: aggressive, un-fortified, and NOT co-located
        # (the P4.76 guard bails for paired corps like Murat+Lannes).
        massena = world.marshals["Massena"]
        result = ai._consider_strategic_move(massena, "France", world)
        assert calls, "P7 must route target choice through the NA-3 helper"
        assert result is None or result.get("action") in ("move", "attack")


# ═══════════════════ NA-3: PAYMASTER TIERS (§5.7) ═════════════════════════

class TestPaymasterTiers:
    def test_boot_sits_exactly_at_the_floor(self, world1805):
        """Britain boots at 2,000 — the authored floor is EXCLUSIVE
        (the NA-0 pin), so the boot turn pays nothing; the first gold
        above the floor opens Pitt's purse."""
        from backend.game_logic.agendas import get_paymaster_nation
        assert get_paymaster_nation(world1805) is None

    def test_tier_ladder_and_cap(self, world):
        from backend.game_logic.agendas import (
            get_paymaster_nation, get_paymaster_subsidy_amount,
        )
        for treasury, expected in ((2001, 200), (4000, 200), (4001, 300),
                                   (8000, 300), (8001, 400), (999999, 400)):
            world.nation_gold["Britain"] = treasury
            assert get_paymaster_nation(world) == "Britain"
            assert get_paymaster_subsidy_amount(world, "Britain") == expected

    def test_subsidy_event_carries_the_tiered_amount(self, world):
        from backend.game_logic.coalition import _process_british_subsidy
        world.nation_gold["Britain"] = 8001
        events = _process_british_subsidy(world)
        assert events and events[0]["type"] == "british_subsidy"
        assert events[0]["payer"] == "Britain"
        assert events[0]["recipient"] == "Austria"
        assert events[0]["amount"] == 400
        assert world.nation_gold["Britain"] == 8001 - 400

    def test_gr5_any_authored_paymaster_pays(self, world):
        """A non-Britain paymaster works through the same seam — the
        Britain literal is gone."""
        from backend.game_logic.coalition import _process_british_subsidy
        world.nation_gold["Britain"] = 100   # below floor AND solvency
        world.agendas["Russia"] = [{
            "id": "war_chest", "type": "paymaster",
            "title": "The War Chest", "treasury_floor": 1000,
        }]
        world.nation_gold["Russia"] = 5000
        world.invalidate_bloc_members_cache()
        events = _process_british_subsidy(world)
        assert events and events[0]["payer"] == "Russia"
        assert events[0]["amount"] == 300

    def test_gr5_paymaster_contribution_attributes_to_the_payer(self, world):
        """Review fix pin: the war-attribution resolver is keyed on the
        actual SUPPORTER — a non-Britain paymaster's war_support_delivered
        accrues against the war IT shares with the recipient (the old
        Britain literal silently dropped it)."""
        from backend.game_logic.coalition import _process_british_subsidy
        world.nation_gold["Britain"] = 100
        world.agendas["Russia"] = [{
            "id": "war_chest", "type": "paymaster",
            "title": "The War Chest", "treasury_floor": 1000,
        }]
        world.nation_gold["Russia"] = 5000
        world.invalidate_bloc_members_cache()
        events = _process_british_subsidy(world)
        # Russia and Austria share the boot Third-Coalition defenders'
        # side of war_1 — the transfer must attribute there.
        assert events and events[0]["war_id"] == "war_1"
        assert events[0]["subsidy_source_detail"] != "unattributed_subsidy"

    def test_survival_override_closes_the_purse(self, world):
        """A paymaster fighting for its life ships no gold abroad."""
        from backend.game_logic.agendas import get_paymaster_nation
        world.nation_gold["Britain"] = 9000
        capital = world.get_nation_capital("Britain")
        _conquer(world, capital, "France")
        world.invalidate_bloc_members_cache()
        assert get_paymaster_nation(world) is None

    def test_legacy_world_keeps_the_britain_literal(self):
        """Deckless worlds ride the historical arm byte-identically:
        Britain literal, 500-gold gate, flat 200."""
        from backend.game_logic.agendas import (
            get_paymaster_nation, get_paymaster_subsidy_amount,
        )
        legacy = WorldState()
        legacy.active_coalition = {
            "members": ["Britain", "Austria"], "target_nation": "France",
        }
        legacy.nation_gold["Britain"] = 501
        assert get_paymaster_nation(legacy) == "Britain"
        assert get_paymaster_subsidy_amount(legacy, "Britain") == 200
        legacy.nation_gold["Britain"] = 500
        assert get_paymaster_nation(legacy) is None


# ═══════════════════ NA-3: THE POST-PEACE GRUDGE (§5.8) ═══════════════════

def _end_war_with_france(world, nation, turns_ago):
    """Plant an ENDED war instance between France and `nation` in the
    PRODUCTION shape (review fix): the war-end path strips side_by_nation
    as participants exit, so an ended instance carries its sides only in
    participant_meta (with per-nation exited_turn stamped). The pair is
    set back to PEACE (the settlement package's post-ratify state)."""
    key = world._make_diplo_key("France", nation)
    world.diplomatic_states[key] = "PEACE"
    world.invalidate_bloc_members_cache()
    end = int(world.current_turn) - int(turns_ago)
    world.war_instances[f"war_grudge_{nation}"] = {
        "war_id": f"war_grudge_{nation}",
        "ended_turn": end,
        "side_by_nation": {},   # stripped on end — the production shape
        "active_participants": [],
        "participant_meta": {
            "France": {"side": "attackers", "exited_turn": end,
                       "exit_path": "war_ended"},
            nation: {"side": "defenders", "exited_turn": end,
                     "exit_path": "war_ended"},
        },
    }


class TestAgendaGrudge:
    def test_denied_design_after_peace_feeds_threat(self, world):
        from backend.game_logic.agendas import get_agenda_grudge_nations
        _end_war_with_france(world, "Austria", 1)
        assert get_agenda_grudge_nations(world) == ["Austria"]

    def test_contributor_reaches_the_threat_panel(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        _end_war_with_france(world, "Austria", 1)
        world.threat_sources_this_turn = []
        process_coalition_turn(world)
        sources = {s["source"]: s["amount"]
                   for s in world.threat_sources_this_turn}
        assert sources.get("agenda_grudge") == 1

    def test_cap_across_nations(self, world):
        from backend.game_logic.agendas import (
            AGENDA_GRUDGE_CAP, get_agenda_grudge_nations,
        )
        from backend.game_logic.coalition import (
            _calculate_agenda_grudge_threat,
        )
        for nation in ("Austria", "Britain", "Sardinia"):
            _end_war_with_france(world, nation, 1)
        assert len(get_agenda_grudge_nations(world)) == 3
        assert _calculate_agenda_grudge_threat(world) == AGENDA_GRUDGE_CAP

    def test_grudge_expires_with_the_horizon(self, world):
        from backend.game_logic.agendas import (
            AGENDA_GRUDGE_TURNS, get_agenda_grudge_nations,
        )
        world.current_turn = 20
        _end_war_with_france(world, "Austria", AGENDA_GRUDGE_TURNS)
        assert get_agenda_grudge_nations(world) == []

    def test_returning_the_targets_dissolves_the_grudge(self, world):
        """The R156 payoff: cede the design and the grudge is gone the
        same turn (Sardinia's single-entry deck goes quiet once Piedmont
        and Savoy come home)."""
        from backend.game_logic.agendas import get_agenda_grudge_nations
        _end_war_with_france(world, "Sardinia", 1)
        assert "Sardinia" in get_agenda_grudge_nations(world)
        for region in ("Piedmont", "Savoy"):
            _conquer(world, region, "Sardinia")
        world.invalidate_bloc_members_cache()
        assert "Sardinia" not in get_agenda_grudge_nations(world)

    def test_live_or_resumed_war_is_not_a_grudge(self, world):
        from backend.game_logic.agendas import get_agenda_grudge_nations
        # Unended instance (armistice-shaped): no grudge.
        world.war_instances["war_x"] = {
            "war_id": "war_x", "ended_turn": None,
            "side_by_nation": {"France": "attackers", "Austria": "defenders"},
        }
        assert get_agenda_grudge_nations(world) == []
        # Ended-but-back-at-war: the grudge IS the war now.
        _end_war_with_france(world, "Austria", 1)
        _war(world, "France", "Austria")
        assert get_agenda_grudge_nations(world) == []

    def _separate_peace_austria(self, world):
        """Resolve every one of Austria's pairs on the BOOT Third-
        Coalition instance (war_1) — what a real separate peace does:
        Austria settles with the whole French bloc and exits."""
        from backend.game_logic.settlement_helpers import (
            resolve_pair_to_resolved,
        )
        instance = world.war_instances["war_1"]
        for other in ("France", "Bavaria", "KingdomOfItaly"):
            pair = world._make_diplo_key("Austria", other)
            if pair in (instance.get("active_diplo_keys") or []):
                resolve_pair_to_resolved(world, pair)
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()
        return instance

    def test_separate_peace_exit_grudges_while_the_war_burns_on(self, world):
        """The Pressburg/1809 case (review P1/P2 fix pin) on the REAL
        boot instance and the REAL exit path: Austria separate-peaces
        out of the live Third Coalition — resolve_pair_to_resolved pops
        it from side_by_nation and stamps participant_meta exited_turn
        while the instance fights on. The grudge fires from Austria's
        OWN exit, not the whole war's distant end."""
        from backend.game_logic.agendas import get_agenda_grudge_nations
        instance = self._separate_peace_austria(world)
        assert instance["ended_turn"] is None       # Britain/Russia fight on
        assert "Austria" not in instance["side_by_nation"]  # the strip
        meta = instance["participant_meta"]["Austria"]
        assert meta["exited_turn"] is not None
        assert meta["side"] == "defenders"          # side survives exit
        grudged = get_agenda_grudge_nations(world)
        assert "Austria" in grudged
        assert "Britain" not in grudged  # still fighting — no grudge

    def test_production_war_end_path_fires_the_grudge(self, world):
        """Review P1 fix pin: resolving the LAST pair stamps ended_turn
        and strips side_by_nation EMPTY — the derivation must read
        participant_meta or the grudge is structurally dead on every
        real resolution path."""
        from backend.game_logic.agendas import get_agenda_grudge_nations
        from backend.game_logic.settlement_helpers import (
            resolve_pair_to_resolved,
        )
        instance = world.war_instances["war_1"]
        for pair in list(instance.get("active_diplo_keys") or []):
            resolve_pair_to_resolved(world, pair)
        assert instance["ended_turn"] is not None
        assert instance["side_by_nation"] == {}     # the production strip
        for nation in ("Austria", "Britain", "Russia"):
            key = world._make_diplo_key("France", nation)
            world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()
        assert "Austria" in get_agenda_grudge_nations(world)


# ═══════════════════ NA-3: THE ANSBACH TRAP (§5.9) ════════════════════════

class TestNeutralityViolation:
    def _relation(self, world, a, b):
        return world.nation_relations.get(world._make_diplo_key(a, b), 0)

    def test_player_columns_offend_copenhagen(self, world):
        """GR5 canonical case: belligerent France's marshal in Jutland
        (Denmark's ACTIVE guard) → one-time -25 + dispatch + campaign log."""
        from backend.game_logic.agendas import (
            AGENDA_VIOLATION_RELATION_PENALTY, process_agenda_violations,
        )
        before = self._relation(world, "France", "Denmark")
        world.marshals["Ney"].location = "Jutland"
        events = process_agenda_violations(world)
        assert [(e["violator"], e["guard_holder"]) for e in events] == [
            ("France", "Denmark")]
        assert (self._relation(world, "France", "Denmark")
                == max(-100, before + AGENDA_VIOLATION_RELATION_PENALTY))
        assert any(e.get("type") == "agenda_violation"
                   for e in world.event_log)
        assert any(e.get("type") == "agenda_violation"
                   for e in world.pending_dispatch_events)

    def test_latch_fires_once_per_pair_per_cooldown(self, world):
        from backend.game_logic.agendas import (
            AGENDA_VIOLATION_COOLDOWN, process_agenda_violations,
        )
        world.marshals["Ney"].location = "Jutland"
        # Two French corps in two guard regions: still ONE beat per pair.
        world.marshals["Davout"].location = "Copenhagen"
        assert len(process_agenda_violations(world)) == 1
        assert process_agenda_violations(world) == []
        world.current_turn += AGENDA_VIOLATION_COOLDOWN
        assert len(process_agenda_violations(world)) == 1

    def test_ai_violator_pays_the_same(self, world):
        """GR5 mirror: a British column in Jutland (Britain at war with
        France, at peace with Denmark) offends Copenhagen identically."""
        from backend.game_logic.agendas import process_agenda_violations
        british = [m for m in world.marshals.values()
                   if m.nation == "Britain"]
        assert british, "1805 roster should field a British marshal"
        british[0].location = "Jutland"
        events = process_agenda_violations(world)
        assert [(e["violator"], e["guard_holder"]) for e in events] == [
            ("Britain", "Denmark")]

    def test_exemptions_hold(self, world):
        from backend.game_logic.agendas import process_agenda_violations
        from backend.game_logic.diplomacy import set_diplomatic_state
        world.marshals["Ney"].location = "Jutland"
        # Ally: France allied to Denmark → its columns are no outrage.
        set_diplomatic_state(world, "France", "Denmark", "ALLIANCE", "test")
        assert process_agenda_violations(world) == []
        # Open war with the holder supersedes outrage (and deactivates
        # the guard itself — _guard_active requires peace).
        set_diplomatic_state(world, "France", "Denmark", "WAR", "test")
        assert process_agenda_violations(world) == []

    def test_peaceful_nation_never_offends(self, world):
        """Only a belligerent's columns violate — France at peace with
        the whole world may cross Jutland freely."""
        from backend.game_logic.agendas import process_agenda_violations
        for nation in list(world.get_nations_at_war_with("France")):
            key = world._make_diplo_key("France", nation)
            world.diplomatic_states[key] = "PEACE"
        world.invalidate_bloc_members_cache()
        world.marshals["Ney"].location = "Jutland"
        assert process_agenda_violations(world) == []

    def test_latent_guard_prices_nothing(self, world):
        """Prussia's armed_neutrality is deck-LATENT behind the
        hanoverian_prize — Berlin is not yet a priced guard region."""
        from backend.game_logic.agendas import process_agenda_violations
        world.marshals["Ney"].location = "Berlin"
        assert process_agenda_violations(world) == []

    def test_courier_remnants_do_not_trigger(self, world):
        from backend.game_logic.agendas import process_agenda_violations
        world.marshals["Ney"].location = "Jutland"
        world.marshals["Ney"].strength = 999
        assert process_agenda_violations(world) == []

    def test_own_soil_is_never_a_violation(self, world):
        """Review fix pin: a garrison on a legally-held (treaty-ceded)
        province is no transit — Denmark's reactivated guard over a now-
        FRENCH Jutland cannot bleed France -25 forever."""
        from backend.game_logic.agendas import process_agenda_violations
        _conquer(world, "Jutland", "France")
        world.invalidate_bloc_members_cache()
        world.marshals["Ney"].location = "Jutland"
        assert process_agenda_violations(world) == []
        # The other guard region is still Danish — crossing IT violates.
        world.marshals["Ney"].location = "Copenhagen"
        assert len(process_agenda_violations(world)) == 1

    def test_rolled_event_log_fails_safe(self, world):
        """Review fix pin: when the 500-entry rolling cap has evicted
        events INSIDE the cooldown window, the latch cannot prove a
        prior firing was absent — it suppresses rather than re-fires."""
        from backend.game_logic.agendas import process_agenda_violations
        world.marshals["Ney"].location = "Jutland"
        cap = world.MAX_EVENT_LOG_SIZE
        world.event_log = [
            {"type": "noise", "turn": int(world.current_turn)}
            for _ in range(cap)
        ]
        assert process_agenda_violations(world) == []
        # Old traffic (outside the window) proves nothing was evicted
        # in-window — the trap fires normally.
        world.event_log = [
            {"type": "noise", "turn": int(world.current_turn) - 50}
            for _ in range(cap)
        ]
        assert len(process_agenda_violations(world)) == 1

    def test_advance_turn_runs_the_violation_pass(self, world):
        """Review fix pin: the world_state wiring itself — deleting the
        process_agenda_violations call from _advance_turn_internal must
        fail HERE, not just in the helper tests."""
        world.marshals["Ney"].location = "Jutland"
        key = world._make_diplo_key("France", "Denmark")
        before = world.nation_relations.get(key, 0)
        world.advance_turn()
        assert any(e.get("type") == "agenda_violation"
                   for e in world.event_log)
        assert world.nation_relations.get(key, 0) <= before - 25


# ═══════════════════ NA-3 RIDER (a): SETTLEMENT TERM ══════════════════════

class TestSettlementAgendaTerm:
    def _score(self, world, terms, accepting_leader="Austria"):
        from backend.game_logic import settlement_scoring
        from tests.helpers.full_europe_settlement_fixtures import (
            make_synthetic_war_instance,
        )
        instance = make_synthetic_war_instance(
            "war_na3", attackers=["France"], defenders=["Austria"],
            attacker_leader="France", defender_leader="Austria",
        )
        return settlement_scoring.calculate_common_peace_acceptance(
            world,
            war_id="war_na3",
            war_instance=instance,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader=accepting_leader,
            covered_enemy_participants=["Austria"],
            settlement_terms=terms,
        )

    def test_ceding_the_design_target_raises_the_court(self, world):
        """The §7 rider-(a) pin: a settlement clause ceding a design
        target raises that court's acceptance by AGENDA_ACCEPT_ADVANCE."""
        from backend.game_logic.agendas import AGENDA_ACCEPT_ADVANCE
        _set_war_score(world, "France", "Austria", 50)
        result = self._score(world, [{
            "type": "territory", "from": "France", "to": "Austria",
            "regions": ["Savoy"],
        }])
        assert (result["components"]["agenda_settlement_mod"]
                == AGENDA_ACCEPT_ADVANCE)
        assert "agenda_settlement_mod" in result["component_debug"]

    def test_the_peace_that_returns_nothing_entrenches(self, world):
        """France's bloc holds Milan and the package returns no design
        region — the common peace prices Austria's denial at -8."""
        from backend.game_logic.agendas import AGENDA_ACCEPT_ENTRENCH
        _set_war_score(world, "France", "Austria", 50)
        result = self._score(world, [])
        assert (result["components"]["agenda_settlement_mod"]
                == AGENDA_ACCEPT_ENTRENCH)

    def test_stripping_a_held_design_region_entrenches(self, world):
        from backend.game_logic.agendas import AGENDA_ACCEPT_ENTRENCH
        _set_war_score(world, "France", "Austria", 50)
        _conquer(world, "Milan", "Austria")
        world.invalidate_bloc_members_cache()
        result = self._score(world, [{
            "type": "territory_cede", "from": "Austria", "to": "France",
            "regions": ["Milan"],
        }])
        assert (result["components"]["agenda_settlement_mod"]
                == AGENDA_ACCEPT_ENTRENCH)

    def test_deckless_court_scores_zero(self, world):
        _set_war_score(world, "France", "Austria", 50)
        result = self._score(world, [], accepting_leader="Spain")
        assert result["components"]["agenda_settlement_mod"] == 0

    def test_component_has_a_display_label(self):
        from backend.display_names import ACCEPTANCE_COMPONENT_DISPLAY
        assert (ACCEPTANCE_COMPONENT_DISPLAY["agenda_settlement_mod"]
                == "National design")


# ═══════════════════ NA-3 RIDER (b): PREVIEW POSITIVE ROW ═════════════════

class TestPreviewPositiveRow:
    def _armistice_fixture(self, world):
        """The designed armistice-first route (the Pressburg shape): the
        pause holds, relations recover, and the peace on the table cedes
        Savoy — a live design target France itself controls."""
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ARMISTICE"
        world.invalidate_bloc_members_cache()
        _set_war_score(world, "France", "Austria", -10)
        world.nation_relations[key] = 40

    def test_suggested_peace_reaches_the_positive_row(self, world):
        """The §7 rider-(b) pin: the peace-class preview scores the
        SUGGESTED terms (which inject the design cession), so '+12
        Advances their design' finally appears among the positives —
        unreachable on the pre-NA-3 bare mock."""
        from backend.game_logic.diplomacy import get_diplomatic_preview
        self._armistice_fixture(world)
        preview = get_diplomatic_preview(world, "Austria")
        acceptance = preview.get("acceptance_preview") or {}
        positives = acceptance.get("positive") or []
        agenda_rows = [e for e in positives if e["key"] == "agenda_mod"]
        assert agenda_rows, f"agenda_mod missing from positives: {positives}"
        assert agenda_rows[0]["label"] == "Advances their design"
        assert agenda_rows[0]["value"] == 12

    def test_preview_and_snapshot_describe_the_same_bargain(
            self, world, monkeypatch):
        """The memo pin (review-hardened): ONE generate_suggested_terms
        call serves both the R17d score and the BPH-B snapshot — the
        counting wrapper fails on a memo revert (clause identity alone is
        deterministic and could not detect two independent jitter rolls)."""
        import backend.game_logic.diplomatic_templates as templates
        from backend.game_logic.diplomacy import get_diplomatic_preview
        self._armistice_fixture(world)
        calls = []
        original = templates.generate_suggested_terms

        def counting(target, ptype, w):
            calls.append(ptype)
            return original(target, ptype, w)

        monkeypatch.setattr(
            templates, "generate_suggested_terms", counting)
        preview = get_diplomatic_preview(world, "Austria")
        snapshot = (preview.get("war_context_snapshots") or {}).get(
            "propose_peace")
        assert snapshot is not None
        clauses = snapshot["proposal_terms"].get("clauses", [])
        assert "territory_savoy" in clauses
        assert calls.count("peace") == 1, (
            f"memo broken — generate_suggested_terms ran {calls}")
