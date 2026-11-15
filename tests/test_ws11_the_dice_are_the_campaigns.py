"""WS-11 (row BA, BA-1) — the battle's dice are the campaign's.

The user's ruling of November 14, 2026: "Seed them here, first"
(`docs/BATTLE_DIORAMA_SPEC.md` §15.2 row 5, §15.5.1; `docs/BUG_FIXES.md` §WS
row WS-11).

Before: every draw on the land-battle road came off the module `random`,
which no save carries — save, attack, load, attack again rolled a new battle.
Now a battle in a campaign the game SERVER holds, on a ROLLED campaign seed,
draws from a private stream keyed on the seed and the battle's own identity,
so the same save fights the same battle. Two things did not move:

* the `historical` seed (the whole suite's pin): the stream is None, every
  draw stays on the module `random`, and every call keeps the shape it had;
* a world nobody serves — the measuring tools build their own
  (`WorldState.from_scenario` and a `TurnManager` loop under their own
  `random.seed(...)`), on named seeds: they keep the stream they pin, so the
  recorded series stand (the gate's word: "the test suite and the measured
  series do not move"; `tests/test_sf_lb2_the_defenceless_prize.py`'s driven
  board on austerlitz is the pin that caught it).

One thing DID move, and the gate's word was wrong about it: a tool that plays
THROUGH the server on a named seed is a campaign the server holds. The
playtest driver posts `/new_game`, so its `--seed` arms — the commanded arms
on austerlitz and marengo, the sign-ability sweep's seeds — fight the
campaign's dice as a player does. The deploy gate's France band is read off
those arms: `TestTheBandOnTheCommandedArms` holds its re-measure
(`tools/_ba1_band_2026_11_14.json`).
"""

import ast
import inspect
import json
import random
from pathlib import Path

import pytest

from backend.commands import combat_executor as CE
from backend.commands.executor import CommandExecutor
from backend.game_logic import campaign_variance as cv
from backend.game_logic.combat import CombatResolver
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

ROLLED = "iron-eagle-07"


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _mk(name, location, strength, nation="France", personality="cautious", **kw):
    return Marshal(
        name=name, location=location, strength=int(strength),
        personality=personality, nation=nation, movement_range=1,
        tactical_skill=7, spawn_location=location, **kw)


def _world(*marshals, seed=ROLLED, served=True):
    """A fixture board. `served` stands in for the server's door
    (`backend.main._set_active_world`): the campaign is one a player plays."""
    world = WorldState()
    world.marshals = {m.name: m for m in marshals}
    nations = sorted({m.nation for m in marshals})
    for i, a in enumerate(nations):
        for b in nations[i + 1:]:
            world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"
    world.campaign_seed = seed
    if served:
        cv.serve_campaign(world)
    return world


def _solo_board(seed=ROLLED, served=True):
    ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
    mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
    return _world(ney, mack, seed=seed, served=served)


def _neighbour_of(world, region, besides):
    """A province beside `region` that is none of `besides` (the fixture map)."""
    for name in world.get_region(region).adjacent_regions:
        if name not in besides:
            return name
    raise AssertionError(f"{region} has no third neighbour")


def _coordinated_board(seed=ROLLED):
    """Ney attacks Mack; Davout stands in ANOTHER province beside the field,
    so his arrival is rolled; an Austrian corps stands beside it too."""
    probe = WorldState()
    flank = _neighbour_of(probe, "Waterloo", {"Belgium"})
    rear = _neighbour_of(probe, "Waterloo", {"Belgium", flank})
    ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
    davout = _mk("Davout", flank, 30000)
    mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
    charles = _mk("Charles", rear, 25000, nation="Austria")
    return _world(ney, davout, mack, charles, seed=seed)


def _reload(world):
    """The save and the load: a world rebuilt from its own dict and served
    again, as `/load` does (`load_game` then `_set_active_world`)."""
    loaded = WorldState.from_dict(world.to_dict())
    cv.serve_campaign(loaded)
    return loaded


def _fight(world, attacker="Ney", target="Mack"):
    executor = CommandExecutor()
    result = executor._execute_attack(
        world.marshals[attacker], target, world, {"world": world})
    assert result.get("success"), result.get("message")
    return result


