"""SF-CL-1 "The forecast keeps its word" (SCORE_FINISH_SPEC.md §3 Step 4,
October 3, 2026; rules SYSTEMS_REFERENCE.md §86).

Across the benchmark arms, every prediction the game prints is logged beside
what the resolver then committed, and each divergence class is fixed and
pinned:

- THE INSTRUMENT: `tools/playtest_driver.py::ForecastLedger` (a Transport
  observer) writes one `forecast` jsonl row per surface — the muster's
  "expect about X … up to Y" and its band with the WILL JOIN / WILL NOT rows
  and their quoted arrival odds, an objection's message and band, a bad-odds
  interrupt's, a scout's garrison, a garrison assault's figures — beside the
  resolver's `massed_strength` (lead + committed, who fought, who did not and
  why), the casualty summary and the victor. `tools/forecast_census.py`
  reads the rows into classes.
- THE WIRE: `muster_preview` (W6-4 built it for the result and it never
  reached the API) and `massed_strength` ride the response, display-only.
- FIX 1 — THE MUSTER PRICES THE COORDINATION: the resolver stamps a
  coordination attack bonus (capped +25%) on every participant before it
  sums the committed strength, and the preview never priced it — the
  Emperor's co-located attack quoted "up to 112,775 if all march" and the
  resolver weighed 138,604. The preview now reads its expected figure, its
  ceiling, the defender's term and the odds band under the same context,
  stamped for the hypothetical "every WILL JOIN present" set and restored
  (`CombatExecutor._priced_coordination`). The mirror is exact: a lead
  attacking from next door keeps his own province's context while his
  arrivals relocate into the field and his co-located partner marches off.
- THE CENSUS over the committed exit archive: zero lies in every class; the
  shortfall class (a promised corps whose die failed) is reported beside the
  odds the row quoted.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import combat_executor as CE
from backend.models.marshal import Marshal
from tests import _chip_census as C

REPO_ROOT = Path(__file__).resolve().parents[1]
EXIT_ARMS = REPO_ROOT / "docs" / "audits" / "score_runs" / "2026_10_03_sf_cl1" / "arms"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


driver = _load("playtest_driver_for_cl1", "tools/playtest_driver.py")
census = _load("forecast_census_for_cl1", "tools/forecast_census.py")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def client(monkeypatch):
    C.board_env(monkeypatch)
    random.seed(0)
    return TestClient(M.app)


def _post(client, text):
    with _quiet():
        return client.post("/command", json={"command": text}).json()


class _StubDigest:
    def __init__(self):
        self.rows = []

    def record(self, kind, **fields):
        self.rows.append({"kind": kind, **fields})


# ════════════════════════════════════════════════════════════════════════
# THE INSTRUMENT
# ════════════════════════════════════════════════════════════════════════

class TestTheLedger:
    def test_the_band_word(self):
        f = driver._band_word
        assert f("MUSTER — Ney (24,000) vs Mack at Swabia — the balance of force looks favorable.") == "favorable"
        assert f("the balance of force looks unfavorable.") == "unfavorable"
        assert f("the balance of force looks even — a hard fight") == "even"
        assert f("Sire, the odds are unfavourable here") == "unfavorable"
        assert f("the enemy is too strong") == ""
        assert f(None) == "" and f("") == ""

    def _muster_response(self):
        return {
            "action_summary": {"turn": 4},
            "muster_preview": {
                "attacker": {"name": "Ney", "strength": 24000, "committed_strength": 85373,
                             "ceiling_strength": 96789},
                "target": {"name": "Mack", "location": "Swabia"},
                "odds_band": "favorable",
                "rows": [
                    {"marshal": "Davout", "will_join": True, "arrival_odds": 98},
                    {"marshal": "Soult", "will_join": False},
                ],
            },
            "battle_report": {"casualty_summary": {"attacker_casualties": 2157,
                                                   "defender_casualties": 17054}},
            "massed_strength": {"lead": 24000, "committed": 72789, "total": 96789,
                                "arrived": ["Davout"], "contributors": ["Davout", "Lannes"],
                                "absent": [["Soult", "literal_personality"]]},
            "battle_diorama": {"player_side": "attacker", "victor": "Ney",
                               "attacker": {"contingents": [
                                   {"name": "Ney", "lead": True, "status": "engaged"},
                                   {"name": "Davout", "lead": False, "status": "reinforced"},
                                   {"name": "Bernadotte", "lead": False, "status": "refused"},
                               ]}},
        }

    def test_a_muster_with_its_battle_is_one_row(self):
        d = _StubDigest()
        driver.ForecastLedger(d).observe("/command", {"command": "Ney, attack Mack"},
                                         self._muster_response())
        rows = [r for r in d.rows if r["kind"] == "forecast"]
        assert len(rows) == 1 and rows[0]["family"] == "muster"
        p, c = rows[0]["predicted"], rows[0]["committed"]
        assert (p["lead_name"], p["lead"], p["expected"], p["ceiling"], p["band"]) == ("Ney", 24000, 85373, 96789, "favorable")
        assert p["will_join"] == ["Davout"] and p["will_not"] == ["Soult"]
        assert p["arrival_odds"] == {"Davout": 98}
        assert c["total"] == 96789 and c["lead"] == 24000 and c["committed"] == 72789
        # arrivals + co-located contributors, deduped; the shelf from the
        # resolver's own record first, the capped diorama's shelf after
        assert c["arrived"] == ["Davout", "Lannes"]
        assert c["absent"] == [["Soult", "literal_personality"], ["Bernadotte", "refused"]]
        assert (c["own_losses"], c["enemy_losses"], c["victor"]) == (2157, 17054, "Ney")
        assert rows[0]["turn"] == 4 and rows[0]["text"] == "Ney, attack Mack"

    def test_a_muster_without_a_battle_has_no_commitment(self):
        d = _StubDigest()
        resp = self._muster_response()
        for key in ("battle_report", "massed_strength", "battle_diorama"):
            resp.pop(key)
        driver.ForecastLedger(d).observe("/command", {"command": "x"}, resp)
        assert d.rows[0]["committed"] is None

    def test_the_objection_rides_as_a_flag_with_its_detail_beside_it(self):
        d = _StubDigest()
        driver.ForecastLedger(d).observe("/command", {"command": "Massena, hold"}, {
            "action_summary": {"turn": 3},
            "pending_objection": True,
            "objection": {"marshal": "Massena", "original_order": {"action": "hold", "target": None},
                          "message": "Massena firmly objects — the balance of force looks unfavorable."},
        })
        row = d.rows[0]
        assert row["family"] == "objection" and row["marshal"] == "Massena"
        assert row["action"] == "hold" and row["band"] == "unfavorable"
        # a bare flag with nothing beside it writes no row
        d2 = _StubDigest()
        driver.ForecastLedger(d2).observe("/command", {}, {"pending_objection": True})
        assert d2.rows == []

    def test_scout_and_garrison_assault_rows(self):
        d = _StubDigest()
        led = driver.ForecastLedger(d)
        led.observe("/command", {"command": "Murat, scout Vienna"}, {
            "action_summary": {"turn": 2},
            "events": [{"type": "scout", "marshal": "Murat", "target": "Vienna",
                        "intel": {"garrison": 25000, "works_bonus": 10}}]})
        led.observe("/command", {"command": "Davout, attack Vienna"}, {
            "action_summary": {"turn": 4},
            "events": [{"type": "garrison_assault", "marshal": "Davout", "region": "Vienna",
                        "garrison_losses": 3000, "garrison_remaining": 23000,
                        "attacker_losses": 1200}]})
        scout, assault = d.rows
        assert (scout["family"], scout["region"], scout["garrison"], scout["works_bonus"]) == ("scout", "Vienna", 25000, 10)
        assert (assault["family"], assault["region"], assault["garrison_before"]) == ("garrison_assault", "Vienna", 26000)
        assert scout["seq"] < assault["seq"]

    def test_the_digest_attaches_the_ledger_under_the_lever(self):
        assert driver.THE_DIGEST_KEEPS_THE_FORECAST is True
        src = (REPO_ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert "transport.observers.append(forecast.observe)" in src
        assert "self.forecast = ForecastLedger(self) if THE_DIGEST_KEEPS_THE_FORECAST else None" in src


# ════════════════════════════════════════════════════════════════════════
# THE WIRE
# ════════════════════════════════════════════════════════════════════════

class TestTheWire:
    def test_the_allowlist_carries_both_keys(self):
        assert "muster_preview" in M._COMMAND_RESULT_SIMPLE_FIELDS
        assert "massed_strength" in M._COMMAND_RESULT_SIMPLE_FIELDS
        src = (REPO_ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        # the two hand-enumerated roads (the objection's insist and the charge)
        assert src.count('_copy_truthy_result_fields(response, result, ("muster_preview", "massed_strength"))') == 2

    def test_a_coordinated_attack_carries_its_muster_and_its_massed_strength(self, client):
        resp = _post(client, "Ney, attack Mack")
        assert resp.get("success"), resp.get("message")
        pv, ms = resp["muster_preview"], resp["massed_strength"]
        assert pv["attacker"]["name"] == "Ney" and pv["target"]["name"] == "Mack"
        assert set(ms) == {"lead", "committed", "total", "arrived", "contributors", "absent"}
        assert ms["total"] == ms["lead"] + ms["committed"]
        assert ms["lead"] == pv["attacker"]["strength"]
        promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
        assert set(ms["arrived"]) <= promised
        assert all(name in {r["marshal"] for r in pv["rows"]} for name, _ in ms["absent"])

    def test_lever_down_the_key_is_absent(self, client, monkeypatch):
        monkeypatch.setattr(CE, "THE_REPORT_NAMES_THE_MASSED_STRENGTH", False)
        resp = _post(client, "Ney, attack Mack")
        assert resp.get("battle_report") and "massed_strength" not in resp


# ════════════════════════════════════════════════════════════════════════
# FIX 1 — THE MUSTER PRICES THE COORDINATION
# ════════════════════════════════════════════════════════════════════════

def _attack_twice(client):
    """Ney (Rhineland) attacks Mack at Swabia from next door; then the Emperor,
    now co-located with four corps at Swabia, attacks Mack there."""
    first = _post(client, "Ney, attack Mack")
    assert first.get("massed_strength"), first.get("message")
    second = _post(client, "Napoleon, attack Mack")
    assert second.get("massed_strength"), second.get("message")
    return first, second


class TestTheMusterPricesTheCoordination:
    def test_the_emperors_co_located_muster_is_the_battle_to_the_man(self, client):
        """Every WILL JOIN corps stands on the field already (no arrival die):
        expected == ceiling == the resolver's massed strength. Before the fix
        the resolver weighed ~23% more than the ceiling (138,604 vs 112,775)."""
        _, second = _attack_twice(client)
        pv, ms = second["muster_preview"], second["massed_strength"]
        promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
        assert promised and promised <= set(ms["contributors"]) | set(ms["arrived"])
        assert pv["attacker"]["committed_strength"] == pv["attacker"]["ceiling_strength"] == ms["total"]

    def test_the_ceiling_bounds_the_battle_from_next_door(self, client):
        """Ney at Rhineland, Mack at Swabia: arrivals relocate into the field
        and Ney keeps his own province's context. The ceiling is the exact
        massed strength when every promised corps fought, and never below
        it."""
        first, _ = _attack_twice(client)
        pv, ms = first["muster_preview"], first["massed_strength"]
        promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
        fought = set(ms["arrived"]) | set(ms["contributors"])
        assert ms["total"] <= pv["attacker"]["ceiling_strength"]
        if promised <= fought:
            assert ms["total"] == pv["attacker"]["ceiling_strength"]
        else:
            assert ms["total"] < pv["attacker"]["ceiling_strength"]

    def test_lever_down_reproduces_the_divergence(self, client, monkeypatch):
        monkeypatch.setattr(CE, "THE_MUSTER_PRICES_THE_COORDINATION", False)
        _, second = _attack_twice(client)
        pv, ms = second["muster_preview"], second["massed_strength"]
        # the pre-fix preview: the resolver's coordination (+25% capped on a
        # four-corps field) never priced — the battle exceeds the ceiling
        assert ms["total"] > pv["attacker"]["ceiling_strength"] * 1.15

    def test_the_transients_are_restored(self, client):
        """A value that EXISTED before the read comes back exactly (a fresh
        boot carries none of these attributes, where deletion alone would
        pass for a restore — so one is planted first), and inside the read
        the context is genuinely stamped."""
        world = M.world
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        fields = tuple(Marshal.COORDINATION_TRANSIENT_FIELDS) + ("sovereign_presence",)
        ney.total_coordination_attack_bonus = 0.07
        ney.sovereign_presence = 0.33
        before = {m.name: {f: getattr(m, f, None) for f in fields} for m in world.marshals.values()}
        preview = combat._build_muster_preview(ney, mack, world, {"world": world})
        assert preview and preview["attacker"]["ceiling_strength"] >= preview["attacker"]["committed_strength"]
        after = {m.name: {f: getattr(m, f, None) for f in fields} for m in world.marshals.values()}
        assert after == before
        assert ney.total_coordination_attack_bonus == 0.07 and ney.sovereign_presence == 0.33
        joiners = [world.marshals[r["marshal"]] for r in preview["rows"] if r["will_join"]]
        with combat._priced_coordination(ney, joiners, mack, [], world, mack.location):
            assert ney.total_coordination_attack_bonus != 0.07, "the context was never stamped"
        assert ney.total_coordination_attack_bonus == 0.07

    def test_assume_present_and_absent(self, client):
        world = M.world
        combat = M.executor._combat
        ney = world.marshals["Ney"]
        murat = world.marshals["Murat"]
        base = combat._count_unit_types(ney.location, "France", world)
        with_cav = combat._count_unit_types(ney.location, "France", world, assume_present=[murat])
        assert murat.cavalry and murat.location != ney.location
        assert with_cav >= base and with_cav >= 2
        davout = world.marshals["Davout"]
        assert davout.location == ney.location
        everyone = [m.name for m in world.marshals.values()
                    if m.nation == "France" and m.location == ney.location]
        assert base >= 1
        assert combat._count_unit_types(ney.location, "France", world, assume_absent=everyone) == 0
        assert combat._count_unit_types(ney.location, "France", world, assume_absent=[davout.name]) <= base

    def test_the_mirror_follows_the_resolver_on_both_roads(self, client, monkeypatch):
        """`_priced_coordination` assumes a joiner present only where the
        resolver will find him — in the lead's region when that IS the
        field — and marks the co-located partner gone when the field is next
        door.

        §6 row 16 (Score Finish Step 7, October 4, 2026) — CONSCIOUSLY
        RE-PINNED: the resolver reads the lead's context on the FIELD now, so
        Davout, marching from Ney's side to Swabia, stands beside him there
        and the mirror prices him (per-ally coordination > 0). Lever down
        keeps the old reading — he marches off and is gone from Ney's."""
        world = M.world
        combat = M.executor._combat
        ney, mack, davout = world.marshals["Ney"], world.marshals["Mack"], world.marshals["Davout"]
        assert ney.location != mack.location and davout.location == ney.location
        with combat._priced_coordination(ney, [davout], mack, [], world, mack.location):
            # Davout stands beside Ney on the field: his coordination counts
            assert getattr(ney, "_display_coordination_atk", 0.0) > 0.0
        monkeypatch.setattr(CE, "THE_COORDINATION_IS_READ_ON_THE_FIELD", False)
        with combat._priced_coordination(ney, [davout], mack, [], world, mack.location):
            # lever down: Davout marches off: no per-ally coordination for Ney
            assert getattr(ney, "_display_coordination_atk", 0.0) == 0.0
        monkeypatch.setattr(CE, "THE_COORDINATION_IS_READ_ON_THE_FIELD", True)
        # Napoleon's field: Mack and the lead share the province
        nap = world.marshals["Napoleon"]
        nap.location = mack.location
        world.invalidate_bloc_members_cache()
        with combat._priced_coordination(nap, [davout], mack, [], world, mack.location):
            assert getattr(davout, "total_coordination_attack_bonus", 0.0) > 0.0
        assert getattr(davout, "total_coordination_attack_bonus", 0.0) == 0.0


