"""S14c part 3 — the Crown of the Reich, the windows, the matrix
(`docs/EVENTS_SPEC.md` §2 M3, §3.6, §4, §5, §9 Part 3).

On the shipped 1805 boot (the whole deck armed): on a staged Road I board —
the Rhine proclaimed through its own button, three German clients held, the
Confederation fulfilled by the designs' own tick — the Reich's letter
arrives a turn after the morning that tells the fulfilment; "Demand the
abdication" raises each Confederation member that is France's vassal by 10,
costs Austria 15 goodwill and Europe's alarm 3, and Le Moniteur's next
issue carries THE EMPIRE IS NO MORE (on that answer only); on Roads II and
III the letter is forsworn. The windows' clauses A–G hold over the ten
sweep seeds.
"""
import contextlib
import copy
import io
import json
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import imperial_designs as ID
from backend.game_logic import moments as MO
from backend.models.world_state import WorldState
from tests import _chip_census as C
from tests.test_moments_engine import _at, _letter, _make_current, _rich, _tick
from tests.test_vp1_the_roads_armed import _proclaim, _vassalize

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
SWEEP_SEEDS = ["historical", "ulm", "austerlitz", "jena", "marengo",
               "eylau", "friedland", "wagram", "lodi", "rivoli"]
MEMBERS = ("Bavaria", "Hesse", "Saxony")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def client(world):
    from fastapi.testclient import TestClient
    return TestClient(M.app)


def _confederation(client, world):
    """The Rhine proclaimed through its button, three clients, the designs'
    own tick until the Confederation latches; returns the latch turn."""
    for mid in ("bavarian_match", "throne_of_holland", "decree_of_berlin"):
        world.moments["state"][mid] = {"status": "passed", "turn": 1, "reason": "premise"}
    _proclaim(client, "rhine")
    for court in MEMBERS:
        _vassalize(world, court)
    for _ in range(6):
        world.current_turn += 1
        with _quiet():
            ID.tick(world, world.current_turn)
        if ID.is_fulfilled(world, "rhine.confederation"):
            return ID.fulfilled_turn(world, "rhine.confederation")
    raise AssertionError("the Confederation never latched")


class TestTheReich:
    def test_it_arrives_a_turn_after_the_confederation_is_told(self, client, world):
        latched = _confederation(client, world)
        _at(world, latched + 1)                   # the morning that tells the fulfilment
        assert _tick(world) == []
        _at(world, latched + 2)                   # lag 1
        assert _tick(world) == ["crown_of_the_reich"]
        letter = _letter(world, "crown_of_the_reich")
        assert letter["popup_payload"]["title"] == "The Crown of the Reich"

    def test_demanding_the_abdication_applies_its_quote_and_prints_the_special(self, client, world):
        from backend.game_logic.gazette import _special_candidates
        latched = _confederation(client, world)
        _rich(world)
        _at(world, latched + 2)
        _tick(world)
        letter = _letter(world, "crown_of_the_reich")
        _make_current(world, letter)
        loyalty = {c: int(world.vassals[c]["loyalty"]) for c in MEMBERS}
        austria = int(world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0))
        alarm = int(world.threat_by_target.get("France", 0))
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue", json={
                "choice": "accept", "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert {c: int(world.vassals[c]["loyalty"]) for c in MEMBERS} == {
            c: min(100, v + 10) for c, v in loyalty.items()}
        assert int(world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0)) == max(-100, austria - 15)
        assert int(world.threat_by_target.get("France", 0)) == min(100, alarm + 3)
        answered = [e for e in world.event_log if e.get("type") == "moment" and e.get("phase") == "answered"]
        reasons = [r for _w, r, _k in _special_candidates(world, answered)]
        assert "THE EMPIRE IS NO MORE" in reasons

    def test_letting_francis_keep_his_crown_changes_nothing_and_prints_nothing(self, client, world):
        from backend.game_logic.gazette import _special_candidates
        latched = _confederation(client, world)
        _at(world, latched + 2)
        _tick(world)
        letter = _letter(world, "crown_of_the_reich")
        _make_current(world, letter)
        austria = int(world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0))
        with _quiet():
            client.post("/respond_to_diplomatic_dialogue", json={
                "choice": "reject", "dialogue_id": letter["dialogue_id"]})
        assert int(world.nation_relations.get(world._make_diplo_key("France", "Austria"), 0)) == austria
        answered = [e for e in world.event_log if e.get("type") == "moment" and e.get("phase") == "answered"]
        assert "THE EMPIRE IS NO MORE" not in [r for _w, r, _k in _special_candidates(world, answered)]

    @pytest.mark.parametrize("road", ["crowns", "system"])
    def test_on_roads_ii_and_iii_it_is_forsworn(self, world, road):
        state = ID._state(world)
        state["road"], state["proclaimed_turn"] = road, 2
        _at(world, 3)
        _tick(world)
        assert MO.status_row(world, "crown_of_the_reich")["reason"] == "forsworn"

    def test_an_austria_already_the_emperor_s_vassal_is_no_fork(self, client, world):
        latched = _confederation(client, world)
        _vassalize(world, "Austria")
        _at(world, latched + 2)
        assert _tick(world) == []                 # the premise names Austria not a vassal


