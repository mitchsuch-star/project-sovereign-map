"""MC-2 pin tests (MARSHAL_CONTENT_PASS_SPEC.md §4/§7, memo §3 — skills + trust).

The July 10, 2026 gate blessed the full 21-row skills/trust table (memo §3)
with the Q3 amendment applied: the four combat skills + command ship authored
(command ACTIVATES The Rally texture — Davout 9 / ArchdukeCharles 8 fast tier,
Mack/Massena/Buxhowden/Hohenlohe 3 poor tier); administration ships FLAT 5 for
all 21 (reserved data — the authored values live in the memo table and land at
the owned MC-2b slice).

Also the memo §6.4 re-measures: Ney's Bravest of the Brave at authored shock 9
(+7% relative, under the ~+10% anchor) and the Lannes/Bernadotte arrival
mirror at authored logistics (deterministic base 90 vs 60; 75 without the
ability; 70 under a written SUPPORT order).

Visual layer (this slice): the marshal card ships per-skill mechanic hints
(`skill_notes`) and a backend-derived Rally tier + note (`rally_tier`,
`rally_note`) — Godot renders these verbatim (shown = applied, Q3 pattern).
"""

import random as _random

import pytest

from backend.ai.parser_eval import build_world
from backend.commands.executor import CommandExecutor
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState


@pytest.fixture()
def world():
    return build_world("1805")


# name: (tactical, shock, defense, logistics, command, trust) — memo §3,
# blessed July 10, 2026. Values are in-band tunable; a change here must be a
# deliberate tuning decision recorded in the spec §14-style ledger, not drift.
BLESSED_TABLE = {
    "Ney":             (5, 9, 6, 4, 7, 75),
    "Davout":          (8, 6, 8, 7, 9, 85),
    "Soult":           (9, 6, 7, 6, 6, 70),
    "Lannes":          (7, 8, 5, 4, 7, 85),
    "Murat":           (4, 9, 2, 3, 5, 75),
    "Bernadotte":      (6, 4, 5, 6, 5, 40),
    "Massena":         (8, 7, 7, 8, 3, 60),
    "Deroy":           (5, 4, 5, 5, 5, 70),
    "Mack":            (2, 3, 3, 4, 3, 75),
    "ArchdukeCharles": (8, 6, 8, 7, 8, 55),
    "ArchdukeJohn":    (3, 3, 4, 5, 4, 65),
    "Kutuzov":         (7, 3, 7, 8, 7, 50),
    "Buxhowden":       (3, 5, 4, 3, 3, 65),
    "Moore":           (7, 5, 7, 6, 7, 65),
    "Brunswick":       (4, 3, 5, 6, 4, 70),
    "Hohenlohe":       (3, 4, 3, 3, 3, 60),
    "Armfelt":         (3, 4, 4, 3, 4, 55),
    "Damas":           (4, 4, 4, 3, 4, 65),
    "Frederick":       (3, 3, 5, 5, 4, 85),
    "Castanos":        (4, 3, 4, 5, 4, 70),
    "Abdurrahman":     (4, 5, 4, 5, 4, 60),
}

FRENCH = ("Ney", "Davout", "Soult", "Lannes", "Murat", "Bernadotte", "Massena")


# ════════════════════════════════════════════════════════════════════════
# Boot pins: the authored table survives the scenario pipeline, per marshal
# ════════════════════════════════════════════════════════════════════════

class TestAuthoredSkillsAndTrust:
    @pytest.mark.parametrize("name", sorted(BLESSED_TABLE))
    def test_marshal_boots_with_blessed_skills(self, world, name):
        tac, shk, dfn, log, cmd, _ = BLESSED_TABLE[name]
        m = world.get_marshal(name)
        assert m.skills["tactical"] == tac, name
        assert m.skills["shock"] == shk, name
        assert m.skills["defense"] == dfn, name
        assert m.skills["logistics"] == log, name
        assert m.skills["command"] == cmd, name

    @pytest.mark.parametrize("name", sorted(BLESSED_TABLE))
    def test_marshal_boots_with_blessed_trust(self, world, name):
        assert world.get_marshal(name).trust.value == BLESSED_TABLE[name][5], name

    @pytest.mark.parametrize("name", sorted(BLESSED_TABLE))
    def test_administration_flat_5_until_mc2b(self, world, name):
        # Gate Q3: admin ships FLAT — the authored values are reserved data
        # (memo §3 table) that the owned MC-2b slice lands live. Authoring a
        # non-5 admin here without MC-2b is a gate violation, not tuning.
        assert world.get_marshal(name).skills["administration"] == 5, name

    @pytest.mark.parametrize("name", sorted(BLESSED_TABLE))
    def test_legacy_tactical_skill_field_coheres(self, world, name):
        # The legacy dice-fallback field is authored equal to skills.tactical
        # so no surface (payload or fallback path) can show a split value.
        m = world.get_marshal(name)
        assert m.tactical_skill == m.skills["tactical"], name

    def test_all_21_marshals_covered(self, world):
        assert set(BLESSED_TABLE) == set(world.marshals.keys())


