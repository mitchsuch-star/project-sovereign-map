"""The review of row BA's session BA-2 (November 15, 2026).

Six readers went over commit 567f3e85, each in a lane: the two tableaux and
their wiring, the script and the fog, the chips played out on later boards and
other seeds, the client, the tests and tools, the records. Nothing crashed,
leaked or touched a save. What they found is pinned here by the behaviour, a
class a row — `docs/BUG_FIXES.md` §BA2, rows BA2-X8 … BA2-X19; the record is
`docs/BATTLE_DIORAMA_SPEC.md` §15.13.

Each case is staged on the 1805 board the session's own tests use
(`tools.ba1_stage_battles._board`) and judged by the game: an order is sent
through the real executor and the world read after it.
"""

import copy
import json
import random
import re
from pathlib import Path

import pytest

from backend.commands import order_quotes
from backend.game_logic import battle_script, siege_diorama
from backend.game_logic.diplomacy import can_enter_territory
from backend.models.intel import FULL
from backend.models.marshal import StrategicOrder
from tests._ledgers import doc_text
from tools import ba1_acts_walk as WALK
from tools import ba1_stage_battles as STAGE
from tools import ba2_switch_off as SWITCH
from tools import keyed_world_probe as PROBE

REPO = Path(__file__).resolve().parents[1]


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════

def _staged(mack_at, lead, lead_at, corps, corps_at):
    """The 1805 board with Mack, a lead and a corps of ours put where the case
    needs them, Mack's province seen whole, no order standing."""
    world, executor = STAGE._board()
    world.marshals["Mack"].location = mack_at
    world.get_region_intel(mack_at).visibility = FULL
    world.marshals[lead].location = lead_at
    world.marshals[corps].location = corps_at
    for marshal in world.marshals.values():
        marshal.strategic_order = None
    return world, executor


def _lit(world, lead, enemy="Mack"):
    """The chips an attack by `lead` offers LIT, by the corps they bring."""
    quote = order_quotes.attack_quote(world, world.marshals[lead], world.marshals[enemy])
    assert quote["ok"], quote.get("refusal")
    return {row["marshal"]: row for row in quote["bring"] if row["ok"]}


def _send(world, executor, row, lead):
    """A chip's order, sent as the client sends it."""
    parsed = {"command": {"raw_input": row["command"], "marshal": row["marshal"],
                          "action": "support", "target": lead},
              "is_strategic": True, "strategic_type": "SUPPORT"}
    random.seed(11)
    with STAGE._quiet():
        return executor.execute(parsed, {"world": world})


def _beats(payload_or_script, kind):
    script = payload_or_script.get("script", payload_or_script)
    return [beat for block in script["acts"] for beat in block["beats"] if beat["kind"] == kind]


# ════════════════════════════════════════════════════════════════════════
# BA2-X8 — a chip never takes the action the attack needs
# ════════════════════════════════════════════════════════════════════════

class TestAChipNeverTakesTheActionTheAttackNeeds:
    """The attack costs an action and so does the order that brings a corps
    to it. With ONE action left the chip was lit all the same: pressed, it
    spent the action, and the attack it was offered for was then refused."""

    @pytest.mark.parametrize("left, offered", [(4, True), (2, True), (1, False)])
    def test_the_chip_is_offered_only_while_the_attack_can_follow(self, left, offered):
        world, _executor = STAGE._board()
        world.actions_remaining = left
        assert ("Soult" in _lit(world, "Ney")) is offered

    def test_what_the_rule_guards_against(self):
        """The chips as they stood (an attack that costs nothing is the rule
        switched off): lit on the last action, and the attack refused after."""
        world, executor = STAGE._board()
        world.actions_remaining = 1
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        rows = {row["marshal"]: row
                for row in order_quotes.bring_quotes(world, ney, mack, attack_ap=0) if row["ok"]}
        assert "Soult" in rows, "a free attack keeps its chips on the last action"
        _send(world, executor, rows["Soult"], "Ney")
        assert world.actions_remaining == 0
        after = order_quotes.attack_quote(world, ney, mack)
        assert not after["ok"] and "action" in after["refusal"]

    def test_the_price_it_reads_is_the_attacks_own(self):
        world, _executor = STAGE._board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        quote = order_quotes.attack_quote(world, ney, mack)
        assert quote["ap"] == int(world.get_action_cost("attack")) == 1
        world.actions_remaining = quote["ap"] + 1
        assert "Soult" in _lit(world, "Ney")


