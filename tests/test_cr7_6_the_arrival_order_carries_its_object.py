"""CR-7-6 — "The arrival order carries its object" (kill-gated FIRST).

Build contract: `docs/audits/COMPOUND_CONDITIONAL_COMMANDS_2026_09_20.md`
§CR-7-6. THE KILL GATE WAS RUN BEFORE A LINE WAS WRITTEN (September 22,
2026): the arrival attack fires deterministically on the player path at the
FIRST-STEP seam — with Mack AND Archduke Charles staged at Swabia and an
aggressive Ney (250,000 men, favourable odds) ordered `march to Swabia then
attack Archduke Charles`, the strategic attack issued was against MACK
(`enemies[0]`); at unfavourable odds the interrupt named Mack. The named
quarry survived nowhere: `attack_on_arrival` was a bare bool. (The
`_handle_move_to_arrival` branch itself was NOT observed firing in the
ambient world — a cannon-fire redirect intervened on every multi-turn
probe — so it is pinned by a direct call below and named as the belt.)

Built: `StrategicOrder.arrival_target` (a DECLARED dataclass field, nested
in the marshal dict, legacy saves load by construction), set from the
parse (`strategic_parser._extract_arrival_target`), carried through BOTH
construction sites (the 12-kwarg objection-resume rebuild included), and
read by ONE helper at the three seams that pick a contact enemy
(`strategic.pick_contact_enemy`).
"""

import pathlib
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
import backend.commands.strategic as strategic_mod
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser
from backend.commands.strategic import StrategicOrderProcessor, pick_contact_enemy
from backend.models.marshal import StrategicOrder


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


@pytest.fixture
def attack_spy(monkeypatch):
    # A class-level patch is blind to the singleton the moment ANY earlier
    # test has monkeypatched `execute` on the INSTANCE: pytest's undo of an
    # instance-level setattr writes the captured bound method back as an
    # instance attribute, which shadows the class for the rest of the
    # session (measured September 22, 2026 — three pins here went red in
    # the full suite and green alone). Name the cause instead of reporting
    # an empty list.
    shadow = [name for name in ("execute",) if name in vars(M.executor)]
    assert not shadow, (
        "an earlier test left an instance-level %s on the executor singleton "
        "— patch the CLASS (type(M.executor)), never the instance" % shadow)
    calls = []
    original = CommandExecutor.execute

    def spy(self, parsed, game_state, *args, **kwargs):
        command = (parsed or {}).get("command") or {}
        if command.get("action") == "attack" and command.get("_strategic_execution"):
            calls.append((command.get("marshal"), command.get("target")))
        return original(self, parsed, game_state, *args, **kwargs)

    monkeypatch.setattr(CommandExecutor, "execute", spy)
    return calls


def run(shipped, command):
    client, _world = shipped
    return client.post("/command", json={"command": command}).json()


def stage_two_enemies(world):
    world.get_marshal("ArchdukeCharles").location = "Swabia"
    names = [e.name for e in world.get_enemies_in_region("Swabia", "France")]
    assert names[0] == "Mack" and "ArchdukeCharles" in names, names


class TestTheKillGateProbeAsAPin:

    def test_the_named_man_is_the_one_engaged_at_the_first_step(self, shipped, attack_spy):
        _client, world = shipped
        stage_two_enemies(world)
        world.get_marshal("Ney").strength = 250000
        reply = run(shipped, "Ney, march to Swabia then attack Archduke Charles")
        assert reply.get("battle_report"), reply.get("message")
        assert attack_spy == [("Ney", "ArchdukeCharles")], attack_spy

    def test_the_control_without_an_object_engages_the_first(self, shipped, attack_spy):
        _client, world = shipped
        stage_two_enemies(world)
        world.get_marshal("Ney").strength = 250000
        run(shipped, "Ney, march to Swabia then attack")
        assert attack_spy == [("Ney", "Mack")], attack_spy

    def test_the_bad_odds_question_names_the_man(self, shipped):
        _client, world = shipped
        stage_two_enemies(world)
        reply = run(shipped, "Ney, march to Swabia then attack Archduke Charles")
        assert reply.get("pending_interrupt"), reply.get("message")
        assert reply["pending_interrupt"]["enemy"] == "ArchdukeCharles"
        assert "Archduke Charles" in reply["message"] or "ArchdukeCharles" in reply["message"]

    def test_the_order_carries_the_object(self, shipped):
        _client, world = shipped
        stage_two_enemies(world)
        run(shipped, "Ney, march to Swabia then attack Archduke Charles")
        order = M.world.get_marshal("Ney").strategic_order
        assert order is not None and order.attack_on_arrival is True
        assert order.arrival_target == "ArchdukeCharles"