# ════════════════════════════════════════════════════════════════════════
# Balance frame (memo §3): roster means hold — global balance does not shift
# ════════════════════════════════════════════════════════════════════════

class TestBalanceFrame:
    @pytest.mark.parametrize("skill_index,skill_name", [
        (0, "tactical"), (1, "shock"), (2, "defense"),
        (3, "logistics"), (4, "command"),
    ])
    def test_per_skill_roster_mean_in_band(self, skill_index, skill_name):
        mean = sum(v[skill_index] for v in BLESSED_TABLE.values()) / len(BLESSED_TABLE)
        assert 4.95 <= mean <= 5.10, f"{skill_name} mean {mean:.3f} out of band"

    def test_french_trust_mean_exactly_70(self):
        # The player objection/defiance economy is net-unchanged (memo §3).
        mean = sum(BLESSED_TABLE[n][5] for n in FRENCH) / len(FRENCH)
        assert mean == 70.0

    def test_roster_trust_mean_66_7(self):
        # Enemy courts historically distrusted their commanders (Q5 blessed).
        mean = sum(v[5] for v in BLESSED_TABLE.values()) / len(BLESSED_TABLE)
        assert mean == pytest.approx(66.7, abs=0.05)

    def test_peaks_cap_at_9(self):
        for name, row in BLESSED_TABLE.items():
            assert max(row[:5]) <= 9, name


# ════════════════════════════════════════════════════════════════════════
# The Rally activation (gate Q3): authored command values light the texture
# ════════════════════════════════════════════════════════════════════════

class TestRallyActivation:
    def test_fast_tier_davout_and_charles(self, world):
        for name in ("Davout", "ArchdukeCharles"):
            assert world.get_marshal(name).get_rally_stages_per_turn() == 2, name

    @pytest.mark.parametrize("name", ["Mack", "Massena", "Buxhowden", "Hohenlohe"])
    def test_poor_tier_penalties_10pp_deeper(self, world, name):
        m = world.get_marshal(name)
        assert m.get_rally_stages_per_turn() == 1, name
        assert m.get_retreat_stage_penalty(0) == pytest.approx(0.55), name
        assert m.get_retreat_stage_penalty(1) == pytest.approx(0.40), name
        assert m.get_retreat_stage_penalty(2) == pytest.approx(0.25), name

    def test_standard_tier_byte_identical(self, world):
        # Command 4-7 is the unchanged baseline (Ney 7, Murat 5, Soult 6).
        for name in ("Ney", "Murat", "Soult"):
            m = world.get_marshal(name)
            assert m.get_rally_stages_per_turn() == 1, name
            assert m.get_retreat_stage_penalty(0) == pytest.approx(0.45), name

    def test_both_sides_same_methods(self, world):
        # GR5: the fast tier serves the enemy's best army (Charles) through
        # the SAME marshal methods the player's Davout uses.
        assert (world.get_marshal("ArchdukeCharles").get_rally_stages_per_turn()
                == world.get_marshal("Davout").get_rally_stages_per_turn())


# ════════════════════════════════════════════════════════════════════════
# Re-measures (memo §6.4): the MC-1 numbers at authored skills
# ════════════════════════════════════════════════════════════════════════

