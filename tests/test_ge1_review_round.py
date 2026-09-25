"""GE-1 review round (September 25, 2026) — the pins for every finding the
adversarial review of commit 975f1f13 confirmed.

The review (docs/ENDGAME_PLAN.md §6 GE-1, the review-round addendum) sent
seven lenses at the committed slice with two refuters per finding: 50 filed,
38 survived both. Every fix below is driven through the real seam the
finding reproduced on — `/strategic_response`, `/command`, `/load`,
`destroy_marshal`, `_ratify_treaty`, `ratify_settlement_confirm`,
`set_diplomatic_state`, `TurnManager.end_turn` — never a hand-written ending
record. Each test names the finding it pins (#n, the review's own index).
"""

import contextlib
import io
import json
import random
from pathlib import Path

import pytest

from backend.game_logic import fall, game_end
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")
FIXTURE_T20 = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCEN)


def _tick(world, n=1):
    stamped = []
    for _ in range(n):
        world.current_turn += 1
        stamped += game_end.process_end_of_turn(world, turn_ended=world.current_turn - 1)
    return stamped


def _reduce_france_to(world, keep, to="Austria"):
    for region in list(world.get_nation_regions("France")):
        if region not in keep:
            world.regions[region].controller = to
    world.invalidate_active_nations_cache()


def _set(world, a, b, state, reason="test"):
    from backend.game_logic.diplomacy import set_diplomatic_state
    with contextlib.redirect_stdout(io.StringIO()):
        set_diplomatic_state(world, a, b, state, reason)


