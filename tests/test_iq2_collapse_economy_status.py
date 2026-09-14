"""IQ-2 "The Collapse Is Legible" — the economy & status surfaces (Sept 14, 2026).

Measured in played 40-turn campaigns: a France reduced to one province, then
none, with Paris lost and the Emperor captured, kept reading an ordinary
campaign. This file pins the economy/status half of the row:

B1  the levy is OPEN only where `_execute_recruit` would levy — the depot's
    own location gates (who holds it, will its people answer) are ONE
    predicate, `economy_executor.recruit_location_gate`, read by both.
B2  a landless court is told the decisive refusal (no home soil) before the
    gold gate that implies saving would help.
B3  the Strategic Ledger carries the collapse note, the levy's closed reason,
    and a MANPOWER tab that stops pricing a depot the enemy holds.
B4  Berthier's report opens on the state of the empire and names our
    prisoners (a captured Emperor used to vanish from YOUR FORCES).
B5  the captured sovereign's card no longer says "The Empire is his estate."
B6  both end-turn banners carry ONE collapse line and the same event keys,
    from one shared helper — and, with the roster fix, the banner's named
    components are the APPLIED phase (the `Other` residual decomposes into
    tribute + trade + the admin bonus, no phantom upkeep).
B7  the roster fix's economy consequences at the executor level: a landless
    France is billed and goes bankrupt; her settlement debts stand.

Scope note (binding): legible, never terminal. Every collapse surface is
checked for the forbidden outcome words.
"""

import contextlib
import copy
import io
import pathlib

import pytest

import backend.commands.economy_executor as EE
import backend.commands.meta_executor as ME
import backend.game_logic.ledger as L
import backend.game_logic.marshal_overview as MO
import backend.game_logic.recruitment as R
import backend.intel_report as IR
import backend.models.world_state as WS
from backend.commands.economy_executor import get_levy_status
from backend.commands.executor import CommandExecutor
from backend.game_logic import collapse
from backend.game_logic.ledger import build_strategic_ledger
from backend.game_logic.marshal_overview import build_marshal_overview
from backend.game_logic.settlement_offers import process_recurring_settlement_payments
from backend.intel_report import generate_intel_report
from backend.models.world_state import WorldState

SCENARIO = str(pathlib.Path(__file__).resolve().parents[1] / "godot-client"
               / "project-sovereign" / "assets" / "maps" / "europe_1805.json")

# The scope note, as an assertion: no collapse surface may promise an end.
FORBIDDEN = ("game over", "campaign ends", "the campaign is over", "defeat",
             "eliminated", "last chance")


def _assert_never_terminal(text: str):
    low = text.lower()
    for word in FORBIDDEN:
        assert word not in low, f"{word!r} in {text!r}"


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


@pytest.fixture(scope="module")
def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture
def europe(_boot):
    return copy.deepcopy(_boot)


def _collapse(world, enemy="Austria"):
    """Every French province to a court at war with France."""
    for region in world.regions.values():
        if region.controller == "France":
            region.controller = enemy
    world.invalidate_active_nations_cache()


def _maul(world):
    """The levy-open board of test_ec_levy_and_camp: under the ordinance, a
    full pool, and a corps at the capital to receive the men."""
    french = [m for m in world.marshals.values()
              if m.nation == "France" and m.strength > 0]
    for m in french:
        m.strength = int(m.strength * 0.38)
    french[0].location = world.get_nation_capital("France")


def _end_turn(world):
    res = _quiet(CommandExecutor().execute, {"command": {"action": "end_turn"}},
                 {"world": world})
    ev = next(e for e in res.get("events", []) if e.get("type") == "turn_end")
    return res, ev


def _execute(world, command):
    return _quiet(CommandExecutor().execute, {"command": command}, {"world": world})


# ════════════════════════════════════════════════════════════════════════
# B1 — the levy reads the depot's own gate
# ════════════════════════════════════════════════════════════════════════

