"""Row PT, slice D — the battle report tells the truth.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-D. (D1 shipped inside
PT-A2, as the spec requires, and is pinned in
`test_pt_a_regressions.py`.)

⚠ **D3's filed mechanism was REFUTED by the verification fleet and the
prescribed fix is deliberately NOT built.** The audit asked for the
post-battle classifier to be made symmetric like the preview. It must
not be: the arrival score reads `candidate.get_relationship(primary)`,
and the derived −1 applies only when the CANDIDATE is jealous, so a
jealous LEAD cannot depress the candidate's score and there is nothing
to misclassify. What survives is the hostile case, and that is what is
fixed here.
"""

from __future__ import annotations

import random
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.commands.combat_executor import CombatExecutor
from backend.game_logic.battle_report import _OBSERVATIONS, _pick_observation
from backend.game_logic.combat import CombatResolver

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


def _combat():
    return CombatExecutor(SimpleNamespace(combat_resolver=CombatResolver()))


@pytest.fixture()
def field():
    """A lead, a joiner one march away, an enemy on the field."""
    lead = MarshalFactory.infantry(name="Bernadotte", location="Belgium",
                                   strength=25000, personality="cautious")
    ally = MarshalFactory.infantry(name="Ney", location="Paris",
                                   strength=20000, personality="aggressive")
    enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                 nation="Austria", strength=22000,
                                 personality="cautious")
    world = WorldFactory.with_marshals([lead, ally, enemy])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.calculate_visibility()
    return world


def _withholds(world, lead_name="Bernadotte", enemy_name="Mack"):
    preview = _combat()._build_muster_preview(
        world.marshals[lead_name], world.marshals[enemy_name], world,
        {"world": world})
    return {r["marshal"]: r.get("withholds", "") for r in preview["rows"]}


# ═══════════════════════════════════════════════════════════════════════
# D2 — a pair property is not the joiner's personal state
# ═══════════════════════════════════════════════════════════════════════

class TestTheWithholdRowNamesTheRightMan:
    def test_a_jealous_lead_does_not_accuse_the_joiner(self, field):
        """THE MEASURED DEFECT, turn 7: the row on NEY read "but HE is
        nursing a grievance and will bring NOTHING". Ney held no
        grievance — Bernadotte, the LEAD, was `jealous_of: Ney`."""
        field.marshals["Bernadotte"].jealous_of = "Ney"
        field.marshals["Bernadotte"].personality = "aggressive"
        row = _withholds(field).get("Ney", "")
        assert row, "the fixture must produce a withholding row"
        assert "he is nursing a grievance" not in row
        assert "Bernadotte resents him" in row

    def test_a_jealous_joiner_still_reads_as_his_own_grievance(self, field):
        field.marshals["Ney"].jealous_of = "Bernadotte"
        row = _withholds(field).get("Ney", "")
        assert "he is nursing a grievance" in row

    def test_open_hostility_is_not_narrated_as_a_grievance(self, field):
        """The arm fires with NO jealousy at all: a −2 pair scales to 0.0,
        and such a marshal is eligible under a written SUPPORT order. A
        man marching on the player's own order was told he was sulking."""
        from backend.models.marshal import StrategicOrder

        ney = field.marshals["Ney"]
        ney.modify_relationship("Bernadotte", -2)
        field.marshals["Bernadotte"].modify_relationship("Ney", -2)
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Bernadotte",
            target_type="marshal", started_turn=field.current_turn,
            original_command="Ney, support Bernadotte")
        row = _withholds(field).get("Ney", "")
        assert row, "a hostile SUPPORT-ordered marshal must still row"
        assert "grievance" not in row
        assert "openly at odds" in row

    def test_the_half_weight_arm_is_untouched(self, field):
        """Already symmetric, and numerically exact: −1 → 0.50 is the only
        non-zero sub-1.0 value on the scale."""
        field.marshals["Ney"].modify_relationship("Bernadotte", -1)
        field.marshals["Bernadotte"].modify_relationship("Ney", -1)
        row = _withholds(field).get("Ney", "")
        assert "about half his weight" in row


# ═══════════════════════════════════════════════════════════════════════
# D3 — the surviving half: a hostile no-show is not the roads
# ═══════════════════════════════════════════════════════════════════════

