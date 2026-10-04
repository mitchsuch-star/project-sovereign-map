"""SR-7d "The Doctrines" (Score Finish Step 3's eighth slice, October 3, 2026)
— DC-0 the substrate, DC-1 the strengths and flaws, DC-2 the cures.

Every pin stages the ORDINARY case on the real 1805 boot and reads the
production seam, never the constant it pins. Levers run UP in-test (the
shipped tree) and DOWN where the pin is byte-identity.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import random
from pathlib import Path

import pytest

from backend.commands import combat_executor as CE
from backend.commands import economy_executor as EE
from backend.commands.executor import CommandExecutor
from backend.game_logic import combat as CB
from backend.game_logic import doctrines as DC
from backend.game_logic import reforms as RF
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
    executor = CommandExecutor()
    return world, executor, {"world": world, "executor": executor}


@pytest.fixture
def scenario():
    with open(SCENARIO, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def world():
    return _boot()[0]


def _run(executor, game_state, command):
    with contextlib.redirect_stdout(io.StringIO()):
        random.seed(1805)
        return executor.execute({"command": command}, game_state)


def _jitter_into(det: int, lo: int, hi: int):
    """A jitter in the resolver's ±8 that lands `det + jitter` in (lo, hi],
    else None."""
    for j in range(-8, 9):
        if lo < det + j <= hi:
            return j
    return None


def _enact(world, nation, *law_ids):
    for law_id in law_ids:
        RF.enact_law(world, nation, RF.find_law(world, nation, law_id))


# ═════════════════════════ DC-0: the substrate ═════════════════════════════


class TestTheStore:
    def test_the_scenario_authors_five_doctrines_and_the_poor_country(self, scenario):
        assert set(k for k in scenario["doctrines"] if not k.startswith("_")) == set(DC.GREAT_POWERS)
        assert len(scenario["poor_country"]) == 14
        for court, row in scenario["doctrines"].items():
            if court.startswith("_"):
                continue
            assert row["strength"]["type"] in DC.CLAUSE_TYPES
            assert row["flaw"]["type"] in DC.CLAUSE_TYPES
            assert row["cured_by"]

    def test_one_serialized_field_and_a_round_trip(self, world):
        assert set(DC.table(world)) == set(DC.GREAT_POWERS)
        assert "Posen" in DC.poor_country(world)
        data = world.to_dict()
        assert "doctrines" in data and "courts" in data["doctrines"]
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(json.loads(json.dumps(data)))
        assert DC.table(back) == DC.table(world)
        assert DC.poor_country(back) == DC.poor_country(world)

    def test_the_legacy_world_and_the_tutorial_carry_none(self):
        with contextlib.redirect_stdout(io.StringIO()):
            legacy = WorldState()
            tutorial = WorldState.from_scenario(str(SCENARIO.parent / "tutorial_1805.json"))
        assert DC.table(legacy) == {}
        assert DC.table(tutorial) == {}
        assert DC.doctrine_of(tutorial, "France") is None

    def test_a_pre_doctrine_save_of_the_1805_campaign_is_backfilled_only_there(self, world, tmp_path, monkeypatch):
        from backend import save_manager
        monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path))
        data = world.to_dict()
        data.pop("doctrines", None)
        with contextlib.redirect_stdout(io.StringIO()):
            old = WorldState.from_dict(json.loads(json.dumps(data)))
        assert DC.table(old) == {}
        save_manager._backfill_doctrines(old)
        assert set(DC.table(old)) == set(DC.GREAT_POWERS)
        # a modded save receives none
        old.doctrines = {}
        old.scenario_name = "Someone's mod"
        save_manager._backfill_doctrines(old)
        assert DC.table(old) == {}

    def test_every_marshal_carries_the_derived_term_after_a_load(self, world):
        data = world.to_dict()
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(json.loads(json.dumps(data)))
        for m in back.marshals.values():
            assert DC.terms_of(m) == DC.derive_terms(back, m.nation), m.name
        assert "_doctrine_terms" in Marshal.DERIVED_STANDING_FIELDS
        assert "_doctrine_terms" not in Marshal.COORDINATION_TRANSIENT_FIELDS

    def test_the_term_is_never_serialized(self, world):
        m = world.marshals["Ney"]
        assert "_doctrine_terms" not in m.to_dict()


class TestTheValidator:
    def _errs(self, data, needle="doctrines"):
        return [str(e) for e in validate_scenario(copy.deepcopy(data)).errors if needle in str(e)]

    def test_the_shipped_scenario_is_clean(self, scenario):
        result = validate_scenario(copy.deepcopy(scenario))
        assert not [e for e in result.errors if "doctrine" in str(e) or "poor_country" in str(e)], result.errors

    def test_a_clause_outside_its_band_is_refused(self, scenario):
        scenario["doctrines"]["France"]["strength"]["value"] = -25
        assert any("[-20, 20]" in e for e in self._errs(scenario))

    def test_an_unknown_clause_type_is_refused(self, scenario):
        scenario["doctrines"]["Prussia"]["strength"] = {"type": "winter", "value": 1, "name": "x"}
        assert any("closed" in e for e in self._errs(scenario))

    def test_cured_by_must_name_a_cure_in_the_same_deck(self, scenario):
        scenario["doctrines"]["Britain"]["cured_by"] = "orders_in_council"
        assert any("cures" in e for e in self._errs(scenario))
        scenario["doctrines"]["Britain"]["cured_by"] = "no_such_law"
        assert any("not a law" in e for e in self._errs(scenario))

    def test_an_unknown_poor_country_name_is_refused(self, scenario):
        scenario["poor_country"].append("Narnia")
        assert any("Narnia" in e for e in self._errs(scenario, "poor_country"))

    def test_a_shared_clause_without_the_reason_warns(self, scenario):
        scenario["doctrines"]["Russia"].pop("shared_on_purpose")
        scenario["doctrines"]["Austria"].pop("shared_on_purpose")
        result = validate_scenario(copy.deepcopy(scenario))
        assert any("shared_on_purpose" in str(w) for w in result.warnings)

    def test_the_cures_effect_type_is_wired(self):
        assert "cures" in RF.WIRED_EFFECT_TYPES


class TestTheOneSetter:
    def test_no_bare_nation_write_outside_the_setter(self):
        """RV-6: an AST census over the backend — every write to a marshal's
        `.nation` goes through `doctrines.set_marshal_nation`; the only bare
        writes are the constructors' `self.nation`."""
        offenders = []
        for path in (ROOT / "backend").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                for tgt in node.targets:
                    if (isinstance(tgt, ast.Attribute) and tgt.attr == "nation"
                            and not (isinstance(tgt.value, ast.Name) and tgt.value.id == "self")):
                        if path.name == "doctrines.py":
                            continue
                        offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
        assert not offenders, offenders

    def test_the_setter_refreshes_the_term(self, world):
        ney = world.marshals["Ney"]
        assert DC.terms_of(ney)["attack"] == 1.0
        DC.set_marshal_nation(world, ney, "Prussia")
        assert ney.nation == "Prussia"
        assert DC.terms_of(ney)["attack"] == pytest.approx(1.10)
        assert DC.terms_of(ney)["defeat_morale"] == pytest.approx(1.5)


