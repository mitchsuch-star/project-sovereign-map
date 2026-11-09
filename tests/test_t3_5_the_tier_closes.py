"""T3-5 — Tier 3 closes (`AI_INTENT_SPEC.md` §13.2 R6 and the landing
record §13.3; `DYNAMISM_SPEC.md` §2 Tier 3 + §8 row T3-5; November 9,
2026; the rules `SYSTEMS_REFERENCE.md` §197).

Two changes, then the tier's two closing chains:

* THE TERMS MADE CONSISTENT (the user's "do what's best", under T3-4's
  seam `a_held_aim_sues`): the victor's LENIENT aim peace is taken only
  while the loser still stands near its breaking point (`line <= score <=
  line + AIM_TERMS_BAND`); a BROKEN loser sues on its own road and pays
  the war's indemnity as it always has — and every peace that ends a war
  whose victor holds its aim now signs the aim's provinces over by name
  (`held_aim_lock`: the loser's suit and the broker road through
  `build_third_party_terms`, the loser-sues and the mutual-exhaustion pair
  exits). Before, the lenient offer ran first and pre-empted a broken
  loser's own surrender the same turn.
* THE CONDUCT RULE BINDS THE HARNESS FRANCE (seam
  `the_conduct_binds_every_runner`): an AI-run France is bound as every
  court; a marshal under the player's independent command stays exempt
  (`EnemyAI.decide_single_action`, the one human road through the AI's
  rungs — found while planning, the plan's "nothing in real play" read
  corrected before a line was built).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import settlement_third_party as TP  # noqa: E402
from backend.game_logic import war_council as WC  # noqa: E402
from tests._t3_seams import T3_SEAMS_BY_ROW, hold_down  # noqa: E402

SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets"
            / "maps" / "europe_1805.json")


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


def _tyrol(world, score: int) -> None:
    world.regions["Tyrol"].controller = "Bavaria"
    _fresh(world)
    _score(world, "Bavaria", "Austria", score)
    world.current_turn = 6


def _pair_exit(world):
    key = world._make_diplo_key("Austria", "Bavaria")
    inst = next(i for i in world.war_instances.values()
                if key in (i.get("active_diplo_keys") or []))
    events = []
    TP._process_exhausted_pair_exits(world, inst["war_id"], inst, events)
    return events


def _scania_war(world, score: int):
    from backend.game_logic.diplomacy import declare_war
    result = declare_war(world, "Denmark", "Sweden", war_objective="conquest")
    war = world.war_instances[result["war_id"]]
    world.regions["Scania"].controller = "Denmark"
    _fresh(world)
    _score(world, "Denmark", "Sweden", score)
    world.current_turn = int(war.get("created_turn", 1)) + 4
    return result["war_id"], war


class TestTheTermsMadeConsistent:
    def test_the_band_sits_above_the_line(self, world, monkeypatch):
        _tyrol(world, 30)
        monkeypatch.setattr(AD, "effective_peace_threshold", lambda *a, **k: -40)
        for loser_score, signs in ((-24, False), (-25, True), (-40, True), (-41, False)):
            _score(world, "Bavaria", "Austria", -loser_score)
            assert TP.aim_terms_signable(world, "Austria", "Bavaria") is signs, loser_score

    def test_a_broken_loser_sues_and_the_aim_is_locked(self, world):
        # Austria past her line: the lenient exit declines, her own suit
        # ends the pair — and the Tyrol is signed over by treaty.
        _tyrol(world, 60)
        assert not TP.aim_terms_signable(world, "Austria", "Bavaria")
        events = _pair_exit(world)
        assert len(events) == 1
        event = events[0]
        assert event["exit"] == "sub_pair_loser_sues"
        assert (event["proposer"], event["accepter"]) == ("Austria", "Bavaria")
        assert event["consequence"].endswith("Bavaria keeps Tyrol by treaty.")
        title = world.province_title["Tyrol"]
        assert title["kind"] == "treaty" and not title.get("retained")

    def test_a_standing_loser_takes_the_lenient_peace(self, world):
        _tyrol(world, 40)
        events = _pair_exit(world)
        assert events and events[0]["exit"] == "aim_held_sue"

    def test_the_broken_losers_suit_pays_and_signs(self, world):
        # The AI-only war: Sweden broken at −50 sues — the indemnity (clamped
        # to her chest at the signing) AND Scania by name.
        war_id, war = _scania_war(world, 50)
        assert not TP.aim_terms_signable(world, "Sweden", "Denmark")
        chest = int(world.nation_gold.get("Sweden", 0))
        events = [e for e in TP.process_third_party_settlements(world)
                  if e.get("war_id") == war_id]
        assert len(events) == 1
        event = events[0]
        assert "exit" not in event
        assert (event["proposer"], event["accepter"]) == ("Sweden", "Denmark")
        kinds = {t["type"] for t in event["terms"]}
        assert kinds == {"gold_indemnity", "territory_cede"}
        assert int(world.nation_gold.get("Sweden", 0)) < chest
        assert world.province_title["Scania"]["kind"] == "treaty"

    def test_the_lock_never_names_ground_the_winner_lacks(self, world):
        war_id, war = _scania_war(world, 50)
        world.regions["Scania"].controller = "Sweden"
        _fresh(world)
        assert TP.held_aim_lock(world, "Denmark", "Sweden") == []

    def test_a_white_peace_locks_a_held_aim(self, world, monkeypatch):
        # Both courts spent, the score stagnant: the white peace still signs
        # the aim held over.
        _tyrol(world, 5)
        monkeypatch.setattr(TP, "pair_is_mutually_exhausted",
                            lambda w, a, b, j: {a, b} == {"Austria", "Bavaria"})
        events = _pair_exit(world)
        assert events and events[0]["exit"] == "mutual_exhaustion"
        assert {events[0]["proposer"], events[0]["accepter"]} == {"Austria", "Bavaria"}
        assert events[0]["consequence"].endswith("Bavaria keeps Tyrol by treaty.")
        assert world.province_title["Tyrol"]["kind"] == "treaty"

    def test_the_seam_down_restores_the_old_roads(self, world, monkeypatch):
        # The old road: no lock — and the lightly held Tyrol (no Bavarian
        # marshal stands there) goes home with the unheld homeland, the very
        # re-entry landmine the lock removes.
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T3-4"])
        _tyrol(world, 60)
        events = _pair_exit(world)
        assert events and events[0]["exit"] == "sub_pair_loser_sues"
        assert "keeps Tyrol by treaty" not in events[0]["consequence"]
        assert world.regions["Tyrol"].controller == "Austria"


class TestTheHarnessFranceIsBound:
    def _french_marshal(self, world):
        return next(m for m in world.marshals.values() if m.nation == "France")

    def test_an_ai_run_france_keeps_the_conduct(self, world):
        marshal = self._french_marshal(world)
        assert not WC.annexation_permitted(world, "France", "Bohemia", marshal=marshal)
        assert WC.annexation_permitted(world, "France", "Vienna", marshal=marshal)

    def test_independent_command_stays_the_players(self, world):
        marshal = self._french_marshal(world)
        marshal.autonomous = True
        assert WC.annexation_permitted(world, "France", "Bohemia", marshal=marshal)

    def test_a_read_without_its_corps_keeps_the_t3_3_reading(self, world):
        assert WC.annexation_permitted(world, "France", "Bohemia")

    def test_the_seam_down_restores_the_exemption(self, world, monkeypatch):
        hold_down(monkeypatch, T3_SEAMS_BY_ROW["T3-5"])
        marshal = self._french_marshal(world)
        assert WC.annexation_permitted(world, "France", "Bohemia", marshal=marshal)

    def test_the_rungs_pass_their_marshal(self):
        src = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert src.count("annexation_permitted(world, nation, adj_name, marshal=marshal)") == 2
        assert "annexation_permitted(world, nation, adj_name)" not in src

    def test_the_sweep_child_reads_the_seam_channel(self):
        src = (REPO / "tools" / "ai_france_sweep.py").read_text(encoding="utf-8")
        body = src.split("def run_one(", 1)[1].split("\ndef ", 1)[0]
        assert "apply_from_env()" in body


def _record(name: str) -> dict:
    import json
    return json.loads((REPO / "tools" / name).read_text(encoding="utf-8"))


class TestTheMeasure:
    """Tier 3's two closing chains (§13.2 R6), each run ALONE on the final
    tree: chain C (`tools/_t3_4_measure.py`) and chain D
    (`tools/_t3_5_chain_d.py`, two arms). Seeded paths, not laws."""

    CHAIN_C = "_dy_signature_t3_5_chain_c_2026_11_09.json"
    CENSUS = "_t3_5_chain_c_census_2026_11_09.json"
    CHAIN_D = "_t3_5_chain_d_2026_11_09.json"
    LOCK_TURNS = {"austerlitz": 17, "eylau": 22, "friedland": 17, "historical": 16,
                  "jena": 14, "lodi": 21, "marengo": 15, "rivoli": 22, "ulm": 18,
                  "wagram": 16}

    def test_chain_c_is_t3_3s_world_lines_byte_for_byte(self):
        chain_c, t33 = _record(self.CHAIN_C), _record("_dy_signature_t3_3_2026_11_08.json")
        assert set(chain_c["seeds"]) == set(t33["seeds"])
        for seed in t33["seeds"]:
            assert chain_c["seeds"][seed] == t33["seeds"][seed], seed
        assert chain_c["story_class_count"] == 8

    def test_the_fix_removes_t3_4s_purse_butterfly(self):
        chain_c, t34 = _record(self.CHAIN_C), _record("_dy_signature_t3_4_2026_11_09.json")
        movers = {seed for seed in t34["seeds"]
                  if t34["seeds"][seed]["signature"] != chain_c["seeds"][seed]["signature"]}
        assert movers == {"austerlitz", "marengo"}
        assert [23, "Hanover"] in chain_c["seeds"]["marengo"]["signature"]["eliminations"]

    def test_the_lock_signs_on_every_seed(self):
        census = _record(self.CENSUS)
        assert census["totals"] == {"aim_letters": 2, "aim_peaces": 0,
                                    "captures_outside_aim": 208, "signed_cessions": 10}
        for seed, turn in self.LOCK_TURNS.items():
            rows = census["seeds"][seed]["signed_cessions"]
            assert len(rows) == 1, seed
            row = rows[0]
            assert (row["turn"], row["proposer"], row["accepter"], row["exit"]) == (
                turn, "Hanover", "Prussia", ""), seed
            assert row["consequence"].startswith("Prussia takes Hanover. Hanover pays "), seed

    def test_the_tier_against_t2_6(self):
        # Tier 3's whole effect, the debt column (born at T3-1) set aside.
        chain_c, t26 = _record(self.CHAIN_C), _record("_dy_signature_t2_6_2026_11_08.json")

        def bare(row):
            return {k: v for k, v in row["signature"].items() if k != "captures_outside_aim"}
        moved = {seed for seed in t26["seeds"]
                 if bare(t26["seeds"][seed]) != bare(chain_c["seeds"][seed])}
        assert moved == set(t26["seeds"]) - {"marengo"}
        assert (t26["story_class_count"], chain_c["story_class_count"]) == (10, 8)

    def test_chain_d_the_harness_france_bound(self):
        record = _record(self.CHAIN_D)
        assert record["totals"]["D0"]["france_outside_aim"] == 245
        assert record["totals"]["D"]["france_outside_aim"] == 194
        france = {seed: row["france_outside_aim"] for seed, row in record["arms"]["D"].items()}
        assert france == {"austerlitz": 26, "eylau": 19, "friedland": 22, "historical": 15,
                          "jena": 15, "lodi": 22, "marengo": 25, "rivoli": 20, "ulm": 15,
                          "wagram": 15}

    def test_chain_d_the_estonia_road_still_taken(self):
        # The review's march persists in both arms: the road to St. Petersburg
        # (a permitted seat) falls as France's columns enter it — the
        # residual row T3-6 owns.
        record = _record(self.CHAIN_D)
        for arm in ("D0", "D"):
            for seed, row in record["arms"][arm].items():
                taken = {capture[1] for capture in row["france_captures"]}
                assert "Estonia" in taken, (arm, seed)
