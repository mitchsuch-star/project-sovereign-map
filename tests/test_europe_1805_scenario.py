"""1805 Scenario Setup gate — the authored ``europe_1805.json`` campaign opening.

Owns the gate's Tests line (docs/MAP_IMPLEMENTATION_PLAN.md §"1805 Scenario
Setup"): marshals on valid owned provinces (with the three blessed
off-controller placements), a symmetric + valid 1805 diplomatic matrix,
turn-advance stability, and the carried ``allied_region_restored`` Europe
treaty-cession behavior test from the Slice 5 fold.

Also pins the two loader folds this slice landed:
- omitted-``regions`` scenario injection stamps controllers + capital
  garrisons (mirrors ``_setup_initial_control``) — without it the scenario
  world loads controller-less (zero income, no supply, no capturable land);
- authored army-less nations are pre-seeded into the enemy-phase
  "forces are spent" notification dedupe (they are army-less, not eliminated).
"""

import json
from pathlib import Path

import pytest

from backend.game_logic.coalition import get_british_subsidy_recipient
from backend.game_logic.diplomacy import get_relation
from backend.game_logic.war_contribution import current_episode
from backend.models.region import get_starting_controllers
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)

# The three blessed off-controller placements (gate decisions 4 + roster table):
# marshal -> (province, province's 1805 controller).
AUTHORED_OFF_CONTROLLER = {
    "Mack": ("Swabia", "Bavaria"),          # invasion in progress (hostile soil)
    "Bernadotte": ("Franconia", "Bavaria"),  # allied Bavarian soil (Bogenhausen)
    "Massena": ("Milan", "KingdomOfItaly"),  # French-satellite soil
}

# The researched relations matrix (plan §"Researched 1805 opening draft"),
# sorted-pipe keys. War pairs not named in the plan's relations list carry the
# legacy at-war seed (-80): Austria|Bavaria, Britain|Holland, Austria|KingdomOfItaly.
EXPECTED_RELATIONS = {
    "Britain|France": -90,
    "Austria|France": -80,
    "France|Russia": -80,
    "Britain|Spain": -80,
    "Austria|Bavaria": -80,
    "Britain|Holland": -80,
    "Austria|KingdomOfItaly": -80,
    "Britain|Russia": 70,
    "Bavaria|France": 60,
    "Austria|Britain": 60,
    "Austria|Russia": 60,
    "Britain|Sweden": 50,
    "France|Spain": 40,
    "Britain|Portugal": 40,
    "Russia|Sweden": 40,
    "Naples|Russia": 40,
    "Britain|Naples": 30,
    "Prussia|Russia": 30,
    "Ottoman|Russia": 20,
    "Denmark|France": 10,
    "France|Prussia": -10,
    "France|Saxony": -10,
    "France|Portugal": -10,
    "France|PapalStates": -10,
    "France|Ottoman": -20,
    "France|Naples": -30,
    "France|Hanover": -50,
    "France|Sweden": -60,
    "France|Sardinia": -70,
}

WAR_PAIRS = (
    "Britain|France",
    "Austria|France",
    "France|Russia",
    "Britain|Spain",
    "Britain|Holland",
    "Austria|Bavaria",
    "Austria|KingdomOfItaly",
)

ALLIANCE_PAIRS = (
    ("France", "Spain"),
    ("Bavaria", "France"),
    ("Britain", "Russia"),
    ("Austria", "Britain"),
    ("Austria", "Russia"),
)

ARMYLESS_NATIONS = {
    "Portugal", "Saxony", "Hanover", "Hesse", "PapalStates", "Sardinia",
    "Holland", "KingdomOfItaly", "Switzerland",
}


def _load():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture(scope="module")
def world1805():
    """Read-only module world — mutating tests load their own via _load()."""
    return _load()


# ══════════════════════════ shape + placement ══════════════════════════


def test_scenario_loads_full_1805_world(world1805):
    assert world1805.sovereign_map == "europe"
    assert len(world1805.regions) == 126
    assert len(world1805.marshals) == 21
    assert world1805.player_nation == "France"
    assert world1805.current_turn == 1
    assert world1805.max_turns == 60


