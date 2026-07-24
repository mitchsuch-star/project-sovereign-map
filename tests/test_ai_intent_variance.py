"""AI-0b — the campaign seed (docs/AI_INTENT_SPEC.md §3.8, §6 D7, Stage A).

Covers: seed resolution precedence, the serialized WorldState.campaign_seed
field and its §5 pin 14(c) round-trip contract, the deterministic derivation
helpers (seeded_int / jitter / tiebreak / permutation), authored-band
resolution (apply_scenario_variance), the validator's band schema, and the
shown-and-shareable surfaces (strategic ledger + save metadata).

The historian test (six clauses, N-seed sweep) lives in
test_ai_intent_historical_envelope.py.
"""

import json
from pathlib import Path

import pytest

from backend.game_logic.campaign_variance import (
    HISTORICAL_SEED,
    JITTER_RAMP_TURNS,
    apply_scenario_variance,
    is_historical,
    resolve_campaign_seed,
    seeded_int,
    seeded_jitter,
    seeded_permutation,
    seeded_tiebreak,
)
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


# ════════════════════════════════════════════════════════════════════════
# Seed resolution precedence: explicit > SOVEREIGN_SEED env > historical
# ════════════════════════════════════════════════════════════════════════

class TestSeedResolution:
    def test_default_is_historical(self, monkeypatch):
        monkeypatch.delenv("SOVEREIGN_SEED", raising=False)
        assert resolve_campaign_seed() == HISTORICAL_SEED

    def test_env_wins_over_default(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "marengo")
        assert resolve_campaign_seed() == "marengo"

    def test_explicit_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "marengo")
        assert resolve_campaign_seed("ulm") == "ulm"

    def test_blank_explicit_falls_through_to_env(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "marengo")
        assert resolve_campaign_seed("   ") == "marengo"

    def test_blank_env_falls_through_to_historical(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "   ")
        assert resolve_campaign_seed() == HISTORICAL_SEED

    def test_is_historical_semantics(self):
        assert is_historical(None)
        assert is_historical("")
        assert is_historical("historical")
        assert is_historical("HISTORICAL")
        assert is_historical("  historical  ")
        assert not is_historical("ulm")


# ════════════════════════════════════════════════════════════════════════
# The serialized field + pin 14(c): from_dict restores EXACTLY
# ════════════════════════════════════════════════════════════════════════

class TestWorldSeedField:
    def test_conftest_pins_suite_to_historical(self):
        # Defence-in-depth pin: the suite-wide autouse fixture (conftest)
        # keeps every incidentally-built world on the historical seed.
        assert WorldState(player_nation="France").campaign_seed == \
            HISTORICAL_SEED

    def test_bare_ctor_reads_env(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "eylau")
        assert WorldState(player_nation="France").campaign_seed == "eylau"

    def test_to_dict_carries_seed(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "eylau")
        world = WorldState(player_nation="France")
        assert world.to_dict()["campaign_seed"] == "eylau"

    def test_from_dict_restores_exact_seed_never_env(self, monkeypatch):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        data["campaign_seed"] = "wagram"
        # A hostile environment must not leak into the restore (pin 14c:
        # never a freshly generated or env-derived value).
        monkeypatch.setenv("SOVEREIGN_SEED", "not-wagram")
        assert WorldState.from_dict(data).campaign_seed == "wagram"

    def test_pre_seed_save_reads_historical(self, monkeypatch):
        world = WorldState(player_nation="France")
        data = world.to_dict()
        data.pop("campaign_seed", None)
        monkeypatch.setenv("SOVEREIGN_SEED", "not-historical")
        assert WorldState.from_dict(data).campaign_seed == HISTORICAL_SEED

    def test_from_scenario_seed_param_overrides_env(self, monkeypatch):
        monkeypatch.setenv("SOVEREIGN_SEED", "env-seed")
        world = WorldState.from_scenario(str(SCENARIO_PATH), seed="ulm")
        assert world.campaign_seed == "ulm"

    def test_scenario_roundtrip_preserves_seed_and_dispositions(self):
        world = WorldState.from_scenario(str(SCENARIO_PATH), seed="ulm")
        restored = WorldState.from_dict(world.to_dict())
        assert restored.campaign_seed == "ulm"
        assert restored.nation_relations == world.nation_relations
        assert restored.threat_level == world.threat_level
        assert ([e["id"] for e in restored.agendas["Austria"]]
                == [e["id"] for e in world.agendas["Austria"]])
        # Every seeded quantity recomputes identically after a load (14c):
        assert (seeded_jitter(restored.campaign_seed, "weight::Prussia",
                              8, 6)
                == seeded_jitter(world.campaign_seed, "weight::Prussia",
                                 8, 6))

    def test_same_seed_boots_are_identical(self):
        a = WorldState.from_scenario(str(SCENARIO_PATH), seed="ulm")
        b = WorldState.from_scenario(str(SCENARIO_PATH), seed="ulm")
        assert a.to_dict() == b.to_dict()


