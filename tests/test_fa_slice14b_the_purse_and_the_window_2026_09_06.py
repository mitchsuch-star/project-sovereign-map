"""FA slice 14 part 2b — "THE PURSE AND THE WINDOW".

Rows: **FA-21** (the bilateral P8 demand reads the payer's purse) and
**FA-31** (the Grand Diversion says what a won roll buys), plus the two
siblings the FA-31 sweep filed inside the same machinery, **FA-N82** and
**FA-N83**.

Landing record: the boxed SLICE 14 (part 2b) block in
`docs/BUG_FIXES.md` §Final Whole-Game Audit.

Three levers, every one with a False arm that reproduces HEAD:
`ai_diplomacy.PURSE_SCALED_BILATERAL_INDEMNITY`,
`ai_diplomacy.P8_REDUCER_READS_THE_PURSE`,
`naval.DIVERSION_WINDOW_FORECAST`.
"""

import contextlib
import copy
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import naval as N
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
EUROPE = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
             / "europe_1805.json")
FIXTURE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"


def _quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


@pytest.fixture
def rich():
    """The t20 ambient fixture — Britain +54 against a 17,487-gold France.

    This is the row's own geometry and the only kind of world FA-21's
    lever 2 is observable on: the purse floor exceeds the legacy flat 200
    only above a treasury of 1,333, and every legacy fixture in the suite
    gives France 800. **A lever-2 pin written on `make_world()` is
    vacuous** — that is measured, not cautionary.
    """
    return _quiet(WorldState.from_dict,
                  json.loads(FIXTURE.read_text(encoding="utf-8"))["world_state"])


@pytest.fixture
def boot():
    return _quiet(WorldState.from_scenario, EUROPE)


def _harsh(world, nation="Britain", gold_mult=1.0):
    ws = AD._get_war_score_for_nation(nation, "France", world)
    terms = AD._build_proposal_terms(nation, "harsh_peace", ws, world,
                                     gold_mult=gold_mult)
    return ws, terms


def _lump(terms):
    return next(d["value"] for d in terms["demands"]
                if d["type"] == "gold_lump")


def _delivered(world, nation, ws, terms):
    reduced = AD._reduce_p8_demands({"terms": terms, "proposal_type": "harsh_peace"},
                                    nation, ws, world)
    return _lump(reduced["terms"]), bool(reduced.get("_force_send"))


# ═══════════════════════════════════════════════════════════════════════════
# FA-21 — the demand reads the payer's purse
# ═══════════════════════════════════════════════════════════════════════════

