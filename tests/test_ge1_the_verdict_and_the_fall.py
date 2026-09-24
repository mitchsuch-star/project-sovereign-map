"""GE-1 "The Verdict and the Fall" — the campaign's endings (row EP).

Spec: docs/GAME_END_SPEC.md §2 (R1–R9) and docs/ENDGAME_PLAN.md §3–§6
(RULED), with the user's September 25, 2026 additions: the Emperor's death
("The Eagle Falls"), and the exile story on the Fall. Landing record:
ENDGAME_PLAN.md §6 GE-1; rules SYSTEMS_REFERENCE.md §64.

Every staging here drives the REAL seams — `capture_marshal`,
`destroy_marshal`, `_ratify_treaty`, `TurnManager.end_turn`, `/command`,
`/load` — never a hand-written ending record.
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
TUTORIAL = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "tutorial_1805.json")


def _boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(SCEN)


def _tick(world, n=1):
    """n end-of-turn ticks of the endings (the ONE per-turn caller), as
    `TurnManager.end_turn` runs it after the advance."""
    stamped = []
    for _ in range(n):
        world.current_turn += 1
        stamped += game_end.process_end_of_turn(world, turn_ended=world.current_turn - 1)
    return stamped


def _reduce_france_to(world, keep):
    for region in list(world.get_nation_regions("France")):
        if region not in keep:
            world.regions[region].controller = "Austria"
    world.invalidate_active_nations_cache()


# ════════════════════════════════════════════════════════════════════════
# The flag (R7)
# ════════════════════════════════════════════════════════════════════════

class TestTheFlag:
    def test_the_1805_campaign_arms(self):
        w = _boot()
        assert w.endings_armed is True
        assert game_end.verdict_turn(w) == 44
        assert w.campaign_end["fall_grace_turns"] == 5
        assert w.campaign_end["captivity_grace_turns"] == 10

    def test_the_tutorial_the_bare_and_the_legacy_world_never_arm(self):
        with contextlib.redirect_stdout(io.StringIO()):
            tut = WorldState.from_scenario(TUTORIAL)
        assert tut.endings_armed is False
        assert WorldState(player_nation="France", sovereign_map="europe").endings_armed is False
        assert WorldState(player_nation="France").endings_armed is False

    def test_the_lever_down_disarms(self, monkeypatch):
        w = _boot()
        monkeypatch.setattr(game_end, "THE_CAMPAIGN_CAN_END", False)
        assert w.endings_armed is False
        assert game_end.record_ending(w, "defeat", game_end.CAUSE_SOIL) is None

    def test_sandbox_mode_is_never_written(self):
        w = _boot()
        assert w.sandbox_mode is True        # derived from sovereign_map, untouched
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 5)
        assert w.sandbox_mode is True

    def test_the_block_round_trips_and_the_five_fields_serialize(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 2)
        data = json.loads(json.dumps(w.to_dict()))
        for key in ("campaign_end", "fall_clock", "endings", "campaign_totals",
                    "province_title"):
            assert key in data
        again = WorldState.from_dict(data)
        assert again.campaign_end == w.campaign_end
        assert again.fall_clock == w.fall_clock
        assert again.campaign_totals == w.campaign_totals


class TestTheValidator:
    def _v(self, block):
        from backend.modding.validator import validate_scenario
        data = {"sovereign_map": "europe", "player_nation": "France",
                "campaign_end": block}
        return validate_scenario(data, check_adjacency=False)

    def test_the_shipped_block_is_clean(self):
        from backend.modding.validator import validate_scenario
        result = validate_scenario(SCEN)
        assert result.is_valid
        assert not [e for e in result.warnings if "campaign_end" in e.path]

    def test_a_missing_verdict_turn_is_an_error(self):
        result = self._v({"fall_grace_turns": 5})
        assert any(e.path == "campaign_end.verdict_turn" for e in result.errors)

    def test_a_boolean_is_not_an_integer(self):
        result = self._v({"verdict_turn": True})
        assert any("verdict_turn" in e.path for e in result.errors)

    def test_out_of_range_is_an_error(self):
        result = self._v({"verdict_turn": 44, "fall_grace_turns": 0})
        assert any("fall_grace_turns" in e.path for e in result.errors)

    def test_an_unknown_key_warns_for_forward_compatibility(self):
        result = self._v({"verdict_turn": 44, "hold_titled": 50})
        assert result.is_valid
        assert any("hold_titled" in e.path for e in result.warnings)

    def test_a_non_object_is_an_error(self):
        result = self._v([44])
        assert any(e.path == "campaign_end" for e in result.errors)


# ════════════════════════════════════════════════════════════════════════
# Arm 1 — "The Empire Without Soil or Sword"
# ════════════════════════════════════════════════════════════════════════

class TestTheSoilOrSwordClock:
    def test_warns_on_turn_one_with_the_clock_and_the_exits(self):
        from backend.game_logic.turn_manager import get_defeat_imminent_state
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 1)
        warning = get_defeat_imminent_state(w)
        assert warning["heading"] == "THE FALL OF THE EMPIRE"
        assert "1 of 5" in warning["message"]
        assert "4 turns remain" in warning["message"]
        assert "retake a province or make peace" in warning["message"]
        arm = warning["fall"]["arms"][0]
        assert arm["arm"] == fall.ARM_SOIL and arm["turns_left"] == 4

    def test_falls_on_the_fifth(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        assert _tick(w, 4) == []
        assert not w.game_over
        stamped = _tick(w, 1)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_SOIL]
        assert w.game_over and w.victory == "defeat"
        # Review round (#40), flipped consciously: the arm fires at ≤ 1
        # province, so the line names the one still held — "No soil
        # remains" was false while Brittany was French.
        assert stamped[0]["cause_line"].startswith(
            "The Empire is reduced to Brittany alone")

    def test_retaking_a_province_on_turn_three_stops_the_clock(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 3)
        w.regions["Anjou"].controller = "France"
        w.invalidate_active_nations_cache()
        _tick(w, 1)
        assert fall.ARM_SOIL not in w.fall_clock
        # ...and a later loss starts it from ONE, not from where it stopped.
        w.regions["Anjou"].controller = "Austria"
        w.invalidate_active_nations_cache()
        _tick(w, 1)
        assert w.fall_clock[fall.ARM_SOIL]["turns"] == 1

    def test_peace_with_every_court_stops_the_clock(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 3)
        for court in list(w.get_nations_at_war_with("France")):
            w.diplomatic_states[w._make_diplo_key("France", court)] = "PEACE"
        _tick(w, 3)
        assert fall.ARM_SOIL not in w.fall_clock and not w.game_over

    def test_no_sword_arm_ticks_and_a_commission_stops_it(self):
        w = _boot()
        for m in list(w.marshals.values()):
            if m.nation == "France":
                m.strength = 0
        w.nation_gold["France"] = 0
        _tick(w, 2)
        assert w.fall_clock[fall.ARM_SOIL]["sword"] is True
        # A commission (the executor's own road) puts a corps back in the field.
        w.nation_gold["France"] = 10_000
        from backend.game_logic.recruitment import commission_marshal, first_affordable_commission
        cand = first_affordable_commission(w, "France")
        assert cand is not None
        commission_marshal(w, "France", cand)
        _tick(w, 1)
        assert fall.ARM_SOIL not in w.fall_clock

    def test_paris_alone_never_triggers(self):
        w = _boot()
        w.regions["Paris"].controller = "Austria"
        w.invalidate_active_nations_cache()
        assert fall.get_fall_state(w) is None
        assert _tick(w, 12) == []
        assert not w.game_over

    def test_the_standing_realm_is_silent(self):
        from backend.game_logic.turn_manager import get_defeat_imminent_state
        w = _boot()
        _tick(w, 1)
        assert get_defeat_imminent_state(w) is None
        assert w.fall_clock == {}


# ════════════════════════════════════════════════════════════════════════
# Arm 2 — "The Eagle in Chains"
# ════════════════════════════════════════════════════════════════════════

class TestTheChainsClock:
    def test_falls_on_the_tenth_turn_unfreed(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        assert _tick(w, 9) == []
        stamped = _tick(w, 1)
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_CHAINS]
        assert stamped[0]["cause_line"] == "The Emperor, a prisoner these 10 turns, is deposed."
        assert w.game_over

    def test_a_peace_with_the_captor_frees_him_and_resets_the_clock(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Britain", context="t")
        _tick(w, 6)
        set_diplomatic_state(w, "France", "Britain", "PEACE", reason="test")
        assert nap.captured_by == ""
        _tick(w, 1)
        assert fall.ARM_CHAINS not in w.fall_clock

    def test_a_truce_pauses_it_and_never_resets_it(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 4)
        key = w._make_diplo_key("France", "Britain")
        w.diplomatic_states[key] = "ARMISTICE"
        _tick(w, 5)
        entry = w.fall_clock[fall.ARM_CHAINS]
        assert entry["turns"] == 4 and entry["paused"] is True
        w.diplomatic_states[key] = "WAR"
        _tick(w, 1)
        assert w.fall_clock[fall.ARM_CHAINS]["turns"] == 5

    def test_the_captor_offers_its_terms_on_the_clock(self):
        """R1's reachability proof, half one: the offer ARRIVES — on the
        chains clock's turns 1, 4 and 7, whatever the war score."""
        from backend.game_logic import ai_diplomacy as AD
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        offers = []
        for _ in range(9):
            _tick(w, 1)
            prop = AD.process_diplomatic_phase("Britain", w)
            if prop and prop.get("captor_terms"):
                offers.append(w.fall_clock[fall.ARM_CHAINS]["turns"])
        assert offers == [1, 4, 7]

    def test_accepting_the_captors_terms_at_an_empty_treasury_frees_him(self):
        """R1's reachability proof, half two: the exit is LEGAL at 0 gold."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        from backend.game_logic import ai_diplomacy as AD
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Britain", context="t")
        w.nation_gold["France"] = 0
        _tick(w, 1)
        prop = AD.process_diplomatic_phase("Britain", w)
        # Delivered whatever its acceptance score (the P8 reducer forces an
        # unwelcome harsh peace through) — the filter never eats the exit.
        assert prop and prop.get("captor_terms")
        AD.deliver_ai_proposal(prop, w)
        dialogue = w.dialogue_manager.peek()
        de = DiplomaticExecutor.__new__(DiplomaticExecutor)
        with contextlib.redirect_stdout(io.StringIO()):
            result = de._handle_accept_ai_proposal(dialogue, w)
        assert result.get("success") is True
        assert nap.captured_by == ""
        assert w.nation_gold["France"] >= 0
        _tick(w, 1)
        assert fall.ARM_CHAINS not in w.fall_clock and not w.game_over

    def test_the_offer_is_armed_worlds_only(self, monkeypatch):
        from backend.game_logic import ai_diplomacy as AD
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 1)
        monkeypatch.setattr(game_end, "THE_CAMPAIGN_CAN_END", False)
        assert AD._captor_offer_due("Britain", "France", w) is False


# ════════════════════════════════════════════════════════════════════════
# The third arm — "The Eagle Falls" (Sept 25, 2026)
# ════════════════════════════════════════════════════════════════════════

class TestTheEagleFalls:
    def test_the_roll_is_seeded_and_bounded(self):
        w = _boot()
        nap = w.marshals["Napoleon"]
        rolls = [game_end.sovereign_death_roll(w, nap, "battle")
                 for _ in range(3)]
        assert len(set(rolls)) == 1          # the same moment rolls the same
        hits = 0
        for turn in range(1, 401):           # the PRODUCTION roll, turn by turn
            w.current_turn = turn
            hits += game_end.sovereign_death_roll(w, nap, "battle")
        assert 30 <= hits <= 90              # ~15% of 400

    @pytest.mark.parametrize("cause", ["attrition", "interned", "dismissed",
                                       "nation_eliminated"])
    def test_only_the_battlefield_kills(self, cause, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        nap = w.marshals["Napoleon"]
        assert game_end.sovereign_death_roll(w, nap, cause) is False
        w.destroy_marshal(nap, cause=cause, victor="Austria")
        assert "Napoleon" in w.marshals and nap.captured_by
        assert not w.game_over

    def test_a_death_removes_him_and_ends_the_war(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        removed = w.destroy_marshal(w.marshals["Napoleon"], cause="battle",
                                    victor="Austria")
        assert removed is True and "Napoleon" not in w.marshals
        assert w.fallen_marshals["Napoleon"]["sovereign"] is True
        event = [e for e in w.event_log if e.get("type") == "marshal_destroyed"][-1]
        assert event["sovereign"] is True and "THE EMPEROR" in event["message"]
        rec = game_end.terminal_ending(w)
        assert rec["cause"] == game_end.CAUSE_EAGLE_FALLS
        assert rec["cause_line"] == "The Emperor is dead."
        assert w.game_over and w.victory == "defeat"

    def test_the_lever_down_and_the_bare_world_keep_the_death_guard(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        monkeypatch.setattr(game_end, "THE_EMPEROR_IS_MORTAL", False)
        w = _boot()
        w.destroy_marshal(w.marshals["Napoleon"], cause="battle", victor="Austria")
        assert w.marshals["Napoleon"].captured_by == "Austria"
        monkeypatch.setattr(game_end, "THE_EMPEROR_IS_MORTAL", True)
        w2 = _boot()
        w2.campaign_end = {}                  # the rules not authored
        w2.destroy_marshal(w2.marshals["Napoleon"], cause="battle", victor="Austria")
        assert w2.marshals["Napoleon"].captured_by == "Austria"

    def test_a_prisoner_never_dies(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        nap = w.marshals["Napoleon"]
        w.capture_marshal(nap, "Britain", context="t")
        assert w.destroy_marshal(nap, cause="battle", victor="Austria") is False
        assert "Napoleon" in w.marshals

    def test_the_dispatch_and_the_moniteur_carry_it(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        from backend.game_logic import dispatch, gazette
        w = _boot()
        w.destroy_marshal(w.marshals["Napoleon"], cause="battle", victor="Austria")
        head = dispatch._build_headline(w, "France", record=False)
        assert head["class"] == "sovereign_dead"
        assert "THE EMPEROR IS DEAD" in head["text"]
        assert dispatch.HEADLINE_WEIGHTS["sovereign_dead"] > dispatch.HEADLINE_WEIGHTS["sovereign_captured"]
        turn_events = [e for e in w.event_log if e.get("turn") == w.current_turn]
        assert gazette._special_reason(w, turn_events) == "THE EMPEROR IS DEAD"

    def test_the_campaign_log_names_the_emperor(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({"type": "marshal_destroyed", "marshal": "Napoleon",
                                      "location": "Lorraine", "victor": "Austria",
                                      "cause": "battle", "sovereign": True})
        assert line.startswith("THE EMPEROR Napoleon FALLS at Lorraine")


class TestTheEagleFallsDriven:
    """The death through the real /command road: the player's own attack."""

    @pytest.fixture
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from tests._chip_census import board_env
        prior = (M.world, M.game_state.get("world"), M.parser)
        board_env(monkeypatch)
        yield TestClient(M.app), M
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    def test_the_emperor_falls_in_his_own_attack(self, client, monkeypatch):
        tc, M = client
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = M.world
        for m in w.marshals.values():
            if m.nation == "France" and not m.is_sovereign:
                m.location = "Brittany"
        nap = w.marshals["Napoleon"]
        mack = w.marshals["Mack"]
        nap.location = "Lorraine"
        nap.strength = 60
        assert mack.location == "Swabia"          # one march from Lorraine
        w._build_marshal_index()
        random.seed(7)
        with contextlib.redirect_stdout(io.StringIO()):
            r = tc.post("/command", json={"command": "Napoleon, attack Mack"}).json()
        assert "HAS FALLEN" in r["message"], r["message"]
        assert r["game_over"] is True
        assert r["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS
        with contextlib.redirect_stdout(io.StringIO()):
            again = tc.post("/command", json={"command": "end turn"}).json()
        assert again["success"] is False and again["message"] == "The war is over."


# ════════════════════════════════════════════════════════════════════════
# The Fall through the real end turn, the saves, the load (R6)
# ════════════════════════════════════════════════════════════════════════

class TestTheFallDriven:
    @pytest.fixture
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from tests._chip_census import board_env
        prior = (M.world, M.game_state.get("world"), M.parser)
        board_env(monkeypatch)
        yield TestClient(M.app), M
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    def _end_turn(self, tc, seed):
        random.seed(seed)
        with contextlib.redirect_stdout(io.StringIO()):
            return tc.post("/command", json={"command": "end turn"}).json()

    def test_the_realm_falls_on_the_fifth_end_turn_and_the_saves_obey_r6(self, client):
        from backend import save_manager as SM
        tc, M = client
        w = M.world
        _reduce_france_to(w, {"Brittany"})
        responses = []
        for i in range(8):
            r = self._end_turn(tc, 4000 + i)
            responses.append(r)
            if r.get("game_over"):
                break
        warning = responses[0]["morning_dispatch"]["defeat_imminent_warning"]
        assert "1 of 5" in warning["message"] and warning["fall"]
        fallen = responses[-1]
        assert len(responses) == 5
        assert fallen["game_over"] is True and fallen["victory"] == "defeat"
        assert fallen["ending"]["cause"] == game_end.CAUSE_SOIL
        assert "THE FALL OF THE EMPIRE" in fallen["message"]
        assert fallen["game_state"]["endings"][-1]["terminal"] is True
        # R3: terminal — the next order is refused.
        refused = self._end_turn(tc, 4999)
        assert refused["success"] is False and refused["message"] == "The war is over."
        # R6: the autosave keeps the turn BEFORE the fall; a Final save exists.
        auto = json.loads((SM.SAVE_DIR / SM.AUTOSAVE_FILENAME).read_text(encoding="utf-8"))
        assert auto["metadata"].get("ending") in (None, {}) or not auto["metadata"]["ending"].get("terminal")
        final = game_end.terminal_ending(w).get("final_save")
        assert final and Path(final).exists()
        meta = json.loads(Path(final).read_text(encoding="utf-8"))["metadata"]
        assert meta["save_name"].startswith("Final — ")
        assert meta["ending"]["cause"] == game_end.CAUSE_SOIL
        # Continue (the first row) resumes the playable campaign, never the end screen.
        first = SM.list_saves()[0]
        assert not ((first["metadata"].get("ending") or {}).get("terminal"))
        # A defeated save loads onto the end screen.
        with contextlib.redirect_stdout(io.StringIO()):
            loaded = tc.post("/load", json={"filename": Path(final).name}).json()
        assert loaded["ending"]["cause"] == game_end.CAUSE_SOIL
        assert loaded["game_over"] is True
        # /mailbox/activate is guarded like its eleven siblings.
        with contextlib.redirect_stdout(io.StringIO()):
            box = tc.post("/mailbox/activate", json={"mailbox_id": 1}).json()
        assert box["success"] is False and box["message"] == "The war is over."


# ════════════════════════════════════════════════════════════════════════
# GR5 — an AI court meets the predicate and nothing ends
# ════════════════════════════════════════════════════════════════════════

class TestSymmetry:
    def test_the_predicate_answers_for_an_ai_court_and_keeps_no_clock(self):
        w = _boot()
        for region in list(w.get_nation_regions("Prussia"))[1:]:
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        w.diplomatic_states[w._make_diplo_key("France", "Prussia")] = "WAR"
        state = fall.get_fall_state(w, "Prussia")
        assert state and fall.ARM_SOIL in state["arms"]
        assert state["arms"][fall.ARM_SOIL]["turns"] == 0
        assert _tick(w, 6) == [] and not w.game_over
        assert set(w.fall_clock) <= {fall.ARM_SOIL, fall.ARM_CHAINS}


# ════════════════════════════════════════════════════════════════════════
# The Humbled Peace (ENDGAME_PLAN §3)
# ════════════════════════════════════════════════════════════════════════

def _cede(world, regions, to="Austria"):
    return world._ratify_treaty({
        "proposer_nation": to, "target_nation": "France", "type": "peace",
        "demands": [{"type": "territory_cede", "regions": list(regions)}],
        "sweeteners": [],
    })


class TestTheHumbledPeace:
    def test_ceding_paris_is_marked_and_the_campaign_continues(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, ["Paris"])
        assert w.regions["Paris"].controller == "Austria"
        rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]
        assert rec and rec[0]["terminal"] is False
        assert rec[0]["detail"]["capital_ceded"] is True
        assert w.game_over is False
        assert w.province_title["Paris"]["kind"] == game_end.TITLE_TREATY

    def test_one_province_is_no_humbling(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, ["Anjou"])
        assert not [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]
        assert w.campaign_totals["peaces_signed"] == 1
        assert w.campaign_totals["provinces_ceded"] == 1

    def test_half_the_homeland_is_humbling(self):
        w = _boot()
        home = [r for r in w.nation_starting_regions["France"] if r != "Paris"]
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, home[:14])
        rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]
        assert rec and len(rec[0]["detail"]["homeland_ceded"]) == 14

    def test_it_stamps_once_and_the_verdict_reads_it(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, ["Paris"])
            _cede(w, ["Anjou"], to="Britain")
        assert len([r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED]) == 1
        assert game_end.verdict_tier(w)["tier"] == "eclipse"


