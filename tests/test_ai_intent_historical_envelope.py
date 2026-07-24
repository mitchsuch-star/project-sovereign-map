"""AI-0c / AI-0d — the historical envelope (docs/AI_INTENT_SPEC.md §3.8.1).

The six-clause historian test, run across an N-seed sweep: every seed must
be a 1805 a historian would recognise. Tier-1 values are identical on every
seed; Tier-2 values sit inside their authored bands; a value with no
authored band never varies (§5 pin 14b). Pin 22: deck depth never moves the
boot — Russia's second design (gulf_and_straits, AI-0d) is inactive at boot
on every seed.

All worlds here are built through `WorldState.from_scenario(path, seed=...)`
directly (the 75-caller idiom) and are READ-ONLY — module-scoped fixtures.
"""

import json
from pathlib import Path

import pytest

from backend.game_logic.agendas import get_active_agenda
from backend.models.world_state import WorldState
from backend.nation_config import EUROPE_ROSTER

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

# The sweep: the historical seed plus six variance seeds. "ulm" is pinned
# below as a seed that reorders Austria's deck (Germany-first — Mack's
# actual deployment), so the order band is demonstrably live.
SWEEP_SEEDS = ("historical", "crimson-1805", "ulm", "austerlitz",
               "jena-06", "wagram", "tilsit")
VARIANCE_SEEDS = tuple(s for s in SWEEP_SEEDS if s != "historical")

# The two French satellites carry dormant decks (vassalized at boot) —
# excluded from historian clause 3, per the pinned satellite-dormancy
# contract (test_nation_agendas.py::TestSatelliteDormancy).
BOOT_VASSAL_DECK_HOLDERS = {"KingdomOfItaly", "Holland"}


@pytest.fixture(scope="module")
def worlds():
    """seed -> read-only 1805 world. Mutating tests do not belong here."""
    return {seed: WorldState.from_scenario(str(SCENARIO_PATH), seed=seed)
            for seed in SWEEP_SEEDS}


@pytest.fixture(scope="module")
def historical(worlds):
    return worlds["historical"]


@pytest.fixture(scope="module")
def authored():
    """The raw authored scenario file — the band map the sweep checks
    against comes from here, not from constants duplicated in the test."""
    with open(SCENARIO_PATH, encoding="utf-8") as f:
        return json.load(f)


def _banded_pairs(authored):
    """{pair: (lo, hi)} for every band-carrying relation entry."""
    bands = {}
    for pair, entry in authored["nation_relations"].items():
        if isinstance(entry, dict):
            lo, hi = entry["band"]
            bands[pair] = (int(lo), int(hi))
    return bands


# ════════════════════════════════════════════════════════════════════════
# The historian test — six clauses, every seed (§3.8.1)
# ════════════════════════════════════════════════════════════════════════