def _reading(world, result):
    """Everything the dice decided, as plain data."""
    event = result["events"][0]
    rolls = result.get("reinforcement_results") or {}
    return {
        "arrivals": [(side, row.get("marshal"), row.get("arrived"), row.get("score"))
                     for side in ("attacker", "defender")
                     for row in (rolls.get(side) or [])],
        "outcome": event["outcome"],
        "attacker": (event["attacker"]["casualties"], event["attacker"]["remaining"]),
        "defender": (event["defender"]["casualties"], event["defender"]["remaining"]),
        "strengths": {n: int(m.strength) for n, m in sorted(world.marshals.items())},
        "morale": {n: int(m.morale) for n, m in sorted(world.marshals.items())},
        "places": {n: m.location for n, m in sorted(world.marshals.items())},
    }


@pytest.fixture
def stream_names(monkeypatch):
    """The seed string of every private stream made — the battle's identity."""
    made = []
    real = cv._PrivateStream

    def recording(seed_text):
        made.append(seed_text)
        return real(seed_text)

    monkeypatch.setattr(cv, "_PrivateStream", recording)
    return made


# ════════════════════════════════════════════════════════════════════════
# 1. The stream
# ════════════════════════════════════════════════════════════════════════

class TestTheStream:
    def test_no_stream_on_the_historical_seed(self):
        world = _solo_board(seed="historical")
        assert cv.battle_rng(world, "battle", "Ney", "Mack", "Waterloo") is None
        assert CE.battle_dice(world, world.marshals["Ney"], world.marshals["Mack"],
                              "Waterloo") is None

    def test_no_stream_without_a_seed_at_all(self):
        world = _solo_board(seed="")
        assert cv.battle_rng(world, "battle", "Ney", "Mack", "Waterloo") is None

    def test_no_stream_with_the_seam_down(self, monkeypatch):
        monkeypatch.setattr(cv, "the_battle_dice_are_seeded", lambda: False)
        assert cv.battle_rng(_solo_board(), "battle", "Ney", "Mack", "Waterloo") is None

    def test_one_identity_is_one_stream(self):
        a = cv.battle_rng(_solo_board(), "battle", "Ney", "Mack", "Waterloo")
        b = cv.battle_rng(_solo_board(), "battle", "Ney", "Mack", "Waterloo")
        assert [a.random() for _ in range(12)] == [b.random() for _ in range(12)]

    @pytest.mark.parametrize("change", ["seed", "turn", "lead", "foe", "field", "fought"])
    def test_another_identity_is_another_stream(self, change):
        base = _solo_board()
        other = _solo_board(seed="brass-anchor-41" if change == "seed" else ROLLED)
        parts = ["battle", "Ney", "Mack", "Waterloo"]
        if change == "turn":
            other.current_turn = int(base.current_turn) + 1
        elif change == "lead":
            parts[1] = "Davout"
        elif change == "foe":
            parts[2] = "Charles"
        elif change == "field":
            parts[3] = "Belgium"
        elif change == "fought":
            other.record_battle("Belgium", "Soult", "Hiller", "stalemate")
        a = cv.battle_rng(base, "battle", "Ney", "Mack", "Waterloo")
        b = cv.battle_rng(other, *parts)
        assert [a.random() for _ in range(12)] != [b.random() for _ in range(12)]

    def test_the_ambient_stream_is_never_touched(self):
        """`campaign_variance`'s own law: the module `random` is seeded by the
        suite and must not be consumed or reseeded by a private stream."""
        random.seed(20261114)
        before = random.getstate()
        rng = cv.battle_rng(_solo_board(), "battle", "Ney", "Mack", "Waterloo")
        [rng.randint(1, 6) for _ in range(50)]
        assert random.getstate() == before

    def test_the_seam_is_a_function_not_a_lever(self):
        """The code-health ratchet caps module-level flip levers; WS-11's
        switch is a function the series arms patch."""
        assert callable(cv.the_battle_dice_are_seeded)
        assert cv.the_battle_dice_are_seeded() is True
        assert "THE_BATTLE_DICE" not in inspect.getsource(cv)


