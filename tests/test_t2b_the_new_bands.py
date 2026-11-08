"""T2-B — the new bands of the Tier-2 gate record (`AI_INTENT_SPEC.md`
§3.8.2, ruled November 8, 2026; landed this slice; the rules
`SYSTEMS_REFERENCE.md` §187).

What this file pins:

  * INITIAL LADDER READINESS — a deck entry's authored
    `readiness`/`readiness_band` resolves at boot (seeded in-band, the
    band stripped, the authored centre on `historical`), rides
    `AgendaView.params`, and `_derive_weight` adds it (0 when unauthored
    — every pre-band deck derives byte-identically).
  * THE MINORS' LEAN — the statecraft `weight_mod` band resolves the
    same way; `get_statecraft` overlays the resolved int over the code
    table; `wary_of` is untouched.
  * THE VALIDATOR — both new shapes accepted, malformed shapes ERRORS
    (band not containing the value, edges past the clamps, booleans),
    readiness refused outside the top-level decks, and the roster
    widening (a live court with no authored region rows — Hesse — warns
    no more).
  * THE SCENARIO'S AUTHORED CONTENT — four readiness bands (Austria's
    pair, Prussia's prize, Britain's Low Countries; Russia none, pin 22),
    ten lean dials with centres equal to the code table's effective
    values, so the historical seed is byte-identical.
  * THE MEASURE — the dated re-record
    `tools/_dy_signature_bands_2026_11_08.json` against the committed
    PRE-BAND baseline: the class count and which seeds' stories moved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.campaign_variance import (  # noqa: E402
    apply_scenario_variance,
    resolve_statecraft_bands,
)
from backend.modding.validator import validate_scenario  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
BASELINE = REPO / "tools" / "_dy_signature_baseline.json"
BANDS_RECORD = REPO / "tools" / "_dy_signature_bands_2026_11_08.json"


@pytest.fixture(scope="module")
def hist_world(request):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


@pytest.fixture(scope="module")
def ulm_world(request):
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="ulm")


# ═══════════════════════════════════════════════════════════════════════
# The resolvers
# ═══════════════════════════════════════════════════════════════════════
class TestTheResolvers:
    def _data(self):
        return {
            "agendas": {"Austria": [
                {"id": "a", "type": "acquire_regions",
                 "readiness": 0, "readiness_band": [-6, 6]},
                {"id": "b", "type": "acquire_regions"}]},
            "statecraft": {"Saxony": {
                "weight_mod": {"value": -8, "band": [-14, -2]}}},
        }

    def test_historical_collapses_to_the_centre(self):
        data = apply_scenario_variance(self._data(), "historical")
        entry = data["agendas"]["Austria"][0]
        assert entry["readiness"] == 0 and "readiness_band" not in entry
        assert data["statecraft"]["Saxony"]["weight_mod"] == -8

    def test_a_seed_resolves_inside_the_band_and_strips_it(self):
        data = apply_scenario_variance(self._data(), "ulm")
        entry = data["agendas"]["Austria"][0]
        assert -6 <= entry["readiness"] <= 6
        assert "readiness_band" not in entry
        weight_mod = data["statecraft"]["Saxony"]["weight_mod"]
        assert isinstance(weight_mod, int) and -14 <= weight_mod <= -2

    def test_an_unauthored_entry_is_untouched(self):
        data = apply_scenario_variance(self._data(), "ulm")
        assert "readiness" not in data["agendas"]["Austria"][1]

    def test_the_same_seed_resolves_the_same_values(self):
        one = apply_scenario_variance(self._data(), "jena")
        two = apply_scenario_variance(self._data(), "jena")
        assert one == two

    def test_statecraft_resolver_is_idempotent_and_leaves_wary_of(self):
        block = {"Prussia": {"wary_of": {"Austria": 1.25}},
                 "Saxony": {"weight_mod": {"value": -8, "band": [-14, -2]}}}
        resolve_statecraft_bands(block, "ulm")
        first = block["Saxony"]["weight_mod"]
        resolve_statecraft_bands(block, "ulm")
        assert block["Saxony"]["weight_mod"] == first
        assert block["Prussia"]["wary_of"] == {"Austria": 1.25}


# ═══════════════════════════════════════════════════════════════════════
# The engine reads
# ═══════════════════════════════════════════════════════════════════════
class TestTheEngineReads:
    def test_get_statecraft_overlays_the_resolved_int(self, hist_world):
        assert hist_world.get_statecraft("Saxony")["weight_mod"] == -8
        assert hist_world.get_statecraft("Hesse")["weight_mod"] == -12
        assert hist_world.get_statecraft("Denmark")["weight_mod"] == 0
        # a court with no scenario row keeps the code table's value
        assert hist_world.get_statecraft("Austria")["weight_mod"] == 0

    def test_garbage_overlay_falls_back_to_the_table(self, hist_world):
        hist_world.statecraft.setdefault("Bavaria", {})["weight_mod"] = "x"
        try:
            assert hist_world.get_statecraft("Bavaria")["weight_mod"] == 0
        finally:
            hist_world.statecraft.pop("Bavaria", None)

    def test_derive_weight_consumes_readiness(self, hist_world):
        from backend.game_logic.agendas import AgendaView
        from backend.game_logic.intent import _derive_weight
        base = AgendaView(nation="Austria", id="x",
                          type="acquire_regions", title="x",
                          params={})
        ready = AgendaView(nation="Austria", id="x",
                           type="acquire_regions", title="x",
                           params={"readiness": 6})
        quiet = _derive_weight("Austria", base, None, hist_world)
        keen = _derive_weight("Austria", ready, None, hist_world)
        assert keen == quiet + 6

    def test_the_historical_boot_is_byte_identical(self, hist_world):
        """Every authored centre is today's effective value: readiness 0
        on all four banded entries, the leans the code table's own."""
        for nation in ("Austria", "Prussia", "Britain"):
            for entry in hist_world.agendas.get(nation, []):
                assert int(entry.get("readiness", 0) or 0) == 0, entry
        from backend.nation_config import NATION_STATECRAFT
        assert hist_world.get_statecraft("Saxony")["weight_mod"] == \
            NATION_STATECRAFT["Saxony"]["weight_mod"]
        assert hist_world.get_statecraft("Hesse")["weight_mod"] == \
            NATION_STATECRAFT["Hesse"]["weight_mod"]

    def test_a_seeded_boot_varies_and_round_trips(self, ulm_world):
        from backend.models.world_state import WorldState
        readiness = {e["id"]: e.get("readiness")
                     for e in ulm_world.agendas.get("Austria", [])
                     if "readiness" in e}
        assert readiness and any(v != 0 for v in readiness.values())
        lean = ulm_world.get_statecraft("Saxony")["weight_mod"]
        assert -14 <= lean <= -2
        back = WorldState.from_dict(ulm_world.to_dict())
        assert {e["id"]: e.get("readiness")
                for e in back.agendas.get("Austria", [])
                if "readiness" in e} == readiness
        assert back.get_statecraft("Saxony")["weight_mod"] == lean

    def test_russias_deck_stays_unbanded(self, hist_world):
        """Pin 22's sibling: no readiness key on any Russian entry."""
        for entry in hist_world.agendas.get("Russia", []):
            assert "readiness" not in entry, entry