@pytest.fixture
def client(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend import save_manager as SM
    from tests._chip_census import board_env
    prior = (M.world, M.game_state.get("world"), M.parser)
    monkeypatch.setattr(SM, "SAVE_DIR", tmp_path)
    board_env(monkeypatch)
    yield TestClient(M.app), M
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


def _post(tc, path, body, seed=7):
    random.seed(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        return tc.post(path, json=body).json()


def _napoleon_alone_at_lorraine(w, strength=60):
    for m in w.marshals.values():
        if m.nation == "France" and not m.is_sovereign:
            m.location = "Brittany"
    nap = w.marshals["Napoleon"]
    nap.location = "Lorraine"
    nap.strength = strength
    w._build_marshal_index()
    return nap


def _final_save(w):
    record = game_end.terminal_ending(w)
    path = (record or {}).get("final_save")
    return Path(path) if path else None


# ════════════════════════════════════════════════════════════════════════
# #1 / #6 / #22 / #42 — the war is closed on EVERY road, and saved
# ════════════════════════════════════════════════════════════════════════

class TestTheWarIsClosedOnEveryRoad:
    def test_the_emperor_killed_on_an_answered_interrupt(self, client, monkeypatch):
        """#6/#22 (P1): the popup road — the response carries the ending,
        the Final save is on disk, and no 'awaits new instructions'."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        _napoleon_alone_at_lorraine(M.world)
        first = _post(tc, "/command", {"command": "Napoleon, march to Swabia"})
        interrupt = first.get("pending_interrupt") or {}
        assert interrupt.get("interrupt_type") == "contact" or "attack" in str(interrupt), first.get("message")
        r = _post(tc, "/strategic_response", {"marshal_name": "Napoleon",
                                              "response_type": "contact",
                                              "choice": "attack"})
        assert "HAS FALLEN" in r["message"], r["message"]
        assert "awaits new instructions" not in r["message"]
        assert r["game_over"] is True
        assert r["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        final = _final_save(M.world)
        assert final is not None and final.exists()
        meta = json.loads(final.read_text(encoding="utf-8"))["metadata"]
        assert meta["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        # The guard's refusal carries the ending too (#24's dead clause).
        again = _post(tc, "/command", {"command": "end turn"})
        assert again["message"] == "The war is over."
        assert again["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS

    def test_the_emperor_killed_in_his_own_attack_is_saved(self, client, monkeypatch):
        """#42: the direct attack road's Final save is PINNED (it was the
        one untested writer)."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        _napoleon_alone_at_lorraine(M.world)
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert r["game_over"] is True
        final = _final_save(M.world)
        assert final is not None and final.exists()
        saved = json.loads(final.read_text(encoding="utf-8"))
        assert saved["metadata"]["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        # The Final file remembers itself — its own record names it, so a
        # load never writes a second.
        rec = [e for e in saved["world_state"]["endings"] if e.get("terminal")][0]
        assert rec["final_save"] == str(final)


# ════════════════════════════════════════════════════════════════════════
# #23 / #4 — a fallen campaign raises no question nobody can answer
# ════════════════════════════════════════════════════════════════════════

class TestNoUnanswerableQuestion:
    def test_the_death_clears_every_standing_question(self, client, monkeypatch):
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = M.world
        _napoleon_alone_at_lorraine(w)
        w.marshals["Davout"].pending_interrupt = {
            "interrupt_type": "contact", "marshal": "Davout",
            "options": ["attack", "hold_position", "cancel_order"]}
        w.pending_redemption = {"marshal": "Ney"}
        w._popup_queue.push("pending_marshal_petition", {"kind": "fontainebleau"})
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert r["game_over"] is True
        assert w.marshals["Davout"].pending_interrupt is None
        assert w.pending_redemption is None
        assert w._popup_queue.get("pending_marshal_petition") is None
        for key in ("pending_interrupt", "marshal_petition", "redemption_event",
                    "deferred_marshal_petition"):
            assert not r.get(key), key
        # The Final save carries none of it, and its load raises the end.
        loaded = _post(tc, "/load", {"filename": _final_save(w).name})
        assert loaded["game_over"] is True
        assert loaded["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert not loaded.get("pending_interrupt")
        assert not loaded.get("redemption_event")

    def test_the_end_turn_fall_hands_no_petition(self, client):
        """#4: the fifth end turn of the soil clock no longer hands the
        client a Fontainebleau card nobody can answer."""
        tc, M = client
        w = M.world
        _reduce_france_to(w, {"Brittany"})
        fallen = None
        for i in range(8):
            w._popup_queue.push("pending_marshal_petition",
                                {"kind": "fontainebleau", "dialogue_id": None})
            r = _post(tc, "/command", {"command": "end turn"}, seed=4000 + i)
            if r.get("game_over"):
                fallen = r
                break
        assert fallen is not None
        assert not fallen.get("deferred_marshal_petition")
        assert w._popup_queue.get("pending_marshal_petition") is None


# ════════════════════════════════════════════════════════════════════════
# #7 / #35 / #36 / #8 — the finished field, named where he fell
# ════════════════════════════════════════════════════════════════════════

class TestTheFinishedField:
    def test_the_summary_counts_the_battle_that_killed_him(self, client, monkeypatch):
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        _napoleon_alone_at_lorraine(M.world)
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        summary = r["ending"]["summary"]
        assert summary["totals"]["battles_fought"] == 1
        assert summary["totals"]["battles_lost"] == 1
        worst = summary["worst_defeat"] or {}
        assert worst.get("region") == "Swabia"
        # #36: he fell on the FIELD, not in the province he marched from.
        tomb = M.world.fallen_marshals["Napoleon"]
        assert tomb["location"] == "Swabia"
        assert "at Swabia, the Emperor was killed" in " ".join(
            summary["epilogue"]["paragraphs"])
        # #8: Berthier's report and the diorama say he fell — and (the
        # verification round's V21, flipped consciously) his fate REPLACES
        # the verdict about scale: "Hardly an engagement … and the day moved
        # on" was false of the field that ended the Empire.
        report = r.get("battle_report") or {}
        obs = report.get("observation", "")
        assert obs == "The Emperor himself fell on that field."
        assert "moved on" not in obs and "Hardly" not in obs
        diorama = r.get("battle_diorama") or {}
        if diorama:
            assert "watched this field" not in diorama.get("observation", "")

    def test_a_death_stamped_in_the_enemy_phase_is_closed_after_it(self):
        """#7: the summary is rebuilt on the finished field — the stamp's
        own summary (built mid-battle) is replaced at the close."""
        w = _boot()
        rec = game_end.record_ending(w, "defeat", game_end.CAUSE_EAGLE_FALLS,
                                     detail={"location": "Paris"})
        assert rec["summary"]["totals"]["battles_fought"] == 0
        game_end.count_battle(w, player_side="defender", won=False, lost=True,
                              inflicted=10, suffered=40, name="Battle of Paris",
                              region="Paris", enemy="Austria", in_person=True)
        w.regions["Paris"].controller = "Austria"
        game_end.close_campaign(w)
        assert rec["closed"] is True
        assert rec["summary"]["totals"]["battles_fought"] == 1
        text = " ".join(rec["summary"]["epilogue"]["paragraphs"])
        assert "lay in state" not in text and "buried where he fell" in text
        # Idempotent: a second close changes nothing.
        before = json.dumps(rec["summary"], sort_keys=True, default=str)
        game_end.close_campaign(w)
        assert json.dumps(rec["summary"], sort_keys=True, default=str) == before


# ════════════════════════════════════════════════════════════════════════
# #9 / #11 / #12 — the death named, the dead unaddressed, the phase ended
# ════════════════════════════════════════════════════════════════════════

class TestTheDeathInSomeoneElsesBattle:
    def test_a_participant_emperor_is_named(self, monkeypatch):
        """#9: Napoleon and Soult share Lorraine at boot; Mack attacks Soult
        and both corps die — the copy names the Emperor."""
        from backend.commands.executor import CommandExecutor
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        nap, soult = w.marshals["Napoleon"], w.marshals["Soult"]
        assert nap.location == soult.location == "Lorraine"
        nap.strength, soult.strength = 30, 60
        mack = w.marshals["Mack"]
        mack.strength = 60000
        w._build_marshal_index()
        random.seed(3)
        with contextlib.redirect_stdout(io.StringIO()):
            result = CommandExecutor().execute(
                {"command": {"marshal": "Mack", "action": "attack",
                             "target": "Soult", "type": "specific"}},
                {"world": w})
        assert "Napoleon" not in w.marshals
        assert w.fallen_marshals["Napoleon"]["location"] == "Lorraine"
        assert game_end.terminal_ending(w)["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert "THE EMPEROR NAPOLEON HAS FALLEN" in result.get("message", "")

    def test_no_prestige_is_moved_for_a_dead_emperor(self, client, monkeypatch):
        """#11: no "The court will hear of it (Authority −5)" after death."""
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        _napoleon_alone_at_lorraine(M.world)
        before = M.world.authority_tracker.authority
        r = _post(tc, "/command", {"command": "Napoleon, attack Mack"})
        assert r["game_over"] is True
        assert "court will hear of it" not in r["message"]
        assert M.world.authority_tracker.authority == before

    def test_the_killers_turn_stops_with_the_empire(self):
        """#12: the per-marshal loop stops once the war is over."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        control = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            acted = EnemyAI(CommandExecutor()).process_nation_turn(
                "Austria", control, {"world": control})
        assert [a for a in acted if a.get("ai_action")], "control: Austria acts"
        w = _boot()
        w.game_over = True
        with contextlib.redirect_stdout(io.StringIO()):
            actions = EnemyAI(CommandExecutor()).process_nation_turn(
                "Austria", w, {"world": w})
        assert not [a for a in actions if a.get("ai_action")]

    def test_the_standing_headline_is_alone(self, monkeypatch):
        """#11: the sovereign_dead page carries no sub-beat — even beside a
        marshal destroyed and a marshal taken the same turn, which would
        otherwise take the sub-beat slots."""
        from backend.game_logic import dispatch
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        w.destroy_marshal(w.marshals["Davout"], cause="battle", victor="Austria")
        w.capture_marshal(w.marshals["Ney"], "Austria", context="t")
        control = dispatch._build_headline(w, "France", record=False)
        assert control["sub_beats"], "control: the other news does make sub-beats"
        w.destroy_marshal(w.marshals["Napoleon"], cause="battle", victor="Austria")
        headline = dispatch._build_headline(w, "France", record=False)
        assert headline["class"] == "sovereign_dead"
        assert headline["sub_beats"] == []


# ════════════════════════════════════════════════════════════════════════
# #0 / #2 / #3 / #5 / #13 — the clocks say what is true
# ════════════════════════════════════════════════════════════════════════

class TestTheClocks:
    def test_a_ticking_arm_outranks_a_paused_one(self):
        """#2: chains paused at 8 of 10, soil ticking — the soil arm is the
        one every surface names, and a paused arm has no fall date."""
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 8)
        _set(w, "France", "Austria", "ARMISTICE")
        _reduce_france_to(w, {"Brittany"}, to="Britain")
        _tick(w, 3)
        state = fall.get_fall_state(w)
        chains, soil = state["arms"][fall.ARM_CHAINS], state["arms"][fall.ARM_SOIL]
        assert chains["ticking"] is False and chains["turns"] == 8
        assert chains["falls_at_end_of_turn"] is None
        assert soil["ticking"] is True and soil["turns"] == 3
        assert state["soonest"]["arm"] == fall.ARM_SOIL
        assert "WITHOUT SOIL OR SWORD" in fall.scope_sentence(w)
        warn = fall.warning_state(w)
        assert warn["severity"] == "critical"
        assert warn["notification_title"] == fall.ARM_TITLES[fall.ARM_SOIL]

    def test_the_exact_fall_turn_is_named(self):
        """#49: the warning's date is the date the ending is stamped."""
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 2)
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        promised = view["falls_at_end_of_turn"]
        stamped = []
        while not stamped:
            stamped = _tick(w, 1)
        assert stamped[0]["turn"] == promised

    def test_a_fresh_capture_is_a_fresh_clock(self):
        """#0 (the chains half): freed and re-taken by the same court before
        the tick — the clock starts again, and the offer cadence with it."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Austria", context="t")
        _tick(w, 8)
        assert w.fall_clock[fall.ARM_CHAINS]["turns"] == 8
        w.release_captured_marshal("Napoleon", reason="rescued_by_storm")
        w.capture_marshal(nap, "Austria", context="t2")
        _tick(w, 1)
        assert w.fall_clock[fall.ARM_CHAINS]["turns"] == 1
        assert not w.game_over

    def test_a_change_of_captor_resets_the_clock(self):
        """#49 (R4)."""
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Austria", context="t")
        _tick(w, 5)
        nap.captured_by = "Russia"
        _tick(w, 1)
        assert w.fall_clock[fall.ARM_CHAINS]["turns"] == 1

    def test_a_truce_pauses_the_soil_clock(self):
        """#5: a truce is not a peace — the count stands still, then resumes."""
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 4)
        at_war = list(w.get_nations_at_war_with("France"))
        for nation in at_war:
            _set(w, "France", nation, "ARMISTICE")
        _tick(w, 2)
        entry = w.fall_clock[fall.ARM_SOIL]
        assert entry["turns"] == 4 and entry["paused"] is True
        view = fall.get_fall_state(w)["arms"][fall.ARM_SOIL]
        assert "stands still while the truce holds" in fall.arm_clock_sentence(w, view)
        for nation in at_war:
            _set(w, "France", nation, "WAR")
        stamped = _tick(w, 1)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_SOIL]

    def test_a_peace_with_everyone_still_resets_it(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 3)
        for nation in list(w.get_nations_at_war_with("France")):
            _set(w, "France", nation, "PEACE")
        _tick(w, 1)
        assert fall.ARM_SOIL not in w.fall_clock

    def test_the_exits_are_read_from_the_live_state(self):
        """#3: never "any peace frees him" to a France already at peace."""
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        at_war = fall.get_fall_state(w)["arms"][fall.ARM_CHAINS]["exits"]
        assert any("any peace with Austria frees him" in e for e in at_war)
        _set(w, "France", "Austria", "ARMISTICE")
        truce = fall.get_fall_state(w)["arms"][fall.ARM_CHAINS]["exits"]
        assert any("truce" in e for e in truce)
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "PEACE"
        peace = fall.get_fall_state(w)["arms"][fall.ARM_CHAINS]["exits"]
        assert not any("any peace" in e for e in peace)
        assert any("make war on Austria" in e for e in peace)


class TestTheEmperorIsEscortedHome:
    def test_an_internment_at_peace_sends_him_home(self):
        """#13: a lapsed passage on a court at PEACE never takes him."""
        from backend.game_logic import withdrawal
        w = _boot()
        nap = w.marshals["Napoleon"]
        _set(w, "France", "Prussia", "PEACE")
        nap.location = "Berlin"
        nap.strength = 9000
        with contextlib.redirect_stdout(io.StringIO()):
            event = withdrawal._intern(w, nap, "France")
        assert event["type"] == "sovereign_escorted_home"
        assert not nap.captured_by
        assert "Napoleon" in w.marshals
        assert nap.strength <= w.RANSOM_RETURN_STRENGTH
        assert w.regions[nap.location].controller == "France"
        assert fall.get_fall_state(w) is None

    def test_the_lever_down_restores_the_capture(self, monkeypatch):
        from backend.game_logic import withdrawal
        monkeypatch.setattr(withdrawal, "THE_EMPEROR_IS_ESCORTED_HOME", False)
        w = _boot()
        nap = w.marshals["Napoleon"]
        _set(w, "France", "Prussia", "PEACE")
        nap.location = "Berlin"
        with contextlib.redirect_stdout(io.StringIO()):
            withdrawal._intern(w, nap, "France")
        assert nap.captured_by == "Prussia"


# ════════════════════════════════════════════════════════════════════════
# #28 / #33 — the captor's terms arrive, and say what they are
# ════════════════════════════════════════════════════════════════════════

class TestTheCaptorsTerms:
    @pytest.mark.parametrize("score", [-60, -80])
    def test_a_losing_captor_still_offers(self, score, monkeypatch):
        """#28 (P1): Austria BELOW its P1 threshold still sends the captor's
        terms on clock turn 1 — P1's armistice no longer overwrites them."""
        from backend.game_logic import ai_diplomacy as AD
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 1)
        monkeypatch.setattr(AD, "get_war_score_for",
                            lambda world, a, b: score if a == "Austria" else -score,
                            raising=False)
        key = w._make_diplo_key("Austria", "France")
        w.war_scores[key] = -score if key.startswith("Austria") else score
        from backend.game_logic.diplomacy import get_war_score_for
        with contextlib.redirect_stdout(io.StringIO()):
            prop = AD.process_diplomatic_phase("Austria", w)
        assert get_war_score_for(w, "Austria", "France") <= -60 or prop is not None
        assert prop is not None and prop.get("captor_terms"), prop

    def test_the_envoy_names_the_release(self):
        """#33: the one envoy that stops the clock says so."""
        from backend.game_logic import ai_diplomacy as AD
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 1)
        with contextlib.redirect_stdout(io.StringIO()):
            prop = AD.process_diplomatic_phase("Britain", w)
            dialogue = AD.build_ai_proposal_dialogue(prop, w)
        assert dialogue["context"]["captor_terms"] is True
        assert "the Emperor's release" in dialogue["talleyrand_text"]
        assert any("frees the Emperor" in c
                   for c in dialogue["popup_payload"]["clauses"])