def test_every_marshal_placed_on_valid_owned_province(world1805):
    for name, marshal in world1805.marshals.items():
        region = world1805.regions.get(marshal.location)
        assert region is not None, f"{name} placed off-map at {marshal.location!r}"
        if name in AUTHORED_OFF_CONTROLLER:
            province, controller = AUTHORED_OFF_CONTROLLER[name]
            assert marshal.location == province
            assert region.controller == controller
            assert region.controller != marshal.nation
        else:
            assert region.controller == marshal.nation, (
                f"{name} ({marshal.nation}) stands on {marshal.location} "
                f"owned by {region.controller}"
            )


def test_region_control_and_garrisons_injected(world1805):
    """The omitted-`regions` injection must stamp the default world's control.

    DEF-6 (Slice 8): capital garrisons are tier-differentiated on Europe —
    majors 25k, secondary courts 15k, minors 10k — and the scenario's
    region_overrides stamps the Flanders Channel-coast depot (12k) so the
    London<->Flanders sea link is never a free walk into France."""
    assert world1805.regions["Paris"].controller == "France"
    assert world1805.regions["Swabia"].controller == "Bavaria"
    assert world1805.regions["Milan"].controller == "KingdomOfItaly"
    assert len(world1805.get_nation_regions("France")) == 28
    for capital in ("Paris", "London", "Vienna", "Berlin"):  # major courts
        assert world1805.regions[capital].garrison_strength == 25000
    assert world1805.regions["Madrid"].garrison_strength == 15000       # secondary
    assert world1805.regions["Amsterdam"].garrison_strength == 10000    # minor satellite
    assert world1805.regions["Copenhagen"].garrison_strength == 10000   # minor
    # nation_starting_regions derives from the loaded control (pre-slice item 3)
    assert "Paris" in world1805.nation_starting_regions.get("France", [])


def test_flanders_channel_depot_authored(world1805):
    """DEF-6: the region_overrides Flanders garrison sits above the P4.5
    walk-in gate (>= 5,000) — Britain cannot enter France unopposed."""
    assert world1805.regions["Flanders"].garrison_strength == 12000
    assert world1805.regions["Flanders"].controller == "France"


def test_cr5_literal_arm_player_reachable(world1805):
    """CR-5 (Personality-Biased Disambiguation) needs a commandable LITERAL
    marshal so the "asks for clarification" arm is player-reachable (all three
    enemy literals — Mack/Deroy/Buxhowden — are unaddressable by the player).
    Soult was reassigned cautious->literal at the July 5, 2026 CR-5 gate (an
    MC-4 personality-coverage assignment pulled forward, `COMMAND_ROBUSTNESS_SPEC.md`
    §6.1). If this regresses, the signature feature's third arm goes dark for
    the player."""
    french = [m for m in world1805.marshals.values() if m.nation == "France"]
    literals = sorted(m.name for m in french if str(m.personality) == "literal")
    assert literals == ["Soult"], (
        f"expected exactly one literal French marshal (Soult), got {literals}"
    )


def test_cr5_signoff_massena_aggressive_is_his_character(world1805):
    """Guardrail (d) sign-off principle (July 5, 2026 CR-5 gate,
    `COMMAND_ROBUSTNESS_SPEC.md` §6.8): personality_type = the marshal's CHARACTER,
    never his scenario situation or a patch for a mechanic. Massena was briefly
    recast aggressive->cautious to defuse the dangerous inferred-attack arm, then
    REVERTED — he was one of Napoleon's most aggressive marshals ('dear child of
    victory'; he attacked Charles at Caldiero in 1805). His 1805 holding role on
    the Adige is his situation, not his temperament. The danger is handled by the
    guardrail-(c) attack-on-arrival fix (§6.3c), not by falsifying his character.
    The commandable aggressive arm is Ney/Lannes/Murat/Massena."""
    french = [m for m in world1805.marshals.values() if m.nation == "France"]
    assert str(world1805.marshals["Massena"].personality) == "aggressive"
    aggressive = sorted(m.name for m in french if str(m.personality) == "aggressive")
    assert aggressive == ["Lannes", "Massena", "Murat", "Ney"], aggressive


