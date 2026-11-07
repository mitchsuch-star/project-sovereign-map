"""T0-E "the sibling sweep of FA-N72" — the fifth slice of Tier 0 of the
November 6, 2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md`
§4.1 #3, #4, #5; `BUG_FIXES.md` §GR GR-35, GR-36, GR-1, GR-37; the rules
`SYSTEMS_REFERENCE.md` §182).

GR-35 (filed P2) — P3.9's jealousy glory hunt read neither the pair brake nor
the futility counter: one corps attacked the same man twice a phase, every
phase. It routes its one candidate through `_engageable_enemies` now (seam
`p39_reads_the_brakes`).
GR-36 — P4.25's garrison storm had no pair read: the same garrison stormed
2-3 times a phase. It reads the pair stamp (written for region targets since
FA-N72) now (seam `storms_read_the_pair`). The futility counter never keys a
garrison — an escalade emits no "battle" event (CA8-19) — pinned here.
GR-1 — the stagnation breaker's surrounded arm (and its in-arm sibling, the
turn-3+ lowered threshold) ignored the same brakes: Deroy on Bennigsen three
times in one phase. Both arms route through `_engageable_enemies` now (seam
`desperation_reads_the_brakes`).
GR-37 — `_muster_price` swallows a failure into 0 after one deduplicated
report. The errors tally is surfaced where the sweeps read it (the driver's
`errors_tally` in meta.json + the FAULTS lines, lever
`THE_DIGEST_HEARS_THE_FAULTS`), and a clean enemy evaluation reports nothing.
"""
from __future__ import annotations

import contextlib
import io
import inspect
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend import errors as _errors  # noqa: E402
from backend.ai import enemy_ai as ea  # noqa: E402
from backend.ai.enemy_ai import EnemyAI  # noqa: E402
from backend.commands.executor import CommandExecutor  # noqa: E402
from backend.commands.strategic import ATTACK_FUTILITY_LIMIT  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _war(world, a, b):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _park_everyone(world, keep, spot="Paris"):
    for m in world.marshals.values():
        if m.name not in keep:
            m.location = spot
            m.strength = max(int(m.strength), 1000)


def _jealous_hunt(adjacent=True):
    """Wellington (Britain, made aggressive and jealous) with Ney (France)
    in reach on the legacy fixture — P3.9's exact gates, P0 not engaged
    (different region), P4 ranged rungs behind it."""
    world = WorldState(player_nation="France")
    wel = world.get_marshal("Wellington")
    ney = world.get_marshal("Ney")
    wel.location = "Waterloo"
    wel.strength = 30000
    wel.personality = "aggressive"
    wel.jealous_of = "Blucher"
    adj = world.get_region("Waterloo").adjacent_regions[0]
    ney.location = adj if adjacent else "Waterloo"
    ney.strength = 4000
    _park_everyone(world, ("Wellington", "Ney"))
    _war(world, "France", "Britain")
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    ai = EnemyAI(CommandExecutor())
    ai._attacked_targets_this_turn = set()
    return world, ai, wel, ney


