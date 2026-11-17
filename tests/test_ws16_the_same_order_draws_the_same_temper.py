"""WS-16 (row BA, BA-3) — the same order draws the same temper.

WS-11's siblings (`docs/BUG_FIXES.md` §WS row WS-16; `BATTLE_DIORAMA_SPEC.md`
§15.7, §15.14): the draws that decide what a marshal — or Talleyrand, or a
satellite — DOES came off the module `random`, which no save carries. Save,
give the order, load, give it again: a new mood, a new defiance.

Now, in a campaign the game SERVER holds, on a ROLLED campaign seed, each of
those draws comes off a private stream keyed on the seed, the turn, the kind
of draw and its own identity (`campaign_variance.temper_rng`). The same order
from the same save draws the same mood and the same defiance; another order,
another marshal or another turn draws its own.

What did not move — the two cases WS-11 kept, kept here the same way:

* the `historical` seed (the suite's pin): `temper_rng` is None, every draw
  stays on the module `random`, and every call keeps the shape it had (a
  fixed-arity test double of `apply_mood_variance` still fits);
* a world nobody serves (the measuring harnesses build their own).

And one seam: `campaign_variance.the_temper_is_seeded()` held down is the
ambient stream again.

The PROSE stays where it was: which of Berthier's lines is quoted, which
template an objection speaks — display only, ruled as designed (the row).
"""

import ast
import contextlib
import io
import random
from pathlib import Path

import pytest

from backend.commands import defiance as DEF
from backend.commands import diplomatic_defiance as DD
from backend.commands import objection_v2 as OV2
from backend.commands import severity as SEV
from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import ConcernLevel
from backend.game_logic import campaign_variance as cv
from backend.game_logic import vassal as V
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
ROLLED = "iron-eagle-07"
SEEDS = ["iron-eagle-%02d" % n for n in range(1, 25)]
ATTACK = {"action": "attack", "type": "specific", "marshal": "Davout", "target": "Wellington"}


# ════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════

def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _board(seed=ROLLED, *, served=True, ours=None, his=None):
    """The fixture board: Davout (cautious) beside Wellington, at war.

    As it stands his odds concern is MILD — a note in the log, the attack goes
    in — and the mood promotes it to an objection one draw in ten. With
    `ours`/`his` set the odds are bad and he objects outright."""
    world = WorldState()
    davout = world.marshals["Davout"]
    assert davout.personality == "cautious", "fixture roster changed"
    davout.location = "Belgium"
    if ours:
        davout.strength = int(ours)
    if his:
        world.marshals["Wellington"].strength = int(his)
    world.campaign_seed = seed
    if served:
        cv.serve_campaign(world)
    return world


def _reload(world, *, served=True):
    """The save and the load, as `/load` does (`load_game`, then the door)."""
    loaded = WorldState.from_dict(world.to_dict())
    if served:
        cv.serve_campaign(loaded)
    return loaded


def _order(world, command=None):
    executor = CommandExecutor()
    with _quiet():
        result = executor.execute({"command": dict(command or ATTACK)}, {"world": world})
    return executor, result


def _mood(world, result):
    """What the mood decided, as plain data: an objection raised and at what
    level, or the note in the log."""
    pending = world.pending_objection or {}
    return (bool(result.get("pending_objection")), pending.get("concern_level"),
            len(world.mild_concerns_this_turn))


def _insisted(world, executor):
    """Insist, and read what he did: defied or obeyed, and where it left him."""
    with _quiet():
        answer = executor.handle_objection_response("insist", {"world": world})
    davout = world.marshals["Davout"]
    return (bool(answer.get("defiance")), davout.location, bool(getattr(davout, "fortified", False)),
            int(davout.strength))


def _from_the_save(saved, read, *, ambients=(5, 77777)):
    """The same deed from the same save under two ambient streams."""
    out = []
    for ambient in ambients:
        world = _reload(saved, served=cv.campaign_is_served(saved))
        random.seed(ambient)
        out.append(read(world))
    return out


@pytest.fixture
def stream_names(monkeypatch):
    """The seed string of every private stream made — a draw's identity."""
    made = []
    real = cv._PrivateStream

    class Recording(real):
        def __init__(self, seed):
            made.append(str(seed))
            super().__init__(seed)

    monkeypatch.setattr(cv, "_PrivateStream", Recording)
    return made