def test_marshal_statlines_match_blessed_roster(world1805):
    murat = world1805.marshals["Murat"]
    assert murat.cavalry is True
    assert murat.movement_range == 2
    ney = world1805.marshals["Ney"]
    assert ney.cavalry is False  # the legacy cavalry flag moved to Murat
    assert ney.movement_range == 1
    for name, marshal in world1805.marshals.items():
        assert isinstance(marshal.strength, int), name
        assert str(marshal.personality) in {"aggressive", "cautious", "literal"}, name

    def national_total(nation):
        return sum(m.strength for m in world1805.marshals.values() if m.nation == nation)

    assert national_total("France") == 189_000
    # Austria carries the supply-cap deviations of record: Mack 52k (blessed
    # 52k-62k knob bottom) + Charles 54k (Carniola home cap) — Charles > Mack held.
    assert world1805.marshals["Mack"].strength == 52_000
    assert world1805.marshals["ArchdukeCharles"].strength == 54_000
    assert world1805.marshals["ArchdukeCharles"].strength > world1805.marshals["Mack"].strength
    assert national_total("Austria") == 126_000
    assert national_total("Russia") == 70_000
    assert national_total("Britain") == 30_000
    assert national_total("Bavaria") == 22_000


# ══════════════════════════ diplomatic matrix ══════════════════════════


def test_diplomatic_matrix_states(world1805):
    for pair in WAR_PAIRS:
        assert world1805.diplomatic_states[pair] == "WAR", pair
        assert world1805.war_start_turns[pair] == 1, pair
    for a, b in ALLIANCE_PAIRS:
        assert world1805.get_diplomatic_state(a, b) == "ALLIANCE", (a, b)
    # Unlisted pairs default to PEACE (default-PEACE + exceptions, N3)
    assert world1805.get_diplomatic_state("France", "Prussia") == "PEACE"
    assert world1805.get_diplomatic_state("Denmark", "Sweden") == "PEACE"
    # Coalition-committed but NOT belligerent (gate decisions 1 + 2)
    assert world1805.get_diplomatic_state("France", "Sweden") == "PEACE"
    assert world1805.get_diplomatic_state("France", "Naples") == "PEACE"


def test_diplomatic_matrix_symmetric_and_valid(world1805):
    # Exact pin: 5 authored ALLIANCE + 3 authored satellite VASSAL + 7
    # loader-seeded WAR = 15 entries. A from_dict fallback regression that
    # leaks the legacy constructor matrix would grow this dict.
    expected = {
        "France|Spain": "ALLIANCE",
        "Bavaria|France": "ALLIANCE",
        "Britain|Russia": "ALLIANCE",
        "Austria|Britain": "ALLIANCE",
        "Austria|Russia": "ALLIANCE",
        "France|Holland": "VASSAL",
        "France|KingdomOfItaly": "VASSAL",
        "France|Switzerland": "VASSAL",
    }
    expected.update({pair: "WAR" for pair in WAR_PAIRS})
    assert world1805.diplomatic_states == expected
    for key in world1805.diplomatic_states:
        assert key == "|".join(sorted(key.split("|"))), f"unsorted pair key {key!r}"
    for key in world1805.nation_relations:
        assert key == "|".join(sorted(key.split("|"))), f"unsorted relation key {key!r}"
    # The getter must be symmetric (reads via _make_diplo_key)
    assert (world1805.get_diplomatic_state("France", "Britain")
            == world1805.get_diplomatic_state("Britain", "France") == "WAR")
    assert get_relation(world1805, "France", "Britain") == get_relation(
        world1805, "Britain", "France") == -90


