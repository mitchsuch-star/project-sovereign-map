"""CN — "The Chip Names the Man" (the Command-Road Queue, slice 3).

Build contract: `docs/audits/RECRUIT_ARM_UX_2026_09_20.md` (R1 ≡ CN-1, R2 ≡
CN-2, R3 ≡ CN-3, R4 ≡ CN-4). Reproduced on this HEAD before a line was
written (September 22, 2026), fresh 1805 board per cell, `POST /command`,
verdict by EFFECT (the manpower-pool delta, the gold, the admin AP): of the
90 recruit chips the region panel renders, **69 refused and 14 of the 21
that acted delivered an arm the label did not name** —

    recruit cavalry in Rhineland       3,000 INFANTRY via Davout, 741g
    recruit infantry in Franche-Comte  3,000 CAVALRY via Murat, 1,504g
                                       (Lannes, infantry, stood there: 872g)
    recruit artillery in <any>         infantry or cavalry, full price

and every province QUOTED 872g (the infantry base, no marshal, no arm, no
field cap) beside chips that charged 741g, 872g or 1,504g for 3,000 men the
quote called 10,000.

The one mechanics change is CN-2: where the game chooses the man (no marshal
named) the requested arm is a SELECTION KEY. A NAMED marshal's arm is never
overridden (PF-7) — `Davout, recruit cavalry` still raises infantry and says
so, and test_pf7_recruit_arm_amount_bombard.py passes unedited.

Every pin asserts the EFFECT, never a message substring alone.
"""

import ast
import contextlib
import copy
import io
import pathlib
import random

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import economy_executor as EE
from backend.commands.parser import CommandParser
from backend.models.world_state import RECRUIT_ARMS, recruit_arm_of

REPO = pathlib.Path(__file__).resolve().parents[1]


# ═══════════════════════════════════════════════════════════════════════════
# Harness
# ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture
def board(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app)


def _fund(gold=20000):
    M.world.nation_gold["France"] = gold


def _state():
    w = M.world
    return (dict(w.manpower_pools.get("France", {})),
            int(w.nation_gold.get("France", 0)),
            (w.actions_remaining, w.admin_actions_remaining))


def _drive(client, text):
    pools, gold, ap = _state()
    with contextlib.redirect_stdout(io.StringIO()):
        response = client.post("/command", json={"command": text}).json()
    pools2, gold2, ap2 = _state()
    delta = {k: pools2.get(k, 0) - pools.get(k, 0) for k in pools
             if pools2.get(k, 0) != pools.get(k, 0)}
    events = response.get("events") or []
    via = events[0].get("marshal") if events else None
    return {"ok": bool(response.get("success")), "pool": delta,
            "gold": gold - gold2, "ap": (ap, ap2), "via": via,
            "message": response.get("message") or ""}


# ═══════════════════════════════════════════════════════════════════════════
# CN-2 — the arm is a selection key (the memo's R2 done_when)
# ═══════════════════════════════════════════════════════════════════════════
class TestTheArmChoosesTheMan:

    def test_cavalry_in_rhineland_is_cavalry(self, board):
        """Item 1. HEAD: {'infantry': -3000} via Davout, 741g."""
        _fund()
        res = _drive(board, "recruit cavalry in Rhineland")
        assert res["ok"], res["message"]
        assert res["pool"] == {"cavalry": -3000}, res
        assert res["via"] == "Murat", res

    def test_infantry_in_franche_comte_is_lannes_at_his_price(self, board):
        """Item 2. HEAD: {'cavalry': -3000} via Murat at 1,504g."""
        _fund()
        res = _drive(board, "recruit infantry in Franche-Comte")
        assert res["ok"], res["message"]
        assert res["pool"] == {"infantry": -3000}, res
        assert res["via"] == "Lannes", res
        assert res["gold"] == 872, res

    @pytest.mark.parametrize("province", [
        "Burgundy", "Savoy", "Franche-Comte", "Lorraine", "Nivernais",
        "Orleanais", "Rhineland"])
    def test_artillery_is_refused_free_where_no_gun_marshal_stands(
            self, board, province):
        """Item 3 — the seven provinces whose chips ACTED at HEAD, silently
        delivering infantry or cavalry at full price."""
        _fund()
        res = _drive(board, f"recruit artillery in {province}")
        assert not res["ok"], res
        assert res["pool"] == {} and res["gold"] == 0, res
        assert res["ap"][0] == res["ap"][1], res
        assert "commission Marmont (4500g)" in res["message"], res["message"]

    def test_a_named_marshal_keeps_his_arm(self, board):
        """Item 4: PF-7's surfaced correction, untouched — a marshal IS his
        corps; the arm the player named for him is not an override."""
        res = _drive(board, "Davout, recruit cavalry")
        assert res["ok"], res["message"]
        assert res["pool"] == {"infantry": -3000}, res
        assert "commands infantry" in res["message"], res["message"]

    def test_the_refusal_names_who_is_in_range_and_spends_nothing(self, board):
        _fund()
        res = _drive(board, "recruit infantry in Burgundy")
        assert not res["ok"] and res["pool"] == {} and res["gold"] == 0
        assert "Murat commands cavalry" in res["message"], res["message"]
        assert "Nothing was spent." in res["message"], res["message"]

    def test_the_bare_recruit_is_unchanged(self, board):
        """Item 8, the negative control: with no arm named, the choice is
        the pre-slice nearest-then-strongest one."""
        _fund()
        res = _drive(board, "recruit in Franche-Comte")
        assert res["ok"], res["message"]
        assert res["via"] == "Murat" and res["pool"] == {"cavalry": -3000}