class TestP39ReadsTheBrakes:
    """GR-35."""

    def test_the_hunt_stands_when_the_brakes_clear(self):
        world, ai, wel, ney = _jealous_hunt()
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"}, action
        assert prio == 4

    def test_a_pair_already_attacked_this_phase_is_dropped(self):
        world, ai, wel, ney = _jealous_hunt()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_futility_at_the_limit_drops_the_hunt(self):
        world, ai, wel, ney = _jealous_hunt()
        world.ai_attack_futility["Wellington:Ney"] = ATTACK_FUTILITY_LIMIT
        with _quiet():
            action, _prio = ai._evaluate_marshal(wel, "Britain", world)
        assert not (action and action.get("action") == "attack"
                    and action.get("target") == "Ney"), action

    def test_below_the_limit_the_hunt_stands(self):
        world, ai, wel, ney = _jealous_hunt()
        world.ai_attack_futility["Wellington:Ney"] = ATTACK_FUTILITY_LIMIT - 1
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"} and prio == 4

    def test_the_seam_down_restores_the_unbraked_hunt(self, monkeypatch):
        """The attribution control: `p39_reads_the_brakes` held down, the
        stamped pair is hunted again — the pre-fix reading."""
        world, ai, wel, ney = _jealous_hunt()
        ai._attacked_targets_this_turn = {("Wellington", "Ney")}
        monkeypatch.setattr(ea, "p39_reads_the_brakes", lambda: False)
        with _quiet():
            action, prio = ai._evaluate_marshal(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": "Ney"} and prio == 4


def _garrison_board():
    """Wellington (Britain) beside a French-held garrison region on the
    legacy fixture: P4.25's finder alone, no field army in the target."""
    world = WorldState(player_nation="France")
    wel = world.get_marshal("Wellington")
    wel.location = "Waterloo"
    wel.strength = 30000
    wel.personality = "cautious"
    adj = world.get_region("Waterloo").adjacent_regions[0]
    tgt = world.get_region(adj)
    tgt.controller = "France"
    tgt.garrison_strength = 8000
    _park_everyone(world, ("Wellington",))
    _war(world, "France", "Britain")
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    ai = EnemyAI(CommandExecutor())
    ai._attacked_targets_this_turn = set()
    return world, ai, wel, adj


class TestTheStormReadsThePair:
    """GR-36."""

    def test_the_first_storm_stands(self):
        world, ai, wel, adj = _garrison_board()
        with _quiet():
            action = ai._find_garrison_attack(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": adj}, action

    def test_one_storm_per_pair_per_phase(self):
        world, ai, wel, adj = _garrison_board()
        ai._attacked_targets_this_turn = {("Wellington", adj)}
        with _quiet():
            action = ai._find_garrison_attack(wel, "Britain", world)
        assert action is None, action

    def test_another_corps_may_still_storm_it(self):
        """The brake is the PAIR's, not the garrison's — a second corps of
        the court may still assault the same walls this phase."""
        world, ai, wel, adj = _garrison_board()
        ai._attacked_targets_this_turn = {("Moore", adj)}
        with _quiet():
            action = ai._find_garrison_attack(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": adj}

    def test_the_seam_down_restores_the_second_storm(self, monkeypatch):
        world, ai, wel, adj = _garrison_board()
        ai._attacked_targets_this_turn = {("Wellington", adj)}
        monkeypatch.setattr(ea, "storms_read_the_pair", lambda: False)
        with _quiet():
            action = ai._find_garrison_attack(wel, "Britain", world)
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": adj}

    def test_an_escalade_emits_no_battle_event(self):
        """The docstring's claim pinned: garrison combat is a separate
        resolver (CA8-19) whose events carry no `type == "battle"` row, so
        the futility counter — keyed off battle events — never keys a
        garrison. The pair brake is the live half of this sweep here."""
        world, ai, wel, adj = _garrison_board()
        executor = CommandExecutor()
        with _quiet():
            result = executor._combat._resolve_garrison_combat(
                wel, world.get_region(adj), world, {"world": world})
        events = result.get("events") or []
        assert events, "the escalade reports its events"
        assert all(e.get("type") != "battle" for e in events), events


def _surrounded(stamped=(), futile=(), hostiles_per_adj=1):
    """Wellington (Britain) with every adjacent region held by France and a
    French corps standing in each — no move stands, the breaker's surrounded
    arm is the last resort; the weakest neighbor is Ney."""
    world = WorldState(player_nation="France")
    wel = world.get_marshal("Wellington")
    wel.location = "Waterloo"
    wel.strength = 30000
    wel.personality = "aggressive"
    adjacents = list(world.get_region("Waterloo").adjacent_regions)
    french = [m for m in world.marshals.values()
              if m.nation == "France"]
    assert len(french) >= len(adjacents), (len(french), adjacents)
    _park_everyone(world, ("Wellington",), spot="Paris")
    strength = 6000
    placed = []
    for adj, m in zip(adjacents, french):
        region = world.get_region(adj)
        region.controller = "France"
        m.location = adj
        m.strength = strength
        strength += 2000
        placed.append(m)
    _war(world, "France", "Britain")
    world.invalidate_active_nations_cache()
    world._build_marshal_index()
    ai = EnemyAI(CommandExecutor())
    ai._attacked_targets_this_turn = {("Wellington", name) for name in stamped}
    for name in futile:
        world.ai_attack_futility[f"Wellington:{name}"] = ATTACK_FUTILITY_LIMIT
    return world, ai, wel, placed


class TestDesperationReadsTheBrakes:
    """GR-1 and its in-arm sibling."""

    def test_the_desperate_strike_picks_the_weakest(self):
        world, ai, wel, placed = _surrounded()
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3,
                                               "aggressive")
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": placed[0].name}, action

    def test_a_stamped_pair_falls_to_the_next_weakest(self):
        world, ai, wel, placed = _surrounded()
        ai._attacked_targets_this_turn = {("Wellington", placed[0].name)}
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3,
                                               "aggressive")
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": placed[1].name}, action

    def test_every_pair_braked_the_breaker_waits(self):
        """Both arms — the surrounded strike AND the lowered threshold —
        drop every braked pair; the breaker ends at `wait`, visible to the
        stagnation tracker, instead of Deroy's third assault."""
        world, ai, wel, placed = _surrounded()
        ai._attacked_targets_this_turn = {
            ("Wellington", m.name) for m in placed}
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3,
                                               "aggressive")
        assert action == {"marshal": "Wellington", "action": "wait"}, action

    def test_futility_at_the_limit_is_dropped_too(self):
        world, ai, wel, placed = _surrounded()
        for m in placed:
            world.ai_attack_futility[f"Wellington:{m.name}"] = (
                ATTACK_FUTILITY_LIMIT)
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3,
                                               "aggressive")
        assert action == {"marshal": "Wellington", "action": "wait"}, action

    def test_the_seam_down_restores_the_repeat(self, monkeypatch):
        world, ai, wel, placed = _surrounded()
        ai._attacked_targets_this_turn = {
            ("Wellington", m.name) for m in placed}
        monkeypatch.setattr(ea, "desperation_reads_the_brakes",
                            lambda: False)
        with _quiet():
            action = ai._get_stagnation_action(wel, "Britain", world, 3,
                                               "aggressive")
        assert action == {"marshal": "Wellington", "action": "attack",
                          "target": placed[0].name}, action

    def test_the_lead_bar_still_stands_beside_the_brakes(self):
        """T0-D's `_lead_barred_from_field` read survives the routing —
        the surrounded arm keeps both reads (source pin)."""
        src = inspect.getsource(EnemyAI._get_stagnation_action)
        assert "_lead_barred_from_field" in src
        assert src.count("_engageable_enemies") == 2, (
            "both attack arms route through the one filter")


