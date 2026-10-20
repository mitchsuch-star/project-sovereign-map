"""Pre-Deploy S13b part 4, slice S13b-4 — the voice (October 19, 2026;
`docs/BUG_FIXES.md` §DD-B; rules `SYSTEMS_REFERENCE.md` §132).

  DDB-45   a line joining two questions (" and " + a question word) is
           split and each part answered; `enemy_at` takes a place only
           when "at / in <place>" follows the foe.
  DDB-X28  (found by DDB-45's sweep) a yes/no tail ("… and is he
           fortified?") is a second question, its pronoun the first
           part's subject — it was dropped in silence.
  DDB-X29  (found by DDB-45's sweep) two of our marshals asked of at once
           ("how many men do Ney and Davout have?") are each answered —
           Davout was dropped, and "what are Ney and Davout doing?" shrugged.
  DDB-46   a STATE card ends with its state (the deficit card on recovery,
           the brewing card when the coalition forms); a one-shot EVENT
           notice posts at HIGH and ages out after its turn.
  DDB-X31  (found by DDB-46's sweep) the hard-reject posture's card ends
           with the posture.

The player's roads are driven through `/command` on the shipped 1805 boot
(the in-process TestClient, the mock parser); the rail through the
collector and the world's own advance.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.models.world_state import WorldState
from backend.notifications import (
    BANKRUPTCY_ESCALATION, COALITION_BREWING, EVENT_NOTICE_TYPES,
    FORCED_RETREAT_ORDER_VOIDED, NotificationPriority, create_notification,
)

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")
REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


@pytest.fixture
def client(monkeypatch):
    """The player's roads: the endpoints on the shipped 1805 boot, the mock parser."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _say(client, line: str) -> str:
    c, _world = client
    with contextlib.redirect_stdout(io.StringIO()):
        reply = c.post("/command", json={"command": line}).json()
    return str(reply.get("message") or "")


# ═══════════════════════════════════════════════════════════════════════════
# DDB-45 — two questions on one line
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB45:
    def test_how_strong_is_mack_and_where_is_vienna(self, client):
        """The conquest #1 sighting: it read "No, Sire — Mack stands at
        Swabia, not Vienna" — a third question nobody asked."""
        reply = _say(client, "how strong is Mack and where is Vienna?")
        assert "not Vienna" not in reply
        lines = reply.splitlines()
        assert len(lines) == 2, reply
        assert "Mack" in lines[0] and "Swabia" in lines[0]
        assert lines[1].startswith("Vienna")

    def test_where_is_lannes_and_who_holds_bohemia(self, client):
        """The conquest #8 sighting: the shrug."""
        reply = _say(client, "where is Lannes and who holds Bohemia?")
        assert "cannot answer" not in reply
        lines = reply.splitlines()
        assert "Lannes" in lines[0] and "Franche-Comte" in lines[0]
        assert lines[1] == "Bohemia is held by Austria."

    def test_a_part_neither_desk_takes_is_said_so(self, client):
        reply = _say(client, "where is Mack and who rules the waves of the moon?")
        assert "Mack" in reply.splitlines()[0]
        assert "I cannot answer that from the dispatches" in reply.splitlines()[1]

    def test_one_question_is_one_question(self, client):
        assert _say(client, "is Mack at Swabia?").startswith("Yes, Sire — Mack stands at Swabia")
        reply = _say(client, "where are Ney and Davout?")
        assert "Ney" in reply and "Davout" in reply

    def test_the_split_is_the_question_words(self):
        from backend.ai.question_desk import split_compound_question
        assert split_compound_question("how strong is Mack and where is Vienna?") == [
            "how strong is Mack", "where is Vienna?"]
        assert split_compound_question("where are Ney and Davout?") == [
            "where are Ney and Davout?"]
        assert split_compound_question("who holds Bohemia and Moravia?") == [
            "who holds Bohemia and Moravia?"]

    def test_enemy_at_takes_a_place_only_after_the_foe(self):
        from backend.ai.state_desk import _place_after_foe
        assert _place_after_foe("is mack at swabia", "Mack", ["Swabia"]) == "Swabia"
        assert _place_after_foe("is mack dug in at ulm", "Mack", ["Ulm"]) == "Ulm"
        assert _place_after_foe("how strong is mack where is vienna", "Mack",
                                ["Vienna"]) == ""


