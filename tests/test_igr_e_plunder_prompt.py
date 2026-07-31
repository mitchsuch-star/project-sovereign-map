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
    EUROPE_INFRASTRUCTURE_UPKEEP,
    PLUNDER_INCOME_MULTIPLIER,
    WorldState,
    ai_prefers_plunder,
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
                   turns: int, garrisoned: bool = True,
                   damaged_buildings: int = 0) -> int:
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
      * EC-U2 infrastructure bill -> EUROPE_INFRASTRUCTURE_UPKEEP per
        standing structure (post-landing review #2 — a DAMAGED building
        yields nothing yet is still billed, which is the term the first
        cut of this model omitted)

    The occupation term is what makes this honest: it is charged on BASE
    income regardless of what the province actually yields, so the extra
    turns Plunder spends in a worse stability tier cost real gold.

    `damaged_buildings` models Secure's aftermath pessimally: the enemy's
    structures survive DAMAGED — producing nothing until a 150g + 1-AP
    repair, but billed every turn. (A rational owner repairs; the repair
    restores function whose value is partly military — forts defend,
    depots supply — and gold cannot price that, so the model does not try.)
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
        total -= damaged_buildings * EUROPE_INFRASTRUCTURE_UPKEEP
    return total


def forgone_by_plundering(income: int, turns: int, garrisoned: bool = True,
                          buildings: int = 0) -> int:
    """What Plunder costs the owner over `turns` turns, versus Secure.

    Secure leaves stability 25, no war damage, and the province's
    structures DAMAGED (still billed, per EC-U2); Plunder sets stability
    10, adds 0.35 war damage, and deletes the structures — bill and asset
    together (combat_executor._apply_plunder).
    """
    secure = cumulative_net(income, 25, 0.0, turns, garrisoned,
                            damaged_buildings=buildings)
    plunder = cumulative_net(income, 10, 0.35, turns, garrisoned,
                             damaged_buildings=0)
    return secure - plunder