# ════════════════════════════════════════════════════════════════════════
# BA2-X9 — an order that would ask the Emperor first is not offered
# ════════════════════════════════════════════════════════════════════════

class TestAnOrderThatWouldAskIsNotOffered:
    """Bernadotte at Amsterdam, Soult leading from Frankfurt: the direct road
    runs through Hanover's shut frontier, so the order answers "support, or
    cancel?" before it is taken. Its chip was lit, at "about 100%"."""

    def test_a_road_round_a_shut_frontier(self):
        world, executor = _staged("Gelderland", "Soult", "Frankfurt", "Bernadotte", "Amsterdam")
        soult, bernadotte = world.marshals["Soult"], world.marshals["Bernadotte"]
        quote = order_quotes.support_quote(world, bernadotte, soult)
        assert quote["ok"] and "frontier" in quote["detour"], "the order's own quote names the detour"
        assert "Bernadotte" not in _lit(world, "Soult")
        # the oracle: sent, it asks, spends nothing and leaves no order
        before = world.actions_remaining
        result = _send(world, executor, quote, "Soult")
        assert result.get("clarification_kind") == "march_detour_ask"
        assert world.actions_remaining == before and bernadotte.strategic_order is None

    def test_guarded_ground_on_the_road(self, monkeypatch):
        """The other question a march can raise (`march_guard_ask`): the quote
        carries its price in `guard`, and the chip is not offered."""
        world, _executor = STAGE._board()
        assert "Soult" in _lit(world, "Ney")
        real = order_quotes.support_quote

        def guarded(world_, marshal, ally, **kw):
            quote = real(world_, marshal, ally, **kw)
            if marshal.name == "Soult":
                quote["guard"] = "Ansbach is Prussia's guarded ground — the march costs -25 with Prussia"
            return quote

        monkeypatch.setattr(order_quotes, "support_quote", guarded)
        assert "Soult" not in _lit(world, "Ney")


# ════════════════════════════════════════════════════════════════════════
# BA2-X10 — the first march stops at a frontier he may not cross
# ════════════════════════════════════════════════════════════════════════

class TestTheFirstMarchStopsAtAShutFrontier:
    """Soult (a literal man) at Bohemia, Mack on his road at Franconia: his
    road ROUND Mack is plotted through Saxony, whose frontier is shut. The
    order is taken, the march is refused, and he stands where he was. The chip
    read his odds from Dresden — a step he does not take."""

    @staticmethod
    def _case():
        world, executor = _staged("Franconia", "Ney", "Swabia", "Soult", "Bohemia")
        return world, executor, world.marshals["Ney"], world.marshals["Soult"]

    def test_the_chip_reads_the_ground_he_really_stands_on(self):
        world, executor, ney, soult = self._case()
        quote = order_quotes.support_quote(world, soult, ney)
        assert quote["road"][0] == "Dresden", "the road round Mack, as the order plots it"
        assert order_quotes._stop_this_turn(world, soult, quote) == "Bohemia"
        row = _lit(world, "Ney")["Soult"]
        _send(world, executor, row, "Ney")
        assert soult.location == "Bohemia" and soult.strategic_order.command_type == "SUPPORT"
        # the oracle: his odds once the order is his are the odds the chip named
        real = executor._combat._arrival_odds_row(ney, soult, "Franconia", world, "has_support_order")
        assert row["odds_with"] == int(real["arrival_odds"])
        assert f"about {row['odds_with']}% under a written order" in row["why"]

    def test_an_open_road_is_still_walked(self):
        """The opening board: Soult's order to Ney marches him at once, and
        the stop is where that march leaves him."""
        world, executor = STAGE._board()
        ney, soult = world.marshals["Ney"], world.marshals["Soult"]
        quote = order_quotes.support_quote(world, soult, ney)
        stop = order_quotes._stop_this_turn(world, soult, quote)
        _send(world, executor, quote, "Ney")
        assert soult.location == stop

    @pytest.mark.xfail(strict=True, reason="BA2-X10 OPEN — owner row BA's session BA-3")
    def test_a_road_round_never_runs_through_a_frontier_he_may_not_cross(self):
        world, _executor, ney, soult = self._case()
        quote = order_quotes.support_quote(world, soult, ney)
        first = world.get_region(quote["road"][0])
        assert can_enter_territory(world, soult.nation, first.controller,
                                   mover_location=soult.location)


