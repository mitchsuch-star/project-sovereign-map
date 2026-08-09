"""CA9 row 1 — a war that has barely begun is hard to cash in.

Gate record: `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` §1 (authoritative).
The user's ruling, verbatim: *"look at euiv, if war is short its way harder to
end avoids cheesing 1 battle for free cash. think deeply about this"*.

Nothing in the acceptance formula read how old a war was. R142's war weariness
only ever made peace EASIER with time, so the loop "declare → win one battle →
demand gold → peace out" had an exit to run to on turn 2. This is option B from
the gate — a penalty on ending a young war — and only option B. Option A, the
battle-vs-territory re-weight on the war score itself, is deliberately not
built: the gate defers it to a judgement after the playtest.

**The falsifiable acceptance shape is `TestTheCheeseIsClosed`**, and it is
asserted where the player actually meets it: Talleyrand's own recommendation.
The acceptance score is the mechanism; `generate_suggested_terms` is the
surface, and it prices its output through that score (the NA-3 rider-b memo),
so it is the honest place to ask "can a player still cash out a two-turn war".
Each arm carries a negative control that re-runs it with the mechanic disabled
and asserts the OPPOSITE — without those, every test here would pass just as
well against a constant 0.
"""

import pytest

from backend.game_logic import diplomacy as D
from backend.game_logic.diplomacy import (
    WAR_AGE_PENALTY_MAX,
    WAR_AGE_PENALTY_TYPES,
    WAR_AGE_PENALTY_WINDOW,
    proposal_extracts_value,
    war_age_acceptance_mod,
)

SCENARIO = "godot-client/project-sovereign/assets/maps/europe_1805.json"


@pytest.fixture()
def europe():
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(SCENARIO)


def _at_war(world, target="Prussia", *, age, war_score=30, relation=20):
    """France at war with `target` for `age` turns, winning on points."""
    key = world._make_diplo_key("France", target)
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = int(world.current_turn) - int(age)
    world.war_scores[key] = war_score
    world.nation_relations[key] = relation
    return key


def _peace(target="Prussia", gold=1500):
    return {
        "type": "peace", "proposer_nation": "France", "target_nation": target,
        "sweeteners": [], "clauses": [],
        "demands": ([{"type": "gold_lump", "value": gold}] if gold else []),
    }


@pytest.fixture()
def mechanic_off(monkeypatch):
    """The negative control: the curve flattened to nothing, everything else
    untouched. Used to prove an effect is caused by THIS mechanic and not by
    the fixture."""
    monkeypatch.setattr(D, "WAR_AGE_PENALTY_MAX", 0)


# ════════════════════════════════════════════════════════════════════════
# The curve
# ════════════════════════════════════════════════════════════════════════

class TestTheCurve:
    def test_full_penalty_on_the_turn_war_is_declared(self):
        assert war_age_acceptance_mod(0, extracts_value=True) == -30

    def test_decays_to_nothing_by_the_window(self):
        assert war_age_acceptance_mod(
            WAR_AGE_PENALTY_WINDOW, extracts_value=True) == 0
        assert war_age_acceptance_mod(99, extracts_value=True) == 0

    def test_monotonic_across_the_window(self):
        """Strictly non-decreasing toward 0 — no cliff a player could learn
        to sit on, which was the argument for a decay rather than a gate."""
        seq = [war_age_acceptance_mod(t, extracts_value=True)
               for t in range(0, WAR_AGE_PENALTY_WINDOW + 3)]
        assert seq == sorted(seq)
        assert seq[0] == -WAR_AGE_PENALTY_MAX
        assert seq[-1] == 0

    def test_a_white_peace_is_signable_at_any_age(self):
        """The waiver that keeps this from creating a war with no way out —
        the gate record's own caution, and the note CA9's campaign closed
        on."""
        for t in range(0, WAR_AGE_PENALTY_WINDOW + 1):
            assert war_age_acceptance_mod(t, extracts_value=False) == 0

    def test_unknown_age_is_not_treated_as_brand_new(self):
        """`None` means the start turn was never recorded. Charging it the
        maximum would silently re-price legacy saves and any fixture that
        never set `war_start_turns`; it must read as no penalty instead."""
        assert war_age_acceptance_mod(None, extracts_value=True) == 0

    def test_negative_age_cannot_exceed_the_maximum(self):
        assert war_age_acceptance_mod(-5, extracts_value=True) == -30


# ════════════════════════════════════════════════════════════════════════
# What counts as taking something
# ════════════════════════════════════════════════════════════════════════