class TestThePurseIsRead:

    def test_the_measured_defect_is_gone(self, rich):
        """405 gold against a 17,487-gold treasury becomes 15% of the purse."""
        ws, terms = _harsh(rich, gold_mult=1.5)   # Britain boots a hawk
        assert ws == 54
        assert rich.nation_gold["France"] == 17487
        delivered, forced = _delivered(rich, "Britain", ws, terms)
        assert delivered == 2623
        assert delivered == int(17487 * AD.SETTLEMENT_OFFER_TREASURY_FRACTION)
        assert forced is True

    def test_the_control_arm_reproduces_the_defect(self, rich, monkeypatch):
        """Both levers down: the row's own measured 405, delivered whole."""
        monkeypatch.setattr(AD, "PURSE_SCALED_BILATERAL_INDEMNITY", False)
        monkeypatch.setattr(AD, "P8_REDUCER_READS_THE_PURSE", False)
        ws, terms = _harsh(rich, gold_mult=1.5)
        assert _lump(terms) == 405
        delivered, forced = _delivered(rich, "Britain", ws, terms)
        assert delivered == 405
        assert forced is False
        assert delivered / rich.nation_gold["France"] < 0.03

    def test_lever_one_alone_is_the_regression_the_row_prescribes(
            self, rich, monkeypatch):
        """⚠ THE PAIRING PIN. Do not ship lever 1 without lever 2.

        `_reduce_p8_demands` halves exactly ONCE and then falls to a token,
        so any built figure above twice the largest acceptable lump collapses
        to that token. Pricing the BUILD alone therefore delivers LESS than
        the defect it was meant to fix — measured on the ambient board, 200
        on 5 of 5 firings where HEAD delivered 220/352/266/277/243.

        This pin exists so that anyone who disables lever 2 — or writes a
        purse term into the builder and stops — is told why by a red test
        rather than by a playtest.
        """
        monkeypatch.setattr(AD, "P8_REDUCER_READS_THE_PURSE", False)
        ws, terms = _harsh(rich, gold_mult=1.5)
        assert _lump(terms) > 5000          # the build is now a real indemnity
        delivered, forced = _delivered(rich, "Britain", ws, terms)
        assert delivered == 200             # …and the reducer throws it away
        assert forced is True

    def test_a_reduction_never_raises_the_demand(self, rich):
        """The FALLBACK clamp. An unclamped purse floor turned a built 532
        into a delivered 997 — a reduction function that increases the ask."""
        for built in (300, 492, 983, 984, 2000, 6233):
            terms = {"type": "peace", "proposer_nation": "Britain",
                     "target_nation": "France", "sweeteners": [], "clauses": [],
                     "demands": [{"type": "gold_lump", "value": built}]}
            delivered, _ = _delivered(rich, "Britain", 54, terms)
            assert delivered <= built, f"built {built} -> delivered {delivered}"
            assert delivered >= 200

    def test_the_halve_step_never_raises_the_demand_either(self, rich):
        """⚠ THE SECOND CLAMP, and it needs its OWN geometry.

        The mutation sweep reported the halve clamp INERT, and the reason
        was a hole in the test above, not dead code: with gold-only terms
        the halve step's output is always rejected and the FALLBACK decides,
        so the halve clamp is unobservable. The escape hatch is retry 2 —
        drop the weakest non-gold demand and re-score — which can return the
        halved dict directly.

        Measured on this geometry: a built 300 alongside a liberation demand,
        with the payer holding 3,000 (floor 450). Unclamped, the "reduction"
        delivers **450** — half again as much as was asked for. Clamped, 300.
        """
        rich.nation_gold["France"] = 3000
        assert AD._p8_purse_floor({"terms": {"target_nation": "France"}}, rich) == 450
        terms = {"type": "peace", "proposer_nation": "Britain",
                 "target_nation": "France", "sweeteners": [], "clauses": [],
                 "demands": [{"type": "gold_lump", "value": 300},
                             {"type": "liberation", "value": 1,
                              "vassal_nation": "Holland",
                              "lord_nation": "France", "liberator": "Britain"}]}
        reduced = AD._reduce_p8_demands(
            {"terms": terms, "proposal_type": "harsh_peace"}, "Britain", 54, rich)
        assert not reduced.get("_force_send")      # retry 2 returned, not the fallback
        assert _lump(reduced["terms"]) == 300

    def test_a_broke_payer_still_sees_the_flat_two_hundred(self, rich):
        """The floor is `max(200, 15% of the chest)`, so a poor court is
        byte-identical to HEAD — which is why every legacy fixture holds."""
        rich.nation_gold["France"] = 0
        assert AD._p8_purse_floor({"terms": {"target_nation": "France"}}, rich) == 200
        rich.nation_gold["France"] = 1333
        assert AD._p8_purse_floor({"terms": {"target_nation": "France"}}, rich) == 200
        rich.nation_gold["France"] = 1340
        assert AD._p8_purse_floor({"terms": {"target_nation": "France"}}, rich) == 201

    def test_the_low_end_stays_purse_blind_and_that_is_stated(self, rich):
        """A STATED LIMIT, not an oversight.

        `max(legacy, purse)` cannot price DOWN, so a bankrupt payer is still
        asked for the legacy floor. The row's proposed negative control
        ("empty chest, therefore no lump") is unsatisfiable under this shape
        and is recorded as such rather than quietly dropped.
        """
        rich.nation_gold["France"] = 0
        _, terms = _harsh(rich, gold_mult=1.0)
        assert _lump(terms) == 270          # 54 * 5, the legacy ladder

    def test_the_purse_floor_reads_the_term_not_the_player(self, rich):
        """Nation-pair-general for free. Same answer today by construction —
        one call site can pass `harsh_peace` and it targets the player — but
        the seam does not assume it."""
        rich.nation_gold["Austria"] = 40000
        floor = AD._p8_purse_floor({"terms": {"target_nation": "Austria"}}, rich)
        assert floor == int(40000 * AD.SETTLEMENT_OFFER_TREASURY_FRACTION)


