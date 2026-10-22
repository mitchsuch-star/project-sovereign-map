"""VP-1 "The Emperor's Designs", S14b part 3 — the Acts of the Empire, THE
DECISIVE PEACE and its register (`docs/VP1_DESIGNS_SPEC.md` §4, §5, §9 Part
3; the landing record §14).

On the shipped 1805 boot (armed since part 2), through the real endpoints and
the real end-of-turn chokepoint: the stamp on a staged road (once, marked and
continued — the next end turn still plays), every negative board refused
with the condition that fails, the reward (Europe's alarm −15, floored at the
Armed Peace's watch), the Verdict's +2 score term and its tier lines, the
lead order, the fifth register's payload and client, the morning's front page
and Le Moniteur's next issue; and the four Acts — each quoted, charged
exactly its quote, refused the second time, refused off its road or its
board, and pointed to (never executed) when typed as a law.
"""
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import game_end as GE
from backend.game_logic import imperial_designs as ID
from tests.test_vp1_the_roads_armed import (  # noqa: F401 — fixtures
    _peace, _post, _proclaim, _quiet, _restore_active_world, _tick, _vassalize, client, world)

REPO = Path(__file__).resolve().parents[1]
GODOT = REPO / "godot-client" / "project-sovereign" / "scripts"
PRESSBURG = [{"type": "territory_cede", "regions": ["Tyrol", "Bohemia"],
              "from": "Austria", "to": "France"}]


def _rhine_sealed(client, world):
    """The Rhine road, staged: proclaimed through the button, three clients
    held four end turns, then a partition peace with Austria."""
    _proclaim(client, "rhine")
    for court in ("Bavaria", "Hesse", "Saxony"):
        _vassalize(world, court)
    _tick(world, 4)
    assert ID.is_fulfilled(world, "rhine.confederation")
    _peace(world, "Austria", PRESSBURG)


def _end_tick(world):
    with _quiet():
        return GE.process_end_of_turn(world, int(world.current_turn))


def _rel(world, court):
    return int(world.nation_relations.get(world._make_diplo_key("France", court), 0))


def _set_alarm(world, value):
    world.threat_by_target[world.player_nation] = int(value)


# ═══════════════════════════════════════════════════════════════════════════
# The stamp
# ═══════════════════════════════════════════════════════════════════════════

class TestTheStamp:
    def test_the_seam_is_released(self):
        assert ID.decisive_peace_released() is True

    def test_a_sealed_road_stamps_once_marked_and_continued(self, client, world):
        _rhine_sealed(client, world)
        _set_alarm(world, 70)
        stamped = _end_tick(world)
        assert [r["cause"] for r in stamped] == ["decisive_peace"]
        rec = stamped[0]
        assert rec["register"] == "decisive_peace" and rec["title"] == "THE DECISIVE PEACE"
        assert rec["kind"] == "victory" and rec["terminal"] is False
        assert rec["cause_line"] == ("The Peace of Pressburg: Austria is brought to terms by a "
                                     "partition, and the Confederation of the Rhine holds — Road I, "
                                     "the Protector of the Rhine, is sealed.")
        detail = rec["detail"]
        assert (detail["route"], detail["court"], detail["manner"], detail["treaty"]) == (
            "rhine", "Austria", "partition", "the Peace of Pressburg")
        assert detail["alarm_from"] == 70 and detail["alarm_to"] == 55
        assert world.threat_by_target["France"] == 55
        assert not world.game_over
        assert _end_tick(world) == []                       # once per campaign

    def test_the_alarm_never_falls_below_the_armed_peaces_watch(self, client, world):
        _rhine_sealed(client, world)
        _set_alarm(world, 50)
        rec = _end_tick(world)[0]
        assert (rec["detail"]["alarm_from"], rec["detail"]["alarm_to"]) == (50, 45)
        assert world.threat_by_target["France"] == 45

    def test_the_next_end_turn_still_plays(self, client, world):
        _rhine_sealed(client, world)
        assert _end_tick(world)
        reply = _post(client, "end turn")
        assert reply.get("success") is not False
        assert not reply.get("game_over")
        assert not world.game_over


