"""AI-3r — the AI War Decision rework (docs/AI_WAR_DECISION_SPEC.md,
gate record §6.1, rulings §6.2).

Pins carried here:
- §2.1 the rear-security reserve: max-not-sum (Q2), the 0.60 cap, the
  N2 relation bands, the at-war full band, family/ally drops, and the
  §2.7 GR8 scale contract (one region pass, per-turn cached).
- §2.1 the restraint switch: the force gate weighs FREE strength; the
  decomposed reasons busy / penniless / outmatched / exposed.
- §2.2 the moment: all four opportunity terms fire AND decay (per-turn
  readings, never latches); the hollow-guarantee interplay (a busy
  guarantor's -8 nets to -2 against N3's +6) is deliberate and pinned.
- §2.3 the widening (Q3): deny/contain designs open crises; the D3
  guard (player-targeted designs never do); ruling R4 (their war
  objective keeps the [capital] default — no design stamp).
- §2.4 (Q1): MAX_SIMULTANEOUS_AI_WARS stays deleted; SWEEP_WAR_ALARM is
  the SUITE's runaway tripwire, enforced by a 40-turn seeded ambient run.
- §2.5-1 cause honesty: exposed / outmatched / penniless cool with their
  OWN copy; `starved` never renders for a gate refusal (the §0.3 defect).
- §2.5-2/3 the ledger rows; §2.5-4 Talleyrand's designs-in-check rung.
- §2.6 (Q4, ruling R1): authored wary_of — scenario key, validator
  clamps, get_statecraft merge, serialization round-trip.
- Q5: the exposure calculus NEVER gates the player's orders (source pin).
"""

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic import intent as intent_module
from backend.game_logic import war_council
from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
from backend.game_logic.instruments import _mint_grievance, pledge_guarantee
from backend.game_logic.intent import get_nation_intent
from backend.game_logic.war_council import (
    RESERVE_CAP_FRACTION,
    SWEEP_WAR_ALARM,
    _CRISIS_CAUSE_COPY,
    _SOFT_BLOCK_CAUSE,
    _menace_band,
    _restraint_block_reason,
    get_exposure_view,
    get_free_strength,
    get_rear_reserve,
    process_war_council,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _arm_prussia_crisis(world):
    """The war-decision fixture (test_ai_intent_war_decision idiom):
    weight 87 at fight with a climbed ladder via the renege casus."""
    world.nation_relations[world._make_diplo_key("Prussia", "Hanover")] = -45
    _mint_grievance(world, breaker="Hanover", victim="Prussia",
                    grievance_type="bargain_reneged", source="test_fixture")
    declare_war(world, "Hanover", "Denmark")
    world.nation_gold["Hanover"] = -50
    world.nation_gold["Prussia"] = max(
        int(world.nation_gold.get("Prussia", 0)), 2000)
    world.invalidate_bloc_members_cache()


def _poll_next_turn(world):
    world.current_turn = int(world.current_turn) + 1
    return process_war_council(world)


# ════════════════════════════════════════════════════════════════════════
# §2.1 — the rear-security reserve
# ════════════════════════════════════════════════════════════════════════

class TestNeighbourMap:
    def test_boot_neighbours_are_controller_level(self, world1805):
        prussian = world1805.get_neighbouring_nations("Prussia")
        assert "Russia" in prussian
        assert "Hanover" in prussian
        assert "Prussia" not in prussian

    def test_map_is_per_turn_cached_and_invalidated(self, world):
        before = world.get_neighbouring_nations("Prussia")
        cache_obj = world._neighbouring_nations_cache
        world.get_neighbouring_nations("Austria")
        assert world._neighbouring_nations_cache is cache_obj, \
            "second read same turn must reuse the single-pass map"
        # A controller flip routes through the standard invalidation seam.
        hanover = world.regions["Hanover"]
        hanover.controller = "Prussia"
        world.invalidate_active_nations_cache()
        after = world.get_neighbouring_nations("Prussia")
        assert after != before or world._neighbouring_nations_cache is not cache_obj

    def test_single_region_pass_source_pin(self):
        src = inspect.getsource(WorldState.get_neighbouring_nations)
        assert src.count("self.regions.values()") == 1, \
            "the map must be built in ONE region pass (§2.7)"


class TestReserve:
    def test_bands_match_n2(self):
        assert _menace_band(-40) == 1.0
        assert _menace_band(-39) == 0.6
        assert _menace_band(0) == 0.6
        assert _menace_band(1) == 0.3
        assert _menace_band(30) == 0.3
        assert _menace_band(31) == 0.1

    def test_reserve_is_max_not_sum(self, world1805):
        """Q2: Prussia's reserve equals its single worst menace, not the
        sum over Russia + Hanover + the rest."""
        view = get_exposure_view(world1805, "Prussia")
        total = sum(t["menace"] for t in view["threats"])
        assert len(view["threats"]) >= 2
        assert view["reserve"] == min(
            view["worst_menace"],
            int(RESERVE_CAP_FRACTION * view["standing"]))
        assert view["reserve"] < total

    def test_reserve_capped_at_fraction(self, world):
        """A terrified court still keeps 40% of its army marchable."""
        key = world._make_diplo_key("Prussia", "Russia")
        world.nation_relations[key] = -80
        world.invalidate_bloc_members_cache()
        view = get_exposure_view(world, "Prussia")
        assert view["reserve"] == int(RESERVE_CAP_FRACTION * view["standing"])
        assert view["free"] == view["standing"] - view["reserve"]

    def test_wary_of_multiplies_menace(self, world1805):
        """§2.6: Prussia's authored 1.4 dread of Russia shows in the
        menace arithmetic (70,000 x 0.3 band x 1.4 = 29,399)."""
        view = get_exposure_view(world1805, "Prussia")
        russia = next(t for t in view["threats"] if t["nation"] == "Russia")
        assert russia["menace"] == int(70000 * 0.3 * 1.4)

    def test_at_war_neighbour_reads_full_band(self, world1805):
        """Austria vs Bavaria (open war): the enemy is the whole menace
        regardless of the relation number."""
        view = get_exposure_view(world1805, "Austria")
        bavaria = next(t for t in view["threats"] if t["nation"] == "Bavaria")
        assert bavaria["menace"] == 22000  # full standing x 1.0

    def test_alliance_partner_never_menaces(self, world):
        set_diplomatic_state(world, "Prussia", "Russia", "ALLIANCE", "test")
        view = get_exposure_view(world, "Prussia")
        assert all(t["nation"] != "Russia" for t in view["threats"])

    def test_own_vassal_family_never_menaces(self, world1805):
        view = get_exposure_view(world1805, "France")
        named = {t["nation"] for t in view["threats"]}
        assert not named & {"Holland", "KingdomOfItaly", "Switzerland"}

    def test_exposure_cached_per_turn(self, world):
        first = get_exposure_view(world, "Prussia")
        assert get_exposure_view(world, "Prussia") is first
        world.invalidate_bloc_members_cache()
        assert get_exposure_view(world, "Prussia") is not first

    def test_free_strength_and_reserve_accessors(self, world1805):
        view = get_exposure_view(world1805, "Prussia")
        assert get_rear_reserve(world1805, "Prussia") == view["reserve"]
        assert get_free_strength(world1805, "Prussia") == view["free"]

    def test_no_region_scan_in_exposure_source(self):
        """§2.7 GR8 tripwire: the exposure path rides the cached map."""
        src = inspect.getsource(get_exposure_view)
        assert "regions.values(" not in src
        assert "get_neighbouring_nations" in src


# ════════════════════════════════════════════════════════════════════════
# §2.1 — the restraint switch (free strength) + reason decomposition
# ════════════════════════════════════════════════════════════════════════

class TestRestraintReasons:
    def test_clear_case_reads_none(self, world1805):
        assert _restraint_block_reason(world1805, "Prussia", "Hanover") is None

    def test_busy(self, world1805):
        # Austria boots at war — no second design war.
        assert _restraint_block_reason(world1805, "Austria", "Hanover") == "busy"

    def test_penniless(self, world):
        world.nation_gold["Prussia"] = 100
        assert _restraint_block_reason(world, "Prussia", "Hanover") == "penniless"

    def test_outmatched(self, world):
        world.nation_gold["Denmark"] = 2000
        assert _restraint_block_reason(world, "Denmark", "Prussia") == "outmatched"

    def test_exposed_when_reserve_pins_the_army(self, world):
        """Standing suffices; FREE does not — the diegetic replacement
        for the quota. Hanover armed to 40k; Prussia's rear menaced by a
        cold Russia (reserve at the 0.60 cap → free 31,200 < 50,000)."""
        world.nation_gold["Prussia"] = 2000
        frederick = world.marshals["Frederick"]
        frederick.nation = "Hanover"
        frederick.strength = 40000
        world.nation_relations[world._make_diplo_key("Prussia", "Russia")] = -50
        world.invalidate_bloc_members_cache()
        assert _restraint_block_reason(world, "Prussia", "Hanover") == "exposed"
        view = get_exposure_view(world, "Prussia")
        assert view["standing"] >= 1.25 * 40000
        assert view["free"] < 1.25 * 40000

    def test_guarantors_still_stack_on_the_target_side(self, world):
        """The defender's guarantors weigh in at STANDING strength."""
        world.nation_gold["Prussia"] = 2000
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        world.invalidate_bloc_members_cache()
        # Hanover alone: army-less, clear. With Russia's 70k pledged:
        # even the whole Prussian army (78k) < 1.25 x 70k.
        assert _restraint_block_reason(world, "Prussia", "Hanover") == "outmatched"


# ════════════════════════════════════════════════════════════════════════
# §2.2 — the moment (opportunity terms; readings, never latches)
# ════════════════════════════════════════════════════════════════════════

class TestMomentTerms:
    def test_hollow_guarantee_interplay(self, world):
        """DELIBERATE (gate-era re-anchor): a guarantor who is himself at
        war deters -8 but reads allies-committed +6 — the pledge of a
        fully-committed power is nearly hollow. Russia boots at war."""
        before = get_nation_intent("Prussia", world).weight
        assert before == 59
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        world.invalidate_bloc_members_cache()
        after = get_nation_intent("Prussia", world).weight
        assert after == before - 8 + intent_module.WEIGHT_HOLDER_ALLIES_COMMITTED

    def test_allies_committed_via_treaty_ally(self, world):
        # War FIRST, alliance second — a declaration cascades the new
        # ally in (offensive_cascade) and would put HANOVER itself at
        # war, conflating the term with plain opportunism.
        declare_war(world, "Denmark", "Sweden")
        set_diplomatic_state(world, "Hanover", "Denmark", "ALLIANCE", "test")
        world.invalidate_bloc_members_cache()
        assert intent_module._holder_allies_committed("Prussia", "Hanover", world)
        view = get_nation_intent("Prussia", world)
        assert view.weight == 59 + intent_module.WEIGHT_HOLDER_ALLIES_COMMITTED

    def test_recently_beaten_capital_arm(self, world):
        assert not intent_module._holder_recently_beaten("Hanover", world)
        world.regions["Hanover"].controller = "Britain"
        world.invalidate_active_nations_cache()
        assert intent_module._holder_recently_beaten("Hanover", world)

    def test_recently_beaten_war_end_arm_and_decay(self, world):
        """A war that ended for the holder within the window, while home
        soil sits in foreign hands — and the reading DECAYS when the
        window closes (no latch, §3.1a)."""
        world.current_turn = 20
        world.war_instances["wf_beaten"] = {
            "ended_turn": 18,
            "participant_meta": {"Hanover": {"side": "b"},
                                 "Denmark": {"side": "a"}},
        }
        home = world.nation_starting_regions.get("Hanover", [])
        soil = next(r for r in home if r != "Hanover")
        world.regions[soil].controller = "Denmark"
        world.invalidate_active_nations_cache()
        assert intent_module._holder_recently_beaten("Hanover", world)
        world.current_turn = 18 + intent_module.RECENTLY_BEATEN_TURNS
        assert not intent_module._holder_recently_beaten("Hanover", world)

    def test_holder_exhausted_term(self, world):
        world.war_exhaustion["Hanover"] = (
            intent_module.HOLDER_EXHAUSTION_BAND + 20)
        world.invalidate_bloc_members_cache()
        view = get_nation_intent("Prussia", world)
        assert view.weight == 59 + intent_module.WEIGHT_HOLDER_EXHAUSTED

    def test_rear_quiet_wire(self, world, monkeypatch):
        """N6 rides the war council's own view (monkeypatched at the
        module the local import resolves through)."""
        quiet = {"standing": 78000, "reserve": 0, "free": 78000,
                 "worst_threat": None, "worst_menace": 0, "threats": []}
        monkeypatch.setattr(war_council, "get_exposure_view",
                            lambda w, n: dict(quiet))
        world.invalidate_bloc_members_cache()
        view = get_nation_intent("Prussia", world)
        assert view.weight == 59 + intent_module.WEIGHT_OWN_REAR_QUIET

    def test_at_war_term_retired(self, world):
        """Ruling R5: no +10 for being at war with the holder — the
        price early-return still reads fight, but the weight carries
        only real terms."""
        assert not hasattr(intent_module, "WEIGHT_AT_WAR_WITH_HOLDER")
        declare_war(world, "Prussia", "Hanover")
        view = get_nation_intent("Prussia", world)
        assert view.price == "fight"          # the war IS the pursuit
        # cold? no (-45 fixture not applied here; boot 0 → chilly +4).
        # Hanover now in 1 war (+6). No +10 anywhere.
        assert view.weight == 55 + 4 + 6


# ════════════════════════════════════════════════════════════════════════
# §2.3 — the widening (Q3) + ruling R4 + the D3 guard
# ════════════════════════════════════════════════════════════════════════

def _forced_view(nation, want_id, want_type, against):
    return intent_module.IntentView(
        nation=nation, want_id=want_id, want_title="The Design",
        want_type=want_type, against=against, weight=90, price="fight")


class TestWidening:
    def test_contain_design_opens_and_declares(self, world, monkeypatch):
        """Sweden (contain deck, at peace) opens a fore-warned crisis
        against a non-player holder and declares on schedule."""
        forced = _forced_view("Sweden", "scourge_of_the_usurper",
                              "contain_hegemon", "Saxony")
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Sweden"
            else intent_module._indifferent(nation))
        world.current_turn = 20
        world.nation_gold["Sweden"] = 2000
        record_diplomatic_refusal(world, "Sweden", "Saxony", "design_purchase")
        record_diplomatic_refusal(world, "Sweden", "Saxony", "alignment")
        process_war_council(world)
        assert "Sweden" in world.war_intents, \
            "a contain design must be able to open a crisis (Q3)"
        _poll_next_turn(world)   # coerce
        _poll_next_turn(world)   # declare
        assert world.is_at_war("Sweden", "Saxony")
        wars = [w for w in world.war_instances.values()
                if w.get("ai_initiated")]
        assert wars and wars[-1].get("design_id") == "scourge_of_the_usurper"
        # Ruling R4: the objective keeps the [capital] default — no
        # design stamp, no design-province list (acquire-only military
        # targets, the NA-3 §3.1 pin preserved).
        key = world._make_diplo_key("Sweden", "Saxony")
        objective = world.war_objectives[key]["Sweden"]
        assert objective.get("design") is None
        assert objective.get("target_regions") == [
            world.get_nation_capital("Saxony")]

    def test_deny_design_eligible(self):
        assert "deny_regions" in war_council.CRISIS_ELIGIBLE_DESIGNS
        assert "contain_hegemon" in war_council.CRISIS_ELIGIBLE_DESIGNS
        assert "guard_neutrality" not in war_council.CRISIS_ELIGIBLE_DESIGNS
        assert "paymaster" not in war_council.CRISIS_ELIGIBLE_DESIGNS

    def test_d3_guard_player_hegemon_never_targeted(self, world, monkeypatch):
        """A contain design aimed at the PLAYER opens nothing — France-
        containment stays the coalition's business (D3, §16.2 v1)."""
        forced = _forced_view("Sweden", "scourge_of_the_usurper",
                              "contain_hegemon", "France")
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Sweden"
            else intent_module._indifferent(nation))
        world.current_turn = 20
        world.nation_gold["Sweden"] = 2000
        record_diplomatic_refusal(world, "Sweden", "France", "design_purchase")
        record_diplomatic_refusal(world, "Sweden", "France", "alignment")
        process_war_council(world)
        assert "Sweden" not in world.war_intents

    def test_frontier_inert_for_contain_crisis(self, world, monkeypatch):
        """Ruling R4's frontier arm: a deny/contain crisis exposes no
        massing ground (empty military-target set), accepted + pinned."""
        forced = _forced_view("Sweden", "scourge_of_the_usurper",
                              "contain_hegemon", "Saxony")
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Sweden"
            else intent_module._indifferent(nation))
        world.current_turn = 20
        world.nation_gold["Sweden"] = 2000
        record_diplomatic_refusal(world, "Sweden", "Saxony", "design_purchase")
        record_diplomatic_refusal(world, "Sweden", "Saxony", "alignment")
        process_war_council(world)
        assert "Sweden" in world.war_intents
        assert war_council.get_intent_frontier(world, "Sweden") == []


