"""MC-3 pin tests (MARSHAL_CONTENT_PASS_SPEC.md §4/§8, memo §4 — relationships).

The July 10, 2026 gate blessed the memo-§4 starting-relationship table: 13
pairs, all symmetric, scale -2 (Hostile, x0.0 coordination) to +2 (Devoted),
with no pair authored at +2 so no pair boots jealousy-immune. Q4 blessed
France's internal web as net-negative (drama over power — the marshalate WAS
a snake pit); enemy-side pairs ride the same mechanical core with no popups
(Charles-Mack x0.0 makes Mack's isolation at Ulm emerge from the graph).

Authoring path: `europe_1805.json` marshal rows carry a `relationships` dict;
`Marshal.from_dict` (the scenario path) restores it raw. Symmetry is authored
explicitly in BOTH directions and pinned here roster-wide — no code mirror
pass, because play-time asymmetry (the Win/Loss formula, legacy Ney->Davout -2
vs Davout->Ney -1) is a supported substrate feature.

This slice is data + validator support only: every consuming seam (coordination
scaling, A-D4 hostile refusal, arrival score, muster preview, the card list)
shipped earlier and is exercised here against the authored web.
"""

import random as _random

import pytest

from backend.ai.parser_eval import build_world
from backend.commands.executor import CommandExecutor
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState
from backend.modding.validator import validate_marshal, validate_scenario


@pytest.fixture()
def world():
    return build_world("1805")


# (a, b, value) — memo §4, blessed July 10, 2026. All pairs symmetric at boot.
# Values are in-band tunable; a change here must be a deliberate tuning
# decision recorded in the spec, not drift.
BLESSED_PAIRS = [
    ("Lannes", "Murat", -1),
    ("Lannes", "Ney", 1),
    ("Soult", "Ney", -1),
    ("Ney", "Murat", -1),
    ("Davout", "Murat", -1),
    ("Davout", "Bernadotte", -2),
    ("Murat", "Bernadotte", -2),
    ("Ney", "Bernadotte", -1),
    ("Massena", "Soult", 1),
    ("ArchdukeCharles", "Mack", -2),
    ("Kutuzov", "Buxhowden", -1),
    ("ArchdukeCharles", "ArchdukeJohn", 1),
    ("Brunswick", "Hohenlohe", -1),
]

FRENCH = {"Ney", "Davout", "Soult", "Lannes", "Murat", "Bernadotte", "Massena"}

# The seven roster marshals with no authored edge (isolated by design — their
# nations field one army, or their story needs no internal web).
UNAUTHORED = {"Deroy", "Moore", "Armfelt", "Damas", "Frederick",
              "Castanos", "Abdurrahman"}


# ════════════════════════════════════════════════════════════════════════
# Boot pins: the blessed 13-pair web survives the scenario pipeline
# ════════════════════════════════════════════════════════════════════════

class TestBlessedWeb:
    @pytest.mark.parametrize("a,b,value", BLESSED_PAIRS)
    def test_pair_boots_symmetric(self, world, a, b, value):
        assert world.get_marshal(a).get_relationship(b) == value, (a, b)
        assert world.get_marshal(b).get_relationship(a) == value, (b, a)

    def test_exactly_26_directed_edges(self, world):
        # 13 pairs x 2 directions — no stray edge beyond the blessed table.
        edges = {(m.name, other): v
                 for m in world.marshals.values()
                 for other, v in m.relationships.items()}
        assert len(edges) == 26
        blessed = {(a, b): v for a, b, v in BLESSED_PAIRS}
        blessed.update({(b, a): v for a, b, v in BLESSED_PAIRS})
        assert edges == blessed

    def test_roster_wide_symmetry_gate(self, world):
        # Memo §4 implementation note: marshals boot independently, so the
        # symmetric shape is authored in both directions and gated here.
        for m in world.marshals.values():
            for other, value in m.relationships.items():
                assert world.get_marshal(other).get_relationship(m.name) \
                    == value, (m.name, other)

    def test_no_self_edges_and_all_in_range(self, world):
        for m in world.marshals.values():
            for other, value in m.relationships.items():
                assert other != m.name
                assert -2 <= value <= 2, (m.name, other)

    def test_no_pair_boots_devoted(self, world):
        # "No pair starts at +2, so no pair is authored jealousy-immune."
        for m in world.marshals.values():
            for other, value in m.relationships.items():
                assert value < 2, (m.name, other)

    def test_all_edges_same_nation(self, world):
        # Coordination/arrival/muster read same-nation allies only — a
        # cross-nation edge would be dead data (GR9: author nothing inert).
        for m in world.marshals.values():
            for other in m.relationships:
                assert world.get_marshal(other).nation == m.nation, \
                    (m.name, other)

    def test_unauthored_marshals_have_empty_web(self, world):
        for name in UNAUTHORED:
            assert world.get_marshal(name).relationships == {}, name

    def test_unauthored_pair_defaults_professional(self, world):
        # The 1805 web is its OWN authored graph: Ney—Davout is 0 here, not
        # the legacy Waterloo fixture's -2/-1 feud.
        assert world.get_marshal("Ney").get_relationship("Davout") == 0
        assert world.get_marshal("Davout").get_relationship("Ney") == 0


