"""IGR-E — "Plunder earns its prompt" (gate Q4, INGAME_REVIEW_FIXES_SPEC §5).

The July-25 in-game review measured plundering Nassau for **87 gold** against
a 3,085/turn income and a 5,177g treasury, and concluded that Secure was
strictly correct in every situation met — so a modal that stops the game was
asking a question with exactly one right answer.

The gate decided option (a): **plunder = province income x 4**, blessed as
`PLUNDER_INCOME_MULTIPLIER = 4`, in-band tunable, judged by a falsifiable
acceptance test:

    A turn-3 player holding under ~2,000g should plausibly choose Plunder;
    a turn-20 player holding over ~20,000g should not. If both still always
    Secure, the multiplier is too low -- NOT the design.

⚠ RECORDED DISSENT, carried from gate §5 Q4 so it cannot be lost: option (b)
— the stability-vs-authority recut — is arguably the better *design*, since it
deletes the balance-number problem entirely. (a) was taken because it is
in-band tunable. **If this acceptance test fails at TWO different multipliers,
re-open at (b) rather than tuning a third time.** Attempts used: ONE of two
(x4, and it PASSES — see TestTheFalsifiableAcceptanceTest below).

⚠ THE GATE'S WORKED EXAMPLE IS WRONG, and the landing record says so rather
than quietly conforming to it. Gate §5 Q4 illustrates option (a) as "Nassau
pays ~450-750g instead of 87g". Nassau's `income_value` is **50** — the
minimum on the whole 126-province map — so x4 pays **200g**. The 450-750 band
is 150 x 3-5, i.e. the MEDIAN province (41 of 126) labelled with the poorest
one's name. The gate's *shape* text ("~3-5 turns of its income") is what x4
actually satisfies, so the blessed constant stands and only the illustration
was mistaken. `test_the_gates_worked_example_is_wrong_and_this_pins_why`
pins the arithmetic so no future reader re-derives the confusion.

The slice's second half is the prompt itself: quadrupling a number the player
never sees changes no decision. Before IGR-E no surface — modal, terminal or
region panel — stated what Plunder would pay.
"""
import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.combat_executor import CombatExecutor
from backend.models.region import Region
from backend.models.world_state import (
    PLUNDER_INCOME_MULTIPLIER,
    WorldState,
    build_capture_choice,
    capture_choice_prompt,
    plunder_yield,
)

# The real income ladder of the shipped 1805 map, measured off
# create_europe_regions(): five values, 126 provinces.
#   50 x27 (rural, incl. NASSAU) | 100 x22 | 150 x41 (median) | 200 x16 | 300 x20
INCOME_LADDER = [50, 100, 150, 200, 300]
NASSAU_INCOME = 50      # the province the review actually plundered
MEDIAN_INCOME = 150     # the plurality province type


def _model_region(income: int) -> Region:
    """A bare province for the economics model — no buildings, like the
    shipped scenario (which authors zero buildings on all 126 provinces)."""
    return Region(name="Model", adjacent_regions=[], income_value=income)


def cumulative_net(income: int, stability: int, war_damage: float,
                   turns: int, garrisoned: bool = True) -> int:
    """Gold the OWNER nets from a conquered province over `turns` turns.

    THE published break-even model for IGR-E (three independent readers
    produced three different models during the ground-truth pass; this is
    the one the landing record publishes, and it is derived from the
    production formulas rather than restating them).

    Per turn, in the order world_state.advance_turn runs them:
      * process_stability_growth  -> +5, or +10 with a friendly marshal present
      * process_war_damage_recovery -> -0.02
      * income collected          -> Region.get_effective_income()
      * ES-2 occupation cost      -> income_value * Region.get_occupation_fraction()

    The occupation term is what makes this honest: it is charged on BASE
    income regardless of what the province actually yields, so the extra
    turns Plunder spends in a worse stability tier cost real gold.
    """
    region = _model_region(income)
    region.stability = stability
    region.war_damage = war_damage
    total = 0
    for _ in range(turns):
        region.stability = min(100, region.stability + (10 if garrisoned else 5))
        region.recover_war_damage(0.02)
        total += region.get_effective_income()
        total -= int(region.income_value * region.get_occupation_fraction())
    return total


