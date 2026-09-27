"""Score Mandate — the session exit's residue (September 26, 2026).

The exit (`docs/audits/SR_SESSION_EXIT_2026_09_26.md`) read two played arms on
both trees and found four things this slice fixes, each behind its own lever
whose down arm reproduces the finding, measured at `POST /command` on the
shipped 1805 boot before a line was written:

    F1 (P2)  "is Vienna safe" named Austria's OWN Archduke John as the threat
             to Austria's own capital ("It is safe for a turn or two, no
             longer"); a French corps one march off, the only thing that
             threatened it, was invisible to the answer.
    F2 (P2)  "should Davout attack Mack" weighed NEY (the nearest corps) — the
             named marshal replaced; "what are Ney's odds against Vienna" (the
             Creative AAR player's own turn-5 line) had no desk kind; a
             PROVINCE never reached the what-if ("should Ney attack Vienna",
             "can Ney take Vienna" shrugged).
    F3 (P3)  "how long until the armistice with Russia expires" typed without
             its mark fell to the order parser's shrug, and "what if Lannes
             attacks Mack" to the contingency refusal.
    F4       the driver's digest records a reply's FIRST line, and SR-4a made
             the assault's muster that line — every assault's outcome fell out
             of the archive.

Beside them, the garrison assault's loss arithmetic became ONE method,
`CombatExecutor.garrison_exchange`, so the desk's forecast quotes the exchange
the resolver applies — pinned to the digit against the order itself.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.ai.clause_guards as CG
import backend.ai.question_desk as QD
import backend.main as M
from backend.commands.combat_executor import CombatExecutor
from backend.commands.parser import CommandParser
from backend.game_logic import garrison_report as GR
from backend.models.intel import FULL, PARTIAL, UNKNOWN
from backend.models.marshal import Marshal

REPO_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "playtest_driver", REPO_ROOT / "tools" / "playtest_driver.py")
driver = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("playtest_driver", driver)
_spec.loader.exec_module(driver)

SHRUG = "cannot answer that"


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world with a mock parser (the CRT-7 idiom)."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def ask(client, world, question):
    """A question spends nothing and fights nothing."""
    before = (int(world.actions_remaining), int(world.admin_actions_remaining))
    data = post(client, question)
    after = (int(world.actions_remaining), int(world.admin_actions_remaining))
    assert before == after, (question, before, after)
    assert not data.get("battle_report"), question
    return str(data.get("message") or "")


def coordination_snapshot(world):
    return {key: tuple(m.__dict__.get(f, "<missing>")
                       for f in Marshal.COORDINATION_TRANSIENT_FIELDS)
            for key, m in world.marshals.items()}


def stage_beside(world, marshal_name, region_name):
    """Stand our corps on a province adjacent to `region_name` that holds no
    foreign corps, and return that province."""
    region = world.get_region(region_name)
    for name in region.adjacent_regions:
        near = world.get_region(name)
        if near is None:
            continue
        if any(m.location == name and m.nation != "France"
               and int(m.strength or 0) > 0 for m in world.marshals.values()):
            continue
        world.marshals[marshal_name].location = name
        return name
    raise AssertionError(f"no clear province beside {region_name}")


def see(world, region_name, visibility=FULL):
    world.get_region_intel(region_name).visibility = visibility


# ══════════════════════════════════════════════════════════════════════════
# F1 — "is X safe?" reads the HOLDER's side
# ══════════════════════════════════════════════════════════════════════════
class TestF1TheSafeAnswerReadsTheHolder:

    def test_austrias_own_army_is_named_as_its_cover_not_its_threat(self, shipped):
        client, world = shipped
        message = ask(client, world, "is Vienna safe")
        assert "Austria's own we can see: Archduke John" in message, message
        threats = message.split("Austria's own we can see")[0]
        assert "Archduke John" not in threats, message
        assert "safe for a turn or two, no longer" not in message, message

    def test_the_lever_down_reproduces_the_finding(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_SAFE_ANSWER_READS_THE_HOLDER", False)
        message = ask(client, world, "is Vienna safe")
        assert "Threats we can see: Archduke John of Austria" in message, message
        assert "It is safe for a turn or two, no longer." in message, message

    def test_our_corps_one_march_off_is_the_threat_on_enemy_soil(self, shipped):
        client, world = shipped
        where = stage_beside(world, "Ney", "Vienna")
        message = ask(client, world, "is Vienna safe")
        assert f"Corps at war with Austria within two marches: Ney is at {where}, one march away" in message, message
        assert "looks safe today" not in message and "beyond our reach" not in message, message

    def test_with_nothing_near_enemy_soil_lies_beyond_our_reach(self, shipped):
        client, world = shipped
        for m in world.marshals.values():
            if m.nation != "Austria" and m.location in (
                    set(world.get_region("Vienna").adjacent_regions) | {"Vienna"}):
                m.location = "Paris"
        for m in world.marshals.values():
            if m.nation in ("France", "Bavaria") and world.get_distance(m.location, "Vienna") <= 2:
                m.location = "Paris"
        message = ask(client, world, "is Vienna safe")
        assert "No corps at war with Austria stands within two marches of it" in message, message
        assert "it lies beyond our reach today" in message, message

    def test_our_own_soil_reads_exactly_as_before(self, shipped, monkeypatch):
        client, world = shipped
        up = ask(client, world, "is Paris safe")
        monkeypatch.setattr(QD, "THE_SAFE_ANSWER_READS_THE_HOLDER", False)
        down = ask(client, world, "is Paris safe")
        assert up == down, (up, down)

    def test_an_allys_soil_names_the_allys_enemies(self, shipped):
        client, world = shipped
        message = ask(client, world, "is Munich safe")
        assert "Threats we can see: Mack of Austria" in message, message
        assert "It is held, but threatened." in message, message

    def test_a_foreign_corps_out_of_view_is_never_named(self, shipped):
        client, world = shipped
        john = world.get_marshal("ArchdukeJohn")
        see(world, john.location, UNKNOWN)
        message = ask(client, world, "is Vienna safe")
        assert "Archduke John" not in message, message


# ══════════════════════════════════════════════════════════════════════════
# F2 — the what-if names its marshal
# ══════════════════════════════════════════════════════════════════════════
class TestF2TheWhatIfNamesItsMarshal:

    def test_should_davout_attack_mack_weighs_davout(self, shipped):
        client, world = shipped
        message = ask(client, world, "should Davout attack Mack")
        assert "MUSTER — Davout" in message, message

    def test_the_lever_down_weighs_the_nearest_corps_instead(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_WHAT_IF_NAMES_ITS_MARSHAL", False)
        message = ask(client, world, "should Davout attack Mack")
        assert "MUSTER — Ney" in message, message

    def test_a_named_corps_beyond_reach_is_never_substituted(self, shipped):
        client, world = shipped
        message = ask(client, world, "should Massena attack Mack")
        assert "MUSTER" not in message, message
        assert "Massena stands at Milan, beyond reach of Mack at Swabia" in message, message
        assert "the order would set him in pursuit" in message, message
        assert "within reach." in message, message

    def test_a_foreign_subject_is_not_ours_to_order(self, shipped):
        client, world = shipped
        message = ask(client, world, "should Deroy attack Mack")
        assert "MUSTER" not in message, message
        assert "not ours to order" in message, message

    def test_a_name_nobody_has_is_never_the_nearest_corps(self, shipped):
        """The sweep found the plain sentence INERT: "should Zorglub attack
        Mack" never reaches the desk (CX-R1 refuses the unknown name first).
        With the mark it does — and must not weigh the nearest corps."""
        client, world = shipped
        message = ask(client, world, "should Zorglub attack Mack?")
        assert "MUSTER" not in message, message

    def test_the_classifier_ends_on_a_name_it_cannot_place(self):
        question = QD.classify_board_question(
            "should Zorglub attack Mack", marshals=["Ney", "Davout"],
            enemies=["Mack"], regions=["Vienna", "Swabia"])
        assert question is None, question

    def test_we_still_weighs_the_nearest_corps(self, shipped):
        client, world = shipped
        message = ask(client, world, "what if we attack Mack")
        assert "MUSTER — Ney" in message, message


# ══════════════════════════════════════════════════════════════════════════
# F2 — the odds
# ══════════════════════════════════════════════════════════════════════════
class TestF2TheOdds:

    @pytest.mark.parametrize("q", [
        "what are Ney's odds against Mack",
        "what are Ney’s chances against Mack",
        "what's Ney's chance against Mack",
        "how good are Ney's odds against Mack",
        "what odds does Ney have against Mack",
    ])
    def test_the_odds_are_the_named_marshals_muster(self, shipped, q):
        client, world = shipped
        message = ask(client, world, q)
        assert "MUSTER — Ney" in message, (q, message)
        assert "Nothing has been ordered, and nothing spent." in message, (q, message)

    @pytest.mark.parametrize("q", ["what are our odds against Mack",
                                   "what are the odds against Mack"])
    def test_our_odds_weigh_the_nearest_corps(self, shipped, q):
        client, world = shipped
        message = ask(client, world, q)
        assert "MUSTER — " in message, (q, message)

    def test_the_lever_down_shrugs(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_DESK_READS_THE_ODDS", False)
        message = ask(client, world, "what are Ney's odds against Mack")
        assert SHRUG in message, message

    def test_the_classifier_reads_the_subject_and_the_object(self):
        question = QD.classify_board_question(
            "what are Ney's odds against Vienna", marshals=["Ney", "Davout"],
            enemies=["Mack"], regions=["Vienna", "Swabia"])
        assert question == {"kind": "what_if", "subject": "Vienna",
                            "subject_type": "region", "marshal": "Ney",
                            "marshal_foreign": False}, question


# ══════════════════════════════════════════════════════════════════════════
# F2 — a province is weighed as the order reads it
# ══════════════════════════════════════════════════════════════════════════
class TestF2AProvinceIsWeighed:

    @pytest.mark.parametrize("q", ["what if Ney attacks Vienna",
                                   "should Ney attack Vienna",
                                   "can Ney take Vienna",
                                   "what are Ney's odds against Vienna"])
    def test_out_of_reach_the_order_is_refused_and_the_desk_says_so(self, shipped, q):
        client, world = shipped
        message = ask(client, world, q)
        assert "Ney stands at Rhineland, beyond reach of Vienna this turn" in message, (q, message)
        assert "the order would be refused, and nothing spent" in message, (q, message)
        order = post(client, "Ney, attack Vienna")
        assert order.get("success") is False, order
        assert "cannot reach Vienna" in str(order.get("message")), order

    def test_ours_holds_nothing_to_attack(self, shipped):
        client, world = shipped
        message = ask(client, world, "should Ney attack Rhineland")
        assert message.startswith("Rhineland is ours, Sire — there is nothing there to attack."), message

    def test_a_corps_standing_there_is_weighed_as_the_muster(self, shipped):
        client, world = shipped
        message = ask(client, world, "what if Ney attacks Swabia")
        assert "MUSTER — Ney" in message and "vs Mack" in message, message

    def test_in_the_fog_nothing_in_it_is_named(self, shipped):
        client, world = shipped
        stage_beside(world, "Ney", "Vienna")
        see(world, "Vienna", UNKNOWN)
        message = ask(client, world, "what are Ney's odds against Vienna")
        assert "We have no intelligence on what holds Vienna" in message, message
        assert "25,000" not in message, message

    def test_at_partial_the_garrison_is_a_band_and_no_count_leaks(self, shipped):
        client, world = shipped
        stage_beside(world, "Ney", "Vienna")
        see(world, "Vienna", PARTIAL)
        message = ask(client, world, "what are Ney's odds against Vienna")
        assert "ASSAULT — Ney storms the works at Vienna alone" in message, message
        assert "against a garrison (" in message, message
        assert "25,000" not in message and "31,250" not in message, message
        assert "no count of the garrison" in message, message

    def test_the_forecast_is_the_exchange_the_resolver_applies(self, shipped):
        """shown = applied: the desk's figures are the order's, to the digit."""
        client, world = shipped
        where = stage_beside(world, "Ney", "Vienna")
        # A corps at his side makes the coordination stamp non-zero, so the
        # purity check below can see a stamp the question failed to restore.
        world.marshals["Davout"].location = where
        # A stale stamp from an earlier battle: the question must leave it
        # exactly as it found it (the restore's set-back branch).
        world.marshals["Ney"].total_coordination_attack_bonus = 0.123
        see(world, "Vienna", FULL)
        before = coordination_snapshot(world)
        message = ask(client, world, "what are Ney's odds against Vienna")
        assert coordination_snapshot(world) == before, "the question stamped a field"
        assert world.marshals["Ney"].total_coordination_attack_bonus == 0.123
        assert "from the corps at his side" in message, message
        forecast = re.search(r"about ([\d,]+) of the garrison fall and Ney loses "
                             r"about ([\d,]+) — ([\d,]+) remain", message)
        assert forecast, message
        fell, lost, remain = (int(g.replace(",", "")) for g in forecast.groups())
        order = post(client, "Ney, attack Vienna")
        text = str(order.get("message") or "")
        assert text.startswith("ASSAULT — Ney storms the works at Vienna alone"), text
        result = re.search(r"Garrison: [\d,]+ -> ([\d,]+) \(-([\d,]+)\)", text)
        loss = re.search(r"Ney loses ([\d,]+) troops", text)
        assert result and loss, text
        assert int(result.group(2).replace(",", "")) == fell, (message, text)
        assert int(result.group(1).replace(",", "")) == remain, (message, text)
        assert int(loss.group(1).replace(",", "")) == lost, (message, text)

    def test_the_forecast_spends_no_one_time_bonus(self, shipped):
        client, world = shipped
        davout = world.marshals["Davout"]
        stage_beside(world, "Davout", "Vienna")
        see(world, "Vienna", FULL)
        davout.iron_resolve_stacks = 2
        ask(client, world, "what are Davout's odds against Vienna")
        assert davout.iron_resolve_stacks == 2

    def test_an_allys_province_is_refused_like_the_order(self, shipped):
        client, world = shipped
        munich = world.get_region("Munich")
        assert munich.controller == "Bavaria"
        stage_beside(world, "Ney", "Munich")
        message = ask(client, world, "should Ney attack Munich")
        assert "Bavaria is our ally" in message and "refused" in message, message

    def test_all_three_levers_down_shrug_on_a_province(self, shipped, monkeypatch):
        client, world = shipped
        for lever in ("THE_WHAT_IF_NAMES_ITS_MARSHAL", "THE_DESK_READS_THE_ODDS",
                      "THE_WHAT_IF_WEIGHS_A_PROVINCE"):
            monkeypatch.setattr(QD, lever, False)
        assert SHRUG in ask(client, world, "should Ney attack Vienna")

    def test_the_province_lever_alone_down_shrugs_on_a_province(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(QD, "THE_WHAT_IF_WEIGHS_A_PROVINCE", False)
        assert SHRUG in ask(client, world, "should Ney attack Vienna")


# ══════════════════════════════════════════════════════════════════════════
# F3 — a quantity "how" and a conjecture "what if" are questions
# ══════════════════════════════════════════════════════════════════════════
class TestF3TheQuestionLeads:

    @pytest.mark.parametrize("line", [
        "how long until the armistice with Russia expires",
        "how many turns until the truce with Austria ends",
        "what if Lannes attacks Mack",
        "what if Ney attacks Vienna",
    ])
    def test_the_lead_is_a_question(self, line):
        assert CG.is_question(line) is True

    @pytest.mark.parametrize("line", [
        "how long until the armistice with Russia expires",
        "what if Lannes attacks Mack",
    ])
    def test_the_lever_down_reproduces_the_finding(self, line, monkeypatch):
        monkeypatch.setattr(CG, "A_QUANTITY_OR_CONJECTURE_ASKS", False)
        assert CG.is_question(line) is False

    @pytest.mark.parametrize("line", [
        "Ney, attack Mack", "hold until Davout arrives",
        "if Mack advances, fall back", "Ney, march to Paris",
    ])
    def test_orders_stay_orders(self, line):
        assert CG.is_question(line) is False

    def test_the_desk_answers_without_the_mark(self, shipped):
        client, world = shipped
        message = ask(client, world, "how long until the armistice with Russia expires")
        assert message.startswith("There is no armistice with Russia"), message
        message = ask(client, world, "what if Lannes attacks Mack")
        assert "MUSTER — Lannes" in message, message

    def test_no_corpus_row_changes_its_verdict(self, monkeypatch):
        """Every row that predates the residue keeps its verdict; the
        residue's own two F3 rows (`sre-*`) are the ones that move."""
        corpus = json.loads((REPO_ROOT / "tests" / "data" /
                             "parser_golden_corpus.json").read_text(encoding="utf-8"))
        rows = corpus["entries"]
        lines = [row.get("utterance") or "" for row in rows]
        up = [CG.is_question(line) for line in lines]
        monkeypatch.setattr(CG, "A_QUANTITY_OR_CONJECTURE_ASKS", False)
        down = [CG.is_question(line) for line in lines]
        moved = {rows[i]["id"] for i in range(len(lines)) if up[i] != down[i]}
        assert moved == {"sre-how-long-without-the-mark",
                         "sre-what-if-a-marshal-attacks"}, moved