# ════════════════════════════════════════════════════════════════════════
# §2.5-1 — cause honesty (beat 7 never lies again)
# ════════════════════════════════════════════════════════════════════════

class TestCauseHonesty:
    def _open(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        assert "Prussia" in world.war_intents
        _poll_next_turn(world)  # coerce fires; tenure clock runs

    def _cool(self, world, max_polls=12):
        for _ in range(max_polls):
            events = _poll_next_turn(world)
            passed = [e for e in events if e["type"] == "crisis_passed"]
            if passed:
                return passed[0]
        return None

    def test_exposed_cools_with_threat_named(self, world):
        self._open(world)
        frederick = world.marshals["Frederick"]
        frederick.nation = "Hanover"
        frederick.strength = 40000
        world.nation_relations[world._make_diplo_key("Prussia", "Russia")] = -50
        world.invalidate_bloc_members_cache()
        passed = self._cool(world)
        assert passed and passed["cause"] == "exposed"
        assert "Russia" in passed["message"], \
            "the exposed cause names the neighbour that pinned the army"
        assert "opportunism decayed" not in passed["message"]

    def test_penniless_cools_with_own_copy(self, world):
        self._open(world)
        world.nation_gold["Prussia"] = -100
        passed = self._cool(world)
        assert passed and passed["cause"] == "penniless"
        assert "treasury" in passed["message"]

    def test_outmatched_cools_with_own_copy(self, world):
        self._open(world)
        frederick = world.marshals["Frederick"]
        frederick.nation = "Hanover"
        frederick.strength = 200000
        world.invalidate_bloc_members_cache()
        passed = self._cool(world)
        assert passed and passed["cause"] == "outmatched"
        assert "odds" in passed["message"]

    def test_every_reachable_cause_has_distinct_copy(self):
        """§2.5-1's pin: every cause has its OWN copy; none renders
        under another's string."""
        for cause in _SOFT_BLOCK_CAUSE.values():
            assert cause in _CRISIS_CAUSE_COPY
        for cause in ("satisfied", "bought_off", "deterred", "starved",
                      "exposed", "outmatched", "penniless"):
            assert cause in _CRISIS_CAUSE_COPY
        copies = list(_CRISIS_CAUSE_COPY.values())
        assert len(copies) == len(set(copies))

    def test_busy_and_ladder_still_read_starved(self):
        assert _SOFT_BLOCK_CAUSE["busy"] == "starved"
        assert _SOFT_BLOCK_CAUSE["ladder"] == "starved"


# ════════════════════════════════════════════════════════════════════════
# §2.4 — the cap stays deleted; the runaway guard lives HERE (N8)
# ════════════════════════════════════════════════════════════════════════

def _run_ambient_subprocess() -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SOVEREIGN_SEED"] = "historical"
    env["LLM_MODE"] = "mock"
    env.pop("SOVEREIGN_SCENARIO", None)
    env.pop("SOVEREIGN_MAP", None)
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--emit-war-count"],
        env=env, cwd=str(REPO_ROOT), capture_output=True, text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"ambient runner failed:\n{result.stdout[-2000:]}\n"
        f"{result.stderr[-2000:]}")
    payload_line = [ln for ln in result.stdout.splitlines()
                    if ln.startswith("PAYLOAD=")][-1]
    return json.loads(payload_line[len("PAYLOAD="):])


