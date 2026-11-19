"""Row OC — "the rulings built" (ruled November 17, 2026, row BA's session BA-6
and row MC, under the user's "leave no open calls or anything make decisions
yourself soundly with research"; the record `docs/audits/
OPEN_CALLS_RULED_2026_11_17.md` §5; BUILT November 18, 2026 — the rules
`SYSTEMS_REFERENCE.md` §226, the seams `tests/_oc_seams.py`).

Each ruling that landed in row OC was a STRICT xfail here until it landed;
each is now its behaviour test, reading the seam the ruling names. The two
rulings homed at Session H's head keep their strict xfails (CLAUDE.md rule 9:
owner row, landing slice, done-when, STATUS line, behaviour test).
"""
from __future__ import annotations

import contextlib
import importlib
import inspect
import io
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.ai import enemy_ai as EA  # noqa: E402
from backend.game_logic import affairs as AF  # noqa: E402
from backend.game_logic import ai_diplomacy as AD  # noqa: E402
from backend.game_logic import ledger as LG  # noqa: E402
from backend.game_logic import naval as NV  # noqa: E402
from backend.game_logic import reforms as RF  # noqa: E402
from backend.game_logic import standing as ST  # noqa: E402
from backend.models import world_state as WS  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402

SCENARIO = REPO / "godot-client/project-sovereign/assets/maps/europe_1805.json"

_H = ("RULED November 17, 2026 (BA-6) — HOMED at Session H's head "
      "(docs/audits/OPEN_CALLS_RULED_2026_11_17.md §3); this pin turns red the day it lands")


def _seam_up(module: str, name: str) -> bool:
    fn = getattr(importlib.import_module(module), name, None)
    return callable(fn) and not inspect.signature(fn).parameters and fn() is True


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def _board():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO)).to_dict()


@pytest.fixture
def world(_board):
    with _quiet():
        return WorldState.from_dict(_board)


def _row(world, nation, law_id):
    return next(r for r in RF.deck(world, nation) if r.get("id") == law_id)


# ═══════════════════ the seams ═════════════════════════════════════════════

class TestTheSeams:

    def test_every_seam_is_up_in_the_game(self):
        from tests._oc_seams import OC_SEAMS_BY_ROW
        for row, specs in OC_SEAMS_BY_ROW.items():
            for spec in specs:
                target, expr = spec.split("=", 1)
                module, name = target.split(":", 1)
                assert expr == "False", spec
                assert _seam_up(module, name), (row, spec)

    def test_they_are_folded_into_the_standing_list(self):
        from tests._oc_seams import OC_SEAMS_DOWN
        from tests._oct27_seams import OCT27_SEAMS_DOWN
        assert OC_SEAMS_DOWN and set(OC_SEAMS_DOWN) <= set(OCT27_SEAMS_DOWN)

    def test_the_ladder_is_the_measure_order(self):
        from tests._oc_seams import OC_SEAMS_BY_ROW
        assert list(OC_SEAMS_BY_ROW) == ["LETTER", "ARREARS", "RESTLESS", "CURE",
                                         "STAFF", "SAVE", "USED", "CHEAP"]


# ═══════════════════ OC-1 the courts' purse ════════════════════════════════

