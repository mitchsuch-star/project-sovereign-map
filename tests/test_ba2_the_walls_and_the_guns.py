"""Row BA, BA-2 — the walls, the guns and the order of battle: the session's gate.

Owner: `docs/BATTLE_DIORAMA_SPEC.md` §15.5.4 (a garrison assault and a
standalone bombardment each get a tableau), §15.5.5 (the plan of battle, named
in Act I and orderable at the attack row), §15.11 (the session's rulings: the
order of battle, three seats and a reserve, Napoleonic movement) and §15.12
(the landing record). The builders' own pins — every beat's fog case, the
payloads' shape, `bring_quotes` on the muster ladder — are
`tests/test_ba2_backend_walls_guns_plan.py`.

Five kinds of pin here:

1. The SERVED roads: `/command` (storm a wall, fire a battery), the enemy
   phase's chokepoint, and the save — both transports, no float, no tableau
   in the event log.
2. The plan, orderable: `/march_quotes` carries the chip, the chip sends the
   order the game already has at that order's own price, the muster then
   reads the corps as ordered and Act I names him.
3. DRIVEN (the real `battle_diorama.tscn`, headless, eight times faster): an
   assault, a cannonade, three corps a side and a square fought fresh on the
   1805 board and played by the client; the claims are
   `tools/ba1_acts_walk.check`'s, read off the engine's own record.
4. The walk of record and the instruments.
5. Source pins on the seams.
"""
from __future__ import annotations

import ast
import json
import random
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import ba1_acts_walk as WALK  # noqa: E402
import ba1_stage_battles as STAGE  # noqa: E402

SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
AUDIT = REPO / "docs" / "audits" / "ba1_client"
DRIVEN_SCENES = ("assault_stormed", "assault_on_ours", "bombard_levels", "the_reserve",
                 "square_and_horse")
BA2_SCENES = ("the_reserve", "two_a_side", "our_dispositions", "square_and_horse",
              "assault_held", "assault_stormed", "assault_occupied", "assault_capitulated",
              "assault_on_ours", "bombard_link", "bombard_levels", "bombard_ours")