def forgone_by_plundering(income: int, turns: int, garrisoned: bool = True) -> int:
    """What Plunder costs the owner over `turns` turns, versus Secure.

    Secure leaves stability 25 and no war damage; Plunder sets stability 10
    and adds 0.35 war damage (combat_executor._apply_plunder).
    """
    secure = cumulative_net(income, 25, 0.0, turns, garrisoned)
    plunder = cumulative_net(income, 10, 0.35, turns, garrisoned)
    return secure - plunder


class TestTheBlessedNumber:
    """The gate's decision, as a constant."""

    def test_constant_is_four_under_the_name_the_gate_blessed(self):
        assert PLUNDER_INCOME_MULTIPLIER == 4.0

    def test_the_constant_stays_inside_the_blessed_band(self):
        """Option (a) states the band as "~3-5 turns of its income".

        Tuning inside 3..5 is delegated; leaving it is a SHAPE change that
        escalates to the user (and, per the dissent, to option (b)).
        """
        assert 3.0 <= PLUNDER_INCOME_MULTIPLIER <= 5.0

    def test_it_is_a_single_source(self):
        """GR1: one multiplier, no second copy anywhere on the path."""
        assert CombatExecutor.PLUNDER_INCOME_MULTIPLIER == PLUNDER_INCOME_MULTIPLIER
        assert CommandExecutor.PLUNDER_INCOME_MULTIPLIER == PLUNDER_INCOME_MULTIPLIER

    def test_plunder_yield_is_the_one_expression_that_pays(self):
        """The preview and the payout must be the same expression, not two
        copies of it — otherwise a quoted figure can drift from a paid one."""
        world = WorldState(player_nation="France")
        region = world.regions["Paris"]
        executor = CommandExecutor()
        before = world.nation_gold["France"]
        result = executor._apply_plunder(region, world)
        assert result["gold_gained"] == plunder_yield(region)
        assert world.nation_gold["France"] - before == plunder_yield(region)

    def test_the_measured_payout_across_the_real_income_ladder(self):
        """The whole table, pinned, so a retune is visible in one diff."""
        assert [plunder_yield(_model_region(i)) for i in INCOME_LADDER] == [
            200, 400, 600, 800, 1200,
        ]

    def test_plunder_reads_base_income_never_effective(self):
        """A just-captured province sits at stability <= 25, where the
        stability modifier is 0.0. Reading effective income would pay
        exactly 0 on every province in the game — which is precisely the
        live W6-8 estate-windfall bug (routed as IGR-X4). Do not repeat it."""
        region = _model_region(MEDIAN_INCOME)
        region.stability = 10
        assert region.get_effective_income() == 0
        assert plunder_yield(region) == 600

    def test_the_gates_worked_example_is_wrong_and_this_pins_why(self):
        """Gate §5 Q4: "Nassau pays ~450-750g". It does not, and cannot.

        450-750 is the MEDIAN province at the gate's own 3-5x band. Nassau
        is the map MINIMUM. Both facts pinned so the discrepancy is a
        recorded correction rather than a rediscovery.
        """
        assert plunder_yield(_model_region(NASSAU_INCOME)) == 200
        assert 450 <= plunder_yield(_model_region(MEDIAN_INCOME)) <= 750
        # To make Nassau itself pay 450 the multiplier would have to be 9x.
        assert NASSAU_INCOME * 9 == 450