class TestB1LevyReadsTheDepot:

    def test_the_open_board_is_open_with_no_reason(self, europe):
        _maul(europe)
        levy = get_levy_status(europe)
        assert levy["open"] is True
        assert levy["capital_held"] is True
        assert levy["closed_reason"] == ""

    def test_an_enemy_held_capital_closes_the_levy(self, europe):
        """The measured lie: open, priced at Paris, with Austria in Paris.
        Killed by reverting the gate or dropping the lever."""
        _maul(europe)
        europe.regions["Paris"].controller = "Austria"
        europe.invalidate_active_nations_cache()
        levy = get_levy_status(europe)
        assert levy["open"] is False
        assert levy["capital_held"] is False
        assert levy["closed_reason"] == (
            "The depot at Paris is closed — Paris is in Austria's hands.")
        # Shown = applied: the executor refuses the same levy.
        res = _execute(europe, {"action": "recruit"})
        assert res["success"] is False
        assert ("We do not control Paris, Your Majesty. Recruitment is "
                "impossible there.") in res["message"]

    def test_lever_down_reproduces_the_lie(self, europe, monkeypatch):
        _maul(europe)
        europe.regions["Paris"].controller = "Austria"
        europe.invalidate_active_nations_cache()
        monkeypatch.setattr(EE, "LEVY_READS_THE_DEPOT_GATE", False)
        levy = get_levy_status(europe)
        assert levy["open"] is True
        assert "closed_reason" not in levy and "capital_held" not in levy

    def test_an_unrest_capital_closes_the_levy(self, europe, monkeypatch):
        """The executor's SECOND location gate (stability <= 50)."""
        _maul(europe)
        europe.regions["Paris"].stability = 40
        levy = get_levy_status(europe)
        assert levy["open"] is False
        assert levy["capital_held"] is True
        assert "stability 40/100" in levy["closed_reason"]
        res = _execute(europe, {"action": "recruit"})
        assert res["success"] is False
        assert "stability 40/100" in res["message"]
        monkeypatch.setattr(EE, "LEVY_READS_THE_DEPOT_GATE", False)
        assert get_levy_status(europe)["open"] is True

    def test_one_predicate_for_the_status_and_the_executor(self, europe, monkeypatch):
        """Single source: both read `recruit_location_gate` at call time."""
        _maul(europe)
        calls = []
        orig = EE.recruit_location_gate

        def spy(region, nation):
            calls.append(region.name)
            return orig(region, nation)

        monkeypatch.setattr(EE, "recruit_location_gate", spy)
        get_levy_status(europe)
        assert calls == ["Paris"]
        europe.regions["Paris"].controller = "Austria"
        res = _execute(europe, {"action": "recruit"})
        assert res["success"] is False
        assert calls.count("Paris") >= 2

    def test_the_other_terms_are_named_in_the_executors_order(self, europe):
        _maul(europe)
        europe.manpower_pools["France"]["infantry"] = 0
        assert get_levy_status(europe)["closed_reason"] == (
            "The infantry pool holds 0 — a levy is 10,000.")
        for m in europe.marshals.values():
            if m.nation == "France":
                m.location = "Naples"
        assert get_levy_status(europe)["closed_reason"] == (
            "No corps stands within reach of the depot at Paris to receive "
            "the recruits.")

    def test_the_boot_names_the_ordinance(self, europe):
        next(m for m in europe.marshals.values()
             if m.nation == "France" and m.strength > 0).location = "Paris"
        assert get_levy_status(europe)["closed_reason"] == (
            "The establishment stands 59,000 over the ordinance.")

    def test_the_legacy_levy_dict_is_byte_identical(self, monkeypatch):
        legacy = _quiet(WorldState, player_nation="France")
        up = get_levy_status(legacy)
        monkeypatch.setattr(EE, "LEVY_READS_THE_DEPOT_GATE", False)
        assert up == get_levy_status(legacy)
        assert "closed_reason" not in up

    def test_no_ai_module_reads_the_levy(self):
        """GR5 check for B1: the levy status is a player display; no AI
        module reads it, so the AI's recruiting is untouched."""
        root = pathlib.Path(__file__).resolve().parents[1] / "backend"
        for path in list((root / "ai").rglob("*.py")) + [root / "game_logic" / "turn_manager.py"]:
            src = path.read_text(encoding="utf-8")
            assert "get_levy_status" not in src and "_levy_status" not in src, path