class TestDDBX28:
    def test_a_yes_no_tail_is_a_second_question(self, client):
        reply = _say(client, "where is Mack and is he fortified?")
        lines = reply.splitlines()
        assert len(lines) == 2, reply
        assert "Mack" in lines[1] and ("works" in lines[1] or "fortif" in lines[1])

    def test_its_pronoun_is_the_first_parts_subject(self, client):
        reply = _say(client, "where is Ney and can he reach Vienna?")
        assert "Ney can reach Vienna" in reply.splitlines()[1]


class TestDDBX29:
    def test_two_of_our_marshals_are_each_answered(self, client):
        for line in ("how many men do Ney and Davout have?",
                     "how strong are Ney and Davout?",
                     "what are Ney and Davout doing?"):
            reply = _say(client, line)
            assert "Ney" in reply and "Davout" in reply, (line, reply)
        assert _say(client, "how many men does Ney have?").startswith(
            "Marshal Ney commands"), "one marshal keeps his own answer"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-46 — the rail keeps what is still true
# ═══════════════════════════════════════════════════════════════════════════

def _types(world) -> list:
    return [n["type"] for n in world.notifications.get_pending()]


class TestDDB46:
    def test_the_deficit_card_ends_with_the_deficit(self, w):
        player = w.player_nation
        w.nation_bankruptcy_turns[player] = 1
        with contextlib.redirect_stdout(io.StringIO()):
            w.process_bankruptcy_desertion(player)
        assert BANKRUPTCY_ESCALATION in _types(w)
        w.nation_bankruptcy_turns[player] = 0
        with contextlib.redirect_stdout(io.StringIO()):
            w.process_bankruptcy_desertion(player)
        assert BANKRUPTCY_ESCALATION not in _types(w), "the chest recovered"

    def test_the_brewing_card_ends_when_the_coalition_forms(self):
        from backend.game_logic import coalition as CO
        world = WorldState()
        world.current_turn = 5
        for n in world.enemy_nations:
            world.diplomatic_states[world._make_diplo_key("France", n)] = "PEACE"
        world.notifications.add(create_notification(
            COALITION_BREWING, NotificationPriority.CRITICAL,
            "Coalition Brewing — 1 turn", "x", 5))
        with contextlib.redirect_stdout(io.StringIO()):
            assert CO.form_coalition(["Prussia", "Austria"], world).get("success")
        assert COALITION_BREWING not in _types(world)
        assert "coalition_declared" in _types(world)

    def test_an_event_notice_ages_out_after_its_turn(self, w):
        w.current_turn = 7
        w.notifications.add(create_notification(
            FORCED_RETREAT_ORDER_VOIDED, NotificationPriority.HIGH,
            "Ney orders lost", "x", 7, details={"marshal": "Ney"}))
        row = [n for n in w.notifications.get_pending()
               if n["type"] == FORCED_RETREAT_ORDER_VOIDED][0]
        assert row["expires_after_turn"] == 7
        assert w.notifications.retire_aged_events(7) == 0, "it stands through its turn"
        assert w.notifications.retire_aged_events(8) == 1, "and goes after it"

    def test_the_advance_retires_it(self, w):
        """Through the world's own advance: a notice of turn N stands
        through turn N+1's morning and is gone at the next."""
        start = int(w.current_turn)
        w.notifications.add(create_notification(
            FORCED_RETREAT_ORDER_VOIDED, NotificationPriority.HIGH,
            "Ney orders lost", "x", start, details={"marshal": "Ney"}))
        with contextlib.redirect_stdout(io.StringIO()):
            w.advance_turn()
        assert FORCED_RETREAT_ORDER_VOIDED in _types(w)
        with contextlib.redirect_stdout(io.StringIO()):
            w.advance_turn()
        assert FORCED_RETREAT_ORDER_VOIDED not in _types(w)

    def test_a_state_card_does_not_age(self, w):
        w.notifications.add(create_notification(
            BANKRUPTCY_ESCALATION, NotificationPriority.HIGH, "Treasury in deficit",
            "x", int(w.current_turn)))
        assert "expires_after_turn" not in [
            n for n in w.notifications.get_pending()
            if n["type"] == BANKRUPTCY_ESCALATION][0]

    def test_the_one_shot_events_post_at_high(self):
        """The producers outside the commitments routing (whose spec sets its
        own priority) post their one-shot events at HIGH — the census reads
        the source: no CRITICAL beside an event type's producer."""
        import re
        pattern = re.compile(
            r"(FORCED_RETREAT_ORDER_VOIDED|RECKLESS_CAVALRY_ACTION|ARMISTICE_EXPIRED|"
            r"VASSAL_REBELLION as _VR_CONST|_VR_CONST|VASSAL_REBELLION),?\s*\n?\s*"
            r"(?:priority=)?(?:NotificationPriority|_NP)\.CRITICAL")
        hits = []
        for path in ("backend/commands/combat_executor.py", "backend/models/world_state.py",
                     "backend/game_logic/diplomacy.py", "backend/game_logic/vassal.py"):
            src = (REPO / path).read_text(encoding="utf-8")
            hits += [(path, m.group(1)) for m in pattern.finditer(src)]
            for m in re.finditer(r"notification_type=(FORCED_RETREAT_ORDER_VOIDED|"
                                 r"RECKLESS_CAVALRY_ACTION),\s*\n\s*priority="
                                 r"NotificationPriority\.(\w+)", src):
                assert m.group(2) == "HIGH", (path, m.group(1))
        assert not hits, hits
        assert {FORCED_RETREAT_ORDER_VOIDED, "armistice_expired",
                "reckless_cavalry_action", "vassal_rebellion"} <= EVENT_NOTICE_TYPES


