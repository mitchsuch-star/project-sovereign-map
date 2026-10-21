"""SF-RR7 "the morning of the peace" (Pre-Deploy S14 part 4, October 20, 2026).

Rows `docs/BUG_FIXES.md` SFR-B3 (the Score Finish table), DDB-X4 (§DD-B) and
PC-X69 (§PC); the ruling `docs/audits/DD_B_RULINGS_2026_10_14.md` §2 SFR-B3
("Europe waits on Paris"); rules `docs/SYSTEMS_REFERENCE.md` §136.

The gap, measured first on the PRESS arm (`tools/score_run.py`; the econ_gate
archive's `arms/PRESS` and today's tree alike): the Ottoman Empire, Sweden and
Sardinia began to brew at the Congress's fifth day, declared on its eighth,
and the Imperial Peace was proclaimed the next end turn beside "A coalition
has formed against France!" with Europe's alarm at 76 the morning after.

* **The hold** — while the Congress sits and fewer than two great powers
  refuse it, no new league declares against France: a brew's countdown holds
  at its last turn and the instant bar brews instead; the two-refuser lowered
  gate is untouched (`congress.league_waits_on_paris`).
* **The signing** spends Europe's alarm to the Armed Peace's watch (45) and
  dismisses any brew (`congress.the_signing_spends`).
* **The page** names what the peace buys — the great powers' signatures, not
  the lesser courts' grievances (`congress.bought_line`).
* **PC-X69** — a great power the league's bond binds sues the Congress as her
  PRICED separate peace: her sue line reads the bond's depth (−40 → −49 under
  Britain's 200-gold bond on the boot board), the table, its price and her
  letter say so, a held capital still forces it, and her signed suit is
  reneged against her as any separate peace inside the term
  (`congress.sue_line`, `bond.letter_line`).
* **DDB-X4** — `tools/_ge3_series_arms.py` flips LIVE seams, the new rules
  among them, and its dormancy proof re-reads `BASELINE_SERIES` byte for byte.
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy as AI
from backend.game_logic import bond as B
from backend.game_logic import coalition, congress, game_end
from tests.test_congress_of_paris import _boot, _latch, _satisfy_all, _sit, _tick

REPO = Path(__file__).resolve().parents[1]
HOLD = "Europe waits on Paris — no league declares while the Congress sits"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _coalition_tick(w, alarm=None):
    if alarm is not None:
        w.threat_by_target["France"] = alarm
    with _quiet():
        return coalition.process_coalition_turn(w)


def _quiet_board(*, refusers=0):
    """The boot board with the Congress sitting and every great power
    answering it (or all but `refusers` of them), the boot's league spent and
    the cooldown run out — four lesser courts qualify for a league."""
    w = _boot()
    _sit(w)
    if refusers:
        for court in congress.great_powers(w)[:len(congress.great_powers(w)) - refusers]:
            _latch(w, court)
    else:
        _satisfy_all(w)
    w.active_coalition = None
    w.coalition_cooldown = 0
    return w


def _brew_notice(w):
    return next(n for n in w.notifications.get_pending()
                if n.get("type") == coalition.COALITION_BREWING)


# ════════════════════════════════════════════════════════════════════════
# The hold
# ════════════════════════════════════════════════════════════════════════

class TestTheHold:
    def test_a_brew_holds_at_its_last_turn_while_the_congress_sits(self):
        w = _quiet_board()
        assert congress.live_refusers(w) == []
        assert congress.league_waits_on_paris(w) == HOLD
        assert coalition.get_qualifying_nations(w) == ["Ottoman", "Sweden", "Naples", "Sardinia"]
        counts = []
        for _ in range(6):
            _coalition_tick(w, alarm=70)
            counts.append(int(w.coalition_brewing["turns_remaining"]))
            assert not w.active_coalition
        assert counts == [3, 2, 1, 1, 1, 1]
        notice = _brew_notice(w)
        assert notice["title"] == "Coalition Brewing — it waits on Paris"
        assert "They wait on Paris: no league declares while the Congress sits" in notice["message"]
        assert notice["details"]["waits_on_paris"] is True

    def test_the_instant_bar_brews_instead_of_declaring(self):
        w = _quiet_board()
        _coalition_tick(w, alarm=88)
        assert not w.active_coalition
        assert int(w.coalition_brewing["turns_remaining"]) == coalition.BREWING_COUNTDOWN
        _coalition_tick(w, alarm=88)
        assert not w.active_coalition

    def test_two_refusers_lift_it_the_lowered_gate_untouched(self):
        w = _quiet_board(refusers=2)
        assert len(congress.live_refusers(w)) == 2
        assert congress.coalition_gate(w) == 40
        assert congress.league_waits_on_paris(w) == ""
        for _ in range(4):
            _coalition_tick(w, alarm=70)
            if w.active_coalition:
                break
        assert w.active_coalition, "with two refusers the league declares as before"

    def test_a_congress_that_fails_lets_the_league_declare_the_turn_after(self):
        w = _quiet_board()
        for _ in range(4):
            _coalition_tick(w, alarm=70)
        assert int(w.coalition_brewing["turns_remaining"]) == 1 and not w.active_coalition
        table = {court: congress.answer(w, court) for court in congress.great_powers(w)}
        with _quiet():
            congress._dissolve(w, w.current_turn, table, {"key": "staged", "text": "staged"})
        assert congress.league_waits_on_paris(w) == ""
        _coalition_tick(w, alarm=70)
        assert w.active_coalition and not w.coalition_brewing

    def test_the_league_clock_names_the_deadline_if_the_congress_fails(self):
        w = _quiet_board()
        for _ in range(3):
            _coalition_tick(w, alarm=70)
        forecast = coalition.league_forecast(w)
        lift = congress.hold_lifts_in(w)
        assert lift == int(w.congress["ends_turn"]) - int(w.current_turn) + 2
        assert forecast["waits_on_paris"] == HOLD
        assert forecast["declare_turns"] == lift
        line = coalition.league_summary_line(w)
        assert line.startswith("The courts consult now and wait on Paris — no league declares while "
                               "the Congress sits; if it fails, they declare on turn "
                               f"{int(w.current_turn) + lift}:")

    def test_the_surfaces_say_it_waits_on_paris_not_a_countdown(self):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        from backend.game_logic.dispatch import _build_coalition_section
        w = _quiet_board()
        for _ in range(3):
            _coalition_tick(w, alarm=70)
        section = _build_coalition_section(w, "France")
        assert section["brewing"]["waits_on_paris"] == HOLD
        assert _build_balance_of_europe(w)["brewing_waits_on_paris"] == HOLD
        for name in ("dispatch_view.gd", "main.gd"):
            src = (REPO / "godot-client" / "project-sovereign" / "scripts" / name).read_text(encoding="utf-8")
            assert 'brewing.get("waits_on_paris", "")' in src and "A coalition brews — " in src
        led = (REPO / "godot-client" / "project-sovereign" / "scripts" / "diplomatic_ledger.gd").read_text(
            encoding="utf-8")
        assert 'boe.get("brewing_waits_on_paris")' in led

    def test_the_summons_names_the_hold(self):
        w = _boot()
        for court in congress.great_powers(w):
            _latch(w, court)
        result = _sit(w)
        assert ("Europe waits on Paris: while the Congress sits and fewer than two great powers "
                "refuse it, no new league declares against us.") in result["message"]

    def test_dormant_without_a_congress(self):
        w = _boot()
        assert not congress.sitting(w)
        assert congress.league_waits_on_paris(w) == ""
        w.active_coalition = None
        w.coalition_cooldown = 0
        _coalition_tick(w, alarm=88)
        assert w.active_coalition, "no Congress, no hold: the instant bar declares"


# ════════════════════════════════════════════════════════════════════════
# The signing and the page
# ════════════════════════════════════════════════════════════════════════

def _signed_with_a_brew(alarm=76):
    w = _quiet_board()
    for _ in range(3):
        _coalition_tick(w, alarm=70)
    assert w.coalition_brewing
    w.threat_by_target["France"] = alarm
    with _quiet():
        stamped = _tick(w, 9)
    assert [r["cause"] for r in stamped] == [game_end.CAUSE_IMPERIAL_PEACE]
    return w, stamped[0]


class TestTheSigning:
    def test_the_signing_spends_the_alarm_to_the_watch_and_dismisses_the_brew(self):
        w, rec = _signed_with_a_brew()
        assert int(w.threat_level) == coalition.ARMED_PEACE_WATCH == 45
        assert w.coalition_brewing is None
        spent = rec["detail"]["alarm_spent"]
        assert spent == {"alarm_from": 76, "alarm_to": 45,
                         "dismissed": ["Naples", "Ottoman", "Sardinia", "Sweden"]}
        row = [s for s in w.threat_sources_this_turn if s.get("source") == "imperial_peace"]
        assert row and row[-1]["amount"] == -31
        from backend.game_logic.diplomatic_ledger import _threat_source_label
        assert _threat_source_label(w, "imperial_peace") == "The powers signed at Paris"
        assert not [n for n in w.notifications.get_pending()
                    if n.get("type") == coalition.COALITION_BREWING]
        cancelled = [e for e in w.event_log if e.get("type") == "coalition_brewing_cancelled"]
        assert cancelled[-1]["reason"] == "the_imperial_peace"
        from backend.campaign_log import format_event_oneliner
        assert format_event_oneliner(cancelled[-1]) == (
            "The Imperial Peace dismisses the league brewing among Naples, Ottoman Empire, Sardinia "
            "and Sweden — the lesser courts signed nothing")

    def test_an_alarm_under_the_watch_is_never_raised(self):
        w, rec = _signed_with_a_brew(alarm=30)
        assert int(w.threat_level) == 30
        assert rec["detail"]["alarm_spent"]["alarm_from"] == 30
        assert rec["detail"]["alarm_spent"]["alarm_to"] == 30

    def test_the_universal_monarchy_is_not_a_signature(self):
        w = _boot()
        w.threat_by_target["France"] = 70
        with _quiet():
            rec = congress._proclaim(w, w.current_turn, route="universal_monarchy")
        assert rec is not None and "bought_line" not in rec["detail"]
        assert int(w.threat_level) == 70


class TestThePage:
    def test_the_page_names_what_the_peace_buys(self):
        w, rec = _signed_with_a_brew()
        bought = rec["detail"]["bought_line"]
        assert bought == (
            "A peace buys time, not immunity, Sire: it bought the signatures of Britain, Russia, "
            "Austria and Prussia, and Europe's alarm spent from 76 to 45 — the Armed Peace's watch. "
            "The league brewing among Naples, Ottoman Empire, Sardinia and Sweden is dismissed, but "
            "the lesser courts signed nothing and keep their grievances.")
        assert rec["summary"]["congress"]["bought_line"] == bought
        from backend.game_logic.dispatch import _imperial_peace_line
        assert _imperial_peace_line(w).endswith("The order the Emperor made is the order Europe "
                                                "recognizes. " + bought)
        assert congress.stamped_bought_line(w) == bought
        from backend.ai.first_contact import answer_first_contact  # noqa: F401  (the desk's door)
        end = (REPO / "godot-client" / "project-sovereign" / "scripts" / "campaign_end.gd").read_text(
            encoding="utf-8")
        assert 'congress.get("bought_line")' in end

    def test_with_no_brew_the_page_still_names_the_lesser_courts(self):
        w = _quiet_board()
        w.threat_by_target["France"] = 50
        with _quiet():
            rec = _tick(w, 9)[0]
        assert rec["detail"]["bought_line"].endswith(
            "The lesser courts signed nothing and keep their grievances.")


# ════════════════════════════════════════════════════════════════════════
# PC-X69 — the Congress's forced suit reads the league's bond
# ════════════════════════════════════════════════════════════════════════

def _set_pair(w, court, score):
    k = w._make_diplo_key(court, "France")
    w.war_scores[k] = score if k.split("|")[0] == court else -score


def _bonded():
    w = _boot()
    _sit(w)
    with _quiet():
        assert B.mint_bond(w, payer="Britain", member="Austria", enemy="France")["success"]
    return w


class TestPCX69:
    def test_without_a_bond_the_stock_line(self):
        w = _boot()
        _sit(w)
        assert congress.sue_line(w, "Austria") == {"score": -40, "base": -40, "depth": 0, "payer": ""}
        _set_pair(w, "Austria", -45)
        assert congress.court_must_sue(w, "Austria")

    def test_the_bond_deepens_her_sue_line_and_the_table_says_so(self):
        w = _bonded()
        assert congress.sue_line(w, "Austria") == {"score": -49, "base": -40, "depth": 9, "payer": "Britain"}
        _set_pair(w, "Austria", -45)
        assert not congress.court_must_sue(w, "Austria")
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.REFUSES and row["bond_payer"] == "Britain"
        assert row["reason"].endswith("it sues at +49: Britain's bond holds her 9 deeper)")
        price = congress.price(w, "Austria", row)["text"]
        assert price.startswith("win the war to +49 (now +45) — Britain's bond holds her 9 deeper")
        assert ("sign a peace with Austria — Britain's bond costs her 40 at the table (6 in a bilateral "
                "peace); 1,000 gold to her pays it (F1 → Austria → Outbid Britain's Bond)") in price

    def test_beaten_past_it_she_sues_as_her_priced_separate_peace(self):
        w = _bonded()
        _set_pair(w, "Austria", -60)
        assert congress.court_must_sue(w, "Austria")
        row = congress.answer(w, "Austria")
        assert row["stance"] == congress.SUES
        assert row["reason"].endswith("; she breaks Britain's bond to sue — a broken bargain Britain "
                                      "will hold against her")
        with _quiet():
            proposal = AI.process_diplomatic_phase("Austria", w)
        assert proposal["congress_recognition"] and proposal["proposal_type"] == "peace"
        dialogue = AI.build_ai_proposal_dialogue(proposal, w)
        told = ("Austria breaks Britain's bond to sue — a separate peace inside its term (200g a turn, "
                "10 turns left) is a broken bargain Britain will hold against her")
        assert told in dialogue["popup_payload"]["clauses"]
        assert told + "." in dialogue["talleyrand_text"]

    def test_a_held_capital_still_forces_it(self):
        w = _bonded()
        _set_pair(w, "Austria", -10)
        w.regions[w.get_nation_capital("Austria")].controller = "France"
        w.invalidate_active_nations_cache()
        assert congress.court_must_sue(w, "Austria")
        assert "she breaks Britain's bond to sue" in congress.answer(w, "Austria")["reason"]

    def test_her_signed_suit_is_reneged_against_her(self):
        from backend.game_logic.instruments import has_renege_grievance, process_instruments
        w = _bonded()
        _set_pair(w, "Austria", -60)
        with _quiet():
            w._ratify_treaty({"type": "peace", "proposer_nation": "Austria", "target_nation": "France",
                              "sweeteners": [], "demands": [], "clauses": ["congress_recognition"],
                              "congress_recognition": True})
            events = process_instruments(w)
        assert [(e["type"], e["breaker"], e["victim"]) for e in events if e.get("kind") == "bond"] == [
            ("sponsorship_reneged", "Austria", "Britain")]
        assert has_renege_grievance(w, "Britain", "Austria")
        assert congress.answer(w, "Austria")["stance"] == congress.RECOGNIZES

    def test_a_truce_letter_breaks_nothing_and_says_nothing(self):
        w = _bonded()
        assert B.letter_line(w, "Austria", "France")
        assert B.letter_line(w, "Russia", "France") == ""


# ════════════════════════════════════════════════════════════════════════
# DDB-X4 — the dormancy arms flip live seams
# ════════════════════════════════════════════════════════════════════════

def _tool():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_ge3_series_arms", REPO / "tools" / "_ge3_series_arms.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _baseline():
    src = (REPO / "tests" / "test_ai_intent_threat_migration.py").read_text(encoding="utf-8")
    start = src.index("BASELINE_SERIES = [")
    end = src.index("]", start)
    return list(ast.literal_eval(src[start + len("BASELINE_SERIES = "):end + 1]))


class TestDDBX4:
    def test_every_arm_flips_a_live_seam_the_new_rules_among_them(self):
        import importlib
        tool = _tool()
        for key, (module, name, down) in tool.LEVERS.items():
            mod = importlib.import_module(module)
            assert callable(getattr(mod, name, None)), f"{key}: {module}.{name} is not a live seam"
            assert not name.isupper(), f"{key}: {name} is a module constant, not a seam"
            eval("lambda *a, **k: " + down, {"_mod": mod})       # the down answer compiles
        named = {name for _m, name, _d in tool.LEVERS.values()}
        assert {"league_waits_on_paris", "the_signing_spends", "sue_line"} <= named
        assert {"THE_CONGRESS_SITS", "THE_CONGRESS_LOWERS_THE_GATE"}.isdisjoint(named)

    def test_the_dormancy_proof_re_reads_byte_identical(self):
        rec = json.loads((REPO / "tools" / "_ge3_series_arms.json").read_text(encoding="utf-8"))
        baseline = _baseline()
        assert rec["recorded"] == baseline
        assert set(rec["arms"]) >= {"0", "S", "W", "T", "Y", "ALL"}
        assert rec["arm_levers"]["0"] == [] and set(rec["arm_levers"]["ALL"]) == set(_tool().LEVERS)
        for arm, row in rec["arms"].items():
            assert row["series"] == baseline, arm
            assert row["first_divergence_vs_recorded"] is None, arm
            assert row["congress_writes"] == 0, arm
            reach = row["reach"]
            assert int(reach.get("hold_reads", 0)) > 0, f"{arm}: the hold was never read"
            for bite in ("hold_bites", "signings", "bonded_sue_lines"):
                assert int(reach.get(bite, 0)) == 0, (arm, bite)


# ════════════════════════════════════════════════════════════════════════
# The morning of the peace — the PRESS arm, driven
# ════════════════════════════════════════════════════════════════════════

_HELD_DOWN = ("backend.game_logic.congress:league_waits_on_paris=\"\"",
              "backend.game_logic.congress:the_signing_spends={}")


def _drive_press(tmp_path, name, *seams):
    env = dict(os.environ, PYTHONHASHSEED="0")
    for key in ("PYTHONIOENCODING", "SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
    extra = [arg for seam in seams for arg in ("--seam", seam)]
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "playtest_driver.py"), "--name", name,
         "--seed", "historical", "--script", str(REPO / "tools" / "playtest_scripts" / "ge3_pressburg.json"),
         "--from-save", str(REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ge3_pressburg.json"),
         "--turns", "12", "--diplomacy", "accept", "--stop-on-ending",
         "--out", str(tmp_path), "--fresh", *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=900, env=env, cwd=str(REPO))
    run = tmp_path / name
    assert (run / "meta.json").is_file(), proc.stderr[-2000:]
    return (json.loads((run / "meta.json").read_text(encoding="utf-8")),
            (run / "digest.md").read_text(encoding="utf-8"))


def _last_turn(digest):
    return digest.split("\n## Turn ")[-1]


def _ledger_threat(block):
    line = next(ln for ln in block.splitlines() if ln.startswith("- LEDGER"))
    return int(line.split("threat ")[1].split()[0])


class TestTheMorningOfThePeace:
    def test_the_press_arm_signs_with_no_league_formed_the_alarm_at_the_watch(self, tmp_path):
        meta, digest = _drive_press(tmp_path, "vp2-press")
        assert meta["status"] == "ending-reached"
        assert "ENDING — THE IMPERIAL PEACE" in digest
        assert "A coalition has formed against France" not in digest
        assert "coalition_declared" not in digest
        assert "Ottoman has declared war on France" not in digest
        morning = _last_turn(digest)
        assert _ledger_threat(morning) == 45
        assert "A peace buys time, not immunity" in morning
        assert "The Imperial Peace dismisses the league brewing among" in morning

    def test_with_the_rule_held_down_the_gap_returns(self, tmp_path):
        """The sensitivity arm: the same board with the hold and the spend held
        down reproduces the gap the econ_gate archive recorded — the league of
        the lesser courts declares on the Congress's eighth day and the alarm
        reads above the watch the morning after the signing."""
        meta, digest = _drive_press(tmp_path, "vp2-press-down", *_HELD_DOWN)
        assert meta["status"] == "ending-reached"
        assert "A coalition has formed against France! Members: Ottoman, Sardinia, Sweden." in digest
        assert _ledger_threat(_last_turn(digest)) > 45
        assert "A peace buys time, not immunity" in digest     # the page is not a lever