# ═══════════════════════════════════════════════════════════════════════════
# Item 9 — the positive artillery case: recruit WORKS for a gun marshal
# ═══════════════════════════════════════════════════════════════════════════
class TestTheGunMarshal:

    @pytest.mark.parametrize("gunner", ["Marmont", "Senarmont"])
    def test_a_commissioned_gun_marshal_raises_guns(self, board, gunner):
        _fund()
        res = _drive(board, f"commission {gunner}")
        assert res["ok"], res["message"]
        assert M.world.get_marshal(gunner).artillery is True
        assert M.world.get_marshal(gunner).location == "Paris"
        M.world.admin_actions_remaining = 2
        res = _drive(board, "recruit artillery in Paris")
        assert res["ok"], res["message"]
        assert res["pool"] == {"artillery": -3000} and res["via"] == gunner
        quote = EE.recruit_quote(M.world, "Paris", arm="artillery")
        M.world.admin_actions_remaining = 2
        res = _drive(board, f"{gunner}, recruit artillery")
        assert res["ok"], res["message"]
        assert res["pool"] == {"artillery": -3000} and res["via"] == gunner
        assert res["gold"] == quote["price"], (res, quote)

    def test_the_remedy_follows_the_board(self, board):
        """Never hard-coded: 'commission Marmont (4500g)' while no gun
        marshal stands; his name and his order once one does."""
        before = EE.recruit_quote(M.world, "Rhineland", arm="artillery")
        assert "commission Marmont (4500g)" in before["reason"]
        _fund()
        _drive(board, "commission Marmont")
        after = EE.recruit_quote(M.world, "Rhineland", arm="artillery")
        assert after["kind"] == "no_arm_in_range"
        assert "'Marmont, recruit artillery'" in after["reason"], after
        assert "commission" not in after["reason"], after

    def test_the_artillery_chip_lights_on_his_province(self, board):
        _fund()
        _drive(board, "commission Marmont")
        summary = M.world.get_filtered_game_state_summary()
        paris = summary["map_data"]["Paris"]["recruit_here"]["artillery"]
        assert paris["ok"] and paris["recipient"] == "Marmont", paris


# ═══════════════════════════════════════════════════════════════════════════
# CN-1 — the quote is what the executor does (the drift pin)
# ═══════════════════════════════════════════════════════════════════════════
def _all_provinces():
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    return sorted(M.world.regions)