# ══════════════════════════════════════════════════════════════════════════
# F4 — the digest keeps the assault's result
# ══════════════════════════════════════════════════════════════════════════
ASSAULT_REPLY = (
    "ASSAULT — Ney storms the works at Vienna alone: 18,808 men, 22,386 in the "
    "assault's reckoning, against a garrison of 25,000.\n"
    "Ney assaults the Vienna garrison! Garrison: 25,000 -> 17,165 (-7,835). "
    "Ney loses 5,251 troops. Garrison holds — 17,165 defenders remain.")


class TestF4TheDigestKeepsTheResult:

    def _digest(self, tmp_path):
        return driver.Digest(tmp_path, {"name": "t", "seed": "s", "llm": "mock",
                                        "transport": "test", "policy": {}})

    def test_the_line_after_the_muster_is_the_result(self):
        assert driver.assault_result_line(ASSAULT_REPLY).startswith(
            "Ney assaults the Vienna garrison! Garrison: 25,000 -> 17,165")

    def test_any_other_reply_has_no_result_line(self):
        assert driver.assault_result_line("MUSTER — Ney vs Mack\nmore") == ""
        assert driver.assault_result_line("ASSAULT — alone") == ""

    def test_the_digest_records_it_in_both_files(self, tmp_path):
        digest = self._digest(tmp_path)
        digest.command("Ney, attack Vienna", {"success": True,
                                              "message": ASSAULT_REPLY})
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "  - ↳ Ney assaults the Vienna garrison!" in md, md
        rows = [json.loads(line) for line in
                (tmp_path / "digest.jsonl").read_text(encoding="utf-8").splitlines()]
        command = [r for r in rows if r.get("kind") == "command"][-1]
        assert command["result"].startswith("Ney assaults the Vienna garrison!")

    def test_a_lead_in_is_read_past(self, tmp_path):
        """The exit's own re-read: a desk answer opens with "Were you to give
        the order, Sire:" and the digest recorded only that line."""
        reply = ("Were you to give the order, Sire:\n"
                 "ASSAULT — Ney storms the works at Vienna alone: 18,808 men.\n"
                 "The works would hold: about 7,835 of the garrison fall.\n\n"
                 "Nothing has been ordered, and nothing spent.")
        assert driver.continuation_line(reply) == (
            "ASSAULT — Ney storms the works at Vienna alone: 18,808 men. / "
            "The works would hold: about 7,835 of the garrison fall.")
        assert driver.continuation_line("Sire, the answer.\nmore") == ""
        digest = self._digest(tmp_path)
        digest.command("what are Ney's odds against Vienna",
                       {"success": True, "message": reply})
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "  - ↳ ASSAULT — Ney storms the works" in md, md

    def test_the_lead_in_lever_down_stops_at_the_lead_in(self, monkeypatch):
        monkeypatch.setattr(driver, "THE_DIGEST_READS_PAST_A_LEAD_IN", False)
        assert driver.continuation_line("Were you to give the order, Sire:\nX y") == ""
        assert driver.continuation_line(ASSAULT_REPLY).startswith("Ney assaults")

    def test_the_lever_down_drops_it(self, tmp_path, monkeypatch):
        monkeypatch.setattr(driver, "THE_DIGEST_KEEPS_THE_ASSAULT_RESULT", False)
        digest = self._digest(tmp_path)
        digest.command("Ney, attack Vienna", {"success": True,
                                              "message": ASSAULT_REPLY})
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "↳ Ney assaults" not in md
        rows = [json.loads(line) for line in
                (tmp_path / "digest.jsonl").read_text(encoding="utf-8").splitlines()]
        assert "result" not in [r for r in rows if r.get("kind") == "command"][-1]