class TestTheTwoChannelsPriceAlike:

    def test_the_extraction_is_byte_identical_to_the_body_it_replaced(self, rich):
        """The EC-W4 multilateral amount is unchanged, over a real sweep.

        This is the drift pin, and it must recompute the EC-W4 body from the
        CONSTANTS rather than call the helper it is testing. Comparing the
        caller's answer to `purse_scaled_indemnity` is tautological now that
        the caller IS the helper — the mutation sweep proved it by perturbing
        the shared formula and watching both sides move together.
        """
        def ec_w4(treasury, ws, age):
            base = (AD.SETTLEMENT_OFFER_BASE_GOLD_AMOUNT
                    + max(0, age) * AD.SETTLEMENT_OFFER_PER_DURATION_BONUS)
            scaled = (base + abs(int(ws)) * AD.SETTLEMENT_OFFER_PER_WAR_SCORE
                      + int(treasury * AD.SETTLEMENT_OFFER_TREASURY_FRACTION))
            cap = int(treasury * AD.SETTLEMENT_OFFER_MAX_TREASURY_FRACTION)
            return max(0, min(scaled, cap))

        for treasury in (0, 800, 6650, 17487, 100000):
            rich.nation_gold["France"] = treasury
            for ws in (20, 41, 54, 80, 100):
                for age in (0, 5, 19, 40):
                    terms = AD._settlement_offer_build_terms(
                        accepter="France", proposer_nation="Britain",
                        war_age_turns=age, accepter_war_score=-ws, world=rich)
                    got = next((t["amount"] for t in terms
                                if t["type"] == "gold_indemnity"), 0)
                    want = ec_w4(treasury, ws, age)
                    assert got == want, (treasury, ws, age, got, want)
                    assert AD.purse_scaled_indemnity(
                        rich, "France", ws, age) == want

    def test_the_legacy_no_world_arm_survives(self, rich):
        """Direct callers with no world keep the pre-EC-W4 flat sizing."""
        terms = AD._settlement_offer_build_terms(
            accepter="France", proposer_nation="Britain",
            war_age_turns=50, accepter_war_score=-54, world=None)
        amount = next(t["amount"] for t in terms if t["type"] == "gold_indemnity")
        assert amount == AD.SETTLEMENT_OFFER_MAX_GOLD_AMOUNT

    def test_the_personality_ladder_survives_on_a_poor_payer(self, rich):
        """hawk > neutral > dove, where the cap binds.

        This is what decides `gold_mult`'s placement. Multiplying the scaled
        term while leaving the cap raw collapses hawk onto neutral at every
        purse the cap binds on — which is every poor payer — so the whole
        R115 signal disappears exactly where it is loudest.
        """
        rich.nation_gold["France"] = 800
        vals = [AD.purse_scaled_indemnity(rich, "France", 50, 0, gm)
                for gm in (1.5, 1.0, 0.75)]
        assert vals == sorted(vals, reverse=True)
        assert len(set(vals)) == 3

    def test_the_personality_ladder_survives_on_a_rich_payer(self, rich):
        vals = [AD.purse_scaled_indemnity(rich, "France", 80, 19, gm)
                for gm in (1.5, 1.0, 0.75)]
        assert vals == sorted(vals, reverse=True)
        assert len(set(vals)) == 3

    def test_the_demand_still_reads_the_war(self, rich):
        """Monotonic in war score wherever the purse term does not bind.

        The reason the purse is a FLOOR under the legacy ladder rather than a
        replacement: a replacement gives the cap at both 50 and 80 on a poor
        payer, and the demand stops reading the war at all.
        """
        rich.nation_gold["France"] = 800
        got = [_lump(AD._build_proposal_terms("Britain", "harsh_peace", ws, rich))
               for ws in (50, 80, 100)]
        assert got[2] > got[1] > got[0]


