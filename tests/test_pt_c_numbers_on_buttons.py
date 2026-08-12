"""Row PT, slice C — the numbers on the buttons.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-C.

* **PT-C1** Insist quotes -15 and the engine charges -18, and the branch
  that would disclose it is unreachable on the path that charges it.
  Landed WITH PT-B1, as the spec requires: at trust 17 the quoted -15
  lands on 2 and the real -18 lands on 0, and 0 is what fires the
  redemption event PT-B1 was destroying. The second bug hid the first.
* **PT-C2** the strategic buttons render authored constants while the
  handler applies tier-scaled values off the same objection dict.
* **PT-C3** Upkeep prints unsigned among nine signed siblings.
* **PT-C4** the dispatch's `(+N)` and the banner's `Net` measure different
  things and both claim to be "the turn's change".
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from backend.commands.defiance import (
    RELUCTANT_OBEDIENCE_PENALTY,
    describe_reluctant_obedience_cost,
)
from backend.commands.disobedience import _build_strategic_options
from backend.commands.objection_v2 import (
    COMPROMISE_TRUST_GAIN,
    ConcernLevel,
    calculate_trust_gain,
    get_insist_penalty,
    get_trust_tier,
)

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")


@pytest.fixture
def world():
    """The Butcher's Bill is Europe-scoped (N1), so the pin needs the real
    1805 board, exactly as `test_econ_war_coupling.py` does."""
    from backend.models.world_state import WorldState

    return WorldState.from_scenario(str(SCENARIO_PATH))


# ═══════════════════════════════════════════════════════════════════════
# PT-C1 — the surcharge is named, and disclosed where it is charged
# ═══════════════════════════════════════════════════════════════════════

class TestTheSurchargeIsDisclosed:
    def test_the_sentence_states_the_total_and_splits_it(self):
        line = describe_reluctant_obedience_cost(-18)
        assert "-18" in line
        assert "-15" in line, "the base the button quoted"
        assert "-3" in line, "and the surcharge it did not"

    def test_it_reads_the_applied_total_rather_than_re_deriving_it(self):
        """Shown == applied: the sentence cannot drift from the charge
        because it is handed the charge."""
        for total in (-8, -13, -15, -18, -23):
            line = describe_reluctant_obedience_cost(total)
            assert f"{total:+d}" in line
            assert f"{total - RELUCTANT_OBEDIENCE_PENALTY:+d}" in line

    def test_the_penalty_has_one_source(self):
        """It was an anonymous literal `-3` in two places."""
        src = (REPO / "backend" / "commands" / "defiance.py").read_text(
            encoding="utf-8")
        body = src.split("if outcome == \"failed_roll\":")[1].split(
            "return result")[0]
        assert "RELUCTANT_OBEDIENCE_PENALTY" in body
        assert "-3" not in body, "the magic number must be gone from the body"

    def test_both_failed_roll_paths_disclose(self):
        """Tactical AND strategic. The strategic twin had the identical
        silence.

        Bounded to the failed-roll BRANCH, not the file: the first draft
        asserted the helper's name appeared anywhere in the module, and
        the mutation sweep walked through it — deleting the call left the
        import line behind and the pin green.
        """
        meta = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        branch = meta.split("DEFIANCE ROLL FAILS")[1].split("BUG FIX #1")[0]
        assert "describe_reluctant_obedience_cost(" in branch

        strat = (REPO / "backend" / "commands"
                 / "strategic_executor.py").read_text(encoding="utf-8")
        sbranch = strat.split("STRATEGIC DEFIANCE ROLL FAILS")[1].split(
            "Trust penalty was already applied")[0]
        assert "describe_reluctant_obedience_cost(" in sbranch

    def test_the_disclosure_does_not_fake_a_defiance(self):
        """`_display_defiance_result` narrates an act of insubordination.
        The failed roll is the OPPOSITE — he obeyed. Routing it there to
        reach the number would have told the player a different lie."""
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        branch = src.split("DEFIANCE ROLL FAILS")[1].split(
            "BUG FIX #1")[0]
        # Comments in this branch DISCUSS the defiance key at length — the
        # pin is that no line SETS it.
        code = "\n".join(ln for ln in branch.splitlines()
                         if not ln.strip().startswith("#"))
        assert '"defiance"' not in code


class TestC1AndB1AreOneStory:
    def test_the_real_charge_crosses_the_redemption_threshold(self):
        """The measured case: Bernadotte at trust 17. At the quoted -15 he
        lands on 2 and nothing happens; at the real -18 he lands on 0 and
        the redemption event fires — the one PT-B1 was dropping."""
        from backend.commands.disobedience import DisobedienceSystem

        world = WorldFactory.basic()
        marshal = MarshalFactory.infantry(name="Bernadotte", location="Paris",
                                          strength=20000,
                                          personality="cautious")
        world.marshals["Bernadotte"] = marshal
        marshal.trust.set(17)

        tier = get_trust_tier(marshal.trust.value)
        quoted = get_insist_penalty(tier)
        assert marshal.trust.value + quoted > 0, (
            "the fixture must sit where the quote and the charge disagree "
            "about whether he breaks")
        assert marshal.trust.value + quoted + RELUCTANT_OBEDIENCE_PENALTY <= 0

        marshal.modify_trust(quoted + RELUCTANT_OBEDIENCE_PENALTY)
        event = DisobedienceSystem().check_redemption_threshold(marshal, world)
        assert event is not None, (
            "the real charge must reach the threshold — this is the event "
            "PT-B1 then destroyed")


# ═══════════════════════════════════════════════════════════════════════
# PT-C2 — the strategic buttons quote what the engine will do
# ═══════════════════════════════════════════════════════════════════════

def _options(trust_value, personality="aggressive", concern=None):
    marshal = MarshalFactory.infantry(name="Ney", location="Paris",
                                      strength=20000, personality=personality)
    marshal.trust.set(trust_value)
    return marshal, {
        o["type"]: o for o in _build_strategic_options(
            marshal, {"action": "attack", "target": "Mack"},
            {"action": "hold", "max_turns": 3},
            "Proceed with Hold", "Accept: Timed Hold (3 turns)", "HOLD",
            concern=concern)
    }


class TestTheStrategicButtonsAreDerived:
    @pytest.mark.parametrize("trust_value", [10, 35, 60, 90])
    def test_proceed_quotes_the_tier_penalty(self, trust_value):
        """-10 was correct only at TRUSTING. A WARY marshal's button said
        -10 and the handler charged -12."""
        marshal, opts = _options(trust_value)
        expected = get_insist_penalty(get_trust_tier(marshal.trust.value))
        assert opts["proceed"]["trust_change"] == expected

    @pytest.mark.parametrize("trust_value", [10, 35, 60, 90])
    def test_trust_quotes_the_scaled_gain(self, trust_value):
        """+12 was correct only at HOSTILE+EXTREME. At WARY+STRONG the
        button said +12 and the handler paid +6."""
        marshal, opts = _options(trust_value, concern=ConcernLevel.STRONG)
        expected = calculate_trust_gain(
            ConcernLevel.STRONG, get_trust_tier(marshal.trust.value))
        assert opts["preferred"]["trust_change"] == expected

    def test_compromise_stays_flat(self):
        """The one number that was already honest."""
        _m, opts = _options(50)
        assert opts["compromise"]["trust_change"] == COMPROMISE_TRUST_GAIN

    def test_the_wary_strong_divergence_is_closed(self):
        """The spec's worked example, end to end."""
        marshal, opts = _options(35, concern=ConcernLevel.STRONG)
        assert get_trust_tier(marshal.trust.value).name == "WARY"
        assert opts["proceed"]["trust_change"] == -12   # was quoted -10
        assert opts["preferred"]["trust_change"] == 6   # was quoted +12

    def test_a_literal_marshal_is_quoted_his_own_price(self):
        """`strategic_executor.py:1424` prices a literal's strategic order
        at 1; the button said 2 for everyone."""
        _m, opts = _options(50, personality="literal")
        assert opts["proceed"]["ap_cost"] == 1
        _m2, opts2 = _options(50, personality="aggressive")
        assert opts2["proceed"]["ap_cost"] == 2

    def test_the_default_concern_is_the_floor_not_a_guess(self):
        """The eight V1 call sites carry no concern. MODERATE is the level
        at which a strategic objection can be raised at all."""
        marshal, opts = _options(50)
        assert opts["preferred"]["trust_change"] == calculate_trust_gain(
            ConcernLevel.MODERATE, get_trust_tier(marshal.trust.value))

    def test_the_one_site_that_knows_the_concern_hands_it_over(self):
        """`strategic_executor`'s V2 fallback has the real level, so it
        must not let the builder fall back to the floor. Pinned at the
        CALL — a file-wide grep let the sweep delete the argument."""
        src = (REPO / "backend" / "commands"
               / "strategic_executor.py").read_text(encoding="utf-8")
        # Bounded by the call's own closing line, not by the first ")" —
        # the argument list contains an f-string with a paren in it.
        call = src.split("v1_options = _build_strategic_options(")[1].split(
            "\n                            )")[0]
        assert "concern=strategic_concern" in call