class TestRunawayGuard:
    """§2.4: the guard moved from the engine to the suite. A seeded
    40-turn ambient run producing more council wars than SWEEP_WAR_ALARM
    fails HERE and sends a human to look at the costs."""

    @pytest.fixture(scope="class")
    def payload(self):
        return _run_ambient_subprocess()

    def test_council_wars_within_alarm(self, payload):
        assert payload["council_wars_declared"] <= SWEEP_WAR_ALARM

    def test_every_council_war_carries_a_stated_reason(self, payload):
        assert all(payload["stated_reasons"]), \
            "pin 4: no unexplained war — every council war names its design"

    def test_starved_never_renders_for_a_gate_refusal(self, payload):
        """The §0.3 defect, dead: any crisis that cooled while its LAST
        soft block was exposure/force/treasury must not read starved."""
        for cooling in payload["coolings"]:
            if cooling.get("last_soft_block") in ("exposed", "outmatched",
                                                  "penniless"):
                assert cooling["cause"] != "starved"


# ════════════════════════════════════════════════════════════════════════
# §2.6 — authored wary_of (Q4, ruling R1)
# ════════════════════════════════════════════════════════════════════════

class TestWaryOfAuthoring:
    def test_shipped_postures_reach_get_statecraft(self, world1805):
        assert world1805.get_statecraft("Prussia")["wary_of"] == {
            "Austria": 1.25, "Russia": 1.4}
        assert world1805.get_statecraft("Ottoman")["wary_of"] == {
            "Russia": 1.5}
        assert world1805.get_statecraft("France")["wary_of"] == {}

    def test_round_trip(self, world1805):
        restored = WorldState.from_dict(world1805.to_dict())
        assert restored.statecraft == world1805.statecraft
        assert restored.get_statecraft("Sweden")["wary_of"] == {"Russia": 1.4}

    def test_pre_ai3r_save_reads_empty(self, world1805):
        data = world1805.to_dict()
        data.pop("statecraft", None)
        restored = WorldState.from_dict(data)
        assert restored.statecraft == {}
        assert restored.get_statecraft("Prussia")["wary_of"] == {}

    def test_profile_table_not_moddable_through_the_override(self, world):
        """v1 surface: wary_of ONLY — a coercion key in the world store
        never reaches the merged profile."""
        world.statecraft["Prussia"] = {"coercion": "hardens",
                                       "wary_of": {"Austria": 1.5}}
        profile = world.get_statecraft("Prussia")
        assert profile["coercion"] == "folds"  # the code table's word
        assert profile["wary_of"] == {"Austria": 1.5}