class TestTheWarAgeIsReadable:

    def test_the_pair_war_age_is_not_zero(self, rich):
        """`war_instances` is keyed by war id, never by a diplo key — a
        lookup by `_make_diplo_key` silently prices every peace at age 0."""
        assert AD.pair_war_age(rich, "Britain", "France") == 19
        assert AD.pair_war_age(rich, "Austria", "France") == 19

    def test_a_court_not_at_war_prices_at_zero(self, rich):
        assert AD.pair_war_age(rich, "Switzerland", "France") == 0

    def test_same_side_courts_are_not_at_war_with_each_other(self, rich):
        """Both in `war_1`, same side — the age must not be the war's."""
        assert AD.pair_war_age(rich, "Britain", "Austria") == 0

    def test_the_age_reaches_the_demand(self, rich):
        """A longer war costs more, where the cap leaves room.

        ⚠ The treasury has to be big enough that `0.40 x purse` does NOT
        bind, or the age term is invisible and the pin is vacuous — which is
        also the honest answer to "does the age matter?": on three of the
        five ambient P8 firings it does not, because the cap binds.
        """
        rich.nation_gold["France"] = 20000
        young = AD.purse_scaled_indemnity(rich, "France", 30, 0)
        old = AD.purse_scaled_indemnity(rich, "France", 30, 40)
        assert old > young
        rich.nation_gold["France"] = 4000          # the cap binds here
        assert (AD.purse_scaled_indemnity(rich, "France", 30, 40)
                == AD.purse_scaled_indemnity(rich, "France", 30, 0))


# ═══════════════════════════════════════════════════════════════════════════
# FA-31 — the Grand Diversion says what a won roll buys
# ═══════════════════════════════════════════════════════════════════════════

def _diversion_chip(world):
    for chip in N.build_admiralty_report(world).get("chips", []):
        if chip["label"] == "The Grand Diversion":
            return chip
    return {}


def _rot(world, turns, stage_at=None):
    """Advance the naval clock, optionally marching the camp in partway."""
    for t in range(1, turns + 1):
        if stage_at is not None and t == stage_at:
            for name in ("Soult", "Ney"):
                marshal = world.get_marshal(name)
                if marshal:
                    marshal.location = "Normandy"
        _quiet(N.process_naval_turn, world)


class TestTheForecastIsPure:

    def test_a_forecast_leaves_the_board_untouched(self, boot):
        before = copy.deepcopy(boot.fleets)
        N.window_forecast(boot, "France")
        N.window_forecast(boot, "France")
        assert boot.fleets == before

    def test_an_exception_mid_forecast_leaves_the_board_untouched(
            self, boot, monkeypatch):
        """⚠ THE ARM THAT MATTERS. The clean-call arm passes with or without
        the `finally` and proves nothing.

        Without it, an exception raised inside the forecast leaves the actor
        holding a free two-turn window, the blockade lifted and +5 readiness
        on every navy in Europe — ten records — granted by pressing L.
        """
        before = copy.deepcopy(boot.fleets)

        def boom(_world):
            raise RuntimeError("probe")

        monkeypatch.setattr(N, "derive_ai_postures", boom)
        with pytest.raises(RuntimeError):
            N.window_forecast(boot, "France")
        assert boot.fleets == before

    def test_the_store_is_restored_in_place_not_rebound(self, boot):
        """`_meta` hands out `fleets.setdefault(META_KEY, {})` and callers
        hold that dict, so a rebind would orphan every held reference."""
        store = boot.fleets
        meta = N._meta(boot)
        N.window_forecast(boot, "France")
        assert boot.fleets is store
        assert N._meta(boot) is meta

    def test_opening_the_ledger_does_not_move_the_fleets(self, boot):
        """The forecast's only production reader is `GET /ledger`, which the
        player presses every turn."""
        from backend.game_logic.ledger import build_strategic_ledger
        before = copy.deepcopy(boot.fleets)
        _quiet(build_strategic_ledger, boot)
        _quiet(build_strategic_ledger, boot)
        assert boot.fleets == before