def test_satellite_vassal_states_open_movement(world1805):
    """France must be able to enter its satellites' soil (Masséna's Army of
    Italy stands on KingdomOfItaly-controlled Milan and must be reinforceable).
    'VASSAL' is an OPEN_MOVEMENT state; the Slice-4 seam seeded only
    world.vassals — the diplomatic pair state is stamped by _seed_europe_vassals
    (default boot) and authored in the scenario (from_dict wipes constructor
    states)."""
    from backend.game_logic.diplomacy import can_enter_territory

    for satellite in ("Holland", "KingdomOfItaly", "Switzerland"):
        assert world1805.get_diplomatic_state("France", satellite) == "VASSAL"
        assert can_enter_territory(world1805, "France", satellite) is True
    # The army-less default Europe boot carries the same states (live-game
    # parity with vassal.py's treaty/conquest vassalization stamps).
    default_world = WorldState(sovereign_map="europe")
    for satellite in ("Holland", "KingdomOfItaly", "Switzerland"):
        assert default_world.get_diplomatic_state("France", satellite) == "VASSAL"


def test_france_treasury_keeps_europe_constructor_value(world1805):
    """An omitted-gold Europe scenario must NOT trip the legacy single-gold
    migration default (1200): France keeps the blessed EUROPE_NATION_GOLD 800.
    (Legacy bare dicts keep their pinned 1200 — see
    test_economy_foundations.py::test_backward_compat_no_gold_field.)"""
    assert world1805.nation_gold["France"] == 800
    assert world1805.nation_gold["Britain"] == 2000
    assert world1805.nation_gold["Russia"] == 1500


def test_turn_one_dp_matches_constructor_and_regen_formula(world1805):
    """Audit 2026-07-09 fix 1.1: the scenario omits `diplomatic_points`, so the
    from_dict fallback must read the world's construction-time value (5 —
    matching calculate_dp for France: base 3 + Talleyrand skill 10 + authority
    60, holding Paris), not the stale pre-skill-bonus 4 that gave turn 1 one
    less DP than every regenerated turn after it."""
    from backend.models.world_state import WorldState

    constructor_world = WorldState(player_nation="France", sovereign_map="europe")
    assert world1805.diplomatic_points == constructor_world.diplomatic_points == 5


def test_relations_match_researched_matrix(world1805):
    assert world1805.nation_relations == EXPECTED_RELATIONS


# ══════════════════════════ war + coalition seed ══════════════════════════


def test_one_shared_coalition_war_instance(world1805):
    assert len(world1805.war_instances) == 1
    instance = next(iter(world1805.war_instances.values()))
    assert instance["attacker_leader"] == "France"
    assert instance["defender_leader"] == "Britain"
    assert sorted(instance["attackers"]) == [
        "Bavaria", "France", "Holland", "KingdomOfItaly", "Spain"]
    assert sorted(instance["defenders"]) == ["Austria", "Britain", "Russia"]


def test_third_coalition_seeded(world1805):
    coalition = world1805.active_coalition
    assert coalition is not None
    assert coalition["name"] == "Third Coalition"
    assert coalition["leader"] == "Britain"
    assert coalition["target_nation"] == "France"
    assert coalition["members"] == ["Austria", "Britain", "Russia"]
    assert world1805.threat_level == 85
    assert world1805.coalition_count == 1


def test_british_subsidy_flows_to_austria(world1805):
    """NA-3 §5.7 re-bless (July 17, 2026): the subsidy now keys off the
    paymaster POSTURE — Britain boots at EXACTLY its authored 2,000-gold
    treasury floor (`> floor` is exclusive, the NA-0 pin), so the boot
    turn itself pays nothing; one turn of income across the floor and
    Pitt's gold flows to the lowest-relation partner: Austria (60) vs
    Russia (70)."""
    from backend.models.world_state import WorldState
    assert get_british_subsidy_recipient(world1805) is None

    world = WorldState.from_dict(world1805.to_dict())
    world.nation_gold["Britain"] = 2001
    assert get_british_subsidy_recipient(world) == "Austria"


def test_satellite_vassals_survive_scenario_load(world1805):
    assert set(world1805.vassals.keys()) == {"Holland", "KingdomOfItaly", "Switzerland"}


# ══════════════════════════ supply + turn stability ══════════════════════════


def test_supply_clean_except_mack_invasion_strain():
    """Every authored stack fits its province's derived supply cap EXCEPT Mack,
    whose hostile-soil strain on Bavaria-owned Swabia is deliberate (invasion
    in progress — gate decision 4). If this test grows a second event, an
    authored placement has drifted out of its supply budget."""
    world = _load()
    events = world.process_supply_attrition()
    assert len(events) == 1, [e.get("message") for e in events]
    assert "Swabia" in events[0]["message"]
    assert "Mack" in events[0]["message"]