class TestTheOneArrivalBar:
    """RV-1: the resolver's inline bar and the odds row's `60` call
    `_arrival_threshold`; with the lever down the numbers are 60 / 65."""

    def test_lever_down_is_sixty_or_sixty_five(self, world, monkeypatch):
        monkeypatch.setattr(DC, "DOCTRINES_ACTIVE", False)
        ex = CommandExecutor()._combat
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        assert ex._arrival_threshold(ney, davout, "Swabia", world) == 65
        assert ex._arrival_threshold(ney, davout, "Swabia", world, assume_order=True) == 60

    def test_the_resolver_reads_the_bar_through_the_one_source(self):
        src = (ROOT / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        body = src[src.index("def _calculate_reinforcements"):src.index("_COORDINATION_FIELDS = list(")]
        assert "60 if has_explicit_order else 65" not in body
        assert "_arrival_threshold(" in body
        row = src[src.index("def _arrival_odds_row"):src.index("def _arrival_probability")]
        assert "_arrival_probability(det + 10, 60)" not in row
        assert "assume_order=True" in row


# ═════════════════════════ DC-1: the strengths and flaws ═══════════════════


class TestTheCorpsSystem:
    def test_a_french_corps_bar_is_ten_lower(self, world):
        ex = CommandExecutor()._combat
        ney, davout = world.marshals["Ney"], world.marshals["Davout"]
        assert ex._arrival_threshold(ney, davout, "Swabia", world) == 55
        assert ex._arrival_threshold(ney, davout, "Swabia", world, assume_order=True) == 50

    def test_rv2_the_doctrine_never_overrides_the_man(self, world):
        """Bernadotte's Eyes on a Crown, a live grievance, a hostile pair —
        the corps system lowers none of their bars (Auerstedt)."""
        ex = CommandExecutor()._combat
        davout = world.marshals["Davout"]
        bernadotte = world.marshals["Bernadotte"]
        assert bernadotte.ability.get("name") == "Eyes on a Crown"
        assert ex._arrival_threshold(bernadotte, davout, "Swabia", world) == 65
        assert ex._arrival_threshold(bernadotte, davout, "Swabia", world, assume_order=True) == 60
        ney = world.marshals["Ney"]
        ney.jealous_of = "Davout"
        assert ex._arrival_threshold(ney, davout, "Swabia", world) == 65
        ney.jealous_of = None
        ney.set_relationship("Davout", -2)
        assert ex._arrival_threshold(ney, davout, "Swabia", world) == 65

    def test_the_flaw_raises_the_bar_whatever_the_man(self, world):
        """The Hofkriegsrat is the army's: a hostile Austrian still waits."""
        ex = CommandExecutor()._combat
        mack = world.marshals["Mack"]
        charles = world.marshals["ArchdukeCharles"]
        assert ex._arrival_threshold(charles, mack, "Swabia", world) == 75
        charles.set_relationship("Mack", -2)
        assert ex._arrival_threshold(charles, mack, "Swabia", world) == 75

    def test_t7_monotone_over_the_whole_range(self, world):
        """The corps system never lowers P(arrive), the flaws never raise it,
        for every deterministic sum −10…150, both order states."""
        ex = CommandExecutor()._combat
        for assume in (True, False):
            base = 60 if assume else 65
            for det in range(-10, 151):
                p0 = ex._arrival_probability(det, base)
                assert ex._arrival_probability(det, base - 10) >= p0
                assert ex._arrival_probability(det, base + 10) <= p0


class TestDoctrineDelayed:
    """RV-16: a roll between the unshifted bar and the shifted one is
    `doctrine_delayed`, named, and never docked."""

    @staticmethod
    def _stage(world):
        mack = world.marshals["Mack"]
        charles = world.marshals["ArchdukeCharles"]
        ney = world.marshals["Ney"]
        for m in world.marshals.values():
            if m.name not in ("Mack", "ArchdukeCharles", "Ney"):
                m.location = "Paris" if m.nation == "France" else "Hungary"
        # Mack holds Tyrol; Charles stands in Bohemia beside it; Ney attacks
        # from Milan's side — the Austrian reinforcement roll is the case.
        mack.location, charles.location, ney.location = "Tyrol", "Bohemia", "Milan"
        # the MC-3 web authors Charles hostile to Mack (A-D4 would keep him
        # out without a written order); the case is the court's flaw alone
        charles.set_relationship("Mack", 0)
        mack.set_relationship("ArchdukeCharles", 0)
        charles.jealous_of = None
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        return mack, charles, ney

    def test_a_roll_between_the_bars_is_named_and_exempt(self, world, monkeypatch):
        mack, charles, ney = self._stage(world)
        ex = CommandExecutor()._combat
        det = ex._arrival_deterministic(charles, mack, world)
        # force the jitter so the score lands between the unshifted bar (65)
        # and the shifted one (75): the first reachable score in that band
        want = _jitter_into(det, 65, 75)
        assert want is not None, det
        monkeypatch.setattr(random, "randint", lambda a, b: want if (a, b) == (-8, 8) else 20)
        results = ex._calculate_reinforcements(mack, ney, "Tyrol", "Austria", world)
        row = next(r for r in results if r["marshal"] == "ArchdukeCharles")
        assert row["arrived"] is False
        assert row["reason"] == "doctrine_delayed"
        assert row["doctrine"] == "The Hofkriegsrat"
        assert row["threshold"] == 75
        assert DC.arrival_copy(row, "Mack") == "The Hofkriegsrat's orders reached Archduke Charles too late."

    def test_the_trust_dock_exempts_it(self):
        src = (ROOT / "backend" / "commands" / "combat_executor.py").read_text(encoding="utf-8")
        marker = '"literal_personality", "fate_intervened",\n'
        idx = src.index(marker)
        assert "doctrine_delayed" in src[idx:idx + 220]

    def test_the_corps_system_arrival_is_named(self, world, monkeypatch):
        ex = CommandExecutor()._combat
        ney, davout, mack = world.marshals["Ney"], world.marshals["Davout"], world.marshals["Mack"]
        for m in world.marshals.values():
            if m.name not in ("Ney", "Davout", "Mack"):
                m.location = "Paris" if m.nation == "France" else "Hungary"
        davout.location, ney.location, mack.location = "Swabia", "Rhineland", "Swabia"
        det = ex._arrival_deterministic(ney, davout, world)
        want = _jitter_into(det, 55, 65)    # the corps system decided it
        while want is None and ney.skills.get("logistics", 5) > 1:
            ney.skills["logistics"] = int(ney.skills.get("logistics", 5)) - 1
            det = ex._arrival_deterministic(ney, davout, world)
            want = _jitter_into(det, 55, 65)
        assert want is not None, det
        monkeypatch.setattr(random, "randint", lambda a, b: want if (a, b) == (-8, 8) else 20)
        results = ex._calculate_reinforcements(davout, mack, "Swabia", "France", world)
        row = next(r for r in results if r["marshal"] == "Ney")
        assert row["arrived"] is True and row.get("doctrine_arrived") is True
        assert DC.arrival_copy(row, "Davout") == "The corps system brought Ney in."


class TestTheCombatTerms:
    def test_the_line_holds_on_a_british_lead_defending(self, world):
        moore = next(m for m in world.marshals.values() if m.nation == "Britain")
        with_term = moore.get_defense_modifier(consume=False)
        moore._doctrine_terms = dict(DC.NEUTRAL_TERMS)
        without = moore.get_defense_modifier(consume=False)
        assert with_term == pytest.approx(min(1.75, without * 1.15))

    def test_fredericks_drill_on_a_prussian_attack_and_a_reinforcers_weight(self, world):
        brunswick = world.marshals["Brunswick"]
        with_term = brunswick.get_attack_modifier(1.0, consume=False)
        brunswick._doctrine_terms = dict(DC.NEUTRAL_TERMS)
        assert with_term == pytest.approx(brunswick.get_attack_modifier(1.0, consume=False) * 1.10)

    def test_a_british_lead_attacking_gains_nothing_from_the_line(self, world):
        moore = next(m for m in world.marshals.values() if m.nation == "Britain")
        with_term = moore.get_attack_modifier(1.0, consume=False)
        moore._doctrine_terms = dict(DC.NEUTRAL_TERMS)
        assert with_term == pytest.approx(moore.get_attack_modifier(1.0, consume=False))

    def test_the_term_survives_every_clear_path(self, world):
        brunswick = world.marshals["Brunswick"]
        brunswick.clear_combat_transient_state()
        brunswick.clear_coordination_transients()
        assert DC.terms_of(brunswick)["attack"] == pytest.approx(1.10)

    def test_lever_down_is_neutral(self, world, monkeypatch):
        monkeypatch.setattr(DC, "DOCTRINES_ACTIVE", False)
        DC.refresh_doctrine_terms(world)
        for m in world.marshals.values():
            assert DC.terms_of(m) == DC.NEUTRAL_TERMS


class TestStubbornAndBrittle:
    def test_the_penalty_is_scaled_after_its_own_cap(self, world):
        kutuzov = world.marshals["Kutuzov"]
        brunswick = world.marshals["Brunswick"]
        assert DC.scaled_defeat_penalty(kutuzov, 42) == (21, {
            "marshal": "Kutuzov", "nation": "Russia", "name": "Stubborn", "base": 42, "applied": 21})
        applied, rec = DC.scaled_defeat_penalty(brunswick, CB.DECISIVENESS_MORALE_CAP)
        assert applied == int(round(CB.DECISIVENESS_MORALE_CAP * 1.5)) and applied > CB.DECISIVENESS_MORALE_CAP
        assert DC.scaled_defeat_penalty(world.marshals["Ney"], 42) == (42, None)
        assert DC.scaled_defeat_penalty(kutuzov, 0) == (0, None)

    def test_the_morale_line_names_the_doctrine(self):
        assert "Stubborn softened the rout (−21 morale, not −42)" in DC.morale_line(
            {"nation": "Russia", "name": "Stubborn", "base": 42, "applied": 21})
        assert "Brittle deepened the rout (−63 morale, not −42)" in DC.morale_line(
            {"nation": "Prussia", "name": "Brittle", "base": 42, "applied": 63})
        assert DC.morale_line({"nation": "Russia", "name": "Stubborn", "base": 42, "applied": 42}) == ""

    def test_a_lopsided_defeat_in_the_resolver_scales_the_losers_penalty(self, world, monkeypatch):
        """Both resolver paths read the loser's term: a Russian defender
        out-bled 3:1 keeps half the rout, a Prussian one loses half as much again."""
        ex = CommandExecutor()._combat
        resolver = CB.CombatResolver()
        ney = world.marshals["Ney"]
        for nation, factor in (("Russia", 0.5), ("Prussia", 1.5)):
            foe = next(m for m in world.marshals.values() if m.nation == nation)
            foe.morale = 80
            foe.strength = 20000
            ney.strength = 60000
            ney.morale = 90
            random.seed(7)
            with contextlib.redirect_stdout(io.StringIO()):
                res = resolver.resolve_battle(ney, foe, terrain="plains")
            rec = res.get("doctrine_morale")
            if rec:
                assert rec["nation"] == nation
                assert rec["applied"] == int(round(rec["base"] * factor))


class TestTheRecruitClauses:
    def test_the_draft_prices_the_doctrine_and_names_it(self, world):
        ex = CommandExecutor()._economy
        vienna = world.get_region("Vienna")
        cost, terms = ex._recruit_cost_terms(vienna, world, nation="Austria", arm="infantry")
        assert any("The Hereditary Lands" in t and "0.85" in t for t in terms), terms
        london = world.get_region("London")
        cost_b, terms_b = ex._recruit_cost_terms(london, world, nation="Britain", arm="infantry")
        assert any("Irreplaceable" in t and "1.25" in t for t in terms_b), terms_b

    def test_rv17_the_substitute_market_is_not_priced(self, world):
        ex = CommandExecutor()._economy
        london = world.get_region("London")
        _cost, terms = ex._recruit_cost_terms(london, world, nation="Britain", arm="infantry", draft=False)
        assert not any("Irreplaceable" in t for t in terms)

    def test_lever_down_is_byte_identical(self, world, monkeypatch):
        ex = CommandExecutor()._economy
        vienna = world.get_region("Vienna")
        up = ex._calculate_recruit_cost(vienna, world, nation="Austria", arm="infantry")
        monkeypatch.setattr(DC, "DOCTRINES_ACTIVE", False)
        down = ex._calculate_recruit_cost(vienna, world, nation="Austria", arm="infantry")
        assert up == int(round(down * 0.85))

    def test_the_hereditary_lands_stack_with_the_generalissimus(self, world):
        ex = CommandExecutor()._economy
        vienna = world.get_region("Vienna")
        base = ex._calculate_recruit_cost(vienna, world, nation="Austria", arm="infantry")
        _enact(world, "Austria", "generalissimus")
        with_law = ex._calculate_recruit_cost(vienna, world, nation="Austria", arm="infantry")
        assert with_law < base


class TestLivingOffTheLand:
    def test_the_homeland_and_an_allys_soil_never_bite(self, world):
        paris = world.get_region("Paris")
        assert DC.supply_factor(world, "France", paris) == (1.0, "")
        # the exemption has to DECIDE something: a stripped homeland province
        # (the sweep found the bare case inert — Paris was never stripped)
        paris.war_damage = 0.45
        assert DC.supply_ground(world, "France", paris) is None
        assert DC.supply_factor(world, "France", paris, forecast=False) == (1.0, "")
        assert DC.supply_mark(world, "France", paris, True) is None
        paris.war_damage = 0.0
        franconia = world.get_region("Franconia")    # Bavaria's — a French ally's soil
        assert DC.supply_ground(world, "France", franconia) is None
        aragon = world.get_region("Aragon")          # listed poor country, but Spain's
        assert DC.supply_ground(world, "France", aragon) is None

    def test_poor_country_bites_whoever_holds_it(self, world):
        posen = world.get_region("Posen")
        assert DC.supply_factor(world, "France", posen) == (0.8, "Living off the land")
        posen.controller = "France"
        world.invalidate_active_nations_cache()
        assert DC.supply_factor(world, "France", posen) == (0.8, "Living off the land")
        cap_flaw = world.get_effective_supply_cap("France", posen)
        posen.controller = "Prussia"
        world.invalidate_active_nations_cache()
        assert cap_flaw == int(posen.supply_capacity * world.HOME_SUPPLY_MULTIPLIER * 0.8)

    def test_stripped_country_is_read_forward(self, world):
        """A province at 0.26 today is at 0.24 when the next pass reads it —
        a forecast says fed, and so does the bill when it comes; a province
        at 0.27 is stripped in both."""
        tyrol = world.get_region("Tyrol")          # Austrian soil, at war
        tyrol.war_damage = 0.26
        assert DC.supply_factor(world, "France", tyrol)[0] == 1.0
        assert DC.supply_factor(world, "France", tyrol, forecast=False)[0] == 0.8
        tyrol.war_damage = 0.27
        assert DC.supply_factor(world, "France", tyrol)[0] == 0.8
        # the muster's own battle counts
        tyrol.war_damage = 0.20
        assert DC.supply_factor(world, "France", tyrol, extra_damage=0.10)[0] == 0.8

    def test_a_depot_is_not_a_cure(self, world):
        posen = world.get_region("Posen")
        before = world.get_effective_supply_cap("France", posen)
        posen.buildings.append({"type": "supply_depot", "damaged": False})
        after = world.get_effective_supply_cap("France", posen)
        assert after > before
        assert DC.supply_factor(world, "France", posen)[0] == 0.8

    def test_the_bill_reads_the_post_recovery_value_and_the_forecast_reads_forward(self, world):
        """Tyrol at 0.26 today: the forecast says fed (0.24 next pass), and the
        attrition pass — which runs AFTER the recovery tick — bills fed too;
        at 0.28 both say stripped. The pass's own call passes forecast=False."""
        tyrol = world.get_region("Tyrol")
        ney = world.marshals["Ney"]
        for m in world.marshals.values():
            if m.location == "Tyrol":
                m.location = "Hungary"
        ney.location = "Tyrol"
        tyrol.controller = "France"
        world.invalidate_active_nations_cache()
        fed_cap = int(tyrol.supply_capacity * world.HOME_SUPPLY_MULTIPLIER)
        ney.strength = int(fed_cap * 0.9)          # over 80% of the fed cap, under it whole
        tyrol.war_damage = 0.28
        with contextlib.redirect_stdout(io.StringIO()):
            world.process_war_damage_recovery()     # 0.28 → 0.26, as advance_turn does first
            events = world.process_supply_attrition()
        assert any(e.get("marshal") == "Ney" for e in events), "the bill reads 0.26 ≥ 0.25: stripped"
        tyrol.war_damage = 0.26
        with contextlib.redirect_stdout(io.StringIO()):
            world.process_war_damage_recovery()     # 0.26 → 0.24
            events = world.process_supply_attrition()
        assert not any(e.get("marshal") == "Ney" for e in events), "the bill reads 0.24 < 0.25: fed"

    def test_a_commissioned_marshal_takes_his_courts_doctrine(self, world):
        from backend.game_logic.recruitment import commission_marshal
        pool = world.marshal_pool.get("Prussia") or []
        assert pool, "Prussia authors a bench"
        world.nation_gold["Prussia"] = 50000
        with contextlib.redirect_stdout(io.StringIO()):
            result = commission_marshal(world, "Prussia", pool[0])
        name = result.get("marshal") or result.get("name") or pool[0].get("name")
        m = world.marshals[name]
        assert DC.terms_of(m)["attack"] == pytest.approx(1.10)

    def test_the_other_courts_have_no_supply_clause(self, world):
        posen = world.get_region("Posen")
        for nation in ("Austria", "Russia", "Prussia", "Britain"):
            assert DC.supply_factor(world, nation, posen) == (1.0, "")

    def test_the_bite_is_billed_by_the_attrition_pass(self, world):
        posen = world.get_region("Posen")
        posen.controller = "France"
        world.invalidate_active_nations_cache()
        ney = world.marshals["Ney"]
        for m in world.marshals.values():
            if m.location == "Posen":
                m.location = "Berlin"
        ney.location = "Posen"
        ney.strength = int(posen.supply_capacity * world.HOME_SUPPLY_MULTIPLIER * 0.9)
        with contextlib.redirect_stdout(io.StringIO()):
            events = world.process_supply_attrition()
        assert any(e.get("marshal") == "Ney" for e in events), "the flaw's cap should bite at 90% of the fed cap"


class TestTheProvinceMark:
    """RV-13 — found by the DC-3c capture, not by the first pins: the FILTERED
    map summary rebuilds every province's keys and had dropped the mark."""

    def test_the_filtered_summary_carries_the_mark_on_both_branches(self, world):
        tyrol = world.get_region("Tyrol")
        tyrol.war_damage = 0.35
        world.marshals["Lannes"].location = "Tyrol"
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        with contextlib.redirect_stdout(io.StringIO()):
            summary = world.get_filtered_game_state_summary()
        md = summary["map_data"]
        assert md["Posen"]["visibility_status"] == "unknown"
        assert md["Posen"]["war_damage"] == -1                       # the fog sentinel
        assert md["Posen"]["doctrine_supply"]["poor"] is True        # geography always shows
        assert "Poor country" in md["Posen"]["doctrine_supply"]["line"]
        assert md["Tyrol"]["doctrine_supply"]["poor"] is False
        assert "Stripped by war (35%)" in md["Tyrol"]["doctrine_supply"]["line"]
        assert md["Paris"]["doctrine_supply"] is None                 # the homeland carries no mark

    def test_a_fogged_stripped_province_says_scout_it(self, world):
        bohemia = world.get_region("Bohemia")
        bohemia.war_damage = 0.35
        for m in world.marshals.values():
            if m.location == "Bohemia":
                m.location = "Hungary"
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        assert not world.region_econ_visible("Bohemia")
        mark = DC.supply_mark(world, "France", bohemia, world.region_econ_visible("Bohemia"))
        assert mark == {"poor": False, "line": "Stripped? unknown — scout it"}
        assert DC.supply_mark(world, "France", bohemia, True)["line"].startswith("Stripped by war (35%)")

    def test_lever_down_sends_no_mark(self, world, monkeypatch):
        monkeypatch.setattr(DC, "DOCTRINES_ACTIVE", False)
        with contextlib.redirect_stdout(io.StringIO()):
            summary = world.get_filtered_game_state_summary()
        assert summary["map_data"]["Posen"]["doctrine_supply"] is None


# ═════════════════════════ DC-2: the cures ═════════════════════════════════


class TestTheCure:
    def test_t2_each_flaw_has_one_cure_and_the_staff_carries_it(self, world):
        for nation in DC.GREAT_POWERS:
            assert DC.cure_law(world, nation) is not None, nation
            assert not DC.flaw_cured(world, nation)
        # France: the Train alone does nothing without the Staff (RV-15)
        _enact(world, "France", "train_des_equipages")
        assert not DC.flaw_cured(world, "France")
        _enact(world, "France", "grand_quartier_general")
        assert DC.flaw_cured(world, "France")
        assert DC.supply_factor(world, "France", world.get_region("Posen")) == (1.0, "")
        # a repeal of the Staff brings the flaw back at the next read
        RF.repeal_law(world, "France", RF.find_law(world, "France", "grand_quartier_general"))
        assert not DC.flaw_cured(world, "France")
        assert DC.supply_factor(world, "France", world.get_region("Posen"))[0] == 0.8

    def test_for_austria_and_russia_the_cure_is_the_staff(self, world):
        _enact(world, "Austria", "corps_d_armee")
        assert DC.flaw_cured(world, "Austria")
        ex = CommandExecutor()._combat
        assert ex._arrival_threshold(world.marshals["ArchdukeCharles"], world.marshals["Mack"],
                                     "Swabia", world) == 65
        _enact(world, "Russia", "divisional_system")
        assert DC.flaw_cured(world, "Russia")

    def test_britains_and_prussias_cures_wait_for_the_staff(self, world):
        _enact(world, "Britain", "militia_transfer")
        assert not DC.flaw_cured(world, "Britain")
        _enact(world, "Britain", "horse_guards_reforms")
        assert DC.flaw_cured(world, "Britain")
        _enact(world, "Prussia", "articles_of_war")
        assert not DC.flaw_cured(world, "Prussia")
        assert DC.terms_of(world.marshals["Brunswick"])["defeat_morale"] == pytest.approx(1.5)
        _enact(world, "Prussia", "general_staff")
        assert DC.flaw_cured(world, "Prussia")
        assert DC.terms_of(world.marshals["Brunswick"])["defeat_morale"] == 1.0

    def test_a_lapse_brings_the_flaw_back(self, world):
        _enact(world, "Prussia", "articles_of_war", "general_staff")
        assert DC.flaw_cured(world, "Prussia")
        world.nation_gold["Prussia"] = -5000
        with contextlib.redirect_stdout(io.StringIO()):
            RF.process_law_lapses(world)
        assert not DC.flaw_cured(world, "Prussia")
        assert DC.terms_of(world.marshals["Brunswick"])["defeat_morale"] == pytest.approx(1.5)

    def test_the_cures_lever_down_cures_nothing(self, world, monkeypatch):
        monkeypatch.setattr(DC, "THE_CURES_HEAL", False)
        _enact(world, "Austria", "corps_d_armee")
        assert not DC.flaw_cured(world, "Austria")

    def test_the_cure_beat_fires_once_when_both_stand(self, world):
        world.pending_dispatch_events = []
        _enact(world, "Britain", "militia_transfer")
        assert not [e for e in world.pending_dispatch_events if e["type"] == "doctrine_cured_abroad"]
        _enact(world, "Britain", "horse_guards_reforms")
        beats = [e for e in world.pending_dispatch_events if e["type"] == "doctrine_cured_abroad"]
        assert len(beats) == 1 and beats[0]["template_vars"]["flaw"] == "Irreplaceable"

    def test_the_laws_tab_names_the_cure_and_what_it_lifts(self, world):
        posen = world.get_region("Posen")
        posen.controller = "France"
        world.invalidate_active_nations_cache()
        ney = world.marshals["Ney"]
        ney.location = "Posen"
        payload = RF.laws_payload(world, "France")
        train = next(r for r in payload["rows"] if r["id"] == "train_des_equipages")
        assert "Living off the land" in train["cure_line"]
        assert "1 corps drawing 80% now" in train["cure_line"]
        assert "Grand Quartier" in train["cure_line"]


class TestTheAISavesForTheStaff:
    def test_a_court_past_half_the_staffs_price_enacts_nothing_cheaper(self, world, monkeypatch):
        world.current_turn = 12
        world.nation_gold["Austria"] = 6000
        found = RF.find_ai_enactment(world, "Austria", 6000, 1)
        assert found is None or found["target"] == "corps_d_armee"
        monkeypatch.setattr(RF, "THE_AI_SAVES_FOR_THE_STAFF", False)
        found_down = RF.find_ai_enactment(world, "Austria", 6000, 1)
        assert found_down is not None and found_down["target"] != "corps_d_armee"

    def test_under_half_the_rung_is_unchanged(self, world):
        world.current_turn = 12
        world.nation_gold["Austria"] = 3000
        assert RF.find_ai_enactment(world, "Austria", 3000, 1) is not None


# ═════════════════════════ DC-3: the surfaces (T1) ═════════════════════════


class TestTheReadingSurfaces:
    def test_the_generals_screen_carries_our_doctrine(self, world):
        import backend.main as M
        saved = (M.world, dict(M.game_state))
        try:
            M.world = world
            M.game_state["world"] = world
            payload = M.get_marshal_overview()
        finally:
            M.world, M.game_state = saved[0], saved[1]
        d = payload["doctrine"]
        assert d["name"] == "The Corps System"
        assert d["strength"]["name"] == "The corps system" and "10 lower" in d["strength"]["line"]
        assert d["flaw"]["name"] == "Living off the land" and "80%" in d["flaw"]["line"]
        assert d["flaw"]["status_line"].startswith("uncured — the Train des")

    def test_every_great_powers_card_carries_one_doctrine_line(self, world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        _enact(world, "Austria", "corps_d_armee")
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = build_diplomatic_ledger(world)
        rows = {n.get("name") or n.get("nation"): n.get("doctrine") for n in ledger["nations"]}
        assert rows["Austria"] == "The Hereditary Lands; flaw: The Hofkriegsrat (cured since turn 1)"
        assert rows["Prussia"].startswith("Frederick's Drill; flaw: Brittle (uncured")
        assert rows["Britain"].startswith("The Line Holds; flaw: Irreplaceable (uncured")
        assert "\n" not in rows["Russia"]
        minor = next(v for k, v in rows.items() if k not in DC.GREAT_POWERS and k != "France")
        assert minor is None

    def test_the_first_morning_names_our_doctrine(self, world):
        from backend.game_logic.dispatch import build_morning_dispatch
        with contextlib.redirect_stdout(io.StringIO()):
            d = build_morning_dispatch(world, boot=True)
        assert d["today"]["doctrine"].startswith("Our doctrine: The Corps System —")
        assert "(G)" in d["today"]["doctrine"]

    def test_the_desk_answers_the_three_questions(self, world):
        from backend.ai.question_desk import answer_board_question, classify_board_question
        nations = list(world.enemy_nations) + [world.player_nation]
        q = classify_board_question("what is our doctrine?", nations=nations)
        assert q["kind"] == "doctrine_own"
        own = answer_board_question(world, q)
        assert "The Corps System" in own and "Living off the land" in own
        q = classify_board_question("what is Austria's doctrine?", nations=nations)
        assert q["kind"] == "doctrine_nation" and q["subject"] == "Austria"
        assert "The Hereditary Lands" in answer_board_question(world, q)
        q = classify_board_question("what are Austria's weaknesses?", nations=nations)
        assert q["weaknesses"] is True
        weak = answer_board_question(world, q)
        assert "The Hofkriegsrat" in weak and "Hereditary" not in weak
        assert classify_board_question("what is Narnia's doctrine?", nations=nations) is None

    def test_the_help_block_names_the_doctrine(self):
        from backend.commands.meta_executor import MetaExecutor
        src = (ROOT / "backend" / "commands" / "meta_executor.py").read_text(encoding="utf-8")
        assert '"what is our doctrine?"' in src
        assert '(("doctrine", "doctrines"), "marshals")' in src
        assert MetaExecutor is not None

    def test_the_laws_tab_cure_line_and_the_cured_form(self, world):
        _enact(world, "Austria", "corps_d_armee")
        rows = RF.laws_payload(world, "Austria")["rows"]
        corps = next(r for r in rows if r["id"] == "corps_d_armee")
        assert corps["cure_line"] == "Cures The Hofkriegsrat — cured since turn 1."
        landwehr = next(r for r in rows if r["id"] == "landwehr")
        assert "cure_line" not in landwehr
        # the clause renders in the law's own "what it does" list too
        assert RF.effect_line({"type": "cures", "flaw": "The Hofkriegsrat"}) == (
            "cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands")
        assert any(e.startswith("cures The Hofkriegsrat") for e in corps["effects"]), corps["effects"]


class TestTheFiringSurfaces:
    def test_the_muster_row_names_the_bar(self, world, monkeypatch):
        ex = CommandExecutor()._combat
        davout, ney = world.marshals["Davout"], world.marshals["Ney"]
        davout.location, ney.location = "Swabia", "Rhineland"
        row = ex._arrival_odds_row(davout, ney, "Swabia", world, "answers_the_guns")
        assert "(The corps system lowers the bar by 10)" in row["arrival_note"]
        # RV-1 at the second reader: the with-support odds are rolled against
        # the doctrine's bar too — a literal 60 would print the lever-down
        # figure (the sweep found the note alone inert).
        # A strong man's odds saturate on both bars (Ney at logistics 5 reads
        # 99 either way), so the pin stages him where the bar decides it.
        ney.skills["logistics"] = 0
        row = ex._arrival_odds_row(davout, ney, "Swabia", world, "answers_the_guns")
        with_doctrine = row["arrival_odds_with_support"]
        monkeypatch.setattr(DC, "FRANCE_DOCTRINE", False)
        lever_down = ex._arrival_odds_row(davout, ney, "Swabia", world, "answers_the_guns")
        assert "lowers the bar" not in lever_down["arrival_note"]
        assert with_doctrine > lever_down["arrival_odds_with_support"]
        assert row["arrival_odds"] > lever_down["arrival_odds"]
        charles, mack = world.marshals["ArchdukeCharles"], world.marshals["Mack"]
        charles.location = "Bohemia"
        row = ex._arrival_odds_row(mack, charles, "Tyrol", world, "answers_the_guns")
        assert "(The Hofkriegsrat raises the bar by 10)" in row["arrival_note"]

    def test_the_enemy_line_names_slow_concentration(self, world, monkeypatch):
        ex = CommandExecutor()._combat
        ney, mack, john = world.marshals["Ney"], world.marshals["Mack"], world.marshals["ArchdukeJohn"]
        for m in world.marshals.values():
            if m.name not in ("Ney", "Mack", "ArchdukeJohn"):
                m.location = "Paris" if m.nation == "France" else "Hungary"
        # Archduke John, not Charles: Charles refuses Mack by the authored
        # hostile pair (A-D4), which left the first staging silent.
        ney.location, mack.location, john.location = "Rhineland", "Swabia", "Franconia"
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        gs = {"world": world}
        with contextlib.redirect_stdout(io.StringIO()):
            preview = ex._build_muster_preview(ney, mack, world, gs)
        note = preview["target"]["reinforcement_note"]
        assert "does not stand alone" in note, note
        assert "Their columns gather slowly — The Hofkriegsrat: the bar 10 higher." in note
        monkeypatch.setattr(DC, "AUSTRIA_DOCTRINE", False)
        with contextlib.redirect_stdout(io.StringIO()):
            preview = ex._build_muster_preview(ney, mack, world, gs)
        note = preview["target"]["reinforcement_note"]
        assert "does not stand alone" in note and "Hofkriegsrat" not in note

    def test_the_report_names_the_arrival_and_the_corps_apart(self, world):
        ex = CommandExecutor()._combat
        davout, mack = world.marshals["Davout"], world.marshals["Mack"]
        rows = [{"marshal": "Ney", "arrived": True, "doctrine_arrived": True,
                 "doctrine": "The corps system", "origin": "Rhineland"},
                {"marshal": "Lannes", "arrived": True, "origin": "Lorraine"},
                {"marshal": "Soult", "arrived": False, "reason": "doctrine_delayed",
                 "doctrine": "The corps system"}]
        lines = ex._doctrine_lines(world, davout, mack, rows, [])
        assert "The corps system brought Ney in." in lines
        assert "The corps system's orders reached Soult too late." in lines
        assert "Berthier: the corps marched apart and arrived together." in lines
        assert ex._doctrine_lines(world, davout, mack, rows[:1], []) == ["The corps system brought Ney in."]

    def test_the_snapshot_rows_and_the_morale_line(self, world):
        from backend.game_logic import battle_report as BR
        brunswick, ney = world.marshals["Brunswick"], world.marshals["Ney"]
        rows = BR.snapshot_attacker_modifiers(brunswick, ney, "plains", 0.0, 0, False)
        drill = next(r for r in rows if r.get("doctrine"))
        assert drill == {"label": "Frederick's Drill", "value": 10, "type": "bonus", "doctrine": True}
        moore = world.marshals["Moore"]
        rows = BR.snapshot_defender_modifiers(moore, ney, "plains", 0.0)
        line = next(r for r in rows if r.get("doctrine"))
        assert line["label"] == "The Line Holds" and 1 <= line["value"] <= 15
        assert not any(r.get("doctrine") for r in BR.snapshot_attacker_modifiers(ney, brunswick, "plains", 0.0, 0, False))
        report = BR.generate_battle_report({
            "attacker": {"name": "Ney", "casualties": 100}, "defender": {"name": "Kutuzov", "casualties": 300},
            "attacker_original_strength": 20000, "defender_original_strength": 20000,
            "modifier_snapshot": {"attacker": [], "defender": [line]},
            "doctrine_morale": {"nation": "Russia", "name": "Stubborn", "base": 42, "applied": 21},
            "outcome": "attacker_tactical_victory"})
        assert report["morale_line"].startswith("the Russian army would not break: Stubborn softened the rout")
        assert report["doctrine_rows"] == [f"The Line Holds +{line['value']}% (Kutuzov)"]

    def test_the_shelf_names_the_flaw(self, world):
        from backend.game_logic import battle_diorama as BD
        src = (ROOT / "backend" / "game_logic" / "battle_diorama.py").read_text(encoding="utf-8")
        assert 'reason == "doctrine_delayed" and r.get("doctrine")' in src
        assert BD.ABSENT_STATUSES

    def test_the_enemy_phase_recruit_line_carries_the_term(self, world):
        world_, executor, gs = _boot()
        mack = world_.marshals["Mack"]
        mack.location = "Vienna"
        world_.nation_gold["Austria"] = 20000
        world_.manpower_pools["Austria"]["infantry"] = 60000
        result = _run(executor, gs, {"type": "specific", "marshal": "Mack", "action": "recruit",
                                     "target": "Vienna", "_autonomous_execution": True})
        assert result.get("success"), result.get("message")
        assert result["doctrine_note"] == "The Hereditary Lands, ×0.85"

    def test_the_supply_headline_names_the_train(self, world):
        from backend.game_logic.dispatch import _supply_strain_candidate
        posen = world.get_region("Posen")
        posen.controller = "France"
        ney = world.marshals["Ney"]
        ney.location = "Posen"
        ney.strength = 60000
        world.invalidate_active_nations_cache()
        now = int(world.current_turn)
        for t in (now - 1, now):
            world.event_log.append({"type": "supply_attrition", "nation": "France", "region": "Posen",
                                    "turn": t, "losses": 900, "marshal": "Ney"})
        with contextlib.redirect_stdout(io.StringIO()):
            cand = _supply_strain_candidate(world, "France")
        assert cand is not None
        remedy = cand["fields"]["remedy"]
        assert "Living off the land: this poor country feeds a French army 80%." in remedy
        assert "Train des" in remedy

    def test_the_muster_supply_note_names_the_flaw(self, world):
        ex = CommandExecutor()._combat
        ney = world.marshals["Ney"]
        posen = world.get_region("Posen")
        hohenlohe = world.marshals["Hohenlohe"]
        for m in world.marshals.values():
            if m.name not in ("Ney", "Hohenlohe"):
                m.location = "Paris" if m.nation == "France" else "Hungary"
        ney.location, hohenlohe.location = "Dresden", "Posen"
        world.regions["Dresden"].controller = "France"
        world.invalidate_active_nations_cache()
        world.calculate_visibility()
        if not world.region_econ_visible("Posen"):
            world.get_region_intel("Posen").visibility = "full"
        with contextlib.redirect_stdout(io.StringIO()):
            preview = ex._build_muster_preview(ney, hohenlohe, world, {"world": world})
        note = preview.get("supply_note", "")
        assert "Living off the land: this poor country feeds our army 80%" in note, note


# ═══════════════════════════════════════════════════════════════════════════
# T5 (DOCTRINES_SPEC.md §6) — the road to 45, re-measured at Step 4's exit
# ═══════════════════════════════════════════════════════════════════════════

class TestT5TheRoadToFortyFiveAfterTheDoctrines:
    """SR-7d-X2's T5, measured October 3, 2026: the three Q0 roads re-driven on
    the shipped tree with the doctrines up and with `DOCTRINES_ACTIVE` down
    (the counterfactual on the SAME tree — the RF-1 reading of Sept 27
    predates Steps 1–4). Pass = the best road's titled count falls by no more
    than two provinces. The archives are the record; this pin reads them."""

    DIGESTS = Path(__file__).resolve().parents[1] / "docs" / "audits" / "playtest_digests"
    ROADS = ("aar-road", "gev-a", "gev-b")

    def _best(self, suffix):
        best = 0
        for road in self.ROADS:
            data = json.loads((self.DIGESTS / f"sf4-q0-{road}{suffix}" / "titled.json")
                              .read_text(encoding="utf-8"))
            series = data.get("series") or [{"titled": data["titled"]}]
            best = max(best, max(int(s["titled"]) for s in series))
        return best

    def test_the_best_road_falls_by_no_more_than_two(self):
        with_doctrines, without = self._best(""), self._best("-nodoc")
        assert (with_doctrines, without) == (36, 37), (with_doctrines, without)
        assert without - with_doctrines <= 2

    def test_the_counterfactual_ran_with_the_lever_down(self):
        for road in self.ROADS:
            meta = json.loads((self.DIGESTS / f"sf4-q0-{road}-nodoc" / "meta.json")
                              .read_text(encoding="utf-8"))
            assert "backend.game_logic.doctrines:DOCTRINES_ACTIVE=0" in meta["levers"], meta["levers"]
            shipped = json.loads((self.DIGESTS / f"sf4-q0-{road}" / "meta.json")
                                 .read_text(encoding="utf-8"))
            assert shipped["levers"] == []
