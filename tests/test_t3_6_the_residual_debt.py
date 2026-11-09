"""T3-6 — occupation is not annexation (`DYNAMISM_SPEC.md` §8 row T3-6, the
residual debt ruled November 9, 2026 by the user's "make best call, best
design not easiest"; `AI_INTENT_SPEC.md` §13.2's gate amended, §13.3's
addendum; the rules `SYSTEMS_REFERENCE.md` §198).

* THE HANDBACK (`game_end.aim_evacuations`, inside the ONE titling pass
  every signed peace runs, seam `a_peace_evacuates_what_it_does_not_cede`):
  at a peace between AI courts the winner keeps what the treaty cedes and
  what it may keep (`war_council.keepable_regions` — its house's authored
  aims and its declared articles) and hands the rest of the loser's
  homeland back. Armies still occupy what they enter during the war; the
  player's peaces keep SR-1a whole; a corps left standing walks home by the
  Road Home's corridor (opened at the same setter, after the pass).
* THE GATE'S READ (`war_council.annexations_outside_aim`, recorded by the
  instrument at the run's end): provinces a court KEEPS by right outside
  its authored aims — a retention or a settled conquest; never a treaty
  article, a homeland or a liberation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import game_end as GE  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")
T3_6_DOWN = T3_SEAMS_BY_ROW["T3-6"]


@pytest.fixture()
def world():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO), seed="historical")


def _fresh(world) -> None:
    world._agenda_cache = None
    world.invalidate_active_nations_cache()


def _score(world, nation: str, enemy: str, value: int) -> None:
    key = world._make_diplo_key(nation, enemy)
    world.war_scores[key] = value if key.split("|")[0] == nation else -value


def _austria_holds(world, regions) -> None:
    for region_name in regions:
        world.regions[region_name].controller = "Austria"
    _fresh(world)
    _score(world, "Austria", "Bavaria", 60)
    world.current_turn = 8


def _garrison(world, region_name: str) -> None:
    """An Austrian corps standing on the province: army-held ground is what
    the unheld-homeland return (PC15-D4) keeps, so only the handback can
    send it home — the rule isolated."""
    staged = {"Munich", "Swabia", "Franconia"}   # Mack boots at Ulm, in Swabia
    marshal = next(m for m in world.marshals.values()
                   if m.nation == "Austria" and m.strength > 0
                   and m.location not in staged)
    marshal.location = region_name


def _pair_exit(world):
    key = world._make_diplo_key("Austria", "Bavaria")
    inst = next(i for i in world.war_instances.values()
                if key in (i.get("active_diplo_keys") or []))
    events = []
    TP._process_exhausted_pair_exits(world, inst["war_id"], inst, events)
    return events


class TestTheHandback:
    def test_the_keepable_set_is_the_authored_aim(self, world):
        bavaria = set(world.nation_starting_regions["Bavaria"])
        assert WC.keepable_regions(world, "Austria", "Bavaria") & bavaria == {"Munich", "Swabia"}

    def test_an_ai_peace_hands_back_what_it_does_not_keep(self, world):
        # Austria broken-for Bavaria at +60, holding Munich and Swabia (her
        # Primacy in Germany) and Franconia (no aim of hers): Franconia goes
        # home at the signature; Swabia, in the aim, is retained.
        _austria_holds(world, ("Munich", "Swabia", "Franconia"))
        _garrison(world, "Franconia")
        events = _pair_exit(world)
        assert events and events[0]["exit"] == "sub_pair_loser_sues"
        assert world.regions["Franconia"].controller == "Bavaria"
        assert world.regions["Swabia"].controller == "Austria"
        assert world.province_title["Swabia"].get("retained")
        assert "Austria evacuates Franconia." in events[0]["consequence"]

    def test_a_declared_article_is_kept(self, world):
        key = world._make_diplo_key("Austria", "Bavaria")
        world.war_objectives[key]["Austria"]["declared_terms"] = [
            {"kind": "province", "from": "Bavaria", "region": "Franconia"}]
        assert "Franconia" in WC.keepable_regions(world, "Austria", "Bavaria")
        _austria_holds(world, ("Swabia", "Franconia"))
        _garrison(world, "Franconia")
        _pair_exit(world)
        assert world.regions["Franconia"].controller == "Austria"

    def test_a_signed_title_is_never_touched(self, world):
        _austria_holds(world, ("Swabia", "Franconia"))
        GE.record_province_title(world, "Franconia", GE.TITLE_TREATY, "Bavaria", "Austria")
        _garrison(world, "Franconia")
        _pair_exit(world)
        assert world.regions["Franconia"].controller == "Austria"

    def test_a_corps_left_standing_gets_the_road_home(self, world):
        _austria_holds(world, ("Swabia", "Franconia"))
        _garrison(world, "Franconia")
        _pair_exit(world)
        assert world.regions["Franconia"].controller == "Bavaria"
        key = world._make_diplo_key("Austria", "Bavaria")
        assert int((world.evacuation_grants or {}).get(key, 0) or 0) > int(world.current_turn)

    def test_the_players_house_keeps_sr_1a(self, world):
        kept = {"Austria": ["Franconia"]}
        assert GE.aim_evacuations(world, "Austria", "France", "Austria", "France",
                                  kept) == (kept, {})
        assert GE.aim_evacuations(world, "Austria", "KingdomOfItaly", "Austria",
                                  "KingdomOfItaly", kept) == (kept, {})

    def test_the_seam_down_restores_retention(self, world, monkeypatch):
        hold_down(monkeypatch, T3_6_DOWN)
        _austria_holds(world, ("Swabia", "Franconia"))
        _garrison(world, "Franconia")
        events = _pair_exit(world)
        assert world.regions["Franconia"].controller == "Austria"
        assert "evacuates" not in events[0]["consequence"]


class TestTheGatesRead:
    def test_a_retention_outside_the_aim_counts(self, world):
        world.regions["Franconia"].controller = "Austria"
        GE.record_province_title(world, "Franconia", GE.TITLE_TREATY, "Bavaria",
                                 "Austria", retained=True)
        _fresh(world)
        assert WC.annexations_outside_aim(world).get("Austria") == ["Franconia"]

    def test_a_settled_conquest_outside_the_aim_counts(self, world):
        world.regions["Franconia"].controller = "Austria"
        GE.record_province_title(world, "Franconia", GE.TITLE_CONQUEST, "Bavaria", "Austria")
        world.province_title["Franconia"]["since"] = int(world.current_turn) - 20
        _fresh(world)
        assert WC.annexations_outside_aim(world).get("Austria") == ["Franconia"]

    def test_an_unsettled_conquest_is_occupation(self, world):
        world.regions["Franconia"].controller = "Austria"
        GE.record_province_title(world, "Franconia", GE.TITLE_CONQUEST, "Bavaria", "Austria")
        _fresh(world)
        assert "Austria" not in WC.annexations_outside_aim(world)

    def test_a_treaty_article_and_the_aim_do_not_count(self, world):
        for region_name, retained in (("Franconia", False), ("Swabia", True)):
            world.regions[region_name].controller = "Austria"
            GE.record_province_title(world, region_name, GE.TITLE_TREATY, "Bavaria",
                                     "Austria", retained=retained)
        _fresh(world)
        assert "Austria" not in WC.annexations_outside_aim(world)

    def test_the_boot_annexes_nothing(self, world):
        assert WC.annexations_outside_aim(world) == {}

    def test_the_instrument_reads_it_and_excludes_the_player(self):
        from tests.test_dy0_the_signature import _digest, _row
        from tools.ai_v_sweep import _variance_signature, derive_metrics
        digest = _digest([_row(1)])
        digest["final"]["annexations_outside_aim"] = {
            "Austria": ["Franconia"], "France": ["Estonia", "Lithuania"]}
        digest["derived"] = derive_metrics(digest)
        assert digest["derived"]["annexations_outside_aim"] == 1
        assert digest["derived"]["annexations_outside_aim_by_court"] == {
            "Austria": 1, "France": 2}
        assert _variance_signature(digest)["annexations_outside_aim"] == 1

    def test_the_story_class_never_reads_it(self):
        from tests.test_dy0_the_signature import _digest, _row
        from tools.ai_v_sweep import derive_metrics, story_class
        a = _digest([_row(1)])
        b = _digest([_row(1)])
        b["final"]["annexations_outside_aim"] = {"Austria": ["Franconia"]}
        for d in (a, b):
            d["derived"] = derive_metrics(d)
        assert story_class(a) == story_class(b)


def _record(name: str) -> dict:
    import json
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


class TestTheMeasure:
    """Three chains on the final tree, each run ALONE (`tools/_t3_4_measure.py`
    twice — the control with the T3-6 seam held down through
    `INK_IRON_SEAMS`, then the final — and `tools/_t3_5_chain_d.py --arms D`).
    Seeded paths, not laws."""

    CONTROL = "_dy_signature_t3_6_control_2026_11_09.json"
    FINAL = "_dy_signature_t3_6_2026_11_09.json"
    CENSUS = "_t3_6_census_2026_11_09.json"
    CENSUS_CONTROL = "_t3_6_control_census_2026_11_09.json"
    CHAIN_D = "_t3_6_chain_d_2026_11_09.json"

    def test_the_control_is_t3_5s_chain_c_plus_the_column(self):
        control, chain_c = _record(self.CONTROL), _record("_dy_signature_t3_5_chain_c_2026_11_09.json")
        for seed, row in chain_c["seeds"].items():
            bare = {k: v for k, v in control["seeds"][seed]["signature"].items()
                    if k != "annexations_outside_aim"}
            assert bare == row["signature"], seed
            assert control["seeds"][seed]["story_class"] == row["story_class"], seed
        assert _record(self.CENSUS_CONTROL)["totals"]["annexations_outside_aim"] == 42

    def test_the_handback_cuts_the_kept_debt_42_to_7(self):
        census = _record(self.CENSUS)
        assert census["totals"]["annexations_outside_aim"] == 7
        final = _record(self.FINAL)
        for seed, row in census["seeds"].items():
            if seed in ("austerlitz", "lodi", "ulm"):
                assert row["annexations_outside_aim_by_court"] == {}, seed
                continue
            # the residual, every one: Franconia, the spoils of Bavaria's
            # elimination — no peace ever signed to hand it back (Tier 4's)
            assert row["annexations_outside_aim_by_court"] == {"Austria": ["Franconia"]}, seed
            assert any(e[1] == "Bavaria" for e in final["seeds"][seed]["signature"]["eliminations"]), seed

    def test_every_hanover_peace_hands_ground_back(self):
        census = _record(self.CENSUS)
        assert census["totals"]["evacuations"] == 15
        for seed, row in census["seeds"].items():
            words = [e["consequence"] for e in row["evacuations"]
                     if e["proposer"] == "Hanover" and e["accepter"] == "Prussia"]
            assert len(words) == 1, seed
            expected = ("Prussia evacuates Brunswick, Oldenburg, Osnabruck and Westphalia."
                        if seed == "historical" else "Prussia evacuates Brunswick and Oldenburg.")
            assert expected in words[0], seed

    def test_four_world_lines_move_and_the_classes_hold(self):
        control, final = _record(self.CONTROL), _record(self.FINAL)

        def bare(row):
            return {k: v for k, v in row["signature"].items() if k != "annexations_outside_aim"}
        movers = {s for s in control["seeds"] if bare(control["seeds"][s]) != bare(final["seeds"][s])}
        assert movers == {"austerlitz", "lodi", "marengo", "ulm"}
        assert final["story_class_count"] == control["story_class_count"] == 8
        marengo = final["seeds"]["marengo"]["signature"]["eliminations"]
        assert [23, "Hanover"] not in marengo and [6, "Bavaria"] in marengo
        assert final["seeds"]["austerlitz"]["signature"]["eliminations"] == [[10, "KingdomOfItaly"]]

    def test_the_ai_france_harness_ai_courts_keep_eight(self):
        record = _record(self.CHAIN_D)
        arm = record["arms"]["D"]
        assert record["totals"]["D"]["annexations_outside_aim"] == 8
        assert {s: r["annexations_outside_aim"] for s, r in arm.items()} == {
            "austerlitz": 0, "eylau": 1, "friedland": 2, "historical": 0, "jena": 5,
            "lodi": 0, "marengo": 0, "rivoli": 0, "ulm": 0, "wagram": 0}
        # France's own entry is REPORTED, never gated: an AI-run France signs
        # peace under the human's rule (SR-1a) and has no authored aim.
        assert all("France" in r["annexations_outside_aim_by_court"] for r in arm.values())
