"""Score Finish Step 9, SF-RR3 "the page and the copy" (October 21, 2026;
rules SYSTEMS_REFERENCE.md §138).

Every row the final reading filed against the morning page and the game's
copy, reproduced on today's tree before a line was written (most were the
playtester's quoted digest lines; each was staged on a board):

    `where is Napoleon?` -> "the Emperor Napoleon stands at …"      (SFR-D14 i)
    a standing march -> "Under a standing move to order — …"         (SFR-D14 ii)
    the grant -> "Massena, Murat hold under your own orders"         (SFR-D14 iii)
    `is Milan safe?` -> "Milan is Kingdom of Italy's, Sire"          (SFR-D14 iv)
    an armistice sent -> "departs for the Austria court"             (SFR-D14 v)
    a top-up under a truce -> "under the peace with Britain"         (SFR-D14 vi)
    a strategic battle in the digest -> the charge line alone        (SFR-D15)
    a forced retreat -> "broken at Munich" beside "mauled at Tyrol"  (SFR-D17)
    a one-step march -> "(0 turns remaining)", the order a turn more (SFR-D21)
    `what borders Orleanais?` -> faithful to the map                 (SFR-D27, closed)
    a stale top-up -> "Ney is on the wrong side … at Swabia"         (SFR-D30)
    a levy drawn -> "nobody has gone to collect them"; a newcomer
      counted in another man's famine                                (SFR-D32)
    the famine's toll falling as its count rose                      (SFR-D33)
    a satellite lost under a mauled corps                            (SFR-D36)
    a truce headlined "the war with Britain is over"                 (SFR-D43)
    "fortifications decay: 6% → 6%"                                  (SFR-D44)
    the allegiance auction's close told nowhere                      (SFR-B4)
    "For 0 more turns he brings NONE …"                              (SFR-B6)
    "Tribute: +0g/turn (75% of their income)" under a remission      (SFR-B7)
    a second "TRAFALGAR"                                             (SFR-B8)
    a client general's capture over the fleet's loss                 (SFR-B9)
    "prepared to go as far as service to the strong"                 (SFR-B12)
    "Choose your war purpose against PapalStates."                   (SFR-B13)
    a satellite under 40 with no lever named where the reader looks  (SFR-B15)
    "seats 1 courts"                                                 (EA-E4)
    a satellite's fall crowded off the page                          (EG-X3)

Every fix is ONE function seam held down here to reproduce its row (the
DD-B idiom — no module lever; the ratchet holds at 231). Display only:
nothing the AI reads moved, except SFR-D21's completion, which only the
player's own strategic marches reach.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.question_desk as QD
import backend.display_names as DN
import backend.game_logic.ai_diplomacy as AD
import backend.game_logic.diplomacy as DIP
import backend.game_logic.diplomatic_ledger as DL
import backend.game_logic.diplomatic_templates as DT
import backend.game_logic.dispatch as DS
import backend.game_logic.intent as INT
import backend.game_logic.jealousy as J
import backend.game_logic.naval as NV
import backend.game_logic.withdrawal as WD
import backend.main as M
import backend.models.world_state as WS
from backend.commands import strategic as ST
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def ask(client, line):
    with _quiet():
        return str(client.post("/command", json={"command": line}).json().get("message") or "")


def post(client, line):
    with _quiet():
        return client.post("/command", json={"command": line}).json()


def page(world):
    with _quiet():
        head = DS._build_headline(world, "France", record=False) or {}
    return [head.get("text", "")] + list(head.get("sub_beats", []))


def rail(world):
    with _quiet():
        return [e.get("text", "") for e in DS._build_diplomatic_events_section(world, "France")]


# ═════════════ SFR-D14: the copy slips ════════════════════════════════════════

class TestSFRD14TheCopySlips:

    def test_i_the_answer_opens_its_sentence(self, shipped):
        client, _ = shipped
        assert ask(client, "where is Napoleon?").startswith("The Emperor Napoleon stands at Lorraine")

    def test_i_seam_down_reads_lower_case(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(QD, "_own_marshal_name",
                            lambda world, m: DN.marshal_honorific(world, m.name))
        assert ask(client, "where is Napoleon?").startswith("the Emperor Napoleon stands at")

    def test_ii_the_standing_order_reads_its_verb(self, shipped):
        client, _ = shipped
        ask(client, "Davout, march to Franconia")
        answer = ask(client, "where is Davout?")
        assert "Under a standing order to march to Franconia." in answer, answer
        assert "move to order" not in answer

    def test_ii_seam_down_splices_the_raw_type(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(QD, "_order_phrase", lambda order: (
            f"Under a standing {order.command_type.replace('_', ' ').lower()} order — {order.target}."))
        ask(client, "Davout, march to Franconia")
        assert "Under a standing move to order — Franconia." in ask(client, "where is Davout?")

    GRANT = {"pair": ["France", "Britain"], "turns": 9, "orders": [], "cut_off": [],
             "marching": [{"marshal": "Massena", "nation": "France"},
                          {"marshal": "Murat", "nation": "France"}]}

    def test_iii_the_grant_lists_its_names_in_prose(self, world):
        line = WD._grant_message(world, dict(self.GRANT))
        assert "Massena and Murat hold under your own orders" in line, line

    def test_iii_seam_down_reads_a_comma_list(self, world, monkeypatch):
        monkeypatch.setattr(WD, "_names_in_prose", lambda names: ", ".join(names))
        assert "Massena, Murat hold under your own orders" in WD._grant_message(world, dict(self.GRANT))

    def test_iv_the_court_carries_its_article(self, shipped):
        client, _ = shipped
        answer = ask(client, "is Milan safe?")
        assert answer.startswith("Milan is the Kingdom of Italy's, Sire"), answer
        assert ask(client, "who holds Milan?") == "Milan is held by the Kingdom of Italy."

    def test_iv_seam_down_drops_the_article(self, shipped, monkeypatch):
        client, _ = shipped
        from backend.game_logic.formations import formed_display_name
        monkeypatch.setattr(QD, "_court", lambda world, nation, start=False:
                            formed_display_name(world, nation) if nation else "no one")
        assert ask(client, "is Milan safe?").startswith("Milan is Kingdom of Italy's, Sire")

    def test_iv_a_plural_court_takes_the_bare_apostrophe(self):
        assert QD._possessive("the Papal States") == "the Papal States'"
        assert QD._possessive("the Kingdom of Italy") == "the Kingdom of Italy's"

    def test_v_the_office_takes_the_adjective(self):
        assert DN.nation_office("Austria", "court") == "the Austrian court"
        assert DN.nation_office("KingdomOfItaly", "ambassador") == "the Italian ambassador"
        assert DN.nation_office("Ottoman", "court") == "the Ottoman court"

    def _send_armistice(self, client):
        post(client, "Talleyrand, offer Austria an armistice")
        with _quiet():
            r = client.post("/respond_to_diplomatic_dialogue", json={"choice": "1"}).json()
        return str(r.get("message") or "") + " " + str((r.get("proposal_result") or {}).get("message") or "")

    def test_v_talleyrand_departs_for_the_austrian_court(self, shipped):
        client, _ = shipped
        text = self._send_armistice(client)
        assert "departs for the Austrian court" in text, text

    def test_v_seam_down_splices_the_tag(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(DN, "nation_office", lambda nation, office: f"the {nation} {office}")
        assert "departs for the Austria court" in self._send_armistice(client)

    def _truce_top_up(self, world):
        world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "ARMISTICE"
        world.marshals["Massena"].location = "Rome"
        WD._offer_event(world, {"nation": "France", "marshal": "Massena",
                                "from": "Rome", "to": "Lyonnais"}, "Britain", 9)
        return " ".join(page(world))

    def test_vi_a_top_up_under_a_truce_says_the_truce(self, world):
        text = self._truce_top_up(world)
        assert "under the truce with Britain" in text, text
        assert "under the peace" not in text

    def test_vi_seam_down_says_the_peace(self, world, monkeypatch):
        monkeypatch.setattr(WD, "treaty_word", lambda world, a, b: "peace")
        assert "under the peace with Britain" in self._truce_top_up(world)


# ═════════════ SFR-D15: the digest reads the battle a report fought ═════════════

class TestSFRD15TheDigestReadsTheOutcome:

    DETAILS = {"message": "\n[Combat] Murat leads the charge! (Aggressive: +15% attack)\nMurat is beaten.",
               "battle_report": {"casualty_summary": {"attacker_name": "Murat",
                                                      "defender_name": "ArchdukeJohn"},
                                 "headline": "A defeat at Munich"}}

    def test_the_nested_report_is_the_battle(self):
        from tools.playtest_driver import _battle_for_digest
        assert _battle_for_digest(self.DETAILS) is self.DETAILS["battle_report"]
        assert _battle_for_digest({"message": "x"}) == {"message": "x"}

    def test_the_driver_hands_the_nested_report_to_its_reader(self):
        source = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert 'self.d.battle(_battle_for_digest(report["battle_details"]))' in source


# ═════════════ SFR-D17: a rout is placed on its battle's field ═══════════════════

class TestSFRD17OneBattleOnePlace:

    def _rout(self, world):
        world.marshals["Massena"].strength = 9000
        turn = int(world.current_turn)
        world.log_event({"type": "battle", "attacker": "Massena", "attacker_nation": "France",
                         "defender": "Mack", "defender_nation": "Austria", "location": "Tyrol",
                         "outcome": "defender_decisive_victory", "attacker_casualties": 3000,
                         "defender_casualties": 500, "turn": turn})
        world.log_event({"type": "retreat", "marshal": "Massena", "nation": "France",
                         "from": "Munich", "to": "Swabia", "forced": True, "turn": turn})
        return " ".join(page(world))

    def test_the_rout_is_told_at_the_battle(self, world):
        text = self._rout(world)
        assert "broken at Tyrol" in text, text
        assert "broken at Munich" not in text

    def test_seam_down_reads_the_march_origin(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_rout_field", lambda window, e: e.get("from", "the field"))
        assert "broken at Munich" in self._rout(world)


# ═════════════ SFR-D21: a march its first step finished is done ══════════════════

class TestSFRD21TheOneStepMarchEnds:

    def test_the_march_completes_at_its_own_turns_end(self, shipped):
        client, world = shipped
        ask(client, "Ney, march to Lorraine")
        assert world.marshals["Ney"].location == "Lorraine"
        reports = post(client, "end turn").get("strategic_reports") or []
        ney = [r for r in reports if r.get("marshal") == "Ney"]
        assert ney and ney[0].get("order_status") == "completed", ney
        assert "0 turns remaining" not in str(ney)
        assert world.marshals["Ney"].strategic_order is None

    def test_seam_down_lingers_a_turn(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(ST, "_arrived_on_the_first_step", lambda marshal, order: False)
        monkeypatch.setattr(ST, "_countdown_clause",
                            lambda remaining: f" ({DN.plural(remaining, 'turn')} remaining)")
        ask(client, "Ney, march to Lorraine")
        reports = post(client, "end turn").get("strategic_reports") or []
        assert any("Ney is marching to Lorraine (0 turns remaining)" in str(r.get("message"))
                   for r in reports), reports
        assert world.marshals["Ney"].strategic_order is not None

    def test_a_countdown_with_nothing_left_says_nothing(self):
        assert ST._countdown_clause(0) == ""
        assert ST._countdown_clause(2) == " (2 turns remaining)"


# ═════════════ SFR-D27: closed by its reproduction ═══════════════════════════════

class TestSFRD27TheNeighboursAreTheMaps:
    """The answer is the registry's own `adjacent` list, and Paris and
    Ile-de-France are not adjacent on the authored map — the oddity is the
    map's, not the copy's."""

    def test_the_answer_is_the_registry(self, shipped):
        client, world = shipped
        for place in ("Orleanais", "Paris", "Swabia"):
            answer = ask(client, f"what borders {place}?")
            for n in world.get_region(place).adjacent_regions:
                assert n in answer, (place, n, answer)
        assert "Ile-de-France" not in world.get_region("Paris").adjacent_regions


# ═════════════ SFR-D30: a top-up is news once, and only abroad ═══════════════════

class TestSFRD30TheArrivedMarshalIsNotStranded:

    def _stale_morning(self, world):
        world.marshals["Ney"].location = "Swabia"
        WD._offer_event(world, {"marshal": "Ney", "nation": "France", "from": "Swabia",
                                "to": "Franche-Comte"}, "Austria", 3)
        first = " ".join(page(world))
        world.current_turn += 1
        world.marshals["Ney"].location = "Franche-Comte"
        return first, " ".join(page(world))

    def test_told_the_morning_it_happens_and_not_after(self, world):
        first, second = self._stale_morning(world)
        assert "Ney is on the wrong side of the frontier at Swabia" in first, first
        assert "wrong side of the frontier" not in second, second

    def test_seam_down_strands_him_again(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_mid_treaty_road_is_current", lambda world, e, p: True)
        _, second = self._stale_morning(world)
        assert "Ney is on the wrong side of the frontier at Swabia" in second


# ═════════════ SFR-D32 / D33: the levy and the famine count true ═════════════════

def _open_the_levy(world):
    for m in world.marshals.values():
        if m.nation == "France":
            m.strength = int(m.strength * 0.5)
    world.marshals["Soult"].location = "Paris"     # a marshal stands to receive them
    from backend.commands.economy_executor import get_levy_status
    assert get_levy_status(world, "France")["open"]


class TestSFRD32TheLevyAfterADraw:

    def _morning_after_a_draw(self, world):
        _open_the_levy(world)
        world.log_event({"type": "recruitment", "marshal": "Soult", "nation": "France",
                         "amount": 10000, "recruit_type": "infantry", "location": "Paris"})
        world.current_turn += 1
        with _quiet():
            head = DS._build_headline(world, "France", record=False) or {}
        return head

    def test_a_drawn_levy_does_not_nag_the_next_morning(self, world):
        head = self._morning_after_a_draw(world)
        assert head.get("class") != "levy_open"
        assert not any("collect them" in b or "levy" in b for b in head.get("sub_beats", []))

    def test_seam_down_nags(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_levy_drawn_lately", lambda world, nation: False)
        head = self._morning_after_a_draw(world)
        texts = [head.get("text", "")] + list(head.get("sub_beats", []))
        assert any("establishment" in t or "levy" in t for t in texts), texts


def _famine(world, rows):
    for (turn, marshal, losses) in rows:
        world.event_log.append({"type": "supply_attrition", "marshal": marshal, "nation": "France",
                                "region": "Swabia", "losses": losses, "cause": "shortage",
                                "turn": turn})


class TestSFRD32bTheNewcomerIsNotCounted:

    def test_the_run_is_true_of_who_starved_that_long(self, world):
        _famine(world, [(t, "Lannes", 500) for t in (10, 11, 12, 13)] + [(13, "Soult", 300)])
        assert DS._famine_veterans(world, "France", "Swabia", ["Lannes", "Soult"], 4) == ["Lannes"]
        assert DS._famine_veterans(world, "France", "Swabia", ["Lannes", "Soult"], 1) == ["Lannes", "Soult"]

    def test_the_escalation_names_the_veterans(self, world):
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
        world.regions["Swabia"].controller = "France"
        for name in ("Lannes", "Soult"):
            world.marshals[name].location = "Swabia"
            world.marshals[name].strength = 45000
        _famine(world, [(t, "Lannes", 500) for t in (10, 11, 12, 13)] + [(13, "Soult", 300)])
        cand = DS._supply_strain_candidate(world, "France")
        assert cand and cand["fields"]["who_run"] == "Lannes", cand and cand["fields"]
        assert cand["fields"]["who"] == "Soult and Lannes"

    def test_seam_down_counts_the_newcomer(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_famine_veterans", lambda w, p, r, names, run: list(names))
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
        world.regions["Swabia"].controller = "France"
        for name in ("Lannes", "Soult"):
            world.marshals[name].location = "Swabia"
            world.marshals[name].strength = 45000
        _famine(world, [(t, "Lannes", 500) for t in (10, 11, 12, 13)] + [(13, "Soult", 300)])
        assert DS._supply_strain_candidate(world, "France")["fields"]["who_run"] == "Soult and Lannes"


class TestSFRD33TheTollCountsItsOwnTurns:

    def test_the_toll_is_summed_over_the_run(self, world):
        _famine(world, [(10, "Davout", 1000), (11, "Davout", 980), (12, "Davout", 780), (13, "Davout", 875)])
        assert DS._famine_toll(world, "France", "Swabia", 4) == 3635
        assert DS._famine_toll(world, "France", "Swabia", 3) == 2635
        assert DS._famine_toll(world, "France", "Swabia", 0) is None

    def _fourth_morning(self, world):
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Paris"
        world.regions["Swabia"].controller = "France"
        for name in ("Davout", "Lannes"):
            world.marshals[name].location = "Swabia"
            world.marshals[name].strength = 40000
        texts = []
        for turn, losses in ((10, 1000), (11, 980), (12, 780), (13, 875)):
            for name in ("Davout", "Lannes"):
                world.event_log.append({"type": "supply_attrition", "marshal": name, "nation": "France",
                                        "region": "Swabia", "losses": losses // 2, "cause": "shortage",
                                        "turn": turn})
            world.current_turn = turn + 1
            with _quiet():
                head = DS._build_headline(world, "France", record=True) or {}
            texts.append(" ".join([head.get("text", "")] + list(head.get("sub_beats", []))))
        return texts

    def test_the_escalated_line_states_the_runs_toll(self, world):
        texts = self._fourth_morning(world)
        famine = [t for t in texts if "turns of famine at Swabia" in t or "over what Swabia can feed" in t]
        assert famine, texts
        assert "3,634 men" in famine[-1] or "3,635 men" in famine[-1], famine[-1]

    def test_seam_down_states_the_windows_toll(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_famine_toll", lambda w, p, r, run: None)
        texts = self._fourth_morning(world)
        famine = [t for t in texts if "turns of famine at Swabia" in t or "over what Swabia can feed" in t]
        # the window's last two turns (780 + 874) beside "4 turns of famine"
        assert famine and "4 turns of famine at Swabia now. 1,654 men gone" in famine[-1], famine


# ═════════════ SFR-D36 / EG-X3 / SFR-B9: the page's order ═══════════════════════

def _mauled(world, name):
    world.marshals[name].strength = 9000
    return {"type": "battle", "attacker": name, "attacker_nation": "France", "defender": "Mack",
            "defender_nation": "Austria", "location": "Tyrol", "outcome": "defender_tactical_victory",
            "attacker_casualties": 3133, "defender_casualties": 1000, "turn": world.current_turn}


def _italy_falls(world):
    return {"type": "nation_eliminated", "nation": "KingdomOfItaly", "lord": "France",
            "turn": world.current_turn}


class TestSFRD36TheSatelliteOutranksTheMauledCorps:

    def test_the_satellite_leads(self, world):
        world.log_event(_mauled(world, "Murat"))
        world.log_event(_italy_falls(world))
        texts = page(world)
        assert texts[0].startswith("Sire — the Kingdom of Italy is no longer ours."), texts
        assert DS.HEADLINE_WEIGHTS["own_mauled"] < DS._vassal_lost_weight() \
            < DS.HEADLINE_WEIGHTS["garrison_stormed"]

    def test_seam_down_leads_with_the_corps(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_vassal_lost_weight", lambda: 84)
        world.log_event(_mauled(world, "Murat"))
        world.log_event(_italy_falls(world))
        assert "mauled" in page(world)[0]


class TestEGX3TheSatelliteIsNeverCrowdedOff:
    """CMD-H's world turn 6, as the gate measured it: a capture leads, the
    reversal and a broken corps take both slots (three classes, so the
    diverse tail has nothing to vary), and the satellite's fall had none."""

    @staticmethod
    def _cand(cls, text):
        return {"class": cls, "text": text, "identity": text,
                "weight": int(DS.HEADLINE_WEIGHTS[cls])}

    def _crowded(self, world):
        page_ = DS._select_headline(world, [
            self._cand("marshal_captured", "Sire — General Teulie has been taken."),
            self._cand("marshal_reversal", "Sire — Ney, the Duke of Elchingen, is broken."),
            self._cand("own_broken", "Sire — Massena's corps has been broken at Munich."),
            self._cand("vassal_lost", "Sire — the Kingdom of Italy is no longer ours."),
        ], record=False)
        return [page_["text"]] + list(page_["sub_beats"])

    def test_the_fall_rides_beneath(self, world):
        texts = self._crowded(world)
        assert texts[0] == "Sire — General Teulie has been taken.", texts
        assert "Sire — the Kingdom of Italy is no longer ours." in texts, texts

    def test_seam_down_crowds_it_off(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_rides_beneath_classes", lambda: ())
        assert not any("Kingdom of Italy" in t for t in self._crowded(world))


class TestSFRB9TheFleetOutranksAClientGeneral:

    def _morning(self, world):
        world.marshals["Ney"].original_nation = "KingdomOfItaly"     # a client's general
        world.log_event({"type": "trafalgar", "winner": "Britain", "loser": "France",
                         "decisive": True, "battle_name": "the Channel action",
                         "context": "diversion", "turn": world.current_turn,
                         "losses": {"France": {"France": 22}, "Britain": {"Britain": 3}}})
        world.log_event({"type": "marshal_captured", "marshal": "Ney", "nation": "France",
                         "captor": "Austria", "location": "Milan", "turn": world.current_turn})
        with _quiet():
            return DS._build_headline(world, "France", record=False) or {}

    def test_the_fleet_leads(self, world):
        head = self._morning(world)
        assert head["class"] == "fleet_shattered", head
        assert any("has been taken" in b for b in head["sub_beats"])

    def test_seam_down_leads_with_the_capture(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_our_wound_weight", lambda world, key, weight: int(weight))
        assert self._morning(world)["class"] == "marshal_captured"


# ═════════════ SFR-D43: a truce is not the war's end ═════════════════════════════

class TestSFRD43TheTruceIsATruce:

    def _truce(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        world.regions["Volhynia"].controller = "France"
        for m in list(world.marshals.values()):
            if m.nation == "France" and m.name != "Davout":
                m.location = "Paris"
            elif m.nation == "Russia":
                m.location = world.get_nation_capital("Russia")
        world.marshals["Davout"].location = "Volhynia"
        with _quiet():
            set_diplomatic_state(world, "France", "Russia", "WAR")
            world.current_turn = 18
            set_diplomatic_state(world, "France", "Russia", "ARMISTICE")
        return " ".join(page(world))

    def test_the_truce_says_paused_not_over(self, world):
        text = self._truce(world)
        assert "a truce with Russia holds the guns silent — the war is paused, not over." in text, text
        assert "the war with Russia is over" not in text

    def test_seam_down_says_the_war_is_over(self, world, monkeypatch):
        monkeypatch.setattr(WD, "treaty_word", lambda world, a, b: "peace")
        assert "the war with Russia is over" in self._truce(world)


# ═════════════ SFR-D44: the decay says what moved ════════════════════════════════

class TestSFRD44TheDecaySaysWhatMoved:

    def test_a_tie_keeps_its_decimal(self):
        assert WS._fortify_percents(0.0625, 0.06) == ("6.2%", "6.0%")
        assert WS._fortify_percents(0.09, 0.08) == ("9%", "8%")

    def _decay_lines(self, world):
        davout = world.marshals["Davout"]
        from backend.models.marshal import StrategicOrder
        davout.fortified = True
        davout.defense_bonus = 0.10
        davout.cumulative_fortification_turns = 8
        davout.strategic_order = StrategicOrder(command_type="HOLD", target=davout.location,
                                                target_type="region", started_turn=1,
                                                original_command="Davout, hold")
        lines = []
        for _ in range(4):
            with _quiet():
                events = world._process_tactical_states() or []
            lines += [e["message"] for e in events
                      if e.get("type") == "fortify_decayed" and e.get("marshal") == "Davout"]
        return lines

    def test_no_morning_reads_n_to_n(self, world):
        lines = self._decay_lines(world)
        assert lines, lines
        for line in lines:
            was, now = line.split(": ", 1)[1].split(" → ")
            assert was != now, line

    def test_seam_down_reads_n_to_n(self, world, monkeypatch):
        monkeypatch.setattr(WS, "_fortify_percents",
                            lambda old, new: (f"{int(old * 100)}%", f"{int(new * 100)}%"))
        assert any(line.endswith("9% → 9%") for line in self._decay_lines(world))


# ═════════════ SFR-B4: the auction's close is told ═══════════════════════════════

class TestSFRB4TheAuctionCloses:

    def _run(self, world, monkeypatch, prices):
        real = INT.get_nation_intent
        state = {"price": "bandwagon"}

        def fake(nation, w):
            view = real(nation, w)
            if nation == "Sardinia":
                return INT.IntentView(nation, view.want_id or "x",
                                      view.want_title or "The House of Savoy Restored",
                                      view.want_type, view.against, 66, state["price"], False)
            return view
        monkeypatch.setattr(INT, "get_nation_intent", fake)
        world.allegiance_auctions = {}
        lines = []
        for i, price in enumerate(prices):
            world.current_turn = 10 + i
            state["price"] = price
            world.pending_dispatch_events = []
            with _quiet():
                AD.process_allegiance_auctions(world)
            lines += rail(world)
        return lines

    def test_a_lapsed_auction_says_so_and_retires_its_notice(self, world, monkeypatch):
        lines = self._run(world, monkeypatch, ["bandwagon", "coerce"])
        assert any("The allegiance of Sardinia is in play" in t for t in lines), lines
        assert any("The moment passes: Sardinia no longer weighs the flip" in t for t in lines), lines
        titles = [n.get("title", "") for n in world.notifications.get_pending()]
        assert not any("allegiance is in play" in t for t in titles), titles

    def test_seam_down_closes_in_silence(self, world, monkeypatch):
        monkeypatch.setattr(AD, "_announce_allegiance_close", lambda w, n, o, winner: None)
        lines = self._run(world, monkeypatch, ["bandwagon", "coerce"])
        assert not any("bidding" in t or "moment passes" in t for t in lines), lines
        titles = [n.get("title", "") for n in world.notifications.get_pending()]
        assert any("Sardinia's allegiance is in play" in t for t in titles), titles

    def test_every_outcome_has_its_words(self, world):
        for outcome, winner, words in (
                ("flipped", "Austria", "she signs a defensive alliance with Austria"),
                ("player_offer", "France", "closed in our favour"),
                ("player_won_no_pact", "France", "too cool for any pact"),
                ("no_suitor", None, "no court to take her")):
            world.pending_dispatch_events = []
            AD._announce_allegiance_close(world, "Sardinia", outcome, winner)
            assert any(words in t for t in rail(world)), (outcome, rail(world))


# ═════════════ SFR-B6: a grievance with no clock left ════════════════════════════

class TestSFRB6TheLastTurnIsNoThreat:

    def test_no_turns_left_reads_until_it_lapses(self, world):
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        murat.jealous_of = "Ney"
        murat.jealousy_turns_remaining = 0
        line = J._standing_cost_detail(murat, ney)
        assert line.startswith("Free, and it fixes nothing. Until his grievance lapses he brings"), line
        murat.jealousy_turns_remaining = 3
        assert "For 3 more turns he brings" in J._standing_cost_detail(murat, ney)

    def test_seam_down_threatens_for_zero_turns(self, world, monkeypatch):
        monkeypatch.setattr(J, "_stand_duration_phrase", lambda turns: f"For {turns} more turns")
        murat, ney = world.marshals["Murat"], world.marshals["Ney"]
        murat.jealous_of = "Ney"
        murat.jealousy_turns_remaining = 0
        assert "For 0 more turns he brings" in J._standing_cost_detail(murat, ney)

    def test_the_capture_tool_stages_a_live_clock(self):
        source = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        assert 'world.marshals["Murat"].jealousy_turns_remaining = 3' in source


# ═════════════ SFR-B7: a remitted tribute says so ════════════════════════════════

class TestSFRB7TheRemissionIsNamed:

    def _switzerland(self, world):
        world.vassals["Switzerland"]["remission_left"] = 8
        rows = (DL.build_diplomatic_ledger(world).get("vassals") or {}).get("rows") or []
        return next(r for r in rows if r.get("name") == "Switzerland")

    def test_the_note_names_the_remission(self, world):
        row = self._switzerland(world)
        assert row["tribute"] == 0
        assert row["tribute_note"] == "+0g/turn — remitted for 8 more collections (75% of their income when it resumes)", row["tribute_note"]

    def test_seam_down_quotes_the_rate_beside_a_zero(self, world, monkeypatch):
        monkeypatch.setattr(DL, "_tribute_note", lambda w, n, t, pct: f"+{t}g/turn ({pct}% of their income)")
        assert self._switzerland(world)["tribute_note"] == "+0g/turn (75% of their income)"

    def test_the_card_prints_the_note(self):
        source = (REPO / "godot-client" / "project-sovereign" / "scripts" / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'if v.has("tribute_note"):' in source


# ═════════════ SFR-B8: Trafalgar is fought once ══════════════════════════════════

class TestSFRB8TrafalgarOnce:

    RESULT = {"winner": "Britain", "loser": "France", "decisive": True,
              "battle_name": "the Channel action", "context": "diversion",
              "losses": {"France": {"France": 12}, "Britain": {"Britain": 2}}}

    def _two_actions(self, world):
        lines = []
        for turn in (6, 7):
            world.current_turn = turn
            world.pending_dispatch_events = []
            NV._log_fleet_action(world, dict(self.RESULT))
            lines += [t for t in rail(world) if "line has shattered" in t]
        return lines

    def test_the_second_is_named_by_its_waters(self, world):
        lines = self._two_actions(world)
        assert lines[0].startswith("TRAFALGAR:"), lines
        assert lines[1].startswith("THE CHANNEL ACTION:"), lines
        assert world.battle_counts[NV.DECISIVE_ACTIONS_KEY] == 2
        from backend.campaign_log import format_event_oneliner
        logged = [e for e in world.event_log if e.get("type") == "trafalgar"]
        assert format_event_oneliner(logged[-1]).startswith("THE CHANNEL ACTION:")

    def test_seam_down_fights_trafalgar_twice(self, world, monkeypatch):
        monkeypatch.setattr(NV, "fleet_action_banner", lambda nth, result: "TRAFALGAR")
        assert all(t.startswith("TRAFALGAR:") for t in self._two_actions(world))


# ═════════════ SFR-B12: the rung in words ════════════════════════════════════════

class TestSFRB12TheRungInWords:

    def test_prussias_intent_says_what_the_rung_means(self, shipped):
        _, world = shipped
        summary = INT.build_intent_payload("Prussia", world)["summary"]
        assert summary.startswith("prepared to go as far as joining the stronger side for pay"), summary

    def test_seam_down_reads_the_ladder_word(self, shipped, monkeypatch):
        _, world = shipped
        monkeypatch.setattr(INT, "price_words", lambda price: INT.PRICE_DISPLAY[price].lower())
        assert "as far as service to the strong" in INT.build_intent_payload("Prussia", world)["summary"]


# ═════════════ SFR-B13: the war purpose names the court ══════════════════════════

class TestSFRB13TheCourtByName:

    def test_the_prompt_names_the_papal_states(self, shipped):
        client, _ = shipped
        assert ask(client, "declare war on PapalStates") == "Choose your war purpose against the Papal States."

    def test_seam_down_prints_the_tag(self, shipped, monkeypatch):
        client, _ = shipped
        monkeypatch.setattr(DIP, "war_purpose_prompt",
                            lambda world, target: f"Choose your war purpose against {target}.")
        assert ask(client, "declare war on Ottoman") == "Choose your war purpose against Ottoman."


# ═════════════ SFR-B15: the satellite's remedy, where the reader looks ═══════════

class TestSFRB15TheRemedyIsNamed:

    VARS = {"nation": "KingdomOfItaly", "loyalty": 32,
            "recovery_hint": "Invest in them, grant them autonomy, garrison their capital, "
                             "or cede them a province to steady them."}

    def test_the_line_names_the_court_and_its_chips(self):
        line = DS._vassal_unrest_line(dict(self.VARS))
        assert line.startswith("Talleyrand reports unrest in the Kingdom of Italy (loyalty 32). Invest"), line
        assert "Loosen Rein" in line and "the Diplomatic Ledger's Vassals tab (press D, then 6)" in line

    def test_seam_down_prints_the_tag(self, monkeypatch):
        monkeypatch.setattr(DS, "_vassal_unrest_line", lambda v: f"Talleyrand reports unrest in {v['nation']}.")
        assert DS._format_dispatch_event_text("diplomatic_vassal_unrest", dict(self.VARS)) \
            == "Talleyrand reports unrest in KingdomOfItaly."

    def test_the_digest_prints_it_as_the_dispatch_does(self):
        from tools import playtest_driver as PD
        assert "diplomatic_vassal_unrest" in PD.VASSAL_DISPATCH_TYPES


# ═════════════ EA-E4: the count and its noun ═════════════════════════════════════

class TestEAE4OneCourtIsACourt:

    def test_one_court(self):
        assert DT._courts_at_the_table(1) == "1 court"
        assert DT._courts_at_the_table(3) == "3 courts"
        line = DT.resolve_settlement_voice_line(
            "settlement_multi_court_table_talleyrand", war_label="the war with Austria",
            court_count=DT._courts_at_the_table(1), binding_constraint="")
        assert "seats 1 court at the table." in line, line

    def test_seam_down_reads_one_courts(self, monkeypatch):
        monkeypatch.setattr(DT, "_courts_at_the_table", lambda n: f"{n} courts")
        line = DT.resolve_settlement_voice_line(
            "settlement_multi_court_table_talleyrand", war_label="the war with Austria",
            court_count=DT._courts_at_the_table(1), binding_constraint="")
        assert "seats 1 courts at the table." in line


# ═════════════ The siblings (RR3-X1 … X12, all FIXED) ════════════════════════════

class TestTheSiblings:

    def test_x1_a_count_of_one_takes_the_singular(self):
        source = (REPO / "backend" / "intel_report.py").read_text(encoding="utf-8")
        assert "No word from {plural(count, 'province')}" in source
        source = (REPO / "backend" / "game_logic" / "cabinet_rows.py").read_text(encoding="utf-8")
        assert "{_plural(cooldown, 'turn')} before she can be made a vassal again" in source

    def test_x2_the_eta_reads_the_order_in_words(self, shipped):
        client, _ = shipped
        ask(client, "Davout, march to Franconia")
        answer = ask(client, "when will Davout arrive?")
        assert answer.startswith("Davout: under a standing order to march to Franconia — "), answer
        assert "move_to" not in answer and ":  —" not in answer

    def test_x3_an_unnamed_envoy_is_the_courts_adjective(self):
        assert AD._ambassador_of("KingdomOfItaly") == "the Italian ambassador"

    def test_x4_the_chancery_names_the_court(self, shipped):
        client, world = shipped
        assert ask(client, "break treaty with Ottoman") == \
            "There is no treaty with the Ottoman Empire to break, Your Excellency."
        assert DIP._court_named(world, "PapalStates", start=True) == "The Papal States"

    def test_x5_the_log_names_the_courts_the_men_and_the_treaty(self, world):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "evacuation_granted", "nation_a": "France", "nation_b": "KingdomOfItaly",
            "region": "Rome", "turns": 1, "marshals": ["Massena", "ArchdukeCharles"],
            "destinations": {"Massena": "Lyonnais"}, "cut_off": [], "mid_treaty": True,
            "treaty": "truce", "turn": 5}, "France", world)
        assert line == ("Massena and Archduke Charles put on the road home from Rome to Lyonnais "
                        "under the truce with the Kingdom of Italy — 1 turn"), line

    def test_x8_a_bond_of_1805_names_its_button(self, shipped):
        client, _ = shipped
        answer = ask(client, "break treaty with Bavaria")
        assert answer.endswith("The Cabinet's Downgrade (F1 → Bavaria → Downgrade) loosens it."), answer
        assert "'Talleyrand," not in answer

    def test_x9_the_works_round_their_figure(self):
        source = (REPO / "backend" / "models" / "world_state.py").read_text(encoding="utf-8")
        assert "fortifications strengthen: +{round(new_bonus * 100)}% defense" in source

    def test_x7_the_satellite_headline_names_it_with_its_article(self, world, monkeypatch):
        world.log_event(_italy_falls(world))
        assert page(world)[0].startswith("Sire — the Kingdom of Italy is no longer ours.")
        from backend.game_logic.formations import formed_display_name
        monkeypatch.setattr(DS, "_satellite_name", formed_display_name)
        assert page(world)[0].startswith("Sire — Kingdom of Italy is no longer ours.")

    def test_x10_a_client_generals_destruction_weighs_as_the_satellite(self, world):
        world.marshals["Ney"].original_nation = "KingdomOfItaly"
        assert DS._our_wound_weight(world, "Ney", 96) == DS._vassal_lost_weight()
        assert DS._our_wound_weight(world, "Davout", 96) == 96

    def test_x12_the_auction_notice_names_the_court(self, world):
        assert AD._allegiance_notice_title(world, "PapalStates") == "The Papal States' allegiance is in play"
        assert AD._allegiance_notice_title(world, "Sardinia") == "Sardinia's allegiance is in play"

    # ── found re-reading narration C6's CMD-H sample ──────────────────────────

    def _three_peaces(self, world):
        for court in ("Austria", "Britain", "Russia"):
            world.log_event({"type": "evacuation_granted", "nation_a": "France", "nation_b": court,
                             "region": "", "turns": 4, "marshals": [], "destinations": {},
                             "cut_off": [], "treaty": "peace",
                             "message": "The peace grants safe passage home."})
        return page(world)

    def test_x13_one_settlement_is_one_line(self, world):
        texts = self._three_peaces(world)
        assert texts[0] == ("Sire — the war with Austria, Britain and Russia is over. "
                            "The peace grants safe passage home."), texts
        assert not any("the war with Russia is over" in t for t in texts[1:]), texts

    def test_x13_seam_down_tells_one_court_at_a_time(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_one_peace_one_line", lambda candidates: candidates)
        texts = self._three_peaces(world)
        assert texts[0] == "Sire — the war with Austria is over. The peace grants safe passage home.", texts

    def _brewing(self, world):
        world.log_event({"type": "coalition_brewing_started", "target_nation": "France",
                         "threat_level": 61, "qualifying_nations": ["Austria", "Russia"]})
        first = " ".join(page(world))
        world.current_turn += 1
        return first, " ".join(page(world))

    def test_x14_the_brewing_is_told_once(self, world):
        first, second = self._brewing(world)
        assert "drawing together against us" in first, first
        assert "drawing together against us" not in second, second

    def test_x14_seam_down_tells_it_twice(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_brewing_is_news", lambda world, e: True)
        assert "drawing together against us" in self._brewing(world)[1]

    def _the_table_settles(self, world):
        world.log_event({"type": "settlement_summary", "war_id": "war_1", "war_ended": True,
                         "white_peace": True,
                         "covered_enemy_participants": ["Austria", "Britain", "Russia"],
                         "proposer_members": ["France", "Spain"],
                         "accepting_members": ["Britain", "Austria", "Russia"]})
        return self._three_peaces(world)

    def test_x13_the_tables_settlement_leads_as_one_peace(self, world):
        texts = self._the_table_settles(world)
        assert texts[0] == ("Sire — peace with Austria, Britain and Russia is signed. "
                            "A white peace — the map stands as it was."), texts
        assert not any("is over" in t for t in texts), texts

    def test_x13_seam_down_the_settlement_is_not_on_the_page(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_settlement_peace", lambda world, e, nation: None)
        assert self._the_table_settles(world)[0].startswith("Sire — the war with Austria, Britain and Russia is over.")

    def _league_declares(self, world):
        for court in ("Britain", "Russia"):
            world.diplomatic_states[world._make_diplo_key("France", court)] = "WAR"
            world.log_event({"type": "war_declaration", "aggressor": court, "target": "France",
                             "previous_state": "PEACE"})
        with _quiet():
            first = DS._build_headline(world, "France", record=True) or {}
        world.current_turn += 1
        with _quiet():
            second = DS._build_headline(world, "France", record=True) or {}
        return ([first.get("text", "")] + list(first.get("sub_beats", [])),
                [second.get("text", "")] + list(second.get("sub_beats", [])))

    def test_x15_the_mornings_declarations_are_one_line_told_once(self, world):
        first, second = self._league_declares(world)
        assert any(t.startswith("Sire — Britain and Russia are at war with France.") for t in first), first
        assert not any("at war with France" in t or "and France are at war" in t for t in second), second

    def test_x15_seam_down_names_one_court(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_one_war_one_line", lambda w, decls, add: [
            add("war_touches_us", line=d["line"]) for d in decls] and None)
        first, _ = self._league_declares(world)
        told = [t for t in first if "and France are at war" in t]
        assert len(told) == 1, first

    def test_x15_seam_down_tells_it_twice(self, world, monkeypatch):
        monkeypatch.setattr(DS, "_declaration_is_news", lambda w, key: True)
        _, second = self._league_declares(world)
        assert any("are at war with France" in t for t in second), second