# ════════════════════════════════════════════════════════════════════════
# Web shape (Q4 blessed): France net-negative; enemy courts pre-fractured
# ════════════════════════════════════════════════════════════════════════

class TestWebShape:
    def test_french_web_net_negative(self):
        # Q4 blessed the net-negative French web (drama over power). The
        # memo's §4 TABLE authors 9 French pairs — 7 negative / 2 positive
        # (its Q4 prose said "5 negative", a miscount of its own table; the
        # enumerated table is the blessed artifact and governs).
        french_pairs = [(a, b, v) for a, b, v in BLESSED_PAIRS
                        if a in FRENCH and b in FRENCH]
        negative = [p for p in french_pairs if p[2] < 0]
        positive = [p for p in french_pairs if p[2] > 0]
        assert len(french_pairs) == 9
        assert len(negative) == 7
        assert len(positive) == 2
        assert len(negative) > len(positive)  # the blessing itself

    def test_enemy_side_pair_counts(self, world):
        by_nation = {}
        for a, b, v in BLESSED_PAIRS:
            nation = world.get_marshal(a).nation
            by_nation.setdefault(nation, []).append((a, b, v))
        assert len(by_nation["France"]) == 9
        assert len(by_nation["Austria"]) == 2   # Charles-Mack, Charles-John
        assert len(by_nation["Russia"]) == 1    # Kutuzov-Buxhowden
        assert len(by_nation["Prussia"]) == 1   # Brunswick-Hohenlohe
        assert set(by_nation) == {"France", "Austria", "Russia", "Prussia"}

    def test_austria_one_cooperating_axis(self, world):
        # Charles-John +1 is deliberately stable — it makes Charles-Mack
        # legible by contrast (memo §4).
        charles = world.get_marshal("ArchdukeCharles")
        assert charles.get_relationship("Mack") == -2
        assert charles.get_relationship("ArchdukeJohn") == 1


# ════════════════════════════════════════════════════════════════════════
# Mechanical consumption: the shipped seams read the authored web
# ════════════════════════════════════════════════════════════════════════

class TestCoordinationScaling:
    """_RELATIONSHIP_SCALING {-2: 0.0, -1: 0.5, 0: 1.0, +1: 1.25} at the
    per-ally coordination seam (MULTI_MARSHAL_SPEC §3)."""

    def _coord(self, world, name, ally_name):
        return CommandExecutor()._combat._calculate_per_ally_coordination(
            world.get_marshal(name), [world.get_marshal(ally_name)])

    def test_hostile_pair_contributes_zero(self, world):
        # Davout attacking beside Bernadotte: x0.0 — Auerstedt in embryo.
        assert self._coord(world, "Davout", "Bernadotte") == (0.0, 0.0)

    def test_friendly_pair_scales_up(self, world):
        # Lannes beside Ney: +1 -> x1.25 on the 3%/5% base.
        atk, dfn = self._coord(world, "Lannes", "Ney")
        assert atk == pytest.approx(0.03 * 1.25)
        assert dfn == pytest.approx(0.05 * 1.25)

    def test_rival_pair_scales_half(self, world):
        # Murat beside Lannes: -1 -> x0.5.
        atk, dfn = self._coord(world, "Murat", "Lannes")
        assert atk == pytest.approx(0.03 * 0.5)
        assert dfn == pytest.approx(0.05 * 0.5)

    def test_enemy_side_mack_isolated_same_method(self, world):
        # GR5: Austria's x0.0 rides the identical seam — Mack's isolation
        # at Ulm emerges from the graph, not a script.
        assert self._coord(world, "Mack", "ArchdukeCharles") == (0.0, 0.0)