class TestTheWindowIsTwoTurns:

    def test_the_two_turns_are_measured_separately(self, boot):
        forecast = N.window_forecast(boot, "France")
        assert forecast["subject"] == "London|Normandy"
        assert forecast["opens_t1"] is True
        assert forecast["opens_t2"] is True

    def test_turn_two_runs_derive_then_tick_in_that_order(self, boot):
        """Both steps, and the ORDER, are load-bearing — pinned on the
        numbers each one moves rather than on the flag they produce.

        The posture derivation is what recruits a second squadron into the
        covering pool once the player's own success pulls the blockader home
        (coverage 50.0 -> 55.6); the readiness tick is what un-rots the
        Combined Fleet behind it (53.8 -> 57.8). The tick reads
        `blockaded_nations`, which reads postures, so derive must come first
        — this is literally steps 1 and 3 of `process_naval_turn`.
        """
        forecast = N.window_forecast(boot, "France")
        subject = forecast["subject"]
        t1, t2 = forecast["turn_1"][subject], forecast["turn_2"][subject]
        assert t1["coverage"] == 50.0 and t2["coverage"] == 55.6
        assert t1["mover_effective"] == 53.8 and t2["mover_effective"] == 57.8

    def test_the_two_turns_can_disagree_in_both_directions(self, boot):
        """FOUR clause arms, not three.

        A window whose FIRST turn is shut and whose SECOND is open is
        reachable organically — the player's own success pulls the blockade
        home and the crews recover — and a three-arm clause renders a lie
        there through its fall-through. Both mixed arms are walked here on
        the shipped board.
        """
        seen = set()
        for name in ("Soult", "Ney"):
            boot.get_marshal(name).location = "Normandy"
        for _ in range(5):
            _quiet(N.process_naval_turn, boot)
            forecast = N.window_forecast(boot, "France")
            seen.add((forecast["opens_t1"], forecast["opens_t2"]))
        assert (True, False) in seen, seen
        assert (False, True) in seen, seen

    def test_the_clause_has_an_arm_for_every_pair(self, boot):
        """No fall-through: each of the four states renders its own sentence."""
        rendered = set()
        for t1, t2 in ((True, True), (True, False), (False, True), (False, False)):
            fake = {"subject": "London|Normandy", "opens_t1": t1, "opens_t2": t2,
                    "turn_1": {"London|Normandy": {"mover_effective": 39.0,
                                                   "coverage": 50.0, "floor": 0.9}},
                    "turn_2": {}, "now": {}}
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(N, "window_forecast", lambda _w, _a, _f=fake: _f)
                rendered.add(N.window_forecast_clause(boot, "France"))
        assert len(rendered) == 4
        assert all(text for text in rendered)