class TestTheNegativeBoards:
    """Every board the record names never stamps — each with its condition."""

    def _ready(self, world):
        return ID.decisive_peace_reading(world)

    def test_no_road_proclaimed(self, client, world):
        for court in ("Bavaria", "Hesse", "Saxony"):
            _vassalize(world, court)
        _peace(world, "Austria", PRESSBURG)
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["proclaimed"] is False

    def test_a_status_quo_peace_seals_nothing(self, client, world):
        _proclaim(client, "rhine")
        for court in ("Bavaria", "Hesse", "Saxony"):
            _vassalize(world, court)
        _tick(world, 4)
        _peace(world, "Austria", [{"type": "gold_lump", "value": 500}])
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["both_latched"] is False

    def test_paris_lost(self, client, world):
        _rhine_sealed(client, world)
        world.regions["Paris"].controller = "Britain"
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["realm_free"] is False

    def test_a_homeland_province_in_enemy_hands(self, client, world):
        _rhine_sealed(client, world)
        homeland = sorted(world.nation_starting_regions["France"])
        target = next(r for r in homeland if r != "Paris")
        world.regions[target].controller = "Britain"            # at war with France
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["homeland_whole"] is False

    def test_a_lapsed_construction(self, client, world):
        _rhine_sealed(client, world)
        for court in ("Hesse", "Saxony"):
            world.vassals[court]["loyalty"] = 10
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["construction_holds"] is False

    def test_a_humbled_reign(self, client, world):
        _rhine_sealed(client, world)
        with _quiet():
            GE.record_ending(world, "defeat", GE.CAUSE_HUMBLED)
        assert _end_tick(world) == []
        assert self._ready(world)["conditions"]["realm_free"] is False

    def test_the_seam_held_down_stamps_nothing(self, client, world, monkeypatch):
        _rhine_sealed(client, world)
        monkeypatch.setattr(ID, "decisive_peace_released", lambda: False)
        assert _end_tick(world) == []
        assert self._ready(world)["ready"] is True


# ═══════════════════════════════════════════════════════════════════════════
# The Verdict (A2), the lead order, the register (A4)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheVerdict:
    def _inputs(self, world, **overrides):
        inputs = GE.verdict_inputs(world)
        inputs.update({"great_powers_at_war": [], "great_powers_knocked_out": [],
                       "treasury": 1000, "capital_held": True, "emperor": "free",
                       "provinces_held": inputs["opening_provinces"],
                       "satellites_kept": list(inputs["satellites_opening"]),
                       "humbled": False, "fallen": False, "imperial_peace": False})
        inputs.update(overrides)
        return inputs

    def test_a_status_quo_reign_reads_contested_without_and_ascendant_with(self, world):
        without = GE.verdict_tier(world, self._inputs(world))
        assert without["tier"] == "contested" and without["score"] == 0
        with_peace = GE.verdict_tier(world, self._inputs(
            world, decisive_peace=True, decisive_treaty="the Peace of Pressburg"))
        assert with_peace["tier"] == "ascendant"
        assert with_peace["score"] == GE.DECISIVE_PEACE_VERDICT_TERM == 2
        assert with_peace["lines"][1] == "The Peace of Pressburg decided the question it was fought for."

    def test_a_negative_term_still_pulls_it_down(self, world):
        inputs = self._inputs(world, decisive_peace=True, decisive_treaty="the Peace of Pressburg",
                              capital_held=False)
        tier = GE.verdict_tier(world, inputs)
        assert tier["tier"] == "contested"
        assert tier["lines"][1].startswith("The Peace of Pressburg decided one question at the table")
        assert "unbeaten at the table" not in " ".join(tier["lines"])

    def test_the_imperial_peace_keeps_its_own_line_and_floor(self, world):
        inputs = self._inputs(world, decisive_peace=True, decisive_treaty="the Peace of Pressburg",
                              imperial_peace=True, imperial_peace_route="congress")
        tier = GE.verdict_tier(world, inputs)
        assert tier["lines"][1] == "The great powers have signed the order at Paris."

    def test_the_stamped_world_reads_it(self, client, world):
        _rhine_sealed(client, world)
        _end_tick(world)
        inputs = GE.verdict_inputs(world)
        assert inputs["decisive_peace"] is True
        assert inputs["decisive_treaty"] == "the Peace of Pressburg"