class TestTheOtherTwoSeams:

    def _order(self, marshal, target, arrival_target):
        return StrategicOrder(
            command_type="MOVE_TO", target=target, target_type="region",
            started_turn=1, original_command="probe", path=[],
            attack_on_arrival=True, arrival_target=arrival_target,
            issued_turn=0)

    def test_the_arrival_handler_prefers_the_named_man(self, shipped, attack_spy):
        _client, world = shipped
        stage_two_enemies(world)
        ney = world.get_marshal("Ney")
        ney.location = "Swabia"
        ney.strength = 250000
        ney.strategic_order = self._order(ney, "Swabia", "ArchdukeCharles")
        processor = StrategicOrderProcessor(M.executor)
        processor._handle_move_to_arrival(ney, world, M.game_state)
        assert attack_spy and attack_spy[-1] == ("Ney", "ArchdukeCharles"), attack_spy

    def test_the_mid_path_blocked_seam_names_the_named_man(self, shipped):
        _client, world = shipped
        stage_two_enemies(world)
        davout = world.get_marshal("Davout")           # cautious: asks, never fights
        davout.strategic_order = self._order(davout, "Swabia", "ArchdukeCharles")
        processor = StrategicOrderProcessor(M.executor)
        enemies = world.get_enemies_in_region("Swabia", "France")
        result = processor._handle_blocked_path(davout, enemies, "Swabia", world, M.game_state)
        assert result.get("enemy") == "ArchdukeCharles", result

    def test_pick_contact_enemy(self, shipped):
        _client, world = shipped
        stage_two_enemies(world)
        enemies = world.get_enemies_in_region("Swabia", "France")
        named = StrategicOrder(command_type="MOVE_TO", target="Swabia", target_type="region",
                               started_turn=1, original_command="p", arrival_target="ArchdukeCharles")
        elsewhere = StrategicOrder(command_type="MOVE_TO", target="Swabia", target_type="region",
                                   started_turn=1, original_command="p", arrival_target="Kutuzov")
        assert pick_contact_enemy(named, enemies).name == "ArchdukeCharles"
        assert pick_contact_enemy(elsewhere, enemies).name == "Mack"
        assert pick_contact_enemy(None, enemies).name == "Mack"
        assert pick_contact_enemy(named, []) is None

    def test_the_three_seams_read_the_one_helper(self):
        """A census, not a hope: no `enemies[0]` pick survives at the three
        contact seams."""
        import inspect
        import backend.commands.strategic_executor as se
        for func in (strategic_mod.StrategicOrderProcessor._handle_move_to_arrival,
                     strategic_mod.StrategicOrderProcessor._handle_blocked_path,
                     se.StrategicExecutor._handle_first_step_blocked):
            src = inspect.getsource(func)
            assert "pick_contact_enemy(" in src, func.__name__
            head = src[:src.index("pick_contact_enemy(")]
            assert "enemies[0]" not in head, func.__name__