# ════════════════════════════════════════════════════════════════════════
# The Verdict of History (R2)
# ════════════════════════════════════════════════════════════════════════

class TestTheVerdict:
    def test_fires_once_at_the_authored_turn_and_never_ends_the_war(self):
        w = _boot()
        w.current_turn = 43
        assert _tick(w, 1) == []                    # the end of turn 43
        stamped = _tick(w, 1)                       # the end of turn 44
        assert [r["cause"] for r in stamped] == [game_end.CAUSE_VERDICT]
        assert stamped[0]["calendar_label"] == "Early July 1807"
        assert w.game_over is False
        assert _tick(w, 5) == []

    def test_the_status_quo_is_contested(self):
        assert game_end.verdict_tier(_boot())["tier"] == "contested"

    def test_a_ruined_realm_is_the_eclipse(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany", "Anjou", "Normandy"})
        assert game_end.verdict_tier(w)["tier"] == "eclipse"

    def test_great_powers_knocked_out_are_a_triumph(self):
        w = _boot()
        for court in ("Austria", "Prussia", "Russia"):
            for region in list(w.get_nation_regions(court)):
                w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        verdict = game_end.verdict_tier(w)
        assert set(verdict["inputs"]["great_powers_knocked_out"]) == {"Austria", "Prussia", "Russia"}
        assert verdict["tier"] == "triumph"

    def test_the_tiers_have_three_lines_each(self):
        for _tier, _floor, title, lines in game_end.VERDICT_TIERS:
            assert title and len(lines) == 3


# ════════════════════════════════════════════════════════════════════════
# The exile story (Sept 25, 2026) — driven on staged endings
# ════════════════════════════════════════════════════════════════════════

def _assert_facts_exist(world, epilogue):
    facts = epilogue["facts"]
    for name in facts["marshals"]:
        assert name in world.marshals or name in world.fallen_marshals, name
    known = set(world.enemy_nations) | {world.player_nation}
    for court in facts["courts"]:
        assert court in known, court
    battles = {(world.campaign_totals.get("greatest_victory") or {}).get("name"),
               (world.campaign_totals.get("worst_defeat") or {}).get("name")}
    for battle in facts["battles"]:
        assert battle in battles, battle
    assert 3 <= len(epilogue["paragraphs"]) <= 6


class TestTheExileStory:
    def test_an_emperor_captured_by_britain_goes_to_st_helena(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        rec = game_end.terminal_ending(w)
        epi = rec["summary"]["epilogue"]
        text = " ".join(epi["paragraphs"])
        assert epi["variant"] == "captivity"
        assert "Bellerophon" in text and "St Helena" in text
        assert "Castlereagh" in text
        assert "The Verdict of History" in text
        _assert_facts_exist(w, epi)

    def test_a_continental_captor_keeps_him_in_its_own_fortress(self):
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Austria", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "Olmütz" in text and "Metternich" in text

    def test_a_deposed_emperor_with_no_captor_abdicates_to_elba(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        _tick(w, 5)
        epi = game_end.terminal_ending(w)["summary"]["epilogue"]
        text = " ".join(epi["paragraphs"])
        assert epi["variant"] == "abdication"
        assert "Fontainebleau" in text and "Elba" in text
        _assert_facts_exist(w, epi)

    def test_the_death_arm_is_the_funeral(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        w.destroy_marshal(w.marshals["Davout"], cause="battle", victor="Austria")
        w.destroy_marshal(w.marshals["Napoleon"], cause="charge", victor="Austria")
        epi = game_end.terminal_ending(w)["summary"]["epilogue"]
        text = " ".join(epi["paragraphs"])
        assert epi["variant"] == "funeral"
        assert "cut down in a charge" in text and "bier" in text
        assert "Davout" in text                     # the fallen are remembered
        _assert_facts_exist(w, epi)

    def test_a_humbled_peace_is_signed_not_exiled(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, ["Paris"])
        rec = [r for r in w.endings if r["cause"] == game_end.CAUSE_HUMBLED][0]
        epi = rec["summary"]["epilogue"]
        text = " ".join(epi["paragraphs"])
        assert epi["variant"] == "humbled"
        assert "signed" in text and "Paris itself" in text
        assert "Elba" not in text and "St Helena" not in text
        _assert_facts_exist(w, epi)

    def test_the_record_paragraph_names_the_battles_and_the_coalition(self):
        w = _boot()
        game_end.count_battle(w, player_side="attacker", won=True, lost=False,
                              inflicted=12_000, suffered=3_000,
                              name="The Great Battle of Ulm", region="Swabia",
                              enemy="Austria")
        game_end.count_battle(w, player_side="defender", won=False, lost=True,
                              inflicted=2_000, suffered=9_000,
                              name="Battle of Paris", region="Paris",
                              enemy="Britain")
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        epi = game_end.terminal_ending(w)["summary"]["epilogue"]
        text = " ".join(epi["paragraphs"])
        assert "The Great Battle of Ulm" in text and "high-water mark" in text
        assert "Battle of Paris was the worst day" in text
        assert "the Third Coalition" in text
        _assert_facts_exist(w, epi)

    def test_only_a_battlefield_death_is_called_a_fall(self):
        w = _boot()
        w.destroy_marshal(w.marshals["Ney"], cause="attrition")
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        text = " ".join(game_end.terminal_ending(w)["summary"]["epilogue"]["paragraphs"])
        assert "had fallen before him" not in text


# ════════════════════════════════════════════════════════════════════════
# campaign_totals (R4) and province_title (§2.2)
# ════════════════════════════════════════════════════════════════════════

class TestTheRecord:
    def test_the_opening_is_seeded_at_boot(self):
        t = _boot().campaign_totals
        assert t["opening"]["provinces"] == 28
        assert t["opening"]["satellites"] == ["Holland", "KingdomOfItaly", "Switzerland"]
        assert t["coalitions_faced"] == 1 and t["coalition_names"] == ["Third Coalition"]

    def test_captures_and_marshals_are_counted_at_the_moment(self):
        w = _boot()
        w.capture_region("Franconia", "France")
        w.capture_region("Anjou", "Austria")
        w.capture_marshal(w.marshals["Mack"], "France", context="t")
        w.capture_marshal(w.marshals["Ney"], "Austria", context="t")
        t = w.campaign_totals
        assert t["provinces_taken"] == 1 and t["provinces_lost"] == 1
        assert t["lost_to"] == {"Austria": 1}
        assert t["enemy_marshals_taken"] == 1 and t["own_marshals_taken"] == 1

    def test_a_coalition_formed_against_the_player_is_counted(self):
        from backend.game_logic import coalition
        w = _boot()
        before = w.campaign_totals["coalitions_faced"]
        w.active_coalition = None
        w.coalition_cooldown = 0
        qualifying = [n for n in ("Austria", "Britain", "Russia")]
        with contextlib.redirect_stdout(io.StringIO()):
            coalition.form_coalition(qualifying, w)
        assert w.campaign_totals["coalitions_faced"] == before + 1


class TestTheBattleCount:
    """R4: one battle, counted once, through the real /command road."""

    @pytest.fixture
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from tests._chip_census import board_env
        prior = (M.world, M.game_state.get("world"), M.parser)
        board_env(monkeypatch)
        yield TestClient(M.app), M
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    def test_a_battle_is_counted_once_through_the_pipeline(self, client):
        tc, M = client
        before = dict(M.world.campaign_totals)
        random.seed(11)
        with contextlib.redirect_stdout(io.StringIO()):
            r = tc.post("/command", json={"command": "Ney, attack Mack"}).json()
        assert r.get("battle_report"), r.get("message")
        t = M.world.campaign_totals
        assert t["battles_fought"] == before.get("battles_fought", 0) + 1
        assert t["battles_won"] + t["battles_lost"] + t["battles_drawn"] == t["battles_fought"]
        assert t["men_inflicted"] > 0 and t["men_lost"] > 0


class TestProvinceTitle:
    def test_a_conquest_is_held_until_quiet(self):
        w = _boot()
        w.capture_region("Franconia", "France")
        rec = w.province_title["Franconia"]
        assert rec["kind"] == game_end.TITLE_CONQUEST and rec["holder"] == "France"
        assert rec["from"] == "Bavaria"
        assert game_end.province_title_kind(w, "Franconia", "France") == "held"
        w.current_turn += 12
        # Bavaria (France's ally at boot) is not at war with France — quiet.
        assert game_end.province_title_kind(w, "Franconia", "France") == "conquest"

    def test_a_return_home_clears_the_record(self):
        w = _boot()
        w.capture_region("Anjou", "Austria")
        assert "Anjou" in w.province_title
        w.capture_region("Anjou", "France")
        assert "Anjou" not in w.province_title

    def test_a_hostile_army_on_it_restarts_the_quiet_clock(self):
        w = _boot()
        w.capture_region("Munich", "France")
        w.current_turn += 6
        mack = w.marshals["Mack"]
        mack.location = "Munich"
        w._build_marshal_index()
        game_end.reconcile_province_titles(w)
        assert w.province_title["Munich"]["since"] == w.current_turn

    def test_a_signed_cession_is_titled_at_once(self):
        w = _boot()
        with contextlib.redirect_stdout(io.StringIO()):
            _cede(w, ["Anjou"])
        assert game_end.province_title_kind(w, "Anjou", "Austria") == "treaty"

    def test_titled_provinces_counts_the_bloc_not_its_allies(self):
        w = _boot()
        counts = game_end.titled_provinces(w, "France")
        assert len(counts["titled"]) == 35 and counts["held"] == []

    def test_a_signed_province_is_reconciled_out_of_the_revanche(self):
        from backend.game_logic.agendas import _entry_regions
        w = _boot()
        # Austria cedes Tyrol to France by treaty; its Revanche would claim it.
        w._ratify_treaty({"proposer_nation": "France", "target_nation": "Austria",
                          "type": "peace",
                          "demands": [{"type": "territory_cede", "regions": ["Tyrol"]}],
                          "sweeteners": []})
        assert w.province_title["Tyrol"]["kind"] == game_end.TITLE_TREATY
        entry = {"id": "revanche_austria", "type": "acquire_regions",
                 "regions": ["Tyrol", "Bavaria"], "emergent": True}
        assert game_end.reconciled_regions(w, "Austria") == {"Tyrol"}
        assert _entry_regions(w, "Austria", entry) == ["Bavaria"]
        # Breaking the treaty re-arms it. (Review round #45: the tautology
        # that closed this test — `get_active_agenda is not None` — is
        # deleted; the live view and the not-satisfied guard are pinned in
        # tests/test_ge1_review_round.py.)
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "WAR"
        assert game_end.reconciled_regions(w, "Austria") == set()


# ════════════════════════════════════════════════════════════════════════
# E2 / E3 / E4 — global elimination
# ════════════════════════════════════════════════════════════════════════

class TestGlobalElimination:
    def _empty_europe(self):
        w = _boot()
        for court in list(w.enemy_nations):
            if court in w.vassals:
                continue
            for region in list(w.get_nation_regions(court)):
                w.capture_region(region, "France")
        return w

    def test_e2_the_alarm_is_silent_with_nobody_left(self):
        from backend.game_logic import coalition
        w = self._empty_europe()
        assert coalition.no_court_left_to_alarm(w, "France")
        w.threat_level = 50
        with contextlib.redirect_stdout(io.StringIO()):
            coalition.process_coalition_turn(w)
        assert w.threat_level <= 50
        from backend.game_logic.diplomatic_advisory import _assess_situation
        text = _assess_situation(w)
        text = text if isinstance(text, str) else json.dumps(text)
        assert "There is no Europe left to alarm" in text

    def test_e2_is_structural_not_a_quiet_moment(self):
        from backend.game_logic import coalition
        assert coalition.no_court_left_to_alarm(_boot(), "France") is False

    def test_e3_a_dead_court_cannot_be_declared_upon(self):
        from backend.game_logic.diplomacy import declare_war
        w = self._empty_europe()
        result = declare_war(w, "France", "Britain")
        assert result["success"] is False and "no longer exists" in result["message"]

    def test_e3_trade_dominance_dies_with_its_court(self):
        from backend.game_logic import naval
        w = _boot()
        assert naval.trade_dominance_nation(w) == "Britain"
        w = self._empty_europe()
        assert naval.trade_dominance_nation(w) is None

    def test_e3_the_enemy_phase_carries_no_row_for_the_dead(self):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        w = self._empty_europe()
        ex = CommandExecutor()
        tm = TurnManager(w, executor=ex)
        with contextlib.redirect_stdout(io.StringIO()):
            results = tm._process_enemy_turns({"world": w, "executor": ex})
        assert not [s for s in results["summary"] if "eliminated?" in s
                    and s.split(":")[0] not in w.get_active_nations()]

    def test_e4_a_knocked_out_great_power_is_a_verdict_input(self):
        w = _boot()
        for region in list(w.get_nation_regions("Prussia")):
            w.capture_region(region, "France")
        assert "Prussia" in game_end.verdict_inputs(w)["great_powers_knocked_out"]


# ════════════════════════════════════════════════════════════════════════
# WO-D10 — the exile commissions (R8)
# ════════════════════════════════════════════════════════════════════════

class TestTheExileCommissions:
    def test_no_home_soil_commissions_on_the_richest_held_province(self):
        from backend.game_logic import recruitment
        w = _boot()
        for region in list(w.get_nation_regions("France")):
            w.regions[region].controller = "Austria"
        for region in ("Franconia", "Munich"):
            w.regions[region].controller = "France"
        w.invalidate_active_nations_cache()
        spot = recruitment.find_spawn_region(w, "France")
        best = max(w.regions[r].get_effective_income() for r in ("Franconia", "Munich"))
        assert spot in ("Franconia", "Munich")
        assert w.regions[spot].get_effective_income() == best

    def test_the_lever_down_is_home_soil_only(self, monkeypatch):
        from backend.game_logic import recruitment
        monkeypatch.setattr(recruitment, "THE_EXILE_COMMISSIONS", False)
        w = _boot()
        for region in list(w.get_nation_regions("France")):
            w.regions[region].controller = "Austria"
        w.regions["Munich"].controller = "France"
        w.invalidate_active_nations_cache()
        assert recruitment.find_spawn_region(w, "France") is None

    def test_holding_nothing_still_refuses_and_says_why(self):
        from backend.game_logic import recruitment
        w = _boot()
        for region in list(w.get_nation_regions("France")):
            w.regions[region].controller = "Austria"
        w.invalidate_active_nations_cache()
        cand = recruitment.get_marshal_pool(w, "France")[0]
        reason = recruitment.check_commission(w, "France", cand, treasury=99_999)
        assert reason.startswith("No HOME soil remains") and "we hold none" in reason


# ════════════════════════════════════════════════════════════════════════
# First contact — "how do I win" (R7)
# ════════════════════════════════════════════════════════════════════════

class TestFirstContact:
    def test_the_armed_campaign_names_the_verdict_and_the_fall(self):
        from backend.ai.first_contact import answer_first_contact
        text = answer_first_contact("goal", "how do I win", _boot())
        assert "Verdict" in text and "Early July 1807" in text
        assert "can fall" in text and "press T" in text and "Today:" in text

    def test_the_bare_world_stays_open_ended(self):
        from backend.ai.first_contact import answer_first_contact
        bare = WorldState(player_nation="France", sovereign_map="europe")
        assert "open-ended" in answer_first_contact("goal", "how do I win", bare)


# ════════════════════════════════════════════════════════════════════════
# The turn loop's own guards
# ════════════════════════════════════════════════════════════════════════

class TestTheTurnLoop:
    def _tm(self, w):
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.turn_manager import TurnManager
        ex = CommandExecutor()
        return TurnManager(w, executor=ex), {"world": w, "executor": ex}

    def test_a_fallen_campaign_does_not_keep_turning(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        w.destroy_marshal(w.marshals["Napoleon"], cause="battle", victor="Austria")
        tm, gs = self._tm(w)
        before = w.current_turn
        with contextlib.redirect_stdout(io.StringIO()):
            result = tm.end_turn(gs)
        assert w.current_turn == before
        assert result["victory_check"]["game_over"] is True
        assert result["ending"]["cause"] == game_end.CAUSE_EAGLE_FALLS

    def test_the_fall_clears_the_choices_nobody_can_answer(self):
        w = _boot()
        _reduce_france_to(w, {"Brittany"})
        tm, gs = self._tm(w)
        results = []
        for i in range(5):
            if i == 4:
                w.coalition_popup = {"stale": True}
            random.seed(900 + i)
            with contextlib.redirect_stdout(io.StringIO()):
                results.append(tm.end_turn(gs))
        assert results[-1]["victory_check"]["game_over"] is True
        assert results[-1]["ending"]["cause"] == game_end.CAUSE_SOIL
        assert w.coalition_popup is None

    def test_the_enemy_phase_stops_on_a_fallen_empire(self, monkeypatch):
        monkeypatch.setattr(game_end, "SOVEREIGN_DEATH_CHANCE_PCT", 100)
        w = _boot()
        w.destroy_marshal(w.marshals["Napoleon"], cause="battle", victor="Austria")
        tm, gs = self._tm(w)
        with contextlib.redirect_stdout(io.StringIO()):
            results = tm._process_enemy_turns(gs)
        assert results["nations"] == {}

    def test_the_victory_check_reads_the_recorded_ending_only(self):
        from backend.game_logic.turn_manager import TurnManager
        w = _boot()
        tm = TurnManager(w)
        assert tm._check_victory_conditions() == {"game_over": False, "result": None, "reason": None}
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        check = tm._check_victory_conditions()
        assert check["game_over"] is True and check["result"] == "defeat"


class TestTheVassalHumbling:
    def test_a_treaty_that_makes_france_a_vassal_is_humbling(self):
        w = _boot()
        w.vassals["France"] = {"lord": "Austria", "loyalty": 50}
        rec = game_end.note_ratification(
            w, signed_terms=[], applied_clauses=[], was_vassal=False,
            counterparts=["Austria"], war_ending=True, source="settlement")
        assert rec and rec["cause"] == game_end.CAUSE_HUMBLED
        assert rec["detail"]["vassal_of"] == "Austria"

    def test_an_old_vassalage_is_not_a_new_humbling(self):
        w = _boot()
        w.vassals["France"] = {"lord": "Austria", "loyalty": 50}
        assert game_end.note_ratification(
            w, signed_terms=[], applied_clauses=[], was_vassal=True,
            counterparts=["Austria"], war_ending=True, source="treaty") is None


class TestPreGE1Saves:
    def test_a_save_without_the_block_is_armed_from_its_scenario(self, tmp_path):
        from backend import save_manager as SM
        w = _boot()
        data = w.to_dict()
        data.pop("campaign_end")
        path = tmp_path / "old.json"
        path.write_text(json.dumps({"metadata": {"format_version": SM.FORMAT_VERSION,
                                                 "save_name": "old"},
                                    "world_state": data}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            loaded = SM.load_game(path)["world"]
        assert loaded.endings_armed is True
        assert loaded.campaign_end["verdict_turn"] == 44

    def test_the_slot_carries_the_ending(self):
        from backend import save_manager as SM
        w = _boot()
        w.capture_marshal(w.marshals["Napoleon"], "Britain", context="t")
        _tick(w, 10)
        assert SM._slot_ending(w)["cause"] == game_end.CAUSE_CHAINS
        assert SM._slot_ending(_boot()) is None


class TestTheMarkedEndingOnTheWire:
    """The Verdict — a MARKED ending — rides the ordinary end-turn road
    (the allow-list), with the summary the end screen renders, and the
    read-only GET returns it."""

    @pytest.fixture
    def client(self, monkeypatch):
        from fastapi.testclient import TestClient
        import backend.main as M
        from tests._chip_census import board_env
        prior = (M.world, M.game_state.get("world"), M.parser)
        board_env(monkeypatch)
        yield TestClient(M.app), M
        M.world = prior[0]
        M.game_state["world"] = prior[1]
        M.parser = prior[2]

    def test_the_verdict_reaches_the_end_turn_response(self, client):
        tc, M = client
        M.world.current_turn = 44
        random.seed(44)
        with contextlib.redirect_stdout(io.StringIO()):
            r = tc.post("/command", json={"command": "end turn"}).json()
        assert r["ending"]["cause"] == game_end.CAUSE_VERDICT
        assert r["ending"]["summary"]["verdict"]["tier"] in (
            "triumph", "ascendant", "contested", "eclipse")
        assert not r.get("game_over")
        assert "THE VERDICT OF HISTORY" in r["message"]
        with contextlib.redirect_stdout(io.StringIO()):
            g = tc.get("/campaign_end").json()
        assert g["armed"] is True and g["game_over"] is False
        assert [e["cause"] for e in g["endings"]] == [game_end.CAUSE_VERDICT]
        assert g["endings"][0]["summary"]["calendar_label"] == "Early July 1807"
