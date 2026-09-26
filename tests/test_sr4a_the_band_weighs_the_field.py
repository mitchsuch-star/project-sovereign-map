"""SR-4a part (ii) — AAR-32 "'Favorable' is an army-size verdict" (Score
Mandate Chunk 4). Rules `SYSTEMS_REFERENCE.md` §73.2.

Reproduced at `POST /command` on the shipped 1805 boot before a line changed:
a solo strike on a Kutuzov standing in a defensive stance read "the balance
of force looks favorable" and fought a brutal stalemate; Massena, in a
DEFENSIVE stance, attacking Archduke John in the Tyrol mountains read
"even" — the identical line and ratio as in a neutral stance — and his
stance and the mountains appeared only in the post-battle log. The band
compared men, not the modifier stack the resolver applies.
"""

import contextlib
import io
import re

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import objection_v2 as O
from backend.commands.parser import CommandParser
from backend.models.marshal import Stance


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False
    return TestClient(M.app), M.world


def post(client, command):
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": command}).json()


def _solo(world, keep):
    """Move every French corps but `keep` far from the field."""
    for m in world.marshals.values():
        if m.nation == "France" and m.name not in keep:
            m.location = "Normandy"


def _stage_kutuzov(world, attacker="Davout", strength=49400):
    _solo(world, {attacker})
    k = world.get_marshal("Kutuzov")
    k.location = "Swabia"
    k.strength = 38000
    k.stance = Stance.DEFENSIVE
    for m in world.marshals.values():
        if m.location == "Swabia" and m.name != "Kutuzov" and m.nation != "France":
            m.location = "Bohemia"
    a = world.get_marshal(attacker)
    a.location = "Rhineland"
    a.strength = strength
    return a, k


class TestTheBandWeighsTheStandingModifiers:

    def test_a_defensive_kutuzov_is_no_longer_favorable(self, shipped):
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        gs = {"world": world}
        men_only = O.inferred_attack_odds_band(davout, kutuzov, gs)
        folded = O.inferred_attack_odds_band(davout, kutuzov, gs, fold_modifiers=True)
        assert men_only == "favorable"
        assert folded != "favorable", folded

    def test_the_fold_is_the_single_sources(self, shipped):
        """The folded ratio = men x the leads' own modifiers (no second
        formula): recompute it from `get_attack_modifier` /
        `get_defense_modifier` and compare."""
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        gs = {"world": world}
        men = O.inferred_attack_effective_ratio(davout, kutuzov, gs)
        folded = O.inferred_attack_effective_ratio(davout, kutuzov, gs, fold_modifiers=True)
        atk = davout.get_attack_modifier(davout.strength / kutuzov.strength, consume=False)
        dfm = kutuzov.get_defense_modifier(kutuzov.strength < davout.strength, consume=False)
        assert folded == pytest.approx(men * atk / dfm, rel=1e-9)

    def test_the_fold_spends_nothing(self, shipped):
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        kutuzov.strategic_defense_bonus = 10
        davout.strategic_combat_bonus = 10
        O.inferred_attack_effective_ratio(davout, kutuzov, {"world": world}, fold_modifiers=True)
        assert kutuzov.strategic_defense_bonus == 10
        assert davout.strategic_combat_bonus == 10

    def test_a_fortified_defender_is_not_counted_twice(self, shipped):
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        kutuzov.fortified = True
        kutuzov.defense_bonus = 0.12
        gs = {"world": world}
        folded = O.inferred_attack_effective_ratio(davout, kutuzov, gs, fold_modifiers=True)
        atk = davout.get_attack_modifier(davout.strength / kutuzov.strength, consume=False)
        dfm = kutuzov.get_defense_modifier(kutuzov.strength < davout.strength, consume=False)
        assert folded == pytest.approx(davout.strength * atk / (kutuzov.strength * dfm), rel=1e-9)

    def test_the_cr5_gates_keep_their_lead_only_read(self, shipped):
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        gs = {"world": world}
        assert O.inferred_attack_favorable(davout, kutuzov, gs) == (
            O.inferred_attack_effective_ratio(davout, kutuzov, gs) >= 0.7)

    def test_the_lever_down_is_the_men_only_band(self, shipped, monkeypatch):
        monkeypatch.setattr(O, "THE_BAND_WEIGHS_THE_STANDING_MODIFIERS", False)
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        gs = {"world": world}
        assert (O.inferred_attack_effective_ratio(davout, kutuzov, gs, fold_modifiers=True)
                == O.inferred_attack_effective_ratio(davout, kutuzov, gs))