class TestOC1TheCourtsPurse:

    def _prussia_after_the_staff_and_the_levy(self, world, monkeypatch):
        """Prussia at turn 20 with its Staff, the Krümper System and the
        Articles of War in force, every purse and budget gate passed: the
        rung's choice is the demand read's alone. (With the Staff standing
        the Articles — her cure — are used: a cure is bought with its Staff.)"""
        world.current_turn = 20
        _row(world, "Prussia", "general_staff")["enacted_turn"] = 2
        assert RF.law_is_used(world, "Prussia", _row(world, "Prussia", "articles_of_war"))
        for law_id in ("krumper_system", "articles_of_war"):
            _row(world, "Prussia", law_id)["enacted_turn"] = 2
        monkeypatch.setattr(RF, "ai_purse_refusal", lambda *a, **k: "")
        monkeypatch.setattr(RF, "law_refusal", lambda *a, **k: "")

    def test_grd15_a_law_buys_what_is_used(self, world, monkeypatch):
        """Prussia paid ~3,100 gold of upkeep by turn 40 for a drill law it
        never drilled under: the rung reads demand first. Never drilled, never
        recruited — nothing of the rest of its deck is bought; one drill
        completed with room for morale, and the Commission is."""
        assert _seam_up("backend.game_logic.reforms", "a_law_buys_what_is_used")
        self._prussia_after_the_staff_and_the_levy(world, monkeypatch)
        reorg = _row(world, "Prussia", "reorganisation_commission")
        assert RF.law_is_used(world, "Prussia", reorg) is False
        with _quiet():
            assert RF.find_ai_enactment(world, "Prussia", 50_000, 2) is None
        RF.note_law_used(world, "Prussia", "drill")
        assert reorg.get("used_from") == 20 and RF.law_is_used(world, "Prussia", reorg)
        with _quiet():
            assert RF.find_ai_enactment(world, "Prussia", 50_000, 2) == {
                "action": "enact_law", "target": "reorganisation_commission"}

    def test_grd15_down_is_deck_order(self, world, monkeypatch):
        self._prussia_after_the_staff_and_the_levy(world, monkeypatch)
        monkeypatch.setattr(RF, "a_law_buys_what_is_used", lambda: False)
        with _quiet():
            assert RF.find_ai_enactment(world, "Prussia", 50_000, 2) == {
                "action": "enact_law", "target": "reorganisation_commission"}

    def test_grd15_each_effect_reads_its_own_use(self, world):
        """A recruit of the arm marks the price and morale laws of that arm (a
        voided morale term marks only the price law); "all" reads any arm; a
        regen law is used while the pool stands under its cap; a cure while
        the Staff stands; the player's court records nothing."""
        art = _row(world, "Russia", "arakcheev_artillery")
        levy = _row(world, "Russia", "extraordinary_levy")
        RF.note_law_used(world, "Russia", "recruit", "infantry", False)
        assert art.get("used_from") is None
        assert levy.get("used_from") is not None, "the levy's price is used"
        jager = _row(world, "Austria", "jager_battalions")       # morale only
        gen = _row(world, "Austria", "generalissimus")           # price, all arms
        RF.note_law_used(world, "Austria", "recruit", "cavalry", True)
        assert gen.get("used_from") is not None and jager.get("used_from") is None
        RF.note_law_used(world, "Austria", "recruit", "infantry", False)
        assert jager.get("used_from") is None, "a voided morale term is no use"
        RF.note_law_used(world, "Austria", "recruit", "infantry", True)
        assert jager.get("used_from") is not None
        opol = _row(world, "Russia", "opolchenie")
        world.manpower_pools["Russia"]["infantry"] = WS.MAX_INFANTRY_POOL
        assert RF.law_is_used(world, "Russia", opol) is False
        world.manpower_pools["Russia"]["infantry"] = WS.MAX_INFANTRY_POOL - 1
        assert RF.law_is_used(world, "Russia", opol) is True
        train = _row(world, "France", "train_des_equipages")
        assert RF.law_is_used(world, "France", train) is False
        _row(world, "France", "grand_quartier_general")["enacted_turn"] = 1
        assert RF.law_is_used(world, "France", train) is True
        art_fr = _row(world, "France", "artillery_reserve")
        RF.note_law_used(world, world.player_nation, "recruit", "artillery", True)
        assert art_fr.get("used_from") is None, "the player's court records nothing"

    def test_grd15_a_scenario_authors_no_use(self):
        """A court's use of a law is its history: the validator refuses
        `used_from` in a scenario, as it refuses `enacted_turn`."""
        import copy
        import json
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        assert not [e for e in validate_scenario(copy.deepcopy(data)).errors if "used_from" in str(e)]
        data["reforms"]["Prussia"][3]["used_from"] = 2
        assert [e for e in validate_scenario(data).errors if "used_from" in str(e)]

    def test_grd37_the_staff_is_saved_for_without_the_upkeep_reserve(self, world, monkeypatch):
        """At war, a court saves for its Staff (the doctrine's cure) without
        the five-turns-of-upkeep reserve that made it unreachable after S14j."""
        assert _seam_up("backend.game_logic.reforms",
                        "the_staff_is_saved_for_without_the_upkeep_reserve")
        staff = next(r for r in RF.deck(world, "Russia") if RF.is_staff(r))
        assert world.get_nations_at_war_with("Russia"), "Russia boots at war with France"
        price = int(staff["price"])
        assert RF._purse_bar(world, "Russia", staff) == price + max(
            RF.AI_PURSE_RESERVE, LG.one_turn_of_upkeep(world, "Russia"))
        old = price + RF.AI_PURSE_RESERVE + RF.AI_PURSE_UPKEEP_TURNS * (
            RF.law_upkeep_bill(world, "Russia") + int(staff["upkeep"]))
        monkeypatch.setattr(RF, "the_staff_is_saved_for_without_the_upkeep_reserve", lambda: False)
        assert RF._purse_bar(world, "Russia", staff) == old
        monkeypatch.undo()
        # at peace the bar stands, and the player's own bar never moves
        prussia_staff = next(r for r in RF.deck(world, "Prussia") if RF.is_staff(r))
        assert not world.get_nations_at_war_with("Prussia")
        assert RF._purse_bar(world, "Prussia", prussia_staff) == int(prussia_staff["price"]) + \
            RF.AI_PURSE_RESERVE + RF.AI_PURSE_UPKEEP_TURNS * (
                RF.law_upkeep_bill(world, "Prussia") + int(prussia_staff["upkeep"]))
        fr_staff = next(r for r in RF.deck(world, "France") if RF.is_staff(r))
        assert world.get_nations_at_war_with(world.player_nation)
        assert RF._purse_bar(world, world.player_nation, fr_staff) > int(fr_staff["price"]) + RF.AI_PURSE_RESERVE

    def test_grd37_russia_buys_its_staff_at_the_new_bar(self, world, monkeypatch):
        """End to end (the review's T-b): at war, a chest past the new bar and
        under the old, the Staff within reach — Russia enacts its Staff (its
        cure); with the seam down the old bar refuses it."""
        staff = next(r for r in RF.deck(world, "Russia") if RF.is_staff(r))
        new_bar = RF._purse_bar(world, "Russia", staff)
        assert new_bar >= int(staff["price"]) + RF.AI_PURSE_RESERVE
        chest = new_bar + 200
        monkeypatch.setattr(LG, "_build_economy", lambda w, n, income_data=None, **k: {
            "net": 5000, "state_charges": 0, "ceiling": 40_000,
            "ceiling_state": LG.CEILING_BOUNDED, "upkeep": 1000, "laws": 0,
            "infrastructure": 0, "admiralty": 0, "rente_cost": 0, "bankruptcy_turns": 0})
        world.nation_gold["Russia"] = chest
        with _quiet():
            assert RF.find_ai_enactment(world, "Russia", chest, 2) == {
                "action": "enact_law", "target": staff["id"]}
        monkeypatch.setattr(RF, "the_staff_is_saved_for_without_the_upkeep_reserve", lambda: False)
        assert RF._purse_bar(world, "Russia", staff) > chest
        with _quiet():
            assert RF.find_ai_enactment(world, "Russia", chest, 2) is None

    def test_grd37_the_bar_keeps_a_turn_of_upkeep(self, world, monkeypatch):
        """The at-war bar keeps the flat reserve or one turn of upkeep,
        whichever an army makes the larger (GRD-21's every purchase)."""
        staff = next(r for r in RF.deck(world, "Russia") if RF.is_staff(r))
        price = int(staff["price"])
        monkeypatch.setattr(LG, "one_turn_of_upkeep", lambda w, n: 2_400)
        assert RF._purse_bar(world, "Russia", staff) == price + 2_400
        monkeypatch.setattr(LG, "one_turn_of_upkeep", lambda w, n: 600)
        assert RF._purse_bar(world, "Russia", staff) == price + RF.AI_PURSE_RESERVE

    def test_the_save_holds_only_within_the_horizon(self, world, monkeypatch):
        """The review's F1: a saving court holds its discretionary gold only
        while its chest would stand at the bar within the purse's five turns
        at this turn's forecast Net — never while it crawls toward a ceiling."""
        assert _seam_up("backend.ai.enemy_ai", "a_saving_court_holds_its_gold")
        staff = next(r for r in RF.deck(world, "Russia") if RF.is_staff(r))
        monkeypatch.setattr(RF, "ai_is_saving_for_the_staff", lambda w, n, t: staff)
        bar = RF._purse_bar(world, "Russia", staff)
        chest = bar - 4_000

        def _net(value):
            monkeypatch.setattr(LG, "_build_economy",
                                lambda w, n, income_data=None, **k: {"net": value})

        _net(800)
        assert EA.holds_for_the_staff(world, "Russia", chest) is True     # 4,000 ≤ 5 × 800
        _net(799)
        assert EA.holds_for_the_staff(world, "Russia", chest) is False
        _net(0)
        assert EA.holds_for_the_staff(world, "Russia", chest) is False
        _net(800)
        monkeypatch.setattr(EA, "a_saving_court_holds_its_gold", lambda: False)
        assert EA.holds_for_the_staff(world, "Russia", chest) is False
        monkeypatch.undo()
        assert EA.holds_for_the_staff(world, "Russia", 1_000) is False, "not saving: nothing held"

    def test_the_save_holds_the_discretionary_rungs(self, world, monkeypatch):
        """A court that holds builds nothing, commissions nobody and arms no
        corps; with nothing held the same board spends."""
        from backend.commands.executor import CommandExecutor
        monkeypatch.setattr(RF, "find_ai_enactment", lambda *a, **k: None)
        monkeypatch.setattr(AF, "find_ai_edict", lambda *a, **k: None)
        world.nation_gold["Austria"] = 60_000
        ai = EA.EnemyAI(CommandExecutor())
        discretionary = {"build", "repair", "recruit_marshal", "build_fleet", "recruit",
                         "grant_dotation", "grant_pension"}
        monkeypatch.setattr(EA, "holds_for_the_staff", lambda w, n, t: False)
        with _quiet():
            free = ai._pick_admin_action("Austria", world, admin_ap=2)
        assert free and free.get("action") in discretionary, free
        monkeypatch.setattr(EA, "holds_for_the_staff", lambda w, n, t: True)
        with _quiet():
            held = ai._pick_admin_action("Austria", world, admin_ap=2)
        assert held is None or held.get("action") not in discretionary - {"recruit"}, held

    def test_grd21_a_cheap_rung_keeps_a_turn_of_upkeep(self, world, monkeypatch):
        assert _seam_up("backend.ai.enemy_ai", "a_cheap_rung_keeps_a_turn_of_upkeep")
        kept = LG.one_turn_of_upkeep(world, "Austria")
        assert kept > 0
        assert EA.keeps_a_turn(world, "Austria", kept + 350, 350) is True
        assert EA.keeps_a_turn(world, "Austria", kept + 349, 350) is False
        assert EA.keeps_a_turn(world, "Austria", 349, 350) is False
        monkeypatch.setattr(EA, "a_cheap_rung_keeps_a_turn_of_upkeep", lambda: False)
        assert EA.keeps_a_turn(world, "Austria", 350, 350) is True, "down: the price alone"

    def test_grd21_the_turn_is_counted_unhalved(self, world):
        """The mercy halves a court's upkeep the turn after a deficit — the
        reserve counts the full bill, exactly when it matters most."""
        full = LG.one_turn_of_upkeep(world, "Austria")
        world.nation_bankruptcy_turns["Austria"] = 1
        assert abs(LG.one_turn_of_upkeep(world, "Austria") - full) <= 8

    def test_grd29_a_cure_is_never_stranded_by_an_edict(self, world, monkeypatch):
        """Britain at 45 after the Orders in Council: a 3-authority decree
        would leave 42 and strand the Militia Transfer (15): refused. The cure
        itself pays the plain floor; with the cure in force the reserve goes."""
        assert _seam_up("backend.game_logic.affairs", "a_cure_is_never_stranded_by_an_edict")
        assert AF.cure_reserve(world, "Britain") == 15
        ST.move(world, "Britain", 45 - ST.standing_of(world, "Britain"), "test")
        assert ST.standing_of(world, "Britain") == 45
        why = ST.ai_refusal(world, "Britain", 3)
        assert "strand the cure" in why
        assert ST.ai_refusal(world, "Britain", 15, buying_the_cure=True) == ""
        monkeypatch.setattr(AF, "a_cure_is_never_stranded_by_an_edict", lambda: False)
        assert ST.ai_refusal(world, "Britain", 3) == "", "down: the floor alone"
        monkeypatch.undo()
        _row(world, "Britain", "militia_transfer")["enacted_turn"] = 1
        assert AF.cure_reserve(world, "Britain") == 0
        assert ST.ai_refusal(world, "Britain", 3) == ""
        assert AF.cure_reserve(world, world.player_nation) == 0
        assert AF.cure_reserve(world, "Austria") == 0, "Austria's cure rides its gold Staff"

    def test_grd29_the_reserve_reads_the_cures_demand(self, world):
        """The review's F2: no hoard for a cure the law rung will not buy —
        Prussia's Articles of War keep nothing until Prussia recruits infantry
        whose morale the law would carry (or its Staff stands); Britain's
        Militia Transfer is used from the boot (her pool stands under its cap)."""
        assert AF.cure_reserve(world, "Prussia") == 0
        RF.note_law_used(world, "Prussia", "recruit", "infantry", False)
        assert AF.cure_reserve(world, "Prussia") == 0, "a voided morale term is no use"
        RF.note_law_used(world, "Prussia", "recruit", "infantry", True)
        assert AF.cure_reserve(world, "Prussia") == 15
        assert AF.cure_reserve(world, "Britain") == 15