class TestTheFalsifiableAcceptanceTest:
    """THE DEFINITION OF DONE for IGR-E.

    Arm A — a poor, early player plausibly plunders.
    Arm B — a rich, late player does not.

    Both arms are judged on two things a player actually weighs: what the
    loot is worth against the purse in hand, and what it costs against the
    revenue given up. Neither arm is a matter of taste; both are arithmetic
    over the production formulas.

    Baseline note, recorded rather than assumed: a PASSIVE ambient France
    measures 3,565g on turn 3 and 19,014g on turn 20, so neither of the
    gate's anchors ("under ~2,000g", "over ~20,000g") is hit by a France
    that does nothing. A France that plays spends, so the poor-early arm is
    reachable; these fixtures therefore set the purse explicitly to the
    gate's own thresholds instead of inheriting an idle baseline.
    """

    POOR_PURSE = 2000       # gate's "under ~2,000g" at turn 3
    RICH_PURSE = 20000      # gate's "over ~20,000g" at turn 20
    EARLY_HORIZON = 5       # turns a turn-3 player is playing for
    LATE_HORIZON = 30       # turns a turn-20 player will hold the province

    def test_arm_a_a_poor_early_player_plausibly_plunders(self):
        """Two conditions, both required.

        (1) The loot is a MATERIAL share of the purse — it changes what the
            player can do next turn (a corps costs thousands).
        (2) Over the horizon a scrambling player actually plays for, the
            loot EXCEEDS the revenue it destroys.
        """
        for income in (NASSAU_INCOME, MEDIAN_INCOME):
            loot = plunder_yield(_model_region(income))
            share = loot / self.POOR_PURSE
            cost = forgone_by_plundering(income, self.EARLY_HORIZON)
            assert share >= 0.10, (
                f"income {income}: loot {loot} is only {share:.1%} of a poor "
                f"purse — immaterial, so Secure stays automatic")
            assert loot > cost, (
                f"income {income}: loot {loot} <= {cost} forgone over "
                f"{self.EARLY_HORIZON} turns — Plunder is strictly wrong")

    def test_arm_b_a_rich_late_player_does_not_plunder(self):
        """The mirror. Plunder must not become the new always-right answer —
        that would be the same defect wearing the other hat.

        (1) The loot is IMMATERIAL against a late-game purse.
        (2) Over a horizon a settled empire holds the province for, the loot
            no longer beats the revenue it destroys by any margin worth the
            unrest — it converges to break-even.
        """
        for income in INCOME_LADDER:
            loot = plunder_yield(_model_region(income))
            share = loot / self.RICH_PURSE
            cost = forgone_by_plundering(income, self.LATE_HORIZON)
            assert share <= 0.06, (
                f"income {income}: loot {loot} is {share:.1%} of a rich "
                f"purse — still tempting late, multiplier too high")
            assert loot <= cost * 1.10, (
                f"income {income}: loot {loot} still beats {cost} forgone "
                f"over {self.LATE_HORIZON} turns by >10% — Plunder is "
                f"free money for a settled empire")

    def test_the_choice_inverts_with_the_horizon_which_is_the_whole_point(self):
        """Short horizon favours Plunder, long horizon favours Secure. That
        inversion is what makes the modal a decision rather than a quiz."""
        income = MEDIAN_INCOME
        loot = plunder_yield(_model_region(income))
        assert loot > forgone_by_plundering(income, self.EARLY_HORIZON)
        assert loot <= forgone_by_plundering(income, self.LATE_HORIZON) * 1.10

    def test_the_acceptance_test_can_fail_negative_control(self):
        """FALSIFIABILITY. At the OLD x1.75 the poor-early arm fails on both
        of its conditions — which is exactly what the review reported. A test
        that could not fail would not be evidence that x4 fixed anything.
        """
        old = 1.75
        for income in (NASSAU_INCOME, MEDIAN_INCOME):
            old_loot = int(income * old)
            material = old_loot / self.POOR_PURSE >= 0.10
            worth_it = old_loot > forgone_by_plundering(
                income, self.EARLY_HORIZON)
            # Arm A is a CONJUNCTION, so the control asserts the conjunction
            # fails — not that both halves do. At x1.75 the rural province
            # fails both (87g = 4.4% of the purse, and less than it costs);
            # the median province clears materiality at 262g/13.1% but is
            # still strictly worse than securing, which is the review's
            # finding in one line.
            assert not (material and worth_it), (
                f"income {income}: x1.75 should NOT satisfy arm A — if it "
                f"does, this control has stopped discriminating and the "
                f"acceptance test is no longer evidence of anything")
        # And the sharper half of the review's own case, pinned exactly.
        assert int(NASSAU_INCOME * old) == 87

    def test_the_published_break_even_model(self):
        """The single model the landing record publishes, pinned.

        Scale-free: both loot and forgone revenue are linear in income, so
        the verdict is identical at every tier.
        """
        for income in INCOME_LADDER:
            loot = plunder_yield(_model_region(income))
            early = forgone_by_plundering(income, 5)
            late = forgone_by_plundering(income, 30)
            assert loot > early
            assert late > early           # the cost keeps accruing
            assert abs(loot - late) / loot < 0.15   # and converges on the loot