class TestTheBlessedNumber:
    """The gate's decision, as a constant."""

    def test_constant_is_four_under_the_name_the_gate_blessed(self):
        assert PLUNDER_INCOME_MULTIPLIER == 4.0

    def test_the_constant_stays_inside_the_blessed_band(self):
        """Option (a) states the band as "~3-5 turns of its income".

        Tuning inside 3..5 is delegated; leaving it is a SHAPE change that
        escalates to the user (and, per the dissent, to option (b)).

        Post-landing review #6, stated plainly rather than implied: the
        band is PERMISSION TO TRY, not a promise that every value in it
        passes. The acceptance criteria as calibrated admit exactly x4 —
        arm A's materiality floor puts the rural province on the 10% line
        at the gate's own 2,000g anchor (int(50*4)=200 = 10.0%), and arm
        B's ceiling binds at the capital tier. A retune inside the band
        must re-run this file; the acceptance test is the judge.
        """
        assert 3.0 <= PLUNDER_INCOME_MULTIPLIER <= 5.0

    def test_it_is_a_single_source(self, monkeypatch):
        """GR1, falsifiably (post-landing review #7): move the module
        constant and the PAYING expression must move with it — proving
        _apply_plunder carries no hardcoded second copy. The first cut of
        this test asserted equality over executor class attributes that no
        production code reads, so hardcoding plunder_yield would have left
        all 30 tests green.
        """
        # The import-time aliases kept for legacy tests still agree...
        assert CombatExecutor.PLUNDER_INCOME_MULTIPLIER == PLUNDER_INCOME_MULTIPLIER
        assert CommandExecutor.PLUNDER_INCOME_MULTIPLIER == PLUNDER_INCOME_MULTIPLIER
        # ...and the live proof: patch the module constant, the payout moves.
        import backend.models.world_state as ws
        monkeypatch.setattr(ws, "PLUNDER_INCOME_MULTIPLIER", 7.0)
        assert ws.plunder_yield(_model_region(100)) == 700
        world = WorldState(player_nation="France")
        region = world.regions["Paris"]
        before = world.nation_gold["France"]
        result = CommandExecutor()._apply_plunder(region, world)
        assert result["gold_gained"] == int(region.income_value * 7.0)
        assert world.nation_gold["France"] - before == result["gold_gained"]

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
    # The arms' thresholds, named once so the negative control judges the
    # SAME predicate the arms do (post-landing review #8 — the first cut
    # retyped 0.10 in the control, so weakening the arm left it green).
    MATERIALITY_FLOOR = 0.10    # arm A: loot must be >= this share of the purse
    IMMATERIALITY_CEIL = 0.06   # arm B: loot must be <= this share of the purse
    CONVERGENCE_TOL = 1.10      # arm B: loot within 10% of the long-run cost

    @classmethod
    def _arm_a_holds(cls, loot: int, purse: int, cost: int) -> bool:
        """Arm A's whole predicate, used by the arm AND the control."""
        return (loot / purse >= cls.MATERIALITY_FLOOR) and (loot > cost)

    def test_arm_a_a_poor_early_player_plausibly_plunders(self):
        """Two conditions, both required. Model: bare province (the boot
        board authors zero buildings), garrisoned (+10 stability growth).

        (1) The loot is a MATERIAL share of the purse — it changes what the
            player can do next turn (a corps costs thousands).
        (2) Over the horizon a scrambling player actually plays for, the
            loot EXCEEDS the revenue it destroys.
        """
        for income in (NASSAU_INCOME, MEDIAN_INCOME):
            loot = plunder_yield(_model_region(income))
            share = loot / self.POOR_PURSE
            cost = forgone_by_plundering(income, self.EARLY_HORIZON)
            assert share >= self.MATERIALITY_FLOOR, (
                f"income {income}: loot {loot} is only {share:.1%} of a poor "
                f"purse — immaterial, so Secure stays automatic")
            assert loot > cost, (
                f"income {income}: loot {loot} <= {cost} forgone over "
                f"{self.EARLY_HORIZON} turns — Plunder is strictly wrong")
            assert self._arm_a_holds(loot, self.POOR_PURSE, cost)

    def test_arm_b_a_rich_late_player_does_not_plunder(self):
        """The mirror. Plunder must not become the new always-right answer —
        that would be the same defect wearing the other hat.

        Model disclosure (post-landing review #3): bare province,
        garrisoned=True — the same assumptions as arm A, stated because
        they are load-bearing. Under them the long-run gold CONVERGES to
        near-break-even (plunder keeps a sliver of an edge, <= 4%
        measured); the true inversion exists ungarrisoned and is pinned in
        its own test below. Arm B's protection is therefore BOTH halves:
        (1) the loot is IMMATERIAL against a late-game purse (this is the
            half that carries the design weight), and
        (2) the long-run gold offers no margin worth the unrest — within
            10% of break-even at every tier.
        """
        for income in INCOME_LADDER:
            loot = plunder_yield(_model_region(income))
            share = loot / self.RICH_PURSE
            cost = forgone_by_plundering(income, self.LATE_HORIZON)
            assert share <= self.IMMATERIALITY_CEIL, (
                f"income {income}: loot {loot} is {share:.1%} of a rich "
                f"purse — still tempting late, multiplier too high")
            assert loot <= cost * self.CONVERGENCE_TOL, (
                f"income {income}: loot {loot} beats {cost} forgone over "
                f"{self.LATE_HORIZON} turns by >10% — Plunder is "
                f"free money for a settled empire")

    def test_convergence_garrisoned_and_true_inversion_ungarrisoned(self):
        """Renamed from `..._inverts_with_the_horizon_...` (post-landing
        review #3): under garrisoned=True the forgone revenue plateaus just
        BELOW the loot at every tier, so the garrisoned bare-province
        choice CONVERGES to near-break-even rather than inverting —
        plunder keeps a small permanent edge (600 vs 581 at the median).
        The TRUE inversion exists ungarrisoned: without the +10 growth the
        province lingers in the punitive tiers longer and the 30-turn
        forgone revenue EXCEEDS the loot. Both facts pinned so the record
        cites them precisely instead of claiming an inversion the model
        does not produce.
        """
        income = MEDIAN_INCOME
        loot = plunder_yield(_model_region(income))
        forgone_garrisoned = forgone_by_plundering(
            income, self.LATE_HORIZON, garrisoned=True)
        assert forgone_garrisoned < loot          # plunder keeps a sliver...
        assert loot <= forgone_garrisoned * self.CONVERGENCE_TOL  # ...within 10%
        forgone_ungarrisoned = forgone_by_plundering(
            income, self.LATE_HORIZON, garrisoned=False)
        assert forgone_ungarrisoned > loot        # the real inversion

    def test_on_a_built_province_razing_pays_and_is_multiplier_invariant(self):
        """The EC-U2 interaction, published rather than hidden (post-landing
        review #2 — the term the model's first cut omitted).

        Secure keeps the enemy's structures DAMAGED: producing nothing
        until a 150g + 1-AP repair, yet billed EUROPE_INFRASTRUCTURE_UPKEEP
        every turn. Plunder deletes bill and asset together. On a province
        carrying enemy structures the gold therefore favours razing at ANY
        multiplier — including 0: one building's 30-turn bill (1,200g)
        alone exceeds the whole bare-province revenue gap (581g at the
        median).

        This is NOT an acceptance failure of the blessed x4 and does NOT
        touch the dissent counter: the acceptance test judges the
        MULTIPLIER, and a term invariant to the multiplier cannot be moved
        by re-tuning it. The design question — whether shedding the EC-U2
        bill by razing is too attractive — is homed at the econ gate
        (BUG_FIXES.md IGR-X9). The counterweight gold cannot price is the
        structures' function: forts defend, depots supply.
        """
        income = MEDIAN_INCOME
        cost_bare = forgone_by_plundering(income, self.LATE_HORIZON)
        cost_built = forgone_by_plundering(income, self.LATE_HORIZON,
                                           buildings=1)
        assert cost_built == cost_bare - (
            self.LATE_HORIZON * EUROPE_INFRASTRUCTURE_UPKEEP)
        assert cost_built < 0, (
            "one damaged building's bill should exceed the revenue gap — "
            "razing wins on gold even at multiplier 0")

    def test_the_acceptance_test_can_fail_negative_control(self):
        """FALSIFIABILITY. At the OLD x1.75 arm A fails — which is exactly
        what the review reported. A test that could not fail would not be
        evidence that x4 fixed anything.

        Judged through arm A's OWN predicate (`_arm_a_holds`), not a
        retyped copy of it (post-landing review #8), plus one leg aimed
        squarely at the materiality floor: at x1.75 the review's own case
        (87g) must sit BELOW the floor, so weakening the floor breaks this
        control even though the worth-it half fails at 1.75 either way.
        """
        old = 1.75
        for income in (NASSAU_INCOME, MEDIAN_INCOME):
            old_loot = int(income * old)
            cost = forgone_by_plundering(income, self.EARLY_HORIZON)
            assert not self._arm_a_holds(old_loot, self.POOR_PURSE, cost), (
                f"income {income}: x1.75 should NOT satisfy arm A — if it "
                f"does, this control has stopped discriminating and the "
                f"acceptance test is no longer evidence of anything")
        # The materiality-floor leg: the review's measured 87g is 4.35% of
        # the gate's poor purse and must fail the floor on its own.
        assert int(NASSAU_INCOME * old) == 87
        assert 87 / self.POOR_PURSE < self.MATERIALITY_FLOOR

    def test_the_published_break_even_model(self):
        """The single model the landing record publishes, pinned.

        Scale-free: both loot and forgone revenue are linear in income, so
        the verdict is identical at every tier. Bare province, garrisoned —
        the built-province case is its own test above.
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

    def test_a_pre_igr_e_save_is_backfilled_with_the_real_price(self):
        """Post-landing review #4. A pre-IGR-E autosave can carry a LIVE
        stage-1 question without the priced keys (meta_executor sets the
        pending choice during turn resolution and autosaves after) — the
        button would then read "+0 gold" while clicking pays the real sum,
        which is the exact shown≠applied lie this slice removed. from_dict
        backfills the price from the live region at load.
        """
        world, lyon, ney = self._capture_lyon()
        world.pending_capture_choice = build_capture_choice(
            world, lyon, ney.name, "Britain")
        save = world.to_dict()
        # Strip the payload back to its pre-IGR-E three-key shape.
        save["pending_capture_choice"] = {
            "region": "Lyon", "capturer": ney.name,
            "previous_controller": "Britain",
        }
        restored = WorldState.from_dict(save)
        assert (restored.pending_capture_choice["plunder_gold"]
                == plunder_yield(restored.get_region("Lyon")))
        # dialogue_id is deliberately NOT invented for an old question —
        # it stays unguarded, which is the pre-slice behaviour.
        assert "dialogue_id" not in restored.pending_capture_choice

    def test_an_estate_stage_save_is_not_touched_by_the_backfill(self):
        """The W6-8 estate question prices with `windfall`; stuffing
        plunder_gold into it would be a new wrong number."""
        world, lyon, ney = self._capture_lyon()
        save = world.to_dict()
        save["pending_capture_choice"] = {
            "stage": "estate", "region": "Lyon", "capturer": ney.name,
            "previous_controller": "Britain", "estate_holder": "X",
            "estate_holder_nation": "Britain", "windfall": 0,
            "title": "Duke of Lyon", "options": ["confiscate", "respect"],
            "dialogue_id": 7,
        }
        restored = WorldState.from_dict(save)
        assert "plunder_gold" not in restored.pending_capture_choice

    def test_a_keyless_payload_omits_the_figure_rather_than_lying(self):
        """Post-landing review #4, the reader half: if the price is absent
        (backfill could not resolve the region), every restatement omits
        the figure — an absent price is honest, "0 gold" is not."""
        keyless = {"region": "Lyon", "capturer": "Ney",
                   "previous_controller": "Britain"}
        sentence = capture_choice_prompt(keyless)
        assert "0 gold" not in sentence
        assert "'plunder'" in sentence and "'secure'" in sentence
        from backend.commands.capture_executor import CaptureExecutor
        restatement = CaptureExecutor._pending_prompt(keyless)
        assert "0 gold" not in restatement
        assert "'plunder'" in restatement


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
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        assert ai_prefers_plunder(marshal, world, region.name) is True
        CommandExecutor()._apply_ai_capture_choice(marshal, region, world)
        assert region.stability == 10
        assert region.plundered is True

    def test_the_ai_never_sacks_its_own_recaptured_homeland(self):
        """Post-landing review P2 #1 — the own-soil guard.

        Without it, an aggressive commissioned marshal (the recruitment
        pool holds five: Blücher, Bagration, Paget, Kutaisov, ...) retaking
        his nation's OWN soil would burn its buildings, drop it to
        stability 10 / war damage 0.35, and pay himself x4 to loot
        himself. Reproduced by the review on the test world: Britain
        retaking its own starting province plundered it. Newly reachable
        the moment the dead personality_type branch was fixed, so the
        guard lands with the same slice. The PLAYER's own-soil modal is
        deliberately untouched — asking the player is a choice; an AI
        looting itself is not one anyone would make.
        """
        world = WorldState(player_nation="France")
        home = None
        for name, starter in world._starting_controllers.items():
            if starter == "Britain" and world.get_region(name) is not None:
                home = world.get_region(name)
                break
        assert home is not None, "test world must have a British province"
        home.controller = "France"   # France took it; Britain retakes it
        home.stability = 80
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        assert ai_prefers_plunder(marshal, world, home.name) is False
        before = world.nation_gold.get("Britain", 0)
        choice = CommandExecutor()._apply_ai_capture_choice(
            marshal, home, world)
        assert choice == "secure"
        assert home.stability == 25
        assert home.plundered is False
        assert world.nation_gold.get("Britain", 0) == before

    def test_the_own_soil_guard_covers_the_occupation_route_too(self):
        """Both AI branches share the single source, so the guard must hold
        on the fortified-province (occupation-completion) route as well."""
        world = WorldState(player_nation="France")
        home = None
        for name, starter in world._starting_controllers.items():
            if starter == "Britain" and world.get_region(name) is not None:
                home = world.get_region(name)
                break
        assert home is not None
        home.controller = "France"
        home.stability = 80
        home.buildings = [{"type": "supply_depot", "damaged": False}]
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        marshal.nation = "Britain"
        world._apply_occupation_capture_effects(marshal, home.name)
        assert home.stability == 25          # secured, not sacked
        assert home.buildings, "own building must survive the recapture"

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
        """There are TWO AI branches — fixing only the first leaves
        fortified-province captures unable to plunder. (Post-landing review
        #5 then collapsed the second's hand-inlined duplicate into the one
        shared `apply_plunder_effects`.)"""
        world, region = self._world()
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        marshal.nation = "Britain"
        before = world.nation_gold.get("Britain", 0)
        world._apply_occupation_capture_effects(marshal, region.name)
        assert world.nation_gold["Britain"] - before == plunder_yield(region)
        assert region.stability == 10

    def test_occupation_route_plunder_logs_building_damaged_events(self):
        """Post-landing review #5: the occupation branch's hand-inlined
        plunder copy destroyed buildings SILENTLY — an AI sacking a
        fortified province left one campaign-log row where sacking an open
        one left up to four. Both branches now share
        `world_state.apply_plunder_effects`, so the events are identical.
        """
        world, region = self._world()
        region.buildings = [{"type": "supply_depot", "damaged": False},
                            {"type": "market", "damaged": False}]
        region.watchtower = "active"
        marshal = world.get_marshal("Uxbridge")
        marshal.personality = "aggressive"
        marshal.nation = "Britain"
        world._apply_occupation_capture_effects(marshal, region.name)
        damaged = [e for e in world.event_log
                   if e.get("type") == "building_damaged"
                   and e.get("region") == region.name
                   and e.get("cause") == "plunder"]
        assert {e["building"] for e in damaged} == {
            "supply_depot", "market", "watchtower"}
        assert region.buildings == [] and region.watchtower == "none"

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
    the player reads it. capture_choice_dialog.gd was in NEITHER harness
    list before this slice (instantiated at runtime by dialog_manager, not
    embedded in main.tscn) — IGR-E added it to SETTLEMENT_CRITICAL_SCRIPTS
    in tools/godot_parse_check.gd, so parseability is now covered there;
    these pins cover CONTENT, which no harness checks (post-landing review
    #12 corrected this docstring — its first cut claimed the opposite).

    The pins are exact source lines (post-landing review #9): the first
    cut asserted substrings ('+%d gold', 'data.get(\"plunder_gold\"') that
    the estate stage's pre-existing CONFISCATE line already satisfied, so
    a `* 2` slipped into the var line would have kept every pin green
    while the modal quoted double what plunder_yield pays.
    """

    GD = ("godot-client/project-sovereign/scripts/capture_choice_dialog.gd")

    def _source(self):
        import io
        return io.open(self.GD, encoding="utf-8").read()

    def test_the_plunder_button_reads_the_payload_verbatim(self):
        """The var line, exactly — no arithmetic between payload and label."""
        assert ('var plunder_gold = int(data.get("plunder_gold", 0))'
                in self._source())

    def test_the_plunder_button_quotes_the_figure_exactly(self):
        """The priced label line, exactly as authored — formatted through
        Utils.format_number so modal, terminal and outcome line all render
        1,200 the same way (post-landing review #11)."""
        assert ('plunder_button.text = "PLUNDER (+%s gold, buildings burned, '
                'stability 10)" % Utils.format_number(plunder_gold)'
                in self._source())

    def test_a_payload_without_the_key_gets_an_unpriced_label(self):
        """Post-landing review #4: a pre-IGR-E payload must fall back to an
        UNPRICED label — never assert '+0 gold' about a real payout."""
        src = self._source()
        assert 'if data.has("plunder_gold"):' in src
        assert ('plunder_button.text = "PLUNDER (loot the province, '
                'buildings burned, stability 10)"' in src)

    def test_the_generic_unpriced_label_is_gone(self):
        """The exact string the review saw. If it comes back, the slice has
        been reverted at the only surface the player actually reads."""
        assert "PLUNDER (Loot gold, destroy buildings" not in self._source()
