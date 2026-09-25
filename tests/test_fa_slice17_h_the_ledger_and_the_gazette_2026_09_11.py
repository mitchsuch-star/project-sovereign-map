"""FA slice 17 (part h) — "THE LEDGER AND THE GAZETTE" (September 11, 2026).

Six rows and one refutation: FA-N52 (Le Moniteur's collectors named types no
producer wrote — and the laurels passing is now LOGGED), FA-N53 (the promise
said 3 turns and bought 7), FA-N66 (an enemy siege on our soil was fogged as
'beyond our sight'), FA-N85 (the Third Coalition's successor was minted the
Second), FA-N88 (the documented single source for the Charges of Empire had
zero production callers), FA-S16-D5 (the stalemate popup charged −3 twice
and quoted neither), and FA-N51 (REFUTED BY EVENTS — FA-21 landed without the
'second half' the row said it needed; the cheap honest deliverable is the
monotonicity pin on the gold term so the asymmetry cannot drift unobserved).

Every behaviour change sits behind a module-level lever whose False arm
reproduces the prior behaviour, and each lever is pinned in both positions.
"""

import contextlib
import io
import re
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO = REPO_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(scope="module")
def world1805():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(world1805):
    with _quiet():
        w = WorldState.from_dict(world1805.to_dict())
    w.authority_tracker.authority = 50
    return w


# ═══════════════════════════════════════════════════════════════════════
# FA-N52 — Le Moniteur's collectors name types the log actually carries
# ═══════════════════════════════════════════════════════════════════════