# ════════════════════════════════════════════════════════════════════════
# Derivation helpers — pure, deterministic, module-RNG-free
# ════════════════════════════════════════════════════════════════════════

class TestDerivationHelpers:
    def test_seeded_int_bounds_and_determinism(self):
        for namespace in ("a", "b", "relations::France|Prussia"):
            value = seeded_int("ulm", namespace, -25, 5)
            assert -25 <= value <= 5
            assert value == seeded_int("ulm", namespace, -25, 5)

    def test_seeded_int_varies_by_namespace_and_seed(self):
        values = {seeded_int("ulm", f"ns-{i}", 0, 1000) for i in range(16)}
        assert len(values) > 8
        assert (seeded_int("ulm", "ns", 0, 10 ** 6)
                != seeded_int("jena-06", "ns", 0, 10 ** 6))

    def test_seeded_int_degenerate_band(self):
        assert seeded_int("ulm", "ns", 7, 7) == 7
        assert seeded_int("ulm", "ns", 7, 3) == 7  # inverted -> lo

    def test_seeded_int_never_touches_module_rng(self):
        import random
        random.seed(1234)
        expected = random.random()
        random.seed(1234)
        seeded_int("ulm", "ns", 0, 100)
        seeded_jitter("ulm", "ns", 10, 20)
        seeded_permutation("ulm", "ns", [1, 2, 3, 4])
        # The ambient stream is unmoved — pin 2 (M1-M7) depends on this.
        assert random.random() == expected

    def test_jitter_historical_is_zero(self):
        assert seeded_jitter(HISTORICAL_SEED, "ns", 10, 40) == 0

    def test_jitter_turn_zero_is_zero(self):
        # §3.8 "weighted late": turn 1 of 1805 looks like 1805 on every
        # seed — the boot spread is the AUTHORED bands, never this ramp.
        assert seeded_jitter("ulm", "ns", 10, 0) == 0

    def test_jitter_bounded_and_ramped(self):
        for turn in range(0, JITTER_RAMP_TURNS * 2):
            scale = min(1.0, turn / JITTER_RAMP_TURNS)
            span = int(round(10 * scale))
            value = seeded_jitter("ulm", "ns", 10, turn)
            assert abs(value) <= span

    def test_jitter_deterministic(self):
        assert (seeded_jitter("ulm", "ns", 10, 6)
                == seeded_jitter("ulm", "ns", 10, 6))

    def test_jitter_is_actually_alive(self):
        # Review fix [10]: a constant-0 jitter passed every bound test —
        # pin measured NONZERO draws so the mechanic cannot die silently.
        # (A mid-range unit draws 0 at every amplitude by design — the
        # draw is a fixed per-namespace disposition scaled by the ramp —
        # so the pin uses namespaces measured to draw hot/cold.)
        assert seeded_jitter(
            "ulm", "intent_weight::Austria::redeem_italy", 8, 20) == -5
        assert seeded_jitter(
            "jena-06", "intent_weight::Prussia::hanoverian_prize",
            8, 20) == 4

    def test_tiebreak_historical_takes_first(self):
        assert seeded_tiebreak(HISTORICAL_SEED, "ns", ["a", "b", "c"]) == "a"

    def test_tiebreak_seeded_in_set_and_deterministic(self):
        pick = seeded_tiebreak("ulm", "ns", ["a", "b", "c"])
        assert pick in ("a", "b", "c")
        assert pick == seeded_tiebreak("ulm", "ns", ["a", "b", "c"])

    def test_tiebreak_empty_and_singleton(self):
        assert seeded_tiebreak("ulm", "ns", []) is None
        assert seeded_tiebreak("ulm", "ns", ["only"]) == "only"

    def test_permutation_historical_is_identity(self):
        items = ["a", "b", "c", "d"]
        assert seeded_permutation(HISTORICAL_SEED, "ns", items) == items

    def test_permutation_is_a_permutation_and_deterministic(self):
        items = ["a", "b", "c", "d", "e"]
        perm = seeded_permutation("ulm", "ns", items)
        assert sorted(perm) == sorted(items)
        assert perm == seeded_permutation("ulm", "ns", items)