class TestTheQuoteIsWhatTheExecutorDoes:

    def test_every_province_every_arm(self, board):
        """126 provinces × (no arm + three arms), funded board. A refusal is
        driven on the SAME board (a refusal changes nothing — asserted); an
        acting cell on a fresh one. Quote and executor must agree on the
        verdict, the recipient, the gold and the men — and a refusal must
        read the very sentence the chip would show."""
        _fund()
        mismatches = []
        acting = []
        for province in sorted(M.world.regions):
            for arm in (None,) + RECRUIT_ARMS:
                quote = EE.recruit_quote(M.world, province, arm=arm)
                text = (f"recruit {arm} in {province}" if arm
                        else f"recruit in {province}")
                if not quote["ok"]:
                    res = _drive(board, text)
                    if res["ok"] or res["pool"] or res["gold"]:
                        mismatches.append((text, "quote refused, executor acted",
                                           quote["kind"], res["message"][:80]))
                    elif res["message"] != quote["reason"]:
                        mismatches.append((text, "refusal copy",
                                           quote["reason"][:80],
                                           res["message"][:80]))
                else:
                    acting.append((text, quote))
        for text, quote in acting:
            with contextlib.redirect_stdout(io.StringIO()):
                M._reset_world_state()
            _fund()
            client = TestClient(M.app)
            res = _drive(client, text)
            got_men = -sum(res["pool"].values()) if res["pool"] else 0
            if not (res["ok"] and res["via"] == quote["recipient"]
                    and res["gold"] == quote["price"]
                    and got_men == quote["amount"]
                    and list(res["pool"]) == [quote["arm"]]):
                mismatches.append((text, quote["recipient"], quote["price"],
                                   quote["amount"], res))
        assert mismatches == [], mismatches[:5]
        assert len(acting) >= 12, len(acting)

    def test_the_payload_carries_the_quote_for_each_arm(self, board):
        summary = M.world.get_filtered_game_state_summary()
        rhine = summary["map_data"]["Rhineland"]["recruit_here"]
        assert set(rhine) == set(RECRUIT_ARMS)
        assert rhine["infantry"]["recipient"] == "Davout"
        assert rhine["infantry"]["price"] == 741
        assert rhine["infantry"]["amount"] == 3000
        assert rhine["cavalry"]["recipient"] == "Murat"
        assert rhine["artillery"]["ok"] is False

    def test_the_price_here_is_what_the_bare_levy_charges(self, board):
        """The old key quoted 872 (the infantry base) everywhere."""
        summary = M.world.get_filtered_game_state_summary()
        assert summary["map_data"]["Rhineland"]["recruit_price_here"] == 741
        # nobody can reach Paris at boot: the bare levy refuses, so no price
        assert summary["map_data"]["Paris"]["recruit_price_here"] == 0

    def test_ally_soil_carries_the_executors_refusal(self, board):
        """D5: recruiting does not open on ally soil. The row renders there
        (a French corps stands on it, the granary is open) — disabled, with
        the executor's own sentence."""
        summary = M.world.get_filtered_game_state_summary()
        milan = summary["map_data"]["Milan"]["recruit_here"]
        assert milan["infantry"]["ok"] is False
        assert milan["infantry"]["reason"] == EE._msg_not_controlled("Milan")

    def test_a_province_with_no_row_carries_nothing(self, board):
        """Read UNFILTERED: fog alone would hide Vienna's block, and the pin
        is about the producer computing nothing there (GR8 — 96 provinces
        must cost nothing)."""
        summary = M.world.get_game_state_summary()
        assert summary["map_data"]["Vienna"]["recruit_here"] == {}
        assert summary["map_data"]["Vienna"]["recruit_price_here"] == 0
        assert summary["map_data"]["Rhineland"]["recruit_here"] != {}

    def test_the_quote_refuses_what_the_treasury_cannot_pay(self, board):
        """Boot treasury 800g: Murat's cavalry at Franche-Comte is 1,504g."""
        quote = EE.recruit_quote(M.world, "Franche-Comte", arm="cavalry")
        assert quote["kind"] == "treasury" and quote["ok"] is False
        assert quote["price"] == 1504, quote
        res = _drive(board, "recruit cavalry in Franche-Comte")
        assert not res["ok"] and res["message"] == quote["reason"]

    def test_the_quote_refuses_an_empty_pool(self, board):
        _fund()
        M.world.manpower_pools["France"]["cavalry"] = 1000
        quote = EE.recruit_quote(M.world, "Rhineland", arm="cavalry")
        assert quote["kind"] == "pool_short" and quote["ok"] is False
        res = _drive(board, "recruit cavalry in Rhineland")
        assert not res["ok"] and res["message"] == quote["reason"]

    def test_the_quote_refuses_without_an_admin_action(self, board):
        _fund()
        M.world.admin_actions_remaining = 0
        quote = EE.recruit_quote(M.world, "Rhineland", arm="infantry")
        assert quote["kind"] == "no_admin_ap" and quote["ok"] is False
        res = _drive(board, "recruit infantry in Rhineland")
        assert not res["ok"] and res["message"] == quote["reason"]

    def test_the_price_here_is_zero_where_the_bare_levy_refuses(self, board):
        """Franche-Comte's nearest is Murat, whose 1,504g the boot treasury
        cannot pay — the bare levy refuses, so the province quotes nothing
        rather than a price it will not honour."""
        summary = M.world.get_filtered_game_state_summary()
        assert summary["map_data"]["Franche-Comte"]["recruit_price_here"] == 0

    def test_the_remedy_names_the_nearest_commander_of_the_arm(self, board):
        world = M.world
        quote = EE.recruit_quote(world, "Burgundy", arm="infantry")
        assert quote["kind"] == "no_arm_in_range"
        serving = [m for m in world.get_player_marshals()
                   if m.strength > 0 and recruit_arm_of(m) == "infantry"]
        nearest = min(world.get_distance(m.location, "Burgundy")
                      for m in serving)
        named = [m for m in serving if f"'{m.name}, recruit infantry'"
                 in quote["reason"]]
        assert len(named) == 1, quote["reason"]
        assert world.get_distance(named[0].location, "Burgundy") == nearest

    def test_the_quote_is_pure(self, board):
        """The payload asks for 90 quotes a response; none may disturb the
        refusal reason the selector leaves for `_recruit_block_reason`."""
        M.world._last_nearest_marshal_block = ["sentinel"]
        before = copy.deepcopy(_state())
        for arm in (None,) + RECRUIT_ARMS:
            EE.recruit_quote(M.world, "Paris", arm=arm)
        assert M.world._last_nearest_marshal_block == ["sentinel"]
        assert _state() == before


