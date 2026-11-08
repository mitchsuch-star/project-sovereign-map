"""T3-1 — the march metric (`AI_INTENT_SPEC.md` §13.2 the Tier-3 gate
record, R1/R2; `DYNAMISM_SPEC.md` §2 Tier 3; November 8, 2026; the
rules `SYSTEMS_REFERENCE.md` §193).

The measure precedes the build (the DY-0 pattern): `captures_outside_aim`
derives OFFLINE from the digest alone — the `region_captured` event rows
joined against the aim-sets read at each war's opening (`aims` on the
`wars_opened` rows; the BOOT wars' on `boot.wars`, since `_war_ids`
pre-seeds with them). R1's aim-set, deliberately narrow: the
`war_objectives` record's resolved `target_regions` ∪ the active ACQUIRE
design's regions held by the opposing side (overlord-resolved) — enemy
soil is NEVER automatically in-aim (that would bless the Estonia march),
and a capture from a court the capturer is not at war with is outside by
definition (the honesty counter). The ambient total excludes the PLAYER;
the per-court map keeps everyone, and the AI-France sweep's gate line
reads its France entry from the map (one instrument, two surfaces).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

from test_dy0_the_signature import _digest, _row  # noqa: E402
from tools.ai_v_sweep import (  # noqa: E402
    RunCapture,
    _variance_signature,
    derive_metrics,
)

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")


def _capture(region, by, frm):
    return {"type": "region_captured", "region": region,
            "captured_by": by, "captured_from": frm}


def _boot_war(attackers, defenders, aims, ended_turn=None):
    return {"attackers": list(attackers), "defenders": list(defenders),
            "aims": dict(aims), "ended_turn": ended_turn}


def _joined(rows, boot_wars):
    digest = _digest(rows)
    digest["boot"] = {"wars": dict(boot_wars)}
    return derive_metrics(digest)


class TestTheJoiner:
    def test_an_in_aim_capture_counts_nothing(self):
        d = _joined(
            [_row(1, events=[_capture("Munich", "Austria", "Bavaria")])],
            {"w0": _boot_war(["Austria"], ["Bavaria"],
                             {"Austria": ["Munich"]})})
        assert d["captures_outside_aim"] == 0
        assert d["captures_outside_aim_by_court"] == {}

    def test_enemy_soil_off_the_aim_counts(self):
        # The Estonia-march class: at war, capturing, but not the aim.
        d = _joined(
            [_row(1, events=[_capture("Swabia", "Austria", "Bavaria")])],
            {"w0": _boot_war(["Austria"], ["Bavaria"],
                             {"Austria": ["Munich"]})})
        assert d["captures_outside_aim"] == 1
        assert d["captures_outside_aim_by_court"] == {"Austria": 1}

    def test_a_capture_from_a_non_belligerent_counts(self):
        # The honesty counter: no war holds the prior controller.
        d = _joined(
            [_row(1, events=[_capture("Bern", "Austria", "Switzerland")])],
            {"w0": _boot_war(["Austria"], ["Bavaria"],
                             {"Austria": ["Bern"]})})
        assert d["captures_outside_aim"] == 1

    def test_the_player_is_mapped_but_not_totalled(self):
        # France idle in the ambient chains; the AI-France sweep's gate
        # line reads the map's France entry (§13.2 R2's two surfaces).
        d = _joined(
            [_row(1, events=[_capture("Flanders", "France", "Austria")])],
            {"w0": _boot_war(["France"], ["Austria"], {})})
        assert d["captures_outside_aim"] == 0
        assert d["captures_outside_aim_by_court"] == {"France": 1}

    def test_a_war_opened_on_a_row_covers_from_that_row(self):
        war = {"war_id": "w1", "attackers": ["Prussia"],
               "defenders": ["Hanover"], "ai_initiated": True,
               "stated_reason": None, "entry_path": None,
               "aims": {"Prussia": ["Hanover"]}}
        rows = [
            _row(1, events=[_capture("Hanover", "Prussia", "Hanover")]),
            _row(2, wars_opened=[war]),
            _row(3, events=[_capture("Hanover", "Prussia", "Hanover")]),
        ]
        d = _joined(rows, {})
        # The turn-1 capture precedes the war: outside (no live war).
        assert d["captures_outside_aim_by_court"] == {"Prussia": 1}

    def test_an_ended_war_stops_covering(self):
        rows = [_row(5, events=[_capture("Munich", "Austria", "Bavaria")])]
        d = _joined(rows, {"w0": _boot_war(["Austria"], ["Bavaria"],
                                           {"Austria": ["Munich"]},
                                           ended_turn=3)})
        assert d["captures_outside_aim"] == 1

    def test_the_signature_carries_the_column(self):
        digest = _digest(
            [_row(1, events=[_capture("Swabia", "Austria", "Bavaria")])])
        digest["boot"] = {"wars": {"w0": _boot_war(
            ["Austria"], ["Bavaria"], {"Austria": ["Munich"]})}}
        digest["derived"] = derive_metrics(digest)
        signature = _variance_signature(digest)
        assert signature["captures_outside_aim"] == 1


class TestTheAimReader:
    @pytest.fixture(scope="class")
    def world(self):
        from backend.models.world_state import WorldState
        return WorldState.from_scenario(str(SCENARIO), seed="historical")

    def test_the_design_arm_reads_the_overlord(self, world):
        # Austria vs France at boot: redeem_italy's Milan is the
        # Kingdom of Italy's — France's client — and the design arm
        # resolves the overlord, so Milan is Austria's aim in HER war
        # with France (R1's design arm, live).
        capture = RunCapture(world)
        boot = capture.capture_boot()
        franco_austrian = [
            war for war in boot["wars"].values()
            if {"France", "Austria"} <= (set(war["attackers"])
                                         | set(war["defenders"]))]
        assert franco_austrian, "the 1805 boot carries the coalition war"
        aims = {}
        for war in franco_austrian:
            for region in (war.get("aims") or {}).get("Austria", []):
                aims[region] = True
        assert "Milan" in aims

    def test_the_objective_record_arm_reads_target_regions(self, world):
        # A crafted objective record joins the aim-set (resolved names
        # — the council writes the design's provinces, the default road
        # the capital).
        capture = RunCapture(world)
        key = world._make_diplo_key("Austria", "France")
        world.war_objectives.setdefault(key, {})["Austria"] = {
            "target_regions": ["Vienna"]}
        for war in capture._war_summaries().values():
            party = set(war["attackers"]) | set(war["defenders"])
            if {"France", "Austria"} <= party:
                assert "Vienna" in war["aims"]["Austria"]
                break
        else:
            pytest.fail("no Franco-Austrian war at boot")


class TestTheBaseline:
    """The dated baseline `tools/_t3_march_baseline_2026_11_08.json` —
    the tier's starting DEBT, honestly nonzero (the DY-0 floor idiom:
    the gate's 0 is measured at the gate once T3-2…T3-4 land, never
    today), and the widening's innocence: minus the new column, every
    seed's signature is byte-identical to the T2-6 record's."""

    @pytest.fixture(scope="class")
    def baseline(self):
        return json.loads(
            (REPO / "tools" / "_t3_march_baseline_2026_11_08.json")
            .read_text(encoding="utf-8"))

    @pytest.fixture(scope="class")
    def t2_6(self):
        return json.loads(
            (REPO / "tools" / "_dy_signature_t2_6_2026_11_08.json")
            .read_text(encoding="utf-8"))

    def test_the_debt_is_the_record(self, baseline):
        assert baseline["ambient_total"] == 397
        totals = {seed: entry["captures_outside_aim"]
                  for seed, entry in baseline["seeds"].items()}
        assert totals == {
            "historical": 33, "austerlitz": 72, "ulm": 39, "jena": 34,
            "marengo": 22, "eylau": 35, "friedland": 32, "wagram": 31,
            "lodi": 70, "rivoli": 29,
        }

    def test_austria_is_the_chief_offender_on_every_seed(self, baseline):
        # The blob's spread captures — the finding the tier exists to
        # fix, now a number per court.
        for seed, entry in baseline["seeds"].items():
            by_court = entry["by_court"]
            assert by_court, seed
            chief = max(by_court, key=by_court.get)
            assert chief == "Austria", (seed, by_court)

    def test_the_widening_moved_no_world_line(self, baseline, t2_6):
        # The compatibility pin: strip the new column and the baseline's
        # signatures read the T2-6 record's, byte for byte.
        for seed, record in t2_6["seeds"].items():
            ours = dict(baseline["seeds"][seed]["signature"])
            ours.pop("captures_outside_aim", None)
            assert ours == record["signature"], seed