# ════════════════════════════════════════════════════════════════════════
# 1b. Whose dice: the served campaign, and the harness that pins its own
# ════════════════════════════════════════════════════════════════════════

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestTheServedCampaign:
    def test_a_world_nobody_serves_keeps_the_callers_dice(self):
        """The measuring tools' idiom: a world built by hand on a NAMED seed,
        its dice pinned with `random.seed`. No private stream is made."""
        world = _solo_board(served=False)
        assert world.campaign_seed == ROLLED
        assert cv.campaign_is_served(world) is False
        assert cv.battle_rng(world, "battle", "Ney", "Mack", "Waterloo") is None
        assert CE.battle_dice(world, world.marshals["Ney"], world.marshals["Mack"],
                              "Waterloo") is None

    def test_its_pin_still_decides_the_battle(self, stream_names):
        """…so the same `random.seed` fights the same battle, another seed
        another one — exactly as before WS-11, on a named seed too."""
        def fought(ambient):
            world = _solo_board(served=False)
            random.seed(ambient)
            return repr(_reading(world, _fight(world)))

        assert fought(31) == fought(31)
        assert len({fought(n) for n in range(8)}) > 1
        assert stream_names == []

    def test_a_scenario_built_by_hand_is_not_served(self):
        """`WorldState.from_scenario(..., seed=…)` is how every sweep and
        probe builds its board (`tools/ai_v_sweep.py`,
        `tools/_sf_lb1_fight_bar_probe.py`): the model never serves itself."""
        scenario = (REPO_ROOT / "godot-client" / "project-sovereign" / "assets"
                    / "maps" / "europe_1805.json")
        world = WorldState.from_scenario(str(scenario), seed="austerlitz")
        assert world.campaign_seed == "austerlitz"
        assert cv.campaign_is_served(world) is False
        assert cv.battle_rng(world, "battle", "a", "b", "c") is None

    def test_the_servers_door_serves(self):
        import backend.main as M
        before = M.world
        world = _solo_board(served=False)
        try:
            assert M._set_active_world(world) is world
            assert cv.campaign_is_served(world) is True
            assert cv.battle_rng(world, "battle", "Ney", "Mack", "Waterloo") is not None
        finally:
            M._set_active_world(before)

    def test_every_world_the_server_holds_passes_that_door(self):
        """Structural: `backend/main.py` assigns its active `world` in ONE
        function. A second road (a rollback, a hot swap) that skipped the
        door would hand the player re-rollable dice without a word."""
        tree = ast.parse((REPO_ROOT / "backend" / "main.py").read_text(encoding="utf-8"))
        writers = set()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            declares = any(isinstance(n, ast.Global) and "world" in n.names
                           for n in ast.walk(node))
            if not declares:
                continue
            for n in ast.walk(node):
                targets = []
                if isinstance(n, ast.Assign):
                    targets = n.targets
                elif isinstance(n, (ast.AnnAssign, ast.AugAssign)):
                    targets = [n.target]
                if any(isinstance(t, ast.Name) and t.id == "world" for t in targets):
                    writers.add(node.name)
        assert writers == {"_set_active_world"}
        door = inspect.getsource(__import__("backend.main", fromlist=["x"])._set_active_world)
        assert "serve_campaign(new_world)" in door

    def test_a_copy_is_not_served_until_it_passes_the_door(self):
        """Nothing is written on the world and nothing is saved: a load is
        served again at the door, and a copy made off a served world (a
        forecast, a harness arm) is not."""
        world = _solo_board()
        assert cv.campaign_is_served(world)
        copy = WorldState.from_dict(world.to_dict())
        assert cv.campaign_is_served(copy) is False
        bare = _solo_board(served=False)
        assert world.to_dict().keys() == bare.to_dict().keys()

    def test_the_register_keeps_no_world_alive(self):
        """Held weakly: a campaign that was replaced is not kept in memory by
        having once been served."""
        import gc
        import weakref
        world = _solo_board()
        ref = weakref.ref(world)
        del world
        gc.collect()
        assert ref() is None


# ════════════════════════════════════════════════════════════════════════
# 2. The same save fights the same battle
# ════════════════════════════════════════════════════════════════════════