class TestTheClauses:
    """§5's clauses A–G (AI_INTENT §3.8.1, amendment A3) over the sweep seeds."""

    @pytest.fixture(scope="class")
    def boots(self):
        out = {}
        with _quiet():
            for seed in SWEEP_SEEDS:
                out[seed] = WorldState.from_scenario(str(SCENARIO), seed=seed)
        return out

    def _strip(self, deck):
        return [{k: v for k, v in e.items() if k != "turn"} for e in deck]

    def test_a_the_deck_content_is_identical_on_every_seed(self, boots):
        decks = {s: self._strip(MO.deck(w)) for s, w in boots.items()}
        assert all(d == decks["historical"] for d in decks.values())

    def test_b_every_turn_lies_in_its_band_and_historical_is_the_value(self, boots):
        authored = {e["id"]: e.get("turn") for e in json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]["deck"]}
        for seed, w in boots.items():
            for e in MO.deck(w):
                band = authored[e["id"]]
                if isinstance(band, dict):
                    lo, hi = band["band"]
                    assert lo <= e["turn"] <= hi, (seed, e["id"])
                    if seed == "historical":
                        assert e["turn"] == band["value"]

    def test_c_the_unperturbed_schedule_keeps_the_gap(self, boots):
        for seed, w in boots.items():
            gap = MO.pacing(w)["min_gap"]
            windows = sorted((e["turn"], e["grace"], e["id"]) for e in MO.deck(w) if "turn" in e)
            for (t_a, g_a, a), (t_b, _g, b) in zip(windows, windows[1:]):
                assert t_a + g_a + gap <= t_b, (seed, a, b)

    def test_d_every_window_closes_before_the_verdict(self, boots):
        from backend.game_logic import game_end
        for seed, w in boots.items():
            verdict = game_end.verdict_turn(w)
            assert all(e["turn"] + e["grace"] < verdict for e in MO.deck(w) if "turn" in e), seed

    def test_e_eligibility_never_reads_the_seed(self):
        src = (REPO / "backend" / "game_logic" / "moments.py").read_text(encoding="utf-8")
        code = re.sub(r'""".*?"""', "", src, flags=re.S)
        assert "campaign_seed" not in code and "seeded_" not in code

    def test_f_the_causal_entry_never_varies(self, boots):
        assert {("turn" in MO.entry(w, "crown_of_the_reich")) for w in boots.values()} == {False}

    def test_the_band_spreads_across_the_sweep(self, boots):
        assert len({MO.entry(w, "bavarian_match")["turn"] for w in boots.values()}) > 1


class TestTheSignatureReadsTheRun:
    def test_moment_turns_ride_the_signature_from_the_run(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_sweep", REPO / "tools" / "ai_v_sweep.py")
        sweep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sweep)
        src = (REPO / "tools" / "ai_v_sweep.py").read_text(encoding="utf-8")
        body = src[src.index("def _variance_signature"):src.index("def run_arm_b")]
        assert '"moment_turns": derived.get("fire_turns", {})' in body
        assert 'digest["boot"]' not in body.split('"moment_turns"')[1].split("}")[0]