class TestDDBX30:
    """Found by DDB-46's sweep of every CRITICAL producer: the other one-shot
    events never aged out either. The reckless charge and the rebellions post
    at HIGH (`TestDDB46::test_the_one_shot_events_post_at_high` reads their
    producers); the commitments family keeps its spec's priority and ages."""

    def test_the_commitments_family_ages_with_its_own_priority(self):
        from backend.notifications import (BALANCE_OF_EUROPE_SHIFTED, BARGAIN_BREACHED,
                                           CALL_TO_ARMS_HONORED_COSTLY,
                                           CALL_TO_ARMS_REFUSED_DEFENSIVE,
                                           CALL_TO_ARMS_REFUSED_OFFENSIVE)
        for kind in (BARGAIN_BREACHED, CALL_TO_ARMS_REFUSED_OFFENSIVE,
                     CALL_TO_ARMS_REFUSED_DEFENSIVE, CALL_TO_ARMS_HONORED_COSTLY,
                     BALANCE_OF_EUROPE_SHIFTED):
            row = create_notification(kind, NotificationPriority.CRITICAL, "x", "y", 9)
            assert row["expires_after_turn"] == 9, kind
            assert row["priority"] == int(NotificationPriority.CRITICAL), kind

    def test_the_reckless_charge_and_the_rebellion_age_too(self):
        from backend.notifications import RECKLESS_CAVALRY_ACTION, VASSAL_REBELLION
        assert {RECKLESS_CAVALRY_ACTION, VASSAL_REBELLION} <= EVENT_NOTICE_TYPES

    def test_a_decision_and_a_state_never_age(self):
        """The last stand is a question awaiting an answer; the defeat warning
        and the save failure are states retired by their own producers."""
        from backend.notifications import (DEFEAT_IMMINENT_WARNING, MARSHAL_LAST_STAND,
                                           SAVE_FAILED)
        assert not ({MARSHAL_LAST_STAND, DEFEAT_IMMINENT_WARNING, SAVE_FAILED}
                    & EVENT_NOTICE_TYPES)