# ══════════════════════════════════════════════════════════════════════════
# The exchange is ONE copy
# ══════════════════════════════════════════════════════════════════════════
def _pre_extraction_exchange(ce, a_str, a_eff, g_str, g_eff):
    """The resolver's inline arithmetic before the extraction — the oracle."""
    attacker_damage_ratio = min(0.35, g_eff / max(a_eff, 1) * 0.25)
    garrison_damage_ratio = min(0.50, a_eff / max(g_eff, 1) * 0.35)
    attacker_losses = int(a_str * attacker_damage_ratio)
    garrison_losses = int(g_str * garrison_damage_ratio)
    floor_base = g_str if ce.GARRISON_LOSS_FLOOR_READS_THE_GARRISON else a_str
    attacker_losses = max(attacker_losses,
                          int(floor_base * ce.GARRISON_ASSAULT_LOSS_FLOOR))
    garrison_losses = max(garrison_losses, int(g_str * 0.10), 1)
    return attacker_losses, garrison_losses


class TestTheExchangeIsOneCopy:

    @pytest.mark.parametrize("floor_reads_garrison", [True, False])
    def test_the_method_is_the_pre_extraction_arithmetic(self, floor_reads_garrison,
                                                         monkeypatch):
        monkeypatch.setattr(CombatExecutor, "GARRISON_LOSS_FLOOR_READS_THE_GARRISON",
                            floor_reads_garrison)
        ce = CombatExecutor.__new__(CombatExecutor)
        for a_str in (500, 3000, 18808, 40000):
            for a_eff in (400, 3300, 22386, 61000):
                for g_str in (1, 9, 3000, 12000, 25000):
                    for g_eff in (1, 3450, 15000, 31250):
                        assert ce.garrison_exchange(a_str, a_eff, g_str, g_eff) == \
                            _pre_extraction_exchange(ce, a_str, a_eff, g_str, g_eff)

    def test_the_resolver_reads_the_method(self):
        import inspect
        src = inspect.getsource(CombatExecutor._resolve_garrison_combat)
        assert "self.garrison_exchange(" in src
        assert "attacker_damage_ratio" not in src
        assert "_garrison_report.garrison_breaks(" in src

    @pytest.mark.parametrize("garrison", [0, 1, 4999, 5000, 25000])
    @pytest.mark.parametrize("detachment", [True, False])
    def test_the_predicates_are_the_orders_rules(self, garrison, detachment):
        class Region:
            garrison_strength = garrison
            garrison_detachment = detachment
        fights = garrison > 0 and (detachment or garrison >= 5000)
        assert GR.garrison_fights(Region) is fights
        breaks = garrison <= 0 if detachment else garrison < 5000
        assert GR.garrison_breaks(Region, garrison) is breaks

    def test_the_levers_ship_up(self):
        assert QD.THE_SAFE_ANSWER_READS_THE_HOLDER is True
        assert QD.THE_WHAT_IF_NAMES_ITS_MARSHAL is True
        assert QD.THE_DESK_READS_THE_ODDS is True
        assert QD.THE_WHAT_IF_WEIGHS_A_PROVINCE is True
        assert CG.A_QUANTITY_OR_CONJECTURE_ASKS is True
        assert driver.THE_DIGEST_KEEPS_THE_ASSAULT_RESULT is True
        assert driver.THE_DIGEST_READS_PAST_A_LEAD_IN is True