class TestHostileRefusal:
    """A-D4: a -2 marshal without a written SUPPORT order neither
    auto-reinforces nor musters for the hated primary."""

    def _stage_adjacent(self, world, primary_name, candidate_name):
        primary = world.get_marshal(primary_name)
        candidate = world.get_marshal(candidate_name)
        region = world.get_region(primary.location)
        enemy_free = next(
            r for r in region.adjacent_regions
            if not any(m.location == r and m.nation != primary.nation
                       and m.strength > 0 for m in world.marshals.values()))
        candidate.location = enemy_free
        return primary, candidate

    def test_bernadotte_ineligible_to_reinforce_davout(self, world):
        primary, bernadotte = self._stage_adjacent(world, "Davout", "Bernadotte")
        eligible = CommandExecutor()._combat._is_reinforcement_eligible(
            bernadotte, primary, primary.location, "France", world)
        assert eligible is False

    def test_written_support_overrides_hostility(self, world):
        # The counter-lever IS the fantasy: put it in writing and he comes.
        primary, bernadotte = self._stage_adjacent(world, "Davout", "Bernadotte")
        bernadotte.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Davout", target_type="marshal",
            started_turn=1, original_command="Bernadotte, support Davout")
        eligible = CommandExecutor()._combat._is_reinforcement_eligible(
            bernadotte, primary, primary.location, "France", world)
        assert eligible is True

    def test_neutral_massena_eligible_same_stage(self, world):
        # Isolation control: an edge-free marshal on the same staging is
        # eligible, so rule 13 is the differentiator.
        primary, massena = self._stage_adjacent(world, "Davout", "Massena")
        eligible = CommandExecutor()._combat._is_reinforcement_eligible(
            massena, primary, primary.location, "France", world)
        assert eligible is True

    def test_muster_reason_hostile_before_ambition(self, world):
        # vs Davout the preview names the FEUD, not the ability — the
        # hostile arm outranks eyes_on_a_crown in the reason ladder.
        primary, bernadotte = self._stage_adjacent(world, "Davout", "Bernadotte")
        will_join, code = CommandExecutor()._combat._muster_reason(
            bernadotte, primary, primary.location, "France", world)
        assert will_join is False
        assert code == "hostile_refuses"

    def test_muster_reason_mere_rivalry_stays_ambition(self, world):
        # vs Ney (-1, not hostile) Bernadotte's no-show stays his own
        # ambition — the ability arm fires at relationship <= 0.
        primary, bernadotte = self._stage_adjacent(world, "Ney", "Bernadotte")
        will_join, code = CommandExecutor()._combat._muster_reason(
            bernadotte, primary, primary.location, "France", world)
        assert will_join is False
        assert code == "eyes_on_a_crown"

    def test_muster_reason_rival_glory_hound_still_marches(self, world):
        # Murat-Lannes -1: rivalry halves his coordination but the
        # aggressive glory-hound still rides for the headlines.
        primary, murat = self._stage_adjacent(world, "Lannes", "Murat")
        will_join, code = CommandExecutor()._combat._muster_reason(
            murat, primary, primary.location, "France", world)
        assert will_join is True
        assert code == "aggressive_marches"


class TestArrivalStacking:
    """The relationship mod (+/-10 per step, MULTI_MARSHAL_SPEC §7) stacks on
    the MC-2 neutral-primary bases pinned in test_marshal_content_mc2."""

    def _arrival(self, world, marshal, primary, monkeypatch):
        monkeypatch.setattr(_random, "randint", lambda a, b: 0)
        return CommandExecutor()._combat._calculate_arrival_score(
            marshal, primary, world)

    def _stage_on_plains(self, world, *names):
        plains = next(r.name for r in world.regions.values()
                      if r.terrain == "plains")
        for name in names:
            world.get_marshal(name).location = plains

    def test_lannes_for_ney_reaches_100(self, world, monkeypatch):
        # Neutral base 90 (MC-2 pin) + 10 friendship: Roland marches for
        # his fellow fire-eater all but unconditionally.
        self._stage_on_plains(world, "Lannes", "Ney")
        assert self._arrival(world, world.get_marshal("Lannes"),
                             world.get_marshal("Ney"), monkeypatch) == 100

    def test_bernadotte_for_davout_sinks_to_40(self, world, monkeypatch):
        # Neutral base 60 (MC-2 pin) - 20 hostility: I Corps does not march
        # for Davout. (A-D4 already bars auto-reinforcement outright; this
        # pins the same feud priced into the score itself.)
        self._stage_on_plains(world, "Bernadotte", "Davout")
        assert self._arrival(world, world.get_marshal("Bernadotte"),
                             world.get_marshal("Davout"), monkeypatch) == 40

    def test_enemy_side_rivalry_prices_minus_10(self, world, monkeypatch):
        # GR5 delta pin: Buxhowden's score for Kutuzov drops exactly 10
        # vs the same measurement with the edge cleared.
        self._stage_on_plains(world, "Buxhowden", "Kutuzov")
        buxhowden = world.get_marshal("Buxhowden")
        kutuzov = world.get_marshal("Kutuzov")
        with_edge = self._arrival(world, buxhowden, kutuzov, monkeypatch)
        buxhowden.set_relationship("Kutuzov", 0)
        without_edge = self._arrival(world, buxhowden, kutuzov, monkeypatch)
        assert without_edge - with_edge == 10