class TestTheLeadOrder:
    def _lead(self, world, causes):
        from backend.game_logic.turn_manager import _attach_endings
        before = len(GE.endings(world))
        with _quiet():
            for cause in causes:
                GE.record_ending(world, "victory" if cause != GE.CAUSE_VERDICT else "verdict", cause)
        result = {}
        _attach_endings(result, world, before)
        return result["ending"]["cause"]

    def test_the_decisive_peace_leads_a_verdict_on_the_same_turn(self, world):
        assert self._lead(world, [GE.CAUSE_DECISIVE_PEACE, GE.CAUSE_VERDICT]) == "decisive_peace"

    def test_the_imperial_peace_leads_the_decisive_peace(self, world):
        assert self._lead(world, [GE.CAUSE_DECISIVE_PEACE, GE.CAUSE_IMPERIAL_PEACE]) == "imperial_peace"


class TestTheRegister:
    def test_the_cause_registers_as_the_fifth(self):
        assert GE.REGISTERS[GE.CAUSE_DECISIVE_PEACE] == "decisive_peace"
        assert GE.REGISTER_TITLES["decisive_peace"] == "THE DECISIVE PEACE"
        assert GE.CAUSE_DECISIVE_PEACE not in GE.TERMINAL_CAUSES

    def test_the_card_carries_the_road_from_the_stamp(self, client, world):
        _rhine_sealed(client, world)
        rec = _end_tick(world)[0]
        payload = GE.screen_payload(rec)
        block = payload["summary"]["designs"]
        assert block["road_line"].startswith("Road I, The Protector of the Rhine — proclaimed on turn")
        assert [row["id"] for row in block["designs"]] == ["rhine.confederation", "rhine.german_crown"]
        assert all("fulfilled on turn" in row["line"] for row in block["designs"])
        assert "The Congress of Paris still waits." in block["treaty_line"]
        assert json.dumps(payload)                            # ints and strings only

    def test_the_client_has_the_register(self):
        gd = (GODOT / "campaign_end.gd").read_text(encoding="utf-8")
        assert '"decisive_peace": {' in gd and '"title": "THE DECISIVE PEACE"' in gd
        block = gd[gd.index('"decisive_peace": {'):]
        block = block[:block.index("},")]
        assert '"primary": "Continue the reign"' in block and '"secondary": ""' in block
        assert 'if _register == "decisive_peace":' in gd and "_designs_block(summary.get(\"designs\")" in gd
        assert '"decisive_peace":\n\t\t\treturn' in gd.replace("\r\n", "\n")   # the what-now arm


# ═══════════════════════════════════════════════════════════════════════════
# The front page and Le Moniteur
# ═══════════════════════════════════════════════════════════════════════════

class TestTheNews:
    def test_the_morning_leads_with_it(self, client, world):
        from backend.game_logic import dispatch as D
        _rhine_sealed(client, world)
        rec = _end_tick(world)[0]
        line = D._decisive_peace_line(world)
        assert line == ID.decisive_headline_line(rec["detail"])
        assert line.startswith("THE DECISIVE PEACE — The Peace of Pressburg:")
        weights = D.HEADLINE_WEIGHTS
        assert weights["congress_summoned"] < weights["decisive_peace"] < weights["imperial_peace"]
        assert list(weights.values()).count(weights["decisive_peace"]) == 1
        assert "decisive_peace" in D._HEADLINE_TEMPLATES and "decisive_peace" in D._HEADLINE_BERTHIER_NOTES

    def test_le_moniteur_prints_the_treaty_deduped_on_the_stamp(self, client, world):
        from backend.game_logic.gazette import _special_candidates
        _rhine_sealed(client, world)
        rec = _end_tick(world)[0]
        events = [e for e in world.event_log if e.get("type") == "campaign_ending"
                  and e.get("cause") == "decisive_peace"]
        assert len(events) == 1
        cands = _special_candidates(world, events)
        assert ("THE PEACE OF PRESSBURG" in [c[1] for c in cands])
        key = next(c[2] for c in cands if c[1] == "THE PEACE OF PRESSBURG")
        assert key.endswith(f"decisive_peace:{int(rec['turn'])}")

    def test_each_treaty_has_its_caption(self):
        from backend.game_logic.gazette import _SPECIAL_WEIGHTS
        for treaty in list(ID.TREATY_NAMES.values()) + [ID.SYSTEM_TREATY]:
            assert ID.moniteur_caption({"treaty": treaty}) in _SPECIAL_WEIGHTS
        assert ID.moniteur_caption({"treaty": "the peace with Prussia and Saxony"}) in _SPECIAL_WEIGHTS