# ════════════════════════════════════════════════════════
# The headline: the mood
# ════════════════════════════════════════════════════════

class TestAnOrderInsistedOnAgainDrawsTheSameMood:
    """Whether an objection is raised at all is the mood's draw
    (`objection_v2.apply_mood_variance`)."""

    @staticmethod
    def _read(world):
        _, result = _order(world)
        return _mood(world, result)

    # Ambient streams that — were the mood drawn from them — split it both
    # ways (31 promotes the note to an objection; 5 and 77777 do not). The
    # review (BA3-X20): under 5 and 77777 alone the two readings agreed
    # whatever drew the mood, so the pin held with the seam held down.
    AMBIENTS = (5, 31, 77777)

    def test_the_same_order_from_the_same_save_draws_the_same_mood(self):
        for seed in SEEDS:
            readings = _from_the_save(_board(seed), self._read, ambients=self.AMBIENTS)
            assert len(set(readings)) == 1, f"{seed}: the reload drew another mood — {readings}"

    def test_the_same_mood_pin_can_fail(self, monkeypatch):
        """Held down, the same reloads under the same ambient streams draw
        MORE than one mood: the pin above is not blind."""
        monkeypatch.setattr(cv, "the_temper_is_seeded", lambda: False)
        readings = _from_the_save(_board(ROLLED), self._read, ambients=self.AMBIENTS)
        assert len(set(readings)) > 1, "the ambient streams no longer split the mood"

    def test_the_draw_decides_something(self):
        """Not a vacuous pin: across campaigns the same order meets a note in
        the log on most, and an objection on some."""
        readings = {self._read(_reload(_board(seed))) for seed in SEEDS}
        raised = {r for r in readings if r[0]}
        noted = {r for r in readings if not r[0]}
        assert raised and noted, readings

    def test_the_strategic_road_gives_the_same_answer_on_a_reload(self):
        """The strategic road's own draws (its mood, its defiance chance and
        roll) by behaviour — the pin below only reads the source. (The
        review, BA3-X20.) A strong strategic objection, insisted on from the
        same save under three ambient streams: the same answer every time,
        and across campaigns he defies on some."""
        from tests.test_wo_slice16_objection_pays_honestly import COMPROMISE, PROCEED, _objection
        defied = 0
        for seed in SEEDS:
            saved = WorldState(player_nation="France")
            saved.actions_remaining = 4
            saved.admin_actions_remaining = 2
            saved.campaign_seed = seed
            objection = _objection([PROCEED, COMPROMISE])
            objection["concern_level"] = "STRONG"
            saved.pending_strategic_objection = objection
            answers = []
            for ambient in (1, 2, 3):
                world = _reload(saved)
                random.seed(ambient)
                with _quiet():
                    answer = CommandExecutor()._strategic._handle_strategic_objection_from_endpoint(
                        "insist", {"world": world})
                answers.append(bool(answer.get("defiance")))
            assert len(set(answers)) == 1, f"{seed}: the reload met another answer — {answers}"
            defied += answers[0]
        assert 0 < defied < len(SEEDS), "the draw decides something"

    def test_the_strategic_road_draws_from_the_same_seam(self):
        """`strategic_executor`'s copy of the draw reads the same stream kind,
        keyed on the marshal, the order and its target — and, since row BA's
        BA-4 (BA3-X16), the order's own mark, read off the command and the
        parse beside it (`campaign_variance.order_mark`: nothing for an order
        that carries no mark, so such an order draws as it did)."""
        import inspect
        from backend.commands import strategic_executor as SE
        src = " ".join(inspect.getsource(SE).split())
        assert ('_cv.temper_rng(ctx.world, "mood", ctx.marshal.name, ctx.strategic_type, ctx.target, '
                '*_cv.order_mark(ctx.command, ctx.parsed_command))') in src


# ════════════════════════════════════════════════════════
# The headline: the defiance
# ════════════════════════════════════════════════════════