def _gd(name: str) -> str:
    return (SCRIPTS / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _func(source: str, name: str) -> str:
    match = re.search(rf"^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^class |\Z)",
                      source, re.S | re.M)
    assert match, name
    return match.group(0)


def _floats(node, path="$"):
    if isinstance(node, float):
        yield path
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _floats(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _floats(value, f"{path}[{i}]")


def _beats(payload, kind=None):
    return [b for block in (payload.get("script") or {}).get("acts") or []
            for b in block["beats"] if kind is None or b["kind"] == kind]


def _acts(payload):
    return [block["act"] for block in payload["script"]["acts"]]


def _marmont(world):
    """Marmont, the gunner, commissioned and placed in the Rhineland."""
    from backend.game_logic.recruitment import commission_marshal, find_candidate
    world.nation_gold["France"] = int(world.nation_gold.get("France", 0)) + 5000
    with STAGE._quiet():
        commission_marshal(world, "France", find_candidate(world, "France", "Marmont"))
    STAGE._place(world, Marmont="Rhineland")


@pytest.fixture()
def served():
    """The real app over a 1805 board of the test's own (`M._set_active_world`)."""
    import backend.main as M
    from fastapi.testclient import TestClient
    before = M.world
    try:
        with TestClient(M.app) as tc:
            def seat(prepare=None):
                world, executor = STAGE._board()
                if prepare is not None:
                    prepare(world)
                with STAGE._quiet():
                    world.calculate_visibility()
                M._set_active_world(world)
                return world, executor

            def post(command):
                with STAGE._quiet():
                    return tc.post("/command", json={"command": command}).json()

            def quotes(region):
                with STAGE._quiet():
                    return tc.get("/march_quotes", params={"region": region}).json()

            yield {"M": M, "seat": seat, "post": post, "quotes": quotes}
    finally:
        M._set_active_world(before)


# ════════════════════════════════════════════════════════════════════════
# 1. The served roads
# ════════════════════════════════════════════════════════════════════════

class TestTheServedRoads:
    def test_a_stormed_wall_rides_both_transports_of_the_command_road(self, served):
        def board(world):
            world.get_region("Vienna").garrison_strength = 6000
            STAGE._place(world, Ney="Bohemia")
        served["seat"](board)
        random.seed(7)
        body = served["post"]("Ney, attack Vienna")
        assert body["success"], body.get("message")
        payload = body["battle_diorama"]
        assert payload["kind"] == "assault" and payload["fate"] == "stormed"
        assert payload["player_side"] == "attacker" and payload["banner"] == "THE WALLS ARE CARRIED"
        assert body["events"][0]["type"] == "garrison_destroyed"
        assert body["events"][0]["diorama"] == payload, "the two transports carry one tableau"
        assert list(_floats(payload)) == []
        # the storm, the wall, the province: no cannonade and no dice at a wall
        assert _acts(payload) == ["approach", "assault", "crisis", "pursuit"]
        assert not _beats(payload, "dice") and _beats(payload, "wall_falls")
        keeper = payload["defender"]["contingents"][0]
        assert keeper["garrison"] is True and keeper["name"] == "Vienna garrison"
        assert keeper["committed"] == 6000 and keeper["remaining"] == 0

    def test_a_cannonade_is_a_link_and_tells_the_cannonade_alone(self, served):
        world, _ex = served["seat"](_marmont)
        random.seed(1)
        body = served["post"]("Marmont, bombard Mack")
        assert body["success"], body.get("message")
        payload = body["battle_diorama"]
        assert payload["kind"] == "bombardment" and payload["player_side"] == "attacker"
        assert payload["significant"] is False and payload["dramatic"] is False, \
            "a salvo that neither destroys nor levels is a link, never an interruption"
        assert body["events"][0]["type"] == "bombardment"
        assert body["events"][0]["diorama"] == payload
        assert list(_floats(payload)) == []
        assert _acts(payload) == ["cannonade"]
        (battery,) = _beats(payload, "battery")
        mack = body["bombardment_result"]["defender"]
        assert battery["dealt"] == mack["casualties"] and battery["target"] == "Mack"
        # the tableau is written on a COPY of the event: the campaign log and
        # the save carry the bombardment, never its picture
        assert not any(isinstance(e, dict) and "diorama" in e for e in world.event_log)
        assert "diorama" not in json.dumps(world.to_dict(), default=str)

    def test_it_opens_by_itself_only_when_it_levels_or_destroys(self):
        seeds = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
        levelled, reason, _result = STAGE.fight(
            "bombard_levels", int(seeds["bombard_levels"]["ambient_seed"]))
        assert levelled is not None and reason
        assert levelled["significant"] is True and levelled["dramatic"] is True
        assert levelled["banner"] == "THE WORKS ARE LEVELLED"
        (works,) = _beats(levelled, "works")
        assert works["old"] > 0 and works["new"] == 0 == levelled["works_new"]
        link, reason, _result = STAGE.fight(
            "bombard_link", int(seeds["bombard_link"]["ambient_seed"]))
        assert link is not None and reason and link["significant"] is False
        assert link["banner"] == "THE GUNS SPEAK"

    def test_an_enemy_assault_reaches_the_enemy_phase_with_its_tableau(self, served):
        """The enemy's turn carries each AI action's executor result; the
        phase's chokepoint (`_build_visible_enemy_phase`) keeps the tableau on
        the action (what `main.gd` stashes) and on its first event (what the
        dialog's link reads) — and strips the world."""
        M = served["M"]
        for garrison, fate, dramatic, banner in ((25000, "held", False, "THE WALLS HOLD"),
                                                 (6000, "stormed", True, "THE WALLS ARE LOST")):
            def board(world, garrison=garrison):
                world.get_region("Paris").garrison_strength = garrison
                STAGE._place(world, Mack="Artois")
                for marshal in world.marshals.values():
                    if marshal.nation == "France" and marshal.location == "Paris":
                        marshal.location = "Lorraine"
            world, executor = served["seat"](board)
            random.seed(7)
            with STAGE._quiet():
                result = executor._execute_attack(
                    world.marshals["Mack"], "Paris", world, {"world": world, "executor": executor})
                seen = M._build_visible_enemy_phase(
                    {"nations": {"Austria": {"actions": [result], "action_count": 1}},
                     "total_actions": 1}, world)
            (action,) = seen["nations"]["Austria"]["actions"]
            assert "new_state" not in action
            payload = action["battle_diorama"]
            assert payload["kind"] == "assault" and payload["fate"] == fate, (garrison, payload["fate"])
            assert payload["player_side"] == "defender" and payload["banner"] == banner
            assert payload["dramatic"] is dramatic, "only a wall of ours that FELL seizes the screen"
            assert action["events"][0]["diorama"] == payload
            assert list(_floats(payload)) == []
            (walls,) = _beats(payload, "walls")
            assert walls["weight"] == "head", "our own garrison's stand is told first"


class TestTheGunsOwnSide:
    """Two finds of the frames (November 14-15, 2026)."""

    def _salvo(self, friendly):
        from backend.game_logic.siege_diorama import build_bombardment_diorama
        from backend.models.marshal import Marshal
        from backend.models.world_state import WorldState

        def corps(name, where, men, nation, **kw):
            return Marshal(name=name, location=where, strength=men, personality="cautious",
                           nation=nation, movement_range=1, tactical_skill=7,
                           spawn_location=where, **kw)
        battery = corps("Marmont", "Belgium", 2950, "France", artillery=True)
        target = corps("Mack", "Waterloo", 48000, "Austria")
        by = corps("Lannes", "Waterloo", 17400, "France" if friendly else "Russia")
        world = WorldState()
        world.marshals = {m.name: m for m in (battery, target, by)}
        for a, b in (("Austria", "France"), ("Austria", "Russia")):
            world.diplomatic_states[world._make_diplo_key(a, b)] = "WAR"
        br = {"attacker": {"name": "Marmont", "casualties": 50, "remaining": 2950, "morale": 90},
              "defender": {"name": "Mack", "casualties": 2000, "remaining": 48000, "morale": 97},
              "collateral": [{"name": "Lannes", "nation": by.nation, "casualties": 600,
                              "friendly_fire": friendly}],
              "fort_degraded": False, "fort_old": 0, "fort_new": 0,
              "berthier_observation": "The guns speak."}
        result = {"success": True, "bombardment_result": br,
                  "events": [{"type": "bombardment", "defender_location": "Waterloo",
                              "attacker_location": "Belgium"}]}
        return build_bombardment_diorama(world, battery, target, result)

    def test_our_own_corps_under_our_guns_is_counted_with_us(self):
        """Lannes stood beside Mack and is SEATED there; his 600 dead were
        counted in 'AUSTRIA LOSSES' and his men in Austria's bar."""
        payload = self._salvo(friendly=True)
        seated = [c["name"] for c in payload["defender"]["contingents"]]
        assert seated == ["Mack", "Lannes"], "he is seated where he stood"
        lannes = payload["defender"]["contingents"][1]
        assert lannes["bystander"] and lannes["friendly_fire"] and lannes["of_the_guns"]
        assert payload["attacker"]["casualties_total"] == 50 + 600
        assert payload["attacker"]["committed_total"] == 3000 + 18000
        assert payload["defender"]["casualties_total"] == 2000
        assert payload["defender"]["committed_total"] == 50000

    def test_an_ally_of_the_guns_is_counted_with_the_guns_too(self):
        """A corps of another crown at war with the target and not with the
        battery fights on the battery's side."""
        payload = self._salvo(friendly=False)
        lannes = payload["defender"]["contingents"][1]
        assert not lannes["friendly_fire"] and lannes["of_the_guns"]
        assert payload["attacker"]["casualties_total"] == 650
        assert payload["defender"]["casualties_total"] == 2000

    def test_ba2_x1_berthier_reports_the_emperors_batteries_only(self):
        """Every bombardment observation is written from behind OUR guns
        ("our fire", "the enemy position"). Of an enemy battery shelling Ney
        the enemy phase printed 'Ney's numbers absorb our fire'."""
        from backend.game_logic.battle_report import generate_bombardment_report
        data = {"attacker_name": "Hiller", "defender_name": "Ney", "attacker_casualties": 40,
                "defender_casualties": 900, "defender_remaining": 23100,
                "defender_original": 24000, "terrain": "plains", "terrain_modifier": 1.0,
                "fort_degraded": False, "fort_old": 0, "fort_new": 0, "collateral": []}
        random.seed(5)
        ours = generate_bombardment_report(dict(data, attacker_nation="France"), "France")
        after_ours = random.random()
        random.seed(5)
        theirs = generate_bombardment_report(dict(data, attacker_nation="Austria"), "France")
        after_theirs = random.random()
        assert len(ours) > 10 and theirs == ""
        assert after_ours == after_theirs, "the line is still picked: the draw it took is unchanged"
        # a caller that names no nation is answered as it always was
        random.seed(5)
        assert generate_bombardment_report(dict(data), "France") == ours

    def test_a_watcher_is_told_what_the_script_tells_him(self):
        """Another crown's cannonade, watched: who fired on whom and who was
        destroyed. The works, the province fired from and Berthier's line are
        a party's — on the payload as in the script."""
        from backend.game_logic.siege_diorama import build_bombardment_diorama
        from backend.models.marshal import Marshal
        from backend.models.world_state import WorldState

        def corps(name, where, men, nation, **kw):
            return Marshal(name=name, location=where, strength=men, personality="cautious",
                           nation=nation, movement_range=1, tactical_skill=7,
                           spawn_location=where, **kw)
        battery = corps("Hiller", "Belgium", 2950, "Austria", artillery=True)
        target = corps("Blucher", "Waterloo", 30000, "Prussia")
        world = WorldState()
        world.marshals = {m.name: m for m in (battery, target, corps("Ney", "Paris", 9000, "France"))}
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "WAR"
        world.update_intel_from_battle("Waterloo", int(world.current_turn))   # the field in sight
        br = {"attacker": {"name": "Hiller", "casualties": 50, "remaining": 2950, "morale": 90},
              "defender": {"name": "Blucher", "casualties": 2000, "remaining": 30000, "morale": 97},
              "collateral": [], "fort_degraded": True, "fort_old": 12, "fort_new": 0,
              "berthier_observation": "Cracks spread through the enemy works."}
        result = {"success": True, "bombardment_result": br,
                  "events": [{"type": "bombardment", "defender_location": "Waterloo",
                              "attacker_location": "Belgium"}]}
        payload = build_bombardment_diorama(world, battery, target, result)
        assert payload is not None and payload["player_side"] is None
        assert payload["works_old"] == 0 == payload["works_new"] and payload["battery_at"] == ""
        assert payload["observation"] == "" and payload["banner"] == "THE GUNS SPEAK"
        assert payload["significant"] is False, "levelled works he is not told of open nothing"
        assert [b["kind"] for b in _beats(payload)] == ["battery"]
        assert "taken" not in _beats(payload)[0] and "Belgium" not in _beats(payload)[0]["text"]


# ════════════════════════════════════════════════════════════════════════
# 2. The plan, orderable at the attack row
# ════════════════════════════════════════════════════════════════════════

class TestThePlanIsOrderable:
    @staticmethod
    def _ney(quotes):
        return next(q for row in quotes["attack"] for q in row["quotes"]
                    if q["marshal"] == "Ney" and q["kind"] == "attack")

    def test_the_chip_is_the_existing_order_at_its_own_price(self, served):
        world, _ex = served["seat"]()
        lead = self._ney(served["quotes"]("Swabia"))
        rows = {b["marshal"]: b for b in lead["bring"]}
        # Bernadotte and Murat stand beside the field too, and the muster's own
        # hint names the order for each — but it marches Bernadotte at once to
        # Munich, from whose mountains he cannot come, and it stops Murat on his
        # question (Mack stands on his road): no chip for either (BA2-X7 owns
        # the hint; tests/test_ba2_backend_walls_guns_plan.py sends each order
        # and reads the game after it)
        assert set(rows) == {"Soult"}
        for name, row in rows.items():
            assert row["kind"] == "support" and row["ok"] is True
            assert row["command"] == f"{name}, support Ney"
            assert row["ap"] == int(world.marshals[name].strategic_order_ap(order_type="SUPPORT")) == 1
        # a man who will not march unordered: the muster's own reason, and his
        # odds once the order is written
        assert rows["Soult"]["code"] == "literal_awaits_orders" and rows["Soult"]["odds_now"] == -1
        assert rows["Soult"]["odds_with"] > 50
        assert rows["Soult"]["why"].endswith(f"about {rows['Soult']['odds_with']}% under a written order")
        # a man who may not arrive: the muster's own odds, before and under an
        # order — Murat, brought to Lannes, who stands beside him
        lannes = next(q for row in served["quotes"]("Swabia")["attack"] for q in row["quotes"]
                      if q["marshal"] == "Lannes" and q["kind"] == "attack")
        murat = next(b for b in lannes["bring"] if b["marshal"] == "Murat")
        assert murat["command"] == "Murat, support Lannes" and murat["ap"] == 1
        assert murat["odds_with"] >= murat["odds_now"] + 15
        assert f"about {murat['odds_now']}%" in murat["why"]
        # what the order MEETS on the road rides the row: Soult, to the letter of
        # an order to Bernadotte, goes round Mack
        bernadotte = next(q for row in served["quotes"]("Swabia")["attack"] for q in row["quotes"]
                          if q["marshal"] == "Bernadotte" and q["kind"] == "attack")
        (soult,) = bernadotte["bring"]
        assert soult["marshal"] == "Soult" and "goes round him" in soult["contact"]

    def test_the_chip_sends_that_order_and_the_muster_then_reads_him_as_ordered(self, served):
        world, _ex = served["seat"]()
        lead = self._ney(served["quotes"]("Swabia"))
        assert "Soult" not in lead["muster"].split(" would answer the guns")[0]
        chip = next(b for b in lead["bring"] if b["marshal"] == "Soult")
        before = int(world.actions_remaining)
        body = served["post"](chip["command"])
        assert body["success"], body.get("message")
        assert int(world.actions_remaining) == before - chip["ap"], "the price on the chip's face"
        order = world.marshals["Soult"].strategic_order
        assert order is not None and order.command_type == "SUPPORT" and order.target == "Ney", \
            "the order the game already has — no new order type"
        again = self._ney(served["quotes"]("Swabia"))
        assert again["bring"] == []
        assert "Soult" in again["muster"].split(" would answer the guns")[0]

    def test_act_one_names_the_plan_from_the_orders_actually_given(self, served):
        world, _ex = served["seat"]()
        assert served["post"]("Soult, support Ney")["success"]
        random.seed(3)
        body = served["post"]("Ney, attack Mack")
        assert body["success"], body.get("message")
        payload = body["battle_diorama"]
        (plan,) = _beats(payload, "plan")
        assert plan["weight"] == "head" and plan["actor"] == "Ney" and plan["side"] == "attacker"
        assert plan["supports"] == ["Soult"], plan
        assert plan["text"].startswith("The plan: Ney leads; Soult ordered in support")
        approach = payload["script"]["acts"][0]
        assert approach["act"] == "approach" and plan in approach["beats"]
        # no order given, no plan told: the bare exchange keeps its own head beats
        world, _ex = served["seat"]()
        random.seed(3)
        bare = served["post"]("Ney, attack Mack")
        assert bare["success"], bare.get("message")
        assert not [b for b in _beats(bare["battle_diorama"], "plan") if b.get("supports")]


# ════════════════════════════════════════════════════════════════════════
# 3. Driven: the real tableau plays the walls, the guns and the board
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def driven(tmp_path_factory):
    if not Path(WALK.GODOT_DEFAULT).exists():
        pytest.skip("the Godot engine is not on this machine")
    committed = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
    payload_dir = tmp_path_factory.mktemp("ba2_payloads")
    manifest, payloads = {}, {}
    for name in DRIVEN_SCENES:
        payload, reason, _result = STAGE.fight(name, int(committed[name]["ambient_seed"]))
        assert payload is not None and reason, name
        (payload_dir / f"{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        manifest[name] = {"form": payload["script"]["form"]}
        payloads[name] = payload
    (payload_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    shots = WALK.build_shots(payload_dir, [], 1.0)
    results, errors = WALK.run(shots, WALK.GODOT_DEFAULT, tmp_path_factory.mktemp("ba2_run"),
                               headless=True, time_scale=8.0)
    return {"shots": shots, "results": results, "errors": errors, "payloads": payloads,
            "by_id": {r["id"]: r for r in results.get("results") or []}}


def _corps(frame):
    return {c["name"]: c for c in frame["corps"]}


class TestTheTableDriven:
    def test_the_engine_ran_clean_and_every_claim_holds(self, driven):
        assert driven["errors"] == []
        # five battles and their settled frames, and the old four-seat payload's pair
        assert len(driven["by_id"]) == len(driven["shots"]) == 2 * len(DRIVEN_SCENES) + 2
        assert all(r.get("ok") for r in driven["by_id"].values())
        assert WALK.check(driven["results"], driven["shots"]) == []

    def test_the_wall_opens_whole_and_ends_as_the_assault_left_it(self, driven):
        for scene, fate in (("assault_stormed", "stormed"), ("assault_on_ours", "held")):
            res = driven["by_id"][scene]
            opening, end = WALK._frame(res, "opening"), WALK._frame(res, "end")
            settled = WALK._frame(driven["by_id"][f"{scene}__settled"], "settled")
            assert opening["kind"] == "assault" and opening["wall"] == "whole", scene
            assert end["wall"] == fate == settled["wall"], scene
            assert not opening["dice_shown"] and not end["dice_shown"], "a wall is not rolled for"
            (keeper,) = [c for c in end["corps"] if c["garrison"]]
            assert not keeper["portrait_shown"] and not keeper["standard_shown"]
            assert keeper["left"] == (scene == "assault_on_ours"), "our own wall stands on our side"

    def test_the_stormers_go_in_by_column_with_ladders(self, driven):
        storm = WALK._frame(driven["by_id"]["assault_stormed"], "storm")
        end = WALK._frame(driven["by_id"]["assault_stormed"], "end")
        assert storm["wall"] == "whole" and storm["wall_ladders_pct"] > 0
        ney, at_rest = _corps(storm)["Ney"], _corps(end)["Ney"]
        assert ney["files_px"] < at_rest["files_px"], "closed up into columns at the wall's foot"
        assert ney["x"] > ney["home_x"], "and gone in"

    def test_a_cannonade_names_the_cannonade_alone_and_brings_the_works_down(self, driven):
        res = driven["by_id"]["bombard_levels"]
        opening, end = WALK._frame(res, "opening"), WALK._frame(res, "end")
        assert opening["kind"] == "bombardment"
        assert {row["act"] for row in opening["played"]} == {"cannonade"}
        assert not opening["dice_shown"] and not end["dice_shown"], "guns throw no dice"
        (works,) = _beats(driven["payloads"]["bombard_levels"], "works")
        assert opening["works"] == {"Mack": works["old"]} and end["works"] == {"Mack": 0}
        assert end["banner"] == "THE WORKS ARE LEVELLED"

    def test_three_corps_a_side_stand_in_the_order_of_battle(self, driven):
        settled = WALK._frame(driven["by_id"]["the_reserve__settled"], "settled")
        assert settled["laid"] == "wedge"
        for left in (True, False):
            side = [c for c in settled["corps"] if c["left"] == left]
            assert sorted(c["role"] for c in side) == ["far", "lead", "near"]
            lead = next(c for c in side if c["role"] == "lead")
            assert lead["lead"], "the centre is the corps that fought the battle"
            for wing in side:
                if wing is lead:
                    continue
                assert abs(wing["home_x"] - WALK.STAGE_MID_X) > abs(lead["home_x"] - WALK.STAGE_MID_X)
        reserve = [m["text"] for m in settled["marks"] if m["kind"] == "text" and "in reserve" in m["text"]]
        payload = driven["payloads"]["the_reserve"]
        assert sorted(reserve) == sorted(
            f"+{payload[side]['reserve_count']} in reserve" for side in ("attacker", "defender"))

    def test_a_corps_comes_on_in_column_and_ends_in_line(self, driven):
        res = driven["by_id"]["the_reserve"]
        opening, end = _corps(WALK._frame(res, "opening")), _corps(WALK._frame(res, "end"))
        assert opening["Ney"]["files_px"] < end["Ney"]["files_px"]
        settled = _corps(WALK._frame(driven["by_id"]["the_reserve__settled"], "settled"))
        assert {n: c["files_px"] for n, c in end.items()} == {n: c["files_px"] for n, c in settled.items()}

    def test_a_square_stands_in_square_from_the_first_frame(self, driven):
        res = driven["by_id"]["square_and_horse"]
        for tag in ("opening", "end"):
            john = _corps(WALK._frame(res, tag))["ArchdukeJohn"]
            assert john["in_square"] and john["files_px"] <= WALK.SQUARE_SPAN_PX, tag
            assert not _corps(WALK._frame(res, tag))["Murat"]["in_square"]

    def test_an_old_payload_that_seats_four_keeps_the_file(self, driven):
        settled = WALK._frame(driven["by_id"]["old_four_seat__settled"], "settled")
        assert settled["laid"] == "file"
        assert max(sum(1 for c in settled["corps"] if c["left"] == left) for left in (True, False)) == 4
        assert WALK.overlaps(settled) == [] and WALK.off_the_baize(settled) == []


# ════════════════════════════════════════════════════════════════════════
# 4. The walk of record, the frames kept, the instruments
# ════════════════════════════════════════════════════════════════════════

class TestTheWalkOfRecord:
    @pytest.fixture(scope="class")
    def record(self):
        return json.loads((AUDIT / "walk_record.json").read_text(encoding="utf-8"))

    def test_it_walked_the_walls_the_guns_and_the_board(self, record):
        assert record["headless"] is False and record["time_scale"] == 1.0
        assert record["script_errors"] == [] and record["problems"] == []
        ids = {r["id"] for r in record["results"]}
        for scene in BA2_SCENES:
            assert scene in STAGE.SCENES and {scene, f"{scene}__settled"} <= ids, scene
        assert {"old_four_seat", "old_four_seat__settled"} <= ids
        assert "godot-client/project-sovereign/scripts/battle_acts.gd" in record["sources"]
        assert "backend/game_logic/siege_diorama.py" in record["sources"]

    def test_the_record_reads_each_table_as_it_was_staged(self, record):
        by = {r["id"]: r for r in record["results"]}
        manifest = json.loads((AUDIT / "payloads" / "manifest.json").read_text(encoding="utf-8"))
        for scene, fate in (("assault_held", "held"), ("assault_stormed", "stormed"),
                            ("assault_occupied", "stormed"), ("assault_capitulated", "capitulated"),
                            ("assault_on_ours", "held")):
            assert manifest[scene]["kind"] == "assault"
            assert WALK._frame(by[scene], "opening")["wall"] == "whole", scene
            assert WALK._frame(by[scene], "end")["wall"] == fate, scene
        for scene in ("bombard_link", "bombard_levels", "bombard_ours"):
            assert manifest[scene]["kind"] == "bombardment"
            assert {row["act"] for row in WALK._frame(by[scene], "opening")["played"]} == {"cannonade"}
        for scene, laid in (("the_reserve", "wedge"), ("two_a_side", "wedge"), ("ulm_full", "wedge"),
                            ("ordinary_brief", "file"), ("old_four_seat", "file")):
            assert WALK._frame(by[f"{scene}__settled"], "settled")["laid"] == laid, scene

    def test_the_frames_it_kept_are_in_the_repo(self, record):
        kept = record["frames_kept"]
        assert len(kept) == len(WALK.CURATED) == 33
        for stem in ("19_three_seats_and_the_reserve", "24_before_the_walls", "25_the_storm",
                     "27_the_walls_are_carried", "28_the_garrison_capitulates", "29_our_own_walls",
                     "31_the_works_are_levelled", "32_our_own_corps_under_our_guns",
                     "33_an_old_four_seat_battle_keeps_its_file"):
            (name,) = [k for k in kept if stem in k]
            assert (AUDIT / name).exists() and (AUDIT / name).stat().st_size > 20_000, name


# ════════════════════════════════════════════════════════════════════════
# 5. The seams
# ════════════════════════════════════════════════════════════════════════

class TestTheSeams:
    def test_the_table_seats_three_and_the_host_is_untouched(self):
        from backend.game_logic.battle_diorama import MAX_CONTINGENTS_PER_SIDE
        assert MAX_CONTINGENTS_PER_SIDE == 3
        host = _gd("battle_diorama.gd")
        assert host.count("_acts.") == 5, "the tableau still hooks the acts at four places"
        acts = _gd("battle_acts.gd")
        assert "const ORDER_OF_BATTLE := true" in acts
        relay = _func(acts, "_relay")
        assert "if most < 2 or most > WEDGE_ROLES.size():\n\t\treturn []" in relay, \
            "a duel and an old four-seat payload keep the host's file"
        dress = _func(acts, "dress")
        assert "if not relaid.is_empty() and not _wedge_is_clear():\n\t\t_unrelay(relaid)" in dress, \
            "a table that cannot take the wedge is put back on the file"

    def test_what_the_result_lays_is_held_back_until_its_moment(self):
        """BA1-X6, for what BA-2 added: the wall as it ended, the works as the
        battle left them, the reserve's dead."""
        opening = _func(_gd("battle_acts.gd"), "_set_opening")
        for needle in ("(dead as Label).visible = false", "_wall.stand_whole()",
                       "(_works[name] as Rampart).stand_as_built()"):
            assert needle in opening, needle
        assert "modulate.a = 0.0" not in opening.split("for dead in _reserve_dead:")[1].split(
            "for item in _played:")[0], "hidden, never drawn at no alpha"

    def test_the_two_tableaux_are_display_only(self):
        """`siege_diorama.py` writes to nothing it is handed: no attribute of
        the world, a marshal or a region is assigned in it."""
        tree = ast.parse((REPO / "backend" / "game_logic" / "siege_diorama.py").read_text(
            encoding="utf-8"))
        written = []
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Attribute):
                    written.append(ast.unparse(target))
        assert written == []
        carry = (REPO / "backend" / "game_logic" / "siege_diorama.py").read_text(encoding="utf-8")
        assert "dict(events[0], diorama=payload)" in carry, "the tableau rides a COPY of the event"

    def test_the_chips_send_the_rows_own_command(self):
        panel = _gd("region_panel.gd")
        chip = _func(panel, "_bring_chip")
        assert 'Utils.bb_button_chip("do:" + str(b.get("command", ""))' in chip
        assert "Utils.bb_chip_disabled(" in chip, "an order that would be refused keeps its place, locked"
        for name in ("_format_marshal_row", "_marshal_row_folded"):
            assert "_bring_lines(_here_attack_bring(m_name, enemy), bring_seen)" in _func(panel, name), name
        assert "out += _bring_block(bring_groups)" in _func(panel, "_quote_rows")
        # a chip says what its order MEETS on the road (the quote's `contact`)
        assert 'var contact := str(b.get("contact", ""))' in _func(panel, "_bring_said")
        assert 'str(b.get("contact", ""))' in _func(_gd("order_confirm_card.gd"), "_bring_lines")
        assert 'elif meta_str == "toggle:bring":' in panel
        card = _gd("order_confirm_card.gd")
        assert "signal bring_requested(command: String)" in card
        assert "lines.append_array(_bring_lines(q))" in _func(card, "_terms")
        pressed = _func(card, "_on_terms_meta")
        assert pressed.index("_close_quietly()") < pressed.index("bring_requested.emit(cmd)")
        main = _gd("main.gd")
        assert "order_card.bring_requested.connect(_on_order_card_bring)" in main
        bring = _func(main, "_on_order_card_bring")
        assert "_send_map_order(command)" in bring and "_card_sent_stays = true" in bring

    def test_the_field_is_one_click_from_an_assault_and_a_cannonade(self):
        dialog = _gd("enemy_phase_dialog.gd")
        assert dialog.count("result += _field_link(event)") == 3
        link = _func(dialog, "_field_link")
        assert 'event.get("diorama")' in link and "⚔ View the field" in link
        shown = _func(_gd("main.gd"), "_display_result")
        assert 'if event_type != "battle" and events.size() > 0 and events[0] is Dictionary' in shown
        block = shown.split('if event_type != "battle" and events.size() > 0')[1].split("# NV-7")[0]
        for needle in ("last_battle_diorama = siege_tableau", "pending_diorama_data = siege_tableau",
                       "[url=diorama:last]⚔ View the field[/url]"):
            assert needle in block, needle

    def test_the_new_colours_are_palette_tokens(self):
        acts = _gd("battle_acts.gd")
        utils = _gd("utils.gd")
        for token in ("UI_WALL_STONE", "UI_WALL_SHADE", "UI_WALL_SCAR", "UI_WORKS_EARTH",
                      "UI_WORKS_CREST", "UI_WHITE_FLAG", "UI_SQUARE_MARK"):
            assert f"const {token} := Color(" in utils and f"Utils.{token}" in acts, token

    def test_the_engine_lane_and_the_harness_know_the_new_file(self):
        conftest = (REPO / "tests" / "conftest.py").read_text(encoding="utf-8")
        assert '"test_ba2_the_walls_and_the_guns",' in conftest
        report = json.loads((REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8"))
        scripts = {row["path"]: row for row in report["scripts"]}
        for name in ("battle_acts.gd", "region_panel.gd", "order_confirm_card.gd",
                     "enemy_phase_dialog.gd", "main.gd"):
            row = scripts[f"res://scripts/{name}"]
            assert row.get("load_ok", True) and not row.get("errors"), name


# ════════════════════════════════════════════════════════════════════════
# 6. The open row this session filed
# ════════════════════════════════════════════════════════════════════════

class TestBA2X2ACourtsTurnIsNotLost:
    """BA2-X2 (OPEN, owner row BA's session BA-3): a corps beaten to nothing
    and raised again in the middle of its court's phase is not on the phase's
    opening roster, and the fairness tally built from that roster has no key
    for it — the court's whole turn is lost to a `KeyError` (seed jena,
    Prussia, Yorck). Found in passing by the probe that measured how often the
    day hangs; the one-line fix moves a measured world-line, so it lands
    behind a seam in BA-3, whose measure reads what it moves. The pin turns
    red the day the tally changes, so the row is closed with it."""

    def test_the_tally_is_built_from_the_opening_roster(self):
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert "actions_used = {m.name: 0 for m in marshals}" in source, \
            "the defect's own line: the tally knows only the corps the phase opened with"

    @pytest.mark.xfail(strict=True, reason="BA2-X2 OPEN — owner row BA's session BA-3")
    def test_the_tally_takes_a_corps_raised_mid_phase(self):
        source = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert "actions_used[selected_marshal.name] += 1" not in source


class TestBA2X6ThePanelRestsOnWholeLines:
    """BA2-X6 (half fixed here; the rest OPEN, owner Session H): a long
    province's panel opened with its fold through the middle of a line. It now
    opens with the fold between two lines; scrolled, it can still rest on a
    cut line — it is not among the screens `Utils.keep_whole_lines` holds."""

    def test_the_panel_opens_with_its_fold_between_lines(self):
        panel = _gd("region_panel.gd")
        rule = _func(panel, "_window_on_whole_lines")
        assert "content_area.get_line_offset(i + 1)" in rule and "if line_end > available:" in rule
        for name in ("_fit_height", "_fit_height_in_wing"):
            assert "scroll.custom_minimum_size.y = _window_on_whole_lines(content_h, available)" \
                in _func(panel, name), name
        record = json.loads((REPO / "docs" / "audits" / "uxr3" /
                             "frame_census_ba2_walls_guns_2026_11_15.json").read_text(encoding="utf-8"))
        assert record["cut_lines"] == []

    @pytest.mark.xfail(strict=True, reason="BA2-X6 OPEN — owner Session H (S15, the deploy)")
    def test_the_scrolled_panel_rests_on_whole_lines(self):
        assert "Utils.keep_whole_lines(" in _gd("region_panel.gd")


class TestThePlanPressedInTheRealClient:
    """The plan's loop pressed in the real client — `tools/ba2_mode_c_walk.py`:
    the real `main.tscn` against a sandboxed backend on the campaign's opening
    board. The dated record of November 15, 2026 (kept as a record; the walk
    is re-run by hand, never by the suite). Its FIRST run is what found
    Murat's question: his chip for Ney raised MURAT REPORTS and the walk could
    go no further (`_first_step_asks`; BA2-X7's second half)."""

    RECORD = REPO / "docs" / "audits" / "ba2_mode_c_2026_11_15"

    def _steps(self):
        run = json.loads((self.RECORD / "run.json").read_text(encoding="utf-8"))
        assert run["engine_exit"] == 0 and run["script_errors"] == []
        walk = run["walk"]
        assert walk["booted"] and walk["errors"] == [] and "error" not in walk
        return walk, {row["step"]: row for row in walk["results"]}

    def test_every_step_held(self):
        walk, steps = self._steps()
        assert list(steps) == ["boot", "panel_open", "panel_fold_open", "panel_chip", "card_open",
                               "card_chip", "card_again", "lead_card", "attack_sent"]
        assert all(row["ok"] for row in walk["results"])
        for frame in walk["steps"]:
            assert frame["saved"] and (self.RECORD / "frames" / frame["frame"]).is_file(), frame["frame"]

    def test_what_the_client_showed(self):
        _walk, steps = self._steps()
        # the fold, and who is offered to whom: Murat to Lannes alone, Bernadotte to none
        assert "▸ Bring up — " in steps["panel_open"]["saw"]
        offered = steps["panel_fold_open"]["saw"]
        assert 'Murat to ["Lannes"]' in offered and "Bernadotte to []" in offered
        assert '"Ney"' in offered.split(";")[0], "Soult is offered to Ney"
        # the panel's chip: the order taken at its price, no question raised
        assert "actions 4 -> 3" in steps["panel_chip"]["saw"]
        assert "a question raised=''" in steps["panel_chip"]["saw"]
        assert "Soult moves to support Ney" in steps["panel_chip"]["log_tail"]
        # the card's chip: the card shuts at once, the order goes, the lead is selected again
        card = steps["card_chip"]["saw"]
        assert "card shut at once=true" in card and "actions 3 -> 2" in card
        assert "a question raised=''" in card and "selected again=Lannes" in card
        assert "Murat counted=true" in steps["card_again"]["saw"]
        assert "no chip for him again=true" in steps["card_again"]["saw"]
        assert "Soult counted=true" in steps["lead_card"]["saw"]
        # the attack sent: Act I names the plan from the order actually given
        assert steps["attack_sent"]["plan"] == "The plan: Ney leads; Soult ordered in support."
        assert "the tableau up=true" in steps["attack_sent"]["saw"]

    def test_the_walk_presses_the_real_nodes(self):
        walk = (REPO / "tools" / "ba2_mode_c_walk.gd").read_text(encoding="utf-8")
        assert 'load("res://scenes/main.tscn")' in walk
        # the panel's own link handler and the card's, by the signals a click emits
        assert 'area.emit_signal("meta_clicked", "do:" + PANEL_CHIP)' in walk
        assert 'terms_label.emit_signal("meta_clicked", "do:" + CARD_CHIP)' in walk
        assert 'sendb.emit_signal("pressed")' in walk
        # no step may end on a marshal's question
        assert walk.count('asked == ""') == 2
        runner = (REPO / "tools" / "ba2_mode_c_walk.py").read_text(encoding="utf-8")
        assert "start_backend" in runner and "never two engines" in runner
        # the parse check knows the walk, and its committed report read it clean
        harness = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert '"res://../../tools/ba2_mode_c_walk.gd"' in harness
        report = json.loads((REPO / "tools" / "godot_parse_report.json").read_text(encoding="utf-8"))
        row = {r["path"]: r for r in report["scripts"]}["res://../../tools/ba2_mode_c_walk.gd"]
        assert row["parse_ok"] and row["load_ok"] and not row["errors"]


class TestBA2X7TheMusterPromisesWhatTheOrderDelivers:
    """BA2-X7 (OPEN, owner row BA's session BA-3): on the opening battle
    Berthier's muster says a written order "would likely bring" Bernadotte;
    the order marches him at once to Munich, from whose mountains he cannot
    reach the field. It names the same order for Murat ("…and it rises to
    about 100%"), whose road to Ney runs through Mack: the order stops him on
    his question, and two of its four answers abandon it. The chips offer only
    what the order delivers (`bring_quotes`, held to the game by
    `test_ba2_backend_walls_guns_plan.py::TestBringQuotes`); the muster's own
    sentences still read each man from where he stands. The pin turns red the
    day the two agree, so the row is closed with it."""

    @staticmethod
    def _named_and_offered():
        from backend.commands import order_quotes
        world, executor = STAGE._board()
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        with STAGE._quiet():
            preview = executor._combat._build_muster_preview(ney, mack, world, {"world": world})
        named = {row["marshal"] for row in preview["rows"]
                 if ", support Ney'" in (str(row.get("standing_order_hint") or "")
                                         + str(row.get("arrival_note") or ""))}
        offered = {b["marshal"] for b in order_quotes.bring_quotes(world, ney, mack)}
        return named, offered

    def test_the_muster_names_the_lever_for_three_and_the_chips_offer_one(self):
        named, offered = self._named_and_offered()
        assert named == {"Murat", "Soult", "Bernadotte"} and offered == {"Soult"}

    @pytest.mark.xfail(strict=True, reason="BA2-X7 OPEN — owner row BA's session BA-3")
    def test_every_corps_the_muster_names_the_lever_for_is_one_the_order_brings(self):
        named, offered = self._named_and_offered()
        assert named <= offered