# ════════════════════════════════════════════════════════════════════════
# Band resolution (unit level, synthetic scenario dicts)
# ════════════════════════════════════════════════════════════════════════

def _banded_scenario():
    return {
        "nation_relations": {
            "Austria|France": -80,
            "France|Prussia": {"value": -10, "band": [-25, 5]},
        },
        "threat_level": 85,
        "threat_level_band": [80, 90],
        "agendas": {
            "Austria": [
                {"id": "one", "type": "guard_neutrality",
                 "title": "One", "regions": ["X"], "order_group": 1},
                {"id": "two", "type": "guard_neutrality",
                 "title": "Two", "regions": ["X"], "order_group": 1},
            ],
        },
    }


class TestApplyScenarioVariance:
    def test_historical_collapses_to_centres(self):
        data = apply_scenario_variance(_banded_scenario(), HISTORICAL_SEED)
        assert data["nation_relations"]["France|Prussia"] == -10
        assert data["nation_relations"]["Austria|France"] == -80
        assert data["threat_level"] == 85
        assert "threat_level_band" not in data
        assert [e["id"] for e in data["agendas"]["Austria"]] == ["one", "two"]
        assert all("order_group" not in e
                   for e in data["agendas"]["Austria"])

    def test_seeded_resolves_inside_bands(self):
        data = apply_scenario_variance(_banded_scenario(), "ulm")
        assert -25 <= data["nation_relations"]["France|Prussia"] <= 5
        assert data["nation_relations"]["Austria|France"] == -80
        assert 80 <= data["threat_level"] <= 90
        assert "threat_level_band" not in data
        assert (sorted(e["id"] for e in data["agendas"]["Austria"])
                == ["one", "two"])
        assert all("order_group" not in e
                   for e in data["agendas"]["Austria"])

    def test_no_band_no_variance(self):
        data = {"nation_relations": {"Austria|France": -80},
                "threat_level": 85}
        resolved = apply_scenario_variance(dict(data), "ulm")
        assert resolved["nation_relations"] == {"Austria|France": -80}
        assert resolved["threat_level"] == 85

    def test_ungrouped_entries_anchor_their_positions(self):
        data = {
            "agendas": {
                "N": [
                    {"id": "a", "order_group": 1},
                    {"id": "b", "order_group": 1},
                    {"id": "anchor"},
                    {"id": "c", "order_group": 2},
                    {"id": "d", "order_group": 2},
                ],
            },
        }
        resolved = apply_scenario_variance(data, "ulm")
        ids = [e["id"] for e in resolved["agendas"]["N"]]
        assert sorted(ids[0:2]) == ["a", "b"]
        assert ids[2] == "anchor"
        assert sorted(ids[3:5]) == ["c", "d"]