class TestTheDefianceRollIsTheSameOnAReload:
    """Insist against a strong objection: whether he obeys is the defiance
    chance's variance and its roll (`defiance.calculate_defiance_chance`;
    `meta_executor.handle_objection_response`)."""

    @staticmethod
    def _read(world):
        executor, result = _order(world)
        assert result.get("pending_objection"), result.get("message")
        level = (world.pending_objection or {}).get("concern_level")
        random.seed(random.random())            # the insist meets another ambient stream again
        return (level,) + _insisted(world, executor)

    def test_the_same_insistence_from_the_same_save_meets_the_same_answer(self):
        for seed in SEEDS:
            a, b = _from_the_save(_board(seed, ours=20000, his=70000), self._read)
            assert a == b, f"{seed}: the reload drew another defiance — {a} then {b}"

    def test_the_roll_decides_something(self):
        answers = {self._read(_reload(_board(seed, ours=20000, his=70000)))[1] for seed in SEEDS}
        assert answers == {True, False}, "across campaigns he obeys on most and defies on some"

    def test_the_chance_and_the_roll_are_two_draws(self, stream_names):
        world = _reload(_board(ours=20000, his=70000))
        executor, _ = _order(world)
        del stream_names[:]
        _insisted(world, executor)
        kinds = [name.split("|")[3] for name in stream_names if "|temper|" in name]
        assert "defiance_chance" in kinds and "defiance_roll" in kinds, stream_names


# ════════════════════════════════════════════════════════
# The stream's identity
# ════════════════════════════════════════════════════════

class TestTwoOrdersDrawDifferentTemper:

    def _first(self, world, *identity, **kw):
        return cv.temper_rng(world, *identity, **kw).random()

    def test_the_identity_is_the_seed_the_turn_the_kind_and_the_order(self, stream_names):
        world = _board()
        cv.temper_rng(world, "mood", "Davout", "attack", "Wellington")
        assert stream_names[-1] == (
            f"{ROLLED}|temper|{int(world.current_turn)}|mood|Davout|attack|Wellington"
            f"|{len(world.battles_this_turn)}|{int(world.actions_remaining)}")

    def test_the_same_identity_is_the_same_draw(self):
        world = _board()
        assert self._first(world, "mood", "Davout", "attack", "Wellington") == \
            self._first(world, "mood", "Davout", "attack", "Wellington")

    @pytest.mark.parametrize("other", [
        ("mood", "Ney", "attack", "Wellington"),          # another marshal
        ("mood", "Davout", "defend", "Wellington"),       # another order
        ("mood", "Davout", "attack", "Blucher"),          # another target
        ("defiance_roll", "Davout", "attack", "Wellington"),  # another kind of draw
    ])
    def test_another_order_draws_its_own(self, other):
        world = _board()
        assert self._first(world, "mood", "Davout", "attack", "Wellington") != self._first(world, *other)

    def test_another_turn_another_campaign_another_state_of_the_turn(self):
        world = _board()
        base = self._first(world, "mood", "Davout", "attack", "Wellington")
        later = _board()
        later.current_turn = int(world.current_turn) + 1
        assert self._first(later, "mood", "Davout", "attack", "Wellington") != base
        other = _board("iron-eagle-08")
        assert self._first(other, "mood", "Davout", "attack", "Wellington") != base
        spent = _board()
        spent.actions_remaining = int(world.actions_remaining) - 1
        assert self._first(spent, "mood", "Davout", "attack", "Wellington") != base

    def test_a_draw_inside_the_turns_processing_keys_on_the_turn_alone(self, stream_names):
        """`saved=False`: the turn's own processing runs once a turn, with no
        order behind it — the state of the player's turn is no part of it."""
        world = _board()
        cv.temper_rng(world, "vassal_bribe", "Britain", "Saxony", saved=False)
        assert stream_names[-1] == f"{ROLLED}|temper|{int(world.current_turn)}|vassal_bribe|Britain|Saxony"

    def test_the_seeded_mood_is_the_same_mood(self):
        """The stream changed, not the law: ten in a hundred up, fifteen down."""
        world = _board()
        moved = {"up": 0, "down": 0, "same": 0}
        for n in range(4000):
            got = OV2.apply_mood_variance(ConcernLevel.STRONG, rng=cv.temper_rng(world, "mood", "law", n))
            key = "up" if got.value > ConcernLevel.STRONG.value else (
                "down" if got.value < ConcernLevel.STRONG.value else "same")
            moved[key] += 1
        assert 320 <= moved["up"] <= 480, moved
        assert 500 <= moved["down"] <= 700, moved