class TestAHostileNoShowIsNamed:
    def test_a_hostile_no_show_is_classified_as_hostility(self, field):
        """Behavioural, through `_calculate_reinforcements`. The first
        draft grepped the source for the reason string and the mutation
        sweep walked straight through it — `elif False:` leaves the
        literal in the file.

        A −2 marshal is eligible ONLY under a written SUPPORT order,
        which forces `has_explicit_order` and so skips both existing
        overrides. He carries a −20 relationship modifier — the largest
        single term in the arrival score — and his failure always
        rendered as "could not reach the battlefield in time".
        """
        from backend.models.marshal import StrategicOrder

        ney = field.marshals["Ney"]
        ney.modify_relationship("Bernadotte", -2)
        field.marshals["Bernadotte"].modify_relationship("Ney", -2)
        ney.skills["logistics"] = 1          # ...and make the roll a loss
        ney.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Bernadotte",
            target_type="marshal", started_turn=field.current_turn,
            original_command="Ney, support Bernadotte")
        region = field.get_region("Paris")
        if region is not None:
            region.terrain = "mountains"

        random.seed(7)
        results = _combat()._calculate_reinforcements(
            field.marshals["Bernadotte"], field.marshals["Mack"],
            "Belgium", "France", field)
        row = next((r for r in results if r["marshal"] == "Ney"), None)
        assert row is not None, "the fixture must produce a reinforcement row"
        assert row["arrived"] is False, (
            "the fixture must actually produce a NO-SHOW or nothing is "
            "classified at all")
        assert row["reason"] == "hostility_withheld"

    def test_it_does_not_blame_the_roads(self):
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        arm = src.split('elif reason == "hostility_withheld":')[1].split(
            "else:")[0]
        assert "could not reach" not in arm
        assert "openly at odds" in arm

    def test_the_refuted_symmetric_change_was_NOT_made(self):
        """A negative pin, deliberately. The audit prescribed making the
        classifier symmetric; the fleet proved that would be wrong."""
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        arm = src.split('reason = "grievance_withheld"')[0].split(
            "elif (not has_explicit_order")[-1]
        assert 'getattr(candidate, "jealous_of", None)' in arm
        assert "primary.jealous_of" not in arm, (
            "a jealous LEAD cannot depress the candidate's arrival score, "
            "so there is nothing here to misclassify")


# ═══════════════════════════════════════════════════════════════════════
# D4 — a rout is news
# ═══════════════════════════════════════════════════════════════════════

class TestARoutIsReported:
    def _result(self, forced_retreat: bool, our_casualties: int = 5000):
        return {
            "outcome": "defender_victory",
            "attacker_nation": "France",
            "defender_nation": "Austria",
            "attacker": {"name": "Massena", "casualties": our_casualties,
                         "remaining": 14000, "morale": 20,
                         "forced_retreat": forced_retreat},
            "defender": {"name": "Mack", "casualties": 3000,
                         "remaining": 19000, "morale": 70,
                         "forced_retreat": False},
            "attacker_original_strength": 19000,
            "defender_original_strength": 22000,
            "modifier_snapshot": {"attacker": [], "defender": []},
        }

    def test_the_measured_case_is_no_longer_a_standard_affair(self):
        """`The Great Battle of Milan` — Massena routed, 26.2% casualties,
        just under the 30% `lost_costly` line — read "A standard affair.
        Nothing unusual to report."."""
        random.seed(3)
        observation = _pick_observation(self._result(True, 4978), "France")
        assert observation not in _OBSERVATIONS.get("default", [])
        assert observation in [
            line.replace("{marshal}", "Massena").replace("{enemy}", "Mack")
            for line in _OBSERVATIONS["routed"]]

    def test_a_battle_with_no_rout_is_unchanged(self):
        random.seed(3)
        assert _pick_observation(self._result(False, 4978), "France") not in [
            line.replace("{marshal}", "Massena").replace("{enemy}", "Mack")
            for line in _OBSERVATIONS["routed"]]

    def test_the_heavier_defeat_still_wins_the_ladder(self):
        """Priority order: `lost_costly` (>30%) sits ABOVE the rout arm,
        because the butcher's bill is the bigger news when it is that
        large."""
        random.seed(3)
        assert _pick_observation(self._result(True, 12000), "France") in [
            line.replace("{marshal}", "Massena").replace("{enemy}", "Mack")
            for line in _OBSERVATIONS["lost_costly"]]

    def test_the_arm_reads_the_players_own_side(self):
        """Perspective: when the player DEFENDS, his rout is the
        defender's."""
        from backend.game_logic.battle_report import _our_side

        result = self._result(True)
        assert _our_side(result, "France")["name"] == "Massena"
        assert _our_side(result, "Austria")["name"] == "Mack"

    def test_no_bank_was_shipped_that_cannot_fire(self):
        """Two thirds of the filed row are deliberately not built: at this
        seam the province is not yet known to have changed hands and
        `broken` lives on the Marshal, never on the payload. Shipping
        banks that cannot fire is the defect this row is about."""
        assert "lost_province" not in _OBSERVATIONS
        assert "morale_broken" not in _OBSERVATIONS


# ═══════════════════════════════════════════════════════════════════════
# D5 / D6 — one label, one truth
# ═══════════════════════════════════════════════════════════════════════