class TestHistorianClauses:
    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_1_third_coalition_exists(self, worlds, seed):
        world = worlds[seed]
        coalition = world.active_coalition
        assert coalition, f"seed {seed}: no active coalition at boot"
        assert coalition.get("target_nation") == "France"
        assert coalition.get("name") == "Third Coalition"
        for enemy in ("Austria", "Britain", "Russia"):
            assert world.get_diplomatic_state("France", enemy) == "WAR", \
                f"seed {seed}: France not at war with {enemy}"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_2_france_at_peace_with_prussia(self, worlds, seed):
        world = worlds[seed]
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE", \
            f"seed {seed}: Prussia's entry must be a thing that HAPPENS, " \
            f"never a boot state"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_3_deck_holders_have_boot_designs(self, worlds, seed):
        world = worlds[seed]
        for nation, deck in world.agendas.items():
            if nation in BOOT_VASSAL_DECK_HOLDERS:
                assert get_active_agenda(nation, world) is None, \
                    f"seed {seed}: {nation} is vassalized — deck dormant"
                continue
            view = get_active_agenda(nation, world)
            assert view is not None, \
                f"seed {seed}: {nation} holds a deck but no active design"
            assert not view.survival, \
                f"seed {seed}: {nation} boots in survival"
            assert view.id in {e["id"] for e in deck}, \
                f"seed {seed}: {nation} active design not from its deck"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_4_nobody_eliminated_map_identical(self, worlds,
                                                      historical, seed):
        world = worlds[seed]
        # Province ownership is Tier 1 — the seed never touches the map.
        ownership = {name: region.controller
                     for name, region in world.regions.items()}
        baseline = {name: region.controller
                    for name, region in historical.regions.items()}
        assert ownership == baseline, \
            f"seed {seed}: province ownership differs from historical"
        # The live elimination check (not a tautology — NA-6c shipped carve
        # logic that mis-announced eliminations): every roster nation is
        # active at boot.
        active = set(world.get_active_nations())
        for nation in EUROPE_ROSTER:
            assert nation in active, \
                f"seed {seed}: {nation} boots eliminated"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_5_war_set_and_alliance_map_authored(self, worlds,
                                                        historical, seed):
        world = worlds[seed]
        assert world.diplomatic_states == historical.diplomatic_states, \
            f"seed {seed}: the seed may not add, remove or re-point a " \
            f"war or an alliance"
        assert (sorted(world.war_instances.keys())
                == sorted(historical.war_instances.keys()))

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_clause_6_the_1805_alignment(self, worlds, seed):
        world = worlds[seed]
        assert world.get_diplomatic_state("Bavaria", "Austria") == "WAR"
        assert world.get_diplomatic_state("KingdomOfItaly",
                                          "Austria") == "WAR"
        assert world.get_diplomatic_state("Spain", "Britain") == "WAR"
        assert world.get_diplomatic_state("Holland", "Britain") == "WAR"
        for other in EUROPE_ROSTER:
            if other == "Prussia":
                continue
            assert world.get_diplomatic_state("Prussia", other) != "WAR", \
                f"seed {seed}: Prussia boots at war with {other}"


# ════════════════════════════════════════════════════════════════════════
# Tier 1 — the identity of the scenario, fixed on every seed
# ════════════════════════════════════════════════════════════════════════

class TestTierOneFixed:
    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_marshals_identical(self, worlds, historical, seed):
        world = worlds[seed]
        assert set(world.marshals) == set(historical.marshals)
        for name, marshal in world.marshals.items():
            base = historical.marshals[name]
            assert marshal.nation == base.nation
            assert marshal.strength == base.strength
            assert marshal.personality == base.personality
            assert marshal.skills == base.skills
            assert marshal.location == base.location

    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_treasury_manpower_identical(self, worlds, historical, seed):
        world = worlds[seed]
        assert world.nation_gold == historical.nation_gold
        assert world.manpower_pools == historical.manpower_pools

    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_deck_content_identical(self, worlds, historical, seed):
        # Deck CONTENT is Tier 1 (the designs ARE the history); only ORDER
        # inside an authored order_group may vary.
        world = worlds[seed]
        assert set(world.agendas) == set(historical.agendas)
        for nation in world.agendas:
            ours = {json.dumps(e, sort_keys=True)
                    for e in world.agendas[nation]}
            base = {json.dumps(e, sort_keys=True)
                    for e in historical.agendas[nation]}
            assert ours == base, \
                f"seed {seed}: {nation} deck content differs"

    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_capitals_and_player_identical(self, worlds, historical, seed):
        world = worlds[seed]
        assert world.player_nation == historical.player_nation
        for nation in EUROPE_ROSTER:
            assert (world.get_nation_capital(nation)
                    == historical.get_nation_capital(nation))


# ════════════════════════════════════════════════════════════════════════
# Tier 2 — banded dispositions; no band, no variance (§5 pin 14b)
# ════════════════════════════════════════════════════════════════════════