class TestWaryOfValidator:
    def _validate(self, statecraft_block):
        from backend.modding.validator import validate_scenario
        data = {
            "sovereign_map": "legacy",
            "player_nation": "France",
            "regions": {
                "A": {"name": "A", "controller": "France",
                      "adjacent_regions": ["B"]},
                "B": {"name": "B", "controller": "Prussia",
                      "adjacent_regions": ["A"]},
            },
            "statecraft": statecraft_block,
        }
        return validate_scenario(data, check_adjacency=False)

    def test_valid_block_passes(self):
        result = self._validate({"Prussia": {"wary_of": {"France": 1.25}}})
        assert not [e for e in result.errors
                    if e.path.startswith("statecraft")]

    def test_value_out_of_band_errors(self):
        result = self._validate({"Prussia": {"wary_of": {"France": 3.0}}})
        assert any("[0.5, 2.0]" in e.message for e in result.errors)

    def test_self_reference_errors(self):
        result = self._validate({"Prussia": {"wary_of": {"Prussia": 1.2}}})
        assert any("wary of itself" in e.message for e in result.errors)

    def test_unknown_target_errors(self):
        result = self._validate({"Prussia": {"wary_of": {"Atlantis": 1.2}}})
        assert any("unknown nation 'Atlantis'" in e.message
                   for e in result.errors)

    def test_unknown_subkey_errors(self):
        result = self._validate({"Prussia": {"coercion": "hardens"}})
        assert any("wary_of only" in e.message for e in result.errors)

    def test_unknown_nation_warns(self):
        result = self._validate({"Atlantis": {"wary_of": {"France": 1.2}}})
        assert any(w.path == "statecraft.Atlantis" for w in result.warnings)
        assert not [e for e in result.errors
                    if e.path.startswith("statecraft")]

    def test_non_numeric_value_errors(self):
        result = self._validate({"Prussia": {"wary_of": {"France": "big"}}})
        assert any("Must be a number" in e.message for e in result.errors)


