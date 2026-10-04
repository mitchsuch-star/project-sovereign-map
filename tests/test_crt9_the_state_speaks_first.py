"""CRT-9 "The state speaks first" — the client half: CQ-21 and CQ-24
(SCORE_FINISH_SPEC.md §3 Step 4, Chunk 3b trimmed to what the census
confirms; COMMAND_ROBUSTNESS_SPEC.md §12.3 row 9 and §12.16; rules
SYSTEMS_REFERENCE.md §89; rows BUG_FIXES.md CQ-21, CQ-24).

ONE pure probe (`backend.commands.state_probe`) answers "would this order be
refused for the marshal's STATE or for the action it costs?" in the order the
executor meets its gates; the payload ships its short reasons
(`tactical_state.order_refusals`, the Generals cards' `order_refusals`, the
turn's `action_pools`) and the region panel, the Generals screen and the
completer read them.

THE CENSUS (below) is what makes the probe trustworthy: for every staged
state — fortified, drill-locked, recovering from a retreat, broken, acting
on his own authority, no action left, one action left, no administrative
action left — and every verb the screens offer, the command is sent through
the real `POST /command` on a fresh 1805 boot: a verb the probe refuses is
refused at no cost, and a verb the probe passes is never answered by a state
or pool refusal. The driven client censuses ride the CX-R2 and CN-4 files
(the completer's state exemption deleted; the chips at zero actions).
"""

import re

import pytest
from fastapi.testclient import TestClient

