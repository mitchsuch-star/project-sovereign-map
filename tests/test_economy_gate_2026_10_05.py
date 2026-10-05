"""The economy gate (October 5, 2026) — the economy audit's open list ruled
and built under the user's delegation ("fix and decide on these"). Gate record
`docs/SCORE_FINISH_SPEC.md` §6.8; memo `docs/audits/ECONOMY_GATE_2026_10_05.md`;
rules `docs/SYSTEMS_REFERENCE.md` §98.

Every behaviour change sits behind its own lever; each class drives the real
code with the lever up and, where the row names what the shipped tree did,
with it down. The BASELINE_SERIES attribution is
`tools/_econ_gate_series_arms.py` (record `tools/_econ_gate_series_arms_final.json`).
"""
import contextlib
import io
from pathlib import Path

import pytest

from backend.ai import enemy_ai as EA
from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic import coalition as CO
from backend.game_logic import diplomacy as DP
from backend.game_logic import dispatch as DS
from backend.game_logic import ledger as LG
from backend.game_logic import reforms as RF
from backend.game_logic import war_council as WC
from backend.models import world_state as WS
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


def _truce(world, a="France", b="Austria", cooldown=4, relation=-77):
    with _quiet():
        DP.set_diplomatic_state(world, a, b, "ARMISTICE", "test")
    key = world._make_diplo_key(a, b)
    world.armistice_cooldowns[key] = cooldown
    world.nation_relations[key] = relation
    world._league_forecast_cache = None
    return key


# ═════════════════════ EA-19 the truce binds the league ═════════════════════
class TestATruceBindsTheLeague:
    def test_a_truce_partner_does_not_qualify(self):
        w = _boot()
        _truce(w)
        assert CO.qualifies_for_coalition("Austria", w) is False

    def test_lever_down_the_gate_reads_only_war(self, monkeypatch):
        monkeypatch.setattr(CO, "A_TRUCE_BINDS_THE_LEAGUE", False)
        w = _boot()
        _truce(w)
        assert CO.qualifies_for_coalition("Austria", w) is True

    def test_the_forecast_files_her_as_held_by_the_truce(self):
        w = _boot()
        _truce(w)
        forecast = CO.league_forecast(w)
        row = next(r for r in forecast["courts"] if r["nation"] == "Austria")
        assert row["status"] == CO.LEAGUE_TRUCE
        assert row["bound_turns"] == 4
        assert "Austria" not in forecast["joiners"]
        text = CO.league_row_text(w, row, forecast)
        assert "our truce binds her 4 more turns" in text
        assert "cannot declare on us while it holds" in text

    def test_lever_down_the_forecast_names_her_a_joiner(self, monkeypatch):
        monkeypatch.setattr(CO, "A_TRUCE_BINDS_THE_LEAGUE", False)
        w = _boot()
        _truce(w)
        forecast = CO.league_forecast(w)
        row = next(r for r in forecast["courts"] if r["nation"] == "Austria")
        assert row["status"] == CO.LEAGUE_JOINS

    def test_one_cooldown_is_read_by_every_war_entry_gate(self):
        w = _boot()
        _truce(w)
        assert DP.declaration_cooldown_left(w, "Austria", "France") == 4
        with _quiet():
            refused = DP.declare_war(w, "Austria", "France")
        assert refused["success"] is False and "4 turns remaining" in refused["message"]
        assert "a truce's cooldown binds it" in DP.offensive_call_bar(w, "Austria", "France")
        assert WC.can_declare_war(w, "Austria", "France")["reason"] == "armistice_cooldown"

    def test_the_forecast_cache_reads_the_cooldown(self):
        w = _boot()
        key = _truce(w, cooldown=3)
        first = CO.league_forecast(w)
        w.armistice_cooldowns[key] = 0   # the truce's floor spent, same turn
        second = CO.league_forecast(w)
        a1 = next(r for r in first["courts"] if r["nation"] == "Austria")["status"]
        a2 = next(r for r in second["courts"] if r["nation"] == "Austria")["status"]
        assert a1 == CO.LEAGUE_TRUCE and a2 != CO.LEAGUE_TRUCE


class TestAStandingLeagueIsNotReopened:
    """The boot coalition stands; a court newly free to join (the Ottoman) is
    the NEXT league's — never "She will march" into this one."""

    def _ottoman_detail(self, w):
        forecast = CO.league_forecast(w)
        row = next(r for r in forecast["courts"] if r["nation"] == "Ottoman")
        assert forecast["formed"] and row["status"] == CO.LEAGUE_JOINS
        return CO.league_row_detail(w, row, forecast)

    def test_the_line_names_the_next_league(self):
        detail = self._ottoman_detail(_boot())
        assert "A league stands declared without her; she would march in the next" in detail
        assert "She will march" not in detail

    def test_lever_down_she_will_march(self, monkeypatch):
        monkeypatch.setattr(CO, "A_STANDING_LEAGUE_IS_NOT_REOPENED", False)
        detail = self._ottoman_detail(_boot())
        assert "She will march" in detail