# ════════════════════════════════════════════════════════════════════════
# B2 — the commission names the home-soil gate first
# ════════════════════════════════════════════════════════════════════════

class TestB2CommissionNamesTheSoil:

    def _poor_and_landless(self, europe):
        _collapse(europe)
        candidate = dict(europe.marshal_pool["France"][0])
        europe.nation_gold["France"] = int(candidate["cost"]) - 1
        return candidate

    def test_a_landless_court_is_told_about_soil_not_gold(self, europe):
        candidate = self._poor_and_landless(europe)
        refusal = R.check_commission(europe, "France", candidate)
        assert refusal.startswith("No HOME soil remains")
        assert "treasury holds" not in refusal

    def test_lever_down_asks_for_gold_first(self, europe, monkeypatch):
        candidate = self._poor_and_landless(europe)
        monkeypatch.setattr(R, "COMMISSION_ASKS_FOR_HOME_SOIL_FIRST", False)
        assert "treasury holds" in R.check_commission(europe, "France", candidate)

    def test_the_executor_speaks_the_same_refusal(self, europe):
        candidate = self._poor_and_landless(europe)
        res = _execute(europe, {"action": "recruit_marshal",
                                "target": candidate["name"]})
        assert res["success"] is False
        assert "No HOME soil remains" in res["message"]
        assert "treasury holds" not in res["message"]

    def test_a_court_with_soil_still_hears_the_price(self, europe):
        candidate = dict(europe.marshal_pool["France"][0])
        europe.nation_gold["France"] = int(candidate["cost"]) - 1
        assert "treasury holds" in R.check_commission(europe, "France", candidate)


# ════════════════════════════════════════════════════════════════════════
# B3 — the Strategic Ledger
# ════════════════════════════════════════════════════════════════════════