# ═══════════════════ OC-2 the Emperor's purse ══════════════════════════════

def _trace(world, nation, pattern, turns):
    """Drive the real bankruptcy machine with scripted chests ('D' a deficit,
    'S' solvent); the turns on which the army deserts (the next turn's start)."""
    out = []
    for t in range(1, turns + 1):
        world.nation_gold[nation] = -1 if pattern[(t - 1) % len(pattern)] == "D" else 1
        world._update_bankruptcy(nation)
        if world.deserts_now(nation):
            out.append(t + 1)
    return out


class TestOC2TheEmperorsPurse:

    def test_grd20_a_deficit_every_third_turn_is_remembered(self, world):
        assert _seam_up("backend.models.world_state", "a_deficit_every_third_turn_is_remembered")
        assert _trace(world, "Austria", "DSS", 12)[:1] == [11], "D-S-S deserts inside twelve turns"

    def test_grd20_the_other_patterns(self, world):
        assert _trace(world, "Prussia", "DS", 8)[:1] == [6], "every other turn: the third deficit"
        assert _trace(world, "Russia", "D", 3) == [4], "three in a row: the third, as always"
        assert _trace(world, "Britain", "DSSS", 24) == [], "one in four is forgotten"

    def test_grd20_down_is_ea8(self, world, monkeypatch):
        monkeypatch.setattr(WS, "a_deficit_every_third_turn_is_remembered", lambda: False)
        assert _trace(world, "Austria", "DSS", 12) == []
        assert _trace(world, "Prussia", "DS", 8)[:1] == [8], "EA-8: the fourth deficit"

    def test_grd19_restlessness_is_priced_by_the_province(self, world, monkeypatch):
        assert _seam_up("backend.models.world_state", "restlessness_is_priced_by_the_province")
        assert [WS.restless_interior_rate(n) for n in (1, 2, 3, 4, 32)] == [75, 150, 225, 250, 250]
        assert WS.restless_interior_rate(1) != WS.restless_interior_rate(32)
        monkeypatch.setattr(WS, "restlessness_is_priced_by_the_province", lambda: False)
        assert WS.restless_interior_rate(1) == WS.restless_interior_rate(32) == 75

    def test_grd19_the_term_reads_the_count(self, world):
        """One restless province costs what the binary term cost; three cost
        three times it."""
        mine = list(world.get_nation_regions(world.player_nation))
        for name in mine:
            world.regions[name].stability = 100
        world.regions[mine[0]].stability = 30
        terms = {t["key"]: t for t in world.get_state_charges_rate(world.player_nation)["terms"]}
        assert terms["restless_interior"]["amount"] == 75
        for name in mine[1:3]:
            world.regions[name].stability = 30
        terms = {t["key"]: t for t in world.get_state_charges_rate(world.player_nation)["terms"]}
        assert terms["restless_interior"]["amount"] == 225
        assert len(terms["restless_interior"]["regions"]) == 3