# ════════════════════════════════════════════════════════════════════════
# Card surface: the management screen shows the web (shown = applied)
# ════════════════════════════════════════════════════════════════════════

class TestCardSurface:
    def _cards(self, world):
        return {c["name"]: c for c in build_marshal_overview(world)}

    def test_davout_card_names_the_feud(self, world):
        rows = {r["name"]: r for r in self._cards(world)["Davout"]["relationships"]}
        assert rows["Bernadotte"]["value"] == -2
        assert rows["Bernadotte"]["label"] == "Hostile"
        assert rows["Murat"]["value"] == -1
        assert rows["Murat"]["label"] == "Rival"

    def test_lannes_card_names_the_friendship(self, world):
        rows = {r["name"]: r for r in self._cards(world)["Lannes"]["relationships"]}
        assert rows["Ney"]["value"] == 1
        assert rows["Ney"]["label"] == "Friendly"
        assert rows["Murat"]["value"] == -1

    def test_edge_free_marshal_card_shows_no_rows(self, world):
        assert self._cards(world)["Massena"]["relationships"] == [
            {"name": "Soult", "value": 1, "label": "Friendly"}]


# ════════════════════════════════════════════════════════════════════════
# Validator (MC-3 authoring contract)
# ════════════════════════════════════════════════════════════════════════

class TestValidator:
    BASE = {"name": "Test", "location": "Somewhere", "strength": 10000}

    def test_valid_relationships_pass(self):
        result = validate_marshal({**self.BASE,
                                   "relationships": {"Other": -2, "Friend": 1}})
        assert result.is_valid
        assert not result.warnings

    def test_non_dict_is_error(self):
        result = validate_marshal({**self.BASE, "relationships": [-1]})
        assert not result.is_valid

    def test_out_of_range_is_error(self):
        # Marshal.from_dict restores the dict RAW (pinned forward-compat
        # behavior — no clamp), so a scenario authoring 50 must fail loudly.
        result = validate_marshal({**self.BASE, "relationships": {"Other": 50}})
        assert not result.is_valid

    def test_non_int_is_error(self):
        result = validate_marshal({**self.BASE,
                                   "relationships": {"Other": "hostile"}})
        assert not result.is_valid
        result = validate_marshal({**self.BASE, "relationships": {"Other": True}})
        assert not result.is_valid

    def test_self_edge_warns(self):
        result = validate_marshal({**self.BASE, "relationships": {"Test": -1}})
        assert result.is_valid
        assert any("themselves" in w.message for w in result.warnings)

    def test_unknown_target_warns_at_scenario_level(self):
        scenario = {"marshals": {
            "A": {"name": "A", "location": "X", "strength": 1000,
                  "relationships": {"Ghost": -1}},
        }}
        result = validate_scenario(scenario)
        assert any("Ghost" in w.message and "unknown marshal" in w.message
                   for w in result.warnings)

    def test_shipped_scenario_validates_clean(self):
        import json
        from backend.ai.parser_eval import SCENARIO_1805_PATH
        with open(SCENARIO_1805_PATH, encoding="utf-8") as f:
            data = json.load(f)
        result = validate_scenario(data)
        assert result.is_valid
        assert not [w for w in result.warnings if "relationship" in w.path]


# ════════════════════════════════════════════════════════════════════════
# Isolation: the legacy fixture/rollback roster is untouched by MC-3
# ════════════════════════════════════════════════════════════════════════

class TestLegacyRosterUntouched:
    def test_legacy_asymmetric_feud_survives(self):
        # The Waterloo fixture's own authored pair — Ney hates Davout (-2),
        # Davout merely dislikes Ney (-1). Also the standing proof that the
        # substrate supports asymmetry: MC-3 pins symmetric DATA, not a
        # symmetric MECHANIC.
        legacy = WorldState(player_nation="France")
        assert legacy.get_marshal("Ney").get_relationship("Davout") == -2
        assert legacy.get_marshal("Davout").get_relationship("Ney") == -1