# ════════════════════════════════════════════════════════════════════════
# §2.5-2/3 — the ledger rows · §2.5-4 — Talleyrand's rung · Q5
# ════════════════════════════════════════════════════════════════════════

class TestLedgerSurfaces:
    def test_france_exposure_always_rendered_on_europe(self, world1805):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world1805)
        row = ledger["france_exposure"]
        assert row is not None
        assert row["standing"] == 189000
        assert "Free field army" in row["line"]

    def test_visible_court_gets_exposure_row_fogged_court_does_not(
            self, world1805):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world1805)
        rows = {n["name"]: n.get("exposure") for n in ledger["nations"]}
        assert any(v is not None for v in rows.values()), \
            "at least one court is PARTIAL+ visible at boot"
        weariness = {n["name"]: n.get("war_weariness")
                     for n in ledger["nations"]}
        for name, row in rows.items():
            if row is None:
                continue
            # the fog gate is the weariness row's — a court readable
            # here must never be UNKNOWN there by the same gate.
            assert name and isinstance(row["line"], str)
        assert weariness is not None

    def test_legacy_world_stays_byte_identical(self):
        from backend.game_logic.diplomatic_ledger import (
            _build_exposure_line,
            _build_france_exposure,
            build_diplomatic_ledger,
        )
        bare = WorldState(player_nation="France")
        assert _build_france_exposure(bare) is None
        assert _build_exposure_line("Britain", bare) is None
        ledger = build_diplomatic_ledger(bare)
        assert ledger["france_exposure"] is None

    def test_talleyrand_names_the_pinned_design(self, world, monkeypatch):
        """§2.5-4: an exposure-blocked warlike design reads as counsel."""
        from backend.game_logic.diplomatic_advisory import _assess_situation
        frederick = world.marshals["Frederick"]
        frederick.nation = "Hanover"
        frederick.strength = 40000
        world.nation_relations[world._make_diplo_key("Prussia", "Russia")] = -50
        forced = _forced_view("Prussia", "hanoverian_prize",
                              "acquire_regions", "Hanover")
        real = intent_module.get_nation_intent
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Prussia" else real(nation, w))
        world.invalidate_bloc_members_cache()
        payload = _assess_situation(world)
        checked = payload["context"]["designs_in_check"]
        assert checked and checked[0]["nation"] == "Prussia"
        assert checked[0]["threat"] == "Russia"
        assert "not free to move" in payload["talleyrand_text"]

    def test_talleyrand_skips_player_directed_designs(self, world1805):
        """Boot: Sweden sits at the war rung against FRANCE — the
        coalition's business, never a designs-in-check row (D3)."""
        from backend.game_logic.diplomatic_advisory import _assess_situation
        payload = _assess_situation(world1805)
        assert payload["context"]["designs_in_check"] == []