# ═══════════════════════════════════════════════════════════════════════════
# The Acts of the Empire (§5)
# ═══════════════════════════════════════════════════════════════════════════

def _decree(client, act_id):
    """The road page's Decree button: its own command, then the quote's option."""
    row = next(r for r in client.get("/imperial_designs").json()["acts"] if r["id"] == act_id)
    quote = _post(client, row["command"])
    assert quote["state"] == "awaiting_clarification", quote
    confirm = next(o["command"] for o in quote["options"] if o["label"].startswith("Decree"))
    return quote, _post(client, confirm)


class TestTheActs:
    def test_the_block_authors_four_acts_and_the_validator_reads_them(self, world):
        assert [a["id"] for a in ID.acts(world)] == [
            "temple_of_glory", "princes_dotations", "abolition_of_feudalism", "raft_on_the_niemen"]
        from backend.modding.validator import validate_scenario
        data = json.loads((REPO / "godot-client/project-sovereign/assets/maps/europe_1805.json")
                          .read_text(encoding="utf-8"))
        assert validate_scenario(data).is_valid
        data["imperial_designs"]["acts"][0]["effects"] = [{"type": "income", "amount": 5}]
        result = validate_scenario(data)
        assert not result.is_valid and any("acts[0].effects[0].type" in str(e) for e in result.errors)

    def test_before_a_proclamation_every_act_waits(self, client, world):
        rows = client.get("/imperial_designs").json()["acts"]
        assert rows and all(not r["available"] for r in rows)
        assert all("proclaim one first" in r["disabled_reason"] for r in rows)

    def test_each_act_charges_exactly_its_quote_once(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 30000
        authority = world.authority_tracker.authority
        quote, done = _decree(client, "temple_of_glory")
        assert "8,000 gold and 1 administrative action, once" in quote["message"]
        assert done["success"] is True, done
        assert world.gold == 30000 - 8000
        assert world.authority_tracker.authority == min(100, authority + 15)
        assert ID.act_decreed_turn(world, "temple_of_glory") == int(world.current_turn)
        spent = _post(client, "decree the Temple of Glory")
        assert spent["success"] is False and spent["message"].startswith(
            "No administrative actions remaining")              # the executor's pre-gate first
        world.admin_actions_remaining = 2
        again = _post(client, "decree the Temple of Glory")
        assert again["success"] is False and "was decreed on turn" in again["message"]
        assert world.gold == 22000

    def test_the_dotations_pay_the_members(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 30000
        _vassalize(world, "Hesse", loyalty=50)
        before = _rel(world, "Saxony")
        _, done = _decree(client, "princes_dotations")
        assert done["success"] is True, done
        assert world.vassals["Hesse"]["loyalty"] == 65
        assert _rel(world, "Saxony") == min(100, before + 20)

    def test_an_act_off_the_road_is_forsworn(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 30000
        reply = _post(client, "decree the Abolition of Feudalism")
        assert reply["success"] is False
        assert "belongs to Road II, The Crowns of Italy — forsworn" in reply["message"]

    def test_the_board_won_preconditions(self, client, world):
        _proclaim(client, "crowns")
        world.gold = 30000
        reason = ID.act_refusal(world, "abolition_of_feudalism")
        assert reason and "Naples as the Emperor's vassal first" in reason
        _vassalize(world, "Naples", loyalty=50)
        assert ID.act_refusal(world, "abolition_of_feudalism") is None

    def test_the_raft_courts_a_beaten_great_power(self, client, world, monkeypatch):
        from backend.game_logic import diplomacy
        _proclaim(client, "system")
        world.gold = 30000
        assert "needs a great power at war with the Empire beaten first" in (
            ID.act_refusal(world, "raft_on_the_niemen") or "")
        monkeypatch.setattr(diplomacy, "live_war_score_for",
                            lambda w, n, o: -30 if n == "Russia" else 0)
        assert ID.act_beaten_court(world, ID.act(world, "raft_on_the_niemen")) == "Russia"
        before = _rel(world, "Russia")
        _, done = _decree(client, "raft_on_the_niemen")
        assert done["success"] is True, done
        assert _rel(world, "Russia") == min(100, before + 20)

    def test_the_gold_refusal(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 1000
        assert ID.act_refusal(world, "temple_of_glory") == (
            "The Temple of Glory costs 8,000 gold; the treasury holds 1,000.")

    def test_every_row_reads_the_executors_refusal(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 7000
        for row in client.get("/imperial_designs").json()["acts"]:
            assert row["disabled_reason"] == (ID.act_refusal(world, row["id"]) or "")
            assert row["available"] is (ID.act_refusal(world, row["id"]) is None)

    def test_typed_as_a_law_it_is_pointed_to_never_decreed(self, client, world):
        _proclaim(client, "rhine")
        world.gold = 30000
        reply = _post(client, "enact the Temple of Glory")
        assert reply["success"] is False
        assert "is an Act of the Empire, Sire, not a law" in reply["message"]
        assert ID.DESIGNS_CONTROL in reply["message"]
        assert "no law called" not in reply["message"]
        assert world.gold == 30000 and ID.act_decreed_turn(world, "temple_of_glory") == -1

    def test_the_morning_names_the_act_once_the_laws_are_bought(self, client, world, monkeypatch):
        from backend.game_logic import dispatch as D
        from backend.game_logic import reforms
        _proclaim(client, "rhine")
        world.gold = 30000
        for key, state in list(world.diplomatic_states.items()):
            if "France" in key.split("|") and state in ("WAR", "ARMISTICE"):
                world.diplomatic_states[key] = "PEACE"
        monkeypatch.setattr(reforms, "peace_sink_line", lambda w, n: "")
        with _quiet():
            situation = D.build_morning_dispatch(world).get("situation") or {}
        assert situation.get("act_sink") == "the chest could decree the Temple of Glory — 8,000g"
        assert "law_sink" not in situation

    def test_the_log_and_the_save(self, client, world):
        from backend.campaign_log import format_event_oneliner
        from backend.models.world_state import WorldState
        _proclaim(client, "rhine")
        world.gold = 30000
        _decree(client, "temple_of_glory")
        row = next(e for e in world.event_log if e.get("phase") == "decreed")
        assert format_event_oneliner(row) == "The Temple of Glory — an Act of the Empire is decreed (8,000 gold)"
        again = WorldState.from_dict(world.to_dict())
        assert ID.act_decreed_turn(again, "temple_of_glory") == int(world.current_turn)

    def test_an_older_store_gains_the_acts(self, world):
        from backend.save_manager import _backfill_imperial_designs
        store = world.imperial_designs
        store["block"].pop("acts")
        store["state"]["road"] = "crowns"
        _backfill_imperial_designs(world)
        assert [a["id"] for a in ID.acts(world)][0] == "temple_of_glory"
        assert world.imperial_designs["state"]["road"] == "crowns"     # the state kept

    def test_the_client_renders_the_decree_rows(self):
        gd = (GODOT / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert "func _add_acts_block(acts: Array)" in gd
        assert 'btn.text = "Decree " + str(row.get("title", ""))' in gd
        assert 'row.get("disabled_reason")' in gd
        main = (GODOT / "main.gd").read_text(encoding="utf-8")
        assert '"decree the ",' in main
        for view in ("main.gd", "dispatch_view.gd"):
            assert 'situation.get("act_sink", "")' in (GODOT / view).read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# The siblings (BUG_FIXES §VP1) and the arm's dial
# ═══════════════════════════════════════════════════════════════════════════

class TestVP1X20OnceMadeItIsSaidSo:
    def test_the_road_page_and_the_goal_answer_speak_in_the_past(self, client, world):
        _rhine_sealed(client, world)
        assert "a waypoint on the road to the Congress" in ID.goal_clause(world)
        rec = _end_tick(world)[0]
        made = f"THE DECISIVE PEACE was made on turn {rec['turn']} — the Peace of Pressburg"
        assert made in client.get("/imperial_designs").json()["headline"]
        clause = ID.goal_clause(world)
        assert made in clause and "a waypoint on the road to the Congress" not in clause


class TestTheDeclineUntilLatchDial:
    def _answerer(self, policy, latched):
        from tools import playtest_driver as D

        class _T:
            calls = 0

            def get(self, path):
                _T.calls += 1
                assert path == "/imperial_designs"
                return {"roads": [{"id": "system", "designs": [
                    {"id": "system.blockade", "fulfilled_turn": 7 if latched else -1}]}]}

        return D.Answerer(_T(), None, dict(D.POLICY_DEFAULTS) | policy, False), _T

    def test_absent_by_default_so_every_arm_is_unchanged(self):
        import argparse
        from tools import playtest_driver as D
        assert "decline_until_latch" in D.POLICY_FLAG_KEYS
        assert "decline_until_latch" not in D.POLICY_DEFAULTS
        assert json.dumps(D.resolve_policy(argparse.Namespace(), {})) == json.dumps(dict(D.POLICY_DEFAULTS))
        answerer, transport = self._answerer({}, latched=False)
        assert answerer._court_declined({"from_nation": "Britain"}) is False
        assert transport.calls == 0                       # never touches the transport

    def test_declined_until_the_blockade_latches(self):
        answerer, _ = self._answerer({"decline_until_latch": "Britain"}, latched=False)
        assert answerer._court_declined({"from_nation": "Britain"}) is True
        assert answerer._court_declined({"from_nation": "Austria"}) is False
        answerer, transport = self._answerer({"decline_until_latch": "Britain"}, latched=True)
        assert answerer._court_declined({"from_nation": "Britain"}) is False
        assert answerer._court_declined({"from_nation": "Britain"}) is False
        assert transport.calls == 1                       # sticky once latched


class TestTheRoadArms:
    """The record §9 Part 3 / §11: the three road arms, per seed, through the
    real driver (`tools/_vp1_road_arms.py`, its record committed)."""
    RECORD = REPO / "tools" / "_vp1_road_arms_final.json"

    def _record(self):
        return json.loads(self.RECORD.read_text(encoding="utf-8"))

    def test_every_arm_and_seed_is_reported_with_its_reason(self):
        rec = self._record()
        seen = {(r["arm"], r["seed"]) for r in rec["results"]}
        assert seen == {(f"VP1-{a}", s) for a in ("RH", "CS", "TH")
                        for s in ("historical", "austerlitz", "marengo")}
        assert all(r["reason"] for r in rec["results"])

    def test_the_decisive_peace_records_on_a_benchmark_seed(self):
        rec = self._record()
        assert rec["done_when"] is True
        stamped = {(r["arm"], r["seed"]): r["stamped_turn"] for r in rec["results"]}
        assert all(stamped[("VP1-RH", s)] >= 0 for s in ("historical", "austerlitz", "marengo"))
        assert all(stamped[("VP1-TH", s)] >= 0 for s in ("historical", "austerlitz", "marengo"))

    def test_each_script_proclaims_with_the_road_pages_own_command(self, world):
        rec = self._record()
        for arm, spec in rec["arms"].items():
            script = json.loads((REPO / spec["script"]).read_text(encoding="utf-8"))
            lines = [line for loop in script["turns"].values() for line in loop]
            want = ID.proclaim_command(ID.road(world, spec["road"]))
            assert any(line.lower() == want.lower() for line in lines), (arm, want)