class TestTheMusterReadsTheFold:

    def test_the_preview_and_the_glory_gate_agree(self, shipped):
        """`muster_odds` (the glory gate, both boards) reads the band the
        preview prints."""
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world)
        odds = M.executor._combat.muster_odds(davout, kutuzov, world)
        folded = O.inferred_attack_odds_band(
            davout, kutuzov, {"world": world},
            committed_attacker=odds["committed_attacker"],
            committed_defender=odds["committed_defender"], fold_modifiers=True)
        assert odds["band"] == folded

    def test_the_muster_line_says_the_folded_band(self, shipped):
        client, world = shipped
        _stage_kutuzov(world)
        world.update_intel_from_scout("Swabia", world.current_turn)
        data = post(client, "Davout, attack Kutuzov")
        blob = str(data.get("message") or "") + str(data.get("pending_interrupt") or "")
        assert "the balance of force looks favorable" not in blob, blob[:400]


class TestThePostureNoteNamesWhatHurts:

    def _stage_massena(self, world, stance=Stance.DEFENSIVE):
        _solo(world, {"Massena"})
        massena = world.get_marshal("Massena")
        john = world.get_marshal("ArchdukeJohn")
        john.location = "Tyrol"
        tyrol = world.get_region("Tyrol")
        for m in world.marshals.values():
            if m.location == "Tyrol" and m.name != john.name:
                m.location = "Bohemia"
        massena.location = next(r for r in tyrol.adjacent_regions
                                if world.get_region(r).controller in ("France", "Bavaria"))
        massena.stance = stance
        return massena, john

    def test_the_stance_and_the_mountains_are_named(self, shipped):
        _client, world = shipped
        massena, john = self._stage_massena(world)
        note = M.executor._combat._posture_note(massena, john, world)
        # the stance is named even though his aggressive character more than
        # makes it up (the net product is above 1 — the AAR's own case)
        assert "Massena attacks from a defensive stance (−10%)" in note, note
        assert "the ground favors the defender (+" in note and "mountains)" in note, note

    def test_the_net_cost_is_named_when_it_hurts(self, shipped):
        """A cautious man in a defensive stance: his modifiers net below 1
        and the note says by how much (the single source's product)."""
        _client, world = shipped
        _solo(world, {"Davout"})
        davout = world.get_marshal("Davout")
        davout.stance = Stance.DEFENSIVE
        john = world.get_marshal("ArchdukeJohn")
        mod = davout.get_attack_modifier(davout.strength / john.strength, consume=False)
        assert mod < 0.995, mod
        note = M.executor._combat._posture_note(davout, john, world)
        pct = int(round((1.0 - mod) * 100))
        assert f"all told, Davout's own modifiers weigh {pct}% against the attack" in note, note

    def test_the_enemys_stack_only_at_full(self, shipped):
        _client, world = shipped
        massena, john = self._stage_massena(world)
        john.stance = Stance.DEFENSIVE
        from backend.models.intel import FULL, PARTIAL
        world.get_region_intel("Tyrol").refresh(visibility=PARTIAL, source="probe",
                                                 turn=world.current_turn)
        assert "on the defense" not in M.executor._combat._posture_note(massena, john, world)
        world.update_intel_from_scout("Tyrol", world.current_turn)
        assert world.get_region_intel("Tyrol").visibility == FULL
        assert "stands +" in M.executor._combat._posture_note(massena, john, world)

    def test_nothing_is_named_when_nothing_hurts(self, shipped):
        _client, world = shipped
        davout, kutuzov = _stage_kutuzov(world, attacker="Ney")
        world.get_marshal("Ney").stance = Stance.AGGRESSIVE
        kutuzov.stance = Stance.NEUTRAL if hasattr(Stance, "NEUTRAL") else kutuzov.stance
        note = M.executor._combat._posture_note(world.get_marshal("Ney"), kutuzov, world)
        assert "own modifiers" not in note and "defensive stance" not in note, note

    def test_the_muster_prints_the_note(self, shipped):
        """Produced AND rendered: the note reaches the muster text the player
        reads before committing (NP-V's lesson — a producer no surface reads
        is not shown)."""
        client, world = shipped
        massena, john = self._stage_massena(world)
        world.update_intel_from_scout("Tyrol", world.current_turn)
        data = post(client, "Massena, attack Archduke John")
        blob = str(data.get("message") or "") + str(data.get("pending_interrupt") or "")
        assert "Massena attacks from a defensive stance" in blob, blob[:600]

    def test_the_lever_down_names_nothing(self, shipped, monkeypatch):
        monkeypatch.setattr(O, "THE_BAND_WEIGHS_THE_STANDING_MODIFIERS", False)
        _client, world = shipped
        massena, john = self._stage_massena(world)
        assert M.executor._combat._posture_note(massena, john, world) == ""