# ════════════════════════════════════════════════════════════════════════
# BA2-X11, BA2-X12 — the cannonade's two sides
# ════════════════════════════════════════════════════════════════════════

def _cannonade(world, collateral, battery_lost=40, battery_left=2960):
    br = {"attacker": {"name": "Marmont", "casualties": battery_lost, "remaining": battery_left},
          "defender": {"name": "Mack", "casualties": 3000, "remaining": 49000, "morale": 70},
          "fort_degraded": False, "fort_old": 0, "fort_new": 0, "berthier_observation": "",
          "collateral": collateral}
    event = {"type": "bombardment", "attacker_location": "Rhineland", "defender_location": "Swabia"}
    return siege_diorama.build_bombardment_diorama(
        world, world.marshals["Marmont"], world.marshals["Mack"],
        {"success": True, "bombardment_result": br, "events": [event]})


class TestTheReserveIsCountedWithItsOwnSide:
    """BA2-X11 (BA2-X3's sibling): a corps of the guns' own side that stood
    under the fire and found no seat was counted — its men and its dead — in
    the TARGET side's reserve line."""

    @staticmethod
    def _board():
        world, _executor = STAGE._board()
        STAGE._marmont(world)
        STAGE._place(world, Lannes="Swabia", Davout="Swabia", Ney="Swabia", Murat="Swabia",
                     ArchdukeCharles="Swabia")
        return world

    @staticmethod
    def _ours(*rows):
        return [{"name": name, "nation": "France", "casualties": lost, "friendly_fire": True}
                for name, lost in rows]

    def test_two_unseated_corps_of_ours_are_our_reserve(self):
        payload = _cannonade(self._board(), self._ours(
            ("Lannes", 600), ("Davout", 500), ("Ney", 400), ("Murat", 300)))
        ours, theirs = payload["attacker"], payload["defender"]
        assert [c["name"] for c in theirs["contingents"]] == ["Mack", "Lannes", "Davout"]
        assert (ours["reserve_count"], ours["reserve_casualties"]) == (2, 700)
        assert (theirs["reserve_count"], theirs["reserve_casualties"]) == (0, 0)
        assert ours["casualties_total"] == 40 + 600 + 500 + 400 + 300
        assert theirs["casualties_total"] == 3000

    def test_an_unseated_corps_of_the_targets_side_stays_his(self):
        rows = self._ours(("Lannes", 600), ("Davout", 500), ("Ney", 400)) + [
            {"name": "ArchdukeCharles", "nation": "Austria", "casualties": 250, "friendly_fire": False}]
        payload = _cannonade(self._board(), rows)
        ours, theirs = payload["attacker"], payload["defender"]
        assert (ours["reserve_count"], ours["reserve_casualties"]) == (1, 400)
        assert (theirs["reserve_count"], theirs["reserve_casualties"]) == (1, 250)
        assert theirs["casualties_total"] == 3000 + 250

    def test_no_number_of_either_side_is_a_float_or_below_nothing(self):
        payload = _cannonade(self._board(), self._ours(
            ("Lannes", 600), ("Davout", 500), ("Ney", 400), ("Murat", 300)))
        for side in ("attacker", "defender"):
            for key in ("reserve_count", "reserve_casualties", "casualties_total", "committed_total"):
                value = payload[side][key]
                assert type(value) is int and value >= 0, (side, key, value)