class TestTheChipTellsTheTruth:

    def test_the_boot_chip_says_what_a_success_buys(self, boot):
        chip = _diversion_chip(boot)
        assert chip["enabled"] is True
        assert "opens London-Normandy" in chip["note"]

    def test_the_odds_and_the_once_per_war_warning_survive(self, boot):
        """The row's own `fix_shape` — a fourth `diversion_terms` gate row —
        DISABLES the chip, and a disabled chip renders `reason` instead of
        `note`, so it deletes the odds AND the once-per-war warning in
        exactly the state the forecast exists for. It is not built."""
        _rot(boot, 4)
        chip = _diversion_chip(boot)
        assert chip["enabled"] is True
        assert f"{N.DIVERSION_SUCCESS_PCT}%" in chip["note"]
        assert "once only, this war" in chip["note"]
        assert "leaves London-Normandy shut" in chip["note"]

    def test_no_fourth_gate_row_was_added(self, boot):
        report = N.build_admiralty_report(boot)
        assert len(report["diversion_terms"]) == 3
        assert report["diversion_available"] is True

    def test_the_shut_clause_quotes_the_number_that_opens_it(self, boot):
        """`crossing_check` allows on `mover / coverage >= floor`, so the
        least sufficient mover is the CEILING of `coverage x floor`.
        Rounding is off by one on the states this clause is for."""
        _rot(boot, 7, stage_at=5)
        note = _diversion_chip(boot)["note"]
        assert "43 effective against 56" in note
        assert "51 is the least that opens it" in note

    def test_the_remedy_names_the_state_the_player_is_actually_in(self, boot):
        """⚠ The remedy must be gated on the state it names or it becomes
        FA-31 again one layer down: a first cut told an already-staged
        player to stage the camp, and told a player whose blockade had
        already lifted that staging would lift it."""
        _rot(boot, 4)                    # blockaded, unstaged
        assert "staging the camp lifts the blockade" in _diversion_chip(boot)["note"]
        _rot(boot, 2, stage_at=1)        # blockaded, staged
        note = _diversion_chip(boot)["note"]
        assert "staging the camp lifts the blockade" not in note
        assert "the blockade lifts as the enemy squadrons come home" in note
        _rot(boot, 1)                    # unblockaded, staged
        note = _diversion_chip(boot)["note"]
        assert "blockade" not in note
        assert "wait for the crews" in note

    def test_the_confirm_carries_the_clause(self, boot):
        from backend.commands.executor import CommandExecutor
        from backend.commands.naval_executor import NavalExecutor
        result = NavalExecutor(CommandExecutor())._execute_naval_diversion(
            {"action": "naval_diversion", "raw_input": "order the diversion"},
            {"world": boot})
        assert result["state"] == "awaiting_clarification"
        assert "And mark this, Sire:" in result["message"]
        assert "opens London-Normandy" in result["message"]


class TestTheOutcomeIsReportedHonestly:

    def test_a_won_window_that_opens_nothing_says_so(self, boot):
        """The FOURTH surface, and the worst of the four: this one asserts a
        FACT. It said "The Strait lies open: 2 turns" unconditionally."""
        _rot(boot, 4)
        N.get_fleet(boot, "France")["window_turns"] = N.WINDOW_TURNS
        assert all(v["verdict"] not in N._OPEN_VERDICTS
                   for v in N.link_verdicts_for(boot, "France").values())
        sentence = N._diversion_outcome_sentence(boot, "France")
        # The EXACT arm, not "one of the two negative arms" — the loose form
        # was satisfied by the partial-open branch rendering an empty list.
        assert sentence.startswith("But the squadrons are too worn")
        assert "lies open" not in sentence

    def test_the_partial_arm_always_names_what_did_open(self, boot):
        """The branch below the nothing-opened arm must never render an
        empty list; if it can, the arm above it is not doing its job."""
        _rot(boot, 7, stage_at=5)
        N.get_fleet(boot, "France")["window_turns"] = N.WINDOW_TURNS
        verdicts = N.link_verdicts_for(boot, "France")
        opened = [k for k, v in verdicts.items()
                  if v["verdict"] in N._OPEN_VERDICTS]
        assert opened and N.window_forecast(boot, "France")["subject"] not in opened
        sentence = N._diversion_outcome_sentence(boot, "France")
        assert "opens only " in sentence
        assert not sentence.endswith("opens only , which our army cannot use.")
        for key in opened:
            assert N._render_pair(key) in sentence

    def test_the_report_and_the_forecast_name_the_same_crossing(self, boot):
        """A ranking is a pipeline and every reader must share it.

        Ranking only the OPENED links reproduced the ranking defect in a new
        costume: with the Channel shut and a Mediterranean link open, the
        chip said "London-Normandy shut" and the report of the same act
        announced Cagliari-Corsica. Two surfaces, two subjects, one event.
        """
        _rot(boot, 7, stage_at=5)
        subject = N.window_forecast(boot, "France")["subject"]
        N.get_fleet(boot, "France")["window_turns"] = N.WINDOW_TURNS
        sentence = N._diversion_outcome_sentence(boot, "France")
        assert N._render_pair(subject) in sentence

    def test_the_success_line_names_the_royal_navy(self, boot, monkeypatch):
        """The sibling wart in the same sentence: "the Britain fleet", where
        `_fleet_label` exists and gives "the Royal Navy"."""
        monkeypatch.setattr(N, "_pct_roll", lambda *a, **kw: True)
        outcome = _quiet(N.resolve_diversion, boot, "France")
        assert outcome["window"] is True
        assert "the Royal Navy" in outcome["message"]
        assert "the Britain fleet" not in outcome["message"]