class TestExtractionPredicate:
    def test_a_gold_demand_extracts(self):
        assert proposal_extracts_value(_peace(gold=800)) is True

    def test_an_empty_package_does_not(self):
        assert proposal_extracts_value(_peace(gold=0)) is False
        assert proposal_extracts_value({"type": "peace"}) is False

    def test_a_zero_valued_gold_demand_does_not(self):
        assert proposal_extracts_value(
            {"demands": [{"type": "gold_lump", "value": 0}]}) is False

    def test_province_and_client_markers_extract_without_a_scalar(self):
        """`territory` / `create_client` / `prisoner_return` carry their
        subject in a list, not a `value` — the convention `DEMAND_VALUES`
        already uses. A zero-value check alone would miss all three."""
        for dtype in ("territory", "create_client", "prisoner_return",
                      "forced_alliance", "liberation"):
            assert proposal_extracts_value(
                {"demands": [{"type": dtype}]}) is True, dtype

    def test_sweeteners_are_not_extraction(self):
        """Paying a court to sign an early peace is not the behaviour this
        penalty exists to discourage — buying your way out of a war you
        started badly is a perfectly good move."""
        assert proposal_extracts_value({
            "sweeteners": [{"type": "gold_lump", "value": 5000}],
            "demands": [],
        }) is False

    def test_an_unpriced_demand_type_does_not_extract(self):
        assert proposal_extracts_value(
            {"demands": [{"type": "a_type_that_does_not_exist"}]}) is False


# ════════════════════════════════════════════════════════════════════════
# Through the real bilateral scorer
# ════════════════════════════════════════════════════════════════════════

class TestThroughTheScorer:
    def test_the_term_is_on_the_components_and_costs_the_score(self, europe):
        _at_war(europe, age=1)
        result = D.calculate_acceptance(_peace(), europe)
        assert result["components"]["war_age_penalty"] < 0

    def test_the_same_package_scores_higher_once_the_war_has_run(self, europe):
        _at_war(europe, age=1)
        young = D.calculate_acceptance(_peace(), europe)["score"]
        _at_war(europe, age=WAR_AGE_PENALTY_WINDOW + 2)
        old = D.calculate_acceptance(_peace(), europe)["score"]
        assert old > young

    def test_a_white_peace_is_unpenalised_in_the_same_young_war(self, europe):
        _at_war(europe, age=0)
        assert D.calculate_acceptance(
            _peace(gold=0), europe)["components"]["war_age_penalty"] == 0
        assert D.calculate_acceptance(
            _peace(gold=1500), europe)["components"]["war_age_penalty"] < 0

    def test_it_does_not_touch_proposals_that_are_not_war_exits(self, europe):
        _at_war(europe, age=0)
        for ptype in ("alliance", "open_borders", "non_aggression",
                      "defensive_alliance", "vassalage"):
            assert ptype not in WAR_AGE_PENALTY_TYPES
            prop = _peace()
            prop["type"] = ptype
            assert D.calculate_acceptance(
                prop, europe)["components"]["war_age_penalty"] == 0, ptype

    def test_it_does_not_fire_outside_war(self, europe):
        key = europe._make_diplo_key("France", "Sweden")
        europe.diplomatic_states[key] = "PEACE"
        europe.war_start_turns[key] = int(europe.current_turn)
        assert D.calculate_acceptance(
            _peace("Sweden"), europe)["components"]["war_age_penalty"] == 0

    def test_an_unrecorded_war_start_is_not_charged(self, europe):
        """The bilateral read defaults `war_start_turns` to `current_turn`
        for R142's benefit. The age term must NOT inherit that default, or
        every war whose start was never recorded is charged -30 forever."""
        key = europe._make_diplo_key("France", "Sweden")
        europe.diplomatic_states[key] = "WAR"
        europe.war_start_turns.pop(key, None)
        assert D.calculate_acceptance(
            _peace("Sweden"), europe)["components"]["war_age_penalty"] == 0

    def test_the_armistice_arms_are_covered(self, europe):
        """A declared scope extension, not a gate instruction — F14's own
        landing measured the armistice sibling carrying `gold_lump 1600` at
        war score +19, roughly 20x the peace arm. Penalising peace alone
        would move the cheese one door left."""
        _at_war(europe, age=0)
        for ptype in ("armistice_losing", "armistice_winning"):
            prop = _peace()
            prop["type"] = ptype
            assert D.calculate_acceptance(
                prop, europe)["components"]["war_age_penalty"] < 0, ptype


# ════════════════════════════════════════════════════════════════════════
# THE ACCEPTANCE SHAPE — the cheese, at the surface the player uses
# ════════════════════════════════════════════════════════════════════════