class TestDDBX31:
    def test_the_posture_card_ends_with_the_posture(self, w):
        from backend.game_logic.diplomacy import _process_betrayal_decay
        turn = int(w.current_turn)
        key = "Prussia|France"
        w.diplomatic_states[w._make_diplo_key("Prussia", "France")] = "PEACE"
        w.betrayal_history = {key: {"strikes": [
            {"episode_id": "e1", "decays_on_turn": turn},
            {"episode_id": "e2", "decays_on_turn": turn + 5},
            {"episode_id": "e3", "decays_on_turn": turn + 6}]}}
        w.notifications.add(create_notification(
            "hard_reject_posture_triggered", NotificationPriority.CRITICAL,
            "Prussia will hear nothing", "x", turn,
            details={"perpetrator_nation": "Prussia", "victim_nation": "France"}))
        with contextlib.redirect_stdout(io.StringIO()):
            _process_betrayal_decay(w)
        types = _types(w)
        assert "hard_reject_posture_cleared" in types
        assert "hard_reject_posture_triggered" not in types


# ═══════════════════════════════════════════════════════════════════════════
# DDB-47 — "… to join Ney and Davout" is one order
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB47:
    def test_the_sighting_is_one_order(self, client):
        """Diplomacy-first #6: Soult marched, and "Davout" was left on the
        line as a second order."""
        reply = _say(client, "Soult, march to Rhineland to join Ney and Davout")
        assert "Soult" in reply and "Rhineland" in reply
        assert "waits behind it" not in reply

    def test_the_split_needs_an_order_verb_after_the_name(self, w):
        from backend.commands.parser import _split_sequential_orders
        gs = {"world": w}
        assert _split_sequential_orders(
            "Soult, march to Rhineland to join Ney and Davout", gs) is None
        assert _split_sequential_orders("Soult, support Ney and Davout", gs) is None
        assert _split_sequential_orders("Ney, attack Mack and Davout, hold", gs) == (
            "Ney, attack Mack", "Davout, hold")
        assert _split_sequential_orders(
            "Ney, attack Mack and Davout support him", gs) == (
            "Ney, attack Mack", "Davout support him")

    def test_the_named_list_still_relays_its_second_man(self, client):
        """CQ-8 / CC-X17: "Ney and Davout, fortify" hands Davout's order back."""
        reply = _say(client, "Ney and Davout, fortify")
        assert "Davout's own waits behind it" in reply


# ═══════════════════════════════════════════════════════════════════════════
# DDB-48 — one section answers "how do I …"
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB48:
    def test_a_how_do_i_question_gets_its_section(self, client):
        assert _say(client, "how do I build ships?").startswith("THE ADMIRALTY")
        ports = _say(client, "how can I close Britain's ports?")
        assert ports.startswith("PORTS AND THE CONTINENTAL SYSTEM")
        assert "COMMAND REFERENCE" not in ports
        several = _say(client, "how do I attack with several marshals?")
        assert several.startswith("STRATEGIC COMMANDS") and "muster" in several

    def test_help_topic_prints_one_section(self, client):
        assert _say(client, "help navy").startswith("THE ADMIRALTY")
        assert _say(client, "help with the ports").startswith("PORTS AND THE CONTINENTAL SYSTEM")
        assert "COMMAND REFERENCE" in _say(client, "help")
        assert "COMMAND REFERENCE" in _say(client, "how do I sing?"), "no section named"

    def test_help_before_a_name_is_still_an_order(self, client):
        """P8-2: "help Davout" asks for a supporter, never the manual."""
        assert "COMMAND REFERENCE" not in _say(client, "help Davout")

    def test_the_ports_section_reads_the_admiraltys_numbers(self):
        from backend.commands.meta_executor import _ports_help_block
        from backend.game_logic import naval as N
        block = _ports_help_block()
        for pct, we in N.CS_WE_TIERS:
            assert f"{int(round(pct * 100))}%" in block
        assert f"ROTS -{N.READINESS_TICK} a turn to {N.READINESS_BLOCKADE_FLOOR}" in block
        assert f"to {N.NAVY_DRILL_CEILING} while a stronger enemy fleet" in block
        assert "guard home waters" in block and "blockade the enemy" in block

    def test_the_section_reader(self):
        from backend.ai.help_topics import help_request_section, section_for
        assert section_for("how do I make peace with Austria?") == "DIPLOMACY"
        assert section_for("how do I win?") == "THE CONGRESS OF PARIS"
        assert section_for("how do I win a battle?") == "MILITARY COMMANDS"
        assert section_for("how do I fortify?") == "TACTICAL COMMANDS"
        assert help_request_section("help Davout") is None
        assert help_request_section("help me") is None