class TestTheParseAndTheRecord:

    @pytest.mark.parametrize("text,expected", [
        ("Ney, march to Swabia then attack Archduke Charles", "ArchdukeCharles"),
        ("Ney, march to Swabia then attack Mack", "Mack"),
        ("Ney, march to Swabia, attack Mack", "Mack"),
        ("Ney, march to Swabia then attack", None),
        ("Ney, march to Swabia then attack the Austrians", None),
        ("Ney, march to Swabia then attack Davout", None),      # one of ours
        ("Ney, march to Swabia then attack Zorglub", None),
    ])
    def test_the_object_is_parsed_or_left_empty(self, shipped, text, expected):
        got = M.parser.parse(text, M.get_llm_game_state(), world=M.world)
        assert got.get("attack_on_arrival") is True
        assert got.get("arrival_target") == expected

    def test_it_round_trips(self):
        order = StrategicOrder(command_type="MOVE_TO", target="Swabia", target_type="region",
                               started_turn=1, original_command="p",
                               attack_on_arrival=True, arrival_target="ArchdukeCharles")
        data = order.to_dict()
        assert data["arrival_target"] == "ArchdukeCharles"
        assert StrategicOrder.from_dict(data).arrival_target == "ArchdukeCharles"

    def test_a_legacy_save_loads_and_still_fights(self, shipped):
        legacy = {"command_type": "MOVE_TO", "target": "Swabia", "target_type": "region",
                  "started_turn": 1, "original_command": "p", "attack_on_arrival": True}
        order = StrategicOrder.from_dict(legacy)
        assert order.arrival_target is None and order.attack_on_arrival is True
        _client, world = shipped
        enemies = world.get_enemies_in_region("Swabia", "France")
        assert pick_contact_enemy(order, enemies).name == "Mack"

    @pytest.mark.parametrize("answer", ["compromise", "insist"])
    def test_the_objection_resume_rebuild_keeps_it(self, shipped, monkeypatch, answer):
        """The 12-kwarg rebuild at the strategic-objection answer used to eat
        every kwarg it did not name. It is the COMPROMISE arm that builds
        through the rebuild (`insist` re-executes the original order through
        the primary site) — the sweep found an insist-only pin inert."""
        import backend.commands.objection_v2 as objection_v2
        monkeypatch.setattr(objection_v2.random, "random", lambda: 0.5)
        client, world = shipped
        stage_two_enemies(world)
        first = run(shipped, "Davout, march to Swabia then attack Archduke Charles")
        assert first.get("pending_objection"), first.get("message")
        options = {o.get("type") for o in (first.get("objection") or {}).get("options", [])}
        assert "compromise" in options, options
        client.post("/respond_to_objection", json={"choice": answer}).json()
        order = M.world.get_marshal("Davout").strategic_order
        assert order is not None, f"the {answer} order was not created"
        assert order.arrival_target == "ArchdukeCharles"

    def test_the_serialization_census_sees_the_field(self):
        from dataclasses import fields
        assert "arrival_target" in {f.name for f in fields(StrategicOrder)}
        assert "arrival_target" in StrategicOrder(
            command_type="MOVE_TO", target="x", target_type="region",
            started_turn=1, original_command="p").to_dict()


# ═══════════════════════════════════════════════════════════════════════════
# Suite hygiene — found by this file's own pins going red in the full run
# ═══════════════════════════════════════════════════════════════════════════

_INSTANCE_PATCH_RE = re.compile(
    r"""monkeypatch\.setattr\(\s*(?:m|M|main|main_module|m_mod|backend\.main)"""
    r"""\.((?:executor|parser)(?:\.[A-Za-z_]\w*)*)\s*,\s*["']([A-Za-z_]\w*)["']""")


def _resolve_singleton(chain):
    obj = M
    for part in chain.split("."):
        obj = getattr(obj, part)
    return obj


def _instance_patch_leaves_a_shadow(chain, name):
    """True when `name` is NOT an instance attribute of the resolved singleton —
    i.e. it is served by the class or by `CommandExecutor.__getattr__` (the
    delegated names such as `_execute_cancel` are NOT instance attributes:
    `getattr` returns the sub-executor's bound method, and pytest's undo writes
    it back onto the instance as a shadow). A REAL instance attribute
    (`_combat`, `_strategic`, the parser's `llm`) is restored cleanly and is
    exempt. A delegated name is patched on the SUB-executor's class."""
    try:
        obj = _resolve_singleton(chain)
    except AttributeError:
        return True
    return name not in vars(obj)