class TestTheFaultsAreCounted:
    """GR-37."""

    def test_a_clean_evaluation_reports_no_fault(self):
        _errors.reset_tally()
        world, ai, wel, ney = _jealous_hunt()
        with _quiet():
            ai._evaluate_marshal(wel, "Britain", world)
            ai._muster_price(ney, "Britain", world)
        sites = {row["site"] for row in _errors.tally()}
        assert not {s for s in sites if s.startswith("enemy_ai.")}, sites

    def test_a_broken_muster_is_counted_every_call(self, monkeypatch):
        """`report` logs once per site and COUNTS every call — the tally is
        the surface the sweeps read; the price itself stays 0 (the
        review's PLAUSIBLE row: behavior unchanged, silence cured)."""
        _errors.reset_tally()
        world, ai, wel, ney = _jealous_hunt()
        combat = ai.executor._combat

        def _broken(self_, *a, **k):
            raise RuntimeError("the muster broke")

        monkeypatch.setattr(type(combat), "_defender_muster", _broken)
        with _quiet():
            assert ai._muster_price(ney, "Britain", world) == 0
            assert ai._muster_price(ney, "Britain", world) == 0
        rows = [r for r in _errors.tally()
                if r["site"].startswith("enemy_ai.EnemyAI._muster_price")]
        assert rows and rows[0]["count"] == 2, rows

    def test_the_digest_hears_the_faults(self, tmp_path):
        """The driver's close reads the tally in-process: meta.json carries
        `errors_tally` (empty = measured clean) and the markdown names each
        site that reported."""
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        _errors.reset_tally()
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock",
                                  "transport": "in-process", "policy": {}})
        try:
            raise RuntimeError("a staged fault")
        except RuntimeError as exc:
            _errors.report(exc, "enemy_ai.EnemyAI._muster_price: staged")
        d.finish("done")
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        tally = meta.get("errors_tally")
        assert tally and tally[0]["site"].startswith(
            "enemy_ai.EnemyAI._muster_price")
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "FAULTS: enemy_ai.EnemyAI._muster_price" in md
        _errors.reset_tally()

    def test_measured_clean_is_an_empty_list_not_absence(self, tmp_path):
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        _errors.reset_tally()
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock",
                                  "transport": "in-process", "policy": {}})
        d.finish("done")
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        assert meta.get("errors_tally") == []
        assert "FAULTS:" not in (tmp_path / "digest.md").read_text(
            encoding="utf-8")

    def test_the_run_boot_resets_the_tally(self):
        """The slice's own review fleet found the leak: the tally is
        PROCESS-global, so a second in-process run in one process would
        report the first run's faults as its own. The in-process boot
        resets it, after the backend import — "empty = measured clean"
        holds per RUN."""
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        src = inspect.getsource(drv.make_inprocess_transport)
        assert "reset_tally()" in src
        assert src.index("import backend.main") < src.index("reset_tally()")

    def test_a_live_run_does_not_pretend_to_measure(self, tmp_path):
        """Mode B's backend is another process — the driver's own tally
        would read clean whatever the server suffered, so the key is
        ABSENT, never a false clean."""
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        _errors.reset_tally()
        try:
            raise RuntimeError("a staged fault")
        except RuntimeError as exc:
            _errors.report(exc, "enemy_ai.EnemyAI._muster_price: staged")
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock",
                                  "transport": "live", "policy": {}})
        d.finish("done")
        meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        assert "errors_tally" not in meta
        _errors.reset_tally()