# ═══════════════════ OC-3 the Strangulation's letter ══════════════════════

class TestOC3TheStrangulationsLetter:

    def _strangle(self, world, monkeypatch, closure=0.42, we=85):
        monkeypatch.setattr(NV, "closure_against", lambda w, target: closure)
        world.war_exhaustion["Britain"] = we

    def test_brit1_a_strangled_britain_writes_without_contact(self, world, monkeypatch):
        assert _seam_up("backend.game_logic.ai_diplomacy",
                        "a_strangled_britain_writes_without_contact")
        assert NV.trade_dominance_nation(world) == "Britain"
        self._strangle(world, monkeypatch)
        assert AD.strangled_without_contact(world, "Britain") is True
        assert AD.strangled_without_contact(world, "Austria") is False, "the trade power alone"

    def test_brit1_each_condition_holds_her(self, world, monkeypatch):
        self._strangle(world, monkeypatch, closure=0.39)
        assert AD.strangled_without_contact(world, "Britain") is False, "under the first tier"
        self._strangle(world, monkeypatch, we=80)
        assert AD.strangled_without_contact(world, "Britain") is False, "not past the line"
        self._strangle(world, monkeypatch)
        monkeypatch.setattr(AD, "a_strangled_britain_writes_without_contact", lambda: False)
        assert AD.strangled_without_contact(world, "Britain") is False, "down: the window binds"

    def test_brit1_the_letter_on_a_crafted_board(self, world, monkeypatch):
        """Strangled, untouched, seven deadlocked turns: Britain writes for an
        armistice; with the seam down the fifteen-turn window holds her."""
        from backend.game_logic import diplomacy as DP
        self._strangle(world, monkeypatch)
        key = world._make_diplo_key("Britain", world.player_nation)
        assert not DP.pair_has_fought(world, key)
        monkeypatch.setattr(AD, "_update_stalemate_counter", lambda *a, **k: 7)

        def _letter():
            with _quiet():
                got = AD.process_diplomatic_phase("Britain", world)
            return [p for p in (got if isinstance(got, list) else [got])
                    if isinstance(p, dict) and "armistice" in str(p.get("type") or p.get("proposal_type") or "")]

        assert _letter(), "a strangled Britain asks for an armistice"
        monkeypatch.setattr(AD, "a_strangled_britain_writes_without_contact", lambda: False)
        assert not _letter(), "the no-contact window holds her"

    def test_brit1_talleyrand_names_the_system(self, world, monkeypatch):
        """Her letter is read for what it is: the System, not a stalemate."""
        self._strangle(world, monkeypatch)
        monkeypatch.setattr(AD, "get_game_bucket", lambda n, w: "stalemate")
        with _quiet():
            letter = AD._make_proposal("Britain", "armistice", 2, {"type": "armistice_losing"}, world)
        assert letter["talleyrand_assessment"] == AD.TALLEYRAND_ASSESSMENTS[("armistice", "strangled")]
        assert "System" in letter["talleyrand_assessment"]
        monkeypatch.setattr(AD, "a_strangled_britain_writes_without_contact", lambda: False)
        with _quiet():
            letter = AD._make_proposal("Britain", "armistice", 2, {"type": "armistice_losing"}, world)
        assert letter["talleyrand_assessment"] == AD.TALLEYRAND_ASSESSMENTS[("armistice", "stalemate")]