class TestABatteryUnderItsOwnShells:
    """BA2-X12: a battery standing in its target's own province is caught by
    its own collateral roll (the post-objection and defiance roads allow the
    distance). The table seated the same marshal twice, once on each side."""

    @staticmethod
    def _board():
        world, executor = STAGE._board()
        STAGE._marmont(world)
        STAGE._place(world, Marmont="Swabia")
        return world, executor

    def test_he_is_seated_once_and_his_dead_are_his_own(self):
        world, _executor = self._board()
        start = int(world.marshals["Marmont"].strength)
        world.marshals["Marmont"].strength = start - 53 - 636
        payload = _cannonade(world, [{"name": "Marmont", "nation": "France", "casualties": 636,
                                      "friendly_fire": True}],
                             battery_lost=53, battery_left=start - 53 - 636)
        names = [c["name"] for side in ("attacker", "defender") for c in payload[side]["contingents"]]
        assert names == ["Marmont", "Mack"]
        gunners = payload["attacker"]["contingents"][0]
        assert (gunners["committed"], gunners["casualties"], gunners["remaining"]) == (
            start, 53 + 636, start - 53 - 636)
        assert payload["attacker"]["casualties_total"] == 53 + 636
        assert payload["attacker"]["committed_total"] == start
        assert not _beats(payload, "bystander")

    @pytest.mark.xfail(strict=True, reason="BA2-X12 OPEN — owner row BA's session BA-3")
    def test_a_battery_is_never_caught_by_its_own_fire(self):
        world, executor = self._board()
        for seed in range(6):
            board = copy.deepcopy(world)
            random.seed(seed)
            with STAGE._quiet():
                result = executor._combat._execute_bombardment(
                    board.marshals["Marmont"], board.marshals["Mack"], board,
                    {"world": board, "executor": executor})
            hit = [row["name"] for row in result["bombardment_result"]["collateral"]]
            assert "Marmont" not in hit, f"seed {seed}: the battery shelled itself"


# ════════════════════════════════════════════════════════════════════════
# BA2-X13, BA2-X14 — the words
# ════════════════════════════════════════════════════════════════════════

class TestThePlanNamesEachOrderInItsOwnWord:
    """BA2-X13: the resolver counts a PURSUE whose quarry stands on the field
    as a written order, and the plan called it "ordered in support"."""

    def test_a_pursuit_is_not_called_support(self):
        world, executor = STAGE._board()
        random.seed(0)
        world.marshals["Murat"].strategic_order = StrategicOrder(
            command_type="PURSUE", target="Mack", target_type="marshal",
            started_turn=int(world.current_turn), original_command="Murat, pursue Mack",
            issued_turn=int(world.current_turn))
        STAGE._support(world, "Lannes", "Ney")
        with STAGE._quiet():
            result = executor._execute_attack(
                world.marshals["Ney"], "Mack", world, {"world": world, "executor": executor})
        (plan,) = _beats(result["battle_diorama"], "plan")
        assert plan["text"].startswith(
            "The plan: Ney leads; Lannes ordered in support; Murat ordered in pursuit")
        assert plan["supports"] == ["Lannes", "Murat"], "both are touched on the board"

    def test_the_row_names_its_order(self):
        """The reinforcement row itself, read where the resolver writes it."""
        world, executor = STAGE._board()
        random.seed(0)
        world.marshals["Murat"].strategic_order = StrategicOrder(
            command_type="PURSUE", target="Mack", target_type="marshal",
            started_turn=int(world.current_turn), original_command="Murat, pursue Mack",
            issued_turn=int(world.current_turn))
        STAGE._support(world, "Lannes", "Ney")
        with STAGE._quiet():
            rows = executor._combat._calculate_reinforcements(
                world.marshals["Ney"], world.marshals["Mack"], "Swabia", "France", world)
        by_name = {row["marshal"]: row for row in rows}
        assert by_name["Lannes"]["order_type"] == "SUPPORT"
        assert by_name["Murat"]["order_type"] == "PURSUE"
        named = [row for row in rows if "order_type" in row]
        assert all(row["order_type"] == "" for row in named if not row.get("has_explicit_order"))