# ════════════════════════════════════════════════════════
# What did not move
# ════════════════════════════════════════════════════════

class TestTheHistoricalSeedKeepsTheAmbientStream:

    def test_there_is_no_stream_on_the_historical_seed(self):
        world = _board("historical")
        assert cv.temper_rng(world, "mood", "Davout", "attack", "Wellington") is None

    def test_the_mood_follows_the_ambient_stream_as_it_always_did(self):
        saved = _board("historical")
        readings = set()
        for ambient in range(1, 60):
            world = _reload(saved)
            random.seed(ambient)
            _, result = _order(world)
            readings.add(_mood(world, result)[0])
        assert readings == {True, False}, "the reload re-rolls on `historical`, as before"

    def test_a_fixed_arity_double_of_the_mood_still_fits(self, monkeypatch):
        """Forty test files hold the mood level with `lambda concern: concern`:
        the call keeps its one argument where there is no stream."""
        from backend.commands import executor as EX
        monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
        world = _board("historical")
        _, result = _order(world)
        assert result.get("success"), result.get("message")

    def test_the_defiance_follows_the_ambient_stream(self, monkeypatch):
        saved = _board("historical", ours=20000, his=70000)
        monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.5)
        seen = set()
        for ambient in range(1, 40):
            world = _reload(saved)
            random.seed(ambient)
            executor, result = _order(world)
            if not result.get("pending_objection"):
                continue
            seen.add(_insisted(world, executor)[0])
        assert seen == {True, False}


class TestAWorldNobodyServesKeepsTheAmbientStream:

    def test_no_stream_off_the_served_road(self):
        world = _board(served=False)
        assert world.campaign_seed == ROLLED
        assert cv.temper_rng(world, "mood", "Davout", "attack", "Wellington") is None

    def test_the_mood_follows_the_ambient_stream(self):
        saved = _board(served=False)
        readings = set()
        for ambient in range(1, 60):
            world = _reload(saved, served=False)
            random.seed(ambient)
            _, result = _order(world)
            readings.add(_mood(world, result)[0])
        assert readings == {True, False}


class TestTheTemperSeamHeldDownIsTheAmbientStream:

    def test_the_seam_is_a_function_read_through_its_module(self):
        assert cv.the_temper_is_seeded() is True
        assert callable(cv.the_temper_is_seeded)

    def test_held_down_there_is_no_stream(self, monkeypatch):
        world = _board()
        assert cv.temper_rng(world, "mood", "Davout", "attack", "Wellington") is not None
        monkeypatch.setattr(cv, "the_temper_is_seeded", lambda: False)
        assert cv.temper_rng(world, "mood", "Davout", "attack", "Wellington") is None
        assert cv.temper_rng(world, "vassal_bribe", "Britain", "Saxony", saved=False) is None

    def test_held_down_the_battles_dice_stand(self, monkeypatch):
        """One seam, one thing: WS-11's dice are not WS-16's."""
        world = _board()
        monkeypatch.setattr(cv, "the_temper_is_seeded", lambda: False)
        assert cv.campaign_is_served(world) and not cv.is_historical(world.campaign_seed)
        # The review (BA3-X20): the line above asked nothing of the dice.
        assert cv.temper_rng(world, "mood", "Davout", "attack", "Wellington") is None
        assert cv.battle_rng(world, "Davout", "Wellington") is not None, "the battle's dice stand"


# ════════════════════════════════════════════════════════
# The remaining sites
# ════════════════════════════════════════════════════════