class TestTheSupportFallbackHasNumbersAtAll:
    def test_it_uses_the_type_names_the_client_matches_on(self):
        """Found by the verification fleet: these three used
        `insist`/`trust`/`compromise` while `_setup_strategic_buttons`
        matches `proceed`/`preferred` — so Insist and Trust rendered with
        NO numbers whatsoever."""
        src = (REPO / "backend" / "commands"
               / "strategic_executor.py").read_text(encoding="utf-8")
        block = src.split("Build relationship-specific options")[1].split(
            "# Fallback:")[0]
        assert '"type": "proceed"' in block
        assert '"type": "preferred"' in block
        assert block.count('"trust_change"') == 3
        assert block.count('"ap_cost"') == 3

    def test_the_client_matches_those_two_names(self):
        dialog = (SCRIPTS / "objection_dialog.gd").read_text(encoding="utf-8")
        assert '"proceed"' in dialog and '"preferred"' in dialog


# ═══════════════════════════════════════════════════════════════════════
# PT-C3 / PT-C4 — the end-turn line
# ═══════════════════════════════════════════════════════════════════════

class TestTheFinancialLineIsSigned:
    def test_upkeep_prints_its_sign(self):
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        line = next(ln for ln in src.splitlines()
                    if "| Upkeep:" in ln and "message +=" in ln)
        assert "Upkeep: -{upkeep_val}g" in line, (
            "Upkeep was the ONE subtractive term printed bare, mid-line "
            "between nine explicitly-negative siblings")

    def test_every_other_subtractive_term_still_signs_itself(self):
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        for term in ("Occupation", "Contributions", "Charges of Empire",
                     "Dotations", "Rentes", "Infrastructure", "Admiralty",
                     "Blockade", "Materiel"):
            assert re.search(rf'\| {term}: -\{{', src), term