class TestTheCountsAgreeWithTheirNouns:
    """BA2-X14: "1 defenders remain", "1 men", "0 men the fewer"."""

    @staticmethod
    def _held():
        world, executor = STAGE._board()
        random.seed(7)
        who, target = STAGE._stage_assault_held(world, executor)
        with STAGE._quiet():
            result = executor._execute_attack(
                world.marshals[who], target, world, {"world": world, "executor": executor})
        payload = result["battle_diorama"]
        assert payload["kind"] == "assault" and payload["fate"] == "held"
        return world, world.marshals[who], payload

    def _told(self, remaining, lost):
        world, marshal, payload = self._held()
        payload = copy.deepcopy(payload)
        payload["defender"]["contingents"][0]["remaining"] = remaining
        payload["attacker"]["contingents"][0]["casualties"] = lost
        script = battle_script.build_assault_script(world, payload, marshal, {})
        return _beats(script, "wall_holds")[0]["text"], _beats(script, "repulsed")[0]["text"]

    def test_many(self):
        holds, repulsed = self._told(17165, 5251)
        assert holds.endswith("hold: 17,165 defenders remain.")
        assert repulsed.endswith("draws off from the walls, 5,251 men the fewer.")

    def test_one(self):
        holds, repulsed = self._told(1, 1)
        assert holds.endswith("hold: 1 defender remains.")
        assert repulsed.endswith("draws off from the walls, 1 man the fewer.")

    def test_none_lost_is_not_counted(self):
        _holds, repulsed = self._told(4000, 0)
        assert repulsed.endswith("draws off from the walls.")

    def test_the_guns(self):
        assert battle_script._fall(1) == "1 falls" and battle_script._fall(3000) == "3,000 fall"
        assert battle_script._men(1) == "1 man" and battle_script._men(25000) == "25,000 men"

    @pytest.mark.xfail(strict=True, reason="BA2-X14 OPEN (the half left) — owner row BA's session BA-3")
    def test_a_gunner_under_orders_is_named_once(self):
        """Marmont ordered in support, and his guns firing in support, are
        told as two clauses of one plan ("Marmont ordered in support;
        Marmont's guns in support"). Left for BA-3's walk of record: the fix
        changes the staged scene `the_guns`, whose frames are on record."""
        world, executor = STAGE._board()
        random.seed(3)
        who, target = STAGE._stage_guns(world, executor)
        with STAGE._quiet():
            result = executor._execute_attack(
                world.marshals[who], target, world, {"world": world, "executor": executor})
        (plan,) = _beats(result["battle_diorama"], "plan")
        assert plan["text"].count("Marmont") == 1, plan["text"]


# ════════════════════════════════════════════════════════════════════════
# BA2-X15, BA2-X16, BA2-X17, BA2-X18 — the tools and the records
# ════════════════════════════════════════════════════════════════════════

ACTS = "godot-client/project-sovereign/scripts/battle_acts.gd"


