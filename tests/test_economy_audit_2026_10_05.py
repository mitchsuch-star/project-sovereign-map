"""The economy audit (October 5, 2026) — `docs/audits/ECONOMY_AUDIT_2026_10_05.md`,
rules `docs/SYSTEMS_REFERENCE.md` §97, gate record `docs/SCORE_FINISH_SPEC.md`
§6.7.

Every behaviour change sits behind its own lever; each class drives the real
code with the lever up and, where the row says what the shipped tree did, with
it down. The BASELINE_SERIES attribution is `tools/_econ_audit_series_arms.py`
(record `tools/_econ_audit_series_arms_final.json`), chain-pinned in the four
files that carry the series links.
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import coalition as CO
from backend.game_logic import contingent as CT
from backend.game_logic import diplomacy as DP
from backend.game_logic import instruments as IN
from backend.game_logic import jealousy as JL
from backend.game_logic import ledger as LG
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


def _net(world, nation):
    with _quiet():
        return int(LG._build_economy(world, nation)["net"])


# ═════════════════════════ EA-1 the Subsidies line ═════════════════════════
class TestTheSubsidiesAreOnTheBooks:
    def _sponsor(self, w, amount=200):
        res = IN.grant_directed_sponsorship(
            w, payer="France", recipient="Prussia", aim="Hanover",
            amount_per_turn=amount)
        assert res["success"], res

    def test_a_sponsorship_moves_both_projected_nets(self):
        w = _boot()
        fr, pr = _net(w, "France"), _net(w, "Prussia")
        self._sponsor(w)
        assert fr - _net(w, "France") == 200
        assert _net(w, "Prussia") - pr == 200
        econ = LG._build_economy(w, "France")
        assert econ["subsidies"] == -200
        row = next(r for r in econ["subsidy_streams"] if r["counterparty"] == "Prussia")
        assert (row["direction"], row["amount"], row["owed"], row["kind"]) == (
            "outgoing", 200, 200, "sponsorship")

    def test_lever_down_the_projection_omits_it(self, monkeypatch):
        w = _boot()
        self._sponsor(w)
        monkeypatch.setattr(IN, "THE_SUBSIDIES_ARE_ON_THE_BOOKS", False)
        econ = LG._build_economy(w, "France")
        assert econ["subsidies"] == 0 and econ["subsidy_streams"] == []

    def test_the_projection_clamps_by_the_payers_chest(self):
        w = _boot()
        self._sponsor(w)
        w.nation_gold["France"] = 60
        row = next(r for r in LG._build_economy(w, "France")["subsidy_streams"]
                   if r["counterparty"] == "Prussia")
        assert (row["amount"], row["owed"]) == (60, 200)

    def test_the_applied_record_is_what_the_engine_moved_and_what_was_owed(self):
        w = _boot()
        self._sponsor(w)
        w.nation_gold["France"] = 0
        IN.reset_subsidy_record(w)
        with _quiet():
            IN.process_instruments(w)
        out = IN.subsidies_for(w, "France", applied=True)
        row = next(r for r in out["streams"] if r["counterparty"] == "Prussia")
        # N8: a term the chest could not meet is said — paid 0 of 200.
        assert (out["net"], row["amount"], row["owed"]) == (0, 0, 200)
        assert IN.subsidies_for(w, "Prussia", applied=True)["net"] == 0

    def test_a_paid_transfer_is_signed_on_both_sides(self):
        w = _boot()
        self._sponsor(w)
        w.nation_gold["France"] = 5_000
        IN.reset_subsidy_record(w)
        with _quiet():
            IN.process_instruments(w)
        assert IN.subsidies_for(w, "France", applied=True)["net"] == -200
        assert IN.subsidies_for(w, "Prussia", applied=True)["net"] == 200

    def test_the_paymasters_subsidy_is_planned_once_and_paid_as_planned(self):
        from backend.game_logic.agendas import get_paymaster_nation
        w = _boot()
        # Britain boots AT its exclusive 2,000 floor (NA-3 §5.7), so the boot
        # turn pays nothing — stage the chest, then ask who pays.
        w.nation_gold["Britain"] = 30_000
        payer = get_paymaster_nation(w)
        assert payer == "Britain", payer
        plan = CO.projected_paymaster_subsidy(w)
        assert plan is not None and plan["payer"] == payer
        before = dict(w.nation_gold)
        IN.reset_subsidy_record(w)
        with _quiet():
            CO._process_british_subsidy(w)
        payer, recipient, amount = plan["payer"], plan["recipient"], plan["amount"]
        assert before[payer] - w.nation_gold[payer] == amount
        assert w.nation_gold[recipient] - before.get(recipient, 0) == amount
        assert IN.subsidies_for(w, payer, applied=True)["net"] == -amount

    def test_the_net_census_carries_both_new_lines(self):
        assert LG.NET_GOLD_COMPONENTS["subsidies"] == +1
        assert LG.NET_GOLD_COMPONENTS["continental_system"] == -1
        from backend.ai.question_desk import _NET_LABELS
        assert {"subsidies", "continental_system"} <= set(_NET_LABELS)
        from tools import playtest_driver as D
        keys = {k for k, _label in D.NET_COMPONENTS}
        assert {"subsidies", "continental_system"} <= keys

    def test_the_ledger_identity_holds_with_a_subsidy(self):
        w = _boot()
        self._sponsor(w)
        econ = LG._build_economy(w, "France")
        total = 0
        for key, sign in LG.NET_GOLD_COMPONENTS.items():
            total += sign * int(econ.get(key, 0) or 0)
        assert total == econ["net"]


# ═════════════════════════ EA-3 trade is a treaty ═════════════════════════
class TestTradeIsATreaty:
    def test_a_peace_earns_no_trade(self, monkeypatch):
        assert DP.trade_for_state("PEACE") == 0
        assert DP.trade_for_state("OPEN_BORDERS") == DP.TRADE_INCOME["OPEN_BORDERS"]
        monkeypatch.setattr(DP, "A_PEACE_EARNS_NO_TRADE", False)
        assert DP.trade_for_state("PEACE") == 50

    def test_a_written_peace_and_an_unwritten_one_trade_alike(self):
        w = _boot()
        before = DP.calculate_trade_income(w).get("France", 0)
        w.diplomatic_states["|".join(sorted(("France", "Portugal")))] = "PEACE"
        assert DP.calculate_trade_income(w).get("France", 0) == before

    def test_a_court_that_no_longer_stands_trades_with_nobody(self, monkeypatch):
        w = _boot()
        w.diplomatic_states["|".join(sorted(("France", "Portugal")))] = "ALLIANCE"
        with_ally = DP.calculate_trade_breakdown(w).get("France", [])
        assert any(p == "Portugal" for p, _a, _s in with_ally)
        for region in w.regions.values():
            if region.controller == "Portugal":
                region.controller = "Spain"
        w.invalidate_active_nations_cache()
        dead = DP.calculate_trade_breakdown(w)
        assert not any(p == "Portugal" for p, _a, _s in dead.get("France", []))
        assert "Portugal" not in dead
        monkeypatch.setattr(DP, "THE_DEAD_DO_NOT_TRADE", False)
        assert any(p == "Portugal" for p, _a, _s in
                   DP.calculate_trade_breakdown(w).get("France", []))

    def test_the_income_is_the_breakdowns_sum(self):
        w = _boot()
        rows = DP.calculate_trade_breakdown(w)
        income = DP.calculate_trade_income(w)
        assert income == {n: sum(a for _p, a, _s in r) for n, r in rows.items()}


# ═════════════════════════ EA-4 the System taxes trade that exists ═════════════════════════
class TestTheSystemTaxesTradeThatExists:
    def test_a_member_not_trading_with_britain_loses_nothing(self):
        w = _boot()
        w.continental_system_members = ["Holland"]
        assert DP.continental_system_losses(w) == {}

    def test_a_member_trading_with_britain_loses_what_it_earns_capped(self):
        w = _boot()
        w.diplomatic_states["|".join(sorted(("Britain", "Portugal")))] = "ALLIANCE"
        w.continental_system_members = ["Portugal"]
        rows = DP.calculate_trade_breakdown(w)
        earned = next(a for p, a, _s in rows["Portugal"] if p == "Britain")
        theirs = next(a for p, a, _s in rows["Britain"] if p == "Portugal")
        losses = DP.continental_system_losses(w)
        assert losses["Portugal"] == min(DP.CS_MEMBER_CAP, earned, theirs) > 0
        assert losses["Britain"] == losses["Portugal"]
        # The cap binds here (both sides earn more than it), and the cap is
        # the blessed 75 — the sweep found the line above inert to the
        # constant, since it reads the constant itself.
        assert min(earned, theirs) > 75 and losses["Portugal"] == 75

    def test_the_debit_is_named_on_both_ledgers(self):
        w = _boot()
        w.diplomatic_states["|".join(sorted(("Britain", "Portugal")))] = "ALLIANCE"
        w.continental_system_members = ["Portugal"]
        loss = DP.continental_system_losses(w)["Portugal"]
        assert LG._build_economy(w, "Portugal")["continental_system"] == loss
        assert LG._build_economy(w, "Britain")["continental_system"] == loss


# ═════════════════════════ EA-5 / EA-6 the satellite's own books ═════════════════════════
class TestTheSatellitesOwnBooks:
    def test_a_vassal_pays_its_tribute_on_its_own_net(self, monkeypatch):
        w = _boot()
        vassal = next(v for v, s in w.vassals.items() if s.get("lord") == "France")
        from backend.game_logic.vassal import vassal_tribute_owed
        owed = int(vassal_tribute_owed(w, vassal))
        assert owed > 0
        econ = LG._build_economy(w, vassal)
        assert econ["vassal_tribute"] < 0
        monkeypatch.setattr(LG, "THE_VASSAL_PAYS_ON_ITS_OWN_BOOKS", False)
        assert LG._build_economy(w, vassal)["vassal_tribute"] == 0

    def test_a_contingent_is_on_its_satellites_bill_and_not_its_lords(self, monkeypatch):
        w = _boot()
        # No contingent stands at boot (they are raised on turn 2): raise
        # Holland's through the real seam (Dumonceau, 6,500 men).
        with _quiet():
            assert CT.raise_contingent(w, "Holland")
        vassal, rec = "Holland", w.vassal_contingents["Holland"]
        men = int(w.marshals[rec["marshal"]].strength)
        assert men > 0
        lord_total = w.calculate_turn_upkeep("France")["total_strength"]
        own = w.calculate_turn_upkeep(vassal)["total_strength"]
        monkeypatch.setattr(CT, "THE_SATELLITE_PAYS_ON_ITS_OWN_BILL", False)
        assert w.calculate_turn_upkeep(vassal)["total_strength"] == own - men
        assert w.calculate_turn_upkeep("France")["total_strength"] == lord_total


# ═════════════════════════ EA-8 the army remembers its arrears ═════════════════════════
class TestTheArmyRemembersItsArrears:
    def _turn(self, w, nation, gold):
        w.nation_gold[nation] = gold
        w._update_bankruptcy(nation)
        return w.deserts_now(nation)

    def test_alternating_deficits_desert_at_the_fourth(self):
        w = _boot()
        seq = [self._turn(w, "Austria", g) for g in (-1, 10, -1, 10, -1, 10, -1)]
        assert seq == [False, False, False, False, False, False, True]

    def test_three_in_a_row_desert_at_the_third_as_before(self):
        w = _boot()
        assert [self._turn(w, "Austria", -1) for _ in range(3)] == [False, False, True]

    def test_a_single_deficit_is_forgotten_after_two_solvent_turns(self):
        w = _boot()
        self._turn(w, "Austria", -1)
        self._turn(w, "Austria", 10)
        self._turn(w, "Austria", 10)
        assert "Austria" not in w.nation_pay_arrears

    def test_lever_down_alternating_never_deserts(self, monkeypatch):
        monkeypatch.setattr(WS, "ARREARS_ARE_REMEMBERED", False)
        w = _boot()
        seq = [self._turn(w, "Austria", g) for g in (-1, 10, -1, 10, -1, 10, -1)]
        assert not any(seq)

    def test_the_arrears_survive_a_save(self):
        w = _boot()
        self._turn(w, "Austria", -1)
        restored = WorldState.from_dict(w.to_dict())
        assert restored.nation_pay_arrears == {"Austria": WS.ARREARS_PER_DEFICIT}

    def test_the_warning_names_the_arrears_not_a_run(self):
        w = _boot()
        for g in (-1, 10, -1, 10, -1):
            self._turn(w, "France", g)
        with _quiet():
            out = w.process_bankruptcy_desertion("France")
        text = " ".join(out["messages"])
        assert "bankrupt for 1 turns" not in text
        assert "arrears" in text


# ═════════════════════════ EA-9 a market keeps itself ═════════════════════════
class TestAMarketKeepsItself:
    def _region(self, w):
        return next(w.regions[r] for r in w.get_nation_regions("France")
                    if not w.regions[r].buildings)

    def test_a_market_bills_no_upkeep_and_a_depot_does(self, monkeypatch):
        w = _boot()
        region = self._region(w)
        before = w.calculate_turn_income("France")["infrastructure"]
        region.buildings = [{"type": "market", "damaged": False}]
        assert w.calculate_turn_income("France")["infrastructure"] == before
        region.buildings = [{"type": "supply_depot", "damaged": False}]
        assert w.calculate_turn_income("France")["infrastructure"] > before
        region.buildings = [{"type": "market", "damaged": False}]
        monkeypatch.setattr(WS, "A_MARKET_PAYS_ITS_OWN_KEEP", False)
        assert w.calculate_turn_income("France")["infrastructure"] > before


# ═════════════════════════ EA-10 / EA-11 / EA-12 the AI's purse ═════════════════════════
class TestTheAIsPurse:
    def test_no_tower_for_a_court_without_fog(self, monkeypatch):
        """With every building slot full, the admin chain reaches P6.5: the
        shipped AI builds a watchtower there; the audit's AI builds none and
        never asks where one would go."""
        from backend.ai import enemy_ai as EA
        from backend.commands.executor import CommandExecutor
        w = _boot()
        for name in w.get_nation_regions("Ottoman"):
            w.regions[name].buildings = [
                {"type": "market", "damaged": False},
                {"type": "supply_depot", "damaged": False},
                {"type": "fortification", "damaged": False}]
        w.nation_gold["Ottoman"] = 50_000
        ai = EA.EnemyAI(CommandExecutor())
        calls = []
        real = EA.EnemyAI._find_best_watchtower_region

        def spy(self, nation, world):
            calls.append(nation)
            return real(self, nation, world)

        monkeypatch.setattr(EA.EnemyAI, "_find_best_watchtower_region", spy)
        with _quiet():
            up = ai._pick_admin_action("Ottoman", w, 2, skip_actions={"recruit"})
        assert calls == [] and not (up and up.get("building_type") == "watchtower")
        monkeypatch.setattr(EA, "THE_AI_BUILDS_NO_WATCHTOWERS", False)
        with _quiet():
            down = ai._pick_admin_action("Ottoman", w, 2, skip_actions={"recruit"})
        assert calls and down and down.get("building_type") == "watchtower"

    def test_a_subsidy_pays_a_court_that_fights(self, monkeypatch):
        w = _boot()
        w.nation_gold["Britain"] = 30_000  # above the 2,000 floor (NA-3)
        member = CO.get_british_subsidy_recipient(w)
        assert member, "a funded paymaster has a recipient"
        for m in w.marshals.values():
            if m.nation == member:
                m.strength = 0
        assert CO.fields_an_army(w, member) is False
        assert CO.get_british_subsidy_recipient(w) != member
        monkeypatch.setattr(CO, "A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS", False)
        assert CO.get_british_subsidy_recipient(w) == member

    def test_the_court_arms_with_its_purse_at_war(self):
        """Britain at war, rich, its corps at boot strength: the rung raises
        men past the 1805 establishment, at a base, through the executor's
        own verb."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        w = _boot()
        ai = EnemyAI(CommandExecutor())
        w.nation_gold["Britain"] = 60_000
        with _quiet():
            order = ai._court_arms_with_its_purse("Britain", w)
        assert order is not None and order["action"] == "recruit"
        assert w.get_marshal(order["marshal"]).nation == "Britain"

    def test_a_poor_court_does_not_arm(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        w = _boot()
        ai = EnemyAI(CommandExecutor())
        w.nation_gold["Britain"] = 500
        with _quiet():
            assert ai._court_arms_with_its_purse("Britain", w) is None

    def test_a_court_at_peace_levies_only_at_a_base(self):
        """At peace the rung raises only at a supply base (the neutrals
        ballooned on the measured field-levy arm, investigator C's v5)."""
        from backend.ai import enemy_ai as EA
        from backend.commands.economy_executor import region_has_friendly_supply
        from backend.commands.executor import CommandExecutor
        w = _boot()
        ai = EA.EnemyAI(CommandExecutor())
        w.nation_gold["Ottoman"] = 60_000
        with _quiet():
            order = ai._court_arms_with_its_purse("Ottoman", w)
        if order is not None:
            assert region_has_friendly_supply(w.get_region(order["target"]))

    # Every other admin rung skipped, so the chain reaches P7.5 — the lever is
    # read at the call site, and a pin that calls the rung directly cannot
    # see it (the sweep found exactly that inert).
    _ALL_BUT_RECRUIT = {"purchase_levy", "grant_dotation", "grant_pension",
                        "invest_vassal", "grant_region_to_vassal", "change_autonomy",
                        "recruit_marshal", "enact_law", "build_fleet", "build",
                        "naval_expedition", "naval_diversion", "repair"}

    @pytest.mark.parametrize("up", [True, False], ids=["lever_up", "lever_down"])
    def test_the_lever_gates_the_rung_in_the_chain(self, monkeypatch, up):
        from backend.ai import enemy_ai as EA
        from backend.commands.executor import CommandExecutor
        w = _boot()
        ai = EA.EnemyAI(CommandExecutor())
        reached = []
        monkeypatch.setattr(EA.EnemyAI, "_court_arms_with_its_purse",
                            lambda self, nation, world: reached.append(nation))
        if not up:  # the up arm reads the SHIPPED lever, never sets it
            monkeypatch.setattr(EA, "THE_COURT_ARMS_WITH_ITS_PURSE", False)
        w.nation_gold["Britain"] = 60_000
        with _quiet():
            ai._pick_admin_action("Britain", w, 2, skip_actions=set(self._ALL_BUT_RECRUIT))
        assert reached == (["Britain"] if up else [])


# ═════════════════════════ SFR-DR1 the league marches on what it declared ═════════════════════════
class TestTheLeagueDeclaresInItsOwnRight:
    def _spy(self, monkeypatch, succeed=True):
        seen = []
        real = DP.declare_war

        def spy(world, attacker, target, *a, **kw):
            seen.append((attacker, kw.get("suppress_unresolved_offensive_cascade")))
            if not succeed:
                return {"success": False, "message": "refused (staged)"}
            return real(world, attacker, target, *a, **kw)

        monkeypatch.setattr(DP, "declare_war", spy)
        return seen

    def test_each_new_member_declares_in_its_own_right(self, monkeypatch):
        seen = self._spy(monkeypatch)
        w = _boot()
        with _quiet():
            CO.form_coalition(["Prussia"], w)
        assert seen == [("Prussia", True)]
        assert "Prussia" in w.active_coalition["members"]

    def test_lever_down_the_first_declarer_cascades(self, monkeypatch):
        seen = self._spy(monkeypatch)
        monkeypatch.setattr(CO, "THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT", False)
        w = _boot()
        with _quiet():
            CO.form_coalition(["Prussia"], w)
        assert seen == [("Prussia", False)]

    def test_a_failed_declaration_is_not_a_member(self, monkeypatch):
        self._spy(monkeypatch, succeed=False)
        w = _boot()
        with _quiet():
            CO.form_coalition(["Prussia"], w)
        assert "Prussia" not in w.active_coalition["members"]
        monkeypatch.setattr(CO, "A_FAILED_DECLARATION_IS_NOT_A_MEMBER", False)
        w2 = _boot()
        with _quiet():
            CO.form_coalition(["Prussia"], w2)
        assert "Prussia" in w2.active_coalition["members"]


# ═════════════════════════ SFR-D23 the beat reads the morning's chest ═════════════════════════
class TestTheBeatReadsTheMorningsChest:
    def _beat(self, w):
        events = []
        record = {"target": "Hanover", "design_id": "hanoverian_prize",
                  "want_title": "The Hanoverian Prize"}
        with _quiet():
            WC._emit_crisis_brewing(w, "Prussia", record, events)
        return events[-1]["message"]

    def test_the_brewing_beat_prices_against_the_forecast(self, monkeypatch):
        w = _boot()
        w.nation_gold["France"] = 100
        monkeypatch.setattr(LG, "chest_forecast", lambda world, nation: {
            "chest": 100, "net": 49_900, "projected": 50_000})
        assert "you can afford it" in self._beat(w)

    def test_lever_down_the_beat_reads_the_live_chest(self, monkeypatch):
        w = _boot()
        w.nation_gold["France"] = 100
        monkeypatch.setattr(LG, "chest_forecast", lambda world, nation: {
            "chest": 100, "net": 49_900, "projected": 50_000})
        monkeypatch.setattr(WC, "THE_BEAT_READS_THE_MORNINGS_CHEST", False)
        assert "the treasury holds 100" in self._beat(w)


# ═════════════════════════ EA-13 the Net says why it moved ═════════════════════════
class TestTheNetSaysWhyItMoved:
    def test_no_note_without_a_yesterday(self):
        w = _boot()
        assert LG._build_economy(w, "France")["net_moves_note"] == ""

    def test_a_moved_line_is_named_with_its_cause(self):
        w = _boot()
        LG.snapshot_morning_accounts(w)
        w.current_turn += 1
        vassal = next(v for v, s in w.vassals.items() if s.get("lord") == "France")
        w.vassals[vassal]["lord"] = "Austria"
        LG.snapshot_morning_accounts(w)
        note = LG._build_economy(w, "France")["net_moves_note"]
        assert note.startswith("Since yesterday's accounts the Net is")
        assert "tribute" in note
        from backend.display_names import display_nation
        assert display_nation(vassal) in note

    def test_the_two_self_explained_bills_are_left_to_their_own_notes(self):
        w = _boot()
        LG.snapshot_morning_accounts(w)
        w.current_turn += 1
        for m in w.marshals.values():
            if m.nation == "France":
                m.strength = int(m.strength * 0.5)
        vassal = next(v for v, st in w.vassals.items() if st.get("lord") == "France")
        w.vassals[vassal]["lord"] = "Austria"
        LG.snapshot_morning_accounts(w)
        note = LG._build_economy(w, "France")["net_moves_note"]
        assert "tribute" in note
        assert "upkeep" not in note and "Charges of Empire" not in note

    def test_lever_down_no_note(self, monkeypatch):
        w = _boot()
        LG.snapshot_morning_accounts(w)
        w.current_turn += 1
        vassal = next(v for v, st in w.vassals.items() if st.get("lord") == "France")
        w.vassals[vassal]["lord"] = "Austria"
        monkeypatch.setattr(LG, "THE_NET_SAYS_WHY_IT_MOVED", False)
        LG.snapshot_morning_accounts(w)
        assert LG._build_economy(w, "France")["net_moves_note"] == ""

    def test_an_ai_court_is_never_narrated(self):
        w = _boot()
        LG.snapshot_morning_accounts(w)
        w.current_turn += 1
        LG.snapshot_morning_accounts(w)
        assert LG._build_economy(w, "Austria")["net_moves_note"] == ""

    def test_every_net_line_has_a_label(self):
        labelled = {k for k, _l in LG.NET_LINE_LABELS}
        expected = (set(LG.NET_GOLD_COMPONENTS) - {"upkeep_base", "upkeep_surcharge"}) | {"upkeep"}
        assert labelled == expected

    def test_the_charges_note_names_its_line(self):
        last = {"state_charges": 100, "breakdown": {"state_charges_terms": []}}

        class _W:
            _income_phase_results = {"France": last}
            nation_gold = {"France": 30_000}

        out = LG.why_the_bills_moved(_W(), "France", {}, 400, [])
        assert "last turn's charge" in out["charges_note"]


# ═════════════════════════ EA-14 / EA-15 the counsel names the law ═════════════════════════
class TestTheCounselNamesTheLaw:
    def _rich(self):
        w = _boot()
        w.nation_gold["France"] = 40_000
        w.admin_actions_remaining = 2
        return w

    def test_a_rich_france_is_told_of_the_staff(self):
        from backend.ai.counsel import economy_counsel
        lines = economy_counsel(self._rich(), "France", limit=3)
        assert lines and lines[0].startswith("enact the Staff — 9,000g")

    def test_a_rich_court_is_not_refused_for_being_rich(self, monkeypatch):
        """EA-18: at 40,000 the forecast Net is negative only because the
        Charges of Empire are a share of the chest — the Net BEFORE them
        carries the Staff's 300. The AI rung keeps the plain read (EAD-9)."""
        from backend.ai import counsel as CN
        from backend.game_logic import reforms as R
        w = self._rich()
        row = R.resolve_law(w, "France", "the Staff")
        with _quiet():
            assert "forecast Net" in R.ai_purse_refusal(w, "France", row)
            assert R.ai_purse_refusal(w, "France", row, net_before_charges=True) == ""
            assert CN._law_terms(w, "France").startswith("enact the Staff")
        monkeypatch.setattr(CN, "THE_COUNSEL_SEES_THROUGH_THE_CHARGES", False)
        with _quiet():
            assert CN._law_terms(w, "France") is None

    def test_the_charges_read_still_refuses_a_law_the_income_cannot_carry(self):
        """The Net before the Charges must still carry the upkeep: strip
        France's income and the law is refused on that read too."""
        from backend.game_logic import reforms as R
        w = self._rich()
        row = R.resolve_law(w, "France", "the Staff")
        for name, region in w.regions.items():
            if region.controller == "France":
                region.income_value = 0
        with _quiet():
            why = R.ai_purse_refusal(w, "France", row, net_before_charges=True)
        assert why.startswith("the Net before the Charges of Empire"), why

    def test_saving_for_the_staff_offers_no_smaller_law(self):
        from backend.ai.counsel import _law_terms
        w = self._rich()
        w.nation_gold["France"] = 6_000
        assert _law_terms(w, "France") is None

    def test_the_line_is_an_order_the_verb_takes(self):
        from backend.game_logic import reforms as R
        w = self._rich()
        row = R.resolve_law(w, "France", "the Staff")
        assert row is not None and R.is_staff(row)
        assert R.law_refusal(w, "France", str(row["id"])) == ""

    def test_the_desk_answers_what_to_spend_gold_on(self):
        from backend.ai.state_desk import _answer_spend, classify_state_question
        q = classify_state_question("what should I spend gold on", marshals=["Ney"],
                                    enemies=[], regions=["Paris"], nations=["Austria"])
        assert q and q["kind"] == "spend"
        text = _answer_spend(self._rich())
        assert "enact the Staff" in text and "treasury holds" in text

    def test_the_questions_reach_the_desk_through_the_command_road(self, monkeypatch):
        import backend.main as M
        from fastapi.testclient import TestClient
        from tests import _chip_census as C
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            C.board_env(monkeypatch)
            M.world.nation_gold["France"] = 40_000
            M.world.admin_actions_remaining = 2
            client = TestClient(M.app)
            with _quiet():
                spend = client.post("/command", json={"command": "what should I spend gold on"}).json()
                how = client.post("/command", json={"command": "how are our finances"}).json()
            assert "enact the Staff" in str(spend.get("message"))
            assert "treasury holds" in str(how.get("message"))
        finally:
            M.world, M.game_state["world"], M.parser = prior[0], prior[1], prior[2]

    def test_the_desk_answers_how_the_finances_stand(self):
        from backend.ai.state_desk import classify_state_question
        # SFR-D1's own phrasing, its contraction and the fear (found closing
        # the row) — each shrugged before.
        for line in ("how are our finances", "how is the treasury doing",
                     "how is the treasury?", "how's the treasury?",
                     "are we going broke?", "are we running low on gold?"):
            q = classify_state_question(line, marshals=["Ney"], enemies=[],
                                        regions=["Paris"], nations=["Austria"])
            assert q and q["kind"] == "net", line


# ═════════════════════════ EA-17 the top rung promises nothing higher ═════════════════════════
class TestTheTopRungPromisesNothingHigher:
    def test_a_top_rung_card_says_the_quarrel_can_grow_no_worse(self):
        w = _boot()
        a, b = w.marshals["Ney"], w.marshals["Murat"]
        JL._set_escalation_level(a, b.name, JL.ESCALATION_MUTUAL_LEVEL)
        JL._set_escalation_level(b, a.name, JL.ESCALATION_MUTUAL_LEVEL)
        text = JL._standing_cost_detail(a, b)
        assert "may harden further" not in text and "grow no worse" in text


# ═════════════════════════ the series record ═════════════════════════
class TestTheSeriesRecord:
    def test_arm_zero_reproduces_the_prior_and_all_is_the_shipped_series(self):
        rec = json.loads((ROOT / "tools" / "_econ_audit_series_arms_final.json")
                         .read_text(encoding="utf-8"))
        assert rec["arms"]["0"]["series"] == rec["prior"]
        from tests.test_ai_intent_threat_migration import BASELINE_SERIES
        # RE-SEATED by the economy gate (October 5, 2026): the audit's ALL
        # arm is the gate's prior; the gate's ALL arm is the standing series.
        gate = json.loads((ROOT / "tools" / "_econ_gate_series_arms_final.json")
                          .read_text(encoding="utf-8"))
        assert rec["arms"]["ALL"]["series"] == gate["prior"]
        assert gate["arms"]["ALL"]["series"] == BASELINE_SERIES
        # every lever the audit landed has its own arm
        assert set(rec["levers"]) == set("DFSBTGCVKWAMOR")


# ═════════════════════════ EA-16 the C5 reader knows a tableless morning ═════════════════════════
class _Arm:
    """The three things the C5 probe reads off an archived arm."""

    def __init__(self, blocks, groups, path):
        self._blocks, self._groups, self.path = blocks, groups, path
        self.records = [r for g in groups for r in g]

    def blocks(self):
        return self._blocks

    def by_turn(self):
        return self._groups

    def kind(self, k):
        return [r for r in self.records if r.get("kind") == k]


def _morning(turn, *, page, rows=(), line=""):
    return [{"kind": "turn", "turn": turn},
            {"kind": "dispatch", "headline_text": page, "sub_beats": [],
             "league_rows": [{"nation": n, "status": "joins", "major": True, "text": ""}
                             for n in rows],
             "league_line": line}]


class TestTheC5ReaderKnowsATablelessMorning:
    """EA-16: the dispatch records no league table on a morning the old league
    still stands, but the page's beat reads the same forecast every morning —
    the audit's CMD-M arm told Prussia's news on turn 12 and first carried
    her row on turn 13 (measured on the archive, `ECONOMY_AUDIT_2026_10_05.md`
    §8). The keep-out-lever half of the item is held passing here."""

    def _read(self, tmp_path, monkeypatch, t12_line=""):
        from tools import _score_probes as P
        monkeypatch.setattr(P, "_c5_quoted_levers_flip", lambda arms, ctx, peace: (1, 1, []))
        groups = (_morning(11, page="Sire — a truce with Austria is signed.")
                  + _morning(12, page="Sire — Austria and Prussia would now join a league against us (relations -77 and -25).",
                             line=t12_line)
                  + _morning(13, page="Sire — our peace binds Austria for 4 more turns.",
                             rows=("Prussia",), line="Prussia would march in the next league."))
        by_turn = [groups[0:2], groups[2:4], groups[4:6]]
        arm = _Arm([(11, "Treaty signed: France → Armistice with Austria")], by_turn, tmp_path)
        return P.living_balance_c5_front_page({"CMD-M": arm}, {"run_dir": str(tmp_path)})

    def test_the_news_on_the_tableless_morning_counts(self, tmp_path, monkeypatch):
        out = self._read(tmp_path, monkeypatch)
        assert out["measured"] and out["pass"], out["evidence"]
        assert "1 great powers newly free to join, 1 on the page" in out["evidence"]

    def test_lever_down_the_reader_asks_only_the_rows_first_page(self, tmp_path, monkeypatch):
        from tools import _score_probes as P
        monkeypatch.setattr(P, "THE_C5_READER_KNOWS_A_TABLELESS_MORNING", False)
        out = self._read(tmp_path, monkeypatch)
        assert out["measured"] and not out["pass"], out["evidence"]
        assert "CMD-M t13 Prussia newly free" in out["evidence"]

    def test_a_morning_with_a_table_does_not_excuse(self, tmp_path, monkeypatch):
        """A morning that recorded its table had the rows to show her: the
        news one page early is not excused there."""
        out = self._read(tmp_path, monkeypatch,
                         t12_line="No court would join a league against us today.")
        assert out["measured"] and not out["pass"], out["evidence"]