class TestALeagueNeedsTwoMembers:
    def _form_with_one_failure(self, w):
        real = DP.declare_war

        def _declare(world, aggressor, target, *a, **kw):
            if aggressor == "Russia":
                return {"success": False, "message": "refused for the test"}
            return real(world, aggressor, target, *a, **kw)
        return _declare

    def test_a_league_of_one_is_no_league(self, monkeypatch):
        w = _boot()
        w.active_coalition = None
        assert not CO.get_nations_at_war_with_target(w, "Prussia")
        monkeypatch.setattr(DP, "declare_war", self._form_with_one_failure(w))
        with _quiet():
            out = CO.form_coalition(["Austria", "Russia"], w, target="Prussia")
        assert out["success"] is False and "declarations failed" in out["message"]
        assert w.active_coalition is None

    def test_lever_down_a_league_of_one_forms(self, monkeypatch):
        monkeypatch.setattr(CO, "A_LEAGUE_NEEDS_TWO_MEMBERS", False)
        w = _boot()
        w.active_coalition = None
        monkeypatch.setattr(DP, "declare_war", self._form_with_one_failure(w))
        with _quiet():
            out = CO.form_coalition(["Austria", "Russia"], w, target="Prussia")
        assert out["success"] is True
        assert w.active_coalition["members"] == ["Austria"]


# ═════════════════════ EAD-7 the march finds its road ═════════════════════
def _deroy_board():
    """Deroy (Bavaria) at Franconia, an Austrian corps at Moravia: the one
    straight hop (Dresden) is closed Saxon soil; the lawful road runs
    Franconia → Bohemia → Vienna → Moravia."""
    w = _boot()
    john = w.marshals["ArchdukeJohn"]
    john.location = "Moravia"
    ai = EnemyAI(None)
    ai._get_enemy_contacts = lambda nation, world, marshal=None: [john]
    ai._get_effective_personality = lambda m, world: "aggressive"
    ai._marshal_visited_locations = {}
    ai._should_maintain_co_location = lambda *a, **k: False
    return w, ai, w.marshals["Deroy"]