class TestTheSameSaveFightsTheSameBattle:
    def test_a_solo_battle_fought_again_from_the_save(self):
        saved = _solo_board()
        first, second = _reload(saved), _reload(saved)
        random.seed(1)
        a = _reading(first, _fight(first))
        random.seed(999)
        b = _reading(second, _fight(second))
        assert a == b

    def test_a_coordinated_battle_fought_again_from_the_save(self):
        """The arrival rolls, the dice, both variances and the rout all come
        off the one stream: who marched and what it cost are the same."""
        saved = _coordinated_board()
        first, second = _reload(saved), _reload(saved)
        random.seed(3)
        a = _reading(first, _fight(first))
        random.seed(4242)
        b = _reading(second, _fight(second))
        assert a == b
        # not vacuous: both sides' corps beside the field rolled to march
        assert {row[1] for row in a["arrivals"]} == {"Davout", "Charles"}
        assert all(row[3] is not None for row in a["arrivals"])

    def test_the_ambient_seed_decides_nothing_on_a_rolled_campaign(self):
        readings = set()
        for ambient in range(6):
            world = _solo_board()
            random.seed(ambient)
            readings.add(repr(_reading(world, _fight(world))))
        assert len(readings) == 1

    def test_the_battle_spends_none_of_the_ambient_stream_on_its_dice(self, monkeypatch):
        """On a rolled seed the resolver is handed the private stream: the
        2d6 and both variances are drawn from it, not from `combat.random`."""
        import backend.game_logic.combat as combat_module

        class Tripwire:
            def __getattr__(self, name):
                raise AssertionError(f"combat.random.{name} drawn on a rolled seed")

        world = _solo_board()
        monkeypatch.setattr(combat_module, "random", Tripwire())
        _fight(world)

    def test_two_battles_between_one_pair_in_one_turn_roll_their_own(self, stream_names):
        world = _solo_board()
        _fight(world)
        mack = world.marshals.get("Mack")
        if mack is None or mack.strength <= 0 or mack.location != "Waterloo":
            pytest.skip("the first clash drove Mack from the field on this seed")
        world.marshals["Ney"].location = "Belgium"
        _fight(world)
        battles = [s for s in stream_names if "|battle|" in s and "|Ney|Mack|" in s]
        assert len(battles) == 2 and battles[0] != battles[1]

    def test_the_identity_names_the_seed_the_turn_the_pair_and_the_field(self, stream_names):
        world = _solo_board()
        _fight(world)
        assert stream_names, "a rolled-seed battle makes its stream"
        text = stream_names[0]
        for part in (ROLLED, f"|{int(world.current_turn)}|", "|Ney|", "|Mack|", "|Waterloo|"):
            assert part in text, (part, text)


class TestTheEnemysAttackIsTheSame:
    """The enemy phase uses the same executor (Golden Rule 5), so the same
    stream: a battle the ENEMY opens is fought the same way from the save."""

    def test_an_enemy_attack_fought_again_from_the_save(self):
        saved = _coordinated_board()
        first, second = _reload(saved), _reload(saved)
        random.seed(8)
        a = _reading(first, _fight(first, attacker="Mack", target="Ney"))
        random.seed(31337)
        b = _reading(second, _fight(second, attacker="Mack", target="Ney"))
        assert a == b


class TestTheRoutes:
    """The defect as the player met it: F5, attack, F9, attack again."""

    def _battle(self, body):
        events = [e for e in (body.get("events") or []) if isinstance(e, dict)
                  and isinstance(e.get("attacker"), dict) and isinstance(e.get("defender"), dict)]
        assert events, body.get("message")
        e = events[0]
        return (e.get("outcome"), e["attacker"].get("casualties"), e["attacker"].get("remaining"),
                e["defender"].get("casualties"), e["defender"].get("remaining"))

    @staticmethod
    def _seat(world):
        """The suite's New Campaign is the bare Europe board (conftest pins
        SOVEREIGN_SCENARIO=none): two corps are seated on it, in sight."""
        ney = _mk("Ney", "Rhineland", 40000, personality="aggressive")
        foe = _mk("Wellington", "Lorraine", 30000, nation="Britain")   # on our own soil
        world.marshals = {"Ney": ney, "Wellington": foe}
        world.update_intel_from_battle("Lorraine", int(world.current_turn))

    def test_save_attack_load_attack_again(self, monkeypatch):
        import backend.main as M
        from backend.commands import objection_v2
        from fastapi.testclient import TestClient
        # The objection's mood is WS-16's (still on the ambient stream): held
        # level here so that this test reads the battle and nothing else.
        monkeypatch.setattr(objection_v2, "apply_mood_variance",
                            lambda value, *a, **k: value, raising=True)
        before = M.world
        try:
            with TestClient(M.app) as tc:
                booted = tc.post("/new_game", json={"seed": ROLLED}).json()
                assert booted["success"], booted.get("message")
                assert M.world.campaign_seed == ROLLED and cv.campaign_is_served(M.world)
                self._seat(M.world)
                assert tc.post("/save", json={"save_name": "ws11_reload"}).json()["success"]
                random.seed(5)
                first = tc.post("/command", json={"command": "Ney, attack Wellington"}).json()
                loaded = tc.post("/load", json={"filename": "ws11_reload.json"}).json()
                assert loaded["success"], loaded.get("message")
                assert cv.campaign_is_served(M.world), "a load is served again at the door"
                random.seed(77777)
                second = tc.post("/command", json={"command": "Ney, attack Wellington"}).json()
        finally:
            M._set_active_world(before)
        assert self._battle(first) == self._battle(second)

    def test_the_historical_campaign_is_still_the_callers(self, monkeypatch):
        """The same road on the suite's own seed: the reload re-rolls, as it
        always did — nothing on `historical` moved."""
        import backend.main as M
        from backend.commands import objection_v2
        from fastapi.testclient import TestClient
        monkeypatch.setattr(objection_v2, "apply_mood_variance",
                            lambda value, *a, **k: value, raising=True)
        before = M.world
        seen = set()
        try:
            with TestClient(M.app) as tc:
                assert tc.post("/new_game", json={"seed": "historical"}).json()["success"]
                self._seat(M.world)
                assert tc.post("/save", json={"save_name": "ws11_hist"}).json()["success"]
                for ambient in (5, 77777, 123, 9):
                    assert tc.post("/load", json={"filename": "ws11_hist.json"}).json()["success"]
                    random.seed(ambient)
                    seen.add(self._battle(tc.post(
                        "/command", json={"command": "Ney, attack Wellington"}).json()))
        finally:
            M._set_active_world(before)
        assert len(seen) > 1