class TestFAN52TheMoniteurReadsLiveTypes:

    def test_every_collector_key_is_a_campaign_log_type(self):
        """A key the fog filter can never pass is dead by construction — this
        forbids the class from recurring (it fails on five keys before the fix)."""
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        from backend.game_logic import gazette as G
        keys = set(G._WAR_TYPES) | set(G._COURT_TYPES) | set(G._ARMY_TYPES)
        dead = sorted(k for k in keys if k not in CAMPAIGN_LOG_TYPES)
        assert dead == [], dead

    def test_the_lever_down_restores_the_dead_keys(self, monkeypatch):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        from backend.game_logic import gazette as G
        monkeypatch.setattr(G, "THE_MONITEUR_READS_LIVE_TYPES", False)
        court = G.collector_types(G._COURT_TYPES)
        assert "coalition_formed" in court and "coalition_declared" not in court
        assert "incoming_ultimatum" in court and "ai_ultimatum_accepted" not in court
        assert "vassal_created" in court and "vassal_transferred" not in court
        army = G.collector_types(G._ARMY_TYPES)
        assert "marshal_petition" in army and "fontainebleau_petition" not in army
        assert "coalition_formed" not in CAMPAIGN_LOG_TYPES, "the prior key really was dead"

    def test_a_coalition_declaration_reaches_the_court_section(self, world, monkeypatch):
        from backend.game_logic import gazette as G
        world.log_event({"type": "coalition_declared", "members": ["Austria", "Russia"],
                         "leader": "Austria", "target_nation": "France",
                         "name": "The Fourth Austria Coalition"})
        with _quiet():
            issue = G.compose_issue(world, world.current_turn)
        text = " ".join(str(v) for v in issue.values())
        assert "Coalition" in text and "Austria" in text, issue
        monkeypatch.setattr(G, "THE_MONITEUR_READS_LIVE_TYPES", False)
        with _quiet():
            prior = G.compose_issue(world, world.current_turn)
        assert "Coalition formed" not in " ".join(str(v) for v in prior.values())

    def test_a_vassal_changing_lord_and_a_yielded_ultimatum_reach_the_court_section(self, world):
        from backend.game_logic import gazette as G
        world.log_event({"type": "vassal_transferred", "vassal": "Holland",
                         "from_lord": "France", "to_lord": "Britain"})
        world.log_event({"type": "ai_ultimatum_accepted", "source": "Prussia"})
        with _quiet():
            issue = G.compose_issue(world, world.current_turn)
        text = " ".join(str(v) for v in issue.values())
        assert "Holland passes from" in text, issue
        assert "yielded to Prussia" in text, issue

    def test_the_laurels_passing_is_logged_beside_its_beat(self, world, monkeypatch):
        """`glory_crown_lost` had a dispatch beat and no log row — the Gazette
        key for it was dead. The producer now writes the row; lever down, the
        beat still fires and the log stays silent (the prior behaviour)."""
        from backend.game_logic import jealousy as J
        ney = world.marshals["Ney"]
        davout = world.marshals["Davout"]
        for m in world.marshals.values():
            m.glory_crowned = False
            m.glory = 0
        ney.glory_crowned = True   # wore the crown last turn…
        davout.glory = 50          # …and Davout now stands above him
        before = len(world.event_log)
        with _quiet():
            events = J.recompute_crowns(world)
        assert any(e.get("type") == "glory_crown_lost" and e.get("marshal") == "Ney" for e in events), events
        rows = [e for e in world.event_log[before:] if e.get("type") == "glory_crown_lost"]
        assert [r["marshal"] for r in rows] == ["Ney"], world.event_log[before:]
        # lever down: same beat, no row
        monkeypatch.setattr(J, "THE_CROWN_LOST_IS_LOGGED", False)
        ney.glory_crowned = True
        davout.glory_crowned = False
        before = len(world.event_log)
        with _quiet():
            events = J.recompute_crowns(world)
        assert any(e.get("type") == "glory_crown_lost" for e in events)
        assert not [e for e in world.event_log[before:] if e.get("type") == "glory_crown_lost"]

    def test_the_laurels_passing_prints_a_sentence_and_reaches_the_army_section(self, world):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, filter_campaign_log, format_event_oneliner
        from backend.game_logic import gazette as G
        assert "glory_crown_lost" in CAMPAIGN_LOG_TYPES
        world.log_event({"type": "glory_crown_lost", "marshal": "Ney", "nation": "France"})
        with _quiet():
            visible = filter_campaign_log(world.event_log, world)
        lines = [format_event_oneliner(e) for e in visible if e.get("type") == "glory_crown_lost"]
        assert lines and "laurels have passed" in lines[-1] and "Ney" in lines[-1], lines
        assert not lines[-1].startswith("Event:"), "a type with a producer and no arm prints its key"
        with _quiet():
            issue = G.compose_issue(world, world.current_turn)
        assert any("laurels have passed" in ln for ln in (issue.get("army") or [])), issue

    def test_an_enemy_courts_laurels_never_reach_the_players_log(self, world):
        """The player-court rule the crowning obeys: the new type files with
        the same fog arm."""
        from backend.campaign_log import filter_campaign_log
        world.log_event({"type": "glory_crown_lost", "marshal": "Mack", "nation": "Austria"})
        with _quiet():
            visible = filter_campaign_log(world.event_log, world)
        assert not [e for e in visible if e.get("type") == "glory_crown_lost" and e.get("nation") == "Austria"]

    def test_the_log_type_count_moved_once_and_on_purpose(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES
        assert len(CAMPAIGN_LOG_TYPES) == 168  # 162->163 flipped consciously: IQ-1 SW-1 adds `substitutes_purchased` — the substitute market is the first purchase in the game limited by gold alone, and an AI nation buying 30,000 men had no persistent surface to appear on  # 163->164 flipped consciously: IQ-4: diplomatic_mission_ended -- the log never recorded how a mission ended  # 164->165 flipped consciously: IQ-7 (Sept 16, 2026) adds `client_petition_answered` — a loyal satellite's petition (THE PROVINCE / THE RELIEF) is the web's first non-rebellion decision, and its answer — granted, refused, or left to lapse — had no persistent surface (no inert diplomacy type was retired in exchange: the six producerless ones are the FA-R5 census's, not this slice's)  # 165->166 flipped consciously: GE-1 adds `campaign_ending` (the Fall, the Verdict, a Humbled Peace each leave one chronicle line)  # 166->167 flipped consciously: GE-3 adds the congress chronicle type (summons, recognitions, the War of the Congress, the dissolution)  # 167->168 flipped consciously: VP-M1 (GE-D1, Sept 25, 2026) adds `marshal_wounded` — a general carried from the field, the corps standing; a killed general rides `marshal_destroyed` with cause killed_in_action
        src = (REPO_ROOT / "tests" / "test_campaign_log.py").read_text(encoding="utf-8")
        assert "161->162 flipped consciously: FA-N52" in src


# ═══════════════════════════════════════════════════════════════════════
# FA-N53 — the promise quotes the window it buys
# ═══════════════════════════════════════════════════════════════════════

def _make_eroding(world, name, wins=3):
    from backend.game_logic import dotation, jealousy as J
    # F4 "The fuse is longer": the collective petition needs turn >= 12.
    floor = max(dotation.GRACE_TURNS + 3, J.FONTAINEBLEAU_MIN_TURN)
    if world.current_turn < floor:
        world.current_turn = floor
    marshal = world.marshals[name]
    marshal.expectation_steps = wins
    marshal.expectation_grace_turn = world.current_turn - dotation.GRACE_TURNS
    assert dotation.is_eroding(marshal, world)
    return marshal


class TestFAN53ThePromiseQuotesItsWindow:

    def _petition(self, world):
        from backend.game_logic import jealousy as J
        marshals = [_make_eroding(world, n) for n in ("Ney", "Murat", "Lannes")]
        with _quiet():
            J.check_fontainebleau(world, [])
        petition = world.pending_marshal_petition
        assert petition and petition["kind"] == "fontainebleau"
        return marshals, petition

    def test_the_window_is_the_arithmetic_the_arm_applies(self):
        from backend.game_logic import dotation, jealousy as J
        assert J.FONTAINEBLEAU_PROMISE_WINDOW == dotation.GRACE_TURNS + J.FONTAINEBLEAU_PROMISE_GRACE == 7

    def test_option_confirmation_and_dispatch_all_say_the_same_number(self, world):
        from backend.game_logic import dotation, jealousy as J
        marshals, petition = self._petition(world)
        promise = next(o for o in petition["options"] if o["id"] == "promise")
        assert f"extends {J.FONTAINEBLEAU_PROMISE_WINDOW} turns" in promise["detail"], promise["detail"]
        assert "extends 3 turns" not in promise["detail"]
        with _quiet():
            result = J.handle_petition_response(world, "promise")
        assert result["success"]
        assert f"extends {J.FONTAINEBLEAU_PROMISE_WINDOW} turns" in result["message"], result["message"]
        # F4 "The fuse is longer" (Sept 24, 2026): the dispatch's UNMET block
        # is an ALARM — it names a man only within two turns of erosion, so a
        # promise that just bought seven turns of patience takes him OFF it
        # (the rail row and the petition's own confirmation quote the window,
        # asserted above). With the lever down the rows say the same number.
        assert not [r for r in dotation.build_unmet_marshals(world, "France")
                    if r["marshal"] in {m.name for m in marshals}]
        prior = dotation.THE_UNMET_BLOCK_WAITS
        dotation.THE_UNMET_BLOCK_WAITS = False
        try:
            rows = {r["marshal"]: r for r in dotation.build_unmet_marshals(world, "France")}
        finally:
            dotation.THE_UNMET_BLOCK_WAITS = prior
        for m in marshals:
            assert rows[m.name]["grace_turns_left"] == J.FONTAINEBLEAU_PROMISE_WINDOW, rows[m.name]

    def test_the_turns_actually_bought_equal_the_quoted_window(self, world):
        """Measured, not asserted from the constant: erosion is quiet for
        exactly WINDOW turns after the promise and resumes on the next."""
        from backend.game_logic import dotation, jealousy as J
        marshals, _p = self._petition(world)
        with _quiet():
            J.handle_petition_response(world, "promise")
        start = world.current_turn
        for m in marshals:
            assert m.expectation_grace_turn == start + J.FONTAINEBLEAU_PROMISE_GRACE  # the MECHANIC, untouched
        quiet = 0
        for offset in range(0, 12):
            world.current_turn = start + offset
            if any(dotation.is_eroding(m, world) for m in marshals):
                break
            quiet += 1
        assert quiet == J.FONTAINEBLEAU_PROMISE_WINDOW, quiet

    def test_the_lever_down_quotes_the_bare_three_again(self, world, monkeypatch):
        from backend.game_logic import jealousy as J
        monkeypatch.setattr(J, "THE_PROMISE_QUOTES_ITS_WINDOW", False)
        _m, petition = self._petition(world)
        promise = next(o for o in petition["options"] if o["id"] == "promise")
        assert "extends 3 turns" in promise["detail"]


# ═══════════════════════════════════════════════════════════════════════
# FA-N66 — a siege on our own soil survives the fog
# ═══════════════════════════════════════════════════════════════════════

class TestFAN66TheSiegeOnOurSoilIsReported:

    def _phase(self, event_type, region="Rhineland"):
        return {"nations": {"Austria": {"actions": [{
            "marshal": "Mack", "action_type": "attack",
            "message": "Mack invests the works.",
            "ai_action": {"marshal": "Mack", "target": region},
            "events": [{"type": event_type, "marshal": "Mack", "region": region,
                        "turns_required": 2}]}]}}}

    def test_the_ab_the_row_measured_now_agrees(self, world):
        """REPRO_L's A/B on the boot: same French province at PARTIAL, only the
        event type changed — `occupation_started` 0 kept vs `garrison_assault`
        1 kept. One tuple entry separated them."""
        import backend.main as M
        from backend.models.intel import PARTIAL
        world.get_region_intel("Swabia").visibility = PARTIAL
        assert world.regions["Rhineland"].controller == "France"
        siege = M._filter_enemy_phase_by_visibility(self._phase("occupation_started"), world)
        assault = M._filter_enemy_phase_by_visibility(self._phase("garrison_assault"), world)
        assert assault["nations"]["Austria"]["actions"]
        assert siege["nations"]["Austria"]["actions"], siege

    def test_the_lever_down_fogs_the_siege_again(self, world, monkeypatch):
        import backend.main as M
        from backend.models.intel import PARTIAL
        monkeypatch.setattr(M, "THE_SIEGE_ON_OUR_SOIL_IS_REPORTED", False)
        world.get_region_intel("Swabia").visibility = PARTIAL
        out = M._filter_enemy_phase_by_visibility(self._phase("occupation_started"), world)
        assert not out["nations"].get("Austria", {}).get("actions")
        # and the FA-23 pair still passes with the lever down (it is FA-23's arm)
        out = M._filter_enemy_phase_by_visibility(self._phase("garrison_assault"), world)
        assert out["nations"]["Austria"]["actions"]

    def test_a_siege_on_somebody_elses_soil_is_not_leaked(self, world):
        import backend.main as M
        from backend.models.intel import PARTIAL
        world.get_region_intel("Swabia").visibility = PARTIAL
        world.regions["Bohemia"].controller = "Austria"
        out = M._filter_enemy_phase_by_visibility(self._phase("occupation_started", "Bohemia"), world)
        assert not out["nations"].get("Austria", {}).get("actions")

    def test_no_false_beyond_our_sight_line_for_a_court_besieging_us(self, world):
        import backend.main as M
        from backend.models.intel import PARTIAL
        world.get_region_intel("Swabia").visibility = PARTIAL
        visible = M._build_visible_enemy_phase(self._phase("occupation_started"), world) or {}
        hidden = visible.get("fog_hidden_nations") or []
        assert "Austria" not in hidden, visible


# ═══════════════════════════════════════════════════════════════════════
# FA-N85 — the successor to the Third Coalition is the Fourth
# ═══════════════════════════════════════════════════════════════════════

class TestFAN85TheFourthCoalition:

    def test_the_authored_pair_agrees(self, world1805):
        assert world1805.coalition_count == 3
        assert world1805.active_coalition["name"] == "Third Coalition"

    def test_the_next_coalition_is_minted_the_fourth(self, world):
        from backend.game_logic.coalition import dissolve_coalition, form_coalition
        with _quiet():
            dissolve_coalition(world, "test")
            world.coalition_cooldown = 0
            form_coalition(["Austria", "Britain", "Russia"], world)
        assert world.coalition_count == 4
        assert world.active_coalition["name"].startswith("The Fourth "), world.active_coalition["name"]

    def test_the_legacy_world_still_boots_at_zero(self):
        from backend.models.world_state import WorldState
        with _quiet():
            legacy = WorldState()
        assert int(getattr(legacy, "coalition_count", 0)) == 0


# ═══════════════════════════════════════════════════════════════════════
# FA-N88 — the applied figure is PRODUCED BY the documented single source
# ═══════════════════════════════════════════════════════════════════════

class TestFAN88TheSingleSourceIsCalled:

    def test_the_income_phase_reads_the_helper(self, world, monkeypatch):
        """The join pin the row asked for: a sentinel from the helper must
        surface in the income breakdown, the applied result and the treasury."""
        calls = []

        def sentinel(self, nation, rate=None):
            calls.append((nation, rate))
            return 12345

        monkeypatch.setattr(WorldState, "calculate_state_charges", sentinel)
        world.nation_gold["France"] = 50_000
        with _quiet():
            income = world.calculate_turn_income("France")
        assert income["state_charges"] == 12345
        assert calls and calls[-1][0] == "France" and calls[-1][1] is not None, calls
        before = int(world.nation_gold["France"])
        with _quiet():
            applied = world.process_income_phase("France")
        assert applied["state_charges"] == 12345
        # Review round (L3-9): the treasury moved by the applied net, which
        # carries the sentinel — an exact identity, not an `or True`.
        assert int(world.nation_gold["France"]) - before == int(applied.get("net", 0))
        assert applied["state_charges"] == 12345

    def test_the_rate_default_keeps_the_twelve_call_sites_byte_identical(self, world):
        world.nation_gold["France"] = 50_000
        assert world.calculate_state_charges("France") == world.calculate_state_charges(
            "France", rate=world.get_state_charges_rate("France")["rate"])

    def test_the_rate_passed_in_is_the_rate_used(self, world):
        """G4: the caller's once-computed rate is authoritative — a helper that
        quietly re-derived it would walk the regions twice AND could disagree
        with the breakdown the ledger prints beside the figure."""
        world.nation_gold["France"] = 50_000
        real = world.get_state_charges_rate("France")["rate"]
        assert real > 0
        assert world.calculate_state_charges("France", rate=0) == 0
        doubled = world.calculate_state_charges("France", rate=real * 2)
        single = world.calculate_state_charges("France", rate=real)
        assert doubled > single > 0
        assert abs(doubled - 2 * single) <= 1

    def test_the_helper_and_the_income_path_agree_to_the_gold(self, world):
        world.nation_gold["France"] = 50_000
        with _quiet():
            income = world.calculate_turn_income("France")
        assert income["state_charges"] == world.calculate_state_charges("France") > 0

    def test_the_income_phase_calls_no_inline_copy(self):
        """Source census scoped to `calculate_turn_income`'s body: the
        arithmetic is not re-derived there."""
        import inspect
        src = inspect.getsource(WorldState.calculate_turn_income)
        code = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith("#"))
        assert "self.calculate_state_charges(" in code
        assert "WAR_EFFORT_DIVISOR" not in code