# ════════════════════════════════════════════════════════════════════════
# Validator — the authored envelope's schema and clamps
# ════════════════════════════════════════════════════════════════════════

class TestValidatorBands:
    @staticmethod
    def _validate(data):
        from backend.modding.validator import validate_scenario
        return validate_scenario(data, check_adjacency=False)

    def test_shipped_scenario_is_valid(self):
        with open(SCENARIO_PATH, encoding="utf-8") as f:
            data = json.load(f)
        result = self._validate(data)
        assert result.is_valid, [
            f"{e.path}: {e.message}" for e in result.errors]

    def test_band_must_contain_value(self):
        result = self._validate({"nation_relations": {
            "France|Prussia": {"value": -10, "band": [0, 10]}}})
        assert not result.is_valid

    def test_object_without_band_is_error(self):
        result = self._validate({"nation_relations": {
            "France|Prussia": {"value": -10}}})
        assert not result.is_valid

    def test_malformed_band_is_error(self):
        for band in ([5], [5, "x"], [10, -10], [-200, 0], "cold"):
            result = self._validate({"nation_relations": {
                "France|Prussia": {"value": 0, "band": band}}})
            assert not result.is_valid, f"band {band!r} should fail"

    def test_unsorted_pair_key_is_error(self):
        result = self._validate({"nation_relations": {"Prussia|France": -10}})
        assert not result.is_valid

    def test_war_pair_band_clamped_below_armistice_line(self):
        # A pair that boots at war may never carry a band that crosses the
        # -60 armistice-first line (§3.8.1 clamp).
        result = self._validate({
            "starting_wars": [
                {"attacker": "France", "defender": "Britain"}],
            "nation_relations": {
                "Britain|France": {"value": -90, "band": [-95, -55]}},
        })
        assert not result.is_valid
        result_ok = self._validate({
            "starting_wars": [
                {"attacker": "France", "defender": "Britain"}],
            "nation_relations": {
                "Britain|France": {"value": -90, "band": [-95, -65]}},
        })
        assert result_ok.is_valid, [
            f"{e.path}: {e.message}" for e in result_ok.errors]

    def test_threat_band_must_contain_authored_value(self):
        result = self._validate({"threat_level": 85,
                                 "threat_level_band": [40, 60]})
        assert not result.is_valid

    def test_threat_band_malformed_is_error(self):
        for band in ([80], [90, 80], [-5, 90], [80, 105], "hot"):
            result = self._validate({"threat_level": 85,
                                     "threat_level_band": band})
            assert not result.is_valid, f"band {band!r} should fail"

    def test_threat_band_without_centre_is_error(self):
        # Review fix [0]: a band with no authored threat_level would make
        # the historical seed (absent -> 0) and every variance seed
        # (80-90) diverge structurally. No centre, no band.
        result = self._validate({"threat_level_band": [80, 90]})
        assert not result.is_valid

    def test_formable_template_deck_rejects_order_group(self):
        # Review fix [1]: the seed resolver never permutes a dormant
        # formable-template deck — an order band there is rejected, not
        # silently ignored.
        result = self._validate({"formable_nations": {"Ruritania": {
            "display_name": "Ruritania",
            "provinces": ["X"],
            "deck": [
                {"id": "a", "type": "guard_neutrality", "title": "A",
                 "regions": ["X"], "order_group": 1},
                {"id": "b", "type": "guard_neutrality", "title": "B",
                 "regions": ["X"], "order_group": 1},
            ],
        }}})
        assert not result.is_valid
        assert any("order_group" in e.path for e in result.errors)

    def test_order_group_non_contiguous_is_error(self):
        result = self._validate({"agendas": {"N": [
            {"id": "a", "type": "guard_neutrality", "title": "A",
             "regions": ["X"], "order_group": 1},
            {"id": "b", "type": "guard_neutrality", "title": "B",
             "regions": ["X"]},
            {"id": "c", "type": "guard_neutrality", "title": "C",
             "regions": ["X"], "order_group": 1},
        ]}})
        assert not result.is_valid

    def test_order_group_single_member_warns_but_passes(self):
        result = self._validate({"agendas": {"N": [
            {"id": "a", "type": "guard_neutrality", "title": "A",
             "regions": ["X"], "order_group": 1},
        ]}})
        assert result.is_valid
        assert any("order_group" in w.path for w in result.warnings)

    def test_order_group_malformed_is_error(self):
        for group in (0, -1, True, "first", 1.5):
            result = self._validate({"agendas": {"N": [
                {"id": "a", "type": "guard_neutrality", "title": "A",
                 "regions": ["X"], "order_group": group},
            ]}})
            assert not result.is_valid, f"group {group!r} should fail"