class TestTheSeededDiceAreTheSameDice:
    """The stream changed, not the law: a battle's own dice are fair 2d6 and
    a fair ±10 %, as the ambient ones are."""

    def test_two_thousand_battles_roll_like_two_thousand_battles(self):
        from collections import Counter
        world = _solo_board()
        seeded, ambient = Counter(), Counter()
        luck_seeded = luck_ambient = 0.0
        random.seed(20261114)
        for n in range(2000):
            rng = cv.battle_rng(world, "battle", "Ney", "Mack", "Waterloo", n)
            seeded[rng.randint(1, 6) + rng.randint(1, 6)] += 1
            luck_seeded += rng.uniform(-0.10, 0.10)
            ambient[random.randint(1, 6) + random.randint(1, 6)] += 1
            luck_ambient += random.uniform(-0.10, 0.10)
        mean = lambda c: sum(k * v for k, v in c.items()) / 2000.0   # noqa: E731
        assert abs(mean(seeded) - 7.0) < 0.2 and abs(mean(ambient) - 7.0) < 0.2
        assert set(seeded) == set(range(2, 13))
        for total in range(2, 13):
            expected = 2000.0 * (6 - abs(7 - total)) / 36.0
            assert abs(seeded[total] - expected) < 60, (total, seeded[total], expected)
        assert abs(luck_seeded / 2000.0) < 0.006 and abs(luck_ambient / 2000.0) < 0.006

    def test_the_same_matchup_wins_as_often_on_either_stream(self):
        """By odds: Ney's 40,000 on Mack's 30,000, four hundred times each."""
        def won(served, n):
            world = _solo_board(served=served)
            world.current_turn = n          # another battle, another stream
            random.seed(n)
            event = _fight(world)["events"][0]
            return 1 if str(event["outcome"]).startswith("attacker") else 0

        seeded = sum(won(True, n) for n in range(400))
        ambient = sum(won(False, n) for n in range(400))
        assert abs(seeded - ambient) <= 40, (seeded, ambient)   # within ten points


# ════════════════════════════════════════════════════════════════════════
# 3. The historical seed is today's game
# ════════════════════════════════════════════════════════════════════════