class TestTheMarchFindsItsRoad:
    def test_the_lawful_distance_skips_closed_soil(self):
        w = _boot()
        law = EA.lawful_distances_to(w, "Bavaria", "Moravia", "Franconia")
        assert w.get_distance("Franconia", "Moravia") == 2
        assert law["Franconia"] == 3
        assert law["Bohemia"] == 2
        assert w.find_path("Franconia", "Moravia", passable_for="Bavaria") == [
            "Franconia", "Bohemia", "Vienna", "Moravia"]

    def test_a_corps_walks_around_a_closed_neutral(self):
        w, ai, deroy = _deroy_board()
        with _quiet():
            order = ai._consider_strategic_move(deroy, "Bavaria", w)
        assert order == {"marshal": "Deroy", "action": "move", "target": "Bohemia"}

    def test_lever_down_the_corps_stands_still(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_MARCH_READS_THE_LAWFUL_ROAD", False)
        w, ai, deroy = _deroy_board()
        with _quiet():
            assert ai._consider_strategic_move(deroy, "Bavaria", w) is None

    def test_a_straight_hop_that_is_open_is_kept(self):
        """The lawful road is the second pass: a march that already found
        its hop finds the same one (the plan's first metric is straight)."""
        w, ai, deroy = _deroy_board()
        plan = ai._march_plan(w, "Bavaria", deroy, "Moravia")
        assert len(plan) == 2
        assert plan[0]("Bohemia") == w.get_distance("Bohemia", "Moravia")
        assert plan[1]("Bohemia") == 2

    def test_no_lawful_road_keeps_the_straight_reading(self):
        w = _boot()
        # Russia has no lawful road to Paris at boot (Prussia and Hesse are
        # closed to her) — the plan is the straight distance alone.
        ai = EnemyAI(None)
        kutuzov = w.marshals["Kutuzov"]
        plan = ai._march_plan(w, "Russia", kutuzov, "Paris")
        assert len(plan) == 1


class TestTheLeagueAimsAtItsEnemy:
    def test_a_fellow_member_is_never_a_target(self):
        w = _boot()
        w.active_coalition["members"] = ["Austria", "Britain", "Russia", "Sweden"]
        assert EA.league_fellows(w, "Britain") == frozenset({"Austria", "Russia", "Sweden"})
        assert EA.league_fellows(w, "Prussia") == frozenset()

    def test_lever_down_no_fellows(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_LEAGUE_AIMS_AT_ITS_ENEMY", False)
        w = _boot()
        assert EA.league_fellows(w, "Britain") == frozenset()

    def _aims(self, w, ai, marshal, nation):
        aimed = []
        real = ai._march_plan

        def _spy(world, n, m, target_region):
            aimed.append(target_region)
            return real(world, n, m, target_region)
        ai._march_plan = _spy
        with _quiet():
            ai._consider_strategic_move(marshal, nation, w)
        return aimed

    def test_the_march_never_aims_at_a_fellow_members_corps(self):
        w, ai, _deroy = _deroy_board()
        armfelt = w.marshals["Armfelt"]          # Sweden, at Stralsund
        moore = w.marshals["Moore"]              # a British corps
        w.active_coalition["members"] = ["Austria", "Britain", "Russia", "Sweden"]
        ai._get_enemy_contacts = lambda nation, world, marshal=None: [armfelt]
        assert armfelt.location not in self._aims(w, ai, moore, "Britain")

    def test_lever_down_the_march_aims_at_him(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_LEAGUE_AIMS_AT_ITS_ENEMY", False)
        w, ai, _deroy = _deroy_board()
        armfelt = w.marshals["Armfelt"]
        moore = w.marshals["Moore"]
        w.active_coalition["members"] = ["Austria", "Britain", "Russia", "Sweden"]
        ai._get_enemy_contacts = lambda nation, world, marshal=None: [armfelt]
        assert self._aims(w, ai, moore, "Britain") == [armfelt.location]


# ═════════════════════ EAD-8 the league's silent courts ═════════════════════
class TestTheLeaguesSilentCourts:
    def test_the_boot_league_says_who_has_not_struck_and_why(self):
        reading = CO.league_march_reading(_boot())
        assert reading["formed"] is True
        reasons = {r["nation"]: r["reason"] for r in reading["silent"]}
        assert reasons == {"Austria": "open", "Britain": "landing", "Russia": "closed"}
        texts = {r["nation"]: r["text"] for r in reading["silent"]}
        assert "Normandy is a defended shore" in texts["Britain"]
        assert "15,000 men at a time" in texts["Britain"]
        assert "the neutrality of Prussia and Hesse bars it" in texts["Russia"]

    def test_the_reading_names_no_corps(self):
        """Fog: public facts only — no marshal's name or strength."""
        w = _boot()
        reading = CO.league_march_reading(w)
        blob = " ".join(r["text"] for r in reading["silent"])
        for m in w.marshals.values():
            if m.nation != "France":
                assert m.name not in blob

    def test_a_court_that_struck_us_has_marched(self):
        w = _boot()
        w.log_event({"type": "battle", "attacker_nation": "Austria",
                     "defender_nation": "France", "attacker": "Mack",
                     "defender": "Ney"})
        reading = CO.league_march_reading(w)
        assert "Austria" in reading["marched"]
        assert "Austria" not in {r["nation"] for r in reading["silent"]}

    def test_the_coalition_section_carries_the_rows(self):
        w = _boot()
        with _quiet():
            section = DS._build_coalition_section(w, "France")
        rows = section["active_coalition"].get("unmarched") or []
        assert {r["nation"] for r in rows} == {"Austria", "Britain", "Russia"}

    def test_the_beat_fires_when_the_reasons_change(self):
        w = _boot()
        added = []
        w.headline_lead_memory = {"league": {"joiners": [], "bound": [], "march": "x:y"}}
        DS._league_candidates(w, "France", [], lambda cls, **kw: added.append((cls, kw)),
                              record=True)
        beats = [kw for cls, kw in added if cls == "league_unmarched"]
        assert len(beats) == 1
        assert beats[0]["line"].startswith("not every court of the league has struck us.")
        # the same reasons the next morning: silence
        added.clear()
        DS._league_candidates(w, "France", [], lambda cls, **kw: added.append((cls, kw)),
                              record=True)
        assert not [kw for cls, kw in added if cls == "league_unmarched"]

    def test_lever_down_silence(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_LEAGUE_SAYS_WHO_HAS_NOT_MARCHED", False)
        assert CO.league_march_reading(_boot())["silent"] == []

    def test_the_class_is_registered_everywhere(self):
        assert DS.HEADLINE_WEIGHTS["league_unmarched"] < DS.HEADLINE_WEIGHTS["league_bound"]
        assert "league_unmarched" in DS._LEAGUE_CLASSES


# ═════════════════════ EAD-1 campaign pay ═════════════════════
class TestCampaignPay:
    def test_a_corps_on_allied_soil_at_war_pays(self):
        up = _boot().calculate_turn_upkeep("France")
        assert up["campaign_pay"] == (17000 // 1000) * WS.CAMPAIGN_PAY_RATE == 204
        assert up["campaign_ground"] == [
            {"marshal": "Bernadotte", "region": "Franconia", "holder": "Bavaria", "pay": 204}]
        assert up["total"] == up["base"] + up["surcharge"]

    def test_a_satellites_soil_feeds_the_corps(self):
        w = _boot()
        assert w.marshals["Massena"].location == "Milan"
        ground = {g["marshal"] for g in w.calculate_turn_upkeep("France")["campaign_ground"]}
        assert "Massena" not in ground

    def test_enemy_soil_and_home_soil_pay_nothing(self):
        w = _boot()
        w.marshals["Bernadotte"].location = "Vienna"     # enemy (Austria)
        assert w.calculate_turn_upkeep("France")["campaign_pay"] == 0
        w.marshals["Bernadotte"].location = "Lorraine"   # home
        assert w.calculate_turn_upkeep("France")["campaign_pay"] == 0

    def test_the_courts_own_1805_soil_never_pays(self):
        """A homeland province an ally happens to hold is still home."""
        w = _boot()
        w.regions["Lorraine"].controller = "Bavaria"
        w.marshals["Bernadotte"].location = "Lorraine"
        w.invalidate_active_nations_cache()
        ground = {g["marshal"] for g in w.calculate_turn_upkeep("France")["campaign_ground"]}
        assert "Bernadotte" not in ground

    def test_at_peace_no_campaign_pay(self):
        w = _boot()
        for enemy in list(w.get_nations_at_war_with("France")):
            with _quiet():
                DP.set_diplomatic_state(w, "France", enemy, "PEACE", "test")
        w.invalidate_active_nations_cache()
        assert w.calculate_turn_upkeep("France")["campaign_pay"] == 0

    def test_the_mercy_halves_it(self):
        w = _boot()
        w.nation_bankruptcy_turns["France"] = 1
        up = w.calculate_turn_upkeep("France")
        assert up["campaign_pay"] == 102
        assert up["total"] == up["base"] + up["surcharge"]

    def test_lever_down_no_campaign_pay(self, monkeypatch):
        monkeypatch.setattr(WS, "CAMPAIGN_PAY_ON_FOREIGN_SOIL", False)
        assert _boot().calculate_turn_upkeep("France")["campaign_pay"] == 0

    def test_the_ledger_and_the_report_name_it(self):
        w = _boot()
        with _quiet():
            econ = LG._build_economy(w, "France")
        assert econ["campaign_pay"] == 204
        assert econ["campaign_ground"][0]["holder"] == "Bavaria"
        executor = CommandExecutor()
        with _quiet():
            out = executor.execute({"command": {"action": "economy", "type": "general"}},
                                   {"world": w})
        text = str(out.get("message", ""))
        assert "Campaign pay (fed by contract on allied or neutral soil: Bernadotte at Franconia): -204g" in text
        # the over-limit line is the over-limit band alone (surcharge less
        # the Grande Armée premium and the campaign pay)
        up = w.calculate_turn_upkeep("France")
        over = up["surcharge"] - up["grande_armee"] - up["campaign_pay"]
        assert f"-{over}g surcharge" in text

    def test_the_desk_names_it_apart_from_the_over_limit(self):
        from backend.ai.state_desk import _answer_upkeep
        w = _boot()
        with _quiet():
            line = _answer_upkeep(w)
        assert "204 campaign pay for corps fed by contract" in line
        up = w.calculate_turn_upkeep("France")
        over = up["surcharge"] - up["grande_armee"] - up["campaign_pay"]
        assert f"{over:,} over-limit surcharge" in line

    def test_the_end_turn_banner_names_it(self):
        w = _boot()
        executor = CommandExecutor()
        with _quiet():
            out = executor.execute({"command": {"action": "end_turn", "type": "general"}},
                                   {"world": w})
        assert "campaign pay)" in str(out.get("message", "")) or \
            "g campaign pay" in str(out.get("message", ""))


# ═════════════════════ EAD-2 the Charges name their price ═════════════════════
def _rich_france(chest=30000):
    w = _boot()
    w.nation_gold["France"] = chest
    return w


class TestTheChargesNameTheirPrice:
    def test_the_relief_is_the_formula_at_two_chests(self):
        w = _rich_france()
        rate = w.get_state_charges_rate("France", projected=True)["rate"]

        def charge(gold):
            return (gold - WS.CHARGES_HOARD_FLOOR) * rate // WS.WAR_EFFORT_DIVISOR
        assert w.charges_relief("France", 1000) == charge(30000) - charge(29000) > 0

    def test_the_ledger_names_the_relief(self):
        w = _rich_france()
        with _quiet():
            econ = LG._build_economy(w, "France")
        relief = w.charges_relief("France", 1000)
        assert econ["charges_relief_per_1000"] == relief
        assert f"every 1,000g spent from it cuts next turn's draw by {relief:,}g" in \
            econ["state_charges_rate_note"]

    def test_the_counsel_says_what_the_law_takes_off_the_draw(self):
        from backend.ai.counsel import _law_terms
        w = _rich_france(20000)
        line = _law_terms(w, "France")
        assert line and line.startswith("enact the Staff")
        assert "the Charges of Empire fall by" in line

    def test_the_desk_says_what_an_idle_chest_pays(self):
        from backend.ai.state_desk import _answer_spend
        w = _rich_france()
        with _quiet():
            answer = _answer_spend(w)
        assert "The Charges of Empire take" in answer and "every 1,000 spent cuts that by" in answer

    def test_a_political_law_names_the_grip_it_spends(self):
        w = _rich_france()
        w.authority_tracker.authority = 80
        row = RF.find_law(w, "France", "anticipated_class")
        terms = RF.terms_line(w, "France", row)
        assert "the Emperor's grip falls under 70" in terms
        assert "Charges of Empire rise by 50 rate points" in terms

    def test_no_clause_when_the_grip_holds(self):
        w = _rich_france()
        w.authority_tracker.authority = 100
        row = RF.find_law(w, "France", "anticipated_class")
        assert "grip" not in RF.terms_line(w, "France", row)

    def test_lever_down_silence(self, monkeypatch):
        monkeypatch.setattr(LG, "THE_CHARGES_NAME_THEIR_PRICE", False)
        w = _rich_france()
        w.authority_tracker.authority = 80
        row = RF.find_law(w, "France", "anticipated_class")
        assert "grip" not in RF.terms_line(w, "France", row)
        with _quiet():
            assert "cuts next turn's draw" not in LG._build_economy(w, "France")["state_charges_rate_note"]


# ═════════════════════ EAD-4 a third of Europe's men ═════════════════════
def _france_at_share(world, share):
    totals = CO._standing_strength_by_nation(world)
    others = sum(v for k, v in totals.items() if k != "France")
    target = int(share * others / (1 - share))
    french = [m for m in world.marshals.values() if m.nation == "France" and m.strength > 0]
    each = target // len(french)
    for m in french:
        m.strength = each


class TestAThirdOfEuropesMen:
    def test_the_line_is_a_third(self):
        assert CO.establishment_line() == pytest.approx(1 / 3)

    def test_lever_down_the_blessed_040(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_ARMY_LINE_IS_A_THIRD", False)
        assert CO.establishment_line() == 0.40

    def test_an_army_above_a_third_alarms_europe(self):
        w = _boot()
        _france_at_share(w, 0.36)
        before = int(w.threat_by_target.get("France", 0))
        CO._establishment_threat(w, "France")
        assert int(w.threat_by_target.get("France", 0)) == min(100, before + 1)

    def test_lever_down_the_same_army_does_not(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_ARMY_LINE_IS_A_THIRD", False)
        w = _boot()
        _france_at_share(w, 0.36)
        before = int(w.threat_by_target.get("France", 0))
        CO._establishment_threat(w, "France")
        assert int(w.threat_by_target.get("France", 0)) == before

    def test_no_court_accrues_at_boot(self):
        w = _boot()
        totals = CO._standing_strength_by_nation(w)
        europe = sum(totals.values())
        assert max(totals.values()) / europe < CO.establishment_line()


# ═════════════════════ EA-7's recovery path ═════════════════════
def _austria_without_a_general(gold=20000):
    w = _boot()
    for m in w.marshals.values():
        if m.nation == "Austria":
            m.strength = 0
    w.nation_gold["Austria"] = gold
    return w


class TestACourtWithoutAGeneralMayCommission:
    def test_she_commissions_through_the_shared_executor(self):
        w = _austria_without_a_general()
        ai = EnemyAI(CommandExecutor())
        with _quiet():
            out = ai.execute_commission_only("Austria", w, {"world": w})
        assert len(out) == 1 and out[0]["success"]
        assert w.marshals["Schwarzenberg"].nation == "Austria"

    def test_lever_down_nothing(self, monkeypatch):
        monkeypatch.setattr(EA, "A_COURT_WITHOUT_A_GENERAL_MAY_COMMISSION", False)
        w = _austria_without_a_general()
        ai = EnemyAI(CommandExecutor())
        with _quiet():
            assert ai.execute_commission_only("Austria", w, {"world": w}) == []

    def test_a_court_with_no_bench_stays_inert(self):
        w = _boot()
        w.nation_gold["Portugal"] = 50000
        ai = EnemyAI(CommandExecutor())
        with _quiet():
            assert ai.execute_commission_only("Portugal", w, {"world": w}) == []

    def test_the_enemy_turn_runs_the_rung_for_her(self):
        from backend.game_logic.turn_manager import TurnManager
        w = _austria_without_a_general()
        tm = TurnManager(w)
        with _quiet():
            results = tm._process_enemy_turns({"world": w})
        assert "Schwarzenberg" in w.marshals
        assert results["nations"]["Austria"]["admin_actions"] == 1


# ═════════════════════ EA-E8 the instrument talks to no live port ═════════════════════
class TestTheInstrumentTalksToNoLivePort:
    def test_every_child_reads_the_instruments_port(self, tmp_path):
        import tools.score_run as SR
        env = SR._env(tmp_path)
        assert env["SOVEREIGN_PORT"] == SR.INSTRUMENT_PORT != "8005"

    def test_the_formables_entry_row_renders_its_payload(self):
        import tools.iq10_run_captures as IQ
        row = next(r for r in IQ.SHOTS if r["id"] == "wizard_formables_entry")
        assert row["method"] != "open"
        assert any(step.get("call") == "_render_nations" for step in row["steps"])


# ═════════════════════ EG-X1 the order's target by name ═════════════════════
def _pursuing(world, marshal="Davout", target="ArchdukeCharles"):
    from backend.models.marshal import StrategicOrder
    m = world.marshals[marshal]
    m.strategic_order = StrategicOrder(
        command_type="PURSUE", target=target, target_type="marshal",
        started_turn=int(world.current_turn), original_command="pursue Archduke Charles")
    return m


class TestTheOrderNamesItsTarget:
    """EG-X1 (found by NPC-12's driven name census once the lawful road first
    sent a French marshal after Archduke Charles): an order's target is the
    resolved key, and six surfaces printed it raw."""

    def test_the_one_display_form(self):
        from backend.display_names import order_target_display
        assert order_target_display("ArchdukeCharles") == "Archduke Charles"
        assert order_target_display("Franche-Comte") == "Franche-Comte"
        assert order_target_display("") == ""

    def test_the_ledger_order_line(self):
        w = _boot()
        m = _pursuing(w)
        line = LG._derive_strategic_order_summary(m, int(w.current_turn))
        assert "Archduke Charles" in line and "ArchdukeCharles" not in line, line

    def test_the_dispatch_status_note(self):
        w = _boot()
        m = _pursuing(w)
        _status, note = DS._derive_marshal_status(m, w)
        assert "Pursuing Archduke Charles" in note and "ArchdukeCharles" not in note, note

    def test_the_campaign_log_order_line(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "strategic_order", "marshal": "Davout",
                                      "order_type": "PURSUE", "destination": "ArchdukeCharles"})
        assert line == "Davout ordered to pursue Archduke Charles", line

    def test_every_march_report_names_the_target(self):
        """Census: no player-facing f-string in the march reports prints the
        raw `order.target` (the console debug print is exempt)."""
        import re
        for rel in ("backend/commands/strategic.py", "backend/commands/relay.py",
                    "backend/game_logic/marshal_voice.py"):
            for n, ln in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"\{order\.target\}", ln) and "print(" not in ln:
                    raise AssertionError(f"{rel}:{n} prints the raw order target: {ln.strip()}")

    def test_lever_down_the_raw_key(self, monkeypatch):
        from backend import display_names as DN
        monkeypatch.setattr(DN, "THE_ORDER_NAMES_ITS_TARGET", False)
        w = _boot()
        m = _pursuing(w)
        assert "ArchdukeCharles" in LG._derive_strategic_order_summary(m, int(w.current_turn))


# ═════════════════════ EG-X2 the league's news rides beneath ═════════════════════
def _cand(cls, text, weight=None, identity=None):
    return {"class": cls, "text": text, "identity": identity or text,
            "weight": int(DS.HEADLINE_WEIGHTS[cls] if weight is None else weight)}


class TestTheLeaguesNewsRidesBeneath:
    """EG-X2: on the gate's CMD-M arm a war ending and a truce signed took both
    sub-beat slots and "St Petersburg now pays Vienna 400 gold a turn against
    us" left the page on the morning it was fresh."""

    def _crowded(self):
        return [
            _cand("enemy_on_our_soil", "Sire — the enemy has stood on our ground 5 turns."),
            _cand("road_home", "Sire — the war with Austria is over."),
            _cand("truce_signed", "Sire — a truce with Austria is signed."),
            _cand("league_paid", "Sire — St Petersburg now pays Vienna 400 gold a turn against us."),
        ]

    def test_the_paid_line_rides_beneath_a_crowded_morning(self):
        w = _boot()
        page = DS._select_headline(w, self._crowded(), record=False)
        assert any("now pays Vienna" in b for b in page["sub_beats"]), page

    def test_one_line_of_each_league_class_at_most(self):
        w = _boot()
        cands = self._crowded() + [
            _cand("league_paid", "Sire — London now pays Madrid 200 gold a turn against us.",
                  identity="league_paid:x")]
        page = DS._select_headline(w, cands, record=False)
        assert sum("now pays" in b for b in page["sub_beats"]) == 1, page

    def test_lever_down_the_crowded_page_drops_it(self, monkeypatch):
        monkeypatch.setattr(DS, "THE_LEAGUES_NEWS_RIDES_BENEATH", False)
        w = _boot()
        page = DS._select_headline(w, self._crowded(), record=False)
        assert not any("now pays Vienna" in b for b in page["sub_beats"]), page


# ═════════════════════ EG-I1 / EG-I2 the C5 reader ═════════════════════
def _c5(tmp_path, monkeypatch, arm_name, blocks, groups):
    from tests.test_economy_audit_2026_10_05 import _Arm
    from tools import _score_probes as P
    monkeypatch.setattr(P, "_c5_quoted_levers_flip", lambda arms, ctx, peace: (1, 1, []))
    arm = _Arm(blocks, groups, tmp_path)
    return P.living_balance_c5_front_page({arm_name: arm}, {"run_dir": str(tmp_path)})


class TestTheC5ReaderJudgesRowsOnTheirOwnMorning:
    """EG-I1: a log row the driver records late (`log_turn` 24 in turn 34's
    group) is judged on its own morning, where the page led with it."""

    def _read(self, tmp_path, monkeypatch, *, twice):
        """The row as the gate's CMD-M digest has it: surfacing ONLY in turn
        34's group (`twice=False`), or recorded on its own morning as well
        (`twice=True`, the counted-once case)."""
        from tests.test_economy_audit_2026_10_05 import _morning
        row = {"kind": "campaign_log", "dtype": "sponsorship_granted", "log_turn": 24,
               "text": "Britain sponsors Russia against France (500g/turn)"}
        g23 = _morning(23, page="Sire — London now pays St Petersburg 500 gold a turn against us.")
        if twice:
            g23.append(dict(row))
        g34 = _morning(34, page="Sire — Russia and Austria have made peace without us.")
        g34.append(dict(row))
        return _c5(tmp_path, monkeypatch, "CMD-M",
                   [(11, "Treaty signed: France → Armistice with Austria")], [g23, g34])

    def test_a_row_surfacing_late_is_judged_on_its_own_morning(self, tmp_path, monkeypatch):
        out = self._read(tmp_path, monkeypatch, twice=False)
        assert out["measured"] and out["pass"], out["evidence"]
        assert "1 sponsorships against France, 1 on the page" in out["evidence"]

    def test_a_row_recorded_twice_counts_once(self, tmp_path, monkeypatch):
        out = self._read(tmp_path, monkeypatch, twice=True)
        assert out["measured"] and out["pass"], out["evidence"]
        assert "1 sponsorships against France, 1 on the page" in out["evidence"]

    def test_lever_down_it_is_judged_where_it_surfaced(self, tmp_path, monkeypatch):
        from tools import _score_probes as P
        monkeypatch.setattr(P, "THE_C5_READER_JUDGES_A_ROW_ON_ITS_OWN_MORNING", False)
        out = self._read(tmp_path, monkeypatch, twice=False)
        assert not out["pass"] and "CMD-M t34 sponsorship" in out["evidence"], out["evidence"]


class TestTheC5ReaderKnowsARunOfTablelessMornings:
    """EG-I2: the old league stood for two mornings and the page told the news
    on the first of them; EA-16 looked back one."""

    def _read(self, tmp_path, monkeypatch):
        from tests.test_economy_audit_2026_10_05 import _morning
        groups = [
            _morning(7, page="Sire — Prussia moves toward war with Hanover."),
            _morning(8, page="Sire — Prussia would now join a league against us — relations −25."),
            _morning(9, page="Sire — Paget has crossed into Berry."),
            _morning(10, page="Sire — the war with Britain is over.", rows=("Prussia",),
                     line="Europe has watched us 4 quiet turns."),
        ]
        for g in groups[:3]:          # the old league stood: no table recorded
            g[1]["league_rows"] = []
        return _c5(tmp_path, monkeypatch, "CMD-A",
                   [(7, "Treaty signed: France → Armistice with Russia")], groups)

    def test_the_news_on_an_earlier_tableless_morning_counts(self, tmp_path, monkeypatch):
        out = self._read(tmp_path, monkeypatch)
        assert out["measured"] and out["pass"], out["evidence"]

    def test_lever_down_only_the_last_tableless_morning(self, tmp_path, monkeypatch):
        from tools import _score_probes as P
        monkeypatch.setattr(P, "THE_C5_READER_KNOWS_A_RUN_OF_TABLELESS_MORNINGS", False)
        out = self._read(tmp_path, monkeypatch)
        assert not out["pass"] and "CMD-A t10 Prussia newly free" in out["evidence"], out["evidence"]


# ═════════════════════ the driven client session ═════════════════════
class TestTheDrivenClientSession:
    """UI/UX C6's delegate evidence: the harness is parsed by the parse check,
    the reading's client arm runs it, and its backend never touches 8005 or
    the real saves."""

    def test_the_parse_check_reads_the_harness(self):
        src = (ROOT / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "res://../../tools/mode_c_driven_session.gd" in src

    def test_the_client_arm_runs_it(self):
        src = (ROOT / "tools" / "score_run.py").read_text(encoding="utf-8")
        assert "mode_c_driven_session.py" in src and 'rec["modec"]' in src

    def test_the_backend_is_sandboxed_on_an_unused_port(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mode_c_driven_session", str(ROOT / "tools" / "mode_c_driven_session.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.DEFAULT_PORT != 8005
        src = (ROOT / "tools" / "mode_c_driven_session.py").read_text(encoding="utf-8")
        assert '"INK_IRON_SAVE_DIR": str(saves)' in src and '"LLM_MODE": "mock"' in src
        gd = (ROOT / "tools" / "mode_c_driven_session.gd").read_text(encoding="utf-8")
        assert "push_input" in gd and "parse_input_event" not in gd


# ═════════════════════ EG-I3 the descent arm's precondition ═════════════════════
class TestTheTrackerKnowsAnUnknownName:
    """EG-I3: a landing line answered "There is no Marshal 'Oudinot'" never ran;
    the arm is a SCRIPT PRECONDITION, not naval evidence."""

    def _tracker(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "playtest_driver_eg", str(ROOT / "tools" / "playtest_driver.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_an_unknown_name_is_not_a_landing(self):
        mod = self._tracker()
        tr = mod.ExpeditionTracker()
        tr.observe("land Oudinot in Munster with 5,000 men",
                   {"success": True, "state": "awaiting_clarification",
                    "clarification_kind": "unknown_name"})
        assert tr.precondition_failed() is True

    def test_the_expedition_quote_still_counts(self):
        mod = self._tracker()
        tr = mod.ExpeditionTracker()
        tr.observe("land Oudinot in Munster with 5,000 men",
                   {"success": True, "state": "awaiting_clarification",
                    "clarification_kind": "naval_confirm"})
        assert tr.precondition_failed() is False

    def test_lever_down_the_unknown_name_counted(self):
        mod = self._tracker()
        mod.THE_TRACKER_KNOWS_AN_UNKNOWN_NAME = False
        tr = mod.ExpeditionTracker()
        tr.observe("land Oudinot in Munster with 5,000 men",
                   {"success": True, "state": "awaiting_clarification",
                    "clarification_kind": "unknown_name"})
        assert tr.precondition_failed() is False

    def test_the_arm_commissions_when_the_purse_can_bear_it(self):
        import json
        d = json.loads((ROOT / "tools" / "playtest_scripts" / "naval_descent.json")
                       .read_text(encoding="utf-8"))
        loops = {int(k): v for k, v in d["turns"].items()}
        assert "commission Oudinot" in loops[5] and "Oudinot, march to Normandy" in loops[5]
        assert any(x.startswith("land Oudinot in Munster") for x in loops[6])
        assert "_note_eg_i3" in d