# ═══════════════════════════════════════════════════════════════════════════
# Kill criteria (the memo's R2 "do not ship if either holds")
# ═══════════════════════════════════════════════════════════════════════════
def _reference_nearest(world, region_name):
    """The PRE-CN selector, verbatim in its rule: living, >= 1,000 men, in
    his own range; nearest first, strongest breaks the tie."""
    if region_name not in world.regions:
        return None
    ready = []
    for m in world.get_player_marshals():
        d = world.get_distance(m.location, region_name)
        if m.strength <= 0 or m.strength < 1000 or d > m.movement_range:
            continue
        ready.append((m, d))
    if not ready:
        return None
    ready.sort(key=lambda x: (x[1], -x[0].strength))
    return (ready[0][0].name, ready[0][1])


class TestTheKillCriteria:

    def test_no_arm_is_byte_identical_over_every_province(self, board):
        """Kill criterion 1: `arm=None` is the pre-slice selector on 126
        provinces, on the boot board and on eight shuffled boards (the
        selector has five call sites, two in combat)."""
        world = M.world
        rng = random.Random(1805)
        regions = sorted(world.regions)
        ours = world.get_player_marshals()
        for trial in range(9):
            if trial:
                for m in ours:
                    m.location = rng.choice(regions)
                    m.strength = rng.choice([0, 500, 12000, 30000])
            for province in regions:
                got = world.find_nearest_marshal_to_region(province)
                got = (got[0].name, got[1]) if got else None
                assert got == _reference_nearest(world, province), (
                    trial, province)

    def _recruit_producers(self, source):
        tree = ast.parse(source)
        bad = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            for k, v in zip(node.keys, node.values):
                if (isinstance(k, ast.Constant) and k.value == "action"
                        and isinstance(v, ast.Constant) and v.value == "recruit"
                        and "marshal" not in keys):
                    bad.append(node.lineno)
        return bad

    def test_every_ai_recruit_names_its_marshal(self):
        """Kill criterion 2: the AI never enters the arm-keyed branch, so
        GR5 is free and BASELINE_SERIES cannot move. `prompt_builder`'s
        dicts are few-shot EXAMPLES for the model, not producers."""
        found = []
        for path in sorted((REPO / "backend" / "ai").rglob("*.py")):
            if path.name == "prompt_builder.py":
                continue
            found += [(path.name, line) for line in
                      self._recruit_producers(path.read_text(encoding="utf-8"))]
        assert found == [], found

    def test_the_census_sees_a_missing_marshal(self):
        """The sensitivity arm: delete the key from a copy and the census
        goes red."""
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(
            encoding="utf-8")
        assert self._recruit_producers(source) == []
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict) and any(
                    isinstance(k, ast.Constant) and k.value == "action"
                    and isinstance(v, ast.Constant) and v.value == "recruit"
                    for k, v in zip(node.keys, node.values)):
                pairs = [(k, v) for k, v in zip(node.keys, node.values)
                         if not (isinstance(k, ast.Constant) and k.value == "marshal")]
                node.keys = [k for k, _v in pairs]
                node.values = [v for _k, v in pairs]
                break
        assert self._recruit_producers(ast.unparse(tree)) != []


class TestTheLever:

    def test_the_lever_restores_the_arm_blind_choice(self, board, monkeypatch):
        monkeypatch.setattr(EE, "THE_ARM_CHOOSES_THE_MAN", False)
        _fund()
        res = _drive(board, "recruit cavalry in Rhineland")
        assert res["ok"] and res["pool"] == {"infantry": -3000}, res
        assert res["via"] == "Davout", res

    def test_the_lever_is_up(self):
        assert EE.THE_ARM_CHOOSES_THE_MAN is True
        assert recruit_arm_of(type("M", (), {"artillery": True})()) == "artillery"