class TestB3Ledger:

    def test_the_collapse_note_is_the_one_source_plus_the_scope_note(self, europe):
        _collapse(europe)
        note = build_strategic_ledger(europe)["collapse_note"]
        state = collapse.get_collapse_state(europe)
        assert note == (f"{collapse.summary_line(europe, state)} "
                        f"{collapse.CAMPAIGN_CONTINUES}")
        assert "France holds no province of her own." in note
        _assert_never_terminal(note.replace(collapse.CAMPAIGN_CONTINUES, ""))

    def test_a_standing_realm_carries_an_empty_note(self, europe):
        assert build_strategic_ledger(europe)["collapse_note"] == ""

    def test_the_legacy_and_lever_down_payloads_carry_no_key(self, europe, monkeypatch):
        legacy = _quiet(WorldState, player_nation="France")
        assert "collapse_note" not in build_strategic_ledger(legacy)
        _collapse(europe)
        monkeypatch.setattr(collapse, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "collapse_note" not in build_strategic_ledger(europe)

    def test_the_levy_block_carries_the_closed_reason(self, europe):
        _maul(europe)
        europe.regions["Paris"].controller = "Austria"
        levy = build_strategic_ledger(europe)["economy"]["levy"]
        assert levy["open"] is False
        assert levy["closed_reason"] == get_levy_status(europe)["closed_reason"]
        assert "Paris is in Austria's hands" in levy["closed_reason"]

    def test_the_manpower_tab_names_the_closed_depot(self, europe, monkeypatch):
        europe.regions["Paris"].controller = "Austria"
        manpower = build_strategic_ledger(europe)["manpower"]
        for arm in ("infantry", "cavalry", "artillery"):
            assert manpower[arm]["cost_note"] == (
                "The depot at Paris is closed — Paris is in Austria's hands.")
            assert manpower[arm]["depot_closed"] is True
        monkeypatch.setattr(L, "THE_MANPOWER_TAB_READS_THE_DEPOT", False)
        manpower = build_strategic_ledger(europe)["manpower"]
        assert manpower["infantry"]["cost_note"].startswith("Live price at the capital")
        assert "depot_closed" not in manpower["infantry"]

    def test_a_held_capital_keeps_the_live_price_note(self, europe):
        manpower = build_strategic_ledger(europe)["manpower"]
        assert manpower["infantry"]["cost_note"].startswith("Live price at the capital")
        assert "depot_closed" not in manpower["infantry"]


# ════════════════════════════════════════════════════════════════════════
# B4 — Berthier's report
# ════════════════════════════════════════════════════════════════════════

class TestB4IntelReport:

    def test_a_collapsed_report_opens_on_the_state_of_the_empire(self, europe):
        _collapse(europe)
        report = generate_intel_report(europe)
        lines = report["report_text"].split("\n")
        state = collapse.get_collapse_state(europe)
        assert lines[2] == "STATE OF THE EMPIRE:"
        assert lines[3] == f"  {collapse.summary_line(europe, state)}"
        assert lines[4] == f"  {collapse.CAMPAIGN_CONTINUES}"
        assert lines.index("STATE OF THE EMPIRE:") < lines.index("YOUR FORCES:")
        assert report["collapse_line"] == collapse.summary_line(europe, state)
        _assert_never_terminal(lines[3])

    def test_a_standing_realm_has_no_block(self, europe, monkeypatch):
        report = generate_intel_report(europe)
        assert "STATE OF THE EMPIRE" not in report["report_text"]
        assert "collapse_line" not in report
        _collapse(europe)
        monkeypatch.setattr(collapse, "THE_COLLAPSE_IS_LEGIBLE", False)
        assert "STATE OF THE EMPIRE" not in generate_intel_report(europe)["report_text"]

    def _capture(self, world, name, captor="Austria"):
        m = world.marshals[name]
        m.captured_by = captor
        m.captured_turn = 3
        m.strength = 0
        m.location = world.get_nation_capital(captor) or "Vienna"
        return m

    def test_our_prisoners_are_named_with_their_captor(self, europe):
        self._capture(europe, "Ney")
        report = generate_intel_report(europe)
        assert "PRISONERS:" in report["report_text"]
        assert "  Ney: held by Austria at Vienna since T3." in report["report_text"].split("\n")
        assert report["prisoners"][0]["name"] == "Ney"
        assert report["prisoners"][0]["captor"] == "Austria"
        assert "Ney" not in {f["name"] for f in report["your_forces"]}

    def test_the_captured_emperor_no_longer_vanishes(self, europe):
        self._capture(europe, "Napoleon")
        text = generate_intel_report(europe)["report_text"]
        assert "  Napoleon: held by Austria at Vienna since T3." in text.split("\n")

    def test_the_captor_is_humanized(self, europe):
        self._capture(europe, "Ney", captor="KingdomOfItaly")
        text = generate_intel_report(europe)["report_text"]
        assert "held by Kingdom of Italy" in text
        assert "KingdomOfItaly" not in text.split("PRISONERS:")[1].split("\n\n")[0]

    def test_lever_down_restores_the_silent_report(self, europe, monkeypatch):
        self._capture(europe, "Ney")
        monkeypatch.setattr(IR, "THE_REPORT_NAMES_ITS_PRISONERS", False)
        report = generate_intel_report(europe)
        assert "PRISONERS" not in report["report_text"]
        assert "prisoners" not in report

    def test_the_typed_status_command_carries_both_blocks(self, europe):
        _collapse(europe)
        self._capture(europe, "Napoleon")
        res = _execute(europe, {"action": "status"})
        assert "STATE OF THE EMPIRE:" in res["message"]
        assert "PRISONERS:" in res["message"]
        assert "The Emperor is a prisoner of Austria." in res["message"]

    def test_get_status_carries_the_block(self, europe):
        from fastapi.testclient import TestClient
        import backend.main as M
        from backend.commands.parser import CommandParser
        _collapse(europe)
        saved = (M.parser, M.world, M.game_state)
        try:
            M.parser = CommandParser(use_real_llm=False)
            M.world = europe
            M.game_state = {"world": europe}
            body = TestClient(M.app).get("/status").json()
        finally:
            M.parser, M.world, M.game_state = saved
        assert "STATE OF THE EMPIRE:" in body["report_text"]
        assert body["collapse_line"].startswith("France holds no province of her own.")


# ════════════════════════════════════════════════════════════════════════
# B5 — the captured sovereign's card
# ════════════════════════════════════════════════════════════════════════

class TestB5TheCaptiveEmperorsCard:

    def _card(self, world):
        return {c["name"]: c for c in build_marshal_overview(world)}["Napoleon"]

    def test_a_free_emperor_keeps_his_estate(self, europe):
        assert self._card(europe)["sovereign_note"] == "The Empire is his estate."

    def test_a_captured_emperor_is_named_a_prisoner(self, europe, monkeypatch):
        nap = europe.marshals["Napoleon"]
        nap.captured_by, nap.captured_turn, nap.strength = "Austria", 5, 0
        assert self._card(europe)["sovereign_note"] == (
            "A prisoner of Austria — the Empire is governed from a cell.")
        monkeypatch.setattr(MO, "THE_CAPTIVE_EMPEROR_IS_NAMED", False)
        assert self._card(europe)["sovereign_note"] == "The Empire is his estate."

    def test_the_captor_is_humanized(self, europe):
        nap = europe.marshals["Napoleon"]
        nap.captured_by, nap.captured_turn, nap.strength = "KingdomOfItaly", 5, 0
        assert self._card(europe)["sovereign_note"] == (
            "A prisoner of Kingdom of Italy — the Empire is governed from a cell.")


# ════════════════════════════════════════════════════════════════════════
# B6 — the end-turn banners
# ════════════════════════════════════════════════════════════════════════

class TestB6EndTurnBanner:

    def test_the_banner_states_the_collapse(self, europe):
        _collapse(europe)
        res, ev = _end_turn(europe)
        line = collapse.summary_line(europe, collapse.get_collapse_state(europe))
        assert ev["collapse_line"] == line
        assert ev["provinces_held"] == 0
        assert line in res["message"].split("\n")
        _assert_never_terminal(line)

    def test_a_standing_realm_carries_empty_keys(self, europe):
        res, ev = _end_turn(europe)
        assert ev["collapse_line"] == ""
        assert ev["provinces_held"] == len(europe.get_nation_regions("France"))
        assert isinstance(ev["provinces_held"], int)

    def test_the_legacy_event_is_byte_identical(self):
        legacy = _quiet(WorldState, player_nation="France")
        _res, ev = _end_turn(legacy)
        assert "collapse_line" not in ev and "provinces_held" not in ev

    def test_lever_down_drops_the_keys_and_the_line(self, europe, monkeypatch):
        _collapse(europe)
        monkeypatch.setattr(collapse, "THE_COLLAPSE_IS_LEGIBLE", False)
        res, ev = _end_turn(europe)
        assert "collapse_line" not in ev and "provinces_held" not in ev
        assert "holds no province of her own" not in res["message"]

    def test_the_auto_advance_twin_carries_the_same_line(self, europe):
        _collapse(europe)
        europe.actions_remaining = 1
        europe.admin_actions_remaining = 0
        # Soult (literal) takes a defensive order without objecting — an
        # aggressive marshal's objection would return before the AP is spent.
        res = _execute(europe, {"action": "defend", "marshal": "Soult"})
        assert res["action_info"].get("turn_advanced") is True, res.get("message")
        ev = next(e for e in res["events"] if e.get("type") == "turn_end")
        line = collapse.summary_line(europe, collapse.get_collapse_state(europe))
        assert ev["collapse_line"] == line
        assert ev["provinces_held"] == 0
        assert line in res["message"].split("\n")

    def test_both_paths_read_the_one_helper(self, europe, monkeypatch):
        spy = {"collapse_line": "SPY-LINE", "provinces_held": 42}
        monkeypatch.setattr(ME, "collapse_turn_end_fields", lambda world: dict(spy))
        res, ev = _end_turn(copy.deepcopy(europe))
        assert ev["collapse_line"] == "SPY-LINE" and ev["provinces_held"] == 42
        assert "SPY-LINE" in res["message"].split("\n")
        europe.actions_remaining = 1
        europe.admin_actions_remaining = 0
        # Soult (literal) takes a defensive order without objecting — an
        # aggressive marshal's objection would return before the AP is spent.
        res = _execute(europe, {"action": "defend", "marshal": "Soult"})
        assert res["action_info"].get("turn_advanced") is True
        ev = next(e for e in res["events"] if e.get("type") == "turn_end")
        assert ev["collapse_line"] == "SPY-LINE" and ev["provinces_held"] == 42

    def test_the_banner_names_the_applied_phase_for_a_landless_france(self, europe):
        """The probe, pinned: with the roster fix the printed in-phase
        components ARE the charged phase (upkeep, Admiralty, requisitions…),
        so `Other` holds only the out-of-phase sources — no phantom bill."""
        _collapse(europe)
        _res, ev = _end_turn(europe)
        phase = europe._income_phase_results.get("France")
        assert phase is not None
        assert ev["upkeep"] == phase["upkeep_data"]["total"] > 0
        named_in_phase = (ev["income"] + ev["requisitions"] + ev["overseas"]
                          - ev["occupation"] - ev["contributions"]
                          - ev["state_charges"] - ev["dotation_skim"]
                          - ev["rente_cost"] - ev["infrastructure"]
                          - ev["admiralty"] - ev["upkeep"])
        assert named_in_phase + int(phase["admin_bonus"]) == int(phase["net"])

    def test_lever_down_the_printed_upkeep_was_never_charged(self, europe, monkeypatch):
        monkeypatch.setattr(WS, "PLAYER_NEVER_LEAVES_THE_ROSTER", False)
        _collapse(europe)
        _res, ev = _end_turn(europe)
        assert "France" not in europe._income_phase_results
        assert ev["upkeep"] > 0   # printed from a recompute, never billed


# ════════════════════════════════════════════════════════════════════════
# B7 — the roster fix's economy consequences, at the executor level
# ════════════════════════════════════════════════════════════════════════

class TestB7TheLandlessRealmStillPays:

    def test_a_landless_france_is_billed_and_goes_bankrupt(self, europe):
        _collapse(europe)
        europe.nation_gold["France"] = 0
        _end_turn(europe)
        assert europe._income_phase_results["France"]["upkeep_data"]["total"] > 0
        assert europe.nation_gold["France"] < 0
        assert europe.nation_bankruptcy_turns["France"] == 1

    def test_lever_down_her_army_was_free(self, europe, monkeypatch):
        monkeypatch.setattr(WS, "PLAYER_NEVER_LEAVES_THE_ROSTER", False)
        _collapse(europe)
        europe.nation_gold["France"] = 0
        _end_turn(europe)
        assert "France" not in europe._income_phase_results
        assert europe.nation_gold["France"] >= 0
        assert europe.nation_bankruptcy_turns.get("France", 0) == 0

    def _owe_prussia(self, world):
        world.nation_gold["France"] = 5000
        world.recurring_settlement_payments = [{
            "payment_id": "iq2-p1", "from": "France", "to": "Prussia",
            "amount_per_turn": 100, "turns_remaining": 3,
            "war_label": "the IQ-2 settlement"}]
        world.invalidate_active_nations_cache()

    def test_a_landless_france_still_owes_her_settlement_gold(self, europe):
        _collapse(europe)
        self._owe_prussia(europe)
        prussia_before = europe.nation_gold["Prussia"]
        events = process_recurring_settlement_payments(europe)
        assert events["cancelled"] == []
        assert europe.nation_gold["France"] == 4900
        assert europe.nation_gold["Prussia"] == prussia_before + 100
        assert europe.recurring_settlement_payments[0]["turns_remaining"] == 2

    def test_lever_down_the_debt_was_cancelled_as_payer_eliminated(self, europe, monkeypatch):
        monkeypatch.setattr(WS, "PLAYER_NEVER_LEAVES_THE_ROSTER", False)
        _collapse(europe)
        self._owe_prussia(europe)
        events = process_recurring_settlement_payments(europe)
        assert [c["reason"] for c in events["cancelled"]] == ["payer_eliminated"]
        assert europe.nation_gold["France"] == 5000

    def test_the_debt_survives_a_whole_end_turn(self, europe):
        _collapse(europe)
        self._owe_prussia(europe)
        _end_turn(europe)
        payments = europe.recurring_settlement_payments
        assert len(payments) == 1 and payments[0]["turns_remaining"] == 2