class TestNoTestPatchesAMethodOnASingletonInstance:
    """`monkeypatch.setattr(<instance>, "<method>", …)` on a process-lifetime
    singleton (`backend.main.executor`, its sub-executors, `backend.main.parser`)
    is a session-wide pollutant: pytest records `getattr(instance, name)` —
    the BOUND method — and its undo writes that bound method back as an
    INSTANCE attribute, so every later class-level patch of the same method
    is silently bypassed for the singleton. `test_command_robustness_cr5b`
    did exactly that to `execute`, and the three spy pins above measured an
    empty call list under a battle that plainly happened. The rule: patch
    `type(obj)`; the class-level undo restores through `__dict__` cleanly.
    This census reads the direct forms under the module aliases the suite
    uses; the session-end guard in `tests/conftest.py` is the NET — it caught
    two more sites under a fourth alias on the hook's second full run."""

    def test_the_mechanism_is_real(self):
        from _pytest.monkeypatch import MonkeyPatch

        class K:
            def method(self):
                return "real"

        k = K()
        mp = MonkeyPatch()
        mp.setattr(k, "method", lambda *a, **kw: "stub")
        mp.undo()
        assert "method" in vars(k), "the leftover this census exists for"
        mp2 = MonkeyPatch()
        mp2.setattr(K, "method", lambda self: "class-level patch")
        try:
            assert k.method() == "real", "the class-level patch is blinded"
        finally:
            mp2.undo()
        # The class-level shape leaves nothing behind.
        k2 = K()
        mp3 = MonkeyPatch()
        mp3.setattr(type(k2), "method", lambda self: "stub")
        mp3.undo()
        assert "method" not in vars(k2) and k2.method() == "real"

    def test_no_test_file_patches_a_singleton_instance(self):
        offenders = []
        for path in sorted(pathlib.Path(__file__).parent.glob("test_*.py")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                hit = _INSTANCE_PATCH_RE.search(line)
                if hit and _instance_patch_leaves_a_shadow(hit.group(1), hit.group(2)):
                    offenders.append(f"{path.name}:{lineno}: {line.strip()}")
        assert offenders == [], "\n".join(offenders)

    def test_the_census_can_see_an_offender(self):
        # The example lines are split so this file's own scan cannot read
        # them as offenders; the regex sees the joined string.
        bad = 'monkeypatch.setattr(' + 'M.executor, "execute", spy)'
        hit = _INSTANCE_PATCH_RE.search(bad)
        assert hit and hit.group(1) == "executor" and hit.group(2) == "execute"
        assert _instance_patch_leaves_a_shadow("executor", "execute")
        sub = 'monkeypatch.setattr(' + 'main_module.executor._combat, "_calculate_reinforcements", f)'
        hit = _INSTANCE_PATCH_RE.search(sub)
        assert hit and hit.group(1) == "executor._combat"
        assert _instance_patch_leaves_a_shadow("executor._combat", "_calculate_reinforcements")
        # The exemption is real: a genuine instance attribute is restored
        # cleanly by an instance-level undo, and the census lets it through —
        # while a __getattr__-delegated name is flagged (it is not in vars()).
        assert "_combat" in vars(M.executor)
        assert not _instance_patch_leaves_a_shadow("executor", "_combat")
        assert "_execute_cancel" not in vars(M.executor)
        assert _instance_patch_leaves_a_shadow("executor", "_execute_cancel")
        assert not _INSTANCE_PATCH_RE.search(
            'monkeypatch.setattr(' + 'type(M.executor), "execute", spy)')
        assert not _INSTANCE_PATCH_RE.search(
            'monkeypatch.setattr(' + 'M, "parser", CommandParser(use_real_llm=False))')
