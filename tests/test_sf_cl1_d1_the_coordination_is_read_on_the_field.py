"""§6 row 16's build (SF-CL-1-D1, ruled October 3, 2026 by the user: "read the
lead's coordination context on the FIELD") — Score Finish Step 7 slice 3,
October 4, 2026.

The resolver relocates every arriving reinforcer INTO the battle province but
read the lead's coordination context in HIS province, so an attack from next
door earned none from the corps that answered it (Ney at Rhineland on Mack at
Swabia: Davout, Lannes and the Emperor marched to Swabia and none counted),
while a corps beside him that never marched was credited instead. The context
is read on the field now — the lead counted present among the arrivals, kept
out of the adjacent count — and the muster's forecast (`_priced_coordination`)
follows in lockstep.

    combat_executor.THE_COORDINATION_IS_READ_ON_THE_FIELD — lever down: the
    lead's own province, as before (the recorded series reproduces byte for
    byte on that arm: `tools/_coord_field_series_arms_final.json`).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import backend.commands.combat_executor as CE
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def board(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _arrive(world, names, field):
    """Stage what the resolver does before it reads the context: the
    answering corps relocate into the field."""
    for name in names:
        world.marshals[name].location = field
    world.invalidate_bloc_members_cache()


class TestTheFieldIsWhereTheCoordinationIsRead:
    def test_the_corps_that_answer_count_for_the_lead(self, board):
        _, world = board
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        assert ney.location == "Rhineland" and mack.location == "Swabia"
        _arrive(world, ["Davout", "Murat"], mack.location)
        combat._calculate_coordination_context(
            ney, world, exclude_from_adjacent={"Davout", "Murat"}, field=mack.location)
        # Murat's cavalry beside Ney's infantry: combined arms on the field
        assert ney._display_combined_arms_atk > 0.0
        # Davout and Murat are his allies on the field: per-ally coordination
        assert ney._display_coordination_atk > 0.0
        assert ney.total_coordination_attack_bonus > 0.0

    def test_the_lever_down_reads_his_own_province(self, board, monkeypatch):
        monkeypatch.setattr(CE, "THE_COORDINATION_IS_READ_ON_THE_FIELD", False)
        _, world = board
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        _arrive(world, ["Davout", "Murat"], mack.location)
        combat._calculate_coordination_context(
            ney, world, exclude_from_adjacent={"Davout", "Murat"}, field=mack.location)
        # Rhineland is empty of allies once Davout has marched: no per-ally
        # term, and Ney's lone infantry is no combined arms
        assert ney._display_coordination_atk == 0.0
        assert ney._display_combined_arms_atk == 0.0

    def test_a_corps_that_never_marched_is_not_credited(self, board):
        """The ruling's rejected alternative, pinned: Davout stays at
        Rhineland (he never answered), so the field holds Ney alone."""
        _, world = board
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        assert world.marshals["Davout"].location == ney.location
        combat._calculate_coordination_context(ney, world, field=mack.location)
        assert ney._display_coordination_atk == 0.0

    def test_the_lead_is_no_ally_of_himself_next_door(self, board):
        _, world = board
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        ctx = combat._calculate_coordination_context(ney, world, field=mack.location)
        assert "Ney" not in ctx["adjacent_names"]
        assert "Ney" in ctx["eligible_marshals"]

    def test_a_field_that_is_his_own_province_changes_nothing(self, board, monkeypatch):
        _, world = board
        combat = M.executor._combat
        nap, mack = world.marshals["Napoleon"], world.marshals["Mack"]
        _arrive(world, ["Napoleon", "Davout"], mack.location)
        combat._calculate_coordination_context(nap, world, field=mack.location)
        up = (nap.total_coordination_attack_bonus, nap._display_coordination_atk)
        monkeypatch.setattr(CE, "THE_COORDINATION_IS_READ_ON_THE_FIELD", False)
        combat._calculate_coordination_context(nap, world, field=mack.location)
        assert (nap.total_coordination_attack_bonus, nap._display_coordination_atk) == up


class TestTheMusterFollowsInLockstep:
    def test_an_attack_from_next_door_is_priced_on_the_field(self, board):
        """The driven case of the ruling: `Ney, attack Mack` at POST /command.
        The ceiling bounds the battle (SF-CL-1's census rule) and — every
        promised corps that fought — equals it; and with the field read the
        priced strength rises over the lever-down reading."""
        client, world = board
        reply = client.post("/command", json={"command": "Ney, attack Mack"}).json()
        pv, ms = reply["muster_preview"], reply["massed_strength"]
        promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
        fought = set(ms["arrived"]) | set(ms["contributors"])
        assert ms["total"] <= pv["attacker"]["ceiling_strength"]
        if promised <= fought:
            assert ms["total"] == pv["attacker"]["ceiling_strength"]

    def test_the_field_read_prices_more_than_his_province(self, board, monkeypatch):
        client, world = board
        combat = M.executor._combat
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        up = combat._build_muster_preview(ney, mack, world, {"world": world})
        monkeypatch.setattr(CE, "THE_COORDINATION_IS_READ_ON_THE_FIELD", False)
        down = combat._build_muster_preview(ney, mack, world, {"world": world})
        assert up["attacker"]["ceiling_strength"] > down["attacker"]["ceiling_strength"]

    @pytest.mark.parametrize("guns", [False, True])
    def test_every_promised_corps_that_fights_makes_the_ceiling_exact(
            self, board, monkeypatch, guns):
        """SF-CL-1's rule under the field read, with and without a gun
        corps: the battle masses exactly the ceiling when every corps the
        muster promised arrives. A gun stays where he stands and in the
        adjacent count (the resolver keeps him out of `arrived_names`), so
        the forecast must price him there — before the lockstep line it
        priced him nowhere: a ceiling of 87,991 against 88,684 massed on
        this staged board, 693 men short."""
        import random
        client, world = board
        found = None
        for seed in range(1, 60):
            M._reset_world_state()
            monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
            world = M.world
            world.marshals["Lannes"].artillery = guns
            world.marshals["Murat"].location = "Paris"   # the promise: three corps
            world.invalidate_bloc_members_cache()
            random.seed(seed)
            reply = client.post("/command", json={"command": "Ney, attack Mack"}).json()
            pv, ms = reply["muster_preview"], reply["massed_strength"]
            promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
            fought = set(ms["arrived"]) | set(ms["contributors"])
            if promised and promised <= fought:
                found = (pv["attacker"]["ceiling_strength"], ms["total"])
                break
        assert found is not None
        assert found[0] == found[1]