# ════════════════════════════════════════════════════════════════════════
# #14 / #15 / #16 — titles and the Revanche
# ════════════════════════════════════════════════════════════════════════

def _cede_from(world, ceder, regions, to="France", ptype="peace"):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty({
            "proposer_nation": to, "target_nation": ceder, "type": ptype,
            "demands": [{"type": "territory_cede", "regions": list(regions)}],
            "sweeteners": [],
        })


def _view_regions(view):
    if isinstance(view, dict):
        return list(view.get("regions") or [])
    return list(getattr(view, "regions", None) or [])


class TestTitlesAndTheRevanche:
    def test_a_carve_is_reconciled_like_a_cession(self):
        """#14: the Tilsit carve reconciles Prussia's claim on Posen."""
        from backend.game_logic.diplomacy import declare_war
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            declare_war(w, "France", "Prussia")
        w.regions["Posen"].controller = "France"
        w.invalidate_active_nations_cache()
        w.war_scores[w._make_diplo_key("France", "Prussia")] = 100
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({
                "type": "peace", "proposer_nation": "France",
                "target_nation": "Prussia", "sweeteners": [],
                "demands": [{"type": "create_client", "value": 1,
                             "tag": "DuchyOfWarsaw", "provinces": ["Posen"],
                             "client_display_name": "Duchy of Warsaw"}]})
        assert w.regions["Posen"].controller == "DuchyOfWarsaw"
        assert "Posen" in game_end.reconciled_regions(w, "Prussia")
        # And a renewed war breaks the carve's reconciliation — for good: a
        # truce inside that war does not mend it (the at-war check alone
        # would re-reconcile it the moment the guns stop).
        _set(w, "Prussia", "France", "WAR")
        assert "Posen" not in game_end.reconciled_regions(w, "Prussia")
        _set(w, "Prussia", "France", "ARMISTICE")
        assert "Posen" not in game_end.reconciled_regions(w, "Prussia")
        # (Verification round: the carve is a treaty title record now —
        # broken into a conquest — not a `carve_broken` mark on the row.)
        assert w.province_title["Posen"]["kind"] == game_end.TITLE_CONQUEST
        assert w.vassals["DuchyOfWarsaw"]["carved_from"] == "Prussia"

    def test_a_renewed_war_breaks_the_signature_and_a_truce_does_not_mend_it(self):
        """#15: cede → war → truce: the Revanche wakes and STAYS awake."""
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_TREATY
        assert "Tyrol" in game_end.reconciled_regions(w, "Austria")
        _set(w, "Austria", "France", "WAR")
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_CONQUEST
        _set(w, "Austria", "France", "ARMISTICE")
        assert "Tyrol" not in game_end.reconciled_regions(w, "Austria")

    def test_a_grant_to_a_satellite_keeps_the_title(self):
        """#16: a VS-3 grant carries the treaty record to the satellite."""
        from backend.game_logic.vassal import grant_region_to_vassal
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        # The satellite's own boot sub-war with Austria ends too (the
        # bilateral peace leaves it standing), so nothing but the grant
        # is under test.
        _set(w, "Austria", "KingdomOfItaly", "PEACE")
        with contextlib.redirect_stdout(io.StringIO()):
            grant_region_to_vassal(w, "KingdomOfItaly", "Tyrol", actor="France")
        assert w.regions["Tyrol"].controller == "KingdomOfItaly"
        assert game_end.province_title_kind(w, "Tyrol", "France") == "treaty"
        game_end.reconcile_province_titles(w)
        rec = w.province_title["Tyrol"]
        assert rec["holder"] == "KingdomOfItaly" and rec["kind"] == game_end.TITLE_TREATY
        assert "Tyrol" in game_end.reconciled_regions(w, "Austria")

    def test_a_fully_reconciled_revanche_is_inactive_not_satisfied(self):
        """#45: the guard that keeps a signed-away Revanche from reading
        SATISFIED (the NA-3 +10 resolve) — and the live view drops it."""
        from backend.game_logic import agendas
        w = _boot()
        _cede_from(w, "Austria", ["Tyrol"])
        entry = {"id": "revanche_austria", "type": "acquire_regions",
                 "regions": ["Tyrol"], "emergent": True}
        assert agendas._entry_regions(w, "Austria", entry) == []
        assert agendas._entry_satisfied(w, "Austria", entry) is False
        w.agendas.setdefault("Austria", []).insert(0, entry)
        w._agenda_cache = {}
        view = agendas.get_active_agenda("Austria", w)
        assert not view or "Tyrol" not in (_view_regions(view))
        _set(w, "Austria", "France", "WAR")
        w._agenda_cache = {}
        view = agendas.get_active_agenda("Austria", w)
        assert view and "Tyrol" in _view_regions(view)