# ═══════════════════════════════════════════════════════════════════════════
# DDB-49 — the reference's Congress figures are the Congress's
# ═══════════════════════════════════════════════════════════════════════════

def _help(world) -> str:
    from backend.commands.meta_executor import MetaExecutor
    with contextlib.redirect_stdout(io.StringIO()):
        return MetaExecutor(None)._execute_help({}, {"world": world})["message"]


class TestDDB49:
    def test_the_count_is_the_holds(self, w):
        from backend.game_logic import congress as C
        body = _help(w)
        assert f"{C.hold_titled(w)} TITLED" in body and "50 TITLED" not in body
        assert f"Keep the {C.hold_titled(w)}," in body
        assert f"For {C.congress_turns(w)} turns" in body
        assert "⟨" not in body, "every figure is filled"

    def test_a_scenario_that_moves_the_hold_moves_the_reference(self, w):
        w.campaign_end = dict(getattr(w, "campaign_end", None) or {}, hold_titled=40)
        assert "40 TITLED" in _help(w)

    def test_no_developers_note(self, w):
        body = _help(w)
        assert "never named here" not in body and "no player could learn" not in body


# ═══════════════════════════════════════════════════════════════════════════
# DDB-50 — a prisoner the peace releases is announced
# ═══════════════════════════════════════════════════════════════════════════

def _mack_held_then_peace(w):
    from backend.game_logic import diplomacy as D
    mack = w.marshals["Mack"]
    mack.captured_by = "France"
    mack.captured_turn = int(w.current_turn)
    with contextlib.redirect_stdout(io.StringIO()):
        D.set_diplomatic_state(w, "France", "Austria", "PEACE", "common_peace_settlement")
    return mack


class TestDDB50:
    def test_the_ratification_names_the_released_prisoner(self, w):
        from backend.game_logic.game_end import released_prisoner_lines
        mack = _mack_held_then_peace(w)
        assert not mack.captured_by and mack.location == "Vienna"
        lines = released_prisoner_lines(w, [w._make_diplo_key("France", "Austria")], "France")
        assert lines == ["Prisoners: Mack, our captive, goes home to Vienna under this "
                         "peace — an Austrian commander back in the field."]

    def test_the_dispatch_says_he_is_back_in_the_field(self, w):
        from backend.game_logic.dispatch import build_morning_dispatch
        _mack_held_then_peace(w)
        with contextlib.redirect_stdout(io.StringIO()):
            w.advance_turn()
            dispatch = build_morning_dispatch(w, [])
        lines = [t["message"] for t in dispatch["turn_events"] if "Mack" in t["message"]]
        assert lines == ["Mack, our prisoner, is released under the peace and returns "
                         "to Vienna — an Austrian commander back in the field."]

    def test_a_peace_for_other_courts_names_nobody(self, w):
        from backend.game_logic.game_end import released_prisoner_lines
        _mack_held_then_peace(w)
        assert released_prisoner_lines(w, [w._make_diplo_key("France", "Russia")], "France") == []