class TestTheSwitchOffToolPutsTheFileBack:
    """BA2-X15: the tool changes battle_acts.gd in the working tree while its
    walk runs. It had no lock, no kept copy and no time limit, and it put the
    file back as decoded text."""

    CLEAN = b"extends Node\r\nconst X := true\r\nfunc f():\r\n\tpass\r\n"
    CASE = [("demo", "a demo mutation", [("const X := true\n", "const X := false\n")],
             "scene", 1.0, "caught!")]

    def _tree(self, tmp_path):
        acts = tmp_path / ACTS
        acts.parent.mkdir(parents=True)
        (tmp_path / "tools").mkdir()
        acts.write_bytes(self.CLEAN)
        return acts

    @staticmethod
    def _marks(tmp_path):
        return [p.name for p in (tmp_path / "tools").iterdir()]

    def test_the_file_is_put_back_byte_for_byte_in_its_own_line_endings(self, tmp_path):
        acts = self._tree(tmp_path)
        seen = {}

        def walk(root, scenes, speed):
            seen["during"] = acts.read_bytes()
            seen["marks"] = sorted(self._marks(tmp_path))
            return "caught! 1 claim(s) failed"

        results = SWITCH.switch_off(tmp_path, cases=self.CASE, walk=walk, say=lambda line: None)
        assert results == [("a demo mutation", True)]
        assert seen["during"] == self.CLEAN.replace(b"true", b"false"), "the mutant keeps CRLF"
        assert seen["marks"] == [".ba2_switch_off.kept", ".ba2_switch_off.lock"]
        assert acts.read_bytes() == self.CLEAN and self._marks(tmp_path) == []

    def test_a_walk_that_raises_still_puts_it_back(self, tmp_path):
        acts = self._tree(tmp_path)

        def walk(root, scenes, speed):
            raise RuntimeError("the engine died")

        with pytest.raises(RuntimeError):
            SWITCH.switch_off(tmp_path, cases=self.CASE, walk=walk, say=lambda line: None)
        assert acts.read_bytes() == self.CLEAN and self._marks(tmp_path) == []

    def test_a_second_copy_is_refused_and_touches_nothing(self, tmp_path):
        acts = self._tree(tmp_path)
        (tmp_path / "tools" / ".ba2_switch_off.lock").write_text("123", encoding="utf-8")
        with pytest.raises(SystemExit) as refused:
            SWITCH.switch_off(tmp_path, cases=self.CASE, walk=lambda *a: "caught!", say=lambda line: None)
        assert "refused" in str(refused.value) and acts.read_bytes() == self.CLEAN

    def test_a_stale_anchor_is_refused_before_anything_is_written(self, tmp_path):
        acts = self._tree(tmp_path)
        stale = [("demo", "a stale case", [("const Y := true\n", "const Y := false\n")],
                  "scene", 1.0, "caught!")]
        with pytest.raises(SystemExit) as refused:
            SWITCH.switch_off(tmp_path, cases=stale, walk=lambda *a: "caught!", say=lambda line: None)
        assert "matches 0 times" in str(refused.value)
        assert acts.read_bytes() == self.CLEAN and self._marks(tmp_path) == []

    def test_every_shipped_case_still_finds_its_anchor(self):
        clean = (REPO / ACTS).read_bytes()
        assert len(SWITCH.CASES) == 10
        for _key, _name, swaps, *_rest in SWITCH.CASES:
            assert SWITCH.mutated(clean, swaps) != clean


class TestALiveWalkThatFailsKeepsTheRecord:
    """BA2-X16: the live-client walk copied its run over the committed record
    BEFORE it judged the run."""

    def test_this_sessions_walk_judges_first(self):
        runner = (REPO / "tools" / "ba2_mode_c_walk.py").read_text(encoding="utf-8")
        verdict = runner.index("passed = bool(")
        guard = runner.index("if args.export and not passed:")
        wipe = runner.index('shutil.rmtree(dest / "frames")')
        assert verdict < guard < wipe
        assert "return 0 if passed else 1" in runner

    @pytest.mark.xfail(strict=True, reason="BA2-X16 OPEN — owner Session H (S15, the deploy)")
    def test_the_four_older_walks_judge_first_too(self):
        for name in ("au3a", "re5", "ui5", "ui6"):
            runner = (REPO / "tools" / f"{name}_mode_c_walk.py").read_text(encoding="utf-8")
            assert "if args.export and not passed:" in runner, name

    @pytest.mark.xfail(strict=True, reason="BA2-X16 OPEN — owner Session H (S15, the deploy)")
    def test_the_mutation_sweep_refuses_a_second_copy(self):
        """BA2-X15's sibling: the other tool that mutates a source in place
        restores it byte for byte and takes no lock against a second copy."""
        sweep = (REPO / "tools" / "mutation_sweep.py").read_text(encoding="utf-8")
        assert re.search(r"""open\([^)]*["']x["']""", sweep), "an exclusive lock file"