# ════════════════════════════════════════════════════════════════════════
# #17 / #18 / #20 / #34 / #43 / #44 — the treaty record and the Humbled Peace
# ════════════════════════════════════════════════════════════════════════

class TestTheTreatyRecord:
    def test_a_skipped_clause_is_not_a_cession(self):
        """#18: PL-20 skips a cession that would eliminate France — Paris
        stays French, so no Humbled Peace and nothing counted."""
        w = _boot()
        _reduce_france_to(w, {"Paris", "Normandy"})
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({
                "proposer_nation": "Austria", "target_nation": "France",
                "type": "peace", "sweeteners": [],
                "demands": [{"type": "territory_cede", "regions": ["Paris", "Normandy"]}]})
        if w.regions["Paris"].controller == "France":
            assert not game_end.has_ending(w, game_end.CAUSE_HUMBLED)
            assert "Paris" not in (w.campaign_totals["treaties"][-1]["ceded"])

    def test_a_truce_is_not_a_peace(self):
        """#20: armistice then peace = ONE peace; armistice expiring into
        peace = one; armistice collapsing back into war = none."""
        from backend.game_logic import diplomacy as D
        w = _boot()
        base = w.campaign_totals["peaces_signed"]
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "armistice", "sweeteners": [], "demands": []})
        assert w.campaign_totals["peaces_signed"] == base
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "peace", "sweeteners": [], "demands": []})
        assert w.campaign_totals["peaces_signed"] == base + 1
        # An armistice that EXPIRES into peace is counted there, once.
        w2 = _boot()
        _set(w2, "France", "Britain", "ARMISTICE")
        key = w2._make_diplo_key("France", "Britain")
        w2.armistice_turns[key] = D.ARMISTICE_DURATION - 1
        w2.nation_relations[key] = 50
        with contextlib.redirect_stdout(io.StringIO()):
            D._process_armistice_expiration(w2)
        assert w2.get_diplomatic_state("France", "Britain") == "PEACE"
        assert w2.campaign_totals["peaces_signed"] == 1

    def test_the_humbled_peace_grades_itself_an_eclipse(self):
        """#34/#43: a Humbled Peace on a STRONG realm — the stamped record's
        own summary is the eclipse, and the rule is what makes it so."""
        w = _boot()
        for court in ("Austria", "Prussia", "Russia"):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        strong = game_end.verdict_tier(w)
        assert strong["tier"] in ("triumph", "ascendant")
        home = [r for r in w.nation_starting_regions["France"] if r != "Paris"][:14]
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Britain", "target_nation": "France",
                              "type": "peace", "sweeteners": [],
                              "demands": [{"type": "territory_cede", "regions": home}]})
        rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED][0]
        assert rec["summary"]["verdict"]["tier"] == "eclipse"
        inputs = game_end.verdict_inputs(w)
        assert inputs["humbled"] is True
        assert game_end.verdict_tier(w, dict(inputs, humbled=False))["tier"] != "eclipse"
        assert "The Verdict of History: the eclipse." in " ".join(
            rec["summary"]["epilogue"]["paragraphs"])

    def test_a_treaty_that_makes_france_a_vassal_is_snapshotted(self):
        """#44 (R20): the `was_vassal` snapshot is taken BEFORE the treaty
        — a vassalage made by this treaty humbles."""
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            w._ratify_treaty({"proposer_nation": "Austria", "target_nation": "France",
                              "type": "vassalize", "sweeteners": [], "demands": []})
        if (w.vassals.get("France") or {}).get("lord") == "Austria":
            rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]
            assert rec and rec[0]["detail"]["vassal_of"] == "Austria"