def test_turn_advances_cleanly_with_mack_on_hostile_swabia():
    """The gate decision 4 smoke: the engine tolerates a hostile army standing
    on another nation's province from turn 1."""
    world = _load()
    for _ in range(3):
        world.advance_turn()
    assert world.current_turn == 4
    assert not world.game_over
    assert len(world.marshals) == 21  # nobody eliminated by scenario data alone
    mack = world.marshals["Mack"]
    assert mack.location == "Swabia"
    assert 0 < mack.strength < 52_000  # invasion strain applied, army intact


def test_enemy_phase_end_turn_runs_clean():
    """The live end-turn pipeline (TurnManager → enemy AI for all 10 armed AI
    nations over 126 provinces, incl. Mack ACTING from hostile Swabia) — the
    path a player's 'end turn' actually runs, not just world.advance_turn()."""
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager

    world = _load()
    executor = CommandExecutor()
    tm = TurnManager(world, executor)
    game_state = {"world": world}
    for _ in range(2):
        result = tm.end_turn(game_state)
        assert result is not None
    assert world.current_turn == 3
    assert not world.game_over


def test_armyless_nations_preseeded_as_notified():
    """Authored army-less nations must not fire 'forces are spent' notices."""
    world = _load()
    assert world.eliminated_nations_notified == ARMYLESS_NATIONS
    # Armed nations stay OUT of the dedupe so a real elimination still notifies.
    assert "Austria" not in world.eliminated_nations_notified
    assert "Prussia" not in world.eliminated_nations_notified


def test_legacy_scenario_keeps_control_and_armyless_guard_noop(tmp_path):
    """The injection fix + army-less guard are world-scoped: a legacy scenario
    omitting `regions` still stamps legacy control (the injection previously
    loaded controller-less worlds there too), and its fully-armed default
    roster leaves the notification dedupe empty."""
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps({"player_nation": "France"}), encoding="utf-8")
    world = WorldState.from_scenario(str(path))
    assert world.sovereign_map == "legacy"
    default_world = WorldState()
    for name, region in default_world.regions.items():
        assert world.regions[name].controller == region.controller, name
        if region.is_capital:
            assert world.regions[name].garrison_strength == 15000, name
    assert world.eliminated_nations_notified == set()


def test_authored_partial_legacy_scenario_preseeds_armyless(tmp_path):
    """The guard is deliberately scenario-global: a legacy scenario that
    AUTHORS a partial roster treats its army-less nations as deliberate too
    (previously they'd announce 'forces are spent' on the first enemy phase)."""
    path = tmp_path / "partial_legacy.json"
    path.write_text(json.dumps({
        "player_nation": "France",
        "marshals": {
            "Ney": {"name": "Ney", "location": "Paris", "strength": 20000,
                    "personality": "aggressive", "nation": "France"},
        },
    }), encoding="utf-8")
    world = WorldState.from_scenario(str(path))
    assert world.eliminated_nations_notified == set(world.enemy_nations)


# ══════════════════════════ the carried Slice-5 fold test ══════════════════════════