class TestTierTwoBanded:
    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_banded_pairs_inside_their_bands(self, worlds, authored, seed):
        world = worlds[seed]
        for pair, (lo, hi) in _banded_pairs(authored).items():
            value = world.nation_relations[pair]
            assert lo <= value <= hi, \
                f"seed {seed}: {pair}={value} outside band [{lo}, {hi}]"

    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_unbanded_values_never_vary(self, worlds, historical,
                                        authored, seed):
        world = worlds[seed]
        banded = set(_banded_pairs(authored))
        for pair, value in historical.nation_relations.items():
            if pair in banded:
                continue
            assert world.nation_relations[pair] == value, \
                f"seed {seed}: unbanded pair {pair} varied"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_threat_level_inside_band(self, worlds, authored, seed):
        lo, hi = authored["threat_level_band"]
        world = worlds[seed]
        assert lo <= world.threat_level <= hi
        if seed == "historical":
            assert world.threat_level == authored["threat_level"]

    @pytest.mark.parametrize("seed", VARIANCE_SEEDS)
    def test_deck_order_varies_only_where_banded(self, worlds, historical,
                                                 seed):
        world = worlds[seed]
        for nation in world.agendas:
            ours = [e["id"] for e in world.agendas[nation]]
            base = [e["id"] for e in historical.agendas[nation]]
            if nation == "Austria":
                assert sorted(ours) == sorted(base)
            else:
                assert ours == base, \
                    f"seed {seed}: {nation} deck order varied with no band"

    def test_variance_is_real_across_the_sweep(self, worlds):
        # The envelope must actually produce different 1805s — the whole
        # point of D7. Deterministic hash, so these are stable pins.
        prussia = {worlds[s].nation_relations["France|Prussia"]
                   for s in SWEEP_SEEDS}
        assert len(prussia) >= 3, \
            f"France|Prussia took too few values across the sweep: {prussia}"
        austria_orders = {tuple(e["id"] for e in worlds[s].agendas["Austria"])
                          for s in SWEEP_SEEDS}
        assert len(austria_orders) == 2, \
            "the Austria order band never fired across the sweep"
        # Review fix [13]: the threat band was the one family with only a
        # vacuous inside-the-band check (85 sits inside [80, 90], so a
        # dead resolver passed) — the sweep must produce distinct values.
        threat = {worlds[s].threat_level for s in SWEEP_SEEDS}
        assert len(threat) >= 3, \
            f"the threat band never fired across the sweep: {threat}"

    def test_ulm_opens_germany_first(self, worlds):
        # The pinned live-order-band seed: Mack's actual deployment.
        assert [e["id"] for e in worlds["ulm"].agendas["Austria"]] == \
            ["primacy_germany", "redeem_italy"]
        assert get_active_agenda("Austria", worlds["ulm"]).id == \
            "primacy_germany"

    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_seed_is_shown_on_the_world(self, worlds, seed):
        assert worlds[seed].campaign_seed == seed


# ════════════════════════════════════════════════════════════════════════
# Pin 22 — deck depth never moves the boot (AI-0d)
# ════════════════════════════════════════════════════════════════════════

class TestPin22SecondDesign:
    @pytest.mark.parametrize("seed", SWEEP_SEEDS)
    def test_gulf_and_straits_inactive_at_boot_on_every_seed(self, worlds,
                                                             seed):
        world = worlds[seed]
        deck_ids = [e["id"] for e in world.agendas["Russia"]]
        assert deck_ids == ["arbiter_of_europe", "gulf_and_straits"], \
            f"seed {seed}: Russia's deck carries no order band (pin 22)"
        view = get_active_agenda("Russia", world)
        assert view is not None and view.id == "arbiter_of_europe", \
            f"seed {seed}: Russia's boot design moved"

    def test_historical_boot_actives_unchanged(self, historical):
        # Pin 22's second arm: no nation's turn-0 active design differs
        # from today's on the historical seed (the NA-0 boot pins, held
        # here beside the deck-depth change that could have moved them).
        for nation, agenda_id in [
            ("Austria", "redeem_italy"),
            ("Prussia", "hanoverian_prize"),
            ("Britain", "low_countries"),
            ("Russia", "arbiter_of_europe"),
            ("Sweden", "scourge_of_the_usurper"),
            ("Ottoman", "guard_the_straits"),
            ("Sardinia", "house_of_savoy_restored"),
            ("Denmark", "neutrality_of_the_north"),
        ]:
            view = get_active_agenda(nation, historical)
            assert view is not None and view.id == agenda_id

    def test_second_design_targets_exist_with_1805_holders(self, historical):
        # §12.2: Finland boots Swedish, Rumelia boots Ottoman — the scene-4
        # aim has real objects, and both are non-capital provinces (the
        # wars it generates end in settlements, not eliminations — D2).
        assert historical.regions["Finland"].controller == "Sweden"
        assert historical.regions["Rumelia"].controller == "Ottoman"
        assert historical.get_nation_capital("Sweden") != "Finland"
        assert historical.get_nation_capital("Ottoman") != "Rumelia"