class TestThePromptIsPriced:
    """"Earns its prompt" — the modal must state its terms.

    Before IGR-E the stage-1 payload carried three keys, none economic; the
    buttons were string literals; the terminal asked "How shall they
    behave?"; and the nearest indirect surface (the Region Action Panel)
    shows EFFECTIVE income, which for a just-captured province is 0g.
    """

    def _capture_lyon(self):
        world = WorldState(player_nation="France")
        world.regions["Paris"].controller = "France"
        lyon = world.regions["Lyon"]
        lyon.controller = "Britain"
        lyon.stability = 80
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strength = 30000
        return world, lyon, ney

    def test_the_payload_quotes_what_plunder_will_pay(self):
        world, lyon, ney = self._capture_lyon()
        payload = build_capture_choice(world, lyon, ney.name, "Britain")
        assert payload["plunder_gold"] == plunder_yield(lyon)
        assert payload["region"] == "Lyon"

    def test_shown_equals_applied(self):
        """The figure quoted BEFORE the choice is the figure paid AFTER it.

        This is the MC-2/Q3 shown=applied discipline. It holds structurally
        because both call world_state.plunder_yield.
        """
        world, lyon, ney = self._capture_lyon()
        world.pending_capture_choice = build_capture_choice(
            world, lyon, ney.name, "Britain")
        quoted = world.pending_capture_choice["plunder_gold"]
        lyon.controller = "France"
        before = world.nation_gold["France"]
        result = CommandExecutor().handle_capture_choice(
            "plunder", {"world": world})
        assert result["success"]
        assert world.nation_gold["France"] - before == quoted

    def test_both_capture_routes_price_the_question(self):
        """Instant capture and occupation-completion are two different
        builders. Pricing only one leaves the fortified-province capture —
        the harder, more consequential fight — rendering a blank figure."""
        world, lyon, ney = self._capture_lyon()
        lyon.controller = "France"
        message = world._apply_occupation_capture_effects(ney, "Lyon")
        pending = world.pending_capture_choice
        assert pending["plunder_gold"] == plunder_yield(lyon)
        assert f"{plunder_yield(lyon):,}" in message

    def test_the_terminal_path_names_the_figure_too(self):
        """A player answering by typing must not have less information than
        one answering by clicking."""
        world, lyon, ney = self._capture_lyon()
        payload = build_capture_choice(world, lyon, ney.name, "Britain")
        sentence = capture_choice_prompt(payload)
        assert f"{payload['plunder_gold']:,}" in sentence
        # BUG-CA-10: always enumerate the answers the game will accept.
        assert "'plunder'" in sentence and "'secure'" in sentence

    def test_a_refused_answer_restates_the_price(self):
        """A wrong token must not cost the player the figure."""
        world, lyon, ney = self._capture_lyon()
        lyon.controller = "France"
        world.pending_capture_choice = build_capture_choice(
            world, lyon, ney.name, "Britain")
        result = CommandExecutor().handle_capture_choice(
            "burn it", {"world": world})
        assert not result["success"]
        assert f"{plunder_yield(lyon):,}" in result["message"]

    def test_stage_one_now_carries_a_dialogue_id(self):
        """W6-0. Stage 1 never minted one, so the stale-answer guard was
        structurally inert (it requires BOTH operands non-None). That was
        survivable while the buttons were generic; once a button asserts a
        gold figure about a NAMED province, a mis-slotted answer is a lie
        on screen — and the single pending slot is genuinely contended."""
        world, lyon, ney = self._capture_lyon()
        payload = build_capture_choice(world, lyon, ney.name, "Britain")
        assert isinstance(payload["dialogue_id"], int)

    def test_a_stale_answer_is_now_refused_instead_of_misapplied(self):
        world, lyon, ney = self._capture_lyon()
        lyon.controller = "France"
        world.pending_capture_choice = build_capture_choice(
            world, lyon, ney.name, "Britain")
        stale = world.pending_capture_choice["dialogue_id"] + 99
        before = world.nation_gold["France"]
        result = CommandExecutor().handle_capture_choice(
            "plunder", {"world": world}, dialogue_id=stale)
        assert not result["success"]
        assert result.get("stale_dialogue") is True
        assert world.nation_gold["France"] == before

    def test_the_two_builders_agree_on_shape(self):
        """If they ever diverge again, the client renders a blank on one
        route and nobody notices until a live pass."""
        world, lyon, ney = self._capture_lyon()
        a = build_capture_choice(world, lyon, ney.name, "Britain")
        lyon.controller = "France"
        world._apply_occupation_capture_effects(ney, "Lyon")
        b = world.pending_capture_choice
        assert set(a) == set(b)

    def test_the_payload_survives_serialization(self):
        """pending_capture_choice is serialized wholesale, so a save taken
        mid-question must reload with its price intact."""
        world, lyon, ney = self._capture_lyon()
        world.pending_capture_choice = build_capture_choice(
            world, lyon, ney.name, "Britain")
        restored = WorldState.from_dict(world.to_dict())
        assert (restored.pending_capture_choice["plunder_gold"]
                == world.pending_capture_choice["plunder_gold"])
        assert (restored.pending_capture_choice["dialogue_id"]
                == world.pending_capture_choice["dialogue_id"])