class TestEachRemainingSiteIsSeededOrRuledAsDesigned:
    """The row's list, each by behaviour where a small board reaches it and
    all of them by the census below."""

    # ── the severity's variance (`severity.apply_variance`) ──

    def test_the_strategic_severity_reads_the_same_from_the_same_save(self):
        saved = _board()
        got = []
        for ambient in (5, 77777, 12):
            world = _reload(saved)
            random.seed(ambient)
            got.append(SEV.calculate_strategic_severity(
                world.marshals["Davout"], "PURSUE", 0.50, {"world": world}))
        assert len(set(got)) == 1, got

    def test_the_severity_on_historical_follows_the_ambient_stream(self):
        world = _board("historical")
        got = set()
        for ambient in (5, 77777, 12, 9):
            random.seed(ambient)
            got.add(SEV.calculate_strategic_severity(
                world.marshals["Davout"], "PURSUE", 0.50, {"world": world}))
        assert len(got) > 1

    def test_two_concerns_of_one_order_draw_their_own_variance(self, stream_names):
        world = _board()
        SEV.calculate_strategic_severity(world.marshals["Davout"], "PURSUE", 0.50, {"world": world})
        SEV.calculate_strategic_severity(world.marshals["Davout"], "PURSUE", 0.45, {"world": world})
        assert stream_names[-1] != stream_names[-2]

    def test_the_severity_takes_the_world_in_any_of_its_three_shapes(self):
        world = _board()
        davout = world.marshals["Davout"]

        class Holder:
            pass
        holder = Holder()
        holder.world = world
        assert SEV._seeded({"world": world}, davout, "x") and SEV._seeded(world, davout, "x")
        assert SEV._seeded(holder, davout, "x")
        assert SEV._seeded(None, davout, "x") == {} and SEV._seeded({}, davout, "x") == {}

    # ── Talleyrand's defiance: the chance's variance ──

    def test_talleyrands_chance_takes_the_campaigns_stream(self):
        world = _board()
        world.authority_tracker.authority = 45
        talleyrand = world.diplomats[world.player_nation]
        got = set()
        for ambient in (5, 77777, 12):
            random.seed(ambient)
            got.add(DD.calculate_diplomatic_defiance_chance(
                talleyrand, world, rng=cv.temper_rng(world, "talleyrand_defiance", "peace", "Austria")))
        assert len(got) == 1
        ambient = set()
        for seed in (5, 77777, 12, 9):
            random.seed(seed)
            ambient.add(DD.calculate_diplomatic_defiance_chance(talleyrand, world))
        assert len(ambient) > 1, "with no stream handed in it is the module `random`, as before"

    def test_the_proposals_site_hands_the_stream_to_both_draws(self):
        import inspect
        from backend.commands import diplomatic_executor as DX
        src = inspect.getsource(DX)
        assert '_cv.temper_rng(ctx.world, "talleyrand_defiance",' in src
        assert '**({"rng": _t_rng} if _t_rng is not None else {}))' in src
        assert "(_t_rng if _t_rng is not None else random).random() < defiance_chance" in src

    # ── the sabotage's discovery (the morning dispatch) ──

    def test_a_sabotage_is_discovered_or_not_the_same_from_the_same_turn(self):
        world = _board()
        for hidden in range(0, 5):
            sabotage = {"sabotage_type": "softened", "turns_hidden": hidden}
            got = set()
            for ambient in (5, 77777, 12, 9):
                random.seed(ambient)
                got.add(DD.check_sabotage_discovery(dict(sabotage), world))
            assert len(got) == 1, (hidden, got)

    def test_the_discovery_still_falls_both_ways(self):
        found = set()
        for seed in SEEDS:
            found.add(DD.check_sabotage_discovery({"sabotage_type": "softened", "turns_hidden": 0},
                                                  _board(seed)))
        assert found == {True, False}, "forty in a hundred on the first morning"

    def test_the_discovery_on_historical_follows_the_ambient_stream(self, monkeypatch):
        world = _board("historical")
        monkeypatch.setattr(random, "random", lambda: 0.0)
        assert DD.check_sabotage_discovery({"turns_hidden": 0}, world) is True
        monkeypatch.setattr(random, "random", lambda: 0.99)
        assert DD.check_sabotage_discovery({"turns_hidden": 0}, world) is False

    # ── the drafting pushback ──

    @staticmethod
    def _harsh():
        return {"demands": [{"type": "territory_cede", "regions": ["A", "B", "C", "D", "E"]}]}

    def test_the_same_draft_from_the_same_save_meets_the_same_pushback(self):
        saved = _board()
        saved.authority_tracker.authority = 40
        for target in ("Austria", "Prussia", "Russia", "Britain", "Spain"):
            context = {"proposal_type": "peace", "target_nation": target}
            got = set()
            for ambient in (5, 77777, 12, 9):
                world = _reload(saved)
                random.seed(ambient)
                got.add(DD.roll_drafting_pushback(self._harsh(), dict(context), world))
            assert len(got) == 1, (target, got)

    def test_the_pushback_still_falls_both_ways(self):
        got = set()
        for seed in SEEDS:
            world = _board(seed)
            world.authority_tracker.authority = 40
            for target in ("Austria", "Prussia", "Russia"):
                got.add(DD.roll_drafting_pushback(
                    self._harsh(), {"proposal_type": "peace", "target_nation": target}, world))
        assert got == {True, False}

    def test_the_pushback_on_historical_follows_the_ambient_stream(self, monkeypatch):
        world = _board("historical")
        world.authority_tracker.authority = 40
        context = {"proposal_type": "peace", "target_nation": "Austria"}
        monkeypatch.setattr(random, "uniform", lambda a, b: 0.0)
        monkeypatch.setattr(random, "random", lambda: 0.0)
        assert DD.roll_drafting_pushback(self._harsh(), dict(context), world) is True
        monkeypatch.setattr(random, "random", lambda: 0.99)
        assert DD.roll_drafting_pushback(self._harsh(), dict(context), world) is False

    # ── a satellite's defection (the turn's processing) ──

    @staticmethod
    def _losing_lord(seed):
        from backend.game_logic.vassal import AUTONOMY_SATELLITE, TRIBUTE_RATES
        world = WorldState()
        world.vassals["Saxony"] = {
            "lord": "France", "loyalty": 5, "autonomy": int(AUTONOMY_SATELLITE), "path": "treaty",
            "created_turn": 1, "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
            "carved_from": None, "regions": None,
        }
        bond = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[bond] = "VASSAL"
        world.nation_relations[bond] = 0
        war = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[war] = "WAR"
        world.war_scores[war] = -40
        world.campaign_seed = seed
        cv.serve_campaign(world)
        return world

    def test_a_satellite_defects_or_stays_the_same_from_the_same_save(self):
        outcomes = set()
        for seed in SEEDS[:12]:
            saved = self._losing_lord(seed)
            got = set()
            for ambient in (5, 77777, 12):
                world = _reload(saved)
                random.seed(ambient)
                with _quiet():
                    got.add(len(V.check_defection_cascade(world)))
            assert len(got) == 1, (seed, got)
            outcomes |= got
        assert outcomes == {0, 1}, "forty-five in a hundred at loyalty 5: both across campaigns"

    def test_the_defection_on_historical_follows_the_ambient_stream(self):
        from unittest.mock import patch
        world = self._losing_lord("historical")
        with patch("backend.game_logic.vassal.random") as ambient:
            ambient.random.return_value = 0.01
            with _quiet():
                assert len(V.check_defection_cascade(world)) == 1

    # ── the census: every site, by its kind ──

    KINDS = {
        "mood": ("backend/commands/executor.py", "backend/commands/strategic_executor.py"),
        "defiance_chance": ("backend/commands/meta_executor.py", "backend/commands/strategic_executor.py"),
        "defiance_roll": ("backend/commands/meta_executor.py", "backend/commands/strategic_executor.py"),
        "severity": ("backend/commands/severity.py",),
        "talleyrand_defiance": ("backend/commands/diplomatic_executor.py",),
        "sabotage_discovery": ("backend/commands/diplomatic_defiance.py",),
        "drafting_pushback": ("backend/commands/diplomatic_defiance.py",),
        "mission_blowback": ("backend/game_logic/diplomacy.py",),
        "rivalry": ("backend/game_logic/jealousy.py",),
        "defection_cascade": ("backend/game_logic/vassal.py",),
        "courting_heard": ("backend/game_logic/vassal.py",),
        "vassal_bribe": ("backend/game_logic/vassal.py",),
    }
    # The turn's own processing: no order behind the draw.
    TURN_KINDS = {"sabotage_discovery", "mission_blowback", "defection_cascade",
                  "courting_heard", "vassal_bribe"}

    @staticmethod
    def _temper_calls():
        """(file, kind, saved=False given) for every `temper_rng(...)` call."""
        found = []
        for path in sorted((REPO / "backend").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if "temper_rng" not in text:
                continue
            for node in ast.walk(ast.parse(text)):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "temper_rng"):
                    continue
                kind = node.args[1].value if len(node.args) > 1 and isinstance(
                    node.args[1], ast.Constant) else None
                unsaved = any(k.arg == "saved" and isinstance(k.value, ast.Constant)
                              and k.value.value is False for k in node.keywords)
                found.append((path.relative_to(REPO).as_posix(), kind, unsaved))
        return found

    def test_every_site_of_the_row_draws_from_the_temper_stream(self):
        calls = self._temper_calls()
        for kind, files in self.KINDS.items():
            for file in files:
                assert any(f == file and k == kind for f, k, _ in calls), (
                    f"{file} no longer draws its `{kind}` from `campaign_variance.temper_rng`")

    def test_a_draw_of_the_turns_processing_is_keyed_on_the_turn_alone(self):
        for file, kind, unsaved in self._temper_calls():
            if kind in self.KINDS:
                assert unsaved == (kind in self.TURN_KINDS), (file, kind, unsaved)

    def test_the_rows_count_of_vassal_sites_is_three(self):
        """The row said two; the sweep found the courting's detection too."""
        kinds = {k for f, k, _ in self._temper_calls() if f == "backend/game_logic/vassal.py"}
        assert kinds == {"defection_cascade", "courting_heard", "vassal_bribe"}

    def test_the_courtings_detection_is_still_drawn_for_our_satellites_alone(self):
        """IQ7-X1 kept: a rival lord's courting consumes no draw of any stream."""
        src = (REPO / "backend/game_logic/vassal.py").read_text(encoding="utf-8")
        assert "if lord == player and (_heard if _heard is not None else _rng).random() < 0.60:" in src
        head = src.index("_heard = None")
        assert "if lord == player:" in src[head:head + 120]