# ═══════════════════ OC-4 golden rule 1 ════════════════════════════════════

class TestOC4GoldenRuleOne:

    def _murat(self):
        from backend.models.marshal import Marshal
        m = Marshal(name="Murat", location="Bavaria", strength=20000,
                    personality="aggressive", nation="France")
        m.cavalry = True
        m.recklessness = 3
        return m

    def test_grd34_terrain_scaled_recklessness_is_read_in_the_marshal(self):
        from backend.models.marshal import Marshal
        assert "terrain" in inspect.signature(Marshal.get_attack_modifier).parameters
        m = self._murat()
        assert m.is_reckless_cavalry and m._get_recklessness_attack_bonus() > 0
        base = m.get_attack_modifier(1.0, consume=False)
        assert m.get_attack_modifier(1.0, consume=False, terrain=None) == base
        assert m.get_attack_modifier(1.0, consume=False, terrain="open") == base
        r = m._get_recklessness_attack_bonus()
        for terrain, mult in (("plains", 1.2), ("forest", 0.5), ("mountains", 0.3)):
            assert m.recklessness_terrain_scale(terrain) == mult
            got = m.get_attack_modifier(1.0, consume=False, terrain=terrain)
            old = base * ((1.0 + r * mult) / (1.0 + r))      # the resolver's old two-step
            assert abs(got - old) <= 1e-12 * old, (terrain, got, old)

    def test_grd34_everyone_else_is_untouched(self):
        from backend.models.marshal import Marshal
        ney = Marshal(name="Ney", location="Bavaria", strength=20000,
                      personality="aggressive", nation="France")
        assert ney.recklessness_terrain_scale("mountains") == 1.0
        assert ney.get_attack_modifier(1.0, consume=False, terrain="mountains") == \
            ney.get_attack_modifier(1.0, consume=False)

    def test_grd34_the_resolver_rederives_nothing(self):
        src = (REPO / "backend/game_logic/combat.py").read_text(encoding="utf-8")
        assert "scaled_contribution" not in src and "TERRAIN_CAVALRY_EFFECTIVENESS" not in src
        report = (REPO / "backend/game_logic/battle_report.py").read_text(encoding="utf-8")
        assert "TERRAIN_CAVALRY_EFFECTIVENESS" not in report

    def test_grd34_the_coordination_magnitudes_live_on_the_marshal(self):
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.marshal import Marshal
        assert CombatExecutor._RELATIONSHIP_SCALING is Marshal.RELATIONSHIP_SCALING
        ce = CombatExecutor.__new__(CombatExecutor)
        assert ce._get_combined_arms_bonus(3) == Marshal.COMBINED_ARMS_BONUS[3] == (0.20, 0.10)
        assert ce._get_combined_arms_bonus(2) == (0.10, 0.05)
        assert ce._get_combined_arms_bonus(1) == (0.0, 0.0)
        src = (REPO / "backend/commands/combat_executor.py").read_text(encoding="utf-8")
        for literal in ("0.03 * scale", "0.05 * scale", "adj_count * 0.02",
                        "min(raw_atk, 0.25)", "min(raw_def, 0.20)"):
            assert literal not in src, literal