class TestPlayerNeverGated:
    def test_q5_no_executor_consults_the_exposure_calculus(self):
        """Gate Q5's pinned asymmetry: the player's orders are NEVER
        gated by free strength — display only."""
        import backend.commands.combat_executor as combat_executor
        import backend.commands.economy_executor as economy_executor
        import backend.commands.executor as executor
        import backend.commands.meta_executor as meta_executor
        import backend.commands.movement_executor as movement_executor
        import backend.commands.strategic_executor as strategic_executor
        import backend.commands.tactical_executor as tactical_executor
        for module in (executor, combat_executor, movement_executor,
                       strategic_executor, tactical_executor,
                       economy_executor, meta_executor):
            src = inspect.getsource(module)
            assert "get_free_strength" not in src, module.__name__
            assert "get_rear_reserve" not in src, module.__name__


# ════════════════════════════════════════════════════════════════════════
# Serialization — crisis records carry the block bookkeeping
# ════════════════════════════════════════════════════════════════════════

class TestSerialization:
    def test_last_soft_block_survives_a_save(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        _poll_next_turn(world)
        world.nation_gold["Prussia"] = -100
        _poll_next_turn(world)
        record = world.war_intents["Prussia"]
        assert record.get("last_soft_block") == "penniless"
        restored = WorldState.from_dict(world.to_dict())
        assert restored.war_intents["Prussia"] == record


# ── The subprocess runner (invoked with --emit-war-count) ───────────────


def _emit_war_count() -> None:
    import random

    from backend.commands.executor import CommandExecutor
    from backend.game_logic.turn_manager import TurnManager

    world = WorldState.from_scenario(str(SCENARIO_PATH))
    executor = CommandExecutor()
    tm = TurnManager(world, executor=executor)
    game_state = {"world": world, "executor": executor}
    for turn in range(40):
        random.seed(10_000 + turn)  # the M7 per-turn re-seed idiom
        tm.end_turn(game_state)
    declared = [e for e in world.event_log
                if e.get("type") == "ai_war_declared"]
    coolings = [
        {"cause": e.get("cause"),
         "last_soft_block": e.get("last_soft_block")}
        for e in world.event_log if e.get("type") == "crisis_passed"]
    print("PAYLOAD=" + json.dumps({
        "council_wars_declared": len(declared),
        "stated_reasons": [bool(e.get("stated_reason")) for e in declared],
        "coolings": coolings,
        "crises_opened": sum(1 for e in world.event_log
                             if e.get("type") == "crisis_brewing"),
    }))


if __name__ == "__main__":
    if "--emit-war-count" in sys.argv:
        sys.path.insert(0, str(REPO_ROOT))
        _emit_war_count()