class TestTheSubjectIsTheCrossingTheArmyMeans:

    def test_the_camp_province_outranks_the_alphabet(self, boot):
        keys = {"Cagliari|Corsica", "London|Normandy", "Corsica|Piedmont"}
        assert N._rank_links(boot, "France", keys) == "London|Normandy"

    def test_army_mass_breaks_the_tie_when_no_camp_is_involved(self, boot):
        marshal = boot.get_marshal("Soult")
        marshal.location = "Piedmont"
        keys = {"Cagliari|Corsica", "Corsica|Piedmont"}
        assert N._rank_links(boot, "France", keys) == "Corsica|Piedmont"

    def test_the_ranking_is_deterministic_with_nothing_to_choose(self, boot):
        keys = {"Cagliari|Corsica", "Corsica|Piedmont"}
        assert N._rank_links(boot, "Austria", keys) == "Cagliari|Corsica"


class TestTheMirrorAnswersForAnyCourt:

    def test_the_forecast_reads_the_actors_own_shore(self, boot):
        """GR5. `_tracked_links` is player-keyed, so an un-parameterised
        forecast would have scanned FRANCE's coast to answer for Britain."""
        forecast = N.window_forecast(boot, "Britain")
        assert forecast["subject"] == "London|Normandy"
        for key in forecast["turn_1"]:
            assert set(key.split("|")) & N._actor_shore(boot, "Britain")

    def test_the_player_scan_is_unchanged(self, boot):
        assert N.link_verdicts(boot) == N.link_verdicts_for(boot, "France")

    def test_the_window_waives_the_host_rule_and_the_forecast_can_say_so(self, boot):
        """Britain's descent is `landing` today; a window makes it a crossing."""
        assert N.link_verdicts_for(boot, "Britain")[
            "London|Normandy"]["verdict"] == "landing"
        assert N.window_forecast(boot, "Britain")["opens_t1"] is True


class TestTheAiAsksTheSameQuestion:

    def test_the_rung_refuses_a_window_that_would_open_nothing(self, boot):
        """The rung REQUIRED the trap state — a staged camp under a blockade
        is exactly when the rot has made a won window worthless — so it
        steered the AI into spending its once-per-war card on shut water."""
        _rot(boot, 6, stage_at=5)
        assert N.camp_staged(boot, "France") is True
        assert N.find_ai_diversion(boot, "France") is None

    def test_the_rung_allows_it_once_the_crews_recover(self, boot):
        _rot(boot, 3, stage_at=1)
        assert N.camp_staged(boot, "France") is True
        assert N.find_ai_diversion(boot, "France") is not None

    def test_the_gate_keys_on_the_ranked_subject(self, boot, monkeypatch):
        """Not on "any link opens". With the naive any-link form the rung
        still fired in the trap, because a Mediterranean link the army
        cannot use opens."""
        _rot(boot, 6, stage_at=5)
        forecast = N.window_forecast(boot, "France")
        any_open = any(
            v.get("verdict") in N._OPEN_VERDICTS
            for turn in ("turn_1", "turn_2") for v in forecast[turn].values())
        assert any_open is True
        assert forecast["opens_t1"] is False and forecast["opens_t2"] is False

    def test_the_lever_down_restores_the_old_rung(self, boot, monkeypatch):
        monkeypatch.setattr(N, "DIVERSION_WINDOW_FORECAST", False)
        _rot(boot, 6, stage_at=5)
        assert N.find_ai_diversion(boot, "France") is not None
        assert _diversion_chip(boot)["note"] == (
            f"{N.DIVERSION_SUCCESS_PCT}% — and once only, this war")