class TestTheMeasureOfRecord:
    """Row OC's one measure (`SYSTEMS_REFERENCE.md` §226.2; `tools/_oc_measure.py`,
    the chain run alone on a frozen copy of the final tree). Cumulative arms in
    the ladder order of `tests/_oc_seams.py`: arm 0 holds every OC seam down
    (the commit before, `9c5228a5`), each later arm lets one more row up, ALL is
    the shipped tree. The records are `tools/_oc_*_2026_11_18.json`."""

    STAMP = "2026_11_18"
    COMMANDED = ("CMD-H", "CMD-A", "CMD-M")

    @staticmethod
    def _load(name):
        import json
        path = REPO / "tools" / name
        assert path.is_file(), f"{name} is not on record"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_the_ladder_is_the_hold_list(self):
        from tests._oc_seams import OC_SEAMS_BY_ROW, OC_SEAMS_DOWN
        from tools import _oc_measure as M
        assert list(M.ROWS) == list(OC_SEAMS_BY_ROW)
        assert set(M.held("0")) == set(OC_SEAMS_DOWN) and M.held("ALL") == []

    @pytest.mark.parametrize("seed", ["jena", "marengo"])
    def test_arm_0_is_the_commit_before_on_every_key(self, seed):
        """OC-4 stands in arm 0 (it has no seam by design): golden rule 1's fold
        moved no key of the world on either seed in forty turns. LETTER moves
        nothing on the ambient probe either — no Britain there is strangled
        without contact."""
        probe = self._load(f"_oc_probe_{self.STAMP}.json")
        for arm in ("0", "LETTER"):
            cell = probe["arms"][arm][seed]
            assert cell["vs_head"] == {"identical": True} and cell["keys"] == {}, arm
            assert cell["keys_a_turn"] == 213
        for arm, cells in probe["arms"].items():
            assert cells[seed]["crashes"] == cells[seed]["head_crashes"] == 0, (arm, seed)
        assert list(probe["arms"]["ARREARS"][seed]["keys"]) == ["nation_pay_arrears"]

    def test_the_band_holds_on_the_shipped_tree(self):
        """The deploy gate's difficulty guard, 23–28: arm 0 reads BA-6's 28 / 27 / 28,
        the shipped tree 26 / 27 / 28; France's T40 chest inside S14j's 16–40k on
        both, the courts under S14j's ceilings."""
        from tools import _oc_measure as M
        band = self._load(f"_oc_band_{self.STAMP}.json")
        for arm, want in (("0", [28, 27, 28]), ("ALL", [26, 27, 28])):
            cells = band["arms"][arm]
            assert all(cells[n]["ok"] for n in self.COMMANDED)
            assert [cells[n]["provinces"] for n in self.COMMANDED] == want, arm
            assert set(cells["seams_held"]) == set(M.held(arm))
            for n in self.COMMANDED:
                chests = cells[n]["chests"]
                assert 16_000 <= chests["france"] <= 40_000, (arm, n, chests)
                assert chests["court_max"] <= 35_000 and chests["courts_total"] <= 200_000, (arm, n)

    def test_the_staff_arms_breach_is_on_record(self):
        """The guard written before the data read one breach, reported with its
        attribution (§226.2): with the Staff's lower bar up and the save's reach
        still down, CMD-M ends at 20 — a court reaches its Staff and spends the
        gold its army wanted; the next rung (SAVE, the review's sibling) puts it
        back at 28. Every other arm of the ladder reads inside 23–28."""
        band = self._load(f"_oc_band_{self.STAMP}.json")
        for arm, cells in band["arms"].items():
            got = [cells[n]["provinces"] for n in self.COMMANDED]
            if arm == "STAFF":
                assert got == [28, 27, 20], got
            else:
                assert all(23 <= g <= 28 for g in got), (arm, got)
        assert [band["arms"]["SAVE"][n]["provinces"] for n in self.COMMANDED] == [24, 27, 28]

    def test_the_days_sweep(self):
        """Arm 0 equals the day's sweep on the commit before, 72 cells of 72; arm
        ALL is a whole run (every cell ok)."""
        s0 = self._load(f"_oc_sweep_0_{self.STAMP}.json")
        assert s0["cells_moved_vs_commit_before"] == []
        sa = self._load(f"_oc_sweep_all_{self.STAMP}.json")
        assert sa["held"] == []
        for sweep in (s0, sa):
            assert len(sweep["seeds"]) == 8 and len(sweep["arms"]) == 9
            assert all(sweep["arms"][a][n]["ok"] for a in sweep["arms"] for n in sweep["seeds"])

    def test_off_the_served_road(self):
        """The ambient ten seeds and the AI-France harness: arm 0 is BA-6's final
        tree entry for entry; arm ALL keeps story classes 10 of 10 and no
        annexation outside aim on either surface."""
        sig0, sig6 = (self._load(f"_dy_signature_oc_0_{self.STAMP}.json"),
                      self._load("_dy_signature_ba6_all_2026_11_17.json"))
        assert {k: v for k, v in sig0.items() if k != "_note"} == {k: v for k, v in sig6.items() if k != "_note"}
        assert self._load(f"_oc_0_census_{self.STAMP}.json") == self._load("_ba6_all_census_2026_11_17.json")
        harness = self._load(f"_oc_chain_d_{self.STAMP}.json")
        assert harness["arms"]["0"] == self._load("_ba6_chain_d_2026_11_17.json")["arms"]["ALL"]
        assert self._load(f"_dy_signature_oc_all_{self.STAMP}.json")["story_class_count"] == 10
        assert self._load(f"_oc_all_census_{self.STAMP}.json")["totals"]["annexations_outside_aim"] == 0
        assert harness["totals"]["ALL"]["annexations_outside_aim"] == 0

    def test_oc1_the_courts_purse(self):
        """OC-1's done-whens on the purse probe (ten ambient seeds, forty turns):
        no law bought unused (GRD-15); a court the doctrines held from their Staff
        now reaches it (GRD-37 — Austria on four seeds, Russia on friedland); the
        Militia Transfer is never stranded (GRD-29: Britain's authority holds 45
        through turn 6); the turns any court spends under a turn of upkeep fall
        66 -> 17 — and Saxony still closes under one on marengo and rivoli, by war,
        the reading GRD-21's done-when asked for (§226.2)."""
        p0 = self._load(f"_oc_purse_0_{self.STAMP}.json")["summary"]
        pa = self._load(f"_oc_purse_all_{self.STAMP}.json")["summary"]
        assert p0["grd15_met"] is False and pa["grd15_met"] is True
        assert not any(pa["unused_laws_by_court"].values())
        assert p0["grd37_met_for_the_stuck_courts"] is False and pa["grd37_met_for_the_stuck_courts"] is True
        assert sorted(map(tuple, pa["stuck_courts_reaching_their_staff"])) == [
            ("eylau", "Austria"), ("friedland", "Austria"), ("friedland", "Russia"),
            ("jena", "Austria"), ("rivoli", "Austria")]
        assert all(v == [45] * 5 for v in pa["britain_authority_t1_t6"].values())
        assert all(v[-1] < 42 for v in p0["britain_authority_t1_t6"].values())
        closing = {s: v for s, v in pa["courts_under_a_turn_at_the_close"].items() if v}
        assert closing == {"marengo": ["Saxony"], "rivoli": ["Saxony"]}

        def _turns_under(arm):
            seeds = self._load(f"_oc_purse_{arm}_{self.STAMP}.json")["seeds"]
            return sum(int(v.get("turns_under_keep") or 0) for courts in seeds.values() for v in courts.values())
        assert (_turns_under("0"), _turns_under("all")) == (66, 17)

    def test_t8_is_re_read(self):
        """DOCTRINES_SPEC's T8 on the post-S14j economy: no rival cured before turn
        10 on either arm; by turn 30 on historical 0 of 4 -> 1 of 4 (Britain, her
        Staff at turn 8 and her cure at 14) — still short of the two the bar asks;
        the recorded miss."""
        t0 = self._load(f"_oc_t8_0_{self.STAMP}.json")["t8"]
        ta = self._load(f"_oc_t8_all_{self.STAMP}.json")["t8"]
        assert (t0["cured_by_30_on_historical"], ta["cured_by_30_on_historical"]) == (0, 1)
        assert t0["cured_before_10"] == ta["cured_before_10"] == []
        assert t0["pass"] is False and ta["pass"] is False

    def test_oc3_the_letter_on_the_shut_out_arm(self):
        """OC-3's done-when: on the benchmark's shut-out arm the contactless seed
        (SHUT-H) has Britain write for an armistice at turn 9 with LETTER up and
        never with it down; the seeds that meet a British corps are unmoved by the
        row alone. On the shipped tree every strangulation seed ends Britain's war
        without contact — NAV1-M by the league's common peace at turn 9."""
        sea = self._load(f"_oc_sea_{self.STAMP}.json")["arms"]
        assert sea["0"]["SHUT-H"]["first_armistice"] is None
        assert sea["0"]["SHUT-H"]["strangled_without_contact_turns"] == [8, 9, 10, 11, 12]
        for arm in ("LETTER", "ALL"):
            cell = sea[arm]["SHUT-H"]
            assert cell["first_armistice"] == 9 and cell["contact_by_the_first_armistice"] is False, arm
        for seed in ("SHUT-A", "SHUT-M", "NAV1-H", "NAV1-A", "NAV1-M"):
            assert sea["LETTER"][seed]["first_armistice"] == sea["0"][seed]["first_armistice"], seed
            assert sea["0"][seed]["contact_by_the_first_armistice"] is True, seed
        for seed in ("SHUT-A", "SHUT-M", "NAV1-H", "NAV1-A"):
            assert sea["ALL"][seed]["contact_by_the_first_armistice"] is False, seed
        m = sea["ALL"]["NAV1-M"]
        assert m["letters"] == [] and next(t["turn"] for t in m["turns"] if not t["at_war"]) == 9

    def test_the_deploy_gate(self):
        """The deploy gate per arm (`tools/_oc_gate_2026_11_18.json`). Clause 2 is
        read on thirty ambient seeds by the user's ruling of November 18 (§226.2,
        DYNAMISM_SPEC §7): on the ten the one promotion (marengo, Hesse at turn
        34) is re-timed by the rulings, and the twenty more promote at the same
        rate with the rules up as down — two campaigns in thirty either way."""
        gate = self._load(f"_oc_gate_{self.STAMP}.json")["arms"]
        wide = self._load(f"_oc_promotions_wide_{self.STAMP}.json")["arms"]
        g0, ga = gate["0"], gate["ALL"]
        assert g0["met"] is True and g0["met_on_thirty"] is True
        assert g0["promotions"] == {"marengo": [[34, "Hesse"]]}
        assert ga["met_on_thirty"] is True
        assert ga["story_classes"] == 10 and ga["roster_readings"] >= 2
        assert ga["annexations_outside_aim"] == 0
        assert ga["promotions"] == {} and ga["met"] is False
        assert ga["promotions_on_the_twenty"] == wide["ALL"]["seeds_promoting"] == ["aspern", "borodino"]
        assert g0["promotions_on_the_twenty"] == wide["0"]["seeds_promoting"] == ["borodino"]
        assert wide["ALL"]["seeds"]["aspern"] == [[21, "Bavaria"]]
        assert wide["ALL"]["seeds"]["borodino"] == [[30, "Denmark"]] and wide["0"]["seeds"]["borodino"] == [[31, "Denmark"]]
        on_thirty = {arm: len(gate[arm]["promotions"]) + len(wide[arm]["seeds_promoting"]) for arm in ("0", "ALL")}
        assert on_thirty == {"0": 2, "ALL": 2}, on_thirty