import backend.commands.state_probe as SP
import backend.main as M
from backend.commands.parser import CommandParser
from backend.models.marshal import Stance


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _fresh(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


# ── the states, staged on Davout (cautious, Rhineland, Mack next door) ──────
def _fortified(w):
    d = w.get_marshal("Davout")
    d.fortified, d.stance, d.defense_bonus = True, Stance.DEFENSIVE, 0.10


def _drill_locked(w):
    d = w.get_marshal("Davout")
    d.drilling, d.drilling_locked = True, True
    d.drill_complete_turn = int(w.current_turn) + 1


def _retreating(w):
    d = w.get_marshal("Davout")
    d.retreating, d.retreat_recovery = True, 1


def _broken(w):
    d = w.get_marshal("Davout")
    d.broken, d.broken_recovery = True, 1


def _autonomous(w):
    d = w.get_marshal("Davout")
    d.autonomous, d.autonomy_turns = True, 2


def _no_military(w):
    w.actions_remaining = 0


def _one_military(w):
    w.actions_remaining = 1


def _no_admin(w):
    w.admin_actions_remaining = 0


def _counter_punch_at_zero(w):
    """The counter-punch waiver: the free strike stands at zero actions."""
    d = w.get_marshal("Davout")
    d.counter_punch_available, d.counter_punch_turns = True, 1
    w.actions_remaining = 0


STATES = {
    "fresh": lambda w: None,
    "fortified": _fortified,
    "drill_locked": _drill_locked,
    "retreating": _retreating,
    "broken": _broken,
    "autonomous": _autonomous,
    "no_military": _no_military,
    "one_military": _one_military,
    "no_admin": _no_admin,
    "counter_punch_at_zero": _counter_punch_at_zero,
}

COMMANDS = {
    "attack": "Davout, attack Mack",
    "scout": "Davout, scout Swabia",
    "fortify": "Davout, fortify",
    "unfortify": "Davout, unfortify",
    "drill": "Davout, drill",
    "defend": "Davout, defend",
    "move": "Davout, move to Lorraine",
    "march": "Davout, march to Paris",
    "pursue": "Davout, pursue Mack",
    "hold": "Davout, hold",
    "support": "Davout, support Ney",
    "retreat": "Davout, retreat",
}

# The sentences only a STATE or POOL refusal speaks — an "open" verb must
# never be answered by one of these.
_STATE_SENTENCES = re.compile(
    r"Not enough actions|No administrative actions remaining|locked in drill|"
    r"is fortified at|cannot march from his works|recovering from retreat|"
    r"\bBROKEN\b|army is broken|acting independently|is securing", re.I)


def _davout(world):
    d = world.get_marshal("Davout")
    order = getattr(d, "strategic_order", None)
    return (d.location, int(d.strength), bool(getattr(d, "fortified", False)),
            bool(getattr(d, "drilling", False)), str(getattr(d, "stance", "")),
            (order.command_type, order.target) if order else None)


def _spend(world):
    return (int(world.actions_remaining), int(world.admin_actions_remaining),
            int(world.gold))


CASES = [(s, v) for s in STATES for v in COMMANDS]


class TestTheProbeAgreesWithTheExecutor:

    @pytest.mark.parametrize("state,verb", CASES)
    def test_the_probe_refuses_exactly_what_the_executor_refuses(
            self, monkeypatch, state, verb):
        client, world = _fresh(monkeypatch)
        STATES[state](world)
        davout = world.get_marshal("Davout")
        probe = SP.order_state_refusal(world, davout, verb)
        before = (_davout(world), _spend(world))
        reply = client.post("/command", json={"command": COMMANDS[verb]}).json()
        message = str(reply.get("message") or "")
        if probe:
            # refused, and for nothing — no action, no gold, no state moved
            assert (_davout(M.world), _spend(M.world)) == before, (state, verb, message)
            assert not reply.get("battle_report"), (state, verb)
            assert reply.get("success") is not True or reply.get("objection") is None, (
                state, verb, message)
        else:
            assert not _STATE_SENTENCES.search(message), (state, verb, probe, message)

    def test_the_counter_punch_strike_stands_at_zero(self, shipped):
        """The waiver mirrored: at zero actions a man with a counter-punch
        in hand is offered his strike and nothing else."""
        _client, world = shipped
        _counter_punch_at_zero(world)
        closed = SP.order_refusals(world, world.get_marshal("Davout"))
        assert "attack" not in closed and closed.get("scout") == "no military action left this turn"

    def test_every_state_refuses_something_and_the_fresh_board_little(self, shipped):
        """The census is not vacuous: each staged state closes at least one
        verb, and a fresh Davout is closed only by his own gates."""
        _client, world = shipped
        for state, stage in STATES.items():
            M._reset_world_state()
            stage(M.world)
            closed = SP.order_refusals(M.world, M.world.get_marshal("Davout"))
            if state in ("fresh", "no_admin"):
                assert set(closed) <= {"unfortify", "drill", "defend", "land"}, (state, closed)
            else:
                assert closed, state


class TestThePayloadCarriesIt:

    def test_every_player_marshal_ships_the_map(self, shipped):
        _client, world = shipped
        world.get_marshal("Davout").fortified = True
        summary = world.get_filtered_game_state_summary()
        seen = {}
        for region in summary["map_data"].values():
            for m in region.get("marshals", []):
                tactical = m.get("tactical_state")
                if isinstance(tactical, dict):
                    seen[m["name"]] = tactical.get("order_refusals")
        assert "Davout" in seen and isinstance(seen["Davout"], dict)
        assert seen["Davout"].get("move") == "fortified — unfortify first"
        assert seen["Davout"].get("attack") == "fortified — unfortify first"
        assert "unfortify" not in seen["Davout"]

    def test_the_pools_ride_the_summary(self, shipped):
        _client, world = shipped
        world.actions_remaining, world.admin_actions_remaining = 1, 0
        assert world.get_filtered_game_state_summary()["action_pools"] == {
            "military": 1, "admin": 0}

    def test_the_generals_cards_carry_it(self, shipped):
        client, world = shipped
        world.actions_remaining = 0
        data = client.get("/marshal_overview").json()
        assert data["action_pools"]["military"] == 0
        card = next(c for c in data["marshals"] if c["name"] == "Davout")
        assert card["order_refusals"]["fortify"] == "no military action left this turn"

    def test_no_enemy_marshal_ships_it(self, shipped):
        _client, world = shipped
        summary = world.get_filtered_game_state_summary()
        for region in summary["map_data"].values():
            for m in region.get("marshals", []):
                if m.get("nation") and m.get("nation") != world.player_nation:
                    assert "order_refusals" not in (m.get("tactical_state") or {}), m["name"]

    def test_the_landing_chip_carries_its_refusal(self, shipped):
        _client, world = shipped
        from backend.game_logic import naval
        yards = naval.controlled_dockyards(world, "France")
        lannes = world.get_marshal("Lannes")
        lannes.strength, lannes.location = 12000, yards[0]
        world.actions_remaining = 1
        options = naval.expedition_landing_options(world, "France")
        rows = [row for rows in options.values() for row in rows
                if row["marshal"] == "Lannes"]
        assert rows and all(row.get("refusal") == "needs 2 actions — 1 left" for row in rows)
        world.actions_remaining = 4
        options = naval.expedition_landing_options(world, "France")
        assert all("refusal" not in row for rows in options.values() for row in rows
                   if row["marshal"] == "Lannes")


class TestTheLever:

    def test_the_lever_down_ships_an_empty_map(self, shipped, monkeypatch):
        _client, world = shipped
        world.actions_remaining = 0
        monkeypatch.setattr(SP, "THE_SCREEN_READS_THE_STATE", False)
        assert SP.order_refusals(world, world.get_marshal("Davout")) == {}

    def test_an_enemy_marshal_gets_no_map(self, shipped):
        _client, world = shipped
        world.actions_remaining = 0
        assert SP.order_refusals(world, world.get_marshal("Mack")) == {}