# ═══════════════════════════════════════════════════════════════════════
# The validator
# ═══════════════════════════════════════════════════════════════════════
def _scenario_stub(statecraft=None, deck=None):
    stub = {"name": "t2b", "sovereign_map": "europe"}
    if statecraft is not None:
        stub["statecraft"] = statecraft
    if deck is not None:
        stub["agendas"] = {"Austria": deck}
    return stub


class TestTheValidator:
    def _errors(self, stub):
        result = validate_scenario(stub)
        return [str(e) for e in result.errors
                if "statecraft" in str(e) or "readiness" in str(e)
                or "agendas" in str(e)]

    def test_the_shipped_scenario_passes_clean(self):
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        result = validate_scenario(data)
        assert result.is_valid, [str(e) for e in result.errors[:5]]
        noise = [str(w) for w in result.warnings
                 if "statecraft" in str(w)]
        assert noise == [], noise

    def test_good_shapes_pass(self):
        stub = _scenario_stub(
            statecraft={"Saxony": {"weight_mod": {"value": -8,
                                                  "band": [-14, -2]}},
                        "Denmark": {"weight_mod": 3}},
            deck=[{"id": "a", "type": "acquire_regions",
                   "regions": ["Milan"], "title": "x",
                   "readiness": 0, "readiness_band": [-6, 6]}])
        assert self._errors(stub) == []

    def test_a_band_must_contain_the_value(self):
        stub = _scenario_stub(statecraft={"Saxony": {
            "weight_mod": {"value": -20, "band": [-14, -2]}}})
        assert any("must contain" in e for e in self._errors(stub))

    def test_edges_stay_inside_the_clamps(self):
        stub = _scenario_stub(statecraft={"Saxony": {
            "weight_mod": {"value": 0, "band": [-30, 0]}}})
        assert any("within [-24, 12]" in e for e in self._errors(stub))
        stub = _scenario_stub(deck=[{
            "id": "a", "type": "acquire_regions", "regions": ["Milan"],
            "title": "x", "readiness": 0, "readiness_band": [-12, 0]}])
        assert any("within [-10, 10]" in e for e in self._errors(stub))

    def test_booleans_and_unknown_keys_are_errors(self):
        stub = _scenario_stub(statecraft={"Saxony": {
            "weight_mod": True}})
        assert self._errors(stub)
        stub = _scenario_stub(statecraft={"Saxony": {
            "weight_mod": {"value": 0, "band": [-6, 6], "mode": "x"}}})
        assert any("Unknown key" in e for e in self._errors(stub))

    def test_readiness_refused_outside_the_top_level_decks(self):
        """The seed resolver only touches `scenario_data["agendas"]` — a
        formable-template deck (`allow_order_group=False`, the AI-0c
        gate order_group already uses) refuses the key the same way."""
        from backend.modding.validator import (
            ValidationResult,
            _validate_agenda_deck,
        )
        result = ValidationResult()
        _validate_agenda_deck(
            result, "formable_nations.Germany.deck",
            [{"id": "a", "type": "acquire_regions", "regions": ["Milan"],
              "title": "x", "readiness": 2}],
            {"Milan"}, allow_order_group=False)
        assert any("top-level" in str(e) for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════
# The measure — the dated re-record against the pre-band baseline
# ═══════════════════════════════════════════════════════════════════════
class TestTheMeasure:
    @pytest.fixture(scope="class")
    def records(self):
        return (json.loads(BASELINE.read_text(encoding="utf-8")),
                json.loads(BANDS_RECORD.read_text(encoding="utf-8")))

    def test_the_banded_board_keeps_the_floor(self, records):
        baseline, banded = records
        assert banded["story_class_count"] >= baseline["story_class_count"]

    def test_historical_is_byte_identical(self, records):
        baseline, banded = records
        assert (banded["seeds"]["historical"]
                == baseline["seeds"]["historical"])

    def test_the_moved_seeds_are_the_record(self, records):
        baseline, banded = records
        moved = sorted(
            seed for seed in baseline["seeds"]
            if banded["seeds"][seed]["signature"]
            != baseline["seeds"][seed]["signature"])
        assert moved == MOVED_SEEDS, moved


# The dated re-record's truth (the chain of November 8, 2026): seven
# seeds' world-lines moved under the new bands; friedland's and rivoli's
# draws landed on no-op positions and kept theirs; the historical seed
# never moves — the byte-law. The banded board reads 10 of 10 story
# classes (the pre-band floor was 9 — the eylau/rivoli tie broke).
MOVED_SEEDS = ["austerlitz", "eylau", "jena", "lodi", "marengo", "ulm",
               "wagram"]