class TestTheHooksOwnFind:
    """OC-X3 (row OC's first hook run, November 18, 2026): the client
    instrument's rail refused with no second window open — a sibling lane's
    headless engine starting or exiting shows a blank command line and the
    rail fails closed on it. The count is re-read before it refuses."""

    @staticmethod
    def _start(monkeypatch, tmp_path, counts):
        sys.path.insert(0, str(REPO / "tools"))
        import dd_b_play as P
        reads = iter(counts)
        monkeypatch.setattr(P, "_godot_running", lambda windowed_only=False: next(reads))
        monkeypatch.setattr(P.time, "sleep", lambda s: None)

        class _PastTheRail(Exception):
            pass

        def _engine(arg):
            raise _PastTheRail()
        monkeypatch.setattr(P, "_engine_path", _engine)
        args = type("A", (), {"out": str(tmp_path / "run"), "beside_headless": True,
                              "godot": None, "port": None})()
        return P, _PastTheRail, args

    def test_a_passing_engine_is_not_a_second_window(self, monkeypatch, tmp_path):
        P, past, args = self._start(monkeypatch, tmp_path, [1, 0])
        with pytest.raises(past):
            P.cmd_start(args)

    def test_a_second_engine_that_stays_is_refused(self, monkeypatch, tmp_path):
        P, past, args = self._start(monkeypatch, tmp_path, [1, 1, 1, 1])
        with pytest.raises(SystemExit, match="never two engines at once"):
            P.cmd_start(args)

    @staticmethod
    def _stays(monkeypatch, counts):
        """OC-X5: the client pins' own gate re-reads a window before it skips."""
        from tests import test_dd_b_the_client_hands as H
        reads = iter(counts)
        monkeypatch.setattr(H.P, "_godot_running", lambda windowed_only=False: next(reads))
        monkeypatch.setattr(H.time, "sleep", lambda s: None)
        return H._a_window_stays()

    def test_the_client_pins_do_not_skip_on_a_passing_engine(self, monkeypatch):
        assert self._stays(monkeypatch, [0]) is False
        assert self._stays(monkeypatch, [1, 0]) is False

    def test_the_client_pins_skip_on_a_window_that_stays(self, monkeypatch):
        assert self._stays(monkeypatch, [1, 1, 1]) is True


class TestSessionHsHead:

    def test_grd16_a_marshal_typo_is_offered_the_nearest_own_name(self):
        """BUILT November 18, 2026 (row PW part 2 — the typed road): the strict-xfail turned red the day
        the seam landed, as it said it would, and is re-seated as a pass. Its behaviour:
        `tests/test_pw2_the_typed_road.py::TestGRD16TheNearestOfYourOwnMarshals`."""
        assert _seam_up("backend.commands.executor", "a_marshal_typo_is_offered_the_nearest_own_name")

    @pytest.mark.xfail(strict=True, reason=_H)
    def test_grd33_the_literal_buff_expires_with_the_turn(self):
        assert _seam_up("backend.commands.meta_executor", "the_literal_buff_expires_with_the_turn")