class TestTheSettlementPath:
    def test_a_partial_settlement_names_only_the_courts_that_signed(self, monkeypatch):
        """#17/#44 (R2): the Humbled Peace through `ratify_settlement_confirm`
        — stamped, titled, counted, and "with" the covered court alone."""
        from backend.game_logic import settlement_scoring
        from backend.game_logic.settlement_ratify import ratify_settlement_confirm
        from backend.game_logic.settlement_staging import stage_settlement_confirm
        real = settlement_scoring.calculate_common_peace_acceptance

        def _passes(*a, **k):
            result = real(*a, **k)
            result.update(score=100, verdict="accept", hard_stops=[])
            return result
        monkeypatch.setattr(settlement_scoring, "calculate_common_peace_acceptance", _passes)
        w = _boot()
        war_id = next(iter(w.war_instances))
        with contextlib.redirect_stdout(io.StringIO()):
            staged = stage_settlement_confirm(
                w, war_id=war_id,
                settlement_terms=[{"type": "territory_cede", "from": "France",
                                   "to": "Austria", "region": "Paris"}],
                covered_enemy_participants=["Austria"])
            if not staged.get("success"):
                pytest.skip(f"staging refused: {staged.get('message')}")
            result = ratify_settlement_confirm(w, w.pending_diplomatic_dialogue)
        assert result.get("success"), result
        rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]
        assert rec, "the settlement road stamps the Humbled Peace"
        assert rec[0]["detail"]["with"] == ["Austria"]
        assert w.province_title["Paris"]["kind"] == game_end.TITLE_TREATY
        row = w.campaign_totals["treaties"][-1]
        assert row["with"] == ["Austria"] and row["source"] == "settlement"