# ═══════════════════════════════════════════════════════════════════════
# FA-S16-D5 — the stalemate popup quotes what it charges
# ═══════════════════════════════════════════════════════════════════════

STALEMATE = {"interrupt_type": "combat_stalemate", "marshal": "Davout",
             "options": ["continue_order", "hold_position", "cancel_order"]}


class TestFAS16D5TheStalemateQuotesItsPrice:

    def test_the_quoter_prices_both_paying_arms_and_not_continue(self):
        from backend.commands.strategic import STALEMATE_ABANDON_TRUST, interrupt_option_costs
        assert interrupt_option_costs(dict(STALEMATE)) == {
            "hold_position": STALEMATE_ABANDON_TRUST, "cancel_order": STALEMATE_ABANDON_TRUST}
        assert interrupt_option_costs(dict(STALEMATE, interrupt_type="repeated_combat")) == {
            "hold_position": STALEMATE_ABANDON_TRUST, "cancel_order": STALEMATE_ABANDON_TRUST}

    def test_the_lever_down_quotes_nothing(self, monkeypatch):
        from backend.commands import strategic
        monkeypatch.setattr(strategic, "THE_STALEMATE_QUOTES_ITS_PRICE", False)
        assert strategic.interrupt_option_costs(dict(STALEMATE)) == {}

    @pytest.mark.parametrize("choice", ["hold_position", "cancel_order"])
    def test_the_price_on_the_button_is_the_price_charged(self, world, choice):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import (STALEMATE_ABANDON_TRUST, StrategicOrderProcessor,
                                                interrupt_option_costs)
        from backend.models.marshal import StrategicOrder
        marshal = world.marshals["Davout"]
        order = StrategicOrder(command_type="MOVE_TO", target="Bavaria", target_type="region", started_turn=1, original_command="march to Bavaria")
        marshal.strategic_order = order
        pending = dict(STALEMATE, enemy="Mack", location=marshal.location)
        quoted = interrupt_option_costs(pending, world)[choice]
        before = marshal.trust.value
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc._respond_combat_stalemate(marshal, order, choice, pending, world, {"world": world})
        assert result["success"]
        assert result["trust_change"] == marshal.trust.value - before == quoted == STALEMATE_ABANDON_TRUST

    def test_continue_stays_free(self, world):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.models.marshal import StrategicOrder
        marshal = world.marshals["Davout"]
        order = StrategicOrder(command_type="MOVE_TO", target="Bavaria", target_type="region", started_turn=1, original_command="march to Bavaria")
        marshal.strategic_order = order
        before = marshal.trust.value
        proc = StrategicOrderProcessor(CommandExecutor())
        with _quiet():
            result = proc._respond_combat_stalemate(marshal, order, "continue_order",
                                                    dict(STALEMATE, enemy="Mack"), world, {"world": world})
        assert result["trust_change"] == 0 and marshal.trust.value == before

    def test_the_wire_carries_the_quote(self, world):
        import backend.main as M
        from backend.commands.strategic import STALEMATE_ABANDON_TRUST
        with _quiet():
            response = M.build_base_response(world, pending_interrupt=dict(STALEMATE))
        assert response["pending_interrupt"]["option_costs"] == {
            "hold_position": STALEMATE_ABANDON_TRUST, "cancel_order": STALEMATE_ABANDON_TRUST}

    def test_the_responder_has_no_bare_literal_left(self):
        import inspect
        from backend.commands import strategic
        src = inspect.getsource(strategic.StrategicOrderProcessor._respond_combat_stalemate)
        assert "trust_change = -3" not in src
        assert src.count("STALEMATE_ABANDON_TRUST") == 2