class TestTheHistoricalSeedIsUntouched:
    def test_the_dice_are_still_the_module_streams(self):
        """A solo battle's first two draws are its 2d6 — exactly the module
        stream's next two, as before."""
        world = _solo_board(seed="historical")
        random.seed(77)
        expected = random.randint(1, 6) + random.randint(1, 6)
        random.seed(77)
        seen = {}
        real = CombatResolver.roll_combat_dice

        def spy(self, marshal, flanking_bonus=0):
            seen["roll"] = real(self, marshal, flanking_bonus=flanking_bonus)
            return seen["roll"]

        from unittest.mock import patch
        with patch.object(CombatResolver, "roll_combat_dice", spy):
            _fight(world)
        assert seen["roll"]["natural"] == expected

    def test_a_fixed_arity_double_of_the_dice_still_works(self, monkeypatch):
        """Seven test files replace `roll_combat_dice` with
        `lambda self, marshal, flanking_bonus=0`; the resolver passes no
        `rng` on the historical seed, so they are called as they always were."""
        monkeypatch.setattr(
            CombatResolver, "roll_combat_dice",
            lambda self, marshal, flanking_bonus=0: {
                "natural": 7, "modified": 9, "is_critical_success": False,
                "is_critical_failure": False, "multiplier": 1.075,
                "skill_bonus": 2, "flanking_bonus": int(flanking_bonus)})
        world = _solo_board(seed="historical")
        _fight(world)

    def test_a_fixed_arity_double_of_the_guns_still_works(self, monkeypatch):
        """…and four replace `_execute_bombardment(self, gunner, defender,
        world, game_state)`."""
        calls = []
        real = CE.CombatExecutor._execute_bombardment

        def double(self_exec, gunner, defender, w, gs):
            calls.append(gunner.name)
            return real(self_exec, gunner, defender, w, gs)

        monkeypatch.setattr(CE.CombatExecutor, "_execute_bombardment", double)
        world = _solo_board(seed="historical")
        _fight(world)   # no guns on this board: the double is simply never needed
        assert calls == []

    def test_different_ambient_seeds_still_roll_different_battles(self):
        readings = set()
        for ambient in range(8):
            world = _solo_board(seed="historical")
            random.seed(ambient)
            readings.add(repr(_reading(world, _fight(world))))
        assert len(readings) > 1


# ════════════════════════════════════════════════════════════════════════
# 4. What the resolver now keeps, and the pin WS-11 was filed with
# ════════════════════════════════════════════════════════════════════════

class TestTheResolver:
    def _resolve(self, rng=None):
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        kwargs = {"rng": rng} if rng is not None else {}
        return CombatResolver().resolve_battle(ney, mack, terrain="open", **kwargs)

    def test_each_sides_fortune_is_kept_as_a_whole_percent(self):
        random.seed(5)
        fortune = self._resolve()["fortune"]
        assert set(fortune) == {"attacker", "defender"}
        for side in ("attacker", "defender"):
            assert isinstance(fortune[side], int) and not isinstance(fortune[side], bool)
            assert -10 <= fortune[side] <= 10

    def test_the_fortune_is_the_variance_that_was_drawn(self):
        from unittest.mock import patch
        with patch("backend.game_logic.combat.random.uniform", return_value=0.07), \
                patch("backend.game_logic.combat.random.randint", return_value=4):
            fortune = self._resolve()["fortune"]
        assert fortune == {"attacker": 7, "defender": 7}

    def test_the_deferred_road_keeps_it_too(self):
        ney = _mk("Ney", "Belgium", 40000, personality="aggressive")
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        random.seed(5)
        result = CombatResolver().resolve_battle(
            ney, mack, terrain="open", apply_casualties=False)
        assert set(result["fortune"]) == {"attacker", "defender"}

    def test_a_handed_stream_rolls_the_whole_battle(self):
        a = self._resolve(random.Random("one battle"))
        b = self._resolve(random.Random("one battle"))
        c = self._resolve(random.Random("another battle"))
        key = lambda r: (r["attacker_roll"]["natural"], r["fortune"]["attacker"],  # noqa: E731
                         r["fortune"]["defender"], r["attacker"]["casualties"],
                         r["defender"]["casualties"], r["description"])
        assert key(a) == key(b)
        assert key(a) != key(c)

    def test_the_dice_are_the_campaigns(self):
        """The pin WS-11 was filed with
        (`TestWS11ABattleIsRolledAgainByLoading`), no longer an xfail: the
        2d6 is not drawn straight off the module stream."""
        assert "random.randint(" not in inspect.getsource(CombatResolver.roll_combat_dice)


# ════════════════════════════════════════════════════════════════════════
# 5. The guns
# ════════════════════════════════════════════════════════════════════════

