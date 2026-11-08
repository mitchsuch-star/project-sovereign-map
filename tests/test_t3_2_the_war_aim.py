"""T3-2 — `war_council.war_aim`: one read, spoken in words
(`AI_INTENT_SPEC.md` §13.2 R3; `DYNAMISM_SPEC.md` §2 Tier 3;
November 8, 2026; the rules `SYSTEMS_REFERENCE.md` §194).

ONE public read of the EXISTING objective record per R1's union —
`war_aims_of_instance` is THE derivation (moved home from the
instrument; `RunCapture._war_aims` delegates, so the live read and
the march metric cannot diverge), `war_aim(world, nation, enemy)`
unions it over the pair's live wars, and `war_aim_line` speaks the
OUTSTANDING object (a held province is no object; a lost one joins
the line the turn it falls — the boot DEFENSE objectives put a
court's own soil in the metric's set, which is right for the march
gauge and noise as words). Two folds, zero client changes: the war
room's enemy block (the PC-R7 type_display idiom) and the intent
summary (the defenceless-prize fold's twin).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic.war_council import (  # noqa: E402
    war_aim,
    war_aim_line,
    war_aims_of_instance,
)

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _fresh_eyes(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


class TestTheRead:
    def test_the_boot_aim_carries_the_design_arm(self, world):
        # R1's design arm on the live boot: redeem_italy's provinces —
        # Milan through the Kingdom of Italy (the overlord read),
        # Piedmont and Savoy France's own.
        aims = war_aim(world, "Austria", "France")
        assert {"Milan", "Piedmont", "Savoy"} <= set(aims)

    def test_the_boot_aim_carries_the_defense_records(self, world):
        # The boot pairs carry the declaration's default DEFENSE
        # objective (FA-D4) — a court's own soil sits in the metric's
        # set (recapturing Vienna is never drift; T3-1's 397 counts
        # with these in, deliberately).
        aims = war_aim(world, "Austria", "France")
        assert "Vienna" in aims

    def test_a_pair_not_at_war_reads_empty(self, world):
        assert war_aim(world, "Prussia", "France") == []

    def test_a_crafted_objective_record_joins_the_read(self, world):
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Flanders"]}
        assert "Flanders" in war_aim(world, "Austria", "France")

    def test_the_instrument_delegates(self, world):
        # One body: the sweep's `_war_aims` IS the council's derivation.
        from tools.ai_v_sweep import RunCapture
        capture = RunCapture(world)
        for inst in (world.war_instances or {}).values():
            assert capture._war_aims(inst) \
                == war_aims_of_instance(world, inst)


class TestTheWords:
    def test_the_line_speaks_the_outstanding_object(self, world):
        # Held soil is no object: the boot line is the Italian design,
        # never the defense record's own provinces.
        line = war_aim_line(world, "Austria", "France")
        assert line == "her object: Milan, Piedmont and Savoy"

    def test_a_lost_province_joins_the_line(self, world):
        world.regions["Tyrol"].controller = "Bavaria"
        _fresh_eyes(world)
        assert war_aim_line(world, "Austria", "France") \
            == "her object: Milan, Piedmont, Savoy and Tyrol"

    def test_no_aim_no_line(self, world):
        assert war_aim_line(world, "Prussia", "France") == ""

    def test_the_enemy_block_folds_the_aim(self, world):
        # The fold's own site (the boot war room renders ONE row —
        # Britain the leader, whose outstanding object is honestly
        # empty: the Low Countries design is DENY, outside R1's
        # acquire arm — so the unit pin asks the block directly).
        from backend.game_logic.war_status import _objective_block
        _info, enemy = _objective_block(
            world, "France", "Austria", [],
            world._make_diplo_key("France", "Austria"))
        assert enemy is not None
        assert enemy.get("aim_display") \
            == "her object: Milan, Piedmont and Savoy"
        assert "her object: Milan, Piedmont and Savoy" \
            in enemy.get("type_display", "")

    def test_the_peace_table_names_each_courts_object(self, world):
        # The war room's real surface: the one boot row's peace table
        # speaks Austria's object among its court-by-court lines.
        from backend.game_logic.war_status import build_active_wars
        rows = build_active_wars(world)["wars"]
        assert rows, "the boot board carries the coalition war's row"
        lines = []
        for row in rows:
            lines.extend((row.get("peace_table") or {}).get("lines", []))
        assert any(
            "Austria's object in this war: Milan, Piedmont and Savoy"
            in line for line in lines), lines

    def test_the_ledger_folds_the_aim_at_war(self, world):
        from backend.game_logic.intent import build_intent_payload
        payload = build_intent_payload("Austria", world)
        assert "at war, her object: Milan, Piedmont and Savoy" \
            in payload["summary"]

    def test_the_ledger_never_folds_at_peace(self, world):
        # Prussia stands at align over Hanover, not at war — the
        # summary is exactly the pre-T3-2 composition (no fold).
        from backend.game_logic.intent import build_intent_payload
        payload = build_intent_payload("Prussia", world)
        assert "her object" not in payload["summary"]

    def test_the_measure_reads_zero_movers(self):
        """The dated chain (`_dy_signature_t3_2_2026_11_08.json`) vs the
        T3-1 baseline: words live in payloads, not the world-line, and
        the derivation's move is byte-neutral by delegation — ZERO
        movers, the debt 397 unchanged, historical identical, classes
        10 of 10 (the kept-record idiom; all four pinned)."""
        import json as _json
        t31 = _json.loads(
            (REPO / "tools" / "_t3_march_baseline_2026_11_08.json")
            .read_text(encoding="utf-8"))
        t32 = _json.loads(
            (REPO / "tools" / "_dy_signature_t3_2_2026_11_08.json")
            .read_text(encoding="utf-8"))
        movers = [s for s in sorted(t31["seeds"])
                  if t31["seeds"][s]["signature"]
                  != t32["seeds"][s]["signature"]]
        assert movers == []
        assert sum(t32["seeds"][s]["signature"]["captures_outside_aim"]
                   for s in t32["seeds"]) == 397
        assert t32["story_class_count"] == 10
        assert t31["seeds"]["historical"]["signature"] \
            == t32["seeds"]["historical"]["signature"]

    def test_an_aimless_war_folds_nothing(self, world):
        # A staged war with no objective record and no design arm:
        # the read is empty, both surfaces stay as they were.
        from backend.game_logic.intent import build_intent_payload
        world.war_instances["t3_2::Sweden|Denmark"] = {
            "attackers": ["Sweden"], "defenders": ["Denmark"],
            "participant_meta": {"Sweden": {"side": "attackers"},
                                 "Denmark": {"side": "defenders"}},
        }
        world.diplomatic_states[world._make_diplo_key(
            "Sweden", "Denmark")] = "WAR"
        _fresh_eyes(world)
        # Sweden's contain design carries no acquire arm vs Denmark and
        # no objective record exists for the staged pair.
        assert war_aim(world, "Sweden", "Denmark") == []
        payload = build_intent_payload("Sweden", world)
        if payload is not None:
            assert "her object" not in payload["summary"]