class TestTheProseStaysOnTheAmbientStream:
    """Ruled as designed (the row's last sentence): which line is quoted is
    display only. Every OTHER draw of these modules goes through a stream
    that may be the campaign's."""

    FILES = [
        "backend/commands/objection_v2.py", "backend/commands/defiance.py",
        "backend/commands/severity.py", "backend/commands/diplomatic_defiance.py",
        "backend/commands/disobedience.py", "backend/commands/meta_executor.py",
        "backend/commands/strategic_executor.py", "backend/commands/executor.py",
        "backend/commands/diplomatic_executor.py", "backend/game_logic/diplomacy.py",
        "backend/game_logic/jealousy.py", "backend/game_logic/vassal.py",
    ]
    RULED = {
        ("backend/commands/defiance.py", "get_berthier_defiance_text", "choice"),
        ("backend/commands/disobedience.py", "_generate_objection_message", "choice"),
    }

    def test_the_only_bare_ambient_draws_left_are_the_prose(self):
        bare = set()
        for file in self.FILES:
            tree = ast.parse((REPO / file).read_text(encoding="utf-8"))
            for fn in ast.walk(tree):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for node in ast.walk(fn):
                    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                            and isinstance(node.func.value, ast.Name)
                            and node.func.value.id in ("random", "_rng", "_random")):
                        bare.add((file, fn.name, node.func.attr))
        # A nested function reports under its parents too: keep the innermost.
        assert {b for b in bare if b in self.RULED} == self.RULED
        strays = {b for b in bare if b not in self.RULED
                  and (b[0], b[2]) not in {(r[0], r[2]) for r in self.RULED}}
        assert not strays, f"a temper draw is back on the module `random`: {sorted(strays)}"

    def test_berthiers_line_is_not_the_campaigns(self, stream_names):
        world = _board()
        del stream_names[:]
        text = DEF.get_berthier_defiance_text("right", "Davout", "fortified instead")
        assert isinstance(text, str) and text
        assert not stream_names
        assert world.campaign_seed == ROLLED