# ═══════════════════════════════════════════════════════════════════════════
# FA-N82 / FA-N83 — the two siblings the FA-31 sweep filed
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCampSurvivesALostFleet:
    """FA-N82. The camp is an ARMY fact and must not be read through the
    ships > 0 iterator: at 0 sail it stopped ticking, so the power that has
    just lost its navy could never pull the Royal Navy home — the one move
    it has left."""

    def test_a_sunk_navy_still_stages_its_camp(self, boot):
        N.get_fleet(boot, "France")["ships"] = 0
        _rot(boot, 4, stage_at=1)
        assert N.get_fleet(boot, "France")["camp_turns"] == 4
        assert N.camp_staged(boot, "France") is True

    def test_the_enemy_scan_sees_it(self, boot):
        """`derive_ai_postures` re-implemented `camp_staged` inline over the
        same ships > 0 iterator, so even a ticking camp stayed invisible."""
        N.get_fleet(boot, "France")["ships"] = 0
        _rot(boot, 4, stage_at=1)
        assert N.get_fleet(boot, "Britain")["posture"] == "guard"
        assert "France" not in N.blockaded_nations(boot)

    def test_the_control_arm_reproduces_the_defect(self, boot, monkeypatch):
        monkeypatch.setattr(N, "iter_fleet_records", N.iter_fleets)
        N.get_fleet(boot, "France")["ships"] = 0
        _rot(boot, 4, stage_at=1)
        assert int(N.get_fleet(boot, "France").get("camp_turns", 0)) == 0
        assert N.get_fleet(boot, "Britain")["posture"] == "blockade"

    def test_a_ports_only_row_still_stages_nothing(self, boot):
        """The widening reaches exactly one extra state. The five ports-only
        rows on the shipped board author no camp, so they are unaffected —
        which is the written predicate for the series staying still."""
        for nation, rec in N.iter_fleet_records(boot):
            if int(rec.get("ships", 0) or 0) == 0:
                assert not rec.get("camp_provinces"), nation


class TestOncePerWarMeansTheNavalWar:
    """FA-N83. The reset read ANY war while the gate term read a NAVAL war —
    two readings of one phrase, and the stricter one owned the reset."""

    def test_a_land_war_does_not_withhold_the_card(self, boot):
        N.get_fleet(boot, "France")["diversion_used"] = True
        with contextlib.redirect_stdout(io.StringIO()):
            for nation in ("Britain", "Russia"):
                set_diplomatic_state(boot, "France", nation, "PEACE", "test")
            _rot(boot, 3)
        assert boot.get_nations_at_war_with("France")     # Austria stands
        assert N.get_fleet(boot, "France")["diversion_used"] is False

    def test_a_new_naval_war_returns_the_card(self, boot):
        N.get_fleet(boot, "France")["diversion_used"] = True
        with contextlib.redirect_stdout(io.StringIO()):
            for nation in ("Britain", "Russia", "Austria"):
                set_diplomatic_state(boot, "France", nation, "PEACE", "test")
            _rot(boot, 1)
            set_diplomatic_state(boot, "France", "Britain", "WAR", "test")
        assert N.get_fleet(boot, "France")["diversion_used"] is False
        assert _diversion_chip(boot)["enabled"] is True

    def test_the_card_is_still_spent_inside_its_own_war(self, boot):
        N.get_fleet(boot, "France")["diversion_used"] = True
        _rot(boot, 3)
        assert N.get_fleet(boot, "France")["diversion_used"] is True
        assert _diversion_chip(boot)["enabled"] is False

    def test_the_reset_and_the_gate_term_read_one_predicate(self, boot):
        report = N.build_admiralty_report(boot)
        term = next(t for t in report["diversion_terms"]
                    if t["text"] == "at war with a naval power")
        assert term["met"] is N.has_naval_war(boot, "France")