class TestMaterielIsNamed:
    def test_the_tally_is_opened_where_the_window_opens(self):
        """Not in `advance_turn` — the enemy phase runs BEFORE it
        (`turn_manager.end_turn` :222 vs :292), so resetting there would
        wipe exactly the charges this names."""
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        head = src.split("treasury_before_turn = world.nation_gold.get")[1]
        assert "materiel_spent_this_turn = {}" in head.split("\n\n")[0]

    def test_the_charge_site_tallies_what_it_takes(self, world):
        """Behavioural, through the real post-combat pipeline. The first
        draft grepped the block for the field NAME and the sweep walked
        through it — the lookup line kept the name while the accumulation
        was gone."""
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import MATERIEL_RATE

        combat = CommandExecutor()._combat
        french = next(m for m in world.marshals.values()
                      if m.nation == "France")
        austrian = next(m for m in world.marshals.values()
                        if m.nation == "Austria")
        world.nation_gold["France"] = 5000
        world.nation_gold["Austria"] = 5000
        world.materiel_spent_this_turn = {}
        combat._post_combat_pipeline({
            "attacker": french, "defender": austrian,
            "defender_nation": "Austria",
            "battle_region": austrian.location,
            "outcome": "attacker_victory",
            "attacker_won": True, "defender_won": False,
            "attacker_casualties": 4000, "defender_casualties": 8000,
            "pre_battle_attacker_strength": french.strength,
            "pre_battle_defender_strength": austrian.strength,
            "battle_result": None, "conquered": False,
            "skip_log_battle_event": True, "skip_idle_reset": True,
            "skip_cannon_fire_record": True, "skip_diplo_record": True,
            "skip_war_damage": True, "skip_intel_update": True,
            "skip_coordination_clear": True, "skip_relationships": True,
            "skip_last_combat_result": True, "skip_exhaustion": True,
        }, world)
        assert world.materiel_spent_this_turn.get("France") == int(
            4000 * MATERIEL_RATE)
        assert world.materiel_spent_this_turn.get("Austria") == int(
            8000 * MATERIEL_RATE)

    def test_it_leaves_the_residual(self):
        """Named means removed from `Other` — otherwise it is counted
        twice or explained nowhere."""
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        other = src.split("other_val = net_val - (")[1].split(")")[0]
        assert "materiel_val" in other

    def test_the_tally_serializes(self):
        world = WorldFactory.basic()
        world.materiel_spent_this_turn = {"France": 137}
        from backend.models.world_state import WorldState

        restored = WorldState.from_dict(world.to_dict())
        assert restored.materiel_spent_this_turn == {"France": 137}


class TestTheDispatchSaysWhatItIs:
    def test_the_figure_is_labelled_as_a_component_sum(self):
        """Every NAMED component agrees on all 18 turns; only the total
        differs, because one surface sums declared components and the
        other measures the treasury."""
        from backend.game_logic.dispatch import build_morning_dispatch

        world = WorldFactory.basic()
        dispatch = build_morning_dispatch(world)
        situation = dispatch.get("situation", {})
        assert situation.get("treasury_delta_label"), (
            "the parenthetical must name its own basis")

    def test_both_client_surfaces_render_the_label(self):
        for name in ("main.gd", "dispatch_view.gd"):
            src = (SCRIPTS / name).read_text(encoding="utf-8")
            assert 'situation.get("treasury_delta_label"' in src, name
            assert "delta_suffix" in src, name