# ═══════════════════════════════════════════════════════════════════════
# FA-N51 — REFUTED BY EVENTS; the gold term's shape is pinned so it cannot
# drift unobserved
# ═══════════════════════════════════════════════════════════════════════

class TestFAN51TheGoldTermIsLinearAndUncapped:

    def _score(self, world, lump):
        from backend.game_logic.diplomacy import calculate_acceptance
        proposal = {"type": "peace", "proposer_nation": "France", "target_nation": "Austria",
                    "sweeteners": [], "demands": [{"type": "gold_lump", "value": lump}]}
        with _quiet():
            return calculate_acceptance(proposal, world)

    def test_the_bilateral_gold_term_is_linear_uncapped_and_purse_blind(self, world1805):
        """The row's one surviving true claim, pinned as the CURRENT shape:
        −0.03 per gold on `deal_balance`, no ceiling. A cap or a purse scaling
        (the settlement path's −45 ceiling mirrored) is a balance change to
        every bilateral gold demand on both boards and needs a gate — when it
        lands, this pin is flipped consciously, not silently."""
        from backend.game_logic.diplomacy import DEMAND_VALUES
        rate = DEMAND_VALUES["gold_lump"]
        assert rate == -3 / 100
        balances = {x: self._score(world1805, x)["components"]["deal_balance"] for x in (1000, 2000, 4000, 8000)}
        assert balances[2000] - balances[1000] == pytest.approx(rate * 1000, abs=0.2)
        assert balances[4000] - balances[2000] == pytest.approx(rate * 2000, abs=0.2)
        assert balances[8000] - balances[4000] == pytest.approx(rate * 4000, abs=0.2)
        assert balances[8000] < -200, "no ceiling anywhere — the settlement path caps at −45"

    def test_fa21s_purse_floor_stands_and_the_row_is_recorded_refuted(self):
        gate = (REPO_ROOT / "docs" / "DESIGN_REFINEMENT.md").read_text(encoding="utf-8")
        row = [ln for ln in gate.split("\n") if re.match(r"^(> )?\| \*\*FA-N51\*\* \|", ln)]
        assert row, "FA-N51's row has gone missing"
        assert "REFUTED BY EVENTS" in row[0]
        assert "FA-21" in row[0]