class TestTheGuns:
    def _board(self, seed=ROLLED):
        gunner = _mk("Drouot", "Belgium", 12000, artillery=True)
        mack = _mk("Mack", "Waterloo", 30000, nation="Austria")
        return _world(gunner, mack, seed=seed)

    def _salvo(self, world):
        executor = CommandExecutor()
        result = executor._combat._execute_bombardment(
            world.marshals["Drouot"], world.marshals["Mack"], world, {"world": world})
        assert result.get("success"), result.get("message")
        br = result["bombardment_result"]
        return (br["attacker"]["casualties"], br["defender"]["casualties"])

    def test_a_salvo_fired_again_from_the_save(self):
        saved = self._board()
        first, second = _reload(saved), _reload(saved)
        random.seed(11)
        a = self._salvo(first)
        random.seed(2222)
        b = self._salvo(second)
        assert a == b

    def test_the_second_salvo_has_its_own_dice(self, stream_names):
        world = self._board()
        self._salvo(world)
        self._salvo(world)
        salvos = [s for s in stream_names if "|bombard|" in s]
        assert len(salvos) == 2 and salvos[0] != salvos[1]

    def test_the_historical_guns_are_the_module_streams(self):
        readings = set()
        for ambient in range(8):
            world = self._board(seed="historical")
            random.seed(ambient)
            readings.add(self._salvo(world))
        assert len(readings) > 1


# ═══════════════════════════════════════════════════════════════════════════
# The measure: the France band on the commanded arms
# ═══════════════════════════════════════════════════════════════════════════

class TestTheBandOnTheCommandedArms:
    """The deploy gate's difficulty guard (`DYNAMISM_SPEC.md` §2: France holds
    23–28 provinces at turn 40 on the commanded arms) is read through
    `tools/playtest_driver.py`, which plays THROUGH the server: `/new_game`
    installs its world at the door that serves a campaign. On austerlitz and
    marengo the commanded arms are therefore served campaigns on a rolled
    seed, and their battles draw the campaign's dice.

    The record is `tools/_ba1_band_2026_11_14.json`
    (`tools/_ba1_band_measure.py`, a chain run alone): arm 0 holds WS-11's
    seam down through the driver's own `--seam`; arm ALL is the shipped tree.
    A seeded arm's reading is one world-line of its seed, not a law — the
    seeded dice are the same dice (`TestTheSeededDiceAreTheSameDice`)."""

    ARMS = ("CMD-H", "CMD-A", "CMD-M")

    @staticmethod
    def _record(name):
        return json.loads((REPO_ROOT / "tools" / name).read_text(encoding="utf-8"))

    def _band(self, record, arm):
        return [record["arms"][arm][n]["provinces"] for n in self.ARMS]

    def test_the_seam_down_is_session_g5s_band_to_the_province(self):
        mine = self._record("_ba1_band_2026_11_14.json")
        g5 = self._record("_g5_band_2026_11_11.json")
        assert mine["arms"]["0"]["seams_down"] == [
            "backend.game_logic.campaign_variance:the_battle_dice_are_seeded=False"]
        assert self._band(mine, "0") == self._band(g5, "ALL") == [26, 26, 25]

    def test_the_historical_arm_does_not_move(self):
        mine = self._record("_ba1_band_2026_11_14.json")
        assert mine["arms"]["ALL"]["seams_down"] == []
        assert mine["arms"]["ALL"]["CMD-H"] == mine["arms"]["0"]["CMD-H"]

    def test_the_seeded_arms_move_and_the_guard_holds(self):
        mine = self._record("_ba1_band_2026_11_14.json")
        low, high = mine["band"]
        assert (low, high) == (23, 28)
        assert self._band(mine, "ALL") == [26, 27, 28]
        for arm in ("0", "ALL"):
            for name in self.ARMS:
                row = mine["arms"][arm][name]
                assert row["status"] == "completed" and row["turn"] == 40, (arm, name)
                assert low <= row["provinces"] <= high, (arm, name, row["provinces"])

    def test_the_measure_reads_the_gates_own_arms_through_the_driver(self):
        tool = (REPO_ROOT / "tools" / "_ba1_band_measure.py").read_text(encoding="utf-8")
        assert 'BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")' in tool
        assert "SR._run_driver(ROOT, arms_dir, name, list(SR.ARMS[name][\"argv\"]) + seams)" in tool
        driver = (REPO_ROOT / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'transport.post("/new_game"' in driver          # the door that serves
        from tools import score_run as SR
        seeds = {name: SR.ARMS[name]["argv"][SR.ARMS[name]["argv"].index("--seed") + 1]
                 for name in self.ARMS}
        assert seeds == {"CMD-H": "historical", "CMD-A": "austerlitz", "CMD-M": "marengo"}