class TestReMeasures:
    def test_ney_bravest_relative_value_at_shock_9(self, world):
        # Shock multiplier is 1 + shock/20 (combat.py). At authored shock 9
        # the +2 ability moves 1.45 -> 1.55: ~+6.9% relative attack damage —
        # the memo's recorded +7% figure, under the ~+10% anchor.
        ney = world.get_marshal("Ney")
        shock = ney.get_effective_skill("shock")
        assert shock == 9
        relative = (1 + (shock + 2) / 20.0) / (1 + shock / 20.0) - 1
        assert relative == pytest.approx(0.069, abs=0.001)
        assert relative < 0.10

    def _arrival(self, world, marshal, primary, monkeypatch):
        monkeypatch.setattr(_random, "randint", lambda a, b: 0)  # variance 0
        return CommandExecutor()._combat._calculate_arrival_score(
            marshal, primary, world)

    def _stage_on_plains(self, world, *names):
        # Arrival scores read the DEPARTING region's terrain — stage the
        # marshals on a real plains province so the terrain mod is 0.
        plains = next(r.name for r in world.regions.values()
                      if r.terrain == "plains")
        for name in names:
            world.get_marshal(name).location = plains

    # MC-3 re-anchor: these blessed §6.4 numbers were measured at NEUTRAL
    # relationship (rel_mod 0). The original primary (Ney) gained authored
    # MC-3 edges with both mirror marshals (Lannes +1, Bernadotte -1), so the
    # measurement primary is now Soult — no authored edge with either. The
    # relationship-STACKED arrival numbers are pinned in the MC-3 file.

    def test_lannes_deterministic_base_90(self, world, monkeypatch):
        # 50 base + 20 (authored logistics 4) + 5 aggressive + 15 Roland = 90
        self._stage_on_plains(world, "Lannes", "Soult")
        lannes = world.get_marshal("Lannes")
        soult = world.get_marshal("Soult")
        assert self._arrival(world, lannes, soult, monkeypatch) == 90

    def test_bernadotte_deterministic_base_60(self, world, monkeypatch):
        # 50 base + 30 (authored logistics 6) - 5 cautious - 15 Eyes = 60
        self._stage_on_plains(world, "Bernadotte", "Soult")
        bernadotte = world.get_marshal("Bernadotte")
        soult = world.get_marshal("Soult")
        assert self._arrival(world, bernadotte, soult, monkeypatch) == 60

    def test_bernadotte_75_without_ability(self, world, monkeypatch):
        # The memo's stated baseline: 75 without Eyes on a Crown (his
        # logistics 6 blunts the penalty by +5 vs a flat-5 baseline).
        self._stage_on_plains(world, "Bernadotte", "Soult")
        bernadotte = world.get_marshal("Bernadotte")
        bernadotte.ability["name"] = "None"
        soult = world.get_marshal("Soult")
        assert self._arrival(world, bernadotte, soult, monkeypatch) == 75

    def test_bernadotte_70_under_written_support(self, world, monkeypatch):
        # The counter-lever: a written SUPPORT order mostly cancels the -15.
        self._stage_on_plains(world, "Bernadotte", "Soult")
        bernadotte = world.get_marshal("Bernadotte")
        bernadotte.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Soult", target_type="marshal",
            started_turn=1, original_command="Support Soult")
        soult = world.get_marshal("Soult")
        assert self._arrival(world, bernadotte, soult, monkeypatch) == 70

    def test_arrival_mirror_gap_is_30(self, world, monkeypatch):
        # The drama centerpiece blessed jointly: 90 vs 60 deterministic base.
        self._stage_on_plains(world, "Lannes", "Bernadotte", "Soult")
        soult = world.get_marshal("Soult")
        lannes_score = self._arrival(
            world, world.get_marshal("Lannes"), soult, monkeypatch)
        bernadotte_score = self._arrival(
            world, world.get_marshal("Bernadotte"), soult, monkeypatch)
        assert lannes_score - bernadotte_score == 30


# ════════════════════════════════════════════════════════════════════════
# Visual layer: the card ships hints + Rally tier/note (shown = applied)
# ════════════════════════════════════════════════════════════════════════

class TestCardPayload:
    def _cards(self, world):
        return {c["name"]: c for c in build_marshal_overview(world)}

    def test_card_skills_exclude_administration(self, world):
        for name, card in self._cards(world).items():
            assert set(card["skills"].keys()) == {
                "tactical", "shock", "defense", "logistics", "command"}, name

    def test_card_pins_authored_values(self, world):
        cards = self._cards(world)
        assert cards["Ney"]["skills"]["shock"] == 9
        assert cards["Murat"]["skills"]["defense"] == 2
        assert cards["Soult"]["skills"]["tactical"] == 9
        assert cards["Bernadotte"]["trust_value"] == 40
        assert cards["Bernadotte"]["trust_label"] == "Strained"
        assert cards["Davout"]["trust_value"] == 85
        assert cards["Davout"]["trust_label"] == "Loyal"

    def test_skill_notes_cover_exactly_the_wired_five(self, world):
        # A hint per displayed skill and none for hidden admin (GR9: the
        # card explains only what is wired).
        for name, card in self._cards(world).items():
            assert set(card["skill_notes"].keys()) == set(card["skills"].keys()), name
            for note in card["skill_notes"].values():
                assert note != "", name

    def test_rally_tier_fast_davout(self, world):
        card = self._cards(world)["Davout"]
        assert card["rally_tier"] == "fast"
        assert "2 stages/turn" in card["rally_note"]

    def test_rally_tier_poor_massena_note_shows_applied_numbers(self, world):
        # Shown = applied: the note's percentages derive from the marshal's
        # own get_retreat_stage_penalty, never a hardcoded table.
        card = self._cards(world)["Massena"]
        massena = world.get_marshal("Massena")
        assert card["rally_tier"] == "poor"
        expected = "/-".join(str(int(round(massena.get_retreat_stage_penalty(s) * 100)))
                             for s in (0, 1, 2))
        assert f"-{expected}%" in card["rally_note"]
        assert "-55/-40/-25%" in card["rally_note"]

    def test_rally_tier_standard_ships_empty_note(self, world):
        card = self._cards(world)["Ney"]
        assert card["rally_tier"] == "standard"
        assert card["rally_note"] == ""


# ════════════════════════════════════════════════════════════════════════
# Isolation: the legacy fixture/rollback roster is untouched by MC-2
# ════════════════════════════════════════════════════════════════════════

class TestLegacyRosterUntouched:
    def test_legacy_ney_keeps_authored_waterloo_skills(self):
        legacy = WorldState(player_nation="France")
        ney = legacy.get_marshal("Ney")
        # The Waterloo fixture's own authored values (marshal.py data), not
        # the 1805 table — MC-2 edits europe_1805.json only.
        assert ney.skills["tactical"] == 7
        assert ney.skills["defense"] == 4
        assert ney.trust.value == 75