# ════════════════════════════════════════════════════════════════════════
# THE CENSUS
# ════════════════════════════════════════════════════════════════════════

def _write_arm(tmp_path, arm, rows):
    d = tmp_path / arm
    d.mkdir()
    (d / "digest.jsonl").write_text(
        "".join(json.dumps({"kind": "forecast", **r}) + "\n" for r in rows), encoding="utf-8")


def _muster(seq, turn, lead, target, expected, ceiling, band, will_join, will_not, total,
            arrived, absent=(), own=1, enemy=2, odds=None):
    return {"seq": seq, "family": "muster", "turn": turn,
            "predicted": {"lead_name": lead, "lead": 10000, "expected": expected, "ceiling": ceiling,
                          "band": band, "target": target, "will_join": will_join, "will_not": will_not,
                          "arrival_odds": odds or {}},
            "committed": {"total": total, "lead": 10000, "committed": total - 10000,
                          "arrived": list(arrived), "absent": [list(a) for a in absent],
                          "own_losses": own, "enemy_losses": enemy, "victor": lead}}


class TestTheCensus:
    def test_a_lie_and_a_die_are_different_classes(self, tmp_path):
        _write_arm(tmp_path, "A", [
            _muster(1, 1, "Ney", "Mack", 80000, 90000, "favorable", ["Davout"], [], 120000, ["Davout"]),
            _muster(2, 2, "Ney", "Mack", 80000, 90000, "favorable", ["Davout", "Murat"], [], 50000,
                    ["Davout"], absent=[("Murat", "low_score")], odds={"Davout": 98, "Murat": 60}),
            _muster(3, 3, "Ney", "Mack", 80000, 90000, "favorable", ["Davout"], ["Soult"], 85000,
                    ["Davout", "Soult"]),
        ])
        out = census.census(tmp_path, regen_per_turn=0)
        assert [e["where"] for e in out["expected_miss"]] == ["A t1 Ney→Mack"]
        assert [e["where"] for e in out["shortfall_from_absences"]] == ["A t2 Ney→Mack"]
        assert out["shortfall_from_absences"][0]["quoted_odds"] == {"Murat": 60}
        assert [e["marshal"] for e in out["unpromised_arrival"]] == ["Soult"]
        assert out["promise_rate"][0] == round(3 / 4, 3)

    def test_the_band_pairs_with_the_muster_that_followed(self, tmp_path):
        _write_arm(tmp_path, "A", [
            {"seq": 1, "family": "objection", "turn": 5, "marshal": "Davout", "target": "Mack",
             "band": "unfavorable", "message": "x"},
            _muster(2, 5, "Davout", "Mack", 50000, 50000, "favorable", [], [], 10000, []),
            {"seq": 3, "family": "interrupt", "turn": 6, "marshal": "Ney", "target": "Mack",
             "band": "unfavorable", "message": "x"},
            _muster(4, 6, "Ney", "Mack", 50000, 50000, "unfavorable", [], [], 10000, []),
            # a muster that PRECEDED the judgement in its turn is not its answer
            _muster(5, 7, "Murat", "Mack", 50000, 50000, "favorable", [], [], 10000, []),
            {"seq": 6, "family": "objection", "turn": 7, "marshal": "Murat", "target": "Mack",
             "band": "unfavorable", "message": "x"},
        ])
        out = census.census(tmp_path, regen_per_turn=0)
        assert [(e["family"], e["said"], e["muster"]) for e in out["band_disagreement"]] == [
            ("objection", "unfavorable", "favorable")]
        assert all(e["where"].startswith("A t5") for e in out["band_disagreement"])

    def test_the_scout_is_read_against_the_assault_with_regen(self, tmp_path):
        _write_arm(tmp_path, "A", [
            {"seq": 1, "family": "scout", "turn": 2, "region": "Vienna", "garrison": 20000},
            {"seq": 2, "family": "garrison_assault", "turn": 4, "region": "Vienna", "garrison_before": 23000},
            {"seq": 3, "family": "scout", "turn": 6, "region": "Berlin", "garrison": 20000},
            {"seq": 4, "family": "garrison_assault", "turn": 7, "region": "Berlin", "garrison_before": 30000},
        ])
        out = census.census(tmp_path, regen_per_turn=1500)
        assert [e["where"] for e in out["scout_vs_assault"]] == ["A t6→t7 Berlin"]

    def test_the_exit_archive_reads_clean(self):
        """The committed exit arms (CMD-H / CMD-A / CMD-M / OP / FLD / DL):
        every lie class is empty; the die class carries its quoted odds."""
        assert EXIT_ARMS.is_dir(), EXIT_ARMS
        from backend.models.world_state import CAPITAL_GARRISON_REGEN_PER_TURN
        out = census.census(EXIT_ARMS, regen_per_turn=int(CAPITAL_GARRISON_REGEN_PER_TURN))
        assert out["by_family"].get("muster", 0) >= 15, out["by_family"]
        for key in ("expected_miss", "solo_mismatch", "unpromised_arrival",
                    "band_disagreement", "scout_vs_assault"):
            assert out[key] == [], (key, out[key])
        rate, arrived, promised = out["promise_rate"]
        assert promised >= 20 and rate >= 0.7, out["promise_rate"]
        for entry in out["shortfall_from_absences"]:
            assert entry["absent"] and entry["quoted_odds"], entry