# ════════════════════════════════════════════════════════════════════════
# Shown and shareable — ledger + save metadata (§3.8.1)
# ════════════════════════════════════════════════════════════════════════

class TestSeedSurfaces:
    def test_strategic_ledger_carries_seed(self):
        from backend.game_logic.ledger import build_strategic_ledger
        world = WorldState.from_scenario(str(SCENARIO_PATH), seed="ulm")
        assert build_strategic_ledger(world)["campaign_seed"] == "ulm"

    def test_save_metadata_carries_seed(self, tmp_path):
        from backend.save_manager import save_game
        world = WorldState(player_nation="France")
        world.campaign_seed = "ulm"
        filepath = tmp_path / "seed_probe.json"
        result = save_game(world, "Seed Probe", filepath=filepath)
        assert result.get("success"), result
        with open(filepath, encoding="utf-8") as f:
            payload = json.load(f)
        assert payload["metadata"]["campaign_seed"] == "ulm"
        assert payload["world_state"]["campaign_seed"] == "ulm"


# ════════════════════════════════════════════════════════════════════════
# Pin 14(a) — the historical seed IS today's boot
# ════════════════════════════════════════════════════════════════════════

class TestHistoricalByteIdentity:
    def test_unset_env_equals_explicit_historical(self, monkeypatch):
        monkeypatch.delenv("SOVEREIGN_SEED", raising=False)
        unset = WorldState.from_scenario(str(SCENARIO_PATH))
        explicit = WorldState.from_scenario(str(SCENARIO_PATH),
                                            seed=HISTORICAL_SEED)
        assert unset.to_dict() == explicit.to_dict()

    def test_historical_resolves_authored_centres(self):
        world = WorldState.from_scenario(str(SCENARIO_PATH),
                                         seed=HISTORICAL_SEED)
        # The banded pairs resolve to their authored centres — the exact
        # pre-band values of the shipped 1805 opening.
        assert world.nation_relations["France|Prussia"] == -10
        assert world.nation_relations["Britain|Russia"] == 70
        assert world.nation_relations["Austria|Britain"] == 60
        assert world.nation_relations["Prussia|Russia"] == 30
        assert world.nation_relations["Ottoman|Russia"] == 20
        assert world.nation_relations["Denmark|France"] == 10
        assert world.nation_relations["France|Saxony"] == -10
        assert world.nation_relations["France|Naples"] == -30
        # The two grudge pairs are NEW keys authored at the behaviour-
        # neutral centre 0 (an unauthored pair reads 0 at every seam).
        assert world.nation_relations["Austria|Prussia"] == 0
        assert world.nation_relations["Hanover|Prussia"] == 0
        assert world.threat_level == 85
        # No band residue reaches the world or the save.
        assert all(isinstance(v, int)
                   for v in world.nation_relations.values())
        assert all("order_group" not in e
                   for deck in world.agendas.values() for e in deck)