class TestTheTwoCasualtyFiguresAreDistinguished:
    def test_the_report_says_whose_losses_it_counts(self):
        """"Ney's army 8,141" and "Casualties: Ney 2,171" printed three
        rows apart under the identical word."""
        lead = MarshalFactory.infantry(name="Ney", location="Belgium",
                                       strength=18000)
        defender = MarshalFactory.enemy(name="Mack", location="Belgium",
                                        nation="Austria", strength=15000)
        battle_result = {
            "attacker": {"name": "Ney", "casualties": 8141},
            "defender": {"name": "Mack", "casualties": 4000},
            "battle_report": {"casualty_summary": {
                "attacker_original": 20171, "defender_original": 19000}},
        }
        _combat()._reconcile_report_survivors(battle_result, lead, defender)
        cs = battle_result["battle_report"]["casualty_summary"]
        assert cs["attacker_casualties"] == 2171
        assert cs["attacker_casualties_scope"] == "own corps"

    def test_a_solo_battle_keeps_the_bare_label(self):
        """Byte-identical where there is nothing to disambiguate."""
        lead = MarshalFactory.infantry(name="Ney", location="Belgium",
                                       strength=12000)
        defender = MarshalFactory.enemy(name="Mack", location="Belgium",
                                        nation="Austria", strength=15000)
        battle_result = {
            "attacker": {"name": "Ney", "casualties": 3000},
            "defender": {"name": "Mack", "casualties": 4000},
            "battle_report": {"casualty_summary": {
                "attacker_original": 15000, "defender_original": 19000}},
        }
        _combat()._reconcile_report_survivors(battle_result, lead, defender)
        cs = battle_result["battle_report"]["casualty_summary"]
        assert cs["attacker_casualties_scope"] == ""

    def test_the_client_renders_the_scope(self):
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert 'casualty.get("attacker_casualties_scope"' in src
        assert "atk_label" in src


class TestNoArmyLosesMoreMenThanItHad:
    def test_the_log_clamps_an_annihilation(self):
        """MEASURED: `Mack 15,815` casualties from a 15,437-man corps.
        Casualties are computed uncapped and `take_casualties` clamps the
        STRENGTH, not the number."""
        from backend.campaign_log import format_event_oneliner

        line = format_event_oneliner({
            "type": "battle", "turn": 4,
            "attacker": "Ney", "attacker_nation": "France",
            "defender": "Mack", "defender_nation": "Austria",
            "location": "Swabia", "outcome": "attacker_victory",
            "attacker_casualties": 2000, "defender_casualties": 15815,
            "attacker_strength_before": 20000,
            "defender_strength_before": 15437,
        })
        assert "15,437" in line
        assert "15,815" not in line

    def test_an_ordinary_battle_is_untouched(self):
        from backend.campaign_log import format_event_oneliner

        line = format_event_oneliner({
            "type": "battle", "turn": 4,
            "attacker": "Ney", "attacker_nation": "France",
            "defender": "Mack", "defender_nation": "Austria",
            "location": "Swabia", "outcome": "attacker_victory",
            "attacker_casualties": 2000, "defender_casualties": 4000,
            "attacker_strength_before": 20000,
            "defender_strength_before": 15437,
        })
        assert "4,000" in line

    def test_a_legacy_event_without_the_stamp_still_renders(self):
        from backend.campaign_log import format_event_oneliner

        line = format_event_oneliner({
            "type": "battle", "turn": 4,
            "attacker": "Ney", "attacker_nation": "France",
            "defender": "Mack", "defender_nation": "Austria",
            "location": "Swabia", "outcome": "attacker_victory",
            "attacker_casualties": 2000, "defender_casualties": 15815,
        })
        assert "15,815" in line

    def test_the_mechanical_figure_is_deliberately_untouched(self):
        """It feeds war exhaustion, the DR-1 out-bled predicate and the
        score. Clamping it would move M1-M7."""
        src = (REPO / "backend" / "game_logic" / "combat.py").read_text(
            encoding="utf-8")
        block = src.split('result_dict["log_battle_event"] = {')[1].split(
            "}")[0]
        assert '"defender_casualties": int(defender_casualties)' in block
        assert '"defender_strength_before"' in block


class TestTheClampCoversBothBuilders:
    """Review-fleet correction. `combat.py` has TWO `log_battle_event`
    builders — the solo one at `:1057` and `_build_deferred_result`'s at
    `:1486`, which is the COORDINATED path. PT-D6 stamped only the first,
    so the clamp (conditional on those keys) was inert on exactly the
    multi-marshal battles the audit measured."""

    def test_both_builders_stamp_pre_battle_strength(self):
        src = (REPO / "backend" / "game_logic" / "combat.py").read_text(
            encoding="utf-8")
        builders = src.split('"type": "battle",')
        assert len(builders) >= 3, "expected two log_battle_event builders"
        for body in builders[1:]:
            head = body.split("}")[0]
            assert '"defender_strength_before"' in head, (
                "a builder without the pair silently disables the clamp")