class TestTheAICanActuallyPlunder:
    """IGR-E addendum — GR5, the half that made the windfall player-only.

    Both AI capture sites read `getattr(marshal, 'personality_type', None)`
    and compared it to a `Personality` member. `Marshal` has no such
    attribute (it carries `personality` as a plain string), so the read was
    always None and **the AI could never plunder, on any board, ever**.
    Measured before the fix on the pinned 40-turn ambient run: 41 AI
    capture-choice calls, 100% `secure`, 0 plunder gold. After: 39 secure /
    2 plunder, both by Britain's Paget — the only aggressive non-France
    marshal to reach a capture in that run.

    The second trap, which a careless fix walks straight into: `Personality`
    is a plain `Enum` with no `str` mixin, so `Personality.AGGRESSIVE ==
    'aggressive'` is False. Reading the *right* attribute while still
    comparing against the member leaves the branch just as dead.
    """

    def _world(self):
        world = WorldState(player_nation="France")
        region = world.regions["Paris"]
        region.controller = "France"
        region.stability = 80
        return world, region

    def test_the_enum_does_not_compare_equal_to_its_own_string(self):
        """Pins the trap itself, so a future 'simplification' back to the
        enum comparison fails loudly instead of silently re-killing it."""
        from backend.models.personality import Personality
        assert Personality.AGGRESSIVE != "aggressive"

    def test_an_aggressive_ai_marshal_plunders(self):
        from backend.models.world_state import ai_prefers_plunder
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        assert ai_prefers_plunder(marshal) is True
        CommandExecutor()._apply_ai_capture_choice(marshal, region, world)
        assert region.stability == 10
        assert region.plundered is True

    def test_a_cautious_ai_marshal_secures(self):
        world, region = self._world()
        marshal = world.get_marshal("Wellington")
        marshal.personality = "cautious"
        CommandExecutor()._apply_ai_capture_choice(marshal, region, world)
        assert region.stability == 25
        assert region.plundered is False

    def test_the_ai_is_paid_exactly_the_player_rate(self):
        """GR5: the same modal, the same money. Not 'about the same'."""
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        before = world.nation_gold.get(marshal.nation, 0)
        CommandExecutor()._apply_ai_capture_choice(marshal, region, world)
        assert world.nation_gold[marshal.nation] - before == plunder_yield(region)

    def test_the_occupation_route_is_fixed_too(self):
        """There are TWO AI branches, and the second is a hand-inlined
        duplicate rather than a call — fixing only the first leaves
        fortified-province captures unable to plunder."""
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        marshal.nation = "Britain"
        before = world.nation_gold.get("Britain", 0)
        world._apply_occupation_capture_effects(marshal, region.name)
        assert world.nation_gold["Britain"] - before == plunder_yield(region)
        assert region.stability == 10

    def test_no_pending_choice_is_raised_for_an_ai_capture(self):
        """The AI decides by rule; it must never queue the player's modal."""
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        marshal.nation = "Britain"
        world._apply_occupation_capture_effects(marshal, region.name)
        assert world.pending_capture_choice is None


class TestTheClientRendersIt:
    """The backend can price the question all it likes; the modal is where
    the player reads it. capture_choice_dialog.gd is NOT in the committed
    parse harness (it is instantiated at runtime by dialog_manager, not
    embedded in main.tscn), so a defect here passes the harness and shows
    only in a live boot — hence a text pin as well as the boot check.
    """

    GD = ("godot-client/project-sovereign/scripts/capture_choice_dialog.gd")

    def _source(self):
        import io
        return io.open(self.GD, encoding="utf-8").read()

    def test_the_plunder_button_reads_the_priced_key(self):
        src = self._source()
        assert 'data.get("plunder_gold"' in src

    def test_the_plunder_button_formats_the_number_into_its_label(self):
        src = self._source()
        assert "+%d gold" in src
        assert "% plunder_gold" in src

    def test_the_generic_unpriced_label_is_gone(self):
        """The exact string the review saw. If it comes back, the slice has
        been reverted at the only surface the player actually reads."""
        assert "PLUNDER (Loot gold, destroy buildings" not in self._source()