def test_treaty_cession_restores_1805_owner_fires_allied_region_restored():
    """Carried from the Slice 5 fold (gate Tests line): a Europe treaty cession
    that returns a province to its 1805 starting owner must credit the
    ``allied_region_restored`` contribution event resolved against the EUROPE
    starting map. 'Brabant' exists only on the 126-province map — under the old
    legacy ``get_starting_controllers()`` lookup the starting owner would miss
    and no restoration credit could ever fire."""
    assert "Brabant" not in get_starting_controllers()  # the discriminator

    world = _load()
    war_id = next(iter(world.war_instances.keys()))
    # Holland (French satellite, attacker-side in the shared coalition war) has
    # lost Brabant to Britain in play...
    world.regions["Brabant"].controller = "Britain"
    # The authored 1805 opening seeds Britain|France at -90, below the PEACE
    # ratification gate (STATE_RELATION_REQUIREMENTS >= -60) — the war has
    # thawed by the time this peace is signed.
    world.nation_relations["Britain|France"] = -40
    # ...and France's peace treaty with Britain hands it back to Holland.
    proposal = {
        "proposer_nation": "France",
        "target_nation": "Britain",
        "type": "peace",
        "demands": [{
            "type": "territory_cede",
            "regions": ["Brabant"],
            "from_nation": "Britain",
            "to_nation": "Holland",
        }],
    }
    world._ratify_treaty(proposal)

    assert world.regions["Brabant"].controller == "Holland"
    holland_episode = current_episode(world, war_id, "Holland")
    assert holland_episode is not None
    # THE regression discriminator is the == 15 line (verified: under the
    # legacy-global fallback the episode still EXISTS with occupation == 0 —
    # the `is not None` check alone would pass).
    assert holland_episode["occupation"] == 15  # allied_region_restored, not 20


# ══════════════════════════ boot wiring + registry deviation pins ══════════════════════════


def test_scenario_boots_via_sovereign_scenario_env(monkeypatch):
    import backend.main as main_module

    monkeypatch.setenv("SOVEREIGN_SCENARIO", str(SCENARIO_PATH))
    try:
        world = main_module._reset_world_state()
        assert world.sovereign_map == "europe"
        assert len(world.regions) == 126
        assert len(world.marshals) == 21
        assert world.active_coalition is not None
        assert main_module.world is world
    finally:
        monkeypatch.delenv("SOVEREIGN_SCENARIO", raising=False)
        main_module._reset_world_state()


def test_milan_terrain_corrected_to_plains(world1805):
    """Deviation of record (July 1, 2026): Milan sits in the Po plain; the
    image-derived `mountains` flag halved its supply to 25k and bled the Army
    of Italy -428/turn on the player's own dispatch. Owned with DEF-8's
    image-derived field review."""
    assert world1805.regions["Milan"].terrain == "plains"
    assert world1805.regions["Milan"].supply_capacity == 50_000
    assert world1805.marshals["Massena"].strength <= world1805.regions["Milan"].supply_capacity


# ══════════════════════════ scenario-boot fog (Slice 8 fix) ══════════════════════════


def test_scenario_boot_computes_visibility(world1805):
    """Slice 8 fix (user-reported): from_scenario never ran calculate_visibility,
    so EVERY province — including French home soil — booted "unknown" ("No
    intelligence" tooltips over France, the whole map fog-washed at turn 1).
    Scenario boots must mirror the constructor (:807) and save-load
    (save_manager.py) paths: own territory PARTIAL+, marshal locations FULL,
    distant enemy interior still unknown (fog intact)."""
    from backend.models.intel import FULL, PARTIAL, UNKNOWN

    for name, region in world1805.regions.items():
        if region.controller == "France":
            assert world1805.get_region_intel(name).visibility in (FULL, PARTIAL), (
                f"French province {name} booted {world1805.get_region_intel(name).visibility}"
            )
    for marshal in world1805.marshals.values():
        if marshal.nation == "France":
            assert world1805.get_region_intel(marshal.location).visibility == FULL, (
                f"French marshal location {marshal.location} not FULL"
            )
    # Fog still stands: the remote Russian interior is out of French sight.
    assert world1805.get_region_intel("Estonia").visibility == UNKNOWN


def test_legacy_scenario_boot_computes_visibility(tmp_path):
    """The fix is path-scoped, not map-scoped: legacy scenarios boot with
    computed fog too (own regions PARTIAL+; from_dict alone stays intel-empty
    per the fog backward-compat pin in test_fog_of_war.py)."""
    from backend.models.intel import FULL, PARTIAL

    path = tmp_path / "legacy_fog.json"
    path.write_text(json.dumps({"player_nation": "France"}), encoding="utf-8")
    world = WorldState.from_scenario(str(path))
    own = [n for n, r in world.regions.items() if r.controller == "France"]
    assert own, "legacy scenario should stamp French control"
    for name in own:
        assert world.get_region_intel(name).visibility in (FULL, PARTIAL), name