# ═══════════════════════════════════════════════════════════════════════════
# DDB-51 — an eliminated court's war has no purpose
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB51:
    def test_elimination_concludes_the_war_purpose(self, w):
        from backend.game_logic.dispatch import _build_war_objective_section
        before = [str(l.get("text") or l) for l in _build_war_objective_section(w, "France")]
        assert any("Austria" in line for line in before)
        with contextlib.redirect_stdout(io.StringIO()):
            w._eliminate_nation("Austria")
        after = [str(l.get("text") or l) for l in _build_war_objective_section(w, "France")]
        assert not any("Austria" in line for line in after)
        objectives = w.war_objectives.get(w._make_diplo_key("France", "Austria")) or {}
        assert all(o.get("concluded_turn") is not None for o in objectives.values())
        assert any("Britain" in line for line in after), "the other wars keep theirs"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-52 — the alarm road names the decay the Armed Peace holds
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB52:
    def test_the_held_decay_is_named_with_its_reason(self):
        import sys as _sys
        _sys.path.insert(0, str(REPO / "tests"))
        from test_sr_g7_the_armed_peace import _quiet_france
        from backend.game_logic import coalition as CO
        from backend.game_logic import congress as CG
        with contextlib.redirect_stdout(io.StringIO()):
            world = _quiet_france(turn=5, threat=45)
        forecast = CO.forecast_alarm_tick(world)
        assert forecast["net"] == 0 and forecast["decay_held"] > 0
        road = CG.alarm_road(world)
        assert road.startswith("holding")
        share = int(round(float(forecast["armed_peace"]["share"]) * 100))
        assert (f"of it held: the Armed Peace holds the alarm at {CO.ARMED_PEACE_WATCH} "
                f"while our bloc leads {share}% of Europe's power") in road

    def test_no_hold_says_nothing_of_it(self, w):
        from backend.game_logic import congress as CG
        assert "Armed Peace" not in CG.alarm_road(w), "at war, no watch stands"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-53 — one siege, one outcome
# ═══════════════════════════════════════════════════════════════════════════

def _siege_of_vienna(w):
    w.regions["Vienna"].controller = "Russia"
    w.invalidate_active_nations_cache()
    turn = int(w.current_turn)
    for e in ({"type": "garrison_assault", "defender_nation": "France", "region": "Vienna",
               "marshal": "Kutuzov", "held": True, "attacker_losses": 4000,
               "garrison_remaining": 10000},
              {"type": "garrison_assault", "defender_nation": "France", "region": "Vienna",
               "marshal": "Kutuzov", "held": False, "attacker_losses": 3000,
               "garrison_remaining": 0},
              {"type": "region_captured", "region": "Vienna", "captured_by": "Russia",
               "captured_from": "France", "nation": "Russia"}):
        e["turn"] = turn
        w.event_log.append(e)


class TestDDB53:
    def test_one_siege_prints_its_latest_outcome(self, w):
        from backend.game_logic.dispatch import _build_headline
        _siege_of_vienna(w)
        with contextlib.redirect_stdout(io.StringIO()):
            headline = _build_headline(w, "France", record=False)
        page = [headline["text"]] + list(headline.get("sub_beats") or [])
        vienna = [line for line in page if "Vienna" in line]
        assert len(vienna) == 1, vienna
        assert "taken" in vienna[0]

    def test_the_latest_garrison_outcome_stands(self):
        from backend.game_logic.dispatch import _collapse_sieges
        cands = [{"class": "garrison_held", "identity": "garrison:Ulm"},
                 {"class": "garrison_stormed", "identity": "garrison:Ulm"},
                 {"class": "garrison_held", "identity": "garrison:Paris"}]
        _collapse_sieges(cands)
        assert [c["class"] + "@" + c["identity"] for c in cands] == [
            "garrison_stormed@garrison:Ulm", "garrison_held@garrison:Paris"]

    def test_the_count_names_the_title_lost(self, w):
        from backend.game_logic import congress as CG
        from backend.game_logic.dispatch import _realm_candidates
        view = CG.titled(w)
        if not CG.armed(w) or view["count"] >= view["needed"]:
            pytest.skip("the realm line stands only while the count is short")
        w.headline_lead_memory = {"realm": {"titled": view["count"] + 1,
                                            "names": sorted(view["titled"] + ["Vienna"])}}
        lines = [c["text"] for c in _realm_candidates(w, "France") if c["class"] == "realm_titles"]
        assert lines and f"down from {view['count'] + 1} (Vienna lost)" in lines[0], lines