class TestTheWalksRecordAndItsSources:
    """BA2-X17: the walk's record carries a hash of each source it was shot
    from, and no test compared them; four sources that shape what the walk
    shows are not on the list."""

    @staticmethod
    def _record():
        return json.loads((WALK.OUT / "walk_record.json").read_text(encoding="utf-8"))

    def test_the_payloads_the_walk_played_are_the_committed_ones(self):
        """What the walk SHOWED is fixed by the payloads it played: every one
        on record is the file in the repository, byte for byte."""
        record = self._record()
        assert len(record["payloads"]) >= 23
        for name, sha in record["payloads"].items():
            assert WALK._sha(WALK.OUT / "payloads" / name) == sha, name

    def test_the_client_it_was_shot_from_is_the_client_committed(self):
        record = self._record()
        for name in ("godot-client/project-sovereign/scripts/battle_acts.gd",
                     "godot-client/project-sovereign/scripts/diorama_plinth.gd",
                     "godot-client/project-sovereign/scripts/battle_diorama.gd",
                     "tools/ba1_acts_walk.gd"):
            assert WALK._sha(REPO / name) == record["sources"][name], name

    @pytest.mark.xfail(strict=True, reason="BA2-X17 OPEN — owner row BA's session BA-3")
    def test_every_source_on_record_is_the_source_committed(self):
        """Red since the review's own fixes to `battle_script.py` and
        `siege_diorama.py` (words and counts on roads no staged scene takes:
        the payloads above are unchanged). The next walk of record re-shoots
        it, and this comparison then joins the green pins."""
        record = self._record()
        for name, sha in record["sources"].items():
            assert WALK._sha(REPO / name) == sha, name

    @pytest.mark.xfail(strict=True, reason="BA2-X17 OPEN — owner row BA's session BA-3")
    def test_the_list_names_every_source_that_shapes_the_walk(self):
        for name in ("backend/game_logic/battle_diorama.py", "tools/ba1_stage_battles.py",
                     "tools/ba1_acts_walk.py", "godot-client/project-sovereign/scripts/utils.gd"):
            assert name in WALK.SOURCES, name


class TestTheKeyedWorldProbe:
    """BA2-X18: the probe behind "BA-2 moves no number" lived in a scratch
    folder; `tools/keyed_world_probe.py` keeps it."""

    def test_the_first_turn_and_the_keys_that_differ(self):
        a = [{"gold": "1", "marshals": "2"}, {"gold": "3", "marshals": "4"}]
        b = [{"gold": "1", "marshals": "2"}, {"gold": "3", "marshals": "5"}]
        assert PROBE.first_difference(a, a) is None
        assert PROBE.first_difference(a, b) == (2, ["marshals"])
        assert PROBE.first_difference(a, a[:1]) == (2, ["(one campaign is longer)"])

    def test_a_fresh_notification_id_is_no_difference(self):
        one = PROBE.key_hashes({"notifications": [
            {"id": "0f8fad5b-d9cb-469f-a165-70867728950e", "text": "x"}], "gold": 7})
        two = PROBE.key_hashes({"notifications": [
            {"id": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "text": "x"}], "gold": 7})
        other = PROBE.key_hashes({"notifications": [
            {"id": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "text": "y"}], "gold": 7})
        assert one == two and one["notifications"] != other["notifications"]

    def test_it_refuses_an_unpinned_hash_seed(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PYTHONHASHSEED", "random")
        with pytest.raises(SystemExit):
            PROBE.run(str(REPO), "jena", 1, str(tmp_path / "out.json"))


class TestTheRecordsSayWhatIsNext:
    """BA2-X19: `STATUS.md` ▶ NEXT UP is read first, every session, and its
    head paragraph still ended on BA-2 as the session to come."""

    def test_the_head_of_status_names_no_landed_session_as_next(self):
        # the live file comes first in `doc_text`, so the first head is today's
        head = next(line for line in doc_text("STATUS.md").splitlines()
                    if line.startswith("> **▶ NEXT ="))
        assert "next BA-2 the walls" not in head and "BA-3 the crisis" not in head
        assert "ROW BA, BA-2 ✅ LANDED November 15, 2026" in head

    def test_the_ledger_holds_the_reviews_rows(self):
        ledger = doc_text("BUG_FIXES.md")
        rows = re.findall(r"^\| \*\*(BA2-X\d+)\*\* \| P\d \| (✅ FIXED|OPEN) ", ledger, flags=re.M)
        assert [name for name, _state in rows] == [f"BA2-X{n}" for n in range(1, 20)]