class TestTheCheeseIsClosed:
    """The falsifiable shape, so the blessed number can be judged rather
    than argued. Measured on the shipped 1805 board with France winning on
    points (+30) against Prussia at relation +20.

    If arm A ever fails, a player can again declare, win one skirmish and
    have their own foreign minister recommend collecting for it. If arm B
    ever fails, a long war can no longer be closed on terms and the penalty
    has become the "war with no way out" the gate record warned about.
    """

    def _suggested_demands(self, world, age):
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        _at_war(world, age=age)
        terms = generate_suggested_terms("Prussia", "peace", world)
        return [d.get("type") for d in (terms.get("demands") or [])]

    def test_arm_a_a_two_turn_war_yields_no_recommended_extraction(self, europe):
        assert self._suggested_demands(europe, 1) == [], (
            "Talleyrand still recommends cashing out a war two turns old")

    def test_arm_b_a_long_war_can_still_be_closed_on_terms(self, europe):
        assert self._suggested_demands(europe, WAR_AGE_PENALTY_WINDOW + 1), (
            "a war that has run its course can no longer be ended on terms "
            "— the penalty has closed the exit, not the exploit")

    def test_negative_control_arm_a_fails_with_the_mechanic_off(
            self, europe, mechanic_off):
        """Arm A must fail here. If it passes with the curve flattened, the
        young-war silence is coming from something else and arm A is
        measuring nothing."""
        assert self._suggested_demands(europe, 1) != [], (
            "arm A passes with the mechanic disabled — it does not test the "
            "war-age penalty")

    def test_negative_control_arm_b_is_unaffected_by_the_mechanic(
            self, europe, mechanic_off):
        """Arm B must still pass with the mechanic off — past the window the
        term is 0 anyway, so this pins that the long-war exit was never the
        penalty's doing in either direction."""
        assert self._suggested_demands(europe, WAR_AGE_PENALTY_WINDOW + 1)


# ════════════════════════════════════════════════════════════════════════
# The rule explains itself — option B's whole argument
# ════════════════════════════════════════════════════════════════════════

class TestItSaysSoOutLoud:
    """The gate chose B over A partly because "it must be VISIBLE — the
    per-court acceptance breakdown already names its components, so it would
    read as *The war is barely begun: -30*, which is honest and teaches the
    rule in one line." These pin that the plumbing for that sentence exists.
    """

    def test_the_component_is_feedback_trackable(self):
        """Untracked components can never be named as the sticking point, so
        the rule would be invisible and B would lose its own argument."""
        import inspect
        src = inspect.getsource(D._generate_feedback)
        assert '"war_age_penalty"' in src

    def test_a_negative_phrase_is_authored(self):
        from backend.display_names import FEEDBACK_STRINGS
        entry = FEEDBACK_STRINGS.get("war_age_penalty") or {}
        assert entry.get("negative"), (
            "no authored phrase — feedback would fall through to "
            "'unknown factors' on the one term meant to teach the rule")
        assert entry.get("positive")

    def test_the_advisory_surface_has_a_label(self):
        """`_COMPONENT_LABELS` in the Talleyrand advisory path renders the
        per-component breakdown the gate record points at."""
        import inspect
        from backend.game_logic import diplomacy as _d
        src = inspect.getsource(_d)
        assert '"war_age_penalty": "The war is barely begun"' in src

    def test_the_feedback_names_it_when_it_is_the_obstacle(self):
        """End to end through the real feedback builder, with the term made
        the largest negative so the outcome is determined rather than hoped
        for. Asserted as an exact phrase match — an `or feedback` fallback
        here would pass against any string at all, which is the inert-pin
        shape this project keeps finding."""
        from backend.display_names import FEEDBACK_STRINGS
        phrase = FEEDBACK_STRINGS["war_age_penalty"]["negative"]
        sentence = D._generate_feedback("REJECT", {
            "war_age_penalty": -30,
            "relation_modifier": -5,
            "base_disposition": 40,
        })
        assert phrase in sentence, sentence

    def test_and_it_is_not_named_when_something_else_dominates(self):
        """The control for the test above: with a bigger obstacle present the
        sentence must name THAT one, proving the match is driven by magnitude
        and not by the key merely being listed."""
        from backend.display_names import FEEDBACK_STRINGS
        age_phrase = FEEDBACK_STRINGS["war_age_penalty"]["negative"]
        sentence = D._generate_feedback("REJECT", {
            "war_age_penalty": -10,
            "grievance_modifier": -90,
            "base_disposition": 40,
        })
        assert age_phrase not in sentence, sentence