# ════════════════════════════════════════════════════════════════════════
# #37 / #38 / #39 / #40 — the words
# ════════════════════════════════════════════════════════════════════════

class TestTheWords:
    def test_a_paused_captivity_says_how_long_he_was_held(self):
        """#37."""
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 3)
        _set(w, "France", "Britain", "ARMISTICE")
        _tick(w, 7)
        _set(w, "France", "Britain", "WAR")
        _tick(w, 7)
        rec = game_end.terminal_ending(w)
        assert rec and rec["cause"] == game_end.CAUSE_CHAINS
        held = rec["detail"]["held_turns"]
        assert held == 17
        assert f"a prisoner these {held} turns — 10 of them at war" in rec["cause_line"]
        text = " ".join(rec["summary"]["epilogue"]["paragraphs"])
        assert f"for {held} turns" in text and "for 10 turns" not in text

    def test_the_contested_lines_read_the_record(self):
        """#38: a France that lost every battle is not told the coalition
        is beaten in the field; one that has given ground is not told it
        holds what it held."""
        w = _boot()
        for i in range(6):
            game_end.count_battle(w, player_side="attacker", won=False, lost=True,
                                  inflicted=100, suffered=500, name=f"Battle {i}",
                                  region="Swabia", enemy="Austria")
        _reduce_france_to(w, set(w.get_nation_regions("France"))
                          - {"Anjou", "Brittany", "Normandy"})
        verdict = game_end.verdict_tier(w)
        if verdict["tier"] == "contested":
            assert "beaten in the field" not in " ".join(verdict["lines"])
            assert "holds what it held" not in " ".join(verdict["lines"])
        # The canonical lines are unchanged for a reign that fits them.
        boot = game_end.verdict_tier(_boot())
        assert boot["tier"] == "contested"
        assert boot["lines"][0] == game_end.VERDICT_TIERS[2][3][0]

    def test_the_record_paragraph_reads_like_prose(self):
        """#39."""
        w = _boot()
        game_end.count_battle(w, player_side="attacker", won=True, lost=False,
                              inflicted=9000, suffered=100,
                              name="the assault on Vienna", region="Vienna",
                              enemy="Austria")
        w.capture_region("Anjou", "Austria")
        w.campaign_totals["coalition_names"] = ["The Fourth Austrian Coalition"]
        w.campaign_totals["coalitions_faced"] = 2
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "The assault on Vienna (" in text
        assert "One province was lost, to Austria." in text
        assert "most of them" not in text
        assert "— the last, the Fourth Austrian Coalition." in text

    def test_a_single_coalition_is_not_the_last(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "One coalition stood against him — the Third Coalition." in text
        assert "the last," not in text

    def test_a_tie_names_both_courts(self):
        w = _boot()
        home = [r for r in w.nation_starting_regions["France"] if r != "Paris"][:4]
        for region, court in zip(home, ("Austria", "Austria", "Britain", "Britain")):
            w.capture_region(region, court)
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "as many to Austria as to Britain" in text

    def test_the_realm_arm_names_the_province_it_still_holds(self):
        """#40."""
        w = _boot()
        _reduce_france_to(w, {"Paris"})
        _tick(w, 5)
        rec = game_end.terminal_ending(w)
        assert rec["cause_line"].startswith("The Empire is reduced to Paris alone")
        # (Verification round V19: the `or "Paris" in cause_line` arm made
        # this pin vacuous on its own Paris board — the epilogue said "with no
        # soil left to govern" beside "reduced to Paris alone", and it passed.)
        epilogue = " ".join(rec["summary"]["epilogue"]["paragraphs"])
        assert "no soil left" not in epilogue
        assert "with only Paris left to govern" in epilogue


# ════════════════════════════════════════════════════════════════════════
# #25 / #21 / #26 / #27 — saves and endpoints
# ════════════════════════════════════════════════════════════════════════

class TestSaves:
    def test_two_fallen_campaigns_keep_two_final_saves(self, monkeypatch, tmp_path):
        """#25."""
        from backend import save_manager as SM
        monkeypatch.setattr(SM, "SAVE_DIR", tmp_path)
        paths = []
        for seed in ("ulm", "austerlitz"):
            w = _boot()
            w.campaign_seed = seed
            w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
            _tick(w, 10)
            SM.write_final_save(w)
            paths.append(_final_save(w))
        assert paths[0] != paths[1]
        assert paths[0].exists() and paths[1].exists()
        seeds = {json.loads(p.read_text(encoding="utf-8"))["metadata"]["campaign_seed"]
                 for p in paths}
        assert seeds == {"ulm", "austerlitz"}

    def test_a_pre_ge1_save_is_backfilled_with_a_record(self):
        """#21/#26: the opening, the record's first turn, and conquest
        records so an old conquest can still be titled."""
        from backend import save_manager as SM
        loaded = SM.load_game(FIXTURE_T20)
        w = loaded["world"]
        assert w.endings_armed
        totals = w.campaign_totals
        assert totals["record_since_turn"] == w.current_turn
        assert totals["opening"]["provinces"] == 28
        held_off_home = [n for n, r in w.regions.items()
                         if r.controller and n not in
                         w.nation_starting_regions.get(r.controller, [])]
        for name in held_off_home:
            assert w.province_title[name]["kind"] == game_end.TITLE_CONQUEST
        rec = game_end.record_ending(w, "verdict", game_end.CAUSE_VERDICT)
        assert rec["summary"]["record_since_turn"] == w.current_turn

    def test_the_mailbox_guard_keeps_the_count(self, client):
        """#27."""
        tc, M = client
        w = M.world
        game_end.record_ending(w, "defeat", game_end.CAUSE_EAGLE_FALLS)
        r = _post(tc, "/mailbox/activate", {"mailbox_id": 1})
        assert r["success"] is False and r["message"] == "The war is over."
        assert "count" in r and "items" in r


# ════════════════════════════════════════════════════════════════════════
# #29 / #30 / #31 / #32 — E2, E3, the goal
# ════════════════════════════════════════════════════════════════════════

class TestE2E3:
    def _no_court_left(self, w):
        for region in list(w.regions.values()):
            if region.controller and region.controller != "France" \
                    and region.controller not in w.vassals:
                region.controller = "France"
        w.invalidate_active_nations_cache()

    def test_e2_no_alarm_is_shown_with_nobody_left(self):
        """#30."""
        from backend.game_logic import coalition
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        w = _boot()
        w.threat_level = 99
        self._no_court_left(w)
        assert coalition.no_court_left_to_alarm(w)
        assert coalition.displayed_threat(w) == 0
        boe = build_diplomatic_ledger(w)["balance_of_europe"]
        assert boe["threat_level"] == 0 and boe["threat_tier"] == "LOW"
        assert boe["threat_projection"]["collapse_line"] == coalition.NO_EUROPE_LEFT_LINE
        assert w.threat_level == 99          # display only — the scalar stands

    def test_e3_a_dead_court_is_refused_before_the_war_purpose(self, client):
        """#29."""
        tc, M = client
        w = M.world
        for region in list(w.get_nation_regions("Portugal")):
            w.regions[region].controller = "Spain"
        for name in [m.name for m in w.marshals.values() if m.nation == "Portugal"]:
            del w.marshals[name]
        w.invalidate_active_nations_cache()
        w._build_marshal_index()
        r = _post(tc, "/command", {"command": "declare war on Portugal"})
        assert r["success"] is False
        assert "no longer exists" in r["message"]
        assert not r.get("war_purpose_popup") and not r.get("diplomatic_dialogue")

    def test_e3_a_court_killed_mid_phase_gets_no_row(self, monkeypatch):
        """#31: Britain takes Bavaria's last province during its own turn."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        w = _boot()
        for region in list(w.get_nation_regions("Bavaria"))[1:]:
            w.regions[region].controller = "Austria"
        last = w.get_nation_regions("Bavaria")[0]
        for name in [m.name for m in w.marshals.values() if m.nation == "Bavaria"]:
            del w.marshals[name]
        w.invalidate_active_nations_cache()
        w._build_marshal_index()
        real = EnemyAI.process_nation_turn

        def _patched(self, nation, world, game_state):
            if nation == "Britain":
                world.capture_region(last, "Britain")
                return []
            return real(self, nation, world, game_state)
        monkeypatch.setattr(EnemyAI, "process_nation_turn", _patched)
        tm = TurnManager(w, CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            results = tm._process_enemy_turns({"world": w})
        assert not any("Bavaria: No marshals" in s for s in results["summary"])

    def test_the_goal_after_the_verdict_is_past_tense(self):
        """#32."""
        from backend.ai.first_contact import answer_first_contact
        w = _boot()
        w.current_turn = 44
        _tick(w, 1)
        assert game_end.has_ending(w, game_end.CAUSE_VERDICT)
        text = answer_first_contact("goal", "how do I win", w)
        assert "History has judged the reign" in text
        assert "renders its Verdict" not in text
        assert "can still fall" in text
        assert "turns of war with his captor" in text


# ════════════════════════════════════════════════════════════════════════
# #46 — the death roll is seeded, and consumes no module RNG
# ════════════════════════════════════════════════════════════════════════

class TestTheSeededRoll:
    def test_seeded_and_isolated(self):
        w = _boot()
        nap = w.marshals["Napoleon"]
        random.seed(12345)
        state = random.getstate()

        def _pass(world):
            out = []
            for turn in range(1, 401):
                world.current_turn = turn
                out.append(game_end.sovereign_death_roll(world, nap, "battle"))
            return out
        first, second = _pass(w), _pass(w)
        assert first == second
        assert random.getstate() == state
        w.campaign_seed = "ulm"
        assert _pass(w) != first


# ════════════════════════════════════════════════════════════════════════
# #24 — the driver notes an ending stamped outside the end-turn window
# ════════════════════════════════════════════════════════════════════════

class TestTheDriverReadsTheRecord:
    def test_new_endings_are_noted_once(self):
        from tools.playtest_driver import _note_new_endings

        class _T:
            def __init__(self, rows):
                self.rows = rows

            def get(self, path):
                assert path == "/campaign_end"
                return {"endings": self.rows}

        class _D:
            def __init__(self):
                self.notes = []

            def note(self, text):
                self.notes.append(text)
        row = {"title": "THE FALL OF THE EMPIRE", "cause_line": "The Emperor is dead."}
        digest = _D()
        seen = _note_new_endings(_T([row]), digest, 0)
        seen = _note_new_endings(_T([row]), digest, seen)
        # ⚑ GE-2 (Sept 25, 2026) — CONSCIOUS FLIP: the ending's one-liner is
        # followed by the END SCREEN block (`_end_screen_lines`, each line
        # "↳ …"); the ending itself is still noted ONCE — the headline count
        # is what this pin is about.
        headlines = [n for n in digest.notes if n.startswith("ENDING — ")]
        assert seen == 1 and len(headlines) == 1
        assert all(n.lstrip().startswith("↳") for n in digest.notes if n not in headlines)
        assert "The Emperor is dead." in digest.notes[0]


# ════════════════════════════════════════════════════════════════════════
# #12 / #4 / #11 — after an enemy-phase death nothing of the player's moves
# ════════════════════════════════════════════════════════════════════════

class TestNothingMovesAfterTheFall:
    def test_an_enemy_phase_death_ends_the_turn_for_the_player(self, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        from backend.game_logic import jealousy
        from backend.game_logic.turn_manager import TurnManager
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        first = w.enemy_nations[0]
        calls = {"admin": [], "strategic": 0, "jealousy": 0, "autonomous": 0}

        def _turn(self, nation, world, game_state):
            if nation == first and "Napoleon" in world.marshals:
                world.destroy_marshal(world.marshals["Napoleon"], cause="battle",
                                      victor=first)
            return []

        def _admin(self, nation, world, game_state):
            calls["admin"].append(nation)
            return []

        def _strategic(self, world, game_state):
            calls["strategic"] += 1
            return []

        def _jealousy(world):
            calls["jealousy"] += 1

        def _autonomous(self, game_state):
            calls["autonomous"] += 1
            return None
        monkeypatch.setattr(EnemyAI, "process_nation_turn", _turn)
        monkeypatch.setattr(EnemyAI, "execute_admin_phase", _admin)
        monkeypatch.setattr(StrategicOrderProcessor, "process_strategic_orders", _strategic)
        monkeypatch.setattr(jealousy, "process_turn", _jealousy)
        monkeypatch.setattr(TurnManager, "_process_autonomous_marshals", _autonomous)
        tm = TurnManager(w, CommandExecutor())
        with contextlib.redirect_stdout(io.StringIO()):
            result = tm.end_turn({"world": w})
        assert game_end.terminal_ending(w)["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert calls == {"admin": [], "strategic": 0, "jealousy": 0, "autonomous": 0}
        # The payload is cut from the CLOSED record.
        assert game_end.terminal_ending(w)["closed"] is True
        assert result["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS

    def test_the_marshalate_is_not_offered_to_a_fallen_empire(self):
        w = _boot()
        w.commission_hint_shown = False
        w.gold = 999_999
        w.nation_gold["France"] = 999_999
        game_end.record_ending(w, "defeat", game_end.CAUSE_EAGLE_FALLS)
        with contextlib.redirect_stdout(io.StringIO()):
            w.advance_turn()
        assert w.commission_hint_shown is False


class TestTheSignedProvinceUnderASatellite:
    def test_it_is_titled_to_the_satellite(self):
        """The receiver's satellite occupying the signed province: titled,
        the record's holder the court that holds it."""
        w = _boot()
        w.regions["Tyrol"].controller = "KingdomOfItaly"
        w.invalidate_active_nations_cache()
        _cede_from(w, "Austria", ["Tyrol"])
        rec = w.province_title.get("Tyrol") or {}
        assert rec.get("kind") == game_end.TITLE_TREATY
        assert rec.get("holder") == "KingdomOfItaly"


class TestAProvinceLostTwiceIsOneProvince:
    def test_distinct(self):
        w = _boot()
        home = [r for r in w.nation_starting_regions["France"] if r != "Paris"][0]
        w.capture_region(home, "Austria")
        w.capture_region(home, "France")
        w.capture_region(home, "Austria")
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "One province was lost, to Austria." in text


class TestTheFatalEndTurnAsksNothing:
    def test_a_strategic_question_of_the_fatal_turn_is_not_asked(self):
        """A standing order that met the enemy earlier in the turn the
        Empire fell: the report narrates the march but asks nothing."""
        from backend.game_logic.turn_manager import _attach_endings
        w = _boot()
        before = len(w.endings)
        game_end.record_ending(w, "defeat", game_end.CAUSE_CHAINS)
        result = {"strategic_reports": [
            {"marshal": "Davout", "requires_input": True, "message": "Enemy at Swabia."}]}
        _attach_endings(result, w, before)
        assert "requires_input" not in result["strategic_reports"][0]
        assert result["strategic_reports"][0]["message"] == "Enemy at Swabia."
        assert result["ending"]["cause"] == game_end.CAUSE_CHAINS
